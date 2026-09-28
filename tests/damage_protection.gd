# RUN-007: protection timing and feedback with actual physical contacts.
extends SceneTree

# Keep enemies in contact while retaining the production movement/contact code.
class FollowingSlime extends SliceSlime:
	var target: SlicePlayer
	var offset := Vector2(5, 0)
	func _physics_process(delta: float) -> void:
		global_position = target.global_position + offset
		super._physics_process(delta)

var checks := 0
var failures := 0
var room: Node2D
var player: SlicePlayer
var impact_ticks: Array[int] = []

func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func spawn() -> void:
	for action in ["attack", "jump", "move_left", "move_right"]: Input.action_release(action)
	if is_instance_valid(room):
		room.queue_free()
		await frames(2)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	var floor_body := StaticBody2D.new()
	floor_body.position = Vector2(200, 208)
	var floor_shape := CollisionShape2D.new()
	floor_shape.shape = RectangleShape2D.new()
	floor_shape.shape.size = Vector2(4000, 16)
	floor_body.add_child(floor_shape)
	room.add_child(floor_body)
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(200, 200)
	room.add_child(player)
	impact_ticks.clear()
	player.health_changed.connect(func(_hp: float, _max: float): impact_ticks.append(Engine.get_physics_frames()))
	await frames(4)

func run() -> void:
	check(not root.get_node("Progression").persistence_enabled, "script fixture disables real save persistence")
	check(Engine.physics_ticks_per_second == 60, "timing fixture runs at 60 physics ticks per second")
	await spawn()
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	check(is_equal_approx(player.invulnerability, 1.2), "accepted impact starts exactly 1.2 seconds of shared protection")
	check(is_equal_approx(player.hurt_flash_time, 0.1) and player.hurt_material.get_shader_parameter("white_flash") == 1.0 and player.sprite.modulate.a == 1.0, "accepted impact immediately displays opaque white flash for 0.10 seconds")
	await frames(5)
	check(player.hurt_flash_time > 0.0 and player.hurt_material.get_shader_parameter("white_flash") == 1.0, "white flash remains active immediately before 0.10 seconds")
	var frozen_timer := player.invulnerability
	var frozen_flash := player.hurt_flash_time
	var frozen_alpha := player.sprite.modulate.a
	paused = true
	await frames(20)
	check(player.invulnerability == frozen_timer and player.hurt_flash_time == frozen_flash and player.sprite.modulate.a == frozen_alpha and player.hurt_material.get_shader_parameter("white_flash") == 1.0, "pause freezes protection and white flash together")
	paused = false
	await frames(1)
	check(player.hurt_flash_time == 0.0 and player.hurt_material.get_shader_parameter("white_flash") == 0.0, "sixth physics tick ends the white flash")
	var saw_dim := false
	var saw_opaque := false
	var attempts_ignored := true
	var flash_stays_off := true
	for tick in range(6, 71):
		for source in [SlicePlayer.DamageSource.CONTACT_MELEE, SlicePlayer.DamageSource.PROJECTILE, SlicePlayer.DamageSource.SOLID_TRAP, SlicePlayer.DamageSource.FLAME, SlicePlayer.DamageSource.SWARM]:
			player.take_damage(0.5, Vector2(80, -50), source)
		attempts_ignored = attempts_ignored and player.health_units == 25 and impact_ticks.size() == 1
		flash_stays_off = flash_stays_off and player.hurt_flash_time == 0.0 and player.hurt_material.get_shader_parameter("white_flash") == 0.0
		saw_dim = saw_dim or is_equal_approx(player.sprite.modulate.a, 0.25)
		saw_opaque = saw_opaque or is_equal_approx(player.sprite.modulate.a, 1.0)
		await frames(1)
	check(attempts_ignored and flash_stays_off, "all five sources attempted every tick share protection and cannot restart feedback")
	check(saw_dim and saw_opaque, "remaining protection alternates high-contrast 0.25 and 1.0 alpha")
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	check(player.health_units == 25 and player.invulnerability > 0.0, "contact on tick 71 remains ignored")
	await frames(1)
	check(player.invulnerability == 0.0 and player.hurt_flash_time == 0.0 and player.sprite.modulate == Color.WHITE and player.hurt_material.get_shader_parameter("white_flash") == 0.0, "tick 72 restores ordinary appearance and ends protection")
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	check(player.health_units == 20 and impact_ticks.size() == 2 and player.hurt_material.get_shader_parameter("white_flash") == 1.0, "first contact after 1.2 seconds applies damage and starts a fresh flash")

	await spawn()
	var other: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	other.position = Vector2(300, 200)
	room.add_child(other)
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	check(player.hurt_material != other.hurt_material and other.hurt_material.get_shader_parameter("white_flash") == 0.0 and other.sprite.modulate == Color.WHITE, "each player owns independent material and feedback")

	await spawn()
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	player.take_damage(0.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)
	check(player.dead and player.hurt_flash_time == 0.0 and player.hurt_material.get_shader_parameter("white_flash") == 0.0 and player.sprite.modulate == Color.WHITE, "VOID during white flash restores opaque ordinary death appearance")
	await frames(10)
	check(player.sprite.modulate == Color.WHITE and player.hurt_material.get_shader_parameter("white_flash") == 0.0, "death appearance stays opaque without resuming protection feedback")

	await spawn()
	player.max_health_units = 120
	player.health_units = 120
	var contacts: Array[FollowingSlime] = []
	for offset_x in [-5, 5]:
		var enemy = load("res://scenes/slime.tscn").instantiate()
		enemy.set_script(FollowingSlime)
		enemy.target = player
		enemy.offset = Vector2(offset_x, 0)
		enemy.position = player.position + enemy.offset
		enemy.patrol_left = -2000
		enemy.patrol_right = 2000
		room.add_child(enemy)
		contacts.append(enemy)
	await frames(3)
	var both_overlap := true
	for enemy in contacts:
		both_overlap = both_overlap and enemy.get_node("ContactArea").get_overlapping_bodies().has(player)
	check(both_overlap and impact_ticks.size() == 1 and player.health_units == 115, "two real overlapping Slimes produce only one initial half-HP impact")
	await frames(160)
	var cadence_ok := impact_ticks.size() == 3 and player.health_units == 105
	for i in range(1, impact_ticks.size()):
		cadence_ok = cadence_ok and impact_ticks[i] - impact_ticks[i - 1] == 72
	check(cadence_ok, "maintained physical contact from two Slimes applies one half-HP hit every 72 ticks")

	for facing in [-1, 1]:
		for side in [-1, 0, 1]:
			await spawn()
			Input.action_press("attack")
			await frames(2)
			Input.action_release("attack")
			player.set_physics_process(false)
			player.facing = facing
			player.position.x = 200 + side * 8
			var hazard = load("res://scenes/hazard.tscn").instantiate()
			hazard.position = Vector2(200, 200)
			room.add_child(hazard)
			await frames(3)
			var expected_direction: int = side if side != 0 else -facing
			check(hazard.get_overlapping_bodies().has(player) and player.health_units == 20 and player.velocity == Vector2(expected_direction * 90, -180), "actual trap contact pushes away at side %d and facing %d (center uses -facing)" % [side, facing])
			check(player.knockback_time == 0.16 and player.hit_stun_time == 0.0 and player.attack_time > 0.0, "trap keeps 0.16-second recoil without hit-stun or interrupting Sword")
			var before := player.position
			player.set_physics_process(true)
			await frames(3)
			check((player.position.x - before.x) * expected_direction > 0.0 and player.position.y < before.y, "trap recoil physically moves away and upward")

	for action in ["attack", "jump", "move_left", "move_right"]: Input.action_release(action)
	room.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " damage protection checks; ", failures, " failures")
	quit(failures)

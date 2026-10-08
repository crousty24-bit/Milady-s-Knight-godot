extends SceneTree
var checks := 0
var failures := 0
var room: Node2D
var shots := 0

func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func reset() -> void:
	paused = false
	if is_instance_valid(room):
		room.queue_free()
		await frames()
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
func player_at(at: Vector2) -> SlicePlayer:
	var player: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	player.position = at
	room.add_child(player)
	player.set_physics_process(false)
	return player
func trap(name: String, at: Vector2) -> Node2D:
	var node: Node2D = load("res://scenes/%s.tscn" % name).instantiate()
	node.position = at
	return node
func wall(at: Vector2) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.position = at
	var collision := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(2, 80)
	collision.shape = shape
	body.add_child(collision)
	room.add_child(body)
	return body
func shot(at: Vector2, aim: Vector2 = Vector2.RIGHT, speed: float = 1200.0) -> Node2D:
	var node := trap("trap_projectile", at)
	room.add_child(node)
	node.setup(aim, speed, 320.0)
	return node

func run() -> void:
	await reset()
	var initial_spikes := trap("retractable_spikes", Vector2(200, 180))
	initial_spikes.initial_phase = 2.1
	room.add_child(initial_spikes)
	initial_spikes.set_physics_process(false)
	check(initial_spikes._art.animation == &"extended" and initial_spikes.find_children("*", "AudioStreamPlayer2D", true, false).is_empty(), "initial dangerous phase is settled and silent")
	initial_spikes.cycle_time = 0.0
	initial_spikes._update_phase()
	initial_spikes.cycle_time = 2.1
	initial_spikes._update_phase()
	check(initial_spikes._art.animation == &"extend" and initial_spikes.find_children("*", "AudioStreamPlayer2D", true, false).is_empty(), "later extension plays transition, silently (RUN-021)")
	for angle in [0.0, PI / 2.0, PI, -PI / 2.0]:
		await reset()
		var spikes := trap("retractable_spikes", Vector2(200, 180))
		spikes.rotation = angle
		spikes.safe_duration = 10.0
		room.add_child(spikes)
		spikes.set_physics_process(false)
		var normal := Vector2.UP.rotated(angle)
		var player := player_at(spikes.position + normal * 55 + Vector2(0, 9))
		await frames()
		var blocked := false
		for i in 30:
			if player.move_and_collide(-normal * 3) != null:
				blocked = true
				break
			await frames(1)
		await frames()
		check(blocked and player.health_units == 30, "retracted base solid and safe at rotation %.2f" % angle)
		check(spikes.get_node("Points").disabled, "retracted points do not block at rotation %.2f" % angle)
		player.position = spikes.position + normal * 55 + Vector2(0, 9)
		spikes.cycle_time = 10.6
		spikes._update_phase()
		await frames()
		blocked = false
		spikes.set_physics_process(true)
		player.activate_magic_shield()
		for i in 30:
			if player.move_and_collide(-normal * 3) != null: blocked = true
			await frames(1)
			if blocked: break
		await frames()
		check(blocked and player.health_units == 30 and player.velocity == Vector2.ZERO and player.knockback_time == 0.0, "Shield blocks extended points damage/recoil while keeping solidity at rotation %.2f" % angle)
		player.magic_shield_time = 0.0
		await frames()
		check(player.health_units == 25, "extended solid points deal half HP when Shield ends at rotation %.2f" % angle)
		check(player.velocity.dot(normal) > 170 and player.hit_stun_time == 0.0, "rotated solid trap recoil/profile %.2f" % angle)
		player.dead = true
		var hp: int = player.health_units
		await frames()
		check(player.health_units == hp, "dead player ignored at rotation %.2f" % angle)
	await reset()
	var spikes := trap("retractable_spikes", Vector2.ZERO)
	spikes.safe_duration = 0.1
	spikes.warning_duration = 0.1
	spikes.danger_duration = 0.1
	room.add_child(spikes)
	await frames(8)
	check(spikes.phase == spikes.Phase.WARNING, "spikes show warning before dangerous phase")
	var clock: float = spikes.cycle_time
	paused = true
	await frames(10)
	check(spikes.cycle_time == clock, "pause freezes spike cycle")
	paused = false
	await frames(7)
	check(spikes.phase == spikes.Phase.EXTENDED, "spikes resume dangerous phase")
	await frames(5)
	check(spikes.phase == spikes.Phase.RETRACTED, "spikes retract after danger")

	await reset()
	var door := trap("trapdoor", Vector2(100, 180))
	room.add_child(door)
	var player := player_at(Vector2(100, 200))
	await frames(5)
	check(not door.triggered, "below trapdoor does not trigger")
	player.dead = true
	player.position = Vector2(100, 180)
	await frames(5)
	check(not door.triggered, "dead player does not trigger trapdoor")
	player.dead = false
	player.position = Vector2(118, 180)
	player.velocity = Vector2(60, 0)
	await frames(5)
	check(door.get_node("Trigger").get_overlapping_bodies().has(player) and not door.triggered, "side overlap with feet outside trapdoor width does not trigger")
	player.position = Vector2(100, 180)
	player.velocity = Vector2.ZERO
	await frames(5)
	check(door.triggered and not door.is_open and not door.get_node("Solid").disabled, "resting player on trapdoor starts warning while floor remains solid")
	var remaining: float = door.warning_remaining
	paused = true
	await frames(15)
	check(door.warning_remaining == remaining, "pause freezes trapdoor warning")
	paused = false
	await frames(30)
	check(door.is_open and door.get_node("Solid").disabled, "trapdoor opens after warning")
	player.position = Vector2(100, 165)
	var hit := player.move_and_collide(Vector2(0, 50))
	check(hit == null and player.position.y > 200, "player passes through opened trapdoor")
	await frames(120)
	check(door.is_open, "trapdoor stays open until scene reset")
	# Two ledges around a 32px opening: actual player gravity/jump can reach a lip.
	for x in [60.0, 140.0]:
		var ledge := wall(Vector2(x, 210))
		ledge.get_child(0).shape.size = Vector2(48, 60)
	player.position = Vector2(100, 205)
	player.velocity = Vector2(100, -300)
	player.controls_enabled = true
	player.set_physics_process(true)
	Input.action_press("move_right")
	await frames(35)
	Input.action_release("move_right")
	check(player.position.x > 116 and player.position.y < 180, "physical jump escapes fixture pit to adjacent lip")
	await reset()
	door = trap("trapdoor", Vector2.ZERO)
	room.add_child(door)
	await frames()
	check(not door.is_open and not door.triggered, "new scene resets trapdoor")

	await reset()
	var plant := trap("poison_plant", Vector2(100, 180))
	room.add_child(plant)
	player = player_at(Vector2(65, 180))
	player.activate_magic_shield()
	await frames()
	hit = player.move_and_collide(Vector2(50, 0))
	await frames()
	check(hit != null and player.health_units == 30 and player.knockback_time == 0, "plant remains solid but Shield blocks its damage and recoil")
	player.magic_shield_time = 0.0
	await frames()
	check(player.health_units == 20, "plant damage resumes after Shield ends while still touching")
	check(player.knockback_time > 0 and player.hit_stun_time == 0, "plant uses solid trap response")

	await reset()
	player = player_at(Vector2(100, 160))
	player.attack_time = 0.2
	player.activate_magic_shield()
	await frames()
	var projectile := shot(Vector2(40, 151), Vector2.RIGHT, 12000.0)
	await frames(2)
	check(not is_instance_valid(projectile) and player.health_units == 30 and not player.attack_cancelled and player.invulnerability == 0.0, "Shield absorbs fast turret projectile without damage or interruption")
	player.magic_shield_time = 0.0
	projectile = shot(Vector2(40, 151), Vector2.RIGHT, 12000.0)
	await frames(2)
	check(not is_instance_valid(projectile) and player.health_units == 20, "fast turret hit deals one HP after Shield ends")
	check(player.attack_cancelled and player.hit_stun_time == 0 and player.knockback_time == 0, "turret projectile interrupts without recoil/hit stun")
	await reset()
	player = player_at(Vector2(100, 160))
	wall(Vector2(75, 150))
	await frames()
	projectile = shot(Vector2(40, 151), Vector2.RIGHT, 12000.0)
	await frames(2)
	check(not is_instance_valid(projectile) and player.health_units == 30, "terrain occludes fast turret shot")
	await reset()
	player = player_at(Vector2(100, 160))
	player.dead = true
	await frames()
	projectile = shot(Vector2(40, 151), Vector2.RIGHT, 12000.0)
	await frames(2)
	check(not is_instance_valid(projectile) and player.health_units == 30, "dead player consumes shot without additional damage")
	await reset()
	projectile = shot(Vector2.ZERO)
	await frames(2)
	var at := projectile.position
	paused = true
	await frames(10)
	check(projectile.position == at, "pause freezes projectile travel")
	paused = false
	await frames(30)
	check(not is_instance_valid(projectile), "projectile expires at configured range")

	await reset()
	var turret := trap("turret", Vector2(200, 180))
	turret.direction = Vector2.RIGHT
	turret.rotation = -PI / 2
	turret.cooldown_duration = 0.15
	turret.warning_duration = 0.1
	turret.initial_phase = 0.1
	turret.fired.connect(func(_p): shots += 1)
	room.add_child(turret)
	await frames(5)
	check(turret.warning and shots == 0, "turret fixed initial phase shows telegraph before shot")
	clock = turret.cycle_time
	paused = true
	await frames(20)
	check(turret.cycle_time == clock and shots == 0, "pause freezes turret cadence")
	paused = false
	await frames(7)
	var found := false
	for child in room.get_children():
		if child.get_script() == load("res://scripts/trap_projectile.gd"):
			found = child.direction.is_equal_approx(Vector2.UP) and child.global_position.y < 167
	check(shots == 1 and found, "rotated turret launches along configured local direction beyond housing")
	await frames(16)
	check(shots == 2, "turret repeats configurable cadence")
	await reset()
	turret = trap("turret", Vector2(200, 180))
	turret.direction = Vector2(1, 1)
	room.add_child(turret)
	turret._fire()
	await frames(3)
	found = false
	for child in room.get_children():
		if child.get_script() == load("res://scripts/trap_projectile.gd"):
			found = child.direction.is_equal_approx(Vector2(1, 1).normalized()) and child.distance_travelled > 0
	check(found, "diagonal turret projectile clears solid housing")
	await reset()
	room.queue_free()
	await frames()
	# Fixed-FPS simulation outruns the real-time mixer; drain freed fixture playbacks.
	OS.delay_msec(300)
	print("RESULT %d checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

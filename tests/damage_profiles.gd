# RUN-006: fractional HP and damage-source behavior in a physical Godot room.
extends SceneTree
var failures: int = 0
var checks: int = 0
var room: Node2D
var player: SlicePlayer
var deaths: int = 0
var enemy_deaths: int = 0
var health_events: Array[Array] = []

func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func solid(pos: Vector2, size: Vector2, layer: int = 1) -> void:
	var body := StaticBody2D.new()
	body.position = pos
	body.collision_layer = layer
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	body.add_child(shape)
	room.add_child(body)
func spawn(pos: Vector2 = Vector2(100, 200)) -> void:
	for action in ["attack", "jump", "move_left", "move_right"]: Input.action_release(action)
	if is_instance_valid(room):
		room.queue_free()
		await frames(2)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	solid(Vector2(150, 208), Vector2(600, 16), 9)
	solid(Vector2(208, 80), Vector2(16, 240), 9)
	player = load("res://scenes/player.tscn").instantiate()
	player.position = pos
	room.add_child(player)
	deaths = 0
	health_events.clear()
	player.died.connect(func(): deaths += 1)
	player.health_changed.connect(func(value: float, maximum: float): health_events.append([value, maximum]))
	await frames(4)

func run() -> void:
	check(HealthUnits.from_hp(0.5) == 5 and HealthUnits.from_hp(0.2) == 2, "half and fifth HP have exact integer units")
	await spawn()
	for i in range(6):
		player.invulnerability = 0.0
		player.take_damage(0.5, Vector2.ZERO)
		check(player.health_units == 25 - i * 5, "half-HP damage #%d is exact" % (i + 1))
	check(player.dead and deaths == 1 and health_events.size() == 6, "zero HP emits one death and one health update per hit")
	player.take_damage(5.0, Vector2.ZERO)
	player.heal(1.0)
	check(player.health_units == 0 and deaths == 1 and health_events.size() == 6, "dead player cannot lose more HP, revive or die twice")
	await spawn()
	player.take_damage(0.5, Vector2.ZERO)
	check(player.heal(1.0) == 0.5 and player.health_units == 30 and player.heal(0.5) == 0.0, "healing is capped at maximum HP")
	check(health_events.back() == [3.0, 3.0], "health signal carries current and maximum fractional values")
	var hud = load("res://scenes/hud.tscn").instantiate()
	room.add_child(hud)
	hud.set_health(2.5, 3.0)
	check(hud.get_node("Health").text == "VIE 2.5" and hud.get_node("HealthHearts").displayed_half_hearts() == 5, "HUD shows exact half HP and five filled half-hearts")
	hud.set_health(0.2, 3.0)
	check(hud.get_node("Health").text == "VIE 0.2" and hud.get_node("HealthHearts").displayed_half_hearts() == 1, "sub-half HP stays exact in text and rounds up to a visible half-heart")

	var slime: SliceSlime = load("res://scenes/slime.tscn").instantiate()
	slime.position = Vector2(300, 200)
	room.add_child(slime)
	slime.set_physics_process(false)
	enemy_deaths = 0
	var slime_events: Array[Array] = []
	slime.defeated.connect(func(_bonus: int, _at: Vector2): enemy_deaths += 1)
	slime.health_changed.connect(func(value: float, maximum: float): slime_events.append([value, maximum]))
	for i in range(15):
		slime.take_damage(0.2, Vector2.ZERO, SlicePlayer.DamageSource.FLAME)
		check(slime.health_units == 28 - i * 2, "flame damage in fifths accumulates exactly: hit %d" % (i + 1))
	check(slime.dead and enemy_deaths == 1 and slime_events.size() == 15 and slime_events.back() == [0.0, 3.0], "enemy fractional health and defeat signals are exact and unique")
	slime.take_damage(0.2, Vector2.ZERO, SlicePlayer.DamageSource.FLAME)
	check(enemy_deaths == 1 and slime_events.size() == 15, "dead enemy cannot grant a second reward or health event")

	var profiles := [
		[SlicePlayer.DamageSource.CONTACT_MELEE, true, true, true],
		[SlicePlayer.DamageSource.PROJECTILE, false, false, true],
		[SlicePlayer.DamageSource.SOLID_TRAP, false, true, false],
		[SlicePlayer.DamageSource.FLAME, false, true, false],
		[SlicePlayer.DamageSource.SWARM, false, false, false],
	]
	for profile in profiles:
		await spawn()
		Input.action_press("attack")
		await frames(2)
		check(player.attack_time > 0.0, "attack is active before source %d" % profile[0])
		player.take_damage(0.5, Vector2(80, -50), profile[0])
		check(player.health_units == 25 and player.invulnerability > 0.0, "source %d applies half damage and invulnerability" % profile[0])
		check((player.hit_stun_time > 0.0) == profile[1] and (player.knockback_time > 0.0) == profile[2] and (player.attack_time == 0.0) == profile[3], "source %d has the specified stun, recoil and interruption" % profile[0])
		check((player.velocity == Vector2(80, -50)) == profile[2], "source %d applies physical impulse only with recoil" % profile[0])
		player.take_damage(0.5, Vector2.ZERO, profile[0])
		check(player.health_units == 25, "source %d cannot stack a second contact during invulnerability" % profile[0])

	await spawn()
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	player.invulnerability = 2.0 / 60.0
	await frames(1)
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	check(player.health_units == 25, "contact immediately before invulnerability ends is ignored")
	await frames(1)
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	check(player.invulnerability > 0.0 and player.health_units == 20, "contact on the first unprotected tick applies damage again")

	await spawn()
	Input.action_press("attack")
	await frames(2)
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.CONTACT_MELEE)
	await frames(10)
	check(player.hit_stun_time > 0.0 and player.attack_time == 0.0, "held F stays blocked through hit-stun")
	await frames(1)
	check(player.hit_stun_time == 0.0 and player.attack_time > 0.0, "held F resumes on the first unblocked physics tick")
	await spawn()
	Input.action_press("attack")
	await frames(2)
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
	check(player.attack_time == 0.0 and player.hit_stun_time == 0.0, "projectile interrupts the current swing without hit-stun")
	await frames(1)
	check(player.attack_time > 0.0, "held F can start a new swing on the next tick after projectile interruption")

	await spawn()
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SOLID_TRAP)
	Input.action_press("jump")
	await frames(9)
	check(player.knockback_time > 0.0 and player.is_on_floor() and player.velocity.y >= 0.0, "Space pressed during recoil cannot jump")
	await frames(1)
	check(player.knockback_time == 0.0 and player.is_on_floor(), "held Space does not auto-jump when recoil expires")
	Input.action_release("jump")
	await frames(1)
	Input.action_press("jump")
	await frames(1)
	check(player.velocity.y < 0.0, "fresh Space press jumps after recoil")

	await spawn(Vector2(194.92, 40))
	player.velocity.y = 100.0
	await frames(5)
	check(player.motion_state == SlicePlayer.MotionState.WALL_SLIDE, "fixture reaches the grippable wall")
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.CONTACT_MELEE)
	Input.action_press("jump")
	await frames(2)
	check(player.wall_normal < 0.0 and player.velocity.x == 0.0 and not player.wall_jump_lockout, "wall jump is blocked during recoil")
	await frames(9)
	Input.action_release("jump")
	await frames(1)
	Input.action_press("jump")
	await frames(1)
	check(player.velocity.x < -80.0 and player.wall_jump_lockout, "wall jump resumes after recoil")

	await spawn(Vector2(100, 185))
	player.velocity.y = 100.0
	player.take_damage(0.5, Vector2(0, 100), SlicePlayer.DamageSource.CONTACT_MELEE)
	Input.action_press("attack")
	await frames(8)
	check(player.is_on_floor() and player.hit_stun_time > 0.0 and player.attack_time == 0.0, "landing during hit-stun cannot start held F")
	await frames(3)
	check(player.hit_stun_time == 0.0 and player.attack_time > 0.0, "held F resumes after landing and hit-stun")

	await spawn()
	player.invulnerability = 0.8
	player.take_damage(0.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)
	check(player.dead and player.health_units == 0 and deaths == 1, "void remains fatal through invulnerability")

	for action in ["attack", "jump", "move_left", "move_right"]: Input.action_release(action)
	room.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " damage profile checks; ", failures, " failures")
	quit(failures)

# RUN-018: actual held input cadence and physical shape/ray boundaries for all levels.
extends SceneTree
const ARROW = preload("res://scripts/arrow.gd")
class Target extends StaticBody2D:
	var damage_received := 0.0
	var hits := 0
	func take_damage(amount: float, _impulse := Vector2.ZERO, _source := 0) -> void:
		damage_received += amount
		hits += 1
var failures := 0
var checks := 0
var room: Node2D
var player: SlicePlayer
var shots: Array[Node2D] = []
var shot_ticks: Array[int] = []
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
	paused = false
	Input.action_release("attack")
	if is_instance_valid(room):
		room.queue_free()
		await frames(2)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	wall(Vector2(400, 208), Vector2(1800, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(160, 200)
	room.add_child(player)
	shots.clear()
	shot_ticks.clear()
	player.projectile_fired.connect(func(arrow: Node2D): shots.append(arrow); shot_ticks.append(Engine.get_physics_frames()))
	await frames(4)
func wall(at: Vector2, size: Vector2, layer := 1) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.collision_layer = layer
	body.position = at
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	body.add_child(shape)
	room.add_child(body)
	return body
func target(at: Vector2) -> Target:
	var body := Target.new()
	body.collision_layer = 4
	body.collision_mask = 0
	body.position = at
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = Vector2(0.2, 0.2)
	body.add_child(shape)
	room.add_child(body)
	return body
func equip(id: String) -> void:
	var ranged: bool = WeaponCatalog.stats(id).slot == "ranged"
	player.configure_loadout({"melee": "Sword0" if ranged else id, "ranged": id if ranged else ""})
	player.active_slot = 1 if ranged else 0
func cadence(id: String) -> void:
	await spawn()
	equip(id)
	var stats := WeaponCatalog.stats(id)
	var ticks := int(round(stats.interval * 60.0))
	var starts: Array[int] = []
	var previous := 0.0
	Input.action_press("attack")
	for i in range(ticks * 2 + 3):
		await frames(1)
		if player.attack_cooldown > previous + 0.1:
			starts.append(Engine.get_physics_frames())
		previous = player.attack_cooldown
	Input.action_release("attack")
	if stats.slot == "ranged": starts = shot_ticks
	check(starts.size() == 3 and starts[1] - starts[0] == ticks and starts[2] - starts[1] == ticks, id + " held input cadence matches contract at 60 Hz")
func melee_bounds(id: String, direction: int) -> void:
	await spawn()
	equip(id)
	player.set_physics_process(false)
	player.attack_facing = direction
	player.attack_time = 0.15
	player.attack_cancelled = false
	var stats := WeaponCatalog.stats(id)
	var angle := lerpf(-1.5, 1.2, 1.0 - player.attack_time / SlicePlayer.ATTACK_DURATION)
	var blade := Vector2(cos(angle) * direction, sin(angle))
	var hand := player.global_position + Vector2(4 * direction, -10)
	var inside := target(hand + blade * (stats.reach - 0.3))
	var outside := target(hand + blade * (stats.reach + 0.3))
	await frames(2)
	player._update_sword()
	player._update_sword()
	check(is_equal_approx(inside.damage_received, stats.damage) and inside.hits == 1 and outside.hits == 0, id + " physical tip/damage/unique contact direction " + str(direction))
	var shape: RectangleShape2D = player.get_node("AttackArea/Shape").shape
	check(is_equal_approx(shape.size.x, stats.reach), id + " blade retains exact fractional reach")
func projectile_bounds(id: String, direction: int) -> void:
	await spawn()
	equip(id)
	player.set_physics_process(false)
	player.facing = direction
	var stats := WeaponCatalog.stats(id)
	player._fire_arrow()
	var arrow: Node2D = shots[0]
	arrow.set_physics_process(false)
	var inside := target(arrow.origin + Vector2(direction * (stats.reach - 0.3), 0))
	var outside := target(arrow.origin + Vector2(direction * (stats.reach + 0.3), 0))
	await frames(2)
	arrow._physics_process(5.0)
	arrow._physics_process(5.0)
	check(is_equal_approx(inside.damage_received, stats.damage) and inside.hits == 1 and outside.hits == 0 and arrow.is_queued_for_deletion(), id + " swept tip/damage/unique impact direction " + str(direction))
	await spawn()
	equip(id)
	player.set_physics_process(false)
	player.facing = direction
	player._fire_arrow()
	arrow = shots[0]
	arrow.set_physics_process(false)
	var origin: Vector2 = arrow.origin
	arrow._physics_process(5.0)
	check(arrow.is_queued_for_deletion() and arrow.global_position.is_equal_approx(origin + Vector2(direction * stats.reach, 0)), id + " oversized step clamps exact range")
func state_rules(id: String) -> void:
	await spawn()
	equip(id)
	var ranged: bool = WeaponCatalog.stats(id).slot == "ranged"
	Input.action_press("jump")
	await frames(3)
	Input.action_release("jump")
	Input.action_press("attack")
	await frames(2)
	Input.action_release("attack")
	check(not player.is_on_floor() and (player.bow_cooldown > 0.0 if ranged else player.attack_cooldown > 0.0), id + " airborne input starts an attack")
	if not ranged:
		var cooldown := player.attack_cooldown
		player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
		check(player.attack_time == 0.0 and player.attack_cancelled and player.attack_cooldown == cooldown, id + " projectile hurt interrupts windup without resetting timer")
	await spawn()
	equip(id)
	wall(Vector2(208, 80), Vector2(16, 240), 9)
	player.position = Vector2(194.92, 40)
	player.velocity.y = 100
	await frames(5)
	check(player.motion_state == SlicePlayer.MotionState.WALL_SLIDE, id + " fixture reaches physical wall slide")
	Input.action_press("attack")
	await frames(2)
	Input.action_release("attack")
	check(shots.size() == 1 if ranged else player.attack_cooldown == 0.0, id + " wall slide allows ranged and blocks melee")
	await spawn()
	equip(id)
	Input.action_press("attack")
	await frames(2)
	Input.action_release("attack")
	var cooldown := player.bow_cooldown if ranged else player.attack_cooldown
	paused = true
	await frames(5)
	check((player.bow_cooldown if ranged else player.attack_cooldown) == cooldown, id + " pause preserves active slot cooldown")
	paused = false

func run() -> void:
	for base in WeaponCatalog.BASES:
		for level in range(6):
			var id := str(base) + str(level)
			await cadence(id)
			await state_rules(id)
			for direction in [-1, 1]:
				if WeaponCatalog.stats(id).slot == "melee": await melee_bounds(id, direction)
				else: await projectile_bounds(id, direction)
	await spawn()
	var other: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	room.add_child(other)
	player.configure_loadout({"melee": "Halberds5", "ranged": "ThrowingKnives5"})
	check(other.get_node("AttackArea/Shape").shape.size == Vector2(24, 4), "upgrading one instance leaves another player's blade unchanged")
	player.attack_cooldown = 0.8
	player.bow_cooldown = 0.9
	player.attack_time = 0.2
	player.configure_loadout({"melee": "Sword5", "ranged": "Longbow5"})
	check(player.attack_cooldown == 0.8 and player.bow_cooldown == 0.9 and player.attack_time == 0.0 and player.attack_cancelled, "replacement preserves both slot timers and cancels old contact")
	player.configure_loadout({"melee": "Legendary0", "ranged": ""})
	check(player.equipment.melee == "Sword5" and player.equipment.ranged == "Longbow5", "invalid loadout cannot mutate equipped slots")
	await spawn()
	player.configure_loadout({"melee": "Sword0", "ranged": "Longbow0"})
	player.active_slot = 1
	player._fire_arrow()
	check(player._shot_frame() == 0, "actual shot begins release presentation")
	player.configure_loadout({"melee": "Sword0", "ranged": "ThrowingKnives5"})
	check(player._shot_frame() == -1 and player.bow_cooldown == 2.0, "ranged replacement cancels old release without changing cadence")
	await frames(75)
	check(player._shot_frame() == -1 and player.bow_cooldown > 0.0, "old release cannot replay when timer crosses the new interval")
	for ranged in ["Longbow5", "ThrowingKnives5"]:
		await spawn()
		equip(ranged)
		Input.action_press("attack")
		await frames(2)
		Input.action_release("attack")
		var arrow: Node2D = shots[0]
		var at: Vector2 = arrow.global_position
		var cooldown := player.bow_cooldown
		paused = true
		await frames(12)
		check(arrow.global_position == at and player.bow_cooldown == cooldown, ranged + " pause freezes flight and slot timer")
		paused = false
		await frames(2)
		check(arrow.global_position.x > at.x and player.bow_cooldown < cooldown, ranged + " resumes flight and timer")
		player.die()
		await frames(2)
		check(not is_instance_valid(arrow), ranged + " death removes projectile")
	# Occlusion uses true terrain shapes for both weapon families.
	for id in ["Halberds5", "ThrowingKnives5"]:
		await spawn()
		equip(id)
		var enemy := target(Vector2(185, 190))
		wall(Vector2(175, 180), Vector2(1, 40))
		await frames(2)
		Input.action_press("attack")
		await frames(24)
		Input.action_release("attack")
		check(enemy.hits == 0, id + " one pixel terrain occludes contact")
	room.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " standard weapons checks; ", failures, " failures")
	quit(failures)

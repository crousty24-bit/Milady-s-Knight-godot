extends SceneTree

class RegisteredRoom extends Node2D:
	func register_enemy(_enemy: Node) -> void: pass

var checks: int = 0
var failures: int = 0
var room: Node2D
var player: SlicePlayer

func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for _i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func solid(at: Vector2, size: Vector2) -> void:
	var body := StaticBody2D.new()
	body.position = at
	body.collision_layer = 1
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	body.add_child(shape)
	room.add_child(body)
func cleanup() -> void:
	if not is_instance_valid(room): return
	paused = true
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for emitter in room.find_children("*", audio_type, true, false): emitter.stop()
	OS.delay_msec(300)
	room.queue_free()
	await frames(2)
	paused = false
func fixture(at: Vector2, width: float = 1600.0) -> void:
	await cleanup()
	room = RegisteredRoom.new()
	root.add_child(room)
	current_scene = room
	solid(Vector2(100, 208), Vector2(width, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = at
	room.add_child(player)
	player.controls_enabled = false
	await frames(5)
	player.set_physics_process(false)
func mob(scene: String) -> CharacterBody2D:
	var enemy = load("res://scenes/" + scene + ".tscn").instantiate()
	enemy.position = Vector2(100, 200)
	# Sentries isolate range decisions from movement during boundary checks.
	enemy.patrol_left = 0.0
	enemy.patrol_right = 0.0
	room.add_child(enemy)
	return enemy

func ranged_profile(scene: String) -> void:
	for direction in [-1, 1]:
		await fixture(Vector2(100 + direction * 362, 200))
		var enemy = mob(scene)
		enemy.chase_speed = 0.0
		await frames(3)
		check(not enemy.aggro, scene + " does not acquire at 362px")
		player.position.x = 100 + direction * 358
		await frames(3)
		check(enemy.aggro and enemy.pending_attack == &"", scene + " acquires at 358px without firing outside 240px")
		player.position.x = 100 + direction * 242
		await frames(3)
		check(enemy.pending_attack == &"", scene + " does not fire at 242px")
		player.position.x = 100 + direction * 238
		await frames(3)
		check(enemy.pending_attack == (&"arrow" if scene == "skeleton_archer" else &"blast"), scene + " starts announced attack at 238px")
		var committed: Vector2 = enemy.attack_target
		var start: Vector2 = enemy.position
		if scene == "blight_sorcerer": player.position.x += direction * 30
		await frames(22)
		check(enemy.active_attacks.size() == 1, scene + " releases the extended-range attack")
		if scene == "skeleton_archer":
			check(enemy.position == start and enemy.velocity.x == 0.0, "archer remains stationary during ranged aggro")
		else:
			check(enemy.active_attacks.size() == 1 and enemy.active_attacks[0].global_position == committed, "sorcerer ground warning retains its committed point after player movement")
	await fixture(Vector2(338, 200))
	var blocked = mob(scene)
	blocked.chase_speed = 0.0
	solid(Vector2(210, 170), Vector2(16, 60))
	await frames(5)
	check(not blocked.aggro and blocked.pending_attack == &"", scene + " cannot acquire or fire through terrain")
	await fixture(Vector2(338, 200))
	var retained = mob(scene)
	retained.chase_speed = 0.0
	await frames(3)
	# Block the next attack while aggro is retained; leave the already committed one intact.
	retained.windup_time = 0.0
	retained.pending_attack = &""
	retained.cooldown = 0.0
	solid(Vector2(210, 170), Vector2(16, 60))
	await frames(5)
	check(retained.aggro and retained.pending_attack == &"" and retained.active_attacks.is_empty(), scene + " retained aggro cannot initiate a new attack through terrain")

func elite_profile(scene: String, speed: float, edge_limit: float) -> void:
	await fixture(Vector2(300, 200))
	var enemy = mob(scene)
	await frames(3)
	var start_x: float = enemy.position.x
	await frames(30)
	check(enemy.aggro and is_equal_approx(enemy.velocity.x, speed), scene + " uses its increased chase speed during actual physics")
	check(absf(enemy.position.x - start_x - speed * 0.5) < 1.1, scene + " covers the expected chase distance in 30 physics frames")
	await fixture(Vector2(300, 200), 160.0)
	var edge = mob(scene)
	await frames(180)
	check(edge.aggro and edge.is_on_floor() and edge.position.x <= edge_limit and edge.velocity.x == 0.0, scene + " stops before an unsupported edge at the increased chase speed")
	await fixture(Vector2(300, 200))
	solid(Vector2(150, 196), Vector2(16, 8))
	var wall = mob(scene)
	var highest := 200.0
	for _tick in range(180):
		await frames(1)
		highest = minf(highest, wall.position.y)
	print("OBSERVATION ", scene, " low obstacle x=", wall.position.x, " y=", wall.position.y, " apex=", highest)
	check(highest < 192 and wall.aggro and wall.is_on_floor() and wall.position.x > 178 and wall.velocity.x > 0.0, scene + " jumps the low solid obstacle while retaining visible pursuit")

func run() -> void:
	await ranged_profile("skeleton_archer")
	await ranged_profile("blight_sorcerer")
	await elite_profile("bloated_slime", 60.0, 155.1)
	await elite_profile("chud_blob", 48.0, 159.1)
	await cleanup()
	print("RESULT %d tuning checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

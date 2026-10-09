extends SceneTree

class RegisteredRoom extends Node2D:
	func register_enemy(_enemy: Node) -> void: pass

var room: Node2D
var checks := 0
var failures := 0

func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for _i in range(count):
		await physics_frame
		await process_frame
func action(name: StringName, pressed: bool) -> void:
	var event := InputEventAction.new()
	event.action = name
	event.pressed = pressed
	Input.parse_input_event(event)
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func cleanup() -> void:
	for name in [&"jump", &"move_left", &"move_right"]: action(name, false)
	if not is_instance_valid(room): return
	paused = true
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for emitter in room.find_children("*", audio_type, true, false): emitter.stop()
	OS.delay_msec(300)
	room.queue_free()
	await frames(2)
	paused = false

func dodge(gap: float, delay: int, dir: int, speed: float = -1.0) -> Dictionary:
	await cleanup()
	room = RegisteredRoom.new()
	root.add_child(room)
	current_scene = room
	var floor_body := StaticBody2D.new()
	floor_body.position = Vector2(0, 208)
	var floor_shape := CollisionShape2D.new()
	floor_shape.shape = RectangleShape2D.new()
	floor_shape.shape.size = Vector2(2400, 16)
	floor_body.add_child(floor_shape)
	room.add_child(floor_body)
	var player: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(-dir * gap, 200)
	room.add_child(player)
	var enemy = load("res://scenes/bloated_slime.tscn").instantiate()
	enemy.position = Vector2(0, 200)
	enemy.patrol_left = 0.0
	enemy.patrol_right = 0.0
	if speed >= 0.0: enemy.chase_speed = speed
	room.add_child(enemy)
	await frames(3)
	var before := player.health
	var actual_double := false
	var crossed := false
	var highest := player.position.y
	var hit_tick := -1
	var hit_offset := Vector2.ZERO
	action(&"move_right" if dir == 1 else &"move_left", true)
	action(&"jump", true)
	for tick in range(90):
		if tick == delay - 1: action(&"jump", false)
		if tick == delay: action(&"jump", true)
		if tick == delay + 10: action(&"jump", false)
		await frames(1)
		if player.health < before and hit_tick < 0:
			hit_tick = tick
			hit_offset = player.position - enemy.position
		actual_double = actual_double or player.jump_flash > 0.0
		crossed = crossed or (player.position.x - enemy.position.x) * dir > 35.0
		highest = minf(highest, player.position.y)
	var result := {"gap": gap, "delay": delay, "dir": dir, "speed": enemy.chase_speed, "health_before": before, "health_after": player.health, "double": actual_double, "crossed": crossed, "apex": highest, "player_x": player.position.x, "mob_x": enemy.position.x, "hit_tick": hit_tick, "hit_offset": hit_offset}
	print("DODGE ", result)
	return result

func native_n2_dodge() -> void:
	await cleanup()
	var level = load("res://scenes/blight_town.tscn").instantiate()
	var enemy = level.get_node("Enemies/Enemy10")
	for other in level.get_node("Enemies").get_children():
		if other != enemy: other.free()
	var player: SlicePlayer = level.get_node("Player")
	# Test arrival from the right on the existing supported N2 floor.
	player.position = enemy.position + Vector2(48, 0)
	room = level
	root.add_child(level)
	current_scene = level
	await frames(3)
	var before := player.health
	var start := player.position
	var actual_double := false
	var crossed := false
	action(&"move_left", true)
	action(&"jump", true)
	for tick in range(90):
		if tick == 19: action(&"jump", false)
		if tick == 20: action(&"jump", true)
		if tick == 30: action(&"jump", false)
		await frames(1)
		actual_double = actual_double or player.jump_flash > 0.0
		crossed = crossed or player.position.x < enemy.position.x - 35.0
	print("NATIVE N2 DODGE start=", start, " player=", player.position, " mob=", enemy.position, " health=", player.health, " double=", actual_double)
	check(actual_double and crossed, "authored N2 floor permits an actual double jump across Enemy10")
	check(player.health == before and not player.dead, "authored N2 double jump retains health and escapes the chasing Bloated")

func run() -> void:
	var level = load("res://scenes/blight_town.tscn").instantiate()
	for node_name in ["Enemy10", "Enemy23"]:
		var authored = level.get_node("Enemies/" + node_name)
		check(authored.kind == 0 and is_equal_approx(authored.chase_speed, 44.0), "N2 " + node_name + " inherits the bounded Bloated chase reduction")
		check(authored.get_node("CollisionShape2D").shape.size == Vector2(44, 40), "N2 " + node_name + " retains its full physical/art body")
	level.free()
	for dir in [-1, 1]:
		var baseline := await dodge(64.0, 20, dir, 60.0)
		check(baseline.double and baseline.crossed and baseline.health_after == baseline.health_before - 1.5, "old 60px/s chase reproduces a damaging double-jump catch in direction%d" % dir)
	# Flat supported floor isolates the chase/contact interaction from level hazards.
	# Inputs and player physics are real; no shield, damage suppression or teleport.
	for dir in [-1, 1]:
		for gap in [48.0, 56.0, 64.0]:
			var result := await dodge(gap, 20, dir)
			var label := "double jump gap%d dir%d" % [int(gap), dir]
			check(result.double and result.apex < 135.0, label + " executes both real jump inputs")
			check(result.crossed, label + " passes to the opposite side of the chasing body")
			check(result.health_after == result.health_before, label + " retains health through landing and escape")
	await native_n2_dodge()
	await cleanup()
	print("RESULT %d Bloated dodge checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

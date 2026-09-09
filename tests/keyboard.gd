# Key events exercise project.godot mappings, rather than the route driver's action names.
extends SceneTree
var failures := 0
var checks := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func run() -> void:
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	var player: SlicePlayer = level.get_node("Player")
	await frames(10)
	var start: float = player.position.x
	key(KEY_D, true)
	await frames(12)
	key(KEY_D, false)
	check(player.position.x > start + 10, "D key walks right")
	start = player.position.x
	key(KEY_Q, true)
	await frames(20)
	key(KEY_Q, false)
	check(player.position.x < start - 8, "Q key walks left")
	await frames(10)
	var pos := player.position
	key(KEY_Z, true)
	key(KEY_S, true)
	await frames(4)
	check(Input.is_action_pressed("move_up") and Input.is_action_pressed("move_down") and player.position.distance_to(pos) < 1, "Z/S stay mapped without vertical walking")
	key(KEY_Z, false)
	key(KEY_S, false)
	key(KEY_SPACE, true)
	await frames(4)
	check(player.velocity.y < 0 and not player.is_on_floor(), "SPACE key jumps")
	key(KEY_SPACE, false)
	key(KEY_F, true)
	await frames(2)
	check(player.attack_time > 0, "F key attacks in air")
	key(KEY_F, false)
	key(KEY_E, true)
	await frames(2)
	check(Input.is_action_pressed("interact") and not level.gate.opened, "E maps to interaction and cannot pay remotely")
	key(KEY_E, false)
	key(KEY_R, true)
	await frames(4)
	key(KEY_R, false)
	await frames(6)
	level = current_scene
	player = level.get_node("Player")
	check(player.position.x < 50 and player.health == 3 and level.gold == 0 and not player.wall_jump_lockout, "R key restarts the complete attempt and movement state")
	key(KEY_ESCAPE, true)
	await frames(2)
	check(paused, "ESCAPE key pauses")
	key(KEY_ESCAPE, false)
	await frames(2)
	key(KEY_ESCAPE, true)
	await frames(2)
	key(KEY_ESCAPE, false)
	check(not paused, "ESCAPE key resumes")
	level.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " keyboard checks; ", failures, " failures")
	quit(failures)

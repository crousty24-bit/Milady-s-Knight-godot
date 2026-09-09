# Run without --fixed-fps: inputs are scheduled by physics, independently of rendering.
extends SceneTree
var failures := 0
var checks := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await physics_frame
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
	check(Engine.physics_ticks_per_second == 60 and player.is_on_floor(), "60Hz physics with independently capped rendering")
	Input.action_press("jump")
	await frames(20)
	Input.action_release("jump")
	await frames(2)
	Input.action_press("jump")
	await frames(3)
	check(player.velocity.y < -180 and not player.can_double_jump, "double jump works at this render cadence")
	Input.action_release("jump")
	Input.action_press("attack")
	await frames(3)
	check(player.attack_time > 0 and not player.is_on_floor(), "aerial attack works at this render cadence")
	Input.action_release("attack")
	await frames(22)
	player.position = Vector2(618.925, 0)
	player.velocity = Vector2(0, 45)
	await frames(6)
	check(player.motion_state == SlicePlayer.MotionState.WALL_SLIDE and player.velocity.y <= 35.01, "wall slide cap is stable")
	Input.action_press("jump")
	await frames(3)
	check(player.wall_jump_lockout and player.velocity.x < -80, "wall jump works at this render cadence")
	Input.action_release("jump")
	await frames(3)
	var before := player.velocity.y
	Input.action_press("jump")
	await frames(3)
	check(player.wall_jump_lockout and not player.can_double_jump and player.velocity.y > before, "double jump stays forbidden after wall jump")
	Input.action_release("jump")
	# Let the intentionally buffered, rejected press expire before the next fixture lands.
	await frames(12)
	var ferry = level.get_node("Platforms/Ferry")
	player.position = ferry.position + Vector2(0, -4)
	player.velocity = Vector2.ZERO
	await frames(8)
	var offset: float = player.position.x - ferry.position.x
	check(player.is_on_floor(), "platform fixture has landed before testing transport")
	await frames(40)
	check(player.is_on_floor() and absf(player.position.x - ferry.position.x - offset) < 2, "moving platform carries player at this render cadence")
	Input.action_press("jump")
	await frames(4)
	check(not player.is_on_floor() and player.velocity.y < 0, "jump leaves moving platform at this render cadence")
	Input.action_release("jump")
	await frames(30)
	print("RENDER FPS ", Engine.get_frames_per_second(), " / PHYSICS HZ ", Engine.physics_ticks_per_second)
	level.get_node("Music").stop()
	await create_timer(0.3).timeout
	level.queue_free()
	await process_frame
	OS.delay_msec(150)
	print("RESULT ", checks, " render timing checks; ", failures, " failures")
	quit(failures)

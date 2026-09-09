extends SceneTree
var failures := 0
var checks := 0
var level: Node2D
var player: SlicePlayer
var ferry: AnimatableBody2D
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
	for action in ["move_left", "move_right", "jump"]: Input.action_release(action)
	if is_instance_valid(level):
		level.queue_free()
		await frames(3)
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	player = level.get_node("Player")
	ferry = level.get_node("Platforms/Ferry")
	await frames(5)
func run() -> void:
	for from_left in [true, false]:
		await spawn()
		ferry.elapsed = 3.9 if from_left else 1.9
		player.position = Vector2(793 if from_left else 983, 48)
		player.velocity = Vector2.ZERO
		await frames(2)
		Input.action_press("move_right" if from_left else "move_left")
		await frames(18)
		check(player.is_on_floor() and absf(player.position.y - 48) < 1 and (player.position.x > 816 if from_left else player.position.x < 960), "walk onto docked ferry without a step, side=" + str(from_left))
		Input.action_release("move_right")
		Input.action_release("move_left")
		await frames(10)
		var offset: float = player.position.x - ferry.position.x
		await frames(45)
		check(player.is_on_floor() and absf(player.position.x - ferry.position.x - offset) < 1, "ferry carries stationary player, side=" + str(from_left))
		Input.action_press("jump")
		await frames(4)
		check(not player.is_on_floor() and player.velocity.y < 0, "jump cleanly leaves moving ferry, side=" + str(from_left))
		Input.action_release("jump")
	for phase in [0.25, 1.25, 2.25, 3.25]:
		await spawn()
		ferry.elapsed = phase
		await frames(2)
		var future: float = ferry.elapsed + 0.30
		player.position = Vector2(816 + 144 * (0.5 - 0.5 * cos(future * TAU / 4)), 12)
		player.velocity = Vector2.ZERO
		await frames(24)
		check(player.is_on_floor() and absf(player.position.y - 48) < 1 and absf(player.position.x - ferry.position.x) < 18, "falling onto moving platform at phase %.2f" % phase)
		# Horizontal input must move the rider relative to the deck.
		var before: float = player.position.x - ferry.position.x
		var action: String = "move_left" if before > 0 else "move_right"
		Input.action_press(action)
		await frames(5)
		Input.action_release(action)
		check(player.is_on_floor() and absf(player.position.x - ferry.position.x - before) > 1, "walking along moving deck at phase %.2f" % phase)
	level.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " platform checks; ", failures, " failures")
	quit(failures)

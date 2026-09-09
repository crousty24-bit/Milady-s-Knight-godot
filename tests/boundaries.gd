extends SceneTree
var failures := 0
var checks := 0
var level: Node2D
var player: SlicePlayer
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
	for action in ["jump", "move_left", "move_right", "attack"]: Input.action_release(action)
	if is_instance_valid(level):
		level.queue_free()
		await frames(3)
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	player = level.get_node("Player")
	await frames(5)
func run() -> void:
	await spawn()
	player.position = Vector2(2044, 144)
	player.velocity = Vector2.ZERO
	await frames(3)
	Input.action_press("move_right")
	var gripped := false
	var furthest := player.position.x
	for i in range(180):
		if i % 20 == 0: Input.action_press("jump")
		if i % 20 == 18: Input.action_release("jump")
		await frames(1)
		gripped = gripped or player.wall_normal != 0
		furthest = maxf(furthest, player.position.x)
	check(furthest < 2072 and not level.finished and not level.gate.opened, "repeated ground/double jumps cannot bypass sealed gate")
	check(not gripped, "gate never grants a wall jump")
	for left in [true, false]:
		await spawn()
		player.position = Vector2(12 if left else 2228, 144)
		player.velocity = Vector2.ZERO
		await frames(3)
		Input.action_press("move_left" if left else "move_right")
		gripped = false
		for i in range(180):
			if i % 20 == 0: Input.action_press("jump")
			if i % 20 == 18: Input.action_release("jump")
			await frames(1)
			gripped = gripped or player.wall_normal != 0
		check(not gripped and player.position.x > 0 and player.position.x < 2240, "outer boundary prevents escaping and wall climbing, left=" + str(left))
	# No ferry assistance: isolate the authored gap by hiding only its physics in this fixture.
	# Full route tests use the unmodified moving platform and public input actions exclusively.
	var max_reach := 0.0
	for delay in [5, 15, 25, 35, 40]:
		await spawn()
		level.get_node("Platforms/Ferry").queue_free()
		player.position = Vector2(797, 48)
		player.velocity = Vector2.ZERO
		await frames(3)
		Input.action_press("move_right")
		Input.action_press("jump")
		for i in range(120):
			if i == delay - 1: Input.action_release("jump")
			if i == delay: Input.action_press("jump")
			await frames(1)
			if player.position.y > 49: break
			max_reach = maxf(max_reach, player.position.x)
	check(max_reach < 976 - 5, "double jump cannot cross 176px ferry gap unaided (furthest x=%.1f)" % max_reach)
	await spawn()
	player.position = Vector2(664, 48)
	player.velocity = Vector2.ZERO
	await frames(3)
	Input.action_press("jump")
	for i in range(60):
		if i == 20: Input.action_release("jump")
		if i == 21: Input.action_press("jump")
		await frames(1)
	check(is_instance_valid(level.get_node_or_null("Coins/Coin11")) and level.gold == 0, "wall summit reward cannot be taken by a double jump from the shaft floor")
	for action in ["jump", "move_left", "move_right"]: Input.action_release(action)
	level.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " boundary checks; ", failures, " failures")
	quit(failures)

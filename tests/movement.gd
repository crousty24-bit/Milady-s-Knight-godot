extends SceneTree
var failures: int = 0
func _initialize() -> void:
	call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
func check(ok: bool, label: String) -> void:
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func run() -> void:
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	await frames(10)
	var player = level.get_node("Player")
	check(player.is_on_floor(), "spawn on floor")
	var start: float = player.position.x
	Input.action_press("move_right")
	await frames(30)
	Input.action_release("move_right")
	check(player.position.x > start + 35, "horizontal movement through physics")
	Input.action_press("jump")
	await frames(3)
	Input.action_release("jump")
	await frames(1)
	check(player.velocity.y < 0, "jump leaves floor")
	var previous: float = player.velocity.y
	Input.action_press("jump")
	await frames(2)
	Input.action_release("jump")
	check(player.velocity.y > previous, "air input does not double jump")
	await frames(50)
	check(player.is_on_floor(), "landing on terrain")
	if DisplayServer.get_name() != "headless":
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://work/stage1.png")
	level.queue_free()
	await process_frame
	OS.delay_msec(150)
	quit(failures)

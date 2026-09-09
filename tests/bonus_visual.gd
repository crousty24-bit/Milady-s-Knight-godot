extends SceneTree
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await physics_frame
func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://work/" + name + ".png")
	print("CAPTURE ", name)
func run() -> void:
	root.get_node("Progression").banked_bonus = 20
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	var player: SlicePlayer = level.get_node("Player")
	player.position = Vector2(315, 144)
	player.controls_enabled = false
	player.get_node("Camera2D").reset_smoothing()
	await frames(10)
	level.get_node("Enemies/Slime1").take_damage(3, Vector2.ZERO)
	await frames(4)
	await capture("bonus-earned")
	level._on_collected(14)
	await capture("bonus-threshold")
	level.try_offering()
	level._on_exit(player)
	await frames(40)
	await capture("bonus-banked")
	level.get_node("Music").stop()
	await create_timer(0.3).timeout
	level.queue_free()
	await process_frame
	OS.delay_msec(150)
	quit()

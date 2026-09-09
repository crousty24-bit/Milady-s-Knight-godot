extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var prefix := "collisions-" if debug_collisions_hint else ""
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	var player = level.get_node("Player")
	player.controls_enabled = false
	for item in [["village",Vector2(170,144)],["branches",Vector2(560,192)],["wall",Vector2(608,48)],["summit",Vector2(696,-64)],["upper",Vector2(1000,48)],["corruption",Vector2(1750,144)],["gate",Vector2(2030,144)]]:
		player.position = item[1]
		player.velocity = Vector2.ZERO
		player.invulnerability = 20
		player.get_node("Camera2D").reset_smoothing()
		for i in range(20): await physics_frame
		player.sprite.modulate = Color.WHITE
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://work/"+prefix+item[0]+".png")
		print("CAPTURE ",item[0])
	player.controls_enabled = true
	player.position = Vector2(315,144)
	player.velocity = Vector2.ZERO
	player.facing = 1
	player.get_node("Camera2D").reset_smoothing()
	for i in range(4): await physics_frame
	Input.action_press("attack")
	for i in range(7): await physics_frame
	Input.action_release("attack")
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://work/"+prefix+"combat.png")
	player.die()
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://work/"+prefix+"death.png")
	level.get_node("Music").stop()
	for i in range(20): await physics_frame
	level.queue_free()
	await process_frame
	OS.delay_msec(150)
	quit()

extends SceneTree
var failures := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func run() -> void:
	for sample in [[Vector2(1088, 224), "floor"], [Vector2(2192, 112), "wall"]]:
		var level = load("res://scenes/vertical_slice.tscn").instantiate()
		root.add_child(level)
		current_scene = level
		var player: SlicePlayer = level.get_node("Player")
		player.position = sample[0]
		player.controls_enabled = false
		player.set_physics_process(false)
		for enemy in level.get_node("Enemies").get_children(): enemy.set_physics_process(false)
		await frames(4)
		player.get_node("Camera2D").reset_smoothing()
		await frames(3)
		await RenderingServer.frame_post_draw
		var error := root.get_texture().get_image().save_png("res://work/run-008-spikes-%s.png" % sample[1])
		print("PASS " if error == OK else "FAIL ", "spikes capture ", sample[1])
		if error != OK: failures += 1
		level.queue_free()
		await frames(3)
	OS.delay_msec(200)
	print("RESULT 2 spikes visual checks; ", failures, " failures")
	quit(failures)

# RUN-013/029: capture representative framings of the slice at 640x360.
# Default output: work/run-029/slice/. Override with: -- --out=work/some/dir
extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var out := "res://work/run-029/slice"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="): out = "res://" + arg.trim_prefix("--out=").trim_prefix("res://")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	level.get_node("Music").stop()
	var player = level.get_node("Player")
	player.controls_enabled = false
	# Freeze enemies so the knight keeps its ordinary appearance in every framing.
	for enemy in level.get_node("Enemies").get_children(): enemy.set_physics_process(false)
	for item in [["village",Vector2(170,144)],["cart",Vector2(420,144)],["branches",Vector2(560,192)],["wall",Vector2(608,48)],["summit",Vector2(696,-64)],["upper",Vector2(1000,48)],["lower",Vector2(1000,224)],["spikes",Vector2(1080,224)],["corruption",Vector2(1750,144)],["gate",Vector2(2030,144)]]:
		player.position = item[1]
		player.velocity = Vector2.ZERO
		player.get_node("Camera2D").reset_smoothing()
		for i in range(20): await physics_frame
		player.sprite.modulate = Color.WHITE
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("%s/%s.png" % [out, item[0]])
		print("CAPTURE ", item[0])
	level.queue_free()
	await process_frame
	OS.delay_msec(150)
	print("RESULT 0 slice captures; 0 failures")
	quit()

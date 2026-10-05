extends SceneTree

func _initialize() -> void:
	call_deferred("capture")

func capture() -> void:
	var knight := (load("res://assets/sprites/knight.png") as Texture2D).get_image().get_region(Rect2i(0, 0, 32, 32))
	var slime := (load("res://assets/sprites/slime_green.png") as Texture2D).get_image().get_region(Rect2i(0, 24, 24, 24))
	print("OPAQUE knight=%s slime=%s" % [knight.get_used_rect(), slime.get_used_rect()])
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 360)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var scene := load("res://scenes/scale_comparison.tscn") as PackedScene
	for grid in [16, 32]:
		var sample := scene.instantiate() as Node2D
		sample.set("grid_size", grid)
		viewport.add_child(sample)
		for frame in 3:
			await process_frame
		var path := "res://docs/media/run-003-scale-%d.png" % grid
		var result := viewport.get_texture().get_image().save_png(path)
		print("CAPTURE %s result=%d" % [path, result])
		sample.queue_free()
		await process_frame
	quit()

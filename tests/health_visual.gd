# Graphical inspection fixture for RUN-006 HUD states.
extends SceneTree
func _initialize() -> void: call_deferred("run")
func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var error := root.get_texture().get_image().save_png("res://work/run-006-health-%s.png" % name)
	print("CAPTURE ", name, " ", error)
func run() -> void:
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	var player: SlicePlayer = level.get_node("Player")
	player.controls_enabled = false
	for i in range(4): await physics_frame
	await capture("full")
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SOLID_TRAP)
	await capture("half")
	level.hud.set_health(0.2, 3.0)
	await capture("rounded")
	level.queue_free()
	await process_frame
	OS.delay_msec(150)
	quit()

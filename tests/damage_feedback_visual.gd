# Inspect the real damage shader and blinking in the authored slice.
extends SceneTree
var failures := 0
var checks := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func run() -> void:
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	var player: SlicePlayer = level.get_node("Player")
	player.position = Vector2(315, 144)
	player.controls_enabled = false
	for enemy in level.get_node("Enemies").get_children(): enemy.set_physics_process(false)
	await frames(4)
	player.get_node("Camera2D").reset_smoothing()
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
	var previous := 0
	for sample in [[3, "flash", 1.0, 1.0], [9, "blink-dim", 0.0, 0.25], [15, "blink-visible", 0.0, 1.0], [69, "protected-end", 0.0, 0.25], [72, "normal", 0.0, 1.0]]:
		await frames(sample[0] - previous)
		previous = sample[0]
		await RenderingServer.frame_post_draw
		var error := root.get_texture().get_image().save_png("res://work/run-007-protection-%s.png" % sample[1])
		var ok: bool = error == OK and player.hurt_material.get_shader_parameter("white_flash") == sample[2] and is_equal_approx(player.sprite.modulate.a, sample[3])
		checks += 1
		print("PASS " if ok else "FAIL ", "capture ", sample[1], " invulnerability=", player.invulnerability)
		if not ok: failures += 1
	level.queue_free()
	await frames(5)
	OS.delay_msec(300)
	print("RESULT ", checks, " damage feedback visual checks; ", failures, " failures")
	quit(failures)

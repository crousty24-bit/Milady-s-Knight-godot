# Render the actual Sword gesture on both sides in the authored slice.
extends SceneTree
var failures := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func run() -> void:
	for facing in [1, -1]:
		var level = load("res://scenes/vertical_slice.tscn").instantiate()
		root.add_child(level)
		current_scene = level
		var player: SlicePlayer = level.get_node("Player")
		player.position = Vector2(315, 144)
		player.facing = facing
		player.get_node("Camera2D").reset_smoothing()
		# Isolate the demonstration target; damage still uses the actual physics query.
		for enemy in level.get_node("Enemies").get_children(): enemy.set_physics_process(false)
		var target: SliceSlime = level.get_node("Enemies/Slime1")
		target.position = player.position + Vector2(facing * 22, 0)
		await frames(4)
		Input.action_press("attack")
		await frames(8)
		Input.action_release("attack")
		await RenderingServer.frame_post_draw
		var name := "right" if facing == 1 else "left"
		var error := root.get_texture().get_image().save_png("res://work/run-007-sword-%s.png" % name)
		var ok: bool = error == OK and target.health == 0.5 and player.attack_time > player.ATTACK_HIT_END_TIME
		print("PASS " if ok else "FAIL ", "rendered active Sword and half-HP target on ", name)
		if not ok: failures += 1
		level.queue_free()
		await frames(3)
	OS.delay_msec(150)
	print("RESULT 2 combat visual checks; ", failures, " failures")
	quit(failures)

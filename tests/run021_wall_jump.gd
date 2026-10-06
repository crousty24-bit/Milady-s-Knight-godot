# Physical wall transitions; only room setup places the player.
extends "res://tests/mobility.gd"

func solid(pos: Vector2, size: Vector2, grippable: bool = true) -> void:
	super.solid(pos, size, grippable)
	var visual := Polygon2D.new()
	visual.polygon = PackedVector2Array([Vector2(-size.x, -size.y) * 0.5, Vector2(size.x, -size.y) * 0.5, size * 0.5, Vector2(-size.x, size.y) * 0.5])
	visual.color = Color("41404e")
	room.get_child(room.get_child_count() - 1).add_child(visual)

func capture(label: String) -> void:
	if DisplayServer.get_name() == "headless": return
	player.get_node("Camera2D").position_smoothing_enabled = false
	player.get_node("Camera2D").force_update_scroll()
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://work/run021/final-fixes/wall-" + label + ".png")

func run() -> void:
	for wall_side in [-1, 1]:
		var wall_x := 157.08 if wall_side == -1 else 194.92
		var away := "move_right" if wall_side == -1 else "move_left"
		var toward := "move_left" if wall_side == -1 else "move_right"
		for delay in [0, 3, 5]:
			await spawn(Vector2(wall_x, 40))
			player.velocity.y = 100
			await frames(3)
			check(player.motion_state == SlicePlayer.MotionState.WALL_SLIDE, "slide before departure side=%s delay=%s" % [wall_side, delay])
			if delay == 0: await capture("slide-" + str(wall_side))
			Input.action_press(away)
			await frames(delay)
			Input.action_press("jump")
			await frames(1)
			check(player.velocity.y < -240 and player.velocity.x * -wall_side > 100, "away input and jump preserve rebound side=%s delay=%s" % [wall_side, delay])
			if delay == 0: await capture("rebound-" + str(wall_side))
			check(player.wall_jump_lockout and not player.can_double_jump, "wall rebound consumes no extra aerial jump side=%s delay=%s" % [wall_side, delay])
		# Returning to the same wall should permit another jump on contact,
		# without requiring a landing or restoring a double jump.
		await spawn(Vector2(wall_x, 80))
		Input.action_press("jump")
		await frames(1)
		Input.action_release("jump")
		Input.action_press(toward)
		var returned := false
		for i in range(30):
			await frames(1)
			if player.is_on_wall():
				returned = true
				break
		check(returned, "physical same-wall contact reached side=%s" % wall_side)
		Input.action_press("jump")
		await frames(1)
		check(player.velocity.y < -240 and player.velocity.x * -wall_side > 100, "immediate repeat on actual same-wall contact side=%s" % wall_side)
	# Buffer a press just before reaching the wall with no aerial charge.
	await spawn(Vector2(185, 40))
	Input.action_press("move_right")
	Input.action_press("jump")
	var buffered := false
	for i in range(12):
		await frames(1)
		buffered = buffered or (player.wall_jump_lockout and player.velocity.y < -240 and player.velocity.x < -100)
	check(buffered, "buffered jump fires on wall arrival without aerial charge")
	# Ground coyote must not take precedence over a wall already reached.
	await spawn(Vector2(194.92, 194))
	player.coyote = 0.09
	Input.action_press("jump")
	await frames(1)
	check(player.wall_jump_lockout and player.velocity.x < -100, "wall contact wins over stale ground coyote")
	# The remembered wall expires; it must not create arbitrary aerial jumps.
	await spawn(Vector2(194.92, 40))
	Input.action_press("move_left")
	await frames(9)
	var before := player.velocity.y
	Input.action_press("jump")
	await frames(1)
	check(player.velocity.y >= before and not player.wall_jump_lockout, "wall grace expires after departure")
	for action in ["jump", "attack", "move_left", "move_right"]: Input.action_release(action)
	room.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " wall jump transition checks; ", failures, " failures")
	quit(failures)

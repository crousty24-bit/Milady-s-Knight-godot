# Physical elite navigation regressions for suspended platforms and N2 left entry.
extends "res://tests/run021_chase.gd"

func body_not_penetrating(enemy: CharacterBody2D) -> bool:
	# The planner lifts its probe 0.1px to clear a supporting floor. Use the
	# actual body transform here, otherwise valid ceiling contact looks embedded.
	var collision := enemy.get_node("CollisionShape2D") as CollisionShape2D
	var query := PhysicsShapeQueryParameters2D.new()
	query.shape = collision.shape
	query.transform = collision.global_transform
	query.collision_mask = enemy.collision_mask
	query.exclude = [enemy.get_rid()]
	query.collide_with_areas = false
	return enemy.get_world_2d().direct_space_state.intersect_shape(query, 1).is_empty()

func capture_native(label: String, level: Node2D) -> void:
	if DisplayServer.get_name() == "headless": return
	level.camera.position_smoothing_enabled = false
	level.camera.reset_smoothing()
	level.camera.force_update_scroll()
	await RenderingServer.frame_post_draw
	var path := "res://work/run021/elite-left-entry/" + label + ".png"
	check(root.get_texture().get_image().save_png(path) == OK, "saved native elite evidence " + label)

func native_left_entry(scene: String, patrol_frames: int) -> void:
	var level = load("res://scenes/blight_town.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	room = level
	player = level.get_node("Player")
	player.controls_enabled = false
	var enemy = level.get_node("Enemies/Enemy10")
	if scene == "chud_blob":
		var initial: Vector2 = enemy.position
		var patrol_bounds := Vector2(enemy.patrol_left, enemy.patrol_right)
		enemy.queue_free()
		await frames(1)
		enemy = load("res://scenes/chud_blob.tscn").instantiate()
		enemy.position = initial
		enemy.patrol_left = patrol_bounds.x
		enemy.patrol_right = patrol_bounds.y
		level.get_node("Enemies").add_child(enemy)
	await frames(patrol_frames)
	player.position = Vector2(3220, 90)
	player.velocity = Vector2.ZERO
	print("NATIVE entry ", scene, " patrol_frames=", patrol_frames, " enemy=", enemy.position)
	var acquired := false
	var advanced := false
	var landed_roof := false
	var retreated := false
	var clear_body := true
	var landed_player := false
	var bumped_ceiling := false
	var minimum_y: float = enemy.position.y
	for frame in range(540):
		await frames(1)
		acquired = acquired or enemy.aggro
		advanced = advanced or enemy.position.x < 3250
		var body_clear: bool = body_not_penetrating(enemy)
		if clear_body and not body_clear: print("NATIVE OVERLAP ", scene, " frame=", frame, " position=", enemy.position)
		clear_body = clear_body and body_clear
		landed_player = landed_player or player.is_on_floor()
		bumped_ceiling = bumped_ceiling or enemy.is_on_ceiling()
		if patrol_frames == 240 and frame == 20: await capture_native(scene + "-arrival", level)
		if enemy.chase_detour_dir != 0 and not retreated:
			retreated = true
			if patrol_frames == 240: await capture_native(scene + "-retreat", level)
		if enemy.is_on_floor() and absf(enemy.position.y - 80) < 1 and not landed_roof:
			landed_roof = true
			if patrol_frames == 240: await capture_native(scene + "-roof", level)
		minimum_y = minf(minimum_y, enemy.position.y)
		if frame % 30 == 0:
			print("NATIVE ", scene, " frame=", frame, " player=", player.position, " HP=", player.health, " enemy=", enemy.position, " velocity=", enemy.velocity, " aggro=", enemy.aggro, " seen=", enemy._sees_player(true))
		if advanced and enemy.is_on_floor() and enemy.position.y > 143: break
	print("NATIVE final ", scene, " min_y=", minimum_y, " clear=", clear_body, " aggro=", enemy.aggro, " player_dead=", player.dead)
	check(acquired and landed_player, scene + " acquires target during physical left entry in current N2 phase=" + str(patrol_frames))
	check(advanced and enemy.is_on_floor() and enemy.position.y > 143, scene + " reaches lower-left floor beyond N2 platform phase=" + str(patrol_frames))
	check(landed_roof, scene + " physically lands on N2 platform roof phase=" + str(patrol_frames))
	check(not bumped_ceiling, scene + " clears roof jump without hitting its underside phase=" + str(patrol_frames))
	check(clear_body and enemy.aggro and not player.dead, scene + " keeps collisions and pursuit through N2 encounter phase=" + str(patrol_frames))
	for kind in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for audio in level.find_children("*", kind, true, false): audio.stop()
	OS.delay_msec(300)
	level.queue_free()
	await frames(3)

func underpass(scene: String, dir: int, clearance: float) -> void:
	await fixture(Vector2(80 if dir == -1 else 280, 200))
	solid(Vector2(180, 200 - clearance - 8), Vector2(80, 16))
	var enemy = mob(scene)
	enemy.position = Vector2(200 if dir == -1 else 160, 200)
	var minimum_y := 200.0
	var clear_body := true
	for tick in range(300):
		await frames(1)
		minimum_y = minf(minimum_y, enemy.position.y)
		clear_body = clear_body and body_not_penetrating(enemy)
		if absf(enemy.position.x - player.position.x) < 35: break
	var label := "%s underpass dir=%d clearance=%d" % [scene, dir, clearance]
	check(enemy.is_on_floor() and absf(enemy.position.x - player.position.x) < 35, label + " reaches player on same floor")
	check(minimum_y > 199 and enemy.chase_detour_dir == 0, label + " walks without unnecessary jump or retreat")
	check(clear_body and enemy.aggro, label + " retains aggro without terrain penetration")

func blocked_exit(scene: String, dir: int, width: float, offset: float) -> void:
	await fixture(Vector2(60 if dir == -1 else 300, 200))
	solid(Vector2(180, 144), Vector2(width, 16))
	var edge := 180 + dir * width / 2
	solid(Vector2(edge + dir * 8, 194), Vector2(16, 12))
	var enemy = mob(scene)
	enemy.position = Vector2(180 - dir * (width / 2 - 12) + offset, 200)
	var retreated := false
	var roof_landing := false
	var clear_body := true
	var retained := true
	var acquired := false
	for tick in range(600):
		await frames(1)
		retreated = retreated or enemy.chase_detour_dir != 0
		roof_landing = roof_landing or (enemy.is_on_floor() and absf(enemy.position.y - 136) < 1)
		clear_body = clear_body and body_not_penetrating(enemy)
		acquired = acquired or enemy.aggro
		retained = retained and (not acquired or enemy.aggro)
		if enemy.is_on_floor() and enemy.position.y > 199 and absf(enemy.position.x - player.position.x) < 35: break
	var label := "%s blocked exit dir=%d width=%d offset=%.2f" % [scene, dir, width, offset]
	check(retreated, label + " retreats physically to exposed edge")
	check(roof_landing, label + " jumps onto roof before crossing")
	check(enemy.is_on_floor() and enemy.position.y > 199 and absf(enemy.position.x - player.position.x) < 35, label + " returns to lower floor near player")
	print("FIXTURE ", label, " position=", enemy.position, " clear=", clear_body, " retained=", retained, " acquired=", acquired)
	check(clear_body, label + " never penetrates terrain")
	check(acquired and retained, label + " retains pursuit after acquisition")

func elite_drops(scene: String, drop: float) -> void:
	await fixture(Vector2(220, 200))
	room.get_child(0).queue_free()
	solid(Vector2(70, 208), Vector2(140, 16))
	solid(Vector2(240, 208 + drop), Vector2(200, 16))
	var enemy = mob(scene)
	await frames(3)
	player.position.y += drop
	await frames(220)
	var label := "%s supported drop=%d" % [scene, drop]
	if drop > 72:
		check(enemy.position.x < 140 and enemy.position.y < 201, label + " refuses excessive drop")
		return
	check(enemy.is_on_floor() and enemy.position.x > 170 and absf(enemy.position.y - 200 - drop) < 1, label + " lands on supported lower floor")
	check(enemy.aggro, label + " retains pursuit after descent")
	player.position = Vector2(80, 200)
	await frames(320)
	check(enemy.is_on_floor() and enemy.position.x < 115 and enemy.position.y < 201, label + " climbs back toward reversed target")

func detour_cancellation(scene: String) -> void:
	for reason in ["side", "range", "death"]:
		await fixture(Vector2(60, 200))
		solid(Vector2(180, 144), Vector2(80, 16))
		solid(Vector2(132, 194), Vector2(16, 12))
		var enemy = mob(scene)
		enemy.position = Vector2(180, 200)
		for tick in range(120):
			await frames(1)
			if enemy.chase_detour_dir != 0: break
		check(enemy.chase_detour_dir != 0, scene + " detour active before target " + reason)
		if reason == "side":
			player.position = Vector2(300, 200)
			await frames(1)
			check(enemy.chase_detour_dir == 0 and enemy.velocity.x > 0, scene + " target side change cancels retreat")
		elif reason == "range":
			player.position = Vector2(1000, 200)
			await frames(125)
			check(not enemy.aggro and enemy.chase_detour_dir == 0, scene + " out-of-range target lost after two seconds during detour")
		else:
			player.dead = true
			await frames(1)
			check(not enemy.aggro and enemy.chase_detour_dir == 0, scene + " target death cancels pursuit and retreat")

func unsafe_retreat(scene: String) -> void:
	await fixture(Vector2(60, 200))
	solid(Vector2(180, 144), Vector2(80, 16))
	solid(Vector2(132, 194), Vector2(16, 12))
	solid(Vector2(226, 175), Vector2(12, 50))
	var enemy = mob(scene)
	enemy.position = Vector2(180, 200)
	var clear_body := true
	var detoured := false
	for tick in range(240):
		await frames(1)
		clear_body = clear_body and body_not_penetrating(enemy)
		detoured = detoured or enemy.chase_detour_dir != 0
	check(not detoured and enemy.position.x > 158 and enemy.position.y > 199, scene + " refuses retreat blocked by solid wall")
	check(clear_body, scene + " blocked underpass never penetrates ceiling or wall")

func upper_target(scene: String) -> void:
	await fixture(Vector2(80, 200))
	solid(Vector2(180, 144), Vector2(80, 16))
	var enemy = mob(scene)
	enemy.position = Vector2(180, 200)
	await frames(3)
	player.position = Vector2(180, 136)
	var reached := false
	for tick in range(420):
		await frames(1)
		if enemy.is_on_floor() and absf(enemy.position.y - 136) < 1 and absf(enemy.position.x - 180) < 35:
			reached = true
			break
	check(reached and enemy.aggro, scene + " exits underpass and climbs when retained player is on its roof")

func unsupported_retreat(scene: String) -> void:
	await fixture(Vector2(60, 200))
	room.get_child(0).queue_free()
	solid(Vector2(140, 208), Vector2(160, 16))
	solid(Vector2(180, 144), Vector2(80, 16))
	solid(Vector2(132, 194), Vector2(16, 12))
	var enemy = mob(scene)
	enemy.position = Vector2(180, 200)
	var detoured := false
	await frames(3)
	for tick in range(200):
		await frames(1)
		detoured = detoured or enemy.chase_detour_dir != 0
	check(not detoured and enemy.position.x < 198 and enemy.position.y > 199, scene + " refuses underpass retreat toward unsupported gap")

func detour_pause(scene: String) -> void:
	await fixture(Vector2(60, 200))
	solid(Vector2(180, 144), Vector2(80, 16))
	solid(Vector2(132, 194), Vector2(16, 12))
	var enemy = mob(scene)
	enemy.position = Vector2(180, 200)
	for tick in range(120):
		await frames(1)
		if enemy.chase_detour_dir != 0: break
	var before: Vector2 = enemy.position
	var goal: float = enemy.chase_detour_x
	paused = true
	await frames(30)
	check(enemy.position.is_equal_approx(before) and enemy.chase_detour_x == goal, scene + " pause freezes active overhang retreat")
	paused = false
	await frames(40)
	check(enemy.position.x > before.x + 10 and enemy.aggro, scene + " unpause resumes retreat without stale navigation state")

func run() -> void:
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	if not "native" in OS.get_cmdline_user_args():
		await synthetic_cases()
	for scene in ["bloated_slime", "chud_blob"]:
		for delay in [0, 120, 240, 360]:
			await native_left_entry(scene, delay)
	print("RESULT %d elite navigation checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

func synthetic_cases() -> void:
	for scene in ["bloated_slime", "chud_blob"]:
		for dir in [-1, 1]:
			for clearance in [42.0, 48.0]:
				await underpass(scene, dir, clearance)
			for width in [80.0, 112.0]:
				for offset in [0.0, 0.37]:
					await blocked_exit(scene, dir, width, offset)
		for drop in [32.0, 64.0, 72.0, 120.0]:
			await elite_drops(scene, drop)
		await detour_cancellation(scene)
		await unsafe_retreat(scene)
		await unsupported_retreat(scene)
		await upper_target(scene)
		await detour_pause(scene)
	room.queue_free()
	await frames(3)
	# Native cases instantiate intact N2; Chud is an explicit profile substitution.

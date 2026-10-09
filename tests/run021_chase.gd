extends SceneTree
var checks := 0
var failures := 0
var room: Node2D
var player: SlicePlayer
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func solid(at: Vector2, size: Vector2) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.position = at
	body.collision_layer = 1
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	body.add_child(shape)
	room.add_child(body)
	return body
func fixture(at := Vector2(220, 200)) -> void:
	if is_instance_valid(room):
		paused = true
		for voice_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for voice in room.find_children("*", voice_type, true, false): voice.stop()
		OS.delay_msec(300)
		room.queue_free()
		await frames(2)
	paused = false
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	solid(Vector2(250, 208), Vector2(600, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = at
	room.add_child(player)
	player.controls_enabled = false
	player.set_physics_process(false)
	await frames(2)
func mob(scene: String):
	var enemy = load("res://scenes/" + scene + ".tscn").instantiate()
	enemy.position = Vector2(100, 200)
	room.add_child(enemy)
	return enemy
func obstacle(scene: String, height: float) -> void:
	await fixture(Vector2(400, 200) if scene == "skeleton_archer" else Vector2(220, 200))
	var enemy = mob(scene)
	await frames(3)
	# First acquire normally, then insert a blocking obstacle to exercise retention.
	solid(Vector2(140, 200 - height / 2), Vector2(16, height))
	var minimum_y := 200.0
	for i in range(180):
		await frames(1)
		minimum_y = minf(minimum_y, enemy.position.y)
	print("OBSERVATION ", scene, " obstacle=", height, " x=", enemy.position.x, " y=", minimum_y)
	check(enemy.position.x > 157 and minimum_y < 200 - height, scene + " physically jumps and crosses " + str(height) + "px block")
	check(enemy.aggro, scene + " preserves normal aggro after crossing")
func limits() -> void:
	await fixture()
	var enemy = mob("skeleton_warrior")
	await frames(3)
	solid(Vector2(140, 140), Vector2(16, 120))
	await frames(100)
	check(enemy.position.x < 125 and enemy.position.y > 199, "unreachable wall remains solid and produces no futile jumps")
	check(absf(enemy.velocity.x) < 0.1, "unreachable wall physically stops pursuit before aggro-loss timing")
	await frames(125)
	check(not enemy.aggro, "blocked pursuit loses aggro after two seconds without physical progress")
	await fixture()
	enemy = mob("chud_blob")
	await frames(3)
	solid(Vector2(140, 184), Vector2(16, 32))
	solid(Vector2(100, 143), Vector2(80, 16))
	await frames(100)
	check(enemy.position.x < 115 and enemy.position.y > 199, "elite whole-body probe rejects jump under low ceiling")
	await fixture(Vector2(400, 200))
	enemy = mob("skeleton_archer")
	await frames(80)
	check(enemy.position.x > 115 and enemy.aggro, "archer pursues beyond firing range at original patrol speed")
	player.position = enemy.position + Vector2(120, 0)
	await frames(25)
	check(enemy.active_attacks.size() > 0 and absf(enemy.velocity.x) < 0.1, "archer stops and fires inside unchanged range")
	player.position = Vector2(1000, 200)
	await frames(130)
	check(not enemy.aggro, "archer original aggro-loss delay remains effective")
func area_items() -> void:
	await fixture()
	var enemy = mob("skeleton_warrior")
	var chest = load("res://scenes/reward_chest.tscn").instantiate()
	chest.position = Vector2(145, 200)
	room.add_child(chest)
	await frames(100)
	check(enemy.position.x > 160, "actual common chest Area does not block pursuit")
func traps_and_pause() -> void:
	for scene in ["retractable_spikes", "trapdoor"]:
		await fixture()
		var enemy = mob("chud_blob")
		await frames(3)
		var trap = load("res://scenes/" + scene + ".tscn").instantiate()
		trap.position = Vector2(150, 200)
		if scene == "retractable_spikes":
			trap.initial_phase = 2.1
			trap.danger_duration = 30.0
		room.add_child(trap)
		await frames(120)
		check(enemy.position.x > 168, "elite physically crosses actual " + scene)
	await fixture(Vector2(220, 200))
	var enemy = mob("skeleton_warrior")
	await frames(5)
	var before: Vector2 = enemy.position
	paused = true
	await frames(20)
	check(enemy.position.is_equal_approx(before), "pause freezes pursuing mob without losing aggro")
	paused = false
	await frames(20)
	check(enemy.position.x > before.x + 10 and enemy.aggro, "unpause resumes physical chase")
	player.position = Vector2(1000, 200)
	await frames(130)
	check(not enemy.aggro and absf(enemy.velocity.x) <= enemy.patrol_speed, "lost aggro returns to unchanged patrol locomotion")
func ledges() -> void:
	for drop in [32.0, 120.0]:
		await fixture(Vector2(220, 200 + minf(drop, 32)))
		room.get_child(0).queue_free()
		solid(Vector2(70, 208), Vector2(140, 16))
		solid(Vector2(240, 208 + drop), Vector2(200, 16))
		var enemy = mob("skeleton_warrior")
		await frames(130)
		if drop == 32:
			check(enemy.position.x > 150 and enemy.position.y > 225, "chase descends to supported lower floor")
		else:
			check(enemy.position.x < 135 and enemy.position.y < 201, "chase refuses unsupported lethal-depth drop")
	await fixture(Vector2(220, 200))
	room.get_child(0).queue_free()
	solid(Vector2(70, 208), Vector2(140, 16))
	solid(Vector2(240, 208), Vector2(168, 16))
	var enemy = mob("skeleton_warrior")
	var minimum_y := 200.0
	for i in range(140):
		await frames(1)
		minimum_y = minf(minimum_y, enemy.position.y)
	print("OBSERVATION gap x=", enemy.position.x, " minimum_y=", minimum_y)
	check(enemy.position.x > 165 and minimum_y < 190, "chase physically jumps a sixteen-pixel gap to verified support")
func elite_round_trips() -> void:
	for scene in ["bloated_slime", "chud_blob"]:
		for height in [32.0, 64.0, 72.0]:
			await fixture(Vector2(300, 200))
			var enemy = mob(scene)
			await frames(3)
			solid(Vector2(180, 200 - height / 2), Vector2(64, height))
			for crossing in range(4):
				player.position = Vector2(300 if crossing % 2 == 0 else 80, 200)
				var reached_top := false
				for frame in range(260):
					await frames(1)
					reached_top = reached_top or (enemy.position.x > 148 and enemy.position.x < 212 and enemy.position.y < 200 - height + 1)
					if enemy.is_on_floor() and enemy.position.y > 199 and absf(enemy.position.x - player.position.x) < 35: break
				print("OBSERVATION ", scene, " block=", height, " pursuit leg=", crossing, " position=", enemy.position, " aggro=", enemy.aggro)
				check(reached_top, scene + " climbs " + str(height) + "px block on pursuit leg " + str(crossing))
				check(enemy.is_on_floor() and enemy.position.y > 199 and absf(enemy.position.x - player.position.x) < 35, scene + " descends " + str(height) + "px block toward player on pursuit leg " + str(crossing))
				check(enemy.aggro, scene + " retains pursuit across block on leg " + str(crossing))
		await fixture()
		var enemy = mob(scene)
		await frames(3)
		solid(Vector2(200, 184), Vector2(16, 32))
		player.position = Vector2(1000, 200)
		var minimum_y := 200.0
		for frame in range(125):
			await frames(1)
			minimum_y = minf(minimum_y, enemy.position.y)
		check(minimum_y < 168, scene + " performs verified obstacle jump while target leaves retention range")
		check(not enemy.aggro, scene + " forgets out-of-range target after original two seconds despite terrain jump")
func run() -> void:
	for scene in ["skeleton_warrior", "skeleton_archer", "blight_sorcerer", "bloated_slime", "chud_blob"]:
		await obstacle(scene, 16)
		await obstacle(scene, 32)
	await limits()
	await area_items()
	await traps_and_pause()
	await ledges()
	await elite_round_trips()
	paused = true
	for voice_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for voice in room.find_children("*", voice_type, true, false): voice.stop()
	OS.delay_msec(300)
	room.queue_free()
	await frames(3)
	print("RESULT %d chase checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

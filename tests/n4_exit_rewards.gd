extends SceneTree
const ROOM_ENEMIES = ["Enemy26", "Enemy27", "Enemy11", "Enemy05"]
var checks := 0
var failures := 0
var level: Node2D
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func stop_audio(node: Node) -> void:
	if node is AudioStreamPlayer or node is AudioStreamPlayer2D: node.stop()
	for child in node.get_children(): stop_audio(child)
func run() -> void:
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	level = load("res://scenes/forbidden_graveyard.tscn").instantiate()
	# Keep terrain, gate, exit, and ferry physics; isolate these checks from combat.
	for group in ["Enemies", "Hazards", "Exploration"]:
		for child in level.get_node(group).get_children(): child.process_mode = Node.PROCESS_MODE_DISABLED
	root.add_child(level)
	current_scene = level
	var player: SlicePlayer = level.player
	player.controls_enabled = false
	player.set_physics_process(false)
	await frames(4)
	var before: int = level.bonus
	for name in ROOM_ENEMIES:
		var enemy = level.get_node("Enemies/" + name)
		check(enemy.bonus_reward == 2, "%s coin-room reward is two shards" % name)
		enemy.take_damage(100.0, Vector2.ZERO)
		enemy.take_damage(100.0, Vector2.ZERO)
	check(level.bonus == before+8, "four coin-room kills grant exactly eight shards without duplicates")
	check(level.get_node("Enemies/Enemy28").bonus_reward == 1 and level.get_node("Enemies/Enemy40").bonus_reward == 5, "other archer and Bloated keep original rewards")
	var ferry = level.get_node("Platforms/Ferry6")
	check(ferry.period == 4.0 and ferry.travel == Vector2(0,-144), "Ferry6 has four-second period and authored travel")
	check(level.get_node("Platforms/Ferry7").period == 6.0, "other vertical ferry retains inherited human six-second period")
	ferry.elapsed = 0
	ferry.position = ferry.origin
	await frames(120)
	check(ferry.position.distance_to(ferry.origin+ferry.travel) < 2, "Ferry6 reaches opposite endpoint after two real simulated seconds")
	await frames(120)
	check(ferry.position.distance_to(ferry.origin) < 2, "Ferry6 returns to origin after four real simulated seconds")
	check(not level._inside_void_safe_region(Vector2(4400,400)) and not level._inside_void_safe_region(Vector2(5045,561)), "void exception excludes outside and below final extension")
	# Landing inside actual ExitArea must remain safe, but cannot finish with closed gate.
	player.set_physics_process(true)
	player.position = Vector2(5045,420)
	player.velocity = Vector2.ZERO
	await frames(60)
	check(not player.dead and player.is_on_floor() and absf(player.position.y-448) < 1, "real fall lands alive on upper exit ledge below old void")
	check(not level.finished and not level.gate.opened, "actual ExitArea does not complete level before gate payment")
	level.camera.reset_smoothing()
	level.camera.force_update_scroll()
	await frames(2)
	check(root.get_visible_rect().has_point(root.get_canvas_transform()*player.global_position), "camera includes player at authored exit beyond old horizontal limit")
	player.position = Vector2(4672,330)
	player.velocity = Vector2.ZERO
	await frames(60)
	check(not player.dead and player.is_on_floor() and absf(player.position.y-368) < 1, "real fall lands alive on final gate platform")
	player.set_physics_process(false)
	var hit := player.move_and_collide(Vector2(100,0))
	check(hit != null and player.position.x < 4725, "closed final gate physically blocks approach")
	level.gold = level.gate.COST
	check(level.try_offering(), "final gate accepts required coins")
	await frames(3)
	check(level.gate.opened and level.gate.get_node("Barrier/Shape").disabled, "payment removes final gate collision")
	hit = player.move_and_collide(Vector2(70,0))
	check(hit == null and player.position.x > 4725 and not player.dead, "player physically crosses opened gate without void death")
	player.position = Vector2(4970,527.9)
	var query := PhysicsShapeQueryParameters2D.new()
	query.shape = player.get_node("CollisionShape2D").shape
	query.transform = Transform2D(0,Vector2(5045,518.9))
	query.collision_mask = 1
	check(player.get_world_2d().direct_space_state.intersect_shape(query).is_empty(), "exit corridor has enough headroom for actual player capsule")
	hit = player.move_and_collide(Vector2(75,0))
	check(hit == null and absf(player.position.x-5045) < 1, "player physically traverses lower exit corridor")
	await frames(3)
	check(level.finished and level.reward_settled and not player.dead, "actual exit overlap completes level and settles shards alive")
	paused = false
	level.paused = false
	stop_audio(level)
	OS.delay_msec(350)
	level.queue_free()
	await frames(4)
	print("RESULT %d checks; %d failures" % [checks,failures])
	quit(1 if failures else 0)

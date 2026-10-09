extends SceneTree
const NAMES = ["SkullSwarm4", "SkullSwarm5", "SkullSwarm6"]
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
	root.get_node("Progression").persistence_enabled = false
	level = load("res://scenes/forbidden_graveyard.tscn").instantiate()
	# Isolate navigation/trigger checks from combat without changing authored geometry.
	for group in ["Enemies", "Hazards"]:
		for child in level.get_node(group).get_children(): child.process_mode = Node.PROCESS_MODE_DISABLED
	for swarm in level.get_node("Exploration").get_children():
		if swarm.has_signal("swarm_started"):
			swarm.set_physics_process(false)
			swarm.swarm_started.connect(func():
				for skull in swarm.skulls: skull.set_physics_process(false))
	root.add_child(level)
	current_scene = level
	var player: SlicePlayer = level.player
	player.controls_enabled = false
	player.invulnerability = 100.0
	player.position = Vector2(2992, 280)
	player.velocity = Vector2.ZERO
	await frames(80)
	check(not player.dead and player.is_on_floor() and absf(player.position.y - 352.0) < 1, "real descent crosses void boundary and lands on new entrance ledge")
	player.position = Vector2(3136, 360)
	player.velocity = Vector2.ZERO
	await frames(50)
	check(not player.dead and player.is_on_floor() and absf(player.position.y - 416.0) < 1, "real gravity lands on lower corridor platform")
	check(level.camera.limit_bottom >= 832, "camera includes lowest authored terrain")
	player.set_physics_process(false)
	for name in NAMES:
		var swarm = level.get_node("Exploration/" + name)
		swarm.set_physics_process(true)
		for y in [144, 240, 303, 335]:
			player.position = Vector2(swarm.position.x, y)
			await frames(2)
			check(not swarm.occupied and swarm.skulls.is_empty(), "%s does not spawn above lower zone y=%d" % [name,y])
		if name == "SkullSwarm6":
			player.position = Vector2(swarm.position.x, 416)
			await frames(2)
			check(not swarm.occupied and swarm.skulls.is_empty(), "deep swarm does not activate on corridor above its shaft")
		# The two corridor swarms start at y=336; test the exact included edge
		# after rejecting y=335, while retaining each skull's full-shape query.
		var activation_y: float = 513 if name == "SkullSwarm6" else 336
		player.position = Vector2(swarm.position.x, activation_y)
		await frames(2)
		check(swarm.occupied and swarm.skulls.size() == 4, "%s spawns four skulls in its lower zone" % name)
		for skull in swarm.skulls:
			var query := PhysicsShapeQueryParameters2D.new()
			query.shape = skull.get_node("CollisionShape2D").shape
			query.transform = skull.global_transform
			query.collision_mask = 1
			check(skull.global_position.y >= 336 and skull.get_world_2d().direct_space_state.intersect_shape(query).is_empty(), "%s skull spawns below upper floor and outside solid terrain" % name)
		var before: int = level.bonus
		swarm.skulls[0].take_damage(10.0, Vector2.ZERO)
		check(level.bonus == before + 1, "%s killed slot pays one shard" % name)
		player.position.y = 240
		await frames(30)
		check(not swarm.occupied and swarm.skulls.is_empty(), "%s despawns when returning upstairs" % name)
		player.position.y = activation_y
		await frames(2)
		check(swarm.skulls.size() == 3 and level.bonus == before + 1, "%s reentry keeps defeated slot and cannot duplicate reward" % name)
		player.position.y = 240
		await frames(30)
		swarm.set_physics_process(false)
	var original = level.get_node("Exploration/SkullSwarm")
	check(original.zone_size == Vector2(480,240) and original.zone_offset == Vector2.ZERO, "original upper swarm activation stays unchanged")
	player.position = Vector2(3324, 560)
	await frames(2)
	check(not player.dead, "deep authored shaft remains safe below old void")
	player.position = Vector2(3324, 593)
	await frames(2)
	check(player.dead, "void below authored lower zone still kills through invulnerability")
	stop_audio(level)
	OS.delay_msec(350)
	level.queue_free()
	await frames(4)
	print("RESULT %d checks; %d failures" % [checks,failures])
	quit(1 if failures else 0)

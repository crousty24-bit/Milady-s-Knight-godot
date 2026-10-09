extends SceneTree
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
	for group in ["Enemies", "Hazards"]:
		for child in level.get_node(group).get_children(): child.process_mode = Node.PROCESS_MODE_DISABLED
	for node in level.get_node("Exploration").get_children():
		if node.has_signal("swarm_started"): node.set_physics_process(false)
	root.add_child(level)
	current_scene = level
	level.set_physics_process(false)
	var player: SlicePlayer = level.player
	player.set_physics_process(false)
	player.controls_enabled = false
	var swarm = level.get_node("Exploration/SkullSwarm7")
	var gate = level.get_node("Exploration/MechanismDoor5")
	swarm.swarm_started.connect(func():
		for skull in swarm.skulls: skull.set_physics_process(false))
	swarm.set_physics_process(true)
	player.position = Vector2(2752, 144)
	await frames(4)
	var hit := player.move_and_collide(Vector2(64,0))
	await frames(2)
	check(hit != null and player.position.x < 2784 and not swarm.occupied, "closed gate physically blocks entrance without spawning")
	player.position = Vector2(2848, 144)
	await frames(2)
	check(not swarm.occupied and swarm.skulls.is_empty(), "even injected interior pose cannot activate swarm with gate closed")
	player.position = Vector2(2752,144)
	level.get_node("Exploration/MechanismButton5").activate()
	await frames(3)
	check(gate.opened and gate.get_node("Barrier/Shape").disabled, "actual linked button opens required gate and removes barrier")
	check(not swarm.occupied and swarm.skulls.is_empty(), "gate opening alone does not spawn while player remains outside")
	for point in [Vector2(2760,100), Vector2(3008,100), Vector2(2918,32), Vector2(2918,160)]:
		player.position = point
		await frames(2)
		check(not swarm.occupied and swarm.skulls.is_empty(), "open gate still excludes outside pose %s" % point)
	player.position = Vector2(2760,144)
	await frames(2)
	hit = player.move_and_collide(Vector2(88,0))
	await frames(2)
	check(hit == null and absf(player.position.x-2848) < 1, "player physically crosses open doorway into room")
	check(swarm.occupied and swarm.skulls.size() == 4, "room entry through opened gate spawns four skulls")
	for skull in swarm.skulls:
		var query := PhysicsShapeQueryParameters2D.new()
		query.shape = skull.get_node("CollisionShape2D").shape
		query.transform = skull.global_transform
		query.collision_mask = 1
		check(Rect2(2784,48,208,97).has_point(skull.global_position) and skull.get_world_2d().direct_space_state.intersect_shape(query).is_empty(), "skull appears inside room in free air")
	var before: int = level.bonus
	swarm.skulls[0].take_damage(10.0, Vector2.ZERO)
	check(level.bonus == before+1, "killed skull grants its existing one-shard reward")
	for point in [Vector2(2760,100), Vector2(3008,100), Vector2(2918,32), Vector2(2918,160)]:
		player.position = point
		await frames(30)
		check(not swarm.occupied and swarm.skulls.is_empty(), "leaving room clears swarm at %s" % point)
		player.position = Vector2(2848,144)
		await frames(2)
		check(swarm.occupied and swarm.skulls.size() == 3 and level.bonus == before+1, "reentry restores only three unpaid slots")
	player.position = Vector2(2760,100)
	await frames(30)
	# A missing configured gate must remain closed, rather than bypass the contract.
	swarm.required_gate = NodePath("../MissingGate")
	player.position = Vector2(2848,144)
	await frames(2)
	check(not swarm.occupied and swarm.skulls.is_empty(), "missing configured gate cannot activate swarm")
	var ordinary = level.get_node("Exploration/SkullSwarm")
	check(ordinary.required_gate.is_empty() and ordinary._gate_is_open(), "unconfigured original swarm retains activation without gate")
	stop_audio(level)
	OS.delay_msec(350)
	level.queue_free()
	await frames(4)
	print("RESULT %d checks; %d failures" % [checks,failures])
	quit(1 if failures else 0)

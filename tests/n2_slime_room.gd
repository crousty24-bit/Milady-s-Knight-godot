extends SceneTree
const NAMES = ["Enemy25", "Enemy26", "Enemy27", "Enemy30", "Enemy28", "Enemy29"]
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
	seed(2108)
	level = load("res://scenes/blight_town.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	var player: SlicePlayer = level.player
	player.controls_enabled = false
	player.invulnerability = 100.0
	# Real gravity crosses the void threshold, opens the authored trapdoor,
	# then continues through the shaft into the room.
	player.position = Vector2(2704, 280)
	player.velocity = Vector2.ZERO
	await frames(100)
	check(level.get_node("Hazards/Trapdoor3").is_open, "authored trapdoor opens during descent")
	check(not player.dead and player.is_on_floor() and absf(player.position.y - 528.0) < 1.0, "real fall through lower shaft lands alive in slime room")
	check(level.camera.limit_bottom > 600, "authored lower room included in automatic camera bounds")
	player.set_physics_process(false)
	for point in [Vector2(2584, 520), Vector2(2824, 520)]:
		player.position = point
		await frames(2)
		check(not player.dead, "room side remains safe at %s" % point)
	player.position = Vector2(2704, 460)
	var stats := {}
	for name in NAMES:
		var slime: SliceSlime = level.get_node("Enemies/" + name)
		stats[name] = {"min": slime.position.x, "max": slime.position.x, "turns": 0, "early": 0, "dir": slime.direction}
	for i in 600:
		await frames(1)
		for name in NAMES:
			var slime: SliceSlime = level.get_node("Enemies/" + name)
			var stat: Dictionary = stats[name]
			stat.min = minf(stat.min, slime.position.x)
			stat.max = maxf(stat.max, slime.position.x)
			if stat.dir != slime.direction:
				stat.turns += 1
				if slime.position.x > slime.origin_x + slime.patrol_left + 3 and slime.position.x < slime.origin_x + slime.patrol_right - 3: stat.early += 1
			stat.dir = slime.direction
			if absf(slime.velocity.x) != slime.patrol_speed or not slime.is_on_floor():
				check(false, "%s stays on floor at configured speed (tick %d)" % [name, i])
				break
	for name in NAMES:
		var slime: SliceSlime = level.get_node("Enemies/" + name)
		var stat: Dictionary = stats[name]
		check(stat.max - stat.min > 30 and stat.turns >= 3 and stat.early >= 1, "%s moves and makes varying turns inside patrol" % name)
		check(stat.min >= slime.origin_x + slime.patrol_left - 2 and stat.max <= slime.origin_x + slime.patrol_right + 2, "%s remains within individual patrol" % name)
		check(slime.patrol_speed > slime.RED_PATROL_SPEED and slime.bonus_reward == 2, "%s faster with two shards" % name)
	var ordinary: SliceSlime = level.get_node("Enemies/Enemy09")
	check(ordinary.patrol_speed == 0 and ordinary.patrol_turn_interval == Vector2.ZERO and ordinary.bonus_reward == 1, "existing slimes retain default patrol and reward")
	var before: int = level.bonus
	for name in NAMES:
		var slime: SliceSlime = level.get_node("Enemies/" + name)
		slime.take_damage(100.0, Vector2.ZERO)
		slime.take_damage(100.0, Vector2.ZERO)
	check(level.bonus == before + 12, "six kills grant exactly twelve pending shards without duplicates")
	await frames(35)
	# Injected out-of-room pose exercises actual level death callback.
	player.position = Vector2(2500, 400)
	await frames(2)
	check(player.dead, "void remains fatal outside room despite invulnerability")
	stop_audio(level)
	OS.delay_msec(350)
	level.queue_free()
	await frames(4)
	print("RESULT %d checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

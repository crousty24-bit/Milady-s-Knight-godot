# Walks authored waypoints with real inputs, including combat and waiting for the ferry.
# Never changes an actor's position, health, velocity, gold, or platform phase.
extends RefCounted
var tree: SceneTree
var level: Node2D
var player: SlicePlayer
var failed := false
var tick := 0
var captured: Dictionary = {}
var starting_bank: int = 0
var enemy_rewards: int = 0
func _init(scene_tree: SceneTree) -> void: tree = scene_tree
func start() -> void:
	starting_bank = tree.root.get_node("Progression").banked_bonus
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	tree.root.add_child(level)
	tree.current_scene = level
	player = level.get_node("Player")
	for enemy in level.get_node("Enemies").get_children():
		enemy.defeated.connect(func(value: int, _at: Vector2): enemy_rewards += value)
	for i in range(10): await step(0)
func release_inputs() -> void:
	for action in ["move_left", "move_right", "jump", "attack", "interact"]: Input.action_release(action)
func step(direction: float, combat := true) -> void:
	tick += 1
	Input.action_release("move_left")
	Input.action_release("move_right")
	Input.action_release("attack")
	if combat:
		for enemy in level.get_node("Enemies").get_children():
			if enemy.dead: continue
			var distance: Vector2 = enemy.position - player.position
			if absf(distance.y) < 18 and absf(distance.x) < 36:
				if player.is_on_floor() and absf(distance.x) < 27:
					direction = signf(distance.x) if player.facing != int(signf(distance.x)) else 0.0
				if player.attack_time <= 0 and tick % 2 == 0:
					Input.action_press("attack")
				break
	if direction < 0: Input.action_press("move_left")
	if direction > 0: Input.action_press("move_right")
	await tree.physics_frame
	await tree.process_frame
	if player.dead: failed = true
	if DisplayServer.get_name() != "headless":
		for item in [["double", player.jump_flash > 0], ["wall-slide", player.motion_state == SlicePlayer.MotionState.WALL_SLIDE], ["wall-jump", player.wall_jump_lockout and absf(player.velocity.x) > 90], ["ferry", player.is_on_floor() and player.position.x > 820 and player.position.x < 952 and player.position.y < 60]]:
			if item[1] and not captured.has(item[0]):
				captured[item[0]] = true
				await RenderingServer.frame_post_draw
				tree.root.get_texture().get_image().save_png("res://work/playtest-" + item[0] + ".png")
func fail(label: String) -> void:
	failed = true
	print("DRIVER FAIL ", label, " pos=", player.position, " HP=", player.health, " gold=", level.gold)
func walk(target: float) -> void:
	if failed: return
	for i in range(1000):
		if failed or level.finished: return
		if absf(target - player.position.x) < 2:
			await step(0)
			return
		await step(signf(target - player.position.x))
	fail("walk to %.0f" % target)
func jump(target: float, double := false) -> void:
	if failed: return
	Input.action_release("jump")
	await step(0)
	Input.action_press("jump")
	var airborne := false
	for i in range(120):
		if failed: return
		if i == 20: Input.action_release("jump")
		if double and i == 21: Input.action_press("jump")
		if i == 45: Input.action_release("jump")
		await step(signf(target - player.position.x) if absf(target - player.position.x) > 2 else 0.0)
		if not player.is_on_floor(): airborne = true
		if airborne and player.is_on_floor():
			Input.action_release("jump")
			await walk(target)
			return
	Input.action_release("jump")
	fail("jump to %.0f" % target)
func climb(target: float, direction: float) -> void:
	if failed: return
	print("CLIMB ", target, " from ", player.position)
	var hold := 0
	for i in range(600):
		if failed: return
		if player.is_on_floor() and player.position.y < -63:
			Input.action_release("jump")
			await walk(target)
			return
		var was_held := Input.is_action_pressed("jump")
		if hold > 0:
			hold -= 1
		else:
			Input.action_release("jump")
		if hold == 0 and not was_held and (player.is_on_floor() or player.wall_normal == -direction):
			Input.action_press("jump")
			hold = 18
		await step(signf(target - player.position.x) if absf(player.position.x - target) > 2 else 0.0, false)
	fail("climb")
func ferry(right: bool) -> void:
	if failed: return
	var platform = level.get_node("Platforms/Ferry")
	await walk(788 if right else 988)
	var previous: float = platform.position.x
	for i in range(300):
		await step(0)
		var x: float = platform.position.x
		if (right and x < 820 and x < previous) or (not right and x > 956 and x > previous): break
		previous = x
	var future: float = platform.elapsed + 0.65
	var landing: float = platform.origin.x + platform.travel.x * (0.5 - 0.5 * cos(future * TAU / platform.period))
	print("BOARD ", right, " target ", landing)
	await jump(landing)
	if failed: return
	for i in range(300):
		await step(0)
		if (right and platform.position.x > 948) or (not right and platform.position.x < 828): break
	await jump(988 if right else 780)
func upper(right := true) -> void:
	print("UPPER ", "OUT" if right else "RETURN")
	if right:
		await walk(470)
		await jump(536)
		await walk(548)
		await jump(608, true)
		await climb(632, 1)
		await jump(696)
		await walk(714)
		# Land before approaching the guarded bank.
		for i in range(50): await step(0)
		await ferry(true)
		await walk(1056)
		await jump(1136)
		await walk(1158)
		await jump(1232)
		await walk(1282)
		await jump(1344)
		await walk(1360)
		await jump(1428)
	else:
		await walk(1418)
		await jump(1348)
		await jump(1256)
		await walk(1210)
		await jump(1136)
		await walk(1116)
		await jump(1048)
		await ferry(false)
		await walk(714)
		await climb(696, -1)
		await jump(632)
		await walk(608)
		for i in range(50): await step(0)
		await walk(536)
		for i in range(40): await step(0)
		await walk(524)
		await jump(452)
		await walk(430)
func lower(right := true) -> void:
	print("LOWER ", "OUT" if right else "RETURN")
	if right:
		await walk(852)
		await jump(928)
		await walk(1004)
		await jump(1080)
		await walk(1267)
		await jump(1308)
		await walk(1331)
		await jump(1366)
		await walk(1390)
		await jump(1430)
	else:
		await walk(1068)
		await jump(992)
		await walk(925)
		await jump(842)
		await walk(619)
		await jump(565)
		await walk(555)
		await jump(516)
		await walk(503)
		await jump(460)
		await walk(430)
func approach(right := true) -> void:
	if right:
		await walk(1508)
		await jump(1588)
		await walk(2000)
	else:
		await walk(1578)
		await jump(1500)
		await walk(1420)
func finish() -> void:
	if failed: return
	await walk(2035)
	Input.action_press("interact")
	await step(0)
	Input.action_release("interact")
	await walk(2140)
	if not level.finished: fail("exit")
func close() -> void:
	release_inputs()
	level.get_node("Music").stop()
	level.queue_free()
	await tree.process_frame

# Authored campaign traversal: real inputs only after explicit initial loadout setup.
# Never moves an actor or edits health, coins, enemies, or terrain during the route.
extends SceneTree
const N1_DRIVER = preload("res://tests/route_driver.gd")
const PATHS = ["res://scenes/blight_town.tscn", "res://scenes/black_forrest.tscn", "res://scenes/forbidden_graveyard.tscn"]
var level: Node2D
var player: SlicePlayer
var checks := 0
var failures := 0
var route_failed := false
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func release() -> void:
	for action in ["attack", "move_left", "move_right", "jump", "interact", "switch_equipment"]:
		if InputMap.has_action(action): Input.action_release(action)
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames(3)
func step(direction: float, combat := true) -> void:
	Input.action_release("move_left")
	Input.action_release("move_right")
	Input.action_release("attack")
	if combat:
		Input.action_press("attack")
		for enemy in get_nodes_in_group("enemies"):
			if not level.is_ancestor_of(enemy) or enemy.dead: continue
			var difference: Vector2 = enemy.global_position - player.global_position
			if difference.x > 0 and difference.x < 280 and player.is_on_floor():
				var origin := player.global_position + Vector2(4, -10)
				var ray := PhysicsRayQueryParameters2D.create(origin, Vector2(enemy.global_position.x, origin.y), 1 | 4)
				var hit := player.get_world_2d().direct_space_state.intersect_ray(ray)
				if hit.is_empty() or hit.collider != enemy: continue
				if difference.x < 230: direction = 1 if player.facing < 0 else 0
				break
	if direction > 0: Input.action_press("move_right")
	if direction < 0: Input.action_press("move_left")
	await frames(1)
	if player.dead: route_failed = true
func walk(target: float, combat := true) -> void:
	if route_failed: return
	for i in 3600:
		if route_failed: return
		if level.finished: return
		if absf(target - player.position.x) < 2:
			await step(0, combat)
			return
		await step(signf(target - player.position.x), combat)
	print("ROUTE stuck walk ", target, " at ", player.position, " hp=", player.health, " coins=", level.gold)
	print("ROUTE state face=", player.facing, " slot=", player.active_slot, " cooldown=", player.bow_cooldown, " controls=", player.controls_enabled)
	for enemy in get_nodes_in_group("enemies"):
		if level.is_ancestor_of(enemy): print("ROUTE enemy ", enemy.name, " at=", enemy.global_position, " hp=", enemy.health)
	route_failed = true
func jump(target: float) -> void:
	if route_failed: return
	var double_jump := true
	var second_jump_tick := 28 if absf(target - player.position.x) > 110 else 21
	Input.action_release("jump")
	await step(0, false)
	Input.action_press("jump")
	var airborne := false
	for i in 150:
		if route_failed: break
		if i == 20: Input.action_release("jump")
		if double_jump and i == second_jump_tick: Input.action_press("jump")
		if double_jump and i == second_jump_tick + 24: Input.action_release("jump")
		await step(signf(target - player.position.x) if absf(target - player.position.x) >= 2 else 0.0, false)
		if not player.is_on_floor(): airborne = true
		if airborne and player.is_on_floor():
			print("ROUTE landed target ", target, " at ", player.position)
			Input.action_release("jump")
			await walk(target)
			return
	Input.action_release("jump")
	print("ROUTE stuck jump ", target, " at ", player.position)
	route_failed = true
func cross(before: float, after: float) -> void:
	await walk(before)
	await jump(after)
func route(number: int) -> void:
	match number:
		2:
			await cross(424, 504)
			await cross(552, 656)
			await cross(824, 904)
			await cross(936, 984)
			await walk(1468)
			await jump(1540)
			await cross(1540, 1592)
			await cross(1608, 1688)
			await cross(1832, 1952)
			await cross(2120, 2200)
			await cross(2216, 2264)
		3:
			await cross(392, 472)
			await cross(488, 608)
			await cross(744, 824)
			await cross(840, 888)
			await walk(1244)
			await jump(1320)
			await cross(1352, 1400)
			await cross(1540, 1628)
			await cross(1640, 1688)
			await cross(1992, 2128)
			await cross(2272, 2420)
			await cross(2440, 2488)
			await cross(2668, 2756)
			await cross(2744, 2824)
		4:
			await cross(376, 440)
			await cross(872, 992)
			await cross(1592, 1672)
			await walk(1708)
			await jump(1788)
			await cross(1800, 1848)
			await cross(1848, 1928)
			await cross(2010, 2120)
			await cross(2244, 2328)
			await cross(2408, 2544)
			await walk(2640)
			await tap("interact")
			check(level.get_node("Exploration/MechanismDoor").opened, "N4 keyboard button opens required door on route")
			await cross(2984, 3064)
			await cross(3112, 3160)
			await cross(3180, 3268)
	await walk(level.gate.position.x - 30)
	check(not route_failed and not player.dead and level.gold >= level.gate.COST, "N%d route reaches sealed gate with enough collected coins; HP %.1f coins %d" % [number, player.health, level.gold])
	if route_failed: return
	var before: int = level.gold
	await tap("interact")
	check(level.gate.opened and before - level.gold == level.gate.COST, "N%d keyboard pays exact gate price" % number)
	await walk(level.gate.position.x + 80, false)
	check(level.finished and level.reward_settled, "N%d physical exit settles progression" % number)
func drain() -> void:
	release()
	paused = true # Actors cannot start a fresh voice after the shutdown sweep.
	for kind in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for sound in root.find_children("*", kind, true, false): sound.stop()
	OS.delay_msec(350) # Let the native mixer release voices during accelerated physics.
	await create_timer(0.3, true).timeout
	if is_instance_valid(current_scene): current_scene.queue_free()
	paused = false
	await frames(3)
func run() -> void:
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	var n1 = N1_DRIVER.new(self)
	await n1.start("res://scenes/eidolon_vale.tscn")
	await n1.walk(n1.level.tutorial_chest.position.x)
	Input.action_press("interact")
	await n1.step(0)
	Input.action_release("interact")
	await n1.step(0)
	check(n1.level.player.has_longbow, "N1 walking and E acquire tutorial Longbow0")
	await n1.lower()
	await n1.approach()
	await n1.finish()
	n1.release_inputs()
	check(not n1.failed and n1.level.finished, "N1 real lower route reaches campaign exit")
	await tap("interact")
	await frames(8)
	check(current_scene.scene_file_path == PATHS[0], "N1 keyboard advances to real N2")
	for number in [2, 3, 4]:
		release()
		paused = false
		level = current_scene
		if not is_instance_valid(level) or level.scene_file_path != PATHS[number - 2]:
			check(false, "campaign transition reaches expected N%d" % number)
			break
		player = level.player
		await frames(5)
		await tap("switch_equipment")
		check(player.active_slot == 1, "N%d keyboard selects carried Longbow0" % number)
		route_failed = false
		await route(number)
		print("ROUTE N", number, " hp=", player.health, " pos=", player.position, " coins=", level.gold, " fail=", route_failed)
		if route_failed: break
		if number < 4:
			await tap("interact")
			await frames(8)
			check(current_scene.scene_file_path == PATHS[number - 1], "N%d keyboard exit advances to real N%d" % [number, number + 1])
	check(not route_failed and level.scene_file_path == PATHS[2] and level.finished, "full N1-N4 route completes without position or health edits")
	await drain()
	print("RESULT %d checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

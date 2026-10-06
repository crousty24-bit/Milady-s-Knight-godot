# Authored campaign traversal: real inputs and the actual N1 tutorial Longbow.
# Default: N2–4 lower forks. Add -- upper for upper forks plus the N4 paid HP room.
# Never moves an actor or edits health, coins, enemies, or terrain during the route.
extends SceneTree
const N1_DRIVER = preload("res://tests/route_driver.gd")
const PATHS = ["res://scenes/blight_town.tscn", "res://scenes/black_forrest.tscn", "res://scenes/forbidden_graveyard.tscn"]
const TRAP_BOLT = preload("res://scripts/trap_projectile.gd")
const ENEMY_ATTACK = preload("res://scripts/run019_enemy_attack.gd")
var level: Node2D
var player: SlicePlayer
var checks := 0
var failures := 0
var route_failed := false
var dodge_ticks := 0
var dodging := false
var upper_route := false
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
	if dodge_ticks > 0:
		dodge_ticks -= 1
		if dodge_ticks == 0: Input.action_release("jump")
	elif dodging and player.is_on_floor():
		dodging = false
	Input.action_release("move_left")
	Input.action_release("move_right")
	Input.action_release("attack")
	if combat:
		var closest: Node2D
		var closest_gap := 280.0
		for enemy in get_nodes_in_group("enemies"):
			if not level.is_ancestor_of(enemy) or enemy.dead: continue
			var difference: Vector2 = enemy.global_position - player.global_position
			if absf(difference.y) > 24.0 or absf(difference.x) >= closest_gap: continue
			var origin := player.global_position + Vector2(4 * signf(difference.x), -10)
			var ray := PhysicsRayQueryParameters2D.create(origin, Vector2(enemy.global_position.x, origin.y), 1 | 4)
			var hit := player.get_world_2d().direct_space_state.intersect_ray(ray)
			if hit.is_empty() or hit.collider != enemy: continue
			closest = enemy
			closest_gap = absf(difference.x)
		if closest != null and player.is_on_floor():
			var side := signf(closest.global_position.x - player.global_position.x)
			var reach: float = WeaponCatalog.stats(player.equipment.ranged).reach - 16.0
			if closest_gap <= reach:
				# Aim and fire when ready; keep room for the enemy's chase
				# throughout the equipped ranged weapon's recovery.
				if player.bow_cooldown <= 0.02:
					direction = side if player.facing != int(side) else 0.0
					Input.action_press("attack")
				elif closest_gap < reach:
					var edge := player.global_position + Vector2(-side * 18.0, 0)
					var ground := PhysicsRayQueryParameters2D.create(edge + Vector2(0, -8), edge + Vector2(0, 16), 1)
					var footing := player.get_world_2d().direct_space_state.intersect_ray(ground)
					direction = -side if not footing.is_empty() and footing.collider == level.get_node("Terrain") else 0.0
					for hazard in level.get_node("Hazards").get_children():
						if absf(hazard.global_position.x - edge.x) < 34 and absf(hazard.global_position.y - edge.y) < 24:
							direction = 0.0
				else:
					direction = 0.0
			# Beyond bow reach, continue the authored route; chasing a target
			# behind across a gap would abandon the planned platform landing.
		if closest is SliceSlime and closest_gap < 38.0 and player.is_on_floor() and not dodging:
			# Contact guards can reach the player before Longbow0 recovers.
			# Evade through real jump input, as for a telegraphed melee attack.
			Input.action_press("jump")
			dodge_ticks = 18
			dodging = true
		if closest != null and closest.get_script() == preload("res://scripts/run019_enemy.gd") and closest.pending_attack == &"melee" and closest.windup_time > 0.0 and player.is_on_floor() and not dodging:
			Input.action_press("jump")
			dodge_ticks = 18
			dodging = true
		if player.is_on_floor() and not dodging:
			var projectiles: Array[Node] = level.get_node("Hazards").get_children()
			for enemy in get_nodes_in_group("enemies"):
				if level.is_ancestor_of(enemy) and enemy.get_script() == preload("res://scripts/run019_enemy.gd"):
					for projectile in enemy.active_attacks:
						if is_instance_valid(projectile): projectiles.append(projectile)
			for projectile in projectiles:
				var motion := Vector2.ZERO
				if projectile.get_script() == TRAP_BOLT:
					motion = projectile.direction * projectile.speed
				elif projectile.get_script() == ENEMY_ATTACK and projectile.mode == 0:
					motion = projectile.motion
				else: continue
				var offset: Vector2 = player.global_position + Vector2(0, -12) - projectile.global_position
				if absf(offset.y) < 18 and absf(offset.x) < 70 and offset.dot(motion) > 0:
					Input.action_press("jump")
					dodge_ticks = 8
					dodging = true
					break
		# Keep the chosen movement while evading: stopping throughout a jump
		# lets a chasing melee enemy reach the landing point.

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
func jump(target: float, clear_rise := 0.0) -> void:
	if route_failed: return
	for _tick in 120:
		if player.hit_stun_time <= 0.0 and player.is_on_floor(): break
		await step(0, false)
	# Near a tall solid face, rise before moving instead of demanding a wall jump.
	var launch_y := player.position.y
	var cleared := clear_rise == 0.0
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
		cleared = cleared or player.position.y < launch_y - clear_rise - 1
		await step(signf(target - player.position.x) if cleared and absf(target - player.position.x) >= 2 else 0.0, false)
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
func collect_coin(coin_name: String) -> void:
	# A projectile dodge can carry the player above a floor coin at its X.
	# Return on foot and keep fighting until the actual pickup occurs.
	var coin := level.get_node_or_null("Coins/" + coin_name)
	for _tick in 1200:
		if route_failed or not is_instance_valid(coin) or coin.picked_up: return
		var offset: float = coin.global_position.x - player.global_position.x
		await step(signf(offset) if absf(offset) >= 2.0 else 0.0)
	print("ROUTE could not physically collect ", coin_name, " at=", player.position)
	route_failed = true
func n2_authored_tunnel() -> void:
	# The human-authored pillar closes both old approaches at X3088.
	# Climb its outer left face, traverse the real gap, then drop through
	# the sixteen-pixel shaft at X3280–3296 back to the square.
	dodge_ticks = 0
	dodging = false
	await walk(3050, false)
	if route_failed: return
	print("ROUTE pillar launch at=", player.position, " floor=", player.is_on_floor(), " velocity=", player.velocity)
	Input.action_release("jump")
	# Rise outside the pillar's overhanging foot before approaching its face.
	Input.action_press("jump")
	for _tick in 16:
		await step(0, false)
	Input.action_release("jump")
	await step(0, false)
	var jump_hold := 0
	var entered := false
	for _tick in 900:
		if player.position.x > 3104 and player.position.y < -110:
			entered = true
			break
		if jump_hold == 0 and (player.is_on_floor() or player.wall_normal < 0.0):
			Input.action_press("jump")
			jump_hold = 6
		await step(1, false)
		if route_failed: break
		if jump_hold > 0:
			jump_hold -= 1
			if jump_hold == 0: Input.action_release("jump")
	Input.action_release("jump")
	print("ROUTE authored tunnel entered=", entered, " at=", player.position)
	if not entered:
		route_failed = true
		return
	# Follow the right face down the shaft, then rebound to the left as
	# the body clears the beam ends, avoiding the fixed spikes below.
	await walk(3292, false)
	for _tick in 360:
		if route_failed: return
		if player.position.y > -46: break
		await step(1, false)
	Input.action_press("jump")
	await step(-1, false)
	print("ROUTE shaft rebound at=", player.position, " velocity=", player.velocity, " grace=", player.wall_coyote)
	for _tick in 18: await step(-1, false)
	Input.action_release("jump")
	await walk(3216)
	for _tick in 180:
		if route_failed: return
		if player.is_on_floor() and player.position.y > 100: break
		await step(signf(3216 - player.position.x) if absf(3216 - player.position.x) >= 2 else 0, false)
	await collect_coin("Coin22")
	print("ROUTE authored tunnel exit at=", player.position)

func route(number: int) -> void:
	print("ROUTE variant ", "upper" if upper_route else "lower", " N", number)
	match number:
		2:
			await cross(156, 200)
			await walk(300)
			await jump(352)
			# The human-authored overhang ends at X400. Launch after the
			# body clears its ceiling, before the spikes begin at X416.
			await cross(406, 480)
			await walk(592)
			await cross(742, 810) # Human-added retractable spikes at X784.
			await cross(826, 908)
			await collect_coin("Coin07") # Return on foot after any contact dodge.
			await cross(982, 1032)
			if upper_route:
				await jump(1112)
				# Land on the rampart's unguarded left end and clear its Purple
				# before advancing, rather than landing directly on its patrol.
				await jump(1178)
				for _tick in 900:
					if route_failed: return
					if level.get_node("Enemies/Enemy15").dead: break
					await step(0)
				await walk(1216)
				await cross(1250, 1344)
				await jump(1344)
				await jump(1428)
				for _tick in 900:
					if route_failed: return
					if level.get_node("Enemies/Enemy03").dead: break
					await step(0)
				await walk(1472)
				await cross(1504, 1584)
			else:
				await walk(1080)
				# Descend at the vault entrance before approaching its Red guards.
				await walk(1112, false)
				for _tick in 120:
					if route_failed: return
					if player.is_on_floor(): break
					await step(0, false)
				await walk(1232)
				await cross(1294, 1392)
				await cross(1404, 1488)
				await jump(1528)
				await jump(1576)
				await jump(1616)
			await walk(1664)
			await cross(1684, 1774)
			await jump(1816)
			# Fight from the well's actual support before landing on guarded crates.
			await walk(1830)
			await jump(1928)
			await jump(2048)
			await walk(2240)
			await walk(2288)
			# Leave the market roof near its edge, rather than landing among
			# both street guards while the scripted jump suppresses combat.
			var street_guard := level.get_node("Enemies/Enemy07")
			for _tick in 900:
				if route_failed: return
				if street_guard.dead or (street_guard.position.x > 2375 and street_guard.velocity.x > 0 and player.bow_cooldown <= 0.02): break
				await step(0, false)
			await walk(2312, false)
			for _tick in 120:
				if route_failed: return
				if player.is_on_floor(): break
				await step(0, false)
			await walk(2408)
			await cross(2428, 2472)
			if not upper_route: print("ROUTE N2 lower vault uses upper causeway to bypass closed authored lower lane")
			await jump(2552)
			await jump(2672)
			await cross(2736, 2820)
			await cross(2858, 2950)
			await walk(2976)
			await n2_authored_tunnel()
			await walk(3216)
			# Stay on the lower approach while fighting the pursuing elite;
			# climbing its optional perch would suppress combat during ascent.
			await walk(3600)
		3:
			await cross(204, 256)
			await cross(430, 514)
			await jump(592)
			await walk(640)
			await cross(650, 734)
			await cross(812, 896)
			await walk(1088)
			await jump(1168)
			await cross(1180, 1224)
			if upper_route:
				await jump(1312)
				await jump(1440)
				await jump(1552)
				await jump(1704)
				await cross(1740, 1840)
				await jump(1960)
			else:
				await walk(1344)
				await cross(1446, 1536)
				await jump(1648)
				await jump(1668)
				await walk(1712)
				await walk(1792)
				await walk(1984)
			await walk(2096)
			await walk(2196)
			await jump(2288)
			await jump(2368)
			await jump(2448)
			await jump(2544)
			await walk(2600)
			await jump(2744)
			if upper_route:
				await jump(2880)
				await jump(2992)
				await jump(3112)
				await cross(3150, 3248)
				await jump(3376)
				await jump(3504)
				await jump(3616)
				await walk(3640)
				await jump(3792)
			else:
				await walk(2872)
				await cross(2906, 3008)
				await cross(3050, 3138)
				await cross(3290, 3374)
				await walk(3536)
				await cross(3642, 3688)
				await jump(3736)
				await jump(3792)
			await walk(3792)
			await cross(3836, 3880)
			await walk(3960)
			await jump(4040)
			await walk(4144)
		4:
			await cross(188, 224)
			await walk(304)
			await cross(332, 376)
			await jump(472, 48)
			await walk(376)
			await walk(608)
			await walk(704)
			await cross(778, 862)
			await walk(928)
			await collect_coin("Coin09")
			await cross(956, 1000)
			if upper_route:
				await jump(1120)
				await jump(1248)
				await jump(1420)
				await walk(1522)
				var before_door: int = level.gold
				await tap("interact")
				check(level.get_node("Exploration/CoinDoor").opened and before_door - level.gold == 4, "N4 upper route pays exact optional 4-coin door")
				await walk(1640)
				check(root.get_node("Progression").has_hp_bonus("n4_hp_01"), "N4 upper route physically acquires permanent HP bonus")
				await walk(1518)
				await jump(1600, 64)
				await walk(1676)
				await jump(1776)
				await jump(1896)
				await walk(1918)
				await jump(2048)
			else:
				await walk(1064)
				await walk(1376)
				await cross(1658, 1744)
				await walk(1824)
				await walk(1904)
				await jump(1976)
				await jump(2048)
			await walk(2096)
			await walk(2144)
			await jump(2176)
			await walk(2240)
			await jump(2336)
			await walk(2416)
			await walk(2480)
			await jump(2544)
			await walk(2688)
			if upper_route:
				await cross(2764, 2856)
				await cross(2924, 2976)
				await cross(3082, 3170)
				await walk(3264)
				await cross(3290, 3360)
				await jump(3416)
				await cross(3424, 3560)
			else:
				await walk(2808)
				await walk(2896)
				await cross(3018, 3104)
				await cross(3194, 3278)
				await walk(3440)
				await walk(3496)
				await jump(3520, 48)
				await jump(3576, 48)
			await walk(3600)
			await walk(3744)
			await cross(3756, 3808)
			await walk(3856)
			await jump(3808)
			await jump(3920)
			await jump(4048)
			# Combat can finish the approach in a dodge above the button.
			# Reach its actual X and wait for a physical overlap before E.
			var button := level.get_node("Exploration/MechanismButton")
			await walk(button.position.x, false)
			for _tick in 120:
				if button.can_use(player): break
				await step(0, false)
			await tap("interact")
			check(level.get_node("Exploration/MechanismDoor").opened, "N4 keyboard button opens required door on route")
			await walk(4072)
			# Leave the button platform before returning to its floor coin.
			await walk(4108, false)
			for _tick in 120:
				if player.is_on_floor() and player.position.y > 100: break
				await step(0, false)
			await walk(4096)
			await collect_coin("Coin36")
			await cross(4186, 4272)
			await cross(4296, 4360)
			await walk(4272)
			await walk(4624)
	await walk(level.gate.position.x - 30)
	if level.gold < level.gate.COST:
		for coin in level.get_node("Coins").get_children():
			if not coin.picked_up: print("ROUTE uncollected ", coin.name, " at=", coin.position)
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
	upper_route = "upper" in OS.get_cmdline_user_args()
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
		player.health_changed.connect(func(value: float, _maximum: float) -> void:
			print("ROUTE health ", value, " at=", player.position, " slot=", player.active_slot)
			for enemy in get_nodes_in_group("enemies"):
				if level.is_ancestor_of(enemy) and not enemy.dead and enemy.global_position.distance_to(player.global_position) < 200:
					print("ROUTE nearby ", enemy.name, " at=", enemy.position, " hp=", enemy.health))
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

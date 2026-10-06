extends SceneTree
# Integration fixtures use the real authored scenes. Relocation/removed hazards are
# explicit isolation for transactions; traversal is covered by the separate pilot.
const LEVELS = ["res://scenes/blight_town.tscn", "res://scenes/black_forrest.tscn", "res://scenes/forbidden_graveyard.tscn"]
const SAVE = "user://run020-campaign.json"
var level: Node2D
var progress: Node
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames(4)
func spawn(path: String, isolate: bool = true) -> void:
	paused = false
	if is_instance_valid(level):
		for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for emitter in level.find_children("*", audio_type, true, false): emitter.stop()
		await create_timer(0.3, true).timeout
		level.queue_free()
		await frames(4)
	level = load(path).instantiate()
	root.add_child(level)
	current_scene = level
	await frames(12)
	if isolate: await isolate_transactions()
func isolate_transactions() -> void:
	# Keep real terrain/items/mechanisms, remove opponents/traps only for interaction
	# tests. Native populations and safe spawn are checked before this helper runs.
	for group in ["Enemies", "Hazards"]:
		for node in level.get_node(group).get_children(): node.queue_free()
	await frames(4)
	level.player.controls_enabled = false
func place(at: Vector2) -> void:
	level.player.position = at
	level.player.velocity = Vector2.ZERO
	await frames(5)
func collect_coins() -> void:
	# Relocate each real scene coin onto an empty safe floor fixture, then move the
	# real player through its body area. No signal emission or gold assignment.
	var coins := level.get_node("Coins").get_children()
	for coin in coins:
		if not is_instance_valid(coin) or coin.picked_up: continue
		await place(Vector2(48, 144))
		coin.position = Vector2(96, 132)
		await frames(2)
		await place(Vector2(96, 144))
		check(not is_instance_valid(coin) or coin.picked_up, "scene coin collected through physical body contact")
func delete_save(path: String) -> void:
	for suffix in ["", ".tmp", ".bak", ".bak.1"]: DirAccess.remove_absolute(path + suffix)
func finish(label: String) -> void:
	paused = false
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for emitter in root.find_children("*", audio_type, true, false): emitter.stop()
	if is_instance_valid(level): level.queue_free()
	await frames(5)
	await create_timer(0.35).timeout
	print("RESULT %d %s checks; %d failures" % [checks, label, failures])
	quit(1 if failures else 0)
func reveal_secret(occlusion: bool = false) -> void:
	var secret = level.get_node("Exploration/SecretWall")
	var blocker: StaticBody2D
	# The two attacks come from actual weapon input, including bow selection.
	level.player.configure_loadout({"melee":"Sword0", "ranged":"Longbow0"})
	level.player.controls_enabled = true
	await place(secret.position + Vector2(-24, 0))
	level.player.facing = 1
	if occlusion:
		blocker = StaticBody2D.new()
		blocker.collision_layer = 1
		blocker.collision_mask = 0
		var shape := CollisionShape2D.new()
		var rectangle := RectangleShape2D.new()
		rectangle.size = Vector2(8, 32)
		shape.shape = rectangle
		blocker.add_child(shape)
		level.add_child(blocker)
		blocker.position = secret.position + Vector2(-12, -16)
		await frames(3)
		await tap("attack")
		await frames(25)
		check(not secret.opened, "actual Sword attack is occluded by solid fixture terrain")
		await tap("switch_equipment")
		await tap("attack")
		await frames(25)
		check(not secret.opened, "actual Longbow shot is occluded by solid fixture terrain")
		blocker.queue_free()
		await frames(4)
		level.player.bow_cooldown = 0.0 # Isolate cooldown from prior blocked shot.
		await tap("attack")
	else:
		level.player.attack_cooldown = 0.0
		await tap("attack")
	await frames(30)
	check(secret.opened and progress.permanent_flags.get("secret:n4_secret_01", false), "actual weapon reveals authored secret and commits durable flag")
	level.player.controls_enabled = false
func run() -> void:
	progress = root.get_node("Progression")
	progress.storage_path = SAVE
	progress.persistence_enabled = true
	check(progress.new_game() == OK, "isolated campaign save initializes")
	var populations = [["slime", "red_slime", "bloated_slime"], ["slime", "red_slime", "skeleton_warrior", "skeleton_archer"], ["red_slime", "skeleton_warrior", "skeleton_archer", "blight_sorcerer", "chud_blob"]]
	for index in LEVELS.size():
		await spawn(LEVELS[index], false)
		var cost: int = [18,25,32][index]
		check(level.world_level == index + 2 and level.gate.COST == cost, "authored level number and exit price%d" % cost)
		check(level.next_level_scene == (LEVELS[index + 1] if index < 2 else ""), "authored campaign successor")
		# Human-authored levels may add mobs; the original population is a
		# minimum coverage baseline, not a cap that would forbid these edits.
		print("OBSERVATION native N", index + 2, " enemies=", level.get_node("Enemies").get_child_count())
		check(level.get_node("Coins").get_child_count() == [24,32,40][index] and level.get_node("Enemies").get_child_count() >= [10,13,14][index], "native minimum population and coin budget")
		for family in populations[index]:
			var found := false
			for enemy in level.get_node("Enemies").get_children():
				if enemy.scene_file_path == "res://scenes/%s.tscn" % family: found = true
			check(found, "native family " + family)
		check(level.get_node("Hazards").get_child_count() >= [10,11,10][index], "native minimum authored trap population")
		for family in (["spikes", "retractable_spikes", "trapdoor"] if index == 0 else ["spikes", "retractable_spikes", "trapdoor", "poison_plant", "turret"]):
			var found := false
			for hazard in level.get_node("Hazards").get_children():
				if hazard.scene_file_path == "res://scenes/%s.tscn" % family: found = true
			check(found, "native trap family " + family)
		if index < 2:
			var has_green := false
			var has_purple := false
			for enemy in level.get_node("Enemies").get_children():
				if enemy.scene_file_path == "res://scenes/slime.tscn":
					has_green = has_green or enemy.variant == 0
					has_purple = has_purple or enemy.variant == 1
			check(has_green and has_purple, "native Green and Purple Slime variants")
		check(level.player.is_on_floor() and not level.player.dead and level.player.health_units == 30 and level.modal.is_empty(), "native first twelve physical frames preserve safe spawn")
		check(not level.n1_intro_enabled and not level.tutorial_rewards_enabled and not is_instance_valid(level.tutorial_chest) and not is_instance_valid(level.dialogue_panel), "N2+ creates no N1 tutorial or reward")
		check(level.camera.limit_right == int(level.camera_bounds.end.x) and level.camera.limit_left == 0 and level.camera.limit_top == -224 and level.camera.limit_bottom == 304, "camera uses authored world bounds")
		check(level.hud.get_node("Gold").text.contains("/%d" % cost), "HUD displays actual exit price")
		if index == 2:
			check(level.get_node("Items/RareChest").kind == "rare", "authored secret chest uses rare economy and reward pool")
		await isolate_transactions()
		await collect_coins()
		check(level.gold == [24,32,40][index], "real coin pickups fund full authored route")
		if index == 2:
			await place(level.get_node("Exploration/CoinDoor").position + Vector2(-24, 0))
			await tap("interact")
			check(level.get_node("Exploration/CoinDoor").opened and level.gold == 36, "E pays optional four coin branch once")
			await tap("interact")
			check(level.gold == 36, "opened optional door cannot charge twice")
			await place(level.get_node("Exploration/MechanismButton").position)
			await tap("interact")
			check(level.get_node("Exploration/MechanismButton").active and level.get_node("Exploration/MechanismDoor").opened and level.gold == 36, "E mechanism opens required passage without spending coins")
		await place(level.gate.position + Vector2(-24,0))
		await tap("interact")
		check(level.gate.opened and level.gold == ([24,32,40][index] - cost - (4 if index == 2 else 0)), "physical E opens exit within optional spending budget")
	await spawn(LEVELS[2])
	await reveal_secret(true)
	level.player.health_units = 10
	await place(level.get_node("Items/HpBonus").position + Vector2(0, 12))
	check(progress.has_hp_bonus("n4_hp_01") and level.player.max_health_units == 40 and level.player.health_units == 20, "real authored HP pickup grants current and max health durably")
	# Direct bank funding and deterministic offer are setup fixtures; all payments,
	# acceptance/refusal and equipment commits below pass through keyboard menus.
	check(progress.settle_level(100, LEVELS[2]) == OK, "bank transaction setup for authored chest tests")
	var common = level.get_node("Items/CommonChest")
	common.offer = {"item":"Longsword1", "upgrade":""}
	await place(common.position)
	await tap("interact")
	check(level.modal == "reward" and common.paid and progress.banked_shards == 90, "E opens authored common chest and debits bank10")
	await tap("pause")
	check(level.modal.is_empty() and common.consumed and progress.banked_shards == 90 and progress.equipment.melee == "Sword0", "Escape refuses paid common without refund or equipment change")
	var rare = level.get_node("Items/RareChest")
	rare.offer = {"item":"Longsword1", "upgrade":""}
	await place(rare.position)
	await tap("interact")
	check(level.modal == "reward" and rare.paid and progress.banked_shards == 60, "E rare opens reward and debits30 (modal=%s bank=%d)" % [level.modal, progress.banked_shards])
	await tap("interact")
	check(progress.banked_shards == 60 and progress.equipment.melee == "Longsword1" and level.player.equipment.melee == "Longsword1", "real rare acceptance debits30 and saves equipment (modal=%s bank=%d saved=%s runtime=%s)" % [level.modal, progress.banked_shards, progress.equipment.melee, level.player.equipment.melee])
	check(level.player.health_units == 20, "equipment acceptance preserves existing injury")
	await place(level.get_node("Items/MajorPotion").position + Vector2(0, 12))
	check(level.get_node("Items/MajorPotion").used and level.player.health_units == 30, "physical authored major potion restores exactly one HP")
	# Swarm direct damage is an isolated reward transaction criterion. Spawn,
	# despawn and reentry are caused by physical player position in the real zone.
	var swarm = level.get_node("Exploration/SkullSwarm")
	await place(swarm.position + Vector2(0, 48))
	check(swarm.skulls.size() == 4, "authored zone physically spawns four skull slots")
	for skull in swarm.skulls: skull.take_damage(10, Vector2.ZERO)
	await frames(5)
	var earned: int = level.bonus
	check(earned == 4, "isolated four skull kills credit bounded reward four")
	await place(swarm.position + Vector2(-swarm.zone_size.x / 2 - 64, 96))
	await place(swarm.position + Vector2(0, 48))
	check(swarm.skulls.is_empty(), "cleared zone stays cleared on reentry in the same attempt")
	await frames(5)
	check(level.bonus == earned, "reentry cannot farm additional shard rewards")
	level.player.take_damage(0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)
	check(level.player.dead and level.modal == "death" and level.bonus == 0, "fatal attempt discards pending shards and enters death presentation")
	await create_timer(3.7, true).timeout
	await frames(8)
	level = current_scene
	check(level.scene_file_path == LEVELS[2] and not level.player.dead and level.player.health_units == 40, "real timed death reloads current authored scene healed")
	check(level.gold == 0 and level.bonus == 0 and not level.gate.opened and not level.get_node("Exploration/CoinDoor").opened and not level.get_node("Exploration/MechanismButton").active, "death reload clears coins doors mechanisms and pending gains")
	check(level.get_node("Exploration/SecretWall").opened and level.get_node("Items/HpBonus").used and level.player.equipment.melee == "Longsword1" and progress.banked_shards == 60, "death preserves durable secret HP equipment and bank")
	check(not level.get_node("Exploration/SkullSwarm").rewarded_slots.has(true) and not level.get_node("Items/CommonChest").consumed and not level.get_node("Items/RareChest").consumed, "fresh attempt restores skull eligibility and authored chests")
	delete_save(SAVE)
	await finish("run020 campaign")

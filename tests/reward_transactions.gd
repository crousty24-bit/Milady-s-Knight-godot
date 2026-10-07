extends SceneTree
const Store = preload("res://scripts/progression.gd")
const FIXTURE = preload("res://tests/fixtures/economy_level.tscn")
var checks := 0
var failures := 0
var level: Node2D
var progress: Node
const PATH = "user://run018-transactions.json"
func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames()
# RUN-021: a paid chest first shows "Treasure Found!"; E presses Open and Space skips to the cards.
func open_cards() -> void:
	await tap("interact")
	await tap("jump")
	for i in 120:
		if level.pause_menu.opened: return
		await frames(1)
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func spawn() -> void:
	paused = false
	if is_instance_valid(level):
		level.queue_free()
		await frames()
	level = FIXTURE.instantiate()
	root.add_child(level)
	current_scene = level
	await frames(6)
func near_chest(rare: bool = false) -> Area2D:
	var chest: Area2D = level.get_node("RareChest" if rare else "CommonChest")
	level.player.position = chest.position
	level.player.velocity = Vector2.ZERO
	await frames(4)
	return chest
func reopen() -> Node:
	var store := Store.new()
	store.storage_path = PATH
	store.persistence_enabled = true
	store.load_progress()
	return store
func capture(label: String) -> void:
	if DisplayServer.get_name() == "headless": return
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://work/run018")
	root.get_texture().get_image().save_png("res://work/run018/" + label + ".png")
	await process_frame # Inject following input before node processing, never after frame_post_draw.
func run() -> void:
	progress = root.get_node("Progression")
	progress.storage_path = PATH
	progress.persistence_enabled = true
	progress.new_game()
	progress.banked_shards = 50
	progress.settle_level(0, progress.DEFAULT_LEVEL)
	await spawn()
	level.bonus = 3
	var chest: Area2D = await near_chest()
	chest.offer = {"item": "BrutalAxe2", "upgrade": "Sword1"}
	await tap("interact")
	check(paused and level.modal == "reward" and chest.paid and chest.consumed, "physical E pays and opens an exclusive reward modal")
	check(level.bonus == 0 and progress.banked_shards == 48 and level.chest_economy.counts.common == 1 and level.chest_economy.counts.rare == 0, "opening spends current gains first and increments only common counter")
	var disk := reopen()
	check(disk.banked_shards == 48 and disk.equipment.melee == "Sword0", "opening persists debit before acquisition")
	disk.free()
	check(not level.try_offering() and not level.open_reward_chest(level.get_node("RareChest")), "reward blocks gate and competing chest")
	await open_cards()
	await capture("paid-choice")
	await tap("move_right")
	check(level.pause_menu.selection == 1, "Right chooses the second horizontal upgrade slot")
	await tap("move_left")
	check(level.pause_menu.selection == 0, "Left returns to item slot")
	await tap("pause")
	check(not paused and level.modal.is_empty() and progress.equipment.melee == "Sword0" and progress.banked_shards == 48, "Escape refuses without refund or opening pause")
	await tap("interact")
	check(not paused and level.chest_economy.counts.common == 1, "repeated E cannot pay or grant twice")
	await spawn()
	check(level.chest_economy.price("common", 2) == 5 and not level.get_node("CommonChest").consumed, "reset restores common chest and initial price")
	chest = await near_chest()
	chest.offer = {"item": "ThrowingKnives2", "upgrade": "Sword1"}
	await tap("interact")
	await open_cards()
	var paid_bank: int = progress.banked_shards
	Input.action_press("interact")
	await frames(8)
	check(progress.equipment.ranged == "ThrowingKnives2" and progress.banked_shards == paid_bank and level.resume_pending, "held E accepts once and blocks gameplay until released")
	Input.action_release("interact")
	await frames()
	check(level.player.equipment.ranged == "ThrowingKnives2" and level.hud.get_node("Equipment/Ranged").text == "  Throwing Knives 2", "confirmed reward updates runtime and exact HUD")
	disk = reopen()
	check(disk.equipment.ranged == "ThrowingKnives2", "acquisition survives disk reload")
	disk.free()
	await spawn()
	chest = await near_chest(true)
	chest.offer = {"item": "DarkScythe2", "upgrade": "Sword1"}
	await tap("interact")
	await open_cards()
	await tap("move_right")
	await tap("interact")
	check(progress.equipment.melee == "Sword1" and level.player.equipment.melee == "Sword1" and level.chest_economy.counts.rare == 1 and level.chest_economy.counts.common == 0, "rare upgrade grants only +1 to captured active item")
	await spawn()
	progress.banked_shards = 0
	level.bonus = 4
	chest = await near_chest()
	var rng_state: int = level.chest_economy.rng.state
	await tap("interact")
	check(not chest.paid and not paused and chest.offer.is_empty() and level.chest_economy.rng.state == rng_state and level.bonus == 4, "insufficient funds consume neither payment nor RNG")
	level.bonus = 8
	progress.banked_shards = 50
	progress.settle_level(0, progress.DEFAULT_LEVEL)
	progress.storage_path = "user://run018-missing-dir/progress.json"
	chest.offer = {"item": "Warhammer2", "upgrade": "Sword2"}
	await tap("interact")
	# A current-only debit succeeds without durable bank mutation; acquisition still requires disk.
	check(chest.paid and paused and level.bonus == 3 and progress.banked_shards == 50, "current-only opening has no bank write")
	await open_cards()
	await tap("interact")
	check(paused and chest.save_failed and progress.equipment.melee == "Sword1" and level.chest_economy.counts.common == 1 and level.bonus == 3, "acquisition write failure retains offer and never repeats payment")
	await tap("move_right")
	await tap("interact")
	check(paused and level.pause_menu.selection == 1 and chest.offer.upgrade == "Sword2", "failed upgrade keeps selected slot and captured offer")
	progress.storage_path = PATH
	await tap("interact")
	check(not paused and progress.equipment.melee == "Sword2" and level.bonus == 3 and progress.banked_shards == 50, "retry grants the same offer after storage repair")
	await spawn()
	chest = await near_chest()
	level.bonus = 1
	progress.storage_path = "user://run018-missing-dir/progress.json"
	chest.offer = {"item": "Halberds3", "upgrade": ""}
	await tap("interact")
	check(not paused and not chest.paid and not chest.consumed and chest.save_failed and level.bonus == 1 and progress.banked_shards == 50 and level.chest_economy.counts.common == 0, "bank write failure rolls back all attempt state")
	check(chest.offer.item == "Halberds3", "failed opening preserves its offer for retry")
	progress.storage_path = PATH
	await tap("interact")
	await open_cards()
	await tap("interact")
	check(progress.equipment.melee == "Halberds3" and progress.banked_shards == 46 and level.bonus == 0, "opening retry pays once and accepts original offer")
	await spawn()
	var potion: Area2D = level.get_node("MajorPotion")
	level.player.position = Vector2(320, 144)
	level.player.velocity = Vector2.ZERO
	await frames(6)
	check(not potion.used and level.player.health == 3, "major potion remains at full health")
	level.player.health_units = 13
	await frames(4)
	check(potion.used and level.player.health == 2.3, "physical major potion heals exactly one HP")
	await frames(4)
	check(level.player.health == 2.3, "major potion heals only once")
	await capture("major-heal")
	await spawn()
	potion = level.get_node("MajorPotion")
	level.player.health_units = 28
	level.player.position = Vector2(320, 144)
	level.player.velocity = Vector2.ZERO
	await frames(6)
	check(potion.used and level.player.health == 3, "major potion resets and caps partial missing HP")
	# Deterministic injected RNG for real kill healing, using the production death signal.
	var seed_value := 0
	while true:
		var probe := RandomNumberGenerator.new()
		probe.seed = seed_value
		if probe.randf() < 0.03: break
		seed_value += 1
	var enemy = level.get_node("Enemies/Slime1")
	level.player.health_units = 10
	level.chest_economy.rng.seed = seed_value
	enemy.set_meta("healing_profile", "elite")
	enemy.take_damage(99, Vector2.ZERO)
	check(level.player.health == 2 and level.bonus == 1, "production death signal gives elite instant one HP heal and shards")
	enemy.take_damage(99, Vector2.ZERO)
	check(level.player.health == 2 and level.bonus == 1, "duplicate death cannot repeat heal or shards")
	var skull = level.get_node("Enemies/Slime2")
	skull.set_meta("healing_profile", "skull")
	level.chest_economy.rng.seed = seed_value
	skull.take_damage(99, Vector2.ZERO)
	check(level.player.health == 2, "skull profile never heals even with winning RNG")
	level.player.die()
	await frames(210)
	level = current_scene
	check(level.player.equipment.melee == "Halberds3" and level.bonus == 0 and level.chest_economy.counts.common == 0 and not level.get_node("MajorPotion").used, "real death/restart retains equipment and resets gains prices and healing pickup")
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for emitter in root.find_children("*", audio_type, true, false): emitter.stop()
	paused = false
	level.queue_free()
	await frames()
	progress.persistence_enabled = false
	DirAccess.remove_absolute(PATH)
	for suffix in [".tmp", ".bak", ".bak.1"]: DirAccess.remove_absolute(PATH + suffix)
	OS.delay_msec(300) # Drain real-time audio after accelerated headless simulation.
	print("RESULT %d reward transaction checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

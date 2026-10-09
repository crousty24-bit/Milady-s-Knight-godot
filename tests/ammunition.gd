extends SceneTree
const Store = preload("res://scripts/progression.gd")
const NEXT = "res://tests/fixtures/next_level.tscn"
var checks := 0
var failures := 0
var room: Node2D
var player: SlicePlayer
var shot_count := 0
var empty_count := 0
var collected: Array = []
var stores: Array = []
var path: String
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func make_store() -> Node:
	var store = Store.new()
	store.storage_path = path
	stores.append(store)
	return store
func fixture(data: Dictionary) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()
func spawn(stocks: Dictionary = SlicePlayer.AMMO_DEFAULTS) -> void:
	Input.action_release("attack")
	if is_instance_valid(room):
		room.queue_free()
		await frames(2)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	var floor_body := StaticBody2D.new()
	floor_body.position = Vector2(400, 208)
	floor_body.collision_layer = 1
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = Vector2(1800, 16)
	floor_body.add_child(shape)
	room.add_child(floor_body)
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(160, 200)
	room.add_child(player)
	player.initialize_ammo(stocks)
	shot_count = 0
	empty_count = 0
	collected.clear()
	player.projectile_fired.connect(func(_arrow: Node2D): shot_count += 1)
	player.ammo_empty.connect(func(_family: String): empty_count += 1)
	player.ammo_collected.connect(func(family: String, amount: int): collected.append([family, amount]))
	await frames(4)
func equip(item: String) -> void:
	player.configure_loadout({"melee": "Sword0", "ranged": item})
	player.active_slot = 1
func scene_attempt(scene_path: String) -> void:
	paused = false
	if is_instance_valid(room):
		for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for emitter in room.find_children("*", audio_type, true, false): emitter.stop()
		OS.delay_msec(300)
		room.queue_free()
		await frames(3)
	room = load(scene_path).instantiate()
	root.add_child(room)
	current_scene = room
	await frames(2)
	# Transaction isolation only: no traversal claim or authored scene edits.
	for group in ["Enemies", "Hazards"]:
		for node in room.get_node(group).get_children(): node.queue_free()
	player = room.player
	player.controls_enabled = false
	player.set_physics_process(false)
	await frames(2)
func real_level_snapshots() -> void:
	var progress = root.get_node("Progression")
	progress.storage_path = path
	progress.persistence_enabled = true
	progress.storage_error = OK
	progress.has_save = true
	progress._apply(stores[0]._initial_state())
	var n2 := "res://scenes/blight_town.tscn"
	var n3 := "res://scenes/black_forrest.tscn"
	check(progress.settle_level(0, n2, {"Longbow": 4, "ThrowingKnives": 6}) == OK, "real level fixture persists N2 entry stocks")
	await scene_attempt(n2)
	check(player.ammo == {"Longbow": 4, "ThrowingKnives": 6}, "production N2 ready initializes its matching durable entry snapshot")
	equip("Longbow0")
	player._fire_arrow()
	player.bow_cooldown = 0.0 # Isolate settlement from firing cadence already tested above.
	player._fire_arrow()
	room.bonus = 3
	DirAccess.make_dir_absolute(ProjectSettings.globalize_path(path + ".tmp"))
	room._settle_reward()
	check(not room.reward_settled and progress.resume_scene == n2 and progress.ammo_entry.Longbow == 4 and player.ammo.Longbow == 2, "production settlement disk failure retains entry snapshot and live current separately")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path + ".tmp"))
	room._settle_reward()
	room._settle_reward()
	check(room.reward_settled and progress.resume_scene == n3 and progress.ammo_entry.Longbow == 2 and progress.banked_shards == 3, "production N2 settlement retries once and carries two arrows to N3 atomically")
	await scene_attempt(n3)
	check(player.ammo.Longbow == 2 and player.ammo.ThrowingKnives == 6, "production N3 ready starts with N2 current stocks")
	player.add_ammo("Longbow", 5)
	check(player.ammo.Longbow == 7 and progress.ammo_entry.Longbow == 2, "production N3 loot remains attempt-only")
	# Exercise the actual restart method, which rebuilds the authored scene.
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for emitter in room.find_children("*", audio_type, true, false): emitter.stop()
	OS.delay_msec(300)
	room._restart_attempt()
	await frames(5)
	room = current_scene
	player = room.player
	player.controls_enabled = false
	player.set_physics_process(false)
	check(player.ammo.Longbow == 2 and progress.resume_scene == n3, "production restart discards N3 loot and restores its two-arrow entry")
	player.add_ammo("Longbow", 5)
	player.die()
	check(room.modal == "death" and player.ammo.Longbow == 7 and progress.ammo_entry.Longbow == 2, "production death enters death modal without persisting acquired ammunition")
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for emitter in room.find_children("*", audio_type, true, false): emitter.stop()
	OS.delay_msec(300)
	room._restart_attempt()
	await frames(5)
	room = current_scene
	player = room.player
	check(not player.dead and player.ammo.Longbow == 2, "production retry after death restores N3 entry stock")
	progress.persistence_enabled = false
func run() -> void:
	await spawn()
	check(player.ammo == {"Longbow": 10, "ThrowingKnives": 12}, "new attempt initializes both families before ownership")
	equip("Longbow0")
	Input.action_press("attack")
	await frames(2)
	check(shot_count == 1 and player.ammo.Longbow == 9, "mapped attack creates one projectile and consumes one arrow")
	await frames(20)
	check(shot_count == 1 and player.ammo.Longbow == 9, "held input during cooldown consumes no ammunition")
	var cooldown_before := player.bow_cooldown
	paused = true
	await frames(5)
	check(shot_count == 1 and player.ammo.Longbow == 9 and player.bow_cooldown == cooldown_before, "pause freezes held attack and cooldown without ammunition loss")
	paused = false
	Input.action_release("attack")
	equip("Longbow3")
	check(player.ammo.Longbow == 9 and player.bow_cooldown > 0.0, "upgrade preserves ammunition and running slot cooldown")
	equip("ThrowingKnives0")
	equip("Longbow0")
	player.initialize_ammo(SlicePlayer.AMMO_DEFAULTS)
	check(player.ammo.Longbow == 9 and player.ammo.ThrowingKnives == 12, "family swaps and repeated setup cannot refill pools")
	check(player.add_ammo("Longbow", 10) == 6 and player.ammo.Longbow == 15, "partial pickup returns actual amount up to bow cap")
	check(player.add_ammo("Longbow", 1) == 0 and collected == [["Longbow", 6]], "full stock leaves pickup untouched and emits no collected feedback")
	check(player.add_ammo("ThrowingKnives", 50) == 8 and player.ammo.ThrowingKnives == 20, "independent knife reserve is capped at twenty")
	check(player.add_ammo("Flamethrower", 5) == 0 and player.add_ammo("Longbow", -1) == 0, "unsupported family and invalid amount cannot change ammunition")
	await spawn({"Longbow": 1, "ThrowingKnives": 0})
	equip("Longbow0")
	Input.action_press("attack")
	await frames(135)
	Input.action_release("attack")
	check(shot_count == 1 and player.ammo.Longbow == 0 and player.bow_cooldown <= 0.000001 and empty_count > 0, "last arrow fires once then empty held input creates no projectile or cooldown")
	equip("ThrowingKnives5")
	Input.action_press("attack")
	await frames(2)
	Input.action_release("attack")
	check(shot_count == 1 and player.ammo.ThrowingKnives == 0 and player.bow_cooldown <= 0.000001, "zero upgraded knives refuse shooting without cooldown")
	check(player.add_ammo("ThrowingKnives", 3) == 3, "pickup restores empty family while another family stays empty")
	Input.action_press("attack")
	await frames(2)
	Input.action_release("attack")
	check(shot_count == 2 and player.ammo.ThrowingKnives == 2 and player.ammo.Longbow == 0, "knife projectile consumes only its own family")
	player.die()
	check(player.add_ammo("Longbow", 5) == 0, "dead player cannot collect loot")
	# Entry snapshots are persisted independently of all live pickups and shots.
	path = "user://ammunition-test-%d-%d.json" % [OS.get_process_id(), Time.get_ticks_usec()]
	var store = make_store()
	check(store.new_game() == OK and store.ammo_entry == SlicePlayer.AMMO_DEFAULTS, "new game persists base entry reserves")
	check(store.settle_level(7, NEXT, {"Longbow": 2, "ThrowingKnives": 4}) == OK and store.ammo_entry == {"Longbow": 2, "ThrowingKnives": 4}, "next destination atomically receives current stocks as new entry snapshot")
	await spawn(store.ammo_entry)
	check(player.ammo.Longbow == 2 and player.ammo.ThrowingKnives == 4, "N3 attempt starts with the remaining N2 stocks")
	player.add_ammo("Longbow", 5)
	check(store.set_permanent_flag("ammo-test") == OK, "unrelated durable action succeeds during looting")
	var cold = make_store()
	check(cold.load_progress() == OK and cold.ammo_entry.Longbow == 2 and cold.resume_scene == NEXT and cold.banked_shards == 7, "cold Continue discards attempt loot while retaining destination and bank")
	await spawn(cold.ammo_entry)
	check(player.ammo.Longbow == 2, "new attempt from disk reload restores entry reserve rather than base ten")
	player.add_ammo("Longbow", 5)
	check(cold.settle_level(0, NEXT, player.ammo) == OK and cold.ammo_entry.Longbow == 2, "replay same level never banks farmed loot")
	var saved: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	saved.erase("ammo_entry")
	fixture(saved)
	var old = make_store()
	check(old.load_progress() == OK and old.ammo_entry == SlicePlayer.AMMO_DEFAULTS, "older v2 without optional snapshot loads ten and twelve")
	for invalid in [null, {}, {"Longbow": 1}, {"Longbow": -1, "ThrowingKnives": 4}, {"Longbow": 16, "ThrowingKnives": 4}, {"Longbow": 1.5, "ThrowingKnives": 4}, {"Longbow": "2", "ThrowingKnives": 4}, {"Longbow": true, "ThrowingKnives": 4}, {"Longbow": 2, "ThrowingKnives": 21}, {"Longbow": 2, "ThrowingKnives": 4, "extra": 1}]:
		saved.ammo_entry = invalid
		fixture(saved)
		var original := FileAccess.get_file_as_string(path)
		var rejected = make_store()
		check(rejected.load_progress() == ERR_FILE_CORRUPT and not rejected.has_save and rejected.settle_level(1, NEXT) != OK and FileAccess.get_file_as_string(path) == original, "invalid optional snapshot rejects Continue and prevents overwrite: " + str(invalid))
	fixture(cold._state())
	var retry = make_store()
	check(retry.load_progress() == OK, "save retry fixture loads entry snapshot")
	DirAccess.make_dir_absolute(ProjectSettings.globalize_path(path + ".tmp"))
	check(retry.settle_level(9, Store.DEFAULT_LEVEL, {"Longbow": 7, "ThrowingKnives": 8}) != OK and retry.ammo_entry.Longbow == 2 and retry.banked_shards == 7 and retry.resume_scene == NEXT, "failed atomic settlement changes neither ammunition nor destination nor bank")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path + ".tmp"))
	check(retry.settle_level(9, Store.DEFAULT_LEVEL, {"Longbow": 7, "ThrowingKnives": 8}) == OK and retry.ammo_entry.Longbow == 7 and retry.banked_shards == 16, "retry after repaired storage carries ammunition and reward exactly once")
	check(retry.settle_level(0, NEXT, {"Longbow": 99, "ThrowingKnives": 8}) == ERR_INVALID_PARAMETER and retry.ammo_entry.Longbow == 7, "out of cap transition cannot mutate snapshot")
	check(retry.new_game() == OK and retry.ammo_entry == SlicePlayer.AMMO_DEFAULTS, "confirmed New Game resets previous depleted snapshot")
	await real_level_snapshots()
	for suffix in ["", ".tmp", ".bak"]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path + suffix))
	for object in stores: object.free()
	Input.action_release("attack")
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for emitter in room.find_children("*", audio_type, true, false): emitter.stop()
	OS.delay_msec(300)
	room.queue_free()
	await frames(3)
	print("RESULT %d ammunition checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

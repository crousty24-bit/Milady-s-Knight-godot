extends SceneTree
const Store = preload("res://scripts/progression.gd")
const NEXT = "res://tests/fixtures/next_level.tscn"
var checks := 0
var failures := 0
var level: Node2D
var progress: Node
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func spawn() -> void:
	if is_instance_valid(level):
		level.queue_free()
		await frames(3)
	level = load(Store.DEFAULT_LEVEL).instantiate()
	root.add_child(level)
	current_scene = level
	await frames(6)
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames(6)
func write_fixture(path: String, text: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(text)
	file.close()
func run() -> void:
	progress = root.get_node("Progression")
	check(not progress.persistence_enabled, "test drivers cannot change the player's real save")
	progress.banked_bonus = 20
	await spawn()
	check(level.hud.get_node("Bonus").text == "BONUS 20", "HUD displays existing reserve on entering level")
	var enemy = level.get_node("Enemies/Slime1")
	level.register_enemy(enemy)
	level.register_enemy(enemy)
	enemy.take_damage(1, Vector2.ZERO)
	check(level.bonus == 0, "damaging an enemy does not grant a reward")
	enemy.take_damage(2, Vector2.ZERO)
	check(level.bonus == 1 and progress.banked_bonus == 20, "slime death grants one pending bonus, without banking it")
	enemy.take_damage(99, Vector2.ZERO)
	check(level.bonus == 1, "dead enemy cannot award twice")
	var second = level.get_node("Enemies/Slime2")
	second.bonus_reward = 3
	second.take_damage(3, Vector2.ZERO)
	check(level.bonus == 4, "future enemy reward values use the same death contract")
	var feedback_count := 0
	for child in level.get_children():
		if child.get("bonus_feedback") != null and child.bonus_feedback > 0:
			feedback_count += 1
			check(child.picked_up and child.get_node("Sprite").sprite_frames.get_frame_texture("idle", 0).atlas.resource_path == "res://assets/sprites/coin.png", "reward feedback reuses coin art and cannot be collected again")
	check(feedback_count == 2, "both defeats show existing coin feedback")
	level._on_collected(11)
	check(not level.try_offering() and level.gold == 11 and level.bonus == 4, "reserve and enemy bonuses cannot pay missing seal coins")
	level._on_collected(3)
	check(level.gold == 12 and level.bonus == 6, "pickup crossing threshold splits seal coins and surplus")
	check(level.hud.get_node("Gold").text == "SCEAU 12/12" and level.hud.get_node("Bonus").text == "BONUS 26" and level.hud.get_node("BonusPending").text == "+6 a valider", "HUD distinguishes seal, total bonus and pending gains")
	check(level.try_offering() and level.gold == 0 and level.bonus == 6, "payment spends only the twelve seal coins")
	level._on_collected(2)
	check(level.gold == 0 and level.bonus == 8, "all pickups after opening the seal become bonuses")
	level._on_exit(level.player)
	check(progress.banked_bonus == 28 and level.reward_settled, "finishing banks the current attempt exactly once")
	level._on_exit(level.player)
	level._settle_reward()
	level._on_collected(9)
	check(progress.banked_bonus == 28 and level.bonus == 8, "duplicate finish and late pickups cannot duplicate rewards")
	check(level.hud.get_node("BonusPending").text == "reserve 28", "settled HUD no longer counts bonus as pending")
	await spawn()
	level._on_collected(14)
	level.get_node("Enemies/Slime1").take_damage(3, Vector2.ZERO)
	level.player.die()
	check(level.bonus == 0 and progress.banked_bonus == 28, "death discards only current-attempt bonuses")
	await tap("interact")
	level = current_scene
	check(level.bonus == 0 and level.gold == 0 and progress.banked_bonus == 28, "death confirmation retains bank and clears level currencies")
	level._on_collected(15)
	await tap("special_attack")
	check(current_scene == level and level.bonus == 3 and progress.banked_bonus == 28, "R cannot discard pending rewards by restarting")
	level.player.die()
	await tap("interact")
	level = current_scene
	check(level.bonus == 0 and progress.banked_bonus == 28, "confirmed death restart discards pending surplus")
	level.next_level_scene = NEXT
	level._on_collected(13)
	level.try_offering()
	level._on_exit(level.player)
	await tap("interact")
	level = current_scene
	check(level.scene_file_path == NEXT and progress.resume_scene == NEXT and progress.banked_bonus == 29, "E changes to the configured next level with bank intact")
	check(level.gold == 0 and level.bonus == 0 and level.player.health == 3 and not level.gate.opened and level.get_node("Coins").get_child_count() == 18, "next level starts with a fresh attempt and fresh seal")
	check(not level.try_offering(), "carried bonus reserve cannot open next level's seal")
	# Isolated file on the actual save filesystem (NTFS on Windows), never progress.json.
	var path := "user://astra-bonus-test-%d-%d.json" % [OS.get_process_id(), Time.get_ticks_usec()]
	var first_store = Store.new()
	first_store.storage_path = path
	check(first_store.settle_level(4, Store.DEFAULT_LEVEL) == OK, "writes a versioned save to disk")
	var reopened = Store.new()
	reopened.storage_path = path
	check(reopened.load_progress() == OK and reopened.banked_bonus == 4, "fresh session reads saved bank")
	check(reopened.settle_level(3, NEXT) == OK, "atomic replacement updates an existing save")
	var third = Store.new()
	third.storage_path = path
	check(third.load_progress() == OK and third.banked_bonus == 7 and third.resume_scene == NEXT, "fresh session reads both bank and next scene")
	var contents := FileAccess.get_file_as_string(path)
	check(third.settle_level(1, "res://missing-level.tscn") != OK and FileAccess.get_file_as_string(path) == contents, "invalid next level cannot change save or award bonus")
	third.storage_path = "res://work/missing-save-dir-%d/progress.json" % OS.get_process_id()
	check(third.settle_level(1, NEXT) != OK and third.banked_bonus == 7, "failed write does not credit an unsaved balance")
	third.storage_path = path
	write_fixture(path, '{"version":1,"bonus_bank":-2,"resume_scene":"res://scenes/vertical_slice.tscn"}')
	check(third.load_progress() != OK and third.settle_level(1, NEXT) != OK and FileAccess.get_file_as_string(path).contains('"bonus_bank":-2'), "corrupt save is rejected and never overwritten")
	write_fixture(path, JSON.stringify({"version": 1, "bonus_bank": 9, "resume_scene": NEXT}))
	check(third.settle_level(1, NEXT) == OK and third.banked_bonus == 10, "save retry recovers without double credit after file repair")
	write_fixture(path, JSON.stringify({"version": 99, "bonus_bank": 10, "resume_scene": NEXT}))
	check(third.load_progress() != OK and third.settle_level(1, NEXT) != OK, "unknown future save version is protected")
	write_fixture(path, JSON.stringify({"version": 1, "bonus_bank": 10, "resume_scene": "res://removed-level.tscn"}))
	check(third.load_progress() == OK and third.banked_bonus == 10 and third.resume_scene == Store.DEFAULT_LEVEL, "removed scene falls back without losing saved bank")
	# Boot scene resumes a saved destination instead of always loading level one.
	progress.resume_scene = NEXT
	change_scene_to_file("res://scenes/game.tscn")
	await frames(10)
	level = current_scene
	check(level.scene_file_path == NEXT and progress.banked_bonus == 29, "game bootstrap resumes the stored level")
	progress.persistence_enabled = true
	progress.storage_path = "res://work/missing-save-dir-%d/progress.json" % OS.get_process_id()
	level._on_collected(14)
	level.try_offering()
	level._on_exit(level.player)
	check(level.finished and not level.reward_settled and level.bonus == 2 and progress.banked_bonus == 29, "failed victory save retains pending bonus and offers retry")
	await tap("special_attack")
	check(current_scene == level and level.bonus == 2, "R cannot discard rewards while victory save is awaiting retry")
	progress.storage_path = path
	await tap("interact")
	check(level.reward_settled and progress.banked_bonus == 31, "E retries the victory save and credits once")
	await tap("interact")
	check(progress.banked_bonus == 31, "repeated E after settlement cannot award again")
	level = current_scene
	progress.persistence_enabled = false
	level.hud.set_bonus(1234567, 23)
	var label: Label = level.hud.get_node("Bonus")
	var width: float = label.get_theme_font("font").get_string_size(label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x
	check(label.position.x + width < level.hud.get_node("PauseHint").position.x, "large bonus reserve remains readable without overlapping pause hint")
	first_store.free()
	reopened.free()
	third.free()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	level.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " bonus checks; ", failures, " failures")
	quit(failures)

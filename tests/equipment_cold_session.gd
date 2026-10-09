extends SceneTree
const FIXTURE_PATH = "res://tests/fixtures/economy_level.tscn"
const SAVE = "user://run018-cold.json"
var checks := 0
var failures := 0
var level: Node2D
var progress: Node
func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in count:
		await process_frame
		await physics_frame
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
func enter_common() -> Area2D:
	level.player.position = Vector2(120, 144)
	level.player.velocity = Vector2.ZERO
	await frames(4)
	return level.get_node("CommonChest")
func run() -> void:
	progress = root.get_node("Progression")
	progress.storage_path = SAVE
	progress.persistence_enabled = true
	var stage: String = OS.get_cmdline_user_args()[0]
	if stage == "open":
		DirAccess.remove_absolute(SAVE)
		check(progress.new_game() == OK and progress.settle_level(50, FIXTURE_PATH) == OK, "dedicated cold fixture saves initial bank and level")
		level = load(FIXTURE_PATH).instantiate()
		root.add_child(level)
		current_scene = level
		await frames(8)
		level.bonus = 3
		var chest: Area2D = await enter_common()
		chest.offer = {"item": "Longsword2", "upgrade": "Sword1"}
		await tap("interact")
		check(paused and progress.banked_shards == 48 and level.bonus == 0 and chest.paid, "cold opening debits bank before any acceptance")
		check(progress.equipment.melee == "Sword0", "unaccepted reward leaves initial equipment")
	else:
		check(progress.load_progress() == OK, "fresh process reads dedicated previous save")
		var game = load("res://scenes/game.tscn").instantiate()
		root.add_child(game)
		current_scene = game
		await frames(8)
		await tap("move_down")
		await tap("interact")
		await frames(12)
		level = current_scene
		check(level.scene_file_path == FIXTURE_PATH and level.bonus == 0 and level.gold == 0 and level.chest_economy.counts.common == 0 and not level.get_node("CommonChest").paid, "keyboard Continue restores fresh attempt prices gains and chest")
		if stage == "accept":
			check(progress.banked_shards == 48 and level.player.equipment.melee == "Sword0", "closure after opening retains debit without granting abandoned offer")
			var chest: Area2D = await enter_common()
			chest.offer = {"item": "ThrowingKnives2", "upgrade": ""}
			await tap("interact")
			await open_cards()
			await tap("interact")
			check(progress.equipment.ranged == "ThrowingKnives2" and progress.banked_shards == 43, "cold acquisition commits once after new attempt payment")
			level.bonus = 7
		else:
			check(progress.banked_shards == 43 and level.player.equipment.ranged == "ThrowingKnives2" and level.bonus == 0, "closure after acceptance retains new weapon and debit while discarding gains")
			await tap("switch_equipment")
			check(level.player.active_slot == 1, "continued Throwing Knives can be selected with A")
			for suffix in ["", ".tmp", ".bak", ".bak.1"]: DirAccess.remove_absolute(SAVE + suffix)
	print("RESULT %d equipment cold %s checks; %d failures" % [checks, stage, failures])
	if failures:
		paused = false
		quit(1)
	else:
		level._notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)

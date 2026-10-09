extends SceneTree
const FIXTURE_PATH = "res://tests/fixtures/run019_systems.tscn"
const SAVE = "user://run019-cold.json"
var checks := 0
var failures := 0
var level: Node2D
var progress: Node
func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames(3)
func clear_enemies() -> void:
	for enemy in level.get_node("Enemies").get_children(): enemy.queue_free()
func run() -> void:
	progress = root.get_node("Progression")
	progress.storage_path = SAVE
	progress.persistence_enabled = true
	var stage: String = OS.get_cmdline_user_args()[0]
	if stage == "prepare":
		check(progress.new_game() == OK and progress.settle_level(7, FIXTURE_PATH) == OK, "cold fixture initializes isolated v2 bank and scene")
		level = load(FIXTURE_PATH).instantiate()
		root.add_child(level)
		current_scene = level
		clear_enemies()
		await frames(8)
		level.player.health_units = 10
		level.player.position = Vector2(368, 144)
		level.player.velocity = Vector2.ZERO
		await frames(5)
		check(progress.hp_bonus_count() == 1 and level.player.health_units == 20 and level.player.max_health_units == 40, "physical heart durable before process closure")
		level.player.position = Vector2(396, 144)
		level.player.velocity = Vector2.ZERO
		level.player.facing = 1
		await frames(3)
		await tap("attack")
		await frames(22)
		check(level.get_node("Secret").opened and progress.permanent_flags.get("secret:run019_fixture_secret", false), "physical sword reveals and saves secret before closure")
		level.player.position = Vector2(90, 144)
		level.player.velocity = Vector2.ZERO
		await frames(5)
		level.gold = 3
		await tap("interact")
		check(level.get_node("CoinDoor").opened and level.gold == 0, "paid door opened during closing attempt")
		level.player.activate_magic_shield()
		level.bonus = 5
	else:
		check(progress.load_progress() == OK and progress.hp_bonus_count() == 1 and progress.banked_shards == 7, "fresh process loads v2 unique bonus and original bank")
		var game = load("res://scenes/game.tscn").instantiate()
		root.add_child(game)
		current_scene = game
		await frames(8)
		await tap("move_down")
		await tap("interact")
		await frames(12)
		level = current_scene
		clear_enemies()
		check(level.scene_file_path == FIXTURE_PATH and level.player.health_units == 40 and level.player.max_health_units == 40, "keyboard Continue respawns healed at durable maximum")
		check(level.get_node("Bonus").used and level.get_node("Secret").opened and not level.get_node("Secret").visible, "cold restore removes acquired heart and opens secret without reveal")
		check(not level.get_node("CoinDoor").opened and not level.get_node("Button").active and not level.get_node("Plate").active and level.gold == 0 and level.bonus == 0, "closure discards coins gains doors and mechanisms")
		check(level.player.magic_shield_time == 0.0 and not level.get_node("Shield").used, "closure clears buff and restores shield pickup")
		if stage == "reset":
			check(progress.new_game() == OK and progress.hp_bonus_count() == 0 and not progress.permanent_flags.has("secret:run019_fixture_secret"), "confirmed New Game clears both durable acquisitions")
			for suffix in ["", ".tmp", ".bak", ".bak.1"]: DirAccess.remove_absolute(SAVE + suffix)
	print("RESULT %d run019 cold %s checks; %d failures" % [checks, stage, failures])
	if failures:
		paused = false
		level.queue_free()
		await frames(3)
		quit(1)
	else:
		level._notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)

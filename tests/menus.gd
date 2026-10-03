extends SceneTree
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames()
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func capture(label: String) -> void:
	if DisplayServer.get_name() == "headless": return
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://work/run015")
	root.get_texture().get_image().save_png("res://work/run015/" + label + ".png")
	await process_frame

# This suite isolates menu behavior; the complete introduction/tutorial flow is n1_flow.
func settle_intro() -> void:
	if current_scene.scene_file_path != root.get_node("Progression").DEFAULT_LEVEL: return
	# Cinematic ownership must finish before isolating the menu-only fixture.
	for i in range(240):
		if current_scene.modal != "resurrection" and not current_scene.resume_pending: break
		await frames(1)
	root.get_node("Progression").complete_dialogue(current_scene.INTRO_ID)
	for item in current_scene.TUTORIALS:
		root.get_node("Progression").complete_dialogue(item[0])
	current_scene.n1_intro_enabled = false

func run() -> void:
	var progress = root.get_node("Progression")
	progress.storage_path = "user://run015-menu-%d.json" % OS.get_process_id()
	progress.persistence_enabled = true
	progress.load_progress()
	progress.has_save = false
	var game = load("res://scenes/game.tscn").instantiate()
	root.add_child(game)
	current_scene = game
	await frames()
	check(game.music.playing and game.music.bus == &"Music" and game.music.stream.loop, "menu plays chosen music loop on Music bus")
	game.music.seek(game.music.stream.get_length() - 0.05)
	OS.delay_msec(350)
	await frames(3)
	check(game.music.playing and game.music.get_playback_position() < 1.0, "menu music passes end of track and restarts its loop")
	var menu_music_ref: WeakRef = weakref(game.music)
	await capture("main")
	check(game.screen == "main" and game.menu.opened and 1 in game.menu.unavailable, "cold boot opens main menu with Continue unavailable without save")
	await tap("move_down")
	check(game.menu.selection == 2, "keyboard skips disabled Continue")
	await tap("interact")
	await capture("controls")
	check(game.screen == "controls", "E opens Controls")
	check(game.music.playing and menu_music_ref.get_ref() == game.music, "Controls keeps the same menu music player")
	await tap("pause")
	check(game.screen == "main", "Escape returns from Controls")
	await tap("interact")
	await frames(8)
	await settle_intro()
	var level = current_scene
	check(menu_music_ref.get_ref() == null and level.get_node("Music").playing, "entering gameplay removes menu music and starts level music")
	check(level != game and progress.has_save and level.gold == 0 and level.bonus == 0, "New Game writes initial save and spawns fresh attempt")
	level.gold = 15
	level.bonus = 8
	level.player.position = Vector2(2040, 144)
	level.player.velocity = Vector2.ZERO
	await frames()
	await tap("pause")
	await capture("pause")
	check(paused and level.modal == "pause", "Escape opens exclusive pause menu")
	check(not level.request_context("Reward", "", ["Accept"]), "second modal cannot replace pause")
	var pos: Vector2 = level.player.position
	Input.action_press("move_right")
	Input.action_press("attack")
	Input.action_press("jump")
	await frames(8)
	check(level.player.position == pos and not level.gate.opened, "paused gameplay inputs cannot move or open gate")
	for action in ["move_right", "attack", "jump"]: Input.action_release(action)
	await tap("pause")
	check(not paused and level.modal.is_empty(), "Escape resumes without opening another modal")
	var result := []
	check(level.request_context("Reward", "One choice", ["Accept"], func(index: int): result.append(index)), "context modal acquires exclusive ownership")
	level.gate.opened = true
	level._on_exit(level.player)
	check(not level.finished and level.modal == "context", "exit cannot replace an active context modal")
	level.gate.opened = false
	await frames()
	await capture("context")
	await tap("pause")
	check(not paused and level.modal.is_empty() and result.is_empty(), "Escape cancels context without opening pause or confirming reward")
	check(level.request_context("Reward", "One choice", ["Accept"], func(index: int): result.append(index)), "context can be reopened after keys released")
	await frames()
	Input.action_press("interact")
	await frames(8)
	check(result == [0] and not level.gate.opened and level.resume_pending, "held E confirms once and cannot pass through to gate")
	Input.action_release("interact")
	await frames()
	await tap("pause")
	await tap("move_down")
	await tap("interact")
	await frames(8)
	level = current_scene
	level.n1_intro_enabled = false
	check(level.gold == 0 and level.bonus == 0 and not paused, "Restart clears attempt and unpauses")
	await tap("pause")
	await tap("move_down")
	await tap("move_down")
	await tap("interact")
	await frames(8)
	game = current_scene
	check(game.music.playing and game.music.stream.loop, "returning to menu restarts chosen looping theme")
	check(game.scene_file_path == "res://scenes/game.tscn" and not paused, "Quit to menu returns to main menu")
	await tap("interact")
	await capture("confirm")
	check(game.screen == "new" and game.menu.selection == 0, "New Game with save defaults to Cancel confirmation")
	await tap("pause")
	check(game.screen == "main" and progress.has_save, "Escape cancels replacement without losing save")
	await tap("move_down")
	await tap("interact")
	await frames(8)
	check(current_scene.scene_file_path == progress.resume_scene and current_scene.gold == 0, "Continue resumes saved level at fresh spawn")
	level = current_scene
	level.n1_intro_enabled = false
	await tap("pause")
	Input.action_press("interact")
	await frames()
	level.player.die()
	await frames(210)
	check(current_scene != level and not current_scene.player.dead, "death during held Resume still completes automatic reset")
	Input.action_release("interact")
	current_scene.queue_free()
	await frames()
	var file := FileAccess.open(progress.storage_path, FileAccess.WRITE)
	var original := JSON.stringify({"version": 1, "bonus_bank": 17, "resume_scene": progress.DEFAULT_LEVEL})
	file.store_string(original)
	file.close()
	progress.load_progress()
	game = load("res://scenes/game.tscn").instantiate()
	root.add_child(game)
	current_scene = game
	await frames()
	await tap("move_down")
	await tap("interact")
	check(game.screen == "migration" and game.menu.selection == 0, "legacy Continue requires agreement and defaults to Cancel")
	await capture("migration")
	await tap("pause")
	check(game.screen == "main" and FileAccess.get_file_as_string(progress.storage_path) == original, "refusing migration leaves original unchanged")
	await tap("move_down")
	await tap("interact")
	await tap("move_down")
	await tap("interact")
	await frames(8)
	await settle_intro()
	check(current_scene.scene_file_path == progress.DEFAULT_LEVEL and progress.banked_shards == 17 and FileAccess.get_file_as_string(progress.storage_path + ".v1.bak") == original, "accepted migration enters saved level and preserves original")
	current_scene.queue_free()
	await frames()
	file = FileAccess.open(progress.storage_path, FileAccess.WRITE)
	file.store_string("corrupted-save")
	file.close()
	progress.load_progress()
	game = load("res://scenes/game.tscn").instantiate()
	root.add_child(game)
	current_scene = game
	await frames()
	check(1 in game.menu.unavailable and game.menu.description.text.contains("protected"), "corrupt save disables Continue with visible protection message")
	await tap("interact")
	await tap("pause")
	check(FileAccess.get_file_as_string(progress.storage_path) == "corrupted-save", "cancelling New Game preserves corrupt original for recovery")
	var actual_path: String = progress.storage_path
	progress.storage_path = "res://work/run015-absent-dir/save.json"
	progress.has_save = false
	progress.storage_error = OK
	game._main()
	await frames()
	await tap("interact")
	check(game.screen == "error" and progress.banked_shards == 17, "disk failure displays error and does not start or replace game")
	await capture("save-error")
	progress.storage_path = actual_path
	DirAccess.remove_absolute(ProjectSettings.globalize_path(actual_path + ".v1.bak"))
	progress.persistence_enabled = false
	DirAccess.remove_absolute(ProjectSettings.globalize_path(progress.storage_path))
	current_scene.queue_free()
	await frames()
	OS.delay_msec(300)
	print("RESULT ", checks, " menu checks; ", failures, " failures")
	quit(failures)

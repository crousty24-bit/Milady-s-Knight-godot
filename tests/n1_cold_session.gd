# Run twice with the same isolated user profile: -- prepare, then -- reopen.
extends SceneTree
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int = 5) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func tap(action: String) -> void:
	await process_frame
	Input.action_press(action)
	await process_frame
	await process_frame
	Input.action_release(action)
	await frames()
func check(ok: bool, detail: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", detail)
	if not ok: failures += 1
func run() -> void:
	var progress = root.get_node("Progression")
	progress.storage_path = "user://run017-cold-session.json"
	progress.persistence_enabled = true
	var prepare := "prepare" in OS.get_cmdline_user_args()
	if prepare:
		check(progress.new_game() == OK and progress.settle_level(20, progress.DEFAULT_LEVEL) == OK, "isolated cold-session fixture writes bank and N1 resume")
	else:
		check(progress.load_progress() == OK and progress.has_save, "fresh engine process reads previous session save")
	progress.change_level("res://scenes/game.tscn")
	await frames(10)
	await tap("move_down")
	await tap("interact")
	await frames(10)
	var level = current_scene
	if prepare:
		for i in range(240):
			if level.modal != "resurrection" and not level.resume_pending: break
			await frames(1)
		Input.action_press("move_right")
		for i in range(180):
			await frames(1)
			if level.modal in ["spirit_appearance", "dialogue"]: break
		Input.action_release("move_right")
		for i in range(120):
			if level.modal == "dialogue": break
			await frames(1)
		check(level.modal == "dialogue" and level.player.position.x >= level.intro_spawn_x + 32, "cold preparation waits resurrection and walks two blocks to Spirit dialogue")
		for i in range(level.dialogue_panel.lines.size()): await tap("jump")
		await tap("interact")
		level.player.position = level.tutorial_chest.position
		level.player.velocity = Vector2.ZERO
		await frames(10)
		await tap("interact")
		await tap("interact")
		check(level.player.has_longbow and progress.completed_dialogues.has(level.INTRO_ID), "physical chest and phrase-by-phrase intro commit before closure")
		# Inject attempt counters only to distinguish them from the durable bank on reopen.
		level._on_collected(7)
		level.bonus = 3
		level._update_gold_hud()
		check(level.gold == 7 and level.bonus == 3 and progress.banked_shards == 20, "unsettled attempt gains remain separate before closure")
		level.notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)
		var voice_playing := false
		for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for emitter in root.find_children("*", audio_type, true, false):
				voice_playing = voice_playing or emitter.playing
		check(level.closing and not voice_playing, "close handler stops music and active equip/reward voices before engine exit")
		print("RESULT ", checks, " N1 cold prepare checks; ", failures, " failures")
		if failures: quit(1)
		# Normal engine exit is performed by level's close handler, not this driver.
		return
	check(level.scene_file_path == progress.DEFAULT_LEVEL and level.modal.is_empty() and level.player.has_longbow and level.tutorial_chest.consumed and progress.permanent_flags.has(level.RESURRECTION_ID), "keyboard Continue in new process keeps bow and does not replay resurrection or intro")
	check(level.gold == 0 and level.bonus == 0 and progress.banked_shards == 20 and level.player.health == 3.0 and level.player.position.distance_to(Vector2(48, 144)) < 1, "cold Continue restores safe spawn and bank while discarding attempt gains")
	level.queue_free()
	var ui_audio := root.get_node_or_null("UiSfx") as AudioStreamPlayer
	if ui_audio != null: ui_audio.stop()
	await frames()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(progress.storage_path))
	print("RESULT ", checks, " N1 cold reopen checks; ", failures, " failures")
	OS.delay_msec(300)
	quit(failures)

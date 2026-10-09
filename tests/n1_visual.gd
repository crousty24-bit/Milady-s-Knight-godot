extends SceneTree
var checks := 0
var failures := 0
var level: Node2D
func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, detail: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", detail)
	if not ok: failures += 1
func capture(label: String) -> void:
	if DisplayServer.get_name() == "headless": return
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://work/run017")
	root.get_texture().get_image().save_png("res://work/run017/" + label + ".png")
func tap(action: String) -> void:
	# Inject before process callbacks, including after a render capture.
	await process_frame
	Input.action_press(action)
	await process_frame
	await process_frame
	Input.action_release(action)
	await frames()
func run() -> void:
	var progress = root.get_node("Progression")
	progress.new_game()
	level = load(progress.DEFAULT_LEVEL).instantiate()
	root.add_child(level)
	current_scene = level
	await frames(3) # Let the level's deferred introduction acquire cinematic ownership.
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
	await frames(60)
	check(level.modal == "dialogue" and paused and not level.player.controls_enabled, "rendered introduction freezes gameplay at safe spawn")
	var banner: Control = level.dialogue_panel.panel
	check(banner.get_global_rect() == Rect2(8, 280, 624, 72), "dialogue banner fits the 640x360 viewport")
	check(level.dialogue_panel.body.visible_characters > 0 and level.dialogue_panel.body.visible_characters < level.dialogue_panel.body.text.length(), "text is visibly revealing")
	await capture("intro-revealing")
	await frames(85)
	await capture("intro-readable")
	# Capture the save-error branch before restoring in-memory test persistence.
	progress.persistence_enabled = true
	var original_path: String = progress.storage_path
	progress.storage_path = "res://work/run017-absent-visual-directory/save.json"
	for i in range(level.dialogue_panel.lines.size()): await tap("jump")
	check(level.modal == "dialogue" and level.dialogue_panel.hint.text == "E: Retry saving", "dialogue save error has a visible keyboard retry")
	await capture("intro-save-error")
	progress.persistence_enabled = false
	progress.storage_path = original_path
	await tap("interact")
	await frames()
	check(level.modal == "context", "first contextual tutorial appears after introduction")
	await capture("movement-tutorial")
	await tap("interact")
	for item in level.TUTORIALS: progress.complete_dialogue(item[0])
	level.player.position = Vector2(220, 144)
	level.player.velocity = Vector2.ZERO
	await frames(8)
	var terrain: TileMapLayer = level.get_node("Terrain")
	check(terrain.get_cell_source_id(Vector2i(13, 9)) != -1, "chest has authored ground support")
	var separated := true
	for coin in level.get_node("Coins").get_children():
		if coin.position.distance_to(level.tutorial_chest.position + Vector2(0, -12)) < 32: separated = false
	check(separated, "chest is separated from coin pickups")
	await tap("interact")
	var controls = root.get_node("Controls")
	check(level.modal == "context" and level.pause_menu.description.text.contains(controls.label("switch_equipment") + ": equipment") and level.pause_menu.description.text.contains(controls.label("attack") + " (hold): attack / shoot"), "chest dialog explains selecting and shooting with the active bindings")
	await capture("chest-choice")
	await tap("pause")
	level.player.position = Vector2(1968, 144)
	level.player.velocity = Vector2.ZERO
	await frames(15)
	check(level.player.health == 3.0 and not level.minor_potion.used and terrain.get_cell_source_id(Vector2i(123, 9)) != -1, "potion has support and remains at full health in its safe approach")
	separated = true
	for coin in level.get_node("Coins").get_children():
		if coin.position.distance_to(level.minor_potion.position) < 24: separated = false
	check(separated, "potion is separated from coin pickups")
	await capture("potion-approach")
	level.player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
	await frames(5)
	check(level.minor_potion.used and level.player.health == 3.0, "potion physically heals at its N1 placement")
	level.queue_free()
	await frames()
	print("RESULT ", checks, " N1 presentation checks; ", failures, " failures")
	OS.delay_msec(300)
	quit(failures)

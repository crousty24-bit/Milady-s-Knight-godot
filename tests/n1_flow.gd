extends SceneTree
const Driver = preload("res://tests/route_driver.gd")
const N1 := "res://scenes/eidolon_vale.tscn"
const FIXTURE := "res://tests/fixtures/next_level.tscn"
var checks := 0
var failures := 0
var shots := 0
var progress: Node
var save_path: String

func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(3)
	Input.action_release(action)
	await frames(4)
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func acknowledge_contexts() -> void:
	for i in range(6):
		await frames()
		if current_scene.modal != "context": return
		await tap("interact")
func menu() -> void:
	check(progress.change_level("res://scenes/game.tscn") == OK, "menu scene loads")
	await frames(8)
func new_game_from_menu() -> void:
	await menu()
	await tap("interact")
	if current_scene.scene_file_path == "res://scenes/game.tscn" and current_scene.screen == "new":
		await tap("move_down")
		await tap("interact")
	await frames(8)
func enter_spirit_dialogue() -> void:
	for i in range(240):
		if current_scene.modal != "resurrection" and not current_scene.resume_pending: break
		await frames(1)
	Input.action_press("move_right")
	for i in range(180):
		await frames(1)
		if current_scene.modal in ["spirit_appearance", "dialogue"]: break
	Input.action_release("move_right")
	for i in range(120):
		if current_scene.modal == "dialogue": break
		await frames(1)
func advance_dialogue() -> void:
	for i in range(current_scene.dialogue_panel.lines.size()): await tap("jump")
func run() -> void:
	progress = root.get_node("Progression")
	save_path = "user://run017-n1-%d.json" % OS.get_process_id()
	progress.storage_path = save_path
	progress.persistence_enabled = true
	progress.load_progress()
	await menu()
	await tap("move_down")
	await tap("interact")
	check(current_scene.screen == "controls" and current_scene.controls_menu.opened and current_scene.controls_menu.menu.description.text.contains(root.get_node("Controls").label("jump") + ": jump / next dialogue phrase"), "Controls exposes N1 Space contract through keyboard")
	await tap("pause")
	await tap("interact")
	await frames(8)
	var level = current_scene
	check(level.scene_file_path == N1 and progress.resume_scene == N1, "New Game enters The Eidolon Vale and writes its resume scene")
	check(level.modal == "resurrection" and paused and not level.player.controls_enabled, "new-game resurrection takes exclusive ownership and immobilizes gameplay")
	var spawn: Vector2 = level.player.position
	var health: float = level.player.health
	for action in ["move_right", "attack", "interact", "pause"]: Input.action_press(action)
	await frames(12)
	check(level.player.position == spawn and level.player.health == health and not level.player.dead, "spawn stays safe under movement and combat inputs during intro")
	check(level.modal == "resurrection" and not level.pause_menu.opened and not level.request_context("Overlap", "", ["Continue"]), "Escape and context cannot overlap resurrection")
	# Fixture edge probe: even an already-open gate cannot finish through an active dialogue.
	level.gate.opened = true
	level._on_exit(level.player)
	check(not level.finished and level.modal == "resurrection", "exit refuses to replace resurrection (injected open-gate probe)")
	level.gate.opened = false
	for action in ["move_right", "attack", "interact", "pause"]: Input.action_release(action)
	await enter_spirit_dialogue()
	check(level.modal == "dialogue" and level.player.position.x >= spawn.x + 32 and paused, "walking two blocks triggers Spirit appearance followed by exclusive dialogue")
	Input.action_press("jump")
	await frames(10)
	check(level.dialogue_panel.line_index == 1 and not progress.completed_dialogues.has(level.INTRO_ID), "held Next advances one phrase without saving the intro")
	Input.action_release("jump")
	await frames()
	for i in range(7): await tap("jump")
	check(level.dialogue_panel.line_index == 8 and not progress.completed_dialogues.has(level.INTRO_ID), "intro remains unsaved while its final phrase is visible")
	Input.action_press("jump")
	await frames(10)
	check(progress.completed_dialogues.has(level.INTRO_ID) and level.resume_pending and not level.player.controls_enabled, "final held Next saves intro once and blocks gameplay until release")
	Input.action_release("jump")
	await frames(8)
	check(level.modal == "context" and level.tutorial_id == "n1_movement", "first contextual explanation follows intro")
	await tap("pause")
	check(not progress.completed_dialogues.has("n1_movement") and level.modal.is_empty(), "Escape dismisses tutorial without a durable seen flag")
	level.player.die()
	await frames(220)
	level = current_scene
	check(level.scene_file_path == N1 and level.modal == "context" and not level.dialogue_panel.active and level.player.health == level.player.max_health, "death safely respawns and does not repeat saved intro")
	await tap("interact")
	check(progress.completed_dialogues.has("n1_movement"), "E acknowledges tutorial durably")
	# Fixture positioning below isolates chest and potion edge cases; route checks never teleport.
	level.player.position = level.tutorial_chest.position
	level.player.velocity = Vector2.ZERO
	await frames(8)
	await tap("interact")
	await tap("move_down")
	await tap("interact")
	check(level.tutorial_chest.consumed and not level.player.has_longbow and progress.equipment.ranged == "", "physical chest can be refused without acquiring equipment")
	await tap("pause")
	await tap("move_down")
	await tap("interact")
	await frames(10)
	level = current_scene
	check(not level.tutorial_chest.consumed and not level.dialogue_panel.active, "Restart restores refused chest and preserves seen intro")
	level.player.position = level.tutorial_chest.position
	level.player.velocity = Vector2.ZERO
	await frames(8)
	await tap("interact")
	await tap("interact")
	check(level.player.has_longbow and progress.equipment.ranged == "Longbow0", "accepting physical chest saves Longbow 0")
	level.player.projectile_fired.connect(func(_arrow: Node2D) -> void: shots += 1)
	await tap("switch_equipment")
	await tap("attack")
	check(level.player.active_slot == 1 and shots == 1, "Equipment switch selects bow and Attack fires an actual projectile")
	await tap("switch_equipment")
	level.player.position = level.minor_potion.position
	level.player.velocity = Vector2.ZERO
	await frames(8)
	await acknowledge_contexts()
	await frames(8)
	check(not level.minor_potion.used and level.player.health == level.player.max_health, "full-health player leaves physical potion available")
	level.player.health_units -= 5
	level.player.position = level.minor_potion.position
	level.player.velocity = Vector2.ZERO
	await frames(8)
	check(level.minor_potion.used and level.player.health == level.player.max_health, "physical potion heals exactly the injected 0.5 HP wound")
	await menu()
	check(progress.load_progress() == OK, "cold load reads isolated durable save")
	await tap("move_down")
	await tap("interact")
	await frames(10)
	level = current_scene
	check(level.scene_file_path == N1 and level.modal.is_empty() and level.player.has_longbow and level.tutorial_chest.consumed and progress.completed_dialogues.has("n1_movement"), "Continue retains equipment and seen flags after cold load")
	await tap("pause")
	check(level.modal == "pause" and paused, "Escape opens gameplay pause after dialogue and tutorials")
	await tap("interact")
	check(level.modal.is_empty() and not paused, "E resumes gameplay pause")
	await new_game_from_menu()
	level = current_scene
	check(level.modal == "resurrection" and progress.completed_dialogues.is_empty() and not level.player.has_longbow, "confirmed New Game resets resurrection, intro, tutorial flags and equipment")
	await enter_spirit_dialogue()
	var original := FileAccess.get_file_as_string(save_path)
	progress.storage_path = "res://work/run017/absent-%d/save.json" % OS.get_process_id()
	await advance_dialogue()
	check(level.modal == "dialogue" and level.dialogue_panel.body.text.contains("Unable to save") and not progress.completed_dialogues.has(level.INTRO_ID), "failed intro save remains paused and does not set seen flag")
	check(FileAccess.get_file_as_string(save_path) == original, "failed intro save preserves previous durable file")
	progress.storage_path = save_path
	await tap("interact")
	check(progress.completed_dialogues.has(level.INTRO_ID) and not level.dialogue_panel.active, "E retries intro saving and releases dialogue on success")
	var before_tutorial := FileAccess.get_file_as_string(save_path)
	progress.storage_path = "res://work/run017/absent-%d/save.json" % OS.get_process_id()
	await tap("interact")
	check(level.modal == "context" and level.pause_menu.heading.text == "Tutorial not saved" and not progress.completed_dialogues.has("n1_movement"), "failed tutorial acknowledgement opens exclusive retry without seen flag")
	check(FileAccess.get_file_as_string(save_path) == before_tutorial, "failed tutorial save preserves prior file")
	progress.storage_path = save_path
	await tap("interact")
	check(progress.completed_dialogues.has("n1_movement") and level.modal.is_empty(), "E retries tutorial saving and restores gameplay")
	for upper in [true, false]:
		await new_game_from_menu()
		level = current_scene
		level.next_level_scene = FIXTURE
		var driver = Driver.new(self)
		await driver.start(N1, level)
		await driver.walk(level.tutorial_chest.position.x)
		Input.action_press("interact")
		await driver.step(0)
		Input.action_release("interact")
		await driver.step(0)
		check(level.player.has_longbow, "route %s obtains chest with walking and E" % ("upper" if upper else "lower"))
		await driver.upper() if upper else await driver.lower()
		await driver.approach()
		await driver.finish()
		driver.release_inputs()
		check(not driver.failed and level.finished and level.gate.opened and driver.offering_before - driver.offering_after == 12, "route %s reaches exit and pays exactly 12 coins without teleport" % ("upper" if upper else "lower"))
		check(level.reward_settled and progress.equipment.ranged == "Longbow0" and progress.completed_dialogues.has(level.INTRO_ID), "route saves rewards, bow and intro")
		await tap("interact")
		await frames(10)
		check(current_scene.scene_file_path == FIXTURE and not paused and current_scene.player.has_longbow, "exit transitions to injected fixture with durable equipment")
	# Inject a supported v2 prototype save to exercise slice -> N1 migration, without new gameplay.
	await menu()
	var legacy: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(save_path))
	legacy.resume_scene = "res://scenes/vertical_slice.tscn"
	legacy.shards_bank = 23
	legacy.permanent_flags = {"run017_probe": true}
	legacy.completed_dialogues = {"eidolon_vale_spirit": true, "n1_movement": true}
	var legacy_file := FileAccess.open(save_path, FileAccess.WRITE)
	legacy_file.store_string(JSON.stringify(legacy))
	legacy_file.close()
	check(progress.load_progress() == OK and progress.resume_scene == N1, "v2 prototype slice resume resolves to N1")
	await tap("move_down")
	await tap("interact")
	await frames(10)
	check(current_scene.scene_file_path == N1 and current_scene.player.has_longbow and progress.banked_shards == 23 and progress.permanent_flags.has("run017_probe") and progress.completed_dialogues.has("eidolon_vale_spirit"), "legacy Continue preserves shards, bow and permanent/dialogue flags")
	# Remove only this driver's exact save basename and its generated backups.
	var save_dir := DirAccess.open(save_path.get_base_dir())
	for filename in save_dir.get_files():
		var base := save_path.get_file()
		if filename == base or filename == base + ".tmp" or filename == base + ".bak" or filename.begins_with(base + ".bak."):
			save_dir.remove(filename)
	current_scene.queue_free()
	var ui_audio := root.get_node_or_null("UiSfx") as AudioStreamPlayer
	if ui_audio != null: ui_audio.stop()
	paused = false
	await frames()
	# Fixed-FPS headless simulation outruns the real-time audio mixer; let stopped playbacks drain.
	OS.delay_msec(300)
	print("RESULT %d N1 flow checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

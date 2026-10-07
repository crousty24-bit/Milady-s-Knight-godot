# Real mapped events, isolated settings and production menu/modal integration.
extends SceneTree
var checks := 0
var failures := 0
var controls: Node
var room: Node2D
var player: SlicePlayer
var shots: Array[Node2D] = []
var shot_frames: Array[int] = []
var changed := 0
var test_path: String

func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func key_event(physical: int, logical: int = 0) -> InputEventKey:
	var event := InputEventKey.new()
	event.physical_keycode = physical
	event.keycode = logical if logical != 0 else physical
	if physical == KEY_SHIFT: event.location = KEY_LOCATION_LEFT
	return event
func key(physical: int, pressed: bool, logical: int = 0) -> void:
	var event := key_event(physical, logical)
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()
func mouse_event(button: int) -> InputEventMouseButton:
	var event := InputEventMouseButton.new()
	event.button_index = button
	return event
func mouse(button: int, pressed: bool, position := Vector2(600, 30)) -> void:
	var event := mouse_event(button)
	event.pressed = pressed
	event.position = position
	event.global_position = position
	Input.parse_input_event(event)
	Input.flush_buffered_events()
func tap(code: int) -> void:
	key(code, true)
	await frames(2)
	key(code, false)
	await frames(2)
func release_all() -> void:
	for code in [KEY_A, KEY_Q, KEY_D, KEY_W, KEY_S, KEY_SPACE, KEY_E, KEY_F, KEY_T, KEY_ESCAPE, KEY_ENTER, KEY_DOWN]: key(code, false)
	for button in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_MIDDLE]: mouse(button, false)
	for action in controls.ACTIONS: Input.action_release(action)
func bindings_snapshot() -> Dictionary:
	var snapshot := {}
	for action in controls.ACTIONS:
		var values := []
		for event in InputMap.action_get_events(action):
			values.append(event.as_text())
		snapshot[action] = values
	return snapshot
func destroy_scene() -> void:
	if is_instance_valid(current_scene):
		# Drain live audio before fixture destruction under --fixed-fps 60.
		for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for emitter in root.find_children("*", audio_type, true, false): emitter.stop()
		OS.delay_msec(300)
		current_scene.queue_free()
		await frames(3)
	current_scene = null
func spawn_player() -> void:
	release_all()
	await destroy_scene()
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	var floor_body := StaticBody2D.new()
	floor_body.position = Vector2(400, 208)
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = Vector2(1800, 16)
	floor_body.add_child(shape)
	room.add_child(floor_body)
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(160, 200)
	room.add_child(player)
	shots.clear()
	shot_frames.clear()
	player.projectile_fired.connect(func(arrow: Node2D): shots.append(arrow); shot_frames.append(Engine.get_physics_frames()))
	await frames(5)

func presets_and_remapping() -> void:
	check(controls.set_profile("azerty") == OK, "AZERTY preset accepted")
	var azerty := bindings_snapshot()
	check(controls.label("move_left").contains("Q") and controls.label("move_up").contains("Z"), "AZERTY displays Q/Z for physical movement positions")
	check(controls.set_profile("qwerty") == OK, "QWERTY preset accepted")
	check(bindings_snapshot() == azerty, "AZERTY and QWERTY use identical physical positions")
	check(controls.label("move_left").contains("A") and controls.label("move_up").contains("W"), "QWERTY displays A/W")
	key(KEY_A, true)
	await frames(1)
	check(Input.is_action_pressed("move_left") and not Input.is_action_pressed("switch_equipment"), "QWERTY A only moves left")
	key(KEY_A, false)
	check(controls.set_profile("classic") == OK, "classic preset accepted")
	key(KEY_A, true)
	key(KEY_F, true)
	await frames(1)
	check(Input.is_action_pressed("switch_equipment") and Input.is_action_pressed("attack") and not Input.is_action_pressed("move_left"), "classic A/F retain exclusive equipment/attack bindings")
	release_all()
	controls.set_profile("azerty")
	var before := bindings_snapshot()
	var before_changed := changed
	check(controls.rebind("jump", key_event(KEY_E)) != OK, "conflicting E binding refused")
	check(bindings_snapshot() == before and changed == before_changed, "conflict changes neither InputMap nor bindings signal")
	check(controls.rebind("attack", mouse_event(MOUSE_BUTTON_MIDDLE)) == OK, "attack can be remapped to middle mouse")
	check(controls.profile == "custom", "remapping selects custom profile")
	mouse(MOUSE_BUTTON_LEFT, true)
	await frames(1)
	check(not Input.is_action_pressed("attack"), "removed attack mouse binding no longer triggers")
	mouse(MOUSE_BUTTON_LEFT, false)
	mouse(MOUSE_BUTTON_MIDDLE, true)
	await frames(1)
	check(Input.is_action_pressed("attack"), "remapped middle mouse triggers attack")
	mouse(MOUSE_BUTTON_MIDDLE, false)
	check(controls.rebind("jump", key_event(KEY_T)) == OK, "jump can be remapped to a physical key")
	var customized := bindings_snapshot()
	controls.set_profile("classic")
	controls.set_profile("custom")
	check(bindings_snapshot() == customized, "custom bindings survive a temporary preset change")
	key(KEY_T, true)
	await frames(1)
	check(Input.is_action_pressed("jump"), "remapped physical T triggers jump")
	release_all()
	check(controls.rebind("attack", mouse_event(MOUSE_BUTTON_WHEEL_UP)) == ERR_INVALID_PARAMETER, "wheel cannot bind a held attack")
	check(controls.rebind("jump", mouse_event(MOUSE_BUTTON_WHEEL_UP)) == ERR_INVALID_PARAMETER, "wheel cannot bind variable-height jump")
	check(controls.rebind("switch_equipment", mouse_event(MOUSE_BUTTON_WHEEL_UP)) == OK, "wheel can bind equipment switching")
	mouse(MOUSE_BUTTON_WHEEL_UP, true)
	await frames(1)
	check(Input.is_action_just_pressed("switch_equipment") or Input.is_action_pressed("switch_equipment"), "wheel pulse triggers mapped equipment action")
	mouse(MOUSE_BUTTON_WHEEL_UP, false)
	await frames(1)
	check(not controls.menu_inputs_held(), "wheel release cannot leave modal resume blocked")
	check(changed > 0, "successful binding changes emit bindings_changed")

func persistence() -> void:
	controls.storage_path = test_path
	controls.persistence_enabled = true
	check(controls.save_settings() == OK, "custom settings saved to isolated path")
	var customized := bindings_snapshot()
	controls.persistence_enabled = false
	controls.set_profile("classic")
	controls.persistence_enabled = true
	check(controls.load_settings() == OK and controls.profile == "custom", "saved custom profile loaded")
	check(bindings_snapshot() == customized, "loaded physical and mouse bindings match saved values")
	var file := FileAccess.open(test_path, FileAccess.WRITE)
	file.store_string("{ invalid json")
	file.close()
	check(controls.load_settings() != OK and controls.storage_error != OK, "corrupt controls file reports a storage error")
	check(bindings_snapshot() == customized and controls.profile == "custom", "corrupt file preserves active in-memory controls")
	controls.storage_path = "user://missing-controls-dir-%d/settings.json" % OS.get_process_id()
	check(controls.save_settings() != OK, "unwritable missing-directory path reports save failure")
	check(bindings_snapshot() == customized, "failed save preserves current bindings")
	check(controls.set_profile("classic") != OK and controls.profile == "custom" and bindings_snapshot() == customized, "failed preset save rolls back profile and live bindings")
	check(controls.rebind("jump", key_event(KEY_Y)) != OK and bindings_snapshot() == customized, "failed remap save preserves previous live binding")
	controls.persistence_enabled = false
	controls.storage_path = test_path
	DirAccess.remove_absolute(test_path)

func gameplay() -> void:
	for profile in ["azerty", "qwerty"]:
		controls.set_profile(profile)
		await spawn_player()
		var start := player.position.x
		key(KEY_D, true)
		key(KEY_SPACE, true)
		mouse(MOUSE_BUTTON_LEFT, true)
		await frames(4)
		check(player.position.x > start and player.velocity.y < 0 and player.attack_time > 0, "%s moves, jumps and attacks simultaneously" % profile)
		key(KEY_D, false)
		key(KEY_SPACE, false)
		await frames(60)
		check(player.attack_cooldown > 0.85, "%s held left click repeats melee attack after its cooldown" % profile)
		mouse(MOUSE_BUTTON_LEFT, false)
		await frames(65)
		check(player.attack_time == 0 and player.attack_cooldown == 0, "%s releasing left click stops melee repetition" % profile)
		# Logical AZERTY Q differs from physical A; event still moves left.
		start = player.position.x
		key(KEY_A, true, KEY_Q if profile == "azerty" else KEY_A)
		await frames(8)
		key(KEY_A, false, KEY_Q if profile == "azerty" else KEY_A)
		check(player.position.x < start and player.facing == -1, "%s uses physical left key independently of printed letter" % profile)
		player.configure_equipment(true)
		await tap(KEY_Q)
		check(player.active_slot == 1, "%s physical Q selects owned ranged weapon" % profile)
		mouse(MOUSE_BUTTON_LEFT, true, Vector2(600, 20))
		await frames(2)
		check(shots.size() == 1 and shots[0].direction == -1, "%s cursor on right does not redirect a left-facing shot" % profile)
		var interval_frames := roundi(WeaponCatalog.stats(player.equipment.ranged).interval * 60.0)
		await frames(interval_frames)
		check(shots.size() == 2 and shot_frames[1] - shot_frames[0] == interval_frames, "%s held left click repeats Longbow at production cadence" % profile)
		mouse(MOUSE_BUTTON_LEFT, false)
		mouse(MOUSE_BUTTON_RIGHT, true)
		key(KEY_SHIFT, true)
		await frames(1)
		check(Input.is_action_pressed("special_attack") and Input.is_action_pressed("landing_attack"), "%s right click and Shift map planned combat actions" % profile)
		mouse(MOUSE_BUTTON_RIGHT, false)
		key(KEY_SHIFT, false)
	await destroy_scene()

func click_row(menu: CanvasLayer, index: int, held: bool = false) -> void:
	await frames(3)
	var row: Control = menu.rows.get_child(index)
	var position := root.get_final_transform() * row.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = position
	motion.global_position = position
	Input.parse_input_event(motion)
	await frames(1)
	mouse(MOUSE_BUTTON_LEFT, true, position)
	await frames(2)
	if not held:
		mouse(MOUSE_BUTTON_LEFT, false, position)
		await frames(2)

func capture(label: String) -> void:
	if DisplayServer.get_name() == "headless": return
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://work/controls")
	root.get_texture().get_image().save_png("res://work/controls/" + label + ".png")
	await process_frame

func menus_and_modals() -> void:
	controls.set_profile("qwerty")
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.has_save = false
	progress.legacy_pending = false
	progress.storage_error = OK
	var game = load("res://scenes/game.tscn").instantiate()
	root.add_child(game)
	current_scene = game
	await frames(5)
	await tap(KEY_DOWN)
	await tap(KEY_ENTER)
	check(game.screen == "controls" and game.controls_menu.opened, "keyboard opens interactive Controls from main menu")
	var ui = game.controls_menu
	await capture("home")
	await click_row(ui.menu, 0)
	check(ui.page == "profiles", "mouse opens profile selection")
	await capture("profiles")
	await click_row(ui.menu, 0)
	check(controls.profile == "azerty" and ui.page == "home", "mouse selects AZERTY preset")
	await tap(KEY_DOWN)
	await tap(KEY_ENTER)
	check(ui.page == "bindings", "keyboard enters binding editor")
	await capture("bindings-page1")
	await click_row(ui.menu, 4)
	check(ui.capture_action == "jump", "click enters jump key capture")
	await capture("capture-jump")
	await tap(KEY_T)
	check(ui.capture_action.is_empty() and controls.profile == "custom" and controls.label("jump").contains("T"), "key capture assigns physical T and refreshes binding label")
	await click_row(ui.menu, 5)
	check(ui.capture_action == "attack", "click enters mouse attack capture")
	mouse(MOUSE_BUTTON_MIDDLE, true)
	await frames(2)
	mouse(MOUSE_BUTTON_MIDDLE, false)
	await frames(2)
	check(ui.capture_action.is_empty() and controls.label("attack") == "Middle click", "mouse capture assigns middle button")
	await click_row(ui.menu, 6)
	check(ui.binding_page == 1, "binding editor opens second page")
	await capture("bindings-page2")
	await click_row(ui.menu, 5)
	await click_row(ui.menu, 4)
	var before_cancel := bindings_snapshot()
	await tap(KEY_E)
	check(ui.capture_action == "jump" and ui.menu.description.text.to_lower().contains("already assigned"), "capture reports conflict and stays open (%s: %s)" % [ui.capture_action, ui.menu.description.text.replace("\n", " ")])
	check(bindings_snapshot() == before_cancel, "capture conflict preserves previous settings")
	await tap(KEY_ESCAPE)
	check(ui.capture_action.is_empty() and ui.page == "bindings" and bindings_snapshot() == before_cancel, "Escape cancels capture without changing controls")
	await tap(KEY_ESCAPE)
	await click_row(ui.menu, 2)
	check(controls.profile == "azerty" and controls.label("attack") == "Left click" and controls.label("jump") == "Space", "UI restores defaults of custom profile's AZERTY base")
	await tap(KEY_ESCAPE)
	check(game.screen == "main" and not ui.opened, "Escape returns through Controls pages to main menu")
	controls.set_profile("qwerty")
	progress.resume_scene = "res://scenes/vertical_slice.tscn"
	progress.has_save = true
	game._main()
	await click_row(game.menu, 1, true)
	await frames(8)
	var continued = current_scene
	check(continued.scene_file_path == progress.resume_scene and continued.resume_pending and continued.player.attack_time == 0, "held Continue click cannot attack across scene change")
	mouse(MOUSE_BUTTON_LEFT, false)
	await frames(4)
	check(not continued.resume_pending and continued.player.controls_enabled, "Continue click release enables fresh gameplay")
	await destroy_scene()
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	await frames(10)
	await tap(KEY_ESCAPE)
	check(paused and level.modal == "pause" and level.pause_menu.description.text.contains(controls.label("interact")), "pause shows current mapped confirm hint")
	await click_row(level.pause_menu, 3)
	check(paused and level.controls_menu.opened, "pause Controls entry opens while gameplay stays paused")
	await tap(KEY_ESCAPE)
	check(paused and level.pause_menu.opened, "closing pause Controls restores pause menu")
	await click_row(level.pause_menu, 0, true)
	await frames(65)
	check(not paused and level.resume_pending and not level.player.controls_enabled and level.player.attack_time == 0, "held Resume click cannot attack or unlock gameplay")
	mouse(MOUSE_BUTTON_LEFT, false)
	await frames(4)
	check(not level.resume_pending and level.player.controls_enabled and level.player.attack_time == 0, "Resume release unlocks gameplay without delayed attack")
	mouse(MOUSE_BUTTON_LEFT, true)
	await frames(2)
	check(level.player.attack_time > 0, "fresh gameplay click attacks after modal release")
	mouse(MOUSE_BUTTON_LEFT, false)
	await frames(65)
	var choices := []
	check(level.request_context("Reward", "Choose", ["Accept"], func(index: int): choices.append(index)), "context fixture opens production modal")
	await click_row(level.pause_menu, 0, true)
	await frames(65)
	check(choices == [0] and level.resume_pending and level.player.attack_time == 0, "held reward confirm click is consumed until release")
	mouse(MOUSE_BUTTON_LEFT, false)
	await frames(4)
	check(not level.resume_pending and level.player.attack_time == 0, "reward release resumes without attack")
	check(controls.rebind("pause", key_event(KEY_P)) == OK, "pause can be remapped to physical P")
	check(level.hud.get_node("PauseHint").text == "P", "HUD pause hint updates when bindings change")
	await tap(KEY_P)
	check(paused and level.pause_menu.opened, "remapped P opens pause")
	key(KEY_ENTER, true)
	await frames(3)
	check(not paused and level.resume_pending and not level.player.controls_enabled, "held fallback Enter cannot unlock gameplay on Resume")
	key(KEY_ENTER, false)
	await frames(3)
	check(not level.resume_pending and level.player.controls_enabled, "fallback Enter release restores gameplay")
	controls.rebind("interact", key_event(KEY_Y))
	controls.rebind("jump", key_event(KEY_T))
	level.player.position = Vector2(2040, 144)
	level.player.velocity = Vector2.ZERO
	level.gold = 12
	await frames(5)
	check(level.gate.player_near() and level.hud.get_node("Prompt/CapLabel").text == "Y", "production gate prompt displays remapped interaction key")
	await capture("custom-gate-hint")
	var dialogue = load("res://scripts/dialogue_panel.gd").new()
	level.add_child(dialogue)
	dialogue.show_dialogue("The Ancient Spirit", ["Controls follow your chosen bindings."])
	await frames(3)
	check(dialogue.hint.text == "T: Next", "dialogue Next hint displays remapped jump key")
	await capture("custom-dialogue-hint")
	dialogue.close()
	await destroy_scene()

func run() -> void:
	controls = root.get_node("Controls")
	controls.persistence_enabled = false
	test_path = "user://controls-test-%d.json" % OS.get_process_id()
	controls.bindings_changed.connect(func(): changed += 1)
	await presets_and_remapping()
	persistence()
	await gameplay()
	await menus_and_modals()
	release_all()
	print("RESULT ", checks, " controls checks; ", failures, " failures")
	quit(failures)

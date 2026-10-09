# Run in two fresh engine processes with the same isolated user profile:
# -- prepare, then -- reopen. Never reads or writes the user's controls.json.
extends SceneTree
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func frames() -> void:
	for i in 3:
		await physics_frame
		await process_frame

func run() -> void:
	var controls = root.get_node("Controls")
	check(not controls.persistence_enabled, "script-mode boot does not read production control settings")
	controls.storage_path = "user://controls-cold-session.json"
	controls.persistence_enabled = true
	if "prepare" in OS.get_cmdline_user_args():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(controls.storage_path))
		check(controls.set_profile("azerty") == OK, "prepare saves AZERTY profile")
		var key := InputEventKey.new()
		key.physical_keycode = KEY_T
		check(controls.rebind("jump", key) == OK, "prepare saves custom physical jump")
		var mouse := InputEventMouseButton.new()
		mouse.button_index = MOUSE_BUTTON_MIDDLE
		check(controls.rebind("attack", mouse) == OK, "prepare saves custom mouse attack")
		check(controls.set_profile("qwerty") == OK, "prepare switches preset while preserving custom settings")
	else:
		check(controls.load_settings() == OK and controls.profile == "qwerty", "fresh engine reads saved current profile")
		check(controls.set_profile("custom") == OK and controls.custom_layout == "azerty", "fresh engine restores custom profile with AZERTY labels")
		var event := InputEventKey.new()
		event.physical_keycode = KEY_T
		event.keycode = KEY_T
		event.pressed = true
		Input.parse_input_event(event)
		await frames()
		check(Input.is_action_pressed("jump") and controls.label("jump") == "T", "cold custom physical key triggers jump")
		event = event.duplicate()
		event.pressed = false
		Input.parse_input_event(event)
		var mouse := InputEventMouseButton.new()
		mouse.button_index = MOUSE_BUTTON_MIDDLE
		mouse.pressed = true
		Input.parse_input_event(mouse)
		await frames()
		check(Input.is_action_pressed("attack") and controls.label("attack") == "Middle click", "cold custom mouse event triggers attack")
		mouse = mouse.duplicate()
		mouse.pressed = false
		Input.parse_input_event(mouse)
		DirAccess.remove_absolute(ProjectSettings.globalize_path(controls.storage_path))
	print("RESULT ", checks, " controls cold-session checks; ", failures, " failures")
	quit(failures)

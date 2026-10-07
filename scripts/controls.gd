extends Node
## Input profiles live separately from progression and never alter gameplay rules.
signal bindings_changed

const ACTIONS = ["move_left", "move_right", "move_up", "move_down", "jump", "attack", "interact", "switch_equipment", "special_attack", "landing_attack", "pause"]
const ACTION_LABELS = {
	"move_left": "Move left", "move_right": "Move right", "move_up": "Move up",
	"move_down": "Move down", "jump": "Jump", "attack": "Attack",
	"interact": "Interact", "switch_equipment": "Switch equipment",
	"special_attack": "Special attack", "landing_attack": "Landing attack", "pause": "Pause / back",
}
const PROFILES = ["qwerty", "azerty", "classic", "custom"]
const CLASSIC_KEYS = {
	"move_left": KEY_LEFT, "move_right": KEY_RIGHT, "move_up": KEY_UP,
	"move_down": KEY_DOWN, "jump": KEY_SPACE, "attack": KEY_F,
	"interact": KEY_E, "switch_equipment": KEY_A, "special_attack": KEY_R,
	"landing_attack": KEY_G, "pause": KEY_ESCAPE,
}
const PHYSICAL_KEYS = {
	"move_left": KEY_A, "move_right": KEY_D, "move_up": KEY_W,
	"move_down": KEY_S, "jump": KEY_SPACE, "interact": KEY_E,
	"switch_equipment": KEY_Q, "landing_attack": KEY_SHIFT, "pause": KEY_ESCAPE,
}
const ARROW_KEYS = {"move_left": KEY_LEFT, "move_right": KEY_RIGHT, "move_up": KEY_UP, "move_down": KEY_DOWN}

var profile: String = "qwerty"
var custom_layout: String = "qwerty"
var persistence_enabled: bool = true
var storage_path: String = "user://controls.json"
var storage_error: Error = OK
var _bindings: Dictionary = {}
var _custom_bindings: Dictionary = {}

func _ready() -> void:
	persistence_enabled = not OS.get_cmdline_args().has("--script")
	profile = _default_profile()
	custom_layout = profile
	_bindings = _preset(profile)
	if persistence_enabled:
		load_settings()
	_apply_bindings()

func _default_profile() -> String:
	if DisplayServer.get_name() == "headless": return "qwerty"
	return "azerty" if DisplayServer.keyboard_get_keycode_from_physical(KEY_W) == KEY_Z else "qwerty"

func _key(code: int, physical: bool = false, location: int = KEY_LOCATION_UNSPECIFIED) -> InputEventKey:
	var event := InputEventKey.new()
	if physical:
		event.physical_keycode = code
	else:
		event.keycode = code
	event.location = location
	return event

func _mouse(button: int) -> InputEventMouseButton:
	var event := InputEventMouseButton.new()
	event.button_index = button
	return event

func _preset(id: String) -> Dictionary:
	var result: Dictionary = {}
	for action in ACTIONS:
		if id == "classic":
			result[action] = [_key(CLASSIC_KEYS[action])]
		elif action == "attack":
			result[action] = [_mouse(MOUSE_BUTTON_LEFT)]
		elif action == "special_attack":
			result[action] = [_mouse(MOUSE_BUTTON_RIGHT)]
		else:
			var location := KEY_LOCATION_LEFT if action == "landing_attack" else KEY_LOCATION_UNSPECIFIED
			result[action] = [_key(PHYSICAL_KEYS[action], true, location)]
			if ARROW_KEYS.has(action):
				result[action].append(_key(ARROW_KEYS[action]))
	return result

func _apply_bindings() -> void:
	for action in ACTIONS:
		if not InputMap.has_action(action):
			InputMap.add_action(action, 0.2)
		Input.action_release(action)
		InputMap.action_erase_events(action)
		for event in _bindings[action]:
			InputMap.action_add_event(action, event)
	bindings_changed.emit()

func set_profile(id: String) -> Error:
	if id not in PROFILES:
		return ERR_INVALID_PARAMETER
	var next_custom := _custom_bindings.duplicate(true)
	var next_layout := custom_layout
	var next_bindings: Dictionary
	if id == "custom":
		if next_custom.is_empty():
			next_custom = _bindings.duplicate(true)
			next_layout = profile
		next_bindings = next_custom.duplicate(true)
	else:
		next_bindings = _preset(id)
	return _commit(id, next_layout, next_bindings, next_custom)

func rebind(action: String, event: InputEvent) -> Error:
	if action not in ACTIONS:
		return ERR_INVALID_PARAMETER
	var normalized := _normalize(event)
	if normalized == null or not _allowed(action, normalized):
		return ERR_INVALID_PARAMETER
	for other in ACTIONS:
		if other == action:
			continue
		for existing in _bindings[other]:
			if _conflicts(normalized, existing):
				return ERR_ALREADY_EXISTS
	var next_bindings := _bindings.duplicate(true)
	next_bindings[action] = [normalized]
	var next_layout := custom_layout if profile == "custom" else profile
	return _commit("custom", next_layout, next_bindings, next_bindings.duplicate(true))

func reset_defaults() -> Error:
	var id := custom_layout if profile == "custom" else profile
	return _commit(id, id, _preset(id), {})

func menu_inputs_held() -> bool:
	# Raw state survives action_release(), which menus use before scene changes.
	for code in [KEY_ENTER, KEY_KP_ENTER, KEY_ESCAPE]:
		if Input.is_key_pressed(code) or Input.is_physical_key_pressed(code):
			return true
	if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) or Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		return true
	for action in ["interact", "attack", "jump", "pause", "switch_equipment", "landing_attack", "special_attack"]:
		if Input.is_action_pressed(action):
			return true
		for event in _bindings.get(action, []):
			if event is InputEventKey:
				if event.physical_keycode != 0 and Input.is_physical_key_pressed(event.physical_keycode):
					return true
				if event.keycode != 0 and Input.is_key_pressed(event.keycode):
					return true
			elif event is InputEventMouseButton and Input.is_mouse_button_pressed(event.button_index):
				return true
	return false

func _commit(id: String, layout: String, bindings: Dictionary, custom: Dictionary) -> Error:
	var old_profile := profile
	var old_layout := custom_layout
	var old_bindings := _bindings
	var old_custom := _custom_bindings
	profile = id
	custom_layout = layout
	_bindings = bindings
	_custom_bindings = custom
	var error := save_settings()
	if error != OK:
		profile = old_profile
		custom_layout = old_layout
		_bindings = old_bindings
		_custom_bindings = old_custom
		return error
	_apply_bindings()
	return OK

func _normalize(event: InputEvent) -> InputEvent:
	if event is InputEventKey:
		if event.echo or event.alt_pressed or event.ctrl_pressed or event.meta_pressed:
			return null
		# Shift itself is a binding; Shift plus another key is not a chord.
		var code: int = event.physical_keycode if event.physical_keycode != 0 else event.keycode
		if code <= 0 or code >= KEY_UNKNOWN or OS.get_keycode_string(code).is_empty() or (event.shift_pressed and code != KEY_SHIFT):
			return null
		return _key(code, true, event.location)
	if event is InputEventMouseButton:
		if event.alt_pressed or event.ctrl_pressed or event.meta_pressed or event.shift_pressed:
			return null
		if event.button_index < MOUSE_BUTTON_LEFT or event.button_index > MOUSE_BUTTON_XBUTTON2:
			return null
		return _mouse(event.button_index)
	return null

func _allowed(action: String, event: InputEvent) -> bool:
	if event is InputEventMouseButton and event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN, MOUSE_BUTTON_WHEEL_LEFT, MOUSE_BUTTON_WHEEL_RIGHT]:
		return action in ["interact", "switch_equipment", "landing_attack", "pause"]
	return true

func _conflicts(first: InputEvent, second: InputEvent) -> bool:
	if first is InputEventMouseButton and second is InputEventMouseButton:
		return first.button_index == second.button_index
	if not first is InputEventKey or not second is InputEventKey:
		return false
	if first.location != KEY_LOCATION_UNSPECIFIED and second.location != KEY_LOCATION_UNSPECIFIED and first.location != second.location:
		return false
	if first.physical_keycode != 0 and second.physical_keycode != 0:
		return first.physical_keycode == second.physical_keycode
	var first_code: int = first.keycode if first.keycode != 0 else _logical_key(first.physical_keycode)
	var second_code: int = second.keycode if second.keycode != 0 else _logical_key(second.physical_keycode)
	return first_code == second_code

func _logical_key(code: int) -> int:
	var layout := custom_layout if profile == "custom" else profile
	if DisplayServer.get_name() != "headless" and _default_profile() == layout:
		var native_code := DisplayServer.keyboard_get_keycode_from_physical(code)
		if native_code != 0: return native_code
	if layout == "azerty":
		match code:
			KEY_W: return KEY_Z
			KEY_A: return KEY_Q
			KEY_Q: return KEY_A
			KEY_Z: return KEY_W
	if layout == "qwerty":
		return code
	if DisplayServer.get_name() == "headless": return code
	var mapped := DisplayServer.keyboard_get_keycode_from_physical(code)
	return mapped if mapped != 0 else code

func label(action: String) -> String:
	if not _bindings.has(action) or _bindings[action].is_empty():
		return "—"
	var event: InputEvent = _bindings[action][0]
	if event is InputEventMouseButton:
		match event.button_index:
			MOUSE_BUTTON_LEFT: return "Left click"
			MOUSE_BUTTON_RIGHT: return "Right click"
			MOUSE_BUTTON_MIDDLE: return "Middle click"
			MOUSE_BUTTON_WHEEL_UP: return "Wheel up"
			MOUSE_BUTTON_WHEEL_DOWN: return "Wheel down"
			MOUSE_BUTTON_WHEEL_LEFT: return "Wheel left"
			MOUSE_BUTTON_WHEEL_RIGHT: return "Wheel right"
			MOUSE_BUTTON_XBUTTON1: return "Mouse 4"
			MOUSE_BUTTON_XBUTTON2: return "Mouse 5"
	var code: int = event.keycode if event.keycode != 0 else _logical_key(event.physical_keycode)
	if code == KEY_SHIFT and event.location == KEY_LOCATION_LEFT:
		return "Left Shift"
	return OS.get_keycode_string(code)

func menu_hint(horizontal: bool = false) -> String:
	var directions := "%s / %s" % [label("move_left"), label("move_right")] if horizontal else "%s / %s" % [label("move_up"), label("move_down")]
	return "%s: select · %s: confirm · %s: back" % [directions, label("interact"), label("pause")]

func _encode_bindings(bindings: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for action in bindings:
		result[action] = []
		for event in bindings[action]:
			if event is InputEventKey:
				result[action].append({"kind": "physical" if event.physical_keycode != 0 else "key", "code": event.physical_keycode if event.physical_keycode != 0 else event.keycode, "location": event.location})
			else:
				result[action].append({"kind": "mouse", "code": event.button_index})
	return result

func _integer(value: Variant, minimum: int, maximum: int) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and value == floorf(float(value)) and value >= minimum and value <= maximum

func _decode_bindings(raw: Variant) -> Variant:
	if not raw is Dictionary or raw.size() != ACTIONS.size():
		return null
	var result: Dictionary = {}
	for action in ACTIONS:
		var entries = raw.get(action)
		if not entries is Array or entries.is_empty() or entries.size() > 2:
			return null
		result[action] = []
		for entry in entries:
			if not entry is Dictionary or not entry.get("kind") is String:
				return null
			var event: InputEvent
			if entry.kind == "mouse":
				if entry.size() != 2 or not _integer(entry.get("code"), MOUSE_BUTTON_LEFT, MOUSE_BUTTON_XBUTTON2):
					return null
				event = _mouse(int(entry.code))
			elif entry.kind in ["physical", "key"]:
				if entry.size() != 3 or not _integer(entry.get("code"), 1, KEY_UNKNOWN - 1) or not _integer(entry.get("location"), KEY_LOCATION_UNSPECIFIED, KEY_LOCATION_RIGHT):
					return null
				# Unknown codes are not usable bindings, even if numerically in range.
				if OS.get_keycode_string(int(entry.code)).is_empty():
					return null
				event = _key(int(entry.code), entry.kind == "physical", int(entry.location))
			else:
				return null
			if not _allowed(action, event):
				return null
			result[action].append(event)
	var seen: Array = []
	for action in ACTIONS:
		for event in result[action]:
			for previous in seen:
				if _conflicts(event, previous):
					return null
			seen.append(event)
	return result

func load_settings() -> Error:
	storage_error = _read_settings()
	return storage_error

func _read_settings() -> Error:
	if not persistence_enabled or not FileAccess.file_exists(storage_path):
		return OK
	var file := FileAccess.open(storage_path, FileAccess.READ)
	if file == null:
		return FileAccess.get_open_error()
	var parser := JSON.new()
	if parser.parse(file.get_as_text()) != OK or not parser.data is Dictionary:
		return ERR_FILE_CORRUPT
	var data: Dictionary = parser.data
	if data.get("version") != 1:
		return ERR_FILE_UNRECOGNIZED
	if data.size() != 4 or not data.get("profile") is String or data.profile not in PROFILES or not data.get("custom_layout") is String or data.custom_layout not in ["qwerty", "azerty", "classic"] or not data.get("custom_bindings") is Dictionary:
		return ERR_FILE_CORRUPT
	var custom: Dictionary = {}
	# Validate using the saved layout, then restore it until all data passes.
	var previous_profile := profile
	var previous_layout := custom_layout
	profile = "custom"
	custom_layout = data.custom_layout
	if not data.custom_bindings.is_empty():
		var decoded = _decode_bindings(data.custom_bindings)
		if decoded == null:
			profile = previous_profile
			custom_layout = previous_layout
			return ERR_FILE_CORRUPT
		custom = decoded
	profile = previous_profile
	custom_layout = previous_layout
	if data.profile == "custom" and custom.is_empty():
		return ERR_FILE_CORRUPT
	profile = data.profile
	custom_layout = data.custom_layout
	_custom_bindings = custom
	_bindings = custom.duplicate(true) if profile == "custom" else _preset(profile)
	_apply_bindings()
	return OK

func save_settings() -> Error:
	if not persistence_enabled:
		storage_error = OK
		return OK
	var temporary := storage_path + ".tmp"
	var file := FileAccess.open(temporary, FileAccess.WRITE)
	if file == null:
		storage_error = FileAccess.get_open_error()
		return storage_error
	file.store_string(JSON.stringify({"version": 1, "profile": profile, "custom_layout": custom_layout, "custom_bindings": _encode_bindings(_custom_bindings)}))
	file.flush()
	storage_error = file.get_error()
	file.close()
	if storage_error == OK:
		storage_error = DirAccess.rename_absolute(ProjectSettings.globalize_path(temporary), ProjectSettings.globalize_path(storage_path))
	if storage_error != OK and FileAccess.file_exists(temporary):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(temporary))
	return storage_error

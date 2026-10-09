extends CanvasLayer
@onready var controls = get_node("/root/Controls")
# Reuses the established panel, typography and UI feedback; all pages fit 640 x 360.
signal closed
const MENU = preload("res://scripts/keyboard_menu.gd")
const PROFILES := ["azerty", "qwerty", "classic", "custom"]
const PROFILE_NAMES := ["Keyboard + mouse AZERTY", "Keyboard + mouse QWERTY", "Classic keyboard", "Custom"]
var menu: CanvasLayer
var opened: bool = false
var page: String = "home"
var binding_page: int = 0
var capture_action: String = ""
var message: String = ""
var _capture_frame: int = -1

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 31
	menu = MENU.new()
	add_child(menu)
	menu.selected.connect(_select)
	menu.cancelled.connect(_back)

func open() -> void:
	opened = true
	capture_action = ""
	message = ""
	page = "home"
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_show()

func close() -> void:
	if not opened: return
	opened = false
	capture_action = ""
	menu.set_process(true)
	menu.set_process_input(true)
	menu.close()
	for action in controls.ACTIONS: Input.action_release(action)
	closed.emit()

func _show() -> void:
	menu.set_process(true)
	menu.set_process_input(true)
	var detail := message
	if controls.storage_error != OK:
		detail = "Controls settings unreadable or not saved. Check storage."
	match page:
		"home":
			if detail.is_empty():
				detail = "Profile: " + PROFILE_NAMES[PROFILES.find(controls.profile)] + "\n" + controls.menu_hint()
				detail += "\n" + controls.label("jump") + ": jump / next dialogue phrase"
				detail += "\n" + controls.label("attack") + " (hold): attack / shoot"
			menu.show_menu("Controls", detail, ["Choose profile", "Change bindings", "Restore profile defaults", "Back"])
		"profiles":
			menu.show_menu("Control profile", detail, PROFILE_NAMES + ["Back"])
		"bindings":
			var options: Array[String] = []
			var start := binding_page * 6
			for i in range(start, mini(start + 6, controls.ACTIONS.size())):
				var action: String = controls.ACTIONS[i]
				var suffix := " (planned)" if action in ["special_attack", "landing_attack"] else ""
				options.append(controls.ACTION_LABELS[action] + suffix + ": " + controls.label(action))
			options.append("Next page" if binding_page == 0 else "Previous page")
			options.append("Back")
			menu.show_menu("Bindings %d / 2" % (binding_page + 1), detail, options)
		"pause_binding":
			menu.show_menu("Pause binding", detail, ["Assign key / mouse button", "Use Escape", "Back"])

func _select(index: int) -> void:
	match page:
		"home":
			match index:
				0: page = "profiles"
				1:
					page = "bindings"
					binding_page = 0
				2: _result(controls.reset_defaults())
				3:
					close()
					return
		"profiles":
			if index < PROFILES.size():
				_result(controls.set_profile(PROFILES[index]))
			page = "home"
		"bindings":
			var start := binding_page * 6
			var count := mini(6, controls.ACTIONS.size() - start)
			if index < count:
				var action: String = controls.ACTIONS[start + index]
				if action == "pause":
					page = "pause_binding"
				else:
					_capture(action)
					return
			elif index == count: binding_page = 1 - binding_page
			else: page = "home"
		"pause_binding":
			if index == 0:
				_capture("pause")
				return
			if index == 1:
				var event := InputEventKey.new()
				event.physical_keycode = KEY_ESCAPE
				_result(controls.rebind("pause", event))
			page = "bindings"
	_show()

func _back() -> void:
	if page == "home":
		close()
		return
	capture_action = ""
	message = ""
	page = "bindings" if page == "pause_binding" else "home"
	_show()

func _result(error: Error) -> void:
	message = "" if error == OK else "Change failed (%s). Previous bindings kept." % error_string(error)

func _capture(action: String) -> void:
	capture_action = action
	_capture_frame = Engine.get_process_frames()
	menu.show_menu("Bind " + controls.ACTION_LABELS[action], "Press a key or mouse button. Escape cancels.\nOne input at a time; wheel only binds single actions.", [])
	# The capturing modal alone handles the event; normal menu polling must not confirm it.
	menu.set_process(false)
	menu.set_process_input(false)

func _input(event: InputEvent) -> void:
	if not opened or capture_action.is_empty(): return
	get_viewport().set_input_as_handled()
	if Engine.get_process_frames() <= _capture_frame: return
	if event is InputEventKey:
		if not event.pressed or event.echo: return
		if event.keycode == KEY_ESCAPE or event.physical_keycode == KEY_ESCAPE:
			capture_action = ""
			_show()
			return
	elif event is InputEventMouseButton:
		if not event.pressed: return
	else: return
	var error: Error = controls.rebind(capture_action, event)
	if error != OK:
		menu._play("error")
		if error == ERR_ALREADY_EXISTS:
			menu.description.text = "Already assigned to another action.\nChoose another key / button. Escape cancels."
		elif controls.storage_error != OK:
			menu.description.text = "Could not save controls. Previous bindings kept.\nRetry or press Escape to cancel."
		else:
			menu.description.text = "Unsupported input for this action.\nChoose a single key / button. Escape cancels."
		return
	capture_action = ""
	message = ""
	page = "bindings"
	_show()

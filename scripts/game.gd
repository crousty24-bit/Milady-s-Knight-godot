extends Node
const MENU = preload("res://scripts/keyboard_menu.gd")
var menu: CanvasLayer
var screen: String = "main"
@onready var progression = get_node("/root/Progression")

func _ready() -> void:
	get_tree().paused = false
	get_tree().auto_accept_quit = false
	menu = MENU.new()
	add_child(menu)
	menu.selected.connect(_select)
	menu.cancelled.connect(_cancel)
	_main()

func _main() -> void:
	screen = "main"
	var detail := "Arrows: select   E: confirm   Escape: back"
	if progression.legacy_pending:
		detail = "Legacy save found. Continue offers migration."
	elif progression.storage_error != OK:
		detail = "Save unreadable. Original file protected."
	menu.show_menu("Milady's Knight", detail, ["New Game", "Continue", "Controls", "Quit"], [] if progression.has_save or progression.legacy_pending else [1])

func _select(index: int) -> void:
	match screen:
		"main":
			match index:
				0:
					if progression.has_save or progression.legacy_pending or progression.storage_error != OK:
						screen = "new"
						menu.show_menu("Replace this game?", "The previous file will be backed up.", ["Cancel", "New Game"])
					else: _new_game()
				1:
					if progression.legacy_pending:
						screen = "migration"
						menu.show_menu("Import legacy save?", "Old bonus (kills + extra coins) becomes shards.\nThe original file will be kept.", ["Cancel", "Convert and Continue"])
					elif progression.has_save: _continue()
				2:
					screen = "controls"
					menu.show_menu("Controls", "Arrows: move / menu selection\nSpace: jump / double jump / skip dialogue\nF (hold): attack / shoot   E: interact / confirm\nA: equipment   G: landing attack\nR (hold): Dragon Slayer special\nEscape: close / back / pause", ["Back"])
				3: get_tree().quit()
		"new":
			if index == 1: _new_game()
			else: _main()
		"migration":
			if index == 0: _main()
			elif progression.migrate_v1(true) == OK: _continue()
			else: _error("Migration failed. Original save protected.")
		"controls", "error": _main()

func _new_game() -> void:
	if progression.new_game() == OK: _continue()
	else: _error("Save failed. Your previous game is protected.")

func _continue() -> void:
	menu.close()
	for action in ["interact", "attack", "jump", "pause", "move_left", "move_right"]:
		Input.action_release(action)
	var error: Error = progression.change_level(progression.resume_scene)
	if error != OK: _error("Level unavailable. Your save is protected.")

func _error(message: String) -> void:
	screen = "error"
	menu.show_menu("Unable to continue", message, ["Back"])

func _cancel() -> void:
	if screen != "main": _main()

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST: get_tree().quit()

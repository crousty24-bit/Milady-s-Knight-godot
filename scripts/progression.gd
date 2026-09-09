extends Node
# Only settled bonuses and the next scene cross attempts. Level state stays in level.gd.
const SAVE_VERSION = 1
const DEFAULT_LEVEL = "res://scenes/vertical_slice.tscn"
const SAVE_PATH = "user://progress.json"
const MAX_BONUS = 9007199254740991 # JSON's exact integer range.
var banked_bonus: int = 0
var resume_scene: String = DEFAULT_LEVEL
var storage_path: String = SAVE_PATH
var persistence_enabled: bool = true
var storage_error: Error = OK

func _ready() -> void:
	# SceneTree drivers must never read or change the player's actual save.
	if OS.get_cmdline_args().has("--script"):
		persistence_enabled = false
		return
	load_progress()

func load_progress() -> Error:
	storage_error = _read_progress()
	return storage_error

func _read_progress() -> Error:
	if not FileAccess.file_exists(storage_path): return OK
	var file := FileAccess.open(storage_path, FileAccess.READ)
	if file == null: return FileAccess.get_open_error()
	var data = JSON.parse_string(file.get_as_text())
	if not data is Dictionary or data.get("version") != SAVE_VERSION:
		return ERR_FILE_UNRECOGNIZED
	var amount = data.get("bonus_bank")
	if not (amount is float or amount is int) or not is_finite(float(amount)) or amount < 0 or amount > MAX_BONUS or float(amount) != floorf(float(amount)):
		return ERR_FILE_CORRUPT
	var scene = data.get("resume_scene")
	if not scene is String: return ERR_FILE_CORRUPT
	banked_bonus = int(amount)
	resume_scene = scene if _valid_level(scene) else DEFAULT_LEVEL
	return OK

func _valid_level(path: String) -> bool:
	return path.begins_with("res://") and path.ends_with(".tscn") and ResourceLoader.exists(path, "PackedScene")

func settle_level(earned_bonus: int, destination: String) -> Error:
	if earned_bonus < 0 or not _valid_level(destination):
		return ERR_INVALID_PARAMETER
	# Do not overwrite a save whose format could not be read (including future versions).
	if storage_error != OK and load_progress() != OK: return storage_error
	if earned_bonus > MAX_BONUS - banked_bonus: return ERR_INVALID_PARAMETER
	var new_total: int = banked_bonus + earned_bonus
	if persistence_enabled:
		var temporary := storage_path + ".tmp"
		var file := FileAccess.open(temporary, FileAccess.WRITE)
		if file == null: return FileAccess.get_open_error()
		file.store_string(JSON.stringify({"version": SAVE_VERSION, "bonus_bank": new_total, "resume_scene": destination}))
		file.flush()
		var error := file.get_error()
		file.close()
		if error != OK: return error
		error = DirAccess.rename_absolute(ProjectSettings.globalize_path(temporary), ProjectSettings.globalize_path(storage_path))
		if error != OK: return error
	banked_bonus = new_total
	resume_scene = destination
	return OK

func change_level(path: String) -> Error:
	if not _valid_level(path): return ERR_FILE_NOT_FOUND
	return get_tree().change_scene_to_file(path)

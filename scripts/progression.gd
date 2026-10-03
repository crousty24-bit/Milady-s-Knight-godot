extends Node
# Durable state only. Attempt gains, position and health belong to level.gd.
const SAVE_VERSION = 2
const DEFAULT_LEVEL = "res://scenes/eidolon_vale.tscn"
const LEGACY_SLICE = "res://scenes/vertical_slice.tscn"
const SAVE_PATH = "user://progress.json"
const MAX_BONUS = 9007199254740991 # JSON's exact integer range.
var banked_shards: int = 0
# Compatibility for existing level/HUD callers.
var banked_bonus: int:
	get: return banked_shards
	set(value): banked_shards = value
var resume_scene: String = DEFAULT_LEVEL
var equipment: Dictionary = {"melee": "Sword0", "ranged": ""}
var permanent_flags: Dictionary = {}
var completed_dialogues: Dictionary = {}
var storage_path: String = SAVE_PATH
var persistence_enabled: bool = true
var storage_error: Error = OK
var has_save: bool = false
var legacy_pending: bool = false

func _ready() -> void:
	# SceneTree drivers must never read or change the player's actual save.
	if OS.get_cmdline_args().has("--script"):
		persistence_enabled = false
		return
	load_progress()

func load_progress() -> Error:
	has_save = false
	legacy_pending = false
	storage_error = _read_progress()
	return storage_error

func _read_progress() -> Error:
	if not FileAccess.file_exists(storage_path): return OK
	var file := FileAccess.open(storage_path, FileAccess.READ)
	if file == null: return FileAccess.get_open_error()
	var data = _parse_json(file.get_as_text())
	if not data is Dictionary: return ERR_FILE_CORRUPT
	if data.get("version") == 1:
		if not _valid_legacy(data): return ERR_FILE_CORRUPT
		legacy_pending = true
		return ERR_FILE_UNRECOGNIZED
	if data.get("version") != SAVE_VERSION: return ERR_FILE_UNRECOGNIZED
	if not _valid_amount(data.get("shards_bank")) or not data.get("resume_scene") is String:
		return ERR_FILE_CORRUPT
	var slots = data.get("equipment")
	if not slots is Dictionary or not slots.get("melee") is String or not slots.get("ranged") is String or slots.melee.is_empty():
		return ERR_FILE_CORRUPT
	if not _valid_flags(data.get("permanent_flags")) or not _valid_flags(data.get("completed_dialogues")):
		return ERR_FILE_CORRUPT
	_apply(data)
	has_save = true
	return OK

func _parse_json(text: String) -> Variant:
	var parser := JSON.new()
	return parser.data if parser.parse(text) == OK else null

func _valid_amount(value: Variant) -> bool:
	return (value is float or value is int) and is_finite(float(value)) and value >= 0 and value <= MAX_BONUS and float(value) == floorf(float(value))

func _valid_flags(value: Variant) -> bool:
	if not value is Dictionary: return false
	for key in value:
		if not key is String or key.is_empty() or not value[key] is bool or value[key] != true: return false
	return true

func _valid_legacy(data: Dictionary) -> bool:
	return _valid_amount(data.get("bonus_bank")) and data.get("resume_scene") is String

func _valid_level(path: String) -> bool:
	return path.begins_with("res://") and path.ends_with(".tscn") and ResourceLoader.exists(path, "PackedScene")

func _state() -> Dictionary:
	return {"version": SAVE_VERSION, "shards_bank": banked_shards, "resume_scene": resume_scene, "equipment": equipment.duplicate(true), "permanent_flags": permanent_flags.duplicate(true), "completed_dialogues": completed_dialogues.duplicate(true)}

func _initial_state() -> Dictionary:
	return {"version": SAVE_VERSION, "shards_bank": 0, "resume_scene": DEFAULT_LEVEL, "equipment": {"melee": "Sword0", "ranged": ""}, "permanent_flags": {}, "completed_dialogues": {}}

func _apply(data: Dictionary) -> void:
	banked_shards = int(data.shards_bank)
	resume_scene = data.resume_scene if _valid_level(data.resume_scene) else DEFAULT_LEVEL
	# Existing prototype saves enter N1 with all equipment, bank and flags intact.
	if resume_scene == LEGACY_SLICE: resume_scene = DEFAULT_LEVEL
	equipment = data.equipment.duplicate(true)
	permanent_flags = data.permanent_flags.duplicate(true)
	completed_dialogues = data.completed_dialogues.duplicate(true)

func _write(data: Dictionary) -> Error:
	if persistence_enabled:
		var temporary := storage_path + ".tmp"
		var file := FileAccess.open(temporary, FileAccess.WRITE)
		if file == null: return FileAccess.get_open_error()
		file.store_string(JSON.stringify(data))
		file.flush()
		var error := file.get_error()
		file.close()
		if error != OK: return error
		error = DirAccess.rename_absolute(ProjectSettings.globalize_path(temporary), ProjectSettings.globalize_path(storage_path))
		if error != OK: return error
	_apply(data)
	has_save = true
	legacy_pending = false
	return OK

func _commit(data: Dictionary) -> Error:
	storage_error = _write(data)
	return storage_error

func _can_modify() -> bool:
	# Recover after a repaired file, but never silently overwrite an unreadable save.
	if persistence_enabled and (storage_error != OK or (not has_save and FileAccess.file_exists(storage_path))):
		return load_progress() == OK
	return true

func _preserve_original(suffix: String) -> Error:
	var source := FileAccess.open(storage_path, FileAccess.READ)
	if source == null: return FileAccess.get_open_error()
	var contents := source.get_buffer(source.get_length())
	var error := source.get_error()
	source.close()
	if error != OK: return error
	var canonical := storage_path + suffix
	var backup := canonical
	var index := 0
	while FileAccess.file_exists(backup):
		var previous := FileAccess.open(backup, FileAccess.READ)
		if previous == null: return FileAccess.get_open_error()
		var previous_contents := previous.get_buffer(previous.get_length())
		error = previous.get_error()
		previous.close()
		if error != OK: return error
		if previous_contents == contents: return OK
		index += 1
		backup = canonical + ".%d" % index
	return DirAccess.copy_absolute(ProjectSettings.globalize_path(storage_path), ProjectSettings.globalize_path(backup))

func migrate_v1(accepted: bool = false) -> Error:
	if not accepted: return ERR_UNAUTHORIZED
	if load_progress() != ERR_FILE_UNRECOGNIZED or not legacy_pending: return storage_error if storage_error != OK else ERR_INVALID_DATA
	var data = _parse_json(FileAccess.get_file_as_string(storage_path))
	if not data is Dictionary or not _valid_legacy(data): return ERR_FILE_CORRUPT
	var error := _preserve_original(".v1.bak")
	if error != OK:
		storage_error = error
		return error
	var migrated := _initial_state()
	migrated.shards_bank = int(data.bonus_bank)
	migrated.resume_scene = data.resume_scene if _valid_level(data.resume_scene) else DEFAULT_LEVEL
	return _commit(migrated)

func new_game() -> Error:
	# Explicit overwrite from the confirmed menu; retain the original for recovery.
	if persistence_enabled and FileAccess.file_exists(storage_path):
		var raw = _parse_json(FileAccess.get_file_as_string(storage_path))
		var suffix := ".v1.bak" if raw is Dictionary and raw.get("version") == 1 else ".bak"
		var error := _preserve_original(suffix)
		if error != OK:
			storage_error = error
			return error
	return _commit(_initial_state())

func settle_level(earned_bonus: int, destination: String) -> Error:
	if earned_bonus < 0 or not _valid_level(destination): return ERR_INVALID_PARAMETER
	if not _can_modify(): return storage_error
	if earned_bonus > MAX_BONUS - banked_shards: return ERR_INVALID_PARAMETER
	var data := _state()
	data.shards_bank += earned_bonus
	data.resume_scene = destination
	return _commit(data)

func _spend_state(cost: int, current_gains: int) -> Dictionary:
	if cost < 0 or current_gains < 0 or current_gains > MAX_BONUS: return {}
	var from_bank := maxi(0, cost - current_gains)
	if from_bank > banked_shards: return {}
	var data := _state()
	data.shards_bank -= from_bank
	return {"state": data, "remaining": maxi(0, current_gains - cost)}

func spend_shards(cost: int, current_gains: int) -> int:
	if not _can_modify(): return -1
	var payment := _spend_state(cost, current_gains)
	if payment.is_empty():
		storage_error = ERR_INVALID_PARAMETER
		return -1
	if payment.state.shards_bank != banked_shards and _commit(payment.state) != OK: return -1
	storage_error = OK
	return payment.remaining

func acquire_equipment(slot: String, item: String, cost: int = 0, current_gains: int = 0) -> int:
	if not slot in ["melee", "ranged"] or item.is_empty() or not _can_modify(): return -1
	var payment := _spend_state(cost, current_gains)
	if payment.is_empty(): return -1
	payment.state.equipment[slot] = item
	if _commit(payment.state) != OK: return -1
	return payment.remaining

func set_permanent_flag(id: String) -> Error:
	if id.is_empty(): return ERR_INVALID_PARAMETER
	if not _can_modify(): return storage_error
	var data := _state()
	data.permanent_flags[id] = true
	return _commit(data)

func complete_dialogue(id: String) -> Error:
	if id.is_empty(): return ERR_INVALID_PARAMETER
	if not _can_modify(): return storage_error
	var data := _state()
	data.completed_dialogues[id] = true
	return _commit(data)

func change_level(path: String) -> Error:
	if not _valid_level(path): return ERR_FILE_NOT_FOUND
	return get_tree().change_scene_to_file(path)

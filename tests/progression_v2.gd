extends SceneTree
const Store = preload("res://scripts/progression.gd")
const NEXT = "res://tests/fixtures/next_level.tscn"
var checks := 0
var failures := 0
var stores: Array = []
var path: String
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func make_store(at: String = "") -> Node:
	var store = Store.new()
	store.storage_path = at if not at.is_empty() else path
	stores.append(store)
	return store
func fixture(text: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(text)
	file.close()
func run() -> void:
	path = "user://progress-v2-test-%d-%d.json" % [OS.get_process_id(), Time.get_ticks_usec()]
	var store = make_store()
	check(store.load_progress() == OK and not store.has_save, "no save disables Continue")
	check(store.new_game() == OK and store.has_save and store.equipment.melee == "Sword0", "new game commits initial equipment")
	check(store.settle_level(50, NEXT) == OK, "level settlement persists shards and destination")
	check(store.spend_shards(12, 8) == 0 and store.banked_shards == 46, "purchase spends attempt gains before bank")
	var reopened = make_store()
	check(reopened.load_progress() == OK and reopened.banked_shards == 46 and reopened.resume_scene == NEXT, "cold reload after death retains bank debit and level")
	check(reopened.spend_shards(5, 8) == 3 and reopened.banked_shards == 46, "attempt-only payment retains bank")
	check(reopened.spend_shards(100, 0) == -1 and reopened.banked_shards == 46, "insufficient funds do not mutate bank")
	check(reopened.acquire_equipment("ranged", "Longbow", 10, 3) == 0 and reopened.banked_shards == 39, "acquisition and bank debit commit together")
	check(reopened.set_permanent_flag("unique-key") == OK and reopened.complete_dialogue("intro") == OK, "permanent unique and dialogue completion commit immediately")
	var acquired = make_store()
	check(acquired.load_progress() == OK and acquired.equipment.ranged == "Longbow" and acquired.permanent_flags.has("unique-key") and acquired.completed_dialogues.has("intro") and acquired.banked_shards == 39, "equipment and permanent state survive cold reload")
	var original := FileAccess.get_file_as_string(path)
	check(acquired.new_game() == OK and acquired.banked_shards == 0 and acquired.equipment.ranged == "" and acquired.completed_dialogues.is_empty(), "new game resets all durable state")
	check(FileAccess.get_file_as_string(path + ".bak") == original, "new game preserves exact original")
	check(acquired.acquire_equipment("ranged", "Longbow") == 0, "second game obtains durable equipment")
	var second_original := FileAccess.get_file_as_string(path)
	check(acquired.new_game() == OK and FileAccess.get_file_as_string(path + ".bak") == original, "repeated new game never replaces original backup")
	check(FileAccess.get_file_as_string(path + ".bak.1") == second_original, "second new game preserves the immediately previous equipment save")
	check(acquired.acquire_equipment("ranged", "Longbow") == 0 and acquired.new_game() == OK and not FileAccess.file_exists(path + ".bak.2"), "identical previous save reuses its byte-exact backup")
	var legacy := '{ "version": 1, "bonus_bank": 57, "resume_scene": "res://tests/fixtures/next_level.tscn" }\n'
	fixture(legacy)
	var migration = make_store()
	check(migration.load_progress() == ERR_FILE_UNRECOGNIZED and migration.legacy_pending and not migration.has_save, "v1 requires migration before Continue")
	check(migration.migrate_v1(false) == ERR_UNAUTHORIZED and migration.legacy_pending and FileAccess.get_file_as_string(path) == legacy, "migration refusal preserves original and pending prompt")
	check(migration.settle_level(2, NEXT) != OK and FileAccess.get_file_as_string(path) == legacy, "ordinary writes cannot silently migrate v1")
	check(migration.migrate_v1(true) == OK and migration.banked_shards == 57 and not migration.legacy_pending and migration.has_save, "explicit migration converts exact legacy bank")
	check(FileAccess.get_file_as_string(path + ".v1.bak") == legacy, "migration preserves byte-exact legacy backup")
	var migrated = make_store()
	check(migrated.load_progress() == OK and migrated.banked_shards == 57 and migrated.equipment.melee == "Sword0", "migrated v2 survives cold reload")
	check(migrated.new_game() == OK and FileAccess.get_file_as_string(path + ".v1.bak") == legacy, "new game after migration retains legacy original")
	for bad in ['{broken', '{"version":99}', '{"version":1,"bonus_bank":-1,"resume_scene":"x"}', '{"version":2,"shards_bank":0,"resume_scene":"x","equipment":{},"permanent_flags":{},"completed_dialogues":{}}']:
		fixture(bad)
		var rejected = make_store()
		check(rejected.load_progress() != OK and not rejected.has_save and not rejected.legacy_pending, "corrupt or future save disables Continue")
		check(rejected.settle_level(1, NEXT) != OK and rejected.complete_dialogue("intro") != OK and FileAccess.get_file_as_string(path) == bad, "invalid save cannot be overwritten by durable actions")
	var failed = make_store("user://missing-dir-%d/save.json" % Time.get_ticks_usec())
	failed.banked_shards = 50
	check(failed.spend_shards(12, 8) == -1 and failed.banked_shards == 50 and failed.storage_error != OK, "disk failure refuses debit without memory change")
	check(failed.acquire_equipment("ranged", "Longbow", 5, 8) == -1 and failed.equipment.ranged == "" and failed.banked_shards == 50, "disk failure refuses acquisition even when attempt gains cover cost")
	check(failed.settle_level(7, NEXT) != OK and failed.banked_shards == 50 and failed.resume_scene == Store.DEFAULT_LEVEL, "disk failure does not settle gains or change level")
	check(failed.new_game() != OK and failed.banked_shards == 50 and not failed.has_save, "new game commits memory only after disk success")
	var removed_scene = JSON.parse_string(original)
	removed_scene.resume_scene = "res://removed-level.tscn"
	fixture(JSON.stringify(removed_scene))
	var fallback = make_store()
	check(fallback.load_progress() == OK and fallback.resume_scene == Store.DEFAULT_LEVEL and fallback.banked_shards == 39, "removed level falls back without losing bank or equipment")
	var rename_path := path + ".directory"
	DirAccess.make_dir_absolute(ProjectSettings.globalize_path(rename_path))
	var rename_failure = make_store(rename_path)
	rename_failure.banked_shards = 50
	check(rename_failure.new_game() != OK and rename_failure.banked_shards == 50 and not rename_failure.has_save, "failed atomic rename keeps memory unchanged")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(rename_path + ".tmp"))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(rename_path))
	# A blocked temporary file also keeps the legacy save intact.
	fixture(legacy)
	var blocked = make_store()
	check(blocked.load_progress() != OK, "replacement fixture starts as legacy")
	DirAccess.make_dir_absolute(ProjectSettings.globalize_path(path + ".tmp"))
	check(blocked.migrate_v1(true) != OK and blocked.banked_shards == 0 and blocked.legacy_pending and FileAccess.get_file_as_string(path) == legacy, "failed migration retains old save and memory")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path + ".tmp"))
	check(blocked.migrate_v1(true) == OK and blocked.banked_shards == 57, "migration retries after disk repair without duplicate credit")
	for suffix in ["", ".bak", ".bak.1", ".bak.2", ".bak.3", ".v1.bak", ".tmp"]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path + suffix))
	for object in stores: object.free()
	print("RESULT %d progression v2 checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

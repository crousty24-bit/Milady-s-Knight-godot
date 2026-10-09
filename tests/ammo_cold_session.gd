# Three separate engine processes exercise the durable entry snapshot.
extends SceneTree
var checks := 0
var failures := 0
var room: Node2D
const N3 := "res://scenes/black_forrest.tscn"
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func run() -> void:
	var store := root.get_node("Progression")
	store.storage_path = "user://ammo-cold-entry.json"
	store.persistence_enabled = true
	var args := OS.get_cmdline_user_args()
	var stage: String = args[0] if not args.is_empty() else ""
	if stage == "prepare":
		check(store.new_game() == OK, "cold ammo new game initializes isolated save")
		check(store.settle_level(3, N3, {"Longbow":2,"ThrowingKnives":4}) == OK, "cold ammo prepare stores remaining stocks with next level")
	elif stage in ["reopen", "reset"]:
		check(store.load_progress() == OK and store.ammo_entry == {"Longbow":2,"ThrowingKnives":4}, "cold %s restores entry snapshot from another process" % stage)
		check(store.resume_scene == N3 and store.banked_shards == 3, "cold %s preserves atomic destination and bank" % stage)
		room = load(N3).instantiate()
		root.add_child(room)
		current_scene = room
		check(room.player.ammo == {"Longbow":2,"ThrowingKnives":4}, "real N3 cold spawn starts with two arrows and four knives")
		room.player.add_ammo("Longbow",5)
		check(room.player.ammo.Longbow == 7 and store.ammo_entry.Longbow == 2, "cold %s loot changes live reserve only" % stage)
		if stage == "reopen":
			check(store.set_permanent_flag("ammo-cold-proof") == OK, "durable action after loot saves entry reserve rather than live seven")
		else:
			check(store.permanent_flags.has("ammo-cold-proof"), "third process sees durable flag without saving live loot")
			DirAccess.remove_absolute(ProjectSettings.globalize_path(store.storage_path))
			DirAccess.remove_absolute(ProjectSettings.globalize_path(store.storage_path + ".bak"))
	else:
		check(false,"expected prepare reopen or reset")
	if is_instance_valid(room):
		for sound in room.find_children("*", "AudioStreamPlayer", true, false): sound.stop()
		for sound in room.find_children("*", "AudioStreamPlayer2D", true, false): sound.stop()
		OS.delay_msec(300)
		room.queue_free()
		await process_frame
		await process_frame
	print("RESULT %d ammo cold %s checks; %d failures" % [checks,stage,failures])
	quit(1 if failures else 0)

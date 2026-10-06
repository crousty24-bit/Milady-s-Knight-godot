# RUN-020 reprise: native 640x360 captures of the redrawn Bloated Slime / Chud Blob next to the
# player inside the real N2 / N4 level scenes (read-only). Poses are forced through the enemy's
# AnimatedSprite2D; this is a presentation inspection, not a gameplay test.
# Usage: GODOT_BIN=... bash work/run020/check.sh elites-capture --script res://tools/art/run020_feedback/capture_elites.gd
extends SceneTree
const OUT = "res://work/run020/claude-feedback/elites/native"
const JOBS = [
	{"level": "res://scenes/blight_town.tscn", "kind": 0, "shots": [
		["bloated-crawl-left", &"crawl", 0, -56.0], ["bloated-crawl-right", &"crawl", 3, 56.0],
		["bloated-swell-contact", &"swell", 2, -26.0]]},
	{"level": "res://scenes/forbidden_graveyard.tscn", "kind": 4, "shots": [
		["chud-idle-left", &"idle", 0, -64.0], ["chud-idle-right", &"idle", 1, 64.0],
		["chud-windup-peak", &"windup", 2, -40.0], ["chud-slam-impact", &"slam", 1, -28.0],
		["chud-slam-swing", &"slam", 0, -40.0], ["chud-walk", &"walk", 2, -64.0]]},
]
var level: Node2D
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func shot(name: String, enemy: Node2D, anim: StringName, frame: int, dx: float) -> void:
	paused = false
	var art: AnimatedSprite2D = enemy.get("_art")
	art.play(anim)
	art.set_frame_and_progress(frame, 0.0)
	art.pause()
	# The enemy faces the player; sheets face left, so a player on the right flips the sprite.
	enemy.set("direction", 1 if dx > 0.0 else -1)
	art.flip_h = dx > 0.0
	level.player.position = enemy.global_position + Vector2(dx, -2)
	level.player.velocity = Vector2.ZERO
	level.player.controls_enabled = false
	await frames(25)
	art.flip_h = dx > 0.0
	art.set_frame_and_progress(frame, 0.0)
	art.pause()
	level.camera.position_smoothing_enabled = false
	level.camera.reset_smoothing()
	level.camera.force_update_scroll()
	await frames(2)
	paused = true
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var picture := root.get_texture().get_image()
	check(picture.get_size() == Vector2i(640, 360), "native 640x360 " + name)
	check(picture.save_png(OUT + "/" + name + ".png") == OK, "saved " + name)
	print("INFO %s enemy=%s player=%s anim=%s frame=%d" % [name, enemy.global_position, level.player.global_position, anim, frame])
func run() -> void:
	if DisplayServer.get_name() == "headless":
		check(false, "render requires display")
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	for job in JOBS:
		level = load(job.level).instantiate()
		root.add_child(level)
		current_scene = level
		await frames(6)
		var found: Array = []
		for node in get_nodes_in_group("enemies"):
			if node.get("kind") == job.kind and node.get_script() != null and level.is_ancestor_of(node): found.append(node)
		check(found.size() > 0, "%s has kind %d enemies (%d)" % [job.level, job.kind, found.size()])
		if found.is_empty(): continue
		# Freeze every enemy's logic so only the forced pose is drawn.
		for node in get_nodes_in_group("enemies"):
			node.set_physics_process(false)
			node.set_process(false)
		var enemy: Node2D = found[0]
		print("INFO target enemy at ", enemy.global_position)
		for spec in job.shots:
			await shot(spec[0], enemy, spec[1], spec[2], spec[3])
		for audio in root.find_children("*", "AudioStreamPlayer", true, false): audio.stop()
		level.queue_free()
		paused = false
		await frames(3)
	print("RESULT %d checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

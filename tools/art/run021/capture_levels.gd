# RUN-021: native 640x360 views of the production levels N1-N4 for visual comparison
# (presentation inspection only). The player is placed by code on authored surfaces and
# actors run for a short settle time; these teleports do not prove a natural keyboard route.
# N1 is the production scene eidolon_vale.tscn with its intro cinematic disabled for the view.
# Usage: bash work/run021/check.sh <label> --script res://tools/art/run021/capture_levels.gd -- <out_dir_name>
extends SceneTree
const JOBS = [
	{"level": "res://scenes/eidolon_vale.tscn", "tag": "n1", "shots": [
		["01-spawn", Vector2(220, 144)], ["02-upper-path", Vector2(608, 36)],
		["03-lower-path", Vector2(956, 212)], ["04-high-ledge", Vector2(1136, 68)],
		["05-mid", Vector2(1640, 132)], ["06-gate", Vector2(2072, 144)]]},
	{"level": "res://scenes/blight_town.tscn", "tag": "n2", "shots": [
		["01-spawn-yard", Vector2(240, 112)], ["02-f1-tower-fork", Vector2(1032, 112)],
		["04-f1-vault-chest", Vector2(1150, 240)], ["05-market-trapdoor", Vector2(1660, 144)],
		["07-f2-causeway-potion", Vector2(2860, 48)], ["09-bloated-arena", Vector2(3330, 144)],
		["10-gate", Vector2(3560, 144)]]},
	{"level": "res://scenes/black_forrest.tscn", "tag": "n3", "shots": [
		["01-spawn-hollow", Vector2(330, 144)], ["03-f1-canopy-archer", Vector2(1560, 16)],
		["04-f1-bramble-chest", Vector2(1400, 144)], ["05-ravine-shield-turret", Vector2(2200, 144)],
		["07-f2-crowns-potion", Vector2(3140, -16)], ["09-clearing-gate", Vector2(3880, 112)]]},
	{"level": "res://scenes/forbidden_graveyard.tscn", "tag": "n4", "shots": [
		["01-spawn-graves", Vector2(250, 144)], ["03-f1-chapel-coin-door", Vector2(1440, 48)],
		["04-f1-crypt-chest", Vector2(1700, 240)], ["05-skull-field", Vector2(2250, 144)],
		["07-f2-catacomb", Vector2(3200, 240)], ["08-bell-tower-button", Vector2(4020, 0)],
		["10-chud-arena", Vector2(4380, 144)]]},
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
func run() -> void:
	if DisplayServer.get_name() == "headless":
		check(false, "render requires display")
		quit(1)
		return
	var args := OS.get_cmdline_user_args()
	var out: String = "res://work/run021/captures/" + (args[0] if args.size() > 0 else "native")
	var only: String = args[1] if args.size() > 1 else ""
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	for job in JOBS:
		if only != "" and job.tag != only: continue
		for spec in job.shots:
			# A fresh instance per view: earlier views never leave fights or opened traps behind.
			level = load(job.level).instantiate()
			if "n1_intro_enabled" in level: level.n1_intro_enabled = false
			root.add_child(level)
			current_scene = level
			paused = false
			await frames(4)
			level.player.position = spec[1]
			level.player.velocity = Vector2.ZERO
			level.player.health_units = level.player.max_health_units
			level.camera.reset_smoothing()
			await frames(40)
			check(not level.player.dead, "%s %s player alive" % [job.tag, spec[0]])
			level.camera.reset_smoothing()
			level.camera.force_update_scroll()
			await frames(2)
			paused = true
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var picture := root.get_texture().get_image()
			var path: String = out + "/" + job.tag + "-" + spec[0] + ".png"
			check(picture.get_size() == Vector2i(640, 360) and picture.save_png(path) == OK, "saved native " + path)
			print("INFO %s player=%s" % [path, level.player.global_position])
			paused = false
			level.queue_free()
			await frames(2)
	print("RESULT checks=%d failures=%d" % [checks, failures])
	quit(1 if failures > 0 else 0)

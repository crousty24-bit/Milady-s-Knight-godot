# RUN-020 reprise: native 640x360 views of the recomposed N2-N4 routes (presentation
# inspection only). The player is placed by code on authored surfaces; actors run normally
# for a short settle time. These teleports do not prove the natural keyboard route.
# Usage: GODOT_BIN=... bash work/run020/check.sh levels-capture --script res://tools/art/run020_feedback/capture_levels.gd
extends SceneTree
const OUT = "res://work/run020/claude-feedback/native"
const JOBS = [
	{"level": "res://scenes/blight_town.tscn", "tag": "n2", "shots": [
		["01-spawn-yard", Vector2(240, 112)], ["02-f1-tower-fork", Vector2(1032, 112)],
		["03-f1-ramparts", Vector2(1344, 48)], ["04-f1-vault-chest", Vector2(1150, 240)],
		["05-market-trapdoor", Vector2(1660, 144)], ["06-market-hall-roof", Vector2(2060, 64)],
		["07-f2-causeway-potion", Vector2(2860, 48)], ["08-f2-lane-sunk", Vector2(2620, 144)],
		["09-bloated-arena", Vector2(3330, 144)], ["10-gate", Vector2(3560, 144)]]},
	{"level": "res://scenes/black_forrest.tscn", "tag": "n3", "shots": [
		["01-spawn-hollow", Vector2(330, 144)], ["02-f1-trunk-fork", Vector2(1224, 112)],
		["03-f1-canopy-archer", Vector2(1560, 16)], ["04-f1-bramble-chest", Vector2(1400, 144)],
		["05-ravine-shield-turret", Vector2(2200, 144)], ["06-ravine-stumps", Vector2(2368, 96)],
		["07-f2-crowns-potion", Vector2(3140, -16)], ["08-f2-gully-trapdoor", Vector2(2990, 240)],
		["09-clearing-gate", Vector2(3880, 112)]]},
	{"level": "res://scenes/forbidden_graveyard.tscn", "tag": "n4", "shots": [
		["01-spawn-graves", Vector2(250, 144)], ["02-mausoleum-roof-secret", Vector2(480, 64)],
		["03-f1-chapel-coin-door", Vector2(1440, 48)], ["04-f1-crypt-chest", Vector2(1700, 240)],
		["05-skull-field", Vector2(2250, 144)], ["06-f2-surface-turret", Vector2(3240, 144)],
		["07-f2-catacomb", Vector2(3200, 240)], ["08-bell-tower-button", Vector2(4020, 0)],
		["09-mechanism-door", Vector2(4100, 144)], ["10-chud-arena", Vector2(4380, 144)]]},
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
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	for job in JOBS:
		for spec in job.shots:
			# A fresh instance per view: earlier views never leave fights or opened traps behind.
			level = load(job.level).instantiate()
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
			var path: String = OUT + "/" + job.tag + "-" + spec[0] + ".png"
			check(picture.get_size() == Vector2i(640, 360) and picture.save_png(path) == OK, "saved native " + path)
			print("INFO %s player=%s" % [path, level.player.global_position])
			paused = false
			level.queue_free()
			await frames(2)
	print("RESULT checks=%d failures=%d" % [checks, failures])
	quit(1 if failures > 0 else 0)

# RUN-021: presentation cost per production level (decor prop count, frame time, draw calls).
# Indicative only: one windowed run, player parked at spawn. Usage: bash work/run021/check.sh perf --script res://tools/art/run021/perf_check.gd
extends SceneTree
const LEVELS = ["res://scenes/eidolon_vale.tscn", "res://scenes/blight_town.tscn", "res://scenes/black_forrest.tscn", "res://scenes/forbidden_graveyard.tscn"]
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func run() -> void:
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	for path in LEVELS:
		var level: Node2D = load(path).instantiate()
		if "n1_intro_enabled" in level: level.n1_intro_enabled = false
		root.add_child(level)
		current_scene = level
		for i in 30: await process_frame
		var draw_max := 0
		var samples := 240
		var worst_ms := 0.0
		var start := Time.get_ticks_usec()
		var last := start
		for i in samples:
			await process_frame
			var now := Time.get_ticks_usec()
			worst_ms = maxf(worst_ms, (now - last) / 1000.0)
			last = now
			draw_max = maxi(draw_max, int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)))
		var decor := level.get_node_or_null("Decor")
		var props: int = decor._placed.size() if decor != null and "_placed" in decor else -1
		var avg_ms := (last - start) / 1000.0 / samples
		print("INFO %s props=%d avg_frame_ms=%.2f worst_frame_ms=%.2f max_draw_calls=%d" % [path.get_file(), props, avg_ms, worst_ms, draw_max])
		# 60 fps budget: the average frame (vsync included) must stay within 16.7 ms.
		check(avg_ms < 16.7, "%s average frame within the 60 fps budget" % path.get_file())
		level.queue_free()
		for i in 3: await process_frame
	print("RESULT checks=%d failures=%d" % [checks, failures])
	quit(1 if failures > 0 else 0)

# RUN-021: Skeleton Archer movement-animation reproduction (diagnosis only, no production edits).
# Logs per physics frame the presentation and logic state of archers in production levels, and saves
# native frames / enlarged crops. Needs a display for captures (headless: telemetry only).
# Usage: bash work/run021/check.sh archer-repro --script res://tools/art/run021/archer_repro.gd
extends SceneTree
const OUT := "res://work/run021/archer/"
var level: Node2D
var log_file: FileAccess
var checks := 0
var failures := 0
var headless := false
var capture_budget := 0

func _initialize() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1

func frames(count: int) -> void:
	for i in count: await physics_frame

func art_of(a: Node) -> AnimatedSprite2D: return a.get_node_or_null("Art")

func row(tag: String, n: int, a: Node) -> String:
	var art := art_of(a)
	return "%s,%d,%s,%d,%s,%d,%.3f,%.3f,%s,%s,%s,%.2f,%.3f,%s,%s,%.3f,%.3f" % [tag, n, art.animation, art.frame, str(art.flip_h), a.direction, a.velocity.x, a.velocity.y, str(a.is_on_floor()), str(a.aggro), String(a.pending_attack), a.knockback_time, a.windup_time, str(art.is_playing()), str(art.speed_scale), a.global_position.x, a.global_position.y]

func shot(tag: String, a: Node, scale_up: int = 6) -> void:
	if headless: return
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	var base := ProjectSettings.globalize_path(OUT)
	img.save_png(base + tag + "_native.png")
	var sp: Vector2 = level.get_viewport().get_canvas_transform() * a.global_position
	var r := Rect2i(int(sp.x) - 32, int(sp.y) - 40, 64, 48).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	var crop := img.get_region(r)
	crop.resize(crop.get_width() * scale_up, crop.get_height() * scale_up, Image.INTERPOLATE_NEAREST)
	crop.save_png(base + tag + "_crop.png")

# Run `count` physics frames, log each, return summary stats.
func observe(tag: String, a: Node, count: int, snap_every: int = 0) -> Dictionary:
	var stats := {"flip_changes": 0, "anim_changes": 0, "walk_idle_switches": 0, "dir_changes": 0, "vx_sign_changes": 0, "frames": 0}
	var prev_flip: bool = art_of(a).flip_h
	var prev_anim: StringName = art_of(a).animation
	var prev_dir: int = a.direction
	var prev_sign: int = signi(int(sign(a.velocity.x)))
	log_file.store_line("# scenario " + tag)
	for n in count:
		await physics_frame
		await process_frame
		if not is_instance_valid(a): break
		var art := art_of(a)
		log_file.store_line(row(tag, n, a))
		stats.frames += 1
		if art.flip_h != prev_flip: stats.flip_changes += 1
		if a.direction != prev_dir: stats.dir_changes += 1
		var s := int(sign(a.velocity.x))
		if s != 0 and prev_sign != 0 and s != prev_sign: stats.vx_sign_changes += 1
		if s != 0: prev_sign = s
		if art.animation != prev_anim:
			stats.anim_changes += 1
			if art.animation in [&"walk", &"idle"] and prev_anim in [&"walk", &"idle"]: stats.walk_idle_switches += 1
			log_file.store_line("# anim %s -> %s at %d" % [prev_anim, art.animation, n])
		prev_flip = art.flip_h
		prev_anim = art.animation
		prev_dir = a.direction
		if snap_every > 0 and n % snap_every == 0 and capture_budget > 0:
			capture_budget -= 1
			await shot("%s_f%03d" % [tag, n], a)
	print("STATS ", tag, " ", stats)
	return stats

func load_level(path: String) -> void:
	if level != null:
		level.queue_free()
		await frames(2)
	level = load(path).instantiate()
	root.add_child(level)
	current_scene = level
	await frames(4)

func archers() -> Array:
	var result := []
	for e in get_nodes_in_group("enemies"):
		if e.get("kind") == 2: result.append(e)
	return result

func park_player(a: Node, offset: Vector2, frozen: bool) -> void:
	var p = level.player
	p.position = a.position + offset
	p.velocity = Vector2.ZERO
	p.health_units = p.max_health_units
	p.set_physics_process(not frozen)
	level.camera.reset_smoothing()

func run() -> void:
	headless = DisplayServer.get_name() == "headless"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	log_file = FileAccess.open(OUT + "telemetry.csv", FileAccess.WRITE)
	log_file.store_line("tag,n,anim,frame,flip_h,direction,vx,vy,on_floor,aggro,pending_attack,knockback,windup_time,playing,speed_scale,x,y")
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	capture_budget = 60
	print("INFO display=", DisplayServer.get_name())

	# ---- A: production archers, player parked far above (no aggro), natural behaviour
	for lv in ["res://scenes/black_forrest.tscn", "res://scenes/forbidden_graveyard.tscn"]:
		await load_level(lv)
		var list := archers()
		print("INFO ", lv, " archers=", list.size())
		for a in list:
			print("INFO archer ", a.name, " pos=", a.position, " patrol=", a.patrol_left, "..", a.patrol_right, " origin_x=", a.origin_x)
		var tagbase: String = lv.get_file().get_basename().substr(0, 3)
		for a in list:
			park_player(a, Vector2(0, -600), true)
			await frames(30)
			var st: Dictionary = await observe("A_%s_%s_idlepatrol" % [tagbase, a.name], a, 150, 15)
			check(st.frames > 0, "A observed " + String(a.name))
		if lv.ends_with("black_forrest.tscn"):
			# ---- B: aggro, windup, shoot, hit, resume (first black_forrest archer)
			var a = list[0]
			park_player(a, Vector2(-100, 0), false)
			await frames(5)
			await observe("B_aggro_shoot", a, 240, 10)
			# ---- C: direct damage during several states
			a.cooldown = 0.0
			await frames(2)
			await observe("C_hit_walk_before", a, 20)
			a.take_damage(0.5, Vector2(-100.0, -50.0))
			await observe("C_hit_walk_after", a, 40, 3)
			# hit during windup
			a.knockback_time = 0.0
			a.cooldown = 0.0
			park_player(a, Vector2(-100, 0), false)
			var guard := 0
			while a.pending_attack == &"" and guard < 200:
				await physics_frame
				guard += 1
			print("INFO windup reached after ", guard, " frames pending=", a.pending_attack, " hp_units=", a.health_units)
			await frames(3)
			if a.health_units > 1: a.take_damage(0.5, Vector2(100.0, -50.0))
			await observe("C_hit_after_windup", a, 60, 3)
			# resume walking: lose aggro (park far) and watch
			park_player(a, Vector2(0, -600), true)
			await observe("C_resume_after_aggro_loss", a, 300, 30)

	# ---- D: synthetic archer with real patrol bounds in black_forrest context (turnaround, edge)
	await load_level("res://scenes/black_forrest.tscn")
	var ref: Node = archers()[0]
	var scene: PackedScene = load("res://scenes/skeleton_archer.tscn")
	var s = scene.instantiate()
	s.patrol_left = -40.0
	s.patrol_right = 40.0
	s.position = ref.position
	ref.get_parent().add_child(s)
	ref.process_mode = Node.PROCESS_MODE_DISABLED
	ref.hide()
	park_player(s, Vector2(0, -600), true)
	await frames(10)
	capture_budget = 20
	await observe("D_synthetic_patrol_pm40", s, 420, 20)

	log_file.close()
	print("RESULT checks=%d failures=%d" % [checks, failures])
	quit(1 if failures > 0 else 0)

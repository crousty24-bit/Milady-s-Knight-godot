# Native N3 authored Archer fixture on unchanged terrain;
# initial player poses are injected and other enemies removed for isolation.
extends SceneTree
var checks := 0
var failures := 0
var level: Node2D
var enemy: CharacterBody2D
var captures := "res://work/run021/pursuit-fixes"
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ",label)
func capture(label: String) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	check(image.get_size() == Vector2i(640,360), "actual viewport640x360")
	check(image.save_png(captures + "/" + label + ".png") == OK, "native N3 capture " + label)
func stop_audio(node: Node) -> void:
	if node is AudioStreamPlayer or node is AudioStreamPlayer2D: node.stop()
	for child in node.get_children(): stop_audio(child)
func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(captures))
	var store := root.get_node("Progression")
	store.persistence_enabled = false
	store.resume_scene = "res://scenes/black_forrest.tscn"
	level = load(store.resume_scene).instantiate()
	root.add_child(level)
	current_scene = level
	level.player.controls_enabled = false
	level.player.set_physics_process(false)
	enemy = level.get_node("Enemies/Enemy05")
	var at := enemy.global_position
	print("FIXTURE actual N3 Enemy05=",enemy.get_script().resource_path," pose=",at,"; unchanged authored terrain")
	for other in level.get_node("Enemies").get_children():
		if other != enemy: other.queue_free()
	await frames(2)
	level.player.global_position = at + Vector2(-35,0)
	await frames(3)
	check(enemy.is_on_floor(), "production Archer rests on authored Enemy05 platform")
	check(enemy.aggro, "Archer acquires nearby player with normal perception")
	var ray := PhysicsRayQueryParameters2D.create(at + Vector2(0,24),at + Vector2(0,180),1)
	var support := enemy.get_world_2d().direct_space_state.intersect_ray(ray)
	print("OBSERVATION lower support=",support)
	check(not support.is_empty(), "unchanged N3 terrain has lower supporting floor")
	if not support.is_empty():
		level.player.global_position = support.position + Vector2(0,-0.08)
		var start: float = enemy.global_position.x
		var flips := 0
		var direction: int = enemy.direction
		var maximum_speed := 0.0
		for i in range(75):
			await frames(1)
			if enemy.direction != direction: flips += 1
			direction = enemy.direction
			maximum_speed = maxf(maximum_speed,absf(enemy.velocity.x))
		print("OBSERVATION real N3 lower target=",level.player.global_position," Archer=",enemy.global_position," flips=",flips," speed=",maximum_speed," retained=",enemy.aggro)
		check(flips == 0 and maximum_speed < 0.1 and absf(enemy.global_position.x-start) < 0.1, "N3 Archer stays stable while player is directly underneath")
		check(enemy.aggro, "N3 underneath pose retains normal aggro grace")
		var cam: Camera2D = level.camera
		cam.top_level = true
		cam.position_smoothing_enabled = false
		cam.limit_left = -100000
		cam.limit_right = 100000
		cam.limit_top = -100000
		cam.limit_bottom = 100000
		cam.global_position = at + Vector2(40,-20)
		cam.reset_smoothing()
		cam.force_update_scroll()
		await capture("n3-archer-player-below")
		level.player.global_position.x += 80.0
		await frames(20)
		check(enemy.direction == 1 and enemy.global_position.x > start + 2.0, "N3 Archer resumes pursuit when lower player moves right")
		await capture("n3-archer-pursuit-resumes")
	# Above pose has no reachable supporting platform in this fixture: inspect
	# the in-air perception/facing, without claiming actual player traversal.
	level.player.global_position = enemy.global_position + Vector2(0,-48)
	var above_flips := 0
	var facing: int = enemy.direction
	for i in range(30):
		await frames(1)
		if enemy.direction != facing: above_flips += 1
		facing = enemy.direction
	check(above_flips <= 1, "N3 Archer facing stays stable for injected airborne player above")
	await capture("n3-archer-player-above-fixture")
	stop_audio(level)
	OS.delay_msec(300)
	level.queue_free()
	await frames(3)
	print("RESULT %d N3 pursuit native fixture checks; %d failures" % [checks,failures])
	quit(1 if failures else 0)

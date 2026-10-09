extends SceneTree
var checks := 0
var failures := 0
var room: Node2D
var player: SlicePlayer
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func solid(at: Vector2, size: Vector2) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.position = at
	body.collision_layer = 1
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	body.add_child(shape)
	room.add_child(body)
	return body
func fixture(at := Vector2(220, 200)) -> void:
	if is_instance_valid(room):
		paused = true
		for voice_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for voice in room.find_children("*", voice_type, true, false): voice.stop()
		OS.delay_msec(300)
		room.queue_free()
		await frames(2)
	paused = false
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	solid(Vector2(250, 208), Vector2(600, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = at
	room.add_child(player)
	player.controls_enabled = false
	player.set_physics_process(false)
	await frames(2)
func mob(scene: String):
	var enemy = load("res://scenes/" + scene + ".tscn").instantiate()
	enemy.position = Vector2(100, 200)
	room.add_child(enemy)
	return enemy
func alignment(scene: String, above: bool) -> void:
	await fixture(Vector2(100, 200))
	var enemy = mob(scene)
	enemy.cooldown = 30.0
	await frames(3)
	# Acquire aggro on common ground, then separate on real solid platforms.
	player.position = Vector2(enemy.position.x, 136 if above else 264)
	solid(Vector2(enemy.position.x, 144 if above else 272), Vector2(300, 16))
	var x: float = enemy.position.x
	var flips := 0
	var previous_dir: int = enemy.direction
	var maximum_speed := 0.0
	for i in range(90):
		await frames(1)
		if enemy.direction != previous_dir: flips += 1
		previous_dir = enemy.direction
		maximum_speed = maxf(maximum_speed, absf(enemy.velocity.x))
	print("OBSERVATION ", scene, " above=", above, " flips=", flips, " dx=", enemy.position.x - x, " speed=", maximum_speed, " aggro=", enemy.aggro)
	check(flips <= 1, scene + " aligned " + ("above" if above else "below") + " target does not flip every frame")
	check(absf(enemy.position.x - x) < 1.0 and maximum_speed < 0.1, scene + " does not walk in place when vertical path is unavailable")
	check(enemy.aggro, scene + " preserves two-second retained aggro grace")
	await frames(45)
	check(not enemy.aggro, scene + " blocked alignment loses aggro after normal grace")
func resume_and_airborne(scene: String) -> void:
	for offset in [-1.0, 1.0]:
		await fixture(Vector2(100, 200))
		var enemy = mob(scene)
		enemy.cooldown = 30.0
		await frames(3)
		player.position = Vector2(enemy.position.x + offset, 264)
		await frames(20)
		check(absf(enemy.velocity.x) < 0.1, scene + " stays still for sub-step alignment " + str(offset))
		var start: float = enemy.position.x
		player.position.x = start + offset * 80.0
		await frames(20)
		check((enemy.position.x - start) * offset > 3.0 and enemy.direction == int(offset), scene + " resumes actual chase when lower target moves " + str(offset))
	await fixture(Vector2(220, 200))
	var enemy = mob(scene)
	enemy.cooldown = 30.0
	await frames(3)
	player.position = Vector2(enemy.position.x, 264)
	enemy.velocity.y = -200.0
	var start: float = enemy.position.x
	var launch_direction: int = enemy.direction
	await frames(8)
	check(not enemy.is_on_floor() and (enemy.position.x - start) * launch_direction > 1.0, scene + " aligned airborne chase keeps horizontal jump momentum")
	check(enemy.direction == launch_direction, scene + " aligned airborne target preserves facing")
func aligned_roof(scene: String) -> void:
	await fixture(Vector2(220,200))
	var enemy = mob(scene)
	await frames(3)
	check(enemy.aggro, scene + " acquires before aligned roof fixture")
	enemy.position = Vector2(180,200)
	solid(Vector2(180,144),Vector2(80,16))
	player.position = Vector2(180,136)
	var detour_started := false
	var roof_landed := false
	for i in range(420):
		await frames(1)
		detour_started = detour_started or enemy.chase_detour_dir != 0
		roof_landed = roof_landed or (enemy.is_on_floor() and absf(enemy.position.y - 136.0) < 1.0)
		if roof_landed and absf(enemy.position.x-player.position.x) <= enemy.melee_range: break
	print("OBSERVATION aligned roof ",scene," enemy=",enemy.position," detour=",detour_started," landed=",roof_landed," aggro=",enemy.aggro)
	check(detour_started, scene + " starts verified retreat for horizontally aligned upper target")
	check(roof_landed, scene + " physically climbs reachable roof for aligned target")
	check(enemy.aggro, scene + " preserves aggro across verified aligned roof progress")
	# A ranged Archer may shoot the lower target from verified roof support;
	# the other profiles follow it back down without a forced movement state.
	player.position = Vector2(300,200)
	if scene == "skeleton_archer":
		await frames(180)
		check(enemy.is_on_floor() and enemy.aggro and absf(enemy.velocity.x) < 0.1 and enemy.active_attacks.size() > 0, scene + " resumes grounded shooting at visible lower target within range")
		return
	for i in range(420):
		await frames(1)
		if enemy.is_on_floor() and enemy.position.y > 199.0 and enemy.position.x > 230.0: break
	check(enemy.is_on_floor() and enemy.position.y > 199.0 and enemy.position.x > 230.0, scene + " returns to lower floor after aligned roof pursuit")
func run() -> void:
	for scene in ["skeleton_archer", "skeleton_warrior", "blight_sorcerer", "bloated_slime", "chud_blob"]:
		await alignment(scene, false)
		await alignment(scene, true)
		await resume_and_airborne(scene)
		await aligned_roof(scene)
	paused = true
	for voice_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for voice in room.find_children("*", voice_type, true, false): voice.stop()
	OS.delay_msec(300)
	room.queue_free()
	await frames(3)
	print("RESULT %d vertical pursuit checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

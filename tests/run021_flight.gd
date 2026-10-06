extends SceneTree
var checks := 0
var failures := 0
var room: Node2D
var player: SlicePlayer
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for _i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func solid(at: Vector2, size: Vector2) -> void:
	var body := StaticBody2D.new()
	body.position = at
	body.collision_layer = 1
	var collision := CollisionShape2D.new()
	collision.shape = RectangleShape2D.new()
	collision.shape.size = size
	body.add_child(collision)
	room.add_child(body)
func cleanup() -> void:
	if not is_instance_valid(room): return
	paused = true
	for type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for voice in room.find_children("*", type, true, false): voice.stop()
	OS.delay_msec(300)
	room.queue_free()
	await frames(3)
	paused = false
func fixture() -> CharacterBody2D:
	await cleanup()
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	solid(Vector2(200, 208), Vector2(600, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(300, 200)
	room.add_child(player)
	player.controls_enabled = false
	await frames(5)
	player.set_physics_process(false)
	var skull := load("res://scenes/possessed_skull.tscn").instantiate() as CharacterBody2D
	skull.position = Vector2(100, 188)
	room.add_child(skull)
	return skull
func run() -> void:
	var skull := await fixture()
	solid(Vector2(180, 184), Vector2(16, 32))
	var highest := skull.position.y
	var passed_above := false
	for _tick in 360:
		await frames(1)
		highest = minf(highest, skull.position.y)
		if skull.position.x > 195: passed_above = true
		if player.health_units < 30: break
	check(passed_above and highest < 162, "skull climbs above a solid block and passes it physically")
	check(player.health_units == 25, "skull resumes pursuit and deals its unchanged contact damage after detour")
	check(skull.collision_mask == 1, "flight keeps solid terrain collisions enabled")
	skull = await fixture()
	# A low ceiling forces a lower bypass; keep 14px of room under the wall.
	solid(Vector2(200, 140), Vector2(600, 16))
	solid(Vector2(180, 167), Vector2(16, 38))
	var lowest := skull.position.y
	for _tick in 400:
		await frames(1)
		lowest = maxf(lowest, skull.position.y)
		if player.health_units < 30: break
	check(skull.position.x > 195 and lowest > 191, "skull takes the lower physical bypass when the upper side is blocked")
	check(player.health_units == 25, "lower bypass reaches the player without terrain phasing")
	skull = await fixture()
	player.position = Vector2(200, 200)
	skull.position = Vector2(200, 100)
	solid(Vector2(200, 150), Vector2(80, 16))
	var passed_side := false
	var furthest_side := 0.0
	for _tick in 500:
		await frames(1)
		furthest_side = maxf(furthest_side, absf(skull.position.x - 200))
		if absf(skull.position.x - 200) > 40: passed_side = true
		if player.health_units < 30: break
	print("OBSERVATION platform skull=", skull.position, " side=", furthest_side, " hp=", player.health_units)
	check(passed_side and skull.position.y > 180, "skull bypasses a horizontal platform toward a vertically aligned target")
	check(player.health_units == 25, "platform bypass resumes unchanged contact attack")
	skull = await fixture()
	solid(Vector2(180, 184), Vector2(16, 32))
	await frames(20)
	paused = true
	var held: Vector2 = skull.position
	await frames(20)
	check(skull.position == held, "pause freezes obstacle flight pursuit")
	paused = false
	player.dead = true
	await frames(20)
	check(skull.position == held, "dead target stops pursuit without changing swarm ownership")
	await cleanup()
	print("RESULT %d flight checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

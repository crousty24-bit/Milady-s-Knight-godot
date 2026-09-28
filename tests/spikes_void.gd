extends SceneTree
var checks := 0
var failures := 0
var room: Node2D
var deaths := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func clear_room() -> void:
	if is_instance_valid(room):
		room.queue_free()
		await frames(3)
func run() -> void:
	for angle in [0.0, PI / 2.0, PI, -PI / 2.0]:
		await clear_room()
		room = Node2D.new()
		root.add_child(room)
		current_scene = room
		var spikes = load("res://scenes/spikes.tscn").instantiate()
		spikes.position = Vector2(200, 180)
		spikes.rotation = angle
		room.add_child(spikes)
		var player: SlicePlayer = load("res://scenes/player.tscn").instantiate()
		var normal := Vector2.UP.rotated(angle)
		player.position = spikes.position + normal * 60.0 + Vector2(0, 9)
		room.add_child(player)
		player.set_physics_process(false)
		player.attack_time = 0.20
		await frames(3)
		var blocked := false
		for i in range(30):
			var hit := player.move_and_collide(-normal * 3.0)
			blocked = blocked or hit != null
			await frames(1)
			if blocked: break
		await frames(2)
		check(blocked, "solid surface blocks approach, rotation %.2f" % angle)
		check(player.health_units == 25 and player.invulnerability == player.INVULNERABILITY_DURATION, "physical contact removes 0.5 HP, rotation %.2f" % angle)
		check(player.hit_stun_time == 0.0 and player.attack_time == 0.20 and not player.attack_cancelled, "contact preserves attack without hit-stun, rotation %.2f" % angle)
		check(player.knockback_time > 0.0 and player.velocity.dot(normal) > 170.0, "recoil points away from surface, rotation %.2f" % angle)
		await frames(80)
		check(player.health_units == 25, "repeated overlap respects protection, rotation %.2f" % angle)
		player.invulnerability = 0.0
		await frames(2)
		check(player.health_units == 20, "overlap damages again when protection is absent, rotation %.2f" % angle)
		check(spikes.collision_layer == 1 and spikes.get_node("Contact").collision_mask == 2, "spikes are solid terrain but not grippable, rotation %.2f" % angle)
		# The actual wall-state probes must ignore the new solid surface.
		player._update_wall_state(0.0)
		check(player.wall_normal == 0.0, "wall probes ignore spikes, rotation %.2f" % angle)

	await clear_room()
	room = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(room)
	current_scene = room
	var player: SlicePlayer = room.get_node("Player")
	await frames(4)
	deaths = 0
	player.died.connect(func(): deaths += 1)
	# Real falling body: changing the level limit permits a fall below the old global 340.
	room.void_y = 500.0
	player.position = Vector2(880, 350)
	player.velocity = Vector2.ZERO
	player.invulnerability = 5.0
	await frames(5)
	check(not player.dead and player.position.y > 340.0, "level can place void below old global threshold")
	paused = true
	room.paused = true
	room.void_y = 300.0
	await frames(3)
	check(not player.dead, "paused level does not apply void death")
	paused = false
	room.paused = false
	await frames(2)
	check(player.dead and deaths == 1 and player.health_units == 0, "crossing configured level limit kills through protection")
	await frames(10)
	check(deaths == 1, "continued fall emits death only once")
	await clear_room()
	room = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(room)
	current_scene = room
	player = room.get_node("Player")
	await frames(4)
	check(room.void_y == 304.0 and room.get_node_or_null("Hazards/Pit") == null, "slice keeps old effective pit limit with a single level-owned boundary")
	check(room.get_node("Hazards/Thorns0") is Area2D and room.get_node("Hazards/Thorns1") is Area2D, "existing thorns remain in use")
	# Real gravity lands on the floor spikes and applies the damage profile.
	player.position = Vector2(1120, 180)
	player.velocity = Vector2.ZERO
	player.controls_enabled = false
	var reached := false
	for i in range(30):
		await frames(1)
		if player.health_units < 30:
			reached = true
			break
	check(reached and player.health_units == 25 and player.knockback_time > 0.0 and player.position.y < 224.0, "authored floor spikes damage and repel actual falling player")
	await clear_room()
	OS.delay_msec(200)
	print("RESULT ", checks, " spikes and void checks; ", failures, " failures")
	quit(failures)

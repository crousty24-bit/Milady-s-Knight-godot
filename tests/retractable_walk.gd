extends SceneTree
var checks := 0
var failures := 0
var room: Node2D

func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func reset() -> void:
	if is_instance_valid(room):
		room.queue_free()
		await frames()
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
func spikes_at(at: Vector2, warning: bool = false) -> StaticBody2D:
	var spikes: StaticBody2D = load("res://scenes/retractable_spikes.tscn").instantiate()
	spikes.position = at
	spikes.safe_duration = 30.0
	spikes.warning_duration = 10.0
	spikes.initial_phase = 30.1 if warning else 0.0
	room.add_child(spikes)
	spikes.set_physics_process(false)
	return spikes
func player_at(at: Vector2) -> SlicePlayer:
	var player: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	player.position = at
	room.add_child(player)
	return player

func run() -> void:
	# Use the actual player, gravity, floor contact and directional input: no jump.
	for warning in [false, true]:
		for direction in [-1, 1]:
			await reset()
			var ground := StaticBody2D.new()
			var collision := CollisionShape2D.new()
			var shape := RectangleShape2D.new()
			shape.size = Vector2(300, 32)
			collision.shape = shape
			ground.position = Vector2(200, 216)
			ground.add_child(collision)
			room.add_child(ground)
			spikes_at(Vector2(200, 200), warning)
			var player := player_at(Vector2(200 - direction * 60, 200))
			await frames(8)
			var start_y := player.position.y
			var action := "move_right" if direction == 1 else "move_left"
			Input.action_press(action)
			await frames(55)
			Input.action_release(action)
			var phase_name := "WARNING" if warning else "RETRACTED"
			check((player.position.x - 200) * direction > 25, "%s walk direction %d crosses spikes without jump (x=%.2f)" % [phase_name, direction, player.position.x])
			check(player.is_on_floor() and absf(player.position.y - start_y) < 0.2 and player.health_units == 30, "%s walking stays on ground without damage direction %d" % [phase_name, direction])
	# The base must still support a player when there is no terrain below it.
	for angle in [0.0, PI / 2.0, PI, -PI / 2.0]:
		for warning in [false, true]:
			await reset()
			var spikes := spikes_at(Vector2(200, 200), warning)
			spikes.rotation = angle
			var normal := Vector2.UP.rotated(angle)
			var player := player_at(spikes.position + normal * 55 + Vector2(0, 9))
			player.set_physics_process(false)
			await frames()
			var hit: KinematicCollision2D
			for i in 30:
				hit = player.move_and_collide(-normal * 3)
				if hit != null: break
				await frames(1)
			check(hit != null and hit.get_collider() == spikes and not spikes.get_node("Solid").disabled, "suspended base retains physical support rotation %.2f warning %s" % [angle, warning])
			check(player.health_units == 30 and spikes.get_node("Points").disabled, "suspended base stays safe rotation %.2f warning %s" % [angle, warning])
	await reset()
	room.queue_free()
	await frames()
	OS.delay_msec(300)
	print("RESULT %d checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

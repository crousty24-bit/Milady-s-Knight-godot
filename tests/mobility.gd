# Isolated physical room. Only setup teleports; actions exercise the real controller.
extends SceneTree
var failures := 0
var checks := 0
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
func solid(pos: Vector2, size: Vector2, grippable: bool = true) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 9 if grippable else 1
	body.position = pos
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	body.add_child(shape)
	room.add_child(body)
func spawn(pos := Vector2(100, 200)) -> void:
	for action in ["jump", "attack", "move_left", "move_right"]: Input.action_release(action)
	if is_instance_valid(room):
		room.queue_free()
		await frames(2)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	solid(Vector2(150, 208), Vector2(600, 16))
	solid(Vector2(208, 80), Vector2(16, 240))
	solid(Vector2(144, 80), Vector2(16, 240))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = pos
	room.add_child(player)
	await frames(3)
func press(action: String, count := 2) -> void:
	Input.action_press(action)
	await frames(count)
func release(action: String, count := 2) -> void:
	Input.action_release(action)
	await frames(count)
func run() -> void:
	await spawn()
	await press("jump", 21)
	await release("jump")
	await press("jump")
	check(player.velocity.y < -190 and not player.can_double_jump, "double jump gives distinct second impulse")
	check(player.jump_flash > 0 and player.get_node("JumpSound").pitch_scale > 1.0, "double jump has visual and sound feedback")
	await press("attack")
	check(player.attack_time > 0, "attack during double jump")
	await release("jump")
	var before := player.velocity.y
	await press("jump")
	check(player.velocity.y > before, "third jump refused")
	await release("jump", 80)
	check(player.is_on_floor(), "double jump lands on actual floor")
	await press("jump")
	check(player.can_double_jump, "landing restores double jump after next ground jump")
	await spawn()
	await press("jump", 85)
	check(player.is_on_floor() and not player.can_double_jump, "holding jump never auto-repeats or auto-doubles")
	await spawn(Vector2(100, 80))
	await press("jump")
	check(player.velocity.y > 0, "falling without a ground jump gives no free aerial jump")
	await press("attack")
	check(player.attack_time > 0, "attack during ordinary fall")
	await spawn(Vector2(194.92, 40))
	player.velocity.y = 100
	await frames(5)
	var y := player.position.y
	await frames(12)
	check(player.motion_state == SlicePlayer.MotionState.WALL_SLIDE and player.position.y > y and player.velocity.y <= 35.01, "wall slide descends automatically without direction input")
	await press("attack")
	check(player.attack_time == 0, "attack cannot start on wall slide")
	await press("jump")
	check(player.velocity.x < -80 and player.velocity.y < 0 and player.wall_jump_lockout, "wall jump pushes up and away")
	await release("attack")
	await press("attack")
	check(player.attack_time > 0, "attack allowed after leaving wall")
	await release("jump", 3)
	before = player.velocity.y
	await press("jump")
	check(player.velocity.y > before and not player.can_double_jump, "unused double jump forbidden after wall jump")
	await release("jump")
	await press("move_right")
	var reached := false
	for i in range(100):
		await frames(1)
		if player.wall_normal < 0 and player.wall_detach_time <= 0:
			reached = true
			break
	await press("jump")
	check(reached and player.velocity.x < -80 and player.velocity.y < 0, "same-wall repeat permitted after separation")
	check(player.wall_jump_lockout and not player.can_double_jump, "same-wall chain never restores aerial charge")
	await release("jump")
	Input.action_release("move_right")
	# Force a long fall in the same attempt to isolate reset semantics.
	player.position = Vector2(100, -100)
	player.velocity = Vector2(0, 50)
	await frames(15)
	before = player.velocity.y
	await press("jump")
	check(player.velocity.y >= before and player.wall_jump_lockout, "long fall preserves wall-jump lockout")
	await release("jump", 100)
	await press("jump")
	check(player.can_double_jump and not player.wall_jump_lockout, "actual floor restores charge after wall chain")
	await spawn(Vector2(194.92, 80))
	await press("jump")
	await release("jump")
	Input.action_press("move_left")
	reached = false
	for i in range(60):
		await frames(1)
		if player.wall_normal > 0:
			reached = true
			break
	await press("jump")
	check(reached and player.velocity.x > 80 and player.wall_jump_lockout and not player.can_double_jump, "opposite-wall jump keeps double jump forbidden")
	await spawn(Vector2(194.92, 40))
	player.position.x = 185
	player.velocity.y = 60
	await press("attack")
	await press("move_right", 8)
	check(player.motion_state == SlicePlayer.MotionState.WALL_SLIDE and player.attack_cancelled and player.attack_time > 0, "entering wall slide cancels hit window but keeps recovery")
	await release("move_right")
	await press("move_left", 6)
	check(player.motion_state == SlicePlayer.MotionState.AIR, "away direction detaches promptly")
	await spawn(Vector2(100, 80))
	solid(Vector2(108, 60), Vector2(6, 200), false)
	Input.action_press("move_right")
	await frames(10)
	check(player.wall_normal == 0 and player.motion_state != SlicePlayer.MotionState.WALL_SLIDE, "smooth surfaces cannot be used to climb gate or limits")
	await spawn()
	await press("jump", 21)
	await release("jump")
	await press("jump")
	await release("jump")
	player.position = Vector2(194.92, 80)
	player.velocity = Vector2(0, 50)
	await frames(3)
	await press("jump")
	check(player.wall_jump_lockout and not player.can_double_jump and player.velocity.x < -80, "wall jump after a consumed double jump also keeps charge locked")
	await release("jump")
	player.position = Vector2(100, 120)
	player.velocity = Vector2(0, -255)
	solid(Vector2(100, 72), Vector2(50, 16))
	var hit_ceiling := false
	for i in range(18):
		await frames(1)
		hit_ceiling = hit_ceiling or player.is_on_ceiling()
	check(hit_ceiling and player.wall_jump_lockout, "ceiling contact does not count as landing")
	before = player.velocity.y
	await press("jump")
	check(player.velocity.y >= before and not player.can_double_jump, "head collision cannot restore aerial jump")
	for action in ["jump", "attack", "move_left", "move_right"]: Input.action_release(action)
	room.queue_free()
	await frames(3)
	print("RESULT ", checks, " mobility checks; ", failures, " failures")
	OS.delay_msec(300)
	quit(failures)

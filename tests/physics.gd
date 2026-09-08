extends SceneTree
var failures: int = 0
var level: Node2D
var player: SlicePlayer
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await physics_frame
func check(ok: bool, message: String) -> void:
	print("PASS " if ok else "FAIL ",message)
	if not ok: failures+=1
func reset_position() -> void:
	Input.action_release("jump")
	player.position=Vector2(48,140)
	player.velocity=Vector2.ZERO
	await frames(10)
func jump_height(hold: int) -> float:
	await reset_position()
	var top: float = player.position.y
	Input.action_press("jump")
	for i in range(50):
		if i==hold: Input.action_release("jump")
		await frames(1)
		top=minf(top,player.position.y)
	return 144.0-top
func run() -> void:
	level=load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene=level
	player=level.get_node("Player")
	await frames(10)
	var short_height: float = await jump_height(3)
	var long_height: float = await jump_height(30)
	check(long_height>short_height+15.0,"held jump is substantially higher: short=%.1f long=%.1f"%[short_height,long_height])
	await reset_position()
	Input.action_press("jump")
	await frames(5)
	Input.action_press("attack")
	await frames(3)
	check(player.attack_time>0 and not player.is_on_floor(),"sword can start while airborne")
	Input.action_release("attack")
	Input.action_release("jump")
	await reset_position()
	# Trigger jump while falling just above the floor.
	player.position=Vector2(48,137)
	player.velocity=Vector2(0,110)
	await frames(1)
	Input.action_press("jump")
	await frames(7)
	check(player.velocity.y<0,"jump buffer fires after landing")
	Input.action_release("jump")
	await reset_position()
	player.position=Vector2(476,144)
	Input.action_press("move_right")
	await frames(7)
	Input.action_release("move_right")
	Input.action_press("jump")
	await frames(2)
	check(player.velocity.y<0,"coyote jump works after leaving a ledge")
	Input.action_release("jump")
	# Ride the actual moving AnimatableBody2D, without input correction.
	var ferry=level.get_node("Platforms/Ferry")
	player.position=ferry.position+Vector2(0,-4)
	player.velocity=Vector2.ZERO
	await frames(8)
	var offset: float = player.position.x-ferry.position.x
	await frames(35)
	check(player.is_on_floor() and absf(player.position.x-ferry.position.x-offset)<2.0,"moving platform carries player without sliding off")
	# Hurt collider and visual thorns occupy the same authored region.
	player.invulnerability=0
	player.position=Vector2(1032,219)
	player.velocity=Vector2.ZERO
	await frames(5)
	check(player.health==2,"actual thorn overlap removes one HP")
	level.queue_free()
	await process_frame
	OS.delay_msec(150)
	quit(failures)

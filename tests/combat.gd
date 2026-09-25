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
func spawn() -> void:
	Input.action_release("attack")
	if is_instance_valid(room):
		room.queue_free()
		await frames(2)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	wall(Vector2(160, 208), Vector2(320, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(160, 200)
	room.add_child(player)
	await frames(4)
func wall(pos: Vector2, size: Vector2) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.position = pos
	var collider := CollisionShape2D.new()
	collider.shape = RectangleShape2D.new()
	collider.shape.size = size
	body.add_child(collider)
	room.add_child(body)
func slime(pos: Vector2, purple := false, moving := false) -> SliceSlime:
	var enemy: SliceSlime = load("res://scenes/slime.tscn").instantiate()
	enemy.variant = SliceSlime.Kind.PURPLE if purple else SliceSlime.Kind.GREEN
	enemy.position = pos
	enemy.patrol_left = 0
	enemy.patrol_right = 0
	room.add_child(enemy)
	enemy.set_physics_process(moving)
	return enemy
func swing() -> void:
	Input.action_press("attack")
	await frames(14)
	Input.action_release("attack")
	await frames(10)
func run() -> void:
	for purple in [false, true]:
		await spawn()
		var enemy := slime(Vector2(182, 200), purple)
		await frames(3)
		var hits: int = 4 if purple else 3
		for i in range(hits):
			await swing()
			if i < hits - 1:
				check(is_instance_valid(enemy) and enemy.health == hits - i - 1 and not enemy.dead, "%s swing %d deals exactly one damage" % ["Purple" if purple else "Green", i + 1])
			else:
				check(not is_instance_valid(enemy) or enemy.dead, "%s dies on exactly strike %d" % ["Purple" if purple else "Green", hits])
		await frames(20)
		check(not is_instance_valid(enemy), "dead slime is removed after feedback")
	await spawn()
	player.facing = -1
	var left := slime(Vector2(138, 200))
	await frames(3)
	await swing()
	check(left.health == 2, "mirrored sword hits on left")
	await spawn()
	var far := slime(Vector2(200, 200))
	await frames(3)
	await swing()
	check(far.health == 3, "sword cannot hit beyond visible reach")
	await spawn()
	var behind := slime(Vector2(182, 200))
	wall(Vector2(172, 175), Vector2(2, 50))
	await frames(3)
	await swing()
	check(behind.health == 3, "solid wall occludes sword damage")
	await spawn()
	var first := slime(Vector2(181, 200))
	var second := slime(Vector2(186, 200), true)
	await frames(3)
	await swing()
	check(first.health == 2 and second.health == 3, "one swing hits each nearby enemy once")
	await spawn()
	var right_enemy := slime(Vector2(181, 200))
	var left_enemy := slime(Vector2(139, 200))
	Input.action_press("attack")
	await frames(7)
	Input.action_press("move_left")
	await frames(7)
	Input.action_release("move_left")
	check(right_enemy.health == 2 and left_enemy.health == 3 and player.facing == -1 and player.attack_facing == 1, "turning during a held attack cannot hit both sides in one swing")
	await frames(10)
	check(right_enemy.health == 2 and left_enemy.health == 2, "next held swing follows the new facing")
	Input.action_release("attack")
	await spawn()
	var contact := slime(Vector2(174, 200), false, true)
	await frames(6)
	check(player.health == 3, "nearby non-overlapping sprites do not cause contact damage")
	contact.position = Vector2(170, 200)
	await frames(4)
	check(player.health == 2, "credible physical overlap deals one contact damage")
	await frames(8)
	check(player.health == 2, "invulnerability prevents immediate repeated contact damage")
	await spawn()
	var hurt := slime(Vector2(182, 200), false, true)
	Input.action_press("attack")
	for i in range(20):
		await frames(1)
		if hurt.stagger > 0: break
	check(hurt.health == 2 and hurt.stagger > 0 and hurt.sprite.modulate != Color.WHITE, "hit produces visible stagger feedback")
	hurt.position = player.position + Vector2(9, 0)
	await frames(2)
	check(player.health == 3, "freshly struck slime cannot damage attacker during stagger")
	Input.action_release("attack")
	room.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " combat checks; ", failures, " failures")
	quit(failures)

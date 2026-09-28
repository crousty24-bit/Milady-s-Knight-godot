# RUN-007: actual shape queries, inputs, contacts and patrol movement in Godot.
extends SceneTree
var failures := 0
var checks := 0
var room: Node2D
var player: SlicePlayer
var enemy_deaths := 0
var rewards := 0
var impacts: Array[int] = []
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func spawn(pos := Vector2(160, 200)) -> void:
	for action in ["attack", "jump", "move_left", "move_right"]: Input.action_release(action)
	if is_instance_valid(room):
		room.queue_free()
		await frames(2)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	wall(Vector2(160, 208), Vector2(320, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = pos
	room.add_child(player)
	enemy_deaths = 0
	rewards = 0
	impacts.clear()
	await frames(4)
func wall(pos: Vector2, size: Vector2, layer := 1) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = layer
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
	enemy.defeated.connect(func(bonus: int, _at: Vector2): enemy_deaths += 1; rewards += bonus)
	enemy.health_changed.connect(func(_value: float, _maximum: float): impacts.append(Engine.get_physics_frames()))
	return enemy
func swing() -> void:
	Input.action_press("attack")
	await frames(14)
	Input.action_release("attack")
	await frames(47)
func run() -> void:
	for purple in [false, true]:
		await spawn()
		var enemy := slime(Vector2(178, 200), purple)
		await frames(3)
		var hits: int = 4 if purple else 2
		check(enemy.max_health == (2.0 if purple else 1.0), "%s has the N1-4 HP profile" % ["Purple" if purple else "Green"])
		for i in range(hits):
			await swing()
			if i < hits - 1:
				check(is_instance_valid(enemy) and enemy.health == (hits - i - 1) * 0.5 and not enemy.dead, "%s strike %d deals exactly half HP once" % ["Purple" if purple else "Green", i + 1])
			else:
				check(not is_instance_valid(enemy) or enemy.dead, "%s dies on strike %d" % ["Purple" if purple else "Green", hits])
		check(impacts.size() == hits and enemy_deaths == 1 and rewards == 1, "one defeat and one reward across all damage frames")
		check(not is_instance_valid(enemy), "dead slime is removed after feedback")
	await spawn()
	var held := slime(Vector2(178, 200), true)
	await frames(3)
	Input.action_press("attack")
	await frames(200)
	Input.action_release("attack")
	check(impacts.size() == 4 and enemy_deaths == 1, "holding F for several seconds gives four distinct Purple hits")
	var cadence_ok := impacts.size() == 4
	for i in range(1, impacts.size()):
		cadence_ok = cadence_ok and impacts[i] - impacts[i - 1] == 60
	check(cadence_ok, "held Sword impacts are exactly one second apart at 60 Hz")
	await spawn()
	var repress := slime(Vector2(178, 200), true)
	await frames(3)
	Input.action_press("attack")
	await frames(14)
	Input.action_release("attack")
	await frames(8)
	Input.action_press("attack")
	await frames(37)
	check(repress.health == 1.5 and player.attack_time == 0.0, "releasing and repressing F cannot bypass the one-second cooldown")
	await frames(14)
	check(repress.health == 1.0 and impacts.size() == 2 and impacts[1] - impacts[0] == 60, "repressed F resumes at the original cadence")
	await spawn()
	player.facing = -1
	var left := slime(Vector2(142, 200))
	await frames(3)
	await swing()
	check(left.health == 0.5, "mirrored sword hits on left")
	await spawn()
	var shape: RectangleShape2D = player.get_node("AttackArea/Shape").shape
	check(shape.size == Vector2(16, 4), "RANGE 1 uses a 16 px blade collision from hand to tip")
	var near_tip := slime(Vector2(185, 200))
	var past_tip := slime(Vector2(188, 200), true)
	await frames(3)
	await swing()
	check(near_tip.health == 0.5 and past_tip.health == 2.0, "Sword hits an enemy volume inside range but misses one beyond the tip")
	await spawn()
	var far := slime(Vector2(200, 200))
	await frames(3)
	await swing()
	check(far.health == 1.0, "sword cannot hit beyond visible reach")
	await spawn()
	var behind := slime(Vector2(180, 200))
	wall(Vector2(172, 175), Vector2(2, 50))
	await frames(3)
	await swing()
	check(behind.health == 1.0, "solid wall occludes sword damage")
	await spawn()
	var first := slime(Vector2(178, 200))
	var second := slime(Vector2(182, 200), true)
	await frames(3)
	await swing()
	check(first.health == 0.5 and second.health == 1.5 and impacts.size() == 2, "one swing hits each nearby enemy once")
	await spawn()
	var right_enemy := slime(Vector2(178, 200))
	var left_enemy := slime(Vector2(142, 200))
	Input.action_press("attack")
	await frames(7)
	Input.action_press("move_left")
	await frames(7)
	Input.action_release("move_left")
	check(right_enemy.health == 0.5 and left_enemy.health == 1.0 and player.facing == -1 and player.attack_facing == 1, "turning during active contact cannot strike both sides in one swing")
	await frames(60)
	check(right_enemy.health == 0.5 and left_enemy.health == 0.5, "next held swing follows the new facing after cooldown")
	await spawn()
	var interrupted := slime(Vector2(178, 200), true)
	await frames(3)
	Input.action_press("attack")
	await frames(2)
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
	await frames(14)
	check(interrupted.health == 2.0 and impacts.is_empty(), "interrupting windup prevents all damage from the cancelled swing")
	await frames(60)
	check(interrupted.health == 1.5 and impacts.size() == 1, "held F produces a fresh impact only after interrupted cooldown expires")
	await spawn()
	var after_death := slime(Vector2(178, 200), true)
	Input.action_press("attack")
	await frames(2)
	player.die()
	await frames(80)
	check(after_death.health == 2.0 and impacts.is_empty(), "death cancels windup and held F cannot damage after death")
	await spawn()
	Input.action_press("attack")
	await frames(14)
	var cooldown_before := player.attack_cooldown
	paused = true
	await frames(20)
	check(player.attack_cooldown == cooldown_before, "pause freezes Sword cooldown with the player")
	paused = false
	await frames(47)
	check(player.attack_time > 0.0, "held F resumes at the remaining interval after pause")
	await spawn(Vector2(160, 100))
	var aerial := slime(player.position + Vector2(18, 0))
	await frames(1)
	Input.action_press("attack")
	await frames(14)
	check(aerial.health == 0.5 and not player.is_on_floor(), "aerial Sword query damages a real enemy")
	await spawn(Vector2(194.92, 40))
	wall(Vector2(208, 80), Vector2(16, 240), 9)
	player.velocity.y = 100
	await frames(5)
	Input.action_press("attack")
	await frames(65)
	check(player.motion_state == SlicePlayer.MotionState.WALL_SLIDE and player.attack_time == 0.0 and player.attack_cooldown == 0.0, "held F never starts while wall sliding")
	for purple in [false, true]:
		await spawn()
		var contact := slime(Vector2(174, 200), purple, true)
		await frames(6)
		check(player.health == 3.0, "nearby non-overlapping sprites do not cause contact damage")
		contact.position = Vector2(170, 200)
		await frames(4)
		var remaining: float = 2.0 if purple else 2.5
		check(player.health == remaining, "%s physical overlap applies its contact DMG" % ["Purple" if purple else "Green"])
		check(player.hit_stun_time > 0.0 and player.knockback_time > 0.0, "actual Slime collision applies player stun and recoil")
		await frames(8)
		check(player.health == remaining, "player invulnerability prevents repeated contact damage")
	await spawn()
	var hurt := slime(Vector2(182, 200), false, true)
	Input.action_press("attack")
	for i in range(20):
		await frames(1)
		if hurt.knockback_time > 0.0: break
	check(hurt.health == 0.5 and hurt.knockback_time > 0.0 and hurt.sprite.modulate != Color.WHITE, "hit produces visible recoil feedback")
	hurt.position = player.position + Vector2(9, 0)
	await frames(2)
	check(player.health == 2.5, "a living Slime remains dangerous during recoil")
	await spawn()
	var simultaneous := slime(Vector2(250, 200), true, true)
	simultaneous.take_damage(0.5, Vector2(60, -55))
	simultaneous.take_damage(0.5, Vector2(60, -55))
	check(simultaneous.health == 1.0 and impacts.size() == 2, "simultaneous independent hits are accepted without enemy invulnerability")
	var before := simultaneous.position
	await frames(3)
	check(simultaneous.position.x > before.x and simultaneous.position.y < before.y, "knockback physically moves the Slime without freezing it")
	await frames(10)
	check(simultaneous.knockback_time == 0.0 and absf(simultaneous.velocity.x) == SliceSlime.PURPLE_PATROL_SPEED, "patrol resumes at variant speed after recoil")
	simultaneous.take_damage(1.0, Vector2.ZERO)
	simultaneous.take_damage(99.0, Vector2.ZERO)
	check(enemy_deaths == 1 and rewards == 1 and impacts.size() == 3, "simultaneous lethal hits emit only one defeat and reward")
	await spawn(Vector2(40, 200))
	var patrol := slime(Vector2(250, 200), false, true)
	patrol.patrol_left = -60
	patrol.patrol_right = 100
	var turned_left := false
	var turned_right := false
	var safe := true
	for i in range(600):
		await frames(1)
		turned_left = turned_left or patrol.direction < 0
		turned_right = turned_right or patrol.direction > 0
		safe = safe and patrol.position.x > 180 and patrol.position.x < 320 and patrol.position.y < 202
	check(safe and turned_left and turned_right, "patrol turns at its authored boundary and physical floor edge")
	await spawn(Vector2(40, 200))
	wall(Vector2(280, 170), Vector2(16, 60))
	var blocked := slime(Vector2(250, 200), true, true)
	blocked.patrol_left = -80
	blocked.patrol_right = 80
	blocked.direction = 1
	await frames(80)
	check(blocked.position.x < 264 and blocked.direction == -1, "patrol reverses at a solid wall")
	for action in ["attack", "jump", "move_left", "move_right"]: Input.action_release(action)
	room.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " combat checks; ", failures, " failures")
	quit(failures)

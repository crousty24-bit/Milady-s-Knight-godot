# RUN-016: real mapped input, pausable flight, swept collisions and weapon cooldowns.
extends SceneTree
const ARROW = preload("res://scripts/arrow.gd")
var failures := 0
var checks := 0
var room: Node2D
var player: SlicePlayer
var shots: Array[Node2D] = []
var shot_frames: Array[int] = []
var impacts := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func key(code: int, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)
func wall(pos: Vector2, size: Vector2) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.position = pos
	var collider := CollisionShape2D.new()
	collider.shape = RectangleShape2D.new()
	collider.shape.size = size
	body.add_child(collider)
	room.add_child(body)
func spawn() -> void:
	paused = false
	key(KEY_F, false)
	key(KEY_A, false)
	if is_instance_valid(room):
		room.queue_free()
		await frames(2)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	wall(Vector2(400, 208), Vector2(1800, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(160, 200)
	room.add_child(player)
	shots.clear()
	shot_frames.clear()
	impacts = 0
	player.projectile_fired.connect(func(arrow: Node2D): shots.append(arrow); shot_frames.append(Engine.get_physics_frames()))
	await frames(4)
func switch_slot() -> void:
	key(KEY_A, true)
	await frames(1)
	key(KEY_A, false)
	await frames(1)
func equip_bow() -> void:
	player.configure_equipment(true)
	await switch_slot()
func slime(pos: Vector2, purple := false) -> SliceSlime:
	var enemy: SliceSlime = load("res://scenes/slime.tscn").instantiate()
	enemy.variant = SliceSlime.Kind.PURPLE if purple else SliceSlime.Kind.GREEN
	enemy.position = pos
	room.add_child(enemy)
	enemy.set_physics_process(false)
	enemy.health_changed.connect(func(_hp: float, _max: float): impacts += 1)
	return enemy
func arrow_at(pos: Vector2, direction := 1) -> Node2D:
	var arrow: Node2D = ARROW.new()
	arrow.process_mode = Node.PROCESS_MODE_PAUSABLE
	room.add_child(arrow)
	arrow.global_position = pos
	var stats := WeaponCatalog.stats("Longbow0")
	arrow.setup(direction, stats.damage, stats.reach)
	return arrow
func run() -> void:
	await spawn()
	await switch_slot()
	check(player.active_slot == 0 and not player.has_longbow, "A without Longbow keeps melee selected")
	await equip_bow()
	check(player.active_slot == 1 and player.has_longbow, "mapped A selects owned Longbow")
	key(KEY_F, true)
	await frames(269)
	key(KEY_F, false)
	check(shot_frames.size() == 3, "held mapped F fires three Longbow shots over 4.48 seconds")
	check(shot_frames.size() == 3 and shot_frames[1] - shot_frames[0] == 132 and shot_frames[2] - shot_frames[1] == 132, "Longbow held cadence is exactly 2.2 seconds at 60 Hz")
	await spawn()
	await equip_bow()
	player.facing = -1
	key(KEY_F, true)
	await frames(2)
	key(KEY_F, false)
	var left: Node2D = shots[0]
	check(left.direction == -1 and left.global_position.x < left.origin.x, "Longbow shoots left from the facing muzzle")
	check(left.origin.is_equal_approx(Vector2(156, 190)), "range origin is the muzzle rather than player center")
	var previous := left.global_position
	player.position.x += 80
	await frames(1)
	check(absf(left.global_position.x - previous.x) < 6.0, "flight stays in world space when player moves")
	var saved_position := left.global_position
	var saved_cooldown := player.bow_cooldown
	paused = true
	await frames(25)
	check(left.global_position == saved_position and player.bow_cooldown == saved_cooldown, "pause freezes arrow travel and Longbow cooldown")
	paused = false
	await frames(2)
	check(left.global_position.x < saved_position.x and player.bow_cooldown < saved_cooldown, "arrow and cooldown resume after pause")
	player.die()
	await frames(1)
	check(not is_instance_valid(left), "death clears a projectile already in flight")
	key(KEY_F, true)
	await frames(100)
	check(shots.size() == 1, "dead player cannot fire held F")
	await spawn()
	player.configure_equipment(true)
	key(KEY_F, true)
	await frames(2)
	key(KEY_F, false)
	var sword_before := player.attack_cooldown
	await switch_slot()
	check(player.attack_time == 0.0 and player.attack_cancelled and player.attack_cooldown < sword_before and player.attack_cooldown > 0.8, "switch cancels Sword windup while retaining Sword cooldown")
	key(KEY_F, true)
	await frames(2)
	key(KEY_F, false)
	check(shots.size() == 1 and player.bow_cooldown > 2.1, "Bow has an independent cooldown and can fire after Sword switch")
	var bow_before := player.bow_cooldown
	await switch_slot()
	key(KEY_F, true)
	await frames(2)
	key(KEY_F, false)
	check(player.attack_time == 0.0 and player.attack_cooldown > 0.0 and player.bow_cooldown < bow_before, "switching back cannot bypass melee cooldown or reset bow cooldown")
	await switch_slot()
	key(KEY_F, true)
	await frames(2)
	key(KEY_F, false)
	check(shots.size() == 1, "returning to Longbow cannot bypass its original cooldown")
	player.controls_enabled = false
	await switch_slot()
	check(player.active_slot == 1, "modal controls lock prevents equipment switching")
	player.controls_enabled = true
	player.hit_stun_time = 0.18
	await switch_slot()
	check(player.active_slot == 1, "hit stun prevents equipment switching")
	player.configure_equipment(false)
	check(player.active_slot == 0 and not player.has_longbow, "removing ownership restores melee selection")
	await spawn()
	wall(Vector2(208, 80), Vector2(16, 240))
	var grip_wall: StaticBody2D = room.get_child(room.get_child_count() - 1)
	grip_wall.collision_layer = 9
	player.position = Vector2(194.92, 40)
	player.velocity.y = 100
	await frames(5)
	await equip_bow()
	check(player.motion_state == SlicePlayer.MotionState.WALL_SLIDE, "ranged fixture reaches physical wall slide")
	key(KEY_F, true)
	await frames(2)
	key(KEY_F, false)
	key(KEY_RIGHT, false)
	check(shots.size() == 1, "ranged shot stays available in wall slide; melee-only restriction is preserved")
	await spawn()
	await equip_bow()
	var first := slime(Vector2(215, 200), true)
	var second := slime(Vector2(255, 200), true)
	await frames(2)
	key(KEY_F, true)
	await frames(20)
	key(KEY_F, false)
	check(first.health == 1.0 and second.health == 2.0 and impacts == 1, "one arrow damages exactly one real Slime for one HP")
	check(not is_instance_valid(shots[0]), "arrow is removed immediately after enemy impact")
	await spawn()
	await equip_bow()
	var behind := slime(Vector2(215, 200))
	wall(Vector2(191, 180), Vector2(1, 40))
	await frames(2)
	key(KEY_F, true)
	await frames(20)
	key(KEY_F, false)
	check(behind.health == 1.0 and impacts == 0 and not is_instance_valid(shots[0]), "terrain occludes Longbow and removes the arrow")
	await spawn()
	wall(Vector2(200, 180), Vector2(1, 40))
	var far := slime(Vector2(230, 200))
	await frames(2)
	var swept := arrow_at(Vector2(164, 190))
	swept.set_physics_process(false)
	swept._physics_process(0.5)
	check(swept.is_queued_for_deletion() and swept.global_position.x < 200 and far.health == 1.0, "160 px swept step cannot tunnel through a one-pixel wall")
	await frames(2)
	await spawn()
	var beyond := slime(Vector2(380, 200))
	await frames(2)
	var ranged := arrow_at(Vector2(164, 190))
	ranged.set_physics_process(false)
	ranged._physics_process(2.0)
	check(ranged.is_queued_for_deletion() and ranged.global_position == Vector2(340, 190) and beyond.health == 1.0, "oversized step clamps to 176 px from muzzle and cannot hit beyond range")
	await frames(2)
	await spawn()
	await equip_bow()
	key(KEY_F, true)
	await frames(2)
	key(KEY_F, false)
	var restarting: Node2D = shots[0]
	await spawn()
	check(not is_instance_valid(restarting), "restarting the scene clears player-owned arrows")
	key(KEY_F, false)
	key(KEY_A, false)
	room.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " longbow checks; ", failures, " failures")
	quit(failures)

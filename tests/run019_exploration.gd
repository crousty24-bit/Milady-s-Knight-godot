extends SceneTree
const Store = preload("res://scripts/progression.gd")
const SAVE = "user://run019-exploration.json"
const MELEE = SlicePlayer.DamageSource.CONTACT_MELEE
const SHOT = SlicePlayer.DamageSource.PROJECTILE
var failures := 0
var checks := 0
var room: Node2D
var player: SlicePlayer
var progress: Node
func _initialize() -> void: call_deferred("run")
func frames(count: int = 4) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func item(kind: String, pos: Vector2, id: String = "") -> Node2D:
	var node: Node2D = load("res://scenes/" + kind + ".tscn").instantiate()
	node.position = pos
	if kind == "secret_wall": node.secret_id = id
	if kind == "hp_bonus": node.bonus_id = id
	room.add_child(node)
	return node
func ray_at(x: float) -> Dictionary:
	return room.get_world_2d().direct_space_state.intersect_ray(PhysicsRayQueryParameters2D.create(Vector2(x-20,184),Vector2(x+20,184),1))
func run() -> void:
	progress = root.get_node("Progression")
	progress.storage_path = SAVE
	progress.persistence_enabled = true
	if OS.get_cmdline_user_args().has("reload"):
		check(progress.load_progress() == OK and progress.has_hp_bonus("fixture-heart") and progress.permanent_flags.get("secret:fixture-wall", false), "cold process reload preserves secret and HP acquisition")
		print("RESULT %d run019 exploration checks; %d failures" % [checks, failures])
		quit(failures)
		return
	check(progress.new_game() == OK, "isolated durable baseline")
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	var floor_body := StaticBody2D.new()
	floor_body.position = Vector2(400,208)
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = Vector2(1800,16)
	floor_body.add_child(shape)
	room.add_child(floor_body)
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(80,200)
	room.add_child(player)
	await frames()
	player.health_units = 10
	var heart = item("hp_bonus", Vector2(80,190), "fixture-heart")
	await frames()
	check(heart.used and player.max_health == 4.0 and player.health == 2.0, "physical wounded pickup grants +1 current and maximum")
	var duplicate = item("hp_bonus", Vector2(80,190), "fixture-heart")
	await frames()
	check(duplicate.used and player.health == 2.0 and progress.hp_bonus_count() == 1, "durable duplicate cannot heal twice")
	var full = item("hp_bonus", Vector2(400,190), "full-heart")
	player.configure_bonus_health(1)
	check(full.collect(player) and player.health == 5.0 and player.max_health == 5.0, "full-health bonus grants +1 current and maximum")
	var invalid = item("hp_bonus", Vector2(440,190))
	check(not invalid.collect(player) and invalid.save_failed and not invalid.used, "empty durable ID remains available without grant")
	var failed = item("hp_bonus", Vector2(480,190), "retry-heart")
	progress.storage_path = "user://run019-missing-directory/save.json"
	check(not failed.collect(player) and failed.save_failed and not failed.used and player.max_health == 5.0, "HP disk failure leaves health and pickup unchanged")
	progress.storage_path = SAVE
	check(failed.collect(player) and not failed.save_failed and player.max_health == 6.0, "HP retry commits before grant")
	var shield = item("magic_shield", Vector2(80,190))
	await frames()
	check(shield.used and player.magic_shield_time > 9.8, "physical shield pickup activates ten seconds")
	player.magic_shield_time = 2.0
	var second = item("magic_shield", Vector2(600,190))
	check(second.collect(player) and player.magic_shield_time == 10.0, "shield refreshes to ten seconds without addition")
	var wall = item("secret_wall", Vector2(160,200), "fixture-wall")
	await frames()
	check(not ray_at(160).is_empty(), "closed secret is physically solid")
	progress.storage_path = "user://run019-missing-directory/save.json"
	check(not wall.receive_player_attack(1.0, MELEE) and wall.save_failed and not wall.opened, "secret disk failure leaves collision closed")
	await frames()
	check(not ray_at(160).is_empty(), "failed secret still blocks physical ray")
	progress.storage_path = SAVE
	check(wall.receive_player_attack(1.0, MELEE) and not wall.save_failed, "secret melee retry saves and reveals")
	await frames()
	check(ray_at(160).is_empty() and not wall.receive_player_attack(1.0, SHOT), "revealed wall removes collision and ignores duplicate hits")
	var reload_wall = item("secret_wall", Vector2(200,200), "fixture-wall")
	await frames()
	check(reload_wall.opened and not reload_wall.visible and ray_at(200).is_empty(), "persisted secret starts open without replay")
	var shot_wall = item("secret_wall", Vector2(240,200), "shot-wall")
	var arrow = load("res://scripts/arrow.gd").new()
	room.add_child(arrow)
	arrow.global_position = Vector2(215,184)
	arrow.setup(1)
	await frames(12)
	check(shot_wall.opened and not is_instance_valid(arrow), "actual swept player projectile reveals and is consumed")
	var sword_wall = item("secret_wall", Vector2(300,200), "sword-wall")
	player.position = Vector2(278,200)
	player.velocity = Vector2.ZERO
	player.facing = 1
	await frames()
	var key := InputEventKey.new()
	key.keycode = KEY_F
	key.pressed = true
	Input.parse_input_event(key)
	await frames(24)
	key = InputEventKey.new()
	key.keycode = KEY_F
	key.pressed = false
	Input.parse_input_event(key)
	await frames(4)
	check(sword_wall.opened, "mapped melee input reveals accessible secret wall")
	var door = item("secondary_door", Vector2(360,200))
	var plate = item("pressure_plate", Vector2(300,200))
	plate.target_door = plate.get_path_to(door)
	check(not plate.receive_player_attack(1.0, MELEE), "melee does not activate plate")
	player.position = Vector2(300,200)
	player.velocity = Vector2.ZERO
	await frames(6)
	check(plate.active and door.opened and door.get_node("Barrier/Shape").disabled, "physical top contact activates plate and opens linked door")
	check(not plate.activate() and not door.open(), "plate and door activation remain single use")
	var shot_plate = item("pressure_plate", Vector2(440,200))
	arrow = load("res://scripts/arrow.gd").new()
	room.add_child(arrow)
	arrow.global_position = Vector2(410,197)
	arrow.setup(1)
	await frames(12)
	check(shot_plate.active and not is_instance_valid(arrow), "actual projectile activates plate")
	var button = item("mechanism_button", Vector2(520,200))
	check(not button.can_use(player), "button excludes distant player")
	player.position = Vector2(520,200)
	player.velocity = Vector2.ZERO
	await frames()
	check(button.can_use(player) and button.activate() and not button.can_use(player) and not button.activate(), "button proximity and single-use interface")
	var locked = item("secondary_door", Vector2(580,200))
	locked.coin_cost = 3
	player.position = Vector2(560,200)
	player.velocity = Vector2.ZERO
	await frames()
	check(locked.can_use(player) and locked.coin_cost == 3, "paid door exposes instance cost and proximity")
	player.dead = true
	check(not locked.can_use(player), "dead player cannot use door")
	var dead_shield = item("magic_shield", Vector2(650,190))
	check(not dead_shield.collect(player) and not dead_shield.used, "dead player cannot consume pickup")
	var disk := Store.new()
	disk.storage_path = SAVE
	check(disk.load_progress() == OK and disk.hp_bonus_count() == 3 and disk.permanent_flags.get("secret:fixture-wall", false), "fresh storage object reloads durable state")
	disk.free()
	room.queue_free()
	await frames(6)
	print("RESULT %d run019 exploration checks; %d failures" % [checks, failures])
	quit(failures)

extends SceneTree
var checks := 0
var failures := 0
var room: Node2D
var player: SlicePlayer
var last_drop := -1
func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func stop_audio(node: Node) -> void:
	if node is AudioStreamPlayer or node is AudioStreamPlayer2D: node.stop()
	for child in node.get_children(): stop_audio(child)
func fixture() -> void:
	paused = false
	Input.action_release("attack")
	Input.action_release("move_right")
	if is_instance_valid(room):
		stop_audio(room)
		OS.delay_msec(300)
		room.queue_free()
		await frames()
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	var floor_body := StaticBody2D.new()
	var collision := CollisionShape2D.new()
	collision.shape = RectangleShape2D.new()
	collision.shape.size = Vector2(800, 16)
	floor_body.position = Vector2(320, 208)
	floor_body.add_child(collision)
	room.add_child(floor_body)
	player = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(160, 200)
	room.add_child(player)
	player.configure_loadout({"melee": "Sword0", "ranged": "Longbow0"})
	await frames(5)
func prop(kind: String, at: Vector2, family: String = "Longbow") -> Node2D:
	var node: Node2D = load("res://scenes/ammo_%s.tscn" % kind).instantiate()
	node.position = at
	node.ammo_family = family
	room.add_child(node)
	node.destroyed.connect(func(amount: int): last_drop = amount)
	return node
func pickups() -> Array:
	var found: Array = []
	for child in room.get_children():
		if child.has_signal("collected") and child.get_script() == load("res://scripts/ammo_pickup.gd"): found.append(child)
	return found
func run() -> void:
	await fixture()
	var crate := prop("crate", Vector2(220, 200))
	for sample in [[0.0,0], [0.199999,0], [0.2,1], [0.599999,1], [0.6,3], [0.899999,3], [0.9,5], [0.999999,5]]:
		check(crate.drop_amount_for_roll(sample[0]) == sample[1], "drop table boundary %.6f gives %d" % [sample[0],sample[1]])
	crate.drop_weights.assign([0,0,0,1])
	player.active_slot = 1
	Input.action_press("attack")
	await frames(25)
	Input.action_release("attack")
	check(last_drop == 5 and pickups().size() == 1 and player.ammo.Longbow == 9, "actual arrow destroys crate once and costs one ammunition")
	var loot: Area2D = pickups()[0]
	check(loot.amount == 5 and loot.ammo_family == "Longbow", "crate spawns its authored family and rolled quantity")
	player.position = loot.position + Vector2(0, 8)
	await frames()
	check(pickups().is_empty() and player.ammo.Longbow == 14, "actual contact collects ammo and removes exhausted pickup")
	await fixture()
	var barrel := prop("barrel", Vector2(180, 200), "ThrowingKnives")
	barrel.drop_weights.assign([0,0,1,0])
	player.active_slot = 0
	Input.action_press("attack")
	await frames(16)
	Input.action_release("attack")
	check(last_drop == 3 and pickups().size() == 1 and player.ammo.Longbow == 10, "actual sword destroys barrel without spending arrows")
	var knife_loot: Area2D = pickups()[0]
	player.position = knife_loot.position + Vector2(0,8)
	await frames()
	check(player.ammo.ThrowingKnives == 15 and player.ammo.Longbow == 10 and pickups().is_empty(), "unequipped knives collect into independent family")
	await fixture()
	var intact := prop("crate", Vector2(190,200))
	Input.action_press("move_right")
	await frames(40)
	Input.action_release("move_right")
	check(player.position.x > intact.position.x + 16 and not intact.broken, "walking crosses intact prop without blocking or destroying it")
	intact.drop_weights.assign([0,1,0,0])
	check(intact.receive_player_attack(0.5, SlicePlayer.DamageSource.CONTACT_MELEE) and not intact.receive_player_attack(1.0, SlicePlayer.DamageSource.PROJECTILE), "simultaneous hits cannot create a duplicate drop")
	await frames()
	check(pickups().size() == 1 and pickups()[0].amount == 1, "single positive drop after duplicate hit")
	await fixture()
	var empty := prop("barrel", Vector2(240,200))
	empty.drop_weights.assign([1,0,0,0])
	check(not empty.receive_player_attack(0.0, SlicePlayer.DamageSource.CONTACT_MELEE) and not empty.broken, "non damaging attack cannot break prop")
	empty.receive_player_attack(0.5, SlicePlayer.DamageSource.CONTACT_MELEE)
	await frames()
	check(last_drop == 0 and pickups().is_empty(), "zero drop is a valid destruction outcome")
	var pickup: Area2D = load("res://scenes/ammo_pickup.tscn").instantiate()
	pickup.amount = 5
	pickup.position = player.position - Vector2(0,8)
	room.add_child(pickup)
	player.ammo.Longbow = 14
	await frames()
	check(player.ammo.Longbow == 15 and is_instance_valid(pickup) and pickup.amount == 4, "partial pickup retains remainder at cap")
	await frames(6)
	check(pickup.amount == 4 and player.ammo.Longbow == 15, "full reserve leaves remainder untouched over repeated contact")
	paused = true
	player.ammo.Longbow = 12
	await frames(5)
	check(pickup.amount == 4 and player.ammo.Longbow == 12, "pause suspends contact collection")
	paused = false
	await frames()
	check(player.ammo.Longbow == 15 and pickup.amount == 1, "unpause collects only available capacity")
	player.dead = true
	player.ammo.Longbow = 10
	await frames()
	check(pickup.amount == 1 and player.ammo.Longbow == 10, "dead player cannot collect remainder")
	player.dead = false
	player.ammo.Longbow = 14
	await frames()
	check(not is_instance_valid(pickup) and player.ammo.Longbow == 15, "last remainder consumed exactly once")
	for scene_path in ["eidolon_vale", "blight_town", "black_forrest", "forbidden_graveyard"]:
		var level: Node2D = load("res://scenes/%s.tscn" % scene_path).instantiate()
		var counts := {"Longbow":0, "ThrowingKnives":0}
		for item in level.find_children("*", "StaticBody2D", true, false):
			if item.get_script() == load("res://scripts/ammo_prop.gd"):
				counts[item.ammo_family] += 1
		var expected: Dictionary = {"eidolon_vale":{"Longbow":2,"ThrowingKnives":0},"blight_town":{"Longbow":4,"ThrowingKnives":2},"black_forrest":{"Longbow":4,"ThrowingKnives":4},"forbidden_graveyard":{"Longbow":5,"ThrowingKnives":5}}
		check(counts == expected[scene_path], "authored %s ammo budgets and families match contract" % scene_path)
		level.free()
	stop_audio(room)
	OS.delay_msec(300)
	room.queue_free()
	await frames()
	print("RESULT %d ammunition prop checks; %d failures" % [checks,failures])
	quit(1 if failures else 0)

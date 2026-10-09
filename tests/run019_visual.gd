# Functional rendering pilot, not the final Claude art/animation acceptance.
extends SceneTree
const OUT = "res://work/run019/render"
var room: Node2D
var player: SlicePlayer
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func frames(n: int = 3) -> void:
	for i in n:
		await physics_frame
		await process_frame
func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var picture := root.get_texture().get_image()
	check(picture.get_size() == Vector2i(640, 360), name + " viewport640x360")
	check(picture.save_png(OUT + "/" + name + ".png") == OK, name + " capture saved")
	await process_frame
func reset(title: String) -> void:
	if is_instance_valid(room):
		room.queue_free()
		await frames(3)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	var label := Label.new()
	label.position = Vector2(20, 20)
	label.text = title + " — functional fixture, provisional art"
	room.add_child(label)
	var floor := StaticBody2D.new()
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = Vector2(620, 20)
	shape.shape = rectangle
	floor.add_child(shape)
	room.add_child(floor)
	floor.position = Vector2(320, 270)
	var floor_art := Polygon2D.new()
	floor_art.polygon = PackedVector2Array([Vector2(10,260),Vector2(630,260),Vector2(630,280),Vector2(10,280)])
	floor_art.color = Color("454257")
	room.add_child(floor_art)
	player = load("res://scenes/player.tscn").instantiate()
	room.add_child(player)
	player.get_node("Camera2D").enabled = false
	player.position = Vector2(200, 260)
	player.controls_enabled = false
	player.magic_shield_time = 100.0
	await frames(4)
func add_item(kind: String, at: Vector2) -> Node2D:
	var node = load("res://scenes/" + kind + ".tscn").instantiate()
	node.position = at
	room.add_child(node)
	return node
func run() -> void:
	if DisplayServer.get_name() == "headless":
		check(false, "render pilot needs graphical runtime")
		quit(1)
		return
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	DirAccess.make_dir_recursive_absolute(OUT)
	var progress := root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	for kind in ["red_slime", "bloated_slime", "skeleton_warrior", "skeleton_archer", "blight_sorcerer", "chud_blob"]:
		await reset(kind)
		var enemy := add_item(kind, Vector2(278,260))
		await frames(32)
		check(not enemy.dead and enemy.health > 0, kind + " active rendered actor")
		if kind != "red_slime": check(enemy.aggro, kind + " acquired live visible player")
		if kind == "blight_sorcerer": check(enemy.active_attacks.size() > 0, "sorcerer emitted committed warning zone")
		await capture(kind)
	await reset("skull_swarm")
	var swarm := add_item("skull_swarm", Vector2(200,220))
	await frames(10)
	check(swarm.skulls.size() == 4, "rendered swarm has four slots")
	await capture("swarm")
	await reset("traps")
	player.position = Vector2(60,260)
	var spikes := add_item("retractable_spikes", Vector2(180,260))
	spikes.initial_phase = 2.2
	spikes.cycle_time = 2.2
	var plant := add_item("poison_plant", Vector2(260,260))
	var turret := add_item("turret", Vector2(400,220))
	turret.direction = Vector2.LEFT
	turret.cycle_time = 1.6
	await frames(3)
	check(spikes.phase == spikes.Phase.EXTENDED and turret.warning, "spike danger and turret warning rendered")
	await capture("traps-warning")
	await frames(27)
	check(not turret.warning, "turret finishes warning and fires")
	await capture("traps-fire")
	await reset("trapdoor")
	var door := add_item("trapdoor", Vector2(200,240))
	player.position = Vector2(200,240)
	player.magic_shield_time = 0.0
	await frames(5)
	check(door.triggered and not door.is_open, "rendered trapdoor warning follows physical top passage")
	await capture("trapdoor-warning")
	await frames(30)
	check(door.is_open, "rendered trapdoor stays open")
	await capture("trapdoor-open")
	await reset("persistent pickups and mechanisms")
	player.position = Vector2(40,260)
	var secret = load("res://scenes/secret_wall.tscn").instantiate()
	secret.secret_id = "render-secret"
	secret.position = Vector2(420,260)
	room.add_child(secret)
	var bonus = load("res://scenes/hp_bonus.tscn").instantiate()
	bonus.bonus_id = "render-heart"
	bonus.position = Vector2(480,248)
	room.add_child(bonus)
	add_item("magic_shield",Vector2(100,248))
	var button := add_item("mechanism_button",Vector2(190,260))
	var secondary := add_item("secondary_door",Vector2(320,260))
	var plate := add_item("pressure_plate",Vector2(260,260))
	button.target_door = button.get_path_to(secondary)
	await frames(4)
	await capture("exploration-closed")
	button.activate()
	secret.receive_player_attack(0.5, SlicePlayer.DamageSource.CONTACT_MELEE)
	await create_timer(secret.fade_duration + 0.1, false).timeout
	await frames(2) # Flush the collision change deferred after the fade completes.
	check(button.active and secondary.opened and secret.opened and secret.passage_open and secret.get_node("Shape").disabled, "rendered mechanisms and reveal match gameplay state")
	await capture("exploration-open")
	room.queue_free()
	await frames(4)
	room = load("res://tests/fixtures/run019_systems.tscn").instantiate()
	root.add_child(room)
	current_scene = room
	room.get_node("Music").stop()
	for enemy in room.get_node("Enemies").get_children(): enemy.queue_free()
	room.player.controls_enabled = false
	room.hud.show_save_error()
	await frames(4)
	check(room.hud.save_error_label.visible, "rendered HUD retains durable save failure message")
	await capture("save-error")
	room.queue_free()
	await frames(3)
	await create_timer(0.4).timeout
	print("RESULT %d run019 render checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

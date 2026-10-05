# RUN-019 Claude art capture pilot (presentation inspection, not a gameplay test).
# Contact sheets of every animation in context (knight, 16 px floor) plus live gameplay states.
# Usage (graphical runtime, isolated profile): tools/run.sh --script res://tools/art/run019/capture_run019.gd
extends SceneTree
const OUT = "res://work/run019/claude/render"
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
	check(picture.get_size() == Vector2i(640, 360), name + " viewport 640x360")
	check(picture.save_png(OUT + "/" + name + ".png") == OK, name + " capture saved")

func floor_at(y: float, from: float = 0.0, to: float = 640.0) -> void:
	var body := StaticBody2D.new()
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = Vector2(to - from, 16)
	shape.shape = rectangle
	body.add_child(shape)
	room.add_child(body)
	body.position = Vector2((from + to) / 2.0, y + 8)
	var art := Polygon2D.new()
	art.polygon = PackedVector2Array([Vector2(from, y), Vector2(to, y), Vector2(to, y + 16), Vector2(from, y + 16)])
	art.color = Color("39363f")
	room.add_child(art)
	var lip := Line2D.new()
	lip.points = PackedVector2Array([Vector2(from, y + 0.5), Vector2(to, y + 0.5)])
	lip.width = 1
	lip.default_color = Color("625d67")
	room.add_child(lip)

func label(text: String, at: Vector2) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override("font_size", 8)
	l.modulate = Color(1, 1, 1, 0.7)
	room.add_child(l)

func reset(title: String, with_player: bool = true) -> void:
	if is_instance_valid(room):
		room.queue_free()
		await frames(3)
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	var sky := ColorRect.new()
	sky.color = Color("121720")
	sky.size = Vector2(640, 360)
	sky.z_index = -10
	room.add_child(sky)
	label(title, Vector2(6, 2))
	player = null
	if with_player:
		player = load("res://scenes/player.tscn").instantiate()
		room.add_child(player)
		player.get_node("Camera2D").enabled = false
		player.controls_enabled = false
		player.position = Vector2(-200, 0)

func knight_at(at: Vector2) -> void:
	var knight := AnimatedSprite2D.new()
	knight.sprite_frames = player.sprite.sprite_frames
	knight.position = at + player.sprite.position
	knight.play(&"idle")
	room.add_child(knight)

func add(kind: String, at: Vector2) -> Node2D:
	var node = load("res://scenes/" + kind + ".tscn").instantiate()
	node.position = at
	room.add_child(node)
	return node

# Freeze an actor on one animation frame (physics off) for a contact sheet.
func pose(node: Node, anim: StringName, frame_ratio: float) -> void:
	node.set_physics_process(false)
	node.set_process(false)
	var art: AnimatedSprite2D = node.get_node("Art")
	art.play(anim)
	art.pause()
	art.frame = clampi(int(round(frame_ratio * (art.sprite_frames.get_frame_count(anim) - 1))), 0, art.sprite_frames.get_frame_count(anim) - 1)
	art.modulate = Color.WHITE

func run() -> void:
	if DisplayServer.get_name() == "headless":
		check(false, "capture pilot needs graphical runtime")
		quit(1)
		return
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	DirAccess.make_dir_recursive_absolute(OUT)
	var progress := root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()

	# 1. Enemy contact sheets: one row per family, one column per animation (frame mid / late).
	var rows := {
		"red_slime": [[&"red", 0.3], [&"red_hit", 0.0], [&"red_death", 0.4]],
		"skeleton_warrior": [[&"idle", 0.0], [&"walk", 0.4], [&"windup", 1.0], [&"attack", 0.4], [&"hit", 0.0], [&"death", 0.5], [&"death", 1.0]],
		"skeleton_archer": [[&"idle", 0.0], [&"walk", 0.4], [&"windup", 1.0], [&"shoot", 0.3], [&"hit", 0.0], [&"death", 0.5], [&"death", 1.0]],
		"blight_sorcerer": [[&"idle", 0.0], [&"walk", 0.4], [&"cast", 1.0], [&"cast_release", 0.5], [&"swing_windup", 1.0], [&"swing", 0.4], [&"hit", 0.0], [&"death", 1.0]],
		"bloated_slime": [[&"crawl", 0.0], [&"crawl", 0.5], [&"swell", 1.0], [&"hit", 0.0], [&"death", 0.4], [&"death", 1.0]],
		"chud_blob": [[&"idle", 0.0], [&"walk", 0.4], [&"windup", 1.0], [&"slam", 0.4], [&"hit", 0.0], [&"death", 0.5], [&"death", 1.0]],
	}
	await reset("RUN-019 enemies — contact sheet (knight for scale)")
	var y := 60.0
	for kind in rows:
		floor_at(y, 0, 640)
		knight_at(Vector2(24, y))
		var x := 80.0
		for spec in rows[kind]:
			var enemy := add(kind, Vector2(x, y))
			await frames(1)
			if kind == "red_slime":
				enemy.set_physics_process(false)
				var sprite: AnimatedSprite2D = enemy.get_node("Sprite")
				sprite.play(spec[0])
				sprite.pause()
				sprite.frame = int(spec[1] * (sprite.sprite_frames.get_frame_count(spec[0]) - 1))
			else:
				pose(enemy, spec[0], spec[1])
			x += 66.0
		y += 50.0
	await frames(2)
	await capture("enemies-sheet")

	# 2. Skulls and projectiles/VFX sheet.
	await reset("RUN-019 skulls, arrow, blight zone")
	floor_at(300)
	knight_at(Vector2(40, 300))
	var skull_x := 90.0
	for spec in [[&"fly", 0.0], [&"spawn", 0.5], [&"despawn", 0.5], [&"death", 0.3], [&"bite", 0.5]]:
		var skull := add("possessed_skull", Vector2(skull_x, 270))
		await frames(1)
		pose(skull, spec[0], spec[1])
		skull_x += 40.0
	var attack_script := load("res://scripts/run019_enemy_attack.gd")
	for i in 4:
		var blast := Node2D.new()
		blast.set_script(attack_script)
		blast.mode = 1
		blast.radius = 24.0
		blast.warning_duration = 1.0
		room.add_child(blast)
		blast.global_position = Vector2(320 + i * 70, 300)
		blast.set_physics_process(false)
		blast.elapsed = 0.1 + i * 0.29
	var arrow := Node2D.new()
	arrow.set_script(attack_script)
	arrow.mode = 0
	arrow.motion = Vector2(-150, 0)
	room.add_child(arrow)
	arrow.global_position = Vector2(300, 240)
	arrow.set_physics_process(false)
	await frames(2)
	await capture("skulls-projectiles-sheet")

	# 3. Traps and exploration states sheet.
	await reset("RUN-019 traps / mechanisms — states")
	floor_at(120)
	floor_at(240)
	floor_at(340)
	knight_at(Vector2(20, 120))
	var states := [
		["retractable_spikes", Vector2(70, 120), [&"retracted", &"warning", &"extended"]],
		["trapdoor", Vector2(70, 240), [&"closed", &"warning", &"opened"]],
		["poison_plant", Vector2(380, 120), [&"idle", &"snap"]],
		["pressure_plate", Vector2(380, 240), [&"inactive", &"active"]],
		["mechanism_button", Vector2(500, 240), [&"inactive", &"active"]],
	]
	for item in states:
		var at: Vector2 = item[1]
		for anim in item[2]:
			var node := add(item[0], at)
			await frames(1)
			pose(node, anim, 0.5)
			at.x += 44.0
	var turret_x := 70.0
	for anim in [&"idle", &"warning", &"fire"]:
		var turret := add("turret", Vector2(turret_x, 300))
		await frames(1)
		pose(turret, anim, 0.5)
		turret_x += 40.0
	var aimed := add("turret", Vector2(220, 300))
	aimed.direction = Vector2.LEFT
	await frames(1)
	pose(aimed, &"warning", 1.0)
	aimed._aim_art()
	var door_x := 280.0
	for coin in [true, false]:
		for anim in [&"closed", &"rise", &"opened"]:
			var door := add("secondary_door", Vector2(door_x, 340))
			door.coin_locked = coin
			await frames(1)
			var art: AnimatedSprite2D = door.get_node("Art")
			art.sprite_frames = door._door_frames()
			pose(door, anim, 0.5)
			door_x += 30.0
	var secret := add("secret_wall", Vector2(500, 120))
	var shield := add("magic_shield", Vector2(540, 108))
	var heart := add("hp_bonus", Vector2(570, 108))
	await frames(4)
	check(secret.get_node("Shape") != null and shield.visible and heart.visible, "pickups and secret drawn")
	await capture("world-sheet")

	# 4. Live gameplay states with the real timers.
	await reset("RUN-019 live — warrior/archer/sorcerer attacks")
	floor_at(260)
	player.position = Vector2(200, 260)
	await frames(2)
	var warrior := add("skeleton_warrior", Vector2(226, 260))
	var archer := add("skeleton_archer", Vector2(300, 260))
	var sorcerer := add("blight_sorcerer", Vector2(90, 260))
	await frames(12)
	check(warrior.aggro and archer.aggro and sorcerer.aggro, "three attackers acquired the knight")
	await capture("live-windups")
	await frames(14)
	await capture("live-release")
	await frames(30)
	await capture("live-blast-warning")
	await frames(30)
	await capture("live-blast-explosion")

	await reset("RUN-019 live — shield aura, swarm, kills")
	floor_at(260)
	player.position = Vector2(120, 260)
	await frames(2)
	check(player.activate_magic_shield(), "shield activated")
	var swarm := add("skull_swarm", Vector2(220, 240))
	await frames(6)
	await capture("live-swarm-spawn-shield")
	var chud := add("chud_blob", Vector2(400, 260))
	var bloated := add("bloated_slime", Vector2(500, 260))
	await frames(3)
	chud.take_damage(100.0, Vector2.ZERO)
	bloated.take_damage(100.0, Vector2.ZERO)
	for skull in swarm.skulls:
		if is_instance_valid(skull): skull.take_damage(5.0, Vector2.ZERO)
	await frames(10)
	await capture("live-deaths")
	player.magic_shield_time = 0.01
	await frames(4)
	await capture("live-shield-end")

	await reset("RUN-019 live — traps and doors")
	floor_at(260)
	player.position = Vector2(60, 260)
	player.magic_shield_time = 0.0
	var spikes := add("retractable_spikes", Vector2(140, 260))
	spikes.cycle_time = 2.05
	var turret := add("turret", Vector2(560, 236))
	turret.direction = Vector2.LEFT
	turret.cycle_time = 1.95
	var plant := add("poison_plant", Vector2(240, 260))
	var plate := add("pressure_plate", Vector2(320, 260))
	var door := add("secondary_door", Vector2(380, 260))
	door.coin_locked = false
	plate.target_door = plate.get_path_to(door)
	var wall := add("secret_wall", Vector2(460, 260))
	wall.secret_id = "capture-secret"
	await frames(6)
	plate.activate()
	wall.receive_player_attack(0.5, SlicePlayer.DamageSource.CONTACT_MELEE)
	await frames(10)
	await capture("live-traps-mid")
	await frames(30)
	check(door.opened and wall.opened, "door opened and secret revealed")
	await capture("live-traps-after")
	room.queue_free()
	await frames(3)
	print("RESULT %d run019 capture checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

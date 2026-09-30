# RUN-010: audio buses, routing and the P0 feedbacks triggered by the real systems.
extends SceneTree
var failures := 0
var checks := 0
var room: Node2D
var level: Node2D
var player: SlicePlayer
const PLAYER_SOUNDS = ["JumpSound", "DoubleJumpSound", "WallJumpSound", "HurtSound", "SwingSound", "DeathSound"]
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func press(action: String, count := 2) -> void:
	Input.action_press(action)
	await frames(count)
func release(action: String, count := 2) -> void:
	Input.action_release(action)
	await frames(count)
func solid(pos: Vector2, size: Vector2) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 9
	body.position = pos
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	body.add_child(shape)
	room.add_child(body)
func clear_scene() -> void:
	for action in ["jump", "attack", "move_left", "move_right", "pause"]: Input.action_release(action)
	for node in [room, level]:
		if is_instance_valid(node): node.queue_free()
	paused = false
	await frames(2)
func spawn_room(pos := Vector2(100, 200)) -> void:
	await clear_scene()
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	solid(Vector2(150, 208), Vector2(600, 16))
	solid(Vector2(208, 80), Vector2(16, 240))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = pos
	room.add_child(player)
	await frames(3)
func spawn_level() -> void:
	await clear_scene()
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	player = level.get_node("Player")
	await frames(10)
func only_playing(names: Array) -> bool:
	for sound in PLAYER_SOUNDS:
		if player.get_node(sound).playing != names.has(sound): return false
	return true
func run() -> void:
	var expected := ["Master", "Music", "Ambient", "SFX", "UI"]
	var buses: Array[String] = []
	for i in range(AudioServer.bus_count): buses.append(AudioServer.get_bus_name(i))
	check(buses == expected, "buses Master/Music/Ambient/SFX/UI exist in order")
	var sends_master := true
	for i in range(1, AudioServer.bus_count): sends_master = sends_master and AudioServer.get_bus_send(i) == &"Master"
	check(sends_master, "every group bus sends to Master")
	check(AudioServer.get_bus_effect_count(0) == 1 and AudioServer.get_bus_effect(0, 0) is AudioEffectHardLimiter and AudioServer.is_bus_effect_enabled(0, 0), "Master carries an enabled hard limiter")

	await spawn_room()
	var routed := true
	for sound in PLAYER_SOUNDS:
		var node: Node = player.get_node(sound)
		routed = routed and node is AudioStreamPlayer and node.bus == &"SFX" and node.stream != null
	check(routed, "player feedbacks are non-positional and routed to SFX")
	check(player.get_node("DeathSound").process_mode == Node.PROCESS_MODE_ALWAYS, "death sound ignores the death pause")
	for sound in ["HurtSound", "SwingSound"]:
		var stream = player.get_node(sound).stream
		check(stream is AudioStreamRandomizer and stream.streams_count == 3, "%s rotates three variants" % sound)
	player.position.x = 20
	Input.action_press("move_right")
	var silent_run := true
	var ran := 0.0
	for i in range(60):
		await frames(1)
		ran = maxf(ran, absf(player.velocity.x))
		silent_run = silent_run and player.is_on_floor() and only_playing([])
	Input.action_release("move_right")
	check(silent_run and ran > 90.0, "running on the ground plays no footstep")
	await spawn_room()
	await press("jump", 21)
	check(only_playing(["JumpSound"]), "ground jump plays only the jump sound")
	await release("jump")
	await press("jump")
	check(player.get_node("DoubleJumpSound").playing and player.jump_flash > 0.0, "double jump plays its dedicated sound")
	await release("jump", 80)
	await press("attack")
	check(player.attack_time > 0.0 and player.get_node("SwingSound").playing, "sword swing plays the swing sound")
	await release("attack", 70)

	await spawn_room(Vector2(194.92, 40))
	player.velocity.y = 100
	await frames(17)
	await press("jump")
	check(player.wall_jump_lockout and player.get_node("WallJumpSound").playing and not player.get_node("DoubleJumpSound").playing, "wall jump plays the wall jump sound")
	await release("jump")

	await spawn_room()
	player.take_damage(0.5, Vector2.ZERO)
	check(player.get_node("HurtSound").playing and not player.get_node("DeathSound").playing, "non-lethal damage plays the hit sound only")
	player.invulnerability = 0.0
	player.take_damage(5.0, Vector2.ZERO)
	check(player.dead and player.get_node("DeathSound").playing, "lethal damage plays the death sound")

	await spawn_level()
	var music: AudioStreamPlayer = level.get_node("Music")
	check(music.bus == &"Music" and music.playing and music.stream is AudioStreamOggVorbis and music.stream.loop, "slice music loops on the Music bus")
	var positional := true
	var slime: SliceSlime = level.get_node("Enemies/Slime1")
	for sound in ["HitSound", "DeathSound"]:
		positional = positional and slime.get_node(sound) is AudioStreamPlayer2D and slime.get_node(sound).bus == &"SFX"
	var coin: Node = level.get_node("Coins").get_child(0)
	positional = positional and coin.get_node("Sound") is AudioStreamPlayer2D and coin.get_node("Sound").bus == &"SFX"
	check(positional, "slime and coin sounds are 2D world sounds on SFX")
	check(level.get_node("GoldGate/Sound").bus == &"SFX", "gate sound joins the SFX bus")
	var enemy_count := level.get_node("Enemies").get_child_count()
	slime.take_damage(0.5, Vector2.ZERO)
	check(slime.get_node("HitSound").playing and not slime.dead, "non-lethal strike plays the melee hit on the slime")
	var splash: AudioStreamPlayer2D = slime.get_node("DeathSound")
	var at := slime.global_position
	slime.take_damage(5.0, Vector2.ZERO)
	check(splash.playing and splash.get_parent() == level and splash.global_position.distance_to(at) < 0.5, "slime death splash starts where it died")
	check(level.get_node("Enemies").get_child_count() == enemy_count, "enemy container only keeps enemies")
	await frames(30)
	check(not is_instance_valid(slime) and is_instance_valid(splash) and splash.playing, "splash outlives the removed slime")
	# Headless audio advances in real time, independently of --fixed-fps frames.
	var deadline := Time.get_ticks_msec() + 4000
	while is_instance_valid(splash) and Time.get_ticks_msec() < deadline:
		await process_frame
	check(not is_instance_valid(splash), "detached sounds free themselves once finished")
	var coin_sound: AudioStreamPlayer2D = coin.get_node("Sound")
	player.global_position = coin.global_position + Vector2(0, 8)
	await frames(3)
	check(coin_sound.playing, "coin pickup plays the pickup sound")

	await spawn_level()
	player.take_damage(5.0, Vector2.ZERO)
	await frames(30)
	check(paused and player.get_node("DeathSound").playing and not player.get_node("HurtSound").playing, "death sound keeps playing through the death pause")
	# Stop playbacks and let the mixer release them before quitting.
	for sound in root.find_children("*", "AudioStreamPlayer", true, false) + root.find_children("*", "AudioStreamPlayer2D", true, false):
		sound.stop()
	await clear_scene()
	var release_at := Time.get_ticks_msec() + 300
	while Time.get_ticks_msec() < release_at:
		await process_frame
	print("RESULT %d audio checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

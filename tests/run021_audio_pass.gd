# RUN-021 audio pass (8 Oct 2026): silent retractable spikes, N1 music, human jump cues, shared SFX hearing radius.
# Usage: bash work/run021/check.sh audio-pass --headless --script res://tests/run021_audio_pass.gd
extends SceneTree
const N1_MUSIC := "res://assets/run021/audio/music_n1_eidolon_vale.ogg"
const JUMP := "res://assets/sounds/run021/sfx_player_jump_human.wav"
const DOUBLE_JUMP := "res://assets/sounds/run021/sfx_player_double_jump_human.wav"
var checks := 0
var failures := 0
var room: Node2D

func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame
func reset() -> void:
	paused = false
	if is_instance_valid(room):
		room.queue_free()
		await frames()
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
func world_voices() -> Array:
	return room.find_children("*", "AudioStreamPlayer2D", true, false)

func run() -> void:
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	await spikes_are_silent()
	music_n1()
	jumps()
	await jumps_play()
	await n3_ambience()
	await hearing_radius()
	# Release the impact playbacks still running in the audio server before quitting.
	for voice in world_voices(): voice.stop()
	room.queue_free()
	await frames(4)
	print("RESULT %d audio checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

func spikes_are_silent() -> void:
	await reset()
	var player: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	# Falls onto the retracted base, inside the contact area, before the first extension (safe 1.5 s).
	player.position = Vector2(200, 140)
	room.add_child(player)
	var spikes: Node2D = load("res://scenes/retractable_spikes.tscn").instantiate()
	spikes.position = Vector2(200, 180)
	spikes.initial_phase = 0.0
	room.add_child(spikes)
	check(world_voices().is_empty(), "spikes: no positional player built")
	# Drive a full cycle (warning, extension, damage) and listen for any world SFX.
	var heard := false
	var hurt := false
	for i in 240:
		await physics_frame
		heard = heard or not world_voices().is_empty()
		hurt = hurt or player.health < player.max_health
	check(hurt, "spikes: cycle reached the damaging phase (health %.1f)" % player.health)
	check(not heard, "spikes: extension and hit stay silent through a full cycle")

func music_n1() -> void:
	for path in ["res://scenes/vertical_slice.tscn", "res://scenes/eidolon_vale.tscn"]:
		var level: Node = load(path).instantiate()
		var music := level.get_node("Music") as AudioStreamPlayer
		var stream := music.stream as AudioStreamOggVorbis
		check(stream != null and stream.resource_path == N1_MUSIC, "%s: Music stream = %s" % [path.get_file(), stream.resource_path if stream else "null"])
		check(music.bus == &"Music" and is_equal_approx(music.volume_db, -20.0), "%s: bus Music, volume -20 dB unchanged" % path.get_file())
		check(stream != null and stream.loop and is_zero_approx(stream.loop_offset), "%s: loops from 0" % path.get_file())
		check(stream != null and absf(stream.get_length() - 59.077) < 0.01, "%s: length %.3f s = 8 phrases" % [path.get_file(), stream.get_length() if stream else -1.0])
		level.free()

func jumps() -> void:
	var player: Node = load("res://scenes/player.tscn").instantiate()
	for pair in [["JumpSound", JUMP, 0.35], ["DoubleJumpSound", DOUBLE_JUMP, 0.30]]:
		var audio := player.get_node(pair[0]) as AudioStreamPlayer
		check(audio.stream != null and audio.stream.resource_path == pair[1], "%s stream = %s" % [pair[0], audio.stream.resource_path if audio.stream else "null"])
		check(audio.stream != null and absf(audio.stream.get_length() - pair[2]) < 0.02, "%s length %.2f s" % [pair[0], audio.stream.get_length() if audio.stream else -1.0])
		check(audio.bus == &"SFX", "%s on bus SFX" % pair[0])
	var wall := player.get_node("WallJumpSound") as AudioStreamPlayer
	check(wall.stream.resource_path == "res://assets/sounds/sfx_player_wall_jump.wav", "WallJumpSound stream unchanged")
	# Second pass: the wall cue sits under the jumps (RMS -22.8 dBFS file + node, vs -29.5 + -14 for the jump).
	check(is_equal_approx(wall.volume_db, -23.0) and wall.volume_db < (player.get_node("JumpSound") as AudioStreamPlayer).volume_db, "WallJumpSound node at -23 dB, under the jump node")
	player.free()

func n3_ambience() -> void:
	var level: Node = load("res://scenes/black_forrest.tscn").instantiate()
	var ambient := level.get_node("Ambient") as AudioStreamPlayer
	var stream := ambient.stream as AudioStreamOggVorbis
	check(stream != null and stream.resource_path == "res://assets/sounds/run021/amb_black_forrest_v2.ogg", "N3 Ambient stream = " + (stream.resource_path if stream else "null"))
	check(stream != null and stream.loop and absf(stream.get_length() - 28.0) < 0.01, "N3 ambience loops over 28 s")
	check(ambient.bus == &"Ambient" and is_equal_approx(ambient.volume_db, -8.0), "N3 ambience on bus Ambient, node -8 dB unchanged")
	root.add_child(level)
	await frames(5)
	check(ambient.playing, "N3 entry: ambience playing")
	# Release every playback of the level (music, ambience, mob cues) before freeing it.
	for type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for voice in level.find_children("*", type, true, false): voice.stop()
	level.queue_free()
	await frames(4)

func jumps_play() -> void:
	# Real input on a floor: the ground jump and the air jump each trigger their own new cue.
	await reset()
	var floor := StaticBody2D.new()
	floor.collision_layer = 9
	floor.position = Vector2(150, 208)
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = Vector2(600, 16)
	floor.add_child(shape)
	room.add_child(floor)
	var player: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	player.position = Vector2(100, 200)
	room.add_child(player)
	await frames(6)
	Input.action_press("jump")
	var jumped := false
	for i in 6:
		await frames(1)
		jumped = jumped or (player.get_node("JumpSound").playing and not player.get_node("DoubleJumpSound").playing)
	Input.action_release("jump")
	await frames(4)
	check(jumped and not player.is_on_floor(), "ground jump plays the human jump cue only")
	Input.action_press("jump")
	var doubled := false
	for i in 6:
		await frames(1)
		doubled = doubled or player.get_node("DoubleJumpSound").playing
	Input.action_release("jump")
	check(doubled, "air jump plays the human double-jump cue")
	await frames(2)

func hearing_radius() -> void:
	await reset()
	check(is_equal_approx(Run019Art.SFX_MAX_DISTANCE, 360.0), "shared hearing radius = 360 px")
	# Turret projectile impact (previously OneShotFx with Godot's 2000 px default).
	var wall := StaticBody2D.new()
	wall.position = Vector2(260, 180)
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = Vector2(4, 80)
	wall.add_child(shape)
	room.add_child(wall)
	var shot: Node2D = load("res://scenes/trap_projectile.tscn").instantiate()
	shot.position = Vector2(200, 180)
	room.add_child(shot)
	shot.setup(Vector2.RIGHT, 1200.0, 320.0)
	var impact: AudioStreamPlayer2D = null
	for i in 30:
		await physics_frame
		for voice in world_voices():
			if voice.stream != null and voice.stream.resource_path.ends_with("sfx_turret_projectile_impact.wav"): impact = voice
		if impact != null: break
	check(impact != null, "turret projectile impact plays its positional cue")
	check(impact != null and is_equal_approx(impact.max_distance, 360.0) and impact.bus == &"SFX", "turret impact: max_distance %.0f px on SFX" % (impact.max_distance if impact else -1.0))
	var fx := OneShotFx.spawn(room, load("res://assets/run019/world/vfx_turret_impact.png"), Vector2i(16, 16), 20.0, Vector2(100, 100), false, Vector2(0.5, 0.5), load("res://assets/sounds/sfx_arrow_impact.wav"), -6.0) if ResourceLoader.exists("res://assets/run019/world/vfx_turret_impact.png") else null
	if fx != null:
		var arrow_voice := fx.find_children("*", "AudioStreamPlayer2D", true, false)
		check(arrow_voice.size() == 1 and is_equal_approx(arrow_voice[0].max_distance, 360.0), "OneShotFx sound: max_distance 360 px")
	var holder := Node2D.new()
	room.add_child(holder)
	var voice := Run019Art.voice(holder, null)
	Run019Art.sound(holder, load("res://assets/sounds/sfx_arrow_impact.wav"), Vector2(50, 50))
	var detached: Array = room.find_children("*", "AudioStreamPlayer2D", true, false).filter(func(p): return p != voice and p.stream != null and p.stream.resource_path.ends_with("sfx_arrow_impact.wav") and p.get_parent() != fx)
	check(is_equal_approx(voice.max_distance, 360.0), "Run019Art.voice: max_distance 360 px")
	check(detached.size() >= 1 and detached.all(func(p): return is_equal_approx(p.max_distance, 360.0)), "Run019Art.sound: max_distance 360 px")
	for path in ["res://scenes/slime.tscn", "res://scenes/coin.tscn"]:
		var node: Node = load(path).instantiate()
		var players := node.find_children("*", "AudioStreamPlayer2D", true, false)
		check(not players.is_empty() and players.all(func(p): return is_equal_approx(p.max_distance, 360.0)), "%s: %d positional players at 360 px" % [path.get_file(), players.size()])
		node.free()

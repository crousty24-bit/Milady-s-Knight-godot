# RUN-010 mix stress capture, meant for Movie Maker:
# tools/run.sh --write-movie work/run-010-mix.avi --fixed-fps 60 --script res://tests/audio_mix_capture.gd
# The Master limiter is bypassed so the recorded peak is the real mix, over the slice music.
extends SceneTree
var level: Node2D
var player: SlicePlayer
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await physics_frame
func stack_on_player(node: Node2D) -> void:
	node.global_position = player.global_position + Vector2(12, 0)
func run() -> void:
	AudioServer.set_bus_effect_enabled(0, 0, false)
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	player = level.get_node("Player")
	for enemy in level.get_node("Enemies").get_children(): enemy.set_physics_process(false)
	await frames(90)
	print("MARK 1.5s music alone, then jump + swing + two slime kills + coin + player hit on one frame")
	var slimes := level.get_node("Enemies").get_children()
	for enemy in slimes.slice(0, 2): stack_on_player(enemy)
	var coin: Node2D = level.get_node("Coins").get_child(0)
	Input.action_press("jump")
	Input.action_press("attack")
	for enemy in slimes.slice(0, 2): enemy.take_damage(5.0, Vector2.ZERO)
	coin.global_position = player.global_position
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
	await frames(20)
	Input.action_release("jump")
	await frames(2)
	Input.action_press("jump")
	await frames(40)
	Input.action_release("jump")
	Input.action_release("attack")
	await frames(60)
	print("MARK 3.5s lethal hit and death sound")
	player.invulnerability = 0.0
	player.take_damage(5.0, Vector2.ZERO)
	await frames(120)
	for sound in root.find_children("*", "AudioStreamPlayer", true, false): sound.stop()
	level.queue_free()
	await frames(20)
	quit(0)

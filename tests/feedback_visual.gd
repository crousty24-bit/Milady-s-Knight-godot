# RUN-014 / RUN-029: render the coin pickup burst, the slime hit spray and the death splash in the slice.
extends SceneTree
var failures := 0
var checks := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func capture(name: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://work/run-029/elements/%s.png" % name)
	print("CAPTURE ", name)
func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://work/run-029/elements"))
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	level.get_node("Music").stop()
	var player: SlicePlayer = level.get_node("Player")
	for enemy in level.get_node("Enemies").get_children(): enemy.set_physics_process(false)
	# Walk into the first coin with real input.
	var coin: Area2D = level.get_node("Coins/Coin01")
	player.position = coin.position + Vector2(-30, 0)
	player.position.y = 144
	player.get_node("Camera2D").reset_smoothing()
	await frames(4)
	Input.action_press("move_right")
	for i in range(60):
		await frames(1)
		if coin.picked_up: break
	Input.action_release("move_right")
	await frames(2)
	check(coin.picked_up and coin.get_node("Sprite").animation == &"collect" and coin.get_node("Sprite").visible, "pickup plays the gold burst")
	await capture("coin-burst")
	await frames(22)  # 7 frames at 24 fps = 0.29 s
	check(not is_instance_valid(coin) or not coin.get_node("Sprite").visible, "burst ends without leaving a coin behind")
	# A non-lethal hit shows the recoil frames and a short goo spray.
	var wounded: SliceSlime = level.get_node("Enemies/Slime2")
	wounded.position = Vector2(315, 144) + Vector2(60, 0)
	wounded.set_physics_process(true)
	wounded.take_damage(0.5, Vector2(100, -150))
	await frames(2)
	var spray: Sprite2D = null
	for child in level.get_children():
		if child is Sprite2D and child.texture != null and child.texture.resource_path.ends_with("vfx_slime_hit.png"): spray = child
	check(spray != null and wounded.get_node("Sprite").animation == &"green_hit", "non-lethal hit plays recoil frames and a goo spray")
	await capture("slime-hit")
	await frames(20)
	check(not is_instance_valid(spray) and wounded.get_node("Sprite").animation == &"green", "spray ends and the slime resumes its patrol animation")
	# Finish a slime with the Sword: the splash stays where it died.
	player.position = Vector2(315, 144)
	player.facing = 1
	player.get_node("Camera2D").reset_smoothing()
	var target: SliceSlime = level.get_node("Enemies/Slime1")
	target.position = player.position + Vector2(22, 0)
	target.health_units = 5
	await frames(4)
	Input.action_press("attack")
	await frames(10)
	Input.action_release("attack")
	check(target.dead and target.get_node("Sprite").animation == &"green_death", "slime plays its death collapse animation")
	var splash: Sprite2D = null
	for child in level.get_children():
		if child is Sprite2D and child.texture != null and child.texture.resource_path.ends_with("vfx_slime_splash.png"): splash = child
	check(target.dead and splash != null, "slime death leaves a goo splash in the scene")
	await capture("slime-splash")
	await frames(40)  # 6 frames over 0.36 s plus a short tail
	check(not is_instance_valid(splash), "splash frees itself after playing")
	level.queue_free()
	await frames(2)
	OS.delay_msec(150)
	print("RESULT %d feedback visual checks; %d failures" % [checks, failures])
	quit(failures)

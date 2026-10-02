# RUN-012: render the Ashen Knight states in the authored slice and check that
# each gameplay state selects its animation. Captures go to work/run-012/.
extends SceneTree
var failures := 0
var checks := 0
var level: Node
var player: SlicePlayer

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
	root.get_texture().get_image().save_png("res://work/run-012/%s.png" % name)
	print("CAPTURE ", name)

func load_level(at: Vector2, facing: int = 1) -> void:
	if level != null:
		level.queue_free()
		await frames(2)
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	level.get_node("Music").stop()
	player = level.get_node("Player")
	player.position = at
	player.facing = facing
	player.get_node("Camera2D").reset_smoothing()
	for enemy in level.get_node("Enemies").get_children(): enemy.set_physics_process(false)
	await frames(6)

func release_all() -> void:
	for action in ["move_left", "move_right", "jump", "attack"]: Input.action_release(action)

func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://work/run-012"))
	await load_level(Vector2(170, 144))
	await frames(10)
	check(player.sprite.animation == &"idle", "standing selects idle")
	await capture("idle")
	Input.action_press("move_right")
	await frames(9)
	check(player.sprite.animation == &"run", "moving on the ground selects run")
	await capture("run")
	Input.action_press("jump")
	await frames(5)
	check(player.sprite.animation == &"rise", "rising selects rise")
	await capture("rise")
	Input.action_release("jump")
	await frames(14)
	check(player.sprite.animation == &"fall", "descending selects fall")
	await capture("fall")
	release_all()
	await frames(30)
	# Double jump puff stays drawn from the player's jump origin.
	Input.action_press("jump")
	await frames(10)
	Input.action_release("jump")
	await frames(1)
	Input.action_press("jump")
	await frames(3)
	check(player.jump_flash > 0.0, "double jump shows its air puff")
	await capture("double-jump")
	release_all()
	await frames(40)
	# Wall slide against the climbable wall of the upper branch.
	await load_level(Vector2(612, 0))
	var slid := false
	for direction in ["move_right", "move_left"]:
		Input.action_press(direction)
		for i in range(50):
			await frames(1)
			if player.motion_state == SlicePlayer.MotionState.WALL_SLIDE:
				slid = true
				break
		if slid: break
		Input.action_release(direction)
		await load_level(Vector2(612, 0))
	if slid: await frames(6)
	check(slid and player.sprite.animation == &"wall", "wall slide selects wall")
	await capture("wall-slide")
	release_all()
	# Sword phases on both sides against a real Slime target.
	for facing in [1, -1]:
		var side := "right" if facing == 1 else "left"
		for phase in [[2, 0, "guard"], [7, 1, "cut"], [13, 2, "follow"]]:
			await load_level(Vector2(315, 144), facing)
			var target: SliceSlime = level.get_node("Enemies/Slime1")
			target.position = player.position + Vector2(facing * 22, 0)
			await frames(2)
			Input.action_press("attack")
			await frames(phase[0])
			Input.action_release("attack")
			check(player.sprite.animation == &"attack" and player.sprite.frame == phase[1], "attack %s %s shows pose %d" % [side, phase[2], phase[1]])
			await capture("attack-%s-%s" % [side, phase[2]])
		check(player.hit_sparks.size() > 0 or player.attack_time <= 0.0, "impact spark spawned on %s hit" % side)
	await load_level(Vector2(315, 144))
	var target2: SliceSlime = level.get_node("Enemies/Slime1")
	target2.position = player.position + Vector2(22, 0)
	await frames(2)
	Input.action_press("attack")
	await frames(9)
	Input.action_release("attack")
	check(player.hit_sparks.size() == 1, "one hit leaves exactly one impact spark")
	await capture("attack-spark")
	# Hurt pose, then death collapse during the death pause.
	await load_level(Vector2(170, 144))
	player.take_damage(0.5, Vector2(-100, -150))
	await frames(2)
	check(player.sprite.animation == &"hurt", "contact damage selects hurt")
	await capture("hurt")
	await frames(40)
	player.die()
	await frames(1)
	await capture("death-0")
	await frames(30)
	check(paused and player.sprite.animation == &"dead" and player.sprite.frame == 3, "death collapse plays to the lying frame during the death pause")
	await capture("death-1")
	level.queue_free()
	await frames(2)
	OS.delay_msec(150)
	print("RESULT %d knight visual checks; %d failures" % [checks, failures])
	quit(failures)

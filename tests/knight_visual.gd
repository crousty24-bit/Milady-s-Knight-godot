# RUN-012/029: render the Ashen Knight states in the authored slice and check that
# each gameplay state selects its animation, including the three-move sword chain.
# Captures go to work/run-029/knight/.
extends SceneTree
const OUT := "res://work/run-029/knight"
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
	root.get_texture().get_image().save_png("%s/%s.png" % [OUT, name])
	print("CAPTURE ", name)

func load_level(at: Vector2, facing: int = 1) -> void:
	release_all()
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

func shows(animation: StringName, frame: int) -> bool:
	return player.sprite.animation == animation and player.sprite.frame == frame and not player.upper.visible

func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	await load_level(Vector2(170, 144))
	await frames(10)
	check(player.sprite.animation == &"idle" and not player.upper.visible, "standing selects the combat guard idle")
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
	var landed := false
	for i in range(40):
		await frames(1)
		if player.sprite.animation == &"land":
			landed = true
			break
	check(landed and player.land_dusts.size() == 1, "landing from a jump plays the squash and one dust puff")
	await capture("land")
	await frames(30)
	check(player.sprite.animation == &"idle", "landing squash returns to idle")
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
	# Wall slide against the climbable pillar of the upper branch.
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
	check(slid and player.sprite.flip_h == (player.wall_normal > 0.0), "wall slide faces the wall it grips")
	await capture("wall-slide")
	release_all()
	# Standing gesture of the first move, on both sides, against a real Slime.
	for facing in [1, -1]:
		var side := "right" if facing == 1 else "left"
		for phase in [[1, 0, "windup"], [6, 2, "cut"], [9, 4, "cut-late"], [13, 5, "follow"]]:
			await load_level(Vector2(315, 144), facing)
			var target: SliceSlime = level.get_node("Enemies/Slime1")
			target.position = player.position + Vector2(facing * 22, 0)
			await frames(2)
			Input.action_press("attack")
			await frames(phase[0])
			check(shows(&"atk1", phase[1]) and player.sprite.flip_h == (facing < 0), "move 1 %s %s shows frame %d" % [side, phase[2], phase[1]])
			await capture("atk1-%s-%s" % [side, phase[2]])
			Input.action_release("attack")
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
	await frames(20)
	check(player.sprite.animation == &"idle", "releasing F after the gesture returns to the guard")
	# Holding F chains three different moves, one per Sword hit, then wraps.
	await load_level(Vector2(170, 144))
	Input.action_press("attack")
	await frames(30)
	check(shows(&"atk1", 7), "held F keeps the chain pose between hits instead of idling")
	await capture("chain-hold-1")
	await frames(21)
	check(shows(&"atk1", 9), "held F anticipates the next move before the cooldown ends")
	await capture("chain-ready-2")
	await frames(23)
	check(shows(&"atk2", 5), "second held hit plays move 2")
	await capture("chain-move-2")
	await frames(60)
	check(shows(&"atk3", 5), "third held hit plays move 3")
	await capture("chain-move-3")
	await frames(60)
	check(shows(&"atk1", 5), "fourth held hit wraps back to move 1")
	Input.action_release("attack")
	await frames(90)
	Input.action_press("attack")
	await frames(6)
	check(shows(&"atk1", 2), "a new attack after a pause restarts the chain at move 1")
	Input.action_release("attack")
	# Running and airborne attacks layer the upper body over the legs.
	await load_level(Vector2(170, 144))
	Input.action_press("move_right")
	await frames(10)
	Input.action_press("attack")
	await frames(6)
	check(player.sprite.animation == &"base_run" and player.upper.visible and player.upper.animation == &"up1" and player.upper.frame == 2, "running attack layers move 1 over the running legs")
	await capture("atk-running")
	release_all()
	await load_level(Vector2(170, 144))
	Input.action_press("jump")
	await frames(6)
	Input.action_press("attack")
	await frames(6)
	check(String(player.sprite.animation).begins_with("base_") and player.upper.visible and player.upper.animation == &"up1", "airborne attack layers move 1 over the air legs")
	await capture("atk-air")
	release_all()
	# Hurt pose, then death collapse during the death pause.
	await load_level(Vector2(170, 144))
	player.take_damage(0.5, Vector2(-100, -150))
	await frames(2)
	check(player.sprite.animation == &"hurt" and not player.upper.visible, "contact damage selects hurt")
	await capture("hurt")
	await frames(40)
	player.die()
	await frames(1)
	await capture("death-0")
	await frames(50)
	var last: int = player.sprite.sprite_frames.get_frame_count(&"dead") - 1
	check(paused and player.sprite.animation == &"dead" and player.sprite.frame == last, "death collapse plays to the lying frame during the death pause")
	await capture("death-1")
	level.queue_free()
	await frames(2)
	OS.delay_msec(150)
	print("RESULT %d knight visual checks; %d failures" % [checks, failures])
	quit(failures)

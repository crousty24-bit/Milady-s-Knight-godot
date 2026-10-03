extends SceneTree

var checks := 0
var failures := 0
var level: Node2D
var player: SlicePlayer

func _initialize() -> void: call_deferred("run")

func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame

func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1

func run() -> void:
	var progress = root.get_node("Progression")
	check(not progress.persistence_enabled, "death test cannot change the player's real save")
	progress.banked_bonus = 37
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	player = level.get_node("Player")
	await frames(8)
	level._on_collected(15)
	check(level.gold == 15 and level.bonus == 0, "attempt retains all picked-up coins without awarding shard surplus")
	player.die()
	player.die()
	check(player.dead and player.health == 0 and level.bonus == 0 and progress.banked_bonus == 37, "duplicate death discards pending gains once and retains bank")
	check(level.hud.get_node("Overlay/Title").text == "Thou hast perished.", "death displays required English title")
	Input.action_press("interact")
	await frames(3)
	Input.action_release("interact")
	check(current_scene == level, "E cannot skip automatic death transition")
	await frames(166)
	check(current_scene == level and paused and player.dead, "dead scene remains visible for three seconds")
	await frames(20)
	var fade: ColorRect = level.hud.get_node("DeathFade")
	check(current_scene == level and fade.visible and fade.color.a > 0.0, "fade darkens the scene after three seconds")
	await frames(24)
	var first_level = current_scene
	check(first_level != level and not first_level.player.dead and first_level.player.health == 3.0 and not paused, "automatic reload restores life and unpauses")
	check(first_level.gold == 0 and first_level.bonus == 0 and not first_level.gate.opened and first_level.get_node("Coins").get_child_count() == 18 and progress.banked_bonus == 37, "new attempt clears gains and retains bank")
	await frames(240)
	check(current_scene == first_level and not first_level.player.dead and first_level.player.health == 3.0, "one reload only and waiting at spawn is safe")
	level = first_level
	player = level.player
	Input.action_press("attack")
	await frames(2)
	Input.action_release("attack")
	check(player.attack_time > 0.0, "second death starts during an active sword attack")
	player.die()
	check(player.attack_time == 0.0 and player.dead, "death cancels active sword attack")
	await frames(210)
	check(current_scene != level and current_scene.player.health == 3.0 and not paused, "attack death reloads once without input")
	level = current_scene
	player = level.player
	Input.action_press("pause")
	await frames(2)
	Input.action_release("pause")
	check(paused and level.paused, "pause is active before forced death")
	player.die()
	await frames(210)
	check(current_scene != level and current_scene.player.health == 3.0 and not paused, "death during pause completes reload and releases pause")
	current_scene.queue_free()
	await frames(3)
	OS.delay_msec(300)
	print("RESULT ", checks, " death transition checks; ", failures, " failures")
	quit(failures)

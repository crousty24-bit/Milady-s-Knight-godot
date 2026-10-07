extends SceneTree
var checks := 0
var failures := 0
var level: Node2D
var progress: Node
func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames()
func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1
func spawn() -> void:
	if is_instance_valid(level):
		level.queue_free()
		await frames()
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	await frames(6)
func enter_chest() -> void:
	level.player.position = Vector2(120, 144)
	level.player.velocity = Vector2.ZERO
	await frames()
func capture(label: String) -> void:
	if DisplayServer.get_name() == "headless": return
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://work/run016")
	root.get_texture().get_image().save_png("res://work/run016/" + label + ".png")
	await process_frame
func run() -> void:
	progress = root.get_node("Progression")
	progress.new_game()
	await spawn()
	check(not level.player.has_longbow and level.hud.get_node("Equipment/Melee").text == "> Sword 0" and level.hud.get_node("Equipment/Ranged").text == "  Empty", "fresh attempt has Sword0 and empty ranged slot")
	await tap("switch_equipment")
	check(level.player.active_slot == 0, "A cannot select an empty slot")
	await enter_chest()
	check(level.tutorial_chest.player_near(), "authored chest uses actual proximity overlap")
	await tap("interact")
	check(paused and level.modal == "context" and level.tutorial_chest.consumed, "E opens fixed reward and consumes chest for this attempt")
	await capture("reward")
	await tap("pause")
	check(not paused and level.tutorial_chest.consumed and not level.player.has_longbow, "Escape refuses reward and closes context without opening pause")
	await tap("interact")
	check(not paused and not level.player.has_longbow, "closed chest cannot grant reward on repeated E")
	await spawn()
	check(not level.tutorial_chest.consumed, "reset restores chest when Longbow not acquired")
	await enter_chest()
	await tap("interact")
	await tap("move_down")
	await tap("interact")
	check(not level.player.has_longbow and level.tutorial_chest.consumed and not paused, "explicit Refuse does not grant item or upgrade")
	await spawn()
	await enter_chest()
	await tap("interact")
	Input.action_press("interact")
	await frames(8)
	check(level.player.has_longbow and progress.equipment == {"melee": "Sword0", "ranged": "Longbow0"} and level.resume_pending, "held E accepts Longbow0 once without changing Sword0")
	Input.action_release("interact")
	await frames()
	await tap("switch_equipment")
	check(level.player.active_slot == 1 and level.hud.get_node("Equipment/Ranged").text == "> Longbow 0", "A selects ranged and updates HUD focus")
	await capture("equipped")
	var previous_gold: int = level.gold
	level._on_collected(15)
	level._on_enemy_defeated(2, Vector2(300, 120))
	check(level.gold == previous_gold + 15 and level.bonus == 2 and level.hud.get_node("Gold").text == "%02d/12" % (previous_gold + 15) and level.hud.get_node("BonusPending").text == "+2", "HUD exact after independent coins and shards collection")
	check(level.try_offering() and level.gold == previous_gold + 3 and level.hud.get_node("Gold").text == "%02d  OPEN" % (previous_gold + 3), "door payment preserves surplus coin display")
	level.player.die()
	await frames(210)
	level = current_scene
	check(level.player.has_longbow and level.tutorial_chest.consumed and level.gold == 0 and level.bonus == 0 and level.hud.get_node("Equipment/Ranged").text == "  Longbow 0", "death clears currencies but keeps equipment and suppresses duplicate chest")
	level.player.position = Vector2(176, 144)
	level.player.velocity = Vector2.ZERO
	await frames(6)
	check(not level.minor_potion.used and level.player.health == 3.0, "potion remains on terrain when player is full")
	level.player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
	await frames(4)
	check(level.minor_potion.used and level.player.health == 3.0 and level.hud.get_node("Health").text == "3", "physical potion overlap heals exactly 0.5 and updates HUD")
	level.player.invulnerability = 0
	level.player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
	await frames(4)
	check(level.player.health == 2.5, "consumed potion cannot heal twice")
	await spawn()
	level.player.take_damage(0.2, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
	level.player.position = Vector2(176, 144)
	level.player.velocity = Vector2.ZERO
	await frames(6)
	check(level.minor_potion.used and level.player.health == 3.0, "potion respawns and caps partial missing health at maximum")
	await capture("potion")
	# Failed durable acquisition leaves the free chest available for retry, no half reward.
	progress.equipment.ranged = ""
	await spawn()
	progress.storage_path = "res://work/run016-missing-dir/save.json"
	progress.persistence_enabled = true
	await enter_chest()
	await tap("interact")
	await tap("interact")
	check(not level.player.has_longbow and not level.tutorial_chest.consumed and level.tutorial_chest.save_failed, "disk failure grants nothing and restores chest for retry")
	progress.persistence_enabled = false
	progress.storage_error = OK
	await tap("interact")
	await tap("interact")
	check(level.player.has_longbow and level.tutorial_chest.consumed, "retry succeeds after storage repair without duplicate reward")
	progress.storage_path = "user://run016-reward-%d.json" % OS.get_process_id()
	progress.persistence_enabled = true
	progress.new_game()
	await spawn()
	await enter_chest()
	await tap("interact")
	await tap("interact")
	check(progress.equipment.ranged == "Longbow0" and FileAccess.get_file_as_string(progress.storage_path).contains("Longbow0"), "accepting reward immediately writes durable Longbow0")
	progress.equipment.ranged = ""
	progress.banked_shards = 123
	progress.load_progress()
	await spawn()
	check(level.player.has_longbow and level.tutorial_chest.consumed and progress.banked_shards == 0 and level.gold == 0 and level.bonus == 0, "cold reload restores actual saved weapon without duplicating chest or currencies")
	progress.persistence_enabled = false
	DirAccess.remove_absolute(ProjectSettings.globalize_path(progress.storage_path))
	level.queue_free()
	await frames()
	OS.delay_msec(300)
	print("RESULT ", checks, " reward checks; ", failures, " failures")
	quit(failures)

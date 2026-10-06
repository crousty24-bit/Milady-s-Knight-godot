# Render evidence of native N2-N4. Snapshot relocation is explicit: no route claim.
extends SceneTree
const PATHS = ["res://scenes/blight_town.tscn", "res://scenes/black_forrest.tscn", "res://scenes/forbidden_graveyard.tscn"]
var level: Node2D
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func snapshot(name: String, at: Vector2) -> void:
	paused = false
	level.player.position = at
	level.player.velocity = Vector2.ZERO
	level.player.controls_enabled = false
	await frames(3)
	level.camera.position_smoothing_enabled = false
	level.camera.reset_smoothing()
	level.camera.force_update_scroll()
	paused = true
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var capture := root.get_texture().get_image()
	check(capture.get_size() == Vector2i(640,360), "native 640x360 " + name)
	check(capture.save_png("res://work/run020/" + name + ".png") == OK, "capture " + name)
func close_scene() -> void:
	paused = true
	for kind in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for audio in root.find_children("*", kind, true, false): audio.stop()
	await create_timer(0.3, true).timeout
	level.queue_free()
	paused = false
	await frames(3)
func run() -> void:
	if DisplayServer.get_name() == "headless":
		check(false, "render requires display")
		quit(1)
		return
	var progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	progress.acquire_equipment("ranged", "Longbow0")
	for index in 3:
		level = load(PATHS[index]).instantiate()
		root.add_child(level)
		current_scene = level
		await frames(6)
		check(level.get_node("Backdrop").world_level == index + 2 and level.get_node("Decor").world_level == index + 2 and level.get_node("TerrainSkin").world_level == index + 2, "biome drawing scripts match world level")
		check(level.get_node("Ambient").playing and level.get_node("Ambient").bus == &"Ambient" and level.get_node("Ambient").stream.loop, "ambience runs on Ambient bus with forward loop")
		var ambient: AudioStreamPlayer = level.get_node("Ambient")
		ambient.play(ambient.stream.get_length() - 0.15)
		OS.delay_msec(600) # Audio advances on the native mixer clock, not fixed physics.
		await frames(1)
		check(ambient.playing and ambient.get_playback_position() < 1.0, "native ambience crosses end and loops")
		await snapshot("n%d-spawn" % (index + 2), Vector2(128,144))
		await snapshot("n%d-trap" % (index + 2), level.get_node("Hazards/Trapdoor").position + Vector2(-40, 0))
		await snapshot("n%d-combat" % (index + 2), level.get_node("Enemies/Enemy%d" % [10, 12, 14][index]).position + Vector2(-64, 0))
		# Both authored forks: upper/lower views use scene coin positions as landmarks.
		for fork in 2:
			for route in 2:
				var coin_index: int = [[[9, 11], [19, 20]], [[12, 14], [23, 25]], [[11, 13], [26, 29]]][index][fork][route]
				await snapshot("n%d-f%d-%s" % [index + 2, fork + 1, "upper" if route == 0 else "lower"], level.get_node("Coins/Coin%02d" % coin_index).position + Vector2(0, 12))
		if index == 2:
			await snapshot("n4-secret-closed", level.get_node("Exploration/SecretWall").position + Vector2(-28, 0))
			level.get_node("Exploration/SecretWall").receive_player_attack(1, SlicePlayer.DamageSource.CONTACT_MELEE)
			paused = false
			await frames(40)
			await snapshot("n4-secret-open", level.get_node("Items/MajorPotion").position + Vector2(-40, 12))
			await snapshot("n4-mechanism", level.get_node("Exploration/MechanismButton").position)
		await close_scene()
	print("RESULT %d render checks; %d failures" % [checks,failures])
	quit(1 if failures else 0)

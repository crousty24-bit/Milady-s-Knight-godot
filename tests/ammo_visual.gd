# Native render fixture of actual authored props/HUD; poses are injected for capture,
# so these images are not evidence of input traversal or human playtest.
extends SceneTree
var checks := 0
var failures := 0
var level: Node2D
var captures := "res://work/run021/ammo/captures"
func _initialize() -> void: call_deferred("run")
func frames(count: int = 4) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ",label)
func stop_audio(node: Node) -> void:
	if node is AudioStreamPlayer or node is AudioStreamPlayer2D: node.stop()
	for child in node.get_children(): stop_audio(child)
func cleanup() -> void:
	paused = false
	if not is_instance_valid(level): return
	stop_audio(level)
	OS.delay_msec(300)
	level.queue_free()
	await frames()
func capture(name: String) -> void:
	await frames()
	await RenderingServer.frame_post_draw
	check(root.get_texture().get_image().save_png(captures + "/" + name + ".png") == OK, "native capture " + name)
func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(captures))
	var store := root.get_node("Progression")
	store.persistence_enabled = false
	for scene in ["eidolon_vale", "blight_town", "black_forrest", "forbidden_graveyard"]:
		await cleanup()
		store.resume_scene = "res://scenes/" + scene + ".tscn"
		store.equipment = {"melee":"Sword0","ranged":"Longbow0"}
		store.ammo_entry = {"Longbow":10,"ThrowingKnives":12}
		level = load(store.resume_scene).instantiate()
		level.n1_intro_enabled = false
		root.add_child(level)
		current_scene = level
		level.player.controls_enabled = false
		level.player.set_physics_process(false)
		await frames()
		var props: Array[Node] = []
		for node in level.find_children("*","StaticBody2D",true,false):
			if node.get_script() == load("res://scripts/ammo_prop.gd"): props.append(node)
		check(not props.is_empty(), scene + " contains actual ammo props")
		for prop in props:
			var art: AnimatedSprite2D = prop.get_node("Art")
			check(art.sprite_frames.get_frame_count(art.animation) == 1, scene + " family matches intact presentation " + str(prop.name))
			var from: Vector2 = prop.global_position + Vector2(0,-1)
			var ray := PhysicsRayQueryParameters2D.create(from, from + Vector2(0,5),1)
			check(not prop.get_world_2d().direct_space_state.intersect_ray(ray).is_empty(), scene + " prop rests on authored support " + str(prop.name))
		var focus: Node2D = props[0]
		var cam: Camera2D = level.camera
		cam.top_level = true
		cam.position_smoothing_enabled = false
		cam.limit_left = -100000
		cam.limit_right = 100000
		cam.limit_top = -100000
		cam.limit_bottom = 100000
		cam.global_position = focus.global_position + Vector2(80,-60)
		cam.reset_smoothing()
		level.player.global_position = focus.global_position + Vector2(-45,0)
		level.player.facing = 1
		level._update_equipment_hud(0)
		check(level.hud.get_node("Equipment/AmmoCount").text == "10/15",scene + " ranged counter initially shows10/15")
		await capture(scene + "-ammo")
		focus.drop_weights.assign([0,0,0,1])
		focus.receive_player_attack(0.5,SlicePlayer.DamageSource.CONTACT_MELEE)
		await frames(2)
		await capture(scene + "-break")
		if scene == "blight_town":
			for trap in level.get_node("Hazards").get_children():
				if trap.get_script() != load("res://scripts/retractable_spikes.gd") or not is_zero_approx(trap.rotation): continue
				trap.safe_duration = 100.0
				trap.cycle_time = 0.0
				trap._update_phase()
				cam.global_position = trap.global_position + Vector2(60,-60)
				cam.reset_smoothing()
				level.player.global_position = trap.global_position + Vector2(-35,0)
				await capture("spikes-retracted")
				trap.cycle_time = 100.1
				trap._update_phase()
				await capture("spikes-warning")
				trap.cycle_time = 100.6
				trap._update_phase()
				await capture("spikes-extended")
				break
			level.player.ammo.Longbow = 0
			level._update_equipment_hud(1)
			level.hud.show_ammo_empty("Longbow")
			await capture("hud-empty")
			level.player.configure_loadout({"melee":"Sword0","ranged":"ThrowingKnives0"})
			level.player.ammo.ThrowingKnives = 20
			level._update_equipment_hud(1)
			level.hud.show_ammo_pickup("ThrowingKnives",3)
			await capture("hud-knives-full")
	await cleanup()
	print("RESULT %d ammo native render checks; %d failures" % [checks,failures])
	quit(1 if failures else 0)

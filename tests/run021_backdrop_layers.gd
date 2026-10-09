# RUN-021: regressions for full-screen backdrops occluding world sprites.
extends SceneTree
const PLATFORM = preload("res://scenes/moving_platform.tscn")
var checks := 0
var failures := 0
func _initialize() -> void:
	call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func capture() -> Image:
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	return root.get_texture().get_image()
func changed_pixels(a: Image, b: Image, bounds: Rect2i = Rect2i()) -> int:
	var count := 0
	var region := bounds
	if region.size == Vector2i.ZERO:
		region = Rect2i(Vector2i.ZERO, a.get_size())
	region.position.x = clampi(region.position.x, 0, a.get_width())
	region.position.y = clampi(region.position.y, 0, a.get_height())
	region.size.x = mini(region.size.x, a.get_width() - region.position.x)
	region.size.y = mini(region.size.y, a.get_height() - region.position.y)
	for y in range(region.position.y, region.end.y):
		for x in range(region.position.x, region.end.x):
			if a.get_pixel(x, y) != b.get_pixel(x, y): count += 1
	return count
func freeze_tree(node: Node, states: Array) -> void:
	states.append([node, node.process_mode, node.is_processing(), node.is_physics_processing()])
	node.process_mode = Node.PROCESS_MODE_DISABLED
	node.set_process(false)
	node.set_physics_process(false)
	for child in node.get_children(): freeze_tree(child, states)
func unfreeze_tree(states: Array) -> void:
	for state in states:
		var node: Node = state[0]
		node.process_mode = state[1]
		node.set_process(state[2])
		node.set_physics_process(state[3])
func verify_scene_layering(scene_path: String, backdrop_name: String) -> void:
	var level := load(scene_path).instantiate() as Node2D
	root.add_child(level)
	current_scene = level
	await frames(2)
	var backdrop := level.get_node(backdrop_name) as CanvasItem
	check(backdrop.z_index == -100 and not backdrop.z_as_relative, scene_path.get_file() + " backdrop stays behind world sprites")
	level.queue_free()
	await frames(2)
func verify_inserted_platform(scene_path: String, player_position: Vector2, added_under_platforms: bool) -> void:
	var level := load(scene_path).instantiate() as Node2D
	root.add_child(level)
	current_scene = level
	paused = false
	await frames(4)
	var player = level.get_node("Player")
	player.position = player_position
	player.velocity = Vector2.ZERO
	level.camera.reset_smoothing()
	await frames(35)
	var platforms := level.get_node("Platforms") as Node2D
	var original := level.get_node_or_null("Platforms/Ferry") as AnimatableBody2D
	if scene_path.ends_with("blight_town.tscn") and original != null:
		original.elapsed = 0.0
		original.position = original.origin
		await frames(1)
		var original_screen := level.get_viewport().get_canvas_transform() * original.global_position
		var original_bounds := Rect2i(Vector2i(original_screen.round()) - Vector2i(28, 22), Vector2i(56, 44))
		var original_states: Array = []
		freeze_tree(level, original_states)
		var ferry_visible := await capture()
		original.visible = false
		var ferry_hidden := await capture()
		original.visible = true
		var ferry_diff := changed_pixels(ferry_visible, ferry_hidden, original_bounds)
		var capture_path := "res://work/run021/captures/ferry-backdrop-visible-n2.png"
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://work/run021/captures"))
		check(ferry_visible.save_png(ProjectSettings.globalize_path(capture_path)) == OK, "saved N2 ferry visible capture")
		check(ferry_diff >= 20, "original N2 ferry is rendered at the camera-framed location (%d changed pixels)" % ferry_diff)
		unfreeze_tree(original_states)
	if added_under_platforms:
		level.move_child(platforms, 0)
	var added := PLATFORM.instantiate() as AnimatableBody2D
	added.position = platforms.to_local(player.global_position + Vector2(112, -56))
	platforms.add_child(added)
	added.travel = Vector2(48, 0)
	added.period = 4.0
	await frames(36)
	check(absf(added.global_position.x - (player.global_position.x + 112.0)) > 1.0, scene_path.get_file() + " newly inserted platform moves from its edited transform")
	# Hide any original platform so the pixel comparison isolates the inserted instance.
	var original_visual := level.get_node_or_null("Platforms/Ferry") as CanvasItem
	if original_visual != null: original_visual.visible = false
	var inserted_screen := level.get_viewport().get_canvas_transform() * added.global_position
	var inserted_bounds := Rect2i(Vector2i(inserted_screen.round()) - Vector2i(28, 22), Vector2i(56, 44))
	var inserted_states: Array = []
	freeze_tree(level, inserted_states)
	var visible_image := await capture()
	added.visible = false
	var hidden_image := await capture()
	var diff := changed_pixels(visible_image, hidden_image, inserted_bounds)
	check(diff >= 20, scene_path.get_file() + " z=0 inserted platform is visible over backdrop (%d changed pixels)" % diff)
	paused = false
	level.queue_free()
	await frames(3)
func run() -> void:
	if DisplayServer.get_name() == "headless":
		check(false, "backdrop visibility regression requires rendered viewport")
		quit(1)
		return
	var progression = root.get_node("Progression")
	progression.persistence_enabled = false
	progression.new_game()
	await verify_scene_layering("res://scenes/blight_town.tscn", "Backdrop")
	await verify_scene_layering("res://scenes/black_forrest.tscn", "Backdrop")
	await verify_scene_layering("res://scenes/forbidden_graveyard.tscn", "Backdrop")
	# Move Platforms before Backdrop to reproduce the scene-tree order from the report.
	await verify_inserted_platform("res://scenes/vertical_slice.tscn", Vector2(220, 144), true)
	await verify_inserted_platform("res://scenes/blight_town.tscn", Vector2(1032, 112), true)
	print("RESULT %d backdrop-layer checks; %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)

# Camera framing uses injected poses; riding() separately exercises real ferry/player physics.
extends SceneTree
var checks := 0
var failures := 0
var level: Node2D
func _initialize() -> void: call_deferred("run")
func frames(count: int = 5) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func stop_audio(node: Node) -> void:
	if node is AudioStreamPlayer or node is AudioStreamPlayer2D: node.stop()
	for child in node.get_children(): stop_audio(child)
func cleanup() -> void:
	stop_audio(level)
	OS.delay_msec(300)
	level.queue_free()
	await frames()
func pose(where: Vector2) -> Vector2:
	level.player.global_position = where
	level.camera.reset_smoothing()
	level.camera.force_update_scroll()
	await frames(8)
	return level.camera.get_screen_center_position()
func run() -> void:
	root.get_node("Progression").persistence_enabled = false
	level = load("res://scenes/blight_town.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	level.player.controls_enabled = false
	level.player.set_physics_process(false)
	level.set_physics_process(false)
	await frames()
	var terrain: TileMapLayer = level.get_node("Terrain")
	var used := terrain.get_used_rect()
	print("PROBE terrain cells=", used, " tile_size=", terrain.tile_set.tile_size, " old_bounds=", level.camera_bounds, " actual_limits=", Vector2(level.camera.limit_top,level.camera.limit_bottom))
	var ferry: AnimatableBody2D = level.get_node("Platforms/Ferry2")
	print("PROBE Ferry2 global_origin=", ferry.get_parent().to_global(ferry.origin), " global_travel=", ferry.travel)
	var before := "before" in OS.get_cmdline_user_args()
	var ferry_origin: Vector2 = ferry.get_parent().to_global(ferry.origin)
	var low := await pose(ferry_origin + Vector2(0, -2))
	var high := await pose(Vector2(ferry_origin.x,-305))
	var extension := await pose(Vector2(3696,-352))
	print("PROBE center low=", low, " high=", high, " extension=", extension, " viewport=", root.get_visible_rect().size)
	if before:
		check(absf(low.y-high.y) < 1.0, "BEFORE camera remains clamped while player climbs 130px")
		check(extension.y - (-352.0) > root.get_visible_rect().size.y / 2.0, "BEFORE player above viewport at highest authored N2 terrain")
	else:
		check(high.y < low.y-100, "N2 real camera follows vertical climb")
		check(absf(high.y-(-305.0-38.0)) < 1.0, "N2 high player retains authored vertical framing")
		check(absf(extension.y-(-352.0-38.0)) < 1.0, "N2 high extension retains framing")
	if not before:
		await extensions()
		await riding()
	await cleanup()
	print("RESULT %d checks; %d failures" % [checks,failures])
	quit(1 if failures else 0)


func fixture(configure: Callable = Callable(), rider: bool = false) -> void:
	if is_instance_valid(level): await cleanup()
	level = load("res://scenes/blight_town.tscn").instantiate()
	# Isolate camera tests from combat; keep all authored terrain/platforms.
	for group in ["Enemies", "Hazards"]:
		for node in level.get_node(group).get_children(): node.free()
	if configure.is_valid(): configure.call(level)
	root.add_child(level)
	current_scene = level
	level.player.controls_enabled = false
	level.player.set_physics_process(rider)
	level.set_physics_process(false)
	await frames()

func visible_player() -> bool:
	var view := root.get_visible_rect()
	var transform := root.get_canvas_transform()
	return view.has_point(transform * level.player.global_position) and view.has_point(transform * (level.player.global_position + Vector2(0, -20)))

func add_extension(at: Vector2i) -> void:
	var terrain: TileMapLayer = level.get_node("Terrain")
	var source: Vector2i = terrain.get_used_cells()[0]
	terrain.set_cell(at, terrain.get_cell_source_id(source), terrain.get_cell_atlas_coords(source), terrain.get_cell_alternative_tile(source))

func capture(label: String) -> void:
	if "render" not in OS.get_cmdline_user_args(): return
	await RenderingServer.frame_post_draw
	var directory := "res://work/run021/camera/captures"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	check(root.get_texture().get_image().save_png(directory + "/" + label + ".png") == OK, "native camera capture " + label)

func extensions() -> void:
	check(level.camera.limit_left == 0 and level.camera.limit_right == 3840, "N2 horizontal authored boundaries are preserved")
	check(level.camera.limit_top == -592 and level.camera.limit_bottom == 784, "N2 camera includes upper terrain and authored lower slime room")
	check(level.camera_bounds == Rect2(0, -224, 3840, 528), "authored minimum bounds remain editable and unmodified")
	check(visible_player(), "actual N2 high player body remains within viewport")
	await pose(Vector2(3602, -305))
	await capture("n2-upper-area")
	await fixture(func(_scene):
		add_extension(Vector2i(225, -40))
		add_extension(Vector2i(225, 40)))
	var upper := await pose(Vector2(3602, -650))
	check(absf(upper.y + 688.0) < 1.0 and visible_player(), "future terrain painted higher before load is followed without camera edits")
	var lower := await pose(Vector2(3602, 640))
	check(absf(lower.y - 602.0) < 1.0 and visible_player(), "future lower terrain also expands the camera framing")
	check(level.camera.limit_top == -896 and level.camera.limit_bottom == 896, "future tiles expand both vertical limits only")
	check(level.void_y == 304.0, "camera adaptation does not change the separate lethal fall threshold")
	await fixture(func(scene): scene.auto_camera_vertical_bounds = false)
	var manual := await pose(Vector2(3602, -305))
	var manual_top_center: float = level.camera.limit_top + root.get_visible_rect().size.y * 0.5 / level.camera.zoom.y
	check(absf(manual.y - manual_top_center) < 1.0 and level.camera.limit_top == -224, "automatic mode can be disabled for authored fixed framing at current zoom")
	await fixture(func(scene):
		var terrain: TileMapLayer = scene.get_node("Terrain")
		terrain.position.y = -80.0
		terrain.scale.y = 2.0)
	var transformed := await pose(Vector2(3602, -760))
	check(absf(transformed.y + 798.0) < 1.0 and visible_player(), "terrain vertical translation and scaling use world-space heights")
	await fixture(func(scene): scene.get_node("Player/Camera2D").zoom = Vector2(0.5, 0.5))
	var zoomed := await pose(Vector2(3602, -336))
	check(absf(zoomed.y + 374.0) < 1.0 and visible_player(), "zoomed-out viewport gets sufficient vertical margin")
	await fixture(func(scene): scene.get_node("Platforms/Ferry2").travel = Vector2(0, -600))
	var endpoint := await pose(Vector2(3602, -776))
	check(absf(endpoint.y + 814.0) < 1.0 and visible_player(), "complete upward ferry trajectory is included even above existing terrain")
	check(level.camera.limit_top == -1029, "ferry endpoint rather than current phase defines its camera envelope")

func riding() -> void:
	await fixture(func(scene):
		var ferry: AnimatableBody2D = scene.get_node("Platforms/Ferry2")
		scene.get_node("Player").position = ferry.get_parent().to_global(ferry.position) + Vector2(0, -3), true)
	# Ride from the authored initial pose, then sample the descent above the floor.
	await frames(115)
	var ferry: AnimatableBody2D = level.get_node("Platforms/Ferry2")
	var low: Vector2 = level.camera.get_screen_center_position()
	var low_player: Vector2 = level.player.global_position
	check(level.player.is_on_floor(), "real player rides authored Ferry2 before its lower turning point")
	# Follow a complete ascent using the platform's actual period, rather than
	# frame counts from its former shorter trajectory. Bound the wait on failure.
	for i in ceili(ferry.period * Engine.physics_ticks_per_second):
		if ferry.elapsed >= ferry.period: break
		await frames(1)
	var high: Vector2 = level.camera.get_screen_center_position()
	print("RIDE camera=", low, " -> ", high, " player=", low_player, " -> ", level.player.global_position)
	check(ferry.elapsed >= ferry.period and absf(ferry.global_position.y - ferry.get_parent().to_global(ferry.origin).y) < 1.0, "real ferry completes ascent to its upper turning point")
	check(level.player.is_on_floor() and absf(level.player.global_position.y - ferry.global_position.y + 3.0) < 1.0, "real ascending Ferry2 carries the player without pose injection during movement")
	check(high.y < low.y - 100.0 and visible_player(), "smoothed camera follows the real ascending ferry and keeps player visible")
	check(absf(high.y - level.player.global_position.y + 38.0) < 10.0, "ascending ferry retains normal framing with bounded smoothing lag")
	await capture("n2-ferry-ascent")

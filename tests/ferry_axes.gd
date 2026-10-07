extends SceneTree
var checks := 0
var failures := 0
var room: Node2D
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)
func run() -> void:
	room = Node2D.new()
	root.add_child(room)
	current_scene = room
	var level: Node2D = load("res://scenes/blight_town.tscn").instantiate()
	var platforms: Node2D = level.get_node("Platforms")
	level.remove_child(platforms)
	platforms.owner = null
	room.add_child(platforms)
	level.free()
	var ferry: AnimatableBody2D = platforms.get_node("Ferry")
	var ferry2: AnimatableBody2D = platforms.get_node("Ferry2")
	var start := ferry2.position
	print("PROBE Ferry travel=", ferry.travel, " Ferry2 travel=", ferry2.travel, " start=", start)
	await frames(120)
	print("PROBE Ferry2 half-period position=", ferry2.position, " elapsed=", ferry2.elapsed)
	check(ferry.travel == Vector2(144, 0), "N2 first Ferry keeps horizontal travel")
	check(ferry2.travel == Vector2(0, 144), "N2 second Ferry has explicit vertical travel matching authored intent")
	check(ferry.get_script() == load("res://scripts/moving_platform.gd") and ferry2.get_script() == ferry.get_script(), "N2 both ferries use unchanged shared movement script")
	check(absf(ferry2.position.x-start.x) < 0.1 and absf(ferry2.position.y-start.y-ferry2.travel.y) < 0.2, "N2 second Ferry reaches vertical endpoint after half-period")
	await frames(120)
	print("PROBE Ferry2 full-period position=", ferry2.position, " elapsed=", ferry2.elapsed)
	check(ferry2.position.distance_to(start) < 0.2, "N2 second Ferry returns to authored origin after full-period")
	var before_pause := ferry2.position
	var elapsed_pause: float = ferry2.elapsed
	paused = true
	await frames(30)
	check(ferry2.position == before_pause and ferry2.elapsed == elapsed_pause, "N2 Ferry freezes both position and time while paused")
	paused = false
	await frames(30)
	check(ferry2.elapsed > elapsed_pause and ferry2.position != before_pause, "N2 Ferry resumes on same motion cycle")
	platforms.queue_free()
	await frames(3)
	for scene in ["moving_platform", "moving_platform_vertical"]:
		var platform: AnimatableBody2D = load("res://scenes/%s.tscn" % scene).instantiate()
		check((not is_zero_approx(platform.travel.x) and is_zero_approx(platform.travel.y)) if scene == "moving_platform" else (platform.travel == Vector2(0, 144)), "%s scene default selects its named axis" % scene)
		platform.free()
		for direction in [Vector2(64, 0), Vector2(0, -64), Vector2(0, 64)]:
			await check_carrier(scene, direction)
	room.queue_free()
	await frames(3)
	print("RESULT %d checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

func check_carrier(scene: String, direction: Vector2) -> void:
	var platform: AnimatableBody2D = load("res://scenes/%s.tscn" % scene).instantiate()
	platform.position = Vector2(240, 200)
	platform.travel = direction
	platform.period = 4.0
	room.add_child(platform)
	var player: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	player.position = platform.position + Vector2(0, -3)
	room.add_child(player)
	await frames(12)
	check(player.is_on_floor(), "%s axis %s real player lands on ferry" % [scene, direction])
	var offset := player.position - platform.position
	await frames(75)
	check(player.is_on_floor() and (player.position - platform.position).distance_to(offset) < 2, "%s axis %s carries actual idle player without sliding off" % [scene, direction])
	check((platform.position - platform.origin).length() > 30 and (absf(platform.position.y - platform.origin.y) < 0.1 if direction.y == 0 else absf(platform.position.x - platform.origin.x) < 0.1), "%s inspector Travel override moves only requested axis %s" % [scene, direction])
	for child in player.get_children():
		if child is AudioStreamPlayer or child is AudioStreamPlayer2D: child.stop()
	OS.delay_msec(300)
	player.queue_free()
	platform.queue_free()
	await frames(3)

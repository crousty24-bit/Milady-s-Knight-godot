# Plays both authored routes using the public input actions and live physics.
# No teleportation, health/gold changes or enemy removal.
extends SceneTree
var failures: int = 0
var level: Node2D
var player: SlicePlayer
func _initialize() -> void: call_deferred("run")
func frame() -> void: await physics_frame
func release_inputs() -> void:
	for action in ["move_left","move_right","jump","attack","interact"]: Input.action_release(action)
func play_route(upper: bool) -> void:
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	player = level.get_node("Player")
	for i in range(10): await frame()
	var jumps: Array = [470,548,645,820,999,1160,1280,1365,1515] if upper else [852,1004,1267,1331,1390,1515]
	var jump_index: int = 0
	var jump_frames: int = 0
	var last_x: float = player.position.x
	var stuck: int = 0
	for tick in range(4200):
		if player.dead or level.finished: break
		Input.action_release("attack")
		Input.action_release("interact")
		Input.action_release("move_left")
		Input.action_press("move_right")
		if jump_frames > 0:
			jump_frames -= 1
		else:
			Input.action_release("jump")
		if jump_index < jumps.size() and player.position.x >= jumps[jump_index] and player.is_on_floor():
			Input.action_press("jump")
			jump_frames = 32
			print("JUMP ",upper," #",jump_index," pos=",player.position)
			jump_index+=1
		for enemy in level.get_node("Enemies").get_children():
			if enemy.dead: continue
			var distance: Vector2 = enemy.position-player.position
			if absf(distance.y)<18 and absf(distance.x)<38:
				if distance.x > 0 and distance.x<27: Input.action_release("move_right")
				if distance.x<0:
					Input.action_release("move_right")
					Input.action_press("move_left")
				if tick%24==0: Input.action_press("attack")
		if level.gate.player_near() and not level.gate.opened:
			if tick%10==0: Input.action_press("interact")
		await frame()
		if absf(player.position.x-last_x)<0.05: stuck+=1
		else: stuck=0
		last_x=player.position.x
		if stuck>240:
			print("STUCK route=",upper," pos=",player.position," gold=",level.gold," hp=",player.health," jumps=",jump_index)
			break
	release_inputs()
	var ok: bool = level.finished and not player.dead
	print("PASS " if ok else "FAIL ","route ","upper" if upper else "lower"," pos=",player.position," gold=",level.gold," hp=",player.health)
	if not ok: failures+=1
	if DisplayServer.get_name()!="headless":
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://work/route-"+("upper" if upper else "lower")+".png")
	level.queue_free()
	await process_frame
func run() -> void:
	await play_route(true)
	await play_route(false)
	print("ROUTE FAILURES ",failures)
	OS.delay_msec(150)
	quit(failures)

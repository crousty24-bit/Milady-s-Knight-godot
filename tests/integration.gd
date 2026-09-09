extends SceneTree
var failures: int = 0
var checks: int = 0
var level: Node2D
var player: SlicePlayer
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await physics_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func spawn() -> void:
	if is_instance_valid(level):
		level.queue_free()
		await process_frame
	level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	player = level.get_node("Player")
	await frames(10)
func teleport(pos: Vector2) -> void:
	player.position = pos
	player.velocity = Vector2.ZERO
	await frames(3)
func tap(action: String, count: int = 2) -> void:
	Input.action_press(action)
	await frames(count)
	Input.action_release(action)
	await frames(2)
func run() -> void:
	await spawn()
	check(level.get_node("Coins").get_child_count()==18,"exactly 18 authored coins")
	check(level.get_node("Enemies").get_child_count()==8,"exactly four extra slimes, eight total")
	var purple_count := 0
	for slime in level.get_node("Enemies").get_children():
		if slime.variant == SliceSlime.Kind.PURPLE: purple_count += 1
	check(purple_count==3,"five Green and three Purple")
	var counts = [0,0,0]
	for coin in level.get_node("Coins").get_children(): counts[coin.route]+=1
	check(counts==[8,5,5],"route distribution 8 / 5 / 5")
	var first = level.get_node("Coins").get_child(0)
	await teleport(first.position+Vector2(0,8))
	await frames(3)
	check(level.gold==1,"actual coin collision increments gold")
	if is_instance_valid(first):
		first._on_body_entered(player)
		check(level.gold==1,"same coin cannot be collected twice")
	level.gold=11
	check(not level.try_offering() and level.gold==11 and not level.gate.opened,"11 gold refuses without charge")
	level.gold=12
	check(level.try_offering() and level.gold==0 and level.gate.opened,"12 gold pays and opens")
	check(not level.try_offering() and level.gold==0,"offering cannot charge twice")
	await teleport(Vector2(2160,140))
	await frames(3)
	check(level.finished,"actual exit area triggers victory after offering")
	await spawn()
	await teleport(Vector2(2160,140))
	check(not level.finished,"exit area refuses victory while sealed")
	# Combat with a live physics body; isolate encounter position, do not call damage directly.
	await teleport(Vector2(315,144))
	var enemy = level.get_node("Enemies/Slime1")
	enemy.position=Vector2(339,144)
	enemy.origin_x=339
	enemy.patrol_left=0
	enemy.patrol_right=0
	player.facing=1
	await tap("attack")
	await frames(13)
	check(enemy.health==2,"sword overlaps enemy: one damage per swing")
	await frames(12)
	enemy.position=Vector2(339,144)
	enemy.velocity=Vector2.ZERO
	await frames(3)
	await tap("attack")
	await frames(16)
	check(is_instance_valid(enemy) and enemy.health==1 and not enemy.dead,"Green survives two sword strikes")
	await frames(12)
	enemy.position=Vector2(339,144)
	enemy.velocity=Vector2.ZERO
	await frames(3)
	await tap("attack")
	await frames(16)
	check(not is_instance_valid(enemy) or enemy.dead,"third sword strike kills Green")
	# Player damage, invulnerability, death idempotency.
	player.invulnerability=0
	player.take_damage(1,Vector2.ZERO)
	check(player.health==2 and not player.dead,"contact damage leaves two HP")
	player.take_damage(1,Vector2.ZERO)
	check(player.health==2,"invulnerability blocks repeated impact")
	await frames(55)
	player.take_damage(1,Vector2.ZERO)
	check(player.health==1,"damage resumes after invulnerability")
	player.invulnerability=0
	player.take_damage(1,Vector2.ZERO)
	player.die()
	check(player.dead and player.health==0,"death is stable and health cannot become negative")
	# Restart through the real action and SceneTree reload.
	await tap("restart")
	await frames(12)
	level=current_scene
	player=level.get_node("Player")
	check(level.gold==0 and player.health==3 and not level.gate.opened and level.get_node("Coins").get_child_count()==18,"restart restores whole attempt")
	await tap("pause")
	check(paused,"escape pauses tree")
	var before: Vector2 = player.position
	Input.action_press("move_right")
	await frames(5)
	Input.action_release("move_right")
	check(player.position==before,"paused player cannot move")
	await tap("pause")
	check(not paused,"escape resumes tree")
	await teleport(Vector2(880,290))
	await frames(15)
	check(player.dead,"pit causes death through actual area collision")
	level.queue_free()
	await process_frame
	print("RESULT ",checks," checks; ",failures," failures")
	OS.delay_msec(150)
	quit(failures)

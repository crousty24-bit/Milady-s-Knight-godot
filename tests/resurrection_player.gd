extends SceneTree

var failures := 0
var checks := 0
var events := [0, 0, 0]

func _initialize() -> void:
	call_deferred("run")

func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame

func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok:
		failures += 1

func run() -> void:
	var room := Node2D.new()
	root.add_child(room)
	current_scene = room
	var player: SlicePlayer = load("res://scenes/player.tscn").instantiate()
	room.add_child(player)
	await frames(1)
	player.died.connect(func(): events[0] += 1)
	player.health_changed.connect(func(_hp: float, _maximum: float): events[1] += 1)
	player.projectile_fired.connect(func(_arrow: Node2D): events[2] += 1)
	# Explicit fallback fixture remains valid after Claude adds the dedicated strip.
	var authored := player.sprite.sprite_frames.duplicate() as SpriteFrames
	if authored.has_animation(&"resurrect"): authored.remove_animation(&"resurrect")
	player.sprite.sprite_frames = authored
	var dead_count := authored.get_frame_count(&"dead")
	var dead_loop := authored.get_animation_loop(&"dead")
	var dead_speed := authored.get_animation_speed(&"dead")
	var dead_texture := authored.get_frame_texture(&"dead", dead_count - 1)
	var hp := player.health_units
	var max_hp := player.max_health_units
	player.sprite.flip_h = true
	player.sprite.scale = Vector2(1.25, 0.9)
	player.upper.show()
	player.attack_time = player.ATTACK_DURATION
	player.set_resurrection_progress(-1.0)
	check(player.resurrection_active and player.resurrection_progress == 0.0 and not player.controls_enabled, "progress clamps to zero and locks controls")
	check(player.sprite.animation == &"dead" and player.sprite.frame == dead_count - 1 and not player.sprite.is_playing(), "fallback starts on the lying dead frame and stays manual")
	check(not player.upper.visible and player.sprite.flip_h and player.sprite.scale == Vector2(1.25, 0.9), "resurrection hides upper layer and preserves authored transform")
	check(not player.dead and player.motion_state != SlicePlayer.MotionState.DEAD and player.attack_time == 0.0, "presentation cancels attack without entering gameplay death")
	player.take_damage(99.0)
	player.take_damage(99.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)
	player.die()
	check(player.health_units == hp and player.max_health_units == max_hp and not player.dead and events[0] == 0 and events[1] == 0, "damage, void and direct die preserve health and emit no death")
	var at := player.position
	Input.action_press("attack")
	Input.action_press("move_right")
	Input.action_press("jump")
	await frames(3)
	player._fire_arrow()
	check(player.position == at and player.attack_time == 0.0 and events[2] == 0, "physics/input and direct projectile hook cannot move or attack")
	check(player.sprite.animation == &"dead" and player.sprite.frame == dead_count - 1, "physics leaves manual resurrection frame unchanged")
	Input.action_release("attack")
	Input.action_release("move_right")
	Input.action_release("jump")
	paused = true
	player.set_resurrection_progress(0.5)
	var midpoint := dead_count - 1 - mini(dead_count - 1, int(0.5 * dead_count))
	check(player.sprite.frame == midpoint, "paused manual setter advances fallback frame")
	await frames(3)
	check(player.sprite.frame == midpoint, "paused frame remains stable")
	player.set_resurrection_progress(2.0)
	check(player.resurrection_progress == 1.0 and player.sprite.frame == 0, "fallback ends at standing frame and clamps to one")
	player.finish_resurrection()
	check(not player.resurrection_active and player.sprite.animation == &"idle" and player.sprite.is_playing() and not player.controls_enabled, "finish returns to idle and leaves control restoration to level")
	check(player.sprite.sprite_frames == authored and authored.get_animation_loop(&"dead") == dead_loop and authored.get_animation_speed(&"dead") == dead_speed and authored.get_frame_texture(&"dead", dead_count - 1) == dead_texture, "fallback preserves authored animation resource")
	# Simulate Claude's future dedicated strip without mutating the shared resource.
	var dedicated := authored.duplicate() as SpriteFrames
	dedicated.add_animation(&"resurrect")
	dedicated.set_animation_loop(&"resurrect", false)
	for i in range(4):
		dedicated.add_frame(&"resurrect", authored.get_frame_texture(&"dead", mini(i, dead_count - 1)))
	player.sprite.sprite_frames = dedicated
	player.set_resurrection_progress(0.0)
	check(player.sprite.animation == &"resurrect" and player.sprite.frame == 0, "dedicated strip starts at first frame")
	player.set_resurrection_progress(0.5)
	check(player.sprite.frame == 2 and not player.sprite.is_playing(), "dedicated strip samples forward manually while paused")
	player.set_resurrection_progress(1.0)
	check(player.sprite.frame == 3 and not dedicated.get_animation_loop(&"resurrect"), "dedicated strip reaches final nonloop frame")
	player.finish_resurrection()
	check(player.sprite.animation == &"idle" and not player.resurrection_active and events == [0, 0, 0], "dedicated finish returns idle without gameplay signals")
	paused = false
	room.queue_free()
	await frames(2)
	print("RESULT ", checks, " resurrection player checks; ", failures, " failures")
	quit(1 if failures else 0)

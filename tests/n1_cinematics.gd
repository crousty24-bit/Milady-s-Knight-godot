extends SceneTree
# Real inputs exercise the story route. Explicit positions only probe trigger boundaries.
const N1 := "res://scenes/eidolon_vale.tscn"
var checks := 0
var failures := 0
var level: Node2D
var progress: Node

func _initialize() -> void: call_deferred("run")
func frames(count: int = 3) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func tap(action: String) -> void:
	await process_frame
	Input.action_press(action)
	await frames(3)
	Input.action_release(action)
	await frames(4)
func capture(label: String) -> void:
	if DisplayServer.get_name() == "headless": return
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://work/run017-revision")
	root.get_texture().get_image().save_png("res://work/run017-revision/" + label + ".png")
func load_level() -> void:
	if is_instance_valid(current_scene):
		current_scene.queue_free()
		paused = false
		await frames()
	level = load(N1).instantiate()
	root.add_child(level)
	current_scene = level
	await frames()
func wait_free() -> void:
	for i in range(240):
		if level.modal.is_empty() and not level.resume_pending: return
		await frames(1)
func run() -> void:
	progress = root.get_node("Progression")
	progress.new_game()
	await load_level()
	var art = level.get_node("AncientSpirit/Art")
	var spawn: Vector2 = level.player.position
	check(level.modal == "resurrection" and paused and level.player.resurrection_active, "New Game begins exclusive resurrection")
	check(level.player.sprite.animation in [&"dead", &"resurrect"] and level.player.resurrection_progress == 0.0 and not level.player.dead, "first pose is a corpse presentation without gameplay death")
	check(progress.permanent_flags.has(level.RESURRECTION_ID), "first appearance is claimed before animation playback")
	check(level.spirit_phase == "hidden" and not art.visible and not level.dialogue_panel.active, "Spirit and dialogue are hidden throughout initial resurrection")
	await capture("knight-dead")
	Input.action_press("jump")
	await frames(65)
	check(level.player.resurrection_progress > 0.0 and level.player.resurrection_progress < 1.0, "resurrection progresses while gameplay tree is paused")
	await capture("knight-resurrection")
	await frames(75)
	check(level.modal.is_empty() and level.resume_pending and not level.player.controls_enabled, "held Space cannot jump when resurrection ends")
	Input.action_release("jump")
	await frames(5)
	check(level.player.controls_enabled and level.player.sprite.animation == &"idle" and level.player.position.x == spawn.x and level.player.is_on_floor(), "release returns to grounded idle at spawn with full controls")
	await capture("knight-idle-spirit-hidden")
	# Boundary fixture: net forward distance, rather than total distance walked.
	level.player.position.x = level.intro_spawn_x - 32.0
	await frames()
	check(level.spirit_phase == "hidden" and not level.dialogue_panel.active, "two blocks backward do not trigger Spirit")
	level.player.position.x = level.intro_spawn_x + 31.0
	await frames()
	check(level.spirit_phase == "hidden" and level.modal.is_empty(), "31 pixels forward leave Spirit hidden and gameplay free")
	level.player.position = spawn
	await frames()
	# Assign an existing cue as an audio-hook fixture; the final apparition cue belongs to Claude.
	art.appearance_sound = load("res://assets/sounds/sfx_dialogue_open.wav")
	Input.action_press("move_right")
	for i in range(90):
		await frames(1)
		if level.modal == "spirit_appearance": break
	Input.action_release("move_right")
	check(level.player.position.x >= spawn.x + 32.0 and level.player.position.x < spawn.x + 36.0, "real walking triggers apparition at two forward blocks")
	check(level.spirit_phase == "appearing" and paused and not level.player.controls_enabled and not level.dialogue_panel.active, "apparition owns pause before opening dialogue")
	check(art.appearance_audio.playing and art.appearance_audio.bus == &"SFX", "appearance hook plays its assigned cue on SFX during cinematic pause")
	var apparition_position: Vector2 = level.player.position
	Input.action_press("attack")
	Input.action_press("move_right")
	await frames(18)
	check(level.player.position == apparition_position and level.player.attack_time == 0.0 and art.visible and art.modulate.a > 0.0 and art.modulate.a < 1.0, "fallback fade is visible while movement and attacks remain frozen")
	await capture("spirit-appearing")
	Input.action_release("attack")
	Input.action_release("move_right")
	await tap("pause")
	check(not level.pause_menu.opened and not level.request_context("Overlap", "", ["Continue"]), "appearance rejects overlapping pause and contexts")
	for i in range(90):
		if level.modal == "dialogue": break
		await frames(1)
	check(level.modal == "dialogue" and level.spirit_phase == "present" and paused and not level.player.controls_enabled, "apparition hands pause directly to the dialogue")
	await capture("spirit-dialogue")
	for i in range(level.dialogue_panel.lines.size()): await tap("jump")
	await frames(8)
	check(progress.completed_dialogues.has(level.INTRO_ID) and level.spirit_phase == "present", "Spirit stays present after the final phrase is saved")
	if level.modal == "context": await tap("interact")
	# Walk away to the actual six-block default radius, without teleporting the route.
	Input.action_press("move_right")
	for i in range(120):
		await frames(1)
		if level.spirit_phase == "disappearing": break
	Input.action_release("move_right")
	check(level.spirit_phase == "disappearing" and level.player.controls_enabled and not paused, "walking away starts disappearance with gameplay still active")
	await frames(15)
	check(art.visible and level.spirit_phase_progress > 0.0 and level.spirit_phase_progress < 1.0 and art.modulate.a < 1.0, "disappearance exposes normalized progress and fades existing art")
	await capture("spirit-disappearing")
	await tap("pause")
	var frozen: float = level.spirit_phase_progress
	await frames(60)
	check(level.modal == "pause" and level.spirit_phase_progress == frozen, "menu pause freezes scripted disappearance")
	await tap("interact")
	await frames(60)
	check(level.spirit_phase == "gone" and not art.visible and not art.appearance_audio.playing, "disappearance finishes hidden with appearance audio stopped")
	await capture("spirit-gone")
	level.player.position = spawn
	await frames(8)
	check(level.spirit_phase == "gone", "returning toward Spirit cannot respawn it")
	await load_level()
	check(level.modal.is_empty() and not level.player.resurrection_active and level.spirit_phase == "gone", "completed-intro restart repeats neither resurrection nor Spirit")
	# Restart and death BEFORE the introduction is saved still never resurrect again.
	progress.new_game()
	await load_level()
	await wait_free()
	level._restart_attempt()
	await frames(10)
	level = current_scene
	check(not level.player.resurrection_active and level.modal.is_empty() and level.spirit_phase == "hidden", "restart before dialogue does not replay resurrection")
	level.player.die()
	await frames(220)
	level = current_scene
	check(not level.player.resurrection_active and not level.player.dead and level.modal.is_empty() and level.spirit_phase == "hidden", "death before dialogue respawns safely without resurrection")
	# Existing/migrated saves without New Game intent must not gain the new cinematic.
	progress.new_game()
	progress.permanent_flags.clear()
	await load_level()
	check(level.modal.is_empty() and not level.player.resurrection_active, "existing save without new-game intent starts normally")
	# Transaction failure before first playback is recoverable and must not consume its flag.
	progress.new_game()
	var path: String = progress.storage_path
	progress.persistence_enabled = true
	progress.storage_path = "res://work/nonexistent-cinematics-%d/save.json" % OS.get_process_id()
	await load_level()
	check(level.modal == "resurrection_save" and paused and not progress.permanent_flags.has(level.RESURRECTION_ID), "failed first-spawn save blocks playback without committing its flag")
	await tap("pause")
	check(level.modal == "resurrection_save" and level.player.resurrection_progress == 0.0, "Escape cannot dismiss the first-spawn save error")
	progress.persistence_enabled = false
	progress.storage_path = path
	await tap("interact")
	check(level.modal == "resurrection" and progress.permanent_flags.has(level.RESURRECTION_ID), "E retries first-spawn save and begins resurrection on success")
	await wait_free()
	check(level.player.controls_enabled and not level.player.resurrection_active, "retry finishes in playable idle")
	current_scene.queue_free()
	paused = false
	var ui_audio := root.get_node_or_null("UiSfx") as AudioStreamPlayer
	if ui_audio != null: ui_audio.stop()
	await frames()
	OS.delay_msec(300)
	print("RESULT ", checks, " N1 cinematic checks; ", failures, " failures")
	quit(1 if failures else 0)

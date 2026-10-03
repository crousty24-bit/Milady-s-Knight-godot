extends Node2D
@export var n1_intro_enabled: bool = false
@export var chest_position := Vector2(120, 144)
@export var potion_position := Vector2(176, 134)
const DIALOGUE = preload("res://scripts/dialogue_panel.gd")
const N1_DIALOGUE = preload("res://scripts/n1_dialogue.gd")
const INTRO_ID = "eidolon_vale_spirit"
const RESURRECTION_ID = "n1_resurrection_started"
signal spirit_phase_changed(phase: String)
@export var n1_resurrection_duration: float = 2.0
@export var n1_dead_hold_duration: float = 0.5
@export var spirit_appearance_duration: float = 0.8
@export var spirit_disappearance_duration: float = 0.8
@export var spirit_departure_distance: float = 96.0
const SPIRIT_TRIGGER_DISTANCE: float = 32.0 # Two authored 16px terrain blocks forward.
var intro_spawn_x: float = 0.0
var spirit_phase: String = "hidden"
var spirit_phase_progress: float = 0.0
var n1_sequence_elapsed: float = 0.0
var dialogue_panel: CanvasLayer
var tutorial_id: String = ""
var dismissed_tutorials: Dictionary = {}
const TUTORIALS = [
	["n1_movement", 0.0, "The Eidolon Vale", "Arrows: move   Space: jump / double jump\nCollect coins for the exit. Slime kills give shards."],
	["n1_combat", 280.0, "Weapons and health", "F (hold): attack / shoot   A: switch equipment\nSlimes hurt on contact. Watch your hearts."],
	["n1_traversal", 450.0, "Two paths", "Explore above or below. Jump away from rough walls.\nAvoid spikes and falls. Escape: pause / restart."],
	["n1_exit", 1940.0, "Healing and the exit", "The potion restores 0.5 HP and stays if health is full.\nPay 12 coins with E at the gate. Shards save at the exit."],
]
@export var void_y: float = 304.0
@export_file("*.tscn") var next_level_scene: String = ""
const COIN_SCENE = preload("res://scenes/coin.tscn")
var gold: int = 0
var bonus: int = 0
var reward_settled: bool = false
var transitioning: bool = false
var finished: bool = false
var paused: bool = false
var closing: bool = false
const MENU = preload("res://scripts/keyboard_menu.gd")
var modal: String = ""
var pause_menu: CanvasLayer
var resume_pending: bool = false
var context_result: Callable
const CHEST = preload("res://scenes/tutorial_chest.tscn")
const POTION = preload("res://scenes/minor_potion.tscn")
var tutorial_chest: Area2D
var minor_potion: Area2D
const GATE_PROMPT_OFFSET := Vector2(0, -132)
const DEATH_MESSAGE_DURATION: float = 3.0
const DEATH_FADE_DURATION: float = 0.4
var death_elapsed: float = -1.0
var death_reloading: bool = false
@onready var player: SlicePlayer = $Player
@onready var camera: Camera2D = $Player/Camera2D
@onready var hud = $HUD
@onready var gate = $GoldGate
@onready var progression = get_node("/root/Progression")
func _ready() -> void:
	get_tree().paused = false
	get_tree().auto_accept_quit = false
	pause_menu = MENU.new()
	add_child(pause_menu)
	pause_menu.selected.connect(_pause_choice)
	pause_menu.cancelled.connect(_close_pause)
	# The authored slice owns its camera bounds and framing.
	camera.position = Vector2(32, -38)
	camera.limit_left = 0
	camera.limit_top = -224
	camera.limit_right = 2240
	camera.limit_bottom = 304
	camera.process_callback = Camera2D.CAMERA2D_PROCESS_PHYSICS
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 7.0
	for coin in $Coins.get_children(): coin.collected.connect(_on_collected)
	for enemy in $Enemies.get_children():
		register_enemy(enemy)
	player.configure_equipment(progression.equipment.ranged == "Longbow0")
	player.equipment_changed.connect(_update_equipment_hud)
	tutorial_chest = CHEST.instantiate()
	tutorial_chest.position = chest_position
	add_child(tutorial_chest)
	if player.has_longbow: tutorial_chest.consume()
	minor_potion = POTION.instantiate()
	minor_potion.position = potion_position
	add_child(minor_potion)
	player.health_changed.connect(hud.set_health)
	player.died.connect(_on_died)
	gate.offering_requested.connect(try_offering)
	$ExitArea.body_entered.connect(_on_exit)
	_update_gold_hud()
	hud.set_health(player.health, player.max_health)
	_update_equipment_hud(player.active_slot)
	$Music.play()
	if n1_intro_enabled:
		dialogue_panel = DIALOGUE.new()
		add_child(dialogue_panel)
		dialogue_panel.completed.connect(_complete_intro)
		dialogue_panel.retry_requested.connect(_complete_intro)
		intro_spawn_x = player.position.x
		call_deferred("_prepare_n1_intro")
func _physics_process(_delta: float) -> void:
	if not paused and not finished and player.position.y > void_y:
		player.take_damage(0.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)

func _process(delta: float) -> void:
	if closing: return
	if n1_intro_enabled and modal in ["resurrection", "resurrection_save", "spirit_appearance"]:
		_process_n1_cinematic(delta)
		return
	if resume_pending:
		if not Input.is_action_pressed("interact") and not Input.is_action_pressed("attack") and not Input.is_action_pressed("jump") and not Input.is_action_pressed("pause"):
			resume_pending = false
			player.controls_enabled = true
		return
	if death_elapsed >= 0.0:
		death_elapsed += delta
		if death_elapsed >= DEATH_MESSAGE_DURATION:
			hud.set_death_fade(minf(1.0, (death_elapsed - DEATH_MESSAGE_DURATION) / DEATH_FADE_DURATION))
		if death_elapsed >= DEATH_MESSAGE_DURATION + DEATH_FADE_DURATION and not death_reloading:
			death_reloading = true
			_restart_attempt()
		return
	if finished and Input.is_action_just_pressed("interact"):
		if not reward_settled: _settle_reward()
		elif not next_level_scene.is_empty() and not transitioning:
			transitioning = true
			call_deferred("_next_level")
		elif not transitioning:
			_restart_attempt()
		return
	if Input.is_action_just_pressed("pause") and not finished and not player.dead and modal.is_empty():
		_open_pause()
		return
	if n1_intro_enabled and not finished and not player.dead and not paused and modal.is_empty():
		_process_spirit_story(delta)
		if not modal.is_empty() or _show_n1_tutorial(): return
	if finished or player.dead or paused:
		hud.hide_prompt()
		return
	if tutorial_chest.player_near() and not tutorial_chest.consumed:
		hud.show_item_prompt(tutorial_chest.global_position + Vector2(0, -44), "E: retry save" if tutorial_chest.save_failed else "E: free Longbow 0")
		if Input.is_action_just_pressed("interact"):
			if request_context("Free tutorial chest", "Longbow 0: 1 DMG / 1.5 s / 20 blocks\nA: select weapon   F (hold): attack / shoot", ["Accept Longbow 0", "Refuse"], _choose_tutorial_reward):
				tutorial_chest.consume()
		return
	if gate.player_near() and not gate.opened:
		hud.show_prompt(gate.global_position + GATE_PROMPT_OFFSET, gate.COST, gold)
	else:
		hud.hide_prompt()
func _on_collected(value: int) -> void:
	if finished or player.dead or value <= 0: return
	gold += value
	_update_gold_hud()

func _on_enemy_defeated(value: int, at: Vector2) -> void:
	if finished or player.dead or value <= 0: return
	bonus += value
	_update_gold_hud()
	var feedback = COIN_SCENE.instantiate()
	feedback.bonus_feedback = value
	feedback.position = to_local(at) + Vector2(0, -12)
	feedback.process_mode = Node.PROCESS_MODE_PAUSABLE
	add_child(feedback)

func register_enemy(enemy: Node) -> void:
	if enemy.has_signal("defeated") and not enemy.is_connected("defeated", _on_enemy_defeated):
		enemy.connect("defeated", _on_enemy_defeated)

func _update_gold_hud() -> void:
	hud.set_gold(gold, gate.opened)
	hud.set_bonus(progression.banked_bonus, 0 if reward_settled else bonus)
func try_offering() -> bool:
	if finished or player.dead or gate.opened or not modal.is_empty() or resume_pending: return false
	if gold < gate.COST:
		hud.flash_prompt_failure()
		return false
	gold -= gate.COST
	gate.open()
	_update_gold_hud()
	hud.flash_prompt_success()
	return true
func _on_exit(body: Node2D) -> void:
	if body != player or player.dead or not gate.opened or finished or not modal.is_empty() or resume_pending: return
	finished = true
	modal = "victory"
	paused = true
	get_tree().paused = true
	player.controls_enabled = false
	_settle_reward()

func _settle_reward() -> void:
	if reward_settled: return
	var destination: String = scene_file_path if next_level_scene.is_empty() else next_level_scene
	var error: Error = progression.settle_level(bonus, destination)
	if error != OK:
		hud.set_overlay("Level complete", "Shards not saved.\nE: retry saving")
		return
	reward_settled = true
	_update_gold_hud()
	var action: String = "E: next level" if not next_level_scene.is_empty() else "E: replay"
	hud.set_overlay("Level complete", "+%d shards saved  |  Bank %d\n%s" % [bonus, progression.banked_bonus, action])

func _next_level() -> void:
	get_tree().paused = false
	var error: Error = progression.change_level(next_level_scene)
	if error != OK:
		transitioning = false
		get_tree().paused = true
		hud.set_overlay("Next level unavailable", "Your shards are saved.\nE: retry")

func _on_died() -> void:
	if death_elapsed >= 0.0: return
	bonus = 0
	modal = "death"
	resume_pending = false
	pause_menu.close()
	if is_instance_valid(dialogue_panel): dialogue_panel.close()
	if n1_intro_enabled:
		if player.resurrection_active: player.finish_resurrection()
		_set_spirit_phase("gone")
	_update_gold_hud()
	hud.show_death_overlay()
	death_elapsed = 0.0
	paused = true
	get_tree().paused = true

func _restart_attempt() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()

func _exit_tree() -> void:
	$Music.stop()

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST and not closing:
		closing = true
		# Release active reward/equip voices before the engine tears down their streams.
		for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for emitter in get_tree().root.find_children("*", audio_type, true, false):
				emitter.stop()
		await get_tree().create_timer(0.3, true).timeout
		get_tree().quit()

func _open_pause() -> void:
	modal = "pause"
	paused = true
	player.controls_enabled = false
	get_tree().paused = true
	hud.hide_prompt()
	pause_menu.show_menu("Paused", "Arrows: select   E: confirm   Escape: resume", ["Resume", "Restart", "Quit to menu"])

func _close_pause() -> void:
	if modal not in ["pause", "context"]: return
	context_result = Callable()
	if not tutorial_id.is_empty():
		dismissed_tutorials[tutorial_id] = true
		tutorial_id = ""
	pause_menu.close()
	modal = ""
	paused = false
	resume_pending = true
	get_tree().paused = false

func _pause_choice(index: int) -> void:
	if modal == "resurrection_save":
		_begin_resurrection()
		return
	if modal == "context":
		var result := context_result
		_close_pause()
		if result.is_valid(): result.call(index)
		return
	if modal != "pause": return
	match index:
		0: _close_pause()
		1:
			_release_menu_inputs()
			_restart_attempt()
		2:
			_release_menu_inputs()
			get_tree().paused = false
			progression.change_level("res://scenes/game.tscn")

func _release_menu_inputs() -> void:
	for action in ["interact", "attack", "jump", "pause", "move_left", "move_right"]:
		Input.action_release(action)

# Rewards and tutorials share the exclusive modal owner.
func request_context(title: String, detail: String, options: Array, result: Callable = Callable()) -> bool:
	if not modal.is_empty() or resume_pending or player.dead or finished: return false
	modal = "context"
	context_result = result
	paused = true
	player.controls_enabled = false
	get_tree().paused = true
	hud.hide_prompt()
	pause_menu.show_menu(title, detail, options)
	return true

func _choose_tutorial_reward(index: int) -> void:
	if index != 0: return
	var remaining: int = progression.acquire_equipment("ranged", "Longbow0", 0, bonus)
	if remaining < 0:
		tutorial_chest.retry_after_failure()
		return
	bonus = remaining
	player.configure_equipment(true)
	_update_equipment_hud(player.active_slot)
	_update_gold_hud()

func _update_equipment_hud(slot: int) -> void:
	hud.set_equipment(slot, player.has_longbow)

func _start_intro() -> void:
	if progression.completed_dialogues.has(INTRO_ID): return
	if not modal.is_empty() or player.dead or finished: return
	modal = "dialogue"
	paused = true
	player.prepare_dialogue_pose()
	get_tree().paused = true
	hud.hide_prompt()
	dialogue_panel.show_dialogue(N1_DIALOGUE.SPEAKER, N1_DIALOGUE.LINES)

func _complete_intro() -> void:
	if modal != "dialogue": return
	if progression.complete_dialogue(INTRO_ID) != OK:
		dialogue_panel.show_save_error("Dialogue not saved. Your previous progress is protected.")
		return
	dialogue_panel.close()
	player.finish_dialogue_pose()
	_set_spirit_phase("present")
	modal = ""
	paused = false
	resume_pending = true
	get_tree().paused = false

func _show_n1_tutorial() -> bool:
	if not progression.completed_dialogues.has(INTRO_ID): return false
	for item in TUTORIALS:
		var id: String = item[0]
		if player.position.x < item[1] or progression.completed_dialogues.has(id) or dismissed_tutorials.has(id): continue
		if request_context(item[2], item[3], ["Continue"], _complete_tutorial.bind(id)):
			tutorial_id = id
			return true
	return false

func _complete_tutorial(_index: int, id: String) -> void:
	if progression.complete_dialogue(id) == OK: return
	# Failed acknowledgements do not become seen flags. Release inputs, then retry.
	dismissed_tutorials.erase(id)
	call_deferred("_tutorial_save_error", id)

func _tutorial_save_error(id: String) -> void:
	if player.dead or finished or not modal.is_empty(): return
	# This is the continuation of the context, so it can reacquire before resume.
	resume_pending = false
	if request_context("Tutorial not saved", "Your previous progress is protected.\nE: retry saving   Escape: return", ["Retry"], _complete_tutorial.bind(id)):
		tutorial_id = id

# The level owns sequence timing/persistence; the art scripts only render these states.
func _prepare_n1_intro() -> void:
	if progression.completed_dialogues.has(INTRO_ID):
		_set_spirit_phase("gone")
		return
	_set_spirit_phase("hidden")
	if progression.permanent_flags.has("n1_new_game") and not progression.permanent_flags.has(RESURRECTION_ID):
		_begin_resurrection()

func _begin_resurrection() -> void:
	if player.dead or finished or closing: return
	player.controls_enabled = false
	player.set_resurrection_progress(0.0)
	# The tree pauses from the first frame, before the camera ever smooths toward the framing set in
	# _ready: settle it on the grounded knight now, or it jumps when the presentation ends.
	camera.reset_smoothing()
	camera.force_update_scroll()
	paused = true
	get_tree().paused = true
	hud.hide_prompt()
	# Claim this first spawn before playback; death, restart and cold Continue cannot replay it.
	if progression.set_permanent_flag(RESURRECTION_ID) != OK:
		modal = "resurrection_save"
		pause_menu.show_menu("Unable to start the introduction", "Progress not saved. Your previous save is protected.\nE: retry saving", ["Retry"])
		return
	pause_menu.close()
	modal = "resurrection"
	n1_sequence_elapsed = 0.0

func _process_n1_cinematic(delta: float) -> void:
	if modal == "resurrection_save": return
	n1_sequence_elapsed += delta
	if modal == "resurrection":
		var duration := maxf(n1_resurrection_duration, 0.01)
		var hold := clampf(n1_dead_hold_duration, 0.0, duration - 0.001)
		player.set_resurrection_progress(clampf((n1_sequence_elapsed - hold) / (duration - hold), 0.0, 1.0))
		if n1_sequence_elapsed < duration: return
		player.finish_resurrection()
		modal = ""
		paused = false
		resume_pending = true
		get_tree().paused = false
	elif modal == "spirit_appearance":
		spirit_phase_progress = minf(n1_sequence_elapsed / maxf(spirit_appearance_duration, 0.01), 1.0)
		if spirit_phase_progress < 1.0: return
		_set_spirit_phase("present")
		modal = ""
		# The dialogue takes over in this callback, before any gameplay frame can run.
		_start_intro()

func _process_spirit_story(delta: float) -> void:
	if spirit_phase == "hidden" and not progression.completed_dialogues.has(INTRO_ID):
		if player.position.x < intro_spawn_x + SPIRIT_TRIGGER_DISTANCE: return
		player.prepare_dialogue_pose()
		paused = true
		get_tree().paused = true
		modal = "spirit_appearance"
		n1_sequence_elapsed = 0.0
		hud.hide_prompt()
		_set_spirit_phase("appearing")
	elif spirit_phase == "present" and progression.completed_dialogues.has(INTRO_ID):
		var spirit := get_node_or_null("AncientSpirit") as Node2D
		if spirit != null and player.global_position.distance_to(spirit.global_position) >= spirit_departure_distance:
			n1_sequence_elapsed = 0.0
			_set_spirit_phase("disappearing")
	elif spirit_phase == "disappearing":
		n1_sequence_elapsed += delta
		spirit_phase_progress = minf(n1_sequence_elapsed / maxf(spirit_disappearance_duration, 0.01), 1.0)
		if spirit_phase_progress >= 1.0: _set_spirit_phase("gone")

func _set_spirit_phase(phase: String) -> void:
	spirit_phase = phase
	spirit_phase_progress = 1.0 if phase in ["present", "gone"] else 0.0
	spirit_phase_changed.emit(phase)

extends Node2D
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
	player.health_changed.connect(hud.set_health)
	player.died.connect(_on_died)
	gate.offering_requested.connect(try_offering)
	$ExitArea.body_entered.connect(_on_exit)
	_update_gold_hud()
	hud.set_health(player.health, player.max_health)
	$Music.play()
func _physics_process(_delta: float) -> void:
	if not paused and not finished and player.position.y > void_y:
		player.take_damage(0.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)

func _process(delta: float) -> void:
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
	if finished or player.dead or paused:
		hud.hide_prompt()
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
		$Music.stop()
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
	pause_menu.close()
	modal = ""
	paused = false
	resume_pending = true
	get_tree().paused = false

func _pause_choice(index: int) -> void:
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

# Rewards/tutorials share this exclusive modal owner; their gameplay comes in later runs.
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

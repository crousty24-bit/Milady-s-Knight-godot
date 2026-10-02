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
	get_tree().auto_accept_quit = false
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
	if Input.is_action_just_pressed("pause") and not finished and not player.dead:
		paused = not paused
		get_tree().paused = paused
		hud.set_overlay("PAUSE", "ECHAP pour reprendre") if paused else hud.clear_overlay()
	if finished or player.dead or paused:
		hud.hide_prompt()
		return
	if gate.player_near() and not gate.opened:
		hud.show_prompt(gate.global_position + GATE_PROMPT_OFFSET, gate.COST, gold)
	else:
		hud.hide_prompt()
func _on_collected(value: int) -> void:
	if finished or player.dead or value <= 0: return
	var for_seal: int = 0 if gate.opened else mini(value, maxi(0, gate.COST - gold))
	gold += for_seal
	bonus += value - for_seal
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
	if finished or player.dead or gate.opened: return false
	if gold < gate.COST:
		hud.flash_prompt_failure()
		return false
	gold -= gate.COST
	gate.open()
	_update_gold_hud()
	hud.flash_prompt_success()
	return true
func _on_exit(body: Node2D) -> void:
	if body != player or player.dead or not gate.opened or finished: return
	finished = true
	player.controls_enabled = false
	_settle_reward()

func _settle_reward() -> void:
	if reward_settled: return
	var destination: String = scene_file_path if next_level_scene.is_empty() else next_level_scene
	var error: Error = progression.settle_level(bonus, destination)
	if error != OK:
		hud.set_overlay("NIVEAU TERMINE", "Bonus non sauvegardes.\nE  Reessayer la sauvegarde")
		return
	reward_settled = true
	_update_gold_hud()
	var action: String = "E  Niveau suivant" if not next_level_scene.is_empty() else "E  Rejouer"
	hud.set_overlay("LA POTERNE EST FRANCHIE", "Sa trace continue au-dela des murs.\n+%d bonus valides  |  Reserve %d\n%s" % [bonus, progression.banked_bonus, action])

func _next_level() -> void:
	var error: Error = progression.change_level(next_level_scene)
	if error != OK:
		transitioning = false
		hud.set_overlay("NIVEAU SUIVANT INDISPONIBLE", "Vos bonus sont sauvegardes.\nE  Reessayer")

func _on_died() -> void:
	if death_elapsed >= 0.0: return
	bonus = 0
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

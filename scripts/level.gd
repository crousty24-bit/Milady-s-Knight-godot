extends Node2D
@export_file("*.tscn") var next_level_scene: String = ""
const COIN_SCENE = preload("res://scenes/coin.tscn")
var gold: int = 0
var bonus: int = 0
var reward_settled: bool = false
var transitioning: bool = false
var finished: bool = false
var paused: bool = false
var closing: bool = false
var message_time: float = 0.0
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
func _process(delta: float) -> void:
	if finished and Input.is_action_just_pressed("interact"):
		if not reward_settled: _settle_reward()
		elif not next_level_scene.is_empty() and not transitioning:
			transitioning = true
			call_deferred("_next_level")
		elif not transitioning:
			_restart_attempt()
		return
	if player.dead and Input.is_action_just_pressed("interact"):
		_restart_attempt()
		return
	if Input.is_action_just_pressed("pause") and not finished and not player.dead:
		paused = not paused
		get_tree().paused = paused
		hud.set_overlay("PAUSE", "ECHAP pour reprendre") if paused else hud.clear_overlay()
	if finished or player.dead or paused: return
	message_time = maxf(0.0, message_time - delta)
	if message_time > 0.0: return
	if gate.player_near() and not gate.opened:
		hud.set_hint("E  Offrir 12 or" if gold >= 12 else "Poterne scellee : %d / 12 or" % gold)
	elif absf(player.position.x-1544)<55 or (absf(player.position.x-1032)<55 and player.position.y>160):
		hud.set_hint("Ronces lumineuses : danger. Sautez par-dessus.")
	elif player.position.x < 240:
		hud.set_hint("FLECHES marcher   ESPACE sauter   F attaquer")
	elif player.position.x < 510:
		hud.set_hint("Le chariot est vide. Des traces vers l'est.")
	elif player.position.x < 592:
		hud.set_hint("ESPACE puis ESPACE : double saut")
	elif player.position.x < 720 and player.position.y < 120:
		hud.set_hint("Mur : ESPACE rebondir. Pas de double saut.")
	elif player.position.x < 1080 and player.position.y < 120:
		hud.set_hint("Le bac relie les berges. Attendez son retour.")
	elif player.position.x < 1350:
		hud.set_hint("La banniere royale a ete arrachee.")
	elif player.position.x < 1760:
		hud.set_hint("Les racines ont noirci. Quelque chose avance.")
	else:
		hud.set_hint("Un ruban royal... Elle est passee par ici.")
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
		hud.set_hint("Il manque %d or. Les deux chemins restent ouverts." % (gate.COST-gold))
		message_time = 2.5
		return false
	gold -= gate.COST
	gate.open()
	_update_gold_hud()
	hud.set_hint("Le sceau cede. Traversez la poterne.")
	message_time = 3.0
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
	bonus = 0
	_update_gold_hud()
	hud.set_overlay("LE ROYAUME VOUS A PRIS", "E  Recommencer le niveau")

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

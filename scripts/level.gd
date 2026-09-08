extends Node2D
var gold: int = 0
var finished: bool = false
var paused: bool = false
var closing: bool = false
var message_time: float = 0.0
@onready var player: SlicePlayer = $Player
@onready var hud = $HUD
@onready var gate = $GoldGate
func _ready() -> void:
	get_tree().auto_accept_quit = false
	for coin in $Coins.get_children(): coin.collected.connect(_on_collected)
	player.health_changed.connect(hud.set_health)
	player.died.connect(_on_died)
	gate.offering_requested.connect(try_offering)
	$ExitArea.body_entered.connect(_on_exit)
	hud.set_gold(gold, false)
	hud.set_health(player.health)
	$Music.play()
func _process(delta: float) -> void:
	if Input.is_action_just_pressed("restart"):
		get_tree().paused = false
		get_tree().reload_current_scene()
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
		hud.set_hint("FLECHES / Q D   ESPACE sauter   J frapper")
	elif player.position.x < 510:
		hud.set_hint("Le chariot est vide. Des traces vers l'est.")
	elif player.position.x < 770:
		hud.set_hint("Poterne : 12 or. Haut : sauts / Bas : danger")
	elif player.position.x < 1350:
		hud.set_hint("La banniere royale a ete arrachee.")
	elif player.position.x < 1760:
		hud.set_hint("Les racines ont noirci. Quelque chose avance.")
	else:
		hud.set_hint("Un ruban royal... Elle est passee par ici.")
func _on_collected(value: int) -> void:
	if finished or player.dead: return
	gold += value
	hud.set_gold(gold, gate.opened)
func try_offering() -> bool:
	if finished or player.dead or gate.opened: return false
	if gold < 12:
		hud.set_hint("Il manque %d or. Les deux chemins restent ouverts." % (12-gold))
		message_time = 2.5
		return false
	gold -= 12
	gate.open()
	hud.set_gold(gold, true)
	hud.set_hint("Le sceau cede. Traversez la poterne.")
	message_time = 3.0
	return true
func _on_exit(body: Node2D) -> void:
	if body != player or player.dead or not gate.opened or finished: return
	finished = true
	player.controls_enabled = false
	hud.set_overlay("LA POTERNE EST FRANCHIE", "Sa trace continue au-dela des murs.\nR  Rejouer")
func _on_died() -> void:
	hud.set_overlay("LE ROYAUME VOUS A PRIS", "R  Recommencer le niveau")

func _exit_tree() -> void:
	$Music.stop()

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST and not closing:
		closing = true
		$Music.stop()
		await get_tree().create_timer(0.3, true).timeout
		get_tree().quit()

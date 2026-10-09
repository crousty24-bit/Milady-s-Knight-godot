extends Node2D
@onready var controls = get_node("/root/Controls")
@export var n1_intro_enabled: bool = false
@export_range(1, 10) var world_level: int = 1
@export var camera_bounds := Rect2(0, -224, 2240, 528)
@export var auto_camera_vertical_bounds: bool = true
@export_range(0, 2048, 1) var camera_vertical_padding: float = 256.0
var resolved_camera_bounds: Rect2
@export var tutorial_rewards_enabled: bool = true
@export var secret_wall_intro_enabled: bool = true
const SECRET_HINT_ID = "secret_wall_hint"
const SECRET_TUTORIAL_ID = "secret_wall_tutorial"
var _secret_tutorial_pending: Node2D
var chest_economy := ChestEconomy.new()
var active_reward: Area2D
var reward_choices: Array[String] = []
var registered_enemies: Dictionary = {}
var rewarded_enemies: Dictionary = {}
signal kill_healed(amount: float)
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
	["n1_movement", 0.0, "The Eidolon Vale", "{move_left}/{move_right}: move   {jump}: jump / double jump\nCollect coins for the exit. Slime kills give shards."],
	["n1_combat", 280.0, "Weapons and health", "{attack} (hold): attack / shoot   {switch_equipment}: equipment\nSlimes hurt on contact. Watch your hearts."],
	["n1_traversal", 450.0, "Two paths", "Explore above or below. Jump away from rough walls.\nAvoid spikes and falls. {pause}: pause / restart."],
	["n1_exit", 1940.0, "Healing and the exit", "The potion restores 0.5 HP and stays if health is full.\nPay 12 coins with {interact} at the gate. Shards save at the exit."],
]
@export var void_y: float = 304.0
# Local authored rooms below the usual void boundary, in level coordinates.
@export var void_safe_regions: Array[Rect2] = []
@export_file("*.tscn") var next_level_scene: String = ""
const COIN_SCENE = preload("res://scenes/coin.tscn")
const FEEDBACK_TEXT = preload("res://scripts/feedback_text.gd")
# Gains announced above the knight, in the functional colours of docs/05.
const SHARD_TEXT := Color(0.753, 0.541, 0.831)
const HEAL_TEXT := Color(0.596, 0.8, 0.345)
const HP_BONUS_TEXT := Color(0.941, 0.478, 0.353)
const AMMO_TEXT := Color(0.867, 0.886, 0.91)
var feedback_text: Node2D
var _known_max_health: float = 0.0
# Area names announced by the HUD title card on the first load of a level (not on death/restart).
const LEVEL_TITLES = {
	"res://scenes/eidolon_vale.tscn": "The Eidolon Vale",
	"res://scenes/blight_town.tscn": "Blight Town",
	"res://scenes/black_forrest.tscn": "Black Forest",
	"res://scenes/forbidden_graveyard.tscn": "Forbidden Graveyard",
}
var gold: int = 0
var bonus: int = 0
var reward_settled: bool = false
var transitioning: bool = false
var finished: bool = false
var paused: bool = false
var closing: bool = false
const MENU = preload("res://scripts/keyboard_menu.gd")
const CONTROLS_MENU = preload("res://scripts/controls_menu.gd")
var controls_menu: CanvasLayer
const CHEST_REVEAL = preload("res://scripts/chest_reveal.gd")
var chest_reveal: CanvasLayer
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
	controls_menu = CONTROLS_MENU.new()
	add_child(controls_menu)
	controls_menu.closed.connect(_return_from_controls)
	resume_pending = controls.menu_inputs_held()
	if resume_pending: player.controls_enabled = false
	chest_reveal = CHEST_REVEAL.new()
	add_child(chest_reveal)
	chest_reveal.revealed.connect(_on_chest_revealed)
	# Keep authored horizontal framing; include the current vertical content.
	camera.position = Vector2(32, -38)
	resolved_camera_bounds = _resolve_camera_bounds()
	camera.limit_left = floori(resolved_camera_bounds.position.x)
	camera.limit_top = floori(resolved_camera_bounds.position.y)
	camera.limit_right = ceili(resolved_camera_bounds.end.x)
	camera.limit_bottom = ceili(resolved_camera_bounds.end.y)
	camera.process_callback = Camera2D.CAMERA2D_PROCESS_PHYSICS
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 7.0
	for coin in $Coins.get_children(): coin.collected.connect(_on_collected)
	for enemy in $Enemies.get_children():
		register_enemy(enemy)
	player.initialize_ammo(progression.ammo_entry if progression.resume_scene == scene_file_path else SlicePlayer.AMMO_DEFAULTS)
	player.ammo_changed.connect(_update_ammo_hud)
	player.ammo_empty.connect(hud.show_ammo_empty)
	feedback_text = FEEDBACK_TEXT.new()
	feedback_text.name = "FeedbackText"
	add_child(feedback_text)
	feedback_text.target = player
	player.ammo_collected.connect(_announce_ammo)
	player.healed.connect(_announce_heal)
	player.configure_bonus_health(progression.hp_bonus_count())
	player.configure_loadout(progression.equipment)
	player.equipment_changed.connect(_update_equipment_hud)
	if tutorial_rewards_enabled:
		tutorial_chest = CHEST.instantiate()
		tutorial_chest.position = chest_position
		add_child(tutorial_chest)
		if player.has_longbow: tutorial_chest.consume()
		minor_potion = POTION.instantiate()
		minor_potion.position = potion_position
		add_child(minor_potion)
	player.health_changed.connect(hud.set_health)
	player.health_changed.connect(_announce_max_health)
	player.died.connect(_on_died)
	gate.offering_requested.connect(try_offering)
	$ExitArea.body_entered.connect(_on_exit)
	for item in get_tree().get_nodes_in_group("durable_items"):
		if is_ancestor_of(item) and item.has_signal("save_error"):
			item.save_error.connect(_durable_save_error)
	_update_gold_hud()
	hud.set_health(player.health, player.max_health)
	_known_max_health = player.max_health
	_update_equipment_hud(player.active_slot)
	hud.magic_shield_source = func() -> float: return player.magic_shield_time
	_announce_level()
	$Music.play()
	var ambience := get_node_or_null("Ambient") as AudioStreamPlayer
	if ambience != null: ambience.play()
	if n1_intro_enabled:
		dialogue_panel = DIALOGUE.new()
		add_child(dialogue_panel)
		dialogue_panel.completed.connect(_complete_intro)
		dialogue_panel.retry_requested.connect(_complete_intro)
		intro_spawn_x = player.position.x
		call_deferred("_prepare_n1_intro")
	for wall in get_tree().get_nodes_in_group("secret_walls"):
		if is_ancestor_of(wall) and wall.intro_enabled:
			wall.passage_revealed.connect(_on_secret_passage_revealed.bind(wall))
func _physics_process(_delta: float) -> void:
	if not paused and not finished and player.position.y > void_y and not _inside_void_safe_region(player.position):
		player.take_damage(0.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)

func _inside_void_safe_region(point: Vector2) -> bool:
	for region in void_safe_regions:
		if region.has_point(point): return true
	return false

func _process(delta: float) -> void:
	if closing: return
	if n1_intro_enabled and modal in ["resurrection", "resurrection_save", "spirit_appearance"]:
		_process_n1_cinematic(delta)
		return
	if resume_pending:
		if not controls.menu_inputs_held():
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
			progression.announced_level = ""  # replaying a finished level is a new launch
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
	if modal.is_empty() and _show_secret_wall_tutorial(): return
	for chest in get_tree().get_nodes_in_group("reward_chests"):
		if not is_ancestor_of(chest) or chest.consumed or not chest.player_near(): continue
		var price: int = chest_economy.price(chest.kind, world_level)
		var text: String = controls.label("interact") + ": retry save" if chest.save_failed else "%s: Open, %d shards" % [controls.label("interact"), price]
		if price < 0: text = "Chest unavailable"
		hud.show_item_prompt(chest.global_position + Vector2(0, -44), text)
		if Input.is_action_just_pressed("interact"):
			if not open_reward_chest(chest): hud.flash_prompt_failure()
		return
	if is_instance_valid(tutorial_chest) and tutorial_chest.player_near() and not tutorial_chest.consumed:
		hud.show_item_prompt(tutorial_chest.global_position + Vector2(0, -44), controls.label("interact") + ": retry save" if tutorial_chest.save_failed else controls.label("interact") + ": free Longbow 0")
		if Input.is_action_just_pressed("interact"):
			if request_context("Free tutorial chest", _control_text("Longbow 0: 1 DMG / 2.2 s / 11 blocks\n{switch_equipment}: equipment   {attack} (hold): attack / shoot"), ["Accept Longbow 0", "Refuse"], _choose_tutorial_reward):
				tutorial_chest.consume()
		return
	for button in get_tree().get_nodes_in_group("mechanism_buttons"):
		if not is_ancestor_of(button) or not button.can_use(player): continue
		hud.show_item_prompt(button.global_position + Vector2(0, -32), controls.label("interact") + ": Activate")
		if Input.is_action_just_pressed("interact"): try_mechanism(button)
		return
	for door in get_tree().get_nodes_in_group("secondary_doors"):
		if not is_ancestor_of(door) or not door.can_use(player): continue
		hud.show_item_prompt(door.global_position + Vector2(0, -48), "%s: Open, %d coins" % [controls.label("interact"), door.coin_cost])
		if Input.is_action_just_pressed("interact") and not try_secondary_door(door): hud.flash_prompt_failure()
		return
	if gate.player_near() and not gate.opened:
		hud.show_prompt(gate.global_position + GATE_PROMPT_OFFSET, gate.COST, gold)
	else:
		hud.hide_prompt()
func _durable_save_error(_error: int) -> void:
	hud.show_save_error()

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
	feedback_text.push("+%d SHARDS" % value, SHARD_TEXT)

func register_enemy(enemy: Node) -> void:
	var id := enemy.get_instance_id()
	if not enemy.has_signal("defeated") or registered_enemies.has(id): return
	registered_enemies[id] = true
	enemy.connect("defeated", _enemy_reward.bind(enemy))

func _enemy_reward(value: int, at: Vector2, enemy: Node) -> void:
	var id := enemy.get_instance_id()
	if rewarded_enemies.has(id) or player.dead or finished: return
	rewarded_enemies[id] = true
	_on_enemy_defeated(value, at)
	var profile: String = enemy.get_meta("healing_profile", "ordinary")
	var amount: float = ChestEconomy.heal_drop(world_level, profile == "elite", profile == "skull", chest_economy.rng)
	var healed := player.heal(amount)
	if healed > 0.0: kill_healed.emit(healed)

func _update_gold_hud() -> void:
	hud.set_gold(gold, gate.opened, gate.COST)
	hud.set_bonus(progression.banked_bonus, 0 if reward_settled else bonus)
func try_secondary_door(door: Node) -> bool:
	if finished or player.dead or paused or not modal.is_empty() or resume_pending: return false
	if not is_instance_valid(door) or not is_ancestor_of(door) or not door.coin_locked or not door.can_use(player): return false
	if door.coin_cost < 0 or gold < door.coin_cost: return false
	gold -= door.coin_cost
	door.open()
	_update_gold_hud()
	hud.flash_prompt_success()
	return true

func try_mechanism(button: Node) -> bool:
	if finished or player.dead or paused or not modal.is_empty() or resume_pending: return false
	if not is_instance_valid(button) or not is_ancestor_of(button) or not button.can_use(player): return false
	button.activate()
	return true

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
	var error: Error = progression.settle_level(bonus, destination, player.ammo if destination != scene_file_path else {})
	if error != OK:
		hud.set_overlay("Level complete", _control_text("Shards not saved.\n{interact}: retry saving"))
		return
	reward_settled = true
	_update_gold_hud()
	var action: String = controls.label("interact") + (": next level" if not next_level_scene.is_empty() else ": replay")
	hud.set_overlay("Level complete", "+%d shards saved  |  Bank %d\n%s" % [bonus, progression.banked_bonus, action])

func _next_level() -> void:
	get_tree().paused = false
	var error: Error = progression.change_level(next_level_scene)
	if error != OK:
		transitioning = false
		get_tree().paused = true
		hud.set_overlay("Next level unavailable", _control_text("Your shards are saved.\n{interact}: retry"))

func _announce_ammo(family: String, amount: int) -> void:
	if amount > 0 and not player.dead: feedback_text.push("+%d %s" % [amount, "KNIVES" if family == "ThrowingKnives" else "ARROWS"], AMMO_TEXT)

func _announce_heal(amount: float) -> void:
	if amount > 0.0 and not player.dead: feedback_text.push("+%s HP" % HealthUnits.format_hp(HealthUnits.from_hp(amount)), HEAL_TEXT)

# An HP bonus raises the maximum (and the bar pops a new heart); never on level entry.
func _announce_max_health(_value: float, maximum: float) -> void:
	if maximum > _known_max_health and not player.dead:
		feedback_text.push("+%s MAX HP" % HealthUnits.format_hp(HealthUnits.from_hp(maximum - _known_max_health)), HP_BONUS_TEXT)
	_known_max_health = maximum

func _announce_level() -> void:
	var title: String = LEVEL_TITLES.get(scene_file_path, "")
	if title.is_empty() or progression.announced_level == scene_file_path: return
	progression.announced_level = scene_file_path
	hud.show_level_title(title)

func _on_died() -> void:
	if death_elapsed >= 0.0: return
	bonus = 0
	modal = "death"
	resume_pending = false
	pause_menu.close()
	controls_menu.close()
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
	var ambience := get_node_or_null("Ambient") as AudioStreamPlayer
	if ambience != null: ambience.stop()

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
	pause_menu.show_menu("Paused", controls.menu_hint(), ["Resume", "Restart", "Quit to menu", "Controls"])

func _close_pause() -> void:
	if modal not in ["pause", "context", "reward"]: return
	if modal == "reward":
		active_reward = null
		reward_choices.clear()
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
	if modal == "reward":
		_choose_paid_reward(index)
		return
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
			progression.announced_level = ""
			progression.change_level("res://scenes/game.tscn")
		3:
			modal = "controls"
			pause_menu.close()
			controls_menu.open()

func _return_from_controls() -> void:
	if modal == "controls": _open_pause()

func _release_menu_inputs() -> void:
	for action in controls.ACTIONS:
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
	player.configure_loadout(progression.equipment)
	_update_equipment_hud(player.active_slot)
	_update_gold_hud()

func _update_equipment_hud(slot: int) -> void:
	hud.set_loadout(slot, player.equipment)
	var family: String = str(player.equipment.ranged).left(-1)
	if player.AMMO_CAPS.has(family):
		hud.set_ammo(family, player.ammo[family], player.AMMO_CAPS[family])
	else:
		hud.set_ammo("", 0, 0)

func _update_ammo_hud(family: String, current: int, maximum: int) -> void:
	if str(player.equipment.ranged).left(-1) == family:
		hud.set_ammo(family, current, maximum)

# Payment precedes choice under the RUN-018 contract. Failed writes preserve the offer.
func open_reward_chest(chest: Area2D) -> bool:
	if not modal.is_empty() or resume_pending or player.dead or finished or closing or chest.consumed or not is_ancestor_of(chest) or not chest.player_near(): return false
	var cost: int = chest_economy.price(chest.kind, world_level)
	if cost < 0 or bonus + progression.banked_shards < cost: return false
	if chest.offer.is_empty(): chest.offer = chest_economy.roll(chest.kind, player.active_item())
	if chest.offer.is_empty(): return false
	var remaining: int = progression.spend_shards(cost, bonus)
	if remaining < 0:
		chest.save_failed = true
		return false
	bonus = remaining
	chest.paid = true
	chest.consumed = true
	chest.save_failed = false
	chest.hide()
	chest_economy.paid(chest.kind)
	active_reward = chest
	modal = "reward"
	paused = true
	player.controls_enabled = false
	get_tree().paused = true
	hud.hide_prompt()
	_update_gold_hud()
	# Paid: the "Treasure Found!" window and its opening animation come before the cards.
	chest_reveal.present(chest.kind)
	return true

func _on_chest_revealed() -> void:
	if modal == "reward" and is_instance_valid(active_reward): _show_paid_reward()

func _show_paid_reward(error: bool = false, selected_index: int = 0) -> void:
	reward_choices.assign([active_reward.offer.item])
	var options: Array = [WeaponCatalog.label(active_reward.offer.item)]
	# Both slots always show (RUN-021 human request); without an upgrade the second one is an empty,
	# unselectable slot. No help text: the window carries a single Accept button.
	var unavailable: Array = []
	if not active_reward.offer.upgrade.is_empty():
		reward_choices.append(active_reward.offer.upgrade)
		options.append("Upgrade +1\n" + WeaponCatalog.label(active_reward.offer.upgrade))
	else:
		options.append("")
		unavailable.append(1)
	var detail: String = ""
	if error: detail = _control_text("Unable to save. {interact}: retry   {pause}: refuse\nYour previous equipment is protected.")
	pause_menu.show_menu("Rare chest" if active_reward.kind == "rare" else "Common chest", detail, options, unavailable, true)
	if selected_index > 0:
		pause_menu.selection = selected_index
		pause_menu._redraw_rows()

func _choose_paid_reward(index: int) -> void:
	if not is_instance_valid(active_reward) or index < 0 or index >= reward_choices.size(): return
	var item := reward_choices[index]
	var slot: String = WeaponCatalog.stats(item).slot
	var remaining: int = progression.acquire_equipment(slot, item, 0, bonus)
	if remaining < 0:
		active_reward.save_failed = true
		_show_paid_reward(true, index)
		return
	bonus = remaining
	player.configure_loadout(progression.equipment)
	_update_gold_hud()
	_close_pause()

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
		if request_context(item[2], _control_text(item[3]), ["Continue"], _complete_tutorial.bind(id)):
			tutorial_id = id
			return true
	return false

func _on_secret_passage_revealed(wall: Node2D) -> void:
	_secret_tutorial_pending = wall

func _secret_wall_near(wall: Node2D) -> bool:
	var start := player.global_position + Vector2(0, -9)
	var target := wall.global_position + Vector2(0, -16)
	if start.distance_to(target) > wall.intro_radius: return false
	var query := PhysicsRayQueryParameters2D.create(start, target, 1)
	query.hit_from_inside = true
	var hit := get_world_2d().direct_space_state.intersect_ray(query)
	return hit.is_empty() or hit.get("collider") == wall

func _show_secret_wall_tutorial() -> bool:
	if not secret_wall_intro_enabled or player.dead or finished or paused or resume_pending or not modal.is_empty(): return false
	for wall in get_tree().get_nodes_in_group("secret_walls"):
		if not is_ancestor_of(wall) or not wall.intro_enabled: continue
		var id: String
		var title: String
		var detail: String
		if wall.opened:
			if not wall.passage_open: continue
			if _secret_tutorial_pending != wall and not _secret_wall_near(wall): continue
			id = SECRET_TUTORIAL_ID
			title = "Hidden Secrets"
			detail = "The world is full of secrets. Many lie hidden behind walls. Keep your eyes open."
		else:
			if not _secret_wall_near(wall): continue
			id = SECRET_HINT_ID
			title = "A Strange Wall"
			detail = "There's something strange about this wall..."
		if progression.completed_dialogues.has(id) or dismissed_tutorials.has(id): continue
		if request_context(title, detail, ["Continue"], _complete_tutorial.bind(id)):
			tutorial_id = id
			if id == SECRET_TUTORIAL_ID: _secret_tutorial_pending = null
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
	if request_context("Tutorial not saved", _control_text("Your previous progress is protected.\n{interact}: retry saving   {pause}: return"), ["Retry"], _complete_tutorial.bind(id)):
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
		pause_menu.show_menu("Unable to start the introduction", _control_text("Progress not saved. Your previous save is protected.\n{interact}: retry saving"), ["Retry"])
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

func _resolve_camera_bounds() -> Rect2:
	var bounds := camera_bounds
	if not auto_camera_vertical_bounds: return bounds
	var half_view := camera.get_viewport_rect().size.y * 0.5 / maxf(absf(camera.zoom.y), 0.001)
	var padding := maxf(camera_vertical_padding, half_view + absf(camera.position.y))
	var terrain := get_node_or_null("Terrain") as TileMapLayer
	if terrain != null and terrain.tile_set != null:
		var used := terrain.get_used_rect()
		if used.has_area():
			# Use row origins, excluding the thickness of the last ground row.
			var tile_size := Vector2(terrain.tile_set.tile_size)
			var first := Vector2(used.position) * tile_size
			var last := Vector2(used.end - Vector2i.ONE) * tile_size
			for point in [first, Vector2(last.x, first.y), last, Vector2(first.x, last.y)]:
				bounds = _include_camera_height(bounds, terrain.to_global(point).y, padding)
	var platforms := get_node_or_null("Platforms")
	if platforms != null:
		for platform in platforms.get_children():
			if not platform is AnimatableBody2D: continue
			var travel: Variant = platform.get("travel")
			var origin: Variant = platform.get("origin")
			if travel is Vector2 and origin is Vector2:
				for point in [origin, origin + travel]:
					bounds = _include_camera_height(bounds, platform.get_parent().to_global(point).y, padding)
	return bounds

func _include_camera_height(bounds: Rect2, world_y: float, padding: float) -> Rect2:
	var top := minf(bounds.position.y, world_y - padding)
	var bottom := bounds.end.y
	# Retain the existing lower framing unless new content extends below it.
	if world_y > camera_bounds.end.y: bottom = maxf(bottom, world_y + padding)
	return Rect2(Vector2(bounds.position.x, top), Vector2(bounds.size.x, bottom - top))

func _control_text(text: String) -> String:
	for action in controls.ACTIONS:
		text = text.replace("{" + action + "}", controls.label(action))
	return text

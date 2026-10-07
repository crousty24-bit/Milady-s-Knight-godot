extends CanvasLayer
var ammo_feedback_time: float = 0.0

func set_ammo(family: String, current: int, maximum: int) -> void:
	var counter := get_node_or_null("Equipment/AmmoCount") as Label
	var icon := get_node_or_null("Equipment/AmmoIcon") as TextureRect
	if counter != null:
		counter.visible = not family.is_empty()
		counter.text = "%02d/%d" % [current, maximum]
		counter.modulate = TITLE_RED if current == 0 else (TITLE_GOLD if current == maximum else Color.WHITE)
	if icon != null:
		icon.visible = not family.is_empty()
		var atlas := AtlasTexture.new()
		atlas.atlas = load("res://assets/run021/ammo/ui_ammo_icons.png")
		var index := (1 if family == "ThrowingKnives" else 0) + (2 if current == 0 else 0)
		atlas.region = Rect2(index * 12, 0, 12, 12)
		icon.texture = atlas
	var plate := get_node_or_null("Equipment/AmmoPlate") as CanvasItem
	if plate != null: plate.visible = not family.is_empty()

func show_ammo_empty(family: String) -> void:
	# Held attack at zero must not restart the feedback every physics tick.
	if ammo_feedback_time > 0.0: return
	_show_ammo_feedback("NO KNIVES" if family == "ThrowingKnives" else "NO ARROWS")

func show_ammo_pickup(family: String, amount: int) -> void:
	_show_ammo_feedback("+%d %s" % [amount, "KNIVES" if family == "ThrowingKnives" else "ARROWS"])

func _show_ammo_feedback(message: String) -> void:
	var feedback := get_node_or_null("Equipment/AmmoFeedback") as Label
	if feedback == null: return
	feedback.text = message
	feedback.show()
	ammo_feedback_time = 0.8

var save_error_time: float = 0.0
var save_error_label: Label
func show_save_error() -> void:
	if save_error_label == null:
		save_error_label = $Health.duplicate()
		save_error_label.name = "SaveError"
		save_error_label.position = Vector2(12, 90)
		save_error_label.modulate = Color("ffad94")
		save_error_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(save_error_label)
	save_error_label.text = "Save failed. Try again."
	save_error_label.show()
	save_error_time = 2.0
func set_gold(value: int, paid: bool, cost: int = 12) -> void:
	$Gold.text = "COINS %02d  |  OPEN" % value if paid else "COINS %02d/%d" % [value, cost]
	$Gold.modulate = Color("f4d384") if value >= cost or paid else Color("dac38f")
func set_bonus(banked: int, pending: int) -> void:
	$Bonus.text = "SHARDS " + _compact(banked + pending)
	$BonusPending.text = "+%s current" % _compact(pending) if pending > 0 else "bank " + _compact(banked)
	$Bonus.tooltip_text = "%d shards: %d banked, %d current" % [banked + pending, banked, pending]
	$Bonus.mouse_filter = Control.MOUSE_FILTER_STOP
func _compact(value: int) -> String:
	if value < 100000: return str(value)
	if value < 1000000: return "%.1fk" % (value / 1000.0)
	if value < 1000000000: return "%.1fM" % (value / 1000000.0)
	return "%.1fG" % (value / 1000000000.0)
func set_health(value: float, maximum: float = 3.0) -> void:
	var current_units := HealthUnits.from_hp(value)
	var maximum_units := HealthUnits.from_hp(maximum)
	$Health.text = "HP " + HealthUnits.format_hp(current_units)
	$HealthHearts.set_values(current_units, maximum_units)
	# The exact value sits right after the hearts, whatever their count (one row holds five).
	var hearts_in_row: int = mini(ceili(float(maximum_units) / HealthUnits.PER_HP), $HealthHearts.HEARTS_PER_ROW)
	$Health.position.x = $HealthHearts.position.x + hearts_in_row * $HealthHearts.HEART_SPACING + 6.0
func set_death_fade(alpha: float) -> void:
	$DeathFade.visible = alpha > 0.0
	var fade_color: Color = $DeathFade.color
	fade_color.a = alpha
	$DeathFade.color = fade_color

# --- Overlays (pause, victory, death) share the cluster's panel language. ---
const PANEL_GOLD = preload("res://assets/sprites/ui_panel.png")
const PANEL_RED = preload("res://assets/sprites/ui_panel_red.png")
const TITLE_GOLD := Color("f0d27a")
const TITLE_RED := Color("d8423a")
const RULE_GOLD := Color("8c6b2e")
const RULE_RED := Color("741620")
const OVERLAY_LINE_HEIGHT: float = 11.0
const OVERLAY_DIM: float = 0.88
# Death keeps the knight's collapse visible: lighter veil, panel in the upper third.
const DEATH_DIM: float = 0.55
const DEATH_PANEL_RISE: float = 84.0

func set_overlay(title: String, subtitle: String, danger: bool = false) -> void:
	$Overlay.show()
	$Overlay.color.a = OVERLAY_DIM
	$Overlay/Title.add_theme_color_override("font_color", TITLE_RED if danger else TITLE_GOLD)
	$Overlay/Title.text = title
	$Overlay/Subtitle.text = subtitle
	$Overlay/Panel.texture = PANEL_RED if danger else PANEL_GOLD
	$Overlay/Rule.color = RULE_RED if danger else RULE_GOLD
	# The panel hugs its content and stays centred on the full screen.
	var lines: int = 0 if subtitle.is_empty() else subtitle.count("\n") + 1
	var panel_height: float = 56.0 if lines == 0 else 14.0 + 20.0 + 12.0 + lines * OVERLAY_LINE_HEIGHT + 14.0
	var top: float = -panel_height / 2.0
	$Overlay/Panel.offset_top = top
	$Overlay/Panel.offset_bottom = top + panel_height
	$Overlay/Title.offset_top = top + (panel_height - 20.0) / 2.0 if lines == 0 else top + 14.0
	$Overlay/Title.offset_bottom = $Overlay/Title.offset_top + 20.0
	$Overlay/Rule.visible = lines > 0
	$Overlay/Rule.offset_top = $Overlay/Title.offset_bottom + 3.0
	$Overlay/Rule.offset_bottom = $Overlay/Rule.offset_top + 1.0
	$Overlay/Subtitle.offset_top = $Overlay/Rule.offset_bottom + 6.0
	$Overlay/Subtitle.offset_bottom = $Overlay/Subtitle.offset_top + lines * OVERLAY_LINE_HEIGHT

func clear_overlay() -> void:
	$Overlay.hide()

func show_death_overlay() -> void:
	# Death speaks in the danger red of the Art Bible.
	set_overlay("Thou hast perished.", "", true)
	$Overlay.color.a = DEATH_DIM
	for node in [$Overlay/Panel, $Overlay/Title, $Overlay/Rule, $Overlay/Subtitle]:
		node.offset_top -= DEATH_PANEL_RISE
		node.offset_bottom -= DEATH_PANEL_RISE
	hide_prompt()
	$PauseCap.hide()
	$PauseHint.hide()

# --- Interaction prompt: only while the player can act on something (docs/05). ---
const FEEDBACK_TIME: float = 0.5
const PROMPT_MARGIN: float = 8.0
var _prompt_world := Vector2.ZERO
var _prompt_active: bool = false
var _prompt_leaving: bool = false
var _prompt_shake: float = 0.0
var _prompt_lift: float = 0.0
var _prompt_tween: Tween
var _prompt_key := ""

func show_prompt(world_position: Vector2, cost: int, have: int) -> void:
	if _prompt_leaving: return
	var enough: bool = have >= cost
	var key := "%s|%d|%d" % [enough, cost, have if not enough else 0]
	if key != _prompt_key:
		_prompt_key = key
		_layout_prompt(enough, cost, have)
	_prompt_world = world_position
	_prompt_active = true
	$Prompt.show()
	_place_prompt()

func hide_prompt() -> void:
	if _prompt_leaving: return
	_prompt_active = false
	_prompt_key = ""
	$Prompt.hide()

# Failed offering: red flash and a short shake, ~0.5 s, instead of a text line.
func flash_prompt_failure() -> void:
	if not _prompt_active or _prompt_leaving: return
	_kill_prompt_tween()
	$Prompt/Bg.self_modulate = Color(2.4, 0.45, 0.4)
	$Prompt/Amount.add_theme_color_override("font_color", TITLE_RED)
	_prompt_tween = create_tween().set_parallel(true)
	_prompt_tween.tween_property($Prompt/Bg, "self_modulate", Color.WHITE, FEEDBACK_TIME)
	_prompt_tween.tween_method(func(t: float) -> void: _prompt_shake = sin(t * TAU * 3.0) * 3.0 * (1.0 - t), 0.0, 1.0, FEEDBACK_TIME)
	_prompt_tween.chain().tween_callback(func() -> void:
		_prompt_shake = 0.0
		$Prompt/Amount.remove_theme_color_override("font_color"))

# Accepted offering: golden glow, the prompt rises and fades out.
func flash_prompt_success() -> void:
	if not _prompt_active: return
	_kill_prompt_tween()
	_prompt_leaving = true
	$Prompt/Bg.self_modulate = Color(1.9, 1.7, 1.0)
	_prompt_tween = create_tween().set_parallel(true)
	_prompt_tween.tween_property($Prompt, "modulate:a", 0.0, FEEDBACK_TIME).set_ease(Tween.EASE_IN)
	_prompt_tween.tween_method(func(t: float) -> void: _prompt_lift = -10.0 * t, 0.0, 1.0, FEEDBACK_TIME)
	_prompt_tween.chain().tween_callback(func() -> void:
		_prompt_leaving = false
		_prompt_lift = 0.0
		$Prompt.modulate.a = 1.0
		$Prompt/Bg.self_modulate = Color.WHITE
		hide_prompt())

func prompt_visible() -> bool:
	return $Prompt.visible

func _kill_prompt_tween() -> void:
	if _prompt_tween and _prompt_tween.is_valid(): _prompt_tween.kill()
	_prompt_shake = 0.0
	$Prompt/Bg.self_modulate = Color.WHITE

func _process(_delta: float) -> void:
	if ammo_feedback_time > 0.0:
		ammo_feedback_time = maxf(0.0, ammo_feedback_time - _delta)
		if ammo_feedback_time == 0.0:
			var feedback := get_node_or_null("Equipment/AmmoFeedback") as Label
			if feedback != null: feedback.hide()
	if save_error_time > 0.0:
		save_error_time = maxf(0.0, save_error_time - _delta)
		if save_error_time == 0.0: save_error_label.hide()
	if _prompt_active: _place_prompt()

func _place_prompt() -> void:
	var screen: Vector2 = get_viewport().get_canvas_transform() * _prompt_world
	var size: Vector2 = $Prompt.size
	var limit: Vector2 = get_viewport().get_visible_rect().size
	var x: float = clampf(screen.x - size.x / 2.0, PROMPT_MARGIN, limit.x - PROMPT_MARGIN - size.x)
	var y: float = clampf(screen.y - size.y / 2.0, PROMPT_MARGIN, limit.y - PROMPT_MARGIN - size.y)
	$Prompt.position = Vector2(roundf(x + _prompt_shake), roundf(y + _prompt_lift))

func _text_width(label: Label, text: String) -> float:
	return label.get_theme_font("font").get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x

func _layout_prompt(enough: bool, cost: int, have: int) -> void:
	$Prompt/Coin.show()
	var text: String = str(cost) if enough else "%02d/%d" % [have, cost]
	var amount: Label = $Prompt/Amount
	amount.text = text
	amount.modulate = Color.WHITE if enough else Color(0.65, 0.68, 0.73)
	var atlas: AtlasTexture = $Prompt/Coin.texture.duplicate()
	atlas.region = Rect2(36 if enough else 48, 0, 12, 12)
	$Prompt/Coin.texture = atlas
	$Prompt/Cap.visible = enough
	$Prompt/CapLabel.visible = enough
	var x: float = 5.0
	if enough: x += 14.0 + 4.0
	$Prompt/Coin.position.x = x
	x += 12.0 + 3.0
	amount.position.x = x
	var width: float = ceilf(_text_width(amount, text))
	amount.size.x = width
	x += width + 5.0
	$Prompt.size = Vector2(x, 24.0)
	$Prompt/Bg.size = Vector2(x, 24.0)

# --- Dialogue banner: visual only; the conversation flow belongs to a later run. ---
func show_dialogue(speaker: String, text: String, avatar_texture: Texture2D = null) -> void:
	$DialogueBanner/Speaker.text = speaker
	$DialogueBanner/Text.text = text
	$DialogueBanner/Portrait.texture = avatar_texture
	$DialogueBanner.show()

func hide_dialogue() -> void:
	$DialogueBanner.hide()


# Functional slot labels; Claude supplies the equipment/shard artwork and focus assets.
func set_equipment(active: int, ranged_owned: bool) -> void:
	set_loadout(active, {"melee": "Sword0", "ranged": "Longbow0" if ranged_owned else ""})

func set_loadout(active: int, slots: Dictionary) -> void:
	$Equipment/Melee.text = ("> " if active == 0 else "  ") + WeaponCatalog.label(slots.melee)
	$Equipment/Ranged.text = ("> " if active == 1 else "  ") + ("Empty" if slots.ranged.is_empty() else WeaponCatalog.label(slots.ranged))
	$Equipment.set_items(str(slots.melee), str(slots.ranged))

func show_item_prompt(world_position: Vector2, text: String) -> void:
	_prompt_world = world_position
	_prompt_key = ""
	_prompt_active = true
	_prompt_leaving = false
	$Prompt.show()
	$Prompt/Cap.hide()
	$Prompt/CapLabel.hide()
	$Prompt/Coin.hide()
	$Prompt/Amount.text = text
	$Prompt/Amount.modulate = Color.WHITE
	$Prompt/Amount.position.x = 5
	var width := ceilf(_text_width($Prompt/Amount, text)) + 10.0
	$Prompt.size = Vector2(width, 24)
	$Prompt/Bg.size = Vector2(width, 24)
	_place_prompt()

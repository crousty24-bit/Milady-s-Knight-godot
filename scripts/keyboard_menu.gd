extends CanvasLayer
# Keyboard panel: navigation by Codex, presentation and UI audio by Claude (RUN-015).
signal selected(index: int)
signal cancelled
var choices: Array[String] = []
var unavailable: Array[int] = []
var selection: int = 0
var opened: bool = false
var opened_frame: int = -1
var panel: PanelContainer
var heading: Label
var description: Label
var rows: BoxContainer
var horizontal_choices: bool = false

# Presentation (RUN-015 art pass): title-screen artwork and logo in the front end, a veil over the
# level for pause/context, gold-trim panel shared with the HUD, focus plate + cursors, lock for
# unavailable options and P0 UI sounds. Navigation, signals and the opening-frame guard are unchanged.
const FONT = preload("res://assets/fonts/PixelOperator8.ttf")
const PANEL = preload("res://assets/sprites/ui_panel.png")
const PANEL_RED = preload("res://assets/sprites/ui_panel_red.png")
const FOCUS = preload("res://assets/sprites/ui_menu_focus.png")
const CURSOR = preload("res://assets/sprites/ui_menu_cursor.png")
const LOCK = preload("res://assets/sprites/ui_menu_lock.png")
const LOGO = preload("res://assets/sprites/ui_logo.png")
const LEDGE = preload("res://assets/sprites/ui_menu_ledge.png")
const BRAZIER = preload("res://assets/sprites/prop_brazier.png")
const FLAME = preload("res://assets/sprites/prop_flame.png")
const GLOW = preload("res://assets/sprites/prop_glow.png")
const KNIGHT = preload("res://assets/sprites/ashen_knight_frames.tres")
const BACKDROP = preload("res://scripts/backdrop.gd")
const SFX := {
	"navigate": preload("res://assets/sounds/sfx_ui_navigate.wav"),
	"confirm": preload("res://assets/sounds/sfx_ui_confirm.wav"),
	"cancel": preload("res://assets/sounds/sfx_ui_cancel.wav"),
	"error": preload("res://assets/sounds/sfx_ui_error.wav"),
}
# RUN-018 (Claude): paid chest choices are drawn as two horizontal cards (icon, exact label,
# level badge), with chest-specific refusal audio. The option strings and selection are unchanged.
const CARD = preload("res://assets/run018/ui/ui_reward_card.png")
const CARD_FOCUS = preload("res://assets/run018/ui/ui_reward_card_focus.png")
const LARGE_ICONS = preload("res://assets/run018/ui/ui_weapon_icons_large.png")
const BADGES = preload("res://assets/run018/ui/ui_tier_badges.png")
# RUN-021 (Claude, human request 8 Oct 2026): cards dominated by a 48 px weapon icon, then the name
# and a 12 px level badge; both slots always shown; the selection glows; a single Accept button.
const XL_ICONS = preload("res://assets/run021/ui/ui_weapon_icons_xl.png")
const XL_BADGES = preload("res://assets/run021/ui/ui_tier_badges_large.png")
const KEYCAP = preload("res://assets/sprites/ui_keycap.png")
const XL_EMPTY := 8
const CARD_SIZE := Vector2(124, 96)
const GLOW_PAD := 10.0
const UPGRADE_TEXT = Color(0.596, 0.8, 0.345)
var footer: HBoxContainer
var accept_label: Label
var accept_key: Label
var _glow: TextureRect
const CHEST_KINDS = preload("res://assets/run018/ui/ui_chest_kind.png")
const ICON_ORDER := ["Sword", "Longsword", "BrutalAxe", "DarkScythe", "Warhammer", "Halberds", "Longbow", "ThrowingKnives"]
const REFUSE_SFX = preload("res://assets/sounds/run018/sfx_chest_reward_refuse.wav")
const GAME_TITLE = "Milady's Knight"
const ERROR_TITLES = ["Unable to continue"]
const GOLD_TEXT = Color(0.941, 0.824, 0.478)
const PALE_TEXT = Color(0.867, 0.886, 0.91)
const DIM_TEXT = Color(0.651, 0.682, 0.733)
const OFF_TEXT = Color(0.384, 0.365, 0.404)
const SHADOW = Color(0.09, 0.075, 0.106)
const SCREEN = Vector2(640, 360)
var front_end: bool = false
var stage: Control
var logo: TextureRect
var _drawn_key: String = ""
var _drawn_selection: int = -1
var _last_cue: String = ""
var _handled_frame: int = -1

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 30
	front_end = get_parent() != null and get_parent().scene_file_path == "res://scenes/game.tscn"
	stage = Control.new()
	stage.size = SCREEN
	stage.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(stage)
	if front_end: _build_title_art()
	else:
		var veil := ColorRect.new()
		veil.size = SCREEN
		veil.color = Color(0.055, 0.045, 0.07, 0.62)
		veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
		stage.add_child(veil)
	panel = PanelContainer.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_theme_stylebox_override("panel", _nine(PANEL, 8, Vector4(14, 10, 14, 12)))
	add_child(panel)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 6)
	panel.add_child(column)
	heading = Label.new()
	description = Label.new()
	rows = VBoxContainer.new()
	rows.add_theme_constant_override("separation", 1)
	for label in [heading, description]:
		_style_label(label, 16 if label == heading else 8, GOLD_TEXT if label == heading else DIM_TEXT)
		column.add_child(label)
	column.add_child(rows)
	footer = _build_footer()
	column.add_child(footer)
	panel.visibility_changed.connect(func() -> void: stage.visible = panel.visible)
	selected.connect(func(_index: int) -> void: _play("confirm"))
	cancelled.connect(func() -> void: _cancel_feedback.call_deferred(opened_frame))
	_ensure_player.call_deferred()
	panel.hide()

func _build_footer() -> HBoxContainer:
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 5)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var cap := PanelContainer.new()
	cap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cap.add_theme_stylebox_override("panel", _nine(KEYCAP, 3, Vector4(4, 2, 4, 2)))
	cap.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	accept_key = Label.new()
	_style_label(accept_key, 8, SHADOW)
	accept_key.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	cap.add_child(accept_key)
	row.add_child(cap)
	accept_label = Label.new()
	accept_label.text = "Accept"
	_style_label(accept_label, 16, GOLD_TEXT)
	row.add_child(accept_label)
	row.hide()
	return row

func _build_title_art() -> void:
	# Night sky, clouds, citadel and haze of the slice (scripts/backdrop.gd) at its reference framing.
	var backdrop := Node2D.new()
	backdrop.set_script(BACKDROP)
	backdrop.position = Vector2(0, -BACKDROP.REFERENCE_TOP)
	stage.add_child(backdrop)
	var shade := TextureRect.new()
	var gradient := Gradient.new()
	gradient.offsets = PackedFloat32Array([0.0, 0.38, 0.62, 1.0])
	gradient.colors = PackedColorArray([Color(0.035, 0.03, 0.05, 0.72), Color(0.035, 0.03, 0.05, 0.12), Color(0.035, 0.03, 0.05, 0.12), Color(0.035, 0.03, 0.05, 0.78)])
	var fill := GradientTexture2D.new()
	fill.gradient = gradient
	fill.fill_from = Vector2(0, 0)
	fill.fill_to = Vector2(0, 1)
	fill.width = 4
	fill.height = 90
	shade.texture = fill
	shade.stretch_mode = TextureRect.STRETCH_SCALE
	shade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	shade.size = SCREEN
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stage.add_child(shade)
	# Foreground: the Ashen Knight keeping watch on a broken rampart, a brazier for warm light.
	var ground := Node2D.new()
	ground.position = Vector2(0, SCREEN.y - LEDGE.get_height())
	stage.add_child(ground)
	var glow := Sprite2D.new()
	glow.texture = GLOW
	glow.position = Vector2(134, -2)
	glow.modulate.a = 0.85
	ground.add_child(glow)
	var ledge := Sprite2D.new()
	ledge.texture = LEDGE
	ledge.centered = false
	ground.add_child(ledge)
	var brazier := Sprite2D.new()
	brazier.texture = BRAZIER
	brazier.position = Vector2(134, 7 - BRAZIER.get_height() * 0.5)
	ground.add_child(brazier)
	var flames := SpriteFrames.new()
	flames.set_animation_speed("default", 9.0)
	for i in 3:
		var frame := AtlasTexture.new()
		frame.atlas = FLAME
		frame.region = Rect2(i * 10, 0, 10, 14)
		flames.add_frame("default", frame)
	var flame := AnimatedSprite2D.new()
	flame.sprite_frames = flames
	flame.position = Vector2(134, 7 - BRAZIER.get_height() - 5)
	flame.play()
	ground.add_child(flame)
	var knight := AnimatedSprite2D.new()
	knight.sprite_frames = KNIGHT
	knight.position = Vector2(60, 7 - 29)
	knight.play("idle")
	ground.add_child(knight)
	logo = TextureRect.new()
	logo.texture = LOGO
	logo.position = Vector2(roundf((SCREEN.x - LOGO.get_width()) * 0.5), 6)
	logo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stage.add_child(logo)

func _nine(texture: Texture2D, margin: int, content: Vector4) -> StyleBoxTexture:
	var box := StyleBoxTexture.new()
	box.texture = texture
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		box.set_texture_margin(side, margin)
	box.content_margin_left = content.x
	box.content_margin_top = content.y
	box.content_margin_right = content.z
	box.content_margin_bottom = content.w
	return box

func _style_label(label: Label, size: int, color: Color) -> void:
	label.add_theme_font_override("font", FONT)
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_shadow_color", SHADOW)
	label.add_theme_constant_override("shadow_offset_x", 1)
	label.add_theme_constant_override("shadow_offset_y", 1)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

func show_menu(title: String, detail: String, options: Array, disabled: Array = [], horizontal: bool = false) -> void:
	if horizontal_choices != horizontal:
		var parent := rows.get_parent()
		parent.remove_child(rows)
		rows.queue_free()
		rows = HBoxContainer.new() if horizontal else VBoxContainer.new()
		rows.add_theme_constant_override("separation", 12 if horizontal else 1)
		parent.add_child(rows)
		parent.move_child(footer, -1)  # the Accept button always closes the column
	horizontal_choices = horizontal
	choices.assign(options)
	unavailable.assign(disabled)
	selection = 0
	while selection < choices.size() - 1 and selection in unavailable:
		selection += 1
	heading.text = title
	description.text = detail
	footer.visible = horizontal
	if horizontal:
		var controls := get_node_or_null("/root/Controls")
		accept_key.text = controls.label("interact") if controls != null else "E"
	opened = true
	opened_frame = Engine.get_process_frames()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	panel.show()
	_redraw_rows()

func close() -> void:
	opened = false
	panel.hide()

func _redraw_rows() -> void:
	var key := "%d|%s" % [opened_frame, heading.text]
	var fresh := key != _drawn_key
	if fresh:
		var error := heading.text in ERROR_TITLES
		panel.add_theme_stylebox_override("panel", _nine(PANEL_RED if error else PANEL, 8, Vector4(14, 10, 14, 12)))
		heading.visible = not (front_end and heading.text == GAME_TITLE)
		description.visible = not description.text.is_empty()
		if error: _play("error")
	elif selection != _drawn_selection:
		_play("navigate")
	_drawn_key = key
	_drawn_selection = selection
	for child in rows.get_children():
		rows.remove_child(child)
		child.queue_free()
	if horizontal_choices:
		for i in range(choices.size()): rows.add_child(_reward_card(i))
		_layout.call_deferred()
		return
	for i in range(choices.size()):
		var focused := i == selection and i not in unavailable
		var row := PanelContainer.new()
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.custom_minimum_size = Vector2(216, 0)
		if focused: row.add_theme_stylebox_override("panel", _nine(FOCUS, 4, Vector4(6, 3, 6, 3)))
		else:
			var empty := StyleBoxEmpty.new()
			empty.set_content_margin_all(3)
			empty.content_margin_left = 6
			empty.content_margin_right = 6
			row.add_theme_stylebox_override("panel", empty)
		var line := HBoxContainer.new()
		line.alignment = BoxContainer.ALIGNMENT_CENTER
		line.add_theme_constant_override("separation", 6)
		row.add_child(line)
		var label := Label.new()
		label.text = choices[i]
		_style_label(label, 16, GOLD_TEXT if focused else (OFF_TEXT if i in unavailable else PALE_TEXT))
		var left := _icon(LOCK if i in unavailable else CURSOR, focused or i in unavailable, false)
		var right := _icon(CURSOR, focused, true)
		line.add_child(left)
		line.add_child(label)
		line.add_child(right)
		rows.add_child(row)
	_layout.call_deferred()

# Weapon ID behind an exact choice label ("Brutal Axe 2", "Upgrade +1\nSword 1"), or "".
func _choice_item(text: String) -> String:
	var line := text.split("\n")[-1].strip_edges()
	var space := line.rfind(" ")
	if space < 0: return ""
	for base in WeaponCatalog.BASES:
		if WeaponCatalog.BASES[base][4] == line.left(space): return base + line.substr(space + 1)
	return ""

func _atlas(texture: Texture2D, region: Rect2) -> TextureRect:
	var atlas := AtlasTexture.new()
	atlas.atlas = texture
	atlas.region = region
	var rect := TextureRect.new()
	rect.texture = atlas
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rect.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	return rect

func _reward_card(i: int) -> Control:
	var empty := choices[i].is_empty()
	var focused := i == selection and i not in unavailable
	var item := _choice_item(choices[i])
	var stats := WeaponCatalog.stats(item)
	# Slot: the glow sits behind the card and spills GLOW_PAD around it.
	var slot := Control.new()
	slot.custom_minimum_size = CARD_SIZE
	slot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if focused:
		_glow = TextureRect.new()
		_glow.texture = _glow_texture()
		_glow.position = Vector2(-GLOW_PAD, -GLOW_PAD)
		_glow.size = CARD_SIZE + Vector2(GLOW_PAD, GLOW_PAD) * 2.0
		_glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
		slot.add_child(_glow)
	var card := NinePatchRect.new()
	card.texture = CARD_FOCUS if focused else CARD
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]: card.set_patch_margin(side, 8)
	card.size = CARD_SIZE
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# The other slot steps back so the selection reads at a glance.
	card.modulate = Color.WHITE if focused else Color(0.62, 0.62, 0.68)
	slot.add_child(card)
	var index: int = XL_EMPTY if stats.is_empty() else ICON_ORDER.find(item.left(-1))
	var icon := _atlas(XL_ICONS, Rect2(index * 48, 0, 48, 48))
	icon.position = Vector2(roundf((CARD_SIZE.x - 48.0) * 0.5), 12)
	icon.size = Vector2(48, 48)
	card.add_child(icon)
	var line := HBoxContainer.new()
	line.alignment = BoxContainer.ALIGNMENT_CENTER
	line.add_theme_constant_override("separation", 4)
	line.position = Vector2(0, 68)
	line.size = Vector2(CARD_SIZE.x, 14)
	line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var label := Label.new()
	label.text = "No upgrade" if empty else (str(stats.name) if not stats.is_empty() else choices[i])
	_style_label(label, 8, OFF_TEXT if empty else (GOLD_TEXT if focused else PALE_TEXT))
	label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	line.add_child(label)
	if not stats.is_empty():
		var badge := _atlas(XL_BADGES, Rect2(int(stats.level) * 12, 0, 12, 12))
		badge.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		line.add_child(badge)
	card.add_child(line)
	if choices[i].begins_with("Upgrade"):
		var plus := Label.new()
		plus.text = "+1"
		_style_label(plus, 16, UPGRADE_TEXT)
		plus.position = Vector2(CARD_SIZE.x - 30, 6)
		card.add_child(plus)
	return slot

func _glow_texture() -> GradientTexture2D:
	var glow := GradientTexture2D.new()
	glow.width = int(CARD_SIZE.x + GLOW_PAD * 2.0)
	glow.height = int(CARD_SIZE.y + GLOW_PAD * 2.0)
	glow.fill = GradientTexture2D.FILL_SQUARE
	glow.fill_from = Vector2(0.5, 0.5)
	glow.fill_to = Vector2(0.5, 0.0)
	glow.gradient = Gradient.new()
	glow.gradient.offsets = PackedFloat32Array([0.0, 0.78, 1.0])
	glow.gradient.colors = PackedColorArray([Color(GOLD_TEXT, 0.55), Color(GOLD_TEXT, 0.4), Color(GOLD_TEXT, 0.0)])
	return glow

func _icon(texture: Texture2D, shown: bool, mirrored: bool) -> TextureRect:
	var icon := TextureRect.new()
	icon.texture = texture
	icon.custom_minimum_size = Vector2(7, 9)
	icon.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	icon.flip_h = mirrored
	icon.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	icon.modulate.a = 1.0 if shown else 0.0
	return icon

func _layout() -> void:
	panel.reset_size()
	var top := 132.0 if front_end else 0.0
	var room := SCREEN.y - top - (34.0 if front_end else 0.0)
	panel.position = Vector2(roundf((SCREEN.x - panel.size.x) * 0.5), roundf(top + maxf(0.0, room - panel.size.y) * 0.5))

func _cancel_feedback(frame: int) -> void:
	# Escape with no effect (main screen) stays silent; closing or going back plays the cancel cue.
	if not opened or opened_frame != frame: _play("cancel")

func _ensure_player() -> AudioStreamPlayer:
	var root := get_tree().root if is_inside_tree() else null
	if root == null: return null
	var player := root.get_node_or_null("UiSfx") as AudioStreamPlayer
	if player == null and not root.is_queued_for_deletion():
		player = AudioStreamPlayer.new()
		player.name = "UiSfx"
		player.bus = &"UI"
		player.max_polyphony = 4
		player.process_mode = Node.PROCESS_MODE_ALWAYS
		root.add_child(player)
	return player

func _play(cue: String) -> void:
	# The player lives on the root so a confirm cue survives the scene change it triggers.
	var player := get_tree().root.get_node_or_null("UiSfx") as AudioStreamPlayer if is_inside_tree() else null
	if player == null: return
	_last_cue = cue
	# Paid chest window: refusal has its own cue; acceptance sounds from the opened chest.
	if horizontal_choices and cue == "confirm": return
	player.stream = REFUSE_SFX if horizontal_choices and cue == "cancel" else SFX[cue]
	player.play()

func _exit_tree() -> void:
	# A confirm cue may outlive the menu (scene change it triggers); other cues end with their menu
	# so the audio server does not still hold a playback when the game quits.
	if _last_cue == "confirm" or not is_inside_tree(): return
	var player := get_tree().root.get_node_or_null("UiSfx") as AudioStreamPlayer
	if player != null: player.stop()

func _activate() -> void:
	if selection in unavailable or choices.is_empty(): return
	_handled_frame = Engine.get_process_frames()
	selected.emit(selection)

func _move_selection(direction: int) -> void:
	if choices.is_empty(): return
	for i in range(choices.size()):
		selection = posmod(selection + direction, choices.size())
		if selection not in unavailable: break
	_redraw_rows()

func _input(event: InputEvent) -> void:
	if not opened: return
	if event is InputEventMouse:
		# All mouse presses belong to the modal, including clicks outside its rows.
		if event is InputEventMouseButton:
			get_viewport().set_input_as_handled()
		if Engine.get_process_frames() <= opened_frame: return
		if horizontal_choices and footer.get_global_rect().has_point(event.position):
			if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
				if _handled_frame != Engine.get_process_frames(): _activate()
			return
		for i in range(rows.get_child_count()):
			if rows.get_child(i).get_global_rect().has_point(event.position):
				if i not in unavailable and selection != i:
					selection = i
					_redraw_rows()
				if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed and i not in unavailable:
					if _handled_frame != Engine.get_process_frames(): _activate()
				return
	elif event is InputEventKey and event.pressed and not event.echo:
		if Engine.get_process_frames() <= opened_frame: return
		var key: int = event.keycode
		if key not in [KEY_ESCAPE, KEY_ENTER, KEY_KP_ENTER, KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN]: return
		get_viewport().set_input_as_handled()
		if _handled_frame == Engine.get_process_frames(): return
		_handled_frame = Engine.get_process_frames()
		if key == KEY_ESCAPE: cancelled.emit()
		elif key in [KEY_ENTER, KEY_KP_ENTER]: _activate()
		elif horizontal_choices and key in [KEY_LEFT, KEY_RIGHT]: _move_selection(1 if key == KEY_RIGHT else -1)
		elif not horizontal_choices and key in [KEY_UP, KEY_DOWN]: _move_selection(1 if key == KEY_DOWN else -1)

func _process(_delta: float) -> void:
	if opened and horizontal_choices and is_instance_valid(_glow):
		_glow.modulate.a = 0.7 + 0.3 * sin(Time.get_ticks_msec() * 0.005)
	if not opened or Engine.get_process_frames() <= opened_frame or _handled_frame == Engine.get_process_frames(): return
	if Input.is_action_just_pressed("pause"):
		cancelled.emit()
		return
	var direction: int = int(Input.is_action_just_pressed("move_right" if horizontal_choices else "move_down")) - int(Input.is_action_just_pressed("move_left" if horizontal_choices else "move_up"))
	if direction != 0 and choices.size() > 0:
		_move_selection(direction)
	elif Input.is_action_just_pressed("interact") and selection not in unavailable:
		_activate()

extends CanvasLayer
@onready var controls = get_node("/root/Controls")
# RUN-021 presentation (Claude): paid chest reveal between payment and the reward cards. A
# "Treasure Found!" window waits for Open (E or a click); the chest then rattles, opens and
# releases a widening beam of light over a crescendo, ending in a flash that uncovers the cards.
# Space skips straight to the flash. Payment, offer, choice and modal ownership stay with the level.
signal revealed

const FONT = preload("res://assets/fonts/PixelOperator8.ttf")
const PANEL = preload("res://assets/sprites/ui_panel.png")
const FOCUS = preload("res://assets/sprites/ui_menu_focus.png")
const CURSOR = preload("res://assets/sprites/ui_menu_cursor.png")
const CHEST_KINDS = preload("res://assets/run018/ui/ui_chest_kind.png")
# Strip, frame size, mouth row above the foot (where the light leaves), widest beam half-width,
# lid cue. Same 6-frame strips as the world chests: frame 0 closed, frame 5 open.
const ART := {
	"common": [preload("res://assets/run018/world/item_chest_common.png"), Vector2i(24, 20), -12, 7, preload("res://assets/sounds/sfx_chest_open_common.wav")],
	"rare": [preload("res://assets/run018/world/item_chest_rare.png"), Vector2i(32, 24), -14, 9, preload("res://assets/sounds/run018/sfx_chest_open_rare.wav")],
}
const RISE_SFX = preload("res://assets/sounds/run021/sfx_chest_reveal_rise.wav")
const BURST_SFX = preload("res://assets/sounds/run021/sfx_chest_reveal_burst.wav")
const GOLD_TEXT = Color(0.941, 0.824, 0.478)
const DIM_TEXT = Color(0.651, 0.682, 0.733)
const SHADOW = Color(0.09, 0.075, 0.106)
# Neutral interaction light (docs/06: white / pale yellow), GOLD ramp of tools/art/palette.py.
const LIGHT := [Color("8c6b2e"), Color("c9a24a"), Color("f0d27a"), Color("fff4c4"), Color(1, 1, 1)]
const FLASH_COLOR = Color(1.0, 0.957, 0.82)
const SCREEN := Vector2(640, 360)
const WINDOW := Vector2(240, 236)
const INSET := 6.0  # gold trim of ui_panel.png
const PIXEL := 3.0  # the chest is shown at an integer 3x; every effect snaps to that grid
const FOOT_X := 114.0  # chest centre, local to the art layers (window centre minus the trim inset)
# The chest is centred vertically between the kind line (bottom at 44) and the Open button (top at 190).
const ART_TOP := 44.0
const ART_BOTTOM := 190.0
# Timeline in seconds from Open: two rattles, lid frames, beam, flash peak (= cards), flash fade.
const RATTLES := [Vector2(0.12, 0.32), Vector2(0.42, 0.68)]
const LID_AT := 0.7
const LID_FRAME := 0.08
const BEAM_AT := 0.95
const BEAM_GROW := 0.35
const CLIMAX := 2.9
const FLASH_IN := 0.15
const FLASH_OUT := 0.45
const FLASH_PEAK := 0.9
const SKIP_TO := CLIMAX - 0.06

var stage: String = ""  # "" idle, "intro" (Open), "reveal" (animation), "flash" (cards uncovered)
var kind: String = "common"
var elapsed: float = 0.0
var opened_frame: int = -1
var skipped: bool = false
var window: Control
var button: NinePatchRect
var hint: Label
var subtitle: Label
var _kind_icon: TextureRect
var _cursors: Array[TextureRect] = []
var _veil: ColorRect
var _flash: ColorRect
var _back: Control  # chest and rays, normal blend
var _light: Control  # beam, mouth glow and sparks, additive
var _rise: AudioStreamPlayer
var _burst: AudioStreamPlayer
var _lid: AudioStreamPlayer
var _lid_played: bool = false
var _rng := RandomNumberGenerator.new()
var _sparks: Array = []  # [x, y, vy, age, life] in art pixels
var _spark_debt: float = 0.0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 31  # above the reward cards (30) so the flash fades over them
	_veil = ColorRect.new()
	_veil.size = SCREEN
	_veil.color = Color(0.055, 0.045, 0.07, 0.62)
	_veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_veil)
	window = Control.new()
	window.position = ((SCREEN - WINDOW) * 0.5).round()
	window.size = WINDOW
	window.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(window)
	var frame := NinePatchRect.new()
	frame.texture = PANEL
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]: frame.set_patch_margin(side, 8)
	frame.size = WINDOW
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	window.add_child(frame)
	_back = _art_layer(false)
	_light = _art_layer(true)
	_back.draw.connect(_draw_back)
	_light.draw.connect(_draw_light)
	var title := _label("Treasure Found!", 16, GOLD_TEXT, Rect2(0, 12, WINDOW.x, 18))
	window.add_child(title)
	var kind_row := HBoxContainer.new()
	kind_row.alignment = BoxContainer.ALIGNMENT_CENTER
	kind_row.add_theme_constant_override("separation", 3)
	kind_row.position = Vector2(0, 32)
	kind_row.size = Vector2(WINDOW.x, 12)
	kind_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_kind_icon = TextureRect.new()
	_kind_icon.texture = AtlasTexture.new()
	_kind_icon.texture.atlas = CHEST_KINDS
	_kind_icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
	kind_row.add_child(_kind_icon)
	subtitle = _label("", 8, DIM_TEXT, Rect2())
	subtitle.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	kind_row.add_child(subtitle)
	window.add_child(kind_row)
	button = NinePatchRect.new()
	button.texture = FOCUS
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]: button.set_patch_margin(side, 4)
	button.size = Vector2(84, 20)
	button.position = Vector2(roundf((WINDOW.x - button.size.x) * 0.5), 190)
	button.mouse_filter = Control.MOUSE_FILTER_STOP
	button.gui_input.connect(_on_button_input)
	button.add_child(_label("Open", 16, GOLD_TEXT, Rect2(Vector2.ZERO, button.size)))
	window.add_child(button)
	for mirrored in [false, true]:
		var cursor := TextureRect.new()
		cursor.texture = CURSOR
		cursor.flip_h = mirrored
		cursor.mouse_filter = Control.MOUSE_FILTER_IGNORE
		window.add_child(cursor)
		_cursors.append(cursor)
	hint = _label("", 8, DIM_TEXT, Rect2(0, 216, WINDOW.x, 10))
	window.add_child(hint)
	_flash = ColorRect.new()
	_flash.size = SCREEN
	_flash.color = FLASH_COLOR
	_flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var glare := CanvasItemMaterial.new()
	glare.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD  # brightens toward white instead of a flat wash
	_flash.material = glare
	add_child(_flash)
	_rise = _player(RISE_SFX)
	_burst = _player(BURST_SFX)
	_lid = _player(null)
	visible = false

func _art_layer(additive: bool) -> Control:
	var art := Control.new()
	art.position = Vector2(INSET, INSET)
	art.size = WINDOW - Vector2(INSET, INSET) * 2.0
	art.clip_contents = true
	art.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if additive:
		var blend := CanvasItemMaterial.new()
		blend.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		art.material = blend
	window.add_child(art)
	return art

func _label(text: String, font_size: int, color: Color, rect: Rect2) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_override("font", FONT)
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_shadow_color", SHADOW)
	label.add_theme_constant_override("shadow_offset_x", 1)
	label.add_theme_constant_override("shadow_offset_y", 1)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if rect.size != Vector2.ZERO:
		label.position = rect.position
		label.size = rect.size
	return label

func _player(stream: AudioStream) -> AudioStreamPlayer:
	var audio := AudioStreamPlayer.new()
	audio.bus = &"SFX"
	audio.stream = stream
	add_child(audio)
	return audio

# Shows the closed chest of this kind and waits for Open. The level has already paid.
func present(chest_kind: String) -> void:
	kind = chest_kind if ART.has(chest_kind) else "common"
	stage = "intro"
	elapsed = 0.0
	skipped = false
	opened_frame = Engine.get_process_frames()
	_lid_played = false
	_sparks.clear()
	_spark_debt = 0.0
	_rng.seed = 21018 if kind == "rare" else 21017  # same sparkle pattern on every opening
	(_kind_icon.texture as AtlasTexture).region = Rect2(12 if kind == "rare" else 0, 0, 12, 12)
	subtitle.text = "Rare chest" if kind == "rare" else "Common chest"
	hint.text = controls.label("interact") + ": open"
	button.show()
	for cursor in _cursors: cursor.show()
	window.show()
	_veil.show()
	_flash.color.a = 0.0
	visible = true
	_place_cursors(0.0)
	_redraw()

func open() -> void:
	if stage != "intro": return
	stage = "reveal"
	elapsed = 0.0
	hint.text = controls.label("jump") + ": skip"
	button.hide()
	for cursor in _cursors: cursor.hide()
	_play(_rise)

func skip() -> void:
	if stage != "reveal" or elapsed >= SKIP_TO: return
	skipped = true
	elapsed = SKIP_TO

func _on_button_input(event: InputEvent) -> void:
	var click := event as InputEventMouseButton
	if click != null and click.pressed and click.button_index == MOUSE_BUTTON_LEFT:
		get_viewport().set_input_as_handled()
		if Engine.get_process_frames() > opened_frame: open()

func _process(delta: float) -> void:
	if stage.is_empty(): return
	if stage == "intro":
		_place_cursors(float(Time.get_ticks_msec()) / 1000.0)
		# The E that paid for the chest must not also press Open on the same frame.
		if Engine.get_process_frames() > opened_frame and Input.is_action_just_pressed("interact"): open()
		return
	elapsed += delta
	if stage == "reveal":
		if Input.is_action_just_pressed("jump"): skip()
		if not _lid_played and elapsed >= LID_AT:
			_lid_played = true
			if not skipped:
				_lid.stream = ART[kind][4]
				_play(_lid)
		_update_sparks(delta)
		_flash.color.a = FLASH_PEAK * clampf((elapsed - (CLIMAX - FLASH_IN)) / FLASH_IN, 0.0, 1.0)
		if elapsed >= CLIMAX: _climax()
	elif stage == "flash":
		_flash.color.a = FLASH_PEAK * (1.0 - clampf((elapsed - CLIMAX) / FLASH_OUT, 0.0, 1.0))
		if elapsed >= CLIMAX + FLASH_OUT:
			stage = ""
			visible = false
	_redraw()

func _climax() -> void:
	stage = "flash"
	_flash.color.a = FLASH_PEAK
	_rise.stop()
	_play(_burst)
	window.hide()
	_veil.hide()
	revealed.emit()

func _play(audio: AudioStreamPlayer) -> void:
	if get_parent() != null and get_parent().get("closing") == true: return
	audio.play()

func _place_cursors(time: float) -> void:
	var bob := 1.0 if fmod(time, 0.8) < 0.4 else 0.0  # nudges toward the button, like menu cursors
	var y := button.position.y + roundf((button.size.y - CURSOR.get_height()) * 0.5)
	_cursors[0].position = Vector2(button.position.x - CURSOR.get_width() - 4 + bob, y)
	_cursors[1].position = Vector2(button.position.x + button.size.x + 4 - bob, y)

func _redraw() -> void:
	_back.queue_redraw()
	_light.queue_redraw()

# 0 before the beam, then rising to 1 at the climax: drives width, pulse, rays and sparks.
func power() -> float:
	if stage == "intro": return 0.0
	return clampf((elapsed - BEAM_AT) / (CLIMAX - BEAM_AT), 0.0, 1.0)

func chest_frame() -> int:
	if stage == "intro" or elapsed < LID_AT: return 0
	return mini(5, 1 + int((elapsed - LID_AT) / LID_FRAME))

func _rattle() -> int:
	if stage != "reveal": return 0
	for span in RATTLES:
		if elapsed >= span.x and elapsed < span.y: return 1 if int(elapsed * 30.0) % 2 == 0 else -1
	return 0

func _half_width() -> int:
	return 1 + int(roundf((ART[kind][3] - 1) * pow(power(), 1.5)))

func _beam_top() -> float:
	var grow := clampf((elapsed - BEAM_AT) / BEAM_GROW, 0.0, 1.0)
	grow = 1.0 - (1.0 - grow) * (1.0 - grow)
	return lerpf(float(ART[kind][2]), -ceilf(foot().y / PIXEL), grow)

func _cell(canvas: Control, x: float, y: float, w: float, h: float, color: Color) -> void:
	canvas.draw_rect(Rect2(roundf(x), roundf(y), roundf(w), roundf(h)), color)

# Chest foot for the current kind: the 3x chest is centred in the free band of the window.
func foot() -> Vector2:
	var height: float = ART[kind][1].y * PIXEL
	var centre: float = (ART_TOP + ART_BOTTOM) * 0.5 - INSET
	return Vector2(FOOT_X, roundf((centre + height * 0.5) / PIXEL) * PIXEL)

func _draw_back() -> void:
	var art: Array = ART[kind]
	var size: Vector2i = art[1]
	_back.draw_set_transform(foot(), 0.0, Vector2(PIXEL, PIXEL))
	var lit := 1.0 + 0.3 * power()
	var x := -size.x / 2 + _rattle()
	_back.draw_texture_rect_region(art[0], Rect2(x, -size.y, size.x, size.y), Rect2(chest_frame() * size.x, 0, size.x, size.y), Color(lit, lit, lit * 0.94))

func _draw_light() -> void:
	if stage == "intro": return
	_light.draw_set_transform(foot(), 0.0, Vector2(PIXEL, PIXEL))
	var mouth: int = ART[kind][2]
	var widest: int = ART[kind][3]
	var p := power()
	# Light leaking from the lid seam during the second rattle, then the open mouth glow.
	if stage == "reveal" and elapsed >= RATTLES[1].x and elapsed < LID_AT and int(elapsed * 20.0) % 3 != 0:
		_cell(_light, -widest, mouth, widest * 2, 1, Color(LIGHT[2], 0.55))
	if elapsed < BEAM_AT: return
	var pulse := 0.85 + 0.15 * sin(elapsed * lerpf(8.0, 30.0, p))
	var half := _half_width()
	var top := _beam_top()
	var height := mouth - top + 1.0
	_draw_rays(mouth, half, p)
	# Mouth spill: a short horizontal flare that widens with the beam.
	var spill := widest + 2 + int(p * 4.0)
	_cell(_light, -spill, mouth, spill * 2, 1, Color(LIGHT[2], 0.35 * pulse))
	_cell(_light, -spill + 2, mouth - 1, spill * 2 - 4, 1, Color(LIGHT[3], 0.3 * pulse))
	# Beam: dithered halo, soft body, bright core, white heart; fades a little toward the top.
	for y in range(int(top), mouth + 1):
		var fade := lerpf(0.55, 1.0, clampf((y - top) / maxf(1.0, height), 0.0, 1.0)) * pulse
		for side in [-1, 1]:
			for k in [half + 1, half + 2]:
				if (y + k + int(elapsed * 12.0)) % 2 == 0:
					_cell(_light, k if side > 0 else -k - 1, y, 1, 1, Color(LIGHT[1], 0.3 * fade))
		_cell(_light, -half - 1, y, half * 2 + 2, 1, Color(LIGHT[2], 0.32 * fade))
		_cell(_light, -half, y, half * 2, 1, Color(LIGHT[3], 0.5 * fade))
		var heart := maxi(1, half / 3)
		_cell(_light, -heart, y, heart * 2, 1, Color(LIGHT[4], 0.7 * fade))
	for spark in _sparks:
		var life: float = spark[3] / spark[4]
		var alpha := (1.0 - life) * (0.65 + 0.35 * sin(spark[3] * 22.0 + spark[0]))
		var color: Color = LIGHT[4] if int(spark[0] * 7.0) % 3 == 0 else LIGHT[3]
		_cell(_light, spark[0], spark[1], 1, 1, Color(color, alpha))
		if spark[4] > 0.95 and life < 0.5:  # a few larger glints read as a cross
			_cell(_light, spark[0] - 1, spark[1], 3, 1, Color(color, alpha * 0.45))
			_cell(_light, spark[0], spark[1] - 1, 1, 3, Color(color, alpha * 0.45))

func _draw_rays(mouth: int, half: int, p: float) -> void:
	var strength := clampf((elapsed - BEAM_AT - 0.45) / 0.8, 0.0, 1.0)
	if strength <= 0.0: return
	var length := lerpf(18.0, 64.0, p)
	for i in range(9):
		var angle := deg_to_rad(-90.0 + (i - 4) * 19.0 + sin(elapsed * 1.3 + i) * 3.0)
		var direction := Vector2(cos(angle), sin(angle))
		var weight := 1.0 if i % 2 == 0 else 0.6
		var r := float(half + 2)
		while r < length:
			var at := Vector2(0, mouth) + direction * r
			if (int(r) + i) % 2 == 0:
				_cell(_light, floorf(at.x), floorf(at.y), 1, 1, Color(LIGHT[2], 0.2 * strength * weight * (1.0 - r / length)))
			r += 1.0

func _update_sparks(delta: float) -> void:
	for spark in _sparks:
		spark[1] += spark[2] * delta
		spark[3] += delta
	_sparks = _sparks.filter(func(spark: Array) -> bool: return spark[3] < spark[4])
	if elapsed < BEAM_AT + 0.1 or elapsed >= CLIMAX: return
	_spark_debt += delta * lerpf(6.0, 42.0, power())
	var half := _half_width()
	while _spark_debt >= 1.0:
		_spark_debt -= 1.0
		_sparks.append([floorf(_rng.randf_range(-half - 2.0, half + 2.0)), float(ART[kind][2]), -_rng.randf_range(18.0, 44.0), 0.0, _rng.randf_range(0.5, 1.1)])

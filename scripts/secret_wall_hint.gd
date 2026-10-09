# Secret wall hint (RUN-021 Claude art): subtle overlay on the entrance of a secret wall (glow,
# cracks or tint, see SecretWallStyle), drawn just above its SecretWallMask. Presentation only:
# no collision, save, gameplay or sound. The parent wall owns the reveal and fades this node
# through its own modulate:a; the optional breathing below only uses self_modulate.
class_name SecretWallHint
extends Node2D
# Absolute world layer: above the mask (50), below the reveal crumble (52) and floating text (60).
const HINT_Z := 51
const DEFAULT_RECT := Rect2(-8, -32, 16, 32)
var style: SecretWallStyle
# Entrance in the wall's coordinates (the hint sits at its origin).
var rect := DEFAULT_RECT
var _time := 0.0
func _init() -> void:
	z_as_relative = false
	z_index = HINT_Z
	set_process(false)
func configure(p_style: Resource, p_rect: Rect2 = DEFAULT_RECT) -> void:
	style = p_style as SecretWallStyle
	rect = p_rect
	material = null
	if style != null and style.additive:
		var blend := CanvasItemMaterial.new()
		blend.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		material = blend
	_time = 0.0
	self_modulate = Color.WHITE
	set_process(style != null and style.pulse_amount > 0.0)
	queue_redraw()
func _process(delta: float) -> void:
	var period := maxf(1.0, style.pulse_period)
	_time = fmod(_time + delta, period)
	# Eases between 1 and 1 - pulse_amount: a breath, never a flash.
	self_modulate.a = 1.0 - style.pulse_amount * (0.5 - 0.5 * cos(TAU * _time / period))
func _draw() -> void:
	if style == null or not rect.has_area(): return
	_layer(style.texture, style.hint_color)
	_layer(style.detail_texture, style.detail_color)
# 1:1 texels, centred on the entrance and resting on its floor, clipped to it: pixels stay on
# the grid and nothing spills past the entrance whatever its size.
func _layer(tex: Texture2D, color: Color) -> void:
	if tex == null: return
	var size := tex.get_size()
	var dest := Rect2(Vector2(rect.position.x + floorf((rect.size.x - size.x) / 2.0), rect.end.y - size.y), size)
	var cut := dest.intersection(rect)
	if not cut.has_area(): return
	var tint := color
	tint.a *= clampf(style.intensity, 0.0, 1.0)
	draw_texture_rect_region(tex, cut, Rect2(cut.position - dest.position, cut.size), tint)

@tool
# Backdrop of N2-N4 (RUN-020), same structure as backdrop.gd: a sky fixed to the screen,
# drifting N1 clouds and haze tinted per biome, three parallax scenery bands (far, mid, near;
# the near band is RUN-021) and a few slow motes. Purely visual and low-contrast; drawn behind
# Decor, Terrain and gameplay.
extends Node2D
const CLOUDS = preload("res://assets/sprites/bg_clouds.png")
const MIST = preload("res://assets/sprites/bg_mist.png")
const SKIES = [preload("res://assets/run020/bg_blight_town_sky.png"), preload("res://assets/run020/bg_black_forrest_sky.png"), preload("res://assets/run020/bg_forbidden_graveyard_sky.png")]
const FARS = [preload("res://assets/run020/bg_blight_town_far.png"), preload("res://assets/run020/bg_black_forrest_far.png"), preload("res://assets/run020/bg_forbidden_graveyard_far.png")]
const MIDS = [preload("res://assets/run020/bg_blight_town_mid.png"), preload("res://assets/run020/bg_black_forrest_mid.png"), preload("res://assets/run020/bg_forbidden_graveyard_mid.png")]
const NEARS = [preload("res://assets/run021/bg_blight_town_near.png"), preload("res://assets/run021/bg_black_forrest_near.png"), preload("res://assets/run021/bg_forbidden_graveyard_near.png")]
# Per biome: cloud tint, haze tint, colour below the near band (its last row), mote colour, mote count,
# mote rise speed, ground colour of the mid band (fills behind the near band).
const LOOKS = [
	[Color(0.95, 0.92, 0.82, 0.8), Color(0.82, 0.8, 0.62, 1.0), Color("111317"), Color(0.55, 0.52, 0.3), 22, 1.0, Color("1b1e22")],
	[Color(0.75, 0.85, 1.0, 0.55), Color(0.7, 0.85, 0.9, 1.0), Color("0a1012"), Color(0.5, 0.68, 0.6), 18, 0.35, Color("10181a")],
	[Color(0.85, 0.78, 0.95, 0.75), Color(0.75, 0.8, 0.95, 1.0), Color("120f17"), Color(0.45, 0.66, 0.68), 20, 0.6, Color("19161f")],
]
@export_range(2, 4) var world_level: int = 2:
	set(value):
		world_level = value
		queue_redraw()
# Camera top at the start of the level; layers are placed for this framing (floor at y 144).
@export var reference_top := -74.0
const CLOUD_DRIFT = 2.5 # px per second
const MIST_DRIFT = 4.0
var _elapsed := 0.0
func _process(delta: float) -> void:
	_elapsed += delta
	queue_redraw()
func _draw() -> void:
	var b := clampi(world_level, 2, 4) - 2
	var look: Array = LOOKS[b]
	var size := get_viewport_rect().size
	var top_left := Vector2(0, reference_top)
	var camera := get_viewport().get_camera_2d()
	if camera != null and not Engine.is_editor_hint():
		top_left = camera.get_screen_center_position() - size * 0.5
	var dy := top_left.y - reference_top
	draw_texture(SKIES[b], top_left)
	_draw_band(CLOUDS, top_left, size, top_left.x * 0.02 + _elapsed * CLOUD_DRIFT, 14.0 - dy * 0.02, look[0])
	_draw_band(FARS[b], top_left, size, top_left.x * 0.08, 58.0 - dy * 0.05)
	_draw_band(MIST, top_left, size, top_left.x * 0.2 + _elapsed * MIST_DRIFT, 140.0 - dy * 0.1, look[1])
	var mid: Texture2D = MIDS[b]
	var mid_y := 104.0 - dy * 0.15
	_draw_band(mid, top_left, size, top_left.x * 0.3, mid_y)
	# The mid band's ground continues down behind the near band, which fades into the final fill.
	var bottom := roundf(mid_y) + mid.get_height()
	draw_rect(Rect2(top_left + Vector2(0, bottom), Vector2(size.x, maxf(0.0, size.y - bottom))), look[6])
	var near: Texture2D = NEARS[b]
	var near_y := 170.0 - dy * 0.2
	_draw_band(near, top_left, size, top_left.x * 0.42, near_y)
	var below := roundf(near_y) + near.get_height()
	draw_rect(Rect2(top_left + Vector2(0, below), Vector2(size.x, maxf(0.0, size.y - below))), look[2])
	# Slow motes (screen space, very dim): ash and spores, pale forest specks, spectral wisps.
	var mote: Color = look[3]
	for i in int(look[4]):
		var speed := (5.0 + float(i % 5) * 1.5) * float(look[5])
		var x := fposmod(float(i) * 97.0 + _elapsed * (3.0 + float(i % 3)) + sin(_elapsed * 0.6 + float(i)) * 8.0, size.x)
		var y := fposmod(float(i) * 53.0 - _elapsed * speed, size.y)
		var a := 0.18 + 0.16 * sin(_elapsed * 1.3 + float(i) * 1.7)
		draw_rect(Rect2((top_left + Vector2(x, y)).round(), Vector2.ONE), Color(mote, a))
func _draw_band(texture: Texture2D, top_left: Vector2, size: Vector2, scroll_x: float, screen_y: float, tint := Color.WHITE) -> void:
	var width := float(texture.get_width())
	var first := floori(scroll_x / width)
	var origin_y := roundf(screen_y)
	for k in range(first, first + ceili(size.x / width) + 2):
		draw_texture(texture, top_left + Vector2(roundf(k * width - scroll_x), origin_y), tint)

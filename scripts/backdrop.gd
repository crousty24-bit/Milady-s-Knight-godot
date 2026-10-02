@tool
# Night sky fixed to the screen, drifting clouds, and parallax scenery bands
# (far citadel, viaduct of arches, haze, near ruined forest) plus a few slow ash motes.
# Purely visual and low-contrast; drawn behind Kingdom and Terrain.
extends Node2D
const SKY = preload("res://assets/sprites/bg_sky.png")
const CLOUDS = preload("res://assets/sprites/bg_clouds.png")
const FAR = preload("res://assets/sprites/bg_far.png")
const ARCHES = preload("res://assets/sprites/bg_arches.png")
const MID = preload("res://assets/sprites/bg_mid.png")
const MIST = preload("res://assets/sprites/bg_mist.png")
# Camera top in the starting village; layers are placed for this framing.
const REFERENCE_TOP = -74.0
const CLOUD_DRIFT = 2.5 # px per second
const MIST_DRIFT = 4.0
const MOTES = 26
# texture, horizontal factor, vertical factor, screen y at the reference framing, drift px/s
var layers := [
	[FAR, 0.08, 0.05, 58.0, 0.0],
	[ARCHES, 0.16, 0.09, 132.0, 0.0],
	[MIST, 0.2, 0.1, 140.0, MIST_DRIFT],
	[MID, 0.3, 0.15, 104.0, 0.0],
]
var _elapsed := 0.0
func _process(delta: float) -> void:
	_elapsed += delta
	queue_redraw()
func _draw() -> void:
	var size := get_viewport_rect().size
	var top_left := Vector2(0, REFERENCE_TOP)
	var camera := get_viewport().get_camera_2d()
	if camera != null and not Engine.is_editor_hint():
		top_left = camera.get_screen_center_position() - size * 0.5
	draw_texture(SKY, top_left)
	_draw_band(CLOUDS, top_left, size, top_left.x * 0.02 + _elapsed * CLOUD_DRIFT, 14.0 - (top_left.y - REFERENCE_TOP) * 0.02)
	for layer in layers:
		var texture: Texture2D = layer[0]
		var screen_y: float = layer[3] - (top_left.y - REFERENCE_TOP) * layer[2]
		_draw_band(texture, top_left, size, top_left.x * layer[1] + _elapsed * layer[4], screen_y)
		if texture == MID:
			# The forest floor continues down to the bottom of the screen.
			var bottom := screen_y + texture.get_height()
			draw_rect(Rect2(top_left + Vector2(0, bottom), Vector2(size.x, maxf(0.0, size.y - bottom))), Color("1a212b"))
	# Slow ash motes drifting up and sideways (screen space, very dim).
	for i in MOTES:
		var speed := 5.0 + float(i % 5) * 1.5
		var x := fposmod(float(i) * 97.0 + _elapsed * (3.0 + float(i % 3)) + sin(_elapsed * 0.6 + float(i)) * 8.0, size.x)
		var y := fposmod(float(i) * 53.0 - _elapsed * speed, size.y)
		var a := 0.22 + 0.18 * sin(_elapsed * 1.3 + float(i) * 1.7)
		draw_rect(Rect2((top_left + Vector2(x, y)).round(), Vector2.ONE), Color(0.76, 0.42, 0.22, a))
func _draw_band(texture: Texture2D, top_left: Vector2, size: Vector2, scroll_x: float, screen_y: float) -> void:
	var width := float(texture.get_width())
	var first := floori(scroll_x / width)
	var origin_y := roundf(screen_y)
	for k in range(first, first + ceili(size.x / width) + 2):
		draw_texture(texture, top_left + Vector2(roundf(k * width - scroll_x), origin_y))

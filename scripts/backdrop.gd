@tool
# Night sky fixed to the screen and two scenery bands scrolled at reduced speed.
# Purely visual; drawn behind Kingdom and Terrain.
extends Node2D
const SKY = preload("res://assets/sprites/bg_sky.png")
const FAR = preload("res://assets/sprites/bg_far.png")
const MID = preload("res://assets/sprites/bg_mid.png")
const MIST = preload("res://assets/sprites/bg_mist.png")
# Camera top in the starting village; layers are placed for this framing.
const REFERENCE_TOP = -74.0
# texture, horizontal factor, vertical factor, screen y at the reference framing
var layers := [
	[FAR, 0.08, 0.05, 58.0],
	[MIST, 0.2, 0.1, 150.0],
	[MID, 0.3, 0.15, 104.0],
]
func _process(_delta: float) -> void:
	queue_redraw()
func _draw() -> void:
	var size := get_viewport_rect().size
	var top_left := Vector2(0, REFERENCE_TOP)
	var camera := get_viewport().get_camera_2d()
	if camera != null and not Engine.is_editor_hint():
		top_left = camera.get_screen_center_position() - size * 0.5
	draw_texture(SKY, top_left)
	for layer in layers:
		var texture: Texture2D = layer[0]
		var width := float(texture.get_width())
		var scroll_x: float = top_left.x * layer[1]
		var screen_y: float = layer[3] - (top_left.y - REFERENCE_TOP) * layer[2]
		var first := floori(scroll_x / width)
		for k in range(first, first + ceili(size.x / width) + 2):
			draw_texture(texture, top_left + Vector2(k * width - scroll_x, screen_y))
		if texture == MID:
			# The forest floor continues down to the bottom of the screen.
			var bottom := screen_y + texture.get_height()
			draw_rect(Rect2(top_left + Vector2(0, bottom), Vector2(size.x, maxf(0.0, size.y - bottom))), Color("1a212b"))

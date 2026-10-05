extends Node2D
# Technical marker until the Claude art pass: never presented as a final asset.
func _draw() -> void:
	draw_rect(Rect2(-5, -5, 10, 14), Color.DARK_RED)
	draw_line(Vector2(-3, 1), Vector2(3, 1), Color.WHITE, 2)
	draw_line(Vector2(0, -2), Vector2(0, 4), Color.WHITE, 2)

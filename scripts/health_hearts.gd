extends Control

const HEARTS_PER_ROW: int = 5
const HEART_SPACING: int = 12
const ROW_SPACING: int = 11
# Full, half and empty hearts are the first three 12x12 icons (tools/art/ui.py).
const ICONS = preload("res://assets/sprites/ui_icons.png")
var current_units: int = 30
var maximum_units: int = 30

func set_values(current: int, maximum: int) -> void:
	current_units = clampi(current, 0, maximum)
	maximum_units = maximum
	queue_redraw()

func displayed_half_hearts() -> int:
	return ceili(float(current_units) / 5.0)

func _draw() -> void:
	var heart_count := ceili(float(maximum_units) / HealthUnits.PER_HP)
	var filled_halves := displayed_half_hearts()
	for index in range(heart_count):
		var origin := Vector2(index % HEARTS_PER_ROW * HEART_SPACING, index / HEARTS_PER_ROW * ROW_SPACING)
		var halves := clampi(filled_halves - index * 2, 0, 2)
		var icon: int = 0 if halves == 2 else (1 if halves == 1 else 2)
		draw_texture_rect_region(ICONS, Rect2(origin, Vector2(12, 12)), Rect2(icon * 12, 0, 12, 12))

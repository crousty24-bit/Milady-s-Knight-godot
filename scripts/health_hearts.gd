extends Control

const HEARTS_PER_ROW: int = 5
const HEART_SPACING: int = 11
const ROW_SPACING: int = 11
const EMPTY_COLOR := Color("5c5960")
const FILLED_COLOR := Color("df6971")
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
		var outline := PackedVector2Array([Vector2(0, 2), Vector2(1, 0), Vector2(3, 0), Vector2(4, 1), Vector2(5, 0), Vector2(7, 0), Vector2(8, 2), Vector2(8, 4), Vector2(4, 8), Vector2(0, 4)])
		for point in range(outline.size()): outline[point] += origin
		draw_colored_polygon(outline, EMPTY_COLOR)
		var halves := clampi(filled_halves - index * 2, 0, 2)
		if halves == 0: continue
		var fill := PackedVector2Array([Vector2(1, 2), Vector2(2, 1), Vector2(3, 1), Vector2(4, 2), Vector2(4, 7), Vector2(1, 4)]) if halves == 1 else PackedVector2Array([Vector2(1, 2), Vector2(2, 1), Vector2(3, 1), Vector2(4, 2), Vector2(5, 1), Vector2(6, 1), Vector2(7, 2), Vector2(7, 4), Vector2(4, 7), Vector2(1, 4)])
		for point in range(fill.size()): fill[point] += origin
		draw_colored_polygon(fill, FILLED_COLOR)

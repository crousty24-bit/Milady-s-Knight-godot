extends Control

const HEARTS_PER_ROW: int = 5
const HEART_SPACING: int = 12
const ROW_SPACING: int = 11
# Full, half and empty hearts are the first three 12x12 icons (tools/art/ui.py).
const ICONS = preload("res://assets/sprites/ui_icons.png")
var current_units: int = 30
var maximum_units: int = 30

# RUN-021 (Claude): a heart added to the bar (HP bonus) pops in: grows past full size with a light
# halo, then settles. The first values set on level entry never pop.
const POP_TIME: float = 0.6
const POP_PEAK: float = 0.2
var _initialized: bool = false
var _pops: Dictionary = {}

func set_values(current: int, maximum: int) -> void:
	var before: int = ceili(float(maximum_units) / HealthUnits.PER_HP)
	current_units = clampi(current, 0, maximum)
	maximum_units = maximum
	var after: int = ceili(float(maximum_units) / HealthUnits.PER_HP)
	if _initialized:
		for index in range(before, after): _pops[index] = 0.0
	_initialized = true
	queue_redraw()

func popping() -> bool:
	return not _pops.is_empty()

func _process(delta: float) -> void:
	if _pops.is_empty(): return
	for index in _pops.keys():
		_pops[index] += delta
		if _pops[index] >= POP_TIME: _pops.erase(index)
	queue_redraw()

func _pop_scale(t: float) -> float:
	if t < POP_PEAK: return lerpf(0.0, 1.6, ease(t / POP_PEAK, 0.4))
	return lerpf(1.6, 1.0, ease((t - POP_PEAK) / (POP_TIME - POP_PEAK), 0.5))

func displayed_half_hearts() -> int:
	return ceili(float(current_units) / 5.0)

func _draw() -> void:
	var heart_count := ceili(float(maximum_units) / HealthUnits.PER_HP)
	var filled_halves := displayed_half_hearts()
	for index in range(heart_count):
		var origin := Vector2(index % HEARTS_PER_ROW * HEART_SPACING, index / HEARTS_PER_ROW * ROW_SPACING)
		var halves := clampi(filled_halves - index * 2, 0, 2)
		var icon: int = 0 if halves == 2 else (1 if halves == 1 else 2)
		if _pops.has(index):
			var t: float = _pops[index]
			var centre := origin + Vector2(6, 6)
			var glow: float = 1.0 - t / POP_TIME
			draw_arc(centre, 3.0 + 9.0 * t / POP_TIME, 0.0, TAU, 16, Color(0.941, 0.478, 0.353, glow), 1.0)
			var size: float = _pop_scale(t)
			draw_set_transform(centre, 0.0, Vector2(size, size))
			draw_texture_rect_region(ICONS, Rect2(Vector2(-6, -6), Vector2(12, 12)), Rect2(icon * 12, 0, 12, 12), Color(1.0 + glow, 1.0 + glow, 1.0 + glow))
			draw_set_transform(Vector2.ZERO)
			continue
		draw_texture_rect_region(ICONS, Rect2(origin, Vector2(12, 12)), Rect2(icon * 12, 0, 12, 12))

extends StaticBody2D
signal phase_changed(phase: int)
signal warning_started
signal extended
signal retracted

enum Phase { RETRACTED, WARNING, EXTENDED }
# Technical fixture defaults, in gameplay seconds. Phase offset is deterministic.
@export_range(0.05, 30.0) var safe_duration: float = 1.5
@export_range(0.05, 10.0) var warning_duration: float = 0.5
@export_range(0.05, 30.0) var danger_duration: float = 1.0
@export_range(0.0, 60.0) var initial_phase: float = 0.0
var phase: int = -1
var cycle_time: float = 0.0

func _ready() -> void:
	cycle_time = initial_phase
	_update_phase()

func _physics_process(delta: float) -> void:
	cycle_time += delta
	_update_phase()
	if phase != Phase.EXTENDED: return
	for body in $Contact.get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			var away := signf(to_local(body.global_position).x)
			if is_zero_approx(away): away = -body.facing
			body.take_damage(0.5, Vector2(away * 90.0, -180.0).rotated(global_rotation), SlicePlayer.DamageSource.SOLID_TRAP)

func _update_phase() -> void:
	var t := fposmod(cycle_time, safe_duration + warning_duration + danger_duration)
	var next := Phase.RETRACTED if t < safe_duration else (Phase.WARNING if t < safe_duration + warning_duration else Phase.EXTENDED)
	if next == phase: return
	phase = next
	$Points.set_deferred("disabled", phase != Phase.EXTENDED)
	phase_changed.emit(phase)
	if phase == Phase.WARNING: warning_started.emit()
	elif phase == Phase.EXTENDED: extended.emit()
	else: retracted.emit()
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(-16, -2, 32, 2), Color.DIM_GRAY)
	if phase == Phase.RETRACTED: return
	var tint := Color.ORANGE if phase == Phase.WARNING else Color.INDIAN_RED
	for x in [-12, -4, 4, 12]:
		draw_colored_polygon(PackedVector2Array([Vector2(x - 4, -2), Vector2(x, -12 if phase == Phase.EXTENDED else -5), Vector2(x + 4, -2)]), tint)

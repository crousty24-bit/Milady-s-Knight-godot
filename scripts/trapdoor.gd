extends StaticBody2D
signal warning_started
signal opened
@export_range(0.05, 5.0) var warning_duration: float = 0.4
var triggered: bool = false
var is_open: bool = false
var warning_remaining: float = 0.0

func _physics_process(delta: float) -> void:
	if is_open: return
	if triggered:
		warning_remaining -= delta
		if warning_remaining <= 0.0:
			is_open = true
			$Solid.set_deferred("disabled", true)
			opened.emit()
			queue_redraw()
		return
	for body in $Trigger.get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			# Player origin is its feet. Side/below contact does not open the floor.
			var feet := to_local(body.global_position)
			if absf(feet.x) <= 16.0 and feet.y <= 2.0 and feet.y >= -8.0 and body.velocity.dot(Vector2.DOWN.rotated(global_rotation)) >= 0.0:
				triggered = true
				warning_remaining = warning_duration
				warning_started.emit()
				queue_redraw()
				break

func _draw() -> void:
	if is_open:
		draw_line(Vector2(-16, 0), Vector2(-16, 8), Color.DIM_GRAY, 2)
		draw_line(Vector2(16, 0), Vector2(16, 8), Color.DIM_GRAY, 2)
	else: draw_rect(Rect2(-16, 0, 32, 4), Color.ORANGE if triggered else Color.SLATE_GRAY)

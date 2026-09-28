@tool
extends StaticBody2D

const DAMAGE = 0.5

func _physics_process(_delta: float) -> void:
	if Engine.is_editor_hint(): return
	for body in $Contact.get_overlapping_bodies():
		if body is SlicePlayer:
			var away := signf(to_local(body.global_position).x)
			if is_zero_approx(away): away = -body.facing
			var impulse := Vector2(away * 90.0, -180.0).rotated(global_rotation)
			body.take_damage(DAMAGE, impulse, SlicePlayer.DamageSource.SOLID_TRAP)

func _draw() -> void:
	draw_rect(Rect2(-16, -2, 32, 2), Color("596475"))
	for x in range(-12, 16, 8):
		draw_colored_polygon(PackedVector2Array([Vector2(x - 4, 0), Vector2(x, -12), Vector2(x + 4, 0)]), Color("c5d4df"))
		draw_line(Vector2(x, -10), Vector2(x + 2, -3), Color("ffffff"))

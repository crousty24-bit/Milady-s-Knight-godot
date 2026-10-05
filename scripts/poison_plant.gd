extends StaticBody2D
signal contacted(player: SlicePlayer)

func _physics_process(_delta: float) -> void:
	for body in $Contact.get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			var away := signf(to_local(body.global_position).x)
			if is_zero_approx(away): away = -body.facing
			body.take_damage(1.0, Vector2(away * 90.0, -180.0).rotated(global_rotation), SlicePlayer.DamageSource.SOLID_TRAP)
			contacted.emit(body)

func _draw() -> void:
	draw_rect(Rect2(-8, -20, 16, 20), Color.DARK_OLIVE_GREEN)
	draw_circle(Vector2(0, -18), 10, Color.MEDIUM_PURPLE)

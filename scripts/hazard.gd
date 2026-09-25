@tool
extends Area2D
@export var lethal: bool = false
func _physics_process(_delta: float) -> void:
	if Engine.is_editor_hint(): return
	for body in get_overlapping_bodies():
		if body is SlicePlayer:
			if lethal: body.take_damage(0.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)
			else: body.take_damage(1.0, Vector2(-90 if body.facing > 0 else 90, -180), SlicePlayer.DamageSource.SOLID_TRAP)
func _draw() -> void:
	if lethal: return
	draw_rect(Rect2(-16,-2,32,3),Color("392139"))
	for x in range(-14, 16, 7):
		draw_colored_polygon(PackedVector2Array([Vector2(x-3,0),Vector2(x,-12),Vector2(x+4,0)]),Color("d58bb1"))
		draw_line(Vector2(x,-10),Vector2(x+1,-3),Color("ffe0da"))

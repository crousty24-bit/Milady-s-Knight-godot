@tool
extends Area2D
@export var lethal: bool = false
func _physics_process(_delta: float) -> void:
	if Engine.is_editor_hint(): return
	for body in get_overlapping_bodies():
		if body is SlicePlayer:
			if lethal: body.take_damage(0.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)
			else:
				var away := signf(body.global_position.x - global_position.x)
				if is_zero_approx(away): away = -body.facing
				body.take_damage(1.0, Vector2(away * 90.0, -180), SlicePlayer.DamageSource.SOLID_TRAP)
const ART = preload("res://assets/sprites/trap_thorns.png")
var shown_frame: int = -1

func _process(_delta: float) -> void:
	if lethal: return
	# The bramble pulses slowly (4-frame strip at about 5 fps).
	var frame := int(Time.get_ticks_msec() / 200.0 + position.x * 0.05) % 4
	if frame != shown_frame:
		shown_frame = frame
		queue_redraw()

func _draw() -> void:
	if lethal: return
	# Corrupted bramble (tools/art/hazards.py), bottom-centre on the node origin.
	draw_texture_rect_region(ART, Rect2(-16, -16, 32, 16), Rect2(maxi(shown_frame, 0) * 32, 0, 32, 16))

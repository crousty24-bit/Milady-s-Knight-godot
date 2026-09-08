@tool
extends Node2D
signal offering_requested
const COST: int = 12
var opened: bool = false
var lift: float = 0.0
func open() -> void:
	if opened: return
	opened = true
	$Barrier/Shape.set_deferred("disabled", true)
	create_tween().tween_property(self, "lift", 46.0, 0.7).set_trans(Tween.TRANS_SINE)
	$Sound.play()
func _process(_delta: float) -> void:
	queue_redraw()
	if Engine.is_editor_hint(): return
	if opened: return
	for body in $OfferingArea.get_overlapping_bodies():
		if body is SlicePlayer and not body.dead and Input.is_action_just_pressed("interact"):
			offering_requested.emit()
func player_near() -> bool:
	return $OfferingArea.has_overlapping_bodies()
func _draw() -> void:
	var stone = Color("5b6061")
	for x in [-24, 16]:
		for y in range(-64, 0, 8):
			draw_rect(Rect2(x, y, 9, 7), stone)
			draw_line(Vector2(x, y), Vector2(x+8, y), Color("92918a"))
	draw_rect(Rect2(-24,-67,49,5), stone)
	draw_rect(Rect2(-16,-60,32,60), Color("12181e"))
	for x in range(-12, 16, 6): draw_rect(Rect2(x, -52-lift, 2, 52), Color("b9a16d"))
	if not opened:
		draw_circle(Vector2(0,-25-lift),5,Color("e4bd68"))
		draw_rect(Rect2(-1,-28-lift,2,6),Color("584632"))

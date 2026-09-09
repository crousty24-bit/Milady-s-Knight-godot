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
	create_tween().tween_property(self, "lift", 104.0, 0.7).set_trans(Tween.TRANS_SINE)
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
		for y in range(-104, 0, 8):
			draw_rect(Rect2(x, y, 9, 7), stone)
			draw_line(Vector2(x, y), Vector2(x+8, y), Color("92918a"))
	draw_rect(Rect2(-24,-104,49,4), stone)
	draw_rect(Rect2(-16,-100,32,100), Color("12181e"))
	# Smooth iron panel matches the actual 16x100 barrier; side masonry is framing.
	draw_rect(Rect2(-8,-100-lift,16,100), Color("414846"))
	for x in [-8, -1, 6]: draw_rect(Rect2(x, -100-lift, 2, 100), Color("b9a16d"))
	for y in [-96, -52, -8]: draw_rect(Rect2(-8,y-lift,16,2), Color("897a5a"))
	if not opened:
		draw_circle(Vector2(0,-25-lift),5,Color("e4bd68"))
		draw_rect(Rect2(-1,-28-lift,2,6),Color("584632"))

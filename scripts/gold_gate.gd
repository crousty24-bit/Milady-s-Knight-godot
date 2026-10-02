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
	# Stone frame around the 16x100 opening, then the iron panel that lifts (tools/art/hazards.py).
	var art: Texture2D = preload("res://assets/sprites/prop_gold_gate.png")
	draw_texture_rect_region(art, Rect2(-28, -112, 56, 112), Rect2(0, 0, 56, 112))
	var panel_x: float = 72.0 if opened else 56.0
	# The lifted part slides into the lintel and is hidden by the wall.
	var visible_height: float = 100.0 - minf(lift, 100.0)
	if visible_height > 0.0:
		draw_texture_rect_region(art, Rect2(-8, -100, 16, visible_height), Rect2(panel_x, 12 + 100.0 - visible_height, 16, visible_height))

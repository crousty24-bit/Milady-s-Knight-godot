extends Area2D
signal activated
@export var target_door: NodePath
var active: bool = false
func _ready() -> void:
	add_to_group("mechanism_buttons")
func can_use(player: SlicePlayer) -> bool:
	return not active and player != null and not player.dead and overlaps_body(player)
func activate() -> bool:
	if active: return false
	active = true
	var door := get_node_or_null(target_door) if not target_door.is_empty() else null
	if door != null and door.has_method("open"): door.open()
	activated.emit()
	queue_redraw()
	return true
func _draw() -> void:
	draw_rect(Rect2(-5, -12, 10, 12), Color("4b4655"))
	draw_circle(Vector2(0,-7), 3, Color("77a178") if active else Color("c38364"))

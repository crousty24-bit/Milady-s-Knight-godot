extends Area2D
signal activated
@export var target_door: NodePath
var active: bool = false
func _physics_process(_delta: float) -> void:
	if active: return
	for body in get_overlapping_bodies():
		if body is SlicePlayer and not body.dead and body.global_position.y <= global_position.y + 2.0 and body.velocity.y >= 0.0:
			activate()
			return
func receive_player_attack(_amount: float, source: int) -> bool:
	if active or source != SlicePlayer.DamageSource.PROJECTILE: return false
	return activate()
func activate() -> bool:
	if active: return false
	active = true
	var door := get_node_or_null(target_door) if not target_door.is_empty() else null
	if door != null and door.has_method("open"): door.open()
	activated.emit()
	queue_redraw()
	return true
func _draw() -> void:
	draw_rect(Rect2(-10, -3 if active else -5, 20, 3), Color("77a178") if active else Color("8e8390"))

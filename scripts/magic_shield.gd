extends Area2D
signal collected
var used: bool = false
func _physics_process(_delta: float) -> void:
	if used: return
	for body in get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			collect(body)
			return
func collect(player: SlicePlayer) -> bool:
	if used or player == null or player.dead or not player.activate_magic_shield(): return false
	used = true
	hide()
	set_deferred("monitoring", false)
	collected.emit()
	return true
func _draw() -> void:
	draw_colored_polygon(PackedVector2Array([Vector2(-6,-6), Vector2(6,-6), Vector2(5,3), Vector2(0,7), Vector2(-5,3)]), Color("559ec5"))

extends Area2D
signal collected(amount: float)
var used: bool = false
func _physics_process(_delta: float) -> void:
	if used: return
	for body in get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			var healed: float = body.heal(0.5)
			if healed > 0.0:
				used = true
				hide()
				set_deferred("monitoring", false)
				collected.emit(healed)
				return

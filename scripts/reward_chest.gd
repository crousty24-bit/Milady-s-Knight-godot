extends Area2D
# Attempt-local state only. The level owns payment, acquisition and modal exclusivity.
@export_enum("common", "rare") var kind: String = "common"
var offer: Dictionary = {}
var consumed: bool = false
var paid: bool = false
var save_failed: bool = false

func player_near() -> bool:
	return has_overlapping_bodies()

func _draw() -> void:
	# Functional placeholder pending the Claude art contract.
	var color := Color("ae925f") if kind == "common" else Color("668bbc")
	draw_rect(Rect2(-14, -22, 28, 20), color)
	draw_rect(Rect2(-14, -22, 28, 20), Color("302f3c"), false, 2.0)
	draw_line(Vector2(-14, -14), Vector2(14, -14), Color("302f3c"), 2.0)
	draw_rect(Rect2(-2, -16, 4, 7), Color("dfcd93"))

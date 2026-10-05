extends Area2D
# Attempt-local state only. The level owns payment, acquisition and modal exclusivity.
@export_enum("common", "rare") var kind: String = "common"
var offer: Dictionary = {}
var consumed: bool = false
var paid: bool = false
var save_failed: bool = false

func player_near() -> bool:
	return has_overlapping_bodies()

extends Area2D
# Attempt-local state only. The level owns payment, acquisition and modal exclusivity.
@export_enum("common", "rare") var kind: String = "common"
@export var required_secret: NodePath = NodePath()
var offer: Dictionary = {}
var consumed: bool = false
var paid: bool = false
var save_failed: bool = false

func player_near() -> bool:
	if not required_secret.is_empty():
		var secret := get_node_or_null(required_secret)
		if secret == null or secret.get("passage_open") != true: return false
	return has_overlapping_bodies()

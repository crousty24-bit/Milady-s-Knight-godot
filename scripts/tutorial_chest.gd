extends Area2D
# Fixed free reward. Opening consumes this attempt; durable ownership suppresses future copies.
var consumed: bool = false
var save_failed: bool = false
func player_near() -> bool:
	return has_overlapping_bodies()
func consume() -> void:
	consumed = true
	hide()
func retry_after_failure() -> void:
	consumed = false
	save_failed = true
	show()

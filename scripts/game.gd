extends Node
func _ready() -> void:
	call_deferred("_start")
func _start() -> void:
	var progression = get_node("/root/Progression")
	var error: Error = progression.change_level(progression.resume_scene)
	if error != OK:
		progression.change_level(progression.DEFAULT_LEVEL)

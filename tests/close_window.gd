extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var level=load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene=level
	await create_timer(0.25).timeout
	level.notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)

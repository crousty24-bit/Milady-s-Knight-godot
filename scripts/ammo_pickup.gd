extends Area2D
signal collected(amount: int)

@export_enum("Longbow", "ThrowingKnives") var ammo_family: String = "Longbow"
@export_range(1, 20) var amount: int = 1
var used: bool = false

func _ready() -> void:
	_refresh_art()

func _refresh_art() -> void:
	var arrows := get_node_or_null("Arrows") as CanvasItem
	var knives := get_node_or_null("Knives") as CanvasItem
	if arrows != null: arrows.visible = ammo_family == "Longbow"
	if knives != null: knives.visible = ammo_family == "ThrowingKnives"

func _physics_process(_delta: float) -> void:
	if used: return
	for body in get_overlapping_bodies():
		if not body is SlicePlayer or body.dead or body.resurrection_active: continue
		var taken: int = body.add_ammo(ammo_family, amount)
		if taken <= 0: continue
		amount -= taken
		collected.emit(taken)
		if amount <= 0:
			used = true
			hide()
			set_deferred("monitoring", false)
			queue_free()
		return

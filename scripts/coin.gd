extends Area2D
signal collected(value: int)
@export_enum("Common", "Upper", "Lower") var route: int = 0
var picked_up: bool = false
var elapsed: float = 0.0
func _ready() -> void:
	body_entered.connect(_on_body_entered)
	elapsed = position.x * 0.08
func _process(delta: float) -> void:
	elapsed += delta
	$Sprite.position.y = sin(elapsed * 3.0) * 1.5
func _on_body_entered(body: Node2D) -> void:
	if picked_up or not body is SlicePlayer or body.dead: return
	picked_up = true
	$Shape.set_deferred("disabled", true)
	$Sprite.hide()
	$Sound.play()
	collected.emit(1)
	await $Sound.finished
	queue_free()

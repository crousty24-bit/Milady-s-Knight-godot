extends Area2D
signal collected(value: int)
@export_enum("Common", "Upper", "Lower") var route: int = 0
# A defeat reward is already credited by the level. This reuses the coin art as feedback.
var bonus_feedback: int = 0
var picked_up: bool = false
var elapsed: float = 0.0
func _ready() -> void:
	body_entered.connect(_on_body_entered)
	elapsed = position.x * 0.08
	if bonus_feedback > 0:
		picked_up = true
		monitoring = false
		$Shape.set_deferred("disabled", true)
		$Sound.play()
		var label := Label.new()
		label.text = "+%d BONUS" % bonus_feedback
		label.add_theme_font_override("font", preload("res://assets/fonts/PixelOperator8.ttf"))
		label.add_theme_font_size_override("font_size", 8)
		label.position = Vector2(-20, -18)
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(label)
		var tween := create_tween().set_parallel()
		tween.tween_property(self, "position:y", position.y - 18.0, 0.65)
		tween.tween_property(self, "modulate:a", 0.0, 0.3).set_delay(0.35)
		tween.chain().tween_callback(queue_free)
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

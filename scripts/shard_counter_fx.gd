extends TextureRect
# RUN-016 presentation (Claude): the HUD shard icon pulses when the shard total shown by
# hud.set_bonus changes (gain on kills, spending on acquisitions).
var _last := -1

func _ready() -> void:
	pivot_offset = size * 0.5

func _process(_delta: float) -> void:
	var text: String = get_node("../Bonus").text
	var value := text.get_slice(" ", 1).to_int() if text.contains(" ") else 0
	if _last >= 0 and value != _last:
		var gained := value > _last
		var tween := create_tween()
		modulate = Color(1.6, 1.4, 1.8) if gained else Color(1.0, 0.6, 0.6)
		scale = Vector2(1.34, 1.34)
		tween.tween_property(self, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		tween.parallel().tween_property(self, "modulate", Color.WHITE, 0.3)
	_last = value

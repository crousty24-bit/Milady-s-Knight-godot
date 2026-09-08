extends CanvasLayer
func set_gold(value: int, paid: bool) -> void:
	$Gold.text = "OR %02d   %s" % [value, "SCEAU OUVERT" if paid else "/ 12"]
	$Gold.modulate = Color("f4d384") if value >= 12 or paid else Color("dac38f")
func set_health(value: int) -> void:
	$Health.text = "VIE " + "◆".repeat(value) + "◇".repeat(3-value)
func set_hint(value: String) -> void:
	$Hint.text = value
func set_overlay(title: String, subtitle: String) -> void:
	$Overlay.show()
	$Overlay/Title.text = title
	$Overlay/Subtitle.text = subtitle
func clear_overlay() -> void:
	$Overlay.hide()

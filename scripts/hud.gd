extends CanvasLayer
func set_gold(value: int, paid: bool) -> void:
	$Gold.text = "SCEAU OUVERT" if paid else "SCEAU %02d/12" % value
	$Gold.modulate = Color("f4d384") if value >= 12 or paid else Color("dac38f")
func set_bonus(banked: int, pending: int) -> void:
	$Bonus.text = "BONUS " + _compact(banked + pending)
	$BonusPending.text = "+%s a valider" % _compact(pending) if pending > 0 else "reserve " + _compact(banked)
	$Bonus.tooltip_text = "%d bonus : %d valides, %d dans ce niveau" % [banked + pending, banked, pending]
	$Bonus.mouse_filter = Control.MOUSE_FILTER_STOP
func _compact(value: int) -> String:
	if value < 100000: return str(value)
	if value < 1000000: return "%.1fk" % (value / 1000.0)
	if value < 1000000000: return "%.1fM" % (value / 1000000.0)
	return "%.1fG" % (value / 1000000000.0)
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

extends Node2D
signal opened_signal
@export var coin_locked: bool = true
@export_range(0, 1000, 1) var coin_cost: int = 0
var opened: bool = false
func _ready() -> void:
	add_to_group("secondary_doors")
func can_use(player: SlicePlayer) -> bool:
	return coin_locked and not opened and player != null and not player.dead and $UseArea.overlaps_body(player)
func open() -> bool:
	if opened: return false
	opened = true
	$Barrier/Shape.set_deferred("disabled", true)
	opened_signal.emit()
	queue_redraw()
	return true
func _draw() -> void:
	if not opened:
		draw_rect(Rect2(-8, -48, 16, 48), Color("665455"))
		draw_line(Vector2(-6,-24), Vector2(6,-24), Color("aa8770"), 2)

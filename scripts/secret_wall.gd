extends StaticBody2D
signal revealed
signal save_error(error: int)
@export var secret_id: String = ""
@export var fade_duration: float = 0.4
var opened: bool = false
var save_failed: bool = false
var progression: Node
func _ready() -> void:
	add_to_group("durable_items")
	progression = get_node_or_null("/root/Progression")
	if progression != null and not secret_id.is_empty() and progression.permanent_flags.get("secret:" + secret_id, false):
		_open(false)
func receive_player_attack(_amount: float, source: int) -> bool:
	if opened or source not in [SlicePlayer.DamageSource.CONTACT_MELEE, SlicePlayer.DamageSource.PROJECTILE]: return false
	var error: int = ERR_INVALID_PARAMETER
	if progression != null and not secret_id.is_empty():
		error = progression.set_permanent_flag("secret:" + secret_id)
	if error != OK:
		save_failed = true
		save_error.emit(error)
		return false
	save_failed = false
	_open(true)
	return true
func _open(animate: bool) -> void:
	opened = true
	$Shape.set_deferred("disabled", true)
	if animate:
		revealed.emit()
		create_tween().tween_property(self, "modulate:a", 0.0, maxf(0.0, fade_duration))
	else:
		hide()
func _draw() -> void:
	draw_rect(Rect2(-8, -32, 16, 32), Color("65606e"))
	draw_line(Vector2(-7, -16), Vector2(7, -16), Color("383440"), 1)

extends Area2D
signal collected
signal save_error(error: int)
@export var bonus_id: String = ""
var used: bool = false
var save_failed: bool = false
var progression: Node
func _ready() -> void:
	add_to_group("durable_items")
	progression = get_node_or_null("/root/Progression")
	if progression != null and not bonus_id.is_empty() and progression.has_hp_bonus(bonus_id):
		_consume()
func _physics_process(_delta: float) -> void:
	if used: return
	for body in get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			collect(body)
			return
func collect(player: SlicePlayer) -> bool:
	if used or player == null or player.dead: return false
	var error: int = ERR_INVALID_PARAMETER
	if progression != null and not bonus_id.is_empty():
		# A duplicate cannot increase current health a second time.
		if progression.has_hp_bonus(bonus_id):
			_consume()
			return false
		error = progression.acquire_hp_bonus(bonus_id)
	if error != OK:
		save_failed = true
		save_error.emit(error)
		return false
	save_failed = false
	player.configure_bonus_health(progression.hp_bonus_count(), true)
	_consume()
	collected.emit()
	return true
func _consume() -> void:
	used = true
	hide()
	set_deferred("monitoring", false)
func _draw() -> void:
	draw_circle(Vector2.ZERO, 6, Color("bc4564"))
	draw_line(Vector2(-3, 0), Vector2(3, 0), Color("fff4dc"), 2)
	draw_line(Vector2(0, -3), Vector2(0, 3), Color("fff4dc"), 2)

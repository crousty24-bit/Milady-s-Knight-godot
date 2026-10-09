extends Area2D
signal collected
signal save_error(error: int)
@export var bonus_id: String = ""
@export var required_secret: NodePath = NodePath()
var used: bool = false
var save_failed: bool = false
var progression: Node
func _ready() -> void:
	_build_art()
	add_to_group("durable_items")
	progression = get_node_or_null("/root/Progression")
	if progression != null and not bonus_id.is_empty() and progression.has_hp_bonus(bonus_id):
		_consume()
func _physics_process(_delta: float) -> void:
	if used or not _secret_available(): return
	for body in get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			collect(body)
			return
func collect(player: SlicePlayer) -> bool:
	if used or player == null or player.dead or not _secret_available(): return false
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
func _secret_available() -> bool:
	if required_secret.is_empty(): return true
	var secret := get_node_or_null(required_secret)
	return secret != null and secret.get("passage_open") == true
func _consume() -> void:
	used = true
	hide()
	set_deferred("monitoring", false)
# --- Presentation (RUN-019 Claude art/SFX): feedback only after a successful durable write.
const FLOAT = preload("res://assets/run019/world/item_hp_bonus.png")
const PICKUP = preload("res://assets/run019/world/vfx_hp_bonus_pickup.png")
const PICKUP_SFX = preload("res://assets/sounds/run019/sfx_player_hp_bonus.wav")
func _build_art() -> void:
	Run019Art.sprite(self, OneShotFx.strip_frames(FLOAT, Vector2i(16, 16), 8.0, true), Vector2(8, 8), &"default")
	collected.connect(func() -> void:
		Run019Art.fx(self, PICKUP, Vector2i(32, 32), 14.0, global_position, Vector2(0.5, 0.5), false, PICKUP_SFX, -4.0))

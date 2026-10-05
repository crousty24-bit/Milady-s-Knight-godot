extends StaticBody2D
signal revealed
signal save_error(error: int)
@export var secret_id: String = ""
@export var fade_duration: float = 0.4
var opened: bool = false
var save_failed: bool = false
var progression: Node
func _ready() -> void:
	_build_art()
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
# --- Presentation (RUN-019 Claude art/SFX): looks like the stone wall; the reveal crumbles while
# the existing fade runs. Already-acquired secrets stay hidden without replaying it.
const WALL = preload("res://assets/run019/world/env_secret_wall.png")
const CRUMBLE = preload("res://assets/run019/world/vfx_secret_crumble.png")
const REVEAL_SFX = preload("res://assets/sounds/run019/sfx_secret_reveal.wav")
func _build_art() -> void:
	var art := Sprite2D.new()
	art.texture = WALL
	art.hframes = 2
	art.centered = false
	art.offset = Vector2(-8, -32)
	add_child(art)
	revealed.connect(func() -> void:
		Run019Art.fx(self, CRUMBLE, Vector2i(32, 40), 16.0, global_position, Vector2(0.5, 36.0 / 40.0), false, REVEAL_SFX, -3.0))

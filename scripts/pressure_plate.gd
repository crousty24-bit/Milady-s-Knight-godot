extends Area2D
signal activated
@export var target_door: NodePath
var active: bool = false
func _ready() -> void:
	_build_art()
func _physics_process(_delta: float) -> void:
	if active: return
	for body in get_overlapping_bodies():
		if body is SlicePlayer and not body.dead and body.global_position.y <= global_position.y + 2.0 and body.velocity.y >= 0.0:
			activate()
			return
func receive_player_attack(_amount: float, source: int) -> bool:
	if active or source != SlicePlayer.DamageSource.PROJECTILE: return false
	return activate()
func activate() -> bool:
	if active: return false
	active = true
	var door := get_node_or_null(target_door) if not target_door.is_empty() else null
	if door != null and door.has_method("open"): door.open()
	activated.emit()
	queue_redraw()
	return true
# --- Presentation (RUN-019 Claude art/SFX).
const SHEET = preload("res://assets/run019/world/mech_pressure_plate.png")
const ANIMS = {&"inactive": [0, 1, 1, false], &"press": [1, 3, 20, false], &"active": [4, 1, 1, false]}
const SPARK = preload("res://assets/run019/world/vfx_mech_activate.png")
const ACTIVATE_SFX = preload("res://assets/sounds/run019/sfx_pressure_plate_activate.wav")
func _build_art() -> void:
	var art := Run019Art.sprite(self, Run019Art.frames(SHEET, Vector2i(24, 8), ANIMS), Vector2(12, 8), &"inactive")
	activated.connect(func() -> void:
		Run019Art.chain(art, &"press", &"active")
		Run019Art.fx(self, SPARK, Vector2i(24, 16), 16.0, global_position, Vector2(0.5, 1.0), false, ACTIVATE_SFX, -5.0))

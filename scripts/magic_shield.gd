extends Area2D
signal collected
var used: bool = false
func _ready() -> void:
	_build_art()
func _physics_process(_delta: float) -> void:
	if used: return
	for body in get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			collect(body)
			return
func collect(player: SlicePlayer) -> bool:
	if used or player == null or player.dead or not player.activate_magic_shield(): return false
	used = true
	hide()
	set_deferred("monitoring", false)
	collected.emit()
	return true
# --- Presentation (RUN-019 Claude art/SFX); the aura itself belongs to the player.
const FLOAT = preload("res://assets/run019/world/item_magic_shield.png")
const PICKUP = preload("res://assets/run019/world/vfx_shield_pickup.png")
const ACTIVATE_SFX = preload("res://assets/sounds/run019/sfx_magic_shield_activate.wav")
func _build_art() -> void:
	Run019Art.sprite(self, OneShotFx.strip_frames(FLOAT, Vector2i(16, 16), 8.0, true), Vector2(8, 8), &"default")
	collected.connect(func() -> void:
		Run019Art.fx(self, PICKUP, Vector2i(32, 32), 16.0, global_position, Vector2(0.5, 0.5), false, ACTIVATE_SFX, -4.0))

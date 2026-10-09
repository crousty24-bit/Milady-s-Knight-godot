extends Node2D
signal opened_signal
@export var coin_locked: bool = true
@export_range(0, 1000, 1) var coin_cost: int = 0
var opened: bool = false
func _ready() -> void:
	_build_art()
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
# --- Presentation (RUN-019 Claude art/SFX). Row 0 = coin door, row 1 = mechanism door. The
# barrier is already off when the art starts; payment and E remain owned by the level.
const SHEET = preload("res://assets/run019/world/mech_door.png")
const ANIMS = {&"closed": [0, 1, 1, false], &"unlock": [1, 3, 16, false], &"rise": [4, 6, 16, false], &"opened": [10, 1, 1, false]}
const DUST = preload("res://assets/run019/world/vfx_door_dust.png")
const PAYMENT_SFX = preload("res://assets/sounds/run019/sfx_door_coin_payment.wav")
const UNLOCK_SFX = preload("res://assets/sounds/run019/sfx_door_unlock.wav")
const OPEN_SFX = preload("res://assets/sounds/run019/sfx_door_open.wav")
var _art: AnimatedSprite2D

func _build_art() -> void:
	_art = Run019Art.sprite(self, _door_frames(), Vector2(12, 56), &"closed")
	opened_signal.connect(_on_opened_art)

func _door_frames() -> SpriteFrames:
	return Run019Art.frames(SHEET, Vector2i(24, 56), ANIMS, 0 if coin_locked else 1)

func _on_opened_art() -> void:
	_art.sprite_frames = _door_frames()
	_art.play(&"unlock")
	if coin_locked:
		Run019Art.sound(self, PAYMENT_SFX, global_position + Vector2(0, -24), -5.0)
	Run019Art.sound(self, UNLOCK_SFX, global_position + Vector2(0, -24), -5.0)
	# Every cue starts now: none may begin later, after the level's closing audio sweep.
	Run019Art.sound(self, OPEN_SFX, global_position + Vector2(0, -24), -4.0)
	await _art.animation_finished
	if _art.animation != &"unlock": return
	_art.play(&"rise")
	Run019Art.fx(self, DUST, Vector2i(32, 12), 14.0, global_position, Vector2(0.5, 1.0))
	await _art.animation_finished
	if _art.animation == &"rise": _art.play(&"opened")

extends Node2D
# RUN-016 presentation (Claude) for scenes/tutorial_chest.tscn: closed chest sprite. When the attempt
# consumes the chest (the script hides it as the reward window opens), an opened copy plays in the
# world while the window is up, then dissolves; a failed save shows the closed chest again.
const CHEST = preload("res://assets/sprites/item_chest.png")
const VANISH = preload("res://assets/sprites/vfx_chest_vanish.png")
const OPEN_SFX = preload("res://assets/sounds/sfx_chest_open_common.wav")
const REVEAL_SFX = preload("res://assets/sounds/sfx_chest_reward_reveal.wav")
const ACCEPT_SFX = preload("res://assets/sounds/sfx_chest_reward_accept.wav")
const FOOT_Y = 0.0  # the chest origin sits on the ground line
var chest: Area2D
var _armed: bool = false  # consume() during level setup (Longbow already owned) stays silent

func _ready() -> void:
	chest = get_parent()
	var sprite := Sprite2D.new()
	sprite.texture = CHEST
	sprite.region_enabled = true
	sprite.region_rect = Rect2(0, 0, 24, 20)
	sprite.centered = false
	sprite.offset = Vector2(-12, FOOT_Y - 20)
	add_child(sprite)
	chest.visibility_changed.connect(_on_chest_visibility)
	set_deferred("_armed", true)

func _on_chest_visibility() -> void:
	if not _armed or chest.visible or not chest.consumed or not is_inside_tree(): return
	var opened := Node2D.new()
	opened.set_script(preload("res://scripts/chest_opened_fx.gd"))
	opened.setup(chest, CHEST, VANISH, [OPEN_SFX, REVEAL_SFX, ACCEPT_SFX], FOOT_Y)
	chest.get_parent().add_child(opened)
	opened.global_position = chest.global_position

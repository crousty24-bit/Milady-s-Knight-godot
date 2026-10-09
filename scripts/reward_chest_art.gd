extends Node2D
# RUN-018 presentation (Claude) for scenes/reward_chest.tscn: closed common/rare chest. When the
# level hides the paid chest as its reward window opens, an opened snapshot plays in the world,
# then dissolves once the window closes. Payment, offer and acquisition stay with the level.
const STRIPS := {
	"common": [preload("res://assets/run018/world/item_chest_common.png"), Vector2i(24, 20), preload("res://assets/sprites/vfx_chest_vanish.png"), Vector2i(32, 24), preload("res://assets/sounds/sfx_chest_open_common.wav")],
	"rare": [preload("res://assets/run018/world/item_chest_rare.png"), Vector2i(32, 24), preload("res://assets/run018/world/vfx_chest_vanish_rare.png"), Vector2i(40, 28), preload("res://assets/sounds/run018/sfx_chest_open_rare.wav")],
}
const OPENED_FX = preload("res://scripts/reward_chest_opened_fx.gd")
var chest: Area2D
var _sprite: Sprite2D

func _ready() -> void:
	chest = get_parent()
	_sprite = Sprite2D.new()
	_sprite.centered = false
	_sprite.region_enabled = true
	add_child(_sprite)
	_apply_kind()
	chest.visibility_changed.connect(_on_chest_visibility)

func _apply_kind() -> void:
	var art: Array = STRIPS.get(chest.kind, STRIPS.common)
	var size: Vector2i = art[1]
	_sprite.texture = art[0]
	_sprite.region_rect = Rect2(0, 0, size.x, size.y)
	_sprite.offset = Vector2(-size.x / 2.0, -size.y)

func _on_chest_visibility() -> void:
	if chest.visible or not chest.paid or not is_inside_tree(): return
	var art: Array = STRIPS.get(chest.kind, STRIPS.common)
	var opened := Node2D.new()
	opened.set_script(OPENED_FX)
	opened.setup(chest, art)
	chest.get_parent().add_child(opened)
	opened.global_position = chest.global_position

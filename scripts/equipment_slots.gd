extends Control
# RUN-016 presentation (Claude): two vertical slot plates (melee / ranged) around the functional
# labels written by hud.set_equipment ("> " marks the active slot). Icons and focus follow the text.
const ICONS = preload("res://assets/sprites/ui_slot_icons.png")
const PLATE = preload("res://assets/sprites/ui_plate.png")
const FOCUS = preload("res://assets/sprites/ui_menu_focus.png")
const ACTIVE_TEXT = Color(0.941, 0.824, 0.478)
const IDLE_TEXT = Color(0.867, 0.886, 0.91)
const EMPTY_TEXT = Color(0.384, 0.365, 0.404)
var _seen := ["", ""]

func _process(_delta: float) -> void:
	_refresh(0, $Melee, $MeleePlate, $MeleeIcon)
	_refresh(1, $Ranged, $RangedPlate, $RangedIcon)

func _refresh(slot: int, label: Label, plate: NinePatchRect, icon: TextureRect) -> void:
	if label.text == _seen[slot]: return
	_seen[slot] = label.text
	var active := label.text.begins_with(">")
	var empty := label.text.strip_edges().ends_with("Empty")
	plate.texture = FOCUS if active else PLATE
	plate.modulate.a = 1.0 if active else 0.85
	(icon.texture as AtlasTexture).region = Rect2((2 if empty else slot) * 12, 0, 12, 12)
	label.add_theme_color_override("font_color", EMPTY_TEXT if empty else (ACTIVE_TEXT if active else IDLE_TEXT))

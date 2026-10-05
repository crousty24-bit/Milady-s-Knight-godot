extends Control
# RUN-016 presentation (Claude): two vertical slot plates (melee / ranged) around the functional
# labels written by hud.set_loadout ("> " marks the active slot). Icons and focus follow the text.
# RUN-018: one icon per standard weapon and a level badge (digit always shown, tier colour 0-3);
# plates widen together so the longest exact label (e.g. "Throwing Knives 3") fits at 640x360.
const ICONS = preload("res://assets/run018/ui/ui_weapon_icons.png")
const BADGES = preload("res://assets/run018/ui/ui_tier_badges.png")
const PLATE = preload("res://assets/sprites/ui_plate.png")
const FOCUS = preload("res://assets/sprites/ui_menu_focus.png")
const ACTIVE_TEXT = Color(0.941, 0.824, 0.478)
const IDLE_TEXT = Color(0.867, 0.886, 0.91)
const EMPTY_TEXT = Color(0.384, 0.365, 0.404)
const ORDER := ["Sword", "Longsword", "BrutalAxe", "DarkScythe", "Warhammer", "Halberds", "Longbow", "ThrowingKnives"]
const EMPTY_ICON := 8
const MIN_WIDTH := 92.0
const TEXT_LEFT := 17.0
var _seen := ["", ""]
var _items := ["", ""]
var _badges: Array[TextureRect] = []

func _ready() -> void:
	for slot in 2:
		var badge := TextureRect.new()
		badge.name = "MeleeBadge" if slot == 0 else "RangedBadge"
		badge.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var atlas := AtlasTexture.new()
		atlas.atlas = BADGES
		atlas.region = Rect2(0, 0, 9, 9)
		badge.texture = atlas
		badge.size = Vector2(9, 9)
		badge.position = Vector2(MIN_WIDTH - 12.0, 3.0 + slot * 17.0)
		badge.hide()
		add_child(badge)
		_badges.append(badge)
	for icon: TextureRect in [$MeleeIcon, $RangedIcon]:
		var atlas := AtlasTexture.new()
		atlas.atlas = ICONS
		atlas.region = Rect2(0, 0, 12, 12)
		icon.texture = atlas

# Called by hud.set_loadout with the exact item IDs behind the two labels.
func set_items(melee: String, ranged: String) -> void:
	_items = [melee, ranged]
	_seen = ["", ""]

func _process(_delta: float) -> void:
	var changed := false
	changed = _refresh(0, $Melee, $MeleePlate, $MeleeIcon) or changed
	changed = _refresh(1, $Ranged, $RangedPlate, $RangedIcon) or changed
	if changed: _layout()

func _refresh(slot: int, label: Label, plate: NinePatchRect, icon: TextureRect) -> bool:
	var key: String = label.text + "|" + str(_items[slot])
	if key == _seen[slot]: return false
	_seen[slot] = key
	var active := label.text.begins_with(">")
	var empty := label.text.strip_edges().ends_with("Empty")
	plate.texture = FOCUS if active else PLATE
	plate.modulate.a = 1.0 if active else 0.85
	var stats := {} if empty else WeaponCatalog.stats(_items[slot])
	var index: int = EMPTY_ICON
	if not stats.is_empty(): index = ORDER.find(str(_items[slot]).left(-1))
	elif not empty: index = slot * 6  # labels set without IDs (legacy calls): Sword / Longbow
	(icon.texture as AtlasTexture).region = Rect2(maxi(0, index) * 12, 0, 12, 12)
	var badge := _badges[slot]
	badge.visible = not stats.is_empty()
	if badge.visible: (badge.texture as AtlasTexture).region = Rect2(int(stats.level) * 9, 0, 9, 9)
	label.add_theme_color_override("font_color", EMPTY_TEXT if empty else (ACTIVE_TEXT if active else IDLE_TEXT))
	return true

func _layout() -> void:
	var width := MIN_WIDTH
	var labels: Array[Label] = [$Melee, $Ranged]
	for label in labels:
		var font := label.get_theme_font("font")
		var text_width := font.get_string_size(label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, label.get_theme_font_size("font_size")).x
		width = maxf(width, ceilf(TEXT_LEFT + text_width + 3.0 + 9.0 + 4.0))
	for slot in 2:
		var plate: NinePatchRect = [$MeleePlate, $RangedPlate][slot]
		plate.size.x = width
		labels[slot].size.x = width - TEXT_LEFT - 14.0
		_badges[slot].position.x = width - 12.0
	size.x = maxf(size.x, width)

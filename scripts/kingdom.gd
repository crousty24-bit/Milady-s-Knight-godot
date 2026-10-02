@tool
# Hand-placed scenery of the slice, drawn from generated props (tools/art/world.py).
# Pure drawing, no gameplay state; positions are those of the authored layout.
extends Node2D
const FONT = preload("res://assets/fonts/PixelOperator8.ttf")
const TILES = preload("res://assets/sprites/terrain_stone.png")
const HOUSE = preload("res://assets/sprites/prop_house.png")
const HOUSE_RUINED = preload("res://assets/sprites/prop_house_ruined.png")
const TREES = [preload("res://assets/sprites/prop_tree_a.png"), preload("res://assets/sprites/prop_tree_b.png")]
const DEAD_TREES = [preload("res://assets/sprites/prop_tree_dead_a.png"), preload("res://assets/sprites/prop_tree_dead_b.png")]
const CART = preload("res://assets/sprites/prop_cart.png")
const SIGNPOST = preload("res://assets/sprites/prop_signpost.png")
const BANNER = preload("res://assets/sprites/prop_banner.png")
const BLIGHT = [preload("res://assets/sprites/prop_blight_a.png"), preload("res://assets/sprites/prop_blight_b.png"), preload("res://assets/sprites/prop_blight_c.png")]
const FAR_TOWERS = [preload("res://assets/sprites/prop_far_tower_a.png"), preload("res://assets/sprites/prop_far_tower_b.png")]
const RIBBON_SPEAR = preload("res://assets/sprites/prop_ribbon_spear.png")

# Draw a prop with its bottom-centre (or given anchor) at a world point.
func prop(texture: Texture2D, foot: Vector2, anchor_x: float = -1.0) -> void:
	var ax: float = texture.get_width() * 0.5 if anchor_x < 0.0 else anchor_x
	draw_texture(texture, (foot - Vector2(ax, texture.get_height())).round())

func _draw() -> void:
	# Distant fortification, growing closer toward the exit.
	for x in range(1590, 2280, 72):
		prop(FAR_TOWERS[(x / 72) % 2], Vector2(x - 4, 184), 0.0)
	draw_rect(Rect2(1570, 150, 740, 64), Color("161b25"))
	for i in range(24):
		var x: int = i * 99 + 22
		if i > 12: prop(DEAD_TREES[i % 2], Vector2(x + 2, 144))
		else: prop(TREES[i % 2], Vector2(x + 2, 146))
	prop(HOUSE, Vector2(70, 144))
	prop(HOUSE_RUINED, Vector2(246, 144))
	# Cart and its spilled cargo.
	prop(CART, Vector2(427, 144))
	# Two-path sign. Visible before committing to either route.
	prop(SIGNPOST, Vector2(482, 144))
	draw_string(FONT, Vector2(466, 113), "12 OR >", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("e2c989"))
	# Bridge pillars distinguish the high route from the lower road.
	for x in [706, 780, 986, 1050, 1130, 1210]:
		draw_rect(Rect2(x, 88, 9, 136), Color("39363f"))
		draw_rect(Rect2(x, 88, 1, 136), Color("625d67"))
		draw_rect(Rect2(x + 8, 88, 1, 136), Color("2a2830"))
		for yy in range(92, 224, 12): draw_rect(Rect2(x + 1, yy, 7, 1), Color("1c1a21"))
	# Torn royal standard: second environmental clue.
	prop(BANNER, Vector2(1049, 46), 2.0)
	# Corruption is sparse at first, dense close to the sealed wall.
	for i in range(22):
		prop(BLIGHT[(i * 13) % 3], Vector2(1390 + i * 37, 145))
	# Final wall and columns frame the actual gate, which draws in front.
	for x in range(1968, 2232, 16):
		if x > 2040 and x < 2104: continue
		for y in range(16, 144, 16):
			var mask: int = 1 if y == 16 else 0
			var shade: float = 0.82 - minf(0.2, (y - 16) / 640.0)
			draw_texture_rect_region(TILES, Rect2(x, y, 16, 16), Rect2(mask * 16, (3 + posmod(x / 16 + y / 16, 3)) * 16, 16, 16), Color(shade, shade, shade))
	for x in range(1968, 2240, 24):
		if x > 2040 and x < 2104: continue
		draw_texture_rect_region(TILES, Rect2(x, 6, 12, 10), Rect2(16 * 15, 48, 12, 10), Color(0.82, 0.82, 0.82))
	# Princess's ribbon caught on a spear; no dialogue system needed.
	prop(RIBBON_SPEAR, Vector2(1893, 144), 6.0)

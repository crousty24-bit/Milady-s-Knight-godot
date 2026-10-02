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
const PILLARS = [preload("res://assets/sprites/prop_pillar_a.png"), preload("res://assets/sprites/prop_pillar_b.png")]
const LAMP = preload("res://assets/sprites/prop_lantern_post.png")
const BRAZIER = preload("res://assets/sprites/prop_brazier.png")
const SCONCE = preload("res://assets/sprites/prop_sconce.png")
const CHAIN_LANTERN = preload("res://assets/sprites/prop_chain_lantern.png")
const FLAME = preload("res://assets/sprites/prop_flame.png")
const GLOW = preload("res://assets/sprites/prop_glow.png")
const GRAVES = [preload("res://assets/sprites/prop_grave_a.png"), preload("res://assets/sprites/prop_grave_b.png"), preload("res://assets/sprites/prop_grave_c.png")]
const FENCE = preload("res://assets/sprites/prop_fence.png")
const BUSH = preload("res://assets/sprites/prop_bush.png")
const BUSH_CORRUPT = preload("res://assets/sprites/prop_bush_corrupt.png")
const RUBBLE = preload("res://assets/sprites/prop_rubble.png")
const BONES = preload("res://assets/sprites/prop_bones.png")
const RUIN_WALL = preload("res://assets/sprites/prop_ruin_wall.png")
const SHRINE = preload("res://assets/sprites/prop_shrine.png")
const GALLOWS = preload("res://assets/sprites/prop_gallows.png")
const CROW = preload("res://assets/sprites/prop_crow.png")
const BANNER_HANG = preload("res://assets/sprites/prop_banner_hang.png")
const ROOTS = preload("res://assets/sprites/prop_roots.png")
const POD = preload("res://assets/sprites/prop_pod.png")

# Slow flicker of lanterns and braziers: redraw about ten times per second.
var _time := 0.0
var _since_draw := 0.0
func _process(delta: float) -> void:
	_time += delta
	_since_draw += delta
	if _since_draw >= 0.1:
		_since_draw = 0.0
		queue_redraw()

# Warm accent: animated flame (3 frames) over a dithered, low-alpha glow.
func light(point: Vector2, flame: bool, phase: float, strength: float = 1.0) -> void:
	var flicker := 0.78 + 0.22 * sin(_time * 7.0 + phase) * sin(_time * 3.1 + phase * 2.0)
	draw_texture(GLOW, (point - Vector2(32, 32)).round(), Color(1, 1, 1, clampf(flicker * strength, 0.0, 1.0)))
	if flame:
		var frame := posmod(int(_time * 9.0 + phase * 3.0), 3)
		draw_texture_rect_region(FLAME, Rect2((point + Vector2(-5, -12)).round(), Vector2(10, 14)), Rect2(frame * 10, 0, 10, 14))

# Draw a prop with its bottom-centre (or given anchor) at a world point.
func prop(texture: Texture2D, foot: Vector2, anchor_x: float = -1.0, flip: bool = false, tint: Color = Color.WHITE) -> void:
	var ax: float = texture.get_width() * 0.5 if anchor_x < 0.0 else anchor_x
	var origin := (foot - Vector2(ax, texture.get_height())).round()
	if flip:
		# A negative width mirrors the prop: cheap variety for repeated trees.
		draw_texture_rect(texture, Rect2(origin + Vector2(texture.get_width(), 0), Vector2(-texture.get_width(), texture.get_height())), false, tint)
	else:
		draw_texture(texture, origin, tint)

func _draw() -> void:
	# Distant fortification, growing closer toward the exit.
	for x in range(1590, 2280, 72):
		prop(FAR_TOWERS[(x / 72) % 2], Vector2(x - 4, 184), 0.0)
	draw_rect(Rect2(1570, 150, 740, 64), Color("161b25"))
	_scenery_back()
	for i in range(24):
		var x: int = i * 99 + 22
		if i > 12: prop(DEAD_TREES[i % 2], Vector2(x + 2, 144), -1.0, i % 4 >= 2)
		else: prop(TREES[i % 2], Vector2(x + 2, 146), -1.0, i % 3 == 1)
	prop(HOUSE, Vector2(70, 144))
	prop(HOUSE_RUINED, Vector2(246, 144))
	# Cart and its spilled cargo.
	prop(CART, Vector2(427, 144))
	# Two-path sign. Visible before committing to either route.
	prop(SIGNPOST, Vector2(482, 144))
	draw_string(FONT, Vector2(466, 113), "12 OR >", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("e2c989"))
	# Bridge pillars distinguish the high route from the lower road.
	var pillar_index := 0
	for x in [706, 780, 986, 1050, 1130, 1210]:
		prop(PILLARS[1 if pillar_index == 2 or pillar_index == 5 else 0], Vector2(x + 5, 224), -1.0, false, Color(0.88, 0.9, 0.95))
		pillar_index += 1
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
			draw_texture_rect_region(TILES, Rect2(x, y, 16, 16), Rect2(mask * 16, _wall_row(x, y) * 16, 16, 16), Color(shade, shade, shade))
	for x in range(1968, 2240, 24):
		if x > 2040 and x < 2104: continue
		draw_texture_rect_region(TILES, Rect2(x, 6, 12, 10), Rect2(16 * 15, _wall_row(x, 16) * 16, 12, 10), Color(0.82, 0.82, 0.82))
	# Two torn standards and two sconces on the sealed wall.
	prop(BANNER_HANG, Vector2(1996, 30), 10.0, false, Color(0.9, 0.9, 0.9))
	prop(BANNER_HANG, Vector2(2200, 30), 10.0, false, Color(0.9, 0.9, 0.9))
	for sx in [2018, 2126]:
		prop(SCONCE, Vector2(sx, 102))
		light(Vector2(sx, 92), true, float(sx))
	_scenery_front()
	# Princess's ribbon caught on a spear; no dialogue system needed.
	prop(RIBBON_SPEAR, Vector2(1893, 144), 6.0)

func _wall_row(x: int, y: int) -> int:
	return 18 + posmod(y / 16, 3) * 6 + posmod(x / 16, 6)

# Decor behind the ground line, before narrative props (trees are drawn by the caller).
func _scenery_back() -> void:
	prop(RUIN_WALL, Vector2(354, 144), -1.0, false, Color(0.9, 0.9, 0.95))
	prop(RUIN_WALL, Vector2(830, 224), -1.0, true, Color(0.85, 0.88, 0.95))

# Ground-level decor, drawn over the narrative props but behind the terrain skin and gameplay.
func _scenery_front() -> void:
	# Village.
	prop(LAMP, Vector2(204, 144)); light(Vector2(204 + 5, 144 - 38), false, 1.0, 0.6)
	prop(GRAVES[0], Vector2(140, 144)); prop(GRAVES[1], Vector2(158, 144)); prop(GRAVES[2], Vector2(172, 144), -1.0, true)
	prop(CROW, Vector2(161, 124))
	prop(BUSH, Vector2(304, 144)); prop(RUBBLE, Vector2(292, 144)); prop(BONES, Vector2(396, 144))
	prop(FENCE, Vector2(522, 160)); prop(BUSH, Vector2(572, 192), -1.0, true)
	# Lower road.
	prop(GRAVES[2], Vector2(640, 224)); prop(BONES, Vector2(660, 224), -1.0, true)
	prop(LAMP, Vector2(745, 224)); light(Vector2(745 + 5, 224 - 38), false, 2.0, 0.6)
	prop(GRAVES[0], Vector2(765, 224), -1.0, true)
	prop(SHRINE, Vector2(934, 224)); light(Vector2(934, 224 - 25), false, 3.0, 0.6)
	prop(BUSH, Vector2(984, 224)); prop(RUBBLE, Vector2(1160, 224)); prop(BONES, Vector2(1186, 224))
	prop(BRAZIER, Vector2(1255, 224)); light(Vector2(1255, 224 - 15), true, 4.0)
	for x in [640, 744]:
		prop(CHAIN_LANTERN, Vector2(x, 64), 4.0)
		light(Vector2(x, 64 + 30), false, float(x), 0.4)
	prop(CHAIN_LANTERN, Vector2(1016, 64), 4.0); light(Vector2(1016, 64 + 30), false, 7.0, 0.4)
	# Corrupted approach.
	prop(BUSH_CORRUPT, Vector2(1424, 144)); prop(ROOTS, Vector2(1500, 144))
	prop(GALLOWS, Vector2(1596, 144)); prop(CROW, Vector2(1604, 144 - 68))
	prop(POD, Vector2(1702, 144)); prop(BONES, Vector2(1724, 144), -1.0, true); prop(POD, Vector2(1764, 144), -1.0, true)
	prop(GRAVES[1], Vector2(1850, 144), -1.0, false, Color(0.82, 0.86, 1.0)); prop(GRAVES[2], Vector2(1866, 144), -1.0, false, Color(0.82, 0.86, 1.0))
	prop(ROOTS, Vector2(1962, 144), -1.0, true)

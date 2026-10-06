@tool
# Skins the authored Terrain (TileMapLayer) of N2-N4 with generated tiles (RUN-020).
# Sibling of Terrain; collision and layout stay in Terrain, this node only draws.
# Atlas layout as terrain_stone.png: column = exposure mask, row = theme * 18 + seed * 6 + phase.
#   N2 Blight Town: terrain_campaign.png theme 0 (masonry, rot moss).
#   N3 Black Forest: run021/terrain_black_forest.png (RUN-020 earth with the soil ramp lifted
#   one step for readability against the forest backdrop, RUN-021).
#   N4 Forbidden Graveyard: terrain_stone.png theme 0, unchanged, so the RUN-019 secret wall matches.
extends Node2D
const STONE = preload("res://assets/sprites/terrain_stone.png")
const CAMPAIGN = preload("res://assets/run020/terrain_campaign.png")
const FOREST = preload("res://assets/run021/terrain_black_forest.png")
const TUFTS = preload("res://assets/run020/tufts_campaign.png")
const VINES = preload("res://assets/run020/vines_campaign.png")
const DEPTH_SHADE = [1.0, 0.86, 0.74, 0.64, 0.56, 0.5]
@export_range(2, 4) var world_level: int = 2:
	set(value):
		world_level = value
		queue_redraw()
var terrain: TileMapLayer
func _ready() -> void:
	terrain = get_parent().get_node_or_null("Terrain")
	if terrain != null:
		terrain.changed.connect(queue_redraw)
	queue_redraw()
func _hash(cell: Vector2i, salt: int) -> int:
	return posmod(cell.x * 73 + cell.y * 151 + salt * 31 + cell.x * cell.y * 7, 1009)
# Depth below the exposed top, relaxed by one step per cell along each row so the ground
# under a raised step darkens as a soft gradient instead of a hard-edged dark column.
func _depths(used: Dictionary) -> Dictionary:
	var depth := {}
	var rows := {}
	for cell: Vector2i in used:
		var d := 0
		while d < 5 and used.has(cell - Vector2i(0, d + 1)): d += 1
		depth[cell] = d
		if not rows.has(cell.y): rows[cell.y] = []
		rows[cell.y].append(cell.x)
	for y: int in rows:
		var xs: Array = rows[y]
		xs.sort()
		for i in range(1, xs.size()):
			if xs[i] == xs[i - 1] + 1:
				depth[Vector2i(xs[i], y)] = mini(depth[Vector2i(xs[i], y)], depth[Vector2i(xs[i - 1], y)] + 1)
		for i in range(xs.size() - 2, -1, -1):
			if xs[i + 1] == xs[i] + 1:
				depth[Vector2i(xs[i], y)] = mini(depth[Vector2i(xs[i], y)], depth[Vector2i(xs[i + 1], y)] + 1)
	return depth
func _draw() -> void:
	if not is_instance_valid(terrain): return
	var atlas: Texture2D = [CAMPAIGN, FOREST, STONE][clampi(world_level, 2, 4) - 2]
	var theme := 0
	var biome := world_level - 2
	var used := {}
	for cell in terrain.get_used_cells(): used[cell] = true
	var depths := _depths(used)
	var surfaces: Array[Vector2i] = []
	var overhangs: Array[Vector2i] = []
	for cell: Vector2i in used:
		var p := terrain.position + Vector2(cell * 16)
		# Exposure mask: 1 open above, 2 right, 4 below, 8 left.
		var mask := 0
		if not used.has(cell + Vector2i.UP): mask |= 1
		if not used.has(cell + Vector2i.RIGHT): mask |= 2
		if not used.has(cell + Vector2i.DOWN): mask |= 4
		if not used.has(cell + Vector2i.LEFT): mask |= 8
		var row := theme * 18 + posmod(cell.y, 3) * 6 + posmod(cell.x, 6)
		var shade: float = DEPTH_SHADE[depths[cell]]
		draw_texture_rect_region(atlas, Rect2(p, Vector2(16, 16)), Rect2(mask * 16, row * 16, 16, 16), Color(shade, shade, shade))
		if mask & 1: surfaces.append(cell)
		if mask & 4 and cell.y < 18: overhangs.append(cell)
	for cell in surfaces:
		var p := terrain.position + Vector2(cell * 16)
		draw_texture_rect_region(TUFTS, Rect2(p + Vector2(0, -11), Vector2(16, 12)), Rect2((_hash(cell, 1) % 8) * 16, biome * 12, 16, 12))
	# Strands, roots or rot hang from some undersides (decor only, low contrast).
	for cell in overhangs:
		if _hash(cell, 2) % 100 >= 55: continue
		var p := terrain.position + Vector2(cell * 16)
		draw_texture_rect_region(VINES, Rect2(p + Vector2(0, 15), Vector2(16, 24)), Rect2((_hash(cell, 3) % 8) * 16, biome * 24, 16, 24), Color(0.8, 0.8, 0.8))

# Secret wall cover (RUN-021 Claude art): redraws the N4 stone masonry over `rect` as if the
# hidden cavity were solid rock, so the cache, its rewards and their effects read as plain wall.
# Presentation only: no collision, save, gameplay or sound. The parent wall owns the reveal and
# fades this node through its own modulate:a.
# Rendering mirrors the N4 path of campaign_terrain_skin.gd (terrain_stone.png theme 0, same
# exposure columns, world-grid phases, DEPTH_SHADE, tufts and vines) on the real cells plus the
# rectangle filled as fake solid cells, so the cover meets the surrounding skin without a seam
# and hides the cavity lips (ceiling underside, floor top, inner faces) that would betray it.
class_name SecretWallMask
extends Node2D
const STONE = preload("res://assets/sprites/terrain_stone.png")
const TUFTS = preload("res://assets/run020/tufts_campaign.png")
const VINES = preload("res://assets/run020/vines_campaign.png")
const DEPTH_SHADE = [1.0, 0.86, 0.74, 0.64, 0.56, 0.5]
const CELL := 16
# N4 strip row in tufts/vines, theme row block in terrain_stone.png.
const BIOME := 2
const THEME := 0
# World layer above reward art (z 0), the player (1) and pickup/crumble effects (5), below
# floating feedback text (60); the HUD is a CanvasLayer and always stays on top.
const MASK_Z := 50
var terrain: TileMapLayer
# Covered area in this node's coordinates (the wall's own, the mask sits at its origin).
var rect := Rect2()
func _init() -> void:
	z_as_relative = false
	z_index = MASK_Z
func configure(p_terrain: TileMapLayer, p_rect: Rect2) -> void:
	terrain = p_terrain
	rect = p_rect
	queue_redraw()
func _draw() -> void:
	if not is_instance_valid(terrain) or not rect.has_area(): return
	# Draw in Terrain coordinates so atlas phases follow the world grid like the skin.
	var to_self := get_global_transform().affine_inverse() * terrain.get_global_transform()
	var area := to_self.affine_inverse() * rect
	var first := Vector2i((area.position / CELL).floor())
	var last := Vector2i((area.end / CELL).ceil()) - Vector2i.ONE
	var real := {}
	for cell in terrain.get_used_cells(): real[cell] = true
	var used := real.duplicate()
	for y in range(first.y, last.y + 1):
		for x in range(first.x, last.x + 1):
			used[Vector2i(x, y)] = true
	var depths := _depths(used)
	draw_set_transform_matrix(to_self)
	for y in range(first.y, last.y + 1):
		for x in range(first.x, last.x + 1):
			var cell := Vector2i(x, y)
			var shade: float = DEPTH_SHADE[depths[cell]]
			var tint := Color(shade, shade, shade)
			var row := THEME * 18 + posmod(cell.y, 3) * 6 + posmod(cell.x, 6)
			var dest := Rect2(Vector2(cell * CELL), Vector2(CELL, CELL))
			var mask := _exposure(used, cell)
			# The skin still draws the real tile underneath: where its exposure differs, lay that
			# tile first at the cover's shade so its edge pixels cannot show through ours.
			if real.has(cell):
				var real_mask := _exposure(real, cell)
				if real_mask != mask:
					_clipped(STONE, dest, Rect2(real_mask * CELL, row * CELL, CELL, CELL), area, tint)
			_clipped(STONE, dest, Rect2(mask * CELL, row * CELL, CELL, CELL), area, tint)
	# Decorations of every cell that reaches into the area, decided on the filled layout and
	# clipped to it: the parts inside match the skin, cavity tufts and strands disappear.
	for y in range(first.y - 3, last.y + 2):
		for x in range(first.x, last.x + 1):
			var cell := Vector2i(x, y)
			if not used.has(cell) or used.has(cell + Vector2i.UP): continue
			var p := Vector2(cell * CELL)
			_clipped(TUFTS, Rect2(p + Vector2(0, -11), Vector2(16, 12)), Rect2((_hash(cell, 1) % 8) * 16, BIOME * 12, 16, 12), area)
	for y in range(first.y - 3, last.y + 2):
		for x in range(first.x, last.x + 1):
			var cell := Vector2i(x, y)
			if not used.has(cell) or used.has(cell + Vector2i.DOWN) or cell.y >= 18: continue
			if _hash(cell, 2) % 100 >= 55: continue
			var p := Vector2(cell * CELL)
			_clipped(VINES, Rect2(p + Vector2(0, 15), Vector2(16, 24)), Rect2((_hash(cell, 3) % 8) * 16, BIOME * 24, 16, 24), area, Color(0.8, 0.8, 0.8))
# Draws the part of `dest` inside `area` (1:1 texel scale, so pixels stay on the grid).
func _clipped(tex: Texture2D, dest: Rect2, src: Rect2, area: Rect2, tint := Color.WHITE) -> void:
	var cut := dest.intersection(area)
	if not cut.has_area(): return
	draw_texture_rect_region(tex, cut, Rect2(src.position + cut.position - dest.position, cut.size), tint)
# Exposure mask: 1 open above, 2 right, 4 below, 8 left (atlas column).
func _exposure(cells: Dictionary, cell: Vector2i) -> int:
	var mask := 0
	if not cells.has(cell + Vector2i.UP): mask |= 1
	if not cells.has(cell + Vector2i.RIGHT): mask |= 2
	if not cells.has(cell + Vector2i.DOWN): mask |= 4
	if not cells.has(cell + Vector2i.LEFT): mask |= 8
	return mask
# Same hash and depth relaxation as campaign_terrain_skin.gd, kept local so the cover follows
# the N4 skin without touching that file.
func _hash(cell: Vector2i, salt: int) -> int:
	return posmod(cell.x * 73 + cell.y * 151 + salt * 31 + cell.x * cell.y * 7, 1009)
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

@tool
# Skins the authored Terrain (TileMapLayer) of N2-N4 with generated tiles (RUN-020).
# Sibling of Terrain; collision and layout stay in Terrain, this node only draws.
# Atlas layout as terrain_stone.png: column = exposure mask, row = theme * 18 + seed * 6 + phase.
#   N2 Blight Town: run021/n2/terrain_blight_town.png (RUN-021 N2 pass): street masonry near
#   the surface, then below the street line a foundation course sinking into rot earth drawn
#   from a seamless world-space texture, plus rare decals (cellar grates, sewer mouths, bones).
#   N3 Black Forest: run021/terrain_black_forest.png (RUN-020 earth with the soil ramp lifted
#   one step for readability against the forest backdrop, RUN-021).
#   N4 Forbidden Graveyard: terrain_stone.png theme 0, unchanged, so the RUN-019 secret wall matches.
extends Node2D
const STONE = preload("res://assets/sprites/terrain_stone.png")
const CAMPAIGN = preload("res://assets/run020/terrain_campaign.png")
const FOREST = preload("res://assets/run021/terrain_black_forest.png")
const TUFTS = preload("res://assets/run020/tufts_campaign.png")
const VINES = preload("res://assets/run020/vines_campaign.png")
const N2_TILES = preload("res://assets/run021/n2/terrain_blight_town.png")
const N2_EARTH = preload("res://assets/run021/n2/n2_earth.png")
const N2_DECALS = preload("res://assets/run021/n2/n2_terrain_decals.png")
const GLOW = preload("res://assets/sprites/prop_glow.png")
const N2_BACK = preload("res://assets/run021/n2/n2_backwall.png")
# Enclosed spaces narrower than this (in cells) count as closed when finding the open sky,
# so a 2-3 cell shaft or hole leads into the underground instead of letting the sky in.
const CELLAR_ARCH = preload("res://assets/run021/n2/props/cellar_arch.png")
const CELLAR_NICHE = preload("res://assets/run021/n2/props/cellar_niche.png")
const HANG_CAGE = preload("res://assets/run021/n2/props/hang_cage.png")
const N2_GLOW = preload("res://assets/run021/n2/n2_glow.png")
const N2_CLOSING = 2
const N2_BELOW_ROWS = 22
# N2: earth only under the street line (cell row 10, y 160) so raised blocks stay masonry.
const N2_GROUND_ROW = 10
const DEPTH_SHADE = [1.0, 0.86, 0.74, 0.64, 0.56, 0.5]
@export_range(2, 4) var world_level: int = 2:
	set(value):
		world_level = value
		queue_redraw()
var terrain: TileMapLayer
# N2 only: world-space back walls behind enclosed spaces (cellars, shafts, the void under the
# town), drawn by a child below platforms and decor (z -60) but above the parallax backdrop,
# so underground views no longer show the town skyline. Built from the authored Terrain.
var _underground: Node2D
var _rooms: Array[Vector2i] = []
var _room_tops: Dictionary = {}
var _deep: Array[Vector2i] = []
var _deep_bottom := 0.0
var _span := Vector2.ZERO
var _cellar: Array = [] # [texture, top-left, candle point or null]
var _deep_set := {}
# N2: true when a cell belongs to the solid-earth void under the town (Decor hangs nothing there).
func is_deep(cell: Vector2i) -> bool:
	return _deep_set.has(cell) or (_deep_bottom > 0.0 and cell.y * 16 >= _deep_bottom)
func _ready() -> void:
	terrain = get_parent().get_node_or_null("Terrain")
	if terrain != null:
		terrain.changed.connect(_on_terrain_changed)
	if world_level == 2:
		_underground = Node2D.new()
		_underground.name = "N2Underground"
		_underground.z_index = -60
		_underground.draw.connect(_draw_underground)
		add_child(_underground)
		_build_underground()
	queue_redraw()
func _on_terrain_changed() -> void:
	queue_redraw()
	if _underground != null: _build_underground()
func _build_underground() -> void:
	_rooms.clear()
	_room_tops.clear()
	_deep.clear()
	if not is_instance_valid(terrain): return
	var rect := terrain.get_used_rect()
	var x0 := rect.position.x - 2
	var x1 := rect.end.x + 2
	var y0 := rect.position.y - 2
	var y1 := rect.end.y + N2_BELOW_ROWS
	var solid := {}
	for cell in terrain.get_used_cells(): solid[cell] = true
	# Closing: grow solids, flood the open sky from the top row, then grow the sky back.
	# Only below the street line: covered passages above ground keep their skyline view.
	var grown := {}
	for cell: Vector2i in solid:
		for dy in range(-N2_CLOSING, N2_CLOSING + 1):
			for dx in range(-N2_CLOSING, N2_CLOSING + 1):
				var g := cell + Vector2i(dx, dy)
				if g.y >= N2_GROUND_ROW or solid.has(g): grown[g] = true
	var sky := {}
	var stack: Array[Vector2i] = []
	for x in range(x0, x1):
		var c := Vector2i(x, y0)
		if not grown.has(c):
			sky[c] = true
			stack.append(c)
	var dirs := [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]
	while not stack.is_empty():
		var c: Vector2i = stack.pop_back()
		for d: Vector2i in dirs:
			var n := c + d
			if n.x < x0 or n.x >= x1 or n.y < y0 or n.y >= y1 or sky.has(n) or grown.has(n): continue
			sky[n] = true
			stack.append(n)
	var open := sky.duplicate()
	for c: Vector2i in sky:
		for dy in range(-N2_CLOSING, N2_CLOSING + 1):
			for dx in range(-N2_CLOSING, N2_CLOSING + 1):
				var n := c + Vector2i(dx, dy)
				if not solid.has(n): open[n] = true
	for y in range(y0, N2_GROUND_ROW):
		for x in range(x0, x1):
			var c := Vector2i(x, y)
			if not solid.has(c): open[c] = true
	# Enclosed components: a room if bounded, deep earth if it reaches the grid border.
	var seen := {}
	for y in range(y0, y1):
		for x in range(x0, x1):
			var start := Vector2i(x, y)
			if solid.has(start) or open.has(start) or seen.has(start): continue
			var component: Array[Vector2i] = [start]
			seen[start] = true
			var deep := false
			var i := 0
			while i < component.size():
				var c: Vector2i = component[i]
				i += 1
				if c.x <= x0 or c.x >= x1 - 1 or c.y >= y1 - 1: deep = true
				for d: Vector2i in dirs:
					var n := c + d
					if n.x < x0 or n.x >= x1 or n.y < y0 or n.y >= y1: continue
					if solid.has(n) or open.has(n) or seen.has(n): continue
					seen[n] = true
					component.append(n)
			if deep:
				_deep.append_array(component)
			else:
				_rooms.append_array(component)
				for c in component:
					if open.has(c + Vector2i.UP): _room_tops[c] = true
	_deep_set.clear()
	for c in _deep: _deep_set[c] = true
	_furnish_cellars(solid)
	_span = Vector2(x0 * 16, x1 * 16)
	_deep_bottom = y1 * 16.0
	_underground.queue_redraw()
# Cellar dressing on the back wall: a bricked-up arch in the middle of each wide room floor,
# candle niches toward its ends and a cage hanging from the ceiling. Background only.
func _furnish_cellars(solid: Dictionary) -> void:
	_cellar.clear()
	var room := {}
	for c in _rooms: room[c] = true
	var floors := {}
	for c: Vector2i in _rooms:
		if solid.has(c + Vector2i.DOWN):
			if not floors.has(c.y): floors[c.y] = []
			floors[c.y].append(c.x)
	for y: int in floors:
		var xs: Array = floors[y]
		xs.sort()
		var start := 0
		for i in range(1, xs.size() + 1):
			if i < xs.size() and xs[i] == xs[i - 1] + 1: continue
			var x0: int = xs[start]
			var x1: int = xs[i - 1] + 1
			start = i
			if x1 - x0 < 8: continue
			var floor_y := float(y * 16 + 16)
			var mid := (x0 + x1) * 8.0
			_cellar.append([CELLAR_ARCH, Vector2(mid - 25, floor_y - 50).round(), null])
			for q in [0.22, 0.78]:
				var nx := roundf(lerpf(x0 * 16.0, x1 * 16.0, q))
				if room.has(Vector2i(int(nx / 16.0), y - 2)):
					_cellar.append([CELLAR_NICHE, Vector2(nx - 12, floor_y - 40), Vector2(nx - 12 + 17, floor_y - 40 + 15)])
			# Cage under the room ceiling above the arch's left side.
			var cx := int((mid - 40.0) / 16.0)
			var cy := y
			while room.has(Vector2i(cx, cy - 1)): cy -= 1
			if y - cy >= 5:
				_cellar.append([HANG_CAGE, Vector2(cx * 16 + 8 - 8, cy * 16), null])
func _draw_underground() -> void:
	var origin := terrain.position if is_instance_valid(terrain) else Vector2.ZERO
	for cell in _deep:
		var p := origin + Vector2(cell * 16)
		_underground.draw_texture_rect_region(N2_BACK, Rect2(p, Vector2(16, 16)), Rect2(posmod(int(p.x), 96), 48 + posmod(int(p.y), 48), 16, 16))
	# Everything below the grid is deep ground too (camera margins).
	_underground.draw_rect(Rect2(origin + Vector2(_span.x, _deep_bottom), Vector2(_span.y - _span.x, 2048)), Color("0f0f0c"))
	for cell in _rooms:
		var p := origin + Vector2(cell * 16)
		# Fade the wall where a shaft opens onto the sky.
		var alpha := 0.55 if _room_tops.has(cell) else 1.0
		_underground.draw_texture_rect_region(N2_BACK, Rect2(p, Vector2(16, 16)), Rect2(posmod(int(p.x), 96), posmod(int(p.y), 48), 16, 16), Color(1, 1, 1, alpha))
	for item in _cellar:
		_underground.draw_texture(item[0], origin + item[1], Color(0.8, 0.8, 0.78))
		if item[2] != null:
			var point: Vector2 = origin + item[2]
			_underground.draw_texture(N2_GLOW, (point - Vector2(32, 32)).round(), Color(1.0, 0.72, 0.4, 0.35))
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
# N2 material: 0 street masonry, 1 foundation sinking into earth, 2 rot earth.
func _n2_material(cell: Vector2i, depth: int) -> int:
	if cell.y < N2_GROUND_ROW: return 0
	if depth >= 3: return 2
	return 1 if depth == 2 else 0
# Well-mixed hash for sparse N2 decals (the linear _hash spaces rare picks regularly).
func _scatter(cell: Vector2i, salt: int) -> int:
	var h := (cell.x * 374761393 + cell.y * 668265263 + salt * 2246822519) & 0x7fffffff
	h = ((h ^ (h >> 13)) * 1274126177) & 0x7fffffff
	return h ^ (h >> 16)
# N2 decal column in n2_terrain_decals.png, or -1. Rare, never on a walkable rim.
func _n2_decal(cell: Vector2i, mask: int, material: int, depth: int, used: Dictionary) -> int:
	var h := _scatter(cell, 7) % 1000
	if material == 2:
		if h % 97 == 0: return 0
		if h % 61 == 1: return 1
		if h % 113 == 2: return 7
		return -1
	if mask != 0 or depth != 1: return -1
	# Foundation course just under a surface: grates, sewer mouths, cracks, rot blooms.
	if not used.has(cell + Vector2i.LEFT) or not used.has(cell + Vector2i.RIGHT): return -1
	if h % 17 == 0: return 3 if _scatter(cell, 8) % 3 == 0 else 2
	if h % 23 == 4: return 4
	if h % 19 == 5: return 5
	if h % 13 == 6: return 6
	return -1
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
	var lit_grates: Array[Vector2] = []
	var n2_earth: Array = []
	var n2_tiles: Array = []
	var n2_decals: Array = []
	for cell: Vector2i in used:
		var p := terrain.position + Vector2(cell * 16)
		# Exposure mask: 1 open above, 2 right, 4 below, 8 left.
		var mask := 0
		if not used.has(cell + Vector2i.UP): mask |= 1
		if not used.has(cell + Vector2i.RIGHT): mask |= 2
		if not used.has(cell + Vector2i.DOWN): mask |= 4
		if not used.has(cell + Vector2i.LEFT): mask |= 8
		var shade: float = DEPTH_SHADE[depths[cell]]
		var tint := Color(shade, shade, shade)
		if biome == 0:
			# Collected per texture and drawn in passes below, so the renderer batches them.
			var material := _n2_material(cell, depths[cell])
			if material > 0:
				n2_earth.append([Rect2(p, Vector2(16, 16)), Rect2(posmod(int(p.x), 256), posmod(int(p.y), 128), 16, 16), tint])
			var n2_row := material * 18 + posmod(cell.y, 3) * 6 + posmod(cell.x, 6)
			n2_tiles.append([Rect2(p, Vector2(16, 16)), Rect2(mask * 16, n2_row * 16, 16, 16), tint])
			var decal := _n2_decal(cell, mask, material, depths[cell], used)
			if decal >= 0:
				n2_decals.append([Rect2(p, Vector2(16, 16)), Rect2(decal * 16, 0, 16, 16), tint])
				if decal == 3: lit_grates.append(p + Vector2(8, 9))
			if mask & 1: surfaces.append(cell)
			if mask & 4 and cell.y < 18: overhangs.append(cell)
			continue
		var row := theme * 18 + posmod(cell.y, 3) * 6 + posmod(cell.x, 6)
		draw_texture_rect_region(atlas, Rect2(p, Vector2(16, 16)), Rect2(mask * 16, row * 16, 16, 16), tint)
		if mask & 1: surfaces.append(cell)
		if mask & 4 and cell.y < 18: overhangs.append(cell)
	for item in n2_earth: draw_texture_rect_region(N2_EARTH, item[0], item[1], item[2])
	for item in n2_tiles: draw_texture_rect_region(N2_TILES, item[0], item[1], item[2])
	for item in n2_decals: draw_texture_rect_region(N2_DECALS, item[0], item[1], item[2])
	# Faint rot light leaking from a few cellar grates (static, very low alpha).
	for point in lit_grates:
		draw_texture(GLOW, (point - Vector2(32, 32)).round(), Color(0.62, 0.66, 0.34, 0.14))
	for cell in surfaces:
		var p := terrain.position + Vector2(cell * 16)
		draw_texture_rect_region(TUFTS, Rect2(p + Vector2(0, -11), Vector2(16, 12)), Rect2((_hash(cell, 1) % 8) * 16, biome * 12, 16, 12))
	# Strands, roots or rot hang from some undersides (decor only, low contrast).
	for cell in overhangs:
		if _hash(cell, 2) % 100 >= 55: continue
		var p := terrain.position + Vector2(cell * 16)
		draw_texture_rect_region(VINES, Rect2(p + Vector2(0, 15), Vector2(16, 24)), Rect2((_hash(cell, 3) % 8) * 16, biome * 24, 16, 24), Color(0.8, 0.8, 0.8))

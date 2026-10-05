@tool
# Ground decor of N2-N4 (RUN-020). Purely visual: no collision, no signage, no hint.
# Props are placed deterministically on the authored Terrain surfaces, so the decor follows
# layout changes without editing this script. A prop is placed only where its whole width
# rests on one surface row with clear headroom, and away from gameplay nodes (coins,
# enemies, hazards, items, doors, secrets, gate) so they keep their contrast. Nothing is
# placed near secret walls, to avoid giving them away.
# Sibling of Player, Coins, Enemies...; place it after Backdrop and before Terrain/TerrainSkin.
extends Node2D
const GLOW = preload("res://assets/sprites/prop_glow.png")
enum Light { NONE, LANTERN, CANDLE }
# Per biome: [texture, weight, light]. Weights are relative; big props are rare.
var SETS := [
	[
		[preload("res://assets/sprites/prop_house.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_house_ruined.png"), 3, Light.NONE],
		[preload("res://assets/run020/blight_town_well.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_cart.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_gallows.png"), 1, Light.NONE],
		[preload("res://assets/sprites/prop_fence.png"), 3, Light.NONE],
		[preload("res://assets/sprites/prop_lantern_post.png"), 3, Light.LANTERN],
		[preload("res://assets/run020/blight_town_barrels.png"), 4, Light.NONE],
		[preload("res://assets/run020/blight_town_rot_mound.png"), 4, Light.NONE],
		[preload("res://assets/sprites/prop_rubble.png"), 3, Light.NONE],
		[preload("res://assets/sprites/prop_bones.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_tree_dead_a.png"), 2, Light.NONE],
	],
	[
		[preload("res://assets/run020/black_forrest_pine.png"), 6, Light.NONE],
		[preload("res://assets/sprites/prop_tree_a.png"), 3, Light.NONE],
		[preload("res://assets/sprites/prop_tree_b.png"), 3, Light.NONE],
		[preload("res://assets/sprites/prop_tree_dead_b.png"), 2, Light.NONE],
		[preload("res://assets/run020/black_forrest_stump.png"), 3, Light.NONE],
		[preload("res://assets/run020/black_forrest_rock.png"), 4, Light.NONE],
		[preload("res://assets/run020/black_forrest_fungus.png"), 3, Light.NONE],
		[preload("res://assets/sprites/prop_bush.png"), 5, Light.NONE],
	],
	[
		[preload("res://assets/run020/forbidden_graveyard_mausoleum.png"), 1, Light.NONE],
		[preload("res://assets/run020/forbidden_graveyard_willow.png"), 2, Light.NONE],
		[preload("res://assets/run020/forbidden_graveyard_cross.png"), 3, Light.NONE],
		[preload("res://assets/run020/forbidden_graveyard_fence.png"), 3, Light.NONE],
		[preload("res://assets/run020/forbidden_graveyard_candle.png"), 3, Light.CANDLE],
		[preload("res://assets/sprites/prop_grave_a.png"), 4, Light.NONE],
		[preload("res://assets/sprites/prop_grave_b.png"), 4, Light.NONE],
		[preload("res://assets/sprites/prop_grave_c.png"), 4, Light.NONE],
		[preload("res://assets/sprites/prop_bones.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_tree_dead_a.png"), 2, Light.NONE],
	],
]
# N1 props are slightly tinted toward the biome; new RUN-020 props are drawn untinted.
const TINTS = [Color(0.92, 0.9, 0.84), Color(0.78, 0.86, 0.94), Color(0.84, 0.8, 0.94)]
@export_range(2, 4) var world_level: int = 2:
	set(value):
		world_level = value
		_laid_out = false
		queue_redraw()
@export var level_width := 2800.0:
	set(value):
		level_width = value
		_laid_out = false
		queue_redraw()
# Mean gap between props, in px; lower is denser. The forest is denser than the town.
@export_range(24.0, 240.0) var spacing := 72.0
const SPACING_SCALE = [1.0, 0.6, 0.9]
const MIN_RUN = 4
# Sibling nodes whose children (or themselves) keep a clear horizontal margin, in px.
# Coins are not listed: they draw over this dark, low-contrast decor and stay readable (as in N1).
# Secret walls and doors (Exploration) and the gate get a wide berth.
@export var avoid_margins := {"Enemies": 12.0, "Hazards": 20.0, "Items": 24.0, "Exploration": 64.0, "GoldGate": 64.0, "ExitArea": 24.0}
var _placed: Array = [] # [texture, foot, tinted, light, phase]
var _laid_out := false
var _time := 0.0
var _since_draw := 0.0
func _process(delta: float) -> void:
	_time += delta
	_since_draw += delta
	if _since_draw >= 0.1:
		_since_draw = 0.0
		queue_redraw()
func _hash(a: int, b: int, salt: int) -> int:
	return posmod(a * 73856093 ^ b * 19349663 ^ salt * 83492791, 1000003)
func _obstacles() -> Array:
	var points := []
	for key in avoid_margins:
		var node := get_parent().get_node_or_null(NodePath(String(key)))
		if node == null: continue
		var nodes: Array = [node]
		if node.get_child_count() > 0 and not node is CollisionObject2D:
			nodes = node.get_children()
		for child in nodes:
			if child is Node2D: points.append([to_local(child.global_position), float(avoid_margins[key])])
	return points
func _layout() -> void:
	_placed.clear()
	_laid_out = true
	var terrain: TileMapLayer = get_parent().get_node_or_null("Terrain")
	if terrain == null: return
	var b := clampi(world_level, 2, 4) - 2
	var props: Array = SETS[b]
	var total := 0
	for p in props: total += int(p[1])
	var used := {}
	for cell in terrain.get_used_cells(): used[cell] = true
	# Surface cells grouped by row, then scanned left to right.
	var rows := {}
	for cell: Vector2i in used:
		if used.has(cell + Vector2i.UP): continue
		if not rows.has(cell.y): rows[cell.y] = []
		rows[cell.y].append(cell.x)
	var obstacles := _obstacles()
	for y: int in rows:
		var xs: Array = rows[y]
		xs.sort()
		# Only runs of at least MIN_RUN cells host decor: small ledges stay bare.
		var surface := {}
		var start := 0
		for i in range(1, xs.size() + 1):
			if i == xs.size() or xs[i] != xs[i - 1] + 1:
				if i - start >= MIN_RUN:
					for k in range(start, i): surface[xs[k]] = true
				start = i
		if surface.is_empty(): continue
		var cursor := float(xs[0] * 16)
		var last := float(xs[-1] * 16 + 16)
		var tries := 0
		while cursor < last and tries < 400:
			tries += 1
			var h := _hash(int(cursor), y, b)
			var pick := h % total
			var entry: Array = props[0]
			for p in props:
				pick -= int(p[1])
				if pick < 0:
					entry = p
					break
			var tex: Texture2D = entry[0]
			var w := float(tex.get_width())
			var foot := to_local(terrain.to_global(Vector2(cursor + w * 0.5, y * 16)))
			if _fits(tex, cursor, surface, used, y) and _clear(foot, w, tex.get_height(), obstacles):
				var tinted: bool = not tex.resource_path.begins_with("res://assets/run020/")
				_placed.append([tex, foot, tinted, entry[2], float(h % 100) * 0.1])
				cursor += w + spacing * SPACING_SCALE[b] * (0.5 + float(h % 97) / 97.0)
			else:
				cursor += 16.0
# cursor: left edge of the prop in Terrain coordinates.
func _fits(tex: Texture2D, cursor: float, surface: Dictionary, used: Dictionary, y: int) -> bool:
	var left := floori(cursor / 16.0)
	var right := floori((cursor + tex.get_width() - 1.0) / 16.0)
	var rows_up := ceili(tex.get_height() / 16.0)
	for x in range(left, right + 1):
		if not surface.has(x): return false
		for k in range(1, rows_up + 1):
			if used.has(Vector2i(x, y - k)): return false
	return true
func _clear(foot: Vector2, w: float, h: float, obstacles: Array) -> bool:
	for o in obstacles:
		var p: Vector2 = o[0]
		var r: float = o[1]
		if absf(p.x - foot.x) < w * 0.5 + r and p.y > foot.y - h - r and p.y < foot.y + r:
			return false
	return true
# Warm lantern or cold grave-candle light: dithered low-alpha glow, flame only for lanterns.
func _light(point: Vector2, kind: int, phase: float) -> void:
	var flicker := 0.78 + 0.22 * sin(_time * 7.0 + phase) * sin(_time * 3.1 + phase * 2.0)
	if kind == Light.LANTERN:
		draw_texture(GLOW, (point - Vector2(32, 32)).round(), Color(1, 1, 1, clampf(flicker * 0.6, 0.0, 1.0)))
	else:
		draw_texture(GLOW, (point - Vector2(32, 32)).round(), Color(0.45, 0.75, 0.8, clampf(flicker * 0.35, 0.0, 1.0)))
func _draw() -> void:
	if not _laid_out: _layout()
	var b := clampi(world_level, 2, 4) - 2
	# N2: the village props drift toward rot colours near the exit (level_width).
	for item in _placed:
		var tex: Texture2D = item[0]
		var foot: Vector2 = item[1]
		var tint: Color = TINTS[b] if item[2] else Color.WHITE
		if b == 0 and level_width > 0.0:
			tint = tint.lerp(Color(0.8, 0.82, 0.66), clampf(foot.x / level_width, 0.0, 1.0) * 0.4)
		draw_texture(tex, (foot - Vector2(tex.get_width() * 0.5, tex.get_height())).round(), tint)
		match int(item[3]):
			Light.LANTERN: _light(foot + Vector2(5, -38), Light.LANTERN, item[4])
			Light.CANDLE: _light(foot + Vector2(0, -9), Light.CANDLE, item[4])

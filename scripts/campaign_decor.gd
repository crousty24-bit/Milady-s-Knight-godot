@tool
# Ground decor of N2-N4 (RUN-020). Purely visual: no collision, no signage, no hint.
# Props are placed deterministically on the authored Terrain surfaces, so the decor follows
# layout changes without editing this script. A prop is placed only where its whole width
# rests on one surface row with clear headroom, and away from gameplay nodes (coins,
# enemies, hazards, items, doors, secrets, gate) so they keep their contrast. Nothing is
# placed near secret walls, to avoid giving them away.
# Sibling of Player, Coins, Enemies...; place it after Backdrop and before Terrain/TerrainSkin.
# RUN-021 N2 pass: Blight Town also gets its own props (tools/art/run021/n2/props_n2.py), wall and
# ceiling props on authored faces and undersides, animated pyre flames, lit windows, bile lamps,
# a slow ground miasma along long streets and flies over rot. Drawn at z -1 so moving platforms
# always stay in front.
# RUN-021 N3 pass: Black Forest gets its own props (tools/art/run021/n3/props_n3.py) with the same
# wall/ceiling placement, camp fire and shrine lights, fungus glows, a cold ground fog and
# fireflies.
# RUN-021 N4 pass: Forbidden Graveyard gets its own props (tools/art/run021/n4/props_n4.py) with the
# same wall/ceiling placement, cold spectral grave candles and lamps, a low grave mist with slow
# plumes and a few drifting will-o'-wisps.
extends Node2D
func _enter_tree() -> void:
	if world_level >= 2 and world_level <= 4: z_index = -1
const GLOW = preload("res://assets/sprites/prop_glow.png")
const N2_GLOW = preload("res://assets/run021/n2/n2_glow.png")
const N2_MIASMA = preload("res://assets/run021/n2/n2_miasma.png")
const FLAME = preload("res://assets/sprites/prop_flame.png")
const N2P = "res://assets/run021/n2/props/"
const N3P = "res://assets/run021/n3/props/"
const N3_FOG = preload("res://assets/run021/n3/n3_fog.png")
const N4_MIST = preload("res://assets/run021/n4/n4_mist.png")
const N4P = "res://assets/run021/n4/props/"
enum Light { NONE, LANTERN, CANDLE, SPORE, FLAME, WINDOW, BILE, FUNGUS, SHRINE, SPECTRAL, SPECTRAL_LAMP }
# Per biome: [texture, weight, light, optional [[offset from the prop's top-left, light], ...]].
# Weights are relative; big props are rare.
# RUN-021: more dim light sources (lanterns, spore caps, grave candles) so N2-N4 keep a few
# warm/cold accents like the lit village of N1.
const SETS = [
	[
		[preload("res://assets/sprites/prop_house.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_house_ruined.png"), 3, Light.NONE],
		[preload("res://assets/run020/blight_town_well.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_cart.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_gallows.png"), 1, Light.NONE],
		[preload("res://assets/sprites/prop_fence.png"), 3, Light.NONE],
		[preload("res://assets/sprites/prop_lantern_post.png"), 5, Light.LANTERN],
		# RUN-021 N2: decor barrels removed (they read like the breakable ammo barrels).
		[preload("res://assets/run020/blight_town_rot_mound.png"), 4, Light.NONE],
		[preload("res://assets/sprites/prop_rubble.png"), 3, Light.NONE],
		[preload("res://assets/sprites/prop_bones.png"), 2, Light.NONE],
		[preload("res://assets/sprites/prop_tree_dead_a.png"), 2, Light.NONE],
		[preload(N2P + "house_timber_a.png"), 3, Light.NONE, [[Vector2(54, 54), Light.WINDOW]]],
		[preload(N2P + "house_timber_b.png"), 3, Light.NONE],
		[preload(N2P + "cathedral_ruin.png"), 1, Light.NONE],
		[preload(N2P + "plague_cart.png"), 2, Light.NONE],
		[preload(N2P + "gibbet.png"), 2, Light.NONE],
		[preload(N2P + "pyre.png"), 3, Light.NONE, [[Vector2(16, 3), Light.FLAME]]],
		[preload(N2P + "stocks.png"), 2, Light.NONE],
		[preload(N2P + "rot_growth_a.png"), 3, Light.NONE],
		[preload(N2P + "rot_growth_b.png"), 3, Light.NONE],
		[preload(N2P + "plague_bell.png"), 2, Light.NONE],
		[preload(N2P + "clothesline.png"), 2, Light.NONE],
		[preload(N2P + "crow_b.png"), 2, Light.NONE],
		[preload(N2P + "bone_pile.png"), 3, Light.NONE],
	],
	[
		# RUN-021 N3: the boxy RUN-020 stump is removed (it read like the breakable ammo crates).
		[preload("res://assets/run020/black_forrest_pine.png"), 4, Light.NONE],
		[preload("res://assets/sprites/prop_tree_a.png"), 1, Light.NONE],
		[preload("res://assets/sprites/prop_tree_b.png"), 1, Light.NONE],
		[preload("res://assets/run020/black_forrest_rock.png"), 2, Light.NONE],
		[preload("res://assets/run020/black_forrest_fungus.png"), 3, Light.SPORE],
		[preload("res://assets/sprites/prop_bush.png"), 2, Light.NONE],
		[preload(N3P + "fir_a.png"), 7, Light.NONE],
		[preload(N3P + "fir_b.png"), 7, Light.NONE],
		[preload(N3P + "gnarled_oak.png"), 2, Light.NONE],
		[preload(N3P + "ancient_trunk.png"), 3, Light.NONE],
		[preload(N3P + "dead_birch.png"), 3, Light.NONE],
		[preload(N3P + "root_arch.png"), 3, Light.NONE],
		[preload(N3P + "fallen_log.png"), 3, Light.NONE],
		[preload(N3P + "fern_a.png"), 5, Light.NONE],
		[preload(N3P + "fern_b.png"), 5, Light.NONE],
		[preload(N3P + "mushroom_cluster.png"), 4, Light.NONE, [[Vector2(8, 5), Light.FUNGUS]]],
		[preload(N3P + "standing_stone.png"), 2, Light.NONE],
		[preload(N3P + "cairn.png"), 2, Light.NONE],
		[preload(N3P + "stag_totem.png"), 2, Light.NONE],
		[preload(N3P + "charcoal_camp.png"), 1, Light.NONE, [[Vector2(50, 29), Light.FLAME]]],
		[preload(N3P + "forest_shrine.png"), 1, Light.NONE, [[Vector2(9, 11), Light.SHRINE]]],
		[preload(N3P + "root_stump.png"), 3, Light.NONE],
		[preload(N3P + "owl_snag.png"), 2, Light.NONE],
		[preload(N3P + "moss_boulder.png"), 3, Light.NONE],
	],
	[
		# RUN-021 N4: the RUN-020 cross and grave candle stay; mausoleum, willow, fence, N1 graves,
		# bones and dead tree give way to the N4 set (light points from props_n4.json).
		[preload("res://assets/run020/forbidden_graveyard_cross.png"), 2, Light.NONE],
		[preload("res://assets/run020/forbidden_graveyard_candle.png"), 3, Light.CANDLE],
		[preload(N4P + "headstone_round.png"), 5, Light.NONE],
		[preload(N4P + "headstone_gothic.png"), 4, Light.NONE],
		[preload(N4P + "headstone_cracked.png"), 4, Light.NONE],
		[preload(N4P + "headstone_sunken.png"), 4, Light.NONE],
		[preload(N4P + "raven_headstone.png"), 1, Light.NONE],
		[preload(N4P + "cross_celtic.png"), 3, Light.NONE],
		[preload(N4P + "mausoleum_small.png"), 2, Light.NONE],
		[preload(N4P + "mausoleum_big.png"), 1, Light.NONE],
		[preload(N4P + "obelisk.png"), 2, Light.NONE],
		[preload(N4P + "column_broken.png"), 3, Light.NONE],
		[preload(N4P + "angel_statue.png"), 1, Light.NONE],
		[preload(N4P + "tomb_chest.png"), 3, Light.NONE],
		[preload(N4P + "grave_mound.png"), 3, Light.NONE],
		[preload(N4P + "yew.png"), 3, Light.NONE],
		[preload(N4P + "willow_dead.png"), 2, Light.NONE],
		[preload(N4P + "railing.png"), 3, Light.NONE],
		[preload(N4P + "candles_cold.png"), 2, Light.NONE, [[Vector2(5, 6), Light.SPECTRAL], [Vector2(10, 4), Light.SPECTRAL]]],
		[preload(N4P + "candles_warm.png"), 1, Light.NONE, [[Vector2(5, 5), Light.SHRINE], [Vector2(11, 7), Light.SHRINE]]],
		[preload(N4P + "lantern_post.png"), 1, Light.NONE, [[Vector2(12, 15), Light.SPECTRAL_LAMP]]],
		[preload(N4P + "wreath_stake.png"), 2, Light.NONE],
		[preload(N4P + "skull_pile.png"), 1, Light.NONE],
	],
]
# N1 props are slightly tinted toward the biome; new RUN-020 props are drawn untinted.
# N2 wall props (drawn for a wall on their left, mirrored otherwise): [texture, weight, anchor y].
const N2_WALL = [
	[preload(N2P + "wall_pipe.png"), 3, 4],
	[preload(N2P + "wall_sign.png"), 2, 2],
	[preload(N2P + "wall_rot.png"), 4, 15],
	[preload(N2P + "wall_chains.png"), 3, 2],
]
# N2 ceiling props (top-centre anchor): [texture, weight, light offset or null].
const N2_CEILING = [
	[preload(N2P + "hang_cage.png"), 2, null],
	[preload(N2P + "hang_rags.png"), 3, null],
	[preload(N2P + "hang_lamp_bile.png"), 2, Vector2(5, 29)],
	[preload("res://assets/sprites/prop_chain_lantern.png"), 2, Vector2(4, 30)],
]
const COBWEB = preload("res://assets/run021/n2/props/cobweb.png")
# N3 wall and ceiling props (same formats as N2_WALL / N2_CEILING); N2's cobweb is reused.
const N3_WALL = [
	[preload(N3P + "wall_roots.png"), 4, 24],
	[preload(N3P + "wall_fungus.png"), 3, 8],
	[preload(N3P + "wall_moss.png"), 4, 10],
	[preload(N3P + "wall_ivy.png"), 3, 2],
]
const N3_CEILING = [
	[preload(N3P + "hang_roots.png"), 4, null],
	[preload(N3P + "hang_moss.png"), 4, null],
	[preload(N3P + "hang_charm.png"), 2, null],
	[preload(N3P + "hang_lantern_hunter.png"), 1, Vector2(7, 23)],
]
const N3_COBWEB = COBWEB
# N4 wall and ceiling props (same formats); N2's cobweb is reused in the crypts.
const N4_WALL = [
	[preload(N4P + "wall_niche.png"), 3, 3],
	[preload(N4P + "wall_vine_dead.png"), 4, 2],
	[preload(N4P + "wall_chain_ring.png"), 3, 4],
	[preload(N4P + "wall_plaque_skull.png"), 2, 10],
]
const N4_CEILING = [
	[preload(N4P + "hang_chains.png"), 4, null],
	[preload(N4P + "hang_censer.png"), 1, Vector2(10, 28)],
	[preload(N4P + "hang_roots_n4.png"), 3, null],
	[preload(N4P + "hang_banner.png"), 2, null],
]
# N3: the ancient trunk is cut at its top edge; it only stands where terrain closes above it.
const N3_CANOPY_PROP = "ancient_trunk.png"
# Props that attract flies.
const N2_ROT = ["blight_town_rot_mound.png", "rot_growth_a.png", "rot_growth_b.png", "plague_cart.png", "bone_pile.png"]
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
const SPACING_SCALE = [0.75, 0.45, 0.55]
const MIN_RUN = 4
# Thin floating ledges (fewer solid rows below than this) only host props up to SMALL_PROP px
# high, so houses, trees or mausoleums never stand on a rampart slab or a branch.
const GROUNDED_ROWS = 3
const SMALL_PROP = 20
# Sibling nodes whose children (or themselves) keep a clear horizontal margin, in px.
# Coins are not listed: they draw over this dark, low-contrast decor and stay readable (as in N1).
# Secret walls and doors (Exploration) and the gate get a wide berth.
@export var avoid_margins := {"Enemies": 12.0, "Hazards": 20.0, "Items": 24.0, "Exploration": 64.0, "GoldGate": 64.0, "ExitArea": 24.0}
var _placed: Array = [] # [texture, foot, tinted, light, phase, extra lights]
# N2 state is untyped on purpose: an editor hot reload leaves newly added members null, and a
# typed container would then be called unchecked (crash). _layout() reassigns them.
var _hung = [] # N2: [texture, top-left, mirrored, light point or null, phase]
var _miasma = [] # N2: [x0, x1, surface y]
var _flies = [] # N2: [centre, phase]
var _fireflies = [] # N3: [centre, phase, radius]
var _wisps = [] # N4: [centre, phase, drift]
var _laid_out := false
# Bumped when the layout entry format changes. An editor hot reload keeps the old member values
# (_placed built by the previous script, _laid_out true); a version mismatch forces a fresh layout.
const LAYOUT_VERSION = 4
var _layout_version = 0
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
	var margins: Dictionary = avoid_margins.duplicate()
	# N2-N4: keep decor clear of the breakable ammo crates/barrels so they stay identifiable.
	if world_level >= 2 and world_level <= 4: margins["AmmoSupplies"] = 28.0
	for key in margins:
		var node := get_parent().get_node_or_null(NodePath(String(key)))
		if node == null: continue
		var nodes: Array = [node]
		if node.get_child_count() > 0 and not node is CollisionObject2D:
			nodes = node.get_children()
		for child in nodes:
			if child is Node2D: points.append([to_local(child.global_position), float(margins[key])])
	return points
func _layout() -> void:
	_placed = []
	_hung = []
	_miasma = []
	_flies = []
	_fireflies = []
	_wisps = []
	_laid_out = true
	_layout_version = LAYOUT_VERSION
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
			var fits := _fits(tex, cursor, surface, used, y)
			if fits and tex.resource_path.get_file() == N3_CANOPY_PROP: fits = _canopy_above(tex, cursor, used, y)
			if fits and _clear(foot, w, tex.get_height(), obstacles):
				var tinted: bool = not tex.resource_path.begins_with("res://assets/run020/") and not tex.resource_path.begins_with(N3P) and not tex.resource_path.begins_with(N4P)
				_placed.append([tex, foot, tinted, entry[2], float(h % 100) * 0.1, entry[3] if entry.size() > 3 else []])
				if b == 0 and tex.resource_path.get_file() in N2_ROT:
					_flies.append([foot + Vector2(0, -tex.get_height() - 6), float(h % 50) * 0.37])
				cursor += w + spacing * SPACING_SCALE[b] * (0.5 + float(h % 97) / 97.0)
			else:
				cursor += 16.0
		_collect_miasma(xs, y)
		if b == 1:
			_collect_fireflies(xs, y, obstacles)
		if b == 2:
			_collect_wisps(xs, y, obstacles)
	if b == 0:
		_layout_n2_hung(used, obstacles, N2_WALL, N2_CEILING, COBWEB)
	elif b == 1:
		_layout_n2_hung(used, obstacles, N3_WALL, N3_CEILING, N3_COBWEB)
	else:
		_layout_n2_hung(used, obstacles, N4_WALL, N4_CEILING, COBWEB)
# N3: a few firefly swarms over long runs, one every ~10 cells, kept clear of gameplay nodes.
func _collect_fireflies(xs: Array, y: int, obstacles: Array) -> void:
	var start := 0
	for i in range(1, xs.size() + 1):
		if i == xs.size() or xs[i] != xs[i - 1] + 1:
			if i - start >= 6:
				var x := int(xs[start]) + 2
				while x < int(xs[i - 1]) - 1:
					var h := _hash(x, y, 21)
					var centre := Vector2(x * 16 + 8, y * 16 - 22 - h % 30)
					if h % 3 != 0 and _clear(centre + Vector2(0, 24), 24.0, 48.0, obstacles):
						_fireflies.append([centre, float(h % 100) * 0.13, 10.0 + float(h % 9)])
					x += 8 + h % 6
			start = i
# N4: a few will-o'-wisps over long runs, one every ~16 cells, kept well clear of gameplay nodes
# so a dim drifting light is never taken for a projectile or a skull.
func _collect_wisps(xs: Array, y: int, obstacles: Array) -> void:
	var start := 0
	for i in range(1, xs.size() + 1):
		if i == xs.size() or xs[i] != xs[i - 1] + 1:
			if i - start >= 10:
				var x := int(xs[start]) + 4
				while x < int(xs[i - 1]) - 3:
					var h := _hash(x, y, 31)
					var centre := Vector2(x * 16 + 8, y * 16 - 18 - h % 22)
					if h % 2 == 0 and _clear(centre + Vector2(0, 30), 64.0, 72.0, obstacles):
						_wisps.append([centre, float(h % 100) * 0.17, 6.0 + float(h % 7)])
					x += 14 + h % 8
			start = i
# N2: miasma strips over runs of at least 8 surface cells (N3: ground fog, N4: grave mist).
func _collect_miasma(xs: Array, y: int) -> void:
	var start := 0
	for i in range(1, xs.size() + 1):
		if i == xs.size() or xs[i] != xs[i - 1] + 1:
			if i - start >= 8: _miasma.append([float(xs[start] * 16), float(xs[i - 1] * 16 + 16), float(y * 16)])
			start = i
func _pick(table: Array, h: int) -> Array:
	var total := 0
	for e in table: total += int(e[1])
	var pick := h % total
	for e in table:
		pick -= int(e[1])
		if pick < 0: return e
	return table[0]
func _rect_free(rect: Rect2, used: Dictionary, obstacles: Array) -> bool:
	var skin := get_parent().get_node_or_null("TerrainSkin")
	var deep_check := skin != null and skin.has_method("is_deep")
	for cy in range(floori(rect.position.y / 16.0), floori((rect.end.y - 1.0) / 16.0) + 1):
		for cx in range(floori(rect.position.x / 16.0), floori((rect.end.x - 1.0) / 16.0) + 1):
			if used.has(Vector2i(cx, cy)): return false
			if deep_check and skin.is_deep(Vector2i(cx, cy)): return false
	for o in obstacles:
		var p: Vector2 = o[0]
		if rect.grow(o[1]).has_point(p): return false
	return true
# N2 wall props on vertical faces at least three cells tall, ceiling props under undersides
# at least three cells wide, cobwebs in ceiling corners. Terrain coordinates are local here
# (Terrain sits at the origin of the level, like this node).
func _layout_n2_hung(used: Dictionary, obstacles: Array, wall_table: Array, ceiling_table: Array, cobweb: Texture2D) -> void:
	var last_face := {}
	var cells: Array = used.keys()
	cells.sort()
	for cell: Vector2i in cells:
		for side in [1, -1]:
			var out := Vector2i(side, 0)
			if used.has(cell + out): continue
			if not (used.has(cell + Vector2i.UP) and used.has(cell + Vector2i.DOWN)): continue
			if used.has(cell + Vector2i.UP + out) or used.has(cell + Vector2i.DOWN + out): continue
			var h := _hash(cell.x * 3 + side, cell.y, 11)
			if h % 7 != 0: continue
			var key := Vector2i(cell.x * 2 + (1 if side > 0 else 0), 0)
			if last_face.has(key) and absi(int(last_face[key]) - cell.y) < 4: continue
			var entry := _pick(wall_table, h / 7)
			var tex: Texture2D = entry[0]
			var wall_x := float(cell.x * 16 + (16 if side > 0 else 0))
			var top := float(cell.y * 16 + 8 - int(entry[2]))
			var left := wall_x if side > 0 else wall_x - tex.get_width()
			var rect := Rect2(left, top, tex.get_width(), tex.get_height())
			if not _rect_free(rect.grow_individual(-1 if side > 0 else 0, 0, 0 if side > 0 else -1, 0), used, obstacles): continue
			last_face[key] = cell.y
			_hung.append([tex, rect.position, side < 0, null, float(h % 100) * 0.1])
	for cell: Vector2i in cells:
		if used.has(cell + Vector2i.DOWN): continue
		var h := _hash(cell.x, cell.y, 12)
		# Cobweb in an inner corner where the underside meets a wall.
		for side in [-1, 1]:
			# Inner corner: the wall beside this underside continues down past it.
			if used.has(cell + Vector2i(side, 0)) and used.has(cell + Vector2i(side, 1)) and h % 3 == 0:
				var x := float(cell.x * 16 + (0 if side < 0 else 16 - cobweb.get_width()))
				var r := Rect2(x, cell.y * 16 + 16, cobweb.get_width(), cobweb.get_height())
				if _rect_free(r, used, obstacles):
					_hung.append([cobweb, r.position, side > 0, null, 0.0])
		if not (used.has(cell + Vector2i.LEFT) and used.has(cell + Vector2i.RIGHT)): continue
		if used.has(cell + Vector2i.LEFT + Vector2i.DOWN) or used.has(cell + Vector2i.RIGHT + Vector2i.DOWN): continue
		if h % 5 != 1: continue
		var entry := _pick(ceiling_table, h / 5)
		var tex: Texture2D = entry[0]
		var rect := Rect2(cell.x * 16 + 8 - tex.get_width() / 2, cell.y * 16 + 16, tex.get_width(), tex.get_height())
		# Keep two free cells under the prop so nothing dangles onto a floor.
		if not _rect_free(Rect2(rect.position, rect.size + Vector2(0, 32)), used, obstacles): continue
		var light = null
		if entry[2] != null: light = rect.position + Vector2(entry[2])
		_hung.append([tex, rect.position, false, light, float(h % 100) * 0.1])
# N3: terrain right above the top of a prop standing at row y, over its middle (no visible gap).
func _canopy_above(tex: Texture2D, cursor: float, used: Dictionary, y: int) -> bool:
	if tex.get_height() % 16 != 0: return false
	var mid := floori((cursor + tex.get_width() * 0.5) / 16.0)
	return used.has(Vector2i(mid, y - tex.get_height() / 16 - 1))
# cursor: left edge of the prop in Terrain coordinates.
func _fits(tex: Texture2D, cursor: float, surface: Dictionary, used: Dictionary, y: int) -> bool:
	var left := floori(cursor / 16.0)
	var right := floori((cursor + tex.get_width() - 1.0) / 16.0)
	var rows_up := ceili(tex.get_height() / 16.0)
	for x in range(left, right + 1):
		if not surface.has(x): return false
		if tex.get_height() > SMALL_PROP:
			for k in range(1, GROUNDED_ROWS):
				if not used.has(Vector2i(x, y + k)): return false
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
# Warm lantern, cold grave-candle or faint spore light: dithered low-alpha glow.
func _light(point: Vector2, kind: int, phase: float) -> void:
	var flicker := 0.78 + 0.22 * sin(_time * 7.0 + phase) * sin(_time * 3.1 + phase * 2.0)
	if kind == Light.LANTERN:
		draw_texture(GLOW, (point - Vector2(32, 32)).round(), Color(1, 1, 1, clampf(flicker * 0.6, 0.0, 1.0)))
	elif kind == Light.CANDLE:
		draw_texture(GLOW, (point - Vector2(32, 32)).round(), Color(0.45, 0.75, 0.8, clampf(flicker * 0.35, 0.0, 1.0)))
	else:
		# Spores pulse slowly instead of flickering; kept greyer than healing green.
		var pulse := 0.7 + 0.3 * sin(_time * 1.2 + phase)
		draw_texture(GLOW, (point - Vector2(32, 32)).round(), Color(0.55, 0.72, 0.62, 0.22 * pulse))
func _n2_glow(point: Vector2, color: Color, alpha: float) -> void:
	draw_texture(N2_GLOW, (point - Vector2(32, 32)).round(), Color(color, clampf(alpha, 0.0, 1.0)))
func _draw_prop_lights(tex: Texture2D, foot: Vector2, lights: Array, phase: float) -> void:
	var origin := foot - Vector2(tex.get_width() * 0.5, tex.get_height())
	for l in lights:
		var point: Vector2 = origin + Vector2(l[0])
		var flicker := 0.78 + 0.22 * sin(_time * 7.0 + phase) * sin(_time * 3.1 + phase * 2.0)
		match int(l[1]):
			Light.FLAME:
				draw_texture(GLOW, (point - Vector2(32, 36)).round(), Color(1, 1, 1, clampf(flicker * 0.85, 0.0, 1.0)))
				var frame := posmod(int(_time * 9.0 + phase * 3.0), 3)
				draw_texture_rect_region(FLAME, Rect2((point + Vector2(-5, -11)).round(), Vector2(10, 14)), Rect2(frame * 10, 0, 10, 14))
			Light.WINDOW:
				# A slow, warm candle-lit window: slower breathing than a flame.
				_n2_glow(point, Color(1.0, 0.7, 0.38), 0.32 + 0.08 * sin(_time * 1.7 + phase))
				draw_rect(Rect2((point + Vector2(-2, -2)).round(), Vector2(4, 4)), Color(1.0, 0.72, 0.36, 0.28 + 0.06 * sin(_time * 2.3 + phase)))
			Light.SHRINE:
				# A small warm candle: a faint flickering glow and a 1 px flame.
				_n2_glow(point, Color(1.0, 0.7, 0.4), 0.22 + 0.08 * flicker)
				draw_rect(Rect2((point + Vector2(0, -1)).round(), Vector2(1, 2)), Color(1.0, 0.82, 0.5, 0.75 * flicker))
			Light.FUNGUS:
				# Cold fungus light: slow pulse, kept greyer than healing green.
				_n2_glow(point, Color(0.62, 0.82, 0.72), 0.16 + 0.06 * sin(_time * 0.9 + phase))
			Light.SPECTRAL:
				# N4 grave candle: a pale cold 1 px flame over the painted wick, faint cold glow.
				_n2_glow(point, Color(0.56, 0.72, 0.8), 0.14 + 0.06 * flicker)
				draw_rect(Rect2((point + Vector2(0, -2)).round(), Vector2(1, 2)), Color(0.72, 0.85, 0.9, 0.7 * flicker))
			Light.SPECTRAL_LAMP:
				_spectral_lamp(point, phase)
# N4 lantern or censer: a cold flame in the glass, a slow-breathing cold glow.
func _spectral_lamp(point: Vector2, phase: float) -> void:
	var flicker := 0.8 + 0.2 * sin(_time * 5.0 + phase) * sin(_time * 2.3 + phase * 2.0)
	_n2_glow(point, Color(0.56, 0.72, 0.8), 0.24 + 0.06 * sin(_time * 1.1 + phase))
	draw_rect(Rect2((point + Vector2(-1, -2)).round(), Vector2(2, 3)), Color(0.66, 0.8, 0.86, 0.6 * flicker))
	draw_rect(Rect2((point + Vector2(0, -1)).round(), Vector2(1, 1)), Color(0.82, 0.9, 0.92, 0.8 * flicker))
func _draw_n2_hung() -> void:
	for item in _hung:
		var tex: Texture2D = item[0]
		var at: Vector2 = item[1]
		var tint := Color(0.9, 0.9, 0.86)
		if item[2]:
			draw_texture_rect(tex, Rect2(at + Vector2(tex.get_width(), 0), Vector2(-tex.get_width(), tex.get_height())), false, tint)
		else:
			draw_texture(tex, at, tint)
		if item[3] != null:
			var point: Vector2 = item[3]
			if tex.resource_path.ends_with("hang_lamp_bile.png"):
				_n2_glow(point, Color(0.72, 0.74, 0.4), 0.3 + 0.07 * sin(_time * 1.3 + item[4]))
			elif tex.resource_path.ends_with("hang_censer.png"):
				_spectral_lamp(point, item[4])
			else:
				_light(point, Light.LANTERN, item[4])
func _draw_n2_atmosphere() -> void:
	# Ground miasma: two drifting layers, low alpha, behind terrain and gameplay.
	for strip in _miasma:
		for layer in 2:
			var speed := 3.0 if layer == 0 else -2.0
			var alpha := 0.13 if layer == 0 else 0.09
			_draw_strip(N2_MIASMA, strip[0], strip[1], strip[2] - 30.0 + layer * 4.0, _time * speed + layer * 97.0, Color(0.6, 0.62, 0.38, alpha))
	for fly in _flies:
		var centre: Vector2 = fly[0]
		for k in 3:
			var t: float = _time * (2.4 + k * 0.7) + float(fly[1]) + k * 2.1
			var p := centre + Vector2(sin(t) * (5.0 + k * 2.0), sin(t * 1.7) * 3.0 - k * 2.0)
			draw_rect(Rect2(p.round(), Vector2.ONE), Color(0.3, 0.31, 0.24, 0.9))
# N3: cold ground fog (two slow layers, opposite drift) and blinking fireflies.
func _draw_n3_atmosphere() -> void:
	for strip in _miasma:
		for layer in 2:
			var speed := 2.2 if layer == 0 else -1.6
			var alpha := 0.1 if layer == 0 else 0.07
			_draw_strip(N3_FOG, strip[0], strip[1], strip[2] - 30.0 + layer * 5.0, _time * speed + layer * 131.0, Color(0.62, 0.72, 0.86, alpha))
	for swarm in _fireflies:
		var centre: Vector2 = swarm[0]
		var phase: float = swarm[1]
		var radius: float = swarm[2]
		for k in 3:
			var t := _time * (0.35 + k * 0.11) + phase + k * 2.3
			var p := centre + Vector2(sin(t) * radius, sin(t * 1.6 + k) * radius * 0.5)
			# Each fly blinks: a slow on/off with a soft peak.
			var on := sin(_time * (0.8 + k * 0.17) + phase * 3.0 + k * 1.9)
			if on <= 0.0: continue
			var a := on * on
			draw_rect(Rect2(p.round(), Vector2.ONE), Color(0.74, 0.88, 0.8, 0.9 * a))
			for d in [Vector2.LEFT, Vector2.RIGHT, Vector2.UP, Vector2.DOWN]:
				draw_rect(Rect2((p + d).round(), Vector2.ONE), Color(0.55, 0.75, 0.66, 0.25 * a))
# N4: grave mist hugging the ground (two slow layers, opposite drift) and will-o'-wisps: a
# faint cold glow with a 1 px core that drifts slowly and fades in and out.
func _draw_n4_atmosphere() -> void:
	for strip in _miasma:
		for layer in 2:
			var speed := 1.6 if layer == 0 else -1.1
			var alpha := 0.11 if layer == 0 else 0.07
			_draw_strip(N4_MIST, strip[0], strip[1], strip[2] - 30.0 + layer * 3.0, _time * speed + layer * 89.0, Color(0.66, 0.68, 0.84, alpha))
	for wisp in _wisps:
		var centre: Vector2 = wisp[0]
		var phase: float = wisp[1]
		var drift: float = wisp[2]
		var on := sin(_time * 0.42 + phase)
		if on <= 0.1: continue
		var a := (on - 0.1) / 0.9
		var p := centre + Vector2(sin(_time * 0.23 + phase) * drift * 2.0, sin(_time * 0.51 + phase * 2.0) * drift * 0.6)
		_n2_glow(p, Color(0.56, 0.72, 0.8), 0.13 * a)
		draw_rect(Rect2(p.round(), Vector2.ONE), Color(0.74, 0.86, 0.9, 0.75 * a))
		for d in [Vector2.LEFT, Vector2.RIGHT, Vector2.UP, Vector2.DOWN]:
			draw_rect(Rect2((p + d).round(), Vector2.ONE), Color(0.55, 0.7, 0.78, 0.22 * a))
# Whole pixels only: every step advances by at least 1 px (a float version stalled when
# x + scroll landed a hair below a multiple of 256, looping forever and exhausting memory).
func _draw_strip(texture: Texture2D, x0: float, x1: float, surface_y: float, scroll: float, tint: Color) -> void:
	var x := int(x0)
	var end := int(x1)
	var offset := int(floorf(scroll))
	var y := roundf(surface_y)
	var guard := 0
	while x < end and guard < 64:
		guard += 1
		var u := posmod(x + offset, 256)
		var w := mini(end - x, 256 - u)
		draw_texture_rect_region(texture, Rect2(x, y, w, 32), Rect2(u, 0, w, 32), tint)
		x += w
func _draw() -> void:
	if not _laid_out or _layout_version != LAYOUT_VERSION: _layout()
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
			Light.SPORE: _light(foot + Vector2(0, -5), Light.SPORE, item[4])
		if item.size() > 5 and not item[5].is_empty():
			_draw_prop_lights(tex, foot, item[5], item[4])
	if b == 0:
		_draw_n2_hung()
		_draw_n2_atmosphere()
	elif b == 1:
		_draw_n2_hung()
		_draw_n3_atmosphere()
	else:
		_draw_n2_hung()
		_draw_n4_atmosphere()

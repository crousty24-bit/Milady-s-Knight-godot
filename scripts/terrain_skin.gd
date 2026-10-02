@tool
# Skins the authored Terrain (TileMapLayer) with generated stone tiles.
# Collision and layout remain in Terrain; this node only draws.
# Atlas (tools/art/world_terrain.py): column = exposure mask, row = theme * 18 + seed * 6 + phase.
extends Node2D
const TILES = preload("res://assets/sprites/terrain_stone.png")
const TUFTS = preload("res://assets/sprites/terrain_tufts.png")
const VINES = preload("res://assets/sprites/env_vines.png")
# Blight takes over the masonry from here to the sealed gate.
const CORRUPTION_X = 1392.0
const DEPTH_SHADE = [1.0, 0.86, 0.74, 0.64, 0.56, 0.5]
@onready var terrain: TileMapLayer = get_parent().get_node("Terrain")
func _ready() -> void:
	terrain.changed.connect(queue_redraw)
	queue_redraw()
func _hash(cell: Vector2i, salt: int) -> int:
	return posmod(cell.x * 73 + cell.y * 151 + salt * 31 + cell.x * cell.y * 7, 1009)
func _draw() -> void:
	if not is_instance_valid(terrain): return
	var used := {}
	for cell in terrain.get_used_cells(): used[cell] = true
	var surfaces: Array[Vector2i] = []
	var overhangs: Array[Vector2i] = []
	for cell: Vector2i in used:
		var p := Vector2(cell * 16)
		# Exposure mask: 1 open above, 2 right, 4 below, 8 left.
		var mask := 0
		if not used.has(cell + Vector2i.UP): mask |= 1
		if not used.has(cell + Vector2i.RIGHT): mask |= 2
		if not used.has(cell + Vector2i.DOWN): mask |= 4
		if not used.has(cell + Vector2i.LEFT): mask |= 8
		var theme := 1 if p.x >= CORRUPTION_X else 0
		var row := theme * 18 + posmod(cell.y, 3) * 6 + posmod(cell.x, 6)
		var depth := 0
		while depth < 5 and used.has(cell - Vector2i(0, depth + 1)): depth += 1
		var shade: float = DEPTH_SHADE[depth]
		draw_texture_rect_region(TILES, Rect2(p, Vector2(16, 16)), Rect2(mask * 16, row * 16, 16, 16), Color(shade, shade, shade))
		if mask & 1: surfaces.append(cell)
		if mask & 4 and cell.y < 18: overhangs.append(cell)
	for cell in surfaces:
		var p := Vector2(cell * 16)
		var theme := 1 if p.x >= CORRUPTION_X else 0
		var column := _hash(cell, 1) % 8
		draw_texture_rect_region(TUFTS, Rect2(p + Vector2(0, -11), Vector2(16, 12)), Rect2(column * 16, theme * 12, 16, 12))
	# Vines and roots hang from some undersides (decor only, low contrast).
	for cell in overhangs:
		if _hash(cell, 2) % 100 >= 55: continue
		var p := Vector2(cell * 16)
		var theme := 1 if p.x >= CORRUPTION_X else 0
		var column := _hash(cell, 3) % 8
		draw_texture_rect_region(VINES, Rect2(p + Vector2(0, 15), Vector2(16, 24)), Rect2(column * 16, theme * 24, 16, 24), Color(0.8, 0.8, 0.8))

@tool
# Skins the authored Terrain (TileMapLayer) with generated stone tiles.
# Collision and layout remain in Terrain; this node only draws.
extends Node2D
const TILES = preload("res://assets/sprites/terrain_stone.png")
const TUFTS = preload("res://assets/sprites/terrain_tufts.png")
# Blight takes over the masonry from here to the sealed gate.
const CORRUPTION_X = 1392.0
const DEPTH_SHADE = [1.0, 0.86, 0.74, 0.64, 0.56, 0.5]
@onready var terrain: TileMapLayer = get_parent().get_node("Terrain")
func _ready() -> void:
	terrain.changed.connect(queue_redraw)
	queue_redraw()
func _draw() -> void:
	if not is_instance_valid(terrain): return
	var used := {}
	for cell in terrain.get_used_cells(): used[cell] = true
	var surfaces: Array[Vector2i] = []
	for cell: Vector2i in used:
		var p := Vector2(cell * 16)
		# Exposure mask: 1 open above, 2 right, 4 below, 8 left (tools/art/world.py).
		var mask := 0
		if not used.has(cell + Vector2i.UP): mask |= 1
		if not used.has(cell + Vector2i.RIGHT): mask |= 2
		if not used.has(cell + Vector2i.DOWN): mask |= 4
		if not used.has(cell + Vector2i.LEFT): mask |= 8
		var row := (3 if p.x >= CORRUPTION_X else 0) + posmod(cell.x * 7 + cell.y * 3, 3)
		var depth := 0
		while depth < 5 and used.has(cell - Vector2i(0, depth + 1)): depth += 1
		var shade: float = DEPTH_SHADE[depth]
		draw_texture_rect_region(TILES, Rect2(p, Vector2(16, 16)), Rect2(mask * 16, row * 16, 16, 16), Color(shade, shade, shade))
		if mask & 1: surfaces.append(cell)
	for cell in surfaces:
		var p := Vector2(cell * 16)
		var column := (3 if p.x >= CORRUPTION_X else 0) + posmod(cell.x * 5 + cell.y, 3)
		draw_texture_rect_region(TUFTS, Rect2(p + Vector2(0, -6), Vector2(16, 8)), Rect2(column * 16, 0, 16, 8))

@tool
# Opaque, grid-aligned stonework keeps the playable surfaces visually quiet.
# Collision and authored layout remain in Terrain (TileMapLayer).
extends Node2D
@onready var terrain: TileMapLayer = get_parent().get_node("Terrain")
func _ready() -> void:
	terrain.changed.connect(queue_redraw)
	queue_redraw()
func _draw() -> void:
	if not is_instance_valid(terrain): return
	for cell in terrain.get_used_cells():
		var p = Vector2(cell * 16)
		var corrupt: bool = p.x >= 1392
		var surface: bool = terrain.get_cell_source_id(cell+Vector2i.UP) == -1
		var shade: int = posmod(cell.x*13+cell.y*7,3)
		var colors: Array = ["41484a","454c4d","484f50"] if corrupt else ["53534b","58584f","50534b"]
		draw_rect(Rect2(p,Vector2(16,16)),Color(colors[shade]))
		draw_line(p+Vector2(0,15),p+Vector2(15,15),Color("30393b"))
		draw_line(p+Vector2(15,1),p+Vector2(15,7),Color("30393b"))
		draw_line(p+Vector2(0,7),p+Vector2(16,7),Color("384041"))
		draw_line(p+Vector2(7,9),p+Vector2(7,15),Color("384041"))
		if surface:
			draw_rect(Rect2(p,Vector2(16,2)),Color("93908a" if corrupt else "a3a080"))
			if not corrupt and p.y >= 144:
				draw_rect(Rect2(p+Vector2(0,-1),Vector2(16,2)),Color("6e7e59"))
				draw_rect(Rect2(p+Vector2(shade*4,-3),Vector2(2,3)),Color("89966a"))

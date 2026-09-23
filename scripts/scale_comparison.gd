@tool
extends Node2D
## RUN-003 visual fixture. Change grid_size in the inspector (16 or 32).
## The 32px view enlarges existing art; it is a size study, not 32px source art.

@export_enum("16:16", "32:32") var grid_size: int = 16:
	set(value):
		grid_size = value
		queue_redraw()

const KNIGHT = preload("res://assets/sprites/knight.png")
const SLIME = preload("res://assets/sprites/slime_green.png")
const FONT = preload("res://assets/fonts/PixelOperator8.ttf")

func _draw() -> void:
	var factor := float(grid_size) / 16.0
	draw_rect(Rect2(0, 0, 640, 360), Color("191e23"))
	draw_rect(Rect2(0, 205, 640, 57), Color("29323a"))
	draw_rect(Rect2(0, 258, 640, 4), Color("8b8871"))
	for x in range(0, 640, grid_size):
		var shade := Color("52534a") if (x / grid_size) % 3 == 0 else Color("484d49")
		draw_rect(Rect2(x, 262, grid_size, 98), shade)
		draw_line(Vector2(x, 262), Vector2(x, 360), Color("343c3d"))
	for x in [34, 125, 344, 544]:
		_draw_tree(Vector2(x, 262), factor)
	_draw_knight(Vector2(124, 262), factor)
	_draw_slime(Vector2(236, 262), factor)
	_draw_humanoid(Vector2(363, 262), factor)
	_draw_thorns(Vector2(468, 262), factor)
	_draw_chest(Vector2(559, 262), factor)
	draw_string(FONT, Vector2(12, 24), "RUN-003 / grille %d x %d / viewport 640 x 360" % [grid_size, grid_size], HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color.WHITE)
	draw_string(FONT, Vector2(12, 43), "N1 : extrait de terrain et proportions au sol", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("d3d5d1"))
	for label in [["Joueur", 124], ["Slime", 236], ["Humanoide*", 363], ["Piques*", 468], ["Coffre*", 559]]:
		draw_string(FONT, Vector2(label[1] - 31, 293), label[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color.WHITE)
	draw_string(FONT, Vector2(12, 334), "* Maquette sans asset final. Contours jaunes : collision indicative.", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("e3d5aa"))
	draw_string(FONT, Vector2(12, 350), "32 : sprites agrandis, aucun detail source nouveau.", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("d3d5d1"))

func _draw_knight(foot: Vector2, factor: float) -> void:
	var size := Vector2(32, 32) * factor
	draw_texture_rect_region(KNIGHT, Rect2(foot - Vector2(size.x / 2, size.y), size), Rect2(0, 0, 32, 32))
	_draw_hitbox(foot, Vector2(10, 18) * factor)

func _draw_slime(foot: Vector2, factor: float) -> void:
	var size := Vector2(24, 24) * factor
	draw_texture_rect_region(SLIME, Rect2(foot - Vector2(size.x / 2, size.y), size), Rect2(0, 24, 24, 24))
	_draw_hitbox(foot, Vector2(14, 12) * factor)

func _draw_humanoid(foot: Vector2, factor: float) -> void:
	# Shape-only stand-in at the art bible target, roughly 24 x 36 px.
	var origin := foot - Vector2(12, 36) * factor
	draw_rect(Rect2(origin + Vector2(7, 0) * factor, Vector2(10, 10) * factor), Color("c7c6ad"))
	draw_rect(Rect2(origin + Vector2(4, 10) * factor, Vector2(16, 16) * factor), Color("736c76"))
	draw_rect(Rect2(origin + Vector2(4, 26) * factor, Vector2(6, 10) * factor), Color("a9a9a1"))
	draw_rect(Rect2(origin + Vector2(14, 26) * factor, Vector2(6, 10) * factor), Color("a9a9a1"))
	_draw_hitbox(foot, Vector2(14, 26) * factor)

func _draw_thorns(foot: Vector2, factor: float) -> void:
	# Current hazard is a 30 x 10 Area2D; its thorn graphic is generated in code.
	for x in [-12, -4, 4]:
		var p := foot + Vector2(x, 0) * factor
		draw_colored_polygon(PackedVector2Array([p, p + Vector2(5, -12) * factor, p + Vector2(10, 0) * factor]), Color("c47768"))
	_draw_hitbox(foot, Vector2(30, 10) * factor)

func _draw_chest(foot: Vector2, factor: float) -> void:
	var origin := foot - Vector2(12, 20) * factor
	draw_rect(Rect2(origin, Vector2(24, 20) * factor), Color("684b33"))
	draw_rect(Rect2(origin, Vector2(24, 5) * factor), Color("ad8250"))
	draw_rect(Rect2(origin + Vector2(10, 8) * factor, Vector2(4, 6) * factor), Color("e6ce75"))
	_draw_hitbox(foot, Vector2(22, 18) * factor)

func _draw_tree(foot: Vector2, factor: float) -> void:
	draw_rect(Rect2(foot + Vector2(-2, -28) * factor, Vector2(4, 28) * factor), Color("51483b"))
	draw_colored_polygon(PackedVector2Array([foot + Vector2(-11, -22) * factor, foot + Vector2(0, -49) * factor, foot + Vector2(11, -22) * factor]), Color("405b51"))

func _draw_hitbox(foot: Vector2, size: Vector2) -> void:
	draw_rect(Rect2(foot - Vector2(size.x / 2, size.y), size), Color("efdc81"), false, 1.0)

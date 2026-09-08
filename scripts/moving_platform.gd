@tool
extends AnimatableBody2D
@export var travel: Vector2 = Vector2(48, 0)
@export var period: float = 3.2
var origin: Vector2
var elapsed: float = 0.0
func _ready() -> void:
	origin = position
func _physics_process(delta: float) -> void:
	if Engine.is_editor_hint(): return
	elapsed += delta
	position = origin + travel * (0.5 - 0.5 * cos(elapsed * TAU / period))
func _draw() -> void:
	draw_rect(Rect2(-17, -3, 34, 6), Color("584a3d"))
	draw_rect(Rect2(-17, -3, 34, 2), Color("b29c72"))
	for x in [-12, -4, 4, 12]: draw_line(Vector2(x, -2), Vector2(x, 2), Color("302c2e"))

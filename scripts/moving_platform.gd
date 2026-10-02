@tool
extends AnimatableBody2D
@export var travel: Vector2 = Vector2(144, 0)
@export var period: float = 4.0
var origin: Vector2
var elapsed: float = 0.0
func _ready() -> void:
	origin = position
func _physics_process(delta: float) -> void:
	if Engine.is_editor_hint(): return
	elapsed += delta
	position = origin + travel * (0.5 - 0.5 * cos(elapsed * TAU / period))
func _draw() -> void:
	# Ferry planks (tools/art/hazards.py); the top row is the walkable surface.
	draw_texture(preload("res://assets/sprites/prop_ferry.png"), Vector2(-18, -3))

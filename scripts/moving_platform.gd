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
const ART = preload("res://assets/sprites/prop_ferry.png")
var shown_frame: int = -1

func _process(_delta: float) -> void:
	# Ropes and lantern sway (4-frame strip); the walkable top rows never change.
	var frame := int(Time.get_ticks_msec() / 260.0) % 4
	if frame != shown_frame:
		shown_frame = frame
		queue_redraw()

func _draw() -> void:
	# Ferry planks (tools/art/hazards.py); the top row is the walkable surface.
	draw_texture_rect_region(ART, Rect2(-18, -3, 36, 16), Rect2(maxi(shown_frame, 0) * 36, 0, 36, 16))

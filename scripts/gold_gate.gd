@tool
extends Node2D
signal offering_requested
const COST: int = 12
var opened: bool = false
const DUST = preload("res://assets/sprites/vfx_gate_dust.png")
const TORCHES = [Vector2(-18, -70), Vector2(17, -70)]
var lift: float = 0.0
func open() -> void:
	if opened: return
	opened = true
	$Barrier/Shape.set_deferred("disabled", true)
	create_tween().tween_property(self, "lift", 104.0, 0.7).set_trans(Tween.TRANS_SINE)
	$Sound.play()
	_dust()
func _dust() -> void:
	# Dust and gold motes shaken loose at the foot of the gate (tools/art/vfx.py).
	var holder: Node = get_parent()
	if holder == null: return
	var dust := Sprite2D.new()
	dust.texture = DUST
	dust.hframes = 7
	dust.process_mode = Node.PROCESS_MODE_PAUSABLE
	holder.add_child(dust)
	dust.global_position = global_position + Vector2(0, -16)
	var tween := dust.create_tween()
	tween.tween_property(dust, "frame", 6, 0.6)
	tween.tween_callback(dust.queue_free)
func _process(_delta: float) -> void:
	queue_redraw()
	if Engine.is_editor_hint(): return
	if opened: return
	for body in $OfferingArea.get_overlapping_bodies():
		if body is SlicePlayer and not body.dead and Input.is_action_just_pressed("interact"):
			offering_requested.emit()
func player_near() -> bool:
	return $OfferingArea.has_overlapping_bodies()
func _draw() -> void:
	# Stone frame around the 16x100 opening, then the iron panel that lifts (tools/art/hazards.py).
	var art: Texture2D = preload("res://assets/sprites/prop_gold_gate.png")
	draw_texture_rect_region(art, Rect2(-28, -112, 56, 112), Rect2(0, 0, 56, 112))
	var panel_x: float = 72.0 if opened else 56.0
	# The lifted part slides into the lintel and is hidden by the wall.
	var visible_height: float = 100.0 - minf(lift, 100.0)
	if visible_height > 0.0:
		draw_texture_rect_region(art, Rect2(-8, -100, 16, visible_height), Rect2(panel_x, 12 + 100.0 - visible_height, 16, visible_height))
	var ms := Time.get_ticks_msec()
	# Torch flames on the pillars (4 frames, 8x12, strip at x=88,y=16).
	for i in range(TORCHES.size()):
		var f := (ms / 110 + i * 2) % 4
		draw_texture_rect_region(art, Rect2(TORCHES[i].x - 4.0, TORCHES[i].y, 8, 12), Rect2(88 + f * 8, 16, 8, 12))
	# A slow gleam over the keystone seal while the gate is sealed (4 frames, 12x12, x=88,y=0).
	if not opened:
		var t := fposmod(ms / 1000.0, 3.2)
		if t > 2.6:
			var g := mini(3, int((t - 2.6) / 0.15))
			draw_texture_rect_region(art, Rect2(-6, -112 + 0, 12, 12), Rect2(88 + g * 12, 0, 12, 12))

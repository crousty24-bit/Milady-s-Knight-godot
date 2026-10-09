# Source-owned ranged attack. No rewards; terrain blocks arrows and blast impacts.
extends Node2D
signal impacted(at: Vector2)
@export var mode: int = 0 # 0 arrow, 1 committed ground warning / explosion
@export var damage: float = 0.5
@export var motion: Vector2 = Vector2(150, 0)
@export var radius: float = 24.0
@export var warning_duration: float = 1.0
var source_origin: Vector2
var elapsed: float = 0.0
var spent: bool = false

func _physics_process(delta: float) -> void:
	if spent: return
	elapsed += delta
	if mode == 0:
		var destination := global_position + motion * delta
		var ray := PhysicsRayQueryParameters2D.create(global_position, destination, 3)
		var hit := get_world_2d().direct_space_state.intersect_ray(ray)
		if not hit.is_empty():
			var body = hit.collider
			if body is SlicePlayer and not body.dead:
				body.take_damage(damage, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
			_finish(hit.position)
		else:
			global_position = destination
			if elapsed > 5.0: _finish(global_position)
	elif elapsed >= warning_duration:
		var circle := CircleShape2D.new()
		circle.radius = radius
		var query := PhysicsShapeQueryParameters2D.new()
		query.shape = circle
		query.transform = Transform2D(0, global_position + Vector2(0, -radius / 2))
		query.collision_mask = 2
		for hit in get_world_2d().direct_space_state.intersect_shape(query):
			var body = hit.collider
			if body is SlicePlayer and not body.dead:
				var ray := PhysicsRayQueryParameters2D.create(global_position + Vector2(0, -2), body.global_position + Vector2(0, -12), 1)
				if get_world_2d().direct_space_state.intersect_ray(ray).is_empty():
					body.take_damage(damage, Vector2.ZERO, SlicePlayer.DamageSource.PROJECTILE)
		_finish(global_position)
	queue_redraw()

func cancel() -> void:
	spent = true
	set_physics_process(false)
	queue_free()

func _finish(at: Vector2) -> void:
	spent = true
	impacted.emit(at)
	queue_free()

# --- Presentation (RUN-019 Claude art/SFX). The warning frame follows the gameplay timer and
# the drawn rune is the real 48 px contact zone, frozen on the committed ground point.
const ARROW = preload("res://assets/run019/enemies/proj_bone_arrow.png")
const ARROW_IMPACT = preload("res://assets/run019/enemies/vfx_bone_arrow_impact.png")
const ARROW_IMPACT_SFX = preload("res://assets/sounds/sfx_arrow_impact.wav")
const WARNING = preload("res://assets/run019/enemies/vfx_blight_warning.png")
const EXPLOSION = preload("res://assets/run019/enemies/vfx_blight_explosion.png")
const WARNING_SFX = preload("res://assets/sounds/run019/sfx_sorcerer_ground_warning.wav")
const EXPLOSION_SFX = preload("res://assets/sounds/run019/sfx_sorcerer_ground_explosion.wav")
const WARNING_FRAMES = 8
var _art: Sprite2D

func _ready() -> void:
	_art = Sprite2D.new()
	_art.centered = false
	if mode == 0:
		_art.texture = ARROW
		# Tip (13, 2) on the flight point, turned along the motion.
		_art.offset = Vector2(-13, -2)
		_art.rotation = motion.angle()
		_art.z_index = 4
	else:
		_art.texture = WARNING
		_art.hframes = WARNING_FRAMES
		_art.offset = Vector2(-28, -36)
		_art.z_index = -1
		if not is_equal_approx(radius, 24.0): _art.scale = Vector2.ONE * radius / 24.0
		# Attached: the owner positions this node right after adding it; ends with the warning.
		Run019Art.voice(self, WARNING_SFX, -6.0).play()
	add_child(_art)
	impacted.connect(_on_impacted_art)

func _process(_delta: float) -> void:
	if mode == 1 and _art != null:
		_art.frame = clampi(int(elapsed / maxf(warning_duration, 0.001) * WARNING_FRAMES), 0, WARNING_FRAMES - 1)

func _on_impacted_art(at: Vector2) -> void:
	if mode == 0:
		Run019Art.fx(self, ARROW_IMPACT, Vector2i(16, 16), 20.0, at, Vector2(0.5, 0.5), motion.x < 0.0, ARROW_IMPACT_SFX, -6.0)
	else:
		Run019Art.fx(self, EXPLOSION, Vector2i(64, 56), 16.0, at, Vector2(0.5, 52.0 / 56.0), false, EXPLOSION_SFX, -4.0)

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

func _draw() -> void:
	if mode == 0:
		var direction := motion.normalized()
		draw_line(-direction * 6, direction * 6, Color("f4ddaa"), 2)
	else:
		draw_rect(Rect2(Vector2(-radius, -3), Vector2(radius * 2, 3)), Color(0.7, 0.2, 0.65, 0.5))
		draw_arc(Vector2(0, -radius / 2), radius, 0, TAU * minf(elapsed / warning_duration, 1), 24, Color("f7a4dd"), 2)

extends Node2D
signal impacted(at: Vector2, player_hit: bool)
@export_range(1.0, 2000.0) var speed: float = 160.0
@export_range(1.0, 2000.0) var reach: float = 320.0
var direction := Vector2.RIGHT
var distance_travelled: float = 0.0

func setup(aim: Vector2, travel_speed: float = 160.0, max_range: float = 320.0) -> void:
	direction = aim.normalized() if not aim.is_zero_approx() else Vector2.RIGHT
	speed = travel_speed
	reach = max_range
	rotation = direction.angle()

func _physics_process(delta: float) -> void:
	if is_queued_for_deletion(): return
	var step := minf(speed * delta, reach - distance_travelled)
	var next := global_position + direction * step
	# Continuous swept point: cannot tunnel through a wall/player between frames.
	var query := PhysicsRayQueryParameters2D.create(global_position, next, 1 | 2)
	query.hit_from_inside = true
	var hit := get_world_2d().direct_space_state.intersect_ray(query)
	if not hit.is_empty():
		global_position = hit.position
		var body: Object = hit.collider
		if body is SlicePlayer and not body.dead:
			body.take_damage(1.0, Vector2.ZERO, SlicePlayer.DamageSource.TRAP_PROJECTILE)
		impacted.emit(global_position, body is SlicePlayer)
		queue_free()
		return
	global_position = next
	distance_travelled += step
	if distance_travelled >= reach: queue_free()

func _draw() -> void:
	draw_line(Vector2(-5, 0), Vector2.ZERO, Color.ORANGE_RED, 2.0)

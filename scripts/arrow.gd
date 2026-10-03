extends Node2D
signal impacted(at: Vector2, enemy: bool)

const DAMAGE = 1.0
const RANGE = 20.0 * 16.0
# Technical travel speed: 320 px/s; the full range takes one active second.
const SPEED = 320.0
const COLLISION_MASK = 1 | 4
var direction: int = 1
var origin := Vector2.ZERO
var distance_travelled: float = 0.0

func setup(aim: int) -> void:
	direction = -1 if aim < 0 else 1
	origin = global_position

func _physics_process(delta: float) -> void:
	if is_queued_for_deletion():
		return
	var step := minf(SPEED * delta, RANGE - distance_travelled)
	var next := global_position + Vector2(direction * step, 0.0)
	var query := PhysicsRayQueryParameters2D.create(global_position, next, COLLISION_MASK)
	query.hit_from_inside = true
	var hit := get_world_2d().direct_space_state.intersect_ray(query)
	if not hit.is_empty():
		global_position = hit.position
		var body: Object = hit.collider
		if body.has_method("take_damage"):
			body.take_damage(DAMAGE, Vector2(direction * 60.0, -55.0), SlicePlayer.DamageSource.PROJECTILE)
		impacted.emit(global_position, body.has_method("take_damage"))
		queue_free()
		return
	global_position = next
	distance_travelled += step
	if distance_travelled >= RANGE - 0.000001:
		queue_free()

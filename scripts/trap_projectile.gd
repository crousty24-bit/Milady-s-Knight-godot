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

# --- Presentation (RUN-019 Claude art/SFX): node rotation already follows the aim.
const BOLT = preload("res://assets/run019/world/proj_turret_bolt.png")
const IMPACT = preload("res://assets/run019/world/vfx_turret_impact.png")
const IMPACT_SFX = preload("res://assets/sounds/run019/sfx_turret_projectile_impact.wav")

func _ready() -> void:
	var art := Run019Art.sprite(self, OneShotFx.strip_frames(BOLT, Vector2i(12, 6), 12.0, true), Vector2(11, 3), &"default", 4)
	art.play(&"default")
	impacted.connect(func(at: Vector2, player_hit: bool) -> void:
		Run019Art.fx(self, IMPACT, Vector2i(16, 16), 20.0, at, Vector2(0.5, 0.5), false, IMPACT_SFX, -4.0 if player_hit else -10.0))

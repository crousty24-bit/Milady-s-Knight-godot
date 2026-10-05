extends Node2D
signal impacted(at: Vector2, enemy: bool)

const DAMAGE = 1.0
const RANGE = 20.0 * 16.0
# Technical travel speed: 320 px/s; the full range takes one active second.
const SPEED = 320.0
const COLLISION_MASK = 1 | 4
var damage: float = DAMAGE
var reach: float = RANGE
var direction: int = 1
var origin := Vector2.ZERO
var distance_travelled: float = 0.0
# RUN-016 presentation (Claude): sprite with its tip on the travelling point, impact effects.
const ARROW_TEXTURE = preload("res://assets/sprites/proj_arrow.png")
const IMPACT_FX = preload("res://assets/sprites/vfx_arrow_impact.png")
const HIT_FX = preload("res://assets/sprites/vfx_arrow_hit.png")
const IMPACT_SFX = preload("res://assets/sounds/sfx_arrow_impact.wav")
var _sprite: Sprite2D

func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = ARROW_TEXTURE
	_sprite.centered = false
	add_child(_sprite)
	_orient_sprite()
	impacted.connect(_on_impacted_fx)

func _process(_delta: float) -> void:
	_orient_sprite()

func _orient_sprite() -> void:
	_sprite.flip_h = direction < 0
	_sprite.offset = Vector2(0.0 if direction < 0 else -16.0, -2.0)

func _on_impacted_fx(at: Vector2, enemy: bool) -> void:
	var world: Node = get_tree().current_scene if get_tree().current_scene != null else get_parent()
	OneShotFx.spawn(world, HIT_FX if enemy else IMPACT_FX, Vector2i(16, 16), 20.0, at, direction < 0, Vector2(0.5, 0.5), IMPACT_SFX, -6.0 if enemy else -2.0)

func setup(aim: int, hit_damage: float = DAMAGE, max_range: float = RANGE) -> void:
	damage = hit_damage
	reach = max_range
	direction = -1 if aim < 0 else 1
	origin = global_position

func _physics_process(delta: float) -> void:
	if is_queued_for_deletion():
		return
	var step := minf(SPEED * delta, reach - distance_travelled)
	var next := global_position + Vector2(direction * step, 0.0)
	var query := PhysicsRayQueryParameters2D.create(global_position, next, COLLISION_MASK)
	query.hit_from_inside = true
	var hit := get_world_2d().direct_space_state.intersect_ray(query)
	if not hit.is_empty():
		global_position = hit.position
		var body: Object = hit.collider
		if body.has_method("take_damage"):
			body.take_damage(damage, Vector2(direction * 60.0, -55.0), SlicePlayer.DamageSource.PROJECTILE)
		impacted.emit(global_position, body.has_method("take_damage"))
		queue_free()
		return
	global_position = next
	distance_travelled += step
	if distance_travelled >= reach - 0.000001:
		queue_free()

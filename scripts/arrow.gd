extends Node2D
signal impacted(at: Vector2, enemy: bool)

const DAMAGE = 1.0
const RANGE = 12.0 * 16.0
# Technical travel speed: 320 px/s; base Longbow range takes 0.6 active seconds.
const SPEED = 320.0
const COLLISION_MASK = 1 | 4 | 16
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
# RUN-018 presentation (Claude): Throwing Knives look, set once by the shooter at the throw.
const KNIFE_TEXTURE = preload("res://assets/run018/world/proj_knife.png")
const KNIFE_IMPACT_FX = preload("res://assets/run018/world/vfx_knife_impact.png")
const KNIFE_HIT_FX = preload("res://assets/run018/world/vfx_knife_hit.png")
const KNIFE_IMPACT_SFX = preload("res://assets/sounds/run018/sfx_knife_impact.wav")
var look: String = "arrow"

func set_look(kind: String) -> void:
	look = kind
	if _sprite != null:
		_sprite.texture = KNIFE_TEXTURE if look == "knife" else ARROW_TEXTURE
		_orient_sprite()

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
	var length := _sprite.texture.get_width()
	_sprite.offset = Vector2(0.0 if direction < 0 else -float(length), -2.0)

func _on_impacted_fx(at: Vector2, enemy: bool) -> void:
	var world: Node = get_tree().current_scene if get_tree().current_scene != null else get_parent()
	var knife := look == "knife"
	var strip: Texture2D = (KNIFE_HIT_FX if knife else HIT_FX) if enemy else (KNIFE_IMPACT_FX if knife else IMPACT_FX)
	OneShotFx.spawn(world, strip, Vector2i(16, 16), 20.0, at, direction < 0, Vector2(0.5, 0.5), KNIFE_IMPACT_SFX if knife else IMPACT_SFX, -6.0 if enemy else -2.0)

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
	query.collide_with_areas = true
	var hit := get_world_2d().direct_space_state.intersect_ray(query)
	if not hit.is_empty():
		global_position = hit.position
		var body: Object = hit.collider
		if body.has_method("receive_player_attack"):
			body.receive_player_attack(damage, SlicePlayer.DamageSource.PROJECTILE)
		elif body.has_method("take_damage"):
			body.take_damage(damage, Vector2(direction * 60.0, -55.0), SlicePlayer.DamageSource.PROJECTILE)
		impacted.emit(global_position, body.has_method("take_damage"))
		queue_free()
		return
	global_position = next
	distance_travelled += step
	if distance_travelled >= reach - 0.000001:
		queue_free()

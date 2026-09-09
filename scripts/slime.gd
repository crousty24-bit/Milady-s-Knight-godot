class_name SliceSlime
extends CharacterBody2D
signal defeated(bonus: int, at: Vector2)
enum Kind { GREEN, PURPLE }
const GREEN_PATROL_SPEED = 30.0
const PURPLE_PATROL_SPEED = 34.0
@export var patrol_left: float = -40.0
@export var patrol_right: float = 40.0
@export var variant: Kind = Kind.GREEN
@export_range(0, 1000000, 1) var bonus_reward: int = 1
var health: int = 3
var direction: int = -1
var origin_x: float
var stagger: float = 0.0
var dead: bool = false
@onready var sprite: AnimatedSprite2D = $Sprite

func _ready() -> void:
	origin_x = position.x
	health = 4 if variant == Kind.PURPLE else 3
	sprite.play("purple" if variant == Kind.PURPLE else "green")

func _physics_process(delta: float) -> void:
	if dead: return
	stagger = maxf(0.0, stagger - delta)
	velocity.y = minf(velocity.y + 760.0 * delta, 400.0)
	if stagger <= 0.0:
		if position.x < origin_x + patrol_left: direction = 1
		if position.x > origin_x + patrol_right: direction = -1
		$EdgeRay.position.x = direction * 10
		$EdgeRay.force_raycast_update()
		if is_on_wall() or (is_on_floor() and not $EdgeRay.is_colliding()): direction *= -1
		velocity.x = direction * (PURPLE_PATROL_SPEED if variant == Kind.PURPLE else GREEN_PATROL_SPEED)
	move_and_slide()
	sprite.flip_h = direction > 0
	sprite.modulate = Color("fff1a6") if stagger > 0.0 else Color.WHITE
	if stagger > 0.0: return
	for body in $ContactArea.get_overlapping_bodies():
		if body is SlicePlayer:
			body.take_damage(1, Vector2(100.0 if body.global_position.x > global_position.x else -100.0, -150.0))

func take_damage(amount: int, impulse: Vector2) -> void:
	if dead: return
	health = maxi(0, health - amount)
	velocity = impulse
	stagger = 0.12
	$HitSound.play()
	if health <= 0:
		dead = true
		defeated.emit(bonus_reward, global_position)
		$CollisionShape2D.set_deferred("disabled", true)
		$ContactArea/Shape.set_deferred("disabled", true)
		var tween = create_tween()
		tween.tween_property(sprite, "scale", Vector2(1.4, 0.25), 0.13)
		tween.parallel().tween_property(sprite, "modulate:a", 0.0, 0.22)
		tween.tween_callback(queue_free)

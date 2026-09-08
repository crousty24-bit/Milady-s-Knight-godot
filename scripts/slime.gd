class_name SliceSlime
extends CharacterBody2D
@export var patrol_left: float = -40.0
@export var patrol_right: float = 40.0
@export var corrupted: bool = false
var health: int = 2
var direction: int = -1
var origin_x: float
var stagger: float = 0.0
var dead: bool = false
@onready var sprite: AnimatedSprite2D = $Sprite

func _ready() -> void:
	origin_x = position.x
	if corrupted:
		sprite.modulate = Color("c594c9")

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
		velocity.x = direction * 27.0
	move_and_slide()
	sprite.flip_h = direction > 0
	sprite.modulate = Color("fff1a6") if stagger > 0.0 else (Color("c594c9") if corrupted else Color.WHITE)
	for body in $ContactArea.get_overlapping_bodies():
		if body is SlicePlayer:
			body.take_damage(1, Vector2(100.0 if body.global_position.x > global_position.x else -100.0, -150.0))

func take_damage(amount: int, impulse: Vector2) -> void:
	if dead: return
	health -= amount
	velocity = impulse
	stagger = 0.23
	$HitSound.play()
	if health <= 0:
		dead = true
		$CollisionShape2D.set_deferred("disabled", true)
		$ContactArea/Shape.set_deferred("disabled", true)
		var tween = create_tween()
		tween.tween_property(sprite, "scale", Vector2(1.4, 0.25), 0.13)
		tween.parallel().tween_property(sprite, "modulate:a", 0.0, 0.22)
		tween.tween_callback(queue_free)

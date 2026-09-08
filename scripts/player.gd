class_name SlicePlayer
extends CharacterBody2D

signal health_changed(value: int)
signal died
const SPEED = 105.0
const GRAVITY = 760.0
const JUMP_SPEED = -255.0
const ATTACK_DURATION = 0.32
var health: int = 3
var facing: int = 1
var dead: bool = false
var controls_enabled: bool = true
var coyote: float = 0.0
var jump_buffer: float = 0.0
var invulnerability: float = 0.0
var knockback_time: float = 0.0
var attack_time: float = 0.0
var hit_targets: Array[int] = []
@onready var sprite: AnimatedSprite2D = $Sprite
@onready var sword: Area2D = $AttackArea

func _physics_process(delta: float) -> void:
	invulnerability = maxf(0.0, invulnerability - delta)
	knockback_time = maxf(0.0, knockback_time - delta)
	velocity.y = minf(velocity.y + GRAVITY * delta, 420.0)
	if dead:
		velocity.x = move_toward(velocity.x, 0.0, 600.0 * delta)
		move_and_slide()
		return
	if is_on_floor():
		coyote = 0.10
	else:
		coyote = maxf(0.0, coyote - delta)
	jump_buffer = maxf(0.0, jump_buffer - delta)
	var direction: float = Input.get_axis("move_left", "move_right") if controls_enabled else 0.0
	if controls_enabled and Input.is_action_just_pressed("jump"):
		jump_buffer = 0.12
	if jump_buffer > 0.0 and coyote > 0.0:
		velocity.y = JUMP_SPEED
		jump_buffer = 0.0
		coyote = 0.0
		$JumpSound.play()
	if controls_enabled and Input.is_action_just_released("jump") and not Input.is_action_pressed("jump") and velocity.y < -90.0:
		velocity.y *= 0.45
	if direction != 0.0 and attack_time <= 0.0:
		facing = 1 if direction > 0.0 else -1
	if knockback_time <= 0.0:
		velocity.x = move_toward(velocity.x, direction * SPEED, 1100.0 * delta)
	if controls_enabled and Input.is_action_just_pressed("attack") and attack_time <= 0.0:
		attack_time = ATTACK_DURATION
		hit_targets.clear()
		$SwingSound.play()
	attack_time = maxf(0.0, attack_time - delta)
	sword.position.x = 17.0 * facing
	if attack_time < 0.25 and attack_time > 0.11:
		for body in sword.get_overlapping_bodies():
			if body.has_method("take_damage") and not hit_targets.has(body.get_instance_id()):
				hit_targets.append(body.get_instance_id())
				body.take_damage(1, Vector2(facing * 90.0, -100.0))
	sprite.flip_h = facing < 0
	sprite.modulate = Color(1.0, 0.65, 0.65, 0.45 if int(invulnerability * 18) % 2 == 0 else 1.0) if invulnerability > 0.0 else Color.WHITE
	if attack_time > 0.0:
		sprite.play("jump")
	elif not is_on_floor():
		sprite.play("jump")
	else:
		sprite.play("run" if absf(velocity.x) > 5.0 else "idle")
	move_and_slide()
	queue_redraw()
	if global_position.y > 340.0:
		die()

func take_damage(amount: int, impulse: Vector2 = Vector2.ZERO) -> void:
	if dead or invulnerability > 0.0:
		return
	health = maxi(0, health - amount)
	health_changed.emit(health)
	$HurtSound.play()
	if health == 0:
		die()
		return
	invulnerability = 0.85
	knockback_time = 0.16
	attack_time = 0.0
	velocity = impulse

func die() -> void:
	if dead:
		return
	dead = true
	health = 0
	attack_time = 0.0
	sprite.modulate = Color.WHITE
	sprite.play("dead")
	health_changed.emit(0)
	died.emit()
	queue_redraw()

func _draw() -> void:
	if attack_time <= 0.0:
		return
	var progress: float = 1.0 - attack_time / ATTACK_DURATION
	var angle: float = lerpf(-1.5, 1.2, progress)
	var origin = Vector2(4.0 * facing, -12.0)
	var tip = origin + Vector2(cos(angle) * facing, sin(angle)) * 24.0
	if attack_time < 0.25 and attack_time > 0.11:
		for i in range(4):
			var a: float = angle - i * 0.16
			draw_line(origin + Vector2(cos(a) * facing, sin(a)) * 12.0, origin + Vector2(cos(a) * facing, sin(a)) * 27.0, Color(0.95, 0.8, 0.44, 0.7 - i * 0.15), 2.0)
	draw_line(origin, tip, Color("e9e4c5"), 2.0)
	draw_line(origin, origin - Vector2(cos(angle) * facing, sin(angle)) * 5.0, Color("ae7c42"), 3.0)

class_name SlicePlayer
extends CharacterBody2D
enum MotionState { GROUND, AIR, WALL_SLIDE, DEAD }

signal health_changed(value: float, maximum: float)
signal died
enum DamageSource { CONTACT_MELEE, PROJECTILE, SOLID_TRAP, FLAME, SWARM, VOID }
const SPEED = 105.0
const GRAVITY = 760.0
const JUMP_SPEED = -255.0
const DOUBLE_JUMP_SPEED = -225.0
const WALL_SLIDE_SPEED = 35.0
const WALL_JUMP_SPEED = 110.0
const GRIPPABLE_MASK = 8
const ATTACK_DURATION = 0.28
# Keep the original windup, contact and recovery proportions as the cycle changes.
const ATTACK_HIT_START_TIME = ATTACK_DURATION * (0.25 / 0.32)
const ATTACK_HIT_END_TIME = ATTACK_DURATION * (0.11 / 0.32)
const INVULNERABILITY_DURATION = 0.85
const HIT_STUN_DURATION = 0.18
const KNOCKBACK_DURATION = 0.16
var max_health_units: int = 30
var health_units: int = 30
var health: float:
	get: return HealthUnits.to_hp(health_units)
var max_health: float:
	get: return HealthUnits.to_hp(max_health_units)
var facing: int = 1
var attack_facing: int = 1
var dead: bool = false
var controls_enabled: bool = true
var coyote: float = 0.0
var jump_buffer: float = 0.0
var invulnerability: float = 0.0
var knockback_time: float = 0.0
var hit_stun_time: float = 0.0
var attack_time: float = 0.0
var hit_targets: Array[int] = []
var can_double_jump: bool = false
var wall_jump_lockout: bool = false
var jump_flash: float = 0.0
var jump_effect_origin := Vector2.ZERO
var motion_state: MotionState = MotionState.AIR
var wall_normal: float = 0.0
var blocked_wall_normal: float = 0.0
var wall_detach_time: float = 0.0
var wall_control_time: float = 0.0
var attack_cancelled: bool = false
@onready var sprite: AnimatedSprite2D = $Sprite
@onready var sword: Area2D = $AttackArea

func _physics_process(delta: float) -> void:
	invulnerability = maxf(0.0, invulnerability - delta)
	knockback_time = maxf(0.0, knockback_time - delta)
	hit_stun_time = maxf(0.0, hit_stun_time - delta)
	jump_flash = maxf(0.0, jump_flash - delta)
	wall_detach_time = maxf(0.0, wall_detach_time - delta)
	wall_control_time = maxf(0.0, wall_control_time - delta)
	velocity.y = minf(velocity.y + GRAVITY * delta, 420.0)
	if dead:
		motion_state = MotionState.DEAD
		velocity.x = move_toward(velocity.x, 0.0, 600.0 * delta)
		move_and_slide()
		return
	if is_on_floor() and velocity.y >= 0.0:
		coyote = 0.10
		can_double_jump = false
		wall_jump_lockout = false
	else:
		coyote = maxf(0.0, coyote - delta)
	jump_buffer = maxf(0.0, jump_buffer - delta)
	var direction: float = Input.get_axis("move_left", "move_right") if controls_enabled else 0.0
	_update_wall_state(direction)
	if controls_enabled and knockback_time <= 0.0 and Input.is_action_just_pressed("jump"):
		jump_buffer = 0.12
	if knockback_time <= 0.0 and jump_buffer > 0.0 and coyote > 0.0:
		velocity.y = JUMP_SPEED
		jump_buffer = 0.0
		coyote = 0.0
		can_double_jump = true
		$JumpSound.pitch_scale = 1.0
		$JumpSound.play()
	elif knockback_time <= 0.0 and jump_buffer > 0.0 and wall_normal != 0.0 and not is_on_floor():
		velocity = Vector2(wall_normal * WALL_JUMP_SPEED, JUMP_SPEED)
		facing = int(wall_normal)
		blocked_wall_normal = wall_normal
		wall_control_time = 0.07
		wall_detach_time = 0.20
		wall_jump_lockout = true
		can_double_jump = false
		coyote = 0.0
		jump_buffer = 0.0
		motion_state = MotionState.AIR
		$JumpSound.pitch_scale = 1.12
		$JumpSound.play()
	elif knockback_time <= 0.0 and jump_buffer > 0.0 and can_double_jump and not wall_jump_lockout:
		velocity.y = DOUBLE_JUMP_SPEED
		jump_buffer = 0.0
		can_double_jump = false
		jump_flash = 0.22
		jump_effect_origin = global_position
		$JumpSound.pitch_scale = 1.35
		$JumpSound.play()
	if controls_enabled and Input.is_action_just_released("jump") and not Input.is_action_pressed("jump") and velocity.y < -90.0:
		velocity.y *= 0.45
	if motion_state == MotionState.WALL_SLIDE:
		velocity.y = minf(velocity.y, WALL_SLIDE_SPEED)
	if direction != 0.0 and wall_control_time <= 0.0 and (attack_time >= ATTACK_HIT_START_TIME or attack_time <= ATTACK_HIT_END_TIME):
		facing = 1 if direction > 0.0 else -1
		if attack_time >= ATTACK_HIT_START_TIME or attack_time <= 0.0:
			attack_facing = facing
	if knockback_time <= 0.0 and wall_control_time <= 0.0:
		velocity.x = move_toward(velocity.x, direction * SPEED, 2100.0 * delta)
	if controls_enabled and hit_stun_time <= 0.0 and Input.is_action_pressed("attack") and attack_time <= 0.0 and motion_state != MotionState.WALL_SLIDE:
		attack_time = ATTACK_DURATION
		attack_facing = facing
		attack_cancelled = false
		hit_targets.clear()
		$SwingSound.play()
	attack_time = maxf(0.0, attack_time - delta)
	sprite.flip_h = facing < 0
	sprite.modulate = Color(1.0, 0.65, 0.65, 0.45 if int(invulnerability * 18) % 2 == 0 else 1.0) if invulnerability > 0.0 else Color.WHITE
	if attack_time > 0.0:
		sprite.play("jump")
	elif not is_on_floor():
		sprite.play("jump")
	else:
		sprite.play("run" if absf(velocity.x) > 5.0 else "idle")
	move_and_slide()
	_update_wall_state(direction)
	_update_sword()
	queue_redraw()
	if global_position.y > 340.0:
		die()

func _update_wall_state(direction: float) -> void:
	wall_normal = 0.0
	if is_on_floor() and velocity.y >= 0.0:
		motion_state = MotionState.GROUND
		return
	# Two probes cover the straight sides of the capsule, not its rounded feet.
	for side in [-1.0, 1.0]:
		if wall_detach_time > 0.0 and -side == blocked_wall_normal:
			continue
		for height in [-6.0, -12.0]:
			var from := global_position + Vector2(0, height)
			var query := PhysicsRayQueryParameters2D.create(from, from + Vector2(side * 5.5, 0), GRIPPABLE_MASK)
			var hit := get_world_2d().direct_space_state.intersect_ray(query)
			if not hit.is_empty() and absf(hit.normal.x) > 0.9:
				wall_normal = hit.normal.x
				break
		if wall_normal != 0.0:
			break
	if wall_normal != 0.0 and velocity.y >= 0.0 and direction != wall_normal and knockback_time <= 0.0:
		motion_state = MotionState.WALL_SLIDE
		velocity.y = minf(velocity.y, WALL_SLIDE_SPEED)
		if attack_time > 0.0:
			attack_cancelled = true
	else:
		motion_state = MotionState.AIR

func take_damage(amount: float, impulse: Vector2 = Vector2.ZERO, source: int = DamageSource.CONTACT_MELEE) -> void:
	if dead:
		return
	if source == DamageSource.VOID:
		die()
		return
	if invulnerability > 0.0 or amount <= 0.0:
		return
	health_units = maxi(0, health_units - HealthUnits.from_hp(amount))
	$HurtSound.play()
	if health_units == 0:
		die()
		return
	health_changed.emit(health, max_health)
	invulnerability = INVULNERABILITY_DURATION
	var has_knockback: bool = source == DamageSource.CONTACT_MELEE or source == DamageSource.SOLID_TRAP or source == DamageSource.FLAME
	var interrupts_attack: bool = source == DamageSource.CONTACT_MELEE or source == DamageSource.PROJECTILE
	if source == DamageSource.CONTACT_MELEE:
		hit_stun_time = HIT_STUN_DURATION
	if interrupts_attack:
		attack_time = 0.0
		attack_cancelled = true
	if has_knockback:
		knockback_time = KNOCKBACK_DURATION
		jump_buffer = 0.0
		wall_control_time = 0.0
		velocity = impulse

func heal(amount: float) -> float:
	if dead or amount <= 0.0:
		return 0.0
	var before := health_units
	health_units = mini(max_health_units, health_units + HealthUnits.from_hp(amount))
	if health_units != before:
		health_changed.emit(health, max_health)
	return HealthUnits.to_hp(health_units - before)

func die() -> void:
	if dead:
		return
	dead = true
	motion_state = MotionState.DEAD
	health_units = 0
	attack_time = 0.0
	hit_stun_time = 0.0
	knockback_time = 0.0
	sprite.modulate = Color.WHITE
	sprite.play("dead")
	health_changed.emit(0.0, max_health)
	died.emit()
	queue_redraw()

func _update_sword() -> void:
	var angle: float = lerpf(-1.5, 1.2, 1.0 - attack_time / ATTACK_DURATION)
	var blade_direction := Vector2(cos(angle) * attack_facing, sin(angle))
	var hand := Vector2(4.0 * attack_facing, -10.0)
	sword.position = hand + blade_direction * 12.0
	sword.rotation = blade_direction.angle()
	if attack_cancelled or dead or attack_time >= ATTACK_HIT_START_TIME or attack_time <= ATTACK_HIT_END_TIME:
		return
	var query := PhysicsShapeQueryParameters2D.new()
	query.shape = $AttackArea/Shape.shape
	query.transform = sword.global_transform
	query.collision_mask = 4
	for hit in get_world_2d().direct_space_state.intersect_shape(query):
		var body = hit.collider
		if not body.has_method("take_damage") or hit_targets.has(body.get_instance_id()):
			continue
		var ray := PhysicsRayQueryParameters2D.create(to_global(hand), body.global_position + Vector2(0, -6), 1)
		if not get_world_2d().direct_space_state.intersect_ray(ray).is_empty():
			continue
		hit_targets.append(body.get_instance_id())
		body.take_damage(1, Vector2(attack_facing * 60.0, -55.0))

func _draw() -> void:
	if motion_state == MotionState.WALL_SLIDE:
		var dust_y: float = float(Engine.get_physics_frames() % 12)
		draw_rect(Rect2(-wall_normal * 6.0 - 1.0, -5.0 + dust_y, 2, 2), Color("b8ad94"))
	if jump_flash > 0.0:
		var radius: float = 4.0 + (1.0 - jump_flash / 0.22) * 12.0
		draw_arc(to_local(jump_effect_origin), radius, 0, TAU, 16, Color(0.75, 0.87, 0.95, jump_flash / 0.22), 1.0)
	if attack_time <= 0.0 or attack_cancelled:
		return
	var progress: float = 1.0 - attack_time / ATTACK_DURATION
	var angle: float = lerpf(-1.5, 1.2, progress)
	var origin = Vector2(4.0 * attack_facing, -10.0)
	var tip = origin + Vector2(cos(angle) * attack_facing, sin(angle)) * 24.0
	if attack_time < ATTACK_HIT_START_TIME and attack_time > ATTACK_HIT_END_TIME:
		for i in range(4):
			var a: float = angle - i * 0.16
			draw_line(origin + Vector2(cos(a) * attack_facing, sin(a)) * 12.0, origin + Vector2(cos(a) * attack_facing, sin(a)) * 27.0, Color(0.95, 0.8, 0.44, 0.7 - i * 0.15), 2.0)
	draw_line(origin, tip, Color("e9e4c5"), 2.0)
	draw_line(origin, origin - Vector2(cos(angle) * attack_facing, sin(angle)) * 5.0, Color("ae7c42"), 3.0)

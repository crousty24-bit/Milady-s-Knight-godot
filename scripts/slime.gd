class_name SliceSlime
extends CharacterBody2D
signal defeated(bonus: int, at: Vector2)
signal health_changed(value: float, maximum: float)
enum Kind { GREEN, PURPLE, RED }
const GREEN_PATROL_SPEED = 30.0
const PURPLE_PATROL_SPEED = 34.0
const RED_PATROL_SPEED = 38.0
@export var patrol_left: float = -40.0
@export var patrol_right: float = 40.0
@export var variant: Kind = Kind.GREEN
@export_range(0, 1000000, 1) var bonus_reward: int = 1
var max_health_units: int = 10
var health_units: int = 10
var health: float:
	get: return HealthUnits.to_hp(health_units)
var max_health: float:
	get: return HealthUnits.to_hp(max_health_units)
var direction: int = -1
var origin_x: float
const KNOCKBACK_DURATION = 0.12
const SPLASH = preload("res://assets/sprites/vfx_slime_splash.png")
const HIT_SPRAY = preload("res://assets/sprites/vfx_slime_hit.png")
# RUN-019 Red: own sheet with the green layout (tools/art/run019/enemies_blobs.py).
const RED_SHEET = preload("res://assets/run019/enemies/enemy_slime_red.png")
const RED_SPLASH = preload("res://assets/run019/enemies/vfx_slime_splash_red.png")
const RED_SPRAY = preload("res://assets/run019/enemies/vfx_slime_hit_red.png")
const RED_ANIMS = {&"red": [0, 8, 10, true], &"red_hit": [8, 2, 16, true], &"red_death": [10, 4, 20, false]}
var knockback_time: float = 0.0
var dead: bool = false
@onready var sprite: AnimatedSprite2D = $Sprite

func _ready() -> void:
	origin_x = position.x
	max_health_units = 10 if variant == Kind.GREEN else 20
	health_units = max_health_units
	if variant == Kind.RED: sprite.sprite_frames = Run019Art.frames(RED_SHEET, Vector2i(24, 24), RED_ANIMS)
	sprite.play(_base_animation())
	sprite.modulate = _base_tint()
	if variant == Kind.RED:
		var ancestor := get_parent()
		while ancestor != null:
			if ancestor.has_method("register_enemy"):
				ancestor.register_enemy(self)
				break
			ancestor = ancestor.get_parent()

func _base_tint() -> Color:
	return Color.WHITE

func _base_animation() -> StringName:
	return &"purple" if variant == Kind.PURPLE else (&"red" if variant == Kind.RED else &"green")

func _physics_process(delta: float) -> void:
	if dead: return
	knockback_time = maxf(0.0, knockback_time - delta)
	velocity.y = minf(velocity.y + 760.0 * delta, 400.0)
	if knockback_time <= 0.0:
		if position.x < origin_x + patrol_left: direction = 1
		if position.x > origin_x + patrol_right: direction = -1
		$EdgeRay.position.x = direction * 10
		$EdgeRay.force_raycast_update()
		if is_on_wall() or (is_on_floor() and not $EdgeRay.is_colliding()): direction *= -1
		velocity.x = direction * (PURPLE_PATROL_SPEED if variant == Kind.PURPLE else (RED_PATROL_SPEED if variant == Kind.RED else GREEN_PATROL_SPEED))
	move_and_slide()
	sprite.flip_h = direction > 0
	# Recoil frames only while the knockback lasts (tools/art/slime_art.py).
	var wanted: StringName = _base_animation() if knockback_time <= 0.0 else StringName(String(_base_animation()) + "_hit")
	if sprite.animation != wanted: sprite.play(wanted)
	sprite.modulate = Color("fff1a6") if knockback_time > 0.0 else _base_tint()
	for body in $ContactArea.get_overlapping_bodies():
		if body is SlicePlayer:
			body.take_damage(1.5 if variant == Kind.RED else (1.0 if variant == Kind.PURPLE else 0.5), Vector2(100.0 if body.global_position.x > global_position.x else -100.0, -150.0), SlicePlayer.DamageSource.CONTACT_MELEE)

func take_damage(amount: float, impulse: Vector2, _source: int = SlicePlayer.DamageSource.CONTACT_MELEE) -> void:
	if dead or amount <= 0.0: return
	health_units = maxi(0, health_units - HealthUnits.from_hp(amount))
	health_changed.emit(health, max_health)
	velocity = impulse
	knockback_time = KNOCKBACK_DURATION
	if health_units > 0:
		$HitSound.play()
		_spray(impulse)
	else:
		dead = true
		_play_detached($HitSound)
		_play_detached($DeathSound)
		defeated.emit(bonus_reward, global_position)
		_splash()
		$CollisionShape2D.set_deferred("disabled", true)
		$ContactArea/Shape.set_deferred("disabled", true)
		# Collapse animation (bloat, burst, puddle) instead of a scaled sprite, then fade out.
		sprite.play(StringName(String(_base_animation()) + "_death"))
		var tween = create_tween()
		tween.tween_property(sprite, "modulate:a", 0.0, 0.1).set_delay(0.12)
		tween.tween_callback(queue_free)

func _splash() -> void:
	# Goo burst outlives the slime, in the scene like its detached sounds.
	var holder: Node = get_tree().current_scene if get_tree().current_scene != null else get_parent()
	if holder == null or holder == self: return
	var splash := Sprite2D.new()
	splash.texture = RED_SPLASH if variant == Kind.RED else SPLASH
	splash.hframes = 6
	splash.vframes = 1 if variant == Kind.RED else 2
	var first: int = 6 if variant == Kind.PURPLE else 0
	splash.frame = first
	splash.process_mode = Node.PROCESS_MODE_PAUSABLE
	holder.add_child(splash)
	# 40x24 frames: the bottom edge sits on the ground where the slime stood.
	splash.global_position = global_position + Vector2(0, -12)
	var tween := splash.create_tween()
	tween.tween_property(splash, "frame", first + 5, 0.36)
	tween.tween_interval(0.06)
	tween.tween_callback(splash.queue_free)

func _spray(impulse: Vector2) -> void:
	# Short goo spray away from the blow on a non-lethal hit (tools/art/vfx.py).
	var holder: Node = get_tree().current_scene if get_tree().current_scene != null else get_parent()
	if holder == null or holder == self: return
	var dir: float = -1.0 if impulse.x < 0.0 else 1.0
	var spray := Sprite2D.new()
	spray.texture = RED_SPRAY if variant == Kind.RED else HIT_SPRAY
	spray.hframes = 4
	spray.vframes = 1 if variant == Kind.RED else 2
	var first: int = 4 if variant == Kind.PURPLE else 0
	spray.frame = first
	spray.flip_h = dir < 0.0
	spray.process_mode = Node.PROCESS_MODE_PAUSABLE
	holder.add_child(spray)
	spray.global_position = global_position + Vector2(5.0 * dir, -10.0)
	var tween := spray.create_tween()
	tween.tween_property(spray, "frame", first + 3, 0.18)
	tween.tween_callback(spray.queue_free)

func _play_detached(sound: AudioStreamPlayer2D) -> void:
	# The final impact and splash outlive the slime's removal, where it died.
	# They leave the enemy container, whose children are all expected to be enemies.
	var holder: Node = get_tree().current_scene if get_tree().current_scene != null else get_parent()
	if holder != null and holder != self:
		sound.reparent(holder)
		sound.process_mode = Node.PROCESS_MODE_PAUSABLE
		sound.finished.connect(sound.queue_free)
	sound.play()

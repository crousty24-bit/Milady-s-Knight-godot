# One logical swarm slot; reward eligibility is assigned by its zone before spawn.
extends CharacterBody2D
signal defeated(bonus: int, at: Vector2)
signal health_changed(value: float, maximum: float)
@export var speed: float = 52.0
var bonus_reward: int = 1
var health_units: int = 10
var max_health_units: int = 10
var health: float:
	get: return HealthUnits.to_hp(health_units)
var max_health: float:
	get: return HealthUnits.to_hp(max_health_units)
var dead: bool = false
var target: SlicePlayer

func _ready() -> void:
	set_meta("healing_profile", "skull")
	_build_art()
	add_to_group("enemies")
	var ancestor := get_parent()
	while ancestor != null:
		if ancestor.has_method("register_enemy"):
			ancestor.register_enemy(self)
			break
		ancestor = ancestor.get_parent()

func _physics_process(_delta: float) -> void:
	if dead: return
	target = get_tree().get_first_node_in_group("player") as SlicePlayer
	if not is_instance_valid(target) or target.dead: return
	var destination := target.global_position + Vector2(0, -12)
	velocity = (destination - global_position).normalized() * speed
	move_and_slide()
	if global_position.distance_to(destination) < 16.0:
		var ray := PhysicsRayQueryParameters2D.create(global_position, destination, 1)
		if get_world_2d().direct_space_state.intersect_ray(ray).is_empty():
			target.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SWARM)
			if Run019Art.just_hurt(target): _voice.play()

func take_damage(amount: float, _impulse: Vector2, _source: int = SlicePlayer.DamageSource.CONTACT_MELEE) -> void:
	if dead or amount <= 0.0: return
	health_units = maxi(0, health_units - HealthUnits.from_hp(amount))
	health_changed.emit(health, max_health)
	if health_units == 0:
		dead = true
		defeated.emit(bonus_reward, global_position)
		queue_free()

# --- Presentation (RUN-019 Claude art/SFX). Origin = cell centre; despawn effects belong to
# the swarm exit path, never to the reward path (defeated).
const SHEET = preload("res://assets/run019/enemies/possessed_skull.png")
const ANIMS = {&"fly": [0, 4, 10, true], &"spawn": [4, 5, 14, false], &"despawn": [9, 5, 14, false], &"death": [14, 6, 14, false], &"bite": [20, 3, 14, false]}
const HIT_SFX = preload("res://assets/sounds/sfx_melee_hit.tres")
const DEATH_SFX = preload("res://assets/sounds/run019/sfx_skull_death.tres")
const ATTACK_SFX = preload("res://assets/sounds/run019/sfx_skull_attack.wav")
var _art: AnimatedSprite2D
var _voice: AudioStreamPlayer2D

func _build_art() -> void:
	_art = Run019Art.sprite(self, Run019Art.frames(SHEET, Vector2i(20, 20), ANIMS), Vector2(10, 10), &"spawn", 2)
	Run019Art.chain(_art, &"spawn", &"fly")
	_voice = Run019Art.voice(self, ATTACK_SFX, -8.0)
	health_changed.connect(func(value: float, _maximum: float) -> void:
		if value > 0.0: Run019Art.sound(self, HIT_SFX, global_position, -8.0))
	defeated.connect(func(_bonus: int, at: Vector2) -> void:
		Run019Art.spawn_anim(self, _art.sprite_frames, &"death", at, Vector2(10, 10), _art.flip_h, 0.0, 0.1)
		Run019Art.sound(self, DEATH_SFX, at, -6.0))

func _process(_delta: float) -> void:
	if dead or _art == null: return
	if absf(velocity.x) > 1.0: _art.flip_h = velocity.x > 0.0
	if _art.animation == &"fly" and is_instance_valid(target) and global_position.distance_to(target.global_position + Vector2(0, -12)) < 16.0:
		Run019Art.chain(_art, &"bite", &"fly")

func despawn_art() -> void:
	if _art != null and not dead:
		Run019Art.spawn_anim(self, _art.sprite_frames, &"despawn", global_position, Vector2(10, 10), _art.flip_h, 0.0, 0.1)

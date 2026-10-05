# Functional RUN-019 N2–4 profiles. Drawn presentation is provisional art.
extends CharacterBody2D
signal defeated(bonus: int, at: Vector2)
signal health_changed(value: float, maximum: float)
signal aggro_changed(active: bool)
signal attack_started(kind: StringName, at: Vector2)
signal attack_released(attack: Node2D)
enum Kind { BLOATED, WARRIOR, ARCHER, SORCERER, CHUD }
const ATTACK_SCRIPT = preload("res://scripts/run019_enemy_attack.gd")
const HP = [5.0, 2.0, 2.0, 2.0, 10.0]
const DAMAGE = [1.5, 0.5, 0.5, 0.5, 2.0]
const REWARDS = [5, 1, 1, 1, 5]
@export var kind: Kind = Kind.WARRIOR
@export var patrol_left: float = -40.0
@export var patrol_right: float = 40.0
@export var patrol_speed: float = 24.0
@export var chase_speed: float = 48.0
@export var aggro_size: Vector2 = Vector2(240, 96)
@export var melee_range: float = 28.0
@export var ranged_range: float = 140.0
@export_range(0.05, 5.0, 0.05) var windup_duration: float = 0.3
@export_range(0.1, 10.0, 0.1) var attack_interval: float = 1.5
@export var projectile_speed: float = 150.0
@export_range(0.1, 5.0, 0.1) var blast_warning: float = 1.0
@export var blast_radius: float = 24.0
var health_units: int
var max_health_units: int
var health: float:
	get: return HealthUnits.to_hp(health_units)
var max_health: float:
	get: return HealthUnits.to_hp(max_health_units)
var bonus_reward: int
var dead: bool = false
var aggro: bool = false
var direction: int = -1
var origin_x: float
var knockback_time: float = 0.0
var windup_time: float = 0.0
var cooldown: float = 0.0
var pending_attack: StringName = &""
var attack_target: Vector2
var target: SlicePlayer
var active_attacks: Array[Node2D] = []

func _ready() -> void:
	origin_x = global_position.x
	max_health_units = HealthUnits.from_hp(HP[kind])
	health_units = max_health_units
	bonus_reward = REWARDS[kind]
	set_meta("healing_profile", "elite" if kind in [Kind.BLOATED, Kind.CHUD] else "ordinary")
	add_to_group("enemies")
	var ancestor := get_parent()
	while ancestor != null:
		if ancestor.has_method("register_enemy"):
			ancestor.register_enemy(self)
			break
		ancestor = ancestor.get_parent()

func _player() -> SlicePlayer:
	return get_tree().get_first_node_in_group("player") as SlicePlayer

func _clear_line(to: Vector2) -> bool:
	var ray := PhysicsRayQueryParameters2D.create(global_position + Vector2(0, -12), to, 1)
	ray.exclude = [get_rid()]
	return get_world_2d().direct_space_state.intersect_ray(ray).is_empty()

func _sees_player() -> bool:
	if not is_instance_valid(target) or target.dead: return false
	var center := global_position + Vector2(0, -12)
	var point := target.global_position + Vector2(0, -12)
	return Rect2(center - aggro_size / 2.0, aggro_size).has_point(point) and _clear_line(point)

func _safe_direction(dir: int) -> bool:
	var feet := global_position
	var wall := PhysicsRayQueryParameters2D.create(feet + Vector2(0, -8), feet + Vector2(dir * 14, -8), 1)
	var ground := PhysicsRayQueryParameters2D.create(feet + Vector2(dir * 14, -8), feet + Vector2(dir * 14, 16), 1)
	return get_world_2d().direct_space_state.intersect_ray(wall).is_empty() and not get_world_2d().direct_space_state.intersect_ray(ground).is_empty()

func _physics_process(delta: float) -> void:
	if dead: return
	target = _player()
	var seen := _sees_player()
	if seen != aggro:
		aggro = seen
		aggro_changed.emit(aggro)
		if not aggro:
			windup_time = 0.0
			pending_attack = &""
	cooldown = maxf(0.0, cooldown - delta)
	knockback_time = maxf(0.0, knockback_time - delta)
	velocity.y = minf(velocity.y + 760.0 * delta, 400.0)
	if windup_time > 0.0:
		windup_time = maxf(0.0, windup_time - delta)
		if windup_time == 0.0: _release_attack()
	if aggro:
		direction = 1 if target.global_position.x > global_position.x else -1
		if cooldown == 0.0 and pending_attack == &"": _try_attack()
	elif global_position.x < origin_x + patrol_left:
		direction = 1
	elif global_position.x > origin_x + patrol_right:
		direction = -1
	if knockback_time == 0.0:
		var moving := pending_attack == &"" and not (aggro and kind == Kind.ARCHER)
		if is_on_floor() and not _safe_direction(direction):
			moving = false
			if not aggro: direction *= -1
		velocity.x = direction * (chase_speed if aggro else patrol_speed) if moving else 0.0
	move_and_slide()
	if kind == Kind.BLOATED and aggro and global_position.distance_to(target.global_position) < 18.0:
		_damage_player(1.5)
	queue_redraw()

func _try_attack() -> void:
	if kind == Kind.BLOATED: return
	var offset := target.global_position - global_position
	if absf(offset.y) < 24.0 and absf(offset.x) <= melee_range and kind != Kind.ARCHER:
		pending_attack = &"melee"
	elif kind == Kind.ARCHER and offset.length() <= ranged_range:
		pending_attack = &"arrow"
	elif kind == Kind.SORCERER and offset.length() <= ranged_range:
		# Commit the ground point before the warning; it never tracks the player.
		var query := PhysicsRayQueryParameters2D.create(target.global_position + Vector2(0, -4), target.global_position + Vector2(0, 100), 1)
		var floor_hit := get_world_2d().direct_space_state.intersect_ray(query)
		if floor_hit.is_empty(): return
		attack_target = floor_hit.position
		pending_attack = &"blast"
	else: return
	windup_time = windup_duration
	cooldown = attack_interval
	attack_started.emit(pending_attack, attack_target if pending_attack == &"blast" else target.global_position)

func _release_attack() -> void:
	var released := pending_attack
	pending_attack = &""
	if not aggro or not is_instance_valid(target) or target.dead: return
	if released == &"melee":
		var offset := target.global_position - global_position
		if absf(offset.x) <= melee_range and absf(offset.y) < 24.0 and _clear_line(target.global_position + Vector2(0, -12)):
			_damage_player(DAMAGE[kind])
		attack_released.emit(self)
	elif released in [&"arrow", &"blast"]:
		var attack := Node2D.new()
		attack.set_script(ATTACK_SCRIPT)
		attack.mode = 1 if released == &"blast" else 0
		attack.damage = 2.0 if released == &"blast" else 0.5
		attack.radius = blast_radius
		attack.warning_duration = blast_warning
		attack.motion = (target.global_position + Vector2(0, -12) - (global_position + Vector2(0, -12))).normalized() * projectile_speed
		attack.source_origin = global_position + Vector2(0, -12)
		# Keep effects outside an enemy-only container; source retains their ownership.
		var holder := get_parent().get_parent() if get_parent().name == &"Enemies" else get_parent()
		holder.add_child(attack)
		attack.global_position = attack_target if released == &"blast" else global_position + Vector2(0, -12)
		active_attacks = active_attacks.filter(func(item: Node2D) -> bool: return is_instance_valid(item))
		active_attacks.append(attack)
		attack_released.emit(attack)

func _damage_player(amount: float) -> void:
	if is_instance_valid(target) and not target.dead and _clear_line(target.global_position + Vector2(0, -12)):
		target.take_damage(amount, Vector2(direction * 100.0, -150.0), SlicePlayer.DamageSource.CONTACT_MELEE)

func take_damage(amount: float, impulse: Vector2, _source: int = SlicePlayer.DamageSource.CONTACT_MELEE) -> void:
	if dead or amount <= 0.0: return
	health_units = maxi(0, health_units - HealthUnits.from_hp(amount))
	health_changed.emit(health, max_health)
	# Recoil never cancels the attack, grants invulnerability or adds hit-stun.
	velocity = impulse
	knockback_time = 0.12
	if health_units == 0:
		dead = true
		_clear_attacks()
		defeated.emit(bonus_reward, global_position)
		queue_free()

func _clear_attacks() -> void:
	for attack in active_attacks:
		if is_instance_valid(attack): attack.cancel()
	active_attacks.clear()

func _exit_tree() -> void: _clear_attacks()

func _draw() -> void:
	var colors := [Color("ad78b8"), Color("ded6bd"), Color("d5b787"), Color("87bb79"), Color("bd8477")]
	var tint: Color = Color("ffe082") if windup_time > 0.0 else colors[kind]
	var size := Vector2(24, 24) if kind in [Kind.CHUD, Kind.BLOATED] else Vector2(16, 24)
	draw_rect(Rect2(Vector2(-size.x / 2, -size.y), size), tint)
	draw_circle(Vector2(direction * 4, -17), 2, Color("322638"))
	if windup_time > 0.0:
		draw_arc(Vector2(0, -14), 18, -PI, -PI + TAU * (1.0 - windup_time / windup_duration), 16, Color("fff3bd"), 2)

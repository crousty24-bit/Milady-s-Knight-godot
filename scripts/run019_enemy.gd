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
@export var aggro_size: Vector2 = Vector2(480, 96)
@export var aggro_exit_margin: Vector2 = Vector2(80, 32)
@export_range(0.0, 5.0, 0.1) var aggro_loss_delay: float = 2.0
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
var aggro_lost_time: float = 0.0
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
	_build_art()
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

func _sees_player(retaining: bool = false) -> bool:
	if not is_instance_valid(target) or target.dead: return false
	var center := global_position + Vector2(0, -12)
	var point := target.global_position + Vector2(0, -12)
	var size := aggro_size + aggro_exit_margin * 2.0 if retaining else aggro_size
	return Rect2(center - size / 2.0, size).has_point(point) and _clear_line(point)

func _safe_direction(dir: int) -> bool:
	var feet := global_position
	var wall := PhysicsRayQueryParameters2D.create(feet + Vector2(0, -8), feet + Vector2(dir * 14, -8), 1)
	var ground := PhysicsRayQueryParameters2D.create(feet + Vector2(dir * 14, -8), feet + Vector2(dir * 14, 16), 1)
	return get_world_2d().direct_space_state.intersect_ray(wall).is_empty() and not get_world_2d().direct_space_state.intersect_ray(ground).is_empty()

func _physics_process(delta: float) -> void:
	if dead: return
	target = _player()
	var seen := _sees_player(aggro)
	if not is_instance_valid(target) or target.dead:
		aggro_lost_time = 0.0
	elif seen:
		aggro_lost_time = 0.0
	elif aggro:
		aggro_lost_time += delta
		seen = aggro_lost_time < aggro_loss_delay
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
	# Retained aggro through brief occlusion must not start attacks through terrain.
	if not _clear_line(target.global_position + Vector2(0, -12)): return
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
		# A projectile may already be freed when the next shot starts. Avoid
		# passing that stale object through a typed callable argument.
		for index in range(active_attacks.size() - 1, -1, -1):
			if not is_instance_valid(active_attacks[index]): active_attacks.remove_at(index)
		active_attacks.append(attack)
		attack_released.emit(attack)

func _damage_player(amount: float) -> void:
	if is_instance_valid(target) and not target.dead and _clear_line(target.global_position + Vector2(0, -12)):
		target.take_damage(amount, Vector2(direction * 100.0, -150.0), SlicePlayer.DamageSource.CONTACT_MELEE)
		if kind == Kind.BLOATED and Run019Art.just_hurt(target): _contact_feedback()

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

# --- Presentation (RUN-019 Claude art/SFX). Reads gameplay state only; sheets face left,
# feet on the last cell row (tools/art/run019/enemies_*.py, work SPEC tables).
const SHEETS = [
	[preload("res://assets/run019/enemies/bloated_slime.png"), Vector2i(40, 32), {&"crawl": [0, 8, 8, true], &"swell": [8, 4, 14, false], &"hit": [12, 2, 16, true], &"death": [14, 6, 12, false]}],
	[preload("res://assets/run019/enemies/skeleton_warrior.png"), Vector2i(48, 32), {&"idle": [0, 4, 6, true], &"walk": [4, 6, 10, true], &"windup": [10, 3, 10, false], &"attack": [13, 4, 16, false], &"hit": [17, 2, 16, true], &"death": [19, 8, 12, false]}],
	[preload("res://assets/run019/enemies/skeleton_archer.png"), Vector2i(40, 32), {&"idle": [0, 4, 6, true], &"walk": [4, 6, 10, true], &"windup": [10, 3, 10, false], &"shoot": [13, 3, 12, false], &"hit": [16, 2, 16, true], &"death": [18, 8, 12, false]}],
	[preload("res://assets/run019/enemies/blight_sorcerer.png"), Vector2i(40, 36), {&"idle": [0, 4, 6, true], &"walk": [4, 6, 10, true], &"cast": [10, 4, 13, false], &"cast_release": [14, 3, 12, false], &"swing_windup": [17, 3, 10, false], &"swing": [20, 4, 16, false], &"hit": [24, 2, 16, true], &"death": [26, 8, 12, false]}],
	[preload("res://assets/run019/enemies/chud_blob.png"), Vector2i(48, 36), {&"idle": [0, 4, 5, true], &"walk": [4, 6, 8, true], &"windup": [10, 3, 10, false], &"slam": [13, 4, 16, false], &"hit": [17, 2, 16, true], &"death": [19, 7, 10, false]}],
]
const STRIKES = [&"attack", &"shoot", &"cast_release", &"swing", &"slam", &"swell"]
const HIT_SFX = preload("res://assets/sounds/sfx_melee_hit.tres")
const DEATH_SFX = [
	preload("res://assets/sounds/run019/sfx_bloated_slime_death.wav"),
	preload("res://assets/sounds/run019/sfx_skeleton_warrior_death.wav"),
	preload("res://assets/sounds/run019/sfx_skeleton_archer_death.wav"),
	preload("res://assets/sounds/run019/sfx_sorcerer_death.wav"),
	preload("res://assets/sounds/run019/sfx_chud_death.wav"),
]
const MELEE_SFX = [
	preload("res://assets/sounds/run019/sfx_bloated_slime_attack.wav"),
	preload("res://assets/sounds/run019/sfx_skeleton_warrior_attack.tres"),
	null,
	preload("res://assets/sounds/run019/sfx_sorcerer_melee_attack.wav"),
	preload("res://assets/sounds/run019/sfx_chud_attack.tres"),
]
const SHOT_SFX = preload("res://assets/sounds/run019/sfx_skeleton_archer_shot.tres")
const CAST_SFX = preload("res://assets/sounds/run019/sfx_sorcerer_spell_cast.wav")
const RELEASE_FX = preload("res://assets/run019/enemies/vfx_bone_arrow_release.png")
const CAST_FX = preload("res://assets/run019/enemies/vfx_blight_cast.png")
const BURST_FX = preload("res://assets/run019/enemies/vfx_bloated_burst.png")
const HIT_TINT = Color("fff1a6")
var _art: AnimatedSprite2D
var _voice: AudioStreamPlayer2D

func _build_art() -> void:
	var sheet: Array = SHEETS[kind]
	var cell: Vector2i = sheet[1]
	_art = Run019Art.sprite(self, Run019Art.frames(sheet[0], cell, sheet[2]), Vector2(cell.x * 0.5, cell.y), &"crawl" if kind == Kind.BLOATED else &"idle")
	_voice = Run019Art.voice(self, null, -6.0)
	attack_started.connect(_on_attack_started_art)
	attack_released.connect(_on_attack_released_art)
	health_changed.connect(_on_health_changed_art)
	defeated.connect(_on_defeated_art)

func _process(_delta: float) -> void:
	if dead or _art == null: return
	_art.flip_h = direction > 0
	_art.modulate = HIT_TINT if knockback_time > 0.0 else Color.WHITE
	var wanted := _art.animation
	if pending_attack != &"":
		wanted = &"cast" if pending_attack == &"blast" else (&"swing_windup" if kind == Kind.SORCERER else &"windup")
	elif _art.animation in STRIKES and _art.is_playing():
		return
	elif knockback_time > 0.0:
		wanted = &"hit"
	elif kind == Kind.BLOATED:
		wanted = &"crawl"
	else:
		wanted = &"walk" if absf(velocity.x) > 1.0 else &"idle"
	_art.speed_scale = 1.5 if wanted == &"walk" and aggro else 1.0
	if _art.animation != wanted: _art.play(wanted)

func _play_voice(stream: AudioStream, volume_db: float = -6.0) -> void:
	if stream == null: return
	_voice.stream = stream
	_voice.volume_db = volume_db
	_voice.play()

func _on_attack_started_art(attack_kind: StringName, _at: Vector2) -> void:
	_art.play(&"cast" if attack_kind == &"blast" else (&"swing_windup" if kind == Kind.SORCERER else &"windup"))
	if attack_kind == &"blast":
		_play_voice(CAST_SFX, -6.0)
		# Spark on the staff stone (upper front of the 40x36 cell).
		Run019Art.fx(self, CAST_FX, Vector2i(16, 16), 14.0, global_position + Vector2(direction * 9, -30))

func _on_attack_released_art(attack: Node2D) -> void:
	if attack == self:
		_art.play({Kind.WARRIOR: &"attack", Kind.SORCERER: &"swing", Kind.CHUD: &"slam"}.get(kind, &"idle"))
		_play_voice(MELEE_SFX[kind], -5.0)
	elif kind == Kind.ARCHER:
		_art.play(&"shoot")
		_play_voice(SHOT_SFX, -6.0)
		Run019Art.fx(self, RELEASE_FX, Vector2i(16, 12), 24.0, attack.global_position, Vector2(0.0, 0.5), direction < 0)
	else:
		_art.play(&"cast_release")

func _contact_feedback() -> void:
	_art.play(&"swell")
	_play_voice(MELEE_SFX[kind], -5.0)

func _on_health_changed_art(value: float, _maximum: float) -> void:
	if value > 0.0: _play_voice(HIT_SFX, -8.0)

func _on_defeated_art(_bonus: int, at: Vector2) -> void:
	var cell: Vector2i = SHEETS[kind][1]
	Run019Art.spawn_anim(self, _art.sprite_frames, &"death", at, Vector2(cell.x * 0.5, cell.y), direction > 0)
	if kind == Kind.BLOATED: Run019Art.fx(self, BURST_FX, Vector2i(64, 32), 14.0, at, Vector2(0.5, 1.0))
	Run019Art.sound(self, HIT_SFX, at, -8.0)
	Run019Art.sound(self, DEATH_SFX[kind], at, -5.0)

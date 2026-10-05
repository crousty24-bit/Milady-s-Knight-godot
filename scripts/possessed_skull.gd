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

func take_damage(amount: float, _impulse: Vector2, _source: int = SlicePlayer.DamageSource.CONTACT_MELEE) -> void:
	if dead or amount <= 0.0: return
	health_units = maxi(0, health_units - HealthUnits.from_hp(amount))
	health_changed.emit(health, max_health)
	if health_units == 0:
		dead = true
		defeated.emit(bonus_reward, global_position)
		queue_free()

func _draw() -> void:
	draw_circle(Vector2.ZERO, 7, Color("d8d0ac"))
	draw_circle(Vector2(-3, -1), 2, Color("9441ae"))
	draw_circle(Vector2(3, -1), 2, Color("9441ae"))
	draw_rect(Rect2(-3, 4, 6, 4), Color("d8d0ac"))

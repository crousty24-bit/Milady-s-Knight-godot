# N4 zone: exactly four stable slots, no replacement until exit/reentry.
extends Node2D
signal swarm_started
signal swarm_cleared
const SKULL = preload("res://scenes/possessed_skull.tscn")
@export var zone_size: Vector2 = Vector2(240, 160)
@export var spawn_offsets: Array[Vector2] = [Vector2(-80, -50), Vector2(-40, -70), Vector2(40, -70), Vector2(80, -50)]
var rewarded_slots: Array[bool] = [false, false, false, false]
var skulls: Array[Node2D] = []
var occupied: bool = false

func _physics_process(_delta: float) -> void:
	var player := get_tree().get_first_node_in_group("player") as SlicePlayer
	var inside := is_instance_valid(player) and not player.dead and Rect2(-zone_size / 2, zone_size).has_point(to_local(player.global_position))
	if inside and not occupied:
		occupied = true
		_spawn()
	elif not inside and occupied:
		occupied = false
		_despawn_art()
		_clear()

func _spawn() -> void:
	for slot in range(4):
		var skull = SKULL.instantiate()
		skull.bonus_reward = 0 if rewarded_slots[slot] else 1
		skull.position = spawn_offsets[slot] if slot < spawn_offsets.size() else Vector2((slot - 1.5) * 32, -48)
		# Connect before ready/level registration so eligibility is claimed first.
		skull.defeated.connect(_slot_defeated.bind(slot))
		add_child(skull)
		skulls.append(skull)
	swarm_started.emit()

func _slot_defeated(_bonus: int, _at: Vector2, slot: int) -> void:
	rewarded_slots[slot] = true

func _clear() -> void:
	for skull in skulls:
		if is_instance_valid(skull):
			skull.set_physics_process(false)
			skull.queue_free()
	skulls.clear()
	swarm_cleared.emit()

func reset_attempt() -> void:
	occupied = false
	_clear()
	rewarded_slots = [false, false, false, false]

# --- Presentation (RUN-019 Claude SFX/VFX): spawn cue once per swarm, despawn effects only on
# zone exit; neither touches rewarded_slots.
const SPAWN_SFX = preload("res://assets/sounds/run019/sfx_skull_spawn.wav")
const DESPAWN_SFX = preload("res://assets/sounds/run019/sfx_skull_despawn.wav")

func _ready() -> void:
	swarm_started.connect(func() -> void: Run019Art.sound(self, SPAWN_SFX, global_position + Vector2(0, -60), -5.0))

func _despawn_art() -> void:
	var any := false
	for skull in skulls:
		if is_instance_valid(skull) and not skull.dead:
			skull.despawn_art()
			any = true
	if any: Run019Art.sound(self, DESPAWN_SFX, global_position + Vector2(0, -60), -8.0)

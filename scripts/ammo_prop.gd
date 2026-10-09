extends StaticBody2D
signal destroyed(amount: int)

@export_enum("Longbow", "ThrowingKnives") var ammo_family: String = "Longbow"
@export var drop_weights: Array[int] = [20, 40, 30, 10]
const DROP_AMOUNTS := [0, 1, 3, 5]
const PICKUP = preload("res://scenes/ammo_pickup.tscn")
var broken: bool = false
var rng := RandomNumberGenerator.new()

func _ready() -> void:
	rng.randomize()
	var art := get_node_or_null("Art") as AnimatedSprite2D
	# Crates and barrels look the same for both families; only the pickup reveals the ammo.
	if art != null and art.sprite_frames.has_animation(&"intact"):
		art.play(&"intact")

func drop_amount_for_roll(roll: float) -> int:
	# Roll is in [0, 1); the same function drives actual loot and boundary tests.
	if drop_weights.size() != DROP_AMOUNTS.size(): return 0
	var total := 0
	for weight in drop_weights:
		if weight < 0: return 0
		total += weight
	if total == 0: return 0
	var threshold := clampf(roll, 0.0, 0.999999999) * total
	var cumulative := 0
	for index in DROP_AMOUNTS.size():
		cumulative += drop_weights[index]
		if threshold < cumulative: return DROP_AMOUNTS[index]
	return 0

func receive_player_attack(amount: float, source: int) -> bool:
	if broken or amount <= 0.0 or source not in [SlicePlayer.DamageSource.CONTACT_MELEE, SlicePlayer.DamageSource.PROJECTILE]:
		return false
	broken = true
	$Shape.set_deferred("disabled", true)
	var dropped := drop_amount_for_roll(rng.randf())
	if dropped > 0:
		var pickup := PICKUP.instantiate()
		pickup.ammo_family = ammo_family
		pickup.amount = dropped
		get_parent().add_child(pickup)
		pickup.global_position = global_position + Vector2(0, -8)
	destroyed.emit(dropped)
	var art := get_node_or_null("Art") as AnimatedSprite2D
	if art != null and art.sprite_frames.has_animation(&"break") and art.sprite_frames.get_frame_count(&"break") > 0:
		art.animation_finished.connect(queue_free, CONNECT_ONE_SHOT)
		art.play(&"break")
	else:
		hide()
		queue_free()
	return true

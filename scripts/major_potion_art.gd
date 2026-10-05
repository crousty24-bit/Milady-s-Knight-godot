extends Node2D
# RUN-018 presentation (Claude) for scenes/major_potion.tscn: larger idle flask, drink cue and the
# potion heal feedback. Collection and healing stay in scripts/minor_potion.gd.
const POTION = preload("res://assets/run018/world/item_potion_major.png")
const HEAL_FX = preload("res://assets/sprites/vfx_heal.png")
const PICKUP_SFX = preload("res://assets/sounds/run018/sfx_major_potion_pickup.wav")
const HEAL_SFX = preload("res://assets/sounds/sfx_player_heal.wav")
const FOOT_Y = 10.0  # the flask stands on the ground 10 px below the pickup centre

func _ready() -> void:
	var flask := AnimatedSprite2D.new()
	flask.sprite_frames = OneShotFx.strip_frames(POTION, Vector2i(12, 16), 6.0, true)
	flask.centered = false
	flask.offset = Vector2(-6, FOOT_Y - 16)
	flask.play()
	add_child(flask)
	get_parent().collected.connect(_on_collected)

func _on_collected(_amount: float) -> void:
	var drink := AudioStreamPlayer2D.new()
	drink.stream = PICKUP_SFX
	drink.bus = &"SFX"
	add_child(drink)
	drink.play()
	var player: Node2D = get_tree().get_first_node_in_group("player")
	if player != null:
		OneShotFx.spawn(player, HEAL_FX, Vector2i(24, 32), 10.0, player.global_position + Vector2(0, 1), false, Vector2(0.5, 1.0), HEAL_SFX, -3.0)

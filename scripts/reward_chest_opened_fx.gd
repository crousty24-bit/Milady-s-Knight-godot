extends Node2D
# RUN-018 presentation (Claude): opened paid chest left in the world while its reward window is
# up. Accepting plays the accept cue (or the upgrade cue for +1 of the same weapon); a refusal
# already sounds in the window. Then the chest dissolves. Purely visual and audio.
const REVEAL_SFX = preload("res://assets/sounds/sfx_chest_reward_reveal.wav")
const ACCEPT_SFX = preload("res://assets/sounds/sfx_chest_reward_accept.wav")
const UPGRADE_SFX = preload("res://assets/sounds/run018/sfx_weapon_upgrade.wav")
var chest: Area2D
var art: Array
var _anim: AnimatedSprite2D
var _audio: AudioStreamPlayer2D
var _before := {}
var _leaving: bool = false

func setup(source: Area2D, strips: Array) -> void:
	chest = source
	art = strips

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # animates while the reward window pauses the level
	var size: Vector2i = art[1]
	_anim = AnimatedSprite2D.new()
	_anim.sprite_frames = OneShotFx.strip_frames(art[0], size, 14.0)
	_anim.centered = false
	_anim.offset = Vector2(-size.x / 2.0, -size.y)
	add_child(_anim)
	_anim.play()
	_audio = AudioStreamPlayer2D.new()
	_audio.bus = &"SFX"
	_audio.max_polyphony = 3
	add_child(_audio)
	_play(art[4])
	get_tree().create_timer(0.3, true).timeout.connect(func() -> void: if is_inside_tree() and not _leaving: _play(REVEAL_SFX))
	var player := get_tree().get_first_node_in_group("player")
	if player != null: _before = (player.get("equipment") as Dictionary).duplicate()

func _play(cue: AudioStream) -> void:
	var level := get_tree().current_scene
	if level != null and level.get("closing") == true: return
	_audio.stream = cue
	_audio.play()

func _process(_delta: float) -> void:
	if _leaving: return
	if not is_instance_valid(chest) or chest.visible:
		queue_free()
		return
	if get_tree().paused: return
	_leaving = true
	var player := get_tree().get_first_node_in_group("player")
	var after: Dictionary = player.get("equipment") if player != null else _before
	for slot in ["melee", "ranged"]:
		if after.get(slot) == _before.get(slot): continue
		var upgrade := str(_before.get(slot, "")).left(-1) == str(after[slot]).left(-1)
		_play(UPGRADE_SFX if upgrade else ACCEPT_SFX)
		break
	var vanish: Vector2i = art[3]
	_anim.sprite_frames = OneShotFx.strip_frames(art[2], vanish, 12.0)
	_anim.offset = Vector2(-vanish.x / 2.0, -vanish.y)
	_anim.play()
	await _anim.animation_finished
	_anim.hide()
	if _audio.playing: await _audio.finished
	queue_free()

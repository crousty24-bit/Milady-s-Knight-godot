extends Node2D
# Opened tutorial chest left in the world while its reward window is open (presentation only).
var chest: Area2D
var strip: Texture2D
var vanish: Texture2D
var sounds: Array
var foot_y: float
var _anim: AnimatedSprite2D
var _audio: AudioStreamPlayer2D
var _had_bow: bool = false
var _leaving: bool = false

func setup(source: Area2D, chest_strip: Texture2D, vanish_strip: Texture2D, cues: Array, foot: float) -> void:
	chest = source
	strip = chest_strip
	vanish = vanish_strip
	sounds = cues
	foot_y = foot

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # animates while the reward window pauses the level
	z_index = 0
	_anim = AnimatedSprite2D.new()
	_anim.sprite_frames = OneShotFx.strip_frames(strip, Vector2i(24, 20), 14.0)
	_anim.centered = false
	_anim.offset = Vector2(-12, foot_y - 20)
	add_child(_anim)
	_anim.play()
	_audio = AudioStreamPlayer2D.new()
	_audio.bus = &"SFX"
	_audio.max_polyphony = 3
	add_child(_audio)
	_play(sounds[0])
	get_tree().create_timer(0.3, true).timeout.connect(func() -> void: if is_inside_tree(): _play(sounds[1]))
	var player := get_tree().get_first_node_in_group("player")
	_had_bow = player != null and player.get("has_longbow") == true

func _play(cue: AudioStream) -> void:
	# A delayed reveal must not restart audio during the level close grace period.
	var level := get_tree().current_scene
	if level != null and level.get("closing") == true: return
	_audio.stream = cue
	_audio.play()

func _process(_delta: float) -> void:
	if _leaving: return
	if not is_instance_valid(chest) or chest.visible:
		queue_free()  # failed save: the closed chest is back
		return
	if get_tree().paused: return
	# Window closed: accepted or refused, the chest is gone for this attempt.
	_leaving = true
	var player := get_tree().get_first_node_in_group("player")
	if player != null and player.get("has_longbow") == true and not _had_bow:
		_play(sounds[2])
	_anim.sprite_frames = OneShotFx.strip_frames(vanish, Vector2i(32, 24), 12.0)
	_anim.offset = Vector2(-16, foot_y - 24)
	_anim.play()
	await _anim.animation_finished
	_anim.hide()
	if _audio.playing: await _audio.finished
	queue_free()

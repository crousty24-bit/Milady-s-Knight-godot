extends Node2D
# RUN-017 presentation (Claude) for the AncientSpirit node of scenes/eidolon_vale.tscn: floating sage
# at rest, speaking pose while the level's dialogue modal is open, cool aura and facing toward the
# knight. Purely visual: no collision, input or progression state (tools/art/spirit.py).
# RUN-017/2: authored appear/disappear frames and a column of light, sampled from the level's
# spirit_phase_progress; the level owns the trigger, states and timings.
const IDLE = preload("res://assets/sprites/npc_spirit_idle.png")
const TALK = preload("res://assets/sprites/npc_spirit_talk.png")
const APPEAR = preload("res://assets/sprites/npc_spirit_appear.png")
const DISAPPEAR = preload("res://assets/sprites/npc_spirit_disappear.png")
const AURA = preload("res://assets/sprites/vfx_spirit_aura.png")
const MANIFEST = preload("res://assets/sprites/vfx_spirit_manifest.png")  # 8x2 cells of 48x64: appear, disappear
const FRAME := Vector2i(32, 48)
# The figure is drawn 8 px right of the node: at (76,144) the open hand otherwise crossed the
# knight's resting sword at spawn. Visual only; the node and its contract position are unchanged.
const ART_OFFSET := Vector2(8, 0)
const FACE_MARGIN := 4.0  # avoid flipping back and forth when the knight stands right above the spirit
# The spirit is drawn after the knight; it turns translucent while he walks through it so the player
# keeps visual priority (docs/06). Only the opaque figure fades: the halo and the column of light live
# on the sibling Glow node, so the spirit stays readable when the knight stands inside it (the 32 px
# trigger puts him there for the apparition and the whole dialogue).
const PASS_THROUGH_DISTANCE := 20.0
const PASS_THROUGH_ALPHA := 0.3
var level: Node
var body: AnimatedSprite2D
var glow: Node2D
var aura: Sprite2D
var manifest: Sprite2D
var _time := 0.0
var _pass_through_alpha := 1.0
# Technical contract: Claude assigns this cue and may replace the fade with authored frames.
@export var appearance_sound: AudioStream
var appearance_audio: AudioStreamPlayer2D

func _ready() -> void:
	# The dialogue pauses the tree; the spirit must keep moving while it speaks.
	process_mode = Node.PROCESS_MODE_ALWAYS
	level = owner if owner != null else get_parent().get_parent()
	position = ART_OFFSET
	glow = Node2D.new()
	glow.name = "Glow"
	glow.position = ART_OFFSET
	glow.visible = false
	aura = Sprite2D.new()
	aura.texture = AURA
	aura.centered = false
	aura.offset = Vector2(-24, -52)
	glow.add_child(aura)
	manifest = Sprite2D.new()
	manifest.texture = MANIFEST
	manifest.centered = false
	manifest.offset = Vector2(-24, -60)  # the 32x48 spirit cell sits at (8, 12) of each 48x64 cell
	manifest.hframes = 8
	manifest.vframes = 2
	glow.add_child(manifest)
	# Drawn just before Art (behind the figure); the parent is still adding its children here.
	_attach_glow.call_deferred()
	body = AnimatedSprite2D.new()
	body.sprite_frames = _frames()
	body.centered = false
	body.offset = Vector2(-FRAME.x / 2, -FRAME.y)  # bottom row of the frame on the ground line
	body.flip_h = true  # the knight spawns to the left
	add_child(body)
	body.play("idle")
	appearance_audio = AudioStreamPlayer2D.new()
	appearance_audio.bus = &"SFX"
	appearance_audio.stream = appearance_sound
	add_child(appearance_audio)
	if level != null and level.has_signal("spirit_phase_changed"):
		level.spirit_phase_changed.connect(_on_story_phase_changed)
		_on_story_phase_changed(level.spirit_phase)

func _frames() -> SpriteFrames:
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	# appear/disappear are sampled by phase progress, never played: their speed is unused.
	for item in [["idle", IDLE, 6.0, true], ["talk", TALK, 8.0, true], ["appear", APPEAR, 10.0, false], ["disappear", DISAPPEAR, 10.0, false]]:
		frames.add_animation(item[0])
		frames.set_animation_speed(item[0], item[2])
		frames.set_animation_loop(item[0], item[3])
		for i in range(item[1].get_width() / FRAME.x):
			var region := AtlasTexture.new()
			region.atlas = item[1]
			region.region = Rect2(i * FRAME.x, 0, FRAME.x, FRAME.y)
			frames.add_frame(item[0], region)
	return frames

func _attach_glow() -> void:
	var parent := get_parent()
	if parent == null or not is_instance_valid(glow): return
	parent.add_child(glow)
	parent.move_child(glow, get_index())
	glow.visible = visible

func _on_story_phase_changed(phase: String) -> void:
	visible = phase not in ["hidden", "gone"]
	if glow != null: glow.visible = visible
	if phase == "appearing" and appearance_sound != null:
		appearance_audio.stream = appearance_sound
		appearance_audio.play()
	elif phase in ["hidden", "gone"]:
		appearance_audio.stop()

func _process(delta: float) -> void:
	var phase: String = level.spirit_phase if level != null else "present"
	if phase in ["hidden", "gone"]:
		hide()
		glow.hide()
		body.pause()
		return
	show()
	glow.show()
	var appearing: bool = phase == "appearing"
	var disappearing: bool = phase == "disappearing"
	var speaking: bool = level != null and level.get("modal") == "dialogue"
	# Other pauses (menu, context, death) freeze the spirit with the rest of the world.
	if get_tree().paused and not speaking and not appearing:
		body.pause()
		return
	_time += delta
	var animation := "talk" if speaking else "idle"
	var authored_phase: StringName = &"appear" if appearing else &"disappear"
	var authored: bool = (appearing or disappearing) and body.sprite_frames.has_animation(authored_phase)
	manifest.visible = authored
	if authored:
		body.animation = authored_phase
		body.pause()
		var frames := body.sprite_frames.get_frame_count(authored_phase)
		var sampled := mini(int(level.spirit_phase_progress * frames), frames - 1)
		body.frame = sampled
		manifest.frame = sampled + (0 if appearing else manifest.hframes)
	elif body.animation != animation or not body.is_playing():
		body.play(animation)
	var player: Node2D = get_tree().get_first_node_in_group("player")
	var target_alpha := 1.0
	if player != null:
		var dx: float = player.global_position.x - global_position.x
		if absf(dx) > FACE_MARGIN: body.flip_h = dx < 0.0
		if absf(dx) < PASS_THROUGH_DISTANCE and absf(player.global_position.y - global_position.y) < 48.0:
			target_alpha = PASS_THROUGH_ALPHA
	var progress: float = level.spirit_phase_progress if level != null else 1.0
	var story_alpha: float = progress if appearing else (1.0 - progress if disappearing else 1.0)
	_pass_through_alpha = move_toward(_pass_through_alpha, target_alpha, delta * 4.0)
	# Authored frames draw the apparition themselves; the disappearance still sinks a little into
	# the night as it dissolves. Without them, the technical fade remains the fallback.
	if authored: story_alpha = 1.0 if appearing else 1.0 - 0.5 * progress
	modulate.a = _pass_through_alpha * story_alpha
	aura.flip_h = body.flip_h
	manifest.flip_h = body.flip_h
	var pulse := 0.5 + 0.5 * sin(_time * (3.2 if speaking else 1.6))
	aura.modulate.a = (0.75 + 0.25 * pulse) if speaking else (0.4 + 0.15 * pulse)
	# The halo gathers with the figure and leaves with it, ending invisible.
	if appearing: aura.modulate.a *= clampf(progress * 1.6 - 0.3, 0.0, 1.0)
	elif disappearing: aura.modulate.a *= 1.0 - progress

func _exit_tree() -> void:
	if appearance_audio != null: appearance_audio.stop()
	if is_instance_valid(glow): glow.queue_free()

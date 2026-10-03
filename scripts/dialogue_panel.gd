extends CanvasLayer
# Functional RUN-017 panel. The level owns modal exclusivity, pause and persistence.
signal completed
signal retry_requested

const HUD = preload("res://scenes/hud.tscn")
# Presentation (Claude, RUN-017): speaker portrait in the banner frame and an opening cue.
const PORTRAITS = {"The Ancient Spirit": preload("res://assets/sprites/ui_portrait_spirit.png")}
const OPEN_SFX = preload("res://assets/sounds/sfx_dialogue_open.wav")
@export var characters_per_second: float = 35.0
@export var minimum_read_seconds: float = 2.0
@export var read_seconds_per_character: float = 0.035

var active: bool = false
var panel: Control
var heading: Label
var body: Label
var hint: Label
var portrait: TextureRect
var open_sound: AudioStreamPlayer
var lines: Array[String] = []
var line_index: int = 0
var opened_frame: int = -1
var _elapsed: float = 0.0
var _finished: bool = false
var _save_error: bool = false

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 30
	# Reuse the authored HUD banner, including its font, trim and portrait frame.
	# Only this detached Control enters the tree; no HUD gameplay script is started.
	var template := HUD.instantiate()
	panel = template.get_node("DialogueBanner")
	template.remove_child(panel)
	template.free()
	add_child(panel)
	panel.set_anchors_preset(Control.PRESET_TOP_LEFT)
	panel.position = Vector2(8, 280)
	panel.size = Vector2(624, 72)
	heading = panel.get_node("Speaker")
	body = panel.get_node("Text")
	hint = panel.get_node("Skip")
	portrait = panel.get_node("Portrait")
	open_sound = AudioStreamPlayer.new()
	open_sound.stream = OPEN_SFX
	open_sound.bus = &"UI"
	add_child(open_sound)
	panel.hide()

func show_dialogue(speaker: String, dialogue_lines: Array) -> void:
	lines.assign(dialogue_lines)
	heading.text = speaker
	portrait.texture = PORTRAITS.get(speaker)
	hint.text = "Space: Skip"
	line_index = 0
	active = true
	_finished = false
	_save_error = false
	opened_frame = Engine.get_process_frames()
	panel.show()
	open_sound.play()
	_show_line()

func _show_line() -> void:
	_elapsed = 0.0
	body.text = lines[line_index] if line_index < lines.size() else ""
	body.visible_characters = 0

func close() -> void:
	active = false
	panel.hide()
	open_sound.stop()

func show_save_error(detail: String) -> void:
	_save_error = true
	_finished = true
	body.text = "Unable to save dialogue progress. " + detail
	body.visible_characters = -1
	hint.text = "E: Retry saving"
	opened_frame = Engine.get_process_frames()

func _complete() -> void:
	_finished = true
	body.visible_characters = -1
	hint.text = "Saving..."
	completed.emit()

func _process(delta: float) -> void:
	if not active or Engine.get_process_frames() <= opened_frame: return
	if _save_error:
		if Input.is_action_just_pressed("interact"): retry_requested.emit()
		return
	if _finished: return
	if Input.is_action_just_pressed("jump") or lines.is_empty():
		_complete()
		return
	_elapsed += delta
	var speed := maxf(characters_per_second, 1.0)
	body.visible_characters = mini(int(_elapsed * speed), body.text.length())
	var reveal_seconds := body.text.length() / speed
	var read_seconds := maxf(minimum_read_seconds, body.text.length() * read_seconds_per_character)
	if _elapsed < reveal_seconds + read_seconds: return
	line_index += 1
	if line_index >= lines.size(): _complete()
	else: _show_line()

func _exit_tree() -> void:
	open_sound.stop()

func _input(_event: InputEvent) -> void:
	if active: get_viewport().set_input_as_handled()

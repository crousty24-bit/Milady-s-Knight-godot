extends StaticBody2D
signal phase_changed(phase: int)
signal warning_started
signal extended
signal retracted

enum Phase { RETRACTED, WARNING, EXTENDED }
# Technical fixture defaults, in gameplay seconds. Phase offset is deterministic.
@export_range(0.05, 30.0) var safe_duration: float = 1.5
@export_range(0.05, 10.0) var warning_duration: float = 0.5
@export_range(0.05, 30.0) var danger_duration: float = 1.0
@export_range(0.0, 60.0) var initial_phase: float = 0.0
var phase: int = -1
var cycle_time: float = 0.0

func _ready() -> void:
	_build_art()
	cycle_time = initial_phase
	_update_phase()

func _physics_process(delta: float) -> void:
	cycle_time += delta
	_update_phase()
	if phase != Phase.EXTENDED: return
	for body in $Contact.get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			var away := signf(to_local(body.global_position).x)
			if is_zero_approx(away): away = -body.facing
			body.take_damage(0.5, Vector2(away * 90.0, -180.0).rotated(global_rotation), SlicePlayer.DamageSource.SOLID_TRAP)
			if Run019Art.just_hurt(body): Run019Art.sound(self, HIT_SFX, body.global_position, -6.0)

func _update_phase() -> void:
	var t := fposmod(cycle_time, safe_duration + warning_duration + danger_duration)
	var next := Phase.RETRACTED if t < safe_duration else (Phase.WARNING if t < safe_duration + warning_duration else Phase.EXTENDED)
	if next == phase: return
	phase = next
	$Points.set_deferred("disabled", phase != Phase.EXTENDED)
	phase_changed.emit(phase)
	if phase == Phase.WARNING: warning_started.emit()
	elif phase == Phase.EXTENDED: extended.emit()
	else: retracted.emit()
	queue_redraw()

# --- Presentation (RUN-019 Claude art/SFX), driven by phase_changed only.
const SHEET = preload("res://assets/run019/world/trap_spikes_retract.png")
const ANIMS = {&"retracted": [0, 1, 1, false], &"warning": [1, 4, 12, true], &"extend": [5, 3, 30, false], &"extended": [8, 2, 6, true], &"retract": [10, 3, 24, false]}
const HIT_SFX = preload("res://assets/sounds/run019/sfx_spikes_hit.wav")
const EXTEND_SFX = preload("res://assets/sounds/run019/sfx_spikes_extend.wav")
var _art: AnimatedSprite2D
var _voice: AudioStreamPlayer2D

func _build_art() -> void:
	_art = Run019Art.sprite(self, Run019Art.frames(SHEET, Vector2i(32, 16), ANIMS), Vector2(16, 16), &"retracted")
	_voice = Run019Art.voice(self, EXTEND_SFX, -12.0)
	phase_changed.connect(_on_phase_art)

func _on_phase_art(next: int) -> void:
	# The initial phase is shown at rest, without a transition or sound.
	var settled := not is_node_ready()
	match next:
		Phase.WARNING: _art.play(&"warning")
		Phase.EXTENDED:
			if settled: _art.play(&"extended")
			else:
				Run019Art.chain(_art, &"extend", &"extended")
				_voice.play()
		_:
			if settled: _art.play(&"retracted")
			else: Run019Art.chain(_art, &"retract", &"retracted")

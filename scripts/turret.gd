extends StaticBody2D
signal warning_started
signal fired(projectile: Node2D)
const PROJECTILE = preload("res://scenes/trap_projectile.tscn")
@export var direction := Vector2.RIGHT
@export_range(0.05, 30.0) var cooldown_duration: float = 1.5
@export_range(0.05, 10.0) var warning_duration: float = 0.5
@export_range(0.0, 60.0) var initial_phase: float = 0.0
@export_range(1.0, 2000.0) var projectile_speed: float = 160.0
@export_range(1.0, 2000.0) var projectile_range: float = 320.0
var cycle_time: float = 0.0
var warning: bool = false

func _ready() -> void:
	_build_art()
	cycle_time = fposmod(initial_phase, cooldown_duration + warning_duration)
	_update_warning()

func _physics_process(delta: float) -> void:
	cycle_time += delta
	var period := cooldown_duration + warning_duration
	while cycle_time >= period:
		cycle_time -= period
		_fire()
	_update_warning()

func _update_warning() -> void:
	var next := cycle_time >= cooldown_duration
	if next == warning: return
	warning = next
	if warning: warning_started.emit()
	queue_redraw()

func _fire() -> void:
	var aim := direction.normalized().rotated(global_rotation) if not direction.is_zero_approx() else Vector2.RIGHT.rotated(global_rotation)
	var projectile := PROJECTILE.instantiate()
	get_parent().add_child(projectile)
	# Spawn beyond the solid housing to avoid hitting the turret itself.
	var clearance := 10.0 / maxf(absf(aim.x), absf(aim.y)) + 3.0
	projectile.global_position = global_position + aim * clearance
	projectile.setup(aim, projectile_speed, projectile_range)
	fired.emit(projectile)

# --- Presentation (RUN-019 Claude art/SFX). The sheet aims right; the art turns with `direction`
# and stays lit from above when it aims left.
const SHEET = preload("res://assets/run019/world/trap_turret.png")
const ANIMS = {&"idle": [0, 2, 2, true], &"warning": [2, 4, 12, true], &"fire": [6, 4, 20, false]}
const MUZZLE = preload("res://assets/run019/world/vfx_turret_muzzle.png")
const FIRE_SFX = preload("res://assets/sounds/run019/sfx_turret_fire.wav")
var _art: AnimatedSprite2D
var _voice: AudioStreamPlayer2D

func _build_art() -> void:
	_art = Run019Art.sprite(self, Run019Art.frames(SHEET, Vector2i(24, 24), ANIMS), Vector2(12, 12), &"idle")
	_aim_art()
	_voice = Run019Art.voice(self, FIRE_SFX, -7.0)
	warning_started.connect(func() -> void: _art.play(&"warning"))
	fired.connect(func(projectile: Node2D) -> void:
		Run019Art.chain(_art, &"fire", &"idle")
		_voice.play()
		var flash := Run019Art.fx(self, MUZZLE, Vector2i(12, 12), 24.0, projectile.global_position, Vector2(0.0, 0.5))
		if flash != null: flash.rotation = projectile.rotation)

func _process(_delta: float) -> void:
	_aim_art()

func _aim_art() -> void:
	var aim := direction.normalized() if not direction.is_zero_approx() else Vector2.RIGHT
	_art.rotation = aim.angle()
	_art.flip_v = aim.x < -0.01

func _exit_tree() -> void:
	# Release the firing cue's playback with the turret (fixtures free it mid-sound).
	if _voice != null: _voice.stop()

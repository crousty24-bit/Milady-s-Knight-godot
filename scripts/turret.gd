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

func _draw() -> void:
	draw_rect(Rect2(-10, -10, 20, 20), Color.ORANGE if warning else Color.DARK_SLATE_GRAY)
	var aim := direction.normalized() if not direction.is_zero_approx() else Vector2.RIGHT
	draw_line(Vector2.ZERO, aim * 13.0, Color.LIGHT_GRAY, 4.0)

extends StaticBody2D
signal warning_started
signal opened
@export_range(0.05, 5.0) var warning_duration: float = 0.4
var triggered: bool = false
var is_open: bool = false
var warning_remaining: float = 0.0

func _ready() -> void:
	_build_art()

func _physics_process(delta: float) -> void:
	if is_open: return
	if triggered:
		warning_remaining -= delta
		if warning_remaining <= 0.0:
			is_open = true
			$Solid.set_deferred("disabled", true)
			opened.emit()
			queue_redraw()
		return
	for body in $Trigger.get_overlapping_bodies():
		if body is SlicePlayer and not body.dead:
			# Player origin is its feet. Side/below contact does not open the floor.
			var feet := to_local(body.global_position)
			if absf(feet.x) <= 16.0 and feet.y <= 2.0 and feet.y >= -8.0 and body.velocity.dot(Vector2.DOWN.rotated(global_rotation)) >= 0.0:
				triggered = true
				warning_remaining = warning_duration
				warning_started.emit()
				queue_redraw()
				break

# --- Presentation (RUN-019 Claude art/SFX).
const SHEET = preload("res://assets/run019/world/trap_trapdoor.png")
const ANIMS = {&"closed": [0, 1, 1, false], &"warning": [1, 4, 16, true], &"open": [5, 4, 20, false], &"opened": [9, 1, 1, false]}
const TRIGGER_SFX = preload("res://assets/sounds/run019/sfx_trapdoor_trigger.wav")
var _art: AnimatedSprite2D

func _build_art() -> void:
	_art = Run019Art.sprite(self, Run019Art.frames(SHEET, Vector2i(32, 20), ANIMS), Vector2(16, 4), &"closed")
	var voice := Run019Art.voice(self, TRIGGER_SFX, -5.0)
	warning_started.connect(func() -> void:
		_art.play(&"warning")
		voice.play())
	opened.connect(func() -> void: Run019Art.chain(_art, &"open", &"opened"))

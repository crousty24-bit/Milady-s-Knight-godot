extends Node2D
# RUN-021 presentation (Claude): gains announced above the knight (shards, heals, ammo, HP bonus).
# Requests are queued and released one after another at a short interval; each new line pushes the
# previous ones up by a full line, so texts never overlap even when a kill, a heal and a pickup land
# in the same frame. Presentation only: the level pushes the amounts it already credited.
const FONT = preload("res://assets/fonts/PixelOperator8.ttf")
const SHADOW := Color(0.09, 0.075, 0.106)
const HEAD_OFFSET := Vector2(0, -44)
const LINE: float = 10.0
const STAGGER: float = 0.14
const LIFE: float = 0.85
const RISE: float = 12.0
const FADE: float = 0.3
const POP: float = 0.08
const STACK_SPEED: float = 30.0
var target: Node2D
var _pending: Array = []
var _cooldown: float = 0.0
var _lines: Array[Dictionary] = []

func _ready() -> void:
	z_index = 60
	z_as_relative = false

func push(text: String, color: Color) -> void:
	_pending.append([text, color])

func clear() -> void:
	_pending.clear()
	for entry in _lines: entry.label.queue_free()
	_lines.clear()

func pending_count() -> int:
	return _pending.size()

func visible_texts() -> Array[String]:
	var texts: Array[String] = []
	for entry in _lines: texts.append(entry.label.text)
	return texts

func _process(delta: float) -> void:
	if is_instance_valid(target):
		global_position = (target.global_position + HEAD_OFFSET).round()
	_cooldown = maxf(0.0, _cooldown - delta)
	if _cooldown == 0.0 and not _pending.is_empty():
		var next: Array = _pending.pop_front()
		_spawn(next[0], next[1])
		_cooldown = STAGGER
	for i in range(_lines.size() - 1, -1, -1):
		var entry: Dictionary = _lines[i]
		entry.age += delta
		if entry.age >= LIFE:
			entry.label.queue_free()
			_lines.remove_at(i)
	# Oldest first: a newer line always sits at least one full line below the previous one,
	# even while the older lines are still sliding up to make room.
	var floor_y: float = -INF
	for entry in _lines:
		entry.stack = move_toward(entry.stack, entry.slot * LINE, STACK_SPEED * LINE * delta)
		var rise: float = RISE * (1.0 - pow(1.0 - entry.age / LIFE, 2.0))
		var y: float = maxf(roundf(-rise - entry.stack - 8.0), floor_y)
		floor_y = y + LINE
		var label: Label = entry.label
		label.position = Vector2(roundf(-entry.width / 2.0), y)
		var pop: float = minf(entry.age / POP, 1.0)
		label.scale = Vector2.ONE * lerpf(1.2, 1.0, pop)
		label.modulate.a = clampf((LIFE - entry.age) / FADE, 0.0, 1.0)

func _spawn(text: String, color: Color) -> void:
	for entry in _lines: entry.slot += 1
	var label := Label.new()
	label.text = text
	label.add_theme_font_override("font", FONT)
	label.add_theme_font_size_override("font_size", 8)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_shadow_color", SHADOW)
	label.add_theme_constant_override("shadow_offset_x", 1)
	label.add_theme_constant_override("shadow_offset_y", 1)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var width: float = ceilf(FONT.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x)
	label.pivot_offset = Vector2(width / 2.0, 5.0)
	add_child(label)
	_lines.append({"label": label, "age": 0.0, "slot": 0, "stack": 0.0, "width": width})

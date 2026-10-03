extends CanvasLayer
# Functional keyboard panel. Art direction and final assets are handed off to Claude.
signal selected(index: int)
signal cancelled
var choices: Array[String] = []
var unavailable: Array[int] = []
var selection: int = 0
var opened: bool = false
var opened_frame: int = -1
var panel: PanelContainer
var heading: Label
var description: Label
var rows: VBoxContainer

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 30
	panel = PanelContainer.new()
	panel.position = Vector2(120, 60)
	panel.size = Vector2(400, 240)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(panel)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 10)
	panel.add_child(column)
	heading = Label.new()
	description = Label.new()
	rows = VBoxContainer.new()
	for label in [heading, description]:
		label.add_theme_font_override("font", preload("res://assets/fonts/PixelOperator8.ttf"))
		label.add_theme_font_size_override("font_size", 12 if label == heading else 8)
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		column.add_child(label)
	column.add_child(rows)
	panel.hide()

func show_menu(title: String, detail: String, options: Array, disabled: Array = []) -> void:
	choices.assign(options)
	unavailable.assign(disabled)
	selection = 0
	while selection < choices.size() - 1 and selection in unavailable:
		selection += 1
	heading.text = title
	description.text = detail
	opened = true
	opened_frame = Engine.get_process_frames()
	panel.show()
	_redraw_rows()

func close() -> void:
	opened = false
	panel.hide()

func _redraw_rows() -> void:
	for child in rows.get_children():
		rows.remove_child(child)
		child.queue_free()
	for i in range(choices.size()):
		var row := Label.new()
		row.text = ("> " if i == selection else "  ") + choices[i] + (" (unavailable)" if i in unavailable else "")
		row.add_theme_font_override("font", preload("res://assets/fonts/PixelOperator8.ttf"))
		row.add_theme_font_size_override("font_size", 10)
		row.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		row.modulate = Color(0.5, 0.5, 0.5) if i in unavailable else Color.WHITE
		rows.add_child(row)

func _process(_delta: float) -> void:
	if not opened or Engine.get_process_frames() <= opened_frame: return
	if Input.is_action_just_pressed("pause"):
		cancelled.emit()
		return
	var direction: int = int(Input.is_action_just_pressed("move_down")) - int(Input.is_action_just_pressed("move_up"))
	if direction != 0 and choices.size() > 0:
		for i in range(choices.size()):
			selection = posmod(selection + direction, choices.size())
			if selection not in unavailable: break
		_redraw_rows()
	elif Input.is_action_just_pressed("interact") and selection not in unavailable:
		selected.emit(selection)

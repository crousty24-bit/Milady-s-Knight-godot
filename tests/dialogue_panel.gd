extends SceneTree
const DIALOGUE = preload("res://scripts/dialogue_panel.gd")
const N1 = preload("res://scripts/n1_dialogue.gd")
var checks := 0
var failures := 0
var completions := 0
var retries := 0

func _initialize() -> void: call_deferred("run")

func frames(count: int = 3) -> void:
	for i in range(count): await process_frame

func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1

func run() -> void:
	# This component never writes progression, and the autoload is disabled for this driver.
	root.get_node("Progression").persistence_enabled = false
	var dialogue = DIALOGUE.new()
	root.add_child(dialogue)
	dialogue.completed.connect(func() -> void: completions += 1)
	dialogue.retry_requested.connect(func() -> void: retries += 1)
	await frames()
	check(N1.LINES.size() == 9 and N1.SPEAKER == "The Ancient Spirit", "N1 content exposes nine Spirit sentences")
	Input.action_press("jump")
	dialogue.show_dialogue(N1.SPEAKER, N1.LINES)
	dialogue._process(0.0)
	check(dialogue.active and completions == 0, "opening frame does not skip from triggering Space")
	Input.action_release("jump")
	paused = true
	await frames(5)
	check(dialogue.body.visible_characters > 0 and dialogue.body.visible_characters < dialogue.body.text.length(), "text reveals progressively while tree is paused")
	check(dialogue.panel.position.y >= 240 and dialogue.panel.position.x >= 0 and dialogue.panel.size.x <= 640, "panel occupies the lower 640x360 viewport")
	Input.action_press("pause")
	await frames()
	Input.action_release("pause")
	check(dialogue.active and completions == 0 and paused, "Escape neither closes nor completes the conversation")
	await frames(ceili(N1.LINES[0].length() / dialogue.characters_per_second * 60.0))
	check(dialogue.line_index == 0 and dialogue.body.visible_characters == dialogue.body.text.length(), "fully revealed sentence remains visible for its reading delay")
	Input.action_press("jump")
	await frames()
	check(completions == 1 and dialogue.active and dialogue.line_index == 0, "Space completes the entire conversation and retains modal ownership for save")
	await frames(8)
	check(completions == 1, "held Space emits completion only once")
	Input.action_release("jump")
	dialogue.show_save_error("Please try again.")
	await frames()
	check(dialogue.active and dialogue.body.text.contains("Unable to save") and dialogue.hint.text.contains("Retry"), "save failure stays visible with a retry instruction")
	Input.action_press("jump")
	await frames()
	Input.action_release("jump")
	check(retries == 0 and completions == 1, "Space cannot bypass save failure")
	Input.action_press("interact")
	await frames(8)
	check(retries == 1, "held E requests a single save retry")
	Input.action_release("interact")
	await frames()
	Input.action_press("interact")
	await frames()
	Input.action_release("interact")
	check(retries == 2, "a later E press permits another retry")
	dialogue.close()
	check(not dialogue.active and not dialogue.panel.visible, "owner closes panel after successful save")
	dialogue.characters_per_second = 600.0
	dialogue.minimum_read_seconds = 0.05
	dialogue.read_seconds_per_character = 0.0
	dialogue.show_dialogue(N1.SPEAKER, N1.LINES)
	var visited: Array[int] = []
	for i in range(240):
		await process_frame
		if dialogue.line_index < N1.LINES.size() and dialogue.line_index not in visited:
			visited.append(dialogue.line_index)
			check(dialogue.body.text == N1.LINES[dialogue.line_index], "sentence %d follows authored order" % (dialogue.line_index + 1))
		if completions == 2: break
	check(visited.size() == 9 and completions == 2, "nine sentences advance automatically and complete while paused")
	await frames()
	check(completions == 2, "natural completion emits once")
	dialogue.close()
	paused = false
	dialogue.queue_free()
	await frames()
	print("RESULT %d dialogue panel checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

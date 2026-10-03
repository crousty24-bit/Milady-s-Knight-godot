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
	check(completions == 0 and dialogue.active and dialogue.line_index == 1 and not dialogue._finished, "Space advances exactly one phrase without completing or saving")
	check(dialogue.hint.text == "Space: Next", "hint describes phrase advancement")
	await frames(8)
	check(completions == 0 and dialogue.line_index == 1, "held Space does not advance another phrase")
	Input.action_release("jump")
	await frames()
	dialogue.open_sound.stop()
	Input.action_press("jump")
	await frames()
	Input.action_release("jump")
	check(dialogue.line_index == 2 and completions == 0, "Space advances one phrase even during text reveal")
	check(not dialogue.open_sound.playing, "Next neither retriggers opening cue nor plays a skip sound")
	for i in range(N1.LINES.size() - 3):
		await frames()
		Input.action_press("jump")
		await frames()
		Input.action_release("jump")
	check(dialogue.line_index == N1.LINES.size() - 1 and completions == 0, "last phrase remains active until its own advance")
	await frames()
	Input.action_press("jump")
	await frames(8)
	check(completions == 1 and dialogue.active and dialogue._finished, "advancing final phrase completes once and retains modal ownership for save")
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
	# Exercise exact simulated durations independently of render-frame timing.
	dialogue.set_process(false)
	check(dialogue.extra_read_seconds == 2.0, "default extra phrase delay is two seconds")
	for phrase in ["Short.", "A sufficiently long phrase makes the character-based reading time longer than the minimum."]:
		dialogue.show_dialogue(N1.SPEAKER, [phrase, "Next phrase."])
		await frames()
		var previous_duration: float = phrase.length() / dialogue.characters_per_second + maxf(dialogue.minimum_read_seconds, phrase.length() * dialogue.read_seconds_per_character)
		dialogue._process(previous_duration + 1.99)
		check(dialogue.line_index == 0 and completions == 1, "short/long phrase remains for its previous duration plus almost two seconds")
		dialogue._process(0.02)
		check(dialogue.line_index == 1 and not dialogue._finished, "short/long phrase advances after the added two seconds")
		dialogue.close()
	dialogue.set_process(true)
	dialogue.characters_per_second = 600.0
	dialogue.minimum_read_seconds = 0.05
	dialogue.read_seconds_per_character = 0.0
	dialogue.extra_read_seconds = 0.0
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
	# Fixed-FPS headless simulation outruns the real-time audio mixer; let the stopped opening cue drain.
	OS.delay_msec(300)
	print("RESULT %d dialogue panel checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

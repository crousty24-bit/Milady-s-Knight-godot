extends "res://tests/run020_campaign.gd"
# Real authored N4, isolated enemies/hazards. Poses and suppression state are
# injected to exercise LOS/modal guards; this is not a traversal or art playtest.
const INTRO_SAVE = "user://secret-wall-intro.json"
const COLD_SAVE = "user://secret-wall-intro-cold.json"
const FLAG = "secret:n4_secret_01"
const HINT = "secret_wall_hint"
const TUTORIAL = "secret_wall_tutorial"
const HINT_TEXT = "There's something strange about this wall..."
const TUTORIAL_TEXT = "The world is full of secrets. Many lie hidden behind walls. Keep your eyes open."
var reveal_events := 0

# Contexts are opened synchronously by these fixtures. Wait past the real
# KeyboardMenu opening-frame guard before submitting a fresh input edge.
func tap(action: String) -> void:
	await frames(2)
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames(4)

func secret() -> Node2D: return level.get_node("Exploration/SecretWall")
func pose(at: Vector2) -> void:
	level.player.set_physics_process(false)
	level.player.position = at
	level.player.velocity = Vector2.ZERO
func fixture() -> void:
	await spawn(LEVELS[2])
	level.secret_wall_intro_enabled = true
	level.set_process(false)
	pose(Vector2(200,144))
func show_intro() -> bool: return level._show_secret_wall_tutorial()
func context_is(id: String, title: String, detail: String) -> bool:
	return level.modal == "context" and level.tutorial_id == id and level.pause_menu.heading.text == title and level.pause_menu.description.text == detail and level.pause_menu.choices == ["Continue"]
func release_resume() -> void:
	# Let the production held-input gate clear without opening the next context
	# until this fixture explicitly probes it. Timed sequence below keeps it on.
	level.secret_wall_intro_enabled = false
	level.set_process(true)
	await frames(4)
	level.set_process(false)
	level.secret_wall_intro_enabled = true
	level.player.set_physics_process(false)
func acknowledge() -> void:
	await tap("interact")
	await release_resume()
func begin_reveal() -> void:
	secret().passage_revealed.connect(func() -> void: reveal_events += 1)
	check(secret().receive_player_attack(1.0, SlicePlayer.DamageSource.PROJECTILE), "valid attack saves production reveal")
func finish_reveal() -> void:
	await create_timer(0.7, true).timeout
	await frames(3)

func cold(stage: String) -> void:
	progress.storage_path = COLD_SAVE
	if stage == "prepare":
		delete_save(COLD_SAVE)
		check(progress.new_game() == OK, "intro cold isolated New Game")
		await fixture()
		pose(Vector2(528,64))
		check(show_intro() and context_is(HINT, "A Strange Wall", HINT_TEXT), "intro cold first hint opens in real N4")
		await acknowledge()
		check(progress.completed_dialogues.has(HINT), "intro cold hint acknowledged through actual E")
		begin_reveal()
		await finish_reveal()
		check(secret().passage_open and reveal_events == 1 and not progress.completed_dialogues.has(TUTORIAL), "intro cold prepare saves revealed secret without explanatory acknowledgement")
	else:
		check(progress.load_progress() == OK and progress.completed_dialogues.has(HINT) and progress.permanent_flags.get(FLAG, false) and not progress.completed_dialogues.has(TUTORIAL), "intro cold process loads pending explanation and completed hint")
		await fixture()
		check(secret().passage_open and not show_intro() and level.modal.is_empty(), "intro cold acquired reload never pops up at distant spawn")
		pose(Vector2(528,64))
		check(show_intro() and context_is(TUTORIAL, "Hidden Secrets", TUTORIAL_TEXT), "intro cold approach shows only pending explanation")
		if stage == "reopen":
			await tap("pause")
			check(not progress.completed_dialogues.has(TUTORIAL), "intro cold Escape leaves pending acknowledgement durable state untouched")
		else:
			await acknowledge()
			check(progress.completed_dialogues.has(TUTORIAL), "intro cold explanation acknowledged")
			check(progress.new_game() == OK, "intro cold New Game commits reset")
			await fixture()
			check(not secret().opened and not progress.completed_dialogues.has(HINT) and not progress.completed_dialogues.has(TUTORIAL), "intro cold New Game resets both acknowledgements and secret")
			pose(Vector2(528,64))
			check(show_intro() and context_is(HINT, "A Strange Wall", HINT_TEXT), "intro cold reset first hint returns")
	await finish("secret wall intro cold " + stage)

func run() -> void:
	progress = root.get_node("Progression")
	progress.persistence_enabled = true
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		check(args[0] in ["prepare", "reopen", "reset"], "explicit intro cold phase")
		if args[0] in ["prepare", "reopen", "reset"]: await cold(args[0])
		else: await finish("secret wall intro invalid phase")
		return
	progress.storage_path = INTRO_SAVE
	delete_save(INTRO_SAVE)
	check(progress.new_game() == OK, "intro isolated baseline")
	await fixture()
	check(secret().intro_enabled and is_equal_approx(secret().intro_radius,64.0), "first authored N4 secret opts in at64px")
	check(secret().hint_style != null and secret().hint_art != null and secret().hint_style.resource_path.ends_with("n4_cracks.tres"), "authored N4 uses reusable cracks style and hint node")
	for style_name in ["glow", "cracks", "tint"]:
		var style: Resource = load("res://assets/run021/secrets/n4_" + style_name + ".tres")
		var wall = load("res://scenes/secret_wall.tscn").instantiate()
		wall.secret_id = "intro-style-" + style_name
		wall.hint_style = style
		wall.position = Vector2(100,144)
		level.add_child(wall)
		check(style != null and wall.hint_art != null and not wall.intro_enabled, "reusable " + style_name + " variant instantiates without enabling tutorial")
		wall.queue_free()
		await frames(2)
	check(not show_intro(), "distant first secret shows no hint")
	pose(Vector2(608,16))
	check(not show_intro(), "real N4 ceiling prevents nearby hint through terrain")
	pose(Vector2(528,64))
	var blocker := StaticBody2D.new()
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = Vector2(8,32)
	shape.shape = rectangle
	blocker.add_child(shape)
	level.add_child(blocker)
	blocker.position = Vector2(548,48)
	await frames(3)
	check(not show_intro(), "physical foreground obstacle suppresses nearby hint")
	blocker.queue_free()
	await frames(3)
	level.player.dead = true
	check(not show_intro(), "dead player cannot acquire intro modal")
	level.player.dead = false
	level.finished = true
	check(not show_intro(), "completed level cannot acquire intro modal")
	level.finished = false
	level.resume_pending = true
	check(not show_intro(), "resume input gate defers intro")
	level.resume_pending = false
	check(level.request_context("Existing context", "existing", ["Continue"]), "existing context owns modal")
	check(not show_intro() and level.pause_menu.heading.text == "Existing context", "intro cannot replace another context")
	await acknowledge()
	level._open_pause()
	check(not show_intro() and level.modal == "pause", "pause menu takes priority over intro")
	await tap("pause")
	await release_resume()
	check(show_intro() and context_is(HINT, "A Strange Wall", HINT_TEXT), "unobstructed proximity shows exact first hint and Continue")
	await tap("pause")
	await release_resume()
	check(not progress.completed_dialogues.has(HINT) and level.dismissed_tutorials.has(HINT) and not show_intro(), "Escape suppresses hint for attempt without durable acknowledgement")
	await fixture()
	pose(Vector2(528,64))
	check(show_intro(), "unacknowledged hint returns in new attempt")
	progress.storage_path = "user://secret-intro-missing-directory/save.json"
	await tap("interact")
	check(not progress.completed_dialogues.has(HINT) and level.modal == "context" and level.pause_menu.heading.text == "Tutorial not saved", "failed actual E acknowledgement keeps hint pending and offers retry")
	progress.storage_path = INTRO_SAVE
	await acknowledge()
	check(progress.completed_dialogues.has(HINT) and not show_intro(), "actual retry durably acknowledges hint once")
	pose(Vector2(200,144))
	begin_reveal()
	check(not secret().passage_open and not show_intro() and reveal_events == 0, "explanation never interleaves during reveal fade")
	await create_timer(0.15, true).timeout
	check(not show_intro() and not secret().passage_open, "mid-fade still has no explanation modal")
	await finish_reveal()
	check(secret().passage_open and reveal_events == 1, "passage completion emits one explanatory event")
	level.player.dead = true
	check(not show_intro(), "pending reveal explanation waits for living player")
	level.player.dead = false
	check(level.request_context("Deferred context", "existing", ["Continue"]), "another modal can delay reveal explanation")
	check(not show_intro() and level.pause_menu.heading.text == "Deferred context", "completed reveal does not replace active modal")
	await tap("interact")
	# Keep the actual held-input resume behavior independent of auto-triggering.
	Input.action_press("interact")
	level.set_process(true)
	await frames(5)
	check(level.resume_pending and level.modal.is_empty() and not level.player.controls_enabled, "held confirmation delays explanation and keeps gameplay blocked")
	Input.action_release("interact")
	await frames(5)
	check(context_is(TUTORIAL, "Hidden Secrets", TUTORIAL_TEXT), "release presents pending explanation even away from entry")
	level.set_process(false)
	await acknowledge()
	check(progress.completed_dialogues.has(TUTORIAL) and not show_intro(), "explanatory acknowledgement is durable and single-use")
	check(not secret().receive_player_attack(1.0, SlicePlayer.DamageSource.PROJECTILE) and reveal_events == 1, "duplicate reveal never triggers explanatory event again")
	await fixture()
	pose(Vector2(528,64))
	check(secret().passage_open and not show_intro(), "acknowledged acquired reload replays neither tutorial")
	# Remote reveal before proximity hint skips the first context entirely.
	check(progress.new_game() == OK, "remote-reveal case resets isolated baseline")
	await fixture()
	begin_reveal()
	await finish_reveal()
	check(show_intro() and context_is(TUTORIAL, "Hidden Secrets", TUTORIAL_TEXT) and not progress.completed_dialogues.has(HINT), "remote first reveal skips proximity hint and shows only explanation")
	await tap("pause")
	await release_resume()
	check(level.dismissed_tutorials.has(TUTORIAL) and not show_intro() and not progress.completed_dialogues.has(TUTORIAL), "Escape suppresses explanatory popup for this attempt only")
	await fixture()
	check(secret().passage_open and not show_intro(), "unacknowledged acquired secret has no distant reload popup")
	pose(Vector2(528,64))
	check(show_intro() and context_is(TUTORIAL, "Hidden Secrets", TUTORIAL_TEXT), "near acquired entry shows pending explanation without first hint")
	await finish("secret wall intro")

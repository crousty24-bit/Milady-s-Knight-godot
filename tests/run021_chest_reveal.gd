# RUN-021 chest reveal (human request, 7 Oct 2026): a paid chest first shows a "Treasure Found!"
# window with an Open button; Open (E or click) plays a 3-4 s opening with a rising beam and a
# crescendo, skippable with Space; the existing two-slot reward window follows. Real N2 chests,
# keyboard and mouse input. Captures 640x360 into work/run021/chest-reveal/ (run without --headless,
# with --fixed-fps 60: durations are counted in frames).
extends SceneTree
const OUT := "res://work/run021/chest-reveal"
const LEVEL := "res://scenes/blight_town.tscn"
var failures := 0
var checks := 0
var progress: Node
var level: Node
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print(("PASS " if ok else "FAIL ") + label)
	if not ok: failures += 1
func frames(count: int = 1) -> void:
	for i in range(count): await physics_frame
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames(2)
func until(condition: Callable, limit: int = 400) -> int:
	var count := 0
	while not condition.call() and count < limit:
		await process_frame
		count += 1
	return count
func capture(name: String, crop: Rect2i = Rect2i(), zoom: int = 1) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if crop.size != Vector2i.ZERO: image = image.get_region(crop)
	if zoom > 1: image.resize(image.get_width() * zoom, image.get_height() * zoom, Image.INTERPOLATE_NEAREST)
	image.save_png("%s/%s.png" % [OUT, name])
	print("CAPTURE ", name)
	await physics_frame  # an input sent after frame_post_draw would miss its just-pressed frame
func spawn() -> void:
	if is_instance_valid(level):
		for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for player in level.find_children("*", audio_type, true, false): player.stop()
		level.queue_free()
		await frames(2)
	paused = false
	progress.announced_level = LEVEL  # no title card over the captures
	level = load(LEVEL).instantiate()
	root.add_child(level)
	current_scene = level
	await frames(8)
	progress.banked_shards = 500
	level._update_gold_hud()
func place(at: Vector2) -> void:
	level.player.position = at
	level.player.velocity = Vector2.ZERO
	await frames(6)
func lit_pixels(rect: Rect2i) -> int:
	# Bright warm pixels (beam/flare) inside a screen rectangle.
	var image := root.get_texture().get_image()
	var count := 0
	for y in range(rect.position.y, rect.end.y):
		for x in range(rect.position.x, rect.end.x):
			var c := image.get_pixel(x, y)
			if c.r > 0.85 and c.g > 0.75 and c.b > 0.45: count += 1
	return count

func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	await spawn()
	var reveal: CanvasLayer = level.chest_reveal
	var window_rect := Rect2i(reveal.window.position, reveal.window.size)
	var beam_rect := Rect2i(window_rect.position + Vector2i(70, 20), Vector2i(100, 140))
	check(reveal != null and reveal.stage.is_empty() and not reveal.visible, "level owns an idle reveal window")
	# --- Common chest: intro window, Open, full animation, two cards.
	var common: Area2D = level.get_node("Items/CommonChest")
	common.offer = {"item": "BrutalAxe2", "upgrade": "Sword1"}
	await place(common.global_position)
	var before: int = progress.banked_shards
	await tap("interact")
	check(level.modal == "reward" and common.paid and progress.banked_shards < before, "E pays and keeps the exclusive reward modal")
	check(reveal.stage == "intro" and reveal.visible and reveal.window.visible and reveal.button.visible, "Treasure Found! window waits on its Open button")
	check(not level.pause_menu.opened and level.reward_choices.is_empty(), "reward cards are not shown before Open")
	check(reveal.chest_frame() == 0 and reveal.subtitle.text == "Common chest" and reveal.hint.text == "E: open", "closed common chest, kind and key hint")
	for chest_kind in ["common", "rare"]:
		var saved: String = reveal.kind
		reveal.kind = chest_kind
		var height: float = reveal.ART[chest_kind][1].y * reveal.PIXEL
		var middle: float = reveal.foot().y + reveal.INSET - height * 0.5
		check(absf(middle - (reveal.ART_TOP + reveal.ART_BOTTOM) * 0.5) <= 2.0 and is_equal_approx(reveal.foot().x + reveal.INSET, reveal.WINDOW.x * 0.5), "%s chest centred in the window (middle %.1f)" % [chest_kind, middle])
		reveal.kind = saved
	await capture("01-intro-common")
	await capture("01-intro-common-x2", window_rect, 2)
	await tap("pause")
	check(reveal.stage == "intro" and level.modal == "reward", "Escape cannot discard the paid chest before Open")
	await tap("jump")
	check(reveal.stage == "intro", "Space does not press Open")
	var opened_at := Engine.get_process_frames()
	await tap("interact")
	check(reveal.stage == "reveal" and not reveal.button.visible and reveal.hint.text == "Space: skip", "E presses Open and starts the animation")
	check(reveal._rise.playing, "crescendo starts with the animation")
	var frames_seen: Array[int] = []
	var widths: Array[int] = []
	var shots := {0.3: "02-rattle", 1.0: "03-lid", 1.6: "04-beam", 2.2: "05-beam-wide", 2.75: "06-climax"}
	var pending := shots.keys()
	var lit := {}
	while reveal.stage == "reveal":
		if frames_seen.is_empty() or frames_seen[-1] != reveal.chest_frame(): frames_seen.append(reveal.chest_frame())
		if reveal.elapsed >= reveal.BEAM_AT: widths.append(reveal._half_width())
		if not pending.is_empty() and reveal.elapsed >= pending[0]:
			var name: String = shots[pending.pop_front()]
			await capture(name)
			await capture(name + "-x2", window_rect, 2)
			lit[name] = lit_pixels(beam_rect)
			continue
		await process_frame
	var to_cards := (Engine.get_process_frames() - opened_at) / 60.0
	check(frames_seen == [0, 1, 2, 3, 4, 5], "lid opens through the six chest frames once (%s)" % [frames_seen])
	var growing := widths.size() > 10
	for i in range(1, widths.size()): growing = growing and widths[i] >= widths[i - 1]
	check(growing and widths[0] == 1 and widths[-1] == 7, "beam only widens, 1 to 7 art pixels (%d samples)" % widths.size())
	check(lit.get("02-rattle", 1) < lit.get("04-beam", 0) and lit.get("04-beam", 1) < lit.get("06-climax", 0), "light grows on screen: %s" % [lit])
	check(reveal._lid_played and not reveal.skipped, "lid cue played during an unskipped opening")
	check(reveal.stage == "flash" and reveal._burst.playing and not reveal._rise.playing, "climax swaps the crescendo for the burst")
	check(to_cards >= 2.7 and to_cards <= 3.4, "cards uncovered %.2f s after Open" % to_cards)
	check(level.pause_menu.opened and level.pause_menu.horizontal_choices and level.pause_menu.rows.get_child_count() == 2, "existing two-slot reward window follows")
	check(not level.pause_menu.description.visible and level.pause_menu.footer.visible and level.pause_menu.accept_label.text == "Accept" and level.pause_menu.accept_key.text == "E", "no help text, a single Accept (E) button")
	check(level.pause_menu.footer.get_global_rect().position.y >= level.pause_menu.rows.get_global_rect().end.y, "Accept button sits under the cards")
	check(is_instance_valid(level.pause_menu._glow) and level.pause_menu._glow.get_parent() == level.pause_menu.rows.get_child(level.pause_menu.selection), "selected card glows")
	check(not reveal.window.visible and reveal._flash.color.a > 0.5, "flash covers the switch to the cards")
	await frames(6)
	await capture("07-flash-over-cards")
	await until(func() -> bool: return reveal.stage.is_empty())
	await frames(2)
	check(not reveal.visible and level.pause_menu.opened, "flash fades out over the cards")
	var world_fx: Node = null
	for child in common.get_parent().get_children():
		if child.get_script() == preload("res://scripts/reward_chest_opened_fx.gd"): world_fx = child
	check(world_fx != null and world_fx._reveal == null and world_fx._anim.frame == 5, "world chest shows open behind the cards")
	await capture("08-cards-common")
	await tap("move_right")
	await tap("interact")
	await frames(20)
	check(level.modal.is_empty() and level.player.equipment.melee == "Sword1", "upgrade card still accepts through the reward window")
	# --- Rare chest: Space skips to the climax.
	await until(func() -> bool: return not level.resume_pending, 60)
	var rare: Area2D = level.get_node("Items/RareChest")
	rare.offer = {"item": "ThrowingKnives3", "upgrade": ""}
	await place(rare.global_position)
	await tap("interact")
	check(reveal.stage == "intro" and reveal.subtitle.text == "Rare chest" and reveal.chest_frame() == 0, "rare chest gets its own intro")
	await capture("09-intro-rare-x2", window_rect, 2)
	await tap("interact")
	await until(func() -> bool: return reveal.elapsed >= 0.4)
	var skip_at := Engine.get_process_frames()
	await tap("pause")
	check(reveal.stage == "reveal", "Escape does not interrupt the animation")
	await tap("jump")
	await until(func() -> bool: return level.pause_menu.opened, 30)
	var skip_time := (Engine.get_process_frames() - skip_at) / 60.0
	check(reveal.skipped and not reveal._lid.playing, "Space skipped before the lid, whose cue stays silent")
	check(level.pause_menu.opened and level.pause_menu.rows.get_child_count() == 2 and level.pause_menu.unavailable == [1] and skip_time < 0.4, "skip uncovers the rare card and its empty upgrade slot in %.2f s" % skip_time)
	check(reveal._burst.playing and not reveal._rise.playing, "skip still ends on the burst")
	await capture("10-skip-flash")
	await until(func() -> bool: return reveal.stage.is_empty())
	await tap("pause")
	await frames(20)
	check(level.modal.is_empty() and level.player.equipment.ranged != "ThrowingKnives3", "Escape on the card refuses the rare reward")
	# --- Mouse: clicking Open works too.
	await spawn()
	reveal = level.chest_reveal
	common = level.get_node("Items/CommonChest")
	common.offer = {"item": "Longsword1", "upgrade": ""}
	await place(common.global_position)
	await tap("interact")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = reveal.button.get_global_rect().get_center()
	click.global_position = click.position
	root.push_input(click, true)
	var release := click.duplicate()
	release.pressed = false
	root.push_input(release, true)
	await frames(2)
	check(reveal.stage == "reveal", "a left click on Open starts the animation")
	await tap("jump")
	await until(func() -> bool: return level.pause_menu.opened, 30)
	await tap("interact")
	await frames(20)
	check(level.modal.is_empty() and level.player.equipment.melee == "Longsword1", "accepting after a skipped reveal equips the item")
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for player in level.find_children("*", audio_type, true, false): player.stop()
	level.queue_free()
	await frames(4)
	print("RESULT %d chest reveal checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

# RUN-029: capture the redesigned HUD states at 640x360 into work/run-029/ui/ (non-headless) and check
# that no bottom information banner exists during normal play.
extends SceneTree
const OUT := "res://work/run-029/ui"
var failures := 0
var checks := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print(("PASS " if ok else "FAIL ") + label)
	if not ok: failures += 1
func frames(count: int) -> void:
	for i in range(count): await physics_frame
func capture(name: String, crop: Rect2i = Rect2i(), zoom: int = 1) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if crop.size != Vector2i.ZERO: image = image.get_region(crop)
	if zoom > 1: image.resize(image.get_width() * zoom, image.get_height() * zoom, Image.INTERPOLATE_NEAREST)
	image.save_png("%s/%s.png" % [OUT, name])
	print("CAPTURE ", name)
func bottom_banner_visible(hud: Node) -> bool:
	for child in hud.get_children():
		if child is Control and child.visible and child.name not in ["Overlay", "DeathFade"]:
			if child.get_global_rect().end.y > 360.0 - 36.0 and child.get_global_rect().position.y > 360.0 - 120.0: return true
	return false
func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	root.get_node("Progression").persistence_enabled = false
	var level = load("res://scenes/vertical_slice.tscn").instantiate()
	root.add_child(level)
	current_scene = level
	var hud = level.hud
	var player: SlicePlayer = level.get_node("Player")
	player.controls_enabled = false
	await frames(10)
	var top := Rect2i(0, 0, 640, 48)
	await capture("01-normal-full")
	await capture("01-normal-full-top", top, 3)
	check(not hud.has_node("Bottom") and not hud.has_node("Hint"), "legacy bottom bar and hint nodes are gone")
	check(not hud.get_node("DialogueBanner").visible, "dialogue banner hidden in normal play")
	check(not bottom_banner_visible(hud), "no HUD element occupies the bottom band during normal play")
	check(not hud.prompt_visible(), "gate prompt hidden away from the gate")
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.SOLID_TRAP)
	await frames(2)
	await capture("02-half-hp-top", top, 3)
	level.hud.set_health(0.5, 3.0)
	check(hud.get_node("Health").text == "0.5", "exact half HP text")
	await capture("02-half-hp-top-0.5", top, 3)
	hud.set_health(3.0, 3.0)
	level.hud.set_bonus(1234567, 23)
	await capture("03-bonus-large-top", top, 3)
	level.hud.set_bonus(0, 0)
	# Gate prompt, insufficient then sufficient, with the player at the offering spot.
	player.position = Vector2(2030, 144)
	player.get_node("Camera2D").reset_smoothing()
	level.gold = 5
	level._update_gold_hud()
	await frames(12)
	check(hud.prompt_visible(), "gate prompt visible next to the gate")
	await capture("04-gate-insufficient")
	await capture("04-gate-insufficient-zoom", Rect2i(300, 50, 320, 180), 3)
	check(not bottom_banner_visible(hud), "no bottom banner with the gate prompt")
	level.try_offering()
	await frames(5)
	await capture("05-gate-failed-flash-zoom", Rect2i(300, 50, 320, 180), 3)
	check(level.gold == 5 and not level.gate.opened, "failed offering keeps gold and gate closed")
	await frames(40)
	level.gold = 12
	level._update_gold_hud()
	await frames(5)
	await capture("06-gate-sufficient")
	await capture("06-gate-sufficient-zoom", Rect2i(300, 50, 320, 180), 3)
	level.try_offering()
	await frames(8)
	await capture("07-gate-success-zoom", Rect2i(300, 50, 320, 180), 3)
	check(level.gate.opened and level.gold == 0, "successful offering spends 12 and opens the gate")
	await frames(60)
	check(not hud.prompt_visible(), "prompt gone after the success feedback")
	# Overlays.
	hud.set_overlay("PAUSE", "ECHAP pour reprendre")
	await capture("08-pause")
	hud.set_overlay("LA POTERNE EST FRANCHIE", "Sa trace continue au-dela des murs.\n+12 bonus valides  |  Reserve 40\nE  Rejouer")
	await capture("09-victory")
	hud.set_overlay("NIVEAU TERMINE", "Bonus non sauvegardes.\nE  Reessayer la sauvegarde")
	await capture("09b-level-end-error")
	hud.show_death_overlay()
	await capture("10-death")
	hud.clear_overlay()
	hud.get_node("PauseCap").show()
	hud.get_node("PauseHint").show()
	hud.show_dialogue("The Ancient Spirit", "Placeholder dialogue line for banner layout.", load("res://assets/sprites/ui_portrait_knight.png"))
	await capture("11-dialogue-banner")
	await capture("11-dialogue-banner-zoom", Rect2i(0, 270, 640, 90), 2)
	hud.hide_dialogue()
	check(not hud.get_node("DialogueBanner").visible, "dialogue banner can be hidden again")
	level.get_node("Music").stop()
	await create_timer(0.3).timeout
	level.queue_free()
	await process_frame
	OS.delay_msec(150)
	print("RESULT %d hud visual checks; %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)

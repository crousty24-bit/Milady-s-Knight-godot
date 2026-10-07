# RUN-021 HUD pass (human request, 7 Oct 2026): panel-less HUD without word labels, shards next to the
# coins, Magic Shield effect top-left with its remaining seconds, level title card on first load only,
# death message centred. Captures 640x360 into work/run021/hud-pass/ (run without --headless).
extends SceneTree
const OUT := "res://work/run021/hud-pass"
const LEVELS := {
	"res://scenes/eidolon_vale.tscn": "The Eidolon Vale",
	"res://scenes/blight_town.tscn": "Blight Town",
	"res://scenes/black_forrest.tscn": "Black Forest",
	"res://scenes/forbidden_graveyard.tscn": "Forbidden Graveyard",
}
var failures := 0
var checks := 0
var progress: Node
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print(("PASS " if ok else "FAIL ") + label)
	if not ok: failures += 1
func frames(count: int) -> void:
	for i in range(count): await physics_frame
func seconds(duration: float) -> void:
	await create_timer(duration, true, false, true).timeout
func capture(name: String, crop: Rect2i = Rect2i(), zoom: int = 1) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if crop.size != Vector2i.ZERO: image = image.get_region(crop)
	if zoom > 1: image.resize(image.get_width() * zoom, image.get_height() * zoom, Image.INTERPOLATE_NEAREST)
	image.save_png("%s/%s.png" % [OUT, name])
	print("CAPTURE ", name)
func open(path: String) -> Node:
	var level = load(path).instantiate()
	root.add_child(level)
	current_scene = level
	level.player.controls_enabled = false
	await frames(8)
	return level
func close(level: Node) -> void:
	# Stop every voice (music, ambience, title sting, death cue) before freeing, as the other suites do.
	for player in level.find_children("*", "AudioStreamPlayer", true, false): player.stop()
	for player in level.find_children("*", "AudioStreamPlayer2D", true, false): player.stop()
	level.queue_free()
	await process_frame
func right(node: Control) -> float:
	return node.position.x + node.get_theme_font("font").get_string_size(node.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x

func run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	progress = root.get_node("Progression")
	progress.persistence_enabled = false
	var top := Rect2i(0, 0, 320, 100)
	# --- Panel-less layout and labels on N1.
	var level = await open("res://scenes/eidolon_vale.tscn")
	var hud = level.hud
	check(not hud.has_node("PanelCluster") and not hud.has_node("PanelBonus"), "stat panels removed")
	check(hud.get_node("AvatarFrame").visible and hud.get_node("Portrait").visible, "avatar frame kept")
	check(hud.get_node("AvatarFrame").texture.resource_path.ends_with("ui_avatar_frame_round.png") and hud.get_node("AvatarFrame").size == Vector2(34, 34), "round 34 px avatar frame")
	check(hud.get_node("Portrait").texture.resource_path.ends_with("ui_portrait_knight_round.png") and hud.get_node("Portrait").position == Vector2(11, 11), "three-quarter portrait fills the round window")
	check(hud.get_node("HealthHearts").position.x >= hud.get_node("AvatarFrame").get_rect().end.x + 6.0 and hud.get_node("Equipment").position.y >= hud.get_node("AvatarFrame").get_rect().end.y + 2.0, "stats and slots clear the larger frame")
	for plate in ["MeleePlate", "RangedPlate", "AmmoPlate"]:
		check(not hud.get_node("Equipment/" + plate).visible, plate + " hidden")
	level.player.equipment = {"melee": "Sword0", "ranged": "Longbow0"}
	level._update_equipment_hud(0)
	await frames(3)
	check(not hud.get_node("Equipment/AmmoPlate").visible and hud.get_node("Equipment/AmmoCount").visible, "ammo count shown without its plate")
	# Third pass: weapon name only, then a 12x12 level badge right after it.
	level.player.configure_loadout({"melee": "Longsword1", "ranged": "Longbow2"})
	level._update_equipment_hud(0)
	for i in 3: await process_frame
	for slot in [["Melee", "MeleeBadge", "> Longsword", 1], ["Ranged", "RangedBadge", "  Longbow", 2]]:
		var label: Label = hud.get_node("Equipment/" + slot[0])
		var badge: TextureRect = hud.get_node("Equipment/" + slot[1])
		check(label.text == slot[2], "%s slot shows the weapon name without its level digit" % slot[0])
		check(badge.visible and badge.size == Vector2(12, 12) and (badge.texture as AtlasTexture).region == Rect2(slot[3] * 12, 0, 12, 12), "%s slot shows the large level-%d badge" % [slot[0], slot[3]])
		var gap: float = badge.position.x - (label.position.x + right(label) - label.position.x)
		check(gap >= 2.0 and gap <= 6.0 and absf(badge.position.y + 6.0 - (label.position.y + 5.0)) <= 2.0, "%s badge sits right after the name" % slot[0])
	await capture("01b-n1-slots-badges-x3", top, 3)
	level.player.configure_loadout({"melee": "Sword0", "ranged": "Longbow0"})
	level._update_equipment_hud(0)
	await frames(3)
	level.gold = 7
	level.bonus = 4
	progress.banked_shards = 20
	level._update_gold_hud()
	await frames(2)
	check(hud.get_node("Health").text == "3" and hud.get_node("Gold").text == "07/12", "HP and coins without words")
	check(hud.get_node("Bonus").text == "24" and hud.get_node("BonusPending").text == "+4", "shards total and current gain without words")
	for name in ["Health", "Gold", "Bonus", "BonusPending"]:
		var text: String = hud.get_node(name).text
		check(not text.contains("HP") and not text.contains("COINS") and not text.contains("SHARDS") and not text.contains("reserve") and not text.contains("current") and not text.contains("bank"), name + " carries no word label")
	var gold: Label = hud.get_node("Gold")
	var shard: Control = hud.get_node("ShardIcon")
	check(is_equal_approx(shard.position.y, hud.get_node("GoldIcon").position.y) and shard.position.x > right(gold) + 4.0 and shard.position.x < right(gold) + 16.0, "shard counter sits right after the coins on the same row")
	check(hud.get_node("Bonus").position.x > shard.position.x + 12.0 and hud.get_node("BonusPending").position.x > right(hud.get_node("Bonus")), "shard values follow their icon without overlap")
	check(hud.get_node("Bonus").get_global_rect().end.x < 320.0, "shards stay in the top-left cluster")
	await capture("01-n1-hud-full")
	await capture("01-n1-hud-top-x3", top, 3)
	# Large values and the paid gate.
	level.gate.opened = true
	progress.banked_shards = 1234567
	level._update_gold_hud()
	await frames(2)
	check(hud.get_node("Gold").text == "07  OPEN" and right(hud.get_node("BonusPending")) < hud.get_node("PauseHint").position.x, "paid gate and large shard totals stay readable")
	await capture("02-n1-paid-large-top-x3", top, 3)
	level.gate.opened = false
	progress.banked_shards = 20
	level._update_gold_hud()
	# --- Magic Shield effect.
	var effect: Control = hud.get_node("ShieldEffect")
	check(not effect.visible, "shield effect hidden without an active shield")
	level.player.activate_magic_shield()
	await frames(3)
	check(effect.visible and effect.get_node("Time").text == "10", "active shield shows its icon and 10 s")
	var icon_rect: Rect2 = effect.get_node("Icon").get_global_rect()
	check(icon_rect.position.x > 560.0 and icon_rect.end.x <= 632.0 and icon_rect.position.y >= hud.get_node("PauseCap").get_global_rect().end.y + 4.0 and icon_rect.end.y <= 60.0, "shield effect sits top-right under the pause key")
	check(icon_rect.size == Vector2(24, 24) and effect.get_node("Time").get_theme_font_size("font_size") == 16, "large shield icon and timer")
	check(effect.get_node("Time").get_global_rect().end.x <= icon_rect.position.x, "timer reads left of the icon without overlap")
	await capture("03-shield-active-top-x3", top, 3)
	await capture("03b-shield-active-right-x3", Rect2i(480, 0, 160, 64), 3)
	await seconds(1.2)
	check(effect.get_node("Time").text == "9", "shield time counts down with the gameplay timer")
	level.player.magic_shield_time = 1.5
	await frames(2)
	check(effect.visible and effect.get_node("Time").text == "2", "last seconds rounded up")
	await capture("04-shield-ending-top-x3", top, 3)
	level.player.magic_shield_time = 0.0
	await frames(2)
	check(not effect.visible, "shield effect hidden when the shield ends")
	# --- Two heart rows push the lower rows down without overlap.
	hud.set_health(6.0, 6.0)
	await frames(2)
	check(hud.get_node("GoldIcon").position.y >= 26.0 + 11.0 and hud.get_node("Equipment").position.y >= 55.0, "second heart row shifts coins and equipment")
	level.player.activate_magic_shield()
	await frames(2)
	await capture("05-six-hearts-shield-top-x3", top, 3)
	level.player.magic_shield_time = 0.0
	hud.set_health(level.player.health, level.player.max_health)
	await close(level)
	# --- HP bonus pops a new heart; simultaneous gains are announced one after another above the knight.
	level = await open("res://scenes/blight_town.tscn")
	hud = level.hud
	var hearts = hud.get_node("HealthHearts")
	var queue = level.get_node("FeedbackText")
	check(not hearts.popping() and queue.visible_texts().is_empty(), "no pop and no text on level entry")
	await seconds(5.2)
	level.player.configure_bonus_health(1, true)
	await frames(1)
	check(hearts.popping() and level.player.max_health == 4.0, "HP bonus pops the new heart")
	for i in 6: await process_frame
	await capture("08-heart-pop-top-x3", top, 3)
	await seconds(0.7)
	check(not hearts.popping(), "heart pop settles")
	await seconds(1.0)
	check(queue.visible_texts().is_empty(), "HP bonus line expired")
	# Kill + ammo + potion in the same frame.
	level.player.health_units = 20
	level._on_enemy_defeated(3, level.player.global_position + Vector2(24, -8))
	level.player.ammo_collected.emit("Longbow", 3)
	level.player.heal(0.5)
	check(queue.pending_count() == 3, "three gains queued in order")
	var order: Array[String] = []
	var overlap := false
	var peak := 0
	var elapsed := 0.0
	var mid_captured := false
	while elapsed < 1.6:
		await process_frame
		elapsed += level.get_process_delta_time()
		for text in queue.visible_texts():
			if not order.has(text): order.append(text)
		var rects: Array[Rect2] = []
		for child in queue.get_children():
			if child is Label and child.modulate.a > 0.05:
				rects.append(Rect2(child.position, Vector2(child.size.x, 8)))
		peak = maxi(peak, rects.size())
		for a in rects.size():
			for b in range(a + 1, rects.size()):
				if rects[a].intersects(rects[b]):
					overlap = true
					print("OVERLAP t=%.3f %s %s" % [elapsed, rects[a], rects[b]])
		if rects.size() == 3 and not mid_captured:
			mid_captured = true
			var at := Vector2i(level.get_viewport().get_canvas_transform() * level.player.global_position)
			await capture("09-chained-gains-x3", Rect2i(clampi(at.x - 60, 0, 520), clampi(at.y - 80, 0, 260), 120, 100), 3)
	check(order == ["+3 SHARDS", "+3 ARROWS", "+0.5 HP"], "gains appear one after another in event order: %s" % [order])
	check(peak == 3 and not overlap, "all three lines readable together without overlap (peak %d, overlap %s)" % [peak, overlap])
	check(queue.visible_texts().is_empty() and queue.pending_count() == 0, "queue drains within 1.6 s")
	await close(level)
	# --- Title card on each campaign level: first load only, centred, 5 s with fades.
	for path in LEVELS:
		progress.announced_level = ""
		level = await open(path)
		hud = level.hud
		var card: Control = hud.get_node("LevelTitle")
		var label: Label = card.get_node("Name")
		check(card.visible and label.text == LEVELS[path], "%s announces its name on first load" % LEVELS[path])
		check(card.get_node("Sound").stream != null and card.get_node("Sound").bus == &"UI" and is_equal_approx(card.get_node("Sound").volume_db, -3.0), "%s title sting on the UI bus, 3 dB lower" % LEVELS[path])
		var rect := label.get_global_rect()
		check(absf(rect.get_center().x - 320.0) <= 1.0 and absf(rect.get_center().y - 176.0) <= 6.0, "%s title centred on screen" % LEVELS[path])
		check(label.get_theme_font_size("font_size") >= 24, "%s title uses a large font" % LEVELS[path])
		for i in 12: await process_frame
		var early: float = card.modulate.a
		for i in 12: await process_frame
		check(early > 0.0 and card.modulate.a > early and card.modulate.a < 0.95, "%s title fades in (alpha %.2f then %.2f)" % [LEVELS[path], early, card.modulate.a])
		await seconds(1.4)
		check(is_equal_approx(card.modulate.a, 1.0), "%s title fully shown after the fade-in" % LEVELS[path])
		await capture("06-title-" + path.get_file().get_basename())
		await capture("06-title-%s-zoom" % path.get_file().get_basename(), Rect2i(120, 130, 400, 90), 2)
		await seconds(2.7)
		check(card.visible and card.modulate.a < 1.0, "%s title fading out before 5 s" % LEVELS[path])
		await seconds(0.8)
		check(not card.visible, "%s title gone after 5 s" % LEVELS[path])
		await close(level)
	# Death / restart reload the same scene: no second announcement; quitting to menu re-arms it.
	progress.announced_level = ""
	level = await open("res://scenes/blight_town.tscn")
	check(level.hud.level_title_visible(), "N2 title on first load")
	level._restart_attempt()
	await frames(8)
	level = current_scene
	level.player.controls_enabled = false
	check(not level.hud.level_title_visible(), "restart / death reload does not replay the title")
	# The death message replaces a running title and sits mid-screen.
	progress.announced_level = ""
	level.hud.show_level_title("Blight Town")
	level.player.take_damage(99.0, Vector2.ZERO, SlicePlayer.DamageSource.SOLID_TRAP)
	await frames(4)
	check(not level.hud.level_title_visible(), "death hides a running title card")
	var panel: Control = level.hud.get_node("Overlay/Panel")
	var title: Label = level.hud.get_node("Overlay/Title")
	check(absf(panel.get_global_rect().get_center().y - 180.0) <= 1.0 and absf(title.get_global_rect().get_center().y - 180.0) <= 1.0, "death message centred vertically")
	check(absf(panel.get_global_rect().get_center().x - 320.0) <= 1.0 and title.text == "Thou hast perished.", "death message centred horizontally")
	await capture("07-death-centred")
	paused = false
	await close(level)
	await seconds(0.3)
	OS.delay_msec(150)
	print("RESULT %d run021 hud pass checks; %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)

# RUN-018 Claude render pilot: equipped weapons, Throwing Knives, HUD slots, paid chest choice,
# major potion and kill-heal feedback in the economy fixture at 640x360.
# Captures go to work/run018/claude/render/. Uses its own save basename and must be run with an
# isolated user profile (APPDATA/XDG); it never touches the player's progress.json.
extends SceneTree
const FIXTURE = preload("res://tests/fixtures/economy_level.tscn")
const OUT := "res://work/run018/claude/render"
const PATH := "user://run018-claude-visual.json"
const MELEE := ["Sword", "Longsword", "BrutalAxe", "DarkScythe", "Warhammer", "Halberds"]
var checks := 0
var failures := 0
var level: Node2D
var player: SlicePlayer
var progress: Node
var rendered := false

func _initialize() -> void: call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print("PASS " if ok else "FAIL ", label)

func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame

func capture(name: String) -> void:
	if not rendered: return
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("%s/%s.png" % [OUT, name])
	print("CAPTURE ", name)
	await process_frame

func release_all() -> void:
	for action in ["move_left", "move_right", "jump", "attack", "switch_equipment", "interact"]: Input.action_release(action)

func spawn(at: Vector2 = Vector2(64, 140)) -> void:
	release_all()
	paused = false
	if is_instance_valid(level):
		level.queue_free()
		await frames(2)
	level = FIXTURE.instantiate()
	root.add_child(level)
	current_scene = level
	level.get_node("Music").stop()
	player = level.player
	for enemy in level.get_node("Enemies").get_children(): enemy.set_physics_process(false)
	player.position = at
	player.get_node("Camera2D").reset_smoothing()
	await frames(8)

func loadout(melee: String, ranged: String = "", slot: int = 0) -> void:
	player.configure_loadout({"melee": melee, "ranged": ranged})
	player.active_slot = slot if not ranged.is_empty() else 0
	player.equipment_changed.emit(player.active_slot)
	await frames(2)

# Farthest weapon pixel from the hand, in rig pixels (the texture is the rasterised strip + outline).
func weapon_extent(hand: Vector2) -> float:
	var art: Sprite2D = player.get_node("Sprite/Weapon")
	var image := art.texture.get_image()
	var flip := art.flip_h
	var best := 0.0
	for y in image.get_height():
		for x in image.get_width():
			if image.get_pixel(x, y).a <= 0.0: continue
			var local := Vector2(image.get_width() - 1 - x if flip else x, y)
			var rig := art.position + local + Vector2(0.5, 0.5) - Vector2(0, 29)
			if flip: rig.x = -rig.x
			best = maxf(best, rig.distance_to(hand))
	return best

func contact_pose(facing: int) -> void:
	player.facing = facing
	player.attack_cooldown = 0.0
	Input.action_press("attack")
	for i in 40:
		await physics_frame
		if player.attack_time > 0.0 and player.attack_time < SlicePlayer.ATTACK_HIT_START_TIME - 0.02: break
	await process_frame
	Input.action_release("attack")

func run() -> void:
	rendered = DisplayServer.get_name() != "headless"
	DirAccess.make_dir_recursive_absolute(OUT)
	progress = root.get_node("Progression")
	progress.storage_path = PATH
	progress.persistence_enabled = false
	progress.new_game()
	progress.settle_level(0, progress.DEFAULT_LEVEL)
	await spawn()
	# --- melee weapons: layers, reach-following blade, both facings, air and stowed.
	for base: String in MELEE:
		for level_index: int in [0, 3, 5]:
			var id := "%s%d" % [base, level_index]
			await loadout(id)
			await contact_pose(1)
			var carrier: AnimatedSprite2D = player.upper if player.upper.visible else player.sprite
			var spec: Array = player.RIG.FRAMES[String(carrier.animation)][carrier.frame]
			var reach: float = WeaponCatalog.stats(id).reach
			var art: Sprite2D = player.get_node("Sprite/Weapon")
			var extent := weapon_extent(Vector2(spec[1], spec[2])) if art.visible else 0.0
			check(art.visible and player.get_node("Sprite/Mid").animation == carrier.animation and player.get_node("Sprite/Over").frame == carrier.frame, "%s contact frame draws the weapon between synced mid/over layers" % id)
			check(absf(extent - reach) <= 2.5, "%s drawn reach %.1f px follows gameplay reach %.1f px" % [id, extent, reach])
			if level_index != 5: await capture("melee_%s_right" % id)
			await frames(30)
		var id0 := base + "0"
		await loadout(id0)
		await contact_pose(-1)
		var art_left: Sprite2D = player.get_node("Sprite/Weapon")
		check(art_left.visible and art_left.flip_h and player.sprite.flip_h, "%s mirrors with the knight when facing left" % id0)
		await capture("melee_%s_left" % id0)
		await frames(30)
		player.velocity = Vector2(0, -200)
		player.position.y -= 24
		await frames(2)
		await contact_pose(1)
		check(player.upper.visible and player.get_node("Sprite/Mid").position == player.upper.position, "%s airborne attack draws the weapon on the layered upper body" % id0)
		await capture("melee_%s_air" % id0)
		await frames(40)
		await loadout(id0, "Longbow0", 1)
		await frames(4)
		check(player.sprite.animation.begins_with("bow_") and player.get_node("Sprite/Weapon").visible, "%s is stowed while the Longbow is active" % id0)
		await capture("stowed_%s" % id0)
	# --- Throwing Knives: stance, throw, captured projectile look, impact.
	await spawn(Vector2(64, 140))
	await loadout("Sword0", "ThrowingKnives0", 1)
	check(String(player.sprite.animation).begins_with("knife_"), "Throwing Knives select the knife stance")
	await capture("knives_idle")
	player.bow_cooldown = 0.0
	Input.action_press("attack")
	var knife: Node2D = null
	for i in 20:
		await physics_frame
		for child in player.get_children():
			if child.get_script() == preload("res://scripts/arrow.gd"): knife = child
		if knife != null: break
	Input.action_release("attack")
	await frames(2)
	check(knife != null and knife.look == "knife" and player.sprite.animation == &"throw", "a throw plays the throw strip and launches a knife-look projectile")
	await capture("knives_throw")
	await loadout("Sword0", "Longbow0", 1)
	check(not is_instance_valid(knife) or knife.look == "knife", "a knife already thrown keeps its look after switching to the Longbow")
	await frames(10)
	await capture("knives_flight")
	await hud_and_rewards()
	level.queue_free()
	await frames(4)
	print("RESULT %d checks; %d failures" % [checks, failures])
	quit(1 if failures > 0 else 0)

func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames(3)

func near(node: Node2D) -> void:
	player.position = node.position
	player.velocity = Vector2.ZERO
	await frames(4)

func hud_and_rewards() -> void:
	# --- HUD: icons, level badges and plates wide enough for the longest exact labels.
	await spawn()
	await loadout("Halberds2", "ThrowingKnives3", 1)
	level._update_equipment_hud(player.active_slot)
	await frames(3)
	var slots: Control = level.hud.get_node("Equipment")
	var ranged: Label = slots.get_node("Ranged")
	var text_width := ranged.get_theme_font("font").get_string_size(ranged.text, HORIZONTAL_ALIGNMENT_LEFT, -1, ranged.get_theme_font_size("font_size")).x
	var badge: TextureRect = slots.get_node("RangedBadge")
	check(ranged.text == "> Throwing Knives 3" and slots.get_node("RangedPlate").size.x >= ranged.position.x + text_width + 12.0, "ranged plate fits the exact label and its badge")
	check(badge.visible and (badge.texture as AtlasTexture).region.position.x == 27.0 and (slots.get_node("RangedIcon").texture as AtlasTexture).region.position.x == 84.0, "Throwing Knives 3 shows its icon and the level-3 badge")
	check((slots.get_node("MeleeIcon").texture as AtlasTexture).region.position.x == 60.0 and slots.get_node("MeleePlate").size.x == slots.get_node("RangedPlate").size.x, "Halberds icon and plates share one width")
	await capture("hud_long_labels")
	await loadout("Sword0")
	level._update_equipment_hud(player.active_slot)
	await frames(3)
	check(slots.get_node("Ranged").text == "  Empty" and not slots.get_node("RangedBadge").visible and (slots.get_node("RangedIcon").texture as AtlasTexture).region.position.x == 96.0, "empty ranged slot keeps the empty frame without badge")
	await capture("hud_default")
	# --- Paid chests: closed art, horizontal cards, upgrade accept, refusal.
	progress.banked_shards = 500
	level._update_gold_hud()
	var common: Area2D = level.get_node("CommonChest")
	var rare: Area2D = level.get_node("RareChest")
	check(common.get_node("Art").get_child(0).texture.resource_path.ends_with("item_chest_common.png") and rare.get_node("Art").get_child(0).texture.resource_path.ends_with("item_chest_rare.png"), "common and rare chests use their own closed art")
	player.position = Vector2(180, 140)
	await frames(6)
	await capture("chests_closed")
	await near(common)
	common.offer = {"item": "BrutalAxe2", "upgrade": "Sword1"}
	await tap("interact")
	check(level.modal == "reward" and level.pause_menu.horizontal_choices and level.pause_menu.rows.get_child_count() == 2, "common chest opens two horizontal cards")
	await frames(10)
	await capture("chest_common_choice")
	await tap("move_right")
	check(level.pause_menu.selection == 1, "Right focuses the upgrade card")
	await capture("chest_common_upgrade_focus")
	await tap("interact")
	await frames(20)
	check(player.equipment.melee == "Sword1" and level.modal.is_empty(), "accepting the upgrade equips Sword 1")
	await capture("chest_common_after_upgrade")
	await near(rare)
	rare.offer = {"item": "ThrowingKnives3", "upgrade": ""}
	await tap("interact")
	check(level.modal == "reward" and level.pause_menu.rows.get_child_count() == 1, "rare chest without upgrade shows a single item card")
	await frames(10)
	await capture("chest_rare_choice")
	await tap("pause")
	await frames(20)
	check(level.modal.is_empty() and player.equipment.ranged.is_empty(), "Escape refuses the rare reward")
	await capture("chest_rare_refused")
	# --- Healing: major potion pickup and instant kill heal feedback.
	await spawn()
	player.take_damage(1.5, Vector2.ZERO, SlicePlayer.DamageSource.SOLID_TRAP)
	player.invulnerability = 0.0
	var potion: Area2D = level.get_node("MajorPotion")
	player.position = potion.position + Vector2(-40, 0)
	await frames(30)
	await capture("major_potion_idle")
	await near(potion)
	await frames(4)
	check(potion.used and player.health == 2.5, "major potion heals 1 HP")
	await capture("major_potion_heal")
	await frames(30)
	level.kill_healed.emit(0.5)
	await frames(4)
	await capture("kill_heal_minor")
	await frames(30)
	level.kill_healed.emit(1.0)
	await frames(4)
	await capture("kill_heal_major")
	await frames(30)

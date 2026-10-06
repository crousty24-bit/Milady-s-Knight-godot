extends SceneTree
const FIXTURE = preload("res://tests/fixtures/run019_systems.tscn")
const STORE = preload("res://scripts/progression.gd")
const ARROW = preload("res://scripts/arrow.gd")
var level: Node2D
var progress: Node
var checks := 0
var failures := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func frames(count: int = 3) -> void:
	for i in count:
		await physics_frame
		await process_frame
func tap(action: String) -> void:
	Input.action_press(action)
	await frames(2)
	Input.action_release(action)
	await frames(3)
func spawn() -> void:
	paused = false
	if is_instance_valid(level):
		level.queue_free()
		await frames(3)
	level = FIXTURE.instantiate()
	root.add_child(level)
	current_scene = level
	for enemy in level.get_node("Enemies").get_children(): enemy.queue_free()
	for coin in level.get_node("Coins").get_children(): coin.queue_free()
	await frames(8)
	level.player.controls_enabled = false
func place(at: Vector2) -> void:
	level.player.position = at
	level.player.velocity = Vector2.ZERO
	await frames(4)
func shoot(at: Vector2, facing: int = 1) -> Node2D:
	var arrow := ARROW.new()
	level.add_child(arrow)
	arrow.global_position = at
	arrow.setup(facing)
	return arrow
func run() -> void:
	progress = root.get_node("Progression")
	progress.persistence_enabled = false
	progress.new_game()
	await spawn()
	check(level.player.max_health_units == 30, "old v2 without hearts spawns at base3")
	level.player.health_units = 10
	await place(Vector2(368, 144))
	check(progress.hp_bonus_count() == 1 and level.player.health_units == 20 and level.player.max_health_units == 40 and level.get_node("Bonus").used, "real pickup commits +1 max and +1 current without full heal")
	check(progress.acquire_hp_bonus("run019_fixture_heart") == OK and progress.hp_bonus_count() == 1, "duplicate acquisition does not grant a second heart")
	check(progress.acquire_hp_bonus("") == ERR_INVALID_PARAMETER, "empty permanent id rejected")
	await spawn()
	check(level.player.health_units == 40 and level.get_node("Bonus").used, "reset keeps unique heart and heals new maximum")
	level.player.health_units = 20
	level._choose_tutorial_reward(0)
	check(level.player.health_units == 20, "free equipment acceptance does not heal existing injury")
	var chest = load("res://scenes/reward_chest.tscn").instantiate()
	level.add_child(chest)
	chest.position = level.player.position
	chest.offer = {"item":"Longsword1", "upgrade":""}
	level.bonus = 100
	await frames(4)
	check(level.open_reward_chest(chest), "paid reward opens through real proximity")
	await frames(3)
	await tap("interact")
	check(level.player.health_units == 20 and level.player.equipment.melee == "Longsword1", "paid equipment acceptance preserves injury and applies item")
	level.player.controls_enabled = false
	level.player.health_units = 40
	await place(Vector2(224, 144))
	check(level.get_node("Shield").used and level.player.magic_shield_time > 9.8, "physical shield pickup activates ten gameplay seconds")
	var player: SlicePlayer = level.player
	for source in [SlicePlayer.DamageSource.CONTACT_MELEE, SlicePlayer.DamageSource.PROJECTILE, SlicePlayer.DamageSource.SWARM]:
		player.invulnerability = 0.0
		player.attack_time = 0.2
		player.attack_cancelled = false
		player.take_damage(1.0, Vector2(200, -200), source)
		check(player.health_units == 40 and player.invulnerability == 0.0 and not player.attack_cancelled, "shield blocks enemy source%d and reactions" % source)
	for source in [SlicePlayer.DamageSource.SOLID_TRAP, SlicePlayer.DamageSource.FLAME, SlicePlayer.DamageSource.TRAP_PROJECTILE]:
		player.invulnerability = 0.0
		player.health_units = 40
		player.attack_cancelled = false
		player.take_damage(0.5, Vector2(90, -180), source)
		check(player.health_units == 40 and player.invulnerability == 0.0 and not player.attack_cancelled and player.knockback_time == 0.0, "shield blocks trap source%d and reactions" % source)
	player.velocity = Vector2.ZERO
	player.knockback_time = 0.0
	player.invulnerability = 0.0
	player.health_units = 40
	player.magic_shield_time = 2.0
	check(player.activate_magic_shield() and player.magic_shield_time == 10.0, "second shield refreshes to10 without stacking")
	player.configure_loadout({"melee":"Sword0", "ranged":"Longbow0"})
	player.controls_enabled = true
	await tap("switch_equipment")
	check(player.active_slot == 1 and player.magic_shield_time > 9.8, "weapon switch preserves shield")
	player.controls_enabled = false
	var shield_before: float = player.magic_shield_time
	paused = true
	await frames(30)
	check(is_equal_approx(player.magic_shield_time, shield_before), "pause freezes shield timer")
	paused = false
	await frames(610)
	check(player.magic_shield_time == 0.0, "shield expires after ten active seconds")
	player.invulnerability = 0.0
	player.take_damage(0.5, Vector2.ZERO, SlicePlayer.DamageSource.TRAP_PROJECTILE)
	check(player.health_units == 35 and player.attack_cancelled and player.invulnerability > 0.0, "turret damage and interruption resume after shield expires")
	player.activate_magic_shield()
	player.take_damage(0.0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)
	check(player.dead and player.magic_shield_time == 0.0, "void remains fatal under shield and clears buff")
	await spawn()
	check(level.player.magic_shield_time == 0.0 and not level.get_node("Shield").used, "reset restores pickup without buff")
	# E belongs to the level, so one interaction frame cannot charge twice.
	await place(Vector2(90, 144))
	level.gold = 2
	await tap("interact")
	check(not level.get_node("CoinDoor").opened and level.gold == 2, "insufficient E payment leaves coins and door")
	level.gold = 15
	Input.action_press("interact")
	await frames(20)
	Input.action_release("interact")
	check(level.get_node("CoinDoor").opened and level.gold == 12, "held E opens once and leaves fixture exit budget12")
	check(not level.try_secondary_door(level.get_node("CoinDoor")) and level.gold == 12, "opened door cannot charge again")
	await place(Vector2(312, 144))
	level.gold = 1000
	await tap("interact")
	check(not level.get_node("MechanismDoor").opened and level.gold == 1000 and not level.try_secondary_door(level.get_node("MechanismDoor")), "rich player cannot pay or press E to bypass mechanism-only door")
	level.gold = 12
	await place(Vector2(192, 144))
	level._open_pause()
	await frames(3)
	check(not level.try_mechanism(level.get_node("Button")), "pause excludes button interaction")
	await tap("pause")
	await frames(4)
	await tap("interact")
	check(level.get_node("Button").active and level.get_node("MechanismDoor").opened, "E button opens linked door without coins")
	check(level.gold == 12, "mechanism never spends coins")
	await spawn()
	check(not level.get_node("CoinDoor").opened and not level.get_node("MechanismDoor").opened and not level.get_node("Button").active and not level.get_node("Plate").active and level.gold == 0, "reset closes paid and linked doors and clears mechanisms/coins")
	var plate: Area2D = level.get_node("Plate")
	check(not plate.receive_player_attack(0.5, SlicePlayer.DamageSource.CONTACT_MELEE), "melee cannot activate plate")
	shoot(Vector2(240, 140))
	await frames(12)
	check(plate.active and level.get_node("MechanismDoor").opened, "real player projectile activates plate")
	# Real F hit on the accessible face, then verify persistent state on reset.
	await place(Vector2(396, 144))
	level.player.facing = 1
	level.player.controls_enabled = true
	level.player.attack_cooldown = 0.0
	await tap("attack")
	await frames(22)
	check(level.get_node("Secret").opened and progress.permanent_flags.get("secret:run019_fixture_secret", false), "real sword swing reveals solid secret and saves flag")
	await spawn()
	check(level.get_node("Secret").opened and not level.get_node("Secret").visible, "reset secret starts open without reveal animation")
	progress.permanent_flags.erase("secret:run019_fixture_secret")
	await spawn()
	shoot(Vector2(380, 132))
	await frames(15)
	check(level.get_node("Secret").opened, "real player projectile reveals and stops at secret")
	# Opaque terrain placed before a secret prevents a remote hit.
	progress.permanent_flags.erase("secret:run019_fixture_secret")
	await spawn()
	var wall := StaticBody2D.new()
	wall.collision_layer = 1
	wall.collision_mask = 0
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = Vector2(8, 32)
	shape.shape = rectangle
	wall.add_child(shape)
	level.add_child(wall)
	wall.position = Vector2(392, 128)
	await frames(3)
	shoot(Vector2(370, 132))
	await frames(15)
	check(not level.get_node("Secret").opened, "terrain occludes projectile before secret")
	await place(Vector2(380, 144))
	level.player.facing = 1
	level.player.attack_cooldown = 0.0
	level.player.controls_enabled = true
	await tap("attack")
	await frames(22)
	check(not level.get_node("Secret").opened, "terrain occludes actual melee swing before secret")
	level.player.controls_enabled = false
	# Level/HUD wiring reports real I/O failures, while neither pickup nor wall is consumed.
	var old_path: String = progress.storage_path
	var old_enabled: bool = progress.persistence_enabled
	progress.persistence_enabled = true
	progress.storage_path = "user://run019-missing-parent/progress.json"
	progress.storage_error = OK
	level.get_node("Secret").receive_player_attack(0.5, SlicePlayer.DamageSource.CONTACT_MELEE)
	check(level.get_node("Secret").save_failed and not level.get_node("Secret").opened and level.hud.save_error_label != null and level.hud.save_error_label.visible, "secret disk failure is visible and leaves wall closed")
	progress.permanent_flags.erase("hp_bonus:run019_fixture_heart")
	var failed_heart = load("res://scenes/hp_bonus.tscn").instantiate()
	failed_heart.bonus_id = "retry_heart"
	level.add_child(failed_heart)
	failed_heart.position = Vector2(48, 40)
	failed_heart.save_error.connect(level._durable_save_error)
	var before_health: int = level.player.health_units
	check(not failed_heart.collect(level.player) and not failed_heart.used and level.player.health_units == before_health and level.hud.save_error_time > 0.0, "heart disk failure is visible and does not heal or consume")
	progress.storage_path = old_path
	progress.persistence_enabled = old_enabled
	progress.storage_error = OK
	check(level.get_node("Secret").receive_player_attack(0.5, SlicePlayer.DamageSource.CONTACT_MELEE) and level.get_node("Secret").opened, "same failed secret accepts retry after storage repair")
	# I/O failure is exercised against a directory, with memory and player unchanged.
	var store := STORE.new()
	store.persistence_enabled = true
	store.storage_path = "user://run019-integration-dir"
	DirAccess.make_dir_recursive_absolute(store.storage_path)
	check(store.acquire_hp_bonus("disk_failure") != OK and store.hp_bonus_count() == 0, "failed disk transaction does not grant a permanent heart")
	DirAccess.remove_absolute(store.storage_path + ".tmp")
	DirAccess.remove_absolute(store.storage_path)
	store.free()
	check(progress.new_game() == OK and progress.hp_bonus_count() == 0, "confirmed new game clears unique hearts/secrets")
	paused = false
	level.queue_free()
	await frames(5)
	await create_timer(0.35).timeout
	print("RESULT %d run019 integration checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

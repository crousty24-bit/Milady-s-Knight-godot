extends "res://tests/run020_campaign.gd"
# Real N4 terrain and rewards. Enemies/hazards are removed by spawn() solely to
# isolate the secret transaction. Poses are injected; collision sweeps, weapon
# input and reward overlaps exercise production behavior, not a route playtest.
const SECRET_SAVE = "user://secret-wall-reveal.json"
const COLD_SAVE = "user://secret-wall-cold.json"
const SECRET_FLAG = "secret:n4_secret_01"
const SECRET_SFX = preload("res://assets/sounds/run019/sfx_secret_reveal.wav")
var reveal_sounds := 0
var reveal_effects := 0
var reveal_signals := 0

func observe_node(node: Node) -> void:
	if node is AudioStreamPlayer2D and node.stream == SECRET_SFX:
		reveal_sounds += 1
	if node is OneShotFx:
		var texture := node.sprite_frames.get_frame_texture("default", 0) as AtlasTexture
		if texture != null and texture.atlas == preload("res://assets/run019/world/vfx_secret_crumble.png"):
			reveal_effects += 1

func wall() -> Node2D: return level.get_node("Exploration/SecretWall")
func hp() -> Node2D: return level.get_node("Items/HpBonus")
func chest() -> Node2D: return level.get_node("Items/CommonChest2")
func entrance_hit() -> Dictionary:
	return level.get_world_2d().direct_space_state.intersect_ray(PhysicsRayQueryParameters2D.create(Vector2(540, 48), Vector2(590, 48), 1))
func sweep(at: Vector2, motion: Vector2) -> KinematicCollision2D:
	level.player.set_physics_process(false)
	level.player.position = at
	level.player.velocity = Vector2.ZERO
	return level.player.move_and_collide(motion)
func wait_open() -> void:
	await create_timer(0.7, false).timeout
	await frames(3)
func observe_wall() -> void:
	wall().revealed.connect(func() -> void: reveal_signals += 1)
func attack_wall() -> void:
	var outcome := {"failed":false}
	var on_error := func(_error: int) -> void: outcome.failed = true
	wall().save_error.connect(on_error)
	level.player.set_physics_process(true)
	level.player.controls_enabled = true
	level.player.configure_loadout({"melee":"Sword0", "ranged":"Longbow0"})
	level.player.position = Vector2(544,64)
	level.player.velocity = Vector2.ZERO
	level.player.facing = 1
	level.player.attack_cooldown = 0.0
	Input.action_press("attack")
	for tick in 20:
		await frames(1)
		if wall().opened or outcome.failed: break
	wall().save_error.disconnect(on_error)
	Input.action_release("attack")
	level.player.controls_enabled = false

func closed_rewards(label: String) -> void:
	level.player.set_physics_process(false)
	level.player.position = Vector2(655,56)
	await frames(4)
	var health_before: int = level.player.max_health_units
	check(hp().has_overlapping_bodies() and not hp().used and not hp().collect(level.player), label + " HP overlap and direct collect are blocked")
	check(level.player.max_health_units == health_before and not progress.has_hp_bonus("n4_hp_01"), label + " blocked HP grants no durable acquisition")
	level.player.position = Vector2(704,64)
	await frames(4)
	check(chest().has_overlapping_bodies() and not chest().player_near() and not chest().paid, label + " chest overlap remains ineligible")

func cold(stage: String) -> void:
	progress.storage_path = COLD_SAVE
	if stage == "prepare":
		delete_save(COLD_SAVE)
		check(progress.new_game() == OK, "cold isolated New Game")
		await spawn(LEVELS[2])
		observe_wall()
		await attack_wall()
		await wait_open()
		check(wall().passage_open and progress.permanent_flags.get(SECRET_FLAG, false), "cold prepare actual Sword saves and opens secret")
		level.player.set_physics_process(true)
		await place(Vector2(655,64))
		check(hp().used and progress.has_hp_bonus("n4_hp_01"), "cold prepare real HP overlap saves acquisition")
		check(reveal_sounds == 1 and reveal_signals == 1, "cold prepare single reveal cue")
	else:
		check(progress.load_progress() == OK and progress.permanent_flags.get(SECRET_FLAG, false) and progress.has_hp_bonus("n4_hp_01"), "cold process loads secret and HP from disk")
		await spawn(LEVELS[2])
		check(wall().opened and wall().passage_open and not wall().visible and wall().get_node("Shape").disabled, "cold acquired secret immediately exposes open passage")
		check(hp().used and not hp().visible and reveal_sounds == 0 and reveal_effects == 0, "cold acquired rewards and secret replay no effects")
		if stage == "reset":
			check(progress.new_game() == OK, "cold New Game commits reset")
			await spawn(LEVELS[2])
			check(not wall().opened and not wall().passage_open and wall().visible and not wall().get_node("Shape").disabled and wall().mask_art != null, "cold New Game restores mask and collision")
			check(not hp().used and not progress.has_hp_bonus("n4_hp_01") and not progress.permanent_flags.has(SECRET_FLAG), "cold New Game restores HP and removes secret acquisition")
			await closed_rewards("cold reset")
	await finish("secret wall cold " + stage)

func run() -> void:
	progress = root.get_node("Progression")
	progress.persistence_enabled = true
	node_added.connect(observe_node)
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		check(args[0] in ["prepare", "reopen", "reset"], "known cold phase")
		if args[0] in ["prepare", "reopen", "reset"]: await cold(args[0])
		else: await finish("secret wall invalid phase")
		return
	progress.storage_path = SECRET_SAVE
	delete_save(SECRET_SAVE)
	check(progress.new_game() == OK, "isolated secret baseline")
	await spawn(LEVELS[2])
	observe_wall()
	check(wall().cover_rect == Rect2(-8,-48,176,64) and wall().mask_art != null and wall().visible, "authored N4 whole-cache mask is configured")
	check(not wall().opened and not wall().passage_open and not entrance_hit().is_empty(), "closed authored entrance is solid")
	check(is_equal_approx(wall().fade_duration, 0.6), "approved reveal duration is 0.6 seconds")
	check(not wall().receive_player_attack(1.0, SlicePlayer.DamageSource.TRAP_PROJECTILE) and not wall().opened, "non-player projectile cannot reveal the secret")
	check(sweep(Vector2(544,64), Vector2(70,0)) != null, "real player collision blocks closed left entrance")
	for entry in [[Vector2(640,64), Vector2(0,-70), "ceiling"], [Vector2(640,64), Vector2(0,70), "floor"], [Vector2(640,64), Vector2(160,0), "right wall"]]:
		var hit := sweep(entry[0], entry[1])
		check(hit != null and hit.get_collider() == level.get_node("Terrain"), "real authored terrain seals cavity " + entry[2])
	await closed_rewards("closed")
	# Missing and wrong-type references must fail closed. Empty remains opt-in.
	var fixture_hp = load("res://scenes/hp_bonus.tscn").instantiate()
	fixture_hp.bonus_id = "ungated-fixture"
	fixture_hp.position = Vector2(80,100)
	level.add_child(fixture_hp)
	fixture_hp.required_secret = NodePath("../missing-secret")
	check(not fixture_hp.collect(level.player), "missing HP secret reference denies direct collection")
	fixture_hp.required_secret = fixture_hp.get_path_to(level.get_node("Terrain"))
	check(not fixture_hp.collect(level.player), "wrong-type HP secret reference denies collection")
	fixture_hp.required_secret = NodePath()
	check(fixture_hp.collect(level.player), "default ungated HP remains collectable")
	level.player.position = Vector2(704,64)
	await frames(3)
	var original_path: NodePath = chest().required_secret
	chest().required_secret = NodePath("../missing-secret")
	check(not chest().player_near(), "missing chest secret reference denies interaction")
	chest().required_secret = chest().get_path_to(level.get_node("Terrain"))
	check(not chest().player_near(), "wrong-type chest secret reference denies interaction")
	chest().required_secret = NodePath()
	check(chest().player_near(), "default ungated chest retains physical proximity behavior")
	chest().required_secret = original_path
	progress.storage_path = "user://secret-wall-missing-directory/save.json"
	await attack_wall()
	check(wall().save_failed and not wall().opened and not wall().passage_open and wall().modulate.a == 1.0, "real Sword save failure leaves cache opaque and closed")
	check(reveal_signals == 0 and reveal_sounds == 0 and reveal_effects == 0 and not entrance_hit().is_empty(), "failed save emits no reveal effect or sound and retains collision")
	progress.storage_path = SECRET_SAVE
	level.player.attack_time = 0.0
	await attack_wall()
	check(wall().opened and not wall().save_failed and not wall().passage_open and progress.permanent_flags.get(SECRET_FLAG, false), "real Sword retry commits secret before opening passage")
	check(reveal_signals == 1 and reveal_sounds == 1 and reveal_effects == 1, "successful attack emits exactly one reveal animation and SFX")
	check(not entrance_hit().is_empty(), "entrance remains solid at reveal start")
	await create_timer(0.15, false).timeout
	var alpha: float = wall().modulate.a
	check(alpha > 0.0 and alpha < 1.0 and not wall().passage_open, "mid-fade mask opacity decreases while passage remains closed")
	check(sweep(Vector2(544,64), Vector2(70,0)) != null, "real player remains blocked during fade")
	paused = true
	await create_timer(0.7, true).timeout
	check(is_equal_approx(wall().modulate.a, alpha) and not wall().passage_open and not wall().get_node("Shape").disabled, "pause longer than reveal duration freezes fade and solid entrance")
	paused = false
	await closed_rewards("during reveal")
	check(not wall().receive_player_attack(1.0, SlicePlayer.DamageSource.PROJECTILE), "duplicate projectile during reveal is ignored")
	await wait_open()
	check(wall().passage_open and not wall().visible and wall().get_node("Shape").disabled and entrance_hit().is_empty(), "completed fade hides mask and removes entrance collision")
	check(sweep(Vector2(544,64), Vector2(70,0)) == null and level.player.position.x > 600, "real player can cross revealed entrance")
	check(not wall().receive_player_attack(1.0, SlicePlayer.DamageSource.CONTACT_MELEE) and reveal_sounds == 1 and reveal_signals == 1, "repeated attacks never replay reveal or SFX")
	level.player.position = Vector2(704,64)
	await frames(4)
	check(chest().player_near(), "revealed authored chest becomes eligible through overlap")
	level.player.set_physics_process(true)
	await place(Vector2(655,64))
	check(hp().used and progress.has_hp_bonus("n4_hp_01"), "revealed authored HP is collected through actual body overlap")
	await spawn(LEVELS[2])
	check(wall().opened and wall().passage_open and not wall().visible and entrance_hit().is_empty() and hp().used, "scene reinstantiation immediately restores secret and HP acquisition")
	check(reveal_sounds == 1 and reveal_signals == 1, "acquired scene reload emits no reveal SFX")
	# A real swept arrow on a fresh production wall verifies the second attack path.
	var projectile_wall = load("res://scenes/secret_wall.tscn").instantiate()
	projectile_wall.secret_id = "projectile-fixture"
	projectile_wall.position = Vector2(100,144)
	level.add_child(projectile_wall)
	var arrow = load("res://scripts/arrow.gd").new()
	level.add_child(arrow)
	arrow.global_position = Vector2(75,128)
	arrow.setup(1)
	await frames(8)
	check(projectile_wall.opened and not projectile_wall.passage_open and not is_instance_valid(arrow), "actual swept projectile starts production reveal and is consumed")
	await wait_open()
	check(projectile_wall.passage_open, "projectile revelation also releases passage only after fade")
	await finish("secret wall reveal")

extends SceneTree
const MOB = preload("res://scripts/run019_enemy.gd")
const ATTACK = preload("res://scripts/run019_enemy_attack.gd")
class RegisteredRoom extends Node2D:
	var registered: Array[Node] = []
	func register_enemy(enemy: Node) -> void: registered.append(enemy)

var checks: int = 0
var failures: int = 0
var room: Node2D
var player: SlicePlayer
var reward: int = 0
var deaths: int = 0

func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count):
		await physics_frame
		await process_frame
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", label)
	if not ok: failures += 1
func solid(at: Vector2, size: Vector2) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.position = at
	body.collision_layer = 1
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = size
	body.add_child(shape)
	room.add_child(body)
	return body
func fixture(at: Vector2 = Vector2(150, 200), floor_width: float = 600.0) -> void:
	if is_instance_valid(room):
		paused = true
		for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
			for emitter in room.find_children("*", audio_type, true, false): emitter.stop()
		# --fixed-fps advances timers faster than the independent audio thread.
		OS.delay_msec(300)
		room.queue_free()
		await frames(2)
	paused = false
	room = RegisteredRoom.new()
	root.add_child(room)
	current_scene = room
	solid(Vector2(100, 208), Vector2(floor_width, 16))
	player = load("res://scenes/player.tscn").instantiate()
	player.position = at
	room.add_child(player)
	player.controls_enabled = false
	await frames(5)
func mob(scene: String, at: Vector2 = Vector2(100, 200)) -> CharacterBody2D:
	var enemy = load("res://scenes/" + scene + ".tscn").instantiate()
	enemy.position = at
	room.add_child(enemy)
	return enemy
func reward_received(value: int, _at: Vector2) -> void:
	reward += value
	deaths += 1

func run() -> void:
	await fixture(Vector2(300, 200))
	var profiles := [["red_slime", 2.0, 1], ["bloated_slime", 5.0, 5], ["skeleton_warrior", 2.0, 1], ["skeleton_archer", 2.0, 1], ["blight_sorcerer", 2.0, 1], ["chud_blob", 10.0, 5], ["possessed_skull", 1.0, 1]]
	for profile in profiles:
		var enemy = mob(profile[0])
		enemy.set_physics_process(false)
		check(enemy.health == profile[1] and enemy.bonus_reward == profile[2], "%s HP/reward table" % profile[0])
		reward = 0
		deaths = 0
		enemy.defeated.connect(reward_received)
		enemy.take_damage(0.2, Vector2(40, -20))
		check(enemy.health_units == HealthUnits.from_hp(profile[1]) - 2, "%s exact fractional hit without invulnerability" % profile[0])
		enemy.take_damage(20, Vector2.ZERO)
		enemy.take_damage(20, Vector2.ZERO)
		check(deaths == 1 and reward == profile[2], "%s unique defeat" % profile[0])
		await frames(20)

	await fixture(Vector2(330, 200))
	player.set_physics_process(false)
	var warrior = mob("skeleton_warrior")
	warrior.chase_speed = 0
	warrior.patrol_speed = 0
	await frames(2)
	check(room.get("registered").has(warrior), "dynamic ground enemy registers with level ancestor")
	check(warrior.aggro, "warrior acquires visible player at 230px")
	player.position = Vector2(380, 200)
	await frames(3)
	check(warrior.aggro and warrior.aggro_lost_time == 0.0, "exit envelope retains visible player at 280px without countdown")
	player.position = Vector2(160, 200)
	var wall := solid(Vector2(132, 160), Vector2(12, 80))
	await frames(60)
	check(warrior.aggro, "brief terrain occlusion retains aggro")
	paused = true
	var paused_loss: float = warrior.aggro_lost_time
	await frames(10)
	check(warrior.aggro_lost_time == paused_loss, "pause freezes aggro loss countdown")
	paused = false
	wall.queue_free()
	await frames(2)
	check(warrior.aggro and warrior.aggro_lost_time == 0.0, "restored visibility resets loss countdown")
	wall = solid(Vector2(132, 160), Vector2(12, 80))
	await frames(125)
	check(not warrior.aggro, "continuous occlusion loses aggro after two seconds")
	await frames(3)
	check(not warrior.aggro, "terrain blocks fresh aggro acquisition")
	wall.queue_free()
	player.position = Vector2(380, 200)
	await frames(2)
	check(not warrior.aggro, "exit envelope cannot acquire a fresh player at 280px")
	player.position = Vector2(160, 200)
	await frames(2)
	check(warrior.aggro, "aggro reacquired within acquisition rectangle")
	player.position = Vector2(600, 200)
	await frames(60)
	check(warrior.aggro, "rectangle exit retains aggro during grace period")
	await frames(65)
	check(not warrior.aggro, "continuous exit loses aggro after two seconds")
	warrior.position = Vector2(170, 200)
	warrior.patrol_speed = 24
	await frames(2)
	check(warrior.velocity.x < 0, "loss returns toward original patrol segment without teleport")
	player.position = Vector2(200, 200)
	await frames(2)
	check(warrior.aggro, "living player reacquired before death")
	player.dead = true
	await frames(2)
	check(not warrior.aggro and warrior.pending_attack == &"", "player death bypasses aggro grace immediately")

	await fixture(Vector2(130, 200))
	warrior = mob("skeleton_warrior", Vector2(110, 200))
	await frames(2)
	check(warrior.windup_time > 0 and player.health_units == 30, "melee windup telegraphs before damage")
	paused = true
	var paused_windup: float = warrior.windup_time
	await frames(5)
	check(warrior.windup_time == paused_windup, "pause freezes melee windup")
	paused = false
	var pending: float = warrior.windup_time
	warrior.take_damage(0.2, Vector2(-30, 0))
	check(warrior.windup_time == pending and warrior.knockback_time > 0, "hit recoils without interrupting windup")
	await frames(22)
	check(player.health_units == 25, "released warrior melee deals half HP in physical room")

	await fixture(Vector2(130, 200))
	warrior = mob("skeleton_warrior", Vector2(110, 200))
	warrior.windup_duration = 3.0
	await frames(2)
	player.set_physics_process(false)
	player.position = Vector2(600, 200)
	await frames(125)
	check(not warrior.aggro and warrior.pending_attack == &"" and player.health_units == 30, "delayed aggro loss cancels unreleased melee")

	await fixture(Vector2(160, 200), 120)
	warrior = mob("skeleton_warrior", Vector2(145, 200))
	warrior.melee_range = 0
	player.set_physics_process(false)
	player.position = Vector2(200, 200)
	await frames(80)
	check(warrior.global_position.x <= 152 and warrior.is_on_floor(), "chase stops before unsupported edge")

	await fixture(Vector2(180, 200))
	var archer = mob("skeleton_archer")
	await frames(3)
	check(archer.aggro and archer.velocity.x == 0 and archer.windup_time > 0, "archer stationary with visible windup")
	await frames(19)
	check(archer.active_attacks.size() == 1, "archer releases a projectile")
	player.set_physics_process(false)
	player.position = Vector2(600, 200)
	await frames(125)
	check(not archer.aggro and is_instance_valid(archer.active_attacks[0]), "released arrow persists through delayed aggro loss")
	var attack = archer.active_attacks[0]
	archer.take_damage(20, Vector2.ZERO)
	check(attack.spent and not attack.is_physics_processing(), "source death disables projectile before deferred deletion")
	await frames(2)
	check(not is_instance_valid(attack), "source death removes released arrow")

	await fixture(Vector2(180, 200))
	archer = mob("skeleton_archer")
	await frames(65)
	check(player.health_units == 25 and player.knockback_time == 0 and player.hit_stun_time == 0, "enemy projectile hits half HP without recoil/hit-stun")
	# A real impact frees the source-owned projectile, leaving a stale typed array
	# entry until the next release. Exercise that lifecycle without queue_free or
	# calling the release method: the same living archer must fire again naturally.
	var spent_arrow = archer.active_attacks[0]
	check(not is_instance_valid(spent_arrow), "first physical impact leaves freed projectile reference for pruning")
	await frames(55)
	check(archer.active_attacks.size() == 1 and is_instance_valid(archer.active_attacks[0]), "subsequent real archer release prunes freed reference and owns new projectile")
	await frames(30)
	check(player.health_units == 20, "second real projectile still reaches player after stale reference pruning")

	await fixture(Vector2(180, 200))
	archer = mob("skeleton_archer")
	await frames(21)
	wall = solid(Vector2(150, 180), Vector2(8, 40))
	archer.cooldown = 0.0
	await frames(45)
	check(player.health_units == 30, "released arrow blocked by subsequently added terrain")
	check(archer.aggro and archer.pending_attack == &"" and archer.active_attacks.size() == 1, "occlusion grace retains aggro without starting new ranged attacks")

	await fixture(Vector2(180, 200))
	var sorcerer = mob("blight_sorcerer")
	await frames(22)
	check(sorcerer.active_attacks.size() == 1, "sorcerer releases announced ground zone")
	attack = sorcerer.active_attacks[0]
	var fixed_point: Vector2 = attack.global_position
	paused = true
	var timer: float = attack.elapsed
	await frames(8)
	check(attack.elapsed == timer, "pause freezes ground warning")
	paused = false
	await frames(45)
	check(player.health_units == 30, "ground warning has no early damage")
	await frames(18)
	check(player.health_units == 10, "ground explosion deals exactly 2 HP once after one second")
	await frames(4)
	check(player.health_units == 10, "ground blast cannot repeat its impact")

	await fixture(Vector2(180, 200))
	sorcerer = mob("blight_sorcerer")
	await frames(22)
	attack = sorcerer.active_attacks[0]
	fixed_point = attack.global_position
	player.position = Vector2(230, 200)
	await frames(20)
	check(attack.global_position == fixed_point, "announced ground point never follows moving player")
	# Freeze the committed warning to inspect ownership after the longer grace.
	attack.set_physics_process(false)
	player.set_physics_process(false)
	player.position = Vector2(800, 200)
	await frames(125)
	check(not sorcerer.aggro and is_instance_valid(attack), "committed zone survives delayed aggro loss")
	sorcerer.take_damage(20, Vector2.ZERO)
	await frames(2)
	check(not is_instance_valid(attack), "source death cancels pending ground zone")

	await fixture(Vector2(100, 200))
	var red = mob("red_slime", Vector2(100, 200))
	await frames(2)
	check(player.health_units == 15, "Red real contact deals 1.5 HP")
	check(room.get("registered").has(red), "dynamic Red registers with level ancestor")
	await fixture(Vector2(180, 200))
	red = mob("red_slime")
	await frames(3)
	check(red.velocity.x < 0, "Red patrol ignores player to its right without aggro")
	await fixture(Vector2(100, 200))
	var skull_contact = mob("possessed_skull", Vector2(100, 188))
	await frames(2)
	check(player.health_units == 25 and player.knockback_time == 0 and player.hit_stun_time == 0, "physical Skull contact uses half HP swarm profile")
	check(room.get("registered").has(skull_contact), "dynamic Skull registers with level ancestor")
	await fixture(Vector2(100, 200))
	var bloated = mob("bloated_slime", Vector2(100, 200))
	await frames(2)
	check(player.health_units == 15 and bloated.get_meta("healing_profile") == "elite", "bloated contact deals 1.5 HP and elite metadata")
	await fixture(Vector2(120, 200))
	var chud = mob("chud_blob", Vector2(100, 200))
	await frames(23)
	check(player.health_units == 10 and chud.get_meta("healing_profile") == "elite", "Chud melee deals 2 HP and elite metadata")

	await fixture(Vector2(330, 200))
	var zone = load("res://scenes/skull_swarm.tscn").instantiate()
	zone.position = Vector2(100, 160)
	room.add_child(zone)
	await frames(2)
	check(zone.skulls.size() == 4 and zone.get_child_count() == 4, "extended zone creates four stable slots at 230px from center")
	paused = true
	var skull_point: Vector2 = zone.skulls[0].global_position
	await frames(5)
	check(zone.skulls[0].global_position == skull_point, "pause freezes active swarm movement")
	paused = false
	reward = 0
	deaths = 0
	for skull in zone.skulls:
		skull.defeated.connect(reward_received)
		var motion: Vector2 = skull.velocity
		skull.take_damage(0.2, Vector2(100, -100))
		check(skull.velocity == motion and skull.get_meta("healing_profile") == "skull", "skull hit has no recoil and cannot heal")
		skull.take_damage(1, Vector2.ZERO)
	await frames(3)
	check(zone.get_child_count() == 0 and reward == 4, "first four kills pay four shards; no replacement")
	player.position = Vector2(350, 200)
	await frames(2)
	player.position = Vector2(100, 200)
	await frames(2)
	check(zone.skulls.size() == 0 and zone.get_child_count() == 0, "reentry cannot respawn four defeated slots")
	check(reward == 4 and deaths == 4, "exhausted slots preserve four kills and four shard budget")
	zone.reset_attempt()
	await frames(2)
	check(zone.skulls.size() == 4 and not zone.rewarded_slots.has(true), "attempt reset restores four slot eligibility")
	zone.skulls[1].take_damage(1, Vector2.ZERO)
	await frames(3)
	check(zone.rewarded_slots == [false, true, false, false], "partial kill defeats only its stable slot")
	player.position = Vector2(350, 200)
	await frames(3)
	check(zone.get_child_count() == 0 and reward == 4, "exit despawns survivors without rewards")
	player.position = Vector2(100, 200)
	await frames(2)
	check(zone.skulls.size() == 3 and zone.get_child_count() == 3 and zone.rewarded_slots[1], "partial reentry restores only three surviving slots")
	player.take_damage(0, Vector2.ZERO, SlicePlayer.DamageSource.VOID)
	await frames(3)
	check(zone.get_child_count() == 0 and not zone.occupied, "player death clears swarm immediately")

	# Keep emitters alive while the audio server drains stopped random streams;
	# sleeping only after queue_free cannot protect their playback teardown.
	paused = true
	for audio_type in ["AudioStreamPlayer", "AudioStreamPlayer2D"]:
		for emitter in root.find_children("*", audio_type, true, false): emitter.stop()
	OS.delay_msec(300)
	room.queue_free()
	await frames(3)
	paused = false
	OS.delay_msec(300)
	print("RESULT ", checks, " RUN019 enemy checks; ", failures, " failures")
	quit(failures)

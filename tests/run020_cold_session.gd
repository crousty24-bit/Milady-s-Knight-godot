extends "res://tests/run020_campaign.gd"
# Three genuinely separate Godot processes share only this isolated durable save.
const COLD_SAVE = "user://run020-cold.json"
func run() -> void:
	progress = root.get_node("Progression")
	progress.storage_path = COLD_SAVE
	progress.persistence_enabled = true
	var args := OS.get_cmdline_user_args()
	var stage: String = args[0] if not args.is_empty() else ""
	check(stage in ["prepare", "reopen", "reset"], "cold stage is explicitly selected")
	if stage == "prepare":
		delete_save(COLD_SAVE)
		check(progress.new_game() == OK and progress.settle_level(100, LEVELS[2]) == OK, "isolated durable bank100 and N4 resume setup")
		await spawn(LEVELS[2])
		await reveal_secret()
		level.player.health_units = 10
		await place(level.get_node("Items/HpBonus").position)
		check(progress.has_hp_bonus("n4_hp_01") and level.player.health_units == 20 and level.player.max_health_units == 40, "physical authored heart commits before process closure")
		var rare = level.get_node("Items/RareChest")
		check(rare.kind == "rare", "cold authored secret chest remains a real rare chest")
		rare.offer = {"item":"Longsword1", "upgrade":""} # Deterministic offer setup only.
		await place(rare.position)
		await tap("interact")
		await tap("interact")
		check(progress.equipment.melee == "Longsword1" and progress.banked_shards == 70, "physical paid acceptance saves equipment and bank")
		await collect_coins()
		await place(level.get_node("Exploration/CoinDoor").position + Vector2(-24, 0))
		await tap("interact")
		await place(level.get_node("Exploration/MechanismButton").position)
		await tap("interact")
		check(level.gold == 36 and level.get_node("Exploration/CoinDoor").opened and level.get_node("Exploration/MechanismDoor").opened, "closing attempt contains physical coins and opened doors")
		level.player.activate_magic_shield() # Attempt-state setup for cold reset assertion.
		level.bonus = 5 # Unsettled gains setup, deliberately never settled.
	else:
		check(progress.load_progress() == OK and progress.hp_bonus_count() == 1 and progress.permanent_flags.get("secret:n4_secret_01", false) and progress.equipment.melee == "Longsword1" and progress.banked_shards == 70, "fresh process reads durable N4 acquisitions and bank")
		var menu = load("res://scenes/game.tscn").instantiate()
		root.add_child(menu)
		current_scene = menu
		await frames(8)
		await tap("move_down")
		await tap("interact")
		await frames(12)
		level = current_scene
		check(level.scene_file_path == LEVELS[2], "keyboard Continue returns to the real N4 saved scene")
		if level.scene_file_path != LEVELS[2]:
			await finish("run020 cold " + stage)
			return
		check(not level.player.dead and level.player.health_units == 40 and level.player.max_health_units == 40 and level.player.equipment.melee == "Longsword1", "cold Continue restores equipment and heals durable maximum")
		check(level.get_node("Items/HpBonus").used and level.get_node("Exploration/SecretWall").opened and not level.get_node("Exploration/SecretWall").visible, "cold Continue removes heart and leaves secret already open")
		check(level.gold == 0 and level.bonus == 0 and not level.gate.opened and not level.get_node("Exploration/CoinDoor").opened and not level.get_node("Exploration/MechanismDoor").opened and not level.get_node("Exploration/MechanismButton").active, "cold process resets coins gains and all authored doors mechanisms")
		check(level.player.magic_shield_time == 0.0 and not level.get_node("Items/MagicShield").used and not level.get_node("Items/RareChest").consumed and not level.get_node("Exploration/SkullSwarm").rewarded_slots.has(true), "cold attempt clears shield and restores chest skull eligibility")
		if stage == "reset":
			# new_game is the already-confirmed isolated reset transaction, rather than
			# a second keyboard flow; loading N4 afterwards checks runtime consumers.
			check(progress.new_game() == OK, "confirmed isolated New Game commits reset")
			await spawn(LEVELS[2])
			check(progress.hp_bonus_count() == 0 and progress.banked_shards == 0 and progress.equipment.melee == "Sword0" and not progress.permanent_flags.has("secret:n4_secret_01"), "New Game clears durable bank equipment heart secret")
			check(level.player.max_health_units == 30 and not level.get_node("Items/HpBonus").used and not level.get_node("Exploration/SecretWall").opened and level.player.equipment.melee == "Sword0", "reset runtime scene exposes original heart secret and baseline equipment")
			delete_save(COLD_SAVE)
	await finish("run020 cold " + stage)

extends SceneTree

var checks := 0
var failures := 0

func _initialize() -> void: call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	print("PASS " if ok else "FAIL ", message)
	if not ok: failures += 1

func boundaries(weights: Array[int], title: String) -> void:
	var total := 0
	for weight in weights: total += weight
	var cumulative := 0
	for index in range(weights.size()):
		check(ChestEconomy.weighted_index(weights, float(cumulative + weights[index] * 0.5) / total) == index, "%s interval %d" % [title, index])
		if cumulative > 0:
			var boundary := float(cumulative) / total
			check(ChestEconomy.weighted_index(weights, boundary) == index and ChestEconomy.weighted_index(weights, boundary - 0.0000001) == index - 1 and ChestEconomy.weighted_index(weights, boundary + 0.0000001) == index, "%s cumulative boundary %d" % [title, index])
		cumulative += weights[index]
	check(ChestEconomy.weighted_index(weights, 0.0) == 0 and ChestEconomy.weighted_index(weights, 0.9999999) == weights.size() - 1, title + " extreme endpoints")

func run() -> void:
	var expected := {
		"Sword": [0.5, 1.0, 24.0, 3.0, 0.5, 36.0, "melee"],
		"Longsword": [1.0, 1.5, 28.8, 3.5, 1.0, 40.8, "melee"],
		"BrutalAxe": [1.5, 1.2, 19.2, 4.0, 0.7, 31.2, "melee"],
		"DarkScythe": [2.0, 2.5, 36.0, 4.5, 2.0, 48.0, "melee"],
		"Warhammer": [1.5, 1.5, 19.2, 4.0, 1.0, 31.2, "melee"],
		"Halberds": [1.0, 1.5, 48.0, 3.5, 1.0, 60.0, "melee"],
		"Longbow": [1.0, 2.2, 176.0, 3.5, 1.7, 216.0, "ranged"],
		"ThrowingKnives": [0.5, 1.4, 104.0, 3.0, 0.9, 144.0, "ranged"],
	}
	for base in expected:
		var values: Array = expected[base]
		for level in range(6):
			var id: String = base + str(level)
			var data := WeaponCatalog.stats(id)
			var ratio := float(level) / 5.0
			check(WeaponCatalog.valid(id, values[6]) and data.level == level and is_equal_approx(data.damage, lerpf(values[0], values[3], ratio)) and is_equal_approx(data.interval, lerpf(values[1], values[4], ratio)) and is_equal_approx(data.reach, lerpf(values[2], values[5], ratio)), "catalog exact stats " + id)
		check(WeaponCatalog.upgraded(base + "2") == base + "3" and WeaponCatalog.upgraded(base + "3").is_empty() and WeaponCatalog.upgraded(base + "4").is_empty() and WeaponCatalog.upgraded(base + "5").is_empty(), "ordinary cap " + base)
	check(WeaponCatalog.label("BrutalAxe2") == "Brutal Axe 2" and WeaponCatalog.label("ThrowingKnives1") == "Throwing Knives 1", "readable labels")
	for invalid in ["", "Sword", "Sword00", "Sword6", "Sword-1", "Legendary0", "FireGauntlet0", "Longbow1.0"]:
		check(not WeaponCatalog.valid(invalid) and WeaponCatalog.upgraded(invalid).is_empty(), "reject invalid or excluded " + invalid)
	check(not WeaponCatalog.valid("Sword0", "ranged") and not WeaponCatalog.valid("Longbow0", "melee"), "slot validation")

	var economy := ChestEconomy.new()
	var common_prices := [5, 8, 12, 17]
	var rare_prices := [15, 23, 34, 51]
	for count in range(4):
		check(economy.price("common", 2) == common_prices[count] and economy.price("rare", 2) == rare_prices[count], "N2 escalating price %d" % count)
		economy.paid("common")
		check(economy.counts.rare == count, "common payment leaves rare count %d" % count)
		economy.paid("rare")
	var fresh := ChestEconomy.new()
	var bases := [5, 7, 10, 15, 22, 34, 50, 75]
	for world in range(2, 10):
		check(fresh.price("common", world) == bases[world - 2] and fresh.price("rare", world) == 3 * bases[world - 2], "initial world price %d" % world)
	var prior := fresh.counts.duplicate()
	check(fresh.price("common", 1) == -1 and fresh.price("rare", 10) == -1 and fresh.price("legendary", 2) == -1 and fresh.roll("legendary", "Sword0").is_empty() and fresh.counts == prior, "invalid requests do not mutate counters")
	for fixture in [[40, 55286662], [60, 183842343585], [75, 80503439049024], [80, 611322990278524], [85, 4642233957427536], [86, 6963350936141304]]:
		fresh.counts.common = fixture[0]
		check(fresh.price("common", 2) == fixture[1], "exact integer price at count %d" % fixture[0])
	fresh.counts.common = 90
	check(fresh.price("common", 9) == -1, "unsafe price rejected")
	fresh.counts.common = -1
	check(fresh.price("common", 2) == -1, "negative counter rejected")
	boundaries(ChestEconomy.COMMON_WEIGHTS, "common weapon")
	boundaries(ChestEconomy.RARE_WEIGHTS, "rare weapon")
	boundaries(ChestEconomy.COMMON_LEVELS, "common level")
	boundaries(ChestEconomy.RARE_LEVELS, "rare level")
	check(ChestEconomy.COMMON_WEIGHTS == [9,8,7,6,5,4,3,1] and ChestEconomy.RARE_WEIGHTS == [5,9,6,8,4,7,3,1] and ChestEconomy.COMMON_LEVELS == [40,30,20,10] and ChestEconomy.RARE_LEVELS == [70,30], "contract weight tables")
	check(ChestEconomy.weighted_index([1], -0.1) == -1 and ChestEconomy.weighted_index([1], 1.0) == -1, "out-of-range unit rolls rejected")

	# Each seeded test compares independent RNG draws, not a statistical sample.
	for kind in ["common", "rare"]:
		var saw_upgrade := false
		var saw_no_upgrade := false
		for seed_value in range(100):
			var oracle := RandomNumberGenerator.new()
			oracle.seed = seed_value
			var item_roll := oracle.randf()
			var level_roll := oracle.randf()
			var upgrade_roll := oracle.randf()
			var source := RandomNumberGenerator.new()
			source.seed = seed_value
			var subject := ChestEconomy.new(source)
			var offer := subject.roll(kind, "Sword2")
			var item_index := ChestEconomy.weighted_index(ChestEconomy.COMMON_WEIGHTS if kind == "common" else ChestEconomy.RARE_WEIGHTS, minf(item_roll, 0.9999999999999999))
			var level := ChestEconomy.weighted_index(ChestEconomy.COMMON_LEVELS if kind == "common" else ChestEconomy.RARE_LEVELS, minf(level_roll, 0.9999999999999999)) + (2 if kind == "rare" else 0)
			var upgrade_expected := upgrade_roll < (0.05 if kind == "common" else 0.15)
			saw_upgrade = saw_upgrade or upgrade_expected
			saw_no_upgrade = saw_no_upgrade or not upgrade_expected
			check(offer.item == ChestEconomy.ITEMS[item_index] + str(level) and offer.upgrade == ("Sword3" if upgrade_expected else "") and WeaponCatalog.valid(offer.item) and source.state == oracle.state, "%s independent deterministic draws seed %d" % [kind, seed_value])
			source.seed = seed_value
			var capped := subject.roll(kind, "Sword3")
			check(capped.item == offer.item and capped.upgrade.is_empty() and source.state == oracle.state, "%s capped upgrade keeps item and stream seed %d" % [kind, seed_value])
		check(saw_upgrade and saw_no_upgrade, kind + " exercises upgrade and absence")

	for world in range(1, 11):
		for elite in [false, true]:
			var expected_chance: float = 0.0 if world == 1 or world == 10 else ([0.03,0.02,0.01][mini((world - 2) / 3, 2)] if elite else [0.1,0.06,0.04][mini((world - 2) / 3, 2)])
			check(is_equal_approx(ChestEconomy.chance(world, elite), expected_chance) and ChestEconomy.chance(world, elite, true) == 0.0, "heal chance and Skull exclusion world %d elite %s" % [world, elite])
			var got_drop := false
			var got_miss := false
			for seed_value in range(400):
				var source := RandomNumberGenerator.new()
				source.seed = seed_value
				var roll_value := source.randf()
				source.seed = seed_value
				var result := ChestEconomy.heal_drop(world, elite, false, source)
				var expected_drop := (1.0 if elite else 0.5) if roll_value < expected_chance else 0.0
				if result != expected_drop:
					check(false, "heal RNG mismatch")
				got_drop = got_drop or result > 0.0
				got_miss = got_miss or result == 0.0
			check(got_miss and (got_drop or expected_chance == 0.0), "heal outcomes exercised world %d elite %s" % [world, elite])
	var skull_rng := RandomNumberGenerator.new()
	skull_rng.seed = 42
	check(ChestEconomy.heal_drop(2, false, true, skull_rng) == 0.0 and ChestEconomy.heal_drop(2, true, true, skull_rng) == 0.0, "Skull kill never gives minor or major heal")
	var chest := load("res://scenes/reward_chest.tscn").instantiate() as Area2D
	root.add_child(chest)
	check(chest.is_in_group("reward_chests") and chest.collision_layer == 0 and chest.collision_mask == 2 and chest.get_node("Shape").position == Vector2(0,-16) and chest.get_node("Shape").shape.size == Vector2(44,48) and chest.offer.is_empty() and not chest.consumed and not chest.paid and not chest.save_failed and not chest.player_near(), "chest shape and fresh attempt state")
	chest.queue_free()
	await process_frame
	print("RESULT %d checks; %d failures" % [checks, failures])
	quit(1 if failures else 0)

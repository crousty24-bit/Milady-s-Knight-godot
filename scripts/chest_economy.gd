class_name ChestEconomy
extends RefCounted

const MAX_PRICE: int = 9007199254740991 # Same exact JSON integer domain as banked shards.
const BASE_PRICES: Array[int] = [5, 7, 10, 15, 22, 34, 50, 75]
const ITEMS: Array[String] = ["Sword", "Longsword", "Halberds", "Warhammer", "BrutalAxe", "Longbow", "ThrowingKnives", "DarkScythe"]
const COMMON_WEIGHTS: Array[int] = [9, 8, 7, 6, 5, 4, 3, 1]
const RARE_WEIGHTS: Array[int] = [5, 9, 6, 8, 4, 7, 3, 1]
# Direct common rewards stop at level 2; the former level-3 share goes to level 2.
const COMMON_LEVELS: Array[int] = [40, 30, 30]
const RARE_LEVELS: Array[int] = [70, 30]

var counts: Dictionary = {"common": 0, "rare": 0}
var rng: RandomNumberGenerator

func _init(random: RandomNumberGenerator = null) -> void:
	rng = random if random != null else RandomNumberGenerator.new()
	if random == null: rng.randomize()

# -1 means invalid kind/world/count or a price outside the safe integer domain.
func price(kind: String, world_level: int) -> int:
	if not counts.has(kind) or world_level < 2 or world_level > 9: return -1
	var count: Variant = counts[kind]
	if not count is int or count < 0 or count > 90: return -1
	# Small decimal limbs keep ceil(base * 3^count / 2^count) exact even when
	# its fractional part is below float precision near MAX_PRICE.
	var limbs: Array[int] = [BASE_PRICES[world_level - 2] * (3 if kind == "rare" else 1)]
	const RADIX: int = 1000000000
	for step in range(count):
		var carry := 0
		for index in range(limbs.size()):
			var value := limbs[index] * 3 + carry
			limbs[index] = value % RADIX
			carry = value / RADIX
		if carry > 0: limbs.append(carry)
	var has_remainder := false
	for step in range(count):
		var carry := 0
		for index in range(limbs.size() - 1, -1, -1):
			var value := carry * RADIX + limbs[index]
			limbs[index] = value / 2
			carry = value % 2
		has_remainder = has_remainder or carry != 0
	var amount := 0
	for index in range(limbs.size() - 1, -1, -1):
		if amount > (MAX_PRICE - limbs[index]) / RADIX: return -1
		amount = amount * RADIX + limbs[index]
	if has_remainder:
		if amount == MAX_PRICE: return -1
		amount += 1
	return amount

func paid(kind: String) -> void:
	if counts.has(kind) and counts[kind] is int and counts[kind] >= 0 and counts[kind] < MAX_PRICE:
		counts[kind] += 1

# Half-open cumulative intervals: a roll on a boundary belongs to the next item.
static func weighted_index(weights: Array[int], unit_roll: float) -> int:
	if weights.is_empty() or unit_roll < 0.0 or unit_roll >= 1.0: return -1
	var total: int = 0
	for weight in weights:
		if weight <= 0: return -1
		total += weight
	var position := unit_roll * total
	var cumulative: int = 0
	for index in range(weights.size()):
		cumulative += weights[index]
		if position < cumulative: return index
	return weights.size() - 1

func roll(kind: String, active_item: String) -> Dictionary:
	if kind not in ["common", "rare"]: return {}
	# randf can return 1, so normalize its endpoint into the final interval.
	var item_index := weighted_index(COMMON_WEIGHTS if kind == "common" else RARE_WEIGHTS, minf(rng.randf(), 0.9999999999999999))
	var level := weighted_index(COMMON_LEVELS if kind == "common" else RARE_LEVELS, minf(rng.randf(), 0.9999999999999999))
	if kind == "rare": level += 2
	var upgrade_roll := rng.randf()
	var upgrade := WeaponCatalog.upgraded(active_item) if upgrade_roll < (0.05 if kind == "common" else 0.15) else ""
	return {"item": ITEMS[item_index] + str(level), "upgrade": upgrade}

static func chance(world_level: int, elite: bool, skull: bool = false) -> float:
	if skull or world_level < 2 or world_level > 9: return 0.0
	if world_level <= 4: return 0.03 if elite else 0.10
	if world_level <= 7: return 0.02 if elite else 0.06
	return 0.01 if elite else 0.04

static func heal_drop(world_level: int, elite: bool, skull: bool, random: RandomNumberGenerator) -> float:
	# Even full health must call this once per actual kill; the caller caps the heal.
	var roll_value := random.randf()
	return (1.0 if elite else 0.5) if roll_value < chance(world_level, elite, skull) else 0.0

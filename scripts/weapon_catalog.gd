class_name WeaponCatalog
extends RefCounted

# Standard equipment only. Reach is physical pixels, including fractional melee reach.
const BASES: Dictionary = {
	"Sword": [0.5, 1.0, 1.0, "melee", "Sword"],
	"Longsword": [1.0, 1.5, 1.2, "melee", "Longsword"],
	"BrutalAxe": [1.5, 1.2, 0.8, "melee", "Brutal Axe"],
	"DarkScythe": [2.0, 2.5, 1.5, "melee", "Dark Scythe"],
	"Warhammer": [1.5, 1.5, 0.8, "melee", "Warhammer"],
	"Halberds": [1.0, 1.5, 2.0, "melee", "Halberds"],
	"Longbow": [1.0, 2.0, 12.0, "ranged", "Longbow"],
	"ThrowingKnives": [0.5, 1.3, 7.0, "ranged", "Throwing Knives"],
}

static func stats(id: String) -> Dictionary:
	if id.length() < 2: return {}
	var base_id := id.left(-1)
	var digit := id.right(1)
	if not BASES.has(base_id) or digit not in ["0", "1", "2", "3", "4", "5"]: return {}
	var level := int(digit)
	var base: Array = BASES[base_id]
	var ranged: bool = base[3] == "ranged"
	return {
		"damage": float(base[0]) + 0.5 * level,
		"interval": float(base[1]) - 0.1 * level,
		"reach": (float(base[2]) + (0.5 if ranged else 0.1) * level) * (16.0 if ranged else 24.0),
		"slot": base[3], "name": base[4], "level": level,
	}

static func valid(id: String, slot: String = "") -> bool:
	var data := stats(id)
	return not data.is_empty() and (slot.is_empty() or data.slot == slot)

static func label(id: String) -> String:
	var data := stats(id)
	return "%s %d" % [data.name, data.level] if not data.is_empty() else ""

static func upgraded(id: String) -> String:
	var data := stats(id)
	return id.left(-1) + str(data.level + 1) if not data.is_empty() and data.level < 3 else ""

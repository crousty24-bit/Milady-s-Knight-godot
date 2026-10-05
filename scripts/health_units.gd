class_name HealthUnits
extends RefCounted

const PER_HP: int = 10

static func from_hp(value: float) -> int:
	var units := roundi(value * PER_HP)
	assert(is_equal_approx(value * PER_HP, float(units)), "Health values must use tenths of an HP")
	return units

static func to_hp(units: int) -> float:
	return float(units) / PER_HP

static func format_hp(units: int) -> String:
	return str(floori(float(units) / PER_HP)) if units % PER_HP == 0 else "%.1f" % to_hp(units)

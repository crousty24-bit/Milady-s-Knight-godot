class_name WeaponArt
extends RefCounted
# RUN-018 presentation (Claude): held weapons drawn at their exact gameplay reach.
# Port of tools/art/run018/weapon_raster.py (same strips, sampling and outline): a strip column
# covers the shaft distance t from the hand, its last `head` columns stay on the tip and the
# middle repeats, so RANGE x 24 px is drawn without rescaling pixels. Purely visual.
const RIG = preload("res://assets/run018/knight/knight_rig.gd")
const STRIP_TEXTURE = preload("res://assets/run018/knight/weapon_strips.png")
const OUTLINE := Color8(0x17, 0x13, 0x1b)
const LIGHT := Vector2(0.5, -0.65)
const STEP := 0.25
const SMEAR_COLORS := [Color8(0xff, 0xfb, 0xe8), Color8(0xf2, 0xe2, 0xa8), Color8(0xc9, 0xb9, 0x8a), Color8(0x8f, 0x98, 0xaa)]
# Long shafts use the rig's carry angle outside the contact window.
const POLES := ["DarkScythe", "Halberds"]
# While a ranged weapon is active: strip, length and angle (null: the rig's belt angle).
const STOWED := {
	"Sword": ["Scabbard", 8.5, null], "Longsword": ["ScabbardLong", 11.5, null],
	"BrutalAxe": ["BrutalAxe", 12.0, 2.15], "Warhammer": ["Warhammer", 12.0, 2.15],
	"DarkScythe": ["DarkScythe", 26.0, -2.3], "Halberds": ["Halberds", 30.0, -2.3],
}
static var _strips: Image
static var _cache := {}

# Rasterised weapon for a rig slot: {"texture", "origin" (rig pixel of the top-left corner)} or {}.
static func held(strip: String, hand: Vector2, angle: float, reach: float) -> Dictionary:
	var key := "w|%s|%.4f|%.4f|%.5f|%.3f" % [strip, hand.x, hand.y, angle, reach]
	if _cache.has(key): return _cache[key]
	var pixels := _rasterize(strip, hand, angle, reach)
	var result := _to_texture(pixels)
	_cache[key] = result
	return result

static func smear(hand: Vector2, a0: float, a1: float, heavy: bool, reach: float) -> Dictionary:
	var key := "s|%.4f|%.4f|%.5f|%.5f|%s|%.3f" % [hand.x, hand.y, a0, a1, heavy, reach]
	if _cache.has(key): return _cache[key]
	var pixels := {}
	var span := a1 - a0
	if absf(span) >= 0.05:
		var r_out := reach + 0.6
		for iy in range(floori(hand.y - r_out - 2.0), ceili(hand.y + r_out + 2.0) + 1):
			for ix in range(floori(hand.x - r_out - 2.0), ceili(hand.x + r_out + 2.0) + 1):
				var dx := ix + 0.5 - hand.x
				var dy := iy + 0.5 - hand.y
				var r := sqrt(dx * dx + dy * dy)
				if r < 7.0 or r > r_out: continue
				var ang := atan2(dy, dx)
				var rel := fposmod(ang - a0, TAU) if span > 0.0 else fposmod(a0 - ang, TAU)
				if rel > absf(span): continue
				var lead := rel / absf(span)
				var thick := (3.0 if heavy else 2.0) + (9.0 if heavy else 6.5) * lead * lead
				if r < r_out - thick: continue
				var k := lead * (0.55 + 0.45 * (r - (r_out - thick)) / thick)
				var index := 0 if k > 0.72 else 1 if k > 0.45 else 2 if k > 0.24 else 3 if k > 0.1 else -1
				if index >= 0: pixels[Vector2i(ix, iy)] = SMEAR_COLORS[index]
	var result := _to_texture(pixels)
	_cache[key] = result
	return result

static func _rasterize(strip: String, hand: Vector2, angle: float, reach: float) -> Dictionary:
	if _strips == null: _strips = STRIP_TEXTURE.get_image()
	var meta: Array = RIG.STRIPS[strip]
	var y0: int = meta[0]
	var width: int = meta[1]
	var rows: int = meta[2]
	var grip: float = meta[3]
	var axis: float = meta[4]
	var stretch: int = meta[6]
	var head: int = meta[7]
	var d := Vector2(cos(angle), sin(angle))
	var n := Vector2(-d.y, d.x)
	var top: int = y0 + (rows if n.dot(LIGHT) > 0.0 else 0)
	var pixels := {}
	var steps := floori((reach + grip) / STEP + 0.000001)
	for k in range(steps + 1):
		var t := -grip + k * STEP
		var column := _column(t, reach, grip, width, stretch, head)
		for r in range(rows):
			var color := _strips.get_pixel(column, top + r)
			if color.a <= 0.0: continue
			var offsets := [r - axis]
			if r + 1 < rows and _strips.get_pixel(column, top + r + 1).a > 0.0: offsets.append(r - axis + 0.5)
			for s in offsets:
				var at: Vector2 = hand + d * t + n * s
				pixels[Vector2i(floori(at.x), floori(at.y))] = color
	var ring := {}
	for q in pixels:
		for step in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var p: Vector2i = q + step
			if not pixels.has(p): ring[p] = OUTLINE
	ring.merge(pixels, true)
	return ring

static func _column(t: float, reach: float, grip: float, width: int, stretch: int, head: int) -> int:
	var u := t + grip
	if t > reach - head:
		return clampi(width - head + floori(t - (reach - head)), 0, width - 1)
	if u < stretch:
		return maxi(0, floori(u))
	var period := maxi(1, width - head - stretch)
	return stretch + posmod(floori(u - stretch), period)

static func _to_texture(pixels: Dictionary) -> Dictionary:
	if pixels.is_empty(): return {}
	var lo := Vector2i(1 << 20, 1 << 20)
	var hi := -lo
	for q in pixels:
		lo = lo.min(q)
		hi = hi.max(q)
	var image := Image.create_empty(hi.x - lo.x + 1, hi.y - lo.y + 1, false, Image.FORMAT_RGBA8)
	for q in pixels:
		image.set_pixelv(q - lo, pixels[q])
	return {"texture": ImageTexture.create_from_image(image), "origin": lo}

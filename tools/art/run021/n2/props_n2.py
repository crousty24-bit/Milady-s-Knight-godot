"""N2 "Blight Town" decor props (RUN-021 aesthetic pass).

Pure Python (tools/art/pixel.py). Helpers are imported read-only from world_props.py and the
palette files. Everything is decor: dark, desaturated, no outlines, soft top-left light.
Warm light (windows, pyre) and BILE glints are tiny accents; the lights themselves are drawn by
scripts/campaign_decor.gd at the positions listed in props_n2.json.

Run:  python3 tools/art/run021/n2/props_n2.py [name ...]
Writes assets/run021/n2/props/*.png, props_n2.json, the preview boards and PROPS_REPORT.md.
"""
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
ART = os.path.join(ROOT, "tools", "art")
sys.path.insert(0, ART)
sys.path.insert(0, os.path.join(ART, "run020"))
sys.path.insert(0, os.path.join(ART, "run020_feedback"))
from pixel import Canvas, hexc, line, save_png  # noqa: E402
from palette import EMBER, STEEL, STONE, STONE_COOL, WOOD  # noqa: E402
from world_props import BONE, CLOTH, masonry_rect, mix  # noqa: E402  (read only)
from palette_run020 import MUD, ROT  # noqa: E402
from pngio import load_png  # noqa: E402

OUT = os.path.join(ROOT, "assets", "run021", "n2", "props")
PREVIEW = os.path.join(ROOT, "work", "run021", "n2pass", "preview")
REPORT = os.path.join(ROOT, "work", "run021", "n2pass", "PROPS_REPORT.md")
BILE = [hexc(c) for c in ("2e3216", "474d1f", "666d2a", "8a8d38", "b2ad52", "d4cc7e")]

# ----------------------------------------------------------------------------- materials
WD = [mix(w, MUD[1], 0.22) for w in WOOD[:4]]  # rotten timber, dark -> light
PL = [hexc("2a251c"), hexc("393428"), hexc("4d4739"), hexc("625b48")]  # dirty plaster
RF = [mix(STONE[i], ROT[i], 0.45) for i in range(4)]  # olive slate
ST = [mix(STONE[i], ROT[min(i, 4)], 0.25) for i in range(6)]  # masonry
IR = [hexc("13151a"), hexc("1f232b"), hexc("323945"), hexc("4b5463")]  # dark iron
RU = [hexc("26150f"), hexc("3f2418"), hexc("5a3522")]  # rust
CL = [hexc("23211b"), hexc("33302a"), hexc("48443a"), hexc("5d5849")]  # dirty grey cloth
ROPE = [hexc("3a3022"), hexc("5a4c34")]
VOID = hexc("0e0d0a")
ASH = [hexc("1e1b17"), hexc("302b25"), hexc("463f35"), hexc("5a5246")]


def rng(*seed):
	return random.Random("-".join(map(str, ("run021-n2",) + seed)))


# ----------------------------------------------------------------------------- primitives
def fill(c, x, y, w, h, col):
	c.rect(x, y, w, h, col)


def hl(c, x0, x1, y, col):
	for x in range(x0, x1 + 1):
		c.put(x, y, col)


def vl(c, x, y0, y1, col):
	for y in range(y0, y1 + 1):
		c.put(x, y, col)


def slab(c, x, y, w, h, ramp, tone=2):
	"""Lit box: light top/left, dark bottom/right."""
	for yy in range(y, y + h):
		for xx in range(x, x + w):
			k = tone
			if xx == x or yy == y:
				k = min(3, tone + 1)
			if xx == x + w - 1 or yy == y + h - 1:
				k = max(0, tone - 2) if (xx == x + w - 1 and yy == y + h - 1) else max(0, tone - 1)
			c.put(xx, yy, ramp[k])


def beam_h(c, x0, x1, y, th, ramp=None):
	ramp = ramp or WD
	for i in range(th):
		k = 3 if i == 0 else 0 if i == th - 1 else 2 if i == 1 else 1
		hl(c, x0, x1, y + i, ramp[k])


def beam_v(c, x, y0, y1, tw, ramp=None):
	ramp = ramp or WD
	for i in range(tw):
		k = 3 if i == 0 else 0 if i == tw - 1 else 2 if i == 1 else 1
		vl(c, x + i, y0, y1, ramp[k])


def brace(c, x0, y0, x1, y1, ramp=None, shade=True):
	"""2 px wide diagonal timber."""
	ramp = ramp or WD
	line(c, x0, y0, x1, y1, ramp[2])
	if shade:
		line(c, x0 + 1, y0, x1 + 1, y1, ramp[1])
		line(c, x0, y0 - 1 if abs(x1 - x0) > abs(y1 - y0) else y0, x1, y1 - 1 if abs(x1 - x0) > abs(y1 - y0) else y1, ramp[3])


def grime(c, x0, x1, y0, y1, col, bottom_up=True):
	"""Dithered darkening toward the bottom of a wall (splash / damp)."""
	bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
	for y in range(y0, y1 + 1):
		t = (y - y0) / max(1, y1 - y0)
		t = t if bottom_up else 1 - t
		for x in range(x0, x1 + 1):
			if c.get(x, y) is not None and t * 16 > bayer[y % 4][x % 4] + 0.5:
				c.put(x, y, col)


def recolor_dark(c, x0, y0, x1, y1, k, toward):
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			p = c.get(x, y)
			if p is not None:
				c.put(x, y, mix(p, toward, k))


def chain(c, x, y0, y1, ramp=None, wave=0):
	ramp = ramp or IR
	for i, y in enumerate(range(y0, y1 + 1)):
		xx = x + (int(round(math.sin(i * 0.5) * wave)) if wave else 0)
		c.put(xx, y, ramp[2] if i % 2 == 0 else ramp[1])
		if i % 2 == 0:
			c.put(xx + 1, y, ramp[0])


def shear(c, total, extra_w, toward_right=True):
	"""Lean: shift rows horizontally; the top moves by `total` px, the bottom stays."""
	out = Canvas(c.w + extra_w, c.h)
	for y in range(c.h):
		off = int(round((c.h - 1 - y) / (c.h - 1) * total))
		for x in range(c.w):
			p = c.px[y * c.w + x]
			if p is not None:
				out.put(x + (off if toward_right else extra_w - off), y, p)
	return out


def bricks(c, x, y, w, h, ramp, r, bw=5, bh=3, mortar=None):
	mortar = mortar or ramp[0]
	row = 0
	for yy in range(y, y + h):
		ty = (yy - y) % bh
		if ty == 0:
			row += 1
		off = (row * 2) % bw if row % 2 else 0
		for xx in range(x, x + w):
			sx = (xx - x + off) % bw
			bi = ((xx - x + off) // bw, row)
			if ty == bh - 1 or sx == bw - 1:
				col = mortar
			else:
				t = r.random() if (sx == 0 and ty == 0) else None
				col = ramp[2 if (hash(bi) + row) % 5 else 1]
				if ty == 0:
					col = ramp[3] if col is ramp[2] else ramp[2]
			c.put(xx, yy, col)


def bricks_det(c, x, y, w, h, ramp, bw=5, bh=3, mortar=None):
	mortar = mortar or ramp[0]
	for yy in range(y, y + h):
		row = (yy - y) // bh
		ty = (yy - y) % bh
		off = (bw // 2 + 1) if row % 2 else 0
		for xx in range(x, x + w):
			sx = (xx - x + off) % bw
			bi = (xx - x + off) // bw
			if ty == bh - 1 or sx == bw - 1:
				col = mortar
			else:
				col = ramp[2 if (bi * 7 + row * 3) % 5 else 1]
				if ty == 0:
					col = ramp[3 if col == ramp[2] else 2]
			c.put(xx, yy, col)


def rot_patch(c, cx, cy, rx, ry, r, k=0.9, pustules=2, glints=1, upward=False):
	"""Flat crusty rot bloom: irregular olive/mud crust with a few dark pustules and BILE glints."""
	cells = []
	for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
		for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
			d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
			if d + (r.random() - 0.5) * 0.55 < k:
				cells.append((x, y, d))
	cs = {(x, y) for x, y, _ in cells}
	for x, y, d in cells:
		top = (x, y - 1) not in cs
		left = (x - 1, y) not in cs
		col = ROT[2] if d < 0.45 else ROT[1]
		if (x * 5 + y * 3) % 7 == 0:
			col = MUD[2]
		if top or (left and (x + y) % 2):
			col = ROT[3]
		c.put(x, y, col)
	pts = r.sample(cells, min(len(cells), pustules + glints)) if cells else []
	for i, (x, y, _) in enumerate(pts):
		if i < pustules:
			c.put(x, y, MUD[0])
			c.put(x + 1, y, MUD[1])
			c.put(x, y - 1, ROT[4])
		else:
			c.put(x, y, BILE[2] if r.random() < 0.7 else BILE[3])
	return cs


def pustule(c, x, y, big=False):
	if big:
		c.put(x, y, MUD[2])
		c.put(x + 1, y, MUD[1])
		c.put(x, y + 1, MUD[1])
		c.put(x + 1, y + 1, MUD[0])
		c.put(x, y, ROT[4])
	else:
		c.put(x, y, MUD[2])
		c.put(x + 1, y, MUD[0])


def planks_v(c, x, y, w, h, r, pw=4, ramp=None, tone=0):
	ramp = ramp or WD
	px = x
	while px < x + w:
		wdt = min(pw + r.choice((0, 0, 1)), x + w - px)
		base = max(0, min(3, 1 + r.choice((0, 0, 1, 1, 2)) + tone))
		for xx in range(px, px + wdt):
			for yy in range(y, y + h):
				k = base
				if xx == px:
					k = min(3, base + 1)
				elif xx == px + wdt - 1:
					k = max(0, base - 1)
				if (yy * 3 + xx * 5) % 17 == 0:
					k = max(0, k - 1)
				c.put(xx, yy, ramp[k])
		px += wdt
	for yy in (y + 2, y + h - 3):  # nails
		for xx in range(x + 1, x + w, 5):
			c.put(xx, yy, IR[3])


def board_window(c, x, y, w, h, r, planks=3, frame=True):
	"""Dark opening boarded with crossing planks."""
	fill(c, x, y, w, h, VOID)
	fill(c, x, y + 1, 1, h - 2, hexc("191712"))
	if frame:
		beam_h(c, x - 1, x + w, y - 2, 2)
		beam_h(c, x - 1, x + w, y + h, 2, [WD[0], WD[0], WD[1], WD[2]])
		vl(c, x - 1, y, y + h - 1, WD[2])
		vl(c, x + w, y, y + h - 1, WD[0])
	ys = sorted(r.sample(range(1, h - 3), planks))
	for i, py in enumerate(ys):
		tilt = r.choice((-2, -1, 0, 1, 2))
		x0 = x - 1 + r.choice((0, 0, 1))
		x1 = x + w + (0 if i % 2 else -1)
		for xx in range(x0, x1 + 1):
			t = (xx - x0) / max(1, x1 - x0)
			yy = y + py + int(round(tilt * (t - 0.5)))
			c.put(xx, yy, WD[3])
			c.put(xx, yy + 1, WD[2])
			c.put(xx, yy + 2, WD[0])
		c.put(x0, y + py + 1, IR[3])
		c.put(x1, y + py + 1, IR[3])


def plague_cross(c, cx, y, h=10, arm=4, sway=0):
	col, hi = CLOTH[1], CLOTH[2]
	for i in range(h):
		c.put(cx, y + i, col)
		c.put(cx + 1, y + i, CLOTH[0])
	for i in range(-arm, arm + 1):
		c.put(cx + i, y + 3, col)
		c.put(cx + i, y + 4, CLOTH[0])
	c.put(cx, y + 3, hi)
	c.put(cx - arm, y + 3, hi)
	c.put(cx, y, hi)
	c.put(cx, y + h, CLOTH[0])  # drip
	c.put(cx - arm, y + 5, CLOTH[0])


def shingled_roof(c, cx, peak, eave, hw, ramp, r, flat_top=0, tile_h=4, tile_w=6, side="both"):
	"""Triangular roof. Left slope lit. Returns {y: (xl, xr)}."""
	h = eave - peak
	spans = {}
	cache = {}
	for y in range(peak, eave + 1):
		half = (y - peak + 1) * hw / (h + 1) + flat_top
		xl, xr = int(round(cx - half)), int(round(cx + half)) - 1
		spans[y] = (xl, xr)
		row = (y - peak) // tile_h
		ty = (y - peak) % tile_h
		off = (row * 3) % tile_w
		for x in range(xl, xr + 1):
			left = x < cx
			if side == "left" and not left:
				continue
			if side == "right" and left:
				continue
			sx = (x + off) % tile_w
			key = (row, (x + off) // tile_w)
			if key not in cache:
				cache[key] = r.random()
			base = 2 if left else 1
			if cache[key] < 0.18:
				base -= 1
			elif cache[key] > 0.88:
				base += 1
			base = max(0, min(3, base))
			col = ramp[base]
			if ty == tile_h - 1 or sx == tile_w - 1:
				col = ramp[max(0, base - 1)]
			elif ty == 0:
				col = ramp[min(3, base + 1)]
			if x == xl:
				col = ramp[3] if left else col
			if x == xr:
				col = ramp[0]
			c.put(x, y, col)
	return spans


def moss_spots(c, r, n, x0, x1, y0, y1, only_on=None):
	for _ in range(n):
		x, y = r.randint(x0, x1), r.randint(y0, y1)
		if c.get(x, y) is not None:
			c.put(x, y, ROT[3])
			if r.random() < 0.6:
				c.put(x + 1, y, ROT[2])


def bell(c, cx, top, size=1):
	"""Small tarnished iron-bronze bell, hung from (cx, top)."""
	b = [hexc("1a1511"), hexc("2c241b"), hexc("423629"), hexc("5c4c38")]
	rows = [(1, 0), (2, 1), (3, 1), (3, 2), (3, 2), (3, 2), (4, 3), (5, 3)]
	if size == 2:
		rows = [(1, 0), (2, 1), (3, 1), (3, 2), (4, 2), (4, 3), (5, 3), (5, 4), (6, 4), (6, 5), (7, 5)]
	for i, (half, _) in enumerate(rows):
		y = top + 1 + i
		for x in range(cx - half, cx + half + 1):
			k = 3 if x == cx - half else 0 if x == cx + half else 2 if x < cx else 1
			c.put(x, y, b[k])
	y = top + 1 + len(rows)
	half = rows[-1][0] + 1
	for x in range(cx - half, cx + half + 1):
		c.put(x, y, b[0] if x > cx else b[1])
	c.put(cx, y + 1, IR[1])  # clapper
	c.put(cx, top, IR[3])


# ============================================================================= GROUND
def house_timber_a():
	W, H = 76, 104
	c = Canvas(W, H)
	r = rng("house_a")
	cx = 38
	# ---- upper floor + jetty behind the roof.
	fill(c, 7, 42, 62, 26, PL[1])
	for y in range(42, 68):  # plaster texture + shade on the right
		for x in range(7, 69):
			if (x * 7 + y * 13) % 23 == 0:
				c.put(x, y, PL[2])
			if x > 64:
				c.put(x, y, PL[0])
			if (x * 3 + y * 5) % 29 == 0:
				c.put(x, y, PL[0])
	# exposed lath patches where plaster fell
	for px_, py_, pw_, ph_ in ((27, 56, 8, 7), (60, 47, 4, 5)):
		bricks_det(c, px_, py_, pw_, ph_, [hexc("1d1a15"), hexc("2b251d"), hexc("3a3025"), hexc("453a2c")], bw=4, bh=3)
	# upper posts and rails
	beam_v(c, 7, 42, 67, 3)
	beam_v(c, 36, 42, 67, 3)
	beam_v(c, 66, 42, 67, 3)
	beam_h(c, 7, 68, 42, 2)
	beam_h(c, 7, 68, 64, 3)
	brace(c, 27, 63, 35, 45)
	brace(c, 39, 45, 46, 63)
	brace(c, 9, 62, 13, 48)
	# left window: shuttered askew, open dark
	fill(c, 14, 48, 12, 13, VOID)
	fill(c, 14, 49, 1, 11, hexc("1a1812"))
	beam_h(c, 13, 26, 46, 2)
	beam_h(c, 13, 26, 61, 2, [WD[0], WD[0], WD[1], WD[2]])
	for i in range(0, 12):  # hanging shutter, tilted
		for j in range(0, 4):
			c.put(11 + j, 47 + i + (j // 2), WD[2] if j == 0 else WD[1] if j < 3 else WD[0])
	for yy in (49, 53, 57):
		hl(c, 11, 14, yy + 1, WD[0])
	c.put(11, 47, IR[3])
	c.put(11, 58, IR[3])
	# right window: glazed, dark, mullion and sheen (the script lights it)
	gl = [hexc("0d1114"), hexc("151b20"), hexc("1f2830")]
	fill(c, 49, 48, 11, 13, gl[0])
	fill(c, 50, 49, 4, 5, gl[1])
	fill(c, 55, 49, 4, 5, gl[1])
	fill(c, 50, 55, 4, 5, gl[1])
	fill(c, 55, 55, 4, 5, gl[0])
	vl(c, 54, 48, 60, WD[1])
	hl(c, 49, 59, 54, WD[1])
	c.put(51, 50, gl[2])
	c.put(52, 50, gl[2])
	c.put(56, 56, gl[2])
	beam_h(c, 48, 60, 46, 2)
	beam_h(c, 48, 60, 61, 2, [WD[0], WD[0], WD[1], WD[2]])
	vl(c, 48, 48, 60, WD[2])
	vl(c, 60, 48, 60, WD[0])
	# broken shutter stub on the right window
	for i in range(7):
		c.put(61, 48 + i, WD[1])
		c.put(62, 49 + i, WD[0])
	# ---- jetty beam with corbels
	beam_h(c, 4, 71, 68, 4)
	for x in range(4, 72, 4):
		c.put(x, 69, WD[3])
	for bx in (12, 36, 62):
		for i in range(4):
			hl(c, bx - 1 + i // 2, bx + 3 - i // 2, 72 + i, WD[2] if i < 2 else WD[1])
		c.put(bx, 72, WD[3])
	# ---- ground floor
	fill(c, 10, 72, 56, 25, PL[1])
	for y in range(72, 97):
		for x in range(10, 66):
			if (x * 7 + y * 11) % 21 == 0:
				c.put(x, y, PL[2])
			if x > 61:
				c.put(x, y, PL[0])
			if y < 74:
				c.put(x, y, PL[0])
	beam_v(c, 10, 72, 96, 3)
	beam_v(c, 63, 72, 96, 3)
	beam_v(c, 28, 72, 96, 2)
	beam_v(c, 46, 72, 96, 2)
	beam_h(c, 10, 65, 76, 2)
	brace(c, 13, 93, 18, 82)
	brace(c, 59, 82, 62, 92)
	board_window(c, 15, 79, 11, 12, r, 3)
	board_window(c, 50, 79, 11, 12, r, 2)
	# door with plague cross, barred by a nailed plank
	fill(c, 31, 79, 14, 18, WD[1])
	planks_v(c, 31, 79, 14, 18, r, pw=3)
	beam_h(c, 29, 46, 77, 2)
	vl(c, 30, 79, 96, WD[2])
	vl(c, 45, 79, 96, WD[0])
	plague_cross(c, 37, 80, h=10, arm=4)
	for i in range(18):  # diagonal bar nailed across
		xx = 30 + i
		yy = 93 - i * 8 // 17
		c.put(xx, yy, WD[3])
		c.put(xx, yy + 1, WD[2])
		c.put(xx, yy + 2, WD[0])
	c.put(31, 92, IR[3])
	c.put(44, 85, IR[3])
	# wall grime / rising damp
	for x in range(11, 63):
		for y in range(92 - (x * 7) % 4 - (1 if x % 5 == 0 else 0), 97):
			if c.get(x, y) is not None and c.get(x, y) in (PL[0], PL[1], PL[2]):
				c.put(x, y, ROT[1])
	# ---- stone foundation with rot
	fnd = Canvas(W, H)
	masonry_rect(fnd, 6, 97, 64, 7, ST, r, course=4, moss=ROT)
	c.blit(fnd, 0, 0)
	for x in range(6, 70):
		c.put(x, 97, ST[4] if x % 5 else ST[3])
	recolor_dark(c, 6, 97, 69, 103, 0.18, MUD[1])
	# ---- roof (left slope lit) + holes
	spans = shingled_roof(c, cx, 3, 42, 38, RF, r, flat_top=0)
	for x in range(1, 76):  # eave band & its shadow on the wall
		c.put(x, 42, RF[0])
		c.put(x, 41, RF[1] if x % 3 else RF[0])
	for x in range(1, 76):
		c.put(x, 43, WD[0]) if c.get(x, 43) is None and 3 < x < 73 else None
	hole = set()
	for y in range(15, 38):  # big break on the left slope
		xl, xr = spans[y]
		for x in range(xl, xr):
			if x < cx - 2:
				d = (x - 21) ** 2 / 100.0 + (y - 27) ** 2 / 85.0
				if d + (r.random() - 0.5) * 0.4 < 0.85:
					hole.add((x, y))
	for (x, y) in hole:
		c.put(x, y, hexc("0f0e0a"))
	for k in range(4):  # rafters across the hole (parallel to the slope)
		for t in range(0, 44):
			xx = 5 + k * 5 + t
			yy = 42 - int(t * 38 / 37)
			for dx, col in ((0, WD[3]), (1, WD[2]), (2, WD[0])):
				if (xx + dx, yy) in hole:
					c.put(xx + dx, yy, col)
	for x in range(8, 36):  # a cross batten
		if (x, 31) in hole:
			c.put(x, 31, WD[1])
	moss_spots(c, r, 16, 12, 66, 14, 38)
	for k in range(3):  # ridge cap highlights
		c.put(cx - 1 + k, 3, RF[3])
	c.put(cx, 2, RF[2])
	# ---- chimney (right), crumbled top, bottom clipped to the slope
	ch = Canvas(10, 40)
	bricks_det(ch, 0, 0, 10, 40, [hexc("1e1b17"), hexc("34302a"), hexc("48423a"), hexc("5a544a")], bw=5, bh=3)
	for x in range(10):
		ytop = 3 + (x * 5) % 4
		for y in range(0, ytop):
			ch.px[y * 10 + x] = None
	for y in range(40):
		ch.px[y * 10 + 9] = hexc("1e1b17") if ch.px[y * 10 + 9] else None
	for x in range(10):
		ch.put(x, 3 + (x * 5) % 4, ST[4])
	for x in range(10):
		sy = int(3 + (55 + x - cx) * 39 / 38) + 3
		for y in range(40):
			if y + 0 > sy - 0:
				ch.px[y * 10 + x] = None
	c.blit(ch, 55, 0)
	for y in range(8, 24):  # soot streak
		c.put(58, y, hexc("1e1b17"))
	return c


def house_timber_b():
	"""Tall narrow leaning house, right half of the roof collapsed, rot climbing from the base."""
	W0, H = 46, 112
	c = Canvas(W0, H)
	r = rng("house_b")
	cx = 22
	pl = PL

	def wall(x, y, w, h):
		fill(c, x, y, w, h, pl[1])
		for yy in range(y, y + h):
			for xx in range(x, x + w):
				if (xx * 7 + yy * 13) % 23 == 0:
					c.put(xx, yy, pl[2])
				if xx >= x + w - 3:
					c.put(xx, yy, pl[0])
				if (xx * 3 + yy * 5) % 31 == 0:
					c.put(xx, yy, pl[0])

	# top floor
	wall(4, 31, 40, 25)
	beam_v(c, 4, 31, 55, 3)
	beam_v(c, 41, 31, 55, 3)
	beam_h(c, 4, 43, 31, 2)
	beam_h(c, 4, 43, 53, 3)
	brace(c, 7, 52, 12, 35)
	brace(c, 36, 36, 40, 51)
	fill(c, 16, 37, 14, 14, VOID)
	fill(c, 16, 38, 1, 12, hexc("1a1812"))
	beam_h(c, 15, 30, 35, 2)
	beam_h(c, 15, 30, 51, 2, [WD[0], WD[0], WD[1], WD[2]])
	vl(c, 15, 37, 50, WD[2])
	vl(c, 30, 37, 50, WD[0])
	for i in range(11):  # shutter half off its hinge
		c.put(31 + i // 5, 37 + i, WD[1])
		c.put(32 + i // 5, 38 + i, WD[0])
	for i in range(8):  # rag hanging out of the window
		c.put(19 + i // 4, 51 + i // 2 + 1, CL[2] if i % 3 else CL[1])
		c.put(20 + i // 4, 51 + i // 2 + 1, CL[1])
	beam_h(c, 2, 45, 56, 4)
	for bx in (8, 22, 36):
		for i in range(3):
			hl(c, bx - 1 + i // 2, bx + 2 - i // 2, 60 + i, WD[2] if i < 2 else WD[1])
	# middle floor
	wall(6, 60, 36, 21)
	for xx in range(6, 42):
		for yy in range(60, 62):
			c.put(xx, yy, pl[0])
	beam_v(c, 6, 60, 80, 3)
	beam_v(c, 39, 60, 80, 3)
	beam_v(c, 22, 60, 80, 2)
	beam_h(c, 6, 41, 78, 3)
	board_window(c, 11, 65, 8, 11, r, 3)
	board_window(c, 27, 65, 8, 11, r, 2)
	beam_h(c, 4, 43, 81, 3)
	# ground floor
	wall(9, 84, 30, 21)
	for xx in range(9, 39):
		for yy in range(84, 86):
			c.put(xx, yy, pl[0])
	beam_v(c, 9, 84, 104, 3)
	beam_v(c, 36, 84, 104, 3)
	beam_h(c, 9, 38, 86, 2)
	# barred door: crossed planks, nailed
	fill(c, 17, 89, 13, 16, WD[1])
	planks_v(c, 17, 89, 13, 16, r, pw=3)
	beam_h(c, 15, 31, 87, 2)
	vl(c, 16, 89, 104, WD[2])
	vl(c, 30, 89, 104, WD[0])
	for sgn in (1, -1):
		for i in range(14):
			xx = 16 + i + 1
			yy = (92 + i * 9 // 13) if sgn == 1 else (104 - i * 9 // 13)
			c.put(xx, yy, WD[3])
			c.put(xx, yy + 1, WD[2])
			c.put(xx, yy + 2, WD[0])
	c.put(18, 93, IR[3])
	c.put(28, 102, IR[3])
	# foundation
	fb = Canvas(W0, H)
	masonry_rect(fb, 7, 105, 34, 7, ST, r, course=4, moss=ROT)
	c.blit(fb, 0, 0)
	recolor_dark(c, 7, 105, 40, 111, 0.18, MUD[1])
	for x in range(7, 41):
		c.put(x, 105, ST[4] if x % 4 else ST[3])
	# roof: left slope intact, right side collapsed to bare rafters
	spans = shingled_roof(c, cx, 2, 31, 25, RF, r, side="left")
	for y in range(2, 32):
		xl, xr = spans[y]
		for x in range(cx, xr + 1):  # clear right slope
			c.px[y * W0 + x] = None
	for x in range(0, 46):
		c.put(x, 31, RF[0]) if x < cx + 1 else None
	# tattered edge of the left slope: ragged lower-left eave
	# right-hand rafters: bare, snapped at different heights
	for k, (x1, top) in enumerate(((27, 12), (32, 17), (37, 8), (42, 23))):
		x0 = cx
		y0 = 2
		xe, ye = 25 + 5 * k + 1, 30
		xe = min(xe, 44)
		for t in range(60):
			tt = t / 59
			xx = int(round(cx + 1 + (xe - cx - 1) * tt))
			yy = int(round(3 + (ye - 3) * tt))
			if yy < top:
				continue
			c.put(xx, yy, WD[3])
			c.put(xx + 1, yy, WD[1])
			c.put(xx, yy + 1, WD[0])
	# dark attic visible between the rafters
	for y in range(5, 31):
		for x in range(cx + 1, 45):
			t = (y - 3) / 27
			if x < cx + 1 + t * 22 and c.get(x, y) is None and (x + y) % 5 < 4 and x < 40:
				c.put(x, y, hexc("100f0b"))
	# purlin and broken ridge stub
	for x in range(cx - 1, cx + 3):
		c.put(x, 2, WD[3])
		c.put(x, 3, WD[1])
	for x in range(14, 36):  # eave band
		c.put(x, 31, RF[0])
	moss_spots(c, r, 8, 3, cx - 2, 10, 28)
	# rot climbing from the base (left side)
	rr = rng("house_b_rot")
	rot_patch(c, 12, 103, 7, 4, rr, k=1.0, pustules=3, glints=1)
	rot_patch(c, 36, 104, 5, 3, rr, k=0.95, pustules=2, glints=0)
	for y in range(78, 104):  # tendrils up the wall
		x = 10 + int(2 * math.sin(y * 0.35)) + (104 - y) // 14
		if y % 3 != 2:
			c.put(x, y, ROT[2])
			c.put(x + 1, y, ROT[1])
	rot_patch(c, 13, 92, 4, 3, rr, k=0.9, pustules=2, glints=1)
	rot_patch(c, 17, 79, 3, 2, rr, k=0.8, pustules=1, glints=0)
	out = shear(c, 8, 10, toward_right=True)
	return out


def cathedral_ruin():
	W, H = 72, 108
	c = Canvas(W, H)
	r = rng("cathedral")
	S = ST

	def stone(x0, y0, w, h, course=6):
		masonry_rect(c, x0, y0, w, h, S, r, course=course, moss=ROT)

	# tower shaft
	stone(5, 28, 26, 80)
	# nave front
	stone(31, 46, 37, 62)
	# silhouette of the nave: top edge falls toward the right, jagged
	for x in range(31, 68):
		top = 46 + int((x - 31) * 0.38) + (x * 7) % 4
		for y in range(46, top):
			c.px[y * W + x] = None
	for x in range(31, 68):
		for y in range(0, H):
			if c.get(x, y) is not None and c.get(x, y - 1) is None:
				c.put(x, y, S[4])
				break
	# gable remnant over the window: pointed stub
	# tower string courses
	for yy in (56, 90):
		hl(c, 4, 31, yy, S[4])
		hl(c, 4, 31, yy + 1, S[3])
		hl(c, 4, 31, yy + 2, S[0])
	# quoins on the tower edges
	for y in range(30, 108, 4):
		hl(c, 5, 6, y, S[4])
		hl(c, 5, 7, y + 1, S[3])
		hl(c, 29, 30, y + 2, S[1])
	# belfry opening with a bell
	for y in range(28, 54):
		half = 6 if y > 38 else int(6 * math.sqrt(max(0.0, 1 - ((38 - y) / 10.0) ** 2)))
		for x in range(18 - half, 18 + half + 1):
			c.put(x, y, VOID)
	for y in range(30, 54):  # arch moulding
		half = 6 if y > 38 else int(6 * math.sqrt(max(0.0, 1 - ((38 - y) / 10.0) ** 2)))
		c.put(18 - half - 1, y, S[4])
		c.put(18 + half + 1, y, S[1])
	for x in range(13, 24):
		c.put(x, 53, S[4])
		c.put(x, 54, S[0])
	beam_h(c, 12, 24, 35, 2)
	bell(c, 18, 38, size=1)
	for x in range(13, 24):
		for y in range(27, 33):
			if c.get(x, y) is None:
				pass
	# belfry roof: broken pyramid
	for y in range(4, 28):
		half = 2 + (y - 4) * 15 / 23.0
		for x in range(int(18 - half), int(18 + half) + 1):
			if x > 18 + 2 + (y - 4) * 0.5 and y < 14:
				continue  # broken right side
			col = RF[2] if x < 18 else RF[1]
			t = (y - 4) % 4
			if t == 3:
				col = RF[0]
			elif t == 0:
				col = RF[3] if x < 18 else RF[2]
			if (x + (y // 4) * 3) % 6 == 5:
				col = RF[0]
			c.put(x, y, col)
	for x in range(0, 38):
		c.put(x, 27, RF[0])
	# bare rafters at the broken top
	for k, (x0, y0, x1, y1) in enumerate(((19, 4, 24, 14), (17, 2, 19, 6), (21, 8, 28, 20))):
		line(c, x0, y0, x1, y1, WD[2])
		line(c, x0 + 1, y0, x1 + 1, y1, WD[0])
	# big pointed window on the nave
	cxw = 49
	for y in range(52, 82):
		half = 7 if y > 62 else int(7 * math.sqrt(max(0.0, 1 - ((62 - y) / 10.0) ** 2)))
		for x in range(cxw - half, cxw + half + 1):
			c.put(x, y, VOID)
	# stone moulding around the window (incomplete on the right)
	for y in range(51, 84):
		half = 7 if y > 62 else int(7 * math.sqrt(max(0.0, 1 - ((62 - y) / 10.0) ** 2)))
		c.put(cxw - half - 1, y, S[4])
		c.put(cxw - half - 2, y, S[3])
		if y > 60 or (y + (cxw + half)) % 7:
			c.put(cxw + half + 1, y, S[1])
			c.put(cxw + half + 2, y, S[0])
	# broken tracery: central mullion + circle stub
	for y in range(64, 82):
		c.put(cxw, y, S[3])
		c.put(cxw + 1, y, S[1])
	for a in range(0, 40):
		ang = a * math.tau / 40
		if not (0.3 < ang < 2.2):
			c.put(int(round(cxw + 4 * math.cos(ang))), int(round(58 + 4 * math.sin(ang))), S[3])
	for x in range(cxw - 8, cxw + 9):
		c.put(x, 82, S[4])
		c.put(x, 83, S[1])
	# pointed door: rubble-filled, not usable
	for y in range(90, 108):
		half = 6 if y > 96 else max(0, 6 - (96 - y))
		for x in range(40 - half, 40 + half + 1):
			c.put(x, y, hexc("100e0b"))
	# rubble in front of the door and across the base
	for bx, by, bw, bh in ((32, 100, 9, 8), (38, 96, 8, 12), (44, 102, 10, 6), (28, 104, 7, 4), (54, 100, 9, 8), (62, 103, 8, 5)):
		for y in range(by, by + bh):
			for x in range(bx, bx + bw):
				if y >= H:
					continue
				k = 4 if y == by else 0 if y == by + bh - 1 or x == bx + bw - 1 else 3 if x == bx else 2 if (x + y) % 3 else 1
				c.put(x, y, S[k])
	# buttresses
	def buttress(x0, w_top, steps):
		for (y0, y1, wid) in steps:
			stone(x0 + (w_top - wid) if x0 < 40 else x0, y0, wid, y1 - y0, course=5)
	# left tower buttress (stepped)
	for y0, y1, wid in ((82, 92, 3), (92, 108, 5)):
		stone(5 - wid, y0, wid, y1 - y0, course=5)
		hl(c, 5 - wid, 4, y0, S[4])
	# right buttress against the nave
	for y0, y1, x0, wid in ((58, 70, 63, 5), (70, 88, 63, 7), (88, 108, 62, 10)):
		stone(x0, y0, wid, y1 - y0, course=5)
		hl(c, x0, x0 + wid - 1, y0, S[4])
		hl(c, x0, x0 + wid - 1, y0 + 1, S[3])
		vl(c, x0 + wid - 1, y0, y1 - 1, S[0])
	# sloping weathering on the right buttress top and a broken pinnacle stub
	for i in range(5):
		hl(c, 64, 68, 58 - i if i < 1 else 58, S[3]) if i == 0 else None
	# moss / rot at the base
	for x in range(5, 68):
		if (x * 3) % 5 < 2:
			c.put(x, 107, ROT[1])
			if x % 3 == 0:
				c.put(x, 106, ROT[2])
	moss_spots(c, r, 18, 5, 66, 30, 100)
	recolor_dark(c, 0, 90, 71, 107, 0.15, MUD[1])
	# pinnacle stub on the right buttress
	for i in range(9):
		half = max(0, 3 - i // 3)
		for x in range(66 - half, 66 + half + 1):
			c.put(x, 52 + i, S[3] if x < 66 else S[1])
	c.put(66, 51, S[4])
	for x in range(63, 69):
		c.put(x, 61, S[4])
	recolor_dark(c, 0, 0, 71, 107, 0.2, hexc("100f0c"))
	rot_patch(c, 14, 105, 8, 3, rng("cath_rot"), k=0.95, pustules=2, glints=1)
	return c


def wheel(c, cx, cy, rad, broken=False, r=None):
	r = r or rng("wheel")
	for a in range(0, 120):
		ang = a * math.tau / 120
		if broken and 3.3 < ang < 4.7:
			continue
		x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
		lit = math.cos(ang - 3.9) > 0
		c.put(int(round(x)), int(round(y)), WD[3] if lit else WD[0])
		xi, yi = int(round(cx + (rad - 1) * math.cos(ang))), int(round(cy + (rad - 1) * math.sin(ang)))
		c.put(xi, yi, WD[2] if lit else WD[1])
	for k in range(4):
		ang = k * math.pi / 4 + 0.3
		if broken and k in (2,):
			line(c, cx, cy, cx + 3 * math.cos(ang), cy + 3 * math.sin(ang), WD[1])
			continue
		line(c, cx - (rad - 2) * math.cos(ang), cy - (rad - 2) * math.sin(ang), cx + (rad - 2) * math.cos(ang), cy + (rad - 2) * math.sin(ang), WD[2])
	fill(c, cx - 1, cy - 1, 3, 3, IR[2])
	c.put(cx, cy, IR[3])


def plague_cart():
	W, H = 62, 30
	c = Canvas(W, H)
	r = rng("cart")
	# shafts (right) resting on the ground
	line(c, 44, 20, 61, 26, WD[2])
	line(c, 44, 21, 61, 27, WD[0])
	line(c, 44, 19, 60, 25, WD[3])
	# wheels
	wheel(c, 38, 21, 8, False, r)
	wheel(c, 12, 22, 7, True, r)
	# bed (rear sags: stepped down to the left)
	for x in range(4, 48):
		sag = 2 if x < 12 else 1 if x < 20 else 0
		y0 = 15 + sag
		c.put(x, y0, WD[3])
		c.put(x, y0 + 1, WD[2])
		c.put(x, y0 + 2, WD[1])
		c.put(x, y0 + 3, WD[0])
	for x in range(4, 48, 9):
		c.put(x, 18 + (2 if x < 12 else 1 if x < 20 else 0), IR[3])
	# side boards
	for x in range(5, 47):
		sag = 2 if x < 12 else 1 if x < 20 else 0
		c.put(x, 13 + sag, WD[3])
		c.put(x, 14 + sag, WD[1])
	for x in range(5, 47, 7):
		vl(c, x, 12 + (2 if x < 12 else 1 if x < 20 else 0), 14 + (2 if x < 12 else 1 if x < 20 else 0), WD[2])
	# heap of sacks under a dirty cloth
	for y in range(3, 15):
		t = (y - 3) / 11.0
		half = 6 + 15 * math.sqrt(max(0.0, 1 - (1 - t) ** 2 * 1.0))
		xl, xr = int(round(23 - half)), int(round(23 + half * 1.02))
		for x in range(xl, xr + 1):
			if y < 5 and (y - 3) < (1 if (x // 4) % 2 else 0) + (1 if x - xl < 2 or xr - x < 2 else 0):
				continue
			d = (x - 23) / half
			col = CL[3] if (d < -0.35 and y < 8) else CL[2]
			if d > 0.5:
				col = CL[1]
			if (x + y * 2) % 9 == 0 and 0.2 < d:
				col = CL[1]
			if y == 3 or x == xl:
				col = CL[3]
			c.put(x, y, col)
	for k, fx in enumerate((12, 21, 30, 37)):  # fold lines
		for i in range(8):
			c.put(fx + i // 4, 5 + i, CL[1])
	# cloth hem draping over the side boards (scalloped)
	for x in range(5, 44):
		sag = 2 if x < 12 else 1 if x < 20 else 0
		hem = 15 + sag + (2 if (x // 3) % 2 else 1)
		for y in range(13 + sag, hem):
			if c.get(x, y) in (WD[3], WD[1], WD[2]):
				c.put(x, y, CL[2] if x < 22 else CL[1])
	# rope across
	for x in range(8, 40):
		y = 9 + int(round(math.sin((x - 8) / 31.0 * math.pi) * -0)) + 0
	line(c, 9, 12, 38, 9, ROPE[1])
	line(c, 9, 13, 38, 10, ROPE[0])
	# a sack end poking out at the rear
	for (x, y) in ((4, 9), (5, 9), (6, 9), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (3, 11), (4, 11), (5, 11), (6, 11), (7, 11), (4, 12), (5, 12), (6, 12)):
		c.put(x, y, MUD[3] if x < 5 else MUD[2])
	c.put(5, 9, MUD[1])
	c.put(5, 8, ROPE[1])
	# rot on the cloth and ground
	rot_patch(c, 30, 26, 10, 2, rng("cart_rot"), k=0.9, pustules=0, glints=0)
	for x in range(0, 62):
		if c.get(x, 29) is None and x % 3 == 0 and x < 58:
			c.put(x, 29, MUD[0])
	return c


def gibbet():
	W, H = 38, 72
	c = Canvas(W, H)
	r = rng("gibbet")
	# post + arm with brace
	beam_v(c, 4, 4, 71, 4)
	beam_h(c, 3, 33, 4, 4)
	for i in range(9):
		brace(c, 8 + i, 17 - i, 8 + i, 17 - i, WD, shade=False)
		c.put(8 + i, 17 - i + 1, WD[1])
		c.put(8 + i + 1, 17 - i, WD[1])
	c.put(33, 4, IR[3])
	c.put(6, 6, IR[3])
	c.put(6, 40, IR[3])
	for y in range(9, 70, 11):
		c.put(5, y, WD[0])
	# stone footing
	for x in range(1, 12):
		for y in range(66, 72):
			k = 3 if y == 66 else 0 if y == 71 or x == 11 else 2 if (x + y) % 3 else 1
			c.put(x, y, ST[min(4, k + 1)])
	# chain to the cage
	chain(c, 29, 8, 22, IR, 0)
	# cage (humanoid taper)
	cx = 29
	rows = []
	for y in range(22, 55):
		t = (y - 22)
		if t < 4:
			half = 3
		elif t < 8:
			half = 3 + (t - 4)
		elif t < 22:
			half = 7
		elif t < 28:
			half = 7 - (t - 21) * 0.5
		else:
			half = 4
		rows.append((y, int(round(half))))
	for y, half in rows:
		c.put(cx - half, y, IR[3])
		c.put(cx + half, y, IR[0])
		if (y - 22) % 8 == 0:  # hoops
			for x in range(cx - half, cx + half + 1):
				c.put(x, y, IR[2] if x < cx else IR[1])
	for k in (-2, 0, 2):  # inner bars
		for y, half in rows:
			if abs(k) < half:
				c.put(cx + k, y, IR[1] if y % 7 else IR[2])
	for x in range(cx - 3, cx + 4):
		c.put(x, 54, IR[1])
		c.put(x, 55, IR[0])
	c.put(cx, 21, IR[3])
	c.put(cx - 1, 22, IR[2])
	c.put(cx + 1, 22, IR[2])
	# rust streaks
	for (x, y) in ((cx - 5, 30), (cx + 2, 35), (cx - 1, 46)):
		c.put(x, y, RU[0])
		c.put(x, y + 1, RU[0])
	# a few bones on the cage floor
	for x in range(cx - 2, cx + 3):
		c.put(x, 53, BONE[1] if x % 2 else BONE[0])
	c.put(cx + 1, 52, BONE[1])
	c.put(cx - 1, 51, BONE[0])
	# shackle rag hanging from the arm
	for i in range(6):
		c.put(14, 8 + i, CL[2] if i < 5 else CL[1])
		c.put(15, 8 + i + (i // 3), CL[1])
	moss_spots(c, r, 5, 4, 7, 30, 62)
	rot_patch(c, 6, 71, 6, 2, rng("gib_rot"), k=0.9, pustules=1, glints=1)
	return c


def pyre():
	W, H = 32, 19
	c = Canvas(W, H)
	lg = [hexc("0c0a09"), hexc("171210"), hexc("251d17"), hexc("352a21")]
	# ash bed
	for x in range(3, 29):
		c.put(x, 15, ASH[1])
	# back sticks crossing at the top
	for (x0, y0, x1, y1) in ((8, 8, 21, 0), (24, 8, 11, 1), (14, 6, 26, 2)):
		for t in range(0, 40):
			tt = t / 39.0
			x = int(round(x0 + (x1 - x0) * tt))
			y = int(round(y0 + (y1 - y0) * tt))
			c.put(x, y, lg[3] if t % 6 else lg[2])
			c.put(x, y + 1, lg[1])
	# stacked logs seen end-on (rows of discs): 5 / 4 / 3 / 2
	rows = [(12, 5, 5.0), (8, 4, 7.5), (4, 3, 10.0), (1, 2, 12.5)]
	for ry, n, x0 in rows:
		for i in range(n):
			cx = int(round(x0 + i * 5))
			cy = ry + 2
			for yy in range(cy - 2, cy + 3):
				for xx in range(cx - 2, cx + 3):
					d = (xx - cx) ** 2 + (yy - cy) ** 2
					if d > 5:
						continue
					if d <= 2:
						col = ASH[1] if (i + ry) % 2 else ASH[0]  # charred end grain
					elif xx < cx and yy < cy:
						col = lg[3]
					elif xx > cx or yy > cy:
						col = lg[0]
					else:
						col = lg[2]
					c.put(xx, yy, col)
	# a few dull embers deep in the pile, no flame
	c.put(16, 5, EMBER[0])
	c.put(13, 9, EMBER[0])
	# stone ring in front
	for i, sx in enumerate(range(0, 30, 5)):
		sw = 5 + (i % 2)
		for yy in range(14, 19):
			for xx in range(sx + 1, sx + 1 + sw):
				if yy == 14 and (xx == sx + 1 or xx == sx + sw):
					continue
				k = 4 if yy == 14 else 0 if yy == 18 or xx == sx + sw else 3 if xx == sx + 1 else 2 if (xx + yy) % 3 else 1
				c.put(xx, yy, ST[k])
	return c


def stocks():
	W, H = 32, 24
	c = Canvas(W, H)
	for px in (3, 24):
		beam_v(c, px, 2, 23, 4)
		c.put(px + 1, 2, WD[3])
		c.put(px + 2, 1, WD[2])
	# two stacked boards with round holes along the seam
	for x in range(1, 31):
		for y in range(9, 18):
			k = 2
			if y == 9:
				k = 3
			elif y == 17:
				k = 0
			elif y == 13:
				k = 0  # seam
			elif y == 12:
				k = 1
			elif y == 14:
				k = 3
			elif (x * 3 + y) % 13 == 0:
				k = 1
			c.put(x, y, WD[k])
	for nx, rad in ((9, 2), (15, 3), (21, 2)):
		for yy in range(13 - rad - 1, 13 + rad + 2):
			for xx in range(nx - rad - 1, nx + rad + 2):
				if (xx - nx) ** 2 + (yy - 13) ** 2 <= rad * rad + 1.5:
					c.put(xx, yy, VOID)
		hl(c, nx - rad, nx + rad, 13 - rad - 1, WD[0]) if False else None
	# hinge and hasp with padlock
	fill(c, 1, 11, 3, 5, IR[1])
	c.put(2, 12, IR[3])
	hl(c, 25, 30, 12, IR[2])
	fill(c, 27, 13, 3, 3, IR[1])
	c.put(28, 14, IR[3])
	# bottom stretcher and mud
	for x in range(7, 24):
		c.put(x, 20, WD[1])
		c.put(x, 21, WD[0])
	for x in range(0, 32):
		if x % 2 or c.get(x, 23) is None:
			c.put(x, 23, MUD[1])
	rot_patch(c, 27, 22, 4, 2, rng("stocks_rot"), k=0.9, pustules=0, glints=0)
	return c


def rot_growth(variant):
	W, H = 22, 14
	c = Canvas(W, H)
	r = rng("rot_growth", variant)
	# crust bed along the ground
	for x in range(0, W):
		hgt = 2 + int(2 * math.sin(x * 0.6 + variant)) + (1 if x % 3 == 0 else 0)
		for y in range(H - hgt, H):
			col = ROT[1] if y > H - 2 else ROT[2]
			if y == H - hgt:
				col = ROT[3]
			c.put(x, y, col)
	# bracket fungi (flat shelves)
	centres = ((6, 9, 4, 2), (14, 7, 5, 2), (10, 11, 3, 1), (18, 10, 3, 1)) if variant == 0 else ((5, 10, 3, 1), (11, 8, 5, 2), (17, 10, 4, 2), (8, 12, 3, 1))
	for cx, cy, rx, ry in centres:
		for y in range(cy - ry, cy + 1):
			for x in range(cx - rx, cx + rx + 1):
				d = ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.8)) ** 2
				if d <= 1.0:
					col = MUD[2] if d < 0.5 else MUD[1]
					if y == cy - ry:
						col = ROT[4] if x < cx else ROT[3]
					c.put(x, y, col)
		for x in range(cx - rx, cx + rx + 1):  # shadowed rim underneath
			c.put(x, cy + 1, MUD[0])
	# pustules
	spots = [(3, 11), (20, 11), (9, 6), (16, 5)] if variant == 0 else [(2, 11), (13, 5), (19, 7), (7, 7)]
	for x, y in spots:
		pustule(c, x, y, big=(x + y) % 2 == 0)
	# dim BILE glints
	for gx, gy, gk in (((8, 6, 2), (15, 4, 3), (19, 9, 2)) if variant == 0 else ((4, 9, 2), (12, 6, 3))):
		c.put(gx, gy, BILE[gk])
	# thin tendrils creeping
	for sx in ((1, 13), (21, 12)):
		c.put(sx[0], sx[1], ROT[3])
	for x in range(0, W):
		if c.get(x, H - 1) is None:
			c.put(x, H - 1, ROT[0])
	return c


def rot_growth_a():
	return rot_growth(0)


def rot_growth_b():
	return rot_growth(1)


def plague_bell():
	W, H = 18, 38
	c = Canvas(W, H)
	beam_v(c, 12, 4, 37, 4)
	# arm with the bell hanging on its left end
	beam_h(c, 1, 15, 3, 3)
	c.put(1, 2, WD[2])
	for i in range(4):
		c.put(11 - i, 6 + i, WD[1])
		c.put(11 - i, 7 + i, WD[0])
	for y in range(6, 9):
		c.put(5, y, IR[2])
	bell(c, 5, 8, size=1)
	# rag tied to the post, trailing left
	for i in range(8):
		for j in range(3 if i < 5 else 2):
			c.put(11 - i, 22 + j + (i // 3), CL[2] if j == 0 else CL[1] if i < 6 else CL[0])
	c.put(12, 21, ROPE[1])
	c.put(12, 22, ROPE[0])
	# cairn at the foot
	for bx, by, bw, bh in ((7, 33, 6, 5), (12, 34, 7, 4), (10, 31, 5, 3)):
		for y in range(by, by + bh):
			for x in range(bx, bx + bw):
				k = 4 if y == by else 0 if y == by + bh - 1 or x == bx + bw - 1 else 3 if x == bx else 2
				c.put(x, y, ST[k])
	rot_patch(c, 6, 37, 5, 2, rng("pbell_rot"), k=0.9, pustules=0, glints=0)
	return c


def clothesline():
	W, H = 66, 34
	c = Canvas(W, H)
	r = rng("cline")
	# leaning posts
	for y in range(0, H):
		xl = 3 - int((H - 1 - y) * 0.0) + int((H - 1 - y) * 3 / 33)
		c.put(xl, y, WD[3])
		c.put(xl + 1, y, WD[2])
		c.put(xl + 2, y, WD[0])
		xr = 61 + int((H - 1 - y) * -2 / 33) + 0
		c.put(xr, y, WD[2])
		c.put(xr + 1, y, WD[1])
		c.put(xr + 2, y, WD[0])
	for x in range(1, 7):
		c.put(x, 0, WD[3])
	# sagging rope
	pts = []
	for x in range(5, 63):
		t = (x - 5) / 57.0
		y = 3 + int(round(5 * math.sin(t * math.pi)))
		pts.append((x, y))
		c.put(x, y, ROPE[1])
		c.put(x, y + 1, ROPE[0])
	# hanging rags and sheets
	rags = [(9, 7, 17, CL[2], 0), (19, 6, 12, CL[1], 0), (28, 6, 20, CL[3], 1), (41, 7, 14, CL[2], 0), (51, 5, 10, CLOTH[1], 2)]
	for x0, wd, ln, col, kind in rags:
		for dx in range(wd):
			x = x0 + dx
			ytop = dict(pts).get(x, 6) + 2
			bot = ytop + ln - (3 if (dx + kind) % 4 == 0 else 0) - (2 if (dx * 3 + kind) % 5 == 0 else 0) - (dx % 2 if ln > 14 else 0)
			for y in range(ytop, min(H - 2, bot)):
				k = col
				if dx == 0:
					k = mix(col, hexc("8a8574"), 0.25) if col in CL else CLOTH[2]
				elif dx == wd - 1:
					k = mix(col, hexc("0c0b0a"), 0.45)
				elif dx % 4 == 2:
					k = mix(col, hexc("0c0b0a"), 0.22)
				c.put(x, y, k)
	# clothes pegs
	for x in (10, 20, 31, 44, 53):
		y = dict(pts).get(x, 6) + 1
		c.put(x, y, WD[1])
	# mud at the posts
	for x in list(range(0, 10)) + list(range(55, 66)):
		c.put(x, H - 1, MUD[1])
		if x % 2:
			c.put(x, H - 2, MUD[2])
	return c


def crow_b():
	c = Canvas(9, 8)
	cols = {"d": hexc("14121a"), "m": hexc("2a2832"), "b": hexc("5a5240")}
	rows = [".........", "......dd.", "...dmmmmd", "..dmmmmmd", ".dmmmmmd.", "bdmmmmd..", "b..d.d...", "...d.d..."]
	for y, row in enumerate(rows):
		for x, ch in enumerate(row):
			if ch in cols:
				c.put(x, y, cols[ch])
	return c


def bone_pile():
	W, H = 24, 10
	c = Canvas(W, H)
	r = rng("bonepile")
	b = [mix(BONE[i], MUD[2], 0.45) for i in range(3)]
	# mud mound
	for x in range(0, W):
		hgt = 4 + int(2 * math.sin(x * 0.4 + 1))
		if x < 2 or x > 21:
			hgt = 2
		for y in range(H - hgt, H):
			c.put(x, y, MUD[2] if y == H - hgt else MUD[1] if y < H - 1 else MUD[0])
	# skull, half buried (left)
	for y in range(1, 8):
		for x in range(2, 10):
			d = math.hypot((x - 5.5) / 3.8, (y - 4.2) / 3.2)
			if d < 1.0 and y < 8:
				c.put(x, y, b[2] if (x < 5 and y < 4) else b[1] if d < 0.85 else b[0])
	for x, y in ((4, 4), (7, 4)):
		c.put(x, y, hexc("0f0d0b"))
		c.put(x, y + 1, hexc("0f0d0b"))
	c.put(6, 6, hexc("0f0d0b"))
	for x in range(2, 10):  # buried lower half
		c.put(x, 7, MUD[2])
		c.put(x, 8, MUD[1])
	# femur
	line(c, 11, 8, 20, 4, b[1])
	line(c, 11, 7, 20, 3, b[2])
	c.put(11, 7, b[1])
	c.put(10, 8, b[1])
	c.put(21, 3, b[1])
	c.put(21, 5, b[1])
	# rib arcs
	for k, rx in enumerate((12, 15, 18)):
		for i in range(5):
			y = 8 - i if i < 3 else 6 - (i - 2)
			c.put(rx + (1 if i > 2 else 0), y - (1 if k == 1 else 0) + 1, b[0] if i % 2 else b[1])
	return c


# ============================================================================= WALL (wall on the LEFT, x=0 is the wall face)
def wall_pipe():
	W, H = 14, 26
	c = Canvas(W, H)
	# flange plate bolted to the wall
	for y in range(0, 9):
		c.put(0, y, IR[0])
		c.put(1, y, IR[3] if y in (0, 8) else IR[2])
		c.put(2, y, IR[1])
	for y in (1, 7):
		c.put(1, y, IR[3])
	# round pipe: lit top, dark belly
	for x in range(3, 11):
		prof = [IR[3], IR[2], IR[2], IR[1], IR[1], IR[0]]
		for i, col in enumerate(prof):
			col2 = col
			if (x * 5 + i * 3) % 9 == 0:
				col2 = RU[2] if i < 3 else RU[1]
			c.put(x, 1 + i, col2)
	for y in range(0, 8):  # mouth collar
		c.put(10, y, IR[2] if y not in (0, 7) else IR[1])
		c.put(11, y, IR[0])
	for y in range(2, 6):
		c.put(11, y, VOID)
	for y in range(1, 7):  # collar ring
		c.put(5, y, IR[1] if y > 2 else IR[3])
	# damp stain on the wall
	for y in range(9, 21):
		c.put(0, y, ROT[1] if y % 3 else ROT[0])
	for y in range(9, 14):
		c.put(1, y, ROT[1])
	# sludge: from the mouth, falls in a thin line, pools small
	for y in range(6, 21):
		c.put(11, y, BILE[0])
	for y in (9, 15):
		c.put(11, y, BILE[1])
	c.put(11, 12, BILE[2])
	c.put(11, 19, BILE[2])
	c.put(10, 7, ROT[1])
	c.put(12, 8, ROT[1])
	for x in range(9, 14):
		c.put(x, 21, ROT[1])
	c.put(10, 21, BILE[1])
	c.put(11, 21, BILE[2])
	c.put(12, 20, ROT[2])
	return c


def wall_sign():
	W, H = 24, 22
	c = Canvas(W, H)
	# wall plate + bracket arm + scroll brace
	for y in range(0, 6):
		c.put(0, y, IR[0])
		c.put(1, y, IR[2])
		c.put(2, y, IR[1])
	for x in range(2, 22):
		c.put(x, 1, IR[2] if x % 6 else IR[3])
		c.put(x, 2, IR[0])
	for i in range(8):
		c.put(2 + i, 8 - i + 1 - (1 if i > 5 else 0) - 0, IR[1])
	line(c, 2, 9, 10, 3, IR[1])
	for a in range(0, 14):  # scroll curl
		ang = a * 0.45
		c.put(int(round(4 + 2 * math.cos(ang))), int(round(7 + 2 * math.sin(ang) * 0.9)), IR[1]) if a > 6 else None
	c.put(21, 2, IR[3])
	c.put(22, 3, IR[2])
	c.put(22, 4, IR[1])
	# hanging chains
	for y in range(3, 8):
		c.put(8, y, IR[2] if y % 2 else IR[1])
	for y in range(3, 10):
		c.put(18, y, IR[2] if y % 2 else IR[1])
	# board hanging askew (right chain longer)
	for x in range(6, 21):
		t = (x - 6) / 14.0
		y0 = 8 + int(round(t * 2))
		for y in range(y0, y0 + 9):
			k = 2
			if y == y0:
				k = 3
			elif y == y0 + 8:
				k = 0
			elif x == 6:
				k = 3
			elif x == 20:
				k = 0
			elif (x * 5 + y) % 11 == 0:
				k = 1
			c.put(x, y, WD[k])
		# plank seam
		c.put(x, y0 + 4, WD[1])
	# carved emblem: ring and diamond
	for dx, dy in ((0, -2), (-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2)):
		c.put(13 + dx, 14 + dy + 1, WD[0])
	c.put(13, 15, WD[1])
	# moss/rot drip on the board and a nail
	c.put(8, 9, IR[3])
	c.put(18, 11, IR[3])
	for x in range(13, 18):
		c.put(x, 18, ROT[1] if x % 2 else ROT[2])
	return c


def wall_rot():
	W, H = 18, 30
	c = Canvas(W, H)
	r = rng("wrot")
	cells = set()
	# clinging mass: dense at the wall, thinning out and sending streaks down
	for y in range(0, H):
		reach = 3 + int(5 * math.sin(y * 0.28 + 1) ** 2) + (4 if 8 < y < 18 else 0) - max(0, y - 22)
		reach = max(1, reach)
		for x in range(0, reach):
			if r.random() < 0.85 - x * 0.05:
				cells.add((x, y))
	for sx in (6, 9, 12):  # long drips
		ln = r.randint(6, 12)
		y0 = r.randint(8, 16)
		for i in range(ln):
			cells.add((sx + (i // 5), y0 + i))
	for x, y in cells:
		col = ROT[1]
		if (x + y) % 4 == 0:
			col = ROT[2]
		if (x - 1, y) not in cells and x > 0:
			col = ROT[3]
		if x == 0:
			col = ROT[0]
		c.put(x, y, col)
	for x, y in r.sample(sorted(cells), 6):
		pustule(c, x, y, big=False)
	c.put(5, 12, BILE[1])
	c.put(2, 17, BILE[2])
	return c


def wall_chains():
	W, H = 12, 26
	c = Canvas(W, H)
	# ring bolted to the wall
	for dx, dy in ((0, 1), (1, 0), (2, 0), (3, 1), (3, 2), (2, 3), (1, 3), (0, 2)):
		c.put(dx, 1 + dy, IR[3] if dy < 2 else IR[1])
	c.put(0, 0, IR[0])
	c.put(0, 4, IR[0])
	# main chain with a sag and a shackle cuff at its end
	x = 3
	for i, y in enumerate(range(4, 16)):
		xx = x + int(round(2 * math.sin(i * 0.3)))
		c.put(xx, y, IR[3] if i % 2 == 0 else IR[1])
		if i % 2 == 0:
			c.put(xx + 1, y, IR[0])
	for dx, dy in ((-2, 0), (-1, -1), (0, -1), (1, 0), (-2, 1), (1, 1), (-1, 2), (0, 2)):
		c.put(5 + dx + 2, 16 + dy + 1, IR[2] if dy < 2 else IR[0])
	c.put(6, 17, IR[0])
	# second, shorter chain with a cuff clamped on a bone-pale ring
	for i, y in enumerate(range(4, 11)):
		c.put(7 + i // 4, y, IR[2] if i % 2 == 0 else IR[0])
	for dx, dy in ((0, 0), (1, 0), (2, 1), (2, 2), (1, 3), (0, 3), (-1, 2), (-1, 1)):
		c.put(9 + dx, 11 + dy, IR[2] if dy < 2 else IR[0])
	# rust runs on the wall
	for y in range(5, 20):
		c.put(0, y, RU[0] if y % 3 else RU[1])
	return c


# ============================================================================= CEILING (anchor top-centre)
def hang_cage():
	W, H = 16, 42
	c = Canvas(W, H)
	cx = 8
	chain(c, cx, 0, 15, IR, 0)
	# suspension ring and dome
	for dx in range(-2, 3):
		c.put(cx + dx, 15, IR[2])
	for i in range(4):
		for dx in range(-(2 + i), 3 + i):
			c.put(cx + dx, 16 + i, IR[3] if dx < 0 else IR[1] if dx > 0 else IR[2])
		c.put(cx - 2 - i, 16 + i, IR[3])
	# body
	for y in range(20, 38):
		half = 6 if y < 33 else 6 - (y - 32)
		c.put(cx - half, y, IR[3])
		c.put(cx + half, y, IR[0])
		for k in (-3, 0, 3):
			if abs(k) < half:
				c.put(cx + k, y, IR[1] if y % 4 else IR[2])
	for y in (21, 28, 36):
		for x in range(cx - 6, cx + 7):
			if abs(x - cx) <= (6 if y < 33 else 2):
				c.put(x, y, IR[2] if x < cx else IR[1])
	# bottom plate and rust
	for x in range(cx - 2, cx + 3):
		c.put(x, 38, IR[1])
		c.put(x, 39, IR[0])
	c.put(cx, 40, IR[0])
	# bone in the cage
	for x in range(cx - 2, cx + 2):
		c.put(x, 35, BONE[0] if x % 2 else BONE[1])
	c.put(cx - 4, 24, RU[1])
	c.put(cx + 3, 30, RU[1])
	c.put(cx - 5, 31, RU[0])
	return c


def hang_rags():
	W, H = 14, 30
	c = Canvas(W, H)
	for x in range(0, 14):  # crossbar rope
		c.put(x, 0, ROPE[1])
		c.put(x, 1, ROPE[0])
	strips = [(1, 3, 16, CL[2]), (4, 2, 22, CL[1]), (9, 3, 13, CLOTH[1]), (12, 2, 18, CL[2])]
	for x0, wd, ln, col in strips:
		for dx in range(wd):
			for y in range(2, 2 + ln - (dx * 2)):
				k = col
				if dx == wd - 1:
					k = mix(col, hexc("0c0b0a"), 0.4)
				c.put(x0 + dx, y, k)
	# string of small bones
	for y in range(2, 27):
		c.put(7, y, ROPE[0])
	for y in (7, 11, 15, 19, 23):
		c.put(6, y, BONE[1])
		c.put(7, y, BONE[0])
		c.put(8, y, BONE[1])
		c.put(7, y + 1, BONE[1])
	return c


def hang_lamp_bile():
	W, H = 10, 36
	c = Canvas(W, H)
	cx = 5
	chain(c, cx, 0, 21, IR, 0)
	# cap
	for i in range(3):
		for dx in range(-(1 + i), 2 + i):
			c.put(cx + dx, 22 + i, IR[3] if dx < 0 else IR[1])
	# glass
	for y in range(25, 33):
		for x in range(cx - 3, cx + 4):
			edge = x in (cx - 3, cx + 3)
			if edge:
				c.put(x, y, IR[1] if x > cx else IR[3])
			else:
				k = BILE[1]
				if 27 <= y <= 31 and abs(x - cx) <= 1:
					k = BILE[2]
				c.put(x, y, k)
	c.put(cx, 29, BILE[4])
	c.put(cx, 28, BILE[3])
	c.put(cx, 30, BILE[3])
	for x in range(cx - 3, cx + 4):
		c.put(x, 25, IR[2])
		c.put(x, 33, IR[1])
	c.put(cx - 1, 34, IR[1])
	c.put(cx, 34, IR[0])
	c.put(cx + 1, 34, IR[1])
	c.put(cx, 35, IR[0])
	return c


def cobweb():
	c = Canvas(16, 16)
	web = lambda a: (140, 142, 130, a // 2)
	pts = [(15, 0), (13, 5), (9, 9), (5, 13), (0, 15)]
	# radial threads from the corner
	for (tx, ty) in ((15, 1), (14, 6), (10, 10), (6, 14), (1, 15)):
		line(c, 0, 0, tx, ty, web(50))
	# arcs
	for rad, a in ((5, 90), (9, 75), (13, 60)):
		for k in range(0, 40):
			ang = k * (math.pi / 2) / 39
			x = int(round(rad * math.cos(ang) * (1 - 0.15 * math.sin(2 * ang))))
			y = int(round(rad * math.sin(ang) * (1 - 0.15 * math.sin(2 * ang))))
			if k % 2 == 0:
				c.put(x, y, web(a))
	for x in range(0, 16):
		c.put(x, 0, web(80))
	for y in range(0, 16):
		c.put(0, y, web(80))
	return c


# ============================================================================= UNDERGROUND (anchor bottom-centre)
def cellar_arch():
	W, H = 50, 50
	c = Canvas(W, H)
	r = rng("cellararch")
	br = [hexc("0f0e0b"), hexc("1a1812"), hexc("24211a"), hexc("2f2b22")]
	dk = [hexc("0b0a08"), hexc("131210"), hexc("1b1914"), hexc("23201a")]
	cx = 25
	# outer arch (voussoir ring)
	for y in range(2, H):
		half = 23 if y > 24 else int(23 * math.sqrt(max(0.0, 1 - ((24 - y) / 22.0) ** 2)))
		for x in range(cx - half, cx + half + 1):
			c.put(x, y, br[2])
	bricks_det(c, 1, 2, 48, 48, br, bw=6, bh=4)
	# inner recess, bricked up with a darker, finer pattern
	for y in range(9, H):
		half = 15 if y > 24 else int(15 * math.sqrt(max(0.0, 1 - ((24 - y) / 15.0) ** 2)))
		for x in range(cx - half, cx + half + 1):
			c.put(x, y, dk[2])
	for y in range(9, H):
		half = 15 if y > 24 else int(15 * math.sqrt(max(0.0, 1 - ((24 - y) / 15.0) ** 2)))
		sub = Canvas(W, H)
		for x in range(cx - half, cx + half + 1):
			row = (y - 9) // 3
			ty = (y - 9) % 3
			off = 3 if row % 2 else 0
			sx = (x + off) % 6
			col = dk[0] if ty == 2 or sx == 5 else dk[2 if (x * 3 + row) % 5 else 1]
			if x == cx - half:
				col = br[0]
			c.put(x, y, col)
	# arch ring edge highlight (very faint)
	for y in range(2, 25):
		half = int(23 * math.sqrt(max(0.0, 1 - ((24 - y) / 22.0) ** 2)))
		c.put(cx - half, y, br[3])
	# collapsed brick hole in the infill, showing darkness + fallen bricks
	for y in range(22, 32):
		for x in range(cx - 9, cx - 1):
			if ((x - (cx - 5)) / 4.2) ** 2 + ((y - 27) / 4.5) ** 2 < 1:
				c.put(x, y, hexc("070706"))
	for bx, by in ((cx - 8, 41), (cx - 4, 43), (cx + 1, 42), (cx + 6, 44), (cx - 1, 45)):
		fill(c, bx, by, 4, 3, br[3])
		hl(c, bx, bx + 3, by + 2, br[0])
	# rubble heap and damp at the bottom
	for x in range(cx - 20, cx + 21):
		for y in range(H - 5 + abs(x - cx) // 8, H):
			c.put(x, y, br[2] if (x + y) % 3 else br[1])
	rot_patch(c, 34, 48, 8, 2, rng("arch_rot"), k=0.9, pustules=1, glints=0)
	for x in range(cx - 23, cx + 24):
		if c.get(x, H - 1) is not None and x % 2:
			c.put(x, H - 1, ROT[0])
	for y in range(0, H):
		half = 23 if y > 24 else (int(23 * math.sqrt(max(0.0, 1 - ((24 - y) / 22.0) ** 2))) if y >= 2 else -1)
		for x in range(0, W):
			if abs(x - cx) > half:
				c.px[y * W + x] = None
	recolor_dark(c, 0, 0, W - 1, H - 1, 0.1, hexc("0a0a08"))
	return c


def cellar_niche():
	W, H = 24, 26
	c = Canvas(W, H)
	r = rng("niche")
	cx = 12
	# stone surround (arched)
	for y in range(0, H):
		half = 11 if y > 9 else int(11 * math.sqrt(max(0.0, 1 - ((9 - y) / 9.0) ** 2)))
		for x in range(cx - half, cx + half + 1):
			k = 3 if (x == cx - half or y == 0) else 1 if x == cx + half else 2
			if (x * 5 + y * 3) % 13 == 0:
				k = 1
			c.put(x, y, ST[k])
	# recess
	for y in range(4, 23):
		half = 7 if y > 11 else int(7 * math.sqrt(max(0.0, 1 - ((11 - y) / 7.0) ** 2)))
		for x in range(cx - half, cx + half + 1):
			c.put(x, y, VOID if x > cx - half else hexc("141311"))
	# shelf
	for x in range(cx - 8, cx + 9):
		c.put(x, 21, ST[4])
		c.put(x, 22, ST[1])
	for x in range(cx - 7, cx + 8):  # mid shelf
		c.put(x, 14, ST[3]) if False else None
	# skulls (low contrast)
	sk = [mix(BONE[i], MUD[2], 0.4) for i in range(3)]
	for sx, sy in ((cx - 6, 17), (cx - 1, 17), (cx + 4, 17), (cx - 3, 13)):
		for (dx, dy) in ((1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3)):
			c.put(sx + dx, sy + dy, sk[1] if dx > 0 and dy < 2 else sk[0] if dy > 2 or dx == 4 else sk[1])
		c.put(sx + 1, sy + 1, hexc("0d0c0a"))
		c.put(sx + 3, sy + 1, hexc("0d0c0a"))
		c.put(sx + 1, sy, sk[2])
	# candle stubs (unlit) with wax drips
	for kx, ky, kh in ((cx + 5, 17, 3), (cx - 7, 13, 2)):
		for y in range(ky, ky + kh):
			c.put(kx, y, BONE[1])
		c.put(kx, ky - 1, hexc("1a1613"))
	cx_candle = (cx + 5, 16)
	# cobweb-ish soot at the arch
	for x in range(cx - 3, cx + 4):
		c.put(x, 5, hexc("0a0908"))
	rot_patch(c, 4, 25, 4, 1.5, rng("niche_rot"), k=0.9, pustules=0, glints=0)
	for x in range(0, W):
		if c.get(x, H - 1) is None and 2 < x < 22:
			c.put(x, H - 1, ST[0])
	recolor_dark(c, 0, 0, W - 1, H - 1, 0.12, hexc("0e0d0b"))
	return c


# ============================================================================= catalogue / outputs
# name -> (function, kind, anchor(w, h) -> [x, y], lights, weight, big)
def _ground(w, h):
	return [w // 2, h]


def _ceil(w, h):
	return [w // 2, 0]


PROPS = [
	("house_timber_a", house_timber_a, "ground", _ground, [{"pos": [54, 54], "type": "window"}], 3, True),
	("house_timber_b", house_timber_b, "ground", _ground, [], 3, True),
	("cathedral_ruin", cathedral_ruin, "ground", _ground, [], 1, True),
	("plague_cart", plague_cart, "ground", _ground, [], 2, False),
	("gibbet", gibbet, "ground", _ground, [], 2, False),
	("pyre", pyre, "ground", _ground, [{"pos": [16, 3], "type": "flame"}], 2, False),
	("stocks", stocks, "ground", _ground, [], 2, False),
	("rot_growth_a", rot_growth_a, "ground", _ground, [], 4, False),
	("rot_growth_b", rot_growth_b, "ground", _ground, [], 4, False),
	("plague_bell", plague_bell, "ground", _ground, [], 2, False),
	("clothesline", clothesline, "ground", _ground, [], 2, False),
	("crow_b", crow_b, "ground", _ground, [], 4, False),
	("bone_pile", bone_pile, "ground", _ground, [], 4, False),
	("wall_pipe", wall_pipe, "wall", lambda w, h: [0, 4], [], 3, False),
	("wall_sign", wall_sign, "wall", lambda w, h: [0, 2], [], 2, False),
	("wall_rot", wall_rot, "wall", lambda w, h: [0, h // 2], [], 4, False),
	("wall_chains", wall_chains, "wall", lambda w, h: [0, 2], [], 3, False),
	("hang_cage", hang_cage, "ceiling", _ceil, [], 2, False),
	("hang_rags", hang_rags, "ceiling", _ceil, [], 3, False),
	("hang_lamp_bile", hang_lamp_bile, "ceiling", _ceil, [{"pos": [5, 29], "type": "bile"}], 2, False),
	("cobweb", cobweb, "ceiling", lambda w, h: [0, 0], [], 5, False),
	("cellar_arch", cellar_arch, "underground", _ground, [], 2, True),
	("cellar_niche", cellar_niche, "underground", _ground, [{"pos": [17, 15], "type": "candle"}], 2, False),
]


def sha256(path):
	return hashlib.sha256(open(path, "rb").read()).hexdigest()


def board(path, names, scale, bg="1b1e22", pad=4, row_w=330):
	"""All props on one dark board, wrapped into rows, bottoms aligned per row."""
	imgs = [load_png(os.path.join(OUT, n + ".png")) for n in names]
	rows, cur, curw = [], [], pad
	for i in imgs:
		if curw + i.w + pad > row_w and cur:
			rows.append(cur)
			cur, curw = [], pad
		cur.append(i)
		curw += i.w + pad
	rows.append(cur)
	H = sum(max(i.h for i in r) + pad * 2 for r in rows)
	b = Canvas(row_w, H)
	b.rect(0, 0, row_w, H, hexc(bg))
	y = 0
	for r in rows:
		rh = max(i.h for i in r) + pad * 2
		x = pad
		for i in r:
			b.blit(i, x, y + rh - pad - i.h)
			x += i.w + pad
		y += rh
	save_png(b, path, scale)


def scale_preview(path):
	"""Props on a strip of N2 terrain next to the N1 house and a 24x32 knight placeholder."""
	terr = load_png(os.path.join(ROOT, "assets", "run020", "terrain_campaign.png"))

	def tile(col, row):
		t = Canvas(16, 16)
		for y in range(16):
			for x in range(16):
				t.px[y * 16 + x] = terr.get(col * 16 + x, row * 16 + y)
		return t

	pick = [("house_timber_a", 76), ("house_timber_b", 54), ("cathedral_ruin", 72), ("plague_cart", 62), ("gibbet", 38), ("pyre", 32), ("stocks", 32),
		("plague_bell", 18), ("clothesline", 66), ("rot_growth_a", 22), ("bone_pile", 24), ("crow_b", 9)]
	imgs = [(load_png(os.path.join(OUT, n + ".png")), n) for n, _ in pick]
	n1 = load_png(os.path.join(ROOT, "assets", "sprites", "prop_house.png"))
	W = 8 + sum(i.w + 10 for i, _ in imgs) + 24 + n1.w + 40
	H = 150
	ground = 126
	b = Canvas(W, H)
	b.rect(0, 0, W, H, hexc("1b1e22"))
	for tx in range(0, W, 16):
		b.blit(tile(1, 0), tx, ground)
		for ty in range(ground + 16, H, 16):
			b.blit(tile(0, 1), tx, ty)
	# knight placeholder 24x32, simple silhouette (not the real sprite)
	x = 6

	def knight(cx):
		sil = hexc("5a6070")
		for yy in range(32):
			for xx in range(24):
				if yy < 9 and 6 <= xx < 18 or 9 <= yy < 22 and 4 <= xx < 20 or yy >= 22 and (5 <= xx < 11 or 13 <= xx < 19):
					b.put(cx + xx, ground - 32 + yy, sil if xx < 12 else hexc("444a58"))
		hl(b, cx - 0, cx + 23, ground - 33, hexc("00000000")) if False else None

	knight(x)
	x += 24 + 10
	b.blit(n1, x, ground - n1.h)
	x += n1.w + 10
	for im, n in imgs:
		b.blit(im, x, ground - im.h)
		x += im.w + 10
	save_png(b, path, 3)


def main(argv):
	os.makedirs(OUT, exist_ok=True)
	os.makedirs(PREVIEW, exist_ok=True)
	meta = []
	rows = []
	for name, fn, kind, anchor, lights, weight, big in PROPS:
		if argv and name not in argv:
			continue
		c = fn()
		path = os.path.join(OUT, name + ".png")
		save_png(c, path)
		meta.append({"file": name + ".png", "w": c.w, "h": c.h, "kind": kind, "anchor": anchor(c.w, c.h), "lights": lights, "weight": weight, "big": big})
		rows.append((name, c.w, c.h, kind, anchor(c.w, c.h), lights, sha256(path)))
	if argv:
		return
	with open(os.path.join(OUT, "props_n2.json"), "w") as f:
		json.dump(meta, f, indent=1)
	groups = ["house_timber_a", "house_timber_b", "cathedral_ruin"], ["plague_cart", "gibbet", "pyre", "stocks", "plague_bell", "clothesline"], \
		["rot_growth_a", "rot_growth_b", "crow_b", "bone_pile", "wall_pipe", "wall_sign", "wall_rot", "wall_chains"], \
		["hang_cage", "hang_rags", "hang_lamp_bile", "cobweb", "cellar_arch", "cellar_niche"]
	allnames = [n for g in groups for n in g]
	board(os.path.join(PREVIEW, "props_n2_board.png"), allnames, 3)
	scale_preview(os.path.join(PREVIEW, "props_n2_scale.png"))
	with open(os.path.join(OUT, "props_n2.sha256"), "w") as f:
		for name, w, h, kind, anc, lights, sha in rows:
			f.write("%s  %s.png\n" % (sha, name))


if __name__ == "__main__":
	main(sys.argv[1:])

"""Terrain masonry, grass/blight tufts and hanging vines (RUN-029).

Tiles stay 16x16 and indexed by an exposure mask (bit 1 = open above, 2 = open
right, 4 = open below, 8 = open left) so TerrainSkin can skin the authored
TileMapLayer without touching it. New in RUN-029: the brick pattern is generated
as a 96x16 seamless strip per seed, cut into 6 horizontal phases, so blocks run
across tile borders (larger, irregular ashlar instead of a 16 px grid) and each
block gets its own tone, bevel, moss cap and weathering.

Atlas layout (terrain_stone.png, 256 px wide): row = theme*18 + seed*6 + phase,
column = exposure mask. theme 0 = village, 1 = corrupt approach.
"""
import functools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, hexc, sheet  # noqa: E402
from palette import CORRUPT, MOSS, STONE, STONE_COOL, WOOD  # noqa: E402

T = 16
STRIP = 96
SEEDS = 3
PHASES = STRIP // T
THEMES = {
	"village": dict(stone=STONE, moss=MOSS, accent=MOSS[3], tint=WOOD[2], tint_k=0.2),
	"corrupt": dict(stone=STONE_COOL, moss=CORRUPT[:4], accent=CORRUPT[4], tint=CORRUPT[2], tint_k=0.14),
}
THEME_ORDER = ("village", "corrupt")


def rng(*seed):
	return random.Random("-".join(map(str, seed)))


def mix(a, b, k):
	return tuple(int(round(a[i] * (1 - k) + b[i] * k)) for i in range(3)) + (255,)


def _hash(x, y, salt=0):
	return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xFFFF


def _widths(r, total=STRIP):
	widths, rem = [], total
	while rem > 0:
		w = r.randint(10, 22)
		if rem <= 22:
			w = rem
		elif rem - w < 10:
			w = rem - 10
		widths.append(w)
		rem -= w
	return widths


def _brick(c, theme, r, x0, x1, top, bottom):
	t = THEMES[theme]
	s, m = t["stone"], t["moss"]
	k = r.random()
	tone = s[2] if k < 0.38 else s[3] if k < 0.84 else mix(s[2], s[1], 0.5)
	if r.random() < 0.4:
		tone = mix(tone, t["tint"], t["tint_k"])
	hi, hi2 = mix(tone, s[5], 0.42), mix(tone, s[5], 0.2)
	lo, lo2 = mix(tone, s[0], 0.42), mix(tone, s[0], 0.2)
	W = c.w
	for y in range(top, bottom + 1):
		for x in range(x0, x1):
			xx = x % W
			if y == bottom or x == x1 - 1:
				col = s[0]  # mortar
			elif y == top:
				col = hi
			elif x == x0:
				col = hi2
			elif y == bottom - 1:
				col = lo
			elif x == x1 - 2:
				col = lo2
			else:
				h = _hash(xx, y, 3)
				col = lo2 if h % 9 == 0 else hi2 if h % 13 == 0 else tone
			c.put(xx, y, col)
	# Chipped top-right corner and pits.
	if r.random() < 0.3:
		c.put((x1 - 2) % W, top, s[0])
		c.put((x1 - 3) % W, top, lo2)
	for _ in range(r.randint(1, 3)):
		c.put(r.randint(x0 + 2, x1 - 3) % W, r.randint(top + 2, max(top + 2, bottom - 2)), lo)
	# Hairline crack.
	if r.random() < 0.14 and x1 - x0 > 8:
		cx = r.randint(x0 + 3, x1 - 4)
		for y in range(top + 1, bottom - 1):
			c.put(cx % W, y, s[1])
			if r.random() < 0.6:
				cx += r.choice((-1, 1))
	# Moss cap on the brick's upper face.
	moss_p = 0.34 if theme == "village" else 0.18
	if r.random() < moss_p:
		mw = r.randint(3, max(3, min(8, x1 - x0 - 3)))
		mx = r.randint(x0 + 1, max(x0 + 1, x1 - mw - 2))
		for i in range(mw):
			c.put((mx + i) % W, top, m[2] if i % 3 else m[1])
			if r.random() < 0.7:
				c.put((mx + i) % W, top + 1, m[1] if r.random() < 0.7 else m[0])
		if r.random() < 0.6:
			c.put((mx + r.randint(0, mw - 1)) % W, top + 2, m[0])
	# Moss in the bottom mortar joint.
	if r.random() < (0.25 if theme == "village" else 0.12):
		for x in range(x0 + 1, min(x1 - 1, x0 + 1 + r.randint(3, 6))):
			c.put(x % W, bottom, m[0] if r.random() < 0.7 else m[1])


@functools.lru_cache(maxsize=None)
def strip(theme, seed):
	"""Seamless 96x16 masonry strip."""
	c = Canvas(STRIP, T)
	r = rng(theme, seed, "strip")
	for top, bottom in ((0, 7), (8, 15)):
		widths = _widths(r)
		x = r.randint(0, STRIP - 1)
		for w in widths:
			_brick(c, theme, r, x, x + w, top, bottom)
			x += w
	if seed == 2:
		# A tall ashlar slab spanning both courses, with an inner chiselled bevel.
		s = THEMES[theme]["stone"]
		sx, sw = r.randint(8, STRIP - 30), 15
		tone = s[2]
		for y in range(T):
			for x in range(sx, sx + sw):
				if y == T - 1 or x == sx + sw - 1:
					col = s[0]
				elif y == 0 or x == sx:
					col = mix(tone, s[5], 0.3)
				elif y == T - 2 or x == sx + sw - 2:
					col = mix(tone, s[0], 0.35)
				else:
					col = tone if _hash(x, y, 9) % 7 else s[2]
				c.put(x, y, col)
		for i in range(4):
			c.put(sx + 5 + i, 6 + i // 2, s[1])
	return c


def terrain_tile(theme, seed, phase, mask):
	t = THEMES[theme]
	s, m = t["stone"], t["moss"]
	base = strip(theme, seed)
	c = Canvas(T, T)
	for y in range(T):
		for x in range(T):
			c.put(x, y, base.get(phase * T + x, y))
	r = rng(theme, seed, phase, mask, "edge")
	up, right, down, left = mask & 1, mask & 2, mask & 4, mask & 8
	if left:
		for y in range(T):
			c.put(0, y, s[0])
			c.put(1, y, s[4] if y % 8 not in (7,) else s[0])
		for _ in range(2):
			y0 = r.randint(1, 12)
			for y in range(y0, y0 + r.randint(2, 4)):
				c.put(1, min(y, T - 1), m[1] if theme == "village" else m[2])
	if right:
		for y in range(T):
			c.put(T - 1, y, s[0])
			c.put(T - 2, y, s[1])
		for _ in range(2):
			y0 = r.randint(1, 12)
			for y in range(y0, y0 + r.randint(2, 3)):
				c.put(T - 2, min(y, T - 1), m[0] if theme == "village" else m[1])
	if down:
		for x in range(T):
			c.put(x, T - 1, s[0])
			c.put(x, T - 2, s[1])
		# Ragged, crumbling underside.
		for x in range(1, T - 1):
			if r.random() < 0.3:
				c.px[(T - 1) * T + x] = None
				if r.random() < 0.35:
					c.px[(T - 2) * T + x] = None
		for x in range(T):
			if r.random() < 0.18:
				c.put(x, T - 3, m[0] if theme == "village" else CORRUPT[0])
	if up:
		# Walkable rim: bright capstone, then a shadowed course, so the top reads at once.
		for x in range(T):
			chip = r.random() < 0.1
			c.put(x, 0, s[4] if chip else s[5])
			c.put(x, 1, s[3] if chip else s[4])
			c.put(x, 2, s[2] if x % 5 else s[1])
		for x in range(1, T, 5):
			c.put((x + r.randint(0, 2)) % T, 0, mix(s[5], s[3], 0.5))  # worn flecks
		for x in range(T):
			depth = r.choice((1, 1, 2, 2, 3, 4, 5)) if theme == "village" else r.choice((0, 1, 1, 2, 3))
			for y in range(depth):
				c.put(x, y, m[2] if y == 0 else (m[1] if y < depth - 1 else m[0]))
			if theme == "village" and r.random() < 0.3:
				c.put(x, 0, m[3])
		if left:
			c.put(0, 0, s[0])
		if right:
			c.put(T - 1, 0, s[0])
	return c


def tuft(theme, variant):
	"""16x12 grass / blight cluster. Baseline row 10 stands on the surface top; row 11
	overlaps the tile's first row. Drawn at (cell x, cell y - 11)."""
	t = THEMES[theme]
	m = t["moss"]
	c = Canvas(T, 12)
	r = rng(theme, variant, "tuft2")
	x = r.randint(0, 2)
	while x < T:
		kind = r.random()
		if theme == "village":
			if kind < 0.62:
				h = r.choice((2, 3, 3, 4, 5, 6))
				lean = r.choice((-1, 0, 0, 1))
				for y in range(h):
					xx = x + (lean if y >= h - 2 else 0)
					c.put(xx, 10 - y, m[3] if y == h - 1 else m[2] if y > 0 else m[1])
				if h >= 4 and x + 1 < T:
					c.put(x + 1, 10 - (h - 3), m[2])
			elif kind < 0.74:
				# Little fern: stem plus two fronds.
				h = r.choice((3, 4))
				for y in range(h):
					c.put(x, 10 - y, m[2])
				c.put(x - 1, 10 - h + 1, m[3])
				c.put(x + 1, 10 - h + 1, m[3])
				c.put(x - 2, 10 - h + 2, m[2])
				c.put(x + 2, 10 - h + 2, m[2])
			elif kind < 0.82:
				# Flower on a thin stem (pale, low-key warm-neutral).
				h = r.choice((3, 4, 5))
				for y in range(h):
					c.put(x, 10 - y, m[2])
				c.put(x, 10 - h, hexc("c8bd96") if r.random() < 0.6 else hexc("9a8aa8"))
			elif kind < 0.88:
				# Toadstool, dark desaturated red cap.
				c.put(x, 10, hexc("cfc4ae"))
				c.put(x, 9, hexc("cfc4ae"))
				for dx in (-1, 0, 1):
					c.put(x + dx, 8, hexc("7a3038"))
				c.put(x, 7, hexc("7a3038"))
				c.put(x - 1, 8, hexc("a05a52"))
			else:
				c.put(x, 10, STONE[4])
				c.put(x + 1, 10, STONE[3])
				c.put(x, 9, STONE[5])
			c.put(x, 11, m[1])
		else:
			if kind < 0.7:
				h = r.choice((2, 3, 4, 6, 8))
				xx = x
				for y in range(h):
					xx += r.choice((-1, 0, 0, 0, 1)) if y > 2 else 0
					c.put(xx, 10 - y, CORRUPT[2] if y < h - 1 else t["accent"])
					if y == h // 2 and h >= 6:
						c.put(xx + 1, 10 - y - 1, CORRUPT[1])
						c.put(xx + 2, 10 - y - 2, CORRUPT[3])
			elif kind < 0.85:
				c.put(x, 10, CORRUPT[1])
				c.put(x, 9, CORRUPT[2])
				c.put(x - 1, 9, CORRUPT[1])
				c.put(x + 1, 8, CORRUPT[3])
				c.put(x - 1, 8, CORRUPT[3])
			else:
				c.put(x, 10, CORRUPT[0])
				c.put(x, 9, CORRUPT[3])
				c.put(x, 8, t["accent"])
			c.put(x, 11, CORRUPT[1])
		x += r.choice((2, 3, 3, 4, 4, 5))
	return c


def vine(theme, variant):
	"""16x24 strands hanging from an overhang (drawn just under a tile's bottom)."""
	t = THEMES[theme]
	m = t["moss"]
	c = Canvas(T, 24)
	r = rng(theme, variant, "vine")
	strands = r.randint(2, 3)
	xs = sorted(r.sample(range(1, T - 1), strands))
	for x in xs:
		length = r.randint(6, 22)
		xx = float(x)
		for y in range(length):
			xx += r.choice((-0.34, 0, 0, 0.34))
			col = m[1] if y < length - 3 else m[2] if theme == "village" else CORRUPT[3]
			if theme == "corrupt":
				col = CORRUPT[1] if y < length - 3 else CORRUPT[2]
			c.put(int(round(xx)), y, col)
			if y % 4 == 2 and y < length - 2:
				side = 1 if (y // 4) % 2 == 0 else -1
				c.put(int(round(xx)) + side, y, m[2] if theme == "village" else CORRUPT[2])
				if theme == "village" and r.random() < 0.7:
					c.put(int(round(xx)) + side, y - 1, m[3])
		if theme == "corrupt":
			c.put(int(round(xx)), length, t["accent"])
	return c


def build_tiles():
	frames = []
	for theme in THEME_ORDER:
		for seed in range(SEEDS):
			for phase in range(PHASES):
				for mask in range(16):
					frames.append(terrain_tile(theme, seed, phase, mask))
	tiles = sheet(frames, 16)
	tufts = Canvas(T * 8, 12 * 2)
	vines = Canvas(T * 8, 24 * 2)
	for ti, theme in enumerate(THEME_ORDER):
		for v in range(8):
			tufts.blit(tuft(theme, v), v * T, ti * 12)
			vines.blit(vine(theme, v), v * T, ti * 24)
	return tiles, tufts, vines

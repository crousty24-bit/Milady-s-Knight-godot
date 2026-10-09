"""Terrain skin and underground back wall of N3 Black Forest (RUN-021 N3 visual pass).

terrain_black_forest_n3.png follows the layout of terrain_stone.png (16 px tiles, column =
exposure mask 1 up / 2 right / 4 down / 8 left, row = theme*18 + seed*6 + phase), with
four materials chosen in campaign_terrain_skin.gd:
  theme 0 = forest floor: the RUN-021 cold earth (readable pale moss rim kept) with leaf
            litter, needles and small stones near the surface;
  theme 1 = root layer: a tangle of roots in dark humus, ragged lower boundary;
  theme 2 = deep earth: edge overlay only, the skin draws n3_earth.png (seamless world-space
            texture: cold soil, slate boulders, roots, faint mycelium threads) underneath;
  theme 3 = bark: narrow tall columns read as giant trunks and roots (vertical grain, knots,
            moss, lit from the upper right like the N3 moon); a walkable top keeps the moss rim.
The forest thus reads as "an ancient wood rooted deep", distinct from N1 and N2 masonry.

n3_backwall.png (16 px tiles, 6 phases per row): back walls drawn behind enclosed spaces
(world space, behind terrain), much darker and flatter than the terrain:
  row 0-2 = root cave (rooms, shafts), row 3-5 = deep earth (the void under the forest).
n3_terrain_decals.png: rare 16x16 overlays (see decals()).
Usage: python3 tools/art/run021/n3/terrain_n3.py
"""
import functools
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "run020"))
from pixel import Canvas, hexc, save_png, sheet  # noqa: E402
from palette import STONE_COOL, WOOD  # noqa: E402
import world_terrain  # noqa: E402  (read only)

T = 16
STRIP = 96
SEEDS = 3
PHASES = STRIP // T
mix = world_terrain.mix
# RUN-021 lifted soil and pine rim (tools/art/run021/terrain_run021.py), kept for continuity.
SOIL = [hexc(c) for c in ("1d1b1f", "2b2729", "383236", "474045", "5a5258")]
PINE = [hexc(c) for c in ("111c1c", "182826", "213632", "2c4741", "4d7065")]
DEEP = [hexc(c) for c in ("1c1b21", "24222a", "2d2a33", "37343d", "44404a")]
BARK = [hexc(c) for c in ("161317", "1f1a1e", "2a2327", "373033", "463d40")]
ROOT_C = [mix(WOOD[0], SOIL[1], 0.5), mix(WOOD[1], SOIL[2], 0.5), mix(WOOD[2], SOIL[3], 0.55)]
LITTER = [hexc("3a2f2a"), hexc("4a3a2e"), hexc("2f3a33")]
FIREFLY = [hexc(c) for c in ("2c4a40", "4f7a66", "86b49c", "b4dcc8")]
BONE = [hexc("38352f"), hexc("57524a"), hexc("757060")]
RUST = [hexc("221a17"), hexc("33261f"), hexc("4a372a")]


def rng(*seed):
	return random.Random("-".join(map(str, ("run021-n3",) + seed)))


def _h(x, y, salt=0):
	return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xFFFF


# ------------------------------------------------------------------ deep earth (world space)
EARTH_W, EARTH_H = 256, 128


def earth_macro():
	"""Seamless 256x128 cold deep earth sampled in world space by the skin: soft blotches,
	wavy strata, slate boulders, roots and a few faint mycelium threads."""
	W, H = EARTH_W, EARTH_H
	c = Canvas(W, H)
	r = rng("earth-macro")
	c.rect(0, 0, W, H, DEEP[2])

	def wput(x, y, col):
		c.put(x % W, y % H, col)

	for _ in range(44):  # blotches
		bx, by, rx, ry = r.randint(0, W - 1), r.randint(0, H - 1), r.randint(4, 12), r.randint(2, 5)
		col = DEEP[1] if r.random() < 0.75 else DEEP[3]
		for y in range(by - ry, by + ry + 1):
			for x in range(bx - rx, bx + rx + 1):
				d = ((x - bx) / rx) ** 2 + ((y - by) / ry) ** 2
				if d < 0.5 or (d < 1.0 and (x + y) % 2 == 0):
					wput(x, y, col)
	for k in range(4):  # wavy strata
		base = int((k + 0.5) * H / 4) + r.randint(-3, 3)
		ph = r.uniform(0, 6.28)
		for x in range(W):
			y = base + int(round(2.6 * math.sin(2 * math.pi * x * 2 / W + ph)))
			if (x * 7 + k) % 9:
				wput(x, y, DEEP[1])
			if (x * 5 + k) % 11 == 0:
				wput(x, y - 1, DEEP[3])
	for _ in range(140):  # grit
		px, py = r.randint(0, W - 1), r.randint(0, H - 1)
		wput(px, py, DEEP[3])
		wput(px, py + 1, DEEP[0])
	for _ in range(18):  # slate boulders, lit from the upper right (N3 moon)
		sx, sy, rw, rh = r.randint(0, W - 1), r.randint(0, H - 1), r.randint(3, 7), r.randint(2, 4)
		for y in range(sy - rh, sy + rh + 1):
			for x in range(sx - rw, sx + rw + 1):
				d = ((x - sx) / rw) ** 2 + ((y - sy) / rh) ** 2
				if d <= 1.0:
					k = 3 if (y < sy and x > sx - 1 and d < 0.6) else 1 if y > sy else 2
					wput(x, y, mix(STONE_COOL[k], DEEP[2], 0.35))
		for x in range(sx - rw + 1, sx + rw + 1):
			wput(x, sy + rh + 1, DEEP[0])
	for i in range(10):  # roots; the last three are faint mycelium threads
		x, y = r.randint(0, W - 1), r.randint(0, H - 1)
		thread = i >= 7
		for k in range(r.randint(20, 46)):
			if thread:
				if k % 3 == 0:
					wput(x, y, FIREFLY[0] if k % 9 else FIREFLY[1])
			else:
				wput(x, y, ROOT_C[1] if k % 6 else ROOT_C[2])
				wput(x, y + 1, ROOT_C[0])
				if k % 8 == 5:
					wput(x + 1, y + 2, ROOT_C[0])  # rootlet
			x += 1
			y += r.choice((-1, 0, 0, 0, 1, 1)) if not thread else r.choice((-1, 0, 1))
	return c


def _earth_edges(c, r, mask, ramp=DEEP):
	if mask & 8:
		for y in range(T):
			c.put(0, y, ramp[0])
			c.put(1, y, ramp[3] if y % 5 else ramp[2])
	if mask & 2:
		for y in range(T):
			c.put(T - 1, y, ramp[0])
			c.put(T - 2, y, ramp[1])
	if mask & 4:
		for x in range(T):
			c.put(x, T - 1, ramp[0])
			c.put(x, T - 2, ramp[1])
		for x in range(1, T - 1):  # crumbling underside with root ends
			if r.random() < 0.3:
				c.px[(T - 1) * T + x] = None
			elif r.random() < 0.14:
				c.put(x, T - 1, ROOT_C[1])
	if mask & 1:
		_moss_rim(c, r, mask)


def _moss_rim(c, r, mask):
	"""Readable walkable rim: pale cold moss edge over darker moss drips (RUN-021 values)."""
	for x in range(T):
		c.put(x, 0, PINE[4] if r.random() > 0.12 else PINE[3])
		c.put(x, 1, PINE[3])
		c.put(x, 2, PINE[2] if x % 4 else PINE[1])
		for y in range(3, 3 + r.choice((0, 0, 1, 1, 2, 3))):
			c.put(x, y, PINE[1])
	if mask & 8:
		c.put(0, 0, SOIL[0])
	if mask & 2:
		c.put(T - 1, 0, SOIL[0])


def earth_tile(seed, phase, mask):
	"""Edge overlay only (interior transparent): the skin draws earth_macro underneath."""
	c = Canvas(T, T)
	_earth_edges(c, rng("earth-edge", seed, phase, mask), mask)
	return c


# ------------------------------------------------------------------ forest floor
@functools.lru_cache(maxsize=None)
def floor_strip(seed):
	"""Seamless 96x16 topsoil: packed cold earth, leaf litter, needles, pebbles, root threads."""
	c = Canvas(STRIP, T)
	r = rng("floor", seed)
	for y in range(T):
		for x in range(STRIP):
			h = _h(x, y, seed)
			k = 2 if h % 7 else 1
			if h % 23 == 0:
				k = 3
			c.put(x, y, SOIL[k])
	for _ in range(3 + seed):  # rounded stones
		sx, sy = r.randint(0, STRIP - 1), r.randint(5, 13)
		rw, rh = r.randint(2, 5), r.randint(1, 2)
		for y in range(sy - rh, sy + rh + 1):
			for x in range(sx - rw, sx + rw + 1):
				d = ((x - sx) / rw) ** 2 + ((y - sy) / rh) ** 2
				if d <= 1.0 and 0 <= y < T:
					k = 3 if y < sy and d < 0.7 else 1 if y > sy else 2
					c.put(x % STRIP, y, STONE_COOL[k])
		c.put((sx + rw) % STRIP, sy + 1, SOIL[0])
	for _ in range(26):  # leaf litter and needles in the upper half
		x, y = r.randint(0, STRIP - 1), r.randint(3, 8)
		col = r.choice(LITTER)
		c.put(x, y, col)
		if r.random() < 0.5:
			c.put((x + 1) % STRIP, y + r.choice((0, 1)), mix(col, SOIL[1], 0.4))
	for _ in range(2):  # root threads
		x, y = r.randint(0, STRIP - 1), r.randint(6, 13)
		for i in range(r.randint(14, 30)):
			c.put(x % STRIP, y, ROOT_C[1] if i % 5 else ROOT_C[2])
			x += 1
			y = max(4, min(T - 2, y + r.choice((-1, 0, 0, 0, 1))))
	return c


def floor_tile(seed, phase, mask):
	base = floor_strip(seed)
	c = Canvas(T, T)
	for y in range(T):
		for x in range(T):
			c.put(x, y, base.get(phase * T + x, y))
	_earth_edges(c, rng("floor-edge", seed, phase, mask), mask, SOIL)
	return c


# ------------------------------------------------------------------ root layer
def root_tile(seed, phase, mask):
	"""Humus packed with roots; its lower boundary is ragged so the deep earth shows below."""
	base = floor_strip((seed + 1) % SEEDS)
	c = Canvas(T, T)
	for x in range(T):
		gx = phase * T + x
		edge = 7 + int(round(2.5 * math.sin(gx * 2 * math.pi / STRIP * 2 + seed))) + (_h(gx // 3, seed, 9) % 3)
		for y in range(T):
			if y < edge:
				col = mix(base.get(gx, y), DEEP[2], 0.25)
			elif y == edge:
				col = DEEP[0]
			else:
				col = None
			if col is not None:
				c.put(x, y, col)
	r = rng("roots", seed, phase)
	for _ in range(3):  # thick roots crossing the tile, some dropping into the deep earth
		x, y = r.randint(-4, 6), r.randint(1, 9)
		for k in range(r.randint(10, 20)):
			if 0 <= x < T and 0 <= y < T:
				c.put(x, y, ROOT_C[2] if k % 4 == 0 else ROOT_C[1])
				if y + 1 < T:
					c.put(x, y + 1, ROOT_C[0])
			x += 1
			y += r.choice((0, 0, 1, 1, -1))
	_earth_edges(c, rng("root-edge", seed, phase, mask), mask & ~1, SOIL)
	if mask & 1:
		_moss_rim(c, rng("root-rim", seed, phase, mask), mask)
	return c


# ------------------------------------------------------------------ bark
@functools.lru_cache(maxsize=None)
def bark_strip(seed):
	"""Seamless 96x16 bark: vertical plates and furrows (vertical period 16 so tiles stack)."""
	c = Canvas(STRIP, T)
	r = rng("bark", seed)
	x = 0
	plates = []
	while x < STRIP:
		w = r.randint(4, 8)
		plates.append((x, w))
		x += w
	for x0, w in plates:
		lift = r.choice((0, 0, 1))
		for xx in range(x0, x0 + w):
			for y in range(T):
				if xx == x0:
					col = BARK[0]  # furrow
				elif xx == x0 + w - 1:
					col = BARK[3 if lift else 2]  # plate edge catching the moonlight (upper right)
				else:
					col = BARK[2 if (_h(xx, y, seed) % 9) else 1]
				c.put(xx % STRIP, y, col)
		# Horizontal cracks across a plate, wrapping vertically.
		for _ in range(r.randint(0, 2)):
			cy = r.randint(0, T - 1)
			for xx in range(x0 + 1, x0 + w - 1):
				c.put(xx % STRIP, cy, BARK[1])
	for _ in range(2 + seed):  # moss creeping up the plates
		mx, my = r.randint(0, STRIP - 1), r.randint(0, T - 1)
		for i in range(r.randint(3, 7)):
			c.put((mx + (i % 2)) % STRIP, (my + i) % T, PINE[1] if i % 3 else PINE[2])
	return c


def bark_tile(seed, phase, mask):
	base = bark_strip(seed)
	c = Canvas(T, T)
	for y in range(T):
		for x in range(T):
			c.put(x, y, base.get(phase * T + x, y))
	r = rng("bark-edge", seed, phase, mask)
	if (_h(seed, phase, mask) % 7) == 0:  # a knot
		kx, ky = r.randint(4, 10), r.randint(4, 10)
		for y in range(ky - 2, ky + 3):
			for x in range(kx - 2, kx + 3):
				d = (x - kx) ** 2 + (y - ky) ** 2
				if d <= 5:
					c.put(x, y, BARK[0] if d <= 1 else BARK[3] if (x > kx and y < ky) else BARK[1])
	if mask & 2:  # moon side (the N3 moon and beams light from the upper right): a lighter rim
		for y in range(T):
			c.put(T - 1, y, BARK[1])
			c.put(T - 2, y, BARK[4] if y % 6 else BARK[3])
	if mask & 8:
		for y in range(T):
			c.put(0, y, BARK[0])
			c.put(1, y, BARK[1])
	if mask & 4:
		for x in range(T):
			c.put(x, T - 1, BARK[0])
			c.put(x, T - 2, BARK[1])
		for x in range(1, T - 1):
			if r.random() < 0.25:
				c.px[(T - 1) * T + x] = None
	if mask & 1:
		_moss_rim(c, r, mask)
	return c


# ------------------------------------------------------------------ back walls
BACK_CAVE = [hexc(c) for c in ("0c0d10", "111317", "16181d", "1c1e24")]
BACK_DEEP = [hexc(c) for c in ("0a0a0d", "0d0e11", "111215", "15161a")]


@functools.lru_cache(maxsize=None)
def back_strip(kind, seed):
	"""Seamless 96x16 back wall strip: flat, very dark, minimal detail."""
	c = Canvas(STRIP, T)
	r = rng("back", kind, seed)
	ramp = BACK_CAVE if kind == "cave" else BACK_DEEP
	for y in range(T):
		for x in range(STRIP):
			h = _h(x, y, 40 + seed)
			c.put(x, y, ramp[1] if h % 6 else ramp[0])
	if kind == "cave":
		# Packed earth with embedded stones and roots running along the wall.
		for _ in range(3):
			sx, sy = r.randint(0, STRIP - 1), r.randint(2, 13)
			rw, rh = r.randint(3, 6), r.randint(1, 3)
			for y in range(sy - rh, sy + rh + 1):
				for x in range(sx - rw, sx + rw + 1):
					d = ((x - sx) / rw) ** 2 + ((y - sy) / rh) ** 2
					if d <= 1.0 and 0 <= y < T:
						c.put(x % STRIP, y, ramp[3] if y < sy else ramp[2])
		for _ in range(3):
			x, y = r.randint(0, STRIP - 1), r.randint(1, 14)
			for k in range(r.randint(16, 34)):
				c.put(x % STRIP, y, hexc("1b1714") if k % 5 else hexc("221c18"))
				x += 1
				y = max(0, min(T - 1, y + r.choice((-1, 0, 0, 1))))
	else:
		for _ in range(4):
			sx, sy = r.randint(0, STRIP - 1), r.randint(2, 13)
			for i in range(r.randint(2, 4)):
				c.put((sx + i) % STRIP, sy, ramp[3])
				c.put((sx + i) % STRIP, sy + 1, ramp[0])
		for _ in range(2):
			x, y = r.randint(0, STRIP - 1), r.randint(2, 13)
			for k in range(r.randint(10, 20)):
				c.put(x % STRIP, y, hexc("15120f"))
				x += 1
				y = max(1, min(T - 2, y + r.choice((-1, 0, 0, 1))))
	return c


def backwall():
	out = Canvas(STRIP, T * 6)
	for k, kind in enumerate(("cave", "deep")):
		for seed in range(SEEDS):
			out.blit(back_strip(kind, seed), 0, (k * 3 + seed) * T)
	return out


# ------------------------------------------------------------------ terrain decals
# 16x16 overlays drawn rarely by the skin over terrain cells (same depth shade):
# 0 skull, 1 bones, 2 rusted helm, 3 glowing mycelium, 4 burrow, 5 root knot, 6 slate slab,
# 7 buried rune stone. Transparent elsewhere. Kept dark: they are texture, not pickups.
def decals():
	out = Canvas(T * 8, T)
	# 0 skull half sunk in the earth
	c = Canvas(T, T)
	for y in range(5):
		for x in range(6):
			if (x, y) in ((0, 0), (5, 0)):
				continue
			c.put(5 + x, 6 + y, BONE[2] if y < 2 else BONE[1])
	for x, y in ((6, 8), (9, 8)):
		c.put(x, y, DEEP[0])
		c.put(x + 1, y, DEEP[0])
	c.put(8, 10, DEEP[0])
	for x in range(6, 10, 2):
		c.put(x, 11, BONE[1])
		c.put(x, 12, BONE[0])
	for x in range(4, 12):
		c.put(x, 13, DEEP[1])
	out.blit(c, 0, 0)
	# 1 two crossed bones
	c = Canvas(T, T)
	for i in range(9):
		c.put(3 + i, 6 + i // 3, BONE[2] if i % 4 else BONE[1])
		c.put(11 - i, 9 + i // 4, BONE[1])
	for x, y in ((2, 5), (2, 7), (12, 10), (12, 12)):
		c.put(x, y, BONE[2])
	out.blit(c, T, 0)
	# 2 rusted helm (dark, dented, half buried; no weapon)
	c = Canvas(T, T)
	for y in range(5, 12):
		for x in range(3, 13):
			d = ((x - 7.5) / 5) ** 2 + ((y - 11) / 6) ** 2
			if d <= 1.0:
				c.put(x, y, RUST[2] if (y < 8 and x < 8) else RUST[1])
	for x in range(4, 12):
		c.put(x, 9, RUST[0])  # eye slit
	c.put(9, 6, RUST[0])  # dent
	for x in range(2, 14):
		c.put(x, 12, DEEP[1])
	out.blit(c, 2 * T, 0)
	# 3 glowing mycelium cluster (cold, faint; the skin adds a dim glow)
	c = Canvas(T, T)
	r = rng("mycelium")
	for _ in range(16):
		bx, by = r.randint(3, 12), r.randint(4, 12)
		c.put(bx, by, FIREFLY[0] if r.random() < 0.6 else FIREFLY[1])
	for bx, by in ((6, 8), (9, 9), (7, 11)):
		c.put(bx, by, FIREFLY[2])
	out.blit(c, 3 * T, 0)
	# 4 burrow: a dark hole with root fringe
	c = Canvas(T, T)
	for y in range(4, 13):
		for x in range(2, 14):
			d = ((x - 7.5) / 5.5) ** 2 + ((y - 8.5) / 4) ** 2
			if d <= 1.0:
				c.put(x, y, hexc("0b0b0d") if d < 0.7 else DEEP[0])
	for x in (4, 7, 10):
		c.put(x, 4, ROOT_C[1])
		c.put(x + 1, 5, ROOT_C[0])
	for x in range(3, 13):
		c.put(x, 13, DEEP[3] if x % 3 else DEEP[2])
	out.blit(c, 4 * T, 0)
	# 5 root knot: a cut root seen end-on with rings
	c = Canvas(T, T)
	for y in range(3, 13):
		for x in range(3, 13):
			d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
			if d <= 4.6:
				c.put(x, y, ROOT_C[0] if d > 3.8 else ROOT_C[2] if int(d) % 2 else ROOT_C[1])
	out.blit(c, 5 * T, 0)
	# 6 slate slab (a flat buried stone, lit from the upper left)
	c = Canvas(T, T)
	for y in range(6, 11):
		for x in range(2, 14):
			if (x, y) in ((2, 6), (13, 6), (2, 10), (13, 10)):
				continue
			c.put(x, y, STONE_COOL[3] if y == 6 else STONE_COOL[1] if y == 10 else STONE_COOL[2])
	for x in range(5, 9):
		c.put(x, 8, STONE_COOL[1])
	out.blit(c, 6 * T, 0)
	# 7 buried rune stone with a very dim cold rune
	c = Canvas(T, T)
	for y in range(3, 14):
		for x in range(4, 12):
			if (x in (4, 11)) and y < 5:
				continue
			c.put(x, y, STONE_COOL[2] if x < 7 else STONE_COOL[1])
	for x, y in ((7, 6), (7, 7), (7, 8), (7, 9), (8, 7), (9, 6), (8, 9), (9, 10)):
		c.put(x, y, FIREFLY[0])
	out.blit(c, 7 * T, 0)
	return out


def build():
	frames = []
	for theme in (floor_tile, root_tile, earth_tile, bark_tile):
		for seed in range(SEEDS):
			for phase in range(PHASES):
				for mask in range(16):
					frames.append(theme(seed, phase, mask))
	return {"terrain_black_forest_n3": sheet(frames, 16), "n3_backwall": backwall(), "n3_terrain_decals": decals(), "n3_earth": earth_macro()}


def preview(out_dir, built):
	"""Floor, roots and deep earth laid out as the skin draws them (with depth shade), a pit to
	show side walls, a bark column on the right and back walls behind."""
	tiles, macro, back = built["terrain_black_forest_n3"], built["n3_earth"], built["n3_backwall"]
	W, H = 16 * 32, 16 * 14
	c = Canvas(W, H)
	c.rect(0, 0, W, H, hexc("10181a"))
	solid = set()
	for cy in range(3, 14):
		for cx in range(32):
			if 18 <= cx <= 21 and cy < 9:
				continue  # a pit showing earth side walls
			if cx >= 26 and cy < 6:
				continue
			solid.add((cx, cy))
	for cy in range(0, 3):
		for cx in (27, 28):
			solid.add((cx, cy))  # a trunk column
	for cy in range(3, 6):
		for cx in (27, 28):
			solid.add((cx, cy))
	bark = {(cx, cy) for (cx, cy) in solid if cx in (27, 28) and cy < 6}
	for (cx, cy) in [(x, y) for x in range(18, 22) for y in range(3, 9)]:
		for y in range(16):
			for x in range(16):
				c.put(cx * 16 + x, cy * 16 + y, back.get((cx * 16 + x) % 96, (cy % 3) * 16 + y))
	for (cx, cy) in solid:
		depth = 0
		while depth < 5 and (cx, cy - depth - 1) in solid:
			depth += 1
		mask = (0 if (cx, cy - 1) in solid else 1) | (0 if (cx + 1, cy) in solid else 2) | (0 if (cx, cy + 1) in solid or cy == 13 else 4) | (0 if (cx - 1, cy) in solid else 8)
		theme = 3 if (cx, cy) in bark else 0 if depth <= 1 else 1 if depth == 2 else 2
		row = theme * 18 + (cy % 3) * 6 + cx % 6
		shade = 0.92 if theme == 3 else [1.0, 0.92, 0.84, 0.78, 0.74, 0.72][min(depth, 5)]
		for y in range(16):
			for x in range(16):
				col = None
				if theme in (1, 2):
					col = macro.get((cx * 16 + x) % macro.w, (cy * 16 + y) % macro.h)
				t = tiles.get(mask * 16 + x, row * 16 + y)
				if t is not None:
					col = t
				if col is not None:
					c.put(cx * 16 + x, cy * 16 + y, tuple(int(v * shade) for v in col[:3]) + (255,))
	save_png(c, os.path.join(out_dir, "terrain_n3_stack.png"), 3)


if __name__ == "__main__":
	out = os.path.join(ROOT, "assets", "run021", "n3")
	os.makedirs(out, exist_ok=True)
	built = build()
	for name, canvas in built.items():
		save_png(canvas, os.path.join(out, name + ".png"))
		print("wrote", name, canvas.w, "x", canvas.h)
	prev = os.path.join(ROOT, "work", "run021", "n3pass", "preview")
	os.makedirs(prev, exist_ok=True)
	preview(prev, built)
	save_png(built["n3_terrain_decals"], os.path.join(prev, "terrain_n3_decals.png"), 4)

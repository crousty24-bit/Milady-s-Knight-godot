"""Terrain skins of N2-N4 (RUN-020).

terrain_campaign.png follows the layout of assets/sprites/terrain_stone.png (16 px tiles,
column = exposure mask 1 up / 2 right / 4 down / 8 left, row = theme*18 + seed*6 + phase):
  theme 0 = Blight Town: the masonry of world_terrain.py with rot moss and mud tint;
  theme 1 = Black Forrest: packed earth with stones and roots under a cold moss rim.
Forbidden Graveyard keeps terrain_stone.png theme 0 (village masonry) unchanged, so the
RUN-019 secret wall, which samples those exact tiles, matches its surroundings.

tufts_campaign.png (16x12 cells) and vines_campaign.png (16x24 cells): 8 variants per row,
row 0 = N2, row 1 = N3, row 2 = N4. Tufts stand on the surface (baseline row 10, drawn at
cell y - 11); vines hang under overhangs (drawn at cell y + 15), as in TerrainSkin.
"""
import functools
import math
import os
import random
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from pixel import Canvas, sheet  # noqa: E402
from palette import STONE, STONE_COOL, WOOD  # noqa: E402
import world_terrain  # noqa: E402  (read only: functions reused, file untouched)
from palette_run020 import DUSK_VIOLET, MUD, PINE, ROT, SOIL, SPECTRAL  # noqa: E402

T = 16
STRIP = 96
SEEDS = 3
PHASES = STRIP // T
world_terrain.THEMES["blight_town"] = dict(stone=STONE, moss=ROT[:4], accent=ROT[4], tint=MUD[2], tint_k=0.22)


def rng(*seed):
	return random.Random("-".join(map(str, ("run020",) + seed)))


def _h(x, y, salt=0):
	return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xFFFF


# ------------------------------------------------------------------ N3 earth
@functools.lru_cache(maxsize=None)
def soil_strip(seed):
	"""Seamless 96x16 packed earth with embedded stones and root threads."""
	c = Canvas(STRIP, T)
	r = rng("soil", seed)
	for y in range(T):
		for x in range(STRIP):
			h = _h(x, y, seed)
			k = 2 if h % 7 else 1
			if h % 23 == 0:
				k = 3
			c.put(x, y, SOIL[k])
	# Rounded stones, wrapping horizontally.
	for _ in range(3 + seed):
		sx, sy = r.randint(0, STRIP - 1), r.randint(2, 13)
		rw, rh = r.randint(3, 6), r.randint(2, 3)
		for y in range(sy - rh, sy + rh + 1):
			for x in range(sx - rw, sx + rw + 1):
				d = ((x - sx) / rw) ** 2 + ((y - sy) / rh) ** 2
				if d <= 1.0 and 0 <= y < T:
					k = 3 if y < sy - rh / 2 and d < 0.7 else 1 if y > sy + rh / 2 else 2
					c.put(x % STRIP, y, STONE_COOL[k])
		c.put((sx + rw) % STRIP, sy + 1, SOIL[0])
	# Root threads.
	for _ in range(2):
		x, y = r.randint(0, STRIP - 1), r.randint(3, 12)
		for i in range(r.randint(14, 30)):
			c.put(x % STRIP, y, WOOD[1] if i % 5 else WOOD[2])
			x += 1
			y = max(1, min(T - 2, y + r.choice((-1, 0, 0, 0, 1))))
	return c


def earth_tile(seed, phase, mask):
	base = soil_strip(seed)
	c = Canvas(T, T)
	for y in range(T):
		for x in range(T):
			c.put(x, y, base.get(phase * T + x, y))
	r = rng("earth", seed, phase, mask)
	if mask & 8:
		for y in range(T):
			c.put(0, y, SOIL[0])
			c.put(1, y, SOIL[3] if y % 5 else SOIL[1])
	if mask & 2:
		for y in range(T):
			c.put(T - 1, y, SOIL[0])
			c.put(T - 2, y, SOIL[1])
	if mask & 4:
		for x in range(T):
			c.put(x, T - 1, SOIL[0])
			c.put(x, T - 2, SOIL[1])
		for x in range(1, T - 1):
			if r.random() < 0.3:
				c.px[(T - 1) * T + x] = None
		for x in range(T):  # root ends poking out of the underside
			if r.random() < 0.12:
				c.put(x, T - 1, WOOD[1])
	if mask & 1:
		# Readable walkable rim: pale cold moss edge, then darker courses with drips.
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
	return c


# ------------------------------------------------------------------ tufts / vines
def tuft(biome, variant):
	c = Canvas(T, 12)
	r = rng("tuft", biome, variant)
	x = r.randint(0, 2)
	while x < T:
		k = r.random()
		if biome == 0:  # N2: dead grass, rot sprouts and fungal caps
			if k < 0.6:
				h = r.choice((2, 3, 3, 4, 5))
				for y in range(h):
					c.put(x + (r.choice((-1, 0, 1)) if y == h - 1 else 0), 10 - y, ROT[3] if y == h - 1 else ROT[2])
			elif k < 0.8:
				c.put(x, 10, MUD[2])
				c.put(x, 9, ROT[3])
				c.put(x - 1, 9, ROT[2])
				c.put(x + 1, 8, ROT[4])
			else:
				for dx in (-1, 0, 1):
					c.put(x + dx, 9, MUD[3])
				c.put(x, 10, MUD[1])
				c.put(x, 8, MUD[4])
			c.put(x, 11, ROT[1])
		elif biome == 1:  # N3: cold ferns and grass blades
			if k < 0.55:
				h = r.choice((3, 4, 5, 6))
				lean = r.choice((-1, 0, 1))
				for y in range(h):
					c.put(x + (lean if y >= h - 2 else 0), 10 - y, PINE[4] if y == h - 1 else PINE[3] if y > 1 else PINE[2])
			elif k < 0.85:
				h = r.choice((3, 4))
				for y in range(h):
					c.put(x, 10 - y, PINE[2])
				for dx, dy in ((-1, 1), (1, 1), (-2, 2), (2, 2)):
					c.put(x + dx, 10 - h + dy, PINE[3])
			else:
				c.put(x, 10, STONE_COOL[3])
				c.put(x + 1, 10, STONE_COOL[2])
				c.put(x, 9, STONE_COOL[4])
			c.put(x, 11, PINE[1])
		else:  # N4: dry pale grass, rare dim spectral bloom
			if k < 0.75:
				h = r.choice((2, 3, 4, 5))
				lean = r.choice((-1, 0, 0, 1))
				for y in range(h):
					c.put(x + (lean if y >= h - 2 else 0), 10 - y, DUSK_VIOLET[5] if y == h - 1 else DUSK_VIOLET[4] if y > 0 else DUSK_VIOLET[3])
			elif k < 0.9:
				c.put(x, 10, STONE[3])
				c.put(x + 1, 10, STONE[2])
			else:
				for y in range(3):
					c.put(x, 10 - y, DUSK_VIOLET[3])
				c.put(x, 7, SPECTRAL[3])
			c.put(x, 11, DUSK_VIOLET[2])
		x += r.choice((2, 3, 3, 4, 5))
	return c


def vine(biome, variant):
	c = Canvas(T, 24)
	r = rng("vine", biome, variant)
	for x in sorted(r.sample(range(1, T - 1), r.randint(2, 3))):
		length = r.randint(5, 20)
		xx = float(x)
		for y in range(length):
			xx += r.choice((-0.34, 0, 0, 0.34))
			if biome == 0:  # rot strings ending in a drip
				col = ROT[1] if y < length - 2 else ROT[3]
			elif biome == 1:  # roots
				col = WOOD[1] if y < length - 3 else WOOD[2]
				if y % 5 == 3:
					c.put(int(round(xx)) + (1 if y % 10 < 5 else -1), y, WOOD[1])
			else:  # dead roots and web threads
				col = DUSK_VIOLET[2] if y < length - 3 else DUSK_VIOLET[4]
			c.put(int(round(xx)), y, col)
		if biome == 0:
			c.put(int(round(xx)), length, ROT[4])
	if biome == 2 and r.random() < 0.6:
		# A sagging web thread between two strands (very low contrast).
		for x in range(2, T - 2):
			c.put(x, 3 + int(2 * math.sin(math.pi * (x - 2) / (T - 4))), DUSK_VIOLET[3])
	return c


def build():
	frames = []
	for seed in range(SEEDS):
		for phase in range(PHASES):
			for mask in range(16):
				frames.append(world_terrain.terrain_tile("blight_town", seed, phase, mask))
	for seed in range(SEEDS):
		for phase in range(PHASES):
			for mask in range(16):
				frames.append(earth_tile(seed, phase, mask))
	tiles = sheet(frames, 16)
	tufts = Canvas(T * 8, 12 * 3)
	vines = Canvas(T * 8, 24 * 3)
	for b in range(3):
		for v in range(8):
			tufts.blit(tuft(b, v), v * T, b * 12)
			vines.blit(vine(b, v), v * T, b * 24)
	return {"terrain_campaign": tiles, "tufts_campaign": tufts, "vines_campaign": vines}

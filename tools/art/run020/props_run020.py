"""New decor props of N2-N4 (RUN-020). Origin: bottom-centre of the canvas unless noted.

Decor only: darker and less saturated than gameplay (coins gold, Slimes, plants, turrets,
doors), outlines omitted so they stay behind the gameplay read. Each biome also reuses
N1 props from assets/sprites/ (houses, cart, fence, graves, bones, crow, roots, bushes...),
listed in scripts/campaign_decor.gd.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from pixel import Canvas, hexc  # noqa: E402
from palette import EMBER, MOSS, STONE, STONE_COOL, WOOD  # noqa: E402
from world_props import masonry_rect  # noqa: E402  (read only)
from palette_run020 import DUSK_VIOLET, MUD, PINE, ROT, SOIL, SPECTRAL  # noqa: E402


def rng(*seed):
	return random.Random("-".join(map(str, ("run020-props",) + seed)))


def ellipse(c, cx, cy, rx, ry, shade):
	"""Filled ellipse; shade(x, y, d) returns a colour or None."""
	for y in range(int(cy - ry), int(cy + ry) + 1):
		for x in range(int(cx - rx), int(cx + rx) + 1):
			d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
			if d <= 1.0:
				c.put(x, y, shade(x, y, d))


# ------------------------------------------------------------------ N2
def barrels():
	"""30x22 two rotting barrels and a spill of ooze."""
	c = Canvas(30, 22)
	for bx, top in ((2, 4), (15, 8)):
		for y in range(top, 21):
			for x in range(bx, bx + 12):
				bulge = 1 if y in (top, 20) else 0
				if (x == bx and bulge) or (x == bx + 11 and bulge):
					continue
				k = 3 if x < bx + 3 else 1 if x > bx + 9 else 2
				col = WOOD[k]
				if (y - top) in (2, 9, 15) or y == 20:
					col = STONE[1] if x % 3 else STONE[2]  # iron hoops
				c.put(x, y, col)
		for x in range(bx + 1, bx + 11):
			c.put(x, top, WOOD[0])
	for x in range(0, 30):  # ooze puddle
		if 3 < x < 27:
			c.put(x, 21, ROT[2] if x % 4 else ROT[3])
	for y in range(9, 18):
		c.put(13, y, ROT[2])
	c.put(13, 18, ROT[3])
	return c


def rot_mound():
	"""32x14 heap of rot with pustules."""
	c = Canvas(32, 14)
	r = rng("mound")
	ellipse(c, 16, 14, 15, 11, lambda x, y, d: ROT[3] if (y < 8 and d < 0.6 and (x + y) % 3) else ROT[2] if d < 0.85 else ROT[1])
	for _ in range(7):
		px, py = r.randint(6, 25), r.randint(6, 12)
		c.put(px, py, ROT[4])
		c.put(px + 1, py, MUD[3])
		c.put(px, py + 1, ROT[1])
	return c


def well():
	"""30x34 broken village well with a rotten winch."""
	c = Canvas(30, 34)
	r = rng("well")
	masonry_rect(c, 2, 20, 26, 14, STONE, r, course=5, moss=list(ROT[:3]))
	for x in range(2, 28):
		c.put(x, 20, STONE[4])
	for px in (4, 25):
		for y in range(3, 20):
			c.put(px, y, WOOD[2])
			c.put(px + 1, y, WOOD[1])
	for x in range(2, 28):
		c.put(x, 3, WOOD[3])
		c.put(x, 4, WOOD[1])
	for y in range(5, 15):
		c.put(15, y, STONE_COOL[2])
	for x in range(12, 19):
		c.put(x, 15, WOOD[2])
	c.put(18, 15, WOOD[0])
	return c


# ------------------------------------------------------------------ N3
def big_pine():
	"""48x100 dark pine, moonlit needle tips on the right."""
	c = Canvas(48, 100)
	r = rng("pine")
	for y in range(70, 100):
		for x in range(21, 27):
			c.put(x, y, WOOD[1] if x < 25 else WOOD[0])
	for i in range(88):
		y = 88 - i
		t = i / 88
		half = (1 - t) * 22 + 1
		if i % 9 >= 6:
			half *= 0.72
		for x in range(int(24 - half), int(24 + half) + 1):
			lit = x > 24 + half * 0.55
			c.put(x, y, PINE[2] if lit else PINE[1] if (x + y) % 5 else PINE[0])
		if i % 9 == 5 and half > 3:
			c.put(int(24 + half), y, PINE[3])
	for x in range(18, 31):  # root flare
		if r.random() < 0.7:
			c.put(x, 99, WOOD[0])
	return c


def stump():
	"""24x14 cut stump with roots."""
	c = Canvas(24, 14)
	for y in range(3, 14):
		for x in range(6, 18):
			c.put(x, y, WOOD[2] if x < 9 else WOOD[1])
	for x in range(6, 18):
		c.put(x, 3, WOOD[4] if 8 < x < 16 else WOOD[3])
		c.put(x, 4, WOOD[3])
	c.put(11, 3, WOOD[2])
	c.put(12, 3, WOOD[2])
	for x, d in ((2, 1), (4, 1), (19, -1), (21, -1)):
		for y in range(10, 14):
			c.put(x + (y - 10) * -d // 2, y, WOOD[1])
	for x in range(7, 12):
		c.put(x, 5, PINE[2])
	return c


def mossy_rock():
	"""28x16 boulder with a cold moss cap."""
	c = Canvas(28, 16)
	ellipse(c, 14, 16, 13, 13, lambda x, y, d: STONE_COOL[4] if (x < 12 and d < 0.5) else STONE_COOL[3] if d < 0.8 else STONE_COOL[2])
	for x in range(5, 23):
		top = next((y for y in range(16) if c.get(x, y) is not None), None)
		if top is not None:
			c.put(x, top, PINE[3])
			if x % 3:
				c.put(x, top + 1, PINE[2])
	return c


def fungus():
	"""16x10 cluster of pale cold shelf mushrooms."""
	c = Canvas(16, 10)
	for cx, cy, rw in ((4, 6, 3), (10, 4, 4), (13, 7, 2)):
		for y in range(cy, 10):
			c.put(cx, y, SOIL[4])
		for x in range(cx - rw, cx + rw + 1):
			c.put(x, cy, STONE_COOL[5] if x < cx else STONE_COOL[4])
			if abs(x - cx) < rw:
				c.put(x, cy - 1, STONE_COOL[4])
	return c


# ------------------------------------------------------------------ N4
def mausoleum():
	"""60x62 small crypt with a pediment and sealed door."""
	c = Canvas(60, 62)
	r = rng("mausoleum")
	masonry_rect(c, 6, 22, 48, 40, STONE_COOL, r, course=6, moss=list(DUSK_VIOLET[1:4]))
	for i in range(14):  # pediment
		half = 27 * (1 - i / 14)
		for x in range(int(30 - half), int(30 + half) + 1):
			c.put(x, 21 - i, STONE_COOL[4] if x < 30 else STONE_COOL[2])
	for x in range(3, 57):
		c.put(x, 22, STONE_COOL[5])
		c.put(x, 23, STONE_COOL[1])
	for px in (10, 45):
		for y in range(24, 62):
			c.put(px, y, STONE_COOL[4])
			c.put(px + 4, y, STONE_COOL[1])
	for y in range(36, 62):
		for x in range(23, 37):
			c.put(x, y, DUSK_VIOLET[0] if (x + y) % 7 else DUSK_VIOLET[1])
	for x in range(23, 37):
		c.put(x, 35, STONE_COOL[4])
	c.put(30, 12, SPECTRAL[1])
	return c


def tall_cross():
	"""18x34 ringed stone cross."""
	c = Canvas(18, 34)
	for y in range(2, 34):
		c.put(8, y, STONE[4])
		c.put(9, y, STONE[2])
	for x in range(2, 16):
		c.put(x, 9, STONE[4])
		c.put(x, 10, STONE[2])
	for a in range(36):
		ang = a * math.tau / 36
		c.put(int(round(8.5 + 5 * math.cos(ang))), int(round(9.5 + 5 * math.sin(ang))), STONE[3])
	for x in range(5, 13):
		c.put(x, 32, STONE[3])
		c.put(x, 33, STONE[1])
	for y in range(26, 32):
		c.put(10, y, DUSK_VIOLET[3])
	return c


def iron_fence():
	"""48x24 wrought-iron fence with spear tips, one bar bent."""
	c = Canvas(48, 24)
	for x in range(1, 47, 5):
		bend = 2 if x == 26 else 0
		for y in range(3, 24):
			c.put(x + (bend if y < 10 else 0), y, STEEL_D[1])
		c.put(x + bend, 2, STEEL_D[2])
		c.put(x + bend - 1, 3, STEEL_D[1])
		c.put(x + bend + 1, 3, STEEL_D[1])
		c.put(x + bend, 1, STEEL_D[2])
	for y in (7, 19):
		for x in range(0, 48):
			c.put(x, y, STEEL_D[0])
	return c


STEEL_D = [hexc("1f1d26"), hexc("2f2c38"), hexc("454152")]


def willow():
	"""64x84 dead weeping willow."""
	c = Canvas(64, 84)
	r = rng("willow")
	col, lit = DUSK_VIOLET[2], DUSK_VIOLET[3]
	for y in range(36, 84):
		w = 3 + (84 - y) // 30
		for x in range(32 - w, 32 + w):
			c.put(x + (1 if y < 50 else 0), y, lit if x == 32 + w - 1 else col)

	def branch(x, y, ang, length, depth):
		if depth == 0:
			return
		x1, y1 = x + math.cos(ang) * length, y + math.sin(ang) * length
		for i in range(int(length) + 1):
			t = i / max(1, length)
			c.put(int(x + (x1 - x) * t), int(y + (y1 - y) * t), col)
		for _ in range(2):
			branch(x1, y1, ang + r.uniform(-0.6, 0.6), length * 0.65, depth - 1)
		if depth <= 2:
			for i in range(r.randint(6, 20)):  # hanging strands
				c.put(int(x1) + (i // 7), int(y1) + i, col if i % 4 else lit)

	branch(32, 38, -math.pi / 2, 14, 5)
	return c


def ghost_candle():
	"""8x14 grave candle with a dim spectral flame (the backdrop adds a low-alpha cold glow)."""
	c = Canvas(8, 14)
	for y in range(7, 14):
		c.put(3, y, STONE[4])
		c.put(4, y, STONE[3])
	for x in range(2, 6):
		c.put(x, 13, STONE[2])
	c.put(3, 6, SPECTRAL[3])
	c.put(4, 6, SPECTRAL[2])
	c.put(3, 5, SPECTRAL[4])
	c.put(4, 4, SPECTRAL[2])
	return c


PROPS = {
	"blight_town_barrels": barrels, "blight_town_rot_mound": rot_mound, "blight_town_well": well,
	"black_forrest_pine": big_pine, "black_forrest_stump": stump, "black_forrest_rock": mossy_rock,
	"black_forrest_fungus": fungus,
	"forbidden_graveyard_mausoleum": mausoleum, "forbidden_graveyard_cross": tall_cross,
	"forbidden_graveyard_fence": iron_fence, "forbidden_graveyard_willow": willow,
	"forbidden_graveyard_candle": ghost_candle,
}
_ = (EMBER, MOSS)

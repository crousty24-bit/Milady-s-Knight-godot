"""Generate the slice terrain tiles, parallax backdrop and narrative props.

Usage: python3 tools/art/world.py [--preview DIR]

RUN-013. Terrain tiles are 16x16, indexed by an exposure mask (bit 1 = open
above, 2 = open right, 4 = open below, 8 = open left), so TerrainSkin can skin
the authored TileMapLayer without touching it. Two themes: the abandoned
village (warm stone, moss) and the corrupted approach (cold stone, violet
blight). Backdrop layers tile horizontally and are scrolled by
scripts/backdrop.gd at reduced speed.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, grid, hexc, save_png, sheet  # noqa: E402
from palette import (BLOOD, CORRUPT, EMBER, GOLD, MIST, MOSS, OUTLINE, SKY, STEEL,  # noqa: E402
	STONE, STONE_COOL, WOOD)

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
T = 16


def rng(*seed):
	# String seeds are hashed deterministically, so outputs are reproducible.
	return random.Random("-".join(map(str, seed)))


# ---------------------------------------------------------------- terrain
THEMES = {
	"village": dict(stone=STONE, moss=MOSS, accent=MOSS[3]),
	"corrupt": dict(stone=STONE_COOL, moss=CORRUPT[:4], accent=CORRUPT[4]),
}
# Brick layouts per variant: course rows and the x positions of vertical joints.
COURSES = [
	[(0, 7, [6]), (8, 15, [2, 11])],
	[(0, 7, [10]), (8, 15, [4, 13])],
	[(0, 7, [3, 12]), (8, 15, [8])],
]


def masonry(theme, variant):
	s = THEMES[theme]["stone"]
	c = Canvas(T, T)
	r = rng(theme, variant)
	for top, bottom, joints in COURSES[variant]:
		edges = [0] + joints + [T]
		for i in range(len(edges) - 1):
			x0, x1 = edges[i], edges[i + 1]
			base = s[2] if r.random() < 0.5 else s[3]
			for y in range(top, bottom + 1):
				for x in range(x0, x1):
					col = base
					if y == bottom or x == x1 - 1:
						col = s[0]  # mortar joint
					elif y == top:
						col = s[4] if base == s[3] else s[3]
					elif x == x0:
						col = s[3] if base == s[2] else s[4]
					elif y == bottom - 1:
						col = s[1] if base == s[2] else s[2]
					c.put(x, y, col)
			# Weathering: a couple of pits and a hairline crack.
			for _ in range(2):
				px, py = r.randint(x0 + 1, max(x0 + 1, x1 - 3)), r.randint(top + 1, max(top + 1, bottom - 2))
				c.put(px, py, s[1])
			if r.random() < 0.35 and x1 - x0 > 4:
				cx = r.randint(x0 + 2, x1 - 3)
				for y in range(top + 2, bottom - 1):
					if r.random() < 0.7:
						c.put(cx, y, s[1])
					cx += r.choice((-1, 0, 0, 1)) if x0 + 1 < cx < x1 - 2 else 0
	return c


def terrain_tile(theme, variant, mask):
	t = THEMES[theme]
	s, m = t["stone"], t["moss"]
	c = masonry(theme, variant)
	r = rng(theme, variant, mask, "edge")
	up, right, down, left = mask & 1, mask & 2, mask & 4, mask & 8
	if left:
		for y in range(T):
			c.put(0, y, s[0])
			c.put(1, y, s[4] if c.get(1, y) not in (s[0],) else s[3])
	if right:
		for y in range(T):
			c.put(T - 1, y, s[0])
			c.put(T - 2, y, s[1])
	if down:
		for x in range(T):
			c.put(x, T - 1, s[0])
			c.put(x, T - 2, s[1])
	if up:
		# Walkable rim: one lighter capstone row, then moss creeping down.
		for x in range(T):
			c.put(x, 0, s[5])
			c.put(x, 1, s[4])
			c.put(x, 2, s[2] if x % 5 else s[1])
		for x in range(T):
			depth = r.choice((1, 1, 2, 2, 3, 4)) if theme == "village" else r.choice((0, 1, 1, 2, 3))
			for y in range(depth):
				c.put(x, y, m[2] if y == 0 else (m[1] if y < depth - 1 else m[0]))
			if theme == "village" and r.random() < 0.25:
				c.put(x, 0, m[3])
		if left:
			c.put(0, 0, s[0])
		if right:
			c.put(T - 1, 0, s[0])
	return c


def tuft_overlay(theme, variant):
	"""Grass (village) or blighted tendrils (corrupt) sitting on top of a surface tile.
	Drawn 16x8; rows 0..5 stand above the tile top, rows 6..7 overlap it."""
	t = THEMES[theme]
	m = t["moss"]
	c = Canvas(T, 8)
	r = rng(theme, variant, "tuft")
	x = r.randint(0, 3)
	while x < T:
		h = r.choice((1, 2, 2, 3, 4)) if theme == "village" else r.choice((1, 2, 3, 5))
		for y in range(h):
			col = m[3] if y == h - 1 else m[2]
			if theme == "corrupt":
				col = m[2] if y < h - 1 else t["accent"]
			c.put(x, 5 - y, col)
		if theme == "village" and h >= 3 and x + 1 < T:
			c.put(x + 1, 5 - (h - 2), m[2])
		c.put(x, 6, m[1])
		x += r.choice((2, 3, 3, 4, 5))
	return c


def build_tiles():
	frames = []
	for theme in ("village", "corrupt"):
		for variant in range(3):
			for mask in range(16):
				frames.append(terrain_tile(theme, variant, mask))
	tiles = sheet(frames, 16)
	tufts = Canvas(T * 6, 8)
	for i, (theme, variant) in enumerate([(th, v) for th in ("village", "corrupt") for v in range(3)]):
		tufts.blit(tuft_overlay(theme, variant), i * T, 0)
	return tiles, tufts


# ---------------------------------------------------------------- backdrop
def dither_band(c, y0, y1, a, b, x0=0, x1=None):
	"""Vertical a->b blend with a 4x4 ordered dither (pixel-art gradient)."""
	bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
	x1 = c.w if x1 is None else x1
	for y in range(y0, y1):
		t = (y - y0) / max(1, y1 - y0 - 1)
		for x in range(x0, x1):
			c.put(x, y, b if t * 16 > bayer[y % 4][x % 4] + 0.5 else a)


def sky():
	"""Screen-fixed 640x360: night gradient, red moon, thin clouds, few stars."""
	c = Canvas(640, 360)
	bands = [SKY[0], SKY[1], SKY[2], SKY[3], SKY[4]]
	h = 360 // (len(bands) - 1)
	for i in range(len(bands) - 1):
		dither_band(c, i * h, (i + 1) * h, bands[i], bands[i + 1])
	r = rng("stars")
	for _ in range(70):
		x, y = r.randint(0, 639), r.randint(0, 150)
		c.put(x, y, MIST[2] if r.random() < 0.2 else MIST[0])
	# Blood moon (Art Bible: rare saturated red), soft halo then disc.
	mx, my, rad = 500, 70, 24
	halo = [hexc("3a1a24"), hexc("2c1820")]
	for y in range(my - rad - 14, my + rad + 15):
		for x in range(mx - rad - 14, mx + rad + 15):
			d = math.hypot(x - mx, y - my)
			if rad < d <= rad + 6 and (x + y) % 2 == 0:
				c.put(x, y, halo[0])
			elif rad + 6 < d <= rad + 14 and (x + y) % 4 == 0:
				c.put(x, y, halo[1])
	moon = [BLOOD[0], BLOOD[1], BLOOD[2], BLOOD[3], BLOOD[4]]
	for y in range(my - rad, my + rad + 1):
		for x in range(mx - rad, mx + rad + 1):
			d = math.hypot(x - mx, y - my)
			if d > rad:
				continue
			# Lit from upper-left, darker limb, a few craters.
			lx, ly = (x - mx) / rad, (y - my) / rad
			light = 0.55 - 0.45 * (lx * 0.6 + ly * 0.8) - 0.35 * (d / rad) ** 3
			k = 3 if light > 0.85 else 2 if light > 0.45 else 1 if light > 0.1 else 0
			c.put(x, y, moon[k])
	for cx, cy, cr in ((490, 60, 4), (510, 80, 3), (505, 63, 2), (484, 78, 2), (516, 66, 1)):
		for y in range(cy - cr, cy + cr + 1):
			for x in range(cx - cr, cx + cr + 1):
				if math.hypot(x - cx, y - cy) <= cr:
					c.put(x, y, moon[1] if x + y < cx + cy else moon[2])
	# Long ragged cloud banks, two tones, one crossing the moon.
	for cy, cx, w in ((58, 360, 230), (100, 410, 200), (40, 40, 170), (128, 90, 220), (24, 250, 130)):
		for x in range(cx, cx + w):
			t = (x - cx) / w
			thick = int(1 + 3 * math.sin(math.pi * t) + math.sin(x / 5.0))
			for yy in range(cy - thick // 2, cy + thick - thick // 2):
				c.put(x % 640, yy, SKY[3] if yy == cy - thick // 2 else SKY[2])
			if 0.2 < t < 0.8 and x % 3 == 0:
				c.put(x % 640, cy - thick // 2 - 1, SKY[4])
	return c


def far_layer():
	"""640x150 tiling: distant crags and the Darkveil citadel with ember windows."""
	W, H = 640, 150
	c = Canvas(W, H)
	r = rng("far")
	col_back, col_front = hexc("1f2737"), hexc("161b26")
	# Faint ember haze around the citadel (Art Bible: rare saturated red).
	for yy in range(40, 100):
		for x in range(330, 560):
			d = math.hypot((x - 445) / 115.0, (yy - 92) / 55.0)
			if d < 1.0 and (x + yy) % (2 if d < 0.55 else 4) == 0:
				c.put(x, yy, hexc("2a1c26") if d < 0.55 else hexc("231c27"))
	ridge = []
	y = 80
	for x in range(W):
		y += r.choice((-1, 0, 0, 1))
		y = max(52, min(104, y))
		ridge.append(y)
	# Make the seam continuous.
	for x in range(40):
		t = x / 40
		ridge[W - 40 + x] = int(ridge[W - 40 + x] * (1 - t) + ridge[0] * t)
	for x in range(W):
		for yy in range(ridge[x], H):
			c.put(x, yy, col_back)
	# Citadel silhouette.
	base_x, base_y = 410, 86
	towers = [(0, 30, 9), (12, 44, 7), (22, 58, 10), (36, 40, 8), (48, 26, 6), (58, 34, 9), (-12, 18, 7)]
	for dx, h, w in towers:
		x0 = base_x + dx
		for x in range(x0, x0 + w):
			for yy in range(base_y - h, H):
				c.put(x, yy, col_front)
		# Spire.
		for i in range((w + 1) // 2):
			for x in range(x0 + i, x0 + w - i):
				c.put(x, base_y - h - 1 - i * 2, col_front)
				c.put(x, base_y - h - 2 - i * 2, col_front)
		for wy in range(base_y - h + 6, base_y, 9):
			if r.random() < 0.55:
				c.put(x0 + w // 2, wy, EMBER[1] if r.random() < 0.7 else BLOOD[2])
	for x in range(base_x - 30, base_x + 90):
		for yy in range(base_y - 6, H):
			c.put(x, yy, col_front)
	# Front crag line.
	y = 112
	for x in range(W):
		y += r.choice((-1, 0, 0, 0, 1))
		y = max(100, min(124, y))
		for yy in range(y, H):
			c.put(x, yy, hexc("141a23"))
	return c


def _branch(c, x, y, angle, length, width, col, r, depth):
	"""Recursive gnarled branch, drawn as stepped pixel lines."""
	if depth == 0 or length < 2:
		return
	x1 = x + math.cos(angle) * length
	y1 = y + math.sin(angle) * length
	steps = int(length) + 1
	for i in range(steps + 1):
		t = i / steps
		px, py = x + (x1 - x) * t, y + (y1 - y) * t
		for w in range(width):
			c.put(int(px) + w, int(py), col)
	for _ in range(r.choice((1, 2, 2, 3))):
		_branch(c, x1, y1, angle + r.uniform(-0.75, 0.75), length * r.uniform(0.55, 0.75), max(1, width - 1), col, r, depth - 1)


def mid_layer():
	"""512x120 tiling: gnarled dead forest and a broken watchtower, blue-grey."""
	W, H = 512, 120
	c = Canvas(W, H)
	r = rng("mid")
	ground = hexc("1a212b")
	tree = hexc("1f2732")
	far_tree = hexc("1c2430")
	for x in range(W):
		for yy in range(98 + int(3 * math.sin(x / 37.0) + 2 * math.sin(x / 13.0)), H):
			c.put(x, yy, ground)
	# Broken watchtower.
	tx = 300
	for x in range(tx, tx + 18):
		top = 46 + (0 if x < tx + 11 else (x - tx - 10) * 3)
		for yy in range(top, 100):
			c.put(x, yy, tree)
	for x in range(tx - 2, tx + 12, 4):
		for yy in range(42, 46):
			c.put(x, yy, tree)
			c.put(x + 1, yy, tree)
	c.put(tx + 6, 60, EMBER[0])
	c.put(tx + 6, 61, EMBER[0])
	x = 6
	while x < W - 10:
		if tx - 14 < x < tx + 26:
			x += 8
			continue
		h = r.randint(30, 62)
		col = tree if r.random() < 0.6 else far_tree
		_branch(c, x, 100, -math.pi / 2 + r.uniform(-0.12, 0.12), h * 0.55, 3, col, r, 5)
		x += r.randint(22, 46)
	return c


def mist_layer():
	"""640x40 tiling haze band to soften the horizon (semi-transparent)."""
	c = Canvas(640, 40)
	for y in range(40):
		a = int(70 * math.sin(math.pi * y / 39))
		for x in range(640):
			if (x * 3 + y * 5) % 7 < 4 + int(2 * math.sin(x / 41.0)):
				c.put(x, y, MIST[0][:3] + (a,))
	return c


# ---------------------------------------------------------------- props
def _shade_rect(c, x0, y0, w, h, ramp, light_top=True):
	for y in range(y0, y0 + h):
		for x in range(x0, x0 + w):
			k = 2
			if y == y0 and light_top:
				k = 3
			elif x == x0:
				k = 3
			elif x == x0 + w - 1 or y == y0 + h - 1:
				k = 1
			c.put(x, y, ramp[k])


def house(ruined):
	"""72x84 timber-framed house. Origin = bottom-centre (36, 84)."""
	W, H = 72, 84
	c = Canvas(W, H)
	plaster = [hexc("2e2a2b"), hexc("4a4240"), hexc("625752"), hexc("7a6d63")]
	beam = [WOOD[0], WOOD[1], WOOD[2]]
	wall_top = 34
	# Wall body.
	for y in range(wall_top, H):
		for x in range(6, 66):
			c.put(x, y, plaster[2] if (x * 7 + y * 3) % 11 else plaster[1])
	for x in range(6, 66):
		c.put(x, H - 1, OUTLINE)
		c.put(x, wall_top, beam[1])
	# Timber frame: posts, rails and braces.
	for x in (6, 7, 34, 35, 64, 65):
		for y in range(wall_top, H):
			c.put(x, y, beam[0] if x in (6, 65) else beam[1])
	for y in (wall_top + 1, wall_top + 24):
		for x in range(6, 66):
			c.put(x, y, beam[1])
			c.put(x, y + 1, beam[0])
	for i in range(22):
		c.put(8 + i, wall_top + 2 + i, beam[1])
		c.put(63 - i, wall_top + 2 + i, beam[1])
	# Door with iron straps.
	for y in range(H - 28, H - 1):
		for x in range(27, 43):
			arch = y < H - 24 and abs(x - 34.5) > 6 - (H - 24 - y) * 2
			if not arch:
				c.put(x, y, WOOD[1] if x % 4 else WOOD[0])
	for y in (H - 22, H - 10):
		for x in range(27, 43):
			c.put(x, y, STEEL[0])
	c.put(40, H - 15, STEEL[3])
	# Windows: warm lamplight in the intact house, dark in the ruin.
	for wx in (13, 51):
		for y in range(wall_top + 6, wall_top + 18):
			for x in range(wx, wx + 9):
				edge = x in (wx, wx + 8) or y in (wall_top + 6, wall_top + 17)
				if edge:
					c.put(x, y, beam[0])
				elif ruined:
					c.put(x, y, SKY[0])
				else:
					c.put(x, y, EMBER[2] if (x + y) % 3 else EMBER[3])
		for y in range(wall_top + 7, wall_top + 17):
			c.put(wx + 4, y, beam[0])
	# Slate roof.
	roof = [hexc("1d1b22"), hexc("2c2932"), hexc("3d3944"), hexc("524d5a")]
	for y in range(0, wall_top + 1):
		half = int((y + 2) * 1.12)
		for x in range(36 - half, 36 + half):
			if 0 <= x < W:
				k = 2 if (y // 3) % 2 == 0 else 1
				if (x + (y // 3) * 3) % 6 == 0:
					k = 0
				c.put(x, y, roof[k])
		if 36 - half >= 0:
			c.put(36 - half, y, roof[3])
	for x in range(0, W):
		c.put(x, wall_top, roof[0])
		c.put(x, wall_top - 1, roof[3] if x % 2 else roof[2])
	# Chimney.
	for y in range(6, 18):
		for x in range(50, 56):
			c.put(x, y, STONE[2] if x < 55 else STONE[1])
	if ruined:
		# Caved-in roof: a hole and a fallen beam.
		r = rng("ruin")
		for y in range(8, 30):
			for x in range(30, 48):
				if (x - 39) ** 2 / 81 + (y - 19) ** 2 / 110 < 1 + r.uniform(-0.25, 0.25):
					c.put(x, y, SKY[1] if y < 24 else plaster[0])
		for i in range(30):
			for w in range(3):
				c.put(28 + i, 12 + int(i * 0.75) + w, WOOD[1] if w else WOOD[2])
	return c


def tree(alive, variant):
	"""56x92 tree. Origin = bottom-centre (28, 92)."""
	W, H = 56, 92
	c = Canvas(W, H)
	r = rng("tree", alive, variant)
	bark = [hexc("1c1a1f"), hexc("2a2629"), hexc("3a3433")]
	for y in range(30, H):
		w = 3 if y < 70 else 4 + (y - 70) // 7
		for x in range(28 - w // 2, 28 + w - w // 2):
			c.put(x, y, bark[2] if x == 28 - w // 2 else bark[1])
	if alive:
		leaves = [hexc("1a2422"), hexc("22302c"), hexc("2c3d36"), hexc("3a4d42")]
		blobs = [(28, 26, 18), (17, 36, 12), (39, 34, 13), (28, 12, 12), (20, 20, 10), (37, 20, 10)]
		for bx, by, br in blobs:
			for y in range(by - br, by + br):
				for x in range(bx - br, bx + br):
					d = math.hypot(x - bx, (y - by) * 1.15)
					if d < br - r.random() * 2:
						lit = (x - bx) + (y - by) < -br * 0.4
						k = 3 if lit and d < br - 3 else 2 if d < br - 2 else 1
						if (x * 5 + y * 3) % 13 == 0:
							k = 0
						c.put(x, y, leaves[k])
	else:
		_branch(c, 28, 40, -math.pi / 2, 18, 2, bark[1], r, 4)
		_branch(c, 28, 52, -math.pi / 2 - 0.9, 14, 2, bark[1], r, 3)
		_branch(c, 29, 48, -math.pi / 2 + 0.9, 14, 2, bark[1], r, 3)
	return c


def cart():
	"""56x26 broken cart with a loose wheel. Origin = bottom-centre (28, 26)."""
	c = Canvas(56, 26)
	for y in range(6, 15):
		for x in range(6, 44):
			k = 3 if y == 6 else (1 if y == 14 or x in (6, 43) else 2)
			if (x - 6) % 9 == 0 and y > 6:
				k = 1
			c.put(x, y, WOOD[k])
	for i in range(14):
		c.put(43 + i, 10 + i // 3, WOOD[2])
		c.put(43 + i, 11 + i // 3, WOOD[1])
	for (wx, wy) in ((13, 18), (36, 18)):
		for y in range(wy - 7, wy + 8):
			for x in range(wx - 7, wx + 8):
				d = math.hypot(x - wx, y - wy)
				if 5.2 < d <= 7.2:
					c.put(x, y, WOOD[0] if d > 6.4 else WOOD[2])
				elif d <= 1.5:
					c.put(x, y, STEEL[2])
				elif d <= 5.2 and (abs(x - wx) < 1 or abs(y - wy) < 1):
					c.put(x, y, WOOD[1])
	# Spilled sack and a crate.
	for y in range(19, 25):
		for x in range(0, 7):
			if (x - 3) ** 2 / 12 + (y - 22) ** 2 / 9 < 1:
				c.put(x, y, hexc("6a5a44") if y < 22 else hexc("4e4232"))
	return c


def signpost():
	"""44x40 signpost; text is drawn by the game. Origin = bottom-centre (22, 40)."""
	c = Canvas(44, 40)
	for y in range(6, 40):
		c.put(20, y, WOOD[1])
		c.put(21, y, WOOD[2])
		c.put(22, y, WOOD[1])
	for y in range(2, 13):
		for x in range(1, 43):
			edge = y in (2, 12) or x in (1, 42)
			c.put(x, y, WOOD[0] if edge else (WOOD[3] if y == 3 else WOOD[2]))
	# Arrow point on the right.
	for i in range(5):
		for y in range(3 + i, 12 - i):
			c.put(43 + i - 4, y, WOOD[2])
	return c


def banner():
	"""24x48 torn royal standard on a pole. Origin = pole base (2, 48)."""
	c = Canvas(24, 48)
	for y in range(0, 48):
		c.put(1, y, WOOD[2])
		c.put(2, y, WOOD[1])
	c.put(1, 0, GOLD[3])
	c.put(2, 0, GOLD[2])
	cloth = [hexc("2a0d14"), hexc("4a1420"), hexc("6a1c28")]
	for y in range(2, 30):
		right = 22 if y < 20 else 22 - (y - 20) * 2 + (3 if y % 4 < 2 else 0)
		for x in range(3, max(4, right)):
			k = 2 if x < 6 else (1 if (x + y // 2) % 7 else 0)
			c.put(x, y, cloth[k])
	# Tear and gold crown emblem.
	for y in range(12, 22):
		c.put(16 + (y - 12) // 3, y, None if False else cloth[0])
	for x, y in ((10, 9), (12, 8), (14, 9), (10, 10), (11, 10), (12, 10), (13, 10), (14, 10), (10, 11), (14, 11)):
		c.put(x, y, GOLD[2])
	return c


def blight_stalk(variant):
	"""16x44 blighted thorn stalk with a violet bud. Origin = bottom-centre (8, 44)."""
	c = Canvas(16, 44)
	r = rng("stalk", variant)
	h = 22 + variant * 8
	x = 8.0
	for i in range(h):
		y = 43 - i
		x += r.choice((-0.5, 0, 0, 0.5))
		c.put(int(x), y, CORRUPT[1])
		c.put(int(x) + 1, y, CORRUPT[0])
		if i % 6 == 3:
			d = r.choice((-1, 1))
			c.put(int(x) + (2 if d > 0 else -1), y - 1, CORRUPT[2])
			c.put(int(x) + (3 if d > 0 else -2), y - 2, CORRUPT[3])
	top = 43 - h
	for dy in range(-2, 2):
		for dx in range(-1, 3):
			c.put(int(x) + dx, top + dy, CORRUPT[2])
	c.put(int(x), top - 1, CORRUPT[4])
	c.put(int(x) + 1, top - 2, CORRUPT[4])
	return c


def far_tower(variant):
	"""60x168 dark tower silhouette for the fortress near the exit. Origin = bottom-left."""
	c = Canvas(60, 168)
	r = rng("tower", variant)
	body = hexc("161b25")
	edge = hexc("1d2430")
	top = 18 + variant * 10
	for y in range(top, 168):
		for x in range(4, 56):
			c.put(x, y, edge if x in (4, 5) else body)
	for x in range(2, 58, 8):
		for y in range(top - 8, top):
			for xx in range(x, x + 5):
				c.put(xx, y, body)
	for wy in range(top + 14, 150, 22):
		for wx in (16, 38):
			if r.random() < 0.5:
				for y in range(wy, wy + 6):
					c.put(wx, y, EMBER[0] if y < wy + 2 else hexc("4a2418"))
					c.put(wx + 1, y, hexc("4a2418"))
	return c


def ribbon_spear():
	"""28x44 spear stuck in the ground with the princess's ribbon. Origin = (6, 44)."""
	c = Canvas(28, 44)
	for y in range(8, 44):
		c.put(5, y, WOOD[2])
		c.put(6, y, WOOD[1])
	for i, w in enumerate((1, 1, 2, 3, 3, 2, 2)):
		for x in range(6 - w // 2 - 1, 6 + (w + 1) // 2):
			c.put(x, 1 + i, STEEL[4] if x < 6 else STEEL[2])
	rib = [hexc("8a5a68"), hexc("c38d9e"), hexc("e6b8c4")]
	pts = [(7, 14), (10, 15), (13, 15), (16, 17), (19, 18), (21, 21), (23, 23), (24, 26)]
	for (x, y) in pts:
		c.put(x, y, rib[2])
		c.put(x, y + 1, rib[1])
		c.put(x, y + 2, rib[0])
	return c


PROPS = {
	"prop_house": lambda: house(False), "prop_house_ruined": lambda: house(True),
	"prop_tree_a": lambda: tree(True, 0), "prop_tree_b": lambda: tree(True, 1),
	"prop_tree_dead_a": lambda: tree(False, 0), "prop_tree_dead_b": lambda: tree(False, 1),
	"prop_cart": cart, "prop_signpost": signpost, "prop_banner": banner,
	"prop_blight_a": lambda: blight_stalk(0), "prop_blight_b": lambda: blight_stalk(1), "prop_blight_c": lambda: blight_stalk(2),
	"prop_far_tower_a": lambda: far_tower(0), "prop_far_tower_b": lambda: far_tower(1),
	"prop_ribbon_spear": ribbon_spear,
}


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	tiles, tufts = build_tiles()
	save_png(tiles, os.path.join(OUT, "terrain_stone.png"))
	save_png(tufts, os.path.join(OUT, "terrain_tufts.png"))
	layers = {"bg_sky": sky(), "bg_far": far_layer(), "bg_mid": mid_layer(), "bg_mist": mist_layer()}
	for name, layer in layers.items():
		save_png(layer, os.path.join(OUT, name + ".png"))
	built = {name: make() for name, make in PROPS.items()}
	for name, prop in built.items():
		save_png(prop, os.path.join(OUT, name + ".png"))
	if preview:
		save_png(tiles, os.path.join(preview, "tiles_x4.png"), 4, (52, 60, 66, 255))
		# A small authored-looking chunk: two-tile ledge, step, floating platform.
		demo = Canvas(160, 80)
		solid = set()
		for x in range(10):
			for y in range(3, 5):
				solid.add((x, y))
		for x in range(6, 10):
			solid.add((x, 2))
		for x in range(1, 4):
			solid.add((x, 0))
		for x in range(10):
			solid.add((x, 4))
		for theme_split in (5,):
			for (x, y) in solid:
				theme = "village" if x < theme_split else "corrupt"
				mask = (1 if (x, y - 1) not in solid else 0) | (2 if (x + 1, y) not in solid else 0) | (4 if (x, y + 1) not in solid else 0) | (8 if (x - 1, y) not in solid else 0)
				demo.blit(terrain_tile(theme, (x * 7 + y * 3) % 3, mask), x * 16, y * 16 + 8)
			for (x, y) in solid:
				if (x, y - 1) not in solid:
					theme = "village" if x < theme_split else "corrupt"
					demo.blit(tuft_overlay(theme, x % 3), x * 16, y * 16 + 8 - 6)
		save_png(demo, os.path.join(preview, "terrain_demo_x4.png"), 4, (33, 42, 55, 255))
		save_png(layers["bg_sky"], os.path.join(preview, "sky_x2.png"), 2)
		comp = layers["bg_sky"].copy()
		comp.blit(layers["bg_far"], 0, 120)
		comp.blit(layers["bg_mist"], 0, 200)
		comp.blit(layers["bg_mid"], 0, 170)
		comp.blit(layers["bg_mid"], 512, 170)
		save_png(comp, os.path.join(preview, "backdrop_x2.png"), 2)
		strip = Canvas(sum(p.w + 4 for p in built.values()), 170)
		x = 0
		for p in built.values():
			strip.blit(p, x, 170 - p.h)
			x += p.w + 4
		save_png(strip, os.path.join(preview, "props_x3.png"), 3, (33, 42, 55, 255))
	print("tiles", tiles.w, tiles.h, "tufts", tufts.w, tufts.h)


if __name__ == "__main__":
	main()

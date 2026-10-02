"""Narrative props of the slice, enriched in RUN-029: houses, trees, dead trees,
cart, signpost, blight stalks, far towers, torn standard and the ribbon spear.

Footprints and anchors are unchanged from RUN-013 (see each docstring); only the
material detail changes: timber grain, plaster cracks and stains, shingles with
moss, framed and shuttered windows, foliage built from 3-4 tone masses, bark,
spokes, iron bands. All remain decor behind gameplay: darker and less saturated
than enemies, player and hazards.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, hexc  # noqa: E402
from palette import BLOOD, CORRUPT, EMBER, GOLD, MOSS, OUTLINE, SKY, STEEL, STONE, WOOD  # noqa: E402
from world_props import masonry_rect, mix  # noqa: E402

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def rng(*seed):
	return random.Random("-".join(map(str, seed)))


def dith(t, x, y):
	return t * 16 > BAYER[y % 4][x % 4] + 0.5


def _hash(x, y, salt=0):
	return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xFFFF


def thick_line(c, x0, y0, x1, y1, w0, w1, cols):
	"""Tapered pixel line; cols = (shadow, body, highlight). Highlight on the left edge."""
	steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
	for i in range(steps + 1):
		t = i / steps
		x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
		w = max(1, int(round(w0 + (w1 - w0) * t)))
		xi, yi = int(round(x)) - w // 2, int(round(y))
		for k in range(w):
			col = cols[2] if k == 0 and w > 2 else cols[0] if k == w - 1 and w > 1 else cols[1]
			if (i + k) % 5 == 3 and w > 2:
				col = cols[0]
			c.put(xi + k, yi, col)


# ------------------------------------------------------------------ houses
def house(ruined):
	"""72x84 timber-framed house. Origin = bottom-centre (36, 84)."""
	W, H = 72, 84
	c = Canvas(W, H)
	r = rng("house2", ruined)
	plaster = [hexc("2a2627"), hexc("3f3836"), hexc("5a504b"), hexc("72665c"), hexc("86796d")]
	beam = [WOOD[0], WOOD[1], WOOD[2], WOOD[3]]
	wall_top = 34
	found_top = H - 10
	# Plaster wall with grain noise, grime near the ground and lit upper area.
	for y in range(wall_top, H):
		for x in range(6, 66):
			k = 2
			h = _hash(x, y, 5)
			if h % 7 == 0:
				k = 1
			elif h % 13 == 0:
				k = 3
			if y > H - 20 and dith((y - (H - 20)) / 12.0, x, y):
				k = max(0, k - 1)
			c.put(x, y, plaster[k])
	# Plaster cracks and a patch where the plaster fell to reveal brick.
	for _ in range(4 if ruined else 2):
		x, y = r.randint(10, 60), r.randint(wall_top + 4, H - 22)
		for i in range(r.randint(5, 10)):
			c.put(x, y + i, plaster[0])
			x += r.choice((-1, 0, 0, 1))
	px, py = (46, wall_top + 24) if not ruined else (12, wall_top + 22)
	for yy in range(py, py + 8):
		for xx in range(px, px + 11):
			if (xx - px - 5) ** 2 / 36.0 + (yy - py - 3.5) ** 2 / 16.0 < 1:
				brick = (yy - py) % 3 == 2 or (xx + (yy - py) // 3 * 3) % 6 == 0
				c.put(xx, yy, hexc("3a2c2a") if brick else hexc("62463c"))
	# Stone foundation.
	masonry_rect(c, 4, found_top, 64, 10, STONE, rng("found", ruined), course=5, moss=MOSS)
	for x in range(4, 68):
		c.put(x, found_top, STONE[4])
		c.put(x, H - 1, OUTLINE)
	# Timber frame: posts, rails, braces with grain.
	def timber(x, y, vertical):
		c.put(x, y, beam[2] if (x if vertical else y) % 3 else beam[1])
	for x in (6, 7, 8, 33, 34, 35, 63, 64, 65):
		for y in range(wall_top, found_top):
			col = beam[0] if x in (6, 33, 63) else beam[2] if x in (8, 35, 65) else beam[1]
			if (y + x) % 9 == 0:
				col = beam[0]
			c.put(x, y, col)
	for y in (wall_top + 1, wall_top + 24):
		for x in range(6, 66):
			c.put(x, y, beam[3] if x % 11 else beam[2])
			c.put(x, y + 1, beam[1] if x % 7 else beam[0])
			c.put(x, y + 2, beam[0])
	for i in range(22):
		for dx in (0, 1):
			c.put(10 + i + dx, wall_top + 3 + i, beam[1] if (i + dx) % 4 else beam[0])
			c.put(61 - i - dx, wall_top + 3 + i, beam[1] if (i + dx) % 4 else beam[0])
	for x, y in ((7, wall_top + 12), (34, wall_top + 12), (64, wall_top + 12), (7, wall_top + 36), (34, wall_top + 36), (64, wall_top + 36)):
		c.put(x, y, STEEL[1])  # iron pegs
	# Door: planks, iron straps, ring handle, stone lintel.
	for y in range(H - 38, H - 10):
		for x in range(27, 43):
			arch = y < H - 34 and abs(x - 34.5) > 6 - (H - 34 - y) * 2
			if arch:
				continue
			col = WOOD[1] if (x - 27) % 4 else WOOD[0]
			if (x - 27) % 4 == 1:
				col = WOOD[2]
			c.put(x, y, col)
	for y in (H - 32, H - 20):
		for x in range(27, 43):
			c.put(x, y, STEEL[0])
			c.put(x, y + 1, STEEL[1] if x % 4 else STEEL[2])
	for x in range(25, 45):
		c.put(x, H - 40, STONE[4] if x % 3 else STONE[3])
		c.put(x, H - 39, STONE[2])
	for y in range(H - 38, H - 10):
		c.put(26, y, STONE[2])
		c.put(43, y, STONE[1])
	c.put(40, H - 24, STEEL[3])
	c.put(40, H - 23, STEEL[1])
	for x in range(24, 46):  # worn doorstep
		c.put(x, H - 10, STONE[4])
	# Windows: frame, shutters, mullion, pane glow.
	for wx in (13, 51):
		y0 = wall_top + 6
		for y in range(y0, y0 + 12):
			for x in range(wx, wx + 9):
				edge = x in (wx, wx + 8) or y in (y0, y0 + 11)
				if edge:
					c.put(x, y, beam[0])
				elif ruined:
					c.put(x, y, SKY[0] if (x + y) % 5 else SKY[1])
				else:
					d = abs(x - (wx + 4)) + abs(y - (y0 + 6)) * 0.7
					c.put(x, y, EMBER[3] if d < 2 else EMBER[2] if d < 4.5 else EMBER[1])
		for y in range(y0 + 1, y0 + 11):
			c.put(wx + 4, y, beam[0])
		for x in range(wx + 1, wx + 8):
			c.put(x, y0 + 6, beam[0])
		for x in range(wx - 1, wx + 10):  # sill
			c.put(x, y0 + 12, STONE[4])
			c.put(x, y0 + 13, STONE[1])
		for sx, side in ((wx - 3, -1), (wx + 9, 1)):  # shutters
			broken = ruined and (wx == 13 or side == 1)
			for y in range(y0, y0 + 12 - (3 if broken and side == 1 else 0)):
				for k in range(3):
					off = (y - y0) // 4 if broken and side == 1 else 0
					c.put(sx + k + off, y, WOOD[2] if k == 0 else WOOD[1] if k == 1 else WOOD[0])
			for y in (y0 + 3, y0 + 8):
				if not broken:
					for k in range(3):
						c.put(sx + k, y, STEEL[0])
		if not ruined:
			for x in range(wx, wx + 9):  # tiny flower box
				c.put(x, y0 + 14, WOOD[1])
			for x in range(wx + 1, wx + 8, 2):
				c.put(x, y0 + 13, MOSS[2])
	# Slate roof: shingle courses with offsets, per-shingle tones, moss.
	roof = [hexc("1a1920"), hexc("272530"), hexc("373440"), hexc("4a4655"), hexc("5e5a6a")]
	rr = rng("roof", ruined)
	for y in range(0, wall_top + 1):
		half = int((y + 2) * 1.12)
		course = y // 3
		for x in range(36 - half, 36 + half):
			if not 0 <= x < W:
				continue
			sx = (x + course * 3) // 6
			tone = 2 if _hash(sx, course, 8) % 3 else 3 if _hash(sx, course, 9) % 2 else 1
			k = tone
			if y % 3 == 2:
				k = 0 if (x + course * 3) % 6 in (0, 1, 3) else 1
			elif y % 3 == 0:
				k = min(4, tone + 1) if (x + course * 3) % 6 else 0
			if (x + course * 3) % 6 == 0:
				k = 0
			c.put(x, y, roof[k])
		if 36 - half >= 0:
			c.put(36 - half, y, roof[4])
			c.put(36 - half + 1, y, roof[3])
		if 36 + half - 1 < W:
			c.put(36 + half - 1, y, roof[0])
	for _ in range(7):  # moss patches on the slates
		mx, my = rr.randint(14, 58), rr.randint(14, wall_top - 4)
		for i in range(rr.randint(3, 6)):
			for j in range(rr.randint(1, 2)):
				if c.get(mx + i, my + j) is not None and abs(mx + i - 36) < (my + j + 2) * 1.12 - 1:
					c.put(mx + i, my + j, MOSS[1] if dith(0.6, mx + i, my + j) else MOSS[0])
	for x in range(0, W):  # eaves with shadow beneath
		c.put(x, wall_top, roof[0])
		c.put(x, wall_top - 1, roof[4] if x % 2 else roof[3])
		c.put(x, wall_top + 1, plaster[0] if x % 2 else plaster[1])
	# Chimney with brick courses.
	for y in range(6, 20):
		for x in range(49, 57):
			brick = y % 3 == 0 or (x + (y // 3) * 2) % 4 == 0
			c.put(x, y, STONE[1] if brick else STONE[3] if x < 54 else STONE[2])
	for x in range(48, 58):
		c.put(x, 5, STONE[4])
		c.put(x, 6, STONE[1])
	if ruined:
		# Caved-in roof: ragged hole, bare rafters, fallen beam and missing shingles.
		for y in range(8, 30):
			for x in range(30, 48):
				if (x - 39) ** 2 / 81 + (y - 19) ** 2 / 110 < 1 + rr.uniform(-0.25, 0.25):
					c.put(x, y, SKY[1] if y < 24 else plaster[0])
		for x in range(31, 48, 4):  # rafters across the hole
			for y in range(10, 26):
				if c.get(x, y) in (SKY[1], plaster[0]):
					c.put(x, y, beam[1])
		for i in range(30):
			for w in range(3):
				c.put(28 + i, 12 + int(i * 0.75) + w, beam[1] if w else beam[2])
		for _ in range(18):  # missing shingles
			mx, my = rr.randint(18, 56), rr.randint(6, 30)
			if c.get(mx, my) in roof:
				c.put(mx, my, roof[0])
				c.put(mx + 1, my, roof[0])
	else:
		# Smoke-stained chimney top and a warm lamp hung by the door.
		c.put(52, 4, STONE[0])
		c.put(53, 4, STONE[0])
		for y in range(H - 38, H - 33):
			c.put(47, y, STEEL[0])
		for y in range(H - 33, H - 28):
			for x in range(46, 50):
				c.put(x, y, STEEL[0] if x in (46, 49) or y in (H - 33, H - 29) else EMBER[2])
		c.put(47, H - 31, EMBER[3])
	return c


# ------------------------------------------------------------------ trees
def leaf_mass(c, cx, cy, rx, ry, ramp, r, shift=0):
	"""One foliage mass: scalloped edge, light from the upper left, dithered tone steps."""
	ph = r.uniform(0, 6.28)
	for y in range(int(cy - ry - 2), int(cy + ry + 3)):
		for x in range(int(cx - rx - 2), int(cx + rx + 3)):
			dx, dy = (x - cx) / rx, (y - cy) / ry
			ang = math.atan2(dy, dx)
			lim = 1.0 + 0.1 * math.sin(ang * 6 + ph) + 0.06 * math.sin(ang * 11)
			d = math.hypot(dx, dy)
			if d > lim:
				continue
			light = -0.55 * dx - 0.7 * dy + (0.35 - d) * 0.8
			k = 3 if light > 0.45 else 2 if light > 0.0 else 1 if light > -0.4 else 0
			if abs(light - 0.45) < 0.08 and dith(0.5, x, y):
				k = min(3, k + 1)
			elif abs(light) < 0.08 and dith(0.5, x, y):
				k = min(3, k + 1)
			if _hash(x, y, 4) % 11 == 0:
				k = max(0, k - 1)
			k = max(0, min(3, k - shift))
			c.put(x, y, ramp[k])


def tree(alive, variant):
	"""56x92 tree. Origin = bottom-centre (28, 92)."""
	W, H = 56, 92
	c = Canvas(W, H)
	r = rng("tree2", alive, variant)
	bark = [hexc("14121a"), hexc("221f24"), hexc("322d2e"), hexc("453e3b")]
	trunk_w = 4 if alive else 5
	if alive:
		# Trunk with roots, bark furrows, a knot and moss on the shaded side.
		for y in range(34, H):
			w = trunk_w if y < 76 else trunk_w + (y - 76) // 3
			x0 = 28 - w // 2 + (1 if variant else 0) * ((y // 10) % 2 == 0)
			for k in range(w):
				col = bark[3] if k == 0 else bark[0] if k == w - 1 else bark[2] if (y // 4 + k) % 3 else bark[1]
				c.put(x0 + k, y, col)
			if y > 70 and (y % 4 == 0):
				c.put(x0 + w, y, bark[0])
		for y in range(80, 92):
			c.put(22 + (y - 80) // 4 * -1 + 2, y, bark[1])
			c.put(34 - (y - 80) // 4 * -1 - 2, y, bark[1])
		for y in range(58, 72):
			if y % 2 == 0:
				c.put(31, y, MOSS[0])
		c.put(27, 60, bark[0])
		c.put(28, 60, bark[0])
		thick_line(c, 28, 44, 17, 30, 3, 1, (bark[0], bark[1], bark[3]))
		thick_line(c, 28, 42, 40, 28, 3, 1, (bark[0], bark[1], bark[3]))
		leaves = [hexc("131c1b"), hexc("1d2a27"), hexc("2a3b34"), hexc("3a4f43")]
		masses = [(28, 14, 11, 9, 1), (18, 22, 11, 9, 1), (38, 22, 11, 9, 1), (13, 33, 9, 7, 1), (43, 33, 9, 7, 1),
			(28, 26, 15, 11, 0), (20, 15, 8, 7, 0), (36, 15, 8, 7, 0), (24, 36, 9, 6, 0), (34, 36, 8, 6, 0)]
		if variant:
			masses = [(x + (2 if i % 2 else -1), y + (1 if i % 3 == 0 else 0), a, b, s) for i, (x, y, a, b, s) in enumerate(masses)]
		for cx, cy, rx, ry, shift in masses:
			leaf_mass(c, cx, cy, rx, ry, leaves, r, shift)
		for _ in range(14):  # gaps and hanging leaves at the canopy edge
			x, y = r.randint(8, 48), r.randint(36, 42)
			if c.get(x, y) is not None and c.get(x, y + 1) is None:
				c.put(x, y + 1, leaves[1])
				if r.random() < 0.4:
					c.put(x, y + 2, leaves[0])
	else:
		_dead_tree(c, r, variant, bark)
	return c


def _dead_tree(c, r, variant, bark):
	"""Gnarled leafless tree with tapering branches, bark, knot hole and moss."""
	cols = (bark[0], bark[1], bark[3])
	sway = 1 if variant else -1
	x = 28.0
	pts = []
	for y in range(91, 36, -1):
		x += r.choice((0, 0, 0, 0.35 * sway, -0.2 * sway))
		pts.append((int(round(x)), y))
	for i, (px, py) in enumerate(pts):
		w = 6 if i < 14 else 5 if i < 30 else 3
		w += 3 if i < 6 else 0
		for k in range(w):
			xx = px - w // 2 + k
			col = bark[3] if k == 0 else bark[0] if k == w - 1 else bark[2] if (py // 3 + k) % 4 else bark[1]
			c.put(xx, py, col)
	for y in range(84, 92):  # root flare
		c.put(pts[91 - y][0] - 6 + (y - 84) // 3, y, bark[1])
		c.put(pts[91 - y][0] + 6 - (y - 84) // 3, y, bark[1])
	kx, ky = pts[30]
	c.put(kx, ky, bark[0])
	c.put(kx + 1, ky, bark[0])
	c.put(kx, ky + 1, bark[0])
	for i in range(8, 36, 3):
		c.put(pts[i][0] + 2, pts[i][1], MOSS[0])
	top = pts[-1]

	def twig(x0, y0, ang, length, width, depth):
		x1, y1 = x0 + math.cos(ang) * length, y0 + math.sin(ang) * length
		thick_line(c, x0, y0, x1, y1, width, max(1, width - 1), cols)
		if depth <= 0 or length < 4:
			return
		for da in (-0.6, 0.45):
			twig(x1, y1, ang + da + r.uniform(-0.2, 0.2), length * r.uniform(0.6, 0.75), max(1, width - 1), depth - 1)
		if r.random() < 0.5:
			twig(x1, y1, ang + r.uniform(-0.2, 0.2), length * 0.5, 1, depth - 1)

	twig(top[0], top[1], -math.pi / 2 + 0.3 * sway, 14, 3, 4)
	twig(top[0], top[1] + 2, -math.pi / 2 - 0.9 * sway, 13, 2, 3)
	twig(pts[25][0], pts[25][1], -math.pi / 2 + 1.0 * sway, 15, 3, 3)
	twig(pts[40][0], pts[40][1], -math.pi / 2 - 1.15 * sway, 12, 2, 3)
	for _ in range(5):  # hanging tatters of dead leaves / lichen
		x, y = r.randint(10, 46), r.randint(14, 40)
		if c.get(x, y) is not None and c.get(x, y + 1) is None:
			c.put(x, y + 1, MOSS[0])


# ------------------------------------------------------------------ cart
def cart():
	"""56x26 broken cart with a loose wheel. Origin = bottom-centre (28, 26)."""
	c = Canvas(56, 26)
	r = rng("cart2")
	for x in range(2, 50):  # ground shadow
		if (x + 1) % 2:
			c.put(x, 25, hexc("17131b"))
	# Bed: planks with grain, gaps, nails and a cracked board.
	for y in range(6, 15):
		for x in range(6, 44):
			plank = (y - 6) // 3
			k = 2
			if (y - 6) % 3 == 0:
				k = 3 if y == 6 else 1
			elif (x + plank * 7) % 11 == 0:
				k = 1
			elif (x * 3 + y) % 17 == 0:
				k = 1
			if x in (6, 43):
				k = 0
			if y == 14:
				k = 0
			c.put(x, y, WOOD[k])
	for x in range(6, 44, 9):
		for y in (7, 11):
			c.put(x, y, STEEL[2])
	for y in range(6, 15):
		c.put(24 + (y - 6) // 3, y, WOOD[0])  # crack
	for x in range(6, 44):  # iron band
		c.put(x, 9, STEEL[0])
	# Broken shaft.
	for i in range(14):
		c.put(43 + i, 10 + i // 3, WOOD[2])
		c.put(43 + i, 11 + i // 3, WOOD[1])
	c.put(56 - 1, 14, WOOD[0])
	# Wheels: rim, iron band, 8 spokes (one broken), hub and bolts.
	for (wx, wy, broken) in ((13, 18, False), (36, 18, True)):
		for y in range(wy - 8, wy + 8):
			for x in range(wx - 8, wx + 8):
				d = math.hypot(x - wx, y - wy)
				if 5.4 < d <= 7.4:
					c.put(x, y, WOOD[0] if d > 6.6 else WOOD[2])
				elif 7.4 < d <= 8.0 and (x + y) % 2 == 0:
					c.put(x, y, STEEL[0])
				elif d <= 2.0:
					c.put(x, y, STEEL[2] if d > 1 else STEEL[3])
		for i in range(8):
			if broken and i in (2, 3):
				continue
			a = i * math.pi / 4
			for t in range(2, 6):
				c.put(int(round(wx + math.cos(a) * t)), int(round(wy + math.sin(a) * t)), WOOD[1] if i % 2 else WOOD[2])
		if broken:
			for x in range(wx + 4, wx + 8):  # snapped rim piece
				c.px[(wy - 5) * 56 + x] = None
	# Spilled cargo: sack with a tie, apples-like pale spots dim, and a barrel stave.
	for y in range(18, 25):
		for x in range(0, 9):
			if (x - 4) ** 2 / 17 + (y - 21.5) ** 2 / 11 < 1:
				k = hexc("7a6a50") if (x + y) % 3 and y < 22 else hexc("5a4c38") if y < 23 else hexc("40362a")
				c.put(x, y, k)
	c.put(4, 18, hexc("40362a"))
	c.put(5, 18, hexc("40362a"))
	for i in range(3):
		c.put(46 + i * 2, 24, WOOD[2])
		c.put(46 + i * 2, 23, WOOD[1])
	return c


# ------------------------------------------------------------------ signpost
def signpost():
	"""44x40 signpost; text is drawn by the game on the board (x 1..42, y 2..12).
	Board interior stays nearly flat so the pale text remains readable."""
	c = Canvas(44, 40)
	r = rng("sign2")
	for y in range(6, 40):
		c.put(19, y, WOOD[0])
		c.put(20, y, WOOD[2] if y % 4 else WOOD[3])
		c.put(21, y, WOOD[1])
		c.put(22, y, WOOD[0] if y % 3 else WOOD[1])
	for y in range(34, 40):  # mossy stones at the foot
		for x in range(15, 27):
			if abs(x - 21) < 6 - (y - 34) // 2 + 2 and not (x in range(19, 23) and y < 36):
				c.put(x, y, STONE[2] if (x + y) % 3 else STONE[3])
	for x in range(15, 27):
		if c.get(x, 38) is not None:
			c.put(x, 38, MOSS[1])
	for y in range(2, 13):
		for x in range(1, 43):
			edge = y in (2, 12) or x in (1, 42)
			k = WOOD[0] if edge else (WOOD[3] if y == 3 else WOOD[2])
			if not edge and y > 3 and (x * 5 + y * 11) % 23 == 0:
				k = WOOD[1]  # sparse subtle grain
			c.put(x, y, k)
	for y in range(3, 12):  # worn right arrow point
		c.put(42, y, WOOD[1])
	for i in range(5):
		for y in range(3 + i, 12 - i):
			c.put(43 + i - 4, y, WOOD[2] if y > 3 + i else WOOD[3])
	for x, y in ((3, 4), (3, 10), (39, 4), (39, 10)):
		c.put(x, y, STEEL[2])
	for x in range(3, 42):  # dark underside shadow of the board
		c.put(x, 13, hexc("17131b") if x % 2 else None)
	for y in range(13, 18):  # frayed rope loop
		c.put(10 + (y % 2), y, hexc("7a6a4a"))
	return c


# ------------------------------------------------------------------ banner
def banner():
	"""24x48 torn royal standard on a pole. Origin = pole base (2, 48)."""
	c = Canvas(24, 48)
	for y in range(0, 48):
		c.put(1, y, WOOD[3] if y % 5 else WOOD[2])
		c.put(2, y, WOOD[1])
		c.put(0, y, WOOD[0] if y % 7 == 0 else None)
	for x in range(0, 4):  # finial
		c.put(x, 0, GOLD[1])
	c.put(1, 0, GOLD[3])
	c.put(2, 0, GOLD[2])
	cloth = [hexc("22090f"), hexc("3c1219"), hexc("56202a"), hexc("6e2c35")]
	r = rng("banner2")
	for y in range(2, 32):
		right = 22 if y < 20 else 22 - (y - 20) * 2 + (3 if y % 4 < 2 else 0)
		for x in range(3, max(4, right)):
			fold = (x + y // 6) % 6
			k = 3 if fold == 0 else 2 if fold in (1, 2) else 1 if fold in (3, 4) else 0
			if y in (2, 3):
				k = 0  # hem on the pole
			if x == 3 or (right > 5 and x == right - 1):
				k = 0
			c.put(x, y, cloth[k])
	for x in range(5, 20):  # stitched border
		if c.get(x, 5) is not None:
			c.put(x, 5, hexc("8a6a3a") if x % 2 else cloth[0])
	for y in range(12, 24):  # tear
		for x in range(16 + (y - 12) // 3, 20 + (y - 12) // 3):
			c.px[y * 24 + x] = None
	for x, y in ((10, 9), (12, 8), (14, 9), (10, 10), (11, 10), (12, 10), (13, 10), (14, 10), (10, 11), (14, 11), (12, 12), (12, 13), (11, 13), (13, 13)):
		c.put(x, y, hexc("a8884e") if y < 10 else hexc("8a6a3a"))
	for x in range(4, 14, 3):  # loose threads at the lower edge
		for yy in range(30, 30 + r.randint(1, 3)):
			if c.get(x, yy - 1) is not None and x < 12:
				c.put(x, yy, cloth[0])
	return c


# ------------------------------------------------------------------ blight
def blight_stalk(variant):
	"""16x44 blighted thorn stalk with a violet bud. Origin = bottom-centre (8, 44)."""
	c = Canvas(16, 44)
	r = rng("stalk2", variant)
	h = 22 + variant * 8
	x = 8.0
	for dx in (-4, -3, 3, 4):  # spreading roots
		c.put(8 + dx, 43, CORRUPT[1])
		c.put(8 + dx // 2, 42, CORRUPT[0])
	for i in range(h):
		y = 43 - i
		x += r.choice((-0.5, 0, 0, 0.5))
		wdt = 3 if i < 6 else 2
		for k in range(wdt):
			c.put(int(x) + k - (1 if wdt == 3 else 0), y, CORRUPT[2] if k == 0 else CORRUPT[0] if k == wdt - 1 else CORRUPT[1])
		if i % 5 == 3:
			d = r.choice((-1, 1))
			for t in range(3):
				c.put(int(x) + d * (2 + t), y - t, CORRUPT[2] if t < 2 else CORRUPT[3])
			c.put(int(x) + d * 2, y + 1, CORRUPT[0])
		if i % 7 == 5:  # small curled leaf
			d = r.choice((-1, 1))
			c.put(int(x) + d * 2, y, CORRUPT[1])
			c.put(int(x) + d * 3, y - 1, CORRUPT[2])
			c.put(int(x) + d * 3, y, CORRUPT[0])
	top = 43 - h
	cx = int(x)
	for dy in range(-3, 2):
		for dx in range(-2, 3):
			if abs(dx) + abs(dy + 1) <= 3:
				col = CORRUPT[3] if (dx < 0 and dy < 0) else CORRUPT[2] if dy < 1 else CORRUPT[1]
				c.put(cx + dx, top + dy, col)
	for dx in (-3, 3):  # petals
		c.put(cx + dx, top - 1, CORRUPT[1])
		c.put(cx + dx, top - 2, CORRUPT[2])
	c.put(cx, top - 1, CORRUPT[4])
	c.put(cx + 1, top - 2, CORRUPT[4])
	c.put(cx, top - 3, CORRUPT[3])
	return c


# ------------------------------------------------------------------ far towers
def far_tower(variant):
	"""60x168 dark tower silhouette for the fortress near the exit. Origin = bottom-left."""
	c = Canvas(60, 168)
	r = rng("tower2", variant)
	body, edge, hi, lo = hexc("161b25"), hexc("1d2430"), hexc("1f2634"), hexc("11151d")
	top = 18 + variant * 10
	for y in range(top, 168):
		for x in range(4, 56):
			col = body
			if (y - top) % 8 == 0 and 5 < x < 55:
				col = hi if (x + y) % 3 else body  # faint course lines
			elif (_hash(x // 6 + ((y - top) // 8) % 2 * 3, (y - top) // 8, 3)) % 9 == 0 and (y - top) % 8 == 4:
				col = lo
			if x in (4, 5):
				col = edge
			elif x == 55:
				col = lo
			c.put(x, y, col)
	for y in range(top + 20, 168):  # corner buttresses
		c.put(2, y, body)
		c.put(3, y, body)
		c.put(56, y, lo)
		c.put(57, y, lo)
	for x in range(0, 60):  # corbel band under the parapet
		c.put(x, top, edge)
		c.put(x, top + 1, lo)
		if x % 4 == 0:
			c.put(x, top + 2, lo)
	for x in range(2, 58, 8):  # crenellations, one broken
		hgt = 8 if not (variant == 1 and x == 26) else 3
		for y in range(top - hgt, top):
			for xx in range(x, x + 5):
				c.put(xx, y, body if xx > x else edge)
	for wy in range(top + 14, 150, 22):  # arrow slits and lit windows
		for wx in (16, 38):
			if r.random() < 0.6:
				for y in range(wy, wy + 7):
					c.put(wx, y, lo)
					c.put(wx + 1, y, lo)
				if r.random() < 0.55:
					c.put(wx, wy + 2, EMBER[0])
					c.put(wx, wy + 3, hexc("4a2418"))
			else:
				for y in range(wy, wy + 6):
					c.put(wx, y, lo)
	for i in range(8):  # ivy at the base
		for y in range(150 + (i * 5) % 9, 168):
			if _hash(i, y, 2) % 3:
				c.put(6 + i * 6 + (y % 2), y, hexc("17211c"))
	return c


# ------------------------------------------------------------------ ribbon spear
def ribbon_spear():
	"""28x44 spear stuck in the ground with the princess's ribbon. Origin = (6, 44)."""
	c = Canvas(28, 44)
	for y in range(8, 44):  # shaft with grain and leather wrap
		c.put(4, y, WOOD[3] if y % 4 else WOOD[2])
		c.put(5, y, WOOD[2])
		c.put(6, y, WOOD[1])
		c.put(7, y, WOOD[0] if y % 3 else WOOD[1])
	for y in range(16, 22):
		c.put(5, y, hexc("5a4030") if y % 2 else hexc("3a2a22"))
		c.put(6, y, hexc("3a2a22"))
	for i, w in enumerate((1, 1, 2, 3, 4, 4, 3, 3)):  # blade with fuller
		for x in range(6 - w // 2 - 1, 6 + (w + 1) // 2):
			c.put(x, 0 + i, STEEL[4] if x < 6 - w // 2 + 1 else STEEL[2])
	for y in range(3, 8):
		c.put(5, y, STEEL[1])
	for x in range(3, 9):  # socket bands
		c.put(x, 8, STEEL[1])
		c.put(x, 9, STEEL[3] if x < 6 else STEEL[0])
	rib = [hexc("6a3f4e"), hexc("8a5a68"), hexc("c38d9e"), hexc("e6b8c4")]
	pts = [(7, 14), (10, 15), (13, 16), (16, 17), (19, 19), (21, 22), (23, 24), (24, 27), (23, 30)]
	for (x, y) in pts:
		c.put(x, y, rib[3])
		c.put(x, y + 1, rib[2])
		c.put(x, y + 2, rib[1] if (x % 3) else rib[0])
	c.put(8, 13, rib[1])  # knot
	c.put(8, 14, rib[2])
	c.put(7, 16, rib[0])
	for dx, dy in ((22, 27), (24, 29), (23, 31)):  # frayed tail
		c.put(dx, dy, rib[0])
	for x in range(1, 12):  # earth mound, pebbles and grass at the foot
		c.put(x, 43, hexc("2a2220") if x % 3 else hexc("3a302a"))
		if 2 < x < 10:
			c.put(x, 42, hexc("3a302a"))
	for x in (2, 4, 9):
		c.put(x, 41, MOSS[2])
		c.put(x, 40, MOSS[1])
	c.put(10, 42, STONE[3])
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

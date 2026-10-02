"""Backdrop layers of the slice (RUN-029): sky, drifting clouds, far citadel,
viaduct of arches, haze and the near ruined forest.

All layers are native 1x pixel art, dithered (no smooth gradients) and tile
horizontally without seams (every x-dependent function is periodic or wraps).
Contrast stays below the foreground (Art Bible: backgrounds less contrasted and
less detailed than gameplay layers); warm/red accents are sparse and dark.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, hexc  # noqa: E402
from palette import BLOOD, EMBER, MIST, SKY  # noqa: E402

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

# Local extra colours (dark desaturated reds / haze) consistent with the Art Bible:
# decor uses dark desaturated reds, saturated red stays reserved for danger/moon.
DUSK_RED = [hexc("22171f"), hexc("2c1a24"), hexc("3a1c28"), hexc("4a2230")]
FOG = hexc("2b3647")


def rng(*seed):
	return random.Random("-".join(map(str, seed)))


def dither(t, x, y):
	"""True where the ordered dither says 'use the second colour' for blend t in 0..1."""
	return t * 16 > BAYER[y % 4][x % 4] + 0.5


def dither_band(c, y0, y1, a, b, x0=0, x1=None):
	x1 = c.w if x1 is None else x1
	for y in range(y0, y1):
		t = (y - y0) / max(1, y1 - y0 - 1)
		for x in range(x0, x1):
			c.put(x, y, b if dither(t, x, y) else a)


def periodic(W, seed, terms=4, base_freq=2):
	"""Sum of sines whose frequencies are integers over W: seamless on wrap. Returns f(x)."""
	r = rng("periodic", seed)
	parts = [(r.randint(base_freq, base_freq + 5 * (i + 1)), r.uniform(0, 6.28), 1.0 / (i + 1)) for i in range(terms)]
	norm = sum(p[2] for p in parts)
	return lambda x: sum(a * math.sin(2 * math.pi * k * x / W + ph) for k, ph, a in parts) / norm


def spire(c, cx, base_y, half_w, height, color, concave=1.5):
	for i in range(height):
		w = half_w * (1 - i / height) ** concave
		for x in range(int(round(cx - w)), int(round(cx + w)) + 1):
			c.put(x % c.w, base_y - i, color)


def block(c, x0, y0, w, h, color):
	for y in range(y0, y0 + h):
		for x in range(x0, x0 + w):
			c.put(x % c.w, y, color)


# ------------------------------------------------------------------ sky
def sky():
	"""Screen-fixed 640x360: night gradient, dusky horizon haze, stars, blood moon."""
	c = Canvas(640, 360)
	bands = [SKY[0], SKY[1], SKY[2], SKY[3], SKY[4], hexc("33323f")]
	h = 360 // (len(bands) - 1)
	for i in range(len(bands) - 1):
		dither_band(c, i * h, (i + 1) * h, bands[i], bands[i + 1])
	# Dark desaturated red underglow of the horizon (below the clouds, sparse).
	for y in range(150, 300):
		t = 1 - abs(y - 215) / 70.0
		if t <= 0:
			continue
		for x in range(640):
			if dither(t * 0.55, x, y) and (x + y) % 2 == 0:
				c.put(x, y, DUSK_RED[1] if t > 0.5 else DUSK_RED[0])
	r = rng("stars")
	for _ in range(130):
		x, y = r.randint(0, 639), r.randint(0, 190)
		if math.hypot(x - 520, y - 74) < 46:
			continue
		k = r.random()
		c.put(x, y, MIST[2] if k < 0.15 else MIST[1] if k < 0.45 else MIST[0])
		if k < 0.06:  # a few brighter plus-shaped stars
			for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
				c.put(x + dx, y + dy, SKY[5])
	mx, my, rad = 520, 74, 26
	halo = [hexc("3a1a24"), hexc("2c1820"), hexc("241820")]
	for y in range(my - rad - 22, my + rad + 23):
		for x in range(mx - rad - 22, mx + rad + 23):
			d = math.hypot(x - mx, y - my)
			if rad < d <= rad + 5 and (x + y) % 2 == 0:
				c.put(x, y, halo[0])
			elif rad + 5 < d <= rad + 12 and (x + 2 * y) % 4 == 0:
				c.put(x, y, halo[1])
			elif rad + 12 < d <= rad + 22 and (x + 2 * y) % 8 == 0:
				c.put(x, y, halo[2])
	moon = [BLOOD[0], BLOOD[1], BLOOD[2], BLOOD[3], BLOOD[4]]
	for y in range(my - rad, my + rad + 1):
		for x in range(mx - rad, mx + rad + 1):
			d = math.hypot(x - mx, y - my)
			if d > rad:
				continue
			lx, ly = (x - mx) / rad, (y - my) / rad
			light = 0.55 - 0.45 * (lx * 0.6 + ly * 0.8) - 0.35 * (d / rad) ** 3
			k = 3 if light > 0.85 else 2 if light > 0.45 else 1 if light > 0.1 else 0
			# Ordered dither between neighbouring tones keeps the disc pixel-art.
			frac = (light % 0.4) / 0.4
			if k < 3 and dither(frac * 0.5, x, y) and 0.1 < light < 0.9:
				k += 1
			c.put(x, y, moon[k])
	for cx, cy, cr in ((508, 63, 5), (530, 85, 4), (524, 67, 2), (503, 84, 3), (534, 70, 1), (515, 92, 2)):
		for y in range(cy - cr, cy + cr + 1):
			for x in range(cx - cr, cx + cr + 1):
				if math.hypot(x - cx, y - cy) <= cr:
					c.put(x, y, moon[1] if x + y < cx + cy else moon[2])
	# Three bats crossing the moon.
	for bx, by in ((505, 58), (548, 48), (539, 100)):
		for dx, dy in ((-2, 0), (-1, -1), (0, 0), (1, -1), (2, 0), (0, 1)):
			c.put(bx + dx, by + dy, hexc("16101a"))
	return c


def clouds():
	"""640x120 transparent tiling cloud banks and wisps (drifted by the backdrop).

	Each cloud is a union of flattened-bottom puffs with a dithered edge, light from
	the upper right (the moon side) giving a faint rim, and a dark warm underside.
	Contrast stays low against the night sky."""
	W, H = 640, 120
	r = rng("clouds2")
	c = Canvas(W, H)
	rim, lit, body, shade = SKY[5], SKY[4], SKY[3], SKY[2]
	under = hexc("1f1b27")
	# (centre x, centre y, half width, kind): banks have several puffs, wisps are thin.
	specs = [(70, 30, 62, "bank"), (210, 62, 78, "bank"), (350, 22, 46, "wisp"), (430, 80, 70, "bank"),
		(560, 40, 54, "bank"), (140, 100, 44, "wisp"), (330, 52, 38, "wisp"), (610, 96, 36, "wisp")]
	for cx, cy, hw, kind in specs:
		puffs = []
		if kind == "bank":
			n = r.randint(5, 7)
			for i in range(n):
				t = (i + 0.5) / n
				px = cx - hw + 2 * hw * t + r.randint(-4, 4)
				env = math.sin(math.pi * t) ** 0.8
				ry = 3 + 9 * env * r.uniform(0.6, 1.0)
				puffs.append((px, cy - ry * 0.3 + r.randint(-2, 2), hw / n * r.uniform(1.0, 1.5), ry))
		else:
			for i in range(3):
				puffs.append((cx + (i - 1) * hw * 0.6, cy + r.randint(-1, 1), hw * r.uniform(0.5, 0.7), r.uniform(3.0, 4.4)))
		mask = {}
		for y in range(cy - 20, cy + 14):
			for x in range(cx - hw - 20, cx + hw + 20):
				best = 0.0
				for px, py, rx, ry in puffs:
					dy = (y - py) * (1.0 if y < py else 2.3)
					d = 1 - ((x - px) / rx) ** 2 - (dy / ry) ** 2
					best = max(best, d)
				if best > 0.3 or (best > 0 and dither(best / 0.3, x, y)):
					mask[(x, y)] = best
		for (x, y), d in mask.items():
			l = d - 0.25 * ((x - cx) / hw) * -1 - 0.15 * ((y - cy) / 8.0)
			if (x, y - 1) not in mask and ((x + 1, y - 1) not in mask or d < 0.5):
				col = rim if dither(0.75, x, y) else lit
			elif (x + 1, y) not in mask and (x + 1, y - 1) not in mask:
				col = lit
			elif (x, y + 1) not in mask:
				col = under if dither(0.6, x, y) else shade
			else:
				col = body if (l > 0.35 and dither(0.7, x, y)) or l > 0.6 else shade
			c.put(x % W, y % H, col)
	return c


# ------------------------------------------------------------------ far citadel
def far_layer():
	"""640x170 tiling: two crag ridges and the Darkveil citadel with ember windows."""
	W, H = 640, 170
	c = Canvas(W, H)
	r = rng("far2")
	back, mid, cit, front = hexc("1f2838"), hexc("1a2230"), hexc("12161f"), hexc("141a23")
	# Dark red haze behind the citadel (dithered; Art Bible: rare red).
	for yy in range(14, 118):
		for x in range(330, 600):
			d = math.hypot((x - 475) / 135.0, (yy - 100) / 80.0)
			if d < 1.0 and dither((1 - d) * 0.7, x, yy) and (x + yy) % 2 == 0:
				c.put(x, yy, DUSK_RED[2] if d < 0.45 else DUSK_RED[1] if d < 0.75 else DUSK_RED[0])
	f1, f2 = periodic(W, "far-back", 5, 3), periodic(W, "far-mid", 5, 6)
	back_h = [int(104 + 20 * f1(x) + r.choice((-1, 0, 0, 1))) for x in range(W)]
	mid_h = [int(116 + 12 * f2(x) + r.choice((-1, 0, 0, 0, 1))) for x in range(W)]
	for x in range(W):
		for yy in range(back_h[x], H):
			c.put(x, yy, back if (yy - back_h[x] > 1 or x % 2) else hexc("26303f"))
	# Citadel mound (peak around x=470) then the keep.
	for x in range(380, 580):
		top = 114 - int(18 * math.exp(-((x - 470) / 55.0) ** 2))
		for yy in range(top, H):
			c.put(x, yy, cit)
	base = 108
	# (x centre, half width, height, spire height, style) back to front; tall central keep.
	towers = [(398, 5, 20, 12, "broken"), (412, 6, 40, 26, "spire"), (428, 8, 58, 30, "step"), (446, 6, 36, 0, "broken"),
		(466, 10, 86, 46, "step"), (486, 7, 54, 28, "spire"), (504, 9, 70, 38, "step"), (522, 6, 36, 0, "broken"),
		(538, 7, 50, 26, "spire"), (555, 5, 28, 0, "broken"), (380, 4, 16, 10, "spire")]
	for cx, hw, ht, sp, style in towers:
		block(c, cx - hw, base - ht, hw * 2 + 1, ht + 8, cit)
		if style == "step":
			# Setback shoulder: wider lower body, then ledge.
			block(c, cx - hw - 3, base - int(ht * 0.55), hw * 2 + 7, int(ht * 0.55) + 8, cit)
			block(c, cx - hw - 1, base - int(ht * 0.55) - 2, hw * 2 + 3, 2, cit)
		if style == "broken":
			for x in range(cx - hw, cx + hw + 1):
				c.put(x, base - ht - 1 - ((x * 5) % 3), cit)
				if (x + cx) % 3 == 0:
					c.put(x, base - ht - 3, cit)
		elif sp:
			spire(c, cx, base - ht - 1, hw + 1, sp, cit, 1.1 + (cx % 3) * 0.25)
			for sx in (cx - hw, cx + hw):
				block(c, sx, base - ht - 4, 1, 4, cit)
				c.put(sx, base - ht - 5, cit)
	# Terraced lower town: gabled roofs stepping down the mound on both sides.
	for x0, wd, hh in ((386, 16, 10), (574, 14, 12), (362, 14, 7), (590, 16, 8)):
		block(c, x0, base - hh + 8, wd, hh + 4, cit)
		spire(c, x0 + wd // 2, base - hh + 7, wd // 2 + 2, 8, cit, 1.0)
	block(c, 392, base - 10, 172, 18, cit)
	for x in range(392, 564, 4):
		block(c, x, base - 13, 2, 3, cit)
	for bx, direction in ((410, 1), (444, -1), (490, 1), (528, -1)):
		for i in range(12):
			c.put(bx + direction * i, base - 26 + i, cit)
			c.put(bx + direction * i, base - 25 + i, cit)
	# Moon rim-light (moon is to the upper right): dark red pixel on bodies' right edges.
	for x in range(360, 600):
		for yy in range(base - 90, base + 4):
			if c.get(x, yy) == cit and c.get(x + 1, yy) != cit and c.get(x + 1, yy + 1) != cit and c.get(x, yy - 1) == cit:
				if yy % 2 == 0:
					c.put(x, yy, DUSK_RED[3])
	# Windows: tiny ember/red lights, sparse; the keep has a red sigil.
	for cx, hw, ht, sp, style in towers:
		for wy in range(base - ht + 8, base - 4, 11):
			if r.random() < 0.6:
				col = EMBER[0] if r.random() < 0.65 else BLOOD[1]
				c.put(cx, wy, col)
				c.put(cx, wy + 1, col)
				if r.random() < 0.35:
					c.put(cx + 3, wy + 3, EMBER[1])
	for dx, dy, col in ((0, 0, BLOOD[3]), (-1, 0, BLOOD[1]), (1, 0, BLOOD[1]), (0, -1, BLOOD[1]), (0, 1, BLOOD[1])):
		c.put(466 + dx, base - 62 + dy, col)
	c.put(466, base - 62, BLOOD[4])
	for yy in range(base - 58, base - 44):
		if yy % 2 == 0:
			c.put(466, yy, BLOOD[0] if yy % 4 else BLOOD[1])
	# Front crag line, darker.
	for x in range(W):
		for yy in range(mid_h[x], H):
			if not (380 <= x < 580 and yy < 118):
				c.put(x, yy, front)
	# Tiny watch fires on the far ridge (distant warm accent).
	for fx in (60, 160, 255, 330, 610):
		fy = mid_h[fx] - 1
		c.put(fx, fy, EMBER[1])
		c.put(fx, fy - 1, EMBER[0])
	return c


# ------------------------------------------------------------------ viaduct of arches
def arch_layer():
	"""640x112 tiling: a ruined multi-arched viaduct with towers, lit by sparse lanterns."""
	W, H = 640, 112
	c = Canvas(W, H)
	r = rng("arches")
	stone, light, dark = hexc("1a2230"), hexc("222d3c"), hexc("151b26")
	pitch = 64
	deck_y = 34
	# Deck slab and parapet.
	block(c, 0, deck_y, W, 7, stone)
	for x in range(W):
		c.put(x, deck_y, light)
		c.put(x, deck_y + 6, dark)
	for x in range(0, W, 6):
		if r.random() < 0.8:
			block(c, x, deck_y - 3, 3, 3, stone)
	# Arches: piers + semi-elliptical openings (transparent, showing the layers behind).
	for k in range(W // pitch):
		x0 = k * pitch
		for x in range(x0, x0 + pitch):
			dx = (x - (x0 + pitch / 2.0 - 1)) / 24.0
			open_h = 0 if abs(dx) >= 1 else int(30 * math.sqrt(1 - dx * dx))
			for yy in range(deck_y + 7, H):
				if yy < deck_y + 7 + 36 - open_h and yy - (deck_y + 7) < 36 - open_h + 0:
					col = stone
				elif yy >= deck_y + 7 + 36:
					col = stone if (x - x0) < 9 or (x - x0) > pitch - 10 else None
				else:
					col = None
				if col is not None:
					edge = abs(dx) < 1 and yy == deck_y + 7 + 36 - open_h
					c.put(x, yy, light if edge else col)
		# pier shading
		for yy in range(deck_y + 43, H):
			c.put(x0 + 8, yy, dark)
			c.put((x0 + pitch - 9) % W, yy, dark)
	# Voussoir tick marks to read as masonry, plus a few missing stones.
	for k in range(W // pitch):
		x0 = k * pitch
		for i in range(11):
			a = math.pi * (0.1 + 0.8 * i / 10)
			ex, ey = x0 + pitch // 2 - 1 + int(24 * math.cos(a)), deck_y + 43 - int(30 * math.sin(a))
			c.put(ex, ey, dark)
	for _ in range(60):
		x, y = r.randint(0, W - 1), r.randint(deck_y + 8, H - 1)
		if c.get(x, y) == stone:
			c.put(x, y, dark if r.random() < 0.5 else light)
	# Towers rising from the deck (ruined tops), fixed positions.
	for tx, tw, th, kind in ((88, 22, 50, "broken"), (292, 18, 66, "spire"), (500, 26, 38, "broken"), (410, 12, 28, "stub")):
		block(c, tx, deck_y - th, tw, th + 2, stone)
		for yy in range(deck_y - th, deck_y):
			c.put(tx, yy, light)
			c.put(tx + tw - 1, yy, dark)
		if kind == "spire":
			spire(c, tx + tw // 2, deck_y - th - 1, tw // 2 + 1, 26, stone, 1.3)
		elif kind == "broken":
			for x in range(tx, tx + tw, 5):
				cut = r.randint(0, 3)
				block(c, x, deck_y - th - 3 + cut, 3, 3 - cut + 3, stone)
			block(c, tx + tw // 2 - 4, deck_y - th, 10, 6, None)  # collapsed top
			for x in range(tx + tw // 2 - 4, tx + tw // 2 + 6):
				for yy in range(deck_y - th, deck_y - th + 6):
					c.px[yy * W + x % W] = None
		for wy in range(deck_y - th + 10, deck_y - 6, 12):
			block(c, tx + tw // 2 - 1, wy, 2, 5, dark)
			if r.random() < 0.45:
				c.put(tx + tw // 2, wy + 1, EMBER[0])
				c.put(tx + tw // 2, wy + 2, EMBER[1] if r.random() < 0.4 else EMBER[0])
	# Lanterns on the parapet.
	for lx in (40, 152, 232, 372, 452, 560):
		c.put(lx, deck_y - 4, EMBER[0])
		c.put(lx, deck_y - 3, EMBER[1])
	# Atmospheric fade: dither toward fog at the base and slightly at the top.
	for y in range(H):
		for x in range(W):
			p = c.px[y * W + x]
			if p is None:
				continue
			t = max(0.0, (y - 56) / 56.0) * 0.8
			if t > 0 and dither(t, x, y):
				c.px[y * W + x] = FOG
	return c


# ------------------------------------------------------------------ haze
def mist_layer():
	"""640x48 tiling haze band (semi-transparent, dithered)."""
	W, H = 640, 48
	c = Canvas(W, H)
	f = periodic(W, "mist", 4, 4)
	for y in range(H):
		a = int(78 * max(0.0, math.sin(math.pi * y / (H - 1))) ** 1.3)
		for x in range(W):
			thick = 0.5 + 0.45 * f(x)
			if dither(thick * max(0.0, math.sin(math.pi * y / (H - 1))), x * 3, y) and (x + y) % 3 != 0:
				c.put(x, y, MIST[0][:3] + (a,))
	return c


# ------------------------------------------------------------------ near ruined forest
def _branch(c, x, y, angle, length, width, col, r, depth):
	if depth == 0 or length < 2:
		return
	x1 = x + math.cos(angle) * length
	y1 = y + math.sin(angle) * length
	steps = int(length) + 1
	for i in range(steps + 1):
		t = i / steps
		px, py = x + (x1 - x) * t, y + (y1 - y) * t
		for w in range(width):
			c.put(int(px) % c.w + w, int(py), col)
	for _ in range(r.choice((1, 2, 2, 3))):
		_branch(c, x1, y1, angle + r.uniform(-0.75, 0.75), length * r.uniform(0.55, 0.75), max(1, width - 1), col, r, depth - 1)


def mid_layer():
	"""512x132 tiling: dead forest, broken arched walls, columns and crosses, blue-grey."""
	W, H = 512, 132
	c = Canvas(W, H)
	r = rng("mid2")
	ground, tree, far_tree = hexc("1a212b"), hexc("1d2530"), hexc("1b232e")
	ruin, ruin_l, ruin_d = hexc("1f2835"), hexc("273241"), hexc("171d27")
	gy = lambda x: 104 + int(3 * math.sin(2 * math.pi * 3 * x / W) + 2 * math.sin(2 * math.pi * 9 * x / W))
	# Ruined walls with arched openings behind the trees.
	for wx, ww, wh in ((40, 76, 46), (232, 92, 58), (400, 64, 34)):
		for x in range(wx, wx + ww):
			top = 104 - wh + (r.randint(0, 5) if (x - wx) % 9 < 4 else 0)
			if x > wx + ww - 18:
				top += (x - (wx + ww - 18)) * 2
			for yy in range(top, 110):
				c.put(x, yy, ruin)
			c.put(x, top, ruin_l)
		for x in range(wx, wx + ww):
			c.put(x, 104 - 1, ruin_d)
		# arched openings
		for ax in range(wx + 10, wx + ww - 22, 28):
			for x in range(ax, ax + 12):
				dx = (x - (ax + 5.5)) / 6.0
				for yy in range(104 - 28 + int(6 - 6 * math.sqrt(max(0, 1 - dx * dx))), 104):
					c.px[yy * W + x] = None if abs(dx) < 1 else c.px[yy * W + x]
	# Ground.
	for x in range(W):
		for yy in range(gy(x), H):
			c.put(x, yy, ground)
		if r.random() < 0.5:
			c.put(x, gy(x), hexc("212a35"))
	# Broken columns, crosses and a gibbet.
	for cx, ch in ((18, 30), (166, 22), (214, 36), (356, 26), (470, 20)):
		block(c, cx, gy(cx) - ch, 6, ch + 2, ruin)
		block(c, cx - 1, gy(cx) - ch - 2, 8, 2, ruin_l)
		c.put(cx + 5, gy(cx) - ch, ruin_d)
	for cx in (130, 190, 330, 426, 498):
		for yy in range(gy(cx) - 12, gy(cx)):
			c.put(cx, yy, ruin)
		block(c, cx - 3, gy(cx) - 9, 7, 1, ruin)
	for yy in range(gy(300) - 40, gy(300)):
		c.put(300, yy, ruin)
	block(c, 300, gy(300) - 40, 12, 2, ruin)
	for yy in range(gy(300) - 38, gy(300) - 28):
		c.put(310, yy, ruin_d)
	# Dead trees, denser at the edges (skipping the ruin walls).
	x = 6
	while x < W - 10:
		h = r.randint(34, 70)
		col = tree if r.random() < 0.6 else far_tree
		_branch(c, x, gy(x) + 2, -math.pi / 2 + r.uniform(-0.14, 0.14), h * 0.55, 3, col, r, 5)
		x += r.randint(26, 52)
	# Sparse warm lanterns in the ruin (dim).
	for lx, ly in ((78, 74), (270, 62), (418, 86)):
		c.put(lx, ly, EMBER[0])
		c.put(lx, ly + 1, EMBER[1])
	return c


def build_all():
	return {"bg_sky": sky(), "bg_clouds": clouds(), "bg_far": far_layer(), "bg_arches": arch_layer(),
		"bg_mid": mid_layer(), "bg_mist": mist_layer()}

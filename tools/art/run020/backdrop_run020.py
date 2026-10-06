"""Backdrop layers of N2-N4 (RUN-020), same method and scale as tools/art/world_bg.py.

Per biome: bg_<biome>_sky (640x360, fixed to the screen), bg_<biome>_far (640x170) and
bg_<biome>_mid (512x132), both tiling horizontally without seams (periodic x functions,
wrapped puts). The N1 clouds and mist layers are reused, tinted by the backdrop script.
Backgrounds keep very low contrast (Art Bible: background < terrain < interactive <
enemies < player < VFX); warm/spectral accents are single dim pixels.
"""
import math
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from pixel import Canvas, hexc  # noqa: E402
from palette import EMBER, MIST, SKY  # noqa: E402
from world_bg import _branch, block, dither, dither_band, periodic, rng, spire  # noqa: E402  (read only)
from palette_run020 import DUSK_VIOLET, MUD, NIGHT, PINE, ROT, SPECTRAL  # noqa: E402


def wput(c, x, y, col):
	c.put(x % c.w, y, col)


def sky(name, bands, haze, haze_y, moon, moon_pos, moon_r, stars, halo):
	c = Canvas(640, 360)
	h = 360 // (len(bands) - 1)
	for i in range(len(bands) - 1):
		dither_band(c, i * h, (i + 1) * h, bands[i], bands[i + 1])
	for y in range(haze_y - 70, haze_y + 70):
		t = 1 - abs(y - haze_y) / 70.0
		for x in range(640):
			if t > 0 and dither(t * 0.5, x, y) and (x + y) % 2 == 0:
				c.put(x, y, haze[1] if t > 0.5 else haze[0])
	r = rng(name, "stars")
	mx, my = moon_pos
	for _ in range(stars):
		x, y = r.randint(0, 639), r.randint(0, 200)
		if math.hypot(x - mx, y - my) < moon_r + 18:
			continue
		k = r.random()
		c.put(x, y, MIST[2] if k < 0.12 else MIST[1] if k < 0.4 else MIST[0])
	for y in range(my - moon_r - 18, my + moon_r + 19):
		for x in range(mx - moon_r - 18, mx + moon_r + 19):
			d = math.hypot(x - mx, y - my)
			if moon_r < d <= moon_r + 6 and (x + y) % 2 == 0:
				c.put(x, y, halo[0])
			elif moon_r + 6 < d <= moon_r + 16 and (x + 2 * y) % 6 == 0:
				c.put(x, y, halo[1])
	for y in range(my - moon_r, my + moon_r + 1):
		for x in range(mx - moon_r, mx + moon_r + 1):
			d = math.hypot(x - mx, y - my)
			if d > moon_r:
				continue
			light = 0.6 - 0.45 * ((x - mx) / moon_r * 0.6 + (y - my) / moon_r * 0.8) - 0.3 * (d / moon_r) ** 3
			k = 3 if light > 0.85 else 2 if light > 0.45 else 1 if light > 0.1 else 0
			if k < 3 and dither((light % 0.4) / 0.8, x, y) and 0.1 < light < 0.9:
				k += 1
			c.put(x, y, moon[k])
	return c


def ridge(c, W, H, seed, base, amp, color, terms=5, freq=3):
	f = periodic(W, seed, terms, freq)
	tops = [int(base + amp * f(x)) for x in range(W)]
	for x in range(W):
		for y in range(tops[x], H):
			c.put(x, y, color)
	return tops


def house(c, x0, ground, w, h, roof, col, broken=False, lean=0):
	block_wrap(c, x0, ground - h, w, h + 2, col)
	for i in range(roof):
		half = (w // 2 + 2) * (1 - i / roof)
		cx = x0 + w / 2 + lean * i / roof
		if broken and i > roof // 2 and int(cx) % 2:
			continue
		for x in range(int(cx - half), int(cx + half) + 1):
			wput(c, x, ground - h - i, col)


def block_wrap(c, x0, y0, w, h, col):
	for y in range(y0, y0 + h):
		for x in range(x0, x0 + w):
			wput(c, x, y, col)


def pine(c, cx, ground, height, col, r):
	for i in range(height):
		t = i / height
		half = (1 - t) * height * 0.28 + 0.5
		if (i % 5) == 4:
			half *= 0.7  # layered branch tiers
		for x in range(int(round(cx - half)), int(round(cx + half)) + 1):
			wput(c, x, ground - i, col)
	for y in range(ground - 3, ground + 2):
		wput(c, cx, y, col)


# ------------------------------------------------------------------ N2 Blight Town
def blight_far():
	W, H = 640, 170
	c = Canvas(W, H)
	r = rng("n2far")
	ridge(c, W, H, "n2-hills", 118, 10, hexc("1d2129"))
	town = hexc("15171d")
	ground = 126
	ridge(c, W, H, "n2-ground", ground, 3, town, 3, 4)
	x = 4
	while x < W - 6:
		w = r.randint(12, 22)
		hh = r.randint(10, 22)
		house(c, x, ground, w, hh, r.randint(7, 11), town, r.random() < 0.3, r.choice((-2, 0, 0, 2)))
		if r.random() < 0.4:  # chimney
			block_wrap(c, x + w - 4, ground - hh - 9, 2, 6, town)
		if r.random() < 0.5:
			wput(c, x + w // 2, ground - hh // 2, EMBER[0])
		x += w + r.randint(-3, 6)
	# Leaning steeple of the town chapel.
	block_wrap(c, 300, ground - 44, 10, 46, town)
	spire(c, 305, ground - 45, 6, 26, town, 1.2)
	wput(c, 305, ground - 30, EMBER[0])
	# Rot smoke columns (dithered, very low contrast).
	for sx in (90, 300, 470):
		for y in range(20, ground - 20):
			t = (y - 20) / (ground - 40)
			wx = int(sx + 10 * math.sin(y / 9.0) * (1 - t))
			for dx in range(-3 - int(6 * (1 - t)), 4 + int(6 * (1 - t))):
				if dither(0.35 * t, wx + dx, y):
					wput(c, wx + dx, y, ROT[1])
	return c


def blight_mid():
	W, H = 512, 132
	c = Canvas(W, H)
	r = rng("n2mid")
	ground, body, edge = hexc("1b1e22"), hexc("1d2026"), hexc("252830")
	gy = lambda x: 104 + int(2 * math.sin(2 * math.pi * 3 * x / W))
	for hx, w, hh, broken in ((20, 46, 40, False), (150, 38, 52, True), (300, 54, 36, False), (420, 40, 46, True)):
		house(c, hx, 104, w, hh, 18, body, broken, r.choice((-4, 0, 4)))
		for x in range(hx, hx + w):
			if c.get(x, 104 - hh) == body:
				c.put(x, 104 - hh, edge)
		for wx in range(hx + 6, hx + w - 6, 12):  # boarded windows
			block_wrap(c, wx, 104 - hh + 10, 5, 6, hexc("17191d"))
			for i in range(5):
				wput(c, wx + i, 104 - hh + 10 + i, MUD[1])
	for x in range(W):
		for y in range(gy(x), H):
			c.put(x, y, ground)
	for cx in (110, 260, 392, 490):  # dead trees
		_branch(c, cx, gy(cx) + 2, -math.pi / 2 + r.uniform(-0.2, 0.2), r.randint(22, 32), 3, body, r, 5)
	# Gallows silhouette.
	block_wrap(c, 240, gy(240) - 44, 3, 44, body)
	block_wrap(c, 240, gy(240) - 44, 22, 2, body)
	for y in range(gy(240) - 42, gy(240) - 30):
		wput(c, 259, y, edge)
	for lx in (64, 330):  # dim lanterns
		wput(c, lx, 80, EMBER[0])
		wput(c, lx, 81, EMBER[1])
	return c


# ------------------------------------------------------------------ N3 Black Forest
def forrest_far():
	W, H = 640, 170
	c = Canvas(W, H)
	r = rng("n3far")
	back = ridge(c, W, H, "n3-ridge", 96, 18, NIGHT[3])
	for layer, (base, col, step, hmin, hmax) in enumerate(((112, NIGHT[2], 7, 18, 34), (128, hexc("111a22"), 9, 24, 44))):
		f = periodic(W, ("n3-pines", layer), 4, 3)
		x = r.randint(0, 5)
		while x < W:
			g = int(base + 6 * f(x))
			pine(c, x, g, r.randint(hmin, hmax), col, r)
			for y in range(g, H):
				wput(c, x, y, col)
				wput(c, x + 1, y, col)
			x += r.randint(step - 3, step + 3)
		for x in range(W):
			for y in range(int(base + 6 * f(x)) + 1, H):
				c.put(x, y, col)
	# A faint cold glint on the far ridge top.
	for x in range(0, W, 3):
		if c.get(x, back[x]) == NIGHT[3] and (x * 7) % 5 == 0:
			c.put(x, back[x], NIGHT[4])
	return c


def forrest_mid():
	W, H = 512, 132
	c = Canvas(W, H)
	r = rng("n3mid")
	ground, trunk, needle, edge = hexc("10181a"), hexc("131d20"), hexc("152422"), PINE[1]
	gy = lambda x: 106 + int(3 * math.sin(2 * math.pi * 4 * x / W) + 2 * math.sin(2 * math.pi * 7 * x / W))
	x = 4
	while x < W:
		kind = r.random()
		if kind < 0.55:  # large pine
			h = r.randint(70, 104)
			pine(c, x, gy(x), h, needle, r)
			for y in range(gy(x) - h // 3, gy(x)):
				wput(c, x, y, trunk)
				wput(c, x + 1, y, trunk)
			for i in range(0, h, 5):  # cold moonlit needle tips on the right side
				half = int((1 - i / h) * h * 0.28)
				if half > 2 and r.random() < 0.6:
					wput(c, x + half, gy(x) - i, edge)
		else:  # tall bare trunk with crooked branches
			h = r.randint(60, 96)
			for y in range(gy(x) - h, gy(x)):
				for w in range(3):
					wput(c, x + w, y, trunk)
			for _ in range(3):
				_branch(c, x + 1, gy(x) - r.randint(h // 2, h), -math.pi / 2 + r.uniform(-1.0, 1.0), r.randint(10, 20), 2, trunk, r, 3)
		x += r.randint(18, 34)
	for x in range(W):
		for y in range(gy(x), H):
			c.put(x, y, ground)
		if r.random() < 0.4:  # ferns along the forest floor
			for y in range(gy(x) - r.randint(1, 4), gy(x)):
				c.put(x, y, needle)
	return c


# ------------------------------------------------------------------ N4 Forbidden Graveyard
def graveyard_far():
	W, H = 640, 170
	c = Canvas(W, H)
	r = rng("n4far")
	hill_col, sil = DUSK_VIOLET[2], hexc("1a1622")
	ridge(c, W, H, "n4-hill", 110, 14, hill_col)
	tops = ridge(c, W, H, "n4-front", 124, 6, sil, 4, 3)
	# Chapel with a tall bell tower on the hill.
	cx = 420
	g = tops[cx]
	block_wrap(c, cx - 20, g - 22, 34, 24, sil)
	house(c, cx - 20, g - 22, 34, 0, 12, sil)
	block_wrap(c, cx + 14, g - 52, 10, 54, sil)
	spire(c, cx + 19, g - 53, 6, 22, sil, 1.0)
	wput(c, cx + 19, g - 40, SPECTRAL[1])
	wput(c, cx + 19, g - 39, SPECTRAL[1])
	# Crosses and headstones along the hill line, bare trees.
	x = 6
	while x < W:
		gx = tops[x % W]
		if not cx - 26 < x < cx + 30:
			if r.random() < 0.6:
				for y in range(gx - r.randint(5, 9), gx):
					wput(c, x, y, sil)
				wput(c, x - 1, gx - 6, sil)
				wput(c, x + 1, gx - 6, sil)
			else:
				block_wrap(c, x - 1, gx - 4, 3, 4, sil)
		x += r.randint(8, 18)
	for tx in (70, 230, 560):
		_branch(c, tx, tops[tx] + 1, -math.pi / 2 + r.uniform(-0.2, 0.2), r.randint(18, 26), 2, sil, r, 5)
	return c


def graveyard_mid():
	W, H = 512, 132
	c = Canvas(W, H)
	r = rng("n4mid")
	ground, stone, edge = hexc("19161f"), hexc("1f1a27"), DUSK_VIOLET[3]
	gy = lambda x: 104 + int(2 * math.sin(2 * math.pi * 2 * x / W) + 2 * math.sin(2 * math.pi * 5 * x / W))
	# Mausoleum.
	mx = 300
	block_wrap(c, mx, gy(mx) - 40, 46, 42, stone)
	house(c, mx - 2, gy(mx) - 40, 50, 0, 14, stone)
	for px in (mx + 4, mx + 38):
		for y in range(gy(mx) - 36, gy(mx)):
			wput(c, px, y, edge)
	block_wrap(c, mx + 17, gy(mx) - 24, 12, 24, hexc("141119"))
	# Dead willow.
	_branch(c, 120, gy(120) + 2, -math.pi / 2, 30, 4, stone, r, 5)
	for _ in range(26):  # hanging strands
		sx = 120 + r.randint(-26, 26)
		sy = gy(120) - r.randint(38, 66)
		for y in range(sy, sy + r.randint(8, 22)):
			wput(c, sx, y, stone)
	for x in range(W):
		for y in range(gy(x), H):
			c.put(x, y, ground)
	# Iron fence segments with spear tips.
	for fx0, fx1 in ((20, 96), (180, 270), (380, 470)):
		for x in range(fx0, fx1):
			wput(c, x, gy(x) - 14, stone)
			wput(c, x, gy(x) - 6, stone)
			if (x - fx0) % 5 == 0:
				for y in range(gy(x) - 18, gy(x)):
					wput(c, x, y, stone)
				wput(c, x, gy(x) - 19, edge)
	# Headstones and crosses.
	x = 8
	while x < W:
		if not mx - 4 < x < mx + 50:
			g = gy(x)
			if r.random() < 0.5:
				block_wrap(c, x - 3, g - 10, 7, 10, stone)
				for dx in range(-2, 3):
					wput(c, x + dx, g - 11, stone)
				wput(c, x + 3, g - 9, edge)
			else:
				for y in range(g - 14, g):
					wput(c, x, y, stone)
				block_wrap(c, x - 3, g - 11, 7, 1, stone)
		x += r.randint(14, 30)
	for lx, ly in ((330, gy(330) - 30), (60, gy(60) - 22)):  # spectral candles, one pixel
		wput(c, lx, ly, SPECTRAL[2])
	return c


def build():
	return {
		"bg_blight_town_sky": sky("n2", [SKY[0], SKY[1], SKY[2], hexc("23262c"), hexc("2c2d2e"), hexc("34332e")],
			[ROT[1], ROT[2]], 215, [MUD[1], MUD[2], hexc("6e6a52"), hexc("88826a"), hexc("a29c80")], (150, 70), 18, 90,
			[hexc("2c2b22"), hexc("24241e")]),
		"bg_blight_town_far": blight_far(),
		"bg_blight_town_mid": blight_mid(),
		"bg_black_forrest_sky": sky("n3", [NIGHT[0], NIGHT[1], NIGHT[2], NIGHT[3], NIGHT[4], hexc("2a3a4c")],
			[NIGHT[3], hexc("1d2c34")], 230, [NIGHT[4], MIST[0], MIST[1], MIST[2], hexc("b8c6d0")], (470, 58), 16, 200,
			[NIGHT[4], NIGHT[3]]),
		"bg_black_forrest_far": forrest_far(),
		"bg_black_forrest_mid": forrest_mid(),
		"bg_forbidden_graveyard_sky": sky("n4", [DUSK_VIOLET[0], DUSK_VIOLET[1], DUSK_VIOLET[2], DUSK_VIOLET[3], hexc("403648"), hexc("483e50")],
			[SPECTRAL[0], hexc("2a3c44")], 200, [DUSK_VIOLET[4], SPECTRAL[2], SPECTRAL[3], SPECTRAL[4], hexc("a8c4c4")], (330, 64), 24, 120,
			[DUSK_VIOLET[3], DUSK_VIOLET[2]]),
		"bg_forbidden_graveyard_far": graveyard_far(),
		"bg_forbidden_graveyard_mid": graveyard_mid(),
	}

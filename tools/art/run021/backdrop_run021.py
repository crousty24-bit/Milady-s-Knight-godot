"""Near backdrop band of N2-N4 (RUN-021), same method and scale as tools/art/run020/backdrop_run020.py.

Per biome one bg_<biome>_near (512x190, wraps horizontally: periodic x functions, wrapped
puts). It replaces the flat fill under the mid band: very dark silhouettes, a touch cooler
and darker than the mid band, with the top rows left empty so no band edge shows. The last
rows fade by ordered dither into one solid colour (FINAL), which campaign_backdrop.gd uses to
fill below the band. No flat horizontal tops (broken, stepped, spiked outlines).
Usage: python3 tools/art/run021/backdrop_run021.py   (also writes work/run021/preview/*)
"""
import math
import os
import sys

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "run020"))
from pixel import Canvas, hexc, save_png  # noqa: E402
from palette import EMBER  # noqa: E402
from world_bg import dither, dither_band, periodic, rng  # noqa: E402  (read only)
from palette_run020 import DUSK_VIOLET, MUD, NIGHT, PINE, SPECTRAL  # noqa: E402
import backdrop_run020 as b20  # noqa: E402  (read only)

W, H = 512, 190
OUT = os.path.join(ROOT, "assets", "run021")
PREVIEW = os.path.join(ROOT, "work", "run021", "preview")
# Final fill colour of each band (campaign_backdrop.gd LOOKS[b][2] must match).
FINAL = {"n2": hexc("111317"), "n3": hexc("0a1012"), "n4": hexc("120f17")}


def wput(c, x, y, col):
	c.put(x % c.w, y, col)


def wblock(c, x0, y0, w, h, col):
	for y in range(y0, y0 + h):
		for x in range(x0, x0 + w):
			wput(c, x, y, col)


def ground_fill(c, tops, col, final, fade_from, speck=None, seed="speck"):
	"""Solid ground below the undulating line, sparse litter specks, then dither to the solid final colour."""
	for x in range(W):
		for y in range(tops[x], H):
			c.put(x, y, col)
	r = rng(seed)
	for _ in range(520 if speck else 0):  # litter / roots, thinning out with depth
		x, y = r.randint(0, W - 1), r.randint(min(tops) + 2, H - 60)
		if c.get(x, y) == col and r.random() < 1.0 - (y - min(tops)) / 90.0:
			wput(c, x, y, speck)
			if r.random() < 0.5:
				wput(c, x + r.choice((-2, -1, 1, 2)), y, speck)
	dither_band(c, fade_from, H - 6, col, final)
	for y in range(H - 6, H):
		for x in range(W):
			c.put(x, y, final)


def line_fade(c, x, y0, y1, col, fade=8):
	"""Vertical stroke whose top `fade` rows dither out (no hard cut)."""
	for y in range(y0, y1):
		t = min(1.0, (y - y0) / fade)
		if dither(t, x, y):
			wput(c, x, y, col)


# ------------------------------------------------------------------ N2 Blight Town
def blight_near():
	c = Canvas(W, H)
	r = rng("n2near")
	body, edge, dark, board = hexc("14171b"), hexc("1a1d22"), hexc("0f1114"), hexc("101215")
	ground, final = hexc("13161a"), FINAL["n2"]
	f = periodic(W, "n2near-ground", 3, 3)
	tops = [98 + int(2.5 * f(x)) for x in range(W)]
	x = 6
	while x < W - 40:
		w, h = r.randint(44, 70), r.randint(34, 52)
		base = tops[(x + w // 2) % W]
		top = base - h
		wblock(c, x, top, w, h + 2, body)
		# Broken gable / collapsed roof: ragged pitched top, never a flat edge.
		pitch, lean = r.randint(8, 14), r.choice((-5, -2, 0, 3, 5))
		for i in range(pitch):
			half = (w // 2 + 2) * (1 - i / pitch)
			cx = x + w / 2 + lean * i / pitch
			for xx in range(int(cx - half), int(cx + half) + 1):
				if i > 2 and ((xx * 7 + i * 3) % 11 < 3 or (i > pitch // 2 and xx % 3 == 0 and r.random() < 0.5)):
					continue
				wput(c, xx, top - i, body)
		for k in range(r.randint(2, 4)):  # ragged eave teeth in the wall top
			wblock(c, x + r.randint(0, w - 4), top, r.randint(2, 4), r.randint(2, 5), (0, 0, 0, 0) if False else body)
		# Timber frame: posts, rail, diagonal braces (slightly lighter than the wall).
		for px in range(x + 2, x + w - 1, r.randint(11, 14)):
			for y in range(top + 2, base + 2):
				wput(c, px, y, edge)
		for xx in range(x + 2, x + w - 2):
			wput(c, xx, top + h // 2, edge)
		bx = x + 3
		for i in range(min(10, w // 3)):
			wput(c, bx + i, top + 3 + i, edge)
			wput(c, bx + w - 8 - i, top + 3 + i, edge)
		# Boarded windows (dim); at most a rare single warm pixel.
		for wx in range(x + 7, x + w - 9, r.randint(13, 17)):
			wy = top + 5 + r.randint(0, 3)
			wblock(c, wx, wy, 6, 8, dark)
			for i in range(6):
				wput(c, wx + i, wy + 1 + i, board)
				wput(c, wx + 5 - i, wy + 6 - i, board)
			if r.random() < 0.15:
				wput(c, wx + 3, wy + 3, hexc("3a2616"))
		# Rot drips below the eave line.
		for dx in range(x + 3, x + w - 3, 5):
			if r.random() < 0.7:
				for y in range(base - r.randint(3, 8), base):
					wput(c, dx, y, MUD[0])
		x += w + r.randint(8, 26)
	# Rubble, snapped fence posts and a leaning beam between houses.
	for _ in range(34):
		px = r.randint(0, W - 1)
		g = tops[px]
		hh = r.randint(3, 11)
		for y in range(g - hh, g + 1):
			wput(c, px + (g - y) // 5 * r.choice((-1, 1)) * 0, y, body)
		if r.random() < 0.5:
			wput(c, px + 1, g - hh + 1, body)
			wput(c, px - 1, g - hh + 2, body)
	ground_fill(c, tops, ground, final, max(tops) + 24, edge, 'n2s')
	return c


# ------------------------------------------------------------------ N3 Black Forest
def forest_near():
	c = Canvas(W, H)
	r = rng("n3near")
	trunk, bark, fern, dark = hexc("0c1315"), hexc("101a1b"), hexc("0e1a19"), hexc("0a1011")
	ground, final = hexc("0c1315"), FINAL["n3"]
	f = periodic(W, "n3near-ground", 4, 3)
	tops = [102 + int(3 * f(x)) for x in range(W)]
	# Young pines behind (layered tiers, tops fade by dither, nothing reaches the band edge).
	x = 5
	while x < W:
		h = r.randint(46, 62)
		g = tops[x]
		for i in range(h):
			t = i / h
			half = (1 - t) * h * 0.26 + 0.5
			if i % 5 == 4:
				half *= 0.65
			for xx in range(int(round(x - half)), int(round(x + half)) + 1):
				wput(c, xx, g - i, fern)
		x += r.randint(16, 26)
	# Dense trunks: thick, slightly lighter bark edge on the right, roots flaring out.
	x = 3
	while x < W:
		w = r.randint(3, 6)
		g = tops[x]
		top = g - r.randint(46, 66)
		for xx in range(w):
			line_fade(c, x + xx, top, g + 3, bark if xx == w - 1 else trunk, 14)
		for k in range(r.randint(1, 2)):  # a snapped branch stub
			by = top + r.randint(18, 36)
			s = r.choice((-1, 1))
			for i in range(r.randint(4, 8)):
				wput(c, x + (w if s > 0 else -1) + s * i, by - i // 2, trunk)
		for i in range(1, 5):  # root flare
			wput(c, x - i, g + 1 - (4 - i) // 2 + 1, trunk)
			wput(c, x + w - 1 + i, g + 1 - (4 - i) // 2 + 1, trunk)
		x += r.randint(11, 22)
	# Undergrowth: arching fern fronds and bracken along the forest floor.
	for _ in range(70):
		px = r.randint(0, W - 1)
		g = tops[px]
		s = r.choice((-1, 1))
		ln = r.randint(6, 13)
		for i in range(ln):
			wput(c, px + s * i, g - int(i * 0.8 - (i * i) / (ln * 1.6)) - 1, dark)
			if i % 3 == 1:
				wput(c, px + s * i, g - int(i * 0.8 - (i * i) / (ln * 1.6)) - 2, dark)
	ground_fill(c, tops, ground, final, max(tops) + 24, bark, 'n3s')
	return c


# ------------------------------------------------------------------ N4 Forbidden Graveyard
def graveyard_near():
	c = Canvas(W, H)
	r = rng("n4near")
	stone, edge, dark = hexc("141119"), hexc("191521"), hexc("0e0c12")
	ground, final = hexc("120f17"), FINAL["n4"]
	f = periodic(W, "n4near-ground", 3, 2)
	tops = [100 + int(2.5 * f(x)) for x in range(W)]
	# Cemetery wall with crumbling, stepped top, in segments between crypts and gaps.
	crypts = ((60, 52), (330, 60))
	x = 0
	while x < W:
		seg = r.randint(60, 110)
		if any(cx - 8 < x + seg and x < cx + cw + 8 for cx, cw in crypts):
			x += r.randint(10, 20) + seg // 3
			continue
		for xx in range(x, x + seg):
			g = tops[xx % W]
			hh = 24 + int(3 * math.sin(xx / 7.0)) + (xx // 9) % 3 * 2 - r.randint(0, 1)
			if (xx // 13) % 5 == 3:
				hh -= 8  # breach
			for y in range(g - hh, g + 1):
				wput(c, xx, y, stone)
			if xx % 12 == 0:  # buttress pillar
				for y in range(g - hh - 5, g + 1):
					wput(c, xx, y, edge)
					wput(c, xx + 1, y, edge)
		# Iron fence rising over the wall: bars with spear tips.
		for xx in range(x + 4, x + seg - 4, 5):
			g = tops[xx % W]
			top = g - 24 - r.randint(12, 20)
			for y in range(top, g - 20):
				wput(c, xx, y, dark)
			wput(c, xx, top - 1, dark)
			wput(c, xx - 1, top + 1, dark)
			wput(c, xx + 1, top + 1, dark)
		for xx in range(x + 4, x + seg - 4):
			wput(c, xx, tops[xx % W] - 36, dark)
		x += seg + r.randint(8, 30)
	# Crypt fronts with a pediment and a dark door.
	for cx, cw in crypts:
		g = tops[(cx + cw // 2) % W]
		ch = 40
		wblock(c, cx, g - ch, cw, ch + 2, stone)
		for i in range(14):
			half = (cw // 2 + 3) * (1 - i / 14)
			for xx in range(int(cx + cw / 2 - half), int(cx + cw / 2 + half) + 1):
				if i > 9 and (xx + i) % 4 == 0:
					continue
				wput(c, xx, g - ch - i, stone)
		for px in (cx + 3, cx + cw - 5):
			for y in range(g - ch + 3, g + 1):
				wput(c, px, y, edge)
				wput(c, px + 1, y, edge)
		wblock(c, cx + cw // 2 - 6, g - 24, 12, 25, dark)
		for y in range(g - 30, g - 24):  # arched door head
			wput(c, cx + cw // 2 - 4 + (g - y - 24) * 0, y, stone)
		wput(c, cx + cw // 2, g - ch - 6, SPECTRAL[0])
	# Leaning tombstones and crosses in front, drifting sheared.
	x = 6
	while x < W:
		if not any(cx - 4 < x < cx + cw + 4 for cx, cw in crypts):
			g = tops[x]
			lean = r.choice((-2, -1, 1, 2))
			if r.random() < 0.6:
				hh = r.randint(10, 16)
				for y in range(g - hh, g + 1):
					off = (g - y) * lean // 8
					for dx in range(-3, 4):
						if y == g - hh and abs(dx) > 1:
							continue
						if y == g - hh + 1 and abs(dx) > 2:
							continue
						wput(c, x + dx + off, y, dark)
			else:
				hh = r.randint(14, 20)
				for y in range(g - hh, g + 1):
					wput(c, x + (g - y) * lean // 8, y, dark)
				wblock(c, x - 3 + (hh - 5) * lean // 8, g - hh + 4, 7, 1, dark)
		x += r.randint(12, 26)
	# Faint low spectral haze (very sparse dithered cyan-grey just above the ground).
	for y in range(tops_min(tops) - 6, max(tops) + 10):
		t = max(0.0, 1 - abs(y - (tops_min(tops) + 8)) / 14.0)
		for x in range(W):
			if t > 0 and c.get(x, y) in (None, dark) and dither(t * 0.22, x, y) and (x + y) % 2 == 0:
				c.put(x, y, SPECTRAL[0])
	ground_fill(c, tops, ground, final, max(tops) + 24, edge, 'n4s')
	return c


def tops_min(tops):
	return min(tops)


def build():
	return {
		"bg_blight_town_near": blight_near(),
		"bg_black_forrest_near": forest_near(),
		"bg_forbidden_graveyard_near": graveyard_near(),
	}


# ------------------------------------------------------------------ previews
def stack(near, sky, far, mid, mist_col, near_y=170, mid_y=104, far_y=58, shift=0):
	"""640x360 composition of the layers at the reference framing (tiled bands)."""
	c = Canvas(640, 360)
	c.blit(sky, 0, 0)
	for k in range(-1, 3):
		c.blit(far, k * far.w - shift // 12, far_y)
	for k in range(-1, 3):
		c.blit(mid, k * mid.w - shift // 3, mid_y)
	for k in range(-1, 3):
		c.blit(near, k * near.w - int(shift * 0.42), near_y)
	return c


def previews(built):
	os.makedirs(PREVIEW, exist_ok=True)
	skies = {"n2": b20.build()["bg_blight_town_sky"]}
	layers = b20.build()
	for tag, name, biome in (("n2", "bg_blight_town_near", "blight_town"), ("n3", "bg_black_forrest_near", "black_forrest"), ("n4", "bg_forbidden_graveyard_near", "forbidden_graveyard")):
		near = built[name]
		save_png(near, os.path.join(PREVIEW, f"{name}_x2.png"), 2)
		save_png(near, os.path.join(PREVIEW, f"{name}_x3.png"), 3)
		tiled = Canvas(W * 2, H)
		tiled.blit(near, 0, 0)
		tiled.blit(near, W, 0)
		save_png(tiled, os.path.join(PREVIEW, f"{name}_tiled_seam.png"), 2)
		key = {"n2": "blight_town", "n3": "black_forrest", "n4": "forbidden_graveyard"}[tag]
		st = stack(near, layers[f"bg_{key}_sky"], layers[f"bg_{key}_far"], layers[f"bg_{key}_mid"], None)
		save_png(st, os.path.join(PREVIEW, f"stack_{tag}.png"), 2)
		st2 = stack(near, layers[f"bg_{key}_sky"], layers[f"bg_{key}_far"], layers[f"bg_{key}_mid"], None, shift=0)
		save_png(st2, os.path.join(PREVIEW, f"stack_{tag}_x1.png"), 1)


if __name__ == "__main__":
	built = build()
	os.makedirs(OUT, exist_ok=True)
	for name, canvas in built.items():
		save_png(canvas, os.path.join(OUT, name + ".png"))
		print(name, canvas.w, canvas.h)
	for k, col in FINAL.items():
		print(k, "final", "%02x%02x%02x" % col[:3])
	previews(built)
	# Seam check: columns 511 and 0 must be adjacent-plausible; report solid last row.
	for name, canvas in built.items():
		last = {canvas.get(x, H - 1) for x in range(W)}
		print(name, "last-row colours:", len(last), "top-row empty:", all(canvas.get(x, 0) is None for x in range(W)))

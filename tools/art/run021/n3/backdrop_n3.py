"""N3 Black Forest backdrop layers (RUN-021 aesthetic pass): a primeval night forest under a cold moon.

Writes to assets/run021/n3/:
  bg_n3_sky.png      640x360  opaque, screen-fixed: deep night-blue, sparse cold stars, large cold moon, thin dark clouds
  bg_n3_far.png      640x170  tiling: crag ridges, far fir ridgeline in fog, charcoal-burner kilns + smoke, ruined watchtower
  bg_n3_ridge.png    640x112  tiling: dense wall of fir/spruce tops at middle distance, fog foot dithered to transparent
  bg_n3_mid.png      512x132  tiling: tall trunks (pines, oaks, spruce), standing stones, a camp; opaque ground below
  bg_n3_near.png     512x190  tiling: darkest giant trunks with root flares, hanging moss, ferns; ends on flat FINAL
  bg_n3_<band>_lights.png     same size as the band: kiln embers / fireflies / fungus specks / one camp fire only
  bg_n3_beams.png    512x220  tiling: faint diagonal moonbeam shafts (alpha 20-60, ordered dither on transparency)
and previews to work/run021/n3pass/preview/.

Same method as tools/art/run021/n2/backdrop_n2.py and tools/art/world_bg.py: native 1x pixel art, ordered dither
(no smooth gradients), every x-dependent routine wraps (periodic functions, wrapped puts), deterministic seeded rng.
Usage: python3 tools/art/run021/n3/backdrop_n3.py
"""
import hashlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ART = os.path.join(ROOT, "tools", "art")
sys.path.insert(0, ART)
sys.path.insert(0, os.path.join(ART, "run020"))
sys.path.insert(0, os.path.join(ART, "run020_feedback"))
from pixel import Canvas, hexc, save_png  # noqa: E402
from palette import EMBER  # noqa: E402
from world_bg import dither, dither_band, periodic, rng  # noqa: E402  (read only)
from pngio import load_png  # noqa: E402

OUT = os.path.join(ROOT, "assets", "run021", "n3")
PREVIEW = os.path.join(ROOT, "work", "run021", "n3pass", "preview")

MOON = [hexc(c) for c in ("1c2433", "2a3448", "3e4c66", "5a6c8a", "8496b4", "b8c6dc")]
FIREFLY = [hexc(c) for c in ("2c4a40", "4f7a66", "86b49c", "b4dcc8")]
FINAL = hexc("0a0e11")       # last row of the near band
MID_GROUND = hexc("0d151a")  # bottom rows of the mid band


# ------------------------------------------------------------------ wrapped primitives
def wput(c, x, y, col):
	c.put(x % c.w, y, col)


def wrect(c, x0, y0, w, h, col):
	for y in range(y0, y0 + h):
		for x in range(x0, x0 + w):
			c.put(x % c.w, y, col)


def wclear(c, x0, y0, w, h):
	for y in range(y0, y0 + h):
		if 0 <= y < c.h:
			for x in range(x0, x0 + w):
				c.px[y * c.w + x % c.w] = None


def wline(c, x0, y0, x1, y1, col):
	steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
	for i in range(steps + 1):
		t = i / steps
		wput(c, int(math.floor(x0 + (x1 - x0) * t + 0.5)), int(math.floor(y0 + (y1 - y0) * t + 0.5)), col)


def wdisc(c, cx, cy, r, col):
	for y in range(cy - r, cy + r + 1):
		for x in range(cx - r, cx + r + 1):
			if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.5:
				wput(c, x, y, col)


def wget(c, x, y):
	return c.get(x % c.w, y)


def smoke(c, x, y_base, height, lean, col, w0=1, w1=7, density=0.5, phase=0.0):
	"""Dithered smoke column rising from y_base, leaning with the wind, widening and thinning upward."""
	for i in range(height):
		t = i / height
		y = y_base - i
		cx = x + lean * t + 3.0 * math.sin(t * 7.0 + phase) * t
		hw = w0 + (w1 - w0) * t ** 0.8
		d = density * (1 - t) ** 0.9
		for xx in range(int(cx - hw), int(cx + hw) + 1):
			edge = 1 - abs(xx - cx) / (hw + 0.5)
			if dither(d * (0.35 + 0.65 * edge), xx, y):
				wput(c, xx, y, col)


def fog_over(c, y0, y1, col, dmax, existing_only=False, x0=0, x1=None, t_pow=1.0):
	"""Ordered-dither fog: replaces pixels by `col`, density rising from 0 at y0 to dmax at y1."""
	x1 = c.w if x1 is None else x1
	for y in range(y0, y1):
		t = ((y - y0) / max(1, y1 - y0 - 1)) ** t_pow * dmax
		for x in range(x0, x1):
			if existing_only and c.px[y * c.w + x] is None:
				continue
			if dither(t, x, y):
				c.px[y * c.w + x] = col


def fir(c, cx, base_y, h, hw, col, r, rim=None, tier=(4, 7), lean=0.0, spike=3, droop=0.0):
	"""Spruce / fir: stacked drooping tiers, ragged, pointed top. Right edge may carry a moon-side rim pixel."""
	i = 0
	while i < h:
		T = r.randint(*tier)
		wl, wr = r.uniform(0.88, 1.12), r.uniform(0.88, 1.12)
		for k in range(T):
			if i + k >= h:
				break
			t = (i + k) / h
			prof = hw * (1 - t) ** 0.95
			f = 0.5 + 0.5 * (k / max(1, T - 1))
			cxx = cx + lean * t
			lw = prof * f * wl
			rw = prof * f * wr
			x0, x1 = int(round(cxx - lw)), int(round(cxx + rw))
			y = base_y - (i + k)
			for x in range(x0, x1 + 1):
				wput(c, x, y, col)
			if rim is not None and prof > 1.5 and (y % 2 == 0 or k == T - 1):
				wput(c, x1, y, rim)
			if droop and k == T - 1 and prof > 3:  # drooping tip of the tier
				wput(c, x1 + 1, y + 1, col)
				wput(c, x0 - 1, y + 1, col)
		i += T
	for k in range(spike):
		wput(c, int(round(cx + lean)), base_y - h - k, col)


# ------------------------------------------------------------------ lights
class Lights:
	"""Collects lit spots while the base band is drawn; rendered into a transparent overlay of the same size."""

	def __init__(self, w, h):
		self.w, self.h = w, h
		self.items = []

	def add(self, x, y, kind, w=1, h=1, halo=True):
		self.items.append((x, y, kind, w, h, halo))

	def render(self):
		c = Canvas(self.w, self.h)
		for x, y, kind, w, h, halo in self.items:  # halos first (alpha 70), cores opaque on top
			if not halo:
				continue
			if kind == "flame":
				glow = EMBER[0]
				for yy in range(y - 6, y + h + 3):
					for xx in range(x - 7, x + w + 7):
						d = math.hypot((xx - (x + w / 2.0 - 0.5)) / 1.5, yy - (y + h / 2.0))
						if 1.5 < d <= 6.5 and dither(0.55 * (1 - d / 6.8), xx, yy) and (xx + yy) % 2 == 0:
							wput(c, xx, yy, glow[:3] + (70,))
				continue
			glow = EMBER[0] if kind in ("ember", "spark") else FIREFLY[0]
			for yy in range(y - 1, y + h + 1):
				for xx in range(x - 1, x + w + 1):
					inside = x <= xx < x + w and y <= yy < y + h
					diag = (xx < x or xx >= x + w) and (yy < y or yy >= y + h)
					if not inside and not diag:
						wput(c, xx, yy, glow[:3] + (70,))
		for x, y, kind, w, h, halo in self.items:
			if kind == "flame":
				for yy in range(y, y + h):
					for xx in range(x, x + w):
						k = EMBER[2] if yy < y + h - 1 else EMBER[1]
						if xx == x + w // 2 and yy >= y + 1:
							k = EMBER[3] if yy < y + h - 1 else EMBER[2]
						if h > 2 and (yy == y and xx != x + w // 2):
							continue
						wput(c, xx, yy, k)
				continue
			core = {"ember": EMBER[1], "spark": EMBER[0], "fly": FIREFLY[2], "fungus": FIREFLY[1], "fly_hot": FIREFLY[3]}[kind]
			for yy in range(y, y + h):
				for xx in range(x, x + w):
					wput(c, xx, yy, core)
		return c


def periodic_tops(W, seed, base, amp, terms=4, freq=3):
	f = periodic(W, seed, terms, freq)
	return [int(round(base + amp * f(x))) for x in range(W)]


# ------------------------------------------------------------------ shared tree / terrain helpers
def dxw(x, cx, W):
	return ((x - cx + W // 2) % W) - W // 2


def pen(c, x, y, w, col):
	"""Square pen for w<=2, round pen above."""
	x, y = int(round(x)), int(round(y))
	if w <= 2:
		for yy in range(w):
			for xx in range(w):
				wput(c, x - w // 2 + xx, y - w // 2 + yy, col)
		return
	rr = w / 2.0
	for yy in range(int(math.floor(y - rr)), int(math.ceil(y + rr)) + 1):
		for xx in range(int(math.floor(x - rr)), int(math.ceil(x + rr)) + 1):
			if (xx - x + 0.0) ** 2 + (yy - y + 0.0) ** 2 <= rr * rr + 0.35:
				wput(c, xx, yy, col)


def limb(c, x0, y0, x1, y1, w0, w1, col, bend=0.0):
	"""Tapered, slightly bent limb (quadratic curve) drawn with a round pen."""
	n = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.5) + 2
	mx, my = (x0 + x1) / 2.0 + bend, (y0 + y1) / 2.0 - abs(bend) * 0.4
	for i in range(n + 1):
		t = i / n
		x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1
		y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1
		pen(c, x, y, max(1, int(round(w0 + (w1 - w0) * t))), col)
	return (x1, y1)


def bough(c, x, y, ang, length, w, col, r, depth, spread=0.8, shrink=(0.62, 0.8), ymin=None):
	"""Recursive gnarled branching (wrapped), thick at the root. Limbs never climb above `ymin` (tips end, no cut)."""
	if depth == 0 or length < 3:
		return
	x1 = x + math.cos(ang) * length
	y1 = y + math.sin(ang) * length
	if ymin is not None and y1 < ymin:
		if y - ymin < 3:
			return
		k = (y - ymin) / float(y - y1)
		x1, y1, length = x + (x1 - x) * k, ymin, length * k
	limb(c, x, y, x1, y1, w, max(1, w - 1 if w > 2 else 1), col, bend=r.uniform(-2.5, 2.5))
	for _ in range(r.choice((2, 2, 3))):
		bough(c, x1, y1, ang + r.uniform(-spread, spread), length * r.uniform(*shrink), max(1, w - 1), col, r, depth - 1, spread, shrink, ymin)


def leaf_clump(c, cx, cy, rw, rh, col, col_lt, r):
	"""Ragged dithered foliage mass: dense core, dithered rim, optional lit upper-right edge."""
	ph = r.uniform(0, 6.28)
	for y in range(cy - rh - 3, cy + rh + 4):
		for x in range(cx - rw - 3, cx + rw + 4):
			d = math.hypot((x - cx) / float(rw), (y - cy) / float(rh))
			noise = (math.sin(x * 1.7 + y * 0.9 + ph) + math.sin(x * 0.6 - y * 2.1 + ph)) * 0.07
			if d + noise < 0.78 or (d + noise < 1.12 and dither(1.0 - (d + noise - 0.78) / 0.34, x, y)):
				wput(c, x, y, col)
				if col_lt is not None and (x - cx) / float(rw) * 0.7 - (y - cy) / float(rh) * 0.7 > 0.5 and (x + y) % 2 == 0:
					wput(c, x, y, col_lt)


def moss(c, x, y, length, col, col2, r, phase=0.0, wid=1):
	"""Hanging moss curtain: tapering, swaying, ragged at the tip."""
	for i in range(length):
		xo = int(round(1.3 * math.sin(i * 0.3 + phase)))
		t = i / float(length)
		if t > 0.5 and r.random() < 0.4 * t:
			continue
		w = max(1, int(round(wid * (1 - t))))
		for k in range(w):
			wput(c, x + xo + k - w // 2, y + i, col)
		if t < 0.6 and r.random() < 0.4:
			wput(c, x + xo + w, y + i, col2)


def fern_clump(c, x, y, size, col, col2, r):
	for k in range(r.randint(4, 6)):
		ang = math.radians(-80 + 160 * k / 5.0 + r.uniform(-8, 8))
		L = size * r.uniform(0.7, 1.1)
		for i in range(int(L) + 1):
			t = i / max(1.0, L)
			px = x + math.sin(ang) * L * t
			py = y - math.cos(ang) * L * t + 3.0 * t * t * L / 6.0
			wput(c, int(round(px)), int(round(py)), col)
			if i % 2 == 1 and i < L - 1:
				wput(c, int(round(px)) + 1, int(round(py)) + 1, col2)
				wput(c, int(round(px)) - 1, int(round(py)) + 1, col2)


def rim_pass(c, mapping, y0=0, y1=None, step=2):
	"""Moon-side (right) rim light: a body pixel whose right neighbour is empty becomes its rim colour."""
	y1 = c.h if y1 is None else y1
	hits = []
	for y in range(y0, y1):
		for x in range(c.w):
			p = c.px[y * c.w + x]
			if p in mapping and c.px[y * c.w + (x + 1) % c.w] is None and (x + y) % step == 0:
				hits.append((x, y, mapping[p]))
	for x, y, col in hits:
		c.px[y * c.w + x] = col


def ridged(W, seed, freqs=((3, 1.0), (7, 0.5), (13, 0.28), (29, 0.14), (53, 0.06))):
	"""Wrapped ridged noise in 0..1: sharp crests, soft valleys (crags)."""
	rr = rng("ridged", seed)
	ph = [rr.uniform(0, 6.28) for _ in freqs]
	norm = sum(a for _, a in freqs)
	return lambda x: sum(a * (1 - abs(math.sin(math.pi * f * x / W + p))) for (f, a), p in zip(freqs, ph)) / norm


# ------------------------------------------------------------------ sky
def sky():
	c = Canvas(640, 360)
	stops = [(0, "060912"), (60, "0a0f19"), (125, "0f1623"), (190, "141d2c"), (260, "182333"), (359, "182333")]
	for (y0, a), (y1, b) in zip(stops, stops[1:]):
		dither_band(c, y0, y1 + 1, hexc(a), hexc(b))
	for y in range(150, 300):  # cold horizon veil, sparse and low (mostly hidden behind the forest bands)
		t = 1 - abs(y - 225) / 75.0
		for x in range(640):
			if t > 0 and dither(t * 0.35, x, y) and (x + y) % 2 == 0:
				c.put(x, y, hexc("1a2535"))
	mx, my, rad = 432, 70, 19
	r = rng("n3sky-stars")
	for _ in range(120):
		x, y = r.randint(0, 639), r.randint(0, 190)
		if math.hypot(x - mx, y - my) < rad + 28:
			continue
		k = r.random()
		col = MOON[3] if k < 0.07 else MOON[2] if k < 0.30 else MOON[1] if k < 0.62 else MOON[0]
		c.put(x, y, col)
		if k < 0.025:  # a rare cold twinkle cross
			for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
				c.put(x + dx, y + dy, MOON[0])
	for y in range(my - rad - 28, my + rad + 29):  # halo: dithered rings
		for x in range(mx - rad - 28, mx + rad + 29):
			d = math.hypot(x - mx, y - my)
			if rad < d <= rad + 4 and (x + y) % 2 == 0:
				c.put(x, y, MOON[1])
			elif rad + 4 < d <= rad + 12 and (x + 2 * y) % 4 == 0:
				c.put(x, y, MOON[0])
			elif rad + 12 < d <= rad + 28 and (x + 2 * y) % 8 == 0:
				c.put(x, y, hexc("141c2a"))
	moon_cols = [MOON[0], MOON[1], MOON[2], MOON[3]]  # dimmed one step by the integrator (background contrast); disc lit from the upper right (as the beams and rim lights)
	for y in range(my - rad, my + rad + 1):
		for x in range(mx - rad, mx + rad + 1):
			d = math.hypot(x - mx, y - my)
			if d > rad:
				continue
			nx, ny = (x - mx) / float(rad), (y - my) / float(rad)
			light = 0.62 + 0.42 * (nx * 0.6 - ny * 0.8) - 0.3 * (d / rad) ** 3
			k = 3 if light > 0.9 else 2 if light > 0.52 else 1 if light > 0.2 else 0
			frac = (light % 0.35) / 0.35
			if k < 3 and dither(frac * 0.55, x, y) and 0.2 < light < 0.95:
				k += 1
			c.put(x, y, moon_cols[k])
	for cx, cy, cr in ((mx - 8, my - 4, 6), (mx + 6, my + 6, 4), (mx - 4, my + 11, 3), (mx + 10, my - 10, 3), (mx - 13, my + 4, 3), (mx + 1, my - 3, 2)):
		for y in range(cy - cr, cy + cr + 1):
			for x in range(cx - cr, cx + cr + 1):
				if math.hypot(x - cx, y - cy) <= cr and math.hypot(x - mx, y - my) <= rad - 1:
					base = c.get(x, y)
					lo = moon_cols[max(0, moon_cols.index(base) - 1)] if base in moon_cols else MOON[1]
					c.put(x, y, lo if dither(0.7, x, y) else base)
	for y in range(my - rad, my + rad + 1):  # bright limb glint, a few pixels only
		for x in range(mx - rad, mx + rad + 1):
			d = math.hypot(x - mx, y - my)
			if rad - 1.6 < d <= rad and (x - mx) * 0.6 - (y - my) * 0.8 > rad * 0.78 and (x + y) % 2 == 0:
				c.put(x, y, MOON[4])
	# High thin dark cloud streaks: tapered lenses with dithered rims, soft against the sky.
	streaks = [(my + 12, mx - 58, mx + 46, 2.0, 0.03), (46, 40, 190, 2.0, 0.04), (92, 150, 330, 2.4, -0.03), (20, 470, 628, 1.8, 0.04),
		(118, 500, 640, 2.2, -0.04), (140, 10, 120, 1.6, 0.02), (28, 250, 380, 1.4, -0.02)]
	for sy, x0, x1, th, tilt in streaks:
		for x in range(x0, x1 + 1):
			t = (x - x0) / float(x1 - x0)
			wob = math.sin(t * 7.0 + sy) * 0.7
			thick = th * math.sin(math.pi * t) ** 0.85
			cy = sy + (x - (x0 + x1) / 2.0) * tilt + wob
			for y in range(int(cy - thick - 1), int(cy + thick + 2)):
				dy = abs(y - cy)
				if dy > thick:
					continue
				on_moon = (x - mx) ** 2 + (y - my) ** 2 < (rad + 1) ** 2
				core = dy < thick - 0.9
				if core or dither(0.5, x, y):
					if on_moon:
						c.put(x, y, hexc("2a3448") if core else hexc("3e4c66"))
					else:
						c.put(x, y, hexc("05080e") if core else hexc("0a0f19"))
	return c


# ------------------------------------------------------------------ ridge: wall of fir tops at middle distance
RIDGE_W, RIDGE_H = 640, 112
RIDGE = {"back": hexc("12222a"), "mid": hexc("0f1d25"), "front": hexc("0b171d"), "fog": hexc("16262c"), "rim": hexc("182a2c"), "rim2": hexc("152529")}
VALLEYS = [88, 250, 420, 566]  # clearings where the ridge canopy dips: the far kilns show here


def ridge_top_fn():
	f = periodic(RIDGE_W, "n3ridge-top", 4, 3)

	def T(x):
		v = 20 + 9 * f(x)
		for vx in VALLEYS:
			v += 17 * math.exp(-(dxw(x, vx, RIDGE_W) / 30.0) ** 2)
		return v
	return T


def snag(c, x, base, h, col, r, w=2):
	for y in range(base - h, base + 2):
		t = (y - (base - h)) / float(h)
		ww = 1 if t < 0.4 else w
		for k in range(ww):
			wput(c, x - ww // 2 + k, y, col)
	for k in range(3 + h // 14):
		by = base - h + 3 + k * max(5, h // 5)
		side = 1 if k % 2 == 0 else -1
		bough(c, x, by, -math.pi / 2 + side * r.uniform(0.8, 1.2), r.randint(5, 8 + h // 8), 1, col, r, 2, 0.5)


def ridge_build():
	W, H = RIDGE_W, RIDGE_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n3ridge-v2")
	P = RIDGE
	T = ridge_top_fn()

	def row(base, hmin, step, offs, jit, col, rimcol, tier, hw_f, oak_p, snag_p, gap_p):
		x = r.randint(0, 6)
		while x < W:
			if r.random() < gap_p:
				x += r.randint(7, 14)
				continue
			top = int(T(x)) + offs + r.randint(-jit, jit)
			h = max(hmin, base - top)
			k = r.random()
			if k < oak_p:
				rw = r.randint(8, 13)
				wrect(c, x - 1, base - 12, 3, 14, col)
				for dx in (-rw // 2, 0, rw // 2):
					leaf_clump(c, x + dx, base - 13 - r.randint(0, 5), rw // 2 + 2, r.randint(5, 8), col, None, r)
			elif k < oak_p + snag_p:
				snag(c, x, base, min(h, 40), col, r)
			else:
				hw = max(4, min(12, int(h * r.uniform(hw_f[0], hw_f[1]))))
				fir(c, x, base, h, hw, col, r, tier=tier, droop=1.0, lean=r.choice((-1.0, 0.0, 0.0, 1.0)))
			x += r.randint(*step)

	row(62, 18, (7, 14), 0, 8, P["back"], P["rim2"], (4, 7), (0.2, 0.3), 0.0, 0.07, 0.05)
	fog_over(c, 44, 66, P["fog"], 0.85, existing_only=True)
	row(74, 14, (6, 12), 12, 7, P["mid"], P["rim"], (3, 6), (0.2, 0.32), 0.14, 0.04, 0.05)
	fog_over(c, 58, 78, P["fog"], 0.7, existing_only=True)
	row(86, 10, (5, 9), 24, 6, P["front"], P["rim2"], (3, 5), (0.22, 0.34), 0.06, 0.0, 0.0)
	for x in range(W):  # solid forest mass under the tree lines
		for y in range(66, 88):
			if c.px[y * W + x] is None:
				c.px[y * W + x] = P["front"]
	rim_pass(c, {P["back"]: P["rim2"], P["mid"]: P["rim"], P["front"]: P["rim2"]}, 0, 70, 2)
	fog_over(c, 74, 88, P["fog"], 0.55, existing_only=True)
	for y in range(62, H):  # fade the foot by ordered dither into transparency
		t = min(1.0, (y - 62) / 25.0)
		for x in range(W):
			if c.px[y * W + x] is not None and dither(t, x, y):
				c.px[y * W + x] = None
	for x in range(W):
		for y in range(88, H):
			c.px[y * W + x] = None
	rl = rng("n3ridge-fly")
	for _ in range(5):
		lights.add(rl.randint(0, W - 1), rl.randint(54, 76), "fly", 1, 1, True)
	return c, lights.render()


# ------------------------------------------------------------------ far: crags, fir ridgeline in fog, kilns, a watchtower
FAR_W, FAR_H = 640, 170
FAR = {
	"A": hexc("142030"), "A_lit": hexc("162331"), "A_fog": hexc("152231"),
	"B": hexc("0f1925"), "B_lit": hexc("14212d"),
	"fog": hexc("132030"), "forest": hexc("0b131c"), "forest_rim": hexc("101a24"), "ground": hexc("09101a"),
	"tower": hexc("0a1119"), "tower_rim": hexc("111b26"), "smoke": hexc("172230"), "kiln": hexc("080e15"), "turf": hexc("0d1620"),
}


def far_build(ridge):
	W, H = FAR_W, FAR_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n3far-v2")
	P = FAR
	rtop = []
	for x in range(W):  # canopy line of the ridge band, in far-row units (ridge drawn at y120, far at y58)
		t = 99
		for y in range(ridge.h):
			if ridge.px[y * W + x] is not None:
				t = y
				break
		rtop.append(t + 62)
	# 1. Far crags A: ridged noise, faceted; right-facing faces catch the moonlight.
	fA = ridged(W, "A")
	topA = [max(5, int(round(84 - 84 * fA(x) ** 1.1))) for x in range(W)]
	for x in range(W):
		sl = topA[(x + 2) % W] - topA[(x - 2) % W]
		for y in range(topA[x], H):
			col = P["A"]
			depth = y - topA[x]
			if sl > 0 and depth < 3 + sl * 2.0 and (depth < 2 or (x + y) % 2 == 0):
				col = P["A_lit"]
			wput(c, x, y, col)
	fog_over(c, 50, 92, P["A_fog"], 0.9, existing_only=True)
	# 2. Crags B (darker, nearer), with a watchtower on its highest crag.
	fB = ridged(W, "B", ((2, 1.0), (5, 0.6), (11, 0.35), (23, 0.18), (47, 0.08)))
	topB = [max(24, int(round(100 - 66 * fB(x) ** 1.2))) for x in range(W)]
	tx = min(range(200, 260), key=lambda x: topB[x])
	for x in range(tx - 4, tx + 5):  # level the crag top under the tower
		topB[x % W] = topB[tx] + 1
	for x in range(W):
		sl = topB[(x + 2) % W] - topB[(x - 2) % W]
		for y in range(topB[x], H):
			col = P["B"]
			depth = y - topB[x]
			if sl > 0 and depth < 2 + sl * 1.8 and (x + y) % 2 == 0:
				col = P["B_lit"]
			wput(c, x, y, col)
	fog_over(c, 68, 100, P["fog"], 0.85, existing_only=True)
	tb = topB[tx] + 2  # watchtower: slim square keep, broken crown, a stub of curtain wall to the left
	for yy in range(tb - 24, tb + 1):
		wrect(c, tx - 3, yy, 7, 1, P["tower"])
	for xx in range(tx - 3, tx + 4):
		wrect(c, xx, tb - 24 - ((xx * 5 + 1) % 4), 1, (xx * 5 + 1) % 4, P["tower"])
	wrect(c, tx + 1, tb - 24 - 6, 1, 3, P["tower"])  # a remaining beam
	wrect(c, tx, tb - 16, 1, 3, P["B"])  # dark window slit
	wrect(c, tx - 3, tb - 12, 2, 1, P["B"])
	for i in range(16):  # ruined curtain wall stepping down the crag to the left, ragged
		hh = max(2, 9 - i // 2 - ((i * 5) % 3))
		wrect(c, tx - 4 - i, tb - hh + 2, 1, hh, P["tower"])
	for i in range(8):  # rubble at the foot
		wput(c, tx + 4 + i, tb - ((i * 3) % 3), P["tower"])
	# 3. Far fir ridgeline (tiny firs) with clearings where the charcoal kilns smoke.
	fl_f = periodic(W, "n3far-fl", 3, 3)
	ground_line = [int(round(80 + 5 * fl_f(x))) for x in range(W)]
	kilns = list(VALLEYS)
	kil_base = {}
	for kx in kilns:
		span = min(rtop[(kx + k) % W] for k in range(-9, 10))
		kil_base[kx] = span - 3
		for x in range(kx - 30, kx + 31):
			w = math.exp(-(dxw(x, kx, W) / 17.0) ** 2)
			ground_line[x % W] = int(round(ground_line[x % W] * (1 - w) + (span - 3) * w))
	for x in range(W):
		for y in range(ground_line[x], H):
			wput(c, x, y, P["forest"])
	x = 0
	while x < W:
		gx = ground_line[x % W]
		if not any(abs(dxw(x, kx, W)) < 12 for kx in kilns):
			fir(c, x, gx + 2, r.randint(8, 18), r.randint(2, 4), P["forest"], r, tier=(3, 4), spike=2)
		x += r.randint(3, 6)
	rim_pass(c, {P["forest"]: P["forest_rim"]}, 60, 100, 2)
	fog_over(c, 74, 120, P["fog"], 0.55, existing_only=True)
	for x in range(W):  # darker ground below the ridgeline mist; bottom rows opaque
		for y in range(112, H):
			if dither((y - 112) / 22.0, x, y):
				wput(c, x, y, P["ground"])
	for x in range(W):
		for y in range(134, H):
			wput(c, x, y, P["ground"])
	# 4. Charcoal-burner kilns: turf beehive, vent, log piles and a thin smoke column leaning left with the wind.
	for i, kx in enumerate(kilns):
		b = kil_base[kx]
		for dx in range(-7, 8):
			hgt = int(round(6.0 * math.sqrt(max(0.0, 1 - (dx / 7.5) ** 2))))
			wrect(c, kx + dx, b - hgt + 1, 1, hgt + 3, P["kiln"])
		for k in range(-5, 6, 2):  # turf strips
			wput(c, kx + k, b - 3 + (abs(k) // 3), P["turf"])
		for k in range(4):  # moon-side rim
			wput(c, kx + 5 - k // 2, b - 2 - k, P["forest_rim"])
		wput(c, kx, b - 6, P["kiln"])
		wrect(c, kx + 9, b - 1, 5, 2, P["kiln"])  # log pile
		wrect(c, kx - 13, b - 1, 4, 2, P["kiln"])
		smoke(c, kx, b - 7, 62 + 8 * (i % 2), -12 - 4 * (i % 3), P["smoke"], 2, 7, 0.95, phase=kx * 0.1)
		lights.add(kx, b - 6, "ember", 1, 1, True)
		lights.add(kx - 3 + (i % 2) * 6, b - 3, "spark", 1, 1, False)
		if i % 2 == 0:
			lights.add(kx - 1, b - 13 - i, "spark", 1, 1, False)
	return c, lights.render()


# ------------------------------------------------------------------ mid: tall trunks, oaks, standing stones, a camp
MID_W, MID_H = 512, 132
MID = {
	"trunk": hexc("091215"), "trunk_b": hexc("0b1417"), "trunk_f": hexc("0d181c"), "dark": hexc("060b0d"),
	"rim": hexc("192a2e"), "rim_f": hexc("14242a"), "leaf": hexc("091315"), "leaf_f": hexc("0c171b"), "leaf_lt": hexc("132428"),
	"moss": hexc("0d1a16"), "stone": hexc("17232a"), "stone_rim": hexc("1e2c2e"), "stone_dk": hexc("0f1a20"),
	"ground": MID_GROUND, "gline": hexc("142026"), "fog": hexc("13222a"), "cloth": hexc("0a1315"), "cloth_lt": hexc("14232a"),
}


def trunk_col(c, cx, y0, y1, w0, w1, col, lean=0.0, wob=0.0, ph=0.0):
	"""Vertical tapered trunk from y0 (top, width w0) to y1 (base, width w1)."""
	for y in range(y0, y1 + 1):
		t = (y - y0) / float(max(1, y1 - y0))
		w = max(1, int(round(w0 + (w1 - w0) * t ** 1.2)))
		xc = cx + lean * (1 - t) + wob * math.sin(y * 0.11 + ph)
		xs = int(round(xc - w / 2.0))
		for k in range(w):
			wput(c, xs + k, y, col)


def tall_fir(c, cx, gy, h, hw, col, leaf, r, bare=0.3, lean=0.0, tier=(5, 8)):
	"""Tall spruce on a bare trunk with dead stubs, foliage from `bare` of the height up."""
	b = int(h * bare)
	trunk_col(c, cx, gy - b - 4, gy + 2, 2, 4 if hw > 8 else 3, col, lean=0.0)
	for k in range(b // 6):
		by = gy - 5 - k * 6 - r.randint(0, 2)
		side = 1 if k % 2 == 0 else -1
		for i in range(r.randint(2, 4)):
			wput(c, cx + side * (2 + i), by - i // 2, col)
	fir(c, cx, gy - b, h - b, hw, leaf, r, tier=tier, droop=1.0, spike=4, lean=lean)


def crown_pine(c, cx, gy, h, tw, col, leaf, r, lean=0.0):
	"""Old pine: long bare trunk with a few dead stubs, and a ragged, irregular crown of overlapping foliage pads."""
	top = gy - h
	trunk_col(c, cx, top, gy + 2, 2, tw, col, lean=lean, wob=1.0, ph=cx)
	for k in range(h // 14):  # dead stubs on the bare trunk
		by = gy - 8 - k * 9 - r.randint(0, 3)
		side = 1 if k % 2 == 0 else -1
		for i in range(r.randint(2, 4)):
			wput(c, cx + side * (2 + i), by - i // 2, col)
	crown_h = int(h * 0.42)
	for k in range(7):
		t = k / 6.0
		by = top + int(t * crown_h)
		xb = int(round(cx + lean * (1 - (by - top) / float(h))))
		for side in (-1, 1):
			if r.random() < 0.85:
				ln = int(5 + 9 * t) + r.randint(-1, 2)
				dy = 1 + int(t * 3)
				limb(c, xb, by, xb + side * ln, by + dy, 2, 1, col)
				leaf_clump(c, xb + side * ln, by + dy - 1, int(5 + 5 * t), 3 + int(t * 2), leaf, None, r)
	leaf_clump(c, int(round(cx + lean)), top + 3, 6, 6, leaf, None, r)
	wput(c, int(round(cx + lean)), top - 4, leaf)
	wput(c, int(round(cx + lean)), top - 5, leaf)


def oak(c, ox, base, oh, ow, col, leaf, r, P):
	"""Ancient oak: thick root-flared trunk, wide dense crown of leaf masses with sky gaps, hanging moss."""
	for y in range(base - oh, base + 2):
		t = (y - (base - oh)) / float(oh)
		w = ow - 2 + int(round(2 * t)) + (int(5 * ((t - 0.82) / 0.18) ** 2) if t > 0.82 else 0)
		xs = ox - w // 2 + (1 if (y // 9) % 2 else 0)
		for k in range(w):
			wput(c, xs + k, y, col)
	for ang, ln, bw in ((-2.5, 20, 4), (-0.65, 22, 4), (-1.6, 18, 4), (-3.1, 12, 3), (0.0, 12, 3)):
		bough(c, ox + (2 if math.cos(ang) > 0 else -2), base - oh + 6, ang, ln, bw, col, r, 3, 0.6)
	cy0 = base - oh - 2
	for k in range(8):
		leaf_clump(c, ox + int(r.uniform(-1, 1) * ow * 1.9), cy0 + r.randint(-6, 8), r.randint(12, 18), r.randint(7, 10), leaf, P["leaf_lt"] if k % 3 == 0 else None, r)
	for k in range(5):  # sky gaps inside the crown
		wclear(c, ox + r.randint(-int(ow * 1.6), int(ow * 1.6)), cy0 + r.randint(-3, 7), r.randint(2, 4), r.randint(1, 2))
	for k in range(11):  # hanging moss under the crown
		mxx = ox + r.randint(-int(ow * 2.0), int(ow * 2.0))
		moss(c, mxx, cy0 + r.randint(6, 14), r.randint(8, 22), P["moss"], P["leaf"], r, phase=mxx, wid=2)
	for side in (-1, 1):  # roots
		for i in range(9):
			wput(c, ox + side * (ow // 2 + 1 + i), base - 1 + i // 4 - (1 if i < 3 else 0), col)
			wput(c, ox + side * (ow // 2 + 1 + i), base - 2 + i // 4 - (1 if i < 3 else 0), col)


def standing_stone(c, cx, gy, h, w, lean, P):
	"""Menhir: leaning rough slab, chipped angled top; no face-like features."""
	for yy in range(h):
		t = yy / float(h)
		hw = w / 2.0 * (0.62 + 0.38 * t ** 0.7)
		xc = cx + lean * (1 - t)
		x0, x1 = int(round(xc - hw)), int(round(xc + hw))
		if yy > h - 4 and (x1 - x0) > 2 and ((x0 + yy) % 3 == 0):
			x1 -= 1
		for x in range(x0, x1 + 1):
			col = P["stone"]
			if x == x0 and w >= 4:
				col = P["stone_dk"]
			wput(c, x, gy - yy, col)
	for k in range(3):
		wput(c, cx - 1 + k, gy - h // 2 + k * 2, P["stone_dk"])
	wrect(c, cx - w // 2 - 1, gy - 1, w + 2, 2, P["stone_dk"])


def snag_mid(c, x, base, h, P, r):
	trunk_col(c, x, base - h, base + 1, 2, 5, P["trunk"], wob=1.2, ph=x)
	for k in range(4):
		by = base - h + 6 + k * 9
		side = 1 if k % 2 == 0 else -1
		bough(c, x, by, -math.pi / 2 + side * r.uniform(0.9, 1.3), r.randint(9, 15), 3, P["trunk"], r, 3, 0.6)


def mid_build():
	W, H = MID_W, MID_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n3mid-v2")
	P = MID
	f = periodic(W, "n3mid-ground", 3, 3)
	gy = [104 + int(round(1.5 * f(x))) for x in range(W)]

	def g(x):
		return gy[x % W]

	for x in range(W):
		for y in range(gy[x], H):
			c.put(x, y, P["ground"])
	# back tone (lighter, further): spruces and pines, drawn first
	for x, h, hw in ((22, 72, 11), (146, 66, 10), (236, 78, 12), (338, 68, 11), (420, 74, 12), (498, 62, 10)):
		tall_fir(c, x, g(x) + 1, h, hw, P["trunk_f"], P["leaf_f"], r, bare=0.3, lean=r.choice((-1.5, 0, 1.5)))
	for x, h, tw in ((60, 90, 4), (198, 94, 4), (290, 88, 3), (376, 98, 4), (462, 86, 4)):
		crown_pine(c, x, g(x) + 1, h, tw, P["trunk_f"], P["leaf_f"], r, lean=r.choice((-2, -1, 1, 2)))
	# standing stones: a small cult circle and two lone menhirs
	for sx, sh, sw, sl in ((118, 26, 7, -2), (130, 34, 8, 1), (143, 22, 6, 2), (156, 29, 7, -1)):
		standing_stone(c, sx, g(sx) + 1, sh, sw, sl, P)
	for i in range(15):  # fallen lintel, low and ragged
		wput(c, 120 + i, g(120) - 20 + i // 4 - (1 if i % 5 == 0 else 0), P["stone_dk"])
		wput(c, 120 + i, g(120) - 21 + i // 4, P["stone"])
	standing_stone(c, 478, g(478) + 1, 30, 8, -2, P)
	standing_stone(c, 322, g(322) + 1, 18, 7, 2, P)
	# front tone: big old trees
	for ox, oh, ow in ((98, 56, 9), (264, 52, 8), (440, 54, 9)):
		oak(c, ox, g(ox) + 2, oh, ow, P["trunk"], P["leaf"], r, P)
	for x, h, hw in ((42, 84, 11), (214, 88, 12), (372, 82, 11)):
		tall_fir(c, x, g(x) + 2, h, hw, P["trunk"], P["leaf"], r, bare=0.28, lean=r.choice((-1.5, 1.5)), tier=(5, 8))
	for x, h, tw in ((8, 96, 5), (190, 104, 6), (312, 94, 5), (404, 100, 5), (498, 88, 5)):
		crown_pine(c, x, g(x) + 2, h, tw, P["trunk"], P["leaf"], r, lean=r.choice((-2, -1, 1, 2)))
	for tx, hgt in ((26, 46), (388, 40)):
		snag_mid(c, tx, g(tx) + 2, hgt, P, r)
	# charcoal-burner camp: A-frame tent, drying rack, a small fire pit
	cx0 = 300
	gyc = g(cx0)
	for i in range(12):
		hw = 9 * (1 - i / 12.0)
		for x in range(int(round(cx0 - hw)), int(round(cx0 + hw)) + 1):
			col = P["cloth"]
			if x >= cx0 + hw - 1 and i > 1:
				col = P["cloth_lt"]
			wput(c, x, gyc - i, col)
	wrect(c, cx0 - 1, gyc - 6, 2, 6, P["dark"])
	wrect(c, cx0, gyc - 14, 1, 3, P["trunk"])
	for dx in (14, 21):
		wrect(c, cx0 + dx - 1, gyc - 1, 2, 2, P["stone"])
	wrect(c, cx0 + 15, gyc - 1, 5, 1, P["dark"])
	wput(c, cx0 + 17, gyc - 2, P["dark"])
	lights.add(cx0 + 17, gyc - 5, "flame", 2, 4, True)
	for k in range(2):
		wline(c, cx0 - 21 + k * 7, gyc, cx0 - 16 + k * 7, gyc - 13, P["trunk"])
	wline(c, cx0 - 18, gyc - 10, cx0 - 8, gyc - 10, P["trunk"])
	# undergrowth along the ground: young firs, ferns, low deadfall
	x = r.randint(0, 8)
	while x < W:
		if not (cx0 - 24 < x < cx0 + 26):
			fir(c, x, g(x) + 3, r.randint(14, 26), r.randint(4, 6), P["trunk"], r, tier=(3, 5), spike=2)
		x += r.randint(11, 22)
	for _ in range(40):
		x = r.randint(0, W - 1)
		if not (cx0 - 24 < x < cx0 + 26):
			fern_clump(c, x, g(x) + 1, r.randint(5, 9), P["leaf"], P["moss"], r)
	for _ in range(12):
		x = r.randint(0, W - 1)
		ln = r.randint(9, 18)
		for i in range(ln):
			wput(c, x + i, g(x + i) - 1 - (i // 6) + (1 if (i * 7) % 3 == 0 else 0), P["trunk_b"])
			wput(c, x + i, g(x + i) - (i // 6), P["trunk_b"])
	rim_pass(c, {P["trunk"]: P["rim"], P["trunk_f"]: P["rim_f"], P["stone"]: P["stone_rim"], P["leaf"]: P["rim_f"], P["leaf_f"]: P["rim_f"]}, 0, 100, 2)
	for x in range(W):  # ground fog bank: dithered, denser toward the ground line
		for y in range(g(x) - 20, g(x) + 1):
			t = (y - (g(x) - 20)) / 20.0
			if dither(0.3 * t ** 1.4, x, y) and (x + y) % 2 == 0:
				c.put(x, y, P["fog"])
	for x in range(W):  # ground crust line and specks; the bottom rows stay flat
		if r.random() < 0.55:
			c.put(x, gy[x], P["gline"])
	for _ in range(420):
		x, y = r.randint(0, W - 1), r.randint(100, 114)
		if c.get(x, y) == P["ground"] and y >= gy[x] + 2 and r.random() < 1.0 - (y - 104) / 12.0:
			c.put(x, y, P["gline"] if r.random() < 0.5 else P["trunk_b"])
	rl = rng("n3mid-fly")
	for _ in range(9):
		lights.add(rl.randint(0, W - 1), rl.randint(60, 98), "fly", 1, 1, True)
	for _ in range(6):
		x = rl.randint(0, W - 1)
		lights.add(x, g(x) - rl.randint(1, 4), "fungus", 1, 1, False)
	return c, lights.render()


# ------------------------------------------------------------------ near: darkest giant trunks, roots, moss, ferns
NEAR_W, NEAR_H = 512, 190
NEAR = {"body": hexc("070b0e"), "shade": hexc("050709"), "edge": hexc("0f171b"), "moss": hexc("0a1411"), "moss_lt": hexc("0f1b17"),
	"ground": hexc("0b1114"), "bark": hexc("0a1013")}


def near_trunk(c, cx, gyb, top_y, w_top, w_base, flare, r, ph, fh=30):
	P = NEAR
	for y in range(top_y, gyb + 10):
		t = (y - top_y) / float(gyb - top_y)
		w = w_top + (w_base - w_top) * t ** 1.4
		if y < top_y + 14:  # rounded shoulder where the trunk splits into limbs
			w *= math.sqrt((y - top_y + 1) / 15.0)
		ff = max(0.0, (y - (gyb - fh)) / float(fh)) ** 2.0
		wob = 2.2 * math.sin(y * 0.04 + ph) + 1.2 * math.sin(y * 0.1 + ph * 2) + (0.8 if (y // 5) % 2 else 0)
		cxx = cx + wob
		left = int(round(cxx - w / 2.0 - flare * ff))
		right = int(round(cxx + w / 2.0 + flare * ff))
		for x in range(left, right + 1):
			wput(c, x, y, P["shade"] if x <= left + 1 else P["body"])
		k = 0
		for gx in range(left + 4, right - 3, 5 + int(ph > 3)):  # broken vertical bark seams
			if (y // 7 + k + int(ph * 3)) % 3 != 0:
				wput(c, gx + int(1.2 * math.sin(y * 0.3 + k)), y, P["shade"])
			k += 1
	# knot holes
	for _ in range(2):
		ky = r.randint(top_y + 30, max(top_y + 31, gyb - 40))
		kx = cx + r.randint(-int(w_top * 0.2), int(w_top * 0.2))
		for yy in range(-3, 4):
			for xx in range(-2, 3):
				if (xx / 2.2) ** 2 + (yy / 3.4) ** 2 <= 1:
					wput(c, kx + xx, ky + yy, P["shade"])


def root(c, x0, y0, dirn, length, w0, col, r):
	"""Root crawling out of a trunk base and sinking into the ground."""
	px, py = float(x0), float(y0)
	for i in range(length):
		t = i / float(length)
		px += dirn * (1.0 + 0.4 * (1 - t))
		py += 0.25 + 0.9 * t ** 1.6 + r.uniform(-0.1, 0.1)
		w = max(1, int(round(w0 * (1 - t) + 1)))
		for k in range(w):
			wput(c, int(round(px)), int(round(py)) - k, col)


def near_build():
	W, H = NEAR_W, NEAR_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n3near-v2")
	P = NEAR
	f = periodic(W, "n3near-ground", 3, 3)
	tops = [100 + int(round(3 * f(x))) for x in range(W)]

	def g(x):
		return tops[x % W]

	for x in range(W):
		for y in range(tops[x], H):
			c.put(x, y, P["ground"])
	# (cx, top row, width at top, width at base, flare, phase)
	trunks = [(40, 44, 18, 30, 8, 1.0), (166, 36, 24, 40, 10, 2.3), (268, 58, 14, 24, 7, 3.6), (392, 40, 22, 36, 9, 5.0)]
	for cx, ty, wt, wb, fl, ph in trunks:
		near_trunk(c, cx, g(cx), ty, wt, wb, fl, r, ph)
	# Crowns: each trunk forks into gnarled limbs that rise, taper and end below row 12 (nothing is cut flat).
	crowns = {40: [(-0.75, 26), (0.3, 32)], 166: [(-0.55, 16), (0.45, 20)], 268: [(-0.8, 24), (-0.2, 28), (0.35, 26), (0.85, 22)], 392: [(-0.5, 30), (0.15, 20), (0.75, 24)]}
	for cx, ty, wt, wb, fl, ph in trunks:
		for da, ln in crowns[cx]:
			ang = -math.pi / 2 + da
			bough(c, cx + int(da * wt * 0.35), ty + 9, ang, ln, max(4, wt // 3 + (3 if cx == 166 else 0)), P["body"], r, 4 if cx != 166 else 2, 0.55, (0.7, 0.85), ymin=12)
	# Great rising limbs reaching out from each trunk, drooping at the tip, with moss curtains under them.
	reach = [(40, -1, 62, 52), (40, 1, 76, 56), (166, -1, 84, 70), (166, 1, 70, 54), (268, -1, 66, 46), (268, 1, 90, 62), (392, -1, 74, 58), (392, 1, 80, 60)]
	for cx, side, y0, ln in reach:
		x0 = cx + side * 12
		x1 = cx + side * (12 + ln)
		y1 = y0 - r.randint(14, 24)
		limb(c, x0, y0, x1, y1, 8, 2, P["body"], bend=side * 6 * 1.0)
		limb(c, x1, y1, x1 + side * 8, y1 + 10, 2, 1, P["body"], bend=side * 2)
		for k in range(4):
			t = r.uniform(0.2, 0.95)
			mxx = int(x0 + (x1 - x0) * t)
			myy = int(y0 + (y1 - y0) * t + 5)
			moss(c, mxx, myy, r.randint(10, 36), P["moss"], P["moss_lt"], r, phase=mxx * 0.3, wid=3)
	# Side limbs, snapped stubs and moss beards on the trunks.
	for cx, ty, wt, wb, fl, ph in trunks:
		for k in range(3):
			by = r.randint(ty + 22, ty + 54)
			side = r.choice((-1, 1))
			ln = r.randint(10, 20)
			limb(c, cx + side * (wt // 2), by, cx + side * (wt // 2 + ln), by - r.randint(-4, 8), 5, 1, P["body"], bend=r.uniform(-3, 3))
			moss(c, cx + side * (wt // 2 + ln // 2), by + 2, r.randint(10, 26), P["moss"], P["moss_lt"], r, phase=by, wid=3)
		for k in range(3):
			by = r.randint(ty + 30, 92)
			moss(c, cx + r.choice((-1, 1)) * (wt // 2 + 1), by, r.randint(6, 14), P["moss"], P["moss_lt"], r, phase=by, wid=2)
	for cx, ty, wt, wb, fl, ph in trunks:  # big roots out of each trunk base
		gb = g(cx)
		root(c, cx - wb // 2 - fl // 2 + 2, gb - 18, -1, 26 + r.randint(0, 8), 7, P["body"], r)
		root(c, cx + wb // 2 + fl // 2 - 2, gb - 16, 1, 28 + r.randint(0, 8), 7, P["body"], r)
		root(c, cx - wb // 2 - 2, gb - 6, -1, 14, 4, P["body"], r)
		root(c, cx + wb // 2 + 2, gb - 5, 1, 16, 4, P["body"], r)
	for bx, bw, bh in ((100, 16, 7), (222, 20, 8), (330, 14, 6), (470, 18, 7)):  # mossy knuckles half buried
		for x in range(bx - bw // 2, bx + bw // 2 + 1):
			hh = int(round(bh * math.sqrt(max(0.0, 1 - ((x - bx) / (bw / 2.0 + 0.5)) ** 2))))
			for y in range(g(x) - hh, g(x) + 2):
				wput(c, x, y, P["body"])
			if hh > 2:
				wput(c, x, g(x) - hh, P["moss"])
	for _ in range(30):
		x = r.randint(0, W - 1)
		fern_clump(c, x, g(x) + 1, r.randint(9, 18), P["body"], P["moss"], r)
	for _ in range(60):
		x = r.randint(0, W - 1)
		hh = r.randint(3, 8)
		for i in range(hh):
			wput(c, x + (i // 4) * r.choice((-1, 0, 1)), g(x) - i, P["moss"] if i < hh - 1 else P["body"])
	wclear(c, 0, 0, W, 8)
	rim_pass(c, {P["body"]: P["edge"]}, 0, 110, 2)
	fade_from = max(tops) + 18
	dither_band(c, fade_from, H - 6, P["ground"], FINAL)
	for y in range(H - 6, H):
		for x in range(W):
			c.put(x, y, FINAL)
	rl = rng("n3near-fly")
	for _ in range(5):
		lights.add(rl.randint(0, W - 1), rl.randint(40, 92), "fly", 1, 1, True)
	for k, (cx, ty, wt, wb, fl, ph) in enumerate(trunks[1::2]):
		for q in range(3):
			lights.add(cx + (wb // 2 + 6 + q * 3) * (1 if k == 0 else -1), g(cx) - 8 + q, "fungus", 1, 1, False)
	return c, lights.render()


# ------------------------------------------------------------------ beams: soft moonbeam shafts
BEAM_W, BEAM_H = 512, 220


def beams():
	W, H = BEAM_W, BEAM_H
	c = Canvas(W, H)
	# (x at top, width at top, width at bottom, strength): slanted down-left (the moon is up and to the right).
	shafts = [(90, 18, 30, 1.0), (205, 10, 16, 0.75), (300, 26, 40, 0.9), (390, 8, 12, 0.6), (468, 16, 26, 0.85)]
	slope = 0.42
	inten = [[0.0] * W for _ in range(H)]
	for sx, w0, w1, st in shafts:
		ph = sx * 0.07
		for y in range(H):
			t = y / float(H)
			center = sx - slope * y
			half = (w0 + (w1 - w0) * t) / 2.0
			vfade = st * (1 - t) ** 1.25 * min(1.0, 0.08 + y / 80.0)
			vmod = 0.82 + 0.18 * math.sin(y * 0.09 + ph) + 0.08 * math.sin(y * 0.31 + ph * 3)
			for x in range(int(center - half - 2), int(center + half + 3)):
				d = abs(x - center) / half
				if d >= 1.0:
					continue
				prof = 1 - d * d
				if d < 0.35 and (y // 5 + int(sx)) % 4 == 0:
					prof *= 0.78
				inten[y][x % W] = min(1.0, inten[y][x % W] + prof * vfade * vmod)
	levels = [20, 38, 56]
	for y in range(H):
		for x in range(W):
			s = inten[y][x] * 3.7
			if s < 0.25:
				continue
			k = int(s)
			if k < 3 and dither(s - k, x, y):
				k += 1
			if k == 0:
				continue
			c.px[y * W + x] = MOON[3][:3] + (levels[min(3, k) - 1],)
	return c


# ------------------------------------------------------------------ build / previews
def mist_overlay():
	"""Approximation of the N1 mist strip (assets/sprites/bg_mist.png) tinted cold for the preview only."""
	try:
		m = load_png(os.path.join(ROOT, "assets", "sprites", "bg_mist.png"))
	except Exception:
		return None
	for i, p in enumerate(m.px):
		if p is not None:
			m.px[i] = (34, 52, 66, max(1, p[3] // 2))
	return m


def stack(layers, sky_c, lit=None, terrain=False, with_beams=None, mist=None):
	"""Approximate in-game stacking at the reference framing (camera x 0)."""
	c = Canvas(640, 360)
	c.blit(sky_c, 0, 0)
	far, ridge, mid, near = layers["far"], layers["ridge"], layers["mid"], layers["near"]

	def tile(img, y, x_off=0):
		for k in range(-1, 640 // img.w + 2):
			c.blit(img, k * img.w + x_off, y)

	tile(far, 58)
	if lit:
		tile(lit["far"], 58)
	tile(ridge, 120)
	if lit:
		tile(lit["ridge"], 120)
	if mist is not None:
		tile(mist, 140)
	tile(mid, 104)
	c.rect(0, 104 + MID_H, 640, 360 - 104 - MID_H, MID_GROUND)
	if lit:
		tile(lit["mid"], 104)
	if with_beams is not None:
		tile(with_beams, 40)
	tile(near, 170)
	if lit:
		tile(lit["near"], 170)
	c.rect(0, 170 + NEAR_H, 640, 360 - 170 - NEAR_H, FINAL)
	if terrain:  # rough stand-in for the terrain wall (soil ramp), floor at y 224
		soil = [hexc(v) for v in ("211f24", "2c2930", "39353c")]
		c.rect(0, 224, 640, 136, soil[0])
		for y in range(224, 360, 8):
			for x in range(0, 640, 16):
				c.rect(x + ((y // 8) % 2) * 8, y, 15, 7, soil[1] if (x + y) % 3 else soil[2])
		c.rect(0, 224, 640, 2, hexc("2c4741"))
	return c


def sha(path):
	return hashlib.sha256(open(path, "rb").read()).hexdigest()


def seam_strip(img, half=48):
	"""Columns [W-half, W) followed by [0, half): the 2x-tiled join."""
	s = Canvas(half * 2, img.h)
	for y in range(img.h):
		for x in range(half):
			s.px[y * s.w + x] = img.px[y * img.w + (img.w - half + x)]
			s.px[y * s.w + half + x] = img.px[y * img.w + x]
	return s


def board(items, scale=2, gap=6, bg=(255, 0, 255, 255)):
	"""Vertical board: each (canvas) at its own width."""
	w = max(i.w for i in items) * scale
	h = sum(i.h * scale + gap for i in items)
	b = Canvas(w, h)
	for y in range(h):
		for x in range(w):
			b.px[y * w + x] = bg
	y0 = 0
	for it in items:
		for y in range(it.h):
			for x in range(it.w):
				p = it.px[y * it.w + x]
				if p is not None:
					for sy in range(scale):
						for sx in range(scale):
							b.px[(y0 + y * scale + sy) * w + x * scale + sx] = p
		y0 += it.h * scale + gap
	return b


def main():
	os.makedirs(OUT, exist_ok=True)
	os.makedirs(PREVIEW, exist_ok=True)
	sk = sky()
	ridge, ridge_l = ridge_build()
	far, far_l = far_build(ridge)
	mid, mid_l = mid_build()
	near, near_l = near_build()
	bm = beams()
	out = {"bg_n3_sky": sk, "bg_n3_far": far, "bg_n3_far_lights": far_l, "bg_n3_ridge": ridge, "bg_n3_ridge_lights": ridge_l,
		"bg_n3_mid": mid, "bg_n3_mid_lights": mid_l, "bg_n3_near": near, "bg_n3_near_lights": near_l, "bg_n3_beams": bm}
	for name, cv in out.items():
		save_png(cv, os.path.join(OUT, name + ".png"))
	layers = {"far": far, "ridge": ridge, "mid": mid, "near": near}
	lit = {"far": far_l, "ridge": ridge_l, "mid": mid_l, "near": near_l}
	mist = mist_overlay()
	save_png(stack(layers, sk, mist=mist), os.path.join(PREVIEW, "stack_n3.png"))
	save_png(stack(layers, sk, lit, mist=mist), os.path.join(PREVIEW, "stack_n3_lit.png"))
	save_png(stack(layers, sk, lit, with_beams=bm, mist=mist), os.path.join(PREVIEW, "stack_n3_lit_beams.png"))
	save_png(stack(layers, sk, lit, terrain=True, with_beams=bm, mist=mist), os.path.join(PREVIEW, "stack_n3_terrain.png"))
	for xo, name in ((0, "a"), (160, "b"), (320, "c")):  # shifted camera views (parallax-free approximation)
		pass
	for name, base, lt in (("far", far, far_l), ("ridge", ridge, ridge_l), ("mid", mid, mid_l), ("near", near, near_l)):
		both = base.copy()
		both.blit(lt, 0, 0)
		save_png(both, os.path.join(PREVIEW, f"bg_band_{name}_lit.png"), 2, (255, 0, 255, 255))
		save_png(base, os.path.join(PREVIEW, f"bg_band_{name}.png"), 2, (255, 0, 255, 255))
	save_png(board([far, ridge, mid, near]), os.path.join(PREVIEW, "bg_n3_layers.png"))
	lit_all = []
	for base, lt in ((far, far_l), (ridge, ridge_l), (mid, mid_l), (near, near_l)):
		both = base.copy()
		both.blit(lt, 0, 0)
		lit_all.append(both)
	save_png(board(lit_all), os.path.join(PREVIEW, "bg_n3_layers_lit.png"))
	save_png(board([sk]), os.path.join(PREVIEW, "bg_n3_sky_board.png"), 1)
	save_png(board([bm], 2, 6, (60, 60, 70, 255)), os.path.join(PREVIEW, "bg_n3_beams_board.png"))
	save_png(board([seam_strip(b, 40) for b in (far, ridge, mid, near, bm)], 4, 6), os.path.join(PREVIEW, "bg_seams.png"))
	for name in out:
		p = os.path.join(OUT, name + ".png")
		print(name, sha(p))


if __name__ == "__main__":
	main()

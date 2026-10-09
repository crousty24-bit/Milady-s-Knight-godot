"""N2 Blight Town backdrop layers (RUN-021 aesthetic pass): a plague town rotting on its hill.

Writes to assets/run021/n2/:
  bg_n2_sky.png      640x360  opaque, screen-fixed: olive-black to ochre-grey, veiled moon, dim stars
  bg_n2_far.png      640x170  tiling: hill-top plague town, plague cathedral, town wall, pyres + smoke
  bg_n2_rampart.png  640x112  tiling: curtain wall, towers, closed gatehouse, gibbets, leaning roofs
  bg_n2_mid.png      512x132  tiling: half-timbered street, jetties, collapsed houses, gibbet, crows
  bg_n2_near.png     512x190  tiling: darkest house fronts / awning frame, fades to FINAL (#121410)
  bg_n2_<band>_lights.png     same size as the band: lit windows / pyre embers / torches only
and previews to work/run021/n2pass/preview/.

Same method as tools/art/world_bg.py: native 1x pixel art, ordered dither (no smooth gradients),
every x-dependent routine wraps (periodic functions, wrapped puts), deterministic seeded rng.
Usage: python3 tools/art/run021/n2/backdrop_n2.py
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
from world_bg import _branch, dither, dither_band, periodic, rng  # noqa: E402  (read only)
from pngio import load_png  # noqa: E402

OUT = os.path.join(ROOT, "assets", "run021", "n2")
PREVIEW = os.path.join(ROOT, "work", "run021", "n2pass", "preview")

BILE = [hexc(c) for c in ("2e3216", "474d1f", "666d2a", "8a8d38", "b2ad52", "d4cc7e")]
CLOTH = [hexc(c) for c in ("24101a", "3a1620", "52202a", "6a2d36")]
FINAL = hexc("121410")  # last row of the near band
MID_GROUND = hexc("191c13")  # bottom rows of the mid band


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


def gable(c, cx, base_y, half, height, col, lean=0.0, skip=None, edge=None, tex=None):
	"""Triangular (gabled) roof: rows from base_y upward. `edge` colours the left rim, `tex` the shingle rows."""
	for i in range(height):
		hw = half * (1 - i / height)
		ccx = cx + lean * i / height
		x0, x1 = int(round(ccx - hw)), int(round(ccx + hw))
		for x in range(x0, x1 + 1):
			if skip is not None and skip(x, i):
				continue
			col2 = col
			if edge is not None and x <= x0 + 0:
				col2 = edge
			elif tex is not None and i % 3 == 2 and (x + i) % 2 == 0:
				col2 = tex
			wput(c, x, base_y - i, col2)


def crenels(c, x0, x1, y, col, merlon=3, gap=2, h=3, r=None, miss=0.0):
	x = x0
	while x < x1:
		if r is None or r.random() >= miss:
			wrect(c, x, y - h, merlon, h, col)
		x += merlon + gap


def smoke(c, x, y_base, height, lean, col, w0=1, w1=7, density=0.5, phase=0.0):
	"""Dithered smoke column rising from y_base, leaning with the wind (+x), widening and thinning upward."""
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


class Lights:
	"""Collects lit spots while the base band is drawn; rendered into a transparent overlay of the same size."""

	def __init__(self, w, h):
		self.w, self.h = w, h
		self.items = []

	def window(self, x, y, w, h, kind="ember", halo=True, mull=False):
		self.items.append((x, y, w, h, kind, halo, mull))

	def render(self):
		c = Canvas(self.w, self.h)
		for x, y, w, h, kind, halo, mull in self.items:
			if kind == "bile":
				core, hot, glow = BILE[2], BILE[3], BILE[1]
			elif kind == "pyre":
				core, hot, glow = EMBER[1], EMBER[2], EMBER[0]
			else:
				core, hot, glow = EMBER[0], EMBER[1], EMBER[0]
			if halo:
				for yy in range(y - 1, y + h + 1):
					for xx in range(x - 1, x + w + 1):
						if (xx < x or xx >= x + w or yy < y or yy >= y + h) and (xx + yy) % 2 == 0:
							wput(c, xx, yy, glow[:3] + (70,))
			for yy in range(y, y + h):
				for xx in range(x, x + w):
					if mull and (xx == x + w // 2 or yy == y + h // 2 - 1):
						continue
					wput(c, xx, yy, hot if (yy == y + h - 1 or (xx + yy) % 3 == 0) and kind != "bile" else core if kind != "pyre" else hot)
			if kind == "pyre":
				wput(c, x + w // 2, y - 1, EMBER[3])
		return c


def periodic_tops(W, seed, base, amp, terms=4, freq=3, jitter=None):
	f = periodic(W, seed, terms, freq)
	return [int(round(base + amp * f(x))) for x in range(W)]


# ------------------------------------------------------------------ sky
def sky():
	c = Canvas(640, 360)
	stops = [(0, "0a0c08"), (70, "0f120b"), (130, "161810"), (180, "201f14"), (225, "2c2a1a"), (270, "38351f"), (359, "38351f")]
	for (y0, a), (y1, b) in zip(stops, stops[1:]):
		dither_band(c, y0, y1 + 1, hexc(a), hexc(b))
	# Sickly horizon veil: sparse extra ochre dither low on the sky.
	for y in range(150, 290):
		t = 1 - abs(y - 225) / 75.0
		for x in range(640):
			if t > 0 and dither(t * 0.4, x, y) and (x + y) % 2 == 0:
				c.put(x, y, hexc("3b3721"))
	r = rng("n2sky-stars")
	mx, my, rad = 222, 66, 15
	for _ in range(95):
		x, y = r.randint(0, 639), r.randint(0, 175)
		if math.hypot(x - mx, y - my) < rad + 26:
			continue
		k = r.random()
		c.put(x, y, hexc("55533c") if k < 0.12 else hexc("43432f") if k < 0.45 else hexc("34352a"))
		if k < 0.04:
			for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
				c.put(x + dx, y + dy, hexc("2a2b20"))
	# Moon halo: dithered rings, olive.
	for y in range(my - rad - 24, my + rad + 25):
		for x in range(mx - rad - 24, mx + rad + 25):
			d = math.hypot(x - mx, y - my)
			if rad < d <= rad + 5 and (x + y) % 2 == 0:
				c.put(x, y, hexc("33321d"))
			elif rad + 5 < d <= rad + 13 and (x + 2 * y) % 4 == 0:
				c.put(x, y, hexc("2a2a1a"))
			elif rad + 13 < d <= rad + 24 and (x + 2 * y) % 8 == 0:
				c.put(x, y, hexc("232314"))
	moon = [hexc(v) for v in ("353421", "4c4b2c", "67653b", "807d4c", "949060")]
	for y in range(my - rad, my + rad + 1):
		for x in range(mx - rad, mx + rad + 1):
			d = math.hypot(x - mx, y - my)
			if d > rad:
				continue
			light = 0.6 - 0.5 * ((x - mx) / rad * 0.6 + (y - my) / rad * 0.8) - 0.3 * (d / rad) ** 3
			k = 3 if light > 0.85 else 2 if light > 0.45 else 1 if light > 0.1 else 0
			frac = (light % 0.4) / 0.4
			if k < 3 and dither(frac * 0.5, x, y) and 0.1 < light < 0.9:
				k += 1
			c.put(x, y, moon[k])
	# A few maria / craters (darker blotches).
	for cx, cy, cr in ((mx - 5, my - 4, 4), (mx + 5, my + 3, 3), (mx - 2, my + 8, 2), (mx + 7, my - 6, 2), (mx - 9, my + 3, 2)):
		for y in range(cy - cr, cy + cr + 1):
			for x in range(cx - cr, cx + cr + 1):
				if math.hypot(x - cx, y - cy) <= cr and math.hypot(x - mx, y - my) <= rad - 1:
					c.put(x, y, moon[1] if dither(0.6, x, y) else moon[0])
	# Dark cloud streaks crossing the lower half of the moon (tapered, dithered ends).
	for sy, x0, x1, th, tilt in ((my + 5, mx - 34, mx + 40, 2.6, 0.06), (my - 3, mx - 22, mx + 26, 1.2, 0.04), (my + 12, mx - 40, mx + 30, 1.6, -0.03)):
		for x in range(x0, x1 + 1):
			t = (x - x0) / (x1 - x0)
			wob = math.sin(t * 9.0) * 0.8
			thick = th * math.sin(math.pi * t) ** 0.7
			cy = sy + (x - mx) * tilt + wob
			for y in range(int(cy - thick - 1), int(cy + thick + 2)):
				dy = abs(y - cy)
				if dy <= thick and (dy < thick - 0.7 or dither(0.55, x, y)):
					c.put(x, y, hexc("0f100a") if dy < thick - 0.4 else hexc("1a1a10"))
	return c


# ------------------------------------------------------------------ far: plague town on its hill
FAR_W, FAR_H = 640, 170
FAR = {
	"haze": [hexc(v) for v in ("1f1f13", "27261a", "302e1c")],
	"hill": hexc("2a2d21"),
	"back": hexc("1f2218"),
	"town": hexc("191b12"),
	"front": hexc("13150d"),
	"wall": hexc("1a1c13"),
	"wall_lt": hexc("22251a"),
	"roof_far": hexc("191b12"),
	"cath": hexc("0f1008"),
	"cath_hi": hexc("171910"),
	"rim": hexc("23251a"),
	"ground": hexc("12140d"),
	"open": hexc("2c2d1b"),
	"smoke": hexc("16170e"),
}
CATH_X = 410


def far_build():
	W, H = FAR_W, FAR_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n2far-v3")
	P = FAR
	f_land = periodic(W, "n2far-land", 4, 3)
	f_hill = periodic(W, "n2far-hill", 5, 4)

	def dxw(x, cx):
		return ((x - cx + W // 2) % W) - W // 2

	def land(x):
		return int(round(134 + 3 * f_land(x)))

	def top(x):  # surface of the town hill
		bump = 50 * math.exp(-(abs(dxw(x, CATH_X)) / 100.0) ** 3) + 30 * math.exp(-(dxw(x, 96) / 36.0) ** 2) + 22 * math.exp(-(dxw(x, 196) / 30.0) ** 2) + 32 * math.exp(-(dxw(x, 590) / 38.0) ** 2) + 8 * math.exp(-(dxw(x, 20) / 30.0) ** 2)
		return int(round(land(x) - bump))

	# 1. Sickly haze behind the cathedral (dithered, like the N1 citadel halo but olive/ochre).
	hx, hy = CATH_X + 6, 64
	for y in range(hy - 66, hy + 80):
		for x in range(hx - 150, hx + 150):
			d = math.hypot(dxw(x, hx) / 148.0, (y - hy) / 78.0)
			if d < 1.0 and dither((1 - d) * 0.75, x, y) and (x + y) % 2 == 0:
				wput(c, x, y, P["haze"][2] if d < 0.45 else P["haze"][1] if d < 0.75 else P["haze"][0])
	# 2. Rolling back hills (lighter, further).
	for x in range(W):
		t = int(round(112 + 9 * f_hill(x) - 14 * math.exp(-(dxw(x, 250) / 70.0) ** 2)))
		for y in range(t, H):
			wput(c, x, y, P["hill"] if (y - t > 1 or x % 2) else hexc("272a1f"))
	# 3. The town hill body, then rows of tiny roofs climbing it.
	for x in range(W):
		for y in range(top(x) + 4, H):
			wput(c, x, y, P["back"])

	def roofs(x_from, x_to, row_off, col, hmin, hmax, wmin, wmax, gap, seedtag, dens=1.0, lit_p=0.38):
		rr = rng("n2far-roofs", seedtag)
		x = x_from
		while x < x_to:
			w = rr.randint(wmin, wmax)
			if any(abs(dxw(x + w // 2, pxx)) < 11 for pxx in (96, 196, 590)) or rr.random() > dens:
				x += w + gap
				continue
			cx = x + w // 2
			base = top(cx) + row_off
			hh = max(4, int(w * rr.uniform(0.42, 0.75)))
			wall_h = rr.randint(3, 7)
			kind = rr.random()
			wrect(c, x, base - wall_h, w, wall_h + 8, col)
			if kind < 0.18:  # long house seen side-on: ridge parallel to the view, hipped ends
				for i in range(hh // 2 + 1):
					wrect(c, x + i, base - wall_h - i, w - 2 * i, 1, col)
			elif kind < 0.3:  # tall narrow house with a steep spire roof
				gable(c, cx, base - wall_h, w // 2 + 1, hh + 5, col, lean=rr.choice((-1, 0, 1)))
			else:
				gable(c, cx, base - wall_h, w // 2 + 1, hh, col, lean=rr.choice((-2, -1, 0, 0, 1, 2)),
					skip=(lambda xx, i: rr.random() < 0.18 and i > hh * 0.6) if rr.random() < 0.18 else None)
			if rr.random() < 0.5:  # chimney
				wrect(c, x + rr.randint(1, max(1, w - 4)), base - wall_h - hh - 1 + rr.randint(0, 2), 2, 5, col)
			if rr.random() < lit_p:  # lit window (dark pane in the base band)
				lx, ly = x + rr.randint(2, max(2, w - 3)), base - wall_h + 1
				wput(c, lx, ly, P["open"])
				lights.window(lx % W, ly, 1, 2 if rr.random() < 0.5 else 1, "ember" if rr.random() < 0.82 else "bile", False)
			x += w + gap + rr.randint(-1, 2)

	tiers = [hexc("1f2218"), hexc("1b1d14"), hexc("17190f"), hexc("13150d")]
	for k, (off, col, x0, x1) in enumerate(((4, tiers[0], 270, 552), (12, tiers[1], 258, 566), (20, tiers[2], 252, 572), (28, tiers[3], 246, 580))):
		roofs(x0, x1, off, col, 6, 10, 10, 17, 0, "row%d" % k, 1.0, 0.1 + 0.03 * k)
	# Outskirts: sparse small houses on the lower ground, wrapping around the seam.
	roofs(-60, 246, 0, P["town"], 5, 8, 8, 13, 20, "out1", 0.8, 0.2)
	roofs(556, 700, 0, P["town"], 5, 8, 8, 13, 16, "out2", 0.8, 0.2)

	# 4. Town wall climbing the hill, with towers (stone, a touch lighter than the roofs).
	def wall_top(x):
		return min(top(x) + 35, land(x) - 5)

	for x in range(W):
		if -139 <= dxw(x, CATH_X) <= 146:
			wt = wall_top(x)
			for y in range(wt, H):
				wput(c, x, y, P["ground"] if y > wt + 7 else P["wall"])
			if x % 3 == 0:
				wput(c, x, wt + 1, P["wall_lt"])
	for x in range(CATH_X - 138, CATH_X + 146, 4):
		if r.random() > 0.08:
			wrect(c, x, wall_top(x) - 2, 2, 2, P["wall"])
	towers = [(CATH_X - 132, 7, 15, "cone"), (CATH_X - 80, 6, 20, "flat"), (CATH_X - 28, 8, 13, "cone"), (CATH_X + 52, 6, 24, "flat"),
		(CATH_X + 108, 7, 17, "cone"), (CATH_X + 142, 5, 11, "broken")]
	for tx, hw, ht, style in towers:
		wb = wall_top(tx)
		wrect(c, tx - hw, wb - ht, hw * 2 + 1, ht + 8, P["wall"])
		for y in range(wb - ht, wb + 8):
			wput(c, tx - hw, y, P["wall_lt"])
		if style == "cone":
			gable(c, tx, wb - ht, hw + 2, hw + 8, P["roof_far"])
		elif style == "flat":
			crenels(c, tx - hw, tx + hw + 1, wb - ht, P["wall"], 2, 2, 2)
			wrect(c, tx + 2, wb - ht - 7, 1, 5, P["wall"])  # banner pole
			wput(c, tx + 3, wb - ht - 7, CLOTH[0])
			wput(c, tx + 4, wb - ht - 6, CLOTH[0])
		else:
			for xx in range(tx - hw, tx + hw + 1):
				wrect(c, xx, wb - ht - (xx * 5) % 4, 1, (xx * 5) % 4, P["wall"])
		wput(c, tx, wb - ht + 4, P["open"])
		lights.window(tx % W, wb - ht + 3, 1, 2, "ember", False) if style in ("flat", "cone") and tx % 2 == 0 else None
	# 5. Ground below the outskirts.
	for x in range(W):
		for y in range(land(x) + 4, H):
			wput(c, x, y, P["ground"])
	for x in range(W):
		for y in range(land(x) - 2, land(x) + 4):
			if c.get(x, y) is None:
				wput(c, x, y, P["ground"])

	# 6. The plague cathedral on its terrace: stepped Gothic nave with flying buttresses, a facing
	# transept gable with rose window, ONE very tall bell tower and a broken second spire.
	K, KH = P["cath"], P["cath_hi"]
	B = top(CATH_X) + 8  # plateau line (the cathedral sits amid the town roofs)
	for x in range(CATH_X - 42, CATH_X + 78):  # retaining masonry down the hill flanks
		for y in range(B, min(top(x) + 19, B + 12)):
			wput(c, x, y, K)
	nx0, nx1 = CATH_X - 20, CATH_X + 64
	# aisles (low) and clerestory (high)
	wrect(c, nx0, B - 22, nx1 - nx0, 24, K)
	for i in range(8):  # aisle lean-to roofs: one-pixel steps from the clerestory wall
		wrect(c, nx0 + i // 2, B - 22 - (8 - i) // 2, nx1 - nx0 - i, 1, K) if False else None
	cx0, cx1 = nx0 + 6, nx1 - 8
	wrect(c, cx0, B - 40, cx1 - cx0, 20, K)
	rid = B - 54  # ridge height
	for i in range(14):  # hipped roof slab: ends slope in 1:1
		wrect(c, cx0 - 2 + i, B - 40 - i, (cx1 - cx0) + 4 - 2 * i, 1, K)
	for x in range(cx0 + 8, cx1 - 6, 5):  # roof cresting spikes along the ridge
		wput(c, x, rid - 1, K)
		wput(c, x, rid - 2, K) if x % 10 == 0 else None
	# aisle roof slope pixels (shallow)
	for i in range(6):
		wrect(c, nx0 - 1 + i, B - 22 - (6 - i) // 3 - 1 + 1, 1, 1, K)
	# flèche on the ridge
	fx = cx0 + 26
	for i in range(26):
		hw = 2.4 * (1 - i / 26.0) ** 1.2
		for x in range(int(round(fx - hw)), int(round(fx + hw)) + 1):
			wput(c, x, rid - 1 - i, K)
	wput(c, fx, rid - 28, K)
	# buttress piers with pinnacle spikes + flying arcs, both flanks of the clerestory
	for bx in range(nx0 + 4, nx1 - 3, 11):
		wrect(c, bx - 1, B - 28, 3, 32, K)
		for i in range(7):
			hw = 1.5 * (1 - i / 7.0)
			for xx in range(int(round(bx - hw)), int(round(bx + hw)) + 1):
				wput(c, xx, B - 29 - i, K)
		wline(c, bx + 1, B - 27, bx + 5, B - 37, K)
		wline(c, bx + 1, B - 26, bx + 5, B - 36, K)
		for yy in range(B - 20, B - 6):  # tall lancets: lighter slits (sickly haze showing through)
			wput(c, bx + 5, yy, P["open"] if yy % 2 == 0 else K)
	for bx in range(cx0 + 4, cx1 - 2, 9):  # clerestory lancets
		for yy in range(B - 37, B - 28):
			wput(c, bx, yy, P["open"] if yy % 2 == 0 else K)
	# transept gable facing us with a big rose window
	tcx = CATH_X + 30
	wrect(c, tcx - 14, B - 46, 29, 50, K)
	gable(c, tcx, B - 46, 17, 30, K, edge=KH)
	for pxx in (tcx - 14, tcx + 14):  # corner turrets
		wrect(c, pxx - 1, B - 62, 3, 18, K)
		gable(c, pxx, B - 62, 2, 10, K)
	wput(c, tcx, B - 77, K)
	wput(c, tcx, B - 78, K)
	wrect(c, tcx - 1, B - 76, 3, 1, K)
	rr_y = B - 34
	for a in range(0, 360, 15):
		wput(c, tcx + int(round(6 * math.cos(math.radians(a)))), rr_y + int(round(6 * math.sin(math.radians(a)))), P["open"])
	for a in range(0, 360, 60):
		wline(c, tcx, rr_y, tcx + int(round(6 * math.cos(math.radians(a)))), rr_y + int(round(6 * math.sin(math.radians(a)))), P["open"])
	for lx in (tcx - 8, tcx - 2, tcx + 5):
		for yy in range(B - 24, B - 10):
			wput(c, lx, yy, P["open"] if yy % 2 == 0 else K)
	for yy in range(B - 66, B - 52):  # tall lancet in the gable
		wput(c, tcx, yy, P["open"] if yy % 2 == 0 else K)
	# east end: apse cone + the broken second tower
	ex = nx1 + 4
	wrect(c, ex - 8, B - 56, 17, 62, K)
	for xx in range(ex - 8, ex + 9):
		wrect(c, xx, B - 56 - ((xx * 7 + 3) % 6), 1, (xx * 7 + 3) % 6, K)
	for i in range(20):  # snapped, leaning spire remnant
		hw = max(0.0, 3.4 * (1 - i / 20.0) ** 1.1)
		for xx in range(int(round(ex + 3 + i * 0.3 - hw)), int(round(ex + 3 + i * 0.3 + hw)) + 1):
			if i < 13 or (xx + i) % 2:
				wput(c, xx, B - 62 - i, K)
	for yy in range(B - 46, B - 32):
		wput(c, ex, yy, P["open"] if yy % 2 == 0 else K)
	# Bell tower: tall, with buttressed base, string courses, belfry louvres, clock ring, needle spire + cross.
	tx0, tw = CATH_X - 38, 17
	shaft = 49
	t_top = B - shaft
	wrect(c, tx0, t_top, tw, shaft + 8, K)
	wrect(c, tx0 - 2, B - 28, tw + 4, 36, K)
	wrect(c, tx0 - 1, t_top + 22, tw + 2, 2, K)
	for pxx in (tx0 - 1, tx0 + tw):  # corner pinnacles
		wrect(c, pxx, t_top - 6, 1, 8, K)
		wput(c, pxx, t_top - 7, K)
	sc = tx0 + tw // 2
	spire_h = 34
	for i in range(spire_h):
		hw = (tw / 2.0 + 0.5) * (1 - i / spire_h) ** 1.35
		for x in range(int(round(sc - hw)), int(round(sc + hw)) + 1):
			wput(c, x, t_top - 1 - i, K)
	for i in range(4):
		wput(c, sc, t_top - spire_h - i, K)
	wrect(c, sc - 1, t_top - spire_h - 2, 3, 1, K)
	for ox in (tx0 + 3, tx0 + 9):  # belfry louvres
		for y in range(t_top + 5, t_top + 17):
			wput(c, ox, y, P["open"] if y % 2 == 0 else K)
			wput(c, ox + 1, y, P["open"] if y % 2 == 0 else K)
		wput(c, ox, t_top + 4, P["open"])
	for a in range(0, 360, 30):  # clock ring
		wput(c, sc + int(round(4 * math.cos(math.radians(a)))), t_top + 34 + int(round(4 * math.sin(math.radians(a)))), P["open"])
	for y in range(t_top + 42, B - 10, 9):
		wput(c, sc, y, P["open"])
		wput(c, sc, y + 1, P["open"])
	# Lights: candle in the belfry, lancets, rose window glint.
	lights.window(sc - 2, t_top + 8, 1, 2, "ember", False)
	lights.window(sc + 3, t_top + 8, 1, 2, "bile", False)
	lights.window(bx0 := nx0 + 9, B - 16, 1, 3, "ember", False)
	lights.window(nx0 + 31, B - 16, 1, 3, "ember", False)
	lights.window(tcx - 2, B - 20, 1, 3, "ember", False)
	lights.window(tcx, rr_y, 1, 1, "bile", False)
	lights.window(ex, B - 40, 1, 2, "ember", False)
	lights.window(sc, B - 14, 1, 2, "ember", False)

	# 7. Pyres on the outskirts with long dithered smoke columns leaning with the wind.
	for px, sh, lean in ((96, 100, 34), (196, 86, 28), (590, 108, 36)):
		g = min(top(px), land(px)) + 1
		for i in range(7):
			wput(c, px - 3 + i, g, P["front"])
			wput(c, px - 2 + i, g - 1, P["front"])
		for i in range(5):
			wput(c, px - 2 + i, g - 2, P["front"])
		wput(c, px, g - 3, P["front"])
		smoke(c, px, g - 4, sh, lean, P["smoke"], 1, 7, 0.55, phase=px * 0.1)
		lights.window(px - 1, g - 2, 3, 1, "pyre", True)
		lights.window(px, g - 4, 1, 1, "pyre", False)
		lights.window(px + 2, g - 3, 1, 1, "ember", False)
	for sx, sh in ((330, 40), (368, 34), (498, 44)):  # chimney smoke from the town
		smoke(c, sx, top(sx) - 6, sh, 12, hexc("191a11"), 1, 4, 0.4, phase=sx * 0.2)

	# 8. Moon-side rim light on the cathedral (veiled moon is to the left): 1 px, every other row.
	darkset = (K, KH)
	for y in range(0, B + 2):
		for x in range(CATH_X - 44, CATH_X + 90):
			p = c.get(x % W, y)
			l = c.get((x - 1) % W, y)
			if p == K and l not in darkset and (y + x) % 2 == 0 and l is not None and l not in (P["town"], P["front"], P["back"], P["wall"], P["ground"]):
				wput(c, x, y, P["rim"])
	return c, lights.render()


# ------------------------------------------------------------------ rampart
RAMP_W, RAMP_H = 640, 112
RAMP = {"wall": hexc("1d2016"), "lt": hexc("252819"), "dk": hexc("161810"), "roof": hexc("191b12"), "gib": hexc("10120b"), "dark": hexc("0f110b")}


def gibbet(c, x, base_y, h, col, r, side=1):
	for y in range(base_y - h, base_y + 1):
		wput(c, x, y, col)
		wput(c, x + 1, y, col)
	wrect(c, x - 2, base_y - 1, 6, 2, col)
	for i in range(1, h // 3):  # brace
		wput(c, x + 2 + i, base_y - h + i + 8 - 8, col) if False else None
	wline(c, x + 1, base_y - h + 7, x + 6 * side, base_y - h, col)
	wrect(c, x + (2 if side > 0 else -14), base_y - h - 1, 14, 2, col)  # arm
	ax = x + (13 if side > 0 else -13)
	for y in range(base_y - h + 1, base_y - h + 7):  # chain
		if y % 2 == 0:
			wput(c, ax, y, col)
	cy = base_y - h + 7  # cage
	for yy in range(cy, cy + 10):
		wput(c, ax - 2, yy, col)
		wput(c, ax + 2, yy, col)
		if (yy - cy) % 3 == 0:
			for xx in range(ax - 2, ax + 3):
				wput(c, xx, yy, col)
	wput(c, ax - 1, cy - 1, col)
	wput(c, ax + 1, cy - 1, col)
	wput(c, ax, cy - 2, col)
	for k in range(-1, 2):
		wput(c, ax + k, cy + 10, col)
	for yy in range(cy + 1, cy + 9):  # inner lattice, diagonal
		wput(c, ax - 1 + (yy - cy) % 3, yy, col)


def rampart_build():
	W, H = RAMP_W, RAMP_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n2ramp-v1")
	P = RAMP
	WT, BOT = 40, 86  # crenel base, nominal wall foot
	broken = [(238, 268), (590, 622)]  # collapsed sections
	# Leaning roofs peeking above the wall (behind it): gabled, hipped, one chapel with a spirelet.
	rr = rng("n2ramp-roofs")
	x = 6
	while x < W - 10:
		rw, rh = rr.randint(16, 32), rr.randint(10, 26)
		lean = rr.choice((-3, -2, -1, 0, 1, 2, 3))
		hb = rr.randint(10, 18)
		wrect(c, x, WT - hb, rw, hb + 2, P["roof"])
		kind = rr.random()
		if kind < 0.25:  # hipped / side-on roof: trapezoid
			for i in range(rh // 2):
				wrect(c, x + i, WT - hb - i, rw - 2 * i, 1, P["roof"])
		elif kind < 0.33 and rw < 24:  # chapel with spirelet
			gable(c, x + rw // 2, WT - hb, rw // 2 + 1, rh, P["roof"], lean=lean, tex=P["dk"])
			spire_c = x + rw // 2
			for i in range(18):
				wput(c, spire_c, WT - hb - rh - i, P["roof"])
				if i < 9:
					wput(c, spire_c - 1, WT - hb - rh - i, P["roof"])
					wput(c, spire_c + 1, WT - hb - rh - i, P["roof"])
		else:
			gable(c, x + rw // 2, WT - hb, rw // 2 + 2, rh, P["roof"], lean=lean, edge=P["lt"], tex=P["dk"],
				skip=(lambda xx, i, rh=rh: i > rh * 0.55 and (xx * 5 + i) % 7 < 2) if rr.random() < 0.25 else None)
		if rr.random() < 0.7:  # chimney
			wrect(c, x + rr.randint(2, rw - 5), WT - hb - rh // 2 - 4, 2, 7, P["roof"])
		if rr.random() < 0.5:  # dark attic window
			wrect(c, x + rw // 2 - 1, WT - hb - 1 + 0, 3, 4, P["dark"])
		x += rw + rr.randint(0, 14)
	# Wall body with course lines, buttresses, arrow slits.
	for x in range(W):
		cut = next((b for b in broken if b[0] <= x < b[1]), None)
		if cut:
			mid = (cut[0] + cut[1]) / 2
			depth = abs(x - mid) / ((cut[1] - cut[0]) / 2)
			top = int(WT + 4 + (1 - depth) ** 0.7 * 26 + ((x * 7) % 5) + (3 if (x // 3) % 2 else 0))
		else:
			top = WT
		for y in range(top, BOT):
			wput(c, x, y, P["wall"])
	for y in range(WT + 4, BOT - 6, 5):  # stone courses
		off = (y // 5) % 2 * 4
		for x in range(W):
			if (x + off) % 9 == 0 and c.get(x, y) == P["wall"]:
				wput(c, x, y, P["dk"])
			elif (x * 3 + y) % 17 == 0 and c.get(x, y) == P["wall"]:
				wput(c, x, y, P["lt"])
	for x in range(0, W, 40):  # pilasters
		if any(b[0] - 6 <= x < b[1] + 6 for b in broken):
			continue
		for y in range(WT + 2, BOT):
			wput(c, x, y, P["lt"])
			wput(c, x + 1, y, P["wall"])
			wput(c, x + 2, y, P["dk"])
	for x in range(14, W, 26):  # arrow slits
		if any(b[0] - 4 <= x < b[1] + 4 for b in broken):
			continue
		for y in range(WT + 8, WT + 14):
			wput(c, x, y, P["dark"])
	rs = rng("n2ramp-streaks")
	for _ in range(46):  # rot streaks and dripping stains
		x = rs.randint(0, W - 1)
		if any(b[0] - 3 <= x < b[1] + 3 for b in broken):
			continue
		for y in range(WT + 2, WT + 2 + rs.randint(5, 22)):
			if c.get(x % W, y) == P["wall"]:
				wput(c, x, y, P["dk"])
	# Crenellations along the wall top.
	for x in range(0, W, 5):
		if any(b[0] - 2 <= x < b[1] + 2 for b in broken):
			continue
		if r.random() > 0.12:
			wrect(c, x, WT - 3, 3, 3, P["wall"])
			wput(c, x, WT - 3, P["lt"])
	# Towers: (cx, half width, top y, kind)
	towers = [(92, 11, 14, "round"), (190, 9, 10, "square"), (300, 0, 0, "gate"), (420, 9, 18, "broken"), (520, 10, 16, "round")]
	for tx, hw, ty, kind in towers:
		if kind == "gate":
			continue
		wrect(c, tx - hw, ty, hw * 2 + 1, BOT - ty, P["wall"])
		if kind == "round":  # shaded cylinder: darker right side + lit left rim
			for y in range(ty, BOT):
				wput(c, tx - hw, y, P["lt"])
				for k in range(3):
					wput(c, tx + hw - k, y, P["dk"] if k < 2 else P["wall"])
			wrect(c, tx - hw - 2, ty - 2, hw * 2 + 5, 3, P["wall"])  # corbelled top
			gable(c, tx, ty - 2, hw + 3, hw + 12, P["roof"], tex=P["dk"])
			wput(c, tx, ty - hw - 15, P["wall"])
			wput(c, tx, ty - hw - 16, P["wall"])
			for y in range(ty + 8, ty + 14):
				wput(c, tx, y, P["dark"])
			lights.window(tx - hw - 1, ty + 1, 1, 2, "ember", True)
		elif kind == "square":
			for y in range(ty, BOT):
				wput(c, tx - hw, y, P["lt"])
				wput(c, tx + hw, y, P["dk"])
			wrect(c, tx - hw - 2, ty - 3, hw * 2 + 5, 3, P["wall"])
			crenels(c, tx - hw - 2, tx + hw + 3, ty - 3, P["wall"], 3, 2, 3, r)
			# timber hoarding lean-to
			for i in range(8):
				wline(c, tx + hw, ty + 2 + i, tx + hw + 6, ty + 6 + i, P["dk"]) if False else None
			wrect(c, tx + hw + 1, ty + 6, 5, 12, P["dk"])
			wline(c, tx + hw + 1, ty + 6, tx + hw + 6, ty + 10, P["wall"])
			for y in range(ty + 10, ty + 18):
				wput(c, tx - 1, y, P["dark"])
				wput(c, tx, y, P["dark"])
			lights.window(tx - hw - 2, ty - 2, 1, 2, "ember", True)
			lights.window(tx + hw + 2, ty - 2, 1, 2, "ember", True)
		else:  # broken
			for xx in range(tx - hw, tx + hw + 1):
				wclear(c, xx, ty - 3, 1, 1)
			for xx in range(tx - hw, tx + hw + 1):
				cut = (xx * 5 + 2) % 7
				wclear(c, xx, ty, 1, cut)
			for i in range(14):  # leaning broken beam
				wput(c, tx - hw + 2 + i // 2, ty + 10 - i, P["dk"])
	# Gatehouse: two squat square towers with a pointed roof and a closed pointed portcullis gate.
	gx = 300
	for side in (-1, 1):
		bx = gx + side * 21
		wrect(c, bx - 9, 20, 19, BOT - 20, P["wall"])
		for y in range(20, BOT):
			wput(c, bx - 9, y, P["lt"])
			wput(c, bx + 9, y, P["dk"])
		wrect(c, bx - 11, 17, 23, 3, P["wall"])
		crenels(c, bx - 11, bx + 12, 17, P["wall"], 3, 2, 3, r)
		for y in range(30, 37):
			wput(c, bx, y, P["dark"])
	wrect(c, gx - 14, 28, 29, BOT - 28, P["wall"])
	gable(c, gx, 28, 17, 18, P["roof"], tex=P["dk"])
	for yy in range(46, BOT):  # pointed arch opening (closed): dark with grating
		hw = 9 if yy > 56 else int(9 * math.sqrt(max(0.0, 1 - ((56 - yy) / 10.0) ** 2)))
		for xx in range(gx - hw, gx + hw + 1):
			wput(c, xx, yy, P["dark"])
			if (xx - gx) % 3 == 0 or (yy % 4 == 0):
				wput(c, xx, yy, hexc("191b12"))
	wput(c, gx, 40, P["lt"])
	lights.window(gx - 21, 22, 1, 2, "ember", True)
	lights.window(gx + 21, 22, 1, 2, "ember", True)
	lights.window(gx - 1, 32, 3, 1, "bile", False)
	for pcx in (70, 360, 548):  # painted plague crosses (dark desaturated red) on the wall face
		for y in range(WT + 12, WT + 21):
			wput(c, pcx, y, hexc("2a1219"))
		wrect(c, pcx - 2, WT + 15, 5, 1, hexc("2a1219"))
	# Gibbets in front of the wall.
	gibbet(c, 150, 90, 44, P["gib"], r, 1)
	gibbet(c, 468, 90, 40, P["gib"], r, -1)
	# Rubble at the collapsed sections.
	for a, b in broken:
		for _ in range(20):
			x = r.randint(a - 6, b + 6)
			y = r.randint(WT + 24, BOT - 2)
			wrect(c, x, y, r.randint(1, 3), r.randint(1, 2), P["wall"] if r.random() < 0.6 else P["dk"])
	# Fade the foot by ordered dither into transparency (no hard horizontal edge).
	for y in range(66, H):
		t = min(1.0, (y - 66) / 24.0)
		for x in range(W):
			if c.px[y * W + x] is not None and dither(t, x, y):
				c.px[y * W + x] = None
	for x in range(W):
		for y in range(92, H):
			c.px[y * W + x] = None
	return c, lights.render()


# ------------------------------------------------------------------ mid street
MID_W, MID_H = 512, 132
MID = {
	"wall": hexc("1c1f15"), "wall2": hexc("191b12"), "timber": hexc("272a1c"), "shadow": hexc("12140c"),
	"roof": hexc("191b12"), "roof_lt": hexc("232617"), "hole": hexc("0d0f09"), "board": hexc("262819"),
	"ground": MID_GROUND, "gline": hexc("23261a"),
}


def mid_house(c, lights, r, x, w, floors, roof_h, ground_y, *, jetty=2, lean=0, collapsed=None, door=True, cross=False, lit=(), style="gable", dormer=False, sign=False):
	"""Half-timbered house with a jettied upper floor, steep gabled roof, crooked shutters."""
	P = MID
	fh = 17
	body_h = fh * floors
	top = ground_y - body_h
	# ground floor, upper floors (jettied)
	wrect(c, x, ground_y - fh, w, fh + 1, P["wall2"])
	for k in range(1, floors):
		wrect(c, x - jetty, ground_y - fh * (k + 1), w + jetty * 2, fh, P["wall"])
		wrect(c, x - jetty, ground_y - fh * k - 2, w + jetty * 2, 2, P["timber"])  # jetty beam
		wrect(c, x, ground_y - fh * k, w, 2, P["shadow"])  # shadow under the jetty
	# timber frame: posts and braces on every floor
	for k in range(floors):
		y1, y0 = ground_y - fh * k, ground_y - fh * (k + 1)
		xa, xb = (x, x + w - 1) if k == 0 else (x - jetty, x + w - 1 + jetty)
		for px in range(xa, xb + 1, 8 if (xb - xa) > 24 else 7):
			for y in range(y0 + 1, y1 - 1):
				wput(c, px, y, P["timber"])
		for px in (xb,):
			for y in range(y0 + 1, y1 - 1):
				wput(c, px, y, P["timber"])
		if k > 0 or True:
			mid = (xa + xb) // 2
			for i in range(min(8, fh - 4)):
				wput(c, xa + 2 + i, y0 + 2 + i, P["timber"])
				wput(c, xb - 2 - i, y0 + 2 + i, P["timber"])
	# roof (steep) with shingle texture and lighter left rim
	rb = top
	half = (w + jetty * 2) // 2 + 2
	cx = x + w // 2
	skip = None
	if collapsed:
		bx, by = collapsed
		skip = lambda xx, i, bx=bx, by=by, cx=cx, half=half, rb=rb: (xx > cx + bx and i > by - (xx - cx - bx) * 0.9) or (i > by + 6 and xx > cx + bx - 4 and r.random() < 0.5)
	if style == "side":  # long roof parallel to the street: hipped ends
		xa, xb = x - jetty - 2, x + w + jetty + 1
		for i in range(roof_h):
			for xx in range(xa + i + (lean if i > roof_h // 2 else 0) // 2, xb - i + 1):
				wput(c, xx, rb - i, P["roof_lt"] if xx == xa + i else P["shadow"] if i % 3 == 2 and (xx + i) % 2 == 0 else P["roof"])
	else:
		gable(c, cx, rb, half, roof_h, P["roof"], lean=lean, skip=skip, edge=P["roof_lt"], tex=P["shadow"])
	if dormer and not collapsed and style != "side":  # small dormer window in the roof
		dx0 = cx - 8 if lean < 0 else cx + 3
		dy = rb - roof_h // 3 - 1
		wrect(c, dx0, dy - 4, 6, 5, P["roof"])
		gable(c, dx0 + 3, dy - 4, 4, 4, P["roof"], edge=P["roof_lt"])
		wrect(c, dx0 + 2, dy - 3, 2, 3, P["hole"])
	# corbels under the jetty (shadow brackets)
	for k in range(1, floors):
		for cxx in range(x + 3, x + w - 2, 8):
			wput(c, cxx, ground_y - fh * k + 2, P["timber"])
			wput(c, cxx - 1, ground_y - fh * k + 2, P["shadow"])
			wput(c, cxx, ground_y - fh * k + 3, P["shadow"])
	if sign:  # hanging sign on an iron bracket
		sx0 = x + w + jetty
		wrect(c, sx0, ground_y - 24, 6, 1, P["timber"])
		wrect(c, sx0 + 4, ground_y - 23, 1, 2, P["timber"])
		wrect(c, sx0 + 2, ground_y - 21, 5, 4, P["shadow"])
	# exposed rafters at the break
	if collapsed:
		bx, by = collapsed
		for i in range(0, 9, 2):
			wline(c, cx + bx + 1 + i, rb - by + 1 + int(i * 0.8), cx + bx + 5 + i, rb - by - 5 + int(i * 0.8), P["timber"])
		for yy in range(rb - 6, rb + 8):  # hole in the wall
			if yy % 2 == 0:
				wrect(c, cx + bx - 2, yy, 6, 1, P["hole"])
	# windows on the upper floors, door on the ground floor
	wins = []
	for k in range(1, floors):
		y0 = ground_y - fh * (k + 1)
		n = 2 if w < 34 else 3
		for i in range(n):
			wx = x - jetty + (w + 2 * jetty) * (i + 1) // (n + 1) - 2
			wins.append((wx, y0 + 5, 4, 6, k))
	if floors == 1 or True:
		n = 1 if w < 32 else 2
		for i in range(n):
			wx = x + w * (i + 1) // (n + 1) + (4 if door and i == 0 else -2)
			wins.append((wx, ground_y - fh + 4, 4, 5, 0))
	for idx, (wx, wy, ww, wh, k) in enumerate(wins):
		wrect(c, wx, wy, ww, wh, P["hole"])
		kind = r.random()
		if kind < 0.34:  # boarded: planks across
			wline(c, wx - 1, wy + 1, wx + ww, wy + wh - 2, P["board"])
			wline(c, wx - 1, wy + wh - 2, wx + ww, wy + 1, P["board"])
		elif kind < 0.7:  # crooked shutter
			wrect(c, wx - 2, wy, 2, wh - (1 if idx % 2 else 0), P["timber"])
			wrect(c, wx + ww, wy + 1, 2, wh - 2, P["timber"])
		if idx in lit:
			lights.window(wx % c.w, wy + 1, ww, wh - 2, "ember" if r.random() < 0.8 else "bile", True)
	if door:
		dx = x + 3
		wrect(c, dx, ground_y - 11, 5, 11, P["hole"])
		wrect(c, dx - 1, ground_y - 12, 7, 1, P["timber"])
		if cross:  # painted plague cross, dark desaturated red
			for y in range(ground_y - 9, ground_y - 3):
				wput(c, dx + 2, y, hexc("2e121a"))
			wput(c, dx + 1, ground_y - 7, hexc("2e121a"))
			wput(c, dx + 3, ground_y - 7, hexc("2e121a"))
	# chimney
	if r.random() < 0.8:
		chx = x + w - 6 + lean // 2
		wrect(c, chx, rb - roof_h // 2 - 8, 3, 10, P["wall2"])
		wrect(c, chx - 1, rb - roof_h // 2 - 9, 5, 2, P["timber"])
		return (chx + 1, rb - roof_h // 2 - 10)
	return None


def mid_build():
	W, H = MID_W, MID_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n2mid-v1")
	P = MID
	f = periodic(W, "n2mid-ground", 3, 3)
	gy = [104 + int(round(1.6 * f(x))) for x in range(W)]

	def g(x):
		return gy[x % W]

	# Ground first so houses sit on it.
	for x in range(W):
		for y in range(gy[x], H):
			c.put(x, y, P["ground"])
	chimneys = []
	# (x, w, floors, roof_h, kwargs)
	plan = [
		(6, 30, 3, 22, dict(jetty=2, lean=2, cross=True, lit=(1,), dormer=True)),
		(52, 38, 3, 24, dict(jetty=3, lean=-3, sign=True)),
		(100, 30, 2, 18, dict(jetty=2, collapsed=(2, 8), lit=())),
		# gap + dead tree at ~140
		(160, 42, 3, 26, dict(jetty=3, lean=3, cross=True, lit=(0, 3), dormer=True)),
		(214, 40, 2, 15, dict(jetty=2, lean=-2, style="side", lit=(1,))),
		# gibbet at ~268
		(298, 44, 3, 24, dict(jetty=3, lean=0, collapsed=(-6, 10), lit=(2,))),
		(354, 32, 2, 22, dict(jetty=2, lean=4, lit=(1,), dormer=True)),
		# plague cross at ~398
		(412, 40, 3, 26, dict(jetty=3, lean=-3, cross=True, lit=(0, 4), dormer=True, sign=True)),
		(460, 34, 1, 14, dict(jetty=2, lean=2, style="side", door=True)),
	]
	for hx, w, floors, rh, kw in plan:
		gyv = g(hx + w // 2)
		ch = mid_house(c, lights, r, hx, w, floors, rh, gyv, **kw)
		if ch:
			chimneys.append(ch)
	for i, (chx, chy) in enumerate(chimneys):  # some chimneys smoke
		if i % 2 == 0:
			smoke(c, chx, chy, 34, 9, hexc("191b12"), 1, 4, 0.5, phase=i)
	# Small low outbuildings / a cart between houses.
	for sx, sw, sh in ((140, 14, 10), (252, 14, 8), (390, 12, 9)):
		pass
	# Dead trees.
	for tx, hgt in ((136, 30), (258, 26), (499, 34)):
		_branch(c, tx, g(tx) + 2, -math.pi / 2 + r.uniform(-0.15, 0.15), hgt * 0.7, 3, P["wall2"], r, 5)
	# Gibbet with cage (post + arm + hanging cage) and a plague cross on a mound.
	gb = P["shadow"]
	gibbet(c, 268, g(268), 54, gb, r, 1)
	cx0 = 398
	for y in range(g(cx0) - 36, g(cx0) + 1):
		wput(c, cx0, y, gb)
		wput(c, cx0 + 1, y, gb)
	wrect(c, cx0 - 7, g(cx0) - 28, 16, 2, gb)
	for y in range(g(cx0) - 26, g(cx0) - 14):  # rag hanging off the arm
		if y % 2 == 0 or y < g(cx0) - 22:
			wput(c, cx0 + 6, y, CLOTH[0])
	# Crows on rooftops and posts.
	for crx, cry in ((34, 49), (183, 38), (432, 52), (232, 46), (281, g(268) - 55)):
		for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 0), (-1, -1), (4, 1), (0, -1), (1, -1)):
			pass
		wput(c, crx, cry, P["hole"])
		wput(c, crx + 1, cry, P["hole"])
		wput(c, crx + 2, cry, P["hole"])
		wput(c, crx - 1, cry - 1, P["hole"])
		wput(c, crx + 3, cry + 1, P["hole"])
		wput(c, crx - 2, cry - 1, P["hole"])
		wput(c, crx, cry - 1, P["hole"])
	# Ground surface: lighter crust line, cobble specks and litter near the top (bottom rows stay flat).
	for x in range(W):
		if r.random() < 0.55:
			c.put(x, gy[x], P["gline"])
	for _ in range(520):
		x, y = r.randint(0, W - 1), r.randint(100, 118)
		if c.get(x, y) == P["ground"] and y >= gy[x] + 2 and r.random() < 1.0 - (y - 104) / 20.0:
			wput(c, x, y, P["gline"] if r.random() < 0.5 else P["shadow"])
	return c, lights.render()


# ------------------------------------------------------------------ near
NEAR_W, NEAR_H = 512, 190
NEAR = {"body": hexc("0e100a"), "edge": hexc("161910"), "hole": hexc("090b07"), "ground": hexc("131610"), "cloth": hexc("150d0f"), "lt": hexc("1a1d13")}


def near_build():
	W, H = NEAR_W, NEAR_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n2near-v1")
	P = NEAR
	f = periodic(W, "n2near-ground", 3, 3)
	tops = [100 + int(round(2.5 * f(x))) for x in range(W)]

	def g(x):
		return tops[x % W]

	# Ground
	for x in range(W):
		for y in range(tops[x], H):
			c.put(x, y, P["ground"])
	# 1. House A: tall jettied house front with collapsed right roof (x 0..92)
	def big_house(x, w, top_y, roof_h, collapse_from, lean, windows, name):
		base = g(x + w // 2)
		wrect(c, x, top_y, w, base - top_y + 2, P["body"])
		jt = 5
		mid_y = top_y + (base - top_y) * 45 // 100
		wrect(c, x - jt, top_y, w + jt * 2, mid_y - top_y, P["body"])  # overhanging upper floor
		wrect(c, x - jt, mid_y - 2, w + jt * 2, 2, P["edge"])
		wrect(c, x, mid_y, w, 3, P["hole"])
		# timber frame
		for px in range(x - jt + 3, x + w + jt - 2, 12):
			for y in range(top_y + 2, mid_y - 2):
				wput(c, px, y, P["edge"])
		for px in range(x + 3, x + w - 2, 12):
			for y in range(mid_y + 4, base):
				wput(c, px, y, P["edge"])
		for i in range(10):
			wput(c, x - jt + 3 + i, top_y + 3 + i, P["edge"])
			wput(c, x + w + jt - 4 - i, top_y + 3 + i, P["edge"])
		# roof: stepped / ragged slopes, never flat
		half = w // 2 + jt + 3
		cxr = x + w // 2
		def skip(xx, i):
			if collapse_from is not None and xx > cxr + collapse_from:
				return i > roof_h - 3 - (xx - cxr - collapse_from) * 0.8
			return (xx * 7 + i * 3) % 13 < 2 and i > roof_h // 2
		gable(c, cxr, top_y, half, roof_h, P["body"], lean=lean, skip=skip, edge=P["edge"], tex=P["hole"])
		# windows (dark panes), some boarded
		wlist = []
		for wx in windows:
			wy = top_y + 8
			wrect(c, x + wx, wy, 7, 9, P["hole"])
			wlist.append((x + wx, wy))
			if r.random() < 0.5:
				wline(c, x + wx, wy, x + wx + 6, wy + 8, P["edge"])
				wline(c, x + wx, wy + 8, x + wx + 6, wy, P["edge"])
		# ground-floor door and window
		wrect(c, x + w - 20, base - 20, 9, 20, P["hole"])
		wrect(c, x + w - 21, base - 21, 11, 1, P["edge"])
		wrect(c, x + 8, mid_y + 12, 7, 8, P["hole"])
		wlist.append((x + 8, mid_y + 12))
		# plague cross on the door
		for y in range(base - 16, base - 6):
			wput(c, x + w - 16, y, hexc("190e11"))
		wrect(c, x + w - 18, base - 13, 5, 1, hexc("190e11"))
		# rot drips under the jetty
		for dx in range(x - jt + 3, x + w + jt - 2, 6):
			if r.random() < 0.6:
				wrect(c, dx, mid_y, 1, r.randint(3, 8), P["hole"])
		return wlist

	wa = big_house(4, 80, 40, 32, 18, -5, (8, 30, 52), "A")
	wb = big_house(258, 74, 38, 30, None, 4, (10, 34, 56), "B")
	# 2. Market awning frame (x 138..232): crooked posts, a sagging sloped beam, scalloped cloth, torn flap, hanging sign.
	ax0, ax1 = 138, 232

	def beam_y(xx):
		return 30 + (xx - ax0) * 7 // (ax1 - ax0)

	for px in (ax0, ax1 - 3):
		for y in range(beam_y(px), g(px) + 2):
			wrect(c, px, y, 4, 1, P["body"])
			wput(c, px + 3, y, P["edge"])
	for xx in range(ax0 - 4, ax1 + 6):  # beam, 3 px thick, ragged right end
		if xx > ax1 + 2 and (xx * 5) % 3 == 0:
			continue
		for y in range(beam_y(xx), beam_y(xx) + 3):
			wput(c, xx, y, P["body"])
		wput(c, xx, beam_y(xx), P["edge"])
	for i in range(6):  # diagonal braces
		wput(c, ax0 + 4 + i, beam_y(ax0) + 3 + i, P["body"])
		wput(c, ax1 - 5 - i, beam_y(ax1) + 3 + i, P["body"])
	for xx in range(ax0 + 4, ax1 - 3):  # cloth
		sag = int(8 + 5 * math.sin(math.pi * (xx - ax0) / (ax1 - ax0)) + (xx % 11 == 0))
		scallop = 3 if (xx // 6) % 2 == 0 else 0
		for y in range(beam_y(xx) + 3, beam_y(xx) + 3 + sag + scallop):
			wput(c, xx, y, P["cloth"] if y < beam_y(xx) + 3 + sag else P["body"])
	for xx in range(ax0 + 4, ax1 - 3, 12):  # cloth folds
		for y in range(beam_y(xx) + 4, beam_y(xx) + 12):
			if y % 2 == 0:
				wput(c, xx, y, P["body"])
	for y in range(beam_y(ax0 + 30) + 14, beam_y(ax0 + 30) + 28):  # torn flap
		wput(c, ax0 + 30, y, P["cloth"] if y < beam_y(ax0 + 30) + 22 else P["body"])
		wput(c, ax0 + 31, y, P["cloth"] if y < beam_y(ax0 + 30) + 24 else P["body"])
	sy = beam_y(ax1) + 6  # hanging sign on a bracket
	wrect(c, ax1 + 1, sy, 14, 2, P["body"])
	wrect(c, ax1 + 3, sy + 2, 1, 4, P["edge"])
	wrect(c, ax1 + 11, sy + 2, 1, 4, P["edge"])
	wrect(c, ax1 + 2, sy + 6, 11, 8, P["body"])
	wrect(c, ax1 + 5, sy + 9, 5, 2, P["hole"])
	# 3. House C (lower, collapsed left roof) and a ruined chimney stack between A and the awning.
	wc = big_house(352, 66, 44, 28, -14, -4, (8, 29, 50), "C")
	for xx in range(102, 114):  # brick stack of a burnt house, ragged top
		top_y = 20 + ((xx * 5) % 4) + (6 if xx > 109 else 0)
		for y in range(top_y, g(xx) + 2):
			wput(c, xx, y, P["body"])
	for y in range(20, g(104) + 1):
		wput(c, 102, y, P["edge"])
	wrect(c, 100, 28, 16, 3, P["body"])
	for xx in range(114, 132):  # fallen lean-to beam resting on a stub wall
		wput(c, xx, 96 - (xx - 114) // 2 + 8, P["body"])
		wput(c, xx, 97 - (xx - 114) // 2 + 8, P["body"])
	wrect(c, 120, 90, 4, g(120) - 90 + 2, P["body"])
	# 4. Hand cart with sacks and a leaning shaft
	cx, cy = 456, g(456) - 1
	wrect(c, cx - 12, cy - 12, 26, 4, P["body"])
	for xx in range(cx - 12, cx + 14):
		wput(c, xx, cy - 12, P["edge"])
	for sx, sw in ((cx - 8, 7), (cx, 6), (cx + 6, 6)):  # sack humps (part of the cart silhouette)
		for yy in range(0, 5):
			half = sw // 2 - (yy // 3)
			for xx in range(sx - half, sx + half + 1):
				wput(c, xx, cy - 13 - yy, P["body"])
	wdisc(c, cx - 3, cy - 5, 6, P["body"])
	wdisc(c, cx - 3, cy - 5, 4, P["hole"])
	wdisc(c, cx - 3, cy - 5, 1, P["body"])
	for a in range(0, 180, 45):
		wline(c, cx - 3 - round(4 * math.cos(math.radians(a))), cy - 5 - round(4 * math.sin(math.radians(a))), cx - 3 + round(4 * math.cos(math.radians(a))), cy - 5 + round(4 * math.sin(math.radians(a))), P["body"])
	wline(c, cx + 13, cy - 11, cx + 30, cy - 2, P["body"])
	wline(c, cx + 13, cy - 10, cx + 30, cy - 1, P["body"])
	# 5. Broken fence posts / rubble heaps between houses
	for _ in range(34):
		px = r.randint(0, W - 1)
		hh = r.randint(3, 11)
		for y in range(g(px) - hh, g(px) + 1):
			wput(c, px, y, P["body"])
		if r.random() < 0.5:
			wput(c, px + 1, g(px) - hh + 1, P["body"])
	# 6. Lit windows: pick a few big-house windows
	for wx, wy in (wa[1], wb[0], wc[2], wb[3]):
		lights.window(wx % W + 1, wy + 1, 5, 7, "ember", True, True)
	lights.window(wc[0][0] % W + 1, wc[0][1] + 1, 5, 7, "bile", True, True)
	# Fade to the solid final colour.
	fade_from = max(tops) + 18
	dither_band(c, fade_from, H - 6, P["ground"], FINAL)
	for y in range(H - 6, H):
		for x in range(W):
			c.put(x, y, FINAL)
	# Remove light spots that ended up in the faded zone (none expected) and bottom check.
	# Top rows stay fully transparent.
	return c, lights.render()


# ------------------------------------------------------------------ build / previews
def fix_lights(lt):
	return lt


def stack(layers, sky_c, lit=None, terrain=False):
	"""Approximate in-game stacking at the reference framing (camera x 0)."""
	c = Canvas(640, 360)
	c.blit(sky_c, 0, 0)
	far, ramp, mid, near = layers["far"], layers["rampart"], layers["mid"], layers["near"]

	def tile(img, y, x_off=0):
		for k in range(-1, 640 // img.w + 2):
			c.blit(img, k * img.w + x_off, y)

	tile(far, 58)
	if lit:
		tile(lit["far"], 58)
	tile(ramp, 120)
	if lit:
		tile(lit["rampart"], 120)
	tile(mid, 104)
	c.rect(0, 104 + MID_H, 640, 360 - 104 - MID_H, MID_GROUND)
	if lit:
		tile(lit["mid"], 104)
	tile(near, 170)
	if lit:
		tile(lit["near"], 170)
	c.rect(0, 170 + NEAR_H, 640, 360 - 170 - NEAR_H, FINAL)
	if terrain:  # rough stand-in for the terrain wall (stone ramp 2a2830 -> 807a82), floor at y 224
		stone = [hexc(v) for v in ("2a2830", "39363f", "4b4751")]
		c.rect(0, 224, 640, 136, stone[0])
		for y in range(224, 360, 8):
			for x in range(0, 640, 16):
				c.rect(x + ((y // 8) % 2) * 8, y, 15, 7, stone[1] if (x + y) % 3 else stone[2])
		c.rect(0, 224, 640, 1, hexc("807a82"))
	return c


def sha(path):
	return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
	os.makedirs(OUT, exist_ok=True)
	os.makedirs(PREVIEW, exist_ok=True)
	sk = sky()
	far, far_l = far_build()
	ramp, ramp_l = rampart_build()
	mid, mid_l = mid_build()
	near, near_l = near_build()
	out = {"bg_n2_sky": sk, "bg_n2_far": far, "bg_n2_far_lights": far_l, "bg_n2_rampart": ramp, "bg_n2_rampart_lights": ramp_l,
		"bg_n2_mid": mid, "bg_n2_mid_lights": mid_l, "bg_n2_near": near, "bg_n2_near_lights": near_l}
	for name, cv in out.items():
		save_png(cv, os.path.join(OUT, name + ".png"))
	layers = {"far": far, "rampart": ramp, "mid": mid, "near": near}
	lit = {"far": far_l, "rampart": ramp_l, "mid": mid_l, "near": near_l}
	save_png(stack(layers, sk), os.path.join(PREVIEW, "stack_n2.png"))
	save_png(stack(layers, sk, lit), os.path.join(PREVIEW, "stack_n2_lit.png"))
	save_png(stack(layers, sk, lit, terrain=True), os.path.join(PREVIEW, "stack_n2_terrain.png"))
	# Per-band previews on magenta at x2 (lights composited for the lit variants).
	for name, base, lt in (("far", far, far_l), ("rampart", ramp, ramp_l), ("mid", mid, mid_l), ("near", near, near_l)):
		save_png(base, os.path.join(PREVIEW, f"band_{name}.png"), 2, (255, 0, 255, 255))
		both = base.copy()
		both.blit(lt, 0, 0)
		save_png(both, os.path.join(PREVIEW, f"band_{name}_lit.png"), 2, (255, 0, 255, 255))
	for name in out:
		p = os.path.join(OUT, name + ".png")
		print(name, sha(p))


if __name__ == "__main__":
	main()

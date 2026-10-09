"""N4 "Forbidden Graveyard" decor props (RUN-021 aesthetic pass).

Pure Python (tools/art/pixel.py). Helpers/palettes are imported read-only from world_props.py,
palette.py and palette_run020.py. Everything is decor: dark, desaturated, lower contrast than
gameplay sprites, no outlines, soft light from the UPPER RIGHT (the moon is up-right).
Stone is STONE_COOL mixed toward DUSK_VIOLET (dull cold grey). Cold flames / glints only in a dim,
greyed SPECTRAL ramp; EMBER only for the rare warm mourner's candle. No flame is painted beyond a
1 px wick (scripts/campaign_decor.gd draws flames/glows at the light points of props_n4.json).

Run:  python3 tools/art/run021/n4/props_n4.py [name ...]
Writes assets/run021/n4/props/*.png, props_n4.json, props_n4.sha256 and the preview boards in
work/run021/n4pass/preview/ (props_n4_board.png, props_n4_scale.png).
"""
import bisect
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
ART = os.path.join(ROOT, "tools", "art")
sys.path.insert(0, ART)
sys.path.insert(0, os.path.join(ART, "run020"))
sys.path.insert(0, os.path.join(ART, "run020_feedback"))
from pixel import Canvas, hexc, save_png  # noqa: E402
from palette import EMBER, MOSS, STONE_COOL, WOOD  # noqa: E402
from world_props import BONE, mix  # noqa: E402  (read only)
from palette_run020 import DUSK_VIOLET, NIGHT, PINE, SOIL, SPECTRAL  # noqa: E402
from pngio import load_png  # noqa: E402

OUT = os.path.join(ROOT, "assets", "run021", "n4", "props")
PREVIEW = os.path.join(ROOT, "work", "run021", "n4pass", "preview")

# ----------------------------------------------------------------------------- materials (dark -> light)
ST = [mix(mix(STONE_COOL[i], DUSK_VIOLET[i], 0.30), NIGHT[2], 0.14) for i in range(6)]  # cold violet-grey stone
STD = [mix(ST[i], NIGHT[0], 0.50) for i in range(6)]  # crypt stone, very dark
MS = [mix(mix(MOSS[i], PINE[i], 0.6), NIGHT[3], 0.30) for i in range(4)]  # dull cold moss
LICH = [hexc(c) for c in ("2a3230", "3b4642", "4f5a55")]  # pale grey-green lichen
YEW = [mix(PINE[i], NIGHT[1], 0.5) for i in range(5)]  # dense dark yew
BARK = [hexc(c) for c in ("131216", "1d1b20", "29262d", "37343c", "46434c")]  # grey-violet dead bark
SOILD = [mix(SOIL[i], NIGHT[1], 0.35) for i in range(5)]
WD = [hexc(c) for c in ("151416", "201e21", "2d2a2d", "3b3739", "4c4749")]  # grey weathered wood
IRON = [hexc(c) for c in ("0f1115", "1a1d24", "272c35", "38404c")]
BRONZE = [hexc(c) for c in ("131211", "1d1c1a", "2a2926", "3b3935")]  # dull dark bronze (never gold)
CLOTH = [hexc(c) for c in ("15131a", "1f1c26", "2a2733", "37343f", "45424e")]
WAX = [mix(BONE[i], NIGHT[2], 0.52) for i in range(3)]
BN = [mix(BONE[i], NIGHT[2], 0.66) for i in range(3)]  # tiny dark bone (skull pile)
BND = [mix(BONE[i], NIGHT[0], 0.84) for i in range(3)]  # ossuary bone, background only
SPEC = [mix(SPECTRAL[i], NIGHT[min(i + 1, 5)], 0.38) for i in range(5)]  # greyed dim spectral
ROOTC = [hexc(c) for c in ("0e0d11", "181619", "232025", "322e34")]
RAVEN = [hexc(c) for c in ("0b0b0f", "14141a", "1e1e26", "2c2c36")]
VOID = hexc("07070a")
CH = [hexc(c) for c in ("1c1f24", "2a2e35", "3b4149", "4d555f")]  # lighter chain links


def rng(*seed):
	return random.Random("-".join(map(str, ("run021-n4",) + seed)))


# ----------------------------------------------------------------------------- primitives
def clamp(v, lo, hi):
	return max(lo, min(hi, v))


def rect(x0, y0, x1, y1):
	return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def ell(cx, cy, rx, ry):
	return {(x, y) for y in range(int(cy - ry) - 1, int(cy + ry) + 2) for x in range(int(cx - rx) - 1, int(cx + rx) + 2)
		if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0}


def poly(pts):
	ys = [p[1] for p in pts]
	cells = set()
	n = len(pts)
	for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
		yc = y + 0.5
		xs = []
		for i in range(n):
			(x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
			if (y0 <= yc < y1) or (y1 <= yc < y0):
				xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
		xs.sort()
		for i in range(0, len(xs) - 1, 2):
			for x in range(int(math.ceil(xs[i] - 0.5)), int(math.floor(xs[i + 1] - 0.5)) + 1):
				cells.add((x, y))
	return cells


def lean(cells, ybase, slope):
	"""Shear: x shifts by (ybase - y) * slope (rows keep their pixels, no holes for |slope| < 0.5)."""
	out = set()
	for (x, y) in cells:
		out.add((x + int(round((ybase - y) * slope)), y))
	return out


def disk(cells, cx, cy, rad):
	ir = int(math.ceil(rad))
	for y in range(int(cy) - ir, int(cy) + ir + 1):
		for x in range(int(cx) - ir, int(cx) + ir + 1):
			if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad + 0.3:
				cells.add((x, y))


def bez(p0, p1, p2, n=None):
	if n is None:
		n = int(max(abs(p2[0] - p0[0]), abs(p2[1] - p0[1])) * 1.6) + 3
	return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
		(1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


def stroke(cells, pts, r0, r1):
	n = len(pts)
	for i, (x, y) in enumerate(pts):
		disk(cells, x, y, r0 + (r1 - r0) * i / max(1, n - 1))


def edge(cells, side):
	d = {"top": (0, -1), "bottom": (0, 1), "left": (-1, 0), "right": (1, 0)}[side]
	return sorted((x, y) for (x, y) in cells if (x + d[0], y + d[1]) not in cells)


def form(c, cells, ramp, lit=3, cap=5, noise=True, shift=0, tones=None):
	"""Shade cells as a rounded form lit from the UPPER RIGHT. If `tones` is a dict the tone index
	is stored there instead of painting."""
	def dist(x, y, dx, dy):
		n = 0
		while n < cap and (x + dx * (n + 1), y + dy * (n + 1)) in cells:
			n += 1
		return n

	for (x, y) in cells:
		a = min(dist(x, y, 1, 0), dist(x, y, 0, -1))
		b = min(dist(x, y, -1, 0), dist(x, y, 0, 1))
		if a == 0 and b == 0:
			k = lit - 1
		elif a == 0:
			k = lit
		elif b == 0:
			k = lit - 3
		else:
			k = lit - 1 if a <= b else lit - 2
		if noise:
			if (x * 7 + y * 13) % 11 == 0:
				k -= 1
			elif (x * 5 + y * 11) % 17 == 0:
				k += 1
		k = clamp(k + shift, 0, len(ramp) - 1)
		if tones is not None:
			tones[(x, y)] = k
		else:
			c.put(x, y, ramp[k])


def masonry(c, cells, ramp, r, course=6, bw=(7, 12), base=2, grad=None, mortar=0):
	"""Ashlar fill for any cell set: staggered courses, per-block tone, lit right/top edges."""
	y0 = min(y for _, y in cells)
	x0 = min(x for x, _ in cells)
	x1 = max(x for x, _ in cells)
	edges, tone = {}, {}
	nrows = (max(y for _, y in cells) - y0) // course + 1
	for ri in range(nrows):
		xs = [x0 - r.randint(0, bw[1])]
		while xs[-1] < x1 + 2:
			xs.append(xs[-1] + r.randint(*bw))
		edges[ri] = xs
		tone[ri] = [clamp(base + r.choice((-1, 0, 0, 0, 1)), 0, len(ramp) - 2) for _ in xs]
	for (x, y) in cells:
		ri = (y - y0) // course
		ry = (y - y0) % course
		bi = bisect.bisect_right(edges[ri], x) - 1
		k = tone[ri][bi]
		if ry == course - 1 or x == edges[ri][bi]:
			k = mortar
		elif ry == 0:
			k += 1
		elif (x * 7 + y * 3) % 13 == 0:
			k -= 1
		if grad:
			k += grad(x, y)
		# lit edges of the whole shape
		if (x + 1, y) not in cells and k > mortar:
			k += 1
		if (x - 1, y) not in cells and k > mortar:
			k -= 1
		if (x, y - 1) not in cells and k > mortar:
			k += 1
		c.put(x, y, ramp[clamp(k, 0, len(ramp) - 1)])


def crack(c, cells, r, x, y, length, col, drift=0.3, side=None):
	for i in range(length):
		if (x, y) in cells:
			c.put(x, y, col)
		y += 1
		if r.random() < 0.55:
			x += r.choice((-1, 1)) if r.random() > drift else (1 if side == "r" else -1)
		if r.random() < 0.18 and (x, y) in cells:
			c.put(x, y, col)
			x += 1 if r.random() < 0.5 else -1


def speckle(c, cells, r, ramp, n, kmin=0, kmax=3):
	cl = sorted(cells)
	for _ in range(n):
		x, y = r.choice(cl)
		c.put(x, y, ramp[r.randint(kmin, kmax)])


def mossify(c, cells, r, p=0.6, depth=2, sides=("top",), ramp=None, xr=None, yr=None):
	ramp = ramp or MS
	for side in sides:
		for (x, y) in edge(cells, side):
			if xr and not (xr[0] <= x <= xr[1]):
				continue
			if yr and not (yr[0] <= y <= yr[1]):
				continue
			if r.random() > p:
				continue
			d = r.choice([1, depth, depth, depth + 1])
			dx, dy = {"top": (0, 1), "bottom": (0, -1), "left": (1, 0), "right": (-1, 0)}[side]
			for i in range(d):
				if (x + dx * i, y + dy * i) in cells:
					k = 3 if (i == 0 and (x + y) % 4 == 0) else 2 if i == 0 else 1 if (x + i) % 3 else 0
					c.put(x + dx * i, y + dy * i, ramp[k])


def lichen(c, cells, r, n, ramp=None):
	ramp = ramp or LICH
	cl = sorted(cells)
	for _ in range(n):
		x, y = r.choice(cl)
		if (x + 1, y) in cells and (x, y + 1) in cells:
			c.put(x, y, ramp[r.randint(0, 2)])
			if r.random() < 0.5:
				c.put(x + 1, y, ramp[0])


def foot(c, x0, x1, yb, r, h=2, ramp=None):
	"""Ragged earth/grass skirt so a prop sits in the ground (yb = last row of the canvas)."""
	ramp = ramp or SOILD
	for x in range(x0, x1 + 1):
		hh = r.choice((0, 1, 1, h)) if x not in (x0, x1) else r.choice((0, 1))
		for i in range(hh):
			c.put(x, yb - i, ramp[1 + (x + i) % 2] if i == 0 else ramp[2])
		if hh and r.random() < 0.35:
			c.put(x, yb - hh, MS[0] if r.random() < 0.6 else MS[1])


def hl(c, x0, x1, y, col):
	for x in range(x0, x1 + 1):
		c.put(x, y, col)


def vl(c, x, y0, y1, col):
	for y in range(y0, y1 + 1):
		c.put(x, y, col)


def stone_prop(c, cells, r, ramp=None, lit=4, moss=0.55, cracks=1, noise=True, shift=0):
	ramp = ramp or ST
	form(c, cells, ramp, lit=lit, noise=noise, shift=shift)
	speckle(c, cells, r, ramp, max(2, len(cells) // 50), 0, lit - 1)
	if moss:
		mossify(c, cells, r, p=moss * 0.6, sides=("top", "bottom"))
	lichen(c, cells, r, max(1, len(cells) // 90))
	for _ in range(cracks):
		cl = [p for p in edge(cells, "top") if True]
		if cl:
			x, y = r.choice(cl)
			crack(c, cells, r, x, y, r.randint(4, 8), ramp[0])


def hang_chain(c, x, y0, length, r, sway=0.0, ramp=None):
	ramp = ramp or IRON
	y = y0
	front = True
	i = 0
	while y < y0 + length:
		xx = x + int(round(math.sin(i * 0.5) * sway))
		if front:
			c.put(xx, y, ramp[3])
			c.put(xx - 1, y + 1, ramp[1])
			c.put(xx + 1, y + 1, ramp[2])
			c.put(xx, y + 2, ramp[1])
			y += 3
		else:
			c.put(xx, y, ramp[2])
			c.put(xx, y + 1, ramp[3] if i % 4 == 1 else ramp[1])
			y += 2
		front = not front
		i += 1
	return y


# ============================================================================= GROUND: headstones
def headstone_round():
	W, H = 14, 20
	c = Canvas(W, H)
	r = rng("headstone_round")
	cells = ell(6.5, 6.5, 6.3, 6.0) | rect(1, 6, 12, 17)
	cells = {p for p in cells if p[1] <= 17}
	stone_prop(c, cells, r, moss=0.5, cracks=0)
	vl(c, 6, 3, 8, ST[0])
	hl(c, 4, 8, 5, ST[0])  # carved cross
	c.put(7, 4, ST[4])
	for (y, x0, x1) in ((11, 4, 9), (13, 4, 7), (15, 5, 9)):  # inscription
		for x in range(x0, x1 + 1):
			if (x + y) % 3:
				c.put(x, y, ST[1])
	crack(c, cells, r, 9, 6, 4, ST[0])
	foot(c, 0, 13, H - 1, r, 3)
	for x in range(1, 13):
		c.put(x, 18, SOILD[2] if x % 3 else SOILD[1])
	return c


def headstone_gothic():
	W, H = 14, 27
	c = Canvas(W, H)
	r = rng("headstone_gothic")
	pts = [(1, 24), (1, 10), (2.6, 5.5), (7, 0), (11.4, 5.5), (13, 10), (13, 24)]
	cells = poly(pts)
	form(c, cells, ST, lit=3)
	inner = poly([(3, 24), (3, 11), (4.2, 7.6), (7, 3.2), (9.8, 7.6), (11, 11), (11, 24)])
	for (x, y) in inner:  # recessed arched panel
		c.put(x, y, ST[1] if (x + y) % 5 else ST[0])
	for (x, y) in edge(inner, "right"):
		c.put(x, y, ST[2])
	for (x, y) in edge(inner, "top"):
		if x >= 7:
			c.put(x, y, ST[3])
	vl(c, 7, 8, 14, ST[3])  # cross in relief
	hl(c, 5, 9, 11, ST[3])
	vl(c, 7, 8, 14, ST[3])
	for x in (5, 6, 8, 9):
		c.put(x, 18, ST[2])
	for x in (5, 6, 7, 8):
		c.put(x, 21, ST[2])
	mossify(c, cells, r, p=0.5, sides=("bottom",))
	lichen(c, cells, r, 3)
	crack(c, cells, r, 4, 12, 7, ST[0])
	foot(c, 0, 13, H - 1, r, 3)
	for x in range(1, 14):
		c.put(x, 25, SOILD[2] if x % 3 else SOILD[1])
	return c


def headstone_cracked():
	W, H = 18, 21
	c = Canvas(W, H)
	r = rng("headstone_cracked")
	cells = poly([(2, 19), (2, 11), (4, 9), (6, 10.5), (8, 6.5), (10, 3), (12, 2), (14, 3.5), (15.5, 6), (15.5, 19)])
	cells = {p for p in cells if p[1] <= 18}
	form(c, cells, ST, lit=4)
	speckle(c, cells, r, ST, 4, 0, 2)
	x = 10
	for y in range(3, 19):  # main fissure, a lit lip on its right
		if (x, y) in cells:
			c.put(x, y, ST[0])
			if (x + 1, y) in cells and y % 2:
				c.put(x + 1, y, ST[4])
		if r.random() < 0.6:
			x += -1 if y < 12 else 1
		x = clamp(x, 6, 12)
	for (y, x0, x1) in ((12, 4, 7), (14, 11, 14), (16, 4, 8)):
		for xx in range(x0, x1 + 1):
			if (xx + y) % 3:
				c.put(xx, y, ST[1])
	mossify(c, cells, r, p=0.35, sides=("top", "bottom"))
	chunk = poly([(14.5, 19.5), (15, 17), (17, 16.5), (17.9, 19.5)])
	form(c, chunk, ST, lit=4, noise=False)
	foot(c, 0, 17, H - 1, r, 3)
	for x in range(2, 16):
		c.put(x, 19, SOILD[2] if x % 3 else SOILD[1])
	return c

def headstone_sunken():
	W, H = 22, 19
	c = Canvas(W, H)
	r = rng("headstone_sunken")
	slab = ell(8.5, 6.5, 6.2, 6.0) | rect(3, 6, 14, 13)
	slab = {p for p in slab if p[1] <= 14}
	cells = lean(slab, 14, -0.22)
	cells = {(x + 4, y + 1) for (x, y) in cells}
	form(c, cells, ST, lit=4)
	speckle(c, cells, r, ST, 3, 0, 2)
	hl(c, 7, 10, 7, ST[0])
	vl(c, 9, 5, 9, ST[0])
	mossify(c, cells, r, p=0.7, depth=3, sides=("top", "left"))
	# the earth swallowing the base: heaved mound, higher on the lean side
	for x in range(0, W):
		top = 14 + int(abs(x - 11) * 0.16) - (2 if 7 <= x <= 16 else 0) + (1 if x % 4 == 0 else 0)
		for y in range(clamp(top, 11, H), H):
			c.put(x, y, SOILD[3] if y == top else SOILD[2] if y < top + 2 else SOILD[1])
		if x % 3 == 1:
			c.put(x, top - 1, MS[1 if x % 2 else 0])
	for (x, y) in ((6, 15), (13, 14), (16, 15)):
		c.put(x, y, SOILD[4])
	return c

def raven_headstone():
	W, H = 16, 27
	c = Canvas(W, H)
	r = rng("raven_headstone")
	slab = (ell(7.5, 15.5, 6.3, 5.5) | rect(1, 15, 14, 23))
	cells = {p for p in slab if p[1] <= 23}
	stone_prop(c, cells, r, moss=0.4, cracks=0)
	hl(c, 4, 10, 17, ST[0])
	hl(c, 5, 9, 19, ST[1])
	hl(c, 5, 10, 21, ST[1])
	grid = (
		".bbb........",
		"abbbb.......",
		".bbbcbb.....",
		"..bbbccbb...",
		"...bbcccbbb.",
		"....bbbbbbbb",
		".....bbbbbba",
		"......a.a...",
	)
	pal = {"a": RAVEN[0], "b": RAVEN[1], "c": RAVEN[2], "d": RAVEN[3]}
	ox, oy = 2, 9  # feet rest on the stone top (y 16 row of the arch at the centre)
	for j, row in enumerate(grid):
		for i, ch in enumerate(row):
			if ch in pal:
				c.put(ox + i, oy + j, pal[ch])
	for (i, j) in ((5, 3), (6, 3), (6, 4), (7, 4), (8, 5)):  # sheen on the upper-right of the back
		c.put(ox + i, oy + j - 1 if j > 3 else oy + j, RAVEN[3] if (i + j) % 2 == 0 else RAVEN[2])
	foot(c, 0, 15, H - 1, r, 3)
	for x in range(1, 15):
		c.put(x, 24, SOILD[2] if x % 3 else SOILD[1])
	return c

# ============================================================================= GROUND: crosses, statues, monuments
def cross_celtic():
	W, H = 22, 32
	c = Canvas(W, H)
	r = rng("cross_celtic")
	cx = 11
	ccx, ccy = cx + 0.5, 9.0
	shaft = rect(cx - 1, 2, cx + 1, 25)
	arms = rect(cx - 9, 8, cx + 9, 9)
	ring = {(x, y) for y in range(0, 20) for x in range(0, 22)
		if 3.7 <= math.hypot(x + 0.5 - ccx, y + 0.5 - ccy) <= 6.0}
	cross = shaft | arms | ring
	cross = lean(cross, 25, -0.045)
	base = rect(cx - 4, 26, cx + 4, 28) | rect(cx - 6, 29, cx + 6, 31)
	form(c, cross, ST, lit=4, cap=2)
	form(c, base, ST, lit=4, cap=3)
	for y in range(13, 24, 3):  # carved knot beads down the shaft
		c.put(cx - 1 + (1 if y < 14 else 0) , y, ST[0])
	for x in (cx - 8, cx - 6, cx + 5, cx + 7):
		c.put(x, 8, ST[0])
	crack(c, cross, r, cx + 1, 15, 6, ST[0])
	mossify(c, base, r, p=0.5, sides=("top", "bottom"))
	mossify(c, cross, r, p=0.2, depth=2, sides=("bottom",), yr=(20, 26))
	foot(c, 3, 18, H - 1, r, 2)
	return c

def mausoleum_small():
	W, H = 60, 76
	c = Canvas(W, H)
	r = rng("mausoleum_small")
	body = rect(7, 33, 52, 71)
	plinth = rect(3, 69, 56, 75)
	pediment = poly([(2, 33), (29.5, 12), (57, 33)])
	pil_l, pil_r = rect(7, 36, 12, 68), rect(47, 36, 52, 68)
	grad = lambda x, y: (1 if x > 40 else -1 if x < 18 else 0)
	masonry(c, body, ST, r, course=6, bw=(7, 10), base=2, grad=grad)
	masonry(c, plinth, ST, r, course=7, bw=(9, 13), base=2)
	# pediment: outer cornice band + recessed tympanum
	tymp = poly([(8, 31), (29.5, 16.5), (51, 31)])
	cornice = pediment - tymp
	form(c, cornice, ST, lit=4, cap=2, noise=False)
	for (x, y) in sorted(tymp):
		c.put(x, y, ST[1] if (x + y) % 6 else ST[0])
	for (x, y) in edge(tymp, "right"):
		c.put(x, y, ST[2])
	# carved wheel emblem in the tympanum (flat)
	for (x, y) in ell(29.5, 26.5, 3.3, 3.3) - ell(29.5, 26.5, 1.9, 1.9):
		c.put(x, y, ST[2] if x > 29 else ST[0])
	c.put(29, 26, ST[2])
	# entablature (shadow under the cornice)
	hl(c, 5, 54, 33, ST[4])
	hl(c, 5, 54, 34, ST[3])
	hl(c, 7, 52, 35, ST[0])
	hl(c, 7, 52, 36, ST[0])
	# pilasters with capital/base
	for (p, cap_x) in ((pil_l, 6), (pil_r, 46)):
		x0 = min(x for x, _ in p)
		form(c, p, ST, lit=3, cap=3, noise=False)
		hl(c, x0 - 1, x0 + 6, 37, ST[3])
		hl(c, x0 - 1, x0 + 6, 38, ST[2])
		hl(c, x0 - 1, x0 + 6, 67, ST[2])
		hl(c, x0 - 1, x0 + 6, 68, ST[0])
		for y in range(40, 66, 3):
			c.put(x0 + 2, y, ST[1])
	# door recess (sealed bronze-dark door, no bars): arched
	door = rect(22, 49, 37, 70) | ell(29.5, 49.5, 7.7, 5.5)
	door = {p for p in door if p[1] <= 70}
	for (x, y) in door:
		c.put(x, y, BRONZE[1] if (x + y * 2) % 7 else BRONZE[0])
	for (x, y) in sorted(door):
		if (x - 1, y) not in door:
			c.put(x, y, BRONZE[0])
	inner = rect(24, 51, 35, 70) | ell(29.5, 51.5, 5.7, 3.6)
	inner = {p for p in inner if p[1] <= 70}
	for (x, y) in inner:
		k = 2 if x >= 30 else 1
		c.put(x, y, BRONZE[k] if (x + y) % 9 else BRONZE[k - 1])
	vl(c, 29, 52, 70, BRONZE[0])  # double-leaf seam
	vl(c, 30, 52, 70, BRONZE[3])
	for y in (56, 62, 67):
		hl(c, 24, 35, y, BRONZE[0])
	for (x, y) in ((27, 60), (32, 60)):  # two blunt bosses
		c.put(x, y, BRONZE[3])
		c.put(x - 1, y + 1, BRONZE[0])
	for x in range(20, 40):  # threshold shadow
		c.put(x, 70, ST[0])
	# steps
	form(c, rect(18, 71, 41, 72), ST, lit=3, noise=False)
	# acroterion + broken urn on the apex
	form(c, rect(27, 10, 32, 12) | rect(28, 8, 31, 9), ST, lit=3, cap=2, noise=False)
	form(c, poly([(52, 33), (56, 30), (56.9, 33.5)]), ST, lit=3, noise=False)
	form(c, rect(49, 28, 54, 31), ST, lit=3, noise=False)
	# weathering: stains, cracks, moss on ledges, lichen
	allc = body | plinth | pediment
	speckle(c, body, r, ST, 40, 0, 2)
	for x0 in (14, 40):
		crack(c, body, r, x0, 52, 14, ST[0])
	crack(c, plinth, r, 50, 69, 5, ST[0])
	mossify(c, pil_l | pil_r, r, p=0.7, sides=("top", "bottom"))
	mossify(c, plinth | rect(18, 71, 41, 72), r, p=0.7, depth=3, sides=("top",))
	mossify(c, cornice, r, p=0.45, depth=2, sides=("top",))
	lichen(c, allc, r, 28)
	for x in range(8, 56):  # stain streaks under the cornice
		if x % 4 == 0:
			vl(c, x, 37, 40 + (x * 7) % 9, ST[0] if x < 40 else ST[1])
	foot(c, 0, 59, H - 1, r, 3)
	return c


def mausoleum_big():
	W, H = 94, 112
	c = Canvas(W, H)
	r = rng("mausoleum_big")
	# belfry tower (left), nave with broken gable (centre), ragged right wing
	tower = rect(5, 22, 25, 106) | poly([(5, 22), (8, 14), (11, 18), (14, 10), (18, 16), (21, 12), (25, 22)])
	nave = rect(26, 58, 78, 106) | poly([(26, 58), (52, 30), (60, 38), (63, 36), (68, 46), (73, 54), (78, 58)])
	wing = rect(79, 70, 90, 106) | poly([(79, 70), (82, 61), (85, 67), (88, 63), (90, 70)])
	plinth = rect(2, 104, 92, 111)
	grad = lambda x, y: (1 if x > 62 else -1 if x < 14 else 0)
	for (cells, base) in ((tower, 2), (nave, 2), (wing, 2)):
		masonry(c, cells, ST, r, course=6, bw=(7, 11), base=base, grad=grad)
	masonry(c, plinth, ST, r, course=8, bw=(10, 15), base=2)
	# tower buttress band and louver opening (dark, bell-less)
	hl(c, 5, 25, 27, ST[0])
	hl(c, 6, 25, 28, ST[4])
	arch = rect(11, 38, 19, 54) | poly([(11, 38), (15, 29), (19, 38)])
	for (x, y) in arch:
		c.put(x, y, VOID if (x + y) % 5 else hexc("0a0a0f"))
	for (x, y) in edge(arch, "right"):
		c.put(x + 1, y, ST[3])
	for (x, y) in edge(arch, "top"):
		c.put(x, y - 1, ST[3])
	for y in range(40, 54, 4):  # louvre slats
		hl(c, 12, 18, y, ST[0])
		hl(c, 13, 18, y + 1, hexc("12121a"))
	hl(c, 5, 25, 66, ST[0])
	hl(c, 6, 25, 67, ST[4])
	hl(c, 5, 25, 82, ST[0])
	hl(c, 6, 25, 83, ST[3])
	# nave: tall gothic window with mullion and broken tracery
	win = rect(46, 64, 58, 84) | poly([(46, 64), (52, 52), (58, 64)])
	for (x, y) in win:
		c.put(x, y, hexc("0a0a10") if (x + y) % 4 else VOID)
	for (x, y) in edge(win, "right"):
		c.put(x + 1, y, ST[3])
	for (x, y) in edge(win, "top"):
		c.put(x, y - 1, ST[3])
	for (x, y) in edge(win, "left"):
		c.put(x - 1, y, ST[0])
	vl(c, 52, 56, 84, ST[1])
	vl(c, 53, 56, 84, ST[3])
	hl(c, 47, 57, 70, ST[1])
	for (x, y) in ((50, 57), (51, 58), (53, 58), (54, 57)):  # remaining tracery
		c.put(x, y, ST[2])
	for (x, y) in ((50, 62), (51, 62)):
		c.put(x, y, hexc("0a0a10"))
	# sealed pointed doorway
	door = rect(41, 89, 59, 105) | poly([(41, 89), (50, 78), (59, 89)])
	for (x, y) in door:
		c.put(x, y, BRONZE[1] if (x + y * 2) % 7 else BRONZE[0])
	inner = rect(44, 92, 56, 105) | poly([(44, 92), (50, 83), (56, 92)])
	for (x, y) in inner:
		k = 2 if x >= 51 else 1
		c.put(x, y, BRONZE[k] if (x + y) % 9 else BRONZE[k - 1])
	vl(c, 50, 85, 105, BRONZE[0])
	vl(c, 51, 85, 105, BRONZE[3])
	for y in (92, 99):
		hl(c, 44, 56, y, BRONZE[0])
	for (x, y) in door:
		pass
	for (x, y) in edge(door, "top"):
		c.put(x, y - 1, ST[3])
	form(c, rect(37, 105, 63, 106), ST, lit=3, noise=False)
	# buttresses on the nave and right wing
	for bx in (30, 72):
		bt = rect(bx, 74, bx + 4, 104)
		form(c, bt, ST, lit=3, cap=3)
		hl(c, bx - 1, bx + 5, 73, ST[4])
		hl(c, bx - 1, bx + 5, 74, ST[0])
	# wing: dark empty window
	for (x, y) in rect(83, 84, 86, 92) | poly([(83, 84), (84.5, 80), (86.5, 84)]):
		c.put(x, y, VOID)
	for (x, y) in rect(83, 84, 86, 92):
		if x == 87:
			c.put(x, y, ST[3])
	# exposed rafters / loose stones at the broken gable
	for (x, y, ln) in ((61, 37, 4), (65, 40, 5), (70, 49, 4)):
		for i in range(ln):
			c.put(x + i, y + i // 2 + 1, ST[0])
	form(c, poly([(66, 57), (70, 55), (72, 58), (68, 59)]), ST, lit=3, noise=False)
	# weathering
	allc = tower | nave | wing | plinth
	speckle(c, tower | nave | wing, r, ST, 90, 0, 2)
	for (cells, x0, y0, ln) in ((tower, 9, 70, 18), (nave, 36, 62, 14), (nave, 68, 80, 16), (wing, 84, 72, 10), (tower, 21, 60, 14)):
		crack(c, cells, r, x0, y0, ln, ST[0])
	mossify(c, plinth, r, p=0.7, depth=3, sides=("top",))
	mossify(c, tower | nave | wing, r, p=0.5, depth=2, sides=("top",))
	lichen(c, allc, r, 60)
	for x in range(5, 91):
		if x % 5 == 0 and (x < 40 or x > 60):
			vl(c, x, 60, 62 + (x * 7) % 15, ST[0] if x < 60 else ST[1])
	foot(c, 0, 93, H - 1, r, 3)
	return c


def obelisk():
	W, H = 18, 60
	c = Canvas(W, H)
	r = rng("obelisk")
	cx = 9
	shaft = poly([(cx - 5, 47), (cx - 3, 6), (cx, 0), (cx + 3, 6), (cx + 5, 47)])
	left = {p for p in shaft if p[0] < cx}
	right = {p for p in shaft if p[0] >= cx}
	form(c, left, ST, lit=3, cap=2, noise=False, shift=-1)
	form(c, right, ST, lit=3, cap=4, noise=False, shift=0)
	for y in range(8, 47):
		if y % 9 == 0:
			hl(c, cx - 5, cx + 5, y, ST[0]) if (cx, y) in shaft else None
	for (x, y) in sorted(shaft):
		if (x, y) in shaft and (x * 5 + y * 3) % 17 == 0:
			c.put(x, y, ST[1])
	b1 = rect(cx - 6, 47, cx + 5, 52)
	b2 = rect(cx - 8, 53, cx + 7, 59)
	form(c, b1, ST, lit=3, cap=3)
	form(c, b2, ST, lit=3, cap=3)
	hl(c, cx - 6, cx + 5, 47, ST[4])
	hl(c, cx - 8, cx + 7, 53, ST[4])
	for y in range(20, 40, 3):  # carved roundel (flat)
		pass
	for (x, y) in ell(cx - 0.5 + 0.5, 28, 2.4, 3.0) - ell(cx, 28, 1.2, 1.7):
		c.put(x, y, ST[0] if x < cx else ST[3])
	crack(c, shaft | b1 | b2, r, cx + 1, 38, 12, ST[0])
	mossify(c, b1 | b2, r, p=0.7, depth=3, sides=("top", "bottom"))
	mossify(c, shaft, r, p=0.35, depth=3, sides=("bottom",), yr=(40, 47))
	lichen(c, shaft | b1 | b2, r, 8)
	foot(c, 0, 17, H - 1, r, 2)
	return c


def column_broken():
	W, H = 20, 35
	c = Canvas(W, H)
	r = rng("column_broken")
	base = rect(2, 31, 17, 34)
	torus = rect(4, 28, 15, 30)
	shaft = poly([(5, 28), (5, 11), (7, 7), (9, 10), (12, 5), (14, 12), (15, 9), (15, 28)])
	form(c, shaft, ST, lit=3, cap=3, noise=False)
	for x in (7, 10, 13):  # flutes
		for y in range(12, 28):
			if (x, y) in shaft and (y + x) % 6:
				c.put(x, y, ST[1] if x < 13 else ST[2])
	for x in (8, 11, 14):
		for y in range(12, 28):
			if (x, y) in shaft and (y + x) % 5:
				c.put(x, y, ST[3] if x < 14 else ST[4])
	form(c, torus, ST, lit=3, cap=2, noise=False)
	form(c, base, ST, lit=3, cap=3)
	hl(c, 2, 17, 31, ST[4])
	# jagged break line
	for (x, y) in ((7, 7), (8, 8), (9, 10), (12, 5), (13, 6), (14, 12)):
		c.put(x, y, ST[4])
	chunk = poly([(15.5, 34), (16, 31.5), (18.5, 30.5), (19.5, 34)])
	form(c, chunk, ST, lit=3, noise=False)
	crack(c, shaft, r, 9, 14, 12, ST[0])
	mossify(c, shaft | torus | base, r, p=0.6, depth=3, sides=("top", "bottom"))
	lichen(c, shaft | base, r, 6)
	foot(c, 0, 19, H - 1, r, 2)
	return c


def angel_statue():
	W, H = 26, 42
	c = Canvas(W, H)
	r = rng("angel_statue")
	cx = 13
	base = rect(4, 38, 21, 41)
	die = rect(7, 31, 18, 37)
	cap = rect(6, 29, 19, 30)
	form(c, base, ST, lit=4, cap=3)
	form(c, die, ST, lit=4, cap=4)
	form(c, cap, ST, lit=4, cap=2, noise=False)
	hl(c, 4, 21, 38, ST[4])
	hl(c, 6, 19, 29, ST[4])
	hl(c, 6, 19, 30, ST[1])
	for (x, y) in rect(9, 32, 16, 36):  # recessed panel
		c.put(x, y, ST[1] if (x + y) % 4 else ST[0])
	vl(c, 16, 32, 36, ST[2])
	# wings: rise above the shoulders and fold down behind the back (scalloped feather edge)
	wl = poly([(11, 14), (7, 9), (4, 3), (5, 8), (3, 10), (3, 18), (4, 24), (7, 28), (9, 24), (10, 20)])
	wr = poly([(15, 14), (19, 9), (22, 3), (21, 8), (23, 10), (23, 18), (22, 24), (19, 28), (17, 24), (16, 20)])
	form(c, wl, ST, lit=4, cap=2, noise=False, shift=-1)
	form(c, wr, ST, lit=4, cap=2, noise=False, shift=0)
	for (x0, y0, dx) in ((4, 12, 1), (4, 16, 1), (5, 20, 1), (22, 12, -1), (22, 16, -1), (21, 20, -1)):  # feather rows
		for i in range(3):
			c.put(x0 + dx * i, y0 + i, ST[0])
	# robe: slim bell with vertical folds; arms folded to the chest
	robe = poly([(10, 13), (11.5, 11), (14.5, 11), (16, 13), (17, 20), (18.5, 28.5), (7.5, 28.5), (9, 20)])
	form(c, robe, ST, lit=4, cap=4, noise=False)
	for x in (10, 12, 15, 17):
		for y in range(17, 28):
			if (x + y) % 6 and (x, y) in robe:
				c.put(x, y, ST[1] if x < 13 else ST[2])
	for (x, y) in ((11, 15), (12, 16), (13, 16), (14, 15)):  # crossed forearms
		c.put(x, y, ST[4] if x > 12 else ST[1])
	# bowed head, face turned down (smooth stone, no features)
	head = ell(cx - 0.8, 7.5, 2.6, 2.7)
	form(c, head, ST, lit=4, cap=3, noise=False)
	for (x, y) in ((cx - 3, 6), (cx - 3, 8), (cx - 2, 10), (cx - 1, 10)):
		c.put(x, y, ST[1])
	for (x, y) in ((cx, 10), (cx + 1, 11)):
		c.put(x, y, ST[0])
	speckle(c, robe | wl | wr, r, ST, 8, 0, 2)
	crack(c, die, r, 13, 33, 4, ST[0])
	mossify(c, base | die | cap, r, p=0.55, depth=3, sides=("top", "bottom"))
	mossify(c, robe | wl | wr, r, p=0.15, depth=2, sides=("top",))
	foot(c, 2, 23, H - 1, r, 2)
	return c

def tomb_chest():
	W, H = 40, 13
	c = Canvas(W, H)
	r = rng("tomb_chest")
	body = rect(2, 6, 27, 11)
	form(c, body, ST, lit=4, cap=3)
	hl(c, 2, 27, 6, ST[0])  # the lid has slid: dark gap along the top of the chest
	# the lid, slid and tilted: a thick, chipped slab resting on the chest and slumping to the ground
	lid = poly([(3, 2), (22, 2), (30, 5), (38.5, 8.5), (38.5, 11.9), (28, 8.5), (22, 5.5), (3, 5.5)])
	lid -= {(38, 8), (38, 9), (37, 8), (3, 2), (3, 3), (4, 2)}
	lid |= {(5, 1), (6, 1), (7, 1), (8, 1)}
	form(c, lid, ST, lit=4, cap=2)
	for (x, y) in sorted(lid):
		if (x, y + 1) not in lid:
			c.put(x, y, ST[0])
	# carved panel and a worn cross on the chest front
	hl(c, 5, 24, 9, ST[1])
	vl(c, 14, 7, 10, ST[3])
	hl(c, 13, 15, 8, ST[3])
	crack(c, body, r, 20, 7, 5, ST[0])
	crack(c, lid, r, 12, 3, 3, ST[0])
	mossify(c, lid, r, p=0.8, depth=2, sides=("top",))
	mossify(c, body, r, p=0.9, depth=2, sides=("bottom",))
	chip = {(30, 11), (31, 11), (31, 10), (32, 11)}
	form(c, chip, ST, lit=4, noise=False)
	foot(c, 0, 39, H - 1, r, 1)
	return c

def grave_mound():
	W, H = 32, 26
	c = Canvas(W, H)
	r = rng("grave_mound")
	mound = set()
	for x in range(0, 31):
		t = max(0.0, 1 - ((x - 14.5) / 15.5) ** 2)
		hgt = int(round(9.5 * t ** 0.75))
		for y in range(24 - hgt, 25):
			mound.add((x, y))
	form(c, mound, SOILD, lit=4, cap=4, noise=True)
	for _ in range(30):  # clods
		x, y = r.choice(sorted(mound))
		c.put(x, y, SOILD[r.randint(1, 4)])
	for (x, y) in ((6, 22), (11, 20), (23, 22)):  # pebbles
		c.put(x, y, ST[2])
		c.put(x + 1, y, ST[3])
	for x in range(0, 31):  # dead grass tufts at the base
		if r.random() < 0.4:
			h = r.choice((1, 2, 3))
			for i in range(h):
				c.put(x, 24 - i, MS[0] if i else MS[1])
	# leaning plank marker (no tools): post, crossbar, two nails
	post = rect(21, 3, 22, 21)
	post = {(x + (1 if y < 10 else 0), y) for (x, y) in post}
	arm = rect(16, 7, 26, 8)
	cross = post | arm
	form(c, cross, WD, lit=4, cap=2, noise=False)
	for y in range(4, 21):
		if (22, y) in cross and y % 4:
			c.put(22, y, WD[2])
	c.put(21, 7, WD[0])
	c.put(27, 7, None)
	crack(c, post, r, 22, 10, 5, WD[0])
	foot(c, 0, 31, H - 1, r, 1)
	return c

def yew():
	W, H = 40, 68
	c = Canvas(W, H)
	r = rng("yew")
	cx = 20
	YW = [hexc(h) for h in ("0b0d10", "11151a", "181d21", "212829", "2c3534")]
	blobs = []
	cells = set()
	for i, y in enumerate(range(7, 58, 5)):
		t = (y - 5) / 52.0
		rx = 3.8 + 9.5 * t ** 0.9 + r.uniform(-0.8, 0.8)
		ry = 4.6
		bx = cx + r.uniform(-1.6, 1.6) * (0.4 + t)
		for sx in ((-0.55, 0.55) if t > 0.25 else (0.0,)):
			b = (bx + sx * rx, y + r.uniform(-1, 1), rx * (0.62 if sx else 1.0), ry)
			blobs.append(b)
			cells |= ell(*b)
	cells |= ell(cx, 4, 2.4, 4)
	trunk = rect(cx - 2, 54, cx + 1, 67) | rect(cx - 3, 63, cx + 2, 67)
	form(c, trunk, BARK, lit=3, cap=2)
	form(c, cells, YW, lit=3, cap=5, noise=False)
	for (bx, by, rx, ry) in blobs:  # clump volumes: lit upper-right, shaded lower-left
		for (x, y) in ell(bx, by, rx, ry):
			if (x, y) not in cells:
				continue
			d = ((x + 0.5 - bx) / rx) ** 2 + ((y + 0.5 - by) / ry) ** 2
			if d > 0.35 and x + 0.5 > bx and y + 0.5 < by:
				c.put(x, y, YW[3] if d < 0.8 else YW[4])
			elif d > 0.5 and x + 0.5 < bx and y + 0.5 > by - 0.5:
				c.put(x, y, YW[0])
	cl = sorted(cells)
	for _ in range(len(cl) // 7):  # needle flecks
		x, y = r.choice(cl)
		c.put(x, y, YW[r.randint(0, 3)])
	foot(c, 10, 30, H - 1, r, 2)
	return c

def willow_dead():
	W, H = 60, 78
	c = Canvas(W, H)
	r = rng("willow_dead")
	trunk = set()
	stroke(trunk, bez((28, 77), (30, 56), (30, 36)), 4.6, 2.6)
	stroke(trunk, bez((24, 77), (22, 75), (18, 78)), 3.8, 2.2)
	stroke(trunk, bez((33, 77), (35, 75), (39, 78)), 3.2, 1.8)
	limbs = []
	for (p0, p1, p2, w0, w1) in (
		((29, 40), (12, 2), (5, 32), 2.5, 1.0),
		((31, 40), (48, 0), (55, 30), 2.4, 1.0),
		((29, 37), (18, 0), (16, 20), 1.9, 0.9),
		((31, 37), (41, 0), (44, 20), 1.9, 0.9),
	):
		cl = set()
		pts = bez(p0, p1, p2)
		stroke(cl, pts, w0, w1)
		limbs.append((cl, pts))
		trunk |= cl
	form(c, trunk, BARK, lit=4, cap=3)
	for _ in range(22):
		x, y = r.choice(sorted(trunk))
		c.put(x, y, BARK[r.randint(0, 3)])
	for y in range(46, 76, 4):  # bark fissures
		x = 29 + (y * 3) % 5 - 2
		if (x, y) in trunk:
			vl(c, x, y, y + 2, BARK[0])
	# hanging strands: from the arc past each apex down to different lengths, swaying
	for (cl, pts) in limbs:
		n = len(pts)
		for i in range(n // 4, n - 1):
			if r.random() < 0.85:
				x, y = int(pts[i][0]), int(pts[i][1]) + 1
				ln = r.randint(9, 34) if i > n // 2 else r.randint(5, 16)
				ph = r.uniform(0, 6)
				for j in range(ln):
					xx = x + int(round(math.sin(j * 0.28 + ph) * 1.2))
					yy = y + j
					if yy >= H - 3:
						break
					t = j / max(1, ln - 1)
					k = 3 if t < 0.15 else 2 if t < 0.55 else 1 if t < 0.9 else 0
					if (xx, yy) not in trunk:
						c.put(xx, yy, BARK[k])
	foot(c, 17, 41, H - 1, r, 2)
	return c

# ============================================================================= GROUND: small pieces
def railing():
	W, H = 40, 16
	c = Canvas(W, H)
	r = rng("railing")
	curb = rect(0, 13, 39, 15)
	form(c, curb, ST, lit=3, cap=2)
	mossify(c, curb, r, p=0.6, sides=("top",))
	posts = (2, 10, 18, 26, 34)
	for i, px in enumerate(posts):
		top = 3 if i != 3 else 6  # one broken post
		for y in range(top, 13):
			c.put(px, y, IRON[1])
			c.put(px + 1, y, IRON[3] if y % 5 else IRON[2])
		if i != 3:  # rounded finial (never a spike)
			for (dx, dy, k) in ((0, 1, 1), (1, 1, 3), (0, 0, 2), (1, 0, 3), (-1, 1, 1), (2, 1, 2)):
				c.put(px + dx, dy, IRON[k])
			c.put(px, 2, IRON[1])
			c.put(px + 1, 2, IRON[2])
		else:
			c.put(px, 5, IRON[0])
			c.put(px + 1, 5, IRON[1])
	for y, col in ((6, IRON[2]), (11, IRON[1])):  # two thin rails; one span missing
		for x in range(2, 36):
			if not (24 <= x <= 29 and y == 6):
				c.put(x, y, col if x % 7 else IRON[3])
	for (x, y) in ((20, 7), (21, 8), (30, 12)):  # rust-dull flecks
		c.put(x, y, mix(IRON[2], hexc("3a2a22"), 0.5))
	foot(c, 0, 39, H - 1, r, 2)
	return c


def candle_cluster(name, warm):
	W, H = 24, 15
	c = Canvas(W, H)
	r = rng(name)
	slab = poly([(0, 14), (2, 11), (22, 11), (24, 14)])
	form(c, slab, ST, lit=3, cap=2)
	mossify(c, slab, r, p=0.5, sides=("top",))
	wick = EMBER[0] if warm else SPEC[2]
	spec = ((5, 5, 6), (11, 7, 4), (16, 4, 8), (19, 8, 3)) if warm else ((5, 7, 5), (10, 5, 7), (15, 8, 4), (19, 6, 6))
	lights = []
	for (x, ytop, ln) in spec:
		yb = 11
		top = yb - ln + 2
		for y in range(top, yb):
			c.put(x, y, WAX[2] if y % 3 else WAX[1])
			c.put(x - 1, y, WAX[1])
			c.put(x + 1, y, WAX[0])
		c.put(x, top - 1, WAX[0])
		c.put(x, top - 2, wick)
		for dx in (-2, -1, 0, 1, 2):  # wax puddle
			c.put(x + dx, yb, WAX[1] if dx < 1 else WAX[0])
		lights.append({"pos": [x, top - 2], "type": "candle_warm" if warm else "candle_cold"})
		c.put(x - 1, top + 1, WAX[2])  # drip
	foot(c, 0, 23, H - 1, r, 1)
	return c, lights[:2] if not warm else lights[:2]


def candles_cold():
	return candle_cluster("candles_cold", False)[0]


def candles_warm():
	return candle_cluster("candles_warm", True)[0]


def lantern_post():
	W, H = 20, 46
	c = Canvas(W, H)
	r = rng("lantern_post")
	base = rect(2, 41, 8, 45)
	form(c, base, ST, lit=3, cap=3)
	mossify(c, base, r, p=0.6, sides=("top",))
	for y in range(9, 41):  # slim iron post
		c.put(5, y, IRON[1])
		c.put(6, y, IRON[3] if y % 7 else IRON[2])
	for y in (14, 28, 38):
		hl(c, 4, 7, y, IRON[2])
		c.put(7, y, IRON[3])
	for (dx, dy) in ((4, 9), (4, 8), (5, 7), (6, 6), (7, 6), (8, 5), (9, 5), (10, 5), (11, 5), (12, 6)):  # crook arm
		c.put(dx, dy, IRON[2])
		c.put(dx, dy + 1 if dx > 5 else dy, IRON[1])
	for y in (6, 7):
		c.put(12, y, IRON[1])
	# hanging lantern: cap, glass with dim cold core, base
	lx = 12
	for i, half in enumerate((1, 2, 3)):
		for x in range(lx - half, lx + half + 1):
			c.put(x, 7 + i, IRON[3] if x >= lx else IRON[1])
	for y in range(10, 21):
		for x in range(lx - 3, lx + 4):
			edge_ = x in (lx - 3, lx + 3)
			c.put(x, y, (IRON[3] if x > lx else IRON[0]) if edge_ else mix(NIGHT[1], SPEC[0], 0.35 + 0.1 * (y % 2)))
	for (dx, dy, k) in ((0, 14, 2), (0, 15, 3), (0, 16, 2), (0, 13, 1)):
		c.put(lx + dx, dy, SPEC[k])
	for y in range(10, 21):
		c.put(lx, y, c.get(lx, y)) if False else None
	for x in range(lx - 4, lx + 5):
		c.put(x, 21, IRON[3] if x >= lx else IRON[1])
		c.put(x, 22, IRON[1] if x >= lx else IRON[0])
	c.put(lx, 23, IRON[1])
	foot(c, 0, 12, H - 1, r, 1)
	return c


def wreath_stake():
	W, H = 20, 32
	c = Canvas(W, H)
	r = rng("wreath_stake")
	st = {(x + (1 if y < 12 else 0), y) for (x, y) in rect(9, 9, 10, 30)}
	form(c, st, WD, lit=4, cap=2, noise=False)
	for y in range(10, 30, 4):
		c.put(9 if y > 12 else 10, y, WD[0])
	ring = {(x, y) for y in range(0, 22) for x in range(0, 20) if 3.4 <= math.hypot(x + 0.5 - 10.5, y + 0.5 - 10.5) <= 6.4}
	ring -= {(10, 4), (11, 4)}
	form(c, ring, BARK, lit=4, cap=2, noise=False)
	for (x, y) in sorted(ring):  # dead twig/leaf texture, dull moss specks
		if (x * 3 + y * 5) % 4 == 0:
			c.put(x, y, BARK[1 + (x >= 10) * 2])
		if (x * 5 + y * 7) % 13 == 0:
			c.put(x, y, MS[1])
	for (x, y) in ((13, 7), (6, 12), (14, 13), (8, 7)):  # dried heads, greyed
		c.put(x, y, mix(BN[1], CLOTH[2], 0.5))
	for (x, y) in ((9, 16), (10, 16), (11, 16), (8, 17), (12, 17)):  # faded ribbon bow
		c.put(x, y, CLOTH[3] if x >= 10 else CLOTH[2])
	for (i, x0) in enumerate((9, 11)):
		for j in range(6 + i * 2):
			c.put(x0 + (1 if j > 3 else 0) * (1 if i else -1), 18 + j, CLOTH[3 if i else 2])
	foot(c, 4, 15, H - 1, r, 2)
	return c

def skull_pile():
	W, H = 28, 14
	c = Canvas(W, H)
	r = rng("skull_pile")
	slab = poly([(0, 13), (1, 11), (27, 11), (28, 13)])
	form(c, slab, ST, lit=4, cap=2)
	mossify(c, slab, r, p=0.4, sides=("top",))
	pal = {"b": BN[1], "c": BN[2], "d": hexc("0f0e12"), "a": BN[0]}
	skull = (
		".bcb.",
		"bbbbc",
		"bdbdb",
		".bbb.",
		".bab.",
	)
	for (ox, oy) in ((3, 6), (10, 6), (17, 6), (6, 2), (13, 2), (22, 7)):
		for j, row in enumerate(skull):
			for i, ch in enumerate(row):
				if ch in pal:
					c.put(ox + i, oy + j, pal[ch])
	for (x0, y0, ln) in ((1, 10, 7), (14, 10, 8), (19, 10, 6)):  # long bones at the foot
		for i in range(ln):
			c.put(x0 + i, y0, BN[1] if i % 2 else BN[0])
		c.put(x0, y0 - 1, BN[2])
		c.put(x0 + ln - 1, y0 + 1 if y0 < 11 else y0, BN[2])
	foot(c, 0, 27, H - 1, r, 1)
	return c

# ============================================================================= WALL (wall on the LEFT: x=0 is the face)
def wall_niche():
	W, H = 18, 32
	c = Canvas(W, H)
	r = rng("wall_niche")
	frame = rect(1, 3, 15, 30) | poly([(1, 3), (8, 0), (15, 3)])
	form(c, frame, ST, lit=3, cap=3, noise=False)
	vl(c, 0, 2, 31, ST[0])  # contact with the wall
	slab = rect(4, 8, 12, 27)
	for (x, y) in slab:
		c.put(x, y, ST[1] if (x + y) % 7 else ST[0])
	for (x, y) in edge(slab, "right"):
		c.put(x, y, ST[3])
	for (x, y) in edge(slab, "top"):
		c.put(x, y, ST[0])
	# sealed slab: a small arched plaque and inscription lines, two nails
	pl = rect(6, 11, 10, 15)
	for (x, y) in pl:
		c.put(x, y, ST[2])
	for (x, y) in edge(pl, "top"):
		c.put(x, y, ST[3])
	vl(c, 8, 12, 15, ST[0])
	hl(c, 7, 9, 13, ST[0])
	for (y, x1) in ((19, 11), (21, 10), (23, 11)):
		for x in range(5, x1):
			if (x + y) % 3:
				c.put(x, y, ST[0])
	for (x, y) in ((5, 9), (11, 9), (5, 26), (11, 26)):
		c.put(x, y, ST[4])
	crack(c, frame, r, 13, 5, 8, ST[0])
	mossify(c, frame, r, p=0.6, depth=2, sides=("top", "bottom"))
	lichen(c, frame, r, 5)
	return c


def wall_vine_dead():
	W, H = 20, 46
	c = Canvas(W, H)
	r = rng("wall_vine_dead")
	VINE = [hexc(c_) for c_ in ("141218", "1f1c22", "2c282f", "3b363f")]
	LEAF = [hexc(c_) for c_ in ("24222a", "35323b", "47434d")]

	def vine(x, y, steps, dirx, depth):
		ph = r.uniform(0, 6)
		for i in range(steps):
			y += 1 if r.random() < 0.8 else 0
			x += dirx * (1 if r.random() < 0.5 else 0) + (1 if math.sin(i * 0.5 + ph) > 0.7 and dirx else 0)
			x = clamp(x, 1, W - 2)
			k = 2 if (i % 5) else 1
			c.put(x, y, VINE[k])
			if depth == 0 and i % 2 == 0:
				c.put(x - 1, y, VINE[1])
			if i % 6 == 3 and r.random() < 0.7:  # dead diamond leaf
				side = 1 if r.random() < 0.5 else -1
				c.put(x + side, y, LEAF[1])
				c.put(x + side * 2, y, LEAF[2]) if side > 0 and x + 2 < W else None
				c.put(x + side, y + 1, LEAF[0])
			if depth < 2 and i > 4 and i % 8 == 0 and r.random() < 0.8:
				vine(x, y, r.randint(5, 11), 1, depth + 1)
		return x, y

	vl(c, 0, 0, H - 1, VINE[0])
	vine(1, 0, 38, 1, 0)
	for (x, y) in ((1, 3), (2, 4), (1, 5)):
		c.put(x, y, VINE[3])
	# a thin second strand creeping
	vine(2, 12, 24, 0, 1)
	return c


def wall_chain_ring():
	W, H = 14, 46
	c = Canvas(W, H)
	r = rng("wall_chain_ring")
	plate = rect(0, 1, 3, 8)
	form(c, plate, IRON, lit=3, cap=2, noise=False)
	for (x, y) in ((1, 2), (1, 7)):
		c.put(x, y, IRON[0])
	vl(c, 0, 0, 12, IRON[0])
	hl(c, 4, 6, 4, IRON[2])  # eye bolt
	hl(c, 4, 6, 5, IRON[1])
	ring = {(x, y) for y in range(0, 16) for x in range(0, 14) if 2.4 <= math.hypot(x + 0.5 - 8.5, y + 0.5 - 9.5) <= 4.2}
	form(c, ring, IRON, lit=3, cap=1, noise=False)
	for (x, y) in sorted(ring):
		if (x + y) % 5 == 0:
			c.put(x, y, IRON[3])
	end = hang_chain(c, 8, 14, 26, r, sway=0.9, ramp=CH)
	for (dx, dy) in ((0, 0), (0, 1), (1, 2), (2, 2), (2, 1)):  # open end link
		c.put(8 + dx, end + dy, CH[2] if dx else CH[1])
	return c

def wall_plaque_skull():
	W, H = 20, 24
	c = Canvas(W, H)
	r = rng("wall_plaque_skull")
	plaque = rect(1, 1, 17, 21)
	form(c, plaque, ST, lit=3, cap=3, noise=False)
	vl(c, 0, 0, 23, ST[0])
	# bevelled inner field (flat slate), tone-on-tone carving
	field = rect(3, 3, 15, 19)
	for (x, y) in field:
		c.put(x, y, ST[1] if (x + y * 3) % 8 else ST[0])
	for (x, y) in edge(field, "right"):
		c.put(x, y, ST[3])
	for (x, y) in edge(field, "top"):
		c.put(x, y, ST[0])
	# carved laurel roundel with a small skull relief (flat: lit lower right edge, shaded upper left)
	for (x, y) in ell(9, 8, 5.2, 4.6) - ell(9, 8, 4.0, 3.5):
		c.put(x, y, ST[3] if x + y > 17 else ST[0])
	sk = ell(9, 7.6, 2.4, 2.4) | {(8, 10), (9, 10), (10, 10)}
	for (x, y) in sk:
		c.put(x, y, ST[2])
	for (x, y) in ((8, 8), (10, 8)):  # sockets: single carved dots, shallow
		c.put(x, y, ST[0])
	hl(c, 8, 10, 11, ST[0])
	for x in (7, 11):
		c.put(x, 11, ST[3])
	# inscription lines
	for (y, x0, x1) in ((15, 5, 13), (17, 6, 12)):
		for x in range(x0, x1 + 1):
			if (x + y) % 3:
				c.put(x, y, ST[0])
	for (x, y) in ((2, 2), (16, 2), (2, 20), (16, 20)):  # corner rosettes
		c.put(x, y, ST[4])
	crack(c, plaque, r, 14, 1, 8, ST[0])
	mossify(c, plaque, r, p=0.55, depth=2, sides=("top", "bottom"))
	lichen(c, plaque, r, 4)
	return c


# ============================================================================= CEILING (anchor top-centre)
def hang_chains():
	W, H = 18, 40
	c = Canvas(W, H)
	r = rng("hang_chains")
	for (x, ln, sw) in ((4, 31, 0.8), (10, 36, 0.6), (15, 20, 0.9)):
		for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1)):
			c.put(x + dx, dy, CH[1])
		end = hang_chain(c, x, 1, ln, r, sway=sw, ramp=CH)
		for (dx, dy) in ((0, 0), (0, 1), (1, 2), (2, 2), (2, 1)):
			c.put(x + dx, end + dy, CH[3] if dx else CH[2])
	return c

def hang_censer():
	W, H = 20, 44
	c = Canvas(W, H)
	r = rng("hang_censer")
	cx = 10
	for (dx, dy) in ((0, 0), (1, 0), (-1, 0)):
		c.put(cx + dx, dy, IRON[1])
	end = hang_chain(c, cx, 1, 13, r, sway=0.0)
	# crown / dome with perforations
	dome = poly([(cx - 5, 24), (cx - 4, 19), (cx - 2, 16), (cx, 15), (cx + 2, 16), (cx + 4, 19), (cx + 5, 24)])
	form(c, dome, BRONZE, lit=3, cap=3, noise=False)
	for (dx, dy) in ((-2, 20), (0, 19), (2, 20), (-3, 22), (1, 22), (3, 22)):
		c.put(cx + dx, dy, VOID)
	c.put(cx, 14, BRONZE[3])
	c.put(cx, 13, BRONZE[2])
	for (x0, sx) in ((cx - 4, -1), (cx + 4, 1)):  # side chains to the bowl
		for i in range(5):
			c.put(x0 + sx * (i // 3), 16 + i, IRON[2 if sx > 0 else 1])
	hl(c, cx - 6, cx + 6, 24, BRONZE[3])
	hl(c, cx - 6, cx + 6, 25, BRONZE[0])
	# bowl with dim cold core visible through slits
	bowl = poly([(cx - 6, 26), (cx + 6, 26), (cx + 5, 30), (cx + 3, 33), (cx - 3, 33), (cx - 5, 30)])
	form(c, bowl, BRONZE, lit=3, cap=3, noise=False)
	for (dx, dy) in ((-3, 28), (-1, 28), (1, 28), (3, 28)):
		c.put(cx + dx, dy, SPEC[1])
	for (dx, dy) in ((-1, 29), (0, 29), (1, 29)):
		c.put(cx + dx, dy, SPEC[2])
	c.put(cx, 28, SPEC[3])
	hl(c, cx - 3, cx + 3, 33, BRONZE[0])
	for (x, y) in ((cx - 3, 34), (cx + 3, 34), (cx, 35)):
		c.put(x, y, BRONZE[1])
	c.put(cx, 36, BRONZE[2])
	return c


def hang_roots_n4():
	W, H = 26, 44
	c = Canvas(W, H)
	r = rng("hang_roots_n4")
	cl = set()
	for i in range(8):
		x = 3 + i * 3 + r.randint(-1, 1)
		stroke(cl, bez((x, 0), (x + r.uniform(-3, 3), 6), (x + r.uniform(-2, 2), 12 + r.randint(0, 3))), 1.3, 0.9)
	form(c, cl, ROOTC, lit=3, cap=2, noise=False)
	for x in range(0, W):
		for y in range(0, 3):
			if (x * 3 + y) % 5:
				c.put(x, y, ROOTC[1 + (x % 2)])
	for i in range(11):
		x = 2 + i * 2 + r.randint(0, 1)
		ln = r.randint(8, 36) if 3 < i < 8 else r.randint(5, 22)
		ph = r.uniform(0, 6)
		for j in range(ln):
			xx = x + int(round(math.sin(j * 0.3 + ph) * 1.3))
			t = j / max(1, ln - 1)
			k = 3 if t < 0.2 else 2 if t < 0.6 else 1 if t < 0.9 else 0
			c.put(xx, 10 + j, ROOTC[k])
			if t < 0.3 and i % 3 == 0:
				c.put(xx + 1, 10 + j, ROOTC[1])
	return c


def hang_banner():
	W, H = 24, 50
	c = Canvas(W, H)
	r = rng("hang_banner")
	CL = [hexc(h) for h in ("17151c", "232029", "322f3a", "433f4d", "56525f")]
	rod = rect(0, 0, 23, 1)
	form(c, rod, IRON, lit=3, cap=1, noise=False)
	for (x, y) in ((0, 2), (23, 2), (1, 2), (22, 2)):  # finials
		c.put(x, y, CH[2])
	cloth = set()
	for y in range(2, 46):
		x0 = 4 + int(round(1.6 * math.sin(y * 0.16)))
		x1 = 19 + int(round(1.4 * math.sin(y * 0.16 + 1.2)))
		bot = 40 + [0, 3, 1, 5, 2, 6, 3, 4][(y) % 8] if y > 36 else 99
		for x in range(x0, x1 + 1):
			# swallow-tail bottom (two points) and ragged tears
			depth = 36 + int(abs(x - 11.5) * -0.9 + 9.0) + (x * 5 % 3)
			if y <= depth:
				cloth.add((x, y))
	cloth -= {(19, 14), (19, 15), (18, 15), (4, 26), (5, 26), (5, 27), (18, 31), (19, 32)}
	cloth -= {(x, y) for (x, y) in cloth if 28 < y < 33 and 12 <= x <= 14 and (x + y) % 2 == 0}
	tones = {}
	form(c, cloth, CL, lit=3, cap=3, noise=False, tones=tones)
	for (x, y), k in tones.items():
		if (x - 4) % 5 == 3 and y > 4:
			k = clamp(k - 1, 0, 4)  # fold shadow
		elif (x - 4) % 5 == 4 and y > 4:
			k = clamp(k + 1, 0, 4)
		c.put(x, y, CL[k])
	for y in range(4, 40):  # faded sash band
		for x in (10, 11, 12):
			if (x, y) in cloth:
				c.put(x, y, CL[1] if x < 12 else CL[2])
	hl(c, 6, 17, 5, CL[0])
	for (x, y) in ((11, 14), (11, 15), (11, 16), (10, 15), (12, 15), (11, 17)):  # faded cross
		c.put(x, y, CL[4] if x >= 11 else CL[3])
	for x, y0 in ((8, 40), (13, 44), (16, 41)):
		for j in range(r.randint(2, 4)):
			c.put(x, y0 + j, CL[1])
	return c

# ============================================================================= UNDERGROUND (dark crypt back wall)
def crypt_niche():
	W, H = 38, 36
	c = Canvas(W, H)
	r = rng("crypt_niche")
	cx = 19
	frame = rect(3, 12, 34, 35) | poly([(3, 12), (6, 6), (12, 2), (19, 0), (26, 2), (32, 6), (35, 12)])
	hole = rect(8, 14, 29, 35) | poly([(8, 14), (10, 9), (14, 6), (19, 4.5), (24, 6), (28, 9), (30, 14)])
	form(c, frame - hole, STD, lit=3, cap=2, noise=False)
	for (x, y) in hole:
		c.put(x, y, hexc("08080c") if (x + y) % 6 else hexc("0b0b10"))
	for (x, y) in edge(hole, "left"):
		c.put(x, y, STD[0])
	for (x, y) in edge(hole, "right"):
		c.put(x + 1, y, STD[2])
	# keystone and voussoirs
	for i, (x, y) in enumerate(((19, 0), (19, 1), (18, 0), (20, 0))):
		c.put(x, y, STD[3] if i < 2 else STD[2])
	# sarcophagus resting on a ledge inside the niche
	box = rect(10, 26, 27, 32)
	lid = poly([(9, 26), (11, 22), (26, 22), (28, 26)])
	form(c, box, STD, lit=3, cap=2, noise=False, shift=-1)
	form(c, lid, STD, lit=4, cap=2, noise=False, shift=-1)
	hl(c, 10, 27, 26, STD[0])
	hl(c, 9, 28, 33, STD[2])
	hl(c, 9, 28, 34, STD[0])
	vl(c, 18, 28, 31, STD[0])
	for (x, y) in ((17, 24), (18, 24), (19, 24), (18, 23)):  # tiny carved cross on the lid
		c.put(x, y, STD[3])
	speckle(c, frame - hole, r, STD, 18, 0, 2)
	crack(c, frame - hole, r, 5, 14, 9, STD[0])
	mossify(c, box | lid, r, p=0.5, depth=1, sides=("top",), ramp=[mix(m, NIGHT[0], 0.45) for m in MS])
	return c


def ossuary_wall():
	W, H = 42, 36
	c = Canvas(W, H)
	r = rng("ossuary_wall")
	block = rect(2, 2, 39, 35)
	for (x, y) in block:
		c.put(x, y, hexc("0a0a0e") if (x + y) % 4 else hexc("0c0c11"))
	sk = (
		".bcb.",
		"bbbbc",
		"bdbdb",
		".bbb.",
		".bab.",
	)
	pal = {"b": BND[1], "c": BND[2], "a": BND[0], "d": hexc("0c0c10")}
	for (y, xo) in ((3, 3), (9, 6), (15, 3)):  # two or three loosely heaped skull rows
		x = xo
		while x < 37:
			if r.random() < 0.82:
				oy = y + r.choice((0, 0, 1))
				for j, row in enumerate(sk):
					for i, ch in enumerate(row):
						if ch in pal:
							c.put(x + i, oy + j, pal[ch])
			x += r.choice((5, 6, 6))
	hl(c, 2, 39, 21, hexc("050508"))
	for ri in range(4):  # stacked long bones below, knobbed ends
		y = 23 + ri * 3
		x = 3 - r.randint(0, 3)
		while x < 39:
			ln = r.randint(5, 8)
			for i in range(ln):
				c.put(x + i, y, BND[1] if i % 2 else BND[0])
			for (dx, dy) in ((0, 1), (ln - 1, 1), (0, -1), (ln - 1, -1)):
				c.put(x + dx, y + dy, BND[2] if dx == ln - 1 else BND[0])
			x += ln + r.randint(0, 1)
	fr = rect(0, 0, 41, 35) - block
	form(c, fr, STD, lit=3, cap=2, noise=False)
	crack(c, fr, r, 38, 0, 6, STD[0])
	return c

def loculi_grid():
	W, H = 40, 40
	c = Canvas(W, H)
	r = rng("loculi_grid")
	wall = rect(0, 0, 39, 39)
	masonry(c, wall, STD, r, course=8, bw=(9, 13), base=2)
	lights = None
	for gy in range(3):
		for gx in range(3):
			x0, y0 = 3 + gx * 12, 3 + gy * 12
			niche = rect(x0, y0, x0 + 8, y0 + 8)
			state = (gx * 3 + gy * 5) % 4
			if (gx, gy) == (0, 2):
				state = 9
			for (x, y) in niche:
				c.put(x, y, hexc("08080b") if state in (0, 1, 9) else STD[1] if (x + y) % 5 else STD[0])
			if state in (0, 1, 9):
				for (x, y) in edge(niche, "left"):
					c.put(x, y, STD[0])
				for (x, y) in edge(niche, "right"):
					c.put(x + 1, y, STD[2])
				for x in range(x0 + 1, x0 + 8):
					c.put(x, y0 + 8, STD[1])
					c.put(x, y0 + 7, hexc("0b0b0f"))
			else:  # sealed with a plaque slab
				for (x, y) in edge(niche, "right"):
					c.put(x, y, STD[3])
				for (x, y) in edge(niche, "top"):
					c.put(x, y, STD[0])
				hl(c, x0 + 2, x0 + 6, y0 + 3, STD[0])
				hl(c, x0 + 2, x0 + 5, y0 + 5, STD[0])
			for (x, y) in edge(niche, "top"):
				c.put(x, y - 1, STD[3])
	# one cold candle in the open lower-left niche
	cx, yb = 7, 3 + 24 + 8
	for y in range(yb - 4, yb):
		c.put(cx, y, WAX[1] if y % 2 else WAX[0])
		c.put(cx + 1, y, WAX[0])
	c.put(cx, yb - 5, WAX[0])
	c.put(cx, yb - 6, SPEC[2])
	c.put(cx - 1, yb - 1, WAX[0])
	for dx in (-2, -1, 0, 1, 2):
		c.put(cx + dx, yb, WAX[1])
	return c


def _ground(w, h):
	return [w // 2, h]


def _ceil(w, h):
	return [w // 2, 0]


_c_cold = candle_cluster("candles_cold", False)[1]
_c_warm = candle_cluster("candles_warm", True)[1]

# name, fn, kind, anchor, lights, weight, big
PROPS = [
	("headstone_round", headstone_round, "ground", _ground, [], 5, False),
	("headstone_gothic", headstone_gothic, "ground", _ground, [], 4, False),
	("headstone_cracked", headstone_cracked, "ground", _ground, [], 4, False),
	("headstone_sunken", headstone_sunken, "ground", _ground, [], 4, False),
	("raven_headstone", raven_headstone, "ground", _ground, [], 1, False),
	("cross_celtic", cross_celtic, "ground", _ground, [], 3, False),
	("mausoleum_small", mausoleum_small, "ground", _ground, [], 2, False),
	("mausoleum_big", mausoleum_big, "ground", _ground, [], 1, True),
	("obelisk", obelisk, "ground", _ground, [], 2, False),
	("column_broken", column_broken, "ground", _ground, [], 3, False),
	("angel_statue", angel_statue, "ground", _ground, [], 1, False),
	("tomb_chest", tomb_chest, "ground", _ground, [], 3, False),
	("grave_mound", grave_mound, "ground", _ground, [], 3, False),
	("yew", yew, "ground", _ground, [], 3, False),
	("willow_dead", willow_dead, "ground", _ground, [], 2, True),
	("railing", railing, "ground", _ground, [], 4, False),
	("candles_cold", candles_cold, "ground", _ground, _c_cold, 2, False),
	("candles_warm", candles_warm, "ground", _ground, _c_warm, 1, False),
	("lantern_post", lantern_post, "ground", _ground, [{"pos": [12, 15], "type": "flame_cold"}], 1, False),
	("wreath_stake", wreath_stake, "ground", _ground, [], 2, False),
	("skull_pile", skull_pile, "ground", _ground, [], 2, False),
	("wall_niche", wall_niche, "wall", lambda w, h: [0, 3], [], 3, False),
	("wall_vine_dead", wall_vine_dead, "wall", lambda w, h: [0, 2], [], 4, False),
	("wall_chain_ring", wall_chain_ring, "wall", lambda w, h: [0, 4], [], 3, False),
	("wall_plaque_skull", wall_plaque_skull, "wall", lambda w, h: [0, 10], [], 2, False),
	("hang_chains", hang_chains, "ceiling", _ceil, [], 4, False),
	("hang_censer", hang_censer, "ceiling", _ceil, [{"pos": [10, 28], "type": "flame_cold"}], 1, False),
	("hang_roots_n4", hang_roots_n4, "ceiling", _ceil, [], 3, False),
	("hang_banner", hang_banner, "ceiling", _ceil, [], 2, False),
	("crypt_niche", crypt_niche, "underground", _ground, [], 2, False),
	("ossuary_wall", ossuary_wall, "underground", _ground, [], 2, False),
	("loculi_grid", loculi_grid, "underground", _ground, [{"pos": [7, 25], "type": "candle_cold"}], 2, False),
]

LIMITS = {"mausoleum_small": (64, 80), "mausoleum_big": (96, 112), "tomb_chest": (99, 14), "railing": (99, 16)}


def sha256(path):
	return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_palette(names):
	"""Programmatic palette guard. Returns a list of (file, x, y, rgb, reason)."""
	bad = []
	for n in names:
		im = load_png(os.path.join(OUT, n + ".png"))
		for y in range(im.h):
			for x in range(im.w):
				p = im.get(x, y)
				if p is None or p[3] == 0:
					continue
				R, G, B = p[0], p[1], p[2]
				mx = max(R, G, B)
				if min(R, G, B) >= 0xdc:
					bad.append((n, x, y, p[:3], "near-white"))
				if min(G, B) - R > 30:
					bad.append((n, x, y, p[:3], "cyan"))
				if min(R, B) - G > 14 and mx > 0x28:
					bad.append((n, x, y, p[:3], "violet"))
				if R > G + 14 and G > B + 8 and R > 0x60 and p[:3] != tuple(EMBER[0][:3]):
					bad.append((n, x, y, p[:3], "gold/warm bright"))
				if R > 0x90 and R > G + 55:
					bad.append((n, x, y, p[:3], "bright red"))
				if mx > 0x7a:
					bad.append((n, x, y, p[:3], "too bright for decor"))
	return bad


def board(path, names, scale, bg="1b1e22", pad=4, row_w=330):
	imgs = [load_png(os.path.join(OUT, n + ".png")) for n in names]
	rows, cur, curw = [], [], pad
	for i in imgs:
		if curw + i.w + pad > row_w and cur:
			rows.append(cur)
			cur, curw = [], pad
		cur.append(i)
		curw += i.w + pad
	rows.append(cur)
	H = sum(max(i.h for i in r) + pad * 2 for r in rows)
	b = Canvas(row_w, H)
	b.rect(0, 0, row_w, H, hexc(bg))
	y = 0
	for r in rows:
		rh = max(i.h for i in r) + pad * 2
		x = pad
		for i in r:
			b.blit(i, x, y + rh - pad - i.h)
			x += i.w + pad
		y += rh
	save_png(b, path, scale)


def scale_preview(path, names, scale=3):
	"""Props on a strip of the placeholder N4 terrain (assets/sprites/terrain_stone.png theme 0, seed 0:
	row = phase, column = exposure mask) with a 24x32 knight-size and a ~24x28 skeleton-size grey
	placeholder (NOT the real sprites) for scale."""
	terr = load_png(os.path.join(ROOT, "assets", "sprites", "terrain_stone.png"))

	def tile(col, row):
		t = Canvas(16, 16)
		for y in range(16):
			for x in range(16):
				t.px[y * 16 + x] = terr.get(col * 16 + x, row * 16 + y)
		return t

	imgs = [load_png(os.path.join(OUT, n + ".png")) for n in names]
	W = 8 + 24 + 12 + 24 + 14 + sum(i.w + 8 for i in imgs) + 8
	mh = max(i.h for i in imgs)
	ground = mh + 8
	H = ground + 16 * 3
	b = Canvas(W, H)
	b.rect(0, 0, W, H, hexc("0f121a"))
	for tx in range(0, W, 16):
		ph = (tx // 16) % 6
		b.blit(tile(1, ph), tx, ground)
		for ty in range(ground + 16, H, 16):
			b.blit(tile(0, ph), tx, ty)
	x = 8
	sil = hexc("5a6070")
	for yy in range(32):
		for xx in range(24):
			if yy < 9 and 6 <= xx < 18 or 9 <= yy < 22 and 4 <= xx < 20 or yy >= 22 and (5 <= xx < 11 or 13 <= xx < 19):
				b.put(x + xx, ground - 32 + yy, sil if xx >= 12 else hexc("444a58"))
	x += 36
	sk = hexc("8a8478")
	for yy in range(28):
		for xx in range(24):
			if yy < 8 and 8 <= xx < 16 or 8 <= yy < 20 and 9 <= xx < 15 or yy >= 20 and (8 <= xx < 11 or 13 <= xx < 16):
				b.put(x + xx, ground - 28 + yy, sk if xx >= 12 else hexc("6a665c"))
	x += 38
	for im in imgs:
		b.blit(im, x, ground - im.h)
		x += im.w + 8
	save_png(b, path, scale)


def main(argv):
	os.makedirs(OUT, exist_ok=True)
	os.makedirs(PREVIEW, exist_ok=True)
	meta, rows = [], []
	for name, fn, kind, anchor, lights, weight, big in PROPS:
		if argv and name not in argv:
			continue
		c = fn()
		if name in LIMITS:
			assert c.w <= LIMITS[name][0] and c.h <= LIMITS[name][1], (name, c.w, c.h)
		path = os.path.join(OUT, name + ".png")
		save_png(c, path)
		meta.append({"file": name + ".png", "w": c.w, "h": c.h, "kind": kind, "anchor": anchor(c.w, c.h), "lights": lights, "weight": weight, "big": big})
		rows.append((name, c.w, c.h, kind, anchor(c.w, c.h), lights, sha256(path)))
	bad = check_palette([m["file"][:-4] for m in meta])
	for b_ in bad[:40]:
		print("PALETTE", b_)
	print("palette violations:", len(bad))
	if argv:
		board(os.environ.get("N4_TMP", "/tmp/n4_tmp_board.png"), [n for n, *_ in PROPS if n in argv], int(os.environ.get("N4_SCALE", "4")), row_w=int(os.environ.get("N4_ROW", "330")))
		return
	with open(os.path.join(OUT, "props_n4.json"), "w") as f:
		json.dump(meta, f, indent=1)
	board(os.path.join(PREVIEW, "props_n4_board.png"), [n for n, *_ in PROPS], 3, row_w=330)
	scale_preview(os.path.join(PREVIEW, "props_n4_scale.png"), [n for n, _, k, *_ in PROPS if k == "ground"])
	with open(os.path.join(OUT, "props_n4.sha256"), "w") as f:
		for name, w, h, kind, anc, lights, sha in rows:
			f.write("%s  %s.png\n" % (sha, name))
	sys.exit(1 if bad else 0)


if __name__ == "__main__":
	main(sys.argv[1:])

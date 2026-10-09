"""N3 "Black Forest" decor props (RUN-021 aesthetic pass).

Pure Python (tools/art/pixel.py). Helpers/palettes are imported read-only from world_props.py,
palette.py and palette_run020.py. Everything is decor: dark, desaturated, lower contrast than
gameplay sprites, no outlines, soft light from the upper left (moon side).
EMBER only in the charcoal-camp embers, the shrine candle and the hunter lantern glass (no flame
is painted: scripts/campaign_decor.gd draws flames/glows at the light points of props_n3.json).
FIREFLY only as 1-3 px glints (fungus); MOON only as rare cold rim pixels on the moon side.

Run:  python3 tools/art/run021/n3/props_n3.py [name ...]
Writes assets/run021/n3/props/*.png, props_n3.json, props_n3.sha256 and the preview boards in
work/run021/n3pass/preview/ (props_n3_board.png, props_n3_scale.png).
"""
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
from pixel import Canvas, hexc, line, save_png  # noqa: E402
from palette import EMBER, MOSS, STONE_COOL, WOOD  # noqa: E402
from world_props import BONE, mix  # noqa: E402  (read only)
from palette_run020 import NIGHT, PINE, SOIL  # noqa: E402
from pngio import load_png  # noqa: E402

OUT = os.path.join(ROOT, "assets", "run021", "n3", "props")
PREVIEW = os.path.join(ROOT, "work", "run021", "n3pass", "preview")
MOON = [hexc(c) for c in ("1c2433", "2a3448", "3e4c66", "5a6c8a", "8496b4", "b8c6dc")]
FIREFLY = [hexc(c) for c in ("2c4a40", "4f7a66", "86b49c", "b4dcc8")]

# ----------------------------------------------------------------------------- materials (dark -> light)
BARK = [mix(WOOD[i], NIGHT[i + 1], 0.46) for i in range(5)]  # cold dark bark
BARK_D = [mix(BARK[i], NIGHT[1], 0.38) for i in range(5)]  # even darker (back / underground)
LEAF = [PINE[0], PINE[1], PINE[2], PINE[3], PINE[4]]  # foliage
MS = [mix(mix(MOSS[i], PINE[i], 0.5), NIGHT[3], 0.18) for i in range(4)]  # cold moss
LICHEN = [hexc(c) for c in ("1f2a28", "2f3f3a", "46594f", "627669")]  # old man's beard, greyer
STN = STONE_COOL
BIRCH = [hexc(c) for c in ("14161a", "202327", "32363a", "484d51", "5f6468")]  # dim pale bark
CAP = [hexc(c) for c in ("1d272c", "2f3f47", "4b6068", "6f8a90")]  # pale blue-grey fungus caps
GILL = hexc("141b1f")
VOID = hexc("07080b")
ROOTD = [hexc(c) for c in ("0c0d10", "131418", "1b1c21", "25262c")]  # very dark underground roots
EARTHD = [hexc(c) for c in ("0b0b0e", "111114", "18181c", "212126")]
CORD = [hexc("2a2620"), hexc("403a30")]
IRON = [hexc("101216"), hexc("1b1f26"), hexc("2a303a"), hexc("3d4552")]
RU = [hexc("1f130e"), hexc("33201a"), hexc("4a2e22")]
ASH = [hexc("14120f"), hexc("221e1a"), hexc("342e28"), hexc("463f37")]
TBONE = [mix(BONE[0], NIGHT[1], 0.25), mix(BONE[1], NIGHT[2], 0.62), mix(BONE[1], NIGHT[2], 0.45), mix(BONE[2], NIGHT[2], 0.6)]  # stag skull: dark bone
BONED = [mix(BONE[i], NIGHT[2], 0.42) for i in range(3)]  # dark bone, <= N2 bone values


def rng(*seed):
	return random.Random("-".join(map(str, ("run021-n3",) + seed)))


# ----------------------------------------------------------------------------- primitives
def clamp(v, lo, hi):
	return max(lo, min(hi, v))


def hl(c, x0, x1, y, col):
	for x in range(x0, x1 + 1):
		c.put(x, y, col)


def vl(c, x, y0, y1, col):
	for y in range(y0, y1 + 1):
		c.put(x, y, col)


def smooth_noise(r, n, scale):
	"""n+1 control values -> callable t(i) smooth in [-1, 1]."""
	vals = [r.uniform(-1, 1) for _ in range(n // scale + 40)]

	def f(i):
		k = i / scale
		a = int(math.floor(k)) % (len(vals) - 1)
		t = k - math.floor(k)
		t = t * t * (3 - 2 * t)
		return vals[a] * (1 - t) + vals[a + 1] * t

	return f


def disk(cells, cx, cy, rad):
	ir = int(math.ceil(rad))
	for y in range(int(cy) - ir, int(cy) + ir + 1):
		for x in range(int(cx) - ir, int(cx) + ir + 1):
			if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad + 0.3:
				cells.add((x, y))


def bez(p0, p1, p2, n=None):
	if n is None:
		n = int(max(abs(p2[0] - p0[0]), abs(p2[1] - p0[1])) * 1.6) + 3
	out = []
	for i in range(n + 1):
		t = i / n
		out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
			(1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
	return out


def stroke(cells, pts, r0, r1):
	n = len(pts)
	for i, (x, y) in enumerate(pts):
		t = i / max(1, n - 1)
		disk(cells, x, y, r0 + (r1 - r0) * t)


def _runs(cells, axis):
	groups = {}
	for (x, y) in cells:
		if axis == "h":
			groups.setdefault(y, []).append(x)
		else:
			groups.setdefault(x, []).append(y)
	info = {}
	for k, vs in groups.items():
		vs.sort()
		start = prev = vs[0]
		for v in vs[1:] + [None]:
			if v is None or v != prev + 1:
				w = prev - start + 1
				for u in range(start, prev + 1):
					pos = (u, k) if axis == "h" else (k, u)
					info[pos] = (u - start, prev - u, w)
				start = v
			prev = v
	return info


def paint(c, cells, ramp, r, axis="h", shift=0, furrows=0, seg=(8, 18), top_hi=True, under=False, noise=True, wide_rim=14, lit=None):
	"""Shade a set of cells as a rounded form lit from the upper left.

	axis 'h': tone across each row (left lit, right dark); 'v': across each column (top lit).
	furrows: number of dark vertical fissures following the form (broken segments)."""
	info = _runs(cells, axis)
	top = len(ramp) - 2 if lit is None else lit  # max body tone
	fur = []
	if furrows:
		y0 = min(y for _, y in cells)
		y1 = max(y for _, y in cells)
		for j in range(furrows):
			f = (j + 0.5) / furrows + r.uniform(-0.06, 0.06)
			sl = r.randint(*seg)
			on = {}
			for yy in range(y0 - 2, y1 + 3):
				kk = yy // sl
				if kk not in on:
					on[kk] = r.random() > 0.28
			wob = smooth_noise(r, y1 - y0 + 6, 7)
			fur.append((f, on, sl, wob, y0))
	tones = {}
	F = set()
	for (x, y), (a, b, w) in info.items():
		if w == 1:
			k = top - 1
		elif w == 2:
			k = top if a == 0 else top - 2
		elif w == 3:
			k = top if a == 0 else top - 2 if b == 0 else top - 1
		else:
			frac = a / (w - 1)
			if a == 0 or (w >= wide_rim and a == 1):
				k = top
			elif b == 0 or (w >= wide_rim and b == 1):
				k = top - 3
			elif frac < 0.42:
				k = top - 1
			elif frac < 0.75:
				k = top - 2
			else:
				k = top - 3 + (1 if frac < 0.82 else 0)
		for (f, on, sl, wob, y0) in fur:
			if w >= 6 and on.get(y // sl, True):
				pos = (a + 0.5) / w
				if abs(pos - (f + wob(y - y0 + 3) * 0.04)) * w < 0.62 + (0.3 if w > 20 else 0):
					F.add((x, y))
					break
		if noise:
			if (x * 7 + y * 13) % 11 == 0:
				k -= 1
			elif (x * 3 + y * 11) % 19 == 0:
				k += 1
		if top_hi and ((x, y - 1) not in cells) and (axis == "h" or a == 0):
			k += 1
		if under and (x, y + 1) not in cells:
			k -= 1
		tones[(x, y)] = k
	for (x, y), k in tones.items():
		if (x, y) in F:
			k = min(k, top - 2) - 1
		elif (x + 1, y) in F:
			k += 1  # lit ridge beside a crevice
		c.put(x, y, ramp[clamp(k + shift, 0, len(ramp) - 1)])


def edge_cells(cells, side="top"):
	out = []
	for (x, y) in cells:
		if side == "top" and (x, y - 1) not in cells:
			out.append((x, y))
		elif side == "left" and (x - 1, y) not in cells:
			out.append((x, y))
		elif side == "bottom" and (x, y + 1) not in cells:
			out.append((x, y))
	return out


def moon_rim(c, cells, r, p=0.12, cx=None, ymax=None):
	"""A few dim cold rim pixels on the moon (upper-left) side."""
	for (x, y) in sorted(edge_cells(cells, "left")):
		if ymax is not None and y > ymax:
			continue
		if r.random() < p:
			c.put(x, y, MOON[2] if r.random() < 0.7 else MOON[3])


def moss_cap(c, cells, r, ramp=None, p=0.7, depth=2, x0=None, x1=None, y0=None, y1=None):
	"""Moss growing on the top-facing surface of `cells` (organic, ragged, never a flat band)."""
	ramp = ramp or MS
	for (x, y) in sorted(edge_cells(cells, "top")):
		if x0 is not None and not (x0 <= x <= x1):
			continue
		if y0 is not None and not (y0 <= y <= y1):
			continue
		if r.random() > p:
			continue
		d = r.choice([1, depth, depth, depth + 1])
		for i in range(d):
			if (x, y + i) in cells:
				k = 3 if (i == 0 and (x + y) % 4 == 0) else 2 if i == 0 else 1 if (x + i) % 3 else 0
				c.put(x, y + i, ramp[k])


def moss_blob(c, cells, cx, cy, rx, ry, r, ramp=None, k=1.0, over=None):
	ramp = ramp or MS
	blob = set()
	for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
		for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
			d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
			if d + (r.random() - 0.5) * 0.6 < k and (x, y) in cells:
				blob.add((x, y))
	for (x, y) in blob:
		kk = 1
		if (x, y - 1) not in blob or ((x - 1, y) not in blob and (x + y) % 2):
			kk = 2
		if (x + 2 * y) % 5 == 0:
			kk = 0 if kk == 1 else 3
		if (x, y + 1) not in blob and kk == 1:
			kk = 0
		c.put(x, y, ramp[kk])
	return blob


def hang_strand(c, x, y, length, ramp, r, sway=0.6, thick=1):
	"""Thin hanging strand (roots / lichen)."""
	ph = r.uniform(0, 6)
	for i in range(length):
		xx = x + int(round(math.sin(i * 0.35 + ph) * sway))
		t = i / max(1, length - 1)
		k = 2 if t < 0.5 else 1 if t < 0.85 else 0
		c.put(xx, y + i, ramp[k])
		if thick > 1 and t < 0.6:
			c.put(xx + 1, y + i, ramp[max(0, k - 1)])


def glints(c, pts, ramp_i=1, col=None):
	for (x, y) in pts:
		c.put(x, y, col or FIREFLY[ramp_i])


def paint_dir(c, cells, ramp, r, lit=3, shift=0, noise=True, cap=6):
	"""Shade arbitrary rounded forms (roots, limbs, logs, stones): the lit side is up-left."""
	def dist(x, y, dx, dy):
		n = 0
		while n < cap and (x + dx * (n + 1), y + dy * (n + 1)) in cells:
			n += 1
		return n

	for (x, y) in cells:
		a = min(dist(x, y, -1, 0), dist(x, y, 0, -1))
		b = min(dist(x, y, 1, 0), dist(x, y, 0, 1))
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
			elif (x * 3 + y * 11) % 17 == 0:
				k += 1
		c.put(x, y, ramp[clamp(k + shift, 0, len(ramp) - 1)])


def blob(cells, cx, cy, rx, ry, r, jag=0.25, k=1.0):
	for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
		for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
			d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
			if d + (r.random() - 0.5) * jag < k:
				cells.add((x, y))


STD = [mix(STN[i], NIGHT[2], 0.2) for i in range(6)]  # stones, a little darker/colder than the ground

# ============================================================================= GROUND
def ancient_trunk():
	W, H = 56, 128
	c = Canvas(W, H)
	r = rng("ancient_trunk")
	nl = smooth_noise(r, H, 9)
	nr = smooth_noise(r, H, 9)
	nc = smooth_noise(r, H, 40)
	cells = set()
	for y in range(H):
		cx = 28 + 1.6 * nc(y)
		hw = 12.5 + 1.2 * math.sin(y * 0.07) + 1.6 * math.exp(-((y - 70) / 14.0) ** 2)
		if y > 86:
			hw += 15.5 * ((y - 86) / 41.0) ** 2.1
		xl = int(round(cx - hw + 0.9 * nl(y)))
		xr = int(round(cx + hw + 0.9 * nr(y)))
		for x in range(xl, xr + 1):
			cells.add((x, y))
	paint(c, cells, BARK, r, furrows=9, seg=(9, 22))
	# horizontal bark checks
	for _ in range(46):
		x, y = r.randint(16, 40), r.randint(2, 100)
		if (x, y) in cells and (x + 1, y) in cells and c.get(x, y) in (BARK[1], BARK[2]):
			c.put(x, y, BARK[0])
			if r.random() < 0.6:
				c.put(x + 1, y, BARK[0])
	# buttress roots over the flare (painted separately so they read as forms)
	roots = []
	for (p0, p1, p2, r0, r1) in (((21, 98), (10, 108), (1, 125), 4.2, 1.2), ((36, 98), (47, 108), (55, 125), 4.2, 1.2),
		((26, 108), (21, 120), (13, 127), 3.2, 1.2), ((32, 108), (36, 120), (43, 127), 3.0, 1.2), ((9, 112), (4, 118), (0, 123), 2.2, 1.0)):
		one = set()
		stroke(one, wavy(bez(p0, p1, p2, n=40), r, 1.4, 4), r0, r1)
		one = {p for p in one if 0 <= p[0] < W and 0 <= p[1] < H}
		roots.append(one)
		paint_dir(c, one, BARK, r, lit=3, cap=5)
	allroots = set().union(*roots)
	# broken branch stubs (cut ends paler)
	for (sx, sy, d, ln) in ((14, 34, -1, 9), (44, 52, 1, 7)):
		stub = set()
		stroke(stub, bez((sx + 2 * -d, sy + 3), (sx + d * ln * 0.5, sy + 1), (sx + d * ln, sy - 3)), 2.8, 2.0)
		paint_dir(c, stub - cells, BARK, r, lit=3, cap=3)
		c.put(sx + d * ln, sy - 3, BARK[4])
		c.put(sx + d * (ln - 1), sy - 3, BARK[3])
		c.put(sx + d * ln, sy - 2, BARK[3])
	# knot hollow
	hx, hy = 29, 74
	hol = set()
	for y in range(hy - 11, hy + 8):
		t = (y - (hy - 11)) / 18.0
		half = 1 + 5.2 * math.sin(min(1.0, t * 1.15) * math.pi * 0.55) ** 0.8 if t < 0.9 else 3.0
		half = half * (1 - max(0.0, (t - 0.75)) * 1.2)
		for x in range(int(round(hx - half)), int(round(hx + half)) + 1):
			hol.add((x, y))
	for (x, y) in hol:
		inner = ((x - hx) / 5.0) ** 2 + ((y - hy + 1) / 9.0) ** 2
		c.put(x, y, VOID if inner < 0.6 else hexc("0c0e12"))
	for (x, y) in sorted(hol):
		if (x - 1, y) not in hol and y < hy + 3:
			c.put(x - 1, y, BARK[3])
		if (x, y - 1) not in hol:
			c.put(x, y - 1, BARK[3] if x < hx else BARK[2])
		if (x + 1, y) not in hol:
			c.put(x + 1, y, BARK[0])
	for x in range(hx - 3, hx + 4):
		c.put(x, hy + 8, BARK[0] if x > hx else BARK[1])
	for (x, y) in ((hx + 1, hy - 3), (hx, hy - 2), (hx - 1, hy)):  # faint cold glint of moisture deep inside
		c.put(x, y, NIGHT[3])
	for (x, y) in ((hx - 2, hy + 8), (hx - 1, hy + 8), (hx, hy + 8), (hx + 2, hy + 9)):
		c.put(x, y, MS[2])
	c.put(hx - 3, hy + 7, MS[1])
	# moss: north-west flank, flare shoulder and root tops
	body = cells | allroots
	moss_blob(c, body, 17, 62, 4.2, 22, r, k=0.95)
	moss_blob(c, body, 15, 108, 7, 5.5, r)
	moss_blob(c, body, 41, 112, 4, 4, r, k=0.8)
	moss_blob(c, body, 21, 22, 4, 9, r, k=0.85)
	moss_cap(c, allroots - cells, r, p=0.8, depth=2)
	# hanging moss from the left stub
	for i, dx in enumerate((-1, 0, 1)):
		hang_strand(c, 6 + i * 2, 36, r.randint(6, 12), LICHEN, r, 0.7)
	moon_rim(c, cells, r, 0.12, ymax=100)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, BARK[0])
	return c


def _tapered_limb(cells, pts, r0, r1):
	stroke(cells, pts, r0, r1)


def gnarled_oak():
	W, H = 74, 96
	c = Canvas(W, H)
	r = rng("gnarled_oak")
	nl = smooth_noise(r, H, 8)
	nr = smooth_noise(r, H, 8)
	cells = set()
	# short fat trunk with a root flare, splitting into limbs at y ~ 52
	for y in range(50, H):
		cx = 36 + 1.5 * math.sin(y * 0.09)
		hw = 9.5 + 1.0 * math.sin(y * 0.2) - max(0, 58 - y) * 0.2
		if y > 74:
			hw += 9.5 * ((y - 74) / 22.0) ** 2
		for x in range(int(round(cx - hw + 0.7 * nl(y))), int(round(cx + hw + 0.7 * nr(y))) + 1):
			cells.add((x, y))
	limbs = []
	spec = [  # (p0, p1, p2, r0, r1)
		((29, 62), (12, 56), (5, 30), 6.0, 2.4),  # left limb sweeping out and up
		((36, 60), (30, 40), (44, 10), 6.2, 2.0),  # kinked leader
		((43, 62), (62, 56), (68, 32), 5.6, 2.2),  # right limb
		((13, 50), (4, 40), (2, 34), 2.6, 1.0),
		((10, 44), (18, 30), (14, 16), 2.8, 1.0),
		((7, 34), (4, 20), (12, 6), 2.2, 0.9),
		((38, 42), (26, 34), (24, 20), 3.0, 1.0),
		((41, 28), (50, 22), (54, 10), 2.6, 1.0),
		((43, 14), (36, 8), (34, 2), 1.8, 0.7),
		((63, 44), (70, 40), (72, 34), 2.4, 0.9),
		((66, 36), (60, 26), (63, 14), 2.2, 0.8),
		((24, 26), (30, 18), (28, 8), 1.8, 0.8),
	]
	for (p0, p1, p2, r0, r1) in spec:
		one = set()
		stroke(one, wavy(bez(p0, p1, p2, n=44), r, 2.2 if r0 > 4 else 1.4, 4), r0, r1)
		limbs.append(one)
	body = set(cells)
	for one in limbs:
		body |= one
	paint(c, cells, BARK, r, furrows=4, seg=(8, 16), wide_rim=10)
	for one in limbs:  # each limb is painted as its own rounded form
		paint_dir(c, one - cells if False else one, BARK, r, lit=3, cap=5)
	# re-blend limb roots into the trunk top
	for (x, y) in sorted(cells):
		if y < 62 and c.get(x, y) is not None and r.random() < 0.15:
			c.put(x, y, BARK[1])
	# crown clusters: ragged dark leaf scatter around the limb tips (holes everywhere, not blobs)
	for (cx, cy, rx, ry, n) in ((7, 14, 8, 8, 62), (42, 7, 10, 7, 70), (63, 17, 7, 8, 54), (24, 17, 6, 6, 38), (56, 36, 7, 5, 30), (5, 30, 5, 4, 22), (14, 6, 5, 4, 20)):
		pts = set()
		for _ in range(n):
			ang = r.uniform(0, math.tau)
			d = math.sqrt(r.random())
			x, y = int(round(cx + math.cos(ang) * rx * d)), int(round(cy + math.sin(ang) * ry * d))
			pts.add((x, y))
			if r.random() < 0.55:
				pts.add((x + 1, y))
			if r.random() < 0.3:
				pts.add((x, y + 1))
		for (x, y) in sorted(pts):
			if c.get(x, y) is None or r.random() < 0.3:
				up = (x, y - 1) not in pts
				k = 2 if (up and x < cx) else 1 if (x + y) % 3 else 0
				if (x + 2 * y) % 7 == 0:
					k = 0
				c.put(x, y, LEAF[k])
	# knot hollow low on the trunk
	hx, hy = 35, 78
	for (x, y) in [(hx + ddx, hy + ddy) for ddy in range(-5, 5) for ddx in range(-3, 4) if (ddx / 3.2) ** 2 + (ddy / 5.2) ** 2 < 1 and ddy > -5 + abs(ddx)]:
		c.put(x, y, VOID if x < hx + 3 else hexc("0c0e12"))
	for dy in range(-4, 5):
		c.put(hx - 4, hy + dy, BARK[3])
	for dx in range(-3, 3):
		c.put(hx + dx, hy - 5, BARK[3])
		c.put(hx + dx, hy + 5, BARK[0])
	moss_blob(c, body, 26, 80, 5, 10, r, k=0.9)
	moss_blob(c, body, 27, 62, 5, 5, r, k=0.9)
	moss_cap(c, set().union(*limbs), r, p=0.35, depth=1)
	moss_blob(c, body, 48, 90, 6, 4, r)
	for x, y, ln in ((14, 38, 9), (18, 42, 7), (22, 46, 11), (50, 44, 6), (58, 48, 8)):  # hanging moss
		hang_strand(c, x, y, ln, LICHEN, r, 0.6)
	moon_rim(c, body, r, 0.12, ymax=75)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, BARK[0])
	return c


# ---- conifers --------------------------------------------------------------------------------
def _fir(W, H, seed, top, fol_bot, env_max, step, droop, band, lean=0.0, sparse=0.0, bias=(1.0, 1.0), trunk_w=3, power=0.95, base_y=None):
	"""Spruce: a triangular envelope filled with drooping boughs; bough length follows a saw-tooth
	so the skirts form ragged tiers. Returns (canvas, foliage cells)."""
	c = Canvas(W, H)
	r = rng(seed)
	cx = W // 2
	base_y = base_y if base_y is not None else H - 1
	lean_f = lambda y: cx + int(round(lean * (base_y - y) / max(1, base_y - top)))
	trunk = set()
	for y in range(top, base_y + 1):
		hw = trunk_w / 2.0 + (1.7 * ((y - (base_y - 10)) / 10.0) ** 2 if y > base_y - 10 else 0)
		for x in range(int(round(lean_f(y) - hw)), int(round(lean_f(y) + hw)) + 1):
			trunk.add((x, y))
	fol = set()
	env = lambda y: env_max * clamp((y - top) / float(fol_bot - top), 0.0, 1.0) ** power
	y0 = top + 3
	row = 0
	while y0 <= fol_bot:
		for si, side in enumerate((-1, 1)):
			if r.random() < sparse * (0.5 + (y0 - top) / float(fol_bot - top)):
				continue
			ph = ((y0 - top) % band) / float(band)  # 0 at tier top .. 1 at tier bottom
			saw = 0.55 + 0.5 * ph
			ln = max(2.0, env(y0 + 5) * saw * r.uniform(0.78, 1.08) * bias[si])
			dr = droop * ln * r.uniform(0.7, 1.2) + 2
			x0 = lean_f(y0)
			p0 = (x0 + side, y0)
			p1 = (x0 + side * ln * 0.55, y0 + dr * 0.15 - 1)
			p2 = (x0 + side * ln, y0 + dr)
			pts = bez(p0, p1, p2)
			m = len(pts)
			for i, (x, y) in enumerate(pts):
				tt = i / max(1, m - 1)
				disk(fol, x, y, 1.9 - 0.9 * tt if tt < 0.95 else 0.5)
				if tt > 0.3:
					for j in range(1, 3):
						if r.random() < 0.5:
							fol.add((int(round(x)), int(round(y)) + j + (1 if tt > 0.7 else 0)))
			xe, ye = int(round(p2[0])), int(round(p2[1]))
			if r.random() < 0.7:
				fol.add((xe, ye + 1))
				fol.add((xe - side, ye + 2))
		y0 += step + r.choice((0, 0, 1))
		row += 1
	# narrow core so the stem reads as foliage-covered but still ragged
	for y in range(top + 3, fol_bot + 4):
		hw = env(y) * 0.28
		for x in range(int(round(lean_f(y) - hw)), int(round(lean_f(y) + hw)) + 1):
			if r.random() > sparse * 0.6:
				fol.add((x, y))
	body_f = {p for p in fol if 0 <= p[0] < W and 0 <= p[1] < H}
	paint(c, trunk, BARK, r, furrows=1, seg=(6, 12), top_hi=False)
	for (x, y) in sorted(body_f):
		up = (x, y - 1) not in body_f
		dn = (x, y + 1) not in body_f
		k = 1
		lx = lean_f(y)
		if up:
			k = 3 if x <= lx + 1 else 2
		elif x < lx - 1 and (x + y) % 2 == 0:
			k = 2
		elif x > lx + 3 and (x + y) % 3:
			k = 0 if (x * 3 + y) % 2 else 1
		if dn:
			k = 0
		if (x * 5 + y * 3) % 7 == 0:
			k = max(0, k - 1)
		c.put(x, y, LEAF[k])
	moon_rim(c, body_f, r, 0.06, ymax=int(H * 0.5))
	return c, body_f


def fir_a():
	W, H = 42, 94
	c, fol = _fir(W, H, "fir_a", top=4, fol_bot=80, env_max=19, step=3, droop=0.34, band=13, trunk_w=3, power=0.9)
	for y in range(1, 9):  # thin leader spike
		c.put(W // 2, y, LEAF[2] if y > 3 else LEAF[3])
	c.put(W // 2 - 1, 7, LEAF[1])
	return c


def fir_b():
	W, H = 46, 84
	c, fol = _fir(W, H, "fir_b", top=12, fol_bot=72, env_max=21, step=4, droop=0.62, band=17, lean=-3, sparse=0.3, bias=(1.15, 0.8), trunk_w=3, power=0.8)
	# bare snapped crown with a dead side twig
	cx = W // 2 - 3
	for y in range(4, 14):
		c.put(cx + (y - 4) // 5 - 1, y, BARK[2] if y % 2 else BARK[1])
		c.put(cx + (y - 4) // 5, y, BARK[1])
	c.put(cx - 1, 4, BARK[3])
	c.put(cx - 2, 3, BARK[1])
	line(c, cx, 10, cx + 6, 6, BARK[1])
	line(c, cx - 1, 8, cx - 5, 5, BARK[1])
	return c


def dead_birch():
	W, H = 28, 80
	c = Canvas(W, H)
	r = rng("dead_birch")
	nc = smooth_noise(r, H, 22)
	cells = set()
	for y in range(3, H):
		t = (H - 1 - y) / float(H - 4)
		cx = 13 + 2.4 * nc(y) + 1.2 * t
		hw = 3.0 - 1.4 * t + (2.8 * ((y - (H - 9)) / 8.0) ** 2 if y > H - 9 else 0)
		for x in range(int(round(cx - hw)), int(round(cx + hw)) + 1):
			cells.add((x, y))
	for (x, y) in list(cells):  # ragged snapped top
		if y < 9 and (x * 5 + y) % 3 == 0 and y < 7:
			cells.discard((x, y))
	roots = set()
	stroke(roots, bez((11, 77), (7, 78), (2, 79)), 1.7, 0.6)
	stroke(roots, bez((16, 77), (20, 78), (25, 79)), 1.7, 0.6)
	allc = cells | roots
	paint(c, allc, BIRCH, r, noise=False, top_hi=False, lit=3, shift=0)
	# paper-bark lenticels: short dark dashes across the trunk, peeling flecks
	for y in range(8, H - 6):
		if r.random() < 0.2:
			row = sorted(x for (x, yy) in cells if yy == y)
			if row:
				x0 = row[0] + r.randint(0, 1)
				ln = r.randint(1, 3)
				for x in range(x0, min(row[-1], x0 + ln) + 1):
					c.put(x, y, BIRCH[1])
	for y in range(14, H - 12, 8):  # black scars where branches fell
		row = sorted(x for (x, yy) in cells if yy == y)
		if row:
			c.put(row[len(row) // 2], y, BIRCH[0])
			c.put(row[len(row) // 2], y + 1, BIRCH[0])
			c.put(row[len(row) // 2] - 1, y + 1, BIRCH[0])

	def twig(x0, y0, dx, dy, ln, depth):
		pts = wavy(bez((x0, y0), (x0 + dx * ln * 0.55, y0 + dy * ln * 0.55), (x0 + dx * ln, y0 + dy * ln)), r, 1.4, 2)
		m = len(pts)
		for i, (x, y) in enumerate(pts):
			col = BIRCH[2] if i < m * 0.5 else BIRCH[1]
			c.put(int(round(x)), int(round(y)), col)
			if i < m * 0.35:
				c.put(int(round(x)) + 1, int(round(y)), BIRCH[0])
		if depth:
			for fr in (0.45, 0.75):
				j = int(m * fr)
				fx, fy = pts[j]
				twig(int(round(fx)), int(round(fy)), dx * r.choice((-0.6, 0.5, 0.9)), dy * 0.8 - 0.2, max(4, int(ln * 0.45)), depth - 1)

	for (bx, by, dx, dy, ln) in ((14, 30, -1.0, -0.6, 13), (15, 21, 0.9, -0.7, 11), (14, 44, 1.0, -0.35, 10), (12, 52, -0.9, -0.15, 8), (13, 14, -0.5, -0.9, 7), (14, 62, 0.8, -0.2, 5)):
		twig(bx, by, dx, dy, ln, 1)
	moss_blob(c, allc, 13, 77, 6, 3, r, k=0.9)
	moon_rim(c, cells, r, 0.05, ymax=60)
	return c


def root_arch():
	W, H = 48, 26
	c = Canvas(W, H)
	r = rng("root_arch")
	cells = set()
	# one thick root ring forming the arch, plus a second root twisting over it
	ring = wavy(bez((5, 25), (1, 3), (24, 3), n=40), r, 1.3, 3) + wavy(bez((24, 3), (47, 3), (43, 25), n=40), r, 1.3, 3)
	n = len(ring)
	for i, (x, y) in enumerate(ring):
		t = i / (n - 1)
		foot = max(abs(t - 0.5) * 2, 0)
		disk(cells, x, y, 2.6 + 2.1 * foot ** 3 + (0.4 if i % 9 < 3 else 0))
	cross = wavy(bez((13, 25), (11, 8), (30, 7), n=36), r, 1.6, 3) + wavy(bez((30, 7), (40, 9), (37, 25), n=30), r, 1.6, 3)
	for i, (x, y) in enumerate(cross):
		disk(cells, x, y, 1.6 + 0.8 * (i % 11 < 4))
	stroke(cells, wavy(bez((0, 24), (9, 20), (18, 25)), r, 1.0, 3), 2.3, 0.9)
	stroke(cells, wavy(bez((47, 24), (41, 20), (31, 25)), r, 1.0, 3), 2.2, 0.9)
	for (kx, ky) in ((3, 12), (44, 14), (16, 6)):  # knobs
		disk(cells, kx, ky, 2.2)
	paint_dir(c, cells, BARK, r, lit=3, cap=5)
	moss_cap(c, cells, r, p=0.7, depth=2)
	moss_blob(c, cells, 4, 17, 3.5, 6, r, k=0.8)
	for x in (14, 19, 29, 34):  # rootlets under the arch
		hang_strand(c, x, 9 if 17 < x < 31 else 12, r.randint(4, 8), BARK_D, r, 0.5)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, BARK[0])
	moon_rim(c, cells, r, 0.06)
	return c


def fallen_log():
	W, H = 56, 12
	c = Canvas(W, H)
	r = rng("fallen_log")
	nl = smooth_noise(r, W, 5)
	cells = set()
	cut = 43  # the log breaks here; right of it only the hollow shell remains
	for x in range(1, 54):
		rad = 3.7 - 0.35 * (x / 52.0) + 0.55 * nl(x)
		cy = 7.4 + 0.3 * nl(x + 20)
		for y in range(int(round(cy - rad)), int(round(cy + rad)) + 1):
			if y <= 10:
				cells.add((x, y))
	for x in range(cut, 54):  # torn shell: upper half missing, ragged splinters
		t = (x - cut) / 10.0
		lim = int(5 + t * 4)
		for y in range(0, lim):
			cells.discard((x, y))
	for x, top in ((cut + 1, 2), (cut + 3, 3), (cut + 4, 1), (cut + 6, 3), (cut + 8, 4), (cut + 9, 5)):
		for y in range(top, 6):
			cells.add((x, y))
	hollow = {(x, y) for x in range(cut + 2, 52) for y in range(5 + int((x - cut - 2) * 0.35), 9)}
	shell = {p for p in cells if p not in hollow}
	paint_dir(c, shell, BARK, r, lit=3, cap=4)
	for (x, y) in hollow:
		if (x, y) in cells:
			c.put(x, y, VOID if y > 6 else BARK_D[1])
	for (x, y) in sorted(shell):  # pale rotten rim of the break
		if x >= cut and any(((x + dx, y + dy) in hollow) for dx, dy in ((0, -1), (-1, 0), (0, 1))):
			c.put(x, y, BARK[3] if (x + y) % 3 else BARK[2])
	for x in range(3, cut):  # bark grain along the log
		if (x * 5) % 7 < 2:
			y = 4 + (x * 3) % 6
			for i in range(r.randint(2, 5)):
				if c.get(x + i, y) in (BARK[1], BARK[2]):
					c.put(x + i, y, BARK[0])
	body = {p for p in shell if p[0] < cut}
	# moss lumps growing over the top: irregular mounds of different height (ragged silhouette)
	mound = set()
	for (mx, w, hgt) in ((5, 6, 3), (14, 4, 2), (19, 8, 3), (31, 5, 2), (35, 7, 3), (11, 3, 1)):
		for x in range(mx, mx + w):
			top = min(y for (xx, y) in body if xx == x) if any(xx == x for (xx, _) in body) else 4
			prof = hgt * math.sin(math.pi * (x - mx + 0.5) / w) ** 0.8
			for y in range(top - int(round(prof)) - (1 if (x * 7) % 5 == 0 else 0), top):
				mound.add((x, y))
	for (x, y) in mound:
		k = 2
		if (x, y - 1) not in mound:
			k = 3 if (x + y) % 3 == 0 else 2
		elif (x - 1, y) not in mound:
			k = 2
		else:
			k = 1 if (x + y) % 3 else 0
		c.put(x, y, MS[k])
	moss_cap(c, body, r, p=0.7, depth=2)
	for (x, y, ln) in ((13, 3, 3), (26, 3, 3), (39, 4, 2)):  # snapped twig stubs
		for i in range(ln):
			c.put(x - i // 2, y - i, BARK[2] if i % 2 == 0 else BARK[1])
	for x in range(0, 54):  # soil line + shadow
		if c.get(x, 11) is not None:
			c.put(x, 11, BARK[0])
	for x in (0, 1, 2, 53):
		c.put(x, 11, BARK_D[1])
	moon_rim(c, body, r, 0.05)
	return c


def _fern(variant):
	W, H = 22, 14
	c = Canvas(W, H)
	r = rng("fern", variant)
	cx = 11
	ramp = [PINE[1], PINE[2], PINE[3], mix(PINE[3], MS[3], 0.45)]
	fronds = [(-10, 4, 4.5), (-6, 9, 8), (-1, 12, 6), (5, 10, 7), (9, 5, 5)] if variant == 0 else \
		[(-9, 7, 6), (-4, 11, 4), (1, 9, 8), (6, 12, 5), (10, 4, 4)]
	for dx, dy, bend in fronds:
		xe, ye = cx + dx, 13 - dy + (2 if abs(dx) > 8 else 0)
		ctrl = (cx + dx * 0.3, 13 - dy - bend * 0.55)
		pts = bez((cx, 13), ctrl, (xe, ye), n=26)
		m = len(pts)
		for i, (x, y) in enumerate(pts):
			t = i / (m - 1)
			c.put(int(round(x)), int(round(y)), ramp[1] if t < 0.5 else ramp[2])
			if 5 <= i < m - 1 and i % 2 == 1:
				a, b = pts[i - 1], pts[i + 1]
				nx, ny = b[0] - a[0], b[1] - a[1]
				ln = math.hypot(nx, ny) or 1.0
				px, py = -ny / ln, nx / ln
				reach = 1 + int(round(1.6 * math.sin(math.pi * min(1.0, (t - 0.1) * 1.15))))
				for sgn in (-1, 1):
					for j in range(1, reach + 1):
						xx, yy = int(round(x + px * j * sgn + nx / ln * 0.4 * j)), int(round(y + py * j * sgn + ny / ln * 0.4 * j + 0.6 * j))
						if c.get(xx, yy) is None:
							c.put(xx, yy, ramp[2] if (j == 1 and sgn < 0) else ramp[1] if j == 1 else ramp[0])
		# curled tip
		tx, ty = pts[-1]
		c.put(int(round(tx)), int(round(ty)) + 1, ramp[0])
	for y in range(11, 14):
		c.put(cx, y, BARK[1])
	for dx in (-2, -1, 0, 1, 2):
		c.put(cx + dx, 13, BARK[0])
	for x, y in ((3, 8), (14, 3), (18, 9), (8, 4)):
		if c.get(x, y) is not None:
			c.put(x, y, ramp[3])
	return c


def fern_a():
	return _fern(0)


def fern_b():
	return _fern(1)


def mushroom_cluster():
	W, H = 18, 12
	c = Canvas(W, H)
	r = rng("mushrooms")
	for x in range(1, 17):  # moss / litter bed
		c.put(x, 11, BARK[0])
		if x % 3 != 1:
			c.put(x, 10, MS[1] if x % 2 else MS[0])
	for (x, y) in ((2, 10), (3, 10), (11, 10), (12, 10), (13, 10), (7, 10)):
		c.put(x, y, MS[2])
	_mushroom(c, 6, 10, 3, 2, 4, CAP, GILL, FIREFLY[2])
	_mushroom(c, 12, 10, 2, 2, 3, CAP, GILL, FIREFLY[1])
	_mushroom(c, 9, 10, 2, 1, 2, [CAP[0], CAP[1], CAP[1], CAP[2]], GILL)
	_mushroom(c, 2, 10, 1, 1, 2, [CAP[0], CAP[1], CAP[1], CAP[2]], GILL)
	c.put(14, 8, FIREFLY[0])
	return c


def standing_stone():
	W, H = 20, 40
	c = Canvas(W, H)
	r = rng("standing_stone")
	nl = smooth_noise(r, H, 6)
	nr = smooth_noise(r, H, 6)
	cells = set()
	for y in range(2, H):
		t = (y - 2) / float(H - 3)
		xl = 3.5 - 2.5 * t * t - (1.4 if y < 8 else 0) * 0 + 0.9 * nl(y)
		xr = 16.5 + 1.6 * t * t - 3.2 * max(0.0, 1 - t * 2.2) + 0.9 * nr(y)
		if y < 6:  # slanted, irregular top
			xr -= (6 - y) * 1.1
			xl += (6 - y) * 0.1 - 1.0
		for x in range(int(round(xl + 0.5 * 1)), int(round(xr)) + 1):
			cells.add((x, y))
	for (x, y) in list(cells):  # chipped corner and slanted summit
		if y < 4 + (x - 3) * 0.28 - 1.5:
			cells.discard((x, y))
	paint_dir(c, cells, STD, r, lit=3, cap=7)
	# cracks and weathering
	for (x0, y0, x1, y1) in ((9, 12, 11, 20), (6, 27, 9, 33), (13, 25, 12, 30)):
		for (x, y) in zip(range(x0, x1 + 1) if x1 > x0 else [x0] * (y1 - y0 + 1), range(y0, y1 + 1)):
			if (x, y) in cells:
				c.put(x, y, STD[0])
	for (x, y) in r.sample(sorted(cells), 14):
		c.put(x, y, STD[1] if (x + y) % 2 else STD[3])
	# faint cold rune: algiz-like stem with two arms
	for (x, y) in ((9, 20), (9, 21), (9, 22), (9, 23), (9, 24), (9, 25), (7, 17), (8, 18), (9, 19), (11, 17), (10, 18)):
		if (x, y) in cells:
			c.put(x, y, MOON[1] if y > 18 else MOON[2])
	for (x, y) in ((7, 17), (11, 17), (9, 22)):
		c.put(x, y, MOON[3])
	for (x, y) in ((9, 26), (8, 21)):  # chipped notches beside the rune
		c.put(x, y, STD[0])
	moss_blob(c, cells, 8, 36, 8, 4.5, r, k=1.0)
	moss_cap(c, cells, r, p=0.6, depth=2, y0=0, y1=8)
	moss_blob(c, cells, 4, 24, 2.2, 8, r, k=0.9)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, STD[0])
	moon_rim(c, cells, r, 0.08, ymax=26)
	return c


def cairn():
	W, H = 20, 22
	c = Canvas(W, H)
	r = rng("cairn")
	stones = [(10, 18, 9, 3.8, 0), (6, 19, 4, 3, -1), (14, 18.5, 5, 3.4, 0), (9, 13, 6.5, 3.4, 1), (12, 12, 4, 3, 0), (10, 8, 4.8, 3.0, 0), (9.5, 4.6, 3.0, 2.6, 1)]
	for (cx, cy, rx, ry, sh) in stones:
		cells = set()
		blob(cells, cx, cy, rx, ry, r, jag=0.35)
		cells = {p for p in cells if 0 <= p[1] < H}
		paint_dir(c, cells, STD, r, lit=3, shift=sh - 0, cap=5)
		for (x, y) in sorted(cells):  # dark seam under each stone
			if (x, y + 1) not in cells and c.get(x, y + 1) is not None:
				c.put(x, y + 1, STD[0])
		moss_cap(c, cells, r, p=0.35, depth=1)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, STD[0])
	return c


def wavy(pts, r, amp=1.2, scale=3):
	"""Perturb a polyline perpendicular to its direction (gnarled, twisting roots and limbs)."""
	f = smooth_noise(r, len(pts) + 4, scale)
	out = []
	for i, (x, y) in enumerate(pts):
		a = pts[max(0, i - 1)]
		b = pts[min(len(pts) - 1, i + 1)]
		dx, dy = b[0] - a[0], b[1] - a[1]
		ln = math.hypot(dx, dy) or 1.0
		k = f(i) * amp * math.sin(math.pi * min(1.0, i / max(1, len(pts) - 1) * 1.0)) ** 0.5
		out.append((x - dy / ln * k, y + dx / ln * k))
	return out


def scale_preview(path, names, scale=3):
	"""Props on a strip of the current N3 terrain colours with a 24x32 knight-size and a ~24x28
	skeleton-size grey placeholder (NOT the real sprites) for scale."""
	terr = load_png(os.path.join(ROOT, "assets", "run021", "n3", "terrain_black_forest_n3.png"))

	def tile(col, row):
		t = Canvas(16, 16)
		for y in range(16):
			for x in range(16):
				t.px[y * 16 + x] = terr.get(col * 16 + x, row * 16 + y)
		return t

	imgs = [load_png(os.path.join(OUT, n + ".png")) for n in names]
	W = 8 + 24 + 12 + 24 + 14 + sum(i.w + 8 for i in imgs) + 8
	H = 150
	ground = 126
	b = Canvas(W, H)
	b.rect(0, 0, W, H, hexc("0f141c"))
	for tx in range(0, W, 16):
		b.blit(tile(1, 0), tx, ground)
		for ty in range(ground + 16, H, 16):
			b.blit(tile(0, 1), tx, ty)
	x = 8
	sil = hexc("5a6070")
	for yy in range(32):  # knight-size placeholder 24x32
		for xx in range(24):
			if yy < 9 and 6 <= xx < 18 or 9 <= yy < 22 and 4 <= xx < 20 or yy >= 22 and (5 <= xx < 11 or 13 <= xx < 19):
				b.put(x + xx, ground - 32 + yy, sil if xx < 12 else hexc("444a58"))
	x += 36
	sk = hexc("8a8478")
	for yy in range(28):  # skeleton-size placeholder 24x28
		for xx in range(24):
			if yy < 8 and 8 <= xx < 16 or 8 <= yy < 20 and 9 <= xx < 15 or yy >= 20 and (8 <= xx < 11 or 13 <= xx < 16):
				b.put(x + xx, ground - 28 + yy, sk if xx < 12 else hexc("6a665c"))
	x += 38
	for im in imgs:
		b.blit(im, x, ground - im.h)
		x += im.w + 8
	save_png(b, path, scale)


def stag_totem():
	W, H = 26, 58
	c = Canvas(W, H)
	r = rng("stag_totem")
	cx = 13
	bone = TBONE
	# pole (weathered, leaning a little)
	pole = set()
	nl = smooth_noise(r, H, 8)
	for y in range(15, H):
		lean = 0.8 * (H - y) / H
		hw = 2.0 + (1.2 * ((y - (H - 8)) / 8.0) ** 2 if y > H - 8 else 0)
		for x in range(int(round(cx - hw + lean + 0.4 * nl(y))), int(round(cx + hw + lean + 0.4 * nl(y + 9))) + 1):
			pole.add((x, y))
	paint(c, pole, BARK, r, furrows=2, seg=(5, 11), top_hi=False, wide_rim=99)
	for yy in (28, 29, 43, 44):  # lashings
		for x in range(cx - 3, cx + 4):
			if (x, yy) in pole or abs(x - cx) <= 2:
				c.put(x, yy, CORD[1] if (x + yy) % 2 else CORD[0])
	# skull on the pole top: dark, small
	rows = {5: (-2, 2), 6: (-3, 3), 7: (-3, 3), 8: (-3, 3), 9: (-3, 3), 10: (-2, 2), 11: (-2, 2), 12: (-1, 1), 13: (-1, 1), 14: (-2, 2), 15: (-1, 1)}
	for y, (a, b) in rows.items():
		for x in range(cx + a, cx + b + 1):
			k = 3 if (x == cx + a and y < 12) else 2 if x < cx else 1
			if y >= 14:
				k = 1 if x >= cx else 2
			c.put(x, y, bone[k])
	for (x, y) in ((cx - 2, 8), (cx - 1, 8), (cx + 1, 8), (cx + 2, 8), (cx - 2, 9), (cx + 2, 9)):
		c.put(x, y, hexc("08090b"))
	c.put(cx, 11, bone[0])
	c.put(cx - 1, 14, bone[0])
	c.put(cx + 1, 14, bone[0])
	c.put(cx, 6, bone[3])
	# antlers: main beams sweep out and up, tines branch off
	for side in (-1, 1):
		beam = wavy(bez((cx + side * 3, 7), (cx + side * 12, 9), (cx + side * 10, -1), n=28), r, 0.6, 3)
		for i, (x, y) in enumerate(beam):
			col = bone[2] if side < 0 else bone[1]
			c.put(int(round(x)), int(round(y)), col)
			if i < 12:
				c.put(int(round(x)) + side, int(round(y)), bone[1])
		for fr, ln, ang in ((0.3, 5, 0.7), (0.5, 6, 0.45), (0.72, 5, 0.3), (0.9, 3, 0.15)):
			bx, by = beam[int(len(beam) * fr)]
			for j in range(1, ln + 1):
				c.put(int(round(bx - side * j * ang)), int(round(by - j * 0.95)), bone[2] if side < 0 else bone[1])
	# hanging twig charms and bone beads from the antlers and lashings
	def hang(x, y0, y1, item):
		for y in range(y0, y1):
			c.put(x, y, CORD[1] if y % 2 else CORD[0])
		item(x, y1)

	def twig_star(x, y):
		for (dx, dy) in ((-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2), (2, -2), (1, -1), (-1, 1), (-2, 2)):
			c.put(x + dx, y + dy, BARK[3] if dx <= 0 else BARK[2])
		c.put(x, y, CORD[1])

	def bones(x, y):
		for dy in (0, 1, 2):
			c.put(x, y + dy, bone[2] if dy != 1 else bone[1])
		c.put(x - 1, y, bone[1])
		c.put(x + 1, y + 2, bone[1])

	def feather(x, y):
		for i in range(5):
			c.put(x + (i > 2), y + i, BARK[2] if i < 3 else BARK[1])
		c.put(x - 1, y + 1, BARK[1])

	hang(cx - 11, 3, 19, twig_star)
	hang(cx + 10, 0, 14, bones)
	hang(cx - 5, 18, 31, feather)
	hang(cx + 4, 32, 38, bones)
	# base: stacked stones, moss
	for (sx, sy, rx, ry) in ((cx - 5, H - 3, 4.5, 2.8), (cx + 5, H - 3, 4.2, 2.6), (cx, H - 5, 3.2, 2.4), (cx - 8, H - 2, 2.5, 1.8)):
		sc = set()
		blob(sc, sx, sy, rx, ry, r, jag=0.3)
		sc = {p for p in sc if p[1] < H}
		paint_dir(c, sc, STD, r, lit=3, cap=4)
		moss_cap(c, sc, r, p=0.5, depth=1)
	moss_blob(c, pole, cx - 1, 50, 2.5, 5, r, k=0.9)
	moon_rim(c, pole, r, 0.08)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, STD[0])
	return c


def charcoal_camp():
	W, H = 62, 38
	c = Canvas(W, H)
	r = rng("charcoal_camp")
	ground = H - 1
	# ---- lean-to: back post, front fork, ridge pole, boughs over it
	post = set()
	stroke(post, bez((4, ground), (3, 18), (5, 7)), 1.9, 1.5)
	paint_dir(c, post, BARK, r, lit=3, cap=3)
	front = set()
	stroke(front, bez((35, ground), (36, 30), (34, 22)), 1.6, 1.4)
	stroke(front, bez((34, 24), (31, 22), (30, 19)), 0.9, 0.7)
	paint_dir(c, front, BARK, r, lit=3, cap=3)
	# interior (dark) between the roof and the ground: back wall of boughs in shadow
	interior = set()
	for y in range(9, ground + 1):
		xr = 5 + (y - 9) * 31.0 / 28.0 if y < 29 else 36
		for x in range(6, int(min(36, xr + 8))):
			if y > 11 + (x - 6) * 0.54:
				interior.add((x, y))
	for (x, y) in interior:
		k = 0 if (x * 3 + y * 5) % 11 else 1
		c.put(x, y, VOID if k == 0 else hexc("0b0f12"))
	for i in range(18):  # bough ends / bedding catching a little light inside
		x, y = r.randint(8, 30), r.randint(20, ground - 1)
		if (x, y) in interior:
			c.put(x, y, LEAF[0])
	# bedding of cut boughs on the floor
	for x in range(7, 34):
		for y in range(ground - 2, ground + 1):
			if (x, y) in interior and r.random() < 0.7:
				c.put(x, y, LEAF[0] if (x + y) % 2 else LEAF[1])
	# roof: a thick layer of fir boughs laid on poles, sloping down to the right; ragged lower edge
	roof = set()
	for x in range(1, 40):
		t = (x - 1) / 38.0
		top = 7 + int(t * 24) + (1 if x % 5 == 0 else 0)
		thick = 7 - int(t * 2.5)
		for y in range(top, top + thick):
			roof.add((x, y))
	for (x, y) in sorted(roof):  # boughs hanging past the lower edge
		if (x, y + 1) not in roof and r.random() < 0.65:
			for j in range(1, r.randint(2, 4)):
				roof.add((x, y + j))
	body = {p for p in roof if p[1] < H}
	for (x, y) in sorted(body):
		up = (x, y - 1) not in body
		dn = (x, y + 1) not in body
		k = 1
		if (x * 2 + y) % 4 in (0, 1) and (x + y) % 3:
			k = 2
		if up:
			k = 3 if x < 26 else 2
		if dn or (y % 4 == 3 and (x + y) % 2):
			k = 0
		c.put(x, y, LEAF[clamp(k, 0, 3)])
	# bark strips / poles poking out of the roof edge, ridge pole protruding at the top
	for (x0, y0, x1, y1) in ((2, 6, 9, 9), (14, 13, 21, 18), (27, 22, 38, 29)):
		line(c, x0, y0, x1, y1, BARK[3])
		line(c, x0, y0 + 1, x1, y1 + 1, BARK[1])
	for x in range(0, 6):
		c.put(x, 6 - (1 if x > 3 else 0), BARK[3])
		c.put(x, 7, BARK[1])
	c.put(1, 5, BARK[2])
	moon_rim(c, body, r, 0.04, ymax=24)
	# ---- stone fire ring (flattened ellipse), ash and charcoal
	ox, oy = 50, ground - 4
	ring = []
	for i in range(9):
		ang = math.pi + i * math.tau / 9.0
		ring.append((ox + 10 * math.cos(ang), oy + 3.4 * math.sin(ang), ang))
	# ash bed
	for y in range(oy - 2, oy + 3):
		for x in range(ox - 9, ox + 10):
			if ((x - ox) / 9.5) ** 2 + ((y - oy) / 3.0) ** 2 < 1:
				c.put(x, y, ASH[1] if (x + y) % 3 else ASH[0])
	# charred sticks resting in the ring
	line(c, ox - 6, oy + 1, ox + 1, oy - 3, hexc("120e0c"))
	line(c, ox - 5, oy + 1, ox + 2, oy - 2, hexc("1d1613"))
	line(c, ox + 6, oy + 1, ox + 0, oy - 3, hexc("120e0c"))
	line(c, ox + 5, oy, ox - 1, oy - 3, hexc("221915"))
	for (dx, dy, col) in ((-2, -1, EMBER[0]), (1, -2, EMBER[0]), (3, -1, EMBER[1]), (-4, 0, EMBER[0]), (0, -1, mix(EMBER[0], VOID, 0.3))):
		c.put(ox + dx, oy + dy, col)
	for (sx, sy, ang) in sorted(ring, key=lambda t: t[1]):
		sc = set()
		back = sy < oy
		blob(sc, sx, sy, 3.2 if not back else 2.5, 2.4 if not back else 1.9, r, jag=0.35)
		sc = {p for p in sc if 0 <= p[1] < H}
		paint_dir(c, sc, STD, r, lit=3, shift=0 if not back else -1, cap=4)
		for (x, y) in sorted(sc):
			if (x, y + 1) not in sc and c.get(x, y + 1) is not None and not back:
				c.put(x, y + 1, STD[0])
		if not back:
			moss_cap(c, sc, r, p=0.25, depth=1)
	# charcoal lumps and a leaning stick beside the ring
	for (lx, ly) in ((38, ground - 1), (40, ground), (41, ground - 1)):
		c.put(lx, ly, hexc("0f0d0d"))
		c.put(lx + 1, ly, hexc("1c1816"))
	line(c, 41, ground - 1, 45, ground - 9, BARK[1])
	line(c, 42, ground - 1, 46, ground - 9, BARK[2])
	for x in range(0, W):
		if c.get(x, ground) is not None and c.get(x, ground) not in (VOID,):
			pass
	return c


def forest_shrine():
	W, H = 20, 44
	c = Canvas(W, H)
	r = rng("forest_shrine")
	cx = 10
	# post
	post = set()
	nl = smooth_noise(r, H, 8)
	for y in range(15, H):
		hw = 1.9 + (1.4 * ((y - (H - 7)) / 7.0) ** 2 if y > H - 7 else 0)
		for x in range(int(round(cx - hw + 0.4 * nl(y))), int(round(cx + hw + 0.3 * nl(y + 5))) + 1):
			post.add((x, y))
	paint(c, post, BARK, r, furrows=1, seg=(5, 10), top_hi=False, wide_rim=99)
	# shrine: small open niche under a pitched roof, sitting on a ledge on top of the post
	for y in range(8, 16):  # dark niche
		for x in range(4, 17):
			c.put(x, y, VOID if x > 5 else hexc("0c0e11"))
	for y in range(8, 16):  # corner posts
		c.put(3, y, BARK[3])
		c.put(4, y, BARK[2])
		c.put(16, y, BARK[0])
		c.put(17, y, BARK[1])
	for x in range(2, 19):  # floor ledge
		c.put(x, 16, BARK[3] if x < 10 else BARK[2])
		c.put(x, 17, BARK[0])
	# pitched roof of bark shingles, overhanging
	for y in range(0, 9):
		half = 2 + y * 1.1
		for x in range(int(round(cx - half)), int(round(cx + half)) + 1):
			left = x < cx
			k = 2 if left else 1
			if (y % 3) == 2:
				k = 0
			elif (y % 3) == 0 and y > 0:
				k = 3 if left else 2
			if x == int(round(cx - half)):
				k = 3
			elif x == int(round(cx + half)):
				k = 0
			c.put(x, y, BARK[k])
	for x in range(1, 20):
		c.put(x, 9, BARK[0])
	for (x, y) in ((6, 5), (7, 5), (6, 6), (12, 7), (13, 7), (9, 2)):  # moss on the roof
		c.put(x, y, MS[2] if (x + y) % 2 else MS[1])
	c.put(cx, 0, BARK[3])
	# candle: wax stub, soot, a dull ember at the wick (the flame glow is drawn by the game)
	for y in range(12, 16):
		c.put(9, y, BONED[2] if y > 12 else BONED[1])
		c.put(10, y, BONED[1] if y > 12 else BONED[0])
	c.put(9, 11, hexc("0e0b0a"))
	c.put(9, 12, EMBER[0])
	c.put(8, 15, BONED[0])
	c.put(11, 15, BONED[0])
	# tied twig charms under the eaves
	for x, ln in ((3, 7), (17, 5)):
		for y in range(10, 10 + ln):
			c.put(x - 1 if x < 10 else x + 1, y + 1, CORD[1] if y % 2 else CORD[0])
	c.put(1, 18, BARK[2])
	c.put(2, 17, BARK[2])
	c.put(1, 19, BARK[1])
	c.put(19, 16, BARK[1])
	c.put(19, 17, BARK[2])
	# base stones and moss
	for (sx, sy, rx, ry) in ((6, H - 2, 3.5, 2.3), (14, H - 2, 3.8, 2.4), (10, H - 3, 2.8, 2.0)):
		sc = set()
		blob(sc, sx, sy, rx, ry, r, jag=0.3)
		sc = {p for p in sc if p[1] < H}
		paint_dir(c, sc, STD, r, lit=3, cap=4)
		moss_cap(c, sc, r, p=0.5, depth=1)
	moss_blob(c, post, cx - 1, 30, 2.2, 6, r, k=0.9)
	moon_rim(c, post, r, 0.06)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, STD[0])
	return c


def root_stump():
	W, H = 32, 22
	c = Canvas(W, H)
	r = rng("root_stump")
	cells = set()
	tops = {9: 7, 10: 4, 11: 8, 12: 3, 13: 6, 14: 2, 15: 5, 16: 8, 17: 4, 18: 7, 19: 5, 20: 8, 21: 9}
	for x in range(9, 22):
		for y in range(tops[x], 21):
			cells.add((x, y))
	roots = []
	for (p0, p1, p2, r0, r1) in (((10, 11), (8, 21), (0, 20), 3.6, 1.0), ((20, 11), (23, 21), (31, 20), 3.6, 1.0),
		((12, 14), (11, 21), (5, 21), 2.6, 1.0), ((18, 14), (20, 21), (26, 21), 2.6, 1.0)):
		one = set()
		stroke(one, wavy(bez(p0, p1, p2, n=26), r, 0.9, 3), r0, r1)
		roots.append({p for p in one if p[1] < H})
	body = set(cells)
	paint_dir(c, cells, BARK, r, lit=3, cap=5)
	for one in roots:
		body |= one
		paint_dir(c, one, BARK, r, lit=3, cap=4)
	# torn, splintered top: pale broken wood on the splinter tips, dark hollow between
	hol = {(x, y) for x in range(12, 18) for y in range(5, 10) if ((x - 14.5) / 2.9) ** 2 + ((y - 8) / 2.6) ** 2 < 1}
	for (x, y) in hol:
		c.put(x, y, VOID)
	for x in range(9, 22):
		c.put(x, tops[x], BARK[4] if x % 3 else BARK[3])
		if (x + tops[x]) % 2:
			c.put(x, tops[x] + 1, BARK[3])
	for y in range(9, 19):  # vertical splits
		for x in (12, 17):
			if (x, y) in cells and (y * 3 + x) % 4:
				c.put(x, y, BARK[0])
	moss_blob(c, body, 10, 14, 3.5, 6, r, k=0.9)
	for one in roots:
		moss_cap(c, one, r, p=0.6, depth=2)
	moss_blob(c, body, 20, 12, 2.0, 3, r, k=0.9)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, BARK[0])
	moon_rim(c, body, r, 0.07)
	return c


def owl_snag():
	W, H = 16, 32
	c = Canvas(W, H)
	r = rng("owl_snag")
	nl = smooth_noise(r, H, 6)
	cells = set()
	for y in range(9, H):
		t = (y - 9) / float(H - 10)
		hw = 1.9 + 0.8 * t + (1.8 * ((y - (H - 6)) / 6.0) ** 2 if y > H - 6 else 0)
		cx = 8 + 0.7 * nl(y)
		for x in range(int(round(cx - hw)), int(round(cx + hw)) + 1):
			cells.add((x, y))
	for (x, y) in list(cells):  # slanted broken top
		if y < 11 + (x - 5) * 0.4 - 1:
			cells.discard((x, y))
	stub = set()
	stroke(stub, bez((6, 20), (3, 19), (1, 15)), 1.4, 0.8)
	stroke(stub, bez((10, 25), (13, 24), (14, 21)), 1.2, 0.7)
	body = cells | stub
	paint(c, cells, BARK, r, furrows=1, seg=(5, 9), top_hi=False, wide_rim=99)
	paint_dir(c, stub - cells, BARK, r, lit=3, cap=3)
	moss_blob(c, body, 7, 27, 4, 3, r, k=0.9)
	moss_cap(c, stub, r, p=0.6, depth=1)
	for (x, y) in ((5, 14), (5, 15), (6, 14)):
		c.put(x, y, MS[1])
	# tiny dark owl on the broken top (dark, bluish grey, eyes barely lit)
	ow = [hexc("0d1015"), hexc("161a21"), hexc("20262f"), hexc("2c333d")]
	rows = {3: (-3, -2, 2, 3), 4: (-2, 2), 5: (-2, 2), 6: (-3, 3), 7: (-3, 3), 8: (-2, 2), 9: (-2, 2)}
	cx = 8
	for y, span in rows.items():
		if len(span) == 4:  # ear tufts
			for x in (cx + span[0], cx + span[3]):
				c.put(x, y, ow[2])
			c.put(cx + span[1], y + 1, ow[2])
			c.put(cx + span[2], y + 1, ow[1])
			continue
		for x in range(cx + span[0], cx + span[1] + 1):
			k = 3 if x == cx + span[0] else 0 if x == cx + span[1] else 2 if x < cx else 1
			c.put(x, y, ow[k])
	c.put(cx - 1, 5, FIREFLY[1])  # barely lit eyes
	c.put(cx + 1, 5, FIREFLY[0])
	c.put(cx, 6, ow[3])  # beak
	c.put(cx, 8, ow[3])
	c.put(cx - 1, 9, ow[0])
	c.put(cx + 1, 9, ow[0])
	moon_rim(c, cells, r, 0.05)
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, BARK[0])
	return c


def moss_boulder():
	W, H = 30, 20
	c = Canvas(W, H)
	r = rng("moss_boulder")
	big = set()
	blob(big, 14, 12, 12.5, 7.4, r, jag=0.4)
	blob(big, 8, 10, 7, 6, r, jag=0.4)
	small = set()
	blob(small, 25, 15, 4.6, 3.8, r, jag=0.4)
	big = {p for p in big if p[1] < H - 1}
	small = {p for p in small if p[1] < H - 1} - big
	paint_dir(c, big, STD, r, lit=3, cap=7)
	paint_dir(c, small, STD, r, lit=3, shift=-1, cap=5)
	for (x, y) in ((15, 8), (16, 9), (17, 11), (17, 13), (18, 15)):  # crack
		if (x, y) in big:
			c.put(x, y, STD[0])
	for (x, y) in r.sample(sorted(big), 12):
		c.put(x, y, STD[1] if (x + y) % 2 else STD[3])
	moss_blob(c, big, 12, 7, 9, 3.2, r, k=0.95)
	moss_cap(c, big, r, p=0.8, depth=2)
	moss_blob(c, big, 3, 14, 3, 5, r, k=0.9)
	moss_cap(c, small, r, p=0.6, depth=1)
	for x in range(0, W):
		if c.get(x, H - 2) is not None:
			c.put(x, H - 2, STD[0])
		c.put(x, H - 1, c.get(x, H - 1))
	moon_rim(c, big, r, 0.08)
	return c


def wall_roots():
	W, H = 18, 48
	c = Canvas(W, H)
	r = rng("wall_roots")
	cells = set()
	paths = [
		(bez((0, 0), (11, 6), (5, 22), n=40), 3.0, 1.4),
		(bez((5, 20), (14, 28), (10, 40), n=30), 2.0, 0.8),
		(bez((0, 12), (8, 17), (15, 15), n=22), 1.8, 0.7),
		(bez((0, 28), (7, 33), (3, 47), n=26), 2.2, 0.9),
		(bez((8, 30), (13, 34), (15, 41), n=16), 1.4, 0.6),
	]
	for pts, r0, r1 in paths:
		stroke(cells, wavy(pts, r, 1.4, 3), r0, r1)
	cells = {p for p in cells if p[0] >= 0}
	paint_dir(c, cells, BARK, r, lit=3, cap=4)
	moss_cap(c, cells, r, p=0.5, depth=2)
	for x, y, ln in ((10, 40, 5), (15, 41, 4), (3, 46, 2)):
		hang_strand(c, x, y, ln, BARK_D, r, 0.4)
	for y in range(0, H):
		if c.get(0, y) is not None:
			c.put(0, y, BARK[0])
	moon_rim(c, cells, r, 0.05)
	return c


def wall_fungus():
	W, H = 22, 30
	c = Canvas(W, H)
	r = rng("wall_fungus")
	# bracket fungi: convex, drooping, rounded caps growing out of the wall; pale blue-grey, dark gills below
	for (cy, ln, th) in ((8, 13, 6), (19, 10, 5), (26, 7, 4)):
		cells = set()
		for x in range(0, ln + 1):
			t = x / float(ln + 0.8)
			cyx = cy + int(round(t * t * 2.0))
			for y in range(cyx - th - 1, cyx + 3):
				v = (y - cyx) / float(th if y < cyx else 1.8)
				if t * t + v * v <= 1.0:
					cells.add((x, y))
		paint_dir(c, cells, CAP, r, lit=3, cap=4, noise=False)
		for x in range(1, ln + 1):  # dark gill underside
			col = [yy for (xx, yy) in cells if xx == x]
			if col:
				c.put(x, max(col), GILL)
				if x > 2 and x < ln - 1:
					c.put(x, max(col) - 1, mix(CAP[0], GILL, 0.55))
		for k in (0.32, 0.6, 0.82):  # growth rings
			x = int(ln * k)
			col = sorted(yy for (xx, yy) in cells if xx == x)
			for yy in col[1:-2]:
				c.put(x, yy, CAP[1])
		x0 = int(ln * 0.32)
		c.put(x0 - 1, min(yy for (xx, yy) in cells if xx == x0 - 1) + 1, FIREFLY[1] if ln > 9 else FIREFLY[0])
	for y in range(0, H):
		if c.get(0, y) is not None:
			c.put(0, y, CAP[0])
	return c


def wall_moss():
	W, H = 16, 38
	c = Canvas(W, H)
	r = rng("wall_moss")
	cells = set()
	for (cy, rx, ry) in ((3, 7, 4), (9, 9, 5), (16, 7, 4.5), (22, 8, 4), (7, 5, 7), (27, 5, 3)):
		blob(cells, 0, cy, rx, ry, r, jag=1.0)
	cells = {p for p in cells if p[0] >= 0}
	for sx in (2, 5, 4, 7, 9):  # drips below the mass
		y0 = r.randint(17, 26)
		for i in range(r.randint(4, 9)):
			cells.add((sx, y0 + i))
			if i < 3:
				cells.add((sx + 1, y0 + i))
	for (x, y) in cells:
		k = 1
		if (x, y - 1) not in cells or ((x + 1, y) not in cells and (x + y) % 2):
			k = 2
		if x <= 1 or (x * 3 + y * 7) % 11 == 0:
			k = 0
		elif k == 1 and (x * 5 + y * 3) % 7 == 0:
			k = 2
		if (x, y - 1) not in cells and (x + y) % 3 == 0:
			k = 3
		if (x, y + 1) not in cells and k > 0:
			k -= 1
		c.put(x, y, MS[k])
	for x, y, ln in ((3, 25, 12), (6, 22, 9), (1, 28, 10), (8, 26, 7)):
		hang_strand(c, x, y, ln, LICHEN, r, 0.5)
	return c


def wall_ivy():
	W, H = 18, 44
	c = Canvas(W, H)
	r = rng("wall_ivy")
	stem = wavy(bez((1, 0), (7, 10), (3, 21), n=40), r, 1.0, 3) + wavy(bez((3, 21), (8, 31), (3, 43), n=30), r, 1.0, 3)
	for i, (x, y) in enumerate(stem):
		c.put(int(round(x)), int(round(y)), BARK[2] if i % 3 else BARK[1])
	leaves = [(int(round(stem[i][0])), int(round(stem[i][1]))) for i in range(4, len(stem) - 2, 7)]
	for (x0, y0) in ((5, 8), (6, 26), (2, 16)):
		pts = wavy(bez((x0, y0), (x0 + 4, y0 - 1), (x0 + 8, y0 + 3), n=12), r, 0.7, 2)
		for (x, y) in pts:
			c.put(int(round(x)), int(round(y)), BARK[1])
		leaves += [(int(round(pts[k][0])), int(round(pts[k][1]))) for k in (4, 9)]
	for i, (x, y) in enumerate(leaves):  # ivy leaves: little hanging diamonds, dark and cold
		side = 2 if i % 2 else -1
		lx, ly = max(1, x + side), y + 1
		for (ox, oy, k) in ((0, 0, 3), (1, 0, 2), (-1, 0, 3), (0, 1, 2), (0, -1, 3), (1, 1, 1), (0, 2, 1)):
			if c.get(lx + ox, ly + oy) is None:
				c.put(lx + ox, ly + oy, LEAF[k])
		c.put(lx, ly, LEAF[2])
	return c


def hang_roots():
	W, H = 22, 42
	c = Canvas(W, H)
	r = rng("hang_roots")
	cells = set()
	for x in (0, 1, 4, 5, 9, 10, 14, 15, 16, 19, 20, 21):  # crumbs of soil / root collar
		cells.add((x, 0))
		if x % 3:
			cells.add((x, 1))
	for (x0, ln, th, sway) in ((2, 26, 1.3, 3), (6, 40, 1.6, 4), (10, 17, 1.1, 3), (13, 34, 1.4, 4), (16, 27, 1.2, 3), (19, 13, 1.0, 2), (21, 21, 1.1, 3)):
		pts = wavy(bez((x0, 0), (x0 + r.uniform(-sway, sway), ln * 0.5), (x0 + r.uniform(-sway, sway), ln), n=ln * 2), r, 1.8, 4)
		stroke(cells, pts, th, 0.35)
		if ln > 20:
			j = len(pts) // 2
			bx, by = pts[j]
			stroke(cells, wavy(bez((bx, by), (bx + r.choice((-3, 3)), by + 3), (bx + r.choice((-5, 5)), by + 9), n=14), r, 1.0, 2), 0.7, 0.3)
	paint_dir(c, cells, BARK, r, lit=3, cap=3, noise=False)
	for x in range(0, W):
		if c.get(x, 0) is not None:
			c.put(x, 0, SOIL[1])
		if c.get(x, 1) is not None and (x * 3) % 4 == 0:
			c.put(x, 1, SOIL[2])
	return c


def hang_moss():
	W, H = 18, 36
	c = Canvas(W, H)
	r = rng("hang_moss")
	for x in range(0, W):  # dense top, stringy strands of different lengths
		for y in range(0, 3):
			c.put(x, y, LICHEN[2] if (x * 7 + y * 3) % 5 < 2 else LICHEN[1])
	xs = list(range(0, W))
	for x in xs:
		ln = int(4 + 22 * (math.sin(x * 0.55) * 0.5 + 0.5) * r.uniform(0.5, 1.0) + (8 if x in (4, 9, 14) else 0))
		ph = r.uniform(0, 6)
		for i in range(ln):
			xx = x + int(round(math.sin(i * 0.28 + ph) * 0.9))
			t = i / float(max(1, ln - 1))
			k = 2 if t < 0.35 else 1 if t < 0.8 else 0
			if (xx + i) % 5 == 0 and k > 0:
				k -= 1
			if t < 0.4 and (xx + i) % 4 == 0:
				k = 3
			c.put(xx, 3 + i, LICHEN[k])
	return c


def hang_charm():
	W, H = 14, 32
	c = Canvas(W, H)
	r = rng("hang_charm")
	cx = 7
	for y in range(0, 12):
		c.put(cx, y, CORD[1] if y % 2 else CORD[0])
	# twig effigy: two crossed twigs bound in the middle, a small knot of twigs on top
	for (x0, y0, x1, y1, col) in ((2, 11, 12, 21, BARK[3]), (12, 11, 2, 21, BARK[2]), (7, 10, 7, 23, BARK[3])):
		line(c, x0, y0, x1, y1, col)
	for (x, y) in ((1, 11), (13, 11), (1, 22), (13, 22), (6, 10), (8, 10)):
		c.put(x, y, BARK[1])
	for y in range(15, 18):  # lashing
		c.put(cx - 1, y, CORD[1])
		c.put(cx + 1, y, CORD[0])
	c.put(cx, 16, CORD[1])
	# small bones on threads
	for (x, y0, ln) in ((4, 22, 3), (7, 24, 4), (10, 22, 2)):
		for y in range(y0, y0 + ln):
			c.put(x, y, CORD[0])
		by = y0 + ln
		c.put(x, by, BONED[2])
		c.put(x, by + 1, BONED[1])
		c.put(x - 1, by + 2, BONED[1]) if by + 2 < H else None
		c.put(x + 1, by + 2, BONED[0]) if by + 2 < H else None
	return c


def hang_lantern_hunter():
	W, H = 14, 38
	c = Canvas(W, H)
	cx = 7
	for y in range(0, 11):  # rope
		c.put(cx, y, CORD[1] if y % 2 else CORD[0])
		c.put(cx + 1, y, CORD[0]) if y % 3 == 0 else None
	for (dx, dy) in ((-1, 11), (0, 10), (1, 11), (-1, 12), (1, 12)):  # iron ring
		c.put(cx + dx, dy, IRON[3] if dx <= 0 else IRON[1])
	# conical cap
	for i, half in enumerate((1, 2, 3, 4)):
		for x in range(cx - half, cx + half + 1):
			c.put(x, 13 + i, IRON[3] if x < cx else IRON[1] if x > cx else IRON[2])
	for x in range(cx - 5, cx + 6):
		c.put(x, 17, IRON[2] if x < cx else IRON[0])
	# glass body: dark pane, dull ember core, iron posts
	for y in range(18, 30):
		for x in range(cx - 4, cx + 5):
			edge = x in (cx - 4, cx + 4)
			if edge:
				c.put(x, y, IRON[3] if x < cx else IRON[0])
			else:
				c.put(x, y, hexc("14110f") if y % 5 else hexc("1a1512"))
	for (dx, dy, col) in ((0, 23, EMBER[0]), (-1, 24, mix(EMBER[0], VOID, 0.35)), (1, 24, mix(EMBER[0], VOID, 0.45)), (0, 24, EMBER[1]), (0, 22, mix(EMBER[0], VOID, 0.55))):
		c.put(cx + dx, dy, col)
	for x in (cx - 2, cx + 2):  # window bars
		vl(c, x, 18, 29, IRON[1])
	for x in range(cx - 5, cx + 6):
		c.put(x, 30, IRON[2] if x < cx else IRON[0])
		c.put(x, 31, IRON[1])
	for (dx, dy) in ((-1, 32), (0, 32), (1, 32), (0, 33)):
		c.put(cx + dx, dy, IRON[1])
	for y in range(17, 30):  # a little rust-dark streak
		if y % 6 == 0:
			c.put(cx - 3, y, RU[1])
	return c


def root_hollow():
	"""Root-framed hollow / old burrow arch, drawn on a very dark root back wall: dark, low contrast."""
	W, H = 52, 52
	c = Canvas(W, H)
	r = rng("root_hollow")
	cx = 26
	rim = [mix(ROOTD[i], BARK_D[i], 0.5) for i in range(4)]
	ramp = [hexc("0a0b0d"), hexc("15161a"), hexc("202227"), hexc("2e3037")]
	fr = set()
	inner = set()
	for y in range(0, H):
		if y >= 26:
			ho, hi = 24, 13
		else:
			ho = 24 * math.sqrt(max(0.0, 1 - ((26 - y) / 25.0) ** 2))
			hi = 13 * math.sqrt(max(0.0, 1 - ((28 - y) / 20.0) ** 2)) if y > 8 else -1
		for x in range(cx - int(ho), cx + int(ho) + 1):
			if abs(x - cx) > hi:
				fr.add((x, y))
		if hi > 0:
			for x in range(cx - int(hi), cx + int(hi) + 1):
				inner.add((x, y))
	# base fill (packed earth between the roots)
	for (x, y) in fr:
		c.put(x, y, EARTHD[1] if (x * 3 + y * 5) % 7 else EARTHD[2])
	# roots following the arch (concentric strands, twisting), crossing roots and knobs
	strands = set()
	layers = []
	for k, rad in enumerate((15.5, 18, 20.5, 23)):
		pts = []
		for i in range(0, 91):
			a = math.pi + i * math.pi / 90.0
			rr = rad + 2.0 * math.sin(i * 0.31 + k * 1.7) + 0.7 * math.sin(i * 0.9 + k) + r.uniform(-0.15, 0.15)
			pts.append((cx + rr * math.cos(a), 26 + rr * math.sin(a) * 1.04))
		for i in range(1, 8):  # legs straight down on both sides
			pts.insert(0, (cx - rad + 0.8 * math.sin(i + k), 26 + (8 - i) * 3.2 - 1))
			pts.append((cx + rad + 0.8 * math.sin(i + k), 26 + i * 3.2))
		one = set()
		stroke(one, pts, 2.3 if k % 2 else 1.9, 1.9)
		layers.append(one)
	for (x0, y0, x1, y1) in ((cx - 24, 44, cx - 10, 22), (cx + 24, 40, cx + 8, 20), (cx - 22, 20, cx - 4, 6), (cx + 22, 24, cx + 6, 6), (cx - 5, 3, cx - 9, 12), (cx + 8, 4, cx + 11, 13)):
		one = set()
		stroke(one, wavy(bez((x0, y0), ((x0 + x1) / 2 + r.uniform(-3, 3), (y0 + y1) / 2), (x1, y1)), r, 2.4, 3), 2.0, 1.4)
		layers.append(one)
	for one in layers:
		one = {p for p in one if p in fr}
		strands |= one
		paint_dir(c, one, ramp, r, lit=3, cap=3, noise=False)
	# the opening: near-black void, floor of leaf litter
	for (x, y) in inner:
		if (x, y) in strands:
			continue
		c.put(x, y, hexc("050507") if y < 44 else hexc("0b0c0f"))
	for (x, y) in sorted(inner):
		if (x - 1, y) not in inner:
			c.put(x, y, ramp[2])
	for x in range(cx - 13, cx + 14):  # litter / earth mound inside
		top = 44 + int(abs(x - cx) * 0.18) + (1 if x % 3 == 0 else 0)
		for y in range(top, H):
			if (x, y) in inner or abs(x - cx) <= 13:
				c.put(x, y, EARTHD[2] if (x + y) % 3 else EARTHD[1])
	for x, ln in ((cx - 8, 6), (cx - 2, 9), (cx + 5, 5), (cx + 9, 7)):  # rootlets hanging into the void
		hang_strand(c, x, 12 if abs(x - cx) < 8 else 18, ln, ROOTD, r, 0.5)
	# ragged outer edge: roots splaying out, a few dangling rootlets
	for (x, y) in sorted(fr):
		if (x - cx) ** 2 / 24.0 ** 2 + ((y - 26) / 25.0) ** 2 > 0.88 and y < 40 and r.random() < 0.4:
			c.put(x, y, None) if False else None
	for x in range(0, W):  # earth shadow at the bottom
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, EARTHD[0])
	for (x, y) in ((cx - 15, 20), (cx + 17, 16), (cx - 7, 4)):
		c.put(x, y, MS[0])  # a hint of moss in the cold
	return c


def fungus_niche():
	W, H = 26, 28
	c = Canvas(W, H)
	r = rng("fungus_niche")
	cx = 13
	ramp = [hexc("0a0b0d"), hexc("15161a"), hexc("202227"), hexc("2e3037")]
	fr = set()
	inner = set()
	for y in range(0, H):
		ho = 12 if y > 11 else 12 * math.sqrt(max(0.0, 1 - ((11 - y) / 11.0) ** 2))
		hi = 8 if y > 12 else 8 * math.sqrt(max(0.0, 1 - ((12 - y) / 8.0) ** 2)) if y > 4 else -1
		for x in range(cx - int(ho), cx + int(ho) + 1):
			if abs(x - cx) > hi:
				fr.add((x, y))
		if hi > 0:
			for x in range(cx - int(hi), cx + int(hi) + 1):
				if y < H - 3:
					inner.add((x, y))
	for (x, y) in fr:
		c.put(x, y, EARTHD[1] if (x * 3 + y * 5) % 6 else EARTHD[2])
	roots = set()
	layers = []
	for k, rad in enumerate((9.5, 11.3)):
		pts = [(cx + (rad + 1.4 * math.sin(i * 0.5 + k)) * math.cos(math.pi + i * math.pi / 40.0), 12 + (rad + 1.4 * math.sin(i * 0.5 + k)) * math.sin(math.pi + i * math.pi / 40.0)) for i in range(41)]
		pts = [(cx - rad + 0.8 * math.sin(j * 0.6 + k), 27 - j) for j in range(0, 15)][::-1] + pts + [(cx + rad + 0.8 * math.sin(j * 0.6 + k), 12 + j) for j in range(0, 16)]
		one = set()
		stroke(one, pts, 1.7, 1.7)
		layers.append(one)
	for one in layers:
		one = {p for p in one if p in fr}
		paint_dir(c, one, ramp, r, lit=3, cap=3, noise=False)
	for (x, y) in inner:
		c.put(x, y, hexc("060608"))
	for (x, y) in sorted(inner):
		if (x - 1, y) not in inner:
			c.put(x, y, ramp[2])
	for x in range(cx - 8, cx + 9):  # floor
		for y in range(H - 5, H - 3):
			c.put(x, y, EARTHD[2] if (x + y) % 2 else EARTHD[1])
	# glowing pale caps (faint)
	glow = [hexc("182e29"), hexc("274a40"), hexc("3b6556"), FIREFLY[1]]
	_mushroom(c, cx - 4, H - 5, 2, 2, 3, glow, hexc("0b1411"), FIREFLY[2])
	_mushroom(c, cx + 1, H - 5, 3, 2, 5, glow, hexc("0b1411"), FIREFLY[2])
	_mushroom(c, cx + 5, H - 5, 1, 1, 2, [glow[0], glow[1], glow[1], glow[2]], hexc("0b1411"))
	c.put(cx - 1, H - 11, FIREFLY[0])
	c.put(cx + 6, H - 9, FIREFLY[0])
	for x in range(0, W):
		if c.get(x, H - 1) is not None:
			c.put(x, H - 1, EARTHD[0])
	return c


def _mushroom(c, cx, base_y, hw, h, stem, ramp, gill, glint=None):
	"""Small domed mushroom: stem rising from base_y, cap of half-width hw and height h."""
	top_stem = base_y - stem
	for i in range(stem):
		c.put(cx, base_y - i, ramp[1] if i % 2 == 0 else ramp[0])
		if hw >= 2 and i < stem - 1:
			c.put(cx + 1, base_y - i, ramp[0])
	for j in range(h + 1):
		half = hw if j >= 1 else max(1, hw - 1)
		for x in range(cx - half, cx + half + 1):
			k = 3 if (j == 0 and x <= cx) else 2 if (x < cx and j < h) else 1
			if j == h:
				k = 0
			c.put(x, top_stem - h + j, ramp[k])
	for x in range(cx - hw + 1, cx + hw):
		c.put(x, top_stem + 1, gill)
	if glint:
		c.put(cx - 1 if hw > 1 else cx, top_stem - h, glint)


# <<MORE_PROPS>>

# ============================================================================= catalogue / outputs
def _ground(w, h):
	return [w // 2, h]


def _ceil(w, h):
	return [w // 2, 0]


PROPS = [
	("ancient_trunk", ancient_trunk, "ground", _ground, [], 2, True),
	("gnarled_oak", gnarled_oak, "ground", _ground, [], 2, True),
	("fir_a", fir_a, "ground", _ground, [], 5, False),
	("fir_b", fir_b, "ground", _ground, [], 5, False),
	("dead_birch", dead_birch, "ground", _ground, [], 3, False),
	("root_arch", root_arch, "ground", _ground, [], 3, False),
	("fallen_log", fallen_log, "ground", _ground, [], 4, False),
	("fern_a", fern_a, "ground", _ground, [], 5, False),
	("fern_b", fern_b, "ground", _ground, [], 5, False),
	("mushroom_cluster", mushroom_cluster, "ground", _ground, [{"pos": [8, 5], "type": "fungus"}], 4, False),
	("standing_stone", standing_stone, "ground", _ground, [], 2, False),
	("cairn", cairn, "ground", _ground, [], 3, False),
	("stag_totem", stag_totem, "ground", _ground, [], 2, False),
	("charcoal_camp", charcoal_camp, "ground", _ground, [{"pos": [50, 29], "type": "flame"}], 1, False),
	("forest_shrine", forest_shrine, "ground", _ground, [{"pos": [9, 11], "type": "candle"}], 1, False),
	("root_stump", root_stump, "ground", _ground, [], 4, False),
	("owl_snag", owl_snag, "ground", _ground, [], 2, False),
	("moss_boulder", moss_boulder, "ground", _ground, [], 4, False),
	("wall_roots", wall_roots, "wall", lambda w, h: [0, h // 2], [], 4, False),
	("wall_fungus", wall_fungus, "wall", lambda w, h: [0, 8], [{"pos": [6, 4], "type": "fungus"}], 3, False),
	("wall_moss", wall_moss, "wall", lambda w, h: [0, 10], [], 4, False),
	("wall_ivy", wall_ivy, "wall", lambda w, h: [0, 2], [], 3, False),
	("hang_roots", hang_roots, "ceiling", _ceil, [], 4, False),
	("hang_moss", hang_moss, "ceiling", _ceil, [], 4, False),
	("hang_charm", hang_charm, "ceiling", _ceil, [], 2, False),
	("hang_lantern_hunter", hang_lantern_hunter, "ceiling", _ceil, [{"pos": [7, 23], "type": "flame"}], 1, False),
	("root_hollow", root_hollow, "underground", _ground, [], 2, True),
	("fungus_niche", fungus_niche, "underground", _ground, [{"pos": [13, 19], "type": "fungus"}], 2, False),
]


def sha256(path):
	return hashlib.sha256(open(path, "rb").read()).hexdigest()


def board(path, names, scale, bg="1b1e22", pad=4, row_w=330):
	"""All props on one dark board, wrapped into rows, bottoms aligned per row."""
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


def main(argv):
	os.makedirs(OUT, exist_ok=True)
	os.makedirs(PREVIEW, exist_ok=True)
	meta = []
	rows = []
	for name, fn, kind, anchor, lights, weight, big in PROPS:
		if argv and name not in argv:
			continue
		c = fn()
		path = os.path.join(OUT, name + ".png")
		save_png(c, path)
		meta.append({"file": name + ".png", "w": c.w, "h": c.h, "kind": kind, "anchor": anchor(c.w, c.h), "lights": lights, "weight": weight, "big": big})
		rows.append((name, c.w, c.h, kind, anchor(c.w, c.h), lights, sha256(path)))
	if argv:
		board(os.environ.get("N3_TMP", "/tmp/n3_tmp_board.png"), [n for n, *_ in PROPS if n in argv], int(os.environ.get("N3_SCALE", "4")), row_w=int(os.environ.get("N3_ROW", "330")))
		scale_preview(os.environ.get("N3_TMP2", "/tmp/n3_tmp_scale.png"), [n for n, _, k, *_ in PROPS if n in argv and k == "ground"], 3)
		return
	with open(os.path.join(OUT, "props_n3.json"), "w") as f:
		json.dump(meta, f, indent=1)
	board(os.path.join(PREVIEW, "props_n3_board.png"), [n for n, *_ in PROPS], 3, row_w=330)
	scale_preview(os.path.join(PREVIEW, "props_n3_scale.png"), [n for n, _, k, *_ in PROPS if k == "ground"])
	with open(os.path.join(OUT, "props_n3.sha256"), "w") as f:
		for name, w, h, kind, anc, lights, sha in rows:
			f.write("%s  %s.png\n" % (sha, name))


if __name__ == "__main__":
	main(sys.argv[1:])

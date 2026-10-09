"""N4 Forbidden Graveyard backdrop layers (RUN-021 aesthetic pass): a vast necropolis on a hill under a cold moon.

Writes to assets/run021/n4/:
  bg_n4_sky.png      640x360  opaque, screen-fixed: very dark violet-grey night, sparse dim stars, small cold violet-grey moon, thin clouds
  bg_n4_far.png      640x170  tiling: ruined cemetery basilica with a broken spire, distant mausoleum roofs, obelisks, cypress spires, crosses
  bg_n4_ridge.png    640x112  tiling: rows of crypt roofs, mausoleums, ossuary-chapel belfry, yews, iron railings in fog; foot fades out
  bg_n4_mid.png      512x132  tiling: the graveyard slope: headstones, crosses, mausoleums, willows, yews, an open grave; opaque ground below
  bg_n4_wisps.png    512x220  tiling: very faint spectral veils / grave mist plumes (alpha 16 / 30 / 46, ordered dither)
  bg_n4_near.png     512x190  tiling: darkest silhouettes (leaning tombstones, mausoleum corner, bare yew, angel statue); ends on flat FINAL
  bg_n4_<band>_lights.png     same size as the band: grave candles (cold flames, a few warm), dim lit doorways/windows, will-o'-wisps
and previews to work/run021/n4pass/preview/.

Same method as tools/art/run021/n3/backdrop_n3.py: native 1x pixel art, ordered dither (no smooth gradients), every x-dependent
routine wraps (periodic functions, wrapped puts), deterministic seeded rng.
Usage: python3 tools/art/run021/n4/backdrop_n4.py
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
from palette_run020 import SPECTRAL  # noqa: E402
from world_bg import dither, dither_band, periodic, rng  # noqa: E402  (read only)
from pngio import load_png  # noqa: E402

OUT = os.path.join(ROOT, "assets", "run021", "n4")
PREVIEW = os.path.join(ROOT, "work", "run021", "n4pass", "preview")

# pale cold violet-grey moon ramp (not the N1 blood red, N2 olive or N3 blue moon)
MOON = [hexc(c) for c in ("1f1d2c", "2f2d40", "454359", "5e5c74", "82809a", "aeacc0")]
FINAL = hexc("0a090f")       # last row of the near band
MID_GROUND = hexc("100f18")  # bottom rows of the mid band
WISP_RGB = SPECTRAL[3][:3]   # greyed spectral cyan, used at low alpha only
WISP_LEVELS = [16, 30, 46]


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


def dxw(x, cx, W):
	return ((x - cx + W // 2) % W) - W // 2


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


# ------------------------------------------------------------------ lights
class Lights:
	"""Collects lit spots while the base band is drawn; rendered into a transparent overlay of the same size.
	kinds: cold (spectral candle flame), warm (ember candle flame), wisp (will-o'-wisp), win / winw (dim lit doorway or window, cold / warm)."""

	def __init__(self, w, h):
		self.w, self.h = w, h
		self.items = []

	def add(self, x, y, kind, w=1, h=1, halo=True):
		self.items.append((x, y, kind, w, h, halo))

	def render(self):
		c = Canvas(self.w, self.h)
		halos = {"cold": SPECTRAL[1], "wisp": SPECTRAL[1], "warm": EMBER[0], "win": SPECTRAL[0], "winw": EMBER[0]}
		for x, y, kind, w, h, halo in self.items:  # halos first (alpha 70), cores opaque on top
			if not halo:
				continue
			glow = halos[kind][:3] + (70,)
			if kind in ("win", "winw"):
				for yy in range(y - 2, y + h + 2):
					for xx in range(x - 2, x + w + 2):
						inside = x <= xx < x + w and y <= yy < y + h
						if inside:
							continue
						d = max(x - xx, xx - (x + w - 1), y - yy, yy - (y + h - 1))
						if d == 1 or (d == 2 and (xx + yy) % 2 == 0):
							wput(c, xx, yy, glow)
				continue
			for yy in range(y - 1, y + h + 1):
				for xx in range(x - 1, x + w + 1):
					inside = x <= xx < x + w and y <= yy < y + h
					diag = (xx < x or xx >= x + w) and (yy < y or yy >= y + h)
					if not inside and not diag:
						wput(c, xx, yy, glow)
			if kind == "wisp" and w > 1:  # faint trailing glow behind a drifting wisp
				for k in range(2, 5):
					if k % 2 == 0 or w > 2:
						wput(c, x - k, y, glow)
		for x, y, kind, w, h, halo in self.items:
			for yy in range(y, y + h):
				for xx in range(x, x + w):
					if kind == "cold":
						k = SPECTRAL[4] if yy == y else SPECTRAL[3]
					elif kind == "warm":
						k = EMBER[2] if yy == y else EMBER[1]
					elif kind == "wisp":
						k = SPECTRAL[4]
					elif kind == "win":
						k = SPECTRAL[2] if yy == y else SPECTRAL[1]
					else:
						k = EMBER[1] if yy == y else EMBER[0]
					wput(c, xx, yy, k)
		return c


# ------------------------------------------------------------------ shared drawing helpers
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
	pts = []
	for i in range(n + 1):
		t = i / n
		x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1
		y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1
		pen(c, x, y, max(1, int(round(w0 + (w1 - w0) * t))), col)
		pts.append((x, y, t))
	return pts


def bough(c, x, y, ang, length, w, col, r, depth, spread=0.8, shrink=(0.62, 0.8), ymin=None, ends=None):
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
	pts = limb(c, x, y, x1, y1, w, max(1, w - 1 if w > 2 else 1), col, bend=r.uniform(-2.5, 2.5))
	if ends is not None:
		ends.extend(pts[::3])
	for _ in range(r.choice((2, 2, 3))):
		bough(c, x1, y1, ang + r.uniform(-spread, spread), length * r.uniform(*shrink), max(1, w - 1), col, r, depth - 1, spread, shrink, ymin, ends)


def strand(c, x, y, length, col, col2, r, phase=0.0, ymax=None):
	"""Hanging strand (willow tendril, root hair): 1 px wide, swaying, ragged at the tip."""
	for i in range(length):
		yy = y + i
		if ymax is not None and yy > ymax:
			break
		t = i / float(length)
		if t > 0.55 and r.random() < 0.45 * t:
			continue
		xo = int(round(1.2 * math.sin(i * 0.28 + phase)))
		wput(c, x + xo, yy, col)
		if col2 is not None and t < 0.5 and r.random() < 0.18:
			wput(c, x + xo + 1, yy, col2)


def trunk_col(c, cx, y0, y1, w0, w1, col, lean=0.0, wob=0.0, ph=0.0):
	"""Vertical tapered trunk from y0 (top, width w0) to y1 (base, width w1)."""
	for y in range(y0, y1 + 1):
		t = (y - y0) / float(max(1, y1 - y0))
		w = max(1, int(round(w0 + (w1 - w0) * t ** 1.2)))
		xc = cx + lean * (1 - t) + wob * math.sin(y * 0.11 + ph)
		xs = int(round(xc - w / 2.0))
		for k in range(w):
			wput(c, xs + k, y, col)


# ------------------------------------------------------------------ graveyard shapes
def tri(c, cx, ybase, hw, h, col):
	"""Filled isosceles roof triangle: apex at ybase-h+1, full width 2*hw+1 on row ybase."""
	for i in range(h):
		w = int(round(hw * (i + 1) / float(h)))
		wrect(c, cx - w, ybase - h + 1 + i, 2 * w + 1, 1, col)


def headstone(c, x, base, h, w, col, shade, shape, lean, r, mark=True):
	"""Leaning grave slab. shape: round / peak / square / chip (broken corner). No hollows, no eyes."""
	for yy in range(h):
		xc = x + lean * (yy / float(h))
		hw = w / 2.0
		top = h - yy  # rows remaining to the top, 1 at the very top
		if shape == "round" and top <= hw:
			hw = math.sqrt(max(0.0, hw * hw - (hw - top + 0.5) ** 2)) + 0.5
		elif shape == "peak" and top <= max(2, h * 0.28):
			hw = max(0.6, hw * top / max(2.0, h * 0.28))
		elif shape == "chip" and top <= 3:
			hw = hw * (0.55 + 0.15 * top)
		x0, x1 = int(round(xc - hw)), int(round(xc + hw - 0.5))
		if shape == "chip" and top <= 4:
			x1 -= (4 - top)
		for xx in range(x0, x1 + 1):
			wput(c, xx, base - yy, col)
	if mark and w >= 5 and h >= 9:  # carved cross or dashes
		mx = int(round(x + lean * 0.6))
		my = base - int(h * 0.6)
		if w >= 7:
			wrect(c, mx, my - 2, 1, 4, shade)
			wrect(c, mx - 1, my - 1, 3, 1, shade)
		else:
			wrect(c, mx - 1, my, 3, 1, shade)
			wrect(c, mx - 1, my + 2, 3, 1, shade)
	if w >= 6:  # ground contact
		wrect(c, int(round(x - w / 2.0)) - 1, base, w + 2, 1, shade)


def cross(c, x, base, h, col, shade, lean=0.0, kind="latin", r=None):
	"""Grave cross. kind: latin / celtic (ring) / broken (snapped arm and top)."""
	sw = 2 if h >= 16 else 1
	top_y = base - h
	arm_y = top_y + max(2, int(h * 0.3))
	arm_hw = max(3, h // 4)
	for yy in range(h + 1):
		xc = int(round(x + lean * (1 - yy / float(h))))
		if kind == "broken" and yy < 3:
			continue
		wrect(c, xc - sw // 2, top_y + yy, sw, 1, col)
	xt = int(round(x + lean * 0.7))
	if kind == "broken":
		wrect(c, xt - arm_hw, arm_y + 1, arm_hw + 1, sw, col)
		wrect(c, xt + 1, arm_y + 1, max(1, arm_hw // 3), sw, col)
	else:
		wrect(c, xt - arm_hw, arm_y, 2 * arm_hw + 1, sw, col)
	if kind == "celtic":
		rr = max(3, h // 5)
		for a in range(24):
			ang = a * math.pi / 12
			wput(c, xt + int(round(rr * math.cos(ang))), arm_y + int(round(rr * math.sin(ang))), col)
	wrect(c, x - 3, base, 7, 1, shade)
	wrect(c, x - 2, base - 1, 5, 1, col)  # small stone footing


def obelisk(c, cx, base, h, hw, col, shade):
	for i in range(h):
		t = i / float(h)  # 0 at the base
		w = hw * (1 - 0.35 * t)
		if i > h - 5:
			w = max(0.5, w * (h - i) / 5.0)
		wrect(c, int(round(cx - w)), base - i, int(round(2 * w)) + 1, 1, col)
	wrect(c, cx - hw - 1, base - 2, 2 * hw + 3, 3, col)
	wrect(c, cx - hw - 2, base, 2 * hw + 5, 1, shade)
	for k in range(h // 7):
		wput(c, cx, base - 6 - k * 5, shade)


def cypress(c, cx, base, h, hw, col, r, lean=0.0):
	"""Narrow, dense, ragged columnar yew/cypress spire; trunk stub at the foot."""
	for i in range(h):
		t = i / float(h)
		w = hw * (1 - t) ** 0.55 * min(1.0, 0.45 + t * 5.0)
		w *= r.uniform(0.82, 1.12)
		xc = cx + lean * t
		x0, x1 = int(round(xc - w)), int(round(xc + w))
		wrect(c, x0, base - i, x1 - x0 + 1, 1, col)
	wput(c, int(round(cx + lean)), base - h, col)
	wput(c, int(round(cx + lean)), base - h - 1, col)


def yew(c, cx, base, h, hw, col, col_lt, r):
	"""Old broad yew: bare trunk and a dense ragged domed mass of leaf clumps."""
	trunk_col(c, cx, base - h // 3, base + 1, 3, 4, col)
	k = max(3, h // 9)
	for i in range(k):
		t = i / float(k)
		cy = base - h // 3 - int(t * h * 0.62)
		rw = max(3, int(hw * (1 - 0.7 * t) * r.uniform(0.9, 1.15)))
		for side in (-1, 1) if rw > 5 else (0,):
			ph = r.uniform(0, 6.28)
			ccx = cx + side * rw // 2
			for y in range(cy - 5, cy + 6):
				for x in range(ccx - rw - 2, ccx + rw + 3):
					d = math.hypot((x - ccx) / float(rw), (y - cy) / 4.5)
					noise = (math.sin(x * 1.7 + y * 0.9 + ph) + math.sin(x * 0.6 - y * 2.1 + ph)) * 0.07
					if d + noise < 0.8 or (d + noise < 1.12 and dither(1.0 - (d + noise - 0.8) / 0.32, x, y)):
						wput(c, x, y, col)
						if col_lt is not None and (x - ccx) / float(rw) * 0.7 - (y - cy) / 4.5 * 0.7 > 0.6 and (x + y) % 2 == 0:
							wput(c, x, y, col_lt)
	wput(c, cx, base - h, col)
	wput(c, cx, base - h + 1, col)


def willow(c, cx, base, h, col, col2, r, ymax=None, nl=6, slen=(10, 30)):
	"""Weeping willow, bare and ragged: short gnarled trunk, arching limbs, a dome of sparse leaf dither and dense hanging tendrils."""
	top = base - int(h * 0.5)
	trunk_col(c, cx, top, base + 1, 3, 6, col, wob=1.0, ph=cx * 0.3)
	wrect(c, cx - 4, base - 1, 9, 2, col)
	ymax = base - 1 if ymax is None else ymax
	tips = []
	for k in range(nl):
		side = -1 if k % 2 == 0 else 1
		ang = -math.pi / 2 + side * r.uniform(0.3, 1.2)
		ln = r.randint(int(h * 0.22), int(h * 0.36))
		x1 = cx + math.cos(ang) * ln
		y1 = top + 3 + math.sin(ang) * ln
		pts = limb(c, cx, top + 3, x1, y1, 3, 1, col, bend=side * r.uniform(2, 5))
		pts2 = limb(c, x1, y1, x1 + side * r.randint(4, 9), y1 + r.randint(4, 9), 1, 1, col, bend=side * 2)
		tips += [(px, py) for px, py, t in pts[2:] + pts2]
	for px, py in tips:  # tendrils from every limb pixel column, long, swaying, ragged; a second tone for depth
		if r.random() < 0.8:
			L = int(min(h * 0.7, (ymax - py) * r.uniform(0.35, 0.95)))
			if L > 4:
				strand(c, int(round(px)), int(round(py)) + 1, L, col if r.random() < 0.6 else col2, col2, r, phase=px * 0.5, ymax=ymax)
	for _ in range(int(h * 1.1)):  # sparse dithered leaf mass over the crown
		dx = r.uniform(-1, 1) * h * 0.3
		dy = -abs(r.gauss(0, h * 0.12)) + 3
		wput(c, int(cx + dx), int(top + dy), col2)
	return top


def railing(c, x0, x1, base, h, col, shade, r, spacing=5, gaps=0.0):
	"""Low iron cemetery railing: sparse thin posts with rounded (ball) finials, two rails; dark, no spikes."""
	x = x0
	k = 0
	while x <= x1:
		if r.random() < gaps:
			x += spacing
			k += 1
			continue
		ph = h - (1 if (k % 7) == 3 else 0)
		wrect(c, x, base - ph, 1, ph + 1, col)
		wrect(c, x - 1, base - ph - 1, 3, 1, col)  # ball finial
		wput(c, x, base - ph - 2, col)
		k += 1
		x += spacing
	for yy in (base - h + 3, base - 2):
		for xx in range(x0, x1 + 1):
			if (xx + yy) % 7 != 0:
				wput(c, xx, yy, col)
	for gx in (x0, x1):  # heavier end posts
		wrect(c, gx - 1, base - h - 1, 3, h + 2, shade)
		wrect(c, gx - 1, base - h - 3, 3, 2, col)


def mausoleum(c, cx, base, w, h, col, shade, door, roof="gable", ph=None, door_w=None, broken=False, r=None, pil=True, dark_win=None):
	"""Front-facing family mausoleum: plinth, cornice, pediment/dome, pilasters, arched dark doorway. Returns the door rect."""
	x0 = cx - w // 2
	wrect(c, x0, base - h + 1, w, h, col)
	wrect(c, x0 - 1, base - 1, w + 2, 2, col)           # plinth
	wrect(c, x0 - 2, base + 1, w + 4, 1, shade)         # step shadow
	wrect(c, x0 - 1, base - h, w + 2, 2, col)           # cornice
	wrect(c, x0 - 1, base - h + 2, w + 2, 1, shade)
	ph = ph if ph is not None else max(4, w // 3)
	if roof == "gable":
		tri(c, cx, base - h - 1, w // 2 + 1, ph, col)
		if w >= 14:  # oculus under the pediment
			wrect(c, cx, base - h - 3, 1, 1, shade)
			wrect(c, cx - 1, base - h - 2, 3, 1, shade)
	elif roof == "dome":
		for i in range(ph):
			t = i / float(ph)
			hw = int(round((w // 2) * math.sqrt(max(0.0, 1 - (1 - t) ** 2 * 1.0))))
			wrect(c, cx - hw, base - h - 1 - (ph - 1 - i) + 0, 2 * hw + 1, 1, col)
		wrect(c, cx, base - h - ph - 3, 1, 3, col)
		wrect(c, cx - 1, base - h - ph - 2, 3, 1, col)
	elif roof == "pyramid":
		tri(c, cx, base - h - 1, w // 2 - 1, ph, col)
		wrect(c, cx, base - h - ph - 3, 1, 3, col)
		wrect(c, cx - 1, base - h - ph - 2, 3, 1, col)
	elif roof == "flat":
		wrect(c, x0 - 1, base - h - 2, w + 2, 2, col)
		wrect(c, cx - 1, base - h - 4, 3, 2, col)
	if pil and w >= 14:
		for px in (x0 + 2, x0 + w - 3):
			wrect(c, px, base - h + 3, 1, h - 5, shade)
		for px in (x0 + 4, x0 + w - 5):
			wrect(c, px, base - h + 3, 1, h - 5, col)
	dw = door_w or max(4, w // 4)
	dh = max(7, int(h * 0.58))
	dx = cx - dw // 2
	wrect(c, dx, base - dh + 1, dw, dh, door)
	wrect(c, dx - 1, base - dh + 3, 1, dh - 3, shade)
	wclear_pts = [(dx, base - dh + 1), (dx + dw - 1, base - dh + 1)]  # arched head: round both top corners
	for px, py in wclear_pts:
		wput(c, px, py, col)
	wrect(c, dx - 1, base + 0, dw + 2, 1, shade)
	if dark_win:
		for wx in dark_win:
			wrect(c, wx, base - h + 6, 2, 4, door)
	if broken and r is not None:  # chipped pediment corner, gaps in the cornice
		for k in range(5):
			wclear(c, cx + w // 2 - 1 - k, base - h - 1 - (ph - 2 - k * 1 if ph - 2 - k > 0 else 0), 1 + k % 2, 1)
		for k in range(3):
			wclear(c, x0 + r.randint(1, w - 2), base - h, 1, 1)
	return (dx, base - dh + 1, dw, dh)


def chapel(c, cx, base, col, shade, door, r):
	"""Ossuary chapel: small nave with a steep gable, a slim belfry tower with an open (bell-less) arch and a pyramid cap."""
	x0 = cx - 14
	wrect(c, x0, base - 13, 22, 14, col)
	tri(c, x0 + 11, base - 14, 13, 9, col)
	wrect(c, x0 + 5, base - 8, 3, 8, door)  # door
	wrect(c, x0 + 14, base - 9, 2, 4, door)  # window slit
	wrect(c, x0 + 11 - 1, base - 20, 2, 1, shade)
	tx = cx + 8
	wrect(c, tx - 4, base - 34, 9, 35, col)           # belfry tower
	wrect(c, tx - 5, base - 35, 11, 2, col)           # cornice
	wrect(c, tx - 4, base - 28, 9, 1, shade)
	wrect(c, tx - 2, base - 33, 5, 8, door)           # open belfry arch (no bell)
	wput(c, tx - 2, base - 33, col)
	wput(c, tx + 2, base - 33, col)
	wrect(c, tx - 1, base - 31, 1, 1, shade)
	wrect(c, tx - 1, base - 21, 3, 6, door)           # lower slit
	tri(c, tx, base - 36, 5, 11, col)                 # pyramid cap
	wrect(c, tx, base - 51, 1, 5, col)                # cross finial
	wrect(c, tx - 1, base - 49, 3, 1, col)
	wrect(c, x0 - 1, base + 1, 24, 1, shade)


def basilica(c, cx, base, col, win, r):
	"""Far ruined cemetery basilica: roofless nave with arched window holes, a broken roof, flying-buttress stubs, a tower with a broken spire."""
	nx0, nx1 = cx - 38, cx + 6
	wall_h = 30
	wrect(c, nx0, base - wall_h, nx1 - nx0 + 1, wall_h + 2, col)
	mid = (nx0 + nx1) // 2
	half = (nx1 - nx0) // 2 + 2
	tops = {}
	for x in range(nx0 - 1, nx1 + 2):
		rh = int(13 * max(0.0, 1 - abs(x - mid) / float(half)))
		tops[x] = base - wall_h - rh
		wrect(c, x, base - wall_h - rh, 1, rh + 1, col)
	for x in range(mid - 9, mid + 8):   # the roof is broken open: ragged notch with a few rafters left
		d = 3 + ((x * 7 + 3) % 5)
		wclear(c, x, tops[x] - 1, 1, d)
	for x in (mid - 6, mid - 1, mid + 4):
		wrect(c, x, tops[x] - 1 + 3 + ((x * 3) % 3), 1, 6, col)
	for k in range(5):       # tall pointed window holes (dark), one lit in the lights overlay
		wx = nx0 + 5 + k * 8
		wrect(c, wx, base - wall_h + 6, 3, 12, win)
		wrect(c, wx + 1, base - wall_h + 4, 1, 2, win)
		wput(c, wx, base - wall_h + 6, col)
		wput(c, wx + 2, base - wall_h + 6, col)
	for k in range(6):       # buttresses with flying stubs
		bx = nx0 + 1 + k * 8
		wrect(c, bx, base - 18, 2, 19, col)
		wrect(c, bx - 1, base - 3, 4, 4, col)
	for x in range(nx0, nx0 + 7):     # ragged ruined west end
		wclear(c, x, base - wall_h - (0 if x > nx0 + 3 else 2), 1, 2 + (x * 5) % 4)
	tx = cx + 12                   # tower
	wrect(c, tx - 6, base - 52, 13, 54, col)
	wrect(c, tx - 7, base - 53, 15, 2, col)
	for yy in (base - 46, base - 36):
		wrect(c, tx - 2, yy, 5, 6, win)
		wput(c, tx - 2, yy, col)
		wput(c, tx + 2, yy, col)
		wput(c, tx, yy - 1, win)
	wrect(c, tx - 1, base - 18, 3, 7, win)
	for i in range(14):            # spire, broken at the top (jagged)
		w = max(0, int(round(6 * (1 - i / 19.0))))
		wrect(c, tx - w, base - 53 - i, 2 * w + 1, 1, col)
	for k, dx in enumerate((-2, -1, 0, 2)):   # jagged broken tip
		wrect(c, tx + dx, base - 67 - (k % 3), 1, 2 + (k % 3), col)
	wclear(c, tx + 1, base - 68, 1, 3)
	tx2 = cx + 30                  # transept with a rose window
	wrect(c, tx2 - 9, base - 24, 19, 26, col)
	tri(c, tx2, base - 25, 10, 8, col)
	wdisc(c, tx2, base - 18, 3, win)
	wrect(c, tx2 - 1, base - 14, 3, 14, win)
	for x in range(tx2 + 4, tx2 + 10):   # ruined right shoulder
		wclear(c, x, base - 25 + (x % 3), 1, 3 + (x % 2))
	for i in range(14):            # rubble
		wput(c, nx0 - 6 + i * 2, base - ((i * 3) % 3), col)
		wput(c, nx1 + 20 + i, base - (i % 2), col)


def open_grave(c, x, gy, soil, pit, P_ground):
	"""Gravediggers' abandoned open grave: a raw earth mound and a dark rectangular pit cut into the ground (no tools)."""
	for dx in range(-24, -9):
		hh = int(round(7 * math.sqrt(max(0.0, 1 - ((dx + 16.5) / 8.0) ** 2))))
		for yy in range(hh):
			wput(c, x + dx, gy - yy, soil)
	wrect(c, x - 9, gy, 18, 5, pit)
	wrect(c, x - 10, gy - 1, 1, 2, soil)
	wrect(c, x + 9, gy - 1, 1, 2, soil)
	for k in range(5):
		wput(c, x - 6 + k * 3, gy + 5, P_ground)


def angel(c, cx, base, body, shade, edge):
	"""Broken angel on a plinth: small, dark stone, bowed head (no face, no eyes), one wing intact, one snapped."""
	wrect(c, cx - 11, base - 3, 23, 4, body)
	wrect(c, cx - 8, base - 15, 17, 13, body)
	wrect(c, cx - 10, base - 18, 21, 4, body)
	wrect(c, cx - 5, base - 12, 11, 6, shade)       # recessed inscription panel
	wrect(c, cx - 3, base - 10, 7, 1, body)
	y0 = base - 19
	for i in range(21):  # robed column, narrow at the waist
		w = 4 if i < 3 else 3 if i < 12 else 4
		if i > 17:
			w = 3
		wrect(c, cx - w, y0 - i, 2 * w + 1, 1, body)
	for i in range(3):   # bowed head, turned forward and down (hands to the face)
		wrect(c, cx - 4 - i // 2, y0 - 21 - i, 5, 1, body)
	wrect(c, cx - 5, y0 - 23, 4, 1, body)
	for i in range(16):  # left wing: broad, feathered, swept up and out behind the shoulder
		w = max(2, int(round(6 * math.sin(math.pi * (i + 3) / 21.0))))
		xr = cx - 4 - i // 3
		wrect(c, xr - w, y0 - 13 - i, w + 1, 1, body)
		if i % 3 == 1:
			wrect(c, xr - w - 1, y0 - 13 - i, 1, 1, body)   # feather notches
	for i in range(7):   # right wing: snapped near the root, ragged stump
		w = max(1, 5 - i // 2)
		wrect(c, cx + 4 + i // 3, y0 - 13 - i, w, 1, body)
	for dx, hh in ((3, 2), (5, 1), (7, 3)):
		wrect(c, cx + 4 + dx, y0 - 20 - (hh % 2), 1, hh, body)
	wrect(c, cx - 11, base + 1, 24, 1, shade)
	wput(c, cx + 7, y0 - 23, edge)


def tombstone_big(c, x, base, h, w, lean, col, shade, r, shape="round"):
	"""Large leaning tombstone for the near band: one slab, a carved cross, vertical cracks, a chipped corner."""
	headstone(c, x, base, h, w, col, shade, shape, lean, r, mark=False)
	mx = int(round(x + lean * 0.62))
	my = base - int(h * 0.62)
	wrect(c, mx, my - 5, 2, 11, shade)
	wrect(c, mx - 3, my - 2, 8, 2, shade)
	for k in range(3):  # vertical cracks
		cx = int(round(x + lean * (0.3 + 0.15 * k))) + r.randint(-w // 3, w // 3)
		for i in range(r.randint(8, 16)):
			wput(c, cx + (i // 5) * (1 if k % 2 else -1), base - 4 - i - k * 6, shade)
	wrect(c, int(round(x - w / 2.0)) - 3, base - 1, w + 7, 3, col)  # sunk footing


def near_trunk(c, cx, gyb, top_y, w_top, w_base, flare, r, ph, P, fh=30):
	for y in range(top_y, gyb + 10):
		t = (y - top_y) / float(gyb - top_y)
		w = w_top + (w_base - w_top) * t ** 1.4
		if y < top_y + 14:
			w *= math.sqrt((y - top_y + 1) / 15.0)
		ff = max(0.0, (y - (gyb - fh)) / float(fh)) ** 2.0
		wob = 2.2 * math.sin(y * 0.04 + ph) + 1.2 * math.sin(y * 0.1 + ph * 2) + (0.8 if (y // 5) % 2 else 0)
		cxx = cx + wob
		left = int(round(cxx - w / 2.0 - flare * ff))
		right = int(round(cxx + w / 2.0 + flare * ff))
		for x in range(left, right + 1):
			wput(c, x, y, P["shade"] if x <= left + 1 else P["body"])
		k = 0
		for gx in range(left + 4, right - 3, 5):
			if (y // 7 + k) % 3 != 0:
				wput(c, gx + int(1.2 * math.sin(y * 0.3 + k)), y, P["shade"])
			k += 1
	for _ in range(2):  # knot holes
		ky = r.randint(top_y + 30, max(top_y + 31, gyb - 40))
		kx = cx + r.randint(-int(w_top * 0.2), int(w_top * 0.2))
		for yy in range(-3, 4):
			for xx in range(-2, 3):
				if (xx / 2.2) ** 2 + (yy / 3.4) ** 2 <= 1:
					wput(c, kx + xx, ky + yy, P["shade"])


def root(c, x0, y0, dirn, length, w0, col, r):
	px, py = float(x0), float(y0)
	for i in range(length):
		t = i / float(length)
		px += dirn * (1.0 + 0.4 * (1 - t))
		py += 0.25 + 0.9 * t ** 1.6 + r.uniform(-0.1, 0.1)
		w = max(1, int(round(w0 * (1 - t) + 1)))
		for k in range(w):
			wput(c, int(round(px)), int(round(py)) - k, col)


# ------------------------------------------------------------------ sky
def sky():
	c = Canvas(640, 360)
	stops = [(0, "09080f"), (60, "0d0b16"), (125, "131020"), (190, "191528"), (260, "1e192e"), (359, "1e192e")]
	for (y0, a), (y1, b) in zip(stops, stops[1:]):
		dither_band(c, y0, y1 + 1, hexc(a), hexc(b))
	for y in range(168, 300):  # faint spectral veil low on the horizon (mostly behind the hill bands)
		t = 1 - abs(y - 228) / 62.0
		for x in range(640):
			if t > 0 and dither(t * 0.34, x, y) and (x + y) % 2 == 0:
				c.put(x, y, hexc("1d2530"))
	mx, my, rad = 432, 70, 18
	r = rng("n4sky-stars")
	for _ in range(95):
		x, y = r.randint(0, 639), r.randint(0, 190)
		if math.hypot(x - mx, y - my) < rad + 24:
			continue
		k = r.random()
		col = MOON[3] if k < 0.05 else MOON[2] if k < 0.24 else MOON[1] if k < 0.58 else MOON[0]
		c.put(x, y, col)
		if k < 0.02:  # a rare cold twinkle cross
			for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
				c.put(x + dx, y + dy, MOON[0])
	for y in range(my - rad - 26, my + rad + 27):  # halo: dithered rings, dim
		for x in range(mx - rad - 26, mx + rad + 27):
			d = math.hypot(x - mx, y - my)
			if rad < d <= rad + 3 and (x + y) % 2 == 0:
				c.put(x, y, MOON[1])
			elif rad + 3 < d <= rad + 10 and (x + 2 * y) % 4 == 0:
				c.put(x, y, MOON[0])
			elif rad + 10 < d <= rad + 26 and (x + 2 * y) % 8 == 0:
				c.put(x, y, hexc("171325"))
	moon_cols = [MOON[0], MOON[1], MOON[2], MOON[3]]
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
	for cx, cy, cr in ((mx - 7, my - 4, 5), (mx + 5, my + 6, 4), (mx - 4, my + 10, 3), (mx + 9, my - 9, 3), (mx - 12, my + 4, 3), (mx + 1, my - 2, 2)):
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
	# Thin dark cloud streaks: tapered lenses with dithered rims.
	streaks = [(my + 11, mx - 54, mx + 44, 1.8, 0.03), (44, 30, 200, 2.0, 0.04), (94, 160, 340, 2.4, -0.03), (22, 470, 628, 1.8, 0.04),
		(120, 500, 640, 2.2, -0.04), (140, 10, 120, 1.6, 0.02), (30, 250, 380, 1.4, -0.02), (160, 300, 470, 1.8, 0.02)]
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
						c.put(x, y, hexc("2f2d40") if core else hexc("454359"))
					else:
						c.put(x, y, hexc("06050b") if core else hexc("0d0b16"))
	return c


# ------------------------------------------------------------------ far: ruined basilica, mausoleum roofs, obelisks, cypresses
FAR_W, FAR_H = 640, 170
FAR = {
	"A": hexc("1a1927"), "A_lit": hexc("1d1c2b"), "A_fog": hexc("1b1b2a"),
	"B": hexc("141322"), "B_lit": hexc("191828"), "bas": hexc("121120"), "bas_win": hexc("0a0911"),
	"fog": hexc("191a29"), "crest": hexc("0d0c16"), "crest_rim": hexc("151420"), "hill": hexc("0e0d17"), "ground": hexc("09080f"),
}


def far_build():
	W, H = FAR_W, FAR_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n4far-v1")
	P = FAR
	fA = periodic(W, "n4far-A", 3, 3)
	topA = [int(round(66 + 7 * fA(x))) for x in range(W)]
	for x in range(W):
		for y in range(topA[x], H):
			wput(c, x, y, P["A"])
	# distant spires, obelisks and roof lines on the hazy hill (A tone)
	for x in range(6, W, 1):
		pass
	x = 4
	while x < W:
		k = r.random()
		gx = topA[x % W] + 2
		if k < 0.26:
			cypress(c, x, gx, r.randint(14, 26), r.randint(2, 3), P["A"], r)
		elif k < 0.45:
			yew(c, x, gx, r.randint(12, 18), r.randint(4, 5), P["A"], None, r)
		elif k < 0.7:
			obelisk(c, x, gx, r.randint(14, 22), 1, P["A"], P["A"])
		elif k < 0.9:
			wrect(c, x - 5, gx - 7, 11, 8, P["A"])  # distant crypt with a pitched roof
			tri(c, x, gx - 8, 6, 5, P["A"])
		else:
			cross(c, x, gx, r.randint(8, 12), P["A"], P["A"], 0.0, "latin", r)
		x += r.randint(9, 22)
	fog_over(c, 36, 84, P["A_fog"], 0.8, existing_only=True)
	# ruined cemetery basilica (B tone) on a higher shoulder of the hill, a second ruin (broken arch) to the east
	for bx, by in ((236, 86), ):
		basilica(c, bx, by, P["bas"], P["bas_win"], r)
	for x in range(W):  # shoulder of the hill under the basilica
		pass
	ax = 568   # free-standing ruined gothic arch / gate with two piers and a cypress
	wrect(c, ax - 10, 62, 4, 26, P["bas"])
	wrect(c, ax + 7, 70, 4, 18, P["bas"])
	for i in range(8):
		wput(c, ax - 6 + i, 62 - int(4 * math.sin(math.pi * i / 10.0)), P["bas"])
		wput(c, ax - 6 + i, 63 - int(4 * math.sin(math.pi * i / 10.0)), P["bas"])
	fB = periodic(W, "n4far-B", 3, 3)
	topB = [int(round(78 + 5 * fB(x))) for x in range(W)]
	for x in range(W):
		for y in range(topB[x], H):
			sl = topB[(x + 2) % W] - topB[(x - 2) % W]
			col = P["B"]
			if sl > 0 and y - topB[x] < 2 and (x + y) % 2 == 0:
				col = P["B_lit"]
			wput(c, x, y, col)
	x = 10
	while x < W:   # darker cypress spires and obelisks standing on the B hill
		k = r.random()
		gx = topB[x % W] + 2
		if k < 0.3:
			cypress(c, x, gx, r.randint(14, 26), r.randint(2, 3), P["B"], r, lean=r.choice((-0.5, 0, 0.5)))
		elif k < 0.55:
			yew(c, x, gx, r.randint(12, 20), r.randint(4, 6), P["B"], None, r)
		elif k < 0.8:
			obelisk(c, x, gx, r.randint(14, 24), 1, P["B"], P["B"])
		else:
			cross(c, x, gx, r.randint(9, 14), P["B"], P["B"], 0.0, r.choice(("latin", "latin", "celtic")), r)
		x += r.randint(11, 26)
	fog_over(c, 54, 96, P["fog"], 0.85, existing_only=True)
	# crest: darkest line of mausoleum roofs, crosses and yews along the hilltop
	fC = periodic(W, "n4far-crest", 3, 3)
	gl = [int(round(88 + 4 * fC(x))) for x in range(W)]
	for x in range(W):
		for y in range(gl[x], H):
			wput(c, x, y, P["hill"])
	x = 3
	while x < W:
		k = r.random()
		gx = gl[x % W] + 2
		if k < 0.34:
			w = r.randint(9, 15)
			h = r.randint(7, 12)
			wrect(c, x - w // 2, gx - h, w, h + 1, P["crest"])
			tri(c, x, gx - h - 1, w // 2 + 1, r.randint(4, 7), P["crest"])
			wput(c, x, gx - h - 9, P["crest"])
			x += w // 2
		elif k < 0.5:
			if r.random() < 0.5:
				cypress(c, x, gx, r.randint(14, 24), r.randint(2, 3), P["crest"], r)
			else:
				yew(c, x, gx, r.randint(12, 18), r.randint(4, 6), P["crest"], None, r)
		elif k < 0.72:
			cross(c, x, gx, r.randint(9, 15), P["crest"], P["crest"], r.choice((-1.0, 0, 0, 1.0)), r.choice(("latin", "latin", "broken", "celtic")), r)
		elif k < 0.84:
			obelisk(c, x, gx, r.randint(12, 20), 1, P["crest"], P["crest"])
		else:   # row of tiny headstones
			for i in range(r.randint(3, 6)):
				headstone(c, x + i * 4, gx, r.randint(3, 5), 3, P["crest"], P["crest"], "round", r.choice((-1.0, 0, 1.0)), r, mark=False)
		x += r.randint(6, 13)
	rim_pass(c, {P["crest"]: P["crest_rim"], P["bas"]: hexc("181727"), P["B"]: P["B_lit"]}, 0, 110, 2)
	fog_over(c, 80, 120, P["fog"], 0.5, existing_only=True)
	for x in range(W):  # darker ground below the crest; bottom rows opaque
		for y in range(112, H):
			if dither((y - 112) / 22.0, x, y):
				wput(c, x, y, P["ground"])
	for x in range(W):
		for y in range(134, H):
			wput(c, x, y, P["ground"])
	# lights: a few candles and wisps far away, one dim lit basilica window, one warm mourner's candle
	lights.add(236 - 38 + 5 + 16 + 1, 86 - 30 + 6 + 3, "win", 1, 6, False)
	lights.add(236 + 30 - 1 + 1, 86 - 6, "win", 1, 2, False)
	for lx, ly in ((60, 90), (141, 91), (305, 90), (402, 88), (493, 91), (618, 90)):
		lights.add(lx, ly, "cold", 1, 1, True)
	lights.add(356, 91, "warm", 1, 1, True)
	for lx, ly in ((120, 70), (378, 62), (520, 76)):
		lights.add(lx, ly, "wisp", 1, 1, True)
	return c, lights.render()


# ------------------------------------------------------------------ ridge: rows of crypt roofs, mausoleums, belfry, yews, railings
RIDGE_W, RIDGE_H = 640, 112
RIDGE = {"back": hexc("1b1a29"), "mid": hexc("151422"), "front": hexc("0f0e19"), "fog": hexc("1c1d2b"), "rim": hexc("272639"), "rim2": hexc("201f31"),
	"door": hexc("08070e"), "dk": hexc("0b0a12")}


def ridge_build():
	W, H = RIDGE_W, RIDGE_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n4ridge-v1")
	P = RIDGE
	doors = []

	def row(base, hmin, hmax, step, col, shade, door, gap_p, kinds):
		x = r.randint(0, 6)
		while x < W:
			if r.random() < gap_p:
				x += r.randint(6, 12)
				continue
			k = r.random()
			acc = 0.0
			kind = kinds[-1][0]
			for name, p in kinds:
				acc += p
				if k < acc:
					kind = name
					break
			if kind == "crypt":
				w = r.randint(10, 18)
				h = r.randint(hmin, hmax)
				d = mausoleum(c, x, base, w, h, col, shade, door, "gable", ph=max(4, w // 3), door_w=3, r=r, pil=w >= 14, broken=r.random() < 0.2)
				doors.append((x, base, d, col))
				x += w // 2
			elif kind == "domed":
				w = r.randint(12, 18)
				h = r.randint(hmin, hmax)
				mausoleum(c, x, base, w, h, col, shade, door, "dome", ph=w // 3, door_w=3, r=r)
				x += w // 2
			elif kind == "flat":
				w = r.randint(10, 16)
				h = r.randint(hmin - 3, hmax - 2)
				mausoleum(c, x, base, w, h, col, shade, door, "flat", door_w=3, r=r, pil=False)
				x += w // 2
			elif kind == "cypress":
				cypress(c, x, base + 1, r.randint(hmax + 4, hmax + 18), r.randint(3, 4), col, r, lean=r.choice((-0.5, 0, 0.5)))
			elif kind == "yew":
				yew(c, x, base + 1, r.randint(hmax - 2, hmax + 6), r.randint(5, 8), col, None, r)
			elif kind == "obelisk":
				obelisk(c, x, base, r.randint(hmax, hmax + 10), 2, col, shade)
			elif kind == "cross":
				cross(c, x, base, r.randint(10, 18), col, shade, r.choice((-1.0, 0, 0, 1.0)), r.choice(("latin", "celtic", "broken")), r)
			elif kind == "rail":
				ln = r.randint(18, 36)
				railing(c, x, x + ln, base, 7, col, shade, r, spacing=4, gaps=0.08)
				x += ln
			elif kind == "stones":
				for i in range(r.randint(3, 6)):
					headstone(c, x + i * 5, base + (i % 2), r.randint(5, 9), r.randint(3, 4), col, shade, r.choice(("round", "peak", "square")), r.choice((-1.5, 0, 1.5)), r, mark=False)
				x += 22
			x += r.randint(*step)

	kinds_back = [("crypt", 0.3), ("domed", 0.08), ("flat", 0.08), ("cypress", 0.2), ("yew", 0.06), ("obelisk", 0.1), ("cross", 0.06), ("stones", 0.12)]
	kinds_mid = [("crypt", 0.28), ("domed", 0.08), ("flat", 0.1), ("cypress", 0.1), ("yew", 0.1), ("obelisk", 0.05), ("cross", 0.07), ("rail", 0.1), ("stones", 0.12)]
	kinds_front = [("crypt", 0.1), ("flat", 0.08), ("cypress", 0.08), ("yew", 0.1), ("cross", 0.14), ("rail", 0.28), ("stones", 0.22)]
	row(60, 12, 20, (3, 9), P["back"], P["mid"], P["dk"], 0.04, kinds_back)
	fog_over(c, 40, 64, P["fog"], 0.85, existing_only=True)
	row(73, 11, 17, (3, 8), P["mid"], P["front"], P["door"], 0.04, kinds_mid)
	# ossuary chapel with a belfry (mid row) and a second, lower one (back row)
	chapel(c, 330, 73, P["mid"], P["front"], P["door"], r)
	fog_over(c, 56, 78, P["fog"], 0.7, existing_only=True)
	row(85, 8, 13, (3, 7), P["front"], P["dk"], P["door"], 0.03, kinds_front)
	for x in range(W):
		for y in range(68, 88):
			if c.px[y * W + x] is None:
				c.px[y * W + x] = P["front"]
	rim_pass(c, {P["back"]: P["rim2"], P["mid"]: P["rim2"], P["front"]: hexc("17162a")}, 0, 72, 2)
	fog_over(c, 74, 88, P["fog"], 0.55, existing_only=True)
	for y in range(62, H):  # fade the foot by ordered dither into transparency
		t = min(1.0, (y - 62) / 25.0)
		for x in range(W):
			if c.px[y * W + x] is not None and dither(t, x, y):
				c.px[y * W + x] = None
	for x in range(W):
		for y in range(88, H):
			c.px[y * W + x] = None
	# lights: chapel window, two crypt doorways, candles and wisps (all dim)
	lights.add(330 + 8 - 1, 73 - 21, "win", 3, 4, True)       # chapel belfry slit
	lights.add(330 - 14 + 5, 73 - 7, "winw", 3, 5, True)   # chapel door, warm and dim
	lr = rng("n4ridge-lights")
	picked = 0
	for x, base, d, col in doors:
		if base == 60 and picked < 2 and lr.random() < 0.18:
			lights.add(d[0] + 1, d[1] + 2, "win", 1, 3, True)
			picked += 1
	for _ in range(9):
		lights.add(lr.randint(0, W - 1), lr.randint(70, 84), "cold", 1, 1, True)
	for _ in range(2):
		lights.add(lr.randint(0, W - 1), lr.randint(72, 84), "warm", 1, 1, True)
	for _ in range(4):
		lights.add(lr.randint(0, W - 1), lr.randint(44, 74), "wisp", 1, 1, True)
	return c, lights.render()


# ------------------------------------------------------------------ mid: the graveyard slope
MID_W, MID_H = 512, 132
MID = {
	"stone": hexc("1c1a28"), "stone_f": hexc("171622"), "stone_dk": hexc("100f19"), "rim": hexc("262434"), "rim_f": hexc("201e30"),
	"tree": hexc("0d0c15"), "tree_f": hexc("121120"), "tree_lt": hexc("181727"), "dark": hexc("08070e"),
	"soil": hexc("171620"), "ground": MID_GROUND, "gline": hexc("1a1923"), "fog": hexc("1d1e2d"), "iron": hexc("0b0a12"), "pit": hexc("07060c"),
}


def mid_build():
	W, H = MID_W, MID_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n4mid-v1")
	P = MID
	f = periodic(W, "n4mid-ground", 3, 3)
	gy = [104 + int(round(2.0 * f(x))) for x in range(W)]

	def g(x):
		return gy[x % W]

	for x in range(W):
		for y in range(gy[x], H):
			c.put(x, y, P["ground"])
	back_doors = []
	# back tone (lighter, further): mausoleums, obelisk, cypress/yews, a far willow
	for x, w, h, roof in ((60, 30, 30, "gable"), (222, 26, 26, "dome"), (430, 34, 33, "gable")):
		d = mausoleum(c, x, g(x) + 1, w, h, P["stone_f"], P["stone_dk"], P["dark"], roof, ph=w // 3 + 1, door_w=5, r=r)
		back_doors.append(d)
	obelisk(c, 164, g(164) + 1, 46, 3, P["stone_f"], P["stone_dk"])
	for x, h, hw in ((14, 52, 5), (110, 46, 4), (196, 58, 5), (292, 48, 4), (372, 56, 5), (470, 50, 5)):
		cypress(c, x, g(x) + 2, h, hw, P["tree_f"], r, lean=r.choice((-0.8, 0, 0.8)))
	willow(c, 335, g(335) + 1, 62, P["tree_f"], P["tree"], r, ymax=g(335) - 2, nl=5, slen=(10, 24))
	for x, h, kind in ((250, 26, "latin"), (130, 22, "celtic"), (404, 24, "latin"), (500, 20, "broken")):
		cross(c, x, g(x) + 1, h, P["stone_f"], P["stone_dk"], r.choice((-1.0, 1.0)), kind, r)
	railing(c, 270, 320, g(300) - 1, 11, P["iron"], P["stone_dk"], r, spacing=5, gaps=0.05)
	# front tone: big mausoleums
	for x, w, h, roof in ((152, 42, 40, "gable"), (276, 34, 34, "flat")):
		d = mausoleum(c, x, g(x) + 2, w, h, P["stone"], P["stone_dk"], P["dark"], roof, ph=w // 3 + 2, door_w=6, r=r, broken=(x == 152))
		if x == 152:
			lights.add(d[0] + 1, d[1] + 3, "win", 4, 4, True)
	# trees: yews and weeping willows
	for x, h, hw in ((100, 48, 8), (345, 50, 8), (462, 54, 9)):
		yew(c, x, g(x) + 2, h, hw, P["tree"], P["tree_lt"], r)
	for x, h in ((18, 76), (405, 72)):
		willow(c, x, g(x) + 2, h, P["tree"], P["tree_f"], r, ymax=g(x) + 1, nl=6, slen=(12, 34))
	# open grave
	open_grave(c, 214, g(214), P["soil"], P["pit"], P["ground"])
	# crosses
	for x, h, kind in ((60, 22, "latin"), (205, 30, "celtic"), (372, 21, "latin"), (448, 26, "broken"), (322, 17, "latin"), (188, 17, "broken")):
		cross(c, x, g(x) + 1, h, P["stone"], P["stone_dk"], r.choice((-2.0, -1.0, 1.0, 2.0)), kind, r)
	# railings
	railing(c, 28, 92, g(60) + 1, 11, P["iron"], P["stone_dk"], r, spacing=5, gaps=0.06)
	railing(c, 436, 500, g(470) + 1, 12, P["iron"], P["stone_dk"], r, spacing=5, gaps=0.06)
	# headstones along the slope
	blocked = [(138, 168), (260, 296), (60, 70), (200, 232), (-6, 40), (396, 428)]
	x = r.randint(0, 5)
	stones = []
	while x < W:
		if any(a - 2 < x < b + 2 for a, b in blocked):
			x += 4
			continue
		h = r.randint(8, 17)
		w = r.randint(5, 9)
		shape = r.choice(("round", "round", "peak", "square", "chip"))
		lean = r.choice((-2.5, -1.5, 0, 0, 1.5, 2.5))
		headstone(c, x, g(x) + 1, h, w, P["stone"], P["stone_dk"], shape, lean, r)
		stones.append((x, h))
		x += r.randint(7, 14)
	# a few small tilted stones on the mound edge and bare grass tufts
	for _ in range(60):
		x = r.randint(0, W - 1)
		hh = r.randint(2, 5)
		for i in range(hh):
			wput(c, x + i // 3, g(x) - i, P["tree"])
	rim_pass(c, {P["stone"]: P["rim"], P["stone_f"]: P["rim_f"], P["tree"]: P["rim_f"], P["tree_f"]: P["rim_f"], P["tree_lt"]: P["rim_f"]}, 0, 100, 2)
	for x in range(W):  # ground fog bank: dithered, denser toward the ground line
		for y in range(g(x) - 22, g(x) + 1):
			t = (y - (g(x) - 22)) / 22.0
			if dither(0.32 * t ** 1.4, x, y) and (x + y) % 2 == 0:
				c.put(x, y, P["fog"])
	for x in range(W):  # ground crust line and specks; the bottom rows stay flat
		if r.random() < 0.55:
			c.put(x, gy[x], P["gline"])
	for _ in range(420):
		x, y = r.randint(0, W - 1), r.randint(100, 114)
		if c.get(x, y) == P["ground"] and y >= gy[x] + 2 and r.random() < 1.0 - (y - 104) / 12.0:
			c.put(x, y, P["gline"] if r.random() < 0.5 else P["tree"])
	# lights
	rl = rng("n4mid-lights")
	for sx, sh in stones:
		if rl.random() < 0.09:
			lights.add(sx + rl.choice((-5, 5)), g(sx) - 1, "cold", 1, 2, True)
	lights.add(66, g(66) - 2, "warm", 1, 2, True)
	lights.add(322 + 6, g(328) - 2, "warm", 1, 2, True)
	lights.add(207, g(207) - 1, "cold", 1, 2, True)
	lights.add(150, g(150) - 1, "cold", 1, 2, True)
	lights.add(280, g(280) - 1, "cold", 1, 2, True)
	d0 = back_doors[2]
	lights.add(d0[0] + 1, d0[1] + 2, "win", 2, 4, True)
	for _ in range(5):
		lights.add(rl.randint(0, W - 1), rl.randint(60, 96), "wisp", 2 if rl.random() < 0.4 else 1, 1, True)
	return c, lights.render()


# ------------------------------------------------------------------ wisps: faint spectral veils / grave mist plumes
WISP_W, WISP_H = 512, 220


def wisps():
	W, H = WISP_W, WISP_H
	c = Canvas(W, H)
	inten = [[0.0] * W for _ in range(H)]
	TAU = 2 * math.pi

	def noise(x, y, ph):  # large soft billows, periodic in x (integer frequencies over W)
		return (0.52 + 0.30 * math.sin(TAU * 4 * x / W + ph) * math.cos(y * 0.075 + ph * 1.7)
			+ 0.22 * math.sin(TAU * 9 * x / W + ph * 2.3) * math.cos(y * 0.12 - ph)
			+ 0.12 * math.sin(TAU * 17 * x / W - ph) * math.cos(y * 0.2 + ph * 3))
	# 1. low ground mist, patchy: puffs, densest around rows 150-176 (the mid ground sits at row ~168)
	for y in range(128, 192):
		bell = max(0.0, 1.0 - abs(y - 166) / 32.0) ** 1.4
		for x in range(W):
			n = noise(x, y, 0.7)
			inten[y][x] = max(inten[y][x], 0.62 * bell * max(0.0, (n - 0.25) * 1.6))
	# 2. grave mist plumes rising between tombs: wide, billowy, swaying, widening and thinning upward
	plumes = [(30, 96, 1.0), (118, 108, 0.8), (196, 90, 1.0), (268, 112, 0.7), (338, 84, 1.0), (410, 104, 0.8), (474, 94, 0.9)]
	for px0, top, st in plumes:
		ph = px0 * 0.07
		for y in range(top, 178):
			t = (178 - y) / float(178 - top)  # 0 at the foot, 1 at the tip
			cx = px0 + 11.0 * math.sin(t * 3.4 + ph) * t + 3.0 * math.sin(t * 8.0 + ph * 2)
			hw = 6.0 + 12.0 * t ** 0.7
			vfade = (1 - t) ** 0.8 * min(1.0, (178 - y) / 8.0) * st
			for x in range(int(cx - hw - 2), int(cx + hw + 3)):
				d = abs(x - cx) / hw
				if d < 1:
					n = noise(x, y, ph)
					inten[y][x % W] = min(1.0, inten[y][x % W] + (1 - d * d) ** 1.3 * vfade * max(0.0, (n - 0.2) * 1.5) * 0.85)
	# 3. two broad ribbons drifting at mid height (periodic), faint
	for ry, amp, per, strength in ((124, 6.0, 2, 0.34), (96, 5.0, 3, 0.26)):
		ph = ry * 0.31
		for x in range(W):
			yy = ry + amp * math.sin(TAU * per * x / W + ph) + 2.0 * math.sin(TAU * 7 * x / W + ph * 2)
			amod = max(0.0, math.sin(TAU * (per + 1) * x / W + ph * 3)) ** 1.2
			th = 2.0 + 3.0 * amod
			for y in range(int(yy - th - 1), int(yy + th + 2)):
				d = abs(y - yy) / th
				if d < 1 and 0 <= y < H:
					inten[y][x] = min(1.0, inten[y][x] + (1 - d * d) * strength * amod)
	for y in range(H):
		for x in range(W):
			s = inten[y][x] * 3.6
			if s < 0.3:
				continue
			k = int(s)
			if k < 3 and dither(s - k, x, y):
				k += 1
			if k == 0:
				continue
			c.px[y * W + x] = WISP_RGB + (WISP_LEVELS[min(3, k) - 1],)
	return c


# ------------------------------------------------------------------ near: darkest tombstones, mausoleum corner, bare yew, angel
NEAR_W, NEAR_H = 512, 190
NEAR = {"body": hexc("09080e"), "shade": hexc("060509"), "edge": hexc("161425"), "ground": hexc("0c0b13"), "strand": hexc("0b0a11"), "iron": hexc("07060b")}


def near_build():
	W, H = NEAR_W, NEAR_H
	c = Canvas(W, H)
	lights = Lights(W, H)
	r = rng("n4near-v1")
	P = NEAR
	f = periodic(W, "n4near-ground", 3, 3)
	tops = [100 + int(round(3 * f(x))) for x in range(W)]

	def g(x):
		return tops[x % W]

	for x in range(W):
		for y in range(tops[x], H):
			c.put(x, y, P["ground"])
	# big leaning tombstones
	tombstone_big(c, 30, g(30) + 1, 62, 26, 6, P["body"], P["shade"], r, "round")
	tombstone_big(c, 360, g(360) + 1, 50, 22, -5, P["body"], P["shade"], r, "peak")
	tombstone_big(c, 490, g(490) + 1, 58, 24, 5, P["body"], P["shade"], r, "chip")
	tombstone_big(c, 112, g(112) + 1, 30, 16, -4, P["body"], P["shade"], r, "round")
	# mausoleum corner: heavy block with a broken pediment, pilasters and a stepped plinth
	mx, mb = 205, g(205) + 2
	d = mausoleum(c, mx, mb, 56, 62, P["body"], P["shade"], P["shade"], "gable", ph=14, door_w=10, r=r, broken=True)
	for k in range(4):
		wrect(c, mx - 30 - k * 2, mb + 1 - k, 60 + k * 4, 1, P["body"])
	for yy in range(mb - 62, mb - 56):  # break the pediment: ragged right slope
		wclear(c, mx + 6 + (yy - (mb - 62)) * 2, yy - 6, 8, 3)
	# bare gnarled yew with hanging strands
	tx, tb, ty = 286, g(286), 44
	near_trunk(c, tx, tb, ty, 16, 28, 8, r, 2.3, P)
	ends = []
	# primary limbs rise and arch outward, then droop at the tips (gnarled, no blunt cut), twigs and long strands hang from them
	for dx, dy, bend in ((-30, -22, -5), (-14, -30, -3), (4, -34, 2), (22, -28, 4), (38, -12, 6), (-40, -6, -6)):
		x0, y0 = tx + int(dx * 0.2), ty + 10
		x1, y1 = tx + dx, max(22, ty + 10 + dy)
		pts = limb(c, x0, y0, x1, y1, 6, 2, P["body"], bend=bend)
		side = 1 if dx > 0 else -1
		pts2 = limb(c, x1, y1, x1 + side * r.randint(10, 16), y1 + r.randint(10, 16), 2, 1, P["body"], bend=side * 3)
		ends.extend(pts[3::3] + pts2[2::2])
		bough(c, x1 - side * 4, y1 + 2, -math.pi / 2 + side * r.uniform(0.6, 1.2), 12, 2, P["body"], r, 2, 0.8, (0.6, 0.8), ymin=20)
	for px, py, t in ends:
		if r.random() < 0.55 and py > 14:
			strand(c, int(round(px)), int(round(py)), r.randint(14, 56), P["strand"], P["body"], r, phase=px * 0.4, ymax=g(int(px)) - 4)
	for sx, lo in ((-1, 62), (1, 70)):  # two long drooping side limbs
		x0, y0 = tx + sx * 10, ty + lo
		pts = limb(c, x0, y0, x0 + sx * 40, y0 - r.randint(8, 16), 6, 1, P["body"], bend=sx * 5)
		for px, py, t in pts[8::3]:
			strand(c, int(round(px)), int(round(py)), r.randint(14, 40), P["strand"], P["body"], r, phase=px * 0.4, ymax=g(int(px)) - 4)
	gb = g(tx)
	root(c, tx - 20, gb - 18, -1, 28, 7, P["body"], r)
	root(c, tx + 20, gb - 16, 1, 30, 7, P["body"], r)
	root(c, tx - 16, gb - 6, -1, 16, 4, P["body"], r)
	root(c, tx + 16, gb - 5, 1, 18, 4, P["body"], r)
	# angel statue on a plinth
	ax, ab = 428, g(428) + 1
	angel(c, ax, ab, P["body"], P["shade"], P["edge"])
	# iron railings with rounded finials, low
	railing(c, 56, 100, g(80) + 1, 16, P["iron"], P["shade"], r, spacing=6, gaps=0.1)
	railing(c, 316, 352, g(330) + 1, 16, P["iron"], P["shade"], r, spacing=6, gaps=0.1)
	railing(c, 448, 484, g(466) + 1, 14, P["iron"], P["shade"], r, spacing=6, gaps=0.12)
	# grave mounds, grass blades
	for bx, bw, bh in ((150, 20, 5), (252, 18, 4), (402, 22, 5), (322, 14, 3)):
		for x in range(bx - bw // 2, bx + bw // 2 + 1):
			hh = int(round(bh * math.sqrt(max(0.0, 1 - ((x - bx) / (bw / 2.0 + 0.5)) ** 2))))
			for y in range(g(x) - hh, g(x) + 2):
				wput(c, x, y, P["body"])
	for _ in range(70):
		x = r.randint(0, W - 1)
		hh = r.randint(3, 8)
		for i in range(hh):
			wput(c, x + (i // 4) * r.choice((-1, 0, 1)), g(x) - i, P["strand"] if i < hh - 1 else P["body"])
	wclear(c, 0, 0, W, 9)
	rim_pass(c, {P["body"]: P["edge"]}, 0, 110, 2)
	fade_from = max(tops) + 18
	dither_band(c, fade_from, H - 6, P["ground"], FINAL)
	for y in range(H - 6, H):
		for x in range(W):
			c.put(x, y, FINAL)
	# lights
	rl = rng("n4near-lights")
	lights.add(30 + 20, g(50) - 2, "cold", 1, 2, True)
	lights.add(360 - 18, g(342) - 2, "cold", 1, 2, True)
	lights.add(112 + 12, g(124) - 1, "cold", 1, 2, True)
	lights.add(ax + 16, g(ax + 16) - 2, "warm", 1, 2, True)
	lights.add(466, g(466) - 1, "cold", 1, 2, True)
	lights.add(mx + 17, d[1] + 3, "win", 1, 1, False)
	for _ in range(3):
		lights.add(rl.randint(0, W - 1), rl.randint(40, 92), "wisp", 2 if rl.random() < 0.4 else 1, 1, True)
	return c, lights.render()


# ------------------------------------------------------------------ build / previews
def mist_overlay():
	"""Approximation of the N1 mist strip (assets/sprites/bg_mist.png) tinted cold violet for the preview only."""
	try:
		m = load_png(os.path.join(ROOT, "assets", "sprites", "bg_mist.png"))
	except Exception:
		return None
	for i, p in enumerate(m.px):
		if p is not None:
			m.px[i] = (44, 44, 66, max(1, p[3] // 2))
	return m


def stack(layers, sky_c, lit=None, terrain=False, with_wisps=None, mist=None):
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
	if with_wisps is not None:
		tile(with_wisps, 40)
	tile(near, 170)
	if lit:
		tile(lit["near"], 170)
	c.rect(0, 170 + NEAR_H, 640, 360 - 170 - NEAR_H, FINAL)
	if terrain:  # rough stand-in for the terrain wall (cool stone), floor at y 224
		soil = [hexc(v) for v in ("252a31", "323841", "434a53")]
		c.rect(0, 224, 640, 136, soil[0])
		for y in range(224, 360, 8):
			for x in range(0, 640, 16):
				c.rect(x + ((y // 8) % 2) * 8, y, 15, 7, soil[1] if (x + y) % 3 else soil[2])
		c.rect(0, 224, 640, 2, hexc("2c3a38"))
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


def over(base, ov, bgc):
	"""Composite an alpha overlay onto an opaque-ish stand-in background for preview."""
	b = Canvas(base.w, base.h)
	b.rect(0, 0, base.w, base.h, bgc)
	b.blit(base, 0, 0)
	b.blit(ov, 0, 0)
	return b


def main():
	os.makedirs(OUT, exist_ok=True)
	os.makedirs(PREVIEW, exist_ok=True)
	sk = sky()
	ridge, ridge_l = ridge_build()
	far, far_l = far_build()
	mid, mid_l = mid_build()
	near, near_l = near_build()
	wp = wisps()
	out = {"bg_n4_sky": sk, "bg_n4_far": far, "bg_n4_far_lights": far_l, "bg_n4_ridge": ridge, "bg_n4_ridge_lights": ridge_l,
		"bg_n4_mid": mid, "bg_n4_mid_lights": mid_l, "bg_n4_near": near, "bg_n4_near_lights": near_l, "bg_n4_wisps": wp}
	for name, cv in out.items():
		save_png(cv, os.path.join(OUT, name + ".png"))
	layers = {"far": far, "ridge": ridge, "mid": mid, "near": near}
	lit = {"far": far_l, "ridge": ridge_l, "mid": mid_l, "near": near_l}
	mist = mist_overlay()
	save_png(stack(layers, sk, mist=mist), os.path.join(PREVIEW, "stack_n4.png"))
	save_png(stack(layers, sk, lit, mist=mist), os.path.join(PREVIEW, "stack_n4_lit.png"))
	save_png(stack(layers, sk, lit, with_wisps=wp, mist=mist), os.path.join(PREVIEW, "stack_n4_lit_wisps.png"))
	save_png(stack(layers, sk, lit, terrain=True, with_wisps=wp, mist=mist), os.path.join(PREVIEW, "stack_n4_terrain.png"))
	for name, base, lt in (("far", far, far_l), ("ridge", ridge, ridge_l), ("mid", mid, mid_l), ("near", near, near_l)):
		both = base.copy()
		both.blit(lt, 0, 0)
		save_png(both, os.path.join(PREVIEW, f"bg_band_{name}_lit.png"), 2, (255, 0, 255, 255))
		save_png(base, os.path.join(PREVIEW, f"bg_band_{name}.png"), 2, (255, 0, 255, 255))
	save_png(board([far, ridge, mid, near]), os.path.join(PREVIEW, "bg_n4_layers.png"))
	lit_all = []
	for base, lt in ((far, far_l), (ridge, ridge_l), (mid, mid_l), (near, near_l)):
		both = base.copy()
		both.blit(lt, 0, 0)
		lit_all.append(both)
	save_png(board(lit_all), os.path.join(PREVIEW, "bg_n4_layers_lit.png"))
	save_png(board([sk]), os.path.join(PREVIEW, "bg_n4_sky_board.png"), 1)
	wbg = Canvas(WISP_W, WISP_H)
	wbg.rect(0, 0, WISP_W, WISP_H, hexc("15141f"))
	wbg.blit(wp, 0, 0)
	save_png(board([wbg], 2, 6, (60, 60, 70, 255)), os.path.join(PREVIEW, "bg_n4_wisps_board.png"))
	save_png(board([seam_strip(b, 40) for b in (far, ridge, mid, near)] + [seam_strip(wbg, 40)], 4, 6), os.path.join(PREVIEW, "bg_seams.png"))
	for name in out:
		p = os.path.join(OUT, name + ".png")
		print(name, sha(p))


if __name__ == "__main__":
	main()

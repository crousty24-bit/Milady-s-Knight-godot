"""RUN-019 Claude art: Red Slime, Bloated Slime, Chud Blob, Possessed Skull (+ their VFX).

Usage: python3 tools/art/run019/enemies_blobs.py [--preview DIR]

Contract: work/run019/claude/SPEC.md section B. Outputs (assets/run019/enemies/):
  enemy_slime_red.png       336x24  14 x 24x24  (same layout as enemy_slime_green.png)
  vfx_slime_splash_red.png  240x24  6 x 40x24   (bottom = ground)
  vfx_slime_hit_red.png      64x16  4 x 16x16   (impact centre (8,8), sprays toward +x)
  bloated_slime.png         800x32  20 x 40x32
  vfx_bloated_burst.png     384x32  6 x 64x32   (bottom = ground, centre x=32)
  chud_blob.png            1248x36  26 x 48x36
  possessed_skull.png       460x20  23 x 20x20  (origin = cell centre)
Ground enemies face LEFT, feet on the last row, body centred on cell_w/2.
Everything is procedural and deterministic (no randomness). Original art only.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, TOOLS)
from pixel import Canvas, outline, save_png, sheet  # noqa: E402
from palette import BLOOD, CORRUPT, EMBER, OUTLINE  # noqa: E402
import slime_art as SA  # noqa: E402  (read-only reuse of its drawing functions)
import vfx as VFX  # noqa: E402  (read-only reuse of slime_splash / goo)

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "run019", "enemies")
GREY_BG = (40, 44, 52, 255)
WHITE = (255, 255, 255, 255)
PALE = (255, 244, 196, 255)


# ------------------------------------------------------------------ helpers
def mix(a, b, t):
	return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3)) + (255,)


def tint_ramp(ramp, col, t):
	return [mix(c, col, t) for c in ramp]


def fade(canvas, alpha):
	"""Return a copy whose opaque pixels use at most the given alpha (0..255)."""
	out = Canvas(canvas.w, canvas.h)
	for i, c in enumerate(canvas.px):
		if c is not None:
			out.px[i] = (c[0], c[1], c[2], min(c[3], alpha))
	return out


def disc(c, cx, cy, r, color):
	for y in range(int(cy - r - 1), int(cy + r + 2)):
		for x in range(int(cx - r - 1), int(cx + r + 2)):
			if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
				c.put(x, y, color)


LIGHT = (-0.5, -0.55, 0.67)


def paint(w, h, ells, ramp, clip_y=None, light=LIGHT):
	"""Height-field style shading of the union of ellipses (cx, cy, rx, ry).

	Each pixel takes the normal of the ellipsoid that is highest there, giving
	rounded lumps with visible creases, lit from the upper left.
	"""
	ln = math.sqrt(sum(v * v for v in light))
	lx, ly, lz = (v / ln for v in light)
	best = {}
	for (cx, cy, rx, ry) in ells:
		scale = min(rx, ry)
		for y in range(max(0, int(cy - ry - 1)), min(h, int(cy + ry + 2))):
			if clip_y is not None and y > clip_y:
				continue
			for x in range(max(0, int(cx - rx - 1)), min(w, int(cx + rx + 2))):
				dx = (x + 0.5 - cx) / rx
				dy = (y + 0.5 - cy) / ry
				d2 = dx * dx + dy * dy
				if d2 <= 1.0:
					nz = math.sqrt(1.0 - d2)
					hz = nz * scale
					if (x, y) not in best or hz > best[(x, y)][0]:
						best[(x, y)] = (hz, dx, dy, nz)
	cv = Canvas(w, h)
	for (x, y), (hz, dx, dy, nz) in best.items():
		n = math.sqrt(dx * dx + dy * dy + nz * nz + 1e-9)
		d = (dx * lx + dy * ly + nz * lz) / n
		tone = 4 if d > 0.9 else 3 if d > 0.52 else 2 if d > 0.14 else 1
		cv.put(x, y, ramp[tone])
	# rim shading: dark inner edge below / right, lit edge above / left
	for (x, y) in list(best):
		below = (x, y + 1) not in best
		right = (x + 1, y) not in best
		up = (x, y - 1) not in best
		left = (x - 1, y) not in best
		if (below or right) and not (up or left):
			cv.put(x, y, ramp[0] if cv.get(x, y) == ramp[1] else ramp[1])
		elif up or left:
			cv.put(x, y, ramp[3] if cv.get(x, y) in (ramp[1], ramp[2]) else cv.get(x, y))
	return cv


def inside(cv, x, y):
	return cv.get(x, y) is not None


def dot(cv, x, y, c):
	if inside(cv, x, y):
		cv.put(x, y, c)


def limb(ells, p0, p1, r0, r1, n=None):
	steps = n or int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])) / 1.5) + 2
	for i in range(steps + 1):
		t = i / steps
		r = r0 + (r1 - r0) * t
		ells.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, r, r))


def polyline(cv, pts, color, only_inside=True):
	for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
		steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
		for i in range(steps + 1):
			t = i / steps
			x = int(math.floor(x0 + (x1 - x0) * t + 0.5))
			y = int(math.floor(y0 + (y1 - y0) * t + 0.5))
			if only_inside:
				dot(cv, x, y, color)
			else:
				cv.put(x, y, color)


def glint(cv, x, y, size, core=WHITE, arm=PALE):
	cv.put(x, y, core)
	for d in range(1, size + 1):
		col = arm if d == 1 else (255, 244, 196, 200)
		for ddx, ddy in ((d, 0), (-d, 0), (0, d), (0, -d)):
			cv.put(x + ddx, y + ddy, col)


# =================================================================== RED SLIME
RED_RAMP = [BLOOD[0], BLOOD[1], BLOOD[2], BLOOD[3], BLOOD[4]]
RED_DARK = BLOOD[0]
HOT_WHITE = (255, 226, 214, 255)


def red_frame(params, idx=0, mode="normal"):
	"""Red Slime: same jelly body as the green one + dorsal spikes and a dark pulsing core."""
	w, h, lean, shift, wob = params
	ramp = RED_RAMP
	cells = SA.cells_of(w, h, lean, shift, wob)
	body = SA.shade(cells, ramp)
	SA.specular(body, cells, ramp, h)
	top_row = {}
	for (x, y) in cells:
		top_row[x] = min(top_row.get(x, 99), y)
	cx = 12.0 + shift
	off_top = lean * 0.9
	# dorsal spikes: three thorns with light tips, leaning with the body
	if mode != "dead":
		for (sx, sh) in ((-4, 2), (0, 3), (4, 2)):
			bx = int(round(cx + off_top + sx * (w / 16.0)))
			if bx not in top_row:
				continue
			ty = top_row[bx]
			sh = sh + (1 if h >= 13 else 0) - (1 if h <= 8 else 0)
			for j in range(sh):
				y = ty - j
				if y < 1:
					break
				ww = 1 if j >= sh - 1 else 2
				x0 = bx - (0 if ww == 1 else 1)
				for xx in range(x0, x0 + ww):
					body.put(xx, y, BLOOD[4] if j == sh - 1 else BLOOD[1] if xx > bx else BLOOD[2])
				if ww == 2:
					body.put(x0, y, BLOOD[3])
	# dark core pulsing in the back/lower body (hot ember point in the middle)
	if mode != "dead":
		ccx = int(round(cx + 3 + lean * 0.4))
		ccy = 22 - max(2, int(h * 0.38))
		for dx in range(-1, 2):
			for dy in range(0, 2):
				if (ccx + dx, ccy + dy) in cells:
					body.put(ccx + dx, ccy + dy, RED_DARK)
		if (ccx, ccy) in cells:
			body.put(ccx, ccy, EMBER[2] if idx % 2 else BLOOD[4])
	SA.bubbles(body, cells, ramp, idx, 1 if h >= 10 else 0)
	# angry eyes: pink-white sclera, dark pupils (swap the module constant only in-process)
	old = SA.BONE_WHITE
	SA.BONE_WHITE = HOT_WHITE
	try:
		SA.eyes(body, cells, w, h, lean, shift, False, "squint" if mode == "hit" else mode)
	finally:
		SA.BONE_WHITE = old
	SA.mouth(body, cells, w, h, lean, shift, mode)
	return outline(body, OUTLINE)


def red_slime_sheet():
	frames = [red_frame(p, i) for i, p in enumerate(SA.PATROL)]
	frames += [red_frame(p, i, "hit") for i, p in enumerate(SA.HIT)]
	f0 = red_frame((20, 13, 0.0, 0, 0.3), 0, "dead")
	for (x, y) in ((11, 11), (12, 12), (11, 13), (12, 14), (11, 15)):
		if f0.get(x, y) is not None:
			f0.put(x, y, BLOOD[4])
	f1 = SA.puddle(RED_RAMP, 11.0, 6, 0.6, drops=((-8, 9, 2), (-5, 11, 2), (4, 11, 2), (7, 8, 2), (0, 12, 1), (-2, 8, 1)))
	f2 = SA.puddle(RED_RAMP, 11.0, 3, 1.2, drops=((-6, 6, 1), (6, 5, 1)))
	f3 = SA.puddle(RED_RAMP, 9.0, 2, 2.0)
	frames += [f0, f1, f2, f3]
	return sheet(frames, len(frames))


def red_splash():
	frames = VFX.slime_splash(RED_RAMP)
	for i, c in enumerate(frames):
		# ember flecks so the red goo reads as hot/dangerous rather than a plain recolour
		for k, (ex, ey) in enumerate(((12, 12), (27, 11), (20, 7), (8, 15), (32, 14))):
			y = ey - i + (i * i) // 2
			if i < 5 and k <= 4 - i and 0 <= y < 22 and c.get(ex, y) is None:
				c.put(ex, y, EMBER[2] if k % 2 else BLOOD[4])
	return sheet(frames, 6)


def red_hit():
	"""4 frames 16x16: red goo + ember sparks spraying toward +x, impact at (8, 8)."""
	frames = []
	jets = [(1.7, -1.5), (2.2, -0.3), (1.0, -2.1), (2.4, -1.0), (0.8, 0.5), (-1.2, -1.4)]
	for i in range(4):
		c = Canvas(16, 16)
		t = i + 1
		if i == 0:
			for ddx, ddy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (-1, -1)):
				c.put(8 + ddx, 8 + ddy, HOT_WHITE if ddx == 0 and ddy == 0 else BLOOD[4] if abs(ddx) + abs(ddy) == 1 else BLOOD[3])
			for d in (2, 3):
				c.put(8 + d, 8 - d // 2, BLOOD[4])
		for k, (vx, vy) in enumerate(jets):
			x = 8 + vx * t * 1.05
			y = 8 + vy * t * 1.0 + 0.45 * t * t
			if not (0 <= x < 15 and 0 <= y < 15) or (i == 3 and k % 2):
				continue
			size = 2 if i < 3 and k < 3 else 1
			VFX.goo(c, int(x), int(y), RED_RAMP, size)
		if i in (1, 2):
			c.put(10 + i * 2, 5 - i, EMBER[3])
			c.put(9 + i * 2, 11, EMBER[2])
		frames.append(c)
	return sheet(frames, 4)


# ================================================================ BLOATED SLIME
BL = [(36, 27, 44, 255), (62, 52, 70, 255), (98, 102, 80, 255), (142, 152, 98, 255), (198, 208, 142, 255)]
BL_VEIN = CORRUPT[3]
PUS = (236, 228, 150, 255)
PUS_HI = (255, 250, 206, 255)
PUS_SH = (170, 150, 84, 255)
BL_BOT = 30


def bloated_shapes(w, h, lean=0.0, wob=0.0):
	cx = 20.0
	bot = BL_BOT + 0.5
	return [
		(cx, bot - h * 0.42, w * 0.5, h * 0.55),
		(cx - w * 0.2 + lean, bot - h * 0.64 + wob * 0.3, w * 0.27, h * 0.34),
		(cx + w * 0.24, bot - h * 0.40 + wob, w * 0.24, h * 0.34),
		(cx - w * 0.31, bot - h * 0.22, w * 0.2, h * 0.24),
		(cx + w * 0.05 - lean * 0.4, bot - h * 0.8, w * 0.2, h * 0.22),
	]


PUSTULES = [(-0.05, 0.84, 3), (0.24, 0.66, 3), (0.06, 0.3, 3), (-0.36, 0.2, 2), (0.36, 0.28, 2), (0.14, 0.5, 2), (-0.2, 0.74, 2)]


def pustule(cv, x, y, r, glow=0.0):
	rim = RED_DARK if glow < 0.5 else BLOOD[3]
	fill = PUS if glow < 0.5 else (255, 214, 140, 255)
	if r >= 3:
		for yy in range(-2, 3):
			for xx in range(-2, 3):
				if abs(xx) + abs(yy) <= 3 and not (abs(xx) == 2 and abs(yy) == 2):
					dot(cv, x + xx, y + yy, rim if abs(xx) + abs(yy) >= 3 else fill)
		dot(cv, x - 1, y - 1, PUS_HI)
		dot(cv, x, y - 1, PUS_HI)
		dot(cv, x + 1, y + 1, PUS_SH)
	elif r == 2:
		for xx, yy in ((0, 0), (1, 0), (0, 1), (1, 1)):
			dot(cv, x + xx, y + yy, fill)
		for xx, yy in ((-1, 0), (-1, 1), (0, -1), (1, -1), (2, 0), (2, 1), (0, 2), (1, 2)):
			dot(cv, x + xx, y + yy, rim)
		dot(cv, x, y, PUS_HI)
	else:
		dot(cv, x, y, PUS_HI if glow < 0.5 else (255, 226, 160, 255))
		for xx, yy in ((-1, 0), (1, 0), (0, 1), (0, -1)):
			dot(cv, x + xx, y + yy, rim)


def bloated_frame(w, h, lean=0.0, wob=0.0, mode="normal", glow=0.0, ripple=None, pop=0.0):
	ramp = BL if glow <= 0 else tint_ramp(BL, EMBER[1], 0.22 * glow)
	ells = bloated_shapes(w, h, lean, wob)
	body = paint(40, 32, ells, ramp, clip_y=BL_BOT)
	cx = 20.0
	bot = BL_BOT
	vc = BL_VEIN if glow < 0.4 else (BLOOD[3] if glow < 0.8 else EMBER[2])
	vseg = [[(cx - w * .30, bot - h * .55), (cx - w * .15, bot - h * .45), (cx - w * .1, bot - h * .25)],
		[(cx + w * .1, bot - h * .8), (cx + w * .18, bot - h * .6), (cx + w * .3, bot - h * .5), (cx + w * .33, bot - h * .35)],
		[(cx - w * .05, bot - h * .3), (cx + w * .08, bot - h * .2)]]
	for seg in vseg:
		polyline(body, [(int(x), int(y)) for x, y in seg], vc)
	if glow >= 0.8:
		for seg in vseg[:2]:
			polyline(body, [(int(x) + 1, int(y)) for x, y in seg], BLOOD[3])
	for k, (rx, ry, r) in enumerate(PUSTULES):
		px = int(round(cx + rx * w))
		py = int(round(bot - ry * h))
		rr = r + (1 if glow > 0.5 and r == 2 else 0)
		if pop > 0 and k % 2 == 0:
			rr = 3
		pustule(body, px, py, min(3, rr), glow)
	# face: one big dull eye, one small, lopsided drooling mouth
	ex = int(round(cx - w * 0.33))
	ey = int(round(bot - h * 0.5))
	sclera = (226, 222, 150, 255)
	if mode == "hit":
		for dx in range(4):
			dot(body, ex + dx, ey, OUTLINE)
		for dx in range(3):
			dot(body, ex + 6 + dx, ey - 1, OUTLINE)
	elif mode == "dead":
		for ddx, ddy in ((0, 0), (2, 0), (1, 1), (0, 2), (2, 2)):
			dot(body, ex + ddx, ey + ddy - 1, OUTLINE)
	else:
		# big eye (4x4 sclera, 2x2 pupil, heavy lid) and small eye
		for dx in range(4):
			for dy in range(4):
				if not (dx in (0, 3) and dy in (0, 3)):
					dot(body, ex + dx, ey + dy - 1, sclera)
		for dx in range(2):
			for dy in range(2):
				dot(body, ex + dx, ey + dy, BLOOD[2] if glow > 0 else OUTLINE)
		for dx in range(-1, 5):
			dot(body, ex + dx, ey - 2, OUTLINE)
		dot(body, ex + 4, ey - 1, OUTLINE)
		for dx in range(3):
			for dy in range(3):
				if not (dx == 2 and dy == 0):
					dot(body, ex + 7 + dx, ey + dy - 1, sclera)
		dot(body, ex + 7, ey, OUTLINE)
		dot(body, ex + 7, ey - 1, OUTLINE)
		for dx in range(7, 11):
			dot(body, ex + dx, ey - 2 + (dx - 7) // 2, OUTLINE)
	my = int(round(bot - h * 0.24))
	mx = int(round(cx - w * 0.3))
	open_m = 1 + (1 if glow > 0.3 else 0)
	for dx in range(7):
		dot(body, mx + dx, my + (1 if dx in (0, 6) else 0), OUTLINE)
	for dy in range(open_m):
		for dx in range(1, 6):
			dot(body, mx + dx, my + 1 + dy, BLOOD[0] if glow < 0.5 else BLOOD[3])
	dot(body, mx + 2, my + 1, PUS_HI)
	dot(body, mx + 4, my + 1, PUS_HI)
	dot(body, mx + 1, my + 2 + open_m - 1, PUS)  # drool
	if ripple is not None:
		rcx, rcy, rr = ripple
		for k in range(40):
			a = k / 40.0 * math.tau
			x = int(round(rcx + math.cos(a) * rr))
			y = int(round(rcy + math.sin(a) * rr * 0.75))
			if k % 3:
				dot(body, x, y, ramp[4] if (x + y) % 2 == 0 else ramp[3])
	gx, gy = int(round(cx - w * 0.2 + lean)) - 1, int(round(bot - h * 0.8))
	for ddx, ddy, t in ((0, 0, 4), (1, 0, 4), (0, 1, 4), (2, 0, 3), (0, 2, 3)):
		dot(body, gx + ddx, gy + ddy, ramp[t])
	out = outline(body, OUTLINE)
	if glow >= 0.6:
		glint(out, int(cx - w * 0.2 + lean) - 2, int(bot - h * 0.8) - 2, 3 if glow > 0.9 else 2)
		for ddx, ddy in ((12, -4), (-14, -2)):
			sx, sy = int(cx + ddx * w / 30), int(bot - h * 0.55 + ddy)
			out.put(sx, sy, EMBER[3])
			out.put(sx, sy - 1, EMBER[2])
	return out


def goo_puddle(rx, ht, ramp, drops=(), bubbles=0, cxp=20.0, w=40, h=32):
	c = Canvas(w, h)
	bottom = BL_BOT
	for r in range(ht):
		t = (r + 0.5) / ht
		half = rx * (1.0 - t ** 2.0) ** 0.5
		half += 0.5 * math.sin(r * 1.3 + rx)
		for x in range(w):
			if abs(x + 0.5 - cxp) <= half:
				tone = 1 if r == 0 and (x + 0.5 < cxp - half + 2 or x + 0.5 > cxp + half - 2) else 2 if r < ht - 1 or ht == 1 else 3
				if x + 0.5 < cxp - half * 0.3 and r > 0:
					tone = 3
				c.put(x, bottom - r, ramp[tone])
	xs = [x for x in range(w) if c.get(x, bottom) is not None]
	if xs:
		c.put(xs[0] + 2, bottom - min(ht - 1, 1), ramp[4])
		c.put(xs[0] + 3, bottom - min(ht - 1, 1), ramp[4])
	for k in range(bubbles):
		bx = int(cxp - 8 + k * 7)
		by = bottom - max(0, ht - 1)
		if c.get(bx, by) is not None:
			pustule(c, bx, by, 1)
	for (dx, dy, sz, col) in drops:
		for ox in range(sz):
			for oy in range(sz):
				c.put(int(cxp + dx) + ox, int(bottom - dy) + oy, col if (ox, oy) != (0, 0) else PUS_HI if sz == 2 else col)
	return outline(c, OUTLINE)


def bloated_sheet():
	frames = []
	crawl = [(28, 24, 0.0, 0.0), (30, 22, 0.6, 0.6), (32, 20, 1.0, 1.0), (26, 26, -1.4, 0.4),
		(27, 27, -2.0, -0.4), (31, 21, -0.8, -0.8), (30, 22, -0.2, -0.3), (28, 25, 0.4, 0.3)]
	for (w, h, lean, wob) in crawl:
		frames.append(bloated_frame(w, h, lean, wob))
	# swell (telegraph/contact): grows, veins turn red, pustules glow, white glint
	for w, h, g in ((30, 25, 0.35), (32, 26, 0.65), (34, 28, 1.0), (34, 27, 0.9)):
		frames.append(bloated_frame(w, h, 0.0, 0.0, glow=g))
	frames.append(bloated_frame(31, 22, 0.8, 0.8, mode="hit", ripple=(24, 22, 6)))
	frames.append(bloated_frame(27, 27, -0.8, -0.5, mode="hit", ripple=(21, 20, 11)))
	# death: overswell with cracks, burst, deflate, puddle
	f14 = bloated_frame(34, 29, 0.0, 0.0, mode="dead", glow=1.0, pop=1.0)
	for pts in (((19, 12), (21, 15), (19, 18), (21, 21)), ((26, 14), (24, 17), (26, 20))):
		polyline(f14, pts, PALE)
	frames.append(f14)
	f15 = bloated_frame(30, 14, 0.0, 0.0, mode="dead", glow=0.6)
	for (x, y, s, c) in ((6, 12, 3, PUS), (12, 6, 2, PUS_HI), (30, 10, 3, PUS), (34, 15, 2, BL[3]), (20, 4, 2, PUS_HI), (27, 5, 2, BL[3]), (3, 20, 2, BL[3]), (36, 22, 2, PUS)):
		for ox in range(s):
			for oy in range(s):
				f15.put(x + ox, y + oy, c if (ox, oy) != (0, 0) else PUS_HI)
	frames.append(f15)
	frames.append(goo_puddle(15.0, 8, BL, ((-14, 12, 3, PUS), (-10, 9, 2, BL[3]), (11, 12, 3, PUS), (14, 8, 2, BL[3]), (-4, 13, 2, PUS_HI), (4, 15, 2, BL[3])), 1))
	frames.append(goo_puddle(16.0, 5, BL, ((-15, 6, 2, PUS), (13, 5, 2, PUS), (-6, 9, 1, BL[3])), 2))
	frames.append(goo_puddle(15.0, 3, BL, ((14, 3, 1, PUS),), 2))
	frames.append(goo_puddle(13.0, 2, BL, (), 1))
	return sheet(frames, 20)


def bloated_burst():
	"""6 frames 64x32: gerbe of droplets + corrupt gas. Ground = bottom, centre x=32."""
	frames = []
	gas = [(176, 196, 104), (146, 166, 92), (118, 134, 86)]
	drops = [(-1.0, -2.2, 3), (1.1, -2.0, 3), (-2.0, -1.5, 2), (2.2, -1.6, 2), (-0.3, -2.7, 2), (0.6, -2.4, 3), (-3.0, -1.0, 2), (3.1, -1.1, 2),
		(-1.6, -1.9, 2), (1.8, -1.8, 2), (-3.8, -0.6, 1), (3.9, -0.7, 1)]
	for i in range(6):
		c = Canvas(64, 32)
		for k, (gx, gy, gr) in enumerate(((-9, 2, 5), (8, 3, 5), (0, 6, 6), (-15, 0, 3), (15, 1, 3))):
			r = gr + i * 1.1 - (1.0 if i == 5 else 0)
			cxg = 32 + gx * (1 + 0.15 * i)
			cyg = 27 - gy - i * 2.0 - (k % 2) * 1.5
			col = gas[min(2, i // 2)]
			alpha = (210, 190, 165, 130, 95, 60)[i]
			for yy in range(int(cyg - r), int(cyg + r) + 1):
				for xx in range(int(cxg - r), int(cxg + r) + 1):
					d = (xx - cxg) ** 2 + (yy - cyg) ** 2
					if d <= r * r and (d < r * r * 0.7 or (xx + yy) % 2 == 0):
						c.put(xx, yy, col + (alpha if d > r * r * 0.35 else min(255, alpha + 40),))
		half = (5, 9, 13, 14, 11, 7)[i]
		ht = (4, 3, 3, 2, 2, 1)[i]
		for hh in range(ht):
			for x in range(32 - half, 32 + half):
				edge = x in (32 - half, 32 + half - 1)
				c.put(x, 31 - hh, BL[1] if edge else BL[2] if hh < ht - 1 else BL[3])
		for x in (32 - half, 32 + half - 1):
			c.put(x, 31, OUTLINE)
		if i in (1, 2, 3):
			c.put(32 - half // 2, 30 if ht > 1 else 31, PUS_HI)
		t = (i + 1) * 0.9
		if i == 0:
			for x in range(26, 38):
				for y in range(19, 28):
					if ((x - 32) / 6.0) ** 2 + ((y - 26) / 6.0) ** 2 <= 1.0:
						c.put(x, y, PUS_HI if x - 32 < -1 and y < 24 else PUS if y < 25 else BL[3])
		for k, (vx, vy, sz) in enumerate(drops):
			x = 32 + vx * t * 4.4
			y = 27 + vy * t * 4.6 + 1.9 * t * t
			if y > 29 or (i == 5 and sz >= 2) or (i == 4 and sz == 3 and k % 2):
				continue
			xi, yi = int(x), int(y)
			for ox in range(sz):
				for oy in range(sz):
					c.put(xi + ox, yi + oy, PUS_HI if (ox, oy) == (0, 0) and sz > 1 else PUS if oy == 0 else BL[3] if oy == 1 else BL[2])
			if i in (1, 2) and sz >= 2:
				c.put(xi + 1, yi - 1, PUS_SH)
		frames.append(c)
	return sheet(frames, 6)


# ==================================================================== CHUD BLOB
FL = [(34, 38, 34, 255), (62, 72, 60, 255), (98, 112, 88, 255), (138, 152, 114, 255), (184, 196, 152, 255)]
RAW = (150, 92, 90, 255)
RAW_DK = (104, 60, 66, 255)
TEETH = (214, 206, 174, 255)
CW, CH = 48, 36
CBOT = 34
CCX = 24


def chud_pose(**kw):
	p = dict(bob=0.0, lean=0.0, breath=0.0, foot=0.0, S=(CCX - 9, CBOT - 11), E=None, F=(CCX - 13, CBOT - 6), fr=6.0, glow=0.0,
		mouth=1, head=(0.0, 0.0), squint=False, sag=0.0, melt=0.0, lump=0.0, flash=0.0)
	p.update(kw)
	return p


def chud_frame(p):
	glow = p["glow"]
	ramp = FL if glow <= 0 else tint_ramp(FL, BLOOD[3], 0.16 * glow)
	bob, lean, br = p["bob"], p["lean"], p["breath"]
	m = p["melt"]
	cx = CCX
	bot = CBOT + 0.5

	def E(x, cy, rx, ry):
		# melting: everything slumps toward the ground and spreads
		return (x, bot - (bot - cy) * (1 - 0.78 * m), rx * (1 + 0.55 * m), ry * (1 - 0.6 * m))

	lm = p["lump"]
	torso = [
		E(cx + 1.5, bot - 8, 9.5 + br * 0.5, 8),
		E(cx + 5 + lean * 0.6, bot - 16.5 + bob - p["sag"], 7.5 + br * 0.4, 9),
		E(cx - 2 + lean, bot - 12 + bob * 0.5 - p["sag"], 6.5, 6),
		E(cx + 7 + lm, bot - 5, 4.5, 4.5),
		E(cx - 6 - lm, bot - 4, 4, 3.5),
	]
	feet = [E(cx - 4 + p["foot"], bot - 1.5, 4.5, 2.5), E(cx + 6 - p["foot"], bot - 1.5, 4.5, 2.5)]
	body = paint(CW, CH, torso + feet, ramp, clip_y=CBOT)
	for (px, py, r) in ((cx + 4, bot - 10, 2), (cx - 1, bot - 6, 1), (cx + 9, bot - 14, 1)):
		py2 = int(bot - (bot - py) * (1 - 0.78 * m))
		for ddx in range(-r, r + 1):
			for ddy in range(-r, r + 1):
				if abs(ddx) + abs(ddy) <= r:
					dot(body, int(px) + ddx, py2 + ddy, RAW if ddx <= 0 and ddy <= 0 else RAW_DK)
	if m < 0.5:
		polyline(body, [(cx + 2, bot - 12), (cx + 5, bot - 9), (cx + 4, bot - 6)], ramp[0])
		for k in range(3):
			dot(body, int(cx + 3 + k * 1.2), int(bot - 11 + k * 2), ramp[3])
	if glow > 0:
		vc = BLOOD[3] if glow < 0.8 else EMBER[2]
		for seg in (((cx + 8, bot - 22), (cx + 6, bot - 16), (cx + 9, bot - 10), (cx + 7, bot - 5)),
			((cx - 2, bot - 18), (cx + 1, bot - 14), (cx - 1, bot - 9)),
			((cx + 11, bot - 18), (cx + 13, bot - 13))):
			polyline(body, [(int(x + lean * 0.5), int(y - p["sag"] + bob * 0.5)) for x, y in seg], vc)
	out = outline(body, OUTLINE)
	# ---- head (small, sunk between the shoulders, wide mouth)
	hx = cx - 6 + lean + p["head"][0]
	hy = bot - 21.5 + bob * 0.5 + p["head"][1] + m * 12
	if m < 0.9:
		head = paint(CW, CH, [(hx, hy, 6.5, 5.0)], ramp, clip_y=CBOT)
		ey = int(hy) - 1
		ex = int(hx) - 4
		eyec = BLOOD[3] if glow < 0.5 else EMBER[3]
		if p["squint"] or m > 0.3:
			for ddx in range(2):
				dot(head, ex + ddx, ey, OUTLINE)
				dot(head, ex + 4 + ddx, ey + 1, OUTLINE)
		else:
			for ddx in range(2):
				for ddy in range(2):
					dot(head, ex + ddx, ey + ddy, eyec)
					dot(head, ex + 5 + ddx, ey + 1 + ddy, eyec)
			dot(head, ex, ey, EMBER[3] if glow > 0.5 else BLOOD[4])
			for ddx in range(-1, 3):
				dot(head, ex + ddx, ey - 1, OUTLINE)
			for ddx in range(4, 8):
				dot(head, ex + ddx, ey, OUTLINE)
		my = int(hy) + 2
		op = p["mouth"]
		for ddx in range(-6, 6):
			for ddy in range(op):
				dot(head, int(hx) + ddx, my + ddy, EMBER[1] if glow > 0.5 else BLOOD[0])
			dot(head, int(hx) + ddx, my - 1, OUTLINE)
		for ddx in (-4, -2, 0, 2):
			dot(head, int(hx) + ddx, my, TEETH)
		if op > 1:
			for ddx in (-3, 1, 3):
				dot(head, int(hx) + ddx, my + op - 1, TEETH)
		if glow > 0.5:
			for ddx in range(-4, 4, 2):
				dot(head, int(hx) + ddx, my + op - 1, EMBER[3])
		out.blit(outline(head, OUTLINE), 0, 0)
	# ---- club arm (drawn last, in front)
	arm_cells = []
	S = (p["S"][0] + lean * 0.5, p["S"][1] + bob * 0.5 - p["sag"])
	F = p["F"]
	if m > 0:
		F = (F[0] + 2 * m, bot - 4 - (bot - 4 - F[1]) * (1 - m))
	Epos = p["E"]
	if Epos is None:
		Epos = ((S[0] + F[0]) / 2 - 2, (S[1] + F[1]) / 2 + 2)
	Wr = (Epos[0] + (F[0] - Epos[0]) * 0.72, Epos[1] + (F[1] - Epos[1]) * 0.72)
	limb(arm_cells, S, Epos, 4.0, 3.4)
	limb(arm_cells, Epos, Wr, 3.4, 3.0)
	arm_cells.append((F[0], F[1], p["fr"], p["fr"] * (0.92 - 0.25 * m)))
	arm = paint(CW, CH, arm_cells, tint_ramp(ramp, RAW, 0.2), clip_y=CBOT)
	for k in range(3):  # rotten bandage band at the wrist
		wx, wy = int(Wr[0] + k * 0.7), int(Wr[1] - 2 + k)
		for dd in (-2, -1, 0, 1):
			dot(arm, wx + dd, wy + (dd > 0), RAW_DK)
	fx, fy = int(F[0]), int(F[1])
	for ddx, ddy in ((-3, -2), (-2, -3), (-4, 0), (-3, 1)):
		dot(arm, fx + ddx, fy + ddy, RAW if ddy < 0 else RAW_DK)
	for ddx in (-2, 0, 2):
		dot(arm, fx + ddx, fy + 2, ramp[0])
	for ddx, ddy in ((-1, -int(p["fr"] * 0.9)), (2, -int(p["fr"] * 0.9) + 1), (-int(p["fr"]) + 1, -2)):
		dot(arm, fx + ddx, fy + ddy, TEETH)
	if glow > 0:
		polyline(arm, [(int(S[0]), int(S[1])), (int(Epos[0]), int(Epos[1])), (fx, fy)], BLOOD[3] if glow < 0.8 else EMBER[2])
	arm = outline(arm, OUTLINE)
	if p["flash"] > 0:
		glint(arm, fx - int(p["fr"]) + 1, fy - int(p["fr"]) + 1, 3)
		for ddx, ddy in ((3, -6), (-2, -8), (7, -3)):
			arm.put(fx + ddx, fy + ddy, EMBER[3])
	out.blit(arm, 0, 0)
	return out


def dust(c, cxp, base, i):
	"""Impact dust and ground cracks in front of the Chud (x <= cxp)."""
	tones = [(176, 170, 160, 235), (146, 140, 134, 215), (112, 108, 106, 190), (86, 84, 88, 150)]
	if i == 0:
		for k, (dx, r) in enumerate(((-2, 4), (5, 3), (-9, 3), (11, 2))):
			disc(c, cxp + dx, base - r + 1, r, tones[0] if k < 2 else tones[1])
	elif i == 1:
		for k, (dx, r) in enumerate(((-4, 4), (4, 4), (-11, 3), (10, 3), (-1, 6))):
			disc(c, cxp + dx, base - r + 1 - (k == 4) * 2, r, tones[1] if k < 4 else tones[2])
	else:
		for k, (dx, r) in enumerate(((-6, 3), (6, 3), (-13, 2), (12, 2))):
			disc(c, cxp + dx, base - r - 1, r, tones[2 + (i > 2)])
	for dx in range(-9, 8):
		if abs(dx) % 3 == 0:
			c.put(cxp + dx, base, OUTLINE)


def chud_sheet():
	frames = []
	cx = CCX
	# idle: heavy breathing
	for (bob, br, fy) in ((0.0, 0.0, 0.0), (-0.6, 0.6, -0.4), (-1.0, 1.0, -0.6), (-0.5, 0.5, -0.3)):
		frames.append(chud_frame(chud_pose(bob=bob, breath=br, F=(cx - 13, CBOT - 6 + fy))))
	# walk: dragging shuffle, arm drags along the ground
	walk = [(0.0, 3.0, 0.0), (-0.8, 1.5, -0.8), (-1.0, -1.0, -1.2), (0.0, -3.0, 0.0), (-0.8, -1.5, -0.8), (-1.0, 1.0, -1.2)]
	for i, (bob, foot, fy) in enumerate(walk):
		sway = math.sin(i / 6.0 * math.tau)
		frames.append(chud_frame(chud_pose(bob=bob, foot=foot, lean=-1.0, F=(cx - 14 + sway * 1.5, CBOT - 5 + fy * 0.3), fr=6.0)))
	# windup: arm raised high, veins and mouth glow, white glint on the fist
	frames.append(chud_frame(chud_pose(lean=1.0, bob=0.5, F=(cx - 11, CBOT - 16), E=(cx - 12, CBOT - 12), glow=0.5, mouth=2)))
	frames.append(chud_frame(chud_pose(lean=2.0, bob=1.0, sag=-1.0, F=(cx - 8, CBOT - 26), E=(cx - 13, CBOT - 21), glow=0.9, mouth=3, flash=1, fr=5.5)))
	frames.append(chud_frame(chud_pose(lean=2.5, bob=1.0, sag=-1.0, F=(cx - 7, CBOT - 27), E=(cx - 12, CBOT - 22), glow=1.0, mouth=3, flash=1, fr=5.5)))
	# slam: fast descent, impact (dust + cracks), hold, recovery
	f13 = chud_frame(chud_pose(lean=-3.0, bob=2.0, F=(cx - 14, CBOT - 14), E=(cx - 12, CBOT - 20), glow=0.8, mouth=2, fr=6.5))
	for ddx in (3, 5, 7):
		polyline(f13, [(cx - 7 + ddx, CBOT - 24 + ddx // 2), (cx - 6 + ddx, CBOT - 19 + ddx // 2)], (222, 214, 190, 255), only_inside=False)
	frames.append(f13)
	f14 = chud_frame(chud_pose(lean=-3.5, bob=2.5, F=(cx - 17, CBOT - 5), E=(cx - 13, CBOT - 12), glow=0.6, mouth=2, fr=7.0, flash=1))
	dust(f14, cx - 17, CBOT, 0)
	frames.append(f14)
	f15 = chud_frame(chud_pose(lean=-3.0, bob=2.0, F=(cx - 17, CBOT - 5), E=(cx - 13, CBOT - 11), glow=0.2, mouth=2, fr=7.0))
	dust(f15, cx - 17, CBOT, 1)
	frames.append(f15)
	f16 = chud_frame(chud_pose(lean=-1.0, bob=0.5, F=(cx - 15, CBOT - 9), E=(cx - 12, CBOT - 13), mouth=1, fr=6.5))
	dust(f16, cx - 17, CBOT, 2)
	frames.append(f16)
	# hit: flesh ripples
	frames.append(chud_frame(chud_pose(lean=2.5, bob=1.5, lump=1.5, squint=True, breath=1.0, F=(cx - 11, CBOT - 6), mouth=2)))
	frames.append(chud_frame(chud_pose(lean=-1.0, bob=-0.5, lump=-1.5, squint=True, breath=-0.5, F=(cx - 14, CBOT - 7), mouth=2)))
	# death: staggers, collapses, liquefies into a heap
	death = [
		dict(lean=2.0, bob=2.5, sag=2.5, F=(cx - 11, CBOT - 4), mouth=3, squint=True, head=(1, 2), melt=0.08),
		dict(lean=3.0, bob=4.0, sag=3.0, F=(cx - 12, CBOT - 3), mouth=2, squint=True, head=(1, 3), melt=0.22),
		dict(lean=2.0, bob=4.0, sag=3.0, F=(cx - 13, CBOT - 3), mouth=1, squint=True, head=(1, 3), melt=0.4),
		dict(lean=1.0, bob=4.0, sag=3.0, F=(cx - 13, CBOT - 3), mouth=1, squint=True, melt=0.58),
		dict(F=(cx - 13, CBOT - 3), squint=True, melt=0.74),
		dict(F=(cx - 13, CBOT - 3), squint=True, melt=0.88),
		dict(F=(cx - 13, CBOT - 3), squint=True, melt=1.0),
	]
	dframes = [chud_frame(chud_pose(**d)) for d in death]
	drips = [((31, 25, 3), (14, 26, 2)), ((32, 27, 3), (13, 28, 2)), ((33, 28, 2), (14, 29, 2)), ((35, 29, 2),), ((12, 31, 1),), (), ()]
	for f, ds in zip(dframes, drips):
		for (x, y, ln) in ds:
			for k in range(ln):
				f.put(x, y + k, FL[3] if k < ln - 1 else FL[4])
	for f, bub in ((dframes[4], ((22, 28), (28, 29))), (dframes[5], ((20, 30), (30, 31))), (dframes[6], ((18, 32), (24, 31), (31, 32)))):
		for (x, y) in bub:
			if f.get(x, y) is not None:
				f.put(x, y, FL[4])
				f.put(x - 1, y, FL[3])
	frames += dframes
	return sheet(frames, 26)


# ================================================================ POSSESSED SKULL
BONE = [(58, 50, 56, 255), (112, 100, 104, 255), (170, 160, 146, 255), (222, 214, 190, 255), (250, 246, 226, 255)]
V_HI = (236, 214, 255, 255)
V_SOCK = (192, 138, 212, 255)
SMOKE_V = [(94, 52, 112), (138, 80, 160), (192, 138, 212)]
DARKV = (30, 16, 40, 255)


def skull_body(jaw=0, dx=0, dy=0, sock=1.0, crack=0, bright=0.0):
	"""Facing left. Skull occupies about x 4..15, y 4..15 of a 20x20 cell (jaw open shifts it down)."""
	ramp = BONE if bright <= 0 else tint_ramp(BONE, V_HI, bright)
	cv = paint(20, 20, [(10 + dx, 8.5 + dy, 6.2, 5.0), (9.0 + dx, 12.0 + dy, 4.8, 2.8)], ramp)
	for (sx, sy, w, h) in ((5, 6, 4, 4), (11, 7, 3, 3)):
		for xx in range(w):
			for yy in range(h):
				if not (xx in (0, w - 1) and yy in (0, h - 1)):
					dot(cv, sx + xx + dx, sy + yy + dy, DARKV)
		glow_c = V_SOCK if sock > 0.5 else CORRUPT[2]
		for xx in range(1, w - 1):
			for yy in range(1, h - 1):
				dot(cv, sx + xx + dx, sy + yy + dy, glow_c)
		dot(cv, sx + 1 + dx, sy + 1 + dy, V_HI if sock > 0.5 else glow_c)
		if sock > 0.5:
			for xx, yy in ((-1, 1), (w, 1), (w // 2, -1)):
				dot(cv, sx + xx + dx, sy + yy + dy, (192, 138, 212, 110))
	dot(cv, 8 + dx, 11 + dy, BONE[0])
	dot(cv, 9 + dx, 11 + dy, BONE[0])
	dot(cv, 9 + dx, 10 + dy, BONE[1])
	dot(cv, 5 + dx, 10 + dy, BONE[1])
	dot(cv, 13 + dx, 10 + dy, BONE[1])
	for xx in range(6, 13):
		dot(cv, xx + dx, 13 + dy, TEETH if (xx % 2 == 0) else BONE[2])
	jaw_c = Canvas(20, 20)
	jy = 14 + jaw
	for yy in range(3):
		half = 3.2 - yy * 0.6
		for xx in range(20):
			if abs(xx + 0.5 - (9.5 + dx)) <= half + 0.5:
				jaw_c.put(xx, jy + yy + dy, BONE[3] if yy == 0 else BONE[2] if yy == 1 else BONE[1])
	for xx in range(7, 12):
		if (xx % 2) == 1 and jaw_c.get(xx + dx, jy + dy) is not None:
			jaw_c.put(xx + dx, jy + dy, DARKV if xx % 4 == 3 else TEETH)
	cv_o = outline(cv, OUTLINE)
	jaw_o = outline(jaw_c, OUTLINE)
	if jaw > 0:
		for yy in range(14, 14 + jaw):
			for xx in range(6, 13):
				if cv_o.get(xx + dx, yy + dy) is None and jaw_c.get(xx + dx, yy + dy) is None:
					cv_o.put(xx + dx, yy + dy, DARKV if 7 <= xx <= 11 else OUTLINE)
	cv_o.blit(jaw_o, 0, 0)
	if crack:
		polyline(cv_o, [(9, 4), (10, 6), (9, 8), (11, 10)], OUTLINE)
		polyline(cv_o, [(9, 4), (8, 6), (7, 7)], OUTLINE)
		if crack > 1:
			polyline(cv_o, [(11, 10), (12, 12), (11, 14)], OUTLINE)
			polyline(cv_o, [(9, 8), (7, 10), (6, 12)], OUTLINE)
	return cv_o


def skull_flame(c, phase, back=1.0):
	"""Spectral flame trailing behind (right, curling up) and flickering up from the crown."""
	for k, (by, ln) in enumerate(((7, 6), (10, 5), (12, 4))):
		length = max(1, int(round(ln * back + math.sin(phase * 1.6 + k * 1.7) * 1.0)))
		for j in range(length):
			x = 14 + j
			yc = by - int(j * (0.6 if k == 0 else 0.25)) + int(round(math.sin(phase * 1.2 + j * 0.8 + k)))
			thick = 3 if j < length - 2 else 2 if j < length - 1 else 1
			for t in range(thick):
				y = yc - thick // 2 + t
				mid = abs(t - (thick - 1) / 2.0) < 0.6
				col = V_HI if (j >= length - 1 and mid) else V_SOCK if mid and j < 3 else CORRUPT[3] if mid else CORRUPT[2] if j < length - 1 else CORRUPT[1]
				c.put(x, y, col)
	for k, bx in enumerate((7, 10, 13)):
		h_ = 2 + int((phase + k) % 2)
		for j in range(h_):
			c.put(bx + int(round(math.sin(phase + k + j) * 0.6)), 4 - j, (CORRUPT[3] if j < h_ - 1 else V_SOCK))


def skull_fly(i):
	c = Canvas(20, 20)
	flame = Canvas(20, 20)
	skull_flame(flame, i * 1.4, 1.0)
	c.blit(flame, 0, 0)
	c.blit(skull_body(dy=(0, -1, 0, 1)[i], jaw=(1 if i == 2 else 0)), 0, 0)
	return c


def smoke_puffs(c, pts, palette_idx, alpha):
	for (x, y, r) in pts:
		col = SMOKE_V[palette_idx]
		for yy in range(int(y - r - 1), int(y + r + 2)):
			for xx in range(int(x - r - 1), int(x + r + 2)):
				d = (xx + 0.5 - x) ** 2 + (yy + 0.5 - y) ** 2
				if d <= r * r and 0 <= xx < 20 and 0 <= yy < 20:
					c.put(xx, yy, col + (alpha if d > r * r * 0.3 else min(255, alpha + 50),))


def skull_spawn(i):
	"""Violet smoke condenses toward the centre and solidifies into the skull."""
	c = Canvas(20, 20)
	ring = [(math.cos(k * math.tau / 7 + 0.4), math.sin(k * math.tau / 7 + 0.4)) for k in range(7)]
	prog = i / 4.0
	dist = 9.0 * (1.0 - prog) + 2.0
	pts = [(10 + x * dist, 10 + y * dist, 2.6 - prog * 0.8 + (k % 2) * 0.6) for k, (x, y) in enumerate(ring)]
	if i == 0:
		smoke_puffs(c, pts, 0, 90)
	elif i in (1, 2):
		smoke_puffs(c, pts, 1, 150)
		smoke_puffs(c, [(10, 9, 4.0)], 0, 110)
	if i >= 1:
		c.blit(fade(skull_body(sock=1.0), (0, 70, 130, 200, 255)[i]), 0, 0)
		if i == 3:
			smoke_puffs(c, [(8, 12, 2.0), (13, 7, 2.0)], 2, 120)
	if i == 4:
		fl = Canvas(20, 20)
		skull_flame(fl, 0.0, 0.6)
		c.blit(fl, 0, 0)
		for (x, y) in ((4, 3), (16, 14), (3, 13)):
			glint(c, x, y, 1, core=V_HI, arm=V_SOCK)
	if i < 4:
		for k in range(5):
			a = k * 1.3 + i
			rr = 8.5 - i * 2.0
			c.put(int(10 + math.cos(a) * rr), int(10 + math.sin(a) * rr), V_HI if k % 2 else V_SOCK)
	return c


def skull_despawn(i):
	"""Skull erodes pixel by pixel (jaw first) and drifts upward as dark grey-violet smoke."""
	c = Canvas(20, 20)
	sk = skull_body(sock=0.3 if i >= 2 else 1.0)
	keep = (0.88, 0.62, 0.38, 0.16, 0.0)[i]
	eroded = Canvas(20, 20)
	for y in range(20):
		for x in range(20):
			p = sk.get(x, y)
			if p is None:
				continue
			bayer = ((x * 5 + y * 3) % 7) / 7.0 + ((x + y * 2) % 3) / 12.0
			bias = (y - 4) / 12.0 * 0.45
			if bayer + bias * (0.4 + i * 0.25) < keep + 0.1:
				eroded.put(x, y, p)
	c.blit(fade(eroded, (255, 235, 200, 150, 100)[i]), 0, 0)
	for y in range(20):
		for x in range(20):
			if sk.get(x, y) is not None and eroded.get(x, y) is None:
				ny = y - 2 - i * 2 - ((x * 3) % 3)
				nx = x + ((x + y) % 3 - 1) * (1 + i // 2)
				if 0 <= nx < 20 and 0 <= ny < 20 and (x + y + i) % 2 == 0:
					c.put(nx, ny, SMOKE_V[0 if i >= 2 else 1] + ((190, 170, 140, 110, 70)[i] if (x + y) % 3 else 110,))
	if i >= 1:
		smoke_puffs(c, [(9 + (i % 2), 6 - i, 2.0 + i * 0.5), (12, 9 - i * 1.5, 1.6 + i * 0.4)], 0, (0, 120, 110, 90, 60)[i])
	if i <= 1:
		fl = Canvas(20, 20)
		skull_flame(fl, 0.0, 0.8 - i * 0.4)
		c.blit(fl, 0, 0)
	return c


def skull_death(i):
	"""Skull shatters: white-violet flash + cracks, then bone shards fly outward."""
	c = Canvas(20, 20)
	if i == 0:
		c.blit(skull_body(crack=2, bright=0.55, sock=1.0), 0, 0)
		for (x, y) in ((3, 4), (16, 5), (10, 17)):
			glint(c, x, y, 2, core=WHITE, arm=V_HI)
		return c
	flash_r = (0, 8.0, 8.5, 5.5, 0, 0)[i]
	if flash_r:
		for y in range(20):
			for x in range(20):
				d = math.hypot(x + 0.5 - 10, y + 0.5 - 9.5)
				if d <= flash_r:
					a = int(210 * (1 - d / flash_r) ** 0.9) if i == 1 else int(120 * (1 - d / flash_r))
					col = V_HI if d < flash_r * 0.35 else V_SOCK if d < flash_r * 0.65 else CORRUPT[3]
					if i == 1 and d < flash_r * 0.22:
						col = WHITE
					c.put(x, y, col[:3] + (max(40, a),))
		for k in range(8):
			a = k * math.tau / 8 + 0.3
			for t in range(int(flash_r * 0.5), int(flash_r)):
				if k % 2 == 0 or t > flash_r * 0.7:
					c.put(int(10 + math.cos(a) * t), int(9.5 + math.sin(a) * t), (255, 255, 255, 230) if i == 1 else V_HI)
	shards = [(0.2, 1.0, 3, 3), (1.1, 0.9, 3, 2), (2.0, 1.1, 3, 3), (2.9, 0.95, 2, 3), (3.8, 1.0, 3, 2), (4.6, 1.15, 2, 3), (5.5, 0.9, 3, 3), (0.7, 0.6, 2, 4), (3.4, 0.55, 2, 4)]
	for k, (a, sp, sz, tone) in enumerate(shards):
		r = sp * (1.2 + i * 2.1)
		x = 10 + math.cos(a) * r - sz / 2.0
		y = 9.5 + math.sin(a) * r * 0.9 - sz / 2.0 + (0.35 * i * i if i > 2 else 0)
		if i >= 5 and k % 2:
			continue
		sz2 = sz if i < 4 else max(1, sz - 1)
		for ox in range(sz2):
			for oy in range(sz2):
				col = BONE[tone] if (ox, oy) != (0, 0) else BONE[4]
				if ox + oy == 2 * (sz2 - 1) and sz2 > 1:
					col = BONE[1]
				c.put(int(x) + ox, int(y) + oy, col)
	if i >= 2:
		for k in range(6):
			a = k * 1.05 + 0.2
			r = 3 + i * 2.2 + (k % 2)
			c.put(int(10 + math.cos(a) * r), int(9.5 + math.sin(a) * r), V_HI if k % 2 == 0 and i < 5 else CORRUPT[3])
	return c


def skull_bite(i):
	c = Canvas(20, 20)
	fl = Canvas(20, 20)
	skull_flame(fl, i + 2.0, 1.0 if i != 1 else 1.4)
	c.blit(fl, 0, 0)
	if i == 0:
		c.blit(skull_body(jaw=3, dx=0, dy=-1), 0, 0)
	elif i == 1:
		c.blit(skull_body(jaw=0, dx=-1, dy=0, bright=0.15), 0, 0)
		glint(c, 3, 13, 1, core=WHITE, arm=V_HI)
	else:
		c.blit(skull_body(jaw=1), 0, 0)
	return c


def skull_sheet():
	frames = [skull_fly(i) for i in range(4)]
	frames += [skull_spawn(i) for i in range(5)]
	frames += [skull_despawn(i) for i in range(5)]
	frames += [skull_death(i) for i in range(6)]
	frames += [skull_bite(i) for i in range(3)]
	return sheet(frames, len(frames))


# ===================================================================== OUTPUT
SPECS = [
	# name, builder, cell_w, cell_h, frames, preview columns
	("enemy_slime_red.png", red_slime_sheet, 24, 24, 14, 7),
	("vfx_slime_splash_red.png", red_splash, 40, 24, 6, 6),
	("vfx_slime_hit_red.png", red_hit, 16, 16, 4, 4),
	("bloated_slime.png", bloated_sheet, 40, 32, 20, 8),
	("vfx_bloated_burst.png", bloated_burst, 64, 32, 6, 3),
	("chud_blob.png", chud_sheet, 48, 36, 26, 7),
	("possessed_skull.png", skull_sheet, 20, 20, 23, 12),
]


def split(cv, cw, ch, n):
	frames = []
	for i in range(n):
		f = Canvas(cw, ch)
		for y in range(ch):
			for x in range(cw):
				f.px[y * cw + x] = cv.px[y * cv.w + i * cw + x]
		frames.append(f)
	return frames


def preview(cv, cw, ch, n, path, cols):
	frames = split(cv, cw, ch, n)
	rows = (n + cols - 1) // cols
	pad = 1
	sh = Canvas(cols * (cw + pad), rows * (ch + pad))
	for i, f in enumerate(frames):
		ox, oy = (i % cols) * (cw + pad), (i // cols) * (ch + pad)
		sh.blit(f, ox, oy)
		for y in range(ch):
			if sh.get(ox + cw, oy + y) is None:
				sh.put(ox + cw, oy + y, (70, 76, 90, 255))
		for x in range(cw):
			if sh.get(ox + x, oy + ch) is None:
				sh.put(ox + x, oy + ch, (70, 76, 90, 255))
	flat = Canvas(sh.w, sh.h)
	flat.rect(0, 0, sh.w, sh.h, GREY_BG)
	flat.blit(sh, 0, 0)
	save_png(flat, path, scale=4)


def check(sheets):
	ok = True
	ground = {"enemy_slime_red.png": (10, 8), "bloated_slime.png": (14, 12), "chud_blob.png": (19, 17)}
	for name, cv, cw, ch, n in sheets:
		good = cv.w == cw * n and cv.h == ch
		print("%-28s %4dx%-3d expected %4dx%-3d %s" % (name, cv.w, cv.h, cw * n, ch, "OK" if good else "FAIL"))
		ok &= good
		if name in ground:
			death_start, centre_end = ground[name]
			for i, f in enumerate(split(cv, cw, ch, n)):
				bb = f.bbox()
				if bb is None:
					print("  frame %d EMPTY" % i)
					ok = False
					continue
				cxm = (bb[0] + bb[2]) / 2.0
				flag = ""
				if i < death_start and bb[3] != ch:
					flag = " LOWEST ROW != last"
					ok = False
				if i < centre_end and name != "chud_blob.png" and abs(cxm - cw / 2.0) > 2:
					flag += " CENTRE OFF %.1f" % cxm
					ok = False
				print("  f%02d bbox=%s w=%d h=%d cx=%.1f%s" % (i, bb, bb[2] - bb[0], bb[3] - bb[1], cxm, flag))
	return ok


def main():
	pdir = None
	if "--preview" in sys.argv:
		pdir = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(pdir, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	sheets = []
	for name, builder, cw, ch, n, cols in SPECS:
		cv = builder()
		save_png(cv, os.path.join(OUT, name))
		sheets.append((name, cv, cw, ch, n))
		print("wrote", os.path.join(OUT, name), cv.w, cv.h)
		if pdir:
			preview(cv, cw, ch, n, os.path.join(pdir, name.replace(".png", "_x4.png")), cols)
	ok = check(sheets)
	print("CHECK", "OK" if ok else "FAILED")
	return 0 if ok else 1


if __name__ == "__main__":
	sys.exit(main())

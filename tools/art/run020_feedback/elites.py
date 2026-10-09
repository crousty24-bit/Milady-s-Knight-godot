"""RUN-020 reprise: redrawn Bloated Slime and Chud Blob (native pixel density, no upscaling).

Usage: python3 tools/art/run020_feedback/elites.py [--preview DIR] [--log FILE]

Outputs (NEW files, RUN-019 originals untouched), assets/run020_feedback/enemies/:
  bloated_slime.png      1440x56   20 x 72x56   crawl 0-7, swell 8-11, hit 12-13, death 14-19
  vfx_bloated_burst.png   672x48    6 x 112x48  bottom = ground, centre x=56
  chud_blob.png          2496x64   26 x 96x64   idle 0-3, walk 4-9, windup 10-12, slam 13-16, hit 17-18, death 19-25
Ground enemies face LEFT, feet on the last row, body centred on cell_w/2 (pivot = bottom-centre).
Deterministic, procedural, original art; reuses only helpers/palettes from tools/art (read-only).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "run019"))
from pixel import Canvas, outline, save_png, sheet  # noqa: E402
from palette import BLOOD, CORRUPT, EMBER, OUTLINE, STEEL, WOOD  # noqa: E402
import enemies_blobs as EB  # noqa: E402  (read-only reuse of helpers/palettes)
from enemies_blobs import paint, dot, limb, polyline, glint, disc, tint_ramp, mix, fade  # noqa: E402
from enemies_blobs import BL, BL_VEIN, PUS, PUS_HI, PUS_SH, FL, RAW, RAW_DK, TEETH, BONE, PALE, WHITE, GREY_BG  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "run020_feedback", "enemies")

# ================================================================ BLOATED SLIME
BW, BH = 72, 56
BCX = 36.0
BBOT = BH - 1  # feet row
SCLERA = (226, 222, 150, 255)
RIM = BLOOD[0]


def bshapes(w, h, lean=0.0, wob=0.0):
	cx = BCX
	bot = BBOT + 0.5
	return [
		(cx, bot - h * 0.37, w * 0.5, h * 0.42),                       # wide base mass
		(cx - w * 0.07 + lean, bot - h * 0.63 + wob * 0.3, w * 0.36, h * 0.37),  # swollen dome
		(cx + w * 0.28, bot - h * 0.36 + wob, w * 0.22, h * 0.30),     # right belly bulge
		(cx - w * 0.34, bot - h * 0.2, w * 0.17, h * 0.2),             # low left sag
		(cx + w * 0.1 - lean * 0.4, bot - h * 0.86, w * 0.17, h * 0.16),  # crown lump
		(cx - w * 0.3 + lean * 0.5, bot - h * 0.58, w * 0.17, h * 0.2),   # brow lump
		(cx + w * 0.43, bot - h * 0.14, w * 0.1, h * 0.13),            # right foot-blob
	]


def bpustule(cv, x, y, r, glow=0.0, popped=False):
	rim = RIM if glow < 0.5 else BLOOD[3]
	fill = PUS if glow < 0.5 else (255, 214, 140, 255)
	if popped:
		for yy in range(-r, r + 1):
			for xx in range(-r, r + 1):
				d = xx * xx + yy * yy
				if d <= r * r:
					dot(cv, x + xx, y + yy, rim if d > (r - 1) ** 2 else (BLOOD[1] if glow < 0.5 else BLOOD[3]))
		dot(cv, x, y + 1, PUS_SH)
		dot(cv, x - 1, y - r, BL[3])
		return
	for yy in range(-r, r + 1):
		for xx in range(-r, r + 1):
			d = xx * xx + yy * yy
			if d <= r * r + 1:
				edge = d > (r - 1) ** 2 + 1
				dot(cv, x + xx, y + yy, rim if edge else (PUS_SH if (xx + yy > r - 1 and d > (r - 2) ** 2) else fill))
	dot(cv, x - r // 2, y - r // 2, PUS_HI)
	dot(cv, x - r // 2 + 1, y - r // 2, PUS_HI)
	dot(cv, x - r // 2, y - r // 2 + 1, PUS_HI)
	if r >= 4:
		dot(cv, x + 1, y + 1, PUS_SH)


# fractional positions (x of w, y of h) and radius; some popped craters
BPUS = [(-0.12, 0.86, 4, 0), (0.36, 0.7, 3, 0), (0.0, 0.3, 5, 0), (-0.42, 0.2, 3, 0), (0.42, 0.24, 3, 1), (0.2, 0.42, 4, 0),
	(-0.24, 0.74, 3, 1), (0.38, 0.5, 2, 0), (-0.14, 0.14, 2, 0), (0.06, 0.88, 3, 0)]


def bcrust(body, w, h, ramp):
	"""Scabby dark patches and crusty ridge on the swollen hide (inside only)."""
	cx, bot = BCX, BBOT
	for (fx, fy, n) in ((-0.1, 0.62, 3), (0.3, 0.42, 4), (-0.4, 0.45, 2), (0.0, 0.1, 4), (0.42, 0.18, 2)):
		for k in range(n):
			dot(body, int(cx + fx * w + k * 2), int(bot - fy * h + (k % 2)), BL[0] if k % 2 == 0 else BL[1])


def bskull(body, w, h):
	"""Half-digested skull swallowed into the upper right of the mass."""
	cx, bot = BCX, BBOT
	sx, sy = int(cx + w * 0.17), int(bot - h * 0.66)
	for yy in range(-5, 6):
		for xx in range(-5, 6):
			d = xx * xx + yy * yy
			if d <= 26 and not (yy > 3 and abs(xx) > 3):
				dot(body, sx + xx, sy + yy, OUTLINE if d > 22 else BONE[1] if d > 16 else BONE[2] if (xx + yy) > 0 else BONE[3])
	for xx, yy in ((-3, -1), (-2, -1), (-3, 0), (-2, 0), (2, -1), (3, -1), (2, 0), (3, 0), (0, 1)):
		dot(body, sx + xx, sy + yy, OUTLINE)
	for xx in (-2, 0, 2):
		dot(body, sx + xx, sy + 4, OUTLINE)


def bloated_frame(w, h, lean=0.0, wob=0.0, mode="normal", glow=0.0, ripple=None, pop=0.0, skull=True):
	ramp = BL if glow <= 0 else tint_ramp(BL, EMBER[1], 0.22 * glow)
	cx, bot = BCX, BBOT
	body = paint(BW, BH, bshapes(w, h, lean, wob), ramp, clip_y=BBOT)
	bcrust(body, w, h, ramp)
	vc = BL_VEIN if glow < 0.4 else (BLOOD[3] if glow < 0.8 else EMBER[2])
	vseg = [[(cx - w * .34, bot - h * .62), (cx - w * .2, bot - h * .5), (cx - w * .14, bot - h * .3), (cx - w * .2, bot - h * .14)],
		[(cx + w * .06, bot - h * .94), (cx + w * .14, bot - h * .74), (cx + w * .3, bot - h * .62), (cx + w * .36, bot - h * .44), (cx + w * .33, bot - h * .26)],
		[(cx - w * .02, bot - h * .3), (cx + w * .1, bot - h * .2), (cx + w * .2, bot - h * .12)],
		[(cx + w * .2, bot - h * .9), (cx + w * .1, bot - h * .8)]]
	for seg in vseg:
		polyline(body, [(int(x), int(y)) for x, y in seg], vc)
	if glow >= 0.8:
		for seg in vseg[:2]:
			polyline(body, [(int(x) + 1, int(y)) for x, y in seg], BLOOD[3])
	if skull and mode != "dead":
		bskull(body, w, h)
	for k, (rx, ry, r, popped) in enumerate(BPUS):
		px = int(round(cx + rx * w))
		py = int(round(bot - ry * h))
		rr = r + (1 if (glow > 0.5 and r < 5) else 0)
		if pop > 0 and k % 2 == 0:
			rr = max(rr, 4)
		bpustule(body, px, py, min(5, rr), glow, bool(popped) and glow < 0.5 and pop == 0)
	# face: one huge dull eye, one small, heavy brow, wide lopsided maw of broken fangs
	ex = int(round(cx - w * 0.38))
	ey = int(round(bot - h * 0.58))
	if mode == "hit":
		for dx in range(10):
			dot(body, ex + dx, ey + 2, OUTLINE)
		for dx in range(6):
			dot(body, ex + 14 + dx, ey + 1, OUTLINE)
	elif mode == "dead":
		for (ox, oy) in ((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (4, 0), (3, 1), (1, 3), (0, 4)):
			dot(body, ex + 2 + ox, ey + oy - 2, OUTLINE)
		for (ox, oy) in ((0, 0), (1, 1), (2, 2), (2, 0), (0, 2)):
			dot(body, ex + 15 + ox, ey + oy, OUTLINE)
	else:
		for dy in range(10):
			for dx in range(10):
				if (dx - 4.5) ** 2 + (dy - 4.5) ** 2 <= 19.5:
					dot(body, ex + dx, ey + dy - 4, SCLERA)
		for (ox, oy) in ((1, 0), (7, 4), (8, 2), (2, 7)):
			dot(body, ex + ox, ey + oy - 3, BLOOD[2])
		for dx in range(3, 7):
			for dy in range(4):
				dot(body, ex + dx, ey + dy - 1, BLOOD[2] if glow > 0 else OUTLINE)
		dot(body, ex + 3, ey - 1, WHITE)
		for dx in range(-1, 11):  # heavy drooping lid
			dot(body, ex + dx, ey - 4 + (1 if dx in (-1, 10) else 0) + (1 if dx in (0, 9) else 0), OUTLINE)
		for dx in range(0, 10):
			if dx < 4 or dx > 5:
				dot(body, ex + dx, ey - 3 + (1 if dx in (0, 9) else 0), OUTLINE)
		for dy in range(6):
			for dx in range(6):
				if (dx - 2.5) ** 2 + (dy - 2.5) ** 2 <= 7.5:
					dot(body, ex + 15 + dx, ey + dy - 2, SCLERA)
		for dx in range(2):
			for dy in range(2):
				dot(body, ex + 16 + dx, ey + 1 + dy, OUTLINE)
		for dx in range(14, 22):  # slanted brow over the small eye
			dot(body, ex + dx, ey - 3 + (dx - 14) // 3, OUTLINE)
	my = int(round(bot - h * 0.2))
	mx = int(round(cx - w * 0.33))
	mw = 20
	open_m = 3 + (2 if glow > 0.3 else 0)
	for dx in range(mw):
		dot(body, mx + dx, my + (1 if dx < 2 or dx > mw - 3 else 0), OUTLINE)
		dot(body, mx + dx, my - 1 + (dx % 2) if dx in (0, mw - 1) else my, OUTLINE)
	for dy in range(open_m):
		for dx in range(1, mw - 1):
			dot(body, mx + dx, my + 1 + dy, BLOOD[0] if glow < 0.5 else BLOOD[3])
	for dx in range(2, mw - 3, 4):  # broken fangs down from the top lip, stumps up from below
		for k in range(3 if dx % 8 == 2 else 2):
			dot(body, mx + dx, my + 1 + k, PUS_HI if k < 2 else PUS)
			dot(body, mx + dx + 1, my + 1 + k, PUS if k < 2 else PUS_SH)
	for dx in range(4, mw - 3, 6):
		dot(body, mx + dx, my + open_m, PUS)
		dot(body, mx + dx + 1, my + open_m, PUS_SH)
	for dy in range(1, 6):  # drool strand
		dot(body, mx + 5, my + 1 + open_m + dy - 1, PUS)
	dot(body, mx + 5, my + 5 + open_m, PUS_HI)
	if ripple is not None:
		rcx, rcy, rr = ripple
		for k in range(60):
			a = k / 60.0 * math.tau
			x = int(round(rcx + math.cos(a) * rr))
			y = int(round(rcy + math.sin(a) * rr * 0.75))
			if k % 3:
				dot(body, x, y, ramp[4] if (x + y) % 2 == 0 else ramp[3])
	gx, gy = int(round(cx - w * 0.2 + lean)) - 2, int(round(bot - h * 0.9))
	for ddx, ddy, t in ((0, 0, 4), (1, 0, 4), (2, 0, 4), (0, 1, 4), (1, 1, 3), (3, 0, 3), (0, 2, 3), (0, 3, 3)):
		dot(body, gx + ddx, gy + ddy, ramp[t])
	out = outline(body, OUTLINE)
	if glow >= 0.6:
		glint(out, int(cx - w * 0.2 + lean) - 3, int(bot - h * 0.9) - 3, 4 if glow > 0.9 else 3)
		for ddx, ddy in ((14, -8), (-18, -4), (22, 6)):
			sx, sy = int(cx + ddx * w / 40), int(bot - h * 0.55 + ddy)
			out.put(sx, sy, EMBER[3])
			out.put(sx, sy - 1, EMBER[2])
	return out


def goo_puddle(rx, ht, ramp, drops=(), bubbles=0, cxp=BCX):
	c = Canvas(BW, BH)
	for r in range(ht):
		t = (r + 0.5) / ht
		half = rx * (1.0 - t ** 2.0) ** 0.5
		half += 0.6 * math.sin(r * 1.3 + rx)
		for x in range(BW):
			if abs(x + 0.5 - cxp) <= half:
				tone = 1 if r == 0 and (x + 0.5 < cxp - half + 3 or x + 0.5 > cxp + half - 3) else 2 if r < ht - 1 or ht == 1 else 3
				if x + 0.5 < cxp - half * 0.3 and r > 0:
					tone = 3
				c.put(x, BBOT - r, ramp[tone])
	xs = [x for x in range(BW) if c.get(x, BBOT) is not None]
	if xs:
		for k in range(4):
			c.put(xs[0] + 3 + k, BBOT - min(ht - 1, 1), ramp[4])
	for k in range(bubbles):
		bx = int(cxp - 12 + k * 10)
		by = BBOT - max(0, ht - 1)
		if c.get(bx, by) is not None:
			bpustule(c, bx, by, 2)
	for (dx, dy, sz, col) in drops:
		for ox in range(sz):
			for oy in range(sz):
				c.put(int(cxp + dx) + ox, int(BBOT - dy) + oy, col if (ox, oy) != (0, 0) else PUS_HI if sz >= 2 else col)
	return outline(c, OUTLINE)


def bloated_sheet():
	frames = []
	# crawl: heavy squash/stretch loop, feet row fixed. (w, h, lean, wob)
	crawl = [(48, 46, 0.0, 0.0), (50, 44, 0.8, 0.8), (52, 43, 1.4, 1.4), (46, 48, -1.8, 0.5),
		(45, 49, -2.6, -0.5), (50, 44, -1.0, -1.0), (49, 45, -0.3, -0.4), (47, 47, 0.5, 0.4)]
	for (w, h, lean, wob) in crawl:
		frames.append(bloated_frame(w, h, lean, wob))
	for w, h, g in ((52, 47, 0.35), (55, 49, 0.65), (58, 52, 1.0), (57, 50, 0.9)):
		frames.append(bloated_frame(w, h, 0.0, 0.0, glow=g))
	frames.append(bloated_frame(54, 43, 1.2, 1.2, mode="hit", ripple=(42, 36, 9)))
	frames.append(bloated_frame(47, 48, -1.2, -0.8, mode="hit", ripple=(36, 32, 17)))
	f14 = bloated_frame(58, 52, 0.0, 0.0, mode="dead", glow=1.0, pop=1.0)
	for pts in (((34, 14), (37, 20), (34, 27), (37, 34)), ((46, 18), (43, 25), (46, 32), (43, 38))):
		polyline(f14, pts, PALE)
	frames.append(f14)
	f15 = bloated_frame(52, 22, 0.0, 0.0, mode="dead", glow=0.6, skull=False)
	for (x, y, s, c) in ((6, 22, 4, PUS), (14, 12, 3, PUS_HI), (56, 20, 4, PUS), (62, 28, 3, BL[3]), (34, 8, 3, PUS_HI), (46, 10, 3, BL[3]), (4, 36, 3, BL[3]), (66, 40, 3, PUS)):
		for ox in range(s):
			for oy in range(s):
				f15.put(x + ox, y + oy, c if (ox, oy) != (0, 0) else PUS_HI)
	frames.append(f15)
	frames.append(goo_puddle(27.0, 10, BL, ((-24, 14, 4, PUS), (-17, 10, 3, BL[3]), (20, 14, 4, PUS), (25, 9, 3, BL[3]), (-6, 16, 3, PUS_HI), (6, 18, 3, BL[3])), 2))
	frames.append(goo_puddle(29.0, 6, BL, ((-26, 8, 3, PUS), (23, 6, 3, PUS), (-9, 12, 2, BL[3])), 3))
	frames.append(goo_puddle(28.0, 4, BL, ((26, 4, 2, PUS),), 3))
	frames.append(goo_puddle(25.0, 2, BL, (), 2))
	return sheet(frames, 20)


def bloated_burst():
	"""6 frames 112x48: gerbe of droplets + corrupt gas, bigger than RUN-019. Ground = bottom, centre x=56."""
	W, H, CX = 112, 48, 56
	frames = []
	gas = [(176, 196, 104), (146, 166, 92), (118, 134, 86)]
	drops = [(-1.0, -2.2, 4), (1.1, -2.0, 4), (-2.0, -1.5, 3), (2.2, -1.6, 3), (-0.3, -2.7, 3), (0.6, -2.4, 4), (-3.0, -1.0, 3), (3.1, -1.1, 3),
		(-1.6, -1.9, 3), (1.8, -1.8, 3), (-3.8, -0.6, 2), (3.9, -0.7, 2), (-4.6, -0.5, 2), (4.7, -0.6, 2)]
	for i in range(6):
		c = Canvas(W, H)
		for k, (gx, gy, gr) in enumerate(((-15, 3, 8), (14, 4, 8), (0, 9, 10), (-25, 0, 5), (25, 1, 5))):
			r = gr + i * 1.5 - (1.5 if i == 5 else 0)
			cxg = CX + gx * (1 + 0.15 * i)
			cyg = 42 - gy - i * 3.0 - (k % 2) * 2.0
			col = gas[min(2, i // 2)]
			alpha = (210, 190, 165, 130, 95, 60)[i]
			for yy in range(int(cyg - r), int(cyg + r) + 1):
				for xx in range(int(cxg - r), int(cxg + r) + 1):
					d = (xx - cxg) ** 2 + (yy - cyg) ** 2
					if d <= r * r and (d < r * r * 0.7 or (xx + yy) % 2 == 0):
						c.put(xx, yy, col + (alpha if d > r * r * 0.35 else min(255, alpha + 40),))
		half = (8, 15, 22, 24, 19, 12)[i]
		ht = (6, 5, 4, 3, 2, 1)[i]
		for hh in range(ht):
			for x in range(CX - half, CX + half):
				edge = x in (CX - half, CX + half - 1)
				c.put(x, H - 1 - hh, BL[1] if edge else BL[2] if hh < ht - 1 else BL[3])
		for x in (CX - half, CX + half - 1):
			c.put(x, H - 1, OUTLINE)
		if i in (1, 2, 3):
			c.put(CX - half // 2, H - 2 if ht > 1 else H - 1, PUS_HI)
		t = (i + 1) * 0.9
		if i == 0:
			for x in range(CX - 10, CX + 10):
				for y in range(26, 44):
					if ((x - CX) / 10.0) ** 2 + ((y - 40) / 12.0) ** 2 <= 1.0:
						c.put(x, y, PUS_HI if x - CX < -2 and y < 36 else PUS if y < 38 else BL[3])
		for k, (vx, vy, sz) in enumerate(drops):
			x = CX + vx * t * 6.2
			y = 42 + vy * t * 6.6 + 2.6 * t * t
			if y > H - 4 or (i == 5 and sz >= 3) or (i == 4 and sz == 4 and k % 2):
				continue
			xi, yi = int(x), int(y)
			for ox in range(sz):
				for oy in range(sz):
					c.put(xi + ox, yi + oy, PUS_HI if (ox, oy) == (0, 0) and sz > 1 else PUS if oy == 0 else BL[3] if oy == 1 else BL[2])
			if i in (1, 2) and sz >= 3:
				c.put(xi + 1, yi - 1, PUS_SH)
		frames.append(c)
	return sheet(frames, 6)


# ==================================================================== CHUD BLOB
CW, CH = 96, 64
CBOT = CH - 1
CCX = 48
IRON = [STEEL[0], STEEL[1], STEEL[2], STEEL[3], STEEL[4]]
VIOLET = CORRUPT


def cleaver(cv, F, ang, ln=21, bw=12, hot=0.0, edge_left=True):
	"""Crude rusted slab cleaver gripped at F, pointing along ang (degrees, screen coords)."""
	a = math.radians(ang)
	d = (math.cos(a), math.sin(a))
	n = (-d[1], d[0])
	layer = Canvas(cv.w, cv.h)
	hw = bw / 2.0
	edge_sign = -1 if n[0] > 0 else 1
	if not edge_left:
		edge_sign = -edge_sign
	for y in range(int(F[1] - ln - 4), int(F[1] + ln + 5)):
		for x in range(int(F[0] - ln - 4), int(F[0] + ln + 5)):
			px, py = x + 0.5 - F[0], y + 0.5 - F[1]
			t = px * d[0] + py * d[1]
			s = (px * n[0] + py * n[1]) * edge_sign  # +s = cutting-edge side
			if -5 <= t < 4 and abs(s) <= 1.2:
				layer.put(x, y, WOOD[1] if (int(t) + 5) % 3 else WOOD[3])
			elif 4 <= t <= ln and -hw <= s <= hw:
				if t > ln - 3 and s > hw - (t - (ln - 3)) * 1.5:
					continue  # clipped leading corner
				if s >= hw - 1.6:
					col = PALE if hot > 0.5 else IRON[4]
				elif s <= -hw + 1.6:
					col = IRON[0]
				elif ((x * 7 + y * 13) % 11 == 0) or (s < -hw * 0.2 and (x + 2 * y) % 5 == 0):
					col = RAW_DK
				else:
					col = IRON[2] if s > 0 else IRON[1]
				if hot > 0 and s >= hw - 3.0:
					col = mix(col, EMBER[2], 0.45 * hot)
				layer.put(x, y, col)
	# bolt-hole near the spine
	hx, hy = F[0] + d[0] * 11 - n[0] * edge_sign * (hw - 3.2), F[1] + d[1] * 11 - n[1] * edge_sign * (hw - 3.2)
	layer.put(int(hx), int(hy), OUTLINE)
	hx2, hy2 = F[0] + d[0] * 17 - n[0] * edge_sign * (hw - 3.2), F[1] + d[1] * 17 - n[1] * edge_sign * (hw - 3.2)
	layer.put(int(hx2), int(hy2), OUTLINE)
	return outline(layer, OUTLINE)


def chud_pose(**kw):
	p = dict(bob=0.0, lean=0.0, breath=0.0, foot=0.0, F=(CCX - 18, CBOT - 14), E=None, glow=0.0, mouth=1, head=(0.0, 0.0),
		squint=False, sag=0.0, melt=0.0, lump=0.0, flash=0.0, wa=130.0, wl=20, hot=0.0, B=(CCX + 16, CBOT - 13), nw=False, crouch=0.0,
		hump=0.0)
	p.update(kw)
	return p


def chud_frame(p):
	glow = p["glow"]
	ramp = FL if glow <= 0 else tint_ramp(FL, BLOOD[3], 0.16 * glow)
	dark = tint_ramp(FL, OUTLINE, 0.35)
	bob, lean, br, m = p["bob"], p["lean"], p["breath"], p["melt"]
	cr = p["crouch"]
	cx = CCX
	bot = CBOT + 0.5
	out = Canvas(CW, CH)

	def E(x, cy, rx, ry):
		return (x, bot - (bot - cy) * (1 - 0.8 * m), rx * (1 + 0.6 * m), ry * (1 - 0.6 * m))

	up = bob - p["sag"] - cr
	# ---- far (back) arm, darker, behind everything
	B = p["B"]
	bs = (cx + 9 + lean * 0.5, bot - 28 + up * 0.6)
	if m > 0:
		B = (B[0] + 4 * m, bot - 4 - (bot - 4 - B[1]) * (1 - m))
		bs = (bs[0], bot - (bot - bs[1]) * (1 - 0.8 * m))
	be = ((bs[0] + B[0]) / 2 + 3, (bs[1] + B[1]) / 2)
	cells = []
	limb(cells, bs, be, 4.6, 4.2)
	limb(cells, be, B, 4.2, 3.9)
	cells.append((B[0], B[1], 5.0, 4.8 - 1.8 * m))
	back_arm = paint(CW, CH, cells, dark, clip_y=CBOT)
	out.blit(outline(back_arm, OUTLINE), 0, 0)
	# ---- legs and body
	lm = p["lump"]
	legs = [E(cx - 7 + p["foot"] * 0.7, bot - 7, 6, 8), E(cx + 8 - p["foot"] * 0.7, bot - 7, 6, 8),
		E(cx - 9 + p["foot"], bot - 2.6, 7.5, 3.2), E(cx + 10 - p["foot"], bot - 2.6, 7.5, 3.2)]
	torso = [
		E(cx + 1 + lean * 0.3, bot - 16 - cr * 0.5, 14 + br * 0.5, 10),                       # heavy belly / hips
		E(cx + 3 + lean * 0.7 + lm, bot - 26 + up, 14.5 + br * 0.6, 11),                       # barrel chest
		E(cx + 9 + lean * 0.8, bot - 30 + up + p["hump"], 9.5, 9.5),                           # hunched back hump
		E(cx - 8 + lean * 0.8, bot - 29 + up, 8, 7),                                           # front shoulder mass
		E(cx + 10 + lm, bot - 13, 6, 6), E(cx - 9 - lm, bot - 15, 5, 5),                       # hip lumps
	]
	body = paint(CW, CH, legs + torso, ramp, clip_y=CBOT)
	if m < 0.9:
		def Y(y):
			return int(bot - (bot - y) * (1 - 0.8 * m))
		# raw wounds, exposed ribs, stitches, belt
		for (px, py, r) in ((cx + 6, bot - 14 + up * 0.4, 3), (cx - 3, bot - 8, 2), (cx + 13, bot - 21 + up * 0.7, 2), (cx + 1, bot - 30 + up, 2)):
			for ddx in range(-r, r + 1):
				for ddy in range(-r, r + 1):
					if ddx * ddx + ddy * ddy <= r * r + 1:
						dot(body, int(px) + ddx, Y(py) + ddy, RAW if ddx <= 0 and ddy <= 0 else RAW_DK)
		for k in range(4):  # ribs
			rx0 = cx + 1 + lean * 0.6
			ry = bot - 27 + up + k * 3
			polyline(body, [(int(rx0), Y(ry)), (int(rx0 + 4), Y(ry + 1)), (int(rx0 + 8), Y(ry))], TEETH if k % 2 == 0 else BONE[2])
		for k in range(5):  # stitches down the belly
			dot(body, int(cx - 1 + (k % 2)), Y(bot - 21 + k * 2.2 + up * 0.3), OUTLINE)
			dot(body, int(cx - 3 + (k % 2) * 4), Y(bot - 21 + k * 2.2 + up * 0.3), OUTLINE)
		for xx in range(int(cx - 14), int(cx + 17)):  # tattered belt with a rag skirt
			yy = Y(bot - 17 + (xx - cx) * 0.06)
			dot(body, xx, yy, WOOD[1])
			dot(body, xx, yy + 1, WOOD[0])
		for xx in (cx - 9, cx - 3, cx + 5, cx + 11):
			for k in range(4):
				dot(body, int(xx), Y(bot - 16) + k, WOOD[1] if k < 3 else WOOD[0])
		dot(body, int(cx - 1), Y(bot - 17), TEETH)
		dot(body, int(cx), Y(bot - 17), TEETH)
		if m < 0.5:  # cracks
			polyline(body, [(cx - 4, Y(bot - 14)), (cx - 1, Y(bot - 10)), (cx - 3, Y(bot - 5))], ramp[0])
	if glow > 0:
		vc = BLOOD[3] if glow < 0.8 else EMBER[2]
		for seg in (((cx + 12, bot - 38), (cx + 9, bot - 30), (cx + 13, bot - 21), (cx + 10, bot - 12)),
			((cx - 2, bot - 30), (cx + 2, bot - 24), (cx - 1, bot - 17)),
			((cx + 17, bot - 26), (cx + 19, bot - 18)), ((cx - 8, bot - 14), (cx - 5, bot - 8))):
			polyline(body, [(int(x + lean * 0.5), int(y + up * 0.5)) for x, y in seg], vc)
	body = outline(body, OUTLINE)
	out.blit(body, 0, 0)
	# ---- corrupted crystal spurs on the back hump (violet, readable on dark graveyard)
	if m < 0.5:
		spurs = Canvas(CW, CH)
		bx, by = cx + 9 + lean * 0.8, bot - 37 + up + p["hump"]
		for (ox, oy, hgt, wd) in ((-3, 3, 7, 3), (2, 0, 10, 4), (7, 4, 7, 3), (11, 10, 6, 3)):
			for k in range(hgt):
				half = wd * (1 - k / hgt) / 2.0
				for xx in range(int(-half), int(half) + 1):
					c = VIOLET[2] if xx > 0 else VIOLET[4] if k > hgt * 0.5 and xx < 0 else VIOLET[3]
					spurs.put(int(bx + ox + xx + (k * 0.25 if ox > 0 else -k * 0.1)), int(by + oy - k), c)
		out.blit(outline(spurs, OUTLINE), 0, 0)
		# redraw body overlap edge so spurs sit behind the body silhouette base
		covered = Canvas(CW, CH)
		for i, c in enumerate(body.px):
			if c is not None and not (c == OUTLINE and spurs.px[i] is not None):
				covered.px[i] = c
		# body pixels win where both exist, except at the spur tips above the hump
		for i, c in enumerate(covered.px):
			if c is not None:
				out.px[i] = c
	# ---- head: small, sunk between shoulders, red eyes, wide toothy mouth, bolted jaw band
	hx = cx - 9 + lean + p["head"][0]
	hy = bot - 38 + up * 0.9 + p["head"][1] + m * 20
	if m < 0.92:
		head = paint(CW, CH, [(hx, hy, 7.8, 6.2), (hx + 1.5, hy - 3.2, 6.5, 4.2)], ramp, clip_y=CBOT)
		ey = int(hy) - 2
		ex = int(hx) - 5
		eyec = BLOOD[3] if glow < 0.5 else EMBER[3]
		if p["squint"] or m > 0.3:
			for ddx in range(3):
				dot(head, ex + ddx, ey, OUTLINE)
				dot(head, ex + 6 + ddx, ey + 1, OUTLINE)
		else:
			for ddx in range(3):
				for ddy in range(2):
					dot(head, ex + ddx, ey + ddy, eyec)
					dot(head, ex + 6 + ddx, ey + 1 + ddy, eyec)
			dot(head, ex, ey, EMBER[3] if glow > 0.5 else BLOOD[4])
			for ddx in range(-1, 4):
				dot(head, ex + ddx, ey - 1, OUTLINE)
			for ddx in range(5, 10):
				dot(head, ex + ddx, ey, OUTLINE)
		my = int(hy) + 2
		op = p["mouth"] + 1
		for ddx in range(-7, 7):
			for ddy in range(op):
				dot(head, int(hx) + ddx, my + ddy, EMBER[1] if glow > 0.5 else BLOOD[0])
			dot(head, int(hx) + ddx, my - 1, OUTLINE)
		for ddx in (-6, -4, -2, 0, 2, 4):
			dot(head, int(hx) + ddx, my, TEETH)
			dot(head, int(hx) + ddx + 1, my, TEETH) if ddx % 4 == 0 else None
		if op > 2:
			for ddx in (-5, -1, 3, 5):
				dot(head, int(hx) + ddx, my + op - 1, TEETH)
		for tx in (-6, 4):
			for k in range(1, 4):
				dot(head, int(hx) + tx, my - k, TEETH if k < 3 else BONE[2])
		if glow > 0.5:
			for ddx in range(-6, 6, 2):
				dot(head, int(hx) + ddx, my + op - 1, EMBER[3])
		out.blit(outline(head, OUTLINE), 0, 0)
	# ---- weapon arm (in front)
	S = (cx - 9 + lean * 0.8, bot - 26 + up * 0.9)
	F = p["F"]
	if m > 0:
		F = (F[0] + 3 * m, bot - 4 - (bot - 4 - F[1]) * (1 - m))
		S = (S[0], bot - (bot - S[1]) * (1 - 0.8 * m))
	Epos = p["E"]
	if Epos is None:
		Epos = ((S[0] + F[0]) / 2 - 3, (S[1] + F[1]) / 2 + 3)
	cells = []
	limb(cells, S, Epos, 5.6, 5.0)
	limb(cells, Epos, F, 5.0, 5.2)
	cells.append((F[0], F[1], 6.4, 6.2 - 2.2 * m))
	arm = paint(CW, CH, cells, tint_ramp(ramp, RAW, 0.2), clip_y=CBOT)
	wx, wy = int(Epos[0] + (F[0] - Epos[0]) * 0.7), int(Epos[1] + (F[1] - Epos[1]) * 0.7)
	for k in range(4):  # rotten bandage bands
		for dd in range(-3, 3):
			dot(arm, wx + dd + k // 2, wy - 2 + k + (dd > 0), RAW_DK if k % 2 == 0 else WOOD[2])
	for k in range(3):
		dot(arm, int(Epos[0]) + k - 1, int(Epos[1]) + 2, RAW)
	if glow > 0:
		polyline(arm, [(int(S[0]), int(S[1])), (int(Epos[0]), int(Epos[1])), (int(F[0]), int(F[1]))], BLOOD[3] if glow < 0.8 else EMBER[2])
	arm = outline(arm, OUTLINE)
	if m < 1.0 or True:
		out.blit(cleaver(out, F, p["wa"], p["wl"], 12, p["hot"]), 0, 0)
	out.blit(arm, 0, 0)
	# knuckles over the grip
	for k in range(3):
		out.put(int(F[0]) - 2 + k * 2, int(F[1]) + 3, OUTLINE)
	if p["flash"] > 0:
		a = math.radians(p["wa"])
		tx, ty = F[0] + math.cos(a) * p["wl"] * 0.8, F[1] + math.sin(a) * p["wl"] * 0.8
		glint(out, int(tx), int(ty), 4)
	return out


def cdust(c, cxp, base, i):
	tones = [(176, 170, 160, 235), (146, 140, 134, 215), (112, 108, 106, 190), (86, 84, 88, 150)]
	if i == 0:
		for k, (dx, r) in enumerate(((-2, 6), (7, 5), (-10, 4), (13, 3))):
			disc(c, cxp + dx, base - r + 1, r, tones[0] if k < 2 else tones[1])
	elif i == 1:
		for k, (dx, r) in enumerate(((-5, 6), (6, 6), (-12, 4), (13, 4), (-1, 8))):
			disc(c, cxp + dx, base - r + 1 - (k == 4) * 3, r, tones[1] if k < 4 else tones[2])
	else:
		for k, (dx, r) in enumerate(((-7, 4), (8, 4), (-13, 3), (14, 3))):
			disc(c, cxp + dx, base - r - 2, r, tones[2 + (i > 2)])
	for dx in range(-11, 12):
		if abs(dx) % 3 == 0:
			c.put(cxp + dx, base, OUTLINE)


def drip(f, x, ln, base=CBOT - 3):
	ys = [y for y in range(CH) if f.get(x, y) is not None]
	if not ys:
		return
	y0 = max(ys)
	if y0 >= base:
		return
	for k in range(1, ln + 1):
		if f.get(x, y0 + k) is None:
			f.put(x, y0 + k, FL[3] if k < ln else FL[4])


def chud_sheet():
	frames = []
	cx, B = CCX, CBOT
	# idle: heavy breathing, cleaver trailing on the ground in front
	for (bob, br, fy) in ((0.0, 0.0, 0.0), (-0.8, 0.6, -0.5), (-1.4, 1.0, -0.8), (-0.7, 0.5, -0.4)):
		frames.append(chud_frame(chud_pose(bob=bob, breath=br, F=(cx - 19, B - 15 + fy), B=(cx + 16, B - 13 + fy * 0.5), wa=130 - fy * 3)))
	# walk: dragging shuffle, cleaver scrapes the floor
	walk = [(0.0, 3.5, 0.0), (-1.0, 1.8, -0.8), (-1.4, -1.5, -1.4), (0.0, -3.5, 0.0), (-1.0, -1.8, -0.8), (-1.4, 1.5, -1.4)]
	for i, (bob, foot, fy) in enumerate(walk):
		sway = math.sin(i / 6.0 * math.tau)
		frames.append(chud_frame(chud_pose(bob=bob, foot=foot, lean=-1.5, F=(cx - 19 + sway * 1.5, B - 15 + fy * 0.4),
			B=(cx + 16 - sway * 2, B - 13 + fy * 0.3), wa=128 + sway * 4)))
	# windup 0.3 s: crouch, haul the cleaver overhead, glow
	frames.append(chud_frame(chud_pose(lean=2.0, bob=1.0, crouch=1.0, F=(cx - 18, B - 23), E=(cx - 22, B - 18), glow=0.5, mouth=2, wa=-175, wl=20, hot=0.3, B=(cx + 14, B - 12))))
	frames.append(chud_frame(chud_pose(lean=3.5, bob=0.5, hump=1.0, F=(cx - 19, B - 34), E=(cx - 25, B - 28), glow=0.9, mouth=3, wa=-112, wl=21, hot=0.8, flash=1, B=(cx + 14, B - 12))))
	frames.append(chud_frame(chud_pose(lean=4.5, bob=0.5, hump=1.5, F=(cx - 15, B - 37), E=(cx - 24, B - 31), glow=1.0, mouth=3, wa=-84, wl=21, hot=1.0, flash=1, B=(cx + 14, B - 12))))
	# slam: release (fast arc), impact, hold, recover
	f13 = chud_frame(chud_pose(lean=-4.0, bob=2.0, F=(cx - 21, B - 27), E=(cx - 22, B - 30), glow=0.9, mouth=3, wa=-165, wl=21, hot=1.0, B=(cx + 14, B - 14)))
	for ddx in (0, 3, 6):
		polyline(f13, [(cx - 36 + ddx, B - 38 - ddx), (cx - 31 + ddx, B - 45 - ddx)], (222, 214, 190, 255), only_inside=False)
	frames.append(f13)
	f14 = chud_frame(chud_pose(lean=-5.0, bob=2.5, crouch=1.0, F=(cx - 21, B - 14), E=(cx - 21, B - 22), glow=0.6, mouth=3, wa=128, wl=21, hot=0.6, flash=1, B=(cx + 14, B - 14)))
	cdust(f14, cx - 30, B, 0)
	frames.append(f14)
	f15 = chud_frame(chud_pose(lean=-4.5, bob=2.0, crouch=0.8, F=(cx - 21, B - 14), E=(cx - 21, B - 21), glow=0.2, mouth=2, wa=128, wl=21, B=(cx + 14, B - 14)))
	cdust(f15, cx - 30, B, 1)
	frames.append(f15)
	f16 = chud_frame(chud_pose(lean=-2.0, bob=0.8, F=(cx - 20, B - 15), E=(cx - 21, B - 22), mouth=1, wa=130, wl=20, B=(cx + 15, B - 13)))
	cdust(f16, cx - 30, B, 2)
	frames.append(f16)
	# hit: flesh ripples
	frames.append(chud_frame(chud_pose(lean=3.5, bob=1.5, lump=2.0, squint=True, breath=1.0, F=(cx - 17, B - 15), mouth=2, wa=122)))
	frames.append(chud_frame(chud_pose(lean=-1.0, bob=-0.5, lump=-2.0, squint=True, breath=-0.5, F=(cx - 20, B - 15), mouth=2, wa=132)))
	# death: staggers, drops the cleaver, collapses and liquefies into a heap
	death = [
		dict(lean=3.0, bob=3.0, sag=3.0, F=(cx - 16, B - 8), mouth=3, squint=True, head=(1, 2), melt=0.08, wa=135),
		dict(lean=4.0, bob=5.0, sag=4.0, F=(cx - 17, B - 5), mouth=2, squint=True, head=(1, 3), melt=0.22, wa=150),
		dict(lean=3.0, bob=5.0, sag=4.0, F=(cx - 19, B - 4), mouth=1, squint=True, head=(1, 3), melt=0.4, wa=168),
		dict(lean=1.5, bob=5.0, sag=4.0, F=(cx - 20, B - 3), mouth=1, squint=True, melt=0.58, wa=174),
		dict(F=(cx - 21, B - 3), squint=True, melt=0.74, wa=178),
		dict(F=(cx - 21, B - 3), squint=True, melt=0.88, wa=178),
		dict(F=(cx - 21, B - 3), squint=True, melt=1.0, wa=178),
	]
	dframes = [chud_frame(chud_pose(**d)) for d in death]
	for f, xs in zip(dframes[:4], ((44, 30), (46, 28), (48, 29), (51,))):
		for x in xs:
			drip(f, x, 4)
	for f, bub in ((dframes[4], (32, 42, 51)), (dframes[5], (30, 44, 54)), (dframes[6], (28, 38, 47, 56))):
		for x in bub:
			ys = [y for y in range(CH - 1) if f.get(x, y) is not None]
			if ys:
				f.put(x, min(ys) + 2, FL[4])
				f.put(x - 1, min(ys) + 2, FL[3])
	frames += dframes
	return sheet(frames, 26)


# ====================================================================== checks
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
	sh = Canvas(cols * (cw + 1), rows * (ch + 1))
	sh.rect(0, 0, sh.w, sh.h, GREY_BG)
	for i, f in enumerate(frames):
		ox, oy = (i % cols) * (cw + 1), (i // cols) * (ch + 1)
		sh.blit(f, ox, oy)
		for y in range(ch):
			if sh.get(ox + cw, oy + y) == GREY_BG:
				sh.put(ox + cw, oy + y, (70, 76, 90, 255))
		for x in range(cw):
			if sh.get(ox + x, oy + ch) == GREY_BG:
				sh.put(ox + x, oy + ch, (70, 76, 90, 255))
	save_png(sh, path, scale=4)


ANIMS = {
	"bloated_slime.png": [("crawl", 0, 8), ("swell", 8, 4), ("hit", 12, 2), ("death", 14, 6)],
	"chud_blob.png": [("idle", 0, 4), ("walk", 4, 6), ("windup", 10, 3), ("slam", 13, 4), ("hit", 17, 2), ("death", 19, 7)],
}


def check(sheets, log):
	ok = True
	for name, cv, cw, ch, n in sheets:
		good = cv.w == cw * n and cv.h == ch
		log("%-26s %4dx%-3d expected %4dx%-3d %s" % (name, cv.w, cv.h, cw * n, ch, "OK" if good else "FAIL"))
		ok &= good
		if name not in ANIMS:
			continue
		fr = split(cv, cw, ch, n)
		for anim, s, c in ANIMS[name]:
			ws, hs, cxs = [], [], []
			for i in range(s, s + c):
				bb = fr[i].bbox()
				if bb is None:
					log("  f%02d EMPTY" % i)
					ok = False
					continue
				w, h = bb[2] - bb[0], bb[3] - bb[1]
				cxm = (bb[0] + bb[2]) / 2.0
				flag = ""
				grounded = not (anim == "death" and i > s + 1)
				if grounded and bb[3] != ch:
					flag += " LOWEST ROW != last"
					ok = False
				if anim == "death" and bb[3] != ch:
					flag += " (death: floating, FAIL)"
					ok = False
				if edge_touch(fr[i]):
					flag += " TOUCHES CELL EDGE"
					ok = False
				ws.append(w)
				hs.append(h)
				cxs.append(cxm)
				log("  %-6s f%02d bbox=%s w=%d h=%d cx=%.1f%s" % (anim, i, bb, w, h, cxm, flag))
			log("  == %s: w %d..%d  h %d..%d  cx %.1f..%.1f" % (anim, min(ws), max(ws), min(hs), max(hs), min(cxs), max(cxs)))
	return ok


def edge_touch(f):
	bb = f.bbox()
	return bb[0] <= 0 or bb[2] >= f.w or bb[1] <= 0


SPECS = [
	("bloated_slime.png", bloated_sheet, BW, BH, 20, 5),
	("vfx_bloated_burst.png", bloated_burst, 112, 48, 6, 3),
	("chud_blob.png", chud_sheet, CW, CH, 26, 5),
]


def main():
	pdir = log_path = None
	if "--preview" in sys.argv:
		pdir = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(pdir, exist_ok=True)
	if "--log" in sys.argv:
		log_path = sys.argv[sys.argv.index("--log") + 1]
	lines = []

	def log(s):
		print(s)
		lines.append(s)

	os.makedirs(OUT, exist_ok=True)
	sheets = []
	for name, builder, cw, ch, n, cols in SPECS:
		cv = builder()
		save_png(cv, os.path.join(OUT, name))
		sheets.append((name, cv, cw, ch, n))
		log("wrote %s %d %d" % (os.path.join(OUT, name), cv.w, cv.h))
		if pdir:
			preview(cv, cw, ch, n, os.path.join(pdir, name.replace(".png", "_x4.png")), cols)
	ok = check(sheets, log)
	log("CHECK " + ("OK" if ok else "FAILED"))
	if log_path:
		open(log_path, "w").write("\n".join(lines) + "\n")
	return 0 if ok else 1


if __name__ == "__main__":
	sys.exit(main())

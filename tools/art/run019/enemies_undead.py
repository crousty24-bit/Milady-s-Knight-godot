"""RUN-019 undead enemies: skeleton warrior, skeleton archer, blight sorcerer + VFX.

Original procedural pixel art (no third-party pixels). Contract: work/run019/claude/SPEC.md
section A. Enemies face LEFT, feet on the last row of the cell (outline row), body centred on
column cell_w/2, anchor stable on every frame. Light comes from the upper left.

Usage:
  python3 tools/art/run019/enemies_undead.py [--preview DIR]
Final PNGs are written to assets/run019/enemies/ (deterministic).
"""
import argparse
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
from pixel import Canvas as _Canvas, line, outline, save_png, sheet  # noqa: E402
from palette import BLOOD, CORRUPT, EMBER, OUTLINE, SLIME_GREEN, WOOD, MOSS  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "run019", "enemies")

# ---------------------------------------------------------------- colours
BONE_D = (92, 82, 74, 255)
BONE_M = (152, 141, 124, 255)
BONE_L = (206, 196, 172, 255)
BONE_H = (238, 231, 208, 255)
GAP = (48, 41, 44, 255)
SOCKET = (22, 16, 24, 255)
RUST = (138, 74, 42, 255)
BLADE = [(88, 84, 92, 255), (140, 138, 148, 255), (190, 192, 200, 255), (232, 236, 242, 255)]
CLOTH = [MOSS[0], MOSS[1], MOSS[2], MOSS[3]]  # archer hood / cloak (olive: distinct from bone and violet)
GLOW_E = [EMBER[1], EMBER[2], EMBER[3], (255, 244, 214, 255)]
MAG = [CORRUPT[2], CORRUPT[3], CORRUPT[4], (232, 180, 240, 255), (255, 232, 255, 255)]
LILAC = (214, 196, 236, 255)
WHITE_HOT = (255, 244, 214, 255)


class Canvas(_Canvas):
	def put(self, x, y, color):
		super().put(int(math.floor(x + 0.5)), int(math.floor(y + 0.5)), color)

	def copy(self):
		c = Canvas(self.w, self.h)
		c.px = list(self.px)
		return c


def mix(c0, c1, t):
	return tuple(int(round(c0[i] * (1 - t) + c1[i] * t)) for i in range(4))


def alpha(c, a):
	return (c[0], c[1], c[2], int(a))


class Pen:
	"""Draws in coordinates relative to the feet anchor (cx, gy); x<0 is forward (left)."""

	def __init__(self, cv, cx, gy):
		self.cv, self.cx, self.gy = cv, cx, gy

	def put(self, x, y, col):
		self.cv.put(self.cx + int(math.floor(x + 0.5)), self.gy + int(math.floor(y + 0.5)), col)

	def erase(self, x, y):
		ax, ay = self.cx + int(math.floor(x + 0.5)), self.gy + int(math.floor(y + 0.5))
		if 0 <= ax < self.cv.w and 0 <= ay < self.cv.h:
			self.cv.px[ay * self.cv.w + ax] = None

	def line(self, x0, y0, x1, y1, col):
		line(self.cv, self.cx + x0, self.gy + y0, self.cx + x1, self.gy + y1, col)

	def rect(self, x, y, w, h, col):
		for yy in range(h):
			for xx in range(w):
				self.put(x + xx, y + yy, col)

	def grid(self, x, y, rows, pal):
		for j, r in enumerate(rows):
			for i, ch in enumerate(r):
				if ch in pal:
					self.put(x + i, y + j, pal[ch])

	def disc(self, x, y, r, col):
		for yy in range(int(-r - 1), int(r + 2)):
			for xx in range(int(-r - 1), int(r + 2)):
				if xx * xx + yy * yy <= r * r + 0.3:
					self.put(x + xx, y + yy, col)


def ik(a, b, l1, l2, want):
	dx, dy = b[0] - a[0], b[1] - a[1]
	dist = math.hypot(dx, dy) or 1.0
	d = min(max(dist, 0.001), l1 + l2 - 0.01)
	ex, ey = dx / dist, dy / dist
	along = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
	h = math.sqrt(max(l1 * l1 - along * along, 0.0))
	bx, by = a[0] + ex * along, a[1] + ey * along
	s1 = (bx - ey * h, by + ex * h)
	s2 = (bx + ey * h, by - ex * h)
	return s1 if want(s1, s2) else s2


def knee_fwd(s1, s2):
	return s1[0] < s2[0]


def elbow_down(s1, s2):
	return s1[1] > s2[1]


# ---------------------------------------------------------------- skeleton rig
SKULL = [
	".llbbb.",
	"llbbbbd",
	"leebbbd",
	".eebbd.",
]
JAW = [
	"tTtbd",
	".lbbd",
]
SKPAL = {"l": BONE_L, "b": BONE_M, "d": BONE_D, "e": SOCKET, "t": BONE_H, "T": BONE_D}


def draw_skull(pen, hcx, top, jaw=0, glow=None, jaw_dx=0):
	"""Skull, face to the left. (hcx, top) = top row; cranium spans x hcx-4..hcx+2, 6 rows."""
	pen.grid(hcx - 4, top, SKULL, SKPAL)
	if glow is not None:
		pen.put(hcx - 3, top + 2, glow[0])
		pen.put(hcx - 2, top + 2, glow[1])
		pen.put(hcx - 3, top + 3, glow[2])
	pen.grid(hcx - 4 + jaw_dx, top + 4 + jaw, JAW, SKPAL)
	if jaw >= 1:
		for xx in range(hcx - 3, hcx):
			pen.put(xx + jaw_dx, top + 4, SOCKET if jaw >= 2 else GAP)


def draw_ribs(pen, x, ytop, rows=7, tilt=0):
	for r in range(rows):
		w = 7 if r < 3 else 6 if r < 5 else 5
		x0 = x - w // 2 - 1 + int(round(tilt * r / max(1, rows - 1)))
		for i in range(w):
			if r % 2 == 0:
				col = BONE_H if (i == 0 and r == 0) else BONE_L if i < w - 2 else BONE_M
			else:
				col = GAP if 0 < i < w - 1 else BONE_M
			pen.put(x0 + i, ytop + r, col)
		pen.put(x0 + w - 1, ytop + r, BONE_D)


def draw_limb(pen, a, m, b, col, joint):
	pen.line(a[0], a[1], m[0], m[1], col)
	pen.line(m[0], m[1], b[0], b[1], col)
	pen.put(m[0], m[1], joint)


def draw_leg(pen, hip, foot, shade=False):
	knee = ik(hip, foot, 4.6, 4.6, knee_fwd)
	draw_limb(pen, hip, knee, foot, BONE_M if shade else BONE_L, BONE_L if shade else BONE_H)
	pen.put(foot[0] - 1, foot[1], BONE_M if shade else BONE_L)
	pen.put(foot[0], foot[1], BONE_M if shade else BONE_L)


def draw_arm(pen, sh, hand, shade=False):
	el = ik(sh, hand, 4.4, 4.4, elbow_down)
	draw_limb(pen, sh, el, hand, BONE_M if shade else BONE_L, BONE_L if shade else BONE_H)
	pen.put(hand[0], hand[1], BONE_L if shade else BONE_H)


def walk_feet(i, n, stride=3.0, lift=2.0):
	th = 2 * math.pi * i / n
	res = []
	for ph in (math.pi, 0.0):  # far, near
		t = th + ph
		res.append((stride * math.cos(t), -lift * max(0.0, math.sin(t))))
	return res, (1 if abs(math.cos(th)) > 0.6 else 0)


def pose(**kw):
	p = dict(dx=0, dy=0, lean=0, hx=0, hy=0, jaw=0, glow=None, ffar=(3, 0), fnear=(-3, 0),
	         far_hand=(2, -10), near_hand=(-4, -11), tilt=0)
	p.update(kw)
	return p


def joints(p):
	return (p["dx"], -9 + p["dy"]), (p["dx"] + p["lean"], -17 + p["dy"])


def head_x(p):
	return joints(p)[1][0] + p["hx"] + (-1 if p["lean"] < 0 else 0)


def head_top(p):
	return joints(p)[1][1] - 7 + p["hy"]


def skeleton_body(pen, p, behind=None, headgear=None):
	hip, sh = joints(p)
	hj = (hip[0], hip[1] + 1)
	draw_leg(pen, (hj[0] + 1, hj[1]), p["ffar"], shade=True)
	draw_arm(pen, (sh[0] + 1, sh[1]), p["far_hand"], shade=True)
	if behind:
		behind(pen)
	pen.line(hip[0] + 1, hip[1] - 1, sh[0] + 1, sh[1] + 1, BONE_M)
	pen.rect(hip[0] - 2, hip[1] - 1, 5, 2, BONE_M)
	pen.put(hip[0] - 2, hip[1] - 1, BONE_L)
	pen.put(hip[0] - 1, hip[1] - 1, BONE_L)
	pen.put(hip[0], hip[1], BONE_D)
	draw_ribs(pen, sh[0], sh[1] - 1, tilt=p["tilt"])
	draw_skull(pen, head_x(p), head_top(p), p["jaw"], p["glow"])
	if headgear:
		headgear(pen, head_x(p), head_top(p))
	draw_leg(pen, hj, p["fnear"])
	draw_arm(pen, (sh[0], sh[1] + 1), p["near_hand"])


def finish(cv):
	return outline(cv, OUTLINE)


def bone_line(pen, x0, y0, x1, y1, shade=0):
	pen.line(x0, y0, x1, y1, (BONE_L, BONE_M, BONE_D)[shade])
	pen.put(x0, y0, BONE_H)
	pen.put(x1, y1, BONE_L)


def rib_block(pen, x, y, w, h):
	for r in range(h):
		for i in range(w):
			col = BONE_L if (r % 2 == 0) else GAP
			if i == 0 and r == 0:
				col = BONE_H
			if i >= w - 1:
				col = BONE_D if r % 2 == 0 else BONE_M
			pen.put(x + i, y + r, col)


def eye_glow_fx(pen, p, k):
	"""Red-orange glow just in front of the eye socket (drawn after outline)."""
	ex = head_x(p) - 4
	ey = head_top(p) + 2
	pen.put(ex, ey, BLOOD[3])
	if k >= 1:
		pen.put(ex, ey - 1, EMBER[2])
		pen.put(ex, ey + 1, BLOOD[2])
	if k >= 2:
		pen.put(ex - 1, ey, BLOOD[4])


# ================================================================= SKELETON WARRIOR
def sword(pen, hand, ang, length=12):
	"""Rusty sword; ang 0 = pointing left, 90 = up. Returns the tip."""
	hx, hy = hand
	dx, dy = -math.cos(math.radians(ang)), -math.sin(math.radians(ang))
	px, py = -dy, dx
	pen.put(hx - dx, hy - dy, WOOD[3])
	pen.put(hx, hy, WOOD[2])
	for s in (-1, 0, 1):
		pen.put(hx + dx * 2 + px * s, hy + dy * 2 + py * s, BLADE[2] if s else BLADE[1])
	n = int(length)
	for k in range(3, n + 3):
		col = BLADE[2] if k % 3 else BLADE[1]
		if k in (6, 7, 10):
			col = RUST
		pen.put(hx + dx * k, hy + dy * k, col)
	tip = (hx + dx * (n + 2), hy + dy * (n + 2))
	pen.put(tip[0], tip[1], BLADE[3])
	return tip


def shield(pen, x, y):
	pen.disc(x, y, 3.3, WOOD[2])
	for yy in range(-4, 5):
		for xx in range(-4, 5):
			d = xx * xx + yy * yy
			if 8.5 <= d <= 12.2:
				pen.put(x + xx, y + yy, BLADE[1] if (xx + yy) < 1 else BLADE[0])
	pen.put(x, y, BLADE[2])
	pen.put(x - 1, y - 1, WOOD[4])
	pen.put(x + 1, y, WOOD[1])
	pen.put(x, y + 1, WOOD[1])


SWING_H = [(-2, -19), (-6, -15), (-8, -12), (-6, -10)]
SWING_A = [80, 20, -25, -60]


def swing_tip(k, reach=14):
	h, a = SWING_H[k], SWING_A[k]
	return (h[0] - math.cos(math.radians(a)) * reach, h[1] - math.sin(math.radians(a)) * reach)


def warrior_pose(i):
	"""(pose, sword(hand, ang), shield pos, tag)"""
	if i < 4:
		dy, jaw, ang = [(0, 0, 115), (1, 1, 112), (1, 0, 110), (0, 0, 114)][i]
		p = pose(dy=dy, jaw=jaw, near_hand=(-4, -11 + dy), far_hand=(2, -10 + dy))
		return p, ((3, -10 + dy), ang), (-6, -13 + dy), None
	if i < 10:
		k = i - 4
		feet, dy = walk_feet(k, 6)
		p = pose(dy=dy, lean=-1, jaw=k % 2, ffar=feet[0], fnear=feet[1], near_hand=(-4, -11 + dy), far_hand=(2, -10 + dy))
		return p, ((3, -10 + dy), 112 + (4 if k % 2 else 0)), (-6, -13 + dy), None
	if i < 13:
		k = i - 10
		glow = [(EMBER[0], EMBER[1], EMBER[0]), (EMBER[1], EMBER[2], EMBER[1]), (EMBER[2], GLOW_E[3], GLOW_E[3])][k]
		hand = [(3, -14), (4, -18), (4, -20)][k]
		dy = 1 + k // 2
		p = pose(dy=dy, lean=1 + k, jaw=1 + (k > 0), glow=glow, fnear=(-4, 0), ffar=(3, 0),
		         near_hand=(-5, -11), far_hand=(hand[0], hand[1] + dy))
		return p, (hand, [126, 142, 158][k]), (-7, -12), ("windup", k)
	if i < 17:
		k = i - 13
		p = pose(dx=[0, -1, -2, -1][k], dy=[1, 1, 2, 1][k], lean=[-1, -2, -3, -2][k], jaw=2 if k < 3 else 1,
		         glow=[(EMBER[2], GLOW_E[3], EMBER[2]), (EMBER[1], EMBER[2], EMBER[1]), None, None][k],
		         fnear=(-5, 0), ffar=(4, 0), near_hand=(-5, -11), far_hand=SWING_H[k])
		return p, (SWING_H[k], SWING_A[k]), (-7, -12), ("swing", k)
	k = i - 17
	p = pose(dx=[2, 1][k], dy=[0, 1][k], lean=[2, 1][k], hx=[1, 2][k], hy=[-2, -1][k], jaw=2, tilt=1,
	         fnear=(-2, 0), ffar=(4, 0), near_hand=(-3, -11), far_hand=(4, -13))
	return p, ((5, -12), [150, 140][k]), (-4, -12), ("hit", k)


def warrior_death(k):
	cv = Canvas(48, 32)
	pen = Pen(cv, 24, 30)
	if k <= 2:
		dy = [3, 6, 8][k]
		p = pose(dx=[2, 2, 1][k], dy=dy, lean=[3, 3, 2][k], hx=[1, 1, 0][k], hy=[-1, 0, 2][k], jaw=2,
		         tilt=[1, 2, 3][k], fnear=(-5, 0), ffar=(2, 0),
		         near_hand=(-3, -9 + dy // 2), far_hand=(4, -9 + dy // 2))
		shield(pen, [-7, -9, -10][k], [-10, -6, -3][k])
		sword(pen, [(8, -14), (11, -8), (13, -2)][k], [150, 190, 180][k], 11)
		skeleton_body(pen, p)
	else:
		s = k - 3
		sk = [(-5, -10), (-9, -7), (-12, -5), (-13, -5), (-13, -5)][s]
		jawo = [2, 1, 1, 1, 1][s]
		sword(pen, (9, -1), 8 if s < 2 else 3, 11)
		pen.rect(-4, -1, 6, 2, WOOD[2])
		pen.put(-4, -1, WOOD[4])
		pen.put(-3, -1, BLADE[1])
		pen.put(-2, -1, BLADE[1])
		pen.put(1, 0, WOOD[1])
		hts = [6, 4, 3, 3, 3][s]
		rib_block(pen, 1, -hts, 6, hts)
		pen.rect(-2, -2, 5, 2, BONE_M)
		pen.put(-2, -2, BONE_L)
		bone_line(pen, -5, 0, 1, -3, 0)
		bone_line(pen, 4, -1, 10, 0, 1)
		bone_line(pen, 7, -3, 10, -2, 2)
		pen.put(5, -4 if hts >= 4 else -3, BONE_H)
		draw_skull(pen, sk[0], sk[1], jawo, None)
	return cv


def render_warrior(i):
	if i >= 19:
		return finish(warrior_death(i - 19))
	cv = Canvas(48, 32)
	pen = Pen(cv, 24, 30)
	p, sw, sh, tag = warrior_pose(i)
	skeleton_body(pen, p)
	tip = sword(pen, sw[0], sw[1], 12)
	shield(pen, sh[0], sh[1])
	cv = finish(cv)
	pen = Pen(cv, 24, 30)
	if tag and tag[0] == "windup":
		k = tag[1]
		eye_glow_fx(pen, p, k)
		pen.put(tip[0], tip[1], WHITE_HOT)
		pen.put(tip[0] + 1, tip[1] - 1, GLOW_E[2])
		if k >= 1:
			pen.put(tip[0] - 1, tip[1] + 1, EMBER[2])
		if k >= 2:
			pen.put(tip[0] + 1, tip[1] + 1, BLOOD[4])
			pen.put(tip[0], tip[1] - 2, GLOW_E[3])
	if tag and tag[0] == "swing":
		k = tag[1]
		if k < 2:
			eye_glow_fx(pen, p, 1)
		if k in (1, 2):
			for t in range(11):
				u = t / 10.0
				hh = (SWING_H[k - 1][0] + (SWING_H[k][0] - SWING_H[k - 1][0]) * u, SWING_H[k - 1][1] + (SWING_H[k][1] - SWING_H[k - 1][1]) * u)
				an = math.radians(SWING_A[k - 1] + (SWING_A[k] - SWING_A[k - 1]) * u)
				pen.put(hh[0] - math.cos(an) * 15, hh[1] - math.sin(an) * 15 - 1,
				        (236, 240, 246, 255) if t % 2 == 0 else BLADE[2])
			b = swing_tip(k, 15)
			pen.put(b[0] - 1, b[1], WHITE_HOT)
		if k == 0:
			t = swing_tip(0, 14)
			pen.put(t[0] + 1, t[1] - 1, WHITE_HOT)
	if tag and tag[0] == "hit":
		k = tag[1]
		pen.put(-9 + 4 * k, -22 - k, (236, 240, 246, 255))
		pen.put(-10 + 4 * k, -21 - k, BLADE[2])
	return cv


# ================================================================= SKELETON ARCHER
HOOD = [
	".....ab.",
	"...aabbb",
	"..aabbbc",
	"...bbbcc",
	"...bbbcc",
	"...bbbcc",
	"....bbcc",
]
HOODPAL = {"a": CLOTH[3], "b": CLOTH[2], "c": CLOTH[1]}


def bow(pen, grip, string_back=0.0, vib=0, tilt=0.0, length=7):
	gx, gy = grip
	pts = []
	for t in range(-length, length + 1):
		u = t / float(length)
		pts.append((gx + (u * u) * 2.2 + tilt * u, gy + t))
	for (x, y) in pts:
		pen.put(x, y, WOOD[2] if y >= gy else WOOD[3])
	pen.put(gx, gy, WOOD[4])
	pen.put(gx, gy - 1, WOOD[4])
	pen.put(gx, gy + 1, WOOD[1])
	top, bot = pts[0], pts[-1]
	mid = (gx + 2.2 + string_back, gy + vib)
	pen.line(top[0], top[1], mid[0], mid[1], BONE_M)
	pen.line(mid[0], mid[1], bot[0], bot[1], BONE_M)
	return mid


def arrow(pen, nock, length=13, glow=0):
	x0, y = nock
	x1 = x0 - length
	pen.line(x0, y, x1 + 2, y, BONE_L)
	pen.put(x1 + 1, y, BLADE[1])
	pen.put(x1, y, BLADE[3] if glow else BLADE[2])
	pen.put(x1 + 2, y - 1, BLADE[2])
	pen.put(x1 + 2, y + 1, BLADE[0])
	pen.put(x0, y - 1, BONE_M)
	pen.put(x0 + 1, y + 1, BONE_M)
	return (x1, y)


def archer_pose(i):
	if i < 4:
		dy, jaw = [(0, 0), (1, 0), (1, 1), (0, 0)][i]
		p = pose(dy=dy, jaw=jaw, near_hand=(-6, -11 + dy), far_hand=(1, -9 + dy))
		return p, dict(grip=(-8, -11 + dy)), None
	if i < 10:
		k = i - 4
		feet, dy = walk_feet(k, 6)
		p = pose(dy=dy, lean=-1, ffar=feet[0], fnear=feet[1], near_hand=(-6, -11 + dy), far_hand=(1, -9 + dy), jaw=k % 2)
		return p, dict(grip=(-8, -11 + dy)), None
	if i < 13:
		k = i - 10
		glow = [(EMBER[0], EMBER[1], EMBER[0]), (EMBER[1], EMBER[2], EMBER[1]), (EMBER[2], GLOW_E[3], GLOW_E[3])][k]
		draw = [(-3, -11), (-2, -11), (0, -11)][k]
		p = pose(dy=2, lean=-1, hx=-1, glow=glow, jaw=1, fnear=(-4, 0), ffar=(3, 0),
		         near_hand=(-9, -11), far_hand=(draw[0] + 1, draw[1]))
		return p, dict(grip=(-9, -11), sb=draw[0] - (-9 + 2.2), nock=draw, arrow=k), ("windup", k)
	if i < 16:
		k = i - 13
		gx = -9 + (1 if k == 2 else 0)
		p = pose(dy=[2, 2, 1][k], lean=-1, hx=-1, jaw=[2, 1, 0][k],
		         glow=[(EMBER[2], GLOW_E[3], EMBER[2]), None, None][k], fnear=(-4, 0), ffar=(3, 0),
		         near_hand=(gx, -11), far_hand=[(-2, -11), (-1, -10), (1, -9)][k])
		return p, dict(grip=(gx, -11), sb=[-1.5, 0.8, 0][k], vib=[0, 1, -1][k]), ("shoot", k)
	k = i - 16
	p = pose(dx=[2, 1][k], dy=[0, 1][k], lean=[2, 1][k], hx=[1, 2][k], hy=[-2, -1][k], jaw=2, tilt=1,
	         fnear=(-2, 0), ffar=(4, 0), near_hand=(-4, -11), far_hand=(3, -12))
	return p, dict(grip=(-6 + 3 * k, -11), tilt=1.5), ("hit", k)


def cloak(pen, p, t_sway=0):
	hip, sh = joints(p)
	top = sh[1] - 1
	hem = -4 + (1 if p["dy"] > 0 else 0)
	for y in range(top, hem + 1):
		u = (y - top) / float(max(1, hem - top))
		x0 = sh[0] + 1 + int(u * 1.5)
		w = 3 + int(u * 3)
		jag = [0, 1, 0, 2, 1, 0][(y + t_sway) % 6] if y > hem - 3 else 0
		for xx in range(w):
			col = CLOTH[3] if xx == 0 and u < 0.5 else CLOTH[2] if xx < w - 2 else CLOTH[1]
			if jag and xx >= w - jag:
				col = None
			if col is not None:
				pen.put(x0 + xx, y, col)


def quiver(pen, p):
	hip, sh = joints(p)
	qx, qy = sh[0] + 4 + (1 if p["lean"] > 0 else 0), sh[1] - 2
	pen.rect(qx, qy, 3, 8, WOOD[1])
	pen.rect(qx, qy, 1, 8, WOOD[2])
	pen.put(qx + 1, qy + 2, WOOD[3])
	pen.put(qx + 1, qy + 5, WOOD[3])
	pen.put(qx, qy - 1, BONE_M)
	pen.put(qx + 1, qy - 2, BONE_L)
	pen.put(qx + 2, qy - 1, BONE_M)
	pen.put(qx + 1, qy - 1, BONE_D)


def hood_over(pen, hcx, top):
	pen.grid(hcx - 4, top - 2, HOOD, HOODPAL)


def render_archer(i):
	W, H, CX, GY = 40, 32, 20, 30
	if i >= 18:
		return finish(archer_death(i - 18))
	cv = Canvas(W, H)
	pen = Pen(cv, CX, GY)
	p, bo, tag = archer_pose(i)

	def behind(pen_):
		cloak(pen_, p, t_sway=i)
		quiver(pen_, p)

	skeleton_body(pen, p, behind=behind, headgear=hood_over)
	bow(pen, bo["grip"], bo.get("sb", 0), bo.get("vib", 0), bo.get("tilt", 0))
	if "arrow" in bo:
		arrow(pen, bo["nock"], 13, glow=bo["arrow"])
		pen.put(bo["nock"][0], bo["nock"][1], BONE_H)
	cv = finish(cv)
	pen = Pen(cv, CX, GY)
	if tag and tag[0] == "windup":
		k = tag[1]
		eye_glow_fx(pen, p, k)
		tx, ty = bo["nock"][0] - 13, bo["nock"][1]
		pen.put(tx - 1, ty, WHITE_HOT)
		pen.put(tx, ty - 2, GLOW_E[2])
		pen.put(tx - 1, ty + 1, EMBER[2])
		if k >= 1:
			pen.put(tx + 1, ty + 2, EMBER[1])
			pen.put(tx - 2, ty - 1, EMBER[2])
		if k >= 2:
			pen.put(tx - 2, ty + 1, GLOW_E[3])
			pen.put(tx + 2, ty - 2, BLOOD[4])
	if tag and tag[0] == "shoot":
		k = tag[1]
		if k == 0:
			pen.put(-14, -12, WHITE_HOT)
			pen.put(-15, -11, GLOW_E[2])
			eye_glow_fx(pen, p, 1)
		if k == 1:
			pen.put(-5, -11, BONE_H)
	if tag and tag[0] == "hit":
		k = tag[1]
		pen.put(-9 + 4 * k, -22 - k, (236, 240, 246, 255))
	return cv


def archer_death(k):
	cv = Canvas(40, 32)
	pen = Pen(cv, 20, 30)
	if k <= 2:
		dy = [3, 6, 8][k]
		p = pose(dx=[2, 2, 1][k], dy=dy, lean=[3, 3, 2][k], hx=[1, 1, 0][k], hy=[-1, 0, 2][k], jaw=2,
		         tilt=[1, 2, 3][k], fnear=(-5, 0), ffar=(2, 0), near_hand=(-3, -9 + dy // 2), far_hand=(4, -9 + dy // 2))

		def behind(pen_):
			cloak(pen_, p, t_sway=k)

		bow(pen, (-9 - k, [-10, -7, -3][k]), 0, 0, tilt=[0, 2, 4][k], length=[7, 5, 3][k])
		skeleton_body(pen, p, behind=behind, headgear=hood_over)
	else:
		s = k - 3
		sk = [(-5, -10), (-8, -7), (-10, -5), (-10, -5), (-10, -5)][s]
		jawo = [2, 1, 1, 1, 1][s]
		for t in range(-6, 7):
			pen.put(-2 + t, -1 - (1 if abs(t) > 4 else 0), WOOD[2] if t < 2 else WOOD[3])
		pen.line(-8, -2, -1, -2, BONE_H)
		heights = [5, 4, 3, 3, 3][s]
		for y in range(heights):
			for x in range(9 - (heights - y)):
				pen.put(3 + x + (heights - y - 1) // 2, -heights + y, CLOTH[2] if x < 5 else CLOTH[1])
		pen.put(5, -heights, CLOTH[3])
		pen.put(6, -heights + 1, CLOTH[3])
		pen.rect(9, -2, 5, 2, WOOD[1])
		pen.put(9, -2, WOOD[3])
		pen.put(14, -3, BONE_L)
		pen.put(15, -2, BONE_M)
		hts = [5, 3, 3, 3, 3][s]
		rib_block(pen, 0, -hts, 6, hts)
		pen.rect(-3, -2, 4, 2, BONE_M)
		bone_line(pen, -6, 0, 0, -3, 0)
		bone_line(pen, 2, 0, 8, -1, 1)
		draw_skull(pen, sk[0], sk[1], jawo, None)
		pen.grid(sk[0] - 4, sk[1] - 1, HOOD[2:5], HOODPAL)
	return cv


# ================================================================= BLIGHT SORCERER
def staff(pen, base, top, twist=1, phase=0):
	x0, y0 = base
	x1, y1 = top
	n = int(max(abs(y1 - y0), abs(x1 - x0))) + 1
	for k in range(n + 1):
		u = k / float(n)
		x = x0 + (x1 - x0) * u
		y = y0 + (y1 - y0) * u
		off = twist * (1, 1, 0, -1, -1, 0)[(k + phase) % 6]
		pen.put(x + off, y, WOOD[3] if (k // 2) % 2 == 0 else WOOD[2])
		if k % 6 == 2:
			pen.put(x + off + 1, y, WOOD[1])
	pen.put(x1 - 1, y1 + 1, WOOD[4])
	pen.put(x1 + 1, y1 + 1, WOOD[2])
	pen.put(x1 - 1, y1 + 2, WOOD[3])
	return (x1, y1 - 1)


def staff_hand(pen, hand, ang, back, fwd, twist=0, phase=0):
	dx, dy = -math.cos(math.radians(ang)), -math.sin(math.radians(ang))
	return staff(pen, (hand[0] - dx * back, hand[1] - dy * back), (hand[0] + dx * fwd, hand[1] + dy * fwd), twist, phase)


def stone(pen, pos, level=0, pulse=0):
	x, y = pos
	body = MAG[min(level, 4)]
	pen.rect(x - 1, y - 1, 3, 3, body)
	pen.put(x, y - 2, MAG[2])
	pen.put(x - 1, y - 1, MAG[4] if level >= 1 else MAG[3])
	pen.put(x + 1, y + 1, MAG[0])
	pen.put(x, y, SLIME_GREEN[3] if pulse else SLIME_GREEN[2])


def robe(pen, H=22, top_w=6, hem_w=15, sway=0.0, phase=0.0, lean=0.0, dx=0, hem_y=0):
	R = CORRUPT
	for r in range(H):
		y = hem_y - H + 1 + r
		u = r / float(max(1, H - 1))
		w = int(round(top_w + (hem_w - top_w) * (u ** 1.15)))
		cxo = lean * (1 - u) + sway * math.sin(phase + u * 3.0) * u
		x0 = int(round(-w / 2.0 + cxo + dx))
		for i in range(w):
			t = i / float(max(1, w - 1))
			c = R[3] if t < 0.14 else R[2] if t < 0.45 else R[1] if t < 0.8 else R[0]
			if u > 0.35 and i in (w // 3, (2 * w) // 3 + 1) and r % 5 != 0:
				c = R[1] if t < 0.5 else R[0]
			pen.put(x0 + i, y, c)
		if r == H - 1:
			off = int(phase * 1.5) % 7
			for i in range(w):
				for c_ in range((0, 1, 0, 2, 1, 0, 1)[(i + off) % 7]):
					pen.erase(x0 + i, y - c_)


MASK = [
	"lbb",
	"eeb",
	"ebd",
	"tTd",
]
MASKPAL = {"l": BONE_L, "b": BONE_M, "d": BONE_D, "e": SOCKET, "t": BONE_H, "T": BONE_D}


def hood_sorc(pen, hx, hy, glow=None):
	R = CORRUPT
	rows = [
		"....bb..",
		"..bbbbb.",
		".bbbbbbc",
		".bbbbbcc",
		".bbbbbcc",
		".bbbbbcc",
		"..bbbbcc",
	]
	pen.grid(hx - 4, hy, rows, {"b": R[2], "c": R[1]})
	pen.put(hx - 3, hy + 1, R[3])
	pen.put(hx - 2, hy, R[3])
	pen.put(hx - 3, hy + 2, R[3])
	pen.put(hx + 3, hy - 1, R[2])
	pen.put(hx + 4, hy - 1, R[1])
	pen.put(hx + 4, hy, R[1])
	pen.grid(hx - 5, hy + 2, MASK, MASKPAL)
	pen.put(hx - 5, hy + 2, BONE_H)
	if glow is not None:
		pen.put(hx - 5, hy + 3, glow)
		pen.put(hx - 4, hy + 3, glow)


def sorc_arm(pen, sh, hand):
	el = ik(sh, hand, 4.2, 4.2, elbow_down)
	pen.line(sh[0], sh[1], el[0], el[1], CORRUPT[2])
	pen.line(el[0], el[1], hand[0], hand[1], CORRUPT[1])
	pen.put(hand[0], hand[1], BONE_L)
	pen.put(hand[0] - 1, hand[1], BONE_M)


def sorcerer_pose(i):
	if i < 4:
		return dict(bob=[0, 0, 1, 0][i], phase=[0.0, 0.9, 1.8, 2.7][i], sway=1.0, lean=0, hand=(-8, -13), lift=0,
		            stone=[1, 3, 2, 3][i], pulse=i % 2, eye=MAG[3], hood_dy=0)
	if i < 10:
		k = i - 4
		return dict(bob=k % 2, phase=k * 1.05, sway=1.8, lean=-1, hand=(-8, -13), lift=0,
		            stone=[1, 2, 3, 2, 1, 2][k], pulse=k % 2, eye=MAG[3], hood_dy=0)
	if i < 14:
		k = i - 10
		return dict(bob=0, phase=1 + k, sway=1.2, lean=-1, hand=(-8, [-17, -19, -20, -20][k]), lift=[1, 2, 3, 3][k],
		            stone=[2, 3, 4, 4][k], pulse=1, eye=MAG[4], hood_dy=-1, cast=k,
		            left_hand=[(-3, -14), (-4, -17), (-5, -19), (-5, -20)][k])
	if i < 17:
		k = i - 14
		return dict(bob=[1, 2, 1][k], phase=3 + k, sway=1.2, lean=[-2, -3, -1][k],
		            hand=RL_HAND[k], lift=0, stone=[4, 4, 2][k], pulse=1, eye=MAG[3],
		            hood_dy=[0, 1, 0][k], release=k)
	if i < 20:
		k = i - 17
		return dict(bob=0, phase=1 + k, sway=1.0, lean=[1, 2, 3][k], hand=[(0, -17), (2, -19), (3, -21)][k], lift=0,
		            stone=[3, 3, 4][k], pulse=0, eye=LILAC, hood_dy=0, swwind=k)
	if i < 24:
		k = i - 20
		return dict(bob=1, phase=2 + k, sway=1.4, lean=[-1, -2, -3, -2][k],
		            hand=SG_HAND[k], lift=0,
		            stone=[3, 3, 2, 1][k], pulse=0, eye=LILAC, hood_dy=1, swing=k)
	k = i - 24
	return dict(bob=0, phase=0.5 + k, sway=0.5, lean=[2, 1][k], hand=[(-3, -12), (-4, -13)][k], lift=0,
	            stone=1, pulse=0, eye=SOCKET, hood_dy=[-1, 0][k], hit=k, jolt=[2, 1][k])


SW_ANG = [115, 125, 135]
SG_HAND = [(-4, -17), (-8, -16), (-10, -13), (-9, -10)]
SG_ANG = [80, 25, -20, -40]
RL_HAND = [(-8, -14), (-9, -10), (-9, -11)]
RL_ANG = [70, -10, 90]
RL_BF = [(8, 12), (4, 14), (11, 17)]
SG_TIP = [(-4 - math.cos(math.radians(a)) * 14, h[1] - math.sin(math.radians(a)) * 14) for h, a in zip(SG_HAND, SG_ANG)]


def render_sorcerer(i):
	W, H, CX, GY = 40, 36, 20, 34
	if i >= 26:
		return sorc_death(i - 26)
	cv = Canvas(W, H)
	pen = Pen(cv, CX, GY)
	s = sorcerer_pose(i)
	jolt = s.get("jolt", 0)
	lean = s["lean"] + jolt
	bob = s["bob"]
	robe(pen, H=22 - bob, top_w=6, hem_w=15 - bob, sway=s["sway"], phase=s["phase"], lean=lean * 0.7, dx=jolt)
	hx = lean
	hood_y = -27 + bob + s["hood_dy"]
	sh = (-3 + hx, -19 + bob)
	hand = s["hand"]
	if "swwind" in s:
		k = s["swwind"]
		st_top = staff_hand(pen, s["hand"], SW_ANG[k], 4, 16, 0, i)
	elif "swing" in s:
		k = s["swing"]
		st_top = staff_hand(pen, s["hand"], SG_ANG[k], 6, 14, 0, i)
	elif "release" in s:
		k = s["release"]
		st_top = staff_hand(pen, s["hand"], RL_ANG[k], RL_BF[k][0], RL_BF[k][1], 1 if k == 2 else 0, i)
	else:
		st_top = staff(pen, (-9 + jolt, -s["lift"]), (-9 + jolt, -28 - s["lift"]), twist=1, phase=i)
	sorc_arm(pen, (sh[0] + 1, sh[1] + 2), hand)
	if "cast" in s:
		sorc_arm(pen, (sh[0] + 3, sh[1] + 3), s["left_hand"])
	hood_sorc(pen, 1 + hx, hood_y, glow=s["eye"])
	stone(pen, st_top, level=s["stone"], pulse=s["pulse"])
	cv = finish(cv)
	pen = Pen(cv, CX, GY)
	cx_, cy_ = st_top
	if "cast" in s:
		k = s["cast"]
		rad = [2, 3, 4, 4][k]
		for a in range(0, 360, 45 if k < 2 else 30):
			pen.put(cx_ + math.cos(math.radians(a)) * (rad + 1), cy_ + math.sin(math.radians(a)) * (rad + 1),
			        MAG[4] if (k >= 2 and a % 60 == 0) else MAG[3])
		pen.put(cx_, cy_ - rad - 1, (255, 232, 255, 255))
		for hnd in (s["hand"], s["left_hand"]):
			pen.put(hnd[0] - 1, hnd[1] - 1, MAG[3])
			if k >= 1:
				pen.put(hnd[0] + 1, hnd[1] - 1, MAG[4])
				pen.put(hnd[0], hnd[1] - 2, MAG[3])
	if "release" in s:
		k = s["release"]
		if k == 0:
			for a in range(0, 360, 40):
				pen.put(cx_ + math.cos(math.radians(a)) * 4, cy_ + math.sin(math.radians(a)) * 4, MAG[4])
		if k == 1:
			for a in range(0, 360, 30):
				r_ = 5 if a % 60 == 0 else 3
				pen.put(cx_ + math.cos(math.radians(a)) * r_, cy_ + math.sin(math.radians(a)) * r_,
				        (255, 232, 255, 255) if a % 60 == 0 else MAG[3])
			pen.put(cx_ - 4, 0, MAG[3])
			pen.put(cx_ + 3, -1, MAG[2])
		if k == 2:
			for a in (200, 240, 280, 320, 20, 160):
				pen.put(cx_ + math.cos(math.radians(a)) * 5, math.sin(math.radians(a)) * 2 - 1, MAG[2])
	if "swwind" in s:
		k = s["swwind"]
		pen.put(cx_, cy_ - 3, LILAC)
		pen.put(cx_ + 2, cy_ - 2, (244, 236, 255, 255))
		pen.put(cx_ - 2, cy_ - 2, LILAC)
		if k >= 1:
			pen.put(cx_ + 3, cy_ + 1, LILAC)
	if "swing" in s:
		k = s["swing"]
		if k in (1, 2):
			for t in range(10):
				u = t / 9.0
				hh = (SG_HAND[k - 1][0] + (SG_HAND[k][0] - SG_HAND[k - 1][0]) * u, SG_HAND[k - 1][1] + (SG_HAND[k][1] - SG_HAND[k - 1][1]) * u)
				an = math.radians(SG_ANG[k - 1] + (SG_ANG[k] - SG_ANG[k - 1]) * u)
				pen.put(hh[0] - math.cos(an) * 16, hh[1] - math.sin(an) * 16 - 1, LILAC if t % 2 == 0 else (244, 236, 255, 255))
		if k == 0:
			pen.put(1, -31, LILAC)
		if k == 3:
			pen.put(-17, 0, MAG[2])
			pen.put(-14, 1, MAG[1])
	if "hit" in s:
		k = s["hit"]
		pen.put(-8 + 4 * k, -28 - k, (240, 236, 250, 255))
		pen.put(-9 + 4 * k, -27 - k, LILAC)
	return cv


def sorc_death(k):
	W, H, CX, GY = 40, 36, 20, 34
	cv = Canvas(W, H)
	pen = Pen(cv, CX, GY)
	heights = [20, 16, 12, 9, 6, 4, 3, 3]
	wid = [15, 16, 17, 18, 18, 18, 18, 18]
	h = heights[k]
	st = [((-9, 0), (-12, -26)), ((-10, 0), (-17, -22)), ((-11, 0), (-21, -15)),
	      ((-12, 0), (-23, -8)), ((-12, -1), (-24, -3)), ((-12, -1), (-24, -1)),
	      ((-12, -1), (-24, -1)), ((-12, -1), (-24, -1))][k]
	top = staff(pen, st[0], st[1], twist=1 if k < 2 else 0, phase=k)
	robe(pen, H=h, top_w=max(6 - k, 3) if k < 5 else 8, hem_w=wid[k], sway=0.4, phase=k,
	     lean=[1, 2, 3, 3, 2, 1, 0, 0][k], dx=1 if k < 3 else 0)
	if k < 4:
		hood_sorc(pen, 1 + [0, 1, 2, 3][k], (-27 + (22 - h)) if k < 2 else (-h - 2), glow=MAG[3] if k < 2 else SOCKET)
	elif k == 4:
		hood_sorc(pen, 3, -9, glow=SOCKET)
	if k >= 5:
		pen.grid(-8 if k == 5 else -9, -3, MASK[:3], MASKPAL)
	stone(pen, top, level=[4, 4, 3, 3, 2, 1, 1, 1][k], pulse=k % 2)
	cv = finish(cv)
	pen = Pen(cv, CX, GY)
	rnd = random.Random(70 + k)
	if 0 < k:
		n = [0, 8, 10, 10, 8, 6, 4, 2][k]
		for _ in range(n):
			sx = rnd.randint(-9, 9)
			sy = max(-rnd.randint(2, 6 + k * 2), -(heights[k] + k * 2))
			col = CORRUPT[rnd.choice((1, 2, 3))]
			pen.put(sx, sy - (k if k < 6 else 0), alpha(col, 150 if k < 6 else 100))
	return cv


# ================================================================= VFX / PROJECTILES
def proj_bone_arrow():
	cv = Canvas(14, 5)
	for x in range(3, 12):
		cv.put(x, 2, BONE_H if x % 3 else BONE_L)
	for x in range(5, 11):
		cv.put(x, 3, BONE_D)
	cv.put(11, 1, BLADE[2])
	cv.put(11, 2, BLADE[0])
	cv.put(11, 3, BLADE[0])
	cv.put(12, 2, BLADE[1])
	cv.put(13, 2, BLADE[0])
	cv.put(12, 3, OUTLINE)
	cv.put(12, 1, OUTLINE)
	for (x, y, c) in [(0, 0, BONE_M), (1, 1, BONE_L), (2, 1, BONE_M), (0, 1, BONE_D), (1, 0, BONE_D),
	                  (0, 4, BONE_M), (1, 3, BONE_L), (2, 3, BONE_M), (1, 4, BONE_D), (0, 3, BONE_D),
	                  (2, 2, BONE_M), (3, 1, BONE_M), (3, 3, BONE_D), (1, 2, BONE_M), (0, 2, BONE_D)]:
		cv.put(x, y, c)
	return cv


def vfx_release():
	frames = []
	for f in range(4):
		cv = Canvas(16, 12)
		a = [230, 190, 130, 70][f]
		if f == 0:
			for x in range(0, 5):
				cv.put(x, 6, alpha(BONE_H, 240))
			cv.put(2, 5, alpha(BONE_H, 220))
			cv.put(2, 7, alpha(BONE_H, 220))
			cv.put(1, 4, alpha(GLOW_E[2], 200))
			cv.put(1, 8, alpha(GLOW_E[2], 200))
			cv.put(5, 6, alpha(BONE_L, 150))
		elif f == 1:
			for (x, y) in [(2, 6), (3, 5), (3, 7), (4, 6), (5, 4), (5, 8), (6, 6), (4, 4), (4, 8)]:
				cv.put(x, y, alpha(BONE_L, a))
			cv.put(7, 6, alpha(BONE_H, a - 40))
		elif f == 2:
			for (x, y) in [(5, 5), (6, 7), (7, 4), (8, 6), (9, 5), (6, 3), (7, 9), (8, 8), (10, 6)]:
				cv.put(x, y, alpha(BONE_M, a))
			cv.put(8, 7, alpha(BONE_L, a + 20))
		else:
			for (x, y) in [(8, 4), (10, 6), (11, 5), (9, 8), (12, 7), (7, 3)]:
				cv.put(x, y, alpha(BONE_M, a))
		frames.append(cv)
	return frames


def vfx_impact():
	frames = []
	shards = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1.4), (-1.4, 0), (1.4, 0.2)]
	for f in range(5):
		cv = Canvas(16, 16)
		cx, cy = 8, 8
		if f == 0:
			for r in range(-3, 4):
				cv.put(cx + r, cy, alpha(BONE_H, 240))
				cv.put(cx, cy + r, alpha(BONE_H, 220))
			cv.put(cx, cy, (255, 250, 232, 255))
			cv.put(cx - 1, cy - 1, alpha(GLOW_E[2], 200))
			cv.put(cx + 1, cy + 1, alpha(GLOW_E[2], 200))
		else:
			d = [0, 3, 5, 6, 7][f]
			for k, (sx, sy) in enumerate(shards):
				x = cx + sx * d * (0.9 if k % 2 else 1.1)
				y = cy + sy * d + (f * f * 0.3 if f > 2 else 0)
				if f <= 3:
					cv.put(x, y, BONE_L if k % 2 else BONE_H)
					cv.put(x + (1 if sx > 0 else -1), y, BONE_M)
				else:
					cv.put(x, y, alpha(BONE_M, 140))
			r = [0, 3, 4.5, 5.5, 6.5][f]
			a = [0, 170, 130, 90, 50][f]
			for ang in range(0, 360, 36):
				cv.put(cx + math.cos(math.radians(ang + f * 9)) * r, cy + math.sin(math.radians(ang + f * 9)) * r * 0.8,
				       alpha(BONE_D, a))
			if f <= 2:
				cv.put(cx, cy, alpha(BONE_H, 230 - f * 60))
		frames.append(cv)
	return frames


def _hash(x, y, f=0):
	return ((int(x) * 73856093) ^ (int(y) * 19349663) ^ (int(f) * 83492791)) & 0xFFFF


def vfx_blight_warning():
	W, H = 56, 40
	frames = []
	ccx, ccy = 28, 24  # contact circle: radius 24, centre 12 px above the ground point (28,36)
	for n in range(8):
		cv = Canvas(W, H)
		prog = n / 8.0
		a_rune = int(150 + 105 * prog)
		rune = alpha(mix(MAG[2], MAG[4], prog), a_rune)
		for x in range(4, 52):  # ground ellipse, exactly x 4..51
			t = (x - 27.5) / 23.5
			dy = 3.5 * math.sqrt(max(0.0, 1 - t * t))
			for y in (35.5 - dy, 35.5 + dy):
				cv.put(x, int(round(y)), rune)
		for x in range(10, 46):
			t = (x - 27.5) / 17.5
			dy = 2.0 * math.sqrt(max(0.0, 1 - t * t))
			if (x + n) % 3:
				cv.put(x, int(round(35.5 - dy)), alpha(MAG[1], int(a_rune * 0.8)))
				cv.put(x, int(round(35.5 + dy)), alpha(MAG[1], int(a_rune * 0.8)))
		for k in range(8):
			ang = (k / 8.0) * 2 * math.pi + n * 0.45
			cv.put(27.5 + math.cos(ang) * 20.5, 35.5 + math.sin(ang) * 2.6,
			       alpha(MAG[3] if k % 2 else SLIME_GREEN[3], a_rune))
		cv.put(28, 36, alpha(MAG[4], a_rune))
		cv.put(27, 36, alpha(MAG[3], a_rune))
		for (x, y) in ((4, 36), (51, 36), (4, 35), (51, 35)):
			cv.put(x, y, alpha(MAG[3], 255))
		arc_a = int(80 + 90 * prog)
		for deg in range(0, 361):
			ang = math.radians(deg)
			x = ccx + math.cos(ang) * 24
			y = ccy - math.sin(ang) * 24
			if y <= 36 and (deg % 3 != 2 or prog > 0.6):
				cv.put(x, y, alpha(MAG[3], arc_a))
		level = 36 - prog * 36 - 1
		for y in range(0, 36):
			if y < level:
				continue
			for x in range(W):
				if math.hypot(x - ccx, y - ccy) < 23.2:
					h = _hash(x, y, n)
					if y - level < 1.5:
						cv.put(x, y, alpha(MAG[3], 150))
					elif (x + y) % 2 == 0 and h % 5 < 1 + int(prog * 2.5):
						cv.put(x, y, alpha(MAG[1] if h % 3 else MAG[2], 70 + int(prog * 55)))
		for k in range(10):
			h = _hash(k, 3)
			px = 8 + (h % 40)
			speed = 5 + (h >> 4) % 5
			py = 34 - ((n * speed + (h >> 8) % 20) % 32)
			if math.hypot(px - ccx, py - ccy) < 22:
				col = MAG[4] if k % 3 == 0 else SLIME_GREEN[3] if k % 4 == 1 else MAG[3]
				cv.put(px, py, alpha(col, 220))
				if prog > 0.5 and k % 2 == 0:
					cv.put(px, py + 1, alpha(col, 120))
		frames.append(cv)
	return frames


def vfx_blight_explosion():
	W, H = 64, 56
	frames = []
	ccy = 40
	for f in range(7):
		cv = Canvas(W, H)
		rad = [8, 17, 24, 24, 22, 18, 12][f]
		colh = [34, 38, 34, 28, 22, 16, 10][f]
		fade = [255, 255, 245, 215, 160, 110, 70][f]
		colw = [3, 5, 9, 11, 10, 8, 6][f]
		for y in range(0, 53):
			for x in range(W):
				dx = x + 0.5 - 32
				dy = y + 0.5 - ccy
				d = math.hypot(dx, dy)
				h = _hash(x, y, f * 3 + 1)
				col = None
				in_col = abs(dx) <= colw * (0.6 + 0.4 * (y / 52.0)) and (52 - y) <= colh
				in_dome = d <= rad and dy <= 12
				if f <= 3:
					if in_dome and d >= rad - 2.2:
						col = MAG[3] if h % 3 else MAG[4]
					elif in_dome and d >= rad - 6:
						col = MAG[2] if h % 4 else SLIME_GREEN[2]
					elif in_dome:
						col = MAG[1] if (h % 7) < 3 else (SLIME_GREEN[1] if h % 5 == 0 else MAG[2])
					if in_col and abs(dx) <= colw * 0.4:
						col = (255, 236, 255, 255) if abs(dx) <= colw * 0.2 else MAG[4]
					elif in_col and col is None:
						col = MAG[3] if h % 2 else SLIME_GREEN[3]
					if col is not None and f >= 2 and d > rad - 1.2 and h % 3 == 0:
						col = None
					if col is not None and in_dome and f == 3 and h % 4 == 0 and d < rad - 3:
						col = None
				else:
					rise = (f - 3) * 5
					sd = math.hypot(dx * 0.9, (dy + rise) * 1.1)
					if sd <= rad and dy <= 12 and (h % 100) < 62 - (f - 4) * 14 and (x + y) % 2 == 0:
						col = mix(CORRUPT[1], CORRUPT[3], (h % 5) / 8.0)
						if h % 9 == 0:
							col = SLIME_GREEN[1]
					if f == 4 and in_col and abs(dx) <= 3 and h % 3:
						col = MAG[2]
				if col is not None:
					cv.put(x, y, alpha(col, 255 if f <= 3 else fade))
		for x in range(8, 57):
			if f <= 3:
				cv.put(x, 52, alpha(MAG[3], 220 - f * 30))
		for k in range(10):
			h = _hash(k, f, 9)
			ang = h % 360
			r = 6 + (h >> 3) % 20 + f * 2
			x = 32 + math.cos(math.radians(ang)) * r
			y = 44 - abs(math.sin(math.radians(ang))) * (r * 0.8) - f
			if f <= 5 and y < 52:
				cv.put(x, y, alpha(MAG[4] if k % 2 else SLIME_GREEN[3], 230 if f < 4 else 150))
		frames.append(cv)
	return frames


def vfx_blight_cast():
	frames = []
	c = 8
	for f in range(5):
		cv = Canvas(16, 16)
		if f == 0:
			cv.put(c, c, (255, 240, 255, 255))
			for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
				cv.put(c + dx, c + dy, alpha(MAG[4], 230))
			cv.put(c + 1, c + 1, alpha(MAG[3], 200))
			cv.put(c - 1, c - 1, alpha(MAG[3], 200))
		elif f == 1:
			for r in range(1, 5):
				for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
					cv.put(c + dx * r, c + dy * r, alpha(MAG[4] if r < 3 else MAG[3], 230 - r * 30))
			cv.put(c, c, (255, 240, 255, 255))
			cv.put(c + 1, c + 1, alpha(SLIME_GREEN[3], 220))
			cv.put(c - 2, c - 2, alpha(MAG[3], 200))
			cv.put(c + 2, c + 2, alpha(MAG[3], 200))
		elif f == 2:
			for ang in range(0, 360, 30):
				cv.put(c + math.cos(math.radians(ang)) * 5, c + math.sin(math.radians(ang)) * 5, alpha(MAG[3], 210))
			for ang in range(15, 360, 90):
				cv.put(c + math.cos(math.radians(ang)) * 3, c + math.sin(math.radians(ang)) * 3, alpha(MAG[4], 230))
			cv.put(c, c, alpha(MAG[4], 240))
			cv.put(c + 4, c - 3, alpha(SLIME_GREEN[3], 220))
			cv.put(c - 4, c + 3, alpha(SLIME_GREEN[2], 200))
		elif f == 3:
			for ang in range(10, 360, 50):
				cv.put(c + math.cos(math.radians(ang)) * 6.5, c + math.sin(math.radians(ang)) * 6.5, alpha(MAG[3], 170))
			for ang in range(35, 360, 90):
				cv.put(c + math.cos(math.radians(ang)) * 4, c + math.sin(math.radians(ang)) * 4, alpha(MAG[4], 200))
			cv.put(c, c - 1, alpha(MAG[3], 150))
		else:
			for ang in range(20, 360, 60):
				cv.put(c + math.cos(math.radians(ang)) * 7, c + math.sin(math.radians(ang)) * 7, alpha(MAG[2], 100))
			cv.put(c, c, alpha(MAG[3], 70))
		frames.append(cv)
	return frames


# ================================================================= build
SPECS = {
	"skeleton_warrior.png": (48, 32, 27),
	"skeleton_archer.png": (40, 32, 26),
	"blight_sorcerer.png": (40, 36, 34),
	"proj_bone_arrow.png": (14, 5, 1),
	"vfx_bone_arrow_release.png": (16, 12, 4),
	"vfx_bone_arrow_impact.png": (16, 16, 5),
	"vfx_blight_warning.png": (56, 40, 8),
	"vfx_blight_explosion.png": (64, 56, 7),
	"vfx_blight_cast.png": (16, 16, 5),
}


def build_all():
	return {
		"skeleton_warrior.png": [render_warrior(i) for i in range(27)],
		"skeleton_archer.png": [render_archer(i) for i in range(26)],
		"blight_sorcerer.png": [render_sorcerer(i) for i in range(34)],
		"proj_bone_arrow.png": [proj_bone_arrow()],
		"vfx_bone_arrow_release.png": vfx_release(),
		"vfx_bone_arrow_impact.png": vfx_impact(),
		"vfx_blight_warning.png": vfx_blight_warning(),
		"vfx_blight_explosion.png": vfx_blight_explosion(),
		"vfx_blight_cast.png": vfx_blight_cast(),
	}


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--preview", metavar="DIR", default=None)
	args = ap.parse_args()
	all_frames = build_all()
	os.makedirs(OUT_DIR, exist_ok=True)
	for name, frames in all_frames.items():
		w, h, n = SPECS[name]
		assert len(frames) == n, (name, len(frames), n)
		for f in frames:
			assert (f.w, f.h) == (w, h), (name, f.w, f.h)
		save_png(sheet(frames, n), os.path.join(OUT_DIR, name))
	print("wrote %d PNG to %s" % (len(all_frames), OUT_DIR))
	if args.preview:
		os.makedirs(args.preview, exist_ok=True)
		bg = (40, 44, 52, 255)
		for name, frames in all_frames.items():
			cols = 9 if name.startswith(("skeleton", "blight_sorcerer")) else 4 if name.startswith("vfx_blight_") and len(frames) > 5 else len(frames)
			pad = []
			for f in frames:
				c = Canvas(f.w + 1, f.h + 1)
				c.blit(f, 0, 0)
				for x in range(c.w):
					c.put(x, f.h, (70, 76, 90, 255))
				for y in range(c.h):
					c.put(f.w, y, (70, 76, 90, 255))
				pad.append(c)
			save_png(sheet(pad, cols), os.path.join(args.preview, name.replace(".png", "_x4.png")), scale=4, background=bg)


if __name__ == "__main__":
	main()

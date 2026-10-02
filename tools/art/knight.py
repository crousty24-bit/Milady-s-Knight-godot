"""Generate the Ashen Knight spritesheet, its three-move sword chain and VFX.

Usage: python3 tools/art/knight.py [--preview DIR]

RUN-029 rig. Every frame is posed on a small skeleton (hip, torso lean, two-bone
IK legs and arms, sword angle, cape ribbon) and rasterised as pixel art with a
shared light, selective outlines and the project ramps (steel plate, mail,
charcoal tabard with a gold emblem, red cape and mantle). Frames are 64x64,
facing right, feet on row 60 (ground line y=0 is the bottom edge of that row)
and body centred on column 32: `player.tscn` places the sprite at (0, -29).

Game coordinates below are relative to the feet, +x forward, +y down. The
gameplay sword pivot is the hand at (+4, -10); during the contact window every
move draws the blade at the exact gameplay angle lerp(-1.5, 1.2, progress).

Animations written to ashen_knight_frames.tres:
  full body: idle (combat guard), run, rise, fall, land, wall, hurt, dead,
             atk1/atk2/atk3 (10 frames: 6 gesture + 4 chain while F is held)
  layered:   up1/up2/up3 (upper body of the same attack frames) drawn over
             base_run / base_rise / base_fall (legs, tabard skirt and cape)
             when the knight attacks while running or airborne.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, hexc, save_png, sheet  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")

FRAME = 64
OX, OY = 32, 61  # game (0, 0) = bottom-centre of the feet

OUTLINE = hexc("17131b")
STEEL = [hexc(c) for c in ("2b303b", "48505f", "737c8c", "a6aebb", "dde2e8")]
STEEL_DEEP = hexc("20232c")
MAIL = [hexc(c) for c in ("23262e", "33384a", "4a5163", "646c7e")]
CLOTH = [hexc(c) for c in ("221c20", "342b2f", "4b3f43", "66575a")]
RED = [hexc(c) for c in ("3f0c13", "741620", "a8242c", "d8423a")]
GOLD = [hexc(c) for c in ("4a3418", "8c6b2e", "c9a24a", "f0d27a", "fff4c4")]
LEATHER = [hexc(c) for c in ("2a1f1a", "3f2e24", "5a4030", "7a5a3c")]
VISOR = hexc("0a080c")
BLADE = [hexc(c) for c in ("5d6676", "8d96a6", "c4cbd6", "eef1f5", "ffffff")]

LIGHT = (0.5, -0.65, 0.57)
_n = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _n for c in LIGHT)

THIGH, SHIN = 6.9, 6.6
UPPER_ARM, FOREARM = 4.8, 4.6
SWORD_REACH = 24.0
HIP_REF = -14  # hip height of the layered upper-body frames


def gameplay_angle(progress):
	return -1.5 + 2.7 * progress


# ---------------------------------------------------------------- raster helpers
def pix_center(ix, iy):
	return ix + 0.5 - OX, iy + 0.5 - OY


def lum(nx, ny, nz):
	return nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]


def tone(ramp, v, bias=0, cuts=None):
	"""Pick a ramp colour from a lighting value in [-1, 1]."""
	if cuts is None:
		cuts = {5: (-0.05, 0.36, 0.64, 0.88), 4: (0.0, 0.42, 0.78), 6: (-0.1, 0.25, 0.5, 0.72, 0.9)}[len(ramp)]
	i = 0
	while i < len(cuts) and v >= cuts[i]:
		i += 1
	return ramp[max(0, min(len(ramp) - 1, i + bias))]


def bounds(points, pad):
	xs = [p[0] for p in points]
	ys = [p[1] for p in points]
	x0 = max(0, int(math.floor(min(xs) - pad + OX)))
	x1 = min(FRAME - 1, int(math.ceil(max(xs) + pad + OX)))
	y0 = max(0, int(math.floor(min(ys) - pad + OY)))
	y1 = min(FRAME - 1, int(math.ceil(max(ys) + pad + OY)))
	return x0, x1, y0, y1


def capsule(a, b, r0, r1, colorer):
	"""Tapered capsule from a to b; colorer(nx, ny, nz, t, ix, iy) -> colour."""
	out = {}
	ax, ay = a
	bx, by = b
	dx, dy = bx - ax, by - ay
	ll = dx * dx + dy * dy or 1e-9
	x0, x1, y0, y1 = bounds([a, b], max(r0, r1) + 1)
	for iy in range(y0, y1 + 1):
		for ix in range(x0, x1 + 1):
			px, py = pix_center(ix, iy)
			t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / ll))
			cx, cy = ax + dx * t, ay + dy * t
			r = r0 + (r1 - r0) * t
			ox, oy = px - cx, py - cy
			d = math.hypot(ox, oy)
			if d <= r:
				nx, ny = ox / r, oy / r
				nz = math.sqrt(max(0.0, 1.0 - nx * nx - ny * ny))
				c = colorer(nx, ny, nz, t, ix, iy)
				if c is not None:
					out[(ix, iy)] = c
	return out


def disc(c, r, colorer):
	return capsule(c, (c[0] + 0.001, c[1]), r, r, colorer)


def steel_shader(bias=0, ramp=STEEL):
	return lambda nx, ny, nz, t, ix, iy: tone(ramp, lum(nx, ny, nz), bias)


def mail_shader(bias=0):
	def f(nx, ny, nz, t, ix, iy):
		v = lum(nx, ny, nz)
		i = MAIL.index(tone(MAIL, v, bias))
		if (ix + iy) % 2 == 0:
			i = max(0, i - 1)
		return MAIL[i]
	return f


def stamp(text, palette, origin):
	"""Hand-drawn grid placed with its top-left pixel at a game position."""
	out = {}
	ox = int(math.floor(origin[0] + OX))
	oy = int(math.floor(origin[1] + OY))
	rows = text.strip("\n").split("\n")
	ind = min(len(r) - len(r.lstrip("\t")) for r in rows if r.strip())
	for y, row in enumerate(rows):
		for x, ch in enumerate(row[ind:]):
			if ch in palette and 0 <= ox + x < FRAME and 0 <= oy + y < FRAME:
				out[(ox + x, oy + y)] = palette[ch]
	return out


# ---------------------------------------------------------------- compositor
class Frame:
	"""Parts painted back to front; each part gets a 1 px contour that is the
	dark outline on empty space and a softer inner line over earlier parts."""

	def __init__(self):
		self.px = {}
		self.edge = set()
		self.owner = {}
		self.n = 0

	def add(self, pixels, inner=None, outline=True):
		if not pixels:
			return
		idx = self.n
		self.n += 1
		for q, c in pixels.items():
			self.px[q] = c
			self.owner[q] = idx
			self.edge.discard(q)
		if not outline:
			return
		ring = set()
		for (x, y) in pixels:
			for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
				q = (x + dx, y + dy)
				if q not in pixels and 0 <= q[0] < FRAME and 0 <= q[1] < FRAME:
					ring.add(q)
		for q in ring:
			if q not in self.px:
				self.px[q] = OUTLINE
				self.edge.add(q)
				self.owner[q] = idx
			elif q not in self.edge and inner is not None and self.owner[q] != idx:
				self.px[q] = inner
				self.owner[q] = idx

	def canvas(self):
		c = Canvas(FRAME, FRAME)
		for (x, y), col in self.px.items():
			if y < OY:  # nothing below the ground line
				c.put(x, y, col)
		return c


# ---------------------------------------------------------------- skeleton
def ik(root, target, l1, l2, prefer):
	"""Two-bone IK; returns the middle joint on the side of `prefer`."""
	dx, dy = target[0] - root[0], target[1] - root[1]
	d = math.hypot(dx, dy)
	d = max(0.5, min(d, l1 + l2 - 0.05))
	ux, uy = dx / (math.hypot(dx, dy) or 1), dy / (math.hypot(dx, dy) or 1)
	end = (root[0] + ux * d, root[1] + uy * d)
	ca = max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
	a = math.acos(ca)
	best = None
	for s in (1, -1):
		cs, sn = math.cos(a * s), math.sin(a * s)
		jx = root[0] + (ux * cs - uy * sn) * l1
		jy = root[1] + (ux * sn + uy * cs) * l1
		score = jx * prefer[0] + jy * prefer[1]
		if best is None or score > best[0]:
			best = (score, (jx, jy))
	return best[1], end


def rot(v, a):
	c, s = math.cos(a), math.sin(a)
	return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def add(a, b, k=1.0):
	return (a[0] + b[0] * k, a[1] + b[1] * k)


class Pose:
	def __init__(self, **kw):
		self.hip = (0.5, -13)
		self.lean = 0.1
		self.head = "normal"
		self.head_off = (0, 0)
		self.near_foot = (4.5, -2)
		self.far_foot = (-4.5, -2)
		self.near_toe = 0.0
		self.far_toe = 0.0
		self.near_hand = (5, -12)
		self.far_hand = (2, -12)
		self.two_hands = False
		self.sword = -0.9
		self.sword_behind = False
		self.cape = [(-2, 5), (-4, 11), (-5, 16)]
		self.smear = None
		self.dust = None
		self.dropped_sword = None
		self.lying = False
		self.far_arm_front = False
		self.sword_far = False  # sword held by the far hand, behind the body
		self.__dict__.update(kw)

	def copy(self, **kw):
		p = Pose()
		p.__dict__.update(self.__dict__)
		p.__dict__.update(kw)
		return p


# ---------------------------------------------------------------- hand-drawn parts
HELM_PAL = {"o": OUTLINE, "1": STEEL[0], "2": STEEL[1], "3": STEEL[2], "4": STEEL[3], "5": STEEL[4], "v": VISOR, "d": STEEL_DEEP, "r": RED[1], "R": RED[2]}
# Great helm in three-quarter view, face plate on the right. 10 x 10.
HELM = """
..oooo...
.o34455o.
o2344555o
o1234oooooo
o123ovvvvo
o1234o545o
o12234444o
.o122333o.
..oo222o..
"""
HELM_DOWN = """
.........
..oooo...
.o34455o.
o2344555oo
o1234ooooo
o123ovvvvo
o12234545o
.o122343o.
..oo222o..
"""
HELM_UP = """
.oooo....
o34455oo.
o2344555o
o1234oooo
o123ovvvoo
o1234o454o
o12234444o
.o122333o.
..oo222o..
"""
HELMS = {"normal": HELM, "down": HELM_DOWN, "up": HELM_UP}

PAULDRON = """
.ooo..
o3445o
o23445o
o12334o
.o122o.
..ooo..
"""
PAULDRON_FAR = """
.ooo.
o2334o
o12233o
.oooo.
"""


# ---------------------------------------------------------------- body parts
def draw_leg(f, hip, foot, toe, far):
	bias = -1 if far else 0
	root = add(hip, (-0.6 if far else 0.7, 0.2))
	knee, ankle = ik(root, foot, THIGH, SHIN, (1.0, -0.15))
	toe_tip = add(ankle, (math.cos(toe) * 3.2, math.sin(toe) * 3.2))
	inner = STEEL_DEEP
	f.add(capsule(root, knee, 1.8, 1.5, mail_shader(bias)), inner)
	f.add(capsule(knee, ankle, 1.5, 1.2, steel_shader(bias)), inner)
	f.add(capsule(add(ankle, (-0.4, 0.3)), toe_tip, 1.15, 0.9, steel_shader(bias)), inner)
	f.add(disc(add(knee, (0.5, -0.1)), 1.05, steel_shader(bias + 1)), inner)
	return knee, ankle


def torso_frame(p):
	up = (math.sin(p.lean), -math.cos(p.lean))
	fwd = (math.cos(p.lean), math.sin(p.lean))
	return up, fwd


def neck_of(p):
	up, _ = torso_frame(p)
	return add(p.hip, up, 9.0)


def shoulders(p):
	up, fwd = torso_frame(p)
	n = neck_of(p)
	near = add(add(n, up, -2.0), fwd, 0.4)
	far = add(add(n, up, -2.2), fwd, -2.0)
	return near, far


# back/front profile of the torso (v across, u up from the hip)
def torso_profile(u):
	if u < 0 or u > 9.6:
		return None
	back = -3.2 + (0.3 if u > 6 else 0) - (0.4 if u < 2 else 0)
	if u < 2.0:
		front = 2.6 + u * 0.2
	elif u < 7.0:
		front = 3.0 + (u - 2.0) * 0.22
	else:
		front = 4.1 - (u - 7.0) * 0.9
	if u > 8.4:
		back += (u - 8.4) * 1.3
	return back, front


def draw_torso(f, p):
	up, fwd = torso_frame(p)
	pts = [add(p.hip, up, 10), add(p.hip, fwd, -4), add(p.hip, fwd, 5), add(add(p.hip, up, 10), fwd, 5)]
	x0, x1, y0, y1 = bounds(pts, 2)
	out = {}
	for iy in range(y0, y1 + 1):
		for ix in range(x0, x1 + 1):
			px, py = pix_center(ix, iy)
			rx, ry = px - p.hip[0], py - p.hip[1]
			u = rx * up[0] + ry * up[1]
			v = rx * fwd[0] + ry * fwd[1]
			prof = torso_profile(u)
			if prof is None or not (prof[0] <= v <= prof[1]):
				continue
			mid = (prof[0] + prof[1]) * 0.5
			half = (prof[1] - prof[0]) * 0.5
			nxl = max(-1.0, min(1.0, (v - mid) / half))
			nyl = -0.45 if u > 8.0 else (0.25 if u < 1.0 else 0.0)
			nzl = math.sqrt(max(0.0, 1 - nxl * nxl - nyl * nyl))
			# local (forward, up) -> screen
			nx = nxl * fwd[0] - nyl * up[0] * -1
			ny = nxl * fwd[1] + nyl * -up[1] * -1
			light = lum(nx, ny, nzl)
			if u > 8.3:
				col = tone(STEEL, light)  # gorget
			elif 1.1 <= u <= 2.3:
				col = tone(LEATHER, light)
				if prof[1] - 2.2 <= v <= prof[1] - 0.8:
					col = GOLD[3] if u > 1.7 else GOLD[2]
			else:
				col = tone(CLOTH, light + 0.15)
				# vertical fold lines on the tabard
				if u < 1.1 and int(math.floor(v + 10)) % 3 == 0:
					col = CLOTH[max(0, CLOTH.index(col) - 1)]
			out[(ix, iy)] = col
	# gold emblem on the chest: a small rampant mark
	emblem = [(2.0, 7.0, 3), (3.0, 7.0, 4), (2.5, 6.0, 3), (1.5, 5.6, 2), (3.5, 5.6, 3), (2.5, 5.0, 2), (2.5, 4.0, 2), (1.7, 3.4, 1), (3.3, 3.4, 2)]
	for ev, eu, gi in emblem:
		ex, ey = add(add(p.hip, up, eu), fwd, ev)
		q = (int(math.floor(ex + OX)), int(math.floor(ey + OY)))
		if q in out:
			out[q] = GOLD[gi]
	f.add(out, CLOTH[0])


def draw_skirt(f, p, knees):
	"""Tabard skirt from the belt over the thighs; corners follow the knees."""
	up, fwd = torso_frame(p)
	top_b = add(add(p.hip, up, 1.2), fwd, -3.4)
	top_f = add(add(p.hip, up, 1.2), fwd, 3.2)
	kx = [k[0] for k in knees]
	hem_y = max(p.hip[1] + 3.6, min(k[1] for k in knees) - 1.5)
	hem_b = (min(min(kx) - 0.5, top_b[0] - 0.5), hem_y)
	hem_f = (max(max(kx) + 0.8, top_f[0] + 0.3), hem_y + 0.5)
	poly = [top_b, top_f, hem_f, hem_b]
	x0, x1, y0, y1 = bounds(poly, 1)
	out = {}

	def inside(px, py):
		sign = 0
		for i in range(4):
			ax, ay = poly[i]
			bx, by = poly[(i + 1) % 4]
			c = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
			if c != 0:
				if sign == 0:
					sign = 1 if c > 0 else -1
				elif (c > 0) != (sign > 0):
					return False
		return True

	for iy in range(y0, y1 + 1):
		for ix in range(x0, x1 + 1):
			px, py = pix_center(ix, iy)
			if not inside(px, py):
				continue
			span = (px - hem_b[0]) / max(1.0, hem_f[0] - hem_b[0])
			col = CLOTH[2] if span > 0.62 else CLOTH[1]
			if (ix % 3) == 0:
				col = CLOTH[max(0, CLOTH.index(col) - 1)]
			if py > hem_y - 1.0:
				col = RED[1] if (ix % 2 == 0) else RED[0]  # dark red hem trim
			out[(ix, iy)] = col
	f.add(out, CLOTH[0])


def draw_arm(f, shoulder, hand, far, bias_extra=0):
	bias = (-1 if far else 0) + bias_extra
	elbow, wrist = ik(shoulder, hand, UPPER_ARM, FOREARM, (-0.55, 0.8))
	f.add(capsule(shoulder, elbow, 1.45, 1.25, mail_shader(bias)), STEEL_DEEP)
	f.add(capsule(elbow, wrist, 1.25, 1.5, steel_shader(bias)), STEEL_DEEP)
	return elbow, wrist


def draw_hand(f, hand, far):
	bias = -1 if far else 0
	f.add(disc(hand, 1.35, steel_shader(bias)), STEEL_DEEP)


def draw_head(f, p):
	n = neck_of(p)
	up, fwd = torso_frame(p)
	c = add(add(n, up, 0.6), fwd, 0.6)
	text = HELMS[p.head]
	origin = (c[0] - 4.0 + p.head_off[0], c[1] - 8.6 + p.head_off[1])
	f.add(stamp(text, HELM_PAL, origin), outline=False)


def draw_collar(f, p):
	near, far = shoulders(p)
	up, fwd = torso_frame(p)
	a = add(add(far, up, 1.0), fwd, -0.5)
	b = add(add(near, up, 1.3), fwd, 0.3)
	f.add(capsule(a, b, 2.1, 1.7, lambda nx, ny, nz, t, ix, iy: tone(RED, lum(nx, ny, nz) + 0.05)), RED[0])


def draw_pauldron(f, p, near_side):
	near, far = shoulders(p)
	if near_side:
		f.add(stamp(PAULDRON, HELM_PAL, (near[0] - 3.6, near[1] - 2.0)), outline=False)
	else:
		f.add(stamp(PAULDRON_FAR, HELM_PAL, (far[0] - 3.2, far[1] - 1.8)), outline=False)


def cape_anchor(p):
	n = neck_of(p)
	up, fwd = torso_frame(p)
	return add(add(n, up, -1.6), fwd, -2.6)


def draw_cape(f, p, anchor=None):
	"""Ribbon through the anchor and three trailing points, tattered hem."""
	a = anchor or cape_anchor(p)
	pts = [a] + [add(a, d) for d in p.cape]
	# resample the polyline
	samples = []
	for i in range(len(pts) - 1):
		for k in range(12):
			t = k / 12
			samples.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t))
	samples.append(pts[-1])
	lengths = [0.0]
	for i in range(1, len(samples)):
		lengths.append(lengths[-1] + math.hypot(samples[i][0] - samples[i - 1][0], samples[i][1] - samples[i - 1][1]))
	total = lengths[-1] or 1
	x0, x1, y0, y1 = bounds(samples, 6)
	out = {}
	for iy in range(y0, y1 + 1):
		for ix in range(x0, x1 + 1):
			px, py = pix_center(ix, iy)
			best = None
			for i in range(len(samples) - 1):
				ax, ay = samples[i]
				bx, by = samples[i + 1]
				dx, dy = bx - ax, by - ay
				ll = dx * dx + dy * dy or 1e-9
				t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / ll))
				cx, cy = ax + dx * t, ay + dy * t
				dd = (px - cx) ** 2 + (py - cy) ** 2
				if best is None or dd < best[0]:
					side = 1 if (dx * (py - ay) - dy * (px - ax)) > 0 else -1
					best = (dd, (lengths[i] + math.sqrt(ll) * t) / total, side * math.sqrt(dd), i == len(samples) - 2 and t >= 1.0)
			dd, s, lat, past_end = best
			if past_end:
				continue
			w = 2.0 + 2.6 * s
			if abs(lat) > w:
				continue
			# tattered hem: notches along the last part
			if s > 0.86:
				notch = (int(math.floor(lat + 20)) * 7) % 5
				if s > 0.9 + notch * 0.025:
					continue
			fold = math.sin(lat * 1.9 + s * 4.0)
			k = 1
			if fold > 0.55:
				k = 2
			elif fold < -0.6:
				k = 0
			if s < 0.1:
				k = 0
			if abs(lat) > w - 0.9 and lat * (1 if p.cape[-1][0] < 0 else -1) < 0 and s > 0.15:
				k = min(3, k + 1)
			out[(ix, iy)] = RED[k]
	f.add(out, RED[0])


def draw_sword(f, hand, angle, inner=STEEL_DEEP):
	d = (math.cos(angle), math.sin(angle))
	n = (-d[1], d[0])
	lit_side = 1 if (n[0] * LIGHT[0] + n[1] * LIGHT[1]) > 0 else -1
	out = {}

	def plot(x, y, col):
		q = (int(math.floor(x + OX)), int(math.floor(y + OY)))
		if 0 <= q[0] < FRAME and 0 <= q[1] < FRAME:
			out[q] = col

	steps = 120
	for i in range(steps + 1):
		t = -3.4 + (SWORD_REACH + 3.4) * i / steps
		x, y = hand[0] + d[0] * t, hand[1] + d[1] * t
		if t < -2.6:
			plot(x, y, GOLD[2])  # pommel
		elif t < 1.0:
			plot(x, y, LEATHER[2])  # grip
		elif t < 2.2:
			for s in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5):
				plot(x + n[0] * s, y + n[1] * s, GOLD[3] if s * lit_side > 0 else GOLD[1])
		else:
			tip = t > SWORD_REACH - 1.5
			plot(x, y, BLADE[4] if tip else BLADE[3])
			plot(x + n[0] * 0.9 * -lit_side, y + n[1] * 0.9 * -lit_side, BLADE[1])
	f.add(out, inner)


def draw_smear(f, hand, a0, a1, heavy=False):
	"""Crescent from a0 to a1 around the hand; brightest at the leading edge."""
	out = {}
	span = a1 - a0
	if abs(span) < 0.05:
		return
	r_out = SWORD_REACH + 0.6
	x0, x1, y0, y1 = bounds([hand], r_out + 2)
	for iy in range(y0, y1 + 1):
		for ix in range(x0, x1 + 1):
			px, py = pix_center(ix, iy)
			dx, dy = px - hand[0], py - hand[1]
			r = math.hypot(dx, dy)
			if r < 7.0 or r > r_out:
				continue
			ang = math.atan2(dy, dx)
			rel = (ang - a0) % math.tau if span > 0 else (a0 - ang) % math.tau
			if rel > abs(span):
				continue
			lead = rel / abs(span)
			thick = (2.0 if not heavy else 3.0) + (6.5 if not heavy else 9.0) * lead * lead
			if r < r_out - thick:
				continue
			k = lead * (0.55 + 0.45 * (r - (r_out - thick)) / thick)
			if k > 0.72:
				col = hexc("fffbe8")
			elif k > 0.45:
				col = hexc("f2e2a8")
			elif k > 0.24:
				col = hexc("c9b98a")
			elif k > 0.1:
				col = hexc("8f98aa")
			else:
				continue
			out[(ix, iy)] = col
	f.add(out, outline=False)


def draw_dust(f, at, stage):
	"""Ground impact puffs at a game point, stage 0..2."""
	out = {}
	cols = [hexc("d9cfb8"), hexc("a89e88"), hexc("7a7262")]
	spread = 3 + stage * 3
	for k in range(-3, 4):
		x = at[0] + k * spread / 3.0
		h = (3 - abs(k)) * (1.4 - stage * 0.35)
		for j in range(int(h) + 1):
			y = at[1] - 1 - j - (stage if abs(k) > 1 else 0)
			if (k + j + stage) % 2 == 0 or stage == 0:
				q = (int(math.floor(x + OX)), int(math.floor(y + OY)))
				out[q] = cols[min(2, stage + (1 if j > 1 else 0))]
	f.add(out, outline=False)


def draw_dropped_sword(f, spec):
	hand, angle = spec
	draw_sword(f, hand, angle)


# ---------------------------------------------------------------- full render
def render(p, layer="full"):
	"""layer: full | base (legs, skirt, cape) | upper (torso, head, arms, sword)."""
	f = Frame()
	base = layer in ("full", "base")
	upper = layer in ("full", "upper")
	near_sh, far_sh = shoulders(p)
	if base:
		draw_cape(f, p)
	if p.dropped_sword is not None and base:
		draw_dropped_sword(f, p.dropped_sword)
	far_hand = p.far_hand
	if p.two_hands and p.sword is not None:
		far_hand = add(p.near_hand, (math.cos(p.sword), math.sin(p.sword)), -2.6)
	if upper and not p.far_arm_front:
		draw_arm(f, far_sh, far_hand, True)
		if p.sword_far and p.sword is not None:
			draw_sword(f, far_hand, p.sword)
		draw_hand(f, far_hand, True)
	if upper:
		draw_pauldron(f, p, False)
		if p.sword is not None and p.sword_behind and not p.sword_far:
			draw_sword(f, p.near_hand, p.sword)
	knees = []
	if base:
		k1, _ = draw_leg(f, p.hip, p.far_foot, p.far_toe, True)
		k2, _ = draw_leg(f, p.hip, p.near_foot, p.near_toe, False)
		knees = [k1, k2]
		draw_skirt(f, p, knees)
	if upper:
		draw_torso(f, p)
		draw_collar(f, p)
		draw_head(f, p)
		if p.far_arm_front:
			draw_arm(f, far_sh, far_hand, True)
			draw_hand(f, far_hand, True)
		if p.smear is not None:
			a0, a1, heavy = p.smear
			draw_smear(f, p.near_hand, a0, a1, heavy)
		draw_arm(f, near_sh, p.near_hand, False)
		draw_pauldron(f, p, True)
		if p.sword is not None and not p.sword_behind and not p.sword_far:
			draw_sword(f, p.near_hand, p.sword)
		draw_hand(f, p.near_hand, False)
	if p.dust is not None and (layer == "full" or layer == "upper"):
		draw_dust(f, p.dust[0], p.dust[1])
	return f.canvas()


def shifted_upper(p):
	"""Upper body for the layered frames: hip moved to the reference height."""
	target = (0.5 + 0.35 * (p.hip[0] - 0.5), HIP_REF)
	d = (target[0] - p.hip[0], target[1] - p.hip[1])
	q = p.copy(hip=target, near_hand=add(p.near_hand, d), far_hand=add(p.far_hand, d))
	if q.dust is not None:
		q.dust = None
	return q


# ---------------------------------------------------------------- poses
def guard(bob=0, sway=0, tip=0.0):
	return Pose(hip=(0.5, -13 + bob), lean=0.14, near_foot=(5, -2), far_foot=(-4.5, -2), far_toe=0.0,
		near_hand=(6.0, -14.5 + bob), two_hands=True, sword=-0.82 + tip,
		cape=[(-2.2 + sway * 0.3, 5), (-4.0 + sway, 10.5), (-5.2 + sway, 15.5)])


def idle_frames():
	seq = [(0, 0, 0.0), (0, 1, 0.0), (1, 1, 0.03), (1, 0, 0.05), (1, -1, 0.03), (0, -1, 0.0)]
	return [guard(b, s, t) for b, s, t in seq]


RUN_CYCLE = [
	# near foot, far foot, near toe, far toe, hip y, arm phase
	((6.5, -2), (-6.0, -5.5), 0.0, 0.9, -14, -1.0),
	((2.5, -2), (-5.0, -8.5), 0.0, 1.0, -13, -0.5),
	((-1.5, -2), (1.0, -7.5), 0.2, 0.5, -14, 0.3),
	((-5.5, -3.5), (5.0, -5.0), 0.9, 0.0, -15, 1.0),
	((-6.0, -5.5), (6.5, -2), 0.9, 0.0, -14, 1.0),
	((-5.0, -8.5), (2.5, -2), 1.0, 0.0, -13, 0.5),
	((1.0, -7.5), (-1.5, -2), 0.5, 0.2, -14, -0.3),
	((5.0, -5.0), (-5.5, -3.5), 0.0, 0.9, -15, -1.0),
]


def run_pose(i):
	nf, ff, nt, ft, hy, ph = RUN_CYCLE[i]
	wave = math.sin(i / 8 * math.tau)
	return Pose(hip=(0.5, hy), lean=0.32, near_foot=nf, far_foot=ff, near_toe=nt, far_toe=ft,
		near_hand=(1.5 - ph * 2.5, -13.5 + hy + 13 + abs(ph) * 0.5), far_hand=(2.0 + ph * 3.0, -15 + hy + 13),
		sword=2.72 + ph * 0.06,
		cape=[(-4.0, 3.0 + wave * 0.5), (-8.5, 5.0 - wave), (-13.0, 6.0 + wave * 1.5)])


def run_frames():
	return [run_pose(i) for i in range(8)]


def rise_frames():
	base = Pose(hip=(0.5, -14), lean=0.08, near_foot=(3.5, -6.5), far_foot=(-2.5, -3.0), near_toe=0.5, far_toe=1.0,
		near_hand=(5.5, -17), far_hand=(-2.5, -16.5), sword=-1.15, cape=[(-1.8, 5), (-2.8, 10.5), (-3.2, 15.5)])
	return [base, base.copy(cape=[(-2.2, 5), (-3.4, 10.5), (-4.2, 15.0)], near_hand=(5.5, -17.5))]


def fall_frames():
	base = Pose(hip=(0.5, -14), lean=0.05, near_foot=(3.0, -2.8), far_foot=(-3.0, -3.8), near_toe=0.7, far_toe=0.9,
		near_hand=(6.5, -16.5), far_hand=(-4.5, -19.5), sword=-0.45, cape=[(-3.0, -1.5), (-6.0, -5.0), (-8.0, -9.0)])
	return [base, base.copy(cape=[(-3.2, -0.5), (-6.8, -3.5), (-9.5, -6.5)], far_hand=(-4.5, -19))]


def land_frames():
	a = Pose(hip=(1.0, -10), lean=0.38, near_foot=(5.5, -2), far_foot=(-4.5, -2), near_hand=(6.5, -10.5), far_hand=(1.5, -11),
		sword=0.25, cape=[(-3, 3.5), (-5.5, 8.0), (-7.5, 12.0)])
	b = a.copy(hip=(0.8, -11), lean=0.26, near_hand=(6.0, -12.0), sword=-0.3, cape=[(-2.6, 4.5), (-4.6, 9.5), (-6.2, 14.0)])
	return [a, b]


def wall_frames():
	"""Facing the wall (x = +5): far hand grips above, near foot braced."""
	frames = []
	for k in range(3):
		frames.append(Pose(hip=(0.5, -13), lean=0.1, near_foot=(2.2, -5.5), near_toe=-0.2, far_foot=(-0.5, -1.5), far_toe=1.0,
			near_hand=(4.2, -19.5 + (k % 2) * 0.5), far_hand=(-4.0, -14.0), sword_far=True, sword=2.58,
			cape=[(-2.6, 3.0 - k * 0.6), (-5.0 - k * 0.3, 1.5 - k), (-8.0 - k * 0.6, -1.0 - k * 1.2)]))
	return frames


def hurt_frames():
	a = Pose(hip=(-1.0, -12.5), lean=-0.32, head="down", near_foot=(3.5, -2), far_foot=(-4.5, -2.5), far_toe=0.4,
		near_hand=(0.5, -15.5), far_hand=(-5.5, -17.5), sword=-2.55, sword_behind=True,
		cape=[(-0.5, 4.5), (1.0, 9.0), (3.0, 13.0)])
	b = a.copy(hip=(-1.0, -12.0), lean=-0.22, near_hand=(1.5, -14.5), sword=-2.35, cape=[(-1.2, 4.8), (-0.5, 9.8), (0.8, 14.5)])
	return [a, b]


def dead_frames():
	h = hurt_frames()[0]
	d1 = Pose(hip=(-1.0, -10.5), lean=-0.15, head="down", near_foot=(3.5, -2), far_foot=(-4.0, -2), near_hand=(3.0, -10),
		far_hand=(-3.0, -12), sword=0.9, cape=[(-1.5, 4.5), (-2.5, 9.5), (-3.0, 13.5)])
	d2 = Pose(hip=(-0.5, -7.0), lean=0.15, head="down", near_foot=(4.0, -2), far_foot=(-6.5, -1.2), far_toe=0.0,
		near_hand=(4.5, -6.5), far_hand=(-1.0, -8.0), sword=None, dropped_sword=((9.0, -6.0), 1.25),
		cape=[(-2.0, 3.0), (-4.0, 6.0), (-6.0, 7.5)])
	d3 = Pose(hip=(-1.0, -5.5), lean=0.85, head="down", near_foot=(1.5, -2), far_foot=(-7.5, -1.2), near_toe=0.6,
		near_hand=(7.0, -3.5), far_hand=(4.0, -4.5), sword=None, dropped_sword=((4.0, -1.6), 0.08),
		cape=[(-3.5, 1.0), (-6.5, 2.5), (-9.5, 3.5)])
	d4 = Pose(hip=(-3.0, -3.2), lean=1.45, head="down", head_off=(0, 1), near_foot=(-11.5, -1.5), far_foot=(-12.5, -1.0),
		near_toe=1.2, far_toe=1.3, near_hand=(5.5, -1.6), far_hand=(3.0, -2.0), sword=None, dropped_sword=((4.0, -1.6), 0.0),
		cape=[(-2.6, 0.8), (-4.8, 2.0), (-6.2, 3.2)])
	d5 = d4.copy(cape=[(-2.8, 1.0), (-5.0, 2.4), (-6.0, 3.6)])
	return [h, d1, d2, d3, d4, d5]


# ---------------------------------------------------------------- attack chain
GESTURE = [0.06, 0.17, 0.29, 0.44, 0.58, 0.83]  # sample progress of the 6 gesture frames
STANCE_N, STANCE_F = (5.0, -2), (-5.0, -2)


def attack_frames():
	"""Three moves x (6 gesture + 4 chain frames). In g2..g4 the blade uses the
	gameplay angle so the drawing matches the contact window."""
	ga = [gameplay_angle(GESTURE[i]) for i in (2, 3, 4)]
	moves = []
	# Move 1: forehand diagonal cut.
	m1 = [
		Pose(hip=(-0.5, -12.5), lean=-0.05, near_hand=(1.0, -19.0), far_hand=(4.5, -15.0), sword=-1.78,
			near_foot=STANCE_N, far_foot=STANCE_F, cape=[(-2.0, 5), (-3.5, 10.5), (-4.5, 15.5)]),
		Pose(hip=(0.0, -12.5), lean=0.05, near_hand=(3.0, -18.0), far_hand=(4.5, -14.5), sword=-1.25, smear=(-1.78, -1.25, False),
			near_foot=STANCE_N, far_foot=STANCE_F, cape=[(-2.2, 5), (-3.8, 10.5), (-5.0, 15.5)]),
		Pose(hip=(1.0, -12), lean=0.2, near_hand=(5.0, -15.0), far_hand=(3.0, -13.5), sword=ga[0], smear=(-1.5, ga[0], False),
			near_foot=(6.0, -2), far_foot=STANCE_F, cape=[(-2.8, 4.5), (-5.0, 9.5), (-6.5, 14.0)]),
		Pose(hip=(1.5, -12), lean=0.3, near_hand=(6.0, -13.0), far_hand=(2.0, -13.0), sword=ga[1], smear=(-1.25, ga[1], False),
			near_foot=(6.5, -2), far_foot=STANCE_F, cape=[(-3.2, 4.0), (-5.8, 8.5), (-7.8, 12.5)]),
		Pose(hip=(2.0, -11.5), lean=0.36, near_hand=(6.5, -12.0), far_hand=(1.0, -12.5), sword=ga[2], smear=(-0.95, ga[2], False),
			near_foot=(7.0, -2), far_foot=STANCE_F, cape=[(-3.5, 3.8), (-6.2, 8.0), (-8.5, 11.5)]),
		Pose(hip=(2.0, -11.5), lean=0.4, near_hand=(5.5, -10.5), far_hand=(0.0, -12.5), sword=0.4, smear=(0.0, 0.4, False),
			near_foot=(7.0, -2), far_foot=STANCE_F, cape=[(-3.2, 4.0), (-5.8, 8.8), (-7.6, 12.8)]),
	]
	m1 += [
		m1[5].copy(smear=None, sword=0.42, near_hand=(5.5, -10.8), cape=[(-3.0, 4.2), (-5.2, 9.2), (-6.8, 13.6)]),
		m1[5].copy(smear=None, hip=(1.5, -12), lean=0.3, sword=0.38, near_hand=(5.5, -11.2), cape=[(-2.8, 4.5), (-4.9, 9.6), (-6.3, 14.2)]),
		Pose(hip=(1.0, -12.5), lean=0.12, near_hand=(2.5, -17.0), far_hand=(4.5, -14.5), sword=-1.45,
			near_foot=STANCE_N, far_foot=STANCE_F, cape=[(-2.4, 5), (-4.2, 10.2), (-5.6, 15)]),
		Pose(hip=(0.0, -12.5), lean=-0.08, near_hand=(-2.0, -15.5), far_hand=(5.0, -15.0), sword=-2.78,
			near_foot=(4.0, -2), far_foot=STANCE_F, cape=[(-2.0, 5), (-3.5, 10.5), (-4.5, 15.5)]),
	]
	moves.append(m1)
	# Move 2: backswing over the top into a lunging cut.
	m2 = [
		m1[9].copy(),
		Pose(hip=(0.5, -13), lean=0.0, near_hand=(1.0, -20.0), far_hand=(4.5, -15.5), sword=-1.72, smear=(-2.78, -1.72, False),
			near_foot=(4.5, -2), far_foot=STANCE_F, cape=[(-2.2, 5), (-3.8, 10.5), (-4.8, 15.5)]),
		Pose(hip=(2.0, -12), lean=0.25, near_hand=(4.5, -16.0), far_hand=(1.5, -14.0), sword=ga[0], smear=(-2.2, ga[0], False),
			near_foot=(7.5, -2), far_foot=STANCE_F, cape=[(-3.2, 4.2), (-5.8, 8.8), (-7.8, 13.0)]),
		Pose(hip=(3.0, -11), lean=0.4, near_hand=(7.0, -13.5), far_hand=(-1.0, -13.5), sword=ga[1], smear=(-1.6, ga[1], False),
			near_foot=(9.0, -2), far_foot=(-5.5, -2), cape=[(-3.8, 3.5), (-7.0, 7.0), (-9.8, 10.0)]),
		Pose(hip=(3.5, -10.5), lean=0.46, near_hand=(8.5, -12.5), far_hand=(-3.0, -13.5), sword=ga[2], smear=(-1.1, ga[2], False),
			near_foot=(9.5, -2), far_foot=(-5.5, -2), cape=[(-4.2, 3.0), (-7.8, 6.0), (-11.0, 8.5)]),
		Pose(hip=(3.5, -10.5), lean=0.46, near_hand=(9.0, -12.0), far_hand=(-4.5, -14.0), sword=0.24, smear=(0.0, 0.24, False),
			near_foot=(9.5, -2), far_foot=(-5.5, -2), cape=[(-4.0, 3.2), (-7.4, 6.6), (-10.4, 9.6)]),
	]
	m2 += [
		m2[5].copy(smear=None, sword=0.28, cape=[(-3.8, 3.5), (-7.0, 7.2), (-9.6, 10.6)]),
		m2[5].copy(smear=None, hip=(2.5, -11), lean=0.36, near_hand=(8.0, -12.5), sword=0.24, cape=[(-3.4, 4.0), (-6.2, 8.2), (-8.4, 12.0)]),
		Pose(hip=(1.0, -12.5), lean=0.05, near_hand=(4.0, -21.0), two_hands=True, sword=-1.42,
			near_foot=STANCE_N, far_foot=STANCE_F, cape=[(-2.4, 5), (-4.2, 10.2), (-5.6, 15)]),
		Pose(hip=(0.0, -13), lean=-0.18, near_hand=(2.0, -27.5), two_hands=True, sword=-2.4, sword_behind=True, head="up",
			near_foot=(4.5, -2), far_foot=STANCE_F, cape=[(-1.8, 5), (-3.2, 10.5), (-4.2, 15.5)]),
	]
	moves.append(m2)
	# Move 3: two-handed overhead chop ending on the ground.
	m3 = [
		m2[9].copy(hip=(0.0, -12.5)),
		Pose(hip=(1.0, -13.5), lean=0.1, near_hand=(5.0, -24.0), two_hands=True, sword=-1.5, smear=(-2.4, -1.5, True), head="up",
			near_foot=(6.0, -2.5), near_toe=0.2, far_foot=STANCE_F, cape=[(-2.0, 5.2), (-3.4, 10.8), (-4.4, 16.0)]),
		Pose(hip=(2.0, -12), lean=0.35, near_hand=(6.0, -17.0), two_hands=True, sword=ga[0], smear=(-2.0, ga[0], True),
			near_foot=(7.0, -2), far_foot=STANCE_F, cape=[(-3.0, 4.0), (-5.6, 8.4), (-7.6, 12.4)]),
		Pose(hip=(2.5, -11), lean=0.5, near_hand=(6.5, -13.5), two_hands=True, sword=ga[1], smear=(-1.6, ga[1], True),
			near_foot=(7.5, -2), far_foot=(-5.5, -2), cape=[(-3.6, 3.2), (-6.6, 6.6), (-9.2, 9.6)]),
		Pose(hip=(3.0, -10), lean=0.6, near_hand=(6.5, -11.0), two_hands=True, sword=ga[2], smear=(-1.1, ga[2], True),
			near_foot=(8.0, -2), far_foot=(-5.5, -2), cape=[(-4.0, 2.4), (-7.4, 5.0), (-10.4, 7.2)]),
		Pose(hip=(3.0, -9), lean=0.7, near_hand=(6.0, -8.5), two_hands=True, sword=0.36, smear=(0.0, 0.36, True),
			near_foot=(8.0, -2), far_foot=(-5.5, -2), dust=((28.0, 0.0), 0), cape=[(-3.6, 2.6), (-6.8, 5.4), (-9.6, 8.0)]),
	]
	m3 += [
		m3[5].copy(smear=None, dust=((28.0, 0.0), 1), cape=[(-3.4, 3.0), (-6.4, 6.2), (-9.0, 9.2)]),
		m3[5].copy(smear=None, hip=(2.5, -9.5), lean=0.62, dust=((28.0, 0.0), 2), cape=[(-3.0, 3.6), (-5.8, 7.4), (-8.0, 10.8)]),
		Pose(hip=(1.0, -12), lean=0.2, near_hand=(4.0, -15.0), far_hand=(5.0, -13.5), sword=-0.6,
			near_foot=STANCE_N, far_foot=STANCE_F, cape=[(-2.6, 4.8), (-4.6, 9.8), (-6.0, 14.6)]),
		m1[0].copy(),
	]
	moves.append(m3)
	return moves


# ---------------------------------------------------------------- small VFX
def _plot(c, x, y, color):
	c.put(int(math.floor(x + 0.5)), int(math.floor(y + 0.5)), color)


def spark_frames():
	"""Impact spark (16x16, 5 frames): white core, warm rays, fading embers."""
	frames = []
	W = hexc("ffffff")
	Y = hexc("ffe9a0")
	O = hexc("e8a24a")
	D = hexc("9a5a2a")
	for i in range(5):
		c = Canvas(16, 16)
		if i == 0:
			for x, y, col in [(0, 0, W), (1, 0, W), (-1, 0, W), (0, 1, W), (0, -1, W), (1, 1, Y), (-1, -1, Y), (1, -1, Y), (-1, 1, Y), (2, 0, Y), (-2, 0, Y), (0, 2, Y), (0, -2, Y)]:
				c.put(8 + x, 8 + y, col)
		elif i < 4:
			length = (3, 5, 6)[i - 1]
			for a in range(8):
				ang = a * math.pi / 4 + (0.2 if a % 2 else 0)
				reach = length if a % 2 == 0 else length - 2
				for t in range(1, reach + 1):
					col = W if t <= reach // 3 + (1 if i == 1 else 0) else (Y if t <= 2 * reach // 3 + 1 else O)
					if i == 3 and t < 3:
						continue
					_plot(c, 8 + math.cos(ang) * t, 8 + math.sin(ang) * t, col)
			if i < 3:
				c.put(8, 8, W)
		else:
			for x, y in ((3, 4), (12, 5), (5, 12), (11, 11), (2, 9), (13, 8)):
				c.put(x, y, D)
		frames.append(c)
	return frames


def puff_frames():
	"""Double-jump air ring seen edge-on (24x10, 5 frames), pale steel blue."""
	frames = []
	cols = [hexc("eef6ff"), hexc("c0d8ea"), hexc("9fb9cf"), hexc("7d93a8", 200), hexc("5e7186", 140)]
	for i in range(5):
		c = Canvas(24, 10)
		rx = 3 + i * 2.2
		ry = 1.2 + i * 0.6
		for k in range(64):
			a = k / 64 * math.tau
			x, y = 12 + math.cos(a) * rx, 5 + math.sin(a) * ry
			if i >= 3 and math.sin(a) < -0.2:
				continue
			_plot(c, x - 0.5, y - 0.5, cols[i])
		if i < 2:
			for dx in (-1, 0, 1):
				c.put(12 + dx, 5, cols[0])
		frames.append(c)
	return frames


def dust_frames():
	"""Wall-slide grit (6x8, 3 frames) in warm stone grey."""
	frames = []
	A = hexc("c9bea4")
	B = hexc("968b75")
	pts = [
		[(2, 1, A), (3, 2, B), (1, 3, B), (4, 0, B)],
		[(3, 3, A), (1, 4, B), (4, 5, B), (2, 6, B)],
		[(2, 5, B), (4, 7, B), (0, 6, B)],
	]
	for pp in pts:
		c = Canvas(6, 8)
		for x, y, col in pp:
			c.put(x, y, col)
		frames.append(c)
	return frames


def land_dust_frames():
	"""Landing puff (32x8, 4 frames): two low clouds rolling outward."""
	frames = []
	cols = [hexc("d9cfb8"), hexc("b0a690"), hexc("857c6a"), hexc("5f584c")]
	for i in range(4):
		c = Canvas(32, 8)
		for side in (-1, 1):
			cx = 16 + side * (4 + i * 3.2)
			r = 2.2 + i * 0.5
			for y in range(8):
				for x in range(32):
					dx, dy = x + 0.5 - cx, (y + 0.5 - (6.5 - i * 0.6)) * 1.6
					d = math.hypot(dx, dy)
					if d <= r and (i < 2 or (x + y) % 2 == 0):
						c.put(x, y, cols[min(3, i + (1 if dy > 0.5 else 0))])
		frames.append(c)
	return frames


# ---------------------------------------------------------------- outputs
def write_sprite_frames(path, texture_res, layout):
	"""Write a Godot SpriteFrames resource using AtlasTexture regions."""
	subs = []
	anims = []
	n = 0
	for name, fps, loop, regions in layout:
		frames = []
		for (x, y, w, h) in regions:
			n += 1
			sid = f"{name}_{len(frames)}"
			subs.append(f'[sub_resource type="AtlasTexture" id="{sid}"]\natlas = ExtResource("1")\nregion = Rect2({x}, {y}, {w}, {h})\n')
			frames.append('{"duration": 1.0, "texture": SubResource("%s")}' % sid)
		anims.append('{"frames": [%s], "loop": %s, "name": &"%s", "speed": %s}' % (", ".join(frames), "true" if loop else "false", name, repr(float(fps))))
	lines = [f'[gd_resource type="SpriteFrames" load_steps={n + 2} format=3]\n', f'[ext_resource type="Texture2D" path="{texture_res}" id="1"]\n']
	lines.extend(subs)
	lines.append("[resource]\nanimations = [%s]\n" % ", ".join(anims))
	with open(path, "w", newline="\n") as f:
		f.write("\n".join(lines))


def build():
	"""Return [(name, fps, loop, [Canvas...])] in sheet order."""
	anims = []
	anims.append(("idle", 6.0, True, [render(p) for p in idle_frames()]))
	anims.append(("run", 14.0, True, [render(p) for p in run_frames()]))
	anims.append(("rise", 8.0, True, [render(p) for p in rise_frames()]))
	anims.append(("fall", 8.0, True, [render(p) for p in fall_frames()]))
	anims.append(("land", 20.0, False, [render(p) for p in land_frames()]))
	anims.append(("wall", 7.0, True, [render(p) for p in wall_frames()]))
	anims.append(("hurt", 10.0, False, [render(p) for p in hurt_frames()]))
	anims.append(("dead", 8.0, False, [render(p) for p in dead_frames()]))
	moves = attack_frames()
	for i, m in enumerate(moves):
		anims.append((f"atk{i + 1}", 1.0, False, [render(p) for p in m]))
	for i, m in enumerate(moves):
		anims.append((f"up{i + 1}", 1.0, False, [render(shifted_upper(p), "upper") for p in m]))
	anims.append(("base_run", 14.0, True, [render(p, "base") for p in run_frames()]))
	anims.append(("base_rise", 8.0, True, [render(p, "base") for p in rise_frames()]))
	anims.append(("base_fall", 8.0, True, [render(p, "base") for p in fall_frames()]))
	return anims


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	anims = build()
	columns = max(len(fr) for _, _, _, fr in anims)
	cells = []
	layout = []
	for r, (name, fps, loop, frames) in enumerate(anims):
		cells.extend(frames + [Canvas(FRAME, FRAME)] * (columns - len(frames)))
		layout.append((name, fps, loop, [(i * FRAME, r * FRAME, FRAME, FRAME) for i in range(len(frames))]))
	knight = sheet(cells, columns)
	save_png(knight, os.path.join(OUT, "ashen_knight.png"))
	write_sprite_frames(os.path.join(OUT, "ashen_knight_frames.tres"), "res://assets/sprites/ashen_knight.png", layout)
	save_png(sheet(spark_frames(), 5), os.path.join(OUT, "vfx_hit_spark.png"))
	save_png(sheet(puff_frames(), 5), os.path.join(OUT, "vfx_air_puff.png"))
	save_png(sheet(dust_frames(), 3), os.path.join(OUT, "vfx_wall_dust.png"))
	save_png(sheet(land_dust_frames(), 4), os.path.join(OUT, "vfx_land_dust.png"))
	if preview:
		save_png(knight, os.path.join(preview, "knight_sheet_x3.png"), 3, (52, 60, 66, 255))
	print("knight sheet", knight.w, knight.h, {n: len(fr) for n, _, _, fr in anims})


if __name__ == "__main__":
	main()

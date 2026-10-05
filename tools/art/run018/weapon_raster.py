"""RUN-018 weapon strips and their rasteriser (shared contract with scripts/weapon_art.gd).

A held weapon is authored as a horizontal *strip*: column c covers the shaft distance
t in [c - grip, c + 1 - grip) from the hand (t = 0), row r sits at the perpendicular
offset s = r - axis (s > 0 is the leading edge of the forward cut). The last `head`
columns stay anchored to the tip, columns [stretch, width - head) repeat, so a strip is
drawn at any gameplay reach L (hand to tip, RANGE x 24 px) without rescaling pixels.

Each strip has two shading variants stacked vertically: variant A when the light comes
from the -s side, variant B when it comes from +s (sign of n . LIGHT, like knight.draw_sword).
The rasteriser plots samples every 0.25 px along t (one per row, plus a bridge sample
between vertically adjacent opaque rows), keeps the last colour per pixel, then adds a
1 px outline. Coordinates are the knight rig's (feet origin, +x forward, +y down).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pixel import Canvas, hexc  # noqa: E402
from palette import CORRUPT, GOLD, OUTLINE, STEEL, WOOD  # noqa: E402

LIGHT = (0.5, -0.65)
STEP = 0.25
BLADE = [hexc(c) for c in ("5d6676", "8d96a6", "c4cbd6", "eef1f5", "ffffff")]
LEATHER = [hexc(c) for c in ("2a1f1a", "3f2e24", "5a4030", "7a5a3c")]
DARK_STEEL = [hexc(c) for c in ("1d1f27", "30333f", "4a4f5e", "6e7586")]


class Strip:
	def __init__(self, name, grip, axis, rows, length, stretch, head):
		self.name = name
		self.grip = grip  # float: t of column 0 is -grip
		self.axis = axis  # float row of s = 0
		self.rows = rows
		self.length = length  # authored reach (strip width = ceil(grip + length))
		self.width = int(math.ceil(grip + length - 1e-6))
		self.stretch = stretch
		self.head = head
		self.variants = [Canvas(self.width, rows), Canvas(self.width, rows)]

	def paint(self, painter):
		"""painter(t, s, lit) -> colour or None; lit: True on the light-facing side."""
		for v in (0, 1):
			for c in range(self.width):
				t = c - self.grip + 0.5
				for r in range(self.rows):
					s = r - self.axis
					lit = (s < 0) if v == 0 else (s > 0)
					col = painter(t, s, lit, c)
					if col is not None:
						self.variants[v].put(c, r, col)

	def column(self, t, reach):
		u = t + self.grip
		if t > reach - self.head:
			return max(0, min(self.width - 1, self.width - self.head + int(math.floor(t - (reach - self.head)))))
		if u < self.stretch:
			return max(0, int(math.floor(u)))
		period = max(1, self.width - self.head - self.stretch)
		return self.stretch + int(math.floor(u - self.stretch)) % period


def rasterize(strip, hand, angle, reach):
	d = (math.cos(angle), math.sin(angle))
	n = (-d[1], d[0])
	variant = strip.variants[1 if n[0] * LIGHT[0] + n[1] * LIGHT[1] > 0 else 0]
	out = {}
	steps = int(math.floor((reach + strip.grip) / STEP + 1e-6))
	for k in range(steps + 1):
		t = -strip.grip + k * STEP
		col = strip.column(t, reach)
		for r in range(strip.rows):
			c = variant.get(col, r)
			if c is None:
				continue
			ss = [r - strip.axis]
			if r + 1 < strip.rows and variant.get(col, r + 1) is not None:
				ss.append(r - strip.axis + 0.5)
			for s in ss:
				x = hand[0] + d[0] * t + n[0] * s
				y = hand[1] + d[1] * t + n[1] * s
				out[(int(math.floor(x)), int(math.floor(y)))] = c
	ring = {}
	for (x, y) in out:
		for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
			q = (x + dx, y + dy)
			if q not in out:
				ring[q] = OUTLINE
	ring.update(out)
	return ring


def smear(hand, a0, a1, heavy, reach):
	"""knight.draw_smear with the radius following the weapon reach."""
	out = {}
	span = a1 - a0
	if abs(span) < 0.05:
		return out
	r_out = reach + 0.6
	x0, x1 = int(math.floor(hand[0] - r_out - 2)), int(math.ceil(hand[0] + r_out + 2))
	y0, y1 = int(math.floor(hand[1] - r_out - 2)), int(math.ceil(hand[1] + r_out + 2))
	for iy in range(y0, y1 + 1):
		for ix in range(x0, x1 + 1):
			dx, dy = ix + 0.5 - hand[0], iy + 0.5 - hand[1]
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
	return out


# ---------------------------------------------------------------- strips
def sword():
	"""knight.draw_sword segments: pommel t<-2.6, grip <1.0, guard <2.2 (6 px), blade, tip in the last 1.5 px."""
	st = Strip("Sword", 3.4, 2.5, 6, 24.0, 0, 2)

	def p(t, s, lit, c):
		if t < -2.6:
			return GOLD[2] if s == -0.5 else None
		if t < 1.0:
			return LEATHER[2] if s == -0.5 else None
		if t < 2.2:
			return GOLD[3] if lit else GOLD[1]
		if abs(s) == 0.5:
			if t > 22.5:
				return BLADE[4] if lit else BLADE[1]
			return BLADE[3] if lit else BLADE[1]
		return None
	st.stretch = 7
	st.paint(p)
	return st


def longsword():
	"""Longer two-hand grip, wider guard with drooping quillons, fuller line down the blade."""
	st = Strip("Longsword", 6.4, 2.5, 6, 28.8, 0, 4)
	def p(t, s, lit, c):
		if t < -5.4:
			return GOLD[2] if abs(s) < 2 else None
		if t < -4.6:
			return GOLD[1] if abs(s) < 1 else None
		if t < 1.0:
			if s == -0.5:
				return LEATHER[3] if int(t + 10) % 2 == 0 else LEATHER[1]
			return None
		if t < 2.2:
			if abs(s) <= 2.5:
				return GOLD[3] if lit else GOLD[1]
			return None
		if t < 3.2:
			return (GOLD[2] if abs(s) == 2.5 and not lit else None) or (BLADE[2] if abs(s) == 0.5 else None)
		if abs(s) == 0.5:
			if t > st.length - 2.0:
				return BLADE[4] if lit else BLADE[2]
			if lit:
				return BLADE[3]
			return BLADE[1] if int(t) % 5 else BLADE[2]
		return None
	st.stretch = 11
	st.paint(p)
	return st


def haft(t, s, dark=False):
	ramp = DARK_STEEL if dark else WOOD
	if s == -0.5:
		return ramp[2] if not dark else ramp[2]
	if s == 0.5:
		return ramp[1]
	return None


def brutal_axe():
	"""Short wooden haft, iron butt cap, heavy single bit on the leading edge, small poll."""
	st = Strip("BrutalAxe", 3.0, 2.5, 12, 19.2, 0, 8)
	L = st.length

	def p(t, s, lit, c):
		if t < -2.0:
			return STEEL[1] if abs(s) < 1 else None
		u = t - (L - 8)  # 0..8 across the head
		if u >= 0:
			if abs(s) <= 0.5:
				return STEEL[2] if u < 7 else STEEL[3]
			if s > 0:
				# bit: grows towards the edge, curved cutting edge, bright rim on the far side
				reach = 2.0 + 7.0 * min(1.0, (s - 0.5) / 7.5)
				lo, hi = 4.0 - reach * 0.55, 4.0 + reach * 0.55
				if s <= 8.5 and lo <= u <= hi:
					if s >= 7.5:
						return BLADE[4] if lit else BLADE[3]
					return STEEL[3] if lit else STEEL[2]
				return None
			if -2.5 <= s < 0 and 3 <= u <= 6:
				return STEEL[2] if lit else STEEL[1]
			return None
		h = haft(t, s)
		if h is not None and 3.0 < t < 5.0:
			return LEATHER[3] if s == -0.5 else LEATHER[2]
		return h
	st.stretch = 4
	st.paint(p)
	return st


def warhammer():
	"""Iron-banded haft and a blocky hammer head with a short top spike."""
	st = Strip("Warhammer", 3.0, 4.5, 10, 19.2, 0, 7)
	L = st.length

	def p(t, s, lit, c):
		if t < -2.0:
			return STEEL[1] if abs(s) < 1 else None
		u = t - (L - 7)
		if u >= 0:
			if u >= 5.5:
				return (STEEL[3] if lit else STEEL[2]) if abs(s) <= 0.5 else None
			if 0.5 <= u <= 5.5 and abs(s) <= 4.5:
				if abs(s) == 4.5:
					return STEEL[4] if lit else STEEL[2]
				if u < 1.5 or u > 4.5:
					return STEEL[1]
				return STEEL[3] if lit else STEEL[2]
			return (STEEL[2] if abs(s) <= 0.5 else None)
		h = haft(t, s)
		if h is not None and int(t) % 6 == 3:
			return STEEL[2]
		return h
	st.stretch = 4
	st.paint(p)
	return st


def dark_scythe():
	"""Dark iron-shod haft; from the top a long crescent blade sweeps out on the leading side
	and back towards the hand (inner cutting edge), a sparing violet socket stone."""
	st = Strip("DarkScythe", 7.0, 1.5, 18, 36.0, 0, 15)
	L = st.length

	def p(t, s, lit, c):
		if t < -6.0:
			return DARK_STEEL[2] if abs(s) < 1 else None
		u = t - (L - 15)  # 0..15, the shaft ends at u = 14
		if u >= 0:
			if abs(s) <= 0.5 and u <= 14:
				if 12 <= u <= 14:
					return CORRUPT[3] if lit else CORRUPT[2]
				return DARK_STEEL[2] if lit else DARK_STEEL[1]
			if s > 0:
				k = s - 0.5  # 0..15 out from the shaft
				centre = 13.0 - 0.12 * k - 0.024 * k * k
				half = max(0.6, 2.6 - k * 0.13)
				if k <= 15.5 and centre - half <= u <= centre + half:
					if u < centre - half + 1.0:
						return BLADE[4] if lit else BLADE[3]
					return DARK_STEEL[3] if lit else BLADE[0]
			return None
		h = haft(t, s, dark=True)
		if h is not None and -1.0 < t < 1.5:
			return LEATHER[2]
		return h
	st.stretch = 3
	st.paint(p)
	return st


def halberds():
	"""Long wooden pole: axe blade on the leading side, back hook, top spike."""
	st = Strip("Halberds", 8.0, 4.5, 12, 48.0, 0, 13)
	L = st.length

	def p(t, s, lit, c):
		if t < -7.0:
			return STEEL[1] if abs(s) < 1 else None
		u = t - (L - 13)  # 0..13
		if u >= 0:
			if u >= 8:
				# top spike along the axis, tapering
				if abs(s) <= 0.5 or (abs(s) <= 1.5 and u < 10):
					return BLADE[4] if (u > 11.5 and lit) else (STEEL[3] if lit else STEEL[2])
				return None
			if abs(s) <= 0.5:
				return STEEL[2] if u >= 1 else WOOD[2]
			if s > 0 and s <= 6.5:
				lo, hi = 1.5 - (s - 0.5) * 0.25, 7.0 + (s - 0.5) * 0.15
				if lo <= u <= hi:
					if s >= 5.5:
						return BLADE[4] if lit else BLADE[3]
					return STEEL[3] if lit else STEEL[2]
			if s < 0 and s >= -3.5 and 3.0 <= u <= 5.0 + (s + 0.5) * 0.6:
				return STEEL[2] if lit else STEEL[1]
			return None
		return haft(t, s)
	st.stretch = 9
	st.paint(p)
	return st


def scabbard(length=8.5, name="Scabbard"):
	"""knight.draw_sheath along its own axis: pommel, grip, guard, leather scabbard, gold chape."""
	st = Strip(name, 4.5, 0.5, 2, length, 0, 1)

	def p(t, s, lit, c):
		if t < -3.5:
			return GOLD[2] if s == -0.5 else None
		if t < -1.2:
			return LEATHER[3] if s == -0.5 else None
		if t < -0.4:
			return GOLD[1] if s == -0.5 else None
		if t < length - 1.0:
			return LEATHER[1] if s == -0.5 else LEATHER[2]
		return GOLD[1] if s == -0.5 else None
	st.stretch = 6
	st.paint(p)
	return st


def knife():
	"""Throwing knife held in the hand (RUN-018): grip, small guard, bright blade."""
	st = Strip("Knife", 2.0, 1.5, 3, 6.0, 0, 0)

	def p(t, s, lit, c):
		if t < 0.0:
			return LEATHER[2] if s == 0.5 else None
		if t < 1.0:
			return GOLD[1]
		if s == 0.5 or (s == -0.5 and t < 4.0):
			return BLADE[4] if lit or t > 5.0 else BLADE[2]
		return None
	st.stretch = 3
	st.paint(p)
	return st


def all_strips():
	return [sword(), longsword(), brutal_axe(), dark_scythe(), warhammer(), halberds(), scabbard(), scabbard(11.5, "ScabbardLong")]

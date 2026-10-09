"""RUN-019 world art: traps, mechanisms and pickups (section C of work/run019/claude/SPEC.md).

Usage:
  python3 tools/art/run019/world_run019.py [--preview DIR]

Writes the 21 PNG strips to assets/run019/world/ (cell sizes, frame order and counts are
the strict contract read by the Godot integration). --preview DIR also writes x4 zoomed
copies on a grey (40,44,52) background. Fully deterministic, dependency free.

The secret wall samples the real terrain tiles from assets/sprites/terrain_stone.png
(read only) so it matches the stone masonry of the level.
"""
import argparse
import math
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from pixel import Canvas, hexc, outline, sheet, save_png  # noqa: E402
from palette import BLOOD, CORRUPT, EMBER, GOLD, MOSS, OUTLINE, SLIME_GREEN, STEEL, STONE, WOOD  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "run019", "world")
TERRAIN = os.path.join(ROOT, "assets", "sprites", "terrain_stone.png")
O = OUTLINE
# Magic Shield ramp (functional colour: cyan / blue).
BLUE = [hexc(c) for c in ("0b2340", "1b4f94", "3a8fd4", "7ad0f0", "dcf7ff")]
WHITE = (255, 255, 255, 255)


def A(c, a):
	return (c[0], c[1], c[2], int(a))


def hsh(x, y, s=0):
	return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) & 0xFFFF


def ell(c, cx, cy, rx, ry, col):
	for y in range(math.floor(cy - ry) - 1, math.ceil(cy + ry) + 2):
		for x in range(math.floor(cx - rx) - 1, math.ceil(cx + rx) + 2):
			if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
				c.put(x, y, col)


def disc(c, cx, cy, r, col):
	ell(c, cx, cy, r, r, col)


def lerp_col(a, b, k):
	return tuple(int(round(a[i] * (1 - k) + b[i] * k)) for i in range(3)) + (255,)


# ---------------------------------------------------------------- trap_spikes_retract
def spikes_frame(h, glow, glint, tipred):
	"""h = spike height in px above the socle top (y14), glow 0..3 = ember light in holes."""
	c = Canvas(32, 16)
	centres = [4 + 5 * i for i in range(6)]
	hole_cols = [O, BLOOD[1], EMBER[1], EMBER[2]]
	for x in range(32):
		c.put(x, 14, STEEL[3] if hsh(x, 1) % 4 else STEEL[2])
		c.put(x, 15, STEEL[1] if hsh(x, 2) % 3 else STEEL[0])
	c.put(0, 14, STEEL[4])
	c.put(31, 14, STEEL[1])
	for x in (0, 31):
		c.put(x, 15, O)
	for cx in centres:
		for dx in (-1, 0, 1):
			c.put(cx + dx, 14, O if dx else hole_cols[glow])
		if glow >= 2:
			c.put(cx, 14, EMBER[3])
			c.put(cx - 1, 14, hole_cols[glow - 1])
			c.put(cx + 1, 14, hole_cols[glow - 1])
		if glow == 3:
			c.put(cx, 14, GOLD[4])
		if glow:
			# ember light spilling out of the hole onto the plate and between the spikes
			for dx in (-2, 2):
				c.put(cx + dx, 14, A(EMBER[2], 255) if glow >= 2 else BLOOD[2])
			for dx in (-2, -1, 1, 2):
				c.put(cx + dx, 13, A(EMBER[2], 70 * glow))
	if h > 0:
		sp = Canvas(32, 16)
		for cx in centres:
			for i in range(h):
				y = 13 - i
				wide = (i < max(1, int(h * 0.55))) if h > 3 else (i == 0)
				if wide:
					sp.put(cx - 1, y, STEEL[4] if i % 5 else STEEL[3])
					sp.put(cx, y, STEEL[3])
					sp.put(cx + 1, y, STEEL[1])
				else:
					sp.put(cx, y, STEEL[3])
					if i < h - 1:
						sp.put(cx - 1, y, None)
				if i >= h - 2 and tipred:
					sp.put(cx, y, BLOOD[3] if i == h - 1 else BLOOD[2])
			if glint:
				sp.put(cx, 13 - h + 1, GOLD[4])
				sp.put(cx, 13 - h, EMBER[3])
		sp = outline(sp, O)
		for y in range(14, 16):
			for x in range(32):
				sp.put(x, y, None)
		c.blit(sp, 0, 0)
	return c


def trap_spikes_retract():
	# (height, glow, glint, tip red)
	spec = [(0, 0, 0, 0),
		(2, 2, 1, 0), (3, 3, 0, 0), (2, 2, 1, 0), (3, 3, 0, 0),
		(3, 2, 0, 1), (6, 1, 0, 1), (10, 0, 0, 1),
		(10, 0, 0, 1), (10, 0, 1, 1),
		(7, 1, 0, 1), (4, 2, 0, 1), (2, 1, 0, 0)]
	return [spikes_frame(*s) for s in spec]


# ---------------------------------------------------------------- trap_trapdoor
def leaf(theta):
	"""Left leaf (16x20) pivoting about its outer edge; theta 0 = closed, 90 = hanging."""
	c = Canvas(16, 20)
	th = math.radians(theta)
	cs, sn = math.cos(th), math.sin(th)
	k = theta / 90.0
	px, py = 1.5 * k, 6.0
	half = 2.0 - 0.5 * k
	length = 16.0 - 1.5 * k
	for y in range(20):
		for x in range(16):
			dx, dy = x + 0.5 - px, y + 0.5 - py
			t = dx * cs + dy * sn
			u = -dx * sn + dy * cs
			if 0 <= t <= length and -half <= u <= half + 1e-6:
				s = (u + half) / (2 * half)
				col = WOOD[3] if s < 0.3 else WOOD[2] if s < 0.6 else WOOD[1] if s < 0.85 else WOOD[0]
				if s < 0.1:
					col = WOOD[4]
				if 4 <= t < 6 or 10.5 <= t < 12.5:
					col = STEEL[3] if s < 0.3 else STEEL[2] if s < 0.7 else STEEL[1]
				elif t < 2:
					col = STEEL[2] if s < 0.5 else STEEL[1]
				elif int(t * 1.0) % 5 == 3 and s > 0.3 and s < 0.7:
					col = WOOD[1]
				c.put(x, y, col)
	return c


def trapdoor_frame(f):
	c = Canvas(32, 20)
	if f <= 4:
		gap = [0, 1, 2, 1, 2][f]
		jit = [(0, 0), (0, 1), (1, 0), (0, 1), (1, 0)][f]
		left, right = leaf(0), leaf(0)
		c.blit(left, -gap // 2 * 0 - (gap + 1) // 2, jit[0])
		c.blit(right, 16 + gap // 2 + (1 if gap else 0) - 1 + 1 - 1, jit[1], flip=True)
		c = outline(c, O)
		if f:
			for gx in range(15 - (gap + 1) // 2 + 1, 16 + gap // 2 + 1):
				for y in range(4, 8):
					if c.get(gx, y) is None or c.get(gx, y) == O:
						c.put(gx, y, EMBER[2] if y > 4 else EMBER[3])
			# fissure across the leaves
			cr = 6 + f
			for i in range(3):
				c.put(15 - cr + 2 * i, 5 + (i % 2), BLOOD[1])
				c.put(16 + cr - 2 * i, 6 - (i % 2), BLOOD[1])
			c.put(15, 4, GOLD[4])
			c.put(16, 4, GOLD[4] if f % 2 else EMBER[3])
			for i in range(f):
				c.put(14 + (hsh(f, i) % 5), 9 + (i * 3 + f) % 8, A(STONE[5], 220))
		return c
	ang = {5: 25, 6: 50, 7: 72, 8: 86, 9: 90}[f]
	c.blit(leaf(ang), 0, 0)
	c.blit(leaf(ang), 16, 0, flip=True)
	c = outline(c, O)
	if f in (5, 6, 7):
		for i in range(5):
			x = 13 + (hsh(f, i) % 7)
			y = 6 + (f - 5) * 2 + (hsh(i, f) % 6)
			c.put(x, y, A(STONE[5], 190 - 30 * (f - 5)))
			c.put(x + 1, y, A(STONE[4], 150))
	return c


def trap_trapdoor():
	frames = [trapdoor_frame(f) for f in range(10)]
	for fr in frames:  # nothing above the floor line (row 4)
		for y in range(4):
			for x in range(32):
				fr.put(x, y, None) if fr.px[y * 32 + x] is not None else None
				fr.px[y * 32 + x] = None
	return frames


# ---------------------------------------------------------------- trap_turret
MOUTH = [O, BLOOD[1], BLOOD[3], EMBER[2], EMBER[3], GOLD[4]]
EYE = [O, BLOOD[0], BLOOD[1], BLOOD[2], BLOOD[3], EMBER[2], EMBER[3]]


def turret_frame(dx, g, eye, smoke=0):
	b = Canvas(24, 24)
	for y in range(4, 20):
		for x in range(3, 19):
			if (x in (3, 18)) and (y in (4, 19)):
				continue
			col = STONE[3]
			h = hsh(x, y, 7) % 9
			if h == 0:
				col = STONE[2]
			elif h == 1:
				col = STONE[4]
			if x == 3 or y == 4:
				col = STONE[4]
			if x == 18 or y == 19:
				col = STONE[2]
			if x >= 17 and y >= 18:
				col = STONE[1]
			b.put(x, y, col)
	# horns / crest
	for (x, y) in ((6, 3), (5, 4), (13, 3), (12, 2), (13, 2)):
		b.put(x, y, STONE[4] if x in (6, 13) else STONE[3])
	b.put(6, 2, STONE[4])
	b.put(12, 3, STONE[3])
	# ear fin grooves
	for y in range(9, 15):
		b.put(5, y, STONE[1] if y % 2 else STONE[2])
	# brow and eye
	for x in range(8, 18):
		b.put(x, 8, STONE[1])
	for x in range(13, 17):
		b.put(x, 9, EYE[eye])
		b.put(x, 10, EYE[max(eye - 1, 0)] if eye else STONE[1])
	b.put(12, 9, STONE[1])
	b.put(12, 10, STONE[1])
	b.put(17, 9, STONE[1])
	if eye >= 3:
		b.put(14, 9, EMBER[3] if eye >= 5 else EYE[eye])
	# snout / cannon barrel
	for y in range(8, 16):
		for x in range(19, 23):
			col = STONE[3]
			if y == 8:
				col = STONE[4]
			elif y >= 14:
				col = STONE[2]
			if x == 19:
				col = STONE[2]
			b.put(x, y, col)
	for y in range(10, 14):
		for x in (21, 22):
			b.put(x, y, MOUTH[g])
	if g >= 3:
		b.put(21, 11, MOUTH[min(g + 1, 5)])
		b.put(22, 12, MOUTH[min(g + 1, 5)])
	b.put(20, 10, STEEL[4])
	b.put(20, 13, STEEL[4])
	b.put(22, 9, STONE[1])
	b.put(22, 14, STONE[1])
	# jaw and fangs
	for x in range(12, 19):
		b.put(x, 17, STONE[2])
		b.put(x, 18, STONE[1])
	b.put(19, 16, STONE[1])
	b.put(19, 17, STEEL[3])
	b.put(15, 16, STEEL[3])
	# moss and cracks
	for (x, y) in ((4, 18), (5, 19), (4, 19), (8, 19), (9, 19)):
		b.put(x, y, MOSS[2] if (x + y) % 2 else MOSS[1])
	for (x, y) in ((9, 5), (10, 6), (10, 7), (11, 7)):
		b.put(x, y, STONE[1])
	b = outline(b, O)
	c = Canvas(24, 24)
	if g >= 2:
		for (x, y) in ((19, 7), (20, 7), (19, 16), (20, 16), (23, 8), (23, 15), (23, 9), (23, 14)):
			c.put(x + dx, y, A(EMBER[2], 90 * (g - 1) // 2))
	c.blit(b, dx, 0)
	if g == 5:
		for (x, y) in ((22, 9), (22, 14), (23, 10), (23, 13), (23, 11), (23, 12)):
			c.put(x + dx, y, GOLD[4])
	for i in range(smoke):
		x = 21 + (i % 2)
		y = 7 - i * 2
		disc(c, x, y, 1.6 + 0.2 * i, A(STEEL[2], max(170 - 45 * i, 50)))
		c.put(x - 1, y - 1, A(STEEL[3], max(150 - 45 * i, 40)))
	return c


def trap_turret():
	spec = [(0, 0, 2), (0, 0, 1),
		(0, 1, 3), (0, 2, 4), (0, 3, 5), (0, 4, 6),
		(-2, 5, 6, 0), (-1, 4, 5, 1), (0, 2, 4, 2), (0, 1, 3, 3)]
	return [turret_frame(*s) for s in spec]


# ---------------------------------------------------------------- proj_turret_bolt
def bolt_frame(f):
	b = Canvas(12, 6)
	tail = [4, 5, 3][f]
	for x in range(tail, 12):
		b.put(x, 2, EMBER[3] if x > 6 else EMBER[2])
		b.put(x, 3, EMBER[3] if x > 6 else EMBER[2])
	for x in range(tail + 1 + f % 2, 11):
		b.put(x, 1, EMBER[2] if x > 4 else EMBER[1])
		b.put(x, 4, EMBER[1] if x > 4 else BLOOD[3])
	for x in range(9, 12):
		b.put(x, 2, GOLD[4])
		b.put(x, 3, GOLD[4] if x > 9 else GOLD[3])
	b.put(11, 1, None)
	b.put(11, 4, None)
	b.put(10, 1, EMBER[3])
	b.put(10, 4, EMBER[2])
	for x in range(1 + f, tail):
		b.put(x, 2 + (x + f) % 2, BLOOD[3] if x > 2 else BLOOD[1])
	b.put(tail, 1, BLOOD[3])
	b.put(tail + 1, 4, BLOOD[3])
	return outline(b, O)


def proj_turret_bolt():
	return [bolt_frame(f) for f in range(3)]


# ---------------------------------------------------------------- particles / bursts
def sparks(c, cx, cy, n, radius, ramp, size_big, seed, alpha=255, phase=0.0):
	for i in range(n):
		a = (i / n) * math.tau + (hsh(i, seed) % 100) / 100.0 * 0.6 + phase
		r = radius * (0.7 + (hsh(i, seed, 3) % 60) / 100.0)
		x = cx + math.cos(a) * r
		y = cy + math.sin(a) * r
		col = ramp
		xi, yi = int(math.floor(x)), int(math.floor(y))
		c.put(xi, yi, A(col, alpha))
		if size_big:
			c.put(xi + 1, yi, A(col, alpha * 0.7))
			c.put(xi, yi + 1, A(col, alpha * 0.7))


def impact_frame(f):
	c = Canvas(16, 16)
	cx, cy = 8, 8
	if f == 0:
		disc(c, cx, cy, 3.0, A(EMBER[2], 255))
		disc(c, cx, cy, 2.0, GOLD[4])
		for d in (-1, 1):
			c.put(cx + d * 5, cy, EMBER[3])
			c.put(cx, cy + d * 5, EMBER[3])
	elif f == 1:
		disc(c, cx, cy, 2.0, EMBER[3])
		for i in range(8):
			a = i * math.tau / 8
			for r in (3, 4, 5):
				col = EMBER[3] if r == 3 else EMBER[2] if r == 4 else EMBER[1]
				c.put(int(cx + math.cos(a) * r), int(cy + math.sin(a) * r), col)
	elif f == 2:
		sparks(c, cx, cy, 10, 5.5, EMBER[2], True, 5)
		sparks(c, cx, cy, 6, 3.0, EMBER[3], False, 9)
		c.put(cx, cy, A(EMBER[3], 200))
	elif f == 3:
		sparks(c, cx, cy + 1, 9, 6.5, EMBER[1], True, 5, 230)
		sparks(c, cx, cy, 5, 4.0, EMBER[2], False, 9, 200)
	else:
		sparks(c, cx, cy + 3, 7, 6.5, BLOOD[2], False, 5, 170)
		sparks(c, cx, cy + 2, 4, 5.0, EMBER[1], False, 3, 140)
	return c


def vfx_turret_impact():
	return [impact_frame(f) for f in range(5)]


def muzzle_frame(f):
	c = Canvas(12, 12)
	length = [11, 9, 6, 3][f]
	hh = [4.5, 4.0, 3.0, 1.8][f]
	for x in range(0, length + 1):
		k = x / max(length, 1)
		half = hh * (1 - k) ** 0.8 + 0.5 if x else hh * 0.6
		half = hh * (1 - k * k) + 0.6
		for y in range(12):
			d = abs(y + 0.5 - 6)
			if d <= half:
				col = EMBER[1]
				if d <= half * 0.7:
					col = EMBER[2]
				if d <= half * 0.4:
					col = EMBER[3]
				if d <= half * 0.2 and k < 0.8:
					col = GOLD[4]
				c.put(x, y, col if f < 3 else A(col, 200))
	for i in range(3 + (3 - f)):
		x = 3 + (hsh(f, i) % 8)
		y = 6 + ((hsh(i, f, 4) % 9) - 4)
		c.put(x, y, A(EMBER[3], 220 - f * 40))
	return c


def vfx_turret_muzzle():
	return [muzzle_frame(f) for f in range(4)]


# ---------------------------------------------------------------- trap_poison_plant
def plant_frame(bob, op, sway, burst):
	b = Canvas(28, 28)
	# roots and thorn vines (ground = row 27)
	for y in range(23, 28):
		for x in range(11, 17):
			if (x == 11 and y < 25) or (x == 16 and y < 25):
				continue
			b.put(x, y, SLIME_GREEN[1] if x < 14 else SLIME_GREEN[0])
	vines = [(-1, 0), (1, 0)]
	for side, _ in vines:
		for i in range(7):
			x = 13 + side * (2 + i) + (0 if side > 0 else -1)
			y = 26 - (i // 3) + (1 if i == 6 else 0) - (sway if i > 3 else 0) * 0
			b.put(x, 26 - (i // 3), SLIME_GREEN[2] if i % 2 else SLIME_GREEN[1])
			b.put(x, 27 - (i // 3) * 0, SLIME_GREEN[0])
		tipx = 13 + side * 9 + (0 if side > 0 else -1)
		b.put(tipx, 24 - sway, CORRUPT[4])
		b.put(tipx - side, 25, CORRUPT[3])
		b.put(13 + side * 5 + (0 if side > 0 else -1), 24, CORRUPT[4])
	# thorn spikes radiating from the bulb (back / right)
	cx, cy = 13.5, 16.5 - bob
	for deg, ln in ((-112, 4), (-84, 5), (-58, 5), (-32, 4), (-4, 4), (24, 3), (-150, 3)):
		ang = math.radians(deg + sway * 4)
		for i in range(-1, ln):
			x = int(math.floor(cx + math.cos(ang) * (6.8 + i) + 0.5))
			y = int(math.floor(cy + math.sin(ang) * (5.8 + i) + 0.5))
			b.put(x, y, CORRUPT[2] if i < ln - 2 else CORRUPT[4])
		b.put(x, y, BLOOD[3])
	# bulb
	ry = 6.5 + (bob * 0.5)
	for y in range(28):
		for x in range(28):
			nx = (x + 0.5 - cx) / 7.5
			ny = (y + 0.5 - cy) / ry
			d = nx * nx + ny * ny
			if d <= 1.0:
				lit = -nx * 0.6 - ny * 0.7
				col = CORRUPT[3] if lit > 0.45 else CORRUPT[2] if lit > -0.1 else CORRUPT[1] if lit > -0.6 else CORRUPT[0]
				if hsh(x, y, 11) % 7 == 0 and ny > -0.2:
					col = SLIME_GREEN[1] if lit < 0.2 else SLIME_GREEN[2]
				if hsh(x, y, 13) % 17 == 0:
					col = SLIME_GREEN[3]
				b.put(x, y, col)
	# maw on the upper left (plant faces LEFT like the enemies)
	mx, my = 9.6, 13.5 - bob
	rx, ryy = 3.6 + 1.6 * op, 1.4 + 3.2 * op
	for y in range(28):
		for x in range(28):
			nx = (x + 0.5 - mx) / rx
			ny = (y + 0.5 - my) / ryy
			if nx * nx + ny * ny <= 1.0:
				col = CORRUPT[0] if ny < 0.1 else SLIME_GREEN[2] if ny < 0.6 else SLIME_GREEN[3]
				b.put(x, y, col)
	# teeth (pale spikes) along the maw rim
	n_teeth = 4
	for k in range(n_teeth):
		tx = int(round(mx - rx + 1 + k * (2 * rx - 2) / (n_teeth - 1)))
		ny = (tx + 0.5 - mx) / rx
		hh = ryy * math.sqrt(max(0.0, 1 - ny * ny))
		top = int(math.floor(my - hh))
		bot = int(math.ceil(my + hh)) - 1
		b.put(tx, top, SLIME_GREEN[4])
		b.put(tx, top + 1, SLIME_GREEN[4])
		if op > 0.05 or k % 2:
			b.put(tx + (1 if k % 2 else -1), bot, SLIME_GREEN[4])
	b = outline(b, O)
	c = Canvas(28, 28)
	c.blit(b, 0, 0)
	if burst:
		# toxic spit: bright droplets out of the maw towards the left
		for i, (ox, oy) in enumerate(((-2, -2), (-4, 0), (-3, 3), (0, -4))):
			x, y = int(mx) + ox - burst, int(my) + oy - burst // 2
			c.put(x, y, SLIME_GREEN[4])
			c.put(x + 1, y, SLIME_GREEN[3])
			c.put(x, y + 1, CORRUPT[4])
	return c


def trap_poison_plant():
	idle = [(0, 0.2, 0), (0, 0.3, 1), (1, 0.35, 1), (1, 0.3, 0), (1, 0.25, -1), (0, 0.2, -1)]
	frames = [plant_frame(b, o, s, 0) for (b, o, s) in idle]
	frames.append(plant_frame(1, 1.0, 0, 0))
	frames.append(plant_frame(-1, 0.0, 0, 1))
	frames.append(plant_frame(0, 0.55, 0, 3))
	return frames


def spores_frame(f):
	c = Canvas(20, 16)
	k = f / 4.0
	pts = [(-6, 0), (-3, -3), (0, -1), (3, -4), (6, -1), (1, -6), (-5, -5), (4, 1)]
	for i, (ox, oy) in enumerate(pts):
		x = 10 + ox * (0.5 + 0.9 * k)
		y = 12 + oy * (0.7 + 0.8 * k) - 4 * k
		r = 1.6 - 0.1 * (i % 3) - 0.25 * k
		if f == 0 and i > 4:
			continue
		a = 235 - 45 * f
		body = SLIME_GREEN[3] if i % 2 else CORRUPT[3]
		rim = SLIME_GREEN[1] if i % 2 else CORRUPT[1]
		disc(c, x, y, r + 0.7, A(rim, a * 0.8))
		disc(c, x, y, max(r - 0.2, 0.8), A(body, a))
		c.put(int(x - 1), int(y - 1), A(SLIME_GREEN[4], a * 0.9))
	return c


def vfx_poison_spores():
	return [spores_frame(f) for f in range(5)]


# ---------------------------------------------------------------- item_magic_shield
SHIELD_ROWS = [6, 6, 6, 6, 6, 6, 6, 5, 5, 4, 4, 3, 2, 1]


def shield_frame(f):
	dy = [0, -1, -1, 0, 0, 0][f]
	sweep = [-3, 0, 4, 8, 12, 17][f]
	b = Canvas(16, 16)
	for i, w in enumerate(SHIELD_ROWS):
		y = 1 + i
		for x in range(8 - w, 8 + w):
			col = BLUE[2] if x < 8 else BLUE[1]
			if i > 8:
				col = BLUE[1] if x < 8 else BLUE[0]
			edge = x in (8 - w, 7 + w) or i == 0
			if edge:
				col = BLUE[3] if (x < 8 or i == 0) else BLUE[2]
			b.put(x, y, col)
	# rune: pale sigil (cross with a lozenge), reads as "protection"
	for (x, y) in ((7, 4), (8, 4), (7, 5), (8, 5), (6, 6), (9, 6), (7, 7), (8, 7), (7, 8), (8, 8), (7, 9), (8, 9), (7, 10)):
		b.put(x, y, BLUE[4])
	for x in range(5, 11):
		b.put(x, 6, BLUE[4]) if x not in (6, 9) else None
	b.put(8, 10, BLUE[3])
	b.put(7, 11, None) if False else None
	# reflection sweep (diagonal)
	for y in range(1, 15):
		for x in range(2, 14):
			if b.get(x, y) is not None and x + y * 0.9 == sweep or (b.get(x, y) is not None and int(x + y * 0.9) == sweep):
				c0 = b.get(x, y)
				b.put(x, y, BLUE[4] if c0 in (BLUE[3], BLUE[2]) else BLUE[3])
	b = outline(b, O)
	c = Canvas(16, 16)
	c.blit(b, 0, dy)
	return c


def item_magic_shield():
	return [shield_frame(f) for f in range(6)]


# ---------------------------------------------------------------- shield aura / end / pickup
def aura_pixels(rx, ry, cx, cy):
	"""Yield (x, y, kind, angle) for ring (kind 'e') and interior ('i') of an ellipse."""
	out = []
	for y in range(40):
		for x in range(36):
			nx = (x + 0.5 - cx) / rx
			ny = (y + 0.5 - cy) / ry
			d = math.sqrt(nx * nx + ny * ny)
			dist = (d - 1.0) * (rx + ry) * 0.5
			ang = math.atan2(ny, nx)
			if -1.0 <= dist <= 0.2:
				out.append((x, y, "e", ang))
			elif dist < -1.0:
				out.append((x, y, "i", ang))
	return out


def aura_frame(f, end=False):
	c = Canvas(36, 40)
	breath = [0.0, 0.4, 0.7, 0.4, 0.0, -0.3][f % 6]
	rx, ry = 15.8 + breath * 0.5, 16.8 + breath * 0.6
	cx, cy = 18.0, 17.5
	for (x, y, kind, ang) in aura_pixels(rx, ry, cx, cy):
		if kind == "i":
			# interior: very light cyan, a bit more at the lower rim, never above ~12 %
			ny = (y + 0.5 - cy) / ry
			a = 18 + int(10 * max(ny, 0))
			c.put(x, y, A(BLUE[2], a))
		else:
			lit = -math.cos(ang - math.radians(-130))
			col = BLUE[4] if lit > 0.85 else BLUE[3] if lit > 0.1 else BLUE[2]
			a = 215 if lit > 0.1 else 175
			if ang > 0.3 and ang < 2.8:
				col = BLUE[3]
				a = 150
			c.put(x, y, A(col, a))
	# glossy reflection arcs (top-left) and a slow shimmer travelling around the rim
	for i in range(8):
		t = math.radians(-155 + i * 6)
		c.put(int(cx + math.cos(t) * (rx - 2.4)), int(cy + math.sin(t) * (ry - 2.4)), A(WHITE, 200))
	for i in range(4):
		t = math.radians(-110 + i * 5)
		c.put(int(cx + math.cos(t) * (rx - 2.4)), int(cy + math.sin(t) * (ry - 2.4)), A(BLUE[4], 150))
	sh = math.radians(f * 60 + 20)
	for j in range(3):
		t = sh + j * 0.09
		c.put(int(cx + math.cos(t) * rx), int(cy + math.sin(t) * ry), A(WHITE, 255))
	# ground contact ring (feet = row 34)
	for x in range(10, 26):
		k = (x - 17.5) / 8.0
		y = 34 + (0 if abs(k) < 0.6 else -0)
		c.put(x, 34, A(BLUE[3], 150 if abs(k) < 0.85 else 90))
	return c


def vfx_shield_aura():
	return [aura_frame(f) for f in range(6)]


def end_frame(f):
	c = Canvas(36, 40)
	cx, cy = 18.0, 17.5
	rx, ry = 15.8, 16.8
	if f == 0:
		c = aura_frame(0)
		# cracks + brighter flash
		for (x, y) in ((11, 8), (12, 9), (12, 10), (13, 11), (13, 12), (24, 22), (25, 23), (25, 24), (24, 25), (15, 29), (16, 30), (17, 30)):
			c.put(x, y, A(WHITE, 255))
		for (x, y, kind, ang) in aura_pixels(rx, ry, cx, cy):
			if kind == "i":
				c.put(x, y, A(BLUE[3], 34))
		return c
	nsec = 14
	spread = [0, 2.0, 4.0, 6.0, 8.0][f]
	fade = [1, 0.85, 0.6, 0.35, 0.15][f]
	for (x, y, kind, ang) in aura_pixels(rx, ry, cx, cy):
		if kind != "e":
			continue
		sec = int(((ang + math.pi) / math.tau) * nsec) % nsec
		# some sectors vanish early, the rest drift outwards
		if (sec * 5 + 3) % 7 < f - 1:
			continue
		ux, uy = math.cos(ang), math.sin(ang)
		jitter = 0.6 + 0.8 * ((sec * 37) % 10) / 10.0
		nx = int(round(x + ux * spread * jitter))
		ny = int(round(y + uy * spread * jitter + (f - 1) * 0.8))
		if hsh(x, y, f) % 5 == 0:
			continue
		lit = -math.cos(ang - math.radians(-130))
		col = BLUE[4] if lit > 0.6 else BLUE[3]
		c.put(nx, ny, A(col, 235 * fade))
	if f <= 2:
		for i in range(10):
			a = i * math.tau / 10 + 0.3
			r = (spread * 0.8) + 4 + (hsh(i, f) % 4)
			c.put(int(cx + math.cos(a) * r * 1.1), int(cy + math.sin(a) * r * 1.1), A(WHITE, 220 * fade))
	return c


def vfx_shield_end():
	return [end_frame(f) for f in range(5)]


def star(c, cx, cy, ln, col, alpha=255, diag=False):
	for i in range(1, ln + 1):
		for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
			c.put(cx + dx * i, cy + dy * i, A(col, alpha * (1 - 0.5 * i / (ln + 1))))
		if diag and i <= ln // 2:
			for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
				c.put(cx + dx * i, cy + dy * i, A(col, alpha * 0.8))
	c.put(cx, cy, A(col, alpha))


def ring(c, cx, cy, r, col, alpha, thick=0.7, ry=None):
	ry = ry or r
	for y in range(c.h):
		for x in range(c.w):
			d = math.hypot((x + 0.5 - cx) / r, (y + 0.5 - cy) / ry) * ((r + ry) / 2)
			if abs(d - (r + ry) / 2) <= thick:
				c.put(x, y, A(col, alpha))


def shield_pickup_frame(f):
	c = Canvas(32, 32)
	cx = cy = 16
	if f == 0:
		disc(c, cx, cy, 4.0, A(BLUE[3], 230))
		disc(c, cx, cy, 2.5, WHITE)
		star(c, cx, cy, 5, WHITE, 255)
	elif f == 1:
		disc(c, cx, cy, 3.0, A(BLUE[4], 240))
		star(c, cx, cy, 9, BLUE[4], 255, True)
		ring(c, cx, cy, 6, BLUE[3], 220)
	elif f == 2:
		ring(c, cx, cy, 9.5, BLUE[3], 230, 0.9)
		ring(c, cx, cy, 6, BLUE[4], 200)
		star(c, cx, cy, 12, BLUE[4], 230)
		sparks(c, cx, cy, 8, 10, WHITE, False, 21)
	elif f == 3:
		ring(c, cx, cy, 12.5, BLUE[3], 190, 0.8)
		ring(c, cx, cy, 8, BLUE[2], 140)
		sparks(c, cx, cy, 10, 12, BLUE[4], True, 23)
	elif f == 4:
		ring(c, cx, cy, 14.5, BLUE[2], 120, 0.7)
		sparks(c, cx, cy - 1, 10, 13, BLUE[3], False, 25, 200)
		sparks(c, cx, cy - 1, 6, 8, WHITE, False, 27, 200)
	else:
		sparks(c, cx, cy - 3, 8, 14, BLUE[3], False, 29, 130)
		sparks(c, cx, cy - 2, 4, 10, WHITE, False, 31, 110)
	return c


def vfx_shield_pickup():
	return [shield_pickup_frame(f) for f in range(6)]


# ---------------------------------------------------------------- item_hp_bonus
HEART = ["XX.XX", "XXXXX", "XXXXX", ".XXX.", "..X.."]


def hp_frame(f):
	pul = [0, 1, 2, 3, 2, 1][f]
	b = Canvas(16, 16)
	# pale-gold octagonal setting with four prongs (not a bottle, not a flat HUD heart)
	oct_rows = {1: (5, 10), 2: (3, 12), 3: (2, 13), 4: (1, 14), 5: (1, 14), 6: (1, 14), 7: (1, 14), 8: (1, 14), 9: (1, 14), 10: (1, 14), 11: (2, 13), 12: (3, 12), 13: (5, 10)}
	for y, (x0, x1) in oct_rows.items():
		for x in range(x0, x1 + 1):
			edge = x in (x0, x1) or y in (1, 13)
			col = GOLD[3] if edge else GOLD[1]
			if edge and (x + y) % 5 == 0:
				col = GOLD[4]
			if edge and x >= 8 and y >= 7:
				col = GOLD[2]
			b.put(x, y, col)
	# dark enamel back plate
	for y in range(3, 12):
		for x in range(3, 13):
			if (x, y) in ((3, 3), (12, 3), (3, 11), (12, 11)):
				continue
			if b.get(x, y) is not None and b.get(x, y) not in (GOLD[3],):
				b.put(x, y, BLOOD[0])
	# prongs
	for (x, y) in ((7, 0), (8, 0), (0, 7), (0, 8), (15, 7), (15, 8), (7, 14), (8, 14)):
		b.put(x, y, GOLD[3] if x < 8 else GOLD[2])
	# faceted heart crystal, brightness pulsing
	ramps = [(BLOOD[3], BLOOD[2], BLOOD[1]), (BLOOD[4], BLOOD[3], BLOOD[2]), (BLOOD[4], BLOOD[4], BLOOD[3]), (EMBER[3], BLOOD[4], BLOOD[3])][pul]
	hx, hy = 4, 3
	rows = [".XX..XX.", "XXXXXXXX", "XXXXXXXX", ".XXXXXX.", "..XXXX..", "...XX..."]
	for j, row in enumerate(rows):
		for i, ch in enumerate(row):
			if ch != "X":
				continue
			x, y = hx + i + 0, hy + j
			col = ramps[0] if (i < 4 and j < 3 and i + j < 5) else ramps[1] if (i + j) < 7 else ramps[2]
			b.put(x, y, col)
	b.put(hx + 5, hy + 1, ramps[2]) if False else None
	b.put(hx + 1, hy + 1, WHITE)
	b.put(hx + 1, hy + 2, GOLD[4])
	b.put(hx + 2, hy, GOLD[4] if pul >= 1 else ramps[0])
	if pul >= 2:
		b.put(hx + 6, hy + 1, ramps[0])
	b = outline(b, O)
	c = Canvas(16, 16)
	c.blit(b, 0, 0)
	if pul >= 2:
		for (x, y) in ((7, 1), (14, 8) if pul == 3 else (7, 1)):
			pass
	if pul == 3:
		c.put(2, 2, A(WHITE, 255))
		c.put(1, 2, A(GOLD[4], 200))
		c.put(2, 1, A(GOLD[4], 200))
		c.put(2, 3, A(GOLD[4], 200))
		c.put(3, 2, A(GOLD[4], 200))
	return c


def item_hp_bonus():
	return [hp_frame(f) for f in range(6)]


def hp_pickup_frame(f):
	c = Canvas(32, 32)
	cx, cy = 16, 17
	rise = f * 2.0
	if f <= 1:
		disc(c, cx, cy, 4.5 - f, A(BLOOD[4], 235))
		disc(c, cx, cy, 2.5 - f * 0.5, WHITE)
		star(c, cx, cy, 6 + f * 3, BLOOD[4], 255, True)
	if f >= 1:
		ring(c, cx, cy - rise, 4 + f * 2.2, WHITE, int(255 - f * 14), 0.8, ry=(4 + f * 2.2) * 0.45)
	if f >= 2:
		ring(c, cx, cy - rise * 0.5 + 3, 3 + f * 1.8, BLOOD[4], int(255 - f * 22), 0.7, ry=(3 + f * 1.8) * 0.45)
	sparks(c, cx, cy - rise, 7, 4 + f * 2.2, BLOOD[3], f < 4, 41, int(255 - f * 28))
	sparks(c, cx, cy - rise, 4, 3 + f * 1.8, WHITE, False, 43, int(255 - f * 30), 0.5)
	if f >= 3:
		for i in range(3):
			x = 10 + i * 6 + (hsh(i, f) % 3)
			y = 24 - f * 2 - i
			c.put(x, y, A(BLOOD[4], 220 - f * 20))
			c.put(x, y + 1, A(BLOOD[3], 180 - f * 20))
	return c


def vfx_hp_bonus_pickup():
	return [hp_pickup_frame(f) for f in range(7)]


# ---------------------------------------------------------------- mech_pressure_plate
def plate_frame(f):
	drop = [0, 0, 1, 1, 1][f]
	lit = [0, 1, 2, 3, 3][f]  # groove light level
	c = Canvas(24, 8)
	# bed
	for x in range(24):
		c.put(x, 6, STONE[3] if hsh(x, 3) % 3 else STONE[2])
		c.put(x, 7, STONE[1])
	c.put(0, 6, O)
	c.put(23, 6, O)
	for x in range(24):
		c.put(x, 7, O if hsh(x, 4) % 2 else STONE[0])
	for x in (3, 8, 15, 20):
		c.put(x, 6, STONE[1])
	# plate (20 wide, raised 3 px)
	y0 = 4 + drop
	pl = Canvas(24, 8)
	for x in range(2, 22):
		pl.put(x, y0, STONE[5] if x not in (2, 21) else None)
		pl.put(x, y0 + 1, STONE[4])
		pl.put(x, y0 + 2, STONE[3] if x < 19 else STONE[2])
	pl.put(2, y0 + 1, STONE[5])
	pl.put(2, y0 + 2, STONE[4])
	pl.put(21, y0 + 2, STONE[1])
	# grooves
	groove_cols = [STONE[0], GOLD[1], GOLD[3], GOLD[4]][lit]
	for x in list(range(5, 10)) + list(range(14, 19)):
		pl.put(x, y0 + 1, groove_cols)
	pl.put(11, y0 + 1, groove_cols)
	pl.put(12, y0 + 1, groove_cols)
	pl.put(11, y0, STONE[3] if lit < 2 else GOLD[2])
	pl.put(12, y0, STONE[3] if lit < 2 else GOLD[2])
	if lit >= 2:
		for x in (4, 10, 13, 19):
			pl.put(x, y0 + 1, A(GOLD[3], 200))
	pl = outline(pl, O)
	c.blit(pl, 0, 0)
	if f == 4:
		for (x, y) in ((1, 5), (22, 5)):
			c.put(x, y, A(GOLD[4], 220))
	return c


def mech_pressure_plate():
	return [plate_frame(f) for f in range(5)]


# ---------------------------------------------------------------- mech_button
def button_frame(f):
	c = Canvas(16, 20)
	press = [0, 0, 1, 3, 4, 5][f]
	active = f == 5
	# stone base (ground = row 19)
	b = Canvas(16, 20)
	for y in range(13, 19):
		for x in range(1, 15):
			col = STONE[3]
			if y == 13:
				col = STONE[5]
			elif y == 14:
				col = STONE[4]
			elif y >= 17:
				col = STONE[2]
			if x == 1:
				col = STONE[4] if y < 17 else STONE[3]
			if x == 14:
				col = STONE[2]
			if hsh(x, y, 5) % 11 == 0:
				col = STONE[2]
			b.put(x, y, col)
	b.put(3, 16, STEEL[3])
	b.put(12, 16, STEEL[3])
	b = outline(b, O)
	c.blit(b, 0, 0)
	# button stem and cap (cap sinks when pressed)
	top = 6 + press
	if active:
		top = 11
	cap_h = 5 if not active else 3
	cap = Canvas(16, 20)
	for y in range(top, top + cap_h):
		k = (y - top)
		w = 4 - (1 if k == 0 else 0)
		for x in range(8 - w, 8 + w):
			if active:
				col = GOLD[3] if x < 8 else GOLD[2]
				if y == top:
					col = GOLD[4]
			else:
				col = EMBER[2] if x < 8 else EMBER[1]
				if y == top:
					col = EMBER[3]
				if k >= cap_h - 1:
					col = BLOOD[2]
			cap.put(x, y, col)
	if not active:
		cap.put(6, top, GOLD[4] if f in (0, 2) else EMBER[3])
		cap.put(5, top + 1, EMBER[3])
		if f == 1:
			cap.put(10, top + 1, GOLD[4])
	cap = outline(cap, O)
	# stem between cap and base
	stem_top = top + cap_h
	for y in range(stem_top, 13):
		for x in (6, 7, 8, 9):
			c.put(x, y, STEEL[2] if x < 8 else STEEL[1])
		c.put(5, y, O)
		c.put(10, y, O)
	c.blit(cap, 0, 0)
	if active:
		for (x, y) in ((3, 10), (12, 10), (2, 12), (13, 12), (8, 7), (5, 8), (11, 8)):
			c.put(x, y, A(GOLD[4], 230))
		for x in range(4, 12):
			c.put(x, 10, A(GOLD[3], 160)) if c.get(x, 10) is None else None
	if f in (3, 4):
		c.put(2, 12, A(GOLD[4], 220))
		c.put(13, 12, A(GOLD[4], 220))
	return c


def mech_button():
	return [button_frame(f) for f in range(6)]


# ---------------------------------------------------------------- mech_door
def brick(c, x0, y0, x1, y1, seed, theme=0):
	"""Masonry in the terrain stone tones with dark mortar."""
	for y in range(y0, y1 + 1):
		for x in range(x0, x1 + 1):
			row = (y - y0) // 5
			off = (row * 5) % 8
			mortar = (y - y0) % 5 == 4 or (x - x0 + off) % 8 == 7
			if mortar:
				col = STONE[0]
			else:
				col = STONE[3]
				h = hsh(x, y, seed) % 9
				if h == 0:
					col = STONE[2]
				elif h == 1:
					col = STONE[4]
				if (y - y0) % 5 == 0:
					col = STONE[4]
			c.put(x, y, col)


def cog(c, cx, cy, rot, rbody, rtooth, col_hi, col_mid, col_lo, teeth=8):
	cg = Canvas(c.w, c.h)
	for y in range(c.h):
		for x in range(c.w):
			dx, dy = x + 0.5 - cx, y + 0.5 - cy
			r = math.hypot(dx, dy)
			ang = math.atan2(dy, dx)
			lim = rbody
			if math.cos(teeth * (ang - rot)) > 0.15:
				lim = rtooth
			if r <= lim:
				lit = -(dx + dy) / max(r, 1e-6)
				col = col_hi if lit > 0.5 else col_mid if lit > -0.4 else col_lo
				if r < 1.7:
					col = None
				cg.put(x, y, col)
	cg = outline(cg, O)
	c.blit(cg, 0, 0)


def herse_layer(kind, f, off):
	h = Canvas(24, 56)
	bars = (5, 9, 13, 17)
	for bx in bars:
		for y in range(8, 56):
			if y > 52:
				if y == 55 and False:
					continue
			light = STEEL[3] if kind == 0 else STEEL[3]
			h.put(bx, y, light)
			h.put(bx + 1, y, STEEL[1])
		h.put(bx, 55, STEEL[4])
		h.put(bx + 1, 55, None)
	for y0 in (14, 30, 46):
		for x in range(4, 20):
			h.put(x, y0, STEEL[2] if kind == 0 else STEEL[3])
			h.put(x, y0 + 1, STEEL[0])
	# rivets where bars cross
	for y0 in (14, 30, 46):
		for bx in bars:
			h.put(bx, y0, STEEL[4])
	out = Canvas(24, 56)
	for y in range(56):
		for x in range(24):
			p = h.get(x, y)
			if p is not None and 0 <= y - off < 56:
				pass
	# vertical shift (rise): move pixels up by `off`
	for y in range(56):
		for x in range(24):
			p = h.get(x, y)
			if p is not None and y - off >= 8:
				out.put(x, y - off, p)
	return out


def door_frame(kind, f):
	off = [0, 0, 0, 0, 4, 10, 17, 24, 31, 37, 42][f]
	c = Canvas(24, 56)
	# jambs
	brick(c, 0, 10, 3, 55, 21)
	brick(c, 20, 10, 23, 55, 22)
	for y in range(10, 56):
		c.put(0, y, STONE[2])
		c.put(3, y, STONE[1])
		c.put(20, y, STONE[2])
		c.put(23, y, STONE[1])
	hs = herse_layer(kind, f, off)
	# attached emblem (moves with the portcullis)
	emb = Canvas(24, 56)
	if kind == 0:
		lx, ly = 12, 31
		dxs, dys = 0, 0
		drop = 0
		show = f <= 3
		if f == 1:
			dxs = 1
		elif f == 2:
			dxs = -1
			drop = 2
		elif f == 3:
			drop = 12
		if show:
			lk = Canvas(24, 56)
			# shackle
			sh_y = ly - 7 - (3 if f == 2 else 0)
			if f < 3:
				for y in range(sh_y, sh_y + 4):
					lk.put(lx - 3, y, GOLD[1])
					lk.put(lx - 2, y, GOLD[3])
					lk.put(lx + 2, y, GOLD[1])
					lk.put(lx + 1, y, GOLD[2])
				for x in range(lx - 2, lx + 2):
					lk.put(x, sh_y, GOLD[3])
			# body
			for y in range(ly - 3, ly + 4):
				for x in range(lx - 4, lx + 4):
					col = GOLD[3] if x < lx else GOLD[2]
					if y == ly - 3:
						col = GOLD[4]
					elif y >= ly + 2:
						col = GOLD[1]
					lk.put(x, y, col)
			# coin symbol on the lock
			disc(lk, lx - 0.5 + 0.5, ly - 0.5, 2.2, GOLD[4])
			disc(lk, lx - 0.5 + 0.5, ly - 0.5, 1.4, GOLD[2])
			lk.put(lx, ly - 1, GOLD[0])
			lk.put(lx, ly, GOLD[0])
			lk = outline(lk, O)
			if f == 3:
				for p in range(len(lk.px)):
					if lk.px[p] is not None:
						lk.px[p] = A(lk.px[p], 190)
			if f in (1, 2):
				lk.put(lx - 4, ly - 4, WHITE)
				lk.put(lx - 5, ly - 4, A(GOLD[4], 200))
				lk.put(lx - 4, ly - 5, A(GOLD[4], 200))
			emb.blit(lk, dxs, drop)
	else:
		rot = [0.0, 0.2, 0.4, 0.55, 0, 0, 0, 0, 0, 0, 0][f]
		if f in (1, 2, 3):
			for (gx, gy) in ((12, 22), (4, 31), (19, 31), (12, 41)):
				pass
			disc(emb, 12, 32, 9.0, A(GOLD[4], 32 + 14 * f))
		cog(emb, 12, 32, rot, 4.5, 6.6, STEEL[4], STEEL[3], STEEL[1])
		# pale rune ticks beside the cog
		for (x, y) in ((6, 24), (17, 24), (6, 40), (17, 40)):
			c0 = GOLD[4] if f in (2, 3) else STEEL[3]
			emb.put(x, y, c0)
			emb.put(x + 1, y, c0) if x < 12 else emb.put(x - 1, y, c0)
	# apply emblem with the same rise offset (row 0 lock only exists before rise)
	if kind == 1 and off:
		em2 = Canvas(24, 56)
		for y in range(56):
			for x in range(24):
				p = emb.get(x, y)
				if p is not None and y - off >= 8:
					em2.put(x, y - off, p)
		emb = em2
	# opened: tips of the portcullis stay visible under the lintel
	c.blit(hs, 0, 0)
	c.blit(emb, 0, 0)
	# lintel (full width, covers the top of the portcullis)
	lt = Canvas(24, 56)
	brick(lt, 0, 0, 23, 9, 30)
	for x in range(24):
		lt.put(x, 0, STONE[4])
		lt.put(x, 9, STONE[1])
	for y in range(10):
		lt.put(0, y, STONE[2] if y else STONE[3])
		lt.put(23, y, STONE[1])
	# medallion
	if kind == 0:
		disc(lt, 12, 5, 4.2, GOLD[1])
		disc(lt, 12, 5, 3.4, GOLD[3])
		disc(lt, 12, 5, 2.2, GOLD[2])
		for y in range(3, 8):
			lt.put(12, y, GOLD[4])
		lt.put(11, 3, GOLD[4])
		lt.put(13, 3, GOLD[4])
		if f in (1, 2, 3):
			lt.put(9, 2, WHITE)
			lt.put(15, 8, A(GOLD[4], 255))
	else:
		disc(lt, 12, 5, 4.2, STEEL[0])
		disc(lt, 12, 5, 3.4, STEEL[2])
		disc(lt, 12, 5, 2.2, STEEL[0])
		for (x, y) in ((12, 3), (12, 7), (10, 5), (14, 5)):
			lt.put(x, y, STEEL[4])
		lt.put(12, 5, GOLD[4] if f in (1, 2, 3) else STEEL[3])
	lt = outline(lt, O)
	for y in range(10, 56):
		for x in range(24):
			if lt.get(x, y) == O and False:
				lt.put(x, y, None)
	for y in range(11, 56):
		for x in range(24):
			lt.put(x, y, None)
	# the outline row under the lintel must not paint over the portcullis tips
	if lt.get(12, 10) is not None and False:
		pass
	c.blit(lt, 0, 0)
	c = outline(c, O) if False else c
	return c


def mech_door():
	frames = []
	for kind in (0, 1):
		for f in range(11):
			frames.append(door_frame(kind, f))
	return sheet(frames, 11)


# ---------------------------------------------------------------- env_secret_wall / crumble
_TERRAIN_CACHE = {}


def terrain_tile(row):
	"""Pixels of tile (column 0 = fully enclosed masonry) at tile row `row` from terrain_stone.png."""
	if "img" not in _TERRAIN_CACHE:
		with open(TERRAIN, "rb") as fh:
			data = fh.read()
		pos, idat, w, h = 8, b"", 0, 0
		while pos < len(data):
			n = struct.unpack(">I", data[pos:pos + 4])[0]
			kind = data[pos + 4:pos + 8]
			body = data[pos + 8:pos + 8 + n]
			if kind == b"IHDR":
				w, h = struct.unpack(">II", body[:8])
			elif kind == b"IDAT":
				idat += body
			pos += 12 + n
		raw = zlib.decompress(idat)
		img = Canvas(w, h)
		stride = w * 4
		prev = bytearray(stride)
		i = 0
		for y in range(h):
			ft = raw[i]
			ln = bytearray(raw[i + 1:i + 1 + stride])
			i += 1 + stride
			for x in range(stride):
				a = ln[x - 4] if x >= 4 else 0
				b = prev[x]
				cc = prev[x - 4] if x >= 4 else 0
				if ft == 1:
					ln[x] = (ln[x] + a) & 255
				elif ft == 2:
					ln[x] = (ln[x] + b) & 255
				elif ft == 3:
					ln[x] = (ln[x] + (a + b) // 2) & 255
				elif ft == 4:
					p = a + b - cc
					pa, pb, pc = abs(p - a), abs(p - b), abs(p - cc)
					pr = a if pa <= pb and pa <= pc else b if pb <= pc else cc
					ln[x] = (ln[x] + pr) & 255
			prev = ln
			for x in range(w):
				px = tuple(ln[x * 4:x * 4 + 4])
				if px[3]:
					img.put(x, y, px)
		_TERRAIN_CACHE["img"] = img
	img = _TERRAIN_CACHE["img"]
	t = Canvas(16, 16)
	for y in range(16):
		for x in range(16):
			t.put(x, y, img.get(x, row * 16 + y))
	return t


def secret_wall_base():
	w = Canvas(16, 32)
	w.blit(terrain_tile(1), 0, 0)
	w.blit(terrain_tile(2), 0, 16)
	return w


def env_secret_wall():
	base = secret_wall_base()
	hint = base.copy()
	crack = [(9, 6), (9, 7), (8, 8), (8, 9), (9, 10), (9, 11), (10, 12), (10, 13), (9, 14), (9, 15), (8, 16), (8, 17), (7, 18)]
	for (x, y) in crack:
		hint.put(x, y, STONE[0])
	for (x, y) in crack[::3]:
		hint.put(x + 1, y, STONE[4])
	return [base, hint]


def crumble_frame(f):
	base = secret_wall_base()
	c = Canvas(32, 40)
	ox, oy = 8, 4  # wall region x 8..23, y 4..35 (ground = row 36)
	# chunk layout: (x, y, w, h) inside the 16x32 wall
	chunks = []
	rows = [(0, 8), (8, 8), (16, 8), (24, 8)]
	for ri, (ry, rh) in enumerate(rows):
		cuts = [0, 6 + (ri % 2) * 3, 11 + (ri % 2) * 2, 16] if ri % 2 == 0 else [0, 5, 10, 16]
		cuts = [0, 5 + (ri % 3), 10 + (ri % 2), 16]
		for a, b in zip(cuts[:-1], cuts[1:]):
			chunks.append((a, ry, b - a, rh))
	ch = Canvas(32, 40)
	for i, (x, y, w, h) in enumerate(chunks):
		delay = 0 if y >= 16 else 0
		delay = (3 - y // 8) * 0.0 + (i % 3) * 0.35
		t = max(0.0, f - 0.5 - delay)
		if f == 0:
			t = 0
		vy = 0.9 + (i % 4) * 0.35
		drift = ((i * 7) % 5 - 2) * 0.7
		fall = vy * t + 0.55 * t * t
		nx = ox + x + drift * t + (1 if f >= 1 and (i % 2) else 0) * (0 if f == 0 else 0)
		ny = oy + y + fall
		bottom = ny + h
		rest = False
		if bottom > 37:
			ny = 37 - h
			rest = True
		if f >= 5 and not rest:
			continue
		if f == 6 and (i % 3) != 0:
			continue
		for yy in range(h):
			for xx in range(w):
				p = base.get(x + xx, y + yy)
				if p is not None:
					ch.put(int(round(nx)) + xx, int(round(ny)) + yy, p if not (rest and f >= 5) else A(p, 255))
	ch = outline(ch, O) if f > 0 else ch
	if f == 0:
		ch = Canvas(32, 40)
		ch.blit(base, ox, oy)
		for (x, y) in ((16, 10), (16, 11), (15, 12), (15, 13), (16, 14), (16, 15), (17, 16), (16, 17)):
			ch.put(x, y, A(GOLD[4], 255))
	c.blit(ch, 0, 0)
	# dust clouds
	puffs = [(10, 33), (16, 35), (22, 33), (13, 24), (19, 14), (11, 8), (21, 26), (16, 20)]
	for i, (px, py) in enumerate(puffs):
		if f == 0 and i > 2:
			continue
		r = (1.3 + f * 0.55 + (i % 3) * 0.3) if f < 6 else 2.4 + (i % 2)
		a = [70, 105, 115, 105, 85, 60, 35][f]
		rise = f * 1.0
		cxp = px + (px - 16) * 0.12 * f
		disc(c, cxp, py - rise, r, A(STONE[5], a))
		disc(c, cxp - 0.5, py - rise - 0.5, max(r - 1.2, 0.8), A(STONE[4] if i % 2 else (96, 90, 84, 255), a))
	return c


def vfx_secret_crumble():
	return [crumble_frame(f) for f in range(7)]


# ---------------------------------------------------------------- dust / activation vfx
def door_dust_frame(f):
	c = Canvas(32, 12)
	spread = [2, 6, 10, 13, 15][f]
	alpha = [210, 230, 200, 140, 80][f]
	rad = [2.2, 3.0, 3.6, 3.4, 2.8][f]
	rise = [0.5, 1.5, 2.5, 3.5, 4.5][f]
	for side in (-1, 1):
		for j, k in enumerate((0.45, 0.8, 1.0)):
			x = 16 + side * spread * k
			y = 9.5 - rise * (0.6 + 0.3 * j) + (j == 1) * -0.5
			r = rad * (1.0 - 0.15 * j)
			disc(c, x, y, r, A(STONE[5], alpha))
			disc(c, x - 0.6, y - 0.7, max(r - 1.1, 0.7), A((150, 142, 132, 255), alpha))
	disc(c, 16, 9.5 - rise * 0.5, rad + 1.0, A(STONE[5], int(alpha * 0.8)))
	for i in range(4):
		x = 16 + ((hsh(i, f) % 21) - 10) * (0.5 + 0.1 * f)
		c.put(int(x), 6 - f // 2 - (i % 3), A(STONE[4], alpha))
	return c


def vfx_door_dust():
	return [door_dust_frame(f) for f in range(5)]


def activate_frame(f):
	c = Canvas(24, 16)
	cx, cy = 12, 12
	if f == 0:
		disc(c, cx, cy, 2.5, A(GOLD[4], 240))
		disc(c, cx, cy, 1.4, WHITE)
		star(c, cx, cy, 3, GOLD[4], 255)
	elif f == 1:
		star(c, cx, cy, 6, GOLD[4], 255, True)
		disc(c, cx, cy, 1.6, WHITE)
		ring(c, cx, cy, 4, GOLD[3], 200, 0.7, ry=2.2)
	elif f == 2:
		ring(c, cx, cy, 7, GOLD[3], 210, 0.8, ry=3.4)
		sparks(c, cx, cy - 1, 8, 7, GOLD[4], False, 51)
		disc(c, cx, cy, 1.5, A(WHITE, 230))
	elif f == 3:
		ring(c, cx, cy, 10, GOLD[2], 150, 0.7, ry=4.4)
		sparks(c, cx, cy - 2, 8, 8.5, GOLD[4], False, 53, 220)
	else:
		sparks(c, cx, cy - 3, 6, 9.5, GOLD[3], False, 55, 140)
	return c


def vfx_mech_activate():
	return [activate_frame(f) for f in range(5)]


# ---------------------------------------------------------------- driver
# name -> (builder, cell_w, cell_h, frames, rows)
FILES = {
	"trap_spikes_retract": (trap_spikes_retract, 32, 16, 13, 1),
	"trap_trapdoor": (trap_trapdoor, 32, 20, 10, 1),
	"trap_turret": (trap_turret, 24, 24, 10, 1),
	"proj_turret_bolt": (proj_turret_bolt, 12, 6, 3, 1),
	"vfx_turret_impact": (vfx_turret_impact, 16, 16, 5, 1),
	"vfx_turret_muzzle": (vfx_turret_muzzle, 12, 12, 4, 1),
	"trap_poison_plant": (trap_poison_plant, 28, 28, 9, 1),
	"vfx_poison_spores": (vfx_poison_spores, 20, 16, 5, 1),
	"item_magic_shield": (item_magic_shield, 16, 16, 6, 1),
	"vfx_shield_aura": (vfx_shield_aura, 36, 40, 6, 1),
	"vfx_shield_end": (vfx_shield_end, 36, 40, 5, 1),
	"vfx_shield_pickup": (vfx_shield_pickup, 32, 32, 6, 1),
	"item_hp_bonus": (item_hp_bonus, 16, 16, 6, 1),
	"vfx_hp_bonus_pickup": (vfx_hp_bonus_pickup, 32, 32, 7, 1),
	"mech_pressure_plate": (mech_pressure_plate, 24, 8, 5, 1),
	"mech_button": (mech_button, 16, 20, 6, 1),
	"mech_door": (mech_door, 24, 56, 11, 2),
	"env_secret_wall": (env_secret_wall, 16, 32, 2, 1),
	"vfx_secret_crumble": (vfx_secret_crumble, 32, 40, 7, 1),
	"vfx_door_dust": (vfx_door_dust, 32, 12, 5, 1),
	"vfx_mech_activate": (vfx_mech_activate, 24, 16, 5, 1),
}


def flatten(canvas, bg=(40, 44, 52)):
	"""Composite over an opaque background so alpha VFX read correctly in previews."""
	out = Canvas(canvas.w, canvas.h)
	for i, p in enumerate(canvas.px):
		if p is None:
			p = (bg[0], bg[1], bg[2], 255)
		elif p[3] < 255:
			a = p[3] / 255.0
			p = tuple(int(round(p[k] * a + bg[k] * (1 - a))) for k in range(3)) + (255,)
		out.px[i] = p
	return out


def png_size(path):
	with open(path, "rb") as fh:
		d = fh.read(24)
	return struct.unpack(">II", d[16:24])


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--preview", metavar="DIR")
	args = ap.parse_args()
	os.makedirs(OUT, exist_ok=True)
	if args.preview:
		os.makedirs(args.preview, exist_ok=True)
	ok = True
	for name, (fn, cw, ch, n, rows) in FILES.items():
		res = fn()
		if isinstance(res, list):
			assert len(res) == n, (name, len(res), n)
			for fr in res:
				assert (fr.w, fr.h) == (cw, ch), (name, fr.w, fr.h)
			sh = sheet(res, n)
		else:
			sh = res
		path = os.path.join(OUT, name + ".png")
		save_png(sh, path)
		w, h = png_size(path)
		exp = (cw * n, ch * rows) if rows == 1 else (cw * n, ch * rows)
		good = (w, h) == exp
		ok = ok and good
		print("%-22s %4dx%-4d expected %4dx%-4d cell %2dx%-2d frames %2d%s %s" % (name, w, h, exp[0], exp[1], cw, ch, n, " x%d rows" % rows if rows > 1 else "", "OK" if good else "MISMATCH"))
		if args.preview:
			save_png(flatten(sh), os.path.join(args.preview, name + ".png"), 4)
	print("ALL DIMENSIONS OK" if ok else "DIMENSION MISMATCH")
	return 0 if ok else 1


if __name__ == "__main__":
	sys.exit(main())

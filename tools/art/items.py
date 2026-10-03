"""Generate the RUN-016 item, projectile, VFX and HUD art (Longbow, shards, chest, potion).

Usage: python3 tools/art/items.py [--preview DIR]

Outputs (assets/sprites/, horizontal strips, frames left -> right, all frames the same size):
  proj_arrow.png         16x5    1 frame, arrow pointing RIGHT (flip for left); tip at x=15, centre row y=2
  vfx_arrow_release.png  96x12   6 frames of 16x12, anchor left-centre (0, 6), emits rightwards
  vfx_arrow_impact.png   80x16   5 frames of 16x16, centre (8, 8): terrain splinters + stone dust
  vfx_arrow_hit.png      80x16   5 frames of 16x16, centre (8, 8): pale-yellow/white enemy spark burst
  item_shard.png         80x12   8 frames of 10x12: floating violet shard, slow turn + glint
  vfx_shard_burst.png    120x20  6 frames of 20x20, centre (10, 10): violet sparkle burst
  ui_shard_icon.png      12x12   1 frame, HUD shard icon (same size/weight as the coin in ui_icons.png)
  ui_slot_icons.png      36x12   3 frames of 12x12: Sword 0, Longbow 0, Empty
  item_chest.png         144x20  6 frames of 24x20, anchor bottom-centre (12, 19): closed, opening x4, open+glow
  vfx_chest_vanish.png   192x24  6 frames of 32x24, anchor bottom-centre (16, 23): open chest dissolving to dust
  item_potion_minor.png  60x14   6 frames of 10x14, anchor bottom-centre (5, 13): green healing flask, glint loop
  vfx_heal.png           168x32  7 frames of 24x32, anchor bottom-centre (12, 31): rising green motes and crosses

Everything is drawn by code from tools/art/palette.py (plus a local healing-green ramp, POTION),
seeded and deterministic, no third-party pixel and no generated image.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, line, outline, save_png, sheet  # noqa: E402
from palette import BLOOD, CORRUPT, EMBER, GOLD, OUTLINE, STEEL, STONE, WOOD  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
BG = (22, 24, 31, 255)
WHITE = (255, 255, 255, 255)
# Healing green: cooler/brighter than SLIME_GREEN (teal-leaning) so potions never read as slime goo.
POTION = [(18, 64, 46, 255), (31, 122, 80, 255), (47, 184, 114, 255), (110, 230, 160, 255), (200, 255, 224, 255)]


def a(color, alpha):
	return (color[0], color[1], color[2], alpha)


def from_rows(rows, pal):
	c = Canvas(max(len(r) for r in rows), len(rows))
	for y, r in enumerate(rows):
		assert len(r) == c.w, (y, r)
		for x, ch in enumerate(r):
			if ch in pal:
				c.put(x, y, pal[ch])
	return c


# ------------------------------------------------------------------ arrow
def arrow():
	pal = {"P": STEEL[4], "R": BLOOD[3], "r": BLOOD[2], "L": WOOD[4], "W": WOOD[3], "D": WOOD[1],
		"S": STEEL[3], "s": STEEL[1], "T": WHITE, "M": STEEL[2]}
	rows = [
		".PP........sS...",
		"PRP.LLLLLLLLSST.",
		"rRPWWWWWWWWWSSST",
		"PrP.DDDDDDDDSST.",
		".PP........sM...",
	]
	return from_rows(rows, pal)


# ------------------------------------------------------------- particles
def burst(frames, w, h, cx, cy, parts, ramp, gravity=0.0, trail=False):
	"""parts: (angle, speed, size) ; position = c + v*t*(decel) ; colour fades along ramp (light -> dark)."""
	out = []
	n = frames
	for i in range(n):
		c = Canvas(w, h)
		for ang, spd, size in parts:
			t = i + 0.5
			r = spd * (t - 0.08 * t * t)
			x = cx + math.cos(ang) * r
			y = cy + math.sin(ang) * r + gravity * t * t * 0.5
			col = ramp[min(len(ramp) - 1, int(i / n * len(ramp)))]
			if i >= n - 1 and size > 1:
				size = 1
			if size >= 2:
				c.rect(int(round(x - 0.5)), int(round(y - 0.5)), 2, 2, col)
			else:
				c.put(int(round(x)), int(round(y)), col)
		out.append(c)
	return out


def arrow_release():
	"""Bowstring snap: expanding pale crescents + two air wisps heading right."""
	frames = []
	rng = random.Random(16)
	cols = [WHITE, STEEL[4], STEEL[3], a(STEEL[3], 190), a(STEEL[2], 130), a(STEEL[2], 70)]
	for i in range(6):
		c = Canvas(16, 12)
		radius = 2.5 + i * 2.1
		if i < 5:
			for k in range(-30, 31):
				ang = k / 30 * 1.0
				if i >= 2 and k % 3 == 0:
					continue
				x = math.cos(ang) * radius
				y = math.sin(ang) * radius * 0.8
				c.put(int(round(x)), int(round(5.5 + y)), cols[i])
		# trailing inner puff
		if i < 4:
			r = (3, 3, 2, 1)[i]
			for yy in range(-r, r + 1):
				for xx in range(0, r + 1):
					if xx * xx + yy * yy <= r * r:
						c.put(1 + xx, 6 + yy, cols[i + 1] if xx + abs(yy) > 1 else cols[i])
		# two streaks
		for k, dy in enumerate((-3, 3)):
			x0 = 2 + i * 2 + k
			if i < 5:
				c.put(x0, 6 + dy, cols[min(5, i + 1)])
				c.put(x0 + 1, 6 + dy, cols[min(5, i + 2)])
		frames.append(c)
	return frames


def arrow_impact():
	rng = random.Random(17)
	parts = []
	# splinters flick up and back (wood) ; dust puffs spread out (stone)
	frames = []
	for i in range(5):
		c = Canvas(16, 16)
		t = i + 0.5
		dust = [STEEL[4], STEEL[3], STONE[5], STONE[4], STONE[3]][i]
		# dust puffs on the left half (arrow comes from the left) drifting out and up
		for k, (ang, spd, s) in enumerate([(math.pi * 1.15, 1.4, 2), (math.pi * 0.85, 1.3, 2), (math.pi * 1.5, 1.0, 1),
				(math.pi * 0.6, 1.0, 1), (math.pi * 1.3, 1.9, 1), (math.pi * 0.95, 2.0, 1)]):
			r = spd * t * 1.2
			x = 8 + math.cos(ang) * r * 1.2
			y = 8 + math.sin(ang) * r - t * 0.4
			if s == 2 and i < 4:
				c.rect(int(round(x - 1)), int(round(y - 1)), 2, 2, dust)
			else:
				c.put(int(round(x)), int(round(y)), dust)
		# splinters: 2 px wood slivers arcing out
		for k, (ang, spd) in enumerate([(-2.3, 2.6), (-0.9, 2.9), (-1.6, 3.2), (-2.8, 2.0), (-0.4, 2.2)]):
			if i == 4 and k % 2:
				continue
			x = 8 + math.cos(ang) * spd * t * 0.9
			y = 8 + math.sin(ang) * spd * t * 0.9 + 0.5 * t * t * 0.55
			col = WOOD[4] if i < 3 else WOOD[3]
			c.put(int(round(x)), int(round(y)), col)
			if i < 3:
				c.put(int(round(x - math.cos(ang))), int(round(y - math.sin(ang))), WOOD[3])
		if i == 0:
			c.rect(7, 7, 2, 2, WHITE)
			for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
				c.put(8 + dx, 8 + dy, STEEL[4])
		frames.append(c)
	return frames


def arrow_hit():
	frames = []
	rays = [k * math.tau / 8 + 0.2 for k in range(8)]
	pal = [WHITE, GOLD[4], GOLD[4], GOLD[3], GOLD[2]]
	for i in range(5):
		c = Canvas(16, 16)
		col = pal[i]
		if i < 3:
			r = (3, 2, 1)[i]
			for yy in range(-r, r + 1):
				for xx in range(-r, r + 1):
					if xx * xx + yy * yy <= r * r:
						c.put(8 + xx - (1 if xx < 0 else 0), 8 + yy - (1 if yy < 0 else 0), WHITE if i == 0 else GOLD[4])
		for k, ang in enumerate(rays):
			long = k % 2 == 0
			r0 = 2.0 + i * (1.8 if long else 1.3)
			length = (3 if long else 2) - (1 if i >= 3 else 0)
			if i == 4 and not long:
				continue
			for s in range(length):
				r = r0 + s
				x = 8 + math.cos(ang) * r - 0.5
				y = 8 + math.sin(ang) * r - 0.5
				c.put(int(round(x)), int(round(y)), col if s == 0 else pal[min(4, i + 1)])
		frames.append(c)
	return frames


# ----------------------------------------------------------------- shard
def crystal(w, h, phase, shade_levels=True):
	"""Prismatic hexagonal crystal body (no outline) on a w x h canvas; phase turns the facets."""
	c = Canvas(w, h)
	prof = [0.35, 0.65, 0.9, 1.0, 1.0, 1.0, 1.0, 0.9, 0.65, 0.35]
	prof = [prof[int(round(y * (len(prof) - 1) / (h - 1)))] for y in range(h)]
	width = max(3.2, abs(math.cos(phase)) * w)
	cx = (w - 1) / 2
	ridge = math.sin(phase) * width * 0.28
	for y in range(h):
		half = width * prof[y] / 2
		x0 = int(math.ceil(cx - half + 0.01))
		x1 = int(math.floor(cx + half - 0.01))
		if x1 < x0:
			x0 = x1 = int(round(cx))
		for x in range(x0, x1 + 1):
			d = (x - (cx + ridge))
			if d < -0.5:
				col = CORRUPT[3] if y < h * 0.55 else CORRUPT[2]
			elif d <= 0.5:
				col = CORRUPT[4] if y < h * 0.7 else CORRUPT[3]
			else:
				col = CORRUPT[2] if y < h * 0.5 else CORRUPT[1]
			if x == x1 and x1 - x0 >= 2:
				col = CORRUPT[1] if y > h * 0.35 else CORRUPT[2]
			c.put(x, y, col)
		if prof[y] < 0.5 and y > h / 2:
			c.put(int(round(cx)), y, CORRUPT[1])
	return c


def shard_frame(i):
	phase = i / 8 * math.tau + 0.5
	body = crystal(8, 10, phase)
	f = Canvas(10, 12)
	f.blit(outline(body, OUTLINE), 0, 1)
	# glint: bright core pixels that wake up on the turn
	gl = {1: [(3, 3)], 2: [(3, 3), (3, 4)], 3: [(3, 3), (3, 4), (2, 3), (4, 3), (3, 2)], 4: [(4, 4)], 5: [(5, 4)]}
	for k, (x, y) in enumerate(gl.get(i, [])):
		f.put(x, y, WHITE if k == 0 or i == 3 and k == 0 else CORRUPT[4])
	if i == 3:
		f.put(3, 3, WHITE)
	return f


def shard_burst():
	frames = []
	rng = random.Random(18)
	dots = [(rng.random() * math.tau, 2.2 + rng.random() * 1.6) for _ in range(9)]
	ramp = [WHITE, CORRUPT[4], CORRUPT[4], CORRUPT[3], CORRUPT[2], CORRUPT[1]]
	for i in range(6):
		c = Canvas(20, 20)
		col = ramp[i]
		if i < 5:
			radius = 3 + i * 1.8
			steps = 36
			for k in range(steps):
				if i >= 2 and k % 2:
					continue
				ang = k / steps * math.tau
				c.put(int(round(9.5 + math.cos(ang) * radius)), int(round(9.5 + math.sin(ang) * radius * 0.92)), col)
		if i < 3:
			r = (3, 2, 1)[i]
			for yy in range(-r, r + 1):
				for xx in range(-r, r + 1):
					if xx * xx + yy * yy <= r * r:
						c.put(10 + xx, 10 + yy, WHITE if i == 0 else CORRUPT[4])
		if i < 4:
			n = (6, 5, 3, 1)[i]
			c.put(10, 10, WHITE)
			for d in range(1, n + 1):
				cc = CORRUPT[4] if d == 1 else CORRUPT[3]
				for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
					c.put(10 + dx, 10 + dy, cc)
		for k, (ang, spd) in enumerate(dots):
			if i == 0:
				continue
			t = i
			x = 10 + math.cos(ang) * spd * t * 1.5
			y = 10 + math.sin(ang) * spd * t * 1.5 - t * 0.5
			cc = ramp[min(5, i + (k % 2))]
			c.put(int(round(x)), int(round(y)), cc)
		frames.append(c)
	return frames


def shard_icon():
	pal = {"a": CORRUPT[4], "b": CORRUPT[3], "c": CORRUPT[2], "d": CORRUPT[1], "w": WHITE}
	rows = [
		"....bb......",
		"...abbc.....",
		"..abbbcc....",
		"..awbbbcd...",
		"..abbbbcd...",
		".abbbbbccd..",
		".abbbbbcdd..",
		"..abbbccd...",
		"..bbbcccd...",
		"...bbccd....",
		"....cdd.....",
		"............",
	]
	body = from_rows(rows, pal)
	f = outline(body, OUTLINE)
	# shift so the glyph sits in the 12x12 frame like the coin: crop/shift one px
	g = Canvas(12, 12)
	g.blit(f, 0, 0)
	return g


# ------------------------------------------------------------- slot icons
def sword_icon():
	c = Canvas(12, 12)
	line(c, 4, 7, 9, 2, STEEL[3])  # blade
	line(c, 3, 8, 8, 3, STEEL[4])
	c.put(9, 2, STEEL[4])
	c.put(10, 1, STEEL[4])
	# blade lower edge shade
	for x, y in ((5, 7), (6, 6), (7, 5), (8, 4), (9, 3)):
		c.put(x, y, STEEL[2])
	# guard (perpendicular to the blade)
	for x, y, col in ((2, 6, GOLD[3]), (3, 7, GOLD[2]), (4, 8, GOLD[2]), (5, 9, GOLD[1]), (3, 6, GOLD[2]), (4, 7, GOLD[2])):
		c.put(x, y, col)
	# grip + pommel
	c.put(2, 9, WOOD[2])
	c.put(1, 10, GOLD[2])
	return outline(c, OUTLINE)


def bow_icon():
	c = Canvas(12, 12)
	p0, p1, p2 = (2.0, 10.0), (1.0, 1.0), (10.0, 2.0)
	prev = None
	for k in range(0, 25):
		t = k / 24
		x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
		y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
		shade = WOOD[4] if (x + y) < 9 else WOOD[3] if (x + y) < 12 else WOOD[2]
		c.put(int(round(x)), int(round(y)), shade)
		c.put(int(round(x + 0.0)), int(round(y + 1.0)) if t in (0.5,) else int(round(y)), shade)
	for x, y in ((2, 9), (3, 8), (9, 2), (8, 3)):
		pass
	line(c, 3, 10, 10, 3, STEEL[4])  # string, a straight pale chord
	return outline(c, OUTLINE)


def empty_icon():
	c = Canvas(12, 12)
	col = STONE[3]
	for (x, y) in ((2, 2), (3, 2), (4, 2), (7, 2), (8, 2), (9, 2), (2, 9), (3, 9), (4, 9), (7, 9), (8, 9), (9, 9),
			(2, 3), (2, 4), (2, 7), (2, 8), (9, 3), (9, 4), (9, 7), (9, 8)):
		c.put(x, y, col)
	return c


# ------------------------------------------------------------------ chest
def chest_frame(k):
	c = Canvas(24, 20)
	X0, X1 = 2, 21
	bt, bb = 10, 18  # body rows
	bands = (4, 5, 18, 19)

	def plank_rect(x0, x1, y0, y1, underside=False):
		for y in range(y0, y1 + 1):
			for x in range(x0, x1 + 1):
				col = WOOD[1] if underside else WOOD[2]
				if not underside:
					if (x - 2) % 5 == 4 and y > y0:
						col = WOOD[1]  # plank seam
					elif y == y0:
						col = WOOD[3]
					elif y == y1:
						col = WOOD[1]
					elif x == x0:
						col = WOOD[3]
					elif x == x1:
						col = WOOD[1]
				else:
					if y == y0:
						col = WOOD[2]
					elif (x - 2) % 5 == 4:
						col = WOOD[0]
				c.put(x, y, col)

	def bands_rect(y0, y1, under=False):
		for y in range(y0, y1 + 1):
			c.put(4, y, STEEL[1] if under else STEEL[3])
			c.put(5, y, STEEL[1] if under else STEEL[2])
			c.put(18, y, STEEL[1] if under else STEEL[2])
			c.put(19, y, STEEL[0] if under else STEEL[1])

	lid = [(4, 6), (3, 6), (1, 5), (1, 4), (3, 3), (3, 3)][k]
	glow = k >= 1
	# body
	plank_rect(X0, X1, bt, bb)
	bands_rect(bt, bb)
	for x in (4, 18):
		c.put(x, bt + 3, STEEL[4])
		c.put(x, bb - 1, STEEL[4])
	# iron rim strip along the mouth of the body
	for x in range(X0, X1 + 1):
		c.put(x, bt, STEEL[2] if x < 12 else STEEL[1])
	# lid
	top, h = lid
	if k <= 2:
		for y in range(top, top + h):
			for x in range(X0, X1 + 1):
				if (y == top and x in (X0, X1)):
					continue
				col = WOOD[2]
				if y == top:
					col = WOOD[4]
				elif y == top + 1:
					col = WOOD[3]
				elif y == top + h - 1:
					col = WOOD[1]
				elif (x - 2) % 5 == 4:
					col = WOOD[1]
				c.put(x, y, col)
		bands_rect(top + 1, top + h - 1)
		if k == 0:
			for x in range(10, 14):  # lock tab on the lid
				for y in (8, 9):
					c.put(x, y, GOLD[2] if y == 8 else GOLD[1])
	else:
		plank_rect(X0 + 1, X1 - 1, top, top + h - 1, underside=True)
		bands_rect(top, top + h - 1, under=True)
		for x in range(X0 + 1, X1):
			c.put(x, top, WOOD[3])  # lit top rim of the standing lid
	# lock plate on the body
	for y in range(bt + 1, bt + 5):
		for x in range(10, 14):
			col = GOLD[2]
			if y == bt + 1 or x == 10:
				col = GOLD[3]
			if y == bt + 4 or x == 13:
				col = GOLD[1]
			c.put(x, y, col)
	c.put(11, bt + 2, GOLD[0])
	c.put(11, bt + 3, GOLD[0])
	if k >= 2:  # hasp hangs open
		c.put(11, bt + 2, GOLD[3])
		c.put(11, bt + 3, GOLD[2])
	out = outline(c, OUTLINE)
	# warm glow inside the opened mouth
	if glow:
		lvl = [0, 1, 2, 3, 4, 5][k]
		rows = {1: [9], 2: [8, 9], 3: [7, 8, 9], 4: [6, 7, 8, 9], 5: [6, 7, 8, 9]}[k]
		cols = [EMBER[3], EMBER[3], EMBER[2], EMBER[2], EMBER[1]]
		if k >= 3:
			# the mouth: an open interior behind the front rim
			for y in (8, 9):
				for x in range(X0 + 1, X1):
					out.put(x, y, WOOD[0] if y == 8 else WOOD[1])
		for idx, y in enumerate(rows):
			inset = 1 + (0 if y == 9 else 1) if k >= 2 else 3
			for x in range(X0 + inset + 1, X1 - inset):
				if k >= 3 and y <= 9 and y >= 8:
					out.put(x, y, EMBER[3] if y == 9 else EMBER[2])
				elif y == 9 and k <= 2:
					out.put(x, y, EMBER[3] if k >= 1 else EMBER[2])
				elif k == 2 and y == 8:
					out.put(x, y, EMBER[2])
		out.put(11, 9, WHITE if k >= 2 else EMBER[3])
		out.put(12, 9, WHITE if k >= 2 else EMBER[3])
		# soft light rays above the mouth
		rng = random.Random(30 + k)
		if k >= 2:
			for x in (7, 11, 12, 16):
				hgt = [0, 0, 1, 3, 4, 5][k]
				for y in range(9 - hgt, 8):
					if y > top + h:
						out.put(x, y, a(EMBER[3], 120 if y > 5 else 70))
	return out


def chest_frames():
	return [chest_frame(i) for i in range(6)]


def chest_vanish():
	base = chest_frame(5)
	frames = []
	rng = random.Random(41)
	pix = [(x, y) for y in range(base.h) for x in range(base.w) if base.get(x, y) is not None]
	order = {}
	for (x, y) in pix:
		order[(x, y)] = rng.random() * 0.55 + (1 - y / base.h) * 0.45  # top dissolves first
	thresholds = [0.12, 0.30, 0.52, 0.74, 0.92, 1.01]
	motes = [(rng.uniform(5, 27), rng.uniform(12, 23), rng.uniform(0.7, 1.6)) for _ in range(14)]
	for i, th in enumerate(thresholds):
		c = Canvas(32, 24)
		for (x, y) in pix:
			if order[(x, y)] >= th:
				col = base.get(x, y)
				if i >= 3 and (x + y + i) % 2 == 0:
					col = a(col, 150) if i >= 4 else col
				c.put(x + 4, y + 4, col)
		for k, (mx, my, sp) in enumerate(motes):
			if i == 0 and k > 5:
				continue
			y = my - i * sp * 2.2
			x = mx + math.sin(i * 0.9 + k) * 1.5
			ramp = [STEEL[4], STEEL[3], STEEL[3], STEEL[2], a(STEEL[2], 160), a(STEEL[2], 90)]
			if k % 3 == 0:
				ramp = [GOLD[4], GOLD[3], GOLD[3], GOLD[2], a(GOLD[2], 150), a(GOLD[1], 90)]
			c.put(int(round(x)), int(round(y)), ramp[i])
		frames.append(c)
	return frames


# ----------------------------------------------------------------- potion
def potion_frame(i):
	c = Canvas(10, 14)
	cx, cy, r = 4.5, 8.5, 4.2
	level = 7.3 + (0.0 if i % 3 else 0.0)  # liquid surface row
	glass_edge = STEEL[3]
	for y in range(14):
		for x in range(10):
			d = math.hypot(x - cx, (y - cy) * 1.0)
			if y >= 3 and y <= 5 and 3 <= x <= 6:  # neck
				c.put(x, y, STEEL[3] if x == 3 else STEEL[2] if x == 4 else STEEL[1] if x == 5 else STEEL[1])
				continue
			if 5 <= y <= 12 and d <= r:
				if y >= level:
					col = POTION[2]
					lit = (x - cx) * -0.7 + (y - cy) * -0.6
					if lit > 1.8:
						col = POTION[3]
					elif lit < -2.2:
						col = POTION[1]
					if d > r - 1.0 and lit < -0.8:
						col = POTION[0] if lit < -2.6 else POTION[1]
					if y < level + 1 and d <= r - 0.6:
						col = POTION[3]  # lit meniscus
				else:
					col = STEEL[2] if (x - cx) * -0.7 + (y - cy) * -0.6 > 0 else STEEL[1]
					if d > r - 1.0:
						col = STEEL[3] if (x - cx) * -0.7 + (y - cy) * -0.6 > 0 else STEEL[2]
				c.put(x, y, col)
	# cork
	for x in range(3, 7):
		c.put(x, 1, WOOD[4] if x < 5 else WOOD[3])
		c.put(x, 2, WOOD[3] if x < 5 else WOOD[2])
	c.put(2, 3, None)
	out = outline(c, OUTLINE)
	# glass glint sweeping across the upper body over the loop
	path = [(2, 7), (3, 6), (4, 6), (5, 6), (6, 7), (2, 7)]
	gx, gy = path[i % 6]
	if i in (0, 5):
		gx, gy = 2, 8
		out.put(gx, gy, POTION[4])
		out.put(gx, gy - 1, WHITE)
	elif i in (2, 3):
		out.put(gx, gy, WHITE)
		out.put(gx + 1, gy, POTION[4])
	else:
		out.put(gx, gy, POTION[4])
	# rising bubble
	bub = {1: (5, 11), 2: (5, 10), 3: (4, 10), 4: (4, 11)}
	if i in bub:
		out.put(bub[i][0], bub[i][1], POTION[3] if i % 2 else POTION[4])
	out.put(3, 0 + 0, out.get(3, 0))
	return out


def heal():
	frames = []
	rng = random.Random(23)
	motes = []
	for _ in range(16):
		motes.append((rng.uniform(5, 19), rng.uniform(14, 31), rng.uniform(1.2, 2.6), rng.randint(0, 3), rng.random() < 0.3))
	motes[0] = (12, 27, 2.4, 0, True)
	motes[1] = (7, 22, 2.0, 1, True)
	motes[2] = (17, 24, 1.8, 2, True)
	ramps = [WHITE, POTION[4], POTION[3], POTION[3], POTION[2], a(POTION[2], 170), a(POTION[1], 110)]
	for i in range(7):
		c = Canvas(24, 32)
		# soft aura behind the body
		if i < 6:
			strength = (40, 64, 70, 58, 42, 26)[i]
			for y in range(7, 32):
				half = 6.5 * math.sqrt(max(0.0, 1 - ((y - 20) / 13.0) ** 2))
				for x in range(int(math.ceil(12 - half)), int(12 + half) + 1):
					c.put(x, y, a(POTION[2], int(strength * 1.3)))  # RUN-016 review: readable over the knight
		for k, (mx, my, sp, delay, cross) in enumerate(motes):
			t = i - delay * 0.5
			if t < 0 or t > 6:
				continue
			x = mx + math.sin(t * 0.8 + k) * 1.5
			y = my - t * sp * 1.1
			col = ramps[min(6, max(0, int(round(t + 0.2))))]
			xi, yi = int(round(x)), int(round(y))
			if cross and t < 5:
				c.put(xi, yi, POTION[4] if t < 3 else POTION[3])
				for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
					c.put(xi + dx, yi + dy, POTION[3] if t < 3 else POTION[2])
			else:
				c.put(xi, yi, col)
				if t < 2.5 and k % 2 == 0:
					c.put(xi, yi + 1, a(col, 140))
		frames.append(c)
	return frames


# ------------------------------------------------------------------ main
def build():
	rel = arrow_release()
	return {
		"proj_arrow.png": sheet([arrow()], 1),
		"vfx_arrow_release.png": sheet(rel, 6),
		"vfx_arrow_impact.png": sheet(arrow_impact(), 5),
		"vfx_arrow_hit.png": sheet(arrow_hit(), 5),
		"item_shard.png": sheet([shard_frame(i) for i in range(8)], 8),
		"vfx_shard_burst.png": sheet(shard_burst(), 6),
		"ui_shard_icon.png": shard_icon(),
		"ui_slot_icons.png": sheet([sword_icon(), bow_icon(), empty_icon()], 3),
		"item_chest.png": sheet(chest_frames(), 6),
		"vfx_chest_vanish.png": sheet(chest_vanish(), 6),
		"item_potion_minor.png": sheet([potion_frame(i) for i in range(6)], 6),
		"vfx_heal.png": sheet(heal(), 7),
	}


def mock_context(outputs):
	"""Dark stone wall mock-up with the chest, potion and arrow in place (preview only)."""
	w, h = 160, 64
	c = Canvas(w, h)
	rng = random.Random(5)
	for y in range(h):
		for x in range(w):
			row = y // 8
			off = 8 if row % 2 else 0
			seam = y % 8 == 7 or (x + off) % 16 == 15
			c.put(x, y, STONE[1] if seam else STONE[2] if (x * 7 + y * 3) % 11 else STONE[3])
	c.rect(0, 56, w, 8, STONE[3])
	chest = outputs["item_chest.png"]
	for i in range(6):
		fr = Canvas(24, 20)
		for yy in range(20):
			for xx in range(24):
				fr.put(xx, yy, chest.get(i * 24 + xx, yy))
		c.blit(fr, 4 + i * 26, 36)
	pot = outputs["item_potion_minor.png"]
	for i in range(3):
		fr = Canvas(10, 14)
		for yy in range(14):
			for xx in range(10):
				fr.put(xx, yy, pot.get(i * 10 + xx, yy))
		c.blit(fr, 20 + i * 14, 8)
	arr = outputs["proj_arrow.png"]
	c.blit(arr, 80, 14)
	c.blit(arr, 100, 24, flip=True)
	shard = outputs["item_shard.png"]
	for i in range(4):
		fr = Canvas(10, 12)
		for yy in range(12):
			for xx in range(10):
				fr.put(xx, yy, shard.get(i * 10 + xx, yy))
		c.blit(fr, 110 + i * 12, 6)
	return c


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	outputs = build()
	for name, canvas in outputs.items():
		save_png(canvas, os.path.join(OUT, name))
		print(name, canvas.w, canvas.h)
		if preview:
			bed = Canvas(canvas.w, canvas.h)
			bed.rect(0, 0, canvas.w, canvas.h, BG)
			bed.blit(canvas, 0, 0)  # alpha-composited so translucent pixels preview faithfully
			save_png(bed, os.path.join(preview, name[:-4] + "_x4.png"), 4)
	if preview:
		save_png(mock_context(outputs), os.path.join(preview, "mock_context_x4.png"), 4)


if __name__ == "__main__":
	main()

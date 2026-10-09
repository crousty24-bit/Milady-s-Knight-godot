"""RUN-018 world art: paid chests, major potion, kill-heal feedback, Throwing Knife projectile and FX.

Usage: python3 tools/art/run018/world_items.py [--preview DIR]

Outputs (assets/run018/world/, horizontal strips, frames left -> right, all frames the same size):
  item_chest_common.png      144x20  6 frames of 24x20, origin bottom-centre (12, 20) -> offset (-12, -20); frame 0 closed
  item_chest_rare.png        192x24  6 frames of 32x24, origin bottom-centre (16, 24) -> offset (-16, -24); frame 0 closed
  vfx_chest_vanish_rare.png  240x28  6 frames of 40x28, origin bottom-centre (20, 28) -> offset (-20, -28)
  item_potion_major.png      72x16   6 frames of 12x16, loop 6 fps, foot (6, 16) -> offset (-6, FOOT_Y-16) = (-6, -6)
  vfx_heal_kill_minor.png    144x32  6 frames of 24x32, 12 fps, once, anchor bottom-centre (12, 32) at the player's feet
  vfx_heal_kill_major.png    144x32  6 frames of 24x32, 12 fps, once, anchor bottom-centre (12, 32) at the player's feet
  proj_knife.png             10x5    1 frame, knife pointing RIGHT (flip for left); tip at x=9, centre row y=2
  vfx_knife_release.png      64x12   4 frames of 16x12, anchor left-centre (0, 6), emits rightwards
  vfx_knife_impact.png       80x16   5 frames of 16x16, centre (8, 8): steel sparks on terrain (sparks bounce back left)
  vfx_knife_hit.png          80x16   5 frames of 16x16, centre (8, 8): slash streak + sparks on an enemy

The common chest is derived from the validated RUN-016 tutorial chest frames (tools/art/items.py, imported, not
modified) by recolouring (dark iron, violet shard lock) and adding an emblem; everything else is drawn here.
All procedurally generated in-house from tools/art/palette.py: no third-party pixel, no generated image.
"""
import math
import os
import random
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import items  # noqa: E402
from pixel import Canvas, line, outline, save_png, sheet  # noqa: E402
from palette import CORRUPT, EMBER, GOLD, OUTLINE, STEEL, STONE, WOOD  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "run018", "world")
POTION = items.POTION
WHITE = items.WHITE
a = items.a
# Cold blue accent (rare trim): kept dark and desaturated, a single bright gem highlight.
COLD = [(26, 38, 62, 255), (44, 70, 112, 255), (74, 114, 168, 255), (128, 176, 222, 255), (206, 232, 255, 255)]


def sub(src, x, y, w, h):
	c = Canvas(w, h)
	for yy in range(h):
		for xx in range(w):
			c.put(xx, yy, src.get(x + xx, y + yy))
	return c


# ------------------------------------------------------------ common chest
def common_frame(k):
	"""Tutorial chest recoloured: dark iron bands, violet shard lock plate, shard emblem on the lid."""
	base = items.chest_frame(k)
	mapping = {GOLD[3]: CORRUPT[4], GOLD[2]: CORRUPT[3], GOLD[1]: CORRUPT[2], GOLD[0]: CORRUPT[0],
		STEEL[4]: STEEL[3], STEEL[3]: STEEL[2], STEEL[2]: STEEL[1], STEEL[1]: STEEL[0]}
	c = base.copy()
	c.px = [mapping.get(p, p) if p is not None else None for p in c.px]
	# iron corner straps on the front of the body (not in the tutorial chest)
	for (x, y) in ((3, 17), (3, 18), (20, 17), (20, 18)):
		if c.get(x, y) is not None:
			c.put(x, y, STEEL[2] if x < 12 else STEEL[1])
	for x in (3, 20):
		c.put(x, 11, STEEL[2] if x < 12 else STEEL[1])
	if k == 0:
		# violet shard emblem on the closed lid: small diamond with one bright facet
		for (x, y, col) in ((11, 5, CORRUPT[3]), (12, 5, CORRUPT[2]), (10, 6, CORRUPT[3]), (11, 6, CORRUPT[4]),
				(12, 6, CORRUPT[3]), (13, 6, CORRUPT[1]), (11, 7, CORRUPT[2]), (12, 7, CORRUPT[1])):
			c.put(x, y, col)
		for (x, y) in ((11, 4), (12, 4), (9, 6), (14, 6), (10, 7), (13, 7), (11, 8), (12, 8), (10, 5), (13, 5)):
			if c.get(x, y) in (None,) or c.get(x, y) in (items.OUTLINE if hasattr(items, "OUTLINE") else OUTLINE, OUTLINE):
				c.put(x, y, OUTLINE)
	return c


# -------------------------------------------------------------- rare chest
RW, RH = 32, 24
RX0, RX1 = 2, 29          # body columns (inclusive), 28 wide
RBT, RBB = 13, 22         # body rows (inclusive); row 23 is outline


def rare_frame(k):
	c = Canvas(RW, RH)
	wood = [WOOD[0], WOOD[1], WOOD[2], WOOD[3]]  # darker than the common chest: reads as aged/dark timber
	cx = (RX0 + RX1) / 2.0

	def timber(x, y, y0, y1, under=False):
		col = WOOD[1]
		if under:
			col = WOOD[0] if (x - RX0) % 6 == 5 else WOOD[1]
			if y == y0:
				col = WOOD[2]
			return col
		if (x - RX0) % 6 == 5 and y > y0:
			col = WOOD[0]
		elif y == y0:
			col = WOOD[3]
		elif y == y1:
			col = WOOD[0]
		elif x == RX0:
			col = WOOD[2]
		elif x == RX1:
			col = WOOD[0]
		else:
			col = WOOD[1]
		return col

	strap_x = (6, 7, 24, 25)

	def straps(y0, y1, under=False):
		for y in range(y0, y1 + 1):
			for x, col in zip(strap_x, (STEEL[3], STEEL[2], STEEL[2], STEEL[1])):
				if under:
					col = STEEL[1] if col != STEEL[1] else STEEL[0]
				c.put(x, y, col)

	# body
	for y in range(RBT, RBB + 1):
		for x in range(RX0, RX1 + 1):
			c.put(x, y, timber(x, y, RBT, RBB))
	straps(RBT, RBB)
	# cold-blue lower trim band + steel rim along the mouth
	for x in range(RX0, RX1 + 1):
		c.put(x, RBB, COLD[1] if x < 16 else COLD[0])
		c.put(x, RBB - 1, STEEL[2] if x < 16 else STEEL[1])
		c.put(x, RBT, STEEL[3] if x < 16 else STEEL[2])
	# steel corner caps (3 px wide, full height of the body corners)
	for y in range(RBT, RBB + 1):
		for x in (RX0, RX0 + 1, RX0 + 2):
			c.put(x, y, STEEL[3] if x == RX0 else STEEL[2])
		for x in (RX1 - 2, RX1 - 1, RX1):
			c.put(x, y, STEEL[2] if x == RX1 - 2 else STEEL[1])
	for (x, y) in ((RX0 + 1, RBT + 2), (RX0 + 1, RBB - 3), (RX1 - 1, RBT + 2), (RX1 - 1, RBB - 3)):
		c.put(x, y, STEEL[4] if x < 16 else STEEL[3])
	# lock plate: steel with a violet keyhole (shard-priced)
	for y in range(RBT + 1, RBT + 6):
		for x in range(14, 18):
			col = STEEL[3] if (y == RBT + 1 or x == 14) else STEEL[1] if (y == RBT + 5 or x == 17) else STEEL[2]
			c.put(x, y, col)
	c.put(15, RBT + 2, CORRUPT[3])
	c.put(15, RBT + 3, CORRUPT[1])
	c.put(16, RBT + 2, CORRUPT[1])
	c.put(16, RBT + 3, CORRUPT[0])

	# lid
	closed_top, lid_h = 5, 8   # rows 5..12 when closed
	tops = [(5, 8), (4, 8), (2, 6), (2, 5), (4, 4), (4, 4)]
	top, h = tops[k]
	if k <= 1:
		# domed lid: rows narrow towards the top
		inset = {0: 7, 1: 4, 2: 2, 3: 1, 4: 0, 5: 0}
		for i, y in enumerate(range(top, top + h)):
			ins = {0: 6, 1: 4, 2: 2, 3: 1}.get(i, 0)
			for x in range(RX0 + ins, RX1 + 1 - ins):
				if i == 0:
					col = WOOD[3]
				elif i == 1:
					col = WOOD[2]
				elif i == h - 1:
					col = WOOD[0]
				elif (x - RX0) % 6 == 5:
					col = WOOD[0]
				else:
					col = WOOD[1]
				c.put(x, y, col)
		# lid straps follow the dome
		for i, y in enumerate(range(top, top + h)):
			ins = {0: 6, 1: 4, 2: 2, 3: 1}.get(i, 0)
			for x, col in zip(strap_x, (STEEL[4], STEEL[3], STEEL[2], STEEL[1])):
				if RX0 + ins <= x <= RX1 - ins:
					c.put(x, y, col)
		# steel rim at the bottom of the lid, blue gem at the centre
		for x in range(RX0, RX1 + 1):
			c.put(x, top + h - 1, STEEL[3] if x < 16 else STEEL[2])
		if k == 0:
			for (x, y, col) in ((14, 7, COLD[4]), (15, 7, COLD[3]), (16, 7, COLD[3]), (17, 7, COLD[2]),
					(14, 8, COLD[3]), (15, 8, COLD[3]), (16, 8, COLD[2]), (17, 8, COLD[1]),
					(15, 9, COLD[2]), (16, 9, COLD[1])):
				c.put(x, y, col)
			for (x, y) in ((14, 6), (15, 6), (16, 6), (17, 6), (13, 7), (18, 7), (13, 8), (18, 8), (14, 9), (17, 9), (15, 10), (16, 10)):
				if c.get(x, y) is not None or True:
					c.put(x, y, OUTLINE)
			# re-lay the steel behind the gem outline so it reads as a mounted stone
			for (x, y) in ((14, 6), (15, 6), (16, 6), (17, 6)):
				c.put(x, y, STEEL[2])
			c.put(14, 9, STEEL[2]); c.put(17, 9, STEEL[1]); c.put(15, 10, STEEL[2]); c.put(16, 10, STEEL[1])
	else:
		# standing lid slab behind the body, showing its dark underside; rounded top corners
		for y in range(top, top + h):
			for x in range(RX0 + 1, RX1):
				if y == top and (x < RX0 + 4 or x > RX1 - 4):
					continue
				c.put(x, y, WOOD[1] if y == top else timber(x, y, top, top + h - 1, under=True))
		for y in range(top, top + h):
			for x, col in zip(strap_x, (STEEL[1], STEEL[1], STEEL[0], STEEL[0])):
				if c.get(x, y) is not None:
					c.put(x, y, col)
		for x in range(RX0 + 4, RX1 - 3):
			c.put(x, top, STEEL[3] if x < 16 else STEEL[2])  # lit top rim of the lid
	out = outline(c, OUTLINE)
	# the mouth and the reward glow
	if k >= 1:
		glow_rows = {1: [12], 2: [11, 12], 3: [9, 10, 11, 12], 4: [8, 9, 10, 11, 12], 5: [8, 9, 10, 11, 12]}[k]
		inset = 3
		if k >= 2:
			for y in range(top + h, RBT):
				for x in range(RX0 + 1, RX1):
					out.put(x, y, WOOD[0])
		for y in glow_rows:
			for x in range(RX0 + inset + 1, RX1 - inset):
				if k == 1:
					col = EMBER[3]
				else:
					col = EMBER[3] if y >= 11 else EMBER[2] if y >= 9 else EMBER[1]
				if y < RBT:
					out.put(x, y, col)
		# hot white core
		for x in (14, 15, 16, 17):
			if k >= 2:
				out.put(x, 12 if k < 3 else 11, WHITE)
		# light rays rising out of the mouth
		if k >= 3:
			for x in (8, 12, 16, 20, 24):
				hgt = {3: 3, 4: 5, 5: 6}[k]
				for y in range(RBT - hgt - 1, RBT - 1):
					if out.get(x, y) is None:
						out.put(x, y, a(EMBER[3], 120 if y > RBT - 4 else 70))
	return out


def rare_vanish():
	base = rare_frame(5)
	frames = []
	rng = random.Random(81)
	pix = [(x, y) for y in range(base.h) for x in range(base.w) if base.get(x, y) is not None]
	order = {p: rng.random() * 0.55 + (1 - p[1] / base.h) * 0.45 for p in pix}
	thresholds = [0.12, 0.30, 0.52, 0.74, 0.92, 1.01]
	motes = [(rng.uniform(6, 34), rng.uniform(14, 27), rng.uniform(0.7, 1.7)) for _ in range(18)]
	for i, th in enumerate(thresholds):
		c = Canvas(40, 28)
		for (x, y) in pix:
			if order[(x, y)] >= th:
				col = base.get(x, y)
				if i >= 4 and (x + y + i) % 2 == 0:
					col = a(col, 150)
				c.put(x + 4, y + 4, col)
		for kk, (mx, my, sp) in enumerate(motes):
			if i == 0 and kk > 6:
				continue
			y = my - i * sp * 2.4
			x = mx + math.sin(i * 0.9 + kk) * 1.5
			ramp = [STEEL[4], STEEL[3], STEEL[3], STEEL[2], a(STEEL[2], 160), a(STEEL[2], 90)]
			if kk % 3 == 0:
				ramp = [COLD[4], COLD[3], COLD[3], COLD[2], a(COLD[2], 150), a(COLD[1], 90)]
			c.put(int(round(x)), int(round(y)), ramp[i])
		frames.append(c)
	return frames


# ------------------------------------------------------------ major potion
def major_frame(i):
	W, H = 12, 16
	c = Canvas(W, H)
	cx, cy, r = 5.5, 10.2, 5.2
	level = 8.6
	for y in range(H):
		for x in range(W):
			d = math.hypot((x - cx) * 0.95, (y - cy))
			if 4 <= y <= 5 and 4 <= x <= 7:  # neck
				c.put(x, y, STEEL[3] if x == 4 else STEEL[2] if x == 5 else STEEL[1])
				continue
			if 6 <= y <= 15 and d <= r:
				lit = (x - cx) * -0.7 + (y - cy) * -0.6
				if y >= level:
					col = POTION[3]
					if lit > 2.4:
						col = POTION[4]
					elif lit < -1.0:
						col = POTION[2]
					if lit < -3.2:
						col = POTION[1]
					if d > r - 1.0 and lit < -1.2:
						col = POTION[1] if lit > -3.4 else POTION[0]
					if y < level + 1 and d <= r - 0.6:
						col = POTION[4]
				else:
					col = STEEL[2] if lit > 0 else STEEL[1]
					if d > r - 1.0:
						col = STEEL[3] if lit > 0 else STEEL[2]
				c.put(x, y, col)
	# cork (wider than the minor's) and bone-white ribbon tied at the neck
	for x in range(3, 9):
		c.put(x, 1, WOOD[4] if x < 6 else WOOD[3])
		c.put(x, 2, WOOD[3] if x < 6 else WOOD[2])
	for x in range(4, 8):
		c.put(x, 3, WOOD[2] if x < 6 else WOOD[1])
	for x in range(3, 9):
		c.put(x, 5, STEEL[4] if x < 6 else STEEL[3])  # ribbon wraps the neck base
	c.put(8, 6, STEEL[3]); c.put(9, 6, STEEL[2])      # ribbon tail on the right
	c.put(3, 6, STEEL[3]); c.put(2, 7, STEEL[2])      # ribbon tail on the left
	out = outline(c, OUTLINE)
	# glint loop + two bubbles; the bright ring around the liquid reads as stronger magic
	spots = [(3, 9), (4, 8), (5, 8), (7, 8), (8, 9), (3, 9)]
	gx, gy = spots[i % 6]
	out.put(gx, gy, WHITE if i in (0, 2, 3) else POTION[4])
	if i in (0, 3):
		out.put(gx, gy + 1, POTION[4])
	for idx, (bx, by) in {1: (6, 13), 2: (6, 12), 3: (5, 12), 4: (7, 13), 5: (7, 12)}.items():
		if idx == i:
			out.put(bx, by, POTION[4])
	# tiny sparkle above the cork on two frames (distinguishes it from the minor flask)
	if i == 2:
		out.put(9, 0, POTION[4]); out.put(10, 0, POTION[3]) if False else None
	if i == 3:
		out.put(2, 0, POTION[3])
	return out


# -------------------------------------------------------- kill-heal feedback
def plus(c, x, y, big, col, edge):
	c.put(x, y, col)
	for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
		c.put(x + dx, y + dy, edge if big else edge)
	if big:
		c.put(x + 2, y, edge); c.put(x - 2, y, edge); c.put(x, y + 2, edge); c.put(x, y - 2, edge)


def heal_kill(major):
	frames = []
	rng = random.Random(118 if major else 117)
	n = 6
	nm = 11 if major else 5
	motes = []
	for k in range(nm):
		motes.append((rng.uniform(4.5, 19.5), rng.uniform(22, 29) if k % 2 else rng.uniform(15, 26), rng.uniform(1.6, 3.0), k % 3))
	for i in range(n):
		c = Canvas(24, 32)
		# bright ring at the feet (major: two ripples), expanding and fading
		if major and i < 5:
			for ring in range(2):
				t = i - ring * 1.0
				if t < 0:
					continue
				rx = 4 + t * 1.9
				ry = 1 + t * 0.35
				col = [WHITE, POTION[4], POTION[3], POTION[2], a(POTION[2], 140)][int(min(4, t))]
				for s in range(200):
					ang = s / 200 * math.tau
					px = 12 + math.cos(ang) * rx
					py = 28.6 + math.sin(ang) * ry
					c.put(int(round(px)), int(round(py)), col)
		elif not major and i < 3:
			rx = 3 + i * 2.2
			for s in range(120):
				ang = s / 120 * math.tau
				c.put(int(round(12 + math.cos(ang) * rx)), int(round(29 + math.sin(ang) * 0.9)), [POTION[4], POTION[3], a(POTION[2], 150)][i])
		ramp = [WHITE, POTION[4], POTION[3], POTION[3], POTION[2], a(POTION[2], 150)]
		for k, (mx, my, sp, delay) in enumerate(motes):
			t = i - delay * (0.4 if major else 0.6)
			if t < 0 or t > 5:
				continue
			x = mx + math.sin(t * 0.9 + k) * 1.3
			y = my - t * sp
			col = ramp[min(5, max(0, int(round(t))))]
			xi, yi = int(round(x)), int(round(y))
			c.put(xi, yi, col)
			if major and t < 2.5 and k % 2 == 0:
				c.put(xi, yi + 1, a(col, 150))
		# one "+" rising from the chest area; major is bigger and brighter
		if i <= 4:
			py = (24 - i * 3.2) if major else (22 - i * 2.4)
			px = 12
			if major:
				col = [WHITE, WHITE, POTION[4], POTION[3], POTION[2]][i]
				edge = [POTION[4], POTION[4], POTION[3], POTION[2], a(POTION[2], 150)][i]
				plus(c, px, int(round(py)), i < 3, col, edge)
			else:
				col = [POTION[4], POTION[4], POTION[3], POTION[3], a(POTION[2], 150)][i]
				edge = [POTION[3], POTION[3], POTION[2], a(POTION[2], 170), a(POTION[1], 120)][i]
				plus(c, px, int(round(py)), False, col, edge)
		frames.append(c)
	return frames


# ------------------------------------------------------------ knife family
def knife():
	"""10x5 throwing knife: wood grip, steel cross-guard, kite blade with a bright top edge; tip at (9, 2)."""
	pal = {"H": WOOD[3], "G": WOOD[2], "g": WOOD[1], "C": STEEL[3], "c": STEEL[1], "P": STEEL[4], "M": STEEL[3], "s": STEEL[2], "T": WHITE}
	rows = [
		"...C......",
		"H..CPPPP..",
		"GGGCMMMMMT",
		"g..CssssS.",
		"...c......",
	]
	rows[3] = "H..CssssM."
	return items.from_rows(rows, pal)


def knife_release():
	frames = []
	cols = [WHITE, STEEL[4], STEEL[3], a(STEEL[2], 150)]
	for i in range(4):
		c = Canvas(16, 12)
		col = cols[i]
		# 4-point glint at the hand, growing then splitting
		L = (1, 2, 2, 1)[i]
		cx = 2 + i
		for d in range(-L, L + 1):
			if i < 3 or d != 0:
				c.put(cx + d, 6, col)
				c.put(cx, 6 + d, col if i < 3 else cols[3])
		if i == 0:
			c.put(cx, 6, WHITE)
		# two thin steel streaks shooting right (not crescents)
		for dy, off in ((-2, 0), (2, 1)):
			x0 = 4 + i * 3 + off
			for s in range(3 if i < 3 else 2):
				c.put(x0 + s, 6 + dy, STEEL[4] if s == 2 and i < 2 else cols[min(3, i + (1 if s < 2 else 0))])
		frames.append(c)
	return frames


def spark(c, cx, cy, ang, r0, ln, col, tail):
	for s in range(ln):
		r = r0 + s
		x = cx + math.cos(ang) * r
		y = cy + math.sin(ang) * r
		c.put(int(round(x)), int(round(y)), col if s == ln - 1 else tail)


def knife_impact():
	frames = []
	# sparks bounce back-left (the knife arrives from the left) with a short vertical fan
	angs = [math.pi + 0.0, math.pi + 0.55, math.pi - 0.55, math.pi + 1.1, math.pi - 1.1, -1.5, 1.5]
	for i in range(5):
		c = Canvas(16, 16)
		col = [WHITE, GOLD[4], GOLD[3], STEEL[3], STEEL[2]][i]
		tail = [STEEL[4], STEEL[4], STEEL[3], STEEL[2], a(STEEL[2], 120)][i]
		if i < 2:
			# impact flash: small bright diamond at the wall
			for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
				c.put(8 + dx, 8 + dy, WHITE)
			if i == 0:
				for dx, dy in ((-1, 0), (2, 0), (0, -1), (0, 2), (1, -1), (1, 2)):
					c.put(8 + dx, 8 + dy, STEEL[4])
		for k, ang in enumerate(angs):
			if i == 4 and k % 2:
				continue
			ln = 3 if k < 3 else 2
			r0 = 1.5 + i * (2.0 if k < 3 else 1.5)
			spark(c, 8, 8, ang + (0.12 * (k % 2) - 0.06), r0, ln - (1 if i >= 3 else 0), col, tail)
		# a chip of stone/steel dust falling
		if 1 <= i <= 4:
			c.put(7 - i // 2, 9 + i, [None, STONE[5], STONE[4], STONE[3], a(STONE[3], 150)][i])
		frames.append(c)
	return frames


def knife_hit():
	frames = []
	for i in range(5):
		c = Canvas(16, 16)
		# diagonal slash (top-right to bottom-left) that thins out; sparks flick off it
		L = (3, 6, 6, 5, 3)[i]
		cx = 8
		for s in range(-L, L + 1):
			x = cx + s * 0.8
			y = 8 - s * 0.8
			thick = i < 3 and abs(s) < L - 1
			col = WHITE if i < 2 else STEEL[4] if i == 2 else STEEL[3] if i == 3 else a(STEEL[2], 130)
			c.put(int(round(x)), int(round(y)), col)
			if thick and i < 2:
				c.put(int(round(x)) + 1, int(round(y)), STEEL[3])
		sc = [WHITE, STEEL[4], STEEL[3], STEEL[2], a(STEEL[2], 120)][i]
		for k, (ang, spd) in enumerate([(-0.3, 2.2), (-1.0, 2.0), (2.6, 2.0), (3.5, 1.8), (0.5, 1.6)]):
			if i == 0 or (i == 4 and k % 2):
				continue
			r = spd * i * 1.1 + 2
			c.put(int(round(8 + math.cos(ang) * r)), int(round(8 + math.sin(ang) * r)), sc)
		frames.append(c)
	return frames


# ------------------------------------------------------------------ build
def build():
	common = [common_frame(i) for i in range(6)]
	rare = [rare_frame(i) for i in range(6)]
	return {
		"item_chest_common.png": sheet(common, 6),
		"item_chest_rare.png": sheet(rare, 6),
		"vfx_chest_vanish_rare.png": sheet(rare_vanish(), 6),
		"item_potion_major.png": sheet([major_frame(i) for i in range(6)], 6),
		"vfx_heal_kill_minor.png": sheet(heal_kill(False), 6),
		"vfx_heal_kill_major.png": sheet(heal_kill(True), 6),
		"proj_knife.png": sheet([knife()], 1),
		"vfx_knife_release.png": sheet(knife_release(), 4),
		"vfx_knife_impact.png": sheet(knife_impact(), 5),
		"vfx_knife_hit.png": sheet(knife_hit(), 5),
	}


EXPECTED = {  # name: (frame w, frame h, frames)
	"item_chest_common.png": (24, 20, 6), "item_chest_rare.png": (32, 24, 6), "vfx_chest_vanish_rare.png": (40, 28, 6),
	"item_potion_major.png": (12, 16, 6), "vfx_heal_kill_minor.png": (24, 32, 6), "vfx_heal_kill_major.png": (24, 32, 6),
	"proj_knife.png": (10, 5, 1), "vfx_knife_release.png": (16, 12, 4), "vfx_knife_impact.png": (16, 16, 5),
	"vfx_knife_hit.png": (16, 16, 5),
}


def read_png(path):
	d = open(path, "rb").read()
	pos, idat, w, h = 8, b"", 0, 0
	while pos < len(d):
		n, kind = struct.unpack(">I4s", d[pos:pos + 8])
		body = d[pos + 8:pos + 8 + n]
		if kind == b"IHDR":
			w, h = struct.unpack(">II", body[:8])
			assert body[8] == 8 and body[9] == 6
		elif kind == b"IDAT":
			idat += body
		pos += 12 + n
	raw = zlib.decompress(idat)
	stride = w * 4
	c = Canvas(w, h)
	prev = bytearray(stride)
	p = 0
	for y in range(h):
		f = raw[p]
		line_ = bytearray(raw[p + 1:p + 1 + stride])
		p += 1 + stride
		for i in range(stride):
			l = line_[i - 4] if i >= 4 else 0
			u = prev[i]
			ul = prev[i - 4] if i >= 4 else 0
			if f == 1:
				line_[i] = (line_[i] + l) & 255
			elif f == 2:
				line_[i] = (line_[i] + u) & 255
			elif f == 3:
				line_[i] = (line_[i] + (l + u) // 2) & 255
			elif f == 4:
				pa, pb, pc = abs(u - ul), abs(l - ul), abs(l + u - 2 * ul)
				pr = l if pa <= pb and pa <= pc else (u if pb <= pc else ul)
				pr = l if (abs(u - ul) <= abs(l - ul) and abs(u - ul) <= abs(l + u - 2 * ul)) else (u if abs(l - ul) <= abs(l + u - 2 * ul) else ul)
				line_[i] = (line_[i] + pr) & 255
		prev = line_
		for x in range(w):
			px = tuple(line_[x * 4:x * 4 + 4])
			if px[3] > 0:
				c.put(x, y, px)
	return c


def mock_context(outputs):
	"""Dark stone mock-up: knight reference, tutorial/common/rare chests, minor/major potion, knife vs arrow."""
	w, h = 230, 112
	c = Canvas(w, h)
	for y in range(h):
		for x in range(w):
			row = y // 8
			off = 8 if row % 2 else 0
			seam = y % 8 == 7 or (x + off) % 16 == 15
			c.put(x, y, STONE[0] if seam else STONE[1] if (x * 7 + y * 3) % 11 else STONE[2])
	ground = 96
	c.rect(0, ground, w, h - ground, STONE[3])
	for x in range(0, w, 16):
		c.rect(x, ground, 1, h - ground, STONE[1])
	c.rect(0, ground, w, 1, STONE[4])
	try:
		kn = read_png(os.path.join(ROOT, "assets", "sprites", "ashen_knight.png"))
		c.blit(sub(kn, 0, 0, 64, 64), 2, ground - 56)  # 64x64 idle cell, feet near the ground
	except Exception as e:  # preview only
		print("knight reference skipped:", e)
	x = 60
	tut = items.chest_frames()
	for fr_set, fw, fh in ((("tut", [tut[0], tut[5]]), 24, 20), (("com", None), 24, 20), (("rare", None), 32, 24)):
		pass
	def frame_of(name, i, fw, fh):
		return sub(outputs[name], i * fw, 0, fw, fh)
	c.blit(tut[0], x, ground - 20); x += 26
	c.blit(tut[5], x, ground - 20); x += 28
	c.blit(frame_of("item_chest_common.png", 0, 24, 20), x, ground - 20); x += 26
	c.blit(frame_of("item_chest_common.png", 5, 24, 20), x, ground - 20); x += 28
	c.blit(frame_of("item_chest_rare.png", 0, 32, 24), x, ground - 24); x += 34
	c.blit(frame_of("item_chest_rare.png", 5, 32, 24), x, ground - 24)
	# potions on the ground line: minor (10x14) next to major (12x16)
	px = 150
	c.blit(items.potion_frame(2), px, ground - 14)
	c.blit(frame_of("item_potion_major.png", 2, 12, 16), px + 16, ground - 16)
	# projectiles in flight
	arrow = items.arrow()
	k = outputs["proj_knife.png"]
	c.blit(arrow, 150, 30)
	c.blit(k, 150, 44)
	c.blit(arrow, 190, 30, flip=True)
	c.blit(k, 190, 44, flip=True)
	# FX frames at the player's feet / impact points
	fx = outputs["vfx_heal_kill_minor.png"]
	c.blit(frame_of("vfx_heal_kill_minor.png", 2, 24, 32), 2 + 20, ground - 32 + 0)
	c.blit(frame_of("vfx_heal_kill_major.png", 2, 24, 32), 2 + 20 + 24, ground - 32 + 0)
	return c


def contact_sheet(outputs):
	"""All frames of every strip, spaced, over the level-like dark background (preview only)."""
	rows = list(outputs.items())
	pad = 4
	wmax = max(cv.w for _, cv in rows) + 2 * pad
	hsum = sum(cv.h + pad for _, cv in rows) + pad
	sheetc = Canvas(wmax, hsum)
	sheetc.rect(0, 0, wmax, hsum, items.BG)
	y = pad
	for _, cv in rows:
		sheetc.blit(cv, pad, y)
		y += cv.h + pad
	return sheetc


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	outputs = build()
	for name, canvas in outputs.items():
		fw, fh, n = EXPECTED[name]
		assert (canvas.w, canvas.h) == (fw * n, fh), (name, canvas.w, canvas.h)
		save_png(canvas, os.path.join(OUT, name))
		print(name, canvas.w, canvas.h, "%dx%d x%d" % (fw, fh, n))
		if preview:
			bed = Canvas(canvas.w, canvas.h)
			bed.rect(0, 0, canvas.w, canvas.h, items.BG)
			bed.blit(canvas, 0, 0)
			save_png(bed, os.path.join(preview, name[:-4] + "_x4.png"), 4)
	if preview:
		mc = mock_context(outputs)
		save_png(mc, os.path.join(preview, "mock_context_x1.png"), 1)
		save_png(mc, os.path.join(preview, "mock_context_x3.png"), 3)
		save_png(contact_sheet(outputs), os.path.join(preview, "contact_sheet_x3.png"), 3)


if __name__ == "__main__":
	main()

"""Gold coin (RUN-029): 12 frames of 16x16, embossed face, ridged edge, glint.

Frames: F12, F9, F5, Edge, B5, B9, B12, B9, B5, Edge, F5, F9 (spin front -> back -> front).
The coin is centred on (8, 8); the full face is 12x12 plus a 1 px outline.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, outline  # noqa: E402
from palette import GOLD, OUTLINE  # noqa: E402

WHITE = (255, 255, 255, 255)
WIDTHS = [12, 9, 5, 0, 5, 9, 12, 9, 5, 0, 5, 9]
FACES = ["f", "f", "f", "e", "b", "b", "b", "b", "b", "e", "f", "f"]

# Emblems on a 6x6 grid centred on the face (u,v in -3..2): front crown/cross, back diamond.
FRONT_MARK = ["..XX..", ".XXXX.", "XX..XX", "X.XX.X", ".XXXX.", "..XX.."]
BACK_MARK = ["..XX..", "..XX..", "XXXXXX", "XXXXXX", "..XX..", "..XX.."]


def face_pixel(u, v, side):
	"""u, v in [-1, 1] across the face. Returns a palette colour or None."""
	r2 = u * u + v * v
	if r2 > 1.0:
		return None
	light = -0.6 * u - 0.7 * v  # light from upper left
	if r2 > 0.62:  # raised rim
		return GOLD[3] if light > 0.25 else GOLD[2] if light > -0.35 else GOLD[1]
	if r2 > 0.5:  # engraved groove
		return GOLD[0] if light < 0.1 else GOLD[1]
	base = GOLD[2] if light > -0.25 else GOLD[1] if light > -0.8 else GOLD[1]
	# emblem
	mx, my = int(math.floor((u + 0.5) / 1.0 * 6 * 0.5 + 3)), int(math.floor((v + 0.5) / 1.0 * 6 * 0.5 + 3))
	return base


def render_face(width, side):
	c = Canvas(16, 16)
	if width <= 0:
		return None
	# sample the face on a fixed 12x12 grid but squeeze columns to the target width
	x0 = 8 - width // 2 - (1 if width < 12 else 0)
	for xi in range(width):
		u = ((xi + 0.5) / width) * 2 - 1
		for yi in range(12):
			v = ((yi + 0.5) / 12) * 2 - 1
			col = face_pixel(u, v, side)
			c.put(x0 + xi, 2 + yi, col)
	mark = FRONT_MARK if side == "f" else BACK_MARK
	for yi, row in enumerate(mark):
		for xi, ch in enumerate(row):
			if ch != "X":
				continue
			fx = (xi + 0.5) / 6 * 0.62 * 2 - 0.62  # emblem spans the inner field
			px = int(math.floor((fx + 1) / 2 * width))
			py = 5 + yi
			if 0 <= px < width and width >= 5:
				lit = GOLD[0] if side == "f" else GOLD[3]
				if side == "f":
					lit = GOLD[1]
				c.put(x0 + px, py, lit)
	return c


def edge_coin():
	c = Canvas(16, 16)
	cols = [GOLD[3], GOLD[2], GOLD[1], GOLD[0]]
	for i, col in enumerate(cols):
		x = 6 + i
		for y in range(3, 13):
			ridge = (y % 2 == 0)
			c.put(x, y, col if not ridge else (GOLD[1] if col is GOLD[3] else GOLD[0]) if i != 1 else (GOLD[1]))
	# rounded caps: centred, so the outline does not leave notched corners
	for x in (7, 8):
		c.put(x, 2, GOLD[2] if x == 7 else GOLD[1])
		c.put(x, 13, GOLD[1] if x == 7 else GOLD[0])
	return c


def frame(i):
	width = WIDTHS[i]
	side = FACES[i]
	if side == "e":
		base = edge_coin()
	else:
		base = render_face(width, side)
		# thickness: a dark gold rim sliver on the trailing side when turning; it follows the
		# face's right edge row by row so it never pokes out of the round silhouette
		if width < 12:
			t = 1 if width >= 8 else 2
			for y in range(16):
				xs = [x for x in range(16) if base.get(x, y) is not None]
				if not xs:
					continue
				right = xs[-1]
				for k in range(t):
					base.put(right + 1 + k, y, GOLD[1] if k == 0 else GOLD[0])
	out = outline(base, OUTLINE)
	# glint: a small four-point star on the upper-left of the broadest faces
	if i in (0, 6, 1, 7):
		gx, gy = (5, 5) if i in (0, 6) else (6, 5)
		star = [(0, 0, WHITE), (-1, 0, GOLD[4]), (1, 0, GOLD[4]), (0, -1, GOLD[4]), (0, 1, GOLD[4])]
		if i in (1, 7):
			star = [(0, 0, WHITE), (0, -1, GOLD[4])]
		for dx, dy, col in star:
			out.put(gx + dx, gy + dy, col)
	return out


def frames():
	return [frame(i) for i in range(len(WIDTHS))]

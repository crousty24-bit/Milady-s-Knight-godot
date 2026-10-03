"""Generate the menu art (RUN-015): title logo, foreground rampart, focus plate, cursor and lock icons.

Usage: python3 tools/art/menu_art.py [--preview DIR]

Outputs (assets/sprites/):
  ui_logo.png         title logo: gold blackletter "Milady's / Knight", crowned sword, tattered red banner
  ui_menu_ledge.png   dark broken rampart for the title screen foreground (the knight stands on it)
  ui_menu_focus.png   12x12 9-slice (margin 4): focused menu row, warm gold trim on a deep red plate
  ui_menu_cursor.png  7x9 gold pointer drawn left of the focused row (mirrored on the right in Godot)
  ui_menu_lock.png    7x8 dim padlock marking an unavailable option

The logo follows the composition of the brand reference "artwork & logo/MK logo 1.png" (gold
blackletter on a torn red banner, crowned sword through the title) but is redrawn natively at
1x by a broad-nib pen simulation: the reference is a high-resolution AI-style image with the
misspelling "Milaay's", so no pixel of it is used. Palette and outline come from tools/art/palette.py.
Deterministic, no third-party asset.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, hexc, outline, save_png  # noqa: E402
from palette import BLOOD, GOLD, MOSS, OUTLINE, STEEL, STONE, STONE_COOL  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
BG = (18, 23, 32, 255)

# ------------------------------------------------------------ broad-nib pen
NIB = (0.7071, -0.7071)  # 45 degree nib: down-right strokes are thick, up-right strokes are hairlines


class Pen:
	"""Collects pixels into a mask by sweeping a flat nib along polylines."""

	def __init__(self, width, height):
		self.w = width
		self.h = height
		self.mask = set()

	def stroke(self, points, nib=8.0, ox=0.0, oy=0.0):
		pts = [(x + ox, y + oy) for x, y in points]
		if len(pts) == 1:
			pts = pts * 2
		for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
			length = max(abs(x1 - x0), abs(y1 - y0), 0.01)
			steps = int(length * 4) + 1
			for i in range(steps + 1):
				t = i / steps
				px = x0 + (x1 - x0) * t
				py = y0 + (y1 - y0) * t
				s = -nib / 2.0
				while s <= nib / 2.0:
					self.mask.add((int(math.floor(px + s * NIB[0])), int(math.floor(py + s * NIB[1]))))
					s += 0.3

	def hair(self, points, ox=0.0, oy=0.0):
		"""1 px hairline (flourishes, crossbars)."""
		pts = [(x + ox, y + oy) for x, y in points]
		for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
			steps = int(max(abs(x1 - x0), abs(y1 - y0))) * 2 + 1
			for i in range(steps + 1):
				t = i / steps
				self.mask.add((int(math.floor(x0 + (x1 - x0) * t + 0.5)), int(math.floor(y0 + (y1 - y0) * t + 0.5))))


# Glyph metrics in pixels; origin = left of the letter on the baseline (y grows down).
XH = 19  # x-height
ASC = 29  # ascender / cap height
T = -XH


def stem(x, top, bottom, head=True, foot=True):
	"""Textura stem: lozenge head, straight body, lozenge foot."""
	path = []
	path += [(x - 2, top), (x, top + 2)] if head else [(x, top)]
	path += [(x, bottom - 2)]
	path += [(x + 2, bottom)] if foot else [(x, bottom)]
	return path


def glyph(ch):
	"""Return (strokes, hairs, advance)."""
	if ch == "M":
		s = [
			[(1, -ASC + 7), (4, -ASC + 4), (6, -ASC + 6), (6, -2), (3, 1)],
			[(6, -ASC + 10), (11, -ASC + 4), (14, -ASC + 7), (14, -2), (16, 0)],
			[(14, -ASC + 10), (19, -ASC + 4), (22, -ASC + 7), (22, -1), (24, 2), (27, 1)],
		]
		h = [[(0, -ASC + 14), (-3, -ASC + 18), (-3, -ASC + 23), (0, -ASC + 26)], [(10, -ASC + 14), (10, -6)]]
		return s, h, 30
	if ch == "K":
		s = [
			[(1, -ASC + 5), (4, -ASC + 2), (6, -ASC + 4), (6, -2), (3, 1)],
			[(18, -ASC + 3), (15, -ASC + 6), (8, -14)],
			[(8, -14), (12, -11), (16, -2), (19, 0), (22, -2)],
		]
		h = [[(0, -ASC + 12), (-3, -ASC + 16), (-3, -ASC + 21), (0, -ASC + 24)], [(18, -ASC + 3), (21, -ASC + 1), (23, -ASC + 3)]]
		return s, h, 24
	if ch == "i":
		return [stem(3, T, 0)], [], 9
	if ch == "l":
		return [stem(3, -ASC, 0)], [], 9
	if ch == "a":
		s = [
			[(1, T + 3), (4, T), (9, T + 2), (9, -2), (11, 0)],
			[(9, T + 8), (3, T + 10), (3, -2), (5, 0), (9, -3)],
		]
		return s, [], 14
	if ch == "d":
		s = [
			[(10, -ASC + 2), (8, -ASC), (8, -ASC + 1), (9, -ASC + 3), (9, -2), (11, 0)],
			[(9, T + 2), (5, T), (3, T + 2), (3, -2), (5, 0), (9, -3)],
		]
		return s, [], 14
	if ch == "y":
		s = [
			stem(3, T, -2, foot=False) + [(6, 0), (9, -3)],
			stem(9, T, 5, foot=False) + [(6, 8), (2, 7)],
		]
		return s, [], 14
	if ch == "'":
		return [[(2, -ASC), (3, -ASC + 2), (2, -ASC + 6)]], [], 6
	if ch == "s":
		s = [[(9, T + 2), (6, T), (3, T + 2), (3, T + 6), (9, -6), (9, -2), (6, 0), (2, -2)]]
		return s, [], 13
	if ch == "n":
		s = [stem(3, T, 0), [(3, T + 3), (7, T), (9, T + 2), (9, -2), (11, 0)]]
		return s, [], 15
	if ch == "g":
		s = [
			[(9, T + 2), (5, T), (3, T + 2), (3, -3), (5, -1), (9, -3)],
			[(9, T), (9, 5), (6, 8), (1, 6)],
		]
		return s, [], 14
	if ch == "h":
		s = [stem(3, -ASC, 0, foot=False), [(3, T + 3), (7, T), (9, T + 2), (9, 3), (6, 7)]]
		return s, [], 15
	if ch == "t":
		s = [[(4, -ASC + 6), (4, -2), (6, 0), (9, -3)]]
		h = [[(0, T), (9, T)], [(0, T + 1), (9, T + 1)]]
		return s, h, 12
	return [], [], 8


def write(pen, text, ox, oy, track=0):
	x = ox
	for ch in text:
		s, h, adv = glyph(ch)
		for path in s:
			pen.stroke(path, ox=x, oy=oy)
		for path in h:
			pen.hair(path, ox=x, oy=oy)
		x += adv + track
	return x


def text_width(text, track=0):
	return sum(glyph(ch)[2] + track for ch in text) - track


# --------------------------------------------------------------------- logo
def banner(c, x0, x1, top, depth, seed):
	"""Tattered red cloth swag hanging from (x0, top) to (x1, top), corners lifted, torn hem."""
	r = random.Random(seed)
	w = x1 - x0
	hem = []
	for i in range(w + 1):
		u = i / w
		base = depth * (0.25 + 0.75 * math.sin(math.pi * u) ** 0.8)
		hem.append(base)
	# torn tails: a few longer strips and notches
	tails = [0] * (w + 1)
	x = 0
	while x <= w:
		run = r.randint(2, 6)
		extra = r.choice([0, 0, 2, 4, 7, 11, 15]) if 6 < x < w - 6 else r.choice([10, 16, 22])
		for k in range(run):
			if x + k <= w:
				taper = 1.0 - abs(k - run / 2.0) / (run / 2.0 + 0.5)
				tails[x + k] = extra * taper
		x += run
	for i in range(w + 1):
		u = i / w
		lift = 16 * (1 - math.sin(math.pi * u)) ** 3  # corners rise
		y_top = top - lift + 2 * math.sin(u * math.pi * 6)
		y_bot = top + hem[i] + tails[i]
		for y in range(int(y_top), int(y_bot) + 1):
			fold = math.sin(i * 0.21 + math.sin(i * 0.047) * 2.4 + (y - top) * 0.035 * math.sin(i * 0.09))
			shade = 2 if fold > 0.35 else 1 if fold > -0.4 else 0
			if y > top + hem[i] - 3:
				shade = max(0, shade - 1)  # hem darker
			if y < y_top + 2:
				shade = min(3, shade + 1)  # lit top edge
			col = BLOOD[shade]
			if fold > 0.85 and (i + y) % 3 == 0:
				col = BLOOD[3]
			c.put(x0 + i, y, col)


def sword(c, cx, top, bottom):
	"""Vertical sword behind the title: steel blade with a fuller, gold guard and red gems."""
	for y in range(top + 20, bottom):
		taper = 3 if y < bottom - 10 else max(0, (bottom - y) // 3)
		for dx in range(-taper, taper + 1):
			col = STEEL[3] if dx < 0 else STEEL[1] if dx > 0 else STEEL[4]
			if dx == 0 and y < bottom - 14:
				col = STEEL[2]  # fuller
			c.put(cx + dx, y, col)
	# grip and pommel
	for y in range(top + 8, top + 17):
		c.put(cx - 1, y, BLOOD[1])
		c.put(cx, y, BLOOD[0] if y % 2 else BLOOD[2])
		c.put(cx + 1, y, BLOOD[0])
	# cross-guard
	for x in range(cx - 13, cx + 14):
		end = abs(x - cx) > 10
		c.put(x, top + 17, GOLD[3] if not end else GOLD[2])
		c.put(x, top + 18, GOLD[2] if not end else GOLD[1])
		c.put(x, top + 19, GOLD[1])
	for gx in (cx - 13, cx + 12):
		c.rect(gx, top + 16, 2, 5, GOLD[2])
		c.put(gx, top + 16, GOLD[4])
	for gx in (cx - 8, cx + 7):
		c.rect(gx, top + 17, 2, 2, BLOOD[3])
		c.put(gx, top + 17, BLOOD[4])
	c.rect(cx - 1, top + 17, 3, 2, BLOOD[2])
	c.put(cx - 1, top + 17, BLOOD[4])


def crown(c, cx, top):
	"""Small gold crown with a cross finial and red gems."""
	rows = [
		"......X......",
		".....XXX.....",
		"......X......",
		"X.....X.....X",
		"XX...XXX...XX",
		"XXX.XXRXX.XXX",
		"XXXXXXXXXXXXX",
		"XRXXXXRXXXXRX",
		"XXXXXXXXXXXXX",
	]
	k = Canvas(26, 18)
	for y, row in enumerate(rows):
		for x, ch in enumerate(row):
			for sy in range(2):
				for sx in range(2):
					px, py = x * 2 + sx, y * 2 + sy
					if ch == "X":
						col = GOLD[4] if y < 3 else GOLD[3] if (px < 12 and y < 7) else GOLD[2]
						if y == 8 or (sx == 1 and sy == 1 and y < 8 and px > 13):
							col = GOLD[1]
						k.put(px, py, col)
					elif ch == "R":
						k.put(px, py, BLOOD[4] if (sx, sy) == (0, 0) else BLOOD[2])
	c.blit(outline(k, OUTLINE), cx - 14, top - 1)


def gild(mask, w, h, seed):
	"""Turn a glyph mask into bevelled, slightly worn gold."""
	r = random.Random(seed)
	c = Canvas(w, h)
	ys = [y for _, y in mask]
	y0, y1 = min(ys), max(ys)
	for (x, y) in mask:
		if not (0 <= x < w and 0 <= y < h):
			continue
		t = (y - y0) / max(1, y1 - y0)
		col = GOLD[3] if t < 0.45 else GOLD[2]
		up = (x, y - 1) not in mask
		left = (x - 1, y) not in mask
		down = (x, y + 1) not in mask
		right = (x + 1, y) not in mask
		if up or left:
			col = GOLD[4] if t < 0.5 else GOLD[3]
		if down or right:
			col = GOLD[1]
		if not (up or left or down or right) and r.random() < 0.04:
			col = GOLD[2] if col is GOLD[3] else GOLD[1]  # worn speckles
		c.put(x, y, col)
	return c


def logo():
	W, H = 300, 112
	c = Canvas(W, H)
	line1, line2 = "Milady's", "Knight"
	w1, w2 = text_width(line1, 1), text_width(line2, 1)
	base1, base2 = 54, 94
	x1 = (W - w1) // 2 - 6
	x2 = (W - w2) // 2 + 14
	cx = W // 2 + 2
	banner(c, 34, W - 34, 30, 58, "banner")
	sword(c, cx, 12, 108)
	crown(c, cx + 1, 4)
	pen = Pen(W, H)
	write(pen, line1, x1, base1, 1)
	write(pen, line2, x2, base2, 1)
	letters = gild(pen.mask, W, H, "gold")
	# dark rim then a soft drop shadow so the gold reads on red cloth and on the night sky
	rim = outline(letters, OUTLINE)
	shadow = Canvas(W, H)
	for y in range(H):
		for x in range(W):
			if rim.get(x, y) is not None:
				shadow.put(x + 1, y + 2, (12, 8, 14, 255))
	c.blit(shadow, 0, 0)
	c.blit(rim, 0, 0)
	return c


# ------------------------------------------------------------- small UI bits
def focus_plate():
	c = Canvas(12, 12)
	for y in range(12):
		for x in range(12):
			ring = min(x, y, 11 - x, 11 - y)
			if min(x, 11 - x) == 0 and min(y, 11 - y) == 0:
				continue
			if ring == 0:
				col = OUTLINE
			elif ring == 1:
				col = GOLD[2] if y < 6 else GOLD[1]
			else:
				col = (88, 24, 34, 235) if y < 6 else (70, 18, 28, 235)
			c.put(x, y, col)
	for x in range(3, 9):
		c.put(x, 1, GOLD[3])
	return c


def cursor():
	rows = [
		"X......",
		"XX.....",
		"XYX....",
		"XYYX...",
		"XYYYX..",
		"XYYX...",
		"XYX....",
		"XX.....",
		"X......",
	]
	c = Canvas(7, 9)
	for y, row in enumerate(rows):
		for x, ch in enumerate(row):
			if ch == "X":
				c.put(x, y, GOLD[3] if y < 4 else GOLD[2])
			elif ch == "Y":
				c.put(x, y, GOLD[4] if y < 4 else GOLD[3])
	return outline(c, OUTLINE) if False else c


def lock():
	rows = [
		"..XXX..",
		".X...X.",
		".X...X.",
		"XXXXXXX",
		"XYYYYYX",
		"XYYKYYX",
		"XYYKYYX",
		"XXXXXXX",
	]
	c = Canvas(7, 8)
	for y, row in enumerate(rows):
		for x, ch in enumerate(row):
			col = {"X": STONE[4], "Y": STONE[3], "K": OUTLINE}.get(ch)
			if col is not None:
				c.put(x, y, col)
	return c


# ------------------------------------------------------------------- ledge
def ledge():
	"""Broken rampart top for the title-screen foreground, lit faintly from the right (moon)."""
	W, H = 220, 70
	r = random.Random("ledge")
	c = Canvas(W, H)
	# silhouette height per column: crenels on the left, crumbling toward the right
	tops = []
	for x in range(W):
		if x < 150:
			merlon = (x // 18) % 2 == 0
			top = 6 if merlon else 16
		else:
			top = 16 + int((x - 150) ** 1.35 * 0.25) + r.randint(0, 2)
		tops.append(min(H - 1, top))
	for x in range(W):
		for y in range(tops[x], H):
			row = (y - 6) // 7
			off = 0 if row % 2 == 0 else 9
			mortar = (y - 6) % 7 == 0 or (x + off) % 18 == 0
			depth = (y - tops[x])
			col = STONE_COOL[1] if mortar else STONE_COOL[2]
			if depth < 2:
				col = STONE_COOL[4] if not mortar else STONE_COOL[3]  # lit top edge
			elif depth < 4 and not mortar:
				col = STONE_COOL[3]
			if y > H - 22:
				col = STONE_COOL[1] if not mortar else STONE_COOL[0]  # falls into shadow
			c.put(x, y, col)
	# moss and creepers on the crenels
	for x in range(W):
		if r.random() < 0.35:
			for k in range(r.randint(1, 3 if x < 150 else 5)):
				c.put(x, tops[x] + k, MOSS[2] if k == 0 else MOSS[1])
	# a few chipped stones / cracks
	for _ in range(16):
		x = r.randint(4, 140)
		y = r.randint(max(tops[x] + 4, 10), H - 24)
		for k in range(r.randint(2, 5)):
			c.put(x + k // 2, y + k, STONE_COOL[0])
	return outline(c, OUTLINE)


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	outputs = {
		"ui_logo.png": logo(),
		"ui_menu_ledge.png": ledge(),
		"ui_menu_focus.png": focus_plate(),
		"ui_menu_cursor.png": cursor(),
		"ui_menu_lock.png": lock(),
	}
	for name, canvas in outputs.items():
		save_png(canvas, os.path.join(OUT, name))
		print(name, canvas.w, canvas.h)
		if preview:
			save_png(canvas, os.path.join(preview, name[:-4] + "_x3.png"), 3, BG)


if __name__ == "__main__":
	main()

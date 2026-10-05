"""RUN-018 UI art: weapon icons (12 and 24 px), tier badges, reward cards, chest-kind glyphs.

Usage: python3 tools/art/run018/ui_icons.py [--preview DIR]

Outputs (assets/run018/ui/), all RGBA, 1x pixels, deterministic, drawn in-house from tools/art/palette.py
(provenance: original, project-generated, no third-party asset):
  ui_weapon_icons.png        108x12   9 cells of 12x12: Sword, Longsword, BrutalAxe, DarkScythe, Warhammer,
                                      Halberds, Longbow, ThrowingKnives, empty slot (index 8)
  ui_weapon_icons_large.png  192x24   8 cells of 24x24, same weapon order, no empty cell
  ui_tier_badges.png         54x9     6 cells of 9x9, levels 0..5 (4 and 5 reuse the level-0 plate)
  ui_reward_card.png         24x24    9-slice, margin 8, unfocused card
  ui_reward_card_focus.png   24x24    9-slice, margin 8, focused card (gold trim)
  ui_chest_kind.png          24x12    2 cells of 12x12: common chest, rare chest
Index 0 and 6 of the small strip are the validated items.sword_icon() / items.bow_icon() (reused, not redrawn).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
from pixel import Canvas, grid, line, outline, save_png, sheet  # noqa: E402
from palette import BLOOD, CORRUPT, GOLD, OUTLINE, SLIME_GREEN, STEEL, STONE, WOOD, SKY, MOSS  # noqa: E402
import items  # noqa: E402

OUT = os.path.join(ROOT, "assets", "run018", "ui")
WEAPONS = ["Sword", "Longsword", "BrutalAxe", "DarkScythe", "Warhammer", "Halberds", "Longbow", "ThrowingKnives"]

# ---------------------------------------------------------------- drawing helpers (light from upper-left)
LIGHT = (-0.7071, -0.7071)


def _dist_seg(px, py, a, b):
	ax, ay = a
	bx, by = b
	dx, dy = bx - ax, by - ay
	l2 = dx * dx + dy * dy
	t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
	cx, cy = ax + dx * t, ay + dy * t
	return math.hypot(px - cx, py - cy), t, ((px - cx) * LIGHT[0] + (py - cy) * LIGHT[1])


def seg(c, a, b, hw0, hw1=None, cols=None, w=None):
	"""Thick tapered segment. cols = (light, mid, dark) picked by the side facing the light."""
	hw1 = hw0 if hw1 is None else hw1
	for y in range(c.h):
		for x in range(c.w):
			d, t, side = _dist_seg(x + 0.5, y + 0.5, a, b)
			hw = hw0 + (hw1 - hw0) * t
			if d <= hw:
				k = side / max(hw, 0.01)
				col = cols[0] if k > 0.33 else cols[2] if k < -0.33 else cols[1]
				c.put(x, y, col)


def poly(c, pts, cols, split=(0.28, 0.72)):
	"""Filled polygon, shaded by position along the light axis."""
	proj = [p[0] * LIGHT[0] + p[1] * LIGHT[1] for p in pts]
	lo, hi = min(proj), max(proj)
	n = len(pts)
	for y in range(c.h):
		for x in range(c.w):
			px, py = x + 0.5, y + 0.5
			inside = False
			j = n - 1
			for i in range(n):
				xi, yi = pts[i]
				xj, yj = pts[j]
				if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
					inside = not inside
				j = i
			if inside:
				k = ((px * LIGHT[0] + py * LIGHT[1]) - lo) / max(hi - lo, 0.01)
				k = 1 - k  # 1 = facing light
				c.put(x, y, cols[0] if k > split[1] else cols[2] if k < split[0] else cols[1])


def disc(c, cx, cy, r, cols):
	for y in range(c.h):
		for x in range(c.w):
			dx, dy = x + 0.5 - cx, y + 0.5 - cy
			if math.hypot(dx, dy) <= r:
				k = (dx * LIGHT[0] + dy * LIGHT[1]) / max(r, 0.01)
				c.put(x, y, cols[0] if k > 0.4 else cols[2] if k < -0.4 else cols[1])


def dots(c, pts, col):
	for x, y in pts:
		c.put(x, y, col)


ST = (STEEL[4], STEEL[3], STEEL[2])
STD = (STEEL[3], STEEL[2], STEEL[1])
WD = (WOOD[3], WOOD[2], WOOD[1])
GD = (GOLD[3], GOLD[2], GOLD[1])
CR = (CORRUPT[3], CORRUPT[2], CORRUPT[1])
LEA = (WOOD[2], WOOD[1], WOOD[0])


# ---------------------------------------------------------------- 12 px weapons (hand-placed pixels)
def _g(text, pal):
	text = "\n".join(l.strip() for l in text.strip().splitlines() if l.strip())
	return outline(grid(text, pal), OUTLINE)


def longsword12():
	c = Canvas(12, 12)
	seg(c, (3.5, 8.5), (10.5, 1.5), 1.0, 0.5, ST)  # long slim blade
	c.put(10, 1, STEEL[4])
	dots(c, [(4, 7), (5, 6)], STEEL[3])
	# narrow guard, long two-pixel grip, round pommel
	dots(c, [(2, 7), (3, 8), (4, 9)], GOLD[2])
	dots(c, [(2, 8)], GOLD[3])
	dots(c, [(2, 9), (1, 10)], WOOD[2])
	c.put(0, 11, GOLD[2])
	return outline(c, OUTLINE)


def axe12():
	c = Canvas(12, 12)
	seg(c, (2.5, 9.5), (8.5, 3.5), 0.8, 0.8, WD)  # haft
	# heavy bit, one side only (upper-left), flared edge
	for x, y, col in ((6, 1, STEEL[4]), (7, 1, STEEL[4]), (5, 2, STEEL[4]), (6, 2, STEEL[3]), (7, 2, STEEL[3]), (8, 2, STEEL[2]),
			(4, 3, STEEL[4]), (5, 3, STEEL[3]), (6, 3, STEEL[3]), (7, 3, STEEL[2]),
			(4, 4, STEEL[3]), (5, 4, STEEL[3]), (6, 4, STEEL[2]),
			(5, 5, STEEL[2]), (6, 5, STEEL[1]), (4, 5, STEEL[3])):
		c.put(x, y, col)
	# socket / poll behind the haft
	dots(c, [(9, 3), (8, 4)], STEEL[1])
	dots(c, [(9, 2)], STEEL[2])
	return outline(c, OUTLINE)


def scythe12():
	c = Canvas(12, 12)
	seg(c, (1.5, 10.5), (8.5, 3.5), 0.7, 0.7, WD)  # pole
	# long curved blade sweeping from the pole top to the left, hooked tip down
	for x, y, col in ((8, 2, STEEL[4]), (7, 1, STEEL[4]), (6, 1, STEEL[4]), (5, 1, STEEL[4]), (4, 2, STEEL[3]), (3, 3, STEEL[3]), (2, 4, STEEL[3]), (2, 5, STEEL[2]),
			(7, 2, STEEL[3]), (6, 2, STEEL[3]), (5, 2, STEEL[2]), (4, 3, STEEL[2]), (3, 4, STEEL[2])):
		c.put(x, y, col)
	dots(c, [(9, 2), (9, 3)], CORRUPT[3])  # sparing corrupt accent at the socket
	dots(c, [(9, 4)], CORRUPT[2])
	dots(c, [(3, 5)], CORRUPT[2])
	return outline(c, OUTLINE)


def hammer12():
	c = Canvas(12, 12)
	seg(c, (1.5, 10.5), (7.5, 4.5), 0.8, 0.8, WD)  # haft
	# blocky head set perpendicular, 5x4 block
	for y in range(1, 5):
		for x in range(6, 11):
			pass
	pts = {
		(6, 3): STEEL[4], (7, 2): STEEL[4], (8, 1): STEEL[4], (9, 1): STEEL[4],
		(7, 3): STEEL[3], (8, 2): STEEL[3], (9, 2): STEEL[3], (10, 2): STEEL[2],
		(8, 3): STEEL[3], (9, 3): STEEL[2], (10, 3): STEEL[2], (7, 4): STEEL[2],
		(8, 4): STEEL[2], (9, 4): STEEL[1], (10, 4): STEEL[1], (6, 4): STEEL[3],
	}
	for (x, y), col in pts.items():
		c.put(x, y, col)
	return outline(c, OUTLINE)


def halberd12():
	c = Canvas(12, 12)
	seg(c, (1.5, 10.5), (9.5, 2.5), 0.7, 0.7, WD)  # pole
	dots(c, [(10, 1), (11, 0)], STEEL[4])  # spike
	# axe blade to the upper-left of the pole top, curved edge
	for x, y, col in ((6, 2, STEEL[4]), (7, 2, STEEL[4]), (5, 3, STEEL[4]), (6, 3, STEEL[3]), (7, 3, STEEL[3]), (5, 4, STEEL[3]), (6, 4, STEEL[2]), (7, 4, STEEL[2]),
			(8, 3, STEEL[2]), (4, 4, STEEL[3])):
		c.put(x, y, col)
	dots(c, [(10, 2), (9, 1)], STEEL[3])
	return outline(c, OUTLINE)


def knives12():
	c = Canvas(12, 12)
	# three small knives fanned from a common lower-left grip point: steep, middle, flat
	for (x0, y0, x1, y1) in ((3, 7, 5, 1), (4, 8, 10, 2), (5, 9, 10, 7)):
		line(c, x0, y0, x1, y1, STEEL[3])
		c.put(x1, y1, STEEL[4])
	dots(c, [(4, 6), (5, 5), (7, 5), (8, 4)], STEEL[4])
	dots(c, [(3, 8), (3, 9), (2, 10)], WOOD[2])
	dots(c, [(4, 9)], GOLD[2])
	dots(c, [(2, 9)], WOOD[1])
	return outline(c, OUTLINE)


# ---------------------------------------------------------------- 24 px weapons
def sword24():
	c = Canvas(24, 24)
	seg(c, (9.5, 15.5), (21.5, 3.5), 1.9, 0.6, ST)
	seg(c, (10, 15), (19, 6), 0.4, 0.4, (STEEL[3],) * 3)  # fuller
	seg(c, (6.5, 12.5), (12.5, 18.5), 1.2, 1.2, GD)  # guard
	disc(c, 6.5, 12.5, 1.4, GD)
	disc(c, 12.5, 18.5, 1.4, GD)
	seg(c, (9.5, 15.5), (5.5, 19.5), 1.1, 1.1, WD)
	dots(c, [(8, 16), (7, 17), (6, 18)], WOOD[1])
	disc(c, 3.8, 21.0, 1.6, GD)
	return outline(c, OUTLINE)


def longsword24():
	c = Canvas(24, 24)
	seg(c, (8.5, 16.5), (22.0, 2.5), 1.5, 0.5, ST)  # longer, slimmer blade
	seg(c, (9, 16), (20, 5), 0.35, 0.35, (STEEL[3],) * 3)
	seg(c, (6.0, 13.5), (11.0, 18.5), 0.9, 0.9, (STEEL[4], STEEL[3], STEEL[2]))  # slim steel crossguard
	dots(c, [(6, 13), (11, 18)], GOLD[2])
	seg(c, (8.5, 16.5), (3.0, 22.0), 1.0, 1.0, LEA)  # long leather grip
	dots(c, [(7, 17), (5, 19), (4, 20)], WOOD[3])
	disc(c, 2.0, 22.4, 1.5, GD)
	return outline(c, OUTLINE)


def axe24():
	c = Canvas(24, 24)
	seg(c, (3.5, 21.5), (17.5, 7.5), 1.2, 1.2, WD)
	# one broad bit swept to the upper-left, with a back poll on the other side
	poly(c, [(13, 12), (11.5, 14.5), (5.5, 8.5), (5.0, 5.0), (8.5, 2.5), (15.5, 3.5), (17.5, 6.0)], ST)
	poly(c, [(15.5, 11.0), (18.0, 9.5), (20.5, 9.5), (20.5, 7.0), (18.5, 6.0)], STD)
	seg(c, (13.5, 12.5), (17.5, 8.5), 1.5, 1.5, STD)
	# edge highlight along the bit
	dots(c, [(5, 6), (5, 7), (6, 8), (6, 5), (7, 4)], STEEL[4])
	dots(c, [(10, 10), (11, 11)], STEEL[1])
	seg(c, (14.0, 11.5), (11.0, 14.5), 0.7, 0.7, (STEEL[2],) * 3)
	return outline(c, OUTLINE)


def scythe24():
	c = Canvas(24, 24)
	seg(c, (3.5, 21.5), (16.5, 8.5), 1.1, 1.1, WD)
	# long crescent blade sweeping left from the pole head, hooked tip pointing down
	pts = []
	n = 16
	outer = [(16.5, 5.0), (14.5, 3.0), (11, 2.0), (7.5, 2.5), (4.5, 4.5), (2.5, 7.5), (2.0, 11.0)]
	inner = [(2.0, 11.0), (3.5, 8.5), (6, 6.5), (9, 5.5), (12, 5.5), (14.5, 7.0), (16.5, 8.5)]
	poly(c, outer + inner, ST)
	# dark corrupt accents, sparing: socket gem and a smear on the lower blade edge
	seg(c, (16.5, 6.0), (18.5, 8.0), 1.4, 1.4, CR)
	dots(c, [(3, 9), (3, 10), (4, 8)], CORRUPT[2])
	dots(c, [(8, 6), (10, 6)], CORRUPT[1])
	dots(c, [(9, 3), (10, 3), (6, 4)], STEEL[4])
	return outline(c, OUTLINE)


def hammer24():
	c = Canvas(24, 24)
	seg(c, (3.5, 21.5), (16.0, 9.0), 1.2, 1.2, WD)
	# large blocky head perpendicular to the haft (rotated rectangle)
	poly(c, [(9.0, 8.0), (14.0, 3.0), (22.0, 11.0), (17.0, 16.0)], ST, (0.2, 0.7))
	seg(c, (11.5, 5.5), (19.5, 13.5), 0.6, 0.6, (STEEL[4],) * 3)
	poly(c, [(8.0, 8.0), (10.0, 6.0), (13.0, 9.0), (11.0, 11.0)], STD)  # striking face
	seg(c, (14.5, 14.0), (19.0, 9.5), 0.7, 0.7, (STEEL[1],) * 3)
	dots(c, [(13, 10), (14, 9)], STEEL[1])
	return outline(c, OUTLINE)


def halberd24():
	c = Canvas(24, 24)
	seg(c, (3.0, 21.0), (18.0, 6.0), 1.1, 1.1, WD)
	# long spike on the pole axis, axe blade to the upper-left, small back hook lower-right
	seg(c, (17.0, 7.0), (22.5, 1.5), 1.6, 0.2, ST)
	poly(c, [(16.5, 8.5), (14.0, 11.0), (7.0, 6.5), (7.0, 3.0), (11.5, 4.0), (15.5, 6.5)], ST)
	poly(c, [(17.0, 9.0), (18.5, 12.5), (21.5, 13.5), (19.5, 10.0)], STD)
	dots(c, [(8, 4), (9, 4), (8, 5)], STEEL[4])
	dots(c, [(13, 9)], STEEL[1])
	disc(c, 16.5, 7.5, 1.4, STD)
	return outline(c, OUTLINE)


def knives24():
	c = Canvas(24, 24)
	origin = (6.0, 19.0)
	for tip, hw in (((20.5, 3.5), 1.4), ((7.5, 2.5), 1.3), ((22.0, 12.5), 1.3)):
		dx, dy = tip[0] - origin[0], tip[1] - origin[1]
		l = math.hypot(dx, dy)
		ux, uy = dx / l, dy / l
		hs = (origin[0] + ux * 4.5, origin[1] + uy * 4.5)  # blade starts here
		seg(c, hs, tip, hw, 0.3, ST)
		seg(c, origin, hs, 1.0, 1.0, LEA)
		seg(c, (hs[0] - uy * 1.8, hs[1] + ux * 1.8), (hs[0] + uy * 1.8, hs[1] - ux * 1.8), 0.7, 0.7, GD)
	disc(c, 5.2, 20.0, 1.7, GD)
	return outline(c, OUTLINE)


# ---------------------------------------------------------------- tier badges 9x9
DIGITS = {
	"0": ["XXX", "X.X", "X.X", "X.X", "XXX"],
	"1": [".X.", "XX.", ".X.", ".X.", "XXX"],
	"2": ["XXX", "..X", "XXX", "X..", "XXX"],
	"3": ["XXX", "..X", ".XX", "..X", "XXX"],
	"4": ["X.X", "X.X", "XXX", "..X", "..X"],
	"5": ["XXX", "X..", "XXX", "..X", "XXX"],
}
# (border, fill, digit) -- grey/green/blue/red tiers; the digit stays pale and carries the information
TIERS = {
	0: (STONE[5], STONE[2], STEEL[4]),
	1: (MOSS[3], MOSS[1], STEEL[4]),
	2: ((72, 118, 164, 255), (24, 40, 68, 255), STEEL[4]),
	3: (BLOOD[3], BLOOD[0], STEEL[4]),
}


def badge(level):
	border, fill, ink = TIERS.get(level, TIERS[0])
	c = Canvas(9, 9)
	for y in range(9):
		for x in range(9):
			edge = x in (0, 8) or y in (0, 8)
			if (x in (0, 8)) and (y in (0, 8)):
				continue
			c.put(x, y, OUTLINE if edge else fill)
	# inner 1px border colour on the 7x7 interior frame
	for i in range(1, 8):
		for (x, y) in ((i, 1), (i, 7), (1, i), (7, i)):
			c.put(x, y, border)
	for y in range(5):
		for x in range(3):
			if DIGITS[str(level)][y][x] == "X":
				c.put(3 + x, 2 + y, ink)
	# dark drop-shadow under the digit for legibility on any plate
	for y in range(5):
		for x in range(3):
			if DIGITS[str(level)][y][x] == "X" and c.get(3 + x + 1, 2 + y + 1) == fill and DIGITS[str(level)][min(y + 1, 4)][min(x + 1, 2)] != "X":
				pass
	return c


# ---------------------------------------------------------------- reward cards 24x24 9-slice (margin 8)
def card(focus):
	c = Canvas(24, 24)
	if focus:
		trim, trim_hi, trim_lo, fill, fill2 = GOLD[2], GOLD[3], GOLD[1], (88, 24, 34, 235), (70, 18, 28, 235)
	else:
		trim, trim_hi, trim_lo, fill, fill2 = STEEL[1], STEEL[2], STONE[1], (32, 30, 38, 236), (28, 26, 34, 236)
	for y in range(24):
		for x in range(24):
			if (x in (0, 23)) and (y in (0, 23)):
				continue
			if x in (0, 23) or y in (0, 23):
				c.put(x, y, OUTLINE)
				continue
			if x == 1 or x == 22 or y == 1 or y == 22:
				c.put(x, y, trim)
				continue
			c.put(x, y, fill if y < 16 or not focus else fill2)
	if focus:
		c.put(1, 1, trim_hi)
		for x in range(2, 22):
			c.put(x, 1, trim_hi)
		for y in range(2, 22):
			c.put(1, y, trim_hi) if False else None
		for x in range(2, 22):
			c.put(x, 22, trim_lo)
		# soft inner line, as in ui_panel
		for i in range(2, 22):
			for (x, y) in ((i, 2), (i, 21), (2, i), (21, i)):
				c.put(x, y, (74, 22, 32, 235))
		# corner studs
		for (x, y) in ((1, 1), (22, 1), (1, 22), (22, 22)):
			c.put(x, y, GOLD[4])
	else:
		for x in range(2, 22):
			c.put(x, 1, STEEL[2])
		for x in range(2, 22):
			c.put(x, 22, STONE[0])
		# subtle inner shade
		for i in range(2, 22):
			for (x, y) in ((i, 2), (i, 21), (2, i), (21, i)):
				c.put(x, y, (22, 20, 27, 236))
		for (x, y) in ((1, 1), (22, 1), (1, 22), (22, 22)):
			c.put(x, y, STEEL[2])
	return c


# ---------------------------------------------------------------- chest glyphs 12x12
def chest_common():
	p = {"w": WOOD[3], "b": WOOD[2], "d": WOOD[1], "i": STEEL[3], "j": STEEL[2], "k": STEEL[1], "g": GOLD[3]}
	return _g("""
		............
		............
		.wwwwwwwwww.
		.bijbbbbijb.
		.bijbbbbijb.
		.kkkkkkkkkk.
		.wijwgwwijw.
		.bijbbbbijb.
		.bijbbbbijb.
		.ddkddddkdd.
		............
		............
	""", p)


def chest_rare():
	cold, cold_d, cold_k = (150, 200, 240, 255), (72, 118, 164, 255), (24, 40, 68, 255)
	p = {"w": WOOD[2], "b": WOOD[1], "d": WOOD[0], "i": STEEL[4], "j": STEEL[3], "k": STEEL[1], "s": STEEL[4],
		"g": cold, "G": cold_d, "c": STEEL[3], "n": cold_k, "m": cold_d}
	return _g("""
		............
		....cssc....
		..cswwwwsc..
		.cmwbbggbwmc
		.cmbbbGGbbmc
		.knnnnGnnnnk
		.cmwbbbbbwmc
		.cmbbbbbbbmc
		.cmbbbbbbbmc
		.ckkddddddkc
		............
		............
	""", p)


# ---------------------------------------------------------------- build / preview
def strip(cells):
	return sheet(cells, len(cells))


def build():
	small = [items.sword_icon(), longsword12(), axe12(), scythe12(), hammer12(), halberd12(), items.bow_icon(), knives12(), items.empty_icon()]
	large = [sword24(), longsword24(), axe24(), scythe24(), hammer24(), halberd24(), bow24(), knives24()]
	badges = [badge(i) for i in range(6)]
	return {
		"ui_weapon_icons.png": strip(small),
		"ui_weapon_icons_large.png": strip(large),
		"ui_tier_badges.png": strip(badges),
		"ui_reward_card.png": card(False),
		"ui_reward_card_focus.png": card(True),
		"ui_chest_kind.png": strip([chest_common(), chest_rare()]),
	}


def bow24():
	c = Canvas(24, 24)
	p0, p1, p2 = (4.0, 21.0), (2.0, 2.0), (21.0, 4.0)
	for k in range(0, 121):
		t = k / 120
		x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
		y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
		s = x + y
		shade = WOOD[4] if s < 14 else WOOD[3] if s < 21 else WOOD[2]
		for ox, oy in ((0, 0), (1, 0), (0, 1)):
			if s < 14 or ox + oy < 2 or True:
				c.put(int(x) + ox, int(y) + oy, shade)
	seg(c, (5.5, 21.0), (21.0, 5.5), 0.4, 0.4, (STEEL[4],) * 3)
	return outline(c, OUTLINE)


def preview(cells, d):
	os.makedirs(d, exist_ok=True)
	bg = (23, 22, 30, 255)
	for name, cv in cells.items():
		for s in (4, 8):
			save_png(cv, os.path.join(d, name.replace(".png", "_x%d.png" % s)), s, bg)
	# mock: two cards side by side with content, 1x and x3, over the dark ui panel colour
	small = cells["ui_weapon_icons.png"]
	large = cells["ui_weapon_icons_large.png"]
	badges = cells["ui_tier_badges.png"]
	chest = cells["ui_chest_kind.png"]
	for wset, tag in (((2, 0), "A"), ((5, 6), "B"), ((3, 4), "C"), ((1, 7), "D")):
		mock = Canvas(280, 100)
		mock.rect(0, 0, 280, 100, (38, 36, 45, 255))
		for i, wi in enumerate(wset):
			ox, oy = 10 + i * 135, 12
			nine(mock, cells["ui_reward_card_focus.png" if i == 0 else "ui_reward_card.png"], ox, oy, 120, 64)
			crop = Canvas(24, 24)
			for y in range(24):
				for x in range(24):
					crop.put(x, y, large.get(wi * 24 + x, y))
			mock.blit(crop, ox + 8, oy + 8)
			bd = Canvas(9, 9)
			for y in range(9):
				for x in range(9):
					bd.put(x, y, badges.get((1 + i * 2) * 9 + x, y))
			mock.blit(bd, ox + 40, oy + 40)
			ic = Canvas(12, 12)
			for y in range(12):
				for x in range(12):
					ic.put(x, y, chest.get(i * 12 + x, y))
			mock.blit(ic, ox + 100, oy + 6)
			ic2 = Canvas(12, 12)
			for y in range(12):
				for x in range(12):
					ic2.put(x, y, small.get(wi * 12 + x, y))
			mock.blit(ic2, ox + 100, oy + 46)
		for s in (1, 3):
			save_png(mock, os.path.join(d, "mock_cards_%s_x%d.png" % (tag, s)), s, (38, 36, 45, 255))


def nine(dst, src, x0, y0, w, h, m=8):
	for y in range(h):
		for x in range(w):
			sx = x if x < m else (24 - (w - x)) if x >= w - m else m + (x - m) % (24 - 2 * m)
			sy = y if y < m else (24 - (h - y)) if y >= h - m else m + (y - m) % (24 - 2 * m)
			dst.put(x0 + x, y0 + y, src.get(sx, sy))


def main():
	os.makedirs(OUT, exist_ok=True)
	cells = build()
	for name, cv in cells.items():
		save_png(cv, os.path.join(OUT, name))
	# checks
	s = cells["ui_weapon_icons.png"]
	sw, bw = items.sword_icon(), items.bow_icon()
	ok0 = all(s.get(x, y) == sw.get(x, y) for y in range(12) for x in range(12))
	ok6 = all(s.get(6 * 12 + x, y) == bw.get(x, y) for y in range(12) for x in range(12))
	print("sizes:", {n: (c.w, c.h) for n, c in cells.items()})
	print("identity index0 == sword_icon:", ok0, "| index6 == bow_icon:", ok6)
	if "--preview" in sys.argv:
		preview(cells, sys.argv[sys.argv.index("--preview") + 1])


if __name__ == "__main__":
	main()

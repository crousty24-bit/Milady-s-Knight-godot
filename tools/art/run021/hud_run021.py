"""RUN-021 HUD pass: active-effect icons and the round player avatar.

Usage: python3 tools/art/run021/hud_run021.py [--preview DIR]

Outputs (assets/run021/ui/):
  ui_effect_shield.png        12x12  first pass (7 Oct 2026), kept for reference, no longer used by the HUD.
  ui_effect_shield_large.png  24x24  Magic Shield effect, top-right of the HUD (second pass, human request): the
                                     RUN-019 pickup shield redrawn bigger, rim, quartered field, pale sigil, outline.
  ui_avatar_frame_round.png   34x34  round gold frame, dark outer/inner lines, four red gems on the diagonals;
                                     transparent window of diameter 28 at (3,3).
  ui_tier_badges_large.png    72x12  6 cells of 12x12, weapon levels 0..5 for the HUD slots (third pass): the RUN-018
                                     tier plates (grey/green/blue/red, 4 and 5 on the level-0 plate) with a 5x7 digit,
                                     shown right after the weapon name, which no longer carries the level number.
  ui_weapon_icons_xl.png     432x48  9 cells of 48x48 for the chest reward cards (fourth pass): the eight RUN-018
                                     24 px weapon drawings re-rasterised natively at 2x from their geometry (segments,
                                     polygons, discs), so edges stay single crisp pixels; hand-placed accent dots become
                                     2x2. Cell 8 is the empty slot (no upgrade available): dashed steel frame.
  ui_portrait_knight_round.png 28x28 three-quarter view of the in-game knight (assets/run018/knight: rounded steel
                                     great helm, protruding visor with a dark slit, red mantle, steel plate), facing
                                     right like the sprite, light from the upper left; masked to the round window.

Original art drawn by code from tools/art/palette.py; deterministic. No third-party pixel, no AI image.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ART)
from pixel import Canvas, hexc, outline, save_png  # noqa: E402
from palette import BLOOD, GOLD, MOSS, OUTLINE, SKY, STEEL, STONE  # noqa: E402

ROOT = os.path.normpath(os.path.join(ART, "..", ".."))
OUT = os.path.join(ROOT, "assets", "run021", "ui")
# Same ramp as the RUN-019 Magic Shield item, aura and pickup VFX.
BLUE = [hexc(c) for c in ("0b2340", "1b4f94", "3a8fd4", "7ad0f0", "dcf7ff")]
# Half widths of the heater shield, top to bottom (8 px wide, 9 px tall before the outline).
ROWS = [4, 4, 4, 4, 4, 3, 3, 2, 1]


def shield_icon():
	b = Canvas(10, 10)
	for i, w in enumerate(ROWS):
		for x in range(5 - w, 5 + w):
			col = BLUE[2] if x < 5 else BLUE[1]
			if i > 5:
				col = BLUE[1] if x < 5 else BLUE[0]
			if x in (5 - w, 4 + w) or i == 0:
				col = BLUE[3] if (x < 5 or i == 0) else BLUE[2]
			b.put(x, i, col)
	# Sigil: vertical bar and short crossbar, as on the pickup.
	for y in range(2, 7):
		b.put(4, y, BLUE[4])
	for x in (3, 5):
		b.put(x, 3, BLUE[4])
	b.put(5, 2, BLUE[3])
	f = Canvas(12, 12)
	f.blit(outline(b, OUTLINE), 1, 1)
	return f


# ---------------------------------------------------------------- large shield (24x24)
# Half widths of a 20 px wide heater shield, 21 rows.
LARGE_ROWS = [10] * 11 + [9, 9, 8, 7, 6, 5, 4, 3, 2, 1]


def shield_icon_large():
	b = Canvas(22, 22)
	cx = 11
	inside = set()
	for i, w in enumerate(LARGE_ROWS):
		for x in range(cx - w, cx + w):
			inside.add((x, i))
	for (x, y) in inside:
		edge = any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
		inner_edge = not edge and any((x + dx, y + dy) not in inside for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2) if abs(dx) + abs(dy) <= 2)
		left = x < cx
		if edge:
			# Bright rim, lit from the upper left.
			col = BLUE[4] if (left and y < 8) or y == 0 else BLUE[3] if left or y < 3 else BLUE[2]
		elif inner_edge:
			col = BLUE[1] if left else BLUE[0]
		else:
			# Quartered field: light upper-left, deep lower-right.
			upper = y < 9
			col = BLUE[2] if left == upper else BLUE[1]
			if not left and not upper:
				col = BLUE[0] if y > 14 else BLUE[1]
		b.put(x, y, col)
	# Sigil: tall pale cross with a small lozenge at the crossing (the pickup's "protection" rune).
	for y in range(3, 17):
		b.put(10, y, BLUE[4])
		b.put(11, y, BLUE[3])
	for x in range(6, 16):
		b.put(x, 7, BLUE[4] if x < 11 else BLUE[3])
	for (x, y) in ((9, 6), (12, 6), (9, 8), (12, 8)):
		b.put(x, y, BLUE[3])
	# Specular glint on the upper-left rim.
	for (x, y) in ((3, 2), (4, 2), (3, 3)):
		b.put(x, y, BLUE[4])
	f = Canvas(24, 24)
	f.blit(outline(b, OUTLINE), 1, 1)
	return f


# ---------------------------------------------------------------- large tier badges (12x12)
DIGITS_5X7 = {
	"0": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
	"1": ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", ".XXX."],
	"2": [".XXX.", "X...X", "....X", "...X.", "..X..", ".X...", "XXXXX"],
	"3": ["XXXX.", "....X", "....X", ".XXX.", "....X", "....X", "XXXX."],
	"4": ["...X.", "..XX.", ".X.X.", "X..X.", "XXXXX", "...X.", "...X."],
	"5": ["XXXXX", "X....", "XXXX.", "....X", "....X", "X...X", ".XXX."],
}
# (border, fill) as the RUN-018 tiers: grey / green / blue / red; the pale digit carries the information.
TIERS = {
	0: (STONE[5], STONE[2]),
	1: (MOSS[3], MOSS[1]),
	2: ((72, 118, 164, 255), (24, 40, 68, 255)),
	3: (BLOOD[3], BLOOD[0]),
}


def badge_large(level):
	border, fill = TIERS.get(level, TIERS[0])
	c = Canvas(12, 12)
	for y in range(12):
		for x in range(12):
			if x in (0, 11) and y in (0, 11):
				continue
			edge = x in (0, 11) or y in (0, 11)
			inner = x in (1, 10) or y in (1, 10)
			c.put(x, y, OUTLINE if edge else border if inner else fill)
	glyph = DIGITS_5X7[str(level)]
	for y in range(7):
		for x in range(5):
			if glyph[y][x] == "X":
				# Dark drop shadow first, so the digit reads on every tier colour.
				if c.get(4 + x, 3 + y) == fill:
					c.put(4 + x, 3 + y, OUTLINE)
	for y in range(7):
		for x in range(5):
			if glyph[y][x] == "X":
				c.put(3 + x, 2 + y, STEEL[4])
	return c


def badge_strip():
	strip = Canvas(72, 12)
	for level in range(6):
		strip.blit(badge_large(level), level * 12, 0)
	return strip


# ---------------------------------------------------------------- 48 px weapon icons (reward cards)
SCALE = 2


class _Canvas2x(Canvas):
	"""Canvas whose direct put() calls (accent dots, the bow curve) land as SCALE x SCALE blocks,
	while the geometric helpers below draw natively at the doubled resolution."""
	native = False

	def put(self, x, y, color):
		if self.native:
			Canvas.put(self, x, y, color)
			return
		for dy in range(SCALE):
			for dx in range(SCALE):
				Canvas.put(self, x * SCALE + dx, y * SCALE + dy, color)


def _native(fn):
	def wrapped(c, *args, **kwargs):
		c.native = True
		try:
			fn(c, *args, **kwargs)
		finally:
			c.native = False
	return wrapped


def weapon_icons_xl():
	sys.path.insert(0, os.path.join(ART, "run018"))
	import ui_icons as r18  # noqa: E402  (RUN-018 geometry, read only)
	k = SCALE
	orig = {name: getattr(r18, name) for name in ("seg", "poly", "disc", "Canvas")}
	seg, poly, disc = (_native(orig["seg"]), _native(orig["poly"]), _native(orig["disc"]))
	r18.seg = lambda c, a, b, hw0, hw1=None, cols=None, w=None: seg(c, (a[0] * k, a[1] * k), (b[0] * k, b[1] * k), hw0 * k, None if hw1 is None else hw1 * k, cols)
	r18.poly = lambda c, pts, cols, split=(0.28, 0.72): poly(c, [(x * k, y * k) for x, y in pts], cols, split)
	r18.disc = lambda c, cx, cy, r, cols: disc(c, cx * k, cy * k, r * k, cols)
	r18.Canvas = lambda w, h: _Canvas2x(w * k, h * k)
	try:
		cells = [r18.sword24(), r18.longsword24(), r18.axe24(), r18.scythe24(), r18.hammer24(), r18.halberd24(), r18.bow24(), r18.knives24()]
	finally:
		for name, value in orig.items():
			setattr(r18, name, value)
	empty = Canvas(48, 48)
	for i in range(6, 42):
		if (i // 3) % 2 == 0:
			for (x, y) in ((i, 6), (i, 41), (6, i), (41, i)):
				empty.put(x, y, STEEL[1])
	strip = Canvas(48 * 9, 48)
	for index, cell in enumerate(cells + [empty]):
		strip.blit(cell, index * 48, 0)
	return strip


# ---------------------------------------------------------------- round avatar
FRAME = 34
WINDOW = 28
WINDOW_AT = 3


def _window_mask(x, y):
	c = (WINDOW - 1) / 2.0
	return math.hypot(x - c, y - c) <= WINDOW / 2.0 - 0.15


def avatar_frame_round():
	c = Canvas(FRAME, FRAME)
	centre = (FRAME - 1) / 2.0
	for y in range(FRAME):
		for x in range(FRAME):
			if _window_mask(x - WINDOW_AT, y - WINDOW_AT):
				continue
			d = math.hypot(x - centre, y - centre)
			if d > FRAME / 2.0 - 0.15:
				continue
			if d > FRAME / 2.0 - 1.15:
				color = OUTLINE
			elif d < WINDOW / 2.0 + 0.85:
				color = OUTLINE
			else:
				# Bevelled gold ring: light from the upper left, shade bottom right.
				lit = (x - centre) + (y - centre) < -2.0
				shade = (x - centre) + (y - centre) > 5.0
				outer = d > FRAME / 2.0 - 2.2
				color = (GOLD[4] if outer else GOLD[3]) if lit else (GOLD[1] if outer else GOLD[0]) if shade else (GOLD[3] if outer else GOLD[2])
			c.put(x, y, color)
	# Four red gems on the diagonals, set in the ring.
	for ang in (45, 135, 225, 315):
		r = (FRAME / 2.0 + WINDOW / 2.0) / 2.0
		gx = int(round(centre + r * math.cos(math.radians(ang)) - 1))
		gy = int(round(centre + r * math.sin(math.radians(ang)) - 1))
		c.rect(gx, gy, 2, 2, BLOOD[2])
		c.put(gx, gy, BLOOD[4])
		c.put(gx + 1, gy + 1, BLOOD[0])
	return c


# Helm silhouette of the three-quarter view, y: (left x, right x). The visor juts out to the right.
HELM = {
	2: (11, 16), 3: (9, 18), 4: (8, 19), 5: (7, 20), 6: (7, 20), 7: (7, 21), 8: (7, 22), 9: (7, 23),
	10: (7, 23), 11: (7, 22), 12: (7, 21), 13: (7, 21), 14: (7, 21), 15: (7, 21), 16: (8, 21), 17: (8, 20),
	18: (9, 20),
}
RIDGE = 16  # centre line of the face: side plane to the left, front plane to the right.
SLIT = (74, 22, 32, 255)


def _helm():
	h = Canvas(WINDOW, WINDOW)
	for y, (lx, rx) in HELM.items():
		for x in range(lx, rx + 1):
			if x == lx:
				color = STEEL[2]  # back edge turning away
			elif x < RIDGE:
				t = (x - lx) / float(RIDGE - lx)
				color = STEEL[4] if 0.1 < t < 0.32 else STEEL[3] if t < 0.62 else STEEL[2]
			elif x == RIDGE:
				color = STEEL[4]
			else:
				color = STEEL[2] if x <= RIDGE + 2 else STEEL[1] if x < rx else STEEL[0]
			if y <= 3 and x < RIDGE:
				color = STEEL[4] if color in (STEEL[3], STEEL[4]) else STEEL[3]
			elif y <= 4 and x > RIDGE:
				color = STEEL[1] if x < rx else STEEL[0]  # dome turning away from the light
			if y >= 16 and x < RIDGE and color == STEEL[4]:
				color = STEEL[3]
			h.put(x, y, color)
	# Visor brim catching the light, eye slit wrapping round the side, dim red glint inside.
	for x in range(11, 24):
		if h.get(x, 8) is not None:
			h.put(x, 8, STEEL[4] if x <= RIDGE + 2 else STEEL[3])
	for x in range(9, 23):
		h.put(x, 9, OUTLINE)
	for x in range(12, 22):
		h.put(x, 10, OUTLINE)
	# The visor juts forward: steel tip and lower lip beyond the slit.
	h.put(23, 9, STEEL[2])
	h.put(22, 10, STEEL[1])
	h.put(23, 10, STEEL[0])
	h.put(19, 9, SLIT)
	h.put(20, 9, BLOOD[1])
	# Shadow under the visor on the front plane.
	for x in range(RIDGE + 1, 23):
		if h.get(x, 11) is not None:
			h.put(x, 11, STEEL[0] if x > RIDGE + 2 else STEEL[1])
	# Breathing holes on the front plane, rivets on the side band.
	for (x, y) in ((18, 13), (18, 14), (20, 13), (20, 14), (18, 16), (20, 16)):
		h.put(x, y, OUTLINE)
	for (x, y) in ((9, 6), (9, 14), (13, 17)):
		h.put(x, y, STEEL[4])
	for (x, y) in ((9, 7), (9, 15)):
		h.put(x, y, STEEL[1])
	# Seam between the dome and the face band on the side.
	for x in range(8, RIDGE):
		if h.get(x, 5) is not None and x not in (9,):
			h.put(x, 5, STEEL[2] if x < 12 else STEEL[1])
	return outline(h, OUTLINE)


def portrait_round():
	c = Canvas(WINDOW, WINDOW)
	# Backdrop: cold night blue, a blood glow behind the far shoulder (as the first portrait).
	for y in range(WINDOW):
		for x in range(WINDOW):
			glow = max(0.0, 1.0 - math.hypot(x - 23, y - 22) / 15.0)
			base = SKY[3] if y < 9 else SKY[2] if y < 17 else SKY[1]
			if glow > 0.55:
				base = BLOOD[0]
			elif glow > 0.3:
				base = (40, 16, 26, 255)
			c.put(x, y, base)
	# Red mantle across the shoulders, folds falling to the lower left.
	for y in range(19, WINDOW):
		for x in range(WINDOW):
			half = 7.0 + (y - 19) * 1.6
			if abs(x - 14.0) <= half:
				color = BLOOD[2] if x < 10 else BLOOD[1] if x < 19 else BLOOD[0]
				if (x - y) % 6 == 0 and 4 < x < 22:
					color = BLOOD[1] if x < 12 else BLOOD[0]
				if y == 19 or (y == 20 and abs(x - 14.0) > half - 1):
					color = BLOOD[3] if x < 14 else BLOOD[2]
				c.put(x, y, color)
	# Far pauldron (right, mostly in shade) then the near one (left, larger, lit), gold edged.
	for y in range(20, 25):
		for x in range(19, 26):
			if (x - 22.5) ** 2 / 12.0 + (y - 22.0) ** 2 / 6.0 <= 1.0:
				c.put(x, y, STEEL[1] if y < 22 else STEEL[0])
	for x in range(20, 25):
		c.put(x, 20, GOLD[1])
	for y in range(19, 27):
		for x in range(1, 13):
			if (x - 6.5) ** 2 / 30.0 + (y - 22.5) ** 2 / 11.0 <= 1.0:
				color = STEEL[4] if (x < 5 and y < 22) else STEEL[3] if y < 23 else STEEL[2] if y < 25 else STEEL[1]
				c.put(x, y, color)
	for x in range(2, 12):
		c.put(x, 19 if 3 < x < 10 else 20, GOLD[3] if x < 7 else GOLD[2])
	# Articulated lames: a dark joint line and a lit edge below it.
	for x in range(2, 12):
		if c.get(x, 23) in (STEEL[2], STEEL[3]):
			c.put(x, 23, STEEL[1])
		if c.get(x, 24) is not None and x < 11:
			c.put(x, 24, STEEL[3] if x < 6 else STEEL[2])
	for (x, y) in ((4, 21), (8, 21)):
		c.put(x, y, GOLD[2])
	# Gorget under the helm, gold rim.
	for y in range(18, 21):
		for x in range(10, 20):
			c.put(x, y, STEEL[3] if x < 13 else STEEL[2] if x < 17 else STEEL[1])
	for x in range(10, 20):
		c.put(x, 20, GOLD[3] if x < 14 else GOLD[2] if x < 17 else GOLD[1])
	c.blit(_helm(), 0, 0)
	# Chin shadow on the gorget.
	for x in range(15, 20):
		c.put(x, 19, STEEL[0])
	# Round window.
	for y in range(WINDOW):
		for x in range(WINDOW):
			if not _window_mask(x, y):
				c.px[y * WINDOW + x] = None
	return c


def composite_avatar():
	"""Preview only: frame over portrait, as the HUD stacks them."""
	a = Canvas(FRAME, FRAME)
	a.blit(portrait_round(), WINDOW_AT, WINDOW_AT)
	a.blit(avatar_frame_round(), 0, 0)
	return a


def main():
	os.makedirs(OUT, exist_ok=True)
	outputs = {
		"ui_effect_shield.png": shield_icon(),
		"ui_effect_shield_large.png": shield_icon_large(),
		"ui_avatar_frame_round.png": avatar_frame_round(),
		"ui_portrait_knight_round.png": portrait_round(),
		"ui_tier_badges_large.png": badge_strip(),
		"ui_weapon_icons_xl.png": weapon_icons_xl(),
	}
	for name, canvas in outputs.items():
		save_png(canvas, os.path.join(OUT, name))
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
		for name, canvas in outputs.items():
			save_png(canvas, os.path.join(preview, name[:-4] + "_x8.png"), 8, (52, 60, 66, 255))
		save_png(composite_avatar(), os.path.join(preview, "avatar_composite_x8.png"), 8, (52, 60, 66, 255))


if __name__ == "__main__":
	main()

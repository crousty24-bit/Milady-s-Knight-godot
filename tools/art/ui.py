"""Generate the HUD art (RUN-029): icons, 9-slice panels, key caps, avatar frame and knight portrait.

Usage: python3 tools/art/ui.py [--preview DIR]

Outputs (assets/sprites/):
  ui_icons.png           60x12  5 icons of 12x12: heart full, heart half, heart empty, coin, coin dim
  ui_panel.png           24x24  9-slice (margin 8): dark translucent fill, gold trim, red inner line, gold studs
  ui_panel_red.png       24x24  same panel with a blood-red trim (death / danger)
  ui_plate.png           12x12  9-slice (margin 4): small plate for interaction prompts and tags
  ui_keycap.png          12x12  9-slice (margin 3): steel key cap with dark ink on a light face
  ui_avatar_frame.png    32x32  gold frame with red corner gems, transparent centre (24x24 window at 4,4)
  ui_portrait_knight.png 24x24  great helm, steel ramp, red mantle, gold trim (palette of tools/art/palette.py)

Everything is drawn by code from tools/art/palette.py, deterministic, no third-party asset.
The 16x16 Assorted RPG Icons pack (Shade, CC0) was inspected but has no HUD heart, coin or key glyph
fitting this style, so no pixel of it is used.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, outline, remap, save_png, sheet  # noqa: E402
from palette import BLOOD, GOLD, OUTLINE, SKY, STEEL, STONE  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
BG = (52, 60, 66, 255)
FILL = (38, 36, 45, 236)  # between STONE[1] and STONE[2] at ~92 % opacity: the world stays faintly visible


# ---------------------------------------------------------------- icons
HEART_SHAPE = [
	".XXX.XXX.",
	"XXXXXXXXX",
	"XXXXXXXXX",
	"XXXXXXXXX",
	".XXXXXXX.",
	"..XXXXX..",
	"...XXX...",
	"....X....",
]


def heart(state):
	"""state: 2 full, 1 left half only, 0 empty. 11x10 body inside a 12x12 frame."""
	body = Canvas(9, 8)
	for y, row in enumerate(HEART_SHAPE):
		for x, ch in enumerate(row):
			if ch != "X":
				continue
			live = state == 2 or (state == 1 and x <= 4)
			if live:
				s = (x - 4) * 0.5 + (y - 3.5) * 0.65
				color = BLOOD[3] if s < -1.2 else BLOOD[2] if s < 1.6 else BLOOD[1]
				if (x, y) in ((1, 1), (2, 1)):
					color = BLOOD[4]
				if (x, y) == (1, 2):
					color = BLOOD[3]
			else:
				color = STONE[2] if (y <= 1 or x <= 1) else STONE[1]
				if (x, y) in ((1, 1), (2, 1)):
					color = STONE[3]
			body.put(x, y, color)
	f = Canvas(12, 12)
	f.blit(outline(body, OUTLINE), 0, 1)
	return f


def coin():
	f = Canvas(12, 12)
	# a plain round coin: rim, bright face with a tilted highlight and a centre notch
	cx = cy = 5.5
	for y in range(12):
		for x in range(12):
			d = math.hypot(x - cx, y - cy)
			if d <= 4.9:
				color = GOLD[1] if d > 3.7 else GOLD[2]
				if d <= 3.7 and (x - cx) * -0.6 + (y - cy) * -0.6 > 1.7:
					color = GOLD[3]
				f.put(x, y, color)
	f.put(3, 3, GOLD[4])
	f.put(4, 3, GOLD[3])
	f.put(3, 4, GOLD[3])
	for y in range(4, 8):
		f.put(6, y, GOLD[1])
	f.put(6, 4, GOLD[0])
	f.put(6, 7, GOLD[0])
	return outline(f, OUTLINE)


def coin_dim():
	mapping = {GOLD[1]: STONE[2], GOLD[2]: STONE[3], GOLD[3]: STONE[4], GOLD[4]: STONE[5], GOLD[0]: STONE[1]}
	return remap(coin(), mapping)


def icon_sheet():
	return sheet([heart(2), heart(1), heart(0), coin(), coin_dim()], 5)


# --------------------------------------------------------------- panels
def panel(size, margin, trim, inner, stud):
	"""Rounded 9-slice plate: outline, 1 px trim, 1 px inner line, translucent fill, corner studs."""
	c = Canvas(size, size)
	last = size - 1
	for y in range(size):
		for x in range(size):
			ring = min(x, y, last - x, last - y)
			if ring == 0:
				color = None if (min(x, last - x) == 0 and min(y, last - y) == 0) else OUTLINE
			elif ring == 1:
				color = trim[0]
			elif ring == 2:
				color = inner
			elif ring == 3 and margin >= 8:
				color = (23, 19, 27, 235)  # soft inner shadow
			else:
				color = FILL
			if color is not None:
				c.put(x, y, color)
	if stud and margin >= 8:
		for ox, oy in ((2, 2), (last - 3, 2), (2, last - 3), (last - 3, last - 3)):
			c.rect(ox, oy, 2, 2, stud[0])
			c.put(ox, oy, stud[1])
	# gold highlight along the top edge only, light from the upper left
	for x in range(margin, size - margin):
		c.put(x, 1, trim[1])
	return c


def plate():
	c = panel(12, 4, (GOLD[1], GOLD[2]), (74, 22, 32, 255), None)
	return c


def keycap():
	c = Canvas(12, 12)
	for y in range(12):
		for x in range(12):
			corner = min(x, 11 - x) == 0 and min(y, 11 - y) == 0
			if corner:
				continue
			if x == 0 or x == 11 or y == 0 or y == 11:
				color = OUTLINE
			elif y == 1:
				color = STEEL[4]
			elif y >= 9:
				color = STEEL[1]
			else:
				color = STEEL[3]
			c.put(x, y, color)
	return c


# --------------------------------------------------------- avatar frame
def avatar_frame():
	c = Canvas(32, 32)
	for y in range(32):
		for x in range(32):
			ring = min(x, y, 31 - x, 31 - y)
			if min(x, 31 - x) == 0 and min(y, 31 - y) == 0:
				continue
			if ring == 0:
				color = OUTLINE
			elif ring in (1, 2):
				# bevelled gold: light top-left, shade bottom-right
				lit = (x + y) < 31
				color = (GOLD[3] if ring == 1 else GOLD[2]) if lit else (GOLD[1] if ring == 1 else GOLD[0])
				if ring == 1 and lit and (x + y) < 20:
					color = GOLD[3]
			elif ring == 3:
				color = OUTLINE
			else:
				continue
			c.put(x, y, color)
	# red gems at the four corners
	for ox, oy in ((1, 1), (28, 1), (1, 28), (28, 28)):
		c.rect(ox, oy, 3, 3, BLOOD[2])
		c.put(ox, oy, BLOOD[4])
		c.put(ox + 2, oy + 2, BLOOD[0])
	return c


# ------------------------------------------------------------- portrait
def portrait():
	c = Canvas(24, 24)
	# backdrop: cold dark blue climbing to a blood glow behind the shoulder
	for y in range(24):
		for x in range(24):
			t = y / 23.0
			glow = max(0.0, 1.0 - math.hypot(x - 20, y - 20) / 14.0)
			base = SKY[2] if t < 0.45 else SKY[1]
			c.put(x, y, BLOOD[0] if glow > 0.45 else (SKY[1] if (glow > 0.2 or t > 0.7) else base))
	# red mantle behind and over the shoulders, deep fold on the right
	for y in range(15, 24):
		for x in range(0, 24):
			half = 5.5 + (y - 14) * 1.25
			if abs(x - 11.5) <= min(half, 11.5):
				color = BLOOD[2] if x < 6 else BLOOD[1] if x < 16 else BLOOD[0]
				if (x + y) % 7 == 0 and 5 < x < 20:
					color = BLOOD[0] if x >= 11 else BLOOD[1]
				c.put(x, y, color)
	# steel pauldrons with a gold edge
	for sx, flip in ((1, False), (22, True)):
		for dy in range(5):
			w = 6 - dy // 2
			for dx in range(w):
				x = sx + dx if not flip else sx - dx
				y = 17 + dy
				ramp = STEEL[3] if (dy < 2 and dx < 3) else STEEL[2] if dy < 3 else STEEL[1]
				if flip:
					ramp = STEEL[1] if dy < 3 else STEEL[0]
				c.put(x, y, ramp)
		x0 = sx if not flip else sx - 5
		for dx in range(6):
			c.put(x0 + dx, 17, GOLD[2] if dx not in (0, 5) else GOLD[1])
	# gorget under the helm
	for y in range(15, 19):
		for x in range(7, 17):
			if y == 18 and (x < 8 or x > 15):
				continue
			c.put(x, y, STEEL[2] if x < 10 else STEEL[1] if x < 14 else STEEL[0])
	for x in range(8, 16):
		c.put(x, 18, GOLD[2] if x < 12 else GOLD[1])
	# great helm: rounded crown, near-flat bottom, left light / right shadow
	rows = {  # y: (left x, right x)
		2: (9, 14), 3: (7, 16), 4: (6, 17), 5: (6, 17), 6: (6, 17), 7: (6, 17),
		8: (6, 17), 9: (6, 17), 10: (6, 17), 11: (6, 17), 12: (6, 17), 13: (7, 16),
		14: (7, 16), 15: (8, 15),
	}
	for y, (lx, rx) in rows.items():
		for x in range(lx, rx + 1):
			t = (x - lx) / float(rx - lx)
			color = STEEL[4] if t < 0.14 else STEEL[3] if t < 0.38 else STEEL[2] if t < 0.66 else STEEL[1] if t < 0.9 else STEEL[0]
			if y <= 3 and color is STEEL[3]:
				color = STEEL[4]
			c.put(x, y, color)
	# eye slit and breath plate
	for x in range(7, 17):
		c.put(x, 8, OUTLINE)
		c.put(x, 9, OUTLINE)
	c.put(7, 9, STEEL[1])
	for x in (10, 11):
		c.put(x, 8, (74, 22, 32, 255))
	for y in range(10, 15):
		c.put(11, y, STEEL[1])
		c.put(12, y, STEEL[4] if y < 12 else STEEL[2])
	for y in (11, 13):
		for x in (14, 15):
			c.put(x, y, OUTLINE)
	# Plain steel like the in-game great helm: rivets and a darker rim, no plume or gilding.
	for x in range(8, 16):
		c.put(x, 15, STEEL[1] if x < 12 else STEEL[0])
	for x, y in ((8, 6), (15, 6), (8, 13), (15, 13)):
		c.put(x, y, STEEL[4] if x < 12 else STEEL[2])
	return c


def helm_outline(c):
	"""Draw a 1 px dark outline around the helm mass (steel pixels) so it separates from the mantle."""
	out = c.copy()
	steel = set(STEEL)
	for y in range(24):
		for x in range(24):
			p = c.get(x, y)
			if p in steel or p in set(GOLD):
				continue
			if any(c.get(x + dx, y + dy) in steel for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and y < 16:
				out.put(x, y, OUTLINE)
	return out


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	red = panel(24, 8, (BLOOD[2], BLOOD[3]), (63, 12, 19, 255), (BLOOD[3], BLOOD[4]))
	outputs = {
		"ui_icons.png": icon_sheet(),
		"ui_panel.png": panel(24, 8, (GOLD[1], GOLD[2]), (74, 22, 32, 255), (GOLD[3], GOLD[4])),
		"ui_panel_red.png": red,
		"ui_plate.png": plate(),
		"ui_keycap.png": keycap(),
		"ui_avatar_frame.png": avatar_frame(),
		"ui_portrait_knight.png": helm_outline(portrait()),
	}
	for name, canvas in outputs.items():
		save_png(canvas, os.path.join(OUT, name))
		print(name, canvas.w, canvas.h)
		if preview:
			save_png(canvas, os.path.join(preview, name[:-4] + "_x8.png"), 8, BG)


if __name__ == "__main__":
	main()

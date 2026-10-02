"""Generate slimes, the gold coin and the HUD icons (RUN-013 harmonisation).

Usage: python3 tools/art/creatures.py [--preview DIR]

Outputs (assets/sprites/):
  enemy_slime_green.png   144x24  6 frames of 24x24, faces LEFT, ground contact on row 23, centred on col 12
  enemy_slime_purple.png  144x24  same layout, CORRUPT ramp, glowing core
  item_gold_coin.png      128x16  8 frames of 16x16, spinning coin centred on (8, 8)
  hud_icons.png           60x12   5 icons of 12x12: heart full, heart half, heart empty, coin, seal

Colours come only from tools/art/palette.py. Light comes from the upper left.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, grid, outline, save_png, sheet  # noqa: E402
from palette import BLOOD, CORRUPT, GOLD, OUTLINE, SLIME_GREEN, STONE  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
BG = (52, 60, 66, 255)


# ---------------------------------------------------------------- slimes
# (body width, body height, forward lean in px at the top, centre shift)
# measured on the inner body; the 1 px outline is added around it.
SLIME_CYCLE = [
	(16, 11, 0.0, 0),    # rest
	(18, 9, -0.5, 0),    # squash
	(14, 13, -2.0, -1),  # stretch, leaning forward (left)
	(16, 12, -1.0, -1),  # land
	(18, 9, 0.0, 0),     # squash
	(15, 12, 0.5, 0),    # recoil
]


def slime_frame(ramp, w, h, lean, shift, tough):
	body = Canvas(24, 24)
	cx = 12.0 + shift
	bottom = 22  # outline lands on row 23
	cells = {}
	for r in range(h):
		t = r / float(h)
		hw = (w / 2.0) * (1.0 - t ** 2.1) ** (1.0 / 2.1)
		if r == 0:
			hw -= 1.0
		elif r == 1:
			hw -= 0.3
		off = lean * (r / float(h - 1)) ** 1.5
		y = bottom - r
		for x in range(24):
			if abs(x + 0.5 - (cx + off)) <= hw:
				cells[(x, y)] = (x + 0.5 - (cx + off)) / (w / 2.0), r / float(h - 1), r
	for (x, y), (u, v, r) in cells.items():
		s = v * 0.95 - u * 0.55
		if r == 0:
			tone = 0
		elif r == 1 or (u > 0.62 and v < 0.7):
			tone = 1
		elif s > 0.8:
			tone = 3
		elif s > 0.3:
			tone = 2
		else:
			tone = 1 if (r <= 2 or u > 0.35) else 2
		body.put(x, y, ramp[tone])
	# rim lights/glossy highlight (upper left)
	top_y = bottom - (h - 1)
	left_x = min(x for (x, y) in cells if y == bottom - h // 2)
	hx = left_x + 2 + int(round(abs(lean) * 0.0))
	hy = top_y + 2
	for dx, dy, tone in ((0, 0, 4), (1, 0, 4), (0, 1, 3), (-1, 1, 3), (2, 0, 3)):
		if (hx + dx, hy + dy) in cells:
			body.put(hx + dx, hy + dy, ramp[tone])
	# eyes on the left side: dark sockets with a pale menacing slit
	ey = bottom - int(h * 0.55)
	ex = int(round(cx - w * 0.28 + lean * 0.45))
	for k, e in enumerate((ex, ex + (4 if w >= 16 else 3))):
		glow = CORRUPT[4] if tough else ramp[4]
		body.put(e, ey, glow)
		body.put(e + 1, ey, glow)
		body.put(e, ey + 1, glow)
		body.put(e + 1, ey + 1, glow)
		body.put(e, ey + 1, OUTLINE)  # pupil looks left
		body.put(e - 1 + k, ey - 1 + k, OUTLINE)  # angry brow slants down to the centre
		body.put(e + k, ey - 1, OUTLINE)
		body.put(e + 1 + k, ey - 1 + (1 - k) * 0, OUTLINE)
	if tough:
		# glowing core under the dome
		cxp, cyp = int(round(cx + lean * 0.3 + 2)), bottom - 3
		for dx, dy, c in ((0, 0, CORRUPT[4]), (-1, 0, CORRUPT[3]), (1, 0, CORRUPT[3]), (0, -1, CORRUPT[3]), (0, 1, CORRUPT[3])):
			if (cxp + dx, cyp + dy) in cells:
				body.put(cxp + dx, cyp + dy, c)
	return outline(body, OUTLINE)


def slime_sheet(ramp, tough):
	return sheet([slime_frame(ramp, w, h, l, s, tough) for (w, h, l, s) in SLIME_CYCLE], 6)


# ------------------------------------------------------------------ coin
COIN_PAL = {"o": OUTLINE, "k": GOLD[0], "d": GOLD[1], "m": GOLD[2], "l": GOLD[3], "h": GOLD[4]}
COIN_FRONT = """
..oooooo..
.oldmmmmo.
olmmmmmmdo
olmmldmmdo
olmldddmdo
olmmdddmdo
omdmmdmmdo
odmmmmmmdo
.oddmmddo.
..oooooo..
"""
COIN_BACK = """
..oooooo..
.oldmmmmo.
olmmmmmmdo
olmmmmmmdo
olmmmmmmdo
olmmmmmmdo
omdmmmmddo
odmmmmmmdo
.oddmmddo.
..oooooo..
"""


def resample(face, width):
	out = Canvas(face.w, face.h)
	if width <= 2:
		for y in range(2, face.h - 2):
			out.put(face.w // 2 - 1, y, OUTLINE)
			out.put(face.w // 2, y, OUTLINE)
		for y in range(1, face.h - 1):
			pass
		# edge-on: a slim gold band with outline
		band = Canvas(face.w, face.h)
		for y in range(1, face.h - 1):
			band.put(face.w // 2 - 1, y, GOLD[3] if y < 4 else GOLD[2] if y < 7 else GOLD[1])
			band.put(face.w // 2, y, GOLD[2] if y < 4 else GOLD[1] if y < 7 else GOLD[0])
		return outline(band, OUTLINE)
	x0 = (face.w - width) // 2
	for x in range(width):
		sx = min(face.w - 1, int((x + 0.5) * face.w / width))
		for y in range(face.h):
			out.put(x0 + x, y, face.get(sx, y))
	return out


def coin_frames():
	front = grid(COIN_FRONT, COIN_PAL)
	back = grid(COIN_BACK, COIN_PAL)
	widths = [10, 9, 7, 4, 2, 4, 7, 9]
	frames = []
	for i, w in enumerate(widths):
		face = front if i < 4 else back
		spun = resample(face, w)
		f = Canvas(16, 16)
		f.blit(spun, 3, 3)
		if i in (1, 5) and w >= 7:
			f.put(5, 5, GOLD[4])
			f.put(4, 6, GOLD[4]) if i == 1 else None
		frames.append(f)
	return frames


# ------------------------------------------------------------- HUD icons
HEART = """
.oooo.oooo.
ohhllolllmo
ohlllllllmo
ollllllllmo
ollllllmmdo
.olllmmmmdo
.ommmmmmdo.
..ommmmdo..
...ommdo...
....odo....
.....o.....
"""
HEART_LIVE = {"o": OUTLINE, "h": BLOOD[4], "l": BLOOD[3], "m": BLOOD[2], "d": BLOOD[1]}
HEART_DEAD = {"o": OUTLINE, "h": STONE[3], "l": STONE[2], "m": STONE[1], "d": STONE[0]}


def heart(live_cols, mono=False):
	f = Canvas(12, 12)
	rows = HEART.strip("\n").split("\n")
	for y, row in enumerate(rows):
		for x, ch in enumerate(row):
			if ch == ".":
				continue
			pal = HEART_LIVE if x < live_cols else HEART_DEAD
			f.put(x + 1, y, pal[ch])
	# a faint inner rim keeps empty sockets readable on dark HUD panels
	if live_cols < 11:
		for y, row in enumerate(rows):
			for x, ch in enumerate(row):
				if x >= live_cols and ch == "o":
					f.put(x + 1, y, STONE[3] if (x + y) % 1 == 0 and (y < 4 or x < 6) else STONE[2])
	return f


def hud_coin():
	f = Canvas(12, 12)
	f.blit(grid(COIN_FRONT, COIN_PAL), 1, 1)
	return f


def hud_seal():
	f = Canvas(12, 12)
	cx = cy = 5.5
	cells = set()
	for y in range(12):
		for x in range(12):
			dx, dy = x - cx, y - cy
			ang = math.atan2(dy, dx)
			if math.hypot(dx, dy) <= 4.7 + 0.35 * math.cos(10 * ang):
				cells.add((x, y))
	for (x, y) in cells:
		s = -(x - cx) * 0.5 - (y - cy) * 0.6
		f.put(x, y, GOLD[3 if s > 2.0 else 2 if s > -1.6 else 1])
	for (x, y) in [(3, 3), (5, 3), (6, 3), (8, 3)] + [(x, 4) for x in range(3, 9)]:
		f.put(x, y, GOLD[0])
	for x in range(3, 9):
		f.put(x, 5, GOLD[1])
		f.put(x, 6, GOLD[0])
	f.put(4, 4, GOLD[1])
	f.put(7, 4, GOLD[1])
	f.put(3, 2, GOLD[4]); f.put(4, 2, GOLD[4])
	return outline(f, OUTLINE)


def hud_sheet():
	return sheet([heart(11), heart(5), heart(0), hud_coin(), hud_seal()], 5)


# ------------------------------------------------------------------ main
def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	outputs = {
		"enemy_slime_green.png": slime_sheet(SLIME_GREEN, False),
		"enemy_slime_purple.png": slime_sheet(CORRUPT, True),
		"item_gold_coin.png": sheet(coin_frames(), 8),
		"hud_icons.png": hud_sheet(),
	}
	for name, canvas in outputs.items():
		save_png(canvas, os.path.join(OUT, name))
		print(name, canvas.w, canvas.h)
		if preview:
			save_png(canvas, os.path.join(preview, name[:-4] + "_x8.png"), 8, BG)


if __name__ == "__main__":
	main()

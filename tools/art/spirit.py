"""Generate The Ancient Spirit (RUN-017): world sprite (rest / dialogue), banner portrait and aura.

Usage: python3 tools/art/spirit.py [--preview DIR]

Outputs (assets/sprites/):
  npc_spirit_idle.png    256x48  8 frames of 32x48: rest, slow float, drifting motes
  npc_spirit_talk.png    256x48  8 frames of 32x48: dialogue, open hand toward the listener,
                                 brighter eyes and staff light
  ui_portrait_spirit.png  24x24  hooded face for the dialogue banner (same frame as the knight portrait)
  vfx_spirit_aura.png     48x56  dithered cool halo drawn behind the spirit (alpha only)
  npc_spirit_appear.png  256x48  RUN-017/2, 8 frames of 32x48: pale silhouette gathers bottom-up, then
                                 takes colour; last frame = idle frame 0
  npc_spirit_disappear.png 256x48 RUN-017/2, 8 frames: idle frame 0 pales, dissolves bottom-up into
                                 rising motes; last frame empty
  vfx_spirit_manifest.png 384x128 RUN-017/2, 8 columns of 48x64, row 0 appear / row 1 disappear: column
                                 of cold light and motes, translucent only, same anchor as the aura

Appear/disappear are sampled by the level's phase progress (scripts/spirit_art.gd), not played at a
frame rate. The manifest light is drawn outside the pass-through fade so the apparition stays readable
while the knight stands inside the spirit at the 32 px trigger.

Frames face right; the game mirrors them toward the knight. The bottom row of a frame is the ground
line (origin of the AncientSpirit node); the figure floats about 5 px above it. Body about 16x34 px
opaque, slightly taller than the knight's 20x28 as a robed elder, at the same 1x pixel density.

Design: the spirit of an ancient sage (docs/09). Hooded robe read from the hooded statue of the
project concept art, made spectral: pale cold ramp, robe dissolving into a tail, staff of the same
light. Eyes and the staff core use the pale yellow of neutral interaction (docs/06); no gold, red,
violet or green, which carry gameplay meanings.
Everything is drawn by code from tools/art/palette.py conventions, deterministic, no third-party asset.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, hexc, outline, save_png, sheet  # noqa: E402
from palette import GOLD, OUTLINE, SKY  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
BG = (30, 36, 48, 255)
W, H = 32, 48
FRAMES = 8
# Pale spectral ramp, dark -> light: cold and desaturated so it reads as a ghost, not as the cyan
# of a magic shield. Brighter than the terrain so the NPC separates from the night village.
SPIRIT = [hexc(c) for c in ("1d2735", "2e4254", "4a6679", "7193a2", "a8c6cc", "e0f0ee")]
VOID = hexc("0b0e14")
EYE = GOLD[4]
EYE_DIM = GOLD[3]

# Opaque robe, y: (left x, right x), an A-line that flares to the hem. Hood 7-17 with the brim toward +x, robe 18-35.
ROBE = {
	7: (13, 14), 8: (12, 16), 9: (11, 18), 10: (11, 19), 11: (10, 20), 12: (10, 20), 13: (10, 20),
	14: (10, 20), 15: (10, 20), 16: (10, 20), 17: (11, 20), 18: (10, 20), 19: (9, 21), 20: (8, 21),
	21: (8, 22), 22: (8, 22), 23: (8, 22), 24: (8, 22), 25: (8, 22), 26: (7, 22), 27: (7, 22),
	28: (7, 22), 29: (7, 22), 30: (7, 23), 31: (7, 23), 32: (7, 23), 33: (7, 23), 34: (6, 23), 35: (6, 23),
}
# Face opening under the hood.
FACE = {11: (16, 18), 12: (15, 19), 13: (14, 19), 14: (14, 19), 15: (14, 19), 16: (15, 19), 17: (16, 18)}
# Dissolving tail, y: (left, right) before sway.
TAIL = {36: (8, 21), 37: (9, 20), 38: (10, 19), 39: (11, 18), 40: (12, 17), 41: (13, 16), 42: (13, 15), 43: (14, 14)}
IDLE_BOB = [0, 0, -1, -1, -2, -2, -1, -1]
TALK_BOB = [0, -1, -1, -1, 0, -1, -1, -1]


def robe_color(x, y, lx, rx):
	t = (x - lx) / float(max(1, rx - lx))
	if y <= 17:  # hood: lit from the staff light behind the left shoulder
		return SPIRIT[4] if t < 0.22 else SPIRIT[3] if t < 0.62 else SPIRIT[2]
	color = SPIRIT[4] if t < 0.14 else SPIRIT[3] if t < 0.58 else SPIRIT[2]
	if x in (12, 16) and 21 <= y <= 34 and color is not SPIRIT[4]:
		color = SPIRIT[2]  # two long folds
	if y >= 32 and color is SPIRIT[3]:
		color = SPIRIT[2]  # the hem darkens before it dissolves
	return color


def body(frame, talk):
	"""Opaque, outlined part of the figure (hood, beard, robe, sleeves, staff hand)."""
	c = Canvas(W, H)
	for y, (lx, rx) in ROBE.items():
		for x in range(lx, rx + 1):
			c.put(x, y, robe_color(x, y, lx, rx))
	# Hood rim and shoulder mantle catch the light.
	for x, y in ((13, 7), (14, 7), (12, 8), (13, 8), (14, 8), (15, 8)):
		c.put(x, y, SPIRIT[5] if x < 14 else SPIRIT[4])
	for y in range(9, 17):
		c.put(ROBE[y][0], y, SPIRIT[4])
	for x in range(10, 21):
		c.put(x, 18, SPIRIT[2] if x > 16 else SPIRIT[3])
	# Face in shadow, glowing eyes.
	for y, (lx, rx) in FACE.items():
		for x in range(lx, rx + 1):
			c.put(x, y, VOID)
	bright = talk or frame not in (5,)
	c.put(16, 14, EYE if bright else EYE_DIM)
	c.put(18, 14, EYE if bright else EYE_DIM)
	if talk and frame % 4 in (1, 2):
		c.put(18, 13, EYE_DIM)  # a slight widening while speaking
	# Long pale beard falling over the robe; it sways while speaking.
	sway = [0, 0, 1, 1, 0, 0, -1, -1][frame] if talk else [0, 0, 0, 1, 1, 1, 0, 0][frame]
	for y in range(16, 29):
		k = y - 16
		half = 2.4 - k * 0.12
		cx = 17.0 + (sway * k / 12.0 if k > 4 else 0.0)
		for x in range(int(math.floor(cx - half)), int(math.ceil(cx + half)) + 1):
			if abs(x + 0.5 - cx) > half + 0.5:
				continue
			color = SPIRIT[5] if abs(x + 0.5 - cx) < half * 0.55 else SPIRIT[4]
			if y > 19 and abs(x + 0.5 - cx) > 0.6 and (x + y // 3) % 3 == 0:
				color = SPIRIT[3]  # strands
			c.put(x, y, color)
	for x in range(15, 20):
		c.put(x, 16, SPIRIT[4])  # moustache under the eyes
	# Back sleeve gripping the staff, left side.
	for y in range(22, 27):
		for x in range(5, 9):
			if (x, y) in ((5, 22), (5, 26)):
				continue
			c.put(x, y, SPIRIT[3] if y < 24 else SPIRIT[2])
	c.put(6, 24, SPIRIT[5])  # knuckles on the staff
	c.put(7, 24, SPIRIT[4])
	# Front sleeve: hanging at rest, raised toward the listener in dialogue.
	if talk:
		lift = [0, 1, 1, 0, 0, 1, 1, 0][frame]
		for y in range(20, 24):
			for x in range(19, 24):
				if x - 19 > (y - 19) * 2:
					continue
				c.put(x, y - lift, SPIRIT[3] if y < 22 else SPIRIT[2])
		for x, y in ((24, 18), (25, 18), (24, 19), (25, 19), (26, 19), (24, 20), (25, 20)):
			c.put(x, y - lift, SPIRIT[5] if y < 20 else SPIRIT[4])  # open palm turned to the listener
	else:
		for y in range(21, 30):
			w = 3 if y < 27 else 4
			for x in range(20, 20 + w):
				c.put(x, y, SPIRIT[2] if x > 20 else SPIRIT[3])
		for x in range(20, 24):
			c.put(x, 29, SPIRIT[1])  # cuff shadow
	return c


def staff(c, frame, talk):
	"""Spectral staff in the back hand: shaft fading out below the robe, light at the crook."""
	for y in range(11, 46):
		if y > 35 and (y + frame) % 2 == 0 and y > 39:
			continue
		alpha = 255 if y <= 36 else max(70, 255 - (y - 36) * 22)
		c.put(6, y, SPIRIT[3][:3] + (alpha,) if y < 24 else SPIRIT[2][:3] + (alpha,))
		if y <= 36:
			c.put(7, y, SPIRIT[1] if y > 26 else SPIRIT[2])
	# Crook curling toward the head, with the light it holds.
	for x, y in ((6, 10), (6, 9), (7, 8), (8, 8), (9, 9), (9, 10)):
		c.put(x, y, SPIRIT[4])
	core = (talk and frame % 2 == 0) or (not talk and frame in (2, 3, 4))
	c.put(7, 9, (255, 255, 240, 255) if core else EYE)
	c.put(8, 9, EYE)
	c.put(7, 10, EYE_DIM)
	c.put(8, 10, EYE_DIM if core else SPIRIT[5])
	if talk:
		ring = [(5, 8), (10, 10), (7, 6), (4, 10), (10, 7), (5, 12)]
		for i, (x, y) in enumerate(ring):
			if (i + frame) % 3 == 0:
				c.put(x, y, SPIRIT[5][:3] + (200,))


def tail(c, frame):
	"""Robe dissolving into a swaying, semi-transparent tail (no outline: it fades into the night)."""
	for y, (lx, rx) in TAIL.items():
		k = y - 35
		shift = int(round(math.sin(frame / FRAMES * math.tau + k * 0.7) * min(1.5, k * 0.35) - k * 0.35))
		alpha = max(90, 235 - k * 20)
		for x in range(lx + shift, rx + shift + 1):
			if k >= 4 and (x + y + frame) % 2:
				continue  # dither the last wisps
			t = (x - lx - shift) / float(max(1, rx - lx))
			base = SPIRIT[3] if t < 0.3 else SPIRIT[2]
			c.put(x, y, base[:3] + (alpha,))


def motes(c, frame, talk):
	"""Three motes rising around the figure, looping over the 8 frames."""
	for i, (x0, phase) in enumerate(((11, 0), (19, 5), (15, 10))):
		rise = (frame * 2 + phase) % 16
		y = 44 - rise
		x = x0 + int(round(math.sin((frame + i * 3) / FRAMES * math.tau)))
		alpha = max(60, 230 - rise * 12)
		color = SPIRIT[5] if (talk or i != 2) else SPIRIT[4]
		if c.get(x, y) is None:
			c.put(x, y, color[:3] + (alpha,))


def frame(index, talk):
	f = Canvas(W, H)
	fig = Canvas(W, H)
	staff(fig, index, talk)
	fig.blit(outline(body(index, talk), OUTLINE), 0, 0)
	tail(fig, index)
	motes(fig, index, talk)
	bob = (TALK_BOB if talk else IDLE_BOB)[index]
	f.blit(fig, 0, bob)
	return f


def aura():
	"""Alpha-only cool halo; the script modulates it (stronger while the spirit speaks)."""
	c = Canvas(48, 56)
	cx, cy = 23.5, 25.0
	for y in range(56):
		for x in range(48):
			d = math.hypot((x - cx) / 21.0, (y - cy) / 27.0)
			if d >= 1.0:
				continue
			a = (1.0 - d) ** 1.6
			# Ordered dither between two alpha steps keeps hard pixel edges.
			level = a * 4.0
			step = int(level)
			if (level - step) > (((x % 2) * 2 + (y % 2)) + 0.5) / 4.0:
				step += 1
			if step <= 0:
				continue
			c.put(x, y, SPIRIT[4][:3] + (min(4, step) * 22,))
	return c


def portrait():
	c = Canvas(24, 24)
	# Backdrop: night blue with the staff light glowing at the upper left.
	for y in range(24):
		for x in range(24):
			glow = max(0.0, 1.0 - math.hypot(x - 2, y - 3) / 13.0)
			color = SKY[1] if y > 15 else SKY[2]
			if glow > 0.55:
				color = SPIRIT[1]
			elif glow > 0.3:
				color = SKY[3]
			c.put(x, y, color)
	# Hood: tall rounded mass falling onto the shoulders.
	hood = {}
	for y in range(1, 24):
		if y <= 9:
			half = 1.5 + math.sqrt(max(0.0, 1.0 - ((9 - y) / 8.6) ** 2)) * 5.6
		else:
			half = 7.1 + (y - 9) * 0.2
		hood[y] = (int(round(11.5 - half)), int(round(11.5 + half)))
	for y, (lx, rx) in hood.items():
		for x in range(max(0, lx), min(23, rx) + 1):
			t = (x - lx) / float(rx - lx)
			color = SPIRIT[4] if t < 0.2 else SPIRIT[3] if t < 0.55 else SPIRIT[2] if t < 0.88 else SPIRIT[1]
			if y <= 2 and color is SPIRIT[3]:
				color = SPIRIT[4]
			c.put(x, y, color)
	# Face opening in deep shadow.
	face = {6: (9, 14), 7: (8, 15), 8: (7, 16), 9: (7, 16), 10: (7, 16), 11: (7, 16), 12: (7, 16), 13: (8, 15), 14: (8, 15)}
	for y, (lx, rx) in face.items():
		for x in range(lx, rx + 1):
			c.put(x, y, VOID)
	for x in range(8, 16):
		c.put(x, 8, SPIRIT[0])  # brow under the hood edge
	for x, y in ((9, 10), (10, 10), (13, 10), (14, 10)):
		c.put(x, y, EYE)
	c.put(9, 11, EYE_DIM)
	c.put(14, 11, EYE_DIM)
	c.put(11, 12, SPIRIT[0])
	c.put(12, 12, SPIRIT[0])
	# Moustache and beard, pale and long.
	for x in range(8, 16):
		c.put(x, 13, SPIRIT[4] if x in (8, 15) else SPIRIT[5])
	for y in range(14, 24):
		half = 3.2 + (y - 14) * 0.28
		for x in range(int(round(11.5 - half)), int(round(11.5 + half)) + 1):
			d = abs(x - 11.5)
			color = SPIRIT[5] if d < half * 0.5 else SPIRIT[4]
			if x in (10, 13) and y > 15:
				color = SPIRIT[3]  # two long strands
			c.put(x, y, color)
	for x in (10, 13):
		c.put(x, 14, SPIRIT[3])  # parting under the moustache
	# Outline the hood mass against the backdrop.
	out = c.copy()
	figure = set(SPIRIT) | {VOID, EYE, EYE_DIM}
	for y in range(24):
		for x in range(24):
			if c.get(x, y) in figure:
				continue
			if any(c.get(x + dx, y + dy) in figure for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
				out.put(x, y, OUTLINE)
	return out


# 4x4 ordered dither, normalised to [0, 1): shared by the reveal / dissolve thresholds.
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def bayer(x, y):
	return (BAYER[y % 4][x % 4] + 0.5) / 16.0


def figure_pixels(c):
	"""Opaque or translucent pixels of a frame with their bottom-up height in [0, 1]."""
	pts = [(x, y) for y in range(H) for x in range(W) if c.get(x, y) is not None]
	y0 = min(y for _, y in pts)
	y1 = max(y for _, y in pts)
	return [(x, y, (y1 - y) / float(y1 - y0)) for x, y in pts]


def ghost(c, x, y):
	"""Flat pale version of a pixel: the spirit before it takes form. Edges one step darker."""
	edge = any(c.get(x + dx, y + dy) is None for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
	alpha = c.get(x, y)[3]
	return (SPIRIT[4] if edge else SPIRIT[5])[:3] + (min(alpha, 235),)


def threshold(x, y, h):
	return 0.55 * h + 0.45 * bayer(x, y)


def appear_frame(stage):
	"""Stages 0-7: nothing, nothing (the light column gathers), silhouette 30 %, 65 %, 100 % pale,
	half coloured, coloured with a pale rim, idle frame 0."""
	base = frame(0, False)
	if stage == 7:
		return base
	out = Canvas(W, H)
	if stage < 2:
		return out
	cover = {2: 0.3, 3: 0.65}.get(stage, 1.01)
	for x, y, h in figure_pixels(base):
		if threshold(x, y, h) >= cover:
			continue
		color = ghost(base, x, y)
		if stage == 5 and bayer(x, y) < 0.5:
			color = base.get(x, y)
		elif stage == 6:
			color = base.get(x, y) if base.get(x, y) != OUTLINE else SPIRIT[3]
		out.put(x, y, color)
	return out


def disappear_frame(stage):
	"""Stages 0-7: idle frame 0, half pale, pale silhouette, then it erodes from the hem upward while
	the lost pixels rise as motes; last frame empty."""
	base = frame(0, False)
	if stage == 0:
		return base
	out = Canvas(W, H)
	if stage == 7:
		return out
	erode = {3: 0.25, 4: 0.5, 5: 0.75, 6: 1.01}.get(stage, 0.0)
	for x, y, h in figure_pixels(base):
		t = threshold(x, y, h)
		if t < erode:
			# A few of the lost pixels drift up and fade: the spirit leaves as light, not as a cut.
			if bayer(x, y) < 0.13:
				lift = int((erode - t) * 18) + 2
				sway = int(round(math.sin(y * 0.7 + stage) * 1.2))
				out.put(x + sway, y - lift, SPIRIT[5][:3] + (max(70, 220 - lift * 9),))
			continue
		color = ghost(base, x, y)
		if stage == 1 and bayer(x, y) < 0.5:
			color = base.get(x, y)
		out.put(x, y, color)
	return out


MW, MH = 48, 64  # manifest cell: the spirit cell (32x48) sits at (8, 12), ground on the bottom row - 4
MCX, MGROUND = 24, 59  # column centre and ground row inside the cell


def light_column(c, height, half, alpha, phase=0):
	"""Dithered vertical light from the ground up; brighter core, softer edges and top."""
	for y in range(MGROUND - height, MGROUND + 1):
		k = (MGROUND - y) / float(max(1, height))
		for x in range(MCX - half - 1, MCX + half + 1):
			d = abs(x + 0.5 - MCX) / float(half + 0.5)
			if d > 1.0:
				continue
			a = alpha * (1.0 - d * 0.6) * (1.0 - k ** 3)
			if d > 0.5 and bayer(x, y + phase) > 0.5:
				continue
			if k > 0.75 and bayer(x, y + phase) > 1.0 - k:
				continue
			color = (255, 255, 240) if d < 0.25 and k < 0.8 else SPIRIT[5] if d < 0.6 else SPIRIT[4]
			c.put(x, y, color[:3] + (int(max(30, a)),))


def ground_ring(c, radius, alpha):
	for x in range(MCX - radius - 1, MCX + radius + 2):
		dx = (x + 0.5 - MCX) / float(radius)
		if abs(dx) > 1.0:
			continue
		dy = int(round(math.sqrt(1.0 - dx * dx) * 1.5))
		for y in (MGROUND - dy, MGROUND + 1 - (1 if dy else 0)):
			if bayer(x, y) < 0.75:
				c.put(x, y, SPIRIT[4][:3] + (alpha,))


def motes_at(c, points, alpha):
	for i, (x, y) in enumerate(points):
		c.put(int(round(x)), int(round(y)), (SPIRIT[5] if i % 2 else (255, 255, 240, 255))[:3] + (alpha,))


def manifest_appear(stage):
	c = Canvas(MW, MH)
	# Motes drawn in from both sides toward the column, then thrown out when the figure forms.
	seeds = [(-1, 6, 0.0), (1, 14, 0.8), (-1, 22, 1.6), (1, 30, 2.4), (-1, 38, 0.4), (1, 46, 1.2)]
	if stage <= 3:
		pull = stage / 3.0
		pts = [(MCX + side * (20 - 17 * pull) + math.sin(ph + stage) * 1.5, MGROUND - h * (0.4 + 0.6 * pull)) for side, h, ph in seeds]
		motes_at(c, pts, 150 + 30 * stage)
	elif stage <= 6:
		push = (stage - 3) / 3.0
		pts = [(MCX + side * (4 + 16 * push), MGROUND - h - push * 8) for side, h, _ in seeds[::2 if stage == 6 else 1]]
		motes_at(c, pts, int(200 - 110 * push))
	if stage == 0:
		for x, y, a in ((MCX - 1, MGROUND, 200), (MCX, MGROUND, 255), (MCX, MGROUND - 1, 160), (MCX + 1, MGROUND, 200)):
			c.put(x, y, SPIRIT[5][:3] + (a,))
	column = {1: (20, 0, 120), 2: (38, 1, 140), 3: (46, 2, 150), 4: (46, 2, 120), 5: (44, 1, 70), 6: (40, 1, 35)}
	if stage in column:
		light_column(c, *column[stage], phase=stage)
	if stage in (3, 4, 5):
		ground_ring(c, {3: 6, 4: 9, 5: 12}[stage], {3: 190, 4: 150, 5: 80}[stage])
	return c


def manifest_disappear(stage):
	c = Canvas(MW, MH)
	column = {1: (44, 1, 50), 2: (46, 2, 100), 3: (46, 2, 110), 4: (46, 1, 85), 5: (44, 1, 50), 6: (40, 0, 25)}
	if stage in column:
		light_column(c, *column[stage], phase=stage)
	if 2 <= stage <= 7:
		rise = (stage - 2) / 5.0
		pts = [(MCX + dx + math.sin(rise * 4 + i) * 1.5, 40 - rise * 34 + dy) for i, (dx, dy) in enumerate(((-6, 6), (5, 2), (-3, -4), (7, -8), (-8, -12), (2, -16)))]
		motes_at(c, [p for p in pts if p[1] >= 1], int(210 - 150 * rise))
	if stage == 2:
		ground_ring(c, 8, 110)
	return c


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	outputs = {
		"npc_spirit_idle.png": sheet([frame(i, False) for i in range(FRAMES)], FRAMES),
		"npc_spirit_talk.png": sheet([frame(i, True) for i in range(FRAMES)], FRAMES),
		"ui_portrait_spirit.png": portrait(),
		"vfx_spirit_aura.png": aura(),
		"npc_spirit_appear.png": sheet([appear_frame(i) for i in range(FRAMES)], FRAMES),
		"npc_spirit_disappear.png": sheet([disappear_frame(i) for i in range(FRAMES)], FRAMES),
		"vfx_spirit_manifest.png": sheet([manifest_appear(i) for i in range(FRAMES)] + [manifest_disappear(i) for i in range(FRAMES)], FRAMES),
	}
	for name, canvas in outputs.items():
		save_png(canvas, os.path.join(OUT, name))
		print(name, canvas.w, canvas.h)
		if preview:
			save_png(canvas, os.path.join(preview, name[:-4] + "_x8.png"), 8, BG)


if __name__ == "__main__":
	main()

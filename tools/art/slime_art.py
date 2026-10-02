"""Slime sprites (RUN-029 second pass): jelly shading, wobble, hit and death frames.

Frames are 24x24, the slime faces LEFT, ground contact on row 23 (1 px outline
below the body), body centred on column 12. Light comes from the upper left.

Sheet layout (one row, 24 px per frame):
  0..7   patrol cycle (loop)           animation "green" / "purple"
  8..9   hit recoil (loop, 2 frames)   animation "*_hit"
  10..13 death collapse (no loop)      animation "*_death"
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, outline, sheet  # noqa: E402
from palette import BLOOD, CORRUPT, OUTLINE, SLIME_GREEN  # noqa: E402

PINK_WHITE = (255, 222, 232, 255)
BONE_WHITE = (238, 250, 214, 255)

# (width, height, top lean, centre shift, wobble phase)
PATROL = [
	(16, 11, 0.0, 0, 0.0),     # rest
	(18, 9, 0.7, 0, 0.9),      # anticipation squash, leans back
	(19, 8, 1.0, 0, 1.8),      # deepest squash
	(14, 14, -2.6, -1, 2.7),   # launch stretch, leans forward (left)
	(14, 13, -3.0, -1, 3.6),   # peak stretch
	(18, 9, -1.2, -1, 4.5),    # landing squash
	(17, 10, -0.3, 0, 5.4),    # settle
	(15, 12, 0.6, 0, 6.3),     # rebound
]
HIT = [
	(20, 8, 1.8, 1, 0.5),      # smashed flat, recoiling right
	(14, 13, 2.2, 1, 2.0),     # snapped upright
]


def cells_of(w, h, lean, shift, wob):
	cx = 12.0 + shift
	bottom = 22
	cells = {}
	for r in range(h):
		t = (r + 0.5) / h
		hw = (w / 2.0) * (1.0 - t ** 2.2) ** (1.0 / 2.2)
		if r == 0:
			hw += 0.4
		elif r == 1:
			hw += 0.15
		if r == h - 1:
			hw -= 0.7
		hw += 0.45 * math.sin(wob + r * 0.85) * min(1.0, r / 2.0)
		hw = max(hw, 0.9)
		off = lean * (r / float(max(1, h - 1))) ** 1.5
		y = bottom - r
		for x in range(24):
			dx = x + 0.5 - (cx + off)
			if abs(dx) <= hw:
				ex = dx / (w / 2.0 + 0.001)
				cells[(x, y)] = (ex, t, r)
	return cells


def shade(cells, ramp):
	body = Canvas(24, 24)
	for (x, y), (ex, t, r) in cells.items():
		ex_c = max(-0.98, min(0.98, ex))
		z2 = 1.0 - ex_c * ex_c - min(0.98, t) ** 2
		z = math.sqrt(max(0.04, z2))
		norm = math.sqrt(ex_c * ex_c + t * t + z * z)
		d = (-0.55 * ex_c + 0.55 * t + 0.63 * z) / norm
		if d > 0.64:
			tone = 3
		elif d > 0.30:
			tone = 2
		else:
			tone = 1
		# translucent belly: light bleeds back in at the lowest rows
		if r == 0:
			tone = 2 if tone < 2 else tone
		body.put(x, y, ramp[tone])
	# edge definition: lit rim up-left, dark inner edge down-right
	for (x, y), (ex, t, r) in cells.items():
		up = (x, y - 1) not in cells
		left = (x - 1, y) not in cells
		down = (x, y + 1) not in cells
		right = (x + 1, y) not in cells
		if (down and r > 0) or (right and r > 0):
			body.put(x, y, ramp[1] if ex > -0.2 or down else ramp[2])
		if up or left:
			body.put(x, y, ramp[3] if (ex < 0.2) else ramp[2])
	return body


def specular(body, cells, ramp, h):
	top = min(y for (x, y) in cells)
	row = [x for (x, y) in cells if y == top + 2]
	if not row:
		return
	x0 = min(row)
	for dx, dy, tone in ((1, 0, 4), (2, 0, 4), (0, 1, 4), (0, 2, 3), (-1, 1, 3)) if h >= 11 else ((1, 0, 4), (2, 0, 3), (0, 1, 3)):
		p = (x0 + 1 + dx, top + 2 + dy)
		if p in cells:
			body.put(p[0], p[1], ramp[tone])
	# secondary dot on the lower right
	right = max(x for (x, y) in cells if y == top + h - 3) if h >= 10 else None
	if right is not None:
		p = (right - 2, top + h - 3)
		if p in cells:
			body.put(p[0], p[1], ramp[3])


def bubbles(body, cells, ramp, phase, count):
	"""Small bubbles drifting upward inside the jelly."""
	ys = [y for (x, y) in cells]
	top, bot = min(ys), max(ys)
	for k in range(count):
		bx = 12 + int(round(math.sin(k * 2.4 + 1.0) * 3.2))
		prog = ((phase / 8.0) + k * 0.37) % 1.0
		by = int(round(bot - 1 - prog * (bot - top - 3)))
		if (bx, by) in cells and (bx, by - 1) in cells:
			body.put(bx, by, ramp[3])
			body.put(bx, by - 1, ramp[4]) if prog < 0.7 else None


def eyes(body, cells, w, h, lean, shift, tough, mode):
	cx = 12.0 + shift
	bottom = 22
	ey = bottom - int(round(h * 0.52))
	off = lean * (0.52) ** 1.5
	ex0 = int(round(cx + off - w * 0.30)) - 1
	gap = 5 if w >= 16 else 4
	sclera = PINK_WHITE if tough else BONE_WHITE
	iris = BLOOD[3] if tough else OUTLINE
	for k, ex in enumerate((ex0, ex0 + gap)):
		if mode == "squint":
			for dx in range(3):
				body.put(ex + dx, ey, OUTLINE)
			continue
		if mode == "dead":
			for dx, dy in ((0, -1), (2, -1), (1, 0), (0, 1), (2, 1)):
				body.put(ex + dx, ey + dy, OUTLINE)
			continue
		for dx in range(3):
			for dy in range(3):
				if dx == 2 and dy == 2:
					continue
				body.put(ex + dx, ey + dy - 1, sclera)
		body.put(ex, ey, iris)
		body.put(ex, ey - 1, iris)
		for dx in range(3):
			body.put(ex + dx, ey - 2, OUTLINE)
		body.put(ex + (2 if k == 0 else 0), ey - 1, OUTLINE)


def mouth(body, cells, w, h, lean, shift, mode):
	if mode not in ("hit", "dead"):
		return
	cx = 12.0 + shift
	bottom = 22
	my = bottom - int(round(h * 0.2))
	mx = int(round(cx + lean * 0.2)) - 2
	for dx in range(5):
		if (mx + dx, my) in cells:
			body.put(mx + dx, my, OUTLINE)
	for dx in (1, 2, 3):
		if (mx + dx, my + 1) in cells:
			body.put(mx + dx, my + 1, OUTLINE)


def purple_extras(body, cells, ramp, phase, h, lean, shift):
	"""Corrupt crystals on the crown and a pulsing core."""
	top = min(y for (x, y) in cells)
	cxp = 12 + shift + int(round(lean * 0.6))
	# three shards sprouting from the dome
	for sx, sh in ((-3, 2), (2, 3)):
		base = [(x, y) for (x, y) in cells if y == top + 1 and abs(x - (cxp + sx)) <= 0]
		bx = cxp + sx
		for k in range(sh):
			y = top + 1 - k
			if y < 0:
				break
			body.put(bx, y, CORRUPT[4] if k == sh - 1 else CORRUPT[3])
			if k == 0:
				body.put(bx + 1, y, CORRUPT[1])
				body.put(bx - 1, y, CORRUPT[2])
	# glowing core below the shoulder
	cyp = 22 - max(2, h // 3) - 0
	cxc = cxp + 2
	pulse = int(round(0.5 + 0.5 * math.sin(phase * 1.0)))
	pts = [(dx, dy, CORRUPT[4]) for dx in (0, 1) for dy in (0, 1)] + [(dx, dy, CORRUPT[3]) for dx, dy in ((-1, 0), (2, 0), (0, -1), (1, -1), (0, 2), (1, 2), (-1, 1), (2, 1))]
	if pulse:
		pts += [(dx, dy, CORRUPT[2]) for dx, dy in ((-2, 0), (3, 0), (0, -2), (1, -2), (-2, 1), (3, 1))]
	for dx, dy, c in pts:
		if (cxc + dx, cyp + dy) in cells:
			body.put(cxc + dx, cyp + dy, c)
	# shard motes rising around it
	mote = int(phase) % 3
	mx, my = cxp - 4 + mote * 3, top - 1 - (1 if mote == 1 else 0)
	if my >= 0 and (mx, my + 3) in cells:
		body.put(mx, my, CORRUPT[3])


def frame(ramp, tough, params, index=0, mode="normal"):
	w, h, lean, shift, wob = params
	cells = cells_of(w, h, lean, shift, wob)
	body = shade(cells, ramp)
	specular(body, cells, ramp, h)
	bubbles(body, cells, ramp, index, 2 if h >= 10 else 1)
	if tough:
		purple_extras(body, cells, ramp, index, h, lean, shift)
	eyes(body, cells, w, h, lean, shift, tough, "squint" if mode == "hit" else mode)
	mouth(body, cells, w, h, lean, shift, mode)
	return outline(body, OUTLINE)


# ------------------------------------------------------------ death frames
def puddle(ramp, hw, hh, wob, drops=(), tough=False):
	c = Canvas(24, 24)
	bottom = 22
	cx = 11.5
	for r in range(hh):
		t = (r + 0.5) / hh
		half = hw * (1.0 - t ** 2.0) ** 0.5
		half += 0.5 * math.sin(wob + r)
		for x in range(24):
			if abs(x + 0.5 - cx) <= half:
				tone = 2 if r == hh - 1 else 3 if (x < cx - half * 0.35 and r > 0) else 2 if r > 0 else 1
				c.put(x, bottom - r, ramp[tone])
	# lit left edge, dark right edge
	xs = [x for x in range(24) if c.get(x, bottom) is not None]
	if xs:
		c.put(xs[0], bottom, ramp[1])
		c.put(xs[-1], bottom, ramp[1])
		if hh > 1:
			c.put(xs[0] + 2, bottom - hh + 1 if c.get(xs[0] + 2, bottom - hh + 1) else bottom, ramp[4])
			c.put(xs[0] + 3, bottom - hh + 1 if c.get(xs[0] + 3, bottom - hh + 1) else bottom, ramp[4])
	for (dx, dy, sz) in drops:
		for ox in range(sz):
			for oy in range(sz):
				c.put(int(11 + dx) + ox, int(bottom - dy) + oy, ramp[4] if (ox, oy) == (0, 0) else ramp[3] if oy == 0 else ramp[2])
	return outline(c, OUTLINE)


def death_frames(ramp, tough):
	f0 = frame(ramp, tough, (20, 13, 0.0, 0, 0.3), 0, "dead")
	# crack of light through the bloated body
	for (x, y) in ((11, 11), (12, 12), (11, 13), (12, 14), (11, 15)):
		if f0.get(x, y) is not None:
			f0.put(x, y, ramp[4])
	f1 = puddle(ramp, 11.0, 6, 0.6, drops=((-8, 9, 2), (-5, 11, 2), (4, 11, 2), (7, 8, 2), (0, 12, 1), (-2, 8, 1)), tough=tough)
	f2 = puddle(ramp, 11.0, 3, 1.2, drops=((-6, 6, 1), (6, 5, 1)), tough=tough)
	f3 = puddle(ramp, 9.0, 2, 2.0)
	return [f0, f1, f2, f3]


def slime_sheet(ramp, tough):
	frames = [frame(ramp, tough, p, i) for i, p in enumerate(PATROL)]
	frames += [frame(ramp, tough, p, i, "hit") for i, p in enumerate(HIT)]
	frames += death_frames(ramp, tough)
	return sheet(frames, len(frames))


def preview_sheets():
	return {"green": slime_sheet(SLIME_GREEN, False), "purple": slime_sheet(CORRUPT, True)}

"""Generate hazard and prop sprites: iron spikes, corrupt thorns, ferry raft, gold gate.

Usage: python3 tools/art/hazards.py [--preview DIR]

RUN-013. Shapes follow the code-drawn originals so gameplay is unchanged.
  trap_spikes.png     32x14  origin (16,14) bottom-centre, drawn pointing up
  trap_thorns.png     32x16  origin (16,16) bottom-centre
  prop_ferry.png      36x10  origin (18,3); walkable top = rows 0..1
  prop_gold_gate.png  88x112 frame 0..56 (origin (28,112)), closed panel with
                      medallion x56..72 (rows 12..112), open panel without
                      medallion x72..88 (rows 12..112)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, hexc, line, save_png, sheet  # noqa: E402
from palette import OUTLINE, STEEL, STONE_COOL, MOSS, WOOD, GOLD, BLOOD, CORRUPT, SKY, EMBER  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
PREVIEW_BG = (52, 60, 66, 255)


def hsh(x, y, s=0):
	n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
	n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
	return (n ^ (n >> 16)) & 0xFFFF


def edge_outline(c, color=OUTLINE):
	"""Turn opaque pixels touching transparency (or the canvas edge) into outline."""
	marks = []
	for y in range(c.h):
		for x in range(c.w):
			if c.get(x, y) is None:
				continue
			for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
				nx, ny = x + dx, y + dy
				if not (0 <= nx < c.w and 0 <= ny < c.h) or c.get(nx, ny) is None:
					marks.append((x, y))
					break
	for x, y in marks:
		c.px[y * c.w + x] = color


def halo(c, color=OUTLINE):
	"""Outline drawn on transparent pixels around the shape (inside canvas)."""
	out = c.copy()
	for y in range(c.h):
		for x in range(c.w):
			if c.get(x, y) is None and any(c.get(x + dx, y + dy) is not None for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
				out.put(x, y, color)
	return out


# ------------------------------------------------------------------ spikes
RUST = [hexc("3a2218"), hexc("5a3422"), hexc("7a4a2c")]
SPIKE_HALF = (0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3)
SPIKE_CENTRES = (4, 12, 20, 28)


def spikes_base():
	c = Canvas(32, 14)
	for cx in SPIKE_CENTRES:
		for r in range(11):
			hw = SPIKE_HALF[r]
			depth = r / 10.0
			for x in range(cx - hw, cx + hw + 1):
				rel = x - cx
				if hw == 0:
					tone = STEEL[4]
				elif rel < 0:
					tone = STEEL[4] if rel == -hw and hw > 1 and r > 5 else STEEL[3]
				elif rel == 0:
					tone = STEEL[4] if r < 8 else STEEL[3]
				elif rel == hw:
					tone = STEEL[0] if r > 3 else STEEL[1]
				else:
					tone = STEEL[2] if depth < 0.7 else STEEL[1]
				c.put(x, r, tone)
		# darker steel towards the root, a scratch and a pitted rust spot
		for r in (8, 9, 10):
			c.put(cx + 1, r, STEEL[1])
		c.put(cx - 1, 7, STEEL[2])
		c.put(cx, 9, RUST[1] if cx in (12, 28) else STEEL[2])
		c.put(cx + 1, 10, RUST[0] if cx in (12, 28) else STEEL[0])
		# blood on the tips, a dried run down the right face and drips on the plate
		for r in range(0, 4):
			hw = (0, 0, 0, 1)[r]
			for x in range(cx - hw, cx + hw + 1):
				c.put(x, r, BLOOD[4] if (r == 0) else BLOOD[3] if x <= cx else BLOOD[2])
		c.put(cx + 1, 4, BLOOD[2])
		c.put(cx + 1, 5, BLOOD[1])
		c.put(cx + 2, 6, BLOOD[1])
		c.put(cx + 2, 7, BLOOD[0])
	body = c.copy()
	for y in range(11):
		for x in range(32):
			if body.get(x, y) is None and any(body.get(x + dx, y + dy) is not None for dx, dy in ((1, 0), (-1, 0), (0, -1))):
				c.put(x, y, OUTLINE)
	# base plate rows 11..13: bevelled iron with rivets
	for x in range(32):
		c.put(x, 11, STEEL[3] if x % 8 else OUTLINE)
		c.put(x, 12, STEEL[2])
		c.put(x, 13, STEEL[0])
	for x in (0, 8, 16, 24):
		c.put(x, 12, OUTLINE)
	for x in (3, 11, 19, 27):  # rivets with a lit pixel
		c.put(x, 12, STEEL[4])
		c.put(x + 1, 12, STEEL[1])
	for x in range(32):
		if hsh(x, 13, 3) % 5 == 0:
			c.put(x, 13, STEEL[1])
	for x in (5, 6, 20, 21, 7):
		c.put(x, 11, BLOOD[1])
	for x in (5, 6, 20):
		c.put(x, 12, BLOOD[0])
	for x in (13, 14, 29):
		c.put(x, 11, RUST[1])
	for (x, y) in ((0, 11), (31, 11), (31, 12), (31, 13), (0, 13), (0, 12)):
		c.put(x, y, OUTLINE)
	return c


def spikes():
	"""6 frames: a cold glint sweeps over the tips so the trap catches the eye."""
	frames = []
	for f in range(6):
		c = spikes_base().copy()
		if f >= 1:
			for i, cx in enumerate(SPIKE_CENTRES):
				r = (f * 2 + i * 3) % 11 if f < 5 else None
				if f in (1, 2, 3, 4):
					r = 1 + (f - 1) * 2 + (i % 2)
					hw = SPIKE_HALF[min(r, 10)]
					if r <= 9 and c.get(cx - hw, r) is not None and c.get(cx - hw, r) not in (OUTLINE,):
						c.put(cx - hw if hw else cx, r, WHITE)
				if f == 3 and i in (0, 2):
					c.put(cx, 0, WHITE)
					c.put(cx - 1, 0, STEEL[4]) if c.get(cx - 1, 0) is not None else None
		frames.append(c)
	return frames


WHITE = (255, 255, 255, 255)


# ------------------------------------------------------------------ thorns
THORN_VINES = [
	[(0, 13), (3, 11), (6, 12), (9, 9), (12, 10), (15, 7), (18, 9), (21, 6), (24, 8), (27, 5), (31, 7)],
	[(2, 15), (4, 10), (3, 7), (6, 5), (9, 6), (11, 3)],
	[(13, 15), (15, 11), (14, 8), (17, 4), (20, 3)],
	[(21, 15), (23, 11), (27, 12), (31, 10)],
	[(27, 15), (28, 10), (26, 6), (29, 2)],
]
THORN_SPIKES = (
	(3, 11, -1, -1, 3), (9, 9, 0, -1, 4), (15, 7, 0, -1, 4), (21, 6, 0, -1, 4), (27, 5, 1, -1, 3),
	(4, 8, -1, 0, 3), (6, 5, 0, -1, 3), (11, 3, 0, -1, 2), (17, 4, -1, -1, 3), (14, 9, -1, 0, 3),
	(23, 11, 0, -1, 3), (28, 10, 1, 0, 3), (26, 6, -1, 0, 3), (29, 2, 1, 0, 2), (12, 10, 1, 1, 2), (24, 8, 1, 1, 2),
)
BUDS = ((9, 8), (15, 6), (21, 5), (4, 9), (26, 7), (12, 12))


def thorns_frame(f):
	c = Canvas(32, 16)
	for pts in THORN_VINES:  # thick, shaded vines
		for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
			line(c, x0, y0 + 1, x1, y1 + 1, CORRUPT[1])
	for pts in THORN_VINES:
		for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
			line(c, x0, y0, x1, y1, CORRUPT[2])
	core = c.copy()
	for y in range(16):
		for x in range(32):
			if core.get(x, y) is None:
				continue
			if core.get(x, y - 1) is None:
				c.put(x, y, CORRUPT[3])
			if core.get(x - 1, y) is None and core.get(x, y - 1) is not None and (x + y) % 2:
				c.put(x, y, CORRUPT[3])
	sway = (0, 0, 1, 1)[f] if f < 4 else 0
	for i, (x, y, dx, dy, n) in enumerate(THORN_SPIKES):
		for k in range(1, n + 1):
			tipx = x + dx * k + (sway if (i % 2 == 0 and k == n and dy != 0) else 0)
			col = CORRUPT[4] if k > 1 else CORRUPT[3]
			c.put(tipx, y + dy * k, col)
		c.put(x, y, CORRUPT[3])
	# glowing buds pulse red/violet (danger colour kept clearly visible)
	for i, (x, y) in enumerate(BUDS):
		ph = (f + i) % 4
		c.put(x, y, BLOOD[4] if ph in (0, 1) else BLOOD[3])
		c.put(x + 1, y, BLOOD[3] if ph in (0, 1) else BLOOD[2])
		c.put(x, y + 1, BLOOD[2])
		if ph == 0:
			c.put(x - 1, y, CORRUPT[4])
			c.put(x, y - 1, CORRUPT[4])
	for x in range(0, 32):
		if c.get(x, 15) is None and hsh(x, 15) % 2:
			c.put(x, 15, CORRUPT[0])
	out = halo(c)
	# spores drifting up (frame dependent)
	for i, (sx, sy) in enumerate(((7, 4), (19, 2), (30, 5))):
		out.put(sx, (sy - f) % 6, CORRUPT[4] if i != 1 else BLOOD[4])
	return out


def thorns():
	return [thorns_frame(f) for f in range(4)]


# ------------------------------------------------------------------ ferry
def ferry_frame(f):
	c = Canvas(36, 16)
	# rows 0..5 = walkable slab (collision 34x6), x 1..34; outline sits at x 0 / 35
	plank_w = (8, 8, 9, 9)
	x = 1
	for pi, w in enumerate(plank_w):
		base = WOOD[2] if pi % 2 == 0 else WOOD[1]
		for xx in range(x, min(x + w, 35)):
			c.put(xx, 0, WOOD[4])
			c.put(xx, 1, WOOD[3])
			c.put(xx, 2, base)
			c.put(xx, 3, base)
			c.put(xx, 4, WOOD[1])
			c.put(xx, 5, WOOD[0])
			if hsh(xx, pi, 5) % 6 == 0:  # grain streaks
				c.put(xx, 2 + hsh(xx, 1) % 2, WOOD[3] if pi % 2 == 0 else WOOD[2])
		for y in range(1, 6):
			c.put(x + w - 1, y, WOOD[0])
		c.put(x + 1, 3, WOOD[3])
		x += w
	for nx in (3, 11, 20, 29):  # nail heads with highlight
		c.put(nx, 3, STEEL[4])
		c.put(nx + 1, 3, STEEL[1])
	for bx in (6, 27):  # riveted iron bands
		for y in range(0, 6):
			c.put(bx, y, STEEL[4] if y == 0 else STEEL[3] if y < 3 else STEEL[2])
			c.put(bx + 1, y, STEEL[3] if y == 0 else STEEL[2] if y < 3 else STEEL[1])
		c.put(bx, 2, STEEL[4])
	# hull: dark curved belly with plank lines, dripping slime-green moss
	for xx in range(0, 36):
		c.put(xx, 6, OUTLINE)
	for xx in range(2, 34):
		c.put(xx, 7, WOOD[0] if xx % 6 else OUTLINE)
	for xx in range(5, 31):
		c.put(xx, 8, WOOD[0] if xx % 5 else OUTLINE)
	for xx in range(9, 27):
		c.put(xx, 9, OUTLINE)
	for xx in (3, 4, 31, 32):
		c.put(xx, 8, OUTLINE)
	for xx in (12, 13, 20, 21):
		c.put(xx, 8, MOSS[1])
	c.put(13, 9, MOSS[0])
	# swaying ropes and a small lantern at the stern
	sway = (0, 1, 0, -1)[f]
	for rx in (7, 28):
		for y in range(6, 12):
			off = sway if y > 8 else 0
			c.put(rx + off, y, WOOD[4] if y % 2 else WOOD[3])
			c.put(rx + off - 1, y, OUTLINE)
			c.put(rx + off + 1, y, OUTLINE)
		c.put(rx + sway - 1, 12, OUTLINE); c.put(rx + sway, 12, OUTLINE); c.put(rx + sway + 1, 12, OUTLINE)
		c.put(rx + sway, 11, WOOD[2])
	# lantern: chain, iron cage, flickering flame
	lx = 17 + sway
	for y in range(6, 9):
		c.put(17, y, STEEL[2])
		c.put(16, y, OUTLINE); c.put(18, y, OUTLINE)
	for y in range(9, 14):
		for xx in range(lx - 2, lx + 3):
			edge = xx in (lx - 2, lx + 2) or y in (9, 13)
			c.put(xx, y, STEEL[1] if edge else EMBER[1 + (f % 2)] if y > 9 else STEEL[1])
	c.put(lx, 11, EMBER[3])
	c.put(lx, 12, EMBER[2])
	if f % 2:
		c.put(lx - 1, 11, EMBER[2])
	for xx in range(lx - 3, lx + 4):
		c.put(xx, 14, OUTLINE) if xx in (lx - 3, lx + 3) else None
	for y in range(0, 6):
		c.put(0, y, OUTLINE)
		c.put(35, y, OUTLINE)
	return c


def ferry():
	return [ferry_frame(f) for f in range(4)]


# ------------------------------------------------------------------ gold gate
SEAL = None


def stone_fill(c, x0, y0, x1, y1, seed, ramp=STONE_COOL, course=8):
	for y in range(y0, y1):
		row = (y - y0) // course
		by = (y - y0) % course
		bw = 10 + (hsh(row, seed) % 5)
		off = hsh(row, seed + 9) % bw
		for x in range(x0, x1):
			bx = (x - x0 + off) % bw
			blk = (x - x0 + off) // bw
			tone = 3 + ((hsh(blk, row, seed) % 3) - 1) * (1 if hsh(blk, row, seed + 1) % 2 else 0)
			if by == 0:
				tone += 1
			elif bx == 0:
				tone += 1
			if by == course - 1:
				tone = 1
			elif bx == bw - 1:
				tone = 1
			tone = max(0, min(5, tone))
			if hsh(x, y, seed + 2) % 17 == 0 and 0 < by < course - 1:
				tone = max(1, tone - 1)
			c.put(x, y, ramp[tone])


def moss_patch(c, x0, y0, x1, y1, seed, density=2):
	for y in range(y0, y1):
		for x in range(x0, x1):
			cur = c.get(x, y)
			if cur is None or cur == OUTLINE:
				continue
			d = (y - y0) / max(1, (y1 - y0))
			if hsh(x, y, seed) % 6 < density * (1.6 - d):
				c.put(x, y, MOSS[1 + (hsh(x, y, seed + 3) % 3)] if hsh(x, y, seed + 4) % 3 else MOSS[0])


def gate_frame():
	W, H = 56, 112
	c = Canvas(W, H)
	# silhouette: pillars + lintel with chamfered shoulders
	for y in range(H):
		for x in range(W):
			inside = True
			if y < 3 and (x < 4 - y or x > W - 5 + y):
				inside = False
			if inside:
				c.put(x, y, STONE_COOL[3])
	stone_fill(c, 0, 0, W, H, 3)
	# plinth at the foot of both pillars
	for y in range(H - 6, H):
		for x in range(W):
			if not (20 <= x < 36):
				t = STONE_COOL[4] if y == H - 6 else STONE_COOL[2] if y < H - 2 else STONE_COOL[1]
				if (x + y // 2) % 11 == 0 and y > H - 6:
					t = STONE_COOL[0]
				c.put(x, y, t)
	# shoulder cuts (keep chamfer)
	for y in range(3):
		for x in range(W):
			if x < 4 - y or x > W - 5 + y:
				c.px[y * W + x] = None
	# lintel: a band separating arch from pillars + underside shadow
	for x in range(W):
		c.put(x, 12, STONE_COOL[1] if 20 <= x < 36 else c.get(x, 12))
	for x in range(0, W):
		if not (20 <= x < 36):
			c.put(x, 11, STONE_COOL[1])
	# opening interior: dark with vertical gradient
	for y in range(12, H):
		for x in range(20, 36):
			t = SKY[0] if y < 100 else OUTLINE
			c.put(x, y, t)
	for y in range(12, H):
		c.put(20, y, OUTLINE)
		c.put(35, y, OUTLINE)
		c.put(21, y, SKY[1])
	for x in range(20, 36):
		c.put(x, 12, OUTLINE)
		c.put(x, 13, SKY[1])
	# vertical joint shading on pillars' inner edge
	for y in range(13, H - 6):
		c.put(19, y, STONE_COOL[1] if y % 8 else STONE_COOL[0])
		c.put(36, y, STONE_COOL[2])
	# cracks
	for (x, y) in ((6, 40), (7, 41), (7, 42), (8, 43), (8, 44), (47, 70), (46, 71), (46, 72), (45, 73), (11, 85), (12, 86), (12, 87)):
		c.put(x, y, STONE_COOL[0])
	# moss: lintel top, pillar feet, a trailing drip on the left pillar
	moss_patch(c, 0, 0, 21, 5, 11, 1)
	moss_patch(c, 35, 0, W, 5, 12, 1)
	moss_patch(c, 0, H - 22, 20, H - 6, 21, 3)
	moss_patch(c, 36, H - 18, W, H - 6, 22, 3)
	moss_patch(c, 2, 20, 8, 48, 33, 1)
	moss_patch(c, 48, 50, W, 64, 34, 1)
	for y in range(48, 58):
		if hsh(3, y, 5) % 4:
			c.put(4, y, MOSS[1])
	# keystone with gold seal (after moss so it stays clean)
	for y in range(1, 11):
		for x in range(22, 34):
			c.put(x, y, STONE_COOL[4] if x < 28 else STONE_COOL[3])
		c.put(22, y, STONE_COOL[0])
		c.put(33, y, STONE_COOL[0])
	for x in range(22, 34):
		c.put(x, 1, STONE_COOL[5])
		c.put(x, 10, STONE_COOL[0])
	for y in range(2, 10):
		for x in range(23, 33):
			d = (x - 27.5) ** 2 + (y - 5.5) ** 2
			if d <= 11.5:
				t = GOLD[2]
				if d > 7.5:
					t = GOLD[1]
				if x < 28 and y < 6 and d > 2:
					t = GOLD[3]
				c.put(x, y, t)
			elif d <= 15:
				c.put(x, y, GOLD[0])
	c.put(26, 3, GOLD[4]); c.put(27, 3, GOLD[3])
	for (x, y) in ((27, 5), (28, 5), (27, 6), (28, 6), (27, 7), (28, 7)):
		c.put(x, y, GOLD[0])
	c.put(26, 5, GOLD[1]); c.put(29, 5, GOLD[1])
	# dim gold inlays: chevron bands on both pillars
	for (x0, x1) in ((3, 16), (40, 53)):
		for by in (28, 92 - 12, 96 - 6 if False else 88):
			for x in range(x0, x1):
				mid = (x0 + x1) // 2
				dy = abs(x - mid) // 3
				c.put(x, by + dy, GOLD[1] if x < mid else GOLD[0])
				c.put(x, by + dy - 1, GOLD[2] if x < mid else GOLD[1])
	# carved rivets near the opening on both pillars
	for y in range(20, 100, 10):
		for x in (17, 38):
			c.put(x, y, STONE_COOL[5])
			c.put(x, y + 1, STONE_COOL[0])
	# torch sconces (flame is animated by gold_gate.gd) and the warm light they throw on the stone
	for tx in (10, 45):
		for yy in range(52, 62):
			for xx in range(tx - 12, tx + 13):
				d = ((xx - tx) ** 2 + ((yy - 52) * 1.1) ** 2) ** 0.5
				cur = c.get(xx, yy)
				if cur is not None and cur != OUTLINE and d < 12 and not (19 <= xx < 37):
					k = (12 - d) / 12.0 * 0.38
					c.put(xx, yy, tuple(int(cur[i] * (1 - k) + EMBER[2][i] * k) for i in range(3)) + (255,))
		for yy in range(40, 52):
			for xx in range(tx - 12, tx + 13):
				d = ((xx - tx) ** 2 + ((yy - 52) * 1.1) ** 2) ** 0.5
				cur = c.get(xx, yy)
				if cur is not None and cur != OUTLINE and d < 12 and not (19 <= xx < 37):
					k = (12 - d) / 12.0 * 0.38
					c.put(xx, yy, tuple(int(cur[i] * (1 - k) + EMBER[2][i] * k) for i in range(3)) + (255,))
		for y in range(56, 66):  # iron arm
			c.put(tx, y, STEEL[2]); c.put(tx - 1, y, STEEL[3]); c.put(tx + 1, y, STEEL[0])
		for xx in range(tx - 3, tx + 4):  # cup
			c.put(xx, 54, STEEL[3]); c.put(xx, 55, STEEL[2])
		for xx in range(tx - 2, tx + 3):
			c.put(xx, 56, STEEL[1])
		c.put(tx - 3, 53, STEEL[4]); c.put(tx + 3, 53, STEEL[1])
		for xx in range(tx - 1, tx + 2):
			c.put(xx, 66, STEEL[1])
	edge_outline(c)
	return c


def panel(medallion):
	c = Canvas(16, 100)
	for y in range(100):
		for x in range(16):
			m = x % 4
			t = (STEEL[2], STEEL[1], STEEL[0], OUTLINE)[m]
			c.put(x, y, t)
	# top rounded spearhead-less cap and horizontal gold bands
	for by in (0, 48, 96):
		for x in range(16):
			c.put(x, by, GOLD[3])
			c.put(x, by + 1, GOLD[2])
			c.put(x, by + 2, GOLD[1] if by != 96 else GOLD[1])
			if by < 96:
				c.put(x, by + 3, GOLD[0])
	for x in range(16):
		c.put(x, 99, OUTLINE)
	for y in range(100):
		c.put(0, y, OUTLINE)
		c.put(15, y, OUTLINE)
	for by in (0, 48, 96):
		for x in (2, 6, 10, 13):
			c.put(x, by + 1, GOLD[4])
	if medallion:
		cx, cy = 8, 75
		# hasp above
		for y in range(cy - 9, cy - 4):
			for x in range(6, 10):
				c.put(x, y, GOLD[1] if x > 6 else GOLD[2])
		for x in range(5, 11):
			c.put(x, cy - 10, OUTLINE)
		c.put(5, cy - 9, OUTLINE); c.put(10, cy - 9, OUTLINE)
		for y in range(cy - 7, cy + 8):
			for x in range(0, 16):
				d = (x - 7.5) ** 2 + (y - cy) ** 2
				if d <= 30.25:
					t = GOLD[2]
					if d > 20:
						t = GOLD[1]
					elif x < 7 and y < cy and d > 6:
						t = GOLD[3]
					c.put(x, y, t)
				elif d <= 42:
					c.put(x, y, OUTLINE)
		c.put(5, cy - 4, GOLD[4]); c.put(6, cy - 5, GOLD[3])
		# coin keyhole: round socket + slot
		for (x, y) in ((7, cy - 1), (8, cy - 1), (7, cy), (8, cy), (7, cy + 1), (8, cy + 1), (7, cy + 2), (8, cy + 2), (7, cy + 3), (8, cy + 3)):
			c.put(x, y, GOLD[0])
		for (x, y) in ((6, cy - 2), (9, cy - 2)):
			c.put(x, y, GOLD[0])
		c.put(7, cy - 2, GOLD[0]); c.put(8, cy - 2, GOLD[0])
	return c


def seal_glints():
	"""4 frames 12x12: a gleam travelling over the gold seal on the keystone."""
	out = []
	for f in range(4):
		c = Canvas(12, 12)
		if f == 1:
			c.put(5, 5, WHITE); c.put(4, 5, GOLD[4]); c.put(6, 5, GOLD[4])
		if f == 2:
			c.put(6, 5, WHITE)
			for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, -2), (0, 2)):
				c.put(6 + dx, 5 + dy, GOLD[4] if abs(dx) + abs(dy) == 1 else GOLD[3])
		if f == 3:
			c.put(6, 5, GOLD[4])
		out.append(c)
	return out


def flames():
	"""4 frames 8x12 torch flames, base on the bottom row centre (4, 11)."""
	out = []
	shapes = [
		[(4, 11, 3), (3, 10, 3), (4, 10, 3), (5, 10, 3), (3, 9, 2), (4, 9, 3), (5, 9, 2), (4, 8, 2), (4, 7, 1), (4, 6, 0)],
		[(4, 11, 3), (3, 10, 3), (4, 10, 3), (5, 10, 3), (3, 9, 2), (4, 9, 3), (5, 9, 2), (3, 8, 1), (4, 8, 2), (3, 7, 1), (3, 6, 0)],
		[(4, 11, 3), (3, 10, 3), (4, 10, 3), (5, 10, 3), (3, 9, 2), (4, 9, 3), (5, 9, 2), (4, 8, 2), (5, 8, 1), (4, 7, 2), (4, 6, 1), (4, 5, 0)],
		[(4, 11, 3), (3, 10, 3), (4, 10, 3), (5, 10, 3), (3, 9, 2), (4, 9, 3), (5, 9, 2), (5, 8, 1), (4, 8, 2), (5, 7, 1), (5, 6, 0)],
	]
	for pts in shapes:
		c = Canvas(8, 12)
		for x, y, t in pts:
			c.put(x, y, EMBER[t])
		c.put(4, 10, EMBER[3]); c.put(4, 9, EMBER[3])
		out.append(c)
	return out


def gate():
	c = Canvas(136, 112)
	c.blit(gate_frame(), 0, 0)
	c.blit(panel(True), 56, 12)
	c.blit(panel(False), 72, 12)
	for i, g in enumerate(seal_glints()):
		c.blit(g, 88 + 12 * i, 0)
	for i, fl in enumerate(flames()):
		c.blit(fl, 88 + 8 * i, 16)
	return c


# ------------------------------------------------------------------ main
def build():
	return {
		"trap_spikes": sheet(spikes(), 6),
		"trap_thorns": sheet(thorns(), 4),
		"prop_ferry": sheet(ferry(), 4),
		"prop_gold_gate": gate(),
	}


def main():
	assets = build()
	os.makedirs(OUT, exist_ok=True)
	for name, canvas in assets.items():
		save_png(canvas, os.path.join(OUT, name + ".png"))
		print(name, canvas.w, canvas.h)
	if "--preview" in sys.argv:
		d = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(d, exist_ok=True)
		for name, canvas in assets.items():
			save_png(canvas, os.path.join(d, name + "_x6.png"), scale=6, background=PREVIEW_BG)


if __name__ == "__main__":
	main()

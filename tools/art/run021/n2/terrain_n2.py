"""Terrain skin and underground back wall of N2 Blight Town (RUN-021 N2 visual pass).

terrain_blight_town.png follows the layout of terrain_stone.png (16 px tiles, column =
exposure mask 1 up / 2 right / 4 down / 8 left, row = theme*18 + seed*6 + phase), with
three materials chosen by depth below the walkable surface in campaign_terrain_skin.gd:
  theme 0 = street masonry: the RUN-020 blight masonry, muddier, with rot drips under the
            walkable rim (the rim itself keeps its bright capstone for readability);
  theme 1 = foundation: masonry courses sinking into putrid earth (ragged boundary);
  theme 2 = rot earth: mud with rubble, brick shards, bones, roots and dim sludge veins.
The town thus reads as "rotting from below", distinct from N1 masonry and N3 cold earth.

n2_backwall.png (16 px tiles, 6 phases per row): back walls drawn behind enclosed spaces
(world space, behind terrain), much darker and flatter than the terrain:
  row 0-2 = cellar brick (rooms, shafts), row 3-5 = deep earth (the void under the town).
Usage: python3 tools/art/run021/n2/terrain_n2.py
"""
import functools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "run020"))
from pixel import Canvas, hexc, save_png, sheet  # noqa: E402
from palette import STONE, WOOD  # noqa: E402
import world_terrain  # noqa: E402  (read only)
from palette_run020 import MUD, ROT  # noqa: E402

T = 16
STRIP = 96
SEEDS = 3
PHASES = STRIP // T
BILE = [hexc(c) for c in ("2e3216", "474d1f", "666d2a", "8a8d38", "b2ad52", "d4cc7e")]
BONE = [hexc("3a342c"), hexc("5a5246"), hexc("7a705e")]
BRICK = [hexc("2a1e1a"), hexc("3e2a23"), hexc("54382c")]
# Muddier than the RUN-020 "blight_town" theme (tint 0.22): street stones stained by rot.
world_terrain.THEMES["blight_n2"] = dict(stone=STONE, moss=ROT[:4], accent=ROT[4], tint=MUD[2], tint_k=0.3)
mix = world_terrain.mix


def rng(*seed):
	return random.Random("-".join(map(str, ("run021-n2",) + seed)))


def _h(x, y, salt=0):
	return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xFFFF


# ------------------------------------------------------------------ rot earth
EARTH_W, EARTH_H = 256, 128


def earth_macro():
	"""Seamless 256x128 putrid earth sampled in world space by the skin (no tile grid,
	period far larger than the masonry's): soft blotches, wavy strata, rubble, brick
	shards, roots, dim sludge veins and pebbles. Bones and skulls are rare decals."""
	W, H = EARTH_W, EARTH_H
	c = Canvas(W, H)
	r = rng("earth-macro")
	c.rect(0, 0, W, H, MUD[2])

	def wput(x, y, col):
		c.put(x % W, y % H, col)

	for _ in range(46):  # blotches
		bx, by, rx, ry = r.randint(0, W - 1), r.randint(0, H - 1), r.randint(4, 12), r.randint(2, 5)
		col = MUD[1] if r.random() < 0.8 else mix(MUD[2], ROT[2], 0.4)
		for y in range(by - ry, by + ry + 1):
			for x in range(bx - rx, bx + rx + 1):
				d = ((x - bx) / rx) ** 2 + ((y - by) / ry) ** 2
				if d < 0.5 or (d < 1.0 and (x + y) % 2 == 0):
					wput(x, y, col)
	for k in range(5):  # wavy strata
		base = int((k + 0.5) * H / 5) + r.randint(-3, 3)
		ph = r.uniform(0, 6.28)
		for x in range(W):
			y = base + int(round(2.2 * __import__("math").sin(2 * 3.14159 * x * 2 / W + ph)))
			if (x * 7 + k) % 11:
				wput(x, y, MUD[1])
			if (x * 5 + k) % 13 == 0:
				wput(x, y - 1, MUD[3])
	for _ in range(150):  # pebbles
		px, py = r.randint(0, W - 1), r.randint(0, H - 1)
		wput(px, py, MUD[3])
		if r.random() < 0.4:
			wput(px + 1, py, MUD[3])
		wput(px, py + 1, MUD[0])
	for _ in range(16):  # rubble stones
		sx, sy, rw, rh = r.randint(0, W - 1), r.randint(0, H - 1), r.randint(2, 5), r.randint(1, 3)
		for y in range(sy - rh, sy + rh + 1):
			for x in range(sx - rw, sx + rw + 1):
				d = ((x - sx) / rw) ** 2 + ((y - sy) / rh) ** 2
				if d <= 1.0:
					k = 4 if y < sy and d < 0.5 else 2 if y > sy else 3
					wput(x, y, mix(STONE[k], MUD[3], 0.3))
		for x in range(sx - rw + 1, sx + rw + 1):
			wput(x, sy + rh + 1, MUD[0])
	for _ in range(7):  # brick shards
		bx, by, bw = r.randint(0, W - 1), r.randint(0, H - 1), r.randint(5, 9)
		slope = r.choice((0, 0, 1, -1))
		for i in range(bw):
			yy = by + (i * slope) // 4
			wput(bx + i, yy, BRICK[2] if i < bw - 1 else BRICK[1])
			wput(bx + i, yy + 1, BRICK[1])
			wput(bx + i, yy + 2, BRICK[0])
	for i in range(8):  # roots, 3 of them sludge veins
		x, y = r.randint(0, W - 1), r.randint(0, H - 1)
		vein = i < 3
		for k in range(r.randint(18, 40)):
			col = (BILE[2] if k % 5 == 1 else BILE[1]) if vein else (WOOD[2] if k % 6 == 0 else WOOD[1])
			wput(x, y, col)
			if not vein and k % 9 == 4:
				wput(x, y + 1, WOOD[1])  # rootlet
			x += 1
			y += r.choice((-1, 0, 0, 0, 1))
	return c


def _earth_edges(c, r, mask):
	if mask & 8:
		for y in range(T):
			c.put(0, y, MUD[0])
			c.put(1, y, MUD[3] if y % 5 else MUD[2])
	if mask & 2:
		for y in range(T):
			c.put(T - 1, y, MUD[0])
			c.put(T - 2, y, MUD[1])
	if mask & 4:
		for x in range(T):
			c.put(x, T - 1, MUD[0])
			c.put(x, T - 2, MUD[1])
		for x in range(1, T - 1):  # crumbling underside with root ends and drips
			if r.random() < 0.32:
				c.put(x, T - 1, hexc("120f0c"))
			elif r.random() < 0.12:
				c.put(x, T - 1, WOOD[1])
			elif r.random() < 0.08:
				c.put(x, T - 1, BILE[1])
	if mask & 1:
		# Never used at depth (an exposed top is always the street theme) but kept valid.
		for x in range(T):
			c.put(x, 0, ROT[3])
			c.put(x, 1, ROT[2])
			c.put(x, 2, MUD[2])


def earth_tile(seed, phase, mask):
	"""Edge overlay only (interior transparent): the skin draws earth_macro underneath."""
	c = Canvas(T, T)
	_earth_edges(c, rng("earth-edge", seed, phase, mask), mask)
	return c


# ------------------------------------------------------------------ street masonry
def street_tile(seed, phase, mask):
	c = world_terrain.terrain_tile("blight_n2", seed, phase, mask)
	r = rng("street", seed, phase, mask)
	if mask & 1:
		# Rot drips and mud smears running down from the rim moss into the courses.
		for x in range(T):
			if r.random() < 0.16:
				length = r.randint(2, 6)
				for y in range(3, 3 + length):
					if c.get(x, y) is not None:
						c.put(x, y, ROT[1] if y < 2 + length else ROT[2])
			elif r.random() < 0.06:
				c.put(x, 3, MUD[1])
	elif _h(seed, phase, mask) % 5 == 0:
		# Occasional dark wet streak down a block face.
		x = r.randint(3, 12)
		for y in range(r.randint(0, 5), r.randint(9, 15)):
			if c.get(x, y) is not None:
				c.put(x, y, mix(c.get(x, y), ROT[1], 0.55))
	return c


def foundation_tile(seed, phase, mask):
	"""Masonry upper part sinking into earth: ragged boundary, loose bricks below it."""
	stone = world_terrain.terrain_tile("blight_n2", seed, phase, mask & ~1)
	r = rng("foundation", seed, phase)
	c = Canvas(T, T)
	for x in range(T):
		gx = phase * T + x
		# Boundary row varies smoothly along the 96 px strip so it runs across tiles.
		# Broken courses: the edge steps every few pixels like snapped brick ends.
		step = gx // 5
		edge = 5 + (_h(step, seed, 5) % 7)
		for y in range(T):
			if y < edge:
				col = stone.get(x, y)
			elif y == edge:
				col = MUD[0] if _h(gx, y, 7) % 3 else ROT[1]
			else:
				col = None  # earth_macro shows through
			if col is not None:
				c.put(x, y, col)
			else:
				c.px[y * T + x] = None
	# A couple of loose bricks dropped into the earth.
	for _ in range(r.randint(0, 2)):
		bx, by = r.randint(1, 10), r.randint(10, 13)
		for i in range(r.randint(3, 5)):
			c.put(bx + i, by, mix(STONE[3], MUD[2], 0.3))
			c.put(bx + i, by + 1, mix(STONE[1], MUD[1], 0.3))
	_earth_edges(c, rng("foundation-edge", seed, phase, mask), mask & ~1 & ~8 & ~2)
	if mask & 8:
		for y in range(T):
			c.put(0, y, STONE[0])
			c.put(1, y, STONE[4] if y < 8 else MUD[2])
	if mask & 2:
		for y in range(T):
			c.put(T - 1, y, STONE[0])
			c.put(T - 2, y, STONE[1] if y < 8 else MUD[1])
	return c


# ------------------------------------------------------------------ back walls
BACK_BRICK = [hexc(c) for c in ("0d0e0f", "141513", "1a1a17", "201f1b")]
BACK_EARTH = [hexc(c) for c in ("0b0b09", "0f0f0c", "131310", "171612")]


@functools.lru_cache(maxsize=None)
def back_strip(kind, seed):
	"""Seamless 96x16 back wall strip: flat, very dark, minimal detail."""
	c = Canvas(STRIP, T)
	r = rng("back", kind, seed)
	ramp = BACK_BRICK if kind == "brick" else BACK_EARTH
	for y in range(T):
		for x in range(STRIP):
			h = _h(x, y, 40 + seed)
			c.put(x, y, ramp[1] if h % 6 else ramp[0])
	if kind == "brick":
		for top in (0, 8):
			x = r.randint(0, 20)
			while x < STRIP + 20:
				w = r.randint(10, 18)
				tone = ramp[2] if r.random() < 0.6 else ramp[1]
				for y in range(top, top + 8):
					for xx in range(x, x + w):
						if y == top + 7 or xx == x + w - 1:
							col = ramp[0]
						elif y == top:
							col = ramp[3]
						else:
							col = tone if _h(xx, y, 41) % 9 else ramp[1]
						c.put(xx % STRIP, y, col)
				x += w
		# Damp patches.
		for _ in range(2):
			px, py = r.randint(0, STRIP - 1), r.randint(2, 12)
			for i in range(r.randint(4, 9)):
				c.put((px + i) % STRIP, py + (i % 3 == 0), ROT[0])
	else:
		for _ in range(4):
			sx, sy = r.randint(0, STRIP - 1), r.randint(2, 13)
			for i in range(r.randint(2, 4)):
				c.put((sx + i) % STRIP, sy, ramp[3])
				c.put((sx + i) % STRIP, sy + 1, ramp[0])
		for _ in range(2):
			x, y = r.randint(0, STRIP - 1), r.randint(2, 13)
			for k in range(r.randint(10, 20)):
				c.put(x % STRIP, y, hexc("17130f"))
				x += 1
				y = max(1, min(T - 2, y + r.choice((-1, 0, 0, 1))))
	return c


def backwall():
	out = Canvas(STRIP, T * 6)
	for k, kind in enumerate(("brick", "earth")):
		for seed in range(SEEDS):
			out.blit(back_strip(kind, seed), 0, (k * 3 + seed) * T)
	return out


# ------------------------------------------------------------------ terrain decals
# 16x16 overlays drawn rarely by the skin over terrain cells (same depth shade):
# 0 skull, 1 bones, 7 ribs (earth); 2 cellar grate, 3 lit cellar grate, 4 sewer mouth,
# 5 crack, 6 rot bloom (masonry). Transparent elsewhere.
def decals():
	out = Canvas(T * 8, T)
	S = STONE
	# 0 skull half sunk in mud
	c = Canvas(T, T)
	for y in range(5):
		for x in range(6):
			if (x, y) in ((0, 0), (5, 0)):
				continue
			c.put(5 + x, 6 + y, BONE[2] if y < 2 else BONE[1])
	for x, y in ((6, 8), (9, 8)):
		c.put(x, y, MUD[0])
		c.put(x + 1, y, MUD[0])
	c.put(8, 10, MUD[0])
	for x in range(6, 10, 2):
		c.put(x, 11, BONE[1])
		c.put(x, 12, BONE[0])
	for x in range(4, 12):
		c.put(x, 13, MUD[1])
	out.blit(c, 0, 0)
	# 1 two crossed bones
	c = Canvas(T, T)
	for i in range(9):
		c.put(3 + i, 6 + i // 3, BONE[2] if i % 4 else BONE[1])
		c.put(11 - i, 9 + i // 4, BONE[1])
	for x, y in ((2, 5), (2, 7), (12, 10), (12, 12)):
		c.put(x, y, BONE[2])
	out.blit(c, T, 0)
	# 2 cellar grate (barred basement window) and 3 the same with a dim rot glow inside
	for k in (2, 3):
		c = Canvas(T, T)
		for y in range(4, 12):
			for x in range(3, 13):
				edge = y in (4, 11) or x in (3, 12)
				c.put(x, y, S[4] if (y == 4 and not x in (3, 12)) else S[1] if edge else hexc("0c0c0b"))
		if k == 3:
			for y in range(7, 11):
				for x in range(4, 12):
					if (x + y) % 2 == 0 or y == 10:
						c.put(x, y, BILE[1] if y < 10 else BILE[2])
		for x in (5, 8, 11):
			for y in range(5, 11):
				c.put(x, y, hexc("2a2a2c") if y % 3 else S[2])
		for x in range(4, 12):
			c.put(x, 12, ROT[1] if x % 3 else ROT[2])
		out.blit(c, k * T, 0)
	# 4 sewer mouth with a sludge trail
	c = Canvas(T, T)
	for y in range(3, 10):
		for x in range(3, 13):
			d = ((x - 7.5) / 5) ** 2 + ((y - 6) / 3.5) ** 2
			if d <= 1.0:
				c.put(x, y, S[3] if d > 0.6 and y < 6 else S[1] if d > 0.6 else hexc("0b0b0a"))
	for y in range(8, 16):
		c.put(7, y, BILE[1] if y < 13 else ROT[1])
		if y < 12:
			c.put(8, y, BILE[2] if y == 8 else BILE[1])
	out.blit(c, 4 * T, 0)
	# 5 long crack
	c = Canvas(T, T)
	x = 6
	for y in range(1, 15):
		c.put(x, y, S[0])
		if y % 4 == 0:
			c.put(x + 1, y, S[1])
		x += (1, 0, -1, 0, 1, 1, 0, -1)[y % 8]
	out.blit(c, 5 * T, 0)
	# 6 rot bloom crusted on stone
	c = Canvas(T, T)
	r = rng("bloom")
	for _ in range(14):
		bx, by = r.randint(3, 12), r.randint(5, 12)
		c.put(bx, by, ROT[2] if r.random() < 0.6 else ROT[3])
	for bx, by in ((6, 8), (9, 10), (7, 11)):
		c.put(bx, by, BILE[3])
		c.put(bx + 1, by, BILE[2])
	out.blit(c, 6 * T, 0)
	# 7 ribs
	c = Canvas(T, T)
	for x in range(3, 13):
		c.put(x, 6, BONE[1])
	for i, x in enumerate(range(4, 13, 2)):
		for y in range(7, 11 + (i % 2)):
			c.put(x - (y - 7) // 2, y, BONE[2] if y == 7 else BONE[1])
	out.blit(c, 7 * T, 0)
	return out


def build():
	frames = []
	for theme in (street_tile, foundation_tile, earth_tile):
		for seed in range(SEEDS):
			for phase in range(PHASES):
				for mask in range(16):
					frames.append(theme(seed, phase, mask))
	return {"terrain_blight_town": sheet(frames, 16), "n2_backwall": backwall(), "n2_terrain_decals": decals(), "n2_earth": earth_macro()}


def preview(out_dir):
	"""Street, foundation and earth laid out as the skin draws them (with depth shade)."""
	built = build()
	tiles, macro = built["terrain_blight_town"], built["n2_earth"]
	W, H = 16 * 30, 16 * 12
	c = Canvas(W, H)
	c.rect(0, 0, W, H, hexc("1b1e22"))
	for cy in range(2, 12):
		for cx in range(30):
			if cx >= 22 and cy < 6:
				continue  # a pit to show earth side walls
			depth = cy - 2 if cx < 22 else cy - 6
			theme = 0 if depth <= 1 else 1 if depth == 2 else 2
			up = cy == 2 or (cx >= 22 and cy == 6)
			mask = (1 if up else 0) | (8 if cx == 0 else 0) | (2 if cx == 29 or (cx == 21 and cy < 6) else 0)
			row = theme * 18 + (cy % 3) * 6 + cx % 6
			shade = [1.0, 0.86, 0.74, 0.64, 0.56, 0.5][min(depth, 5)]
			for y in range(16):
				for x in range(16):
					col = None
					if theme > 0:
						col = macro.get((cx * 16 + x) % macro.w, (cy * 16 + y) % macro.h)
					t = tiles.get(mask * 16 + x, row * 16 + y)
					if t is not None:
						col = t
					if col is not None:
						c.put(cx * 16 + x, cy * 16 + y, tuple(int(v * shade) for v in col[:3]) + (255,))
	save_png(c, os.path.join(out_dir, "terrain_n2_stack.png"), 3)


if __name__ == "__main__":
	out = os.path.join(ROOT, "assets", "run021", "n2")
	os.makedirs(out, exist_ok=True)
	for name, canvas in build().items():
		save_png(canvas, os.path.join(out, name + ".png"))
		print("wrote", name, canvas.w, "x", canvas.h)
	prev = os.path.join(ROOT, "work", "run021", "n2pass", "preview")
	os.makedirs(prev, exist_ok=True)
	preview(prev)

"""Terrain skin and underground back wall of N4 Forbidden Graveyard (RUN-021 N4 visual pass).

terrain_forbidden_graveyard_n4.png follows the layout of terrain_stone.png (16 px tiles,
column = exposure mask 1 up / 2 right / 4 down / 8 left, row = theme*18 + seed*6 + phase),
with four materials chosen in campaign_terrain_skin.gd:
  theme 0 = cemetery masonry: large weathered ashlar in cold violet-grey stone, grey lichen and
            moss in the joints (plaques and carvings come from the rare decals); a pale capstone rim keeps every walkable
            top readable. Everything above the ground line (mausoleum blocks, the tower) stays
            masonry, as in N2;
  theme 1 = foundation course: the last masonry course breaking up into grave earth, with a
            ragged lower boundary so the earth shows below;
  theme 2 = grave earth: edge overlay only, the skin draws n4_earth.png (seamless world-space
            texture: dark violet-brown soil, strata, buried stones, bone fragments, rotten coffin
            boards, roots) underneath;
  theme 3 = crypt pillar: narrow tall columns read as stacked pillar drums with a chamfered
            edge, lit from the upper right like the N4 moon; a walkable top keeps the rim.
The graveyard thus reads as "a necropolis built over its own dead", distinct from the N1
village masonry it used before, from N2's rot and from N3's forest floor.

n4_backwall.png (16 px tiles, 6 phases per row): back walls drawn behind enclosed spaces
(world space, behind terrain), much darker and flatter than the terrain:
  row 0-2 = crypt (rooms, shafts): dark ashlar with a few sealed burial slots,
  row 3-5 = deep earth (the void under the graveyard).
n4_terrain_decals.png: rare 16x16 overlays (see decals()).
n4_mist.png: 256x32 ground mist strip, drawn by the decor (see atmos_n4.py).
Usage: python3 tools/art/run021/n4/terrain_n4.py
"""
import functools
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "run020"))
from pixel import Canvas, hexc, save_png, sheet  # noqa: E402
from palette import STONE_COOL, WOOD  # noqa: E402
from palette_run020 import DUSK_VIOLET, SPECTRAL  # noqa: E402
import world_terrain  # noqa: E402  (read only)

T = 16
STRIP = 96
SEEDS = 3
PHASES = STRIP // T
mix = world_terrain.mix
# Cold stone pulled toward the N4 desaturated violet (dark -> light). The light end stays the
# capstone rim, clearly lighter than the body so platforms read at once.
STONE = [mix(STONE_COOL[i], DUSK_VIOLET[min(i, 5)], 0.3) for i in range(6)]
# Grey lichen and dull moss: greyed, never the saturated healing / slime green.
LICHEN = [hexc(c) for c in ("262a26", "343a32", "464d41", "5c6455")]
EARTH = [hexc(c) for c in ("17141a", "1e1a21", "26212a", "2f2933", "3a333e")]
BONE = [hexc("332f33"), hexc("4a4549"), hexc("625c5e")]
COFFIN = [mix(WOOD[0], EARTH[1], 0.45), mix(WOOD[1], EARTH[2], 0.5), mix(WOOD[2], EARTH[3], 0.55)]
ROOT_C = [mix(WOOD[0], EARTH[1], 0.55), mix(WOOD[1], EARTH[2], 0.55)]
GHOST = SPECTRAL  # greyed spectral cyan, only as a few faint pixels


def rng(*seed):
	return random.Random("-".join(map(str, ("run021-n4",) + seed)))


def _h(x, y, salt=0):
	return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xFFFF


def _widths(r, lo=14, hi=28, total=STRIP):
	widths, rem = [], total
	while rem > 0:
		w = r.randint(lo, hi)
		if rem <= hi:
			w = rem
		elif rem - w < lo:
			w = rem - lo
		widths.append(w)
		rem -= w
	return widths


def _block(c, r, x0, x1, top, bottom, s=STONE):
	"""One weathered ashlar block: bevel, mortar, pits, rare crack, lichen on its face."""
	k = r.random()
	tone = s[2] if k < 0.45 else s[3] if k < 0.85 else mix(s[2], s[1], 0.5)
	hi, hi2 = mix(tone, s[5], 0.36), mix(tone, s[5], 0.16)
	lo, lo2 = mix(tone, s[0], 0.42), mix(tone, s[0], 0.2)
	W = c.w
	for y in range(top, bottom + 1):
		for x in range(x0, x1):
			xx = x % W
			if y == bottom or x == x0:
				col = s[0]  # mortar (left joint: the light comes from the upper right)
			elif y == top:
				col = hi2
			elif x == x1 - 1:
				col = hi
			elif y == bottom - 1:
				col = lo
			elif x == x0 + 1:
				col = lo2
			else:
				h = _h(xx, y, 3)
				col = lo2 if h % 8 == 0 else hi2 if h % 15 == 0 else tone
			c.put(xx, y, col)
	for _ in range(r.randint(1, 4)):  # weathering pits
		c.put(r.randint(x0 + 2, x1 - 3) % W, r.randint(top + 2, max(top + 2, bottom - 2)), lo)
	if r.random() < 0.2 and x1 - x0 > 10:  # hairline crack
		cx = r.randint(x0 + 3, x1 - 4)
		for y in range(top + 1, bottom - 1):
			c.put(cx % W, y, s[1])
			if r.random() < 0.55:
				cx += r.choice((-1, 1))
	if r.random() < 0.38:  # grey lichen blotch
		lx, ly = r.randint(x0 + 2, x1 - 4), r.randint(top + 1, max(top + 1, bottom - 3))
		for i in range(r.randint(3, 7)):
			c.put((lx + r.randint(-2, 2)) % W, max(top + 1, min(bottom - 1, ly + r.randint(-1, 1))), LICHEN[1] if i % 3 else LICHEN[2])
	if r.random() < 0.3:  # moss in the bottom joint
		for x in range(x0 + 1, min(x1 - 1, x0 + 1 + r.randint(3, 7))):
			c.put(x % W, bottom, LICHEN[0] if r.random() < 0.7 else LICHEN[1])



@functools.lru_cache(maxsize=None)
def masonry_strip(seed):
	"""Seamless 96x16 cemetery masonry: two 8 px courses of long blocks."""
	c = Canvas(STRIP, T)
	r = rng("masonry", seed)
	for top, bottom in ((0, 7), (8, 15)):
		x = r.randint(0, STRIP - 1)
		for w in _widths(r):
			_block(c, r, x, x + w, top, bottom)
			x += w
	return c


def _rim(c, r, mask, s=STONE):
	"""Walkable rim: pale capstone and a shadowed course, sparse lichen and grass on top."""
	for x in range(T):
		chip = r.random() < 0.1
		c.put(x, 0, s[4] if chip else s[5])
		c.put(x, 1, s[3] if chip else s[4])
		c.put(x, 2, s[2] if x % 5 else s[1])
	for x in range(1, T, 5):
		c.put((x + r.randint(0, 2)) % T, 0, mix(s[5], s[3], 0.5))  # worn flecks
	for x in range(T):
		if r.random() < 0.42:
			depth = r.choice((1, 1, 2, 2, 3))
			for y in range(depth):
				c.put(x, y, LICHEN[3] if y == 0 else LICHEN[2] if y < depth - 1 else LICHEN[1])
	if mask & 8:
		c.put(0, 0, s[0])
	if mask & 2:
		c.put(T - 1, 0, s[0])


def _stone_edges(c, r, mask, s=STONE):
	if mask & 8:
		for y in range(T):
			c.put(0, y, s[0])
			c.put(1, y, s[2] if y % 8 != 7 else s[0])
	if mask & 2:  # moon side: a lighter face
		for y in range(T):
			c.put(T - 1, y, s[1])
			c.put(T - 2, y, s[4] if y % 8 != 7 else s[1])
		for _ in range(2):
			y0 = r.randint(1, 12)
			for y in range(y0, y0 + r.randint(2, 3)):
				c.put(T - 2, min(y, T - 1), LICHEN[1])
	if mask & 4:
		for x in range(T):
			c.put(x, T - 1, s[0])
			c.put(x, T - 2, s[1])
		for x in range(1, T - 1):  # crumbling underside
			if r.random() < 0.3:
				c.px[(T - 1) * T + x] = None
				if r.random() < 0.3:
					c.px[(T - 2) * T + x] = None
	if mask & 1:
		_rim(c, r, mask, s)


def masonry_tile(seed, phase, mask):
	base = masonry_strip(seed)
	c = Canvas(T, T)
	for y in range(T):
		for x in range(T):
			c.put(x, y, base.get(phase * T + x, y))
	_stone_edges(c, rng("masonry-edge", seed, phase, mask), mask)
	return c


# ------------------------------------------------------------------ foundation course
def foundation_tile(seed, phase, mask):
	"""The lowest masonry course giving way to grave earth: blocks end raggedly, the earth
	(drawn underneath by the skin) shows through below and between sunken stones."""
	base = masonry_strip((seed + 2) % SEEDS)
	c = Canvas(T, T)
	for x in range(T):
		gx = phase * T + x
		edge = 8 + int(round(2.2 * math.sin(gx * 2 * math.pi / STRIP * 2 + seed))) + (_h(gx // 4, seed, 9) % 3)
		for y in range(T):
			if y < edge:
				col = mix(base.get(gx, y), EARTH[2], 0.22)
			elif y == edge:
				col = EARTH[0]
			else:
				col = None
			if col is not None:
				c.put(x, y, col)
	r = rng("sunken", seed, phase)
	for _ in range(r.randint(0, 2)):  # a sunken stone below the course
		sx, sy, rw, rh = r.randint(2, 13), r.randint(11, 13), r.randint(2, 3), 1
		for y in range(sy - rh, sy + rh + 1):
			for x in range(sx - rw, sx + rw + 1):
				if 0 <= x < T and 0 <= y < T and ((x - sx) / rw) ** 2 + ((y - sy) / (rh + 0.5)) ** 2 <= 1.0:
					c.put(x, y, STONE[2] if y < sy else STONE[1])
	if r.random() < 0.4:  # a root threading out under the course
		x, y = r.randint(0, 6), r.randint(10, 13)
		for k in range(r.randint(6, 12)):
			if 0 <= x < T and 0 <= y < T:
				c.put(x, y, ROOT_C[1] if k % 4 else ROOT_C[0])
			x += 1
			y = max(9, min(T - 1, y + r.choice((-1, 0, 0, 1))))
	_stone_edges(c, rng("foundation-edge", seed, phase, mask), mask & ~1)
	if mask & 1:
		_rim(c, rng("foundation-rim", seed, phase, mask), mask)
	return c


# ------------------------------------------------------------------ grave earth (world space)
EARTH_W, EARTH_H = 256, 128


def earth_macro():
	"""Seamless 256x128 grave earth sampled in world space by the skin: dark violet-brown
	soil, wavy strata, buried stones, bone fragments, rotten coffin boards and roots."""
	W, H = EARTH_W, EARTH_H
	c = Canvas(W, H)
	r = rng("earth-macro")
	c.rect(0, 0, W, H, EARTH[2])

	def wput(x, y, col):
		c.put(x % W, y % H, col)

	for _ in range(46):  # blotches
		bx, by, rx, ry = r.randint(0, W - 1), r.randint(0, H - 1), r.randint(4, 12), r.randint(2, 5)
		col = EARTH[1] if r.random() < 0.72 else EARTH[3]
		for y in range(by - ry, by + ry + 1):
			for x in range(bx - rx, bx + rx + 1):
				d = ((x - bx) / rx) ** 2 + ((y - by) / ry) ** 2
				if d < 0.5 or (d < 1.0 and (x + y) % 2 == 0):
					wput(x, y, col)
	for k in range(4):  # wavy strata
		base = int((k + 0.5) * H / 4) + r.randint(-3, 3)
		ph = r.uniform(0, 6.28)
		for x in range(W):
			y = base + int(round(2.4 * math.sin(2 * math.pi * x * 2 / W + ph)))
			if (x * 7 + k) % 9:
				wput(x, y, EARTH[1])
			if (x * 5 + k) % 13 == 0:
				wput(x, y - 1, EARTH[3])
	for _ in range(150):  # grit
		px, py = r.randint(0, W - 1), r.randint(0, H - 1)
		wput(px, py, EARTH[3])
		wput(px, py + 1, EARTH[0])
	for _ in range(16):  # buried stones, lit from the upper right
		sx, sy, rw, rh = r.randint(0, W - 1), r.randint(0, H - 1), r.randint(3, 6), r.randint(2, 3)
		for y in range(sy - rh, sy + rh + 1):
			for x in range(sx - rw, sx + rw + 1):
				d = ((x - sx) / rw) ** 2 + ((y - sy) / rh) ** 2
				if d <= 1.0:
					k = 3 if (y < sy and x > sx - 1 and d < 0.6) else 1 if y > sy else 2
					wput(x, y, mix(STONE[k], EARTH[2], 0.38))
		for x in range(sx - rw + 1, sx + rw + 1):
			wput(x, sy + rh + 1, EARTH[0])
	for _ in range(5):  # rotten coffin boards: short dark planks, broken, never box-shaped
		bx, by, bw = r.randint(0, W - 1), r.randint(4, H - 6), r.randint(10, 18)
		for x in range(bx, bx + bw):
			if _h(x, by, 5) % 7 == 0:
				continue
			wput(x, by, COFFIN[2] if x % 5 else COFFIN[1])
			wput(x, by + 1, COFFIN[1])
			wput(x, by + 2, COFFIN[0])
		wput(bx + bw // 2, by + 1, EARTH[0])  # nail hole
	for _ in range(14):  # bone fragments
		bx, by = r.randint(0, W - 1), r.randint(0, H - 1)
		n = r.randint(3, 5)
		dy = r.choice((-1, 0, 1))
		for i in range(n):
			wput(bx + i, by + (i * dy) // 3, BONE[1] if i in (0, n - 1) else BONE[0])
	for i in range(7):  # roots
		x, y = r.randint(0, W - 1), r.randint(0, H - 1)
		for k in range(r.randint(18, 40)):
			wput(x, y, ROOT_C[1] if k % 6 else ROOT_C[0])
			x += 1
			y += r.choice((-1, 0, 0, 0, 1, 1))
	return c


def earth_tile(seed, phase, mask):
	"""Edge overlay only (interior transparent): the skin draws earth_macro underneath."""
	c = Canvas(T, T)
	r = rng("earth-edge", seed, phase, mask)
	if mask & 8:
		for y in range(T):
			c.put(0, y, EARTH[0])
			c.put(1, y, EARTH[3] if y % 5 else EARTH[2])
	if mask & 2:
		for y in range(T):
			c.put(T - 1, y, EARTH[0])
			c.put(T - 2, y, EARTH[4] if y % 4 else EARTH[3])
	if mask & 4:
		for x in range(T):
			c.put(x, T - 1, EARTH[0])
			c.put(x, T - 2, EARTH[1])
		for x in range(1, T - 1):
			if r.random() < 0.3:
				c.px[(T - 1) * T + x] = None
			elif r.random() < 0.12:
				c.put(x, T - 1, ROOT_C[1])
	if mask & 1:
		_rim(c, r, mask)
	return c


# ------------------------------------------------------------------ crypt pillar
@functools.lru_cache(maxsize=None)
def pillar_strip(seed):
	"""Seamless 96x16 stacked pillar drums: one 16 px drum per tile height, joints offset by
	seed, vertical fluting, the right edge of each flute lit by the moon (upper right)."""
	c = Canvas(STRIP, T)
	r = rng("pillar", seed)
	joint = (5 + seed * 4) % T
	for x in range(STRIP):
		flute = x % 6
		for y in range(T):
			if y == joint:
				col = STONE[0]
			elif y == (joint + 1) % T:
				col = STONE[4]
			elif flute == 0:
				col = STONE[1]
			elif flute == 5:
				col = STONE[3]
			else:
				col = STONE[2] if _h(x, y, seed) % 11 else STONE[1]
			c.put(x, y, col)
	for _ in range(3 + seed):  # lichen streaks running down a flute
		lx, ly = r.randint(0, STRIP - 1), r.randint(0, T - 1)
		for i in range(r.randint(3, 6)):
			c.put(lx % STRIP, (ly + i) % T, LICHEN[1] if i % 3 else LICHEN[2])
	for _ in range(2):  # chips
		c.put(r.randint(0, STRIP - 1), r.randint(0, T - 1), STONE[0])
	return c


def pillar_tile(seed, phase, mask):
	base = pillar_strip(seed)
	c = Canvas(T, T)
	for y in range(T):
		for x in range(T):
			c.put(x, y, base.get(phase * T + x, y))
	r = rng("pillar-edge", seed, phase, mask)
	if mask & 2:  # moon side: chamfered lit edge
		for y in range(T):
			c.put(T - 1, y, STONE[2])
			c.put(T - 2, y, STONE[5] if y % 7 else STONE[4])
	if mask & 8:
		for y in range(T):
			c.put(0, y, STONE[0])
			c.put(1, y, STONE[1])
	if mask & 4:
		for x in range(T):
			c.put(x, T - 1, STONE[0])
			c.put(x, T - 2, STONE[1])
		for x in range(1, T - 1):
			if r.random() < 0.2:
				c.px[(T - 1) * T + x] = None
	if mask & 1:
		_rim(c, r, mask)
	return c


# ------------------------------------------------------------------ back walls
BACK_CRYPT = [hexc(c) for c in ("0c0b10", "111017", "17151d", "1d1a23")]
BACK_DEEP = [hexc(c) for c in ("0a090c", "0d0c10", "111014", "151319")]


@functools.lru_cache(maxsize=None)
def back_strip(kind, seed):
	"""Seamless 96x16 back wall strip: flat, very dark, minimal detail."""
	c = Canvas(STRIP, T)
	r = rng("back", kind, seed)
	ramp = BACK_CRYPT if kind == "crypt" else BACK_DEEP
	for y in range(T):
		for x in range(STRIP):
			h = _h(x, y, 40 + seed)
			c.put(x, y, ramp[1] if h % 6 else ramp[0])
	if kind == "crypt":
		# Large dark ashlar blocks, joints barely visible, a sealed burial slot now and then.
		for top, bottom in ((0, 7), (8, 15)):
			x = r.randint(0, STRIP - 1)
			for w in _widths(r, 16, 30):
				for y in range(top, bottom + 1):
					c.put(x % STRIP, y, ramp[0])
				for xx in range(x, x + w):
					c.put(xx % STRIP, bottom, ramp[0])
					c.put(xx % STRIP, top, ramp[2] if _h(xx, top, 7) % 3 else ramp[1])
				x += w
		if seed != 1:
			sx = r.randint(4, STRIP - 24)
			for y in range(3, 13):
				for x in range(sx, sx + 18):
					edge = y in (3, 12) or x in (sx, sx + 17)
					c.put(x, y, ramp[3] if edge and (y == 3 or x == sx + 17) else ramp[0] if edge else ramp[2])
			for x in range(sx + 4, sx + 14, 3):  # worn inscription
				c.put(x, 7, ramp[0])
	else:
		for _ in range(4):
			sx, sy = r.randint(0, STRIP - 1), r.randint(2, 13)
			for i in range(r.randint(2, 4)):
				c.put((sx + i) % STRIP, sy, ramp[3])
				c.put((sx + i) % STRIP, sy + 1, ramp[0])
		for _ in range(2):
			x, y = r.randint(0, STRIP - 1), r.randint(2, 13)
			for k in range(r.randint(10, 20)):
				c.put(x % STRIP, y, hexc("15121a"))
				x += 1
				y = max(1, min(T - 2, y + r.choice((-1, 0, 0, 1))))
	return c


def backwall():
	out = Canvas(STRIP, T * 6)
	for k, kind in enumerate(("crypt", "deep")):
		for seed in range(SEEDS):
			out.blit(back_strip(kind, seed), 0, (k * 3 + seed) * T)
	return out


# ------------------------------------------------------------------ terrain decals
# 16x16 overlays drawn rarely by the skin over terrain cells (same depth shade):
# earth (theme 2): 0 skull, 1 bones, 2 coffin corner, 3 ghost-light fungus (the skin adds a
# faint cold glow); masonry (theme 0 interior): 4 epitaph plaque, 5 carved cross,
# 6 crack with roots, 7 sealed burial slot. Transparent elsewhere. Dark: texture, not pickups.
def decals():
	out = Canvas(T * 8, T)
	# 0 skull half sunk in the earth (dark, sideways)
	c = Canvas(T, T)
	for y in range(5):
		for x in range(6):
			if (x, y) in ((0, 0), (5, 0)):
				continue
			c.put(5 + x, 6 + y, BONE[2] if y < 2 else BONE[1])
	for x, y in ((6, 8), (9, 8)):
		c.put(x, y, EARTH[0])
		c.put(x + 1, y, EARTH[0])
	c.put(8, 10, EARTH[0])
	for x in range(6, 10, 2):
		c.put(x, 11, BONE[1])
		c.put(x, 12, BONE[0])
	for x in range(4, 12):
		c.put(x, 13, EARTH[1])
	out.blit(c, 0, 0)
	# 1 a long bone and a rib
	c = Canvas(T, T)
	for i in range(10):
		c.put(3 + i, 7 + i // 4, BONE[2] if 0 < i < 9 else BONE[1])
	for x, y in ((2, 6), (2, 8), (13, 9), (13, 11)):
		c.put(x, y, BONE[1])
	for i in range(5):
		c.put(5 + i, 12 - abs(i - 2) // 2, BONE[0])
	out.blit(c, T, 0)
	# 2 coffin corner: two dark boards meeting, half buried
	c = Canvas(T, T)
	for x in range(2, 14):
		c.put(x, 6, COFFIN[2] if x % 4 else COFFIN[1])
		c.put(x, 7, COFFIN[1])
	for y in range(6, 14):
		c.put(11, y, COFFIN[2] if y % 4 else COFFIN[1])
		c.put(12, y, COFFIN[0])
	for x in range(2, 11):
		c.put(x, 8, EARTH[0])
	c.put(6, 6, EARTH[0])  # nail
	c.put(11, 10, EARTH[0])
	out.blit(c, 2 * T, 0)
	# 3 ghost-light fungus: a few faint cold caps (the skin adds a dim glow)
	c = Canvas(T, T)
	r = rng("ghost-fungus")
	for _ in range(10):
		bx, by = r.randint(3, 12), r.randint(6, 12)
		c.put(bx, by, GHOST[0] if r.random() < 0.7 else GHOST[1])
	for bx, by in ((6, 9), (9, 10)):
		c.put(bx, by, GHOST[2])
		c.put(bx, by + 1, EARTH[1])
	out.blit(c, 3 * T, 0)
	# 4 epitaph plaque set into the masonry
	c = Canvas(T, T)
	for y in range(3, 13):
		for x in range(3, 13):
			edge = y in (3, 12) or x in (3, 12)
			c.put(x, y, STONE[1] if edge and (y == 12 or x == 3) else STONE[4] if edge else STONE[3])
	for y in (6, 8, 10):
		for x in range(5, 11):
			if _h(x, y, 21) % 3:
				c.put(x, y, STONE[1])
	out.blit(c, 4 * T, 0)
	# 5 carved cross relief (flat, recessed)
	c = Canvas(T, T)
	for y in range(3, 14):
		c.put(7, y, STONE[1])
		c.put(8, y, STONE[4] if y > 3 else STONE[1])
	for x in range(4, 12):
		c.put(x, 6, STONE[1])
		c.put(x, 7, STONE[4] if x > 4 else STONE[1])
	out.blit(c, 5 * T, 0)
	# 6 crack with a root pushing through
	c = Canvas(T, T)
	x = 4
	for y in range(1, 15):
		c.put(x, y, STONE[0])
		if y % 3 == 0:
			x += 1
	for i, (rx, ry) in enumerate(((5, 9), (6, 10), (7, 10), (8, 11), (9, 11), (10, 12))):
		c.put(rx, ry, ROOT_C[1] if i % 2 else ROOT_C[0])
	out.blit(c, 6 * T, 0)
	# 7 sealed burial slot: a recessed slab with a worn ring
	c = Canvas(T, T)
	for y in range(5, 12):
		for x in range(2, 14):
			edge = y in (5, 11) or x in (2, 13)
			c.put(x, y, STONE[0] if edge and (y == 5 or x == 2) else STONE[4] if edge else STONE[2])
	for x, y in ((7, 8), (8, 7), (9, 8), (8, 9)):
		c.put(x, y, STONE[1])
	out.blit(c, 7 * T, 0)
	return out


def build():
	frames = []
	for theme in (masonry_tile, foundation_tile, earth_tile, pillar_tile):
		for seed in range(SEEDS):
			for phase in range(PHASES):
				for mask in range(16):
					frames.append(theme(seed, phase, mask))
	return {
		"terrain_forbidden_graveyard_n4": sheet(frames, 16),
		"n4_backwall": backwall(),
		"n4_terrain_decals": decals(),
		"n4_earth": earth_macro(),
	}


def preview(out_dir, built):
	"""Masonry, foundation and grave earth laid out as the skin draws them (with depth shade),
	a pit with side walls, a pillar on the right and a crypt back wall behind the pit."""
	tiles, macro, back = built["terrain_forbidden_graveyard_n4"], built["n4_earth"], built["n4_backwall"]
	W, H = 16 * 32, 16 * 14
	c = Canvas(W, H)
	c.rect(0, 0, W, H, hexc("19161f"))
	solid = set()
	for cy in range(3, 14):
		for cx in range(32):
			if 18 <= cx <= 21 and cy < 9:
				continue
			if cx >= 26 and cy < 6:
				continue
			solid.add((cx, cy))
	for cy in range(0, 6):
		for cx in (27, 28):
			solid.add((cx, cy))
	pillar = {(cx, cy) for (cx, cy) in solid if cx in (27, 28) and cy < 6}
	for (cx, cy) in [(x, y) for x in range(18, 22) for y in range(3, 9)]:
		for y in range(16):
			for x in range(16):
				c.put(cx * 16 + x, cy * 16 + y, back.get((cx * 16 + x) % 96, (cy % 3) * 16 + y))
	for (cx, cy) in solid:
		depth = 0
		while depth < 5 and (cx, cy - depth - 1) in solid:
			depth += 1
		mask = (0 if (cx, cy - 1) in solid else 1) | (0 if (cx + 1, cy) in solid else 2) | (0 if (cx, cy + 1) in solid or cy == 13 else 4) | (0 if (cx - 1, cy) in solid else 8)
		theme = 3 if (cx, cy) in pillar else 0 if depth <= 1 else 1 if depth == 2 else 2
		row = theme * 18 + (cy % 3) * 6 + cx % 6
		shade = [1.0, 0.92, 0.84, 0.78, 0.74, 0.72][min(depth, 5)] if theme != 3 else 0.92
		for y in range(16):
			for x in range(16):
				col = None
				if theme in (1, 2):
					col = macro.get((cx * 16 + x) % macro.w, (cy * 16 + y) % macro.h)
				t = tiles.get(mask * 16 + x, row * 16 + y)
				if t is not None:
					col = t
				if col is not None:
					c.put(cx * 16 + x, cy * 16 + y, tuple(int(v * shade) for v in col[:3]) + (255,))
	save_png(c, os.path.join(out_dir, "terrain_n4_stack.png"), 3)


if __name__ == "__main__":
	out = os.path.join(ROOT, "assets", "run021", "n4")
	os.makedirs(out, exist_ok=True)
	built = build()
	for name, canvas in built.items():
		save_png(canvas, os.path.join(out, name + ".png"))
		print("wrote", name, canvas.w, "x", canvas.h)
	prev = os.path.join(ROOT, "work", "run021", "n4pass", "preview")
	os.makedirs(prev, exist_ok=True)
	preview(prev, built)
	save_png(built["n4_terrain_decals"], os.path.join(prev, "terrain_n4_decals.png"), 4)

"""New decor props of the slice (RUN-029): bridge pillars, lanterns, braziers, torches,
graves, fences, bushes, rubble, bones, shrine, gallows, chains, banners, roots and
the dithered warm glow texture.

Origin of every prop is documented per function. All of them are decor: they sit
behind gameplay, stay darker and less saturated than enemies/player/hazards, and
warm light (EMBER ramp) is a sparse accent. The glow is a dithered, low-alpha
texture; saturated red is never used here (dark desaturated reds only).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, hexc, sheet  # noqa: E402
from palette import CORRUPT, EMBER, GOLD, MOSS, STEEL, STONE, STONE_COOL, WOOD  # noqa: E402

# Dark desaturated reds for cloth (Art Bible: decor uses dark desaturated reds).
CLOTH = [hexc("24101a"), hexc("3a1620"), hexc("52202a"), hexc("6a2d36")]
BONE = [hexc("4a4238"), hexc("7a705e"), hexc("a89c84"), hexc("cfc4ae")]
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def rng(*seed):
	return random.Random("-".join(map(str, seed)))


def mix(a, b, k):
	return tuple(int(round(a[i] * (1 - k) + b[i] * k)) for i in range(3)) + (255,)


def masonry_rect(c, x0, y0, w, h, ramp, r, course=6, moss=None):
	"""Small ashlar fill used by pillars, shrines and ruin stubs."""
	y = y0
	row = 0
	while y < y0 + h:
		ch = min(course, y0 + h - y)
		x = x0 - (0 if row % 2 == 0 else r.randint(2, 5))
		while x < x0 + w:
			bw = r.randint(7, 12)
			tone = ramp[2] if r.random() < 0.55 else ramp[3]
			for yy in range(y, y + ch):
				for xx in range(x, x + bw):
					if not (x0 <= xx < x0 + w):
						continue
					if yy == y + ch - 1 or xx == x + bw - 1:
						col = ramp[0]
					elif yy == y:
						col = ramp[4]
					elif xx == x:
						col = mix(tone, ramp[4], 0.4)
					elif yy == y + ch - 2:
						col = ramp[1]
					else:
						col = tone if (xx * 7 + yy * 5) % 11 else ramp[1]
					c.put(xx, yy, col)
			if moss and r.random() < 0.22:
				for xx in range(x + 1, min(x + bw - 1, x + 5)):
					if x0 <= xx < x0 + w:
						c.put(xx, y, moss[2] if xx % 2 else moss[1])
			x += bw
		y += ch
		row += 1


# ------------------------------------------------------------------ pillars
def pillar(broken):
	"""16x140 bridge pillar, origin bottom-centre (8, 140). Cool stone, behind gameplay."""
	W, H = 16, 140
	c = Canvas(W, H)
	r = rng("pillar", broken)
	s = [mix(v, hexc("1c2128"), 0.18) for v in STONE_COOL]  # slightly deeper than the terrain
	top = 6 if not broken else 14
	for y in range(top, H - 12):
		for x in range(3, 13):
			if x == 3:
				col = s[4]
			elif x == 4:
				col = s[3]
			elif x == 12:
				col = s[0]
			elif x == 11:
				col = s[1]
			else:
				col = s[2] if (x * 3 + y) % 17 else s[1]
			c.put(x, y, col)
	for y in range(top + 10, H - 12, 14):  # drum joints
		for x in range(3, 13):
			c.put(x, y, s[0])
			c.put(x, y + 1, s[3] if x < 10 else s[1])
	for _ in range(7):  # cracks and pits
		x, y = r.randint(5, 10), r.randint(top + 4, H - 20)
		for i in range(r.randint(3, 8)):
			c.put(x, y + i, s[0])
			x += r.choice((-1, 0, 0, 1)) if 4 < x < 11 else 0
	for _ in range(5):  # moss streaks hanging from the joints
		x, y = r.randint(4, 10), top + 11 + 14 * r.randint(0, 7)
		if y < H - 14:
			for i in range(r.randint(2, 6)):
				c.put(x, y + i, MOSS[1] if i % 3 else MOSS[0])
			c.put(x, y, MOSS[2])
	if not broken:
		# Capital: abacus, echinus.
		for x in range(1, 15):
			c.put(x, 0, s[4])
			c.put(x, 1, s[3])
			c.put(x, 2, s[2])
			c.put(x, 3, s[1])
		for x in range(2, 14):
			c.put(x, 4, s[2])
			c.put(x, 5, s[0])
		for x in range(1, 15):
			c.put(x, 0 if x else 0, s[4] if x < 14 else s[0])
	else:
		# Snapped shaft: jagged top and fallen chips.
		for x in range(3, 13):
			for y in range(top - r.randint(0, 5), top):
				c.put(x, y, s[2] if x < 8 else s[1])
		for x in range(3, 13):
			c.put(x, top - 6 if x % 3 == 0 else top, s[3])
	# Plinth.
	for y in range(H - 12, H):
		for x in range(1, 15):
			k = 4 if y == H - 12 else 0 if y == H - 1 or x in (1, 14) else 3 if x == 2 else 1 if x > 12 else 2
			c.put(x, y, s[k])
	for x in range(1, 15):
		c.put(x, H - 9, s[0])
		c.put(x, H - 5, s[0])
	for x in range(2, 8):
		c.put(x, H - 12, MOSS[2] if x % 2 else MOSS[1])
	return c


# ------------------------------------------------------------------ lights
def flame_frames():
	"""Three 10x14 flame frames, origin bottom-centre (5, 14)."""
	frames = []
	for k in range(3):
		c = Canvas(10, 14)
		h = (9, 11, 10)[k]
		sway = (0, 1, -1)[k]
		for i in range(h):
			t = i / h
			half = max(0, int(round(3.2 * (1 - t) ** 0.8 * (1 if i > 1 else 0.8))))
			cx = 5 + int(round(sway * t * 1.6))
			for dx in range(-half, half + 1):
				d = abs(dx)
				if i == h - 1:
					col = EMBER[0]
				elif d == half and half > 0:
					col = EMBER[1]
				elif d <= max(0, half - 2) and i < h * 0.55:
					col = EMBER[3]
				else:
					col = EMBER[2]
				c.put(cx + dx, 13 - i, col)
		if k == 1:
			c.put(7, 2, EMBER[0])
		if k == 2:
			c.put(3, 3, EMBER[0])
		frames.append(c)
	return frames


def flame_sheet():
	return sheet(flame_frames(), 3)


def glow():
	"""64x64 dithered warm halo, centred (32, 32); alpha-blended, never saturated."""
	c = Canvas(64, 64)
	col = EMBER[1]
	for y in range(64):
		for x in range(64):
			d = math.hypot(x - 31.5, y - 31.5)
			if d < 9:
				a, density = 54, 1.0
			elif d < 18:
				a, density = 38, 0.55
			elif d < 31:
				a, density = 24, 0.28
			else:
				continue
			if density * 16 > BAYER[y % 4][x % 4] + 0.5:
				c.put(x, y, col[:3] + (a,))
	return c


def lantern_post():
	"""14x48 iron lamp post with a hanging lantern. Origin bottom-centre (7, 48)."""
	c = Canvas(14, 48)
	r = rng("lamp")
	iron = [STEEL[0], hexc("20242d"), STEEL[1]]
	for y in range(8, 48):
		c.put(6, y, iron[1])
		c.put(7, y, iron[2] if y % 9 else STEEL[2])
	for x in range(3, 11):  # stone footing
		for y in range(43, 48):
			c.put(x, y, STONE[2] if y > 43 else STONE[4])
	for x in range(3, 11):
		c.put(x, 47, STONE[0])
	for x in range(6, 12):  # arm
		c.put(x, 7, iron[2])
		c.put(x, 6, iron[1])
	c.put(11, 8, iron[1])
	# Lantern frame and warm glass.
	for y in range(9, 18):
		for x in range(9, 14):
			edge = x in (9, 13) or y in (9, 17)
			c.put(x, y, iron[1] if edge else (EMBER[3] if (x == 11 and 11 <= y <= 14) else EMBER[2]))
	c.put(11, 8, iron[2])
	c.put(11, 18, iron[1])
	for x in range(9, 14):
		c.put(x, 9, iron[2])
	c.put(10, 10, EMBER[3])
	return c


def brazier():
	"""14x24 stone pedestal with an iron bowl; the flame is a separate animated prop.
	Origin bottom-centre (7, 24); the bowl rim is at y=9."""
	c = Canvas(14, 24)
	for y in range(13, 24):
		half = 3 if y < 20 else 5
		for x in range(7 - half, 7 + half):
			k = 3 if x == 7 - half else 1 if x == 7 + half - 1 else 2
			c.put(x, y, STONE[k + 1] if y > 13 else STONE[4])
	for x in range(1, 13):
		c.put(x, 23, STONE[0])
	for x in range(2, 12):
		c.put(x, 12, STEEL[0])
		c.put(x, 11, STEEL[1])
	for x in range(3, 11):
		c.put(x, 10, STEEL[1])
		c.put(x, 9, EMBER[0])
	c.put(2, 9, STEEL[2])
	c.put(11, 9, STEEL[1])
	return c


def sconce():
	"""8x14 wall sconce with torch head. Origin bottom-centre (4, 14); flame sits above."""
	c = Canvas(8, 14)
	for y in range(3, 14):
		c.put(3, y, WOOD[2] if y < 10 else STEEL[1])
		c.put(4, y, WOOD[1] if y < 10 else STEEL[0])
	for x in range(1, 7):
		c.put(x, 3, STEEL[1])
		c.put(x, 4, STEEL[0])
	for x in range(2, 6):
		c.put(x, 2, WOOD[0])
	c.put(1, 2, STEEL[1])
	c.put(6, 2, STEEL[1])
	return c


def chain_lantern():
	"""8x40 chain hanging from an overhang to a small lantern. Origin top-centre (4, 0)."""
	c = Canvas(8, 40)
	for y in range(0, 26):
		c.put(3 + (y % 2), y, STEEL[1] if y % 2 else STEEL[2])
	for y in range(26, 37):
		for x in range(1, 7):
			edge = x in (1, 6) or y in (26, 36)
			c.put(x, y, STEEL[0] if edge else EMBER[2])
	for y in range(28, 33):
		c.put(3, y, EMBER[3])
		c.put(4, y, EMBER[3] if y < 31 else EMBER[2])
	c.put(3, 37, STEEL[0])
	c.put(4, 37, STEEL[0])
	return c


# ------------------------------------------------------------------ graves, fences, litter
def gravestone(kind):
	"""16x22 grave marker. Origin bottom-centre (8, 22)."""
	c = Canvas(16, 22)
	r = rng("grave", kind)
	s = STONE
	if kind == 0:  # rounded headstone
		for y in range(3, 22):
			half = 5 if y > 6 else int(5 * math.sqrt(max(0.0, 1 - ((6 - y) / 4.0) ** 2)))
			for x in range(8 - half, 8 + half):
				k = 4 if x == 8 - half or y == 3 else 1 if x == 8 + half - 1 else 3 if (x * 5 + y) % 9 else 2
				c.put(x, y, s[k])
		for y in range(9, 13):  # engraved cross
			c.put(8, y, s[0])
		c.put(7, 10, s[0])
		c.put(9, 10, s[0])
	elif kind == 1:  # leaning cross
		for y in range(2, 22):
			for x in (7, 8):
				c.put(x + (1 if y < 10 else 0), y, s[3] if x == 7 else s[1])
		for x in range(4, 12):
			c.put(x + 1, 8, s[3])
			c.put(x + 1, 9, s[1])
	else:  # broken slab with a chip missing
		for y in range(8, 22):
			for x in range(3, 13):
				if y < 11 and x > 8 + (11 - y):
					continue
				k = 4 if y == 8 or x == 3 else 1 if x == 12 else 3 if (x + y) % 5 else 2
				c.put(x, y, s[k])
		for i in range(5):
			c.put(5 + i, 13 + i % 2, s[0])
	for x in range(2, 14):  # mound at the foot
		c.put(x, 21, MOSS[0] if x % 3 else s[0])
		if r.random() < 0.7:
			c.put(x, 20, MOSS[1])
	for _ in range(3):
		c.put(r.randint(4, 11), 19, MOSS[2])
	return c


def fence():
	"""44x18 broken wooden fence. Origin bottom-centre (22, 18)."""
	c = Canvas(44, 18)
	r = rng("fence")
	for i, x in enumerate(range(2, 43, 8)):
		h = r.choice((18, 16, 12, 17)) if i not in (2,) else 8
		for y in range(18 - h, 18):
			c.put(x, y, WOOD[3] if y == 18 - h else WOOD[2])
			c.put(x + 1, y, WOOD[1])
			c.put(x + 2, y, WOOD[0])
		c.put(x, 18 - h, WOOD[4])
	for y in (6, 12):
		for x in range(0, 44):
			if r.random() < 0.9 and not 20 < x < 25:
				c.put(x, y, WOOD[1])
				c.put(x, y + 1, WOOD[0])
	return c


def bush(corrupt):
	"""28x16 shrub. Origin bottom-centre (14, 16)."""
	c = Canvas(28, 16)
	r = rng("bush", corrupt)
	ramp = [CORRUPT[0], CORRUPT[1], CORRUPT[2], CORRUPT[3]] if corrupt else [hexc("141b17"), hexc("1c2822"), hexc("26352c"), hexc("33473a")]
	for bx, by, br in ((14, 11, 7), (8, 12, 5), (20, 12, 5), (12, 8, 4)):
		for y in range(by - br, by + br):
			for x in range(bx - br, bx + br):
				d = math.hypot(x - bx, (y - by) * 1.2)
				if d < br - r.random() * 1.2 and y < 16:
					lit = (x - bx) + (y - by) < -br * 0.3
					k = 3 if lit and d < br - 2 else 2 if d < br - 1.5 else 1
					c.put(x, y, ramp[k] if (x * 3 + y * 7) % 11 else ramp[0])
	for _ in range(9):  # twigs poking out
		x, y = r.randint(5, 22), r.randint(3, 8)
		for i in range(r.randint(2, 4)):
			c.put(x + i * r.choice((-1, 1)) // 2, y - i, ramp[1])
	if corrupt:
		for _ in range(4):
			c.put(r.randint(7, 21), r.randint(5, 12), CORRUPT[4])
	return c


def rubble():
	"""28x10 fallen masonry. Origin bottom-centre (14, 10)."""
	c = Canvas(28, 10)
	r = rng("rubble")
	for bx, bw, bh in ((1, 9, 5), (9, 8, 7), (17, 10, 4), (6, 6, 4), (21, 5, 6)):
		for y in range(10 - bh, 10):
			for x in range(bx, bx + bw):
				k = 4 if y == 10 - bh else 0 if y == 9 or x == bx + bw - 1 else 3 if x == bx else 2 if (x + y) % 4 else 1
				c.put(x, y, STONE[k])
	for _ in range(3):
		c.put(r.randint(2, 24), 9, MOSS[1])
	for x in range(2, 26, 3):
		c.put(x, 9, MOSS[0])
	return c


def bones():
	"""22x10 skull and ribs. Origin bottom-centre (11, 10)."""
	c = Canvas(22, 10)
	for y in range(2, 8):
		for x in range(2, 9):
			d = math.hypot(x - 5, (y - 4.5) * 1.1)
			if d < 3.4:
				c.put(x, y, BONE[2] if x < 5 else BONE[1])
	for x, y in ((3, 5), (6, 5)):
		c.put(x, y, hexc("17131b"))
	c.put(4, 7, hexc("17131b"))
	c.put(5, 7, BONE[0])
	for i in range(4):  # ribs
		for x in range(11 + i * 3, 14 + i * 3):
			c.put(x, 7 - (1 if x % 2 else 0) - (i % 2), BONE[2] if x % 2 else BONE[1])
	for x in range(10, 20):
		c.put(x, 8, BONE[0])
	c.put(1, 8, BONE[1])
	c.put(2, 8, BONE[2])
	c.put(9, 8, BONE[1])
	c.put(20, 8, BONE[2])
	for x in range(0, 22):
		c.put(x, 9, hexc("1c1a21"))
	return c


def ruin_wall():
	"""56x32 mossy broken wall stub. Origin bottom-centre (28, 32)."""
	c = Canvas(56, 32)
	r = rng("ruinwall")
	s = [mix(v, hexc("14181e"), 0.1) for v in STONE]
	masonry_rect(c, 0, 0, 56, 32, s, r, course=7, moss=MOSS)
	# Re-cut the silhouette (masonry_rect fills a rectangle).
	for x in range(0, 56):
		top = 8 if 10 < x < 30 else (18 if x < 6 else 12 + (x * 7) % 5 + max(0, (x - 34)) // 3)
		for y in range(0, min(top, 32)):
			c.px[y * 56 + x] = None
	# Window opening.
	for y in range(12, 24):
		for x in range(15, 22):
			if not (y < 15 and (x < 16 or x > 20)):
				c.px[y * 56 + x] = hexc("14181e")
	for x in range(0, 56):
		for y in range(0, 32):
			if c.get(x, y) is not None and c.get(x, y - 1) is None:
				c.put(x, y, s[4])
				if r.random() < 0.4:
					c.put(x, y, MOSS[2])
	return c


def shrine():
	"""30x40 roadside shrine with a candle. Origin bottom-centre (15, 40)."""
	c = Canvas(30, 40)
	r = rng("shrine")
	s = STONE
	masonry_rect(c, 3, 30, 24, 10, s, r, course=5, moss=MOSS)
	masonry_rect(c, 6, 22, 18, 8, s, r, course=4, moss=MOSS)
	# Niche pedestal.
	for y in range(8, 22):
		for x in range(8, 22):
			k = 4 if x == 8 else 1 if x == 21 else 2
			c.put(x, y, s[k] if (x + y) % 9 else s[1])
	for y in range(11, 21):  # dark arched niche
		half = 4 if y > 14 else 2 + (y - 11)
		for x in range(15 - half, 15 + half):
			c.put(x, y, hexc("14111a"))
	# Roof slab and moss.
	for x in range(5, 25):
		c.put(x, 6, s[0])
		c.put(x, 7, s[4])
		c.put(x, 5, s[3])
	for x in range(8, 22):
		c.put(x, 4, s[3])
		c.put(x, 3, s[2])
	for x in range(11, 19):
		c.put(x, 2, s[3])
	c.put(15, 0, s[4])
	c.put(15, 1, s[3])
	for x in range(6, 22, 2):
		c.put(x, 5, MOSS[2])
	# Candle with a small warm flame (sparse accent) and a scrap of cloth.
	for y in range(16, 20):
		c.put(15, y, BONE[3])
	c.put(15, 15, EMBER[3])
	c.put(15, 14, EMBER[2])
	c.put(14, 15, EMBER[0])
	c.put(16, 15, EMBER[0])
	for y in range(22, 27):
		c.put(8 + (y - 22) // 3, y, CLOTH[2])
		c.put(9 + (y - 22) // 3, y, CLOTH[1])
	return c


def gallows():
	"""48x72 gallows with a noose. Origin bottom-centre (24, 72)."""
	c = Canvas(48, 72)
	for y in range(6, 72):
		for x in (8, 9, 10):
			c.put(x, y, WOOD[2] if x == 8 else WOOD[1] if x == 9 else WOOD[0])
	for x in range(6, 44):  # beam
		c.put(x, 4, WOOD[3] if x % 7 else WOOD[2])
		c.put(x, 5, WOOD[1])
		c.put(x, 6, WOOD[0])
	for i in range(10):  # brace
		c.put(11 + i, 7 + i, WOOD[1])
		c.put(11 + i, 8 + i, WOOD[0])
	for x in range(2, 20):  # platform
		c.put(x, 66, WOOD[3] if x % 5 else WOOD[2])
		c.put(x, 67, WOOD[1])
		c.put(x, 68, WOOD[0])
	for y in range(5, 22):  # rope and noose
		c.put(36, y, hexc("7a6a4a"))
	for dx, dy in ((-2, 22), (-1, 22), (0, 22), (1, 22), (2, 22), (-2, 23), (2, 23), (-2, 24), (2, 24), (-1, 25), (0, 25), (1, 25)):
		c.put(36 + dx, dy, hexc("7a6a4a"))
	return c


def crow():
	"""9x9 perched crow, origin bottom-centre (4, 9)."""
	c = Canvas(9, 9)
	dark, mid = hexc("14121a"), hexc("2a2832")
	for x, y in ((3, 2), (4, 2), (2, 3), (3, 3), (4, 3), (5, 3), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (4, 6), (5, 6), (6, 6), (8, 6)):
		c.put(x, y, mid if (x + y) % 3 else dark)
	c.put(1, 3, hexc("5a5240"))
	c.put(2, 2, dark)
	c.put(3, 2, dark)
	c.put(3, 7, dark)
	c.put(5, 7, dark)
	return c


def banner_hang():
	"""20x48 tattered banner hanging from a rod. Origin top-centre (10, 0)."""
	c = Canvas(20, 48)
	for x in range(0, 20):
		c.put(x, 0, WOOD[1])
		c.put(x, 1, WOOD[0])
	c.put(0, 0, GOLD[1])
	c.put(19, 0, GOLD[1])
	r = rng("hang")
	for y in range(2, 46):
		for x in range(2, 18):
			tear = y > 36 and (x * 5 + y) % 6 < (y - 36) // 2
			if tear:
				continue
			col = CLOTH[2] if x < 5 else CLOTH[1] if (x + y // 3) % 6 else CLOTH[0]
			if x == 17 or y == 2:
				col = CLOTH[0]
			c.put(x, y, col)
	# Faded sigil: a cross-hilted sword in desaturated gold-brown.
	sig = hexc("8a6a3a")
	for y in range(12, 28):
		c.put(10, y, sig)
	for x in range(7, 14):
		c.put(x, 16, sig)
	c.put(10, 11, hexc("a8884e"))
	for y in range(28, 30):
		c.put(9, y, sig)
		c.put(11, y, sig)
	return c


def roots():
	"""36x16 twisted blighted roots. Origin bottom-centre (18, 16)."""
	c = Canvas(36, 16)
	r = rng("roots")
	for base in (6, 16, 27):
		x, y = float(base), 15.0
		ang = r.uniform(-2.2, -0.9)
		for i in range(r.randint(12, 20)):
			x += math.cos(ang) * 1.0
			y += math.sin(ang) * 0.9
			ang += r.uniform(-0.35, 0.35)
			xi, yi = int(round(x)), int(round(y))
			c.put(xi, yi, CORRUPT[1] if i % 3 else CORRUPT[2])
			c.put(xi + 1, yi, CORRUPT[0])
		c.put(int(round(x)), int(round(y)), CORRUPT[4])
	for x in range(0, 36):
		if c.get(x, 15) is None and x % 2 == 0:
			c.put(x, 15, CORRUPT[0])
	return c


def pod():
	"""12x12 corruption pods. Origin bottom-centre (6, 12)."""
	c = Canvas(12, 12)
	for cx, cy, rad in ((4, 8, 3.5), (9, 9, 2.5), (6, 5, 3.0)):
		for y in range(12):
			for x in range(12):
				d = math.hypot(x - cx, (y - cy) * 1.1)
				if d < rad:
					lit = (x - cx) + (y - cy) < 0
					c.put(x, y, CORRUPT[3] if lit and d < rad - 1 else CORRUPT[2] if d < rad - 0.6 else CORRUPT[1])
	c.put(5, 4, CORRUPT[4])
	c.put(3, 7, CORRUPT[4])
	for x in range(0, 12):
		c.put(x, 11, CORRUPT[0])
	return c


PROPS = {
	"prop_pillar_a": lambda: pillar(False), "prop_pillar_b": lambda: pillar(True),
	"prop_lantern_post": lantern_post, "prop_brazier": brazier, "prop_sconce": sconce,
	"prop_chain_lantern": chain_lantern, "prop_flame": flame_sheet, "prop_glow": glow,
	"prop_grave_a": lambda: gravestone(0), "prop_grave_b": lambda: gravestone(1), "prop_grave_c": lambda: gravestone(2),
	"prop_fence": fence, "prop_bush": lambda: bush(False), "prop_bush_corrupt": lambda: bush(True),
	"prop_rubble": rubble, "prop_bones": bones, "prop_ruin_wall": ruin_wall, "prop_shrine": shrine,
	"prop_gallows": gallows, "prop_crow": crow, "prop_banner_hang": banner_hang,
	"prop_roots": roots, "prop_pod": pod,
}

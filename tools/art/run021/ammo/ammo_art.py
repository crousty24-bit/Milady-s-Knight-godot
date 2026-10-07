"""RUN-021 ammo art: destructible crate/barrel per ammo family, destruction strips, ground pickups, HUD icons, pickup VFX.

Usage: python3 tools/art/run021/ammo/ammo_art.py [--preview DIR]

Outputs (assets/run021/ammo/, horizontal strips, frames left -> right, all frames the same size):
  prop_{crate,barrel}_{arrows,knives}.png        32x32   1 frame, intact, origin bottom-centre (16, 32)
  prop_{crate,barrel}_{arrows,knives}_break.png  192x32  6 frames of 32x32, 12 fps once, origin bottom-centre (16, 32);
                                                         0 flash/crack, 1-4 burst, 5 low residue (<= 5 px high)
  pickup_arrows.png, pickup_knives.png           64x16   4 frames of 16x16, 6 fps loop (glint), centre (8, 8); rests on row 15
  vfx_ammo_pickup.png                            80x16   5 frames of 16x16, 15 fps once, centre (8, 8)
  ui_ammo_icons.png                              48x12   4 frames of 12x12: arrows, knives, arrows empty, knives empty
  ammo_{crate,barrel}_frames.tres                SpriteFrames: intact_/break_{arrows,knives} (break 12 fps, no loop)
  ammo_pickup_frames.tres                        SpriteFrames: arrows, knives (6 fps loop), collect (15 fps once)

Family marker: contents poking out of the top (arrows with red fletching like proj_arrow.png / knife hilts and
blades like proj_knife.png) plus a pale neutral tag with the family glyph on the front. The break strips never show
ammo flying out (a prop may drop nothing): contents vanish in the burst, only wood/steel debris and dust remain.

Original art drawn by code from tools/art/palette.py; deterministic (seeded). No third-party pixel, no AI image.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ART)
from pixel import Canvas, line, outline, save_png, sheet  # noqa: E402
from palette import BLOOD, GOLD, OUTLINE, STEEL, STONE, WOOD  # noqa: E402

ROOT = os.path.normpath(os.path.join(ART, "..", ".."))
OUT = os.path.join(ROOT, "assets", "run021", "ammo")
BG = (22, 24, 31, 255)  # same preview bed as tools/art/items.py
WHITE = (255, 255, 255, 255)
# Pale parchment tag: neutral interaction (pale yellow) per Art Bible functional colours, darker than coin gold.
TAG = [(104, 90, 66, 255), (170, 152, 112, 255), (222, 208, 166, 255)]
PALE = (238, 230, 196, 255)
SHADOW = (8, 8, 12, 110)
FAMILIES = ("arrows", "knives")
KINDS = ("crate", "barrel")


def a(color, alpha):
	return (color[0], color[1], color[2], alpha)


def lerp(c0, c1, t):
	return tuple(int(round(c0[i] + (c1[i] - c0[i]) * t)) for i in range(3)) + (c0[3],)


# ------------------------------------------------------------------ glyphs
GLYPH_ARROWS = (
	"R...s.",
	"RDDDSS",
	"R...s.",
)
GLYPH_KNIVES = (
	"..c...",
	"DDcSSs",
	"..c...",
)
GLYPH_PAL = {"R": BLOOD[3], "D": WOOD[1], "S": STEEL[2], "s": STEEL[1], "c": STEEL[1]}


def tag(c, family, x0, y0):
	"""8x5 pale tag (outline included) with a 6x3 family glyph."""
	for y in range(5):
		for x in range(8):
			edge = x in (0, 7) or y in (0, 4)
			col = TAG[0] if edge else (TAG[1] if (x == 6 or y == 3) else TAG[2])
			c.put(x0 + x, y0 + y, col)
	rows = GLYPH_ARROWS if family == "arrows" else GLYPH_KNIVES
	for y, row in enumerate(rows):
		for x, ch in enumerate(row):
			if ch in GLYPH_PAL:
				c.put(x0 + 1 + x, y0 + 1 + y, GLYPH_PAL[ch])


# --------------------------------------------------------------- contents
def contents(family, spots):
	"""Ammo poking out of the top. spots: (x_base, x_top, top_y); bases are hidden behind the body rim."""
	c = Canvas(32, 32)
	for i, (xb, xt, ty) in enumerate(spots):
		if family == "arrows":
			# shaft from the rim up to the fletching, nock on top, red vanes either side (as proj_arrow.png)
			base_y = 16
			for y in range(ty + 1, base_y + 1):
				t = (y - (ty + 1)) / max(1, base_y - (ty + 1))
				x = int(round(xt + (xb - xt) * t))
				c.put(x, y, WOOD[4] if y > ty + 3 else WOOD[3])
			c.put(xt, ty, STEEL[4])
			for y in range(ty + 1, ty + 4):
				c.put(xt - 1, y, BLOOD[3] if y < ty + 3 else BLOOD[2])
				c.put(xt + 1, y, BLOOD[2] if y < ty + 3 else BLOOD[1])
		else:
			if i % 2 == 0:
				# hilt up: steel pommel, wood grip, cross-guard (blade hidden in the container)
				c.put(xt, ty, STEEL[3])
				for y in range(ty + 1, ty + 4):
					c.put(xt, y, WOOD[3] if y % 2 else WOOD[2])
				for x, col in ((xt - 1, STEEL[3]), (xt, STEEL[2]), (xt + 1, STEEL[1])):
					c.put(x, ty + 4, col)
				for y in range(ty + 5, 17):
					c.put(xt, y, STEEL[1])
			else:
				# blade up: 2 px kite blade with a bright edge and a white tip (as proj_knife.png)
				c.put(xt, ty, WHITE)
				for y in range(ty + 1, 17):
					c.put(xt, y, STEEL[4] if y < ty + 5 else STEEL[3])
					c.put(xt + 1, y, STEEL[2] if y > ty + 1 else None)
	return outline(c, OUTLINE)


SPOTS = {
	("crate", "arrows"): ((10, 9, 6), (13, 13, 4), (18, 19, 5), (22, 23, 8)),
	("crate", "knives"): ((10, 10, 8), (13, 13, 5), (18, 18, 7), (21, 22, 6)),
	("barrel", "arrows"): ((11, 10, 6), (14, 14, 3), (18, 19, 5), (21, 22, 8)),
	("barrel", "knives"): ((11, 11, 7), (14, 14, 4), (18, 18, 6), (20, 21, 6)),
}


# ------------------------------------------------------------------ bodies
def crate_body():
	"""20x17 nailed crate (outline -> 22x19), rows 13..31: frame boards, diagonal brace, iron corners."""
	c = Canvas(32, 32)
	X0, X1, Y0, Y1 = 6, 25, 14, 30
	for y in range(Y0, Y1 + 1):
		for x in range(X0, X1 + 1):
			col = WOOD[1] if (y - Y0) % 4 == 3 else WOOD[2]
			if x > X1 - 4 and col == WOOD[2]:
				col = WOOD[2] if (x + y) % 5 else WOOD[1]
			c.put(x, y, col)
	# diagonal brace bottom-left -> top-right inside the frame
	for x in range(X0 + 2, X1 - 1):
		t = (x - (X0 + 2)) / float(X1 - 2 - (X0 + 2))
		y = int(round((Y1 - 2) - t * ((Y1 - 2) - (Y0 + 2))))
		c.put(x, y, WOOD[3])
		c.put(x, y - 1, WOOD[3])
		c.put(x, y + 1, WOOD[0])
	# frame boards
	for y in range(Y0, Y1 + 1):
		for x in range(X0, X1 + 1):
			top, bot = y in (Y0, Y0 + 1), y in (Y1 - 1, Y1)
			left, right = x in (X0, X0 + 1), x in (X1 - 1, X1)
			if not (top or bot or left or right):
				continue
			col = WOOD[3]
			if y == Y0 or (x == X0 and not bot):
				col = WOOD[4]
			elif y == Y1 or x == X1:
				col = WOOD[1]
			elif right or bot:
				col = WOOD[2]
			c.put(x, y, col)
	# iron corner brackets with rivets
	for cx, cy, sx, sy in ((X0, Y0, 1, 1), (X1, Y0, -1, 1), (X0, Y1, 1, -1), (X1, Y1, -1, -1)):
		lit = sx > 0 and sy > 0
		col = STEEL[2] if lit else STEEL[1]
		for k in range(3):
			c.put(cx + sx * k, cy, col)
			c.put(cx, cy + sy * k, col)
		c.put(cx + sx, cy + sy, STEEL[4] if lit else STEEL[3])
	return c


def barrel_body():
	"""Bulged barrel, 16..20 px wide, rows 12..31 with outline: vertical staves, three steel hoops."""
	c = Canvas(32, 32)
	Y0, Y1 = 13, 30
	cx = 16.0
	for y in range(Y0, Y1 + 1):
		hw = 8.0 + 2.0 * math.sin(math.pi * (y - Y0 + 0.5) / (Y1 - Y0 + 1))
		for x in range(32):
			u = (x + 0.5 - cx) / hw
			if abs(u) > 1.0:
				continue
			col = WOOD[3] if u < -0.55 else WOOD[2] if u < 0.35 else WOOD[1]
			if u < -0.85:
				col = WOOD[4] if y not in (Y0, Y1) else WOOD[3]
			for seam in (-0.5, -0.05, 0.4):
				if abs(u - seam) < 0.5 / hw:
					col = WOOD[1] if seam < 0 else WOOD[0]
			c.put(x, y, col)
	# rim lip
	for x in range(32):
		if c.get(x, Y0) is not None:
			c.put(x, Y0, WOOD[4] if x < 16 else WOOD[3])
	# hoops
	for hy in (15, 22, 28):
		for x in range(32):
			if c.get(x, hy) is None:
				continue
			u = (x + 0.5 - cx) / 10.0
			c.put(x, hy, STEEL[3] if u < -0.45 else STEEL[2] if u < 0.3 else STEEL[1])
			c.put(x, hy + 1, STEEL[1] if u < 0.3 else STEEL[0])
	c.put(9, 15, STEEL[4])
	return c


BODY_TAG = {"crate": (12, 19), "barrel": (12, 17)}


def body_layer(kind, family):
	body = crate_body() if kind == "crate" else barrel_body()
	x0, y0 = BODY_TAG[kind]
	tag(body, family, x0, y0)
	return outline(body, OUTLINE)


def intact(kind, family):
	c = contents(family, SPOTS[(kind, family)])
	c.blit(body_layer(kind, family), 0, 0)
	return c


# ------------------------------------------------------------------- break
def chunks_of(src, cw, ch, rng):
	"""Cut the opaque pixels of src into cells -> list of (pixels {(dx,dy): col}, cx, cy, vx, vy)."""
	bb = src.bbox()
	out = []
	for gy in range(bb[1], bb[3], ch):
		shift = (cw // 2) if ((gy - bb[1]) // ch) % 2 else 0  # staggered like brickwork, not a grid
		for gx in range(bb[0] - shift, bb[2], cw):
			pix = {}
			for y in range(gy, min(gy + ch, bb[3])):
				for x in range(gx, min(gx + cw, bb[2])):
					p = src.get(x, y)
					if p is not None:
						pix[(x - gx, y - gy)] = p
			if len(pix) < 4:
				continue
			ccx, ccy = gx + cw / 2.0, gy + ch / 2.0
			vx = (ccx - 16.0) * 0.5 + rng.uniform(-0.9, 0.9)
			vy = -(2.0 + rng.uniform(0.0, 2.0)) - (31 - ccy) * 0.1
			out.append((pix, gx, gy, vx, vy))
	return out


def flash(src):
	c = src.copy()
	c.px = [None if p is None else (p if p[:3] == OUTLINE[:3] else lerp(p, PALE, 0.4)) for p in c.px]
	return c


def residue(kind, rng):
	"""Low debris lying on the floor (rows 27..31), non-interactive."""
	c = Canvas(32, 32)
	pieces = [(7, 30, 5, WOOD[2]), (14, 29, 6, WOOD[3]), (21, 30, 4, WOOD[1]), (11, 31, 9, WOOD[1])]
	for x0, y, ln, col in pieces:
		for x in range(x0, x0 + ln):
			c.put(x, y, col)
		c.put(x0, y, WOOD[3] if col != WOOD[3] else WOOD[4])
	if kind == "barrel":
		for x in range(18, 24):
			c.put(x, 28 if x in (19, 20, 21, 22) else 29, STEEL[2] if x < 21 else STEEL[1])
	else:
		c.put(16, 28, STEEL[2])
		c.put(17, 28, STEEL[1])
	return outline(c, OUTLINE)


def dust(c, i):
	if i < 1 or i > 4:
		return
	t = i - 1
	alpha = (210, 170, 120, 70)[t]
	for k, side in enumerate((-1, 1, -1, 1, -1, 1)):
		r = 4 + t * (2.4 + k * 0.4)
		x = int(round(16 + side * r))
		y = 30 - (k % 3) - (t // 2)
		col = a(STONE[5] if k % 2 else STONE[4], alpha)
		c.rect(x - 1, y - 1, 2, 2, col)
	# puff where the contents vanished
	if i <= 2:
		for (dx, dy) in ((0, 0), (-3, 1), (3, 1), (-1, -2), (2, -2), (-5, 3), (5, 3)):
			c.put(16 + dx * i, 11 + dy - i, a(PALE if i == 1 else STONE[5], 190 if i == 1 else 110))


def break_frames(kind, family):
	rng = random.Random("ammo-break-%s-%s" % (kind, family))
	whole = intact(kind, family)
	body = body_layer(kind, family)
	frames = []
	# 0: flash + crack, contents still visible
	f0 = flash(whole)
	crack = [(16, 14), (16, 15), (15, 16), (15, 17), (16, 18), (17, 25), (17, 26), (18, 27), (18, 28), (19, 29),
		(10, 26), (11, 27), (11, 28), (22, 15), (21, 16)]
	for (x, y) in crack:
		if f0.get(x, y) is not None:
			f0.put(x, y, OUTLINE)
	frames.append(f0)
	chunks = chunks_of(body, 6, 5, rng)
	splinters = [(rng.uniform(-3.4, 3.4), rng.uniform(-4.4, -2.2), WOOD[4] if k % 2 else WOOD[3]) for k in range(8)]
	for i in range(1, 5):
		c = Canvas(32, 32)
		dust(c, i)
		t = float(i)
		for n, (pix, gx, gy, vx, vy) in enumerate(chunks):
			ox = vx * t * 1.4
			oy = vy * t + 0.8 * t * t
			maxy = max(dy for (_, dy) in pix)
			oy = min(oy, 31 - (gy + maxy))  # land on the floor
			keep = (1.0, 1.0, 0.8, 0.5, 0.25)[i]
			for (dx, dy), col in pix.items():
				h = ((gx + dx) * 73856093 ^ (gy + dy) * 19349663 ^ n * 83492791) % 1000 / 1000.0
				if h > keep:
					continue
				c.put(int(round(gx + dx + ox)), int(round(gy + dy + oy)), col)
		for sx, sy, col in splinters:
			if i > 3:
				continue
			x = 16 + sx * t * 2.2
			y = 20 + sy * t + 1.1 * t * t
			c.put(int(round(x)), int(round(y)), col)
			c.put(int(round(x + (1 if sx > 0 else -1))), int(round(y)), WOOD[1])
		frames.append(c)
	frames.append(residue(kind, rng))
	return frames


# ----------------------------------------------------------------- pickups
def diag(c, x0, y0, n, col):
	for k in range(n):
		c.put(x0 + k, y0 - k, col)


def pickup_arrows_base():
	"""Three arrows fanned from a tied fletching end (bottom-left) towards the heads (top-right), pale cord."""
	c = Canvas(16, 16)
	shafts = (((3, 12), (13, 4)), ((3, 12), (11, 2)), ((3, 12), (7, 1)))
	for k, ((x0, y0), (x1, y1)) in enumerate(shafts):
		line(c, x0, y0, x1, y1, WOOD[4] if k != 1 else WOOD[3])
		dx, dy = (x1 - x0), (y1 - y0)
		n = max(abs(dx), abs(dy))
		c.put(x1, y1, STEEL[4])  # head: bright tip + one steel pixel behind it
		c.put(int(round(x1 - dx / n)), int(round(y1 - dy / n)), STEEL[2])
	for (x, y, col) in ((2, 12, BLOOD[3]), (3, 13, BLOOD[2]), (2, 13, BLOOD[1]), (1, 13, BLOOD[2]), (2, 14, BLOOD[1]),
			(4, 13, BLOOD[2]), (1, 12, BLOOD[3])):
		c.put(x, y, col)  # gathered red vanes
	for (x, y) in ((4, 10), (5, 11), (6, 11)):
		c.put(x, y, TAG[2] if x < 6 else TAG[1])  # cord
	return outline(c, OUTLINE)


def knife_diag(c, flip):
	"""Grip bottom-left, guard, 2 px blade to the top-right; mirrored when flip."""
	def p(x, y, col):
		c.put(15 - x if flip else x, y, col)
	for k in range(3):
		p(3 + k, 13 - k, WOOD[3] if k != 1 else WOOD[2])
	p(2, 14, STEEL[2])  # pommel
	for (x, y) in ((5, 10), (6, 11), (7, 12)):
		p(x, y, STEEL[2])
	p(5, 10, STEEL[3])
	for k in range(5):
		p(7 + k, 10 - k, STEEL[4])
		p(7 + k, 11 - k, STEEL[2])
	p(12, 5, STEEL[3])
	p(12, 4, WHITE)


def pickup_knives_base():
	"""Two throwing knives crossed in an X (blades up)."""
	c = Canvas(16, 16)
	knife_diag(c, True)
	knife_diag(c, False)
	return outline(c, OUTLINE)


def glint_frames(base, tips):
	frames = []
	for i in range(4):
		c = Canvas(16, 16)
		for x in range(3, 13):  # contact shadow, behind
			c.put(x, 15, SHADOW if 4 <= x <= 11 else a(SHADOW, 60))
		c.blit(base, 0, 0)
		if i == 1:
			for (x, y) in tips:
				c.put(x, y, WHITE)
		elif i == 2:
			x, y = tips[0]
			for (dx, dy) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
				c.put(x + dx, y + dy, a(PALE, 200))
			c.put(x, y, WHITE)
		frames.append(c)
	return frames


def vfx_pickup():
	frames = []
	cols = [WHITE, PALE, STEEL[4], STEEL[3], a(STEEL[3], 120)]
	for i in range(5):
		c = Canvas(16, 16)
		col = cols[i]
		if i == 0:
			c.rect(7, 7, 2, 2, WHITE)
			for d in (-2, 2):
				c.put(8 + d, 8, PALE)
				c.put(8, 8 + d, PALE)
		r = 2.0 + i * 1.6
		for k in range(16 if i < 3 else 8):
			if i >= 2 and k % 2:
				continue
			ang = k * math.tau / 16
			c.put(int(round(8 + math.cos(ang) * r)), int(round(8 + math.sin(ang) * r)), col)
		for k, mx in enumerate((5, 8, 11)):  # rising motes
			y = 9 - i * 1.6 - (k % 2) * 2
			if i >= 1:
				c.put(mx, int(round(y)), a(PALE, (255, 230, 180, 110, 60)[i]))
		frames.append(c)
	return frames


# --------------------------------------------------------------- HUD icons
def ui_arrows():
	"""12x12, two thin parallel arrows on the 45 degree diagonal (like ui_weapon_icons), no outline."""
	c = Canvas(12, 12)
	for sx, sy in ((1, 8), (3, 10)):
		diag(c, sx, sy, 6, WOOD[4])
		ex, ey = sx + 5, sy - 5
		c.put(ex + 1, ey - 1, STEEL[4])
		c.put(ex, ey - 1, STEEL[3])
		c.put(ex + 1, ey, STEEL[3])
		c.put(sx - 1, sy, BLOOD[3])
		c.put(sx, sy + 1, BLOOD[3])
		c.put(sx - 1, sy + 1, BLOOD[2])
	return c


def ui_knives():
	"""12x12, two throwing knives crossed (blades up), no outline."""
	c = Canvas(12, 12)
	for flip in (True, False):
		def p(x, y, col):
			c.put(11 - x if flip else x, y, col)
		p(1, 11, STEEL[2])
		p(2, 10, WOOD[3])
		p(3, 9, WOOD[2])
		p(3, 8, STEEL[3])
		p(4, 9, STEEL[2])
		for k in range(4):
			p(4 + k, 8 - k, STEEL[4])
			p(5 + k, 8 - k, STEEL[2])
		p(8, 4, WHITE)
	return c


def empty_variant(src):
	"""Dark grey, like the empty heart / spent coin of ui_icons.png."""
	c = src.copy()
	out = []
	for p in c.px:
		if p is None:
			out.append(None)
			continue
		lum = (p[0] * 0.3 + p[1] * 0.59 + p[2] * 0.11) / 255.0
		g = STONE[2] if lum < 0.35 else STONE[3] if lum < 0.6 else STONE[4]
		out.append(g)
	c.px = out
	return c


# -------------------------------------------------------------------- build
EXPECTED = {}


def build():
	out = {}
	for kind in KINDS:
		for fam in FAMILIES:
			out["prop_%s_%s.png" % (kind, fam)] = sheet([intact(kind, fam)], 1)
			EXPECTED["prop_%s_%s.png" % (kind, fam)] = (32, 32, 1)
			out["prop_%s_%s_break.png" % (kind, fam)] = sheet(break_frames(kind, fam), 6)
			EXPECTED["prop_%s_%s_break.png" % (kind, fam)] = (32, 32, 6)
	out["pickup_arrows.png"] = sheet(glint_frames(pickup_arrows_base(), [(11, 2), (13, 4), (7, 1)]), 4)
	out["pickup_knives.png"] = sheet(glint_frames(pickup_knives_base(), [(12, 4), (3, 4)]), 4)
	out["vfx_ammo_pickup.png"] = sheet(vfx_pickup(), 5)
	ar, kn = ui_arrows(), ui_knives()
	out["ui_ammo_icons.png"] = sheet([ar, kn, empty_variant(ar), empty_variant(kn)], 4)
	EXPECTED.update({"pickup_arrows.png": (16, 16, 4), "pickup_knives.png": (16, 16, 4),
		"vfx_ammo_pickup.png": (16, 16, 5), "ui_ammo_icons.png": (12, 12, 4)})
	return out


# ------------------------------------------------------------ SpriteFrames
# Animation names follow scripts/ammo_prop.gd (`intact_<family>`, `break_<family>`, family suffix arrows|knives)
# and the pickup's per-family children. Paths only (no uid): Godot assigns uids on its next import.
FRAMES = {
	"ammo_crate_frames.tres": [
		("intact_arrows", "prop_crate_arrows.png", 32, 1, 1.0, False),
		("intact_knives", "prop_crate_knives.png", 32, 1, 1.0, False),
		("break_arrows", "prop_crate_arrows_break.png", 32, 6, 12.0, False),
		("break_knives", "prop_crate_knives_break.png", 32, 6, 12.0, False),
	],
	"ammo_barrel_frames.tres": [
		("intact_arrows", "prop_barrel_arrows.png", 32, 1, 1.0, False),
		("intact_knives", "prop_barrel_knives.png", 32, 1, 1.0, False),
		("break_arrows", "prop_barrel_arrows_break.png", 32, 6, 12.0, False),
		("break_knives", "prop_barrel_knives_break.png", 32, 6, 12.0, False),
	],
	"ammo_pickup_frames.tres": [
		("arrows", "pickup_arrows.png", 16, 4, 6.0, True),
		("knives", "pickup_knives.png", 16, 4, 6.0, True),
		("collect", "vfx_ammo_pickup.png", 16, 5, 15.0, False),
	],
}


def sprite_frames(anims):
	textures = []
	for _, png, _, _, _, _ in anims:
		if png not in textures:
			textures.append(png)
	subs, blocks = [], []
	for name, png, fw, n, speed, loop in anims:
		tid = textures.index(png) + 1
		refs = []
		for i in range(n):
			sid = "%s_%d" % (name, i)
			subs.append('[sub_resource type="AtlasTexture" id="%s"]\natlas = ExtResource("%d")\nregion = Rect2(%d, 0, %d, %d)\n'
				% (sid, tid, i * fw, fw, fw))
			refs.append('{"duration": 1.0, "texture": SubResource("%s")}' % sid)
		blocks.append('{"frames": [%s], "loop": %s, "name": &"%s", "speed": %.1f}'
			% (", ".join(refs), "true" if loop else "false", name, speed))
	head = '[gd_resource type="SpriteFrames" load_steps=%d format=3]\n\n' % (len(textures) + len(subs) + 1)
	ext = "".join('[ext_resource type="Texture2D" path="res://assets/run021/ammo/%s" id="%d"]\n' % (p, i + 1)
		for i, p in enumerate(textures))
	return head + ext + "\n" + "\n".join(subs) + "\n[resource]\nanimations = [" + ", ".join(blocks) + "]\n"


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	outputs = build()
	for name, canvas in outputs.items():
		fw, fh, n = EXPECTED[name]
		assert (canvas.w, canvas.h) == (fw * n, fh), (name, canvas.w, canvas.h)
		save_png(canvas, os.path.join(OUT, name))
		print(name, canvas.w, canvas.h, "%dx%d x%d" % (fw, fh, n))
	for name, anims in FRAMES.items():
		with open(os.path.join(OUT, name), "w", newline="\n") as f:
			f.write(sprite_frames(anims))
		print(name, ", ".join(a_[0] for a_ in anims))
	if preview:
		import ammo_preview  # noqa: E402  (preview only, reads project art read-only)
		ammo_preview.write(outputs, preview)


if __name__ == "__main__":
	main()

"""Secret wall hints (RUN-021): three subtle overlays for the 16x32 entrance of a secret wall.

Drawn by scripts/secret_wall_hint.gd above the SecretWallMask (z 51), configured by a
SecretWallStyle resource (assets/run021/secrets/n4_{cracks,glow,tint}.tres). Every texture is a
white alpha mask, 16x32, transparent on its outer border, so the colour and strength live in
the style and a biome can retint it without regenerating anything:

  n4_cracks_core.png / n4_cracks_lip.png
            a hairline crack stepping down across the courses, through the mortar joints the
            natural block cracks never cross, with a few chips and a loosened joint; the lip is
            the lit edge (light from the upper right, like the N4 moon). N4's first variant.
  n4_glow_seep.png / n4_glow_embers.png
            a faint greyed-spectral light seeping through the horizontal joints of the entrance,
            plus a very low wash in its middle; nothing reaches the border, so no halo spills
            over the rest of the masked room. Embers are the few brightest joint pixels.
  n4_tint_wash.png
            the entrance stones a touch warmer and paler than the surrounding violet masonry:
            full on the block faces, lighter on the mortar, ragged dithered edges so it never
            reads as a flat panel.

The rows follow the N4 masonry courses (8 px, joints on local rows 7/15/23/31 when the wall
sits on the 16 px grid like every SecretWall). Vertical joints vary with the world phase and
are deliberately not used.

Sources (N4-coloured sheet, context previews) go to assets/source/run021/secrets/. The five
textures only need the tracked tools/art/pixel.py; tools/art/run021/n4/terrain_n4.py is
imported only when present, to draw the previews over the real N4 masonry, else they use a
plain fallback course pattern. Pure Python, no external library.
Usage: python3 tools/art/run021/secrets/secret_hints.py [--no-n4]  (--no-n4: force the fallback)
"""
import os
import sys

sys.dont_write_bytecode = True  # never drop caches into the shared N4 / art tool folders
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from pixel import Canvas, hexc, save_png  # noqa: E402

terrain_n4 = None
if "--no-n4" not in sys.argv:
	sys.path.insert(0, os.path.join(HERE, "..", "..", "run020"))
	sys.path.insert(0, os.path.join(HERE, "..", "n4"))
	try:
		import terrain_n4  # noqa: E402  (optional, read only: real N4 masonry for the previews)
	except ImportError:
		terrain_n4 = None

OUT = os.path.join(ROOT, "assets", "run021", "secrets")
SOURCE = os.path.join(ROOT, "assets", "source", "run021", "secrets")
W, H = 16, 32
JOINTS = (7, 15, 23, 31)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def mix(a, b, k):
	"""Same rounding as tools/art/world_terrain.py mix()."""
	return tuple(int(round(a[i] * (1 - k) + b[i] * k)) for i in range(3)) + (255,)


# N4 cemetery stone, dark -> light: exact values of terrain_n4.STONE
# (mix(STONE_COOL[i], DUSK_VIOLET[i], 0.3)), kept local so nothing depends on the N4 pass.
STONE = [hexc(c) for c in ("181920", "24252f", "30323e", "40424f", "545664", "6e6f7e")]

# Colours and strengths mirrored in the .tres files (kept here for the previews).
STYLES = {
	"cracks": {"core": (hexc("0d0c12"), 0.95), "lip": (mix(STONE[3], STONE[5], 0.55), 0.85), "add": False},
	"glow": {"core": (hexc("7ea4a6"), 0.5), "lip": (hexc("a9c8c6"), 0.5), "add": True},
	"tint": {"core": (hexc("8a7a66"), 0.24), "lip": None, "add": False},
}


def white(a):
	return (255, 255, 255, max(0, min(255, int(a))))


def mask(points):
	c = Canvas(W, H)
	for (x, y), a in points.items():
		if 1 <= x < W - 1 and 0 <= y < H and a > 0:
			c.put(x, y, white(a))
	return c


# ------------------------------------------------------------------ cracks
# Hand-placed path (x, y): enters the top course, drops through two joints with a stair step,
# fades out just above the floor. 1 px wide everywhere.
CRACK = [
	(10, 2), (10, 3), (9, 4), (9, 5), (10, 6), (10, 7), (9, 7),  # top course, then the joint
	(8, 8), (8, 9), (7, 10), (7, 11), (8, 12), (7, 13), (6, 14), (6, 15), (5, 15),
	(5, 16), (6, 17), (6, 18), (5, 19), (5, 20), (6, 21), (6, 22), (6, 23), (7, 23),
	(7, 24), (6, 25), (6, 26), (5, 27), (5, 28),
]
BRANCH = [(8, 12), (9, 13), (10, 13), (11, 14)]  # short split towards the right block
CHIPS = [(11, 7), (4, 15), (8, 23), (4, 16)]  # crumbled corners where it crosses joints


def cracks():
	core, lip = {}, {}
	n = len(CRACK)
	for i, p in enumerate(CRACK):
		# Taper both ends so the crack grows out of the stone instead of starting as a stroke.
		t = min(i, n - 1 - i)
		core[p] = 150 if t == 0 else 205 if t == 1 else 255
	for i, p in enumerate(BRANCH[1:]):
		core[p] = (230, 180, 120)[i]
	for p in CHIPS:
		core[p] = max(core.get(p, 0), 170)
	# Lit lip: the groove wall facing the upper-right light is its left side; every other pixel.
	for i, (x, y) in enumerate(CRACK[2:-2]):
		q = (x - 1, y)
		if i % 2 == 0 and q not in core:
			lip[q] = 210
	for q in ((10, 6), (5, 14), (7, 22)):  # catch-light on the chipped edges
		if q not in core:
			lip[q] = 255
	return mask(core), mask(lip)


# ------------------------------------------------------------------ glow
# Light leaking through a few joint runs only (row, first x, last x), uneven and off-centre so
# it reads as a gap behind the stones, not a lit frame. The floor joint (31) stays dark.
SEEP = ((7, 7, 9), (15, 4, 11), (23, 6, 10))


def glow():
	seep, embers = {}, {}
	for row, x0, x1 in SEEP:
		for x in range(x0, x1 + 1):
			end = min(x - x0, x1 - x)
			seep[(x, row)] = 120 if end == 0 else 200 if end == 1 else 230
			# One-pixel bleed onto the block edges, dithered and only near the middle of the run.
			if end >= 1:
				for dy, a in ((-1, 70), (1, 50)):
					if (x + row + dy) % 2 == 0:
						seep[(x, row + dy)] = a
	# A faint dithered breath between the two lower runs: the cavity behind, never a box.
	for y in range(17, 22):
		for x in range(6, 10):
			if (x + y) % 2 == 0 and not (y in (17, 21) and x in (6, 9)):
				seep[(x, y)] = 34
	for p in ((7, 15), (8, 15), (8, 23)):
		embers[p] = 255
	embers[(9, 15)] = 130
	embers[(8, 7)] = 130
	return mask(seep), mask(embers)


# ------------------------------------------------------------------ tint
# Tinted span per 8 px course (first x, last x): staggered like a patch of re-laid stones, so the
# outline follows the courses instead of forming a column. The top course is only a fragment.
COURSES = ((5, 10), (2, 11), (4, 13), (2, 12))


def tint():
	wash = {}
	for course, (x0, x1) in enumerate(COURSES):
		top = course * 8
		for y in range(top, top + 7):  # the joint row (top + 7) stays untouched
			for x in range(x0, x1 + 1):
				end = min(x - x0, x1 - x)
				if top == 0 and y < 2:
					a = 0
				elif end == 0:
					a = 255 if BAYER[y % 4][x % 4] < 6 else 0  # dithered ends of each span
				elif y == top or y == top + 6:
					a = 190  # block edges slightly lighter, keeps the bevels of the masonry
				else:
					a = 255
				wash[(x, y)] = a
	return mask(wash)


def build():
	ck, cl = cracks()
	gs, ge = glow()
	return {
		"n4_cracks_core": ck,
		"n4_cracks_lip": cl,
		"n4_glow_seep": gs,
		"n4_glow_embers": ge,
		"n4_tint_wash": tint(),
	}


# ------------------------------------------------------------------ previews
def _blend(under, tex, color, strength, add):
	out = under.copy()
	for y in range(tex.h):
		for x in range(tex.w):
			t = tex.get(x, y)
			u = out.get(x, y)
			if t is None or u is None:
				continue
			a = t[3] / 255.0 * strength
			if add:
				px = tuple(min(255, int(round(u[i] + color[i] * a))) for i in range(3)) + (255,)
			else:
				px = tuple(int(round(color[i] * a + u[i] * (1 - a))) for i in range(3)) + (255,)
			out.put(x, y, px)
	return out


def _masonry(cols, rows, seed=1):
	c = Canvas(cols * 16, rows * 16)
	if terrain_n4 is None:
		# Fallback: flat 8 px courses of staggered blocks in the local N4 stone (mortar on the
		# bottom row and left column, as in the N4 masonry), enough to judge the hints.
		for y in range(c.h):
			course = y // 8
			for x in range(c.w):
				bx = (x + course * 11) % 24
				block = (x + course * 11) // 24 + course
				tone = STONE[2] if block % 3 else STONE[3]
				c.put(x, y, STONE[0] if y % 8 == 7 or bx == 0 else STONE[4] if y % 8 == 0 else tone)
		return c
	for cy in range(rows):
		for cx in range(cols):
			tile = terrain_n4.masonry_tile((seed + cy) % terrain_n4.SEEDS, (cx + 2 * cy) % terrain_n4.PHASES, 0)
			c.blit(tile, cx * 16, cy * 16)
	return c


def apply(base, built, name, ox, oy):
	style = STYLES[name]
	layers = [(built["n4_%s_%s" % (name, k)], style[k2]) for k, k2 in (
		("core", "core"), ("lip", "lip"), ("seep", "core"), ("embers", "lip"), ("wash", "core")) if "n4_%s_%s" % (name, k) in built]
	patch = Canvas(W, H)
	for y in range(H):
		for x in range(W):
			patch.put(x, y, base.get(ox + x, oy + y))
	for tex, spec in layers:
		if spec is not None:
			patch = _blend(patch, tex, spec[0], spec[1], style["add"])
	out = base.copy()
	out.blit(patch, ox, oy)
	return out


def preview(built):
	# N4-coloured textures on their own (source reference, local colours only): cracks, glow, tint.
	ref = Canvas(W * 3 + 8, H)
	dark = Canvas(W, H)
	for name, ox in (("cracks", 0), ("glow", W + 4), ("tint", 2 * W + 8)):
		dark.rect(0, 0, W, H, STONE[2])
		ref.blit(apply(dark, built, name, 0, 0), ox, 0)
	save_png(ref, os.path.join(SOURCE, "n4_hints_coloured_x8.png"), 8)
	# Same 7x4-cell masonry patch, entrance on the grid in the middle: none / cracks / glow / tint.
	base = _masonry(7, 4)
	panels = [base] + [apply(base, built, n, 48, 32) for n in ("cracks", "glow", "tint")]
	sheet = Canvas((base.w + 4) * len(panels), base.h)
	for i, p in enumerate(panels):
		sheet.blit(p, i * (base.w + 4), 0)
	if terrain_n4 is None:
		# Without the N4 generator: one fallback preview, the real-masonry ones are left as they are.
		save_png(sheet, os.path.join(SOURCE, "preview_fallback_hints_x6.png"), 6)
		return
	save_png(sheet, os.path.join(SOURCE, "preview_n4_hints_x1.png"))
	save_png(sheet, os.path.join(SOURCE, "preview_n4_hints_x2.png"), 2)
	save_png(sheet, os.path.join(SOURCE, "preview_n4_hints_x6.png"), 6)
	# Close-up of the entrance and one cell around it, for pixel review.
	crop = Canvas((48 + 2) * len(panels), 64)
	for i, p in enumerate(panels):
		for y in range(64):
			for x in range(48):
				crop.put(i * 50 + x, y, p.get(32 + x, y))
	save_png(crop, os.path.join(SOURCE, "preview_n4_hints_closeup_x8.png"), 8)


if __name__ == "__main__":
	os.makedirs(OUT, exist_ok=True)
	os.makedirs(SOURCE, exist_ok=True)
	built = build()
	for name, canvas in built.items():
		assert (canvas.w, canvas.h) == (W, H)
		save_png(canvas, os.path.join(OUT, name + ".png"))
	preview(built)
	print("wrote %d textures to %s and previews to %s" % (len(built), OUT, SOURCE))

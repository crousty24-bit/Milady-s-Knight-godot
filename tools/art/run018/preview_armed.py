"""RUN-018 preview/check: composite the layered knight with every melee weapon and level.

Usage: python3 tools/art/run018/preview_armed.py OUT_DIR

Reproduces in Python what scripts/player.gd + scripts/weapon_art.gd draw in game (body,
smear, mid, weapon, over, ground clip), compares Sword0 with the validated RUN-029 atlas
(assets/sprites/ashen_knight.png) and writes contact sheets. Purely a preview tool.
"""
import os
import struct
import sys
import zlib

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from pixel import Canvas, hexc, save_png  # noqa: E402
import weapon_raster as W  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OX, OY, FRAME = 32, 61, 64
STRIPS = {s.name: s for s in W.all_strips()}
BASE_REACH = {"Sword": 1.0, "Longsword": 1.2, "BrutalAxe": 0.8, "DarkScythe": 1.5, "Warhammer": 0.8, "Halberds": 2.0}
POLE = ("DarkScythe", "Halberds")
STOW = {"Sword": ("Scabbard", 8.5, None), "Longsword": ("ScabbardLong", 11.5, None),
	"BrutalAxe": ("BrutalAxe", 12.0, 2.15), "Warhammer": ("Warhammer", 12.0, 2.15),
	"DarkScythe": ("DarkScythe", 26.0, -2.3), "Halberds": ("Halberds", 30.0, -2.3)}


def load_png(path):
	data = open(path, "rb").read()
	pos, idat, w, h = 8, b"", 0, 0
	while pos < len(data):
		n = struct.unpack(">I", data[pos:pos + 4])[0]
		kind = data[pos + 4:pos + 8]
		body = data[pos + 8:pos + 8 + n]
		if kind == b"IHDR":
			w, h = struct.unpack(">II", body[:8])
		elif kind == b"IDAT":
			idat += body
		pos += 12 + n
	raw = zlib.decompress(idat)
	c = Canvas(w, h)
	stride = w * 4
	prev = bytearray(stride)
	i = 0
	for y in range(h):
		f = raw[i]
		line = bytearray(raw[i + 1:i + 1 + stride])
		i += 1 + stride
		for x in range(stride):
			a = line[x - 4] if x >= 4 else 0
			b = prev[x]
			cc = prev[x - 4] if x >= 4 else 0
			if f == 1:
				line[x] = (line[x] + a) & 255
			elif f == 2:
				line[x] = (line[x] + b) & 255
			elif f == 3:
				line[x] = (line[x] + (a + b) // 2) & 255
			elif f == 4:
				p = a + b - cc
				pa, pb, pc = abs(p - a), abs(p - b), abs(p - cc)
				line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else cc)) & 255
		for x in range(w):
			px = tuple(line[x * 4:x * 4 + 4])
			if px[3]:
				c.px[y * w + x] = px
		prev = line
	return c


def rig():
	"""Parse the generated knight_rig.gd (it is valid JSON once the const header is stripped)."""
	import json
	text = open(os.path.join(ROOT, "assets/run018/knight/knight_rig.gd")).read()
	body = text[text.index("{"):text.index("# Weapon strips")]
	body = body.replace("true", "true").replace(",\n}", "\n}")
	return json.loads(body)


def layout():
	"""Row of each animation in the atlases (same order as knight_armed.build)."""
	text = open(os.path.join(ROOT, "assets/run018/knight/knight_rig.gd")).read()
	text = text[:text.index("# Weapon strips")]
	return [line.split('"')[1] for line in text.splitlines() if line.startswith('\t"')]


def cell(atlas, row, col):
	c = Canvas(FRAME, FRAME)
	for y in range(FRAME):
		for x in range(FRAME):
			p = atlas.get(col * FRAME + x, row * FRAME + y)
			if p is not None:
				c.put(x, y, p)
	return c


def compose(layers, row, col, spec, weapon, level, margin=40, on_floor=True):
	"""Return a canvas (FRAME + 2*margin wide) with the frame composited like in game."""
	size = FRAME + 2 * margin
	out = Canvas(size, size)
	body, mid, over = (cell(a, row, col) for a in layers)
	out.blit(body, margin, margin)
	kind, hx, hy, angle, pole, smear = spec
	if weapon in POLE and kind in (1, 2):
		angle = pole
	reach = (BASE_REACH[weapon] + 0.1 * level) * 24.0
	px = {}
	if kind in (1, 2):
		px = W.rasterize(STRIPS[weapon], (hx, hy), angle, reach)
	elif kind == 3:
		name, length, stow_angle = STOW[weapon]
		px = W.rasterize(STRIPS[name], (hx, hy), angle if stow_angle is None else stow_angle, length)
	if smear:
		for (x, y), col in W.smear((hx, hy), smear[0], smear[1], smear[2], reach).items():
			if not (on_floor and y >= 0):
				out.put(x + OX + margin, y + OY + margin, col)
	out.blit(mid, margin, margin)
	for (x, y), col in px.items():
		if on_floor and y >= 0:
			continue
		out.put(x + OX + margin, y + OY + margin, col)
	out.blit(over, margin, margin)
	return out


def main():
	dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "work/run018/claude/knight")
	os.makedirs(dest, exist_ok=True)
	base = os.path.join(ROOT, "assets/run018/knight/")
	layers = [load_png(base + f"knight_{t}.png") for t in ("body", "mid", "over")]
	original = load_png(os.path.join(ROOT, "assets/sprites/ashen_knight.png"))
	frames = rig()
	names = layout()
	# 1. Sword0 against the validated atlas (rows shared up to resurrect).
	diff_total, px_total, worst = 0, 0, (0, "")
	for row, name in enumerate(names):
		if name.startswith("knife") or name in ("throw", "up_throw"):
			continue
		for col, spec in enumerate(frames[name]):
			mine = compose(layers, row, col, spec, "Sword", 0, margin=0, on_floor=not name.startswith(("up", "base")))
			ref = cell(original, row, col)
			d = 0
			for i in range(FRAME * FRAME):
				a, b = mine.px[i], ref.px[i]
				if (a is None) != (b is None) or (a is not None and a[:3] != b[:3]):
					d += 1
				if b is not None:
					px_total += 1
			diff_total += d
			if d > worst[0]:
				worst = (d, f"{name}[{col}]")
	print(f"Sword0 vs validated atlas: {diff_total} differing pixels over {px_total} opaque reference pixels; worst frame {worst[1]} ({worst[0]} px)")
	# 2. Contact sheets: each melee weapon level 0 and 3 on representative frames.
	picks = [("idle", 0), ("run", 2), ("rise", 0), ("fall", 0), ("land", 0), ("wall", 0), ("hurt", 0), ("atk1", 1), ("atk1", 3), ("atk1", 5), ("atk2", 3), ("atk3", 4), ("dead", 5), ("bow_idle", 0), ("knife_idle", 0)]
	bg = hexc("2e3138")
	margin = 40
	size = FRAME + 2 * margin
	for level in (0, 3, 5):
		sheet = Canvas(size * len(picks), size * len(BASE_REACH))
		for r, weapon in enumerate(BASE_REACH):
			for c, (name, col) in enumerate(picks):
				row = names.index(name)
				img = compose(layers, row, col, frames[name][col], weapon, level, margin)
				sheet.blit(img, c * size, r * size)
		for x in range(sheet.w):  # ground line under every frame
			for r in range(len(BASE_REACH)):
				sheet.put(x, r * size + margin + OY, hexc("4b4751"))
		save_png(sheet, os.path.join(dest, f"armed_level{level}_x2.png"), 2, bg)
	knife = Canvas(FRAME * 16, FRAME)
	for i, (name, col) in enumerate([("knife_idle", 0), ("knife_run", 0), ("knife_run", 4), ("knife_rise", 0), ("knife_fall", 0), ("knife_land", 0), ("knife_wall", 0), ("knife_hurt", 0)] + [("throw", k) for k in range(7)] + [("up_throw", 0)]):
		knife.blit(cell(layers[0], names.index(name), col), i * FRAME, 0)
	save_png(knife, os.path.join(dest, "knives_x3.png"), 3, bg)


if __name__ == "__main__":
	main()

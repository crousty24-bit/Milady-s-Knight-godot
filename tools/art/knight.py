"""Generate the Ashen Knight spritesheet, sword angles, slash smear and VFX.

Usage: python3 tools/art/knight.py [--preview DIR]

Authored for RUN-012 from the project artwork (steel plate, red cape, dark
tabard with a gold emblem). Frames are 32x32 with the feet on the bottom edge
of row 30 and the body centred on column 16, facing right. The sword pivot is
the player's hand at (+4, -10) from the feet, i.e. pixel (20, 21) in a frame.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, grid, hexc, remap, save_png, sheet  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")

PAL = {
	"o": hexc("17131b"), "1": hexc("2b303b"), "2": hexc("48505f"), "3": hexc("737c8c"),
	"4": hexc("a6aebb"), "5": hexc("dde2e8"), "v": hexc("0a080c"),
	"r": hexc("3f0c13"), "R": hexc("741620"), "S": hexc("a8242c"),
	"b": hexc("33251d"), "B": hexc("5a4030"), "g": hexc("d0a84e"), "G": hexc("8c6b2e"),
	"t": hexc("26222c"), "T": hexc("3a3442"),
}
# The far leg and arm sit in shadow: shift every steel tone one step darker.
SHADE = {PAL["2"]: PAL["1"], PAL["3"]: PAL["2"], PAL["4"]: PAL["3"], PAL["5"]: PAL["3"]}


def g(text):
	return grid(text, PAL)


HELM = g("""
....oooo....
..oo4455oo..
.o23445545o.
.o234455555o
o12344oooooo
o1234ovvvvvo
o12344v5v5vo
o1223444444o
.o11223333o.
""")
HELM_DOWN = g("""
............
....oooo....
..oo4455oo..
.o23445545o.
o1234455555o
o1234oooooo.
o123ovvvvvo.
o1234v5v5vo.
.o1123333o..
""")
TORSO = g("""
.oo1122oo.
o12tTTt21o
o1tTTTTt1o
o1tTTgTt1o
o1tTgggt1o
o1tTTgTt1o
o1tTTTTt1o
obBBBgBBbo
o1tTTTTt1o
.o2tTTt2o.
.o1tTTt1o.
""")
ARM_HANG = g("""
..oooo..
.o3455o.
o234555o
o123344o
.oo234o.
..o234o.
..o234o.
..o123o.
..o2445o
..o1234o
...oooo.
""")
ARM_SWING_FWD = g("""
..oooo...
.o3455o..
o234555o.
o123344o.
.oo2344o.
...o2344o
....o2345o
....o12345o
.....o1234o
......oooo.
""")
ARM_SWING_BACK = g("""
..oooo..
.o3455o.
o234555o
o123344o
o234oo..
o234o...
o2345o..
o1234o..
.oooo...
""")
ARM_RAISED = g("""
....oo..
...o45o.
..o345o.
.o344o..
.o3455o.
o234555o
o123344o
.oooooo.
""")
ARM_ATTACK = g("""
..oooo...
.o3455o..
o234555o.
o123344o.
.oo2344o.
...o2344o
...o12345o
....o2445o
....o1234o
.....oooo.
""")
CAPE_IDLE = g("""
......oo.
.....oRSo
....orRSo
....orRSo
....orRSo
...orRRSo
...orRRSo
...orRRSo
...orRRSo
..orrRRSo
..orrRRSo
..orrRRo.
..orrRRo.
.orrrRRo.
.orrRRo..
.orrRRo..
.orrRo...
orrRo....
ooo......
""")
CAPE_IDLE2 = g("""
......oo.
.....oRSo
....orRSo
....orRSo
....orRSo
...orRRSo
...orRRSo
...orRRSo
...orRRSo
..orrRRSo
..orrRRSo
..orrRRo.
..orrRRo.
..orrRRo.
.orrrRo..
.orrRRo..
.orrRRo..
.orRRo...
.ooo.....
""")
CAPE_RUN = g("""
........ooo
......ooRSSo
....oorRRRSo
..oorrRRRRSo
.orrrRRRRSSo
orrrRRRRRSo.
orrRRRRRSo..
.orRRRRSSo..
.orrRRRSo...
..orRRRSo...
..orRRSo....
...orRo.....
....oo......
""")
CAPE_RUN2 = g("""
........ooo
.....oooRSSo
...oorrRRRSo
.oorrRRRRSSo
orrrRRRRRSSo
.orrRRRRRSo.
..orRRRRSSo.
..orrRRRSo..
...orRRRSo..
...orRRSo...
....orRo....
.....oo.....
""")
CAPE_FALL = g("""
o........
oRo......
orSo.....
orRSo....
.orRSo...
.orRRSo..
..orRRSo.
..orRRRSo
...orRRSo
...orrRSo
....orRSo
.....orRo
......oo.
""")
CAPE_FALL2 = g("""
.........
o........
oRo......
orSo.....
orRSo....
.orRSo...
.orRRSo..
..orRRRSo
..orrRRSo
...orrRSo
....orRSo
.....orRo
......oo.
""")
CAPE_HURT = g("""
.......oo.
.....ooRSo
...oorRRSo
..orrRRRSo
.orrRRRSo.
orrRRRSo..
orRRRSo...
.orRSo....
..oo.o....
""")
LEG_STAND = g("""
o234o..
o345o..
o345o..
o234o..
o234o..
o2344o.
o12234o
ooooooo
""")
LEG_FWD = g("""
o234o.....
.o345o....
..o345o...
...o234o..
....o234o.
....o2344o
....o12234o
....ooooooo
""")
LEG_BACK = g("""
....o234o
...o345o.
..o345o..
.o234o...
o234o....
o234o....
o1223o...
ooooo....
""")
LEG_BENT = g("""
o234o..
.o345o.
.o345o.
o234o..
o234o..
o2344o.
o12234o
ooooooo
""")
LEG_LIFT_BACK = g("""
..o234o
..o345o
.o3445o
o2344o.
o123o..
oo1o...
.oo....
""")
LEG_KNEE_FWD = g("""
o2345oo.
.o34455o
..oo234o
....o234o
....o2234o
....oooooo
""")
LEG_TUCK = g("""
o2345oo.
.o34455o
..oo234o
...o1234o
...oooooo
""")
LEG_KNEEL = g("""
o2345ooo.
.o3445554o
..ooo12234o
....ooooooo
""")
LEG_SHIN_DOWN = g("""
o234o
o345o
o2344o
o1223oooo
oooooooo.
""")
LYING = g("""
...................oooo...
.................oo4455o..
....oooo.......oo2344555o.
..ooRRRSooooooo123344oooo.
.orrRRRRStTTTgt123444vvo..
orrrRRRo1tTTggt1233445o...
orrRRo12tTTTgtt11223o.....
.oo.o12344oo12344oooo.....
...o1234455o23445o........
...oooooooooooooo.........
""")

FRAME = 32


def compose(cape=None, cape_at=(3, 12), back_leg=None, back_at=(12, 23), front_leg=None, front_at=(16, 23),
		helm=HELM, arm=ARM_HANG, arm_at=(16, 12), bob=0, lean=0, back_arm=None, back_arm_at=(13, 12)):
	"""Layer order: cape, far arm, far leg, near leg, torso, helm, near arm."""
	f = Canvas(FRAME, FRAME)
	if cape is not None:
		f.blit(cape, cape_at[0] + lean, cape_at[1] + bob)
	if back_arm is not None:
		f.blit(remap(back_arm, SHADE), back_arm_at[0] + lean, back_arm_at[1] + bob)
	if back_leg is not None:
		f.blit(remap(back_leg, SHADE), *back_at)
	if front_leg is not None:
		f.blit(front_leg, *front_at)
	f.blit(TORSO, 11 + lean, 12 + bob)
	f.blit(helm, 11 + lean, 3 + bob)
	if arm is not None:
		f.blit(arm, arm_at[0] + lean, arm_at[1] + bob)
	for x in range(FRAME):
		f.px[(FRAME - 1) * FRAME + x] = None
	return f


def legs_y(leg):
	"""Bottom-align a leg with the ground row 30 when it is the support leg."""
	return 31 - leg.h


def build_frames():
	anims = {}
	stand = dict(back_leg=LEG_STAND, front_leg=LEG_STAND)
	anims["idle"] = [
		compose(CAPE_IDLE, **stand),
		compose(CAPE_IDLE, **stand),
		compose(CAPE_IDLE2, bob=1, **stand),
		compose(CAPE_IDLE2, bob=1, **stand),
	]
	# Six-frame run: contact, down, passing, then the mirrored half.
	run = []
	cycle = [
		(LEG_FWD, (14, 23), LEG_BACK, (8, 23), 0, ARM_SWING_BACK, CAPE_RUN),
		(LEG_BENT, (15, 23), LEG_LIFT_BACK, (9, 24), 1, ARM_HANG, CAPE_RUN2),
		(LEG_STAND, (15, 23), LEG_KNEE_FWD, (13, 23), 0, ARM_SWING_FWD, CAPE_RUN),
		(LEG_BACK, (11, 23), LEG_FWD, (12, 23), 0, ARM_SWING_FWD, CAPE_RUN2),
		(LEG_LIFT_BACK, (12, 24), LEG_BENT, (13, 23), 1, ARM_HANG, CAPE_RUN),
		(LEG_KNEE_FWD, (15, 23), LEG_STAND, (13, 23), 0, ARM_SWING_BACK, CAPE_RUN2),
	]
	for front, fat, back, bat, bob, arm, cape in cycle:
		run.append(compose(cape, (0, 12), back, (bat[0], bat[1] + bob), front, (fat[0], fat[1] + bob), arm=arm, bob=bob, lean=1))
	anims["run"] = run
	anims["rise"] = [
		compose(CAPE_IDLE, (3, 13), LEG_STAND, (12, 23), LEG_TUCK, (16, 23), arm=ARM_RAISED, arm_at=(16, 8)),
		compose(CAPE_IDLE2, (3, 13), LEG_STAND, (12, 23), LEG_TUCK, (16, 23), arm=ARM_RAISED, arm_at=(16, 8)),
	]
	anims["fall"] = [
		compose(CAPE_FALL, (3, 4), LEG_BACK, (9, 23), LEG_STAND, (15, 23), arm=ARM_SWING_BACK),
		compose(CAPE_FALL2, (3, 4), LEG_BACK, (9, 23), LEG_STAND, (15, 23), arm=ARM_SWING_BACK),
	]
	anims["wall"] = [
		compose(CAPE_FALL, (3, 4), LEG_STAND, (13, 23), LEG_KNEE_FWD, (16, 22), arm=ARM_RAISED, arm_at=(17, 7), lean=1),
		compose(CAPE_FALL2, (3, 4), LEG_STAND, (13, 23), LEG_KNEE_FWD, (16, 22), arm=ARM_RAISED, arm_at=(17, 7), lean=1),
	]
	anims["attack"] = [
		compose(CAPE_IDLE, (2, 12), LEG_BACK, (9, 23), LEG_STAND, (16, 23), arm=ARM_ATTACK, lean=-1),
		compose(CAPE_RUN2, (0, 12), LEG_BACK, (10, 23), LEG_FWD, (14, 23), arm=ARM_ATTACK, lean=1),
		compose(CAPE_RUN, (0, 13), LEG_BACK, (10, 23), LEG_FWD, (14, 23), arm=ARM_ATTACK, bob=1, lean=1),
	]
	anims["hurt"] = [
		compose(CAPE_HURT, (2, 12), LEG_STAND, (12, 23), LEG_BACK, (12, 23), helm=HELM_DOWN, arm=ARM_SWING_BACK, lean=-1),
	]
	lying = Canvas(FRAME, FRAME)
	lying.blit(LYING, 3, 21)
	anims["dead"] = [
		anims["hurt"][0],
		compose(CAPE_IDLE, (3, 16), LEG_KNEEL, (14, 27), LEG_SHIN_DOWN, (11, 26), helm=HELM_DOWN, arm=ARM_HANG, bob=4),
		compose(CAPE_RUN2, (1, 19), LEG_KNEEL, (14, 27), LEG_SHIN_DOWN, (11, 26), helm=HELM_DOWN, arm=ARM_HANG, bob=7, lean=2),
		lying,
	]
	return anims


ORDER = [
	# name, fps, loop
	("idle", 5.0, True), ("run", 12.0, True), ("rise", 8.0, True), ("fall", 8.0, True),
	("wall", 6.0, True), ("attack", 1.0, False), ("hurt", 1.0, False), ("dead", 7.0, False),
]


# ---------------------------------------------------------------- sword / smear
SWORD_FRAME = 64
ANGLES = 32
BLADE = hexc("e4e8ee")
BLADE_EDGE = hexc("8d96a6")
BLADE_TIP = hexc("ffffff")
GUARD = hexc("d0a84e")
GUARD_DARK = hexc("8c6b2e")
GRIP = hexc("4a3326")
OUT_C = hexc("17131b")
SWORD_RANGE = 24.0


def _plot(c, x, y, color):
	c.put(int(math.floor(x + 0.5)), int(math.floor(y + 0.5)), color)


def sword_frame(angle):
	c = Canvas(SWORD_FRAME, SWORD_FRAME)
	cx = cy = SWORD_FRAME // 2
	d = (math.cos(angle), math.sin(angle))
	n = (-d[1], d[0])
	body = Canvas(SWORD_FRAME, SWORD_FRAME)
	steps = 96
	for i in range(steps + 1):
		t = -5.0 + (SWORD_RANGE + 5.0) * i / steps
		x, y = cx + d[0] * t, cy + d[1] * t
		if t < -1.0:
			_plot(body, x, y, GRIP if t > -4.0 else GUARD)
		elif t < 1.5:
			for s in (-3, -2, -1, 0, 1, 2, 3):
				_plot(body, x + n[0] * s, y + n[1] * s, GUARD if abs(s) < 3 else GUARD_DARK)
		else:
			_plot(body, x + n[0] * 0.8, y + n[1] * 0.8, BLADE_EDGE)
			_plot(body, x, y, BLADE if t < SWORD_RANGE - 2 else BLADE_TIP)
	# Dark 1 px outline keeps the blade readable over pale skies and stone.
	for y in range(SWORD_FRAME):
		for x in range(SWORD_FRAME):
			if body.get(x, y) is None and any(body.get(x + a, y + b) is not None for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
				c.put(x, y, OUT_C)
	c.blit(body, 0, 0)
	return c


SMEAR_SPAN = 0.85


def smear_frame(angle):
	"""Crescent trailing the blade: bright at the leading edge and outer rim."""
	c = Canvas(SWORD_FRAME, SWORD_FRAME)
	cx = cy = SWORD_FRAME // 2
	for y in range(SWORD_FRAME):
		for x in range(SWORD_FRAME):
			dx, dy = x + 0.5 - cx, y + 0.5 - cy
			r = math.hypot(dx, dy)
			if r < 8.0 or r > SWORD_RANGE + 1.5:
				continue
			behind = (angle - math.atan2(dy, dx)) % math.tau
			if behind > SMEAR_SPAN:
				continue
			lead = 1.0 - behind / SMEAR_SPAN
			# Thin crescent along the tip path, thickest at the blade.
			thickness = 1.5 + 5.5 * lead * lead
			outer = SWORD_RANGE + 0.5
			if r > outer or r < outer - thickness:
				continue
			k = lead * (0.55 + 0.45 * (r - (outer - thickness)) / thickness)
			if k > 0.7:
				col = hexc("fffbe8", 255)
			elif k > 0.42:
				col = hexc("f2e2a8", 215)
			elif k > 0.2:
				col = hexc("c9b98a", 140)
			elif k > 0.08:
				col = hexc("9aa6b8", 80)
			else:
				continue
			c.put(x, y, col)
	return c


# ---------------------------------------------------------------- small VFX
def spark_frames():
	"""Impact spark (16x16, 5 frames): white core, warm rays, fading embers."""
	frames = []
	W = hexc("ffffff")
	Y = hexc("ffe9a0")
	O = hexc("e8a24a")
	D = hexc("9a5a2a")
	specs = [
		[(0, 0, W), (1, 0, W), (-1, 0, W), (0, 1, W), (0, -1, W), (1, 1, Y), (-1, -1, Y), (1, -1, Y), (-1, 1, Y)],
		"ray3", "ray5", "ray6", "embers",
	]
	for i, spec in enumerate(specs):
		c = Canvas(16, 16)
		if isinstance(spec, list):
			for x, y, col in spec:
				c.put(8 + x, 8 + y, col)
		elif spec.startswith("ray"):
			length = int(spec[3:])
			for a in range(8):
				ang = a * math.pi / 4 + (0.2 if a % 2 else 0)
				reach = length if a % 2 == 0 else length - 2
				for t in range(1, reach + 1):
					col = W if t <= reach // 3 + (1 if i == 1 else 0) else (Y if t <= 2 * reach // 3 + 1 else O)
					if i == 3 and t < 3:
						continue
					_plot(c, 8 + math.cos(ang) * t, 8 + math.sin(ang) * t, col)
			if i < 3:
				c.put(8, 8, W)
		else:
			for x, y in ((3, 4), (12, 5), (5, 12), (11, 11), (2, 9), (13, 8)):
				c.put(x, y, D)
		frames.append(c)
	return frames


def puff_frames():
	"""Double-jump air ring seen edge-on (24x10, 5 frames), pale steel blue."""
	frames = []
	cols = [hexc("eef6ff"), hexc("c0d8ea"), hexc("9fb9cf"), hexc("7d93a8", 200), hexc("5e7186", 140)]
	for i in range(5):
		c = Canvas(24, 10)
		rx = 3 + i * 2.2
		ry = 1.2 + i * 0.6
		col = cols[i]
		for k in range(64):
			a = k / 64 * math.tau
			x, y = 12 + math.cos(a) * rx, 5 + math.sin(a) * ry
			if i >= 3 and math.sin(a) < -0.2:
				continue
			_plot(c, x - 0.5, y - 0.5, col)
		if i < 2:
			for dx in (-1, 0, 1):
				c.put(12 + dx, 5, cols[0])
		frames.append(c)
	return frames


def dust_frames():
	"""Wall-slide grit (6x8, 3 frames) in warm stone grey."""
	frames = []
	A = hexc("c9bea4")
	B = hexc("968b75")
	pts = [
		[(2, 1, A), (3, 2, B), (1, 3, B)],
		[(3, 3, A), (1, 4, B), (4, 5, B), (2, 6, B)],
		[(2, 5, B), (4, 7, B), (0, 6, B)],
	]
	for p in pts:
		c = Canvas(6, 8)
		for x, y, col in p:
			c.put(x, y, col)
		frames.append(c)
	return frames


# ---------------------------------------------------------------- outputs
def write_sprite_frames(path, texture_res, layout):
	"""Write a Godot SpriteFrames resource using AtlasTexture regions."""
	lines = []
	subs = []
	anims = []
	n = 0
	for name, fps, loop, regions in layout:
		frames = []
		for (x, y, w, h) in regions:
			n += 1
			sid = f"{name}_{len(frames)}"
			subs.append(f'[sub_resource type="AtlasTexture" id="{sid}"]\natlas = ExtResource("1")\nregion = Rect2({x}, {y}, {w}, {h})\n')
			frames.append('{"duration": 1.0, "texture": SubResource("%s")}' % sid)
		anims.append('{"frames": [%s], "loop": %s, "name": &"%s", "speed": %s}' % (", ".join(frames), "true" if loop else "false", name, repr(float(fps))))
	lines.append(f'[gd_resource type="SpriteFrames" load_steps={n + 2} format=3]\n')
	lines.append(f'[ext_resource type="Texture2D" path="{texture_res}" id="1"]\n')
	lines.extend(subs)
	lines.append("[resource]\nanimations = [%s]\n" % ", ".join(anims))
	with open(path, "w", newline="\n") as f:
		f.write("\n".join(lines))


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	anims = build_frames()
	columns = max(len(anims[name]) for name, _, _ in ORDER)
	rows = []
	layout = []
	for r, (name, fps, loop) in enumerate(ORDER):
		frames = anims[name]
		rows.append(frames + [Canvas(FRAME, FRAME)] * (columns - len(frames)))
		layout.append((name, fps, loop, [(i * FRAME, r * FRAME, FRAME, FRAME) for i in range(len(frames))]))
	knight = sheet([f for row in rows for f in row], columns)
	save_png(knight, os.path.join(OUT, "ashen_knight.png"))
	write_sprite_frames(os.path.join(OUT, "ashen_knight_frames.tres"), "res://assets/sprites/ashen_knight.png", layout)

	angles = [i * math.tau / ANGLES for i in range(ANGLES)]
	save_png(sheet([sword_frame(a) for a in angles], ANGLES), os.path.join(OUT, "ashen_sword.png"))
	save_png(sheet([smear_frame(a) for a in angles], ANGLES), os.path.join(OUT, "ashen_sword_smear.png"))
	save_png(sheet(spark_frames(), 5), os.path.join(OUT, "vfx_hit_spark.png"))
	save_png(sheet(puff_frames(), 5), os.path.join(OUT, "vfx_air_puff.png"))
	save_png(sheet(dust_frames(), 3), os.path.join(OUT, "vfx_wall_dust.png"))
	if preview:
		save_png(knight, os.path.join(preview, "knight_sheet_x6.png"), 6, (52, 60, 66, 255))
		save_png(sheet([sword_frame(a) for a in angles[:16]], 8), os.path.join(preview, "sword_x4.png"), 4, (52, 60, 66, 255))
		save_png(sheet([smear_frame(a) for a in angles[24:32] + angles[0:4]], 6), os.path.join(preview, "smear_x4.png"), 4, (52, 60, 66, 255))
		vfx = Canvas(120, 16)
		for i, f in enumerate(spark_frames()):
			vfx.blit(f, i * 16, 0)
		save_png(vfx, os.path.join(preview, "spark_x8.png"), 8, (52, 60, 66, 255))
		save_png(sheet(puff_frames(), 5), os.path.join(preview, "puff_x8.png"), 8, (52, 60, 66, 255))
	print("knight sheet", knight.w, knight.h, {n: len(anims[n]) for n, _, _ in ORDER})


if __name__ == "__main__":
	main()

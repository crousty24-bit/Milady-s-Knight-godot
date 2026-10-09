"""RUN-018: Ashen Knight with interchangeable weapons (three layers + weapon rig data).

Usage: python3 tools/art/run018/knight_armed.py [--preview DIR]

tools/art/knight.py (validated RUN-029 rig) is imported read-only: every pose, part and
light is reused. Instead of drawing the Sword, its call is *recorded*: the hand, angle and
the moment in the paint order. Three atlases with the same layout come out of each frame:

  body  everything except the weapon (and except the smear crescent);
  mid   only the parts painted after the smear (near arm, pauldron, sword, hand...);
  over  only the parts painted after the weapon (near hand, later parts and their contours).

In game (scripts/player.gd), the carrier sprite draws body, then the smear sized to the
weapon reach, then mid, then the weapon rasterised from its strip (weapon_raster.py ↔
scripts/weapon_art.gd) at the exact gameplay reach, then over. This restores the
original paint order while the blade length follows RANGE x 24 px and polearms may extend
beyond the 64x64 frame. The 64x64 frame, anchor (sprite at (0, -29)) and animation names
are unchanged; Throwing Knives get their own stance and throw (knife_*, throw, up_throw).

Rig data (assets/run018/knight/knight_rig.gd): per animation and frame
  [kind, hand_x, hand_y, angle, pole_angle, smear(a0, a1, heavy) or []]
kind 0 none, 1 held (hand), 2 dropped on the ground, 3 stowed (belt anchor while a ranged
weapon is active). pole_angle replaces the angle for Dark Scythe/Halberds outside the
contact window where the long shaft would otherwise run through the ground.
"""
import math
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import knight as K  # noqa: E402
from pixel import Canvas, save_png, sheet  # noqa: E402
import weapon_raster as W  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "run018", "knight")
RES = "res://assets/run018/knight/"

# ---------------------------------------------------------------- recording render
_frame = None


class RecFrame(K.Frame):
	def __init__(self):
		super().__init__()
		global _frame
		_frame = self
		self.slot = None  # (kind, hand, angle, index)
		self.smear = None  # (a0, a1, heavy, index)


def rec_sword(f, hand, angle, inner=None):
	f.slot = (1, hand, angle, f.n)


def rec_dropped(f, spec):
	f.slot = (2, spec[0], spec[1], f.n)


def rec_smear(f, hand, a0, a1, heavy=False):
	f.smear = (a0, a1, heavy, f.n)


SHEATH_ANGLE = math.atan2(0.84, -0.55)


def rec_sheath(f, p):
	up, fwd = K.torso_frame(p)
	belt = K.add(K.add(p.hip, up, 1.5), fwd, -1.5)
	f.slot = (3, belt, SHEATH_ANGLE, f.n)


K.Frame = RecFrame
K.draw_sword = rec_sword
K.draw_dropped_sword = rec_dropped
K.draw_smear = rec_smear
K.draw_sheath = rec_sheath


def layers(p, layer="full"):
	"""Return (body, mid, over, record) canvases for a pose."""
	body = K.render(p, layer)
	f = _frame
	slot, sm = f.slot, f.smear
	mid = Canvas(K.FRAME, K.FRAME)
	over = Canvas(K.FRAME, K.FRAME)
	if slot is not None:
		split2 = slot[3]
		split1 = sm[3] if sm is not None else split2
		for (x, y), col in f.px.items():
			if y >= K.OY:
				continue
			if f.owner[(x, y)] >= split1:
				mid.put(x, y, col)
			if f.owner[(x, y)] >= split2:
				over.put(x, y, col)
	return body, mid, over, (slot, sm)


# ---------------------------------------------------------------- Throwing Knives stance (RUN-018)
# Same skeleton and stowed weapon as the Longbow stances; the near hand carries a knife.
# The throw starts at the gameplay muzzle (+4, -10), like the arrow.
KNIFE = W.knife()


def draw_knife(f, hand, angle):
	px = W.rasterize(KNIFE, hand, angle, KNIFE.length)
	out = {}
	for (x, y), col in px.items():
		q = (x + K.OX, y + K.OY)
		if 0 <= q[0] < K.FRAME and 0 <= q[1] < K.FRAME:
			out[q] = col
	f.add(out, outline=False)




def knifed(p, hand, angle, held=True):
	q = p.copy(sword=None, two_hands=False, sword_far=False, sword_behind=False, sheathed=True, bow=None)
	q.near_hand = hand
	q.knife = (angle if held else None)
	return q


# Hook the knife into the near hand paint step: render() calls draw_hand(f, near_hand, False) last.
_base_hand = K.draw_hand
_current_knife = [None]


def hand_with_knife(f, hand, far):
	if not far and _current_knife[0] is not None:
		draw_knife(f, hand, _current_knife[0])
	_base_hand(f, hand, far)


K.draw_hand = hand_with_knife


def knife_layers(p, layer="full"):
	_current_knife[0] = getattr(p, "knife", None)
	try:
		return layers(p, layer)
	finally:
		_current_knife[0] = None


def knife_idle_frames():
	out = []
	for p in K.idle_frames():
		dy = p.hip[1] + 13
		q = knifed(p, (5.0, -12.0 + dy), -0.55)
		q.far_hand = (-1.0, -11.5 + dy)
		q.lean = 0.12
		out.append(q)
	return out


def knife_run_frames():
	out = []
	for i, p in enumerate(K.run_frames()):
		ph = K.RUN_CYCLE[i][5]
		hy = K.RUN_CYCLE[i][4]
		out.append(knifed(p, (3.5 - ph * 1.5, -12.0 + hy + 13), 0.9 + ph * 0.1))
	return out


def knife_rise_frames():
	return [knifed(p, (5.5, -16.5), -0.9) for p in K.rise_frames()]


def knife_fall_frames():
	return [knifed(p, (5.5, -15.0), -0.3) for p in K.fall_frames()]


def knife_land_frames():
	a, b = K.land_frames()
	return [knifed(a, (5.5, -9.5), 0.4), knifed(b, (5.5, -11.0), -0.1)]


def knife_wall_frames():
	return [p.copy(sword=None, sword_far=False, sheathed=True, knife=None) for p in K.wall_frames()]


def knife_hurt_frames():
	return [knifed(p, K.add(p.near_hand, (1.0, 2.0)), -2.2) for p in K.hurt_frames()]


def throw_pose(near, far, angle, held, lean=0.16, sway=0.0, head="normal"):
	p = K.Pose(hip=(0.5, -13), lean=lean, head=head, near_foot=(5.0, -2), far_foot=(-5.0, -2), near_hand=near, far_hand=far,
		sword=None, sheathed=True, cape=[(-2.4 + sway * 0.3, 5), (-4.2 + sway, 10.5), (-5.4 + sway, 15.5)])
	p.knife = angle if held else None
	return p


def throw_frames():
	"""Same timing contract as shoot: 0-3 from the throw instant, 4-6 wind-up while F is held."""
	return [
		throw_pose((9.0, -12.5), (-4.5, -12.5), 0.0, False, lean=0.28, sway=-0.8),
		throw_pose((8.0, -11.5), (-3.5, -12.0), 0.0, False, lean=0.24, sway=-0.5),
		throw_pose((6.5, -11.5), (-2.0, -12.0), 0.6, True, lean=0.18, sway=-0.2),
		throw_pose((5.5, -12.0), (-1.0, -11.5), -0.4, True, lean=0.14),
		throw_pose((3.0, -17.5), (2.5, -12.0), -2.0, True, lean=0.06, sway=0.2),
		throw_pose((0.5, -20.5), (4.0, -12.5), -2.6, True, lean=0.0, sway=0.4, head="up"),
		throw_pose((-1.5, -21.0), (5.5, -13.0), -2.9, True, lean=-0.04, sway=0.5, head="up"),
	]


# ---------------------------------------------------------------- pole overrides
def pole_angle(name, i, angle):
	"""Long shafts (Dark Scythe, Halberds) outside the contact window: carried up and back
	instead of trailing through the floor. Contact frames keep the gameplay angle."""
	if name in ("run",):
		return -2.55 + (angle - 2.72) * 0.6
	if name == "land":
		return (-0.75, -0.85)[i]
	if name == "wall":
		return -2.15
	if name == "dead" and i == 0:
		return -2.0
	return angle


# ---------------------------------------------------------------- build
def build():
	"""[(name, fps, loop, [(body, mid, over, rec)])] in atlas row order."""
	anims = []

	def add(name, fps, loop, poses, layer="full", maker=layers):
		anims.append((name, fps, loop, [maker(p, layer) for p in poses]))

	add("idle", 6.0, True, K.idle_frames())
	add("run", 14.0, True, K.run_frames())
	add("rise", 8.0, True, K.rise_frames())
	add("fall", 8.0, True, K.fall_frames())
	add("land", 20.0, False, K.land_frames())
	add("wall", 7.0, True, K.wall_frames())
	add("hurt", 10.0, False, K.hurt_frames())
	add("dead", 8.0, False, K.dead_frames())
	moves = K.attack_frames()
	for i, m in enumerate(moves):
		add(f"atk{i + 1}", 1.0, False, m)
	for i, m in enumerate(moves):
		add(f"up{i + 1}", 1.0, False, [K.shifted_upper(p) for p in m], "upper")
	add("base_run", 14.0, True, K.run_frames(), "base")
	add("base_rise", 8.0, True, K.rise_frames(), "base")
	add("base_fall", 8.0, True, K.fall_frames(), "base")
	add("bow_idle", 6.0, True, K.bow_idle_frames())
	add("bow_run", 14.0, True, K.bow_run_frames())
	add("bow_rise", 8.0, True, K.bow_rise_frames())
	add("bow_fall", 8.0, True, K.bow_fall_frames())
	add("bow_land", 20.0, False, K.bow_land_frames())
	add("bow_wall", 7.0, True, K.bow_wall_frames())
	add("bow_hurt", 10.0, False, K.bow_hurt_frames())
	add("shoot", 1.0, False, K.shoot_frames())
	add("up_shoot", 1.0, False, [K.shifted_upper(p) for p in K.shoot_frames()], "upper")
	add("resurrect", 6.0, False, K.resurrect_frames())
	# RUN-018 Throwing Knives, appended so every earlier region keeps its place.
	add("knife_idle", 6.0, True, knife_idle_frames(), maker=knife_layers)
	add("knife_run", 14.0, True, knife_run_frames(), maker=knife_layers)
	add("knife_rise", 8.0, True, knife_rise_frames(), maker=knife_layers)
	add("knife_fall", 8.0, True, knife_fall_frames(), maker=knife_layers)
	add("knife_land", 20.0, False, knife_land_frames(), maker=knife_layers)
	add("knife_wall", 7.0, True, knife_wall_frames(), maker=knife_layers)
	add("knife_hurt", 10.0, False, knife_hurt_frames(), maker=knife_layers)
	add("throw", 1.0, False, throw_frames(), maker=knife_layers)
	add("up_throw", 1.0, False, [K.shifted_upper(p) for p in throw_frames()], "upper", knife_layers)
	return anims


def fmt(v):
	return repr(round(float(v), 4))


def write_strips(png_path):
	"""Stack every strip (variant A over variant B) into one atlas; return metadata rows."""
	strips = W.all_strips()
	width = max(st.width for st in strips)
	height = sum(st.rows * 2 for st in strips)
	atlas = Canvas(width, height)
	meta = []
	y = 0
	for st in strips:
		atlas.blit(st.variants[0], 0, y)
		atlas.blit(st.variants[1], 0, y + st.rows)
		meta.append((st.name, y, st.width, st.rows, st.grip, st.axis, st.length, st.stretch, st.head))
		y += st.rows * 2
	save_png(atlas, png_path)
	return meta


def write_rig(path, anims, strips):
	lines = [
		"# Generated by tools/art/run018/knight_armed.py — do not edit by hand.",
		"# Per animation/frame: [kind, hand_x, hand_y, angle, pole_angle, smear]",
		"# kind 0 none, 1 held, 2 dropped, 3 stowed; smear [] or [a0, a1, heavy].",
		"const FRAMES := {",
	]
	for name, _, _, frames in anims:
		rows = []
		for i, (_, _, _, (slot, sm)) in enumerate(frames):
			if slot is None:
				rows.append("[0, 0.0, 0.0, 0.0, 0.0, []]")
				continue
			kind, hand, angle, _ = slot
			pa = pole_angle(name, i, angle) if kind == 1 or kind == 2 else angle
			smear = "[]" if sm is None else "[%s, %s, %s]" % (fmt(sm[0]), fmt(sm[1]), "true" if sm[2] else "false")
			rows.append("[%d, %s, %s, %s, %s, %s]" % (kind, fmt(hand[0]), fmt(hand[1]), fmt(angle), fmt(pa), smear))
		lines.append('\t"%s": [%s],' % (name, ", ".join(rows)))
	lines.append("}")
	lines.append("# Weapon strips in weapon_strips.png: [y, width, rows, grip, axis, length, stretch, head]")
	lines.append("const STRIPS := {")
	for name, y, w, rows, grip, axis, length, stretch, head in strips:
		lines.append('\t"%s": [%d, %d, %d, %s, %s, %s, %d, %d],' % (name, y, w, rows, fmt(grip), fmt(axis), fmt(length), stretch, head))
	lines.append("}")
	with open(path, "w", newline="\n") as f:
		f.write("\n".join(lines) + "\n")


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	os.makedirs(OUT, exist_ok=True)
	anims = build()
	columns = max(len(fr) for _, _, _, fr in anims)
	layout = []
	cells = [[], [], []]
	for r, (name, fps, loop, frames) in enumerate(anims):
		for k in range(3):
			cells[k].extend([fr[k] for fr in frames] + [Canvas(K.FRAME, K.FRAME)] * (columns - len(frames)))
		layout.append((name, fps, loop, [(i * K.FRAME, r * K.FRAME, K.FRAME, K.FRAME) for i in range(len(frames))]))
	for k, tag in enumerate(("body", "mid", "over")):
		png = f"knight_{tag}.png"
		save_png(sheet(cells[k], columns), os.path.join(OUT, png))
		K.write_sprite_frames(os.path.join(OUT, f"knight_{tag}_frames.tres"), RES + png, layout)
	strips = write_strips(os.path.join(OUT, "weapon_strips.png"))
	write_rig(os.path.join(OUT, "knight_rig.gd"), anims, strips)
	print("knight layers", columns, "x", len(anims), {n: len(fr) for n, _, _, fr in anims})
	return anims


if __name__ == "__main__":
	main()

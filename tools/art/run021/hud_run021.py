"""RUN-021 HUD pass: icon of the active Magic Shield effect, shown top-left with its remaining time.

Usage: python3 tools/art/run021/hud_run021.py [--preview DIR]

Output (assets/run021/ui/):
  ui_effect_shield.png   12x12   1 frame: the Magic Shield pickup (tools/art/run019/world_run019.py) reduced to the
                                 12x12 HUD icon grid of ui_icons.png (hearts, coin), same cyan/blue functional ramp,
                                 pale protection sigil, dark outline so it reads over any backdrop without a panel.

Original art drawn by code from tools/art/palette.py; deterministic. No third-party pixel, no AI image.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ART)
from pixel import Canvas, hexc, outline, save_png  # noqa: E402
from palette import OUTLINE  # noqa: E402

ROOT = os.path.normpath(os.path.join(ART, "..", ".."))
OUT = os.path.join(ROOT, "assets", "run021", "ui")
# Same ramp as the RUN-019 Magic Shield item, aura and pickup VFX.
BLUE = [hexc(c) for c in ("0b2340", "1b4f94", "3a8fd4", "7ad0f0", "dcf7ff")]
# Half widths of the heater shield, top to bottom (8 px wide, 9 px tall before the outline).
ROWS = [4, 4, 4, 4, 4, 3, 3, 2, 1]


def shield_icon():
	b = Canvas(10, 10)
	for i, w in enumerate(ROWS):
		for x in range(5 - w, 5 + w):
			col = BLUE[2] if x < 5 else BLUE[1]
			if i > 5:
				col = BLUE[1] if x < 5 else BLUE[0]
			if x in (5 - w, 4 + w) or i == 0:
				col = BLUE[3] if (x < 5 or i == 0) else BLUE[2]
			b.put(x, i, col)
	# Sigil: vertical bar and short crossbar, as on the pickup.
	for y in range(2, 7):
		b.put(4, y, BLUE[4])
	for x in (3, 5):
		b.put(x, 3, BLUE[4])
	b.put(5, 2, BLUE[3])
	f = Canvas(12, 12)
	f.blit(outline(b, OUTLINE), 1, 1)
	return f


def main():
	os.makedirs(OUT, exist_ok=True)
	icon = shield_icon()
	save_png(icon, os.path.join(OUT, "ui_effect_shield.png"))
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
		save_png(icon, os.path.join(preview, "ui_effect_shield_x8.png"), 8, (52, 60, 66, 255))


if __name__ == "__main__":
	main()

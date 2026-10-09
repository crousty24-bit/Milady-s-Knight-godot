"""Atmosphere texture of N4 Forbidden Graveyard (RUN-021 N4 visual pass).

n4_mist.png 256x32: seamless grave mist hugging the ground (ordered dither), a thin bank on
the bottom rows with slow plumes curling up from it every so often, as if the graves were
breathing. Distinct from the N3 fog (a thicker bank with horizontal wisps). Drawn along long
walkable surfaces by campaign_decor.gd, tinted greyed spectral violet-cyan, low alpha. The
neutral glow is shared with N2 (assets/run021/n2/n2_glow.png).
Usage: python3 tools/art/run021/n4/atmos_n4.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from pixel import Canvas, save_png  # noqa: E402

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
# Plume centres (x) and heights: periodic over 256 px so the strip tiles.
PLUMES = ((22, 14), (83, 9), (141, 16), (198, 11), (240, 7))


def mist():
	W, H = 256, 32
	c = Canvas(W, H)
	for x in range(W):
		top = 22 + 2 * math.sin(2 * math.pi * x * 4 / W) + 1.5 * math.sin(2 * math.pi * x * 9 / W + 1.3)
		for y in range(H):
			density = 0.0
			if y > top:
				density = min(0.55, (y - top) / (H - top) * 0.75)
			for px, ph in PLUMES:
				dx = (x - px + W // 2) % W - W // 2
				# A plume: soft puffs stacked up from the bank, leaning right and thinning out.
				for k in range(3):
					cx = 2 + k * 3
					cy = top - 2 - k * ph / 3.0
					rx, ry = 9 - k * 2, 3.2 - k * 0.6
					d = ((dx - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
					if d < 1.0:
						density = max(density, (0.46 - k * 0.12) * (1 - d))
			if (y + int(1.5 * math.sin(2 * math.pi * x * 3 / W))) % 6 == 0:
				density *= 0.5
			if density * 16 > BAYER[y % 4][x % 4]:
				v = 165 + int(75 * density)
				c.put(x, y, (v, v, v, 255))
	return c


if __name__ == "__main__":
	out = os.path.join(ROOT, "assets", "run021", "n4")
	os.makedirs(out, exist_ok=True)
	save_png(mist(), os.path.join(out, "n4_mist.png"))
	print("wrote n4_mist.png")
	prev = os.path.join(ROOT, "work", "run021", "n4pass", "preview")
	os.makedirs(prev, exist_ok=True)
	save_png(mist(), os.path.join(prev, "n4_mist_x3.png"), 3)

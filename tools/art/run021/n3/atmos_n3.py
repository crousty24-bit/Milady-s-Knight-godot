"""Atmosphere texture of N3 Black Forest (RUN-021 N3 visual pass).

n3_fog.png 256x32: seamless ground fog in loose horizontal wisps (ordered dither), thicker
toward the bottom row, with thin gaps so it reads as drifting mist, not a flat band. Drawn
along long walkable surfaces by campaign_decor.gd, tinted cold blue, low alpha. The neutral
glow is shared with N2 (assets/run021/n2/n2_glow.png).
Usage: python3 tools/art/run021/n3/atmos_n3.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from pixel import Canvas, save_png  # noqa: E402

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def fog():
	W, H = 256, 32
	c = Canvas(W, H)
	for x in range(W):
		top = 14 + 3 * math.sin(2 * math.pi * x * 3 / W) + 2 * math.sin(2 * math.pi * x * 7 / W + 0.8)
		for y in range(H):
			t = (y - top) / (H - top)
			if t <= 0:
				continue
			density = min(0.62, t * 0.7)
			# Wisps: two drifting streaks above the bank, each a thin periodic band.
			for centre, period, phase in ((top - 4, 4, 0.3), (top - 8, 3, 2.1)):
				w = 0.5 + 0.5 * math.sin(2 * math.pi * x * period / W + phase)
				if abs(y - centre) < 1.2 and w > 0.55:
					density = max(density, 0.3 * w)
			# Thin horizontal gaps through the bank.
			if (y + int(2 * math.sin(2 * math.pi * x * 2 / W))) % 7 == 0:
				density *= 0.45
			if density * 16 > BAYER[y % 4][x % 4]:
				v = 160 + int(80 * density)
				c.put(x, y, (v, v, v, 255))
		for y in range(int(top) - 10, int(top)):
			for centre, period, phase in ((top - 4, 4, 0.3), (top - 8, 3, 2.1)):
				w = 0.5 + 0.5 * math.sin(2 * math.pi * x * period / W + phase)
				if 0 <= y < H and abs(y - centre) < 1.0 and w > 0.6 and (x + y) % 2 == 0:
					c.put(x, y, (190, 190, 190, 255))
	return c


if __name__ == "__main__":
	out = os.path.join(ROOT, "assets", "run021", "n3")
	os.makedirs(out, exist_ok=True)
	save_png(fog(), os.path.join(out, "n3_fog.png"))
	print("wrote n3_fog.png")

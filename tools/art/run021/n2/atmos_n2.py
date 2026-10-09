"""Atmosphere textures of N2 Blight Town (RUN-021 N2 visual pass).

n2_miasma.png 256x32: seamless ground-hugging miasma, ordered-dither density rising toward
the bottom row (drawn along long walkable surfaces by campaign_decor.gd, tinted, low alpha).
n2_glow.png 64x64: neutral grey dithered glow (same falloff as prop_glow.png) so the script
can tint it bile-olive or ember without the warm base of prop_glow.
Usage: python3 tools/art/run021/n2/atmos_n2.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from pixel import Canvas, save_png  # noqa: E402

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def miasma():
	W, H = 256, 32
	c = Canvas(W, H)
	for x in range(W):
		# Two periodic swells so the top edge rolls instead of being flat.
		top = 12 + 4 * math.sin(2 * math.pi * x * 2 / W) + 3 * math.sin(2 * math.pi * x * 5 / W + 1.3) + 1.5 * math.sin(2 * math.pi * x * 11 / W + 0.4)
		for y in range(H):
			t = (y - top) / (H - top)
			if t <= 0:
				continue
			density = min(0.72, t * 0.85)
			if density * 16 > BAYER[y % 4][x % 4]:
				v = 150 + int(70 * density)
				c.put(x, y, (v, v, v, 255))
	return c


def glow():
	"""Same banded, dithered falloff and alphas as world_props.glow(), in neutral white."""
	c = Canvas(64, 64)
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
				c.put(x, y, (255, 255, 255, a))
	return c


if __name__ == "__main__":
	out = os.path.join(ROOT, "assets", "run021", "n2")
	save_png(miasma(), os.path.join(out, "n2_miasma.png"))
	save_png(glow(), os.path.join(out, "n2_glow.png"))
	print("wrote n2_miasma.png, n2_glow.png")

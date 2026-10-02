"""Generate small gameplay feedback VFX (RUN-014).

Usage: python3 tools/art/vfx.py [--preview DIR]

vfx_coin_sparkle.png: 5 frames 16x16, centred, gold burst on pickup.
vfx_slime_splash.png: 2 rows (green, purple) of 5 frames 32x20, origin at the
bottom-centre (16, 20): goo droplets thrown up, then a puddle that soaks away.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, save_png, sheet  # noqa: E402
from palette import CORRUPT, GOLD, OUTLINE, SLIME_GREEN  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
WHITE = (255, 255, 255, 255)


def coin_sparkle():
	frames = []
	for i in range(5):
		c = Canvas(16, 16)
		radius = 2 + i * 1.6
		ring = [WHITE, GOLD[4], GOLD[3], GOLD[2], GOLD[1]][i]
		for k in range(24):
			a = k / 24 * math.tau
			if i >= 3 and k % 2:
				continue
			c.put(int(round(8 + math.cos(a) * radius - 0.5)), int(round(8 + math.sin(a) * radius - 0.5)), ring)
		# Four-point glints rising with the burst.
		for gx, gy, size in ((4, 5 - i, 1 + (i < 3)), (12, 4 - i, 1), (9, 2 - i // 2, 1 + (i == 1))):
			if gy < 0 or i == 4:
				continue
			c.put(gx, gy, WHITE)
			for d in range(1, size + 1):
				for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
					c.put(gx + dx, gy + dy, GOLD[3])
		if i < 2:
			for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
				c.put(7 + dx, 7 + dy, WHITE if i == 0 else GOLD[4])
		frames.append(c)
	return frames


def slime_splash(ramp):
	frames = []
	drops = [(-1.0, -2.2), (1.1, -2.0), (-2.0, -1.2), (2.2, -1.3), (-0.3, -2.6), (0.6, -1.6), (-1.5, -0.6), (1.7, -0.7)]
	for i in range(5):
		c = Canvas(32, 20)
		t = (i + 1) * 0.9
		for vx, vy in drops:
			x = 16 + vx * t * 2.4
			y = 18 + vy * t * 3.2 + 1.3 * t * t
			if y > 19 or i == 4:
				continue
			size = 2 if i < 2 else 1
			for dx in range(size):
				for dy in range(size):
					c.put(int(x) + dx, int(y) + dy, ramp[3] if dy == 0 else ramp[2])
		# Puddle: wide at first, then soaking into the ground.
		half = [5, 8, 9, 8, 6][i]
		for x in range(16 - half, 16 + half):
			edge = x in (16 - half, 16 + half - 1)
			c.put(x, 19, OUTLINE if edge else ramp[1])
			if not edge and i < 4 and abs(x - 16) < half - 2:
				c.put(x, 18, ramp[2] if i < 3 else ramp[1])
		if i == 0:
			for x in range(12, 20):
				for y in range(14, 18):
					c.put(x, y, ramp[3] if y == 14 else ramp[2])
		frames.append(c)
	return frames


def main():
	sparkle = sheet(coin_sparkle(), 5)
	splash = sheet(slime_splash(SLIME_GREEN) + slime_splash(CORRUPT), 5)
	save_png(sparkle, os.path.join(OUT, "vfx_coin_sparkle.png"))
	save_png(splash, os.path.join(OUT, "vfx_slime_splash.png"))
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
		save_png(sparkle, os.path.join(preview, "sparkle_x8.png"), 8, (52, 60, 66, 255))
		save_png(splash, os.path.join(preview, "splash_x6.png"), 6, (52, 60, 66, 255))


if __name__ == "__main__":
	main()

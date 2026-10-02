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
from palette import CORRUPT, GOLD, OUTLINE, SLIME_GREEN, STONE_COOL  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
WHITE = (255, 255, 255, 255)


def star(c, x, y, size, core=WHITE, arm=None):
	arm = arm or GOLD[3]
	c.put(x, y, core)
	for d in range(1, size + 1):
		col = GOLD[4] if d == 1 else arm
		for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
			c.put(x + dx, y + dy, col)


def coin_sparkle():
	"""7 frames 24x24 centred (12, 12): flash, ring, flying gold chips, glints."""
	chips = [(-0.9, -2.6), (1.0, -2.9), (-2.0, -1.8), (2.2, -2.0), (0.2, -3.4), (-1.4, -3.0), (1.7, -3.2)]
	frames = []
	for i in range(7):
		c = Canvas(24, 24)
		# expanding ring
		if i < 5:
			radius = 3.0 + i * 2.0
			ring = [WHITE, GOLD[4], GOLD[3], GOLD[2], GOLD[1]][i]
			steps = 40
			for k in range(steps):
				if i >= 3 and k % 2:
					continue
				a = k / steps * math.tau
				c.put(int(round(12 + math.cos(a) * radius - 0.5)), int(round(12 + math.sin(a) * radius * 0.9 - 0.5)), ring)
		# core flash
		if i < 3:
			r = (4, 3, 2)[i]
			for yy in range(-r, r + 1):
				for xx in range(-r, r + 1):
					if xx * xx + yy * yy <= r * r:
						c.put(12 + xx, 12 + yy, WHITE if i == 0 or xx * xx + yy * yy < r * r * 0.4 else GOLD[4])
		# long four-point star that shrinks
		if i < 4:
			star(c, 12, 12, (6, 5, 3, 1)[i])
		# gold chips thrown upward with gravity
		for k, (vx, vy) in enumerate(chips):
			if i == 0:
				continue
			t = i * 0.75
			x = 12 + vx * t * 1.9
			y = 12 + vy * t * 2.1 + 1.1 * t * t
			if i >= 6 and k % 2:
				continue
			if y > 22:
				continue
			col = (GOLD[4], GOLD[3], GOLD[3], GOLD[2], GOLD[1], GOLD[1])[min(5, i - 1)]
			xi, yi = int(round(x)), int(round(y))
			c.put(xi, yi, col)
			if i < 5:
				c.put(xi + 1, yi, GOLD[1] if col != GOLD[1] else GOLD[0])
				c.put(xi, yi + 1, GOLD[2] if i < 3 else GOLD[1])
		# twinkling glints
		for gx, gy, when in ((5, 6, 1), (19, 5, 2), (18, 17, 3), (6, 17, 2)):
			if i == when:
				star(c, gx, gy, 2, WHITE, GOLD[3])
			elif i == when + 1:
				star(c, gx, gy, 1, GOLD[4], GOLD[3])
		frames.append(c)
	return frames


def goo(c, x, y, ramp, size=2):
	"""A glossy goo droplet whose top-left pixel catches the light."""
	for ox in range(size):
		for oy in range(size):
			if size == 2 and ox == 1 and oy == 1 and False:
				continue
			col = ramp[4] if (ox, oy) == (0, 0) and size == 2 else ramp[3] if oy == 0 else ramp[2] if oy == 1 and size == 2 else ramp[3]
			c.put(x + ox, y + oy, col)
	if size == 2:
		c.put(x + 1, y + 1, ramp[1])


def slime_splash(ramp, wisps=False):
	"""6 frames 40x24, origin bottom-centre (20, 24): burst, arcing droplets, puddle."""
	frames = []
	drops = [(-1.0, -2.3, 2), (1.1, -2.1, 2), (-2.1, -1.4, 2), (2.3, -1.5, 2), (-0.3, -2.8, 2), (0.7, -1.9, 1), (-1.6, -0.8, 1), (1.8, -0.9, 1), (-2.7, -0.9, 1), (2.8, -1.0, 1)]
	for i in range(6):
		c = Canvas(40, 24)
		t = (i + 1) * 0.85
		# puddle: spreads out, then soaks away
		half = [6, 10, 12, 11, 8, 5][i]
		height = [5, 4, 3, 3, 2, 1][i]
		for h in range(height):
			hw = half * (1.0 - (h / (height + 0.4)) ** 2) ** 0.5
			for x in range(int(20 - hw), int(20 + hw)):
				edge = x in (int(20 - hw), int(20 + hw) - 1)
				tone = ramp[1] if edge else ramp[2] if h < height - 1 or i > 3 else ramp[3]
				c.put(x, 23 - h, tone)
		for x in range(20 - half, 20 + half):  # dark rim on the ground line
			c.put(x, 23, OUTLINE if x in (20 - half, 20 + half - 1) else ramp[1])
		if i in (1, 2, 3):
			c.put(20 - half // 2, 22 if height >= 2 else 23, ramp[4])
			c.put(20 - half // 2 + 1, 22 if height >= 2 else 23, ramp[3])
		if i == 0:
			# central burst blob
			for x in range(15, 26):
				for y in range(14, 22):
					dx, dy = x - 20, y - 20
					if dx * dx / 28.0 + dy * dy / 20.0 <= 1:
						c.put(x, y, ramp[4] if dy < -1 and dx < 0 else ramp[3] if dy < 1 else ramp[2])
		# droplets: leave a tail when fast, thin out when landing
		for vx, vy, size in drops:
			x = 20 + vx * t * 2.8
			y = 22 + vy * t * 3.6 + 1.5 * t * t
			if y > 22 or i == 5 and size == 2:
				continue
			xi, yi = int(x), int(y)
			if i < 3:
				goo(c, xi - int(vx > 0) * 0, yi + 2, ramp, 1) if i == 1 else None
			goo(c, xi, yi, ramp, size if i < 4 else 1)
			if size == 2 and i in (1, 2):
				goo(c, xi, yi - 1, ramp, 1)
		if wisps:
			for k in range(3):
				wx = 14 + k * 6 + (i % 2)
				wy = 14 - i * 2 - k
				if i < 5 and wy >= 0:
					c.put(wx, wy, CORRUPT[4] if i < 3 else CORRUPT[3])
					c.put(wx, wy + 1, CORRUPT[2])
		frames.append(c)
	return frames


def slime_hit(ramp):
	"""4 frames 24x16 centred (12, 8): goo sprays toward +x (flip for the other side)."""
	frames = []
	jets = [(1.8, -1.6), (2.4, -0.4), (1.2, -2.4), (2.8, -1.1), (0.9, 0.4)]
	for i in range(4):
		c = Canvas(24, 16)
		t = i + 1
		if i == 0:
			for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1)):
				c.put(7 + dx, 8 + dy, ramp[4] if dx == 0 and dy == 0 else ramp[3])
			star_cols = [WHITE, ramp[4]]
			for d in (1, 2, 3):
				c.put(7 + d, 8 - d // 2, star_cols[0] if d == 1 else ramp[4])
		for k, (vx, vy) in enumerate(jets):
			x = 7 + vx * t * 1.35
			y = 8 + vy * t * 1.3 + 0.55 * t * t
			if not (0 <= y < 16) or (i == 3 and k % 2):
				continue
			size = 2 if i < 3 and k < 4 else 1
			goo(c, int(x), int(y), ramp, size)
		frames.append(c)
	return frames


def gate_dust():
	"""7 frames 64x32, origin bottom-centre (32, 32): dust bursting from the gate base, gold glints."""
	frames = []
	dust = [STONE_COOL[5], STONE_COOL[4], STONE_COOL[3], STONE_COOL[2]]
	puffs = [(-14, 0), (-9, 1), (-4, 0), (4, 0), (9, 1), (14, 0)]
	for i in range(7):
		c = Canvas(64, 32)
		for k, (px, ph) in enumerate(puffs):
			t = i * 0.8
			r = 2 + t * 1.1 + (k % 2) * 0.6
			cx = 32 + px * (1 + 0.14 * i)
			cy = 30 - r * 0.7 - t * 0.9 - ph
			if i >= 6 and k % 2:
				continue
			tone = min(3, i // 2)
			for y in range(int(cy - r), int(cy + r) + 1):
				for x in range(int(cx - r), int(cx + r) + 1):
					d = (x - cx) ** 2 + (y - cy) ** 2
					if d <= r * r:
						if i >= 5 and (x + y) % 2:
							continue
						c.put(x, y, dust[min(3, tone + (1 if (x > cx and y > cy) else 0))] if d > r * r * 0.25 else dust[max(0, tone - 1)])
		# gold motes shaken loose, falling
		for k in range(8):
			if i < 1 or i > 5:
				continue
			mx = 32 - 18 + k * 5 + (k * 3) % 4
			my = 10 + ((i * 3 + k * 2) % 9) + i * 2
			if my < 31:
				c.put(mx, my, GOLD[4] if (i + k) % 3 == 0 else GOLD[3])
		frames.append(c)
	return frames


def main():
	sparkle = sheet(coin_sparkle(), 7)
	splash = sheet(slime_splash(SLIME_GREEN) + slime_splash(CORRUPT, True), 6)
	hit = sheet(slime_hit(SLIME_GREEN) + slime_hit(CORRUPT), 4)
	dust = sheet(gate_dust(), 7)
	save_png(sparkle, os.path.join(OUT, "vfx_coin_sparkle.png"))
	save_png(splash, os.path.join(OUT, "vfx_slime_splash.png"))
	save_png(hit, os.path.join(OUT, "vfx_slime_hit.png"))
	save_png(dust, os.path.join(OUT, "vfx_gate_dust.png"))
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
		bg = (52, 60, 66, 255)
		save_png(sparkle, os.path.join(preview, "sparkle_x6.png"), 6, bg)
		save_png(splash, os.path.join(preview, "splash_x5.png"), 5, bg)
		save_png(hit, os.path.join(preview, "hit_x8.png"), 8, bg)
		save_png(dust, os.path.join(preview, "dust_x4.png"), 4, bg)


if __name__ == "__main__":
	main()

"""N3 Black Forest terrain skin, readability pass (RUN-021).

RUN-020 earth (terrain_run020.earth_tile) sat too close to the forest backdrop: the walkable
masses read as holes in the night. This rebuild keeps the same tiles, layout and seeds, only
lifts the soil ramp one step toward a desaturated cold brown (Art Bible: terrain low to medium
contrast, walkable surfaces may get a slightly lighter rim) and brightens the moss rim's top
row by one step. Output layout matches terrain_stone.png theme 0 (18 rows x 16 masks).

Writes assets/run021/terrain_black_forest.png. tools/art/run020 is imported read only.
"""
import os
import sys

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "run020"))
from pixel import hexc, save_png, sheet  # noqa: E402
import terrain_run020 as base  # noqa: E402  (read only: functions reused, file untouched)

# Same five steps as palette_run020.SOIL, each lifted and nudged toward cold brown.
SOIL_LIFT = [hexc(c) for c in ("1d1b1f", "2b2729", "383236", "474045", "5a5258")]
# PINE with a lighter top-rim step (only used on the exposed top row by earth_tile).
PINE_LIFT = list(base.PINE[:4]) + [hexc("4d7065")]


def build():
	base.SOIL[:] = SOIL_LIFT
	base.PINE[:] = PINE_LIFT
	base.soil_strip.cache_clear()
	frames = []
	for seed in range(base.SEEDS):
		for phase in range(base.PHASES):
			for mask in range(16):
				frames.append(base.earth_tile(seed, phase, mask))
	return sheet(frames, 16)


def main():
	out = os.path.join(ROOT, "assets", "run021")
	os.makedirs(out, exist_ok=True)
	tiles = build()
	save_png(tiles, os.path.join(out, "terrain_black_forest.png"))
	preview = os.path.join(ROOT, "work", "run021", "preview")
	os.makedirs(preview, exist_ok=True)
	save_png(tiles, os.path.join(preview, "terrain_black_forest_x3.png"), 3)
	print("wrote", tiles.w, "x", tiles.h)


if __name__ == "__main__":
	main()

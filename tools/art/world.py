"""Generate the slice terrain, backdrop and props (RUN-013, enriched in RUN-029).

Usage: python3 tools/art/world.py [--preview DIR]

Terrain, tufts and vines live in world_terrain.py, backdrop layers in
world_bg.py, new decor props in world_props.py; this file keeps the narrative
props via world_narrative.py (houses, trees, cart, signpost, banner, blight, towers, ribbon spear) and
writes everything into assets/sprites/. Output is deterministic.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixel import Canvas, grid, hexc, save_png, sheet  # noqa: E402
from palette import (BLOOD, CORRUPT, EMBER, GOLD, MIST, MOSS, OUTLINE, SKY, STEEL,  # noqa: E402
	STONE, STONE_COOL, WOOD)
import world_bg  # noqa: E402
import world_narrative  # noqa: E402
import world_props  # noqa: E402
import world_terrain  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "sprites")
T = 16


def rng(*seed):
	return random.Random("-".join(map(str, seed)))


PROPS = world_narrative.PROPS


def main():
	preview = None
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
	tiles, tufts, vines = world_terrain.build_tiles()
	save_png(tiles, os.path.join(OUT, "terrain_stone.png"))
	save_png(tufts, os.path.join(OUT, "terrain_tufts.png"))
	save_png(vines, os.path.join(OUT, "env_vines.png"))
	layers = world_bg.build_all()
	for name, layer in layers.items():
		save_png(layer, os.path.join(OUT, name + ".png"))
	built = {name: make() for name, make in PROPS.items()}
	built.update({name: make() for name, make in world_props.PROPS.items()})
	for name, prop in built.items():
		save_png(prop, os.path.join(OUT, name + ".png"))
	if preview:
		save_png(tiles, os.path.join(preview, "tiles_x3.png"), 3, (52, 60, 66, 255))
		demo = Canvas(240, 120)
		solid = set()
		for x in range(15):
			for y in range(4, 7):
				solid.add((x, y))
		for x in range(8, 15):
			solid.add((x, 3))
		for x in range(1, 5):
			solid.add((x, 1))
		for (x, y) in solid:
			theme = 0 if x < 8 else 1
			mask = (1 if (x, y - 1) not in solid else 0) | (2 if (x + 1, y) not in solid else 0) | (4 if (x, y + 1) not in solid else 0) | (8 if (x - 1, y) not in solid else 0)
			row = theme * 18 + ((y % 3) * 6) + x % 6
			demo.blit(world_terrain.terrain_tile(world_terrain.THEME_ORDER[theme], y % 3, x % 6, mask), x * 16, y * 16)
		save_png(demo, os.path.join(preview, "terrain_demo_x4.png"), 4, (33, 42, 55, 255))
		for name in ("bg_sky", "bg_clouds", "bg_far", "bg_arches", "bg_mid", "bg_mist"):
			save_png(layers[name], os.path.join(preview, name + "_x2.png"), 2, (60, 20, 60, 255))
		comp = layers["bg_sky"].copy()
		comp.blit(layers["bg_clouds"], 0, 20)
		comp.blit(layers["bg_far"], 0, 58)
		comp.blit(layers["bg_arches"], 0, 140)
		comp.blit(layers["bg_mist"], 0, 150)
		comp.blit(layers["bg_mid"], 0, 100)
		comp.blit(layers["bg_mid"], 512, 100)
		save_png(comp, os.path.join(preview, "backdrop_x2.png"), 2)
		strip = Canvas(sum(p.w + 4 for p in built.values()), 170)
		x = 0
		for p in built.values():
			strip.blit(p, x, 170 - p.h)
			x += p.w + 4
		save_png(strip, os.path.join(preview, "props_x3.png"), 3, (33, 42, 55, 255))
	print("tiles", tiles.w, tiles.h, "tufts", tufts.w, tufts.h)


if __name__ == "__main__":
	main()

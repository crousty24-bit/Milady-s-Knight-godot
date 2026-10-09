"""Generate the N2-N4 presentation layer (RUN-020) into assets/run020/.

Usage: python3 tools/art/run020/biomes_run020.py [--preview DIR]

Original pixel art produced by code on the shared palette (no third-party pixels, no image
AI). Reads tools/art/{pixel,palette,world_terrain,world_bg,world_props}.py without modifying
them. Output is deterministic (identical MD5 on rerun).
"""
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from pixel import Canvas, save_png  # noqa: E402
import backdrop_run020  # noqa: E402
import props_run020  # noqa: E402
import terrain_run020  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "run020")


def main():
	os.makedirs(OUT, exist_ok=True)
	built = {}
	built.update(terrain_run020.build())
	built.update(backdrop_run020.build())
	built.update({name: make() for name, make in props_run020.PROPS.items()})
	for name, canvas in built.items():
		save_png(canvas, os.path.join(OUT, name + ".png"))
	if "--preview" in sys.argv:
		preview = sys.argv[sys.argv.index("--preview") + 1]
		os.makedirs(preview, exist_ok=True)
		for name, canvas in built.items():
			save_png(canvas, os.path.join(preview, name + "_x3.png"), 3, (52, 60, 66, 255))
		# Backdrop stacks at 1x, as the camera would show them at the reference framing.
		for biome in ("blight_town", "black_forrest", "forbidden_graveyard"):
			# Screen rows of scripts/campaign_backdrop.gd at the reference framing.
			view = built["bg_%s_sky" % biome].copy()
			view.blit(built["bg_%s_far" % biome], 0, 58)
			mid = built["bg_%s_mid" % biome]
			view.blit(mid, 0, 104)
			view.blit(mid, mid.w, 104)
			save_png(view, os.path.join(preview, "stack_%s_x2.png" % biome), 2)
	print("wrote %d files to %s" % (len(built), OUT))


if __name__ == "__main__":
	main()
	_ = Canvas

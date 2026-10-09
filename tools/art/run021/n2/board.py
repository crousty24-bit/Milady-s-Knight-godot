"""Preview board: stacks PNGs (optionally upscaled, over a background colour) into one image.
Usage: python3 board.py out.png scale bg_hex in1.png [in2.png ...]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "run020_feedback"))
from pixel import Canvas, hexc, save_png  # noqa: E402
from pngio import load_png  # noqa: E402


def main():
	out, scale, bg = sys.argv[1], int(sys.argv[2]), hexc(sys.argv[3])
	imgs = [load_png(p) for p in sys.argv[4:]]
	W = max(i.w for i in imgs)
	H = sum(i.h + 4 for i in imgs)
	b = Canvas(W, H)
	b.rect(0, 0, W, H, bg)
	y = 0
	for i in imgs:
		b.blit(i, 0, y)
		y += i.h + 4
	save_png(b, out, scale)


if __name__ == "__main__":
	main()

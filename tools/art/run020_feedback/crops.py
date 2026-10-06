"""Integer x3 crops (240x135 source region -> 720x405) of the native captures, for inspection only."""
import os, sys
sys.path.insert(0, '..')
from pngio import load_png, crop
from pixel import save_png
D = sys.argv[1]
for n in sorted(os.listdir(D)):
	if not n.endswith('.png') or n.endswith('_x3.png'): continue
	cv = load_png(os.path.join(D, n))
	# locate the brightest-ish elite: use fixed window centred on screen x (camera follows the player)
	x0 = int(sys.argv[2]) if len(sys.argv) > 2 else 200
	c = crop(cv, x0, 130, 240, 120)
	save_png(c, os.path.join(D, n.replace('.png', '_x3.png')), 3)

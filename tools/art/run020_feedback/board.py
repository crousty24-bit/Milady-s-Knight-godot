"""Before/after comparison board (integer x4): knight idle, OLD/NEW Bloated, OLD/NEW Chud on one baseline.
Usage: python3 board.py OUT.png  (reads assets/sprites/ashen_knight.png, assets/run019 and assets/run020_feedback)"""
import os, sys
sys.path.insert(0, '..')
from pngio import load_png, crop, frames_of
from pixel import Canvas, save_png
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
A = lambda *p: os.path.join(ROOT, 'assets', *p)
knight = crop(load_png(A('sprites', 'ashen_knight.png')), 0, 0, 64, 64)
ob = frames_of(load_png(A('run019', 'enemies', 'bloated_slime.png')), 40, 32, 20)
oc = frames_of(load_png(A('run019', 'enemies', 'chud_blob.png')), 48, 36, 26)
rs = frames_of(load_png(A('run019', 'enemies', 'enemy_slime_red.png')), 24, 24, 14)
nb = frames_of(load_png(A('run020_feedback', 'enemies', 'bloated_slime.png')), 72, 56, 20)
nc = frames_of(load_png(A('run020_feedback', 'enemies', 'chud_blob.png')), 96, 64, 26)
items = [('knight', knight), ('red', rs[0]), ('old_bloated', ob[0]), ('new_bloated', nb[0]), ('old_chud', oc[0]), ('new_chud', nc[0])]
W, H, BASE = 6 * 100 + 20, 84, 76
bg = Canvas(W, H)
bg.rect(0, 0, W, H, (24, 27, 35, 255))
bg.rect(0, BASE, W, H - BASE, (57, 54, 63, 255))
for h in range(16, 80, 16):  # 16 px reference ticks
	for x in range(0, W, 4):
		bg.put(x, BASE - h, (70, 76, 90, 255))
cx = 10
for name, f in items:
	bb = f.bbox()
	w, h = bb[2] - bb[0], bb[3] - bb[1]
	sub = crop(f, bb[0], bb[1], w, h)
	bg.blit(sub, cx + (100 - w) // 2 - 5, BASE - h)
	print('%-12s opaque bbox %dx%d' % (name, w, h))
	cx += 100
save_png(bg, sys.argv[1], 4)

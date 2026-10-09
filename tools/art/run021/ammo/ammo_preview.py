"""Preview-only helpers for ammo_art.py: contact sheet and in-context mock-ups (no game asset written here).

Reads project art read-only (knight idle cell, stone terrain tile, Blight Town decorative barrels, coin, ui_plate)
to judge scale, value and family readability at native 1x. HUD digits use a tiny 3x5 stand-in font,
not PixelOperator8: the mock-up shows layout and colour only.
"""
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ART)
from pixel import Canvas, save_png  # noqa: E402
from palette import BLOOD, GOLD, STONE  # noqa: E402

ROOT = os.path.normpath(os.path.join(ART, "..", ".."))
BG = (22, 24, 31, 255)


def read_png(path):
	"""RGBA8 non-interlaced PNG reader (same approach as tools/art/run018/world_items.py)."""
	d = open(path, "rb").read()
	pos, idat, w, h = 8, b"", 0, 0
	while pos < len(d):
		n, kind = struct.unpack(">I4s", d[pos:pos + 8])
		body = d[pos + 8:pos + 8 + n]
		if kind == b"IHDR":
			w, h = struct.unpack(">II", body[:8])
			assert body[8] == 8 and body[9] == 6, path
		elif kind == b"IDAT":
			idat += body
		pos += 12 + n
	raw = zlib.decompress(idat)
	stride = w * 4
	c = Canvas(w, h)
	prev = bytearray(stride)
	p = 0
	for y in range(h):
		f = raw[p]
		cur = bytearray(raw[p + 1:p + 1 + stride])
		p += 1 + stride
		for i in range(stride):
			l = cur[i - 4] if i >= 4 else 0
			u = prev[i]
			ul = prev[i - 4] if i >= 4 else 0
			if f == 1:
				cur[i] = (cur[i] + l) & 255
			elif f == 2:
				cur[i] = (cur[i] + u) & 255
			elif f == 3:
				cur[i] = (cur[i] + (l + u) // 2) & 255
			elif f == 4:
				pa, pb, pc = abs(u - ul), abs(l - ul), abs(l + u - 2 * ul)
				cur[i] = (cur[i] + (l if pa <= pb and pa <= pc else u if pb <= pc else ul)) & 255
		prev = cur
		for x in range(w):
			px = tuple(cur[x * 4:x * 4 + 4])
			if px[3] > 0:
				c.put(x, y, px)
	return c


def sub(src, x, y, w, h):
	c = Canvas(w, h)
	for yy in range(h):
		for xx in range(w):
			c.put(xx, yy, src.get(x + xx, y + yy))
	return c


def frame(strip, i, fw, fh):
	return sub(strip, i * fw, 0, fw, fh)


def load(rel):
	try:
		return read_png(os.path.join(ROOT, rel))
	except Exception as e:  # preview only
		print("reference skipped:", rel, e)
		return None


DIGITS = {
	"0": ("111", "101", "101", "101", "111"), "1": ("010", "110", "010", "010", "111"),
	"2": ("111", "001", "111", "100", "111"), "3": ("111", "001", "111", "001", "111"),
	"5": ("111", "100", "111", "001", "111"), "/": ("001", "001", "010", "100", "100"),
	"7": ("111", "001", "010", "010", "010"), "+": ("000", "010", "111", "010", "000"),
	"F": ("111", "100", "110", "100", "100"), "U": ("101", "101", "101", "101", "111"),
	"L": ("100", "100", "100", "100", "111"),
}


def text(c, s, x, y, col):
	for ch in s:
		g = DIGITS.get(ch)
		if g:
			for yy, row in enumerate(g):
				for xx, b in enumerate(row):
					if b == "1":
						c.put(x + xx + 1, y + yy + 1, (0, 0, 0, 160))
						c.put(x + xx, y + yy, col)
		x += 4


def nine(c, src, x, y, w, h, m=4):
	sw, sh = src.w, src.h
	for yy in range(h):
		sy = yy if yy < m else (sh - (h - yy)) if yy >= h - m else m + (yy - m) % (sh - 2 * m)
		for xx in range(w):
			sx = xx if xx < m else (sw - (w - xx)) if xx >= w - m else m + (xx - m) % (sw - 2 * m)
			c.put(x + xx, y + yy, src.get(sx, sy))


def ground(c, top, tile):
	for y in range(top, c.h):
		for x in range(c.w):
			if tile is not None:
				c.put(x, y, tile.get(x % 16, (y - top) % 16))
			else:
				c.put(x, y, STONE[3])


def contact_sheet(outputs):
	pad = 4
	rows = list(outputs.values())
	w = max(cv.w for cv in rows) + 2 * pad
	h = sum(cv.h + pad for cv in rows) + pad
	s = Canvas(w, h)
	s.rect(0, 0, w, h, BG)
	y = pad
	for cv in rows:
		s.blit(cv, pad, y)
		y += cv.h + pad
	return s


def mock_world(outputs):
	"""Native 1x scene: knight, decorative barrels, coins, the four props, a break sequence and pickups on stone."""
	w, h = 400, 112
	c = Canvas(w, h)
	c.rect(0, 0, w, h, (17, 19, 26, 255))
	for y in range(0, 80):  # faint back wall so dark outlines are judged against a mid-dark value
		for x in range(w):
			if (x // 16 + y // 8) % 2 == 0 and y % 8 != 7:
				c.put(x, y, (27, 28, 36, 255))
	floor = 80
	terrain = load("assets/sprites/terrain_stone.png")
	tile = sub(terrain, 0, 0, 16, 16) if terrain else None
	ground(c, floor, tile)
	kn = load("assets/sprites/ashen_knight.png")
	if kn:
		cell = sub(kn, 0, 0, 64, 64)
		bb = cell.bbox()
		c.blit(cell, 4, floor - bb[3])
	deco = load("assets/run020/blight_town_barrels.png")
	if deco:
		c.blit(deco, 60, floor - deco.h)
	x = 96
	for name in ("prop_crate.png", "prop_barrel.png", "prop_crate.png", "prop_barrel.png"):
		c.blit(outputs[name], x, floor - 32)
		x += 34
	brk = outputs["prop_barrel_break.png"]
	for i in (0, 2, 3, 5):
		c.blit(frame(brk, i, 32, 32), x, floor - 32)
		x += 34
	coin = load("assets/sprites/item_gold_coin.png")
	if coin:
		c.blit(frame(coin, 0, 16, 16), 50, floor - 22)
	c.blit(frame(outputs["pickup_arrows.png"], 0, 16, 16), 330, floor - 16)
	c.blit(frame(outputs["pickup_knives.png"], 2, 16, 16), 348, floor - 16)
	c.blit(frame(outputs["vfx_ammo_pickup.png"], 1, 16, 16), 366, floor - 16)
	c.blit(frame(outputs["pickup_arrows.png"], 1, 16, 16), 384, floor - 16)
	return c


def mock_hud(outputs):
	"""Equipment cluster as in scenes/hud.tscn (absolute 8,44) with the proposed AmmoPlate at local (94,17)-(146,32)."""
	w, h = 170, 48
	c = Canvas(w, h)
	c.rect(0, 0, w, h, (17, 19, 26, 255))
	plate = load("assets/sprites/ui_plate.png")
	slots = load("assets/sprites/ui_slot_icons.png")
	icons = outputs["ui_ammo_icons.png"]
	ox, oy = 4, 4
	states = ((0, "10/15", None), (1, "20/20", GOLD[3]), (2, "0/15", BLOOD[3]))
	if plate:
		nine(c, plate, ox, oy, 92, 15)
		nine(c, plate, ox, oy + 17, 92, 15)
		nine(c, plate, ox + 94, oy + 17, 52, 15)
	if slots:
		c.blit(frame(slots, 0, 12, 12), ox + 3, oy + 2)
		c.blit(frame(slots, 1, 12, 12), ox + 3, oy + 19)
	c.blit(frame(icons, 0, 12, 12), ox + 97, oy + 19)
	text(c, "10/15", ox + 111, oy + 22, (228, 228, 232, 255))
	# state strip below: knives full, arrows empty, pickup popup
	y = 40 - 4
	for k, (idx, label, col) in enumerate(states[1:]):
		bx = 4 + k * 56
		c.blit(frame(icons, (1, 2)[k], 12, 12), bx, y - 4)
		text(c, label, bx + 14, y - 1, col)
	c.blit(frame(icons, 1, 12, 12), 116, y - 4)
	text(c, "+3", 130, y - 1, GOLD[3])
	return c


def write(outputs, preview):
	cs = contact_sheet(outputs)
	save_png(cs, os.path.join(preview, "contact_sheet_x4.png"), 4)
	mw = mock_world(outputs)
	save_png(mw, os.path.join(preview, "mock_world_x1.png"), 1)
	save_png(mw, os.path.join(preview, "mock_world_x3.png"), 3)
	mh = mock_hud(outputs)
	save_png(mh, os.path.join(preview, "mock_hud_x1.png"), 1)
	save_png(mh, os.path.join(preview, "mock_hud_x4.png"), 4)

"""Minimal PNG loader (8-bit RGBA/RGB, non-interlaced) -> pixel.Canvas, no external deps."""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from pixel import Canvas  # noqa: E402


def load_png(path):
	d = open(path, "rb").read()
	pos = 8
	idat = b""
	w = h = ct = 0
	while pos < len(d):
		ln, kind = struct.unpack(">I4s", d[pos:pos + 8])
		body = d[pos + 8:pos + 8 + ln]
		if kind == b"IHDR":
			w, h, bd, ct = struct.unpack(">IIBB", body[:10])
			assert bd == 8 and ct in (2, 6)
		elif kind == b"IDAT":
			idat += body
		pos += 12 + ln
	bpp = 4 if ct == 6 else 3
	raw = zlib.decompress(idat)
	stride = w * bpp
	rows = []
	prev = bytearray(stride)
	i = 0
	for _ in range(h):
		f = raw[i]
		line = bytearray(raw[i + 1:i + 1 + stride])
		i += 1 + stride
		for x in range(stride):
			a = line[x - bpp] if x >= bpp else 0
			b = prev[x]
			c = prev[x - bpp] if x >= bpp else 0
			if f == 1:
				line[x] = (line[x] + a) & 255
			elif f == 2:
				line[x] = (line[x] + b) & 255
			elif f == 3:
				line[x] = (line[x] + (a + b) // 2) & 255
			elif f == 4:
				p = a + b - c
				pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
				pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
				line[x] = (line[x] + pr) & 255
		rows.append(line)
		prev = line
	cv = Canvas(w, h)
	for y in range(h):
		for x in range(w):
			o = x * bpp
			r, g, b = rows[y][o], rows[y][o + 1], rows[y][o + 2]
			a = rows[y][o + 3] if bpp == 4 else 255
			if a:
				cv.px[y * w + x] = (r, g, b, a)
	return cv


def crop(cv, x0, y0, w, h):
	out = Canvas(w, h)
	for y in range(h):
		for x in range(w):
			out.px[y * w + x] = cv.px[(y0 + y) * cv.w + x0 + x]
	return out


def frames_of(cv, cw, ch, n):
	return [crop(cv, i * cw, 0, cw, ch) for i in range(n)]

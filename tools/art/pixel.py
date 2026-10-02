"""Tiny dependency-free pixel-art toolkit used by the sprite generators.

Sprites are authored as text grids: one character per pixel, '.' or ' ' is
transparent and every other character maps to a palette colour. Layers are
composited onto fixed-size frames, then packed into sheets written as PNG.
"""
import math
import struct
import zlib

Color = tuple  # (r, g, b, a)


def hexc(value: str, alpha: int = 255) -> Color:
	return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


class Canvas:
	def __init__(self, width: int, height: int):
		self.w = width
		self.h = height
		self.px = [None] * (width * height)

	def get(self, x: int, y: int):
		if 0 <= x < self.w and 0 <= y < self.h:
			return self.px[y * self.w + x]
		return None

	def put(self, x: int, y: int, color) -> None:
		if color is None or not (0 <= x < self.w and 0 <= y < self.h):
			return
		if len(color) == 4 and color[3] < 255:
			under = self.px[y * self.w + x]
			if under is not None and color[3] > 0:
				a = color[3] / 255.0
				color = tuple(int(round(color[i] * a + under[i] * (1 - a))) for i in range(3)) + (max(color[3], under[3]),)
			elif color[3] == 0:
				return
		self.px[y * self.w + x] = color

	def blit(self, other: "Canvas", dx: int, dy: int, flip: bool = False) -> None:
		for y in range(other.h):
			for x in range(other.w):
				c = other.px[y * other.w + x]
				if c is not None:
					self.put(dx + (other.w - 1 - x if flip else x), dy + y, c)

	def rect(self, x: int, y: int, w: int, h: int, color) -> None:
		for yy in range(y, y + h):
			for xx in range(x, x + w):
				self.put(xx, yy, color)

	def copy(self) -> "Canvas":
		c = Canvas(self.w, self.h)
		c.px = list(self.px)
		return c

	def bbox(self):
		xs = [i % self.w for i, c in enumerate(self.px) if c is not None]
		ys = [i // self.w for i, c in enumerate(self.px) if c is not None]
		if not xs:
			return None
		return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def grid(text: str, palette: dict) -> Canvas:
	"""Parse a text grid. Leading newline and common indentation are ignored."""
	rows = text.strip("\n").split("\n")
	indent = min(len(r) - len(r.lstrip("\t")) for r in rows if r.strip())
	rows = [r[indent:] for r in rows]
	canvas = Canvas(max(len(r) for r in rows), len(rows))
	for y, row in enumerate(rows):
		for x, ch in enumerate(row):
			if ch in palette:
				canvas.put(x, y, palette[ch])
	return canvas


def remap(canvas: Canvas, mapping: dict) -> Canvas:
	"""Return a copy with exact colours substituted (used for shading variants)."""
	out = canvas.copy()
	out.px = [mapping.get(c, c) if c is not None else None for c in out.px]
	return out


def outline(canvas: Canvas, color: Color) -> Canvas:
	"""Add a 1 px outline around opaque pixels (4-neighbourhood)."""
	out = canvas.copy()
	for y in range(canvas.h):
		for x in range(canvas.w):
			if canvas.get(x, y) is None and any(canvas.get(x + dx, y + dy) is not None for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
				out.put(x, y, color)
	return out


def line(canvas: Canvas, x0: float, y0: float, x1: float, y1: float, color) -> None:
	steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
	for i in range(steps + 1):
		t = i / steps
		canvas.put(int(math.floor(x0 + (x1 - x0) * t + 0.5)), int(math.floor(y0 + (y1 - y0) * t + 0.5)), color)


def sheet(frames: list, columns: int) -> Canvas:
	fw, fh = frames[0].w, frames[0].h
	rows = (len(frames) + columns - 1) // columns
	out = Canvas(fw * columns, fh * rows)
	for i, f in enumerate(frames):
		out.blit(f, (i % columns) * fw, (i // columns) * fh)
	return out


def save_png(canvas: Canvas, path: str, scale: int = 1, background=None) -> None:
	raw = bytearray()
	for y in range(canvas.h * scale):
		raw.append(0)
		for x in range(canvas.w * scale):
			c = canvas.px[(y // scale) * canvas.w + (x // scale)]
			if c is None:
				c = background if background is not None else (0, 0, 0, 0)
			raw.extend(bytes(c[:4]))

	def chunk(kind: bytes, data: bytes) -> bytes:
		return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

	header = struct.pack(">IIBBBBB", canvas.w * scale, canvas.h * scale, 8, 6, 0, 0, 0)
	with open(path, "wb") as f:
		f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))

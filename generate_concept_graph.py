# -*- coding: utf-8 -*-
"""generate_concept_graph.py — 哲学エンジンの概念グラフPNGを標準ライブラリのみで生成"""
import zlib
import struct
import os

W, H = 700, 400
BG = (22, 26, 30)
NODE_FILL = (45, 55, 70)
NODE_BORDER = (120, 180, 255)
TEXT_COLOR = (235, 240, 245)
EDGE_COLOR = (100, 130, 160)

nodes = [
    (120, 200, "Spinoza"),
    (320, 100, "デカルト"),
    (320, 300, "カント"),
    (520, 200, "ライプニッツ"),
]
edges = [
    (1, 0),
    (2, 0),
    (0, 3),
]


def rgb(r, g, b):
    return bytes([r, g, b])


def make_png(width, height, pixels):
    raw = b""
    for y in range(height):
        raw += b"\x00"
        for x in range(width):
            r, g, b = pixels[y][x]
            raw += bytes([r, g, b])

    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

    compressed = zlib.compress(raw, 6)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    return png


def draw_rect(pixels, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < W and 0 <= y < H:
                pixels[y][x] = color


def draw_line(pixels, x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        if 0 <= x < W and 0 <= y < H:
            pixels[y][x] = color
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def main():
    pixels = [[BG for _ in range(W)] for _ in range(H)]

    for i, j in edges:
        x0, y0, _ = nodes[i]
        x1, y1, _ = nodes[j]
        draw_line(pixels, x0 + 25, y0, x1 - 25, y1, EDGE_COLOR)

    for x, y, label in nodes:
        draw_rect(pixels, x, y - 12, x + 50, y + 12, NODE_FILL)
        for dx in range(x, x + 51):
            if 0 <= dx < W:
                pixels[y - 12][dx] = NODE_BORDER
                pixels[y + 12][dx] = NODE_BORDER
        for dy in range(y - 12, y + 13):
            if 0 <= dy < H:
                pixels[dy][x] = NODE_BORDER
                pixels[dy][x + 50] = NODE_BORDER

    png = make_png(W, H, pixels)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "philosophy-engine-concept-graph.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(png)
    print("生成完了:", out, len(png), "bytes")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Draw 'Golden Honey Drip' — one hero ingredient, honey, big in frame.

Renders a warm amber scene: a wooden honey dipper held diagonally, a thick
golden ribbon of honey dripping from its grooved head into a glossy pool,
with a tiny clean caption. Drawn at 2x and downscaled for smooth edges.
Deterministic: fixed seed, no randomness in the final pixels.
"""
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2                      # supersample factor
W = H = 1024 * S           # working canvas
OUT = "/home/hatch/workspace/makefun/the-picture-that-tastes-of-one-20261122-2047-entry/entry.png"

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def honey_color(t):
    """Golden honey ramp: pale gold -> deep amber."""
    stops = [(255, 214, 110), (247, 178, 52), (226, 138, 18), (178, 96, 8)]
    if t <= 0:
        return stops[0]
    if t >= 1:
        return stops[-1]
    seg = t * (len(stops) - 1)
    i = int(seg)
    return lerp(stops[i], stops[i + 1], seg - i)


# ---------------------------------------------------------------- background
img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)
top, mid, bot = (62, 28, 5), (128, 70, 14), (38, 17, 3)
for y in range(H):
    t = y / H
    c = lerp(top, mid, t / 0.55) if t < 0.55 else lerp(mid, bot, (t - 0.55) / 0.45)
    d.line([(0, y), (W, y)], fill=c)

# warm radial glow behind the dipper
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
cx, cy = W // 2, int(H * 0.42)
for r in range(1150, 0, -10):
    a = int(64 * (1 - r / 1150) ** 2)
    gd.ellipse([cx - r, cy - int(r * 0.8), cx + r, cy + int(r * 0.8)],
               fill=(255, 172, 44, a))
img = Image.alpha_composite(img.convert("RGBA"), glow)
d = ImageDraw.Draw(img)

# faint honeycomb hexagons in the upper corners, low alpha
comb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cd = ImageDraw.Draw(comb)
hex_r = 150
for row in range(-1, 4):
    for col in range(-1, 7):
        hx = 210 + col * int(hex_r * 1.5) + (row % 2) * int(hex_r * 0.75)
        hy = 120 + row * int(hex_r * 1.3)
        pts = [(hx + hex_r * math.cos(math.radians(60 * k)),
                hy + hex_r * math.sin(math.radians(60 * k))) for k in range(6)]
        cd.polygon(pts, outline=(255, 190, 80, 16), width=6)
img = Image.alpha_composite(img, comb)
d = ImageDraw.Draw(img)

# ------------------------------------------------------------- honey pool
pool_cx, pool_cy = W // 2, int(H * 0.86)
pool_rx, pool_ry = 800, 250
for i in range(60, 0, -1):
    t = i / 60
    rx, ry = pool_rx * t, pool_ry * t
    d.ellipse([pool_cx - rx, pool_cy - ry, pool_cx + rx, pool_cy + ry],
              fill=honey_color(0.15 + 0.75 * (1 - t)))
d.ellipse([pool_cx - pool_rx, pool_cy - pool_ry,
           pool_cx + pool_rx, pool_cy + pool_ry],
          outline=(120, 58, 4), width=10)
# swirl arcs in the pool
for k, (rr, a0, a1) in enumerate([(560, 200, 340), (380, 20, 160), (200, 180, 320)]):
    d.arc([pool_cx - rr, pool_cy - int(rr * 0.31),
           pool_cx + rr, pool_cy + int(rr * 0.31)],
          a0, a1, fill=(150, 80, 6), width=14)

# ------------------------------------------------------------- honey dipper
# Head: grooved bulb drawn horizontally on its own layer, then rotated.
head = Image.new("RGBA", (900, 460), (0, 0, 0, 0))
hd = ImageDraw.Draw(head)
# bulb body: stacked rounded discs (the grooves of a dipper)
discs = [(70, 60, 760, 400), (150, 30, 700, 430), (230, 10, 640, 450),
         (310, 0, 580, 460), (390, 10, 540, 450), (470, 30, 500, 430),
         (540, 60, 640, 380)]
wood_light, wood_mid, wood_dark = (196, 138, 62), (168, 108, 40), (122, 74, 22)
for i, (x0, y0, x1, y1) in enumerate(discs):
    tone = wood_light if i % 2 == 0 else wood_mid
    hd.ellipse([x0, y0, x1, y1], fill=tone + (255,))
    hd.ellipse([x0, y0, x1, y1], outline=wood_dark + (255,), width=8)
# honey coating over the lower half of the head, glossy and dripping
coat = Image.new("RGBA", (900, 460), (0, 0, 0, 0))
cd2 = ImageDraw.Draw(coat)
for x in range(60, 780, 4):
    wob = 30 * math.sin(x / 90.0)
    top_y = 250 + wob
    cd2.line([(x, top_y), (x, 430)], fill=honey_color(0.35) + (200,), width=4)
cd2.ellipse([60, 210, 780, 330], fill=honey_color(0.25) + (120,))
head = Image.alpha_composite(head, coat)
head = head.filter(ImageFilter.GaussianBlur(2.5))
head = head.rotate(-32, expand=True, resample=Image.BICUBIC)
img.paste(head, (430, 480), head)
d = ImageDraw.Draw(img)

# handle: thick wooden stick from the head up to the top-right
hx0, hy0 = 1080, 760      # where it meets the head
hx1, hy1 = 1720, 190      # top end
d.line([(hx0, hy0), (hx1, hy1)], fill=wood_dark, width=96)
d.line([(hx0, hy0), (hx1, hy1)], fill=wood_mid, width=72)
d.line([(hx0 - 12, hy0 - 26), (hx1 - 12, hy1 - 26)], fill=wood_light, width=22)
d.ellipse([hx1 - 52, hy1 - 52, hx1 + 52, hy1 + 52], fill=wood_mid)
d.ellipse([hx1 - 52, hy1 - 52, hx1 + 52, hy1 + 52], outline=wood_dark, width=8)
d.ellipse([hx1 - 22, hy1 - 22, hx1 + 22, hy1 + 22], fill=wood_light)

# ------------------------------------------- honey ribbon: head -> pool
# thick wavy ribbon falling from the dipper head, with a droplet at its tip
ribbon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(ribbon)
start_y, end_y = 1080, 1660
top_x = 700
pts_left, pts_right = [], []
for y in range(start_y, end_y + 1, 8):
    f = (y - start_y) / (end_y - start_y)
    cxr = top_x + 46 * math.sin((y - start_y) / 260.0) + 26 * f
    half = 62 - 34 * f + 10 * math.sin(y / 90.0)
    pts_left.append((cxr - half, y))
    pts_right.append((cxr + half, y))
rd.polygon(pts_left + pts_right[::-1], fill=honey_color(0.45) + (255,))
# droplet forming at the tip, about to fall
drop_cy = end_y + 78
rd.ellipse([top_x - 26, drop_cy - 95, top_x + 92, drop_cy + 55],
           fill=honey_color(0.4) + (255,))
rd.ellipse([top_x + 8, drop_cy - 30, top_x + 76, drop_cy + 52],
           fill=honey_color(0.15) + (255,))
# thin secondary thread beside the ribbon
for y in range(1150, 1560, 6):
    x = 880 + 18 * math.sin(y / 170.0)
    rd.line([(x, y), (x, y + 6)], fill=honey_color(0.5) + (230,), width=10)
ribbon = ribbon.filter(ImageFilter.GaussianBlur(2))
img = Image.alpha_composite(img, ribbon)
d = ImageDraw.Draw(img)

# gloss highlights on the ribbon and the pool (soft white streaks)
hi = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd2 = ImageDraw.Draw(hi)
hd2.line([(668, 1120), (700, 1620)], fill=(255, 240, 200, 150), width=26)
hd2.line([(636, 1140), (664, 1580)], fill=(255, 244, 210, 90), width=12)
hd2.arc([pool_cx - 640, pool_cy - 150, pool_cx + 640, pool_cy + 150],
        195, 335, fill=(255, 236, 180, 170), width=30)
hd2.arc([pool_cx - 500, pool_cy - 110, pool_cx + 500, pool_cy + 110],
        205, 325, fill=(255, 244, 205, 110), width=14)
hi = hi.filter(ImageFilter.GaussianBlur(6))
img = Image.alpha_composite(img, hi)
d = ImageDraw.Draw(img)

# small bubbles in the pool
for (bx, by, br) in [(760, 1720, 26), (1330, 1760, 18), (1180, 1810, 12)]:
    d.ellipse([bx - br, by - br, bx + br, by + br],
              outline=(255, 220, 130), width=5)
    d.ellipse([bx - br // 2, by - br // 2, bx, by],
              fill=(255, 240, 190))

# ---------------------------------------------------------------- caption
serif = ImageFont.truetype(FONT_SERIF, 116)
sans = ImageFont.truetype(FONT_SANS, 46)
word = "HONEY"
# letterspaced, centred
widths = [d.textlength(ch, font=serif) for ch in word]
total = sum(widths) + 26 * (len(word) - 1)
x = (W - total) // 2
y_text = 1860
for ch, wch in zip(word, widths):
    d.text((x, y_text), ch, font=serif, fill=(255, 214, 130))
    x += wch + 26
sub = "ONE INGREDIENT  ·  PURE GOLD"
sw = d.textlength(sub, font=sans)
d.text(((W - sw) // 2, y_text + 132), sub, font=sans, fill=(232, 178, 96))

# ------------------------------------------------------------- save 1024
final = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
final.save(OUT, format="PNG", optimize=True)
print("saved", OUT)

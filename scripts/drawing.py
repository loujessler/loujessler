from functools import lru_cache
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = Path(__file__).with_name("fonts")
SCALE = 2
INK = "#0d0d18"
PAPER = "#f5f2ff"
MUTED = "#cbc7de"
PANEL = "#18182c"
INNER = "#22223e"
CORAL = "#ff8964"
BLUE, GREEN, OCHRE = "#294a77", "#23593d", "#784b20"
PURPLE, RED, TEAL = "#4c3c78", "#783341", "#205661"


@lru_cache(maxsize=128)
def font(size, face="bold"):
    if face == "mono":
        return ImageFont.truetype(FONTS / "IBMPlexMono-Medium.ttf", round(size * SCALE))
    result = ImageFont.truetype(FONTS / "Nunito.ttf", round(size * SCALE))
    result.set_variation_by_axes([1000 if face == "bold" else 750])
    return result


def width(text, size, face="bold"):
    return font(size, face).getlength(text) / SCALE


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.image = Image.new("RGBA", (round(w * SCALE), round(h * SCALE)))
        self.draw = ImageDraw.Draw(self.image)

    def rect(self, box, color, radius=0, edge=None, weight=1):
        self.draw.rounded_rectangle(
            tuple(round(v * SCALE) for v in box), round(radius * SCALE), fill=color,
            outline=edge, width=round(weight * SCALE),
        )

    def line(self, points, color, weight=1):
        self.draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                       fill=color, width=round(weight * SCALE), joint="curve")

    def polygon(self, points, color):
        self.draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=color)

    def text(self, x, y, value, size, color=PAPER, face="bold", anchor="lt"):
        self.draw.text((round(x * SCALE), round(y * SCALE)), value,
                       font=font(size, face), fill=color, anchor=anchor)

    def place(self, other, x, y, angle=0):
        image = other.image
        if angle:
            image = image.rotate(angle, Image.Resampling.BICUBIC, expand=True)
        left = round(x * SCALE - (image.width - other.image.width) / 2)
        top = round(y * SCALE - (image.height - other.image.height) / 2)
        self.image.alpha_composite(image, (left, top))

    def save(self, name):
        indexed = self.image.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        indexed.save(ASSETS / name, optimize=True)


def panel(w, h):
    canvas = Canvas(w, h)
    canvas.rect((1, 3, w-2, h-1), INK, 22)
    canvas.rect((1, 1, w-3, h-4), PANEL, 22, INK, 2)
    for y in range(14, h-10, 28):
        for x in range(14, w-10, 28):
            canvas.rect((x-1, y-1, x+1.5, y+1.5), "#323248", 1.25)
    return canvas


def sticker(w, h, color, radius=14):
    canvas = Canvas(w, h)
    canvas.rect((3, 4, w-1, h-1), INK, radius)
    canvas.rect((0, 0, w-4, h-5), color, radius, INK, 2.6)
    return canvas


def icon(canvas, name, x, y, size, color=CORAL, edge=INK):
    unit = size / 24

    def points(coords):
        return [(x + a*unit, y + b*unit) for a, b in coords]

    def stroke(coords, ink=edge, weight=1.9):
        canvas.line(points(coords), ink, weight*unit)

    def shape(coords):
        canvas.polygon(points(coords), color)
        stroke([*coords, coords[0]])

    def rect(a, b, c, d, radius=2):
        canvas.rect((x+a*unit, y+b*unit, x+c*unit, y+d*unit), color, radius*unit, edge, 1.8*unit)

    if name == "calendar":
        rect(2, 4, 22, 22)
        stroke([(3, 10), (21, 10)])
        stroke([(7, 2), (7, 7)])
        stroke([(17, 2), (17, 7)])
    elif name == "flame":
        shape([(11, 1), (16, 7), (17, 11), (20, 7), (22, 13), (21, 18),
               (18, 21), (13, 23), (8, 22), (4, 19), (3, 15), (5, 10), (8, 13),
               (10, 10), (12, 7)])
    elif name == "trophy":
        stroke([(6, 5), (2, 5), (2, 9), (4, 12), (8, 13)], color, 3)
        stroke([(18, 5), (22, 5), (22, 9), (20, 12), (16, 13)], color, 3)
        shape([(6, 2), (18, 2), (17, 11), (15, 14), (12, 16), (9, 14), (7, 11)])
        stroke([(12, 15), (12, 20)], color, 2.6)
        rect(6, 20, 18, 23, 1)
    elif name == "chart":
        for left, top in ((2, 13), (9, 4), (16, 9)):
            rect(left, top, left+4.5, 22, 0.6)
    elif name == "folder":
        shape([(2, 4), (9, 4), (12, 7), (21, 7), (22, 9), (22, 20), (20, 21), (3, 21), (1, 19), (1, 6)])
    elif name == "star":
        coords = []
        for i in range(10):
            angle = -pi/2 + i*pi/5
            radius = 11.2 if i % 2 == 0 else 5.2
            coords.append((12 + radius*cos(angle), 12 + radius*sin(angle)))
        shape(coords)
    elif name == "download":
        shape([(9, 2), (15, 2), (15, 10), (20, 10), (12, 18), (4, 10), (9, 10)])
        rect(2, 19, 22, 22, 0.6)
    elif name == "desktop":
        rect(1, 3, 23, 17)
        stroke([(5, 13), (19, 13)])
        stroke([(12, 17), (12, 21)], color, 2.4)
        stroke([(7, 21), (17, 21)], color, 2.4)
    elif name == "plane":
        shape([(1, 11), (23, 2), (19, 22), (12, 17), (9, 20), (8, 15)])
        stroke([(8, 15), (18, 7), (11, 17)], edge, 1.4)
    elif name == "code":
        stroke([(8, 6), (2, 12), (8, 18)], color, 2.7)
        stroke([(16, 6), (22, 12), (16, 18)], color, 2.7)
        stroke([(14, 4), (10, 20)], color, 2)

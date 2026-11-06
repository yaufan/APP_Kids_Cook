"""Food: ingredients, things in between, and finished food.

    python3 food.py

Writes app/assets/art/food/<id>.svg and food/anchors.json. Whole things seen from
the side (tomato, egg, strawberry, bottles ...) stand on the bottom edge of their
picture; slices, wrappers and batter are seen from above. Pictures that swap with
each other in a game have the same size and position:
  egg, egg_half_left, egg_half_right       (the two halves fit back into the egg)
  batter_raw, batter_cooked                (same outline)
  wrapper, wrapper_filled
  skewer, fruit_skewer                     (anchors.json: the five places on the stick)
tea.svg is a plain 100 x 200 block of tea with a wavy top (the wave repeats every
100, so blocks can sit side by side), to fill the cup from below.
"""
import json
import math
import random

import clay as kit
import tools
from clay import (ART, CHEESE, CRUMB, CRUST, LEAF, STEM, TOMATO, WHITE, YOLK, at, begin, blob, bubbles, capsule, circle,
                  clay, contact, dk, ellipse, fill, group, lin, line, lt, mark, parse, ring_pts, rpoly, rrect, save, spot,
                  stroke, worm)

ANCH = {}


def done(name, **kw):
    r = save(f"food/{name}.svg", **kw)
    if r["marks"]:
        ANCH[name] = {"viewBox": {"width": r["width"], "height": r["height"]}, **r["marks"]}
    return r


def same_box(draws):
    """One box that holds every drawing in draws (functions), 4 units round."""
    boxes = []
    for fn in draws:
        begin()
        fn()
        boxes.append(list(kit.PG.box))
    x0 = math.floor(min(b[0] for b in boxes) - 4)
    y0 = math.floor(min(b[1] for b in boxes) - 4)
    x1 = math.ceil(max(b[2] for b in boxes) + 4)
    y1 = math.ceil(max(b[3] for b in boxes) + 4)
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------- tomato
TOMATO_BODY = "M 0 -36 C 22 -44 50 -30 50 0 C 50 30 28 46 0 46 C -28 46 -50 30 -50 0 C -50 -30 -22 -44 0 -36 Z"


def calyx(y=-36, s=1.0):
    with at(0, y, s=s):
        for a in (-54, 18, 90, 162, 234):
            x, yy = math.cos(math.radians(a)) * 11, math.sin(math.radians(a)) * 6
            clay(ellipse(x, yy, 12.5, 5.2, a), LEAF, depth=2.2)
        clay(circle(0, 0, 6), LEAF, depth=2)
        clay(rrect(-3.5, -16, 7, 15, 3.5), STEM, depth=1.6)


def tomato():
    with at(0, 0, s=2.6):
        contact(0, 44, 40, 5, .35)
        clay(parse(TOMATO_BODY), TOMATO, dents=[(22, 20, 9, 20)])
        for sx in (-1, 1):
            stroke(parse(f"M {sx * 8} -32 Q {sx * 24} -12 {sx * 20} 14"), dk(TOMATO, .25), 3, .16)
        spot(-26, -14, 11, 6, -40, .55)
        calyx()


def tomato_slice():
    with at(0, 0, s=4.4):
        clay(circle(0, 0, 20), TOMATO, depth=4)
        clay(circle(0, 0, 16.4), "#F7604F", shadow=False, depth=2.5)
        for k in range(5):
            a = math.radians(k * 72 - 90)
            cx, cy = math.cos(a) * 9.2, math.sin(a) * 9.2
            clay(ellipse(cx, cy, 3.8, 5.8, k * 72), "#FFC09F", shadow=False, depth=1.2)
            for j in (-1, 1):
                sx, sy = cx + math.cos(a + 1.57) * j * 1.6, cy + math.sin(a + 1.57) * j * 1.6
                fill(ellipse(sx, sy, .9, 1.4, k * 72), "#F4D35E")
        clay(circle(0, 0, 3.6), "#FF8070", shadow=False, depth=1.2)
        spot(-10, -11, 5, 2.8, -40, .6)


# ---------------------------------------------------------------- bread, cheese, sandwich
TOAST = ("M -22 24 L -22 -6 C -31 -10 -31 -29 -14 -28 C -8 -35 8 -35 14 -28 C 31 -29 31 -10 22 -6 L 22 24 "
         "Q 22 28 18 28 L -18 28 Q -22 28 -22 24 Z")


def bread():
    with at(0, 0, s=3.8):
        clay(parse(TOAST), CRUST, depth=4.5, dents=[(15, 18, 3.5, 0, .5)])
        with at(0, 1.4, s=.8):
            crumb = parse(TOAST)
        clay(crumb, CRUMB, shadow=False, depth=3)
        r = random.Random(4)
        for _ in range(30):
            x, y = r.uniform(-15, 15), r.uniform(-21, 19)
            if y < -12 and abs(x) < 4:
                continue
            fill(ellipse(x, y, r.uniform(.6, 1.3), r.uniform(.4, .9), r.uniform(0, 180)), "#E9C58A", .55)
        spot(-9, -16, 6, 3, -20, .55)


def cheese():
    with at(0, 0, s=4.4):
        clay(rrect(-22, -22, 44, 44, 6, rot=-6), CHEESE, depth=4)
        for x, y, r in ((-8, -6, 5), (9, 8, 6.5), (10, -11, 3.5), (-11, 12, 3), (1, -15, 2.4)):
            clay(circle(x, y, r), dk(CHEESE, .1), inv=True, shadow=False)
        spot(-12, -15, 5, 3, -20, .6)


def sandwich_body():
    """Triangle toast seen from the cut side (local units, about 108 x 100)."""
    clay(rpoly([(-53, 6), (8, -50), (53, 6)], 9), CRUST, depth=5)
    clay(rpoly([(-40, 3), (8, -38), (40, 3)], 6), CRUMB, shadow=False, depth=3)
    spot(-6, -18, 9, 3, -40, .55)
    clay(rrect(-52, 0, 104, 50, 10), CRUST, depth=6)
    clay(rrect(-46, 3, 92, 13, 4), CRUMB, shadow=False, depth=2)
    clay(rrect(-46, 32, 92, 13, 4), CRUMB, shadow=False, depth=2)
    clay(rrect(-50, 15, 100, 6.5, 3), CHEESE, depth=1.5)
    clay(parse("M 42 17 L 56 17 Q 57 33 51 33 Q 47 33 47 24 Z"), CHEESE, depth=1.5)
    for x in (-32, 0, 32):
        clay(ellipse(x, 26.5, 18, 5.6), TOMATO, depth=1.6)
        fill(ellipse(x, 26, 11, 2.4), "#FF9A85", .85)
    r = random.Random(2)
    for _ in range(14):
        x, y = r.uniform(-40, 40), r.choice((r.uniform(5, 13), r.uniform(34, 43)))
        fill(ellipse(x, y, .9, .6), "#E9C58A", .6)


def sandwich():
    with at(0, 0, s=2.8):
        contact(0, 49, 52, 4, .35)
        sandwich_body()


# ---------------------------------------------------------------- fruit
BANANA = "#FFD84D"


def banana():
    with at(0, 0, s=3.2):
        contact(2, 22, 36, 3.5, .3)
        body = parse("M -40 -16 C -30 18 26 26 46 -6 C 48 -11 43 -14 39 -10 C 18 8 -16 6 -31 -20 C -33 -23 -38 -21 -40 -16 Z")
        clay(body, BANANA, depth=4, dents=[(18, 8, 3.5, 20, .5)])
        stroke(parse("M -34 -12 C -22 10 18 16 40 -6"), lt(BANANA, .5), 2.2, .7)
        stroke(parse("M -30 -6 C -16 12 20 14 38 0"), dk(BANANA, .15), 1.4, .35)
        clay(rrect(-46, -25, 9, 10, 3, rot=34), "#8A6B2E", depth=1.4)
        clay(circle(45, -8, 2.8), "#6B4A22", depth=1, shadow=False)


def banana_face(s=1.0):
    """A round banana slice seen from above (r = 18 local)."""
    with at(0, 0, s=s):
        clay(circle(0, 0, 18), "#F6E3A6", depth=3)
        clay(circle(0, 0, 15.5), "#FFF4CC", shadow=False, depth=2.5)
        for k in range(3):
            a = math.radians(k * 120 - 90)
            fill(ellipse(math.cos(a) * 3, math.sin(a) * 3, 1.4, 3.2, k * 120 + 90), "#E9D29A", .9)
            fill(circle(math.cos(a) * 4.6, math.sin(a) * 4.6, .9), "#9C7A44", .7)
        spot(-6, -7, 4, 2.2, -35, .55)


def banana_piece():
    banana_face(4.2)


STRAW_B = "M 0 36 C -14 32 -30 14 -30 -4 C -30 -20 -18 -26 -8 -24 C -4 -23 -2 -22 0 -22 C 2 -22 4 -23 8 -24 C 18 -26 30 -20 30 -4 C 30 14 14 32 0 36 Z"


def strawberry_body(rest=True, detail=True):
    if rest:
        contact(0, 34, 12, 2.4, .35)
    clay(parse(STRAW_B), "#F0433A", depth=5, dents=[(14, 10, 4, 0, .5)] if detail else ())
    seeds = ((-18, -12), (-6, -14), (6, -14), (18, -12), (-22, 0), (-11, -2), (0, -3), (11, -2), (22, 0),
             (-16, 11), (-5, 9), (6, 9), (16, 11), (-9, 20), (2, 20), (11, 19), (-2, 29))
    for x, y in (seeds if detail else seeds[::2]):
        if detail:
            fill(ellipse(x, y + .6, 1.8, 2.4), dk("#F0433A", .2), .45)
        fill(ellipse(x, y, 1.1, 1.7) if detail else ellipse(x, y, 1.5, 2.2), "#FFE38A")
    spot(-15, -8, 6, 3.4, -40, .5)
    if detail:
        for a in (-160, -120, -60, -20, -90):
            with at(0, -22, a):
                clay(parse("M 0 -3.5 C 6 -4 14 -2 17 0 C 14 2 6 4 0 3.5 Z"), LEAF, depth=1.6)
    else:   # the leaves as one piece (smaller file for small pictures)
        pts = []
        for a in (-160, -125, -90, -55, -20):
            r = math.radians(a)
            pts += [(math.cos(r - .28) * 5, -22 + math.sin(r - .28) * 5), (math.cos(r) * 17, -22 + math.sin(r) * 17)]
        pts += [(6, -18), (-6, -18)]
        clay(rpoly(pts, 2.5), LEAF, depth=1.6)
    clay(capsule(0, -24, 1.5, -33, 2.4), STEM, depth=1)


def strawberry():
    with at(0, 0, s=3.0):
        strawberry_body()


GRAPE = "#A6D86A"


def grape_body(rest=True):
    if rest:
        contact(0, 16, 9, 2, .3)
    clay(ellipse(0, 0, 12.5, 16.5), GRAPE, depth=3.2)
    spot(2, 4, 7, 9, 0, .35, "#E4F7B8")
    spot(-5, -7, 3.2, 5, -20, .7)
    clay(circle(0, -16, 2.6), "#9BBF5A", depth=.8, shadow=False)
    clay(capsule(0, -17, .4, -19.6, 1.2), "#8A6B3A", depth=.6)


def grape():
    with at(0, 0, s=3.5):
        grape_body()


# ---------------------------------------------------------------- skewer
STICK = "#E2C08D"
SLOTS = [-168, -84, 0, 84, 168]        # local y of the five fruits, top to bottom
SK_S = 1.0


def stick():
    clay(rpoly([(-5.5, -244), (0, -260), (5.5, -244), (5.5, 252), (-5.5, 252)], 4), STICK, depth=2)
    for y in (-226, 230):
        stroke(parse(f"M -3 {y} L 3 {y + 3}"), dk(STICK, .25), 1.2, .4)


def fruit_on_stick(i, detail=True):
    y = SLOTS[i]
    kind = ["strawberry", "banana", "grape", "strawberry", "banana"][i]
    if kind == "strawberry":
        with at(0, y - 8, s=1.3):
            strawberry_body(rest=False, detail=detail)
    elif kind == "banana":
        with at(0, y):
            banana_face(2.05)
    else:
        with at(0, y, s=2.3):
            grape_body(rest=False)


def skewer_marks():
    for i, y in enumerate(SLOTS):
        mark(f"slot{i + 1}", 0, y, 38)


def skewer():
    stick()
    skewer_marks()


def fruit_skewer(detail=True):
    stick()
    for i in range(5):
        fruit_on_stick(i, detail)


# ---------------------------------------------------------------- eggs
EGG = "#F6E3C8"
EGG_D = ((0, -42), (22, -42), (32, -6), (32, 12), (32, 32), (18, 44), (0, 44), (-18, 44), (-32, 32), (-32, 12), (-32, -6), (-22, -42), (0, -42))
EGG_PATH = "M 0 -42 C 22 -42 32 -6 32 12 C 32 32 18 44 0 44 C -18 44 -32 32 -32 12 C -32 -6 -22 -42 0 -42 Z"
CRACK = [(0, -42), (-5, -32), (5, -22), (-6, -10), (4, 2), (-5, 14), (5, 26), (-3, 36), (0, 44)]


def _cubic(p0, p1, p2, p3, n=10):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def egg_outline():
    pts = [EGG_D[0]]
    for i in range(0, 12, 3):
        pts += _cubic(EGG_D[i], EGG_D[i + 1], EGG_D[i + 2], EGG_D[i + 3])
    return pts      # clockwise from the top: right side first, then the left side


def egg_specks():
    r = random.Random(11)
    for _ in range(16):
        a, d = r.uniform(0, 6.28), r.uniform(0, 1)
        x, y = math.cos(a) * 24 * d, 6 + math.sin(a) * 30 * d
        fill(circle(x, y, r.uniform(.6, 1.1)), "#C9A27A", .35)


def egg():
    with at(0, 0, s=3.0):
        contact(0, 42.5, 22, 3, .35)
        clay(parse(EGG_PATH), EGG, depth=6, dents=[(14, 22, 5, 20, .5)])
        egg_specks()


def egg_half(side):
    out = egg_outline()
    right = out[:len(out) // 2 + 1]                   # top .. bottom down the right side
    left = out[len(out) // 2:] + [out[0]]             # bottom .. top up the left side
    crack_down = CRACK
    crack_up = CRACK[::-1]
    if side == "left":
        poly = left[:-1] + crack_down[:-1]
    else:
        poly = right[:-1] + crack_up[:-1]
    with at(0, 0, s=3.0):
        contact(-14 if side == "left" else 14, 42.5, 12, 2.6, .35)
        shell = rpoly(poly, 1.2)
        clay(shell, EGG, depth=6)
        with group(clip=shell):
            egg_specks()
            sx = 1 if side == "left" else -1
            inner = line(*[(x + sx * 1.2, y) for x, y in CRACK])
            stroke(inner, "#FFFFFF", 5, .95)
            stroke(line(*[(x + sx * 3.2, y) for x, y in CRACK]), "#E9D6BA", 2.5, .6)


def egg_box():
    return same_box([egg, lambda: egg_half("left"), lambda: egg_half("right")])


# ---------------------------------------------------------------- batter, crepe, 蛋餅
def batter_outline():
    return blob(ring_pts(0, 0, 150, 147, 30, wob=.018, seed=5))


def batter_raw():
    b = batter_outline()
    clay(b, "#FFE48A", depth=10, shadow=False, shine=False)
    for x, y, rx, ry, a in ((-54, -62, 40, 12, -30), (40, 30, 30, 8, -20), (-20, 70, 22, 6, -10)):
        spot(x, y, rx, ry, a, .55)
    for x, y, r in ((30, -40, 4), (-60, 20, 3), (70, -10, 3.5), (10, 60, 2.6), (-30, -10, 2.4)):
        fill(circle(x, y, r), "#FFF6D0", .9)
    mark("center", 0, 0)


def batter_cooked():
    b = batter_outline()
    clay(b, "#F2C04B", depth=10, shadow=False, shine=.25)
    r = random.Random(6)
    with group(clip=b):
        stroke(b, "#C9852B", 16, .25)
        for _ in range(16):
            a, d = r.uniform(0, 6.28), r.uniform(10, 120)
            spot(math.cos(a) * d, math.sin(a) * d, r.uniform(10, 22), r.uniform(7, 14), r.uniform(0, 180), .35, "#C9852B")
        for _ in range(8):
            a, d = r.uniform(0, 6.28), r.uniform(0, 90)
            spot(math.cos(a) * d, math.sin(a) * d, r.uniform(14, 26), r.uniform(8, 14), r.uniform(0, 180), .45, "#FFE27A")
    mark("center", 0, 0)


def toasty(b, n, seed, rmax=130, color="#D9A35E", op=.4):
    r = random.Random(seed)
    with group(clip=b):
        for _ in range(n):
            a, d = r.uniform(0, 6.28), r.uniform(0, rmax)
            spot(math.cos(a) * d, math.sin(a) * d, r.uniform(6, 16), r.uniform(4, 10), r.uniform(0, 180), op, color)


def crepe():
    b = blob(ring_pts(0, 0, 150, 148, 30, wob=.02, seed=9))
    clay(b, "#F8E6BE", depth=10)
    toasty(b, 22, 3)
    mark("center", 0, 0)


SKIN = "#F3D79C"
EGGL = "#FFD24A"
GREEN = "#4FA83A"


def spiral_face(rx, ry, seed=1, turns=2.1):
    """The cut end of a rolled 蛋餅: crepe, egg and scallion rolled into a spiral."""
    clay(ellipse(0, 0, rx, ry), SKIN, depth=min(rx, ry) * .18)
    pts = []
    n = 40
    for i in range(n + 1):
        t = i / n
        a = t * turns * 2 * math.pi + seed
        k = .16 + .66 * t
        pts.append((math.cos(a) * rx * k, math.sin(a) * ry * k))
    p = blob(pts, closed=False)
    stroke(p, EGGL, min(rx, ry) * .2)
    stroke(p, lt(EGGL, .4), min(rx, ry) * .07, .7, dx=-1, dy=-1.5)
    r = random.Random(seed)
    for i in range(6, n, 7):
        x, y = pts[i]
        fill(rrect(x - rx * .05, y - ry * .03, rx * .1, ry * .06, 2, r.uniform(0, 180)), GREEN, .9)
    spot(-rx * .4, -ry * .45, rx * .2, ry * .1, -30, .4)


def danbing_roll():
    body = capsule(-140, 0, 120, 0, 52)
    clay(body, SKIN, depth=14, dents=[(-60, 24, 9, 20, .5)])
    toasty(body, 18, 5, 200, "#D9A35E", .35)
    stroke(parse("M -176 26 C -100 40 40 40 120 26"), dk(SKIN, .18), 5, .45)
    stroke(parse("M -176 30 C -100 44 40 44 120 30"), "#FFFFFF", 3, .35)
    with at(150, 0):
        spiral_face(30, 52, seed=2)
    for x, y in ((-120, -20), (-40, -30), (40, -26), (-90, 10), (10, 6), (80, -6)):
        fill(rrect(x - 5, y - 3, 10, 6, 2, (x * 7) % 180), GREEN, .85)


def danbing_pieces():
    for i, (x, y) in enumerate(((-171, 6), (-57, -6), (57, 6), (171, -6))):
        with at(x, y):
            clay(rrect(-50, -26, 100, 66, 30), dk(SKIN, .06), depth=12)
            with at(0, -8):
                spiral_face(50, 40, seed=i + 1)


# ---------------------------------------------------------------- bottles, scallion
SOY = "#5A3320"


def soy_paste():
    contact(0, 150, 66, 8, .35)
    clay(parse("M -54 -40 C -54 -70 -24 -84 -20 -100 L 20 -100 C 24 -84 54 -70 54 -40 L 54 120 C 54 140 40 150 20 150 "
               "L -20 150 C -40 150 -54 140 -54 120 Z"), SOY, depth=14, dents=[(30, 110, 8, 0, .4)])
    clay(rrect(-24, -118, 48, 26, 8), dk(SOY, .1), depth=4)
    clay(rrect(-28, -160, 56, 46, 14), "#E8573F", depth=8)
    for x in (-14, 0, 14):
        stroke(parse(f"M {x} -152 L {x} -122"), dk("#E8573F", .25), 3, .4)
    clay(rrect(-44, -10, 88, 86, 16), "#FFD166", depth=8)
    clay(parse("M 0 4 C 8 18 18 28 18 40 C 18 52 9 60 0 60 C -9 60 -18 52 -18 40 C -18 28 -8 18 0 4 Z"), SOY, depth=4)
    stroke(parse("M -44 66 L 44 66"), "#E8573F", 6, .8)
    stroke(parse("M -38 -36 C -40 20 -40 80 -36 128"), "#FFFFFF", 7, .35)
    stroke(parse("M -26 -46 L -26 -30"), "#FFFFFF", 5, .3)


def scallion():
    r = random.Random(7)
    pts = [(-30, -14), (0, -22), (28, -12), (-16, 10), (16, 12), (44, 14), (-44, 12), (2, 32)]
    for i, (x, y) in enumerate(pts):
        rr = r.uniform(10, 13)
        c = GREEN if i % 3 else "#7CC75A"
        with at(x, y, r.uniform(0, 60)):
            clay(ellipse(0, 0, rr, rr * .86), c, depth=3)
            clay(ellipse(0, 0, rr * .55, rr * .45), "#D7F0B8", inv=True, shadow=False, depth=1.5)


# ---------------------------------------------------------------- drinks
TEA = "#8E4B1C"


def tea():
    wave = "M 0 14 C 12.5 9 37.5 9 50 14 C 62.5 19 87.5 19 100 14"
    fill(parse(wave + " L 100 200 L 0 200 Z"), TEA)
    stroke(parse(wave), "#B8722F", 5, .8)
    stroke(parse(wave), "#E3A86A", 1.6, .8, dx=0, dy=-1)


def milk():
    contact(0, 160, 74, 8, .3)
    clay(rpoly([(-62, -62), (0, -104), (62, -62)], 10), "#7DB7F0", depth=8)
    clay(rrect(-12, -122, 24, 30, 6), "#F4F8FC", depth=4)
    clay(rrect(-66, -68, 132, 228, 18), "#FDFCF8", depth=16)
    band = parse("M -66 50 C -40 38 -20 62 0 50 C 20 38 40 62 66 50 L 66 142 C 66 152 58 160 48 160 L -48 160 C -58 160 -66 152 -66 142 Z")
    clay(band, "#5B9BE0", depth=10, shadow=False, shine=False)
    clay(parse("M 0 74 C 8 88 18 98 18 110 C 18 122 9 130 0 130 C -9 130 -18 122 -18 110 C -18 98 -8 88 0 74 Z"), "#FFFFFF", depth=4)
    for x, y in ((-34, -30), (30, -10), (-20, 14)):
        clay(circle(x, y, 9), "#BFE0F5", depth=2, shadow=False)


PEARL = "#3A2418"


def pearl_ball(x, y, r):
    clay(circle(x, y, r), PEARL, depth=r * .3, shine=.7)
    fill(circle(x - r * .35, y - r * .38, r * .2), "#FFFFFF", .75)


def pearls():
    contact(0, 62, 86, 9, .35)
    rows = [(4, 0, -28), (3, 13, -10), (4, 26, 6), (5, 40, 22), (6, 54, 38)]
    r = random.Random(3)
    for n, y, half in rows:
        for i in range(n):
            x = (i - (n - 1) / 2) * 27 + r.uniform(-2, 2)
            pearl_ball(x, y - 10 + r.uniform(-2, 2), 14)


def pearl():
    contact(0, 40, 26, 4, .35)
    pearl_ball(0, 0, 40)


def ice():
    c = "#BFE6FA"
    contact(4, 60, 62, 6, .2)
    shape = rpoly([(-50, -14), (-26, -40), (58, -40), (58, 36), (34, 62), (-50, 62)], 14)
    clay(shape, c, depth=12, opacity=.92, sh_op=.6)
    with group(clip=shape):
        fill(parse("M -60 -14 L 34 -14 L 70 -50 L -30 -50 Z"), lt(c, .5), .8)
        fill(parse("M 34 -14 L 70 -50 L 70 70 L 34 70 Z"), dk(c, .12), .55)
        stroke(parse("M -50 -14 L 34 -14 L 58 -40 M 34 -14 L 34 62"), "#FFFFFF", 3, .7)
    stroke(parse("M -38 2 L -38 44"), "#FFFFFF", 8, .75)
    stroke(parse("M -24 -27 L 30 -27"), "#FFFFFF", 5, .7)
    for x, y, r in ((12, 30, 4), (22, 14, 2.6), (2, 46, 2.2)):
        fill(circle(x, y, r), "#FFFFFF", .7)


MILK_TEA = "#CFA072"


def drink_in_cup(color, n_pearls=12):
    inner = tools.cup_shape(6)
    with group(clip=inner):
        top = 54
        fill(parse(f"M -90 {top} C -40 {top - 6} 40 {top + 6} 90 {top} L 90 240 L -90 240 Z"), lin([(0, lt(color, .1)), (1, dk(color, .1))]))
        stroke(parse(f"M -90 {top} C -40 {top - 6} 40 {top + 6} 90 {top}"), lt(color, .45), 4, .8)
        r = random.Random(2)
        k = 0
        for row, y in enumerate((tools.CUP_H - 18, tools.CUP_H - 38, tools.CUP_H - 56)):
            cnt = 6 - row
            for i in range(cnt):
                x = (i - (cnt - 1) / 2) * 21 + r.uniform(-3, 3)
                if k < n_pearls:
                    pearl_ball(x, y + r.uniform(-3, 3), 10.5)
                    k += 1


def milk_tea():
    tools.cup_back()
    drink_in_cup(MILK_TEA)
    with at(14, 0, 8):
        tools.straw(-150, 186)
    tools.cup_front()
    with at(0, -2):
        tools.lid()
    kit.PG.marks = {}


# ---------------------------------------------------------------- dumplings
DOUGH = "#F7EAD2"


def wrapper_outline():
    return blob(ring_pts(0, 0, 120, 118, 30, wob=.012, seed=7))


def wrapper():
    b = wrapper_outline()
    clay(b, DOUGH, depth=10)
    with group(clip=b):
        stroke(b, "#FFFFFF", 14, .35)
    r = random.Random(8)
    for _ in range(9):
        a, d = r.uniform(0, 6.28), r.uniform(20, 95)
        spot(math.cos(a) * d, math.sin(a) * d, r.uniform(8, 16), r.uniform(5, 9), r.uniform(0, 180), .5)
    mark("center", 0, 0)


MEAT = "#D98E73"


def filling(s=1.0):
    with at(0, 0, s=s):
        clay(blob(ring_pts(0, 0, 50, 42, 14, wob=.06, seed=4)), MEAT, depth=12)
        r = random.Random(5)
        for x, y, rr in ((-20, -10, 15), (8, -16, 14), (24, 4, 13), (-6, 10, 15), (-26, 14, 10), (16, 22, 10)):
            clay(circle(x, y, rr), lt(MEAT, r.uniform(0, .12)), depth=4, sh_op=.6)
        for x, y, a in ((-12, -20, 20), (18, -4, -30), (-24, 4, 60), (4, 20, 10), (28, 16, 80), (-4, -2, -40)):
            clay(rrect(x - 6, y - 3.5, 12, 7, 3, a), "#8CCB5E", depth=1.5, sh_op=.5)
        for x, y in ((10, 8), (-16, -2), (22, -14)):
            fill(ellipse(x, y, 3, 2), "#F3E9C9", .9)


def wrapper_filled():
    wrapper()
    filling(1.0)


def dumpling_shape():
    """A half moon with a wavy, pinched top edge."""
    n = 10
    pts = [(-102, 16)]
    for i in range(1, 2 * n):
        t = i / (2 * n)
        a = math.radians(180 + 180 * t)
        r = 90 if i % 2 else 82
        pts.append((math.cos(a) * r * 1.13, 6 + math.sin(a) * r))
    pts.append((102, 16))
    p = kit.Path().M(*pts[0])
    full = pts
    for i in range(len(full) - 1):
        p0 = full[max(i - 1, 0)]
        p1, p2 = full[i], full[i + 1]
        p3 = full[min(i + 2, len(full) - 1)]
        p.C(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, *p2)
    p.C(70, 30, -70, 30, -102, 16).Z()
    return p, pts


def dumpling_body(sh_op=1.0):
    shape, pts = dumpling_shape()
    clay(shape, DOUGH, depth=16, dents=[(46, 2, 8, 20, .45)], sh_op=sh_op)
    spot(0, 0, 50, 16, 0, .3, "#E7A58D")
    for i in range(2, len(pts) - 2, 2):     # a crease in from each dip of the pinched edge
        x, y = pts[i]
        a = math.atan2(y - 10, x / 1.13)
        x2, y2 = x - math.cos(a) * 30 * 1.13, y - math.sin(a) * 30
        p = parse(f"M {x:.1f} {y:.1f} Q {(x + x2) / 2 + 6:.1f} {(y + y2) / 2 + 3:.1f} {x2:.1f} {y2:.1f}")
        stroke(p, dk(DOUGH, .22), 3.4, .45)
        stroke(p, "#FFFFFF", 2.4, .6, dx=-1.6, dy=-1.6)
    worm(parse("M -84 -6 C -66 -56 66 -56 84 -6"), lt(DOUGH, .2), 7, shadow=False)
    spot(-36, -40, 20, 7, -25, .45)


def dumpling():
    dumpling_body()


def dumplings_plate():
    tools.plate(214)
    for i in range(5):           # five round the plate, one in the middle
        a = 360 * i / 5 - 90
        with at(math.cos(math.radians(a)) * 124, math.sin(math.radians(a)) * 124 + 4, a + 90, s=.64):
            dumpling_body(.6)
    with at(0, 8, s=.64):
        dumpling_body(.6)
    kit.PG.marks = {}


# ---------------------------------------------------------------- write
def main():
    simple = [("tomato", tomato, True), ("tomato_slice", tomato_slice, False), ("bread", bread, False),
              ("cheese", cheese, False), ("sandwich", sandwich, True), ("banana", banana, True),
              ("banana_piece", banana_piece, False), ("strawberry", strawberry, True), ("grape", grape, True),
              ("crepe", crepe, False), ("danbing_roll", danbing_roll, False), ("danbing_pieces", danbing_pieces, False),
              ("soy_paste", soy_paste, True), ("scallion", scallion, False), ("milk", milk, True),
              ("pearls", pearls, True), ("pearl", pearl, True), ("ice", ice, True), ("milk_tea", milk_tea, True),
              ("filling", filling, False), ("dumpling", dumpling, False), ("dumplings_plate", dumplings_plate, False)]
    for name, fn, rest in simple:
        begin()
        fn()
        done(name, rest=rest)
    # pictures that swap with each other: one box each pair
    box = egg_box()
    x0, y0, w, h = box
    eb = (x0, y0, w, h - 4)          # they stand: no margin under the shadow
    for name, fn in (("egg", egg), ("egg_half_left", lambda: egg_half("left")), ("egg_half_right", lambda: egg_half("right"))):
        begin()
        fn()
        done(name, box=eb)
    box = same_box([batter_raw, batter_cooked])
    for name, fn in (("batter_raw", batter_raw), ("batter_cooked", batter_cooked)):
        begin()
        fn()
        done(name, box=box)
    box = same_box([wrapper, wrapper_filled])
    for name, fn in (("wrapper", wrapper), ("wrapper_filled", wrapper_filled)):
        begin()
        fn()
        done(name, box=box)
    box = same_box([fruit_skewer, skewer])
    for name, fn in (("skewer", skewer), ("fruit_skewer", fruit_skewer)):
        begin()
        fn()
        done(name, box=box)
    begin()
    tea()
    done("tea", box=(0, 0, 100, 200))
    (ART / "food" / "anchors.json").write_text(json.dumps(ANCH, indent=2, ensure_ascii=False) + "\n")
    print("food:", len(list((ART / "food").glob("*.svg"))))


if __name__ == "__main__":
    main()

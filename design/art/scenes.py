"""Backgrounds, 1080 x 1920, opaque.

    python3 scenes.py

scenes/restaurant.svg  warm wall, bunting, two lamps, shelves, a counter in the bottom third
scenes/kitchen.svg     tiled wall with a window, a wooden worktop filling the lower 60%
scenes/market.svg      a traditional market vegetable stall (for later)
scenes/scenes.json     the lines the app lines things up with (y in the 1920 height)

The middle stays plain where the app puts things: in the restaurant the customer
stands behind the counter (their picture's bottom on counterBack) with the order
bubble above; the middle of the counter top and of the worktop are empty.
The top 200 is calm for the app's buttons.
"""
import json
import math
import random

import clay as kit
import food
import tools
from clay import (ART, GOLD, LEAF, STEM, TOMATO, WHITE, at, begin, blob, capsule, circle, clay, contact, dk, ellipse,
                  fill, group, lin, lt, mark, parse, rad, ring_pts, rpoly, rrect, save, spot, stroke, worm)

W, H = 1080, 1920
INFO = {}


def rect(x, y, w, h):
    return kit.Path().M(x, y).L(x + w, y).L(x + w, y + h).L(x, y + h).Z()


# ---------------------------------------------------------------- shared props
def jar(x, y, color, lid, s=1.0):
    with at(x, y, s=s):
        contact(0, 40, 46, 7, .3)
        clay(rrect(-40, -46, 80, 86, 24), "#EAF6FB", depth=10)
        clay(rrect(-30, -14, 60, 46, 16), color, depth=8, shadow=False)
        clay(rrect(-42, -66, 84, 26, 12), lid, depth=7)
        stroke(kit.parse("M -26 -30 L -26 20"), "#FFFFFF", 7, .6)


def plant(x, y, s=1.0):
    with at(x, y, s=s):
        contact(0, 44, 46, 7, .3)
        for a in (-42, -16, 16, 42, 0):
            with at(0, -18, a):
                clay(ellipse(0, -44, 17, 44), LEAF if a else lt(LEAF, .15), depth=7)
        clay(parse("M -46 -20 L 46 -20 L 36 34 Q 34 44 24 44 L -24 44 Q -34 44 -36 34 Z"), "#E07B52", depth=10)
        clay(rrect(-52, -30, 104, 22, 11), "#EB8F66", depth=6)


def lamp(x, y_top, y):
    stroke(parse(f"M {x} {y_top} L {x} {y - 40}"), "#8A6B52", 5)
    spot(x, y + 60, 190, 150, 0, .35, "#FFF3C4", hard=.2)
    clay(parse(f"M {x - 70} {y + 26} C {x - 64} {y - 40} {x + 64} {y - 40} {x + 70} {y + 26} Z"), "#FFB36B", depth=14)
    clay(ellipse(x, y + 28, 30, 12), "#FFF3B0", depth=5, shadow=False, shine=False)
    clay(circle(x, y - 42, 10), "#C99A6B", depth=4)


def bunting(y, colors, x0=-20, x1=W + 20, sag=70, n=11, size=46):
    p = parse(f"M {x0} {y} Q {(x0 + x1) / 2} {y + sag * 2} {x1} {y}")
    stroke(p, "#C99A6B", 5)
    for i in range(n):
        t = (i + .5) / n
        x = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * (x0 + x1) / 2 + t * t * x1
        yy = (1 - t) ** 2 * y + 2 * t * (1 - t) * (y + sag * 2) + t * t * y
        c = colors[i % len(colors)]
        clay(rpoly([(x - size / 2, yy), (x + size / 2, yy), (x, yy + size * 1.05)], 9), c, depth=6)


def wood_grain(x, y, w, h, n, seed, color, op=.22):
    r = random.Random(seed)
    for i in range(n):
        yy = y + h * (i + .5) / n + r.uniform(-h / n * .3, h / n * .3)
        a = x + r.uniform(0, w * .4)
        b = min(x + w, a + r.uniform(w * .2, w * .55))
        k = r.uniform(4, 10) * r.choice((-1, 1))
        pth = parse(f"M {a:.0f} {yy:.0f} C {a + (b - a) * .3:.0f} {yy + k:.0f} {a + (b - a) * .6:.0f} {yy - k:.0f} {b:.0f} {yy:.0f}")
        stroke(pth, dk(color, .3), 4, op)
        stroke(pth, "#FFFFFF", 2.5, op, dx=0, dy=3)


# ---------------------------------------------------------------- restaurant
COUNTER_BACK = 1280


def restaurant():
    fill(rect(0, 0, W, H), lin([(0, "#FFE8D0"), (1, "#FFD3AE")]))
    for x in range(30, W, 130):
        fill(rect(x, 0, 62, 1100), "#FFF3E6", .4)
    # wainscot under the shelves
    fill(rect(0, 1080, W, 220), "#F6C49A")
    for x in range(20, W, 120):
        clay(rrect(x, 1104, 96, 170, 20), "#F6C49A", inv=True, shadow=False, depth=10)
    clay(rrect(-20, 1062, W + 40, 30, 15), "#E9A877", depth=8)
    # lamps and bunting
    lamp(150, 0, 330)
    lamp(930, 0, 330)
    bunting(196, ["#FF8A80", "#FFD166", "#7FD1AE", "#7EC8F0", "#C7A3FF"], sag=60)
    # shelves at the sides
    for x0, x1 in ((-30, 270), (810, W + 30)):
        clay(rrect(x0, 960, x1 - x0, 30, 15), "#C98E55", depth=9)
        for bx in (x0 + 60, x1 - 60):
            if 0 < bx < W:
                clay(parse(f"M {bx - 10} 990 L {bx + 10} 990 L {bx + 10} 1010 Q {bx} 1030 {bx - 10} 1010 Z"), dk("#C98E55", .1), depth=4)
    jar(70, 914, "#FF8A65", "#E8573F", .9)
    jar(180, 920, "#FFD166", "#5DBB63", .8)
    plant(890, 916, .95)
    jar(1000, 922, "#B9E3A0", "#7EC8F0", .75)
    # upper shelves: plates on the left, a teapot on the right
    for x0, x1 in ((-30, 250), (830, W + 30)):
        clay(rrect(x0, 640, x1 - x0, 28, 14), "#C98E55", depth=8)
    for i in range(3):
        with at(60 + i * 62, 584):
            clay(ellipse(0, 0, 26, 52), WHITE, depth=8)
            clay(ellipse(0, 0, 16, 36), "#F2ECE3", inv=True, shadow=False)
    with at(950, 572, s=.42):
        tools.teapot()
    # the counter
    fill(rect(0, COUNTER_BACK - 10, W, H - COUNTER_BACK + 10), "#B97A45")
    clay(rrect(-30, COUNTER_BACK, W + 60, 100, 26), "#E2AE72", depth=16, shine=.25)
    wood_grain(20, COUNTER_BACK + 14, W - 40, 60, 3, 3, "#E2AE72", .25)
    clay(rrect(-30, COUNTER_BACK + 84, W + 60, 36, 18), "#D39A5E", depth=10, shadow=False)
    for x in range(30, W, 176):
        clay(rrect(x, 1460, 140, 400, 34), "#B97A45", inv=True, shadow=False, depth=16)
    fill(rect(0, COUNTER_BACK + 116, W, 30), "#4A2A14", .12)
    # small things at the ends of the counter
    with at(980, COUNTER_BACK + 40):
        contact(0, 20, 64, 10, .3)
        clay(ellipse(0, 14, 60, 14), "#9BA3AD", depth=6)
        clay(parse("M -46 12 C -46 -30 46 -30 46 12 Z"), GOLD, depth=12)
        clay(circle(0, -26, 9), GOLD, depth=4)
    with at(96, COUNTER_BACK + 42):
        contact(0, 22, 62, 10, .3)
        clay(rrect(-50, -36, 100, 58, 14), "#7FC8E8", depth=10)
        for k in range(4):
            clay(rrect(-40 + k * 20, -64, 18, 40, 6), WHITE, depth=4, shadow=False)
    INFO["restaurant"] = {"counterBack": COUNTER_BACK, "counterTop": COUNTER_BACK + 50, "counterFront": COUNTER_BACK + 120}


# ---------------------------------------------------------------- kitchen
WORK_BACK = 768
WORK_WOOD = "#E3B27A"


def kitchen():
    fill(rect(0, 0, W, WORK_BACK + 20), "#E9D6BC")
    tile = lin([(0, "#FFFBF2"), (1, "#F6E9D6")], 0, 0, 1, 1, key="tile")
    for row in range(7):
        for col in range(10):
            x, y = -40 + col * 120 + (60 if row % 2 else 0), -30 + row * 116
            fill(rrect(x + 4, y + 4, 112, 108, 16), tile)
    # a window with a little view
    with at(540, 420):
        clay(rrect(-210, -190, 420, 330, 40), "#FFFFFF", depth=18)
        glass = rrect(-180, -160, 360, 270, 26)
        fill(glass, lin([(0, "#BFE6FF"), (1, "#E8F7FF")]))
        with group(clip=glass):
            clay(ellipse(-120, 120, 170, 70), "#9ED67A", depth=14, shadow=False, shine=.3)
            clay(ellipse(110, 130, 200, 80), "#8CCB6A", depth=14, shadow=False, shine=.3)
            clay(circle(110, -90, 34), "#FFE27A", depth=8, shadow=False)
            for cx, cy in ((-110, -90), (-60, -100)):
                clay(ellipse(cx, cy, 40, 18), WHITE, depth=6, shadow=False)
            fill(rect(-8, -160, 16, 270), "#FFFFFF")
            fill(rect(-180, -30, 360, 16), "#FFFFFF")
        clay(rrect(-232, 122, 464, 30, 15), "#FFFFFF", depth=8)
        for sx in (-1, 1):
            clay(parse(f"M {sx * 200} -200 C {sx * 150} -120 {sx * 196} 20 {sx * 160} 120 L {sx * 240} 120 L {sx * 240} -200 Z"),
                 "#FF9C8A", depth=12)
        clay(rrect(-250, -214, 500, 26, 13), "#C98E55", depth=7)
    # a shelf with jars on the left, a utensil rail on the right
    clay(rrect(-30, 600, 250, 26, 13), "#C98E55", depth=8)
    jar(60, 556, "#FFB36B", "#E8573F", .8)
    jar(160, 562, "#9ED67A", "#4FA3E0", .7)
    clay(capsule(840, 300, 1060, 300, 9), "#AEB6C0", depth=4)
    for x, tool in ((880, "ladle"), (960, "spoon"), (1030, "whisk")):
        with at(x, 300):
            clay(circle(0, 0, 8), "#8A9099", depth=3)
        with at(x, 420 if tool != "whisk" else 400, s=.62):
            {"ladle": tools.ladle, "spoon": tools.spoon, "whisk": tools.whisk}[tool]()
    # the worktop
    fill(rect(0, WORK_BACK, W, H - WORK_BACK), WORK_WOOD)
    ys = [WORK_BACK + 40]
    h = 150
    while ys[-1] < H:
        ys.append(ys[-1] + h)
        h += 14
    for i, y in enumerate(ys[:-1]):
        y1 = ys[i + 1]
        c = mix_wood(i)
        fill(rect(0, y, W, y1 - y), lin([(0, lt(c, .06)), (1, dk(c, .03))]))
        stroke(parse(f"M 0 {y} L {W} {y}"), dk(c, .3), 4, .35)
        stroke(parse(f"M 0 {y + 3} L {W} {y + 3}"), "#FFFFFF", 2.5, .35)
        wood_grain(30, y + 20, W - 60, y1 - y - 40, 2, 10 + i, c, .18)
    # the back edge where the worktop meets the wall
    clay(rrect(-30, WORK_BACK - 6, W + 60, 52, 20), lt(WORK_WOOD, .1), depth=12, shine=.2)
    fill(rect(0, WORK_BACK + 46, W, 36), lin([(0, "#4A2A14", .16), (1, "#4A2A14", 0)]))
    # small things in the back corners
    with at(80, WORK_BACK + 40, s=.8):
        plant(0, 0)
    with at(960, WORK_BACK + 52):
        for dx, c in ((-30, "#FFFFFF"), (30, "#5A4A44")):
            with at(dx, 0):
                contact(0, 30, 30, 6, .3)
                clay(rrect(-22, -40, 44, 70, 18), c, depth=8)
                clay(rrect(-18, -58, 36, 24, 10), "#AEB6C0", depth=5)
    INFO["kitchen"] = {"worktopBack": WORK_BACK + 46, "worktopMiddle": 1340}


def mix_wood(i):
    return [WORK_WOOD, "#DFAC72", "#E6B680"][i % 3]


# ---------------------------------------------------------------- market
def cabbage(x, y, s=1.0):
    with at(x, y, s=s):
        clay(circle(0, 0, 30), "#8CCB5E", depth=7)
        clay(parse("M -26 8 C -30 -22 -4 -30 6 -24 C -10 -14 -14 4 -6 26 C -16 24 -24 18 -26 8 Z"), "#A9DC78", depth=3, shadow=False)
        clay(parse("M 26 6 C 30 -20 10 -30 -2 -26 C 14 -14 16 6 6 26 C 16 24 24 16 26 6 Z"), "#A9DC78", depth=3, shadow=False)
        clay(circle(0, -2, 13), "#D4F0A6", depth=3, shadow=False)


def small_tomato(x, y, s=1.0):
    """A light tomato for piles (fewer pieces than food.tomato)."""
    with at(x, y, s=s):
        clay(parse(food.TOMATO_BODY), TOMATO, depth=9)
        pts = []
        for i in range(10):
            a = math.radians(-90 + i * 36)
            r = 17 if i % 2 == 0 else 6
            pts.append((math.cos(a) * r, -36 + math.sin(a) * r * .55))
        clay(rpoly(pts, 3), LEAF, depth=2.5, shadow=False)
        clay(rrect(-3.5, -50, 7, 14, 3.5), STEM, depth=1.5, shadow=False)


def carrot(x, y, rot=0, s=1.0):
    with at(x, y, rot, s):
        pts = [(-14, -30), (-6, -46), (-2, -32), (4, -48), (8, -32), (16, -44), (12, -26)]
        clay(rpoly(pts, 3), LEAF, depth=2, shadow=False)
        clay(parse("M -12 -26 C -15 -6 -6 18 0 32 C 6 18 15 -6 12 -26 Q 0 -32 -12 -26 Z"), "#FF8C2B", depth=4)
        stroke(parse("M -9 -10 L -3 -9 M 4 2 L 10 1 M -5 14 L 0 15"), dk("#FF8C2B", .25), 1.8, .5)


def egg_small(x, y, s):
    with at(x, y, s=s):
        clay(parse(food.EGG_PATH), food.EGG, depth=6, sh_op=.7)


def crate(x, y, w, h):
    clay(rrect(x, y, w, h, 18), "#C98E55", depth=14)
    for i in (1, 2):
        yy = y + h * i / 3
        fill(rrect(x + 14, yy - 4, w - 28, 8, 4), dk("#C98E55", .3), .35)
        fill(rrect(x + 14, yy + 3, w - 28, 4, 2), "#FFFFFF", .25)


def tag(x, y):
    with at(x, y):
        clay(rrect(-56, -36, 112, 72, 14), "#FFF8E6", depth=6)
        fill(circle(0, -24, 5), dk("#FFF8E6", .35))


def market():
    fill(rect(0, 0, W, H), lin([(0, "#FFF2DD"), (1, "#FBE0BF")]))
    for x, c in ((-60, "#F6D7C5"), (840, "#D9E8D2")):
        fill(rrect(x, 330, 300, 420, 30), c, .8)
        fill(rrect(x, 300, 300, 60, 20), dk(c, .08), .8)
    # string lights
    stroke(parse(f"M -20 120 Q {W / 2} 230 {W + 20} 120"), "#8A6B52", 4)
    for i in range(9):
        t = (i + .5) / 9
        x = (1 - t) ** 2 * -20 + 2 * t * (1 - t) * W / 2 + t * t * (W + 20)
        yy = (1 - t) ** 2 * 120 + 2 * t * (1 - t) * 230 + t * t * 120
        spot(x, yy + 26, 40, 40, 0, .5, "#FFF3B0", hard=.2)
        clay(ellipse(x, yy + 22, 13, 17), "#FFE27A", depth=4)
    # poles and awning
    for x in (54, W - 54):
        clay(rrect(x - 14, 400, 28, 600, 14), "#A8703F", depth=8)
    n = 12
    sw = (W + 40) / n
    for i in range(n):
        x = -20 + i * sw
        c = "#F2665A" if i % 2 == 0 else "#FFF4E0"
        fill(rect(x, 300, sw + 1, 150), kit.cg(c))
        clay(parse(f"M {x} 446 L {x + sw} 446 C {x + sw} 500 {x} 500 {x} 446 Z"), c, depth=10, shadow=False, shine=False)
    fill(rect(0, 300, W, 30), "#4A2A14", .1)
    clay(rrect(-20, 286, W + 40, 30, 15), "#E2574C", depth=8)
    # hanging bananas and a garlic string
    with at(190, 600):
        stroke(parse("M 0 -110 L 0 -50"), "#8A6B52", 4)
        for k, a in enumerate((-24, 0, 24)):
            with at(k * 10 - 10, -30, a + 90, s=.9):
                food.banana()
    with at(890, 540):
        stroke(parse("M 0 -90 L 0 150"), "#C9A27A", 6)
        for k in range(4):
            with at(0, -50 + k * 56):
                clay(parse("M 0 -26 C 18 -18 26 6 18 18 C 10 26 -10 26 -18 18 C -26 6 -18 -18 0 -26 Z"), "#F6EEE2", depth=6)
                stroke(parse("M 0 -24 L 0 22 M -8 -18 Q -14 0 -8 20 M 8 -18 Q 14 0 8 20"), "#D9C8B0", 2, .6)
    # the stall table: eggs on the left, a scale on the right, the middle free
    clay(rrect(-20, 960, W + 40, 60, 24), "#E2AE72", depth=14, shine=.2)
    wood_grain(20, 972, W - 40, 36, 2, 6, "#E2AE72")
    with at(170, 958):
        clay(rrect(-130, -20, 260, 30, 10), "#E4CDA6", depth=6)
        for ex, ey in ((-56, -66), (0, -66), (56, -66)):
            egg_small(ex, ey, .66)
        for ex, ey in ((-84, -44), (-28, -44), (28, -44), (84, -44)):
            egg_small(ex, ey, .66)
    with at(900, 952, s=1.2):         # a market scale
        contact(0, 6, 80, 10, .3)
        clay(rrect(-60, -60, 120, 66, 20), "#E8574A", depth=10)
        clay(circle(0, -30, 24), "#FFFFFF", depth=6, shadow=False)
        stroke(parse("M 0 -30 L 12 -42"), "#4A2E20", 4)
        clay(ellipse(0, -76, 80, 16), "#C9CED6", depth=6)
        clay(capsule(0, -70, 0, -60, 10), "#AEB6C0", depth=3)
    # three crates: cabbages, tomatoes, carrots
    for cx in (40, 380, 720):
        crate(cx, 1060, 320, 270)
    for i, (x, y) in enumerate(((120, 1050), (200, 1040), (280, 1052), (160, 1074), (240, 1076))):
        cabbage(x, y, 1.35)
    for i, (x, y) in enumerate(((440, 1040), (510, 1032), (580, 1040), (650, 1046), (475, 1070), (545, 1072), (615, 1074))):
        small_tomato(x, y, .78)
    for i in range(8):
        carrot(770 + i * 30, 1046 + (i % 2) * 14, -64 + i * 4, 1.5)
    for x in (200, 540, 880):
        tag(x, 1240)
    # ground
    fill(rect(0, 1330, W, H - 1330), lin([(0, "#E9D6BE"), (1, "#F3E4CF")]))
    fill(rect(0, 1330, W, 40), "#4A2A14", .12)
    for y in range(1460, H, 150):
        stroke(parse(f"M 0 {y} L {W} {y}"), "#D9C3A6", 3, .6)
    INFO["market"] = {"tableTop": 960, "cratesTop": 1060, "ground": 1330}


def main():
    kit.PREC = 0         # whole numbers are plenty at 1080 x 1920, and keep the files small
    kit.LITE = True      # fewer shadow and edge layers: many pieces, and they are seen small
    for name, fn, bg in (("restaurant", restaurant, "#FFE6CC"), ("kitchen", kitchen, "#E9D6BC"), ("market", market, "#FFF0D9")):
        begin()
        fn()
        save(f"scenes/{name}.svg", box=(0, 0, W, H), bg=bg)
    (ART / "scenes" / "scenes.json").write_text(json.dumps(INFO, indent=2) + "\n")
    print("scenes:", ", ".join(INFO))


if __name__ == "__main__":
    main()

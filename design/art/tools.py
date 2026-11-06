"""Kitchen tools and dishes-ware.

    python3 tools.py

Writes app/assets/art/tools/<id>.svg and tools/anchors.json (points the app needs:
the middle and inside radius of the board, bowls, plate, pan, stove; the inside of
the cup; where the lid sits; the tap's spout ...). Long tools stand upright with
their working end at the bottom (whisk, chopsticks, spoon, ladle); the knife and the
pan lie sideways (handle left / right). Things seen from the side stand on the
bottom edge of their picture.
"""
import json
import math
import random

import clay as kit
from clay import (ART, PAN, STEEL, WHITE, WOOD, at, begin, blob, bubbles, capsule, circle, clay, contact, dk, ellipse,
                  fill, group, lin, line, lt, mark, parse, rad, ring_pts, rpoly, rrect, save, spot, stroke, worm)

ANCH = {}


def done(name, **kw):
    r = save(f"tools/{name}.svg", **kw)
    if r["marks"]:
        ANCH[name] = {"viewBox": {"width": r["width"], "height": r["height"]}, **r["marks"]}
    return r


# ---------------------------------------------------------------- helpers
def grain(x, y, w, h, n, seed=1, color=WOOD, op=.3, width=3):
    """Soft wood grooves: a wavy darker line with a light line just under it."""
    r = random.Random(seed)
    for i in range(n):
        yy = y + h * (i + .5) / n + r.uniform(-h / n * .25, h / n * .25)
        x0 = x + r.uniform(0, w * .35)
        x1 = min(x + w, x0 + r.uniform(w * .25, w * .6))
        k = r.uniform(3, 9) * r.choice((-1, 1))
        p = parse(f"M {x0:.1f} {yy:.1f} C {x0 + (x1 - x0) * .3:.1f} {yy + k:.1f} {x0 + (x1 - x0) * .6:.1f} {yy - k:.1f} {x1:.1f} {yy + k * .3:.1f}")
        stroke(p, dk(color, .3), width, op)
        stroke(p, "#FFFFFF", width * .65, op * .9, dx=.6, dy=width * .6)


def glass(p, tint="#DDF1FA", op=.55):
    """See-through plastic: a pale tint, bright edges, no shadow."""
    fill(p, lin([(0, "#FFFFFF", .75), (.18, tint, .25), (.5, tint, .12), (.82, tint, .25), (1, "#FFFFFF", .7)], 0, 0, 1, 0), op)


# ---------------------------------------------------------------- board, knife
BOARD = "#E3AE6E"


def cutting_board():
    clay(rrect(470, 120, 110, 100, 40), BOARD, depth=16)
    clay(capsule(520, 170, 545, 170, 13), dk(BOARD, .25), inv=True, shadow=False)
    clay(rrect(0, 0, 520, 340, 46), BOARD, depth=22, shine=.3, dents=[(440, 280, 14, 20, .5), (70, 60, 11, -20, .5)])
    grain(40, 40, 440, 260, 8, seed=8, color=BOARD, op=.22)
    mark("center", 255, 170)
    mark("area", 255, 170, 130)


SAFE = "#5BBE7A"
BLADE = "#C8DAEA"


def knife():
    blade = parse("M 120 -26 L 300 -26 C 336 -26 352 -4 350 14 C 348 30 330 34 300 34 L 120 34 Z")
    clay(blade, BLADE, depth=8)
    edge = "M 140 30 " + " ".join(f"Q {150 + 20 * i} {38} {160 + 20 * i} 30" for i in range(8))
    stroke(parse(edge), dk(BLADE, .3), 3.5, .6)
    spot(220, -12, 80, 5, 0, .7)
    clay(rrect(100, -30, 30, 68, 10), STEEL, depth=6)
    clay(capsule(0, 4, 104, 4, 26), SAFE, depth=10, dents=[(30, 14, 7, 0, .5)])
    clay(circle(18, 4, 6.5), dk(SAFE, .2), inv=True, shadow=False)
    mark("tip", 350, 6)
    mark("grip", 50, 4)


# ---------------------------------------------------------------- bowl
BOWL_BLUE = "#6FA8DC"


def bowl(egg=False):
    clay(circle(0, 0, 150), WHITE, depth=26, dents=[(96, 96, 14, 30, .4)])
    stroke(circle(0, 0, 134), BOWL_BLUE, 7, .85)
    clay(circle(0, 0, 122), "#F3EEE7", inv=True, shadow=False, depth=20)
    if egg:
        b = blob(ring_pts(0, 6, 104, 100, 20, wob=.015, seed=3))
        clay(b, "#FFC93C", depth=12, shadow=False)
        for i, (r0, a0) in enumerate(((70, 0), (46, 140), (24, 250))):
            pts = [(math.cos(math.radians(a0 + t)) * (r0 + t * .06), 6 + math.sin(math.radians(a0 + t)) * (r0 + t * .06)) for t in range(0, 200, 20)]
            stroke(blob(pts, closed=False), "#FFE08A", 7, .8)
        for x, y, r in ((-40, -30, 6), (-28, -44, 4), (50, 40, 5), (62, 26, 3.5), (8, 66, 4)):
            fill(circle(x, y, r), "#FFF4C8", .85)
        spot(-46, -48, 30, 12, -30, .45)
    mark("center", 0, 0)
    mark("inside", 0, 0, 122)


# ---------------------------------------------------------------- whisk, chopsticks, spoon, ladle
def whisk():
    clay(capsule(0, -170, 0, -70, 17), "#F07A4A", depth=8, dents=[(6, -120, 6, 0, .5)])
    clay(circle(0, -168, 5), dk("#F07A4A", .25), inv=True, shadow=False)
    clay(rrect(-13, -76, 26, 26, 8), STEEL, depth=5)
    for w in (12, 30, 46):
        p = parse(f"M {-6 if w > 12 else -4} -50 C {-w} -10 {-w - 6} 70 0 96 C {w + 6} 70 {w} -10 {6 if w > 12 else 4} -50")
        worm(p, "#B7BEC8", 4.5)
    mark("loops", 0, 40)
    mark("grip", 0, -120)


def chopsticks():
    for sx, a in ((-1, -3.5), (1, 3.5)):
        with at(sx * 18, 0, a):
            clay(rpoly([(-6, -160), (6, -160), (3.2, 160), (-3.2, 160)], 3), "#E0B07A", depth=3)
            clay(rpoly([(-6.4, -162), (6.4, -162), (6, -120), (-6, -120)], 3), "#E25A4E", depth=3)
    mark("tips", 0, 158)


def spoon():
    clay(rpoly([(-11, -170), (11, -170), (7, 20), (-7, 20)], 10), STEEL, depth=6)
    clay(ellipse(0, 70, 50, 64), STEEL, depth=12)
    clay(ellipse(0, 72, 40, 53), dk(STEEL, .05), inv=True, shadow=False, depth=10)
    clay(circle(0, -150, 5.5), dk(STEEL, .2), inv=True, shadow=False)
    mark("bowl", 0, 72, 40)


def ladle():
    worm(parse("M 0 30 L 0 -150 Q 0 -178 -24 -176"), STEEL, 16)
    clay(circle(0, 80, 64), STEEL, depth=14)
    clay(ellipse(0, 76, 54, 50), dk(STEEL, .06), inv=True, shadow=False, depth=10)
    mark("bowl", 0, 76, 50)


# ---------------------------------------------------------------- pan, pot, stove
def pan(handle=True):
    if handle:
        clay(capsule(196, 0, 330, 0, 20), "#A8703F", depth=8, dents=[(290, 6, 6, 0, .5)])
        clay(rrect(150, -14, 64, 28, 8), "#8A9099", depth=5)
    clay(circle(0, 0, 160), PAN, depth=26)
    clay(circle(0, 0, 134), dk(PAN, .12), inv=True, shadow=False, depth=24)
    spot(-62, -84, 50, 14, -38, .18)
    mark("center", 0, 0)
    mark("inside", 0, 0, 134)


POT = "#E8664F"
WATER = "#8FD3F2"


def pot(boil=False):
    contact(0, 182, 160, 12, .3)
    for sx in (-1, 1):
        clay(capsule(sx * 150, -10, sx * 182, -10, 12), dk(POT, .1), depth=5)
    body = parse("M -150 -40 L 150 -40 L 146 140 C 146 168 128 182 100 182 L -100 182 C -128 182 -146 168 -146 140 Z")
    clay(body, POT, depth=24, dents=[(90, 110, 14, 20, .45), (-100, 50, 10, 0, .4)])
    stroke(parse("M -146 20 Q 0 34 146 20"), dk(POT, .15), 6, .35)
    clay(ellipse(0, -40, 158, 34), lt(POT, .1), depth=10, shadow=False)
    clay(ellipse(0, -38, 140, 26), dk(POT, .25), inv=True, shadow=False, depth=6)
    clay(ellipse(0, -34, 132, 20), WATER, shadow=False, depth=6)
    spot(-50, -38, 46, 5, 0, .55)
    if boil:
        bubbles([(-80, -36, 10), (-46, -28, 7), (-10, -38, 12), (26, -30, 8), (60, -38, 10), (92, -32, 6), (-104, -30, 5), (6, -24, 5), (44, -42, 5)])
        for x, h in ((-60, 70), (10, 90), (78, 64)):
            p = parse(f"M {x} -60 C {x - 22} {-60 - h * .3} {x + 22} {-60 - h * .6} {x} {-60 - h}")
            stroke(p, "#FFFFFF", 16, .35)
            stroke(p, "#FFFFFF", 8, .5)
    mark("water", 0, -34)


def flame(x, y, s=1.0, rot=0, outer="#FF9F43", inner="#FFD84D"):
    """A soft round flame, tip up."""
    with at(x, y, rot, s):
        clay(parse("M 0 -40 C 8 -26 24 -16 24 4 C 24 18 13 26 0 26 C -13 26 -24 18 -24 4 C -24 -12 -10 -18 0 -40 Z"), outer, depth=7, shadow=False)
        clay(parse("M 0 -18 C 5 -10 13 -4 13 7 C 13 15 7 19 0 19 C -7 19 -13 15 -13 7 C -13 -3 -6 -8 0 -18 Z"), inner, depth=4, shadow=False)


def stove():
    clay(rrect(0, 0, 400, 400, 54), "#5B6068", depth=24)
    clay(rrect(22, 22, 356, 356, 40), "#666B74", inv=True, shadow=False, depth=14)
    with at(200, 196):
        clay(circle(0, 0, 132), "#45494F", inv=True, shadow=False, depth=14)
        fill(circle(0, 0, 128), rad([(0, "#5AB0FF", 0), (.5, "#5AB0FF", 0), (.72, "#7CC4FF", .55), (1, "#5AB0FF", 0)]))
        n = 12
        for i in range(n):
            a = 360 * i / n
            ax, ay = math.cos(math.radians(a)) * 86, math.sin(math.radians(a)) * 86
            flame(ax, ay, .78, a + 90)
        clay(circle(0, 0, 62), "#4A4E55", depth=10)
        clay(circle(0, 0, 42), "#2F3237", inv=True, shadow=False, depth=8)
        for a in (45, 135, 225, 315):
            with at(0, 0, a):
                clay(capsule(122, 0, 150, 0, 9), "#30343A", depth=4)
    clay(circle(344, 350, 22), "#9BA3AD", depth=7)
    clay(capsule(344, 338, 344, 362, 5), "#7C848E", depth=2.5)
    mark("center", 200, 196)
    mark("flame", 200, 196, 120)


# ---------------------------------------------------------------- sink, soap
def sink():
    clay(rrect(0, 0, 440, 340, 50), "#D5DBE2", depth=24)
    clay(rrect(34, 60, 372, 252, 50), "#BCC4CE", inv=True, shadow=False, depth=30, dents=[])
    clay(circle(220, 250, 22), "#A9B2BD", depth=6, shadow=False)
    for k in (-8, 0, 8):
        stroke(parse(f"M {220 + k} 240 L {220 + k} 260"), "#7D8793", 3, .8)
    # the tap, seen from above
    clay(rrect(170, 4, 100, 40, 18), "#C9CED6", depth=8)
    clay(capsule(220, 26, 220, 118, 15), "#B9C0CA", depth=6)
    clay(circle(220, 120, 17), "#AEB6C0", depth=5)
    clay(circle(220, 120, 8), "#7D8793", inv=True, shadow=False)
    clay(capsule(196, 24, 158, 30, 9), "#E8574A", depth=4)
    clay(capsule(244, 24, 282, 30, 9), "#4FA3E0", depth=4)
    mark("spout", 220, 120)
    mark("basin", 220, 186)


SOAP = "#FFB3C7"


def soap():
    contact(0, 72, 110, 10, .3)
    clay(rrect(-110, -20, 220, 92, 34), dk(SOAP, .06), depth=14)
    clay(rrect(-104, -36, 208, 76, 32), SOAP, depth=14, shadow=False, dents=[(50, 0, 12, 20, .5)])
    clay(rrect(-60, -18, 120, 36, 16), lt(SOAP, .25), inv=True, shadow=False, depth=6)
    bubbles([(-70, -46, 22), (-36, -62, 28), (6, -52, 18), (40, -66, 24), (76, -46, 16), (-6, -86, 14), (28, -34, 10), (-88, -20, 10)])


# ---------------------------------------------------------------- plate, tray
def plate(r=150):
    clay(circle(0, 0, r), WHITE, depth=r * .16, dents=[(r * .62, r * .6, r * .08, 30, .35)])
    clay(circle(0, 0, r * .72), "#F5F0E9", inv=True, shadow=False, depth=r * .1)
    stroke(circle(0, 0, r * .86), "#F2C89A", r * .025, .7)
    mark("center", 0, 0)
    mark("inside", 0, 0, r * .72)


TRAY = "#F0955A"


def tray():
    clay(rrect(0, 0, 500, 330, 54), TRAY, depth=24, dents=[(420, 270, 12, 20, .45)])
    clay(rrect(34, 34, 432, 262, 34), lt(TRAY, .1), inv=True, shadow=False, depth=14)
    for x in (12, 466):
        clay(capsule(x + 11, 135, x + 11, 195, 9), dk(TRAY, .3), inv=True, shadow=False)
    mark("center", 250, 165)


# ---------------------------------------------------------------- cup, lid, straw
CUP_TOP, CUP_BOT, CUP_H = 78, 58, 220     # half widths at the top and bottom, height (y 0..CUP_H)


def cup_shape(inset=0):
    t, b, h = CUP_TOP - inset, CUP_BOT - inset, CUP_H
    return parse(f"M {-t} {inset * .5} L {t} {inset * .5} L {b + 3} {h - 18 - inset * .3} Q {b} {h - inset} {b - 18} {h - inset} "
                 f"L {-b + 18} {h - inset} Q {-b} {h - inset} {-b - 3} {h - 18 - inset * .3} Z")


def cup_back():
    """The back half of the cup (behind the drink)."""
    contact(0, CUP_H, CUP_BOT + 16, 9, .25)
    glass(cup_shape(), op=.5)


def cup_front():
    """The front half: shine streaks, ridges and the rim."""
    s = cup_shape()
    with group(clip=s):
        stroke(parse(f"M {-CUP_TOP + 22} 18 L {-CUP_BOT + 16} {CUP_H - 26}"), "#FFFFFF", 10, .7)
        stroke(parse(f"M {-CUP_TOP + 40} 18 L {-CUP_BOT + 30} {CUP_H - 40}"), "#FFFFFF", 4, .55)
        stroke(parse(f"M {CUP_TOP - 20} 22 L {CUP_BOT - 12} {CUP_H - 30}"), "#FFFFFF", 5, .45)
        for y in (CUP_H - 34,):
            stroke(parse(f"M {-CUP_TOP} {y} Q 0 {y + 8} {CUP_TOP} {y}"), "#BFDDEB", 3, .45)
    stroke(s, "#B9DCEC", 2.5, .6)
    clay(capsule(-CUP_TOP - 2, 1, CUP_TOP + 2, 1, 6), "#EAF6FB", depth=3, shadow=False, opacity=.9)
    grow = kit.grow_path
    grow(s)


def cup():
    cup_back()
    cup_front()
    mark("insideTopLeft", -CUP_TOP + 4, 8)
    mark("insideTopRight", CUP_TOP - 4, 8)
    mark("insideBottomLeft", -CUP_BOT + 6, CUP_H - 6)
    mark("insideBottomRight", CUP_BOT - 6, CUP_H - 6)
    mark("rim", 0, 0)


def lid():
    glass(parse("M -70 -6 C -66 -52 66 -52 70 -6 Z"), "#EAF7FD", .75)
    stroke(parse("M -48 -30 Q -30 -46 0 -48"), "#FFFFFF", 6, .8)
    stroke(parse("M -70 -6 C -66 -52 66 -52 70 -6"), "#B9DCEC", 2.5, .6)
    clay(rrect(-12, -54, 24, 10, 4), "#EAF6FB", depth=2, shadow=False, opacity=.9)
    clay(rrect(-CUP_TOP - 6, -10, 2 * CUP_TOP + 12, 14, 7), "#EEF8FC", depth=4, shadow=False, opacity=.95)
    mark("rim", 0, 0)
    mark("hole", 0, -50)


STRAW = "#FF7F9C"


def straw(top=-170, bottom=170):
    w = 13
    body = parse(f"M {-w} {top} L {w} {top} L {w} {bottom - 16} L {-w} {bottom + 10} Z")
    fill(body, lin([(0, lt(STRAW, .1)), (.35, lt(STRAW, .45)), (.65, STRAW), (1, dk(STRAW, .15))], 0, 0, 1, 0), .92)
    with group(clip=body):
        stroke(parse(f"M -6 {top + 6} L -6 {bottom}"), "#FFFFFF", 4, .7)
    clay(ellipse(0, top, w, 4.5), lt(STRAW, .2), depth=2, shadow=False)
    fill(ellipse(0, top, w - 4, 2.2), dk(STRAW, .35), .6)
    kit.grow_path(body)
    mark("top", 0, top)
    mark("tip", 0, bottom)


TEAPOT = "#7FC8B8"


def teapot():
    """A round clay teapot, side view, spout to the left."""
    contact(0, 118, 120, 11, .32)
    worm(parse("M 104 -30 C 168 -40 176 70 104 70"), dk(TEAPOT, .06), 22)
    clay(parse("M -98 30 C -130 10 -150 -30 -176 -52 C -186 -60 -172 -76 -160 -66 C -134 -46 -108 -24 -84 -14 Z"), TEAPOT, depth=9)
    clay(rpoly([(-179, -62), (-171, -78), (-156, -70), (-163, -55)], 6), dk(TEAPOT, .08), depth=3, shadow=False)
    clay(blob([(0, -82), (70, -70), (116, -20), (118, 40), (84, 100), (0, 120), (-84, 100), (-118, 40), (-116, -20), (-70, -70)]),
         TEAPOT, depth=26, dents=[(60, 60, 12, 20, .5), (-70, 10, 9, 0, .4)])
    stroke(parse("M -112 14 Q 0 34 112 14"), "#FFFFFF", 12, .5)
    for x in (-60, -20, 20, 60):
        clay(circle(x, 22, 6), "#FFFFFF", depth=2, shadow=False)
    clay(ellipse(0, -76, 78, 18), dk(TEAPOT, .08), depth=8, shadow=False)
    clay(parse("M -62 -80 C -50 -120 50 -120 62 -80 Z"), lt(TEAPOT, .08), depth=10)
    clay(circle(0, -118, 15), "#FFB23F", depth=6)
    mark("spout", -174, -70)
    mark("pivot", 0, 20)


def all_tools():
    items = [
        ("cutting_board", cutting_board, {}), ("knife", knife, {}), ("bowl", lambda: bowl(False), {}),
        ("bowl_egg", lambda: bowl(True), {}), ("whisk", whisk, {}), ("chopsticks", chopsticks, {}),
        ("spoon", spoon, {}), ("ladle", ladle, {}), ("pan", pan, {}), ("stove", stove, {}),
        ("sink", sink, {}), ("soap", soap, {"rest": True}), ("plate", plate, {}), ("tray", tray, {}),
        ("cup", cup, {"rest": True}), ("lid", lid, {}), ("straw", straw, {}), ("teapot", teapot, {"rest": True}),
    ]
    for name, fn, kw in items:
        begin()
        fn()
        done(name, **kw)
    # the pot, the same size with and without bubbles
    boxes = []
    for boil in (False, True):
        begin()
        pot(boil)
        boxes.append(list(kit.PG.box))
    x0 = math.floor(min(b[0] for b in boxes) - 4)
    y0 = math.floor(min(b[1] for b in boxes) - 4)
    x1 = math.ceil(max(b[2] for b in boxes) + 4)
    y1 = math.ceil(max(b[3] for b in boxes))
    for boil in (False, True):
        begin()
        pot(boil)
        done("pot_boil" if boil else "pot", box=(x0, y0, x1 - x0, y1 - y0))


def main():
    all_tools()
    (ART / "tools" / "anchors.json").write_text(json.dumps(ANCH, indent=2, ensure_ascii=False) + "\n")
    print("tools:", len(list((ART / "tools").glob("*.svg"))))


if __name__ == "__main__":
    main()

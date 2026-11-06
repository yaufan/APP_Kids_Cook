"""The animal customers and the child's chef badge.

    python3 customers.py

customers/<id>.svg        smiling, eyes open
customers/<id>_happy.svg  eyes closed (^ ^), big open smile, rosy cheeks
customers/customers.json  size of each picture and where its mouth is
chef/chef.svg             the child's avatar: a round face in a chef hat

Each customer is seen from the waist up behind a counter: the picture is cut flat
at the bottom, where the counter's back edge is, and the paws rest on that edge.
The two pictures of one animal have exactly the same size and position.
Drawn in local units round the head (head about 125 wide), scaled by SCALE.
"""
import json
import math

from clay import (ART, BLUSH, INK, WHITE, at, begin, blob, capsule, circle, clay, dk, ellipse, eye, fill, group, lt, mark,
                  parse, rrect, rpoly, save, spot, stroke, worm)
import clay as kit

SCALE = 2.4
CUT = 150            # local y of the counter edge (the flat bottom of the picture)
MOUTH_IN = "#7A3328"
TONGUE = "#FF8C8C"


# ---------------------------------------------------------------- shared bits
HEAD = 1.12          # heads are drawn a little bigger than the bodies (cuter)


def torso(color, w_top=58, w_bot=82, top=54):
    p = parse(f"M {-w_top} {top + 8} C {-w_top - 16} {top + 18} {-w_bot + 2} {top + 50} {-w_bot} {CUT + 30} "
              f"L {w_bot} {CUT + 30} C {w_bot - 2} {top + 50} {w_top + 16} {top + 18} {w_top} {top + 8} Q 0 {top - 12} {-w_top} {top + 8} Z")
    clay(p, color, depth=13, dents=[(-42, 116, 8, 20, .5), (48, 100, 6, -10, .45)])
    return p


def paws(color, x=46):
    for sx in (-1, 1):
        clay(ellipse(sx * x, CUT - 3, 25, 16), color, depth=6)
        for k in (-8, 0, 8):
            stroke(parse(f"M {sx * x + k} {CUT - 15} L {sx * x + k} {CUT - 8}"), dk(color, .3), 1.8, .35)


def eyes(dx, y, happy, rx=6.5, ry=8):
    for sx in (-1, 1):
        if happy:
            worm(parse(f"M {sx * dx - 8} {y + 3} Q {sx * dx} {y - 8} {sx * dx + 8} {y + 3}"), INK, 4.2)
        else:
            eye(sx * dx, y, rx, ry)


def cheeks(dx, y, happy, rx=11, ry=7):
    for sx in (-1, 1):
        if happy:
            spot(sx * dx, y + 1, rx * 1.35, ry * 1.35, 0, .95, "#FF7F8E", hard=.45)
        else:
            spot(sx * dx, y, rx, ry, 0, .75, BLUSH, hard=.45)


def open_mouth(y, w=13, h=12):
    """A big open smile: dark inside, pink tongue, soft clay lip."""
    p = parse(f"M {-w} {y} Q 0 {y - 3} {w} {y} C {w} {y + h * .9} {w * .45} {y + h * 1.15} 0 {y + h * 1.15} "
              f"C {-w * .45} {y + h * 1.15} {-w} {y + h * .9} {-w} {y} Z")
    clay(p, MOUTH_IN, depth=2.5, shine=False)
    clay(ellipse(0, y + h * .82, w * .55, h * .32), TONGUE, depth=1.6, shadow=False)
    worm(parse(f"M {-w - 1} {y} Q 0 {y - 3} {w + 1} {y}"), MOUTH_IN, 2.6, shadow=False, shine=False)


def chef_hat(y=-62, s=1.0):
    with at(0, y, s=s):
        for cx, cy, r in ((-32, -12, 24), (32, -12, 24), (0, -26, 30)):
            clay(circle(cx, cy, r), WHITE, depth=8)
        clay(rrect(-46, 0, 92, 26, 12), "#F4EEE6", depth=6, dents=[(26, -16, 8, 30, .5)])
        spot(-10, -40, 9, 5, -30, .55)


def bow_tie(y, color="#FF7B6B"):
    with at(0, y):
        clay(rpoly([(0, 0), (-21, -12), (-21, 13)], 5), color, depth=4)
        clay(rpoly([(0, 0), (21, -12), (21, 13)], 5), color, depth=4)
        clay(circle(0, 0, 6.5), color, depth=2.5)


# ---------------------------------------------------------------- bear
BEAR, BEAR_LT, BEAR_EAR, NOSE = "#B67B4E", "#F0D0A4", "#E9B387", "#3B2418"


def bear_head(happy, hat=False):
    for sx in (-1, 1):
        clay(circle(sx * 50, -30, 20), BEAR, depth=7)
        clay(circle(sx * 50, -30, 10), BEAR_EAR, inv=True, shadow=False)
    clay(ellipse(0, 4, 64, 56), BEAR, depth=13, dents=[(36, -16, 9, 25, .9), (-40, 34, 7, -10, .7)])
    clay(ellipse(0, 24, 30, 21), BEAR_LT, depth=6)
    clay(ellipse(0, 13, 10, 7.5), NOSE, depth=3)
    spot(-3, 10, 3.5, 2, 0, .7)
    eyes(25, -4, happy)
    cheeks(42, 18, happy)
    if happy:
        open_mouth(25, 11, 11)
        mark("mouth", 0, 31)
    else:
        worm(parse("M -10 30 Q -5 37 0 30 Q 5 37 10 30"), NOSE, 3.4)
        mark("mouth", 0, 32)
    if hat:
        chef_hat(-50)
    mark("headTop", 0, -52 if not hat else -118)


def bear(happy):
    torso("#5FB7A6")
    clay(parse("M -30 54 L 0 88 L 30 54 Q 0 46 -30 54 Z"), WHITE, depth=4)
    with at(0, 0, s=HEAD):
        bear_head(happy)
    bow_tie(78)
    paws(BEAR)


# ---------------------------------------------------------------- rabbit
FUR_R, EAR_R = "#FFF4EA", "#FFB9C6"


def rabbit(happy):
    torso("#FFB3C7")
    clay(parse("M -32 62 L 32 62 L 27 114 Q 0 128 -27 114 Z"), WHITE, depth=6)
    clay(circle(-15, 102, 3.2), "#FFB3C7", depth=1, shadow=False)
    clay(circle(15, 102, 3.2), "#FFB3C7", depth=1, shadow=False)
    with at(0, 0, s=HEAD):
        for sx in (-1, 1):
            clay(ellipse(sx * 24, -80, 16, 44, sx * 9), FUR_R, depth=7)
            clay(ellipse(sx * 24, -76, 7.5, 30, sx * 9), EAR_R, inv=True, shadow=False)
        clay(ellipse(0, 6, 60, 52), FUR_R, depth=12, dents=[(34, -14, 8, 20, .8)])
        clay(ellipse(0, 24, 24, 16), WHITE, depth=5)
        clay(parse("M -7 13 Q 0 9 7 13 Q 4 20 0 21 Q -4 20 -7 13 Z"), "#FF8FA6", depth=2)
        eyes(24, -2, happy)
        cheeks(40, 16, happy)
        if happy:
            open_mouth(27, 10, 10)
            mark("mouth", 0, 32)
        else:
            worm(parse("M -9 26 Q -4.5 32 0 26 Q 4.5 32 9 26"), INK, 3)
            clay(rrect(-5, 30, 10, 8, 2.5), WHITE, depth=1.5)
            mark("mouth", 0, 29)
        mark("headTop", 0, -122)
    bow_tie(64, "#FF8FB1")
    paws(FUR_R)


# ---------------------------------------------------------------- cat
CAT, CAT_DK, CAT_EAR = "#F4A259", "#D9792C", "#FFB4B8"


def cat(happy):
    body = torso("#5B8BE0")
    with group(clip=body):
        for y in (90, 112, 134):
            stroke(parse(f"M -90 {y} Q 0 {y + 8} 90 {y}"), "#FFFFFF", 9, .85)
    with at(0, 0, s=HEAD):
        for sx in (-1, 1):
            clay(rpoly([(sx * 20, -40), (sx * 62, -64), (sx * 58, -10)], 9), CAT, depth=7)
            clay(rpoly([(sx * 28, -36), (sx * 55, -52), (sx * 52, -18)], 6), CAT_EAR, inv=True, shadow=False)
        clay(ellipse(0, 6, 64, 53), CAT, depth=13, dents=[(-38, 30, 7, -10, .7)])
        for x, h in ((-12, 16), (0, 20), (12, 16)):
            worm(parse(f"M {x} -45 Q {x * 1.2} {-45 + h * .5} {x} {-45 + h}"), CAT_DK, 4.5, shadow=False)
        for sx in (-1, 1):
            worm(parse(f"M {sx * 63} 2 Q {sx * 52} 4 {sx * 46} 8"), CAT_DK, 4, shadow=False)
        clay(ellipse(-12, 25, 16, 13), "#FFF6EA", depth=4)
        clay(ellipse(12, 25, 16, 13), "#FFF6EA", depth=4)
        clay(rpoly([(-7, 13), (7, 13), (0, 21)], 3), "#FF8FA6", depth=2)
        for sx in (-1, 1):
            for dy in (-4, 4):
                stroke(parse(f"M {sx * 30} {24 + dy} Q {sx * 46} {22 + dy * 1.6} {sx * 60} {20 + dy * 2.6}"), "#FFFFFF", 2.2, .9)
        eyes(25, -4, happy, 6.5, 8.5)
        cheeks(42, 18, happy)
        if happy:
            open_mouth(26, 10, 10)
            mark("mouth", 0, 31)
        else:
            worm(parse("M -9 25 Q -4.5 31 0 25 Q 4.5 31 9 25"), INK, 3)
            mark("mouth", 0, 28)
        mark("headTop", 0, -62)
    clay(rpoly([(-34, 62), (34, 62), (0, 100)], 9), "#F0564B", depth=5)
    paws(CAT)


# ---------------------------------------------------------------- pig
PIG, PIG_DK, SNOUT = "#FFB7C6", "#FF94AA", "#C9566E"


def pig_head(happy, bandana=True):
    for sx in (-1, 1):
        clay(parse(f"M {sx * 24} -40 Q {sx * 56} -72 {sx * 62} -36 Q {sx * 58} -18 {sx * 40} -22 Z"), PIG_DK, depth=7)
    clay(ellipse(0, 6, 62, 54), PIG, depth=13, dents=[(36, 34, 7, 20, .6)])
    if bandana:
        clay(parse("M -58 -14 C -56 -58 56 -58 58 -14 C 30 -27 -30 -27 -58 -14 Z"), "#4FB286", depth=7)
        for x, y in ((-30, -35), (-8, -43), (14, -41), (36, -31), (-44, -23), (0, -29), (24, -27)):
            clay(circle(x, y, 3.2), "#FFFFFF", depth=1, shadow=False, edge=False)
        clay(ellipse(56, -10, 10, 7, 30), "#4FB286", depth=3)
        clay(ellipse(66, -1, 9, 5, 70), "#4FB286", depth=2.5)
    clay(ellipse(0, 22, 21, 15), PIG_DK, depth=6)
    clay(ellipse(-7, 22, 3.5, 5), SNOUT, inv=True, shadow=False)
    clay(ellipse(7, 22, 3.5, 5), SNOUT, inv=True, shadow=False)
    eyes(27, 0, happy)
    cheeks(45, 24, happy)
    if happy:
        open_mouth(41, 10, 10)
        mark("mouth", 0, 46)
    else:
        worm(parse("M -10 42 Q -5 49 0 42 Q 5 49 10 42"), INK, 3.2)
        mark("mouth", 0, 45)
    mark("headTop", 0, -56)


def pig(happy):
    torso("#FFD166")
    for sx in (-1, 1):
        clay(capsule(sx * 36, 66, sx * 42, 170, 6), "#4FB286", depth=3)
        clay(circle(sx * 38, 112, 4.5), "#FFFFFF", depth=1.5)
    with at(0, 0, s=HEAD):
        pig_head(happy)
    paws(PIG)


# ---------------------------------------------------------------- duck
DUCK, DUCK_DK, BILL = "#FFD84D", "#F2B92B", "#FF9A3C"


def duck(happy):
    torso(DUCK)
    for sx in (-1, 1):   # wing tips resting on the counter
        with at(sx * 48, CUT - 6, sx * -8, sx=sx):
            clay(parse("M -26 6 C -30 -14 -10 -22 8 -18 C 24 -14 32 -2 28 8 C 24 14 -22 16 -26 6 Z"), DUCK_DK, depth=6)
            for k in (-6, 6):
                stroke(parse(f"M {k - 4} -10 Q {k + 2} -2 {k} 8"), dk(DUCK_DK, .25), 2.2, .45)
    with at(0, 0, s=HEAD):
        clay(circle(0, 0, 60), DUCK, depth=12, dents=[(36, -20, 8, 20, .7), (-40, 28, 6, 0, .6)])
        for a, x in ((-20, -8), (0, 0), (20, 8)):
            clay(ellipse(x, -62, 5, 13, a), DUCK, depth=3)
        eyes(23, -10, happy)
        cheeks(40, 14, happy)
        if happy:   # bill open
            clay(parse("M -20 22 Q 0 46 20 22 Q 0 30 -20 22 Z"), BILL, depth=4)
            clay(parse("M -14 26 Q 0 40 14 26 Q 0 32 -14 26 Z"), MOUTH_IN, depth=2, shadow=False, shine=False)
            clay(ellipse(0, 31, 6, 3), TONGUE, depth=1, shadow=False)
            clay(parse("M -28 12 C -28 0 28 0 28 12 C 28 22 -28 22 -28 12 Z"), BILL, depth=5)
            mark("mouth", 0, 28)
        else:
            clay(parse("M -28 12 C -28 0 28 0 28 12 C 28 30 -28 30 -28 12 Z"), BILL, depth=6)
            stroke(parse("M -20 18 Q 0 24 20 18"), dk(BILL, .3), 2.4, .5)
            stroke(parse("M -6 7 L -4 8 M 6 7 L 4 8"), dk(BILL, .35), 2, .5)
            mark("mouth", 0, 19)
        mark("headTop", 0, -76)
    # a knitted scarf round the neck, one end hanging
    clay(rrect(14, 70, 24, 40, 9, -10), "#4FB286", depth=6)
    for y in (82, 96):
        stroke(parse(f"M 16 {y + 2} L 37 {y - 2}"), "#FFFFFF", 4, .85)
    for x in (18, 26, 34):
        stroke(parse(f"M {x + 3} 109 L {x + 2} 118"), "#3E9A70", 3.2)
    clay(parse("M -50 56 Q 0 76 50 56 L 52 72 Q 0 96 -52 72 Z"), "#4FB286", depth=6)
    for x in (-30, -10, 10, 30):
        stroke(parse(f"M {x} {64 + abs(x) * -.1 + 6} L {x} {78 + abs(x) * -.1 + 4}"), "#3E9A70", 2, .5)


# ---------------------------------------------------------------- chef badge
HAIR = "#4A2E22"
CHILD = "#FFD2A8"


def chef_face():
    for sx in (-1, 1):
        clay(circle(sx * 38, 10, 9), CHILD, depth=3)
    clay(circle(0, 6, 40), CHILD, depth=9, dents=[(22, 26, 6, 20, .5)])
    clay(parse("M -41 8 C -46 -30 46 -30 41 8 C 38 -2 30 -8 24 -8 C 20 -2 12 -2 8 -9 C 2 -3 -8 -3 -12 -9 C -18 -2 -28 -2 -32 -8 C -36 -4 -39 2 -41 8 Z"), HAIR, depth=6)
    for sx in (-1, 1):
        eye(sx * 14, 8, 4.4, 5.4)
        spot(sx * 25, 20, 7, 4.5, 0, .8, BLUSH, hard=.45)
    worm(parse("M -8 25 Q 0 32 8 25"), INK, 2.6)
    with at(0, -22, s=.64):
        chef_hat(0)


# ---------------------------------------------------------------- write
ANIMALS = {"bear": bear, "rabbit": rabbit, "cat": cat, "pig": pig, "duck": duck}


def draw(fn, happy):
    begin()
    with at(0, 0, s=SCALE):
        fn(happy)
    return kit.PG


def main():
    info = {}
    for cid, fn in ANIMALS.items():
        boxes = []
        for happy in (False, True):
            boxes.append(list(draw(fn, happy).box))
        half = math.ceil(max(max(-b[0], b[2]) for b in boxes) + 4)   # the same space left and right
        y0 = math.floor(min(b[1] for b in boxes) - 4)
        box = (-half, y0, 2 * half, round(CUT * SCALE) - y0)
        res = {}
        for happy in (False, True):
            draw(fn, happy)
            res[happy] = save(f"customers/{cid}{'_happy' if happy else ''}.svg", box=box)
        r = res[False]
        info[cid] = {"viewBox": {"width": r["width"], "height": r["height"]},
                     "mouth": r["marks"]["mouth"], "mouthHappy": res[True]["marks"]["mouth"],
                     "headTop": r["marks"]["headTop"]}
    (ART / "customers" / "customers.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n")
    begin()
    with at(0, 0, s=3):
        chef_face()
    save("chef/chef.svg", square=True)
    print("customers:", ", ".join(info))


if __name__ == "__main__":
    main()

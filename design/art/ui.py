"""Small pictures for the app's buttons and badges, and the recipe book's dish icons.

    python3 ui.py

ui/<id>.svg      coin, star, recipe_book, check, hands_wash, adult_help, fire, heart,
                 speech, arrow_flip, hand_hint, sparkle
ui/anchors.json  speech: the box inside the bubble for the order; hand_hint: the fingertip
dishes/<id>.svg  sandwich, fruit_skewer, danbing, milk_tea, dumplings: each finished
                 dish as served, in a square picture
"""
import json
import math

import clay as kit
import food
import tools
from clay import (ART, GOLD, SKIN, WHITE, at, begin, bubbles, capsule, circle, clay, contact, dk, ellipse, fill, group,
                  lt, mark, parse, rpoly, rrect, save, sparkle as twinkle, spot, star_pts, stroke, worm)

ANCH = {}


def done(rel, **kw):
    r = save(rel, **kw)
    if r["marks"]:
        ANCH[rel.split("/")[-1][:-4]] = {"viewBox": {"width": r["width"], "height": r["height"]}, **r["marks"]}
    return r


# ---------------------------------------------------------------- ui
def coin():
    r = 64
    clay(circle(0, 0, r), GOLD, depth=12)
    stroke(circle(0, 0, r * .74), dk(GOLD, .25), r * .08, .45)
    stroke(circle(0, 0, r * .74), "#FFFFFF", r * .05, .45, dx=1.6, dy=1.6)
    spot(-r * .42, -r * .48, r * .26, r * .14, -40, .7)


def star():
    clay(rpoly(star_pts(70, 38), 13), "#FFC83A", depth=12, dents=[(24, 18, 6, 20, .5)])
    spot(-14, -22, 12, 7, -30, .7)


def recipe_book():
    clay(rrect(-56, -70, 128, 156, 16), "#FFF3DE", depth=10)
    for k in range(3):
        stroke(parse(f"M {66 - k * 0} {-58 + k * 5} L {66} {74 - k * 5}"), "#E8D6B8", 2, .7, dx=-k * 4)
    clay(rrect(-70, -78, 128, 158, 18), "#E8573F", depth=14, dents=[(30, 50, 8, 20, .5)])
    clay(rrect(-70, -78, 26, 158, 12), dk("#E8573F", .18), depth=6, shadow=False)
    clay(rrect(-24, -40, 70, 70, 18), "#FFF6EA", depth=8, shadow=False)
    with at(11, -4, s=.48):
        for cx, cy, r in ((-32, -12, 24), (32, -12, 24), (0, -26, 30)):
            clay(circle(cx, cy, r), WHITE, depth=8)
        clay(rrect(-46, 0, 92, 26, 12), "#F4EEE6", depth=6)
    clay(parse("M 24 70 L 40 70 L 40 104 L 32 96 L 24 104 Z"), "#FFC83A", depth=4)


def check():
    clay(circle(0, 0, 64), "#5DBB63", depth=12)
    worm(parse("M -28 2 L -8 22 L 28 -20"), "#FFFFFF", 16)


def kid_hand(sx=1, sleeve="#7EC8F0"):
    """Small open hand, fingers up; thumb on the left (sx=1) or right (sx=-1). About 34 wide, 60 tall."""
    clay(rrect(-14, 14, 28, 14, 6), sleeve, depth=3)
    for x, h in ((-9, 20), (-3, 24), (3, 23), (9, 19)):
        clay(rrect(x * sx - 3.3, -8 - h, 6.6, h + 10, 3.3), SKIN, depth=1.6)
    clay(rrect(-13, -12, 26, 28, 9), SKIN, depth=4)
    clay(ellipse(-14 * sx, 0, 4.5, 10, 30 * sx), SKIN, depth=1.6)


def hands_wash():
    with at(0, 0, s=2.4):
        with at(-20, 10, -14, s=1.15):
            kid_hand(-1)
        with at(20, 10, 14, s=1.15):
            kid_hand(1)
        for x, y, r in ((-6, -6, 7), (2, -12, 8), (8, -2, 6), (-2, 4, 6), (-24, -16, 5), (24, -14, 5), (-14, -24, 4)):
            clay(circle(x, y, r), WHITE, depth=2.2, sh_op=.6)
        bubbles([(-30, -36, 9), (0, -46, 12), (28, -32, 8), (-8, 8, 6), (40, 2, 6), (-40, -2, 5), (16, -16, 5)])


def adult_hand():
    """A grown-up's open hand with a sleeve, palm to us."""
    hand = "#F2C29B"
    with at(0, 0, s=2.6):
        clay(rrect(-17, 22, 36, 22, 8), "#4F7BD9", depth=4)
        clay(rrect(-19, 36, 40, 8, 4), dk("#4F7BD9", .2), depth=2, shadow=False)
        for x, h, a in ((-13, 22, -8), (-4.5, 28, -2), (4.5, 27, 3), (13, 22, 9)):
            with at(x, -8, a):
                clay(rrect(-4, -h, 8, h + 8, 4), hand, depth=1.8)
        clay(rrect(-18, -12, 36, 38, 12), hand, depth=5, dents=[(4, 6, 4, 0, .5)])
        with at(-20, 6, 36):
            clay(rrect(-5, -16, 10, 26, 5), hand, depth=1.8)
        stroke(parse("M -10 4 Q 0 10 10 2"), dk(hand, .2), 1.6, .4)


def fire():
    with at(0, 0, s=3.0):
        clay(parse("M 0 -44 C 10 -30 30 -18 30 6 C 30 24 16 34 0 34 C -16 34 -30 24 -30 6 C -30 -10 -20 -16 -16 -28 "
                   "C -12 -20 -8 -16 -6 -14 C -6 -24 -4 -34 0 -44 Z"), "#FF7A3D", depth=7)
        clay(parse("M 0 -20 C 8 -10 18 -2 18 10 C 18 20 10 26 0 26 C -10 26 -18 20 -18 10 C -18 -2 -8 -8 0 -20 Z"), "#FFB23F", depth=5, shadow=False)
        clay(parse("M 0 2 C 5 8 10 12 10 18 C 10 23 5 26 0 26 C -5 26 -10 23 -10 18 C -10 12 -5 8 0 2 Z"), "#FFE27A", depth=3, shadow=False)


def heart():
    s = 3.2
    clay(parse(f"M 0 {12 * s} C {-20 * s} {-2 * s} {-22 * s} {-18 * s} {-10 * s} {-22 * s} C {-4 * s} {-24 * s} 0 {-18 * s} 0 {-14 * s} "
               f"C 0 {-18 * s} {4 * s} {-24 * s} {10 * s} {-22 * s} C {22 * s} {-18 * s} {20 * s} {-2 * s} 0 {12 * s} Z"),
         "#FF6F91", depth=12, dents=[(22, 6, 6, 20, .5)])
    spot(-30, -48, 12, 7, -35, .7)


def speech():
    W, H, R = 420, 280, 70
    d = (f"M {R} 0 L {W - R} 0 C {W - R * .45} 0 {W} {R * .45} {W} {R} L {W} {H - R} C {W} {H - R * .45} {W - R * .45} {H} {W - R} {H} "
         f"L {W / 2 + 36} {H} C {W / 2 + 24} {H + 22} {W / 2 + 8} {H + 46} {W / 2 - 14} {H + 58} C {W / 2 - 8} {H + 40} {W / 2 - 14} {H + 16} {W / 2 - 34} {H} "
         f"L {R} {H} C {R * .45} {H} 0 {H - R * .45} 0 {H - R} L 0 {R} C 0 {R * .45} {R * .45} 0 {R} 0 Z")
    clay(parse(d), "#FFFFFF", depth=22, dents=[(W - 60, H - 50, 12, 20, .35)], shine=.35)
    mark("content", W / 2, H / 2)
    mark("contentTopLeft", 40, 34)
    mark("contentBottomRight", W - 40, H - 34)
    mark("tail", W / 2 - 14, H + 58)


def arrow_flip():
    worm(parse("M -70 50 C -86 -30 -10 -78 50 -50 C 70 -40 80 -24 84 -6"), "#FF8A3D", 22)
    a = math.atan2(1, .14)
    with at(86, 4, math.degrees(a) - 90):
        clay(rpoly([(-30, -6), (30, -6), (0, 34)], 9), "#FF8A3D", depth=7)


def hand_hint():
    with at(0, 0, s=2.6):
        clay(rrect(-16, 46, 34, 18, 8), "#7EC8F0", depth=4)
        clay(rrect(-17, 12, 36, 40, 15), SKIN, depth=6)
        clay(rrect(-7, -2, 14, 36, 7), SKIN, depth=3)
        for y in (22, 32):
            clay(rrect(5, y - 5, 16, 11, 5.5), SKIN, depth=2, sh_op=.6)
        clay(ellipse(-18, 30, 7, 11, -25), SKIN, depth=2)
        clay(ellipse(0, 4, 4, 4.5), "#FFE9D6", depth=1, shadow=False)
        mark("fingertip", 0, -2)


def sparkle():
    twinkle(0, 0, 60, "#FFD84D")
    twinkle(58, -50, 22, "#FFE27A")
    twinkle(-50, 52, 16, "#FFE27A")


# ---------------------------------------------------------------- dishes (square)
def oval_plate(rx=170, ry=74, y=0, color=WHITE, line="#F2C89A"):
    contact(0, y + ry * .62, rx * .9, ry * .32, .25)
    clay(ellipse(0, y, rx, ry), color, depth=18, shine=.3)
    clay(ellipse(0, y - 2, rx * .72, ry * .68), dk(color, .04) if color != WHITE else "#F5F0E9", inv=True, shadow=False, depth=10)
    stroke(ellipse(0, y, rx * .86, ry * .84), line, 4, .6)


def dish_sandwich():
    oval_plate(160, 70, 20)
    with at(-52, -24, s=1.75):
        food.sandwich_body()
    with at(50, 6, s=1.9):
        food.sandwich_body()
    with at(64, -102, s=1.9):
        clay(rrect(-1.5, -16, 3, 40, 1.5), "#F3E2C4", depth=1)
        clay(rpoly([(1.5, -16), (18, -10), (1.5, -4)], 2.5), "#4FA3E0", depth=1.5)


def dish_fruit_skewer():
    oval_plate(170, 80, 30)
    for x, y in ((-6, -20), (10, 44)):
        with at(x, y, 66, s=.64):
            food.fruit_skewer(detail=False)


def dish_danbing():
    oval_plate(170, 76, 10)
    with at(0, -12, s=.72):
        food.danbing_pieces()
    sauce = "M -136 -34 C -104 -70 -80 10 -46 -24 C -12 -58 10 10 46 -24 C 80 -58 104 10 136 -30"
    stroke(parse(sauce), "#5A3320", 8, .9)
    stroke(parse(sauce), "#A0643C", 2.6, .8, dx=-1.5, dy=-2)
    for i, (x, y) in enumerate(((-110, -12), (-64, -44), (-16, -8), (28, -42), (76, -10), (118, -40), (-36, 18), (58, 16))):
        with at(x, y, i * 40, s=.55):
            clay(ellipse(0, 0, 11, 9.5), food.GREEN, depth=2.5)
            clay(ellipse(0, 0, 6, 5), "#D7F0B8", inv=True, shadow=False)


def dish_milk_tea():
    food.milk_tea()


def dish_dumplings():
    oval_plate(170, 84, color="#BFE0F2", line="#FFFFFF")
    for row, y in enumerate((-26, 20)):
        for i in range(3):
            x = (i - 1) * 96 + (12 if row else -12)
            with at(x, y, s=.52, sy=.44):
                food.dumpling_body(.6)
    with at(120, -64, -58, s=.62):
        tools.chopsticks()


def main():
    items = [("coin", coin), ("star", star), ("recipe_book", recipe_book), ("check", check), ("hands_wash", hands_wash),
             ("adult_help", adult_hand), ("fire", fire), ("heart", heart), ("speech", speech), ("arrow_flip", arrow_flip),
             ("hand_hint", hand_hint), ("sparkle", sparkle)]
    for name, fn in items:
        begin()
        fn()
        done(f"ui/{name}.svg")
    for name, fn in (("sandwich", dish_sandwich), ("fruit_skewer", dish_fruit_skewer), ("danbing", dish_danbing),
                     ("milk_tea", dish_milk_tea), ("dumplings", dish_dumplings)):
        begin()
        fn()
        kit.PG.marks = {}
        done(f"dishes/{name}.svg", square=True)
    (ART / "ui" / "anchors.json").write_text(json.dumps(ANCH, indent=2, ensure_ascii=False) + "\n")
    print("ui:", len(list((ART / "ui").glob("*.svg"))), "dishes:", len(list((ART / "dishes").glob("*.svg"))))


if __name__ == "__main__":
    main()

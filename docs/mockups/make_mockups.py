"""Design-stage sketches for the cooking game (小廚師).

    python3 make_mockups.py        # writes docs/mockups/*.png (needs Node.js and Playwright)

Everything is drawn here as SVG shapes (no outside pictures), then render.js turns
each page into a PNG with Playwright's Chromium:

    0_畫風選擇.png   the same tomato, egg pan and bear chef in three styles
    1..6_*.png       six phone screens (390x844, at 2x) in style A, clay
    contact_sheet.png  the six screens in one row

The clay look comes from one SVG filter (blurred shape -> lighting -> soft shadow,
plus a little noise so it reads like plasticine with fingerprints).
The font is jf open-huninn from the sibling 字母寵物 checkout, if it is there.
"""
import math
import re
import pathlib
import random
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
FONT = HERE.parents[2] / "app_kids_paint_for_learning_writing" / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"
W, H = 390, 844

# ---------------------------------------------------------------- colours
INK = "#5A3A26"        # warm dark brown for words
SOFT = "#9A7A62"
CREAM = "#FFF6EA"
TOMATO = "#E9483B"
LEAF = "#5CB25C"
STEM = "#3F8D45"
CRUST = "#D99A55"
CRUMB = "#F8DFAF"
CHEESE = "#FFCC3D"
BEAR = "#B67B4E"
BEAR_LT = "#F0D0A4"
BEAR_EAR = "#E9B387"
NOSE = "#3B2418"
BLUSH = "#FF9C9C"
WOOD = "#DDA86B"
GOLD = "#F2B43A"
SILVER = "#C9CED6"
GREEN = "#5DBB63"
ORANGE = "#FF8A3D"
SKIN = "#FFD2A8"
CARROT = "#FF8C2B"
PAN = "#4F555E"


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#2A140A", t)


# ---------------------------------------------------------------- defs registry
class Defs:
    def __init__(self):
        self.d = {}
        self.n = 0

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def uid(self, p="u"):
        self.n += 1
        return f"{p}{self.n}"

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>"


D = Defs()

# clay filter sizes: blur radius (user units) of the "puffiness"
CLAY = {"xs": 1.4, "s": 2.8, "m": 5.5, "l": 9, "xl": 13}


def _turn(px, py, rot):
    """Rotate a point given in % around the middle (50%, 50%) by -rot degrees."""
    a = math.radians(-rot)
    dx, dy = px - 50, py - 50
    return 50 + dx * math.cos(a) - dy * math.sin(a), 50 + dx * math.sin(a) + dy * math.cos(a)


def cg(color, inv=False, rot=0):
    """Radial gradient for a clay piece: light top-left, a little darker bottom-right (on screen, whatever the rotation)."""
    k = ("cgi-" if inv else "cg-") + color[1:] + (f"_r{rot}" if rot else "")
    a, b = (lt(color, .2), dk(color, .1)) if not inv else (dk(color, .12), lt(color, .1))
    cx, cy = _turn(42, 38, rot)
    fx, fy = _turn(34, 28, rot)
    D.add(k, f'<radialGradient id="{k}" cx="{cx:.0f}%" cy="{cy:.0f}%" r="70%" fx="{fx:.0f}%" fy="{fy:.0f}%">'
             f'<stop offset="0" stop-color="{a}"/><stop offset=".58" stop-color="{color}"/><stop offset="1" stop-color="{b}"/></radialGradient>')
    return f"url(#{k})"


def cf(size="m", shadow=True, wide=False, rot=0):
    """The clay filter: bevel from the blurred outline, soft matte light, tiny bumpy noise, soft shadow.
    rot: how much the piece is turned, so the light still comes from the top left of the screen."""
    b = CLAY[size]
    k = f"cf-{size}-{int(shadow)}{int(wide)}" + (f"_r{rot}" if rot else "")
    az = 225 - rot
    ca, sa = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))
    sdx, sdy = b * .3 * ca - b * .75 * sa, b * .3 * sa + b * .75 * ca
    nz = {"xs": 0, "s": .012, "m": .018, "l": .016, "xl": .011}[size]
    nf = min(.09, .62 / b)
    bump = (f'<feTurbulence type="fractalNoise" baseFrequency="{nf:.3f}" numOctaves="2" seed="4" result="n"/>'
            f'<feComposite in="b0" in2="n" operator="arithmetic" k2="0.86" k3="{nz}" result="b"/>') if nz else '<feOffset in="b0" result="b"/>'
    sh = (f'<feGaussianBlur in="SourceAlpha" stdDeviation="{b * .75:.2f}"/><feOffset dx="{sdx:.2f}" dy="{sdy:.2f}" result="sb"/>'
          '<feFlood flood-color="#4A2A14" flood-opacity=".26"/><feComposite in2="sb" operator="in" result="sh"/>'
          '<feMerge><feMergeNode in="sh"/><feMergeNode in="obj"/></feMerge>') if shadow else ''
    reg = 'x="-60%" y="-80%" width="220%" height="260%"' if wide else 'x="-25%" y="-30%" width="150%" height="170%"'
    ss = b * 2.2
    D.add(k, f'<filter id="{k}" {reg} color-interpolation-filters="sRGB">'
             f'<feGaussianBlur in="SourceAlpha" stdDeviation="{b}" result="b0"/>{bump}'
             f'<feDiffuseLighting in="b" surfaceScale="{ss:.2f}" diffuseConstant="1" lighting-color="#fff" result="d0"><feDistantLight azimuth="{az}" elevation="50"/></feDiffuseLighting>'
             '<feGaussianBlur in="d0" stdDeviation=".7" result="d"/>'
             '<feComposite in="SourceGraphic" in2="d" operator="arithmetic" k1="0.62" k2="0.53" result="lit"/>'
             f'<feSpecularLighting in="b" surfaceScale="{ss:.2f}" specularConstant=".35" specularExponent="14" lighting-color="#fff" result="s0"><feDistantLight azimuth="{az}" elevation="50"/></feSpecularLighting>'
             '<feGaussianBlur in="s0" stdDeviation=".7" result="s1"/>'
             '<feComposite in="s1" in2="SourceAlpha" operator="in" result="s2"/>'
             '<feComposite in="lit" in2="s2" operator="arithmetic" k2="1" k3=".6" result="l2"/>'
             f'<feComposite in="l2" in2="SourceAlpha" operator="in" result="obj"/>{sh}</filter>')
    return f"url(#{k})"


def blur(sd):
    k = f"bl{str(sd).replace('.', '_')}"
    D.add(k, f'<filter id="{k}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f"url(#{k})"


def cl(tag, color, attrs, size="m", shadow=True, inv=False, wide=False):
    """One clay piece."""
    return f'<{tag} {attrs} fill="{cg(color, inv)}" filter="{cf(size, shadow, wide)}"/>'


def clg(inner, size="m", shadow=True, wide=False, extra=""):
    """Several shapes that read as one clay piece."""
    return f'<g filter="{cf(size, shadow, wide)}" {extra}>{inner}</g>'


def cw(d, color, width, size="s", shadow=True, box=None):
    """A rolled clay 'worm' along a path (mouths, arrows, handles)."""
    pad = f'<rect x="{box[0]}" y="{box[1]}" width="{box[2]}" height="{box[3]}" fill="none"/>' if box else ""
    return (f'<g filter="{cf(size, shadow, wide=box is None)}">{pad}<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>')


def hl(cx, cy, rx, ry, rot=0, op=.55):
    """Small soft highlight."""
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" opacity="{op}" '
            f'filter="{blur(round(max(.8, min(rx, ry) * .45), 1))}" transform="rotate({rot} {cx} {cy})"/>')


def dent(cx, cy, r, rot=0, op=1.0):
    """A shallow thumbprint: darker upper-left rim, lighter lower-right, a few faint ridges."""
    D.add("dentg", '<radialGradient id="dentg" cx="50%" cy="50%" r="50%" fx="64%" fy="68%">'
                   '<stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>'
                   '<stop offset=".86" stop-color="#2A140A" stop-opacity=".16"/><stop offset="1" stop-color="#2A140A" stop-opacity="0"/></radialGradient>')
    ridges = "".join(f'<ellipse cx="{cx + 1}" cy="{cy + 1}" rx="{r * f:.1f}" ry="{r * f * .8:.1f}" fill="none" stroke="#fff" stroke-opacity=".10" stroke-width="{max(.5, r * .06):.2f}"/>'
                     for f in (.35, .55, .75))
    return (f'<g opacity="{op}" transform="rotate({rot} {cx} {cy})"><ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * .8:.1f}" fill="url(#dentg)"/>{ridges}</g>')


_REF = re.compile(r"url\(#(cf-([a-z]+)-(\d)(\d)|cg(i?)-([0-9A-F]{6}))(?:_r(-?\d+))?\)")


def _respin(m, rot):
    ang = (int(m.group(7) or 0) + rot + 180) % 360 - 180
    if m.group(2):
        return cf(m.group(2), m.group(3) == "1", m.group(4) == "1", ang)
    return cg("#" + m.group(6), m.group(5) == "i", ang)


def G(inner, x=0, y=0, s=1, rot=0, extra=""):
    if rot:
        inner = _REF.sub(lambda m: _respin(m, round(rot)), inner)
    return f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" {extra}>{inner}</g>'


def tx(x, y, s, size=16, color=INK, anchor="middle", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-family="Huninn, \'WenQuanYi Zen Hei\', sans-serif" {extra}>{s}</text>')


def ctx(x, y, s, size=16, color="#fff", anchor="middle"):
    """Puffy clay letters."""
    return tx(x, y, s, size, color, anchor, f'filter="{cf("xs", True, wide=True)}"')


# ---------------------------------------------------------------- paper and flat styles (sheet only)
def pf(seed=1):
    k = f"pf{seed}"
    D.add(k, f'<filter id="{k}" x="-20%" y="-20%" width="145%" height="150%" color-interpolation-filters="sRGB">'
             f'<feTurbulence type="fractalNoise" baseFrequency="0.08" numOctaves="3" seed="{seed}" result="t"/>'
             '<feDisplacementMap in="SourceGraphic" in2="t" scale="5" xChannelSelector="R" yChannelSelector="G" result="torn"/>'
             f'<feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="{seed + 20}" result="em"/>'
             '<feColorMatrix in="em" type="matrix" values="0 0 0 0 1  0 0 0 0 0.99  0 0 0 0 0.95  0 0 0 7 -3.4" result="emask"/>'
             '<feMorphology in="torn" operator="dilate" radius="1.3" result="dil"/>'
             '<feComposite in="emask" in2="dil" operator="in" result="edge"/>'
             '<feGaussianBlur in="dil" stdDeviation="1.4"/><feOffset dx="2.5" dy="3.5" result="so"/>'
             '<feFlood flood-color="#3B2A1A" flood-opacity=".33"/><feComposite in2="so" operator="in" result="shd"/>'
             f'<feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="1" seed="{seed + 40}" result="g"/>'
             '<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.25  0 0 0 0 0.16  0 0 0 0 0.08  0 0 0 3 -1.95" result="gd"/>'
             '<feComposite in="gd" in2="torn" operator="in" result="g1"/>'
             '<feColorMatrix in="g" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -3 1.05" result="gl"/>'
             '<feComposite in="gl" in2="torn" operator="in" result="g2"/>'
             '<feMerge><feMergeNode in="shd"/><feMergeNode in="edge"/><feMergeNode in="torn"/><feMergeNode in="g1"/><feMergeNode in="g2"/></feMerge>'
             '</filter>')
    return f"url(#{k})"


_seed = [0]


def sh(st, tag, color, attrs, size="m", shadow=True, inv=False):
    """One piece in a given style: clay / paper / flat."""
    if st == "clay":
        return cl(tag, color, attrs, size, shadow, inv)
    if st == "paper":
        _seed[0] = _seed[0] % 7 + 1
        return f'<{tag} {attrs} fill="{color}" filter="{pf(_seed[0])}"/>'
    return f'<{tag} {attrs} fill="{color}"/>'


def flat_shade(tag, attrs, color, dx=5, dy=6, t=.14):
    """Flat style: a darker crescent on the lower right made from two copies of the shape."""
    cp = D.uid("cp")
    D.add(cp, f'<clipPath id="{cp}"><{tag} {attrs}/></clipPath>')
    return (f'<{tag} {attrs} fill="{dk(color, t)}"/>'
            f'<g clip-path="url(#{cp})"><g transform="translate({-dx} {-dy})"><{tag} {attrs} fill="{color}"/></g></g>')


def star_path(R, r, n=5, cx=0, cy=0, rot=-90):
    pts = []
    for i in range(n * 2):
        a = math.radians(rot + i * 180 / n)
        rr = R if i % 2 == 0 else r
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


def heart_path(s=1.0):
    return (f"M 0 {12 * s} C {-20 * s} {-2 * s} {-22 * s} {-18 * s} {-10 * s} {-22 * s} C {-4 * s} {-24 * s} 0 {-18 * s} 0 {-14 * s} "
            f"C 0 {-18 * s} {4 * s} {-24 * s} {10 * s} {-22 * s} C {22 * s} {-18 * s} {20 * s} {-2 * s} 0 {12 * s} Z")


# ---------------------------------------------------------------- the three comparison things
TOMATO_BODY = "M 0 -36 C 22 -44 50 -30 50 0 C 50 30 28 46 0 46 C -28 46 -50 30 -50 0 C -50 -30 -22 -44 0 -36 Z"


def tomato(st="clay"):
    o = []
    if st == "flat":
        o.append(flat_shade("circle", 'cx="0" cy="4" r="46"', "#FF4B3E", 7, 8))
        o.append('<circle cx="-20" cy="-14" r="7" fill="#fff" opacity=".9"/><circle cx="-29" cy="-2" r="3.5" fill="#fff" opacity=".9"/>')
        o.append(f'<path d="{star_path(20, 8, cy=-38)}" fill="#22C55E"/>')
        o.append('<rect x="-3" y="-54" width="6" height="16" rx="3" fill="#15A04A"/>')
        return "".join(o)
    o.append(sh(st, "path", TOMATO, f'd="{TOMATO_BODY}"', "l"))
    if st == "clay":
        o.append(f'<path d="M -8 -32 Q -24 -12 -20 14 M 8 -32 Q 24 -12 20 14" stroke="{dk(TOMATO, .25)}" stroke-width="3" fill="none" opacity=".35" filter="{blur(1.5)}"/>')
        o.append(hl(-26, -12, 10, 6, -40, .5))
        o.append(dent(22, 20, 9, 20))
        leaves = "".join(f'<ellipse cx="{math.cos(math.radians(a)) * 11:.1f}" cy="{-35 + math.sin(math.radians(a)) * 6:.1f}" rx="12.5" ry="5.2" '
                         f'fill="{cg(LEAF)}" transform="rotate({a} {math.cos(math.radians(a)) * 11:.1f} {-35 + math.sin(math.radians(a)) * 6:.1f})"/>'
                         for a in (-54, 18, 90, 162, 234))
        o.append(clg(leaves + f'<circle cx="0" cy="-36" r="6" fill="{cg(LEAF)}"/>', "s"))
        o.append(cl("rect", STEM, 'x="-3.5" y="-52" width="7" height="15" rx="3.5"', "xs"))
    else:  # paper
        o.append(sh(st, "ellipse", lt(TOMATO, .35), 'cx="-24" cy="-12" rx="11" ry="7" transform="rotate(-40 -24 -12)"'))
        o.append(sh(st, "path", LEAF, f'd="{star_path(21, 7, cy=-36)}"'))
        o.append(sh(st, "rect", STEM, 'x="-3" y="-54" width="6" height="16"'))
    return "".join(o)


EGG_WHITE = "M -30 -6 C -34 -26 -12 -34 4 -30 C 22 -34 36 -18 32 0 C 38 18 22 34 2 31 C -16 36 -36 22 -30 -6 Z"


def egg_pan(st="clay"):
    o = []
    if st == "flat":
        o.append('<rect x="44" y="-9" width="66" height="18" rx="9" fill="#F59E0B" transform="rotate(35)"/>')
        o.append('<circle r="52" fill="#334155"/><circle r="43" fill="#1E293B"/>')
        o.append('<circle cx="-1" cy="1" r="32" fill="#FFFFFF"/><circle cx="5" cy="-3" r="14" fill="#FFB800"/><circle cx="1" cy="-7" r="4" fill="#fff"/>')
        return "".join(o)
    o.append(sh(st, "rect", "#A8703F", 'x="46" y="-9" width="64" height="18" rx="9" transform="rotate(35)"', "s"))
    o.append(sh(st, "rect", "#8A9099", 'x="38" y="-6" width="16" height="12" rx="4" transform="rotate(35)"', "xs"))
    o.append(sh(st, "circle", PAN, 'r="52"', "m"))
    o.append(sh(st, "circle", dk(PAN, .15), 'r="42"', "s", shadow=False, inv=True))
    o.append(sh(st, "path", "#FFF8EC", f'd="{EGG_WHITE}"', "m"))
    o.append(sh(st, "circle", "#FFB21F", 'cx="5" cy="-3" r="14"', "s"))
    if st == "clay":
        o.append(hl(-30, -32, 9, 4, -40, .25))
        o.append(hl(0, -9, 4.5, 3, -30, .7))
        o.append(dent(-12, 14, 7, 0, .8))
    return "".join(o)


def face_bits(st, eyes_y=-4, eye_dx=25, mouth_y=30, nose=True, cheeks=True, cheek_dx=42, cheek_y=18, mood="happy"):
    o = []
    for sx in (-1, 1):
        if mood == "joy":   # closed happy eyes ^ ^
            o.append(cw(f"M {sx * eye_dx - 7} {eyes_y + 3} Q {sx * eye_dx} {eyes_y - 6} {sx * eye_dx + 7} {eyes_y + 3}", NOSE, 4, "xs",
                        box=(sx * eye_dx - 12, eyes_y - 10, 24, 18)) if st == "clay" else
                     f'<path d="M {sx * eye_dx - 7} {eyes_y + 3} Q {sx * eye_dx} {eyes_y - 6} {sx * eye_dx + 7} {eyes_y + 3}" stroke="{NOSE}" stroke-width="4" fill="none" stroke-linecap="round"/>')
        else:
            o.append(sh(st, "ellipse", "#2B1B12", f'cx="{sx * eye_dx}" cy="{eyes_y}" rx="6.5" ry="8"', "xs"))
            o.append(f'<circle cx="{sx * eye_dx - 2}" cy="{eyes_y - 3}" r="2.2" fill="#fff"/>')
        if cheeks:
            if st == "clay":
                o.append(cl("ellipse", BLUSH, f'cx="{sx * cheek_dx}" cy="{cheek_y}" rx="10" ry="6.5"', "xs", shadow=False))
            elif st == "paper":
                o.append(sh(st, "ellipse", BLUSH, f'cx="{sx * cheek_dx}" cy="{cheek_y}" rx="10" ry="6.5"'))
            else:
                o.append(f'<ellipse cx="{sx * cheek_dx}" cy="{cheek_y}" rx="10" ry="6.5" fill="#FF8FA3"/>')
    d = f"M -10 {mouth_y} Q -5 {mouth_y + 7} 0 {mouth_y} Q 5 {mouth_y + 7} 10 {mouth_y}"
    if st == "clay":
        o.append(cw(d, NOSE, 3.4, "xs", box=(-14, mouth_y - 5, 28, 16)))
    elif st == "paper":
        o.append(f'<path d="{d}" stroke="{NOSE}" stroke-width="3.6" fill="none" stroke-linecap="round" filter="{pf(3)}"/>')
    else:
        o.append(f'<path d="{d}" stroke="{NOSE}" stroke-width="3.6" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def chef_hat(st="clay", y=-62):
    o = []
    white = "#FFFDF8"
    if st == "flat":
        for cx, cy, r in ((-32, y - 12, 24), (32, y - 12, 24), (0, y - 26, 30)):
            o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff"/>')
        o.append(f'<rect x="-46" y="{y}" width="92" height="26" rx="8" fill="#E2E8F0"/>')
        return "".join(o)
    if st == "clay":
        puffs = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{cg(white)}"/>' for cx, cy, r in ((-32, y - 12, 24), (32, y - 12, 24), (0, y - 26, 30)))
        o.append(clg(puffs, "m"))
        o.append(cl("rect", "#F4EEE6", f'x="-46" y="{y}" width="92" height="26" rx="12"', "s"))
        o.append(hl(-10, y - 40, 9, 5, -30, .6))
        o.append(dent(26, y - 16, 8, 30, .7))
    else:
        for cx, cy, r in ((-32, y - 12, 24), (32, y - 12, 24), (0, y - 26, 30)):
            o.append(sh(st, "circle", white, f'cx="{cx}" cy="{cy}" r="{r}"'))
        o.append(sh(st, "rect", "#EFE8DC", f'x="-46" y="{y}" width="92" height="26"'))
    return "".join(o)


def bear(st="clay", hat=False, mood="happy"):
    """Bear head, about -70..70 wide; with the chef hat it reaches up to about -125."""
    o = []
    if st == "flat":
        for sx in (-1, 1):
            o.append(f'<circle cx="{sx * 50}" cy="-30" r="20" fill="#B45309"/><circle cx="{sx * 50}" cy="-30" r="10" fill="#FDBA74"/>')
        o.append(flat_shade("ellipse", 'cx="0" cy="4" rx="64" ry="56"', "#D97706", 8, 8, .12))
        o.append('<ellipse cx="0" cy="24" rx="30" ry="21" fill="#FDE6C4"/><ellipse cx="0" cy="13" rx="10" ry="7.5" fill="#3B2418"/>')
        o.append(face_bits(st, mood=mood))
        if hat:
            o.append(chef_hat(st))
        return "".join(o)
    for sx in (-1, 1):
        o.append(sh(st, "circle", BEAR, f'cx="{sx * 50}" cy="-30" r="20"', "m"))
        o.append(sh(st, "circle", BEAR_EAR, f'cx="{sx * 50}" cy="-30" r="10"', "s", shadow=False, inv=True))
    o.append(sh(st, "ellipse", BEAR, 'cx="0" cy="4" rx="64" ry="56"', "l"))
    if st == "clay":
        o.append(hl(-34, -22, 13, 7, -35, .35))
        o.append(dent(36, -16, 9, 25, .9))
        o.append(dent(-40, 34, 7, -10, .7))
    o.append(sh(st, "ellipse", BEAR_LT, 'cx="0" cy="24" rx="30" ry="21"', "m"))
    o.append(sh(st, "ellipse", NOSE, 'cx="0" cy="13" rx="10" ry="7.5"', "s"))
    if st == "clay":
        o.append(hl(-3, 10, 3.5, 2, 0, .7))
    o.append(face_bits(st, mood=mood))
    if hat:
        o.append(chef_hat(st))
    return "".join(o)


# ---------------------------------------------------------------- more clay things (screens)
def rabbit(mood="joy"):
    o = []
    for sx in (-1, 1):
        o.append(cl("ellipse", "#FFF4EA", f'cx="{sx * 22}" cy="-78" rx="15" ry="42" transform="rotate({sx * 10} {sx * 22} -78)"', "m"))
        o.append(cl("ellipse", "#FFB9C6", f'cx="{sx * 22}" cy="-74" rx="7" ry="28" transform="rotate({sx * 10} {sx * 22} -74)"', "s", shadow=False, inv=True))
    o.append(cl("ellipse", "#FFF4EA", 'cx="0" cy="6" rx="60" ry="52"', "l"))
    o.append(hl(-30, -20, 12, 7, -35, .5))
    o.append(dent(34, -14, 8, 20, .8))
    o.append(cl("ellipse", "#FFFFFF", 'cx="0" cy="24" rx="24" ry="16"', "m"))
    o.append(cl("path", "#FF8FA6", 'd="M -7 12 Q 0 8 7 12 Q 4 19 0 20 Q -4 19 -7 12 Z"', "xs"))
    o.append(face_bits("clay", eyes_y=-4, eye_dx=24, mouth_y=24, cheek_dx=40, cheek_y=16, mood=mood))
    o.append(cl("rect", "#FFFFFF", 'x="-6" y="30" width="12" height="9" rx="3"', "xs"))
    return "".join(o)


def pig(mood="happy"):
    o = []
    for sx in (-1, 1):
        o.append(cl("path", "#FFA9BA", f'd="M {sx * 26} -40 Q {sx * 56} -70 {sx * 60} -36 Q {sx * 58} -20 {sx * 42} -22 Z"', "m"))
    o.append(cl("ellipse", "#FFB7C6", 'cx="0" cy="6" rx="62" ry="54"', "l"))
    o.append(hl(-32, -18, 12, 7, -35, .45))
    # bandana
    o.append(cl("path", "#4FB286", 'd="M -58 -14 C -56 -56 56 -56 58 -14 C 30 -26 -30 -26 -58 -14 Z"', "m"))
    o.append("".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#fff" opacity=".9"/>' for x, y in ((-30, -34), (-8, -42), (14, -40), (36, -30), (-44, -22), (0, -28), (24, -26))))
    o.append(cl("ellipse", "#4FB286", 'cx="54" cy="-10" rx="10" ry="7" transform="rotate(30 54 -10)"', "s"))
    o.append(cl("ellipse", "#4FB286", 'cx="64" cy="-2" rx="9" ry="5" transform="rotate(70 64 -2)"', "s"))
    o.append(cl("ellipse", "#FF94AA", 'cx="0" cy="22" rx="21" ry="15"', "m"))
    o.append(cl("ellipse", "#C9566E", 'cx="-7" cy="22" rx="3.5" ry="5"', "xs", shadow=False, inv=True))
    o.append(cl("ellipse", "#C9566E", 'cx="7" cy="22" rx="3.5" ry="5"', "xs", shadow=False, inv=True))
    o.append(face_bits("clay", eyes_y=0, eye_dx=27, mouth_y=42, cheek_dx=44, cheek_y=24, mood=mood))
    return "".join(o)


def child_avatar():
    o = [cl("circle", "#FFD66B", 'r="30"', "m")]
    inner = []
    inner.append(cl("circle", SKIN, 'cx="0" cy="6" r="19"', "s"))
    inner.append(cl("path", "#4A2E22", 'd="M -20 6 C -22 -14 22 -14 20 6 C 14 -2 4 -4 -2 -6 C -8 -2 -14 0 -20 6 Z"', "s"))
    inner.append(cl("ellipse", "#2B1B12", 'cx="-7" cy="7" rx="2.6" ry="3.2"', "xs", shadow=False))
    inner.append(cl("ellipse", "#2B1B12", 'cx="7" cy="7" rx="2.6" ry="3.2"', "xs", shadow=False))
    inner.append(cl("ellipse", BLUSH, 'cx="-12" cy="14" rx="4" ry="2.6"', "xs", shadow=False))
    inner.append(cl("ellipse", BLUSH, 'cx="12" cy="14" rx="4" ry="2.6"', "xs", shadow=False))
    inner.append(f'<path d="M -4 15 Q 0 19 4 15" stroke="{NOSE}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    inner.append(G(chef_hat("clay"), 0, -1, .3))
    o.append("".join(inner))
    return "".join(o)


def coin(r=14, color=GOLD, label="", fs=None):
    o = [cl("circle", color, f'r="{r}"', "s" if r < 18 else "m")]
    o.append(f'<circle r="{r * .74:.1f}" fill="none" stroke="{dk(color, .25)}" stroke-opacity=".35" stroke-width="{max(1, r * .08):.1f}"/>')
    o.append(f'<circle r="{r * .74:.1f}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="{max(.6, r * .05):.1f}" transform="translate(.8 .8)"/>')
    if label:
        o.append(tx(0, r * .36, label, fs or r * (1.0 if len(label) < 2 else .82), dk(color, .45)))
    else:
        o.append(f'<path d="{star_path(r * .42, r * .2)}" fill="{dk(color, .2)}" opacity=".45"/>')
    o.append(hl(-r * .45, -r * .5, r * .28, r * .16, -40, .7))
    return "".join(o)


def star_icon(r=14, color="#FFC83A"):
    return (f'<path d="{star_path(r, r * .5)}" fill="{cg(color)}" stroke="{color}" stroke-width="{r * .3:.1f}" stroke-linejoin="round" filter="{cf("s")}"/>'
            + hl(-r * .3, -r * .35, r * .22, r * .14, -30, .7))


def heart(s=1.0, color="#FF6F91", size="m"):
    return cl("path", color, f'd="{heart_path(s)}"', size) + hl(-9 * s, -14 * s, 4 * s, 2.5 * s, -35, .7)


def chip(x, y, w, h, inner, color=CREAM):
    return cl("rect", color, f'x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}"', "m") + inner


def back_btn(x=34, y=40):
    return (cl("circle", CREAM, f'cx="{x}" cy="{y}" r="22"', "m")
            + cw(f"M {x + 4} {y - 9} L {x - 5} {y} L {x + 4} {y + 9}", INK, 4.5, "xs", box=(x - 10, y - 13, 20, 26)))


def title_chip(text, cx=195, y=40, w=None, icon=""):
    w = w or len(text) * 22 + 44 + (34 if icon else 0)
    x0 = cx - w / 2
    tx0 = cx + (16 if icon else 0)
    return (cl("rect", CREAM, f'x="{x0}" y="{y - 22}" width="{w}" height="44" rx="22"', "m")
            + (G(icon, x0 + 30, y) if icon else "") + tx(tx0, y + 8, text, 22))


def big_btn(cx, cy, w, h, color, label, icon="play"):
    x0, y0 = cx - w / 2, cy - h / 2
    o = [cl("rect", dk(color, .22), f'x="{x0}" y="{y0 + 7}" width="{w}" height="{h}" rx="{h / 2}"', "m"),
         cl("rect", color, f'x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{h / 2}"', "l", shadow=False),
         hl(x0 + 40, y0 + 14, 22, 5, 0, .45)]
    if icon == "play":
        o.append(cl("path", "#FFFFFF", f'd="M {cx - 62} {cy - 14} L {cx - 62} {cy + 14} L {cx - 38} {cy} Z" stroke="#FFFFFF" stroke-width="6" stroke-linejoin="round"', "xs"))
        o.append(ctx(cx + 16, cy + 11, label, 32))
    else:
        o.append(ctx(cx, cy + 11, label, 32))
    return "".join(o)


def num_badge(n, r=17, color="#FF8A3D"):
    return cl("circle", color, f'r="{r}"', "s") + tx(0, r * .42, str(n), r * 1.2, "#fff")


def check_badge(r=16):
    return (cl("circle", GREEN, f'r="{r}"', "s")
            + cw(f"M {-r * .45:.1f} {r * .02:.1f} L {-r * .1:.1f} {r * .36:.1f} L {r * .48:.1f} {-r * .32:.1f}", "#FFFFFF", r * .26, "xs",
                 box=(-r, -r, 2 * r, 2 * r)))


def book_icon():
    o = [cl("rect", "#FFF6E6", 'x="-15" y="-19" width="34" height="40" rx="5"', "s"),
         cl("rect", "#E8573F", 'x="-19" y="-21" width="32" height="40" rx="6"', "s"),
         cl("rect", "#FFC83A", 'x="4" y="-21" width="6" height="22" rx="2"', "xs", shadow=False),
         G(chef_hat("clay"), -4, 8, .2)]
    return "".join(o)


def bread_slice():
    crust = TOAST
    return (cl("path", CRUST, f'd="{crust}"', "m")
            + cl("path", CRUMB, f'd="{crust}" transform="translate(0 1.5) scale(.78)"', "s", shadow=False)
            + hl(-10, -16, 6, 3, -20, .6))


def cheese_slice():
    return (cl("rect", CHEESE, 'x="-22" y="-22" width="44" height="44" rx="6" transform="rotate(-6)"', "m")
            + cl("circle", dk(CHEESE, .1), 'cx="-8" cy="-6" r="5"', "xs", shadow=False, inv=True)
            + cl("circle", dk(CHEESE, .1), 'cx="9" cy="8" r="6.5"', "xs", shadow=False, inv=True)
            + cl("circle", dk(CHEESE, .1), 'cx="10" cy="-11" r="3.5"', "xs", shadow=False, inv=True)
            + hl(-12, -15, 5, 3, -20, .6))


def tomato_slice(r=20):
    s = r / 20
    o = [cl("circle", TOMATO, f'r="{r}"', "m" if r > 24 else "s"),
         cl("circle", "#F7604F", f'r="{15.5 * s:.1f}"', "xs", shadow=False)]
    for k in range(5):
        a = math.radians(k * 72 - 90)
        cx, cy = math.cos(a) * 9 * s, math.sin(a) * 9 * s
        o.append(cl("ellipse", "#FFC09F", f'cx="{cx:.1f}" cy="{cy:.1f}" rx="{3.6 * s:.1f}" ry="{5.6 * s:.1f}" transform="rotate({k * 72} {cx:.1f} {cy:.1f})"', "xs", shadow=False))
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{1.1 * s:.1f}" fill="#F4D35E"/>')
    o.append(cl("circle", "#FF8070", f'r="{3.5 * s:.1f}"', "xs", shadow=False))
    o.append(hl(-r * .5, -r * .55, r * .25, r * .14, -40, .6))
    return "".join(o)


TOAST = ("M -22 24 L -22 -6 C -31 -10 -31 -29 -14 -28 C -8 -35 8 -35 14 -28 C 31 -29 31 -10 22 -6 L 22 24 "
         "Q 22 28 18 28 L -18 28 Q -22 28 -22 24 Z")


def sandwich(flag=True):
    """Toast sandwich seen from above: cheese corners and 3 tomato slices peek out. About 76 wide, 80 tall."""
    o = [cl("path", dk(CRUST, .08), f'd="{TOAST}" transform="translate(5 7) rotate(5)"', "m")]
    for x, y in ((-25, 18), (27, 22), (2, 32)):
        o.append(G(tomato_slice(13), x, y))
    o.append(cl("rect", CHEESE, 'x="-27" y="-24" width="54" height="50" rx="5" transform="rotate(14)"', "m"))
    o.append(cl("path", CRUST, f'd="{TOAST}"', "m"))
    o.append(cl("path", CRUMB, f'd="{TOAST}" transform="translate(0 1.5) scale(.78)"', "s", shadow=False))
    o.append(hl(-10, -17, 7, 3, -20, .6))
    o.append(dent(8, 10, 5, 0, .8))
    if flag:
        o.append(cl("rect", "#F3E2C4", 'x="-1.5" y="-46" width="3" height="40" rx="1.5"', "xs"))
        o.append(cl("path", "#4FA3E0", 'd="M 1.5 -46 L 18 -41 L 1.5 -35 Z" stroke="#4FA3E0" stroke-width="3" stroke-linejoin="round"', "xs"))
    return "".join(o)


def carrot(leaves=True):
    o = []
    if leaves:
        for a, x in ((-25, -5), (0, 0), (25, 5)):
            o.append(cl("ellipse", LEAF, f'cx="{x}" cy="-36" rx="4.5" ry="12" transform="rotate({a} {x} -28)"', "xs"))
    o.append(cl("path", CARROT, 'd="M -12 -26 C -15 -6 -6 18 0 32 C 6 18 15 -6 12 -26 Q 0 -32 -12 -26 Z"', "m"))
    o.append(f'<path d="M -9 -10 l 6 1 M 4 2 l 6 -1 M -5 14 l 5 1" stroke="{dk(CARROT, .25)}" stroke-width="1.8" stroke-linecap="round" opacity=".5"/>')
    o.append(hl(-5, -16, 3, 7, 0, .5))
    return "".join(o)


def cabbage():
    o = [cl("circle", "#8CCB5E", 'r="30"', "l")]
    o.append(cl("path", "#A9DC78", 'd="M -26 8 C -30 -22 -4 -30 6 -24 C -10 -14 -14 4 -6 26 C -16 24 -24 18 -26 8 Z"', "s"))
    o.append(cl("path", "#A9DC78", 'd="M 26 6 C 30 -20 10 -30 -2 -26 C 14 -14 16 6 6 26 C 16 24 24 16 26 6 Z"', "s"))
    o.append(cl("circle", "#D4F0A6", 'cx="0" cy="-2" r="13"', "s"))
    o.append(f'<path d="M -16 14 Q -12 0 -16 -12 M 15 14 Q 11 0 15 -12" stroke="#EAF8CF" stroke-width="2" fill="none" opacity=".8" stroke-linecap="round"/>')
    o.append(hl(-12, -18, 6, 3.5, -30, .5))
    return "".join(o)


def egg(color="#F4E2C6"):
    return cl("ellipse", color, 'rx="13" ry="16"', "s") + hl(-4, -7, 3.5, 2.2, -30, .7)


def knife(scale=1.0):
    """Rounded children's knife pointing down; about 22 wide, 120 long (y -60..60)."""
    o = [cl("rect", "#5BBE7A", 'x="-11" y="-62" width="22" height="50" rx="11"', "m"),
         cl("circle", lt("#5BBE7A", .4), 'cx="0" cy="-50" r="4"', "xs", shadow=False, inv=True),
         cl("path", "#D8E8F4", 'd="M -10 -12 L 10 -12 L 12 44 C 12 62 -12 64 -12 44 Z"', "m"),
         f'<path d="M 11 -6 ' + " ".join(f"l -2.4 3.5 l 2.4 3.5" for _ in range(6)) + '" fill="none" stroke="#B9CDDD" stroke-width="1.6" stroke-linejoin="round"/>',
         hl(-4, 14, 2.5, 18, 0, .55)]
    return G("".join(o), s=scale)


def pointer_hand(rot=0, s=1.0):
    """Child's hand with the index finger pointing up (fingertip at 0,0)."""
    o = [cl("rect", "#7EC8F0", 'x="-16" y="44" width="34" height="18" rx="8"', "s"),
         cl("rect", SKIN, 'x="-17" y="12" width="36" height="38" rx="15"', "m"),
         cl("rect", SKIN, 'x="-7" y="-2" width="14" height="34" rx="7"', "s"),
         cl("ellipse", SKIN, 'cx="-18" cy="30" rx="7" ry="11" transform="rotate(-25 -18 30)"', "s"),
         f'<path d="M 9 24 h 8 M 9 33 h 8" stroke="{dk(SKIN, .2)}" stroke-width="1.6" stroke-linecap="round" opacity=".5"/>',
         cl("ellipse", "#FFE9D6", 'cx="0" cy="4" rx="4" ry="4.5"', "xs", shadow=False)]
    return G("".join(o), s=s, rot=rot)


def adult_hand():
    """Open grown-up hand with a sleeve, about 46 wide."""
    o = [cl("rect", "#4F7BD9", 'x="-14" y="18" width="30" height="16" rx="6"', "s")]
    for i, (x, h) in enumerate(((-12, 22), (-4, 27), (4, 26), (12, 21))):
        o.append(cl("rect", "#F2C29B", f'x="{x - 3.6}" y="{-6 - h}" width="7.2" height="{h + 10}" rx="3.6"', "xs"))
    o.append(cl("rect", "#F2C29B", 'x="-15" y="-10" width="31" height="31" rx="10"', "s"))
    o.append(cl("ellipse", "#F2C29B", 'cx="-17" cy="4" rx="5" ry="11" transform="rotate(35 -17 4)"', "xs"))
    return "".join(o)


def wood_grooves(x, y, w, h, n, seed=1, color=WOOD):
    r = random.Random(seed)
    o = []
    for i in range(n):
        yy = y + h * (i + .5) / n + r.uniform(-4, 4)
        x0 = x + r.uniform(0, w * .25)
        x1 = x0 + r.uniform(w * .35, w * .7)
        d = f"M {x0:.0f} {yy:.0f} Q {(x0 + x1) / 2:.0f} {yy + r.uniform(-5, 5):.0f} {x1:.0f} {yy:.0f}"
        o.append(f'<path d="{d}" stroke="{dk(color, .25)}" stroke-width="2" fill="none" stroke-linecap="round" opacity=".28"/>'
                 f'<path d="{d}" stroke="#fff" stroke-width="1.4" fill="none" stroke-linecap="round" opacity=".28" transform="translate(.8 1.6)"/>')
    return "".join(o)


def jar(color, lid):
    return (cl("rect", "#EAF6FB", 'x="-16" y="-20" width="32" height="40" rx="10"', "m")
            + cl("rect", color, 'x="-12" y="-6" width="24" height="23" rx="7"', "s", shadow=False)
            + cl("rect", lid, 'x="-17" y="-28" width="34" height="11" rx="5"', "s")
            + hl(-9, -8, 2.5, 8, 0, .7))


def plant():
    o = []
    for a in (-40, -15, 15, 40, 0):
        o.append(cl("ellipse", LEAF if a else lt(LEAF, .15), f'cx="0" cy="-30" rx="8" ry="20" transform="rotate({a} 0 -10)"', "s"))
    o.append(cl("path", "#E07B52", 'd="M -20 -12 L 20 -12 L 15 18 Q 14 22 10 22 L -10 22 Q -14 22 -15 18 Z"', "m"))
    o.append(cl("rect", "#EB8F66", 'x="-23" y="-16" width="46" height="10" rx="5"', "s"))
    return "".join(o)


def bell():
    return (cl("ellipse", "#9BA3AD", 'cx="0" cy="12" rx="30" ry="7"', "s")
            + cl("path", GOLD, 'd="M -24 10 C -24 -16 24 -16 24 10 Z"', "m")
            + cl("circle", GOLD, 'cx="0" cy="-12" r="4.5"', "xs")
            + hl(-11, -2, 6, 3, -30, .7))


def speech_bubble(x, y, w, h, tail_x, tail_y, color="#FFFFFF", size="l"):
    """Rounded bubble with a tail pointing at (tail_x, tail_y), from whichever side it is on."""
    r = 28
    bx = min(max(tail_x, x + r + 20), x + w - r - 20)
    by = min(max(tail_y, y + r + 12), y + h - r - 12)
    top = f"L {bx - 16} {y} L {tail_x} {tail_y} L {bx + 16} {y} " if tail_y < y and x <= tail_x <= x + w else ""
    bottom = f"L {bx + 18} {y + h} L {tail_x} {tail_y} L {bx - 18} {y + h} " if tail_y > y + h and x <= tail_x <= x + w else ""
    left = f"L {x} {by + 13} L {tail_x} {tail_y} L {x} {by - 13} " if tail_x < x else ""
    right = f"L {x + w} {by - 13} L {tail_x} {tail_y} L {x + w} {by + 13} " if tail_x > x + w else ""
    d = (f"M {x + r} {y} {top}L {x + w - r} {y} Q {x + w} {y} {x + w} {y + r} {right}L {x + w} {y + h - r} Q {x + w} {y + h} {x + w - r} {y + h} "
         f"{bottom}L {x + r} {y + h} Q {x} {y + h} {x} {y + h - r} {left}L {x} {y + r} Q {x} {y} {x + r} {y} Z")
    return f'<path d="{d}" fill="{cg(color)}" stroke="{color}" stroke-width="4" stroke-linejoin="round" filter="{cf(size)}"/>'


def plus(x, y, s=10, color="#F2A65A"):
    return cw(f"M {x - s} {y} H {x + s} M {x} {y - s} V {y + s}", color, 6, "xs", box=(x - s - 4, y - s - 4, 2 * s + 8, 2 * s + 8))


def dots(x, y, n, filled, r=7, gap=22, on=TOMATO, off="#E9D9C8"):
    o = []
    for i in range(n):
        cx = x + (i - (n - 1) / 2) * gap
        o.append(cl("circle", on if i < filled else off, f'cx="{cx}" cy="{y}" r="{r}"', "xs", inv=i >= filled))
    return "".join(o)


# ---------------------------------------------------------------- page wrapper
def page(body, bg, w=W, h=H):
    css = (f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }}"
           f"* {{ margin: 0; padding: 0; }} body {{ width: {w}px; height: {h}px; overflow: hidden; background: {bg}; }}")
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{D.svg()}{body}</svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{svg}</body></html>'


def lin(id_, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    D.add(id_, f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>')
    return f"url(#{id_})"


# ---------------------------------------------------------------- 0 style sheet
def style_sheet():
    SW, SH = 1600, 900
    o = [tx(SW / 2, 62, "畫風選擇", 40, INK), tx(SW / 2, 100, "同樣的番茄、煎蛋、小熊廚師，用三種畫法畫", 20, SOFT)]
    panels = [("A", "黏土風", "像黏土捏出來：圓胖、立體、軟軟的影子", "clay", "#FFE7D2", "#FF8A3D"),
              ("B", "剪紙拼貼風", "像色紙撕下來貼上去：紙邊、紙紋、一層層", "paper", "#F2E6D0", "#4FA3E0"),
              ("C", "扁平明亮風", "乾淨的幾何形狀、顏色鮮明、沒有紋路", "flat", "#E1F3FF", "#22C55E")]
    pw, ph, top = 494, 712, 130
    for i, (letter, name, desc, st, bg, accent) in enumerate(panels):
        x0 = 40 + i * (pw + 19)
        cx = x0 + pw / 2
        if st == "paper":
            D.add("kraft", '<filter id="kraft" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="11" result="n"/>'
                           '<feColorMatrix in="n" type="matrix" values="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .3  0 0 0 1.4 -.78" result="d"/>'
                           '<feComposite in="d" in2="SourceGraphic" operator="in" result="d2"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d2"/></feMerge></filter>')
            o.append(f'<rect x="{x0}" y="{top}" width="{pw}" height="{ph}" rx="28" fill="{bg}" filter="url(#kraft)"/>')
        else:
            o.append(f'<rect x="{x0}" y="{top}" width="{pw}" height="{ph}" rx="28" fill="{bg}"/>')
        o.append(f'<circle cx="{x0 + 50}" cy="{top + 50}" r="26" fill="{accent}"/>' + tx(x0 + 50, top + 61, letter, 30, "#fff"))
        o.append(tx(x0 + 90, top + 60, name, 32, INK, "start"))
        o.append(tx(x0 + 28, top + 108, desc, 18, SOFT, "start"))
        if letter == "A":
            o.append(f'<rect x="{x0 + pw - 108}" y="{top + 26}" width="84" height="40" rx="20" fill="#FF6B4A"/>' + tx(x0 + pw - 66, top + 54, "推薦", 22, "#fff"))
        o.append(G(bear(st, hat=True), cx, top + 322, 1.55))
        o.append(tx(cx, top + 448, "小熊廚師", 17, SOFT))
        o.append(G(tomato(st), cx - 122, top + 578, 1.38))
        o.append(tx(cx - 122, top + 688, "番茄", 17, SOFT))
        o.append(G(egg_pan(st), cx + 72, top + 570, 1.32))
        o.append(tx(cx + 88, top + 688, "小鍋煎蛋", 17, SOFT))
    o.append(tx(SW / 2, 878, "三種都不畫黑色外框：和「畫畫小鎮」的粗框貼紙、「字母寵物」的水彩繪本都不一樣。", 19, SOFT))
    return page("".join(o), "#F6F1EA", SW, SH)


# ---------------------------------------------------------------- shared screen bits
def wall_bg(c0, c1, stripes=None):
    o = [f'<rect width="{W}" height="{H}" fill="{lin("wall" + c0[1:], [(0, c0), (1, c1)])}"/>']
    if stripes:
        o.append("".join(f'<rect x="{x}" y="0" width="22" height="{H}" fill="{stripes}" opacity=".35"/>' for x in range(10, W, 48)))
    return "".join(o)


def tiles_bg(color, y0=0, y1=H, size=48):
    o = [f'<rect x="0" y="{y0}" width="{W}" height="{y1 - y0}" fill="{color}"/>']
    for yy in range(y0, y1, size):
        for xx in range(-4, W, size):
            o.append(f'<rect x="{xx + 3}" y="{yy + 3}" width="{size - 6}" height="{size - 6}" rx="10" fill="#fff" opacity=".28"/>')
    return "".join(o)


def top_bar_coins(x, y, coins=120, stars=8):
    return (chip(x, y - 20, 96, 40, G(coin(13), x + 22, y) + tx(x + 62, y + 7, str(coins), 20))
            + chip(x + 106, y - 20, 76, 40, G(star_icon(13), x + 128, y) + tx(x + 158, y + 7, str(stars), 20)))


def garland(y=86):
    o = [f'<path d="M -10 {y - 8} Q 195 {y + 28} 400 {y - 8}" stroke="#C99A6B" stroke-width="2" fill="none"/>']
    cols = ["#FF8A80", "#FFD166", "#7FD1AE", "#7EC8F0", "#C7A3FF"]
    for i, t in enumerate([j / 11 for j in range(1, 11)]):
        x = -10 + 410 * t
        yy = (1 - t) ** 2 * (y - 8) + 2 * t * (1 - t) * (y + 28) + t * t * (y - 8)
        o.append(cl("path", cols[i % 5], f'd="M {x - 11:.1f} {yy:.1f} L {x + 11:.1f} {yy:.1f} L {x:.1f} {yy + 22:.1f} Z" stroke="{cols[i % 5]}" stroke-width="4" stroke-linejoin="round"', "xs"))
    return "".join(o)


# ---------------------------------------------------------------- 1 order
def screen_order():
    o = [wall_bg("#FFE6CC", "#FFD6B3", "#FFF1E2")]
    o.append(garland(92))
    # shelves beside the bear
    o.append(cl("rect", "#C98E55", 'x="-20" y="486" width="126" height="14" rx="7"', "m"))
    o.append(G(jar("#FF8A65", "#E8573F"), 24, 456) + G(jar("#FFD166", "#5DBB63"), 70, 456, .9))
    o.append(cl("rect", "#C98E55", 'x="284" y="486" width="130" height="14" rx="7"', "m"))
    o.append(G(plant(), 330, 452, .95) + G(jar("#B9E3A0", "#7EC8F0"), 374, 460, .8))
    # bear customer: body, head, paws on the counter
    o.append(cl("path", "#5FB7A6", 'd="M 120 470 C 112 520 108 570 104 620 L 286 620 C 282 570 278 520 270 470 Q 195 440 120 470 Z"', "l"))
    o.append(cl("path", "#FFFFFF", 'd="M 168 466 L 195 500 L 222 466 Q 195 458 168 466 Z"', "s"))
    o.append(cl("path", "#FF7B6B", 'd="M 195 494 L 174 482 L 174 508 Z M 195 494 L 216 482 L 216 508 Z" stroke="#FF7B6B" stroke-width="5" stroke-linejoin="round"', "s"))
    o.append(cl("circle", "#FF7B6B", 'cx="195" cy="494" r="6"', "xs"))
    o.append(G(bear("clay", mood="happy"), 195, 400, 1.05))
    # counter
    o.append(cl("rect", "#B97A45", 'x="-20" y="618" width="430" height="150" rx="10"', "l"))
    for x in range(14, 390, 62):
        o.append(f'<rect x="{x}" y="652" width="50" height="96" rx="12" fill="{dk("#B97A45", .1)}" opacity=".5"/>'
                 f'<rect x="{x + 1.5}" y="654" width="50" height="96" rx="12" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="2"/>')
    o.append(cl("rect", "#E2AE72", 'x="-20" y="600" width="430" height="34" rx="14"', "m"))
    o.append(wood_grooves(10, 604, 370, 26, 3, seed=3, color="#E2AE72"))
    for x in (148, 242):
        o.append(cl("ellipse", BEAR, f'cx="{x}" cy="604" rx="22" ry="14"', "m"))
    o.append(G(bell(), 336, 590, 1.0))
    o.append(cl("ellipse", "#FFFFFF", 'cx="54" cy="606" rx="38" ry="10"', "m"))
    o.append(cl("ellipse", "#F1ECE4", 'cx="54" cy="604" rx="26" ry="5.5"', "xs", shadow=False, inv=True))
    # order bubble (pictures only)
    o.append(speech_bubble(22, 112, 346, 214, 196, 344))
    o.append(G(sandwich(), 195, 186, 1.2))
    o.append(f'<rect x="44" y="244" width="302" height="2" rx="1" fill="#EADFD2"/>')
    o.append(G(bread_slice(), 66, 287, .82))
    o.append(plus(110, 287, 8))
    o.append(G(cheese_slice(), 152, 287, .85))
    o.append(plus(196, 287, 8))
    for i, x in enumerate((230, 250, 270)):
        o.append(G(tomato_slice(17), x, 287 + (i - 1) * 2))
    o.append(G(cl("circle", "#FFC83A", 'r="18"', "s") + tx(0, 9, "3", 26, "#fff"), 322, 276))
    o.append(dots(322, 306, 3, 3, r=4.5, gap=13))
    # top bar
    o.append(G(child_avatar(), 40, 42))
    o.append(top_bar_coins(82, 42))
    o.append(cl("circle", CREAM, 'cx="350" cy="42" r="24"', "m") + G(book_icon(), 350, 42, .85))
    # start button
    o.append(big_btn(195, 800, 290, 72, ORANGE, "開始做"))
    return page("".join(o), "#FFE6CC")


# ---------------------------------------------------------------- 2 recipe card
def kid_hand(sx=1, sleeve="#7EC8F0"):
    """Small open hand, fingers up; thumb on the left (sx=1) or right (sx=-1). About 34 wide, 60 tall."""
    o = [cl("rect", sleeve, 'x="-14" y="14" width="28" height="14" rx="6"', "s")]
    for x, h in ((-9, 20), (-3, 24), (3, 23), (9, 19)):
        o.append(cl("rect", SKIN, f'x="{x * sx - 3.3}" y="{-8 - h}" width="6.6" height="{h + 10}" rx="3.3"', "xs"))
    o.append(cl("rect", SKIN, 'x="-13" y="-12" width="26" height="28" rx="9"', "s"))
    o.append(cl("ellipse", SKIN, f'cx="{-14 * sx}" cy="0" rx="4.5" ry="10" transform="rotate({30 * sx} {-14 * sx} 0)"', "xs"))
    return "".join(o)


def foam(lst):
    return clg("".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{cg("#FFFFFF")}"/>' for x, y, r in lst), "s")


def hands_bubbles():
    o = [G(kid_hand(-1), -19, 8, 1.15, -16), G(kid_hand(1), 19, 8, 1.15, 16)]
    o.append(foam([(-6, -6, 7), (2, -12, 8), (8, -2, 6), (-2, 4, 6), (-24, -16, 5), (24, -14, 5)]))
    o.append(bubbles([(-30, -34, 9), (0, -44, 12), (28, -30, 8), (-8, 6, 7), (40, 4, 6), (-40, 0, 5), (16, -14, 5)]))
    return "".join(o)


def bubbles(lst):
    D.add("bub", '<radialGradient id="bub" cx="50%" cy="50%" r="50%" fx="38%" fy="34%"><stop offset="0" stop-color="#fff" stop-opacity=".15"/>'
                 '<stop offset=".72" stop-color="#CFEFFF" stop-opacity=".35"/><stop offset="1" stop-color="#8FD3F5" stop-opacity=".9"/></radialGradient>')
    o = []
    for x, y, r in lst:
        o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#bub)"/>'
                 f'<path d="M {x - r * .55:.1f} {y - r * .2:.1f} A {r * .6:.1f} {r * .6:.1f} 0 0 1 {x - r * .1:.1f} {y - r * .6:.1f}" stroke="#fff" stroke-width="{max(1.2, r * .18):.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def wash_tomato():
    o = [cl("rect", "#AEB7C2", 'x="-46" y="-56" width="30" height="16" rx="7"', "s"),
         cl("path", "#AEB7C2", 'd="M -24 -56 L 6 -56 Q 22 -56 22 -40 L 22 -30 L 8 -30 L 8 -38 Q 8 -42 4 -42 L -24 -42 Z"', "m"),
         cl("rect", "#E8573F", 'x="-38" y="-66" width="12" height="10" rx="4"', "xs")]
    o.append(f'<path d="M 15 -30 C 11 -18 19 -8 15 6" stroke="#8FD3F5" stroke-width="10" stroke-linecap="round" fill="none" opacity=".75"/>')
    o.append(G(tomato("clay"), 12, 26, .55))
    o.append(bubbles([(-14, 14, 6), (36, 20, 7), (30, 0, 4), (-10, -6, 4)]))
    for x, y in ((-6, 46), (34, 44), (-18, 30)):
        o.append(f'<path d="M {x} {y - 6} Q {x + 4} {y} {x} {y + 3} Q {x - 4} {y} {x} {y - 6} Z" fill="#8FD3F5"/>')
    return "".join(o)


def cut_tomato_icon():
    o = [cl("rect", WOOD, 'x="-50" y="-30" width="100" height="66" rx="14"', "m"),
         wood_grooves(-44, -24, 88, 54, 3, seed=5)]
    o.append(G(tomato("clay"), -14, 0, .42))
    o.append(G(tomato_slice(11), 24, 14))
    o.append(G(tomato_slice(11), 30, -6))
    o.append(G(knife(), 22, -38, .55, -40))
    return "".join(o)


def stack_icon():
    o = [G(cl("rect", CRUST, 'x="-40" y="-8" width="80" height="16" rx="8"', "s"), 0, 40)]
    o.append(G(cl("rect", CHEESE, 'x="-36" y="-6" width="72" height="12" rx="4"', "s"), 0, 18))
    for x in (-22, 0, 22):
        o.append(cl("ellipse", TOMATO, f'cx="{x}" cy="0" rx="12" ry="6"', "xs"))
    o.append(G(cl("rect", CRUST, 'x="-40" y="-9" width="80" height="18" rx="8"', "s")
               + cl("rect", CRUMB, 'x="-34" y="-6" width="68" height="6" rx="3"', "xs", shadow=False), 0, -22))
    o.append(cw("M 52 -30 V 28", "#FFB23F", 6, "xs", box=(44, -36, 16, 70)))
    o.append(cl("path", "#FFB23F", 'd="M 44 22 L 60 22 L 52 34 Z" stroke="#FFB23F" stroke-width="5" stroke-linejoin="round"', "xs"))
    return "".join(o)


def screen_recipe():
    o = [tiles_bg("#DDF1E6")]
    o.append(back_btn())
    o.append(title_chip("食譜", icon=G(book_icon(), 0, 0, .7)))
    o.append(cl("rect", CREAM, 'x="14" y="84" width="362" height="652" rx="34"', "xl"))
    o.append(G(sandwich(flag=False), 195, 160, 1.25))
    o.append(tx(195, 252, "番茄起司三明治", 22, INK))
    steps = [("洗手", hands_bubbles, "done"), ("洗番茄", wash_tomato, "now"), ("切番茄", cut_tomato_icon, ""), ("疊起來", stack_icon, "")]
    for i, (label, pic, state) in enumerate(steps):
        x, y = (30 if i % 2 == 0 else 205), (274 if i < 2 else 498)
        w, h = 155, 206
        if state == "now":
            o.append(f'<rect x="{x - 8}" y="{y - 8}" width="{w + 16}" height="{h + 16}" rx="32" fill="#FFD84D" opacity=".55" filter="{blur(6)}"/>')
            o.append(cl("rect", "#FFC83A", f'x="{x - 6}" y="{y - 6}" width="{w + 12}" height="{h + 12}" rx="30"', "m"))
            o.append(cl("rect", "#FFF6D0", f'x="{x}" y="{y}" width="{w}" height="{h}" rx="25"', "m", shadow=False))
        else:
            o.append(cl("rect", "#F4EADC" if state == "done" else "#FFFFFF", f'x="{x}" y="{y}" width="{w}" height="{h}" rx="25"', "m"))
        o.append(G(pic(), x + w / 2, y + 96, 1.0, extra='opacity=".85"' if state == "done" else ""))
        o.append(G(num_badge(i + 1, 17, "#B7A493" if state == "done" else ("#FF8A3D" if state == "now" else "#7EC8F0")), x + 22, y + 22))
        o.append(tx(x + w / 2, y + h - 18, label, 21, INK if state != "done" else SOFT))
        if state == "done":
            o.append(G(check_badge(18), x + w - 22, y + 22))
        if state == "now":
            for dx, dy, r in ((w + 2, -4, 9), (w - 8, 22, 5), (-4, h + 2, 7)):
                o.append(G(cl("path", "#FFD84D", f'd="{star_path(r, r * .38, 4)}"', "xs"), x + dx, y + dy))
    o.append(big_btn(195, 796, 260, 68, GREEN, "做做看"))
    return page("".join(o), "#DDF1E6")


# ---------------------------------------------------------------- 3 cut and count
def screen_cut():
    o = [tiles_bg("#FFE9D9", 0, 220)]
    o.append(f'<rect x="0" y="200" width="{W}" height="{H - 200}" fill="{lin("counter3", [(0, "#BFE3DA"), (1, "#A6D6CB")])}"/>')
    o.append(cl("rect", "#D8F0EA", 'x="-20" y="192" width="430" height="22" rx="10"', "m"))
    o.append(back_btn())
    # counter 2 / 3 with dots
    o.append(cl("rect", CREAM, 'x="110" y="60" width="170" height="104" rx="30"', "l"))
    o.append(G(tomato_slice(17), 148, 96))
    o.append(tx(222, 108, "2 / 3", 36, INK))
    o.append(dots(195, 140, 3, 2, r=8, gap=28))
    o.append(tx(195, 32, "切切看・數一數", 20, SOFT))
    # board
    o.append(cl("rect", WOOD, 'x="20" y="250" width="350" height="440" rx="36"', "xl"))
    o.append(cl("rect", WOOD, 'x="155" y="222" width="80" height="50" rx="22"', "l"))
    o.append(cl("rect", dk(WOOD, .2), 'x="180" y="236" width="30" height="14" rx="7"', "xs", shadow=False, inv=True))
    o.append(wood_grooves(40, 280, 310, 390, 9, seed=8))
    # tomato with its right side cut off
    D.add("cut3", '<clipPath id="cut3"><rect x="-80" y="-80" width="118" height="160"/></clipPath>')
    body = cl("path", TOMATO, f'd="{TOMATO_BODY}"', "l")
    cutface = (cl("ellipse", "#F65E4C", 'cx="38" cy="5" rx="8" ry="40"', "s", shadow=False)
               + cl("ellipse", "#FF9A85", 'cx="38.5" cy="5" rx="4.5" ry="33"', "xs", shadow=False)
               + "".join(cl("ellipse", "#FFD0B5", f'cx="38.5" cy="{yy}" rx="2.4" ry="6"', "xs", shadow=False) for yy in (-16, 5, 26)))
    tom = f'<g clip-path="url(#cut3)">{body}{hl(-26, -12, 10, 6, -40, .5)}{dent(-20, 22, 8, 10, .8)}</g>{cutface}'
    leaves = "".join(f'<ellipse cx="{math.cos(math.radians(a)) * 11:.1f}" cy="{-35 + math.sin(math.radians(a)) * 6:.1f}" rx="12.5" ry="5.2" '
                     f'fill="{cg(LEAF)}" transform="rotate({a} {math.cos(math.radians(a)) * 11:.1f} {-35 + math.sin(math.radians(a)) * 6:.1f})"/>' for a in (-54, 18, 90, 162, 234))
    tom += clg(leaves, "s") + cl("rect", STEM, 'x="-3.5" y="-52" width="7" height="15" rx="3.5"', "xs")
    o.append(G(tom, 148, 470, 1.7))
    # two slices lying aside
    o.append(G(tomato_slice(36), 302, 420))
    o.append(G(tomato_slice(36), 310, 515))
    # dashed swipe line
    o.append(f'<line x1="198" y1="330" x2="198" y2="612" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-dasharray="1 18" opacity=".14" transform="translate(1.5 2)"/>')
    o.append(f'<line x1="198" y1="330" x2="198" y2="612" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-dasharray="1 18"/>')
    # knife at the top of the line
    o.append(G(knife(), 198, 266, .9, -6))
    # hint finger and arrow showing the swipe goes down
    o.append(cw("M 238 404 V 540", "#FFFFFF", 7, "xs", box=(228, 394, 20, 156)))
    o.append(cl("path", "#FFFFFF", 'd="M 226 534 L 250 534 L 238 552 Z" stroke="#fff" stroke-width="6" stroke-linejoin="round"', "xs"))
    o.append(G(pointer_hand(180, .8), 238, 396))
    # plate with bread and cheese waiting
    o.append(cl("ellipse", "#FFFFFF", 'cx="195" cy="770" rx="96" ry="44"', "l"))
    o.append(cl("ellipse", "#F2ECE3", 'cx="195" cy="768" rx="68" ry="28"', "s", shadow=False, inv=True))
    o.append(G(bread_slice(), 172, 764, .82, -8) + G(cheese_slice(), 216, 768, .66, 10))
    return page("".join(o), "#BFE3DA")


# ---------------------------------------------------------------- 4 egg pancake
def pancake():
    r = random.Random(4)
    o = [cl("circle", "#F2CB80", 'r="94"', "l")]
    o.append(f'<circle r="88" fill="none" stroke="#D99A45" stroke-width="8" opacity=".4" filter="{blur(4)}"/>')
    o.append(f'<path d="M -62 -30 C -50 -70 10 -76 44 -54 C 76 -34 74 10 60 36 C 42 70 -10 74 -40 56 C -70 36 -74 0 -62 -30 Z" fill="#FFE07A" opacity=".85" filter="{blur(5)}"/>')
    for x, y, rx, ry, a in ((-24, -20, 26, 15, 20), (22, 14, 22, 13, -30), (-6, 36, 18, 10, 10), (30, -36, 14, 8, 40)):
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#FFF3B8" opacity=".8" transform="rotate({a} {x} {y})" filter="{blur(4)}"/>')
    for _ in range(10):
        a, d = r.uniform(0, 6.28), r.uniform(55, 84)
        o.append(f'<circle cx="{math.cos(a) * d:.0f}" cy="{math.sin(a) * d:.0f}" r="{r.uniform(4, 8):.1f}" fill="#C98535" opacity=".22" filter="{blur(2.5)}"/>')
    for _ in range(18):
        a, d = r.uniform(0, 6.28), r.uniform(8, 74)
        x, y = math.cos(a) * d, math.sin(a) * d
        o.append(cl("rect", "#63B947" if r.random() < .7 else "#A6DB7A", f'x="{x - 4:.0f}" y="{y - 2.5:.0f}" width="8" height="5" rx="2.5" transform="rotate({r.randint(0, 180)} {x:.0f} {y:.0f})"', "xs"))
    o.append(hl(-46, -50, 18, 7, -40, .35))
    o.append(dent(40, 44, 10, 20, .7))
    return "".join(o)


def arrow_head(x, y, tx_, ty_, size=18, color="#FFFFFF"):
    """Rounded arrow head at (x, y) pointing along (tx_, ty_)."""
    n = math.hypot(tx_, ty_)
    ux, uy = tx_ / n, ty_ / n
    px, py = -uy, ux
    pts = [(x + ux * size, y + uy * size), (x + px * size * .75, y + py * size * .75), (x - px * size * .75, y - py * size * .75)]
    d = "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z"
    return cl("path", color, f'd="{d}" stroke="{color}" stroke-width="6" stroke-linejoin="round"', "s")


def timer_ring(cx, cy, R, frac, width=18):
    o = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#FFFFFF" stroke-opacity=".28" stroke-width="{width}"/>']
    n = 60
    segs = []
    for i in range(int(n * frac)):
        a0 = -90 + 360 * i / n
        a1 = -90 + 360 * (i + 1.3) / n
        t = i / (n * frac)
        col = mix("#FFE45C", "#E59A1E", t)
        x0, y0 = cx + R * math.cos(math.radians(a0)), cy + R * math.sin(math.radians(a0))
        x1, y1 = cx + R * math.cos(math.radians(a1)), cy + R * math.sin(math.radians(a1))
        segs.append(f'<path d="M {x0:.1f} {y0:.1f} A {R} {R} 0 0 1 {x1:.1f} {y1:.1f}" stroke="{col}" stroke-width="{width}" fill="none"/>')
    segs.insert(0, f'<circle cx="{cx}" cy="{cy - R}" r="{width / 2}" fill="#FFE45C"/>')
    ae = math.radians(-90 + 360 * frac)
    ex, ey = cx + R * math.cos(ae), cy + R * math.sin(ae)
    segs.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{width / 2}" fill="#E59A1E"/>')
    o.append(f'<g filter="{cf("s")}">{"".join(segs)}</g>')
    o.append(cl("circle", "#E59A1E", f'cx="{ex:.1f}" cy="{ey:.1f}" r="16"', "s"))
    o.append(G(cl("path", "#FFFFFF", f'd="{star_path(8, 3.6)}" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"', "xs"), ex, ey))
    for dx, dy, s in ((24, -10, 7), (18, 16, 5)):
        o.append(G(cl("path", "#FFF2A8", f'd="{star_path(s, s * .35, 4)}"', "xs"), ex + dx, ey + dy))
    return "".join(o)


def screen_pancake():
    o = [tiles_bg("#FFEFD9", 0, 130)]
    o.append(f'<rect x="0" y="120" width="{W}" height="{H - 120}" fill="#E9D3B8"/>')
    o.append(back_btn())
    dish = (cl("ellipse", "#FFFFFF", 'cy="4" rx="22" ry="9"', "s")
            + "".join(cl("rect", "#F2CB80", f'x="{x - 6}" y="-10" width="12" height="14" rx="5"', "xs")
                      + f'<path d="M {x - 2} -5 a 2.5 2.5 0 1 1 2 3" stroke="#D99A45" stroke-width="1.4" fill="none"/>' for x in (-13, 0, 13)))
    o.append(title_chip("煎蛋餅", icon=dish))
    # stove top
    o.append(cl("rect", "#5B6068", 'x="10" y="96" width="370" height="620" rx="40"', "xl"))
    o.append(cl("rect", "#666B74", 'x="22" y="108" width="346" height="596" rx="32"', "m", shadow=False, inv=True))
    for ccx, ccy in ((70, 154), (320, 154)):
        o.append(f'<circle cx="{ccx}" cy="{ccy}" r="30" fill="none" stroke="#4A4E55" stroke-width="7"/><circle cx="{ccx}" cy="{ccy}" r="13" fill="#4A4E55"/>')
    # pan
    o.append(G(cl("rect", "#A8703F", 'x="120" y="-13" width="110" height="26" rx="13"', "m")
               + cl("rect", "#8A9099", 'x="108" y="-9" width="22" height="18" rx="5"', "s"), 195, 404, 1, 52))
    o.append(cl("circle", PAN, 'cx="195" cy="404" r="124"', "xl"))
    o.append(cl("circle", dk(PAN, .15), 'cx="195" cy="404" r="108"', "m", shadow=False, inv=True))
    o.append(G(pancake(), 195, 404))
    # flip arrow
    o.append(G(cl("rect", "#E8573F", 'x="-6" y="-58" width="12" height="44" rx="6"', "s")
               + cl("rect", "#C9CED6", 'x="-20" y="-16" width="40" height="34" rx="9"', "m")
               + "".join(f'<rect x="{x}" y="-6" width="3" height="16" rx="1.5" fill="#9BA3AD"/>' for x in (-10, -2, 6)), 140, 462, .9, -135))
    o.append(cw("M 128 432 C 112 330 250 292 274 372", "#FFFFFF", 12, "s", box=(104, 300, 186, 140)))
    o.append(arrow_head(274, 372, 24, 80, 20))
    # timer ring
    o.append(timer_ring(195, 404, 156, .68))
    # knobs and the grown-up badge
    for x in (60, 120):
        o.append(cl("circle", "#9BA3AD", f'cx="{x}" cy="666" r="20"', "m") + cl("rect", "#7C848E", f'x="{x - 4}" y="650" width="8" height="32" rx="4"', "xs"))
    o.append(cl("circle", "#9BA3AD", 'cx="330" cy="666" r="22"', "m") + cl("rect", "#7C848E", 'x="326" y="648" width="8" height="36" rx="4" transform="rotate(40 330 666)"', "xs"))
    o.append(G(adult_hand(), 330, 640, .82, -20))
    o.append(cl("rect", "#FFF2C7", 'x="146" y="640" width="160" height="50" rx="25"', "m"))
    o.append(G(adult_hand(), 172, 668, .55))
    o.append(tx(246, 660, "爐火：", 15, "#B5541E") + tx(246, 681, "請大人幫忙", 15, "#B5541E"))
    # counter: waiting plate and sauce bottle
    o.append(cl("rect", "#F4E6D4", 'x="-20" y="736" width="430" height="140" rx="20"', "m"))
    o.append(cl("ellipse", "#FFFFFF", 'cx="120" cy="790" rx="86" ry="34"', "l"))
    o.append(cl("ellipse", "#F2ECE3", 'cx="120" cy="788" rx="60" ry="20"', "s", shadow=False, inv=True))
    o.append(G(cl("rect", "#6B3F22", 'x="-20" y="-34" width="40" height="64" rx="14"', "m")
               + cl("rect", "#FFD166", 'x="-14" y="-10" width="28" height="22" rx="6"', "xs", shadow=False)
               + cl("rect", "#E8573F", 'x="-9" y="-50" width="18" height="18" rx="6"', "s")
               + hl(-11, -14, 3, 10, 0, .5), 300, 784))
    return page("".join(o), "#E9D3B8")


# ---------------------------------------------------------------- 5 market
def crate(x, y, w, h):
    o = [cl("rect", "#C98E55", f'x="{x}" y="{y}" width="{w}" height="{h}" rx="12"', "m")]
    for i in range(1, 3):
        yy = y + h * i / 3
        o.append(f'<rect x="{x + 8}" y="{yy - 2}" width="{w - 16}" height="4" rx="2" fill="{dk("#C98E55", .3)}" opacity=".35"/>'
                 f'<rect x="{x + 8}" y="{yy + 1.5}" width="{w - 16}" height="2" rx="1" fill="#fff" opacity=".25"/>')
    for xx in (x + 12, x + w - 12):
        for yy in (y + 12, y + h - 12):
            o.append(f'<circle cx="{xx}" cy="{yy}" r="2.5" fill="{dk("#C98E55", .4)}" opacity=".5"/>')
    return "".join(o)


def price_tag(cx, cy, name, price):
    return (cl("rect", "#FFF8E6", f'x="{cx - 38}" y="{cy - 24}" width="76" height="48" rx="10"', "s")
            + f'<circle cx="{cx}" cy="{cy - 16}" r="3" fill="{dk("#FFF8E6", .3)}"/>'
            + tx(cx, cy + 1, name, 13, SOFT) + tx(cx, cy + 20, price, 18, "#D9472B"))


def basket(items=True):
    o = [cw("M -72 -10 C -66 -86 66 -86 72 -10", "#B9824A", 9, "s", box=(-80, -90, 160, 90))]
    if items:
        o.append(G(carrot(), -42, -26, .8, -30) + G(carrot(), -22, -34, .8, -12))
        o.append(G(cabbage(), 12, -20, .8))
        o.append(G(egg(), 46, -14, .9) + G(egg(), 60, -24, .9) + G(egg(), 40, -32, .9))
    o.append(cl("path", "#C98E55", 'd="M -86 -14 L 86 -14 L 72 60 Q 70 70 60 70 L -60 70 Q -70 70 -72 60 Z"', "l"))
    for i, yy in enumerate((4, 20, 36, 52)):
        half = 80 - i * 4
        k = -half
        while k < half - 6:
            xx = k + (9 if i % 2 else 0)
            o.append(f'<rect x="{xx:.0f}" y="{yy - 6}" width="15" height="12" rx="6" fill="{dk("#C98E55", .22)}" opacity=".32"/>'
                     f'<rect x="{xx + 2:.0f}" y="{yy - 5}" width="10" height="4" rx="2" fill="#fff" opacity=".22"/>')
            k += 18
    o.append(cl("rect", "#B9824A", 'x="-92" y="-22" width="184" height="18" rx="9"', "m"))
    return "".join(o)


def screen_market():
    o = [wall_bg("#FFF0D9", "#FBE2C2")]
    # distant stalls
    for x, c in ((-30, "#F6D7C5"), (300, "#D9E8D2")):
        o.append(f'<rect x="{x}" y="160" width="120" height="140" rx="16" fill="{c}" opacity=".8"/>')
    o.append(back_btn())
    o.append(title_chip("市場買菜", cx=170, w=150))
    o.append(chip(268, 20, 106, 40, G(coin(13), 290, 40) + tx(334, 47, "30", 20)))
    # awning
    stripes = "".join(f'<rect x="{x}" y="80" width="39" height="62" fill="{cg("#F2665A" if i % 2 == 0 else "#FFF4E0")}"/>' for i, x in enumerate(range(0, 390, 39)))
    stripes += "".join(f'<circle cx="{x + 19.5}" cy="142" r="19.5" fill="{cg("#F2665A" if i % 2 == 0 else "#FFF4E0")}"/>' for i, x in enumerate(range(0, 390, 39)))
    o.append(cl("rect", "#A8703F", 'x="10" y="120" width="12" height="200" rx="6"', "s") + cl("rect", "#A8703F", 'x="368" y="120" width="12" height="200" rx="6"', "s"))
    o.append(clg(stripes, "l"))
    # vendor pig
    o.append(cl("path", "#7FC8E8", 'd="M 50 268 C 46 236 66 222 100 222 C 134 222 154 236 150 268 Z"', "m"))
    o.append(cl("path", "#FFFFFF", 'd="M 76 236 L 124 236 L 120 270 L 80 270 Z"', "s"))
    o.append(G(pig(), 100, 196, .78))
    o.append(speech_bubble(180, 168, 194, 84, 150, 214))
    o.append(tx(236, 224, "要付", 20, INK) + tx(296, 228, "13", 36, "#D9472B") + tx(342, 224, "元", 20, INK))
    # stall table with three crates
    o.append(cl("rect", "#E2AE72", 'x="0" y="262" width="390" height="22" rx="8"', "m"))
    o.append(G(carrot(), 44, 296, .9, -70) + G(carrot(), 52, 314, .9, -60) + G(carrot(), 86, 300, .9, -100) + G(carrot(), 90, 318, .9, -80))
    o.append(G(cabbage(), 172, 300, .95) + G(cabbage(), 222, 306, .95))
    o.append(cl("rect", "#E4CDA6", 'x="276" y="296" width="96" height="26" rx="8"', "s"))
    for i, (ex, ey) in enumerate(((292, 300), (316, 300), (340, 300), (360, 302), (304, 286), (328, 286), (352, 288))):
        o.append(G(egg(), ex, ey, .78))
    o.append(crate(14, 318, 116, 112) + crate(137, 318, 116, 112) + crate(260, 318, 116, 112))
    o.append(price_tag(72, 378, "紅蘿蔔", "2元") + price_tag(195, 378, "高麗菜", "6元") + price_tag(318, 378, "雞蛋", "1元"))
    # shopping list
    o.append(cl("rect", "#FFFDF6", 'x="16" y="458" width="164" height="236" rx="18"', "l"))
    o.append(cl("rect", "#E8573F", 'x="74" y="448" width="48" height="20" rx="8"', "s"))
    o.append(tx(98, 494, "購物清單", 17, SOFT))
    rows = [(530, [(48, .55, carrot), (80, .55, carrot)], "2"), (592, [(60, .62, cabbage)], "1"), (652, [(42, .9, egg), (66, .9, egg), (90, .9, egg)], "3")]
    for y, items, n in rows:
        o.append(f'<rect x="28" y="{y - 31}" width="140" height="2" rx="1" fill="#EFE5D6"/>')
        for x, s, f in items:
            o.append(G(f(), x, y + (4 if f is carrot else 0), s, -70 if f is carrot else 0))
        o.append(tx(122, y + 8, n, 22, INK))
        o.append(G(check_badge(14), 154, y + 2))
    # basket
    o.append(G(basket(), 282, 600, 1.0))
    # coin tray
    o.append(cl("rect", "#C98E55", 'x="14" y="704" width="362" height="126" rx="26"', "l"))
    o.append(cl("rect", "#B07A44", 'x="26" y="716" width="338" height="102" rx="18"', "m", shadow=False, inv=True))
    o.append(G(coin(17, "#E9B04A", "1"), 62, 750) + G(coin(17, "#E9B04A", "1"), 98, 752) + G(coin(17, "#E9B04A", "1"), 64, 790) + G(coin(17, "#E9B04A", "1"), 100, 792))
    o.append(G(coin(20, SILVER, "5"), 160, 752) + G(coin(20, SILVER, "5"), 168, 792))
    o.append(G(coin(25, "#D7DCE3", "10"), 236, 766) + G(coin(25, "#D7DCE3", "10"), 300, 770))
    return page("".join(o), "#FBE2C2")


# ---------------------------------------------------------------- 6 my plate
def rice():
    r = random.Random(2)
    lumps = "".join(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{cg("#FFFDF7")}"/>' for x, y, rr in
                    ((-18, 4, 16), (0, -6, 19), (18, 4, 16), (-6, 10, 15), (10, 12, 14)))
    o = [clg(lumps, "m")]
    for _ in range(22):
        x, y = r.uniform(-26, 26), r.uniform(-18, 18)
        if (x / 30) ** 2 + ((y - 2) / 22) ** 2 < 1:
            o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3" ry="1.6" fill="#EDE5D6" opacity=".9" transform="rotate({r.randint(0, 180)} {x:.1f} {y:.1f})"/>')
    return "".join(o)


def broccoli():
    o = [cl("path", "#A8D982", 'd="M -6 6 L 6 6 L 9 30 Q 0 34 -9 30 Z"', "s")]
    florets = "".join(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{cg("#4FA94A")}"/>' for x, y, rr in
                      ((-14, -2, 11), (0, -10, 13), (14, -2, 11), (-6, 6, 9), (8, 6, 9)))
    o.append(clg(florets, "m"))
    o.append(hl(-6, -14, 5, 3, -30, .4))
    return "".join(o)


def tofu():
    return (cl("rect", "#FFF2D2", 'x="-14" y="-14" width="28" height="28" rx="7"', "s")
            + cl("rect", "#FFF9E8", 'x="-10" y="-11" width="20" height="9" rx="4"', "xs", shadow=False))


def fried_egg(s=1.0):
    return G(cl("path", "#FFFDF6", f'd="{EGG_WHITE}"', "m") + cl("circle", "#FFB21F", 'cx="5" cy="-3" r="13"', "s") + hl(1, -8, 4, 2.6, -30, .7), s=s)


def banana():
    return (cl("path", "#FFD84D", 'd="M -36 -8 C -20 22 22 24 38 -6 C 40 -10 36 -12 34 -9 C 18 10 -18 8 -30 -12 Z" stroke="#FFD84D" stroke-width="6" stroke-linejoin="round"', "m")
            + cl("rect", "#7A5A2A", 'x="-40" y="-16" width="8" height="9" rx="3" transform="rotate(30 -36 -12)"', "xs")
            + hl(-8, 10, 12, 2.5, 8, .55))


def milk_cup():
    return (cw("M 22 -14 C 40 -14 40 18 22 16", "#7EC8F0", 7, "s", box=(16, -22, 30, 44))
            + cl("path", "#7EC8F0", 'd="M -26 -26 L 26 -26 L 22 30 Q 21 36 15 36 L -15 36 Q -21 36 -22 30 Z"', "m")
            + cl("ellipse", "#FFFFFF", 'cx="0" cy="-24" rx="24" ry="6"', "s", shadow=False)
            + cl("path", "#FFFFFF", 'd="M 0 -2 Q 8 8 8 13 A 8 8 0 0 1 -8 13 Q -8 8 0 -2 Z"', "xs")
            + hl(-16, 4, 3, 12, 0, .45))


def nut_spoon():
    o = [cl("rect", "#C9CED6", 'x="10" y="-5" width="54" height="10" rx="5" transform="rotate(-30)"', "s"),
         cl("ellipse", "#C9CED6", 'cx="-6" cy="4" rx="28" ry="18" transform="rotate(-30 -6 4)"', "m"),
         cl("ellipse", "#AEB5BF", 'cx="-6" cy="4" rx="21" ry="12" transform="rotate(-30 -6 4)"', "xs", shadow=False, inv=True)]
    o.append(cl("path", "#C58B52", 'd="M -20 6 Q -14 -6 -6 4 Q -12 12 -20 6 Z"', "xs"))
    o.append(cl("ellipse", "#E8C99A", 'cx="2" cy="-2" rx="7" ry="5" transform="rotate(-20 2 -2)"', "xs"))
    o.append(cl("path", "#D9A066", 'd="M -6 14 C -2 6 10 6 12 12 C 8 10 0 12 -6 14 Z" stroke="#D9A066" stroke-width="4" stroke-linejoin="round"', "xs"))
    o.append(cl("ellipse", "#B97A45", 'cx="-14" cy="-4" rx="5" ry="4"', "xs"))
    return "".join(o)


def wedge(cx, cy, r, a0, a1):
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M {cx} {cy} L {p0[0]:.1f} {p0[1]:.1f} A {r} {r} 0 {large} 1 {p1[0]:.1f} {p1[1]:.1f} Z"


def screen_plate():
    o = [wall_bg("#E9F3FF", "#DCEBFF")]
    # gingham table
    o.append(f'<rect x="0" y="330" width="{W}" height="{H - 330}" fill="#FFF3D6"/>')
    for x in range(0, W, 40):
        o.append(f'<rect x="{x}" y="330" width="20" height="{H - 330}" fill="#FFC9A3" opacity=".35"/>')
    for y in range(330, H, 40):
        o.append(f'<rect x="0" y="{y}" width="{W}" height="20" fill="#FFC9A3" opacity=".35"/>')
    o.append(back_btn())
    o.append(title_chip("我的餐盤", cx=195, w=160))
    # rabbit customer behind the table
    o.append(cl("path", "#FFB3C7", 'd="M 70 340 C 70 290 92 268 130 268 C 168 268 190 290 190 340 Z"', "l"))
    o.append(cl("path", "#FFFFFF", 'd="M 104 276 L 156 276 L 150 312 Q 130 324 110 312 Z"', "s"))
    o.append(G(rabbit("joy"), 130, 206, .95))
    o.append(cl("ellipse", "#FFF4EA", 'cx="88" cy="336" rx="20" ry="12"', "m") + cl("ellipse", "#FFF4EA", 'cx="172" cy="336" rx="20" ry="12"', "m"))
    o.append(G(heart(1.8, "#FF6F91", "l"), 240, 150) + G(heart(.8, "#FF9AB5", "s"), 286, 112) + G(heart(.6, "#FFB3C7", "s"), 208, 104))
    o.append(speech_bubble(222, 196, 150, 60, 196, 226))
    o.append(tx(297, 234, "好好吃！", 20, INK))
    # plate
    cx, cy, R = 166, 520, 148
    o.append(cl("circle", "#FFFFFF", f'cx="{cx}" cy="{cy}" r="{R}"', "xl"))
    o.append(cl("circle", "#F6F1EA", f'cx="{cx}" cy="{cy}" r="{R - 16}"', "m", shadow=False, inv=True))
    secs = [("水果", 270, 335, "#FFE0EA"), ("豆魚蛋肉", 335, 408, "#FFE5D6"), ("蔬菜", 48, 165, "#DDF3D3"), ("全穀雜糧", 165, 270, "#FFF0C6")]
    for name, a0, a1, col in secs:
        o.append(f'<path d="{wedge(cx, cy, R - 22, a0, a1)}" fill="{col}"/>')
    o.append(f'<path d="{wedge(cx, cy, R - 34, 272, 333)}" fill="none" stroke="#FF8FB1" stroke-width="3" stroke-dasharray="8 7" stroke-linecap="round" opacity=".8"/>')
    ridges = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx + (R - 18) * math.cos(math.radians(a)):.1f}" y2="{cy + (R - 18) * math.sin(math.radians(a)):.1f}" '
                     f'stroke="{cg("#FFFFFF")}" stroke-width="9" stroke-linecap="round"/>' for a in (270, 335, 48, 165))
    o.append(f'<g filter="{cf("s")}"><rect x="{cx - R}" y="{cy - R}" width="{2 * R}" height="{2 * R}" fill="none"/>{ridges.replace(cg("#FFFFFF"), "#FFFFFF")}</g>')
    o.append(cl("circle", "#FFFFFF", f'cx="{cx}" cy="{cy}" r="9"', "s"))

    def at(a, d):
        return cx + d * math.cos(math.radians(a)), cy + d * math.sin(math.radians(a))
    # foods
    x, y = at(218, 70)
    o.append(G(rice(), x, y, 1.15))
    x, y = at(100, 66)
    o.append(G(broccoli(), x - 22, y - 4, .95) + G(broccoli(), x + 18, y + 4, .8) + G(carrot(False), x + 2, y + 34, .55, -80) + G(carrot(False), x - 30, y + 28, .5, -60))
    x, y = at(12, 74)
    o.append(G(fried_egg(.72), x - 6, y - 14) + G(tofu(), x - 10, y + 30) + G(tofu(), x + 22, y + 22, .9, 10))
    # labels
    for name, a, d in (("全穀雜糧", 218, 112), ("蔬菜", 106, 116), ("豆魚蛋肉", 12, 112), ("水果", 298, 66)):
        lx, ly = at(a, d)
        w = len(name) * 14 + 16
        o.append(f'<rect x="{lx - w / 2:.1f}" y="{ly - 12:.1f}" width="{w}" height="24" rx="12" fill="#fff" opacity=".9"/>' + tx(lx, ly + 5, name, 14, SOFT))
    # fruit bowl; a banana is being dragged from it into the fruit part
    o.append(cl("ellipse", "#FFB36B", 'cx="346" cy="384" rx="34" ry="13"', "m"))
    o.append(G(cl("circle", "#F2564B", 'r="13"', "s") + cl("rect", STEM, 'x="-1.5" y="-18" width="3" height="8" rx="1.5"', "xs")
               + cl("ellipse", LEAF, 'cx="5" cy="-15" rx="6" ry="3" transform="rotate(-20 5 -15)"', "xs") + hl(-5, -5, 3, 2, -30, .7), 334, 362))
    o.append(G(cl("circle", "#FFA233", 'r="12"', "s") + hl(-4, -5, 3, 2, -30, .7), 358, 366))
    o.append(cl("path", "#FFB36B", 'd="M 310 382 L 382 382 Q 378 404 346 406 Q 314 404 310 382 Z"', "m"))
    o.append("".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".85"/>' for x, y, r in ((314, 352, 3), (302, 362, 4), (290, 372, 5))))
    o.append(G(banana(), 238, 424, .95, -28))
    o.append(G(pointer_hand(-135, .78), 246, 416))
    # milk and nuts
    o.append(G(milk_cup(), 350, 462, .95))
    o.append(tx(350, 518, "乳品", 15, SOFT))
    o.append(G(nut_spoon(), 350, 604, .9, -60))
    o.append(tx(350, 656, "堅果種子", 13, SOFT))
    # bottom label
    o.append(cl("rect", "#FF8FB1", 'x="80" y="742" width="230" height="62" rx="31"', "l"))
    o.append(ctx(195, 783, "均衡又好吃！", 28))
    o.append(G(star_icon(12), 62, 772) + G(star_icon(12), 328, 772))
    return page("".join(o), "#FFF3D6")


SCREENS = {"1_點餐": screen_order, "2_食譜卡": screen_recipe, "3_切切看_數一數": screen_cut,
           "4_煎蛋餅": screen_pancake, "5_市場買菜": screen_market, "6_我的餐盤": screen_plate}


def contact_sheet(names):
    cw_, ch_, gap, m = 250, 541, 18, 30
    w = 6 * cw_ + 5 * gap + 2 * m
    h = ch_ + 92
    imgs = "".join(f'<div style="position:absolute;left:{m + i * (cw_ + gap)}px;top:30px;width:{cw_}px;text-align:center">'
                   f'<img src="file://{HERE / (n + ".png")}" style="width:{cw_}px;height:{ch_}px;border-radius:18px;box-shadow:0 6px 16px rgba(60,40,20,.18)">'
                   f'<div style="font:20px Huninn, sans-serif;color:{INK};margin-top:12px">{n.replace("_", " ")}</div></div>' for i, n in enumerate(names))
    css = f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }} * {{ margin:0; padding:0 }} body {{ width:{w}px; height:{h}px; background:#F6F1EA; position:relative }}"
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{imgs}</body></html>', w, h


def render(html, out, w, h, scale):
    global D
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "page.html"
        p.write_text(html)
        subprocess.run(["node", str(HERE / "render.js"), str(p), str(out), str(w), str(h), str(scale)], check=True)


def main():
    global D
    D = Defs()
    render(style_sheet(), HERE / "0_畫風選擇.png", 1600, 900, 1)
    for name, make in SCREENS.items():
        D = Defs()
        render(make(), HERE / f"{name}.png", W, H, 2)
        print(name)
    html, w, h = contact_sheet(list(SCREENS))
    render(html, HERE / "contact_sheet.png", w, h, 1)
    print("done")


if __name__ == "__main__":
    main()

"""The clay (plasticine) drawing kit shared by every art script of 動物小餐廳.

The mockups (docs/mockups/make_mockups.py) got their clay look from an SVG
lighting filter. The app draws its pictures with flutter_svg, which does not
draw filters, so here the same look is built only from things flutter_svg
draws: paths, linear and radial gradients, clip paths and opacity.

One clay piece (clay()) is, from the back:
  - a soft drop shadow down and to the right (a few see-through copies of the
    shape, each a little fatter, so the edge fades out),
  - the shape filled with a radial gradient, light at the top left,
  - a rolled edge: inside a clip of the shape, a few strokes of its own outline
    with a gradient (white at the top left, a deeper shade of the clay colour
    at the bottom right), so the edge looks rounded and puffy,
  - a small soft shine and, if asked, a thumb dent or two.

Every point goes through the current transform (with at(...)) when a shape is
made, so the paths are written already moved, turned and scaled. That keeps the
light on the top left of the screen whichever way a piece is turned, and lets
save() know exactly how big the drawing is (for a tight viewBox).
Everything is deterministic: there is no randomness without a fixed seed.
"""
import contextlib
import hashlib
import math
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "app" / "assets" / "art"

# ---------------------------------------------------------------- colours
INK = "#4A2E20"          # eyes, mouths
SHADOW = "#4A2A14"       # every shadow
BLUSH = "#FF9C9C"
WHITE = "#FFFDF8"
TOMATO = "#E9483B"
LEAF = "#5CB25C"
STEM = "#3F8D45"
CRUST = "#D99A55"
CRUMB = "#F8DFAF"
CHEESE = "#FFCC3D"
YOLK = "#FFB21F"
WOOD = "#DDA86B"
GOLD = "#F2B43A"
SKIN = "#FFD2A8"
PAN = "#4F555E"
STEEL = "#C9CED6"


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#2A140A", t)


def f(v):
    """A number for the SVG: one decimal, no trailing .0."""
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s == "-0":
        s = "0"
    return s


# ---------------------------------------------------------------- transforms
class Mat:
    def __init__(self, a=1, b=0, c=0, d=1, e=0, f_=0):
        self.m = (a, b, c, d, e, f_)

    def __mul__(self, o):
        a, b, c, d, e, f_ = self.m
        A, B, C, D, E, F = o.m
        return Mat(a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f_)

    def apply(self, x, y):
        a, b, c, d, e, f_ = self.m
        return a * x + c * y + e, b * x + d * y + f_

    def scale(self):
        a, b, c, d, _, _ = self.m
        return math.sqrt(abs(a * d - b * c))


_STACK = [Mat()]


@contextlib.contextmanager
def at(x=0, y=0, rot=0, s=1, sx=None, sy=None):
    """Draw inside: moved to (x, y), turned by rot degrees, scaled (sx, sy or s)."""
    r = math.radians(rot)
    m = Mat(1, 0, 0, 1, x, y) * Mat(math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0, 0) * Mat(sx if sx is not None else s, 0, 0, sy if sy is not None else s, 0, 0)
    _STACK.append(_STACK[-1] * m)
    try:
        yield
    finally:
        _STACK.pop()


def T(x, y):
    return _STACK[-1].apply(x, y)


def S():
    """How much the current transform scales lengths."""
    return _STACK[-1].scale()


# ---------------------------------------------------------------- paths
K = 0.5523


def _bez_ext(p0, p1, p2, p3):
    """Extremes of one coordinate of a cubic."""
    out = [p0, p3]
    a = -p0 + 3 * p1 - 3 * p2 + p3
    b = 2 * (p0 - 2 * p1 + p2)
    c = p1 - p0
    ts = []
    if abs(a) < 1e-9:
        if abs(b) > 1e-9:
            ts.append(-c / b)
    else:
        disc = b * b - 4 * a * c
        if disc >= 0:
            sq = math.sqrt(disc)
            ts += [(-b + sq) / (2 * a), (-b - sq) / (2 * a)]
    for t in ts:
        if 0 < t < 1:
            u = 1 - t
            out.append(u ** 3 * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t ** 3 * p3)
    return min(out), max(out)


class Path:
    """A path whose points are already in page coordinates (made through T)."""

    def __init__(self):
        self.c = []        # (cmd, [points])
        self._cur = None
        self._start = None

    def M(self, x, y):
        p = T(x, y)
        self.c.append(("M", [p]))
        self._cur = self._start = p
        return self

    def L(self, x, y):
        p = T(x, y)
        self.c.append(("L", [p]))
        self._cur = p
        return self

    def C(self, x1, y1, x2, y2, x, y):
        pts = [T(x1, y1), T(x2, y2), T(x, y)]
        self.c.append(("C", pts))
        self._cur = pts[-1]
        return self

    def Q(self, x1, y1, x, y):
        q1, p = T(x1, y1), T(x, y)
        c1 = (self._cur[0] + 2 / 3 * (q1[0] - self._cur[0]), self._cur[1] + 2 / 3 * (q1[1] - self._cur[1]))
        c2 = (p[0] + 2 / 3 * (q1[0] - p[0]), p[1] + 2 / 3 * (q1[1] - p[1]))
        self.c.append(("C", [c1, c2, p]))
        self._cur = p
        return self

    def Z(self):
        self.c.append(("Z", []))
        self._cur = self._start
        return self

    def d(self, dx=0, dy=0):
        out = []
        for cmd, pts in self.c:
            out.append(cmd + " ".join(f"{f(x + dx)} {f(y + dy)}" for x, y in pts))
        return "".join(out)

    def bbox(self):
        xs, ys = [], []
        cur = None
        for cmd, pts in self.c:
            if cmd == "M" or cmd == "L":
                xs.append(pts[0][0]); ys.append(pts[0][1])
                cur = pts[0]
            elif cmd == "C":
                lo, hi = _bez_ext(cur[0], pts[0][0], pts[1][0], pts[2][0])
                xs += [lo, hi]
                lo, hi = _bez_ext(cur[1], pts[0][1], pts[1][1], pts[2][1])
                ys += [lo, hi]
                cur = pts[2]
        return min(xs), min(ys), max(xs), max(ys)

    def __add__(self, o):
        p = Path()
        p.c = self.c + o.c
        p._cur, p._start = o._cur, o._start
        return p


def parse(d):
    """A path from an SVG d string with absolute M L H V C Q Z only."""
    toks = []
    num = ""
    for ch in d.replace(",", " "):
        if ch.isalpha():
            if num.strip():
                toks.append(num)
            num = ""
            toks.append(ch)
        elif ch == " ":
            if num.strip():
                toks.append(num)
            num = ""
        elif ch == "-" and num and num[-1] not in "eE":
            toks.append(num)
            num = ch
        else:
            num += ch
    if num.strip():
        toks.append(num)
    p = Path()
    i = 0
    cmd = None
    lx = ly = 0.0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                p.Z()
                continue
        vals = []
        n = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "Q": 4}[cmd]
        for _ in range(n):
            vals.append(float(toks[i]))
            i += 1
        if cmd == "M":
            p.M(*vals); lx, ly = vals; cmd = "L"
        elif cmd == "L":
            p.L(*vals); lx, ly = vals
        elif cmd == "H":
            p.L(vals[0], ly); lx = vals[0]
        elif cmd == "V":
            p.L(lx, vals[0]); ly = vals[0]
        elif cmd == "C":
            p.C(*vals); lx, ly = vals[4], vals[5]
        elif cmd == "Q":
            p.Q(*vals); lx, ly = vals[2], vals[3]
    return p


def ellipse(cx, cy, rx, ry, rot=0):
    with at(cx, cy, rot):
        k = K
        return (Path().M(rx, 0).C(rx, k * ry, k * rx, ry, 0, ry).C(-k * rx, ry, -rx, k * ry, -rx, 0)
                .C(-rx, -k * ry, -k * rx, -ry, 0, -ry).C(k * rx, -ry, rx, -k * ry, rx, 0).Z())


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def rrect(x, y, w, h, r, rot=0):
    """Rounded rectangle; turned by rot round its middle."""
    r = min(r, w / 2, h / 2)
    cx, cy = x + w / 2, y + h / 2
    with at(cx, cy, rot):
        x0, y0, x1, y1 = -w / 2, -h / 2, w / 2, h / 2
        k = 1 - K
        p = Path().M(x0 + r, y0).L(x1 - r, y0).C(x1 - r * k, y0, x1, y0 + r * k, x1, y0 + r)
        p.L(x1, y1 - r).C(x1, y1 - r * k, x1 - r * k, y1, x1 - r, y1)
        p.L(x0 + r, y1).C(x0 + r * k, y1, x0, y1 - r * k, x0, y1 - r)
        p.L(x0, y0 + r).C(x0, y0 + r * k, x0 + r * k, y0, x0 + r, y0).Z()
        return p


def capsule(x1, y1, x2, y2, r):
    """A stadium (sausage) of radius r from (x1, y1) to (x2, y2)."""
    L = math.hypot(x2 - x1, y2 - y1)
    a = math.degrees(math.atan2(y2 - y1, x2 - x1))
    with at(x1, y1, a):
        return rrect(-r, -r, L + 2 * r, 2 * r, r)


def blob(pts, t=1.0, closed=True):
    """A smooth closed (or open) curve through the points (Catmull-Rom)."""
    n = len(pts)
    p = Path().M(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[(i + 1) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * t, p1[1] + (p2[1] - p0[1]) / 6 * t)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * t, p2[1] - (p3[1] - p1[1]) / 6 * t)
        p.C(*c1, *c2, *p2)
    if closed:
        p.Z()
    return p


def rpoly(pts, r):
    """Polygon with rounded corners."""
    n = len(pts)
    p = Path()
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        la, lc = math.hypot(a[0] - b[0], a[1] - b[1]), math.hypot(c[0] - b[0], c[1] - b[1])
        rr = min(r, la / 2.05, lc / 2.05)
        s = (b[0] + (a[0] - b[0]) * rr / la, b[1] + (a[1] - b[1]) * rr / la)
        e = (b[0] + (c[0] - b[0]) * rr / lc, b[1] + (c[1] - b[1]) * rr / lc)
        if i == 0:
            p.M(*s)
        else:
            p.L(*s)
        p.Q(*b, *e)
    p.Z()
    return p


def star_pts(R, r, n=5, cx=0, cy=0, rot=-90):
    return [(cx + (R if i % 2 == 0 else r) * math.cos(math.radians(rot + i * 180 / n)),
             cy + (R if i % 2 == 0 else r) * math.sin(math.radians(rot + i * 180 / n))) for i in range(2 * n)]


def wobble(pts, amt, seed):
    rnd = random.Random(seed)
    return [(x + rnd.uniform(-amt, amt), y + rnd.uniform(-amt, amt)) for x, y in pts]


def ring_pts(cx, cy, rx, ry, n=24, rot=0, wob=0, seed=1):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + (rnd.uniform(-wob, wob) if wob else 0)
        x, y = rx * k * math.cos(a), ry * k * math.sin(a)
        r = math.radians(rot)
        out.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return out


def line(*pts):
    """An open polyline (for strokes)."""
    p = Path().M(*pts[0])
    for q in pts[1:]:
        p.L(*q)
    return p


# ---------------------------------------------------------------- the page being drawn
class Page:
    def __init__(self):
        self.defs = {}
        self.out = []
        self.box = None
        self.n = 0
        self.paths = {}

    def uid(self, p="c"):
        self.n += 1
        return f"{p}{self.n}"


PG = Page()


def begin():
    global PG
    PG = Page()
    _STACK[:] = [Mat()]


def emit(s):
    PG.out.append(s)


def grow(x0, y0, x1, y1):
    if PG.box is None:
        PG.box = [x0, y0, x1, y1]
    else:
        b = PG.box
        b[0], b[1], b[2], b[3] = min(b[0], x0), min(b[1], y0), max(b[2], x1), max(b[3], y1)


def grow_path(p, pad=0, dx=0, dy=0):
    x0, y0, x1, y1 = p.bbox()
    grow(x0 - pad + dx, y0 - pad + dy, x1 + pad + dx, y1 + pad + dy)


def defadd(key, svg):
    PG.defs.setdefault(key, svg)
    return f"url(#{key})"


@contextlib.contextmanager
def group(opacity=None, clip=None):
    attrs = ""
    if opacity is not None:
        attrs += f' opacity="{opacity}"'
    if clip is not None:
        cid = PG.uid("k")
        PG.defs[cid] = f'<clipPath id="{cid}"><path d="{clip.d()}"/></clipPath>'
        attrs += f' clip-path="url(#{cid})"'
    emit(f"<g{attrs}>")
    try:
        yield
    finally:
        emit("</g>")


# ---------------------------------------------------------------- paints
def cg(color, inv=False):
    """Clay fill: light top left, the colour in the middle, a little deeper bottom right."""
    k = ("cgi" if inv else "cg") + color[1:]
    if inv:   # a hollow: dark top left, light bottom right
        a, m, b = dk(color, .16), color, lt(color, .12)
        return defadd(k, f'<radialGradient id="{k}" cx="58%" cy="62%" r="72%" fx="66%" fy="70%">'
                         f'<stop offset="0" stop-color="{b}"/><stop offset=".55" stop-color="{m}"/><stop offset="1" stop-color="{a}"/></radialGradient>')
    a, b, c = lt(color, .24), dk(color, .08), dk(color, .2)
    return defadd(k, f'<radialGradient id="{k}" cx="42%" cy="38%" r="72%" fx="33%" fy="27%">'
                     f'<stop offset="0" stop-color="{a}"/><stop offset=".55" stop-color="{color}"/>'
                     f'<stop offset=".86" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></radialGradient>')


def rim(color, inv=False):
    """The rolled edge: white top left, deeper colour bottom right (inside a clip)."""
    k = ("rmi" if inv else "rm") + color[1:]
    d = dk(color, .42)
    if inv:
        return defadd(k, f'<linearGradient id="{k}" x1=".15" y1=".1" x2=".85" y2=".95">'
                         f'<stop offset="0" stop-color="{d}" stop-opacity=".6"/><stop offset=".45" stop-color="{d}" stop-opacity="0"/>'
                         f'<stop offset=".6" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="1" stop-color="#FFFFFF" stop-opacity=".55"/></linearGradient>')
    return defadd(k, f'<linearGradient id="{k}" x1=".12" y1=".08" x2=".88" y2=".95">'
                     f'<stop offset="0" stop-color="#FFFFFF" stop-opacity=".62"/><stop offset=".38" stop-color="#FFFFFF" stop-opacity="0"/>'
                     f'<stop offset=".52" stop-color="{d}" stop-opacity=".08"/><stop offset="1" stop-color="{d}" stop-opacity=".62"/></linearGradient>')


def softg(color, hard=.5):
    """Radial gradient: full colour in the middle fading to nothing at the edge."""
    k = f"sg{color[1:]}_{int(hard * 100)}"
    return defadd(k, f'<radialGradient id="{k}"><stop offset="0" stop-color="{color}"/>'
                     f'<stop offset="{hard}" stop-color="{color}" stop-opacity=".7"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')


def _h(x):
    return hashlib.md5(repr(x).encode()).hexdigest()[:7]


def lin(stops, x1=0, y1=0, x2=0, y2=1, key=None):
    """Linear gradient (objectBoundingBox) from a list of (offset, colour[, opacity])."""
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    k = key or "lg" + _h((stops, x1, y1, x2, y2))
    return defadd(k, f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')


def rad(stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, key=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    foc = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    k = key or "rg" + _h((stops, cx, cy, r, fx, fy))
    return defadd(k, f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}"{foc}>{s}</radialGradient>')


# ---------------------------------------------------------------- primitives
def fill(p, paint, opacity=None, box=True, extra=""):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    emit(f'<path d="{p.d()}" fill="{paint}"{op}{extra}/>')
    if box:
        grow_path(p)


def stroke(p, color, w, opacity=None, cap="round", box=True, dx=0, dy=0):
    """w is in local units (scaled by the current transform)."""
    ww = w * S()
    op = f' opacity="{opacity}"' if opacity is not None else ""
    emit(f'<path d="{p.d(dx, dy)}" fill="none" stroke="{color}" stroke-width="{f(ww) if ww >= .95 else round(ww, 2)}" '
         f'stroke-linecap="{cap}" stroke-linejoin="round"{op}/>')
    if box:
        grow_path(p, ww / 2, dx, dy)


def depth_of(p, depth=None):
    x0, y0, x1, y1 = p.bbox()
    m = min(x1 - x0, y1 - y0)
    return depth * S() if depth else max(.8, min(m * .11, 34))


def _sw(w):
    return f(w) if w >= .95 else str(round(w, 2))


def pathref(p):
    """Put the shape in <defs> once; pieces draw it again with <use>, which keeps files small."""
    d = p.d()
    key = PG.paths.get(d)
    if key is None:
        key = PG.uid("p")
        PG.paths[d] = key
        PG.defs[key] = f'<path id="{key}" d="{d}"/>'
    return key


def drop(p, b, opacity=1.0, dx=None, dy=None, ref=None):
    """Soft shadow of a shape, down and to the right: fatter, fainter copies make the edge fade."""
    dx = b * .3 if dx is None else dx
    dy = b * .75 if dy is None else dy
    ref = ref or pathref(p)
    for w, op in ((b * 1.7, .035), (b * 1.2, .04), (b * .75, .045), (b * .35, .05), (0, .055)):
        st = f' stroke="{SHADOW}" stroke-width="{_sw(w)}" stroke-linejoin="round"' if w else ""
        emit(f'<use href="#{ref}" x="{f(dx)}" y="{f(dy)}" fill="{SHADOW}"{st} opacity="{round(op * opacity, 3)}"/>')
    grow_path(p, b * .85, dx, dy)


def clay(p, color, depth=None, shadow=True, inv=False, shine=True, edge=True, dents=(), opacity=None, sh_op=1.0):
    """One clay piece. depth: how round the edge is (local units; default from size)."""
    b = depth_of(p, depth)
    ref = pathref(p)
    if opacity is not None:
        emit(f'<g opacity="{opacity}">')
    if shadow:
        drop(p, b, sh_op, ref=ref)
    emit(f'<use href="#{ref}" fill="{cg(color, inv)}"/>')
    grow_path(p)
    if edge:
        cid = "k" + ref
        PG.defs.setdefault(cid, f'<clipPath id="{cid}"><use href="#{ref}"/></clipPath>')
        r = rim(color, inv)
        lay = ((b * 2.6, .32), (b * 1.9, .34), (b * 1.25, .36), (b * .65, .4)) if b > 2.5 else ((b * 2, .5), (b * .9, .55))
        emit(f'<g clip-path="url(#{cid})">' + "".join(
            f'<use href="#{ref}" fill="none" stroke="{r}" stroke-width="{_sw(w)}" opacity="{op}"/>' for w, op in lay) + "</g>")
    if shine and not inv:
        x0, y0, x1, y1 = p.bbox()
        w, h = x1 - x0, y1 - y0
        spot(x0 + w * .3, y0 + h * .26, max(w * .13, 1), max(h * .07, .6), -35, .5, local=False)
    for dn in dents:
        dent(*dn)
    if opacity is not None:
        emit("</g>")


def flat(p, color, opacity=None):
    """A piece with the clay gradient only (small bits: seeds, crumbs)."""
    fill(p, cg(color), opacity)


def spot(cx, cy, rx, ry, rot=0, op=.5, color="#FFFFFF", local=True, hard=.35, box=False):
    """A soft-edged ellipse (shine, blush, glow). local: cx.. are in the current transform."""
    if local:
        p = ellipse(cx, cy, rx, ry, rot)
    else:
        with at():
            _STACK.append(Mat())
            p = ellipse(cx, cy, rx, ry, rot)
            _STACK.pop()
    emit(f'<path d="{p.d()}" fill="{softg(color, hard)}" opacity="{op}"/>')
    if box:
        grow_path(p)


def contact(cx, cy, rx, ry, op=.32):
    """A soft shadow on the ground under a thing that stands there."""
    p = ellipse(cx, cy, rx, ry)
    emit(f'<path d="{p.d()}" fill="{softg(SHADOW, .25)}" opacity="{op}"/>')
    grow_path(p)


def dent(cx, cy, r, rot=0, op=.8):
    """A shallow thumbprint: darker upper-left rim, lighter lower-right, faint ridges."""
    g = defadd("dentg", '<radialGradient id="dentg" cx="50%" cy="50%" r="50%" fx="64%" fy="68%">'
                        '<stop offset="0" stop-color="#fff" stop-opacity=".24"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>'
                        '<stop offset=".86" stop-color="#2A140A" stop-opacity=".16"/><stop offset="1" stop-color="#2A140A" stop-opacity="0"/></radialGradient>')
    p = ellipse(cx, cy, r, r * .8, rot)
    s = f'<g opacity="{op}"><path d="{p.d()}" fill="{g}"/>'
    for k in (.38, .62):
        q = ellipse(cx + r * .08, cy + r * .1, r * k, r * k * .78, rot)
        s += f'<path d="{q.d()}" fill="none" stroke="#fff" stroke-opacity=".12" stroke-width="{f(max(.4, r * .07 * S()))}"/>'
    emit(s + "</g>")


def worm(p, color, w, shadow=True, shine=True, box=True):
    """A rolled clay rope along an open path (mouths, handles, arrows). w in local units."""
    ww = w * S()
    if shadow:
        stroke(p, SHADOW, w * 1.15, .16, box=box, dx=ww * .12, dy=ww * .3)
    stroke(p, color, w, box=box)
    stroke(p, dk(color, .3), w * .55, .35, box=False, dx=ww * .1, dy=ww * .16)
    stroke(p, color, w * .55, box=False, dx=-ww * .04, dy=-ww * .06)
    if shine:
        stroke(p, lt(color, .55), w * .26, .7, box=False, dx=-ww * .14, dy=-ww * .2)


def eye(cx, cy, rx, ry, color="#2B1B12"):
    """A shiny clay bead eye."""
    clay(ellipse(cx, cy, rx, ry), color, shadow=True, shine=False, edge=False, depth=max(rx, ry) * .25)
    fill(circle(cx - rx * .32, cy - ry * .36, rx * .36), "#FFFFFF")
    fill(circle(cx + rx * .3, cy + ry * .3, rx * .14), "#FFFFFF", .8)


def bubbles(lst):
    """See-through soap or water bubbles: (x, y, r) in local units."""
    g = defadd("bub", '<radialGradient id="bub" cx="50%" cy="50%" r="50%" fx="38%" fy="34%"><stop offset="0" stop-color="#fff" stop-opacity=".2"/>'
                      '<stop offset=".7" stop-color="#D8F3FF" stop-opacity=".4"/><stop offset="1" stop-color="#7FCDF2" stop-opacity=".95"/></radialGradient>')
    for x, y, r in lst:
        fill(circle(x, y, r), g)
        a0, a1 = math.radians(200), math.radians(260)
        arc = Path().M(x + r * .62 * math.cos(a0), y + r * .62 * math.sin(a0)).Q(
            x + r * .9 * math.cos((a0 + a1) / 2), y + r * .9 * math.sin((a0 + a1) / 2), x + r * .62 * math.cos(a1), y + r * .62 * math.sin(a1))
        stroke(arc, "#FFFFFF", max(r * .2, .8), box=False)


def sparkle(x, y, r, color="#FFE27A", op=1):
    """A four-point twinkle."""
    pts = star_pts(r, r * .32, 4, x, y, -90)
    clay(rpoly(pts, r * .08), color, depth=r * .2, shadow=False, opacity=op if op != 1 else None)


# ---------------------------------------------------------------- saving
def svg_text(w, h, tx=0, ty=0, bg=None):
    body = "".join(PG.out)
    back = f'<rect width="{f(w)}" height="{f(h)}" fill="{bg}"/>' if bg else ""
    tr = f'<g transform="translate({f(-tx)} {f(-ty)})">' if (tx or ty) else "<g>"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(w)}" height="{f(h)}" viewBox="0 0 {f(w)} {f(h)}">'
            f'<defs>{"".join(PG.defs.values())}</defs>{back}{tr}{body}</g></svg>\n')


def save(rel, rest=False, margin=4, square=False, box=None, bottom=None, bg=None):
    """Write the page to app/assets/art/<rel>. Returns (x0, y0, w, h): where the viewBox
    sits in drawing units, so callers can turn drawing points into viewBox points.
    rest: the bottom edge is the lowest thing drawn (no margin), for things that stand.
    bottom: cut the picture flat at this y (customers behind the counter)."""
    if box is None:
        x0, y0, x1, y1 = PG.box
        x0, y0, x1 = math.floor(x0 - margin), math.floor(y0 - margin), math.ceil(x1 + margin)
        y1 = math.ceil(PG.box[3] + (0 if rest else margin))
        if bottom is not None:
            y1 = bottom
        if square:
            w, h = x1 - x0, y1 - y0
            if w > h:
                d = w - h
                y0 -= d // 2 if bottom is None and not rest else d
                y1 = y0 + w
            else:
                d = h - w
                x0 -= d // 2
                x1 = x0 + h
    else:
        x0, y0, w_, h_ = box
        x1, y1 = x0 + w_, y0 + h_
    w, h = x1 - x0, y1 - y0
    out = ART / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg_text(w, h, x0, y0, bg))
    return x0, y0, w, h

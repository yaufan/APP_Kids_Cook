"""動物小餐廳's app icon: the bear chef (customers.py's bear in a chef hat)
holding up a little pan with a sunny-side-up egg, on a warm peach background
with soft clay shading.

    python3 icon.py preview out.png   # a sheet: round / squircle / square masks at 48, 96 and 192 px, and a big one
    python3 icon.py export            # writes the Android and iOS icons into app/

export writes
- Android, full square art: app/android/app/src/main/res/mipmap-{mdpi..xxxhdpi}/ic_launcher.png (48..192 px).
- Android adaptive icon (API 26+): mipmap-anydpi-v26/ic_launcher.xml, with
  drawable-{mdpi..xxxhdpi}/ic_launcher_foreground.png and ic_launcher_background.png
  (108 dp canvas; the bear and pan stay inside the central 66 dp circle).
- iOS: every PNG listed in app/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json,
  at its size, opaque (no alpha).
Needs Node.js with Playwright (Chromium draws the SVGs) and Pillow.
"""
import json
import math
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

import clay as kit
import customers
from clay import (PAN, WHITE, YOLK, at, begin, capsule, circle, clay, dk, ellipse, lin, lt, parse, rad, rrect, spot)

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = ROOT / "app"
RES = APP / "android" / "app" / "src" / "main" / "res"
IOS = APP / "ios" / "Runner" / "Assets.xcassets" / "AppIcon.appiconset"
RENDER = HERE / "render_alpha.js"

C = 1024
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
EGG_WHITE = "M -30 -6 C -34 -26 -12 -34 4 -30 C 22 -34 36 -18 32 0 C 38 18 22 34 2 31 C -16 36 -36 22 -30 -6 Z"


# ---------------------------------------------------------------- the drawing (local units, the bear head is about 130 wide)
def subject():
    # a round clay bust in the teal shirt, a white collar and the bow tie
    clay(parse("M -66 64 C -86 78 -96 108 -96 128 C -96 150 -70 158 0 158 C 70 158 96 150 96 128 C 96 108 86 78 66 64 "
               "Q 0 44 -66 64 Z"), "#5FB7A6", depth=12)
    clay(parse("M -30 56 L 0 88 L 30 56 Q 0 48 -30 56 Z"), WHITE, depth=4)
    with at(0, 0, s=1.12):
        customers.bear_head(False, hat=True)
    customers.bow_tie(76)
    # the pan held up on the right: handle down into the paw
    with at(98, 46, -8):
        clay(capsule(-14, 52, -30, 84, 8.5), "#A8703F", depth=4)
        clay(rrect(-17, 40, 16, 16, 4, 30), "#8A9099", depth=2.5)
        clay(circle(0, 0, 52), PAN, depth=11)
        clay(circle(0, 0, 42), dk(PAN, .12), inv=True, shadow=False, depth=9)
        with at(0, 0, 18, s=1.05):
            clay(parse(EGG_WHITE), "#FFF8EC", depth=6)
            clay(circle(5, -3, 13), YOLK, depth=4)
            spot(1, -8, 4, 2.6, -30, .8)
    clay(ellipse(68, 128, 21, 17, -30), customers.BEAR, depth=6)
    for k in (-6, 2, 10):
        kit.stroke(parse(f"M {60 + k} 116 L {58 + k} 122"), dk(customers.BEAR, .3), 1.6, .35)


def subject_svg(px, radius):
    """The bear and pan, see-through around them, centred so the drawing reaches
    [radius] (in 1024ths) from the middle."""
    begin()
    subject()
    x0, y0, x1, y1 = kit.PG.box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = radius / math.hypot((x1 - x0) / 2, (y1 - y0) / 2) * FIT.get(radius, 1.0)
    body = "".join(kit.PG.out)
    defs = "".join(kit.PG.defs.values())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {C} {C}" width="{px}" height="{px}"><defs>{defs}</defs>'
            f'<g transform="translate({C / 2} {C / 2 + 10}) scale({s:.4f}) translate({-cx:.1f} {-cy:.1f})">{body}</g></svg>')


def background_svg(px):
    """Warm peach with a soft light behind the bear and a big, gentle clay dome."""
    begin()
    kit.emit(f'<rect width="{C}" height="{C}" fill="{rad([(0, "#FFEBD6"), (.6, "#FFD2AE"), (1, "#FFB98E")], .5, .42, .75)}"/>')
    clay(circle(C / 2, C / 2 + 20, 380), "#FFE3C9", depth=60, shine=.25, sh_op=.6)
    for x, y, r in ((170, 200, 26), (860, 230, 18), (840, 820, 24), (190, 830, 16)):
        clay(circle(x, y, r), "#FFF4E6", depth=r * .3, sh_op=.6)
    body = "".join(kit.PG.out)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {C} {C}" width="{px}" height="{px}">'
            f'<defs>{"".join(kit.PG.defs.values())}</defs>{body}</svg>')


FULL_R = 0.45 * C                 # full square art (legacy Android, iOS)
SAFE_R = 33 / 108 * C * 0.98      # adaptive foreground: the central 66 dp circle of 108 dp
FIT = {}


# ---------------------------------------------------------------- rendering
def render(svg_text, px):
    with tempfile.TemporaryDirectory() as tmp:
        src, out = pathlib.Path(tmp) / "in.svg", pathlib.Path(tmp) / "out.png"
        src.write_text(svg_text)
        subprocess.run(["node", str(RENDER), str(src), str(out), str(px), str(px)], check=True)
        return Image.open(out).convert("RGBA").copy()


def reach(img):
    a = img.getchannel("A")
    w, h = img.size
    px = a.load()
    best = 0.0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if px[x, y] > 40:
                best = max(best, math.hypot(x + 0.5 - w / 2, y + 0.5 - h / 2))
    return best


def fit():
    for radius in (FULL_R, SAFE_R):
        FIT[radius] = 1.0
        got = reach(render(subject_svg(512, radius), 512)) * C / 512
        FIT[radius] = radius / got


def full_art():
    bg = render(background_svg(C), C)
    fg = render(subject_svg(C, FULL_R), C)
    return Image.alpha_composite(bg, fg).convert("RGB")


def adaptive_layers():
    return render(background_svg(C), C).convert("RGB"), render(subject_svg(C, SAFE_R), C)


def resized(img, px):
    return img.resize((px, px), Image.LANCZOS)


def mask(kind, px):
    m = Image.new("L", (px * 4, px * 4), 0)
    dr = ImageDraw.Draw(m)
    s = px * 4
    if kind == "round":
        dr.ellipse((0, 0, s - 1, s - 1), fill=255)
    elif kind == "squircle":
        pts = []
        for i in range(720):
            t = 2 * math.pi * i / 720
            c, si = math.cos(t), math.sin(t)
            pts.append((s / 2 + s / 2 * math.copysign(abs(c) ** (2 / 5), c), s / 2 + s / 2 * math.copysign(abs(si) ** (2 / 5), si)))
        dr.polygon(pts, fill=255)
    else:
        dr.rounded_rectangle((0, 0, s - 1, s - 1), radius=s * 0.08, fill=255)
    return m.resize((px, px), Image.LANCZOS)


def preview(out):
    fit()
    full = full_art()
    bg, fg = adaptive_layers()
    adaptive = Image.alpha_composite(bg.convert("RGBA"), fg).convert("RGB")
    k = C * 18 / 108          # a launcher shows the middle 72 dp of the 108 dp canvas
    adaptive_view = adaptive.crop((round(k), round(k), round(C - k), round(C - k)))
    sizes = (48, 96, 192)
    rows = [("round", adaptive_view), ("squircle", adaptive_view), ("square", full)]
    pad = 24
    W = pad + sum(s + pad for s in sizes) + 420 + pad
    H = pad + len(rows) * (192 + pad) + 120
    sheet = Image.new("RGB", (W, H), "#E9E4DE")
    sheet.paste(Image.new("RGB", (W, 120), "#2F2B33"), (0, H - 120))
    for r, (kind, art) in enumerate(rows):
        x = pad
        y = pad + r * (192 + pad)
        for s in sizes:
            sheet.paste(resized(art, s), (x, y + 192 - s), mask(kind, s))
            x += s + pad
    sheet.paste(resized(full, 420), (W - pad - 420, pad), mask("squircle", 420))
    x = pad
    for kind, art in rows:
        sheet.paste(resized(art, 72), (x, H - 96), mask(kind, 72))
        x += 72 + pad
    sheet.save(out)
    print(out)


ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""


def export():
    fit()
    full = full_art()
    bg, fg = adaptive_layers()
    written = []
    for name, k in DENSITIES.items():
        mip = RES / f"mipmap-{name}"
        mip.mkdir(parents=True, exist_ok=True)
        resized(full, round(48 * k)).save(mip / "ic_launcher.png")
        draw = RES / f"drawable-{name}"
        draw.mkdir(parents=True, exist_ok=True)
        resized(fg, round(108 * k)).save(draw / "ic_launcher_foreground.png")
        resized(bg, round(108 * k)).save(draw / "ic_launcher_background.png")
        written += [mip / "ic_launcher.png", draw / "ic_launcher_foreground.png", draw / "ic_launcher_background.png"]
    anydpi = RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(ADAPTIVE_XML)
    written.append(anydpi / "ic_launcher.xml")
    contents = json.loads((IOS / "Contents.json").read_text())
    for image in contents["images"]:
        if not image.get("filename"):
            continue
        size = float(image["size"].split("x")[0]) * float(image["scale"].rstrip("x"))
        resized(full, round(size)).convert("RGB").save(IOS / image["filename"])
        written.append(IOS / image["filename"])
    manifest = (APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text()
    if 'android:icon="@mipmap/ic_launcher"' not in manifest:
        print("note: AndroidManifest.xml's android:icon is not @mipmap/ic_launcher")
    for p in written:
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "export":
        export()
    elif len(sys.argv) >= 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        print(__doc__)

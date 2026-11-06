"""A contact sheet of all of 動物小餐廳's art, to look at.

    python3 preview.py out.png            # everything
    python3 preview.py out.png food ui    # only some folders

Each picture sits in a cell on a soft background, scaled to fit, with its name
and size; a thin line shows the bottom of its viewBox (things that stand should
touch it). The customers are drawn with their customers.json points (mouth +,
head top x). The scenes are shown small with the counter and worktop lines.
Needs Node.js with Playwright (Chromium draws the SVGs).
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ART = ROOT / "app" / "assets" / "art"
RENDER = HERE / "render_alpha.js"
GROUPS = ["customers", "chef", "food", "tools", "ui", "dishes", "scenes"]
SHEET_W = 2400
BG = "#F6F1EA"
CELL_BG = "#FFE9D6"


def size_of(svg):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg.read_text())
    return float(m.group(1)), float(m.group(2))


def render_html(html, out, w, h):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as fh:
        fh.write(html)
    try:
        subprocess.run(["node", str(RENDER), fh.name, str(out), str(int(w)), str(int(h))], check=True)
    finally:
        pathlib.Path(fh.name).unlink()


class Sheet:
    def __init__(self):
        self.parts = []
        self.y = 20

    def raw(self, s):
        self.parts.append(s)

    def text(self, s, x, y, size=24, bold=True, color="#6B5547"):
        self.raw(f'<div style="position:absolute;left:{x}px;top:{y}px;font:{"700" if bold else "400"} {size}px sans-serif;color:{color};white-space:nowrap">{s}</div>')

    def title(self, s):
        self.text(s, 24, self.y, 30)
        self.y += 48


def cells(sh, files, cell=230, box=190, per_row=10, marks=None):
    for i, f in enumerate(files):
        vw, vh = size_of(f)
        s = min(box / vw, box / vh)
        w, h = vw * s, vh * s
        cx = 24 + (i % per_row) * cell
        cy = sh.y + (i // per_row) * (cell + 34)
        sh.raw(f'<div style="position:absolute;left:{cx}px;top:{cy}px;width:{cell - 14}px;height:{cell - 14}px;background:{CELL_BG};border-radius:18px"></div>')
        x = cx + (cell - 14 - w) / 2
        y = cy + (cell - 14 - h) / 2
        sh.raw(f'<div style="position:absolute;left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;outline:1px dashed rgba(150,110,80,.35)"></div>')
        sh.raw(f'<img src="file://{f}" style="position:absolute;left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px">')
        if marks and f.stem in marks:
            m = marks[f.stem]
            pts = "".join(f'<path d="M{p["x"] - 9} {p["y"]}h18M{p["x"]} {p["y"] - 9}v18" stroke="{c}" stroke-width="{3 / s:.1f}"/>'
                          for p, c in m)
            sh.raw(f'<svg style="position:absolute;left:{x:.1f}px;top:{y:.1f}px" width="{w:.1f}" height="{h:.1f}" viewBox="0 0 {vw} {vh}">{pts}</svg>')
        kb = f.stat().st_size / 1024
        sh.text(f"{f.stem} <span style='color:#A08C7C'>{int(vw)}×{int(vh)} · {kb:.0f}KB</span>", cx + 4, cy + cell - 10, 15, False)
    sh.y += ((len(files) + per_row - 1) // per_row) * (cell + 34) + 16


def scenes(sh):
    files = sorted((ART / "scenes").glob("*.svg"))
    if not files:
        return
    sh.title("scenes (1080×1920)")
    info = {}
    j = ART / "scenes" / "scenes.json"
    if j.exists():
        info = json.loads(j.read_text())
    k = 0.36
    w, h = 1080 * k, 1920 * k
    for i, f in enumerate(files):
        x = 24 + i * (w + 30)
        sh.raw(f'<img src="file://{f}" style="position:absolute;left:{x}px;top:{sh.y}px;width:{w}px;height:{h}px">')
        for key, val in info.get(f.stem, {}).items():
            if isinstance(val, (int, float)):
                sh.raw(f'<div style="position:absolute;left:{x}px;top:{sh.y + val * k:.1f}px;width:{w}px;border-top:2px dashed rgba(40,120,220,.7)"></div>')
        kb = f.stat().st_size / 1024
        sh.text(f"{f.stem} · {kb:.0f}KB", x, sh.y + h + 6, 18, False)
    # a customer on the restaurant counter, at 46% of the width
    if "restaurant" in info and (ART / "customers" / "bear.svg").exists():
        cw, ch = size_of(ART / "customers" / "bear.svg")
        x = 24 + 3 * (w + 30)
        sh.raw(f'<img src="file://{files[[p.stem for p in files].index("restaurant")]}" style="position:absolute;left:{x}px;top:{sh.y}px;width:{w}px;height:{h}px">')
        pw = 1080 * 0.46 * k
        ph = ch * pw / cw
        sh.raw(f'<img src="file://{ART / "customers" / "bear.svg"}" style="position:absolute;left:{x + (w - pw) / 2}px;top:{sh.y + info["restaurant"]["counterBack"] * k - ph}px;width:{pw}px;height:{ph}px">')
        sh.text("restaurant + bear", x, sh.y + h + 6, 18, False)
    sh.y += h + 50


def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "art_preview.png").resolve()
    groups = sys.argv[2:] or GROUPS
    sh = Sheet()
    for g in groups:
        if g == "scenes":
            scenes(sh)
            continue
        files = sorted((ART / g).glob("*.svg"))
        if not files:
            continue
        marks = None
        if g == "customers":
            info = json.loads((ART / g / "customers.json").read_text())
            marks = {}
            for cid, v in info.items():
                marks[cid] = [(v["mouth"], "#1E9E5A"), (v["headTop"], "#2D7FF9")]
                marks[cid + "_happy"] = [(v["mouthHappy"], "#1E9E5A"), (v["headTop"], "#2D7FF9")]
            files = [ART / g / f"{cid}{s}.svg" for cid in info for s in ("", "_happy")]
        sh.title(f"{g} ({len(files)})")
        cells(sh, files, marks=marks)
    html = (f'<html><body style="margin:0;background:{BG};width:{SHEET_W}px;height:{sh.y}px;position:relative">'
            + "".join(sh.parts) + "</body></html>")
    out.parent.mkdir(parents=True, exist_ok=True)
    render_html(html, out, SHEET_W, sh.y)
    print(out)


if __name__ == "__main__":
    main()

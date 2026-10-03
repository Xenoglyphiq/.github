#!/usr/bin/env python3
"""Xenoglyphiq brand kit builder.

Single source of truth: tokens.json. Every SVG is generated from the geometry and
color tokens; every PNG is rendered from the outlined SVG of the same asset
(rsvg_render.py, which uses the system librsvg + cairo libraries).

Usage:  python3 build.py            # writes everything next to this file
Requires: Python 3, fontTools, Pillow, librsvg-2 + cairo shared libraries.
"""
import json
import math
import os
import shutil

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

from rsvg_render import render

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "tokens.json")))
G = T["geometry"]
C = T["color"]
N = C["neutral"]
E = C["ember"]
FONT_STACK = "'Chakra Petch', sans-serif"


# ----------------------------------------------------------------------------
# Fonts: layout with GPOS pair kerning, outlines via fontTools
# ----------------------------------------------------------------------------
class Font:
    def __init__(self, path):
        self.tt = TTFont(path)
        self.upm = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.gs = self.tt.getGlyphSet()
        self.hmtx = self.tt["hmtx"].metrics
        self.cap = self.tt["OS/2"].sCapHeight / self.upm
        self.desc = -self.tt["hhea"].descent / self.upm
        self._subs = self._kern_subtables()
        self._cache = {}

    def _kern_subtables(self):
        if "GPOS" not in self.tt:
            return []
        gpos = self.tt["GPOS"].table
        idx = set()
        for fr in gpos.FeatureList.FeatureRecord:
            if fr.FeatureTag == "kern":
                idx.update(fr.Feature.LookupListIndex)
        subs = []
        for li in sorted(idx):
            lk = gpos.LookupList.Lookup[li]
            for st in lk.SubTable:
                ltype = lk.LookupType
                if ltype == 9:
                    ltype = st.ExtensionLookupType
                    st = st.ExtSubTable
                if ltype == 2:
                    subs.append((st, set(st.Coverage.glyphs), {g: i for i, g in enumerate(st.Coverage.glyphs)}))
        return subs

    def kern(self, left, right):
        key = (left, right)
        if key in self._cache:
            return self._cache[key]
        val = 0
        for st, cov, cidx in self._subs:
            if left not in cov:
                continue
            if st.Format == 1:
                ps = st.PairSet[cidx[left]]
                hit = next((p for p in ps.PairValueRecord if p.SecondGlyph == right), None)
                if hit is None:
                    continue
                val = getattr(hit.Value1, "XAdvance", 0) or 0
                break
            if st.Format == 2:
                c1 = st.ClassDef1.classDefs.get(left, 0)
                c2 = st.ClassDef2.classDefs.get(right, 0)
                rec = st.Class1Record[c1].Class2Record[c2]
                val = getattr(rec.Value1, "XAdvance", 0) or 0
                break
        self._cache[key] = val
        return val

    def layout(self, text):
        names = [self.cmap[ord(ch)] for ch in text]
        out, x = [], 0
        for i, g in enumerate(names):
            out.append((g, x))
            x += self.hmtx[g][0]
            if i + 1 < len(names):
                x += self.kern(g, names[i + 1])
        return out, x

    def width(self, text, size):
        return self.layout(text)[1] * size / self.upm

    def path(self, text, size, x, baseline):
        s = size / self.upm
        pen = SVGPathPen(self.gs)
        for g, gx in self.layout(text)[0]:
            tp = TransformPen(pen, (s, 0, 0, -s, x + gx * s, baseline))
            self.gs[g].draw(tp)
        return pen.getCommands()


WORD = Font(os.path.join(HERE, T["type"]["wordmark"]["file"]))
TAG = Font(os.path.join(HERE, T["type"]["tagline"]["file"]))


# ----------------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------------
def f(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def hex_points(cx, cy, r):
    pts = []
    for k in range(6):
        a = math.radians(-90 + 60 * k)
        pts.append("%s,%s" % (f(cx + r * math.cos(a)), f(cy + r * math.sin(a))))
    return " ".join(pts)


def hexagon(cx, cy, r, stroke, color, cls=None, extra=""):
    c = (' class="%s"' % cls) if cls else ""
    col = "" if cls else ' stroke="%s"' % color
    return ('<polygon%s points="%s" fill="none"%s stroke-width="%s" stroke-linejoin="round"%s/>'
            % (c, hex_points(cx, cy, r), col, f(stroke), extra))


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))


def chain_colors(n, theme="light"):
    """Back-to-front colors for a chain of n hexes."""
    if n == 3:
        cols = [E["amber"], E["rose"], E["wine"]]
    elif n == 4:
        cols = list(C["ember_4"])
    else:
        cols = []
        for i in range(n):
            t = i / (n - 1)
            cols.append(mix(E["amber"], E["rose"], t * 2) if t <= 0.5 else mix(E["rose"], E["wine"], (t - 0.5) * 2))
    return cols if theme == "light" else list(reversed(cols))


def mark_elems(cx, cy, scale, colors, small=False, classes=None, geo=None, weave=False, uid="m"):
    """The mark: len(colors) hexes on a diagonal, back copies up-right.

    weave=True (one-color versions): each hex hides whatever sits behind it
    (with a small gap), so the stack reads as layers without color.
    """
    geo = geo or (G["small"] if small else G)
    r, step, sw = geo["hex_radius"], geo["step"], geo["stroke"]
    n = len(colors)
    hexes = []
    for i in range(n):
        k = (n - 1) / 2 - i
        hexes.append((cx + k * step * scale, cy - k * step * scale))
    out, defs = [], []
    gap = G["mono_weave"]["gap_ratio"] * sw * scale
    for i, col in enumerate(colors):
        extra = ""
        if weave and i < n - 1:
            mid = "%s-weave-%d" % (uid, i)
            cut = "".join('<polygon points="%s" fill="black" stroke="black" stroke-width="%s" stroke-linejoin="round"/>'
                          % (hex_points(x, y, r * scale), f(sw * scale + 2 * gap)) for x, y in hexes[i + 1:])
            defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-10000" y="-10000" width="20000" height="20000">'
                        '<rect x="-10000" y="-10000" width="20000" height="20000" fill="white"/>%s</mask>' % (mid, cut))
            extra = ' mask="url(#%s)"' % mid
        x, y = hexes[i]
        out.append(hexagon(x, y, r * scale, sw * scale, col, classes[i] if classes else None, extra))
    if defs:
        out.insert(0, "<defs>%s</defs>" % "".join(defs))
    return "\n".join(out)


def display_chain(front, radius, colors):
    """Large display chain. Front hex at `front`, back copies step up-right."""
    step = G["display_chain"]["step_ratio"] * radius
    sw = G["display_chain"]["stroke_ratio"] * radius
    n = len(colors)
    out = []
    for i, col in enumerate(colors):
        k = n - 1 - i
        out.append(hexagon(front[0] + k * step, front[1] - k * step, radius, sw, col))
    return "\n".join(out)


def svg_doc(w, h, body, title, vb=None, bg=None, extra_defs=""):
    vb = vb or (0, 0, w, h)
    bgrect = ('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>\n' % (f(vb[0]), f(vb[1]), f(vb[2]), f(vb[3]), bg)) if bg else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="%s" role="img">\n'
            '<title>%s</title>\n%s%s%s\n</svg>\n'
            % (f(w), f(h), " ".join(f(v) for v in vb), title, extra_defs, bgrect, body))


def text_live(text, font_weight, size, x, baseline, color, anchor="start"):
    a = '' if anchor == "start" else ' text-anchor="%s"' % anchor
    return ('<text x="%s" y="%s" font-family="%s" font-weight="%d" font-size="%s" fill="%s"%s '
            'style="font-synthesis:none">%s</text>' % (f(x), f(baseline), FONT_STACK, font_weight, f(size), color, a, text))


def text_outlined(font, text, size, x, baseline, color, cls=None):
    c = (' class="%s"' % cls) if cls else ' fill="%s"' % color
    return '<path%s d="%s"/>' % (c, font.path(text, size, x, baseline))


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(content)
    return full


def png(svg_text, path, w, h):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    render(svg_text, full, int(round(w)), int(round(h)))
    return full


OUT = HERE  # assets are written next to build.py (the brand/ folder)
NAME, TAGLINE = T["name"], T["tagline"]
THEMES = {
    "light": dict(text=N["ink"], soft=N["ink_soft"], bg=N["paper"]),
    "dark": dict(text=N["on_night"], soft=N["on_night_soft"], bg=N["night"]),
}


# ----------------------------------------------------------------------------
# Mark
# ----------------------------------------------------------------------------
def build_mark():
    vb = G["mark_viewbox"]
    variants = {
        "xenoglyphiq-mark": (chain_colors(3, "light"), "Xenoglyphiq mark, for light backgrounds"),
        "xenoglyphiq-mark-dark": (chain_colors(3, "dark"), "Xenoglyphiq mark, for dark backgrounds"),
        "xenoglyphiq-mark-mono-ink": ([N["ink"]] * 3, "Xenoglyphiq mark, one color ink"),
        "xenoglyphiq-mark-mono-white": ([N["white"]] * 3, "Xenoglyphiq mark, one color white (knockout)"),
    }
    for name, (cols, title) in variants.items():
        svg = svg_doc(vb[2], vb[3], mark_elems(0, 0, 1, cols, weave="mono" in name), title, vb=vb)
        write("mark/%s.svg" % name, svg)
        for px in (256, 512, 1024):
            png(svg, "mark/png/%s-%d.png" % (name, px), px, px)

    # Knockout tiles: mark reversed out of a solid field
    for name, field, cols in (
        ("xenoglyphiq-mark-knockout-wine", E["wine"], [N["white"]] * 3),
        ("xenoglyphiq-mark-knockout-night", N["night"], chain_colors(3, "dark")),
    ):
        body = ('<rect x="-60" y="-60" width="120" height="120" rx="26" fill="%s"/>\n' % field
                + mark_elems(0, 0, 0.82, cols, weave=len(set(cols)) == 1))
        svg = svg_doc(120, 120, body, "Xenoglyphiq mark knocked out of a %s tile" % name.split("-")[-1], vb=(-60, -60, 120, 120))
        write("mark/%s.svg" % name, svg)
        png(svg, "mark/png/%s-512.png" % name, 512, 512)

    # Extended display chains (large surfaces only)
    for n in (4, 5, 7):
        step = G["step"]
        ext = step * (n - 1) / 2 + G["hex_radius"] + G["stroke"]
        vbn = (-ext, -ext, 2 * ext, 2 * ext)
        for theme in ("light", "dark"):
            svg = svg_doc(vbn[2], vbn[3], mark_elems(0, 0, 1, chain_colors(n, theme)),
                          "Xenoglyphiq %d-hex display chain (%s backgrounds)" % (n, theme), vb=vbn)
            write("mark/chain/xenoglyphiq-chain-%d-%s.svg" % (n, theme), svg)
            png(svg, "mark/chain/png/xenoglyphiq-chain-%d-%s-1024.png" % (n, theme), 1024, 1024)


# ----------------------------------------------------------------------------
# Lockups (A primary, F compact, C stacked)
# ----------------------------------------------------------------------------
F = 100.0  # wordmark font size in SVG units; everything else scales from it


def lockup_layout(kind):
    L = T["lockups"][kind]
    pad = L["padding"] * F
    mh = L["mark_box"] * F
    scale = mh / G["mark_viewbox"][2]
    ww = WORD.width(NAME, F)
    if kind == "primary":
        ts = L["tagline_size"] * F
        tw = TAG.width(TAGLINE, ts)
        cy = pad + mh / 2
        block = WORD.cap * F + L["tagline_baseline"] * F
        base = cy - block / 2 + WORD.cap * F
        tx = pad + mh + L["gap"] * F
        W = tx + max(ww, tw) + pad
        H = mh + 2 * pad
        return dict(W=W, H=H, mark=(pad + mh / 2, cy, scale),
                    word=(tx, base), tag=(tx, base + L["tagline_baseline"] * F, ts))
    if kind == "compact":
        cy = pad + mh / 2
        base = cy + WORD.cap * F / 2
        tx = pad + mh + L["gap"] * F
        return dict(W=tx + ww + pad, H=mh + 2 * pad, mark=(pad + mh / 2, cy, scale), word=(tx, base), tag=None)
    if kind == "stacked":
        ts = L["tagline_size"] * F
        tw = TAG.width(TAGLINE, ts)
        W = max(mh, ww, tw) + 2 * pad
        cx = W / 2
        base = pad + mh + L["gap"] * F + WORD.cap * F
        tb = base + L["tagline_baseline"] * F
        H = tb + TAG.desc * ts + pad
        return dict(W=W, H=H, mark=(cx, pad + mh / 2, scale), word=(cx - ww / 2, base),
                    tag=(cx - tw / 2, tb, ts), center=cx)
    raise ValueError(kind)


def lockup_svg(kind, theme, outlined):
    lay = lockup_layout(kind)
    th = THEMES[theme]
    mx, my, ms = lay["mark"]
    parts = [mark_elems(mx, my, ms, chain_colors(3, theme))]
    wx, wb = lay["word"]
    if outlined:
        parts.append(text_outlined(WORD, NAME, F, wx, wb, th["text"]))
    elif kind == "stacked":
        parts.append(text_live(NAME, 500, F, lay["center"], wb, th["text"], "middle"))
    else:
        parts.append(text_live(NAME, 500, F, wx, wb, th["text"]))
    if lay["tag"]:
        tx, tb, ts = lay["tag"]
        if outlined:
            parts.append(text_outlined(TAG, TAGLINE, ts, tx, tb, th["soft"]))
        elif kind == "stacked":
            parts.append(text_live(TAGLINE, 400, ts, lay["center"], tb, th["soft"], "middle"))
        else:
            parts.append(text_live(TAGLINE, 400, ts, tx, tb, th["soft"]))
    title = "%s lockup (%s), for %s backgrounds" % (NAME, T["lockups"][kind]["label"], theme)
    return svg_doc(lay["W"], lay["H"], "\n".join(parts), title), lay


def build_lockups():
    for kind in ("primary", "compact", "stacked"):
        for theme in ("light", "dark"):
            base = "lockups/xenoglyphiq-lockup-%s-%s" % (kind, theme)
            live, lay = lockup_svg(kind, theme, outlined=False)
            outl, _ = lockup_svg(kind, theme, outlined=True)
            write(base + ".svg", live)
            write(base + "-outlined.svg", outl)
            png(outl, "lockups/png/xenoglyphiq-lockup-%s-%s@2x.png" % (kind, theme), lay["W"] * 2, lay["H"] * 2)


# ----------------------------------------------------------------------------
# Banners: GitHub profile (light/dark), Twitter header, social preview
# ----------------------------------------------------------------------------
def banner_svg(spec, theme, outlined=True):
    th = THEMES[theme]
    W, H = spec["size"]
    parts = [display_chain(spec["chain"]["front_center"], spec["chain"]["radius"],
                           chain_colors(spec["chain"]["count"], theme))]
    mc, msc = spec["mark"]["center"], spec["mark"]["scale"]
    parts.append(mark_elems(mc[0], mc[1], msc, chain_colors(3, theme)))
    w, t = spec["wordmark"], spec["tagline"]
    if outlined:
        parts.append(text_outlined(WORD, NAME, w["size"], w["x"], w["baseline"], th["text"]))
        parts.append(text_outlined(TAG, TAGLINE, t["size"], t["x"], t["baseline"], th["soft"]))
    else:
        parts.append(text_live(NAME, 500, w["size"], w["x"], w["baseline"], th["text"]))
        parts.append(text_live(TAGLINE, 400, t["size"], t["x"], t["baseline"], th["soft"]))
    return svg_doc(W, H, "\n".join(parts), "%s, %s" % (NAME, TAGLINE), bg=th["bg"])


def build_banners():
    B = T["banners"]
    jobs = [("github", "github-banner"), ("twitter", "twitter-header"), ("social_preview", "social-preview")]
    for key, fname in jobs:
        spec = B[key]
        for theme in ("light", "dark"):
            outl = banner_svg(spec, theme, True)
            write("banners/%s-%s.svg" % (fname, theme), outl)
            write("banners/%s-%s-live.svg" % (fname, theme), banner_svg(spec, theme, False))
            png(outl, "banners/png/%s-%s.png" % (fname, theme), *spec["size"])


# ----------------------------------------------------------------------------
# Icons: avatars, app icons, favicons
# ----------------------------------------------------------------------------
def icon_svg(px, theme, radius_ratio, fill_ratio):
    """Square icon at `px` pixels. Small sizes switch to the optical small cut."""
    small = px <= G["small"]["max_px"]
    tiny = px <= G["tiny"]["max_px"]
    th = THEMES[theme]
    S = 120.0
    rx = S * radius_ratio
    body = '<rect x="0" y="0" width="%s" height="%s" rx="%s" fill="%s"/>\n' % (f(S), f(S), f(rx), th["bg"])
    scale = S * fill_ratio / G["mark_viewbox"][2]
    if tiny:
        cols = chain_colors(3, theme)[-G["tiny"]["count"]:]
        body += mark_elems(S / 2, S / 2, scale, cols, geo=G["tiny"])
    else:
        body += mark_elems(S / 2, S / 2, scale, chain_colors(3, theme), small=small)
    return svg_doc(px, px, body, "%s icon" % NAME, vb=(0, 0, S, S))


def build_icons():
    for theme in ("light", "dark"):
        svg = icon_svg(500, theme, 0, 0.66)
        write("icons/avatar-%s.svg" % theme, svg)
        png(svg, "icons/avatar-%s-500.png" % theme, 500, 500)
    for px in (1024, 512, 192, 180):
        svg = icon_svg(px, "dark", 0, 0.66)
        name = "apple-touch-icon" if px == 180 else "icon-%d" % px
        png(svg, "icons/%s.png" % name, px, px)
    write("icons/icon-dark.svg", icon_svg(512, "dark", 0, 0.66))
    write("icons/icon-light.svg", icon_svg(512, "light", 0, 0.66))
    frames = []
    for px in (16, 32, 48, 64):
        svg = icon_svg(px, "dark", 0.22, 0.9)
        p = png(svg, "icons/favicon-%d.png" % px, px, px)
        frames.append(Image.open(p).convert("RGBA"))
    write("icons/favicon-small-cut.svg", icon_svg(32, "dark", 0.22, 0.9))
    frames[2].save(os.path.join(OUT, "icons/favicon.ico"), format="ICO",
                   sizes=[(16, 16), (32, 32), (48, 48)], append_images=[frames[0], frames[1]])


# ----------------------------------------------------------------------------
# Web: adaptive SVGs, CSS tokens, head snippet, manifest
# ----------------------------------------------------------------------------
ADAPTIVE_CSS = """<style>
  .h0 { stroke: %(amber)s } .h1 { stroke: %(rose)s } .h2 { stroke: %(wine)s }
  .tx { fill: %(ink)s } .ts { fill: %(soft)s }
  @media (prefers-color-scheme: dark) {
    .h0 { stroke: %(wine)s } .h2 { stroke: %(amber)s }
    .tx { fill: %(on)s } .ts { fill: %(onsoft)s }
  }
</style>
""" % dict(amber=E["amber"], rose=E["rose"], wine=E["wine"], ink=N["ink"], soft=N["ink_soft"],
           on=N["on_night"], onsoft=N["on_night_soft"])


def build_web():
    vb = G["mark_viewbox"]
    cls = ["h0", "h1", "h2"]
    write("web/xenoglyphiq-mark-adaptive.svg",
          svg_doc(vb[2], vb[3], mark_elems(0, 0, 1, [None] * 3, classes=cls), "%s mark" % NAME, vb=vb, extra_defs=ADAPTIVE_CSS))
    write("web/favicon.svg",
          svg_doc(32, 32, mark_elems(0, 0, 1, [None] * 3, small=True, classes=cls), "%s" % NAME, vb=vb, extra_defs=ADAPTIVE_CSS))
    write("web/xenoglyphiq-mark-currentcolor.svg",
          svg_doc(vb[2], vb[3], mark_elems(0, 0, 1, ["currentColor"] * 3, weave=True), "%s mark" % NAME, vb=vb))
    lay = lockup_layout("primary")
    mx, my, ms = lay["mark"]
    body = [mark_elems(mx, my, ms, [None] * 3, classes=cls),
            text_outlined(WORD, NAME, F, lay["word"][0], lay["word"][1], None, cls="tx")]
    tx, tb, ts = lay["tag"]
    body.append(text_outlined(TAG, TAGLINE, ts, tx, tb, None, cls="ts"))
    write("web/xenoglyphiq-lockup-primary-adaptive.svg",
          svg_doc(lay["W"], lay["H"], "\n".join(body), "%s, %s" % (NAME, TAGLINE), extra_defs=ADAPTIVE_CSS))

    css = [":root {"]
    for k, v in E.items():
        css.append("  --xg-%s: %s;" % (k, v))
    for i, v in enumerate(C["ember_4"]):
        css.append("  --xg-ember4-%d: %s;" % (i + 1, v))
    for k, v in N.items():
        css.append("  --xg-%s: %s;" % (k.replace("_", "-"), v))
    css += ["  --xg-bg: var(--xg-paper);", "  --xg-text: var(--xg-ink);", "  --xg-text-soft: var(--xg-ink-soft);",
            "  --xg-font: 'Chakra Petch', system-ui, sans-serif;", "}",
            "@media (prefers-color-scheme: dark) {",
            "  :root { --xg-bg: var(--xg-night); --xg-text: var(--xg-on-night); --xg-text-soft: var(--xg-on-night-soft); }",
            "}", ""]
    for w, fn in ((400, "Regular"), (500, "Medium"), (600, "SemiBold")):
        css += ["@font-face {", "  font-family: 'Chakra Petch';", "  font-weight: %d;" % w, "  font-style: normal;",
                "  font-display: swap;", "  src: url('../fonts/ChakraPetch-%s.ttf') format('truetype');" % fn, "}"]
    css += ["", "html { font-synthesis: none; }", ""]
    write("web/brand.css", "\n".join(css))

    write("web/site.webmanifest", json.dumps({
        "name": NAME, "short_name": NAME, "description": TAGLINE,
        "icons": [{"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": N["night"], "background_color": N["night"], "display": "standalone"}, indent=2) + "\n")
    write("web/head-snippet.html", "\n".join([
        '<!-- Xenoglyphiq: paste into <head>; adjust paths to where you serve the files -->',
        '<link rel="icon" href="/favicon.ico" sizes="48x48">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">',
        '<link rel="manifest" href="/site.webmanifest">',
        '<meta name="theme-color" content="%s" media="(prefers-color-scheme: light)">' % N["paper"],
        '<meta name="theme-color" content="%s" media="(prefers-color-scheme: dark)">' % N["night"],
        '<meta property="og:image" content="/social-preview-dark.png">',
        '<meta name="twitter:card" content="summary_large_image">', ""]))


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    build_mark()
    build_lockups()
    build_banners()
    build_icons()
    build_web()
    print("built into", OUT)

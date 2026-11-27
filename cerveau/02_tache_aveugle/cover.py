"""Couvertures 9:16, 3:4, 16:9 de « Ton nez » : image du nez qui s'illumine + titre (même police et placement que d'habitude)."""
import os, sys, math, numpy as np, skia
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '01_nez'))
import tache as T; import nez as N
from lib import P as LP, C, rad

surf = skia.Surface(N.OW_, N.OH_); cv = surf.getCanvas(); cv.scale(N.SC, N.SC)
T.s_test(cv, 2.0, 2.0)
cv.drawRect(skia.Rect.MakeWH(N.W, N.H), LP(shader=rad(N.W / 2, N.H / 2, 1250, [C('#000000', 0), C('#000000', 0), C('#000000', 70)], [0, 0.7, 1])))
src = Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]).resize((1080, 1920), Image.LANCZOS)
FONT = N.FONT
LINES = [('IL Y A UN', '#F0EBBE'), ('TROU', '#FFE680'), ('DANS TA VISION', '#F0EBBE')]


def paint(col, stroke=None):
    p = skia.Paint(AntiAlias=True); c = col.lstrip('#'); p.setColor(skia.Color(int(c[:2], 16), int(c[2:4], 16), int(c[4:], 16)))
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def cover(w, h, name, ty, cx=0.5, maxw=0.86):
    sw, sh = src.size
    if w > h:
        bg = src.resize((w, int(sh * w / sw)), Image.LANCZOS).crop((0, int(sh * w / sw * 0.3), w, int(sh * w / sw * 0.3) + h)).filter(ImageFilter.GaussianBlur(30))
        fg = src.resize((int(sw * h / sh), h), Image.LANCZOS); bg.paste(fg, (w - fg.width - int(w * 0.06), 0)); im = bg
    else:
        s = max(w / sw, h / sh); im = src.resize((int(sw * s), int(sh * s)), Image.LANCZOS); x = (im.width - w) // 2
        y = int((im.height - h) * 0.35); im = im.crop((x, y, x + w, y + h))
    arr = np.array(im.convert('RGBA'), np.uint8, copy=True, order='C'); surf = skia.Surface(arr); cv = surf.getCanvas()
    size = min(w, h) * 0.13
    for i, (t, col) in enumerate(LINES):
        f = skia.Font(FONT, size * (1.35 if i == 1 else 1)); tw = f.measureText(t)
        if tw > maxw * w: f.setSize(f.getSize() * maxw * w / tw); tw = f.measureText(t)
        y = ty * h + i * size * 1.25 + (size * 0.2 if i == 2 else 0)
        for dx, dy, p in ((size * 0.04, size * 0.07, paint('#120624', size * 0.16)), (size * 0.04, size * 0.07, paint('#120624')), (0, 0, paint('#120624', size * 0.16)), (0, 0, paint(col))):
            cv.drawString(t, cx * w - tw / 2 + dx, y + dy, f, p)
    surf.flushAndSubmit(); Image.fromarray(arr[..., :3]).save(os.path.join(HERE, f'couverture_{name}.png'))


cover(1080, 1920, '9x16', 0.10); cover(1080, 1440, '3x4', 0.09); cover(1920, 1080, '16x9', 0.36, cx=0.3, maxw=0.48)

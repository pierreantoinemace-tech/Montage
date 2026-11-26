"""Couvertures 9:16, 3:4, 16:9 à partir d'une image du plan d'ouverture."""
import os, numpy as np, skia
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = skia.Typeface.MakeFromFile(os.path.join(HERE, '..', 'etoiles', 'fonts', 'Rubik-700.ttf'))
src = Image.open(os.path.join(HERE, 'work', 'frames', 'poignee', 'f_0120.png')).convert('RGB')
LINES = [('NOËL 1914', '#F0EBBE'), ('LA TRÊVE', '#FFE680'), ('ENTRE ENNEMIS', '#F0EBBE')]


def paint(col, stroke=None):
    p = skia.Paint(AntiAlias=True); c = col.lstrip('#'); p.setColor(skia.Color(int(c[:2], 16), int(c[2:4], 16), int(c[4:], 16)))
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def cover(w, h, name, ty, cx=0.5, maxw=0.86):
    sw, sh = src.size; s = max(w / sw, h / sh) if w < h else w / sw   # portrait : remplit ; paysage : fond flou + image nette au centre
    if w > h:
        bg = src.resize((w, int(sh * w / sw)), Image.LANCZOS).crop((0, 0, w, h)).filter(ImageFilter.GaussianBlur(30))
        fg = src.resize((int(sw * h / sh), h), Image.LANCZOS); bg.paste(fg, (w - fg.width - int(w * 0.06), 0)); im = bg
    else:
        im = src.resize((int(sw * s), int(sh * s)), Image.LANCZOS); x = (im.width - w) // 2; im = im.crop((x, int((im.height - h) * 0.35), x + w, int((im.height - h) * 0.35) + h))
    arr = np.array(im.convert('RGBA'), np.uint8, copy=True, order='C'); surf = skia.Surface(arr); cv = surf.getCanvas()
    size = min(w, h) * 0.12
    for i, (t, col) in enumerate(LINES):
        f = skia.Font(FONT, size * (1.35 if i == 1 else 1)); tw = f.measureText(t)
        if tw > maxw * w: f.setSize(f.getSize() * maxw * w / tw); tw = f.measureText(t)
        y = ty * h + i * size * 1.25 + (size * 0.2 if i == 2 else 0)
        for dx, dy, p in ((size * 0.04, size * 0.07, paint('#120624', size * 0.16)), (size * 0.04, size * 0.07, paint('#120624')), (0, 0, paint('#120624', size * 0.16)), (0, 0, paint(col))):
            cv.drawString(t, cx * w - tw / 2 + dx, y + dy, f, p)
    surf.flushAndSubmit(); Image.fromarray(arr[..., :3]).save(os.path.join(HERE, f'couverture_{name}.png'))


cover(1080, 1920, '9x16', 0.16); cover(1080, 1440, '3x4', 0.14); cover(1920, 1080, '16x9', 0.36, cx=0.3, maxw=0.48)

"""Génère les covers : cover_16x9.png (1920x1080) et cover_3x4.png (1080x1440, format grille TikTok)."""
import os, skia
import lib, scenes, render
from lib import W, H, P

def scene_layer(cls, t, d):
    sc = cls()
    s = skia.Surface(W, H); cv = s.getCanvas()
    cv.save(); cv.translate(W/2, H/2); cv.scale(1.08, 1.08); cv.translate(-W/2, -H/2)
    sc.static(cv); sc.dyn(cv, t, d); cv.restore()
    return s.makeImageSnapshot()

def text_lines(cv, lines, cx, cy, size, maxw):
    font = skia.Font(render.TYPE, size); font.setEdging(skia.Font.Edging.kAntiAlias)
    sz = min(size, min(size * maxw / font.measureText(l) for l in lines))
    font.setSize(sz)
    lh = sz * 0.98
    y0 = cy - lh * (len(lines) - 1) / 2 + sz * 0.35
    p = P('#ffffff'); p.setBlendMode(skia.BlendMode.kDifference)
    for i, l in enumerate(lines):
        cv.drawString(l, cx - font.measureText(l) / 2, y0 + i * lh, font, p)

def make(out, w, h, img, lines, size, maxw):
    s = skia.Surface(w, h); cv = s.getCanvas()
    k = max(w / W, h / H)
    cv.save(); cv.translate(w/2, h/2); cv.scale(k, k); cv.translate(-W/2, -H/2)
    cv.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear)); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(w, h), P(shader=lib.rad(w/2, h/2, max(w, h)*0.75, [lib.C('#000000', 0), lib.C('#000000', 0), lib.C('#000000', 130)], [0, .55, 1])))
    text_lines(cv, lines, w/2, h/2, size, maxw)
    s.makeImageSnapshot().save(out)

if __name__ == '__main__':
  img = scene_layer(scenes.Supernova, 1.4, 2.7)
  here = os.path.dirname(os.path.abspath(__file__))
  make(os.path.join(here, 'cover_16x9.png'), 1920, 1080, img, ["TU ES FAIT", "D'ÉTOILES", "MORTES"], 190, 1000)
  make(os.path.join(here, 'cover_3x4.png'), 1080, 1440, img, ["TU ES FAIT", "D'ÉTOILES", "MORTES"], 170, 900)
  print('ok')

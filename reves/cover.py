"""Couvertures 9:16, 3:4, 16:9 à partir de la scène d'enfance."""
import os, sys
import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('reves_video', os.path.join(HERE, 'video.py'))
V = importlib.util.module_from_spec(_s); _s.loader.exec_module(V)
import skia
from lib import P
from symboles import OUT


def title(cv, lines, cx, y, size):
    for i, (txt, col) in enumerate(lines):
        f = skia.Font(V.FONT, size); tw = f.measureText(txt)
        x, yy = cx - tw / 2, y + i * size * 1.05
        o = P(OUT, 255, stroke=size * 0.16); o.setStrokeJoin(skia.Paint.kRound_Join)
        cv.drawString(txt, x + size * 0.03, yy + size * 0.06, f, o); cv.drawString(txt, x, yy, f, o); cv.drawString(txt, x, yy, f, P(col))


LINES = [('TU VOULAIS', V.CREAM), ('DEVENIR QUOI ?', V.GOLD)]


def render(w, h, ox, oy, ty, size, name):
    surf = skia.Surface(int(w * 2), int(h * 2)); cv = surf.getCanvas(); cv.scale(2, 2)
    cv.save(); cv.translate(-ox, -oy); V.s_enfance(cv, 8.6, 8.6); cv.restore()
    title(cv, LINES, w / 2, ty, size)
    surf.makeImageSnapshot().save(os.path.join(HERE, name))


render(1080, 1920, 0, 0, 760, 120, 'cover_9x16.png')
render(1080, 1440, 0, 330, 420, 112, 'cover_3x4.png')
render(1920, 1080, -420, 560, 150, 100, 'cover_16x9.png')
print('ok')

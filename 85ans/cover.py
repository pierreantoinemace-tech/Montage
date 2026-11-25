"""Couvertures 9:16, 3:4, 16:9 : le perso à 85 ans devant la porte de lumière."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vertical'))
_s = importlib.util.spec_from_file_location('film85', os.path.join(HERE, 'film.py'))
V = importlib.util.module_from_spec(_s); _s.loader.exec_module(V)
import skia
from lib import P
V.RV.WORDS = []; V.X.WORDS = []


def title(cv, lines, cx, y, size):
    for i, (txt, col) in enumerate(lines):
        f = skia.Font(V.RV.FONT, size); tw = f.measureText(txt)
        x, yy = cx - tw / 2, y + i * size * 1.05
        o = P(V.OUT, 255, stroke=size * 0.16); o.setStrokeJoin(skia.Paint.kRound_Join)
        cv.drawString(txt, x + size * 0.03, yy + size * 0.06, f, o); cv.drawString(txt, x, yy, f, o); cv.drawString(txt, x, yy, f, P(col))


LINES = [("IMAGINE QUE T'AS", V.CREAM), ('85 ANS', V.GOLD)]


def render(w, h, ox, oy, ty, size, name, cx=None):
    surf = skia.Surface(int(w * 2), int(h * 2)); cv = surf.getCanvas(); cv.scale(2, 2)
    cv.save(); cv.translate(-ox, -oy); V.s_hook(cv, 6.0, 6.0); cv.restore()
    title(cv, LINES, cx or w / 2, ty, size)
    surf.makeImageSnapshot().save(os.path.join(HERE, name))


render(1080, 1920, 0, 0, 560, 110, 'cover_9x16.png')
render(1080, 1440, 0, 380, 220, 104, 'cover_3x4.png')
render(1920, 1080, -560, 700, 480, 92, 'cover_16x9.png', cx=470)
print('ok')

"""Couvertures : 9:16, 3:4 et 16:9 à partir de la scène d'accroche."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import video as V
import skia
from lib import P
from symboles import OUT


def title(cv, lines, cx, y, size):
    for i, (txt, col) in enumerate(lines):
        f = skia.Font(V.FONT, size); tw = f.measureText(txt)
        x, yy = cx - tw / 2, y + i * size * 1.05
        o = P(OUT, 255, stroke=size * 0.16); o.setStrokeJoin(skia.Paint.kRound_Join)
        cv.drawString(txt, x + size * 0.03, yy + size * 0.06, f, o); cv.drawString(txt, x, yy, f, o); cv.drawString(txt, x, yy, f, P(col))


LINES = [("T'ES PAS", V.CREAM), ('EN RETARD', V.GOLD)]
T = 1.0


def render(w, h, sc, ox, oy, ty, size, name):
    surf = skia.Surface(int(w * 2), int(h * 2)); cv = surf.getCanvas(); cv.scale(2, 2)
    cv.save(); cv.scale(sc, sc); cv.translate(-ox, -oy); V.s_hook(cv, T, 0); cv.restore()
    title(cv, LINES, w / 2, ty, size)
    surf.makeImageSnapshot().save(os.path.join(HERE, name))


render(1080, 1920, 1, 0, 0, 640, 165, 'cover_9x16.png')
render(1080, 1440, 1, 0, 330, 330, 150, 'cover_3x4.png')
render(1920, 1080, 1, -420, 560, 170, 120, 'cover_16x9.png')
print('ok')

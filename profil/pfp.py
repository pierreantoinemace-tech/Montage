"""Photos de profil dans le style de l'animation (TikToks × Midnight Gospel). Sortie 1080x1080."""
import math, os, random, sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('../calendrier', '../temps', '../etoiles'):
    sys.path.insert(1, os.path.join(HERE, d))
from lib import *
from kit import Stars, sparkle
from mg import *

S = 1080
ME = dict(skin='#FF8AB8', top='#2DE2C6', bottom='#8A4BFF', hair='#2A0E3A')


def burst(cv, cx, cy, cols, n=24, rot=0):
    for i in range(n):
        cv.save(); cv.translate(cx, cy); cv.rotate(rot + i * 360 / n)
        poly(cv, [(0, 0), (1200, -110), (1200, 110)], cols[i % len(cols)], 255)
        cv.restore()


def rings(cv, cx, cy):
    for i, c in enumerate(['#FF4FA8', '#FF8A1F', '#FFE04A', '#9BFF3B', '#2DE2C6', '#8A4BFF']):
        cv.drawCircle(cx, cy, 520 - i * 34, P(OL, 255, stroke=34)); cv.drawCircle(cx, cy, 520 - i * 34, P(c, 255, stroke=26))


def base(cv, seed):
    cv.drawRect(skia.Rect.MakeWH(S, S), P(shader=rad(S / 2, S / 2, S * 0.75, ['#FF8AD8', '#8A4BFF', '#2A0E5A'])))
    rnd = random.Random(seed)
    for _ in range(1500):
        circle(cv, rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(0.8, 2), '#FFFFFF', 30)


def v1(cv):
    """Le personnage, crâne ouvert sur le cosmos."""
    base(cv, 1)
    burst(cv, S / 2, S / 2, ['#FF8AD8', '#FFB0E8'], 28)
    s = 300
    x, y = S / 2, 560 + 3.6 * s
    hx, hy = x, y - 3.6 * s
    glow(cv, hx, hy - 260, 360, '#FFE680', 200)
    dude(cv, x, y, s, 0.4, mood='wow', look=(0, -0.6), blink=False, **ME)
    cv.save(); cv.clipPath(pcircle(hx, hy, s * 0.98), doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeXYWH(hx - s, hy - s, 2 * s, s * 0.74), P(shader=lin(0, hy - s, 0, hy - s * 0.26, ['#14063A', '#5A1A8A'])))
    Stars(90, 3, area=(hx - s, hy - s, hx + s, hy - s * 0.25), rmax=2.4).draw(cv, 0)
    ofill(cv, pcircle(hx - 120, hy - 230, 46), '#FFE04A'); ofill(cv, pcircle(hx + 110, hy - 200, 30), '#2DE2C6')
    cv.drawOval(skia.Rect.MakeLTRB(hx + 70, hy - 212, hx + 150, hy - 188), P(OL, 255, stroke=5))
    sparkle(cv, hx, hy - 300, 26, '#FFFFFF')
    cv.restore()
    cv.save(); cv.translate(hx + 230, hy - 380); cv.rotate(28)
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(-s, -0.75 * s, s, 1.25 * s), 180, 180); p.close()
    ofill(cv, p, ME['hair']); cv.restore()
    for i, (a, r, c) in enumerate([(-2.4, 470, '#FFE04A'), (-0.7, 480, '#2DE2C6'), (2.6, 470, '#FF4FA8'), (0.5, 480, '#9BFF3B')]):
        ofill(cv, pcircle(S / 2 + math.cos(a) * r, S / 2 + math.sin(a) * r * 0.9, 28 + 6 * i), c)


def v2(cv):
    """Gros plan du visage, anneaux arc-en-ciel et triangle à l'œil."""
    base(cv, 2)
    rings(cv, S / 2, S / 2 + 40)
    holo_triangle(cv, S / 2, 210, 120, 0.5)
    s = 280
    dude(cv, S / 2, 640 + 3.6 * s, s, 0.4, mood='happy', blink=False, **ME)
    for a, c in ((-0.4, '#FFE04A'), (3.5, '#2DE2C6')):
        sparkle(cv, S / 2 + math.cos(a) * 420, 560 + math.sin(a) * 300, 34, c)


def v3(cv):
    """Le personnage qui flotte dans un décor dense, horloge qui fond."""
    cv.drawRect(skia.Rect.MakeWH(S, S), P(shader=lin(0, 0, 0, S, ['#FF8AD8', '#FF8A1F', '#8A2A6A'])))
    rnd = random.Random(5)
    for i in range(7):
        y = 80 + i * 90
        p = skia.Path(); p.moveTo(-50, y)
        for x in range(-50, S + 100, 90):
            p.lineTo(x, y + 26 * math.sin(x * 0.006 + i))
        cv.drawPath(p, P('#FFFFFF', 34, stroke=22))
    junk_pile(cv, 7, 880, n=40, spread=(-60, S + 60), smin=0.8, smax=1.6)
    melting_clock(cv, 830, 260, 130, 1.0, drip=1.4)
    s = 220
    dude(cv, 470, 560 + 3.6 * s, s, 0.4, mood='wow', look=(0.5, -0.4), blink=False, arms='up', **ME)


if __name__ == '__main__':
    for name, fn in (('pfp_1_cosmos', v1), ('pfp_2_arc_en_ciel', v2), ('pfp_3_horloge', v3)):
        surf = skia.Surface(S * 2, S * 2)
        cv = surf.getCanvas(); cv.scale(2, 2)
        fn(cv)
        big = surf.makeImageSnapshot()
        out = skia.Surface(S, S); out.getCanvas().drawImageRect(big, skia.Rect.MakeWH(S, S), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
        out.makeImageSnapshot().save(os.path.join(HERE, name + '.png'))
        print('ok', name)

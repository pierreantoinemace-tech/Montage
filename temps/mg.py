"""Kit « Midnight Gospel × cosmique » : contours violets épais partout, dégradés granuleux,
décors denses remplis d'objets, personnages caoutchouteux aux membres « nouilles », métamorphoses."""
import math, random
import skia
from lib import *

OL = '#2A0E3A'      # couleur de contour (jamais noir pur)
OW = 7              # épaisseur de contour


def ofill(cv, path, color, a=255, w=OW, ol=OL, shade=None):
    cv.drawPath(path, P(color, a))
    if shade:
        cv.save(); cv.clipPath(path, doAntiAlias=True)
        cv.translate(shade[0], shade[1]); cv.drawPath(path, P('#000000', 0))
        cv.translate(-shade[0], -shade[1])
        r = path.computeTightBounds()
        cv.drawRect(r, P(shader=lin(r.left(), r.top(), r.right(), r.bottom(), [C('#FFFFFF', 40), C('#000000', 0), C('#000000', 70)], [0, 0.5, 1])))
        cv.restore()
    if w:
        p = P(ol, a, stroke=w)
        cv.drawPath(path, p)


def pcircle(x, y, r):
    p = skia.Path(); p.addCircle(x, y, r); return p


def poval(x, y, rx, ry):
    p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)); return p


def prr(x, y, w, h, r):
    p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return p


def ppoly(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close(); return p


def pblob(x, y, r, n=9, seed=0, wob=0.25, t=0.0):
    rnd = random.Random(seed)
    radii = [r * (1 - wob + 2 * wob * rnd.random()) for _ in range(n)]
    phs = [rnd.random() * 6.28 for _ in range(n)]
    pts = [(x + math.cos(i / n * 6.283) * radii[i] * (1 + 0.06 * math.sin(t * 1.4 + phs[i])), y + math.sin(i / n * 6.283) * radii[i] * (1 + 0.06 * math.sin(t * 1.4 + phs[i]))) for i in range(n)]
    p = skia.Path()
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    p.moveTo(*mids[-1])
    for i in range(n):
        p.quadTo(pts[i][0], pts[i][1], mids[i][0], mids[i][1])
    p.close(); return p


def noodle(cv, pts, color, w=26, ol=OL):
    p = skia.Path(); p.moveTo(*pts[0])
    if len(pts) == 3:
        p.quadTo(pts[1][0], pts[1][1], pts[2][0], pts[2][1])
    else:
        for q in pts[1:]:
            p.lineTo(*q)
    cv.drawPath(p, P(ol, 255, stroke=w + OW * 2))
    cv.drawPath(p, P(color, 255, stroke=w))


def grain_bg(cv, top, bottom, seed=0, n=2600, col='#FFFFFF', a=22):
    bg_lin(cv, top, bottom)
    rnd = random.Random(seed)
    for _ in range(n):
        circle(cv, rnd.uniform(-200, W + 200), rnd.uniform(-200, H + 200), rnd.uniform(0.8, 2.2), col, a)


PAL = ['#FF4FA8', '#FF8A1F', '#FFE04A', '#9BFF3B', '#2DE2C6', '#2DB8FF', '#8A4BFF', '#E83CFF', '#FF5A5A']


def junk(cv, kind, x, y, s, c, t=0.0, c2='#FFF6E0'):
    """Petits objets du bric-à-brac psychédélique (tous cernés)."""
    if kind == 0:   # bouteille
        ofill(cv, prr(x - 20 * s, y - 60 * s, 40 * s, 70 * s, 12 * s), c)
        ofill(cv, prr(x - 8 * s, y - 85 * s, 16 * s, 30 * s, 6 * s), c)
    elif kind == 1:  # cristal
        ofill(cv, ppoly([(x, y - 80 * s), (x + 30 * s, y - 30 * s), (x + 18 * s, y), (x - 18 * s, y), (x - 30 * s, y - 30 * s)]), c)
        cv.drawLine(x, y - 80 * s, x, y, P(OL, 120, stroke=3))
    elif kind == 2:  # œil sur pied
        noodle(cv, [(x, y), (x + 10 * s * math.sin(t + x), y - 40 * s), (x, y - 70 * s)], c, w=10 * s)
        ofill(cv, pcircle(x, y - 90 * s, 26 * s), '#FFFFFF')
        circle(cv, x + 6 * s * math.sin(t * 1.3 + y), y - 90 * s, 10 * s, OL)
    elif kind == 3:  # lampe
        ofill(cv, ppoly([(x - 34 * s, y - 60 * s), (x + 34 * s, y - 60 * s), (x + 20 * s, y - 100 * s), (x - 20 * s, y - 100 * s)]), c)
        ofill(cv, prr(x - 5 * s, y - 60 * s, 10 * s, 60 * s, 4), c2)
        glow(cv, x, y - 70 * s, 70 * s, '#FFE680', 90)
    elif kind == 4:  # sphère
        ofill(cv, pcircle(x, y - 40 * s, 40 * s), c)
        oval(cv, x - 14 * s, y - 54 * s, 12 * s, 7 * s, '#FFFFFF', 160)
    elif kind == 5:  # boîte
        ofill(cv, prr(x - 40 * s, y - 60 * s, 80 * s, 60 * s, 8 * s), c)
        cv.drawLine(x - 40 * s, y - 40 * s, x + 40 * s, y - 40 * s, P(OL, 255, stroke=4))
    elif kind == 6:  # pyramide
        ofill(cv, ppoly([(x - 50 * s, y), (x, y - 90 * s), (x + 50 * s, y)]), c)
        ofill(cv, pcircle(x, y - 40 * s, 12 * s), '#FFFFFF')
        circle(cv, x, y - 40 * s, 5 * s, OL)
    else:            # champignon
        ofill(cv, prr(x - 12 * s, y - 50 * s, 24 * s, 50 * s, 8 * s), c2)
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - 50 * s, y - 95 * s, x + 50 * s, y - 15 * s), 180, 180); p.close()
        ofill(cv, p, c)
        for k in (-20, 5, 25):
            circle(cv, x + k * s, y - 70 * s, 6 * s, '#FFFFFF')


def junk_pile(cv, seed, y0, n=60, smin=0.6, smax=1.4, t=0.0, spread=(-100, W + 100), rows=3):
    rnd = random.Random(seed)
    items = []
    for i in range(n):
        items.append((rnd.uniform(*spread), y0 + (i % rows) * 55 + rnd.uniform(-20, 20), rnd.uniform(smin, smax), rnd.randrange(8), rnd.choice(PAL)))
    for x, y, s, k, c in sorted(items, key=lambda q: q[1]):
        junk(cv, k, x, y, s, c, t)


def dude(cv, x, y, s, t, skin='#FF8AB8', top='#2DE2C6', bottom='#8A4BFF', hair='#2A0E3A', mood='calm',
         look=(0, 0), arms='down', wave=0.0, kid=False, blink=True, lid=0.0, legs='stand'):
    """Personnage caoutchouteux : grosse tête ronde, énormes yeux ronds à petites pupilles, membres nouilles.
    (x,y) = pieds ; s = rayon de la tête."""
    sw = math.sin(t * 2.2)
    by = y - (1.6 if kid else 2.2) * s
    # jambes nouilles
    if legs == 'stand':
        for k in (-1, 1):
            noodle(cv, [(x + k * 0.3 * s, by + 0.2 * s), (x + k * 0.45 * s, by + 0.7 * s * (1.4 if not kid else 1)), (x + k * 0.4 * s, y - 0.08 * s)], skin, w=0.28 * s)
            ofill(cv, poval(x + k * 0.5 * s, y - 0.05 * s, 0.28 * s, 0.13 * s), skin)
    # bras nouilles
    pose = {'down': ((-0.9, 0.9), (0.9, 0.9)), 'up': ((-1.1, -0.9), (1.1, -0.9)), 'out': ((-1.4, 0.1), (1.4, 0.1)), 'wave': ((-0.9, 0.9), (1.2, -0.9))}[arms]
    for k, (hx, hy) in zip((-1, 1), pose):
        ex, ey = x + hx * s + (0.1 * s * math.sin(t * 6) if (arms == 'wave' and k > 0) else 0), by + hy * s + 0.05 * s * sw
        noodle(cv, [(x + k * 0.45 * s, by - 0.35 * s), (x + k * 0.9 * s + 0.1 * s * sw, by + (hy * 0.2) * s), (ex, ey)], skin, w=0.22 * s)
        ofill(cv, pcircle(ex, ey, 0.16 * s), skin)
    # corps (haricot) + vêtements
    body = poval(x, by, 0.62 * s, (0.55 if kid else 0.75) * s)
    ofill(cv, body, top)
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeXYWH(x - s, by + 0.15 * s, 2 * s, 2 * s), P(bottom))
    cv.drawLine(x - s, by + 0.15 * s, x + s, by + 0.15 * s, P(OL, 255, stroke=OW))
    cv.restore()
    cv.drawPath(body, P(OL, 255, stroke=OW))
    # tête
    hx, hy = x, by - (1.15 if kid else 1.4) * s
    head = pcircle(hx, hy, s)
    ofill(cv, head, skin)
    # mèche / cheveux
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx - s, hy - s, hx + s, hy + s), 195, 150); p.quadTo(hx + 0.2 * s, hy - 0.55 * s, hx - 0.96 * s, hy - 0.26 * s); p.close()
    ofill(cv, p, hair)
    ofill(cv, pblob(hx - 0.1 * s, hy - 1.05 * s, 0.22 * s, seed=3, t=t), hair)
    # yeux énormes
    bl = 1.0
    if blink and ((t * 0.6 + x * 0.001) % 3.0) < 0.1:
        bl = 0.12
    for k in (-1, 1):
        ex, ey = hx + k * 0.36 * s, hy + 0.02 * s
        er = 0.3 * s
        if mood in ('happy', 'joy'):
            p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(ex - er * 0.8, ey - er * 0.5, ex + er * 0.8, ey + er * 0.7), 200, 140)
            cv.drawPath(p, P(OL, 255, stroke=OW * 1.2)); continue
        ofill(cv, poval(ex, ey, er, er * bl * (1.12 if mood == 'wow' else 1)), '#FFFFFF')
        if bl > 0.5:
            circle(cv, ex + look[0] * er * 0.45, ey + look[1] * er * 0.45, er * (0.18 if mood == 'wow' else 0.24), OL)
        if mood == 'tired' or lid > 0:
            lk = max(lid, 0.45 if mood == 'tired' else 0)
            cv.save(); cv.clipPath(poval(ex, ey, er, er), doAntiAlias=True)
            cv.drawRect(skia.Rect.MakeXYWH(ex - er, ey - er, 2 * er, 2 * er * lk), P(skin))
            cv.restore()
            cv.drawLine(ex - er, ey - er + 2 * er * lk, ex + er, ey - er + 2 * er * lk, P(OL, 255, stroke=OW))
    # bouche
    my = hy + 0.48 * s
    if mood in ('wow',):
        ofill(cv, poval(hx, my, 0.1 * s, 0.13 * s), '#6A1030', w=OW * 0.8)
    elif mood in ('joy',):
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx - 0.22 * s, my - 0.14 * s, hx + 0.22 * s, my + 0.16 * s), 0, 180); p.close()
        ofill(cv, p, '#6A1030', w=OW * 0.8)
    elif mood == 'sad' or mood == 'tired':
        cv.drawLine(hx - 0.12 * s, my + 0.02 * s, hx + 0.12 * s, my, P(OL, 255, stroke=OW))
    else:
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx - 0.15 * s, my - 0.1 * s, hx + 0.15 * s, my + 0.08 * s), 20, 140)
        cv.drawPath(p, P(OL, 255, stroke=OW))
    for k in (-1, 1):
        oval(cv, hx + k * 0.62 * s, hy + 0.32 * s, 0.12 * s, 0.07 * s, '#FF3B6B', 120)
    return hx, hy


def melting_clock(cv, x, y, r, t, face='#FFE680', drip=1.0, speed=1.0):
    p = skia.Path(); p.addCircle(x, y, r)
    ofill(cv, p, face)
    for k in range(5):
        dx = x - r * 0.7 + k * r * 0.35
        ln = r * (0.3 + 0.4 * ((k * 37) % 5) / 5) * drip * (1 + 0.15 * math.sin(t * 2 + k))
        d = skia.Path(); d.moveTo(dx - r * 0.13, y + r * 0.85); d.lineTo(dx - r * 0.1, y + r * 0.85 + ln)
        d.quadTo(dx, y + r * 0.95 + ln + r * 0.15, dx + r * 0.1, y + r * 0.85 + ln); d.lineTo(dx + r * 0.13, y + r * 0.85); d.close()
        ofill(cv, d, face)
    cv.drawPath(pcircle(x, y, r * 0.82), P(OL, 255, stroke=4))
    for i in range(12):
        a = i / 12 * 6.283
        circle(cv, x + math.cos(a) * r * 0.68, y + math.sin(a) * r * 0.68, r * 0.045, OL)
    for sp, ln, w in ((0.2 * speed, 0.45, 0.07), (2.4 * speed, 0.65, 0.045)):
        a = t * sp - 1.57
        noodle(cv, [(x, y), (x + math.cos(a) * r * ln, y + math.sin(a) * r * ln)], '#FF4FA8', w=r * w)
    ofill(cv, pcircle(x, y, r * 0.07), '#FF4FA8', w=4)


def holo_triangle(cv, x, y, r, t, a=255):
    """Triangle cosmique avec œil (symbole cosmique)."""
    pts = [(x, y - r), (x + r * 0.87, y + r * 0.5), (x - r * 0.87, y + r * 0.5)]
    glow(cv, x, y, r * 1.5, '#FFE6FF', 120 * a / 255)
    ofill(cv, ppoly(pts), '#FFE6FF', a=a * 0.8)
    cv.save(); cv.clipPath(ppoly(pts), doAntiAlias=True)
    for k in range(6):
        cv.drawLine(x - r, y - r + k * r * 0.3, x + r, y - r + k * r * 0.3, P('#FFB0E0', 120 * a / 255, stroke=3))
    cv.restore()
    ofill(cv, poval(x, y + r * 0.1, r * 0.3, r * 0.18 * (0.2 if (t % 3) < 0.12 else 1)), '#FFFFFF')
    circle(cv, x + r * 0.06 * math.sin(t), y + r * 0.1, r * 0.09, OL)

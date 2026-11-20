"""Photos de profil v2 : style Midnight Gospel plus sombre et onirique, personnage adulte."""
import math, os, random, sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('../calendrier', '../temps', '../etoiles'):
    sys.path.insert(1, os.path.join(HERE, d))
from lib import *
from kit import Stars, sparkle
from mg import *

S = 1080
OLD = '#120624'   # contour plus sombre pour l'ambiance nuit


def night_bg(cv, seed, top='#05020F', mid='#1A0A3A', bottom='#3A0E4A'):
    cv.drawRect(skia.Rect.MakeWH(S, S), P(shader=lin(0, 0, 0, S, [top, mid, bottom])))
    rnd = random.Random(seed)
    for _ in range(2200):
        circle(cv, rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(0.6, 1.8), '#FFFFFF', 18)
    Stars(140, seed, area=(0, 0, S, S), rmax=2.2, colors=('#ffffff', '#BFE6FF', '#FFB0E8', '#B98CFF')).draw(cv, 0.7, 220)


def mist(cv, y, col='#B98CFF', a=60):
    for k in range(4):
        cv.drawOval(skia.Rect.MakeLTRB(-200 + k * 120, y - 60 + k * 30, S + 200 - k * 80, y + 120 + k * 30), P(col, a, blur=40))


def floating_eye(cv, x, y, r, look=(0, 0), col='#FFE6FF'):
    glow(cv, x, y, r * 2.2, '#B98CFF', 90)
    ofill(cv, poval(x, y, r, r * 0.62), col, ol=OLD)
    circle(cv, x + look[0] * r * 0.3, y + look[1] * r * 0.2, r * 0.32, '#2DE2C6')
    circle(cv, x + look[0] * r * 0.3, y + look[1] * r * 0.2, r * 0.16, OLD)
    for k in range(5):
        a = math.radians(200 + k * 35)
        cv.drawLine(x + math.cos(a) * r, y + math.sin(a) * r * 0.62, x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 0.9, P(OLD, 255, stroke=4))


def moon(cv, x, y, r, drip=True):
    glow(cv, x, y, r * 2.6, '#FFE6B0', 120)
    cres = skia.Op(pcircle(x, y, r), pcircle(x + r * 0.42, y - r * 0.2, r * 0.86), skia.PathOp.kDifference_PathOp)
    ofill(cv, cres, '#FFF0C8', ol=OLD)
    if drip:
        for k in range(3):
            dx = x - r * 0.62 + k * r * 0.22
            ln = r * (0.4 + 0.25 * k)
            d = skia.Path(); d.moveTo(dx - 8, y + r * 0.55 - k * 12); d.lineTo(dx - 6, y + r * 0.6 + ln)
            d.quadTo(dx, y + r * 0.7 + ln + 14, dx + 6, y + r * 0.6 + ln); d.lineTo(dx + 8, y + r * 0.55 - k * 12); d.close()
            ofill(cv, d, '#FFF0C8', ol=OLD, w=4)


def dreamer(cv, cx, cy, s, skin='#B48AE0', hair='#2A1050', robe='#1E5A6A', eyes='lidded', third_eye=False, hair_up=True, seed=1):
    """Visage adulte allongé, cou long, paupières lourdes, cheveux qui flottent vers le haut. (cx,cy)=centre du visage."""
    dark = mix(skin, '#000000', 0.35)
    rnd = random.Random(seed)
    # cheveux flottants derrière la tête (mèches ondulées qui montent)
    if hair_up:
        glow(cv, cx, cy - 1.3 * s, 1.4 * s, mix(hair, '#7A3CFF', 0.5), 90)
        for i in range(22):
            u = i / 21
            x0 = cx - 0.7 * s + u * 1.4 * s
            ln = (1.2 + 0.9 * math.sin(u * math.pi)) * s * rnd.uniform(0.8, 1.1)
            ph = rnd.uniform(0, 6.28); lean = (u - 0.5) * 0.9 * s
            n = 14
            for k in range(n):
                v0, v1 = k / n, (k + 1) / n
                def pt(v):
                    return (x0 + lean * v + 0.13 * s * math.sin(v * 7 + ph) * v, cy - 0.55 * s - ln * v)
                w = 0.13 * s * (1 - v0) + 3
                a, b = pt(v0), pt(v1)
                cv.drawLine(a[0], a[1], b[0], b[1], P(OLD, 255, stroke=w + OW * 1.6))
            for k in range(n):
                v0, v1 = k / n, (k + 1) / n
                def pt(v):
                    return (x0 + lean * v + 0.13 * s * math.sin(v * 7 + ph) * v, cy - 0.55 * s - ln * v)
                w = 0.13 * s * (1 - v0) + 3
                a, b = pt(v0), pt(v1)
                cv.drawLine(a[0], a[1], b[0], b[1], P(mix(hair, '#7A3CFF', v0 * 0.6), 255, stroke=w))
    # robe / épaules
    p = skia.Path(); p.moveTo(cx - 1.6 * s, S + 50); p.cubicTo(cx - 1.4 * s, cy + 1.4 * s, cx - 0.5 * s, cy + 1.25 * s, cx, cy + 1.25 * s)
    p.cubicTo(cx + 0.5 * s, cy + 1.25 * s, cx + 1.4 * s, cy + 1.4 * s, cx + 1.6 * s, S + 50); p.close()
    ofill(cv, p, robe, ol=OLD)
    cv.save(); cv.clipPath(p, doAntiAlias=True)
    for k in range(5):
        cv.drawLine(cx - 1.2 * s + k * 0.6 * s, cy + 1.3 * s, cx - 1.5 * s + k * 0.75 * s, S + 50, P(mix(robe, '#000000', 0.3), 255, stroke=6))
    cv.restore()
    # cou long
    ofill(cv, prr(cx - 0.22 * s, cy + 0.6 * s, 0.44 * s, 0.75 * s, 0.15 * s), dark, ol=OLD)
    # visage allongé
    face = poval(cx, cy, 0.72 * s, 0.98 * s)
    ofill(cv, face, skin, ol=OLD)
    cv.save(); cv.clipPath(face, doAntiAlias=True)
    oval(cv, cx + 0.45 * s, cy + 0.2 * s, 0.5 * s, 1.1 * s, dark, 110)      # ombre côté droit
    cv.restore()
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - 0.72 * s, cy - 0.98 * s, cx + 0.72 * s, cy + 0.98 * s), 120, 110)
    cv.drawPath(p, P('#2DE2E6', 200, stroke=5))                                 # liseré de lumière froide
    # frange balayée sur le côté
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - 0.74 * s, cy - 1.0 * s, cx + 0.74 * s, cy + 0.96 * s), 175, 190)
    p.cubicTo(cx + 0.55 * s, cy - 0.45 * s, cx + 0.05 * s, cy - 0.62 * s, cx - 0.2 * s, cy - 0.38 * s)
    p.cubicTo(cx - 0.4 * s, cy - 0.2 * s, cx - 0.6 * s, cy - 0.2 * s, cx - 0.74 * s, cy - 0.05 * s); p.close()
    ofill(cv, p, hair, ol=OLD)
    for k in range(3):
        pp = skia.Path(); pp.moveTo(cx - 0.4 * s + k * 0.3 * s, cy - 0.9 * s); pp.quadTo(cx - 0.1 * s + k * 0.25 * s, cy - 0.7 * s, cx - 0.25 * s + k * 0.3 * s, cy - 0.45 * s)
        cv.drawPath(pp, P(mix(hair, '#7A3CFF', 0.6), 200, stroke=4))
    # yeux : grands, ronds, paupières lourdes
    for k in (-1, 1):
        ex, ey, er = cx + k * 0.3 * s, cy - 0.05 * s, 0.22 * s
        if eyes == 'closed':
            pp = skia.Path(); pp.addArc(skia.Rect.MakeLTRB(ex - er, ey - er * 0.4, ex + er, ey + er * 0.6), 20, 140)
            cv.drawPath(pp, P(OLD, 255, stroke=OW))
            for j in range(4):
                cv.drawLine(ex - er * 0.6 + j * er * 0.4, ey + er * 0.5, ex - er * 0.7 + j * er * 0.45, ey + er * 0.8, P(OLD, 255, stroke=3))
            continue
        ofill(cv, pcircle(ex, ey, er), '#F4ECFF', ol=OLD)
        circle(cv, ex + 0.03 * s, ey + 0.04 * s, er * 0.42, '#2DE2C6')
        circle(cv, ex + 0.03 * s, ey + 0.04 * s, er * 0.2, OLD)
        circle(cv, ex - er * 0.1, ey - er * 0.05, er * 0.1, '#FFFFFF')
        lid = 0.55 if eyes == 'lidded' else 0.2
        cv.save(); cv.clipPath(pcircle(ex, ey, er), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(ex - er, ey - er, 2 * er, 2 * er * lid), P(skin))
        cv.restore()
        cv.drawLine(ex - er, ey - er + 2 * er * lid, ex + er, ey - er + 2 * er * lid, P(OLD, 255, stroke=OW))
        cv.drawPath(pcircle(ex, ey, er), P(OLD, 255, stroke=OW))
        # cernes
        pp = skia.Path(); pp.addArc(skia.Rect.MakeLTRB(ex - er * 0.8, ey + er * 0.6, ex + er * 0.8, ey + er * 1.3), 20, 140)
        cv.drawPath(pp, P(dark, 255, stroke=3))
    # nez + bouche
    p = skia.Path(); p.moveTo(cx - 0.02 * s, cy + 0.1 * s); p.quadTo(cx - 0.12 * s, cy + 0.38 * s, cx + 0.04 * s, cy + 0.4 * s)
    cv.drawPath(p, P(OLD, 255, stroke=5))
    cv.drawLine(cx - 0.14 * s, cy + 0.62 * s, cx + 0.12 * s, cy + 0.6 * s, P(OLD, 255, stroke=5))
    if third_eye:
        glow(cv, cx, cy - 0.55 * s, 0.4 * s, '#FFE680', 230)
        ofill(cv, poval(cx, cy - 0.55 * s, 0.13 * s, 0.08 * s), '#FFF6C8', ol=OLD, w=4)
        circle(cv, cx, cy - 0.55 * s, 0.045 * s, OLD)


def v1(cv):
    """Rêveur aux paupières lourdes, cheveux qui montent dans la nébuleuse, lune qui fond, yeux flottants."""
    night_bg(cv, 11)
    for i, c in enumerate(['#3A0E6A', '#5A1A8A', '#7A2A9A']):
        cv.drawCircle(S / 2, 420, 520 - i * 110, P(c, 70, blur=50))
    moon(cv, 950, 150, 62, drip=False)
    floating_eye(cv, 180, 260, 46, (0.6, 0.2))
    floating_eye(cv, 920, 560, 34, (-0.6, 0))
    floating_eye(cv, 140, 640, 28, (0.5, -0.3))
    dreamer(cv, S / 2, 560, 260, seed=3)
    mist(cv, 960, '#2DE2C6', 40)


def v2(cv):
    """Yeux fermés, troisième œil lumineux, porte qui flotte dans le ciel, reflet dans l'eau noire."""
    night_bg(cv, 12, '#02010A', '#0E1A3A', '#1A0A2A')
    ofill(cv, prr(800, 120, 130, 220, 60), '#1A0A3A', ol=OLD)
    cv.save(); cv.clipPath(prr(812, 132, 106, 196, 52), doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeXYWH(800, 120, 130, 220), P(shader=lin(0, 120, 0, 340, ['#FFE680', '#FF4FA8'])))
    cv.restore()
    glow(cv, 865, 230, 200, '#FFB0E8', 110)
    for k in range(5):
        ofill(cv, prr(820 - k * 30, 360 + k * 46, 120, 26, 8), '#3A2A6A', ol=OLD, w=4)
    floating_eye(cv, 190, 230, 40, (0.5, 0.3))
    dreamer(cv, S / 2, 540, 250, skin='#7AC8D8', hair='#14304A', robe='#3A0E5A', eyes='closed', third_eye=True, seed=5)
    cv.drawRect(skia.Rect.MakeXYWH(0, 930, S, 150), P(shader=lin(0, 930, 0, S, ['#0A1A3A', '#02010A'])))
    for k in range(6):
        cv.drawLine(80 + k * 160, 960 + (k % 3) * 30, 180 + k * 160, 960 + (k % 3) * 30, P('#B98CFF', 120, stroke=4))


def v3(cv):
    """Le haut du visage se dissout en galaxie, planètes en orbite, papillons de nuit."""
    night_bg(cv, 13, '#05020F', '#2A0A3A', '#5A1A4A')
    dreamer(cv, S / 2, 590, 250, skin='#E07AB8', hair='#2A0E3A', robe='#2A1A5A', eyes='lidded', hair_up=False, seed=7)
    # dissolution du crâne en cosmos
    cx, cy, s = S / 2, 590, 250
    cv.save(); clip = skia.Path(); clip.addRect(skia.Rect.MakeXYWH(0, 0, S, cy - 0.55 * s)); cv.clipPath(clip)
    cv.drawOval(skia.Rect.MakeLTRB(cx - 0.76 * s, cy - 1.02 * s, cx + 0.76 * s, cy + 1.0 * s), P(shader=rad(cx, cy - 0.8 * s, 0.9 * s, ['#FFB0E8', '#7A3CFF', '#14063A'])))
    Stars(60, 9, area=(cx - 0.7 * s, cy - 1.0 * s, cx + 0.7 * s, cy - 0.55 * s), rmax=2.4).draw(cv, 0)
    cv.restore()
    rnd = random.Random(4)
    for _ in range(70):
        a = rnd.uniform(-2.8, -0.3); r = rnd.uniform(0.8, 2.0) * s
        x, y = cx + math.cos(a) * r, cy - 0.7 * s + math.sin(a) * r * 0.8
        circle(cv, x, y, rnd.uniform(3, 9), rnd.choice(['#E07AB8', '#FFB0E8', '#B98CFF', '#FFFFFF']), 220)
    for a, r, c in ((-2.3, 400, '#2DE2C6'), (-0.6, 380, '#FFE04A')):
        x, y = cx + math.cos(a) * r, cy - 0.6 * s + math.sin(a) * r * 0.7
        ofill(cv, pcircle(x, y, 34), c, ol=OLD)
        cv.drawOval(skia.Rect.MakeLTRB(x - 60, y - 12, x + 60, y + 12), P(OLD, 255, stroke=5))
    for x, y in ((200, 820), (880, 780)):
        for side in (-1, 1):
            ofill(cv, poval(x + side * 26, y, 28, 18), '#B98CFF', ol=OLD, w=4)
        ofill(cv, poval(x, y, 6, 20), OLD, ol=OLD, w=2)


if __name__ == '__main__':
    for name, fn in (('pfp_nuit_1_reveur', v1), ('pfp_nuit_2_troisieme_oeil', v2), ('pfp_nuit_3_cosmos', v3)):
        surf = skia.Surface(S * 2, S * 2)
        cv = surf.getCanvas(); cv.scale(2, 2)
        fn(cv)
        big = surf.makeImageSnapshot()
        out = skia.Surface(S, S); out.getCanvas().drawImageRect(big, skia.Rect.MakeWH(S, S), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
        out.makeImageSnapshot().save(os.path.join(HERE, name + '.png'))
        print('ok', name)

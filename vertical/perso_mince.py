"""Version plus mince du perso aux trois yeux (même tête, mêmes couleurs, silhouette allongée)."""
import math, random
import skia
from lib import P, mix, circle, oval
from mg import ofill, pcircle, poval, prr, noodle, OW

OLD = '#120624'
BOTTOM = 1990


def arms(cv, cx, cy, s, t, pose, skin, robe):
    sh = [(cx - 0.42 * s, cy + 1.45 * s), (cx + 0.42 * s, cy + 1.45 * s)]
    sw = math.sin(t * 2.0)
    hands = [(cx - 0.7 * s, cy + 2.7 * s + 0.05 * s * sw), (cx + 0.7 * s, cy + 2.7 * s - 0.05 * s * sw)]
    phone = None
    if pose == 'wave': hands[1] = (cx + 1.0 * s + 0.15 * s * math.sin(t * 7), cy + 0.35 * s)
    elif pose == 'phone':
        px, py = cx + 0.22 * s, cy + 1.05 * s
        hands = [(px - 0.15 * s, py + 0.2 * s), (px + 0.12 * s, py + 0.22 * s)]; phone = (px, py)
    elif pose == 'open':
        o = 0.1 * s * math.sin(t * 2.4); hands = [(cx - 1.2 * s - o, cy + 0.9 * s), (cx + 1.2 * s + o, cy + 0.9 * s)]
    elif pose == 'heart': hands = [(cx - 0.13 * s, cy + 1.25 * s), (cx + 0.13 * s, cy + 1.25 * s)]
    for k, ((sx, sy), (hx, hy)) in enumerate(zip(sh, hands)):
        side = -1 if k == 0 else 1
        noodle(cv, [(sx, sy), ((sx + hx) / 2 + side * 0.25 * s, (sy + hy) / 2 + 0.2 * s), (hx, hy)], robe, w=0.2 * s, ol=OLD)
    if phone:
        px, py = phone
        for j in range(4): cv.drawCircle(px, py, 0.7 * s * (1 - j * 0.22), P('#5AD7FF', 30))
        ofill(cv, prr(px - 0.13 * s, py - 0.24 * s, 0.26 * s, 0.48 * s, 0.05 * s), '#0E0E1E', ol=OLD, w=4)
        cv.drawRect(skia.Rect.MakeXYWH(px - 0.1 * s, py - 0.19 * s, 0.2 * s, 0.38 * s), P('#9BEFFF'))
        for j in range(4): cv.drawRect(skia.Rect.MakeXYWH(px - 0.07 * s, py - 0.15 * s + j * 0.09 * s, 0.14 * s, 0.035 * s), P('#3A6A9A', 200))
    for hx, hy in hands: ofill(cv, pcircle(hx, hy, 0.11 * s), skin, ol=OLD, w=4)


def dreamer(cv, cx, cy, s, skin='#7AC8D8', hair='#14304A', robe='#3A0E5A', eyes='open', third_eye=True, hair_up=True, seed=1, t=0.0, arms=None, look=None):
    dark = mix(skin, '#000000', 0.35); rnd = random.Random(seed)
    fw = 0.52                                                   # demi-largeur du visage (avant : 0.72)
    if hair_up:                                                 # mèches fines et longues qui flottent
        for i in range(18):
            u = i / 17; x0 = cx - 0.5 * s + u * 1.0 * s
            ln = (1.5 + 1.1 * math.sin(u * math.pi)) * s * rnd.uniform(0.85, 1.1)
            ph = rnd.uniform(0, 6.28); lean = (u - 0.5) * 0.7 * s
            pts = [(x0 + lean * v + 0.1 * s * math.sin(v * 7 + ph + t * 1.4) * v, cy - 0.6 * s - ln * v * (1 + 0.04 * math.sin(t * 1.1 + ph))) for v in [k / 16 for k in range(17)]]
            for col, extra in ((OLD, OW * 1.6), (None, 0)):
                for k in range(16):
                    v0 = k / 16; w = 0.085 * s * (1 - v0) + 2.5
                    c = OLD if col else mix(hair, '#7A3CFF', v0 * 0.6)
                    cv.drawLine(*pts[k], *pts[k + 1], P(c, 255, stroke=w + extra))
    # longue cape étroite
    p = skia.Path(); p.moveTo(cx - 1.05 * s, BOTTOM + 50)
    p.cubicTo(cx - 0.9 * s, cy + 1.7 * s, cx - 0.35 * s, cy + 1.3 * s, cx, cy + 1.28 * s)
    p.cubicTo(cx + 0.35 * s, cy + 1.3 * s, cx + 0.9 * s, cy + 1.7 * s, cx + 1.05 * s, BOTTOM + 50); p.close()
    ofill(cv, p, robe, ol=OLD)
    cv.save(); cv.clipPath(p, doAntiAlias=True)
    for k in range(4): cv.drawLine(cx - 0.6 * s + k * 0.4 * s, cy + 1.4 * s, cx - 0.8 * s + k * 0.53 * s, BOTTOM + 50, P(mix(robe, '#000000', 0.3), 255, stroke=5))
    cv.restore()
    ofill(cv, prr(cx - 0.13 * s, cy + 0.65 * s, 0.26 * s, 0.75 * s, 0.1 * s), dark, ol=OLD)           # cou fin
    face = poval(cx, cy, fw * s, 1.0 * s); ofill(cv, face, skin, ol=OLD)
    cv.save(); cv.clipPath(face, doAntiAlias=True); oval(cv, cx + 0.33 * s, cy + 0.2 * s, 0.36 * s, 1.1 * s, dark, 110); cv.restore()
    a = skia.Path(); a.addArc(skia.Rect.MakeLTRB(cx - fw * s, cy - s, cx + fw * s, cy + s), 120, 110); cv.drawPath(a, P('#2DE2E6', 200, stroke=4))
    f = skia.Path(); f.addArc(skia.Rect.MakeLTRB(cx - (fw + 0.02) * s, cy - 1.02 * s, cx + (fw + 0.02) * s, cy + 0.98 * s), 175, 190)
    f.cubicTo(cx + 0.4 * s, cy - 0.45 * s, cx + 0.04 * s, cy - 0.62 * s, cx - 0.15 * s, cy - 0.4 * s)
    f.cubicTo(cx - 0.3 * s, cy - 0.22 * s, cx - 0.43 * s, cy - 0.22 * s, cx - (fw + 0.02) * s, cy - 0.05 * s); f.close()
    ofill(cv, f, hair, ol=OLD)
    for k in (-1, 1):                                           # yeux en amande, plus étroits
        ex, ey, er = cx + k * 0.22 * s, cy - 0.03 * s, 0.155 * s
        blink = t > 0 and ((t * 0.55 + seed * 0.37) % 4.0) < 0.13
        if eyes == 'closed' or blink:
            pp = skia.Path(); pp.addArc(skia.Rect.MakeLTRB(ex - er, ey - er * 0.4, ex + er, ey + er * 0.6), 20, 140); cv.drawPath(pp, P(OLD, 255, stroke=OW * 0.8)); continue
        ofill(cv, poval(ex, ey, er, er * 1.1), '#F4ECFF', ol=OLD, w=OW * 0.8)
        lx, ly = look if look else (0.14, 0.18)
        px, py = ex + lx * er * 0.4, ey + ly * er * 0.45
        circle(cv, px, py, er * 0.45, '#2DE2C6'); circle(cv, px, py, er * 0.22, OLD); circle(cv, px - er * 0.13, py - er * 0.12, er * 0.1, '#FFFFFF')
        lid = 0.55 if eyes == 'lidded' else 0.22
        cv.save(); cv.clipPath(poval(ex, ey, er, er * 1.1), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(ex - er, ey - er * 1.1, 2 * er, 2.2 * er * lid), P(skin)); cv.restore()
        cv.drawLine(ex - er, ey - er * 1.1 + 2.2 * er * lid, ex + er, ey - er * 1.1 + 2.2 * er * lid, P(OLD, 255, stroke=OW * 0.8))
        cv.drawPath(poval(ex, ey, er, er * 1.1), P(OLD, 255, stroke=OW * 0.8))
    n = skia.Path(); n.moveTo(cx - 0.01 * s, cy + 0.12 * s); n.quadTo(cx - 0.08 * s, cy + 0.4 * s, cx + 0.04 * s, cy + 0.42 * s); cv.drawPath(n, P(OLD, 255, stroke=4))
    cv.drawLine(cx - 0.1 * s, cy + 0.64 * s, cx + 0.09 * s, cy + 0.62 * s, P(OLD, 255, stroke=4))
    if arms: _arms(cv, cx, cy, s, t, arms, skin, robe)
    if third_eye:
        for j in range(4): cv.drawCircle(cx, cy - 0.55 * s, 0.32 * s * (1 - j * 0.22), P('#FFE680', 40))
        ofill(cv, poval(cx, cy - 0.55 * s, 0.1 * s, 0.065 * s), '#FFF6C8', ol=OLD, w=4)
        circle(cv, cx, cy - 0.55 * s, 0.035 * s, OLD)


_arms = arms

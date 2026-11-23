"""« Est-ce que le travail tue nos rêves ? » — vertical 4K, 30 fps, calé sur le rythme du son de référence (son non inclus)."""
import math, os, random, sys, json, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'retard'))
import video as R                                   # outils + décors de la vidéo précédente
from video import (W, H, SC, OW_, OH_, PX, PY, HS, HERO, FONT, TY, pd, clamp, back, hero, banded_sky, hill, striped_sun, plant,
                   island, figure, floating_ring, pyramid, dots, BIG, bez, road, opath, rect, pop, CREAM, GOLD, sym, OUT, eye, mg)
import extrait2 as X
import numpy as np, skia
from lib import P, C, mix, lin, rad, circle, ease, ease_out

FPS = 30; DUR = 59.5
KID = dict(skin='#7AC8D8', hair='#14304A', robe='#2E6A8A')
RY = json.load(open(os.path.join(HERE, '..', 'son', 'rythme.json')))
BEATS = RY['beats']

# ---------------- mots ----------------
KEYS = {'PETIT', 'ASTRONAUTE', 'VÉTÉRINAIRE', 'FOOTBALLEUR', "D'IMPORTANT", 'GRANDI', 'DEVENU', 'RECOMMENCE', 'MILLE', 'HEURES',
        'ÇA', 'TRAVAIL', 'FAIS', 'ES', 'MÉTIER', 'ÉTOILES', 'EXPLORER', 'ÉMERVEILLÉ', 'PRIS', 'CIEL', 'APPRENDRE', 'CRÉER',
        'BUREAU', 'NOURRIR', 'SOIR', 'GAMIN', 'TOUJOURS'}


def load_words():
    raw = json.load(open(os.path.join(HERE, 'words.json')))
    toks = []
    for w, s, e in raw:
        if w and w[0] in "'-" and toks: toks[-1][0] += w; toks[-1][2] = e; continue
        if w.strip('?!.,…') == '': continue
        toks.append([w, s, e])
    if toks[-2][0].lower().startswith('tout') and toks[-1][0].lower().startswith('jour'):
        toks[-2] = ['toujours', toks[-2][1], toks[-1][2]]; toks.pop()
    out = []
    for i, (w, s, e) in enumerate(toks):
        txt = w.strip(',.?!…').upper()
        txt = {'POSE': 'PAUSE', "T'A": "T'AS"}.get(txt, txt)
        nxt = toks[i + 1][1] if i + 1 < len(toks) else e + 1.5
        end = nxt if nxt - e < 0.7 else e + 0.35
        out.append((txt, s, end, txt in KEYS))
    return out


WORDS = load_words()
X.WORDS = [(w, s, k) for w, s, e, k in WORDS]


def word_at(t):
    for i, (w, s, e, k) in enumerate(WORDS):
        if s <= t < e: return i, w, s, k
    return None


def draw_word(cv, t):
    r = word_at(t)
    if not r: return
    i, w, s, k = r; age = t - s
    size = 185 if k else 160
    f = skia.Font(FONT, size); tw = f.measureText(w)
    if tw > 820: f.setSize(size * 820 / tw); tw = f.measureText(w)
    sc = 0.9 + 0.1 * ease_out(clamp(age / 0.16))
    cv.save(); cv.translate(W / 2, TY); cv.scale(sc, sc)
    x, y = -tw / 2, f.getSize() * 0.35; fs = f.getSize()
    o = P(OUT, 255, stroke=fs * 0.15); o.setStrokeJoin(skia.Paint.kRound_Join)
    cv.drawString(w, x + fs * 0.03, y + fs * 0.06, f, o); cv.drawString(w, x + fs * 0.03, y + fs * 0.06, f, P(OUT))
    cv.drawString(w, x, y, f, o); cv.drawString(w, x, y, f, P(GOLD if k else CREAM))
    cv.restore()


# ---------------- rythme ----------------
def bp(t):
    """Pulsation : 1 sur chaque temps puis décroît ; plus fort sur les premiers temps de mesure."""
    v = 0.0
    for i, b in enumerate(BEATS):
        if b > t: break
        if t - b < 0.6: v = max(v, math.exp(-(t - b) * 8) * (1.0 if i % 4 == 3 else 0.55))
    return v


def twinkle(cv, seed, n, area, t, col='#FFFFFF'):
    rnd = random.Random(seed); p = bp(t)
    for k in range(n):
        x, y = rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3]); s = rnd.uniform(5, 13)
        if k % 5 == 0: sym(cv, 'star4', x, y, s * (1 + 0.5 * p), 0, col, t)
        else: circle(cv, x, y, s * 0.25 * (1 + 0.4 * p), col, 230)


def kid(cv, t, cx, cy, s, eyes='open', look=None, arms=None, pal=KID, helmet=False):
    hero(cv, t, cx, cy, s, eyes, look=look, arms=arms, pal=pal, seed=7)
    if helmet:
        yy = cy + 5 * math.sin(t * 2.1)
        cv.drawCircle(cx, yy - 0.2 * s, 1.25 * s, P('#BFE6FF', 40)); cv.drawCircle(cx, yy - 0.2 * s, 1.25 * s, P(OUT, 255, stroke=9))
        cv.drawCircle(cx, yy - 0.2 * s, 1.25 * s, P('#DFF4FF', 255, stroke=3))
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - 1.05 * s, yy - 1.25 * s, cx + 1.05 * s, yy + 0.85 * s), 200, 50)
        cv.drawPath(p, P('#FFFFFF', 220, stroke=10))


# ---------------- objets ----------------
def bubble(cv, x, y, r, t):
    cv.drawCircle(x, y, r, P('#E8E0F8', 50)); cv.drawCircle(x, y, r, P(OUT, 255, stroke=7)); cv.drawCircle(x, y, r, P(CREAM, 255, stroke=3))
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.8), 200, 50); cv.drawPath(p, P('#FFFFFF', 200, stroke=6))


def rocket(cv, x, y, s, t, rot=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    fl = skia.Path(); fl.moveTo(-0.22 * s, 0.55 * s); fl.lineTo(0, (0.95 + 0.12 * math.sin(t * 20)) * s); fl.lineTo(0.22 * s, 0.55 * s); fl.close()
    opath(cv, fl, '#FFB060', 4)
    for sx in (-1, 1):
        fn = skia.Path(); fn.moveTo(sx * 0.22 * s, 0.15 * s); fn.lineTo(sx * 0.48 * s, 0.6 * s); fn.lineTo(sx * 0.2 * s, 0.5 * s); fn.close(); opath(cv, fn, '#C85A6A', 4)
    b = skia.Path(); b.moveTo(0, -0.8 * s); b.cubicTo(0.35 * s, -0.5 * s, 0.3 * s, 0.3 * s, 0.22 * s, 0.58 * s); b.lineTo(-0.22 * s, 0.58 * s)
    b.cubicTo(-0.3 * s, 0.3 * s, -0.35 * s, -0.5 * s, 0, -0.8 * s); b.close(); opath(cv, b, '#EDE6F2', 5)
    opath(cv, skia.Path().addCircle(0, -0.15 * s, 0.13 * s), '#7AC8D8', 4)
    cv.restore()


def cat(cv, x, y, s, t):
    for sx in (-1, 1):
        e = skia.Path(); e.moveTo(x + sx * 0.55 * s, y - 0.2 * s); e.lineTo(x + sx * 0.5 * s, y - 0.85 * s); e.lineTo(x + sx * 0.1 * s, y - 0.5 * s); e.close(); opath(cv, e, '#E0A070', 5)
    opath(cv, skia.Path().addOval(skia.Rect.MakeLTRB(x - 0.62 * s, y - 0.6 * s, x + 0.62 * s, y + 0.5 * s)), '#E0A070', 5)
    for sx in (-1, 1):
        cv.save(); cv.translate(x + sx * 0.25 * s, y - 0.12 * s); eye(cv, 0.15 * s, '#8FC870', t, (0.2, 0), 255, sx); cv.restore()
        for k in (-1, 1): cv.drawLine(x + sx * 0.25 * s, y + 0.15 * s, x + sx * 0.85 * s, y + 0.1 * s + k * 0.1 * s, P(OUT, 255, stroke=3))
    opath(cv, skia.Path().addCircle(x, y + 0.08 * s, 0.06 * s), '#D86A8A', 3)


def ball(cv, x, y, s, t):
    cv.save(); cv.translate(x, y); cv.rotate(t * 40)
    opath(cv, skia.Path().addCircle(0, 0, s), '#F4F0EC', 6)
    for k in range(5):
        a = k * 2 * math.pi / 5
        opath(cv, skia.Path().addCircle(0.66 * s * math.cos(a), 0.66 * s * math.sin(a), 0.17 * s), '#2A2238', 3)
    opath(cv, skia.Path().addCircle(0, 0, 0.24 * s), '#2A2238', 3)
    cv.restore()


def crown(cv, x, y, s, t):
    p = skia.Path(); p.moveTo(x - 0.7 * s, y + 0.4 * s); p.lineTo(x - 0.75 * s, y - 0.5 * s); p.lineTo(x - 0.35 * s, y - 0.05 * s); p.lineTo(x, y - 0.65 * s)
    p.lineTo(x + 0.35 * s, y - 0.05 * s); p.lineTo(x + 0.75 * s, y - 0.5 * s); p.lineTo(x + 0.7 * s, y + 0.4 * s); p.close(); opath(cv, p, '#F0C860', 6)
    for k, c in enumerate(('#D86A8A', '#7AC8D8', '#D86A8A')): opath(cv, skia.Path().addCircle(x + (k - 1) * 0.4 * s, y + 0.15 * s, 0.1 * s), c, 3)


def alarm(cv, x, y, s, t):
    sh = 6 * bp(t) * math.sin(t * 60)
    cv.save(); cv.translate(x + sh, y)
    for sx in (-1, 1):
        opath(cv, skia.Path().addCircle(sx * 0.55 * s, -0.75 * s, 0.3 * s), '#C85A6A', 5)
        cv.drawLine(sx * 0.5 * s, 0.7 * s, sx * 0.7 * s, 1.0 * s, P(OUT, 255, stroke=10))
    opath(cv, skia.Path().addCircle(0, 0, 0.85 * s), '#E85A6A', 6); opath(cv, skia.Path().addCircle(0, 0, 0.68 * s), '#F4EEE4', 5)
    cv.drawLine(0, 0, 0, -0.5 * s, P(OUT, 255, stroke=9)); cv.drawLine(0, 0, 0.35 * s, 0.1 * s, P(OUT, 255, stroke=9))
    cv.restore()


def train(cv, x, y, s, t):
    xo = x + 30 * math.sin(t * 3)
    opath(cv, rect(xo - 1.1 * s, y - 0.55 * s, 2.2 * s, 1.0 * s, 0.25 * s), '#5A6A8A', 6)
    for k in range(4): opath(cv, rect(xo - 0.95 * s + k * 0.5 * s, y - 0.4 * s, 0.38 * s, 0.35 * s, 6), '#F0E0A0', 4)
    cv.drawLine(xo - 1.1 * s, y + 0.15 * s, xo + 1.1 * s, y + 0.15 * s, P('#C85A6A', 255, stroke=10))
    for k in (-0.7, 0.7): opath(cv, skia.Path().addCircle(xo + k * s, y + 0.5 * s, 0.14 * s), '#2A2238', 4)
    cv.drawLine(x - 1.6 * s, y + 0.66 * s, x + 1.6 * s, y + 0.66 * s, P(OUT, 255, stroke=8))


def screen(cv, x, y, s, t):
    opath(cv, rect(x - 0.12 * s, y + 0.5 * s, 0.24 * s, 0.35 * s), '#3A3450', 5); opath(cv, rect(x - 0.45 * s, y + 0.8 * s, 0.9 * s, 0.12 * s, 6), '#3A3450', 5)
    opath(cv, rect(x - 1.0 * s, y - 0.7 * s, 2.0 * s, 1.25 * s, 14), '#2A2E48', 6)
    opath(cv, rect(x - 0.88 * s, y - 0.58 * s, 1.76 * s, 1.0 * s, 8), '#8FC8E0', 4)
    for k in range(5):
        ww = (0.4 + 0.5 * ((k * 37 + int(t * 4)) % 7) / 7) * s
        cv.drawLine(x - 0.75 * s, y - 0.45 * s + k * 0.18 * s, x - 0.75 * s + ww, y - 0.45 * s + k * 0.18 * s, P('#4A6A8A', 255, stroke=10))


def coffee(cv, x, y, s, t):
    for k in range(3):
        st = skia.Path(); st.moveTo(x - 0.25 * s + k * 0.25 * s, y - 0.55 * s)
        for i in range(1, 7): st.lineTo(x - 0.25 * s + k * 0.25 * s + 0.08 * s * math.sin(i + t * 4 + k), y - 0.55 * s - i * 0.11 * s)
        cv.drawPath(st, P('#D8D0E0', 200, stroke=6))
    cup = skia.Path(); cup.moveTo(x - 0.5 * s, y - 0.45 * s); cup.lineTo(x + 0.5 * s, y - 0.45 * s); cup.lineTo(x + 0.4 * s, y + 0.5 * s); cup.lineTo(x - 0.4 * s, y + 0.5 * s); cup.close()
    hd = skia.Path(); hd.addOval(skia.Rect.MakeLTRB(x + 0.35 * s, y - 0.25 * s, x + 0.8 * s, y + 0.2 * s)); cv.drawPath(hd, P(OUT, 255, stroke=18)); cv.drawPath(hd, P('#E8E0D8', 255, stroke=10))
    opath(cv, cup, '#E8E0D8', 6); cv.drawLine(x - 0.48 * s, y - 0.25 * s, x + 0.48 * s, y - 0.25 * s, P('#C85A6A', 255, stroke=10))


def bed(cv, x, y, s, t):
    opath(cv, rect(x - 1.1 * s, y - 0.1 * s, 2.2 * s, 0.6 * s, 10), '#5A4A7A', 6)
    opath(cv, rect(x - 1.15 * s, y - 0.7 * s, 0.2 * s, 1.5 * s, 8), '#3A2E50', 5); opath(cv, rect(x + 0.95 * s, y - 0.4 * s, 0.2 * s, 1.2 * s, 8), '#3A2E50', 5)
    opath(cv, rect(x - 0.9 * s, y - 0.35 * s, 0.5 * s, 0.3 * s, 14), '#E8E0F0', 5)
    bl = skia.Path(); bl.moveTo(x - 0.35 * s, y - 0.25 * s); bl.quadTo(x + 0.3 * s, y - 0.45 * s, x + 0.95 * s, y - 0.2 * s); bl.lineTo(x + 0.95 * s, y + 0.2 * s); bl.lineTo(x - 0.35 * s, y + 0.2 * s); bl.close()
    opath(cv, bl, '#3E6A8A', 5)
    sym(cv, 'moon', x + 0.6 * s, y - 1.0 * s, 0.3 * s, -20, '#E8E0B8', t)


def loop(cv, x, y, s, t):
    cv.save(); cv.translate(x, y); cv.rotate(-t * 120)
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(-s, -s, s, s), 20, 300)
    cv.drawPath(p, P(OUT, 255, stroke=0.3 * s + 12)); cv.drawPath(p, P('#C8B8FF', 255, stroke=0.3 * s))
    a = math.radians(20); hx, hy = s * math.cos(a), s * math.sin(a)
    tr = skia.Path(); tr.moveTo(hx - 0.35 * s, hy - 0.1 * s); tr.lineTo(hx + 0.35 * s, hy - 0.1 * s); tr.lineTo(hx, hy + 0.4 * s); tr.close(); opath(cv, tr, '#C8B8FF', 6)
    cv.restore()


def telescope(cv, x, y, s, t):
    for sx in (-1, 1): cv.drawLine(x, y, x + sx * 0.5 * s, y + 0.9 * s, P(OUT, 255, stroke=10))
    cv.drawLine(x, y, x, y + 0.9 * s, P(OUT, 255, stroke=10))
    cv.save(); cv.translate(x, y); cv.rotate(-35)
    opath(cv, rect(-0.3 * s, -0.16 * s, 1.3 * s, 0.32 * s, 8), '#D89AAE', 5); opath(cv, rect(0.95 * s, -0.22 * s, 0.25 * s, 0.44 * s, 6), '#B87A8E', 5)
    cv.restore()


def book(cv, x, y, s, t):
    for sx in (-1, 1):
        pg = skia.Path(); pg.moveTo(x, y + 0.1 * s); pg.quadTo(x + sx * 0.5 * s, y - 0.1 * s, x + sx * 1.0 * s, y + 0.05 * s); pg.lineTo(x + sx * 1.0 * s, y + 0.75 * s)
        pg.quadTo(x + sx * 0.5 * s, y + 0.6 * s, x, y + 0.8 * s); pg.close(); opath(cv, pg, '#F4EEE4', 5)
        for k in range(4): cv.drawLine(x + sx * 0.15 * s, y + 0.25 * s + k * 0.13 * s, x + sx * 0.85 * s, y + 0.22 * s + k * 0.13 * s, P('#B8A8C8', 255, stroke=5))
    for k in range(7):
        u = (t * 0.5 + k / 7) % 1
        sym(cv, 'star4', x + 0.6 * s * math.sin(k * 2.3 + u * 3), y - u * 1.6 * s, 0.1 * s * (1 - u) + 3, 0, GOLD, t, 255 * (1 - u))


def easel(cv, x, y, s, t):
    for sx in (-1, 1): cv.drawLine(x, y - 1.0 * s, x + sx * 0.6 * s, y + 1.0 * s, P(OUT, 255, stroke=14)); cv.drawLine(x, y - 1.0 * s, x + sx * 0.6 * s, y + 1.0 * s, P('#A07A5A', 255, stroke=7))
    cv.save(); cv.clipPath(rect(x - 0.75 * s, y - 0.85 * s, 1.5 * s, 1.1 * s, 6), doAntiAlias=True)
    for k, c in enumerate(('#F6E0C0', '#F0C8B0', '#D8B0C8', '#A8A0D0')): cv.drawRect(skia.Rect.MakeXYWH(x - 0.75 * s, y - 0.85 * s + k * 0.275 * s, 1.5 * s, 0.28 * s), P(c))
    cv.drawCircle(x, y - 0.1 * s, 0.3 * s, P('#FFD8A0')); cv.drawCircle(x, y - 0.1 * s, 0.3 * s, P(OUT, 255, stroke=4))
    cv.restore(); cv.drawPath(rect(x - 0.75 * s, y - 0.85 * s, 1.5 * s, 1.1 * s, 6), P(OUT, 255, stroke=6))


def can(cv, x, y, s, tilt):
    cv.save(); cv.translate(x, y); cv.rotate(tilt)
    sp = skia.Path(); sp.moveTo(0.4 * s, -0.1 * s); sp.lineTo(1.1 * s, -0.5 * s); sp.lineTo(1.15 * s, -0.38 * s); sp.lineTo(0.45 * s, 0.1 * s); sp.close(); opath(cv, sp, '#7AA8B8', 5)
    opath(cv, rect(-0.5 * s, -0.4 * s, 1.0 * s, 0.85 * s, 14), '#7AA8B8', 6)
    hd = skia.Path(); hd.addArc(skia.Rect.MakeLTRB(-0.45 * s, -0.75 * s, 0.25 * s, -0.1 * s), 180, 180); cv.drawPath(hd, P(OUT, 255, stroke=16)); cv.drawPath(hd, P('#7AA8B8', 255, stroke=8))
    cv.restore()


# ---------------- scènes ----------------
def s_enfance(cv, t, lt):
    dk = ease(clamp((t - 9.45) / 2.6))
    pale = ['#5A4A7A', '#6E5A8A', '#866C98', '#9E80A4', '#B494AE', '#C6A6B4']
    dark = ['#0A0716', '#100A20', '#170E2C', '#1F1238', '#2A1744', '#381D50']
    banded_sky(cv, [mix(a, b, dk) for a, b in zip(pale, dark)], -600, 1300, t)
    twinkle(cv, 1, 50, (-50, -50, W + 50, 800), t)
    u = clamp(t / 2.4)                                        # étoile filante dès la 1re image
    if u < 1:
        x0, y0 = -80 + 900 * u, 120 + 260 * u
        cv.drawLine(x0 - 220, y0 - 64, x0, y0, P(CREAM, 255, stroke=6)); sym(cv, 'star4', x0, y0, 26, 0, CREAM, t)
    striped_sun(cv, PX, 1100, 360 + 8 * bp(t), t, [mix(a, b, dk) for a, b in zip(['#E8C4A8', '#F0D2B4', '#F6E0C0'], ['#4A2350', '#5A2C5C', '#6C3666'])])
    hill(cv, 1450, 40, 0.006, 0.3, mix('#8A7096', '#2A1A40', dk), mix('#9478A0', '#33214C', dk), t)
    gone = ease(clamp((t - 11.4) / 0.5))
    for (x, y, r, t0, fn) in ((240, 540, 165, 3.27, rocket), (840, 560, 160, 4.83, cat), (190, 1180, 150, 6.41, ball), (890, 1160, 150, 7.99, crown)):
        s = pop(t, t0, 0.45) * (1 - gone)
        if s <= 0.01: continue
        yy = y + 12 * math.sin(t * 1.3 + x)
        cv.save(); cv.translate(x, yy); cv.scale(s, s); cv.translate(-x, -yy)
        bubble(cv, x, yy, r, t)
        if dk > 0: cv.saveLayerAlpha(None, int(255 * (1 - 0.5 * dk)))
        fn(cv, x, yy, r * 0.6, t)
        if dk > 0: cv.restore()
        cv.restore()
    g = ease(clamp((t - 11.42) / 0.9))                       # il grandit
    s = 175 + (230 - 175) * g
    pal = dict(skin=KID['skin'], hair=KID['hair'], robe=mix(KID['robe'], HERO['robe'], g))
    kid(cv, t, PX, PY + 0.55 * s, s, 'open', look=(0.0, -0.9) if t < 9.4 else (0.0, 0.2), pal=pal)


def s_noir(cv, t, lt):
    cv.drawRect(BIG, P('#05030A'))
    sym(cv, 'eye', PX, PY, 40, 0, '#FFD86A', t if lt > 0.5 else 0)


def office_bg(cv, t, tone=0.0):
    cv.drawRect(BIG, P(mix('#1A1826', '#0E0C16', tone)))
    vy = 900
    for k in range(-12, 13):
        cv.drawLine(PX + k * 30, vy, PX + k * 260, H + 300, P('#2A2838', 255, stroke=3))
    for j in range(12):
        y = vy + (H + 300 - vy) * (j / 11) ** 2
        cv.drawLine(-600, y, W + 600, y, P('#2A2838', 255, stroke=3))
    cv.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, vy), P(mix('#14121E', '#08070E', tone)))
    for row in range(3):                                       # rangées de box identiques
        for k in range(-2, 9):
            x = k * 150 + (row % 2) * 75; y = vy - 30 + row * 70; w = 130 - row * 10
            opath(cv, rect(x, y - 60 + row * 10, w, 70, 4), '#24222F', 4)
    cv.drawLine(-600, vy, W + 600, vy, P(OUT, 255, stroke=5))


ROUTINE = [(14.60, alarm), (15.39, train), (16.18, screen), (16.97, coffee), (17.76, screen), (18.55, train), (19.31, bed), (19.73, loop)]


def s_routine(cv, t, lt):
    office_bg(cv, t)
    hero(cv, t, PX, 1650, 200, 'lidded', look=(0.0, 0.2))
    cur = None
    for t0, fn in ROUTINE:
        if t >= t0: cur = (t0, fn)
    if cur:
        t0, fn = cur; s = 0.85 + 0.15 * ease_out(clamp((t - t0) / 0.12))
        cv.save(); cv.translate(PX, 1180); cv.scale(s, s); cv.translate(-PX, -1180)
        fn(cv, PX, 1180, 150, t); cv.restore()


def s_heures(cv, t, lt):
    off = clamp((t - 24.08) / 0.9)
    cv.drawRect(BIG, P('#0E0C18'))
    rnd = random.Random(3)
    for r_ in range(26):                                       # façade sans fin
        for c in range(16):
            x = -60 + c * 76; y = 120 + r_ * 72
            on = rnd.random() < 0.55 and rnd.random() > off * 1.05
            flick = ((c * 7 + r_ * 3 + int(t * 2)) % 23 == 0)
            cv.drawRect(skia.Rect.MakeXYWH(x, y, 52, 48), P('#F0E0A0' if on and not flick else '#1E1C2C'))
    ck = 0 if off >= 1 else 1
    cx_, cy_ = PX, 300
    opath(cv, skia.Path().addCircle(cx_, cy_, 120), '#E8E0D0', 8)
    a1 = (t * 9 * ck + 24.08 * 9 * (1 - ck)); a2 = a1 / 12
    cv.drawLine(cx_, cy_, cx_ + 95 * math.sin(a1), cy_ - 95 * math.cos(a1), P(OUT, 255, stroke=10))
    cv.drawLine(cx_, cy_, cx_ + 60 * math.sin(a2), cy_ - 60 * math.cos(a2), P(OUT, 255, stroke=14))
    hero(cv, t, PX, PY + 0.55 * HS, HS, 'lidded' if t < 24.08 else 'open', look=(0.0, 0.6) if t < 24.08 else (0, 0))
    opath(cv, rect(-100, 1640, W + 200, 500), '#3A2E3A', 7)
    cv.drawLine(-100, 1690, W + 200, 1690, P('#4A3A48', 255, stroke=8))
    for k, (x, h) in enumerate(((140, 260), (250, 180), (830, 320), (950, 220))):
        for j in range(int(h / 22)):
            opath(cv, rect(x - 70 + (j % 2) * 8, 1640 - (j + 1) * 22, 140, 20, 3), '#EDE6DA', 3)


DEBRIS = [(random.Random(i).uniform(0, 6.28), random.Random(i + 50).uniform(0.6, 1.4), i % 3) for i in range(9)]


def s_cosmos(cv, t, lt):
    banded_sky(cv, ['#04030C', '#0A0820', '#12102E', '#0E1A34', '#14223E', '#1A2A48'], -600, 1900, t, wav=30)
    twinkle(cv, 4, 140, (-50, -50, W + 50, H + 50), t)
    sym(cv, 'planet', 870, 300, 150 + 6 * bp(t), 0, '#8A6AAA', t)
    cv.drawCircle(170, 1500, 90, P('#BDB6CE')); cv.drawCircle(170, 1500, 90, P(OUT, 255, stroke=5))
    for a, sp, kind in DEBRIS:                                 # le bureau part en morceaux dans l'espace
        r = 200 + lt * 160 * sp
        x, y = PX + math.cos(a) * r, PY + math.sin(a) * r
        cv.save(); cv.translate(x, y); cv.rotate(lt * 40 * sp)
        if kind == 0: opath(cv, rect(-40, -50, 80, 100, 4), '#EDE6DA', 4)
        elif kind == 1: screen(cv, 0, 0, 40, t)
        else: alarm(cv, 0, 0, 35, t)
        cv.restore()
    hero(cv, t, PX, PY + 0.55 * HS, HS, 'open', look=(0.0, -1.0))


def s_astronaute(cv, t, lt):
    banded_sky(cv, ['#04030C', '#0A0820', '#12102E', '#161838', '#1A2042', '#1E284C'], -600, 1600, t, wav=30)
    twinkle(cv, 5, 120, (-50, -50, W + 50, H + 50), t)
    pl = skia.Path(); pl.addCircle(PX, 2900, 1300)
    cv.drawPath(pl, P('#6A4A7A')); cv.save(); cv.clipPath(pl, doAntiAlias=True)
    for k in range(8): cv.drawCircle(PX, 2900, 1300 - 60 - k * 40, P('#7A5A8A', 255, stroke=10))
    cv.restore(); cv.drawPath(pl, P(OUT, 255, stroke=7))
    a = t * 0.6
    rocket(cv, PX + 330 * math.cos(a), 1000 + 160 * math.sin(a), 110, t, math.degrees(a) + 180)
    kid(cv, t, PX, PY + 0.55 * 170 + 20 * math.sin(t * 0.9), 170, 'open', look=(0.6, -0.6), helmet=True)


def s_etoiles(cv, t, lt):
    banded_sky(cv, ['#06051A', '#0C0A26', '#120E32', '#18143E', '#1E1848', '#241C50'], -600, 1500, t)
    twinkle(cv, 6, 100, (-50, -50, W + 50, 1400), t)
    cons = [(140, 250), (300, 180), (420, 300), (600, 220), (760, 330), (930, 200)]
    prog = clamp((t - 33.37) / 0.8)
    for i in range(len(cons) - 1):
        if prog * (len(cons) - 1) > i:
            u = min(1, prog * (len(cons) - 1) - i); a, b = cons[i], cons[i + 1]
            cv.drawLine(a[0], a[1], a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, P(GOLD, 255, stroke=4))
    for x, y in cons: sym(cv, 'star4', x, y, 18 * (1 + 0.4 * bp(t)), 0, CREAM, t)
    yy = island(cv, PX, 1600, 900, '#3E4A6A', '#22183A', '#2C2246', t * 0, 0)
    if t > 34.27:                                              # explorer : un chemin de pas
        n = int(min(10, (t - 34.27) * 8))
        for k in range(n): cv.drawOval(skia.Rect.MakeXYWH(150 + k * 70, yy - 30 + (k % 2) * 16, 26, 14), P(CREAM, 200))
    telescope(cv, 260, 1380, 160, t)
    kid(cv, t, 680, 1470, 160, 'open', look=(-0.4, -1.0))
    if t > 35.27:                                              # émerveillé
        e = ease_out(clamp((t - 35.27) / 0.6))
        for k in range(10):
            g = k * math.pi / 5 + t * 0.6
            sym(cv, 'star4', 680 + math.cos(g) * 230 * e, 1380 + math.sin(g) * 160 * e, 16 * e, 0, [GOLD, CREAM, '#C8B8FF'][k % 3], t)


def s_pris(cv, t, lt):
    banded_sky(cv, ['#0A0716', '#120C24', '#1A1032', '#22143E', '#2C184A', '#361C54'], -600, 1500, t)
    twinkle(cv, 7, 90, (-50, -50, W + 50, 1300), t)
    hill(cv, 1650, 35, 0.006, 1.0, '#1E2238', '#262A44', t)
    ax, ay, sa = 340, 1300, 200; bx, by, sb = 790, 1450, 145
    hero(cv, t, ax, ay, sa, 'open', look=(0.7, 0.4))
    kid(cv, t, bx, by, sb, 'open', look=(-0.7, -0.5))
    e1 = (ax, ay - 0.55 * sa + 5 * math.sin(t * 2.1)); e2 = (bx, by - 0.55 * sb + 5 * math.sin(t * 2.1))
    pt = ease(clamp(lt / 0.9))
    for k in range(9):
        off = (k - 4) * 45 + 15 * math.sin(t * 1.3 + k)
        p = skia.Path(); p.moveTo(*e1); p.cubicTo(e1[0] + 150, e1[1] + off, e2[0] - 150, e2[1] - off, *e2)
        for paint in (P(OUT, 255, stroke=7), P(['#F0EBBE', '#C8B8FF', '#9FE8D8'][k % 3], 255, stroke=3)):
            if pt < 0.999: paint.setPathEffect(skia.TrimPathEffect.Make(0, max(0.001, pt)))
            cv.drawPath(p, paint)


def s_possibles(cv, t, lt):
    banded_sky(cv, ['#0C0A1E', '#14102C', '#1C1638', '#241C44', '#2E2250', '#38285A'], -600, 1500, t)
    twinkle(cv, 8, 110, (-50, -50, W + 50, 1400), t)
    m = pop(t, 38.62, 0.5)
    if m > 0:
        cv.save(); cv.translate(800, 330); cv.scale(m, m)
        cv.drawCircle(0, 0, 120, P('#E8E0C8')); cv.drawCircle(0, 0, 120, P(OUT, 255, stroke=6))
        for cx_, cy_, r_ in ((-30, -20, 22), (40, 30, 15), (20, -50, 10)): cv.drawCircle(cx_, cy_, r_, P('#D0C6AC'))
        cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(-600, 1700, W + 600, H + 600), P('#16121E'))
    for k in range(-1, 9): opath(cv, rect(k * 140 - 20, 1640 - (k * 53 % 5) * 40, 120, 400, 4), '#1E1A28', 4)
    hero(cv, t, PX, 1630, 200, 'open', look=(0.5, -0.9))
    for (x, y, t0, fn) in ((210, 1130, 40.91, book), (870, 1110, 43.34, easel)):
        s = pop(t, t0, 0.45)
        if s <= 0.01: continue
        cv.save(); cv.translate(x, y); cv.scale(s, s); cv.translate(-x, -y)
        bubble(cv, x, y, 175, t); fn(cv, x, y, 100, t); cv.restore()


def s_plante(cv, t, lt):
    warm = ease(clamp((t - 49.37) / 2.0))
    cv.drawRect(BIG, P(mix('#1A1826', '#2A2236', warm)))
    win = rect(150, 170, 780, 900, 12)
    cv.save(); cv.clipPath(win, doAntiAlias=True)
    banded_sky(cv, [mix(a, b, warm) for a, b in zip(['#06051A', '#0C0A26', '#120E32', '#18143E'], ['#3A2E52', '#664C78', '#967090', '#C8A098'])], 170, 1070, t)
    twinkle(cv, 9, 40, (150, 170, 930, 1070), t)
    cv.restore()
    cv.drawPath(win, P(OUT, 255, stroke=12))
    cv.drawLine(540, 170, 540, 1070, P(OUT, 255, stroke=10)); cv.drawLine(150, 620, 930, 620, P(OUT, 255, stroke=10))
    opath(cv, rect(-100, 1450, W + 200, 600), '#3A2A3A', 7)
    cv.drawLine(-100, 1500, W + 200, 1500, P('#4A3848', 255, stroke=8))
    grow = ease(clamp((t - 49.5) / 1.6)); bloom = ease(clamp((t - 50.03) / 1.2))
    x, base = PX, 1330
    droop = 1 - grow
    h = 230 + 170 * grow
    tx, ty = x + 120 * droop, base - h + 90 * droop
    st = skia.Path(); st.moveTo(x, base); st.cubicTo(x - 20, base - h * 0.5, tx + 40 * droop, ty + 60 * droop, tx, ty)
    cv.drawPath(st, P(OUT, 255, stroke=19)); cv.drawPath(st, P(mix('#6A6A5A', '#3E8A68', grow), 255, stroke=11))
    for sx in (-1, 1):
        lx, ly = x + sx * 4, base - h * 0.4
        lf = skia.Path(); lf.moveTo(lx, ly); lf.quadTo(lx + sx * 70, ly - 60 + 50 * droop, lx + sx * 110, ly - 10 + 60 * droop); lf.quadTo(lx + sx * 60, ly + 10, lx, ly); lf.close()
        opath(cv, lf, mix('#6A6A5A', '#3E8A68', grow), 5)
    if bloom > 0.05:
        for k in range(7):
            a = k * 2 * math.pi / 7 + t * 0.2
            pet = skia.Path(); pet.addOval(skia.Rect.MakeXYWH(-22, -90 * bloom - 10, 44, 90 * bloom))
            cv.save(); cv.translate(tx, ty); cv.rotate(math.degrees(a)); opath(cv, pet, '#F0B8C8', 4); cv.restore()
    cv.drawCircle(tx, ty, 34, P('#F0D890' if bloom > 0.05 else '#8A8A6A')); cv.drawCircle(tx, ty, 34, P(OUT, 255, stroke=5))
    pot = skia.Path(); pot.moveTo(x - 120, base - 10); pot.lineTo(x + 120, base - 10); pot.lineTo(x + 90, 1500); pot.lineTo(x - 90, 1500); pot.close(); opath(cv, pot, '#C8704A', 7)
    opath(cv, rect(x - 135, base - 40, 270, 46, 8), '#D8805A', 6)
    ca = clamp((t - 48.9) / 0.5) * (1 - clamp((t - 51.3) / 0.6))
    if ca > 0:                                                  # l'arrosoir
        cx_, cy_ = -150 + 420 * ease(ca), 900
        can(cv, cx_, cy_, 130, -30 * ease(ca))
        if ca > 0.9:
            for k in range(8):
                u = ((t * 2.2 + k / 8) % 1)
                circle(cv, cx_ + 140 + u * 70 + (k % 3) * 8, cy_ - 30 + u * 360, 9, '#9FD8F0')
    for k in range(3):
        u = (t * 0.25 + k / 3) % 1
        if bloom > 0: sym(cv, 'star4', tx + 120 * math.sin(k * 2 + u * 4), ty - u * 300, 14 * (1 - u) * bloom + 1, 0, GOLD, t)


def s_final(cv, t, lt):
    banded_sky(cv, ['#6E5A86', '#8A7096', '#A888A2', '#C29EA8', '#D6B2AC', '#E4C4B0'], -600, 1300, t)
    rise = ease(clamp(lt / 3.0))
    striped_sun(cv, PX, 1450 - 330 * rise, 330 + 6 * bp(t), t, ['#E8C4A8', '#F0D2B4', '#F6E0C0', '#FAEBD0'])
    hill(cv, 1380, 45, 0.006, 1.0, '#8A7096', '#9478A0', t)
    hill(cv, 1540, 55, 0.005, 3.0, '#6A5A86', '#746490', t)
    for x, h, ph, b in ((60, 280, 0, '#F0C8D0'), (1020, 200, 3.1, '#E0D0F0')):
        plant(cv, x, 1760, h, '#4E7A78', b, t, ph, kind=0.9)
    hero(cv, t, 330, 1320, 195, 'open', look=(0.8, 0.3))
    wav = t > 56.3
    kid(cv, t, 780, 1470, 140, 'open', look=(-0.8, -0.2), arms='wave' if wav else None)
    rocket(cv, 780 + 90 * math.cos(t * 1.1), 1110 + 30 * math.sin(t * 2.2), 55, t, 90 + math.degrees(t * 1.1))
    hill(cv, 1830, 25, 0.008, 5.0, '#4A4270', '#544C7A', t, n=3)


# (début, scène, transition d'entrée)
SCENES = [(0.0, s_enfance, None), (12.7, s_noir, 'cut'), (13.62, s_routine, 'flash'), (20.75, s_heures, 'iris'), (25.2, s_cosmos, 'flash'),
          (28.72, s_astronaute, 'wave'), (32.7, s_etoiles, 'iris'), (36.6, s_pris, 'wave'), (38.55, s_possibles, 'iris'),
          (45.85, s_plante, 'wave'), (53.15, s_final, 'iris')]
TW = 0.3


def draw_scene(i, cv, t):
    s0, fn, _ = SCENES[i]; lt = t - s0
    z = 1.0 + 0.03 * ease(clamp(max(0, lt) / 6)) + 0.004 * bp(t)
    cv.save(); cv.translate(PX, PY); cv.scale(z, z); cv.translate(-PX, -PY); fn(cv, t, max(0.0, lt)); cv.restore()


def mask(kind, p):
    if kind == 'iris': return skia.Path().addCircle(PX, PY, 2000 * ease(p) ** 1.3)
    y = H + 250 - (H + 700) * ease(p)
    m = skia.Path(); m.moveTo(-700, H + 700)
    for x in range(-700, W + 701, 20): m.lineTo(x, y + 60 * math.sin(x * 0.006 + p * 6))
    m.lineTo(W + 700, H + 700); m.close(); return m


def scene(cv, t):
    i = 0
    for k, (s0, _, kind) in enumerate(SCENES):
        if t >= s0 - (TW if kind in ('iris', 'wave') else 0): i = k
    s0, _, kind = SCENES[i]
    if kind in ('iris', 'wave') and t < s0 + TW:
        p = (t - (s0 - TW)) / (2 * TW)
        draw_scene(i - 1, cv, t); m = mask(kind, p)
        cv.save(); cv.clipPath(m, doAntiAlias=True); draw_scene(i, cv, t); cv.restore()
        cv.drawPath(m, P(OUT, 255, stroke=16)); cv.drawPath(m, P(CREAM, 255, stroke=5))
    else:
        draw_scene(i, cv, t)
        if kind == 'flash' and t - s0 < 0.45:                  # anneau net qui part du troisième œil, sur l'impact
            u = ease_out((t - s0) / 0.45)
            cv.drawCircle(PX, PY, 40 + 1600 * u, P(OUT, int(255 * (1 - u)), stroke=26)); cv.drawCircle(PX, PY, 40 + 1600 * u, P(CREAM, int(255 * (1 - u)), stroke=10))


def frame(fi):
    t = fi / FPS
    surf = skia.Surface(OW_, OH_); cv = surf.getCanvas(); cv.scale(SC, SC)
    cv.save(); cv.translate(PX, PY); cv.rotate(0.3 * math.sin(t * 0.35)); cv.scale(1.03, 1.03)
    cv.translate(-PX + 8 * math.sin(t * 0.4), -PY + 8 * math.cos(t * 0.33))
    scene(cv, t); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1250, [C('#000000', 0), C('#000000', 0), C('#000000', 70)], [0, 0.7, 1])))
    draw_word(cv, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        from PIL import Image
        for ts in sys.argv[2].split(','):
            arr = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH_, OW_, 4)
            Image.fromarray(arr[..., :3]).resize((540, 960), Image.LANCZOS).save(os.path.join(sys.argv[3], f'pv_{ts}.png'))
        sys.exit()
    out = os.path.join(HERE, 'travail_reves_4k.mp4'); hd = os.path.join(HERE, 'travail_reves_1080p.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(HERE, 'voice.wav'),
                           '-filter_complex', '[0:v]format=yuv420p,split=2[v4][vh];[vh]scale=1080:1920:flags=lanczos[v1]',
                           # 4K compatible téléphones : H.264 High, niveau 5.1
                           '-map', '[v4]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '5.1', '-preset', 'slow', '-crf', '15',
                           '-maxrate', '25M', '-bufsize', '50M', '-c:a', 'aac', '-b:a', '256k', '-t', str(DUR), '-movflags', '+faststart', out,
                           # Full HD haute qualité
                           '-map', '[v1]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '4.2', '-preset', 'slow', '-crf', '14',
                           '-maxrate', '20M', '-bufsize', '40M', '-c:a', 'aac', '-b:a', '256k', '-t', str(DUR), '-movflags', '+faststart', hd],
                          stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=2)):
            ff.stdin.write(b)
            if i % 300 == 0: print(i, '/', n, flush=True)
    ff.stdin.close(); ff.wait()
    # version de contrôle avec le son de référence (pour vérifier le calage, à ne pas publier)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', hd, '-i', os.path.join(HERE, '..', 'son', 'son_reference.wav'),
                    '-filter_complex', '[1:a]volume=0.35,aresample=44100,aformat=channel_layouts=stereo[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', os.path.join(HERE, 'CONTROLE_calage_avec_son.mp4')])
    print('ok')

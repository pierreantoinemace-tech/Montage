"""« Tu n'es pas en retard » — vertical 4K (2160x3840), 30 fps. Décors abstraits sombres façon Midnight Gospel, perso aux trois yeux."""
import math, os, random, sys, json, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vertical'))
import extrait2 as X
import extrait3 as D
from extrait2 import W, H, SC, OW_, OH_, PX, PY, HS, HERO, OTHER, FONT, TY, pd, clamp, back, hero
from extrait3 import banded_sky, hill, mesa, striped_sun, plant, island, figure, floating_ring, pyramid, dots, BIG
import numpy as np, skia
from lib import P, C, mix, lin, rad, circle, ease, ease_out
from symboles import sym, OUT, eye
import mg

FPS = 30
CREAM = '#F0EBBE'; GOLD = '#FFE680'

# ---------------- mots ----------------
KEYS = {"D'AVANCE", "APPART", "MARIE", "BOÎTE", "LIT", "RATÉ", "COULISSES", "BANDE-ANNONCE", "DOUTES", "CALENDRIER", "VOIE",
        "TRENTE", "QUARANTE", "ROBE", "CINQUANTE", "D'ARRIVÉE", "CHRONO", "MONTRE", "COURSE", "BALADE", "CHEMIN", "VITESSE",
        "RETARD", "ÊTRE", "ARRIVE"}


def load_words():
    raw = json.load(open(os.path.join(HERE, 'words.json')))
    toks = []
    for w, s, e in raw:
        if w and w[0] in "'-" and toks:
            toks[-1][0] += w; toks[-1][2] = e; continue
        if w.strip('?!.,…') == '': continue
        toks.append([w, s, e])
    out = []
    for i, (w, s, e) in enumerate(toks):
        txt = w.strip(',.?!…').upper().replace('’', "'")
        if txt == 'OUT': txt = 'TOUT'
        nxt = toks[i + 1][1] if i + 1 < len(toks) else e + 1.2
        end = nxt if nxt - e < 0.7 else e + 0.35
        out.append((txt, s + 0.25, end + 0.25, txt in KEYS))   # +0.25 : décalage du adelay
    return out


WORDS = load_words()
X.WORDS = [(w, s, k) for w, s, e, k in WORDS]          # pour la pulsation du troisième œil
DUR = 50.25


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


# ---------------- petits outils ----------------
def bez(p0, p1, p2, p3, u):
    a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; c = 3 * (1 - u) * u ** 2; d = u ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def road(cv, pts, w0, w1, col, line=CREAM, trim=1.0, a=255):
    n = max(2, int(len(pts) * trim))
    pts = pts[:n]
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        j = min(i + 1, len(pts) - 1); k = max(i - 1, 0)
        dx, dy = pts[j][0] - pts[k][0], pts[j][1] - pts[k][1]; d = math.hypot(dx, dy) or 1
        w = (w0 + (w1 - w0) * i / max(1, len(pts) - 1)) / 2
        L.append((x - dy / d * w, y + dx / d * w)); R.append((x + dy / d * w, y - dx / d * w))
    p = skia.Path(); p.moveTo(*L[0])
    for q in L[1:]: p.lineTo(*q)
    for q in reversed(R): p.lineTo(*q)
    p.close()
    cv.drawPath(p, P(col, a)); cv.drawPath(p, P(OUT, a, stroke=5))
    c = skia.Path(); c.moveTo(*pts[0])
    for q in pts[1:]: c.lineTo(*q)
    pa = P(line, int(a * 0.7), stroke=max(3, w0 * 0.05)); pa.setPathEffect(skia.DashPathEffect.Make([30, 28], 0)); cv.drawPath(c, pa)


def opath(cv, p, col, w=5, a=255):
    cv.drawPath(p, P(col, a)); cv.drawPath(p, P(OUT, a, stroke=w))


def rect(x, y, w, h, r=0):
    p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return p


def pop(lt, t0, d=0.5):
    return back(clamp((lt - t0) / d)) if lt >= t0 else 0.0


def center_hero(cv, t, eyes='open', look=(0.2, -0.8), s=HS, pal=HERO):
    hero(cv, t, PX, PY + 0.55 * s, s, eyes, look=look, pal=pal)


SKY_NIGHT = ['#0A0716', '#100A20', '#170E2C', '#1F1238', '#2A1744', '#381D50']


# ---------------- scènes ----------------
def s_hook(cv, t, lt):
    banded_sky(cv, SKY_NIGHT, -600, 1250, t)
    dots(cv, 1, 110, (-100, -100, W + 100, 900), '#B8A8D0')
    striped_sun(cv, 760, 360, 150, t, ['#4A2350', '#5A2C5C', '#6C3666', '#7E4270'])
    hill(cv, 1250, 40, 0.006, 0.3, '#2A1A40', '#33214C', t)
    P0, P1, P2, P3 = (540, 2000), (60, 1500), (1080, 1000), (640, 380)
    pts = [bez(P0, P1, P2, P3, i / 80) for i in range(81)]
    road(cv, pts, 300, 20, '#3A2A58')
    for k in range(6):                       # les autres, loin devant
        u = 0.42 + k * 0.085 + 0.012 * t
        u = 0.42 + (u - 0.42) % 0.52
        x, y = bez(P0, P1, P2, P3, u)
        figure(cv, x, y, 34 * (1.15 - u), ['#C8A8D8', '#8FC8C0', '#E0B890', '#D89AAE', '#A8B8E0', '#C8A8D8'][k])
    hill(cv, 1600, 50, 0.005, 2.0, '#1A2438', '#223048', t)
    for x, h, ph, b in ((80, 260, 0, '#C8A8D8'), (1010, 230, 2.2, '#D89AAE')):
        plant(cv, x, 1720, h, '#2E5A5A', b, t, ph)
    center_hero(cv, t, look=(0.5, -1.0))


def house(cv, x, y, s, t):
    opath(cv, rect(x - s * 0.5, y - s * 0.8, s, s * 0.8), '#6A5A8A')
    roof = skia.Path(); roof.moveTo(x - s * 0.65, y - s * 0.78); roof.lineTo(x, y - s * 1.3); roof.lineTo(x + s * 0.65, y - s * 0.78); roof.close()
    opath(cv, roof, '#8A4A6A')
    opath(cv, rect(x - s * 0.32, y - s * 0.6, s * 0.24, s * 0.22, 4), GOLD, 4)
    opath(cv, rect(x + s * 0.08, y - s * 0.45, s * 0.22, s * 0.45, 4), '#3A2A50', 4)


def arch(cv, x, y, s, t):
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - s * 0.6, y - s * 1.4, x + s * 0.6, y - s * 0.2), 180, 180)
    cv.drawPath(p, P(OUT, 255, stroke=s * 0.16 + 9)); cv.drawPath(p, P('#E0B8C8', 255, stroke=s * 0.16))
    for sx in (-0.6, 0.6): cv.drawLine(x + sx * s, y - s * 0.8, x + sx * s, y, P(OUT, 255, stroke=s * 0.16 + 9)); cv.drawLine(x + sx * s, y - s * 0.8, x + sx * s, y, P('#E0B8C8', 255, stroke=s * 0.16))
    figure(cv, x - s * 0.2, y, s * 0.36, '#F0EBE0'); figure(cv, x + s * 0.22, y, s * 0.38, '#3A3050')
    rnd = random.Random(4)
    for k in range(10):
        px = x + rnd.uniform(-s, s); py = y - s * 1.6 + ((t * 40 + rnd.uniform(0, 300)) % (s * 1.7))
        circle(cv, px, py, 6, rnd.choice(['#FFB8D0', '#F0EBBE', '#C8B8FF']))


def tower(cv, x, y, s, t):
    for k, (w, h) in enumerate(((1.0, 0.7), (0.75, 0.6), (0.5, 0.55))):
        yb = y - sum(hh for _, hh in ((1.0, 0.7), (0.75, 0.6), (0.5, 0.55))[:k]) * s
        opath(cv, rect(x - w * s / 2, yb - h * s, w * s, h * s, 6), ['#3E5A6A', '#4A6A7A', '#5A7A8A'][k])
        for j in range(3):
            if (j + k) % 2 == 0: opath(cv, rect(x - w * s / 2 + 14 + j * w * s * 0.3, yb - h * s + 18, w * s * 0.16, h * s * 0.3, 3), GOLD, 3)
    top = y - 1.85 * s
    cv.drawLine(x, top, x, top - s * 0.5, P(OUT, 255, stroke=6))
    fl = skia.Path(); fl.moveTo(x, top - s * 0.5)
    for i in range(9):
        u = i / 8; fl.lineTo(x + u * s * 0.4, top - s * 0.5 + 8 * math.sin(u * 6 + t * 5) * u)
    for i in range(8, -1, -1):
        u = i / 8; fl.lineTo(x + u * s * 0.4, top - s * 0.3 + 8 * math.sin(u * 6 + t * 5) * u)
    fl.close(); opath(cv, fl, '#D89AAE', 4)


def s_iles(cv, t, lt):
    banded_sky(cv, ['#0E0A1E', '#160E2C', '#1E1238', '#281644', '#331A4E', '#3E1E56'], -600, 1500, t)
    dots(cv, 3, 120, (-100, -100, W + 100, 1600), '#B8A8D0')
    floating_ring(cv, 560, 230, 90, t, '#3E5A6A', '#5A7A86', 0)
    for (x, y, w, t0, fn, ph) in ((250, 560, 330, 0.0, house, 0), (830, 1060, 330, 1.85, arch, 1.3), (260, 1290, 300, 3.45, tower, 2.6)):
        s = pop(lt, t0)
        if s <= 0.01: continue
        cv.save(); cv.translate(x, y + (1 - min(1, s)) * 300); cv.scale(s, s); cv.translate(-x, -y)
        yy = island(cv, x, y, w, '#2A3C4C', '#1C1630', '#251E3C', t, ph)
        fn(cv, x, yy, w * 0.42, t)
        cv.restore()
    hero(cv, t, 720, 1560, 175, 'lidded', look=(-0.6, -0.8))


def s_lit(cv, t, lt):
    banded_sky(cv, ['#03050C', '#060A16', '#0A0F20', '#0E152A', '#131B34', '#18213C'], -600, 1600, t)
    dots(cv, 2, 170, (-100, -100, W + 100, H), '#9AA8C8')
    cv.drawCircle(850, 230, 95, P('#BDB6CE')); cv.drawCircle(850, 230, 95, P(OUT, 255, stroke=5))
    for cx_, cy_, r_ in ((820, 210, 18), (875, 260, 12), (860, 190, 9)): cv.drawCircle(cx_, cy_, r_, P('#A49CB8'))
    s = HS; cy = PY + 0.55 * s
    opath(cv, rect(PX - 1.45 * s, cy - 0.9 * s, 2.9 * s, 1.9 * s, 0.5 * s), '#3A3A6A', 6)
    cv.drawLine(PX - 1.2 * s, cy - 0.3 * s, PX + 1.2 * s, cy - 0.3 * s, P('#44447A', 255, stroke=5))
    center_hero(cv, t, 'open', look=(-0.3, -1.0))
    y0 = cy + 1.05 * s
    bl = skia.Path(); bl.moveTo(-200, H + 300)
    for x in range(-200, W + 201, 20): bl.lineTo(x, y0 + 25 * math.sin(x * 0.009 + t * 0.6))
    bl.lineTo(W + 200, H + 300); bl.close()
    cv.drawPath(bl, P('#2A3A6A')); cv.save(); cv.clipPath(bl, doAntiAlias=True)
    for k in range(-4, 14):
        cv.drawLine(k * 110 - 200, y0 - 40, k * 110 + 100, H + 200, P('#34467A', 255, stroke=14))
    for k in range(1, 6):
        q = skia.Path(); q.moveTo(-200, y0 + k * 70)
        for x in range(-200, W + 201, 20): q.lineTo(x, y0 + k * 70 + 25 * math.sin(x * 0.009 + t * 0.6))
        cv.drawPath(q, P('#22305A', 255, stroke=6))
    cv.restore(); cv.drawPath(bl, P(OUT, 255, stroke=6))
    rnd = random.Random(8)                    # petites questions sombres qui flottent
    for k in range(5):
        x = rnd.uniform(120, 960); y = rnd.uniform(300, 640) + 14 * math.sin(t + k)
        sc_ = pop(lt, 2.9 + k * 0.25, 0.4)
        if sc_ > 0: sym(cv, 'spiral', x, y, 26 * sc_, t * 20, '#5A5A8A', t)


def curtain(cv, x0, x1, t, left=True):
    p = skia.Path(); p.moveTo(x0, -100); p.lineTo(x1, -100)
    for i in range(41):
        y = -100 + i * 55
        sway = 14 * math.sin(i * 0.4 + t * 0.8)
        xx = (x1 if left else x0) + sway - (90 * (i / 40) ** 2 if left else -90 * (i / 40) ** 2)
        p.lineTo(xx, y)
    p.lineTo(x0 if left else x1, H + 100); p.close()
    if not left:
        p = skia.Path(); p.moveTo(x1, -100); p.lineTo(x0, -100)
        for i in range(41):
            y = -100 + i * 55; sway = 14 * math.sin(i * 0.4 + t * 0.8)
            p.lineTo(x0 + sway + 90 * (i / 40) ** 2, y)
        p.lineTo(x1, H + 100); p.close()
    cv.drawPath(p, P('#4A1530')); cv.save(); cv.clipPath(p, doAntiAlias=True)
    for k in range(int(x0) - 40, int(x1) + 40, 46): cv.drawLine(k, -100, k + 20, H + 100, P('#5E1E3C', 255, stroke=16))
    cv.restore(); cv.drawPath(p, P(OUT, 255, stroke=6))


def mini_trailer(cv, x, y, w, h, t):
    cv.save(); cv.clipPath(rect(x, y, w, h, 18), doAntiAlias=True)
    cv.translate(x, y)
    cols = ['#F6E0C0', '#F0C8B0', '#E8B0A8', '#D898A8']
    for i, c in enumerate(cols): cv.drawRect(skia.Rect.MakeXYWH(0, i * h / 4, w, h / 4 + 2), P(c))
    striped_sun(cv, w / 2, h * 0.62, h * 0.32, t, ['#FFD8A0', '#FFE4B8', '#FFF0D0'])
    hl = skia.Path(); hl.moveTo(0, h)
    for xx in range(0, int(w) + 11, 10): hl.lineTo(xx, h * 0.8 - 30 * math.sin(xx * 0.012 + 1))
    hl.lineTo(w, h); hl.close(); opath(cv, hl, '#B8D8C0', 4)
    for k, xx in enumerate((w * 0.3, w * 0.5, w * 0.7)):
        figure(cv, xx, h * 0.8 - 10, 40, ['#8A6AAA', '#C86A8A', '#4A8A9A'][k])
        cv.drawLine(xx - 14, h * 0.8 - 60, xx - 30, h * 0.8 - 95 - 8 * math.sin(t * 6 + k), P(OUT, 255, stroke=6))
        cv.drawLine(xx + 14, h * 0.8 - 60, xx + 30, h * 0.8 - 95 - 8 * math.sin(t * 6 + k + 1), P(OUT, 255, stroke=6))
    for k in range(7):
        sym(cv, 'star4', (k * 137 + t * 60) % w, 40 + (k * 53) % (h * 0.4), 12, 0, '#FFFFFF', t)
    cv.restore()
    cv.drawPath(rect(x, y, w, h, 18), P(OUT, 255, stroke=10)); cv.drawPath(rect(x - 6, y - 6, w + 12, h + 12, 22), P(GOLD, 255, stroke=4))


def s_coulisses(cv, t, lt):
    cv.drawRect(BIG, P('#120A1C'))
    for k in range(9):                        # faisceau net et transparent depuis l'écran
        p = skia.Path(); p.moveTo(PX - 300 + k * 75, 640); p.lineTo(PX - 500 + k * 125, 2000); p.lineTo(PX - 470 + k * 125, 2000); p.lineTo(PX - 290 + k * 75, 640); p.close()
        cv.drawPath(p, P('#F6E0C0', 14))
    mini_trailer(cv, 170, 170, 740, 450, t)
    cv.drawRect(skia.Rect.MakeLTRB(-100, 1700, W + 100, H + 300), P('#1E1428')); cv.drawLine(-100, 1700, W + 100, 1700, P(OUT, 255, stroke=6))
    for x, y, w_, h_ in ((60, 1560, 150, 140), (190, 1610, 110, 90), (880, 1580, 140, 120)):   # caisses
        opath(cv, rect(x, y, w_, h_, 6), '#3A2A3A'); cv.drawLine(x, y, x + w_, y + h_, P(OUT, 255, stroke=4))
    for x in (140, 950):                      # cordes
        cv.drawLine(x, -50, x, 1300, P(OUT, 255, stroke=9)); cv.drawLine(x, -50, x, 1300, P('#8A6A4A', 255, stroke=4))
        opath(cv, skia.Path().addCircle(x, 1330, 34), '#6A4A3A')
    curtain(cv, -200, 110, t, True); curtain(cv, 970, W + 200, t, False)
    center_hero(cv, t, 'lidded', look=(0.0, -1.0), s=205)


def polaroid(cv, x, y, w, rot, t, seed, cloud):
    cv.save(); cv.translate(x, y); cv.rotate(rot + 3 * math.sin(t * 0.6 + seed))
    if cloud > 0:                              # les doutes, derrière
        cv.save(); cv.translate(w * 0.25, -w * 0.15); cv.scale(cloud, cloud)
        cl = skia.Path()
        for cx_, cy_, r_ in ((-w * 0.3, 0, w * 0.4), (0, -w * 0.2, w * 0.45), (w * 0.35, 0, w * 0.38), (0, w * 0.15, w * 0.4)): cl.addCircle(cx_, cy_, r_)
        cl = skia.Op(cl, skia.Path(), skia.PathOp.kUnion_PathOp) or cl
        opath(cv, cl, '#1A1428', 6)
        rnd = random.Random(seed)
        sc = skia.Path(); sc.moveTo(-w * 0.4, 0)
        for i in range(22): sc.lineTo(rnd.uniform(-w * 0.45, w * 0.45), rnd.uniform(-w * 0.35, w * 0.3))
        cv.drawPath(sc, P('#3A3050', 255, stroke=4))
        for i in range(6):
            yy = w * 0.5 + ((t * 200 + i * 47) % (w * 0.6))
            cv.drawLine(-w * 0.3 + i * w * 0.12, yy, -w * 0.32 + i * w * 0.12, yy + 26, P('#5A6A9A', 255, stroke=4))
        cv.restore()
    opath(cv, rect(-w / 2, -w * 0.6, w, w * 1.2, 8), '#F4EEE4', 6)
    inner = rect(-w * 0.42, -w * 0.52, w * 0.84, w * 0.84, 4)
    cv.save(); cv.clipPath(inner, doAntiAlias=True)
    cols = [['#F6D8B8', '#F0B8A8'], ['#B8E0E0', '#D8C8F0'], ['#F8E0A8', '#F0B8C8']][seed % 3]
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -w * 0.6, w, w * 0.5), P(cols[0])); cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -w * 0.1, w, w * 0.6), P(cols[1]))
    if seed % 3 == 0: striped_sun(cv, 0, -w * 0.1, w * 0.22, t, ['#FFD8A0', '#FFE8C0'])
    elif seed % 3 == 1: sym(cv, 'star8', 0, -w * 0.12, w * 0.2, t * 30, '#FFB8D0', t)
    else: sym(cv, 'sun', 0, -w * 0.12, w * 0.2, 0, '#FFD8A0', t)
    figure(cv, -w * 0.12, w * 0.28, w * 0.13, '#6A4A8A'); figure(cv, w * 0.14, w * 0.28, w * 0.12, '#C86A8A')
    cv.restore(); cv.drawPath(inner, P(OUT, 255, stroke=4))
    cv.restore()


def s_moments(cv, t, lt):
    banded_sky(cv, ['#120A22', '#1A0E2E', '#22123A', '#2A1646', '#331A50', '#3C1E58'], -600, 1500, t)
    dots(cv, 5, 120, (-100, -100, W + 100, 1600), '#B8A8D0')
    cl = ease_out(clamp((lt - 1.45) / 0.7))
    for x, y, w, rot, sd in ((250, 400, 260, -9, 0), (830, 520, 230, 8, 1), (870, 1180, 210, -5, 2), (200, 1120, 200, 6, 3)):
        polaroid(cv, x, y + 12 * math.sin(t * 0.7 + sd), w, rot, t, sd, cl)
    hill(cv, 1700, 30, 0.007, 1.0, '#1A1830', '#22203C', t, n=3)
    center_hero(cv, t, 'lidded', look=(0.6, -0.6), s=200)


def cal_page(cv, x, y, w, rot, num, col, flip=0.0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(1, max(0.05, 1 - flip))
    h = w * 1.15
    opath(cv, rect(-w / 2, -h / 2, w, h, 14), '#EFE6D8', 6)
    top = rect(-w / 2, -h / 2, w, h * 0.27, 14); cv.drawPath(top, P(col)); cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2 + h * 0.15, w, h * 0.12), P(col))
    cv.drawLine(-w / 2, -h / 2 + h * 0.27, w / 2, -h / 2 + h * 0.27, P(OUT, 255, stroke=5)); cv.drawPath(rect(-w / 2, -h / 2, w, h, 14), P(OUT, 255, stroke=6))
    for k in (-0.25, 0.25): cv.drawCircle(k * w, -h / 2 + 4, w * 0.05, P(OUT))
    f = skia.Font(FONT, h * 0.42); tw = f.measureText(num)
    cv.drawString(num, -tw / 2, h * 0.32, f, P('#2A1E3A'))
    cv.restore()


def s_calendrier(cv, t, lt):
    banded_sky(cv, ['#06121A', '#0A1A24', '#0E222E', '#122A38', '#163242', '#1A3A4A'], -600, 1500, t)
    dots(cv, 6, 120, (-100, -100, W + 100, 1600), '#A8C8D0')
    rnd = random.Random(12)
    for k in range(11):
        sp = rnd.uniform(40, 110); x0 = rnd.uniform(-50, W + 50); ph = rnd.uniform(0, 2400); dirx = rnd.uniform(-0.4, 0.4)
        y = (ph + t * sp) % 2400 - 300; x = x0 + dirx * y * 0.3 + 30 * math.sin(t * 0.5 + k)
        num = str(rnd.randint(1, 31)); col = rnd.choice(['#8A4A6A', '#3E6A7A', '#6A5A9A', '#9A6A4A'])
        flip = max(0.0, math.sin(t * rnd.uniform(0.8, 1.6) + k)) ** 8
        cal_page(cv, x, y, rnd.uniform(90, 170), rnd.uniform(-25, 25) + t * rnd.uniform(-8, 8), num, col, flip)
    hill(cv, 1760, 30, 0.007, 2.0, '#0C1C24', '#12262E', t, n=3)
    center_hero(cv, t, 'open', look=(0.6, -0.9))


def s_chemins(cv, t, lt):
    banded_sky(cv, ['#0E0A1E', '#160E2C', '#20123A', '#2C1846', '#3A1E50', '#4A2658'], -600, 1100, t)
    dots(cv, 7, 90, (-100, -100, W + 100, 900), '#B8A8D0')
    striped_sun(cv, PX, 1080, 230, t, ['#5A2A50', '#6C3460', '#7E406E'])
    hill(cv, 1080, 30, 0.006, 0.5, '#2A1A40', '#33214C', t)
    hill(cv, 1200, 40, 0.005, 2.5, '#22223E', '#2A2A4A', t, n=8, gap=45)
    hz = 1110
    A = [bez((170, 2000), (100, 1600), (420, 1350), (400, hz), i / 60) for i in range(61)]
    B = [bez((540, 2000), (620, 1600), (470, 1350), (545, hz), i / 60) for i in range(61)]
    Cc = [bez((920, 2000), (1000, 1600), (640, 1350), (690, hz), i / 60) for i in range(61)]
    road(cv, A, 220, 20, '#3A2A58')
    gap = ease(clamp((lt - 2.0) / 0.6))       # « la perdent à trente »
    road(cv, B[:30], 220, 120, '#3A2A58')
    road(cv, [(x, y - 40 * gap) for x, y in B[36:]], 100, 20, '#3A2A58', a=int(255 * (1 - 0.6 * gap)))
    if lt > 3.2: road(cv, Cc, 220, 20, '#3A4A58', trim=ease(clamp((lt - 3.2) / 1.2)))
    for k, (path, t0, col) in enumerate(((A, 0.0, '#8FC8C0'), (B, 0.0, '#D89AAE'), (Cc, 3.6, '#E0B890'))):
        if lt < t0: continue
        u = clamp(0.15 + (lt - t0) * 0.08)
        if k == 1: u = min(u, 0.45)
        i = int(u * 60); x, y = path[i]
        figure(cv, x, y, 46 * (1.2 - u), col)


def dress(cv, x, y, s, t):
    cv.drawLine(x, y, x, y - s * 0.4, P(OUT, 255, stroke=8))
    sk = skia.Path(); sk.moveTo(x - s * 0.16, y - s * 1.1); sk.quadTo(x - s * 0.3, y - s * 0.7, x - s * 0.55, y - s * 0.35)
    for i in range(7): sk.quadTo(x - s * 0.55 + (i + 0.5) * s * 1.1 / 7, y - s * 0.28 + 10 * math.sin(t * 2 + i), x - s * 0.55 + (i + 1) * s * 1.1 / 7, y - s * 0.35)
    sk.quadTo(x + s * 0.3, y - s * 0.7, x + s * 0.16, y - s * 1.1); sk.close()
    opath(cv, sk, '#F4EEF4', 6)
    cv.save(); cv.clipPath(sk, doAntiAlias=True)
    for k in range(8): cv.drawLine(x - s + k * s * 0.28, y - s * 1.2, x - s * 0.7 + k * s * 0.28, y, P('#E0D0E8', 255, stroke=8))
    cv.restore()
    bod = skia.Path(); bod.moveTo(x - s * 0.18, y - s * 1.45); bod.quadTo(x, y - s * 1.55, x + s * 0.18, y - s * 1.45); bod.lineTo(x + s * 0.16, y - s * 1.08); bod.lineTo(x - s * 0.16, y - s * 1.08); bod.close()
    opath(cv, bod, '#F4EEF4', 6)
    cv.drawCircle(x, y - s * 1.6, s * 0.09, P('#6A5A7A')); cv.drawCircle(x, y - s * 1.6, s * 0.09, P(OUT, 255, stroke=4))


def s_tardifs(cv, t, lt):
    banded_sky(cv, ['#0A0716', '#120C24', '#1A1032', '#22143E', '#2C184A', '#361C54'], -600, 1700, t)
    dots(cv, 9, 150, (-100, -100, W + 100, H), '#B8A8D0')
    sym(cv, 'planet', 850, 260, 110, 0, '#6A5A8A', t)
    s1 = pop(lt, 0.0, 0.6)
    if s1 > 0:
        x, y = 300, 640
        cv.save(); cv.translate(x, y + (1 - min(1, s1)) * 260); cv.scale(s1, s1); cv.translate(-x, -y)
        yy = island(cv, x, y, 360, '#2A3C4C', '#1C1630', '#251E3C', t, 0)
        dress(cv, x, yy, 170, t)
        cv.restore()
    s2 = pop(lt, 3.45, 0.6)
    if s2 > 0:
        x, y = 760, 1350
        cv.save(); cv.translate(x, y + (1 - min(1, s2)) * 260); cv.scale(s2, s2); cv.translate(-x, -y)
        beam = skia.Path(); beam.moveTo(x - 40, -100); beam.lineTo(x + 40, -100); beam.lineTo(x + 170, y); beam.lineTo(x - 170, y); beam.close()
        cv.drawPath(beam, P('#FFF0C0', 45))
        yy = island(cv, x, y, 380, '#2A3C4C', '#1C1630', '#251E3C', t, 1.3)
        cv.drawOval(skia.Rect.MakeLTRB(x - 150, yy - 22, x + 150, yy + 22), P('#FFF0C0', 120))
        figure(cv, x, yy, 70, '#E0B890')
        for k in range(6):
            g = k * math.pi / 3 + t
            sym(cv, 'star4', x + math.cos(g) * 110, yy - 90 + math.sin(g) * 50, 14, 0, GOLD, t)
        cv.restore()


def s_course(cv, t, lt):
    banded_sky(cv, ['#0A0716', '#100A20', '#170E2C', '#1F1238', '#2A1744', '#381D50'], -600, 1000, t)
    dots(cv, 10, 200, (-100, -100, W + 100, 1000), '#C8B8E0')
    vx, vy = PX, 1000
    ground = skia.Path(); ground.addRect(skia.Rect.MakeLTRB(-600, vy, W + 600, H + 600))
    cv.drawPath(ground, P('#1A1430'))
    for k in range(8):                          # couloirs qui filent vers l'horizon et s'effacent
        xb = -500 + k * 300
        lane = skia.Path(); lane.moveTo(xb, H + 200); lane.lineTo(xb + 300, H + 200); lane.lineTo(vx + (xb + 300 - PX) * 0.04, vy); lane.lineTo(vx + (xb - PX) * 0.04, vy); lane.close()
        cv.drawPath(lane, P(['#4A2234', '#562A3E'][k % 2]))
        cv.drawLine(xb, H + 200, vx + (xb - PX) * 0.04, vy, P(CREAM, 200, stroke=5))
    off = (t * 120) % 140
    for j in range(14):                         # marquages qui défilent
        u = ((j * 140 + off) % 1960) / 1960
        y = vy + (H + 200 - vy) * u ** 2
        cv.drawLine(PX - 600 * u ** 2, y, PX + 600 * u ** 2, y, P('#6A3448', 255, stroke=2 + 6 * u))
    rnd = random.Random(14)
    for k in range(40):                         # l'horizon se dissout en points
        x = rnd.uniform(200, 880); y = vy - rnd.uniform(0, 260) - (t * 30 + k * 13) % 200
        circle(cv, x, y, rnd.uniform(2, 5), CREAM, 200)
    cv.drawLine(-600, vy, W + 600, vy, P(OUT, 255, stroke=6))
    for (x, y, r, ph) in ((180, 520, 70, 0), (900, 640, 55, 1.5), (760, 280, 40, 3)):
        mg.melting_clock(cv, x + 14 * math.sin(t * 0.5 + ph), y + 16 * math.sin(t * 0.7 + ph), r, t, face='#B8A27A', speed=0.5)
    ey_ = 1350; closed = clamp((lt - 2.9) / 0.4)   # « personne ne te regarde »
    cv.save(); cv.translate(PX, ey_ + 10 * math.sin(t * 0.8))
    if closed < 1: eye(cv, 120, '#8A6AAA', t if closed == 0 else 0, (0.0, 0.3))
    if closed > 0:
        p = skia.Path(); p.moveTo(-120, 0); p.quadTo(0, -114 * (1 - closed), 120, 0); p.quadTo(0, 114, -120, 0); p.close()
        opath(cv, p, '#5A4A7A', 7)
        if closed >= 1:
            for k in range(5): cv.drawLine(-80 + k * 40, 50, -90 + k * 45, 80, P(OUT, 255, stroke=5))
    cv.restore()


def s_balade(cv, t, lt):
    banded_sky(cv, ['#1E1838', '#2A2048', '#3A2A58', '#4C3466', '#5E4072', '#704C7C'], -600, 1150, t)
    dots(cv, 11, 80, (-100, -100, W + 100, 800), '#D8C8E0')
    striped_sun(cv, 820, 400, 130, t, ['#9A6A8A', '#AA7A92', '#BC8C9A'])
    hill(cv, 1150, 40, 0.006, 0.8, '#3A2E58', '#433664', t)
    hill(cv, 1330, 50, 0.005, 2.6, '#2E2A4E', '#36325A', t, n=7, gap=40)
    paths = [((-100, 1250), (300, 1100), (500, 1300), (1200, 1180)), ((-100, 1450), (400, 1350), (700, 1550), (1200, 1400)),
             ((150, 1050), (350, 1250), (700, 1000), (950, 1150)), ((-100, 1650), (300, 1550), (800, 1750), (1200, 1600))]
    speeds = [0.035, 0.07, 0.02, 0.05]
    for k, pth in enumerate(paths):
        pts = [bez(*pth, i / 60) for i in range(61)]
        c = skia.Path(); c.moveTo(*pts[0])
        for q in pts[1:]: c.lineTo(*q)
        cv.drawPath(c, P(OUT, 255, stroke=16)); cv.drawPath(c, P('#8A7AA8', 255, stroke=9))
        pa = P(CREAM, 200, stroke=3); pa.setPathEffect(skia.DashPathEffect.Make([16, 18], 0)); cv.drawPath(c, pa)
        for j in range(2):
            u = (t * speeds[k] + j * 0.5 + k * 0.17) % 1
            x, y = bez(*pth, u)
            figure(cv, x, y - 4, 30, ['#C8A8D8', '#8FC8C0', '#E0B890', '#D89AAE'][(k + j) % 4])
    for x, h, ph, b in ((70, 240, 0, '#E0B8C8'), (1010, 210, 2.2, '#E8C8A8')):
        plant(cv, x, 1800, h, '#3E6A68', b, t, ph)
    hero(cv, t, PX, 1560, 170, 'lidded', look=(0.3, -0.5))


def s_ici(cv, t, lt):
    banded_sky(cv, ['#3A2E52', '#4E3C66', '#664C78', '#7E5E86', '#967090', '#A98296'], -600, 1500, t)
    dots(cv, 13, 60, (-100, -100, W + 100, 700), '#F0E0F0')
    top = 1810
    for k in range(4):                          # « tu es ici » : ondes au sol
        u = ((t * 0.35 + k / 4) % 1)
        cv.drawOval(skia.Rect.MakeLTRB(PX - 200 - u * 500, top - 30 - u * 80, PX + 200 + u * 500, top + 30 + u * 80), P(GOLD, int(220 * (1 - u)), stroke=5))
    old = pd.S; pd.S = top - 30
    center_hero(cv, t, 'open', look=(0.0, 0.1))
    pd.S = old
    island(cv, PX, top, 980, '#4A5A6A', '#3A2E4E', '#463A5A', 0, 0)
    for x, h, ph, b in ((160, 170, 0.5, '#B8D8D0'), (920, 150, 2.8, '#E0B8C8')):
        plant(cv, x, top + 6, h, '#3E6A68', b, t, ph, kind=0.6)
    s = pop(lt, 0.2, 0.6)                       # épingle « tu es ici »
    if s > 0:
        x, y = PX, 470 + 12 * math.sin(t * 1.2)
        cv.save(); cv.translate(x, y); cv.scale(s, s)
        pin = skia.Path(); pin.moveTo(0, 90); pin.cubicTo(-40, 40, -70, 0, -70, -40); pin.cubicTo(-70, -80, -38, -112, 0, -112)
        pin.cubicTo(38, -112, 70, -80, 70, -40); pin.cubicTo(70, 0, 40, 40, 0, 90); pin.close()
        opath(cv, pin, '#E8A0A8', 7); opath(cv, skia.Path().addCircle(0, -42, 26), CREAM, 6)
        cv.restore()


def s_aube(cv, t, lt):
    banded_sky(cv, ['#6E5A86', '#8A7096', '#A888A2', '#C29EA8', '#D6B2AC', '#E4C4B0'], -600, 1300, t)
    rise = ease(clamp(lt / 3.0))
    striped_sun(cv, PX, 1500 - 380 * rise, 340, t, ['#E8C4A8', '#F0D2B4', '#F6E0C0', '#FAEBD0'])
    hill(cv, 1380, 45, 0.006, 1.0, '#8A7096', '#9478A0', t)
    hill(cv, 1540, 55, 0.005, 3.0, '#6A5A86', '#746490', t)
    bloom = ease(clamp((lt - 0.4) / 1.5))
    for x, h, ph, b in ((60, 300, 0, '#F0C8D0'), (190, 210, 1.3, '#C8E8E0'), (900, 260, 2.2, '#F8DCB8'), (1030, 190, 3.1, '#E0D0F0')):
        plant(cv, x, 1760, h, '#4E7A78', b, t, ph, kind=max(0.25, bloom))
    center_hero(cv, t, 'open', look=(0.0, -0.2))
    hill(cv, 1820, 25, 0.008, 5.0, '#4A4270', '#544C7A', t, n=3)


SCENES = [(0.0, s_hook), (3.35, s_iles), (9.3, s_lit), (13.9, s_coulisses), (17.65, s_moments), (20.3, s_calendrier),
          (22.8, s_chemins), (27.3, s_tardifs), (32.65, s_course), (36.9, s_balade), (42.3, s_ici), (47.2, s_aube)]
KINDS = ['iris', 'wave', 'iris', 'wave', 'iris', 'wave', 'iris', 'wave', 'iris', 'wave', 'iris']
TIN, TOUT = 0.35, 0.35


def draw_scene(cv, i, t):
    s0, fn = SCENES[i]; lt = t - s0
    z = 1.0 + 0.035 * ease(clamp(max(0, lt) / 6))
    cv.save(); cv.translate(PX, PY); cv.scale(z, z); cv.translate(-PX, -PY)
    fn(cv, t, max(0.0, lt)); cv.restore()


def mask_path(kind, p):
    if kind == 'iris':
        return skia.Path().addCircle(PX, PY, 2000 * ease(p) ** 1.3)
    y = H + 250 - (H + 700) * ease(p)
    m = skia.Path(); m.moveTo(-700, H + 700)
    for x in range(-700, W + 701, 20): m.lineTo(x, y + 60 * math.sin(x * 0.006 + p * 6))
    m.lineTo(W + 700, H + 700); m.close(); return m


def scene(cv, t):
    i = 0
    for k, (s0, _) in enumerate(SCENES):
        if t >= s0 - TIN: i = k
    s0 = SCENES[i][0]
    if i > 0 and t < s0 + TOUT:
        p = (t - (s0 - TIN)) / (TIN + TOUT)
        draw_scene(cv, i - 1, t)
        m = mask_path(KINDS[i - 1], p)
        cv.save(); cv.clipPath(m, doAntiAlias=True); draw_scene(cv, i, t); cv.restore()
        cv.drawPath(m, P(OUT, 255, stroke=16)); cv.drawPath(m, P(CREAM, 255, stroke=5))
    else:
        draw_scene(cv, i, t)


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
    out = os.path.join(HERE, 'pas_en_retard_4k.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(HERE, 'voice.wav'),
                           '-c:v', 'libx264', '-preset', 'slow', '-tune', 'animation', '-crf', '16', '-maxrate', '30M', '-bufsize', '60M',
                           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=2)):
            ff.stdin.write(b)
            if i % 150 == 0: print(i, '/', n, flush=True)
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'high',
                    '-level', '4.1', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
                    os.path.join(HERE, 'pas_en_retard_1080p.mp4')])
    print('ok')

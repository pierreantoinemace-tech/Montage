"""« Le monde va mal… et il va mieux » — vertical 4K, 30 fps, calé sur le son de référence (son non inclus)."""
import math, os, random, sys, json, subprocess, importlib.util
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('reves_video', os.path.join(HERE, '..', 'reves', 'video.py'))
RV = importlib.util.module_from_spec(_s); _s.loader.exec_module(RV)
import extrait2 as X
import extrait as D3
import numpy as np, skia
from lib import P, C, mix, lin, rad, circle, ease, ease_out
W, H, SC, OW_, OH_, PX, PY, HS, HERO = RV.W, RV.H, RV.SC, RV.OW_, RV.OH_, RV.PX, RV.PY, RV.HS, RV.HERO
FONT, TY, CREAM, GOLD, OUT = RV.FONT, RV.TY, RV.CREAM, RV.GOLD, RV.OUT
clamp, back, hero, kid, bp, twinkle, pop = RV.clamp, RV.back, RV.hero, RV.kid, RV.bp, RV.twinkle, RV.pop
banded_sky, hill, striped_sun, plant, island, figure, opath, rect, sym, BIG = RV.banded_sky, RV.hill, RV.striped_sun, RV.plant, RV.island, RV.figure, RV.opath, RV.rect, RV.sym, RV.BIG
FPS = 30; DUR = 60.5
DARK = '#3A3550'

# ---------------- mots ----------------
KEYS = {'MAL', 'GUERRES', 'CRISES', 'CATASTROPHES', 'PIRE', "L'HISTOIRE", 'EXPLOSE', 'DOUCEMENT', 'UNE', 'JAMAIS', 'MIEUX', 'VRAIS',
        'QUATRE', 'PAUVRETÉ', 'UN', 'DEUX', 'CINQ', 'LIRE', 'NEUF', 'MILLE', 'MISÈRE', 'FAIT', 'SOMBRE', 'LUMIÈRES', "S'ALLUMENT", 'PARLE'}


def load_words():
    raw = json.load(open(os.path.join(HERE, 'words.json')))
    toks = []
    for w, s, e in raw:
        if w and w[0] in "'-" and toks: toks[-1][0] += w; toks[-1][2] = e; continue
        if w.strip('?!.,…') == '': continue
        toks.append([w, s, e])
    out, i = [], 0
    seen_list = False
    while i < len(toks):
        w, s, e = toks[i]; txt = w.strip(',.?!…').upper()
        if txt == 'ÇA' and i + 2 < len(toks) and toks[i + 1][0].upper().startswith('VEUT'):     # « savait lire »
            out.append(['SAVAIT', s, toks[i + 1][1]]); out.append(['LIRE', toks[i + 1][1], toks[i + 2][2]]); i += 3; continue
        txt = {'VINGT-DE-CINQ': 'VINGT-CINQ'}.get(txt, txt)
        if not seen_list and txt in ('GUERRE', 'CRISE', 'CATASTROPHE'):
            txt += 'S'
            if txt == 'CATASTROPHES': seen_list = True
        out.append([txt, s, e]); i += 1
    res = []
    for j, (txt, s, e) in enumerate(out):
        nxt = out[j + 1][1] if j + 1 < len(out) else e + 1.0
        end = nxt if nxt - e < 0.7 else e + 0.35
        res.append((txt, s, end, txt in KEYS))
    return res


WORDS = load_words()
RV.WORDS = WORDS
X.WORDS = [(w, s, k) for w, s, e, k in WORDS]


# ---------------- objets ----------------
def burst(cv, x, y, s, t, col='#C8505A', a=255):
    n = 11; pts = []
    for k in range(2 * n):
        r = s * (1.0 if k % 2 == 0 else 0.5) * (1 + 0.08 * math.sin(t * 9 + k))
        g = k * math.pi / n
        pts.append((x + r * math.cos(g), y + r * math.sin(g)))
    opath(cv, poly(pts), col, 6, a)
    opath(cv, poly([(x + s * 0.45 * (1 if k % 2 == 0 else 0.55) * math.cos(k * math.pi / n), y + s * 0.45 * (1 if k % 2 == 0 else 0.55) * math.sin(k * math.pi / n)) for k in range(2 * n)]), '#F0A060', 4, a)


def poly(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); return p


def bolt(cv, x, y, s, a=255):
    opath(cv, poly([(x - 0.1 * s, y - s), (x + 0.4 * s, y - s), (x + 0.1 * s, y - 0.15 * s), (x + 0.45 * s, y - 0.15 * s), (x - 0.3 * s, y + s), (x - 0.05 * s, y + 0.1 * s), (x - 0.4 * s, y + 0.1 * s)]), '#E8D070', 5, a)


def meteor(cv, x, y, s, t, a=255):
    for k in range(3): cv.drawLine(x + (0.3 + k * 0.25) * s, y - (0.9 + k * 0.1) * s, x + (1.2 + k * 0.2) * s, y - (1.8 + k * 0.05) * s, P('#C8705A', a, stroke=8 - k * 2))
    opath(cv, skia.Path().addCircle(x, y, 0.45 * s), '#7A5A6A', 6, a)
    for cx_, cy_, r_ in ((-0.12, -0.1, 0.1), (0.15, 0.12, 0.07)): cv.drawCircle(x + cx_ * s, y + cy_ * s, r_ * s, P('#5A4050', a))


def dark_cloud(cv, x, y, s, t, col='#1E1A2A', a=255):
    p = skia.Path()
    for cx_, cy_, r_ in ((-0.5, 0.05, 0.45), (0, -0.2, 0.55), (0.55, 0.05, 0.42), (0.1, 0.25, 0.45)): p.addCircle(x + cx_ * s, y + cy_ * s, r_ * s)
    p = skia.Op(p, skia.Path(), skia.PathOp.kUnion_PathOp) or p
    opath(cv, p, col, 6, a)


def phone_card(cv, x, y, w, rot, t, seed, a=255):
    cv.save(); cv.translate(x, y); cv.rotate(rot + 4 * math.sin(t * 0.7 + seed))
    opath(cv, rect(-w / 2, -w * 0.65, w, w * 1.3, 16), '#2A2638', 6, a)
    opath(cv, rect(-w * 0.42, -w * 0.55, w * 0.84, w * 1.1, 8), '#4A4458', 4, a)
    cv.drawRect(skia.Rect.MakeXYWH(-w * 0.42, -w * 0.55, w * 0.84, w * 0.18), P('#C8505A', a))
    for k in range(4): cv.drawLine(-w * 0.32, -w * 0.15 + k * w * 0.16, w * (0.32 - 0.12 * (k % 2)), -w * 0.15 + k * w * 0.16, P('#6A6478', a, stroke=w * 0.06))
    cv.restore()


def newspaper(cv, x, y, w, rot, t, kind='bad', a=255, blank=0.0):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    h = w * 1.3
    opath(cv, rect(-w / 2, -h / 2, w, h, 6), '#EDE6D8', 6, a)
    cv.drawLine(-w * 0.42, -h * 0.36, w * 0.42, -h * 0.36, P(OUT, a, stroke=w * 0.07))
    cv.drawLine(-w * 0.42, -h * 0.27, w * 0.2, -h * 0.27, P('#8A8478', a, stroke=w * 0.035))
    if blank < 1:
        b = int(a * (1 - blank))
        cv.save(); cv.clipPath(rect(-w * 0.42, -h * 0.2, w * 0.84, h * 0.42, 4), doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h * 0.2, w, h * 0.45), P('#3A3448' if kind == 'bad' else '#F6E0C0', b))
        if kind == 'bad': burst(cv, 0, 0, w * 0.22, t, a=b)
        else: striped_sun(cv, 0, h * 0.06, w * 0.2, t, ['#FFD8A0', '#FFE8C0']) if b > 200 else None
        cv.restore()
    for k in range(4): cv.drawLine(-w * 0.42, h * 0.3 + k * h * 0.045, w * 0.42 - (k % 2) * w * 0.2, h * 0.3 + k * h * 0.045, P('#A8A090', a, stroke=w * 0.02))
    cv.restore()


def sprout(cv, x, y, s, g, t):
    h = s * (0.2 + 0.8 * g)
    st = skia.Path(); st.moveTo(x, y); st.quadTo(x - 0.1 * s, y - h * 0.5, x + 0.03 * s * math.sin(t), y - h)
    cv.drawPath(st, P(OUT, 255, stroke=14)); cv.drawPath(st, P('#5AA878', 255, stroke=7))
    for sx in (-1, 1):
        lf = skia.Path(); lx, ly = x + 0.03 * s * math.sin(t), y - h
        lf.moveTo(lx, ly); lf.quadTo(lx + sx * 0.3 * s * g, ly - 0.25 * s * g, lx + sx * 0.45 * s * g + sx * 2, ly - 0.05 * s * g); lf.quadTo(lx + sx * 0.2 * s * g, ly + 0.08 * s * g, lx, ly); lf.close()
        opath(cv, lf, '#7AC890', 4)


def globe(cv, x, y, r, t, lights=0.0, storm=1.0):
    opath(cv, skia.Path().addCircle(x, y, r), '#1E2A4A', 8)
    cv.save(); cv.clipPath(skia.Path().addCircle(x, y, r), doAntiAlias=True)
    rnd = random.Random(2)
    for k in range(7):                                         # continents abstraits
        cx_, cy_ = x + rnd.uniform(-0.8, 0.8) * r, y + rnd.uniform(-0.7, 0.7) * r
        opath(cv, D3.blobp(cx_ + 20 * math.sin(t * 0.2), cy_, rnd.uniform(0.15, 0.32) * r, k, t), '#2E4A5A', 5)
    for k in range(9): cv.drawCircle(x, y, r * (1 - k * 0.11), P('#24345A', 255, stroke=3))
    rnd = random.Random(5)
    for k in range(260):                                       # petites lumières
        px, py = x + rnd.uniform(-r, r), y + rnd.uniform(-r, r)
        if (px - x) ** 2 + (py - y) ** 2 > (r * 0.95) ** 2: continue
        if rnd.random() < lights:
            tw = 1 + 0.4 * bp(t) * (k % 3 == 0)
            circle(cv, px, py, rnd.uniform(3, 7) * tw, '#FFE680', 255)
    cv.restore()
    if storm > 0:
        for k, (dx, dy, s) in enumerate(((-0.55, -0.7, 0.55), (0.5, -0.8, 0.6), (0.0, -1.05, 0.5), (-0.85, 0.1, 0.4), (0.85, 0.0, 0.42))):
            dark_cloud(cv, x + dx * r * (1 + 0.6 * (1 - storm)), y + dy * r * (1 + 0.6 * (1 - storm)), s * r * storm, t, a=int(255 * storm))


# ---------------- scènes ----------------
def s_infos(cv, t, lt):
    thick = ease(clamp((t - 6.4) / 2.5))
    banded_sky(cv, [mix(c, '#05040A', 0.4 * thick) for c in ['#0A0A14', '#12101E', '#1A1428', '#221A32', '#2A1E3A', '#32223F']], -600, 1400, t)
    fl = 1 if ((t * 10) % 37 < 1.2 or abs(t - 4.06) < 0.06) else 0                     # éclairs dès la 1re image
    if t < 0.12 or fl: cv.drawRect(BIG, P('#E8E0F0', 60))
    for k, (x, y, s, ph) in enumerate(((150, 240, 170, 0), (520, 170, 210, 1), (900, 260, 180, 2), (330, 520, 140, 3), (800, 600, 150, 4))):
        dark_cloud(cv, x + 25 * math.sin(t * 0.3 + ph), y + 10 * math.sin(t * 0.5 + ph), s * (1 + 0.25 * thick), t, col='#1A1626')
    for (x, y, t0, fn) in ((210, 1080, 3.27, 'burst'), (880, 1050, 4.06, 'bolt'), (540, 620, 4.83, 'meteor')):
        sc = pop(t, t0, 0.35)
        if sc <= 0.01: continue
        if fn == 'burst': burst(cv, x, y, 110 * sc, t)
        elif fn == 'bolt': bolt(cv, x, y, 120 * sc)
        else: meteor(cv, x - 60 * (t - t0), y + 40 * (t - t0), 90 * sc, t)
    rnd = random.Random(3)
    for k in range(int(thick * 6)):                            # les écrans d'alerte s'accumulent
        phone_card(cv, rnd.uniform(80, 1000), rnd.uniform(820, 1350), 110, rnd.uniform(-20, 20), t, k)
    hill(cv, 1700, 30, 0.007, 1.0, '#141220', '#1C1A2A', t, n=3)
    hero(cv, t, PX, PY + 0.55 * HS, HS, 'lidded' if t > 9.8 else 'open', look=(0.0, 0.8), arms='phone')


def s_noir(cv, t, lt):
    cv.drawRect(BIG, P('#05030A')); sym(cv, 'eye', PX, PY, 40, 0, '#FFD86A', t if lt > 0.4 else 0)


def s_histoire(cv, t, lt):
    banded_sky(cv, ['#0C0A1C', '#141028', '#1C1634', '#241C40', '#2E224C', '#382858'], -600, 1500, t)
    twinkle(cv, 21, 70, (-50, -50, W + 50, 900), t)
    hill(cv, 1500, 40, 0.006, 0.5, '#22203A', '#2A2846', t)
    e = pop(t, 16.99, 0.3)
    if e > 0: burst(cv, 230, 1150, 150 * e * (1 + 0.05 * bp(t)), t)
    g = 0.3 + 0.7 * ease(clamp((t - 17.78) / 2.5))
    sprout(cv, 850, 1500, 420, g, t)
    sym(cv, 'star4', 850, 1500 - 420 * (0.2 + 0.8 * g) - 60, 16 * g, 0, GOLD, t)
    hero(cv, t, PX, 1590, 190, 'open', look=(-0.8, 0.0) if t < 17.7 else (0.8, 0.3))


def s_une(cv, t, lt):
    cv.drawRect(BIG, P('#14121E'))
    for k in range(12): cv.drawLine(-600, k * 180, W + 600, k * 180 - 120, P('#1A1826', 255, stroke=60))
    jam = clamp((t - 23.34) / 0.4)
    newspaper(cv, 330, 1120, 430, -6 + 2 * math.sin(t), t, 'bad', blank=0.0)
    if t > 21.6:                                               # 30 ans qui passent pour un arbre
        g = ease(clamp((t - 21.7) / 1.6))
        yr = int(1990 + 30 * g)
        f = skia.Font(FONT, 70); txt = str(yr); tw = f.measureText(txt)
        o = P(OUT, 255, stroke=12); cv.drawString(txt, 820 - tw / 2, 650, f, o); cv.drawString(txt, 820 - tw / 2, 650, f, P(CREAM))
        sprout(cv, 820, 1550, 520, g, t)
        newspaper(cv, 820, 1720, 300, 5, t, 'good', a=int(255 * jam), blank=1.0)
        if jam > 0:
            cv.drawLine(700, 1650, 940, 1790, P('#C8505A', int(255 * jam), stroke=14)); cv.drawLine(940, 1650, 700, 1790, P('#C8505A', int(255 * jam), stroke=14))


def s_planete(cv, t, lt):
    banded_sky(cv, ['#04030C', '#0A0820', '#100E2C', '#141838', '#182044', '#1C2850'], -600, 1900, t, wav=30)
    twinkle(cv, 22, 120, (-50, -50, W + 50, H + 50), t)
    lights = ease(clamp((t - 26.3) / 2.2)); storm = 1 - 0.55 * ease(clamp((t - 26.3) / 2.0))
    globe(cv, PX, 1250, 420 + 6 * bp(t), t, lights, storm)
    sym(cv, 'planet', 880, 330, 90, 0, '#6A5A8A', t)


def people_row(cv, t, n_lit, y=1430, total=10, light_t=None):
    for k in range(total):
        x = 95 + k * 99; lit = k < n_lit
        col = GOLD if lit else DARK
        figure(cv, x, y + (6 * math.sin(t * 2 + k) if lit else 0), 58, col)
        if lit: sym(cv, 'star4', x, y - 100, 10 * (1 + 0.5 * bp(t)), 0, CREAM, t)


def s_pauvrete(cv, t, lt):
    banded_sky(cv, ['#0E0C1E', '#161228', '#1E1834', '#2A1E40', '#38264A', '#463054'], -600, 1300, t)
    twinkle(cv, 23, 60, (-50, -50, W + 50, 700), t)
    dawn = ease(clamp((t - 33.24) / 1.2))
    striped_sun(cv, PX, 1250, 260 * dawn + 1, t, ['#E8C4A8', '#F0D2B4', '#F6E0C0']) if dawn > 0.02 else None
    hill(cv, 1300, 35, 0.006, 0.8, '#2A2440', '#322C4C', t)
    opath(cv, rect(-100, 1440, W + 200, 600), '#1E1A2C', 6)
    poor = 4 if t < 33.24 else (1 if t > 33.9 else 4 - int(3 * (t - 33.24) / 0.66))
    for k in range(10):
        x = 150 + (k % 5) * 195; y = 1330 + (k // 5) * 290
        inpov = (k < poor)
        figure(cv, x, y + (0 if inpov else 6 * math.sin(t * 2 + k)), 105, DARK if inpov else '#C8B8D8')
        if inpov: dark_cloud(cv, x, y - 190, 75, t, col='#2A2438')
        elif t > 33.24: sym(cv, 'star4', x, y - 170, 14 * (1 + 0.5 * bp(t)), 0, GOLD, t)


def s_enfants(cv, t, lt):
    banded_sky(cv, ['#2A2040', '#382A50', '#48345E', '#5A406A', '#6C4C74', '#7E5A7E'], -600, 1300, t)
    shrink = 1 - 0.6 * ease(clamp((t - 38.4) / 0.9))
    striped_sun(cv, 820, 420, 140, t, ['#E8C4A8', '#F0D2B4', '#F6E0C0'])
    dark_cloud(cv, 330, 420, 260 * shrink, t, col='#2A2438')
    hill(cv, 1350, 45, 0.006, 1.0, '#4A3E66', '#544872', t)
    for x, cy_, s, ph in ((260, 1480, 120, 0), (540, 1520, 135, 1), (820, 1470, 115, 2)):
        kid(cv, t + ph, x, cy_, s, 'open', look=(0.3 * math.sin(ph), -0.6), arms='wave' if ph != 1 else None)
    hill(cv, 1800, 25, 0.008, 4.0, '#2E2848', '#363052', t, n=3)


def s_lire(cv, t, lt):
    banded_sky(cv, ['#0E0C20', '#16122C', '#1E1838', '#261E44', '#30244E', '#3A2A58'], -600, 1500, t)
    twinkle(cv, 24, 60, (-50, -50, W + 50, 800), t)
    n = 2 if t < 43.2 else min(9, 2 + int((t - 43.2) * 14))
    for k in range(10):
        x = 150 + (k % 5) * 195; y = 1120 + (k // 5) * 330
        if k < n:
            RV.book(cv, x, y, 88, t + k)
        else:
            opath(cv, rect(x - 80, y, 160, 120, 8), DARK, 5); cv.drawLine(x - 68, y + 26, x + 68, y + 26, P('#4A4460', 255, stroke=6))


def s_journaux(cv, t, lt):
    banded_sky(cv, ['#2A2240', '#362A4E', '#44325C', '#523A66', '#604470', '#6E4E78'], -600, 1500, t)
    gone = ease(clamp((t - 51.92) / 0.6))
    idx = 0
    for b in RV.BEATS:
        if 46.0 <= b <= t: idx += 1
    rnd = random.Random(9)
    for k in range(min(1 + idx // 2, 9)):                          # un journal heureux à chaque mesure, qui ne sort jamais
        x = 220 + rnd.uniform(0, 640); y = 1000 + rnd.uniform(0, 560); rot = rnd.uniform(-15, 15)
        newspaper(cv, x + gone * (x - PX) * 2, y - gone * 900, 300, rot, t, 'good', a=int(255 * (1 - gone)))
    if gone > 0:
        f = skia.Font(FONT, 60)
        for k in range(5):
            u = ((t - 51.92) * 0.8 + k * 0.2) % 1
            sym(cv, 'star4', PX + 300 * math.sin(k * 1.7), 1500 - u * 800, 12, 0, CREAM, t, 255 * (1 - u))


def s_lumieres(cv, t, lt):
    banded_sky(cv, ['#0A0818', '#120E26', '#1A1434', '#221A40', '#2C204C', '#362656'], -600, 1300, t)
    twinkle(cv, 25, 90, (-50, -50, W + 50, 900), t)
    on = ease(clamp((t - 57.38) / 1.6))
    hill(cv, 1150, 40, 0.006, 0.3, '#1C1A30', '#24223C', t)
    hill(cv, 1300, 50, 0.005, 2.0, '#16142A', '#1E1C34', t)
    rnd = random.Random(31)
    for k in range(320):                                       # des millions de petites lumières
        x = rnd.uniform(-60, W + 60); y = rnd.uniform(1180, 1900)
        if rnd.random() < on * (0.4 + 0.6 * (y - 1180) / 720):
            circle(cv, x, y, rnd.uniform(3, 7) * (1 + 0.3 * bp(t) * (k % 4 == 0)), '#FFE680')
    hero(cv, t, PX, 1600, 200, 'open', look=(0.0, 0.6) if t < 57.3 else (0.0, -0.2))


SCENES = [(0.0, s_infos, None), (12.7, s_noir, 'cut'), (13.62, s_histoire, 'flash'), (19.45, s_une, 'iris'), (25.2, s_planete, 'flash'),
          (29.0, s_pauvrete, 'wave'), (36.2, s_enfants, 'iris'), (39.95, s_lire, 'wave'), (45.55, s_journaux, 'iris'), (53.2, s_lumieres, 'iris')]
RV.SCENES = SCENES


def frame(fi):
    t = fi / FPS
    surf = skia.Surface(OW_, OH_); cv = surf.getCanvas(); cv.scale(SC, SC)
    cv.save(); cv.translate(PX, PY); cv.rotate(0.3 * math.sin(t * 0.35)); cv.scale(1.03, 1.03)
    cv.translate(-PX + 8 * math.sin(t * 0.4), -PY + 8 * math.cos(t * 0.33))
    RV.scene(cv, t); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1250, [C('#000000', 0), C('#000000', 0), C('#000000', 70)], [0, 0.7, 1])))
    RV.draw_word(cv, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        from PIL import Image
        for ts in sys.argv[2].split(','):
            arr = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH_, OW_, 4)
            Image.fromarray(arr[..., :3]).resize((540, 960), Image.LANCZOS).save(os.path.join(sys.argv[3], f'pv_{ts}.png'))
        sys.exit()
    out = os.path.join(HERE, 'monde_4k.mp4'); hd = os.path.join(HERE, 'monde_1080p.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(HERE, 'voice.wav'),
                           '-filter_complex', '[0:v]format=yuv420p,split=2[v4][vh];[vh]scale=1080:1920:flags=lanczos[v1]',
                           '-map', '[v4]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '5.1', '-preset', 'slow', '-crf', '15',
                           '-maxrate', '25M', '-bufsize', '50M', '-c:a', 'aac', '-b:a', '256k', '-t', str(DUR), '-movflags', '+faststart', out,
                           '-map', '[v1]', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '4.2', '-preset', 'slow', '-crf', '14',
                           '-maxrate', '20M', '-bufsize', '40M', '-c:a', 'aac', '-b:a', '256k', '-t', str(DUR), '-movflags', '+faststart', hd],
                          stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(n), chunksize=2)):
            ff.stdin.write(b)
            if i % 300 == 0: print(i, '/', n, flush=True)
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', hd, '-i', os.path.join(HERE, '..', 'son', 'son_reference.wav'),
                    '-filter_complex', '[1:a]volume=0.35,aresample=44100,aformat=channel_layouts=stereo[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]',
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', os.path.join(HERE, 'CONTROLE_calage_avec_son.mp4')])
    print('ok')

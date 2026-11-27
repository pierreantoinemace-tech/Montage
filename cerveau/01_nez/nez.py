"""« Ton nez » (Ton cerveau te ment #1) — vertical 4K, 30 fps. DA d'avant (Midnight Gospel sombre, perso aux trois yeux, haut étroit),
mais : hook écrit dès l'image 0, image nouvelle toutes les 1-2 s, texte en petits blocs qui apparaissent au rythme de la voix."""
import math, os, random, sys, json, subprocess
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, '..', 'work')
sys.path.insert(0, os.path.join(HERE, '..', '..', 'retard'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'vertical'))
import video as R
from video import (W, H, SC, OW_, OH_, PX, PY, HERO, OTHER, FONT, clamp, back, hero, banded_sky, hill, striped_sun, plant,
                   island, figure, dots, BIG, opath, rect, pop, CREAM, GOLD, sym, OUT)
import extrait2 as X
import haut_etroit
haut_etroit.appliquer(R.pd)
import numpy as np, skia
from lib import P, C, mix, lin, rad, circle, ease, ease_out

FPS = 30
DUR = 34.6
TY = H * 0.40

# ---------------- texte : petits blocs, mots qui apparaissent quand ils sont dits ----------------
KEYS = {'TRUC', 'YEUX', 'NEZ', 'MILIEU', 'VIE', 'JAMAIS', 'ŒIL', 'LÀ', 'TOUJOURS', 'CERVEAU', 'RÈGLE', 'CHANGE', 'ATTENTION',
        "L'EFFACE", 'TOUT', 'FRIGO', 'VÊTEMENTS', "L'ODEUR", 'PLUS', 'AIMES', 'VOIR'}


def load_words():
    raw = json.load(open(os.path.join(WORK, 'words.json')))
    toks = []
    for w, s, e in raw:
        if w and w[0] in "'-" and toks: toks[-1][0] += w; toks[-1][2] = e; continue
        if w.strip('?!.,…') == '':
            if toks: toks[-1][0] += w
            continue
        toks.append([w, s, e])
    # « il les fasse » -> « il l'efface »
    for i in range(len(toks) - 1):
        if toks[i][0].lower() == 'les' and toks[i + 1][0].lower().startswith('fasse'):
            toks[i] = ["l'efface.", toks[i][1], toks[i + 1][2]]; toks.pop(i + 1); break
    out = []
    for w, s, e in toks:
        txt = w.upper().replace('’', "'").strip()
        brk = txt[-1] in ',.?!…'
        clean = txt.strip(',.?!…')
        out.append([clean, s, e, clean in KEYS, brk])
    return out


WORDS = load_words()
X.WORDS = [(w, s, k) for w, s, e, k, b in WORDS]          # pulsation du troisième œil


def make_chunks():
    ch, cur = [], []
    for i, wd in enumerate(WORDS):
        cur.append(wd)
        nxt = WORDS[i + 1][1] if i + 1 < len(WORDS) else 99
        f = skia.Font(FONT, 150)
        wid = sum(f.measureText(x[0]) for x in cur) + f.measureText(' ') * len(cur)
        nw = f.measureText(WORDS[i + 1][0]) if i + 1 < len(WORDS) else 0
        if wd[4] or len(cur) >= 3 or nxt - wd[2] > 0.35 or wid + nw > 900:
            ch.append(cur); cur = []
    if cur: ch.append(cur)
    out = []
    for j, c in enumerate(ch):
        s = c[0][1]; nxt = ch[j + 1][0][1] if j + 1 < len(ch) else DUR
        e = min(nxt, c[-1][2] + 0.6)
        out.append((s, e, c))
    return out


CHUNKS = make_chunks()


def draw_text(cv, t):
    for s, e, c in CHUNKS:
        if s <= t < e: break
    else: return
    size = 150
    f = skia.Font(FONT, size)
    sp = f.measureText(' ')
    ws = [f.measureText(w[0]) for w in c]
    tot = sum(ws) + sp * (len(c) - 1)
    if tot > 940: f.setSize(size * 940 / tot); sp *= 940 / tot; ws = [x * 940 / tot for x in ws]; tot = 940
    fs = f.getSize(); x = W / 2 - tot / 2; y = TY + fs * 0.35
    for (w, ws_, we, k, _), wd in zip(c, ws):
        if t >= ws_ - 0.02:
            age = t - ws_
            sc = 0.8 + 0.2 * back(clamp(age / 0.18)) if age < 0.18 else 1.0
            cx = x + wd / 2
            cv.save(); cv.translate(cx, y - fs * 0.35); cv.scale(sc, sc); cv.translate(-cx, -(y - fs * 0.35))
            o = P(OUT, 255, stroke=fs * 0.16); o.setStrokeJoin(skia.Paint.kRound_Join)
            cv.drawString(w, x + fs * 0.03, y + fs * 0.07, f, o); cv.drawString(w, x + fs * 0.03, y + fs * 0.07, f, P(OUT))
            cv.drawString(w, x, y, f, o); cv.drawString(w, x, y, f, P(GOLD if k else CREAM))
            cv.restore()
        x += wd + sp


def hook_title(cv, t):
    a = 1.0 if t < 3.9 else 1 - (t - 3.9) / 0.4
    for i, (txt, col, size) in enumerate((('IL EST DEVANT TES YEUX…', CREAM, 84), ('ET TU NE LE VOIS PAS', GOLD, 100))):
        f = skia.Font(FONT, size); tw = f.measureText(txt)
        if tw > 960: f.setSize(size * 960 / tw); size = f.getSize(); tw = f.measureText(txt)
        y = 250 + i * 115 + 6 * math.sin(t * 3)
        cv.save(); cv.translate(W / 2, y); s_ = 1 + 0.03 * math.sin(t * 4 + i); cv.scale(s_, s_)
        o = P(OUT, int(255 * a), stroke=size * 0.18); o.setStrokeJoin(skia.Paint.kRound_Join)
        cv.drawString(txt, -tw / 2 + 3, size * 0.35 + 6, f, o); cv.drawString(txt, -tw / 2, size * 0.35, f, o)
        cv.drawString(txt, -tw / 2, size * 0.35, f, P(col, int(255 * a))); cv.restore()


# ---------------- outils ----------------
SKIN = HERO['skin']


def nose_glow(cv, cx, cy, s, a=1.0, t=0.0):
    """Le nez du perso, surligné en or (il « apparaît »)."""
    p = skia.Path(); p.moveTo(cx - 0.01 * s, cy + 0.1 * s); p.quadTo(cx - 0.1 * s, cy + 0.42 * s, cx + 0.05 * s, cy + 0.44 * s)
    for j in range(3):
        cv.drawCircle(cx - 0.02 * s, cy + 0.32 * s, s * (0.22 + 0.1 * j) * (1 + 0.08 * math.sin(t * 6)), P(GOLD, int(a * (90 - j * 25)), stroke=4))
    cv.drawPath(p, P(GOLD, int(255 * a), stroke=0.05 * s)); cv.drawPath(p, P(OUT, int(255 * a), stroke=0.018 * s))


def pov_world(cv, t, lt, sun_speed=0.0, x0=0):
    """Ce que tu vois : un paysage onirique sombre."""
    day = (lt * sun_speed) % 1.0 if sun_speed else 0.25
    dark = 0.5 - 0.5 * math.cos(day * 2 * math.pi) if sun_speed else 0.0
    sky = [mix(c, '#05040C', dark * 0.7) for c in ['#1A1030', '#261640', '#341C4E', '#44245A', '#562C62', '#6A3668']]
    banded_sky(cv, sky, -600, 1350, t)
    dots(cv, 21, 120, (-100, -100, W + 100, 1100), '#C8B8E0')
    if sun_speed:
        ang = day * 2 * math.pi
        sx, sy = PX + 520 * math.cos(ang - math.pi / 2 + math.pi), 1250 - 900 * math.sin(ang)
        striped_sun(cv, sx, sy, 120, t, ['#8A4A70', '#9C5678', '#B06682'])
        mx, my = PX - 520 * math.cos(ang - math.pi / 2 + math.pi), 1250 + 900 * math.sin(ang)
        cv.drawCircle(mx, my, 80, P('#D8D0E8')); cv.drawCircle(mx, my, 80, P(OUT, 255, stroke=5))
    else:
        striped_sun(cv, 780, 520, 150, t, ['#6A3460', '#7C4068', '#8E4C72', '#A05A7C'])
    hill(cv, 1300, 40, 0.006, 0.4, '#2C1E46', '#352652', t)
    hill(cv, 1520, 55, 0.005, 2.2, '#1E2440', '#26304C', t, n=6)
    for x, h, ph, b in ((110, 240, 0.3, '#C8A8D8'), (300, 170, 1.6, '#8FC8C0'), (820, 200, 2.4, '#E0B890'), (990, 260, 3.3, '#D89AAE')):
        plant(cv, x + x0, 1700, h, '#2E5A5A', b, t, ph)


def pov_nose(cv, t, single=0.0):
    """Ton nez, vu de l'intérieur : flou et transparent avec les deux yeux, net avec un seul."""
    def shape(x, yb):
        p = skia.Path(); p.moveTo(x - 260, H + 200); p.cubicTo(x - 200, yb + 260, x - 120, yb, x - 30, yb)
        p.cubicTo(x + 60, yb, x + 150, yb + 300, x + 230, H + 200); p.close(); return p
    br = 4 * math.sin(t * 1.3)
    if single < 1:
        a = int(70 * (1 - single))
        for dx in (-120, 120):
            p = shape(PX + dx, 1330 + br)
            cv.drawPath(p, P(SKIN, a)); cv.drawPath(p, P(mix(SKIN, '#FFFFFF', 0.4), a, stroke=26))
    if single > 0:
        p = shape(PX + 140 - 140 * (1 - single), 1300 + br + 80 * (1 - single))
        cv.drawPath(p, P(SKIN, int(255 * single))); cv.save(); cv.clipPath(p, doAntiAlias=True)
        cv.drawOval(skia.Rect.MakeLTRB(PX + 120, 1350, PX + 420, 2200), P(mix(SKIN, '#000000', 0.3), int(140 * single)))
        cv.drawOval(skia.Rect.MakeLTRB(PX - 40, 1400, PX + 60, 1600), P('#FFFFFF', int(80 * single)))
        cv.restore(); cv.drawPath(p, P(OUT, int(255 * single), stroke=8))


def eyelid(cv, u):
    """Paupière qui se ferme (u=1 fermé)."""
    if u <= 0: return
    y = -200 + (H / 2 + 260) * u
    p = skia.Path(); p.moveTo(-200, -400); p.lineTo(W + 200, -400); p.lineTo(W + 200, y - 120); p.quadTo(PX, y + 140, -200, y - 120); p.close()
    q = skia.Path(); q.moveTo(-200, H + 400); q.lineTo(W + 200, H + 400); q.lineTo(W + 200, H - y + 120); q.quadTo(PX, H - y - 140, -200, H - y + 120); q.close()
    for pp in (p, q): cv.drawPath(pp, P('#0A0614')); cv.drawPath(pp, P(OUT, 255, stroke=10))
    for k in range(12):                                                   # cils
        x = 80 + k * 84; yy = y - 120 + 260 * (1 - ((x - PX) / 640) ** 2) * 0.5
        cv.drawLine(x, yy, x + 10 * (k - 6), yy + 60, P('#0A0614', 255, stroke=10))


def qmark(cv, x, y, s, rot, col, a=255):
    f = skia.Font(FONT, s); w = f.measureText('?')
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    o = P(OUT, a, stroke=s * 0.14); o.setStrokeJoin(skia.Paint.kRound_Join)
    cv.drawString('?', -w / 2, s * 0.35, f, o); cv.drawString('?', -w / 2, s * 0.35, f, P(col, a)); cv.restore()


def brain(cv, x, y, s, t, col='#E89AB8'):
    p = skia.Path()
    for dx, dy, r in ((-0.55, 0.05, 0.5), (-0.2, -0.3, 0.55), (0.25, -0.3, 0.55), (0.6, 0.05, 0.48), (0.0, 0.15, 0.6), (-0.3, 0.3, 0.42), (0.35, 0.3, 0.42)):
        p.addCircle(x + dx * s, y + dy * s + 4 * math.sin(t * 2 + dx * 3), r * s)
    u = skia.Path(); u.addCircle(x, y, 1)
    for i in range(1):
        pass
    p.setFillType(skia.PathFillType.kWinding)
    cv.drawPath(p, P(OUT, 255, stroke=14)); cv.drawPath(p, P(col))
    cv.save(); cv.clipPath(p, doAntiAlias=True)
    for k in range(6):
        q = skia.Path(); yy = y - 0.6 * s + k * 0.24 * s; q.moveTo(x - 1.2 * s, yy)
        for j in range(60):
            xx = x - 1.2 * s + j * 0.04 * s
            q.lineTo(xx, yy + 0.07 * s * math.sin(j * 0.9 + k * 1.7) + 0.04 * s * math.sin(j * 0.37 + k))
        cv.drawPath(q, P(mix(col, '#5A1E3E', 0.45), 255, stroke=0.045 * s))
    cv.restore()
    cv.drawLine(x, y - 0.75 * s, x, y + 0.55 * s, P(mix(col, '#5A1E3E', 0.6), 255, stroke=0.04 * s))


def fade_ring(cv, x, y, r, t, col, n=3, a=1.0, speed=0.8):
    for k in range(n):
        u = (t * speed + k / n) % 1
        cv.drawCircle(x, y, r * (0.4 + u), P(col, int(220 * (1 - u) * a), stroke=6))


def gray(col, g):
    return mix(col, '#4A4658', g)


# ---------------- scènes ----------------
def s_hook(cv, t, lt):
    """Gros plan sur le perso, une cible se resserre sur son nez : on ne sait pas encore ce que c'est."""
    banded_sky(cv, ['#0A0716', '#120C24', '#1A1032', '#22143E', '#2C184A', '#361C54'], -600, 2000, t)
    dots(cv, 31, 150, (-100, -100, W + 100, H), '#B8A8D0')
    z = 1.0 + 0.25 * ease(clamp(lt / 4.3))
    s = 330; cx, cy = PX, 1250
    cv.save(); cv.translate(cx, cy + 0.3 * s); cv.scale(z, z); cv.translate(-cx, -(cy + 0.3 * s))
    hero(cv, t, cx, cy, s, 'open', look=(0.0, 1.0))
    cv.restore()
    nx, ny = cx, cy + 0.3 * s
    r = 360 - 200 * ease(clamp(lt / 3.6))                       # viseur qui se resserre
    a = 1.0
    pa = P(GOLD, int(255 * a), stroke=7); pa.setPathEffect(skia.DashPathEffect.Make([40, 26], t * 80))
    cv.drawCircle(nx, ny, r, P(OUT, int(255 * a), stroke=16)); cv.drawCircle(nx, ny, r, pa)
    for k in range(4):
        g = k * math.pi / 2 + 0.4 * lt
        cv.drawLine(nx + math.cos(g) * (r + 20), ny + math.sin(g) * (r + 20), nx + math.cos(g) * (r + 90), ny + math.sin(g) * (r + 90), P(GOLD, int(255 * a), stroke=9))
    if lt > 1.8:                                                # « là, maintenant » : flèches qui pointent
        for k, (dx, dy) in enumerate(((-1, -0.4), (1, -0.4))):
            u = pop(lt, 1.8 + k * 0.15, 0.35); b = 22 * math.sin(t * 8)
            if u <= 0: continue
            x0 = nx + dx * (r + 220 + b); y0 = ny + dy * (r + 220 + b)
            cv.save(); cv.translate(x0, y0); cv.rotate(math.degrees(math.atan2(-dy, -dx))); cv.scale(u, u)
            ar = skia.Path(); ar.moveTo(-90, -22); ar.lineTo(20, -22); ar.lineTo(20, -55); ar.lineTo(90, 0); ar.lineTo(20, 55); ar.lineTo(20, 22); ar.lineTo(-90, 22); ar.close()
            opath(cv, ar, GOLD, 7); cv.restore()


def s_yeux(cv, t, lt):
    """« là, maintenant » : très gros plan sur les yeux qui cherchent partout (saccades)."""
    cv.drawRect(BIG, P('#0E0A1E'))
    k = int(lt * 5) % 4; look = [(-0.9, -0.2), (0.9, -0.3), (-0.6, 0.6), (0.8, 0.5)][k]
    hero(cv, t, PX, 1050, 760, 'open', look=look)
    for j in range(5):
        g = j * 1.26 + t * 0.7; r = 470 + 30 * math.sin(t * 3 + j)
        qmark(cv, PX + math.cos(g) * r, 1000 + math.sin(g) * r * 1.4, 90, 15 * math.sin(t * 2 + j), GOLD, 200)


def loupe(cv, x, y, r, t):
    cv.drawCircle(x, y, r, P('#BFE6FF', 50))
    cv.save(); cv.translate(x, y); cv.rotate(40)
    opath(cv, rect(r * 0.95, -r * 0.14, r * 1.1, r * 0.28, r * 0.1), '#8A4A6A', 8); cv.restore()
    cv.drawCircle(x, y, r, P(OUT, 255, stroke=22)); cv.drawCircle(x, y, r, P('#C8A880', 255, stroke=12))
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7), 200, 50); cv.drawPath(p, P('#FFFFFF', 200, stroke=10))


def s_cherche(cv, t, lt):
    """« que tu ne vois pas » : le perso fouille le décor à la loupe, sans trouver."""
    banded_sky(cv, ['#0A0716', '#120C24', '#1A1032', '#22143E', '#2C184A', '#361C54'], -600, 1300, t)
    dots(cv, 81, 120, (-100, -100, W + 100, 1200), '#B8A8D0')
    striped_sun(cv, 200, 420, 110, t, ['#4A2350', '#5A2C5C', '#6C3666'])
    hill(cv, 1300, 40, 0.006, 0.3, '#2A1A40', '#33214C', t)
    hill(cv, 1560, 50, 0.005, 2.0, '#1A2438', '#223048', t)
    for x, h, ph, b in ((90, 260, 0, '#C8A8D8'), (260, 180, 1.2, '#8FC8C0'), (840, 210, 2.2, '#E0B890'), (1000, 250, 3.0, '#D89AAE')):
        plant(cv, x, 1760, h, '#2E5A5A', b, t, ph)
    lx = PX + 330 * math.sin(lt * 2.6); ly = 1150 + 180 * math.sin(lt * 1.9)
    hero(cv, t, PX, 1480, 190, 'open', look=((lx - PX) / 330, (ly - 1480) / 400))
    loupe(cv, lx, ly, 120, t)


def s_journee(cv, t, lt):
    """« toute la journée » : le soleil et la lune font le tour du ciel en accéléré ; le nez, lui, ne bouge pas."""
    pov_world(cv, t, lt * 0.9, sun_speed=1.0)
    pov_nose(cv, t)
    vf = skia.Path(); vf.addOval(skia.Rect.MakeLTRB(-260, 120, W + 260, H - 120))
    full = skia.Path(); full.addRect(skia.Rect.MakeLTRB(-600, -600, W + 600, H + 600))
    cv.drawPath(skia.Op(full, vf, skia.PathOp.kDifference_PathOp), P('#06040C', 235)); cv.drawPath(vf, P(OUT, 255, stroke=10))


def s_vie(cv, t, lt):
    """« toute ta vie » : tempête de pages de calendrier autour du perso."""
    R.s_calendrier(cv, t * 3, lt)


def s_perplexe(cv, t, lt):
    """« tu ne le vois jamais ? » : gros plan, regard qui louche vers le bas, un énorme point d'interrogation."""
    cv.drawRect(BIG, P('#140C24'))
    for k in range(12):
        g = k * math.pi / 6 + lt * 0.5
        p = skia.Path(); p.moveTo(PX, 1100); p.lineTo(PX + math.cos(g) * 2000, 1100 + math.sin(g) * 2000); p.lineTo(PX + math.cos(g + 0.15) * 2000, 1100 + math.sin(g + 0.15) * 2000); p.close()
        cv.drawPath(p, P('#3A1E50', 255))
    hero(cv, t, PX, 1250, 480, 'lidded', look=(0.0, 1.0))
    u = pop(lt, 0.05, 0.4)
    if u > 0: qmark(cv, 880, 1550, 300 * u, 12 + 6 * math.sin(t * 3), GOLD)


def s_reveal(cv, t, lt):
    """« ton nez ! » : flash, zoom fort sur le nez qui s'illumine."""
    banded_sky(cv, ['#2A1036', '#3A1640', '#4A1C4A', '#5A2452', '#6A2C5A', '#7A3462'], -600, 2000, t)
    for k in range(16):                                         # rayons
        g = k * math.pi / 8 + lt * 0.4
        p = skia.Path(); p.moveTo(PX, 1150); p.lineTo(PX + math.cos(g) * 2000, 1150 + math.sin(g) * 2000); p.lineTo(PX + math.cos(g + 0.12) * 2000, 1150 + math.sin(g + 0.12) * 2000); p.close()
        cv.drawPath(p, P('#FFE680', 22))
    s = 520 + 60 * ease_out(clamp(lt / 0.8)); cx, cy = PX, 1150 - 0.3 * s
    hero(cv, t, cx, cy, s, 'open', look=(0.0, 1.0))
    nose_glow(cv, cx, cy, s, ease_out(clamp(lt / 0.25)), t)


def s_pov(cv, t, lt):
    """Ce que tu vois toute la journée, toute ta vie : le nez flou au milieu, le soleil qui tourne de plus en plus vite."""
    sp = 0.0 if lt < 2.0 else 0.35 * (lt - 2.0) ** 1.6
    acc = 0.0 if lt < 2.0 else 0.35 * (lt - 2.0) ** 2.6 / 2.6
    pov_world(cv, t, acc if lt >= 2 else 0, sun_speed=1.0 if lt >= 2.0 else 0.0)
    pov_nose(cv, t)
    # cadre « champ de vision »
    a = clamp(lt / 0.4)
    vf = skia.Path(); vf.addOval(skia.Rect.MakeLTRB(-260, 120, W + 260, H - 120))
    full = skia.Path(); full.addRect(skia.Rect.MakeLTRB(-600, -600, W + 600, H + 600))
    m = skia.Op(full, vf, skia.PathOp.kDifference_PathOp)
    cv.drawPath(m, P('#06040C', int(235 * a))); cv.drawPath(vf, P(OUT, int(255 * a), stroke=10))
    if lt > 3.0:                                                # « toute ta vie » : calendrier qui s'effeuille
        k = int((lt - 3.0) * 10)
        f = skia.Font(FONT, 70); txt = str(2026 - 40 + k * 2)
        x, y = 860, 300
        opath(cv, rect(x - 120, y - 80, 240, 160, 16), '#EFE6D8', 6)
        tw = f.measureText(txt); cv.drawString(txt, x - tw / 2, y + 25, f, P('#2A1E3A'))


def s_pourquoi(cv, t, lt):
    """« Alors pourquoi tu ne le vois jamais ? » : le perso perplexe, les points d'interrogation tombent."""
    banded_sky(cv, ['#0E0A1E', '#160E2C', '#1E1238', '#281644', '#331A4E', '#3E1E56'], -600, 1600, t)
    dots(cv, 41, 120, (-100, -100, W + 100, 1600), '#B8A8D0')
    rnd = random.Random(5)
    for k in range(9):
        u = pop(lt, k * 0.12, 0.4)
        if u <= 0: continue
        x = rnd.uniform(90, 990); y = rnd.uniform(950, 1700) - 30 * lt
        qmark(cv, x, y, rnd.uniform(90, 190) * u, rnd.uniform(-25, 25) + 10 * math.sin(t * 2 + k), rnd.choice([GOLD, CREAM, '#D89AAE', '#8FC8C0']))
    hill(cv, 1640, 40, 0.006, 1.0, '#1A1830', '#22203C', t, n=3)
    hero(cv, t, PX, 1290, 230, 'lidded', look=(-0.7, -0.6), arms='think')


def s_ferme(cv, t, lt):
    """« Ferme un œil. Voilà, il est là. » : la paupière se ferme, se rouvre, et le nez apparaît, net."""
    pov_world(cv, t, 0, x0=40 * ease(clamp((lt - 0.4) / 0.4)))
    single = ease(clamp((lt - 0.45) / 0.35))
    pov_nose(cv, t, single)
    if lt > 1.0:                                                # « voilà » : il s'allume
        u = clamp((lt - 1.0) / 0.4)
        for j in range(3):
            r = 200 + j * 90 + 30 * math.sin(t * 5 - j)
            cv.drawCircle(PX + 120, 1560, r, P(GOLD, int((200 - j * 60) * u), stroke=6))
    if lt > 2.35:                                               # « il a toujours été là » : étiquette
        u = pop(lt, 2.35, 0.4)
        cv.save(); cv.translate(PX + 150, 1230); cv.scale(u, u)
        opath(cv, rect(-170, -55, 340, 110, 26), GOLD, 7)
        f = skia.Font(FONT, 64); tw = f.measureText('TON NEZ'); cv.drawString('TON NEZ', -tw / 2, 22, f, P('#2A1E3A'))
        cv.drawLine(0, 55, -20, 150, P(OUT, 255, stroke=8)); cv.restore()
    vf = skia.Path(); vf.addOval(skia.Rect.MakeLTRB(-260, 120, W + 260, H - 120))
    full = skia.Path(); full.addRect(skia.Rect.MakeLTRB(-600, -600, W + 600, H + 600))
    cv.drawPath(skia.Op(full, vf, skia.PathOp.kDifference_PathOp), P('#06040C', 235)); cv.drawPath(vf, P(OUT, 255, stroke=10))
    eyelid(cv, ease(clamp(lt / 0.3)) if lt < 0.45 else 1 - ease(clamp((lt - 0.45) / 0.3)))


def control_room(cv, t, lt, nose_a=1.0, erase=None, moving=True):
    cv.drawRect(BIG, P('#0E0818'))
    for k in range(7):                                          # câbles
        p = skia.Path(); x = 80 + k * 155; p.moveTo(x, -100); p.cubicTo(x + 60, 400, x - 80, 900, PX + (k - 3) * 40, 1080)
        cv.drawPath(p, P(OUT, 255, stroke=16)); cv.drawPath(p, P(['#5A2A6A', '#2E5A6A', '#6A4A2A'][k % 3], 255, stroke=8))
        u = (t * 0.6 + k * 0.13) % 1; pt = skia.PathMeasure(p, False).getPosTan(u * skia.PathMeasure(p, False).getLength())[0]
        circle(cv, pt.x(), pt.y(), 9, GOLD)
    brain(cv, PX, 400, 330, t)
    # écran : ce que voient les yeux
    x0, y0, w, h = 140, 1080, 800, 620
    opath(cv, rect(x0 - 24, y0 - 24, w + 48, h + 48, 34), '#2A2240', 8)
    cv.save(); cv.clipPath(rect(x0, y0, w, h, 18), doAntiAlias=True); cv.translate(x0, y0); cv.scale(w / W, h / H * 1.15); cv.translate(0, -250)
    pov_world(cv, t, 0)
    if moving:                                                   # ce qui bouge : entouré en vert
        for k in range(3):
            bx = (t * 260 + k * 420) % 1400 - 160; by = 600 + 160 * k + 40 * math.sin(t * 3 + k)
            sym(cv, 'star4', bx, by, 60, t * 60, CREAM, t)
            cv.drawCircle(bx, by, 110, P('#7AE8A0', 255, stroke=14))
    if nose_a > 0:
        cv.save(); cv.translate(0, 0)
        pov_nose(cv, t, 1.0 * nose_a)
        cv.restore()
    if erase is not None and erase > 0:                          # la gomme passe sur le nez
        ex = PX - 300 + 700 * erase; ey = 1650 + 120 * math.sin(erase * 18)
        rnd = random.Random(int(erase * 40))
        for k in range(14): circle(cv, ex + rnd.uniform(-160, 160), ey + rnd.uniform(60, 260), rnd.uniform(8, 18), '#E8A0A8')
        cv.save(); cv.translate(ex, ey); cv.rotate(-25)
        opath(cv, rect(-90, -150, 180, 300, 24), '#E8A0A8', 9); opath(cv, rect(-90, -150, 180, 110, 24), '#4A7ACA', 9)
        cv.restore()
    cv.restore()
    cv.drawPath(rect(x0, y0, w, h, 18), P(OUT, 255, stroke=8))


def s_cerveau(cv, t, lt):
    """« Ton cerveau, lui, le voit très bien. Mais il a une règle. » : salle de contrôle, le nez à l'écran ; un parchemin se déroule."""
    control_room(cv, t, lt, nose_a=1.0, moving=False)
    hero(cv, t, 860, 1780, 120, 'open', look=(-0.6, -1.0))
    if lt > 1.95:                                               # la règle
        u = ease_out(clamp((lt - 1.95) / 0.5))
        x, y = 300, 760
        cv.save(); cv.translate(x, y)
        opath(cv, rect(-190, -30, 380, 60 + 300 * u, 14), '#F0E2C0', 7)
        if u > 0.6:
            sym(cv, 'eye', 0, 140, 70, 0, '#2A1E3A', t)
            cv.drawLine(-80, 60, 80, 220, P('#C0304A', 255, stroke=16))
        for yy in (-30, 30 + 300 * u): opath(cv, rect(-215, yy - 26, 430, 52, 26), '#C8A880', 7)
        cv.restore()


def s_regle(cv, t, lt):
    """« Ce qui ne change jamais ne mérite pas ton attention. Alors il l'efface. »"""
    er = clamp((lt - 2.65) / 0.9)
    control_room(cv, t, lt, nose_a=1 - ease(clamp((lt - 2.9) / 0.6)), erase=er if 0 < er < 1 else None, moving=True)
    hero(cv, t, 860, 1780, 120, 'lidded' if lt > 2.6 else 'open', look=(-0.6, -1.0))


def frigo(cv, x, y, s, t, g):
    opath(cv, rect(x - 0.5 * s, y - 1.6 * s, s, 1.6 * s, 0.12 * s), gray('#8FC8C0', g), 8)
    cv.drawLine(x - 0.5 * s, y - 1.05 * s, x + 0.5 * s, y - 1.05 * s, P(OUT, 255, stroke=7))
    for yy in (-1.35, -0.7): opath(cv, rect(x + 0.3 * s, y + yy * s, 0.07 * s, 0.3 * s, 0.03 * s), gray('#E0D8E8', g), 4)
    for k in range(3):                                          # sons qui s'éteignent
        u = (t * 1.2 + k / 3) % 1
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x + 0.4 * s - u * 300, y - 1.1 * s - u * 300, x + 0.6 * s + u * 300, y - 0.7 * s + u * 300), -40, 80)
        cv.drawPath(p, P(GOLD, int(230 * (1 - u) * (1 - g)), stroke=10))


def tshirt(cv, x, y, s, t, g):
    p = skia.Path(); p.moveTo(x - 0.35 * s, y - 1.2 * s); p.lineTo(x - 0.9 * s, y - 0.9 * s); p.lineTo(x - 0.7 * s, y - 0.55 * s); p.lineTo(x - 0.45 * s, y - 0.7 * s)
    p.lineTo(x - 0.45 * s, y); p.lineTo(x + 0.45 * s, y); p.lineTo(x + 0.45 * s, y - 0.7 * s); p.lineTo(x + 0.7 * s, y - 0.55 * s); p.lineTo(x + 0.9 * s, y - 0.9 * s)
    p.lineTo(x + 0.35 * s, y - 1.2 * s); p.quadTo(x, y - 0.95 * s, x - 0.35 * s, y - 1.2 * s); p.close()
    opath(cv, p, gray('#D89AAE', g), 8)
    rnd = random.Random(2)
    for k in range(10):                                         # picotements sur la peau
        u = (t * 1.5 + k / 10) % 1
        sym(cv, 'star4', x + rnd.uniform(-0.6, 0.6) * s, y - rnd.uniform(0.1, 1.1) * s, 26 * (1 - u) * (1 - g) + 0.1, 0, CREAM, t)


def maison(cv, x, y, s, t, g):
    opath(cv, rect(x - 0.55 * s, y - 0.8 * s, 1.1 * s, 0.8 * s), gray('#6A5A8A', g), 8)
    roof = skia.Path(); roof.moveTo(x - 0.7 * s, y - 0.78 * s); roof.lineTo(x, y - 1.35 * s); roof.lineTo(x + 0.7 * s, y - 0.78 * s); roof.close()
    opath(cv, roof, gray('#8A4A6A', g), 8)
    opath(cv, rect(x - 0.35 * s, y - 0.6 * s, 0.26 * s, 0.24 * s, 6), gray(GOLD, g), 5)
    for k in range(3):                                          # odeur qui serpente
        p = skia.Path(); x0 = x + (k - 1) * 0.3 * s; p.moveTo(x0, y - 1.3 * s)
        for j in range(1, 12): p.lineTo(x0 + 30 * math.sin(j * 0.9 + t * 3 + k), y - 1.3 * s - j * 30)
        cv.drawPath(p, P('#E0B890', int(230 * (1 - g)), stroke=12))


def s_tout(cv, t, lt, which):
    """Le frigo, les vêtements, l'odeur : chaque chose brille… puis devient grise."""
    banded_sky(cv, ['#0A0716', '#120C24', '#1A1032', '#22143E', '#2C184A', '#361C54'], -600, 1600, t)
    dots(cv, 51 + which, 100, (-100, -100, W + 100, 1500), '#B8A8D0')
    yy = island(cv, PX, 1600, 700, '#2A3C4C', '#1C1630', '#251E3C', t, which)
    g = ease(clamp((lt - 0.55) / 0.6))
    [frigo, tshirt, maison][which](cv, PX, yy, 380, t, g)


def s_plus(cv, t, lt):
    """« Tu ne les remarques plus » : les trois objets gris, presque effacés ; le perso blasé."""
    banded_sky(cv, ['#0A0812', '#100C1A', '#161222', '#1C162A', '#221A32', '#281E3A'], -600, 1600, t)
    for k, (fn, x) in enumerate(((frigo, 220), (tshirt, 540), (maison, 860))):
        a = 1 - 0.6 * ease(clamp(lt / 1.0))
        cv.saveLayerAlpha(None, int(255 * a)); fn(cv, x, 980 + 20 * math.sin(t + k), 170, t, 1.0); cv.restore()
    hero(cv, t, PX, 1500, 190, 'lidded', look=(0.0, 0.3))


def cadeau(cv, x, y, s, t, g):
    opath(cv, rect(x - 0.5 * s, y - 0.7 * s, s, 0.7 * s, 10), gray('#D86A8A', g), 8)
    opath(cv, rect(x - 0.58 * s, y - 0.9 * s, 1.16 * s, 0.24 * s, 10), gray('#E88AA0', g), 8)
    cv.drawRect(skia.Rect.MakeXYWH(x - 0.08 * s, y - 0.9 * s, 0.16 * s, 0.9 * s), P(gray(GOLD, g)))
    for k in range(8):
        a = k * math.pi / 4 + t
        sym(cv, 'star4', x + math.cos(a) * s, y - 0.5 * s + math.sin(a) * 0.7 * s, 30 * (1 - g) + 0.1, 0, GOLD, t)


def s_habitue(cv, t, lt):
    """« C'est pour ça que tu t'habitues à tout » : un cadeau tout neuf qui perd ses couleurs, jour après jour."""
    banded_sky(cv, ['#120A22', '#1A0E2E', '#22123A', '#2A1646', '#331A50', '#3C1E58'], -600, 1500, t)
    dots(cv, 61, 110, (-100, -100, W + 100, 1500), '#B8A8D0')
    g = ease(clamp((lt - 0.3) / 1.3))
    yy = island(cv, PX, 1550, 620, '#2A3C4C', '#1C1630', '#251E3C', t, 1.1)
    cadeau(cv, 400, yy, 300, t, g)
    hero(cv, t, 800, yy - 260, 150, 'open' if g < 0.5 else 'lidded', look=(-0.8, 0.4))
    f = skia.Font(FONT, 60); d = f'JOUR {1 + int(g * 364)}'
    tw = f.measureText(d); opath(cv, rect(PX - tw / 2 - 30, 1950 - 230, tw + 60, 90, 20), '#EFE6D8', 6)
    cv.drawString(d, PX - tw / 2, 1950 - 162, f, P('#2A1E3A'))


def s_aimes(cv, t, lt):
    """« même aux gens que tu aimes » : l'autre perso pâlit à côté de lui ; le cœur entre eux s'éteint."""
    banded_sky(cv, ['#1A0E26', '#24122E', '#2E1638', '#3A1A42', '#481E4A', '#562252'], -600, 1500, t)
    dots(cv, 71, 120, (-100, -100, W + 100, 1500), '#D8C0E0')
    striped_sun(cv, PX, 640, 170, t, ['#5A2A50', '#6C3460', '#7E406E'])
    g = ease(clamp((lt - 0.2) / 1.1))
    cv.saveLayerAlpha(None, int(255 * (1 - 0.65 * g)))
    hero(cv, t, 760, 1420, 170, 'open', look=(-0.9, 0.0), pal=OTHER, seed=9)
    cv.restore()
    hero(cv, t, 320, 1420, 170, 'lidded' if g > 0.5 else 'open', look=(0.0, 0.6))
    hx, hy = PX, 1150 + 10 * math.sin(t * 3); hs = 70 * (1 - 0.3 * g)
    p = skia.Path(); p.moveTo(hx, hy + hs); p.cubicTo(hx - hs * 1.6, hy, hx - hs * 0.8, hy - hs * 1.1, hx, hy - hs * 0.4)
    p.cubicTo(hx + hs * 0.8, hy - hs * 1.1, hx + hs * 1.6, hy, hx, hy + hs); p.close()
    opath(cv, p, mix('#E85A7A', '#4A4658', g), 7)


def s_fin(cv, t, lt):
    """« Bon… maintenant, essaie de ne plus voir ton nez. » : retour au gros plan, le nez brille, regard espiègle."""
    banded_sky(cv, ['#0A0716', '#120C24', '#1A1032', '#22143E', '#2C184A', '#361C54'], -600, 2000, t)
    dots(cv, 31, 150, (-100, -100, W + 100, H), '#B8A8D0')
    z = 1.0 + 0.3 * ease(clamp((lt - 0.8) / 2.5))
    s = 330; cx, cy = PX, 1250
    cv.save(); cv.translate(cx, cy + 0.3 * s); cv.scale(z, z); cv.translate(-cx, -(cy + 0.3 * s))
    hero(cv, t, cx, cy, s, 'lidded' if lt < 1.0 else 'open', look=(0.0, 1.0) if lt > 1.0 else (0.8, -0.3))
    if lt > 1.0: nose_glow(cv, cx, cy, s, ease_out(clamp((lt - 1.0) / 0.4)), t)
    cv.restore()


def _tout(i): return lambda cv, t, lt: s_tout(cv, t, lt, i)


# (début, scène, transition d'entrée) — transitions = mouvements de caméra : pan (gauche/droite/haut/bas), zoom (travelling avant), shake (coupe sèche + secousse)
SCENES = [(0.0, s_hook, None), (1.75, s_yeux, 'zoom'), (2.85, s_cherche, 'pan_l'), (4.3, s_reveal, 'shake'), (5.1, s_pov, 'zoom'),
          (7.2, s_journee, 'pan_u'), (8.2, s_vie, 'pan_r'), (9.2, s_pourquoi, 'pan_d'), (10.15, s_perplexe, 'zoom'), (10.95, s_ferme, 'cut'),
          (14.6, s_cerveau, 'pan_u'), (17.85, s_regle, 'zoom'), (21.65, _tout(0), 'pan_l'), (24.25, _tout(1), 'pan_l'), (25.6, _tout(2), 'pan_l'),
          (26.85, s_plus, 'pan_d'), (28.05, s_habitue, 'pan_r'), (29.9, s_aimes, 'pan_r'), (31.15, s_fin, 'zoom')]
TW = 0.22                                           # demi-durée d'une transition


def draw_scene(i, cv, t):
    s0, fn, kind = SCENES[i]; lt = t - s0
    z = 1.0 + 0.05 * ease(clamp(max(0, lt) / 3))
    cv.save(); cv.translate(PX, PY); cv.scale(z, z); cv.translate(-PX, -PY)
    if kind == 'shake' and 0 <= lt < 0.35:
        a = 30 * (1 - lt / 0.35); cv.translate(a * math.sin(lt * 90), a * math.cos(lt * 70))
    fn(cv, t, max(0.0, lt)); cv.restore()


DIRS = {'pan_l': (-1, 0), 'pan_r': (1, 0), 'pan_u': (0, -1), 'pan_d': (0, 1)}


def camera_move(cv, i, t, p):
    """La caméra se déplace de la scène i-1 vers la scène i (avec flou de bougé)."""
    kind = SCENES[i][2]
    if kind in DIRS:
        dx, dy = DIRS[kind]; L = (W if dx else H) * 1.05
        for j, aa in enumerate((255, 128, 85)):                 # 3 échantillons = flou de mouvement
            u = ease(clamp(p + (j - 1) * 0.06))
            cv.saveLayerAlpha(None, aa)
            cv.save(); cv.translate(-dx * L * u, -dy * L * u); draw_scene(i - 1, cv, t); cv.restore()
            cv.save(); cv.translate(dx * L * (1 - u), dy * L * (1 - u)); draw_scene(i, cv, t); cv.restore()
            cv.restore()
    else:                                                       # travelling avant : on fonce dans l'image, la suivante arrive
        u = ease(p)
        cv.save(); z = 1 + 5 * u ** 2; cv.translate(PX, PY); cv.scale(z, z); cv.translate(-PX, -PY); draw_scene(i - 1, cv, t); cv.restore()
        cv.saveLayerAlpha(None, int(255 * clamp((p - 0.35) / 0.4)))
        z = 0.55 + 0.45 * u; cv.save(); cv.translate(PX, PY); cv.scale(z, z); cv.translate(-PX, -PY); draw_scene(i, cv, t); cv.restore()
        cv.restore()


def scene(cv, t):
    i = 0
    for k, (s0, _, kind) in enumerate(SCENES):
        if t >= s0 - (TW if kind in DIRS or kind == 'zoom' else 0): i = k
    s0, _, kind = SCENES[i]
    if (kind in DIRS or kind == 'zoom') and t < s0 + TW:
        camera_move(cv, i, t, (t - (s0 - TW)) / (2 * TW))
    else:
        draw_scene(i, cv, t)


# ---------------- bruitages ----------------
EVENTS = [(0.05, 'beep', 0.6), (0.65, 'beep', 0.6), (1.25, 'beep', 0.6)]
for s0, _, kind in SCENES[1:]:
    if kind in DIRS: EVENTS.append((s0 - TW, 'whoosh', 0.8))
    elif kind == 'zoom': EVENTS.append((s0 - TW, 'rise', 0.5))
EVENTS += [(4.3, 'impact', 1.0), (4.33, 'ding', 0.7), (7.25, 'rise', 0.5)]
EVENTS += [(8.25 + k * 0.09, 'flip', 0.5) for k in range(10)]
EVENTS += [(9.2 + k * 0.12, 'pop', 0.5) for k in range(8)] + [(10.2, 'pop', 0.8)]
EVENTS += [(10.95, 'blink', 0.8), (11.4, 'blink', 0.6), (11.95, 'ding', 0.8), (13.3, 'pop', 0.7)]
EVENTS += [(16.55, 'unroll', 0.7), (17.1, 'click', 0.6), (20.5, 'scrub', 1.0)]
EVENTS += [(21.7, 'hum', 0.9), (24.3, 'sparkle', 0.8), (25.65, 'whoosh', 0.3), (26.2, 'powerdown', 0.6), (27.0, 'powerdown', 0.7)]
EVENTS += [(28.1, 'sparkle', 0.6), (28.6, 'powerdown', 0.6), (30.0, 'heartbeat', 0.9), (30.75, 'heartbeat', 0.5), (32.15, 'ding', 0.9)]


def frame(fi):
    t = fi / FPS
    surf = skia.Surface(OW_, OH_); cv = surf.getCanvas(); cv.scale(SC, SC)
    cv.save(); cv.translate(PX, PY); cv.rotate(0.3 * math.sin(t * 0.35)); cv.scale(1.03, 1.03)
    cv.translate(-PX + 8 * math.sin(t * 0.4), -PY + 8 * math.cos(t * 0.33))
    scene(cv, t); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1250, [C('#000000', 0), C('#000000', 0), C('#000000', 70)], [0, 0.7, 1])))
    if t < 4.3: hook_title(cv, t)
    draw_text(cv, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        from PIL import Image
        ims = []
        for ts in sys.argv[2].split(','):
            arr = np.frombuffer(frame(int(float(ts) * FPS)), np.uint8).reshape(OH_, OW_, 4)
            ims.append(Image.fromarray(arr[..., :3]).resize((270, 480), Image.LANCZOS))
        m = Image.new('RGB', (270 * min(6, len(ims)), 480 * ((len(ims) + 5) // 6)))
        for k, im in enumerate(ims): m.paste(im, ((k % 6) * 270, (k // 6) * 480))
        m.save(sys.argv[3]); sys.exit()
    sys.path.insert(0, os.path.join(HERE, '..')); import sfx
    sfx.mix(os.path.join(WORK, 'voice.wav'), EVENTS, os.path.join(WORK, 'mix_nez.wav'))
    out = os.path.join(HERE, 'nez_4k.mp4'); hd = os.path.join(HERE, 'nez_1080p.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(WORK, 'mix_nez.wav'),
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
    print('ok')

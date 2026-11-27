"""« Il y a un trou dans ta vision » — tache aveugle, test interactif à l'écran. Réutilise le moteur de « Ton nez » (texte en blocs,
caméra qui glisse d'un plan à l'autre, bruitages)."""
import math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '01_nez')); sys.path.insert(0, os.path.join(HERE, '..'))
import nez as N
from nez import (W, H, SC, OW_, OH_, PX, PY, HERO, OTHER, FONT, clamp, back, hero, banded_sky, hill, striped_sun, plant, island, dots, BIG,
                 opath, rect, pop, CREAM, GOLD, sym, OUT, P, C, mix, rad, circle, ease, ease_out, qmark, brain, loupe, pov_world, skia, X)
import numpy as np, subprocess
from multiprocessing import Pool

WORK = os.path.join(HERE, '..', 'work', '02')
N.WORK = WORK; N.DUR = DUR = 39.5; FPS = 30
N.KEYS = {'GAUCHE', 'VITE', 'CROIX', 'DROIT', 'RAPPROCHE', 'DISPARU', 'TROU', 'VISION', 'LÀ', 'TOUJOURS', 'NERF', 'OPTIQUE', 'AUCUN',
          'AVEUGLE', 'NOIR', 'CERVEAU', 'BOUCHE', 'INVENTE', 'CIEL', 'MUR', 'VISAGE', 'JAMAIS', "N'EXISTE", "L'ESPACE", 'TEMPS', 'PASSÉ', 'PARTIE', '2'}
WORDS = N.load_words()
fix = []
for i, w in enumerate(WORDS):
    if w[0] == 'TU' and i + 1 < len(WORDS) and WORDS[i + 1][0] == 'TOUJOURS': continue      # « depuis tu toujours »
    if w[0] == 'BOUGE': w[0] = 'BOUCHE'
    w[3] = w[0] in N.KEYS; fix.append(w)
N.WORDS = WORDS = fix
X.WORDS = [(w, s, k) for w, s, e, k, b in WORDS]
N.CHUNKS = N.make_chunks()

INK = '#1A1426'


# ---------------- le test ----------------
def test_card(cv, t, dot_a=1.0):
    opath(cv, rect(60, 1000, W - 120, 470, 40), '#F4EEE2', 10)
    cx, cy = 165, 1235
    cv.drawLine(cx - 55, cy, cx + 55, cy, P(INK, 255, stroke=22)); cv.drawLine(cx, cy - 55, cx, cy + 55, P(INK, 255, stroke=22))
    if dot_a > 0: cv.drawCircle(915, cy, 48, P(INK, int(255 * dot_a)))


def eye_icon(cv, x, y, r, closed, t):
    if closed:
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - r, y - r * 0.5, x + r, y + r * 0.7), 20, 140)
        cv.drawPath(p, P(OUT, 255, stroke=18)); cv.drawPath(p, P(CREAM, 255, stroke=8))
        for k in range(5): cv.drawLine(x - r * 0.7 + k * r * 0.35, y + r * 0.55, x - r * 0.8 + k * r * 0.4, y + r * 0.95, P(CREAM, 255, stroke=7))
    else:
        p = skia.Path(); p.moveTo(x - r, y); p.quadTo(x, y - r * 1.1, x + r, y); p.quadTo(x, y + r * 1.1, x - r, y); p.close()
        opath(cv, p, '#F4ECFF', 9); circle(cv, x - r * 0.15, y, r * 0.38, '#2DE2C6'); circle(cv, x - r * 0.15, y, r * 0.18, OUT)


BGS = [['#0A0716', '#120C24', '#1A1032', '#22143E', '#2C184A', '#361C54'], ['#06121A', '#0A1A24', '#0E222E', '#122A38', '#163242', '#1A3A4A'],
       ['#1A0E26', '#24122E', '#2E1638', '#3A1A42', '#481E4A', '#562252'], ['#0E0A1E', '#160E2C', '#20123A', '#2C1846', '#3A1E50', '#4A2658']]


def s_test(cv, t, lt):
    """0-7,6 s : la carte du test reste FIXE (pour que le test marche) ; tout le reste bouge autour."""
    banded_sky(cv, BGS[int(lt / 1.3) % 4], -600, 2200, t)
    dots(cv, 3 + int(lt / 1.3), 140, (-100, -100, W + 100, H), '#B8A8D0')
    for k in range(10):                                          # anneaux qui partent de la carte
        u = (lt * 0.35 + k / 10) % 1
        cv.drawRoundRect(skia.Rect.MakeLTRB(60 - 400 * u, 1000 - 400 * u, W - 60 + 400 * u, 1470 + 400 * u), 40 + 200 * u, 40 + 200 * u, P(GOLD, int(70 * (1 - u)), stroke=5))
    dot = 1.0 if lt < 6.55 else 1 - ease(clamp((lt - 6.55) / 0.5))
    test_card(cv, t, dot)
    if 6.55 < lt < 7.6:                                          # « pouf »
        u = clamp((lt - 6.55) / 0.6)
        for k in range(10):
            g = k * math.pi / 5; sym(cv, "star4", 915 + math.cos(g) * 140 * u, 1235 + math.sin(g) * 140 * u, 26 * (1 - u) + 0.1, 0, GOLD, t)
    # œil gauche fermé / œil droit ouvert -> la croix
    eye_icon(cv, 330, 1680, 85, True, t); eye_icon(cv, 750, 1680, 85, False, t)
    if lt < 3.8:
        a = skia.Path(); a.moveTo(750, 1580); a.quadTo(480, 1500, 190, 1330)
        pa = P(GOLD, 255, stroke=10); pa.setPathEffect(skia.DashPathEffect.Make([30, 20], -lt * 120)); cv.drawPath(a, pa)
    else:                                                        # « rapproche ton téléphone » : flèches qui tirent vers toi
        s = 1 + 0.12 * math.sin(lt * 7)
        for d in (-1, 1):
            cv.save(); cv.translate(PX + d * 470, 1840); cv.scale(s, s); cv.rotate(90)
            ar = skia.Path(); ar.moveTo(-60, -18); ar.lineTo(20, -18); ar.lineTo(20, -45); ar.lineTo(70, 0); ar.lineTo(20, 45); ar.lineTo(20, 18); ar.lineTo(-60, 18); ar.close()
            opath(cv, ar, GOLD, 6); cv.restore()


def hook_title(cv, t):
    a = 1.0 if t < 7.3 else max(0.0, 1 - (t - 7.3) / 0.3)
    lines = (("FERME L'ŒIL GAUCHE", GOLD, 104), ('ET FIXE LA CROIX', CREAM, 84)) if t < 3.75 else (('RAPPROCHE', GOLD, 104), ('DOUCEMENT TON ÉCRAN', CREAM, 78))
    for i, (txt, col, size) in enumerate(lines):
        f = skia.Font(FONT, size); tw = f.measureText(txt)
        if tw > 980: f.setSize(size * 980 / tw); size = f.getSize(); tw = f.measureText(txt)
        y = 230 + i * 120
        o = P(OUT, int(255 * a), stroke=size * 0.18); o.setStrokeJoin(skia.Paint.kRound_Join)
        cv.drawString(txt, W / 2 - tw / 2 + 3, y + 6, f, o); cv.drawString(txt, W / 2 - tw / 2, y, f, o)
        cv.drawString(txt, W / 2 - tw / 2, y, f, P(col, int(255 * a)))


# ---------------- le trou ----------------
def hole(cv, x, y, r, t, a=1.0, ring=0.0):
    p = N.R.pd if False else None
    cv.drawCircle(x, y, r, P('#000000', int(255 * a)))
    for k in range(6):
        g = k * math.pi / 3 + t * 0.8; cv.drawCircle(x + math.cos(g) * r * 0.9, y + math.sin(g) * r * 0.9, r * 0.25, P('#000000', int(200 * a)))
    if ring > 0:
        for j in range(3): cv.drawCircle(x, y, r * (1.3 + 0.3 * j) + 10 * math.sin(t * 6 - j), P(GOLD, int((230 - j * 60) * ring), stroke=8))


def vignette(cv):
    vf = skia.Path(); vf.addOval(skia.Rect.MakeLTRB(-260, 120, W + 260, H - 120))
    full = skia.Path(); full.addRect(skia.Rect.MakeLTRB(-600, -600, W + 600, H + 600))
    cv.drawPath(skia.Op(full, vf, skia.PathOp.kDifference_PathOp), P('#06040C', 235)); cv.drawPath(vf, P(OUT, 255, stroke=10))


def s_trou(cv, t, lt):
    """« T'as un trou dans ta vision. Là ! » : ta vue, avec un trou noir."""
    pov_world(cv, t, 0)
    hole(cv, 720, 1150, 110 * ease_out(clamp(lt / 0.4)), t, ring=clamp((lt - 1.35) / 0.3))
    vignette(cv)


def s_toujours(cv, t, lt):
    """« Depuis toujours » : bébé perso dans son berceau, le trou flotte déjà devant lui."""
    banded_sky(cv, BGS[2], -600, 2000, t); dots(cv, 9, 120, (-100, -100, W + 100, H), '#D8C0E0')
    for k in range(5): sym(cv, 'star4', 150 + k * 200, 380 + 60 * math.sin(t * 2 + k), 26, 0, CREAM, t)
    opath(cv, rect(240, 1500, 600, 260, 60), '#8A6AAA', 10)
    for k in range(7): cv.drawLine(280 + k * 85, 1500, 280 + k * 85, 1380, P(OUT, 255, stroke=14)); cv.drawLine(280 + k * 85, 1500, 280 + k * 85, 1380, P('#C8A8D8', 255, stroke=7))
    cv.drawLine(250, 1380, 830, 1380, P(OUT, 255, stroke=18)); cv.drawLine(250, 1380, 830, 1380, P('#C8A8D8', 255, stroke=10))
    hero(cv, t, PX, 1300, 110, 'open', look=(0.6, -0.6), seed=3)
    hole(cv, 720, 1050, 40, t, ring=0.6)


def s_oeil(cv, t, lt):
    """« Au fond de chaque œil… le nerf optique » : coupe de l'œil, la lumière entre, le nerf sort derrière."""
    cv.drawRect(BIG, P('#120A1C')); dots(cv, 11, 100, (-100, -100, W + 100, H), '#9A8AB8')
    cx, cy, r = PX + 40, 1150, 380
    opath(cv, skia.Path().addCircle(cx, cy, r), '#F4ECFF', 12)
    cv.save(); cv.clipPath(skia.Path().addCircle(cx, cy, r - 6), doAntiAlias=True)
    cv.drawCircle(cx, cy, r - 6, P('#2A1E3A', 60))
    ret = skia.Path(); ret.addArc(skia.Rect.MakeLTRB(cx - r + 30, cy - r + 30, cx + r - 30, cy + r - 30), -80, 160); cv.drawPath(ret, P('#D86A8A', 255, stroke=34))
    cv.restore()
    opath(cv, skia.Path().addOval(skia.Rect.MakeLTRB(cx - r - 30, cy - 120, cx - r + 60, cy + 120)), '#8FC8C0', 9)     # cristallin
    for k in range(5):                                           # rayons de lumière
        y0 = cy - 200 + k * 100; u = (lt * 1.2 + k * 0.2) % 1
        cv.drawLine(-50, y0, cx - r, cy + (y0 - cy) * 0.3, P(GOLD, 200, stroke=8))
        cv.drawLine(cx - r, cy + (y0 - cy) * 0.3, cx + r - 40, cy - (y0 - cy) * 0.8, P(GOLD, 140, stroke=6))
    nerve = skia.Path(); nerve.moveTo(cx + r - 40, cy + 40); nerve.cubicTo(cx + r + 150, cy + 60, cx + r + 120, cy + 400, PX + 520, cy + 600)
    g = clamp((lt - 1.2) / 0.6)
    cv.drawPath(nerve, P(OUT, 255, stroke=110)); cv.drawPath(nerve, P(mix('#E0B890', GOLD, g), 255, stroke=90))
    for k in range(5):                                           # influx dans le nerf
        u = (lt * 0.8 + k / 5) % 1; pm = skia.PathMeasure(nerve, False); pt = pm.getPosTan(u * pm.getLength())[0]
        circle(cv, pt.x(), pt.y(), 14, CREAM)
    hero(cv, t, 200, 1830, 90, 'open', look=(0.8, -0.8), seed=4)


def s_capteurs(cv, t, lt):
    """« aucun capteur de lumière. Tu es aveugle » : zoom sur la rétine, rangée de capteurs, un vide au milieu."""
    cv.drawRect(BIG, P('#1A0A18'))
    for row in range(3):
        y = 900 + row * 260
        for k in range(14):
            x = 40 + k * 76
            if 4 <= k <= 8: continue
            h = 200 + 20 * math.sin(k * 1.7 + row)
            lit = 0.5 + 0.5 * math.sin(t * 5 + k * 0.7 + row)
            opath(cv, rect(x, y - h / 2, 46, h, 23), mix('#8FC8C0', GOLD, lit * 0.6), 6)
            circle(cv, x + 23, y - h / 2 + 30, 12, CREAM)
    cv.drawRect(skia.Rect.MakeLTRB(330, 650, 690, 1650), P('#000000', 255))
    blind = clamp((lt - 2.35) / 0.3)
    if blind > 0:
        for j in range(3): cv.drawRect(skia.Rect.MakeLTRB(330 - j * 22, 650 - j * 22, 690 + j * 22, 1650 + j * 22), P('#E8506A', int((230 - 60 * j) * blind), stroke=8))
    for k in range(6):                                           # la lumière tombe dans le vide et disparaît
        u = (lt * 0.9 + k / 6) % 1; x = 360 + k * 55
        circle(cv, x, 600 + 900 * u, 14, GOLD, int(255 * (1 - u)))


def s_pourquoi(cv, t, lt):
    """« Alors pourquoi tu ne vois pas un trou noir en permanence ? »"""
    banded_sky(cv, BGS[0], -600, 1500, t); dots(cv, 13, 110, (-100, -100, W + 100, 1500), '#B8A8D0')
    hill(cv, 1650, 40, 0.006, 1.0, '#1A1830', '#22203C', t, n=3)
    hero(cv, t, 330, 1420, 200, 'open', look=(1.0, -0.5), arms='think')
    hole(cv, 760, 1000, 150 + 15 * math.sin(t * 2), t)
    rnd = random.Random(4)
    for k in range(5):
        u = pop(lt, 0.3 + k * 0.25, 0.4)
        if u > 0: qmark(cv, rnd.uniform(600, 1000), rnd.uniform(650, 1500), 110 * u, rnd.uniform(-20, 20), rnd.choice([GOLD, CREAM]))


def screen_scene(cv, t, lt, fill, scan):
    """Salle de contrôle : à l'écran, la vue avec le trou ; le cerveau regarde autour (loupe) puis bouche le trou."""
    N.control_room(cv, t, lt, nose_a=0, moving=False)
    x0, y0, w, h = 140, 1080, 800, 620
    cv.save(); cv.clipPath(rect(x0, y0, w, h, 18), doAntiAlias=True)
    hx, hy = x0 + 520, y0 + 260
    if fill < 1:
        hole(cv, hx, hy, 80, t, a=1 - fill)
    if 0 < fill < 1:                                            # pinceau qui repeint avec les couleurs d'autour
        bx = hx - 80 + 160 * fill; by = hy - 40 + 60 * math.sin(fill * 20)
        cv.save(); cv.translate(bx, by); cv.rotate(-35)
        opath(cv, rect(-12, -150, 24, 140, 10), '#C8946A', 5); opath(cv, rect(-20, -20, 40, 50, 10), '#B8D8E8', 5); cv.restore()
    if scan > 0:
        g = lt * 3; loupe(cv, hx + 140 * math.cos(g), hy + 100 * math.sin(g), 60, t)
    cv.restore()


def s_bouche(cv, t, lt):
    screen_scene(cv, t, lt, 0, 0)
    hero(cv, t, 860, 1780, 120, 'open', look=(-0.6, -1.0))
    u = pop(lt, 0.6, 0.4)
    if u > 0:                                                    # le bouchon arrive
        cv.save(); cv.translate(660, 1340 - 300 * (1 - min(1, u))); cv.scale(u, u)
        opath(cv, rect(-60, -50, 120, 100, 20), '#C8946A', 7); cv.restore()


def s_invente(cv, t, lt):
    screen_scene(cv, t, lt, clamp((lt - 1.4) / 1.1), 1 if lt < 1.4 else 0)
    hero(cv, t, 860, 1780, 120, 'lidded', look=(-0.6, -1.0))


def patch_scene(cv, t, lt, kind):
    """Le trou se remplit avec ce qu'il y a autour : ciel, mur, visage."""
    if kind == 0:
        banded_sky(cv, ['#2A3E6A', '#34508A', '#4062A0', '#5274B0', '#6888C0', '#7E9CCC'], -600, 2200, t)
        for k in range(5): opath(cv, skia.Path().addOval(skia.Rect.MakeXYWH(80 + k * 240, 300 + 300 * (k % 2), 220, 90)), '#E8EEF8', 6)
    elif kind == 1:
        cv.drawRect(BIG, P('#5A2A2E'))
        for r in range(22):
            for c in range(7):
                x = c * 170 - (85 if r % 2 else 0); y = r * 90
                opath(cv, rect(x + 6, y + 6, 158, 78, 8), ['#A0524A', '#8E463F', '#B05E52'][(r + c) % 3], 5)
    else:
        cv.drawRect(BIG, P('#2A1A3A')); hero(cv, t, PX, 1100, 420, 'open', look=(0.0, 0.0))
    fill = ease(clamp((lt - 0.2) / 0.5)); hx, hy = (640, 1000) if kind < 2 else (PX + 90, 1060)
    hole(cv, hx, hy, 110, t, a=1 - fill)
    if fill > 0:
        cv.drawCircle(hx, hy, 130, P(GOLD, int(230 * (1 - abs(fill - 0.6))), stroke=8))
        if fill < 1: sym(cv, 'star4', hx + 90, hy - 90, 40, t * 90, CREAM, t)


def s_prevenir(cv, t, lt):
    """« Sans jamais te prévenir » : le perso sourit, ignorant ; derrière lui le cerveau fait chut."""
    banded_sky(cv, BGS[3], -600, 1600, t); dots(cv, 15, 110, (-100, -100, W + 100, 1500), '#B8A8D0')
    brain(cv, 760, 700, 220, t)
    cv.save(); cv.translate(760, 980); opath(cv, rect(-20, -150, 40, 160, 20), '#E8A0B8', 6); cv.restore()     # doigt « chut »
    hero(cv, t, 330, 1450, 200, 'lidded', look=(-0.3, 0.2))


def s_existe(cv, t, lt):
    """« Une partie de ce que tu vois… n'existe pas » : une zone de la vue se révèle en grille vide, puis se referme."""
    pov_world(cv, t, 0)
    r = 260 * ease(clamp((lt - 1.7) / 0.6))
    if r > 1:
        cv.save(); cv.clipPath(skia.Path().addCircle(640, 1080, r), doAntiAlias=True)
        cv.drawRect(BIG, P('#0A0814'))
        for k in range(-20, 30): cv.drawLine(k * 50, 0, k * 50, H, P('#5AE0C8', 120, stroke=2)); cv.drawLine(0, k * 50, W, k * 50, P('#5AE0C8', 120, stroke=2))
        cv.restore(); cv.drawCircle(640, 1080, r, P(GOLD, 255, stroke=8))
    vignette(cv)


def clock(cv, x, y, r, t, gap, fill):
    opath(cv, skia.Path().addCircle(x, y, r), '#EFE6D8', 10)
    for k in range(12):
        g = k * math.pi / 6; cv.drawLine(x + math.cos(g) * r * 0.8, y + math.sin(g) * r * 0.8, x + math.cos(g) * r * 0.92, y + math.sin(g) * r * 0.92, P(INK, 255, stroke=8))
    if gap:
        wedge = skia.Path(); wedge.moveTo(x, y); wedge.arcTo(skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), -10, 70, False); wedge.close()
        cv.drawPath(wedge, P('#000000', int(255 * (1 - fill))))
    g = t * 2; cv.drawLine(x, y, x + math.cos(g) * r * 0.75, y + math.sin(g) * r * 0.75, P(INK, 255, stroke=10))
    cv.drawLine(x, y, x + math.cos(g / 12) * r * 0.5, y + math.sin(g / 12) * r * 0.5, P(INK, 255, stroke=14)); circle(cv, x, y, 14, '#C0304A')


def s_espace(cv, t, lt):
    """« …pas que des trous dans l'espace… » : le paysage, son trou rebouché."""
    banded_sky(cv, BGS[1], -600, 1500, t); dots(cv, 17, 120, (-100, -100, W + 100, 1500), '#A8C8D0')
    hill(cv, 1450, 40, 0.006, 0.6, '#12262E', '#183038', t); hill(cv, 1650, 50, 0.005, 2.0, '#0C1C24', '#12262E', t)
    f = ease(clamp(lt / 0.8)); hole(cv, PX, 950, 140, t, a=1 - f)
    if f > 0.3: cv.drawCircle(PX, 950, 160, P(GOLD, int(200 * (1 - f) + 40), stroke=7))


def s_tempsc(cv, t, lt):
    """« …il bouche aussi des trous dans le temps » : une horloge avec un morceau manquant, que le cerveau rebouche."""
    banded_sky(cv, BGS[0], -600, 1500, t); dots(cv, 19, 120, (-100, -100, W + 100, 1500), '#B8A8D0')
    clock(cv, PX, 1080, 330, t, True, ease(clamp((lt - 0.9) / 0.8)))
    hero(cv, t, 860, 1800, 110, 'open', look=(-0.6, -1.0))


def s_passe(cv, t, lt):
    """« tout ce que tu vois… s'est déjà passé » : la vraie balle est devant, celle que tu vois a un temps de retard."""
    banded_sky(cv, BGS[2], -600, 1700, t); dots(cv, 23, 110, (-100, -100, W + 100, 1500), '#D8C0E0')
    hill(cv, 1700, 30, 0.007, 1.0, '#2A1A3A', '#32203F', t, n=3)
    u = (lt * 0.5) % 1
    def bp(v): return (100 + 880 * v, 1300 - 700 * math.sin(math.pi * v))
    x1, y1 = bp(min(1, u + 0.12)); x0, y0 = bp(u)
    cv.drawCircle(x1, y1, 55, P(CREAM, 255, stroke=6)); cv.drawCircle(x1, y1, 55, P(CREAM, 40))        # la vraie (fantôme)
    opath(cv, skia.Path().addCircle(x0, y0, 55), '#E88A5A', 7)
    f = skia.Font(FONT, 46); cv.drawString('-0,1 s', x0 - 70, y0 + 120, f, P(GOLD))
    hero(cv, t, PX, 1650, 170, 'open', look=((x0 - PX) / 500, -0.8))


def s_partie2(cv, t, lt):
    """« Ça, c'est la partie 2. »"""
    banded_sky(cv, ['#1E1838', '#2A2048', '#3A2A58', '#4C3466', '#5E4072', '#704C7C'], -600, 1600, t)
    dots(cv, 29, 110, (-100, -100, W + 100, 1500), '#D8C8E0')
    u = pop(lt, 0.4, 0.5)
    if u > 0:
        cv.save(); cv.translate(PX, 1180); cv.scale(u, u); cv.rotate(-4 + 2 * math.sin(t * 3))
        opath(cv, rect(-330, -130, 660, 260, 40), GOLD, 10)
        f = skia.Font(FONT, 150); tw = f.measureText('PARTIE 2'); cv.drawString('PARTIE 2', -tw / 2, 55, f, P('#2A1E3A'))
        cv.restore()
        clock(cv, 840, 920, 90, t, False, 0)
    hero(cv, t, 300, 1650, 150, 'lidded', look=(0.9, -0.6))


T = lambda k: (lambda cv, t, lt: patch_scene(cv, t, lt, k))
N.SCENES = SCENES = [(0.0, s_test, None), (7.75, s_trou, 'pan_d'), (9.65, s_toujours, 'pan_r'), (10.8, s_oeil, 'pan_l'), (13.85, s_capteurs, 'pan_u'),
                     (17.2, s_pourquoi, 'pan_d'), (19.75, s_bouche, 'pan_r'), (21.25, s_invente, 'cut'), (23.95, T(0), 'pan_u'),
                     (24.72, T(1), 'pan_l'), (25.4, T(2), 'pan_l'), (26.1, s_prevenir, 'pan_d'), (27.7, s_existe, 'pan_r'),
                     (30.7, s_espace, 'pan_u'), (32.7, s_tempsc, 'pan_l'), (34.5, s_passe, 'pan_d'), (37.15, s_partie2, 'pan_u')]
TW = N.TW

EVENTS = [(0.0, 'impact', 0.6), (0.02, 'beep', 0.7), (0.9, 'beep', 0.7), (1.6, 'ting', 0.5), (3.85, 'rise', 0.5), (6.6, 'sparkle', 0.9), (7.15, 'ding', 0.9)]
for s0, _, kind in SCENES[1:]:
    if kind in N.DIRS: EVENTS.append((s0 - TW + 0.05, 'whoosh', 0.55))
EVENTS += [(s, 'pop', 0.22) for w, s, e, k, b in WORDS if k]
EVENTS += [(9.2, 'impact', 0.6), (11.2, 'hum', 0.4), (16.25, 'powerdown', 0.8), (17.5 + 0.25 * 0 + 0.3, 'pop', 0.5), (17.75 + 0.3, 'pop', 0.5),
           (18.3, 'pop', 0.5), (18.55, 'pop', 0.5), (18.8, 'pop', 0.5), (20.35, 'pop', 0.8), (21.3, 'ting', 0.5), (22.0, 'ting', 0.4),
           (22.65, 'scrub', 0.8), (24.15, 'sparkle', 0.6), (24.9, 'sparkle', 0.6), (25.6, 'sparkle', 0.6), (26.3, 'boing', 0.4),
           (29.4, 'powerdown', 0.6), (33.6, 'sparkle', 0.6), (35.0, 'click', 0.4), (37.55, 'ding', 0.9), (37.6, 'impact', 0.5)]
EVENTS += [(32.75 + k * 0.5, 'click', 0.35) for k in range(4)]


def frame(fi):
    t = fi / FPS
    surf = skia.Surface(OW_, OH_); cv = surf.getCanvas(); cv.scale(SC, SC)
    shake = t > 7.75                                             # la carte du test ne bouge PAS au début
    cv.save()
    if shake:
        cv.translate(PX, PY); cv.rotate(0.3 * math.sin(t * 0.35)); cv.scale(1.03, 1.03); cv.translate(-PX + 8 * math.sin(t * 0.4), -PY + 8 * math.cos(t * 0.33))
    N.scene(cv, t); cv.restore()
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(W / 2, H / 2, 1250, [C('#000000', 0), C('#000000', 0), C('#000000', 70)], [0, 0.7, 1])))
    if t < 7.6: hook_title(cv, t)
    N.draw_text(cv, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()


# pas de zoom lent pendant le test (la carte doit rester fixe)
_ds = N.draw_scene
def draw_scene(i, cv, t):
    if i == 0:
        s0, fn, kind = SCENES[0]; fn(cv, t, max(0.0, t - s0)); return
    _ds(i, cv, t)
N.draw_scene = draw_scene


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
    import sfx
    sfx.mix(os.path.join(WORK, 'voice.wav'), EVENTS, os.path.join(WORK, 'mix.wav'))
    out = os.path.join(HERE, 'tache_aveugle_4k.mp4'); hd = os.path.join(HERE, 'tache_aveugle_1080p.mp4')
    n = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW_}x{OH_}', '-r', str(FPS), '-i', '-',
                           '-i', os.path.join(WORK, 'mix.wav'),
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

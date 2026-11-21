"""« Le signal Wow! » : 14 plans, style sombre, onirique et un peu psychédélique (TikToks × Midnight Gospel)."""
import math, os, random, sys, importlib.util
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('../calendrier', '../temps', '../profil'):
    sys.path.insert(1, os.path.join(HERE, d))
from lib import *
from kit import Stars, sparkle, neon
from mg import *
_s = importlib.util.spec_from_file_location('machine_scenes', os.path.join(HERE, '..', 'machine', 'scenes.py'))
ms = importlib.util.module_from_spec(_s); _s.loader.exec_module(ms)
night, stars, hero, eyes_field, OLD, pd = ms.night, ms.stars, ms.hero, ms.eyes_field, ms.OLD, ms.pd

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7, readable=True,
             fps=60, trans=0.75, float=True, trans_kinds=['ripple', 'ink', 'liquid', 'dissolve', 'ripple', 'iris', 'ink', 'dissolve'])


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


DARKPSY = ['#5A0E5A', '#1E3A6A', '#3A0E6A', '#0E4A5A', '#6A1A3A']


def ribbons(cv, t, seed, n=5, y0=150, spread=110, a=150, amp=60):
    """Rubans psychédéliques sombres qui ondulent dans le ciel (comme des aurores de nuit)."""
    rnd = random.Random(seed)
    for i in range(n):
        y = y0 + i * spread
        ph = rnd.uniform(0, 6.28); w = rnd.uniform(40, 90)
        top, bot = [], []
        for x in range(-300, W + 340, 40):
            yy = y + amp * math.sin(x * 0.004 + ph + t * 0.6) + 20 * math.sin(x * 0.011 + t)
            ww = w * (0.6 + 0.4 * math.sin(x * 0.006 + ph))
            top.append((x, yy - ww / 2)); bot.append((x, yy + ww / 2))
        p = skia.Path(); p.moveTo(*top[0])
        for q in top[1:]:
            p.lineTo(*q)
        for q in reversed(bot):
            p.lineTo(*q)
        p.close()
        c1, c2 = DARKPSY[i % 5], DARKPSY[(i + 2) % 5]
        cv.drawPath(p, P(shader=lin(0, y - 60, W, y + 60, [c1, c2, c1]), a=a))
        cv.drawPath(p, P(OLD, a, stroke=4))


def dish(cv, x, y, s, ang, col='#3A2A6A'):
    """Antenne parabolique (pied + coupole), cernée, orientée de ang degrés."""
    ofill(cv, ppoly([(x - 0.25 * s, y), (x + 0.25 * s, y), (x + 0.08 * s, y - 0.7 * s), (x - 0.08 * s, y - 0.7 * s)]), '#2A1A4A', ol=OLD)
    cv.save(); cv.translate(x, y - 0.75 * s); cv.rotate(ang)
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(-0.7 * s, -0.5 * s, 0.7 * s, 0.5 * s), 180, 180); p.close()
    ofill(cv, p, col, ol=OLD)
    cv.drawLine(0, 0, 0, -0.65 * s, P(OLD, 255, stroke=6))
    ofill(cv, pcircle(0, -0.68 * s, 0.07 * s), '#2DE2E6', ol=OLD, w=4)
    cv.restore()


def signal_line(cv, x0, x1, y, t, spike=0.0, amp=18, col='#2DE2E6', a=255):
    """Ligne d'oscilloscope : bruit + éventuel pic au centre."""
    rnd = random.Random(int(t * 30))
    pts = []
    for i in range(121):
        u = i / 120
        x = x0 + (x1 - x0) * u
        n = amp * (rnd.random() - 0.5) * 2
        pk = spike * math.exp(-((u - 0.5) ** 2) / 0.002)
        pts.append((x, y - n - pk))
    neon(cv, pts, col, w=4, a=a, glow_w=14)


def earth_small(cv, x, y, r):
    glow(cv, x, y, r * 1.6, '#2DB8FF', 120)
    ofill(cv, pcircle(x, y, r), '#1E4A9A', ol=OLD)
    cv.save(); cv.clipPath(pcircle(x, y, r), doAntiAlias=True)
    for k in range(4):
        ofill(cv, pblob(x - r * 0.5 + k * r * 0.4, y - r * 0.3 + (k % 2) * r * 0.5, r * 0.3, seed=k), '#1E7A5A', ol=OLD, w=3)
    cv.restore()


# 1 ─ « Le quinze août 1977, quelque chose dans l'espace nous a envoyé un signal. »
class Arrive(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        self.st = stars(901, 260)

    def static(self, cv):
        night(cv, 1, '#02010A', '#120628', '#2A0A3A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        ribbons(cv, t, 2, 4, 120, 120, 110)
        k = ease(t / max(d * 0.85, 0.1))
        x0, y0, x1, y1 = 120, 180, 1560, 760
        pts = []
        for i in range(60):
            u = i / 59 * k
            x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u
            pts.append((x + 0, y + 26 * math.sin(u * 40 - t * 8)))
        if len(pts) > 2:
            neon(cv, pts, '#FF4FD8', w=6, glow_w=22)
        glow(cv, pts[-1][0], pts[-1][1], 60, '#FFB0E8', 230)
        earth_small(cv, 1600, 800, 110)
        label(cv, 260, 1000, '15 · 08 · 1977', 32, color='#B98CFF', font=FONT)


# 2 ─ « Pendant soixante-douze secondes. Et puis plus rien. Jamais. »
class Seconds(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        night(cv, 3, '#000000', '#05020F', '#0E0620')

    def dyn(self, cv, t, d):
        k = min(1.0, t / max(d * 0.55, 0.1))
        on = k < 1.0
        cv.drawRect(skia.Rect.MakeXYWH(260, 760, 1400, 220), P('#0E1A2A', 230))
        cv.drawRect(skia.Rect.MakeXYWH(260, 760, 1400, 220), P('#2DE2E6', 160, stroke=3))
        if on:
            signal_line(cv, 300, 1620, 870, t, spike=70 * math.sin(k * math.pi), amp=10)
        else:
            neon(cv, [(300, 870), (1620, 870)], '#2DE2E6', w=3, a=120, glow_w=8)
        sec = int(72 * k)
        label(cv, 960, 200, f'{sec:02d} s', 60, color='#2DE2E6' if on else '#5A5A7A', font=FONT, box=False)
        if not on:
            fade = min(1.0, (t - d * 0.55) / 0.6)
            cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, 1150), P('#000000', 150 * fade))


# 3 ─ « Cette nuit-là, dans l'Ohio, un radiotélescope géant écoute le ciel. »
class BigEar(Scene):
    zoom = (1.12, 1.0)
    pan = (40, 0, -40, 0)

    def __init__(self):
        self.st = stars(903, 260)

    def static(self, cv):
        night(cv, 4, '#02010A', '#0E1030', '#1A0E3A')
        # champ de réflecteurs en perspective
        for r in range(9):
            y = 760 + r * 38 + r * r * 3
            sc = 0.45 + r * 0.12
            for c in range(-12, 13):
                x = 960 + c * 150 * sc
                ofill(cv, ppoly([(x - 66 * sc, y), (x + 66 * sc, y), (x + 74 * sc, y + 30 * sc), (x - 74 * sc, y + 30 * sc)]), '#3A3A6A' if (r + c) % 2 else '#2E2E5A', ol=OLD, w=3)
        # grands réflecteurs
        p = skia.Path(); p.moveTo(140, 760); p.lineTo(140, 380); p.quadTo(400, 330, 640, 400); p.lineTo(640, 760); p.close()
        ofill(cv, p, '#4A4A7A', ol=OLD)
        for k in range(10):
            cv.drawLine(160 + k * 48, 390 + (k % 2) * 6, 160 + k * 48, 760, P(OLD, 150, stroke=3))
        p = skia.Path(); p.moveTo(1300, 760); p.lineTo(1300, 470); p.lineTo(1780, 420); p.lineTo(1780, 760); p.close()
        ofill(cv, p, '#4A4A7A', ol=OLD)
        for k in range(10):
            cv.drawLine(1320 + k * 46, 470 - k * 5, 1320 + k * 46, 760, P(OLD, 150, stroke=3))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        ribbons(cv, t, 5, 3, 140, 100, 80, amp=40)
        for k in range(4):
            q = (t * 0.4 + k / 4) % 1
            r = 80 + q * 700
            cv.drawCircle(960, 760, r, P('#2DE2E6', 120 * (1 - q), stroke=3))
        label(cv, 960, 1010, 'BIG EAR · OHIO', 28, color='#2DE2E6', font=FONT)


# 4 ─ « Il n'entend presque que du bruit. Le souffle du cosmos. »
class Noise(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        night(cv, 5, '#02010A', '#14062A', '#24082E')

    def dyn(self, cv, t, d):
        ribbons(cv, t * 1.4, 6, 6, 100, 140, 160, amp=80)
        rnd = random.Random(int(t * 24))
        for _ in range(500):
            circle(cv, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 2.5), rnd.choice(['#B98CFF', '#2DE2E6', '#FFFFFF']), rnd.uniform(40, 160))
        cv.drawRect(skia.Rect.MakeXYWH(260, 800, 1400, 160), P('#0E1A2A', 200))
        signal_line(cv, 300, 1620, 880, t, amp=22, col='#7A8BFF')


# 5 ─ « Et soudain, un signal surgit. Puissant. Étroit. »
class Surge(Scene):
    zoom = (1.0, 1.15)
    shake = 0.35

    def __init__(self):
        self.st = stars(905, 200)

    def static(self, cv):
        night(cv, 6, '#05020F', '#1A0630', '#3A0A3A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        k = ease_out(t / 0.6)
        for i in range(10):
            q = (t * 0.7 + i / 10) % 1
            cv.drawCircle(960, 1000, 200 + q * 1200, P(['#FF4FD8', '#2DE2E6', '#FFB05A'][i % 3], 150 * (1 - q), stroke=6))
        glow(cv, 960, 300, 500 * k, '#FF4FD8', 160)
        neon(cv, [(960, 1080), (960, 1080 - 1000 * k)], '#FFB0E8', w=14, glow_w=50)
        hero(cv, t, 960, 820, 200, eyes='open')
        glow(cv, 960, 820 - 0.55 * 200, 140 * k, '#FFE680', 255)


# 6 ─ « Pile sur la fréquence de l'hydrogène, l'élément le plus répandu de l'univers. »
class Hydrogen(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        self.st = stars(906, 220)

    def static(self, cv):
        night(cv, 7, '#05020F', '#120836', '#2A0A40')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        ribbons(cv, t, 8, 3, 160, 330, 90)
        cx, cy = 960, 540
        p = 1 + 0.05 * math.sin(t * 4)
        glow(cv, cx, cy, 300 * p, '#FF4FD8', 200)
        ofill(cv, pcircle(cx, cy, 110 * p), '#E83CB8', ol=OLD)
        oval(cv, cx - 30, cy - 40, 30, 16, '#FFB0E8', 200)
        for j, (rx, ry, rot) in enumerate(((520, 170, 15), (480, 200, -35))):
            cv.save(); cv.translate(cx, cy); cv.rotate(rot)
            cv.drawOval(skia.Rect.MakeLTRB(-rx, -ry, rx, ry), P(OLD, 255, stroke=10))
            cv.drawOval(skia.Rect.MakeLTRB(-rx, -ry, rx, ry), P('#2DE2E6', 200, stroke=4))
            if j == 0:
                a = t * 2.4
                ex, ey = rx * math.cos(a), ry * math.sin(a)
                glow(cv, ex, ey, 60, '#2DE2E6', 255)
                ofill(cv, pcircle(ex, ey, 26), '#BFF6FF', ol=OLD, w=5)
            cv.restore()
        label(cv, 960, 980, 'HYDROGÈNE · 1420 MHz', 30, color='#2DE2E6', font=FONT)


# 7 ─ « Exactement là où des scientifiques avaient prédit qu'une civilisation choisirait d'émettre. »
class Dial(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        night(cv, 8, '#0A0414', '#1A0A2A', '#2A1430')

    def dyn(self, cv, t, d):
        cx, cy = 1180, 460
        ofill(cv, prr(cx - 460, cy - 220, 920, 440, 40), '#3A2A1A', ol=OLD)
        ofill(cv, prr(cx - 400, cy - 170, 800, 230, 20), '#E8C88A', ol=OLD)
        for i in range(41):
            x = cx - 380 + i * 19
            h = 40 if i % 5 == 0 else 20
            cv.drawLine(x, cy - 160, x, cy - 160 + h, P(OLD, 255, stroke=3))
        for i, f in enumerate(('1300', '1350', '1400', '1450', '1500')):
            label(cv, cx - 380 + i * 190, cy - 70, f, 22, color=OLD, font=FONT, box=False)
        k = ease(t / max(d * 0.7, 0.1))
        nx = cx - 380 + (0.2 + 0.4 * k + 0.02 * math.sin(t * 9) * (1 - k)) * 760
        cv.drawLine(nx, cy - 170, nx, cy + 60, P('#E8243C', 255, stroke=6))
        glow(cv, nx, cy - 50, 60, '#FF4F6B', 120 * k)
        for j in range(2):
            ofill(cv, pcircle(cx - 240 + j * 480, cy + 140, 50), '#5A4A3A', ol=OLD)
        for i in range(3):
            hero(cv, t, 280 + i * 190, 880, 95, eyes='lidded', third=False, hair_up=False,
                 skin=['#D8B8A8', '#B48AE0', '#8AD8A8'][i], hair=['#5A5A6A', '#2A1050', '#1A3A2A'][i], robe=['#3A2A1A', '#1E3A5A', '#3A1A2A'][i], seed=30 + i)
        label(cv, 470, 1010, '1959 · COCCONI & MORRISON', 24, color='#E8C88A', font=FONT)


# 8 ─ « Quelques jours plus tard, l'astronome Jerry Ehman découvre les chiffres sur le papier. »
class Desk(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        night(cv, 9, '#05020A', '#140A1E', '#1E1024')
        glow(cv, 520, 300, 500, '#FFB05A', 130)

    def dyn(self, cv, t, d):
        ofill(cv, prr(-100, 860, W + 200, 300, 0), '#2A1A14', ol=OLD)
        ofill(cv, ppoly([(440, 200), (600, 200), (650, 300), (390, 300)]), '#E8A04A', ol=OLD)
        cv.drawLine(520, 300, 520, 860, P(OLD, 255, stroke=10))
        # listing d'imprimante qui se déroule
        off = (t * 120) % 60
        cv.save(); cv.clipPath(prr(900, -50, 600, 960, 0), doAntiAlias=True)
        ofill(cv, prr(950, -100, 500, 1100, 0), '#F4EEDC', ol=OLD)
        rnd = random.Random(int(t * 2))
        for row in range(20):
            y = -40 + row * 60 + off
            s = ''.join(rnd.choice('1111112345 ') for _ in range(14))
            label(cv, 1200, y, s, 26, color='#5A5A6A', font=FONT, box=False)
        cv.restore()
        for k in (-1, 1):
            cv.drawLine(950 + (0 if k < 0 else 500), -100, 950 + (0 if k < 0 else 500), 1000, P('#C8C0A8', 255, stroke=3))
        hero(cv, t, 560, 770, 140, eyes='open', third=False, hair_up=False, skin='#E0B8A0', hair='#3A2A1A', robe='#5A3A2A', seed=40)


# 9 ─ « Il les entoure au stylo rouge. Et il écrit, à côté : Wow. »
class WowPaper(Scene):
    zoom = (1.08, 1.0)

    def static(self, cv):
        cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P('#E8E0C8'))
        rnd = random.Random(10)
        for _ in range(3000):
            circle(cv, rnd.uniform(-200, W + 200), rnd.uniform(-200, H + 200), rnd.uniform(0.6, 1.6), '#8A7A5A', 40)
        for row in range(14):
            y = 60 + row * 76
            for c in range(10):
                ch = rnd.choice('1111111223 ')
                label(cv, 200 + c * 110, y, ch, 40, color='#4A4A5A', font=FONT, box=False)

    def dyn(self, cv, t, d):
        col = '6EQUJ5'
        x = 1320
        for i, ch in enumerate(col):
            label(cv, x, 150 + i * 140, ch, 72, color='#2A2A3A', font=FONT, box=False)
        k = ease(t / max(d * 0.45, 0.1))
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - 110, 60, x + 110, 1010), -90, 359 * k)
        cv.drawPath(p, P('#D81E2E', 230, stroke=10))
        k2 = ease((t - d * 0.5) / max(d * 0.35, 0.1))
        if k2 > 0:
            cv.save(); cv.translate(1660, 560); cv.rotate(-12); cv.skew(-0.25, 0)
            f = skia.Font(FONT, 150)
            w = f.measureText('Wow!')
            cv.clipRect(skia.Rect.MakeXYWH(-w / 2 - 10, -170, (w + 20) * k2, 220))
            cv.drawString('Wow!', -w / 2, 0, f, P('#D81E2E', 240))
            cv.restore()


# 10 ─ « Depuis, on a pointé nos antennes vers ce coin du ciel, dans la constellation du Sagittaire, des dizaines de fois. »
class Sagittarius(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.st = stars(910, 300)

    def static(self, cv):
        night(cv, 11, '#02010A', '#0E0A2A', '#2A0E3A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        ribbons(cv, t, 12, 3, 260, 160, 70)
        pts = [(700, 380), (860, 300), (1040, 330), (1180, 260), (1240, 400), (1080, 470), (880, 470), (760, 520), (1100, 560), (1300, 520)]
        lines = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0), (6, 7), (5, 8), (8, 9), (4, 9)]
        k = ease(t / max(d * 0.6, 0.1))
        for i, (a, b) in enumerate(lines):
            if k * len(lines) > i:
                neon(cv, [pts[a], pts[b]], '#B98CFF', w=3, a=200, glow_w=10)
        for x, y in pts:
            sparkle(cv, x, y, 16, '#FFFFFF')
        label(cv, 1000, 200, 'SAGITTAIRE', 28, color='#B98CFF', font=FONT)
        for i in range(5):
            ang = -30 + 18 * ease(t / max(d * 0.8, 0.1)) + (i - 2) * 6
            dish(cv, 250 + i * 360, 1080, 190, ang + (i - 2) * 4, ['#3A2A6A', '#2A3A6A', '#4A2A5A', '#2A4A5A', '#3A2A6A'][i])


# 11 ─ « Silence. »
class Silence(Scene):
    zoom = (1.0, 1.05)

    def static(self, cv):
        cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P('#020106'))

    def dyn(self, cv, t, d):
        k = 0.5 + 0.5 * math.sin(t * 3)
        glow(cv, 1300, 300, 60, '#FFFFFF', 160 * k)
        circle(cv, 1300, 300, 4, '#FFFFFF', 255 * k)


# 12 ─ « Peut-être que c'était un nuage d'hydrogène, illuminé par une étoile. Peut-être. »
class Cloud(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        self.st = stars(912, 220)

    def static(self, cv):
        night(cv, 13, '#02010A', '#140630', '#2A0A30')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        flare = math.exp(-((t - d * 0.4) ** 2) / 0.5)
        for i in range(7):
            ofill(cv, pblob(900 + (i - 3) * 110, 520 + (i % 2) * 60, 220 - i * 10, seed=i, t=t), ['#5A0E5A', '#3A0E6A', '#6A1A5A'][i % 3], a=200, w=4)
        glow(cv, 900, 540, 700 * (0.4 + flare), '#FF4FD8', 200 * flare + 30)
        sx, sy = 1500, 300
        glow(cv, sx, sy, 160, '#BFE6FF', 220)
        ofill(cv, pcircle(sx, sy, 30), '#F4ECFF', ol=OLD)
        neon(cv, [(sx, sy), (sx - 500 * (0.5 + flare * 0.5), sy + 200 * (0.5 + flare * 0.5))], '#BFE6FF', w=6, a=180 * (0.3 + flare))


# 13 ─ « Ou peut-être qu'une seule fois, quelqu'un, quelque part, nous a dit bonjour. »
class Hello(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = stars(913, 260)

    def static(self, cv):
        night(cv, 14, '#05020F', '#1A0A3A', '#3A0E4A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        ribbons(cv, t, 15, 3, 140, 140, 90)
        px, py, R = 1400, 1350, 700
        glow(cv, px, py - R, 400, '#2DE2C6', 120)
        ofill(cv, pcircle(px, py, R), '#1A4A4A', ol=OLD)
        for k in range(6):
            ofill(cv, pblob(px - 500 + k * 200, py - R + 120 + (k % 2) * 40, 60, seed=k), '#2A6A5A', ol=OLD, w=4)
        # créature lointaine aux longs membres « nouilles » qui fait coucou
        cx, cy = 1360, 640
        noodle(cv, [(cx, cy + 40), (cx - 10, cy - 60), (cx, cy - 160)], '#8AD8C8', w=34)
        ofill(cv, poval(cx, cy - 230, 70, 90), '#8AD8C8', ol=OLD)
        for k in (-1, 1):
            ofill(cv, pcircle(cx + k * 28, cy - 240, 22), '#FFFFFF', ol=OLD, w=4)
            circle(cv, cx + k * 28, cy - 238, 9, OLD)
        wv = 30 * math.sin(t * 5)
        noodle(cv, [(cx + 20, cy - 120), (cx + 120, cy - 180), (cx + 150 + wv, cy - 300)], '#8AD8C8', w=20)
        glow(cv, cx + 150 + wv, cy - 310, 70, '#FFE680', 200)
        noodle(cv, [(cx - 20, cy - 120), (cx - 90, cy - 60), (cx - 120, cy)], '#8AD8C8', w=20)
        neon(cv, [(cx + 150 + wv - j * 40, cy - 310 - j * 6 + 8 * math.sin(j + t * 4)) for j in range(16)], '#FFE680', w=3, a=150)


# 14 ─ « Et qu'on n'a jamais su lui répondre. »
class Reply(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = stars(914, 320)

    def static(self, cv):
        night(cv, 16, '#02010A', '#0E0A2A', '#24082E')
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, 900); p.quadTo(960, 800, W + 400, 900); p.lineTo(W + 400, H + 400); p.close()
        ofill(cv, p, '#0E0620', ol=OLD)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        ribbons(cv, t, 17, 3, 120, 120, 70)
        hero(cv, t, 960, 820, 170, eyes='open')
        k = ease(t / max(d, 0.1))
        lx, ly = 1185, 800 - 560 * k
        noodle(cv, [(1080, 1060), (1170, 980), (1185, 830)], '#7AC8D8', w=26)
        ofill(cv, pcircle(1185, 820, 22), '#7AC8D8', ol=OLD)
        glow(cv, lx, ly, 90, '#FFE680', 240)
        circle(cv, lx, ly, 12, '#FFF6D0')


SEGMENTS = [
    (Arrive, "Le quinze août mille neuf cent soixante-dix-sept, quelque chose dans l'espace nous a envoyé un signal."),
    (Seconds, "Pendant soixante-douze secondes. Et puis plus rien. Jamais."),
    (BigEar, "Cette nuit-là, dans l'Ohio, un radiotélescope géant écoute le ciel."),
    (Noise, "Il n'entend presque que du bruit. Le souffle du cosmos."),
    (Surge, "Et soudain, un signal surgit. Puissant. Étroit."),
    (Hydrogen, "Pile sur la fréquence de l'hydrogène, l'élément le plus répandu de l'univers."),
    (Dial, "Exactement là où des scientifiques avaient prédit qu'une civilisation choisirait d'émettre."),
    (Desk, "Quelques jours plus tard, l'astronome Jerry Ehman découvre les chiffres sur le papier."),
    (WowPaper, "Il les entoure au stylo rouge. Et il écrit, à côté : Wow."),
    (Sagittarius, "Depuis, on a pointé nos antennes vers ce coin du ciel, dans la constellation du Sagittaire, des dizaines de fois."),
    (Silence, "Silence."),
    (Cloud, "Peut-être que c'était un nuage d'hydrogène, illuminé par une étoile. Peut-être."),
    (Hello, "Ou peut-être qu'une seule fois, quelqu'un, quelque part, nous a dit bonjour."),
    (Reply, "Et qu'on n'a jamais su lui répondre."),
]

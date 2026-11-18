"""« Tu n'aurais jamais dû exister » : 22 scènes illustrées (même moteur que etoiles/)."""
import math, random
import skia
from lib import *

FONT = None  # injecté par render.py


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


def ground(cv, y, color, ctrl=None, rim=None):
    ctrl = ctrl if ctrl is not None else y - 120
    p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, y); p.quadTo(W / 2, ctrl, W + 400, y); p.lineTo(W + 400, H + 400); p.close()
    cv.drawPath(p, P(color))
    if rim:
        q = skia.Path(); q.moveTo(-400, y); q.quadTo(W / 2, ctrl, W + 400, y)
        cv.drawPath(q, P(rim, 200, stroke=6))


def comet(cv, x, y, s, t, ph, color='#ffffff', a=255):
    """Petite « comète » nageuse : tête ovale + queue ondulante."""
    p = skia.Path(); p.moveTo(x - 10 * s, y)
    n = 6
    for k in range(1, n + 1):
        xx = x - 10 * s - k * 14 * s
        yy = y + math.sin(t * 14 + ph + k * 0.9) * 7 * s * (k / n)
        p.lineTo(xx, yy)
    cv.drawPath(p, P(color, a * 0.8, stroke=3.2 * s))
    oval(cv, x, y, 13 * s, 9 * s, color, a)


def walker(cv, x, y, s, t, shirt, pants, hair, skin, facing=1, walk=True):
    """Personnage de profil qui marche. (x,y) = pieds."""
    sw = math.sin(t * 7) if walk else 0
    cv.save(); cv.translate(x, y); cv.scale(facing, 1)
    for k, c in ((1, mix(pants, '#000000', 0.25)), (-1, pants)):
        cv.save(); cv.translate(0, -0.95 * s); cv.rotate(22 * sw * k)
        rrect(cv, -0.1 * s, 0, 0.2 * s, 0.95 * s, 0.1 * s, c)
        rrect(cv, -0.1 * s, 0.85 * s, 0.32 * s, 0.13 * s, 0.06 * s, '#1A1030')
        cv.restore()
    cv.save(); cv.translate(0, -1.65 * s); cv.rotate(-25 * sw)
    rrect(cv, -0.08 * s, 0, 0.16 * s, 0.75 * s, 0.08 * s, mix(shirt, '#000000', 0.2))
    cv.restore()
    rrect(cv, -0.26 * s, -1.78 * s, 0.52 * s, 0.92 * s, 0.22 * s, shirt)
    cv.save(); cv.translate(0, -1.65 * s); cv.rotate(25 * sw)
    rrect(cv, -0.08 * s, 0, 0.16 * s, 0.75 * s, 0.08 * s, shirt)
    circle(cv, 0, 0.78 * s, 0.08 * s, skin)
    cv.restore()
    circle(cv, 0.04 * s, -2.08 * s, 0.26 * s, skin)
    circle(cv, -0.04 * s, -2.16 * s, 0.25 * s, hair)
    circle(cv, 0.2 * s, -2.08 * s, 0.035 * s, '#1A1030')
    cv.restore()


def phone_face(cv, x, y, s, t, shirt='#E8475F', hair='#2A1A14', skin='#8A5236'):
    """Personnage assis de profil, penché sur son téléphone."""
    rrect(cv, x - 0.4 * s, y - 1.2 * s, 0.85 * s, 1.0 * s, 0.35 * s, shirt)
    circle(cv, x + 0.18 * s, y - 1.45 * s, 0.33 * s, skin)
    circle(cv, x + 0.08 * s, y - 1.58 * s, 0.33 * s, hair)
    glow(cv, x + 0.7 * s, y - 1.2 * s, 1.1 * s, '#5AD7FF', 150 + 25 * math.sin(t * 9))
    rrect(cv, x + 0.55 * s, y - 1.35 * s, 0.2 * s, 0.33 * s, 0.04 * s, '#111133')
    rrect(cv, x + 0.57 * s, y - 1.32 * s, 0.16 * s, 0.27 * s, 0.03 * s, '#9BEFFF')
    rrect(cv, x + 0.3 * s, y - 1.05 * s, 0.4 * s, 0.14 * s, 0.07 * s, skin)
    circle(cv, x + 0.38 * s, y - 1.48 * s, 0.035 * s, '#ffffff')


# 1 ─ « Tu n'aurais jamais dû exister. »
class Fade(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = Stars(200, 201)

    def static(self, cv):
        bg_lin(cv, '#05031A', '#1E0A40')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        poly(cv, [(860, -50), (1060, -50), (1260, 940), (660, 940)], '#B9A8FF', 40, blur=30)
        oval(cv, 960, 935, 300, 40, '#B9A8FF', 70, blur=10)
        flick = 1 if (int(t * 12) % 5) else 0
        a = 255 * (0.5 + 0.5 * flick) * (0.8 + 0.2 * math.sin(t * 3))
        off = 0 if flick else 14
        cv.saveLayerAlpha(None, int(a))
        person_back(cv, 960 + off, 930, 140, shirt='#7A6BFF', pants='#3A2E8F', hair='#2A1A44', skin='#C9B8FF')
        cv.restore()
        if not flick:
            cv.saveLayerAlpha(None, 110)
            person_back(cv, 960 - 22, 930, 140, shirt='#FF4F81', pants='#FF4F81', hair='#FF4F81', skin='#FF4F81')
            cv.restore()


# 2 ─ « Pour que tu sois là, tes parents devaient se rencontrer. »
class Meet(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        bg_lin(cv, '#120A44', '#4A1E7A')
        rnd = random.Random(3)
        for i in range(14):
            x = -100 + i * 160; h = rnd.uniform(220, 520)
            rrect(cv, x, 860 - h, 150, h + 40, 8, '#25145E')
            for wy in range(int(880 - h), 840, 46):
                for wx in (x + 25, x + 85):
                    if rnd.random() > 0.5:
                        cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 32, 24), P('#FFD34A', 190))
        cv.drawRect(skia.Rect.MakeXYWH(-400, 860, W + 800, 600), P('#1A0E40'))
        cv.drawRect(skia.Rect.MakeXYWH(-400, 860, W + 800, 10), P('#7A5BFF', 160))
        for lx in (420, 1500):
            rrect(cv, lx - 8, 440, 16, 430, 8, '#3A2A7A')
            rrect(cv, lx - 50, 420, 100, 30, 15, '#3A2A7A')
            glow(cv, lx, 470, 300, '#FFD27A', 120)
            poly(cv, [(lx - 40, 450), (lx + 40, 450), (lx + 180, 870), (lx - 180, 870)], '#FFD27A', 35, blur=10)

    def dyn(self, cv, t, d):
        k = ease(t / max(d, 0.1))
        xa = 300 + 480 * k
        xb = 1620 - 480 * k
        walker(cv, xa, 870, 120, t, '#FF4F81', '#2B2A7A', '#3A1E14', '#C98058', 1)
        walker(cv, xb, 870, 112, t + 0.5, '#2DE2C6', '#5A2A8A', '#E0A030', '#F2A97E', -1)
        g = max(0, 1 - (xb - xa) / 900)
        glow(cv, (xa + xb) / 2, 640, 120 + 300 * g, '#FFD27A', 220 * g)


# 3 ─ « Au bon endroit. Au bon moment. »
class Clock(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        bg_lin(cv, '#FFC23B', '#FF8A3D')
        for i in range(0, W, 46):
            cv.drawLine(i, 0, i, H, P('#ffffff', 40, stroke=10))

    def dyn(self, cv, t, d):
        cx, cy, R = 1240, 540, 360
        circle(cv, cx + 18, cy + 22, R + 40, '#C85A1F')
        circle(cv, cx, cy, R + 40, '#3C2ABF')
        circle(cv, cx, cy, R, '#FFF6E8')
        for i in range(12):
            a = i / 12 * 2 * math.pi
            r1 = R - 50 if i % 3 else R - 75
            cv.drawLine(cx + math.cos(a) * r1, cy + math.sin(a) * r1, cx + math.cos(a) * (R - 20), cy + math.sin(a) * (R - 20), P('#3C2ABF', 255, stroke=14 if i % 3 == 0 else 7))
        spin = 1 - ease_out(t / max(d * 0.8, 0.1))
        am = -90 + 360 * 5 * (1 - spin) + 60
        ah = -90 + 360 * 0.6 * (1 - spin) + 110
        for ang, ln, w, c in ((ah, R * 0.5, 22, '#1A1030'), (am, R * 0.78, 14, '#1A1030')):
            r = math.radians(ang)
            cv.drawLine(cx, cy, cx + math.cos(r) * ln, cy + math.sin(r) * ln, P(c, 255, stroke=w))
        circle(cv, cx, cy, 26, '#FF4F81')
        # épingle de carte « ICI »
        px, py = 520, 420 + 20 * math.sin(t * 3)
        oval(cv, px, 790, 90, 22, '#C85A1F', 160)
        p = skia.Path(); p.moveTo(px, py + 300); p.lineTo(px - 105, py + 60); p.lineTo(px + 105, py + 60); p.close()
        cv.drawPath(p, P('#FF4F81'))
        circle(cv, px, py, 130, '#FF4F81')
        circle(cv, px, py, 55, '#FFF6E8')
        label(cv, px, 900, 'ICI · MAINTENANT', 28, color='#3C2ABF', font=FONT)


# 4 ─ « Puis, parmi des centaines de millions de spermatozoïdes, »
class Race(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        rnd = random.Random(41)
        self.c = [(rnd.uniform(-300, W), rnd.uniform(-60, H + 60), rnd.uniform(0.6, 1.6), rnd.uniform(140, 320), rnd.uniform(0, 6)) for _ in range(220)]

    def static(self, cv):
        bg_lin(cv, '#5A0F6E', '#D9407F', angle_h=True)
        for i in range(9):
            blob(cv, 200 + i * 220, 140 + (i % 3) * 360, 190, '#FF7AB6', 40, seed=i, blur=40)

    def dyn(self, cv, t, d):
        for x, y, s, sp, ph in sorted(self.c, key=lambda c: c[2]):
            xx = (x + t * sp * s) % (W + 400) - 200
            yy = y + 18 * math.sin(t * 2 + ph)
            comet(cv, xx, yy, s, t, ph, '#FFF4FA', 150 + 70 * (s - 0.6))
        label(cv, 960, 980, '250 000 000 CONCURRENTS', 30, font=FONT)


# 5 ─ « un seul devait arriver le premier. »
class Egg(Scene):
    zoom = (1.0, 1.15)
    pan = (0, 0, -80, 0)

    def __init__(self):
        rnd = random.Random(51)
        self.c = [(rnd.uniform(-600, -100), rnd.uniform(200, 880), rnd.uniform(0.8, 1.3), rnd.uniform(0, 6)) for _ in range(60)]

    def static(self, cv):
        bg_lin(cv, '#3A0A5E', '#B02F7A', angle_h=True)

    def dyn(self, cv, t, d):
        ex, ey = 1450, 540
        glow(cv, ex, ey, 650, '#FFD27A', 160)
        circle(cv, ex, ey, 330, '#FFB0C8', 120)
        circle(cv, ex, ey, 290, '#FFE0B8')
        circle(cv, ex, ey, 290, '#ffffff', 200, stroke=8)
        circle(cv, ex - 60, ey - 50, 90, '#FFC9A0', 200)
        k = ease_out(t / max(d * 0.7, 0.1))
        for x, y, s, ph in self.c:
            comet(cv, x + 900 * k + 40 * math.sin(ph + t), y, s, t, ph, '#FFF4FA', 140)
        hx = 300 + (ex - 290 - 300 - 10) * k
        glow(cv, hx, ey, 120, '#ffffff', 220)
        comet(cv, hx, ey, 2.2, t, 0, '#ffffff')
        if k > 0.97:
            glow(cv, ex - 290, ey, 400, '#ffffff', 200)


# 6 ─ « Un autre, et ce ne serait pas toi. »
class Others(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        bg_lin(cv, '#0D0838', '#2E1260')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#170C42'))

    def dyn(self, cv, t, d):
        looks = [('#2DE2C6', '#E0A030'), ('#FFD34A', '#1A1030'), ('#FF4F81', '#3A1E14'), ('#7A6BFF', '#C0C0D0'), ('#3FC46A', '#8A3A10')]
        sel = int(t * 3) % 5
        for i, (sh, hr) in enumerate(looks):
            x = 360 + i * 300
            on = i == 2
            a = 255 if on else 110
            cv.saveLayerAlpha(None, a)
            person_back(cv, x, 900, 120 if on else 105, shirt=sh, pants='#2B2A7A', hair=hr, skin=['#F2A97E', '#C98058', '#8A5236'][i % 3], rim='#FFE6A0' if on else None)
            cv.restore()
            if not on:
                label(cv, x, 560, '?', 110, font=FONT, box=False, a=120 + 120 * (i == sel))
        glow(cv, 960, 700, 300, '#FFE6A0', 70)


# 7 ─ « Maintenant, remonte. »
class Rewind(Scene):
    zoom = (1.0, 1.25)
    shake = 0.3

    def static(self, cv):
        bg_rad(cv, 960, 540, 1100, '#5A1EAA', '#0A0428')

    def dyn(self, cv, t, d):
        for i in range(14):
            k = ((i / 14) + t * 0.6) % 1.0
            r = 40 + (1 - k) * 1300
            circle(cv, 960, 540, r, ['#FF4F81', '#5AD7FF', '#FFD34A'][i % 3], 200 * k, stroke=10 + 30 * (1 - k))
        for k in range(30):
            y = (k * 37 + t * 900) % H
            cv.drawRect(skia.Rect.MakeXYWH(-200, y, W + 400, 3), P('#ffffff', 25))
        # icône retour rapide
        for dx in (0, 150):
            poly(cv, [(1420 + dx, 860), (1560 + dx, 780), (1560 + dx, 940)], '#ffffff', 200)
        label(cv, 300, 180, '◀◀ REW', 30, font=FONT) if False else label(cv, 300, 180, 'REW', 30, font=FONT)


# 8 ─ « Tes parents. Leurs parents. »
class Parents(Scene):
    zoom = (1.0, 1.1)
    pan = (0, 60, 0, -60)

    def static(self, cv):
        bg_lin(cv, '#1A0A4E', '#5A1E8A')

    def dyn(self, cv, t, d):
        lv = [(960, 930, 1)]
        cols = ['#FF4F81', '#2DE2C6', '#FFD34A', '#7A6BFF', '#3FC46A', '#FF8A3D']
        k = t / max(d, 0.1)
        levels = [[(960, 900)]]
        for L in range(1, 4):
            prev = levels[-1]
            gap = 760 / (2 ** (L - 1))
            nxt = []
            for (x, y) in prev:
                nxt += [(x - gap / 2, y - 230), (x + gap / 2, y - 230)]
            levels.append(nxt)
        for L in range(1, 4):
            if k < (L - 1) * 0.28:
                break
            e = ease_out((k - (L - 1) * 0.28) / 0.25)
            for j, (x, y) in enumerate(levels[L]):
                px, py = levels[L - 1][j // 2]
                xx, yy = px + (x - px) * e, py + (y - py) * e
                cv.drawLine(px, py, xx, yy, P('#ffffff', 120, stroke=5))
        for L in range(0, 4):
            if L and k < (L - 1) * 0.28:
                break
            e = 1 if L == 0 else ease_out((k - (L - 1) * 0.28) / 0.25)
            for j, (x, y) in enumerate(levels[L]):
                if L:
                    px, py = levels[L - 1][j // 2]
                    x, y = px + (x - px) * e, py + (y - py) * e
                r = [80, 64, 50, 38][L]
                circle(cv, x, y, r + 8, '#ffffff', 200)
                circle(cv, x, y, r, cols[(j + L) % 6])
                circle(cv, x, y - r * 0.15, r * 0.38, '#1A1030', 220)
                oval(cv, x, y + r * 0.55, r * 0.6, r * 0.35, '#1A1030', 220)


# 9 ─ « Il y a trente générations, sur le papier, ça fait plus d'un milliard d'ancêtres. »
class Billion(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        rnd = random.Random(91)
        self.d = [(rnd.uniform(0, 6.28), rnd.random() ** 0.6, rnd.uniform(2, 5), rnd.choice(['#FF4F81', '#2DE2C6', '#FFD34A', '#7A6BFF', '#ffffff'])) for _ in range(2600)]
        self.st = Stars(100, 92)

    def static(self, cv):
        bg_lin(cv, '#07042A', '#2A0A50')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 160)
        k = ease_out(t / max(d * 0.85, 0.1))
        glow(cv, 960, 540, 700 * k + 100, '#7A4BFF', 140)
        for ang, u, r, c in self.d:
            if u > k * 1.05:
                continue
            rr = u * 1100 * (0.3 + 0.7 * k)
            circle(cv, 960 + rr * math.cos(ang + t * 0.05), 540 + rr * 0.62 * math.sin(ang + t * 0.05), r, c, 220)
        g = min(30, int(1 + 29 * k))
        n = 2 ** g
        label(cv, 960, 160, f'GÉNÉRATION {g}', 28, font=FONT)
        label(cv, 960, 980, f'{n:,} ANCÊTRES'.replace(',', ' '), 36, font=FONT)


# 10 ─ « Pas un seul n'est mort avant d'avoir eu un enfant. »
class Torch(Scene):
    zoom = (1.0, 1.1)
    pan = (80, 0, -80, 0)

    def __init__(self):
        self.st = Stars(150, 101)

    def static(self, cv):
        bg_lin(cv, '#0E0838', '#5A1E6E')
        ground(cv, 900, '#1C0C3E', 860, '#C77DFF')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        # file d'ancêtres qui se perd à l'horizon, chacun tient la lumière
        for i in range(12):
            s = 120 * (0.82 ** i)
            x = 1500 - sum(150 * (0.82 ** j) for j in range(i))
            y = 890 - (1 - 0.82 ** i) * 120
            cols = ['#FF4F81', '#2DE2C6', '#FFD34A', '#7A6BFF', '#FF8A3D', '#3FC46A']
            person_back(cv, x, y, s, shirt=cols[i % 6], pants='#2B2A7A', hair='#2A1A14', skin=['#F2A97E', '#C98058', '#8A5236'][i % 3])
        # flamme qui passe de main en main
        k = (t * 0.9) % 1
        i = int(k * 11)
        x = 1500 - sum(150 * (0.82 ** j) for j in range(i)) - 50 * (0.82 ** i)
        y = 890 - (1 - 0.82 ** i) * 120 - 240 * (0.82 ** i)
        glow(cv, x, y, 140, '#FFC24A', 255)
        blob(cv, x, y, 22, '#FFF3C4', seed=3, t=t * 4)


# 11 ─ « Ni à cause de la peste. »
class Plague(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        bg_lin(cv, '#06180F', '#1F3A1C')
        circle(cv, 1600, 230, 110, '#D8F5B0', 230)
        glow(cv, 1600, 230, 300, '#B8F07A', 90)
        rnd = random.Random(111)
        for i in range(10):
            x = -100 + i * 220; h = rnd.uniform(260, 460)
            poly(cv, [(x, 900), (x, 900 - h), (x + 100, 900 - h - 110), (x + 200, 900 - h), (x + 200, 900)], '#0B200F')
            cv.drawRect(skia.Rect.MakeXYWH(x + 80, 900 - h + 40, 36, 46), P('#E0C060', 150))
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#04100A'))

    def dyn(self, cv, t, d):
        for i in range(8):
            x = (i * 300 + t * 70) % (W + 600) - 300
            blob(cv, x, 860 + (i % 2) * 60, 260, '#7AF07A', 50, seed=i, t=t, blur=40)
        # masque de médecin de peste
        cx, cy = 760, 520
        cv.save(); cv.translate(cx, cy); cv.rotate(4 * math.sin(t * 1.5))
        poly(cv, [(-150, -230), (150, -230), (230, -110), (-230, -110)], '#14110E')
        rrect(cv, -330, -130, 660, 70, 35, '#14110E')
        circle(cv, 0, 30, 200, '#E8DCC0')
        p = skia.Path(); p.moveTo(90, -10); p.cubicTo(380, 20, 520, 170, 560, 300); p.cubicTo(420, 220, 250, 190, 90, 160); p.close()
        cv.drawPath(p, P('#D8C8A0'))
        p2 = skia.Path(); p2.moveTo(90, 120); p2.cubicTo(250, 170, 420, 220, 560, 300)
        cv.drawPath(p2, P('#A89870', 255, stroke=8))
        for ex in (-70, 70):
            circle(cv, ex, 10, 62, '#14110E')
            circle(cv, ex, 10, 46, '#9CF07A', 210)
            circle(cv, ex - 14, -4, 12, '#ffffff', 200)
        cv.restore()
        label(cv, 760, 1000, 'PESTE NOIRE · 1347', 28, font=FONT)


# 12 ─ « Ni à cause des guerres. »
class War(Scene):
    zoom = (1.0, 1.12)
    shake = 0.35

    def static(self, cv):
        bg_lin(cv, '#5A0A14', '#FF5A2E')
        ground(cv, 860, '#2A0610', 800)

    def dyn(self, cv, t, d):
        for i in range(5):
            k = ((t * 0.7 + i * 0.37) % 1.0)
            x = 200 + i * 380
            r = 80 + 220 * ease_out(k)
            blob(cv, x, 820 - r * 0.5, r, '#FFB13B', 255 * (1 - k), seed=i, t=t)
            blob(cv, x, 820 - r * 0.5, r * 0.6, '#FFF0B0', 255 * (1 - k), seed=i + 7, t=t)
            blob(cv, x + 40, 700 - r, r * 0.9, '#3A0A1A', 160 * k, seed=i + 20, t=t, blur=10)
        # casques et barbelés
        for i in range(6):
            x = 140 + i * 330
            oval(cv, x, 905, 90, 60, '#1A0408')
            rrect(cv, x - 130, 900, 260, 22, 11, '#1A0408')
        for k in range(40):
            x = k * 52 - 60
            cv.drawLine(x, 990, x + 52, 970 + (k % 2) * 40, P('#1A0408', 255, stroke=5))
        for k in range(0, 40, 2):
            cv.drawLine(k * 52 - 72, 960, k * 52 - 48, 1000, P('#1A0408', 255, stroke=4))


# 13 ─ « Ni à cause de la famine. »
class Famine(Scene):
    zoom = (1.15, 1.0)

    def static(self, cv):
        bg_lin(cv, '#FFE07A', '#FF9A3C')
        glow(cv, 1450, 300, 600, '#FFFFFF', 160)
        circle(cv, 1450, 300, 160, '#FFF6D0')
        ground(cv, 700, '#C8762E', 660)
        rnd = random.Random(131)
        for i in range(70):
            x, y = rnd.uniform(-200, W + 200), rnd.uniform(720, H + 100)
            pts = [(x, y)]
            for k in range(3):
                x += rnd.uniform(-90, 90); y += rnd.uniform(-20, 40); pts.append((x, y))
            p = skia.Path(); p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            cv.drawPath(p, P('#8A4A1A', 200, stroke=5))
        # arbre mort
        tp = P('#4A2410', 255, stroke=34)
        cv.drawLine(420, 760, 440, 420, tp)
        for (x0, y0, x1, y1, w) in [(440, 520, 300, 380, 20), (436, 470, 580, 330, 18), (300, 380, 250, 300, 10), (580, 330, 640, 270, 10), (440, 430, 470, 300, 14)]:
            cv.drawLine(x0, y0, x1, y1, P('#4A2410', 255, stroke=w))

    def dyn(self, cv, t, d):
        for i in range(6):
            y = 200 + i * 120
            p = skia.Path(); p.moveTo(-100, y)
            for x in range(-100, W + 200, 60):
                p.lineTo(x, y + 12 * math.sin(x * 0.01 + t * 3 + i))
            cv.drawPath(p, P('#ffffff', 25, stroke=8))
        for i in range(3):
            bx = (900 + i * 200 + t * 60) % W
            by = 250 + i * 50 + 20 * math.sin(t * 2 + i)
            wv = 14 * math.sin(t * 6 + i)
            path = skia.Path(); path.moveTo(bx - 30, by - wv); path.quadTo(bx - 12, by - 6, bx, by); path.quadTo(bx + 12, by - 6, bx + 30, by - wv)
            cv.drawPath(path, P('#4A2410', 255, stroke=6))


# 14 ─ « Remonte encore. Des humains qui ont survécu aux glaciations. »
class Ice(Scene):
    zoom = (1.0, 1.1)
    pan = (60, 0, -60, 0)

    def __init__(self):
        rnd = random.Random(141)
        self.sn = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 7), rnd.uniform(40, 120)) for _ in range(220)]

    def static(self, cv):
        bg_lin(cv, '#6A7BE8', '#DCE6FF')
        for i, (x, h) in enumerate([(200, 380), (650, 480), (1150, 420), (1650, 520)]):
            poly(cv, [(x - 380, 820), (x, 820 - h), (x + 380, 820)], '#A9B6F0')
            poly(cv, [(x - 120, 820 - h + 110), (x, 820 - h), (x + 120, 820 - h + 110), (x + 40, 820 - h + 80), (x - 30, 820 - h + 120)], '#ffffff')
        ground(cv, 820, '#F4F7FF', 760)
        # mammouth
        mx, my = 1380, 800
        oval(cv, mx, my - 160, 230, 150, '#7A4A3A')
        circle(cv, mx + 200, my - 220, 100, '#7A4A3A')
        for lx in (-150, -60, 70, 150):
            rrect(cv, mx + lx - 30, my - 80, 60, 140, 26, '#5E382C')
        p = skia.Path(); p.moveTo(mx + 280, my - 210); p.quadTo(mx + 330, my - 60, mx + 280, my + 20)
        cv.drawPath(p, P('#5E382C', 255, stroke=36))
        p2 = skia.Path(); p2.moveTo(mx + 250, my - 160); p2.quadTo(mx + 400, my - 120, mx + 380, my - 250)
        cv.drawPath(p2, P('#FFF6E0', 255, stroke=20))
        circle(cv, mx + 230, my - 240, 10, '#1A1030')

    def dyn(self, cv, t, d):
        # feu de camp + humains
        fx, fy = 560, 860
        glow(cv, fx, fy - 60, 320, '#FF8A3D', 200)
        for i in range(3):
            blob(cv, fx, fy - 50 - i * 25, 70 - i * 18, ['#FF5A1F', '#FFB13B', '#FFF0B0'][i], seed=i, t=t * 5, wob=0.35)
        person_back(cv, fx - 200, 900, 90, shirt='#8A5A3A', pants='#5E382C', hair='#2A1A14', skin='#C98058')
        person_back(cv, fx + 210, 905, 80, shirt='#A06A44', pants='#5E382C', hair='#3A1E14', skin='#8A5236')
        for x, y, r, sp in self.sn:
            xx = (x + 30 * math.sin(t + y)) % W
            yy = (y + t * sp) % H
            circle(cv, xx, yy, r, '#ffffff', 220)
        label(cv, 960, 140, '−20 000 ANS · ÈRE GLACIAIRE', 28, color='#2A2A7A', font=FONT)


# 15 ─ « Des créatures qui sont sorties de l'océan. »
class Ocean(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        bg_lin(cv, '#FF8A9A', '#FFD08A')
        circle(cv, 1500, 380, 150, '#FFF0C0')
        glow(cv, 1500, 380, 380, '#FFFFFF', 120)

    def dyn(self, cv, t, d):
        # vagues
        for i, c in enumerate(['#2A6BD6', '#3A8BE8', '#5AD7FF']):
            p = skia.Path(); p.moveTo(-400, H + 400)
            base = 600 + i * 45
            p.lineTo(-400, base)
            for x in range(-400, W + 440, 40):
                p.lineTo(x, base + 12 * math.sin(x * 0.012 + t * (2 + i)))
            p.lineTo(W + 400, H + 400); p.close()
            cv.drawPath(p, P(c, 235))
        sw = 25 * math.sin(t * 2)
        p = skia.Path(); p.moveTo(600, H + 400); p.lineTo(600, 1000); p.quadTo(1000, 800 + sw * 0.3, W + 400, 740); p.lineTo(W + 400, H + 400); p.close()
        cv.drawPath(p, P('#F2C27A'))
        q = skia.Path(); q.moveTo(600, 1000); q.quadTo(1000, 800 + sw * 0.3, W + 400, 740)
        cv.drawPath(q, P('#ffffff', 200, stroke=12))
        # créature (poisson à pattes) qui rampe
        k = ease(t / max(d, 0.1))
        x, y = 980 + 260 * k, 830 + 30 * k
        cv.save(); cv.translate(x, y); cv.rotate(8)
        p = skia.Path(); p.moveTo(-200, 0); p.quadTo(-80, -70, 80, -40); p.quadTo(150, -20, 150, 10); p.quadTo(60, 50, -80, 30); p.close()
        cv.drawPath(p, P('#3FA88A'))
        poly(cv, [(-200, 0), (-280, -50 + 10 * math.sin(t * 6)), (-270, 50 + 10 * math.sin(t * 6))], '#2E8A70')
        for lx, ph in ((-20, 0), (70, 3)):
            sw = 18 * math.sin(t * 6 + ph)
            cv.drawLine(lx, 20, lx + 30 + sw, 70, P('#2E8A70', 255, stroke=16))
        circle(cv, 110, -22, 10, '#1A1030')
        for i in range(5):
            circle(cv, -120 + i * 40, -20, 9, '#7FE0C0', 200)
        cv.restore()
        label(cv, 1300, 1000, '−375 000 000 ANS', 28, color='#7A2A4A', font=FONT)


# 16 ─ « Une seule cellule, il y a quatre milliards d'années. »
class Cell(Scene):
    zoom = (1.0, 1.25)

    def __init__(self):
        rnd = random.Random(161)
        self.b = [(rnd.uniform(0, W), rnd.uniform(0, 1), rnd.uniform(3, 12), rnd.uniform(0.2, 0.6)) for _ in range(90)]

    def static(self, cv):
        bg_lin(cv, '#1A0A5E', '#0A3A5A')
        for i in range(6):
            poly(cv, [(i * 360 - 60, H + 50), (i * 360 + 40, 840), (i * 360 + 120, 840), (i * 360 + 220, H + 50)], '#0A1A3A')

    def dyn(self, cv, t, d):
        for x, ph, r, sp in self.b:
            k = (ph + t * sp) % 1
            circle(cv, x + 20 * math.sin(k * 10), H - k * (H + 100), r, '#9BEFFF', 120, stroke=2)
        cx, cy = 960, 520
        p = 1 + 0.04 * math.sin(t * 3)
        glow(cv, cx, cy, 520 * p, '#2DE2C6', 150)
        blob(cv, cx, cy, 300 * p, '#3FE0B0', 200, seed=5, t=t * 2, wob=0.12)
        blob(cv, cx, cy, 270 * p, '#7AF0C8', 160, seed=6, t=t * 2, wob=0.1)
        blob(cv, cx + 50, cy - 20, 100, '#B04BFF', 230, seed=8, t=t * 3, wob=0.2)
        circle(cv, cx + 30, cy - 40, 40, '#FFD6FF', 200)
        rnd = random.Random(7)
        for i in range(14):
            a = rnd.uniform(0, 6.28) + t * 0.4
            rr = rnd.uniform(120, 220)
            circle(cv, cx + rr * math.cos(a), cy + rr * math.sin(a), rnd.uniform(8, 18), '#FFFFFF', 160)
        label(cv, 960, 980, '−4 000 000 000 ANS', 32, font=FONT)


# 17 ─ « Une chaîne de survie jamais brisée. Pas une seule fois. »
class Chain(Scene):
    zoom = (1.0, 1.08)

    def __init__(self):
        self.st = Stars(160, 171)

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#3A0E5E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        sp = 160
        off = (t * 220) % sp
        for i in range(-2, 16):
            x = i * sp - off
            y = 540 + 30 * math.sin((x + t * 220) * 0.004)
            horiz = i % 2 == 0
            col = '#FFD34A'
            glow(cv, x, y, 140, '#FFC24A', 70)
            if horiz:
                cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 110, y - 55, 220, 110), 55, 55), P(col, 255, stroke=28))
                cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 104, y - 49, 208, 98), 49, 49), P('#FFF3C4', 200, stroke=6))
            else:
                rrect(cv, x - 100, y - 14, 200, 28, 14, '#E0A020')
        label(cv, 960, 900, '4 000 000 000 ANS · 0 RUPTURE', 30, font=FONT)


# 18 ─ « Et au bout de cette chaîne, il y a toi. Sur ton téléphone. »
class EndChain(Scene):
    zoom = (1.18, 1.0)

    def static(self, cv):
        bg_lin(cv, '#1E0E5A', '#0C0630')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 860, W + 800, 600), P('#140A3A'))
        rrect(cv, 1150, 160, 520, 380, 20, '#3B2A8F')
        rrect(cv, 1170, 180, 480, 340, 10, '#0E1250')
        circle(cv, 1530, 270, 50, '#E8E4FF')
        circle(cv, 1555, 255, 50, '#0E1250')
        # lit
        rrect(cv, 520, 700, 900, 180, 40, '#3A98C4')
        rrect(cv, 520, 660, 220, 80, 40, '#E8E4FF')

    def dyn(self, cv, t, d):
        # la chaîne lumineuse arrive jusqu'au personnage
        for i in range(10):
            x = -100 + i * 85
            y = 640 + 8 * math.sin(t * 2 + i)
            a = 255 * min(1, (t * 2.5 - i * 0.15) if t * 2.5 > i * 0.15 else 0)
            if i % 2 == 0:
                cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 55, y - 28, 110, 56), 28, 28), P('#FFD34A', a, stroke=14))
            else:
                rrect(cv, x - 50, y - 7, 100, 14, 7, '#E0A020', a)
        phone_face(cv, 960, 760, 190, t)


# 19 ─ « En train de te dire que tu n'es pas assez. »
class Doubt(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        rnd = random.Random(191)
        self.rain = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(600, 1100)) for _ in range(140)]

    def static(self, cv):
        bg_lin(cv, '#14103A', '#2A1A5A')

    def dyn(self, cv, t, d):
        for x, y, sp in self.rain:
            yy = (y + t * sp) % (H + 100) - 50
            cv.drawLine(x, yy, x - 8, yy + 40, P('#7A8BFF', 90, stroke=3))
        # petites bulles de doute qui gravitent
        words = ['PAS ASSEZ', 'TROP TARD', 'NUL', 'PERSONNE', 'POURQUOI MOI']
        for i, wd in enumerate(words):
            a = t * 0.5 + i * 1.256
            x, y = 960 + 640 * math.cos(a), 520 + 330 * math.sin(a)
            label(cv, x, y, wd, 24, color='#9A9AD0', a=180, font=FONT)
        glow(cv, 960, 700, 420, '#5AD7FF', 80)
        # personnage assis, recroquevillé
        cx, cy = 960, 900
        oval(cv, cx, cy + 10, 260, 30, '#000000', 80)
        rrect(cv, cx - 150, cy - 230, 300, 240, 110, '#3C4CC8')
        rrect(cv, cx - 120, cy - 300, 240, 160, 80, '#2B2A7A')
        circle(cv, cx, cy - 330, 95, '#C98058')
        circle(cv, cx, cy - 360, 95, '#2A1A14')
        rrect(cv, cx - 170, cy - 220, 340, 70, 35, '#C98058')


# 20 ─ « Tu es le résultat de quatre milliards d'années de victoires. »
class Evolution(Scene):
    zoom = (1.0, 1.08)

    def __init__(self):
        self.st = Stars(150, 201)

    def static(self, cv):
        bg_lin(cv, '#0E0838', '#4A1270')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        y = 860
        cv.drawLine(120, y, 1800, y, P('#6B4BFF', 200, stroke=8))
        k = ease(t / max(d * 0.9, 0.1))
        cv.drawLine(120, y, 120 + 1680 * k, y, P('#FFD34A', 255, stroke=10))
        glow(cv, 120 + 1680 * k, y, 100, '#FFD34A', 255)
        stages = [0.06, 0.3, 0.55, 0.78, 0.97]
        for i, u in enumerate(stages):
            x = 120 + 1680 * u
            on = k >= u - 0.03
            a = 255 if on else 70
            cv.saveLayerAlpha(None, a)
            if i == 0:
                blob(cv, x, y - 90, 60, '#3FE0B0', seed=5, t=t); circle(cv, x + 10, y - 95, 20, '#B04BFF')
            elif i == 1:
                oval(cv, x, y - 90, 90, 45, '#3FA88A'); poly(cv, [(x - 90, y - 90), (x - 140, y - 130), (x - 140, y - 50)], '#2E8A70'); circle(cv, x + 55, y - 100, 8, '#1A1030')
            elif i == 2:
                oval(cv, x, y - 80, 80, 45, '#8A5A3A'); circle(cv, x + 80, y - 105, 34, '#8A5A3A')
                for lx in (-50, 40):
                    rrect(cv, x + lx, y - 50, 18, 50, 9, '#6A4028')
            elif i == 3:
                walker(cv, x, y, 70, 0, '#8A5A3A', '#5E382C', '#2A1A14', '#C98058', 1, walk=False)
            else:
                person_back(cv, x, y, 85, shirt='#FF4F81', pants='#2B2A7A', rim='#FFE6A0' if on else None)
            cv.restore()
            if on:
                glow(cv, x, y, 60, '#FFD34A', 200)
                circle(cv, x, y, 16, '#FFD34A')
            else:
                circle(cv, x, y, 12, '#4A3A8A')
        label(cv, 960, 160, f'{int(4_000_000_000 * k):,} ANS DE VICTOIRES'.replace(',', ' '), 32, font=FONT)


# 21 ─ « Alors arrête de douter. »
class Rise(Scene):
    zoom = (1.15, 1.0)

    def static(self, cv):
        bg_rad(cv, 960, 640, 1100, '#FF7AC6', '#2A0A5E')

    def dyn(self, cv, t, d):
        cv.save(); cv.translate(960, 640); cv.rotate(t * 10)
        for i in range(18):
            cv.rotate(20)
            poly(cv, [(0, 0), (1500, -110), (1500, 110)], '#FFE6A0', 45)
        cv.restore()
        glow(cv, 960, 640, 500, '#FFF3C4', 200)
        e = ease_out(t / 0.8)
        ground(cv, 960, '#2A0A4E', 930, '#FFC9F0')
        person_back(cv, 960, 950, 120 + 40 * e, shirt='#FF4F81', pants='#2B2A7A', rim='#FFFFFF')
        # éclats des bulles de doute qui volent en morceaux
        rnd = random.Random(2)
        for i in range(30):
            a = rnd.uniform(0, 6.28)
            r = 200 + 900 * ease_out(t / max(d, 0.1)) * rnd.uniform(0.4, 1)
            rrect(cv, 960 + r * math.cos(a), 600 + r * math.sin(a), 22, 10, 4, '#9A9AD0', 200 * (1 - t / max(d, 0.1)))


# 22 ─ « Tu as déjà gagné la course la plus improbable de l'univers. »
class Finish(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        self.st = Stars(240, 221, colors=('#ffffff', '#FFD6F5', '#BFE6FF'))
        rnd = random.Random(222)
        self.conf = [(rnd.uniform(0, W), rnd.uniform(-H, 0), rnd.uniform(150, 350), rnd.uniform(0, 360), rnd.choice(['#FF4F81', '#2DE2C6', '#FFD34A', '#7A6BFF', '#ffffff'])) for _ in range(160)]

    def static(self, cv):
        bg_lin(cv, '#120838', '#6A1E8A')
        glow(cv, 960, 620, 800, '#FF7AC6', 120)
        # route cosmique en perspective
        poly(cv, [(860, 560), (1060, 560), (1700, H + 200), (220, H + 200)], '#2A1260')
        for k in range(10):
            y0 = 560 + (k / 10) ** 2 * 700
            y1 = 560 + ((k + 0.5) / 10) ** 2 * 700
            w0, w1 = 4 + k * 3, 4 + (k + 0.5) * 3
            poly(cv, [(960 - w0, y0), (960 + w0, y0), (960 + w1, y1), (960 - w1, y1)], '#FFD34A', 200)
        cv.drawLine(860, 560, 220, H + 200, P('#C77DFF', 200, stroke=6))
        cv.drawLine(1060, 560, 1700, H + 200, P('#C77DFF', 200, stroke=6))
        # poteaux d'arrivée
        for x in (330, 1590):
            rrect(cv, x - 14, 300, 28, 700, 14, '#E8E4FF')
        # damier
        for i in range(32):
            for j in range(2):
                if (i + j) % 2 == 0:
                    cv.drawRect(skia.Rect.MakeXYWH(344 + i * 38.75, 300 + j * 38, 38.75, 38), P('#ffffff'))
                else:
                    cv.drawRect(skia.Rect.MakeXYWH(344 + i * 38.75, 300 + j * 38, 38.75, 38), P('#1A1030'))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        k = ease_out(t / max(d * 0.5, 0.1))
        # ruban d'arrivée qui se brise
        if k < 1:
            cv.drawLine(344, 800, 1576, 800, P('#FF4F81', 255, stroke=14))
        else:
            sag = min(1, (t - d * 0.5) * 2)
            cv.drawLine(344, 800, 344 + 200 * (1 - sag * 0.3), 820 + 160 * sag, P('#FF4F81', 255, stroke=14))
            cv.drawLine(1576, 800, 1576 - 200 * (1 - sag * 0.3), 820 + 160 * sag, P('#FF4F81', 255, stroke=14))
        walker(cv, 960, 1040 - 170 * k, 160 - 40 * k, t * 1.4, '#FF4F81', '#2B2A7A', '#2A1A14', '#C98058', 1, walk=k < 1)
        glow(cv, 960, 760, 300, '#FFE6A0', 120)
        for x, y, sp, rot, c in self.conf:
            yy = y + t * sp
            if yy < -20:
                continue
            cv.save(); cv.translate(x + 30 * math.sin(t * 2 + rot), yy % (H + 40)); cv.rotate(rot + t * 200)
            cv.drawRect(skia.Rect.MakeXYWH(-9, -5, 18, 10), P(c))
            cv.restore()


SEGMENTS = [
    (Fade, "Tu n'aurais jamais dû exister."),
    (Meet, "Pour que tu sois là, tes parents devaient se rencontrer."),
    (Clock, "Au bon endroit. Au bon moment."),
    (Race, "Puis, parmi des centaines de millions de spermatozoïdes,"),
    (Egg, "un seul devait arriver le premier."),
    (Others, "Un autre, et ce ne serait pas toi."),
    (Rewind, "Maintenant, remonte."),
    (Parents, "Tes parents. Leurs parents."),
    (Billion, "Il y a trente générations, sur le papier, ça fait plus d'un milliard d'ancêtres."),
    (Torch, "Pas un seul n'est mort avant d'avoir eu un enfant."),
    (Plague, "Ni à cause de la peste."),
    (War, "Ni à cause des guerres."),
    (Famine, "Ni à cause de la famine."),
    (Ice, "Remonte encore. Des humains qui ont survécu aux glaciations."),
    (Ocean, "Des créatures qui sont sorties de l'océan."),
    (Cell, "Une seule cellule, il y a quatre milliards d'années."),
    (Chain, "Une chaîne de survie jamais brisée. Pas une seule fois."),
    (EndChain, "Et au bout de cette chaîne, il y a toi. Sur ton téléphone."),
    (Doubt, "En train de te dire que tu n'es pas assez."),
    (Evolution, "Tu es le résultat de quatre milliards d'années de victoires."),
    (Rise, "Alors arrête de douter."),
    (Finish, "Tu as déjà gagné la course la plus improbable de l'univers."),
]

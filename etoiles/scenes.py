"""Les 21 scènes illustrées. Chaque scène : static(cv) dessiné une fois, dyn(cv, t, d) à chaque frame.
t = temps local (s), d = durée de la scène. Caméra : zoom/pan lents gérés par render.py."""
import math, random
import skia
from lib import *

FONT = None  # injecté par render.py


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)  # px0, py0, px1, py1
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


# 1 ─ « Regarde ta main. »
class Hand(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = Stars(220, 11)
        rnd = random.Random(3)
        self.dust = [(rnd.uniform(-260, 260), rnd.uniform(0, 1), rnd.uniform(2, 6), rnd.uniform(0.6, 1.6)) for _ in range(70)]

    def static(self, cv):
        bg_lin(cv, '#0B0A2E', '#3B1170')
        glow(cv, 960, 1100, 900, '#B23CFF', 120)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        rise = ease_out(t / 1.2)
        y0 = 1180 - 330 * rise
        cv.save()
        cv.translate(1300, y0)
        cv.rotate(-8)
        glow(cv, 0, -300, 520, '#FFC46B', 110)
        sk, sh, rim = '#F2A97E', '#D9845B', '#FFE3A1'
        # avant-bras + paume
        rrect(cv, -150, -40, 300, 700, 120, sh)
        rrect(cv, -190, -380, 380, 430, 150, sk)
        fingers = [(-150, -560, 78, 300, -6), (-62, -640, 82, 360, -2), (30, -650, 82, 370, 2), (118, -590, 76, 320, 7)]
        for fx, fy, fw, fh, rot in fingers:
            cv.save(); cv.rotate(rot)
            rrect(cv, fx, fy, fw, fh, fw / 2, sk)
            rrect(cv, fx + fw * 0.62, fy + 20, fw * 0.25, fh - 60, fw * 0.12, rim, 120)
            cv.restore()
        cv.save(); cv.translate(-170, -190); cv.rotate(-48)
        rrect(cv, -45, -230, 92, 250, 46, sk)
        cv.restore()
        rrect(cv, 120, -360, 50, 380, 25, rim, 90)
        oval(cv, -10, -170, 120, 70, sh, 120)
        cv.restore()
        # poussière d'étoile qui s'échappe de la main
        for dx, ph, r, sp in self.dust:
            k = (ph + t * sp * 0.25) % 1.0
            x = 1300 + dx + 40 * math.sin(k * 9 + dx)
            y = y0 - 600 - k * 700
            a = 255 * math.sin(k * math.pi)
            glow(cv, x, y, r * 4, '#FFD46B', a * 0.5)
            circle(cv, x, y, r, '#FFF3C4', a)


# 2 ─ « Chaque atome de calcium dans tes os, »
class Bones(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        bg_lin(cv, '#2A0B55', '#7A1D8C')
        for i in range(0, W, 60):
            cv.drawLine(i, 0, i, H, P('#ffffff', 14, stroke=2))
        for j in range(0, H, 60):
            cv.drawLine(0, j, W, j, P('#ffffff', 14, stroke=2))

    def dyn(self, cv, t, d):
        pulse = 0.75 + 0.25 * math.sin(t * 5)
        cv.save(); cv.translate(560, 1150); cv.rotate(12)
        bone = '#D8F6FF'
        # silhouette de chair translucide
        rrect(cv, -250, -1050, 500, 1150, 230, '#7FE7FF', 40)
        for bx in (-90, 40):
            rrect(cv, bx - 10, -600, 70, 640, 35, '#7FE7FF', 120 * pulse, blur=18)
            rrect(cv, bx, -600, 50, 640, 25, bone)
        rrect(cv, -150, -760, 300, 170, 70, bone)
        for fx, rot, ln in [(-105, -16, 3), (-40, -5, 3), (25, 5, 3), (90, 15, 3), (-150, -52, 2)]:
            cv.save(); cv.translate(fx + 20, -740); cv.rotate(rot)
            yy = -20
            for k in range(ln):
                h = 125 - k * 22
                circle(cv, 0, yy, 24, bone)
                rrect(cv, -17, yy - h, 34, h, 17, '#7FE7FF', 110 * pulse, blur=12)
                rrect(cv, -17, yy - h, 34, h, 17, bone)
                yy -= h + 14
            cv.restore()
        cv.restore()
        rnd = random.Random(5)
        for i in range(9):
            ang = t * (0.5 + 0.1 * i) + i * 0.7
            cx, cy = 1350 + 330 * math.cos(ang + i), 540 + 260 * math.sin(ang * 1.3 + i)
            glow(cv, cx, cy, 70, '#FFE66B', 140)
            circle(cv, cx, cy, 30, '#FFE66B')
            circle(cv, cx, cy, 30, '#ffffff', 90, stroke=4)
            for e in range(2):
                a2 = t * 3 + e * 3.14 + i
                circle(cv, cx + 60 * math.cos(a2), cy + 22 * math.sin(a2), 7, '#ffffff')
            oval(cv, cx, cy, 60, 22, '#ffffff', 70, stroke=2)
        label(cv, 1350, 900, 'Ca  · CALCIUM', 30, font=FONT)


# 3 ─ « chaque atome de fer dans ton sang, »
class Blood(Scene):
    zoom = (1.05, 1.12)

    def __init__(self):
        rnd = random.Random(7)
        self.cells = [(rnd.uniform(0, W + 400), rnd.uniform(250, 830), rnd.uniform(45, 85), rnd.uniform(-40, 40), rnd.uniform(250, 520)) for _ in range(26)]

    def static(self, cv):
        bg_lin(cv, '#3A0618', '#14020B')
        cv.drawRect(skia.Rect.MakeXYWH(-300, 200, W + 600, 680), P(shader=lin(0, 200, 0, 880, ['#7A0F2A', '#C0213F', '#7A0F2A'])))
        cv.drawRect(skia.Rect.MakeXYWH(-300, 170, W + 600, 50), P('#E8536B'))
        cv.drawRect(skia.Rect.MakeXYWH(-300, 860, W + 600, 50), P('#E8536B'))

    def dyn(self, cv, t, d):
        for x, y, r, rot, sp in sorted(self.cells, key=lambda c: c[2]):
            xx = (x + t * sp) % (W + 400) - 200
            yy = y + 14 * math.sin(t * 2 + x)
            cv.save(); cv.translate(xx, yy); cv.rotate(rot + t * 20)
            oval(cv, 0, 6, r, r * 0.62, '#5A0716', 160)
            oval(cv, 0, 0, r, r * 0.62, '#F0384F')
            oval(cv, 0, 0, r * 0.55, r * 0.3, '#B5132E')
            oval(cv, -r * 0.35, -r * 0.3, r * 0.25, r * 0.1, '#FF9AA6', 160)
            cv.restore()
        for i in range(4):
            xx = (300 + i * 520 + t * 380) % (W + 300) - 150
            yy = 330 + 360 * ((i * 37) % 3) / 2
            glow(cv, xx, yy, 90, '#FF9A2E', 200)
            circle(cv, xx, yy, 26, '#FFB65C')
            label(cv, xx, yy - 60, 'Fe', 28, font=FONT, box=False)


# 4 ─ « a été fabriqué au cœur d'une étoile. »
class StarCore(Scene):
    zoom = (1.0, 1.22)
    pan = (0, 0, -120, 0)

    def static(self, cv):
        bg_lin(cv, '#1A0730', '#3C0B2E')
        glow(cv, 1300, 540, 1100, '#FF7A00', 160)

    def dyn(self, cv, t, d):
        cx, cy = 1300, 540
        cv.save(); cv.translate(cx, cy); cv.rotate(t * 8)
        for i in range(24):
            cv.rotate(15)
            ln = 700 + 80 * math.sin(t * 3 + i)
            cv.drawLine(560, 0, ln, 0, P('#FFC23B', 90, stroke=10))
        cv.restore()
        circle(cv, cx, cy, 560, '#FF6A1F')
        circle(cv, cx, cy, 540, '#FF8A1F')
        for i in range(14):
            a = i * 0.9 + t * 0.15
            blob(cv, cx + 380 * math.cos(a) * (0.4 + 0.5 * ((i * 7) % 5) / 5), cy + 380 * math.sin(a) * (0.4 + 0.5 * ((i * 3) % 5) / 5), 60 + (i % 4) * 18, '#FFB13B', 200, seed=i, t=t)
        circle(cv, cx, cy, 300 + 12 * math.sin(t * 4), '#FFD34A')
        circle(cv, cx, cy, 170 + 10 * math.sin(t * 6), '#FFF4B8')
        glow(cv, cx, cy, 260, '#ffffff', 220)
        # éruption
        k = (t * 0.5) % 1
        cv.save(); cv.translate(cx, cy); cv.rotate(-130)
        path = skia.Path(); path.moveTo(540, -60); path.cubicTo(760 + 80 * k, -120, 780 + 80 * k, 120, 540, 60)
        cv.drawPath(path, P('#FFD34A', 220, stroke=26))
        cv.restore()
        label(cv, 560, 880, 'CŒUR STELLAIRE · 15 000 000 °C', 28, font=FONT)


# 5 ─ « Il y a des milliards d'années, bien avant la Terre, »
class Void(Scene):
    zoom = (1.0, 1.06)

    def __init__(self):
        self.st = Stars(140, 21, rmax=2.2)
        rnd = random.Random(2)
        self.dust = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(80, 260)) for _ in range(22)]

    def static(self, cv):
        bg_rad(cv, 960, 540, 1100, '#1C1C2E', '#030308')
        for x, y, r in self.dust:
            circle(cv, x, y, r, '#8C8CB0', 10, blur=40)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200, drift=(-6, 0))
        # petite galaxie lointaine
        cv.save(); cv.translate(1500, 260); cv.rotate(-25)
        oval(cv, 0, 0, 90, 26, '#C9C6FF', 120, blur=10)
        oval(cv, 0, 0, 30, 12, '#ffffff', 220, blur=4)
        cv.restore()
        years = int(9_000_000_000 - 2_000_000 * t * 60)
        s = f'IL Y A {years:,} ANS'.replace(',', ' ')
        label(cv, 960, 860, s, 30, font=FONT)


# 6 ─ « une étoile géante brûlait seule dans le noir. »
class Giant(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = Stars(160, 31, rmax=2.4)

    def static(self, cv):
        bg_lin(cv, '#020208', '#080A1C')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        cx, cy = 1340, 420
        p = 1 + 0.03 * math.sin(t * 2.4)
        glow(cv, cx, cy, 620 * p, '#3D8BFF', 160)
        glow(cv, cx, cy, 380 * p, '#9CD2FF', 200)
        circle(cv, cx, cy, 200 * p, '#BFE6FF')
        circle(cv, cx, cy, 160 * p, '#ffffff')
        for i in range(4):
            cv.save(); cv.translate(cx, cy); cv.rotate(i * 45 + t * 4)
            cv.drawLine(-520, 0, 520, 0, P('#CFEAFF', 70, stroke=5))
            cv.restore()
        label(cv, cx, cy + 340, 'ÉTOILE GÉANTE · 20 × LE SOLEIL', 26, font=FONT)


# 7 ─ « Pendant des millions d'années, elle a écrasé de l'hydrogène »
class Fusion(Scene):
    zoom = (1.0, 1.15)
    shake = 0.0

    def __init__(self):
        rnd = random.Random(9)
        self.h = [(rnd.uniform(0, 6.28), rnd.uniform(0, 1), rnd.uniform(0.5, 1.0)) for _ in range(26)]

    def static(self, cv):
        bg_rad(cv, 960, 540, 1000, '#FF8A1F', '#7A1208')
        for i in range(8):
            circle(cv, 960, 540, 140 + i * 120, '#FFD34A', 30, stroke=24)

    def dyn(self, cv, t, d):
        cx, cy = 960, 540
        for ang, ph, sp in self.h:
            k = (ph + t * sp * 0.7) % 1.0
            r = 900 * (1 - k) + 40
            x, y = cx + r * math.cos(ang + k), cy + r * math.sin(ang + k)
            circle(cv, x, y, 26, '#FFFFFF')
            circle(cv, x, y, 26, '#5AD7FF', 255, stroke=6)
            if r < 140:
                glow(cv, cx, cy, 300, '#ffffff', 200 * (1 - r / 140))
        flash = 0.5 + 0.5 * math.sin(t * 9)
        glow(cv, cx, cy, 240, '#FFF6C9', 160 + 80 * flash)
        circle(cv, cx, cy, 70, '#FFF6C9')
        label(cv, 470, 220, 'H + H = He', 34, font=FONT)


# 8 ─ « pour créer du carbone, de l'oxygène, et du fer. »
class Layers(Scene):
    zoom = (1.0, 1.08)

    def __init__(self):
        self.st = Stars(120, 41)

    def static(self, cv):
        bg_lin(cv, '#14063A', '#3A0D59')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 160)
        cx, cy = 1150, 560
        rings = [(470, '#FF9A3C', 'H'), (390, '#FF5E7E', 'He'), (310, '#C84BFF', 'C'), (230, '#4F7BFF', 'O'), (150, '#2DE2C6', 'Si'), (80, '#B7C3D6', 'Fe')]
        glow(cv, cx, cy, 700, '#FF9A3C', 120)
        cv.save(); cv.translate(cx, cy); cv.rotate(-20 + 6 * math.sin(t * 0.6))
        for r, col, _ in rings:
            circle(cv, 0, 0, r, col)
        # coupe : un quart retiré pour montrer les couches
        for i, (r, col, _) in enumerate(rings):
            path = skia.Path(); path.moveTo(0, 0); path.arcTo(skia.Rect.MakeLTRB(-r, -r, r, r), -90, 90, False); path.close()
            cv.drawPath(path, P(mix(col, '#000000', 0.25)))
        cv.restore()
        for i, (r, col, name) in enumerate(rings):
            if name in ('C', 'O', 'Fe'):
                yy = 260 + i * 110
                cv.drawLine(cx - r * 0.8, cy - r * 0.3, 480, yy - 10, P('#ffffff', 160, stroke=2))
                label(cv, 420, yy, name, 32, font=FONT)


# 9 ─ « Puis elle est morte. »
class Dying(Scene):
    zoom = (1.0, 1.25)

    def __init__(self):
        self.st = Stars(90, 51, rmax=1.8)

    def static(self, cv):
        bg_lin(cv, '#000000', '#09030C')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 110)
        k = ease(t / max(d, 0.1))
        r = 330 * (1 - 0.65 * k)
        jx, jy = 6 * math.sin(t * 61) * k, 6 * math.cos(t * 53) * k
        col = mix('#FF6A3C', '#5A1630', k)
        glow(cv, 960 + jx, 540 + jy, r * 2.2, '#FF4A2E', 140 * (1 - k * 0.6))
        circle(cv, 960 + jx, 540 + jy, r, col)
        circle(cv, 960 + jx - r * 0.25, 540 + jy - r * 0.25, r * 0.5, mix(col, '#FFFFFF', 0.15), 120)


# 10 ─ « Elle a explosé dans une supernova si violente »
class Supernova(Scene):
    zoom = (1.0, 1.12)
    shake = 0.45

    def __init__(self):
        rnd = random.Random(61)
        self.rays = [(rnd.uniform(0, 360), rnd.uniform(0.6, 1.0), rnd.uniform(3, 9)) for _ in range(60)]
        self.bl = [(rnd.uniform(0, 6.28), rnd.uniform(0.3, 1.0), rnd.uniform(60, 150), i) for i, _ in enumerate(range(22))]
        self.st = Stars(150, 62)

    def static(self, cv):
        bg_lin(cv, '#050414', '#120A2E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        cx, cy = 960, 540
        e = ease_out(t / 1.6)
        for ang, ln, w in self.rays:
            cv.save(); cv.translate(cx, cy); cv.rotate(ang)
            r0 = 200 + 600 * e * ln
            cv.drawLine(r0, 0, r0 + 140 * ln, 0, P('#FFE6A8', 220, stroke=w))
            cv.restore()
        glow(cv, cx, cy, 1200 * e + 200, '#FF7A1F', 150)
        circle(cv, cx, cy, 120 + 720 * e, '#FFB13B', 120 * (1 - e) + 30, stroke=18)
        for ang, ln, r, i in self.bl:
            dd = 120 + 420 * e * ln
            blob(cv, cx + dd * math.cos(ang), cy + dd * math.sin(ang), r * (0.6 + 0.6 * e), ['#FF5A1F', '#FF9A2E', '#FFD34A'][i % 3], 235, seed=i, t=t)
        blob(cv, cx, cy, 260 + 60 * e, '#FFE07A', 255, seed=99, t=t)
        circle(cv, cx, cy, 160, '#FFFBE6')
        glow(cv, cx, cy, 380, '#ffffff', 230 * (1 - e * 0.5))
        if t < 0.18:
            cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P('#ffffff', 255 * (1 - t / 0.18)))
        label(cv, 960, 990, 'SUPERNOVA', 30, font=FONT)


# 11 ─ « qu'elle a illuminé toute sa galaxie. »
class Galaxy(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        rnd = random.Random(71)
        self.p = []
        for arm in range(2):
            for k in range(900):
                u = rnd.random() ** 0.7
                th = arm * math.pi + u * 3.6 * math.pi / 1.4 + rnd.gauss(0, 0.25)
                r = 30 + u * 560 + rnd.gauss(0, 18)
                self.p.append((r, th, rnd.uniform(1.2, 3.6), rnd.choice(['#ffffff', '#C8B8FF', '#8FD3FF', '#FFC9F0'])))
        self.st = Stars(150, 72, rmax=2)

    def static(self, cv):
        bg_lin(cv, '#0B0628', '#2B0C4E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 160)
        cx, cy = 960, 540
        glow(cv, cx, cy, 650, '#7B4BFF', 120)
        cv.save(); cv.translate(cx, cy); cv.scale(1, 0.62); cv.rotate(t * 6)
        for r, th, s, col in self.p:
            circle(cv, r * math.cos(th), r * math.sin(th), s, col, 210)
        cv.restore()
        glow(cv, cx, cy, 200, '#FFE6B0', 255)
        # l'explosion illumine la galaxie
        fx, fy = cx + 330, cy - 120
        k = 0.5 + 0.5 * math.sin(t * 7)
        glow(cv, fx, fy, 520, '#FFD27A', 120 + 60 * k)
        glow(cv, fx, fy, 120, '#ffffff', 255)
        cv.drawLine(fx - 160, fy, fx + 160, fy, P('#ffffff', 200, stroke=4))
        cv.drawLine(fx, fy - 160, fx, fy + 160, P('#ffffff', 200, stroke=4))
        label(cv, 470, 900, 'SA GALAXIE · 100 000 000 000 ÉTOILES', 26, font=FONT)


# 12 ─ « Ses cendres ont dérivé dans le vide pendant une éternité. »
class Nebula(Scene):
    zoom = (1.0, 1.1)
    pan = (60, 0, -60, 0)

    def __init__(self):
        rnd = random.Random(81)
        self.b = [(rnd.uniform(-200, W + 200), rnd.uniform(-100, H + 100), rnd.uniform(160, 420), rnd.choice(['#FF3FA4', '#7A3CFF', '#2DE2E6', '#FF8A3D', '#B13CFF']), rnd.uniform(-30, 30), i) for i in range(26)]
        self.st = Stars(200, 82)

    def static(self, cv):
        bg_lin(cv, '#0A0420', '#1C0638')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 220)
        for x, y, r, col, sp, i in self.b:
            blob(cv, x + sp * t, y, r, col, 70, seed=i, t=t, blur=60)
        for x, y, r, col, sp, i in self.b[::3]:
            blob(cv, x + sp * t * 1.6, y + 40, r * 0.5, mix(col, '#ffffff', 0.3), 110, seed=i + 50, t=t, blur=14)
        rnd = random.Random(4)
        for k in range(80):
            x = (rnd.uniform(0, W) + t * rnd.uniform(20, 60)) % W
            y = rnd.uniform(0, H)
            circle(cv, x, y, rnd.uniform(1.5, 4), '#FFE0B0', 200)


# 13 ─ « Jusqu'à ce qu'elles forment un nuage, puis un soleil, »
class Disk(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        self.st = Stars(140, 91)
        rnd = random.Random(92)
        self.rocks = [(rnd.uniform(260, 820), rnd.uniform(0, 6.28), rnd.uniform(5, 16)) for _ in range(90)]

    def static(self, cv):
        bg_lin(cv, '#120838', '#3A0F5E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        cx, cy = 960, 560
        cv.save(); cv.translate(cx, cy); cv.scale(1, 0.33)
        for i, col in enumerate(['#FF8A3D', '#FFB54A', '#FF5E7E', '#C84BFF', '#FF8A3D']):
            circle(cv, 0, 0, 840 - i * 130, col, 90, stroke=70)
        for r, ph, s in self.rocks:
            a = ph + t * (300 / r)
            circle(cv, r * math.cos(a), r * math.sin(a), s * 2.2, '#FFD9A6', 220)
        cv.restore()
        sun = ease_out(t / max(d * 0.6, 0.1))
        glow(cv, cx, cy, 120 + 440 * sun, '#FFC24A', 220)
        circle(cv, cx, cy, 40 + 110 * sun, '#FFE680')
        circle(cv, cx, cy, 25 + 70 * sun, '#FFFBE0')
        # avant du disque (passe devant le soleil)
        cv.save(); cv.translate(cx, cy); cv.scale(1, 0.33)
        path = skia.Path(); path.addArc(skia.Rect.MakeLTRB(-600, -600, 600, 600), 10, 160)
        cv.drawPath(path, P('#FF8A3D', 140, stroke=60))
        cv.restore()


# 14 ─ « puis une petite planète bleue. »
class Earth(Scene):
    zoom = (1.0, 1.08)

    def __init__(self):
        self.st = Stars(200, 101)

    def static(self, cv):
        bg_lin(cv, '#06041C', '#2A0A50')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 220)
        cx, cy, R = 520, 1060, 760
        glow(cv, cx, cy, R * 1.25, '#4FD8FF', 150)
        circle(cv, cx, cy, R, '#1E63D6')
        cv.save()
        clip = skia.Path(); clip.addCircle(cx, cy, R)
        cv.clipPath(clip, doAntiAlias=True)
        circle(cv, cx + 120, cy + 120, R, '#174BB0')
        for i in range(7):
            x = cx - R + ((i * 330 + t * 60) % (2 * R + 400)) - 200
            blob(cv, x, cy - R * 0.55 + (i % 3) * 170, 150 + (i % 2) * 70, '#3FC46A', seed=i + 3)
            blob(cv, x + 40, cy - R * 0.55 + (i % 3) * 170 + 30, 90, '#2E9E55', seed=i + 9)
        for i in range(6):
            x = cx - R + ((i * 400 + t * 95) % (2 * R + 400)) - 200
            blob(cv, x, cy - R * 0.75 + (i % 3) * 160, 110, '#ffffff', 170, seed=i + 30, wob=0.4)
        cv.restore()
        circle(cv, cx, cy, R, '#9BEFFF', 200, stroke=10)
        # lune
        circle(cv, 1560, 260, 70, '#C7C3E8')
        circle(cv, 1585, 245, 18, '#A49FD0')
        circle(cv, 1540, 285, 12, '#A49FD0')
        label(cv, 1180, 330, 'TERRE', 28, font=FONT)


# 15 ─ « Puis toi. »
class Person(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = Stars(260, 111)

    def static(self, cv):
        bg_lin(cv, '#0E0A3A', '#5B1E7A')
        glow(cv, 960, 900, 900, '#FF7AC6', 110)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        path = skia.Path(); path.moveTo(-300, H + 300); path.lineTo(-300, 900); path.quadTo(960, 700, W + 300, 900); path.lineTo(W + 300, H + 300); path.close()
        cv.drawPath(path, P('#1D0F3E'))
        path2 = skia.Path(); path2.moveTo(-300, 905); path2.quadTo(960, 705, W + 300, 905)
        cv.drawPath(path2, P('#C77DFF', 200, stroke=6))
        glow(cv, 960, 560, 420, '#FFD27A', 90)
        person_back(cv, 960, 800, 150, shirt='#FF4F81', pants='#2B2A7A', rim='#FFE6A0')


# 16 ─ « Tu n'es pas juste dans l'univers. »
class Hill(Scene):
    zoom = (1.25, 1.0)

    def __init__(self):
        self.st = Stars(380, 121, rmax=2.6, colors=('#ffffff', '#FFD6F5', '#BFE6FF'))
        rnd = random.Random(122)
        self.band = [(rnd.uniform(-300, W + 300), rnd.gauss(0, 90), rnd.uniform(1, 3), rnd.choice(['#ffffff', '#FFC9F0', '#B9D5FF'])) for _ in range(1400)]

    def static(self, cv):
        bg_lin(cv, '#08062A', '#33106A')
        cv.save(); cv.translate(960, 420); cv.rotate(-18)
        oval(cv, 0, 0, 1400, 160, '#B04BFF', 70, blur=60)
        oval(cv, 0, 0, 1300, 70, '#FFC9F0', 70, blur=30)
        for x, y, r, c in self.band:
            circle(cv, x - 960, y, r, c, 200)
        cv.restore()

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        circle(cv, 960, 3300, 2350, '#140A33')
        circle(cv, 960, 3300, 2350, '#9B6BFF', 180, stroke=8)
        person_back(cv, 960, 955, 26, shirt='#FF4F81', pants='#2B2A7A', rim='#FFE6A0')


# 17 ─ « Tu es l'univers, qui a appris à se regarder. »
class Eye(Scene):
    zoom = (1.0, 1.15)

    def static(self, cv):
        bg_lin(cv, '#FF9A3C', '#E0477A')

    def dyn(self, cv, t, d):
        cx, cy = 960, 540
        blink = 1.0
        if t < 0.35:
            blink = ease(t / 0.35)
        oval(cv, cx, cy + 30, 860, 470, '#B33468')
        cv.save()
        clip = skia.Path(); clip.addOval(skia.Rect.MakeLTRB(cx - 780, cy - 400 * blink, cx + 780, cy + 400 * blink))
        cv.clipPath(clip, doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), P('#FFF4F0'))
        lx = 40 * math.sin(t * 0.8)
        circle(cv, cx + lx, cy, 360, '#2A0F5E')
        cv.save(); cv.translate(cx + lx, cy); cv.rotate(t * 25)
        for arm in range(3):
            for k in range(60):
                u = k / 60
                th = arm * 2.09 + u * 5.0
                r = 40 + u * 300
                circle(cv, r * math.cos(th), r * math.sin(th), 18 * (1 - u) + 4, ['#FFD34A', '#FF7AC6', '#5AD7FF'][arm], 200)
        cv.restore()
        circle(cv, cx + lx, cy, 130, '#05020F')
        glow(cv, cx + lx, cy, 160, '#FFD34A', 120)
        circle(cv, cx + lx - 110, cy - 120, 50, '#ffffff', 230)
        circle(cv, cx + lx + 90, cy + 110, 18, '#ffffff', 180)
        cv.restore()
        # paupière
        path = skia.Path(); path.addArc(skia.Rect.MakeLTRB(cx - 780, cy - 400 * blink, cx + 780, cy + 400 * blink), 200, 140)
        cv.drawPath(path, P('#7A1E4A', 255, stroke=34))


# 18 ─ « Une étoile est morte pour que tu puisses exister. »
class StarPerson(Scene):
    zoom = (1.0, 1.1)
    pan = (0, -60, 0, 40)

    def __init__(self):
        self.st = Stars(200, 131)
        rnd = random.Random(132)
        self.pp = [(rnd.uniform(-70, 70), rnd.uniform(0, 1), rnd.uniform(2, 6)) for _ in range(90)]

    def static(self, cv):
        bg_lin(cv, '#0C0630', '#4A1470')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        sx, sy = 960, 170
        glow(cv, sx, sy, 300, '#FFD27A', 220)
        circle(cv, sx, sy, 60, '#FFF3C4')
        # faisceau
        poly(cv, [(sx - 60, sy), (sx + 60, sy), (sx + 260, 1000), (sx - 260, 1000)], '#FFD27A', 60, blur=20)
        for dx, ph, r in self.pp:
            k = (ph + t * 0.45) % 1
            x = sx + dx * (1 + k * 3)
            y = sy + k * 760
            circle(cv, x, y, r, '#FFF0B8', 255 * math.sin(k * math.pi))
        rrect(cv, -200, 960, W + 400, 300, 0, '#1B0B3D')
        glow(cv, 960, 760, 380, '#FFC24A', 160 + 60 * math.sin(t * 3))
        person_back(cv, 960, 980, 115, shirt='#FFC24A', pants='#FF8A3D', hair='#7A3A10', skin='#FFD9A0', rim='#ffffff')


# 19 ─ « Alors arrête de vivre comme si tu ne comptais pas. »
class Couch(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        bg_lin(cv, '#2A1466', '#140A3A')
        # fenêtre + ville
        rrect(cv, 1180, 120, 560, 420, 20, '#3B2A8F')
        rrect(cv, 1200, 140, 520, 380, 10, '#0E1250')
        rnd = random.Random(5)
        for i in range(12):
            x = 1200 + i * 44
            h = rnd.uniform(80, 260)
            cv.drawRect(skia.Rect.MakeXYWH(x, 520 - h, 40, h), P('#24207A'))
            for wy in range(int(520 - h + 12), 510, 26):
                if rnd.random() > 0.55:
                    cv.drawRect(skia.Rect.MakeXYWH(x + 10, wy, 8, 10), P('#FFD34A', 200))
        cv.drawRect(skia.Rect.MakeXYWH(1455, 140, 10, 380), P('#3B2A8F'))
        # sol
        cv.drawRect(skia.Rect.MakeXYWH(-200, 860, W + 400, 400), P('#1A0E44'))
        # canapé
        rrect(cv, 220, 520, 1100, 260, 60, '#2F7FA8')
        rrect(cv, 180, 640, 1180, 240, 50, '#3A98C4')
        rrect(cv, 150, 580, 160, 300, 60, '#2F7FA8')
        rrect(cv, 1230, 580, 160, 300, 60, '#2F7FA8')
        # plante
        rrect(cv, 1500, 760, 120, 120, 20, '#C84B7A')
        for i in range(6):
            blob(cv, 1560 + (i - 2.5) * 40, 700 - (i % 3) * 50, 55, '#3FC46A', seed=i)

    def dyn(self, cv, t, d):
        # personnage avachi
        s = 1.0
        rrect(cv, 420, 640, 620, 130, 60, '#2B2A7A')          # jambes allongées
        rrect(cv, 980, 700, 150, 70, 30, '#1E1F5C')
        rrect(cv, 330, 520, 260, 220, 90, '#E8475F')          # torse
        circle(cv, 400, 470, 92, '#8A5236')                   # tête
        circle(cv, 395, 438, 95, '#2A1A14')
        circle(cv, 440, 480, 80, '#8A5236')
        # téléphone qui éclaire le visage
        glow(cv, 520, 470, 220, '#5AD7FF', 150 + 30 * math.sin(t * 11))
        rrect(cv, 500, 430, 50, 86, 10, '#111133')
        rrect(cv, 505, 436, 40, 74, 7, '#9BEFFF')
        rrect(cv, 470, 500, 70, 34, 17, '#8A5236')            # main
        circle(cv, 465, 470, 9, '#ffffff')
        # icônes qui défilent (scroll infini)
        for i in range(5):
            y = 380 - ((t * 140 + i * 70) % 350)
            rrect(cv, 600, y, 60, 46, 10, ['#FF4F81', '#FFD34A', '#5AD7FF'][i % 3], 200 * (1 - abs(y - 200) / 200) if 0 < y < 400 else 0)


# 20 ─ « Tu as mis treize milliards d'années à arriver ici. »
class Timeline(Scene):
    zoom = (1.0, 1.06)

    def __init__(self):
        self.st = Stars(160, 141, rmax=2)

    def static(self, cv):
        bg_lin(cv, '#07052A', '#250B4E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        y = 800
        x0, x1 = 220, 1700
        cv.drawLine(x0, y, x1, y, P('#6B4BFF', 200, stroke=8))
        pts = [(0.0, 'BIG BANG', '#ffffff'), (0.3, '1ères ÉTOILES', '#5AD7FF'), (0.55, 'SUPERNOVA', '#FF8A3D'), (0.75, 'SOLEIL', '#FFD34A'), (0.88, 'TERRE', '#3FC46A'), (1.0, 'TOI', '#FF4F81')]
        k = ease(t / max(d * 0.9, 0.1))
        xk = x0 + (x1 - x0) * k
        cv.drawLine(x0, y, xk, y, P('#FFD34A', 255, stroke=10))
        glow(cv, xk, y, 90, '#FFD34A', 255)
        for u, name, col in pts:
            x = x0 + (x1 - x0) * u
            on = k >= u - 0.01
            circle(cv, x, y, 22 if on else 14, col if on else '#4A3A8A')
            if on:
                glow(cv, x, y, 70, col, 160)
            label(cv, x, y + 80, name, 32, font=FONT, a=255 if on else 90, box=False)
        years = int(13_800_000_000 * k)
        label(cv, 960, 260, f'{years:,} ANS'.replace(',', ' '), 40, font=FONT)


# 21 ─ « Ne gâche pas ça. »
class Sunrise(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        bg_lin(cv, '#3A1C8A', '#FF8A5C')
        cloud(cv, 330, 300, 90, '#FFB0B8', 160, shade='#E07A9A')
        cloud(cv, 1580, 230, 110, '#FFB0B8', 160, shade='#E07A9A')

    def dyn(self, cv, t, d):
        cx = 960
        sy = 860 - 160 * ease_out(t / max(d, 0.1))
        cv.save(); cv.translate(cx, sy); cv.rotate(t * 6)
        for i in range(16):
            cv.rotate(22.5)
            poly(cv, [(0, 0), (1400, -90), (1400, 90)], '#FFE6A0', 40)
        cv.restore()
        glow(cv, cx, sy, 700, '#FFD34A', 200)
        circle(cv, cx, sy, 230, '#FFE680')
        circle(cv, cx, sy, 190, '#FFF6C9')
        path = skia.Path(); path.moveTo(-300, H + 300); path.lineTo(-300, 880); path.quadTo(500, 780, 960, 850); path.quadTo(1500, 920, W + 300, 820); path.lineTo(W + 300, H + 300); path.close()
        cv.drawPath(path, P('#3A1450'))
        path2 = skia.Path(); path2.moveTo(-300, 980); path2.quadTo(800, 900, W + 300, 1000); path2.lineTo(W + 300, H + 300); path2.lineTo(-300, H + 300); path2.close()
        cv.drawPath(path2, P('#24093A'))
        person_back(cv, 960, 858, 95, shirt='#FF4F81', pants='#2B2A7A', rim='#FFF3C4')
        for i in range(5):
            bx = (300 + i * 260 + t * 120) % (W + 200) - 100
            by = 380 + (i % 3) * 50 + 10 * math.sin(t * 4 + i)
            wv = 18 * math.sin(t * 10 + i)
            p = P('#3A1450', 255, stroke=6)
            path = skia.Path(); path.moveTo(bx - 26, by - wv); path.quadTo(bx - 10, by - 6, bx, by); path.quadTo(bx + 10, by - 6, bx + 26, by - wv)
            cv.drawPath(path, p)


SEGMENTS = [
    (Hand, "Regarde ta main."),
    (Bones, "Chaque atome de calcium dans tes os,"),
    (Blood, "chaque atome de fer dans ton sang,"),
    (StarCore, "a été fabriqué au cœur d'une étoile."),
    (Void, "Il y a des milliards d'années, bien avant la Terre,"),
    (Giant, "une étoile géante brûlait seule dans le noir."),
    (Fusion, "Pendant des millions d'années, elle a écrasé de l'hydrogène"),
    (Layers, "pour créer du carbone, de l'oxygène, et du fer."),
    (Dying, "Puis elle est morte."),
    (Supernova, "Elle a explosé dans une supernova si violente"),
    (Galaxy, "qu'elle a illuminé toute sa galaxie."),
    (Nebula, "Ses cendres ont dérivé dans le vide pendant une éternité."),
    (Disk, "Jusqu'à ce qu'elles forment un nuage, puis un soleil,"),
    (Earth, "puis une petite planète bleue."),
    (Person, "Puis toi."),
    (Hill, "Tu n'es pas juste dans l'univers."),
    (Eye, "Tu es l'univers, qui a appris à se regarder."),
    (StarPerson, "Une étoile est morte pour que tu puisses exister."),
    (Couch, "Alors arrête de vivre comme si tu ne comptais pas."),
    (Timeline, "Tu as mis treize milliards d'années à arriver ici."),
    (Sunrise, "Ne gâche pas ça."),
]

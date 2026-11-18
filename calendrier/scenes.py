"""« Si l'univers tenait en un an » : 18 plans riches, longs et toujours en mouvement (style v2)."""
import math, random
import skia
from lib import *
from kit import *

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7)

STAR_COLS = ('#ffffff', '#ffffff', '#FF5A7A', '#6FA8FF', '#FFB13B', '#B98CFF')


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


def nebula_bg(cv, top, bottom, blobs, seed=0):
    bg_lin(cv, top, bottom)
    rnd = random.Random(seed)
    for i in range(blobs):
        blob(cv, rnd.uniform(-100, W + 100), rnd.uniform(-100, H + 100), rnd.uniform(220, 520),
             rnd.choice(['#FF3FA4', '#7A3CFF', '#2DE2E6', '#B13CFF', '#3C5CFF']), 45, seed=i + seed, blur=70)


class RichStars:
    """Ciel étoilé coloré + étoiles scintillantes à 4 branches, comme dans les références."""
    def __init__(self, n=260, seed=1, big=22):
        self.st = Stars(n, seed, rmax=2.6, colors=STAR_COLS)
        rnd = random.Random(seed + 99)
        self.big = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(9, 20), rnd.choice(STAR_COLS[2:] + ('#ffffff',)), rnd.uniform(0, 6)) for _ in range(big)]

    def draw(self, cv, t, a=255):
        self.st.draw(cv, t, a)
        for x, y, r, c, ph in self.big:
            k = 0.6 + 0.4 * math.sin(t * 2.5 + ph)
            sparkle(cv, x, y, r * k, c, a * k)


def page_corner(cv, t, month, day, color, x=250, y=230, s=1.0, a=255):
    cv.save(); cv.translate(x, y); cv.rotate(-6 + 2 * math.sin(t * 1.5)); cv.scale(s, s)
    calendar_page(cv, 0, 0, 260, 300, month, day, color, FONT, a)
    cv.restore()


# 1 ─ « Imagine que toute l'histoire de l'univers tienne dans une seule année. »
class Calendar3D(Scene):
    zoom = (1.12, 1.0)
    months = ['JANV', 'FÉV', 'MARS', 'AVR', 'MAI', 'JUIN', 'JUIL', 'AOÛT', 'SEPT', 'OCT', 'NOV', 'DÉC']
    cols = ['#FF4F81', '#FF8A3D', '#FFD34A', '#B6FF3B', '#3FC46A', '#2DE2C6', '#2DB8FF', '#3C5CFF', '#7A4BFF', '#B13CFF', '#E83CFF', '#FF3FA4']

    def __init__(self):
        self.st = RichStars(240, 301)

    def static(self, cv):
        nebula_bg(cv, '#0A0630', '#2A0B5E', 10, 3)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        cam = Cam(yaw=0, pitch=-14, dist=3300, f=1500, cy=560)
        wire_plane(cv, cam, 560, 2600, 200, '#7A5BFF', 90, off=t * 120)
        R, w, h = 1000, 380, 440
        items = []
        for i in range(12):
            th = math.radians(i * 30 + t * 14)
            c = (R * math.sin(th), 0, R * math.cos(th))
            tx, tz = math.cos(th), -math.sin(th)
            def P3(u, v):
                return cam.p(c[0] + tx * u, c[1] + v, c[2] + tz * u)
            corners = [P3(-w / 2, -h / 2), P3(w / 2, -h / 2), P3(w / 2, h / 2), P3(-w / 2, h / 2)]
            depth = sum(q[2] for q in corners) / 4
            items.append((depth, i, corners, P3))
        for depth, i, corners, P3 in sorted(items, key=lambda it: -it[0]):
            front = depth < 0
            col = self.cols[i]
            a = 255 if front else 110
            poly(cv, [(q[0], q[1]) for q in corners], col, 60 if front else 25)
            band = [P3(-w / 2, -h / 2), P3(w / 2, -h / 2), P3(w / 2, -h / 2 + 90), P3(-w / 2, -h / 2 + 90)]
            poly(cv, [(q[0], q[1]) for q in band], col, 200 if front else 70)
            for k in range(8):
                u = -w / 2 + w * k / 7
                q0, q1 = P3(u, -h / 2 + 90), P3(u, h / 2)
                cv.drawLine(q0[0], q0[1], q1[0], q1[1], P(col, a * 0.55, stroke=1.6))
            for k in range(6):
                v = -h / 2 + 90 + (h - 90) * k / 5
                q0, q1 = P3(-w / 2, v), P3(w / 2, v)
                cv.drawLine(q0[0], q0[1], q1[0], q1[1], P(col, a * 0.55, stroke=1.6))
            neon(cv, [(q[0], q[1]) for q in corners + corners[:1]], col, w=4, a=a, glow_w=16)
            m = P3(0, -h / 2 + 62)
            f = skia.Font(FONT, 58 * m[3])
            tw = f.measureText(self.months[i])
            cv.drawString(self.months[i], m[0] - tw / 2, m[1], f, P('#ffffff', a))
        glow(cv, W / 2, 560, 260, '#FFFFFF', 120)


# 2 ─ « Le premier janvier, à minuit : le Big Bang. »
class BigBang(Scene):
    zoom = (1.0, 1.15)
    shake = 0.6

    def __init__(self):
        rnd = random.Random(302)
        self.p = [(rnd.uniform(0, 6.283), rnd.uniform(0.2, 1.0) ** 0.6, rnd.uniform(2, 7), rnd.choice(['#FFFFFF', '#FFD34A', '#FF4F81', '#2DE2E6', '#B6FF3B', '#B98CFF'])) for _ in range(900)]
        self.rays = [(rnd.uniform(0, 360), rnd.uniform(0.5, 1), rnd.choice(['#FFD34A', '#FF4F81', '#2DE2E6', '#ffffff'])) for _ in range(46)]

    def static(self, cv):
        bg_lin(cv, '#05031A', '#14062E')

    def dyn(self, cv, t, d):
        cx, cy = 960, 560
        e = ease_out(t / 2.2)
        glow(cv, cx, cy, 400 + 1400 * e, '#FF7AC6', 130)
        glow(cv, cx, cy, 200 + 700 * e, '#FFD34A', 180)
        for ang, ln, c in self.rays:
            cv.save(); cv.translate(cx, cy); cv.rotate(ang + t * 4)
            r0 = 120 + 900 * e * ln
            neon(cv, [(r0, 0), (r0 + 260 * ln, 0)], c, w=5, a=230, glow_w=14)
            cv.restore()
        for k in range(3):
            rr = (180 + 1300 * ease_out((t - k * 0.25) / 2.0)) if t > k * 0.25 else 0
            if rr:
                circle(cv, cx, cy, rr, ['#2DE2E6', '#FF4F81', '#FFD34A'][k], 160 * (1 - min(1, rr / 1500)), stroke=10)
        for ang, sp, r, c in self.p:
            dist = 40 + 1300 * e * sp
            x, y = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist * 0.85
            circle(cv, x, y, r * (1.2 - 0.5 * e), c, 230)
        circle(cv, cx, cy, 150 * (1 - e) + 60, '#FFFFFF')
        glow(cv, cx, cy, 300, '#FFFFFF', 255 * (1 - e * 0.6))
        if t < 0.15:
            cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P('#ffffff', 255 * (1 - t / 0.15)))
        page_corner(cv, t, 'JANV', '1', '#FF4F81', 240, 230, 0.95)
        label(cv, 1580, 980, '00:00:00', 34, font=FONT)


# 3 ─ « Pendant des mois, des étoiles naissent, explosent, renaissent. »
class StarsBirth(Scene):
    zoom = (1.0, 1.12)
    pan = (40, 0, -40, 0)

    def __init__(self):
        self.st = RichStars(360, 303, big=30)
        rnd = random.Random(304)
        self.pops = [(rnd.uniform(200, W - 200), rnd.uniform(150, H - 150), rnd.uniform(0, 1), rnd.choice(['#FFD34A', '#FF4F81', '#2DE2E6', '#B6FF3B'])) for _ in range(16)]

    def static(self, cv):
        nebula_bg(cv, '#0B0630', '#3A0D5E', 16, 13)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        for x, y, ph, c in self.pops:
            k = (t * 0.55 + ph) % 1.0
            if k < 0.35:
                r = 10 + 120 * ease_out(k / 0.35)
                glow(cv, x, y, r * 3, c, 220 * (1 - k / 0.35))
                circle(cv, x, y, r, c, 160 * (1 - k / 0.35), stroke=6)
                sparkle(cv, x, y, 50 * (1 - k / 0.35) + 10, '#ffffff', 255 * (1 - k / 0.35))
            else:
                sparkle(cv, x, y, 14 + 6 * math.sin(t * 5 + ph), c, 230)
        # éphéméride qui défile
        months = ['FÉV', 'MARS', 'AVR', 'MAI', 'JUIN', 'JUIL', 'AOÛT']
        cols = ['#FF8A3D', '#FFD34A', '#B6FF3B', '#3FC46A', '#2DE2C6', '#2DB8FF', '#3C5CFF']
        idx = min(len(months) - 1, int(t / max(d, 0.1) * len(months)))
        fl = (t / max(d, 0.1) * len(months)) % 1
        page_corner(cv, t, months[idx], str(1 + int(fl * 27)), cols[idx], 240, 230, 0.95)


# 4 ─ « Il faut attendre début septembre pour que la Terre se forme. »
class EarthForm(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        self.st = RichStars(200, 305)
        rnd = random.Random(306)
        self.ast = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.choice(['#FFB13B', '#2DE2E6', '#FF4F81'])) for _ in range(7)]
        self.cracks = []
        for i in range(14):
            a = rnd.uniform(0, 6.28); r = rnd.uniform(0.1, 0.8)
            pts = [(math.cos(a) * r, math.sin(a) * r)]
            for k in range(4):
                a += rnd.uniform(-0.8, 0.8); r += rnd.uniform(-0.1, 0.15)
                pts.append((math.cos(a) * min(r, 0.95), math.sin(a) * min(r, 0.95)))
            self.cracks.append(pts)

    def static(self, cv):
        nebula_bg(cv, '#08042A', '#2A0A40', 8, 23)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        cx, cy, R = 1180, 560, 330
        cam = Cam(pitch=-10, dist=1600, f=1600, cx=cx, cy=cy)
        glow(cv, cx, cy, R * 2.0, '#FF6A1F', 150)
        shade_ball(cv, cx, cy, R, '#FFB13B', '#8A1A1F')
        cv.save(); cv.translate(cx, cy); cv.rotate(t * 6)
        for pts in self.cracks:
            neon(cv, [(x * R, y * R) for x, y in pts], '#FFE07A', w=5, a=220, glow_w=14)
        cv.restore()
        oval(cv, cx + R * 0.25, cy + R * 0.3, R * 0.55, R * 0.4, '#5A0A1A', 70, blur=30)
        circle(cv, cx - R * 0.35, cy - R * 0.4, R * 0.25, '#FFE07A', 90, blur=30)
        wire_sphere(cv, cam, 0, 0, 0, R * 1.22, '#2DE2E6', 90, spin=t * 0.4, w=1.6)
        for ph, yy, c in self.ast:
            k = (t * 0.45 + ph) % 1.0
            sx, sy = -200 + k * 1100, 120 + yy * 120 + k * 260
            trail = [(sx - 240 + j * 40, sy - 60 + j * 10) for j in range(7)]
            neon(cv, trail, c, w=5, a=200 * (1 - k * 0.5))
            shade_ball(cv, sx, sy, 22, '#E8D8C8', '#6A5A6A')
        page_corner(cv, t, 'SEPT', '2', '#7A4BFF', 240, 230, 0.95)
        label(cv, 1180, 1000, 'TERRE · −4 540 000 000 ANS', 28, font=FONT)


# 5 ─ « Fin septembre, la vie apparaît. Une seule cellule. »
class Life(Scene):
    zoom = (1.0, 1.18)

    def __init__(self):
        rnd = random.Random(307)
        self.bub = [(rnd.uniform(0, W), rnd.uniform(0, 1), rnd.uniform(4, 14), rnd.uniform(0.15, 0.4)) for _ in range(120)]

    def static(self, cv):
        bg_lin(cv, '#123A8A', '#1A0A4E')
        for i in range(7):
            poly(cv, [(i * 300 - 180, 0), (i * 300 - 40, 0), (i * 300 + 260, H), (i * 300 + 60, H)], '#7FE7FF', 18)
        for x in (260, 760, 1500):
            poly(cv, [(x - 140, H + 50), (x - 40, 820), (x + 40, 820), (x + 140, H + 50)], '#0E1A40')
            oval(cv, x, 822, 44, 14, '#FF8A3D', 200)

    def dyn(self, cv, t, d):
        for x in (260, 760, 1500):
            for k in range(6):
                q = (t * 0.4 + k / 6) % 1
                blob(cv, x + 30 * math.sin(q * 6 + x), 800 - q * 520, 40 + q * 90, '#3A3A7A', 140 * (1 - q), seed=k, t=t, blur=12)
        for x, ph, r, sp in self.bub:
            k = (ph + t * sp) % 1
            circle(cv, x + 16 * math.sin(k * 12), H - k * (H + 60), r, '#BFF6FF', 150, stroke=2.5)
        cx, cy = 960, 520
        k = ease(max(0, (t - 0.8) / max(d - 0.8, 0.1)))
        for side in ((-1, 1) if k > 0 else (0,)):
            x = cx + side * 160 * k
            p = 1 + 0.04 * math.sin(t * 3 + side)
            glow(cv, x, cy, 360 * p, '#2DE2C6', 140)
            blob(cv, x, cy, (250 - 60 * k) * p, '#3FE0B0', 220, seed=5, t=t * 2, wob=0.1)
            blob(cv, x, cy, (225 - 55 * k) * p, '#8AF5D0', 170, seed=6, t=t * 2, wob=0.08)
            circle(cv, x - 60, cy - 80, 34, '#ffffff', 120)
            shade_ball(cv, x + 30, cy + 10, 80 - 20 * k, '#E07AFF', '#7A1E9E')
            for j in range(7):
                a = j * 0.9 + t * 0.6
                circle(cv, x + 150 * math.cos(a) * (1 - 0.3 * k), cy + 120 * math.sin(a), 10, '#FFFFFF', 160)
        page_corner(cv, t, 'SEPT', '21', '#7A4BFF', 240, 230, 0.95)
        label(cv, 960, 990, 'LA PREMIÈRE CELLULE', 30, font=FONT)


class _Jungle(Scene):
    sky = ('#2A0E6A', '#E0478A')

    def static(self, cv):
        bg_lin(cv, *self.sky)
        rnd = random.Random(8)
        for layer, (col, y0) in enumerate([('#3A1470', 720), ('#2A0E58', 800), ('#1A0840', 880)]):
            for i in range(12):
                x = rnd.uniform(-100, W + 100)
                blob(cv, x, y0 - rnd.uniform(0, 120), rnd.uniform(120, 220), col, seed=i + layer * 20)
            cv.drawRect(skia.Rect.MakeXYWH(-400, y0, W + 800, 800), P(col))
        for x in (120, 380, 1640, 1820):
            rrect(cv, x - 14, 380, 28, 520, 14, '#140630')
            for k in range(6):
                cv.save(); cv.translate(x, 390); cv.rotate(-150 + k * 50)
                oval(cv, 110, 0, 120, 28, '#1E0A48')
                cv.restore()


# 6 ─ « Les dinosaures arrivent le vingt-cinq décembre. Joyeux Noël. »
class DinoXmas(_Jungle):
    zoom = (1.0, 1.1)
    pan = (0, 30, 0, -10)

    def __init__(self):
        rnd = random.Random(309)
        self.snow = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(3, 8), rnd.uniform(50, 130)) for _ in range(160)]

    def dyn(self, cv, t, d):
        # guirlande lumineuse
        p = skia.Path(); p.moveTo(-50, 150); p.quadTo(960, 380, W + 50, 150)
        cv.drawPath(p, P('#140630', 255, stroke=4))
        for k in range(26):
            u = k / 25
            x = -50 + (W + 100) * u
            y = (1 - u) ** 2 * 150 + 2 * u * (1 - u) * 380 + u ** 2 * 150
            c = ['#FF4F81', '#FFD34A', '#2DE2E6', '#B6FF3B'][k % 4]
            on = (int(t * 4) + k) % 3 != 0
            glow(cv, x, y + 16, 40, c, 200 if on else 60)
            oval(cv, x, y + 16, 10, 14, c, 255 if on else 120)
        dino(cv, 1180, 940, 115, t, santa=True)
        dino(cv, 420, 960, 55, t + 1, body='#FF8A3D', belly='#FFD08A', santa=False)
        for i, (x, c) in enumerate([(700, '#FF4F81'), (820, '#2DE2E6'), (1560, '#FFD34A')]):
            rrect(cv, x, 860, 110, 90, 10, c)
            cv.drawRect(skia.Rect.MakeXYWH(x + 47, 860, 16, 90), P('#ffffff', 220))
            cv.drawRect(skia.Rect.MakeXYWH(x, 895, 110, 14), P('#ffffff', 220))
        for x, y, r, sp in self.snow:
            circle(cv, (x + 20 * math.sin(t + y)) % W, (y + t * sp) % H, r, '#ffffff', 220)
        page_corner(cv, t, 'DÉC', '25', '#E8243C', 240, 230, 0.95)

    def fg(self, cv, t, d):
        for x, y, r in ((-60, 1060, 260), (1980, 1040, 300)):
            blob(cv, x, y, r, '#0E0428', 255, seed=int(r), t=t, blur=14)


# 7 ─ « Ils disparaissent le trente. »
class Meteor(_Jungle):
    zoom = (1.0, 1.2)
    sky = ('#5A0A2A', '#FF7A3D')

    def dyn(self, cv, t, d):
        k = ease(t / max(d, 0.1))
        mx, my = 1800 - 1100 * k, -80 + 640 * k
        glow(cv, mx, my, 260 + 300 * k, '#FFD34A', 200)
        trail = [(mx + j * 70, my - j * 42) for j in range(12)]
        neon(cv, trail, '#FFB13B', w=28, a=230, glow_w=70)
        neon(cv, trail[:7], '#FFF0B0', w=10, a=255)
        shade_ball(cv, mx, my, 50 + 30 * k, '#FFE0B0', '#8A2A1A')
        dino(cv, 760, 940, 110, t, mood='wow', look_up=k)
        dino(cv, 1450, 960, 60, t + 1, body='#FF8A3D', belly='#FFD08A', mood='wow', look_up=k)
        if k > 0.92:
            cv.drawRect(skia.Rect.MakeXYWH(-400, -400, W + 800, H + 800), P('#FFF6D0', 255 * (k - 0.92) / 0.08))
        page_corner(cv, t, 'DÉC', '30', '#E8243C', 240, 230, 0.95)


# 8 ─ « Et nous ? Le trente et un décembre, à vingt-trois heures quarante-huit. »
class Clock(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        self.st = RichStars(200, 311)

    def static(self, cv):
        nebula_bg(cv, '#0A0630', '#3A0E6A', 9, 31)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        cam = Cam(pitch=-20, dist=2200, f=1500, cy=600)
        wire_plane(cv, cam, 520, 2600, 180, '#7A5BFF', 80, off=t * 60)
        cx, cy, R = 960, 520, 390
        glow(cv, cx, cy, 700, '#7A4BFF', 140)
        shade_ball(cv, cx, cy, R + 40, '#4A2AAA', '#1A0A4E')
        circle(cv, cx, cy, R, '#120838')
        for i in range(60):
            a = math.radians(i * 6 - 90)
            big = i % 5 == 0
            r0 = R - (50 if big else 26)
            cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (R - 12), cy + math.sin(a) * (R - 12), P('#BFA8FF' if big else '#6A5AB0', 255, stroke=8 if big else 3))
        mins = 47 + min(1.0, t / 1.2)
        secs = (t * 60) % 60
        for ang, ln, w, c in ((math.radians((23 % 12 + mins / 60) * 30 - 90), R * 0.5, 18, '#FFD34A'),
                              (math.radians(mins * 6 - 90), R * 0.78, 12, '#2DE2E6'),
                              (math.radians(secs * 6 - 90), R * 0.85, 4, '#FF4F81')):
            neon(cv, [(cx, cy), (cx + math.cos(ang) * ln, cy + math.sin(ang) * ln)], c, w=w, glow_w=w * 3)
        circle(cv, cx, cy, 20, '#FFFFFF')
        neon(cv, [(cx + math.cos(math.radians(a - 90)) * (R + 70), cy + math.sin(math.radians(a - 90)) * (R + 70)) for a in range(int(-12 * 6), 1, 4)], '#FF4F81', w=10, arrow=True)
        page_corner(cv, t, 'DÉC', '31', '#E8243C', 240, 230, 0.95)
        label(cv, 1600, 980, '23:48', 44, font=FONT)


# 9 ─ « Il reste douze minutes avant minuit. »
class Cavemen(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = RichStars(260, 312)

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#3A1460')
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, 600); p.quadTo(200, 300, 560, 640); p.lineTo(560, H + 400); p.close()
        cv.drawPath(p, P('#1A0A3A'))
        oval(cv, 260, 760, 150, 180, '#0A0420')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#140830'))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        # horloge géante dans le ciel (compte à rebours)
        cx, cy, R = 1360, 330, 210
        rem = max(0, 12 * 60 - t * 9)
        glow(cv, cx, cy, 380, '#FFD34A', 110)
        circle(cv, cx, cy, R, '#FFF6D0', 230)
        circle(cv, cx, cy, R, '#FFD34A', 255, stroke=10)
        frac = rem / 3600
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - R - 40, cy - R - 40, cx + R + 40, cy + R + 40), -90, -360 * frac * 5)
        cv.drawPath(p, P('#FF4F81', 160, stroke=26, blur=8)); cv.drawPath(p, P('#FF4F81', 255, stroke=12))
        mm, ss = int(rem // 60), int(rem % 60)
        f = skia.Font(FONT, 90); s = f'{mm:02d}:{ss:02d}'
        cv.drawString(s, cx - f.measureText(s) / 2, cy + 32, f, P('#1A1030'))
        # feu + humains préhistoriques
        fx, fy = 960, 930
        glow(cv, fx, fy - 80, 460, '#FF8A3D', 210)
        for i in range(3):
            blob(cv, fx, fy - 60 - i * 40, 100 - i * 26, ['#FF5A1F', '#FFB13B', '#FFF0B0'][i], seed=i, t=t * 5, wob=0.35)
        for k in range(8):
            q = (t * 0.8 + k / 8) % 1
            circle(cv, fx + 60 * math.sin(q * 9 + k), fy - 150 - q * 320, 6 * (1 - q) + 2, '#FFD34A', 255 * (1 - q))
        char_front(cv, 640, 960, 52, t, skin='#C98058', hair='#2A1A14', top='#8A5A3A', pants='#5E382C', mood='wow', look=(1, -1), hairstyle=1)
        char_front(cv, 1280, 960, 48, t + 1.3, skin='#8A5236', hair='#3A1E14', top='#A06A44', pants='#5E382C', mood='smile', look=(-1, 0), hairstyle=2, arms='out')


# 10 ─ « Les pyramides ? Dix secondes avant la fin. »
class Pyramids(Scene):
    zoom = (1.0, 1.12)
    pan = (50, 0, -50, 0)

    def static(self, cv):
        bg_lin(cv, '#5A1E8A', '#FF9A5C')
        glow(cv, 1450, 520, 520, '#FFE07A', 200)
        circle(cv, 1450, 560, 150, '#FFF0B0')
        for (x, b, h) in ((560, 420, 380), (1020, 330, 290), (1350, 230, 200)):
            poly(cv, [(x - b, 820), (x, 820 - h), (x + b * 0.15, 820)], '#F2B25C')
            poly(cv, [(x + b * 0.15, 820), (x, 820 - h), (x + b, 820)], '#B8642E')
            for k in range(1, 8):
                yy = 820 - h * k / 8
                cv.drawLine(x - b * (1 - k / 8), yy, x + b * (1 - k / 8), yy, P('#8A4A1A', 70, stroke=2))
        for i, (col, y) in enumerate([('#E89A4A', 820), ('#C8763A', 900), ('#A85A2E', 980)]):
            p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, y)
            p.quadTo(500, y - 70 + i * 20, 1000, y + 10); p.quadTo(1500, y + 60, W + 400, y - 30); p.lineTo(W + 400, H + 400); p.close()
            cv.drawPath(p, P(col))

    def dyn(self, cv, t, d):
        for i in range(3):
            x = (200 + i * 170 + t * 70) % (W + 300) - 150
            y = 905
            bob = 6 * math.sin(t * 6 + i)
            oval(cv, x, y - 70 + bob, 70, 34, '#5A2A1A'); circle(cv, x - 10, y - 108 + bob, 26, '#5A2A1A')
            p = skia.Path(); p.moveTo(x + 50, y - 80 + bob); p.quadTo(x + 110, y - 110, x + 100, y - 150 + bob)
            cv.drawPath(p, P('#5A2A1A', 255, stroke=20)); oval(cv, x + 110, y - 155 + bob, 28, 16, '#5A2A1A')
            for lx in (-45, -20, 25, 50):
                cv.drawLine(x + lx, y - 50, x + lx + 8 * math.sin(t * 6 + lx), y, P('#5A2A1A', 255, stroke=9))
        cx, cy, R = 1650, 220, 110
        rem = max(0.0, 10 - t * 0.5)
        circle(cv, cx, cy, R, '#1A0A3A', 200)
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - R, cy - R, cx + R, cy + R), -90, 360 * rem / 10)
        cv.drawPath(p, P('#FFD34A', 255, stroke=14))
        f = skia.Font(FONT, 64); s = f'{rem:0.0f} s'
        cv.drawString(s, cx - f.measureText(s) / 2, cy + 22, f, P('#FFFFFF'))
        page_corner(cv, t, 'DÉC', '31', '#E8243C', 240, 230, 0.95)


# 11 ─ « Toute l'histoire écrite de l'humanité tient dans les douze dernières secondes. »
class History(Scene):
    zoom = (1.0, 1.08)

    def __init__(self):
        self.st = RichStars(180, 313)

    def static(self, cv):
        nebula_bg(cv, '#0A0630', '#2A0B5E', 8, 33)

    def _icon(self, cv, kind, x, y, s, t):
        c = '#FFF6E8'
        if kind == 0:   # parchemin
            rrect(cv, x - 60 * s, y - 70 * s, 120 * s, 140 * s, 10 * s, '#F2D9A8')
            for k in range(4):
                cv.drawLine(x - 40 * s, y - 40 * s + k * 26 * s, x + 40 * s, y - 40 * s + k * 26 * s, P('#8A5A2A', 255, stroke=5 * s))
            rrect(cv, x - 75 * s, y - 85 * s, 150 * s, 26 * s, 13 * s, '#C8A070'); rrect(cv, x - 75 * s, y + 60 * s, 150 * s, 26 * s, 13 * s, '#C8A070')
        elif kind == 1:  # château
            rrect(cv, x - 90 * s, y - 40 * s, 180 * s, 110 * s, 6, '#B98CFF')
            for k in range(-1, 2):
                rrect(cv, x + k * 70 * s - 22 * s, y - 100 * s, 44 * s, 70 * s, 4, '#9A6AE8')
                poly(cv, [(x + k * 70 * s - 30 * s, y - 100 * s), (x + k * 70 * s, y - 150 * s), (x + k * 70 * s + 30 * s, y - 100 * s)], '#FF4F81')
            oval(cv, x, y + 40 * s, 26 * s, 34 * s, '#3A1A6A')
        elif kind == 2:  # voilier
            p = skia.Path(); p.moveTo(x - 100 * s, y + 20 * s); p.lineTo(x + 100 * s, y + 20 * s); p.lineTo(x + 70 * s, y + 60 * s); p.lineTo(x - 70 * s, y + 60 * s); p.close()
            cv.drawPath(p, P('#C8763A'))
            cv.drawLine(x, y + 20 * s, x, y - 120 * s, P('#8A4A1A', 255, stroke=7 * s))
            poly(cv, [(x + 6 * s, y - 115 * s), (x + 85 * s, y + 5 * s), (x + 6 * s, y + 5 * s)], c)
            poly(cv, [(x - 6 * s, y - 90 * s), (x - 70 * s, y + 5 * s), (x - 6 * s, y + 5 * s)], '#E8E0F8')
        elif kind == 3:  # train à vapeur
            rrect(cv, x - 100 * s, y - 40 * s, 140 * s, 80 * s, 14 * s, '#2DB8FF'); rrect(cv, x + 30 * s, y - 80 * s, 70 * s, 120 * s, 10 * s, '#2A7ACC')
            rrect(cv, x - 80 * s, y - 90 * s, 30 * s, 50 * s, 6, '#1A3A6A')
            for k in range(3):
                circle(cv, x - 70 * s + k * 70 * s, y + 50 * s, 24 * s, '#1A1030')
            for k in range(4):
                circle(cv, x - 70 * s - k * 30 * s, y - 110 * s - k * 30 * s, (18 + k * 8) * s, '#E8E0F8', 200 - k * 40)
        elif kind == 4:  # voiture
            rrect(cv, x - 110 * s, y - 20 * s, 220 * s, 60 * s, 24 * s, '#FF4F81'); rrect(cv, x - 60 * s, y - 70 * s, 120 * s, 60 * s, 24 * s, '#FF4F81')
            rrect(cv, x - 45 * s, y - 60 * s, 40 * s, 38 * s, 8, '#BFF6FF'); rrect(cv, x + 5 * s, y - 60 * s, 40 * s, 38 * s, 8, '#BFF6FF')
            for k in (-60, 60):
                circle(cv, x + k * s, y + 42 * s, 26 * s, '#1A1030'); circle(cv, x + k * s, y + 42 * s, 10 * s, '#C0C0D0')
        elif kind == 5:  # avion
            rrect(cv, x - 120 * s, y - 18 * s, 240 * s, 36 * s, 18 * s, c)
            poly(cv, [(x - 20 * s, y), (x + 30 * s, y), (x - 10 * s, y + 90 * s), (x - 50 * s, y + 90 * s)], '#C0C8E8')
            poly(cv, [(x - 20 * s, y), (x + 30 * s, y), (x - 10 * s, y - 80 * s), (x - 50 * s, y - 80 * s)], '#C0C8E8')
            poly(cv, [(x - 120 * s, y), (x - 100 * s, y), (x - 130 * s, y - 50 * s), (x - 150 * s, y - 50 * s)], '#FF4F81')
        elif kind == 6:  # fusée
            p = skia.Path(); p.moveTo(x, y - 120 * s); p.quadTo(x + 55 * s, y - 60 * s, x + 40 * s, y + 50 * s); p.lineTo(x - 40 * s, y + 50 * s); p.quadTo(x - 55 * s, y - 60 * s, x, y - 120 * s)
            cv.drawPath(p, P(c)); circle(cv, x, y - 40 * s, 20 * s, '#2DB8FF')
            poly(cv, [(x - 40 * s, y + 10 * s), (x - 80 * s, y + 70 * s), (x - 36 * s, y + 50 * s)], '#FF4F81'); poly(cv, [(x + 40 * s, y + 10 * s), (x + 80 * s, y + 70 * s), (x + 36 * s, y + 50 * s)], '#FF4F81')
            blob(cv, x, y + 85 * s, 30 * s, '#FFB13B', seed=2, t=t * 6, wob=0.4)
        else:  # smartphone
            rrect(cv, x - 55 * s, y - 100 * s, 110 * s, 200 * s, 18 * s, '#1A1030'); rrect(cv, x - 46 * s, y - 88 * s, 92 * s, 176 * s, 12 * s, '#2DE2E6')
            for k in range(3):
                rrect(cv, x - 34 * s, y - 70 * s + k * 50 * s, 68 * s, 36 * s, 8, ['#FF4F81', '#FFD34A', '#B6FF3B'][k], 220)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        cam = Cam(pitch=-22, dist=2000, f=1500, cy=520)
        wire_plane(cv, cam, 480, 2600, 180, '#7A5BFF', 80, off=t * 400)
        y = 760
        neon(cv, [(-100, y), (W + 100, y)], '#7A4BFF', w=6)
        spd = 260
        for i in range(8):
            x = 260 + i * 330 - t * spd
            if -200 < x < W + 200:
                sc = 1.0 - min(0.4, abs(x - 960) / 2400)
                glow(cv, x, y - 140, 170, ['#FFD34A', '#B98CFF', '#2DE2E6', '#2DB8FF', '#FF4F81', '#FFFFFF', '#FFB13B', '#2DE2E6'][i], 90)
                self._icon(cv, i, x, y - 140, sc, t)
                circle(cv, x, y, 14, '#FFD34A')
        rem = max(0.0, 12 - 12 * t / max(d, 0.1))
        label(cv, 960, 980, f'−{rem:04.1f} s'.replace('.', ','), 40, font=FONT)


# 12 ─ « Et ta vie entière dure moins d'un cinquième de seconde. »
class Stopwatch(Scene):
    zoom = (1.0, 1.15)

    def static(self, cv):
        bg_rad(cv, 960, 540, 1200, '#4A2AAA', '#0E0638')
        for k in range(36):
            cv.save(); cv.translate(960, 540); cv.rotate(k * 10)
            poly(cv, [(0, 0), (1500, -60), (1500, 60)], '#7A5BFF', 26)
            cv.restore()

    def dyn(self, cv, t, d):
        cx, cy, R = 1180, 560, 340
        glow(cv, cx, cy, 600, '#2DE2E6', 120)
        rrect(cv, cx - 50, cy - R - 110, 100, 80, 20, '#C8C8E0')
        rrect(cv, cx - 30, cy - R - 50, 60, 60, 10, '#9A9AC0')
        shade_ball(cv, cx, cy, R + 30, '#F0F0FF', '#7A7AA8')
        circle(cv, cx, cy, R, '#FFFFFF')
        for i in range(60):
            a = math.radians(i * 6 - 90)
            r0 = R - (40 if i % 5 == 0 else 20)
            cv.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (R - 10), cy + math.sin(a) * (R - 10), P('#1A1030', 255, stroke=6 if i % 5 == 0 else 2))
        v = 0.18 * ease_out(min(1, t / 0.6))
        ang = math.radians(v * 360 - 90)
        p = skia.Path(); p.moveTo(cx, cy); p.arcTo(skia.Rect.MakeLTRB(cx - R + 30, cy - R + 30, cx + R - 30, cy + R - 30), -90, v * 360, False); p.close()
        cv.drawPath(p, P('#FF4F81', 120))
        neon(cv, [(cx, cy), (cx + math.cos(ang) * (R - 40), cy + math.sin(ang) * (R - 40))], '#FF4F81', w=10)
        circle(cv, cx, cy, 22, '#1A1030')
        f = skia.Font(FONT, 70); s = f'{v:0.2f} s'.replace('.', ',')
        cv.drawString(s, cx - f.measureText(s) / 2, cy + 200, f, P('#1A1030'))
        char_front(cv, 430, 1000, 62, t, mood='wow', look=(1, -1), hairstyle=0, top='#FF4F81')


# 13 ─ « Un clin d'œil. »
class Wink(Scene):
    zoom = (1.0, 1.06)

    def static(self, cv):
        bg_rad(cv, 960, 540, 1100, '#FFD34A', '#FF4F81')
        for k in range(24):
            cv.save(); cv.translate(960, 540); cv.rotate(k * 15)
            poly(cv, [(0, 0), (1500, -90), (1500, 90)], '#FFFFFF', 40)
            cv.restore()

    def dyn(self, cv, t, d):
        mood = 'wink' if t > 0.25 else 'smile'
        char_front(cv, 960, 2000, 300, t, mood=mood, hairstyle=1, hair='#2A1A14', skin='#C98058', top='#3C4CC8', blink=False)
        for i in range(6):
            a = i * 1.05 + t
            sparkle(cv, 960 + 620 * math.cos(a), 420 + 300 * math.sin(a), 28 + 10 * math.sin(t * 6 + i), '#FFFFFF', 255)


# 14 ─ « Alors oui, à cette échelle, tu es minuscule. »
class Tiny(Scene):
    zoom = (2.2, 1.0)

    def __init__(self):
        self.st = RichStars(320, 314)

    def static(self, cv):
        nebula_bg(cv, '#06041C', '#2A0A50', 10, 34)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        cx, cy = 960, 560
        cam = Cam(pitch=-18, dist=1600, f=1500, cx=cx, cy=cy)
        for i, (r, lab, c) in enumerate([(260, '12 742 km', '#2DE2E6'), (420, '150 000 000 km', '#FFD34A'), (620, '100 000 ANNÉES-LUMIÈRE', '#FF4F81')]):
            pts = [cam.p(r * math.cos(a / 40 * 6.283), 0, r * math.sin(a / 40 * 6.283)) for a in range(41)]
            neon(cv, [(q[0], q[1]) for q in pts], c, w=3, a=200, glow_w=10)
            ang = [2.3, 1.15, 1.75][i]
            q = cam.p(r * math.cos(ang), 0, r * math.sin(ang))
            label(cv, q[0], q[1] + 40, lab, 24, color=c, font=FONT, box=False)
        glow(cv, cx, cy, 200, '#4FD8FF', 160)
        shade_ball(cv, cx, cy, 70, '#5AB8FF', '#1A3A9A', rim='#BFF6FF')
        blob(cv, cx - 20, cy - 10, 26, '#3FC46A', seed=2); blob(cv, cx + 25, cy + 20, 18, '#3FC46A', seed=5)
        wire_sphere(cv, cam, 0, 0, 0, 95, '#BFF6FF', 80, spin=t * 0.5, w=1.2)
        char_front(cv, cx, cy - 66, 3.2, t, mood='smile', bob=False)
        neon(cv, [(cx + 140, cy - 210), (cx + 30, cy - 90)], '#FFFFFF', w=3, arrow=True, glow_w=8)
        label(cv, cx + 170, cy - 220, 'TOI', 26, font=FONT)


# 15 ─ « Mais dans ce cinquième de seconde, tu peux aimer, rire, »
class Love(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        rnd = random.Random(315)
        self.h = [(rnd.uniform(0, W), rnd.uniform(0, 1), rnd.uniform(16, 36), rnd.choice(['#FF4F81', '#FF8AB8', '#FFD34A'])) for _ in range(40)]

    def static(self, cv):
        bg_lin(cv, '#FF8AB8', '#FFD08A')
        for k in range(10):
            cloud(cv, 120 + k * 210, 140 + (k % 3) * 60, 60, '#FFFFFF', 120, shade='#FFC0D8')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#FF6F91'))

    def _heart(self, cv, x, y, r, c, a=255):
        circle(cv, x - r * 0.5, y, r * 0.55, c, a); circle(cv, x + r * 0.5, y, r * 0.55, c, a)
        poly(cv, [(x - r * 1.02, y + r * 0.15), (x + r * 1.02, y + r * 0.15), (x, y + r * 1.2)], c, a)

    def dyn(self, cv, t, d):
        for x, ph, r, c in self.h:
            k = (ph + t * 0.25) % 1
            self._heart(cv, x + 30 * math.sin(k * 8 + x), H + 60 - k * (H + 200), r, c, 230 * math.sin(k * math.pi))
        char_front(cv, 640, 960, 70, t, mood='happy', arms='hug', hairstyle=2, hair='#5A2A14', top='#7A4BFF', skin='#F2A97E')
        char_front(cv, 860, 960, 74, t + 0.4, mood='happy', arms='hug', hairstyle=0, hair='#1A1030', top='#2DB8FF', skin='#8A5236')
        self._heart(cv, 750, 560 + 10 * math.sin(t * 4), 50, '#FF4F81')
        char_front(cv, 1340, 960, 76, t * 1.6, mood='laugh', arms='up', hairstyle=1, hair='#2A1A14', top='#FFD34A', pants='#3C4CC8', skin='#C98058')
        for k in range(5):
            q = (t * 0.9 + k / 5) % 1
            label(cv, 1480 + (k % 3) * 70 - 70, 560 - q * 260 - (k % 2) * 40, 'HA', 40, color='#7A1E4A', a=255 * math.sin(q * math.pi), font=FONT, box=False)


# 16 ─ « et créer quelque chose qui n'avait jamais existé en treize milliards d'années. »
class Create(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        self.st = RichStars(200, 316)

    def static(self, cv):
        nebula_bg(cv, '#120838', '#4A1270', 10, 36)
        cv.drawRect(skia.Rect.MakeXYWH(-400, 920, W + 800, 600), P('#1A0A3A'))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        cx, cy = 1200, 460
        cam = Cam(pitch=-10, dist=1500, f=1500, cx=cx, cy=cy)
        k = ease_out(t / max(d * 0.8, 0.1))
        wire_sphere(cv, cam, 0, 0, 0, 260 * k + 10, '#2DE2E6', 160, spin=t * 0.8, w=2)
        for j, c in enumerate(['#FF4F81', '#FFD34A', '#B6FF3B', '#B98CFF']):
            pts = []
            for u in range(0, int(80 * k) + 2):
                a = u * 0.15 + j * 1.57 + t
                r = 40 + u * 4.2
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.6))
            neon(cv, pts, c, w=6, a=230, arrow=True)
        glow(cv, cx, cy, 200, '#FFFFFF', 200)
        sparkle(cv, cx, cy, 70 + 10 * math.sin(t * 5), '#FFFFFF')
        # chevalet + toile
        rrect(cv, 380, 520, 18, 420, 9, '#8A4A1A'); rrect(cv, 560, 520, 18, 420, 9, '#8A4A1A')
        rrect(cv, 330, 420, 300, 240, 10, '#FFF8EE')
        for i, c in enumerate(['#FF4F81', '#2DE2E6', '#FFD34A']):
            blob(cv, 420 + i * 60, 520 + 20 * math.sin(i), 50 * min(1, k * 1.5), c, 220, seed=i + 1)
        char_front(cv, 720, 960, 64, t, mood='happy', arms='out', hairstyle=3, top='#FF8A3D', skin='#F2A97E')
        label(cv, 1200, 860, 'JAMAIS VU EN 13 800 000 000 ANS', 26, font=FONT)


# 17 ─ « Ne passe pas ton clin d'œil à avoir peur. »
class Fear(Scene):
    zoom = (1.0, 1.15)

    def static(self, cv):
        bg_lin(cv, '#0E0A3A', '#1E1050')
        rrect(cv, 1250, 140, 420, 340, 16, '#2A2070'); rrect(cv, 1266, 156, 388, 308, 10, '#0A0830')
        circle(cv, 1540, 260, 46, '#E8E4FF'); circle(cv, 1562, 246, 46, '#0A0830')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 880, W + 800, 600), P('#120A36'))
        rrect(cv, 420, 640, 1080, 280, 50, '#3A3A9A')
        rrect(cv, 420, 600, 260, 110, 50, '#E8E4FF')

    def dyn(self, cv, t, d):
        # ombres de monstres au mur
        for i, (x, y, r) in enumerate([(300, 380, 170), (1000, 300, 220)]):
            sway = 20 * math.sin(t * 1.5 + i)
            blob(cv, x + sway, y, r, '#05041A', 200, seed=i + 40, t=t, wob=0.35)
            for ex in (-0.3, 0.3):
                oval(cv, x + sway + ex * r, y - r * 0.15, 18, 26 * (0.2 if (t * 0.8 + i) % 2.5 < 0.15 else 1), '#FFD34A', 230)
        # couverture avec les yeux qui dépassent
        cx, cy = 960, 700
        p = skia.Path(); p.moveTo(560, 920); p.cubicTo(620, 600, 1300, 560, 1440, 920); p.close()
        cv.drawPath(p, P('#FF4F81'))
        for k in range(5):
            cv.drawLine(640 + k * 160, 760, 620 + k * 170, 920, P('#D93A6A', 200, stroke=6))
        tremble = 4 * math.sin(t * 40)
        circle(cv, cx + tremble, 628, 100, '#2A1A14')
        for side in (-1, 1):
            oval(cv, cx + side * 52 + tremble, 640, 38, 46, '#FFFFFF')
            circle(cv, cx + side * 52 + tremble + 10 * math.sin(t * 2), 648, 17, '#1A1030')
        for side in (-1, 1):
            cv.save(); cv.translate(cx + side * 52 + tremble, 582); cv.rotate(18 * side)
            rrect(cv, -28, -7, 56, 14, 7, '#C98058'); cv.restore()
        rrect(cv, cx - 190, 668, 380, 70, 35, '#FF4F81')
        for side in (-1, 1):
            circle(cv, cx + side * 130 + tremble, 668, 30, '#C98058')
        glow(cv, 300, 860, 160, '#FFD34A', 160)
        rrect(cv, 280, 820, 40, 60, 10, '#FFE680')


# 18 ─ « Fais-en quelque chose de beau. »
class Fireworks(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.st = RichStars(220, 318)
        rnd = random.Random(319)
        self.fw = [(rnd.uniform(200, W - 200), rnd.uniform(140, 520), rnd.uniform(0, 1), rnd.choice(['#FF4F81', '#FFD34A', '#2DE2E6', '#B6FF3B', '#B98CFF'])) for _ in range(9)]

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#5A1E7A')
        rnd = random.Random(6)
        for i in range(20):
            x = -100 + i * 110; h = rnd.uniform(160, 420)
            rrect(cv, x, 900 - h, 100, h + 40, 6, '#1E0E4A')
            for wy in range(int(920 - h), 880, 34):
                for wx in (x + 18, x + 58):
                    if rnd.random() > 0.5:
                        cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 22, 16), P('#FFD34A', 200))
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#140A36'))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        for x, y, ph, c in self.fw:
            k = (t * 0.6 + ph) % 1.0
            if k < 0.25:
                q = k / 0.25
                neon(cv, [(x, 900), (x, 900 - (900 - y) * q)], c, w=4, a=200)
            else:
                q = (k - 0.25) / 0.75
                r = 40 + 240 * ease_out(q)
                for j in range(22):
                    a = j / 22 * 6.283
                    x1, y1 = x + math.cos(a) * r, y + math.sin(a) * r + 60 * q * q
                    neon(cv, [(x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75 + 50 * q * q), (x1, y1)], c, w=4, a=255 * (1 - q), glow_w=10)
                glow(cv, x, y, r * 1.3, c, 120 * (1 - q))
        char_front(cv, 960, 1000, 66, t * 1.5, mood='laugh', arms='up', hairstyle=0, top='#FF4F81', skin='#C98058')
        page_corner(cv, t, 'JANV', '1', '#FF4F81', 240, 230, 0.95)


SEGMENTS = [
    (Calendar3D, "Imagine que toute l'histoire de l'univers tienne dans une seule année."),
    (BigBang, "Le premier janvier, à minuit : le Big Bang."),
    (StarsBirth, "Pendant des mois, des étoiles naissent, explosent, renaissent."),
    (EarthForm, "Il faut attendre début septembre pour que la Terre se forme."),
    (Life, "Fin septembre, la vie apparaît. Une seule cellule."),
    (DinoXmas, "Les dinosaures arrivent le vingt-cinq décembre. Joyeux Noël."),
    (Meteor, "Ils disparaissent le trente."),
    (Clock, "Et nous ? Le trente et un décembre, à vingt-trois heures quarante-huit."),
    (Cavemen, "Il reste douze minutes avant minuit."),
    (Pyramids, "Les pyramides ? Dix secondes avant la fin."),
    (History, "Toute l'histoire écrite de l'humanité tient dans les douze dernières secondes."),
    (Stopwatch, "Et ta vie entière dure moins d'un cinquième de seconde."),
    (Wink, "Un clin d'œil."),
    (Tiny, "Alors oui, à cette échelle, tu es minuscule."),
    (Love, "Mais dans ce cinquième de seconde, tu peux aimer, rire,"),
    (Create, "et créer quelque chose qui n'avait jamais existé en treize milliards d'années."),
    (Fear, "Ne passe pas ton clin d'œil à avoir peur."),
    (Fireworks, "Fais-en quelque chose de beau."),
]

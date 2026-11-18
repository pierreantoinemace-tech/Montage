"""« Notre place » : 15 plans, même style que invisible/ (mascottes rondes, ombrage 2 tons, hologrammes)."""
import math, os, random, sys, importlib.util
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(HERE, '..', 'calendrier'))
from lib import *
from kit import *
_s = importlib.util.spec_from_file_location('inv_scenes', os.path.join(HERE, '..', 'invisible', 'scenes.py'))
inv = importlib.util.module_from_spec(_s); _s.loader.exec_module(inv)
cel, circ_path, oval_path, eye, blinkf, birdie, holo_hemis, RICH = inv.cel, inv.circ_path, inv.oval_path, inv.eye, inv.blinkf, inv.birdie, inv.holo_hemis, inv.RICH

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7, readable=True)


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


class Galaxy:
    def __init__(self, seed=7, n=1600, R=560):
        rnd = random.Random(seed)
        self.p = []
        for arm in range(2):
            for k in range(n // 2):
                u = rnd.random() ** 0.7
                th = arm * math.pi + u * 3.6 * math.pi / 1.4 + rnd.gauss(0, 0.25)
                r = 30 + u * R + rnd.gauss(0, 18)
                self.p.append((r, th, rnd.uniform(1.2, 3.8), rnd.choice(['#ffffff', '#C8B8FF', '#8FD3FF', '#FFC9F0', '#FFE6A0'])))

    def draw(self, cv, cx, cy, t, tilt=0.6, rot=0, scale=1.0, a=230):
        glow(cv, cx, cy, 650 * scale, '#7B4BFF', 120)
        cv.save(); cv.translate(cx, cy); cv.scale(scale, scale * tilt); cv.rotate(rot + t * 5)
        for r, th, s, col in self.p:
            circle(cv, r * math.cos(th), r * math.sin(th), s, col, a)
        cv.restore()
        glow(cv, cx, cy, 220 * scale, '#FFE6B0', 255)


def earth_mascot(cv, x, y, r, t, mood='happy', look=(0, 0)):
    glow(cv, x, y, r * 1.35, '#4FD8FF', 140)
    body = circ_path(x, y, r)
    cel(cv, body, '#2F7BFF', off=(r * 0.12, r * 0.14))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    for i in range(6):
        cx = x - r + ((i * r * 0.7 + t * r * 0.08) % (2.6 * r)) - 0.3 * r
        blob(cv, cx, y - r * 0.5 + (i % 3) * r * 0.45, r * (0.28 + 0.06 * (i % 2)), '#3FD07A', seed=i + 3)
    for i in range(4):
        cx = x - r + ((i * r * 0.9 + t * r * 0.14) % (2.6 * r)) - 0.3 * r
        blob(cv, cx, y - r * 0.7 + (i % 2) * r * 0.9, r * 0.2, '#FFFFFF', 190, seed=i + 30, wob=0.4)
    cv.translate(-r * 0.12, -r * 0.14)
    cv.restore()
    oval(cv, x - r * 0.4, y - r * 0.55, r * 0.25, r * 0.12, '#BFF6FF', 160)
    eye(cv, x - r * 0.28, y - r * 0.05, r * 0.2, look, blinkf(t, 3.3))
    eye(cv, x + r * 0.28, y - r * 0.05, r * 0.2, look, blinkf(t, 3.3))
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - r * 0.22, y + r * 0.12, x + r * 0.22, y + r * 0.42), 20, 140)
    cv.drawPath(p, P('#0E2A6A', 255, stroke=r * 0.05))
    for s in (-1, 1):
        oval(cv, x + s * r * 0.5, y + r * 0.2, r * 0.1, r * 0.06, '#FF6F91', 150)


def sun_mascot(cv, x, y, r, t, bored=True):
    glow(cv, x, y, r * 1.8, '#FFB13B', 200)
    cel(cv, circ_path(x, y, r), '#FFC23B', off=(r * 0.1, r * 0.12), hi=(x - r * 0.4, y - r * 0.5, r * 0.25, r * 0.12))
    for s in (-1, 1):
        ex, ey = x + s * r * 0.3, y - r * 0.08
        eye(cv, ex, ey, r * 0.2, (0.3, 0.2), 1.0)
        if bored:
            cv.drawPath(oval_path(ex, ey - r * 0.12, r * 0.22, r * 0.14), P('#FFC23B'))
            cv.drawLine(ex - r * 0.21, ey - r * 0.02, ex + r * 0.21, ey - r * 0.02, P('#C8761F', 255, stroke=r * 0.03))
    cv.drawLine(x - r * 0.15, y + r * 0.35, x + r * 0.15, y + r * 0.33, P('#8A3A10', 255, stroke=r * 0.05))


def bubble_holo(cv, x, y, r, kind, t, a=255):
    cv.drawCircle(x, y, r, P(shader=rad(x - r * 0.3, y - r * 0.3, r * 1.4, ['#C04BFF', '#3C2AA0']), a=a * 0.85))
    cv.save(); cv.clipPath(circ_path(x, y, r), doAntiAlias=True)
    for k in range(-5, 6):
        cv.drawLine(x - r, y + k * r / 5, x + r, y + k * r / 5, P('#FFFFFF', 30 * a / 255, stroke=2))
    cv.restore()
    circle(cv, x, y, r, '#E8D8FF', 220 * a / 255, stroke=4)
    if kind == 'msg':
        rrect(cv, x - r * 0.35, y - r * 0.6, r * 0.7, r * 1.2, r * 0.12, '#1A1030', a)
        rrect(cv, x - r * 0.28, y - r * 0.5, r * 0.56, r * 1.0, r * 0.08, '#9BEFFF', a)
        rrect(cv, x - r * 0.22, y - r * 0.3, r * 0.4, r * 0.16, r * 0.08, '#FFFFFF', a)
        label(cv, x + r * 0.05, y + r * 0.25, 'VU', int(r * 0.2), color='#7A1E4A', a=a, font=FONT, box=False)
    elif kind == 'eyes':
        for dx in (-0.4, 0.0, 0.4):
            for dy in (-0.3, 0.3):
                eye(cv, x + dx * r, y + dy * r, r * 0.13, (math.sin(t + dx * 5), 0.3), 1.0)
                cv.drawLine(x + dx * r - r * 0.14, y + dy * r - r * 0.2, x + dx * r + r * 0.12, y + dy * r - r * 0.14, P('#1A1030', a, stroke=5))
    else:
        cv.save(); cv.translate(x, y); cv.rotate(t * 120)
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(-r * 0.5, -r * 0.5, r * 0.5, r * 0.5), 20, 290)
        cv.drawPath(p, P('#FF4F81', a, stroke=r * 0.12))
        poly(cv, [(r * 0.5, -r * 0.05), (r * 0.62, r * 0.25), (r * 0.32, r * 0.2)], '#FF4F81', a)
        cv.restore()
        cv.drawLine(x - r * 0.18, y - r * 0.18, x + r * 0.18, y + r * 0.18, P('#FFFFFF', a, stroke=r * 0.08))
        cv.drawLine(x + r * 0.18, y - r * 0.18, x - r * 0.18, y + r * 0.18, P('#FFFFFF', a, stroke=r * 0.08))


# 1 ─ « Il y a plus d'étoiles dans l'univers que de grains de sable sur toutes les plages de la Terre. »
class Sand(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        self.st = Stars(260, 701, rmax=2.4, colors=RICH)
        rnd = random.Random(702)
        self.g = [(rnd.uniform(200, 1400), rnd.uniform(0, 1), rnd.uniform(2, 5), rnd.choice(RICH)) for _ in range(260)]

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#3A1460')
        glow(cv, 960, 860, 800, '#7A3CFF', 100)
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, 860); p.quadTo(960, 760, W + 400, 880); p.lineTo(W + 400, H + 400); p.close()
        cel(cv, p, '#E8B86A', off=(0, -30))
        rnd = random.Random(3)
        for _ in range(500):
            circle(cv, rnd.uniform(0, W), rnd.uniform(860, H), rnd.uniform(1.5, 3), '#B8864A', 200)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 210)
        for x, ph, r, c in self.g:
            k = (ph + t * 0.25) % 1.0
            y = 840 - k * 860
            xx = x + 60 * math.sin(k * 6 + x)
            col = mix('#E8B86A', '#FFFFFF', k)
            if k > 0.5:
                sparkle(cv, xx, y, r * 2.4, c, 255 * (1 - k) * 2)
            else:
                circle(cv, xx, y, r, col, 230)
        birdie(cv, 1480, 900, 340, t, body='#FF8A3D', belly='#FFD08A', look=(-0.6, -0.8), mood='wow', facing=-1)


# 2 ─ « Rien que dans notre galaxie, il y a des centaines de milliards d'étoiles. »
class GalaxyHolo(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = Stars(240, 703, rmax=2.2, colors=RICH)
        self.g = Galaxy(704)

    def static(self, cv):
        bg_lin(cv, '#14063A', '#4A0E6A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        holo_hemis(cv, 960, 540, 470, 1.0, t, core=False)
        self.g.draw(cv, 960, 540, t, tilt=0.55, scale=0.85)


# 3 ─ « Et nous ? On n'est même pas au centre. »
class NotCenter(Scene):
    zoom = (1.0, 1.25)
    pan = (0, 0, -140, -40)

    def __init__(self):
        self.g = Galaxy(705, 2000, 620)

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#2A0B5E')

    def dyn(self, cv, t, d):
        self.g.draw(cv, 860, 520, t * 0.5, tilt=0.62, rot=20, scale=1.0)
        cam = Cam(pitch=-58, dist=1800, f=1300, cx=860, cy=520)
        for r in (200, 400, 600):
            pts = [cam.p(r * math.cos(a / 40 * 6.283), 0, r * math.sin(a / 40 * 6.283)) for a in range(41)]
            neon(cv, [(q[0], q[1]) for q in pts], '#2DE2E6', w=2, a=90, glow_w=8)
        sx, sy = 1300, 690
        glow(cv, sx, sy, 60, '#FFE680', 255)
        circle(cv, sx, sy, 10, '#FFFFFF')
        k = (t * 1.5) % 1
        circle(cv, sx, sy, 20 + 60 * k, '#FFD34A', 255 * (1 - k), stroke=5)
        neon(cv, [(1620, 880), (1500, 800), (1340, 715)], '#FF4F81', w=8, arrow=True)
        label(cv, 1660, 930, 'VOUS ÊTES ICI', 30, color='#FF4F81', font=FONT)
        label(cv, 860, 300, 'CENTRE', 26, color='#FFE6B0', font=FONT, box=False)


# 4 ─ « Notre Soleil est perdu dans un petit bras de la galaxie. Une étoile ordinaire, en banlieue. »
class Suburb(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.st = Stars(320, 706, rmax=2.6, colors=RICH)
        rnd = random.Random(707)
        self.o = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(14, 40), rnd.choice(['#FF5A7A', '#6FA8FF', '#FFB13B', '#FFFFFF', '#B98CFF'])) for _ in range(28)]

    def static(self, cv):
        bg_lin(cv, '#1A0A4E', '#3A1460')
        for k in range(5):
            cv.save(); cv.translate(960, 540); cv.rotate(-20)
            oval(cv, 0, 0, 1400, 260 - k * 40, '#B04BFF', 25, blur=40); cv.restore()

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        for x, y, r, c in self.o:
            glow(cv, x, y, r * 3, c, 120)
            cel(cv, circ_path(x, y + 4 * math.sin(t + x), r), c, off=(r * 0.12, r * 0.14))
        sun_mascot(cv, 960, 640, 300, t)


# 5 ─ « Il lui faut deux cent trente millions d'années pour faire un seul tour. »
class Orbit(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.st = Stars(220, 708, rmax=2.2, colors=RICH)
        self.g = Galaxy(709, 1400, 560)

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#2A0B5E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        self.g.draw(cv, 960, 560, t * 0.3, tilt=0.4, scale=1.1, a=170)
        R, ry = 760, 300
        neon(cv, [(960 + R * math.cos(a / 60 * 6.283), 560 + ry * math.sin(a / 60 * 6.283)) for a in range(61)], '#2DE2E6', w=4, a=200)
        k = t / max(d, 0.1)
        ang = 0.4 + k * 0.5
        trail = [(960 + R * math.cos(ang - j * 0.03), 560 + ry * math.sin(ang - j * 0.03)) for j in range(16)]
        neon(cv, trail, '#FFD34A', w=10)
        sx, sy = trail[0]
        glow(cv, sx, sy, 90, '#FFE680', 255); circle(cv, sx, sy, 18, '#FFFFFF')
        years = int(230_000_000 * k)
        label(cv, 960, 980, f'{years:,} ANS'.replace(',', ' '), 36, font=FONT)


# 6 ─ « La dernière fois qu'on était à cet endroit précis, les premiers dinosaures venaient d'apparaître. »
class Dino(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = Stars(260, 710, rmax=2.4, colors=RICH)

    def static(self, cv):
        bg_lin(cv, '#0E0A3A', '#5A1E7A')
        for layer, (col, y0) in enumerate([('#2A0E58', 820), ('#1A0840', 900)]):
            rnd = random.Random(layer)
            for i in range(10):
                blob(cv, rnd.uniform(-100, W + 100), y0 - rnd.uniform(0, 100), rnd.uniform(120, 220), col, seed=i + layer * 20)
            cv.drawRect(skia.Rect.MakeXYWH(-400, y0, W + 800, 800), P(col))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        dino(cv, 700, 1040, 150, t, body='#3FC46A', belly='#B6F07A', mood='wow', look_up=1.0)
        label(cv, 1500, 200, '−230 000 000 ANS', 30, font=FONT)


# 7 ─ « Et autour de cette étoile, un petit caillou bleu. Le nôtre. »
class EarthBig(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = Stars(260, 711, rmax=2.4, colors=RICH)

    def static(self, cv):
        bg_lin(cv, '#06041C', '#2A0A50')
        glow(cv, -100, 200, 700, '#FFB13B', 160)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        earth_mascot(cv, 1000, 760, 340, t, look=(-0.4, 0))
        circle(cv, 1600, 240, 60, '#C7C3E8'); circle(cv, 1620, 225, 14, '#A49FD0')


# 8 ─ « Maintenant, pense à ce qui t'inquiète en ce moment. »
class Worry(Scene):
    zoom = (1.0, 1.15)

    def static(self, cv):
        bg_lin(cv, '#1E0E5A', '#0A0630')
        rrect(cv, 1300, 120, 460, 380, 20, '#3B2A8F'); rrect(cv, 1320, 140, 420, 340, 10, '#0E1250')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#140A3A'))

    def dyn(self, cv, t, d):
        glow(cv, 760, 700, 500, '#5AD7FF', 60 + 20 * math.sin(t * 3))
        birdie(cv, 760, 900, 340, t, body='#2F6BFF', belly='#5AD7FF', look=(0.2, -0.6), mood='calm')
        for s in (-1, 1):
            ex = 760 + 340 * (0.12 if s < 0 else 0.6)
            cv.save(); cv.translate(ex, 900 - 340 * 0.5); cv.rotate(20 * (1 if s < 0 else -1))
            rrect(cv, -50, -9, 100, 18, 9, '#14306A'); cv.restore()
        for i in range(3):
            q = (t * 0.6 + i / 3) % 1
            circle(cv, 1120 + i * 40, 520 - q * 200, 14 + i * 8, '#C8A8FF', 200 * math.sin(q * math.pi))


# 9 ─ « Ce message sans réponse. Ce que les autres pensent de toi. Cette erreur que tu repasses en boucle. »
class Bubbles(Scene):
    zoom = (1.0, 1.08)

    def static(self, cv):
        bg_lin(cv, '#1E0E5A', '#0A0630')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#140A3A'))

    def dyn(self, cv, t, d):
        birdie(cv, 960, 1180, 330, t, body='#2F6BFF', belly='#5AD7FF', look=(0, -1), mood='calm')
        for i, (x, y, kind) in enumerate([(380, 360, 'msg'), (960, 260, 'eyes'), (1540, 360, 'loop')]):
            k = ease_out((t - i * d / 3.2) / 0.5)
            if k > 0:
                bubble_holo(cv, x, y + 12 * math.sin(t * 2 + i), 210 * k, kind, t)


# 10 ─ « Vu d'ici, tout ça tient dans un point minuscule. »
class Pixel(Scene):
    zoom = (1.0, 1.0)

    def __init__(self):
        self.st = Stars(320, 712, rmax=2.4, colors=RICH)

    def static(self, cv):
        bg_lin(cv, '#06041C', '#2A0A50')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        k = ease(t / max(d * 0.85, 0.1))
        s = 1.0 * (1 - k) + 0.012 * k
        cx, cy = 960, 560
        earth_mascot(cv, cx, cy, 380 * s + 3, t)
        for i, kind in enumerate(['msg', 'eyes', 'loop']):
            a = (i - 1) * 0.9 - 1.57
            bubble_holo(cv, cx + math.cos(a) * 600 * s, cy + math.sin(a) * 600 * s, 150 * s + 0.5, kind, t, 255 * (1 - k))
        if k > 0.8:
            r = 40 + 20 * math.sin(t * 6)
            circle(cv, cx, cy, r, '#FF4F81', 220, stroke=4)
            neon(cv, [(cx + 260, cy - 200), (cx + 60, cy - 40)], '#FF4F81', w=5, arrow=True, glow_w=12)


# 11 ─ « Être petit, ce n'est pas une mauvaise nouvelle. C'est une libération. »
class Freedom(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        rnd = random.Random(713)
        self.c = [(rnd.uniform(0, 6.283), rnd.uniform(0.3, 1), rnd.choice(['#FF4F81', '#2DE2E6', '#FFD34A', '#B98CFF', '#FFFFFF'])) for _ in range(160)]

    def static(self, cv):
        bg_rad(cv, 960, 700, 1200, '#FF8AB8', '#5A1E8A')
        for k in range(24):
            cv.save(); cv.translate(960, 700); cv.rotate(k * 15)
            poly(cv, [(0, 0), (1600, -80), (1600, 80)], '#FFFFFF', 30); cv.restore()

    def dyn(self, cv, t, d):
        k = ease_out(t / max(d, 0.1))
        for ang, sp, c in self.c:
            r = 100 + 1100 * ease_out(t / 1.5) * sp
            cv.save(); cv.translate(960 + math.cos(ang) * r, 500 + math.sin(ang) * r * 0.8 + 100 * t); cv.rotate(t * 300 + ang * 50)
            cv.drawRect(skia.Rect.MakeXYWH(-10, -6, 20, 12), P(c)); cv.restore()
        birdie(cv, 960, 900 - 260 * k, 300, t, body='#2F6BFF', belly='#5AD7FF', look=(0, -0.5), mood='happy', wing=math.sin(t * 14))


# 12 ─ « Tes erreurs ne sont pas si graves. Tes peurs ne sont pas si grandes. »
class Shrink(Scene):
    zoom = (1.0, 1.08)

    def static(self, cv):
        bg_lin(cv, '#3A1A7A', '#7A2A8A')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#2A0E58'))

    def dyn(self, cv, t, d):
        k = ease((t - 0.4) / max(d * 0.7, 0.1))
        s = 1 - 0.85 * k
        mx, my = 1300, 900
        r = 420 * s
        body = skia.Path(); body.addCircle(mx, my - r, r)
        cel(cv, body, '#2A0E3A', off=(r * 0.1, r * 0.12))
        for sx in (-0.35, 0.35):
            eye(cv, mx + sx * r, my - r * 1.2, r * 0.18, (-0.6, 0.2), 1.0, iris='#FFD34A')
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(mx - r * 0.3, my - r * 0.85, mx + r * 0.3, my - r * 0.55), 200 if k < 0.6 else 20, 140)
        cv.drawPath(p, P('#FFD34A', 255, stroke=max(3, r * 0.05)))
        birdie(cv, 620, 860, 300, t * (1 + k), body='#FF8A3D', belly='#FFD08A', look=(1, 0.3), mood='happy' if k > 0.5 else 'calm')


# 13 ─ « Et pourtant, sur ce petit caillou, tu peux rire, aimer, créer, et admirer les étoiles. »
class Joys(Scene):
    zoom = (1.0, 1.1)
    pan = (40, 0, -40, 0)

    def __init__(self):
        self.st = Stars(200, 714, rmax=2.4, colors=RICH)

    def static(self, cv):
        bg_lin(cv, '#1A0A4E', '#FF8A8A')
        glow(cv, 960, 860, 700, '#FFD08A', 160)
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, 900); p.quadTo(960, 780, W + 400, 900); p.lineTo(W + 400, H + 400); p.close()
        cel(cv, p, '#3FA86A', off=(0, -30))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 160)
        birdie(cv, 260, 880, 170, t * 2, body='#FFD34A', belly='#FFF0B0', mood='happy', wing=math.sin(t * 10))
        for k in range(3):
            q = (t * 0.9 + k / 3) % 1
            label(cv, 330 + k * 40, 640 - q * 140, 'HA', 34, color='#7A1E4A', a=255 * math.sin(q * math.pi), font=FONT, box=False)
        birdie(cv, 700, 900, 160, t, body='#FF4F81', belly='#FFB0C8', mood='happy', look=(1, 0))
        birdie(cv, 900, 900, 160, t + 0.5, body='#2F6BFF', belly='#5AD7FF', mood='happy', look=(-1, 0), facing=-1)
        heart_y = 650 + 10 * math.sin(t * 4)
        circle(cv, 780, heart_y, 30, '#FF4F81'); circle(cv, 820, heart_y, 30, '#FF4F81'); poly(cv, [(752, heart_y + 8), (848, heart_y + 8), (800, heart_y + 62)], '#FF4F81')
        rrect(cv, 1180, 620, 200, 160, 10, '#FFF8EE')
        for i, c in enumerate(['#FF4F81', '#2DE2E6', '#FFD34A']):
            blob(cv, 1230 + i * 50, 700, 34, c, 220, seed=i + 1)
        birdie(cv, 1300, 920, 150, t, body='#8A4BFF', belly='#C8A8FF', mood='calm', look=(-0.5, -0.5))
        birdie(cv, 1680, 930, 170, t, body='#2DE2C6', belly='#BFF6FF', mood='wow', look=(0, -1))


# 14 ─ « L'univers est immense. Mais c'est ici, et maintenant, que tu as la chance de vivre. »
class HereNow(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = Stars(320, 715, rmax=2.6, colors=RICH)

    def static(self, cv):
        bg_lin(cv, '#06041C', '#3A0E6A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        earth_mascot(cv, 960, 1480, 800, t * 0.5, look=(0, -1))
        for i, (a, col) in enumerate([(-0.35, '#FFD34A'), (-0.12, '#FF4F81'), (0.12, '#8A4BFF'), (0.35, '#FF8A3D')]):
            x = 960 + math.sin(a) * 820
            y = 1480 - math.cos(a) * 820
            cv.save(); cv.translate(x, y); cv.rotate(math.degrees(a))
            birdie(cv, 0, -60, 60, t * 2 + i, body=col, belly='#FFFFFF', mood='happy', look=(0, -1), wing=math.sin(t * 8 + i))
            cv.restore()


# 15 ─ « Alors profite du voyage. »
class Ride(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        self.st = Stars(320, 716, rmax=2.6, colors=RICH)
        rnd = random.Random(717)
        self.conf = [(rnd.uniform(0, W), rnd.uniform(-H, 0), rnd.uniform(150, 300), rnd.uniform(0, 360), rnd.choice(['#FF4F81', '#2DE2E6', '#FFD34A', '#B98CFF', '#ffffff'])) for _ in range(120)]

    def static(self, cv):
        bg_lin(cv, '#14063A', '#7A1A8A')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        sun_mascot(cv, 960, 560, 150, t, bored=False)
        R, ry = 760, 300
        neon(cv, [(960 + R * math.cos(a / 60 * 6.283), 560 + ry * math.sin(a / 60 * 6.283)) for a in range(61)], '#2DE2E6', w=5, a=220)
        ang = 1.2 + t * 0.6
        ex, ey = 960 + R * math.cos(ang), 560 + ry * math.sin(ang)
        trail = [(960 + R * math.cos(ang - j * 0.04), 560 + ry * math.sin(ang - j * 0.04)) for j in range(14)]
        neon(cv, trail, '#FFD34A', w=12)
        earth_mascot(cv, ex, ey, 150, t)
        for i, col in enumerate(['#FFD34A', '#FF4F81', '#8A4BFF']):
            birdie(cv, ex - 70 + i * 70, ey - 170, 34, t * 3 + i, body=col, belly='#FFFFFF', mood='happy', wing=math.sin(t * 12 + i))
        for x, y, sp, rot, c in self.conf:
            yy = y + t * sp
            if yy < -20:
                continue
            cv.save(); cv.translate(x + 30 * math.sin(t * 2 + rot), yy % (H + 40)); cv.rotate(rot + t * 200)
            cv.drawRect(skia.Rect.MakeXYWH(-9, -5, 18, 10), P(c)); cv.restore()


SEGMENTS = [
    (Sand, "Il y a plus d'étoiles dans l'univers que de grains de sable sur toutes les plages de la Terre."),
    (GalaxyHolo, "Rien que dans notre galaxie, il y a des centaines de milliards d'étoiles."),
    (NotCenter, "Et nous ? On n'est même pas au centre."),
    (Suburb, "Notre Soleil est perdu dans un petit bras de la galaxie. Une étoile ordinaire, en banlieue."),
    (Orbit, "Il lui faut deux cent trente millions d'années pour faire un seul tour."),
    (Dino, "La dernière fois qu'on était à cet endroit précis, les premiers dinosaures venaient d'apparaître."),
    (EarthBig, "Et autour de cette étoile, un petit caillou bleu. Le nôtre."),
    (Worry, "Maintenant, pense à ce qui t'inquiète en ce moment."),
    (Bubbles, "Ce message sans réponse. Ce que les autres pensent de toi. Cette erreur que tu repasses en boucle."),
    (Pixel, "Vu d'ici, tout ça tient dans un point minuscule."),
    (Freedom, "Être petit, ce n'est pas une mauvaise nouvelle. C'est une libération."),
    (Shrink, "Tes erreurs ne sont pas si graves. Tes peurs ne sont pas si grandes."),
    (Joys, "Et pourtant, sur ce petit caillou, tu peux rire, aimer, créer, et admirer les étoiles."),
    (HereNow, "L'univers est immense. Mais c'est ici, et maintenant, que tu as la chance de vivre."),
    (Ride, "Alors profite du voyage."),
]

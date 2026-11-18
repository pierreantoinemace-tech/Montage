"""« La dernière fois » : 17 plans, style v2 + texte lisible (halo sombre / crème plein selon le fond)."""
import math, os, random, sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(HERE, '..', 'calendrier'))
sys.path.insert(1, os.path.join(HERE, '..', 'inconnus'))
from lib import *
from kit import *
import importlib.util
_s = importlib.util.spec_from_file_location('inc_scenes', os.path.join(HERE, '..', 'inconnus', 'scenes.py'))
inc = importlib.util.module_from_spec(_s); _s.loader.exec_module(inc)
heart, bubble, icon_draw, person, street_bg = inc.heart, inc.bubble, inc.icon_draw, inc.person, inc.street_bg

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7, readable=True)
YOU = dict(top='#FF4F81', hair='#2A1A14', skin='#C98058', pants='#2B2A7A', hairstyle=0)
KID = dict(top='#FFD34A', hair='#2A1A14', skin='#C98058', pants='#3C4CC8', hairstyle=0)
MOM = dict(top='#2DE2C6', hair='#5A2A14', skin='#C98058', pants='#3A1E5A', hairstyle=2)
DAD = dict(top='#3C4CC8', hair='#C8C8D8', skin='#C98058', pants='#1E1F5C', hairstyle=0)


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


def motes(cv, t, n=60, seed=1, col='#FFE6A0', area=(0, 0, W, H)):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(area[0], area[2]); y = rnd.uniform(area[1], area[3]); r = rnd.uniform(2, 5); ph = rnd.uniform(0, 6)
        xx = x + 30 * math.sin(t * 0.5 + ph); yy = y - (t * 14 + ph * 30) % 200
        circle(cv, xx, yy, r, col, 120 + 100 * math.sin(t * 2 + ph))


def living_room(cv):
    bg_lin(cv, '#FFB86B', '#C8506A')
    rrect(cv, 1180, 120, 560, 520, 20, '#FFE6A0')
    cv.drawRect(skia.Rect.MakeXYWH(1450, 120, 16, 520), P('#C8506A'))
    cv.drawRect(skia.Rect.MakeXYWH(1180, 370, 560, 16), P('#C8506A'))
    poly(cv, [(1180, 120), (1740, 120), (1300, 1100), (500, 1100)], '#FFF0B0', 60, blur=30)
    cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#8A3A5A'))
    rrect(cv, 200, 200, 220, 170, 10, '#FFFFFF'); rrect(cv, 214, 214, 192, 142, 6, '#FF8AB8')
    rrect(cv, 140, 640, 520, 260, 50, '#7A3A8A'); rrect(cv, 100, 600, 120, 300, 50, '#6A2A7A'); rrect(cv, 600, 600, 120, 300, 50, '#6A2A7A')
    rrect(cv, 1560, 740, 120, 160, 20, '#3A8A6A')
    for k in range(5):
        blob(cv, 1620 + (k - 2) * 40, 690 - (k % 2) * 50, 50, '#3FC46A', seed=k)


def hold_child(cv, x, y, s, t, mom=MOM, kid=KID, mood_mom='happy', mood_kid='happy'):
    char_front(cv, x, y, s, t, mood=mood_mom, look=(0, 0.5), **mom)
    ty = y - 3.15 * s
    char_front(cv, x + 0.1 * s, ty + 2.1 * s, s * 0.5, t * 1.3, mood=mood_kid, arms='up', bob=False, **kid)
    dark = mix(mom['top'], '#000000', 0.2)
    rrect(cv, x - 1.0 * s, ty + 1.05 * s, 2.0 * s, 0.42 * s, 0.21 * s, dark)
    circle(cv, x + 0.75 * s, ty + 1.26 * s, 0.22 * s, mom['skin'])


def polaroid(cv, x, y, w, rot, inner, a=255):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    rrect(cv, -w / 2 + 8, -w * 0.6 + 12, w, w * 1.2, 8, '#000000', 60 * a / 255)
    rrect(cv, -w / 2, -w * 0.6, w, w * 1.2, 8, '#FFF8EE', a)
    cv.save(); cv.clipRect(skia.Rect.MakeXYWH(-w * 0.43, -w * 0.52, w * 0.86, w * 0.86))
    inner(cv, w)
    cv.restore(); cv.restore()


def _mini_room(cv, w):
    cv.drawRect(skia.Rect.MakeXYWH(-w, -w, 2 * w, 2 * w), P(shader=lin(0, -w / 2, 0, w / 2, ['#FFB86B', '#C8506A'])))
    hold_child(cv, 0, w * 0.45, w * 0.1, 0)


# 1 ─ « Un jour, ta mère t'a porté dans ses bras pour la dernière fois. »
class Carry(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        living_room(cv)

    def dyn(self, cv, t, d):
        motes(cv, t, 70, 3)
        sway = 2 * math.sin(t * 1.2)
        cv.save(); cv.translate(960, 1070); cv.rotate(sway); cv.translate(-960, -1070)
        hold_child(cv, 960, 1070, 78, t)
        cv.restore()


# 2 ─ « Et aucun de vous deux ne le savait. »
class NoOneKnew(Scene):
    zoom = (1.0, 1.06)

    def __init__(self):
        self.st = Stars(220, 502)
        rnd = random.Random(503)
        self.ph = [(rnd.uniform(100, W - 100), rnd.uniform(80, 500), rnd.uniform(-15, 15), rnd.uniform(70, 120)) for _ in range(14)]

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#3A1460')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        for i, (x, y, rot, w) in enumerate(self.ph):
            a = ease((t - i * 0.12) / 0.4)
            if a > 0:
                glow(cv, x, y, w, '#FFE6A0', 60 * a)
                polaroid(cv, x, y + 6 * math.sin(t + i), w, rot, lambda cv, w: cv.drawRect(skia.Rect.MakeXYWH(-w, -w, 2 * w, 2 * w), P(['#FFB86B', '#FF8AB8', '#2DE2C6', '#FFD34A'][i % 4])), 255 * a)
        k = ease_out(t / max(d, 0.1))
        polaroid(cv, 960, 760 - 260 * k, 420 - 120 * k, -4 + 6 * k, _mini_room)


# 3 ─ « Un jour, tu as joué dehors avec tes amis d'enfance pour la dernière fois. »
class Play(Scene):
    zoom = (1.0, 1.1)
    pan = (50, 0, -50, 0)

    def static(self, cv):
        street_bg(cv, sky=('#5A2A8A', '#FF9A5C'), seed=21, ground='#6A2A5A')
        glow(cv, 960, 640, 500, '#FFD34A', 160)
        circle(cv, 960, 680, 160, '#FFE680')

    def dyn(self, cv, t, d):
        kids = [dict(KID), dict(top='#2DB8FF', hair='#E0A030', skin='#FFD0B0', pants='#1E1F5C', hairstyle=1),
                dict(top='#3FC46A', hair='#1A1030', skin='#8A5236', pants='#3A1E5A', hairstyle=0), dict(top='#FF8A3D', hair='#B04A1A', skin='#F2A97E', pants='#2B2A7A', hairstyle=2)]
        bx = 960 + 520 * math.sin(t * 1.4)
        by = 960 - abs(math.sin(t * 4)) * 220
        for i, kd in enumerate(kids):
            x = 960 + 600 * math.sin(t * 1.4 - 0.5 - i * 0.6) * (0.6 + 0.15 * i)
            char_front(cv, x, 1010 - (i % 2) * 40, 46, t * 3 + i, mood='laugh', arms='up' if i % 2 else 'out', **kd)
        oval(cv, bx, 1000, 40, 10, '#000000', 60)
        shade_ball(cv, bx, by, 38, '#FFFFFF', '#FF4F81')


# 4 ─ « Vous vous êtes dit : à demain. »
class SeeYou(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        street_bg(cv, sky=('#3A1A7A', '#FF7A6A'), seed=21, ground='#5A2A5A')
        glow(cv, 960, 720, 420, '#FFB86B', 160)

    def dyn(self, cv, t, d):
        k = ease(t / max(d, 0.1))
        char_front(cv, 760 - 300 * k, 1010, 50, t * 2, mood='happy', arms='wave', **KID)
        char_front(cv, 1160 + 300 * k, 1010, 50, t * 2 + 1, mood='happy', arms='wave', top='#2DB8FF', hair='#E0A030', skin='#FFD0B0', pants='#1E1F5C', hairstyle=1)
        for x, s in ((760 - 300 * k, 1), (1160 + 300 * k, -1)):
            bx, by = x + s * 140, 640
            rrect(cv, bx - 140, by - 50, 280, 90, 45, '#FFFFFF')
            poly(cv, [(bx - s * 60, by + 30), (bx - s * 110, by + 80), (bx - s * 20, by + 38)], '#FFFFFF')
            label(cv, bx, by + 14, 'À DEMAIN !', 34, color='#7A1E4A', font=FONT, box=False)
        shade_ball(cv, 960, 990, 34, '#FFFFFF', '#FF4F81')


# 5 ─ « Et ce demain n'est jamais venu. »
class NeverCame(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        rnd = random.Random(505)
        self.leaves = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(80, 200), rnd.uniform(0, 6)) for _ in range(40)]

    def static(self, cv):
        street_bg(cv, sky=('#1A0E4A', '#6A4A8A'), seed=21, ground='#2A1A4A')

    def dyn(self, cv, t, d):
        for x, y, sp, ph in self.leaves:
            xx = (x + t * sp) % (W + 200) - 100
            yy = y + 40 * math.sin(t * 2 + ph) + t * 30
            cv.save(); cv.translate(xx, yy % H); cv.rotate(t * 90 + ph * 50)
            oval(cv, 0, 0, 16, 8, ['#FF8A3D', '#FFB13B', '#C8506A'][int(ph) % 3]); cv.restore()
        for i in range(5):
            q = (t * 0.5 + i / 5) % 1
            calendar_page(cv, 1400 + q * 600, 300 - q * 200 + i * 40, 120, 140, 'DEMAIN', '?', '#7A4BFF', FONT, 255 * (1 - q))
        oval(cv, 960, 1000, 40, 10, '#000000', 80)
        shade_ball(cv, 960, 966, 34, '#E8E0F0', '#8A5A8A')
        glow(cv, 960, 960, 120, '#FFE6A0', 60)


# 6 ─ « Il y a eu une dernière histoire avant de dormir. Un dernier jour d'école. Un dernier appel de ton grand-père. »
class Three(Scene):
    zoom = (1.0, 1.06)

    def static(self, cv):
        bg_lin(cv, '#1A0A4E', '#4A1270')

    def _panel(self, cv, i, x, y, w, h, t):
        cv.save()
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 30, 30)
        cv.clipRRect(rr, doAntiAlias=True)
        if i == 0:
            cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), P(shader=lin(x, y, x, y + h, ['#2A1A6A', '#120838'])))
            glow(cv, x + 120, y + 200, 260, '#FFD34A', 200)
            rrect(cv, x + 90, y + 160, 60, 140, 10, '#FFD34A'); poly(cv, [(x + 60, y + 170), (x + 180, y + 170), (x + 150, y + 110), (x + 90, y + 110)], '#FFE680')
            rrect(cv, x + 40, y + 430, w - 80, 200, 40, '#3A3A9A')
            char_front(cv, x + 290, y + 620, 30, t, mood='happy', look=(1, 0), **KID)
            poly(cv, [(x + 330, y + 480), (x + 420, y + 450), (x + 420, y + 540), (x + 330, y + 560)], '#FFF8EE')
            poly(cv, [(x + 420, y + 450), (x + 510, y + 480), (x + 510, y + 560), (x + 420, y + 540)], '#F0E6D8')
        elif i == 1:
            cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), P(shader=lin(x, y, x, y + h, ['#FFB86B', '#FF7A6A'])))
            rrect(cv, x + 60, y + 120, w - 120, 300, 20, '#C8506A')
            label(cv, x + w / 2, y + 180, 'ÉCOLE', 40, color='#FFFFFF', font=FONT, box=False)
            for k in range(9):
                rrect(cv, x + 50 + k * 55, y + 330, 14, 300, 7, '#3A1A5A')
            cv.drawRect(skia.Rect.MakeXYWH(x + 40, y + 330, w - 80, 14), P('#3A1A5A'))
            rrect(cv, x + 200, y + 470, 160, 150, 30, '#2DB8FF'); rrect(cv, x + 230, y + 440, 100, 50, 20, '#2A7ACC', 255, stroke=14)
        else:
            cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), P(shader=lin(x, y, x, y + h, ['#3FC46A', '#1A6A5A'])))
            ring = math.sin(t * 30) * 8 if (t % 1.2) < 0.6 else 0
            cv.save(); cv.translate(x + w / 2 + ring, y + 360)
            rrect(cv, -150, -60, 300, 160, 30, '#E8243C'); rrect(cv, -170, -110, 340, 70, 35, '#C81A30')
            circle(cv, 0, 20, 50, '#FFF8EE'); circle(cv, 0, 20, 18, '#C81A30')
            cv.restore()
            for k in range(3):
                pp = skia.Path(); pp.addArc(skia.Rect.MakeLTRB(x + w / 2 - 200 - k * 30, y + 200 - k * 30, x + w / 2 + 200 + k * 30, y + 520 + k * 30), -60, 120)
                cv.drawPath(pp, P('#FFFFFF', 180 if ring else 60, stroke=6))
            label(cv, x + w / 2, y + 600, 'PAPI', 34, color='#FFFFFF', font=FONT)
        cv.restore()
        cv.drawRRect(rr, P('#FFFFFF', 255, stroke=10))

    def dyn(self, cv, t, d):
        w, h = 560, 680
        for i in range(3):
            k = ease_out((t - i * d / 3.0) / 0.45)
            if k <= 0:
                continue
            x = 60 + i * 610; y = 200 + (1 - k) * 760
            cv.save(); cv.translate(x + w / 2, y + h / 2); cv.rotate((i - 1) * 3); cv.translate(-(x + w / 2), -(y + h / 2))
            self._panel(cv, i, x, y, w, h, t)
            cv.restore()


# 7 ─ « Personne ne t'a prévenu. La vie ne prévient jamais. »
class Hourglass(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        self.st = Stars(200, 507)
        rnd = random.Random(508)
        self.g = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.choice(['#FF4F81', '#FFD34A', '#2DE2E6', '#B6FF3B', '#FFFFFF'])) for _ in range(160)]

    def static(self, cv):
        bg_lin(cv, '#0A0630', '#2A0B5E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        cx, cy = 960, 540
        cam = Cam(yaw=t * 25, pitch=-12, dist=1500, f=1400, cx=cx, cy=cy)
        for yy, rr in ((-380, 260), (380, 260)):
            pts = [cam.p(rr * math.cos(a / 30 * 6.283), yy, rr * math.sin(a / 30 * 6.283)) for a in range(31)]
            neon(cv, [(q[0], q[1]) for q in pts], '#B98CFF', w=4)
        for j in range(12):
            a = j / 12 * 6.283
            pts = []
            for k in range(21):
                u = -1 + 2 * k / 20
                r = 30 + 230 * abs(u) ** 1.3
                q = cam.p(r * math.cos(a), u * 380, r * math.sin(a)); pts.append((q[0], q[1]))
            neon(cv, pts, '#7A5BFF', w=2, a=160, glow_w=8)
        for ph, dx, c in self.g:
            k = (ph + t * 0.35) % 1.0
            if k < 0.5:
                y = cy + 380 * (k / 0.5) ** 2 - 20
                x = cx + dx * 8
            else:
                y = cy + 360 - (k - 0.5) * 60; x = cx + dx * 200 * (k - 0.5) * 2
            circle(cv, x, y, 5, c, 230)
        k = ease(t / max(d, 0.1))
        p = skia.Path(); p.moveTo(cx - 200 * (1 - k), cy - 330 + 300 * k); p.lineTo(cx + 200 * (1 - k), cy - 330 + 300 * k); p.lineTo(cx, cy - 20); p.close()
        cv.drawPath(p, P('#FFD34A', 160))
        p = skia.Path(); p.moveTo(cx - 220 * k, cy + 370 - 120 * k); p.lineTo(cx + 220 * k, cy + 370 - 120 * k); p.lineTo(cx + 240, cy + 370); p.lineTo(cx - 240, cy + 370); p.close()
        cv.drawPath(p, P('#FFD34A', 160))


# 8 ─ « Et ça continue, en ce moment. »
class Now(Scene):
    zoom = (1.15, 1.0)

    def static(self, cv):
        street_bg(cv, sky=('#06041C', '#2A0A50'), seed=28, ground='#140A30')

    def dyn(self, cv, t, d):
        cx, cy, R = 960, 380, 300
        glow(cv, cx, cy, 500, '#2DE2E6', 110)
        circle(cv, cx, cy, R, '#2DE2E6', 200, stroke=8)
        for i in range(12):
            a = math.radians(i * 30 - 90)
            cv.drawLine(cx + math.cos(a) * (R - 40), cy + math.sin(a) * (R - 40), cx + math.cos(a) * (R - 10), cy + math.sin(a) * (R - 10), P('#2DE2E6', 255, stroke=8))
        for sp, ln, c, w in ((0.3, 0.5, '#FFD34A', 14), (2.0, 0.75, '#FF4F81', 8), (12, 0.85, '#FFFFFF', 3)):
            a = t * sp - 1.57
            neon(cv, [(cx, cy), (cx + math.cos(a) * R * ln, cy + math.sin(a) * R * ln)], c, w=w)
        label(cv, cx, cy + R + 70, 'MAINTENANT', 30, font=FONT)
        char_front(cv, 960, 1020, 70, t, mood='calm', look=(0, -1), **YOU)


# 9 ─ « Il y aura une dernière fois où tu prendras ton père dans tes bras. »
class Father(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        bg_lin(cv, '#FF9A5C', '#7A2A6A')
        rrect(cv, 300, 120, 1320, 820, 20, '#C8706A')
        rrect(cv, 820, 260, 280, 640, 14, '#5A2A4A'); circle(cv, 1060, 600, 14, '#FFD34A')
        for x in (420, 1240):
            rrect(cv, x, 280, 260, 220, 10, '#FFE6A0')
        poly(cv, [(240, 140), (1680, 140), (960, -120)], '#7A2A4A')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 940, W + 800, 600), P('#5A2A4A'))

    def dyn(self, cv, t, d):
        k = ease(t / 1.2)
        g = 1 + 0.02 * math.sin(t * 2)
        char_front(cv, 1040 - 60 * k, 1070, 74 * g, t, mood='happy', arms='hug', **DAD)
        char_front(cv, 880 + 60 * k, 1070, 70 * g, t + 0.3, mood='happy', arms='hug', **YOU)
        for i in range(6):
            q = (t * 0.4 + i / 6) % 1
            heart(cv, 960 + 160 * math.sin(i * 2 + q * 4), 640 - q * 400, 22, '#FF4F81', 255 * math.sin(q * math.pi))
        motes(cv, t, 40, 9)


# 10 ─ « Un dernier fou rire avec ton meilleur ami. »
class Laugh(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        bg_lin(cv, '#2DB8FF', '#BFF6FF')
        for k in range(6):
            cloud(cv, 160 + k * 330, 160 + (k % 2) * 80, 70, '#FFFFFF', 230, shade='#D0E8FF')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 820, W + 800, 600), P('#3FC46A'))
        rrect(cv, 520, 760, 880, 40, 14, '#8A4A1A'); rrect(cv, 520, 680, 880, 30, 12, '#A85A2A')
        for x in (560, 1340):
            rrect(cv, x, 800, 24, 140, 8, '#5A2A1A')

    def dyn(self, cv, t, d):
        shake = 6 * math.sin(t * 25)
        char_front(cv, 780 + shake, 960, 62, t * 3, mood='laugh', arms='up', **YOU)
        char_front(cv, 1140 - shake, 960, 64, t * 3 + 1, mood='laugh', arms='out', top='#FFD34A', hair='#1A1030', skin='#8A5236', pants='#1E1F5C', hairstyle=1)
        for k in range(8):
            q = (t * 0.9 + k / 8) % 1
            x = 960 + (k - 3.5) * 120
            label(cv, x, 520 - q * 300, 'HA', 44, color='#7A1E4A', a=255 * math.sin(q * math.pi), font=FONT, box=False)


# 11 ─ « Un dernier repas tous ensemble. »
class Dinner(Scene):
    zoom = (1.0, 1.08)

    def static(self, cv):
        bg_lin(cv, '#3A1A6A', '#C8506A')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#2A1450'))

    def dyn(self, cv, t, d):
        p = skia.Path(); p.moveTo(-50, 120); p.quadTo(960, 330, W + 50, 120)
        cv.drawPath(p, P('#140630', 255, stroke=4))
        for k in range(24):
            u = k / 23; x = -50 + (W + 100) * u
            y = (1 - u) ** 2 * 120 + 2 * u * (1 - u) * 330 + u ** 2 * 120
            c = ['#FFD34A', '#FFE6A0'][k % 2]
            glow(cv, x, y + 14, 50, c, 200); circle(cv, x, y + 14, 10, c)
        fam = [MOM, DAD, KID, dict(top='#7A4BFF', hair='#C8C8D8', skin='#FFD0B0', pants='#3A1E5A', hairstyle=1), YOU, dict(top='#3FC46A', hair='#B04A1A', skin='#F2A97E', pants='#1E1F5C', hairstyle=2)]
        for i, f in enumerate(fam):
            char_front(cv, 360 + i * 240, 1040, 56, t * 1.5 + i, mood='laugh' if (i + int(t)) % 3 == 0 else 'happy', arms='up' if i == 4 and t % 2 < 1 else 'down', **f)
        rrect(cv, 180, 880, 1560, 60, 20, '#FFF8EE'); cv.drawRect(skia.Rect.MakeXYWH(180, 930, 1560, 160), P('#E8E0F0'))
        for i in range(7):
            x = 300 + i * 220
            oval(cv, x, 890, 70, 18, '#FFFFFF'); blob(cv, x, 880, 34, ['#FF8A3D', '#3FC46A', '#FFD34A', '#C8506A'][i % 4], seed=i)
        for i in range(3):
            q = (t * 0.6 + i / 3) % 1
            circle(cv, 960 + 30 * math.sin(q * 6), 860 - q * 140, 14 * (1 - q) + 4, '#FFFFFF', 150 * (1 - q))


# 12 ─ « Tu ne sais pas quand. »
class DontKnow(Scene):
    zoom = (1.0, 1.15)

    def static(self, cv):
        bg_lin(cv, '#06041C', '#1E0A40')

    def dyn(self, cv, t, d):
        poly(cv, [(900, -50), (1020, -50), (1200, 1040), (720, 1040)], '#E8E4FF', 30, blur=20)
        oval(cv, 960, 1040, 260, 40, '#E8E4FF', 60, blur=10)
        for i in range(7):
            a = i * 0.9 + t * 0.3
            x, y, r = 960 + 650 * math.cos(a), 480 + 300 * math.sin(a * 1.3), 70 + (i % 3) * 20
            circle(cv, x, y, r, '#B98CFF', 120, stroke=4)
            for h, ln in ((t * (0.5 + i * 0.3), 0.5), (t * (3 + i), 0.8)):
                cv.drawLine(x, y, x + math.cos(h) * r * ln, y + math.sin(h) * r * ln, P('#B98CFF', 160, stroke=4))
        char_front(cv, 960, 1040, 64, t, mood='calm', look=(0, -1), **YOU)


# 13 ─ « Et c'est peut-être ça, le plus beau. »
class Beautiful(Scene):
    zoom = (1.0, 1.12)

    def __init__(self):
        rnd = random.Random(513)
        self.fl = [(rnd.uniform(0, W), rnd.uniform(860, 1060), rnd.uniform(0, 1), rnd.choice(['#FF4F81', '#FFD34A', '#FFFFFF', '#B98CFF'])) for _ in range(70)]

    def static(self, cv):
        bg_lin(cv, '#FF9AB8', '#FFE0A0')
        glow(cv, 960, 760, 640, '#FFFFFF', 160)
        circle(cv, 960, 800, 200, '#FFF6D0')
        p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, 840); p.quadTo(960, 760, W + 400, 840); p.lineTo(W + 400, H + 400); p.close()
        cv.drawPath(p, P('#3FC46A'))

    def dyn(self, cv, t, d):
        for x, y, ph, c in self.fl:
            k = ease_out((t - ph * d * 0.6) / 0.5)
            if k <= 0:
                continue
            cv.drawLine(x, y, x, y - 40 * k, P('#2E8A55', 255, stroke=5))
            for j in range(5):
                a = j * 1.256 + t * 0.5
                circle(cv, x + math.cos(a) * 12 * k, y - 40 * k + math.sin(a) * 12 * k, 9 * k, c)
            circle(cv, x, y - 40 * k, 6 * k, '#FFD34A')
        for i in range(3):
            bx = (300 + i * 500 + t * 80) % (W + 200) - 100
            by = 300 + i * 60 + 20 * math.sin(t * 3 + i)
            wv = 18 * math.sin(t * 12 + i)
            oval(cv, bx - 18, by - wv * 0.3, 18, 10 + abs(wv) * 0.4, '#FF8AB8'); oval(cv, bx + 18, by - wv * 0.3, 18, 10 + abs(wv) * 0.4, '#FF8AB8')
            oval(cv, bx, by, 4, 14, '#7A1E4A')


# 14 ─ « Parce que si chaque instant peut être le dernier, alors chaque instant compte. »
class Fireflies(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        rnd = random.Random(514)
        self.f = [(rnd.uniform(0, W), rnd.uniform(150, 1000), rnd.uniform(0, 1), rnd.uniform(0, 6)) for _ in range(400)]
        self.st = Stars(160, 515)

    def static(self, cv):
        bg_lin(cv, '#06041C', '#1A2A5A')
        for i, (col, y) in enumerate([('#0E1A3A', 820), ('#0A1430', 900)]):
            p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, y); p.quadTo(960, y - 100 + i * 40, W + 400, y); p.lineTo(W + 400, H + 400); p.close()
            cv.drawPath(p, P(col))

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 160)
        k = t / max(d, 0.1)
        for x, y, on, ph in self.f:
            if on > k * 1.1:
                continue
            xx = x + 30 * math.sin(t * 0.7 + ph); yy = y + 20 * math.cos(t * 0.9 + ph)
            a = 0.5 + 0.5 * math.sin(t * 3 + ph)
            glow(cv, xx, yy, 26, '#D8FF6B', 140 * a)
            circle(cv, xx, yy, 4, '#F4FFB0', 255 * a)
        char_front(cv, 960, 980, 60, t, mood='wow', look=(0, -1), **YOU)


# 15 ─ « Alors appelle-les. Serre-les un peu plus fort. Ris un peu plus longtemps. »
class CallHug(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        living_room(cv)

    def dyn(self, cv, t, d):
        motes(cv, t, 50, 15)
        third = d / 3
        if t < third:
            char_front(cv, 960, 1070, 76, t, mood='happy', arms='wave', **YOU)
            rrect(cv, 1040, 640, 44, 80, 10, '#1A1030'); rrect(cv, 1045, 646, 34, 66, 7, '#9BEFFF')
            for k in range(3):
                pp = skia.Path(); pp.addArc(skia.Rect.MakeLTRB(1000 - k * 30, 470 - k * 30, 1150 + k * 30, 650 + k * 30), -60, 120)
                cv.drawPath(pp, P('#FFFFFF', 200 - 50 * k, stroke=6))
            bubble(cv, 1300, 400 + 10 * math.sin(t * 3), 90, 'heart', t)
        elif t < 2 * third:
            g = 1 + 0.03 * math.sin(t * 6)
            char_front(cv, 1040, 1070, 72 * g, t, mood='happy', arms='hug', **MOM)
            char_front(cv, 880, 1070, 72 * g, t, mood='happy', arms='hug', **YOU)
            for i in range(8):
                q = (t * 0.6 + i / 8) % 1
                heart(cv, 960 + 260 * math.sin(i * 1.7 + q * 3), 640 - q * 460, 26, '#FF4F81', 255 * math.sin(q * math.pi))
        else:
            char_front(cv, 780, 1070, 68, t * 3, mood='laugh', arms='up', **YOU)
            char_front(cv, 1140, 1070, 68, t * 3 + 1, mood='laugh', arms='out', top='#FFD34A', hair='#1A1030', skin='#8A5236', pants='#1E1F5C', hairstyle=1)
            for k in range(6):
                q = (t * 0.9 + k / 6) % 1
                label(cv, 960 + (k - 2.5) * 150, 520 - q * 300, 'HA', 44, color='#7A1E4A', a=255 * math.sin(q * math.pi), font=FONT, box=False)


# 16 ─ « Tu ne sais pas quelle fois sera la dernière. »
class ParkAgain(Scene):
    zoom = (1.15, 1.0)

    def static(self, cv):
        street_bg(cv, sky=('#5A2A8A', '#FF9A5C'), seed=21, ground='#6A2A5A')
        glow(cv, 960, 640, 500, '#FFD34A', 160)
        circle(cv, 960, 680, 160, '#FFE680')

    def dyn(self, cv, t, d):
        k = ease(t / max(d, 0.1))
        bx = 1700 - 900 * k
        oval(cv, bx, 1000, 40, 10, '#000000', 60)
        cv.save(); cv.translate(bx, 966); cv.rotate(-k * 720)
        shade_ball(cv, 0, 0, 34, '#FFFFFF', '#FF4F81')
        cv.drawLine(-34, 0, 34, 0, P('#C81A50', 200, stroke=4))
        cv.restore()
        char_front(cv, 520, 1010, 74, t, mood='calm', look=(1, 0.5), **YOU)


# 17 ─ « Alors vis chaque fois comme si c'était la première. »
class First(Scene):
    zoom = (1.0, 1.1)

    def __init__(self):
        rnd = random.Random(517)
        self.conf = [(rnd.uniform(0, W), rnd.uniform(-H, 0), rnd.uniform(150, 300), rnd.uniform(0, 360), rnd.choice(['#FF4F81', '#2DE2E6', '#FFD34A', '#B98CFF', '#ffffff'])) for _ in range(120)]

    def static(self, cv):
        street_bg(cv, sky=('#FF7AB8', '#FFE0A0'), seed=21, ground='#7A3A6A')
        glow(cv, 960, 600, 600, '#FFFFFF', 160)
        circle(cv, 960, 640, 180, '#FFF6D0')

    def dyn(self, cv, t, d):
        k = ease_out(t / 1.2)
        kids = [dict(KID), dict(top='#2DB8FF', hair='#E0A030', skin='#FFD0B0', pants='#1E1F5C', hairstyle=1), dict(top='#3FC46A', hair='#1A1030', skin='#8A5236', pants='#3A1E5A', hairstyle=0)]
        for i, kd in enumerate(kids):
            char_front(cv, 1180 + i * 200, 1010, 50, t * 3 + i, mood='laugh', arms='up', **kd)
        char_front(cv, 700, 1010, 76, t * 2, mood='laugh', arms='up', **YOU)
        bx = 760 + 600 * k; by = 900 - math.sin(k * math.pi) * 300 - (abs(math.sin(t * 4)) * 120 if k >= 1 else 0)
        shade_ball(cv, bx, by, 36, '#FFFFFF', '#FF4F81')
        for x, y, sp, rot, c in self.conf:
            yy = y + t * sp
            if yy < -20:
                continue
            cv.save(); cv.translate(x + 30 * math.sin(t * 2 + rot), yy % (H + 40)); cv.rotate(rot + t * 200)
            cv.drawRect(skia.Rect.MakeXYWH(-9, -5, 18, 10), P(c)); cv.restore()


SEGMENTS = [
    (Carry, "Un jour, ta mère t'a porté dans ses bras pour la dernière fois."),
    (NoOneKnew, "Et aucun de vous deux ne le savait."),
    (Play, "Un jour, tu as joué dehors avec tes amis d'enfance pour la dernière fois."),
    (SeeYou, "Vous vous êtes dit : à demain."),
    (NeverCame, "Et ce demain n'est jamais venu."),
    (Three, "Il y a eu une dernière histoire avant de dormir. Un dernier jour d'école. Un dernier appel de ton grand-père."),
    (Hourglass, "Personne ne t'a prévenu. La vie ne prévient jamais."),
    (Now, "Et ça continue, en ce moment."),
    (Father, "Il y aura une dernière fois où tu prendras ton père dans tes bras."),
    (Laugh, "Un dernier fou rire avec ton meilleur ami."),
    (Dinner, "Un dernier repas tous ensemble."),
    (DontKnow, "Tu ne sais pas quand."),
    (Beautiful, "Et c'est peut-être ça, le plus beau."),
    (Fireflies, "Parce que si chaque instant peut être le dernier, alors chaque instant compte."),
    (CallHug, "Alors appelle-les. Serre-les un peu plus fort. Ris un peu plus longtemps."),
    (ParkAgain, "Tu ne sais pas quelle fois sera la dernière."),
    (First, "Alors vis chaque fois comme si c'était la première."),
]

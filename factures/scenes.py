"""« Tu travailles pour payer des factures » : 13 plans, style sombre, onirique et un peu psychédélique."""
import math, os, random, sys, importlib.util
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('../calendrier', '../temps', '../profil'):
    sys.path.insert(1, os.path.join(HERE, d))
from lib import *
from kit import Stars, sparkle, neon
from mg import *
_s = importlib.util.spec_from_file_location('wow_scenes', os.path.join(HERE, '..', 'wow', 'scenes.py'))
ws = importlib.util.module_from_spec(_s); _s.loader.exec_module(ws)
night, stars, hero, OLD, ribbons = ws.night, ws.stars, ws.hero, ws.OLD, ws.ribbons

FONT = None
STYLE = dict(exclusion=True, color='#F0EBBE', size=196, maxw=1760, glitch=True, grain=7, readable=True,
             fps=60, trans=0.75, float=True, trans_kinds=['ink', 'liquid', 'dissolve', 'ripple', 'iris', 'ink', 'dissolve', 'liquid'])


class Scene:
    zoom = (1.0, 1.08)
    pan = (0, 0, 0, 0)
    shake = 0.0

    def static(self, cv):
        pass

    def dyn(self, cv, t, d):
        pass


def bill(cv, x, y, s, rot, txt, col='#F4EEDC', a=255):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    ofill(cv, prr(-0.6 * s, -0.4 * s, 1.2 * s, 0.8 * s, 0.06 * s), col, a=a, ol=OLD, w=4)
    for k in range(3):
        cv.drawLine(-0.45 * s, -0.05 * s + k * 0.15 * s, 0.35 * s, -0.05 * s + k * 0.15 * s, P('#8A7A6A', a, stroke=3))
    label(cv, 0, -0.17 * s, txt, max(10, int(0.2 * s)), color='#D81E2E', a=a, font=FONT, box=False)
    cv.restore()


def coins(cv, x, y, n, seed, t, a=255):
    rnd = random.Random(seed)
    for i in range(n):
        cx, cy = x + rnd.uniform(-180, 180), y - rnd.uniform(0, 120) * (1 - abs(rnd.uniform(-1, 1)))
        ofill(cv, poval(cx, cy, 34, 14), '#FFC23B', a=a, ol=OLD, w=4)
    glow(cv, x, y - 50, 220, '#FFC23B', 90 * a / 255)


# 1 ─ « Tu passes la plupart de tes journées à travailler. Pour payer l'endroit où tu dors. »
class Office(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = stars(1001, 160)

    def static(self, cv):
        night(cv, 1, '#05020F', '#14082E', '#24082E')
        ofill(cv, prr(1080, 120, 700, 520, 20), '#0A0620', ol=OLD)

    def dyn(self, cv, t, d):
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(1090, 130, 680, 500))
        self.st.draw(cv, t, 220)
        ribbons(cv, t, 3, 2, 200, 160, 90, amp=30)
        bx, by = 1430, 400 + 12 * math.sin(t * 1.2)
        p = skia.Path(); p.moveTo(bx - 200, by); p.quadTo(bx, by - 40, bx + 200, by); p.quadTo(bx + 60, by + 160, bx, by + 180); p.quadTo(bx - 60, by + 160, bx - 200, by); p.close()
        ofill(cv, p, '#3A2A5A', ol=OLD)
        ofill(cv, prr(bx - 150, by - 70, 300, 70, 20), '#5A3A8A', ol=OLD)
        ofill(cv, prr(bx - 140, by - 100, 90, 44, 16), '#E8E4FF', ol=OLD, w=4)
        glow(cv, bx, by - 40, 200, '#B98CFF', 80)
        cv.restore()
        cv.drawRect(skia.Rect.MakeXYWH(1425, 130, 10, 500), P(OLD)); cv.drawRect(skia.Rect.MakeXYWH(1090, 375, 680, 10), P(OLD))
        hero(cv, t, 620, 760, 190, eyes='lidded')
        glow(cv, 620, 940, 300, '#5AD7FF', 90 + 20 * math.sin(t * 7))
        ofill(cv, prr(200, 960, 900, 160, 20), '#2A1A3A', ol=OLD)
        ofill(cv, ppoly([(470, 960), (770, 960), (740, 860), (500, 860)]), '#1A2A4A', ol=OLD)


# 2 ─ « Le réveil sonne. Tu te lèves fatigué. »
class Alarm(Scene):
    zoom = (1.0, 1.12)
    shake = 0.6

    def static(self, cv):
        night(cv, 2, '#05020F', '#1A0A2A', '#2A0E2A')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#140A20'))

    def dyn(self, cv, t, d):
        sh = 10 * math.sin(t * 50) * max(0, 1 - t / 1.4)
        cx, cy = 1350 + sh, 470
        for side in (-1, 1):
            ofill(cv, pcircle(cx + side * 150, cy - 210, 70), '#D81E2E', ol=OLD)
        ofill(cv, pcircle(cx, cy, 230), '#E83C3C', ol=OLD)
        ofill(cv, pcircle(cx, cy, 185), '#F4EEDC', ol=OLD)
        for k in (-1, 1):
            ofill(cv, poval(cx + k * 70, cy - 30, 46, 52), '#FFFFFF', ol=OLD, w=5)
            circle(cv, cx + k * 70 + 6, cy - 22, 18, '#D81E2E')
            cv.save(); cv.translate(cx + k * 70, cy - 95); cv.rotate(-20 * k)
            rrect(cv, -45, -8, 90, 16, 8, OLD); cv.restore()
        ofill(cv, poval(cx, cy + 90, 70, 30), '#6A1030', ol=OLD, w=5)
        for k in range(4):
            a = math.radians(-60 + k * 40)
            neon(cv, [(cx + math.cos(a) * 280, cy - 250 + math.sin(a) * 60), (cx + math.cos(a) * 360, cy - 300 + math.sin(a) * 80)], '#FF4F6B', w=6, a=200 * abs(math.sin(t * 12)))
        k = ease(t / max(d, 0.1))
        hero(cv, t, 560, 820 - 40 * k, 180, eyes='lidded', hair_up=True)


# 3 ─ « Métro. Boulot. Écran. »
class Routine(Scene):
    zoom = (1.0, 1.06)

    def static(self, cv):
        night(cv, 3, '#02010A', '#0E0A2A', '#1A0A2A')

    def dyn(self, cv, t, d):
        q = min(2, int(t / max(d, 0.1) * 3))
        if q == 0:
            for i in range(12):
                k = ((i / 12) + t * 0.9) % 1.0
                r = 40 + (1 - k) ** 2 * 1300
                cv.drawCircle(960, 520, r, P(ws.DARKPSY[i % 5], 255 * k, stroke=30 + 40 * (1 - k)))
                cv.drawCircle(960, 520, r, P(OLD, 255 * k, stroke=5))
            ofill(cv, prr(700, 600, 520, 260, 60), '#3A4A8A', ol=OLD)
            for j in range(3):
                ofill(cv, prr(740 + j * 160, 640, 120, 110, 20), '#9BEFFF', a=200, ol=OLD, w=4)
            glow(cv, 960, 860, 200, '#FFE680', 120)
        elif q == 1:
            for r in range(3):
                for c in range(6):
                    x, y = 220 + c * 300, 560 + r * 200
                    hero(cv, t + c * 0.1, x, y, 70 + r * 6, eyes='lidded', third=False, hair_up=False, skin='#8A9AA8', hair='#3A3A4A', robe='#2A2A3A', seed=50 + r * 6 + c)
                    ofill(cv, prr(x - 90, y + 80, 180, 40, 8), '#2A2A4A', ol=OLD, w=4)
        else:
            ofill(cv, prr(560, 220, 800, 520, 30), '#1A1A3A', ol=OLD)
            cv.save(); cv.clipPath(prr(590, 250, 740, 460, 20), doAntiAlias=True)
            for k in range(14):
                a = k * 0.6 + t * 3
                neon(cv, [(960 + math.cos(a + u * 0.3) * u * 22, 480 + math.sin(a + u * 0.3) * u * 14) for u in range(20)], '#5AD7FF', w=4, a=180)
            cv.restore()
            glow(cv, 960, 480, 500, '#5AD7FF', 120)
            hero(cv, t, 960, 900, 150, eyes='open', third=False)


# 4 ─ « Le loyer. L'électricité. Le téléphone. Les courses. »
class Bills(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        night(cv, 4, '#05020F', '#1A0630', '#2A0A2A')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#120A20'))

    def dyn(self, cv, t, d):
        k = ease(t / max(d, 0.1))
        coins(cv, 960, 960, int(40 * (1 - 0.7 * k)) + 5, 4, t)
        names = ['LOYER', 'ÉLEC', 'TÉL', 'COURSES', 'LOYER', 'ÉLEC']
        for i in range(6):
            a = t * 1.2 + i * 1.05
            x = 960 + math.cos(a) * (520 - 200 * k)
            y = 520 + math.sin(a * 1.3) * 260 + 100 * k
            flap = 30 * math.sin(t * 14 + i)
            for side in (-1, 1):
                p = skia.Path(); p.moveTo(x + side * 50, y); p.quadTo(x + side * 140, y - 60 - flap, x + side * 200, y + 10)
                p.quadTo(x + side * 140, y + 10, x + side * 50, y + 20); p.close()
                ofill(cv, p, '#3A1A4A', ol=OLD, w=4)
            bill(cv, x, y, 110, 10 * math.sin(t * 3 + i), names[i])
            for e in (-1, 1):
                circle(cv, x + e * 20, y - 50, 9, '#FF4F6B')


# 5 ─ « Et à la fin du mois, tout est déjà reparti. »
class Wallet(Scene):
    zoom = (1.0, 1.18)

    def __init__(self):
        rnd = random.Random(5)
        self.p = [(rnd.uniform(-1, 1), rnd.uniform(0.3, 1), rnd.choice(['#FFC23B', '#FFE680', '#B98CFF'])) for _ in range(120)]

    def static(self, cv):
        night(cv, 5, '#02010A', '#0E0628', '#1A0A2A')

    def dyn(self, cv, t, d):
        k = ease(t / max(d * 0.8, 0.1))
        cx, cy = 960, 740
        ofill(cv, prr(cx - 260, cy - 120, 520, 260, 40), '#6A3A2A', ol=OLD)
        cv.save(); cv.translate(cx, cy - 120); cv.rotate(-40 * k)
        ofill(cv, prr(-260, -10, 520, 130, 40), '#7A4A3A', ol=OLD)
        cv.restore()
        for dx, sp, c in self.p:
            r = k * 900 * sp
            x, y = cx + dx * r, cy - 120 - r * 0.8
            circle(cv, x, y, 5 * (1 - k * 0.6) + 2, c, 255 * (1 - k * 0.7))


# 6 ─ « Alors tu recommences. Le lundi devient mardi. Les semaines deviennent des années. »
class Loop(Scene):
    zoom = (1.0, 1.08)

    def __init__(self):
        self.st = stars(1006, 200)

    def static(self, cv):
        night(cv, 6, '#05020F', '#120836', '#2A0A40')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 180)
        # anneau infini (lemniscate) façon tapis roulant de Möbius
        pts = []
        for i in range(121):
            a = i / 120 * 6.2832
            pts.append((960 + 620 * math.cos(a) / (1 + math.sin(a) ** 2), 640 + 620 * math.sin(a) * math.cos(a) / (1 + math.sin(a) ** 2)))
        neon(cv, pts, '#B98CFF', w=40, a=200, glow_w=70)
        neon(cv, pts, '#2A1450', w=26, a=255, glow_w=0)
        u = (t * 0.25) % 1
        a = u * 6.2832
        hx, hy = 960 + 620 * math.cos(a) / (1 + math.sin(a) ** 2), 640 + 620 * math.sin(a) * math.cos(a) / (1 + math.sin(a) ** 2)
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(hx - 150, hy - 260, 300, 270))
        hero(cv, t * 2, hx, hy - 150, 60, eyes='lidded', hair_up=False)
        cv.restore()
        days = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI']
        rnd = random.Random(7)
        for i in range(10):
            q = (t * 0.35 + i / 10) % 1
            x = rnd.uniform(200, 1700) + 80 * math.sin(q * 6 + i)
            y = -40 + q * 1100
            cv.save(); cv.translate(x, y); cv.rotate(q * 360 + i * 30)
            ofill(cv, pblob(0, 0, 34, n=6, seed=i, wob=0.3), ['#C8501F', '#E8A04A', '#8A2A3A'][i % 3], a=220, w=4)
            cv.restore()
            label(cv, x, y + 60, days[i % 5], 18, color='#B98CFF', a=200 * (1 - q), font=FONT, box=False)


# 7 ─ « Et un jour, tu te demandes où elles sont passées. »
class Older(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = stars(1007, 260)

    def static(self, cv):
        night(cv, 7, '#02010A', '#0E0A2A', '#24082E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        rnd = random.Random(8)
        for i in range(24):
            q = (t * 0.2 + i / 24) % 1
            x = rnd.uniform(0, W) + 60 * math.sin(q * 5 + i)
            cv.save(); cv.translate(x, -40 + q * 1150); cv.rotate(q * 300)
            ofill(cv, pblob(0, 0, 22, n=6, seed=i, wob=0.3), ['#C8501F', '#E8A04A', '#8A2A3A'][i % 3], a=200, w=3)
            cv.restore()
        hero(cv, t, 960, 790, 210, eyes='open', hair='#9A9AB0', seed=8)


# 8 ─ « Sur une vie, ça fait des dizaines de milliers d'heures. Des heures que personne ne te rendra. »
class Hourglass(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        rnd = random.Random(9)
        self.c = [(rnd.uniform(-1, 1), rnd.uniform(0, 1), rnd.uniform(10, 18)) for _ in range(70)]

    def static(self, cv):
        night(cv, 9, '#000000', '#0A0418', '#14082A')

    def dyn(self, cv, t, d):
        cx, cy = 960, 420
        top = ppoly([(cx - 300, cy - 360), (cx + 300, cy - 360), (cx + 20, cy), (cx - 20, cy)])
        ofill(cv, top, '#BFE6FF', a=60, ol=OLD)
        for dx, ph, r in self.c:
            q = (ph + t * 0.4) % 1
            if q < 0.4:
                x = cx + dx * 200 * (1 - q / 0.4); y = cy - 300 + q / 0.4 * 290
            else:
                x = cx + dx * 40 * (q - 0.4) * 8; y = cy + (q - 0.4) / 0.6 * 700
            a = 255 if q < 0.9 else 255 * (1 - (q - 0.9) / 0.1)
            ofill(cv, pcircle(x, y, r), '#F4EEDC', a=a, ol=OLD, w=3)
            cv.drawLine(x, y, x + r * 0.6 * math.cos(t * 4 + ph * 9), y + r * 0.6 * math.sin(t * 4 + ph * 9), P(OLD, a, stroke=2))
        for k in range(6):
            cv.drawOval(skia.Rect.MakeLTRB(cx - 400 + k * 40, 980 + k * 18, cx + 400 - k * 40, 1060 + k * 10), P('#05020A', 200, stroke=20))
        glow(cv, cx, 1060, 500, '#000000', 200)


# 9 ─ « Attention, je ne te dis pas de tout plaquer. Les factures, il faudra toujours les payer. »
class Calm(Scene):
    zoom = (1.0, 1.08)

    def static(self, cv):
        night(cv, 10, '#0A0414', '#1A0A2A', '#2A1430')
        glow(cv, 400, 300, 400, '#FFB05A', 110)

    def dyn(self, cv, t, d):
        ofill(cv, prr(200, 940, 1500, 200, 20), '#2A1A14', ol=OLD)
        k = ease(t / max(d * 0.5, 0.1))
        for i in range(6):
            bill(cv, 1300, 920 - i * 22 - 300 * (1 - k), 160, (i - 3) * 3, 'FACTURE')
        hero(cv, t, 700, 780, 190, eyes='lidded', smile=True)


# 10 ─ « Mais personne, à la fin de sa vie, ne regrette de ne pas avoir assez répondu à ses mails. »
class Mails(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        night(cv, 11, '#0A0414', '#2A0E3A', '#5A1A3A')

    def dyn(self, cv, t, d):
        k = ease(t / max(d, 0.1))
        glow(cv, 1500, 220, 400, '#FFB05A', 200)
        ofill(cv, pcircle(1500, 220, 90), '#FFE6A0', ol=OLD)
        rnd = random.Random(12)
        for i in range(70):
            x = 960 + rnd.uniform(-500, 500) * (1 - (rnd.random() * 0.3))
            base = 1060 - (1 - abs(x - 960) / 600) * 600
            y = rnd.uniform(base, 1060)
            y += k * (1080 - y) * rnd.uniform(0.6, 1)
            sq = 1 - 0.7 * k
            cv.save(); cv.translate(x, y); cv.rotate(rnd.uniform(-30, 30)); cv.scale(1, sq)
            ofill(cv, prr(-50, -32, 100, 64, 8), '#E8E4FF', a=255 * (1 - 0.5 * k), ol=OLD, w=4)
            cv.drawLine(-50, -32, 0, 4, P(OLD, 255 * (1 - 0.5 * k), stroke=3)); cv.drawLine(50, -32, 0, 4, P(OLD, 255 * (1 - 0.5 * k), stroke=3))
            cv.restore()
        for j in range(8):
            q = (t * 0.5 + j / 8) % 1
            circle(cv, 600 + j * 100, 1060 - q * 60, 8, '#BFE6FF', 200 * (1 - q))


# 11 ─ « On regrette les gens qu'on n'a pas assez vus. Les rêves qu'on a rangés dans un tiroir. »
class Drawer(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        night(cv, 13, '#05020F', '#14082E', '#24082E')

    def dyn(self, cv, t, d):
        half = d * 0.5
        if t < half:
            for i, (sk, hr, rb) in enumerate([('#E07AB8', '#2A0E3A', '#1E5A6A'), ('#D8B8A8', '#3A2A1A', '#2A1A5A'), ('#8AD8A8', '#1A3A2A', '#2A2A6A')]):
                fade = 1 - ease(t / half) * (0.4 + 0.2 * i)
                cv.saveLayerAlpha(None, int(255 * max(0.1, fade)))
                hero(cv, t, 500 + i * 460, 780, 150, eyes='open', third=False, hair_up=False, skin=sk, hair=hr, robe=rb, seed=60 + i)
                cv.restore()
            for k in range(5):
                cv.drawOval(skia.Rect.MakeLTRB(-200 + k * 300 + 40 * math.sin(t + k), 700, 400 + k * 300, 1100), P('#B98CFF', 50, blur=40))
        else:
            k = ease((t - half) / max(half * 0.7, 0.1))
            ofill(cv, prr(560, 480, 800, 520, 20), '#4A2A1A', ol=OLD)
            ofill(cv, prr(600, 520 + 300, 720, 160, 12), '#5A3A2A', ol=OLD)
            ofill(cv, prr(600, 640 - 0 * k, 720, 160 + 120 * k, 12), '#6A4A3A', ol=OLD)
            ofill(cv, prr(910, 690 + 60 * k, 100, 24, 12), '#C8A060', ol=OLD, w=4)
            ox, oy = 960, 640 - 380 * k
            glow(cv, ox, oy, 220, '#FFE680', 230 * k)
            for side in (-1, 1):
                ofill(cv, poval(ox + side * 40, oy, 44, 28), '#FFB0E8', a=255 * k, ol=OLD, w=4)
            ofill(cv, poval(ox, oy, 8, 26), OLD, a=255 * k, ol=OLD, w=2)


# 12 ─ « Alors ce soir, garde une heure. Rien qu'une. Pour ce qui te fait vraiment vivre. »
class OneHour(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        night(cv, 14, '#05020F', '#1A0A3A', '#3A0E4A')

    def dyn(self, cv, t, d):
        half = d * 0.55
        cx, cy, R = 960, 540, 380
        if t < half:
            ofill(cv, pcircle(cx, cy, R), '#1A1030', ol=OLD)
            for i in range(24):
                a = math.radians(i * 15 - 90)
                p = skia.Path(); p.moveTo(cx, cy); p.arcTo(skia.Rect.MakeLTRB(cx - R + 30, cy - R + 30, cx + R - 30, cy + R - 30), i * 15 - 90, 14, False); p.close()
                on = i == 19
                cv.drawPath(p, P('#FFC23B' if on else '#2A1A4A', 255 if on else 200))
            glow(cv, cx + math.cos(math.radians(19 * 15 - 83)) * 250, cy + math.sin(math.radians(19 * 15 - 83)) * 250, 160, '#FFC23B', 200 + 50 * math.sin(t * 5))
        else:
            k = ease_out((t - half) / 0.8)
            for i in range(14):
                a = i / 14 * 6.2832 + t * 0.3
                r = 520 * k
                x, y = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.7
                ofill(cv, pblob(x, y, 30 + 10 * (i % 3), n=7, seed=i, t=t), ['#FF4FD8', '#2DE2C6', '#FFB05A', '#B98CFF', '#FFE680'][i % 5], ol=OLD, w=4)
            glow(cv, cx, cy, 500 * k, '#FFB05A', 150)
            # guitare
            cv.save(); cv.translate(560, 840); cv.rotate(-30)
            ofill(cv, poval(0, 60, 80, 90), '#C8501F', ol=OLD); ofill(cv, poval(0, -40, 60, 66), '#C8501F', ol=OLD)
            ofill(cv, prr(-10, -280, 20, 230, 6), '#5A2A14', ol=OLD, w=4); ofill(cv, pcircle(0, 30, 22), '#1A0A14', ol=OLD, w=4)
            cv.restore()
            # pinceau
            cv.save(); cv.translate(1360, 820); cv.rotate(35)
            ofill(cv, prr(-10, -200, 20, 220, 8), '#E8A04A', ol=OLD, w=4); ofill(cv, ppoly([(-14, -200), (14, -200), (0, -260)]), '#FF4FD8', ol=OLD, w=4)
            cv.restore()


# 13 ─ « Parce que les factures, tu les paieras toujours. Mais ta vie, elle, ne se rembourse pas. »
class Rooftop(Scene):
    zoom = (1.12, 1.0)

    def __init__(self):
        self.st = stars(1013, 300)

    def static(self, cv):
        night(cv, 15, '#02010A', '#0E0A2A', '#24082E')
        rnd = random.Random(16)
        for i in range(22):
            x = -100 + i * 100; h = rnd.uniform(140, 380)
            ofill(cv, prr(x, 1080 - h, 96, h + 40, 6), '#1A1030', ol=OLD, w=4)
            for wy in range(int(1100 - h), 1060, 40):
                if rnd.random() > 0.55:
                    cv.drawRect(skia.Rect.MakeXYWH(x + 30, wy, 22, 18), P('#FFE680', 180))
        ofill(cv, prr(400, 900, 1120, 300, 10), '#2A1A3A', ol=OLD)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        ribbons(cv, t, 17, 3, 120, 130, 70)
        hero(cv, t, 960, 720, 170, eyes='lidded', smile=True)
        glow(cv, 960, 980, 160, '#FFC23B', 220 + 30 * math.sin(t * 3))
        ofill(cv, pcircle(960, 980, 30), '#FFE680', ol=OLD, w=4)


SEGMENTS = [
    (Office, "Tu passes la plupart de tes journées à travailler. Pour payer l'endroit où tu dors."),
    (Alarm, "Le réveil sonne. Tu te lèves fatigué."),
    (Routine, "Métro. Boulot. Écran."),
    (Bills, "Le loyer. L'électricité. Le téléphone. Les courses."),
    (Wallet, "Et à la fin du mois, tout est déjà reparti."),
    (Loop, "Alors tu recommences. Le lundi devient mardi. Les semaines deviennent des années."),
    (Older, "Et un jour, tu te demandes où elles sont passées."),
    (Hourglass, "Sur une vie, ça fait des dizaines de milliers d'heures. Des heures que personne ne te rendra."),
    (Calm, "Attention, je ne te dis pas de tout plaquer. Les factures, il faudra toujours les payer."),
    (Mails, "Mais personne, à la fin de sa vie, ne regrette de ne pas avoir assez répondu à ses mails."),
    (Drawer, "On regrette les gens qu'on n'a pas assez vus. Les rêves qu'on a rangés dans un tiroir."),
    (OneHour, "Alors ce soir, garde une heure. Rien qu'une. Pour ce qui te fait vraiment vivre."),
    (Rooftop, "Parce que les factures, tu les paieras toujours. Mais ta vie, elle, ne se rembourse pas."),
]

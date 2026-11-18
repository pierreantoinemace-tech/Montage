"""« Tout ce que tu ne vois pas » : 13 plans au plus près des références
(cadrages serrés, mascottes rondes ombrées en 2 tons, grands éléments holographiques)."""
import math, os, random, sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(HERE, '..', 'calendrier'))
from lib import *
from kit import *

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


# ------------------------------------------------------------------ outils « cel shading »
def cel(cv, path, base, dark=None, light=None, off=(26, 30), hi=None):
    """Forme pleine + ombre propre en croissant (côté bas-droite) + reflet, comme dans les références."""
    dark = dark or mix(base, '#000000', 0.28)
    cv.drawPath(path, P(dark))
    cv.save(); cv.clipPath(path, doAntiAlias=True)
    cv.translate(-off[0], -off[1]); cv.drawPath(path, P(base)); cv.translate(off[0], off[1])
    if hi:
        x, y, rx, ry = hi
        oval(cv, x, y, rx, ry, light or mix(base, '#FFFFFF', 0.35), 200)
    cv.restore()


def circ_path(x, y, r):
    p = skia.Path(); p.addCircle(x, y, r); return p


def oval_path(x, y, rx, ry):
    p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)); return p


def eye(cv, x, y, r, look=(0, 0), blink=1.0, pupil='#120A2A', iris=None):
    cv.drawPath(oval_path(x, y, r, r * blink), P('#FFFFFF'))
    if blink > 0.3:
        cv.save(); cv.clipPath(oval_path(x, y, r, r * blink), doAntiAlias=True)
        px, py = x + look[0] * r * 0.35, y + look[1] * r * 0.35
        if iris:
            circle(cv, px, py, r * 0.62, iris)
        circle(cv, px, py, r * 0.42, pupil)
        circle(cv, px - r * 0.16, py - r * 0.16, r * 0.13, '#FFFFFF')
        oval(cv, x + r * 0.2, y + r * 0.75, r * 0.9, r * 0.3, '#C8C8E8', 160)
        cv.restore()


def blinkf(t, period=3.2, ph=0.0):
    k = (t + ph) % period
    return 0.08 if k < 0.12 else 1.0


def birdie(cv, x, y, r, t, body='#2F6BFF', belly='#5AD7FF', beak='#FFC23B', look=(0.3, 0), mood='calm', facing=1, wing=0.0):
    """Mascotte ronde type « petit oiseau » : corps-boule, gros yeux, bec, petite aile."""
    cv.save(); cv.translate(x, y); cv.scale(facing, 1)
    cel(cv, circ_path(0, 0, r), body, off=(r * 0.12, r * 0.14), hi=(-r * 0.4, -r * 0.5, r * 0.25, r * 0.14))
    cv.save(); cv.clipPath(circ_path(0, 0, r), doAntiAlias=True)
    oval(cv, r * 0.25, r * 0.55, r * 0.75, r * 0.6, belly, 230)
    cv.restore()
    # aile
    cv.save(); cv.translate(-r * 0.6, r * 0.15); cv.rotate(-20 + 25 * wing)
    cel(cv, oval_path(0, 0, r * 0.38, r * 0.22), mix(body, '#000000', 0.12), off=(r * 0.05, r * 0.06))
    cv.restore()
    bl = blinkf(t, 3.4, x * 0.001)
    eye(cv, r * 0.12, -r * 0.18, r * 0.26, look, bl if mood != 'wow' else 1.0)
    eye(cv, r * 0.6, -r * 0.14, r * 0.22, look, bl if mood != 'wow' else 1.0)
    if mood == 'wow':
        cel(cv, oval_path(r * 0.48, r * 0.18, r * 0.2, r * 0.17), beak, off=(r * 0.03, r * 0.04))
        oval(cv, r * 0.5, r * 0.2, r * 0.09, r * 0.08, '#6A1030')
    else:
        p = skia.Path(); p.moveTo(r * 0.32, r * 0.05); p.quadTo(r * 0.95, r * 0.08, r * 0.95, r * 0.2); p.quadTo(r * 0.7, r * 0.36, r * 0.3, r * 0.22); p.close()
        cel(cv, p, beak, off=(r * 0.03, r * 0.04))
    if mood in ('happy', 'wow'):
        oval(cv, r * -0.15, r * 0.12, r * 0.12, r * 0.07, '#FF6F91', 150)
    cv.restore()


def holo_hemis(cv, cx, cy, r, open_k, t, core=True):
    """Deux demi-sphères holographiques qui s'ouvrent sur un cœur lumineux (motif fort des références)."""
    if core:
        glow(cv, cx, cy, r * 1.4, '#FFD34A', 220)
        circle(cv, cx, cy, r * 0.52, '#FFE680')
        circle(cv, cx, cy, r * 0.4, '#FFFBE6')
    for side in (-1, 1):
        x = cx + side * (r * 0.25 + open_k * r * 0.75)
        cv.save(); cv.translate(x, cy); cv.rotate(side * (8 + 6 * math.sin(t * 0.8)))
        shell = oval_path(0, 0, r * 0.55, r)
        cv.drawPath(shell, P(shader=lin(-r * 0.55, -r, r * 0.55, r, ['#C04BFF', '#7A3CFF', '#2DE2E6']), a=235))
        cv.save(); cv.clipPath(shell, doAntiAlias=True)
        for k in range(1, 7):
            oval(cv, 0, 0, r * 0.55 * k / 7, r, '#FFFFFF', 70, stroke=2)
        for k in range(-6, 7):
            yy = r * k / 7
            cv.drawLine(-r, yy, r, yy, P('#FFFFFF', 60, stroke=2))
        oval(cv, -side * r * 0.25, 0, r * 0.32, r * 0.92, '#3A0A6A', 150)
        cv.restore()
        cv.drawPath(shell, P('#E8D8FF', 200, stroke=3))
        cv.restore()


def thermal(v):
    stops = [(0, '#14062E'), (0.25, '#5A0AAA'), (0.5, '#E8247C'), (0.75, '#FF9A1F'), (1, '#FFF6B0')]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if v <= b:
            return mix(ca, cb, (v - a) / (b - a))
    return stops[-1][1]


RICH = ('#ffffff', '#ffffff', '#FF5A7A', '#6FA8FF', '#FFB13B', '#B98CFF')


# 1 ─ « Il y a, juste devant toi, des couleurs que tes yeux ne verront jamais. »
class EyeClose(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        bg_lin(cv, '#FF9A3C', '#E0477A')

    def dyn(self, cv, t, d):
        cx, cy = 960, 560
        bl = ease(t / 0.45) if t < 0.45 else 1.0
        skin = '#F2A97E'
        cel(cv, oval_path(cx, cy + 40, 1100, 620), skin, off=(0, -60))
        lid = oval_path(cx, cy, 760, 430 * bl)
        cv.drawPath(lid, P('#FFF6F0'))
        cv.save(); cv.clipPath(lid, doAntiAlias=True)
        lx = 60 * math.sin(t * 0.9)
        ix, iy = cx + lx, cy + 10
        circle(cv, ix, iy, 380, '#2A0F5E')
        cv.drawCircle(ix, iy, 360, P(shader=rad(ix, iy, 360, ['#2DE2E6', '#7A3CFF', '#C04BFF'])))
        cam = Cam(yaw=t * 30, pitch=-15, dist=1400, f=1400, cx=ix, cy=iy)
        wire_sphere(cv, cam, 0, 0, 0, 300, '#FFFFFF', 90, nlat=8, nlon=12, w=1.6)
        for k in range(36):
            a = k / 36 * 6.283 + t * 0.2
            cv.drawLine(ix + math.cos(a) * 170, iy + math.sin(a) * 170, ix + math.cos(a) * 350, iy + math.sin(a) * 350, P('#FFFFFF', 50, stroke=3))
        circle(cv, ix, iy, 150, '#05020F')
        circle(cv, ix - 120, iy - 130, 56, '#FFFFFF', 235)
        circle(cv, ix + 100, iy + 110, 20, '#FFFFFF', 180)
        oval(cv, cx, cy + 380 * bl, 760, 140, '#E0C8D8', 120)
        cv.restore()
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - 760, cy - 430 * bl, cx + 760, cy + 430 * bl), 195, 150)
        cv.drawPath(p, P('#7A1E4A', 255, stroke=40))
        for k in range(9):
            a = math.radians(200 + k * 17)
            x0, y0 = cx + 760 * math.cos(a), cy + 430 * bl * math.sin(a)
            cv.drawLine(x0, y0, x0 + 60 * math.cos(a), y0 + 90 * math.sin(a) - 30, P('#3A0A2A', 255, stroke=14))


# 2 ─ « La lumière que tu vois n'est qu'une minuscule fenêtre. Tout le reste est invisible. »
class Spectrum(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        self.st = Stars(220, 602, rmax=2.2, colors=RICH)

    def static(self, cv):
        bg_lin(cv, '#06041C', '#22083E')

    def dyn(self, cv, t, d):
        self.st.draw(cv, t, 200)
        cy = 560
        for band in range(3):
            pts = []
            for x in range(-100, W + 101, 12):
                u = (x + 100) / (W + 200)
                lam = 0.004 + 0.06 * (1 - u) ** 2.2
                pts.append((x, cy + (220 - band * 60) * math.sin(x * lam - t * 4 + band)))
            neon(cv, pts, ['#7A3CFF', '#3C5CFF', '#B13CFF'][band], w=4, a=140, glow_w=16)
        # la petite fenêtre visible, arc-en-ciel
        k = ease_out((t - 0.5) / 0.8)
        wx, ww = 960, 260 * k
        if k > 0:
            cols = ['#FF3B3B', '#FF9A1F', '#FFE04A', '#3FE07A', '#2DB8FF', '#7A4BFF']
            for i, c in enumerate(cols):
                cv.drawRect(skia.Rect.MakeXYWH(wx - ww / 2 + ww * i / 6, 170, ww / 6 + 1, 780), P(c, 200))
            cv.drawRect(skia.Rect.MakeXYWH(wx - ww / 2, 170, ww, 780), P('#FFFFFF', 255, stroke=6))
            glow(cv, wx, 560, 420 * k, '#FFFFFF', 90)
        for x, lab in ((220, 'RADIO'), (560, 'INFRAROUGE'), (1380, 'ULTRAVIOLET'), (1720, 'RAYONS X')):
            label(cv, x, 1010, lab, 26, color='#B98CFF', font=FONT, box=False)


# 3 ─ « Les abeilles voient l'ultraviolet. Pour elles, les fleurs sont couvertes de motifs lumineux, comme des pistes d'atterrissage. »
class Bee(Scene):
    zoom = (1.0, 1.1)
    pan = (40, 0, -40, 0)

    def static(self, cv):
        bg_lin(cv, '#14063A', '#4A0E6A')

    def _flower(self, cv, x, y, r, t, uv):
        for k in range(8):
            a = k / 8 * 6.283 + 0.2 * math.sin(t + x)
            px, py = x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75
            p = oval_path(0, 0, r * 0.55, r * 0.3)
            cv.save(); cv.translate(px, py); cv.rotate(math.degrees(a))
            cel(cv, p, '#FF4FD8' if uv else '#FFE04A', off=(r * 0.05, r * 0.06))
            if uv:
                oval(cv, -r * 0.15, 0, r * 0.32, r * 0.12, '#2DE2E6', 230)
            cv.restore()
        if uv:
            for k in range(4):
                circle(cv, x, y, r * (0.35 + k * 0.18), '#2DE2E6', 200 - k * 40, stroke=6)
            glow(cv, x, y, r * 1.6, '#B13CFF', 120)
        circle(cv, x, y, r * 0.32, '#FFB13B')

    def dyn(self, cv, t, d):
        uv = t > 1.0
        for i, (x, y, r) in enumerate([(1240, 820, 190), (1640, 560, 160), (1500, 1000, 140), (1820, 920, 120), (1120, 380, 110)]):
            self._flower(cv, x, y + 10 * math.sin(t * 1.5 + i), r, t, uv)
        # abeille géante, coupée par le bord gauche
        bx, by = 420 + 30 * math.sin(t * 2), 520 + 24 * math.sin(t * 3)
        for side, ph in ((-1, 0), (1, 1)):
            cv.save(); cv.translate(bx - 40 + side * 60, by - 300); cv.rotate(-25 + side * 30 + 18 * math.sin(t * 40 + ph))
            oval(cv, 0, -140, 130, 230, '#BFF6FF', 140); oval(cv, 0, -140, 130, 230, '#FFFFFF', 200, stroke=4)
            cv.restore()
        body = oval_path(bx - 80, by + 40, 460, 340)
        cel(cv, body, '#FFC23B', off=(40, 46), hi=(bx - 280, by - 160, 120, 50))
        cv.save(); cv.clipPath(body, doAntiAlias=True)
        for k in range(3):
            cv.save(); cv.translate(bx - 380 + k * 190, by); cv.rotate(12)
            cv.drawRect(skia.Rect.MakeXYWH(-45, -500, 90, 1000), P('#2A1430'))
            cv.restore()
        cv.restore()
        head = circ_path(bx + 330, by - 40, 240)
        cel(cv, head, '#2A1430', off=(22, 26), hi=(bx + 250, by - 160, 70, 30))
        eye(cv, bx + 330, by - 80, 120, (0.6, 0.1), blinkf(t))
        eye(cv, bx + 500, by - 60, 80, (0.6, 0.1), blinkf(t))
        for sx in (0, 140):
            p = skia.Path(); p.moveTo(bx + 300 + sx, by - 270); p.quadTo(bx + 320 + sx, by - 420, bx + 420 + sx, by - 440)
            cv.drawPath(p, P('#2A1430', 255, stroke=14)); circle(cv, bx + 420 + sx, by - 440, 22, '#2A1430')
        if uv:
            label(cv, 1500, 150, 'VISION ULTRAVIOLET', 28, color='#2DE2E6', font=FONT)


# 4 ─ « Les serpents voient la chaleur de ton corps, dans le noir complet. »
class Snake(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        bg_lin(cv, '#05020F', '#14062E')
        for k in range(30):
            cv.drawLine(0, 20 + k * 36, W, 20 + k * 36, P('#5A0AAA', 30, stroke=2))

    def dyn(self, cv, t, d):
        # silhouette thermique (personnage-mascotte) à droite
        cx, cy = 1450, 600
        for k in range(7, 0, -1):
            v = 1 - k / 8
            s = 1 + k * 0.08
            cv.save(); cv.translate(cx, cy); cv.scale(s, s)
            circle(cv, 0, -220, 140, thermal(v)); rrect(cv, -170, -90, 340, 520, 140, thermal(v))
            cv.restore()
        circle(cv, cx, cy - 220, 100, thermal(1)); rrect(cv, cx - 120, cy - 70, 240, 440, 110, thermal(0.92))
        glow(cv, cx, cy, 500, '#FF9A1F', 90)
        # tête de serpent géante, coupée par le bord gauche
        sx, sy = 260 + 40 * math.sin(t * 1.2), 640 + 30 * math.sin(t * 0.9)
        p = skia.Path(); p.moveTo(sx - 700, sy + 400); p.cubicTo(sx - 300, sy + 380, sx - 100, sy + 260, sx + 140, sy + 120)
        p.cubicTo(sx + 520, sy - 40, sx + 600, sy - 200, sx + 380, sy - 280); p.cubicTo(sx + 160, sy - 360, sx - 200, sy - 240, sx - 380, sy - 60)
        p.cubicTo(sx - 520, sy + 40, sx - 700, sy + 120, sx - 760, sy + 160); p.close()
        cel(cv, p, '#2EB87A', off=(30, 40), hi=(sx + 80, sy - 220, 160, 40))
        cv.save(); cv.clipPath(p, doAntiAlias=True)
        for k in range(40):
            circle(cv, sx - 500 + (k % 10) * 90 + (k // 10) * 40, sy - 200 + (k // 10) * 110, 30, '#1E8A5A', 160)
        cv.restore()
        eye(cv, sx + 230, sy - 170, 70, (1, 0), blinkf(t, 4), iris='#FFD34A')
        oval(cv, sx + 230 + 25, sy - 170, 14, 50, '#120A2A')
        circle(cv, sx + 420, sy - 120, 14, '#0E5A3A')
        k = (t * 1.6) % 1.0
        if k < 0.4:
            tx = sx + 460
            p = skia.Path(); p.moveTo(tx, sy - 60); p.lineTo(tx + 160 * (k / 0.4), sy - 60 + 10 * math.sin(t * 40))
            p.lineTo(tx + 160 * (k / 0.4) + 40, sy - 90); p.moveTo(tx + 160 * (k / 0.4), sy - 60); p.lineTo(tx + 160 * (k / 0.4) + 40, sy - 30)
            cv.drawPath(p, P('#E8247C', 255, stroke=10))
        label(cv, 1450, 1000, 'VISION THERMIQUE', 28, color='#FF9A1F', font=FONT)


# 5 ─ « La crevette-mante a seize types de récepteurs de couleur. Toi, tu en as trois. »
class Shrimp(Scene):
    zoom = (1.0, 1.1)

    def static(self, cv):
        bg_lin(cv, '#0A2A6A', '#0A0A3A')
        for k in range(8):
            poly(cv, [(k * 280 - 100, 0), (k * 280 + 20, 0), (k * 280 + 300, H), (k * 280 + 120, H)], '#7FE7FF', 16)

    def dyn(self, cv, t, d):
        cols = ['#FF3B6B', '#FF8A1F', '#FFE04A', '#3FE07A', '#2DE2E6', '#2DB8FF', '#7A4BFF', '#E83CFF']
        bx, by = 980, 760
        wig = 10 * math.sin(t * 3)
        for i in range(8):
            x = bx - 520 + i * 140
            y = by + 40 * math.sin(i * 0.5 + t * 2)
            cel(cv, oval_path(x, y, 120, 150 - i * 4), cols[i], off=(14, 18), hi=(x - 40, y - 80, 50, 20))
            for leg in (-1, 1):
                cv.drawLine(x + leg * 30, y + 120, x + leg * 50, y + 210 + wig, P(mix(cols[i], '#000000', 0.3), 255, stroke=14))
        # tête + yeux sur pédoncules qui bougent indépendamment
        hx, hy = bx + 560, by - 60
        cel(cv, oval_path(hx, hy, 190, 160), '#3FE07A', off=(18, 22), hi=(hx - 60, hy - 90, 70, 26))
        for k, (dx, ph) in enumerate(((-60, 0), (80, 2))):
            ang = 25 * math.sin(t * 2.2 + ph)
            cv.save(); cv.translate(hx + dx, hy - 140); cv.rotate(ang)
            rrect(cv, -16, -200, 32, 210, 16, '#2EB87A')
            cel(cv, oval_path(0, -240, 70, 56), '#E83CFF', off=(8, 10))
            for b in range(5):
                cv.drawLine(-60, -262 + b * 11, 60, -262 + b * 11, P(cols[(b + k) % 8], 230, stroke=5))
            circle(cv, 18 * math.sin(t * 3 + ph), -240, 16, '#120A2A')
            cv.restore()
        for i in range(16):
            a = i / 16 * 6.283 + t * 0.4
            circle(cv, 520 + 120 * math.cos(a), 250 + 120 * math.sin(a), 18, cols[i % 8])
        for i in range(3):
            a = i / 3 * 6.283 + t * 0.4
            circle(cv, 1420 + 60 * math.cos(a), 250 + 60 * math.sin(a), 22, ['#FF3B3B', '#3FE07A', '#2DB8FF'][i])
        label(cv, 520, 430, '16', 52, font=FONT, box=False)
        label(cv, 1420, 430, '3', 52, font=FONT, box=False)


# 6 ─ « Les éléphants se parlent avec des sons trop graves pour nos oreilles. »
class Elephant(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        bg_lin(cv, '#5A1E8A', '#FF9A5C')
        glow(cv, 1500, 760, 600, '#FFE07A', 200)
        circle(cv, 1500, 800, 230, '#FFF0B0')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#3A0E4A'))

    def dyn(self, cv, t, d):
        # ondes infrasonores dans le sol
        for k in range(6):
            q = (t * 0.5 + k / 6) % 1
            rr = 100 + q * 1500
            p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(700 - rr, 900 - rr * 0.35, 700 + rr, 900 + rr * 0.35), 0, 180)
            cv.drawPath(p, P('#2DE2E6', 200 * (1 - q), stroke=6))
        # tête d'éléphant géante (profil), coupée par le bord gauche
        ex, ey = 420, 520 + 10 * math.sin(t)
        ear = oval_path(ex - 200, ey + 20, 380, 460)
        cel(cv, ear, '#8A7AB8', off=(30, 36))
        head = oval_path(ex + 160, ey - 40, 420, 380)
        cel(cv, head, '#A898D0', off=(40, 44), hi=(ex + 40, ey - 280, 140, 50))
        sw = 40 * math.sin(t * 1.3)
        p = skia.Path(); p.moveTo(ex + 450, ey + 40); p.cubicTo(ex + 640, ey + 200, ex + 560 + sw, ey + 420, ex + 700 + sw, ey + 500)
        cv.drawPath(p, P('#8A7AB8', 255, stroke=150)); cv.drawPath(p, P('#A898D0', 255, stroke=110))
        for k in range(6):
            u = 0.2 + k * 0.13
            x = (1 - u) ** 3 * (ex + 450) + 3 * u * (1 - u) ** 2 * (ex + 640) + 3 * u * u * (1 - u) * (ex + 560 + sw) + u ** 3 * (ex + 700 + sw)
            y = (1 - u) ** 3 * (ey + 40) + 3 * u * (1 - u) ** 2 * (ey + 200) + 3 * u * u * (1 - u) * (ey + 420) + u ** 3 * (ey + 500)
            cv.drawLine(x - 40, y, x + 40, y - 10, P('#7A6AA8', 200, stroke=5))
        p = skia.Path(); p.moveTo(ex + 380, ey + 150); p.quadTo(ex + 560, ey + 260, ex + 640, ey + 200)
        cv.drawPath(p, P('#FFF6E0', 255, stroke=44))
        eye(cv, ex + 330, ey - 110, 52, (0.5, 0.2), blinkf(t, 3.8))
        oval(cv, ex + 250, ey - 20, 40, 22, '#FF6F91', 130)


# 7 ─ « Et en ce moment, des milliers de milliards de particules venues du Soleil traversent ton corps. »
class Neutrinos(Scene):
    zoom = (1.0, 1.12)
    shake = 0.0

    def __init__(self):
        rnd = random.Random(607)
        self.p = [(rnd.uniform(0, 1), rnd.uniform(-1, 1), rnd.choice(['#FFE680', '#FFFFFF', '#FF9A1F', '#2DE2E6'])) for _ in range(260)]

    def static(self, cv):
        bg_lin(cv, '#14062E', '#3A0A5E')

    def dyn(self, cv, t, d):
        sx, sy = -120, 420
        glow(cv, sx, sy, 900, '#FF9A1F', 200)
        cel(cv, circ_path(sx, sy, 460), '#FFB13B', off=(40, 40))
        circle(cv, sx, sy, 380, '#FFD34A'); circle(cv, sx - 60, sy - 60, 240, '#FFF0B0')
        # silhouette humaine en fil de fer (comme la tête-cerveau des références)
        hx = 1300
        for w_, c, a in ((12, '#2DB8FF', 120), (5, '#5AD7FF', 255)):
            p = skia.Path(); p.addCircle(hx, 300, 140)
            p.moveTo(hx - 70, 430); p.lineTo(hx - 80, 470); p.cubicTo(hx - 340, 500, hx - 380, 600, hx - 380, 1200)
            p.moveTo(hx + 70, 430); p.lineTo(hx + 80, 470); p.cubicTo(hx + 340, 500, hx + 380, 600, hx + 380, 1200)
            cv.drawPath(p, P(c, a, stroke=w_, blur=6 if w_ > 6 else 0))
        cam = Cam(yaw=t * 20, pitch=-5, dist=1400, f=1400, cx=hx, cy=300)
        wire_sphere(cv, cam, 0, 0, 0, 130, '#5AD7FF', 80, nlat=6, nlon=10, w=1.4)
        for ph, dy, c in self.p:
            k = (ph + t * 0.9) % 1.0
            x0 = sx + 300 + k * 2200
            y0 = sy + dy * 500 + k * 200 * dy
            cv.drawLine(x0, y0, x0 + 90, y0 + 9 * dy, P(c, 220, stroke=3))
        glow(cv, hx, 700, 400, '#5AD7FF', 60 + 40 * math.sin(t * 6))


# 8 ─ « Chaque seconde. Sans que tu ne sentes rien. »
class Sleep(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        rnd = random.Random(608)
        self.p = [(rnd.uniform(0, 1), rnd.uniform(0, W), rnd.choice(['#FFE680', '#FFFFFF', '#2DE2E6'])) for _ in range(140)]

    def static(self, cv):
        bg_lin(cv, '#1E0E5A', '#0A0630')
        rrect(cv, 1300, 120, 460, 380, 20, '#3B2A8F'); rrect(cv, 1320, 140, 420, 340, 10, '#0E1250')
        circle(cv, 1620, 250, 56, '#E8E4FF'); circle(cv, 1648, 232, 56, '#0E1250')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#140A3A'))

    def dyn(self, cv, t, d):
        for ph, x, c in self.p:
            k = (ph + t * 0.7) % 1.0
            y = -100 + k * 1400
            cv.drawLine(x, y, x + 12, y + 70, P(c, 150, stroke=2.5))
        bed = skia.Path(); bed.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(260, 700, 1400, 300), 60, 60))
        cel(cv, bed, '#3A98C4', off=(20, 26))
        cel(cv, oval_path(560, 720, 230, 90), '#E8E4FF', off=(10, 14))
        br = 1 + 0.03 * math.sin(t * 1.6)
        birdie(cv, 640, 600, 220 * br, t, body='#FF4F81', belly='#FFB0C8', mood='calm', look=(0, 0))
        # paupières fermées par-dessus les yeux
        for ex, er in ((640 + 220 * 0.12, 220 * 0.26), (640 + 220 * 0.6, 220 * 0.22)):
            cv.drawPath(oval_path(ex, 600 - 220 * 0.16, er + 4, er + 4), P('#FF4F81'))
            p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(ex - er, 600 - 220 * 0.16 - er * 0.5, ex + er, 600 - 220 * 0.16 + er * 0.6), 20, 140)
            cv.drawPath(p, P('#7A1E4A', 255, stroke=8))
        cover = skia.Path(); cover.moveTo(700, 1000); cover.cubicTo(760, 640, 1560, 640, 1640, 1000); cover.close()
        cel(cv, cover, '#FFD34A', off=(20, 26), hi=(1100, 720, 200, 30))
        for k in range(3):
            q = (t * 0.45 + k / 3) % 1
            label(cv, 900 + q * 120, 420 - q * 160, 'Z', 44 + 10 * k, color='#FFFFFF', a=255 * math.sin(q * math.pi), font=FONT, box=False)


# 9 ─ « Le monde est infiniment plus grand que ce que tu perçois. »
class Bigger(Scene):
    zoom = (1.15, 1.0)

    def __init__(self):
        self.st = Stars(320, 609, rmax=2.6, colors=RICH)
        rnd = random.Random(610)
        self.big = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(10, 20), rnd.choice(RICH[2:])) for _ in range(20)]

    def static(self, cv):
        bg_lin(cv, '#3A0A6A', '#7A1A8A')
        glow(cv, 960, 540, 900, '#B13CFF', 120)

    def dyn(self, cv, t, d):
        self.st.draw(cv, t)
        for x, y, r, c in self.big:
            sparkle(cv, x, y, r * (0.7 + 0.3 * math.sin(t * 3 + x)), c)
        holo_hemis(cv, 960, 560, 420, ease_out(t / max(d * 0.8, 0.1)), t)


# 10 ─ « Alors ne le juge pas sur le petit bout que tu en vois. »
class Keyhole(Scene):
    zoom = (1.0, 1.18)

    def static(self, cv):
        bg_lin(cv, '#2A1466', '#140A3A')
        for k in range(14):
            cv.drawRect(skia.Rect.MakeXYWH(k * 140, 0, 6, H), P('#000000', 40))

    def dyn(self, cv, t, d):
        cx, cy = 960, 470
        hole = skia.Path(); hole.addCircle(cx, cy - 60, 170)
        hole.moveTo(cx - 90, cy + 40); hole.lineTo(cx + 90, cy + 40); hole.lineTo(cx + 150, cy + 460); hole.lineTo(cx - 150, cy + 460); hole.close()
        cv.save(); cv.clipPath(hole, doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), P(shader=lin(0, 200, 0, 1000, ['#FFB0C8', '#FFE680'])))
        glow(cv, cx, cy, 500, '#FFFFFF', 220)
        for k in range(12):
            cv.save(); cv.translate(cx, cy + 200); cv.rotate(k * 30 + t * 10)
            poly(cv, [(0, 0), (900, -60), (900, 60)], '#FFFFFF', 70); cv.restore()
        cv.restore()
        cv.drawPath(hole, P('#FFE680', 255, stroke=10))
        # mascotte qui regarde par le trou, de dos, énorme, coupée par le bas
        birdie(cv, 960, 1180, 380, t, body='#2F6BFF', belly='#5AD7FF', look=(0, -1), mood='wow', facing=-1)


# 11 ─ « Ta vie non plus. »
class Desk(Scene):
    zoom = (1.12, 1.0)

    def static(self, cv):
        bg_lin(cv, '#1AA89A', '#0E5A6A')
        for k in range(12):
            cv.drawRect(skia.Rect.MakeXYWH(k * 170, 0, 8, 760), P('#000000', 30))
        # horloge murale
        cel(cv, circ_path(1520, 260, 150), '#FFF8EE', off=(12, 14))
        circle(cv, 1520, 260, 150, '#0E3A4A', 255, stroke=16)
        cv.drawRect(skia.Rect.MakeXYWH(-400, 760, W + 800, 600), P('#0A3A4A'))
        cel(cv, skia.Path().addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-100, 700, 2120, 90), 20, 20)), '#FF9A3C', off=(-10, -14))

    def dyn(self, cv, t, d):
        for ang, ln, w in ((t * 2, 100, 12), (t * 24, 125, 6)):
            cv.drawLine(1520, 260, 1520 + math.cos(ang - 1.57) * ln, 260 + math.sin(ang - 1.57) * ln, P('#0E3A4A', 255, stroke=w))
        birdie(cv, 720, 470, 400, t, body='#8A4BFF', belly='#C8A8FF', beak='#FFC23B', look=(0.7, 0.5), mood='calm')
        lap = skia.Path(); lap.moveTo(1060, 700); lap.lineTo(1500, 700); lap.lineTo(1440, 400); lap.lineTo(1120, 400); lap.close()
        cel(cv, lap, '#2A2A5A', off=(12, 14))
        poly(cv, [(1140, 420), (1420, 420), (1470, 680), (1090, 680)], '#5AD7FF', 230)
        glow(cv, 1280, 560, 340, '#5AD7FF', 110)
        for k in range(4):
            rrect(cv, 1160, 450 + k * 50 + (t * 40) % 50, 240 - k * 30, 20, 8, '#FFFFFF', 160)
        rrect(cv, 1020, 690, 520, 26, 10, '#3A3A6A')


# 12 ─ « Ce que tu vis aujourd'hui n'est qu'une petite fenêtre. »
class Window(Scene):
    zoom = (1.0, 1.12)

    def static(self, cv):
        bg_lin(cv, '#3A1A7A', '#1A0A4E')
        cv.drawRect(skia.Rect.MakeXYWH(-400, 900, W + 800, 600), P('#140A3A'))

    def dyn(self, cv, t, d):
        wx, wy, ww, wh = 1060, 200, 520, 460
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
        cv.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), P(shader=lin(0, wy, 0, wy + wh, ['#0A0630', '#3A1460'])))
        Stars(60, 612, area=(wx, wy, wx + ww, wy + wh)).draw(cv, t)
        circle(cv, wx + 380, wy + 140, 50, '#E8E4FF')
        cv.restore()
        cel(cv, skia.Path().addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(wx - 30, wy - 30, ww + 60, wh + 60), 20, 20)), '#6A4AB8', off=(10, 10))
        cv.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), P(shader=lin(0, wy, 0, wy + wh, ['#0A0630', '#3A1460'])))
        Stars(60, 612, area=(wx, wy, wx + ww, wy + wh)).draw(cv, t)
        circle(cv, wx + 380, wy + 140, 50, '#E8E4FF')
        cv.drawRect(skia.Rect.MakeXYWH(wx + ww / 2 - 8, wy, 16, wh), P('#6A4AB8'))
        cv.drawRect(skia.Rect.MakeXYWH(wx, wy + wh / 2 - 8, ww, 16), P('#6A4AB8'))
        rrect(cv, wx - 60, wy + wh + 20, ww + 120, 40, 14, '#8A6AD8')
        birdie(cv, 620, 820, 360, t, body='#FF4F81', belly='#FFB0C8', look=(1, -0.5), mood='calm')


# 13 ─ « Le reste existe déjà. Simplement, tu ne le vois pas encore. »
class Reveal(Scene):
    zoom = (1.0, 1.15)

    def __init__(self):
        self.st = Stars(300, 613, rmax=2.6, colors=RICH)

    def static(self, cv):
        bg_lin(cv, '#1A0A4E', '#7A1A8A')

    def dyn(self, cv, t, d):
        k = ease((t - 0.6) / 1.6)
        self.st.draw(cv, t)
        # paysage lumineux qui se révèle
        cv.saveLayerAlpha(None, int(255 * k))
        glow(cv, 960, 620, 900, '#FFD34A', 200)
        for i, (col, y, amp) in enumerate([('#B13CFF', 760, 120), ('#7A3CFF', 840, 90), ('#3A1A7A', 930, 60)]):
            p = skia.Path(); p.moveTo(-400, H + 400); p.lineTo(-400, y)
            for x in range(-400, W + 440, 80):
                p.lineTo(x, y - amp * abs(math.sin(x * 0.003 + i)))
            p.lineTo(W + 400, H + 400); p.close()
            cv.drawPath(p, P(col))
        holo_hemis(cv, 960, 420, 220, 0.9, t)
        cv.restore()
        # fenêtre qui s'ouvre (deux battants qui s'écartent)
        for side in (-1, 1):
            off = side * (300 + 1300 * k)
            cv.save(); cv.translate(960 + off, 0)
            cv.drawRect(skia.Rect.MakeXYWH(-300 if side < 0 else 0, 0, 300, H), P('#2A1466'))
            cv.restore()
        birdie(cv, 960, 1160, 300, t, body='#2F6BFF', belly='#5AD7FF', look=(0, -1), mood='wow' if k > 0.3 else 'calm', facing=1)


SEGMENTS = [
    (EyeClose, "Il y a, juste devant toi, des couleurs que tes yeux ne verront jamais."),
    (Spectrum, "La lumière que tu vois n'est qu'une minuscule fenêtre. Tout le reste est invisible."),
    (Bee, "Les abeilles voient l'ultraviolet. Pour elles, les fleurs sont couvertes de motifs lumineux, comme des pistes d'atterrissage."),
    (Snake, "Les serpents voient la chaleur de ton corps, dans le noir complet."),
    (Shrimp, "La crevette-mante a seize types de récepteurs de couleur. Toi, tu en as trois."),
    (Elephant, "Les éléphants se parlent avec des sons trop graves pour nos oreilles."),
    (Neutrinos, "Et en ce moment, des milliers de milliards de particules venues du Soleil traversent ton corps."),
    (Sleep, "Chaque seconde. Sans que tu ne sentes rien."),
    (Bigger, "Le monde est infiniment plus grand que ce que tu perçois."),
    (Keyhole, "Alors ne le juge pas sur le petit bout que tu en vois."),
    (Desk, "Ta vie non plus."),
    (Window, "Ce que tu vis aujourd'hui n'est qu'une petite fenêtre."),
    (Reveal, "Le reste existe déjà. Simplement, tu ne le vois pas encore."),
]

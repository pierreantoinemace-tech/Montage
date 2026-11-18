"""Kit graphique « v2 » plus proche des références : 3D fil de fer, traînées néon, personnages de face expressifs."""
import math, random
import skia
from lib import *


# ------------------------------------------------------------------ 3D
class Cam:
    def __init__(self, yaw=0, pitch=0, dist=1800, f=1300, cx=W / 2, cy=H / 2):
        self.cy_, self.sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        self.cp_, self.sp_ = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
        self.dist, self.f, self.cx, self.cy = dist, f, cx, cy

    def p(self, x, y, z):
        x, z = x * self.cy_ + z * self.sy_, -x * self.sy_ + z * self.cy_
        y, z = y * self.cp_ - z * self.sp_, y * self.sp_ + z * self.cp_
        k = self.f / max(60, z + self.dist)
        return self.cx + x * k, self.cy + y * k, z, k


def wire_sphere(cv, cam, x, y, z, r, color, a=200, nlat=9, nlon=14, spin=0, w=2.2, half=None):
    for i in range(1, nlat):
        th = math.pi * i / nlat
        pts = [cam.p(x + r * math.sin(th) * math.cos(2 * math.pi * k / 40 + spin), y + r * math.cos(th), z + r * math.sin(th) * math.sin(2 * math.pi * k / 40 + spin)) for k in range(41)]
        _poly_line(cv, pts, color, a, w)
    for j in range(nlon):
        ph = 2 * math.pi * j / nlon + spin
        pts = [cam.p(x + r * math.sin(math.pi * k / 30) * math.cos(ph), y + r * math.cos(math.pi * k / 30), z + r * math.sin(math.pi * k / 30) * math.sin(ph)) for k in range(31)]
        _poly_line(cv, pts, color, a, w)


def _poly_line(cv, pts, color, a, w):
    p = skia.Path(); p.moveTo(pts[0][0], pts[0][1])
    for q in pts[1:]:
        p.lineTo(q[0], q[1])
    cv.drawPath(p, P(color, a, stroke=w))


def wire_plane(cv, cam, y, size, step, color, a=120, w=2, off=0.0):
    n = int(size / step)
    for i in range(-n, n + 1):
        v = i * step + (off % step)
        _poly_line(cv, [cam.p(v, y, -size), cam.p(v, y, size)], color, a, w)
        _poly_line(cv, [cam.p(-size, y, v), cam.p(size, y, v)], color, a, w)


def neon(cv, pts, color, w=8, a=255, arrow=False, glow_w=26):
    """Traînée néon (avec halo) le long d'une polyligne, flèche optionnelle au bout."""
    if len(pts) < 2:
        return
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    cv.drawPath(p, P(color, a * 0.35, stroke=glow_w, blur=10))
    cv.drawPath(p, P(color, a, stroke=w))
    cv.drawPath(p, P('#ffffff', a * 0.6, stroke=w * 0.3))
    if arrow:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        ang = math.atan2(y1 - y0, x1 - x0)
        L = w * 3.2
        poly(cv, [(x1 + math.cos(ang) * L * 0.6, y1 + math.sin(ang) * L * 0.6),
                  (x1 + math.cos(ang + 2.4) * L, y1 + math.sin(ang + 2.4) * L),
                  (x1 + math.cos(ang - 2.4) * L, y1 + math.sin(ang - 2.4) * L)], color, a)


def sparkle(cv, x, y, r, color='#ffffff', a=255):
    poly(cv, [(x, y - r), (x + r * 0.18, y), (x, y + r), (x - r * 0.18, y)], color, a)
    poly(cv, [(x - r, y), (x, y - r * 0.18), (x + r, y), (x, y + r * 0.18)], color, a)
    glow(cv, x, y, r * 1.6, color, a * 0.5)


def shade_ball(cv, x, y, r, light, dark, rim=None, a=255):
    cv.drawCircle(x, y, r, P(shader=rad(x - r * 0.35, y - r * 0.4, r * 1.6, [light, dark]), a=a))
    if rim:
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), 20, 120)
        cv.drawPath(p, P(rim, 180 * a / 255, stroke=r * 0.07))


class Grain:
    pass


# ------------------------------------------------------------------ personnages de face
def char_front(cv, x, y, s, t=0.0, skin='#F2A97E', hair='#3A1E14', top='#3C4CC8', pants='#1E1F5C',
               mood='smile', look=(0.0, 0.0), arms='down', hairstyle=0, blink=True, bob=True, scale_y=1.0):
    """Personnage de face, grosse tête, yeux expressifs. (x,y) = pieds, s ≈ rayon de la tête / 1."""
    by = 0.06 * s * math.sin(t * 4) if bob else 0
    cv.save(); cv.translate(x, y); cv.scale(1, scale_y); cv.translate(-x, -y)
    dark_top = mix(top, '#000000', 0.25)
    # jambes + chaussures
    rrect(cv, x - 0.55 * s, y - 1.6 * s, 0.45 * s, 1.55 * s, 0.2 * s, pants)
    rrect(cv, x + 0.1 * s, y - 1.6 * s, 0.45 * s, 1.55 * s, 0.2 * s, mix(pants, '#000000', 0.15))
    oval(cv, x - 0.38 * s, y - 0.05 * s, 0.38 * s, 0.17 * s, '#F4F0FF')
    oval(cv, x + 0.38 * s, y - 0.05 * s, 0.38 * s, 0.17 * s, '#F4F0FF')
    # bras
    ty = y - 3.15 * s + by
    def arm(side, ang, hand=True):
        cv.save(); cv.translate(x + side * 0.82 * s, ty + 0.35 * s); cv.rotate(ang * side)
        rrect(cv, -0.2 * s, 0, 0.4 * s, 1.35 * s, 0.2 * s, dark_top if side > 0 else top)
        if hand:
            circle(cv, 0, 1.42 * s, 0.22 * s, skin)
        cv.restore()
    poses = {'down': (8, 8), 'up': (155 + 10 * math.sin(t * 8), 155 + 10 * math.sin(t * 8 + 1)), 'wave': (8, 140 + 25 * math.sin(t * 9)),
             'hips': (35, 35), 'out': (70, 70), 'hug': (-35, -35)}
    al, ar = poses.get(arms, (8, 8))
    if arms != 'hug':
        arm(-1, al); arm(1, ar)
    # torse (sweat à capuche)
    rrect(cv, x - 0.95 * s, ty, 1.9 * s, 1.75 * s, 0.55 * s, top)
    rrect(cv, x - 0.95 * s, ty + 1.3 * s, 1.9 * s, 0.45 * s, 0.2 * s, dark_top)
    rrect(cv, x - 0.55 * s, ty + 0.85 * s, 1.1 * s, 0.4 * s, 0.15 * s, dark_top)
    oval(cv, x, ty + 0.05 * s, 0.75 * s, 0.28 * s, dark_top)
    for sx in (-0.22, 0.22):
        cv.drawLine(x + sx * s, ty + 0.15 * s, x + sx * s, ty + 0.75 * s, P('#F4F0FF', 230, stroke=0.06 * s))
    rrect(cv, x - 0.95 * s, ty + 0.1 * s, 0.25 * s, 1.5 * s, 0.12 * s, '#ffffff', 40)
    if arms == 'hug':
        rrect(cv, x - 0.95 * s, ty + 0.75 * s, 1.9 * s, 0.38 * s, 0.19 * s, dark_top)
        circle(cv, x - 0.6 * s, ty + 0.95 * s, 0.22 * s, skin); circle(cv, x + 0.6 * s, ty + 0.95 * s, 0.22 * s, skin)
    # tête
    hx, hy = x, ty - 0.95 * s
    if hairstyle == 1:
        circle(cv, hx, hy - 0.25 * s, 1.25 * s, hair)
    if hairstyle == 2:
        rrect(cv, hx - 1.1 * s, hy - 0.6 * s, 2.2 * s, 2.0 * s, 0.8 * s, hair)
    rrect(cv, hx - 0.25 * s, hy + 0.7 * s, 0.5 * s, 0.45 * s, 0.15 * s, mix(skin, '#000000', 0.15))
    circle(cv, hx - 0.98 * s, hy + 0.05 * s, 0.22 * s, mix(skin, '#000000', 0.08))
    circle(cv, hx + 0.98 * s, hy + 0.05 * s, 0.22 * s, mix(skin, '#000000', 0.08))
    circle(cv, hx, hy, 1.0 * s, skin)
    oval(cv, hx + 0.35 * s, hy + 0.45 * s, 0.6 * s, 0.45 * s, mix(skin, '#000000', 0.07), 160)
    if hairstyle in (0, 2):
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx - 1.02 * s, hy - 1.05 * s, hx + 1.02 * s, hy + 0.9 * s), 180, 180); p.close()
        cv.drawPath(p, P(hair))
        oval(cv, hx - 0.35 * s, hy - 0.55 * s, 0.55 * s, 0.28 * s, hair)
        oval(cv, hx + 0.45 * s, hy - 0.6 * s, 0.5 * s, 0.22 * s, hair)
    elif hairstyle == 1:
        for k in range(7):
            circle(cv, hx - 0.85 * s + k * 0.28 * s, hy - 0.68 * s + 0.08 * s * math.sin(k * 2), 0.28 * s, hair)
    elif hairstyle == 3:  # bonnet / capuche
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx - 1.05 * s, hy - 1.1 * s, hx + 1.05 * s, hy + 0.8 * s), 180, 180); p.close()
        cv.drawPath(p, P(top))
        rrect(cv, hx - 1.05 * s, hy - 0.45 * s, 2.1 * s, 0.3 * s, 0.15 * s, dark_top)
    # yeux
    bl = 1.0
    if blink:
        ph = (t * 0.7 + x * 0.001) % 3.0
        if ph < 0.12:
            bl = 0.1
    ex = 0.38 * s
    eyy = hy + 0.05 * s
    lx, ly = look
    for side in (-1, 1):
        cx = hx + side * ex
        if mood == 'wink' and side == 1:
            p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - 0.24 * s, eyy - 0.18 * s, cx + 0.24 * s, eyy + 0.2 * s), 200, 140)
            cv.drawPath(p, P('#1A1030', 255, stroke=0.09 * s))
            continue
        if mood in ('happy', 'laugh') :
            p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(cx - 0.24 * s, eyy - 0.1 * s, cx + 0.24 * s, eyy + 0.3 * s), 200, 140)
            cv.drawPath(p, P('#1A1030', 255, stroke=0.09 * s))
            continue
        ry = (0.36 if mood == 'scared' else 0.3) * s * bl
        oval(cv, cx, eyy, 0.26 * s, ry, '#FFFFFF')
        if bl > 0.5:
            pr = 0.11 * s if mood == 'scared' else 0.15 * s
            circle(cv, cx + lx * 0.09 * s, eyy + ly * 0.1 * s + 0.03 * s, pr, '#1A1030')
            circle(cv, cx + lx * 0.09 * s - 0.05 * s, eyy + ly * 0.1 * s - 0.03 * s, 0.05 * s, '#FFFFFF')
    # sourcils
    br = {'smile': 0, 'happy': -6, 'laugh': -8, 'wink': -4, 'scared': 18, 'sad': 16, 'wow': -14, 'calm': 0}.get(mood, 0)
    for side in (-1, 1):
        cx = hx + side * ex
        cv.save(); cv.translate(cx, eyy - 0.43 * s - (0.08 * s if mood in ('wow', 'scared') else 0)); cv.rotate(-br * side)
        rrect(cv, -0.2 * s, -0.05 * s, 0.4 * s, 0.1 * s, 0.05 * s, mix(hair, '#000000', 0.2))
        cv.restore()
    # nez + joues
    p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx - 0.09 * s, hy + 0.18 * s, hx + 0.09 * s, hy + 0.36 * s), -30, 200)
    cv.drawPath(p, P(mix(skin, '#000000', 0.3), 255, stroke=0.05 * s))
    for side in (-1, 1):
        oval(cv, hx + side * 0.62 * s, hy + 0.38 * s, 0.17 * s, 0.1 * s, '#FF6F91', 120)
    # bouche
    my = hy + 0.55 * s
    if mood in ('laugh', 'wow'):
        oval(cv, hx, my + 0.05 * s, 0.24 * s if mood == 'laugh' else 0.13 * s, 0.17 * s, '#6A1030')
        oval(cv, hx, my + 0.14 * s, 0.12 * s if mood == 'laugh' else 0.07 * s, 0.06 * s, '#FF6F91')
    elif mood in ('scared',):
        p = skia.Path(); p.moveTo(hx - 0.2 * s, my + 0.08 * s)
        for k in range(1, 5):
            p.lineTo(hx - 0.2 * s + k * 0.1 * s, my + (0.0 if k % 2 else 0.08) * s)
        cv.drawPath(p, P('#6A1030', 255, stroke=0.05 * s))
    elif mood == 'sad':
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx - 0.18 * s, my, hx + 0.18 * s, my + 0.25 * s), 200, 140)
        cv.drawPath(p, P('#6A1030', 255, stroke=0.06 * s))
    else:
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx - 0.24 * s, my - 0.12 * s, hx + 0.24 * s, my + 0.12 * s), 20, 140)
        cv.drawPath(p, P('#6A1030', 255, stroke=0.065 * s))
    cv.restore()


# ------------------------------------------------------------------ dinosaure (brachiosaure jovial)
def dino(cv, x, y, s, t, body='#3FC46A', belly='#B6F07A', santa=False, mood='happy', look_up=0.0):
    dark = mix(body, '#000000', 0.25)
    # queue
    p = skia.Path(); p.moveTo(x - 1.2 * s, y - 1.4 * s); p.cubicTo(x - 2.6 * s, y - 1.3 * s, x - 3.3 * s, y - 0.4 * s, x - 3.6 * s + 0.15 * s * math.sin(t * 3), y - 0.6 * s)
    cv.drawPath(p, P(dark, 255, stroke=0.55 * s))
    for lx in (-0.95, 0.7):
        rrect(cv, x + lx * s - 0.25 * s, y - 1.3 * s, 0.55 * s, 1.3 * s, 0.25 * s, dark)
    oval(cv, x, y - 1.75 * s, 1.55 * s, 0.95 * s, body)
    oval(cv, x + 0.1 * s, y - 1.35 * s, 1.1 * s, 0.45 * s, belly, 220)
    for lx in (-0.65, 1.0):
        rrect(cv, x + lx * s - 0.27 * s, y - 1.25 * s, 0.58 * s, 1.3 * s, 0.27 * s, body)
        for k in range(3):
            circle(cv, x + lx * s - 0.15 * s + k * 0.16 * s, y - 0.02 * s, 0.07 * s, '#F4F0FF')
    for k in range(5):
        circle(cv, x - 0.9 * s + k * 0.4 * s, y - 2.35 * s + 0.1 * s * math.sin(k), 0.12 * s, dark, 200)
    # cou
    sway = 0.15 * s * math.sin(t * 1.6)
    hx, hy = x + 2.1 * s + sway, y - 5.4 * s - look_up * 0.6 * s
    p = skia.Path(); p.moveTo(x + 1.0 * s, y - 2.0 * s); p.cubicTo(x + 1.9 * s, y - 2.9 * s, hx - 0.4 * s, hy + 1.4 * s, hx, hy)
    cv.drawPath(p, P(body, 255, stroke=0.75 * s))
    cv.drawPath(p, P(belly, 160, stroke=0.25 * s))
    # tête
    oval(cv, hx + 0.25 * s, hy, 0.75 * s, 0.55 * s, body)
    oval(cv, hx + 0.7 * s, hy + 0.15 * s, 0.4 * s, 0.32 * s, body)
    circle(cv, hx + 0.95 * s, hy + 0.02 * s, 0.05 * s, dark)
    ex, ey = hx + 0.25 * s, hy - 0.12 * s
    if mood == 'wow':
        oval(cv, ex, ey, 0.2 * s, 0.24 * s, '#ffffff'); circle(cv, ex + 0.03 * s, ey - 0.08 * s * look_up, 0.1 * s, '#1A1030')
    else:
        oval(cv, ex, ey, 0.18 * s, 0.2 * s, '#ffffff'); circle(cv, ex + 0.05 * s, ey, 0.1 * s, '#1A1030'); circle(cv, ex + 0.02 * s, ey - 0.04 * s, 0.035 * s, '#ffffff')
    if mood == 'wow':
        oval(cv, hx + 0.75 * s, hy + 0.3 * s, 0.1 * s, 0.12 * s, '#6A1030')
    else:
        p = skia.Path(); p.addArc(skia.Rect.MakeLTRB(hx + 0.35 * s, hy + 0.05 * s, hx + 0.95 * s, hy + 0.38 * s), 20, 120)
        cv.drawPath(p, P('#1A1030', 255, stroke=0.06 * s))
    oval(cv, hx + 0.55 * s, hy + 0.2 * s, 0.1 * s, 0.06 * s, '#FF6F91', 150)
    if santa:
        cv.save(); cv.translate(hx + 0.1 * s, hy - 0.45 * s); cv.rotate(-15)
        p = skia.Path(); p.moveTo(-0.6 * s, 0); p.quadTo(-0.1 * s, -1.2 * s, 0.9 * s + 0.1 * s * math.sin(t * 3), -0.6 * s); p.lineTo(0.6 * s, 0); p.close()
        cv.drawPath(p, P('#E8243C'))
        rrect(cv, -0.7 * s, -0.12 * s, 1.4 * s, 0.28 * s, 0.14 * s, '#ffffff')
        circle(cv, 0.95 * s + 0.1 * s * math.sin(t * 3), -0.6 * s, 0.18 * s, '#ffffff')
        cv.restore()


def calendar_page(cv, x, y, w, h, month, day, color, font, a=255, flip=0.0):
    """Page d'éphéméride : bandeau couleur + gros chiffre."""
    cv.save(); cv.translate(x, y)
    if flip:
        cv.scale(1, max(0.02, 1 - flip))
    rrect(cv, -w / 2 + 10, -h / 2 + 16, w, h, 24, '#000000', 70 * a / 255)
    rrect(cv, -w / 2, -h / 2, w, h, 24, '#FFF8EE', a)
    rrect(cv, -w / 2, -h / 2, w, h * 0.28, 24, color, a)
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2 + h * 0.16, w, h * 0.12), P(color, a))
    for k in (-0.25, 0.25):
        circle(cv, k * w, -h / 2 + 4, 14, '#1A1030', a)
    f = skia.Font(font, h * 0.13)
    tw = f.measureText(month)
    cv.drawString(month, -tw / 2, -h / 2 + h * 0.2, f, P('#ffffff', a))
    f2 = skia.Font(font, h * 0.5)
    tw = f2.measureText(day)
    cv.drawString(day, -tw / 2, h * 0.3, f2, P('#1A1030', a))
    cv.restore()

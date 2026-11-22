"""Bibliothèque de symboles psychiques nets (contour sombre épais + aplats), coordonnées en design 1080x1920."""
import math, skia
from lib import P, mix

OUT = '#120624'
PAL = ['#F0EBBE', '#C8B8FF', '#9FE8D8', '#FFB8D0', '#A8D8FF', '#FFD8A0']
KINDS = ['eye', 'tri_eye', 'moon', 'spiral', 'star4', 'star8', 'planet', 'hourglass', 'clock', 'flower', 'hexa', 'sun', 'infinity', 'diamond']


def _w(s): return max(2.2, s * 0.075)


def ofill(cv, path, col, s, a=255):
    cv.drawPath(path, P(col, a))
    cv.drawPath(path, P(OUT, a, stroke=_w(s)))


def ostroke(cv, path, col, w, s, a=255):
    cv.drawPath(path, P(OUT, a, stroke=w + 2 * _w(s)))
    cv.drawPath(path, P(col, a, stroke=w))


def poly(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); return p


def star(n, ro, ri, rot=0):
    return poly([((ro if i % 2 == 0 else ri) * math.cos(rot + i * math.pi / n - math.pi / 2),
                  (ro if i % 2 == 0 else ri) * math.sin(rot + i * math.pi / n - math.pi / 2)) for i in range(2 * n)])


def eye(cv, s, col, t=0, look=(0, 0), a=255, seed=0):
    p = skia.Path(); p.moveTo(-s, 0); p.quadTo(0, -s * 0.95, s, 0); p.quadTo(0, s * 0.95, -s, 0); p.close()
    blink = ((t * 0.5 + seed * 0.29) % 3.0) < 0.12
    if blink:
        cv.drawPath(p, P(col, a)); cv.drawLine(-s, 0, s, 0, P(OUT, a, stroke=_w(s))); cv.drawPath(p, P(OUT, a, stroke=_w(s))); return
    cv.drawPath(p, P('#FBF6FF', a))
    cv.save(); cv.clipPath(p, doAntiAlias=True)
    ix, iy = look[0] * s * 0.3, look[1] * s * 0.2
    cv.drawCircle(ix, iy, s * 0.4, P(col if col != '#F0EBBE' else '#2DE2C6', a))
    cv.drawCircle(ix, iy, s * 0.4, P(OUT, a, stroke=_w(s) * 0.6))
    cv.drawCircle(ix, iy, s * 0.18, P(OUT, a))
    cv.drawCircle(ix - s * 0.12, iy - s * 0.1, s * 0.08, P('#FFFFFF', a))
    cv.restore()
    cv.drawPath(p, P(OUT, a, stroke=_w(s)))


def sym(cv, kind, x, y, s, rot=0, col='#F0EBBE', t=0, a=255, seed=0):
    if s < 1.5 or a <= 2: return
    a = int(min(255, a))
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    w = _w(s)
    if kind == 'eye':
        eye(cv, s, col, t, (math.sin(t + seed), math.cos(t * 0.7 + seed)), a, seed)
    elif kind == 'tri_eye':
        ofill(cv, poly([(0, -s), (0.87 * s, 0.5 * s), (-0.87 * s, 0.5 * s)]), col, s, a)
        cv.save(); cv.translate(0, 0.1 * s); eye(cv, s * 0.38, '#2DE2C6', t, (0, 0), a, seed); cv.restore()
    elif kind == 'moon':
        p = skia.Op(skia.Path().addCircle(0, 0, s), skia.Path().addCircle(0.42 * s, -0.18 * s, 0.82 * s), skia.PathOp.kDifference_PathOp)
        ofill(cv, p, col, s, a)
    elif kind == 'spiral':
        p = skia.Path()
        for i in range(61):
            u = i / 60; ang = u * 4 * math.pi + t * 2; r = s * u
            (p.moveTo if i == 0 else p.lineTo)(r * math.cos(ang), r * math.sin(ang))
        ostroke(cv, p, col, w * 1.3, s, a)
    elif kind == 'star4':
        ofill(cv, star(4, s, s * 0.3), col, s, a)
    elif kind == 'star8':
        ofill(cv, star(8, s, s * 0.55), col, s, a)
        cv.drawCircle(0, 0, s * 0.2, P(OUT, a))
    elif kind == 'planet':
        ring = skia.Path(); ring.addOval(skia.Rect.MakeLTRB(-s, -0.28 * s, s, 0.28 * s))
        cv.save(); cv.rotate(-18)
        ofill(cv, skia.Path().addCircle(0, 0, 0.55 * s), col, s, a)
        cv.drawLine(-0.45 * s, -0.1 * s, 0.45 * s, -0.1 * s, P(mix(col, OUT, 0.3), a, stroke=w))
        ostroke(cv, ring, mix(col, '#FFFFFF', 0.4), w, s, a)
        cv.restore()
    elif kind == 'hourglass':
        ofill(cv, poly([(-0.6 * s, -s), (0.6 * s, -s), (0, 0)]), col, s, a)
        ofill(cv, poly([(0, 0), (0.6 * s, s), (-0.6 * s, s)]), col, s, a)
        f = (t * 0.4 + seed) % 1
        ofill(cv, poly([(-0.6 * s * f, s * (1 - f)), (0.6 * s * f, s * (1 - f)), (0.6 * s, s), (-0.6 * s, s)]), mix(col, OUT, 0.45), s * 0.5, a)
        cv.drawLine(-0.75 * s, -s, 0.75 * s, -s, P(OUT, a, stroke=w * 1.6)); cv.drawLine(-0.75 * s, s, 0.75 * s, s, P(OUT, a, stroke=w * 1.6))
    elif kind == 'clock':
        ofill(cv, skia.Path().addCircle(0, 0, s), col, s, a)
        for k in range(12):
            g = k * math.pi / 6
            cv.drawLine(0.78 * s * math.cos(g), 0.78 * s * math.sin(g), 0.9 * s * math.cos(g), 0.9 * s * math.sin(g), P(OUT, a, stroke=w * 0.7))
        g1, g2 = t * 6 + seed, t * 0.5 + seed
        cv.drawLine(0, 0, 0.7 * s * math.cos(g1), 0.7 * s * math.sin(g1), P(OUT, a, stroke=w))
        cv.drawLine(0, 0, 0.45 * s * math.cos(g2), 0.45 * s * math.sin(g2), P(OUT, a, stroke=w * 1.4))
    elif kind == 'flower':
        r = s * 0.45
        for k in range(7):
            cx, cy = (0, 0) if k == 0 else (r * math.cos(k * math.pi / 3), r * math.sin(k * math.pi / 3))
            ostroke(cv, skia.Path().addCircle(cx, cy, r), col, w * 0.8, s * 0.6, a)
    elif kind == 'hexa':
        for r0 in (0, math.pi):
            ostroke(cv, poly([(s * math.cos(r0 + k * 2 * math.pi / 3 - math.pi / 2), s * math.sin(r0 + k * 2 * math.pi / 3 - math.pi / 2)) for k in range(3)]), col, w, s, a)
    elif kind == 'sun':
        ofill(cv, star(12, s, s * 0.62, t * 0.5), mix(col, '#FFFFFF', 0.2), s, a)
        ofill(cv, skia.Path().addCircle(0, 0, s * 0.45), col, s, a)
    elif kind == 'infinity':
        p = skia.Path()
        for i in range(81):
            g = i / 80 * 2 * math.pi; d = 1 + math.sin(g) ** 2
            (p.moveTo if i == 0 else p.lineTo)(s * math.cos(g) / d, s * math.sin(g) * math.cos(g) / d)
        p.close(); ostroke(cv, p, col, w * 1.4, s, a)
    elif kind == 'diamond':
        ofill(cv, poly([(0, -s), (0.62 * s, 0), (0, s), (-0.62 * s, 0)]), col, s, a)
        cv.drawLine(-0.62 * s, 0, 0.62 * s, 0, P(OUT, a, stroke=w * 0.7)); cv.drawLine(0, -s, 0, s, P(mix(col, OUT, 0.3), a, stroke=w * 0.5))
    cv.restore()

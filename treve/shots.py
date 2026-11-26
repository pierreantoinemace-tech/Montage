"""Plans 3D de « La trêve de Noël 1914 » (Blender/EEVEE). Usage :
blender -b --python shots.py -- <plan> <durée_s> <sortie> <rx> <ry> [t_aperçu]"""
import sys, os, math, random
sys.path.insert(0, '/home/user/Montage/test3d')
import bpy, lib3d as L
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:]
SHOT, DUR, OUT, RX, RY = a[0], float(a[1]), a[2], int(a[3]), int(a[4])
PREV = float(a[5]) if len(a) > 5 else None
FPS = 30
N = max(2, int(round(DUR * FPS)))
sc = L.setup(RX, RY, samples=int(os.environ.get('SAMPLES', '16')), fps=FPS)
sc.frame_start, sc.frame_end = 1, N
ANIM = []
R = random.Random(1)


def F(t): return 1 + t * FPS
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def M(name, col, **k): return L.mat(name, col, **k)


def mkcam(lens=35):
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = lens; return c


def cam_path(c, p0, p1, look0, look1, t0=0, t1=None):
    t1 = DUR if t1 is None else t1
    for t, p, lk in ((t0, p0, look0), (t1, p1, look1)):
        c.location = p; d = Vector(lk) - Vector(p); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        c.keyframe_insert('location', frame=F(t)); c.keyframe_insert('rotation_euler', frame=F(t))


def box(loc, scale, m, bev=0.04, rot=(0, 0, 0), name='bx'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.scale = scale; o.name = name
    o.data.materials.append(m)
    if bev: b = o.modifiers.new('b', 'BEVEL'); b.width = bev; b.segments = 2
    return o


def ground(col, size=80, z=0.0, bump=0.25, seed=0, name='sol'):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z)); g = bpy.context.object; g.name = name
    g.modifiers.new('sub', 'SUBSURF').levels = 5; g.modifiers['sub'].subdivision_type = 'SIMPLE'
    tx = bpy.data.textures.new('bosses%d' % seed, 'CLOUDS'); tx.noise_scale = 1.6
    d = g.modifiers.new('d', 'DISPLACE'); d.texture = tx; d.strength = bump; d.mid_level = 0.5
    bpy.ops.object.shade_smooth(); g.data.materials.append(M(name + col, col, rough=0.85)); return g


# ---------------- soldats (perso aux trois yeux, haut étroit) ----------------
SOLDIERS = []
UNIF = {'en': '#8A7A4E', 'de': '#6E7A72'}
SCARVES = ['#B83A3A', '#3A7A4A', '#C8A040', '#3A5AA8', '#8A3A7A']


def pose_fn(kind, ph=0.0):
    def f(t, sx):
        if kind == 'down': return (0.22 * sx, -0.15, -1.15 + 0.03 * math.sin(t * 2 + ph))
        if kind == 'warm': return (0.1 * sx, -0.8, -0.7 + 0.04 * math.sin(t * 3 + sx))
        if kind == 'up': return (0.45 * sx + 0.05 * math.sin(t * 5 + sx), -0.1, 1.0)
        if kind == 'wave':
            return (0.55 + 0.18 * math.sin(t * 9 + ph), -0.1, 0.9) if sx > 0 else (-0.22, -0.15, -1.15)
        if kind == 'cheer': return (0.5 * sx, -0.1, 0.65 + 0.25 * abs(math.sin(t * 5 + ph + sx)))
        if kind == 'give': return (0.05, -1.15, -0.2) if sx > 0 else (-0.22, -0.15, -1.15)
        if kind == 'take': return (-0.05, -1.15, -0.25) if sx < 0 else (0.22, -0.15, -1.15)
        if kind == 'sing': return (0.14 * sx, -0.55, -0.6 + 0.06 * math.sin(t * 4 + ph))
        if kind == 'run': return (0.25 * sx, -0.15 + 0.4 * math.sin(t * 11 + ph + (math.pi if sx > 0 else 0)), -0.95)
        if kind == 'laugh': return (0.25 * sx, -0.35, -0.9 + 0.08 * math.sin(t * 12 + ph))
        if kind == 'point': return (0.4, -0.9, 0.2) if sx > 0 else (-0.22, -0.15, -1.15)
        return (0.22 * sx, -0.15, -1.15)
    return f


def soldier(x, y, s=0.5, side='en', rot=0.0, z=0.0, eyes='open', look=(0, 0), hero=False, pose='down', path=None, bob=0.025,
            scarf=None, sing=False, old=False, mous=None, hat=True, poses=None):
    """Crée un soldat debout au sol (z = niveau du sol). path(t) -> (dx, dy, dz) ; poses : liste [(t0, 'pose'), ...]."""
    Z = 2.8 * s
    P = lambda px, py, pz: (px * s, py * s, Z + pz * s)
    before = set(bpy.data.objects)
    root = L.character((0, 0, Z), s, 0, eyes, old=old, look=look, robe=UNIF[side], nhair=0, body=True, hair_cols=('#5A3A24', '#7A5234'))
    for o in list(root.children):                                   # bras refaits (animés), lumière du 3e œil seulement pour les héros
        if o.name.startswith(('arm', 'hand')) or (o.type == 'LIGHT' and not hero): bpy.data.objects.remove(o, do_unlink=True)
    kids = []
    um = M('unif' + side, UNIF[side], rough=0.75)
    if hat:
        if side == 'en':                                            # casquette britannique 1914
            kids.append(L.cyl(P(0, 0.03, 0.78), 0.75 * s, 0.77 * s, 0.32 * s, M('casq_en', '#7A6A3E', rough=0.8), name='hat'))
            kids.append(L.sphere(P(0, 0.03, 0.97), (0.86 * s, 0.82 * s, 0.11 * s), M('casq_en', '#7A6A3E', rough=0.8), name='hat'))
            kids.append(L.sphere(P(0, -0.62, 0.66), (0.45 * s, 0.3 * s, 0.045 * s), M('visiere', '#3A2A1A', rough=0.35), name='hat'))
            kids.append(L.sphere(P(0, -0.76, 0.8), (0.07 * s, 0.02 * s, 0.07 * s), M('insigne', '#E0B850', metal=0.8, rough=0.25), seg=16, name='hat'))
        else:                                                       # casque à pointe
            hm = M('cuir', '#23232A', rough=0.28, spec=0.7)
            kids.append(L.cyl(P(0, 0.03, 0.77), 0.76 * s, 0.76 * s, 0.3 * s, hm, name='hat'))
            kids.append(L.sphere(P(0, 0.03, 0.9), (0.76 * s, 0.73 * s, 0.5 * s), hm, name='hat'))
            kids.append(L.cyl(P(0, 0.03, 1.5), 0.08 * s, 0.0, 0.38 * s, M('laiton', '#E0B850', metal=0.85, rough=0.25), name='hat'))
            kids.append(L.sphere(P(0, -0.7, 0.85), (0.2 * s, 0.05 * s, 0.17 * s), M('laiton', '#E0B850', metal=0.85, rough=0.25), seg=16, name='hat'))
            kids.append(L.sphere(P(0, -0.6, 0.64), (0.45 * s, 0.3 * s, 0.04 * s), hm, name='hat'))
    kids.append(L.sphere(P(0, 0.06, -1.36), (0.45 * s, 0.36 * s, 0.14 * s), M('echarpe' + (scarf or SCARVES[len(SOLDIERS) % 5]), scarf or SCARVES[len(SOLDIERS) % 5], rough=0.95), seg=24, name='scarf'))
    kids.append(L.cyl(P(0, 0.08, -2.15), 0.52 * s, 0.53 * s, 0.1 * s, M('ceinture', '#4A3420', rough=0.5), name='belt'))
    kids[-1].scale.y = 0.74
    for k, bz in enumerate((-1.6, -1.9, -2.4)):
        r = 0.62 - (bz + 2.8) / 1.5 * 0.28
        kids.append(L.sphere(P(0, 0.08 - 0.72 * r - 0.02, bz), (0.045 * s, 0.02 * s, 0.045 * s), M('bouton', '#E8C050', metal=0.85, rough=0.25), seg=12, name='btn'))
    if mous: kids.append(L.curve([P(-0.2, -0.6, -0.34), P(0, -0.66, -0.3), P(0.2, -0.6, -0.34)], [0.6, 1, 0.6], M('moust' + mous, mous, rough=0.8), bevel=0.05 * s, name='moust'))
    mouth = None
    if sing:
        mouth = L.sphere(P(0, -0.6, -0.56), (0.09 * s, 0.03 * s, 0.07 * s), M('bouche', '#2A0E1E', rough=0.6), seg=16, name='omouth'); kids.append(mouth)
    arms = []
    for sx in (-1, 1):
        sh = (0.3 * sx, 0.05, -1.45)
        cu = L.curve([P(*sh), P(*sh), P(*sh)], [1, 0.95, 0.9], um, bevel=0.085 * s, name='arm')
        hd = L.sphere(P(*sh), (0.1 * s, 0.1 * s, 0.11 * s), M('skin', '#6EC3D6', rough=0.45, sss=0.15), seg=16, name='hand')
        arms.append((sx, sh, cu, hd)); kids += [cu, hd]
    for o in kids: o.parent = root
    root.location = (x, y, z); root.rotation_euler = (0, 0, rot)
    ph = R.uniform(0, 6.28)
    seq = poses or [(0, pose)]
    fns = [(t0, pose_fn(p, ph)) for t0, p in seq]
    info = dict(root=root, arms=arms, P=P, base=(x, y, z), path=path, bob=bob, ph=ph, fns=fns, mouth=mouth, s=s)
    SOLDIERS.append(info)
    return info


def hand_world(info, sx):
    for a_ in info['arms']:
        if a_[0] == sx: return info['root'].matrix_world @ a_[3].location


def update_soldiers(t):
    for i in SOLDIERS:
        x, y, z = i['base']; dx = dy = dz = 0.0
        if i['path']: dx, dy, dz = i['path'](t)
        i['root'].location = (x + dx, y + dy, z + dz + i['bob'] * abs(math.sin(t * 2.2 + i['ph'])))
        cur = [f for t0, f in i['fns'] if t >= t0]
        prv = [(t0, f) for t0, f in i['fns'] if t >= t0]
        f = cur[-1] if cur else i['fns'][0][1]
        t0 = prv[-1][0] if prv else 0
        g = prv[-2][1] if len(prv) > 1 else f
        u = ease((t - t0) / 0.35)
        for sx, sh, cu, hd in i['arms']:
            p1, p0 = f(t, sx), g(t, sx)
            tg = tuple(p0[k] * (1 - u) + p1[k] * u for k in range(3))
            hp = (sh[0] + tg[0], sh[1] + tg[1], sh[2] + tg[2])
            el = ((sh[0] + hp[0]) / 2 + 0.18 * sx, (sh[1] + hp[1]) / 2 + 0.06, (sh[2] + hp[2]) / 2 - 0.08)
            P = i['P']
            for bp, q in zip(cu.data.splines[0].bezier_points, (sh, el, hp)): bp.co = P(*q)
            hd.location = P(*hp)
        if i['mouth']: i['mouth'].scale.z = (0.03 + 0.06 * abs(math.sin(t * 4.2 + i['ph']))) * i['s']


ANIM.append(update_soldiers)


# ---------------- accessoires vivants ----------------
def flicker_light(loc, col, e, r=0.1):
    bpy.ops.object.light_add(type='POINT', location=loc); lt = bpy.context.object; lt.data.energy = e
    c = col.lstrip('#'); lt.data.color = tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)); lt.data.shadow_soft_size = r
    ph = R.uniform(0, 9)
    ANIM.append(lambda t: setattr(lt.data, 'energy', e * (0.85 + 0.1 * math.sin(t * 13 + ph) + 0.06 * math.sin(t * 31 + ph * 2))))
    return lt


def flames(objs):
    base = [(o, tuple(o.scale), R.uniform(0, 9)) for o in objs]
    ANIM.append(lambda t: [setattr(o, 'scale', (sx_ * (0.9 + 0.1 * math.sin(t * 17 + p)), sy_ * (0.9 + 0.1 * math.sin(t * 17 + p)), sz_ * (0.8 + 0.25 * abs(math.sin(t * 11 + p * 1.3)))))
                           for o, (sx_, sy_, sz_), p in base])


def xmas_tree(loc, h=1.2, light=True, candles=10):
    x, y, z = loc
    L.cyl((x, y, z + 0.12 * h), 0.06 * h, 0.06 * h, 0.25 * h, M('tronc', '#5A3A2A', rough=0.9), name='tronc')
    for k in range(3):
        r = 0.45 * h * (1 - k * 0.27); zz = z + 0.3 * h + k * 0.25 * h
        L.cyl((x, y, zz + 0.2 * h), r, 0.02, 0.5 * h, M('sapin', '#1E5A44', rough=0.75), name='sapin')
    fl = []
    for k in range(candles):
        tier = k % 3; a = k * 2.39; r = 0.38 * h * (1 - tier * 0.27) * 0.8; zz = z + 0.32 * h + tier * 0.25 * h + 0.05 * h
        cx, cy = x + r * math.cos(a), y + r * math.sin(a)
        L.cyl((cx, cy, zz + 0.04 * h), 0.012 * h, 0.012 * h, 0.08 * h, M('bougie', '#FFF4E0', rough=0.5), name='bougie')
        fl.append(L.sphere((cx, cy, zz + 0.1 * h), (0.018 * h, 0.018 * h, 0.035 * h), M('flamme', '#FFC060', emit=14), seg=8, name='flamme'))
    L.sphere((x, y, z + 1.1 * h), (0.05 * h,) * 3, M('etoile_sapin', '#FFE080', emit=8), seg=12, name='etoile')
    flames(fl)
    if light: flicker_light((x, y - 0.2 * h, z + 0.7 * h), '#FFB060', 60 * h, 0.3)


def brazier(loc, s=1.0):
    x, y, z = loc
    L.cyl((x, y, z + 0.3 * s), 0.25 * s, 0.3 * s, 0.6 * s, M('brasero', '#2A2422', rough=0.6, metal=0.5), name='brasero')
    L.sphere((x, y, z + 0.6 * s), (0.22 * s, 0.22 * s, 0.08 * s), M('braise', '#FF5A20', emit=8), seg=16, name='braise')
    fl = [L.cyl((x + 0.08 * s * math.cos(k * 2.1), y + 0.08 * s * math.sin(k * 2.1), z + 0.75 * s), 0.07 * s, 0.0, 0.35 * s, M('feu', '#FF9A30', emit=10), name='feu') for k in range(5)]
    flames(fl)
    flicker_light((x, y, z + 1.0 * s), '#FF8A40', 180 * s, 0.25)
    sparks(loc=(x, y, z + 0.9 * s), n=10, rise=1.6 * s)


def sparks(loc, n=10, rise=1.5):
    x, y, z = loc; ps = []
    for k in range(n):
        ps.append((L.sphere((x, y, z), (0.012,) * 3, M('etincelle', '#FFB050', emit=20), seg=6, name='sp'), R.uniform(0, 1), R.uniform(-0.3, 0.3), R.uniform(-0.3, 0.3)))
    def up(t):
        for o, ph, vx, vy in ps:
            u = (t * 0.7 + ph) % 1.0; o.location = (x + vx * u + 0.05 * math.sin(t * 6 + ph * 9), y + vy * u, z + rise * u); o.scale = (0.012 * (1 - u) + 0.001,) * 3
    ANIM.append(up)


def smoke(loc, n=6, s=0.25, rise=2.5, col='#8A8490'):
    x, y, z = loc; ps = [(L.sphere((x, y, z), (s,) * 3, M('fumee' + col, col, rough=1.0), seg=16, name='fumee'), k / n) for k in range(n)]
    def up(t):
        for o, ph in ps:
            u = (t * 0.25 + ph) % 1.0; o.location = (x + 0.4 * u + 0.1 * math.sin(t + ph * 7), y + 0.2 * u, z + rise * u)
            k = s * (0.4 + 1.6 * u) * (1 - u) * 1.6; o.scale = (k, k, k)
    ANIM.append(up)


def breath(info, every=1.8):
    """Petits nuages de buée devant la bouche (froid de l'hiver)."""
    P = info['P']; ps = []
    for k in range(3):
        o = L.sphere(P(0, -0.8, -0.55), (0.01,) * 3, M('buee', '#E8F0FF', rough=1.0, emit=0.3), seg=12, name='buee'); o.parent = info['root']; ps.append((o, k / 3))
    s = info['s']
    def up(t):
        for o, ph in ps:
            u = ((t + info['ph']) / every + ph) % 1.0
            o.location = P(0.05 * math.sin(ph * 9), -0.85 - 0.6 * u, -0.5 + 0.35 * u); k = 0.07 * s * math.sin(math.pi * u) ** 0.7; o.scale = (k, k * 0.8, k)
    ANIM.append(up)


def note(loc, s=0.25):
    x, y, z = loc; m = M('note', '#FFE7A0', emit=5)
    hd = L.sphere((x, y, z), (0.12 * s, 0.05 * s, 0.09 * s), m, seg=12, name='note')
    st = L.cyl((x + 0.1 * s, y, z + 0.3 * s), 0.02 * s, 0.02 * s, 0.6 * s, m, name='note'); st.parent = hd; st.matrix_parent_inverse = hd.matrix_world.inverted()
    fl = L.curve([(x + 0.1 * s, y, z + 0.6 * s), (x + 0.25 * s, y, z + 0.45 * s), (x + 0.28 * s, y, z + 0.3 * s)], [1, 0.8, 0.5], m, bevel=0.025 * s, name='note')
    fl.parent = hd; fl.matrix_parent_inverse = hd.matrix_world.inverted()
    return hd


def notes_flow(src, n=10, spread=(3, 1), rise=3.0, drift=(0, -2), s=0.3, speed=0.22):
    x, y, z = src; ns = [(note((x, y, z), s), R.uniform(0, 1), R.uniform(-spread[0], spread[0]), R.uniform(-spread[1], spread[1])) for _ in range(n)]
    def up(t):
        for o, ph, ox, oy in ns:
            u = (t * speed + ph) % 1.0
            o.location = (x + ox + drift[0] * u + 0.3 * math.sin(t * 2 + ph * 9), y + oy + drift[1] * u, z + rise * u)
            k = math.sin(math.pi * u) ** 0.5; o.scale = (k, k, k); o.rotation_euler.y = 0.4 * math.sin(t * 3 + ph * 5)
    ANIM.append(up)


def snowfall(n, seed, bx, speed=0.5):
    rnd = random.Random(seed); m = M('flocon', '#FFFFFF', emit=0.8); fl = []
    for _ in range(n):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rnd.uniform(0.015, 0.04), location=(0, 0, 0))
        o = bpy.context.object; o.data.materials.append(m)
        fl.append((o, rnd.uniform(bx[0], bx[1]), rnd.uniform(bx[2], bx[3]), rnd.uniform(bx[4], bx[5]), rnd.uniform(0, 6)))
    def up(t):
        h = bx[5] - bx[4]
        for o, x, y, z0, ph in fl: o.location = (x + 0.15 * math.sin(t + ph), y, bx[4] + (z0 - bx[4] - t * speed) % h)
    ANIM.append(up)


def sandbags(x0, x1, y, z=0.0, rows=3, col=('#A89070', '#988060', '#B8A080'), rot=0.0):
    n = int((x1 - x0) / 0.5)
    for r in range(rows):
        for k in range(n + (r % 2)):
            xx = x0 + k * 0.5 + (0.25 if r % 2 else 0) + R.uniform(-0.03, 0.03)
            o = L.sphere((xx, y + R.uniform(-0.05, 0.05), z + 0.13 + r * 0.22), (0.27, 0.2, 0.13), M('sac' + str(k % 3), col[k % 3], rough=0.95), seg=16, name='sac')
            o.rotation_euler.z = R.uniform(-0.15, 0.15) + rot


def sandbags_y(y0, y1, x, z=0.0, rows=3):
    n = int((y1 - y0) / 0.5)
    for r in range(rows):
        for k in range(n):
            o = L.sphere((x + R.uniform(-0.03, 0.03), y0 + k * 0.5 + (0.25 if r % 2 else 0), z + 0.13 + r * 0.22), (0.2, 0.27, 0.13), M('sac' + str(k % 3), ('#A89070', '#988060', '#B8A080')[k % 3], rough=0.95), seg=16, name='sac')


def wire(x0, x1, y, z=0.0):
    m = M('fil_fer', '#3A3A40', rough=0.4, metal=0.6)
    for k in range(int((x1 - x0) / 1.5) + 1):
        L.cyl((x0 + k * 1.5, y, z + 0.4), 0.03, 0.03, 0.8, M('piquet', '#4A3A2A'), rot=(R.uniform(-0.15, 0.15), R.uniform(-0.15, 0.15), 0), name='piquet')
    pts = [(x0 + u * 0.12, y + 0.18 * math.sin(u * 0.9), z + 0.4 + 0.25 * math.cos(u * 0.9)) for u in range(int((x1 - x0) / 0.12))]
    L.curve(pts, [1] * len(pts), m, bevel=0.008, name='barbele')


def stump(loc, h=1.2):
    x, y, z = loc
    L.cyl((x, y, z + h / 2), 0.12, 0.07, h, M('souche', '#3A2E2A', rough=0.9), rot=(R.uniform(-0.2, 0.2), R.uniform(-0.2, 0.2), 0), name='souche')
    L.cyl((x + 0.15, y, z + h * 0.8), 0.04, 0.01, 0.5, M('souche', '#3A2E2A', rough=0.9), rot=(0, 0.9, 0), name='branche')


def crater(loc, r=1.0, col='#E8ECF8'):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.18 * r, location=loc); o = bpy.context.object; o.scale.z = 0.4
    bpy.ops.object.shade_smooth(); o.data.materials.append(M('cratere' + col, col, rough=0.8))
    L.sphere((loc[0], loc[1], loc[2] - 0.02), (r * 0.9, r * 0.9, 0.02), M('trou', '#4A4250', rough=0.9), seg=24, name='trou')


def lantern(loc, s=0.2):
    x, y, z = loc
    box((x, y, z), (s, s, 1.4 * s), M('lanterne', '#2A2422', metal=0.5, rough=0.4), bev=0.01)
    L.sphere((x, y, z), (0.6 * s, 0.6 * s, 0.9 * s), M('lumiere', '#FFC070', emit=10), seg=12, name='lum')
    flicker_light((x, y - 0.1, z), '#FFB060', 25, 0.1)


def ball(loc, r=0.13):
    o = L.sphere(loc, (r, r, r), M('cuir_ballon', '#8A5A2A', rough=0.45), seg=24, name='ballon')
    for k in range(3):
        bpy.ops.mesh.primitive_torus_add(major_radius=r * 1.0, minor_radius=r * 0.04, location=loc, rotation=(k * 1.05, k * 0.7, 0))
        b = bpy.context.object; b.data.materials.append(M('couture', '#4A2E14')); b.parent = o; b.matrix_parent_inverse = o.matrix_world.inverted()
    return o


def mini_soldier(loc, side, s=0.3):
    x, y, z = loc
    L.cyl((x, y, z + 0.5 * s), 0.3 * s, 0.18 * s, 1.0 * s, M('unif' + side, UNIF[side], rough=0.75), name='mini')
    L.sphere((x, y, z + 1.25 * s), (0.25 * s, 0.22 * s, 0.32 * s), M('skin', '#6EC3D6', rough=0.45, sss=0.15), seg=16, name='mini')
    L.sphere((x, y, z + 1.45 * s), (0.27 * s, 0.25 * s, 0.14 * s), M('casq_en', '#7A6A3E') if side == 'en' else M('cuir', '#23232A', rough=0.28), seg=16, name='mini')


# ---------------- les plans ----------------
def s_poignee():                          # accroche : la poignée de main au milieu du no man's land
    L.world('#5A6AB0', '#FFC8A0', 1.0); L.lights(key='#FFE0C0', rim='#9AB0FF', fill='#FFC8E0', k=1.1)
    ground('#EEF0FA', bump=0.35)
    sandbags(-12, 12, 12, rows=3); sandbags(-12, 12, -9, rows=2)
    for k in range(7): xmas_tree((-9 + k * 3 + R.uniform(-0.4, 0.4), 11.4, 0.6), 1.0, light=k % 2 == 0, candles=7)
    wire(-12, -3, 8.5); wire(3, 12, 8.5)
    for k in range(5): stump((R.choice([-1, 1]) * R.uniform(4, 9), R.uniform(3, 10), 0), R.uniform(0.8, 1.6))
    crater((-3.5, 6, 0.05), 0.9); crater((4, 4, 0.05), 0.7)
    L.sphere((6, 40, 6), (4, 4, 4), M('soleil', '#FFD8A0', emit=4), name='soleil')
    en = soldier(-0.62, 0, 0.55, 'en', rot=0.95, hero=True, poses=[(0, 'down'), (0.6, 'give')], scarf='#B83A3A')
    de = soldier(0.62, 0, 0.55, 'de', rot=-0.95, hero=True, poses=[(0, 'down'), (0.6, 'take')], mous='#3A2A20', scarf='#3A5AA8')
    for i in (en, de): breath(i)
    for k in range(14):                    # foule mélangée qui discute derrière
        side = 'en' if k % 2 else 'de'; x = -6 + k * 0.9 + R.uniform(-0.2, 0.2); y = R.uniform(3, 7)
        soldier(x, y, 0.45, side, rot=R.uniform(-0.6, 0.6), pose=R.choice(['laugh', 'down', 'wave', 'give', 'point']), bob=0.04, mous='#3A2A20' if side == 'de' and k % 3 == 0 else None)
    b = ball((3.5, -0.5, 0.13))
    b.keyframe_insert('location', frame=1); b.location = (0.35, -0.6, 0.13); b.keyframe_insert('location', frame=F(DUR * 0.8))
    b.rotation_euler = (0, 0, 0); b.keyframe_insert('rotation_euler', frame=1); b.rotation_euler = (0, -12, 0); b.keyframe_insert('rotation_euler', frame=F(DUR * 0.8))
    snowfall(260, 2, (-5, 5, -4, 6, -0.2, 5), 0.45)
    c = mkcam(38); cam_path(c, (0.4, -7.5, 2.1), (0.1, -5.6, 1.7), (0, 2, 1.4), (0, 1, 1.35))


def s_tranchee():                         # la tranchée anglaise, la boue, le froid
    L.world('#2A3A7A', '#E89A70', 1.0); L.lights(key='#FFC8A0', rim='#8A9AFF', fill='#6A8AC8', k=0.9)
    ground('#4A3A30', bump=0.15, z=-0.02)
    for sx in (-1, 1):                     # parois en planches + sacs de sable
        for k in range(30):
            box((1.6 * sx, -4 + k * 0.42, 1.0), (0.08, 0.4, 2.0), M('planche' + str(k % 3), ('#6A4A30', '#5A3E28', '#7A5838')[k % 3], rough=0.85), bev=0.01)
        sandbags_y(-4, 9, 1.75 * sx, z=2.0, rows=2)
    for k in range(28): box((0, -4 + k * 0.45, 0.05), (2.6, 0.32, 0.06), M('caillebotis', '#7A5A3A', rough=0.8), bev=0.01)
    for k in range(4): L.sphere((R.uniform(-0.8, 0.8), R.uniform(0, 10), 0.09), (0.4, 0.3, 0.01), M('flaque', '#3A3A50', rough=0.05), seg=24, name='flaque')
    brazier((-0.7, 2.2, 0.1), 1.0)
    for k in range(5): lantern((1.4 * (1 if k % 2 else -1), 0.5 + k * 2, 1.9), 0.13)
    for k in range(6): L.cyl((1.45 * (1 if k % 2 else -1), 3 + k * 1.1, 0.9), 0.025, 0.025, 1.7, M('fusil', '#5A3A22', rough=0.5), rot=(0.25, 0, 0), name='fusil')
    hero = soldier(0.35, 1.4, 0.5, 'en', rot=0.5, hero=True, pose='warm', scarf='#B83A3A'); breath(hero)
    soldier(-1.05, 2.9, 0.47, 'en', rot=-0.6, pose='warm'); soldier(-0.2, 3.3, 0.47, 'en', rot=0.1, pose='warm')
    for k in range(6):
        sx = 1 if k % 2 else -1
        i = soldier(1.05 * sx, 4.5 + k * 1.3, 0.45, 'en', rot=-0.5 * sx, z=-0.4 if k % 3 == 0 else 0.0, eyes='closed' if k % 3 == 0 else 'open',
                    pose=R.choice(['down', 'laugh', 'sing', 'point']))
        breath(i)
    snowfall(220, 3, (-2, 2, -1, 10, 0, 4.5), 0.4)
    L.stars(60, 4)
    c = mkcam(30); cam_path(c, (0.2, -3.0, 1.9), (0.0, -1.6, 1.7), (-0.2, 3, 1.3), (-0.2, 3.5, 1.2))


def s_nuit():                             # les sapins illuminés en face, « Douce nuit »
    L.world('#0A1240', '#3A3A7A', 1.0); L.lights(key='#8A9AE0', rim='#FFB070', fill='#3A4A9A', k=0.6)
    ground('#DDE4F8', bump=0.4)
    L.stars(220, 7); L.big_moon((-7, 45, 16), 3.5, '#FFF0D0')
    sandbags(-16, 16, 15, rows=3, col=('#8A8070', '#7A7060', '#9A9080'))
    for k in range(11): xmas_tree((-13 + k * 2.6 + R.uniform(-0.3, 0.3), 14.5, 0.65), 1.0, light=k % 2 == 0, candles=8)
    for k in range(12):                    # têtes allemandes au-dessus du parapet
        soldier(-12 + k * 2.2 + R.uniform(-0.3, 0.3), 15.4, 0.4, 'de', z=-0.3, pose='sing', sing=True, bob=0.03, mous='#3A2A20' if k % 2 else None)
    wire(-14, 14, 10); wire(-14, 14, 4.5)
    for k in range(7): stump((R.uniform(-10, 10), R.uniform(5, 13), 0), R.uniform(0.8, 1.8))
    for k in range(4): crater((R.uniform(-8, 8), R.uniform(3, 12), 0.05), R.uniform(0.6, 1.2))
    sandbags(-4, 4, -0.6, rows=4)          # notre parapet au premier plan
    a1 = soldier(-0.9, -1.4, 0.5, 'en', z=-0.35, hero=True, look=(0, 0.3), pose='down', scarf='#B83A3A'); breath(a1)
    a2 = soldier(1.0, -1.5, 0.5, 'en', z=-0.4, look=(0, 0.3), pose='point'); breath(a2)
    notes_flow((0, 14, 2.0), n=18, spread=(9, 0.5), rise=3.5, drift=(0, -5), s=0.3, speed=0.16)
    snowfall(240, 5, (-6, 6, -1, 14, -0.2, 6), 0.35)
    c = mkcam(32); cam_path(c, (0, -5.2, 1.5), (0, -4.6, 2.0), (0, 8, 1.4), (0, 8, 1.6))


def s_chant():                            # les Anglais chantent à leur tour
    L.world('#0E1650', '#4A3A80', 1.0); L.lights(key='#FFB880', rim='#8A9AFF', fill='#3A4A9A', k=0.8)
    ground('#4A3A30', bump=0.15, z=-0.02)
    for k in range(30): box((-4 + k * 0.42, 1.7, 1.0), (0.4, 0.08, 2.0), M('planche' + str(k % 3), ('#6A4A30', '#5A3E28', '#7A5838')[k % 3], rough=0.85), bev=0.01)
    sandbags(-4.5, 8, 1.9, z=2.0, rows=2)
    L.stars(150, 9); L.big_moon((5, 30, 10), 2, '#FFF0D0')
    for k in range(4): lantern((-3 + k * 2.2, 1.45, 1.6), 0.13)
    brazier((2.6, 0.6, 0.1), 0.9)
    for k in range(6):
        i = soldier(-2.6 + k * 1.0, 0.4 + 0.25 * (k % 2), 0.48, 'en', rot=R.uniform(-0.25, 0.25), pose='sing', sing=True, hero=k == 2,
                    path=(lambda ph: (lambda t: (0.06 * math.sin(t * 2.0 + ph), 0, 0)))(k * 0.7), scarf=SCARVES[k % 5])
        breath(i)
    notes_flow((-0.5, 0.8, 2.2), n=12, spread=(3, 0.3), rise=2.5, drift=(0, 3), s=0.22, speed=0.2)
    snowfall(200, 6, (-4, 4, -2, 2, 0, 5), 0.35)
    c = mkcam(32); cam_path(c, (-1.2, -4.6, 1.6), (0.6, -4.2, 1.7), (-0.4, 0.6, 1.4), (0.2, 0.6, 1.4))


def s_sortie():                           # au matin, un Allemand sort les mains vides, puis des centaines
    L.world('#6A80C8', '#FFB890', 1.1); L.lights(key='#FFD0A0', rim='#FFA0C0', fill='#A0B8FF', k=1.1)
    ground('#EEF0FA', bump=0.35)
    L.sphere((-4, 45, 2), (5, 5, 5), M('soleil', '#FFD0A0', emit=4), name='soleil')
    sandbags(-16, 16, 12, rows=3, col=('#8A8070', '#7A7060', '#9A9080'))
    for k in range(6): xmas_tree((-12 + k * 4.6, 11.4, 0.6), 0.9, light=False, candles=6)
    wire(-14, -1.5, 8); wire(1.5, 14, 8)
    for k in range(6): stump((R.choice([-1, 1]) * R.uniform(3, 10), R.uniform(4, 11), 0), R.uniform(0.8, 1.6))
    first = soldier(0, 12.3, 0.5, 'de', hero=True, poses=[(0, 'up')], mous='#3A2A20',
                    path=lambda t: (0, -min(6.5, max(0, t - 0.6) * 2.2), -1.6 * (1 - ease(t / 0.6))))
    breath(first)
    for k in range(22):                    # puis tous les autres sortent
        x = R.choice([-1, 1]) * R.uniform(1.2, 13); t0 = DUR * 0.35 + R.uniform(0, DUR * 0.4)
        sp = R.uniform(1.0, 1.8)
        soldier(x, 12.4, 0.45, 'de', rot=R.uniform(-0.3, 0.3), poses=[(0, 'up'), (t0 + 1.2, R.choice(['wave', 'up', 'cheer']))],
                path=(lambda t0, sp: (lambda t: (0, -max(0, t - t0 - 0.5) * sp, -1.6 * (1 - ease((t - t0) / 0.5)))))(t0, sp))
    sandbags(-5, 5, -0.8, rows=2)
    for k, x in enumerate((-1.6, 1.7)):
        soldier(x, -1.6, 0.5, 'en', z=-0.3, look=(0, 0.4), poses=[(0, 'down'), (DUR * 0.6 + k * 0.3, 'wave')])
    snowfall(160, 8, (-6, 6, -1, 12, -0.2, 5), 0.3)
    c = mkcam(35); cam_path(c, (0, -5.5, 2.3), (0, -4.4, 2.2), (0, 8, 1.0), (0, 6, 0.9))


def s_echanges():                         # chocolat, cigarettes, boutons… et les morts enterrés ensemble
    L.world('#6A8AD0', '#FFE0C0', 1.1); L.lights(key='#FFE0C0', rim='#B0C0FF', fill='#FFD0E0', k=1.1)
    ground('#EEF0FA', bump=0.3)
    sandbags(-16, 16, 14, rows=3); xmas_tree((0, 3.2, 0), 1.5, candles=12)
    items = [('chocolat', lambda loc: box(loc, (0.22, 0.05, 0.12), M('choco', '#5A3020', rough=0.4), bev=0.01)),
             ('cigarettes', lambda loc: box(loc, (0.16, 0.06, 0.1), M('paquet', '#E8D8B0', rough=0.5), bev=0.01)),
             ('bouton', lambda loc: L.sphere(loc, (0.05, 0.02, 0.05), M('bouton', '#E8C050', metal=0.85, rough=0.25), seg=12, name='btn'))]
    pairs = [(-1.9, 0.4), (0.0, -0.4), (1.9, 0.4)]
    for k, (x, y) in enumerate(pairs):
        tsw = DUR * (0.25 + 0.2 * k)
        g = soldier(x - 0.5, y, 0.5, 'en', rot=0.9, hero=k == 1, poses=[(0, 'down'), (tsw - 1.0, 'give'), (tsw + 0.8, 'laugh')])
        r_ = soldier(x + 0.5, y, 0.5, 'de', rot=-0.9, poses=[(0, 'down'), (tsw - 0.7, 'take'), (tsw + 0.8, 'laugh')], mous='#3A2A20' if k != 1 else None)
        breath(g); breath(r_)
        it = items[k][1]((x, y, 1.0))
        def follow(t, it=it, g=g, r_=r_, tsw=tsw):
            if t < tsw - 1.0: it.location = (0, 0, -50); return
            hw = hand_world(g, 1) if t < tsw else hand_world(r_, -1)
            it.location = (hw[0], hw[1] - 0.06, hw[2] + 0.06)
        ANIM.append(follow)
    for k in range(10):                    # groupes qui rient autour
        side = 'en' if k % 2 else 'de'
        soldier(R.choice([-1, 1]) * R.uniform(2.8, 5.5), R.uniform(1.5, 5), 0.45, side, rot=R.uniform(-0.8, 0.8), pose=R.choice(['laugh', 'laugh', 'point', 'down']), bob=0.05)
    for k in range(5):                     # au fond : les croix, on enterre les morts ensemble
        x = -3 + k * 1.5
        L.cyl((x, 10, 0.55), 0.05, 0.05, 1.1, M('croix', '#6A4A30'), name='croix'); L.cyl((x, 10, 0.8), 0.04, 0.04, 0.6, M('croix', '#6A4A30'), rot=(0, math.pi / 2, 0), name='croix')
    for k in range(6): soldier(-3.8 + k * 1.5, 11.0, 0.42, 'en' if k % 2 else 'de', eyes='lidded', hat=k % 3 != 0, pose='down', bob=0.0)
    snowfall(200, 9, (-5, 5, -3, 8, -0.2, 5), 0.3)
    c = mkcam(34); cam_path(c, (-1.4, -6.0, 2.0), (1.0, -5.4, 1.9), (0, 1.5, 1.2), (0.2, 1.5, 1.2))


def s_foot():                             # le match dans la neige
    L.world('#2A50B0', '#FFC8A0', 0.9); L.lights(key='#FFD8B0', rim='#B0C0FF', fill='#8AA0E0', k=0.9)
    ground('#DDE2F4', bump=0.25)
    def bpath(t): return (2.6 * math.sin(t * 0.9), 1.0 + 0.8 * math.sin(t * 1.7), 0.13 + 0.5 * abs(math.sin(t * 3.0)))
    b = ball((0, 1, 0.13))
    def mv(t): b.location = bpath(t); b.rotation_euler = (t * 7, t * 3, 0)
    ANIM.append(mv)
    for k in range(8):                     # joueurs qui courent après le ballon
        side = 'en' if k % 2 else 'de'; off = (R.uniform(-1.6, 1.6), R.uniform(-0.8, 1.4)); lag = R.uniform(0.3, 0.9)
        soldier(0, 0, 0.45, side, pose='run', bob=0.08, hero=k == 1,
                path=(lambda off, lag: (lambda t: (bpath(t - lag)[0] * 0.8 + off[0], bpath(t - lag)[1] + off[1], 0)))(off, lag))
    for k in range(18):                    # spectateurs en arc de cercle
        a = math.pi * (0.1 + 0.8 * k / 17); r = 6.0
        soldier(r * math.cos(a), 2.0 + r * math.sin(a), 0.45, 'en' if k % 2 else 'de', rot=-(a - math.pi / 2) * 0.6, pose=R.choice(['cheer', 'cheer', 'wave', 'laugh']), bob=0.06)
    for x in (-4.2, -3.2, 3.2, 4.2):       # buts en casquettes
        L.sphere((x, 1.2, 0.08), (0.2, 0.2, 0.08), M('casq_en', '#7A6A3E', rough=0.8), seg=16, name='but')
    sandbags(-16, 16, 12, rows=3); [xmas_tree((-10 + k * 5, 11.4, 0.6), 0.9, light=False, candles=6) for k in range(5)]
    snowfall(200, 10, (-6, 6, -3, 9, -0.2, 5), 0.3)
    c = mkcam(30)
    def follow(t):
        bx_, by_, _ = bpath(t); c.location = (bx_ * 0.6, -5.5, 2.4); d = Vector((bx_ * 0.8, by_ + 0.8, 0.9)) - c.location
        c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    ANIM.append(follow); follow(0)


def s_front():                            # vue du ciel : tout le front s'arrête
    L.world('#2A3A80', '#FF9A70', 1.1); L.lights(key='#FFC8A0', rim='#A0B0FF', fill='#FFA0C0', k=1.3)
    ground('#DDE4F8', size=200, bump=0.6)
    for side, y0 in (('de', 9), ('en', -9)):
        pts = [(x, y0 + 1.6 * ((x // 3) % 2), 0.05) for x in range(-60, 61, 3)]
        L.curve(pts, [1] * len(pts), M('tranchee', '#4A3A30', rough=0.9), bevel=0.45, name='tranchee')
    for k in range(26): xmas_tree((R.uniform(-40, 40), R.choice([7.5, -7.5]) + R.uniform(-1, 1), 0), 1.4, light=k % 3 == 0, candles=6)
    for k in range(22):                    # petits feux et attroupements dans le no man's land
        x, y = R.uniform(-25, 25), R.uniform(-4, 6)
        L.sphere((x, y, 0.1), (0.25, 0.25, 0.1), M('braise', '#FF5A20', emit=10), seg=12, name='feu')
        smoke((x, y, 0.5), n=4, s=0.4, rise=4.0)
        for j in range(R.randint(4, 8)):
            a_ = R.uniform(0, 6.3); rr = R.uniform(0.7, 1.4); mini_soldier((x + rr * math.cos(a_), y + rr * math.sin(a_), 0), R.choice(['en', 'de']), 0.5)
    for k in range(160): mini_soldier((R.uniform(-30, 30), R.uniform(-6, 8), 0), R.choice(['en', 'de']), 0.5)
    L.sphere((10, 120, 6), (14, 14, 14), M('soleil', '#FFC890', emit=4), name='soleil')
    c = mkcam(30); cam_path(c, (-5, -9, 3.5), (2, -14, 9), (0, 2, 0), (0, 6, 0))


def s_ordre():                            # l'année suivante, les généraux l'interdisent
    L.world('#141018', '#2A2028', 0.6); L.lights(key='#FFC880', rim='#6A7AC8', fill='#3A2A3A', k=0.7)
    box((0, 4, 2.5), (14, 0.2, 6), M('mur_bureau', '#4A2E2E', rough=0.8), bev=0)
    ground('#3A2420', bump=0.0)
    box((0, 3.85, 2.6), (3.4, 0.05, 2.2), M('carte', '#D8C8A0', rough=0.7), bev=0)                       # carte du front
    L.curve([(-1.5, 3.8, 2.0 + 0.4 * math.sin(k)) for k in range(1)] + [(-1.5 + k * 0.3, 3.8, 2.4 + 0.35 * math.sin(k * 1.3)) for k in range(11)], [1] * 12, M('front_rouge', '#C02020'), bevel=0.025, name='front')
    for k in range(9): L.sphere((-1.4 + k * 0.35, 3.78, 2.0 + R.uniform(0, 1.3)), (0.04,) * 3, M('punaise' + str(k % 2), ('#2040C0', '#E0B020')[k % 2], emit=1), seg=8, name='p')
    box((2.8, 3.85, 2.8), (1.2, 0.05, 1.8), M('fenetre', '#3A5A9A', emit=0.8), bev=0)
    box((0, 0.6, 0.85), (3.2, 1.6, 0.12), M('bureau', '#5A3420', rough=0.35), bev=0.03)
    for x in (-1.4, 1.4): box((x, 0.6, 0.4), (0.3, 1.4, 0.8), M('bureau', '#5A3420', rough=0.35), bev=0.03)
    L.cyl((1.1, 0.9, 1.15), 0.05, 0.05, 0.5, M('laiton', '#E0B850', metal=0.85, rough=0.25), name='lampe')
    L.sphere((1.1, 0.9, 1.45), (0.3, 0.2, 0.12), M('abatjour', '#2A8A5A', emit=2), seg=16, name='abat')
    flicker_light((1.1, 0.7, 1.3), '#FFD090', 90, 0.2)
    paper = box((-0.2, 0.3, 0.93), (0.6, 0.8, 0.01), M('papier', '#F4ECD8', rough=0.8), bev=0)
    gen = soldier(-0.1, 1.7, 0.55, 'en', old=True, hero=True, mous='#E8E4EC', scarf='#B02020', poses=[(0, 'down'), (DUR * 0.25, 'give')], look=(0, -0.4))
    stamp = L.cyl((-0.2, 0.3, 1.3), 0.1, 0.12, 0.2, M('tampon', '#2A1A1A', rough=0.4), name='tampon')
    L.cyl((-0.2, 0.3, 1.85), 0.04, 0.05, 0.3, M('manche', '#6A3A20'), name='tampon').parent = stamp
    ts = DUR * 0.55
    for t, z in ((0, 1.3), (ts - 0.35, 1.38), (ts, 1.05), (ts + 0.15, 1.05), (ts + 0.5, 1.3)):
        stamp.location.z = z; stamp.keyframe_insert('location', frame=F(t))
    word = None
    bpy.ops.object.text_add(location=(-0.2, 0.25, 0.945), rotation=(0, 0, 0)); word = bpy.context.object
    word.data.body = 'INTERDIT'; word.data.size = 0.14; word.data.align_x = 'CENTER'; word.data.align_y = 'CENTER'; word.data.extrude = 0.002
    word.data.materials.append(M('encre', '#C01818', emit=0.6))
    word.scale = (0.001,) * 3; word.keyframe_insert('scale', frame=F(ts)); word.scale = (1, 1, 1); word.keyframe_insert('scale', frame=F(ts) + 2)
    smoke((-1.5, 0.8, 1.3), n=5, s=0.12, rise=1.8, col='#9A949A')         # cigare
    c = mkcam(35); cam_path(c, (0.9, -3.4, 2.9), (0.7, -2.7, 2.7), (-0.1, 1.0, 1.6), (-0.15, 0.9, 1.5))


def s_fin():                              # « pendant un jour, on était juste des hommes »
    L.world('#2A2A70', '#FF9A6A', 1.1); L.lights(key='#FFB880', rim='#B0A0FF', fill='#FF90B0', k=1.1)
    ground('#E8E4F4', bump=0.35)
    L.sphere((3, 40, 1.5), (5, 5, 5), M('soleil', '#FFB070', emit=4), name='soleil')
    L.stars(80, 11)
    en = soldier(-0.42, 0.2, 0.42, 'en', rot=0.35, hero=True, poses=[(0, 'down'), (DUR * 0.2, 'give'), (DUR * 0.55, 'laugh')], scarf='#B83A3A')
    de = soldier(0.42, 0.2, 0.42, 'de', rot=-0.35, poses=[(0, 'down'), (DUR * 0.25, 'take'), (DUR * 0.55, 'laugh')], mous='#3A2A20', scarf='#3A5AA8')
    breath(en); breath(de)
    xmas_tree((1.9, 1.4, 0), 1.3, candles=12)
    for k in range(9): xmas_tree((-12 + k * 3, 12.5, 0.4), 0.9, light=False, candles=6)
    sandbags(-16, 16, 13, rows=3)
    for k in range(16):                    # silhouettes qui rentrent dans leurs tranchées
        side = 'en' if k % 2 else 'de'; x0 = R.uniform(-9, 9); y0 = R.uniform(5, 10)
        soldier(x0, y0, 0.4, side, pose=R.choice(['down', 'wave']), bob=0.04,
                path=(lambda d: (lambda t: (0, d * t * 0.35, 0)))(1 if side == 'de' else -1))
    snowfall(260, 12, (-5, 5, -3, 8, -0.2, 5), 0.25)
    c = mkcam(40); cam_path(c, (0.1, -4.2, 1.6), (0.3, -6.8, 2.4), (0, 0.6, 1.3), (0.2, 2, 1.3))


globals()['s_' + SHOT]()


def polish():
    ee = sc.eevee
    ee.use_motion_blur = True; ee.motion_blur_shutter = 0.45; ee.motion_blur_steps = 1
    ee.gtao_distance = 0.8; ee.bloom_intensity = 0.1
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'; sc.view_settings.exposure = -0.5
    for m in bpy.data.materials:
        if not m.use_nodes or 'Principled BSDF' not in m.node_tree.nodes: continue
        b = m.node_tree.nodes['Principled BSDF']
        if b.inputs['Emission Strength'].default_value > 0:
            if m.name.startswith('soleil'): b.inputs['Emission Strength'].default_value *= 2.5
            continue
        b.inputs['Roughness'].default_value = max(0.22, b.inputs['Roughness'].default_value * 0.75)
        b.inputs['Sheen Weight'].default_value = 0.12; b.inputs['Sheen Roughness'].default_value = 0.4
        if m.name.startswith('skin'):
            b.inputs['Subsurface Weight'].default_value = 0.3; b.inputs['Subsurface Radius'].default_value = (0.4, 0.25, 0.18)
            b.inputs['Coat Weight'].default_value = 0.12; b.inputs['Coat Roughness'].default_value = 0.25
    heroes = [i for i in SOLDIERS if any(o.type == 'LIGHT' for o in i['root'].children)]
    cam = sc.camera
    if heroes and cam and SHOT not in ('front',):
        cam.data.dof.use_dof = True; cam.data.dof.focus_object = heroes[0]['root']; cam.data.dof.aperture_fstop = 2.4
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and 'rim' in o.name.lower(): o.data.energy *= 1.35


polish()
L.on_frame(lambda t: (L.blink(t), [f(t) for f in ANIM]))
if PREV is not None:
    sc.frame_set(int(F(PREV))); sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = OUT + '/f_'; sc.render.image_settings.file_format = 'PNG'
    sc.render.use_overwrite = False; sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True)

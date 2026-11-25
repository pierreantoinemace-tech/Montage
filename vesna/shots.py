"""Plans 3D de l'histoire de Vesna (Blender/EEVEE). Usage :
blender -b --python shots.py -- <plan> <durée_s> <dossier_sortie> <rx> <ry> [t_aperçu]"""
import sys, math, random
sys.path.insert(0, '/home/user/Montage/test3d')
import bpy, lib3d as L
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:]
SHOT, DUR, OUT, RX, RY = a[0], float(a[1]), a[2], int(a[3]), int(a[4])
PREV = float(a[5]) if len(a) > 5 else None
FPS = 12
N = max(2, int(round(DUR * FPS)))
sc = L.setup(RX, RY, samples=12, fps=FPS)
sc.frame_start, sc.frame_end = 1, N
VESNA = dict(robe='#5A3AA8', hat='toque', hair_cols=('#3A2470', '#C080E0'), nhair=24)
ANIM = []                                   # fonctions t -> mises à jour par image


def F(t): return 1 + t * FPS                # seconde -> image
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def cam_path(c, p0, p1, look0, look1, t0=0, t1=None):
    t1 = DUR if t1 is None else t1
    for t, p, lk in ((t0, p0, look0), (t1, p1, look1)):
        c.location = p; d = Vector(lk) - Vector(p); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        c.keyframe_insert('location', frame=F(t)); c.keyframe_insert('rotation_euler', frame=F(t))


def plane3d(loc=(0, 0, 0), s=1.0, rot=(0, 0, 0)):
    """Avion des années 70, tout rond."""
    before = set(bpy.data.objects)
    X, Y, Z = loc
    body = L.mat('fuselage', '#F2ECE4', rough=0.35); stripe = L.mat('stripe', '#5A3AA8', rough=0.4); win = L.mat('win', '#2A3A5A', rough=0.1)
    L.cyl((X, Y, Z), 0.55 * s, 0.55 * s, 5 * s, body, rot=(0, math.pi / 2, 0), name='fus')
    L.sphere((X + 2.5 * s, Y, Z), (0.9 * s, 0.55 * s, 0.55 * s), body, name='nez')
    L.sphere((X - 2.5 * s, Y, Z + 0.05 * s), (0.9 * s, 0.45 * s, 0.45 * s), body, name='queue')
    L.cyl((X, Y - 0.001, Z - 0.05 * s), 0.565 * s, 0.565 * s, 4.6 * s, stripe, rot=(0, math.pi / 2, 0), name='band').scale = (0.4, 1, 1)
    for k in range(9): L.sphere((X - 1.8 * s + k * 0.45 * s, Y - 0.53 * s, Z + 0.18 * s), (0.11 * s, 0.03 * s, 0.13 * s), win, seg=16, name='hublot')
    L.sphere((X + 2.95 * s, Y - 0.28 * s, Z + 0.2 * s), (0.22 * s, 0.12 * s, 0.1 * s), win, seg=16, name='cockpit')
    for sy in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(X - 0.2 * s, Y + sy * 1.6 * s, Z - 0.25 * s)); w = bpy.context.object
        w.scale = (1.3 * s, 2.6 * s, 0.1 * s); w.rotation_euler = (0, 0, sy * -0.35); w.data.materials.append(body)
        bv = w.modifiers.new('b', 'BEVEL'); bv.width = 0.04; bv.segments = 4
        L.cyl((X - 2.7 * s, Y + sy * 0.75 * s, Z + 0.15 * s), 0.25 * s, 0.25 * s, 0.9 * s, stripe, rot=(0, math.pi / 2, 0), name='moteur')
    bpy.ops.mesh.primitive_cube_add(size=1, location=(X - 2.9 * s, Y, Z + 0.9 * s)); d = bpy.context.object
    d.scale = (0.9 * s, 0.08 * s, 1.2 * s); d.rotation_euler = (0, -0.35, 0); d.data.materials.append(stripe)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(X - 3.15 * s, Y, Z + 1.5 * s)); h = bpy.context.object
    h.scale = (0.6 * s, 1.8 * s, 0.07 * s); h.data.materials.append(body)
    root = bpy.data.objects.new('avion', None); bpy.context.collection.objects.link(root)
    for o in set(bpy.data.objects) - before - {root}:
        if o.parent is None: o.parent = root
    root.rotation_euler = rot
    return root


def clouds_field(n, seed, zrange, xr=8, yr=(4, 16), col='#FFE6EE', s=(0.8, 1.6), clear=0.0):
    rnd = random.Random(seed); objs = []
    for i in range(n):
        before = set(bpy.data.objects)
        x = rnd.uniform(-xr, xr)
        if clear and abs(x) < clear: x = math.copysign(clear + abs(x), x if x else 1)
        L.cloud((x, rnd.uniform(*yr), rnd.uniform(*zrange)), rnd.uniform(*s), col, seed=seed * 100 + i)
        objs += list(set(bpy.data.objects) - before)
    return objs


def pine(loc, h=2.0):
    x, y, z = loc
    L.cyl((x, y, z + 0.2 * h), 0.08 * h, 0.08 * h, 0.4 * h, L.mat('tronc', '#5A3A3A', rough=0.9), name='tronc')
    for k in range(3):
        r = 0.55 * h * (1 - k * 0.27); zz = z + 0.35 * h + k * 0.28 * h
        L.cyl((x, y, zz + 0.25 * h), r, 0.02, 0.6 * h, L.mat('sapin', '#2E5A5A', rough=0.8), name='sapin')
        L.cyl((x, y, zz + 0.25 * h + 0.18 * h), r * 0.45, 0.01, 0.25 * h, L.mat('neige', '#F4F6FF', rough=0.6), name='neigesapin')


def snowfall(n, seed, box, speed=0.6):
    rnd = random.Random(seed); m = L.mat('flocon', '#FFFFFF', emit=0.6); fl = []
    for _ in range(n):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rnd.uniform(0.02, 0.05), location=(0, 0, 0))
        o = bpy.context.object; o.data.materials.append(m)
        fl.append((o, rnd.uniform(box[0], box[1]), rnd.uniform(box[2], box[3]), rnd.uniform(box[4], box[5]), rnd.uniform(0, 6)))
    def up(t):
        for o, x, y, z0, ph in fl:
            h = box[5] - box[4]
            o.location = (x + 0.15 * math.sin(t + ph), y, box[4] + (z0 - box[4] - t * speed) % h)
    ANIM.append(up)


def text3d(body, loc, size, col, rot=(math.pi / 2, 0, 0), emit=0.0):
    bpy.ops.object.text_add(location=loc, rotation=rot); o = bpy.context.object
    o.data.body = body; o.data.size = size; o.data.extrude = 0.05 * size; o.data.align_x = 'CENTER'; o.data.align_y = 'CENTER'
    o.data.bevel_depth = 0.01 * size; o.data.materials.append(L.mat('txt' + col, col, rough=0.3, emit=emit)); return o


# ---------------- les plans ----------------
def s_chute():                       # le hook : elle flotte au milieu des nuages
    L.world('#7A9AE0', '#FFC8D8', 1.1); L.lights(key='#FFE0D0', rim='#B8A8FF', k=1.0)
    v = L.character((0, 0, 0), 1.0, 0, 'closed', **VESNA)
    v.rotation_euler = (0.25, 0, 0)
    v.keyframe_insert('rotation_euler', frame=1); v.rotation_euler = (0.25, 0.18, 0.5); v.keyframe_insert('rotation_euler', frame=F(DUR))
    objs = clouds_field(22, 1, (-30, 8), xr=7, yr=(1, 12), col='#FFF0F4', s=(0.7, 1.5), clear=2.8)
    for o in objs:                                   # les nuages montent : on tombe
        z = o.location.z; o.keyframe_insert('location', frame=1); o.location.z = z + DUR * 4.0; o.keyframe_insert('location', frame=F(DUR))
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 40
    cam_path(c, (0, -7.5, 1.4), (0, -6.0, 0.8), (0, 0, 0.6), (0, 0, 0.5))
    # à la fin elle ouvre les yeux
    ANIM.append(lambda t: [setattr(o, 'scale', (o.scale[0], o.scale[1], (0.2 * (0.28 if t > DUR - 1.6 else 1.0) * s_ + 0.005))) for o, lid, ez, P, s_, ex, ey in L.LIDS])


def s_hotesse():
    L.world('#F0A8A0', '#FFE0B8', 1.0); L.lights(key='#FFD8B0', rim='#FF9AC8', k=1.0)
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -2.95)); g = bpy.context.object; g.data.materials.append(L.mat('tarmac', '#6A5A7A', rough=0.9))
    for k in range(6):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(-6 + k * 2.5, 2, -2.94)); m = bpy.context.object; m.scale = (0.9, 0.12, 1); m.data.materials.append(L.mat('marquage', '#F4E6C0'))
    plane3d((0.8, 7, -0.6), 1.6, rot=(0, 0, 0.12))
    L.sphere((5, 30, 3), (5, 5, 5), L.mat('soleil', '#FFD8A0', emit=3), name='soleil')
    v = L.character((1.6, 0, -0.55), 0.75, 0, 'open', look=(-0.3, 0.2), **VESNA)
    v.rotation_euler = (0, 0, 0.15)
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 35
    cam_path(c, (1.8, -9.5, 0.6), (1.6, -8.2, 0.3), (1.0, 3, 0.0), (1.4, 2, -0.2))


def s_confusion():
    L.world('#5A4A9A', '#C8A0D8', 1.0); L.lights(k=1.0)
    cards = []
    for k, (x, col) in enumerate(((-1.3, '#F4EEE4'), (1.3, '#E8E0F8'))):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0)); cd = bpy.context.object
        cd.scale = (1.9, 0.08, 1.15); cd.data.materials.append(L.mat('card' + col, col, rough=0.4))
        bv = cd.modifiers.new('b', 'BEVEL'); bv.width = 0.08; bv.segments = 5
        t = text3d('VESNA', (x, -0.12, 0.2), 0.45, '#3A2A70'); t.parent = cd; t.matrix_parent_inverse = cd.matrix_world.inverted()
        ph = L.sphere((x - 0.55, -0.1, -0.25), (0.22, 0.05, 0.22), L.mat('photo' + col, '#6EC3D6' if k == 0 else '#E8A0B8'), name='photo'); ph.parent = cd; ph.matrix_parent_inverse = cd.matrix_world.inverted()
        cards.append(cd)
    a, b = cards                                     # les deux badges échangent leur place
    for o, x0, x1, z in ((a, -1.3, 1.3, 0.6), (b, 1.3, -1.3, -0.6)):
        o.keyframe_insert('location', frame=F(0.3))
        o.location = ((x0 + x1) / 2, -0.3, z); o.keyframe_insert('location', frame=F(DUR * 0.45))
        o.location = (x1, 0, 0); o.keyframe_insert('location', frame=F(DUR * 0.8))
    for k in range(30):
        L.sphere((random.Random(k).uniform(-5, 5), 4, random.Random(k + 50).uniform(-4, 5)), (0.05,) * 3, L.mat('etin', '#FFF6E0', emit=6), seg=8, name='p')
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 40
    cam_path(c, (0, -7.5, 0.6), (0, -6.6, 0.3), (0, 0, 0.1), (0, 0, 0))


def s_explosion():
    L.world('#3A2A6A', '#E890A0', 1.0); L.lights(key='#FFC0A0', rim='#A890FF', k=0.9)
    clouds_field(14, 3, (-6, -3), xr=14, yr=(0, 18), col='#F0D0E0', s=(1.2, 2.4))
    p = plane3d((0, 4, 0.5), 1.0, rot=(0, 0, 0.1))
    te = DUR * 0.38                                   # moment de l'explosion
    p.keyframe_insert('location', frame=1); p.location = (1.2, 4, 0.5); p.keyframe_insert('location', frame=F(te))
    flash = L.sphere((1.2, 4, 0.5), (0.1, 0.1, 0.1), L.mat('flash', '#FFF6E0', emit=30), name='flash')
    flash.scale = (0.01,) * 3; flash.keyframe_insert('scale', frame=F(te - 0.05))
    flash.scale = (2.2,) * 3; flash.keyframe_insert('scale', frame=F(te + 0.3))
    flash.scale = (0.01,) * 3; flash.keyframe_insert('scale', frame=F(te + 0.9))
    rnd = random.Random(4)
    for o in p.children:                              # les morceaux s'écartent doucement, comme des pétales
        o.keyframe_insert('location', frame=F(te)); o.keyframe_insert('rotation_euler', frame=F(te))
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-0.6, 0.6), rnd.uniform(-1, 0.6))).normalized() * rnd.uniform(1.5, 3.5)
        o.location = o.location + d; o.rotation_euler = (rnd.uniform(-1.5, 1.5), rnd.uniform(-1.5, 1.5), rnd.uniform(-1.5, 1.5))
        o.keyframe_insert('location', frame=F(DUR)); o.keyframe_insert('rotation_euler', frame=F(DUR))
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 35
    cam_path(c, (0, -9, 1.2), (0.6, -8.0, 0.9), (0.4, 4, 0.5), (1.2, 4, 0.3))


def s_cocon():                       # elle tombe, endormie, dans un morceau d'avion, tenue par le chariot
    L.world('#6A80D0', '#FFD8E0', 1.0); L.lights(key='#FFE0D0', rim='#B8A8FF', k=1.1)
    before = set(bpy.data.objects)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.4, depth=2.6, location=(0, 0.6, 0), rotation=(0, math.pi / 2, 0)); tr = bpy.context.object
    tr.data.materials.append(L.mat('fus2', '#F2ECE4', rough=0.35))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.95, 0.35)); cut = bpy.context.object; cut.scale = (3.2, 1.9, 1.9); cut.hide_render = True; cut.hide_viewport = True
    m = tr.modifiers.new('cut', 'BOOLEAN'); m.object = cut; m.operation = 'DIFFERENCE'
    sol = tr.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = 0.12
    tr.data.materials.append(L.mat('inside', '#9A8AB8', rough=0.8))
    for k in range(4): L.sphere((-0.9 + k * 0.6, 1.95, 0.5), (0.13, 0.05, 0.16), L.mat('win', '#2A3A5A', rough=0.1), seg=16, name='hublot')
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.6, -1.1, -0.75)); t = bpy.context.object; t.scale = (0.6, 0.6, 0.85)
    t.data.materials.append(L.mat('chariot', '#D0D0E0', rough=0.25, metal=0.6))
    v = L.character((-0.35, -1.25, -0.1), 0.45, 0, 'closed', **VESNA)
    root = bpy.data.objects.new('cocon', None); bpy.context.collection.objects.link(root)
    for o in set(bpy.data.objects) - before - {root}:
        if o.parent is None: o.parent = root
    root.rotation_euler = (0.1, 0, -0.15); root.keyframe_insert('rotation_euler', frame=1)
    root.rotation_euler = (0.2, 0.15, 0.2); root.keyframe_insert('rotation_euler', frame=F(DUR))
    objs = clouds_field(20, 5, (-30, 6), xr=8, yr=(2, 12), col='#FFF0F4', clear=3.4)
    for o in objs:
        z = o.location.z; o.keyframe_insert('location', frame=1); o.location.z = z + DUR * 4.5; o.keyframe_insert('location', frame=F(DUR))
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 35
    cam_path(c, (0.3, -8.5, 1.2), (-0.2, -7.5, 0.7), (0, 0.4, 0), (0, 0.4, -0.1))


def s_neige():                        # la pente enneigée, puis Bruno avec sa lanterne
    L.world('#1A2050', '#5A5A9A', 0.9); L.lights(key='#C0D0FF', rim='#8A7CFF', k=0.7)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -3)); g = bpy.context.object; g.rotation_euler = (0.18, 0, 0)
    g.data.materials.append(L.mat('neigesol', '#E8ECFF', rough=0.7)); g.modifiers.new('ss', 'SUBSURF').levels = 3
    tex = bpy.data.textures.new('dn', 'CLOUDS'); tex.noise_scale = 3; d = g.modifiers.new('d', 'DISPLACE'); d.texture = tex; d.strength = 0.6
    rnd = random.Random(8)
    for _ in range(26): pine((rnd.uniform(-12, 12), rnd.uniform(3, 20), -2.5 + rnd.uniform(-0.2, 1.5)), rnd.uniform(1.6, 3.2))
    for k in range(4):                                # chalets aux fenêtres chaudes
        x = -9 + k * 5.5
        L.sphere((x, 18, -1.2), (1.6, 1.3, 1.1), L.mat('chalet', '#6A4A5A', rough=0.9), name='chalet')
        L.sphere((x, 16.8, -1.1), (0.35, 0.1, 0.3), L.mat('fenetre', '#FFD890', emit=4), name='fen')
    L.cyl((1.8, 1.4, -2.1), 0.8, 0.8, 2.4, L.mat('fus2', '#F2ECE4', rough=0.35), rot=(0.2, math.pi / 2, 0.5), name='epave')
    for k in range(3): L.sphere((1.2 + k * 0.5, 0.75, -1.85 + k * 0.1), (0.1, 0.04, 0.12), L.mat('win', '#2A3A5A', rough=0.1), seg=16, name='hublot')
    b = L.character((-1.9, 0.6, -0.9), 0.72, 0, 'open', old=True, look=(0.8, 0.0), robe='#6A4A3A', hat='bonnet', beard=True)
    b.keyframe_insert('location', frame=1); b.location = (-0.5, 0.3, -1.0); b.keyframe_insert('location', frame=F(DUR))
    lt = L.sphere((-1.3, 0.25, -1.9), (0.16, 0.16, 0.22), L.mat('lanterne', '#FFD890', emit=8), name='lanterne'); lt.parent = b; lt.matrix_parent_inverse = b.matrix_world.inverted()
    bpy.ops.object.light_add(type='POINT', location=(-1.3, 0.0, -1.8)); pl = bpy.context.object; pl.data.energy = 250; pl.data.color = (1, 0.8, 0.5)
    pl.parent = b; pl.matrix_parent_inverse = b.matrix_world.inverted()
    snowfall(140, 3, (-6, 6, -4, 6, -3, 5))
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 32
    cam_path(c, (0, -8.0, 0.2), (0.3, -7.2, 0.0), (-0.6, 1, -1.0), (0.2, 1, -1.1))


def s_hopital():                      # le lit, puis elle remarche
    L.world('#C8D8F0', '#F0E0F0', 1.2); L.lights(key='#FFF0E0', rim='#C0B8FF', k=1.2)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -3)); bpy.context.object.data.materials.append(L.mat('sol', '#D8D0E8', rough=0.6))
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 6, 0), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(L.mat('mur', '#E8E0F4', rough=0.9))
    half = DUR * 0.55
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.6, 1.8, -2.55)); o = bpy.context.object; o.scale = (2.6, 3.6, 0.6); o.data.materials.append(L.mat('lit', '#FFFFFF', rough=0.5))
    bv = o.modifiers.new('b', 'BEVEL'); bv.width = 0.1; bv.segments = 4
    L.sphere((-1.6, 3.3, -1.9), (1.0, 0.35, 0.45), L.mat('oreiller', '#F4F0FF', rough=0.8), name='oreiller')
    v = L.character((-1.6, 2.6, -0.95), 0.55, 0, 'lidded', look=(0.4, 0.2), **VESNA)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.6, 1.4, -2.0)); cv_ = bpy.context.object; cv_.scale = (2.4, 2.8, 0.5); cv_.data.materials.append(L.mat('couverture', '#B8C8F0', rough=0.8))
    bv = cv_.modifiers.new('b', 'BEVEL'); bv.width = 0.2; bv.segments = 6
    L.cyl((-1.6, 2.35, -0.55), 0.42, 0.42, 0.18, L.mat('bandage', '#FFF8F0', rough=0.8), name='bandage')
    for k in range(3): L.sphere((1.0 + k * 0.5, 3.5, -0.6 + 0.3 * k), (0.12,) * 3, L.mat('led' + str(k), ['#8AF0C0', '#FFB0C8', '#A8D8FF'][k], emit=5), seg=12, name='led')
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 35
    cam_path(c, (-1.2, -5.5, 0.6), (-1.4, -4.6, 0.4), (-1.6, 2.2, -0.8), (-1.6, 2.2, -0.9))


def s_marche():                        # elle remarche, dans un couloir lumineux
    L.world('#D8E0F8', '#F8E8F0', 1.2); L.lights(key='#FFF0E0', rim='#C0B8FF', k=1.2)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -2.6)); bpy.context.object.data.materials.append(L.mat('sol', '#D8D0E8', rough=0.5))
    for x in (-2.6, 2.6):
        bpy.ops.mesh.primitive_plane_add(size=60, location=(x, 0, 0), rotation=(0, math.pi / 2, 0)); bpy.context.object.data.materials.append(L.mat('mur', '#E8E0F4', rough=0.9))
        for k in range(6): L.sphere((x * 0.98, 2 + k * 3, 1.2), (0.05, 0.6, 0.3), L.mat('lampe', '#FFF4D8', emit=6), seg=12, name='lampe')
    for x in (-1.4, 1.4): L.cyl((x, 2.5, -1.4), 0.05, 0.05, 8, L.mat('barre', '#C8C8E0', rough=0.2, metal=0.7), rot=(math.pi / 2, 0, 0), name='barre')
    w = L.character((0, 6.0, -0.45), 0.7, 0, 'open', look=(0.0, 0.1), **VESNA)
    w.keyframe_insert('location', frame=1); w.location = (0, 1.2, -0.45); w.keyframe_insert('location', frame=F(DUR))
    for k in range(int(N) + 1):
        w.rotation_euler = (0, 0.08 * math.sin(k * 1.7), 0); w.location.z = -0.45 + 0.04 * abs(math.sin(k * 1.7)); w.keyframe_insert('rotation_euler', frame=k + 1)
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 35
    cam_path(c, (0, -6.5, 0.6), (0, -5.5, 0.4), (0, 4, -0.4), (0, 1.5, -0.4))


def s_guinness():                      # la scène de fête et la silhouette à la guitare
    L.world('#2A1A4A', '#8A3A7A', 0.8); L.lights(key='#FFD8A0', rim='#FF80C8', k=1.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=6, depth=0.6, location=(0, 2, -3.2)); bpy.context.object.data.materials.append(L.mat('scene', '#4A2A5A', rough=0.6))
    bpy.ops.object.light_add(type='SPOT', location=(0, -1, 7)); sp = bpy.context.object; sp.data.energy = 3000; sp.data.spot_size = 0.7; sp.data.color = (1, 0.9, 0.7)
    sp.rotation_euler = (0.15, 0, 0)
    v = L.character((-1.2, 1.0, -0.55), 0.75, 0, 'open', look=(0.6, 0.3), **VESNA)
    sil = L.mat('silhouette', '#1A1430', rough=0.6)            # silhouette méconnaissable avec une guitare
    L.sphere((1.8, 1.6, 0.9), (0.42, 0.42, 0.5), sil, name='tete')
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.7, radius2=0.35, depth=2.6, location=(1.8, 1.6, -1.5)); bpy.context.object.data.materials.append(sil)
    L.sphere((1.6, 1.2, -1.2), (0.45, 0.12, 0.5), L.mat('guitare', '#C86A3A', rough=0.3), name='guitare')
    L.cyl((1.15, 1.2, -0.7), 0.05, 0.05, 1.3, L.mat('manche', '#6A3A2A'), rot=(0, 0.9, 0), name='manche')
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.3, 0.9, -0.2)); dip = bpy.context.object
    dip.scale = (0.9, 0.05, 0.65); dip.data.materials.append(L.mat('diplome', '#F8E8B8', rough=0.3, emit=0.4))
    dip.keyframe_insert('location', frame=1); dip.location = (-0.1, 0.8, -0.3); dip.keyframe_insert('location', frame=F(DUR * 0.6))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.5, 1.6)); bk = bpy.context.object
    bk.scale = (3.2, 0.3, 2.2); bk.data.materials.append(L.mat('livre', '#E8B840', rough=0.25, metal=0.7))
    text3d('GUINNESS', (0, 4.3, 1.9), 0.55, '#3A1A2A'); text3d('1972', (0, 4.3, 1.2), 0.5, '#3A1A2A')
    rnd = random.Random(2); cols = ['#FFB8D8', '#FFE7A0', '#A8E8FF', '#C8B8FF', '#A8F0C8']
    conf = []
    for k in range(120):
        bpy.ops.mesh.primitive_plane_add(size=0.12, location=(0, 0, 0)); o = bpy.context.object
        o.data.materials.append(L.mat('conf' + str(k % 5), cols[k % 5], rough=0.4, emit=0.5))
        conf.append((o, rnd.uniform(-5, 5), rnd.uniform(-1, 4), rnd.uniform(0, 8), rnd.uniform(0, 6)))
    def up(t):
        for o, x, y, z0, ph in conf:
            o.location = (x + 0.2 * math.sin(t * 2 + ph), y, 5 - (z0 + t * 1.2) % 9)
            o.rotation_euler = (t * 3 + ph, t * 2 + ph, ph)
    ANIM.append(up)
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 34
    cam_path(c, (0.2, -8.5, 0.8), (0.2, -7.3, 0.4), (0.2, 1.5, -0.1), (0.1, 1.3, -0.2))


def s_fin():                           # debout sur un nuage, au lever du soleil
    L.world('#8A78C0', '#FFC8B0', 1.3); L.lights(key='#FFE0C0', rim='#FFB0D8', fill='#B8E8FF', k=1.3)
    L.sphere((0, 25, -3), (6, 6, 6), L.mat('soleil2', '#FFD8A0', emit=3.5), name='soleil')
    L.cloud((0, 0, -3.3), 1.6, '#FFF0F4', seed=9)
    clouds_field(12, 7, (-6, 4), xr=12, yr=(6, 20), col='#FFE6EE')
    v = L.character((0, 0, -0.45), 0.75, 0, 'open', look=(0.0, -0.1), **VESNA)
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(c); sc.camera = c; c.data.lens = 36
    cam_path(c, (0, -10, 0.4), (0, -7.2, 0.3), (0, 0, -0.3), (0, 0, 0.0))


globals()['s_' + SHOT]()
L.on_frame(lambda t: (L.animate_hair(t), [f(t) for f in ANIM]) if SHOT in ('chute', 'cocon') else (L.animate_hair(t), L.blink(t), [f(t) for f in ANIM]))
if PREV is not None:
    sc.frame_set(int(F(PREV))); sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = OUT + '/f_'; sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(animation=True)

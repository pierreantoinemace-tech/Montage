"""Plans 3D de l'histoire de Vesna (Blender/EEVEE). Usage :
blender -b --python shots.py -- <plan> <durée_s> <dossier_sortie> <rx> <ry> [t_aperçu]"""
import sys, math, random
sys.path.insert(0, '/home/user/Montage/test3d')
import bpy, lib3d as L
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:]
SHOT, DUR, OUT, RX, RY = a[0], float(a[1]), a[2], int(a[3]), int(a[4])
PREV = float(a[5]) if len(a) > 5 else None
FPS = 30
N = max(2, int(round(DUR * FPS)))
sc = L.setup(RX, RY, samples=int(__import__('os').environ.get('SAMPLES','32')), fps=FPS)
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


# ---------------- habillage des décors (pour qu'aucun plan ne soit vide) ----------------
def box(loc, scale, m, bev=0.06, rot=(0, 0, 0), name='bx'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.scale = scale; o.name = name
    o.data.materials.append(m)
    if bev: b = o.modifiers.new('b', 'BEVEL'); b.width = bev; b.segments = 3
    return o


def glow(loc, r, col, e=6): return L.sphere(loc, (r, r, r), L.mat('gl' + col, col, emit=e), seg=12, name='glow')


def balloon(loc, col, h=1.6):
    x, y, z = loc
    L.sphere((x, y, z + h), (0.32, 0.3, 0.38), L.mat('bal' + col, col, rough=0.2), name='ballon')
    L.curve([(x, y, z), (x + 0.08, y, z + h * 0.5), (x, y, z + h - 0.35)], [1, 1, 1], L.mat('fil', '#F4F0FF'), bevel=0.008, name='fil')


def floaty(objs, amp=0.15, sp=1.0):          # léger flottement de rêve
    base = [(o, o.location.z, o.rotation_euler.z, random.random() * 6.3) for o in objs]
    ANIM.append(lambda t: [(setattr(o.location, 'z', z + amp * math.sin(t * sp + ph)), setattr(o.rotation_euler, 'z', rz + 0.25 * math.sin(t * sp * 0.7 + ph))) for o, z, rz, ph in base])


def dress_hotesse():
    rnd = random.Random(4)
    pastel = ['#F2B8C8', '#C8B8F0', '#F8D8A8', '#B8E0E8', '#E8C0F0']
    for k in range(9):                                     # aérogare en blocs pastel, fenêtres allumées
        x = -14 + k * 3.4; h = rnd.uniform(2.5, 5.5)
        box((x, 20, -2.95 + h / 2), (3.2, 2.5, h), L.mat('bat' + str(k % 5), pastel[k % 5], rough=0.5), bev=0.15)
        for r in range(int(h / 0.9)):
            for c_ in range(3): box((x - 0.9 + c_ * 0.9, 18.7, -2.4 + r * 0.9), (0.45, 0.05, 0.35), L.mat('fen', '#FFE7A8', emit=4), bev=0)
    L.cyl((-7, 15, 0), 0.5, 0.35, 6, L.mat('tour', '#E8D8F0', rough=0.4), name='tour')
    L.sphere((-7, 15, 3.4), (1.1, 1.1, 0.7), L.mat('vitre', '#8AE0F0', emit=1.5, rough=0.1), name='vigie')
    for k in range(16):                                    # balises de piste
        for x in (-3.2, 5.0): glow((x, -1 + k * 1.4, -2.9), 0.07, '#7FD0FF' if x < 0 else '#FFB070', 8)
    for k in range(6): L.cloud((rnd.uniform(-14, 14), rnd.uniform(26, 34), rnd.uniform(4, 9)), rnd.uniform(1.0, 1.8), '#FFD8DC', seed=k)
    box((2.8, 0.4, -2.55), (0.7, 0.35, 0.8), L.mat('valise', '#E8687A', rough=0.35), bev=0.1)     # sa valise
    L.cyl((2.8, 0.4, -2.05), 0.04, 0.04, 0.3, L.mat('poignee', '#3A2A50'), name='poignee')
    box((-1.6, 5.4, -2.0), (0.9, 2.6, 0.12), L.mat('escalier', '#F4F0FF', rough=0.4), rot=(0.55, 0, 0.12))  # passerelle
    floaty([glow((rnd.uniform(-4, 6), rnd.uniform(1, 6), rnd.uniform(0, 3)), 0.06, '#FFF0C0', 6) for _ in range(14)], 0.3, 0.8)


def dress_confusion():
    rnd = random.Random(8)
    L.stars(80, 3)
    sheets = []
    for k in range(14):                                    # plannings d'équipage qui volent
        o = box((rnd.uniform(-4, 4), rnd.uniform(1.5, 5), rnd.uniform(-4, 4.5)), (0.7, 0.02, 0.95), L.mat('feuille', '#FFF8EC', rough=0.6), bev=0.01,
                rot=(rnd.uniform(1.2, 1.9), rnd.uniform(-0.5, 0.5), rnd.uniform(-0.6, 0.6)))
        for r in range(4): box((o.location.x, o.location.y - 0.03, o.location.z + 0.3 - r * 0.18), (0.5, 0.01, 0.05), L.mat('ligne', '#B8A8D8'), bev=0, rot=o.rotation_euler).parent = o
        sheets.append(o)
    floaty(sheets, 0.35, 0.9)
    for x, col in ((-2.6, '#FFB0D0'), (2.6, '#9FE0FF')):
        q = text3d('?', (x, 2.5, 2.4), 1.6, col, emit=2.5); sheets.append(q)
    clouds_field(10, 3, (-6, -3.5), xr=7, yr=(1, 6), col='#E8C8F0')
    L.orb((0, 3, 3.5), 0.25, '#FFE7A0', 5)


def dress_cocon():
    rnd = random.Random(2)
    things = []
    for k in range(10):                                    # objets de cabine qui flottent autour
        loc = (rnd.uniform(-2.6, 2.6), rnd.uniform(-2, 1), rnd.uniform(-2.2, 2.4))
        if k % 3 == 0: o = L.cyl(loc, 0.12, 0.09, 0.22, L.mat('tasse', '#FFFFFF', rough=0.2), name='tasse')
        elif k % 3 == 1: o = box(loc, (0.45, 0.03, 0.6), L.mat('magazine', rnd.choice(['#F28AA8', '#8AC8F2', '#F2D08A'])), bev=0.01)
        else: o = box(loc, (0.5, 0.04, 0.35), L.mat('plateau', '#C8C0E8', rough=0.3), bev=0.02)
        o.rotation_euler = (rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3)); things.append(o)
    floaty(things, 0.4, 1.3)
    for k in range(3): box((-1.0 + k * 0.75, 1.3, -0.9), (0.55, 0.5, 0.9), L.mat('siege', '#7A5AC8', rough=0.5), bev=0.12)
    L.stars(60, 5)
    for k in range(8): glow((rnd.uniform(-3, 3), rnd.uniform(-1, 3), rnd.uniform(-3, 3)), 0.05, '#FFE8B0', 8)


def dress_hopital():
    box((1.6, 5.9, 0.6), (3.0, 0.1, 2.4), L.mat('ciel', '#9FD8FF', emit=1.6), bev=0)                       # fenêtre sur le ciel
    for z in (-0.6, 1.8): box((1.6, 5.85, z), (3.2, 0.15, 0.12), L.mat('cadre', '#FFFFFF'), bev=0.02)
    for x in (0.0, 1.6, 3.2): box((x, 5.85, 0.6), (0.12, 0.15, 2.5), L.mat('cadre', '#FFFFFF'), bev=0.02)
    L.cloud((1.2, 5.7, 1.0), 0.35, '#FFFFFF', seed=4); L.cloud((2.4, 5.7, 0.2), 0.28, '#FFFFFF', seed=6)
    box((0.6, 3.2, -2.45), (0.9, 0.8, 1.1), L.mat('chevet', '#F2C8A8', rough=0.5), bev=0.08)                # table de chevet + fleurs
    L.cyl((0.6, 3.2, -1.65), 0.14, 0.18, 0.5, L.mat('vase', '#8AC8F0', rough=0.15), name='vase')
    for k in range(5): L.sphere((0.6 + 0.18 * math.cos(k * 1.3), 3.2 + 0.1 * math.sin(k * 1.3), -1.15 + 0.08 * k % 0.2), (0.11,) * 3,
                                L.mat('fleur' + str(k % 3), ['#FF8AB0', '#FFD86A', '#C8A0FF'][k % 3], rough=0.4), seg=16, name='fleur')
    for k, col in enumerate(('#FF8AB0', '#FFD86A', '#8AD8FF')): balloon((-3.6 + k * 0.45, 3.4, -1.9), col, 1.9 + 0.3 * k)   # ballons « bon rétablissement »
    L.cyl((-3.9, 2.0, -1.0), 0.03, 0.03, 4, L.mat('perf', '#D8D8E8', metal=0.6, rough=0.2), name='perf')          # perfusion
    L.sphere((-3.9, 2.0, 1.0), (0.2, 0.08, 0.3), L.mat('poche', '#D8F0FF', rough=0.1), name='poche')
    box((2.6, 3.6, -0.6), (0.9, 0.3, 0.7), L.mat('ecran', '#2A2440', rough=0.3), bev=0.05)                    # moniteur avec battement
    L.curve([(2.25, 3.42, -0.6), (2.45, 3.42, -0.6), (2.55, 3.42, -0.35), (2.65, 3.42, -0.8), (2.75, 3.42, -0.6), (2.95, 3.42, -0.6)], [1] * 6,
            L.mat('ecg', '#7CFFB8', emit=6), bevel=0.015, name='ecg')
    box((-0.8, 5.9, 1.6), (1.0, 0.05, 0.75), L.mat('dessin', '#FFE8C8'), bev=0.02)                           # dessin d'enfant au mur
    L.sphere((-0.8, 5.85, 1.7), (0.18, 0.02, 0.18), L.mat('soleild', '#FFB040', emit=1), seg=16, name='d')


def dress_marche():
    rnd = random.Random(6)
    for k in range(5):
        for x in (-2.55, 2.55):
            box((x, 3 + k * 3.2, -1.0), (0.08, 1.3, 2.6), L.mat('porte' + str(k % 3), ['#C8B8F0', '#F2C0D0', '#B8E0D8'][k % 3], rough=0.5), bev=0.03)
            L.sphere((x * 0.96, 3.4 + k * 3.2, -1.1), (0.06,) * 3, L.mat('poignee2', '#F0D080', metal=0.8, rough=0.2), seg=12, name='p')
    for k in range(4):
        for x in (-2.1, 2.1): L.bulb_plant((x, 1.5 + k * 3.2, -2.6), rnd.uniform(0.9, 1.4), rnd.choice(['#FFB0D0', '#FFE08A', '#A8E8FF']), eye=False)
    box((0, 22, 0), (5, 0.1, 6), L.mat('soleilfond', '#FFF0D0', emit=5), bev=0)                                 # lumière au bout du couloir
    box((0, 6, -2.59), (0.25, 30, 0.01), L.mat('guide', '#FFB8D0', emit=0.4), bev=0)                            # ligne de couleur au sol
    for k in range(3): balloon((1.7, 0.8 + k * 0.4, -2.6), ['#FF8AB0', '#FFD86A', '#8AD8FF'][k], 2.6 + 0.2 * k)


def dress_fin():
    rnd = random.Random(10)
    cols = ['#FF9AB0', '#FFC890', '#FFF0A0', '#A8F0C8', '#A8D0FF', '#C8A8FF']        # arc-en-ciel doux
    for i, col in enumerate(cols):
        R = 9 - i * 0.45
        L.curve([(R * math.cos(a), 22, -2 + R * math.sin(a)) for a in [math.pi * u / 8 for u in range(9)]], [1] * 9, L.mat('arc' + col, col, emit=1.4, rough=0.5), bevel=0.22, name='arc')
    for k in range(4):
        x = rnd.choice([-1, 1]) * rnd.uniform(2.6, 5); L.island((x, rnd.uniform(4, 12), rnd.uniform(-1.5, 2.5)), rnd.uniform(0.6, 1.0), seed=k)
    L.stars(50, 9)
    p = plane3d((-8, 16, 3.5), 0.45, rot=(0, 0, -0.3)); p.keyframe_insert('location', frame=1); p.location.x = -2; p.keyframe_insert('location', frame=F(DUR))
    floaty([glow((rnd.uniform(-4, 4), rnd.uniform(-1, 5), rnd.uniform(-2, 3)), 0.06, '#FFF0C0', 7) for _ in range(16)], 0.3, 0.8)


if 'dress_' + SHOT in globals(): globals()['dress_' + SHOT]()


# ---------------- remplissage : arrière-plans en couches + premiers plans flous ----------------
def mountains(y, n, col, h=(4, 9), z0=-3, xr=30, seed=1, snow=False):
    rnd = random.Random(seed)
    for k in range(n):
        x = -xr + 2 * xr * k / max(1, n - 1) + rnd.uniform(-2, 2); hh = rnd.uniform(*h)
        L.cyl((x, y + rnd.uniform(-3, 3), z0 + hh / 2), hh * 0.6, 0.0, hh, L.mat('mont' + col, col, rough=0.8), name='mont')
        if snow: L.cyl((x, y - 0.2, z0 + hh * 0.88), hh * 0.15, 0.0, hh * 0.24, L.mat('neige_sommet', '#F4F4FF', rough=0.6), name='neige')


def cloud_bank(y, z, col, n=10, xr=16, seed=3, s=(1.6, 2.8)):
    rnd = random.Random(seed)
    for k in range(n): L.cloud((-xr + 2 * xr * k / (n - 1), y + rnd.uniform(-2, 2), z + rnd.uniform(-1, 1.5)), rnd.uniform(*s), col, seed=seed * 10 + k)


def cam_place(x, y, d):                       # position dans le repère caméra (x, y en écran, d = distance)
    sc.frame_set(int(F(DUR / 2))); return tuple(sc.camera.matrix_world @ Vector((x * d, y * d, -d)))


def fg_clouds(col='#FFE6EE', n=3, seed=5):
    rnd = random.Random(seed)
    for k in range(n):
        sx = rnd.choice([-1, 1]) * rnd.uniform(0.4, 0.5); L.cloud(cam_place(sx, rnd.uniform(-0.8, -0.4) if k % 2 else rnd.uniform(0.5, 0.8), 2.6), rnd.uniform(0.18, 0.26), col, seed=seed + k)


def fg_plants(n=4, seed=7, cols=('#FF8AB0', '#FFD86A', '#8AD8FF')):
    rnd = random.Random(seed)
    for k in range(n):
        x, y, z = cam_place(rnd.choice([-1, 1]) * rnd.uniform(0.28, 0.42), -0.85, 2.8); L.bulb_plant((x, y, z - 0.4), rnd.uniform(0.6, 1.1), rnd.choice(cols), eye=False)


def lamp_post(x, y, z0, h=3.2, col='#FFD890'):
    L.cyl((x, y, z0 + h / 2), 0.05, 0.05, h, L.mat('poteau', '#3A3050', rough=0.4, metal=0.5), name='poteau'); L.orb((x, y, z0 + h + 0.1), 0.16, col, 7)


def fill_chute():
    L.stars(120, 12); L.big_moon((-6, 40, 12), 5, '#F6D8E8')
    cloud_bank(30, -6, '#E8A8C8', 12, seed=2); cloud_bank(22, 6, '#F4C0D8', 8, seed=4)
    for k in range(6): L.orb((random.Random(k).uniform(-5, 5), random.Random(k + 9).uniform(8, 16), random.Random(k + 3).uniform(-3, 6)), 0.12, '#FFE7A0', 4)


def fill_hotesse():
    mountains(45, 12, '#7A5A8A', (6, 12), seed=2); mountains(38, 10, '#9A6A8A', (3, 7), seed=5)
    cloud_bank(42, 9, '#FFC0B0', 9, seed=6)
    for k in range(5):
        lamp_post(-4.2, 1 + k * 3.5, -2.95); lamp_post(6.4, 1 + k * 3.5, -2.95)
    for k in range(4): L.cyl((-2.6 + k * 0.5, -0.8, -2.7), 0.18, 0.02, 0.5, L.mat('plot', '#FF7A3A', rough=0.4), name='plot')
    for k in range(2):                                     # chariots à bagages
        box((4.2 + k * 1.6, 3, -2.6), (1.3, 0.8, 0.12), L.mat('chariot2', '#4A6AC8', rough=0.4), bev=0.03)
        for j in range(3): box((3.8 + k * 1.6 + j * 0.4, 3, -2.3), (0.35, 0.5, 0.45), L.mat('bag' + str(j), ['#E8687A', '#F2C04A', '#5AC8A8'][j], rough=0.4), bev=0.06)
    fg_clouds('#FFD0C8', 2)


def fill_confusion():
    L.big_moon((4, 30, 8), 3, '#F0D8FF'); cloud_bank(20, -5, '#B890D8', 10, seed=7); fg_clouds('#E8C8F0', 3)


def fill_explosion(): fg_clouds('#FFD8E0', 2, seed=11)


def fill_cocon():
    L.big_moon((5, 35, 9), 4, '#F6E0F0'); cloud_bank(25, -8, '#C8A0D8', 12, seed=8); cloud_bank(30, 4, '#E8B8D8', 8, seed=9)
    fg_clouds('#F4D8E8', 3, seed=12)


def fill_neige():
    mountains(30, 10, '#2A3A6A', (5, 10), z0=-4, seed=3, snow=True)
    L.big_moon((-5, 34, 9), 2.5, '#FFF0D0')
    for k in range(10):
        x, y, z = cam_place(random.Random(k).choice([-1, 1]) * random.Random(k + 1).uniform(0.3, 0.5), -0.9, random.Random(k + 2).uniform(3, 6))
        pine((x, y, -3.0), random.Random(k + 4).uniform(1.6, 2.6))
    for k in range(5): box((3.5 + k * 1.5, 14 + k, -2.2), (1.0, 1.0, 0.9), L.mat('chalet', '#8A5A4A', rough=0.6), bev=0.05)


def fill_hopital():
    for k in range(9): L.cyl((-4.6 + k * 0.22, 5.8, 0.6), 0.14, 0.14, 4.2, L.mat('rideau', '#E8A0B8', rough=0.7), name='rideau')    # rideau plissé
    box((-0.8, 5.8, -0.2), (2.0, 0.4, 0.08), L.mat('etagere', '#B88A6A'), bev=0.02)
    for k in range(7): box((-1.6 + k * 0.24, 5.75, 0.1), (0.16, 0.3, 0.5 + 0.1 * (k % 3)), L.mat('livre' + str(k % 4), ['#E85A6A', '#4A8AE8', '#F2C04A', '#5AC88A'][k % 4]), bev=0.01)
    for k in range(11):                                    # guirlande d'étoiles en papier
        a = k / 10; x = -4 + 8 * a; z = 2.6 - 0.6 * math.sin(a * math.pi)
        L.sphere((x, 5.6, z), (0.12, 0.04, 0.12), L.mat('guir' + str(k % 3), ['#FFD86A', '#FF8AB0', '#8AD8FF'][k % 3], emit=1.5), seg=8, name='g')
    L.orb((-1.6, 3, 3.6), 0.3, '#FFF0D0', 4)
    box((0, 5.8, -2.0), (12, 0.1, 1.2), L.mat('lambris', '#8A7AB8', rough=0.6), bev=0)
    box((3.6, 1.8, -2.3), (0.9, 0.9, 1.3), L.mat('fauteuil', '#E8687A', rough=0.5), bev=0.15)
    fg_plants(3, seed=8)


def fill_marche():
    for k in range(7): box((0, 1 + k * 3, 2.2), (1.6, 0.4, 0.06), L.mat('plafonnier', '#FFF4D8', emit=4), bev=0)
    for k in range(4):
        for x in (-2.55, 2.55): box((x * 0.99, 4.6 + k * 3.2, 0.6), (0.05, 0.9, 0.7), L.mat('affiche' + str(k % 3), ['#5AC8A8', '#F2C04A', '#E85A8A'][k % 3], emit=0.3), bev=0.01)
    fg_plants(4, seed=9)


def fill_guinness(): pass


def fill_fin():
    cloud_bank(30, -4, '#F0B8C8', 12, seed=13); cloud_bank(26, 6, '#FFD0B8', 8, seed=14)
    for k in range(8):                                     # lanternes qui montent
        r = random.Random(k + 30); x, y, z = r.uniform(-5, 5), r.uniform(4, 14), r.uniform(-3, 2)
        o = L.sphere((x, y, z), (0.16, 0.16, 0.22), L.mat('lanterne', '#FFB050', emit=6), seg=16, name='lanterne')
        o.keyframe_insert('location', frame=1); o.location.z = z + DUR * 0.5; o.keyframe_insert('location', frame=F(DUR))
    fg_clouds('#FFE0E8', 3, seed=15)


globals()['fill_' + SHOT]()


def polish():                               # rendu « film d'animation » : matières satinées, peau translucide, flou de mouvement
    ee = sc.eevee
    ee.use_motion_blur = True; ee.motion_blur_shutter = 0.45; ee.motion_blur_steps = 1
    ee.use_ssr = False
    ee.shadow_cube_size = '1024'; ee.shadow_cascade_size = '1024'; ee.gtao_distance = 0.8
    ee.bloom_intensity = 0.08; sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'; sc.view_settings.exposure = -0.35
    w = bpy.context.scene.world                 # ciel plus profond et plus saturé
    if w and w.use_nodes:
        for nd in w.node_tree.nodes:
            if nd.type == 'BACKGROUND': nd.inputs['Strength'].default_value *= 0.7
            if nd.type == 'VALTORGB':
                for el in nd.color_ramp.elements:
                    c = el.color; m_ = sum(c[:3]) / 3; el.color = tuple(max(0, m_ + (x - m_) * 1.8) * 0.75 for x in c[:3]) + (1,)
    for m in bpy.data.materials:
        if not m.use_nodes or 'Principled BSDF' not in m.node_tree.nodes: continue
        b = m.node_tree.nodes['Principled BSDF']
        if b.inputs['Emission Strength'].default_value > 0:
            if m.name.startswith('soleil'): b.inputs['Emission Strength'].default_value *= 2.5
            continue
        r = b.inputs['Roughness'].default_value
        if not m.name.startswith(('skin', 'eye', 'iris', 'pupil', 'white', 'cloud', 'neige', 'snow')):   # décors : couleurs franches, moins pâles
            c = b.inputs['Base Color'].default_value; mx = max(c[:3]); mn = min(c[:3])
            if mx > 0.35 and (mx - mn) / mx < 0.6:
                m_ = sum(c[:3]) / 3; b.inputs['Base Color'].default_value = tuple(max(0, m_ + (x - m_) * 1.9) * 0.62 for x in c[:3]) + (1,)
        b.inputs['Roughness'].default_value = max(0.22, r * 0.72)
        b.inputs['Sheen Weight'].default_value = 0.12; b.inputs['Sheen Roughness'].default_value = 0.4
        if m.name.startswith('skin'):
            b.inputs['Subsurface Weight'].default_value = 0.3; b.inputs['Subsurface Radius'].default_value = (0.4, 0.25, 0.18)
            b.inputs['Coat Weight'].default_value = 0.12; b.inputs['Coat Roughness'].default_value = 0.25
        elif m.name.startswith('hair'):
            b.inputs['Coat Weight'].default_value = 0.25; b.inputs['Coat Roughness'].default_value = 0.2
    ch = [o for o in bpy.data.objects if o.name.startswith('char')]     # mise au point sur le perso : premiers plans flous
    cam = sc.camera
    if ch and cam:
        cam.data.dof.use_dof = True; cam.data.dof.focus_object = ch[0]; cam.data.dof.aperture_fstop = 2.2
    for o in bpy.data.objects:                 # lumières de contour un peu plus présentes
        if o.type == 'LIGHT' and 'rim' in o.name.lower(): o.data.energy *= 1.35


polish()
L.on_frame(lambda t: (L.animate_hair(t), [f(t) for f in ANIM]) if SHOT in ('chute', 'cocon') else (L.animate_hair(t), L.blink(t), [f(t) for f in ANIM]))
if PREV is not None:
    sc.frame_set(int(F(PREV))); sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = OUT + '/f_'; sc.render.image_settings.file_format = 'PNG'
    sc.render.use_overwrite = False; sc.render.use_placeholder = True   # reprise possible : saute les images déjà faites
    bpy.ops.render.render(animation=True)

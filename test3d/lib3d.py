"""Bibliothèque 3D (Blender) : matériaux, perso aux trois yeux, décors de rêve."""
import bpy, math, random
from mathutils import Vector
sc = None


def setup(rx, ry, samples=16, fps=30):
    global sc
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    sc.render.fps = fps
    ee = sc.eevee
    ee.taa_render_samples = samples
    ee.use_gtao = True; ee.gtao_distance = 0.6
    ee.use_bloom = True; ee.bloom_intensity = 0.06; ee.bloom_threshold = 0.9
    ee.use_soft_shadows = True; ee.shadow_cube_size = '1024'; ee.shadow_cascade_size = '1024'
    sc.view_settings.view_transform = 'Filmic'; sc.view_settings.look = 'Medium High Contrast'
    return sc


def hexc(h, a=1.0):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x ** 2.2 for x in c) + (a,)


MATS = {}
HAIR = []
LIDS = []
def mat(name, col, rough=0.5, emit=0.0, sss=0.0, metal=0.0, spec=0.4):
    key = (name, col, emit)
    if key in MATS: return MATS[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(col); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss; b.inputs['Subsurface Radius'].default_value = (0.3, 0.2, 0.15)
    if emit:
        b.inputs['Emission Color'].default_value = hexc(col); b.inputs['Emission Strength'].default_value = emit
    MATS[key] = m
    return m


def sphere(loc, scale, m, seg=48, smooth=True, name='s'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object; o.scale = scale; o.name = name
    if smooth: bpy.ops.object.shade_smooth()
    o.data.materials.append(m); return o


def cyl(loc, r1, r2, depth, m, rot=(0, 0, 0), name='c'):
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; bpy.ops.object.shade_smooth(); o.data.materials.append(m); return o


def curve(points, radii, m, bevel=1.0, name='crv'):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = bevel; cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(points) - 1)
    for bp, p, r in zip(sp.bezier_points, points, radii):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = r
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o


# ---------------- le perso ----------------
def character(pos=(0, 0, 0), s=1.0, t=0.0, eyes='open', old=False, look=(0.0, 0.0), robe='#4A1E7A', hat=None, beard=False, hair_cols=None, nhair=20, body=True):
    X, Y, Z = pos
    P = lambda x, y, z: (X + x * s, Y + y * s, Z + z * s)
    skin = mat('skin_old' if old else 'skin', '#8FB4C0' if old else '#6EC3D6', rough=0.45, sss=0.15)
    hc = hair_cols or (('#D9D4EA', '#C8C0E8') if old else ('#1C2F5E', '#4A36B0'))
    hairc = mat('hair' + hc[0], hc[0], rough=0.35)
    hairf = mat('hairf' + hc[1], hc[1], rough=0.3)
    before = set(bpy.data.objects)
    head = sphere(P(0, 0, 0), (0.7 * s, 0.62 * s, 0.98 * s), skin, name='head')
    cap = sphere(P(0.04, 0.05, 0.4), (0.73 * s, 0.655 * s, 0.8 * s), hairc, seg=96, name='cap')   # calotte : l'intersection avec la tête dessine une frange lisse
    cap.rotation_euler = (math.radians(-12), math.radians(14), 0)
    # cheveux flottants
    rnd = random.Random(3)
    for i in range(nhair):
        u = i / (nhair - 1); a0 = -1.1 + 2.2 * u
        bx, bz = 0.55 * math.sin(a0) * 0.9, 0.62 + 0.2 * math.cos(a0)
        by = 0.12 + rnd.uniform(-0.15, 0.25)
        L = (1.4 + 1.0 * math.sin(u * math.pi)) * rnd.uniform(0.85, 1.1); ph = rnd.uniform(0, 6.28)
        pts, rad = [], []
        for k in range(7):
            v = k / 6
            x = bx + (u - 0.5) * 1.1 * v + 0.14 * math.sin(v * 5 + ph + t * 1.5) * v
            y = by + 0.15 * math.sin(v * 3 + ph) * v + 0.1 * v
            z = bz + L * v
            pts.append(P(x, y, z)); rad.append(1.0 - 0.85 * v)
        o = curve(pts, rad, hairf if i % 3 else hairc, bevel=0.07 * s, name=f'hair{i}')
        HAIR.append((o, bx, by, bz, u, L, ph, P))
    # yeux
    blink = eyes == 'closed'
    for sx in (-1, 1):
        ex, ey, ez = 0.29 * sx, -0.47, -0.02
        if not blink:
            sphere(P(ex, ey, ez), (0.2 * s, 0.14 * s, 0.2 * s), mat('white', '#F7F2FF', rough=0.15, spec=0.6), name='eyew')
            ix, iz = ex + 0.06 * look[0], ez + 0.05 * look[1] - 0.02
            sphere(P(ix, ey - 0.12, iz), (0.1 * s, 0.03 * s, 0.1 * s), mat('iris', '#24D6BE', rough=0.2), name='iris')
            sphere(P(ix, ey - 0.145, iz), (0.05 * s, 0.015 * s, 0.05 * s), mat('pupil', '#120624', rough=0.1), name='pupil')
            sphere(P(ix - 0.035, ey - 0.16, iz + 0.035), (0.018 * s, 0.006 * s, 0.018 * s), mat('glint', '#FFFFFF', emit=4), name='glint')
        lid = 0.55 if eyes == 'lidded' else (1.0 if blink else 0.28)
        lidm = skin
        o = sphere(P(ex, ey + 0.005, ez + 0.2 * (1 - lid) + 0.02), (0.215 * s, 0.152 * s, 0.2 * lid * s + 0.005), lidm, name='lid')
        LIDS.append((o, lid, ez, P, s, ex, ey))
    # nez, bouche
    sphere(P(0.02, -0.6, -0.22), (0.06 * s, 0.07 * s, 0.13 * s), skin, name='nose')
    curve([P(-0.14, -0.575, -0.53), P(0.0, -0.6, -0.585), P(0.13, -0.575, -0.525)], [1, 1, 1], mat('mouth', '#20102E', rough=0.6), bevel=0.017 * s, name='mouth')
    for sx in (-1, 1): sphere(P(0.4 * sx, -0.44, -0.3), (0.13 * s, 0.05 * s, 0.08 * s), mat('blush', '#E890B0', rough=0.6), name='blush')
    # troisième œil
    sphere(P(0, -0.6, 0.52), (0.17 * s, 0.06 * s, 0.1 * s), mat('teye', '#FFF4D0', rough=0.2, emit=0.4), name='teye')
    sphere(P(0, -0.645, 0.52), (0.07 * s, 0.02 * s, 0.07 * s), mat('teyei', '#F0B030', rough=0.2, emit=1.5), name='teyei')
    sphere(P(0, -0.66, 0.52), (0.032 * s, 0.01 * s, 0.032 * s), mat('teyep', '#120624'), name='teyep')
    bpy.ops.object.light_add(type='POINT', location=P(0, -0.8, 0.55)); L = bpy.context.object
    L.data.energy = 25 * s; L.data.color = (1.0, 0.85, 0.5); L.data.shadow_soft_size = 0.2
    # cou + haut étroit
    cyl(P(0, 0.05, -1.05), 0.21 * s, 0.18 * s, 0.6 * s, skin, name='neck')
    if body:
        robem = mat('robe' + robe, robe, rough=0.7)
        bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.62 * s, radius2=0.34 * s, depth=1.5 * s, location=P(0, 0.08, -2.05))
        bd = bpy.context.object; bd.scale = (1, 0.72, 1); bd.data.materials.append(robem)
        b = bd.modifiers.new('b', 'BEVEL'); b.width = 0.18 * s; b.segments = 8
        bd.modifiers.new('ss', 'SUBSURF').levels = 2; bpy.ops.object.shade_smooth()
        sphere(P(0, 0.08, -1.32), (0.36 * s, 0.26 * s, 0.14 * s), robem, name='col')
        for sx in (-1, 1):                                          # bras fins et souples
            sw = 0.05 * math.sin(t * 2 + sx)
            pts = [P(0.3 * sx, 0.05, -1.45), P(0.52 * sx, 0.0, -1.9), P(0.6 * sx + sw, -0.05, -2.35), P(0.5 * sx + sw, -0.15, -2.62)]
            curve(pts, [1, 0.95, 0.9, 0.85], robem, bevel=0.085 * s, name='arm')
            sphere(P(0.48 * sx + sw, -0.17, -2.68), (0.09 * s, 0.09 * s, 0.1 * s), skin, name='hand')
    if hat == 'toque':                                          # petite toque d'hôtesse
        cyl(P(0.12, -0.05, 0.98), 0.3 * s, 0.27 * s, 0.22 * s, mat('toque', '#3A2A8A', rough=0.5), rot=(math.radians(-12), math.radians(14), 0), name='toque')
        sphere(P(0.12, -0.32, 0.95), (0.05 * s, 0.02 * s, 0.05 * s), mat('or', '#F0C860', rough=0.25, metal=0.8), name='badge')
    elif hat == 'bonnet':
        sphere(P(0, 0.05, 0.62), (0.76 * s, 0.7 * s, 0.6 * s), mat('bonnet', '#A84A4A', rough=0.9), name='bonnet')
        sphere(P(0, 0.05, 1.2), (0.16 * s, 0.16 * s, 0.16 * s), mat('pompon', '#F4EEE4', rough=1), name='pompon')
    if beard:
        sphere(P(0, -0.38, -0.72), (0.5 * s, 0.32 * s, 0.42 * s), mat('beard', '#E4E0EC', rough=0.9), name='beard')
    root = bpy.data.objects.new('char', None); bpy.context.collection.objects.link(root)
    for o in set(bpy.data.objects) - before - {root}:
        if o.parent is None: o.parent = root
    return root


# ---------------- décor ----------------
def stars(n, seed, rmin=16, rmax=26):
    rnd = random.Random(seed); m = mat('star', '#FFF6E0', emit=12)
    for _ in range(n):
        th = rnd.uniform(-1.2, 1.2); ph = rnd.uniform(-0.2, 1.2); r = rnd.uniform(rmin, rmax)
        p = (r * math.sin(th), r * math.cos(th) * math.cos(ph) + 6, r * math.sin(ph))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rnd.uniform(0.03, 0.08), location=p)
        bpy.context.object.data.materials.append(m)


def island(loc, r, top='#3E7A74', rock='#4A3A6A', seed=0):
    x, y, z = loc
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=r, depth=0.25 * r, location=(x, y, z))
    t = bpy.context.object; bpy.ops.object.shade_smooth(); t.data.materials.append(mat('grass' + top, top, rough=0.8))
    bev = t.modifiers.new('b', 'BEVEL'); bev.width = 0.08 * r; bev.segments = 6
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r * 0.98, radius2=0.05, depth=1.5 * r, location=(x, y, z - 0.85 * r), rotation=(math.pi, 0, 0))
    k = bpy.context.object; k.data.materials.append(mat('rock' + rock, rock, rough=0.9))
    rnd = random.Random(seed + 7)
    for _ in range(int(60 * r)):
        a = rnd.uniform(0, 6.28); d = r * 0.97 * math.sqrt(rnd.random())
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.035 * r, radius2=0, depth=rnd.uniform(0.08, 0.2) * r, location=(x + d * math.cos(a), y + d * math.sin(a), z + 0.14 * r), rotation=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0))
        bpy.context.object.data.materials.append(mat('grass2' + top, top, rough=0.8))
    for _ in range(int(2.5 * r)):
        a = rnd.uniform(0, 6.28); d = r * rnd.uniform(0.4, 0.9)
        sphere((x + d * math.cos(a), y + d * math.sin(a), z + 0.13 * r), (0.07 * r, 0.055 * r, 0.04 * r), mat('peb', '#6A6A88', rough=0.7), seg=16, name='peb')
    tex = bpy.data.textures.new(f'n{seed}', 'CLOUDS'); tex.noise_scale = 0.4 * r
    k.modifiers.new('ss', 'SUBSURF').levels = 2
    d = k.modifiers.new('d', 'DISPLACE'); d.texture = tex; d.strength = 0.18 * r
    for pg in k.data.polygons: pg.use_smooth = True


def bulb_plant(loc, h, col, t=0.0, ph=0.0, eye=True):
    x, y, z = loc; sw = 0.12 * math.sin(t * 1.2 + ph)
    pts = [(x, y, z), (x - 0.08, y, z + h * 0.35), (x + 0.1 + sw * 0.5, y, z + h * 0.7), (x + sw, y, z + h)]
    curve(pts, [1, 0.9, 0.8, 0.7], mat('stem', '#2E6A5A', rough=0.6), bevel=0.04, name='stem')
    sphere((x + sw, y, z + h + 0.12), (0.17, 0.17, 0.17), mat('bulb' + col, col, rough=0.3, emit=1.2), name='bulb')
    if eye:
        sphere((x + sw, y - 0.14, z + h + 0.13), (0.07, 0.03, 0.07), mat('bpupil', '#120624'), name='bp')


def cloud(loc, s, col='#FFE6EE', seed=0):
    rnd = random.Random(seed); x, y, z = loc; m = mat('cloud' + col, col, rough=0.9, emit=0.25)
    for k in range(7):
        sphere((x + rnd.uniform(-1.3, 1.3) * s, y + rnd.uniform(-0.2, 0.2) * s, z + rnd.uniform(-0.2, 0.35) * s), (rnd.uniform(0.5, 0.9) * s,) * 3, m, seg=24, name='cl')


def orb(loc, r, col='#FFE7A0', emit=6):
    sphere(loc, (r, r, r), mat('orb' + col, col, emit=emit), name='orb')
    bpy.ops.object.light_add(type='POINT', location=loc); L = bpy.context.object
    L.data.energy = 40 * r * 10; c = col.lstrip('#'); L.data.color = tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)); L.data.shadow_soft_size = r


def world(top, bottom, strength=1.0):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes['Background']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = hexc(bottom)
    ramp.color_ramp.elements[1].position = 0.8; ramp.color_ramp.elements[1].color = hexc(top)
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = strength


def lights(key='#FFD2B0', rim='#8A7CFF', fill='#5AD7FF', k=1.0):
    def area(loc, rot, size, energy, col):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); L = bpy.context.object
        L.data.size = size; L.data.energy = energy * k; c = col.lstrip('#'); L.data.color = tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
    area((-4, -5, 3), (math.radians(60), 0, math.radians(-38)), 4, 900, key)
    area((4.5, 3, 3), (math.radians(-60), 0, math.radians(130)), 3, 1300, rim)
    area((3, -5, -1), (math.radians(95), 0, math.radians(30)), 5, 300, fill)


def camera(loc, look, lens=50):
    sc = bpy.context.scene
    bpy.ops.object.camera_add(location=loc); c = bpy.context.object; sc.camera = c; c.data.lens = lens
    d = Vector(look) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.dof.use_dof = True; c.data.dof.focus_distance = d.length; c.data.dof.aperture_fstop = 4.0


def big_moon(loc, r, col='#F6E6C8'):
    sphere(loc, (r, r, r), mat('moon', col, emit=0.55, rough=0.9), name='moon')
    rnd = random.Random(5)
    for _ in range(7):
        a = rnd.uniform(0, 6.28); d = r * rnd.uniform(0.1, 0.75)
        rr = r * rnd.uniform(0.08, 0.2); sphere((loc[0] + d * math.cos(a), loc[1] - math.sqrt(max(0, r * r - d * d)) + rr * 0.15, loc[2] + d * math.sin(a)), (rr, rr * 0.25, rr), mat('crat', '#D8C8B0', emit=0.35, rough=1), seg=24, name='crat')




def animate_hair(t):
    for o, bx, by, bz, u, L, ph, P in HAIR:
        for k, bp in enumerate(o.data.splines[0].bezier_points):
            v = k / 6
            x = bx + (u - 0.5) * 1.1 * v + 0.14 * math.sin(v * 5 + ph + t * 1.5) * v
            y = by + 0.15 * math.sin(v * 3 + ph + t * 0.7) * v + 0.1 * v
            z = bz + L * v * (1 + 0.03 * math.sin(t * 1.1 + ph))
            bp.co = P(x, y, z)


def blink(t, every=3.3, dur=0.14, seed=0.0):
    c = ((t + seed) % every) < dur
    for o, lid, ez, P, s, ex, ey in LIDS:
        l = 1.0 if c else lid
        o.scale[2] = 0.2 * l * s + 0.005
        o.location = P(ex, ey + 0.005, ez + 0.2 * (1 - l) + 0.02)


def on_frame(fn):
    def h(scene, *a):
        t = (scene.frame_current - 1) / scene.render.fps
        fn(t)
    bpy.app.handlers.frame_change_pre.append(h)


def key(o, frame, **props):
    for k, v in props.items():
        setattr(o, k, v); o.keyframe_insert(data_path=k, frame=frame)

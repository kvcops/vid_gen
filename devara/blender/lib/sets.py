"""Environments and props. Every builder is deterministic (seeded)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler
from . import core as C

# ------------------------------------------------------------------ lights / sky
def light(kind, name, loc=(0, 0, 0), rot=(0, 0, 0), energy=10, color=(1, 1, 1), size=None, spot=None):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if size is not None:
        if kind == 'AREA': ld.size = size
        elif kind == 'SUN': ld.angle = size
        else: ld.shadow_soft_size = size
    if spot: ld.spot_size = math.radians(spot); ld.spot_blend = 0.4
    o = bpy.data.objects.new(name, ld); C.link(o); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]
    return o

def sky_day(sc, sun_elev=35, sun_rot=40, strength=0.35):
    w = bpy.data.worlds.new('sky'); sc.world = w
    try: w.use_nodes = True
    except Exception: pass
    nt = w.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground'); sky = nt.nodes.new('ShaderNodeTexSky')
    for t in ('MULTIPLE_SCATTERING', 'SINGLE_SCATTERING', 'NISHITA', 'HOSEK_WILKIE'):
        try: sky.sky_type = t; break
        except Exception: pass
    for k, v in (('sun_elevation', math.radians(sun_elev)), ('sun_rotation', math.radians(sun_rot)), ('altitude', 50), ('air_density', 1.2), ('dust_density', 1.5)):
        try: setattr(sky, k, v)
        except Exception: pass
    bg.inputs[1].default_value = strength
    nt.links.new(sky.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs['Surface'])
    return w

def sky_night(sc, top=(0.004, 0.008, 0.025), horizon=(0.03, 0.035, 0.06), stars=True, tint=None, strength=1.0):
    w, nt, bg, out = C.world_color(sc, top, horizon, strength)
    if stars:
        add = nt.nodes.new('ShaderNodeAddShader'); em = nt.nodes.new('ShaderNodeEmission')
        tc = nt.nodes.new('ShaderNodeTexCoord'); vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 420
        nt.links.new(tc.outputs['Generated'], vor.inputs['Vector'])
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs[1].default_value = 0.0; mr.inputs[2].default_value = 0.035
        mr.inputs[3].default_value = 1.0; mr.inputs[4].default_value = 0.0
        nt.links.new(vor.outputs['Distance'], mr.inputs[0])
        sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
        hz = nt.nodes.new('ShaderNodeMapRange'); hz.inputs[1].default_value = 0.0; hz.inputs[2].default_value = 0.25
        nt.links.new(sep.outputs['Z'], hz.inputs[0])
        nt.links.new(mr.outputs[0], mul.inputs[0]); nt.links.new(hz.outputs[0], mul.inputs[1])
        em.inputs[0].default_value = (1, 0.95, 0.9, 1); nt.links.new(mul.outputs[0], em.inputs[1])
        nt.links.new(bg.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
        nt.links.new(add.outputs[0], out.inputs['Surface'])
    return w, nt, out

def world_fog(sc, density=0.01, color=(0.5, 0.55, 0.65), anis=0.3, size=(260, 260, 40), center=(0, 0, 18)):
    """Fog as a finite volume box (a world volume in EEVEE would swallow sun/moon light completely)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=center); o = bpy.context.object; o.name = 'fogbox'; o.scale = size
    m = bpy.data.materials.new('fogm')
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); v = nt.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Density'].default_value = density; v.inputs['Color'].default_value = (*color, 1); v.inputs['Anisotropy'].default_value = anis
    nt.links.new(v.outputs[0], out.inputs['Volume'])
    o.data.materials.append(m)
    o.visible_shadow = False
    return v

def moon(loc=(-60, 200, 70), r=6, strength=8):
    m = C.prim('sphere', 'moon', loc=loc, radius=r, segments=32, ring_count=16)
    C.assign(m, C.emission_mat('moonmat', (0.95, 0.93, 0.85), strength))
    m.visible_shadow = False
    return m

# ------------------------------------------------------------------ water
def ocean(name='ocean', size=1.0, spatial=60, res=11, choppy=1.2, wave_scale=1.2, t_speed=1.0, frames=240,
          color=(0.006, 0.03, 0.045), foam=True, loc=(0, 0, 0), repeat=3, red=0.0, seed=1, wind=10, damp=0.5):
    bpy.ops.mesh.primitive_plane_add(size=2, location=loc); o = bpy.context.object; o.name = name
    m = o.modifiers.new('ocean', 'OCEAN')
    m.geometry_mode = 'GENERATE'; m.size = size; m.spatial_size = spatial; m.resolution = res
    m.repeat_x = m.repeat_y = repeat; m.choppiness = choppy; m.wave_scale = wave_scale; m.random_seed = seed
    m.wind_velocity = wind; m.damping = damp
    try: m.wave_scale_min = 0.01
    except Exception: pass
    if foam:
        m.use_foam = True; m.foam_layer_name = 'foam'; m.foam_coverage = 0.35
    m.time = 0; m.keyframe_insert('time', frame=1)
    m.time = t_speed * frames / C.FPS; m.keyframe_insert('time', frame=frames + 1)
    C.all_linear(o)
    for p in o.data.polygons: p.use_smooth = True
    mt = bpy.data.materials.new(name + '_mat')
    try: mt.use_nodes = True
    except Exception: pass
    nt = mt.node_tree; p = nt.nodes.get('Principled BSDF')
    base = tuple(min(1, c + red * k) for c, k in zip(color, (0.6, 0.0, 0.0)))
    p.inputs['Base Color'].default_value = (*base, 1); p.inputs['Roughness'].default_value = 0.06
    p.inputs['Specular IOR Level'].default_value = 0.6; p.inputs['Coat Weight'].default_value = 0.2
    p.inputs['Subsurface Weight'].default_value = 0.0
    if foam:
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'foam'
        ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.9
        nt.links.new(at.outputs['Fac'], ramp.inputs[0])
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
        mix.inputs[6].default_value = (*base, 1); mix.inputs[7].default_value = (0.75, 0.78, 0.8, 1)
        nt.links.new(ramp.outputs[0], mix.inputs['Factor']); nt.links.new(mix.outputs[2], p.inputs['Base Color'])
        rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs[3].default_value = 0.06; rr.inputs[4].default_value = 0.6
        nt.links.new(ramp.outputs[0], rr.inputs[0]); nt.links.new(rr.outputs[0], p.inputs['Roughness'])
    C.assign(o, mt)
    # horizon continuation plane (same look, flat) so the sea reaches the sky
    far = C.prim('plane', name + '_far', loc=(loc[0], loc[1], loc[2] - 0.15), size=4000)
    hole = far.modifiers.new('hole', 'BOOLEAN') if False else None
    C.assign(far, C.mat(name + '_farmat', base, rough=0.12, spec=0.6, coat=0.2))
    return o

# ------------------------------------------------------------------ terrain
def sand(name='sand', size=120, flat_r=14, amp=0.6, color=(0.55, 0.43, 0.3), loc=(0, 0, 0), seed=3, slope=None):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=160, y_subdivisions=160, size=size, location=loc)
    o = bpy.context.object; o.name = name
    r = C.rng(seed)
    for v in o.data.vertices:
        d = Vector((v.co.x, v.co.y)).length
        k = C.ease(min(1, max(0, (d - flat_r) / (flat_r * 1.5))), 'smooth')
        n = C.noise1(v.co.x * 0.15, seed, 1) * C.noise1(v.co.y * 0.15, seed + 1, 1) + 0.5 * C.noise1(v.co.x * 0.4 + v.co.y * 0.3, seed + 2, 1)
        v.co.z = amp * n * k + (slope(v.co.x, v.co.y) if slope else 0.0)
    for p in o.data.polygons: p.use_smooth = True
    C.assign(o, C.mat(name + '_m', color, rough=0.92, noise=0.35, noise_scale=60))
    return o

def rock(name, loc, size=1.0, seed=0, color=(0.18, 0.16, 0.14), squash=(1, 1, 0.7), sub=3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=size, location=loc)
    o = bpy.context.object; o.name = name; o.scale = squash
    tex = bpy.data.textures.new(name + 't', 'VORONOI'); tex.noise_scale = 0.5 + 0.2 * (seed % 3)
    C.add_mod(o, 'DISPLACE', texture=tex, strength=size * 0.35)
    tex2 = bpy.data.textures.new(name + 't2', 'CLOUDS'); tex2.noise_scale = 0.25
    C.add_mod(o, 'DISPLACE', texture=tex2, strength=size * 0.12)
    o.rotation_euler = (0, 0, seed * 1.3)
    for p in o.data.polygons: p.use_smooth = True
    C.assign(o, C.mat('rockmat' + str(color), color, rough=0.85, noise=0.4, noise_scale=12))
    return o

def cliff(loc=(0, 0, 0), w=14, d=10, h=12, seed=2):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], loc[2] + h / 2))
    o = bpy.context.object; o.name = 'cliff'; o.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    C.add_mod(o, 'BEVEL', width=1.5, segments=4)
    C.add_mod(o, 'SUBSURF', levels=4, render_levels=4)
    tex = bpy.data.textures.new('cliffc', 'CLOUDS'); tex.noise_scale = 3.0; tex.noise_depth = 3
    C.add_mod(o, 'DISPLACE', texture=tex, strength=1.6)
    tex2 = bpy.data.textures.new('cliffs', 'STUCCI'); tex2.noise_scale = 0.8
    C.add_mod(o, 'DISPLACE', texture=tex2, strength=0.3)
    for p in o.data.polygons: p.use_smooth = True
    C.assign(o, C.mat('cliffmat', (0.12, 0.1, 0.09), rough=0.9, noise=0.5, noise_scale=6))
    return o

# ------------------------------------------------------------------ vegetation
def palm(name, loc, h=7.0, lean=(0.15, 0.05), seed=0, fronds=11, scale=1.0):
    r = C.rng(seed); objs = []
    base = Vector(loc); pts = []
    for i in range(16):
        t = i / 15
        pts.append(base + Vector((lean[0] * h * t * t, lean[1] * h * t * t, h * t)))
    trunk = C.tube(name + '_trunk', pts, 0.18 * scale, taper=lambda t: 1.25 - 0.45 * t, res=12)
    tex = bpy.data.textures.new(name + 'tt', 'WOOD'); tex.wood_type = 'RINGS'; tex.noise_scale = 0.05
    C.add_mod(trunk, 'DISPLACE', texture=tex, strength=0.025, direction='NORMAL')
    C.assign(trunk, C.mat('palmtrunk', (0.22, 0.16, 0.1), rough=0.9, noise=0.6, noise_scale=30))
    top = pts[-1]
    leaf = C.mat('palmleaf', (0.08, 0.2, 0.04), rough=0.6, sss=0.15, noise=0.4, noise_scale=25)
    for k in range(fronds):
        az = 2 * math.pi * k / fronds + r.uniform(-0.2, 0.2); el = r.uniform(0.15, 0.6); L = r.uniform(2.6, 3.4) * scale
        objs.append(_frond(name + f'_fr{k}', top, az, el, L, r))
    for k in range(5):  # coconuts
        a = 2 * math.pi * k / 5
        c = C.prim('sphere', 'coco', loc=top + Vector((math.cos(a) * 0.22, math.sin(a) * 0.22, -0.25)), radius=0.14 * scale, segments=16, ring_count=8)
        C.assign(c, C.mat('coconut', (0.25, 0.2, 0.06), rough=0.6)); objs.append(c)
    fr = C.join(objs, name + '_crown')
    for p in fr.data.polygons: p.use_smooth = True
    C.assign(fr, leaf, C.mat('coconut', (0.25, 0.2, 0.06), rough=0.6))
    for p in fr.data.polygons:
        pass
    return trunk, fr, top

def _frond(name, top, az, el, L, r):
    d = Vector((math.cos(az), math.sin(az), 0))
    side = Vector((-d.y, d.x, 0))
    verts, faces = [], []
    n = 14
    spine = []
    for i in range(n + 1):
        t = i / n
        p = top + d * L * t + Vector((0, 0, L * (math.sin(el) * t - 0.55 * t * t)))
        spine.append(p)
    for i, p in enumerate(spine):
        t = i / n
        w = 0.55 * math.sin(math.pi * min(1, t * 1.15)) * (1 - 0.2 * t) * L / 3
        droop = Vector((0, 0, -0.25 * w))
        verts += [p + side * w + droop, p, p - side * w + droop]
    for i in range(n):
        a = i * 3
        faces.append((a, a + 3, a + 4, a + 1)); faces.append((a + 1, a + 4, a + 5, a + 2))
    o = C.mesh_obj(name, verts, faces)
    # cut leaflets: alternate thin slits via a wave displacement in the side direction
    return o

def grass_tufts(center, radius, count, seed=0, color=(0.15, 0.25, 0.06)):
    r = C.rng(seed); objs = []
    for i in range(count):
        a = r.uniform(0, 2 * math.pi); d = radius * math.sqrt(r.random())
        p = Vector(center) + Vector((math.cos(a) * d, math.sin(a) * d, 0))
        for k in range(5):
            b = r.uniform(0, 2 * math.pi); hgt = r.uniform(0.25, 0.6)
            objs.append(C.tube('blade', [p, p + Vector((math.cos(b) * 0.08, math.sin(b) * 0.08, hgt * 0.6)), p + Vector((math.cos(b) * 0.2, math.sin(b) * 0.2, hgt))], 0.012, taper=lambda t: 1 - t, res=4))
    if not objs: return None
    g = C.join(objs, 'grass'); C.assign(g, C.mat('grassm', color, rough=0.7, sss=0.1))
    return g

# ------------------------------------------------------------------ village architecture
def hut(name, loc, r=2.2, h=2.2, roof_h=2.4, rot=0, wall=(0.55, 0.38, 0.24), seed=0, door=True):
    o = []
    w = C.prim('cyl', name + '_wall', loc=(loc[0], loc[1], loc[2] + h / 2), radius=r, depth=h, vertices=40)
    tex = bpy.data.textures.new(name + 'mud', 'CLOUDS'); tex.noise_scale = 0.4
    C.add_mod(w, 'SUBSURF', levels=1, render_levels=1); C.add_mod(w, 'DISPLACE', texture=tex, strength=0.04)
    C.assign(w, C.mat('mudwall', wall, rough=0.95, noise=0.5, noise_scale=8))
    roof = C.prim('cone', name + '_roof', loc=(loc[0], loc[1], loc[2] + h + roof_h / 2 - 0.25), radius1=r * 1.35, radius2=0.05, depth=roof_h, vertices=48)
    C.add_mod(roof, 'SUBSURF', levels=2, render_levels=2, subdivision_type='SIMPLE')
    tex2 = bpy.data.textures.new(name + 'thatch', 'STUCCI'); tex2.noise_scale = 0.08
    C.add_mod(roof, 'DISPLACE', texture=tex2, strength=0.08)
    C.assign(roof, C.mat('thatch', (0.36, 0.27, 0.12), rough=0.95, noise=0.7, noise_scale=40))
    o += [w, roof]
    if door:
        a = math.radians(rot)
        dp = Vector((loc[0] + math.sin(a) * -r * 1.0, loc[1] - math.cos(a) * r * 1.0, loc[2] + 0.85))
        d = C.prim('cube', name + '_door', loc=dp, scale=(0.45, 0.06, 0.85)); d.rotation_euler = (0, 0, a)
        C.assign(d, C.mat('doorway', (0.02, 0.015, 0.01), rough=1.0))
        fr = C.prim('cube', name + '_frame', loc=dp + Vector((0, 0, 0.9)), scale=(0.55, 0.08, 0.06)); fr.rotation_euler = (0, 0, a)
        C.assign(fr, C.mat('wood', (0.2, 0.12, 0.06), rough=0.7, noise=0.4, noise_scale=20))
        o += [d, fr]
    return o

def boat(name, loc=(0, 0, 0), L=6.0, W=1.5, H=0.9, rot=0, color=(0.45, 0.18, 0.08), stripe=(0.85, 0.75, 0.2), deck=True):
    """Fishing boat; returns (hull_obj, deck_height). Local origin at waterline centre; deck at z = deck_h."""
    secs, n = 24, 16
    verts, faces = [], []
    for i in range(secs + 1):
        t = i / secs; x = (t - 0.5) * L
        taper = math.sin(math.pi * (0.04 + 0.92 * t)) ** 0.55
        rise = 0.45 * H * ((2 * t - 1) ** 6)  # prow/stern upswept
        for k in range(n + 1):
            a = math.pi * k / n  # 0..pi : one gunwale -> keel -> other gunwale
            y = math.cos(a) * W / 2 * taper
            z = -math.sin(a) * H * 0.75 * (0.35 + 0.65 * taper) + H * 0.35 + rise
            verts.append((x, y, z))
    for i in range(secs):
        for k in range(n):
            a = i * (n + 1) + k; b = a + n + 1
            faces.append((a, b, b + 1, a + 1))
    hull = C.mesh_obj(name, verts, faces)
    C.add_mod(hull, 'SOLIDIFY', thickness=0.06); C.subsurf(hull, 1)
    m_out = C.mat('hull_' + str(color), color, rough=0.55, noise=0.4, noise_scale=10, coat=0.3)
    C.assign(hull, m_out)
    parts = [hull]
    deck_h = H * 0.12
    if deck:
        d = C.prim('cube', name + '_deck', loc=(0, 0, deck_h - 0.03), scale=(L * 0.42, W * 0.42, 0.03))
        C.assign(d, C.mat('deckwood', (0.32, 0.22, 0.12), rough=0.75, noise=0.5, noise_scale=6)); parts.append(d)
        for sx in (-0.25, 0.1, 0.32):
            b = C.prim('cube', 'bench', loc=(sx * L, 0, deck_h + 0.22), scale=(0.12, W * 0.4, 0.04))
            C.assign(b, C.mat('deckwood', (0.32, 0.22, 0.12), rough=0.75, noise=0.5, noise_scale=6)); parts.append(b)
    # painted stripe along gunwale
    st = C.tube(name + '_stripe', [Vector((((i / 30) - 0.5) * L * 0.95, W / 2 * math.sin(math.pi * (0.04 + 0.92 * i / 30)) ** 0.55 + 0.01, H * 0.33 + 0.45 * H * ((2 * i / 30 - 1) ** 6))) for i in range(31)], 0.035, res=6)
    st2 = C.tube(name + '_stripe2', [Vector((((i / 30) - 0.5) * L * 0.95, -(W / 2 * math.sin(math.pi * (0.04 + 0.92 * i / 30)) ** 0.55 + 0.01), H * 0.33 + 0.45 * H * ((2 * i / 30 - 1) ** 6))) for i in range(31)], 0.035, res=6)
    for s_ in (st, st2): C.assign(s_, C.mat('stripe' + str(stripe), stripe, rough=0.4)); parts.append(s_)
    root = C.empty(name + '_root', loc)
    for p in parts:
        p.parent = root
    root.rotation_euler = (0, 0, math.radians(rot))
    return root, deck_h

def bob(obj, f0, f1, amp=0.06, roll=2.0, pitch=1.2, seed=0, base=None, yaw=None):
    """keyframe gentle floating motion on a boat root."""
    base = Vector(base or obj.location); yaw = obj.rotation_euler.z if yaw is None else yaw
    for f in range(f0, f1 + 1, 2):
        t = f / C.FPS
        obj.location = base + Vector((0, 0, amp * math.sin(t * 1.3 + seed) + amp * 0.4 * math.sin(t * 2.7 + seed * 2)))
        obj.rotation_euler = (math.radians(roll * math.sin(t * 1.1 + seed)), math.radians(pitch * math.sin(t * 0.9 + seed * 3)), yaw)
        obj.keyframe_insert('location', frame=f); obj.keyframe_insert('rotation_euler', frame=f)

def torch_pole(loc, h=2.2, seed=0, f0=1, f1=300, strength=120):
    p = C.tube('torchpole', [Vector(loc), Vector(loc) + Vector((0, 0, h))], 0.03, res=6)
    C.assign(p, C.mat('wood', (0.2, 0.12, 0.06), rough=0.7, noise=0.4, noise_scale=20))
    fl = flame(Vector(loc) + Vector((0, 0, h + 0.12)), 0.12, seed, f0, f1, strength)
    return p, fl

def flame(loc, size=0.12, seed=0, f0=1, f1=300, strength=120):
    f = C.prim('ico', 'flame', loc=loc, subdivisions=3, radius=size); f.scale = (1, 1, 1.8)
    C.assign(f, C.emission_mat('fire', (1.0, 0.45, 0.08), 18))
    f.visible_shadow = False
    lt = light('POINT', 'firelight', loc=Vector(loc) + Vector((0, 0, 0.2)), energy=strength, color=(1, 0.55, 0.2), size=0.15)
    for fr in range(f0, f1 + 1, 2):
        t = fr / C.FPS; n = C.noise1(t, seed, 6.0)
        f.scale = (1 + 0.15 * n, 1 + 0.15 * C.noise1(t, seed + 1, 7), 1.8 + 0.4 * C.noise1(t, seed + 2, 5))
        f.keyframe_insert('scale', frame=fr)
        lt.data.energy = strength * (1 + 0.25 * n); lt.data.keyframe_insert('energy', frame=fr)
    return f, lt

def bunting(p0, p1, n=14, sag=0.35, colors=((0.8, 0.1, 0.1), (0.95, 0.7, 0.1), (0.1, 0.4, 0.8), (0.1, 0.6, 0.2))):
    p0, p1 = Vector(p0), Vector(p1); objs = []
    rope = C.tube('rope', [p0.lerp(p1, i / 20) - Vector((0, 0, sag * math.sin(math.pi * i / 20))) for i in range(21)], 0.008, res=5)
    C.assign(rope, C.mat('rope', (0.5, 0.42, 0.3), rough=0.9)); objs.append(rope)
    d = (p1 - p0).normalized()
    for i in range(1, n):
        t = i / n; c = p0.lerp(p1, t) - Vector((0, 0, sag * math.sin(math.pi * t)))
        v = [c - d * 0.12, c + d * 0.12, c - Vector((0, 0, 0.3))]
        fl = C.mesh_obj('flag', v, [(0, 1, 2)], smooth=False); C.assign(fl, C.mat('flag%d' % (i % 4), colors[i % 4], rough=0.7))
        objs.append(fl)
    return objs

def net_pile(loc, size=1.0):
    o = C.prim('sphere', 'netpile', loc=loc, radius=size, segments=24, ring_count=12); o.scale = (1.3, 1, 0.45)
    tex = bpy.data.textures.new('nett', 'CLOUDS'); tex.noise_scale = 0.2
    C.add_mod(o, 'DISPLACE', texture=tex, strength=0.15)
    m = C.mat('netm', (0.25, 0.35, 0.3), rough=0.9)
    nt = m.node_tree; p = nt.nodes.get('Principled BSDF')
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 30
    wv2 = nt.nodes.new('ShaderNodeTexWave'); wv2.inputs['Scale'].default_value = 30; wv2.bands_direction = 'Y'
    mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MULTIPLY'
    nt.links.new(wv.outputs['Fac'], mx.inputs[0]); nt.links.new(wv2.outputs['Fac'], mx.inputs[1])
    bump = nt.nodes.new('ShaderNodeBump'); nt.links.new(mx.outputs[0], bump.inputs['Height']); nt.links.new(bump.outputs[0], p.inputs['Normal'])
    C.assign(o, m)
    return o

# ------------------------------------------------------------------ props
def blade(name='blade', length=0.75):
    """Devara's broad curved machete. Local origin at the grip centre; blade extends along +Y."""
    pts = []
    n = 16
    verts, faces = [], []
    for i in range(n + 1):
        t = i / n; y = 0.12 + t * length
        w = 0.07 + 0.06 * math.sin(math.pi * t * 0.9) + 0.03 * t  # broadening towards the tip
        curve = 0.08 * t * t
        verts += [(curve - 0.0, y, 0), (curve + w, y, 0)]
    for i in range(n):
        a = 2 * i; faces.append((a, a + 2, a + 3, a + 1))
    b = C.mesh_obj(name + '_steel', verts, faces, smooth=False)
    C.add_mod(b, 'SOLIDIFY', thickness=0.008, offset=0); C.add_mod(b, 'BEVEL', width=0.002, segments=2)
    C.assign(b, C.mat('steel', (0.55, 0.56, 0.58), rough=0.22, metal=1.0, noise=0.25, noise_scale=30))
    h = C.prim('cyl', name + '_grip', loc=(0.03, 0.0, 0), rotation=(math.radians(90), 0, 0), radius=0.021, depth=0.24, vertices=16)
    C.assign(h, C.mat('grip', (0.12, 0.06, 0.03), rough=0.6, noise=0.5, noise_scale=40))
    gd = C.prim('cyl', name + '_guard', loc=(0.05, 0.125, 0), rotation=(math.radians(90), 0, 0), radius=0.045, depth=0.02, vertices=16)
    C.assign(gd, C.mat('brass', (0.6, 0.42, 0.15), rough=0.3, metal=1.0))
    o = C.join([b, h, gd], name)
    return o

def axe(name='axe'):
    """Bhaira's long-handled axe. Origin at the grip; handle along +Y."""
    hnd = C.prim('cyl', name + '_h', loc=(0, 0.35, 0), rotation=(math.radians(90), 0, 0), radius=0.022, depth=1.0, vertices=12)
    C.assign(hnd, C.mat('grip', (0.12, 0.06, 0.03), rough=0.6, noise=0.5, noise_scale=40))
    verts = [(0, 0.72, 0), (0.0, 0.9, 0), (0.26, 0.98, 0), (0.3, 0.8, 0), (0.26, 0.62, 0)]
    hd = C.mesh_obj(name + '_head', verts, [(0, 1, 2, 3, 4)], smooth=False)
    C.add_mod(hd, 'SOLIDIFY', thickness=0.025, offset=0); C.add_mod(hd, 'BEVEL', width=0.004, segments=2)
    C.assign(hd, C.mat('darksteel', (0.25, 0.25, 0.27), rough=0.35, metal=1.0, noise=0.3, noise_scale=25))
    return C.join([hnd, hd], name)

def knife(name='knife'):
    b = C.mesh_obj(name + '_b', [(0, 0.06, 0), (0.025, 0.06, 0), (0.02, 0.24, 0), (0.0, 0.3, 0)], [(0, 1, 2, 3)], smooth=False)
    C.add_mod(b, 'SOLIDIFY', thickness=0.004, offset=0)
    C.assign(b, C.mat('steel', (0.55, 0.56, 0.58), rough=0.22, metal=1.0, noise=0.25, noise_scale=30))
    h = C.prim('cyl', name + '_h', loc=(0.01, 0.0, 0), rotation=(math.radians(90), 0, 0), radius=0.017, depth=0.12, vertices=12)
    C.assign(h, C.mat('grip', (0.12, 0.06, 0.03), rough=0.6, noise=0.5, noise_scale=40))
    return C.join([b, h], name)

def dried_fish(name='fish', L=0.5):
    """The legendary 2 kg dried fish. Origin at centre, length along +Y."""
    def sh(x, y, z):
        t = (y / (L / 2) + 1) / 2  # 0 tail .. 1 head
        w = math.sin(math.pi * min(1, t * 1.05)) ** 0.7
        return x * w * 0.35, y, z * w
    body = C.ellipsoid(name + '_b', L * 0.18, L / 2, L * 0.16, seg=24, rings=16, shape=sh)
    tail = C.mesh_obj(name + '_t', [(0, -L / 2 + 0.02, 0), (0, -L / 2 - 0.1, 0.09), (0, -L / 2 - 0.1, -0.09)], [(0, 1, 2)], smooth=False)
    C.add_mod(tail, 'SOLIDIFY', thickness=0.006)
    eye = C.prim('sphere', name + '_e', loc=(0.03, L / 2 - 0.07, 0.025), radius=0.013, segments=10, ring_count=6)
    eye2 = C.prim('sphere', name + '_e2', loc=(-0.03, L / 2 - 0.07, 0.025), radius=0.013, segments=10, ring_count=6)
    fm = C.mat('dryfish', (0.45, 0.36, 0.22), rough=0.55, noise=0.6, noise_scale=25, coat=0.3)
    C.assign(body, fm); C.assign(tail, fm); C.assign(eye, C.mat('fisheye', (0.02, 0.02, 0.02), rough=0.1)); C.assign(eye2, C.mat('fisheye', (0.02, 0.02, 0.02), rough=0.1))
    return C.join([body, tail, eye, eye2], name)

def basket(name='basket', r=0.28, h=0.22, fish=True):
    b = C.prim('cyl', name, loc=(0, 0, 0), radius=r, depth=h, vertices=32)
    for v in b.data.vertices:
        if v.co.z > 0: v.co.x *= 1.2; v.co.y *= 1.2
    bm = bmesh.new(); bm.from_mesh(b.data)
    top = [f for f in bm.faces if f.normal.z > 0.9]; bmesh.ops.delete(bm, geom=top, context='FACES'); bm.to_mesh(b.data); bm.free()
    C.add_mod(b, 'SOLIDIFY', thickness=0.015)
    m = C.mat('wicker', (0.5, 0.36, 0.18), rough=0.9, noise=0.6, noise_scale=60)
    C.assign(b, m); objs = [b]
    if fish:
        for i in range(5):
            f = dried_fish('bf', 0.32); f.location = (0.1 * math.cos(i * 1.3), 0.1 * math.sin(i * 1.3), h / 2 - 0.02); f.rotation_euler = (0.3, 0.2 * i, i * 1.2)
            objs.append(f)
    return C.join(objs, name)

def tea_glass(name='glass'):
    g = C.prim('cyl', name, radius=0.032, depth=0.1, vertices=16)
    for v in g.data.vertices:
        if v.co.z > 0: v.co.x *= 1.18; v.co.y *= 1.18
    tea = C.prim('cyl', name + '_tea', loc=(0, 0, -0.012), radius=0.03, depth=0.07, vertices=16)
    C.assign(g, C.mat('glassm', (0.8, 0.85, 0.85), rough=0.05, alpha=0.35, spec=0.8))
    C.assign(tea, C.mat('tea', (0.35, 0.18, 0.06), rough=0.15, sss=0.3))
    return C.join([g, tea], name)

def coconut(name='coco'):
    c = C.prim('sphere', name, radius=0.13, segments=20, ring_count=10); c.scale = (1, 1, 1.12)
    C.assign(c, C.mat('coconutgreen', (0.25, 0.32, 0.06), rough=0.5, noise=0.3, noise_scale=8))
    return c

def log(name='log', L=2.2, r=0.17):
    l = C.prim('cyl', name, rotation=(0, math.radians(90), 0), radius=r, depth=L, vertices=20)
    tex = bpy.data.textures.new('bark', 'STUCCI'); tex.noise_scale = 0.05
    C.add_mod(l, 'SUBSURF', levels=1, render_levels=1, subdivision_type='SIMPLE'); C.add_mod(l, 'DISPLACE', texture=tex, strength=0.015)
    C.assign(l, C.mat('bark', (0.22, 0.15, 0.08), rough=0.9, noise=0.5, noise_scale=20))
    bpy.ops.object.select_all(action='DESELECT'); l.select_set(True); bpy.context.view_layer.objects.active = l
    bpy.ops.object.transform_apply(rotation=True)
    return l

def poster(name, image_path, w=0.42, h=0.6):
    p = C.prim('plane', name, size=1); p.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    m = bpy.data.materials.new(name + 'm')
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree; pr = nt.nodes.get('Principled BSDF')
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(image_path)
    nt.links.new(tx.outputs['Color'], pr.inputs['Base Color']); pr.inputs['Roughness'].default_value = 0.5
    nt.links.new(tx.outputs['Color'], pr.inputs['Emission Color']); pr.inputs['Emission Strength'].default_value = 0.25
    C.assign(p, m)
    return p

def lantern(loc, strength=60, seed=0, f0=1, f1=300):
    body = C.prim('cyl', 'lantern', loc=loc, radius=0.07, depth=0.16, vertices=16)
    C.assign(body, C.mat('lanternglass', (1.0, 0.7, 0.35), rough=0.2, emit=(1.0, 0.6, 0.25), emit_str=8))
    cap = C.prim('cone', 'lancap', loc=Vector(loc) + Vector((0, 0, 0.11)), radius1=0.085, radius2=0.02, depth=0.07, vertices=16)
    base = C.prim('cyl', 'lanbase', loc=Vector(loc) - Vector((0, 0, 0.09)), radius=0.08, depth=0.025, vertices=16)
    hk = C.prim('torus', 'lanhook', loc=Vector(loc) + Vector((0, 0, 0.17)), major_radius=0.03, minor_radius=0.005, rotation=(math.radians(90), 0, 0))
    for o in (cap, base, hk): C.assign(o, C.mat('tin', (0.25, 0.22, 0.18), rough=0.4, metal=0.8))
    lt = light('POINT', 'lanternlight', loc=loc, energy=strength, color=(1.0, 0.62, 0.3), size=0.05)
    for fr in range(f0, f1 + 1, 2):
        t = fr / C.FPS
        lt.data.energy = strength * (1 + 0.08 * C.noise1(t, seed, 5) + 0.05 * C.noise1(t, seed + 3, 13)); lt.data.keyframe_insert('energy', frame=fr)
    return lt

def shark(name='sundaram', L=3.2):
    """Friendly cartoon shark. Origin at body centre; faces -Y. Returns (root, jaw)."""
    def sh(x, y, z):
        t = (-y / (L / 2) + 1) / 2  # 0 tail .. 1 nose
        w = (math.sin(math.pi * min(1, 0.08 + t * 0.95)) ** 0.8)
        zz = z * w * (1.0 if z > 0 else 0.85)
        return x * w, y, zz
    body = C.ellipsoid(name + '_body', L * 0.17, L / 2, L * 0.16, seg=40, rings=24, shape=sh)
    belly = C.mat('sharkbelly', (0.78, 0.78, 0.76), rough=0.4)
    top = C.mat('sharktop', (0.22, 0.30, 0.38), rough=0.35, coat=0.4, noise=0.2, noise_scale=10)
    C.assign(body, top, belly)
    for p in body.data.polygons: p.material_index = 1 if p.center.z < -L * 0.03 else 0
    fin = C.mesh_obj(name + '_dorsal', [(0, 0.1, L * 0.13), (0, 0.55, L * 0.13), (0, 0.55 + 0.25, L * 0.36), ], [(0, 1, 2)], smooth=False)
    C.add_mod(fin, 'SOLIDIFY', thickness=0.05); C.add_mod(fin, 'BEVEL', width=0.015, segments=2); C.assign(fin, top)
    tail1 = C.mesh_obj(name + '_tail', [(0, L / 2 - 0.15, 0), (0, L / 2 + 0.45, L * 0.2), (0, L / 2 + 0.25, 0), (0, L / 2 + 0.4, -L * 0.12)], [(0, 1, 2), (0, 2, 3)], smooth=False)
    C.add_mod(tail1, 'SOLIDIFY', thickness=0.05); C.assign(tail1, top)
    pecs = []
    for sx in (1, -1):
        pf = C.mesh_obj(name + '_pec', [(sx * L * 0.12, -0.25, -L * 0.07), (sx * L * 0.42, 0.15, -L * 0.17), (sx * L * 0.12, 0.15, -L * 0.07)], [(0, 1, 2)], smooth=False)
        C.add_mod(pf, 'SOLIDIFY', thickness=0.04); C.assign(pf, top); pecs.append(pf)
        e = C.prim('sphere', 'sheye', loc=(sx * L * 0.105, -L * 0.34, L * 0.045), radius=0.07, segments=16, ring_count=8)
        C.assign(e, C.mat('sharkeye', (0.9, 0.9, 0.88), rough=0.2))
        pu = C.prim('sphere', 'shpupil', loc=(sx * L * 0.13, -L * 0.36, L * 0.05), radius=0.035, segments=12, ring_count=6)
        C.assign(pu, C.mat('pupil', (0.004, 0.004, 0.004), rough=0.1, coat=1.0)); pecs += [e, pu]
    mouth = C.ellipsoid(name + '_mouth', L * 0.1, L * 0.05, L * 0.025, loc=(0, -L * 0.43, -L * 0.04))
    C.assign(mouth, C.mat('mouth_in', (0.09, 0.012, 0.015), rough=0.6))
    teeth = []
    for k in range(9):
        x = (k / 8 - 0.5) * L * 0.17
        tt = C.prim('cone', 'tooth', loc=(x, -L * 0.455 + abs(x) * 0.3, -L * 0.025), radius1=0.025, depth=0.06, rotation=(math.radians(180), 0, 0), vertices=6)
        C.assign(tt, C.mat('teeth', (0.95, 0.94, 0.9), rough=0.3)); teeth.append(tt)
    sh_ = C.join([body, fin, tail1, *pecs, mouth, *teeth], name)
    for p in sh_.data.polygons: p.use_smooth = True
    root = C.empty(name + '_root'); sh_.parent = root
    return root, sh_

def wig_from(ch, name='wig'):
    """Duplicate Devara-style hair + beard meshes as a detachable disguise for another character."""
    return None

def title_image(path_png, text, sub='', w=1920, h=1080, color='#e8c27a', bg='transparent', size=260, font='Gautami'):
    """Render Telugu text with headless Chrome (proper complex-script shaping)."""
    import os, subprocess, tempfile
    html = f"""<html><head><meta charset='utf-8'><style>
    html,body{{margin:0;width:{w}px;height:{h}px;background:{bg};display:flex;align-items:center;justify-content:center;flex-direction:column}}
    .t{{font-family:'Nirmala UI','{font}',sans-serif;font-weight:700;font-size:{size}px;color:{color};letter-spacing:6px;
        text-shadow:0 0 30px rgba(255,80,20,.55),0 8px 0 #5a0d06,0 14px 30px #000}}
    .s{{font-family:'Nirmala UI','{font}',sans-serif;font-size:{int(size*0.24)}px;color:#f3e6c8;margin-top:10px;letter-spacing:8px;text-shadow:0 4px 12px #000}}
    </style></head><body><div class='t'>{text}</div><div class='s'>{sub}</div></body></html>"""
    tmp = os.path.join(tempfile.gettempdir(), 'title_tmp.html'); open(tmp, 'w', encoding='utf-8').write(html)
    chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--default-background-color=00000000',
                    f'--window-size={w},{h}', f'--screenshot={path_png}', 'file:///' + tmp.replace('\\', '/')], check=True, capture_output=True)
    return path_png

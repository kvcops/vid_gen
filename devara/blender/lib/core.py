"""Scene, material, mesh and keyframe helpers shared by every shot."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Quaternion, Euler

FPS = 24

# ---------------------------------------------------------------- scene
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    return sc

def setup_render(sc, preset='final'):
    r = sc.render
    r.engine = 'BLENDER_EEVEE'
    if preset == 'final':
        r.resolution_x, r.resolution_y, r.resolution_percentage = 1920, 1080, 100
        sc.eevee.taa_render_samples = 16
    elif preset == 'preview':
        r.resolution_x, r.resolution_y, r.resolution_percentage = 960, 540, 100
        sc.eevee.taa_render_samples = 8
    else:  # 'still' for QA contact sheets
        r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 720, 100
        sc.eevee.taa_render_samples = 16
    e = sc.eevee
    e.use_shadows = True
    e.shadow_ray_count = 1
    e.shadow_step_count = 6
    e.use_raytracing = True
    e.ray_tracing_method = 'SCREEN'
    e.use_fast_gi = True
    e.volumetric_tile_size = '8'
    e.volumetric_samples = 32
    r.use_motion_blur = True
    r.motion_blur_shutter = 0.45
    vs = sc.view_settings
    vs.view_transform = 'AgX'
    try: vs.look = 'AgX - Medium High Contrast'
    except Exception: pass
    r.film_transparent = False
    r.image_settings.file_format = 'JPEG'
    r.image_settings.quality = 94
    _compositor_glow(sc)

def _compositor_glow(sc):
    """Bloom + subtle lens vignette through the compositor (EEVEE Next has no built-in bloom)."""
    try:
        sc.use_nodes = True
        tree = sc.node_tree
    except Exception:
        tree = None
    if tree is None:  # Blender 5.x: compositing node group
        ng = bpy.data.node_groups.new('Comp', 'CompositorNodeTree')
        sc.compositing_node_group = ng
        tree = ng
        out = tree.nodes.new('NodeGroupOutput')
        tree.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    else:
        for n in list(tree.nodes): tree.nodes.remove(n)
        out = tree.nodes.new('CompositorNodeComposite')
    rl = tree.nodes.new('CompositorNodeRLayers')
    glare = tree.nodes.new('CompositorNodeGlare')
    for k, v in (('glare_type', 'BLOOM'), ('quality', 'MEDIUM'), ('threshold', 0.9), ('size', 7), ('mix', -0.82)):
        try: setattr(glare, k, v)
        except Exception: pass
    for k, v in (('Threshold', 0.9), ('Strength', 0.35), ('Size', 0.6)):
        try: glare.inputs[k].default_value = v
        except Exception: pass
    try: glare.inputs['Type'].default_value = 'Bloom'
    except Exception: pass
    tree.links.new(rl.outputs['Image'], glare.inputs['Image'])
    tree.links.new(glare.outputs['Image'], out.inputs[0])

def world_color(sc, top, bottom=None, strength=1.0):
    w = bpy.data.worlds.new('World'); sc.world = w
    nt = w.node_tree if w.node_tree else None
    if nt is None:
        w.use_nodes = True; nt = w.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs[1].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs['Surface'])
    if bottom is None:
        bg.inputs[0].default_value = (*top, 1)
    else:
        tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs[1].default_value = -0.1; mr.inputs[2].default_value = 0.6
        nt.links.new(tc.outputs['Normal'], sep.inputs[0])
        nt.links.new(sep.outputs['Z'], mr.inputs[0]); nt.links.new(mr.outputs[0], ramp.inputs[0])
        ramp.color_ramp.elements[0].color = (*bottom, 1); ramp.color_ramp.elements[1].color = (*top, 1)
        nt.links.new(ramp.outputs[0], bg.inputs[0])
    return w, nt, bg, out

# ---------------------------------------------------------------- materials
_mat_cache = {}
def mat(name, color, rough=0.6, metal=0.0, sss=0.0, emit=None, emit_str=1.0, spec=0.5, alpha=1.0,
        noise=0.0, noise_scale=40.0, coat=0.0, sheen=0.0):
    """Principled material. `noise` adds subtle albedo variation so surfaces never look flat CG."""
    key = (name, tuple(color), rough, metal, sss, emit, noise)
    if key in _mat_cache: return _mat_cache[key]
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    p.inputs['Specular IOR Level'].default_value = spec
    if sss:
        p.inputs['Subsurface Weight'].default_value = sss
        p.inputs['Subsurface Radius'].default_value = (0.9, 0.35, 0.2)
        p.inputs['Subsurface Scale'].default_value = 0.012
    if coat: p.inputs['Coat Weight'].default_value = coat
    if sheen: p.inputs['Sheen Weight'].default_value = sheen
    if emit is not None:
        p.inputs['Emission Color'].default_value = (*emit, 1)
        p.inputs['Emission Strength'].default_value = emit_str
    if alpha < 1:
        p.inputs['Alpha'].default_value = alpha
    if noise:
        tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = noise_scale
        tex.inputs['Detail'].default_value = 6
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = noise
        mix.inputs[6].default_value = (*color, 1)
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.3; ramp.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1)
        ramp.color_ramp.elements[1].position = 0.7; ramp.color_ramp.elements[1].color = (1.1, 1.1, 1.1, 1)
        nt.links.new(tex.outputs['Fac'], ramp.inputs[0]); nt.links.new(ramp.outputs[0], mix.inputs[7])
        nt.links.new(mix.outputs[2], p.inputs['Base Color'])
        bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.15 * noise / 0.3
        nt.links.new(tex.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs[0], p.inputs['Normal'])
    _mat_cache[key] = m
    return m

def emission_mat(name, color, strength=5.0):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m

def assign(obj, *mats):
    obj.data.materials.clear()
    for m in mats: obj.data.materials.append(m)
    return obj

# ---------------------------------------------------------------- objects
def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj

def mesh_obj(name, verts, faces, smooth=True, coll=None):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    o = bpy.data.objects.new(name, me); link(o, coll)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return o

def ellipsoid(name, rx, ry, rz, loc=(0, 0, 0), seg=32, rings=16, shape=None, coll=None):
    """UV ellipsoid; `shape(x,y,z)->(x,y,z)` lets callers sculpt (jaw taper etc.)."""
    verts, faces = [], []
    for i in range(rings + 1):
        th = math.pi * i / rings
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            x = rx * math.sin(th) * math.cos(ph); y = ry * math.sin(th) * math.sin(ph); z = rz * math.cos(th)
            if shape: x, y, z = shape(x, y, z)
            verts.append((x + loc[0], y + loc[1], z + loc[2]))
    for i in range(rings):
        for j in range(seg):
            a = i * seg + j; b = i * seg + (j + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    o = mesh_obj(name, verts, faces, coll=coll)
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth = True
    return o

def prim(kind, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), smooth=True, **kw):
    fn = {'cube': bpy.ops.mesh.primitive_cube_add, 'cyl': bpy.ops.mesh.primitive_cylinder_add,
          'cone': bpy.ops.mesh.primitive_cone_add, 'sphere': bpy.ops.mesh.primitive_uv_sphere_add,
          'ico': bpy.ops.mesh.primitive_ico_sphere_add, 'plane': bpy.ops.mesh.primitive_plane_add,
          'torus': bpy.ops.mesh.primitive_torus_add}[kind]
    rot = kw.pop('rotation', rot)
    fn(location=loc, rotation=rot, **kw)
    o = bpy.context.object; o.name = name; o.scale = scale
    if smooth and kind not in ('cube', 'plane'):
        for p in o.data.polygons: p.use_smooth = True
    return o

def tube(name, pts, radius, taper=None, res=10, coll=None, closed=False, smooth=True):
    """Tube mesh along polyline pts with radius(t) (t in 0..1)."""
    pts = [Vector(p) for p in pts]; n = len(pts)
    verts, faces = [], []
    prev_n = None
    for i, p in enumerate(pts):
        t = i / (n - 1)
        d = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
        nx = d.cross(up).normalized() if prev_n is None else (prev_n - d * prev_n.dot(d)).normalized()
        prev_n = nx; ny = d.cross(nx)
        r = radius * (taper(t) if taper else 1.0)
        for k in range(res):
            a = 2 * math.pi * k / res
            verts.append(p + (nx * math.cos(a) + ny * math.sin(a)) * r)
    for i in range(n - 1):
        for k in range(res):
            a = i * res + k; b = i * res + (k + 1) % res
            faces.append((a, b, b + res, a + res))
    verts.append(pts[0]); verts.append(pts[-1]); c0, c1 = len(verts) - 2, len(verts) - 1
    for k in range(res):
        faces.append((c0, (k + 1) % res, k)); faces.append((c1, (n - 1) * res + k, (n - 1) * res + (k + 1) % res))
    return mesh_obj(name, verts, faces, smooth=smooth, coll=coll)

def add_mod(o, kind, **kw):
    m = o.modifiers.new(kind.lower(), kind)
    for k, v in kw.items(): setattr(m, k, v)
    return m

def subsurf(o, lv=2):
    return add_mod(o, 'SUBSURF', levels=lv, render_levels=lv)

def apply_mods(o):
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(oe)
    o.modifiers.clear(); old = o.data; o.data = me
    bpy.data.meshes.remove(old)
    return o

def join(objs, name):
    objs = [o for o in objs if o]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); o = bpy.context.object; o.name = name
    return o

def parent_keep(child, parent, bone=None):
    """Parent while keeping current world transform (works for bone parents in rest pose)."""
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    if bone:
        child.parent_type = 'BONE'; child.parent_bone = bone
    bpy.context.view_layer.update()
    child.matrix_world = mw
    return child

def empty(name, loc=(0, 0, 0), coll=None):
    e = bpy.data.objects.new(name, None); e.location = loc; link(e, coll)
    return e

# ---------------------------------------------------------------- keys / timing
def key(obj, path, frame, value=None, index=-1, interp=None):
    if value is not None:
        if index >= 0: getattr(obj, path)[index] = value
        else: setattr(obj, path, value)
    obj.keyframe_insert(path, frame=frame, index=index)
    if interp: set_interp(obj, interp)

def set_interp(id_, interp='LINEAR'):
    ad = id_.animation_data
    if not ad or not ad.action: return
    for fc in _fcurves(ad.action):
        for kp in fc.keyframe_points: kp.interpolation = interp

def _fcurves(action):
    if hasattr(action, 'fcurves') and action.fcurves is not None:
        try: return list(action.fcurves)
        except Exception: pass
    out = []  # Blender 5 layered actions
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags: out.extend(bag.fcurves)
    return out

def all_linear(obj):
    set_interp(obj, 'LINEAR')

def ease(t, kind='inout'):
    t = max(0.0, min(1.0, t))
    if kind == 'in': return t * t * t
    if kind == 'out': return 1 - (1 - t) ** 3
    if kind == 'back':  # overshoot settle
        c = 1.70158; t -= 1; return 1 + (c + 1) * t ** 3 + c * t ** 2
    if kind == 'elastic':
        return 1 - math.exp(-6 * t) * math.cos(t * 12) if t < 1 else 1
    return t * t * (3 - 2 * t) if kind == 'smooth' else (4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2)

def lerp(a, b, t):
    if isinstance(a, (tuple, list, Vector)):
        return Vector(a).lerp(Vector(b), t)
    return a + (b - a) * t

def seg(t, t0, t1, kind='inout'):
    """eased 0..1 progress of t over [t0,t1]."""
    if t1 <= t0: return 1.0 if t >= t1 else 0.0
    return ease((t - t0) / (t1 - t0), kind)

def tracks(t, pts, kind='inout'):
    """piecewise eased interpolation through [(time, value), ...]."""
    if t <= pts[0][0]: return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t <= t1: return lerp(v0, v1, seg(t, t0, t1, kind))
    return pts[-1][1]

def rng(seed):
    return random.Random(seed)

def noise1(t, seed=0, freq=1.0):
    """smooth deterministic 1D value noise in [-1,1]."""
    x = t * freq + seed * 17.13; i = math.floor(x); f = x - i
    def h(n): return (math.sin(n * 127.1 + seed * 311.7) * 43758.5453) % 1.0 * 2 - 1
    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u

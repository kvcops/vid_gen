"""Helpers shared by all shot files."""
import bpy, math
from mathutils import Vector, Matrix, Euler, Quaternion
from lib import core as C
from lib import acting as A
from lib import sets as S
from lib import envs as E
from lib.chars import Character
from lib.shot import Cam, standing, talk_arms

V = lambda *a: Vector(a)
FPS = C.FPS

def fwd(yaw):
    """unit vector the character faces for a given yaw (deg)."""
    r = math.radians(yaw); return Vector((math.sin(r), -math.cos(r), 0))

def right_of(yaw):
    r = math.radians(yaw); return Vector((-math.cos(r), -math.sin(r), 0))  # character's right side

def make(key, ctx, seed=1, name=None, variant=None, parent=None):
    ch = Character(key, name=name, variant=variant)
    a = A.Actor(ch, seed=seed)
    if parent is not None:
        ch.arm.parent = parent
    return ch, a

def head_z(ch, ground=0.0, hip_dz=0.0):
    return ground + ch.hc.z + hip_dz

def sit_fn(actor, loc, yaw, seat_h, armL='table', armR='table', look=None, gest=None, hand='R', lean=8, extra=None, expr=None, fist=(False, False)):
    """seated pose on a stool: hips lowered onto the seat, feet planted forward on the floor."""
    loc = Vector((loc[0], loc[1], 0.0)); H = actor.H; J = actor.ch.J   # root on the floor
    dz = (seat_h + 0.075) - J['hip.L'].z
    fw = fwd(yaw)
    def feet():
        out = {}
        for sd, sg in (('L', 1), ('R', -1)):
            side = right_of(yaw) * (-sg) * abs(J['an.L'].x) * 1.25
            p = loc + fw * (0.27 * H) + side; p.z = J['an.L'].z
            out[sd] = (p, yaw + sg * 6, 0)
        return out
    base = standing(actor, loc, yaw, armL, armR, look=look, gest=gest, hand=hand, torso=(lean, 0, 0), expr=expr, fist=fist, extra=extra)
    def fn(t):
        P = base(t)
        P['hip'] = Vector((0, 0.035 * H, dz)) + A.breathe(t, H, actor.seed)
        P['feet'] = feet()
        return P
    fn.seated_head_z = J['neck1'].z + dz + actor.ch.hc.z - J['neck1'].z
    return fn

def grip(rot=(0, 0, 0), off=(0, 0, 0)):
    """local matrix of a prop in the hand-bone frame (bone Y = finger direction)."""
    return Matrix.Translation(Vector(off)) @ Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()

# a fist grip: prop +Y axis (handle->tip) goes out of the thumb side, centred in the palm
FIST = grip((0, 0, 90), (0.0, 0.055, 0.0))
FIST_L = grip((0, 0, -90), (0.0, 0.055, 0.0))
PALM_CUP = grip((90, 0, 0), (0.0, 0.07, 0.03))

def key_obj(obj, f, loc=None, rot=None, scale=None):
    if loc is not None: obj.location = loc; obj.keyframe_insert('location', frame=f)
    if rot is not None: obj.rotation_euler = rot; obj.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: obj.scale = scale; obj.keyframe_insert('scale', frame=f)

def anim_obj(ctx, obj, fn, step=1):
    """fn(t) -> (loc, rot) ; keys every frame."""
    for f in range(1, ctx.N + 1, step):
        t = (f - 1) / FPS; r = fn(t)
        if r is None: continue
        loc, rot = r[0], r[1]
        if loc is not None: obj.location = loc; obj.keyframe_insert('location', frame=f)
        if rot is not None: obj.rotation_euler = rot; obj.keyframe_insert('rotation_euler', frame=f)
        if len(r) > 2 and r[2] is not None: obj.scale = r[2]; obj.keyframe_insert('scale', frame=f)

def splash(ctx, loc, t0, size=1.0, count=160, name='splash'):
    """deterministic spray burst: particle system of small white spheres."""
    em = C.prim('ico', name, loc=loc, radius=0.3 * size, subdivisions=1)
    ps = em.modifiers.new('sp', 'PARTICLE_SYSTEM').particle_system; st = ps.settings
    f0 = int(t0 * FPS) + 1
    st.count = count; st.frame_start = f0; st.frame_end = f0 + 3; st.lifetime = 34
    st.normal_factor = 5.5 * size; st.factor_random = 2.5 * size; st.effector_weights.gravity = 1.0
    st.render_type = 'OBJECT'
    drop = C.prim('ico', name + '_drop', loc=(0, 0, -200), radius=0.05 * size, subdivisions=1)
    C.assign(drop, C.mat('spray', (0.85, 0.9, 0.95), rough=0.15, alpha=0.8, emit=(0.15, 0.18, 0.22), emit_str=0.5))
    st.instance_object = drop; st.particle_size = 1; st.size_random = 0.7
    ps.seed = len(name) * 7 + f0
    em.show_instancer_for_render = False
    return em

def stars_ring(ctx, center_fn, t0, t1, n=5, r=0.22, name='dizzy'):
    """cartoon dizzy stars circling a head between t0 and t1."""
    stars = []
    for i in range(n):
        st = C.prim('ico', f'{name}{i}', radius=0.035, subdivisions=1); st.scale = (1, 1, 0.4)
        C.assign(st, C.emission_mat('starm', (1.0, 0.85, 0.2), 6)); stars.append(st)
    for f in range(1, ctx.N + 1):
        t = (f - 1) / FPS
        on = t0 <= t <= t1
        for i, st in enumerate(stars):
            a = t * 5 + i * 2 * math.pi / n
            c = center_fn(t)
            st.location = c + Vector((math.cos(a) * r, math.sin(a) * r, 0.05 * math.sin(a * 2))) if on else Vector((0, 0, -100))
            st.keyframe_insert('location', frame=f)
    return stars

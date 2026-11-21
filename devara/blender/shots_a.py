"""ACT 1 — prologue storm, title, 1996 hut framing (s01-s09)."""
from shots_common import *

# ============================================================ STORM
def _devara_on_ledge(ctx, env, pose_kind='stand', blade=True, eyes_open_at=None, look_up_at=None):
    ch, a = make('devara', ctx, seed=3)
    E.wind_hair(ch, ctx, strength=0.05, speed=2.0)
    L = env['ledge']; yaw = 0  # facing the sea (-Y), towards camera side
    bl = None
    if blade:
        bl = S.blade('devara_blade'); a.hold(bl, lambda t: ('hand.R', FIST))
    def hd(t):
        if look_up_at is not None:
            k = C.seg(t, look_up_at, look_up_at + 0.8)
            return (14 * (1 - k) - 4 * k, 0, 0)
        return (6, 0, 0)
    def lid_fn(t, P):
        if eyes_open_at is not None:
            P['lid'] = 0.0 if t < eyes_open_at else min(0.85, (t - eyes_open_at) / 0.12 * 0.85)
    fn = standing(a, L, yaw, armL='down', armR='hold_side', gest=False, head=hd, torso=(-3, 0, 0), expr='fierce', fist=(True, True), stance=1.25, extra=lid_fn)
    a.bake(1, ctx.N, fn)
    return ch, a

def s01(ctx):
    env = E.storm(ctx)
    E.lightning(ctx, env['sun'], [0.15, 1.75, 4.6, 6.9], base=0.6, peak=14, world_bg=env['bg'], wbase=0.9, wpeak=6.0)
    _devara_on_ledge(ctx, env)
    Cam(ctx, [(0, V(1.5, -34, 1.4), V(0, 10, 7), 24), (ctx.dur, V(-0.5, -14, 3.2), V(0, 15, 12), 28)], shake=0.08, ease='smooth', fstop=8)

def s02(ctx):
    env = E.storm(ctx)
    tn = ctx.t('name')
    E.lightning(ctx, env['sun'], [0.6, tn - 0.05, tn + 0.9], base=0.6, peak=14, world_bg=env['bg'], wbase=0.9, wpeak=7.0)
    ch, a = _devara_on_ledge(ctx, env, look_up_at=tn - 0.6)
    L = env['ledge']; hz = L.z + ch.hc.z
    Cam(ctx, [(0, V(1.0, 6.5, 3.0), V(0, 15.6, 11), 20),
              (tn - 0.4, V(2.6, 11.4, 12.6), V(0, 15.6, hz - 0.35), 30),
              (ctx.dur, V(2.2, 12.6, 13.6), V(0, 15.6, hz - 0.1), 38)], ease='smooth', shake=0.03, fstop=4)

def s03(ctx):
    env = E.storm(ctx, rain=True)
    E.lightning(ctx, env['sun'], [0.48, 3.1], base=0.6, world_bg=env['bg'], wbase=0.9, wpeak=6.0, peak=16)
    ch, a = _devara_on_ledge(ctx, env, blade=False, eyes_open_at=0.5)
    L = env['ledge']; hz = L.z + ch.hc.z + 0.03
    key = S.light('SPOT', 'eyekey', loc=(1.2, L.y - 2.5, hz + 0.6), rot=(70, 0, 25), energy=180, color=(1.0, 0.55, 0.35), size=0.2, spot=25)
    key.rotation_euler = (V(0, L.y, hz) - key.location).to_track_quat('-Z', 'Y').to_euler()
    Cam(ctx, [(0, V(0.05, L.y - 1.0, hz + 0.02), V(0, L.y, hz - 0.01), 70), (ctx.dur, V(0.02, L.y - 0.85, hz + 0.01), V(0, L.y, hz - 0.01), 78)], shake=0.003, fstop=8.0)

def s04(ctx):
    env = E.storm(ctx, rain=True)
    ts = ctx.t('stab') + 0.45
    E.lightning(ctx, env['sun'], [ts - 0.05, ctx.dur - 1.0], base=0.05, peak=3, world_bg=env['bg'], wbase=1.2, wpeak=9.0)
    env['rim'].data.energy = 20000
    L = env['ledge']
    dv, ad = make('devara', ctx, seed=3); E.wind_hair(dv, ctx, 0.05, 2.0)
    vr, av = make('vara', ctx, seed=5)
    kn = S.knife('vknife'); av.hold(kn, lambda t: ('hand.R', FIST))
    pd = L + V(0.45, 0, 0); pv = L + V(-0.42, 0, 0)
    def dfn(t):
        k = C.seg(t, ts, ts + 0.5, 'out')
        P = standing(ad, pd + V(0.18 * k, 0, 0), -90, armL='relaxed', armR='relaxed', gest=False, expr='shocked' if t > ts else 'fierce')(t)
        P['torso'] = (-16 * k, 0, 0); P['head'] = (-10 * k, 0, 0); P['hip'] = P['hip'] + V(0, 0, -0.04 * k)
        P['armL'] = A.blend_arm(A.arm_pose('relaxed'), A.arm_pose('shock'), k); P['armR'] = A.blend_arm(A.arm_pose('relaxed', True), A.arm_pose('chest', True), k)
        return P
    def vfn(t):
        k = C.seg(t, ts - 0.35, ts, 'in')
        P = standing(av, pv + V(0.12 * k, 0, 0), 90, armL='relaxed', armR='relaxed', gest=False, expr='angry')(t)
        P['armR'] = A.blend_arm(A.arm_pose('hold_side', True), A.arm_pose('stab', True), k); P['fistR'] = True
        P['torso'] = (10 * k, 0, -12 * k)
        return P
    ad.bake(1, ctx.N, dfn); av.bake(1, ctx.N, vfn)
    hz = L.z + 1.25
    Cam(ctx, [(0, V(0.2, L.y - 6.5, L.z + 0.6), V(0, L.y, hz), 40), (ctx.dur, V(0.05, L.y - 5.4, L.z + 0.7), V(0, L.y, hz), 44)], shake=0.02, fstop=5.6)

# ============================================================ TITLE
def s05(ctx):
    p, em = E.title_void(ctx, ctx.asset('title.png'))
    for f in range(1, ctx.N + 1):
        t = (f - 1) / FPS
        k = C.seg(t, 0.25, 0.75, 'back')
        s = 1.9 - 0.9 * k if t > 0.25 else 0.001
        p.scale = (16 * s, 9 * s, 1); p.keyframe_insert('scale', frame=f)
        em.inputs[1].default_value = (0 if t < 0.25 else 1.4 + 3.5 * math.exp(-(t - 0.75) * 6) if t > 0.75 else 1.4 + 3.5 * k); em.inputs[1].keyframe_insert('default_value', frame=f)
    # embers rising
    emi = C.prim('plane', 'emberemit', loc=(0, -1, -6), size=18)
    ps = emi.modifiers.new('emb', 'PARTICLE_SYSTEM').particle_system; st = ps.settings
    st.count = 500; st.frame_start = -60; st.frame_end = ctx.N; st.lifetime = 120; st.normal_factor = 2.2; st.factor_random = 0.6
    st.effector_weights.gravity = -0.05; st.render_type = 'OBJECT'
    ember = C.prim('ico', 'ember', loc=(0, 0, -300), radius=0.04, subdivisions=1); C.assign(ember, C.emission_mat('emberm', (1.0, 0.35, 0.05), 25))
    st.instance_object = ember; st.size_random = 0.8; ps.seed = 3; emi.show_instancer_for_render = False
    glow = S.light('POINT', 'titleglow', loc=(0, 3, 0), energy=4000, color=(1, 0.3, 0.1), size=3)
    Cam(ctx, [(0, V(0, -24, 0.2), V(0, 0, 0), 50), (ctx.dur, V(0, -21.5, 0.1), V(0, 0, 0), 50)], shake=0.0, dof=False)

# ============================================================ HUT (1996)
def _hut_cast(ctx, env):
    sg, a_s = make('singappa', ctx, seed=11)
    dsp, a_d = make('dsp', ctx, seed=13)
    st = env['stools']
    ctx.cast(a_s, 'SINGAPPA'); ctx.cast(a_d, 'DSP')
    return sg, a_s, dsp, a_d, st

def _sip(a, glass, t0, t1, hand='R'):
    """glass travels table -> mouth -> table between t0 and t1."""
    home = glass.location.copy()
    gr = grip((-90, 0, 0), (0.0, 0.075, 0.035)) if hand == 'R' else grip((-90, 0, 0), (0.0, 0.075, 0.035))
    def h(t):
        if t0 + 0.35 <= t <= t1 - 0.35: return ('hand.' + hand, gr)
        return None
    a.hold(glass, h)
    def arm(t):
        k = C.seg(t, t0, t0 + 0.4) * (1 - C.seg(t, t1 - 0.4, t1))
        up = C.seg(t, t0 + 0.4, t0 + 0.8) * (1 - C.seg(t, t1 - 0.8, t1 - 0.4))
        base = A.arm_pose('table', hand == 'R')
        mid = A.arm_pose('glass', hand == 'R'); top = A.arm_pose('drink', hand == 'R')
        return A.blend_arm(A.blend_arm(base, mid, k), top, up)
    return arm, home

def s06(ctx):
    env = E.hut_interior(ctx)
    sg, a_s, dsp, a_d, st = _hut_cast(ctx, env)
    fs = sit_fn(a_s, st['R'], -90, 0.46, armL='table', armR='table', look=V(-1.0, 0, 1.25), expr='wise', gest=False)
    fd = sit_fn(a_d, st['L'], 90, 0.46, armL='table', armR='explain', look=V(1.0, 0, 1.2), gest=['explain', 'palm_out', 'shrug'], hand='R',
                expr=lambda t: 'worried' if t < 7 else 'deadpan')
    a_s.bake(1, ctx.N, fs); a_d.bake(1, ctx.N, fd)
    Cam(ctx, [(0, V(0.3, -3.6, 1.55), V(0, 0.1, 1.05), 30), (ctx.dur, V(0.15, -2.9, 1.45), V(0, 0.1, 1.1), 33)], shake=0.006, fstop=4)

def s07(ctx):
    env = E.hut_interior(ctx)
    sg, a_s, dsp, a_d, st = _hut_cast(ctx, env)
    arm, home = _sip(a_s, env['glasses']['R'], 0.05, 1.35)
    fs = sit_fn(a_s, st['R'], -90, 0.46, armL='table', armR=arm, look=V(-1.0, 0, 1.25), gest=['explain', None], hand='L',
                expr=lambda t: 'closed' if 0.6 < t < 1.1 else ('laugh' if 1.3 < t < 2.0 else 'wise'))
    fd = sit_fn(a_d, st['L'], 90, 0.46, armL='cross', armR='cross_top', look=V(1.0, 0, 1.25), gest=False, expr='deadpan')
    a_s.bake(1, ctx.N, fs); a_d.bake(1, ctx.N, fd)
    hz = 1.3
    Cam(ctx, [(0, V(-0.55, -1.25, 1.42), V(1.0, 0, hz - 0.05), 50), (ctx.dur, V(-0.4, -1.05, 1.4), V(1.0, 0, hz - 0.03), 55)], shake=0.004, fstop=2.8)

def s08(ctx):
    env = E.hut_interior(ctx)
    sg, a_s, dsp, a_d, st = _hut_cast(ctx, env)
    tsh = ctx.t('shock')
    fs = sit_fn(a_s, st['R'], -90, 0.46, armL='table', armR='table', look=V(-1.0, 0, 1.2), gest=['point_up', 'explain'], hand='R',
                lean=8, extra=lambda t, P: P.update(torso=(8 + 14 * C.seg(t, 1.3, 2.0) * (1 - C.seg(t, 10.3, 10.9)), 0, 0)), expr='wise')
    fd = sit_fn(a_d, st['L'], 90, 0.46, armL='table', armR='table', look=V(1.0, 0, 1.25), gest=['palm_out', 'shock'], hand='R',
                expr=lambda t: 'shocked' if tsh - 0.1 < t < tsh + 2.5 else 'worried',
                extra=lambda t, P: P.update(torso=(8 - 14 * C.seg(t, tsh - 0.1, tsh + 0.2) * (1 - C.seg(t, tsh + 2.2, tsh + 3)), 0, 0)))
    a_s.bake(1, ctx.N, fs); a_d.bake(1, ctx.N, fd)
    # lantern swings / flickers harder for drama
    Cam(ctx, [(0, V(0.0, -2.6, 1.3), V(0, 0, 1.18), 38), (tsh - 0.2, V(0.0, -2.1, 1.3), V(0, 0, 1.2), 42),
              (tsh, V(-0.25, -1.15, 1.32), V(-1.0, 0, 1.22), 50), (tsh + 0.9, V(-0.25, -1.15, 1.32), V(-1.0, 0, 1.22), 50), (tsh + 1.3, V(0.15, -1.2, 1.36), V(1.0, 0, 1.26), 50), (ctx.dur, V(0.2, -1.05, 1.36), V(1.0, 0, 1.27), 55)], shake=0.005, fstop=3.2)

def s09(ctx):
    env = E.hut_interior(ctx)
    sg, a_s, dsp, a_d, st = _hut_cast(ctx, env)
    fs = sit_fn(a_s, st['R'], -90, 0.46, armL='table', armR='table', look=V(-1.0, 0, 1.25), gest=['point_up'], hand='R', expr='proud',
                extra=lambda t, P: P.update(head=(8 * math.sin(max(0, t - 2.0) * 6) * (1 - C.seg(t, 2.0, 3.5)), 0, 0)))
    fd = sit_fn(a_d, st['L'], 90, 0.46, armL='table', armR='table', look=V(1.0, 0, 1.25), gest=False, expr='deadpan')
    a_s.bake(1, ctx.N, fs); a_d.bake(1, ctx.N, fd)
    # deadpan close on DSP, then whip to Singappa
    Cam(ctx, [(0, V(0.35, -0.95, 1.32), V(-1.0, 0, 1.24), 55), (1.9, V(0.3, -0.85, 1.32), V(-1.0, 0, 1.24), 58),
              (2.25, V(-0.4, -1.1, 1.38), V(1.0, 0, 1.27), 50), (ctx.dur, V(-0.3, -0.95, 1.36), V(1.0, 0, 1.27), 54)], ease='inout', shake=0.004, fstop=2.8)

"""ACT 3 — night sea climax, Yethi cliffhanger, outro (s21-s35).
Boat-local frames: Vara's boat root at world origin (length along X); Bhaira's boat 'b0' alongside at +2.4 Y.
Characters are parented to boat roots; their coordinates below are boat-local."""
from shots_common import *
from shots_b import make_wig, wear
from shots_a import _hut_cast, _sip

BY = 2.4  # b0 offset from Vara's boat (Y)

def _sea(ctx, ship=False, fog=0.012):
    env = E.night_sea(ctx, fog=fog, ship=ship)
    vb, vdh = env['boats']['vara']; bb, bdh = env['boats']['b0']
    return env, vb, vdh, bb, bdh

def _bhaira(ctx, bb, axe=True):
    bh, ab = make('bhaira', ctx, seed=7, parent=bb); ctx.cast(ab, 'BHAIRA')
    ax = None
    if axe:
        ax = S.axe('bhaira_axe'); ab.hold(ax, lambda t: ('hand.R', FIST))
    return bh, ab, ax

def _goons(ctx, bb, bdh, n=2, kunjara=True):
    out = []
    for i, (key, x) in enumerate((('goon1', 1.7), ('goon2', -1.7))[:n]):
        g, a = make(key, ctx, seed=21 + 2 * i, parent=bb); out.append((g, a, V(x, 0.1, bdh)))
    k = None
    if kunjara:
        kj, ak = make('kunjara', ctx, seed=9, parent=bb); ctx.cast(ak, 'KUNJARA'); k = (kj, ak, V(-0.9, 0.25, bdh))
    return out, k

def _vara(ctx, vb, disguise=True):
    vr, av = make('vara', ctx, seed=5, parent=vb); ctx.cast(av, 'VARA'); ctx.cast(av, 'VARA_FAKE')
    wig = beard = None
    if disguise:
        wig, beard, hcd = make_wig('wig')
    return vr, av, wig, beard

def _idle_goon(a, pos, yaw=0, look=None, expr='fierce', arm=('cross', 'cross_top'), extra=None):
    return standing(a, pos, yaw, armL=arm[0], armR=arm[1], gest=False, look=look, expr=expr, extra=extra)

# ============================================================ s21 establishing
def s21(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    tb = ctx.lines('BHAIRA')[0]['start']
    vr, av, wig, beard = _vara(ctx, vb)
    W = wear(av); av.hold(wig, lambda t: ('head', W)); av.hold(beard, lambda t: ('head', W))
    bl = S.blade('fake_blade'); av.hold(bl, lambda t: ('hand.R', FIST))
    av.bake(1, ctx.N, standing(av, V(0.3, 0, vdh), 180, armL='hip', armR='hold_side', gest=False, fist=(False, True), expr='fierce', look=V(0.3, BY, 1.8), stance=1.3))
    bh, ab, ax = _bhaira(ctx, bb)
    ab.bake(1, ctx.N, standing(ab, V(0.0, 0, bdh), 0, armL='hip', armR='hold_side', gest=['point', 'fist_up'], hand='L', fist=(False, True),
                               expr=lambda t: 'fierce' if t < tb else 'angry', look=V(0.3, -BY, 1.8)))
    gs, k = _goons(ctx, bb, bdh)
    for g, a, p in gs: a.bake(1, ctx.N, _idle_goon(a, p, 0, V(0.3, -BY, 1.6)))
    kj, ak, pk = k; ak.bake(1, ctx.N, _idle_goon(ak, pk, 20, V(0.3, -BY, 1.6), 'smug', ('hip', 'hip')))
    Cam(ctx, [(0, V(14, -22, 9), V(0, 1, 0.8), 26), (tb - 0.5, V(6, -9, 3.2), V(0, 1.2, 1.2), 30),
              (tb + 0.2, V(2.5, -1.2, 1.4), V(0.0, 2.4, 1.75), 40), (ctx.dur, V(2.2, -0.9, 1.35), V(0.0, 2.4, 1.8), 46)], ease='inout', shake=0.01, fstop=4)

# ============================================================ s22 sneeze — the wig flies
def s22(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    tt = ctx.t('tickle'); tsn = ctx.t('sneeze') + 0.75; tw = ctx.t('wigfly')
    vr, av, wig, beard = _vara(ctx, vb)
    W = wear(av)
    av.hold(wig, lambda t: ('head', W) if t < tsn else None); av.hold(beard, lambda t: ('head', W) if t < tsn else None)
    bl = S.blade('fake_blade'); av.hold(bl, lambda t: ('hand.R', FIST))
    def vfn(t):
        P = standing(av, V(0.3, 0, vdh), 180, armL='hip', armR='hold_side', gest=['fist_up'], hand='L', fist=(False, True), look=V(0.3, BY, 1.8),
                     expr=lambda t: 'fierce' if t < tt else ('closed' if t < tsn else ('shocked' if t < tsn + 2 else 'worried')), stance=1.3)(t)
        wind_up = C.seg(t, tt, tsn - 0.05) ; snz = C.seg(t, tsn - 0.05, tsn + 0.08, 'out') * (1 - C.seg(t, tsn + 0.3, tsn + 0.8))
        P['head'] = (P['head'][0] - 22 * wind_up * (1 - snz) + 30 * snz, 0, 0)
        P['torso'] = (P['torso'][0] - 8 * wind_up + 22 * snz, 0, 0)
        P['mouth'] = {'O': 0.8 * wind_up * (1 - snz)}
        if t > tsn + 0.6:
            k = C.seg(t, tsn + 0.6, tsn + 1.0); P['armL'] = A.blend_arm(P['armL'], A.arm_pose('cheek'), k)
        return P
    av.bake(1, ctx.N, vfn)
    sc = ctx.sc; f0 = int(tsn * FPS) + 1; sc.frame_set(f0)
    for o, dx, spin in ((wig, 0.0, 9), (beard, 0.4, -7)):
        p0 = o.matrix_world.translation.copy(); r0 = o.rotation_euler.copy()
        land = V(0.3 + dx, 1.25, -0.05)
        def fly(t, p0=p0, land=land, r0=r0, spin=spin):
            if t < tsn: return None
            u = min(1, (t - tsn) / 1.6)
            p = p0.lerp(land, u) + V(0, 0, 1.4 * math.sin(math.pi * u))
            if u >= 1: p = land + V(0, 0, -0.08 * min(1, (t - tsn - 1.6) * 2))
            return (p, (r0.x + spin * u, r0.y, r0.z + spin * 0.4 * u))
        anim_obj(ctx, o, fly)
    splash(ctx, V(0.35, 1.25, 0.0), tsn + 1.55, 0.6, count=90, name='wigsplash')
    bh, ab, ax = _bhaira(ctx, bb)
    ab.bake(1, ctx.N, standing(ab, V(0.0, 0, bdh), 0, armL='hip', armR='hold_side', gest=False, fist=(False, True), look=V(0.3, -BY, 1.8),
                               expr=lambda t: 'fierce' if t < tsn else 'shocked'))
    Cam(ctx, [(0, V(1.4, -1.6, 0.55), V(0.3, 0, 1.75), 30), (tt, V(1.0, -1.25, 0.95), V(0.3, 0, 1.75), 42),
              (tsn - 0.1, V(0.7, -1.0, 1.55), V(0.3, 0, 1.7), 55), (tsn + 0.15, V(2.2, -1.8, 1.4), V(0.3, 0.5, 1.6), 30),
              (tw + 0.9, V(2.6, -0.8, 1.2), V(0.3, 1.2, 0.4), 30), (ctx.dur, V(1.3, -1.25, 1.6), V(0.3, 0, 1.7), 50)], ease='inout', shake=0.008, fstop=3.2)

# ============================================================ s23 Bhaira laughs
def s23(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    tsh = ctx.t('shock'); tl = ctx.t('laugh'); tv = ctx.lines('VARA')[0]['start']
    vr, av, _, _ = _vara(ctx, vb, disguise=False)
    bl = S.blade('fake_blade'); av.hold(bl, lambda t: ('hand.R', FIST))
    av.bake(1, ctx.N, standing(av, V(0.3, 0, vdh), 180, armL='cheek', armR='hold_side', gest=['shrug'], hand='L', fist=(False, True), look=V(0.0, BY, 1.85),
                               expr=lambda t: 'worried' if t < tv else 'sad'))
    bh, ab, ax = _bhaira(ctx, bb)
    def bfn(t):
        P = standing(ab, V(0.0, 0, bdh), 0, armL='hip', armR='hold_side', gest=['point'], hand='L', fist=(False, True), look=V(0.3, -BY, 1.75),
                     expr=lambda t: 'shocked' if t < tl - 0.2 else ('laugh' if t < tv + 1.0 else 'smug'))(t)
        lk = C.seg(t, tl, tl + 0.3) * (1 - C.seg(t, tv - 0.3, tv + 0.2))
        P['head'] = (P['head'][0] - 22 * lk + 6 * math.sin(t * 18) * lk, 0, 0); P['torso'] = (P['torso'][0] - 10 * lk + 4 * math.sin(t * 18) * lk, 0, 0)
        P['armL'] = A.blend_arm(P['armL'], A.arm_pose('chest'), lk)
        return P
    ab.bake(1, ctx.N, bfn)
    gs, k = _goons(ctx, bb, bdh)
    for i, (g, a, p) in enumerate(gs):
        a.bake(1, ctx.N, _idle_goon(a, p, 0, V(0.3, -BY, 1.6), lambda t: 'laugh' if tl + 0.3 < t < tv + 1.5 else 'fierce',
                                    extra=lambda t, P: P.update(head=(P['head'][0] - 18 * C.seg(t, tl + 0.3, tl + 0.6) * (1 - C.seg(t, tv + 1, tv + 1.5)) + 5 * math.sin(t * 16 + i), 0, 0))))
    kj, ak, pk = k
    ak.bake(1, ctx.N, _idle_goon(ak, pk, 20, V(0.3, -BY, 1.6), lambda t: 'laugh' if t > tl + 0.2 else 'shocked', ('chest', 'point')))
    Cam(ctx, [(0, V(-0.6, -0.3, 1.75), V(0.0, BY, 1.8), 55), (tl - 0.2, V(-0.6, -0.2, 1.75), V(0.0, BY, 1.8), 58),
              (tl + 0.4, V(-3.0, -2.0, 1.9), V(0.0, BY, 1.6), 30), (tv - 0.3, V(-3.0, -2.0, 1.9), V(0.0, BY, 1.6), 30),
              (tv, V(0.8, 1.4, 1.75), V(0.3, 0, 1.7), 55), (ctx.dur, V(0.75, 1.3, 1.75), V(0.3, 0, 1.7), 60)], ease='inout', shake=0.006, fstop=3.2)

# ============================================================ s24 lunge & fight
def s24(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    tl = ctx.t('lunge'); tf = ctx.t('fight')
    vr, av, _, _ = _vara(ctx, vb, disguise=False)
    bh, ab, ax = _bhaira(ctx, bb)
    g1, a1 = make('goon1', ctx, seed=21, parent=bb)
    # Bhaira jumps from his boat onto Vara's: b0-local target = Vara-boat point + (0,-BY)
    land_b = V(-0.6, -BY + 0.1, vdh)
    tj = tl + 1.2
    def bfn(t):
        u = C.seg(t, tj, tj + 0.6)
        p = V(0.0, 0, bdh).lerp(land_b, u) + V(0, 0, 0.7 * math.sin(math.pi * u))
        P = standing(ab, p, 0 if t < tj + 0.6 else 90, armL='hip', armR='hold_side', gest=False, fist=(False, True), look=None, expr='angry')(t)
        # overhead axe swing at tf+0.3, chop at tf+0.75 (misses), recovers, corners Vara
        up = C.seg(t, tj - 0.3, tj) * (1 - C.seg(t, tf + 0.55, tf + 0.75, 'in'))
        dn = C.seg(t, tf + 0.55, tf + 0.75, 'in') * (1 - C.seg(t, tf + 1.6, tf + 2.2))
        P['armR'] = A.blend_arm(A.blend_arm(A.arm_pose('hold_side', True), A.arm_pose('swing_up', True), up), A.arm_pose('swing_dn', True), dn)
        P['armL'] = A.blend_arm(A.blend_arm(A.arm_pose('hip'), A.arm_pose('swing_up'), up), A.arm_pose('swing_dn'), dn)
        P['torso'] = (25 * dn - 8 * up, 0, 0); P['fistL'] = up > 0.3 or dn > 0.3
        adv = C.seg(t, tf + 2.6, tf + 3.8)
        if t > tj + 0.6:
            P['root'] = (land_b + V(1.6 * adv, 0, 0), 90); P['feet'] = A.stand_feet(ab, P['root'][0], 90, 1.3)
        else:
            P['feet'] = None if 0 < u < 1 else P['feet']
        return P
    ab.bake(1, ctx.N, bfn)
    # Vara: dodges sideways from the chop, punches goon1 off the boat, then backs up to the bow
    def vfn(t):
        dodge = C.seg(t, tf + 0.45, tf + 0.7) * (1 - C.seg(t, tf + 1.4, tf + 1.8))
        back = C.seg(t, tf + 2.6, tf + 3.8)
        pos = V(0.3 + 0.0 * dodge, -0.35 * dodge, vdh) + V(1.9 * back, 0, 0)
        P = standing(av, pos, -90 if t > tj else 180, armL='relaxed', armR='relaxed', gest=False, look=None, expr=lambda t: 'scared' if t < tf + 1.6 or t > tf + 2.5 else 'angry')(t)
        P['torso'] = (-15 * dodge, 18 * dodge, 0)
        pu = C.seg(t, tf + 1.7, tf + 1.9, 'out') * (1 - C.seg(t, tf + 2.1, tf + 2.5))
        P['armR'] = A.blend_arm(P['armR'], A.arm_pose('reach', True), pu); P['fistR'] = pu > 0.1
        if t > tf + 2.5:
            k = C.seg(t, tf + 2.5, tf + 2.8); P['armL'] = A.blend_arm(P['armL'], A.arm_pose('palm_out'), k); P['armR'] = A.blend_arm(P['armR'], A.arm_pose('palm_out', True), k)
        return P
    av.bake(1, ctx.N, vfn)
    # goon1 hops over, takes the punch, flies into the sea
    def gfn(t):
        u = C.seg(t, tl + 1.6, tl + 2.1)
        p = V(1.7, 0.1, bdh).lerp(V(1.4, -BY + 0.2, vdh), u) + V(0, 0, 0.6 * math.sin(math.pi * u))
        P = _idle_goon(a1, p, 0 if u < 1 else 180, None, 'angry', ('relaxed', 'relaxed'))(t)
        P['armR'] = A.blend_arm(P['armR'], A.arm_pose('fist_up', True), C.seg(t, tf + 1.0, tf + 1.4))
        hit = tf + 1.85
        if t > hit:
            v = min(1, (t - hit) / 0.9)
            q = V(1.4, -BY + 0.2, vdh).lerp(V(2.8, -BY - 2.2, -1.3), v) + V(0, 0, 1.4 * math.sin(math.pi * v))
            P['root'] = (q, 180 - 200 * v); P['root_rot'] = (70 * v, 0); P['feet'] = None; P['expr'] = 'scared'
            if v >= 1: P['root'] = (V(2.8, -BY - 2.2, -6), 0)
        return P
    a1.bake(1, ctx.N, gfn)
    splash(ctx, V(2.9, -2.3, 0.0), tf + 1.85 + 0.85, 1.0, name='goonsplash')
    Cam(ctx, [(0, V(-2.4, -2.6, 1.6), V(-0.2, 1.4, 1.7), 30), (tj + 0.6, V(-2.6, -2.8, 1.5), V(0.0, 0.5, 1.4), 28),
              (tf + 0.4, V(-1.8, -2.4, 1.3), V(0.0, 0.0, 1.3), 32), (tf + 1.7, V(-0.8, -2.6, 1.3), V(0.8, 0, 1.3), 32),
              (tf + 2.4, V(1.2, -3.5, 1.4), V(1.6, -0.6, 1.0), 26), (ctx.dur, V(0.6, -2.4, 1.2), V(1.6, 0, 1.4), 32)], ease='inout', shake=0.03, fstop=4)

# ============================================================ s25 Devara rises riding Sundaram
def s25(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    tr = ctx.t('rumble'); tb = ctx.t('burst')
    vr, av, _, _ = _vara(ctx, vb, disguise=False)
    av.bake(1, ctx.N, standing(av, V(2.2, 0, vdh), -150, armL='palm_out', armR='palm_out', gest=False, look=V(0, -6, 2.5), expr=lambda t: 'scared' if t < tb else 'shocked'))
    bh, ab, ax = _bhaira(ctx, bb)
    ab.bake(1, ctx.N, standing(ab, V(0.4, -BY, vdh), 90 + 0, armL='hip', armR='hold_side', gest=False, fist=(False, True), look=V(0, -6 - BY, 2.5),
                               expr=lambda t: 'angry' if t < tr + 1 else 'scared', extra=lambda t, P: P.update(root=(P['root'][0], 90 - 120 * C.seg(t, tr + 0.5, tr + 1.4)))))
    root, shark = S.shark('sundaram', 3.4)
    dv, ad = make('devara', ctx, seed=3, parent=root); E.wind_hair(dv, ctx, 0.07, 3.0)
    blade = S.blade('devara_blade'); ad.hold(blade, lambda t: ('hand.R', FIST))
    ad.bake(1, ctx.N, standing(ad, V(0, 0.15, 3.4 * 0.16 - 0.02), 0, armL='fist_up', armR='swing_up', gest=False, fist=(True, True), expr='fierce', stance=1.5,
                               torso=(10, 0, 0), head=(-6, 0, 0)))
    start = V(0.0, -9.0, -3.5); peak = V(0.0, -4.0, 3.6); end = V(-0.8, -1.2, 1.2)
    def sm(t):
        if t < tb: return (start, (math.radians(-70), 0, math.radians(180)))
        u = (t - tb) / (ctx.dur - tb)
        u = C.ease(u, 'out')  # slow-motion feel: fast start, hangs at the top
        p = (start * (1 - u) ** 2 + peak * 2 * u * (1 - u) + end * u * u)
        pitch = -70 + 85 * u
        return (p, (math.radians(pitch), 0, math.radians(180)))
    anim_obj(ctx, root, sm)
    # the rising wave mound
    wv = C.prim('sphere', 'wave', loc=(0, -7.5, -3), radius=3.0, segments=48, ring_count=24); wv.scale = (2.2, 1.0, 1.0)
    tex = bpy.data.textures.new('wavetex', 'CLOUDS'); tex.noise_scale = 0.5; C.add_mod(wv, 'DISPLACE', texture=tex, strength=0.6)
    C.assign(wv, C.mat('wavem', (0.01, 0.04, 0.06), rough=0.05, spec=0.7, coat=0.4))
    anim_obj(ctx, wv, lambda t: (V(0, -7.5, -3.0 + 2.2 * C.seg(t, tr, tb) - 3.5 * C.seg(t, tb + 0.3, tb + 1.5)), None, (2.2, 1.0, 0.6 + 0.6 * C.seg(t, tr, tb))))
    splash(ctx, V(0, -7.5, 0.0), tb, 3.0, count=500, name='bigsplash'); splash(ctx, V(0.5, -6.5, 0.0), tb + 0.15, 2.0, count=300, name='bigsplash2')
    S.light('POINT', 'burstlight', loc=(0, -5, 4), energy=0, color=(0.6, 0.75, 1.0), size=1.0)
    Cam(ctx, [(0, V(3.5, 3.0, 1.6), V(0, -6, 1.0), 28), (tb - 0.2, V(3.0, 2.6, 1.4), V(0, -6, 1.5), 28),
              (tb + 0.6, V(2.4, 1.8, 0.6), V(0, -4.5, 3.2), 24), (ctx.dur, V(2.0, 1.4, 0.8), V(-0.4, -2.5, 3.0), 26)], ease='inout', shake=0.05, fstop=5.6)

# ============================================================ s26 landing + hero line
def _climax_cast(ctx, env, vb, vdh, bb, bdh, devara_pos=V(-0.9, 0, 0), bhaira_on_vara=True):
    dv, ad = make('devara', ctx, seed=3, parent=vb); ctx.cast(ad, 'DEVARA'); E.wind_hair(dv, ctx, 0.03, 1.0)
    blade = S.blade('devara_blade'); ad.hold(blade, lambda t: ('hand.R', FIST))
    vr, av, _, _ = _vara(ctx, vb, disguise=False)
    bh, ab, ax = _bhaira(ctx, bb)
    return dv, ad, vr, av, bh, ab, ax

def s26(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    tla = 0.25; tk = ctx.lines('KUNJARA')[0]['start']; tfa = ctx.t('faint')
    dv, ad, vr, av, bh, ab, ax = _climax_cast(ctx, env, vb, vdh, bb, bdh)
    pd = V(-1.0, 0, vdh); pb = V(0.9, -BY + 0.05, vdh); pv = V(2.3, 0, vdh)
    def dfn(t):
        u = C.seg(t, 0, tla, 'in')
        p = V(-1.6, -1.5, 1.6).lerp(pd, u)
        crouch = C.seg(t, tla, tla + 0.1, 'out') * (1 - C.seg(t, tla + 0.4, tla + 1.0))
        P = standing(ad, p, 90, armL='fist_up', armR='swing_up', gest=['point'], hand='L', fist=(True, True), look=V(0.9, 0, 1.75), expr='fierce', stance=1.4)(t)
        P['hip'] = P['hip'] + V(0, 0, -0.35 * crouch); P['torso'] = (25 * crouch, 0, 0)
        k = C.seg(t, tla + 0.5, tla + 1.2)
        P['armL'] = A.blend_arm(A.arm_pose('fist_up'), A.arm_pose('relaxed'), k); P['armR'] = A.blend_arm(A.arm_pose('swing_up', True), A.arm_pose('hold_side', True), k)
        if u < 1: P['feet'] = None
        return P
    ad.bake(1, ctx.N, dfn)
    ab.bake(1, ctx.N, standing(ab, pb, -90, armL='relaxed', armR='hold_side', gest=False, fist=(False, True), look=V(-1.0, -BY, 1.8), expr='scared',
                               extra=lambda t, P: P.update(torso=(-12, 0, 0))))
    av.bake(1, ctx.N, standing(av, pv, -90, armL='relaxed', armR='relaxed', gest=False, look=V(-1.0, 0, 1.8), expr=lambda t: 'shocked' if t < 4 else 'happy'))
    gs, k = _goons(ctx, bb, bdh, n=1)
    for g, a, p in gs: a.bake(1, ctx.N, _idle_goon(a, p, 0, V(-1.0, -BY, 1.6), 'scared', ('shock', 'shock')))
    kj, ak, pk = k
    def kfn(t):
        P = _idle_goon(ak, pk, -20, V(-1.0, -BY, 1.7), lambda t: 'scared' if t < tfa else 'closed', ('shock', 'shock'))(t)
        P['eyes'] = (0, 0)
        if t > tfa:  # faints straight backwards
            u = min(1, (t - tfa) / 0.6) ** 2
            P['root_rot'] = (90 * u, 0); P['root'] = (pk + V(0, 0, 0.12 * u), -20); P['feet'] = None
        return P
    ak.bake(1, ctx.N, kfn)
    # deck shake on landing
    for f in range(1, int((tla + 0.8) * FPS)):
        t = (f - 1) / FPS
        if t > tla:
            d = math.exp(-(t - tla) * 7) * math.sin((t - tla) * 40) * 0.06
            vb.delta_location = (0, 0, d); vb.keyframe_insert('delta_location', frame=f)
    vb.delta_location = (0, 0, 0); vb.keyframe_insert('delta_location', frame=int((tla + 0.8) * FPS))
    splash(ctx, V(-1.0, 0, 0.2), tla, 1.4, count=250, name='landsplash')
    Cam(ctx, [(0, V(-3.4, -3.2, 0.5), V(-1.0, 0, 1.0), 24), (tla + 0.5, V(-3.0, -2.6, 0.45), V(-1.0, 0, 1.6), 26),
              (0.9, V(-0.1, -1.3, 1.2), V(-1.0, 0, 1.72), 40), (tk - 0.2, V(0.0, -1.2, 1.25), V(-1.0, 0, 1.74), 45),
              (tk, V(-2.0, 0.3, 1.5), V(-0.9, BY + 0.25, 1.4), 40), (ctx.dur, V(-2.2, 0.2, 1.6), V(-0.9, BY + 0.25, 0.9), 38)], ease='inout', shake=0.01, fstop=3.2)

# ============================================================ s27 face-off
def s27(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    dv, ad, vr, av, bh, ab, ax = _climax_cast(ctx, env, vb, vdh, bb, bdh)
    pd = V(-0.9, 0, vdh); pb = V(0.6, -BY + 0.05, vdh); pv = V(2.3, 0.1, vdh)
    t2 = ctx.lines('DEVARA')[1]['start']
    ad.bake(1, ctx.N, standing(ad, pd, 90, armL='relaxed', armR='hold_side', gest=['explain', 'point', 'shrug'], hand='L', fist=(False, True), look=V(0.6, 0, 1.82),
                               expr=lambda t: 'fierce' if t < 3 else ('smug' if t > t2 else 'deadpan')))
    ab.bake(1, ctx.N, standing(ab, pb, -90, armL='relaxed', armR='hold_side', gest=['point', 'shock'], hand='L', fist=(False, True), look=V(-0.9, -BY, 1.8),
                               expr=lambda t: 'scared' if t < 3 else ('shocked' if t > t2 + 1.5 else 'deadpan')))
    av.bake(1, ctx.N, standing(av, pv, -90, armL='cross', armR='cross_top', gest=False, look=V(-0.9, 0, 1.8), expr=lambda t: 'happy' if t > t2 + 1 else 'neutral'))
    Cam(ctx, [(0, V(0.3, -1.5, 1.7), V(-0.2, 0, 1.75), 32), (2.7, V(0.9, -0.9, 1.75), V(0.6, 0, 1.78), 55),
              (2.9, V(0.1, -0.7, 1.72), V(-0.9, 0, 1.8), 55), (t2 - 0.2, V(0.0, -0.75, 1.72), V(-0.9, 0, 1.8), 58),
              (t2 + 2.3, V(1.2, -1.0, 1.75), V(0.6, 0, 1.78), 55), (ctx.dur, V(1.0, -1.1, 1.75), V(0.4, 0, 1.75), 48)], ease='inout', shake=0.005, fstop=2.8)

# ============================================================ s28 the spin
def s28(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    dv, ad, vr, av, bh, ab, ax = _climax_cast(ctx, env, vb, vdh, bb, bdh)
    tsp = 0.4; tsp1 = 1.6; tsi = ctx.t('spit')
    pd = V(-0.9, 0, vdh); pv = V(2.3, 0.1, vdh)
    def dfn(t):
        spin = C.seg(t, tsp, tsp1, 'inout')
        P = standing(ad, pd, 90 + 360 * spin, armL='relaxed', armR='hold_side', gest=['point', 'explain'], hand='L', fist=(False, True),
                     look=None if spin < 1 else V(0.2, -2.6, 0.2), expr='fierce' if t < 4 else 'smug', stance=1.4)(t)
        out = C.seg(t, tsp - 0.2, tsp + 0.1) * (1 - C.seg(t, tsp1, tsp1 + 0.4))
        P['armR'] = A.blend_arm(A.arm_pose('hold_side', True), A.arm_pose('slash_out', True), out)
        P['hip'] = P['hip'] + V(0, 0, -0.12 * out)
        return P
    ad.bake(1, ctx.N, dfn)
    # Bhaira: blade shatters his axe, he is knocked overboard; then in the water; then spat back onto his boat
    pb = V(0.6, -BY + 0.05, vdh)
    water = V(0.6, -BY - 2.6, -1.25)
    deck_land = V(0.0, 0.2, bdh)
    ab.props.clear()
    axh = ax
    def axe_fn(t):
        if t < tsp + 0.5: return ('hand.R', FIST)
        return None
    ab.hold(axh, axe_fn)
    def bfn(t):
        P = standing(ab, pb, -90, armL='relaxed', armR='hold_side', gest=['shock', 'palm_out'], hand='L', fist=(t < tsp + 0.5, t < tsp + 0.5),
                     look=V(-0.9, -BY, 1.8), expr='scared')(t)
        hit = tsp + 0.55
        if t > hit:
            u = min(1, (t - hit) / 0.9)
            P['root'] = (pb.lerp(water, u) + V(0, 0, 1.2 * math.sin(math.pi * u)), -90 + 90 * u); P['root_rot'] = (-50 * math.sin(math.pi * u), 0)
            P['feet'] = None; P['armL'] = A.arm_pose('shock'); P['armR'] = A.arm_pose('shock', True)
        if t > tsi:  # spat out: high arc back onto his own boat, lands on his backside
            v = min(1, (t - tsi - 0.2) / 1.1) if t > tsi + 0.2 else 0
            P['root'] = (water.lerp(deck_land, v) + V(0, 0, 2.6 * math.sin(math.pi * v)), 0 + 180 * v); P['root_rot'] = (-80 * min(1, v * 1.4), 0)
            if v >= 1: P['root_rot'] = (-80, 0); P['root'] = (deck_land + V(0, 0.4, 0.15), 180)
        return P
    ab.bake(1, ctx.N, bfn)
    sc = ctx.sc; f0 = int((tsp + 0.5) * FPS) + 1; sc.frame_set(f0)
    a0 = axh.matrix_world.translation.copy()
    anim_obj(ctx, axh, lambda t: None if t < tsp + 0.5 else (a0.lerp(V(3.5, -4.0, -0.6), min(1, (t - tsp - 0.5) / 1.0)) + V(0, 0, 2.0 * math.sin(math.pi * min(1, (t - tsp - 0.5) / 1.0))), (t * 14, t * 9, 0)))
    av.bake(1, ctx.N, standing(av, pv, -90, armL='relaxed', armR='relaxed', gest=False, look=V(0.3, -2.6, 0.5), expr=lambda t: 'shocked' if t < 3 else 'laugh'))
    # goons on Bhaira's boat get blown into the sea by the shockwave
    gs, k = _goons(ctx, bb, bdh, n=2, kunjara=False)
    for i, (g, a, p) in enumerate(gs):
        tgt = V(p.x + (1.5 if i == 0 else -1.5), 3.0, -1.5)
        def gfn(t, a=a, p=p, tgt=tgt, i=i):
            P = _idle_goon(a, p, 0, V(-0.9, -BY, 1.6), 'scared', ('shock', 'shock'))(t)
            hit = tsp + 0.6 + 0.1 * i
            if t > hit:
                u = min(1, (t - hit) / 1.0)
                P['root'] = (p.lerp(tgt, u) + V(0, 0, 1.8 * math.sin(math.pi * u)) if u < 1 else V(0, 0, -8), 360 * u); P['root_rot'] = (-120 * u, 0); P['feet'] = None
            return P
        a.bake(1, ctx.N, gfn)
        splash(ctx, V(tgt.x + 0.3, BY + 3.0, 0.0), tsp + 1.6 + 0.1 * i, 1.0, name=f'gsplash{i}')
    splash(ctx, V(0.6, -BY - 2.6 + 0.0, 0.0) + V(0, 0, 0), tsp + 1.4, 1.2, name='bsplash')
    # Sundaram circles Bhaira, then rises and spits him out
    sroot, shark = S.shark('sundaram', 3.0)
    wc = V(0.6, -5.0, 0)
    def sm(t):
        if t < tsi:
            a = t * 1.4
            return (wc + V(math.cos(a) * 2.2, math.sin(a) * 1.6, -0.55), (0, 0, a + math.pi))
        k = C.seg(t, tsi, tsi + 0.4, 'out') * (1 - C.seg(t, tsi + 1.2, tsi + 1.8, 'in'))
        return (wc + V(0, 2.4, -0.55 + 1.6 * k), (math.radians(-60 * k), 0, math.radians(180)))
    anim_obj(ctx, sroot, sm)
    splash(ctx, V(0.6, -2.6, 0), tsi + 0.2, 1.4, name='spitsplash')
    flash = S.light('POINT', 'slashglow', loc=(-0.9, 0, 1.4), energy=0, color=(0.7, 0.85, 1.0), size=0.5)
    for f in range(1, ctx.N + 1):
        t = (f - 1) / FPS; flash.data.energy = 3000 * math.exp(-max(0, t - tsp - 0.5) * 6) * (1 if t > tsp + 0.4 else 0); flash.data.keyframe_insert('energy', frame=f)
    Cam(ctx, [(0, V(-0.9, -4.6, 2.4), V(-0.9, 0, 1.3), 26), (tsp1 + 0.2, V(-1.8, -5.5, 3.2), V(-0.3, -1.5, 0.8), 24),
              (ctx.t('spin', 'end'), V(-1.5, -4.8, 1.8), V(0.6, -4.8, 0.2), 32), (tsi - 0.3, V(-1.0, -3.4, 1.9), V(0.4, -1.5, 1.2), 30),
              (ctx.dur, V(-3.0, -2.5, 2.6), V(0.3, 1.5, 0.8), 26)], ease='inout', shake=0.02, fstop=4)

# ============================================================ s29 hug
def s29(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx)
    dv, ad = make('devara', ctx, seed=3, parent=vb); ctx.cast(ad, 'DEVARA'); E.wind_hair(dv, ctx, 0.03, 1.0)
    vr, av, _, _ = _vara(ctx, vb, disguise=False)
    pd = V(-0.16, 0, vdh); pv = V(0.17, 0.0, vdh)
    tv = ctx.lines('VARA')[0]['start']
    hug = lambda t: C.seg(t, 0.2, 0.9) * (1 - C.seg(t, tv - 1.2, tv - 0.5))
    def dfn(t):
        P = standing(ad, pd, 90, armL='relaxed', armR='relaxed', gest=['explain'], hand='L', look=V(0.22, 0, 1.75), expr=lambda t: 'happy' if t < 2.4 else 'smug')(t)
        h = hug(t)
        P['armL'] = A.blend_arm(P['armL'], A.reach_to('hug', pv + V(0.04, 0.18, vr.J['chest'].z), False), h)
        P['armR'] = A.blend_arm(P['armR'], A.reach_to('hug', pv + V(0.04, -0.18, vr.J['chest'].z + 0.1), True), h)
        return P
    def vfn(t):
        P = standing(av, pv, -90, armL='relaxed', armR='relaxed', gest=['shrug'], hand='R', look=V(-0.18, 0, 1.82), expr=lambda t: 'happy' if t < tv else 'proud')(t)
        h = hug(t)
        P['armL'] = A.blend_arm(P['armL'], A.reach_to('hug', pd + V(-0.04, -0.18, dv.J['chest'].z), False), h)
        P['armR'] = A.blend_arm(P['armR'], A.reach_to('hug', pd + V(-0.04, 0.18, dv.J['chest'].z - 0.05), True), h)
        return P
    ad.bake(1, ctx.N, dfn); av.bake(1, ctx.N, vfn)
    Cam(ctx, [(0, V(0.1, -2.4, 1.6), V(0.0, 0, 1.6), 38), (ctx.dur, V(0.05, -1.7, 1.65), V(0.0, 0, 1.65), 46)], ease='smooth', shake=0.004, fstop=2.2)

# ============================================================ s30 the ship
def s30(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx, ship=True, fog=0.02)
    ship = env['ship']
    dv, ad = make('devara', ctx, seed=3, parent=vb); vr, av, _, _ = _vara(ctx, vb, disguise=False)
    turn = lambda t: C.seg(t, 0.8, 1.6)
    ad.bake(1, ctx.N, standing(ad, V(-0.2, 0, vdh), lambda t: 90 + 90 * turn(t), armL='relaxed', armR='relaxed', gest=False, look=V(0, 30, 6), expr='fierce'))
    av.bake(1, ctx.N, standing(av, V(0.5, 0.1, vdh), lambda t: -90 - 90 * turn(t), armL='relaxed', armR='relaxed', gest=False, look=V(0, 30, 6), expr='scared'))
    anim_obj(ctx, ship['root'], lambda t: (V(0, 46 - 14 * C.seg(t, 0, ctx.dur, 'smooth'), 0), (math.radians(1.2 * math.sin(t)), 0, 0)))
    Cam(ctx, [(0, V(1.5, -3.5, 1.0), V(0, 30, 5), 28), (ctx.dur, V(1.0, -2.6, 0.7), V(0, 28, 7), 26)], ease='smooth', shake=0.006, fstop=8)

def _yethi_on_prow(ctx, ship, hood_off_at):
    yt, ay = make('yethi', ctx, seed=31, parent=ship['root']); ctx.cast(ay, 'YETHI')
    # hood: cone+cloak shell hiding the head until it slides back
    rx, ry, rz = yt.hr
    hood = C.ellipsoid('hood', rx * 1.45, ry * 1.4, rz * 1.35, seg=40, rings=24,
                       shape=lambda x, y, z: (x, y + (ry * 0.25 if z > 0 else 0) * (1 if y > 0 else 0.3), z + (rz * 0.35 * max(0, z / rz) * max(0, y / ry))))
    import bmesh as _bm
    bm = _bm.new(); bm.from_mesh(hood.data)
    _bm.ops.delete(bm, geom=[f for f in bm.faces if (f.calc_center_median().y < -ry * 0.35 and f.calc_center_median().z < rz * 0.75) or f.calc_center_median().z < -rz * 0.9], context='FACES')
    bm.to_mesh(hood.data); bm.free()
    C.add_mod(hood, 'SOLIDIFY', thickness=0.02); C.subsurf(hood, 1)
    C.assign(hood, C.mat('hoodm', (0.03, 0.03, 0.035), rough=0.85, sheen=0.5))
    Mh = ay.sk.rest['head']
    on = Mh.inverted() @ Matrix.Translation(yt.hc + V(0, 0.0, 0.02))
    off = Mh.inverted() @ Matrix.Translation(yt.hc + V(0, 0.28, -0.22)) @ Matrix.Rotation(math.radians(-70), 4, 'X')
    def hf(t):
        k = C.seg(t, hood_off_at, hood_off_at + 0.6)
        return ('head', on.lerp(off, k) if hasattr(on, 'lerp') else (on if k < 0.5 else off))
    ay.hold(hood, hf)
    return yt, ay

def s31(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx, ship=True, fog=0.016)
    ship = env['ship']; ship['root'].location = (0, 32, 0)
    tr = ctx.t('reveal')
    yt, ay = _yethi_on_prow(ctx, ship, tr - 0.1)
    pr = V(0, -(26 * 0.42 - 4.0), ship['deck_z'])
    ay.bake(1, ctx.N, standing(ay, pr, 0, armL='relaxed', armR='relaxed', gest=False, expr=lambda t: 'fierce' if t < tr + 0.6 else 'smug', look=None, head=(10, 0, 0)))
    red = S.light('SPOT', 'redback', loc=(0, 32 - 6, 9), rot=(0, 0, 0), energy=4000, color=(1, 0.1, 0.05), size=0.5, spot=40)
    red.location = (0, 32 + pr.y + 5, pr.z + 5)
    red.rotation_euler = (V(0, 32 + pr.y, pr.z + 1.5) - red.location).to_track_quat('-Z', 'Y').to_euler()
    hz = pr.z + yt.hc.z
    w = V(0, 32 + pr.y, 0)
    Cam(ctx, [(0, w + V(0.6, -5.0, hz - 2.2), w + V(0, 0, hz - 0.4), 40), (tr - 0.2, w + V(0.4, -3.4, hz - 1.2), w + V(0, 0, hz), 60),
              (ctx.dur, w + V(0.25, -2.2, hz - 0.35), w + V(0, 0, hz), 85)], ease='smooth', shake=0.004, fstop=2.0)

def s32(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx, ship=True, fog=0.016)
    ship = env['ship']; ship['root'].location = (0, 32, 0)
    dv, ad = make('devara', ctx, seed=3, parent=vb); ctx.cast(ad, 'DEVARA')
    vr, av, _, _ = _vara(ctx, vb, disguise=False)
    tv = ctx.lines('VARA')[0]; td = ctx.lines('DEVARA')[0]; tb = ctx.lines('BHAIRA')[0]
    lookship = V(0, 22, 6)
    ad.bake(1, ctx.N, standing(ad, V(-0.2, 0, vdh), lambda t: 180 - 70 * C.seg(t, td['start'] - 0.4, td['start']), armL='relaxed', armR='head_hold', gest=['explain', 'shrug'], hand='L',
                               look=lambda t: lookship if t < tv['end'] else V(0.5, 0, 1.75), expr=lambda t: 'shocked' if t < td['start'] else 'worried'))
    av.bake(1, ctx.N, standing(av, V(0.5, 0.1, vdh), lambda t: 180 + 70 * C.seg(t, 0.2, 0.6), armL='point_up', armR='relaxed', gest=False,
                               look=lambda t: V(-0.2, 0, 1.82) if t > 0.4 else lookship, expr='shocked'))
    bh, ab = make('bhaira', ctx, seed=7); ctx.cast(ab, 'BHAIRA')
    ab.bake(1, ctx.N, standing(ab, V(1.6, -2.8, -1.25), 30, armL='palm_out', armR='shrug', gest=['shrug'], hand='R', look=V(0, 0, 1.6),
                               expr=lambda t: 'deadpan' if t < tb['start'] else 'angry', extra=lambda t, P: P.update(feet=None)))
    Cam(ctx, [(0, V(0.2, -2.0, 1.65), V(0.15, 0, 1.7), 40), (td['start'] - 0.2, V(0.15, -1.6, 1.7), V(0.15, 0, 1.72), 48),
              (tb['start'] - 0.3, V(0.1, -1.4, 1.7), V(0.0, 0, 1.75), 52), (tb['start'], V(3.4, -4.6, 0.6), V(1.6, -2.8, 0.4), 40),
              (ctx.dur, V(3.0, -4.2, 0.55), V(1.6, -2.8, 0.4), 44)], ease='inout', shake=0.005, fstop=2.8)

def s33(ctx):
    env, vb, vdh, bb, bdh = _sea(ctx, ship=True, fog=0.016)
    ship = env['ship']; ship['root'].location = (0, 32, 0)
    yt, ay = make('yethi', ctx, seed=31, parent=ship['root']); ctx.cast(ay, 'YETHI')
    pr = V(0, -(26 * 0.42 - 4.0), ship['deck_z'])
    ay.bake(1, ctx.N, standing(ay, pr, 0, armL='cross', armR='cross_top', gest=False, expr='smug', look=None, head=(6, -6, 0),
                               extra=lambda t, P: P.update(mouth={'smile': 0.9 * C.seg(t, 2.4, 2.9)})))
    sun = S.light('SUN', 'thunder', rot=(50, 0, 20), energy=0, color=(0.8, 0.85, 1.0))
    E.lightning(ctx, sun, [2.6], base=0.0, peak=18)
    red = S.light('SPOT', 'redback', loc=(0, 32 + pr.y + 5, pr.z + 5), energy=4000, color=(1, 0.1, 0.05), size=0.5, spot=40)
    w = V(0, 32 + pr.y, 0); hz = pr.z + yt.hc.z
    S.light('AREA', 'yethikey', loc=(1.2, 32 + pr.y - 3, hz + 1.0), rot=(70, 0, 20), energy=180, color=(0.7, 0.75, 1.0), size=2)
    red.rotation_euler = (w + V(0, 0, hz) - red.location).to_track_quat('-Z', 'Y').to_euler()
    Cam(ctx, [(0, w + V(0.3, -1.4, hz - 0.15), w + V(0, 0, hz), 70), (ctx.dur, w + V(0.2, -1.05, hz - 0.08), w + V(0, 0, hz + 0.01), 80)], ease='smooth', shake=0.003, fstop=2.0)

# ============================================================ OUTRO
def s34(ctx):
    env = E.hut_interior(ctx)
    sg, a_s, dsp, a_d, st = _hut_cast(ctx, env)
    ts = ctx.t('sip'); tw = ctx.t('wink'); tl = ctx.lines('SINGAPPA')[2]['start']
    arm, home = _sip(a_s, env['glasses']['R'], ts - 0.1, ts + 1.3)
    def wink(t, P):
        if tw + 0.2 < t < tw + 0.8: P['lidR'] = 0.0
        P['torso'] = (8 - 12 * C.seg(t, tl, tl + 0.2) * (1 - C.seg(t, tl + 0.9, tl + 1.3)), 0, 0)
    fs = sit_fn(a_s, st['R'], -90, 0.46, armL='table', armR=arm, look=V(-1.0, 0, 1.25), gest=['explain', 'point_up', None], hand='L',
                expr=lambda t: 'laugh' if t > tl - 0.1 else ('smug' if t > tw - 0.2 else 'wise'), extra=wink)
    fd = sit_fn(a_d, st['L'], 90, 0.46, armL='table', armR='table', look=V(1.0, 0, 1.25), gest=['palm_out'], hand='R',
                expr=lambda t: 'shocked' if t < 4 else ('deadpan' if t < tl else 'shocked'),
                extra=lambda t, P: P.update(mouth={'O': 0.9} if t < 0.85 else P.get('mouth', {})))
    a_s.bake(1, ctx.N, fs); a_d.bake(1, ctx.N, fd)
    Cam(ctx, [(0, V(-0.2, -1.2, 1.32), V(-1.0, 0, 1.25), 50), (4.0, V(-0.25, -1.1, 1.32), V(-1.0, 0, 1.25), 52),
              (4.3, V(-0.5, -1.2, 1.4), V(1.0, 0, 1.28), 52), (tw + 1.0, V(-0.35, -0.95, 1.38), V(1.0, 0, 1.3), 65),
              (ctx.dur, V(0.3, -3.4, 1.7), V(0, 0, 1.1), 30)], ease='inout', shake=0.004, fstop=2.8)

def s35(ctx):
    p, em = E.title_void(ctx, ctx.asset('endcard.png'))
    for f in range(1, ctx.N + 1):
        t = (f - 1) / FPS; k = C.seg(t, 0.0, 1.2, 'out')
        em.inputs[1].default_value = 1.5 * k * (1 - C.seg(t, ctx.dur - 1.0, ctx.dur)); em.inputs[1].keyframe_insert('default_value', frame=f)
    emi = C.prim('plane', 'emberemit', loc=(0, -1, -6), size=18)
    ps = emi.modifiers.new('emb', 'PARTICLE_SYSTEM').particle_system; st = ps.settings
    st.count = 400; st.frame_start = -60; st.frame_end = ctx.N; st.lifetime = 120; st.normal_factor = 2.0; st.factor_random = 0.6
    st.effector_weights.gravity = -0.05; st.render_type = 'OBJECT'
    ember = C.prim('ico', 'ember', loc=(0, 0, -300), radius=0.04, subdivisions=1); C.assign(ember, C.emission_mat('emberm', (1.0, 0.35, 0.05), 25))
    st.instance_object = ember; st.size_random = 0.8; ps.seed = 5; emi.show_instancer_for_render = False
    Cam(ctx, [(0, V(0, -22.5, 0.1), V(0, 0, 0), 50), (ctx.dur, V(0, -21.0, 0.1), V(0, 0, 0), 50)], dof=False)

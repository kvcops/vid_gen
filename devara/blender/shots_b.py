"""ACT 2 — flashback rocks, island retirement, village (s10-s20)."""
from shots_common import *

def make_wig(name='wig'):
    """Builds Devara's hair + beard as detachable props (exact look-alike), origin at Devara's head centre."""
    src = Character('devara', name=name + 'src')
    hc = src.hc.copy()
    bpy.context.view_layer.update()
    keep = {'hair': [f'{src.name}_clumps', f'{src.name}_scalp'], 'beard': [f'{src.name}_beard', f'{src.name}_mustache']}
    out = {}
    for k, names in keep.items():
        objs = []
        for n in names:
            o = bpy.data.objects.get(n)
            if not o: continue
            mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
            C.apply_mods(o); objs.append(o)
        j = C.join(objs, f'{name}_{k}')
        bpy.context.view_layer.update()
        j.data.transform(j.matrix_world); j.matrix_world = Matrix.Identity(4)
        j.data.transform(Matrix.Translation(-hc)); j.location = hc
        out[k] = j
    for o in list(bpy.data.objects):
        if o.name.startswith(src.name) and o not in out.values():
            bpy.data.objects.remove(o, do_unlink=True)
    return out['hair'], out['beard'], hc

def wear(actor, H_src=1.86):
    """hold() local matrix that puts a wig (origin = source head centre) onto actor's head."""
    ch = actor.ch
    Mh = actor.sk.rest['head']
    s = actor.H / H_src
    return Mh.inverted() @ Matrix.Translation(ch.hc) @ Matrix.Diagonal((s, s, s, 1))

# ============================================================ ROCKS flashback
def _rocks_pair(ctx):
    env = E.rocks_night(ctx); g = env['ground']
    dv, ad = make('devara', ctx, seed=3); E.wind_hair(dv, ctx, 0.03, 1.0)
    vr, av = make('vara', ctx, seed=5)
    ctx.cast(ad, 'DEVARA'); ctx.cast(av, 'VARA')
    return env, g, dv, ad, vr, av

def s10(ctx):
    env, g, dv, ad, vr, av = _rocks_pair(ctx)
    ts = 0.85; tp = ctx.t('pull'); tp1 = ctx.t('pull', 'end')
    pd = V(0.42, 0, g); pv = V(-0.40, 0, g)
    fish = S.dried_fish('fish', 0.46); kn = S.knife('vknife')
    # fish hidden in Devara's shirt (chest), then pulled out into his right hand and shown
    fish_chest = grip((90, 0, 0), (0.0, 0.10, -0.115 * dv.H / 1.86))
    ad.hold(fish, lambda t: ('chest', fish_chest) if t < tp + 0.25 else ('hand.R', grip((0, 0, 90), (0.0, 0.06, 0.0))))
    av.hold(kn, lambda t: ('hand.R', FIST) if t < ts else None)
    def dfn(t):
        P = standing(ad, pd, -90, armL='relaxed', armR='relaxed', gest=['shock', 'point'], hand='L', look=V(-0.4, 0, g + 1.7) if t > tp1 else V(0.42, -0.6, g + 1.0),
                     expr=lambda t: 'neutral' if t < ts else ('shocked' if t < 3.6 else 'angry'))(t)
        hit = C.seg(t, ts, ts + 0.2, 'out') * (1 - C.seg(t, ts + 0.3, ts + 0.9))
        P['torso'] = (P['torso'][0] - 8 * hit + 10 * C.seg(t, tp - 0.3, tp) * (1 - C.seg(t, tp1, tp1 + 0.3)), P['torso'][1], P['torso'][2])
        P['hip'] = P['hip'] + V(0.03 * hit, 0, 0)
        reach = C.seg(t, tp - 0.25, tp + 0.2) ; show = C.seg(t, tp + 0.2, tp + 0.6)
        P['armR'] = A.blend_arm(A.blend_arm(A.arm_pose('relaxed', True), A.arm_pose('chest', True), reach), A.arm_pose('glass', True), show)
        P['fistR'] = reach > 0.5
        if t < tp1 + 0.2: P['head'] = (22 * C.seg(t, ts + 0.1, ts + 0.5), 0, 0)
        return P
    def vfn(t):
        k = C.seg(t, ts - 0.4, ts, 'in') * (1 - C.seg(t, ts + 0.6, ts + 1.2))
        P = standing(av, pv + V(0.12 * k, 0, 0), 90, armL='relaxed', armR='relaxed', gest=['shrug', 'palm_out'], hand='R', look=V(0.42, 0, g + 1.75),
                     expr=lambda t: 'angry' if t < ts + 0.5 else 'worried')(t)
        if t < ts + 1.3:
            P['armR'] = A.blend_arm(A.arm_pose('hold_side', True), A.arm_pose('stab', True), k); P['fistR'] = t < ts
            P['torso'] = (10 * k, 0, -10 * k)
        return P
    ad.bake(1, ctx.N, dfn); av.bake(1, ctx.N, vfn)
    # knife sticks in the fish after the stab
    sc = ctx.sc; f0 = int(ts * FPS) + 1
    sc.frame_set(f0); off = fish.matrix_world.inverted() @ kn.matrix_world
    for f in range(f0, ctx.N + 1):
        sc.frame_set(f); kn.matrix_world = fish.matrix_world @ off
        kn.keyframe_insert('location', frame=f); kn.keyframe_insert('rotation_euler', frame=f)
    hz = g + 1.62
    Cam(ctx, [(0, V(0.1, -3.4, g + 1.35), V(0, 0, g + 1.25), 40), (ts + 0.05, V(0.1, -3.2, g + 1.35), V(0, 0, g + 1.25), 40),
              (tp + 0.1, V(0.9, -1.4, g + 1.35), V(0.3, 0, g + 1.3), 50), (tp1 + 0.6, V(0.95, -1.2, g + 1.55), V(0.3, 0, g + 1.45), 55),
              (ctx.dur, V(0.2, -2.6, g + 1.45), V(0, 0, hz - 0.15), 42)], shake=0.006, fstop=2.8)

def s11(ctx):
    env, g, dv, ad, vr, av = _rocks_pair(ctx)
    pd = V(0.40, 0.05, g); pv = V(-0.38, -0.05, g)
    vr_sh = pv + V(0.0, 0.0, 0) + V(0, 0, vr.J['sh.L'].z)  # Vara's right shoulder top (he faces +X, so his left is +Y... use centre)
    def dfn(t):
        P = standing(ad, pd, -95, armL='relaxed', armR='relaxed', gest=['explain', 'chest'], hand='L', look=V(-0.38, 0, g + 1.66), expr='wise')(t)
        k = C.seg(t, 0.3, 1.0)
        tgt = V(-0.38, -0.12, g + vr.J['sh.R'].z + 0.04)
        P['armR'] = A.blend_arm(A.arm_pose('relaxed', True), A.reach_to('reach', tgt, True), k)
        return P
    def vfn(t):
        return standing(av, pv, 85, armL='relaxed', armR='relaxed', gest=False, look=V(0.4, 0, g + 1.74), expr=lambda t: 'worried' if t < 5 else 'sad',
                        head=lambda t: (6 * math.sin(t * 2.2) * C.seg(t, 4.5, 5.0) * (1 - C.seg(t, 6.5, 7)), 0, 0))(t)
    ad.bake(1, ctx.N, dfn); av.bake(1, ctx.N, vfn)
    Cam(ctx, [(0, V(-0.9, -2.2, g + 1.5), V(0.2, 0, g + 1.55), 45), (ctx.dur, V(-0.55, -1.45, g + 1.6), V(0.3, 0, g + 1.62), 55)], ease='smooth', shake=0.004, fstop=2.5)

def s12(ctx):
    env, g, dv, ad, vr, av = _rocks_pair(ctx)
    te = ctx.t('epic'); tr = ctx.t('retire'); tsk = ctx.t('shock'); tn = ctx.line(4)['start']
    pd = V(0.40, 0.05, g); pv = V(-0.38, -0.05, g)
    def dyaw(t):  # turns to gaze at the sea (towards -Y) for the epic beat, back for the punchline
        return -95 + 85 * C.seg(t, te - 0.6, te + 0.2) * (1 - C.seg(t, tr - 0.5, tr - 0.1))
    def dfn(t):
        P = standing(ad, pd, dyaw, armL='hip', armR='hip', gest=False, look=None if te - 0.6 < t < tr - 0.3 else V(-0.38, 0, g + 1.66),
                     expr=lambda t: 'fierce' if te < t < tr - 0.4 else ('smug' if t >= tr else 'wise'),
                     head=lambda t: (-8 * C.seg(t, te, te + 0.6) * (1 - C.seg(t, tr - 0.5, tr - 0.1)), 0, 0))(t)
        if t > tn:  # walks away towards the sea edge (right), narration over
            w = C.seg(t, tn + 0.5, ctx.dur)
            P['root'] = (pd + V(1.6 * w, -0.4 * w, 0), dyaw(t) + 60 * C.seg(t, tn + 0.2, tn + 0.8))
            P['feet'] = A.stand_feet(ad, P['root'][0], P['root'][1])
        return P
    jump = lambda t: C.seg(t, tsk - 0.05, tsk + 0.15, 'out') * (1 - C.seg(t, tsk + 0.25, tsk + 0.5, 'in'))
    def vfn(t):
        P = standing(av, pv, 85, armL='relaxed', armR='relaxed', gest=['explain', 'shock'], hand='R', look=V(0.4, 0, g + 1.74),
                     expr=lambda t: 'shocked' if tsk - 0.1 < t < tsk + 2.5 else 'worried')(t)
        j = jump(t)
        P['hip'] = P['hip'] + V(0, 0, 0.09 * j)
        for sd in ('L', 'R'):
            p, fy, pi = P['feet'][sd]; P['feet'][sd] = (p + V(0, 0, 0.09 * j), fy, pi)
        if t > tsk - 0.1:
            k = C.seg(t, tsk - 0.1, tsk + 0.15) * (1 - C.seg(t, tsk + 2.2, tsk + 2.8))
            P['armL'] = A.blend_arm(P['armL'], A.arm_pose('shock'), k); P['armR'] = A.blend_arm(P['armR'], A.arm_pose('shock', True), k)
        return P
    ad.bake(1, ctx.N, dfn); av.bake(1, ctx.N, vfn)
    Cam(ctx, [(0, V(-0.3, -2.4, g + 1.45), V(0, 0, g + 1.55), 40),
              (te - 0.3, V(-0.3, -2.4, g + 1.45), V(0, 0, g + 1.55), 40),
              (te + 0.3, V(1.2, -1.4, g + 0.9), V(0.4, 0, g + 1.75), 32),
              (tr - 0.2, V(1.15, -1.3, g + 0.95), V(0.4, 0, g + 1.72), 34),
              (tr + 0.1, V(0.75, -1.0, g + 1.62), V(0.4, 0, g + 1.66), 60),
              (tsk - 0.1, V(0.75, -1.0, g + 1.62), V(0.4, 0, g + 1.66), 60),
              (tsk + 0.05, V(-0.8, -1.0, g + 1.6), V(-0.38, 0, g + 1.62), 55),
              (tn + 0.3, V(-0.7, -1.2, g + 1.6), V(-0.38, 0, g + 1.6), 50),
              (ctx.dur, V(-2.0, -9.0, g + 6.5), V(0.8, 2, g + 1.0), 32)], ease='inout', shake=0.005, fstop=3.2)

# ============================================================ ISLAND
def _island_devara(ctx, env, extra_pose=None, expr=None):
    dv, ad = make('devara', ctx, seed=3, variant={'shades': True})
    ctx.cast(ad, 'DEVARA')
    mid = env['ham_mid']; head_dir = (env['ham_b'] - env['ham_a']).normalized()
    H = dv.H
    origin = mid - head_dir * (0.53 * H) - V(0, 0, 0.06)
    yaw = math.degrees(math.atan2(head_dir.x, head_dir.y)) * -1  # rotate +Y(head) onto head_dir
    yaw = -90 if head_dir.x > 0 else 90
    def fn(t):
        P = dict(root=(origin, yaw), root_rot=(-78, 0), hip=A.breathe(t, H), torso=(-6, 0, 0), head=(12, 0, 8),
                 armL=A.arm_pose('head_hold'), armR=A.arm_pose('relaxed', True), expr=expr(t) if callable(expr) else (expr or 'happy'))
        env_, tk = ad.talking(t)
        P['head'] = (P['head'][0] + A.talk_head(t, ad)[0], 0, P['head'][2])
        if extra_pose: extra_pose(t, P)
        return P
    return dv, ad, fn, origin, head_dir

def s13(ctx):
    env = E.island(ctx); g = env['ground']
    tc = ctx.t('call'); tsh = ctx.t('shark')
    dv, ad, base, origin, hd = _island_devara(ctx, env)
    fish = S.dried_fish('treat', 0.42)
    root, shark = S.shark('sundaram', 3.0)
    sea_pt = V(0.2, -7.5, -0.15)
    def throw_pose(t, P):
        k = C.seg(t, tc + 0.3, tc + 1.0) * (1 - C.seg(t, tsh - 0.1, tsh + 0.3))
        P['armR'] = A.blend_arm(P['armR'], A.arm_pose('wave', True), k)
        P['head'] = (P['head'][0] - 15 * C.seg(t, tc - 0.5, tc), 0, P['head'][2] - 30 * C.seg(t, tc - 0.5, tc))
    ad.hold(fish, lambda t: ('hand.R', grip((0, 0, 90), (0.0, 0.06, 0.0))) if t < tsh else None)
    ad.bake(1, ctx.N, lambda t: (lambda P: (throw_pose(t, P), P)[1])(base(t)))
    # fish flight + shark leap
    f0 = int(tsh * FPS) + 1; ctx.sc.frame_set(f0); start = fish.matrix_world.translation.copy()
    catch = sea_pt + V(0, 0.9, 1.6)
    def fishfly(t):
        if t < tsh: return None
        u = min(1, (t - tsh) / 0.7)
        p = start.lerp(catch, u) + V(0, 0, 1.6 * math.sin(math.pi * u))
        return (p if u < 1 else V(0, 0, -50), (u * 8, 0, 0))
    anim_obj(ctx, fish, fishfly)
    def sharkm(t):
        a = t * 0.55
        circ = sea_pt + V(math.cos(a) * 2.5, math.sin(a) * 1.2, -0.55)
        yaw = a + math.pi  # tangent direction
        if t < tsh - 0.6:
            return (circ, (0, 0, yaw))
        k = C.seg(t, tsh - 0.6, tsh + 0.55, 'out'); dn = C.seg(t, tsh + 0.9, tsh + 1.6, 'in')
        p = sea_pt + V(0, 0.4, -0.55 + 2.0 * k - 2.2 * dn)
        return (p, (math.radians(-55 * k + 70 * dn), 0, math.radians(180)))
    anim_obj(ctx, root, sharkm)
    splash(ctx, sea_pt + V(0, 0.4, 0), tsh - 0.25, 1.2, name='sp1'); splash(ctx, sea_pt + V(0, 0.6, 0), tsh + 1.35, 1.4, name='sp2')
    hz = origin.z + 0.5
    Cam(ctx, [(0, V(9, -16, 6), V(0, 0, 1.2), 28), (1.4, V(7, -13, 4.5), V(0, 0, 1.4), 30),
              (tc - 0.4, V(1.2, -3.2, g + 1.6), V(0.2, 0.5, g + 1.1), 32),
              (tsh - 0.7, V(1.5, -2.8, g + 1.7), V(0.2, 0.3, g + 1.1), 30),
              (tsh + 0.3, V(-1.2, -1.8, g + 1.4), V(0.2, -6.5, 0.8), 30),
              (ctx.dur, V(-1.0, -2.6, g + 1.2), V(0.2, -7.0, 0.6), 34)], ease='inout', shake=0.004, fstop=5.6)

def s14(ctx):
    env = E.island(ctx); g = env['ground']
    td = ctx.t('drop'); tb = td + 0.85; tl = ctx.lines('DEVARA')[0]['start']
    def ex(t):
        if t < tb: return 'happy'
        if t < tb + 1.4: return 'shocked'
        return 'angry'
    def extra(t, P):
        j = C.seg(t, tb, tb + 0.12, 'out') * (1 - C.seg(t, tb + 0.15, tb + 0.6))
        P['torso'] = (P['torso'][0] + 18 * j, 0, 0)
        if t > tb + 1.0:
            k = C.seg(t, tb + 1.0, tb + 1.4)
            P['armL'] = A.blend_arm(P['armL'], A.arm_pose('head_hold'), 1.0)
            P['armR'] = A.blend_arm(P['armR'], A.arm_pose('fist_up', True), k); P['fistR'] = True
            P['head'] = (P['head'][0] - 25 * k, 0, P['head'][2] - 20 * k)
    dv, ad, base, origin, hd = _island_devara(ctx, env, extra_pose=extra, expr=ex)
    ad.bake(1, ctx.N, base)
    # coconut: hangs at palm B crown, drops on the head, bounces off onto sand
    co = S.coconut('falling')
    top = env['palmB_top'] + V(-0.25, 0, -0.3)
    headw = origin + hd * (0.93 * dv.H) + V(0, 0, 0.62 * math.sin(math.radians(78)) * 0 + 0.32)
    land = headw + V(0.9, -0.9, 0); land.z = g + 0.13
    def cf(t):
        if t < td: return (top, (0, 0, 0))
        if t < tb:
            u = (t - td) / (tb - td); return (top.lerp(headw, u ** 2), (u * 3, 0, 0))
        u = min(1, (t - tb) / 0.7)
        p = headw.lerp(land, u) + V(0, 0, 0.8 * math.sin(math.pi * u)); return (p, (3 + u * 6, 0, u * 2))
    anim_obj(ctx, co, cf)
    stars_ring(ctx, lambda t: headw + V(0, 0, 0.18), tb + 0.1, tb + 1.6)
    Cam(ctx, [(0, V(2.2, -3.4, g + 1.5), V(0.4, 0.4, g + 1.3), 35), (td, V(2.0, -3.0, g + 1.6), V(0.6, 0.4, g + 1.8), 35),
              (tb, V(2.0, -3.0, g + 1.6), V(1.0, 0.4, g + 1.45), 38), (tb + 0.05, V(2.0, -2.0, g + 1.4), V(1.0, 0.45, g + 1.35), 50),
              (ctx.dur, V(1.6, -2.3, g + 1.5), V(0.8, 0.45, g + 1.3), 42)], ease='inout', shake=0.004, fstop=4)

# ============================================================ VILLAGE
def s15(ctx):
    env = E.village(ctx)
    tl = ctx.t('lift'); tr = ctx.t('roar')
    bh, ab = make('bhaira', ctx, seed=7); ctx.cast(ab, 'BHAIRA')
    lg = S.log('log', 2.0, 0.16)
    pos = V(0, 0, 0)
    log_ground = V(0, -0.55, 0.16)
    ab.hold(lg, lambda t: ('between', 0.0, 0.0) if t > tl + 0.15 else None)
    lg.location = log_ground
    def fn(t):
        P = standing(ab, pos, 0, armL='flex', armR='flex', gest=False, expr=lambda t: 'fierce' if t < tr else 'angry', stance=1.6,
                     head=lambda t: (-10 * C.seg(t, tr - 0.3, tr), 0, 0))(t)
        warm = 1 - C.seg(t, tl - 1.2, tl - 0.6)
        bend = C.seg(t, tl - 0.8, tl - 0.1) * (1 - C.seg(t, tl + 0.1, tl + 0.8))
        up = C.seg(t, tl + 0.1, tl + 0.9, 'out')
        # warm-up flex, then squat to the log, then overhead
        P['fistL'] = P['fistR'] = True
        P['torso'] = (40 * bend, 0, 8 * math.sin(t * 1.5) * warm)
        P['hip'] = P['hip'] + V(0, 0.12 * bend, -0.42 * bend)
        lowL = A.reach_to('down', log_ground + V(0.42, 0, 0.02), False); lowR = A.reach_to('down', log_ground + V(-0.42, 0, 0.02), True)
        P['armL'] = A.blend_arm(A.blend_arm(A.arm_pose('flex'), lowL, bend), A.arm_pose('lift'), up)
        P['armR'] = A.blend_arm(A.blend_arm(A.arm_pose('flex', True), lowR, bend), A.arm_pose('lift', True), up)
        if t > tl + 0.9: P['shrug'] = 0.5
        return P
    ab.bake(1, ctx.N, fn)
    Cam(ctx, [(0, V(-14, -26, 14), V(0, 0, 1), 24), (tl - 1.5, V(-2.5, -8.5, 2.0), V(0, 0, 1.4), 32),
              (tl + 0.8, V(-1.2, -4.6, 0.6), V(0, 0, 1.9), 28), (ctx.dur, V(-0.9, -3.9, 0.5), V(0, 0, 2.1), 26)], ease='inout', shake=0.01, fstop=5.6)

def s16(ctx):
    env = E.village(ctx)
    tk = ctx.lines('KUNJARA')[0]['start']; tg = ctx.t('grab'); tpo = ctx.t('poster'); tt = ctx.t('toss')
    bh, ab = make('bhaira', ctx, seed=7); ctx.cast(ab, 'BHAIRA')
    kj, ak = make('kunjara', ctx, seed=9); ctx.cast(ak, 'KUNJARA')
    post = S.poster('poster', ctx.asset('poster.png'), 0.42, 0.6)
    pb = V(0.6, 0, 0); stop = V(-0.35, -0.15, 0)
    path, L = A.line_path((-9, -4, 0), tuple(stop))
    run_end = 1.4
    G = A.Gait(ak, path, lambda t: L * C.ease(min(1, t / run_end), 'out'), L, run=True)
    lift = lambda t: C.seg(t, tg, tg + 0.3) * (1 - C.seg(t, tt, tt + 0.1))
    land = env['nets'][0].location.copy()
    def kfn(t):
        if t < run_end + 0.05:
            gg = G.at(t); aL, aR = A.gait_arms(gg['phase'], gg['amp'], True)
            return dict(root=gg['root'], feet=gg['feet'], hip=gg['hip'], torso=(18 * gg['amp'], 0, 0), armL=aL, armR=aR, expr='scared')
        P = standing(ak, stop, 60, armL='relaxed', armR='relaxed', gest=['explain', None, 'point'], hand='R', look=V(0.6, 0, 1.75),
                     expr=lambda t: 'scared' if t < tpo else 'happy')(t)
        pant = 1 - C.seg(t, tk - 0.2, tk + 0.4)
        P['torso'] = (35 * pant, 0, 0); P['hip'] = P['hip'] + V(0, 0.05 * pant, -0.08 * pant + 0.012 * math.sin(t * 14) * pant)
        if pant > 0.01:
            P['armL'] = A.blend_arm(P['armL'], A.reach_to('down', V(-0.22, -0.4, 0.55), False), pant)
            P['armR'] = A.blend_arm(P['armR'], A.reach_to('down', V(-0.48, -0.25, 0.55), True), pant)
        k = lift(t)
        P['hip'] = P['hip'] + V(0, 0, 0.18 * k)
        for sd in ('L', 'R'):
            p, fy, pi = P['feet'][sd]; P['feet'][sd] = (p + V(0, 0, 0.18 * k), fy, pi - 20 * k)
        sh = C.seg(t, tpo - 0.3, tpo + 0.2) * (1 - C.seg(t, tt - 0.3, tt))
        P['armR'] = A.blend_arm(P['armR'], A.arm_pose('carry', True), sh); P['armL'] = A.blend_arm(P['armL'], A.arm_pose('carry'), sh)
        if t > tt:  # thrown: arc into the net pile, tumbling
            u = min(1, (t - tt) / 1.1)
            p = stop.lerp(land, u) + V(0, 0, 3.2 * math.sin(math.pi * u))
            P['root'] = (p, 60 + 300 * u); P['root_rot'] = (-90 * min(1, u * 1.6), 0)
            P['feet'] = None; P['expr'] = 'scared'
            P['armL'] = A.arm_pose('shock'); P['armR'] = A.arm_pose('shock', True)
        return P
    Mc = ak.sk.rest['chest']; pw = Matrix.Translation(V(0, -0.30, kj.J['chest'].z + 0.05)) @ Matrix.Rotation(math.radians(90), 4, 'X')
    PL = Mc.inverted() @ pw
    ak.hold(post, lambda t: ('chest', PL) if tpo - 0.4 < t < tt else None)
    post.location = (0, 0, -50)
    def bfn(t):
        P = standing(ab, pb, -100, armL='hip', armR='hip', gest=False, look=V(-0.35, -0.15, 1.5), expr=lambda t: 'fierce' if t < tg else ('angry' if t < tpo + 0.6 or t > tt - 1.2 else 'deadpan'))(t)
        k = lift(t)
        grab_pt = stop + V(0.0, 0.0, kj.J['neck0'].z - 0.05 + 0.18 * k)
        P['armR'] = A.blend_arm(A.arm_pose('hip', True), A.reach_to('grab', grab_pt, True), C.seg(t, tg - 0.2, tg + 0.15) * (1 - C.seg(t, tt + 0.1, tt + 0.4)))
        P['fistR'] = tg < t < tt + 0.1
        thr = C.seg(t, tt - 0.25, tt + 0.15)
        P['torso'] = (P['torso'][0], 0, P['torso'][2] + 35 * thr * (1 - C.seg(t, tt + 0.6, tt + 1.2)))
        return P
    ab.bake(1, ctx.N, bfn); ak.bake(1, ctx.N, kfn)
    splash_net = splash(ctx, land + V(0, 0, 0.2), tt + 1.05, 0.6, count=60, name='dust')
    Cam(ctx, [(0, V(-4, -6.5, 1.5), V(-3, -2, 1.0), 30), (run_end, V(-1.2, -3.6, 1.55), V(0.1, 0, 1.45), 32),
              (tpo - 0.2, V(-1.2, -3.6, 1.55), V(0.1, 0, 1.45), 32), (tpo + 0.4, V(-0.1, -1.6, 1.55), V(-0.3, 0.1, 1.45), 45),
              (tt - 0.3, V(-0.1, -1.7, 1.6), V(0, 0, 1.5), 42), (ctx.dur, V(-2.5, -4.5, 2.4), V(-3.5, 5, 1.0), 28)], ease='inout', shake=0.008, fstop=4)

def s17(ctx):
    env = E.village(ctx)
    bh, ab = make('bhaira', ctx, seed=7); ctx.cast(ab, 'BHAIRA')
    kj, ak = make('kunjara', ctx, seed=9); ctx.cast(ak, 'KUNJARA')
    tg = ctx.t('glare'); kl = ctx.lines('KUNJARA')[0]
    net = env['nets'][0].location
    pb = V(-3.0, 6.2, 0)
    ab.bake(1, ctx.N, standing(ab, pb, -150, armL='cheek', armR='hip', gest=False, look=lambda t: V(-5.5, 9, 0.6) if t > kl['start'] - 0.3 else V(-6, -3, 1.6),
                               expr=lambda t: 'smug' if t < kl['start'] else ('angry' if t > tg - 0.2 else 'deadpan')))
    kpos = net + V(0.3, -0.2, -1.15)
    ak.bake(1, ctx.N, standing(ak, kpos, -20, armL='relaxed', armR='relaxed', gest=False, look=V(-3.0, 6.2, 1.7),
                               expr=lambda t: 'worried' if t < tg else 'scared',
                               extra=lambda t, P: P.update(hip=P['hip'] + V(0, 0, 0.35 * C.seg(t, kl['start'] - 0.8, kl['start'] - 0.3, 'back') - 0.35 * C.seg(t, tg + 0.4, tg + 0.7, 'in')), feet=None)))
    Cam(ctx, [(0, V(-1.2, 3.6, 1.65), V(-3.0, 6.2, 1.62), 55), (kl['start'] - 0.6, V(-1.4, 3.5, 1.6), V(-3.0, 6.2, 1.6), 55),
              (kl['start'] - 0.3, V(-3.6, 5.5, 1.0), V(-5.2, 8.8, 0.6), 45), (kl['end'] + 0.2, V(-3.7, 5.6, 1.0), V(-5.2, 8.8, 0.6), 48),
              (tg - 0.2, V(-1.6, 4.1, 1.58), V(-3.0, 6.2, 1.62), 75), (ctx.dur, V(-1.8, 4.4, 1.6), V(-3.0, 6.2, 1.63), 80)], ease='inout', shake=0.004, fstop=2.8)

def _vara_thangam(ctx, basket=True):
    env = E.village(ctx, arena=False)
    vr, av = make('vara', ctx, seed=5); ctx.cast(av, 'VARA')
    th, at = make('thangam', ctx, seed=15); ctx.cast(at, 'THANGAM')
    bk = S.basket('basket') if basket else None
    return env, vr, av, th, at, bk

def s18(ctx):
    env, vr, av, th, at, bk = _vara_thangam(ctx)
    pt = V(0.55, 2.0, 0); stop = V(-0.5, 2.0, 0)
    path, L = A.line_path((-5.0, -1.0, 0), tuple(stop))
    G = A.Gait(av, path, lambda t: L * C.ease(min(1, t / 2.8), 'smooth'), L)
    av.hold(bk, lambda t: ('between', 0.0, 0.06))
    def vfn(t):
        carry = (A.arm_pose('carry'), A.arm_pose('carry', True))
        if t < 2.85:
            gg = G.at(t)
            return dict(root=gg['root'], feet=gg['feet'], hip=gg['hip'], torso=(4, 0, 0), armL=carry[0], armR=carry[1], look=V(0.55, 2, 1.5), expr='happy')
        P = standing(av, stop, 90, armL=carry[0], armR=carry[1], gest=False, look=V(0.55, 2.0, 1.48), expr=lambda t: 'worried' if t < 7 else 'scared',
                     torso=(6, 0, 0))(t)
        P['shrug'] = 0.6 * C.seg(t, 5.6, 6.0)
        return P
    av.bake(1, ctx.N, vfn)
    at.bake(1, ctx.N, standing(at, pt, -90, armL='cross', armR='cross_top', gest=['point', 'explain'], hand='R', look=lambda t: V(-0.5 if t > 2.5 else -2, 2.0, 1.66),
                               expr=lambda t: 'angry' if t < 5.5 else 'deadpan'))
    Cam(ctx, [(0, V(-2.0, -4.0, 1.5), V(-2.5, 1, 1.2), 30), (2.6, V(0.0, -1.6, 1.5), V(0, 2, 1.45), 35),
              (5.6, V(0.0, -1.5, 1.5), V(0, 2, 1.45), 35), (6.0, V(0.9, 0.6, 1.55), V(-0.5, 2, 1.55), 50), (ctx.dur, V(0.8, 0.8, 1.55), V(-0.5, 2, 1.58), 55)],
        ease='inout', shake=0.005, fstop=3.2)

def s19(ctx):
    env, vr, av, th, at, bk = _vara_thangam(ctx)
    wig, beard, hcd = make_wig('wig')
    tpull = 0.2; tsh = ctx.t('shush'); tl3 = ctx.lines('THANGAM')[1]['start']
    pt = V(0.55, 2.0, 0); pv = V(-0.5, 2.0, 0)
    av.hold(bk, lambda t: ('between', 0.0, 0.06))
    at.hold(wig, lambda t: ('hand.L', grip((180, 0, 0), (0.0, 0.05, -0.12))) if t > tpull + 0.4 else None)
    at.hold(beard, lambda t: ('hand.R', grip((180, 0, 0), (0.0, 0.05, 0.08))) if t > tpull + 0.4 else None)
    wig.location = (-0.0, 2.0, 0.85); beard.location = (0, 2.0, 0.8)
    mouth_t = pt + V(0, 0, th.J['neck1'].z + 0.06)
    def vfn(t):
        P = standing(av, pv, 90, armL='carry', armR='carry', gest=False, look=V(0.55, 2.0, 1.48), expr=lambda t: 'scared' if t < tsh + 3 else 'worried')(t)
        k = C.seg(t, tsh - 0.2, tsh + 0.2) * (1 - C.seg(t, tsh + 1.4, tsh + 1.8))
        P['armR'] = A.blend_arm(P['armR'], A.reach_to('shush', mouth_t + V(-0.08, 0.0, 0.0), True), k)
        P['torso'] = (P['torso'][0] + 12 * k, 0, 0)
        return P
    def tfn(t):
        P = standing(at, pt, -90, armL='relaxed', armR='relaxed', gest=['point', None, 'explain'], hand='R', look=lambda t: V(-0.5, 2.0, 1.55),
                     expr=lambda t: 'shocked' if t < 4 else ('smug' if t > tl3 - 0.3 else 'angry'))(t)
        reach = C.seg(t, tpull - 0.2, tpull + 0.3) * (1 - C.seg(t, tpull + 0.4, tpull + 0.9))
        show = C.seg(t, tpull + 0.5, tpull + 1.0) * (1 - C.seg(t, tl3 - 0.5, tl3))
        bpt = pv + V(0.35, 0, 0.95)
        P['armL'] = A.blend_arm(A.blend_arm(A.arm_pose('relaxed'), A.reach_to('reach', bpt + V(0, 0.08, 0), False), reach), A.arm_pose('fist_up'), show)
        P['armR'] = A.blend_arm(A.blend_arm(A.arm_pose('relaxed', True), A.reach_to('reach', bpt + V(0, -0.08, 0), True), reach), A.arm_pose('shock', True), show)
        if t > tl3 - 0.5:
            c = C.seg(t, tl3 - 0.5, tl3)
            P['armL'] = A.blend_arm(P['armL'], A.arm_pose('cross'), c); P['armR'] = A.blend_arm(P['armR'], A.arm_pose('cross_top', True), c)
        P['fistL'] = P['fistR'] = show > 0.3 and t < tl3 - 0.3
        return P
    av.bake(1, ctx.N, vfn); at.bake(1, ctx.N, tfn)
    # once Thangam crosses her arms, wig & beard drop back in the basket
    f1 = int((tl3 - 0.3) * FPS)
    for o in (wig, beard):
        ctx.sc.frame_set(f1); m = o.matrix_world.copy()
        for f in range(f1, ctx.N + 1):
            o.location = V(-0.05, 2.0, -5); o.keyframe_insert('location', frame=f)
    Cam(ctx, [(0, V(0.1, -0.9, 1.5), V(0.1, 2, 1.4), 32), (tpull + 1.2, V(0.6, 0.2, 1.55), V(0.4, 2, 1.55), 45),
              (tsh - 0.3, V(0.5, 0.3, 1.55), V(0.3, 2, 1.55), 45), (tsh + 0.2, V(-0.1, 0.4, 1.5), V(0, 2, 1.5), 38),
              (tl3 - 0.2, V(-0.1, 0.4, 1.5), V(0, 2, 1.5), 38), (tl3 + 0.2, V(-0.4, 0.9, 1.56), V(0.55, 2, 1.55), 60), (ctx.dur, V(-0.45, 1.0, 1.56), V(0.55, 2, 1.56), 62)],
        ease='inout', shake=0.005, fstop=3.2)

def s20(ctx):
    env, vr, av, th, at, bk = _vara_thangam(ctx, basket=False)
    kj, ak = make('kunjara', ctx, seed=9); ctx.cast(ak, 'KUNJARA')
    g1, a1 = make('goon1', ctx, seed=21)
    g2, a2 = make('goon2', ctx, seed=23)
    tf = ctx.t('flip'); tk2 = ctx.lines('KUNJARA')[1]['start']; tv = ctx.lines('VARA')[0]['start']
    pt = V(0.55, 2.0, 0); pv = V(-0.5, 2.0, 0)
    pk = V(0.4, -0.4, 0); p1 = V(1.25, 1.6, 0); p2 = V(-0.2, 0.9, 0)
    av.bake(1, ctx.N, standing(av, pv, 90, armL='relaxed', armR='relaxed', gest=['chest'], hand='R', look=lambda t: V(0.55, 2.0, 1.48) if t < 0.8 or t > tf else V(0.4, -0.4, 1.4),
                               expr=lambda t: 'scared' if t < tf else ('shocked' if t < tv else 'happy'),
                               extra=lambda t, P: P.update(armL=A.blend_arm(P['armL'], A.arm_pose('chest'), C.seg(t, tv - 0.3, tv)), armR=A.blend_arm(P['armR'], A.arm_pose('chest', True), C.seg(t, tv - 0.3, tv)))))
    def tfn(t):
        P = standing(at, pt, -90, armL='relaxed', armR='hip', gest=['point'], hand='R', look=lambda t: V(1.25, 1.6, 1.55) if t < tf + 2 else V(0.4, -0.4, 1.0),
                     expr=lambda t: 'angry' if t < tf + 2.4 else 'smug')(t)
        k = C.seg(t, tf - 0.2, tf + 0.15) * (1 - C.seg(t, tf + 0.7, tf + 1.0))
        P['armL'] = A.blend_arm(P['armL'], A.arm_pose('swing_up'), k); P['armR'] = A.blend_arm(P['armR'], A.arm_pose('swing_up', True), k)
        P['torso'] = (P['torso'][0] + 35 * C.seg(t, tf + 0.1, tf + 0.5) * (1 - C.seg(t, tf + 0.8, tf + 1.3)), 0, P['torso'][2] - 30 * k)
        P['hip'] = P['hip'] + V(0, 0, -0.12 * k)
        P['fistL'] = P['fistR'] = k > 0.3
        return P
    at.bake(1, ctx.N, tfn)
    def g1fn(t):
        P = standing(a1, p1, -150, armL='relaxed', armR='relaxed', gest=False, look=V(0.55, 2.0, 1.5), expr='angry')(t)
        grab = C.seg(t, tf - 0.9, tf - 0.4)
        P['armR'] = A.blend_arm(P['armR'], A.reach_to('grab', pt + V(0.15, -0.25, 1.05), True), grab * (1 - C.seg(t, tf + 0.1, tf + 0.2)))
        if t > tf:
            u = min(1, (t - tf) / 0.75)
            land = pt + V(-0.6, 0.9, 0)
            p = p1.lerp(land, u) + V(0, 0, 1.6 * math.sin(math.pi * u))
            P['root'] = (p + V(0, 0, 0.12 * u), -150 + 40 * u); P['root_rot'] = (-90 * C.ease(u, 'inout') * 1.0 - (0 if u < 1 else 0), 0)
            P['feet'] = None; P['expr'] = 'scared' if u < 1 else 'closed'
            P['armL'] = A.arm_pose('shock'); P['armR'] = A.arm_pose('shock', True)
        return P
    a1.bake(1, ctx.N, g1fn)
    a2.bake(1, ctx.N, standing(a2, p2, 20, armL='cross', armR='cross_top', gest=False, look=V(0.55, 2.0, 1.4),
                               expr=lambda t: 'fierce' if t < tf + 0.5 else 'scared',
                               extra=lambda t, P: P.update(root=(p2 + V(-1.2, -1.0, 0) * C.seg(t, tf + 0.6, tf + 1.4), 20 + 160 * C.seg(t, tf + 0.6, tf + 0.9)))))
    def kfn(t):
        P = standing(ak, pk, -30, armL='hip', armR='point', gest=['point', 'shock'], hand='R', look=V(0.55, 2.0, 1.45),
                     expr=lambda t: 'smug' if t < tf else 'scared')(t)
        fall = C.seg(t, tf + 0.9, tf + 1.3, 'in')
        if fall > 0:  # plops down on his backside
            P['hip'] = P['hip'] + V(0, 0.15 * fall, -0.72 * fall)
            P['torso'] = (-25 * fall, 0, 0)
            P['feet'] = {sd: (pk + right_of(-30) * sg * 0.14 + fwd(-30) * 0.55 * fall + V(0, 0, kj.J['an.L'].z), -30, -40 * fall) for sd, sg in (('L', -1), ('R', 1))}
        return P
    ak.bake(1, ctx.N, kfn)
    splash(ctx, pt + V(-0.6, 0.9, 0.05), tf + 0.75, 0.5, count=70, name='sanddust')
    Cam(ctx, [(0, V(0.4, -3.2, 1.6), V(0.4, 0.8, 1.3), 30), (tf - 0.6, V(0.4, -3.0, 1.6), V(0.5, 1.2, 1.3), 30),
              (tf + 0.9, V(2.2, -1.5, 1.2), V(0.4, 1.8, 0.9), 30), (tf + 2.0, V(1.5, -0.2, 1.55), V(0.55, 2, 1.55), 50),
              (tk2 - 0.3, V(1.5, -0.2, 1.55), V(0.55, 2, 1.55), 50), (tk2, V(1.0, -2.0, 0.9), V(0.4, -0.2, 0.8), 40),
              (tv - 0.3, V(1.0, -2.0, 0.9), V(0.4, -0.2, 0.8), 40), (tv, V(0.6, 1.0, 1.55), V(-0.5, 2, 1.55), 60), (ctx.dur, V(0.55, 1.1, 1.56), V(-0.5, 2, 1.56), 64)],
        ease='inout', shake=0.006, fstop=3.2)

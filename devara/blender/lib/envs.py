"""Per-location environment builders. Each returns a dict of anchor points used by shots.
All character ground surfaces are perfectly flat at known heights (feet never sink)."""
import bpy, math
from mathutils import Vector
from . import core as C
from . import sets as S

def _rain(ctx, area=60, count=9000, center=(0, 0, 0), z=20):
    em = C.prim('plane', 'rainemit', loc=(center[0], center[1], z), size=area)
    ps = em.modifiers.new('rain', 'PARTICLE_SYSTEM').particle_system; st = ps.settings
    st.count = count; st.frame_start = -60; st.frame_end = ctx.N; st.lifetime = 40
    st.normal_factor = 0; st.object_align_factor = (0, 0, -14); st.effector_weights.gravity = 0.0
    st.render_type = 'OBJECT'
    drop = C.prim('cyl', 'raindrop', loc=(0, 0, -100), radius=0.006, depth=0.45, vertices=4)
    C.assign(drop, C.mat('rainm', (0.7, 0.75, 0.85), rough=0.1, alpha=0.5, emit=(0.4, 0.45, 0.55), emit_str=0.3))
    st.instance_object = drop; st.particle_size = 1; st.use_rotations = True; st.rotation_mode = 'VEL'
    drop.visible_shadow = False; em.visible_shadow = False
    st.use_rotation_instance = True
    ps.seed = 7
    em.show_instancer_for_render = False
    return em

def wind_hair(ch, ctx, strength=0.03, speed=1.2):
    """animated noise displacement on hair clumps (wind) — deterministic."""
    h = ch.face.get('hair')
    if not h: return
    e = C.empty(ch.name + '_wind')
    tex = bpy.data.textures.new(ch.name + '_windtx', 'CLOUDS'); tex.noise_scale = 0.35
    m = h.modifiers.new('wind', 'DISPLACE'); m.texture = tex; m.texture_coords = 'OBJECT'; m.texture_coords_object = e
    m.strength = strength; m.direction = 'Y'
    e.location = (0, 0, 0); e.keyframe_insert('location', frame=1)
    e.location = (speed * ctx.N / C.FPS, speed * 0.3 * ctx.N / C.FPS, 0); e.keyframe_insert('location', frame=ctx.N)
    C.all_linear(e)

def lightning(ctx, sun, times, base=0.3, peak=14.0, world_bg=None, wbase=0.2, wpeak=3.0, bolt_at=None):
    """keyframe lightning flashes (double flicker) on a sun lamp and optionally the world background."""
    def val(t):
        v = 0
        for t0 in times:
            d = t - t0
            if 0 <= d < 0.5:
                v = max(v, math.exp(-d * 9) * (1 if d < 0.06 or 0.12 < d < 0.2 else 0.35))
        return v
    for f in range(1, ctx.N + 1):
        t = (f - 1) / C.FPS; k = val(t)
        sun.data.energy = base + (peak - base) * k; sun.data.keyframe_insert('energy', frame=f)
        if world_bg is not None:
            world_bg.inputs[1].default_value = wbase + (wpeak - wbase) * k; world_bg.inputs[1].keyframe_insert('default_value', frame=f)
    return val

# ------------------------------------------------------------------ STORM (prologue)
def storm(ctx, rain=True):
    sc = ctx.sc
    w, nt, bg, out = C.world_color(sc, (0.035, 0.012, 0.015), (0.32, 0.08, 0.04), 0.9)
    S.world_fog(sc, 0.003, (0.7, 0.4, 0.32), 0.3)
    sea = S.ocean('sea', spatial=80, res=11, choppy=1.6, wave_scale=2.6, t_speed=1.6, frames=ctx.N, color=(0.02, 0.01, 0.012), repeat=4, red=0.05, wind=22, damp=0.3)
    cl = S.cliff(loc=(0, 22, -2), w=26, d=14, h=16)
    ledge_z = 14.0
    led = C.prim('cube', 'ledge', loc=(0, 15.6, ledge_z - 0.6), scale=(2.6, 2.2, 0.6))
    C.add_mod(led, 'BEVEL', width=0.25, segments=4)
    C.assign(led, C.mat('cliffmat', (0.12, 0.1, 0.09), rough=0.9, noise=0.5, noise_scale=6))
    for i in range(6):
        S.rock(f'cr{i}', (math.cos(i) * 9, 10 + i * 1.5, -0.5), size=1.5 + i % 3, seed=i, color=(0.08, 0.07, 0.07))
    sun = S.light('SUN', 'flash', rot=(55, 0, 160), energy=1.0, color=(0.85, 0.85, 1.0), size=0.02)
    rim = S.light('AREA', 'redrim', loc=(0, 40, 22), rot=(-60, 0, 180), energy=40000, color=(1.0, 0.3, 0.15), size=24)
    moonl = S.light('SUN', 'moonl', rot=(38, 0, -25), energy=1.1, color=(0.55, 0.65, 1.0), size=0.03)
    S.moon((-90, 260, 60), 9, 12)
    S.light('AREA', 'ledgefill', loc=(2, 8, 17), rot=(60, 0, 160), energy=900, color=(1.0, 0.55, 0.4), size=4)
    if rain: _rain(ctx, center=(0, 5, 0))
    return dict(ledge=Vector((0, 15.6, ledge_z)), sun=sun, bg=bg, rim=rim, sea=sea)

# ------------------------------------------------------------------ HUT interior (1996)
def hut_interior(ctx):
    sc = ctx.sc
    C.world_color(sc, (0.01, 0.015, 0.03), None, 0.3)
    fl = C.prim('plane', 'floor', size=12); C.assign(fl, C.mat('mudfloor', (0.28, 0.2, 0.13), rough=0.95, noise=0.5, noise_scale=6))
    W, D, Hh = 6.0, 5.0, 3.2
    wm = C.mat('mudwall_in', (0.55, 0.38, 0.24), rough=0.95, noise=0.55, noise_scale=5)
    for nm, loc, sc_ in (('wb', (0, D / 2, Hh / 2), (W / 2, 0.1, Hh / 2)), ('wl', (-W / 2, 0, Hh / 2), (0.1, D / 2, Hh / 2)),
                         ('wr', (W / 2, 0, Hh / 2), (0.1, D / 2, Hh / 2)), ('wf', (0, -D / 2 - 1.5, Hh / 2), (W / 2, 0.1, Hh / 2))):
        o = C.prim('cube', nm, loc=loc, scale=sc_); C.assign(o, wm)
    roof = C.prim('cube', 'ceiling', loc=(0, 0, Hh), scale=(W / 2, D / 2 + 1, 0.05)); C.assign(roof, C.mat('thatch_in', (0.25, 0.18, 0.08), rough=0.95, noise=0.6, noise_scale=30))
    for i in range(5):
        b = C.prim('cyl', 'beam', loc=(-2.4 + i * 1.2, 0, Hh - 0.12), rotation=(math.radians(90), 0, 0), radius=0.07, depth=D + 1, vertices=10)
        C.assign(b, C.mat('wood', (0.2, 0.12, 0.06), rough=0.7, noise=0.4, noise_scale=20))
    # window with moonlight
    win = C.prim('cube', 'window', loc=(-W / 2 + 0.02, 0.6, 1.8), scale=(0.08, 0.5, 0.4)); C.assign(win, C.emission_mat('moonwin', (0.35, 0.45, 0.8), 1.5))
    ml = S.light('AREA', 'moonwin_l', loc=(-W / 2 + 0.3, 0.6, 1.8), rot=(0, -90, 0), energy=60, color=(0.5, 0.6, 1.0), size=0.9)
    # table, stools
    wood = C.mat('wood', (0.2, 0.12, 0.06), rough=0.7, noise=0.4, noise_scale=20)
    tz = 0.74
    top = C.prim('cube', 'tabletop', loc=(0, 0, tz - 0.03), scale=(0.55, 0.42, 0.03)); C.add_mod(top, 'BEVEL', width=0.01, segments=2); C.assign(top, wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            l = C.prim('cube', 'leg', loc=(sx * 0.48, sy * 0.35, (tz - 0.06) / 2), scale=(0.03, 0.03, (tz - 0.06) / 2)); C.assign(l, wood)
    stool_h = 0.46
    stools = {}
    for nm, x in (('L', -1.0), ('R', 1.0)):
        s_ = C.prim('cyl', 'stool' + nm, loc=(x, 0, stool_h - 0.03), radius=0.2, depth=0.06, vertices=24); C.assign(s_, wood)
        for k in range(3):
            a = k * 2.094
            l = C.prim('cyl', 'sleg', loc=(x + math.cos(a) * 0.13, math.sin(a) * 0.13, (stool_h - 0.06) / 2), radius=0.02, depth=stool_h - 0.06, vertices=8); C.assign(l, wood)
        stools[nm] = Vector((x, 0, stool_h))
    lt = S.lantern((0.0, 0.05, 1.75), strength=45, seed=3, f0=1, f1=ctx.N)
    chain = C.tube('chain', [Vector((0, 0.05, 1.92)), Vector((0, 0.05, Hh))], 0.006, res=5); C.assign(chain, C.mat('tin', (0.25, 0.22, 0.18), rough=0.4, metal=0.8))
    fill = S.light('AREA', 'warmfill', loc=(0, -2.4, 2.2), rot=(65, 0, 0), energy=70, color=(1.0, 0.68, 0.42), size=3)
    bounce = S.light('AREA', 'tablebounce', loc=(0, 0, 0.8), rot=(180, 0, 0), energy=12, color=(1.0, 0.6, 0.3), size=1.2)
    # set dressing
    net = S.net_pile((2.3, 2.0, 0.3), 0.6)
    for i in range(4):
        pot = C.prim('sphere', 'pot', loc=(-2.5 + i * 0.35, 2.2, 0.2), radius=0.17, segments=20, ring_count=10); pot.scale = (1, 1, 0.9)
        C.assign(pot, C.mat('clay', (0.45, 0.2, 0.1), rough=0.8, noise=0.3, noise_scale=10))
    oar = C.prim('cube', 'oar', loc=(2.85, 0.5, 1.4), scale=(0.03, 0.08, 1.1)); oar.rotation_euler = (0.15, 0, 0); C.assign(oar, wood)
    fishnet_wall = C.prim('plane', 'wallnet', loc=(2.88, -0.6, 1.7), size=1.4, rotation=(0, math.radians(90), 0)); C.assign(fishnet_wall, C.mat('netm2', (0.3, 0.35, 0.3), rough=0.9, alpha=0.6))
    glasses = {}
    for nm, p in (('L', Vector((-0.32, -0.08, tz + 0.05))), ('R', Vector((0.32, -0.1, tz + 0.05)))):
        g = S.tea_glass('glass' + nm); g.location = p; glasses[nm] = g
    return dict(table_z=tz, stools=stools, glasses=glasses, lantern=lt)

# ------------------------------------------------------------------ ROCKS (night flashback)
def rocks_night(ctx):
    sc = ctx.sc
    w, nt, out = S.sky_night(sc, (0.004, 0.008, 0.03), (0.04, 0.05, 0.09))
    S.world_fog(sc, 0.004, (0.5, 0.55, 0.7), 0.3)
    sea = S.ocean('sea', spatial=60, res=10, choppy=1.0, wave_scale=0.9, t_speed=0.8, frames=ctx.N, color=(0.004, 0.02, 0.035), repeat=4, wind=9)
    plat_z = 1.2
    pl = C.prim('cube', 'platform', loc=(0, 0, plat_z - 0.8), scale=(3.0, 2.2, 0.8)); C.add_mod(pl, 'BEVEL', width=0.35, segments=5)
    C.assign(pl, C.mat('rockdark', (0.1, 0.09, 0.085), rough=0.85, noise=0.45, noise_scale=8))
    for i in range(9):
        S.rock(f'r{i}', (math.cos(i * 0.8) * (4 + i % 3), math.sin(i * 0.8) * 3 + 2.5, 0.3), size=0.8 + (i % 3) * 0.5, seed=i, color=(0.08, 0.075, 0.07))
    S.moon((-40, 160, 55), 5, 10)
    key = S.light('SUN', 'moonkey', rot=(40, 0, 200), energy=2.6, color=(0.6, 0.7, 1.0), size=0.01)
    rim = S.light('AREA', 'rim', loc=(-3, 6, 4), rot=(-55, 0, 200), energy=220, color=(0.6, 0.7, 1.0), size=4)
    fill = S.light('AREA', 'fill', loc=(1.5, -4.5, 3.6), rot=(60, 0, 18), energy=420, color=(0.75, 0.8, 1.0), size=5)
    S.light('AREA', 'warmrim', loc=(4, 3, 3), rot=(-60, 0, 125), energy=250, color=(1.0, 0.6, 0.35), size=3)
    return dict(ground=plat_z)

# ------------------------------------------------------------------ ISLAND (day)
def island(ctx):
    sc = ctx.sc
    S.sky_day(sc, sun_elev=40, sun_rot=210, strength=0.18); sc.view_settings.exposure = -1.6
    sea = S.ocean('sea', spatial=50, res=10, choppy=0.8, wave_scale=0.5, t_speed=0.7, frames=ctx.N, color=(0.02, 0.18, 0.22), repeat=4, wind=7)
    isl = C.prim('sphere', 'island', loc=(0, 0, -5.8), radius=10, segments=64, ring_count=32); isl.scale = (1, 0.8, 0.62)
    tex = bpy.data.textures.new('isl', 'CLOUDS'); tex.noise_scale = 1.2
    C.add_mod(isl, 'DISPLACE', texture=tex, strength=0.25)
    C.assign(isl, C.mat('sandday', (0.78, 0.66, 0.46), rough=0.9, noise=0.3, noise_scale=40))
    top_z = -5.8 + 10 * 0.62 + 0.0  # ~0.4
    # flat walkable sand plateau at exact height
    plat = C.prim('cyl', 'plateau', loc=(0, 0, top_z - 0.25), radius=4.2, depth=0.5, vertices=64)
    C.add_mod(plat, 'BEVEL', width=0.2, segments=4); C.assign(plat, C.mat('sandday', (0.78, 0.66, 0.46), rough=0.9, noise=0.3, noise_scale=40))
    t1, c1, top1 = S.palm('palmA', (-1.6, 0.6, top_z), h=6.2, lean=(-0.12, 0.05), seed=1)
    t2, c2, top2 = S.palm('palmB', (1.7, 0.4, top_z), h=6.6, lean=(0.14, 0.02), seed=2)
    S.palm('palmC', (-3.2, 2.4, top_z - 0.2), h=7.5, lean=(-0.2, 0.1), seed=3)
    S.grass_tufts((0, 1.5, top_z), 3.5, 18, seed=4)
    # hammock between the two palms at ~1.0 m
    hz = top_z + 1.15
    a = Vector((-1.6 - 0.12 * 1.1 * 0.03, 0.6, hz + 0.25)); b = Vector((1.7 + 0.02, 0.4, hz + 0.25))
    verts, faces = [], []
    n, m = 24, 8
    for i in range(n + 1):
        t = i / n; p = a.lerp(b, t); sag = 0.45 * math.sin(math.pi * t)
        for j in range(m + 1):
            u = j / m - 0.5
            wdt = 0.55 * math.sin(math.pi * min(1, 0.15 + t * 0.85)) ** 0.5
            verts.append(p + Vector((0, u * wdt * 1.0, -sag - 0.12 * (1 - (2 * u) ** 2) * math.sin(math.pi * t))))
    for i in range(n):
        for j in range(m):
            k = i * (m + 1) + j; faces.append((k, k + m + 1, k + m + 2, k + 1))
    ham = C.mesh_obj('hammock', verts, faces); C.add_mod(ham, 'SOLIDIFY', thickness=0.01)
    hm = C.mat('hammockm', (0.75, 0.25, 0.12), rough=0.85)
    nt_ = hm.node_tree; p_ = nt_.nodes.get('Principled BSDF'); wv = nt_.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 12
    mix = nt_.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs[6].default_value = (0.75, 0.25, 0.12, 1); mix.inputs[7].default_value = (0.95, 0.8, 0.3, 1)
    gt = nt_.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.6
    nt_.links.new(wv.outputs['Fac'], gt.inputs[0]); nt_.links.new(gt.outputs[0], mix.inputs['Factor']); nt_.links.new(mix.outputs[2], p_.inputs['Base Color'])
    C.assign(ham, hm)
    for end in (a, b):
        r_ = C.tube('hamrope', [end, end + Vector((0, 0, 0.6))], 0.012, res=5); C.assign(r_, C.mat('rope', (0.5, 0.42, 0.3), rough=0.9))
    sun = S.light('SUN', 'sun', rot=(50, 0, 30), energy=5.0, color=(1.0, 0.93, 0.82), size=0.02)
    fill = S.light('AREA', 'bounce', loc=(0, -4, 1.5), rot=(80, 0, 0), energy=150, color=(1.0, 0.85, 0.65), size=5)
    return dict(ground=top_z, ham_mid=(a + b) / 2 + Vector((0, 0, -0.45)), ham_a=a, ham_b=b, palmB_top=top2, palmA_top=top1)

# ------------------------------------------------------------------ VILLAGE (day)
def village(ctx, arena=True, golden=False):
    sc = ctx.sc
    S.sky_day(sc, sun_elev=28 if not golden else 12, sun_rot=200, strength=0.18); sc.view_settings.exposure = -1.4
    sea = S.ocean('sea', loc=(0, 70, -0.6), spatial=70, res=10, choppy=1.0, wave_scale=0.8, t_speed=0.8, frames=ctx.N, color=(0.03, 0.16, 0.2), repeat=3, wind=9)
    beach = S.sand('beach', size=200, flat_r=16, amp=0.5, color=(0.66, 0.53, 0.36), slope=lambda x, y: -0.6 * max(0, (y - 26) / 30) ** 1.5 * 30 / 30)
    # huts in an arc behind the action (south side) and along the sides
    for i, (x, y, r) in enumerate([(-14, -10, 2.2), (-7, -14, 2.4), (1, -15, 2.0), (8, -13, 2.3), (15, -9, 2.1), (-19, -2, 2.0), (20, 1, 2.2)]):
        rot = math.degrees(math.atan2(-x, y)) + 180
        S.hut(f'hut{i}', (x, y, 0), r=r, rot=rot, seed=i)
    for i, (x, y, h, lx, ly) in enumerate([(-10, 6, 8, 0.12, 0.06), (11, 7, 7.5, -0.14, 0.05), (-17, -6, 9, 0.08, -0.04), (17, -5, 8.5, -0.1, 0.0), (-4, -19, 9, 0.05, 0.1), (5, -20, 8, -0.06, 0.08), (-22, 10, 7, 0.1, 0.1), (24, 12, 8, -0.1, 0.1)]):
        S.palm(f'vp{i}', (x, y, 0), h=h, lean=(lx, ly), seed=10 + i)
    # boats pulled up on the sand
    for i, (x, y, rot, col) in enumerate([(-8, 16, 70, (0.12, 0.3, 0.5)), (-2, 19, 95, (0.55, 0.12, 0.08)), (6, 17, 110, (0.1, 0.42, 0.25)), (13, 20, 80, (0.6, 0.45, 0.1))]):
        rt, _ = S.boat(f'vboat{i}', (x, y, 0.25), L=6.5, W=1.5, H=0.9, rot=rot, color=col)
        rt.rotation_euler = (math.radians(4), 0, math.radians(rot))
    nets = [S.net_pile((-5.5, 9, 0.15), 0.9), S.net_pile((8.5, 10, 0.12), 0.7)]
    poles = []
    if arena:
        ring = C.prim('torus', 'arena_ring', loc=(0, 0, 0.02), major_radius=4.6, minor_radius=0.12)
        ring.scale = (1, 1, 0.5); C.assign(ring, C.mat('sandbag', (0.5, 0.36, 0.2), rough=0.95, noise=0.4, noise_scale=20))
        for k in range(8):
            a = 2 * math.pi * k / 8
            p = Vector((math.cos(a) * 5.0, math.sin(a) * 5.0, 0))
            pole = C.tube('apole', [p, p + Vector((0, 0, 3.2))], 0.05, res=8); C.assign(pole, C.mat('wood', (0.2, 0.12, 0.06), rough=0.7, noise=0.4, noise_scale=20))
            poles.append(p)
        for k in range(8):
            S.bunting(poles[k] + Vector((0, 0, 3.1)), poles[(k + 1) % 8] + Vector((0, 0, 3.1)), n=10, sag=0.4)
    sun = S.light('SUN', 'sun', rot=(58 if not golden else 75, 0, 25), energy=4.2 if not golden else 3.0, color=(1.0, 0.92, 0.8) if not golden else (1.0, 0.7, 0.45), size=0.02)
    fill = S.light('AREA', 'skyfill', loc=(0, -8, 6), rot=(55, 0, 0), energy=300, color=(0.75, 0.85, 1.0), size=10)
    return dict(ground=0.0, nets=nets)

# ------------------------------------------------------------------ NIGHT SEA (climax)
def night_sea(ctx, fog=0.012, torches=True, ship=False):
    sc = ctx.sc
    w, nt, out = S.sky_night(sc, (0.003, 0.006, 0.02), (0.03, 0.04, 0.07))
    S.world_fog(sc, fog, (0.45, 0.5, 0.62), 0.35)
    sea = S.ocean('sea', spatial=60, res=11, choppy=1.1, wave_scale=0.7, t_speed=0.9, frames=ctx.N, color=(0.003, 0.015, 0.03), repeat=4, wind=8)
    S.moon((-60, 220, 80), 7, 9)
    key = S.light('SUN', 'moonkey', rot=(42, 0, 200), energy=2.2, color=(0.6, 0.7, 1.0), size=0.01)
    S.light('AREA', 'frontfill', loc=(0, -7, 5), rot=(55, 0, 0), energy=1400, color=(0.7, 0.78, 1.0), size=9)
    rim = S.light('AREA', 'moonrim', loc=(-4, 14, 8), rot=(-50, 0, 200), energy=900, color=(0.55, 0.65, 1.0), size=8)
    boats = {}
    # Vara's boat at the origin, three of Bhaira's boats around it
    rt, dh = S.boat('varaboat', (0, 0, 0), L=6.0, W=1.6, H=0.95, rot=0, color=(0.35, 0.22, 0.12), stripe=(0.9, 0.9, 0.85))
    boats['vara'] = (rt, dh)
    for i, (x, y, rot, col) in enumerate([(0.3, 2.4, 0, (0.08, 0.08, 0.09)), (7.2, -1.0, 25, (0.3, 0.05, 0.04)), (-7.2, -1.4, -25, (0.08, 0.08, 0.09))]):
        rt2, dh2 = S.boat(f'bboat{i}', (x, y, 0), L=6.0, W=1.6, H=0.95, rot=rot, color=col, stripe=(0.8, 0.1, 0.05))
        boats[f'b{i}'] = (rt2, dh2)
        if torches:
            for k, off in enumerate((-2.3, 2.3)):
                tp = Vector((off, 0.5 if i else 0.55, dh2))
                pole = C.tube('tpole', [tp, tp + Vector((0, 0, 1.6))], 0.03, res=6); C.assign(pole, C.mat('wood', (0.2, 0.12, 0.06), rough=0.7, noise=0.4, noise_scale=20))
                fl, lt = S.flame(tp + Vector((0, 0, 1.72)), 0.13, seed=i * 3 + k, f0=1, f1=ctx.N, strength=150)
                for o in (pole, fl, lt): o.parent = rt2
    for nm, (rt_, dh_) in boats.items():
        if nm in ('vara', 'b0'):   # lashed together: identical gentle heave/pitch, almost no roll
            S.bob(rt_, 1, ctx.N, amp=0.04, roll=0.3, pitch=0.7, seed=2)
        else:
            S.bob(rt_, 1, ctx.N, amp=0.05, roll=1.6, pitch=0.8, seed=len(nm) + ord(nm[-1]) % 5)
    res = dict(boats=boats, sea=sea)
    if ship:
        res['ship'] = big_ship(ctx)
    return res

def big_ship(ctx, loc=(0, 40, 0)):
    root = C.empty('ship_root', loc)
    hull_m = C.mat('shiphull', (0.03, 0.025, 0.025), rough=0.6, noise=0.3, noise_scale=6)
    L, W, H = 26, 7, 5
    verts, faces = [], []
    secs, n = 30, 14
    for i in range(secs + 1):
        t = i / secs; y = (t - 0.5) * L
        taper = math.sin(math.pi * (0.03 + 0.94 * t)) ** 0.5 if t < 0.5 else math.sin(math.pi * (0.03 + 0.94 * t)) ** 0.25
        rise = 1.6 * max(0, (0.5 - t) * 2) ** 3  # bow (towards -Y) rises
        for k in range(n + 1):
            a = math.pi * k / n
            x = math.cos(a) * W / 2 * taper; z = -math.sin(a) * H * 0.7 * (0.4 + 0.6 * taper) + H * 0.55 + rise
            verts.append((x, y, z))
    for i in range(secs):
        for k in range(n):
            a = i * (n + 1) + k; b = a + n + 1; faces.append((a, b, b + 1, a + 1))
    hull = C.mesh_obj('shiphull', verts, faces); C.add_mod(hull, 'SOLIDIFY', thickness=0.12); C.assign(hull, hull_m); hull.parent = root
    deck = C.prim('cube', 'shipdeck', loc=(0, 0, H * 0.55 - 0.05), scale=(W * 0.45, L * 0.45, 0.05)); C.assign(deck, hull_m); deck.parent = root
    for my, mh in ((-4, 16), (5, 18)):
        m = C.prim('cyl', 'mast', loc=(0, my, H * 0.55 + mh / 2), radius=0.25, depth=mh, vertices=12); C.assign(m, hull_m); m.parent = root
        sail = C.prim('plane', 'sail', loc=(0, my + 0.4, H * 0.55 + mh * 0.6), size=1, rotation=(math.radians(90), 0, 0)); sail.scale = (5, mh * 0.35, 1)
        C.add_mod(sail, 'SUBSURF', levels=3, render_levels=3, subdivision_type='SIMPLE')
        tex = bpy.data.textures.new('sailw', 'CLOUDS'); tex.noise_scale = 1.5; C.add_mod(sail, 'DISPLACE', texture=tex, strength=0.6)
        C.assign(sail, C.mat('sailcloth', (0.12, 0.03, 0.03), rough=0.9)); sail.parent = root
    for k in range(6):
        p = Vector(((-1) ** k * W * 0.42, -L * 0.35 + k * 3.5, H * 0.55 + 0.7))
        lan = C.prim('ico', 'redlantern', loc=p, radius=0.22, subdivisions=2); C.assign(lan, C.emission_mat('redlan', (1.0, 0.08, 0.04), 30)); lan.parent = root
        lt = S.light('POINT', 'redl', loc=p, energy=300, color=(1, 0.1, 0.05), size=0.2); lt.parent = root
    prow_z = H * 0.55 + 1.6
    return dict(root=root, prow=Vector((0, -L * 0.42, prow_z - 1.2)), deck_z=H * 0.55)

# ------------------------------------------------------------------ TITLE void
def title_void(ctx, image):
    sc = ctx.sc
    C.world_color(sc, (0.0, 0.0, 0.0), None, 0.0)
    p = C.prim('plane', 'title', size=1); p.scale = (16, 9, 1); p.rotation_euler = (math.radians(90), 0, 0)
    m = bpy.data.materials.new('titlem')
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(image)
    em = nt.nodes.new('ShaderNodeEmission'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
    em.inputs[1].default_value = 1.6
    nt.links.new(tx.outputs['Color'], em.inputs[0]); nt.links.new(tx.outputs['Alpha'], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs[0])
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    C.assign(p, m)
    return p, em

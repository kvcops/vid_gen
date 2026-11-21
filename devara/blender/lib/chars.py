"""Procedural stylized characters (fan-art caricatures inspired by costume/silhouette, not likenesses).

Each Character = armature + skinned body + rigid parts on bones (head, face rig, hair, hands, feet, props).
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion
from . import core as C
from .rig import Skeleton, build_armature, joints, frame_rot, BONES

# --------------------------------------------------------------------------- specs
SPECS = {
 'devara': dict(H=1.86, skin=(0.36, 0.20, 0.12), shirt=(0.035, 0.035, 0.045), sleeve='elbow', vneck=0.55,
                lower='lungi_knee', lower_col=(0.03, 0.03, 0.04), lower_check=(0.055, 0.022, 0.02), hair='long', hair_col=(0.018, 0.014, 0.012),
                beard='full', mustache='thick', brow=1.25, kohl=True, kada='R', build=1.1, eyes=(0.17, 0.09, 0.05), jaw=0.32),
 'vara':   dict(H=1.80, skin=(0.37, 0.21, 0.13), shirt=(0.42, 0.58, 0.72), sleeve='forearm', vneck=0.0,
                lower='lungi_knee', lower_col=(0.82, 0.80, 0.74), lower_check=(0.10, 0.22, 0.45), hair='short', hair_col=(0.02, 0.016, 0.014),
                beard='stubble', mustache='trim', brow=1.0, kohl=False, build=1.0, eyes=(0.2, 0.11, 0.06), jaw=0.3),
 'bhaira': dict(H=1.85, skin=(0.46, 0.28, 0.18), shirt=(0.10, 0.12, 0.06), sleeve='none', vneck=0.6,
                lower='lungi_knee', lower_col=(0.32, 0.04, 0.035), lower_check=None, hair='curly', hair_col=(0.03, 0.022, 0.018),
                beard='full', mustache='thick', brow=1.2, kohl=True, earrings=True, armband=True, build=1.15, eyes=(0.24, 0.15, 0.07), jaw=0.36),
 'thangam':dict(H=1.62, skin=(0.50, 0.31, 0.20), shirt=(0.70, 0.12, 0.30), sleeve='short', vneck=0.15, female=True,
                lower='langa', lower_col=(0.80, 0.52, 0.08), lower_check=None, pallu=(0.06, 0.38, 0.22), hair='braid', hair_col=(0.02, 0.015, 0.012),
                beard=None, mustache=None, brow=0.8, kohl=True, bindi=True, earrings=True, bangles=True, build=0.88, eyes=(0.17, 0.09, 0.05), jaw=0.42, lips=(0.45, 0.10, 0.12)),
 'singappa':dict(H=1.68, skin=(0.36, 0.22, 0.15), shirt=(0.80, 0.79, 0.74), sleeve='full', vneck=0.2,
                lower='dhoti', lower_col=(0.84, 0.83, 0.78), lower_check=None, shawl=(0.40, 0.06, 0.07), hair='bald_white', hair_col=(0.75, 0.74, 0.72),
                beard='long_white', mustache='white', brow=1.15, kohl=False, glasses=True, build=0.92, eyes=(0.2, 0.12, 0.06), jaw=0.36, age=1),
 'dsp':    dict(H=1.78, skin=(0.40, 0.25, 0.16), shirt=(0.50, 0.40, 0.24), sleeve='forearm', vneck=0.0,
                lower='pants', lower_col=(0.45, 0.36, 0.21), lower_check=None, hair='short', hair_col=(0.02, 0.016, 0.014),
                beard=None, mustache='police', brow=1.05, kohl=False, cap=True, belt=True, build=1.0, eyes=(0.18, 0.1, 0.05), jaw=0.3),
 'kunjara':dict(H=1.66, skin=(0.33, 0.19, 0.12), shirt=(0.85, 0.38, 0.06), sleeve='short', vneck=0.3,
                lower='lungi_knee', lower_col=(0.08, 0.30, 0.16), lower_check=(0.7, 0.68, 0.2), hair='messy', hair_col=(0.02, 0.016, 0.014),
                beard=None, mustache='thin', brow=0.95, kohl=False, headband=(0.75, 0.06, 0.05), build=0.8, ears=1.35, eyes=(0.2, 0.11, 0.06), jaw=0.24),
 'goon1':  dict(H=1.80, skin=(0.34, 0.20, 0.13), shirt=(0.10, 0.10, 0.12), sleeve='none', vneck=0.4,
                lower='lungi_knee', lower_col=(0.18, 0.12, 0.30), lower_check=None, hair='short', hair_col=(0.02, 0.016, 0.014),
                beard='full', mustache='thick', brow=1.2, kohl=False, headband=(0.1, 0.1, 0.1), build=1.1, eyes=(0.2, 0.1, 0.05), jaw=0.36),
 'goon2':  dict(H=1.76, skin=(0.40, 0.24, 0.15), shirt=(0.30, 0.10, 0.07), sleeve='short', vneck=0.4,
                lower='lungi_knee', lower_col=(0.10, 0.10, 0.10), lower_check=None, hair='messy', hair_col=(0.02, 0.016, 0.014),
                beard='stubble', mustache='thick', brow=1.1, kohl=False, build=1.05, eyes=(0.2, 0.1, 0.05), jaw=0.33),
 'yethi':  dict(H=1.86, skin=(0.36, 0.20, 0.12), shirt=(0.02, 0.02, 0.025), sleeve='full', vneck=0.3,
                lower='coat', lower_col=(0.02, 0.02, 0.025), lower_check=None, hair='long', hair_col=(0.018, 0.014, 0.012), streak=True,
                beard='full', mustache='thick', brow=1.25, kohl=True, shades=True, build=1.1, eyes=(0.17, 0.09, 0.05), jaw=0.32),
}

# --------------------------------------------------------------------------- helpers
def _skin_mesh(name, verts, edges, radii, root=0):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, edges, []); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    m = o.modifiers.new('skin', 'SKIN'); m.use_smooth_shade = True; m.branch_smoothing = 0.6
    sv = me.skin_vertices[0].data
    for i, r in enumerate(radii):
        sv[i].radius = r; sv[i].use_root = (i == root)
    C.subsurf(o, 2)
    return o

def _surface_fn(rx, ry, rz, jaw, chin_fwd):
    """head ellipsoid sculpt + analytic front-surface lookup."""
    def taper(z):
        t = max(0.0, -z / rz)
        return 1 - jaw * t ** 1.6, 1 - 0.18 * t ** 2
    def shape(x, y, z):
        fx, fy = taper(z)
        y2 = y * fy
        if y < 0 and z < 0: y2 -= chin_fwd * rz * max(0, -z / rz) ** 2 * (-y / ry)
        # flatten back of head slightly, raise cranium
        if y > 0: y2 *= 0.96
        return x * fx, y2, z
    def surf(x, z):  # y of front surface at (x,z) in head local coords
        z = max(-rz * 0.999, min(rz * 0.999, z))
        fx, fy = taper(z)
        x0 = x / fx
        k = 1 - (x0 / rx) ** 2 - (z / rz) ** 2
        y0 = -ry * math.sqrt(max(0.0, k))
        y = y0 * fy
        if z < 0: y -= chin_fwd * rz * (-z / rz) ** 2 * (-y0 / ry)
        return y
    return shape, surf


class Character:
    def __init__(self, key, name=None, coll=None, variant=None):
        self.key = key; self.s = dict(SPECS[key]); self.name = name or key
        if variant: self.s.update(variant)
        s = self.s; H = s['H']; self.H = H
        self.J = joints(H, sh_w=0.118 * (s.get('build', 1) ** 0.5), female=s.get('female', False))
        self.arm = build_armature(self.name, self.J, coll)
        self.sk = Skeleton(self.arm, self.J)
        self.parts = []; self.face = {}; self.hands = {}; self.props = {}
        self.mats = self._materials()
        self._body(); self._head(); self._hands(); self._feet(); self._costume_extras()
        self.arm.show_in_front = False

    # ---------------------------------------------------------------- materials
    def _materials(self):
        s = self.s; M = {}
        M['skin'] = C.mat(f'{self.name}_skin', s['skin'], rough=0.48, sss=0.25, noise=0.12, noise_scale=90)
        M['shirt'] = C.mat(f'{self.name}_shirt', s['shirt'], rough=0.8, noise=0.25, noise_scale=140, sheen=0.3)
        M['lower'] = self._cloth_mat(f'{self.name}_lower', s['lower_col'], s.get('lower_check'))
        M['hair'] = C.mat(f'{self.name}_hair', s['hair_col'], rough=0.72, spec=0.3, noise=0.5, noise_scale=260, sheen=0.25)
        M['white'] = C.mat('eye_white', (0.86, 0.84, 0.80), rough=0.25)
        M['iris'] = C.mat(f'{self.name}_iris', s['eyes'], rough=0.2, coat=0.8)
        M['pupil'] = C.mat('pupil', (0.004, 0.004, 0.004), rough=0.1, coat=1.0)
        M['glint'] = C.emission_mat('glint', (1, 1, 1), 1.6)
        M['mouth'] = C.mat('mouth_in', (0.09, 0.012, 0.015), rough=0.6)
        lip = s.get('lips') or (tuple(c * 0.55 for c in s['skin']) if s.get('beard') in ('full', 'long_white') else tuple(c * 0.72 for c in s['skin']))
        M['lip'] = C.mat(f'{self.name}_lip', lip, rough=0.35, sss=0.2)
        M['kohl'] = C.mat('kohl', (0.01, 0.008, 0.008), rough=0.7)
        M['gold'] = C.mat('gold', (0.85, 0.58, 0.18), rough=0.25, metal=1.0)
        M['silver'] = C.mat('silver', (0.8, 0.8, 0.82), rough=0.2, metal=1.0)
        M['teeth'] = C.mat('teeth', (0.85, 0.82, 0.74), rough=0.3)
        return M

    def _cloth_mat(self, name, col, check):
        m = C.mat(name, col, rough=0.85, noise=0.2, noise_scale=160, sheen=0.4)
        if check:  # woven check pattern (lungi)
            nt = m.node_tree; p = nt.nodes.get('Principled BSDF')
            tc = nt.nodes.new('ShaderNodeTexCoord'); wv1 = nt.nodes.new('ShaderNodeTexWave'); wv2 = nt.nodes.new('ShaderNodeTexWave')
            for wv, dirn in ((wv1, 'X'), (wv2, 'Z')):
                wv.wave_type = 'BANDS'; wv.bands_direction = dirn; wv.inputs['Scale'].default_value = 9
                wv.wave_profile = 'SIN'
                nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
            mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
            nt.links.new(wv1.outputs['Fac'], mx.inputs[0]); nt.links.new(wv2.outputs['Fac'], mx.inputs[1])
            gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.82
            nt.links.new(mx.outputs[0], gt.inputs[0])
            mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
            prev = p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].links else None
            if prev: nt.links.new(prev, mix.inputs[6])
            else: mix.inputs[6].default_value = (*col, 1)
            mix.inputs[7].default_value = (*check, 1)
            nt.links.new(gt.outputs[0], mix.inputs['Factor']); nt.links.new(mix.outputs[2], p.inputs['Base Color'])
        return m

    # ---------------------------------------------------------------- body
    def _body(self):
        s = self.s; J = self.J; H = self.H; b = s.get('build', 1.0); fem = s.get('female', False)
        V, E, R = [], [], []
        def v(p, rx, ry=None):
            V.append(tuple(p)); R.append((rx * H, (ry if ry else rx) * H)); return len(V) - 1
        z = lambda f: H * f
        fm = 1.12 if fem else 1.0
        hipc = v((0, 0, z(0.505)), 0.084 * b * fm, 0.062 * b)
        pel = v((0, 0, z(0.545)), 0.087 * b * fm, 0.064 * b)
        wai = v((0, 0.002, z(0.605)), 0.079 * b * (0.84 if fem else 1), 0.058 * b + (0.008 if b > 1.08 else 0))
        bel = v((0, 0.002, z(0.655)), 0.085 * b * (0.88 if fem else 1), 0.062 * b)
        che = v((0, -0.002, z(0.705)), 0.098 * b * (0.9 if fem else 1), 0.070 * b * (1.06 if fem else 1))
        upc = v((0, 0.006, z(0.752)), 0.096 * b * (0.86 if fem else 1), 0.064 * b)
        nk0 = v(J['neck0'] + Vector((0, 0, -0.008 * H)), 0.046 * (b ** 0.5) * (0.8 if fem else 1))
        nk1 = v(J['neck1'] + Vector((0, 0, 0.012 * H)), 0.033 * (b ** 0.5) * (0.82 if fem else 1))
        for a, c in ((hipc, pel), (pel, wai), (wai, bel), (bel, che), (che, upc), (upc, nk0), (nk0, nk1)): E.append((a, c))
        af = 0.84 if fem else 1.0
        for sd in ('L', 'R'):
            sh = v(J[f'sh.{sd}'] + Vector((0, 0, -0.006 * H)), 0.046 * b ** 0.8 * af); E.append((upc, sh))
            mid = v(J[f'sh.{sd}'].lerp(J[f'el.{sd}'], 0.42), 0.043 * b ** 0.8 * af); E.append((sh, mid))
            el = v(J[f'el.{sd}'], 0.032 * b ** 0.6 * af); E.append((mid, el))
            fa = v(J[f'el.{sd}'].lerp(J[f'wr.{sd}'], 0.32), 0.034 * b ** 0.6 * af); E.append((el, fa))
            wr = v(J[f'wr.{sd}'], 0.022 * b ** 0.5 * af); E.append((fa, wr))
            hp = v(J[f'hip.{sd}'] + Vector((0, 0, 0.012 * H)), 0.064 * b * (1.06 if fem else 1)); E.append((hipc, hp))
            th = v(J[f'hip.{sd}'].lerp(J[f'kn.{sd}'], 0.42), 0.060 * b * (1.02 if fem else 1)); E.append((hp, th))
            kn = v(J[f'kn.{sd}'], 0.042 * b ** 0.8); E.append((th, kn))
            cf = v(J[f'kn.{sd}'].lerp(J[f'an.{sd}'], 0.3) + Vector((0, 0.012 * H, 0)), 0.046 * b ** 0.8); E.append((kn, cf))
            an = v(J[f'an.{sd}'] + Vector((0, 0, 0.006 * H)), 0.026 * b ** 0.6); E.append((cf, an))
        body = _skin_mesh(f'{self.name}_body', V, E, R, root=hipc)
        body.modifiers[-1].levels = 3; body.modifiers[-1].render_levels = 3
        C.apply_mods(body)
        C.assign(body, self.mats['skin'], self.mats['shirt'], self.mats['lower'])
        self.body = body
        self.sleeve_t = {'none': 0.0, 'short': 0.5, 'elbow': 0.95, 'forearm': 1.55, 'full': 2.05}[s['sleeve']]
        vneck = s.get('vneck', 0)
        lower_kind = s['lower']
        self.v_apex = H * (0.785 - 0.11 * vneck)
        for p in body.data.polygons:
            c = p.center; ax = abs(c.x); shx = abs(J['sh.L'].x)
            if ax > shx * 0.82 and c.z > H * 0.45 and c.z < H * 0.84:
                d = self._arm_param(Vector((ax, c.y, c.z)))
                mi = 1 if d < self.sleeve_t else 0
            elif c.z > H * 0.795 and ax < 0.06 * H:
                mi = 0
            elif c.z > H * 0.505:
                mi = 1
                if vneck and c.y < 0 and c.z > self.v_apex and ax < (c.z - self.v_apex) * 0.75: mi = 0
                if s.get('open_vest') and c.y < -0.01 * H and ax < 0.05 * H: mi = 0
            else:
                covered = lower_kind in ('dhoti', 'langa') or (lower_kind in ('lungi_knee', 'coat') and c.z > J['kn.L'].z + 0.02 * H)
                mi = 2 if (lower_kind == 'pants' or covered) else 0
            p.material_index = mi
        C.parent_keep(body, self.arm)
        bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); self.arm.select_set(True)
        bpy.context.view_layer.objects.active = self.arm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        self.parts.append(body)
        self._trims()
        self._lower_garment()

    def _arm_param(self, p):
        """0 at shoulder, 1 at elbow, 2 at wrist (left-side coords)."""
        J = self.J
        a, e, w = J['sh.L'], J['el.L'], J['wr.L']
        def proj(p, a, b):
            d = b - a; t = max(0, min(1, (p - a).dot(d) / d.length_squared)); return t, (a + d * t - p).length
        t1, d1 = proj(p, a, e); t2, d2 = proj(p, e, w)
        return t1 if d1 <= d2 else 1 + t2

    def _surface_ring(self, center, axis, n=24, push=0.002):
        """ray-cast the body around an axis to get a ring hugging the surface."""
        axis = axis.normalized(); u = axis.orthogonal().normalized(); w = axis.cross(u)
        pts = []
        for k in range(n):
            a = 2 * math.pi * k / n; d = u * math.cos(a) + w * math.sin(a)
            hit, loc, nor, idx = self.body.ray_cast(center, d, distance=0.4)
            pts.append(loc + d * push if hit else None)
        good = [p for p in pts if p is not None]
        rad = sorted((p - center).length for p in good)[len(good) // 2] if good else 0.05
        out = []
        for k, p in enumerate(pts):  # reject outliers (rays that escaped into another limb)
            a = 2 * math.pi * k / n; d = u * math.cos(a) + w * math.sin(a)
            out.append(p if p is not None and (p - center).length < rad * 1.5 else center + d * rad)
        return out

    def _ring_mesh(self, name, pts, r, mat, bone):
        o = C.tube(name, pts + pts[:2], r, res=8); C.assign(o, mat)
        C.parent_keep(o, self.arm, bone); self.parts.append(o); return o

    def _trims(self):
        s = self.s; H = self.H; J = self.J
        shirt = self.mats['shirt']
        if 0 < self.sleeve_t < 2.0:
            for sd in ('L', 'R'):
                t = self.sleeve_t
                if t <= 1: c = J[f'sh.{sd}'].lerp(J[f'el.{sd}'], t); ax = J[f'el.{sd}'] - J[f'sh.{sd}']; bone = f'upperarm.{sd}'
                else: c = J[f'el.{sd}'].lerp(J[f'wr.{sd}'], t - 1); ax = J[f'wr.{sd}'] - J[f'el.{sd}']; bone = f'forearm.{sd}'
                self._ring_mesh(f'{self.name}_cuff{sd}', self._surface_ring(c, ax), 0.011 * H, shirt, bone)
        elif self.sleeve_t == 0:
            for sd in ('L', 'R'):
                c = J[f'sh.{sd}'].lerp(J[f'el.{sd}'], 0.05)
                self._ring_mesh(f'{self.name}_arm{sd}', self._surface_ring(c, J[f'el.{sd}'] - J[f'sh.{sd}']), 0.008 * H, shirt, 'chest')
        if s['lower'] == 'langa':
            return
        vneck = s.get('vneck', 0)
        if s.get('open_vest'):
            for sx in (1, -1):
                line = []
                for i in range(12):
                    zz = H * (0.80 - 0.27 * i / 11)
                    hit, loc, nor, idx = self.body.ray_cast(Vector((sx * 0.05 * H, -0.5, zz)), Vector((0, 1, 0)))
                    if hit: line.append(loc + nor * 0.004 * H)
                if len(line) > 2:
                    ed = C.tube('vestedge', line, 0.009 * H, res=8); C.assign(ed, shirt); C.parent_keep(ed, self.arm, 'chest'); self.parts.append(ed)
        else:
            nk = self._surface_ring(J['neck0'] + Vector((0, 0.004 * H, -0.004 * H)), Vector((0, 0.2, 1)), n=28)
            if vneck:
                nk = [p for p in nk if p.y > -0.012 * H or abs(p.x) > 0.032 * H]
                # order the open collar from left front around the back to right front
                nk.sort(key=lambda p: math.atan2(p.y, p.x) % (2 * math.pi))
                for sx in (1, -1):
                    line = []
                    for i in range(9):
                        t = i / 8
                        zz = H * 0.795 + (self.v_apex - H * 0.795) * t
                        xx = sx * ((zz - self.v_apex) * 0.75 + 0.003 * H)
                        hit, loc, nor, idx = self.body.ray_cast(Vector((xx, -0.5, zz)), Vector((0, 1, 0)))
                        if hit: line.append(loc + nor * 0.004 * H)
                    if len(line) > 2:
                        lap = C.tube(f'{self.name}_lapel', line, 0.010 * H, taper=lambda t: 1.3 - 0.5 * t, res=8); C.assign(lap, shirt)
                        C.parent_keep(lap, self.arm, 'chest'); self.parts.append(lap)
                if len(nk) > 4:
                    col = C.tube(f'{self.name}_collar', nk, 0.008 * H, res=8); C.assign(col, shirt)
                    C.parent_keep(col, self.arm, 'chest'); self.parts.append(col)
            else:
                col = C.tube(f'{self.name}_collar', nk + nk[:2], 0.008 * H, res=8); C.assign(col, shirt)
                C.parent_keep(col, self.arm, 'chest'); self.parts.append(col)
        if False:
            ring = self._surface_ring(Vector((0, 0, H * 0.545)), Vector((0, 0, 1)), n=32)
            n = len(ring)
            outer = [Vector((p.x, p.y, 0)).normalized() for p in ring]
            verts = [p + Vector((0, 0, 0.06 * H)) + d * 0.002 * H for p, d in zip(ring, outer)] + [p + d * 0.016 * H for p, d in zip(ring, outer)]
            faces = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
            o = C.mesh_obj(f'{self.name}_hem', verts, faces); C.add_mod(o, 'SOLIDIFY', thickness=0.004 * H); C.assign(o, shirt)
            C.parent_keep(o, self.arm, 'hips'); self.parts.append(o)

    def _lower_garment(self):
        s = self.s; H = self.H; kind = s['lower']; b = s.get('build', 1.0); fem = s.get('female', False)
        if kind == 'pants': return
        top, bot = H * 0.565, {'lungi_knee': H * 0.30, 'dhoti': H * 0.075, 'langa': H * 0.022, 'coat': H * 0.28}[kind]
        r_top = 0.096 * b * H * (1.12 if fem else 1.0)
        r_bot = {'lungi_knee': 0.12, 'dhoti': 0.13, 'langa': 0.19, 'coat': 0.14}[kind] * H * (b ** 0.5)
        rings, segn = 16, 40
        verts, faces, wts = [], [], []
        ring0 = self._surface_ring(Vector((0, 0, top)), Vector((0, 0, 1)), n=segn)
        hipring = self._surface_ring(Vector((0, 0, H * 0.50)), Vector((0, 0, 1)), n=segn)
        rx0 = max(abs(p.x) for p in ring0) + 0.004 * H; ry0 = max(abs(p.y) for p in ring0) + 0.004 * H
        rxh = max(abs(self.J['hip.L'].x) + 0.066 * b * H + 0.014 * H, rx0); ryh = max(0.066 * b * H + 0.018 * H, ry0)
        for i in range(rings + 1):
            t = i / rings; zz = top + (bot - top) * t
            fl = (r_bot / r_top) if kind != 'lungi_knee' else 1.12
            kx = (rx0 + (max(rxh, rx0) - rx0) * C.ease(min(1, t / 0.4), 'smooth')) * (1 + (fl - 1) * max(0, t - 0.3) / 0.7)
            ky = (ry0 + (max(ryh, ry0) - ry0) * C.ease(min(1, t / 0.4), 'smooth')) * (1 + (fl - 1) * max(0, t - 0.3) / 0.7) * (1.0 + (0.25 if kind == 'langa' else 0.06) * min(1, t / 0.4))
            for k in range(segn):
                a = 2 * math.pi * k / segn
                x = math.cos(a) * kx; y = math.sin(a) * ky; r = kx
                # gentle folds
                fold = 1 + (0.03 * math.sin(a * 11 + t * 2) + 0.02 * math.sin(a * 5 + 1.3)) * (0.3 + t)
                verts.append((x * fold, y * fold, zz)); wts.append((t, x / r))
        for i in range(rings):
            for k in range(segn):
                a = i * segn + k; bb = i * segn + (k + 1) % segn
                faces.append((a, bb, bb + segn, a + segn))
        o = C.mesh_obj(f'{self.name}_lower', verts, faces)
        C.add_mod(o, 'SOLIDIFY', thickness=0.006, offset=1)
        C.assign(o, self.mats['lower'])
        if kind == 'coat': C.assign(o, self.mats['shirt'])
        C.parent_keep(o, self.arm)
        md = o.modifiers.new('arm', 'ARMATURE'); md.object = self.arm
        o.modifiers.move(len(o.modifiers) - 1, 0)
        gh = o.vertex_groups.new(name='hips'); gl = o.vertex_groups.new(name='thigh.L'); gr = o.vertex_groups.new(name='thigh.R')
        gsl = o.vertex_groups.new(name='shin.L'); gsr = o.vertex_groups.new(name='shin.R')
        knee_z = self.J['kn.L'].z
        for i, (t, side) in enumerate(wts):
            zz = top + (bot - top) * t
            sl = 0.5 + 0.5 * max(-1, min(1, side * 1.6))
            if zz >= knee_z:
                f = C.ease(min(1.0, (top - zz) / max(1e-3, (top - knee_z) * 0.55)), 'smooth')
                gh.add([i], 1 - f, 'REPLACE'); gl.add([i], f * sl, 'REPLACE'); gr.add([i], f * (1 - sl), 'REPLACE')
            else:
                g = C.ease(min(1.0, (knee_z - zz) / (0.12 * H)), 'smooth') * 0.85
                gh.add([i], 0.0, 'REPLACE')
                gl.add([i], (1 - g) * sl, 'REPLACE'); gr.add([i], (1 - g) * (1 - sl), 'REPLACE')
                gsl.add([i], g * sl, 'REPLACE'); gsr.add([i], g * (1 - sl), 'REPLACE')
        # rolled waistband closing the top edge
        roll = [Vector((math.cos(2 * math.pi * k / 40) * (rx0 + 0.005 * H), math.sin(2 * math.pi * k / 40) * (ry0 + 0.005 * H), top + 0.004 * H)) for k in range(40)]
        rl = C.tube(f'{self.name}_roll', roll + roll[:2], 0.011 * H, res=8); C.assign(rl, self.mats['lower'] if kind != 'coat' else self.mats['shirt'])
        C.parent_keep(rl, self.arm, 'hips'); self.parts.append(rl)
        # waist knot / tuck
        knot = C.ellipsoid(f'{self.name}_knot', 0.022 * H, 0.012 * H, 0.018 * H, loc=(0.02 * H, -(ry0 + 0.008 * H) * 1.08, top - 0.008 * H))
        C.assign(knot, self.mats['lower'] if kind != 'coat' else self.mats['shirt'])
        C.parent_keep(knot, self.arm, 'hips')
        self.parts += [o, knot]
        if kind == 'langa':  # gold border
            band = C.prim('torus', f'{self.name}_border', loc=(0, 0, bot + 0.012 * H), major_radius=r_bot * 0.98, minor_radius=0.008 * H)
            band.scale = (1, 0.85, 1); C.assign(band, self.mats['gold']); C.parent_keep(band, o)
            band.modifiers.new('arm', 'ARMATURE').object = self.arm
            for nm in ('thigh.L', 'thigh.R'):
                g = band.vertex_groups.new(name=nm)
            for vtx in band.data.vertices:
                sl = 0.5 + 0.5 * max(-1, min(1, vtx.co.x / r_bot * 1.6))
                band.vertex_groups['thigh.L'].add([vtx.index], 0.75 * sl, 'REPLACE'); band.vertex_groups['thigh.R'].add([vtx.index], 0.75 * (1 - sl), 'REPLACE')
                band.vertex_groups.new(name='hips') if 'hips' not in band.vertex_groups else None
                band.vertex_groups['hips'].add([vtx.index], 0.25, 'REPLACE')
            band.parent = self.arm

    # ---------------------------------------------------------------- head & face
    def _head(self):
        s = self.s; H = self.H; J = self.J
        hh = H / 5.95 * (1.04 if s.get('female') else 1.0)
        rx, ry, rz = hh * 0.385, hh * 0.44, hh * 0.52
        self.hr = (rx, ry, rz)
        hc = Vector((0, J['neck1'].y - 0.004 * H, J['neck1'].z + rz * 0.80))
        self.hc = hc
        shape, surf = _surface_fn(rx, ry, rz, s.get('jaw', 0.3), 0.12)
        self.surf = surf
        head = C.ellipsoid(f'{self.name}_head', rx, ry, rz, seg=48, rings=32, shape=shape)
        head.location = hc; C.assign(head, self.mats['skin']); C.subsurf(head, 1)
        parts = [head]
        def at(x, z, out=0.0):  # head-local front surface point
            return Vector((x, surf(x, z) - out, z))
        self.at = at
        # nose
        nz = -rz * 0.10
        nose = C.ellipsoid(f'{self.name}_nose', rx * 0.17, ry * 0.17, rz * 0.13, loc=at(0, nz, -ry * 0.05))
        nose.location += hc; C.assign(nose, self.mats['skin']); parts.append(nose)
        bridge = C.ellipsoid(f'{self.name}_bridge', rx * 0.085, ry * 0.1, rz * 0.15, loc=at(0, nz + rz * 0.12, -ry * 0.02))
        bridge.location += hc; C.assign(bridge, self.mats['skin']); parts.append(bridge)
        for sx in (1, -1):
            nos = C.ellipsoid(f'{self.name}_nostril', rx * 0.08, ry * 0.1, rz * 0.08, loc=at(sx * rx * 0.1, nz - rz * 0.06, -ry * 0.04))
            nos.location += hc; C.assign(nos, self.mats['skin']); parts.append(nos)
            # ears
            es = s.get('ears', 1.0)
            ear = C.ellipsoid(f'{self.name}_ear', rx * 0.07, ry * 0.15 * es, rz * 0.2 * es, loc=hc + Vector((sx * rx * 0.97, ry * 0.08, -rz * 0.05)))
            ear.rotation_euler = (0, 0, sx * math.radians(-18)); C.assign(ear, self.mats['skin']); parts.append(ear)
            if s.get('earrings'):
                er = C.prim('torus', 'earring', loc=hc + Vector((sx * rx * 1.0, ry * 0.05, -rz * 0.33)), major_radius=rx * 0.07, minor_radius=rx * 0.015, rotation=(0, math.pi / 2, 0))
                C.assign(er, self.mats['gold']); parts.append(er)
        head_obj = C.join(parts, f'{self.name}_head')
        bpy.context.view_layer.update()
        C.parent_keep(head_obj, self.arm, 'head'); self.parts.append(head_obj); self.head = head_obj
        self._eyes(hc, rx, ry, rz, at)
        self._brows(hc, rx, ry, rz, at)
        beard_out = self._beard(hc, rx, ry, rz)
        self._mouth(hc, rx, ry, rz, beard_out)
        self._hair(hc, rx, ry, rz)
        self._head_acc(hc, rx, ry, rz, at)

    def _bone_parent(self, o, bone='head'):
        C.parent_keep(o, self.arm, bone); self.parts.append(o); return o

    def _eyes(self, hc, rx, ry, rz, at):
        s = self.s; ez = rz * 0.12; ex = rx * 0.37; er = rx * 0.175 * (1.12 if s.get('female') else 1)
        for sd, sx in (('L', 1), ('R', -1)):
            ctr = hc + at(sx * ex, ez, -0.0) + Vector((0, er * 0.72, 0))
            piv = C.empty(f'{self.name}_eye{sd}', ctr)
            parts = []
            w = C.ellipsoid('ew', er, er, er, seg=24, rings=12); C.assign(w, self.mats['white']); parts.append(w)
            ir = C.ellipsoid('ir', er * 0.58, er * 0.2, er * 0.58, loc=(0, -er * 0.88, 0), seg=24, rings=12); C.assign(ir, self.mats['iris']); parts.append(ir)
            pu = C.ellipsoid('pu', er * 0.3, er * 0.1, er * 0.3, loc=(0, -er * 1.0, 0), seg=16, rings=8); C.assign(pu, self.mats['pupil']); parts.append(pu)
            gl = C.ellipsoid('gl', er * 0.07, er * 0.03, er * 0.07, loc=(er * 0.2, -er * 1.03, er * 0.2), seg=8, rings=6); C.assign(gl, self.mats['glint']); parts.append(gl)
            eye = C.join(parts, f'{self.name}_eyeball{sd}'); eye.location = (0, 0, 0)
            eye.parent = piv
            # lids: upper (rotates to blink) and lower
            lid = self._lid(f'{self.name}_lidU{sd}', er * 1.08, upper=True)
            lidp = C.empty(f'{self.name}_lidpiv{sd}', ctr); lid.parent = lidp
            low = self._lid(f'{self.name}_lidD{sd}', er * 1.06, upper=False); low.parent = lidp
            low.rotation_euler = (math.radians(62), 0, 0)
            for o in (piv, lidp): self._bone_parent(o)
            self.face[f'eye{sd}'] = eye; self.face[f'lid{sd}'] = lid; self.face[f'lidpiv{sd}'] = lidp
        self.er = er

    def _lid(self, name, r, upper):
        verts, faces = [], []
        rings, segn = 8, 24
        for i in range(rings + 1):
            th = (math.pi / 2) * i / rings
            for k in range(segn + 1):
                ph = math.pi * k / segn
                x = r * math.cos(ph) * math.sin(th + 0.01) if True else 0
                # hemisphere cap facing up (upper) or down
                xx = r * math.cos(ph) * math.sin(th)
                yy = -r * math.sin(ph) * math.sin(th)
                zz = r * math.cos(th) * (1 if upper else -1)
                verts.append((xx, yy * 1.02, zz))
        for i in range(rings):
            for k in range(segn):
                a = i * (segn + 1) + k
                faces.append((a, a + 1, a + segn + 2, a + segn + 1) if upper else (a, a + segn + 1, a + segn + 2, a + 1))
        o = C.mesh_obj(name, verts, faces)
        C.add_mod(o, 'SOLIDIFY', thickness=r * 0.12, offset=1)
        C.assign(o, self.mats['skin'], self.mats['kohl'])
        for p in o.data.polygons:
            if p.center.length > 0 and abs(p.center.z) < r * 0.22 and p.center.y < 0: p.material_index = 1 if (self.s.get('kohl') or upper) else 0
        # upper lid rest: we rotate the lid pivot later; base orientation = half open (cap covers top half)
        return o

    def _brows(self, hc, rx, ry, rz, at):
        s = self.s; bz = rz * 0.30; bx = rx * 0.37; th = s.get('brow', 1.0) * 1.25
        col = self.mats['hair'] if s.get('age') is None else C.mat('whitebrow', (0.8, 0.79, 0.76), rough=0.6)
        for sd, sx in (('L', 1), ('R', -1)):
            pts = []
            for i in range(9):
                t = i / 8; x = sx * (bx - rx * 0.2 + rx * 0.42 * t)
                z = bz + rz * 0.05 * math.sin(t * math.pi) - rz * 0.02 * t
                pts.append(Vector((x - sx * bx, surf_y(self, x, z) - ry * 0.02 - 0.0, z - bz)))
            b = C.tube(f'{self.name}_brow{sd}', pts, rx * 0.045 * th, taper=lambda t: 0.6 + 0.5 * math.sin(min(1, t * 1.3) * math.pi * 0.8) , res=8)
            C.assign(b, col)
            piv = C.empty(f'{self.name}_browpiv{sd}', hc + Vector((sx * bx, 0, bz)))
            b.parent = piv; b.location = (0, 0, 0)
            self._bone_parent(piv)
            self.face[f'brow{sd}'] = b

    def _mouth(self, hc, rx, ry, rz, out):
        s = self.s; mz = -rz * 0.40; W = rx * (0.36 if not s.get('female') else 0.30); Ht = rz * 0.16
        N = 28
        def outline(w=1.0, o=0.06, sm=0.0, rnd=0.0):
            pts = []
            for k in range(N):
                th = 2 * math.pi * k / N
                cx, sy = math.cos(th), math.sin(th)
                x = cx * W * w * (1 - 0.35 * rnd * (1 - abs(sy)))
                up = sy > 0
                y = sy * Ht * o * (0.55 if up else 1.0) * (1 + 0.6 * rnd)
                y += sm * Ht * 0.55 * (cx * cx) - sm * Ht * 0.18
                pts.append((x, y))
            return pts
        def build(pts):
            co = []
            for (x, y) in pts: co.append(Vector((x, 0, y)))
            for (x, y) in pts: co.append(Vector((x * 0.78, 0, y * 0.70)))
            co.append(Vector((sum(p[0] for p in pts) / N, 0, sum(p[1] for p in pts) / N)))
            res = []
            for v in co:
                xx, zz = v.x, mz + v.z
                yy = self.surf(xx, zz) - out - ry * 0.012
                res.append(Vector((xx, yy, zz)))
            return res
        base = build(outline())
        faces = []
        for k in range(N):
            a, b = k, (k + 1) % N
            faces.append((a, b, N + b, N + a))
        for k in range(N): faces.append((N + k, N + (k + 1) % N, 2 * N))
        o = C.mesh_obj(f'{self.name}_mouth', [hc + v for v in base], faces)
        C.assign(o, self.mats['lip'], self.mats['mouth'])
        for i, p in enumerate(o.data.polygons): p.material_index = 0 if i < N else 1
        o.shape_key_add(name='Basis')
        for nm, kw in (('open', dict(o=1.0)), ('wide', dict(w=1.3, o=0.3)), ('smile', dict(sm=1.0, w=1.08)),
                       ('frown', dict(sm=-1.0, w=0.92)), ('O', dict(w=0.62, o=0.85, rnd=1.0)), ('grin', dict(sm=0.8, w=1.25, o=0.55))):
            k = o.shape_key_add(name=nm)
            for i, v in enumerate(build(outline(**kw))): k.data[i].co = hc + v
        C.add_mod(o, 'SOLIDIFY', thickness=rx * 0.02, offset=1)
        # teeth strip (shows when open)
        t = C.ellipsoid(f'{self.name}_teeth', W * 0.62, rx * 0.03, Ht * 0.18, loc=hc + Vector((0, self.surf(0, mz + Ht * 0.12) - out + rx * 0.02, mz + Ht * 0.12)))
        C.assign(t, self.mats['teeth'])
        self._bone_parent(t)
        self._bone_parent(o); self.face['mouth'] = o; self.face['teeth'] = t
        self.mouth_info = (mz, W, Ht, out)
        ms = s.get('mustache')
        if ms:
            th = {'thick': 0.09, 'trim': 0.045, 'police': 0.085, 'white': 0.08, 'thin': 0.028}[ms]
            pts = []
            span = {'thick': 1.35, 'trim': 1.1, 'police': 1.45, 'white': 1.4, 'thin': 1.15}[ms]
            for i in range(13):
                tt = i / 12; x = (tt - 0.5) * 2 * W * span
                droop = (abs(tt - 0.5) * 2) ** 2 * (rz * 0.1 if ms in ('thick', 'white') else rz * 0.03)
                if ms == 'police': droop = -(abs(tt - 0.5) * 2) ** 3 * rz * 0.05
                z = mz + Ht * 0.75 + rz * 0.035 - droop
                pts.append(Vector((x, self.surf(x, z) - out - rx * 0.03, z)))
            m = C.tube(f'{self.name}_mustache', [hc + p for p in pts], rx * th, taper=lambda t: 0.35 + 0.75 * math.sin(t * math.pi), res=10)
            col = self.mats['hair'] if ms != 'white' else C.mat('whitehair', (0.78, 0.77, 0.74), rough=0.55, noise=0.3, noise_scale=300)
            C.assign(m, col); self._bone_parent(m)

    def _beard(self, hc, rx, ry, rz):
        """Parametric beard patch: smooth curved top edge (no jaggies), thickness fading in from the edge."""
        s = self.s; kind = s.get('beard')
        if not kind: return 0.0
        thick = {'full': 0.075, 'stubble': 0.008, 'long_white': 0.09}[kind]
        shape, _ = _surface_fn(rx, ry, rz, s.get('jaw', 0.3), 0.12)
        A = math.radians(100 if kind != 'stubble' else 92)
        NU, NV = 72, 30
        verts, faces = [], []
        for i in range(NU + 1):
            du = -A + 2 * A * i / NU; ph = -math.pi / 2 + du; a = abs(du) / math.radians(90)
            # top edge (polar angle): under the nose at the centre, cheek line, rising to the sideburns
            th_top = math.radians(104 - 26 * min(1.2, a) ** 2 + 7 * math.sin(min(1, a) * math.pi) - (4 if kind == 'stubble' else 0))
            th_bot = math.radians(168 if kind != 'long_white' else 172)
            for j in range(NV + 1):
                v = j / NV
                th = th_top + (th_bot - th_top) * v
                x, y, z = rx * math.sin(th) * math.cos(ph), ry * math.sin(th) * math.sin(ph), rz * math.cos(th)
                x, y, z = shape(x, y, z)
                edge = min(1.0, v / 0.12) * min(1.0, (A - abs(du)) / math.radians(10))
                k = 1 + thick * (0.25 + 0.75 * edge) * (1 + 0.6 * max(0, -z / rz))
                p = Vector((x * k, y * k, z * k))
                if kind == 'long_white' and z < -rz * 0.5 and y < 0:
                    p.z -= rz * 0.55 * ((-z / rz) - 0.5) / 0.5 * (1 - abs(du) / A)
                verts.append(p)
        for i in range(NU):
            for j in range(NV):
                a0 = i * (NV + 1) + j; b0 = (i + 1) * (NV + 1) + j
                faces.append((a0, a0 + 1, b0 + 1, b0))
        o = C.mesh_obj(f'{self.name}_beard', [hc + v for v in verts], faces)
        tex = bpy.data.textures.new(f'{self.name}_beardtex', 'CLOUDS'); tex.noise_scale = 0.006; tex.noise_depth = 3
        if kind != 'stubble':
            C.add_mod(o, 'DISPLACE', texture=tex, strength=rx * 0.035, mid_level=0.5)
        C.add_mod(o, 'SOLIDIFY', thickness=rx * 0.03, offset=-1)
        C.subsurf(o, 1)
        if kind == 'long_white': col = C.mat('whitehair', (0.72, 0.71, 0.68), rough=0.85, spec=0.2, noise=0.45, noise_scale=400)
        elif kind == 'stubble': col = C.mat(f'{self.name}_stubble', tuple(c * 0.62 for c in s['skin']), rough=0.95, spec=0.15, noise=0.7, noise_scale=900)
        else: col = C.mat(f'{self.name}_beardmat', (0.026, 0.019, 0.014), rough=0.95, spec=0.2, noise=0.6, noise_scale=500, sheen=0.3)
        C.assign(o, col)
        self._bone_parent(o)
        self.beard_mat = col
        # how far the beard surface sits in front of the skin at the mouth
        return ry * thick * (1.0 if kind != 'stubble' else 1.0) + rx * 0.03

    def _clump(self, hc, rx, ry, rz, th0, ph, th1, r0, r1, rad, wave=0.0, seed=0, flare=0.0, droop=0.0):
        """hair clump swept over the head: polar angle th0->th1 at azimuth ph (radians), radius scale r0->r1."""
        pts = []
        n = 12
        for i in range(n):
            t = i / (n - 1)
            th = th0 + (th1 - th0) * t
            rr = r0 + (r1 - r0) * t
            p = Vector((math.sin(th) * math.cos(ph) * rx * rr * (1 + flare * t), math.sin(th) * math.sin(ph) * ry * rr, math.cos(th) * rz * rr))
            p.z -= droop * rz * max(0, t - 0.5) ** 2 * 4
            p += Vector((math.cos(ph + 1.57), math.sin(ph + 1.57), 0)) * wave * rx * math.sin(t * 9 + seed)
            pts.append(hc + p)
        return C.tube('clump', pts, rad, taper=lambda t: (0.55 + 0.6 * math.sin(min(1, t * 1.6 + 0.15) * 2.4)) * (1 - 0.65 * t ** 2), res=7)

    def _hair(self, hc, rx, ry, rz):
        s = self.s; kind = s['hair']; M = self.mats['hair']
        shape, _ = _surface_fn(rx, ry, rz, s.get('jaw', 0.3), 0.12)
        def cap(name, scale, mask, disp=0.03):
            def sh(x, y, z):
                x, y, z = shape(x, y, z)
                return x * scale, y * scale, z * scale + rz * 0.015
            o = C.ellipsoid(name, rx, ry, rz, seg=56, rings=36, shape=sh); o.location = hc
            bm = bmesh.new(); bm.from_mesh(o.data)
            kill = [f for f in bm.faces if not mask(f.calc_center_median())]
            bmesh.ops.delete(bm, geom=kill, context='FACES'); bm.to_mesh(o.data); bm.free()
            C.add_mod(o, 'SOLIDIFY', thickness=rx * 0.05, offset=-1)
            tex = bpy.data.textures.new(name + 'tx', 'CLOUDS'); tex.noise_scale = 0.03; tex.noise_depth = 2
            C.add_mod(o, 'DISPLACE', texture=tex, strength=rx * disp, mid_level=0.45)
            C.subsurf(o, 1); C.assign(o, M); self._bone_parent(o)
            return o
        r = C.rng(sum(ord(ch) * (i + 1) for i, ch in enumerate(self.key)))
        hairline = lambda c: c.z > rz * 0.38 + (-c.y / ry) * rz * 0.10 if c.y < 0 else c.z > -rz * 0.2 + (abs(c.x) / rx) * rz * 0.3
        clumps = []
        def comb(x, u1, scale, rad, fall=0.0, jitter=0.0, seed=0, u0=None):
            k = math.sqrt(max(0.04, 1 - (x / rx) ** 2))
            if u0 is None:
                zl = rz * 0.40
                u0 = math.asin(min(0.99, zl / (rz * k * scale))) if zl < rz * k * scale else 1.3
            pts = []
            for i in range(14):
                t = i / 13; u = (u0 + 0.06) + (u1 - u0 - 0.06) * t
                j = jitter * rx * math.sin(t * 7 + seed)
                sc_ = 0.99 + (scale - 0.99) * min(1.0, t / 0.25)
                pts.append(hc + Vector((x * (1 + 0.10 * t) + j, -ry * k * math.cos(u) * sc_, rz * k * math.sin(u) * sc_)))
            if fall:
                last = pts[-1]
                for j in range(1, 7):
                    f = j / 6
                    pts.append(last + Vector((x * 0.12 * f, ry * 0.06 * f, -fall * f)) + Vector((jitter * rx * math.sin(f * 5 + seed), 0, 0)))
            return C.tube('clump', pts, rad, taper=lambda t: min(1.0, 0.5 + t * 3.0) * (1 - 0.6 * t ** 2), res=7)
        def hairline_roll(scale=1.06, rad=0.13, z0=0.40):
            pts = []
            for i in range(25):
                u = math.radians(-150 + 300 * i / 24); ph = -math.pi / 2 + u * 0.55
                k = 1.0
                zz = rz * (z0 + 0.10 * (abs(u) / math.radians(150)) ** 2 * -1.0 - 0.05)
                xx = math.cos(ph) * rx * scale * math.sqrt(max(0.05, 1 - (zz / (rz * scale)) ** 2))
                yy = math.sin(ph) * ry * scale * math.sqrt(max(0.05, 1 - (zz / (rz * scale)) ** 2))
                pts.append(hc + Vector((xx, yy, zz + rz * 0.04)))
            o = C.tube('roll', pts, rx * rad, taper=lambda t: 0.55 + 0.45 * math.sin(t * math.pi), res=10)
            return o
        if kind in ('short', 'messy'):
            cap(f'{self.name}_scalp', 1.03, lambda c: hairline(c) and not (abs(c.x) > rx * 0.85 and c.z < rz * 0.45))
            n = 22 if kind == 'short' else 26
            for layer in range(2):
                for i in range(n):
                    x = (i / (n - 1) - 0.5) * 2 * rx * 0.9 + r.uniform(-0.02, 0.02) * rx
                    clumps.append(comb(x, math.pi * (0.92 + 0.06 * layer), 1.07 + 0.04 * layer, rx * r.uniform(0.14, 0.18),
                                       jitter=0.05 if kind == 'messy' else 0.012, seed=i + layer * 7))
        elif kind == 'long':
            cap(f'{self.name}_scalp', 1.03, lambda c: hairline(c) or c.y > 0)
            for layer in range(3):
                n = (24, 20, 16)[layer]
                for i in range(n):
                    x = (i / (n - 1) - 0.5) * 2 * rx * (0.96 - 0.05 * layer) + r.uniform(-0.03, 0.03) * rx
                    fall = rz * (1.05 + 0.25 * layer) * (1 - 0.35 * abs(x) / rx) * r.uniform(0.85, 1.1)
                    clumps.append(comb(x, math.pi + 0.35, 1.08 + 0.05 * layer, rx * (0.19 - 0.025 * layer) * r.uniform(0.85, 1.15),
                                       fall=fall, jitter=0.05, seed=i * 3 + layer))
            for sx in (1, -1):  # temple sweeps behind the ears
                for i in range(4):
                    clumps.append(comb(sx * rx * (0.9 + 0.03 * i), math.pi + 0.2, 1.08 + 0.03 * i, rx * 0.15, fall=rz * 0.9, jitter=0.04, seed=i, u0=0.15))
            if s.get('streak'):
                st = comb(rx * 0.3, math.pi + 0.35, 1.2, rx * 0.17, fall=rz * 1.0)
                C.assign(st, C.mat('grey', (0.55, 0.55, 0.57), rough=0.5)); self._bone_parent(st)
                pt = [hc + Vector((0, ry * (1.12 + 0.1 * i), rz * (-0.05 - 0.3 * i))) for i in range(6)]
                p = C.tube('pony', pt, rx * 0.17, taper=lambda t: 1 - 0.7 * t, res=10); C.assign(p, M); self._bone_parent(p)
        elif kind == 'curly':
            cap(f'{self.name}_scalp', 1.03, lambda c: hairline(c) or c.y > 0, disp=0.02)
            objs = []
            for i in range(230):
                th = r.uniform(0, math.pi * 0.66); ph = r.uniform(0, 2 * math.pi)
                d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
                if d.y < -0.4 and d.z < 0.6: continue
                p = Vector((d.x * rx, d.y * ry, d.z * rz)) * r.uniform(1.06, 1.16)
                objs.append(C.prim('ico', 'curl', loc=hc + p, subdivisions=2, radius=rx * r.uniform(0.13, 0.2)))
            for i in range(60):  # curls cascading to the nape and shoulders
                a = r.uniform(-1.4, 1.4) + math.pi / 2
                dn = r.uniform(0.1, 1.25)
                p = Vector((math.cos(a) * rx * (1.0 + 0.2 * dn), math.sin(a) * ry * 0.95 + ry * 0.1, -rz * dn + rz * 0.2))
                objs.append(C.prim('ico', 'curl', loc=hc + p, subdivisions=2, radius=rx * r.uniform(0.13, 0.19)))
            h = C.join(objs, f'{self.name}_hair')
            tex = bpy.data.textures.new('curltx', 'CLOUDS'); tex.noise_scale = 0.015
            C.add_mod(h, 'DISPLACE', texture=tex, strength=rx * 0.04)
            for p in h.data.polygons: p.use_smooth = True
            C.assign(h, M); self._bone_parent(h)
        elif kind == 'braid':
            cap(f'{self.name}_hair', 1.03, lambda c: (c.z > rz * 0.42 + (-c.y / ry) * rz * 0.1 - (abs(c.x) / rx) * rz * 0.25) if c.y < 0 else c.z > -rz * 0.45, disp=0.01)
            for sx in (1, -1):  # sweeps from the centre parting, over the temples, back to the bun
                for i in range(12):
                    ph0 = -math.pi / 2 + sx * (0.08 + i * 0.12)
                    phb = math.pi / 2 - sx * 0.25
                    pts = []
                    for k in range(14):
                        t = k / 13
                        th = 0.12 + (1.72 - 0.12) * t
                        ph = ph0 + (phb - ph0) * C.ease(max(0, (t - 0.25) / 0.75), 'smooth') if sx > 0 else ph0 - ((ph0 - phb) % (2 * math.pi) - 2 * math.pi) * 0 + (phb - ph0) * C.ease(max(0, (t - 0.25) / 0.75), 'smooth')
                        sc_ = 1.0 + 0.06 * min(1, t / 0.2)
                        pts.append(hc + Vector((math.sin(th) * math.cos(ph) * rx * sc_, math.sin(th) * math.sin(ph) * ry * sc_, math.cos(th) * rz * sc_)))
                    clumps.append(C.tube('clump', pts, rx * 0.14, taper=lambda t: min(1, 0.5 + 3 * t) * (1 - 0.4 * t), res=7))
            bun = C.ellipsoid('bun', rx * 0.36, ry * 0.3, rz * 0.32, loc=hc + Vector((0, ry * 1.02, -rz * 0.25)))
            C.assign(bun, M); self._bone_parent(bun)
            objs = []; jas = []
            top = hc + Vector((0, ry * 1.1, -rz * 0.45))
            for i in range(18):
                t = i / 17; p = top + Vector((0.006 * math.sin(i * 1.7) * self.H, 0.03 * self.H * t * (1 - t) + 0.012 * self.H * t, -0.38 * self.H * t))
                objs.append(C.ellipsoid('br', rx * 0.21 * (1 - 0.45 * t), ry * 0.16 * (1 - 0.45 * t), rz * 0.12, loc=p, seg=12, rings=8))
                if i < 6:
                    for sx in (1, -1):
                        jas.append(C.prim('ico', 'jas', loc=p + Vector((sx * rx * 0.2, ry * 0.08, 0)), subdivisions=1, radius=rx * 0.06))
            br = C.join(objs, f'{self.name}_braid'); C.assign(br, M); C.parent_keep(br, self.arm, 'chest'); self.parts.append(br)
            js = C.join(jas, f'{self.name}_jasmine'); C.assign(js, C.mat('jasmine', (0.95, 0.94, 0.86), rough=0.5, sss=0.3)); C.parent_keep(js, self.arm, 'chest'); self.parts.append(js)
        elif kind == 'bald_white':
            cap(f'{self.name}_hair', 1.05, lambda c: c.y > -ry * 0.1 and c.z < rz * 0.42 and c.z > -rz * 0.3, disp=0.07)
        if clumps:
            h = C.join(clumps, f'{self.name}_clumps')
            for p in h.data.polygons: p.use_smooth = True
            C.add_mod(h, 'SUBSURF', levels=1, render_levels=1)
            C.assign(h, M); self._bone_parent(h)
            self.face['hair'] = h

    def _head_acc(self, hc, rx, ry, rz, at):
        s = self.s; er = self.er
        if s.get('bindi'):
            b = C.ellipsoid('bindi', rx * 0.05, rx * 0.01, rx * 0.05, loc=hc + at(0, rz * 0.33, rx * 0.012)); C.assign(b, C.mat('bindi', (0.6, 0.02, 0.03), rough=0.3)); self._bone_parent(b)
        if s.get('headband'):
            hb = C.prim('torus', 'headband', loc=hc + Vector((0, 0, rz * 0.5)), major_radius=rx * 1.06, minor_radius=rx * 0.07)
            hb.scale = (1, ry / rx * 1.0, 1); hb.rotation_euler = (math.radians(-8), 0, 0)
            C.assign(hb, C.mat('band', s['headband'], rough=0.8)); self._bone_parent(hb)
        if s.get('cap'):
            cp = C.prim('cyl', 'cap', loc=hc + Vector((0, 0, rz * 0.82)), radius=rx * 1.08, depth=rz * 0.42)
            cp.scale = (1, ry / rx, 1); C.assign(cp, C.mat('khaki_cap', (0.48, 0.38, 0.22), rough=0.8))
            band = C.prim('cyl', 'capband', loc=hc + Vector((0, 0, rz * 0.66)), radius=rx * 1.1, depth=rz * 0.1)
            band.scale = (1, ry / rx, 1); C.assign(band, C.mat('capband', (0.05, 0.05, 0.08), rough=0.5))
            peak = C.ellipsoid('peak', rx * 0.8, ry * 0.5, rz * 0.04, loc=hc + Vector((0, -ry * 0.98, rz * 0.6)))
            C.assign(peak, C.mat('capband', (0.05, 0.05, 0.08), rough=0.5))
            badge = C.ellipsoid('badge', rx * 0.14, rx * 0.02, rx * 0.14, loc=hc + Vector((0, -ry * 1.1, rz * 0.84)))
            C.assign(badge, self.mats['gold'])
            for o in (cp, band, peak, badge): self._bone_parent(o)
        if s.get('glasses') or s.get('shades'):
            ez = rz * 0.13; ex = rx * 0.36
            objs = []
            for sx in (1, -1):
                c = hc + at(sx * ex, ez, er * 0.55) - Vector((0, er * 0.2, 0))
                objs.append(C.prim('torus', 'rim', loc=c, rotation=(math.pi / 2, 0, 0), major_radius=er * 1.25, minor_radius=er * 0.1))
                arm = C.tube('arm', [c + Vector((sx * er * 1.25, 0, 0)), hc + Vector((sx * rx * 1.02, ry * 0.2, ez))], er * 0.08, res=6); objs.append(arm)
            objs.append(C.tube('bridge', [hc + at(ex * 0.55, ez, er * 0.75), hc + at(0, ez + rz * 0.03, er * 0.9), hc + at(-ex * 0.55, ez, er * 0.75)], er * 0.08, res=6))
            g = C.join(objs, f'{self.name}_glasses')
            C.assign(g, C.mat('frame', (0.02, 0.02, 0.02), rough=0.3) if s.get('shades') else self.mats['gold'])
            self._bone_parent(g)
            if s.get('shades'):
                for sx in (1, -1):
                    c = hc + at(sx * ex, ez, er * 0.55) - Vector((0, er * 0.2, 0))
                    ln = C.ellipsoid('lens', er * 1.25, er * 0.15, er * 1.1, loc=c); C.assign(ln, C.mat('lens', (0.01, 0.01, 0.015), rough=0.05, metal=0.3, coat=1.0))
                    self._bone_parent(ln)

    # ---------------------------------------------------------------- hands & feet
    def _hand_mesh(self, name, sd, fist):
        H = self.H; s = self.s; b = s.get('build', 1) ** 0.5 * (0.88 if s.get('female') else 1.0)
        # canonical frame: fingers point -Z, palm faces +X for the left hand (toward body => -X), thumb toward -Y
        V, E, R = [], [], []
        def v(p, r):
            V.append(tuple(p)); R.append((r, r)); return len(V) - 1
        u = 0.01 * H * b
        wr = v((0, 0, 0), 1.9 * u); palm = v((0, -0.2 * u, -3.6 * u), 2.4 * u); E.append((wr, palm))
        curl = 1.25 if fist else 0.28
        for i, off in enumerate((-1.5, -0.5, 0.5, 1.5)):
            base = Vector((0, off * 1.25 * u - 0.2 * u, -5.6 * u)); kb = v(base, 0.75 * u); E.append((palm, kb))
            L = (2.2, 1.6, 1.2)[0:3]; d = Vector((0, 0, -1)); p = base; prev = kb; ang = 0
            for j, l in enumerate(L):
                ang += curl * (0.9 if j == 0 else 1.1)
                d = Vector((math.sin(ang) * 1.0, 0, -math.cos(ang)))  # curls toward palm (+X)
                p = p + d * l * u * (1 - 0.1 * abs(off))
                n = v(p, (0.68 - 0.1 * j) * u); E.append((prev, n)); prev = n
        # thumb
        tb = v((0.8 * u, -2.2 * u, -2.0 * u), 1.0 * u); E.append((palm, tb))
        tc = 1.0 if fist else 0.25
        p1 = Vector((1.4 * u + tc * 0.8 * u, -3.4 * u + tc * 0.9 * u, -3.4 * u)); t1 = v(p1, 0.78 * u); E.append((tb, t1))
        p2 = p1 + Vector((0.6 * u + tc * 0.6 * u, -1.0 * u + tc * 1.2 * u, -1.4 * u)); t2 = v(p2, 0.62 * u); E.append((t1, t2))
        o = _skin_mesh(name, V, E, R, root=wr); C.apply_mods(o)
        # canonical palm faces +X: correct for the RIGHT hand (body is at +X from it); mirror for the LEFT hand
        if sd == 'L':
            for vt in o.data.vertices: vt.co.x *= -1
            o.data.flip_normals()
        for p in o.data.polygons: p.use_smooth = True
        C.assign(o, self.mats['skin'])
        # orient canonical -> bone rest frame
        hb = self.arm.data.bones[f'hand.{sd}']
        d = (hb.tail_local - hb.head_local).normalized()
        fwd = Vector((0, -1, 0)); fwd = (fwd - d * fwd.dot(d)).normalized()
        q = frame_rot(d, fwd, Vector((0, 0, -1)), Vector((0, -1, 0)))
        o.matrix_world = Matrix.Translation(hb.head_local) @ q.to_matrix().to_4x4()
        return o

    def _hands(self):
        for sd in ('L', 'R'):
            op = self._hand_mesh(f'{self.name}_hand{sd}', sd, False)
            fi = self._hand_mesh(f'{self.name}_fist{sd}', sd, True)
            for o in (op, fi): C.parent_keep(o, self.arm, f'hand.{sd}'); self.parts.append(o)
            self.hands[sd] = {'open': op, 'fist': fi}
            fi.hide_render = True; fi.hide_viewport = True
            if self.s.get('bangles') or (self.s.get('kada') == sd):
                wrp = self.J[f'wr.{sd}']
                d = (self.J[f'hd.{sd}'] - wrp).normalized()
                for k in range(3 if self.s.get('bangles') else 1):
                    ring = self._surface_ring(wrp - d * (0.012 + 0.009 * k) * self.H, d, n=16)
                    rr = sum((p - (wrp - d * (0.012 + 0.009 * k) * self.H)).length for p in ring) / len(ring)
                    bg = C.prim('torus', 'bangle', loc=wrp - d * (0.012 + 0.009 * k) * self.H, major_radius=rr + 0.004 * self.H, minor_radius=0.0035 * self.H)
                    bg.rotation_mode = 'QUATERNION'; bg.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
                    C.assign(bg, self.mats['gold'] if self.s.get('bangles') else self.mats['silver'])
                    C.parent_keep(bg, self.arm, f'forearm.{sd}'); self.parts.append(bg)

    def _feet(self):
        H = self.H
        sandal = C.mat('sandal', (0.10, 0.05, 0.025), rough=0.75)
        shoe = C.mat('shoe', (0.03, 0.02, 0.015), rough=0.35, coat=0.6)
        boots = self.s['lower'] in ('pants', 'coat')
        for sd in ('L', 'R'):
            an = self.J[f'an.{sd}']; toe = self.J[f'toe.{sd}']
            L = 0.145 * H; Wd = 0.05 * H * (1.15 if boots else 1.0); Ht = 0.05 * H
            cy = an.y - L * 0.30  # foot centre is forward of the ankle
            def sh(x, y, z, L=L, Ht=Ht):
                fy = y / (L / 2)                      # -1 toe .. +1 heel
                wid = 1.0 - 0.18 * max(0, fy) - 0.05 * max(0, -fy)
                top = Ht * (0.35 + 0.65 * (0.5 + 0.5 * fy) ** 0.7)  # instep slopes down toward the toes
                zz = z if z < 0 else z * top / Ht
                return x * wid, y, zz
            f = C.ellipsoid(f'{self.name}_foot{sd}', Wd / 2, L / 2, Ht, seg=28, rings=16, shape=sh)
            f.location = Vector((an.x, cy, 0.0))
            for v in f.data.vertices:  # flat sole exactly on z = sole thickness
                if v.co.z < 0.004 * H: v.co.z = 0.004 * H
            C.assign(f, shoe if boots else self.mats['skin'])
            C.parent_keep(f, self.arm, f'foot.{sd}'); self.parts.append(f)
            if not boots:
                so = C.ellipsoid('sole', Wd / 2 * 1.12, L / 2 * 1.06, 0.004 * H, loc=(an.x, cy, 0.002 * H), seg=24, rings=6)
                C.assign(so, sandal); C.parent_keep(so, self.arm, f'foot.{sd}'); self.parts.append(so)
                st = C.prim('torus', 'strap', loc=(an.x, cy - L * 0.18, 0.012 * H), major_radius=Wd * 0.42, minor_radius=0.004 * H, rotation=(0, math.radians(90), math.radians(90)))
                st.scale = (1, 1.0, 1.25); C.assign(st, sandal); C.parent_keep(st, self.arm, f'foot.{sd}'); self.parts.append(st)

    def _costume_extras(self):
        s = self.s; H = self.H; J = self.J
        if s.get('pallu'):  # diagonal half-saree drape from left shoulder to right hip, front
            pts = []
            for i in range(12):
                t = i / 11
                p = J['sh.L'].lerp(Vector((-0.07 * H, 0, H * 0.56)), t)
                bulge = 0.072 * H * (1 - (2 * t - 1) ** 2 * 0.4)
                pts.append(Vector((p.x, -bulge - 0.002 * H, p.z)))
            pa = C.tube(f'{self.name}_pallu', pts, 0.05 * H, res=12); pa.scale.y = 0.35
            pa.data.transform(Matrix.Diagonal((1, 0.35, 1, 1))); pa.scale = (1, 1, 1)
            # flowing tail over the shoulder down the back
            back = [J['sh.L'] + Vector((0, 0.01 * H, 0.01 * H)), J['sh.L'] + Vector((0.005 * H, 0.07 * H, -0.05 * H)), J['sh.L'] + Vector((0.01 * H, 0.08 * H, -0.32 * H))]
            pb = C.tube('pallu_back', back, 0.05 * H, res=12); pb.data.transform(Matrix.Translation(Vector((0, 0, 0))))
            p = C.join([pa, pb], f'{self.name}_pallu')
            C.assign(p, C.mat('pallu', s['pallu'], rough=0.55, sheen=0.6, noise=0.2, noise_scale=200))
            C.parent_keep(p, self.arm, 'chest'); self.parts.append(p)
        if s.get('shawl'):
            sw = C.prim('torus', 'shawl', loc=J['neck0'] + Vector((0, 0.004 * H, -0.012 * H)), major_radius=0.085 * H, minor_radius=0.028 * H)
            sw.scale = (1.05, 0.8, 0.7); C.assign(sw, C.mat('shawlm', s['shawl'], rough=0.85, sheen=0.5, noise=0.3, noise_scale=120))
            C.parent_keep(sw, self.arm, 'chest'); self.parts.append(sw)
            for sx in (1, -1):
                tail = C.tube('shawltail', [J['neck0'] + Vector((sx * 0.06 * H, -0.05 * H, -0.02 * H)), Vector((sx * 0.075 * H, -0.075 * H, 0.62 * H))], 0.03 * H, res=10)
                tail.data.transform(Matrix.Diagonal((1.3, 0.4, 1, 1)) if False else Matrix.Identity(4))
                C.assign(tail, C.mat('shawlm', s['shawl'], rough=0.85, sheen=0.5, noise=0.3, noise_scale=120)); C.parent_keep(tail, self.arm, 'chest'); self.parts.append(tail)
        if s.get('belt'):
            bt = C.prim('torus', 'belt', loc=(0, 0, H * 0.555), major_radius=0.086 * H, minor_radius=0.011 * H)
            bt.scale = (1, 0.74, 1.4); C.assign(bt, C.mat('belt', (0.16, 0.08, 0.03), rough=0.4, coat=0.5))
            bk = C.prim('cube', 'buckle', loc=(0, -0.066 * H, H * 0.555), scale=(0.018 * H, 0.004 * H, 0.012 * H)); C.assign(bk, self.mats['gold'])
            for o in (bt, bk): C.parent_keep(o, self.arm, 'hips'); self.parts.append(o)
        if s.get('armband'):
            for sd in ('L', 'R'):
                p = J[f'sh.{sd}'].lerp(J[f'el.{sd}'], 0.55); d = (J[f'el.{sd}'] - J[f'sh.{sd}']).normalized()
                ab = C.prim('torus', 'armband', loc=p, major_radius=0.034 * H, minor_radius=0.006 * H)
                ab.rotation_mode = 'QUATERNION'; ab.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
                C.assign(ab, self.mats['gold']); C.parent_keep(ab, self.arm, f'upperarm.{sd}'); self.parts.append(ab)
        if s.get('open_vest') or s.get('shawl') is None and s['lower'] != 'pants' and self.key in ('devara', 'yethi', 'bhaira'):
            # chain / thread necklace
            ch = C.prim('torus', 'chain', loc=J['neck0'] + Vector((0, -0.012 * H, -0.035 * H)), major_radius=0.05 * H, minor_radius=0.0028 * H, rotation=(math.radians(-62), 0, 0))
            C.assign(ch, self.mats['gold'] if self.key == 'bhaira' else C.mat('thread', (0.08, 0.02, 0.02), rough=0.8))
            C.parent_keep(ch, self.arm, 'chest'); self.parts.append(ch)
        if s['lower'] == 'coat':  # long sleeves already; add lapels
            for sx in (1, -1):
                lp = C.tube('lapel', [J['neck0'] + Vector((sx * 0.04 * H, -0.05 * H, -0.01 * H)), Vector((sx * 0.06 * H, -0.075 * H, 0.62 * H))], 0.012 * H, res=8)
                C.assign(lp, C.mat('lapel', (0.05, 0.05, 0.06), rough=0.3, coat=0.4)); C.parent_keep(lp, self.arm, 'chest'); self.parts.append(lp)

    # ---------------------------------------------------------------- runtime controls
    def place(self, frame, loc, yaw_deg=0.0, parent=None):
        self.arm.location = loc; self.arm.rotation_euler = (0, 0, math.radians(yaw_deg))
        self.arm.keyframe_insert('location', frame=frame); self.arm.keyframe_insert('rotation_euler', frame=frame)

    def set_hand(self, frame, sd, state):
        for st, o in self.hands[sd].items():
            vis = st == state
            o.hide_render = not vis; o.keyframe_insert('hide_render', frame=frame)

    def world_matrix(self):
        return self.arm.matrix_world


def surf_y(ch, x, z):
    return ch.surf(x, z)

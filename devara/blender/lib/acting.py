"""Acting layer: pose blending, locomotion with planted feet, look-at, face & lip-sync, prop attachment.

An Actor is driven by a per-frame `pose(t)` function returning a Pose dict. bake() evaluates it for every frame,
solves IK, writes keys. Everything is deterministic.
"""
import bpy, math
from mathutils import Vector, Matrix, Quaternion, Euler
from . import core as C
from .rig import qe, frame_rot

FPS = C.FPS
V = lambda *a: Vector(a)

# ------------------------------------------------------------------ pose library
# Arm targets are wrist positions relative to the (posed) shoulder, in chest frame, in units of arm reach.
# Left side given; right side mirrors x. 'e' = elbow pole hint, 'h' = finger direction, 'p' = palm normal.
ARM = {
 'down':     dict(w=V(0.16, 0.02, -0.97), e=V(0.2, 1, 0), h=V(0.05, 0, -1), p=V(-1, 0, 0)),
 'relaxed':  dict(w=V(0.14, -0.10, -0.94), e=V(0.3, 1, -0.2), h=V(0.0, -0.2, -1), p=V(-1, 0.2, 0)),
 'hip':      dict(w=V(0.30, 0.04, -0.62), e=V(1, 0.1, 0), h=V(-0.6, 0.2, -0.7), p=V(-0.4, 0, 0.5)),
 'cross':    dict(w=V(-0.32, -0.36, -0.42), e=V(1, -0.2, -0.3), h=V(-1, 0, 0.2), p=V(0, 1, 0)),
 'cross_top':dict(w=V(-0.36, -0.42, -0.32), e=V(1, -0.1, -0.4), h=V(-1, 0, 0.0), p=V(0, 1, 0)),
 'point':    dict(w=V(0.22, -0.95, 0.12), e=V(0.6, 0.4, -1), h=V(0.15, -1, 0.1), p=V(-1, 0, 0)),
 'point_up': dict(w=V(0.2, -0.45, 0.8), e=V(0.9, 0.3, -0.3), h=V(0.1, -0.3, 1), p=V(-1, 0, 0)),
 'palm_out': dict(w=V(0.36, -0.62, -0.32), e=V(0.6, 0.4, -1), h=V(0.2, -0.5, 0.8), p=V(0, -1, 0.1)),
 'explain':  dict(w=V(0.30, -0.62, -0.42), e=V(0.6, 0.6, -1), h=V(0.3, -1, 0.1), p=V(-0.3, 0, 1)),
 'shrug':    dict(w=V(0.55, -0.42, -0.38), e=V(0.4, 0.6, -1), h=V(0.6, -0.7, 0.1), p=V(0, 0, 1)),
 'fist_up':  dict(w=V(0.18, -0.22, 0.95), e=V(1, 0.2, 0), h=V(0, 0, 1), p=V(-1, 0, 0)),
 'flex':     dict(w=V(0.62, -0.12, 0.30), e=V(0.3, 0.3, -1), h=V(0, 0, 1), p=V(-1, 0, 0)),
 'shock':    dict(w=V(0.34, -0.50, 0.02), e=V(1, 0.2, -1), h=V(0.2, -0.3, 1), p=V(0, -1, 0)),
 'cheek':    dict(w=V(0.04, -0.32, 0.30), e=V(0.6, 0, -1), h=V(-0.3, 0, 1), p=V(-1, 0, 0)),
 'chest':    dict(w=V(-0.06, -0.42, -0.28), e=V(1, 0.1, -0.6), h=V(-1, 0, 0.3), p=V(0, 1, 0)),
 'head_hold':dict(w=V(0.08, -0.10, 0.58), e=V(1, -0.2, 0.2), h=V(-0.4, 0, 1), p=V(-1, 0, 0)),
 'reach':    dict(w=V(0.12, -0.98, -0.12), e=V(0.6, 0.4, -1), h=V(0, -1, 0), p=V(-1, 0, 0)),
 'hug':      dict(w=V(-0.22, -0.70, -0.18), e=V(1, 0.3, 0), h=V(-1, 0.2, 0), p=V(0, 1, 0)),
 'back':     dict(w=V(0.18, 0.40, -0.85), e=V(0.6, -0.6, -0.3), h=V(0, 0.4, -1), p=V(-1, 0, 0)),
 'swing_up': dict(w=V(0.30, 0.10, 0.90), e=V(1, 0.4, 0), h=V(0, 0.3, 1), p=V(-1, 0, 0)),
 'swing_dn': dict(w=V(-0.15, -0.80, -0.45), e=V(1, 0, -0.6), h=V(-0.3, -0.7, -0.6), p=V(0, 0, -1)),
 'slash_out':dict(w=V(0.85, -0.45, -0.05), e=V(0.2, 0.3, -1), h=V(1, -0.4, 0), p=V(0, 0, 1)),
 'hold_side':dict(w=V(0.20, -0.20, -0.85), e=V(0.4, 1, 0), h=V(0, -1, -0.2), p=V(-1, 0, 0)),
 'stab':     dict(w=V(0.05, -1.0, -0.1), e=V(0.5, 0.6, -1), h=V(0, -1, 0), p=V(-1, 0, 0)),
 'lift':     dict(w=V(0.06, -0.12, 0.98), e=V(1, 0.2, 0), h=V(0, 0, 1), p=V(0, -1, 0)),
 'carry':    dict(w=V(0.15, -0.45, -0.55), e=V(0.6, 0.8, -0.6), h=V(0, -0.6, -0.6), p=V(-1, 0, 0)),
 'drink':    dict(w=V(-0.02, -0.34, 0.34), e=V(1, 0.2, -1), h=V(-0.5, -0.2, 0.8), p=V(-1, 0, 0)),
 'glass':    dict(w=V(0.10, -0.62, -0.42), e=V(0.5, 0.6, -1), h=V(0, -1, 0), p=V(-1, 0, 0)),
 'table':    dict(w=V(0.10, -0.68, -0.52), e=V(0.6, 0.6, -1), h=V(0, -1, -0.1), p=V(0, 0, -1)),
 'wave':     dict(w=V(0.55, -0.25, 0.75), e=V(0.8, 0.3, -1), h=V(0.2, 0, 1), p=V(0, -1, 0)),
 'shush':    dict(w=V(-0.05, -0.38, 0.38), e=V(1, 0, -1), h=V(0, 0, 1), p=V(-1, 0, 0)),
 'grab':     dict(w=V(0.0, -0.85, 0.05), e=V(0.6, 0.4, -1), h=V(0, -1, 0), p=V(-1, 0, 0)),
}

def arm_pose(name, mirror=False):
    a = ARM[name]
    if not mirror: return a
    f = lambda v: Vector((-v.x, v.y, v.z))
    return {k: f(v) for k, v in a.items()}

def blend_arm(a, b, t):
    out = {k: a[k].lerp(b[k], t) for k in ('w', 'e', 'h', 'p')}
    wa, wb = a.get('W'), b.get('W')
    if wa is not None or wb is not None:   # absolute target fades in/out with the blend
        if wa is not None and wb is not None:
            out['W'] = Vector(wa).lerp(Vector(wb), t); out['Wk'] = a.get('Wk', 1) * (1 - t) + b.get('Wk', 1) * t
        elif wb is not None: out['W'] = Vector(wb); out['Wk'] = b.get('Wk', 1) * t
        else: out['W'] = Vector(wa); out['Wk'] = a.get('Wk', 1) * (1 - t)
    return out

def reach_to(name, W, mirror=False, k=1.0):
    a = dict(arm_pose(name, mirror)); a['W'] = Vector(W); a['Wk'] = k
    return a

EXPR = {  # brow raise, brow angle(+ = inner up/sad, - = angry), lid open, mouth smile, frown, wide
 'neutral': dict(br=0.0, ba=0.0, lid=1.0, smile=0.1, frown=0.0),
 'happy':   dict(br=0.25, ba=0.1, lid=0.85, smile=0.85, frown=0.0),
 'laugh':   dict(br=0.4, ba=0.25, lid=0.45, smile=1.0, frown=0.0, grin=0.6),
 'angry':   dict(br=-0.35, ba=-1.0, lid=0.78, smile=0.0, frown=0.7),
 'fierce':  dict(br=-0.25, ba=-0.7, lid=0.72, smile=0.0, frown=0.3),
 'shocked': dict(br=1.0, ba=0.25, lid=1.35, smile=0.0, frown=0.0, O=0.6),
 'scared':  dict(br=0.8, ba=0.9, lid=1.25, smile=0.0, frown=0.6),
 'sad':     dict(br=0.3, ba=1.0, lid=0.7, smile=0.0, frown=0.6),
 'smug':    dict(br=0.1, ba=-0.3, lid=0.7, smile=0.6, frown=0.0, asym=1),
 'deadpan': dict(br=-0.05, ba=0.0, lid=0.55, smile=0.0, frown=0.15),
 'worried': dict(br=0.5, ba=0.8, lid=1.05, smile=0.0, frown=0.35),
 'wise':    dict(br=0.15, ba=0.15, lid=0.7, smile=0.35, frown=0.0),
 'proud':   dict(br=0.2, ba=0.0, lid=0.8, smile=0.6, frown=0.0),
 'closed':  dict(br=0.0, ba=0.0, lid=0.0, smile=0.15, frown=0.0),
}

def blend_expr(a, b, t):
    keys = set(a) | set(b)
    return {k: (a.get(k, 0) * (1 - t) + b.get(k, 0) * t) for k in keys}


class Actor:
    def __init__(self, ch, seed=1):
        self.ch = ch; self.sk = ch.sk; self.seed = seed
        self.H = ch.H
        self.reach = (self.sk.len['upperarm.L'] + self.sk.len['forearm.L']) * 0.98
        self.props = []  # (obj, fn(t)->(bone, local_matrix) or None)
        self.lines = []  # (start, end, env list) in shot seconds
        self.expr_track = [(0, 'neutral')]
        self.look_fn = None
        self.blink_off = C.rng(seed).uniform(0, 3)
        self.parent_obj = None

    # ------------------------------------------------------------ helpers for shot code
    def say(self, ev, gesture=True):
        self.lines.append((ev['start'], ev['end'], ev['env']))

    def talking(self, t):
        for s, e, env in self.lines:
            if s - 0.05 <= t <= e + 0.05:
                i = int((t - s) * FPS)
                return env[i] if 0 <= i < len(env) else 0.0, True
        return 0.0, False

    def expr(self, *track):
        """track: (time, name[, blend_seconds]) ..."""
        self.expr_track = [(x[0], x[1], x[2] if len(x) > 2 else 0.25) for x in track]

    def _expr_at(self, t):
        tr = self.expr_track; cur = EXPR[tr[0][1]]
        for i, item in enumerate(tr):
            tt, nm = item[0], item[1]; bl = item[2] if len(item) > 2 else 0.25
            if t >= tt:
                prev = EXPR[tr[i - 1][1]] if i > 0 else EXPR[nm]
                cur = blend_expr(prev, EXPR[nm], C.seg(t, tt, tt + bl))
        return cur

    # ------------------------------------------------------------ main bake
    def bake(self, f0, f1, pose_fn):
        """pose_fn(t) -> dict(root=(loc, yaw), hip=Vector, torso=(x,y,z) deg, head=(x,y,z), armL, armR,
                               feet=dict(L=(pos,yaw,pitch), R=...), fistL, fistR, look=Vector world or None)"""
        ch = self.ch; sk = self.sk
        last = {}
        for f in range(f0, f1 + 1):
            t = (f - 1) / FPS
            P = pose_fn(t)
            loc, yaw = P['root']
            rr = P.get('root_rot', (0, 0))
            ch.arm.location = loc; ch.arm.rotation_euler = (math.radians(rr[0]), math.radians(rr[1]), math.radians(yaw))
            ch.arm.keyframe_insert('location', frame=f); ch.arm.keyframe_insert('rotation_euler', frame=f)
            Rroot = Matrix.Rotation(math.radians(yaw), 3, 'Z')
            hip = P.get('hip', Vector())
            R = {}
            tx, ty, tz = P.get('torso', (0, 0, 0))
            R['hips'] = qe(tx * 0.3, ty * 0.3, tz * 0.35) @ qe(*P.get('pelvis', (0, 0, 0)))
            R['spine'] = qe(tx * 0.35, ty * 0.35, tz * 0.35)
            R['chest'] = qe(tx * 0.35, ty * 0.35, tz * 0.3)
            hx, hy, hz = P.get('head', (0, 0, 0))
            look = P.get('look')
            if look is not None:
                # convert world look target to angles relative to chest
                F = sk.fk(R, hip)
                # look targets live in the same space as the root (world, or the parent boat's local space)
                Rfull_ = Euler((math.radians(rr[0]), math.radians(rr[1]), math.radians(yaw))).to_matrix()
                neck_w = Vector(loc) + Rfull_ @ (F['neck'][1] + Vector((0, 0, self.ch.hc.z - self.ch.J['neck1'].z)))
                d = (Vector(look) - neck_w)
                dl = (Rfull_.inverted() @ d)
                dl = F['chest'][0].inverted() @ dl
                yaw_l = math.degrees(math.atan2(dl.x, -dl.y)); pitch = math.degrees(math.atan2(dl.z, Vector((dl.x, dl.y)).length))
                yaw_l = max(-75, min(75, yaw_l)); pitch = max(-40, min(35, pitch))
                hz += yaw_l; hx -= pitch * 0.9
            R['neck'] = qe(hx * 0.4, hy * 0.4, hz * 0.4)
            R['head'] = qe(hx * 0.6, hy * 0.6, hz * 0.6)
            # shoulders shrug
            shr = P.get('shrug', 0.0)
            R['shoulder.L'] = qe(0, -shr * 14, 0); R['shoulder.R'] = qe(0, shr * 14, 0)
            F = sk.fk(R, hip)
            for sd, mir in (('L', False), ('R', True)):
                a = P.get('arm' + sd) or arm_pose('down', mir)
                Gc = F['chest'][0]
                sh = F[f'upperarm.{sd}'][1]
                tgt = sh + Gc @ (a['w'] * self.reach)
                if a.get('W') is not None:  # absolute world/parent-space wrist target, blended by 'Wk'
                    Rfull = Euler((math.radians(rr[0]), math.radians(rr[1]), math.radians(yaw))).to_matrix()
                    wt = Rfull.inverted() @ (Vector(a['W']) - Vector(loc))
                    tgt = tgt.lerp(wt, a.get('Wk', 1.0))
                pole = Gc @ a['e'].normalized()
                sk.ik2(R, f'upperarm.{sd}', f'forearm.{sd}', tgt, pole, hip)
                F = sk.fk(R, hip)
                hd = (Gc @ a['h']).normalized(); pn = (Gc @ a['p']).normalized()
                rest_d = sk.rest_dir(f'hand.{sd}')
                # rest palm normal: points toward body (-X for L, +X for R) approx; compute from rest frame
                rest_p = Vector((-1, 0, 0)) if sd == 'L' else Vector((1, 0, 0))
                rest_p = (rest_p - rest_d * rest_p.dot(rest_d)).normalized()
                Wd = frame_rot(hd, pn, rest_d, rest_p).to_matrix()
                sk.set_world_rot(R, f'hand.{sd}', Wd, hip)
                F = sk.fk(R, hip)
            # legs
            feet = P.get('feet')
            for sd, sg in (('L', 1), ('R', -1)):
                if feet and sd in feet:
                    pos, fyaw, pitch = feet[sd]
                    # pos given in parent/world space -> armature space
                    al = Rroot.inverted() @ (Vector(pos) - Vector(loc))
                else:
                    al = Vector((self.ch.J[f'an.{sd}'].x, self.ch.J[f'an.{sd}'].y, self.ch.J[f'an.{sd}'].z)); fyaw, pitch = yaw, 0
                # knee pole: forward of foot heading
                kdir = Matrix.Rotation(math.radians(fyaw - yaw), 3, 'Z') @ Vector((0.12 * sg, -1, 0.0))
                sk.ik2(R, f'thigh.{sd}', f'shin.{sd}', al, kdir, hip)
                Wf = (Matrix.Rotation(math.radians(fyaw - yaw), 3, 'Z') @ Matrix.Rotation(math.radians(pitch), 3, 'X'))
                sk.set_world_rot(R, f'foot.{sd}', Wf, hip)
            sk.apply(R, hip, f)
            # hands open / fist
            for sd in ('L', 'R'):
                st = 'fist' if P.get('fist' + sd) else 'open'
                if last.get(sd) != st:
                    for nm, o in ch.hands[sd].items():
                        o.hide_render = nm != st; o.keyframe_insert('hide_render', frame=f)
                    last[sd] = st
            self._face(f, t, P)
            self._props(f, t, R, hip)
            self.lastF = F
        for o in [ch.arm] + [o for o in ch.parts if o.animation_data]:
            pass

    # ------------------------------------------------------------ face
    def _face(self, f, t, P):
        ch = self.ch; fc = ch.face
        E = dict(self._expr_at(t))
        if 'expr' in P: E = EXPR[P['expr']] if isinstance(P['expr'], str) else P['expr']
        env, talking = self.talking(t)
        # blink: every 2.5..5 s, 5 frames
        r = C.rng(self.seed * 1000 + int((t + self.blink_off) / 3.7))
        bt = ((t + self.blink_off) % 3.7) - r.uniform(0.3, 2.5)
        blink = 1.0 - (math.sin(min(1, max(0, bt / 0.2)) * math.pi) if 0 <= bt <= 0.2 else 0)
        lid = E.get('lid', 1.0) * blink if E.get('lid', 1) > 0 else 0
        lid = P.get('lid', lid)
        er = ch.er
        for sd in ('L', 'R'):
            lp = fc[f'lidpiv{sd}']
            # lid 1.0 = normal open (-58deg), 0 = closed (+8), 1.35 = wide (-80)
            ld = P.get('lid' + sd, lid)
            ang = 8 - 66 * ld if ld <= 1 else -58 - (ld - 1) * 70
            fc[f'lid{sd}'].rotation_euler = (math.radians(ang), 0, 0); fc[f'lid{sd}'].keyframe_insert('rotation_euler', frame=f)
            low = ch.face_low[sd] if hasattr(ch, 'face_low') else None
            # eye look (small saccades + optional direction)
            ly, lx = P.get('eyes', (0.0, 0.0))
            ly += C.noise1(t, self.seed + (0 if sd == 'L' else 0), 0.7) * 4
            ep = fc[f'eye{sd}']; ep.rotation_euler = (math.radians(-lx), 0, math.radians(ly))
            ep.keyframe_insert('rotation_euler', frame=f)
            # brows
            sg = 1 if sd == 'L' else -1
            asym = E.get('asym', 0) * (0.25 if sd == 'L' else -0.1)
            bp = fc[f'brow{sd}']
            bz = 0.0
            raise_ = (E.get('br', 0) + asym + (env * 0.12 if talking else 0)) * ch.hr[2] * 0.14
            bp.location.z = bz + raise_
            bp.rotation_euler = (0, math.radians(-sg * E.get('ba', 0) * 16), 0)
            bp.keyframe_insert('location', frame=f); bp.keyframe_insert('rotation_euler', frame=f)
        # mouth shape keys
        m = fc['mouth']; kb = m.data.shape_keys.key_blocks
        o = min(1.0, env * 0.95) if talking else 0.0
        var = 0.5 + 0.5 * math.sin(t * 17.0 + self.seed)
        W = {'open': o * (0.75 + 0.25 * var), 'O': o * 0.35 * (1 - var) + E.get('O', 0) * (0 if talking else 1),
             'wide': o * 0.3 * var, 'smile': E.get('smile', 0) * (0.6 if talking else 1),
             'frown': E.get('frown', 0) * (0.6 if talking else 1), 'grin': E.get('grin', 0) * (0.5 if talking else 1)}
        if 'mouth' in P: W.update(P['mouth'])
        for k, v in W.items():
            kb[k].value = max(0, min(1.2, v)); kb[k].keyframe_insert('value', frame=f)
        th = fc['teeth']; op = W['open'] + W.get('grin', 0) * 0.6 + W['O'] * 0.3
        th.scale = (1.0, 1.0, max(0.001, min(1, op * 1.3))); th.keyframe_insert('scale', frame=f)

    # ------------------------------------------------------------ props in hands
    def hold(self, obj, fn):
        """fn(t) -> ('hand.R', Matrix local-to-bone) to attach, or None to leave obj alone at that frame."""
        self.props.append((obj, fn))

    def bone_world(self, R, hip, bone):
        F = self.sk.fk(R, hip); G, head = F[bone]
        M = self.sk.rest[bone].to_3x3()
        mb = (G @ M).to_4x4(); mb.translation = head
        return self.ch.arm.matrix_world @ mb if self.ch.arm.parent is None else self._parent_world() @ self._root_local() @ mb

    def _root_local(self):
        a = self.ch.arm
        return Matrix.Translation(a.location) @ a.rotation_euler.to_matrix().to_4x4()

    def _parent_world(self):
        return self.ch.arm.parent.matrix_world

    def _props(self, f, t, R, hip):
        for obj, fn in self.props:
            r = fn(t)
            if r is None: continue
            if r[0] == 'between':  # two-handed prop: centred between the hands, X axis from left to right hand
                _, roll, lift = (r + (0.0, 0.0))[:3] if len(r) < 3 else r
                F = self.sk.fk(R, hip)
                pl = self.sk.tail(F, 'hand.L').lerp(F['hand.L'][1], 0.5); pr = self.sk.tail(F, 'hand.R').lerp(F['hand.R'][1], 0.5)
                xa = (pl - pr).normalized(); up = Vector((0, 0, 1)); ya = up.cross(xa).normalized(); za = xa.cross(ya)
                Mloc = Matrix((xa, ya, za)).transposed().to_4x4(); Mloc.translation = (pl + pr) / 2 + za * lift
                Mloc = Mloc @ Matrix.Rotation(math.radians(roll), 4, 'X')
                W = (self._parent_world_at(f) if self.ch.arm.parent is not None else Matrix.Identity(4)) @ self._root_local() @ Mloc
                obj.matrix_world = W
                obj.keyframe_insert('location', frame=f); obj.keyframe_insert('rotation_euler', frame=f)
                continue
            bone, local = r
            if self.ch.arm.parent is None:
                W = self._root_local() @ self._bone_arm(R, hip, bone) @ local
            else:
                W = self._parent_world_at(f) @ self._root_local() @ self._bone_arm(R, hip, bone) @ local
            obj.matrix_world = W
            obj.keyframe_insert('location', frame=f); obj.keyframe_insert('rotation_euler', frame=f)

    def _parent_world_at(self, f):
        p = self.ch.arm.parent
        bpy.context.scene.frame_set(f)
        return p.matrix_world.copy()

    def _bone_arm(self, R, hip, bone):
        F = self.sk.fk(R, hip); G, head = F[bone]
        M = self.sk.rest[bone].to_3x3()
        mb = (G @ M).to_4x4(); mb.translation = head
        return mb


# ------------------------------------------------------------------ locomotion
class Gait:
    """Planted-foot walking/running along a ground path.
    path(s) -> Vector world point on ground at arc length s; s_of_t(t) -> arc length (monotone)."""
    def __init__(self, actor, path, s_of_t, total, stride=None, duty=0.62, lift=None, width=None, ground=0.0, run=False):
        H = actor.H
        self.a = actor; self.path = path; self.s_of_t = s_of_t; self.total = total
        self.S = stride or (0.78 * H if not run else 1.35 * H)
        n = max(1, round(total / (self.S / 2))); self.S = 2 * total / n if total > 0.05 else self.S
        self.duty = duty if not run else 0.38
        self.lift = lift or (0.07 * H if not run else 0.16 * H)
        self.w = width or abs(actor.ch.J['an.L'].x)
        self.g = ground; self.run = run
        self.ah = actor.ch.J['an.L'].z

    def heading(self, s):
        a = self.path(max(0, min(self.total, s - 0.05))); b = self.path(max(0, min(self.total, s + 0.05)))
        d = b - a
        if d.length < 1e-6: d = self.path(min(self.total, 0.1)) - self.path(0)
        return math.degrees(math.atan2(d.x, -d.y)) if d.length > 1e-6 else 0.0  # yaw so that -Y faces d

    def _side(self, s, sg):
        yaw = math.radians(self.heading(s))
        right = Vector((math.cos(yaw), math.sin(yaw), 0))  # local +X (char left) rotated
        return self.path(max(0, min(self.total, s))) + right * self.w * sg

    def foot(self, s, sd):
        S = self.S; off = 0.0 if sd == 'L' else S / 2
        lead = (1 - self.duty) * 0.5 * S + self.duty * S * 0.5 - S * 0.5 + 0.3 * S
        u = (s - off) / S; k = math.floor(u); ph = u - k
        sg = 1 if sd == 'L' else -1
        land = lambda kk: kk * S + off + 0.3 * S
        if ph < self.duty:
            fs = land(k); z = 0; pitch = 0
        else:
            v = (ph - self.duty) / (1 - self.duty)
            e = C.ease(v, 'smooth')
            fs = land(k) + S * e
            z = self.lift * math.sin(math.pi * v) ** 0.9
            pitch = -25 * math.sin(math.pi * v * 1.2) * (1 - v) + 12 * math.sin(math.pi * v) * v
        fs = max(0.0, min(self.total, fs))
        p = self._side(fs, sg); p.z = self.g + self.ah + z
        return p, self.heading(fs), pitch

    def at(self, t, settle=0.35):
        """returns dict(root, feet, hip, phase) — settles to a standing stance at the end."""
        s = self.s_of_t(t)
        loc = self.path(s); loc.z = self.g; yaw = self.heading(s)
        feet = {sd: self.foot(s, sd) for sd in ('L', 'R')}
        # end settle: blend feet to rest stance
        rem = self.total - s
        if rem < self.S * 0.5:
            k = C.ease(1 - rem / (self.S * 0.5), 'smooth')
            for sd, sg in (('L', 1), ('R', -1)):
                p, fy, pi = feet[sd]
                st = self._side(self.total, sg); st.z = self.g + self.ah
                q = p.lerp(st, k); q.z = self.g + self.ah + (p.z - self.g - self.ah) * (1 - k)
                feet[sd] = (q, fy, pi * (1 - k))
        phase = s / self.S
        amp = min(1.0, s / (self.S * 0.4)) * min(1.0, max(0, rem) / (self.S * 0.4))
        bob = (0.018 if not self.run else 0.05) * self.a.H
        hip = Vector((0.012 * self.a.H * math.sin(2 * math.pi * phase) * amp, 0,
                      -bob * (0.5 + 0.5 * math.cos(4 * math.pi * phase)) * amp - (0.03 * self.a.H if self.run else 0.008 * self.a.H) * amp))
        return dict(root=(loc, yaw), feet=feet, hip=hip, phase=phase, amp=amp)

def gait_arms(phase, amp, run=False):
    """counter-swinging arms for walk/run."""
    sw = math.sin(2 * math.pi * phase) * amp
    L = blend_arm(arm_pose('relaxed'), arm_pose('relaxed'), 0)
    def sh(a, s, mir):
        a = {k: v.copy() for k, v in a.items()}
        if run:
            a['w'] = Vector((0.18 if not mir else -0.18, -0.25 - 0.35 * s, -0.42 + 0.12 * abs(s)))
            a['e'] = Vector((0.3 if not mir else -0.3, 1, -0.2))
        else:
            a['w'] = a['w'] + Vector((0, -0.28 * s, 0.05 * abs(s)))
        return a
    return sh(arm_pose('relaxed'), -sw, False), sh(arm_pose('relaxed', True), sw, True)

def line_path(a, b):
    a, b = Vector(a), Vector(b); L = (b - a).length
    return (lambda s: a.lerp(b, s / L if L > 0 else 0)), L

def stand_feet(actor, loc, yaw, width=1.0, ground=None, fwd=(0.0, 0.0)):
    """feet planted in a natural stance around root loc (world/parent space)."""
    J = actor.ch.J; out = {}
    Rz = Matrix.Rotation(math.radians(yaw), 3, 'Z')
    g = loc.z if ground is None else ground
    for sd, sg, fw in (('L', 1, fwd[0]), ('R', -1, fwd[1])):
        p = Vector((J[f'an.{sd}'].x * width, -fw * actor.H, 0))
        w = Vector(loc) + Rz @ p; w.z = g + J[f'an.{sd}'].z
        out[sd] = (w, yaw + sg * 8, 0)
    return out

def breathe(t, H, seed=0):
    return Vector((0, 0, 0.003 * H * math.sin(t * 2 * math.pi / 3.6 + seed)))

def idle_torso(t, seed=0, amt=1.0):
    return (1.5 * amt * C.noise1(t, seed, 0.35), 1.5 * amt * C.noise1(t, seed + 3, 0.3), 3 * amt * C.noise1(t, seed + 7, 0.25))

def talk_head(t, actor, amt=1.0):
    env, tk = actor.talking(t)
    n = C.noise1(t, actor.seed + 11, 1.6)
    return ((4 * n * env + 1.5 * C.noise1(t, actor.seed, 0.5)) * amt, 3 * C.noise1(t, actor.seed + 5, 0.6) * amt, 4 * C.noise1(t, actor.seed + 9, 0.4) * amt)

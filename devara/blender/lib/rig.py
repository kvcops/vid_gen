"""Procedural humanoid skeleton with exact FK and analytic 2-bone IK.

All posing is solved here in Python (not with Blender IK constraints) so we always *know* where every
joint lands: feet are placed exactly on the ground/deck, hands exactly on props. Results are written as
local quaternions on Blender pose bones, using the identity  L_b = M_b^-1 * R * M_b  (rotation parts),
where M_b is the bone rest matrix and R the desired rotation in armature space applied after the parent.

Character space: faces -Y, +X is the character's LEFT, +Z up.
"""
import bpy, math
from mathutils import Vector, Matrix, Quaternion, Euler

BONES = [  # name, parent, head-key, tail-key
    ('hips', None, 'pelvis', 'waist'), ('spine', 'hips', 'waist', 'chest'), ('chest', 'spine', 'chest', 'neck0'),
    ('neck', 'chest', 'neck0', 'neck1'), ('head', 'neck', 'neck1', 'crown'),
    ('shoulder.L', 'chest', 'clav.L', 'sh.L'), ('upperarm.L', 'shoulder.L', 'sh.L', 'el.L'),
    ('forearm.L', 'upperarm.L', 'el.L', 'wr.L'), ('hand.L', 'forearm.L', 'wr.L', 'hd.L'),
    ('shoulder.R', 'chest', 'clav.R', 'sh.R'), ('upperarm.R', 'shoulder.R', 'sh.R', 'el.R'),
    ('forearm.R', 'upperarm.R', 'el.R', 'wr.R'), ('hand.R', 'forearm.R', 'wr.R', 'hd.R'),
    ('thigh.L', 'hips', 'hip.L', 'kn.L'), ('shin.L', 'thigh.L', 'kn.L', 'an.L'), ('foot.L', 'shin.L', 'an.L', 'toe.L'),
    ('thigh.R', 'hips', 'hip.R', 'kn.R'), ('shin.R', 'thigh.R', 'kn.R', 'an.R'), ('foot.R', 'shin.R', 'an.R', 'toe.R'),
]

def joints(H, sh_w=0.118, hip_w=0.052, arm_angle=48, female=False, belly=0.0):
    """Joint positions (rest pose, A-pose arms) for a character of height H."""
    j = {}
    j['crown'] = Vector((0, 0.005 * H, H * 0.995))
    j['neck1'] = Vector((0, 0.012 * H, H * 0.845))
    j['neck0'] = Vector((0, 0.018 * H, H * 0.805))
    j['chest'] = Vector((0, 0.008 * H, H * 0.70))
    j['waist'] = Vector((0, 0.0, H * 0.60))
    j['pelvis'] = Vector((0, 0.0, H * 0.535))
    sw = sh_w * H * (0.86 if female else 1.0)
    for s, sg in (('L', 1), ('R', -1)):
        j[f'clav.{s}'] = Vector((sg * 0.02 * H, 0.012 * H, H * 0.80))
        sh = Vector((sg * sw, 0.015 * H, H * 0.79)); j[f'sh.{s}'] = sh
        a = math.radians(arm_angle)
        d = Vector((sg * math.sin(a), 0, -math.cos(a)))
        j[f'el.{s}'] = sh + d * (0.172 * H)
        j[f'wr.{s}'] = j[f'el.{s}'] + Vector((sg * math.sin(a) * 0.98, -0.02, -math.cos(a))).normalized() * (0.150 * H)
        j[f'hd.{s}'] = j[f'wr.{s}'] + Vector((sg * math.sin(a), -0.01, -math.cos(a))).normalized() * (0.095 * H)
        hw = hip_w * H * (1.12 if female else 1.0)
        j[f'hip.{s}'] = Vector((sg * hw, 0.0, H * 0.505))
        j[f'kn.{s}'] = Vector((sg * hw * 0.98, -0.012 * H, H * 0.285))
        j[f'an.{s}'] = Vector((sg * hw * 0.96, 0.0, H * 0.048))
        j[f'toe.{s}'] = Vector((sg * hw * 1.02, -0.135 * H * 0.6, H * 0.012))
    return j

def build_armature(name, J, coll=None):
    ad = bpy.data.armatures.new(name + '_arm'); ob = bpy.data.objects.new(name, ad)
    (coll or bpy.context.scene.collection).objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    eb = {}
    for n, par, h, t in BONES:
        b = ad.edit_bones.new(n); b.head = J[h]; b.tail = J[t]
        # deterministic roll: bone X axis points to character's left (or forward for vertical bones)
        b.align_roll(Vector((0, -1, 0)) if n.startswith(('thigh', 'shin', 'hips', 'spine', 'chest', 'neck', 'head', 'upper', 'fore', 'hand'))
                     else Vector((0, 0, 1)))
        if par: b.parent = eb[par]; b.use_connect = False
        eb[n] = b
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in ob.pose.bones: pb.rotation_mode = 'QUATERNION'
    return ob


class Skeleton:
    """Mirror of the armature's math. pose() computes local quats; apply() writes + keys them."""
    def __init__(self, arm_obj, J):
        self.ob = arm_obj; self.J = J
        self.rest = {b.name: b.matrix_local.copy() for b in arm_obj.data.bones}
        self.parent = {n: p for n, p, _, _ in BONES}
        self.order = [n for n, *_ in BONES]
        self.len = {b.name: b.length for b in arm_obj.data.bones}

    # ---- forward kinematics with armature-space deltas R (dict of Quaternion) ----
    def fk(self, R, hip_off=Vector()):
        """returns dict name -> (G 3x3 delta rotation, head position) in armature space"""
        out = {}
        for n in self.order:
            p = self.parent[n]; M = self.rest[n]
            r = R.get(n, Quaternion())
            if p is None:
                G = r.to_matrix(); head = M.translation + hip_off
            else:
                Gp, hp = out[p]; Mp = self.rest[p]
                head = hp + Gp @ (M.translation - Mp.translation)
                G = Gp @ r.to_matrix()
            out[n] = (G, head)
        return out

    def tail(self, F, n):
        G, h = F[n]; M = self.rest[n]
        return h + G @ (M.to_3x3() @ Vector((0, self.len[n], 0)))

    def rest_dir(self, n):
        return (self.rest[n].to_3x3() @ Vector((0, 1, 0))).normalized()

    def rest_x(self, n):
        return (self.rest[n].to_3x3() @ Vector((1, 0, 0))).normalized()

    # ---- analytic two-bone IK; writes R[a], R[b] ----
    def ik2(self, R, a, b, target, pole_dir, hip_off=Vector()):
        F = self.fk(R, hip_off)
        Gp = F[self.parent[a]][0] if self.parent[a] else Matrix.Identity(3)
        root = F[a][1]
        l1, l2 = self.len[a], self.len[b]
        d = target - root; dist = max(1e-4, min(d.length, (l1 + l2) * 0.9995))
        dn = d.normalized()
        # knee position in plane spanned by dn and pole
        cosA = max(-1, min(1, (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)))
        pole = (pole_dir - dn * pole_dir.dot(dn))
        if pole.length < 1e-5: pole = Vector((0, -1, 0)) - dn * dn.y
        pole.normalize()
        knee = root + dn * (l1 * cosA) + pole * (l1 * math.sqrt(max(0, 1 - cosA * cosA)))
        d1 = (knee - root).normalized(); d2 = (root + dn * dist - knee).normalized()
        # thigh: frame (bone dir, bend-plane dir) rest -> target
        R[a] = frame_rot(Gp.inverted() @ d1, Gp.inverted() @ pole, self.rest_dir(a), self._rest_bend(a, b))
        F = self.fk(R, hip_off); Ga = F[a][0]
        R[b] = frame_rot(Ga.inverted() @ d2, Ga.inverted() @ pole, self.rest_dir(b), self._rest_bend(a, b, child=True))
        return knee

    def _rest_bend(self, a, b, child=False):
        """reference 'pole' direction attached to the rest bones (perpendicular to bone)."""
        n = b if child else a
        d = self.rest_dir(n)
        ref = Vector((0, -1, 0)) if a.startswith('thigh') else Vector((0, 1, 0))
        if a.startswith('upperarm'): ref = Vector((0, 1, 0))  # elbows point back
        v = ref - d * ref.dot(d)
        return v.normalized()

    def set_world_rot(self, R, n, Wdelta, hip_off=Vector()):
        """make bone n have absolute armature-space delta rotation Wdelta (3x3) regardless of parents."""
        F = self.fk(R, hip_off); Gp = F[self.parent[n]][0]
        R[n] = (Gp.inverted() @ Wdelta).to_quaternion()

    # ---- write to blender ----
    def apply(self, R, hip_off, frame):
        for pb in self.ob.pose.bones:
            n = pb.name; r = R.get(n, Quaternion())
            M = self.rest[n].to_3x3()
            q = (M.inverted() @ r.to_matrix() @ M).to_quaternion()
            pb.rotation_quaternion = q
            pb.keyframe_insert('rotation_quaternion', frame=frame)
            if n == 'hips':
                pb.location = M.inverted() @ hip_off
                pb.keyframe_insert('location', frame=frame)


def frame_rot(d_tgt, p_tgt, d_rest, p_rest):
    """rotation taking orthonormal frame (d_rest, p_rest) to (d_tgt, p_tgt)."""
    def fr(d, p):
        d = d.normalized(); p = (p - d * p.dot(d)).normalized(); x = d.cross(p)
        return Matrix((d, p, x)).transposed()
    return (fr(d_tgt, p_tgt) @ fr(d_rest, p_rest).transposed()).to_quaternion()

def qx(deg): return Quaternion((1, 0, 0), math.radians(deg))
def qy(deg): return Quaternion((0, 1, 0), math.radians(deg))
def qz(deg): return Quaternion((0, 0, 1), math.radians(deg))
def qe(x=0, y=0, z=0):
    return Euler((math.radians(x), math.radians(y), math.radians(z)), 'ZXY').to_quaternion()

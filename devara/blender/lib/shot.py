"""Shot framework: timeline access, camera moves, talking-gesture helpers."""
import bpy, math, json, os
from mathutils import Vector, Matrix, Quaternion
from . import core as C
from . import acting as A

class Ctx:
    def __init__(self, shot, preset, root):
        self.shot = shot; self.preset = preset; self.root = root
        self.N = shot['frames']; self.dur = shot['dur']; self.ev = shot['events']
        self.sc = bpy.context.scene
        self.sc.frame_start, self.sc.frame_end = 1, self.N
        self.actors = {}

    def tag(self, tag):
        for e in self.ev:
            if e.get('tag') == tag: return e
        raise KeyError(tag)

    def t(self, tag, which='start'):
        return self.tag(tag)[which]

    def lines(self, speaker=None):
        return [e for e in self.ev if e['type'] == 'say' and (speaker is None or e['speaker'] == speaker)]

    def line(self, i):
        return [e for e in self.ev if e['type'] == 'say'][i]

    def asset(self, *p):
        return os.path.join(self.root, 'assets', *p)

    def cast(self, actor, speaker):
        """lip-sync actor to every line of speaker in this shot"""
        for e in self.lines(speaker): actor.say(e)


class Cam:
    """Keyframed camera: list of keys (t, pos, target, lens) with easing; optional handheld shake & roll."""
    def __init__(self, ctx, keys, shake=0.0, ease='inout', fstop=2.8, roll=None, dof=True, clip=(0.05, 3000)):
        self.ctx = ctx
        cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); C.link(cam)
        ctx.sc.camera = cam; self.cam = cam
        cd.sensor_width = 36; cd.clip_start, cd.clip_end = clip
        cd.dof.use_dof = dof; cd.dof.aperture_fstop = fstop
        self.keys = [(k[0], Vector(k[1]), Vector(k[2]), k[3]) for k in keys]
        self.shake = shake; self.ease = ease; self.roll = roll
        self.bake()

    def at(self, t):
        ks = self.keys
        if t <= ks[0][0]: _, p, g, l = ks[0]; return p, g, l
        for (t0, p0, g0, l0), (t1, p1, g1, l1) in zip(ks, ks[1:]):
            if t <= t1:
                e = C.seg(t, t0, t1, self.ease)
                return p0.lerp(p1, e), g0.lerp(g1, e), l0 + (l1 - l0) * e
        _, p, g, l = ks[-1]; return p, g, l

    def bake(self):
        cam = self.cam; cd = cam.data
        for f in range(1, self.ctx.N + 1):
            t = (f - 1) / C.FPS
            p, g, lens = self.at(t)
            if self.shake:
                p = p + Vector((C.noise1(t, 1, 1.3), C.noise1(t, 2, 1.1), C.noise1(t, 3, 1.2))) * self.shake
                g = g + Vector((C.noise1(t, 4, 0.9), C.noise1(t, 5, 0.8), C.noise1(t, 6, 0.9))) * self.shake * 0.6
            d = g - p
            q = d.to_track_quat('-Z', 'Y')
            r = self.roll(t) if callable(self.roll) else (self.roll or 0.0)
            if r: q = q @ Quaternion((0, 0, 1), math.radians(r))
            cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
            cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_quaternion', frame=f)
            cd.lens = lens; cd.keyframe_insert('lens', frame=f)
            cd.dof.focus_distance = d.length; cd.dof.keyframe_insert('focus_distance', frame=f)


GESTURES = ['explain', 'palm_out', 'point', 'shrug', 'chest', 'explain']

def talk_arms(actor, t, baseL, baseR, style=None, hand='R', amount=1.0):
    """Blend a gesture into one arm while the actor speaks (per line, smooth in/out)."""
    for i, (s, e, env) in enumerate(actor.lines):
        if s - 0.3 <= t <= e + 0.4:
            k = C.seg(t, s - 0.3, s + 0.15) * (1 - C.seg(t, e - 0.05, e + 0.4)) * amount
            g = (style[i % len(style)] if style else GESTURES[(i + actor.seed) % len(GESTURES)])
            if g is None: break
            mir = hand == 'R'
            gp = A.arm_pose(g, mir)
            # small beat motion with the speech energy
            idx = int((t - s) * C.FPS); en = env[idx] if 0 <= idx < len(env) else 0
            gp = {kk: v.copy() for kk, v in gp.items()}
            gp['w'] = gp['w'] + Vector((0, -0.05 * en, 0.06 * en))
            if hand == 'R': baseR = A.blend_arm(baseR, gp, k)
            else: baseL = A.blend_arm(baseL, gp, k)
            break
    return baseL, baseR

def standing(actor, loc, yaw, armL='relaxed', armR='relaxed', look=None, gest=None, hand='R', torso=(0, 0, 0), head=(0, 0, 0),
             expr=None, fist=(False, False), extra=None, ground=None, stance=1.0, idle=1.0):
    """Generic idle/talking pose function factory."""
    loc = Vector(loc)
    def fn(t):
        aL = A.arm_pose(armL) if isinstance(armL, str) else (armL(t) if callable(armL) else armL)
        aR = A.arm_pose(armR, True) if isinstance(armR, str) else (armR(t) if callable(armR) else armR)
        if gest is not False: aL, aR = talk_arms(actor, t, aL, aR, gest, hand)
        it = A.idle_torso(t, actor.seed, idle)
        th = A.talk_head(t, actor)
        tor = torso(t) if callable(torso) else torso
        hd = head(t) if callable(head) else head
        P = dict(root=(loc, yaw(t) if callable(yaw) else yaw), hip=A.breathe(t, actor.H, actor.seed),
                 torso=(tor[0] + it[0], tor[1] + it[1], tor[2] + it[2]),
                 head=(hd[0] + th[0], hd[1] + th[1], hd[2] + th[2]), armL=aL, armR=aR,
                 feet=A.stand_feet(actor, loc, yaw(t) if callable(yaw) else yaw, stance, ground),
                 look=look(t) if callable(look) else look, fistL=fist[0], fistR=fist[1])
        if expr: P['expr'] = expr(t) if callable(expr) else expr
        if extra: extra(t, P)
        return P
    return fn

def head_pos(ch):
    """world-ish position of a character's head (rest height) for look-at."""
    a = ch.arm
    return a.matrix_world @ Vector((0, 0, ch.hc.z))

def look_at_char(ch, dz=0.0):
    return lambda t: head_pos(ch) + Vector((0, 0, dz))

import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lib import core as C
from lib.chars import Character
from lib import acting as A
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
keys = argv[0].split(',') if argv else ['devara']
out = argv[1] if len(argv) > 1 else '//../out/test/char'
sc = C.reset_scene(); C.setup_render(sc, 'still')
C.world_color(sc, (0.35, 0.42, 0.55), (0.12, 0.1, 0.09), 0.6)
g = C.prim('plane', 'ground', size=40); C.assign(g, C.mat('gnd', (0.35, 0.3, 0.24), rough=0.9, noise=0.3))
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); C.link(sun); sun.data.energy = 3.2; sun.rotation_euler = (math.radians(50), 0, math.radians(30)); sun.data.angle = 0.05
fill = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'AREA')); C.link(fill); fill.data.energy = 300; fill.data.size = 4; fill.location = (-3, -4, 3); fill.rotation_euler = (math.radians(55), 0, math.radians(-35))
rim = bpy.data.objects.new('rim', bpy.data.lights.new('rim', 'AREA')); C.link(rim); rim.data.energy = 400; rim.data.size = 2; rim.location = (2, 4, 3); rim.rotation_euler = (math.radians(-60), 0, math.radians(150)); rim.data.color = (1, 0.85, 0.7)
chars = []
POSE_L = os.environ.get('POSE'); POSE_R = os.environ.get('POSE')
if POSE_L: POSE_L = [POSE_L] * 9; POSE_R = [POSE_R] * 9
for i, k in enumerate(keys):
    ch = Character(k); a = A.Actor(ch, seed=i + 1)
    x = (i - (len(keys) - 1) / 2) * 0.9
    def pose(t, a=a, x=x, i=i):
        loc = Vector((x, 0, 0))
        armL = A.arm_pose((POSE_L or ['hip', 'explain', 'cross', 'relaxed', 'point', 'shrug', 'fist_up', 'wave', 'down'])[i % 9])
        armR = A.arm_pose((POSE_R or ['hip', 'relaxed', 'cross_top', 'explain', 'down', 'shrug', 'hold_side', 'down', 'palm_out'])[i % 9], True)
        return dict(root=(loc, 0), hip=A.breathe(t, a.H), torso=(0, 0, 0), head=(0, 0, 0), armL=armL, armR=armR,
                    feet=A.stand_feet(a, loc, 0), expr=['fierce', 'happy', 'angry', 'wise', 'shocked', 'smug', 'laugh', 'worried', 'deadpan'][i % 9], fistR=i == 6)
    a.bake(1, 1, pose); chars.append(ch)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); C.link(cam); sc.camera = cam
tgt = C.empty('tgt', (0, 0, 1.0)); tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
W = max(1.6, len(keys) * 0.95)
views = {'front': ((0, -W * 2.2, 1.1), (0, 0, 0.95), 35), 'q34': ((W * 1.4, -W * 1.7, 1.4), (0, 0, 0.95), 35),
         'side': ((W * 2.3, 0, 1.0), (0, 0, 0.95), 35), 'back': ((-W * 1.0, W * 2.0, 1.4), (0, 0, 0.95), 35),
         'face': ((0.35, -1.25, 1.62), (chars[0].arm.location.x, 0, chars[0].hc.z), 50), 'feet': ((0.8, -1.6, 0.25), (0, 0, 0.12), 35)}
sel = argv[2].split(',') if len(argv) > 2 else list(views)
if 'hands' in sel:
    sel.remove('hands')
    ch = chars[0]; hx = ch.arm.location.x
    cam.location = (hx + 0.35, -1.7, 1.45); tgt.location = (hx, -0.2, 1.12); cam.data.lens = 45
    sc.frame_set(1); sc.render.filepath = f'{out}_hands.jpg'; bpy.ops.render.render(write_still=True)
if 'faces' in sel:
    sel.remove('faces')
    for ch in chars:
        hx = ch.arm.location.x; cam.location = (hx + 0.22, -0.95, ch.hc.z + 0.03); tgt.location = (hx, 0, ch.hc.z - 0.03); cam.data.lens = 55
        sc.frame_set(1); sc.render.filepath = f'{out}_face_{ch.key}.jpg'; bpy.ops.render.render(write_still=True)
if 'faces' in sel:
    sel.remove('faces')
    for ch in chars:
        hx = ch.arm.location.x; cam.location = (hx + 0.22, -0.95, ch.hc.z + 0.03); tgt.location = (hx, 0, ch.hc.z - 0.03); cam.data.lens = 55
        sc.frame_set(1); sc.render.filepath = f'{out}_face_{ch.key}.jpg'; bpy.ops.render.render(write_still=True)
for nm in sel:
    p, tg, lens = views[nm]
    cam.location = p; tgt.location = tg; cam.data.lens = lens
    if nm == 'face':
        hx = chars[0].arm.location.x; cam.location = (hx + 0.25, -0.95, chars[0].hc.z + 0.03); tgt.location = (hx, 0, chars[0].hc.z - 0.02); cam.data.lens = 60
    sc.frame_set(1); sc.render.filepath = f'{out}_{nm}.jpg'; bpy.ops.render.render(write_still=True)

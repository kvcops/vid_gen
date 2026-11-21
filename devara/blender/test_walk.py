import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lib import core as C
from lib.chars import Character
from lib import acting as A
argv = sys.argv[sys.argv.index('--') + 1:]
key, run = argv[0], argv[1] == 'run'
sc = C.reset_scene(); C.setup_render(sc, 'preview')
C.world_color(sc, (0.35, 0.42, 0.55), (0.12, 0.1, 0.09), 0.6)
g = C.prim('plane', 'ground', size=40); C.assign(g, C.mat('gnd', (0.35, 0.3, 0.24), rough=0.9, noise=0.3))
for i in range(-10, 11):  # floor grid lines to judge foot sliding
    l = C.prim('cube', 'line', loc=(i * 0.5, 0, 0.001), scale=(0.005, 20, 0.001)); C.assign(l, C.mat('ln', (0.1, 0.1, 0.1)))
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); C.link(sun); sun.data.energy = 3.5; sun.rotation_euler = (math.radians(50), 0, math.radians(30))
ch = Character(key); a = A.Actor(ch)
dist = 4.0 if not run else 7.0; T = 4.0
path, L = A.line_path((-dist / 2, 0, 0), (dist / 2, 0, 0))
s_of_t = lambda t: L * C.ease(min(1, max(0, (t - 0.3) / (T - 0.6))), 'smooth')
G = A.Gait(a, path, s_of_t, L, run=run)
def pose(t):
    g = G.at(t); armL, armR = A.gait_arms(g['phase'], g['amp'], run)
    return dict(root=g['root'], feet=g['feet'], hip=g['hip'], torso=(8 * g['amp'] if run else 2 * g['amp'], 0, 6 * math.sin(2 * math.pi * g['phase']) * g['amp']),
                head=(-6 * g['amp'] if run else 0, 0, 0), armL=armL, armR=armR, fistL=run, fistR=run, expr='fierce' if run else 'neutral')
N = int(T * 24); a.bake(1, N, pose)
sc.frame_start, sc.frame_end = 1, N
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); C.link(cam); sc.camera = cam
cam.rotation_euler = (math.radians(86), 0, 0); cam.data.lens = 40
for f in range(1, N + 1):
    cam.location = (path(s_of_t((f - 1) / 24)).x, -4.2, 0.95); cam.keyframe_insert('location', frame=f)
sc.render.filepath = f'//../out/test/walk_{key}_{argv[1]}_'
sc.render.image_settings.file_format = 'JPEG'
frames = [int(x) for x in argv[2].split(',')] if len(argv) > 2 else range(1, N + 1)
for f in frames:
    sc.frame_set(f); sc.render.filepath = f'//../out/test/walk_{key}_{argv[1]}_{f:03d}.jpg'; bpy.ops.render.render(write_still=True)

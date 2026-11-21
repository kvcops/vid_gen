"""blender -b --factory-startup --python run_shot.py -- <shot_id> <preset> [frames] [outdir]
frames: 'all' | '10,50,90' | '1-120'"""
import bpy, sys, os, json, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lib import core as C
from lib.shot import Ctx
argv = sys.argv[sys.argv.index('--') + 1:]
sid, preset = argv[0], argv[1]
frames = argv[2] if len(argv) > 2 else 'all'
outdir = os.path.join(ROOT, argv[3]) if len(argv) > 3 else os.path.join(ROOT, 'out', 'frames', sid)
os.makedirs(outdir, exist_ok=True)
TL = json.load(open(os.path.join(ROOT, 'audio', 'timeline.json'), encoding='utf-8'))
shot = [s for s in TL['shots'] if s['id'] == sid][0]
t0 = time.time()
C.reset_scene(); sc = bpy.context.scene; C.setup_render(sc, preset)
ctx = Ctx(shot, preset, ROOT)
import shots
getattr(shots, sid)(ctx)
import cams
if sid in cams.CAMS:
    from lib.shot import Cam
    for o in [o for o in bpy.data.objects if o.type == 'CAMERA']: bpy.data.objects.remove(o, do_unlink=True)
    action = sid in ('s16', 's20', 's22', 's23', 's26')
    Cam(ctx, cams.CAMS[sid](ctx), shake=0.012 if action else 0.005, fstop=3.5, ease='inout')
print(f'BUILD {sid} {time.time() - t0:.1f}s frames={ctx.N}', flush=True)
if frames == 'none':
    print('BUILDONLY ok', flush=True); sys.exit(0)
if frames == 'all': fl = list(range(1, ctx.N + 1))
elif '-' in frames: a, b = frames.split('-'); fl = list(range(int(a), min(ctx.N, int(b)) + 1))
else: fl = [min(ctx.N, max(1, int(x))) for x in frames.split(',')]
if frames == 'all' or '-' in frames:
    sc.frame_start, sc.frame_end = fl[0], fl[-1]
    sc.render.filepath = os.path.join(outdir, '')
    sc.render.use_file_extension = True
    bpy.ops.render.render(animation=True)
else:
    for f in fl:
        sc.frame_set(f); sc.render.filepath = os.path.join(outdir, f'{sid}_{f:04d}.jpg'); bpy.ops.render.render(write_still=True)
print(f'DONE {sid} {time.time() - t0:.1f}s', flush=True)

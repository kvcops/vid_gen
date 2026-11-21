"""On the render node: python3 blender/render_batch.py <0|1>  -> renders its share of shots at final quality (resumable)."""
import json, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
half = int(sys.argv[1])
TL = json.load(open(os.path.join(ROOT, 'audio', 'timeline.json'), encoding='utf-8'))
heavy = {'s01': 2, 's02': 2, 's03': 2, 's04': 2}  # rain + volumes
shots = sorted(TL['shots'], key=lambda s: -s['frames'] * heavy.get(s['id'], 1))
loads = [0, 0]; mine = []
for s in shots:
    i = loads.index(min(loads)); loads[i] += s['frames'] * heavy.get(s['id'], 1)
    if i == half: mine.append(s)
for s in mine:
    d = os.path.join(ROOT, 'out', 'frames', s['id'])
    have = len([f for f in os.listdir(d) if f.endswith('.jpg')]) if os.path.isdir(d) else 0
    if have >= s['frames']: print(s['id'], 'done already', flush=True); continue
    t = time.time()
    r = subprocess.run([os.environ['BLENDER'], '-b', '--factory-startup', '--python', os.path.join(ROOT, 'blender', 'run_shot.py'), '--', s['id'], 'final', 'all'],
                       capture_output=True, text=True)
    err = [l for l in (r.stdout + r.stderr).splitlines() if 'Error' in l or 'Traceback' in l]
    n = len([f for f in os.listdir(d) if f.endswith('.jpg')]) if os.path.isdir(d) else 0
    print(f"{s['id']} {n}/{s['frames']} frames {time.time() - t:.0f}s {' | '.join(err[-2:])}", flush=True)
print('ALLDONE', flush=True)

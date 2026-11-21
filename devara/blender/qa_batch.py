"""Run on the render node: python3 blender/qa_batch.py <gpu-index-of-2> -> renders 3 QA stills for its half of the shots."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
half = int(sys.argv[1]); only = sys.argv[2].split(',') if len(sys.argv) > 2 else None
TL = json.load(open(os.path.join(ROOT, 'audio', 'timeline.json'), encoding='utf-8'))
shots = [s for s in TL['shots'] if (only is None or s['id'] in only)]
mine = shots[half::2]
for s in mine:
    n = s['frames']; fr = ','.join(str(max(1, int(n * k))) for k in (0.2, 0.55, 0.9))
    r = subprocess.run([os.environ['BLENDER'], '-b', '--factory-startup', '--python', os.path.join(ROOT, 'blender', 'run_shot.py'), '--', s['id'], 'still', fr, 'out/qa'],
                       capture_output=True, text=True)
    tail = [l for l in (r.stdout + r.stderr).splitlines() if 'Error' in l or 'Traceback' in l or l.startswith(('BUILD', 'DONE'))]
    print(s['id'], ' | '.join(tail[-4:]), flush=True)

"""Assemble rendered frames + dialogue into the final film (runs on the render node or locally).
python3 blender/assemble.py  ->  out/devara2_part1.mp4  (+ out/devara2_part1_silent.mp4 for BGM mixing)"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, 'audio', 'timeline.json'), encoding='utf-8'))
OUT = os.path.join(ROOT, 'out'); CL = os.path.join(OUT, 'clips'); os.makedirs(CL, exist_ok=True)
FADE_IN = {'s01': 0.8, 's06': 0.4, 's10': 0.5, 's13': 0.4, 's21': 0.5, 's34': 0.5, 's35': 0.6}
FADE_OUT = {'s04': 0.3, 's05': 0.5, 's09': 0.5, 's12': 0.6, 's14': 0.4, 's20': 0.5, 's33': 0.8, 's35': 1.0}

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); sys.exit(1)

PARTIAL = len(sys.argv) > 1 and sys.argv[1] == 'clips'   # just build clips for finished shots
lst = []
for s in TL['shots']:
    sid, n, d = s['id'], s['frames'], s['frames'] / TL['fps']
    fdir = os.path.join(OUT, 'frames', sid)
    have = len([f for f in os.listdir(fdir) if f.endswith('.jpg')]) if os.path.isdir(fdir) else 0
    if have < n:
        if PARTIAL: print(f'skip {sid}: {have}/{n}'); continue
        if os.path.exists(os.path.join(CL, f'{sid}.mp4')): lst.append(os.path.join(CL, f'{sid}.mp4')); continue
        print(f'!! {sid}: {have}/{n} frames'); sys.exit(1)
    if os.path.exists(os.path.join(CL, f'{sid}.mp4')) and PARTIAL: lst.append(os.path.join(CL, f'{sid}.mp4')); continue
    vf = []
    if sid in FADE_IN: vf.append(f'fade=t=in:st=0:d={FADE_IN[sid]}')
    if sid in FADE_OUT: vf.append(f'fade=t=out:st={d - FADE_OUT[sid]:.3f}:d={FADE_OUT[sid]}')
    out = os.path.join(CL, f'{sid}.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(TL['fps']), '-i', os.path.join(fdir, '%04d.jpg'), '-frames:v', str(n)]
    if vf: cmd += ['-vf', ','.join(vf)]
    cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-r', str(TL['fps']), out]
    run(cmd); lst.append(out); print('clip', sid, n)
if PARTIAL: print('CLIPS_DONE'); sys.exit(0)
cat = os.path.join(CL, 'list.txt'); open(cat, 'w').write(''.join(f"file '{p}'\n" for p in lst))
silent = os.path.join(OUT, 'devara2_part1_silent.mp4')
run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', cat, '-c', 'copy', silent])
final = os.path.join(OUT, 'devara2_part1.mp4')
run(['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', os.path.join(ROOT, 'audio', 'dialogue.wav'),
     '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', final])
print('FINAL', final)

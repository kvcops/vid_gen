"""Fit regenerated lines into the existing (already-animated) timeline slots and mix a dialogue track.
usage: python tools/fit_dialogue.py <raw_dir_name> <out_name>    e.g.  raw_f5 dialogue_f5
Each line keeps its original start time; it is time-stretched (rubberband, pitch-preserving) only as much as needed:
 - longer than the free space before the next line -> compressed (max 1.35x)
 - much shorter than the original slot -> slightly slowed (max 0.85x) so lips & gestures still match."""
import os, sys, json, subprocess, tempfile, wave
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.stdout.reconfigure(encoding='utf-8')
SR = 48000
FX = {'DEVARA': 'rubberband=pitch=0.94:formant=preserved,lowshelf=g=3:f=150',
      'VARA_FAKE': 'rubberband=pitch=0.86:formant=preserved,lowshelf=g=4:f=170',
      'YETHI': 'rubberband=pitch=0.92:formant=preserved,aecho=0.8:0.55:45:0.15',
      'KUNJARA': 'rubberband=pitch=1.08:formant=preserved'}

def ff(inp, out, af):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', inp] + (['-af', af] if af else []) + ['-ar', str(SR), '-ac', '1', '-sample_fmt', 's16', out]
    subprocess.run(cmd, check=True)

def read(f):
    w = wave.open(f); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

def trim(x, thr=0.01, pad=0.04):
    win = SR // 100; n = len(x) // win
    if n == 0: return x
    rms = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1)); idx = np.where(rms > thr)[0]
    if not len(idx): return x
    a = max(0, idx[0] * win - int(pad * SR)); b = min(len(x), (idx[-1] + 1) * win + int(pad * 2 * SR))
    y = x[a:b].copy(); f = SR // 100; y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y

def main(raw, outname):
    TL = json.load(open(os.path.join(ROOT, 'audio', 'timeline.json'), encoding='utf-8'))
    tmp = tempfile.mkdtemp(); outdir = os.path.join(ROOT, 'audio', 'fit_' + raw); os.makedirs(outdir, exist_ok=True)
    total = TL['total']; mix = np.zeros(int(total * SR) + SR, np.float32); report = []
    for s in TL['shots']:
        says = [e for e in s['events'] if e['type'] == 'say']
        for i, e in enumerate(says):
            src = os.path.join(ROOT, 'audio', raw, e['file'] + '.wav')
            if not os.path.exists(src): src = src[:-4] + '.mp3'
            if not os.path.exists(src): print('MISSING', e['file']); continue
            a = os.path.join(tmp, 'a.wav'); ff(src, a, FX.get(e['speaker'], ''))
            x = trim(read(a)); d = len(x) / SR
            nxt = says[i + 1]['start'] if i + 1 < len(says) else s['dur']
            avail = max(0.3, nxt - e['start'] - 0.12); orig = e['end'] - e['start']
            tempo = 1.0
            if d > avail: tempo = min(1.35, d / avail)
            elif d < 0.75 * orig: tempo = max(0.85, d / (0.85 * orig))
            if abs(tempo - 1) > 0.01:
                b = os.path.join(tmp, 'b.wav'); open(b, 'wb').close()
                import soundfile as sf; sf.write(a, x, SR)
                ff(a, b, f'rubberband=tempo={tempo:.4f}:pitchq=quality'); x = read(b)
            out = os.path.join(outdir, e['file'] + '.wav'); import soundfile as sf; sf.write(out, x, SR)
            st = int((s['start'] + e['start']) * SR); mix[st:st + len(x)] += x[:len(mix) - st]
            report.append((e['file'], e['speaker'], round(d, 2), round(orig, 2), round(avail, 2), round(tempo, 2), round(len(x) / SR, 2)))
    peak = np.abs(mix).max(); mix *= 0.89 / max(1e-6, peak)
    import soundfile as sf; sf.write(os.path.join(ROOT, 'audio', outname + '.wav'), mix, SR, subtype='PCM_16')
    over = [r for r in report if r[6] > r[4] + 0.05]
    print(f'{outname}: {len(report)} lines, stretched {sum(1 for r in report if r[5] != 1.0)}, still overlapping {len(over)}')
    for r in over: print('  overlap', r)
    json.dump(report, open(os.path.join(ROOT, 'audio', outname + '_fit.json'), 'w'), indent=0)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

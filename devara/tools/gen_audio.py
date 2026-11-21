"""Generate every dialogue line with HeyGen (heygen-voice-1-turbo-free), then build the master timeline.

Outputs
  audio/lines/<shot>_<n>.wav      trimmed 48 kHz mono clips (cached by text+voice hash)
  audio/timeline.json             per-shot timing, line events, per-frame mouth envelopes
  audio/dialogue.wav              full mixed dialogue stem (BGM gets added later)
"""
import os, sys, json, hashlib, subprocess, wave
import numpy as np
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, os.path.join(ROOT, 'story'))
from tts import tts
from translit import te2dev
import importlib, script; importlib.reload(script)
sys.stdout.reconfigure(encoding='utf-8')

SR, FPS = 48000, 24
LINES = os.path.join(ROOT, 'audio', 'lines'); CACHE = os.path.join(ROOT, 'audio', 'cache')
os.makedirs(LINES, exist_ok=True); os.makedirs(CACHE, exist_ok=True)

def read(f):
    w = wave.open(f); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x, w.getframerate()

def write(f, x):
    x = np.clip(x, -1, 1); w = wave.open(f, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()

def trim(x, thr=0.012, pad=0.05):
    win = int(SR * 0.01); n = len(x) // win
    rms = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1))
    idx = np.where(rms > thr)[0]
    if not len(idx): return x
    a = max(0, idx[0] * win - int(pad * SR)); b = min(len(x), (idx[-1] + 1) * win + int(pad * 2 * SR))
    y = x[a:b].copy(); f = int(0.01 * SR)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y

def envelope(x):
    hop = SR // FPS; n = int(np.ceil(len(x) / hop))
    e = np.array([np.sqrt((x[i * hop:(i + 1) * hop] ** 2).mean()) if len(x[i * hop:(i + 1) * hop]) else 0 for i in range(n)])
    e = e / (np.percentile(e, 95) + 1e-6); e = np.clip(e, 0, 1.2)
    sm = np.convolve(e, [0.25, 0.5, 0.25], 'same')
    return [round(float(v), 3) for v in sm]

def job(item):
    key, spk, text = item
    vid = script.CAST[spk][0]; fx = script.FX.get(spk, '')
    h = hashlib.md5(f'{vid}|{text}|{fx}'.encode()).hexdigest()[:12]
    raw = os.path.join(CACHE, h + '.wav')
    if not os.path.exists(raw):
        tts(vid, te2dev(text), raw, lang='hi')
        if fx:
            tmp = raw + '.fx.wav'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', fx, '-ar', str(SR), '-ac', '1', tmp], check=True)
            os.replace(tmp, raw)
    x, sr = read(raw); assert sr == SR, sr
    y = trim(x); out = os.path.join(LINES, key + '.wav'); write(out, y)
    return key, len(y) / SR

def main():
    items = []
    for sh in script.SHOTS:
        n = 0
        for b in sh['beats']:
            if b[0] == 'say':
                items.append((f"{sh['id']}_{n:02d}", b[1], b[2])); n += 1
    print('lines:', len(items))
    with ThreadPoolExecutor(6) as ex: durs = dict(ex.map(job, items))

    tl, gt = [], 0.0
    master = []
    for sh in script.SHOTS:
        t, n, ev = 0.0, 0, []
        for b in sh['beats']:
            if b[0] == 'say':
                o = b[3]; key = f"{sh['id']}_{n:02d}"; n += 1
                t += o.get('pre', 0.12); d = durs[key]
                x, _ = read(os.path.join(LINES, key + '.wav'))
                ev.append(dict(type='say', speaker=b[1], text=b[2], start=round(t, 3), end=round(t + d, 3),
                               tag=o.get('tag'), file=key, env=envelope(x)))
                master.append((gt + t, x)); t += d + o.get('post', 0.35)
            else:
                ev.append(dict(type='wait', start=round(t, 3), end=round(t + b[1], 3), tag=b[2])); t += b[1]
        frames = int(round(t * FPS))
        tl.append(dict(id=sh['id'], set=sh['set'], desc=sh['desc'], start=round(gt, 3), dur=round(frames / FPS, 3),
                       frames=frames, events=ev))
        gt += frames / FPS
    json.dump(dict(fps=FPS, total=round(gt, 3), shots=tl), open(os.path.join(ROOT, 'audio', 'timeline.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    mix = np.zeros(int(gt * SR) + SR)
    for st, x in master:
        a = int(st * SR); mix[a:a + len(x)] += x
    mix *= 0.89 / max(1e-6, np.abs(mix).max())
    write(os.path.join(ROOT, 'audio', 'dialogue.wav'), mix)
    print(f'total {gt:.1f}s = {gt/60:.2f} min, {len(tl)} shots')
    for s in tl: print(s['id'], s['frames'], round(s['dur'], 1))

if __name__ == '__main__':
    main()

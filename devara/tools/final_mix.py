"""Final cut: Veo intro/outro (with Telugu titles) + film + layered soundtrack (dialogue, Veo audio, ambience, SFX, ducked BGM).
python tools/final_mix.py  ->  out/devara2_part1_final.mp4"""
import os, sys, json, subprocess, tempfile
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
sys.stdout.reconfigure(encoding='utf-8')
SR = 48000
TL = json.load(open('audio/timeline.json', encoding='utf-8'))
SH = {s['id']: s for s in TL['shots']}
FILM = 'out/devara2_part1_silent.mp4'
INTRO, OUTRO = 'media/veo_intro.mp4', 'media/veo_outro.mp4'
MUSIC = 'media/bgm_loose_cannon.mp3'
A_END = SH['s05']['start']; C_START = SH['s06']['start']; C_END = SH['s35']['start']
INTRO_NORMAL, INTRO_SLOW, SLOW = 7.5, 2.5, 2.0          # last 2.5 s of the Veo intro slowed 2x -> title hold
B_LEN = INTRO_NORMAL + INTRO_SLOW * SLOW                # 12.5 s
D_PAD = 2.5; D_LEN = 10.0 + D_PAD                       # outro + held last frame
OFF = B_LEN - SH['s05']['dur']                          # shift for everything after the intro
TOTAL = A_END + B_LEN + (C_END - C_START) + D_LEN
B_AT = A_END; D_AT = A_END + B_LEN + (C_END - C_START)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(' '.join(cmd)[:300]); print(r.stderr[-3000:]); sys.exit(1)

def load(path, start=None, dur=None, af=None):
    t = os.path.join(tempfile.gettempdir(), 'fm_tmp.wav')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error']
    if start is not None: cmd += ['-ss', f'{start:.4f}']
    if dur is not None: cmd += ['-t', f'{dur:.4f}']
    cmd += ['-i', path, '-vn'] + (['-af', af] if af else []) + ['-ar', str(SR), '-ac', '2', t]
    run(cmd); x, _ = sf.read(t, dtype='float32'); return x if x.ndim == 2 else np.stack([x, x], 1)

def T(shot, t):  # shot-relative time -> final timeline seconds
    s = SH[shot]; base = s['start'] + (OFF if s['start'] >= C_START else 0)
    return base + t

def tag(shot, name, which='start'):
    for e in SH[shot]['events']:
        if e.get('tag') == name: return e[which]
    raise KeyError(shot + ':' + name)

def put(buf, x, at, gain=1.0):
    a = int(at * SR)
    if a < 0: x = x[-a:]; a = 0
    n = min(len(x), len(buf) - a)
    if n > 0: buf[a:a + n] += x[:n] * gain

def fades(x, fi=0.25, fo=0.25):
    x = x.copy(); n1, n2 = int(fi * SR), int(fo * SR)
    if n1: x[:n1] *= np.linspace(0, 1, n1)[:, None]
    if n2: x[-n2:] *= np.linspace(1, 0, n2)[:, None]
    return x

def tile(x, n, xf=1.5):
    """loop a bed to n samples with equal-power crossfades."""
    f = int(xf * SR); out = np.zeros((n, 2), np.float32); pos = 0; first = True
    while pos < n:
        seg = x.copy()
        if not first: seg[:f] *= np.sqrt(np.linspace(0, 1, f))[:, None]
        seg[-f:] *= np.sqrt(np.linspace(1, 0, f))[:, None]
        m = min(len(seg), n - pos); out[pos:pos + m] += seg[:m]; pos += len(seg) - f; first = False
    return out

N = int(TOTAL * SR) + SR
dlg = np.zeros((N, 2), np.float32); veo = np.zeros_like(dlg); amb = np.zeros_like(dlg); fx = np.zeros_like(dlg); bgm = np.zeros_like(dlg)

# ---------------- dialogue (ElevenLabs track), split around the replaced title/end cards
D = load('audio/dialogue.wav')
put(dlg, D[:int(A_END * SR)], 0)
put(dlg, D[int(C_START * SR):int(C_END * SR)], A_END + B_LEN)

# ---------------- Veo audio
vi = np.concatenate([load(INTRO, 0, INTRO_NORMAL), load(INTRO, INTRO_NORMAL, INTRO_SLOW, f'rubberband=tempo={1 / SLOW}')])
put(veo, fades(vi, 0.05, 0.6), B_AT, 0.42)
vo = load(OUTRO); vo = np.concatenate([vo, np.zeros((int(D_PAD * SR), 2), np.float32)])
put(veo, fades(vo, 0.3, 2.0), D_AT, 0.45)

# ---------------- ambience beds per location
SFXD = 'audio/sfx/'
def rms_norm(x, db=-30.0):
    r = np.sqrt((x ** 2).mean()) + 1e-9; return x * (10 ** (db / 20) / r)
def peak_norm(x, db=-6.0):
    return x * (10 ** (db / 20) / (np.abs(x).max() + 1e-9))
beds = {n: rms_norm(load(SFXD + n + '.mp3')) for n in ('amb_storm', 'amb_sea_night', 'amb_rocks', 'amb_island', 'amb_village', 'amb_hut', 'amb_torch', 'amb_boat_creak')}
LOC = {**{s: [('amb_storm', 0.55)] for s in ('s01', 's02', 's03', 's04')},
       **{s: [('amb_hut', 0.35)] for s in ('s06', 's07', 's08', 's09', 's34')},
       **{s: [('amb_rocks', 0.4)] for s in ('s10', 's11', 's12')},
       **{s: [('amb_island', 0.4)] for s in ('s13', 's14')},
       **{s: [('amb_village', 0.35)] for s in ('s15', 's16', 's17', 's18', 's19', 's20')},
       **{s: [('amb_sea_night', 0.38), ('amb_torch', 0.22), ('amb_boat_creak', 0.16)] for s in
          ('s21', 's22', 's23', 's24', 's25', 's26', 's27', 's28', 's29')},
       **{s: [('amb_sea_night', 0.4), ('amb_boat_creak', 0.14), ('amb_torch', 0.1)] for s in ('s30', 's31', 's32', 's33')}}
for sid, layers in LOC.items():
    d = SH[sid]['dur']
    for name, g in layers:
        seg = tile(beds[name], int((d + 0.3) * SR))
        put(amb, fades(seg, 0.3, 0.3), T(sid, -0.15), g)

# ---------------- spot effects (times are shot-relative, matching the animation code)
EV = []
def ev(shot, t, name, g=0.8): EV.append((shot, t, name, g))
for t, n in ((0.15, 'thunder1'), (1.75, 'thunder2'), (4.6, 'thunder1'), (6.9, 'thunder2')): ev('s01', t, n, 0.9)
tn = tag('s02', 'name')
for t, n in ((0.6, 'thunder2'), (tn - 0.05, 'thunder1'), (tn + 0.9, 'thunder2')): ev('s02', t, n, 0.9)
for t, n in ((0.48, 'thunder1'), (3.1, 'thunder2')): ev('s03', t, n, 0.85)
ts4 = tag('s04', 'stab') + 0.45
ev('s04', ts4 - 0.05, 'thunder1', 0.95); ev('s04', SH['s04']['dur'] - 1.0, 'thunder2', 0.7); ev('s04', ts4, 'stab_thunk', 0.7)
ev('s07', 0.45, 'tea_sip', 0.7); ev('s07', 1.3, 'glass_table', 0.6)
ev('s34', tag('s34', 'sip') + 0.25, 'tea_sip', 0.7); ev('s34', tag('s34', 'sip') + 1.25, 'glass_table', 0.6)
ev('s10', 0.85, 'stab_thunk', 0.85); ev('s10', tag('s10', 'pull'), 'cloth_rustle', 0.6)
tsh = tag('s13', 'shark')
ev('s13', tsh - 0.3, 'shark_leap', 0.8); ev('s13', tsh, 'whoosh_small', 0.6); ev('s13', tsh + 1.35, 'splash_med', 0.8)
td = tag('s14', 'drop'); tb = td + 0.85
ev('s14', td, 'coconut_fall', 0.7); ev('s14', tb, 'bonk', 1.0); ev('s14', tb + 0.1, 'dizzy', 0.6); ev('s14', tb + 0.7, 'sand_thud', 0.7)
ev('s15', tag('s15', 'lift') - 0.7, 'log_lift', 0.75)
tg, tpo, tt = tag('s16', 'grab'), tag('s16', 'poster'), tag('s16', 'toss')
ev('s16', 0.0, 'run_sand', 0.7); ev('s16', tg, 'cloth_rustle', 0.7); ev('s16', tpo - 0.4, 'paper', 0.7)
ev('s16', tt, 'whoosh_big', 0.8); ev('s16', tt + 1.05, 'net_land', 0.9)
ev('s18', 0.0, 'walk_sand', 0.6); ev('s19', 0.2, 'basket', 0.7)
tf = tag('s20', 'flip')
ev('s20', tf - 0.9, 'cloth_rustle', 0.6); ev('s20', tf, 'whoosh_big', 0.8); ev('s20', tf + 0.75, 'body_sand', 1.0); ev('s20', tf + 1.25, 'sand_thud', 0.7)
tsn = tag('s22', 'sneeze') + 0.75
ev('s22', tsn, 'whoosh_small', 0.7); ev('s22', tsn + 1.55, 'splash_small', 0.9)
tl24, tf24 = tag('s24', 'lunge'), tag('s24', 'fight')
ev('s24', tl24 + 1.8, 'boat_jump', 0.9); ev('s24', tf24 + 0.55, 'whoosh_small', 0.7); ev('s24', tf24 + 0.75, 'axe_chop', 0.9)
ev('s24', tf24 + 1.85, 'punch', 1.0); ev('s24', tf24 + 1.9, 'whoosh_big', 0.6); ev('s24', tf24 + 2.7, 'splash_med', 0.9)
tb25 = tag('s25', 'burst')
ev('s25', 0.0, 'rumble_under', 0.9); ev('s25', 2.6, 'rumble_under', 0.8); ev('s25', tb25 - 1.4, 'wave_rise', 0.9); ev('s25', tb25, 'splash_big', 1.0)
ev('s26', 0.2, 'splash_med', 0.8); ev('s26', 0.25, 'deck_land', 1.0)
tsi = tag('s28', 'spit')
ev('s28', 0.4, 'whoosh_blade', 0.9); ev('s28', 0.9, 'metal_break', 1.0); ev('s28', 0.95, 'whoosh_big', 0.6)
for t in (1.8, 2.0, 2.1): ev('s28', t, 'splash_med', 0.7)
ev('s28', tsi, 'shark_leap', 0.8); ev('s28', tsi + 0.2, 'whoosh_big', 0.6); ev('s28', tsi + 1.3, 'deck_land', 0.9)
ev('s30', 0.0, 'foghorn', 1.0); ev('s30', 1.5, 'ship_creak', 0.6)
ev('s31', tag('s31', 'reveal') - 0.1, 'hood', 0.7); ev('s32', 0.5, 'ship_creak', 0.4); ev('s33', 2.6, 'thunder1', 0.9)
cache = {}
for shot, t, name, g in EV:
    if name not in cache: cache[name] = fades(peak_norm(load(SFXD + name + '.mp3'), -8.0 if not name.startswith(('thunder', 'splash_big', 'wave_rise', 'rumble', 'foghorn')) else -9.0), 0.005, 0.08)
    put(fx, cache[name], T(shot, t), g)
print('placed', len(EV), 'sound effects')

# ---------------- BGM: loop the 3-min track to full length, soft, ducked under speech, lower under the Veo clips
M = rms_norm(load(MUSIC), -20.0)
mus = tile(M, N, xf=4.0)
hop = SR // 100
spk = np.abs(dlg[:, 0]); nb = len(spk) // hop
e = spk[:nb * hop].reshape(nb, hop).mean(1)          # 10 ms speech-energy envelope
sm = np.zeros_like(e); a_att, a_rel = 1 - np.exp(-1 / 5), 1 - np.exp(-1 / 45)
for i in range(1, len(e)):
    sm[i] = sm[i - 1] + (a_att if e[i] > sm[i - 1] else a_rel) * (e[i] - sm[i - 1])
duck = 1 - 0.55 * np.clip(sm / (np.percentile(sm[sm > 0], 60) + 1e-6), 0, 1)
duck = np.interp(np.arange(N) / hop, np.arange(len(duck)), duck).astype(np.float32)
base = np.full(N, 0.24, np.float32)
for at, ln in ((B_AT, B_LEN), (D_AT, D_LEN)):
    a, b = int(at * SR), int((at + ln) * SR); base[a:b] = 0.08
k = SR // 2; cs = np.cumsum(np.concatenate([np.zeros(k, np.float32), base, np.full(k, base[-1], np.float32)]))
base = ((cs[2 * k:] - cs[:-2 * k]) / (2 * k))[:N].astype(np.float32)  # smooth level changes
fin = np.ones(N, np.float32); fo = int(4 * SR); fin[int(TOTAL * SR) - fo:int(TOTAL * SR)] = np.linspace(1, 0, fo); fin[int(TOTAL * SR):] = 0
bgm = mus * (base * duck * fin)[:, None]

# ---------------- mix
mix = dlg * 1.0 + veo + amb + fx * 0.5 + bgm
pk = np.abs(mix).max(); mix *= min(1.0, 0.95 / pk)
for name, x in (('dialogue', dlg), ('sfx', fx + amb), ('bgm', bgm), ('veo', veo)):
    sf.write(f'audio/stem_{name}.wav', np.clip(x, -1, 1), SR, subtype='PCM_16')
sf.write('audio/final_mix.wav', mix, SR, subtype='PCM_24')
print(f'audio ok: {TOTAL:.2f}s')

# ---------------- picture
fc = (
 f"[0:v]trim=0:{A_END:.4f},setpts=PTS-STARTPTS,fps=24[a];"
 f"[1:v]scale=1920:1080:flags=lanczos,unsharp=5:5:0.6,fps=24,split[i1][i2];"
 f"[i1]trim=0:{INTRO_NORMAL},setpts=PTS-STARTPTS[b1];"
 f"[i2]trim={INTRO_NORMAL}:10,setpts={SLOW}*(PTS-STARTPTS),fps=24[b2];"
 f"[b1][b2]concat=n=2:v=1:a=0[bb];"
 f"[3:v]format=rgba,fade=t=in:st={INTRO_NORMAL + 0.2}:d=0.8:alpha=1[ttl];"
 f"[bb][ttl]overlay=0:0:shortest=1,fade=t=out:st={B_LEN - 0.5}:d=0.5[b];"
 f"[0:v]trim={C_START:.4f}:{C_END:.4f},setpts=PTS-STARTPTS,fps=24[c];"
 f"[2:v]scale=1920:1080:flags=lanczos,unsharp=5:5:0.6,fps=24,tpad=stop_mode=clone:stop_duration={D_PAD}[dd];"
 f"[4:v]format=rgba,fade=t=in:st=5.5:d=1.0:alpha=1[otx];"
 f"[dd][otx]overlay=0:0:shortest=1,fade=t=out:st={D_LEN - 1.3}:d=1.3[d];"
 f"[a][b][c][d]concat=n=4:v=1:a=0,format=yuv420p[v]")
out = 'out/devara2_part1_final.mp4'
run(['ffmpeg', '-y', '-loglevel', 'error', '-i', FILM, '-i', INTRO, '-i', OUTRO,
     '-loop', '1', '-t', f'{B_LEN}', '-i', 'assets/title.png', '-loop', '1', '-t', f'{D_LEN}', '-i', 'assets/outro_text.png',
     '-i', 'audio/final_mix.wav', '-filter_complex', fc, '-map', '[v]', '-map', '5:a',
     '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-r', '24',
     '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out])
print('FINAL', out)

# =====================================================================================================================
#  ANIMATION RENDER NODE  —  ONE Kaggle cell
#  Kaggle settings:  Accelerator = GPU P100  (or GPU T4 x2)   ·   Internet = ON   ·   Persistence = off is fine
#  What it does:
#    1. Detects GPUs and picks a GPU policy (P100: one GPU for everything · T4x2: GPU0 = Blender, GPU1 = AI models)
#    2. Installs Blender 5.x + the NVIDIA EGL fix (GPU EEVEE) and runs a smoke test
#    3. Starts a token-protected API + public HTTPS tunnel  ->  prints ENDPOINT and TOKEN  (paste both to your agent)
#    4. Installs the AI model environments in the BACKGROUND (voices, foley, sfx, music, motion, whisper)
#       — check progress with  GET /models ; each model lives in its own isolated uv env
#  Keep this tab open. The cell keeps running (heartbeat every 10 min).
# =====================================================================================================================
import os, re, glob, json, time, shutil, secrets, signal, tarfile, threading, subprocess, urllib.request, uuid

# ----------------------------------------------------------------------------------------------- CONFIG (edit freely)
W        = '/kaggle/working'                 # everything lives here
PROJ     = f'{W}/proj'                       # your uploaded project
BIG      = '/root/vg'                        # big system disk (TBs): /kaggle/working is only 20 GB
ENVS     = f'{BIG}/envs'                     # one isolated python env per model (same disk as uv cache -> torch hardlinked, stored once)
MODELS   = f'{BIG}/models'                   # cloned repos + downloaded weights
BLENDER_SERIES = '5.3'                       # newest patch of this series is downloaded automatically
TRACK    = 'both'                            # '3d' · '2d' · 'both'  -> which model set to install
AUDIO_MODELS = ['whisper', 'chatterbox', 'maya1', 'step_editx', 'moss_sfx', 'ace_step', 'hy_foley', 'zonos3']
MODELS_3D    = ['hy_motion']                                        # text -> body motion
MODELS_2D    = ['rhubarb', 'vector2d']                          # lip-sync visemes + vector renderer/title libs (no image models)
INSTALL_MODELS = AUDIO_MODELS + (MODELS_3D if TRACK in ('3d', 'both') else []) + (MODELS_2D if TRACK in ('2d', 'both') else [])
HF_TOKEN = os.environ.get('HF_TOKEN', '')    # or upload .env later; gated models need it (click "Agree" on their pages)

# Each model: python version, pip packages, optional git repo (+ its requirements), HF weights to pre-download.
# Repo URLs / ids come from the model cards (Nov 2026). If one fails, only that model is marked FAILED — see GET /models.
MODEL_SPECS = {
    'whisper':    dict(py='3.11', pip=['faster-whisper'], hf=[]),
    'chatterbox': dict(py='3.11', pip=['chatterbox-tts', 'soundfile'], hf=['ResembleAI/chatterbox-turbo']),
    'maya1':      dict(py='3.11', pip=['transformers', 'accelerate', 'snac', 'soundfile'], hf=['maya-research/maya1']),
    'step_editx': dict(py='3.12', repo='https://github.com/stepfun-ai/Step-Audio-EditX', hf=['stepfun-ai/Step-Audio-EditX', 'stepfun-ai/Step-Audio-Tokenizer']),
    'moss_sfx':   dict(py='3.11', repo='https://github.com/OpenMOSS/MOSS-TTS', hf=[]),
    'ace_step':   dict(py='3.11', repo='https://github.com/ace-step/ACE-Step', hf=[]),
    'hy_foley':   dict(py='3.10', repo='https://github.com/Tencent-Hunyuan/HunyuanVideo-Foley', hf=['tencent/HunyuanVideo-Foley']),
    'hy_motion':  dict(py='3.10', repo='https://github.com/Tencent-Hunyuan/HY-Motion-1.0', hf=[]),
    'zonos3':     dict(py='3.11', pip=['soundfile'], hf=['Zyphra/ZONOS3-Mini']),
    # ---- 2D track ----
    'rhubarb':    dict(shell='wget -q https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Linux.zip '
                         '-O /tmp/rh.zip && unzip -oq /tmp/rh.zip -d {MODELS}/rhubarb'),            # CPU lip-sync visemes (MIT)
    'vector2d':   dict(py='3.11', pip=['skia-python', 'uharfbuzz', 'fonttools', 'numpy', 'scipy', 'pyyaml'], hf=[]),   # vector 2D render + text shaping
}

# ------------------------------------------------------------------------------------------------------------ helpers
LOG_LOCK = threading.Lock()
def log(msg):
    with LOG_LOCK: print(time.strftime('%H:%M:%S'), msg, flush=True)

def sh(cmd, env=None, quiet=True, timeout=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, timeout=timeout)
    out = (r.stdout + r.stderr).strip()
    if not quiet and out: print(out[-2000:])
    return r.returncode, out

for d in (PROJ, ENVS, MODELS): os.makedirs(d, exist_ok=True)
os.chdir(W)

# ----------------------------------------------------------------------------------------------- 1. GPUs + policy
_, gpu_csv = sh('nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader')
GPUS = [dict(zip(('index', 'name', 'mem', 'driver'), [x.strip() for x in l.split(',')])) for l in gpu_csv.splitlines() if l.strip()]
DRIVER = GPUS[0]['driver'] if GPUS else ''
IS_PASCAL = any('P100' in g['name'] for g in GPUS)
RENDER_GPU = '0'                                   # Blender EEVEE on Kaggle always uses GPU 0 (EGL picks it)
MODEL_GPU = '1' if len(GPUS) > 1 else '0'          # T4x2: AI models on GPU 1 · P100: shared (run models before rendering)
TORCH_INDEX = 'https://download.pytorch.org/whl/cu126'   # cu126 wheels still include Pascal (sm_60) kernels
log(f'[1/5] GPUs: {[g["name"] for g in GPUS]} driver {DRIVER} · render GPU {RENDER_GPU} · model GPU {MODEL_GPU}')

# -------------------------------------------------------------------------------- 2. Blender + system packages
log('[2/5] Blender + system packages ...')
if not os.path.exists(f'{W}/blender/blender'):
    idx = urllib.request.urlopen(f'https://download.blender.org/release/Blender{BLENDER_SERIES}/').read().decode()
    tars = sorted(set(re.findall(rf'blender-{re.escape(BLENDER_SERIES)}\.\d+-linux-x64\.tar\.xz', idx)),
                  key=lambda s: int(s.split('.')[2].split('-')[0]))
    sh(f'wget -q https://download.blender.org/release/Blender{BLENDER_SERIES}/{tars[-1]} -O b.tar.xz '
       f'&& tar xf b.tar.xz && mv {tars[-1][:-7]} blender && rm b.tar.xz')
sh('apt-get -qq update; apt-get -qq install -y libegl1 libgl1 libxi6 libxkbcommon0 libsm6 libxrender1 libxxf86vm1 '
   'libxfixes3 ffmpeg git-lfs fonts-noto-core libraqm0 unzip')
sh('pip -q install fastapi uvicorn python-multipart uv huggingface_hub')
if not os.path.exists(f'{W}/cloudflared'):
    sh(f'wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 '
       f'-O {W}/cloudflared && chmod +x {W}/cloudflared')

# -------------------------------------------------------------------- 3. NVIDIA EGL fix (GPU EEVEE) + smoke test
log('[3/5] NVIDIA EGL libraries for GPU EEVEE ...')
LIB = '/usr/lib/x86_64-linux-gnu'
EGL_JSON = '/usr/share/glvnd/egl_vendor.d/10_nvidia.json'
if not glob.glob(f'{LIB}/libEGL_nvidia.so.*'):
    run = f'{W}/NVIDIA-{DRIVER}.run'
    for url in (f'https://us.download.nvidia.com/tesla/{DRIVER}/NVIDIA-Linux-x86_64-{DRIVER}.run',
                f'https://download.nvidia.com/XFree86/Linux-x86_64/{DRIVER}/NVIDIA-Linux-x86_64-{DRIVER}.run'):
        if os.path.exists(run) and os.path.getsize(run) > 10_000_000: break
        sh(f'wget -q "{url}" -O "{run}" || rm -f "{run}"')
    sh(f'rm -rf {W}/nv && sh "{run}" -x --target {W}/nv')
    wanted = re.compile(r'(EGL_nvidia|eglcore|glcore|glsi|tls|GLX_nvidia|gpucomp|glvkspirv|rtcore|nvoptix|ptxjitcompiler|allocator|cfg)')
    for f in glob.glob(f'{W}/nv/*.so*'):
        dst = f'{LIB}/{os.path.basename(f)}'
        if wanted.search(f) and not os.path.exists(dst): shutil.copy2(f, dst)   # never overwrite host CUDA/NVML libs
    os.makedirs(os.path.dirname(EGL_JSON), exist_ok=True)
    open(EGL_JSON, 'w').write('{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}')
    sh(f'ln -sf {LIB}/libEGL_nvidia.so.{DRIVER} {LIB}/libEGL_nvidia.so.0; ldconfig')
os.environ['__EGL_VENDOR_LIBRARY_FILENAMES'] = EGL_JSON

open(f'{W}/smoke.py', 'w').write(
    "import bpy, time\n"
    "sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'\n"
    "sc.render.resolution_x, sc.render.resolution_y = 1920, 1080\n"
    "bpy.ops.mesh.primitive_uv_sphere_add(); bpy.ops.object.light_add(type='SUN'); sc.render.filepath = '/tmp/smoke.png'\n"
    "for i in range(2):\n"
    "    t = time.time(); bpy.ops.render.render(write_still=True); print('SMOKE_SECONDS', round(time.time() - t, 2))\n")
_, smoke = sh(f'{W}/blender/blender -b --factory-startup --python {W}/smoke.py 2>&1 | grep -E "SMOKE|EGL Error" | tail -2')
log(f'      EEVEE smoke test: {smoke.replace(chr(10), " | ")}   (2nd value should be < 2 s)')

# ------------------------------------------------------------- 4. AI model environments (background installer)
MODEL_STATE = {m: 'queued' for m in INSTALL_MODELS}

def install_model(name):
    spec = MODEL_SPECS[name]; env_dir = f'{ENVS}/{name}'; py = f'{env_dir}/bin/python'
    logf = open(f'{W}/install_{name}.log', 'w')
    def step(cmd):
        logf.write(f'$ {cmd}\n'); logf.flush()
        r = subprocess.run(cmd, shell=True, stdout=logf, stderr=subprocess.STDOUT, env=dict(os.environ, HF_TOKEN=HF_TOKEN))
        if r.returncode: raise RuntimeError(f'failed: {cmd[:120]}')
    try:
        MODEL_STATE[name] = 'installing'
        if spec.get('shell'):                                   # plain download (no python env needed)
            step(spec['shell'].format(MODELS=MODELS)); MODEL_STATE[name] = 'ready'; return
        step(f'uv venv {env_dir} --python {spec["py"]} -q')
        step(f'uv pip install --python {py} -q torch torchaudio --index-url {TORCH_INDEX}')
        if spec.get('repo'):
            repo_dir = f'{MODELS}/{name}'
            if not os.path.exists(repo_dir): step(f'git clone --depth 1 {spec["repo"]} {repo_dir}')
            for req in ('requirements.txt', 'requirements-inference.txt'):
                if os.path.exists(f'{repo_dir}/{req}'):
                    # keep our Pascal-compatible torch: drop torch pins from the repo requirements
                    step(f"grep -viE '^(torch|torchaudio|torchvision)([=<>~ ]|$)' {repo_dir}/{req} > {repo_dir}/_req.txt; "
                         f'uv pip install --python {py} -q -r {repo_dir}/_req.txt')
            if os.path.exists(f'{repo_dir}/setup.py') or os.path.exists(f'{repo_dir}/pyproject.toml'):
                has_req = any(os.path.exists(f'{repo_dir}/{r}') for r in ('requirements.txt', 'requirements-inference.txt'))
                # pyproject-only repos carry their deps there -> install them (CUDA torch index kept available)
                step(f'uv pip install --python {py} -q {"--no-deps " if has_req else f"--extra-index-url {TORCH_INDEX} "}-e {repo_dir}')
        if spec.get('pip'): step(f'uv pip install --python {py} -q ' + ' '.join(spec['pip']))
        step(f'uv pip install --python {py} -q huggingface_hub soundfile numpy')
        for repo_id in spec.get('hf', []):   # python API: the old huggingface-cli is gone; token stays out of the log
            dest = f'{MODELS}/hf/{repo_id.replace("/", "__")}'
            step(f'{py} -c "import os; from huggingface_hub import snapshot_download as s; '
                 f's(\'{repo_id}\', local_dir=\'{dest}\', token=os.environ.get(\'HF_TOKEN\') or None)"')
        step(f'CUDA_VISIBLE_DEVICES={MODEL_GPU} {py} -c "import torch; torch.zeros(1).cuda(); print(\'cuda ok\', torch.__version__)"')
        MODEL_STATE[name] = 'ready'
    except Exception as e:
        MODEL_STATE[name] = f'FAILED ({e}) — see install_{name}.log'
    finally:
        logf.close(); log(f'      model {name}: {MODEL_STATE[name]}')

def installer():
    for m in INSTALL_MODELS: install_model(m)     # sequential: keeps disk/network sane

# --------------------------------------------------------------------------------------------- 5. API + tunnel
log('[4/5] API server ...')
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse
import uvicorn

TOKEN = secrets.token_urlsafe(18)
JOBS = {}
app = FastAPI()

def auth(token):
    if token != TOKEN: raise HTTPException(401, 'bad token')

def job_env(gpu):
    return dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu), BLENDER=f'{W}/blender/blender', PROJ=PROJ, ENVS=ENVS,
                MODELS=MODELS, HF_TOKEN=HF_TOKEN, RENDER_GPU=RENDER_GPU, MODEL_GPU=MODEL_GPU,
                USE_JAX='0', USE_FLAX='0', USE_TF='0', USE_TORCH='1')

@app.get('/info')
def info(x_token: str = Header(None)):
    auth(x_token)
    _, util = sh('nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader')
    return {'gpus': util.splitlines(), 'render_gpu': RENDER_GPU, 'model_gpu': MODEL_GPU, 'pascal': IS_PASCAL,
            'disk_free_gb': round(shutil.disk_usage(W).free / 1e9, 1), 'models': MODEL_STATE,
            'jobs': {k: {'cmd': v['cmd'][:120], 'gpu': v['gpu'], 'secs': round(time.time() - v['start']), 'rc': v['proc'].poll()}
                     for k, v in JOBS.items()}}

@app.get('/models')
def models(x_token: str = Header(None)):
    auth(x_token); return MODEL_STATE

@app.post('/models/install/{name}')
def models_install(name: str, x_token: str = Header(None)):
    auth(x_token)
    if name not in MODEL_SPECS: raise HTTPException(404, 'unknown model')
    MODEL_STATE[name] = 'queued'; threading.Thread(target=install_model, args=(name,), daemon=True).start()
    return {'ok': True}

@app.post('/upload')
async def upload(f: UploadFile = File(...), dest: str = '', x_token: str = Header(None)):
    auth(x_token)
    target = os.path.join(PROJ, dest); os.makedirs(target, exist_ok=True)
    tmp = f'{W}/up_{uuid.uuid4().hex}'
    with open(tmp, 'wb') as o: shutil.copyfileobj(f.file, o)
    if f.filename.endswith(('.tar.gz', '.tgz', '.tar')):
        with tarfile.open(tmp) as t: t.extractall(target)
        os.remove(tmp)
    else:
        shutil.move(tmp, os.path.join(target, f.filename))
    if os.path.exists(f'{PROJ}/.env'):            # pick up HF token etc. from the uploaded .env
        for line in open(f'{PROJ}/.env'):
            if line.startswith('HF_TOKEN='): globals()['HF_TOKEN'] = line.split('=', 1)[1].strip()
    return {'ok': True, 'dest': target}

@app.post('/run')
async def run(req: Request, x_token: str = Header(None)):
    auth(x_token)
    j = await req.json(); jid = j.get('name') or uuid.uuid4().hex[:8]
    gpu = j.get('gpu', RENDER_GPU)
    logfile = open(f'{W}/log_{jid}.txt', 'w')
    proc = subprocess.Popen(j['cmd'], shell=True, cwd=PROJ, env=job_env(gpu), stdout=logfile, stderr=subprocess.STDOUT,
                            start_new_session=True)       # own process group -> /kill never touches other jobs
    JOBS[jid] = {'cmd': j['cmd'], 'gpu': gpu, 'start': time.time(), 'log': logfile.name, 'proc': proc}
    return {'job': jid}

@app.get('/log/{jid}', response_class=PlainTextResponse)
def getlog(jid: str, tail: int = 60, x_token: str = Header(None)):
    auth(x_token)
    if jid.startswith('install_'): path = f'{W}/{jid}.log'
    else: path = JOBS[jid]['log']
    lines = open(path, errors='replace').read().splitlines()
    head = f"[rc={JOBS[jid]['proc'].poll()} secs={round(time.time() - JOBS[jid]['start'])}]\n" if jid in JOBS else ''
    return head + '\n'.join(lines[-tail:])

@app.post('/kill/{jid}')
def kill(jid: str, x_token: str = Header(None)):
    auth(x_token)
    p = JOBS[jid]['proc']
    if p.poll() is None: os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    return {'ok': True}

@app.get('/ls')
def ls(path: str = '', x_token: str = Header(None)):
    auth(x_token); d = os.path.join(PROJ, path)
    return sorted(os.listdir(d)) if os.path.isdir(d) else []

@app.get('/download')
def download(path: str, x_token: str = Header(None)):
    auth(x_token); f = os.path.join(PROJ, path)
    if os.path.isdir(f):
        tar_path = f.rstrip('/') + '.tar'
        sh(f'tar cf "{tar_path}" -C "{os.path.dirname(f)}" "{os.path.basename(f)}"'); f = tar_path
    return FileResponse(f, filename=os.path.basename(f))

threading.Thread(target=lambda: uvicorn.run(app, host='0.0.0.0', port=8000, log_level='warning'), daemon=True).start()

log('[5/5] public HTTPS tunnel ...')
URL = None
for attempt in range(3):
    cf = subprocess.Popen(f'{W}/cloudflared tunnel --no-autoupdate --url http://localhost:8000', shell=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    started = time.time()
    for line in cf.stdout:
        m = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
        if m: URL = m.group(0); break
        if time.time() - started > 90: break
    if URL: break
    cf.kill()
threading.Thread(target=lambda: [None for _ in cf.stdout], daemon=True).start()    # keep draining tunnel output

threading.Thread(target=installer, daemon=True).start()                            # AI models install in background

print('\n' + '=' * 78)
print(f'ENDPOINT : {URL}')
print(f'TOKEN    : {TOKEN}')
print('=' * 78)
print(f'GPU policy : render on GPU {RENDER_GPU} · AI models on GPU {MODEL_GPU}' + ('  (P100: run models BEFORE rendering)' if MODEL_GPU == RENDER_GPU else ''))
print('Models     : installing in background → check GET /models  (paste ENDPOINT + TOKEN to your agent now)')
print('Keep this tab open — this cell keeps running.\n', flush=True)

while True:                                                                         # heartbeat keeps the session alive
    time.sleep(600)
    running = sum(v['proc'].poll() is None for v in JOBS.values())
    ready = sum(s == 'ready' for s in MODEL_STATE.values())
    log(f'alive · jobs running {running} · models ready {ready}/{len(MODEL_STATE)}')

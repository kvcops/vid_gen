"""Client for the Kaggle render node. Usage:
  node.py info | ls PATH | log JOB [tail] | kill JOB
  node.py push [project_dir] [extra...]   # e.g. node.py push devara audio/dialogue.wav
  node.py run NAME GPU "shell cmd"   # cwd = project root on Kaggle; $BLENDER available
  node.py get REMOTE LOCAL
"""
import os, sys, json, tarfile, io, urllib.request, uuid
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = dict(l.strip().split('=', 1) for l in open(os.path.join(ROOT, '.env')) if '=' in l)
URL, TOK = ENV['KAGGLE_URL'], ENV['KAGGLE_TOKEN']
def req(method, path, data=None, ctype=None, raw=False, timeout=600):
    h = {'X-Token': TOK, 'User-Agent': 'devara-client'}
    if ctype: h['Content-Type'] = ctype
    r = urllib.request.urlopen(urllib.request.Request(URL + path, data=data, headers=h, method=method), timeout=timeout)
    b = r.read(); return b if raw else b.decode(errors='replace')
def upload(path, dest=''):
    bnd = uuid.uuid4().hex; name = os.path.basename(path)
    body = (f'--{bnd}\r\nContent-Disposition: form-data; name="f"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode() \
        + open(path, 'rb').read() + f'\r\n--{bnd}--\r\n'.encode()
    return req('POST', f'/upload?dest={dest}', body, f'multipart/form-data; boundary={bnd}', timeout=1800)
def push(project='.', extra=()):
    """upload <project>/{blender, audio/timeline.json, assets, story, *extra}; remote paths stay relative to the project."""
    base = os.path.abspath(project)
    tmp = os.path.join(ROOT, 'push.tar.gz')
    with tarfile.open(tmp, 'w:gz') as t:
        for p in ['blender', 'audio/timeline.json', 'assets', 'story', *extra]:
            full = os.path.join(base, p)
            if os.path.exists(full): t.add(full, arcname=p, filter=lambda ti: None if '__pycache__' in ti.name else ti)
    print(f'upload {os.path.getsize(tmp)/1e6:.1f} MB'); return upload(tmp)
def run(name, gpu, cmd): return req('POST', '/run', json.dumps({'name': name, 'gpu': int(gpu), 'cmd': cmd}).encode(), 'application/json')
def get(remote, local):
    data = req('GET', f'/download?path={urllib.request.quote(remote)}', raw=True, timeout=3600)
    os.makedirs(os.path.dirname(os.path.abspath(local)), exist_ok=True); open(local, 'wb').write(data); return f'{len(data)/1e6:.1f} MB -> {local}'
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); a = sys.argv[1:]; c = a[0]
    if c == 'info': print(req('GET', '/info'))
    elif c == 'ls': print(req('GET', f'/ls?path={a[1] if len(a) > 1 else ""}'))
    elif c == 'log': print(req('GET', f'/log/{a[1]}?tail={a[2] if len(a) > 2 else 40}'))
    elif c == 'kill': print(req('POST', f'/kill/{a[1]}'))
    elif c == 'push': print(push(a[1] if len(a) > 1 else '.', a[2:]))
    elif c == 'run': print(run(a[1], a[2], a[3]))
    elif c == 'get': print(get(a[1], a[2]))
    elif c == 'models': print(req('GET', '/models'))
    elif c in ('install', 'remove'): print(req('POST', f'/models/{c}/{a[1]}'))

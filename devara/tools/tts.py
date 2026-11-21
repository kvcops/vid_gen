"""HeyGen TTS helper (model heygen-voice-1-turbo-free). Usage: tts.py voice_id out.wav "text" [boost]"""
import json, os, sys, time, wave, urllib.request, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = [l.split('=',1)[1].strip() for l in open(next(p for p in (os.path.join(ROOT, '.env'), os.path.join(os.path.dirname(ROOT), '.env')) if os.path.exists(p))) if l.startswith('HEYGEN_API_KEY')][0]

def write_wav(raw, out, rate=48000):
    if raw[:4] == b'RIFF':
        open(out, 'wb').write(raw); return
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(raw)

def tts(voice_id, text, out, boost=None, lang=None, model='heygen-voice-1-turbo-free', tries=6):
    body = {'model': model, 'voice_id': voice_id, 'text': text,
            'output_format': {'encoding': 'pcm', 'sample_rate_hertz': 48000}}
    if boost is not None: body['expressiveness_boost'] = boost
    if lang: body['language'] = lang
    for i in range(tries):
        req = urllib.request.Request('https://api.heygen.com/v3/models/audio/tts',
              data=json.dumps(body).encode(), headers={'X-Api-Key': KEY, 'Content-Type': 'application/json'})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            d = r.get('data', r)
            raw = urllib.request.urlopen(d['audio_url'], timeout=120).read()
            write_wav(raw, out)
            return d.get('duration')
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')
            if e.code in (429, 500, 503): time.sleep(5 * (i + 1)); continue
            raise RuntimeError(f'{e.code} {msg}')
    raise RuntimeError('retries exhausted')

if __name__ == '__main__':
    a = sys.argv
    print(tts(a[1], a[3], a[2], float(a[4]) if len(a) > 4 else None))

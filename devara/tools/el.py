"""ElevenLabs v4 Telugu dialogue: design 3 South-Indian voices, then generate every line (resumable).
python tools/el.py design | gen | credits"""
import os, sys, json, base64, time, urllib.request, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = dict(l.strip().split('=', 1) for l in open(next(p for p in (os.path.join(ROOT, '.env'), os.path.join(os.path.dirname(ROOT), '.env')) if os.path.exists(p))) if '=' in l)
KEY = ENV['ELEVEN_KEY']; API = 'https://api.elevenlabs.io'
sys.stdout.reconfigure(encoding='utf-8')
VFILE = os.path.join(ROOT, 'audio', 'el_voices.json')

def call(path, body=None, raw=False, method=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, method=method or ('POST' if body is not None else 'GET'),
                                 headers={'xi-api-key': KEY, 'Content-Type': 'application/json'})
    try:
        r = urllib.request.urlopen(req, timeout=180).read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'{e.code} {e.read().decode(errors="replace")[:400]}')
    return r if raw else json.loads(r)

DESIGN = {
 'DEVARA': ("A deep, powerful, rugged South Indian man in his forties from coastal Andhra Pradesh, native Telugu speaker, commanding heroic voice with a slow, intense, larger-than-life delivery like a Telugu mass action movie hero.",
            "నా కొడుకు మీద చెయ్యి వేస్తే, ఈ సముద్రం మళ్ళీ ఎర్రబడుతుంది. దేవర ఎప్పుడూ ఓడిపోడు. ఈ ఎర్ర సముద్రానికి భయం అంటే ఏంటో నేర్పించింది నేనే. గుర్తుపెట్టుకో."),
 'SINGAPPA': ("A warm, slightly raspy elderly South Indian grandfather in his seventies, native Telugu speaker, a wise and witty village storyteller with a slow, playful, knowing delivery and a gentle chuckle.",
            "అనగనగా ఒక ఎర్ర సముద్రం. ఆ సముద్రానికి ఒక దేవుడు ఉండేవాడు. వాడి పేరు దేవర. ఈ కథ వినండి సారూ, మీకు నిద్ర పట్టదు. సముద్రం అబద్ధం చెప్పదు, కానీ నేను చెప్తా."),
 'THANGAM': ("A bright, confident young South Indian village woman in her early twenties, native Telugu speaker, sassy, witty and expressive with a quick, playful delivery.",
            "వరా! ఊరంతా నిన్ను పిరికోడు అంటున్నారు. నాకు సిగ్గుగా ఉంది. ఏ మాస్ ఇమేజ్? నీకున్నది మాస్క్ ఇమేజ్! నన్ను పట్టుకోవాలంటే ఇంకో జన్మ కావాలి రా!"),
}
PREMADE = {  # ElevenLabs default voices chosen by character (v4 speaks Telugu natively with language_code=te)
 'VARA': 'IKne3meq5aSn9XLyUdCD',      # Charlie - young, can sound gentle
 'BHAIRA': 'SOYHLrjzK2X1ezoPC6cr',    # Harry - fierce warrior, rough
 'KUNJARA': 'N2lVS1w4EtoT3dr4eOWO',   # Callum - husky trickster (comic)
 'DSP': 'onwK4e9ZLuTAKqWW03F9',       # Daniel - steady, formal
 'YETHI': 'nPczCjzI2devNBz1zQrb',     # Brian - deep, resonant
}
# v4 audio tags per speaker/line style (kept short to save credits)
TAG = {'NARR': '[storytelling, slow] ', 'DEVARA': '[deep, commanding] ', 'BHAIRA': '[angry, shouting] ', 'KUNJARA': '[excited, fast] ',
       'THANGAM': '[sassy] ', 'VARA': '[nervous] ', 'VARA_FAKE': '[trying to sound deep and menacing] ', 'YETHI': '[menacing, slow] ', 'SINGAPPA': '', 'DSP': ''}
EN = {'Part 2': 'పార్ట్ టూ', 'Part 1': 'పార్ట్ వన్', 'Story over': 'స్టోరీ ఓవర్', 'Google Maps': 'గూగుల్ మ్యాప్స్', 'EMI': 'ఈ ఎం ఐ'}

def design():
    vs = json.load(open(VFILE)) if os.path.exists(VFILE) else {}
    os.makedirs(os.path.join(ROOT, 'audio', 'el_test'), exist_ok=True)
    for name, (desc, text) in DESIGN.items():
        if name in vs: continue
        d = call('/v1/text-to-voice/design', {'voice_description': desc, 'model_id': 'eleven_ttv_v3', 'text': text, 'guidance_scale': 5})
        p = d['previews'][0]
        open(os.path.join(ROOT, 'audio', 'el_test', f'design_{name}.mp3'), 'wb').write(base64.b64decode(p['audio_base_64']))
        v = call('/v1/text-to-voice', {'voice_name': f'Devara2 {name}', 'voice_description': desc, 'generated_voice_id': p['generated_voice_id']})
        vs[name] = v['voice_id']; json.dump(vs, open(VFILE, 'w'), indent=1); print('designed', name, v['voice_id'], flush=True)
    return vs

CASTMAP = {'NARR': 'pqHfZKP75CvOlQylNhV4', 'SINGAPPA': 'pqHfZKP75CvOlQylNhV4',   # Bill - wise, mature, old
           'DEVARA': 'pNInz6obpgDQGcFmaJgB',                                        # Adam - dominant, firm
           'THANGAM': 'FGY2WhTYpPnrIDTdsKH5',                                       # Laura - sassy, quirky
           'VARA_FAKE': PREMADE['VARA']}
def voice_for(spk, vs):
    return CASTMAP.get(spk) or PREMADE[spk]

def gen():
    vs = {}
    TL = json.load(open(os.path.join(ROOT, 'audio', 'timeline.json'), encoding='utf-8'))
    out = os.path.join(ROOT, 'audio', 'raw_el'); os.makedirs(out, exist_ok=True)
    items = [(e['file'], e['speaker'], e['text']) for s in TL['shots'] for e in s['events'] if e['type'] == 'say']
    for i, (key, spk, text) in enumerate(items):
        f = os.path.join(out, key + '.mp3')
        if os.path.exists(f): continue
        t = text
        for k, v in EN.items(): t = t.replace(k, v)
        body = {'text': TAG.get(spk, '') + t, 'model_id': 'eleven_v4', 'language_code': 'te',
                'voice_settings': {'stability': 0.45, 'similarity_boost': 0.8, 'style': 0.4, 'use_speaker_boost': True}}
        audio = call(f'/v1/text-to-speech/{voice_for(spk, vs)}?output_format=mp3_44100_128', body, raw=True)
        open(f, 'wb').write(audio); print(f'{i + 1}/{len(items)} {key} {spk}', flush=True)
    print('EL_DONE', flush=True)

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'design': print(design())
    elif c == 'gen': gen()
    print('credits used:', call('/v1/user/subscription')['character_count'])

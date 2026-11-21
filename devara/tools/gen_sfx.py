"""Generate the sound-effects library with ElevenLabs sound generation -> audio/sfx/<name>.mp3 (resumable)."""
import os, sys, json, time, urllib.request, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = dict(l.strip().split('=', 1) for l in open(next(p for p in (os.path.join(ROOT, '.env'), os.path.join(os.path.dirname(ROOT), '.env')) if os.path.exists(p))) if '=' in l); K = ENV['ELEVEN_KEY']
OUT = os.path.join(ROOT, 'audio', 'sfx'); os.makedirs(OUT, exist_ok=True)
SFX = {  # name: (prompt, seconds, loop)
 # ambience beds (looped under whole scenes)
 'amb_storm':      ('raging stormy ocean at night, huge waves crashing on rocks, heavy rain and howling wind, continuous ambience', 22, True),
 'amb_sea_night':  ('calm ocean at night, gentle waves lapping against a wooden fishing boat, soft wind, continuous ambience', 22, True),
 'amb_rocks':      ('waves washing gently over coastal rocks at night, soft wind, distant sea, continuous ambience', 22, True),
 'amb_island':     ('tropical island beach in the daytime, gentle waves on sand, distant seagulls, light breeze through palm leaves, continuous ambience', 22, True),
 'amb_village':    ('sunny Indian fishing village beach, waves on the shore, seagulls, faint distant villagers chatter, wind, continuous ambience', 22, True),
 'amb_hut':        ('quiet village hut interior at night, crickets outside, distant sea waves, faint oil lantern hiss, continuous ambience', 22, True),
 'amb_torch':      ('burning wooden torches crackling and flickering in the wind, continuous fire crackle ambience', 15, True),
 'amb_boat_creak': ('old wooden fishing boat creaking gently as it rocks on the water, rope creaks, continuous', 15, True),
 # one-shots
 'thunder1':       ('a close violent thunder crack followed by a deep rolling rumble', 5, False),
 'thunder2':       ('distant thunder rumble rolling across a stormy sky', 5, False),
 'stab_thunk':     ('a knife stabbing hard into a dried fish, a dull wet thunk', 1.2, False),
 'cloth_rustle':   ('quick cloth rustle of a shirt being grabbed', 1.0, False),
 'tea_sip':        ('an old man slurping hot tea from a small glass, then a satisfied ahh breath', 2.0, False),
 'glass_table':    ('a small tea glass placed down on a wooden table', 0.8, False),
 'whoosh_small':   ('a quick light whoosh of an object thrown through the air', 0.8, False),
 'whoosh_big':     ('a heavy fast whoosh of a body flying through the air', 1.2, False),
 'whoosh_blade':   ('a large machete blade spinning in a fast circle, sharp metallic whoosh swoosh', 1.6, False),
 'coconut_fall':   ('a coconut falling from a tall palm tree, leaves rustle then a falling whoosh', 1.0, False),
 'bonk':           ('a single loud cartoon coconut bonk on a head, hollow wooden knock', 1.0, False),
 'dizzy':          ('cartoon dizzy twinkling stars circling sound, little chimes', 1.5, False),
 'sand_thud':      ('something heavy dropping onto soft beach sand, a dull thud', 0.8, False),
 'body_sand':      ('a man thrown and landing hard on his back on beach sand, heavy body thud with a grunt-free impact', 1.0, False),
 'net_land':       ('a man crashing into a pile of fishing nets and rope, soft rustling crash', 1.2, False),
 'run_sand':       ('fast footsteps of a man running on soft beach sand', 1.5, False),
 'walk_sand':      ('relaxed footsteps of a man walking on beach sand', 2.8, False),
 'log_lift':       ('a heavy wooden log being lifted off the ground, wood creak and scrape', 1.5, False),
 'paper':          ('a paper poster being unrolled and shaken', 1.0, False),
 'basket':         ('rummaging inside a woven wicker basket of dried fish', 1.2, False),
 'splash_small':   ('a small object splashing into the sea', 1.0, False),
 'splash_med':     ('a man falling into the sea with a big splash', 1.5, False),
 'splash_big':     ('a giant shark leaping out of the ocean with a huge water explosion and spray', 2.5, False),
 'shark_leap':     ('a shark breaching out of the water and splashing back in', 2.0, False),
 'wave_rise':      ('a huge ocean wave rising and surging upward with a deep roar', 4.0, False),
 'rumble_under':   ('deep ominous underwater rumble, the sea trembling', 3.0, False),
 'deck_land':      ('a heavy man landing hard on a wooden boat deck, deep wooden thump and creak', 1.0, False),
 'boat_jump':      ('a man jumping from one wooden boat to another, wooden thud landing', 1.0, False),
 'axe_chop':       ('a heavy axe swinging and chopping hard into a wooden boat deck', 1.0, False),
 'metal_break':    ('a steel blade striking an axe, loud metal clang and the axe head snapping off', 1.5, False),
 'punch':          ('a single strong cinematic punch hit', 0.6, False),
 'foghorn':        ('a deep old ship foghorn blasting through thick fog at night', 3.0, False),
 'ship_creak':     ('a huge old wooden sailing ship creaking and its sails flapping in the wind', 5.0, False),
 'hood':           ('a heavy cloth hood being pulled back, fabric rustle', 1.0, False),
}
def gen(name, prompt, dur, loop):
    f = os.path.join(OUT, name + '.mp3')
    if os.path.exists(f): return
    body = {'text': prompt, 'duration_seconds': dur, 'prompt_influence': 0.55}
    if loop: body['loop'] = True
    for k in range(4):
        try:
            d = urllib.request.urlopen(urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(),
                                       headers={'xi-api-key': K, 'Content-Type': 'application/json'}), timeout=180).read()
            open(f, 'wb').write(d); print('ok', name, flush=True); return
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:200]
            if 'loop' in msg and 'loop' in body: body.pop('loop'); continue
            if e.code == 429: time.sleep(10); continue
            print('ERR', name, e.code, msg, flush=True); return
for n, (p, d, l) in SFX.items(): gen(n, p, d, l)
print('SFX_DONE')

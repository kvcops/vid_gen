"""DEVARA 2 - Part 1 : "ఎండు చేప రహస్యం" (The Dried-Fish Secret)
A fictional, fan-made comedy animation. Entertainment only.

Single source of truth: audio generation, timeline, lip-sync and every shot read this file.
Beat types inside a shot:
  ('say', speaker, telugu_text, {opts})   opts: pre (gap before, s), post (gap after, s), tag (label), boost
  ('wait', seconds, label)                 silent action time; label lets shot code find the time
"""


# FINAL VOICES (2026-11-21): ElevenLabs eleven_v4, language_code=te, stock voices (tools/el.py CASTMAP/PREMADE):
#   NARR/SINGAPPA=Bill, DEVARA=Adam, VARA/VARA_FAKE=Charlie, BHAIRA=Harry, THANGAM=Laura, KUNJARA=Callum, DSP=Daniel, YETHI=Brian
#   lines fitted to the animated timeline by tools/fit_dialogue.py raw_el -> audio/dialogue.wav
# (original HeyGen cast, superseded)
# speaker -> HeyGen voice id (picked by tools/cast_test.py: intelligibility + pitch)
CAST = {
    'NARR':     ('evZvNNzUH9RxaEHHzerf', 'Wise Hindi Grandfather'),   # Singappa as storyteller
    'SINGAPPA': ('evZvNNzUH9RxaEHHzerf', 'Wise Hindi Grandfather'),
    'DEVARA':   ('2lZkTvkzMXw1TFX4PKlb', 'Deep Authoritative'),
    'VARA':     ('719fdbe3c82e4716aa921f52a37cd075', 'Vikram - Calm & Gentle'),
    'VARA_FAKE':('719fdbe3c82e4716aa921f52a37cd075', 'Vikram - Calm & Gentle (pitched down: Vara faking Devara)'),
    'BHAIRA':   ('19ef3da29d1b474ba9225e58b64b5023', 'Warrior Rohan - Broadcaster'),
    'THANGAM':  ('7aafc1296f5c4d418703c5716d83a4a0', 'Peppy Priya - Excited'),
    'KUNJARA':  ('47b7b3cbf1794a7e9152023c523b91cc', 'Ravi - Upbeat & Lively'),
    'DSP':      ('4e79dcb0af2c4d07a5bf5db075884257', 'Araj - Clear & Professional'),
    'YETHI':    ('50d98873b52e4464ac35987d9b4774da', 'Theron - Rich & Evocative'),
}
# post-processing per speaker (ffmpeg filter); VARA_FAKE = Vara forcing a deep "Devara" voice
FX = {'VARA_FAKE': 'rubberband=pitch=0.78:formant=preserved,lowshelf=g=4:f=180', 'YETHI': 'aecho=0.8:0.6:40:0.12'}

S = lambda spk, txt, **o: ('say', spk, txt, o)
W = lambda sec, label=None: ('wait', sec, label)

SHOTS = [
 # ---------------- PROLOGUE : stormy red sea ----------------
 dict(id='s01', set='storm', desc='Black, lightning reveals a raging red-tinted sea, camera skims waves',
      beats=[W(1.6, 'flash1'), S('NARR', 'ఎర్ర సముద్రం...', post=0.6),
             S('NARR', 'ఈ నీళ్ళలో... ఉప్పు కంటే ఎక్కువ రక్తం కలిసింది.', post=0.8)]),
 dict(id='s02', set='storm', desc='Crane up the cliff; Devara silhouette, hair and lungi in wind, blade in hand',
      beats=[W(0.6), S('NARR', 'ఈ సముద్రాన్ని శాసించిన... ఒకే ఒక్క మగాడు...', post=0.4),
             S('NARR', 'దేవర!', post=1.4, tag='name')]),
 dict(id='s03', set='storm', desc='Extreme close-up: Devara eyes open in lightning flash, slow push-in',
      beats=[W(0.5, 'eyes'), S('NARR', 'కానీ పన్నెండేళ్ల క్రితం... సొంత కొడుకు చేతిలోనే... దేవర కథ ముగిసింది.', post=0.6)]),
 dict(id='s04', set='storm', desc='Silhouettes vs lightning: Vara thrusts a knife, Devara staggers back',
      beats=[W(0.4), S('NARR', 'అందరూ అదే అనుకున్నారు...', post=1.0, tag='stab'), S('NARR', 'కానీ...', post=1.2)]),
 dict(id='s05', set='title', desc='Title slam: దేవర 2 with red splash and embers',
      beats=[W(5.0, 'title')]),

 # ---------------- 1996 : Singappa's hut ----------------
 dict(id='s06', set='hut', desc='Wide: lantern-lit hut, DSP across Singappa, tea glasses; DSP is impatient',
      beats=[W(0.8), S('DSP', 'సింగప్ప గారూ... Part 1 కథ మొత్తం విన్నాం. దేవర చచ్చిపోయాడు, వర చంపేశాడు.', post=0.3),
             S('DSP', 'Story over! ఇంకా Part 2 ఎందుకండీ?', post=0.6)]),
 dict(id='s07', set='hut', desc='Close on Singappa: slow tea sip, chuckle, wise line',
      beats=[W(1.2, 'sip'), S('SINGAPPA', 'హహ్హహ్హ...', post=0.3),
             S('SINGAPPA', 'సముద్రం లోతు తెలియనోడికి... అల మీద నురుగే కథ అనిపిస్తది సారూ.', post=0.5)]),
 dict(id='s08', set='hut', desc='Two-shot, lantern flicker; Singappa leans in, DSP shocked',
      beats=[S('DSP', 'అంటే?', post=0.4), S('SINGAPPA', 'ఆ రోజు రాత్రి... వర కత్తి దించింది... దేవర గుండెలోకి కాదు.', post=0.4),
             S('DSP', 'మరి?!', post=0.5, tag='shock'), S('SINGAPPA', 'దేవర జేబులో ఉన్న... ఎండు చేపలోకి.', post=0.9)]),
 dict(id='s09', set='hut', desc='Deadpan DSP close, then Singappa proud nod',
      beats=[W(0.6), S('DSP', '...ఎండు చేపా?', post=0.6, tag='dead'),
             S('SINGAPPA', 'ఎండు చేప. రెండు కిలోలు. ఆ రోజు మార్కెట్ నుంచి తెస్తున్నాడు.', post=1.0)]),

 # ---------------- FLASHBACK : the staged death ----------------
 dict(id='s10', set='rocks', desc='Night rocks. Vara stabs, knife sticks in a dried fish in Devara\'s shirt',
      beats=[W(1.4, 'stab'), W(0.8, 'pull'), S('DEVARA', 'ఒరేయ్ వరా... నిజంగానే పొడిచేశావా రా?!', post=0.3),
             S('VARA', 'నువ్వే కదా నాన్నా... నిజంలా ఉండాలి అన్నావ్!', post=0.6)]),
 dict(id='s11', set='rocks', desc='Devara hand on Vara shoulder, wise slow push-in, moonlight',
      beats=[S('DEVARA', 'చూడు వరా. దేవర మనుషులకి కనపడకూడదు... భయంలా వినపడాలి.', post=0.4),
             S('DEVARA', 'ఈ రోజు నుంచి దేవర చచ్చిపోయాడు. సముద్రం మీద ఆ భయాన్ని... ఇక నువ్వే మోయాలి.', post=0.6)]),
 dict(id='s12', set='rocks', desc='Devara gazes at sea (epic hero angle), punchline, Vara shocked',
      beats=[S('VARA', 'మరి నువ్వు ఎక్కడికి వెళ్తావ్ నాన్నా?', post=0.5),
             S('DEVARA', 'నేనా...', post=1.1, tag='epic'), S('DEVARA', 'రిటైర్మెంట్.', post=0.5, tag='retire'),
             S('VARA', 'ఏంటీ?!', post=0.6, tag='shock'),
             S('NARR', 'అలా... ప్రపంచాన్ని వణికించిన దేవర... ఒక చిన్న దీవికి వెళ్ళిపోయాడు.', post=0.6)]),

 # ---------------- ISLAND : retirement ----------------
 dict(id='s13', set='island', desc='Sunny island; Devara in hammock with sunglasses; shark Sundaram pops up',
      beats=[W(1.2, 'wide'), S('NARR', 'పన్నెండేళ్లు. ఫోన్ లేదు, గొడవ లేదు, బీపీ లేదు.', post=0.4),
             S('DEVARA', 'సుందరం! రా రా... ఈ రోజు నీకు ఇష్టమైన వంజరం చేప.', post=0.4, tag='call'),
             W(1.6, 'shark')]),
 dict(id='s14', set='island', desc='Coconut drops on Devara\'s head; comic bonk',
      beats=[S('NARR', 'దేవర జీవితంలో... ఒకే ఒక్క టెన్షన్...', post=0.3), W(1.0, 'drop'),
             S('NARR', 'కొబ్బరికాయలు.', post=0.5),
             S('DEVARA', 'అబ్బా! ఈ దీవిలో నాకు ఒకే ఒక్క శత్రువు... నువ్వే రా కొబ్బరీ!', post=0.8)]),

 # ---------------- VILLAGE : Bhaira ----------------
 dict(id='s15', set='village', desc='Arena; Bhaira lifts a log overhead and roars at the sea',
      beats=[S('NARR', 'కానీ అవతల ఎర్ర సముద్రం గ్రామంలో... ఒకడు మాత్రం పన్నెండేళ్లుగా నిద్రపోలేదు.', post=0.4),
             W(1.0, 'lift'), S('BHAIRA', 'దేవరా! ఎక్కడ దాక్కున్నావ్ రా! బయటకు రా!', post=0.6, tag='roar')]),
 dict(id='s16', set='village', desc='Kunjara runs in panting with a poster; Bhaira grabs and tosses him into nets',
      beats=[W(1.4, 'run'), S('KUNJARA', 'అన్నా అన్నా! దేవర కనిపించాడు!', post=0.3),
             S('BHAIRA', 'ఎక్కడ రా?!', post=0.3, tag='grab'),
             S('KUNJARA', 'ఈ పోస్టర్ లో అన్నా... Part 2 పోస్టర్ వచ్చింది.', post=0.5, tag='poster'),
             W(1.6, 'toss')]),
 dict(id='s17', set='village', desc='Bhaira scheming close-up, Kunjara peeks out of the net',
      beats=[S('BHAIRA', 'వాడిని బయటకు రప్పించాలంటే... వాడికి ఇష్టమైనదాన్ని పట్టుకోవాలి.', post=0.4),
             S('KUNJARA', 'అంటే... ఎండు చేపా అన్నా?', post=0.5),
             S('BHAIRA', 'కాదు రా! వాడి కొడుకు... వర!', post=0.8, tag='glare')]),

 # ---------------- VILLAGE : Vara & Thangam ----------------
 dict(id='s18', set='village', desc='Vara walks with fish basket; Thangam arms crossed, scolds',
      beats=[W(1.0, 'walk'), S('THANGAM', 'వరా! ఊరంతా నిన్ను పిరికోడు అంటున్నారు. నాకు సిగ్గుగా ఉంది!', post=0.3),
             S('VARA', 'అయ్యో తంగం... గొడవలంటే నాకు భయం. బొద్దింక వచ్చినా నేను పారిపోతా.', post=0.5)]),
 dict(id='s19', set='village', desc='Thangam pulls a long-hair wig and fake beard out of the basket',
      beats=[W(1.0, 'pull'), S('THANGAM', 'ఇదేంటి?! విగ్గు... గడ్డం... వరా, రాత్రిపూట దేవర వేషం వేసేది నువ్వేనా?!', post=0.3),
             S('VARA', 'ష్ష్! తంగం! ఊరికి తెలిస్తే... నా మాస్ ఇమేజ్ పోతుంది!', post=0.3, tag='shush'),
             S('THANGAM', 'ఏ మాస్ ఇమేజ్? నీకున్నది మాస్క్ ఇమేజ్!', post=0.8)]),
 dict(id='s20', set='village', desc='Kunjara + henchmen surround; Thangam flips a henchman; Kunjara on ground',
      beats=[S('KUNJARA', 'వరా! ఈ రాత్రి సముద్రంలోకి రా... లేదంటే నీ తంగం మా దగ్గర ఉంటుంది!', post=0.3),
             W(1.8, 'flip'), S('THANGAM', 'నన్ను పట్టుకోవాలంటే మీకు ఇంకో జన్మ కావాలి రా!', post=0.4),
             S('KUNJARA', 'అన్నా... ఈ అమ్మాయే దేవర లాగుంది.', post=0.4),
             S('VARA', 'తంగం... నువ్వే నా హీరో.', post=0.8)]),

 # ---------------- NIGHT SEA : climax ----------------
 dict(id='s21', set='nightsea', desc='Foggy night sea; Vara in wig on small boat; Bhaira\'s torch boats surround',
      beats=[S('NARR', 'ఆ రాత్రి... ఎర్ర సముద్రం మళ్ళీ ఎరుపెక్కడానికి సిద్ధమైంది.', post=0.5),
             W(1.0), S('BHAIRA', 'దేవరా! పన్నెండేళ్లు! పన్నెండేళ్లు నీ కోసం ఎదురు చూశాను!', post=0.5)]),
 dict(id='s22', set='nightsea', desc='Vara heroic low angle, fake voice; sneeze blows wig off into the sea',
      beats=[S('VARA_FAKE', 'భైరా... సముద్రం మీద కన్నేస్తే... ఆ సముద్రమే నిన్ను మింగేస్తది!', post=0.5),
             W(0.5, 'tickle'), S('VARA', 'హ... హ... హాచ్!', post=0.2, tag='sneeze'), W(2.2, 'wigfly')]),
 dict(id='s23', set='nightsea', desc='Bhaira shock then laugh; henchmen laugh; Vara embarrassed',
      beats=[S('BHAIRA', 'వరా?! నువ్వా?!', post=0.3, tag='shock'),
             S('BHAIRA', 'ఇన్నేళ్ళు నన్ను భయపెట్టింది... ఒక విగ్గా?! హహ్హహ్హ!', post=0.4, tag='laugh'),
             S('VARA', 'అది... అది ప్రీమియం విగ్గు భైరా.', post=0.6)]),
 dict(id='s24', set='nightsea', desc='Bhaira lunges with axe, Vara dodges, fights two henchmen, gets cornered',
      beats=[S('BHAIRA', 'ఈ రోజుతో నీ కథ ముగిసింది!', post=0.2, tag='lunge'), W(4.2, 'fight')]),
 dict(id='s25', set='nightsea', desc='Sea rumbles; wave rises; Devara bursts out riding shark Sundaram (slow-mo)',
      beats=[W(1.2, 'rumble'), S('NARR', 'అప్పుడు... సముద్రం ఒక్కసారిగా ఊపిరి పీల్చుకుంది.', post=0.2), W(3.4, 'burst')]),
 dict(id='s26', set='nightsea', desc='Devara lands on boat (deck shakes), hero line; Kunjara faints',
      beats=[W(0.8, 'land'), S('DEVARA', 'నా కొడుకు మీద చెయ్యి వేస్తే... ఈ సముద్రం మళ్ళీ ఎర్రబడుతుంది.', post=0.5),
             S('KUNJARA', 'అన్నా... దేవర... నిజంగానే బతికే ఉన్నాడు!', post=0.2), W(1.2, 'faint')]),
 dict(id='s27', set='nightsea', desc='Bhaira vs Devara face-off, comic reveal of retirement',
      beats=[S('BHAIRA', 'నువ్వు... నువ్వు చచ్చిపోయావ్ కదా!', post=0.4),
             S('DEVARA', 'చచ్చిపోలేదు రా... రిటైర్ అయ్యా. పక్క దీవిలోనే ఉన్నా.', post=0.3),
             S('DEVARA', 'పన్నెండేళ్లు వెతికావా? Google Maps లో ఒక్కసారి చూడలేదా?', post=0.7)]),
 dict(id='s28', set='nightsea', desc='One blade spin: henchmen fly into sea, axe breaks; Bhaira in water, shark circles, spits him back',
      beats=[W(3.0, 'spin'), S('BHAIRA', 'దేవరా! నీ చేపని ఆపు రా!', post=0.3),
             S('DEVARA', 'సుందరం... వదిలేయ్. వాడు చేదుగా ఉంటాడు.', post=0.3), W(2.0, 'spit')]),
 dict(id='s29', set='nightsea', desc='Father-son hug, warm moment, comic close',
      beats=[S('DEVARA', 'బాగా చేశావ్ రా వరా. కానీ ఆ విగ్గు... నా జుట్టు కంటే బాగుంది.', post=0.3),
             S('VARA', 'ఆన్‌లైన్ లో కొన్నా నాన్నా. EMI లో.', post=0.8)]),

 # ---------------- CLIFFHANGER ----------------
 dict(id='s30', set='nightsea', desc='Foghorn; huge dark ship emerges from fog, red lanterns; all turn',
      beats=[W(1.8, 'horn'), S('NARR', 'కానీ అదే రాత్రి... ఎర్ర సముద్రం మీదకి... ఇంకో నీడ వచ్చింది.', post=1.0)]),
 dict(id='s31', set='nightsea', desc='Hooded figure on prow lowers hood: Devara\'s face, sunglasses, grey streak',
      beats=[S('YETHI', 'దేవరా...', post=1.2, tag='hood'), W(1.0, 'reveal'), S('YETHI', 'యతి వచ్చాడు.', post=1.0)]),
 dict(id='s32', set='nightsea', desc='Devara and Vara stare, look at each other; Bhaira in water complains',
      beats=[S('VARA', 'నాన్నా... వీడు... అచ్చం నీలాగే ఉన్నాడు!', post=0.4),
             S('DEVARA', 'అయ్యో... అమ్మ ఎప్పుడూ చెప్పేది... నాకు ఒక తమ్ముడు ఉన్నాడని... జాతరలో తప్పిపోయాడని!', post=0.4),
             S('BHAIRA', 'ఇదేం ఫ్యామిలీ రా బాబూ... ఒకే మొహం మూడు సార్లు!', post=0.7)]),
 dict(id='s33', set='nightsea', desc='Yethi smirk close-up, thunder, cut to black',
      beats=[S('YETHI', 'Part 2 లో కలుద్దాం... అన్నయ్యా.', post=1.6, tag='smirk')]),

 # ---------------- OUTRO : back to the hut ----------------
 dict(id='s34', set='hut', desc='DSP jaw dropped, tea overflowing; Singappa winks',
      beats=[W(0.8), S('DSP', 'అసలు... ఈ కథ నిజమేనా సింగప్ప గారూ?', post=0.5),
             W(1.0, 'sip'), S('SINGAPPA', 'సముద్రం అబద్ధం చెప్పదు సారూ...', post=0.5),
             S('SINGAPPA', 'కానీ నేను చెప్తా.', post=0.4, tag='wink'), S('SINGAPPA', 'హహ్హహ్హ!', post=1.0)]),
 dict(id='s35', set='endcard', desc='End card: దేవర 2 - మిగతా కథ త్వరలో', beats=[W(6.0, 'end')]),
]

# TEMPLATES.md — fill-in templates for every film (3D and 2D)

Agents: copy the block, fill every `<...>`, save under `<film>/story/` or `<film>/prompts/` (`<film>` = `videos/<film_slug>/`). Do not invent new formats.

---

## 1. Story / style bible — `<film>/story/bible.yaml`
```yaml
title: "<title>"
logline: "<one sentence: who wants what, what stops them, the twist>"
premise: "<the user's topic as one sentence — every scene must serve it (§16.1)>"
promise: "<what the viewer is waiting to see / gets at the end>"
track: 3d | 2d
style_preset: STYLIZED_3D | SEMI_REAL | TOON | FLAT_CARTOON | ANIME_CEL | STORYBOOK_PAINTED | PAPER_CUTOUT
tone: {primary: "<dark humour | satire | suspense | action | tragedy | horror-tinged | …>", secondary: "<…>", beats: [dread, laugh, anger, grief, triumph]}   # adult range, never default cute (§16.2)
audience: "adults 18–35 (YouTube); not kids"
languages:
  main: en                     # ISO code of dialogue + titles: en | te | hi | ta | kn | ml | bn | …
  extra: []                    # other versions to produce, e.g. [te] for an English + Telugu release
title_mode: single             # single | dual_stacked | dual_sequential | per_version  (TEMPLATES §13.3)
text:                          # every on-screen string, per language (never hard-code text in code)
  en: {title: "<English title>", subtitle: "<tagline>", to_be_continued: "To be continued...", disclaimer: "<fan-made fiction disclaimer>"}
  te: {title: "<Telugu title>", subtitle: "<...>", to_be_continued: "<...>", disclaimer: "<...>"}
palette: {name: "<e.g. neo-noir teal/amber>", colors: ["#<hex>", "#<hex>", "#<hex>", "#<hex>", "#<hex>"], accent: "#<hex>"}   # from tone; must differ from every earlier film (§16.3)
line: {weight_px_1080p: 4, color: "#1a1410"}            # 2D only
shading: flat | one_cel_shadow | soft_gradient          # 2D only
world: {era: "<...>", region: "<...>", recurring_motifs: ["<...>", "<...>"]}
locations:
  - id: <slug>
    description: "<what it looks like>"
    time_of_day: dawn|day|golden|dusk|night
    weather: clear|rain|storm|fog
    key_light: "<direction, colour temperature>"
    practicals: ["<lanterns/torches/neon>"]
    ground: "<flat surface + height, e.g. sand z=0.0>"
continuity_rules: ["<HERO holds blade in RIGHT hand>", "<axis of action on the boat = world X>"]
disclaimer: "<fan-made fictional parody, entertainment only>"   # when parodying existing IP
```

## 2. Story structure (5–7 min comedy/action short)
| beat | % of runtime | purpose |
|---|---|---|
| Cold open / hook | 0–8 % | mystery or big visual in < 10 s, narrator line |
| Title | ~8 % | 4–6 s slam |
| Setup | 8–25 % | world, hero's problem, first laugh |
| Twist 1 | ~25 % | reframes everything (comedic reveal) |
| Escalation | 25–60 % | villain plan, side characters, running gag ×3 |
| Midpoint gag | ~50 % | biggest laugh |
| Climax | 60–85 % | action set piece + hero entry |
| Twist 2 / cliffhanger | 85–95 % | sets up Part 2 |
| Button / outro | 95–100 % | callback joke + end card |
Rules: **every scene serves the topic (§16.1)** · **move to a new location every 30–60 s (§14)** · a laugh or reveal every 20–30 s · every scene ends on a turn · callbacks to earlier jokes · max 2 lines per speech, ≤ 18 words each · stage directions in `action` beats, not in dialogue.

## 3. Character card — `<film>/story/characters/<ID>.yaml`
```yaml
id: HERO
archetype: mass_hero | timid_son | villain | sidekick_comic | heroine_sassy | wise_elder | officer | mystery_twin | child | creature | narrator
role_in_story: "<one line>"
personality: ["<3 adjectives>"]
catchphrase: "<optional>"
body: {height_m: 1.86, build: 1.10, gender: male, age: 40, posture: "<chest out, slow heavy steps>"}
face: {shape: "<square jaw>", eyes: "<brown, kohl-lined>", brows: thick, nose: broad, mouth: "<wide>", ears: normal, marks: "<scar left brow>"}
hair: {style: "<long combed back>", color: "#121010", facial: "<full beard + thick mustache>"}
skin: "#5c3320"
costume: {top: "<black shirt, sleeves rolled, open V>", bottom: "<dark checked lungi folded to knee>", feet: sandals, accessories: ["<silver kada R wrist>"]}
signature_prop: {name: "<machete>", hand: R, grip: fist}
silhouette_test: "<what must read in pure black silhouette>"
default_expression: fierce
walk_style: {stride: 0.82, bob: 0.02, arm_swing: 0.6, speed: 1.2}
voice:
  engine: step | maya | chatterbox | zonos | elevenlabs
  design: "<from §6 presets>"
  fx: "<ffmpeg filter, optional>"
image_prompt_id: "<key into §8.2 when track = 2d>"
```

## 4. Screenplay — `<film>/story/screenplay.yaml`
```yaml
shots:
  - id: s01
    location: <location id>
    function: "<what the audience learns — a shot with no function gets cut>"
    size: WS | LS | MLS | MS | MCU | CU | ECU          # §7
    camera: {move: push|pull|pan|tilt|crane|orbit|handheld|locked, angle: eye|low|high|dutch, lens_mm: 35}
    view: three_quarter          # 2D only: front | three_quarter | side
    layout: {HERO: [0.62, 0.92, 1.0], VARA: [0.30, 0.92, 0.95]}   # 2D only: x%, ground y%, scale
    beats:
      - wait:   {sec: 1.2, tag: <label>, action: "<what happens>"}
      - say:    {who: <ID>, text: "<line>", emotion: <§5 key>, para: "<laugh|sigh|gasp|...>", pace: slow|normal|fast, pre: 0.2, post: 0.4, tag: <label>}
      - action: {who: <ID>, motion: "<text-to-motion prompt or pose-library key>", tag: <label>}
    sfx:   ["<event> @<tag>[+sec]"]
    music: {cue: <cue id>, level: low|mid|high}
    fx:    ["<dust_puff @land>", "<speed_lines>"]
```

## 5. Emotion → acting map (3D rig values · 2D drawing parts · voice)
| emotion | 3D face (brows / lids / mouth) | 2D parts | body | voice |
|---|---|---|---|---|
| neutral | 0 / 1.0 / smile .1 | brows neutral, eyes open | idle breathing | calm |
| happy | up .25 / .85 / smile .85 | brows up, eyes happy-arc, mouth smile | small bounce, open chest | bright, faster |
| laugh | up .4 / .45 / grin + open | eyes closed-arc, mouth D/E, head back | shoulders shake, hand on belly | `<laugh>` / `[laugh]` |
| angry | inner down −1.0 / .78 / frown .7 | brows angry, eyes narrow, teeth | lean in, fists, point | loud, clipped |
| fierce | −.7 / .72 / frown .3 | brows angry, eyes narrow | still, chin down, wide stance | low, slow |
| shocked | up 1.0 / 1.35 / O .6 | eyes wide + tiny pupils, mouth E/F, sweat drop | jump back, hands up, squash-stretch | gasp |
| scared | inner up .9 / 1.25 / frown .6 | brows sad, eyes wide, trembling (±2 px) | shrink, shrug, step back | trembling, high |
| sad | inner up 1.0 / .7 / frown .6 | brows sad, eyes half, mouth frown | head down, slumped | soft, slow, `<sigh>` |
| smug | asym / .7 / half-smile | one brow up, eyes half, smirk | arms crossed, head tilt | slow, teasing |
| deadpan | 0 / .55 / flat | eyes half, flat mouth | no motion, slow blink | flat |
| wise | up .15 / .7 / smile .35 | brows soft, eyes half-smile | slow nods | warm, slow |
| embarrassed | inner up .4 / .8 / smile .3 | blush lines, eyes side-glance | scratch head | quieter, faster |

## 6. Voice casting presets (natural-language voice design; Maya1 / Step-Audio-EditX / ElevenLabs)
- **mass_hero:** "Deep, powerful, gravelly male voice in his forties, slow deliberate commanding delivery, heroic and intimidating, cinematic, close-mic, no background noise."
- **timid_son:** "Soft, gentle young man in his twenties, slightly nervous and polite, warm mid pitch, quick hesitant pacing."
- **villain:** "Rough, raspy, aggressive male voice, low pitch, loud and mocking, fast angry bursts, menacing laugh."
- **sidekick_comic:** "High-pitched excitable comic man, very fast chatter, squeaky when scared, cartoonish energy."
- **heroine_sassy:** "Bright confident young woman, sharp witty delivery, playful sarcasm, clear mid-high pitch."
- **wise_elder:** "Warm raspy elderly storyteller in his seventies, slow, knowing, gentle chuckles, grandfatherly."
- **officer:** "Firm clear middle-aged male officer, crisp formal diction, slightly impatient."
- **mystery_twin:** "Very deep, smooth, slow, menacing whisper-like male voice, calm confident villainy."
- **narrator:** "Rich cinematic trailer narrator, slow dramatic pauses, deep and resonant."
- **child:** "Energetic young child, high pitch, curious, fast and giggly."
Line-level control: full per-line direction + per-model controls in §15.

## 7. Camera presets
| size | frame height | lens (3D) | 2D zoom | use |
|---|---|---|---|---|
| ESTABLISHING | world | 24 mm crane | 0.8 pan | new location |
| WS | 5 m+ | 24 | 0.9 | geography, action |
| LS | 2.4 m | 30 | 1.0 | full body, entrances |
| MLS | 1.6 m | 35 | 1.15 | walk & talk |
| MS | 1.1 m | 40 | 1.35 | conversation |
| MCU | 0.7 m | 50 | 1.7 | dialogue (default) |
| CU | 0.45 m | 60 | 2.2 | emotion, punchlines |
| ECU | 0.25 m | 85 | 3.0 | eyes, reveals |
Rules: 180° axis · 30° rule between cuts · screen direction · eyeline match · speaker filmed from the side they face (30–45° off axis) · reaction-before-reveal · hold 0.5–1 s after punchlines · low angle + slow push for hero beats · handheld noise 0.01–0.03 for action · locked-off wide for comedy.

## 8. Vector character design spec (2D track) — `<film>/story/characters/<ID>.design.yaml`
No image generation. Every field maps to a procedural vector part (MASTER_PROMPT_2D §3).
```yaml
id: HERO
proportions: {heads_tall: 5.5, head_w: 0.36, shoulder_w: 1.25, hip_w: 0.9, leg_len: 0.48, arm_len: 0.42}   # stylization knobs
build: slim | average | heroic | round
head: {shape: egg | square | round | long, jaw: 0.32, chin: pointed | square | round, cheeks: 0.2}
eyes: {type: round | almond | dot | anime, size: 0.18, spacing: 0.36, iris: "#5a3a22", lashes: false, kohl: true}
brows: {thickness: 1.25, arch: 0.3, color: "#151110"}
nose: button | pointy | broad | hooked | line
mouth: {width: 0.34, lips: thin | full, lip_color: "#7a3b2e"}
ears: {size: 1.0, shape: round | pointed}
hair: {style: long_wavy | combed_back | spiky | curly_cloud | bun | braid | bald_ring | short_messy, color: "#121010", highlight: "#3a3330", volume: 1.1}
facial_hair: {beard: full | stubble | goatee | none, mustache: thick | thin | police | none, color: "#121010"}
skin: {base: "#8a5a3c", shadow: "#6b4229", blush: "#a8604a"}
outfit:
  top: {type: shirt_open_v | tshirt | vest | blouse | kurta | coat, color: "#141418", sleeve: elbow | short | long | none, pattern: none | checks | stripes}
  bottom: {type: lungi_knee | dhoti | pants | skirt_long | shorts, color: "#202430", pattern: checks, pattern_color: "#5a1010"}
  feet: sandals | shoes | barefoot
  accessories: [kada_R_silver, thread_necklace]
prop: {name: machete, hand: R, shape: curved_blade, color: "#b9bcc2"}
line: {weight: 4.0, color: "#1a1410"}       # inherits from the style bible if omitted
shadow: {enabled: true, angle_deg: -35, opacity: 0.35}
signature_pose: "fists clenched, chin down, wide stance"
```
Hand-made SVG instead: one layer/group per bone (`head`, `torso`, `upperarm_L`, …), pivot marked by a small circle with id `pivot_<bone>`, mouth visemes as layers `mouth_A … mouth_X`, eyes `eye_open / eye_half / eye_closed`.

### 8.x External raster art (optional, user-made only)
Only static thumbnails/posters may be raster (user makes them in Gemini/ChatGPT image). Prompt pattern:
"YouTube thumbnail 16:9: <hero> in an iconic heroic pose, <dramatic setting>, strong rim light, high contrast, saturated <palette>, expressive face readable at phone size, clean empty area on the <left/right> 40 % for title text, no text, no logo." Titles are always added by code (§13).

## 9. SFX cue template — `<film>/tools/sfx_cues.py`
`{shot: "s14", t: "drop+0.85", event: "coconut bonk", prompt: "single loud cartoon coconut bonk on a head, hollow wooden knock", engine: "foley|moss", gain_db: 0}`
Always include: ambience bed per location (20–30 s seamless loop), every visible impact / throw / landing / splash / footstep run / prop handling / lightning.

## 10. Music cue sheet — `<film>/story/music.yaml`
```yaml
- {id: prologue, start: "0:00", end: "0:25", mood: "dark epic storm", tempo: 80, instruments: "low strings, war drums, wordless male chant", intensity: 0.6, stings: ["0:13 hit"]}
```
Prompt pattern (ACE-Step): "instrumental, no vocals, <genre>, <instruments>, <mood>, <tempo> BPM, cinematic film score, seamless loop".

## 11. YouTube package template
Title (≤ 100 chars: hook + keywords + "Fan Made" when parody) · description (hook paragraph, story tease without spoilers, chapters from `timeline.json`, credits for AI tools, disclaimer, 3–5 hashtags) · 20–25 tags · pinned comment asking for Part 2 · "Altered or synthetic content" = yes.

## 12. Staging, tracking, focus, orientation & timing bible (3D and 2D — mandatory)
### 12.1 Scene map (per location) — `<film>/story/maps/<location>.yaml`
Top-down coordinates in metres (3D) or % of the panorama (2D) for: every character mark (start/end), every prop (owner + which hand), entrances/exits, camera position per shot, key-light direction, the **axis of action line**, ground height of every walkable surface. Props keep their position between shots unless a beat moves them (continuity log: `prop, shot, position, holder`).
### 12.2 Orientation
- Facing = yaw of each character per beat; dialogue partners face each other ±20°; listeners turn toward the speaker within 6–10 frames of the speaker starting.
- **Screen direction:** a character exiting frame-right enters the next shot from frame-left; chases keep one direction; cross the axis only with a visible move or a neutral (head-on) shot.
- **Gaze hierarchy:** eyes move first (2–4 frames ahead) → head (4–8 frames) → torso/feet (8–14 frames). Never snap the body without the eyes leading.
- **Eyelines:** in singles the off-screen partner's eyeline points to the correct side and height (slightly above/below lens for height differences).
### 12.3 Tracking (look-at & camera follow)
- Heads/eyes **track moving targets** (thrown objects, entering characters, ships) via a look-at track with 3–6 frames of lag, yaw clamp ±75°, pitch −40…35°; blink on big head turns.
- Camera follow = critically-damped spring (half-life 0.25–0.5 s); **lead room** ⅓ of frame ahead of a moving subject; **headroom** ~10 % in MCU/CU; eyes on the upper third line; assert in QA that heads/feet never leave frame unintentionally.
- Thrown/falling objects: **ballistic arcs** (g = 9.81 m/s² scaled to the shot), consistent spin, contact frame + squash on impact, ground shadow under airborne objects, smear/motion blur when fast.
- Held props follow the hand bone exactly (grip offset); hand-offs have a frame where both hands touch.
### 12.4 Focus & attention
- One **attention target** per moment (speaker, reacting face, key prop): brightest/most contrasty/sharpest spot; cut so the new target sits where the eye already is (**eye-trace**).
- 3D depth of field: CU f/2–2.8, MCU f/2.8–4, MS f/4–5.6, wides f/8. **Rack focus** to the next speaker 6–12 frames before their line; to a prop on its reveal beat. 2D: blur layers by depth, keep the target layer sharp.
- Use framing (doorways, foreground silhouettes), light pools and vignettes to point at the target; never two competing focal points.
### 12.5 Timing (24 fps)
| moment | frames |
|---|---|
| anticipation (small / big) | 3–5 / 6–10 |
| fast action (punch, throw) | 3–6 |
| settle / follow-through | 6–14 |
| reaction delay after a stimulus | 6–12 (bigger shock → longer freeze, then a fast take) |
| comic beat before a punchline | 12–24 (silence) |
| hold after a punchline / reveal | 12–24 (up to 36 for big laughs) |
| blink | 4 |
| head look-at turn | 6–10 |
| walk cycle (normal / brisk) | 24–28 / 18–20 per 2 steps |
| run cycle | 12–16 per 2 steps |
| shot length | dialogue 3–5 s · action 0.8–2 s · establishing 3–6 s |
| on-screen text read time | 0.33 s per word + 1 s |
Editing: cut on action, J/L-cuts (audio leads/lags picture 6–12 frames), match cuts on shape/motion, never cut inside a held punchline beat.
### 12.6 Physics plausibility
Heavy = slower ease-in + bigger anticipation; light = fast reaction + more overshoot; momentum carries through turns (overlap); contact shadows/decals at every foot plant and landing; water = splash + ripples + drips; cloth/hair secondary motion always on.

## 13. Titles, intro & outro — language-agnostic (English, Telugu, Hindi, … any script)
Nothing about language is hard-coded. Every title/card reads its text, script and fonts from the bible (`§1 languages`) and the font registry below. The same title style works for any language; only the text + font change.

### 13.1 Text engine (one path for every script)
`uharfbuzz` shapes the string with the script/language tags from the bible (correct ligatures and conjuncts for Indic, Arabic, Thai, etc.; kerning for Latin) → `fontTools` glyph outlines → vector paths.
- **3D (Blender):** paths → curve objects → extrude 0.05–0.15, bevel 0.01–0.03 (3–4 segments) → materials (gold/chrome anisotropic metal, molten emissive edge, stone, neon) → animate.
- **2D (skia):** draw paths with fills/gradients/strokes/glows; animate per glyph **cluster** (never split a cluster — conjuncts/ligatures stay intact).
- Missing glyph check: before rendering, verify every cluster maps to a real glyph in the chosen font (no tofu boxes); fall back to the next font in the registry for that script.
- Right-to-left scripts: lay out with HarfBuzz direction = RTL and mirror slide-in directions.

### 13.2 Font registry (free, SIL Open Font License — Google Fonts) — `<film>/assets/fonts.yaml`
Pick fonts by **script × mood**; one display face for the title + one clean face for subtitles/credits, both covering the script.
| script | mass / action | epic / mythic | comedy / cartoon | friendly / round | handwritten | clean (credits/subs) |
|---|---|---|---|---|---|---|
| **Latin** (English…) | Bebas Neue, Anton, Oswald | Cinzel, Cinzel Decorative | Bangers, Luckiest Guy, Lilita One | Fredoka, Baloo 2 | Caveat, Kalam | Montserrat, Inter |
| **Telugu** | Ramabhadra, Gidugu | Sree Krushnadevaraya, Suranna | Timmana | Mallanna | NTR (Bapu-style) | Noto Sans Telugu |
| **Devanagari** (Hindi…) | Teko, Rajdhani | Rozha One, Martel | Baloo 2 (Devanagari) | Mukta | Kalam | Noto Sans Devanagari, Hind |
| **Tamil** | Catamaran (Black) | Pavanam / Noto Serif Tamil | Baloo Thambi 2 | Mukta Malar | — | Noto Sans Tamil |
| **Kannada** | Baloo Tamma 2 | Noto Serif Kannada | Baloo Tamma 2 | Hind (Kannada-capable families) | — | Noto Sans Kannada |
| **Malayalam** | Baloo Chettan 2 | Noto Serif Malayalam | Baloo Chettan 2 | Manjari | — | Noto Sans Malayalam |
| **Bengali** | Baloo Da 2 | Noto Serif Bengali | Galada | Hind Siliguri | — | Noto Sans Bengali |
| **Any other** | — | — | — | — | — | Noto Sans/Serif <Script> (always the fallback) |
Rules: verify each font's licence + glyph coverage at build time; keep 2 fallbacks per script; match stroke weight between the title font and the credit font; Latin and Indic titles side by side need optical size matching (scale Indic ~1.1–1.2× so x-heights look equal).

### 13.3 Bilingual / multilingual titles
Bible field `title_mode`:
- `single` — title in the film's main language only.
- `dual_stacked` — main-language title large, second language below at 45–60 % size (e.g. Telugu over English, or English over Hindi).
- `dual_sequential` — show language A, morph/cross-dissolve into language B on the same beat (great for bilingual audiences).
- `per_version` — render separate intro/outro files per language version (`out/<film>_<lang>.mp4`), same animation, different text/fonts/voice track.
Titles, "to be continued" lines, disclaimers and end-card text all come from `bible.yaml → text.<lang>.*`; voices/subtitles follow the same language keys.

### 13.4 Title animation styles (language-independent; pick one per film; 4–8 s)
1. **Mass slam** — black → title scales 1.6→1.0 with back-ease overshoot, 6-frame camera shake, shockwave ring, embers/sparks, 2-frame white flash, slow push-in. (action)
2. **Metallic light sweep** — extruded gold/chrome glyphs, a specular light band sweeps across (direction follows reading order), anamorphic flare, dust motes. (epic/premium)
3. **Mask reveal** — revealed behind smoke, a passing object, a wave or the hero's silhouette. (cinematic)
4. **Ink/paint bleed** — strokes grow along glyph skeletons, soft ink spread. (storybook)
5. **Handwriting stroke-on** — handwritten font drawn in reading order with a nib glow. (warm/personal)
6. **Letter/cluster cascade** — glyph clusters drop/flip in with 2–3 frame stagger and overshoot. (comedy)
7. **Particle assemble / disintegrate** — sparks or sand converge into the glyphs; outro reverses. (fantasy)
8. **Glitch/RGB split** — channel offsets, scanline jitter, block displacement 8–12 frames then lock. (thriller/tech)
9. **Elegant fade + tracking** — letter-spacing expands 0→+15 % with a soft fade (Latin only; for Indic scripts scale + fade instead — never letter-space connected scripts). (drama)
10. **Logo sting** — 2–3 s channel ident with a sound hit (start of every video).
Rules: title-safe 90 % (Shorts 80 %); main title ≥ 8 % of frame height; contrast ≥ 4.5:1 (glow/shadow plate if needed); sync the reveal to a music hit; hold the readable state ≥ 1.5 s (longer for longer text: 0.33 s/word + 1 s).

### 13.5 Intro & outro structure
- **Intro:** 5–15 s cold-open hook → title (style above) → optional channel sting.
- **Outro / end card:** 10–20 s (YouTube end screens need 5–20 s at the very end): callback gag or calm landscape plate, "to be continued" line, end title, small disclaimer — all text from `text.<lang>`; **reserve empty areas for YouTube end-screen elements** (video tiles left/right, subscribe circle).
- Sound: whoosh-in → hit on reveal → riser into the first scene; outro = music resolve + soft ambience tail.
- Optional AI-video plates (user-made with Veo etc.): prompt them with an empty text area; the code composites the title in the right language.

## 14. Engagement, variety & pacing (YouTube retention) — mandatory, checked before any rendering
A YouTube film lives or dies on retention. **Never build a film in one room, one location or one camera setup.** Talking heads in a closed set = rejected.
### 14.1 Location & look budget (hard minimums)
| | long (5–7 min) | long (2–4 min) | Shorts (≤ 60 s) |
|---|---|---|---|
| distinct locations | **≥ 8** | ≥ 5 | ≥ 3 backdrops |
| exterior / open-air share | ≥ 50 % of runtime | ≥ 50 % | ≥ 1 exterior |
| moving set (vehicle, boat, chase, crowd march, flight) | ≥ 1 | ≥ 1 | optional |
| spectacle set piece (storm, fight, festival, crash, giant reveal) | ≥ 2 | ≥ 1 | 1 (the hook or payoff) |
| lighting looks (time of day / weather) | ≥ 3 | ≥ 2 | ≥ 1 change |
| longest continuous stay in one location | ≤ 60 s | ≤ 45 s | ≤ 20 s |
| one location's total share | ≤ 25 % | ≤ 30 % | ≤ 50 % |
Location ideas to mix (procedural; redress kits cheaply with new colours/props/light): village street, busy market, beach, open sea / boat deck, cliff top, forest path, temple / festival ground, river bank, rooftop at night, highway / vehicle chase, island, hill-top viewpoint, police station, home courtyard, cave, storm sea. Interiors only as short contrast beats.
### 14.2 Visual change cadence
- Average shot length: dialogue 2.5–4 s · action 0.8–2 s · Shorts 1–2 s. Something **new on screen every ≤ 5 s** (cut, camera move, entrance, prop reveal, FX, location change).
- No static camera > 4 s (except a held comic reaction). Each dialogue scene has ≥ 1 blocking change (characters move, stand, cross, turn).
- Every new location opens with a 1.5–3 s establishing shot (wide, moving camera, life in it).
- Transitions do work: match cuts, whip pans, travel montage (3–5 quick shots), map/route wipe, flashback or imagination cutaway gags, split screen for phone calls / parallel action.
### 14.3 Retention curve (beat timing)
- **0–5 s** (Shorts 0–1.5 s): the strongest visual + a line that opens a question. No logo or slow fade first.
- By 15 s: the promise / goal is clear (what we are waiting to see).
- **Re-hook every 30–45 s**: new location, reveal, stakes jump, a new character's entrance or a big gag.
- Midpoint: biggest escalation or twist. Climax: the largest set piece in the most open, dynamic location.
- No exposition block > 10 s; no dead air > 1.5 s except deliberate comic beats; trim the first and last 0.5 s of most dialogue shots.
- Ending: payoff + callback + cliffhanger / button; end card 10–20 s.
### 14.4 Characters that carry a video
- Each main character: a visual hook (silhouette, colour, prop), a clear want, a catchphrase or verbal tic, a distinct energy/walk, a running gag.
- Long films: 3–6 speaking characters + background extras so places feel alive. Entrances are events (music hit, camera move, reaction shots).
- Characters **move through space** (walk-and-talk, chase, ride, climb, fall) instead of standing and talking. Cut to reactions often — faces sell comedy.
- Background life in every exterior: crowds, animals, birds, waves, vehicles, wind in trees, smoke, flags.
### 14.5 Self-check (run on the outline and on `audio/timeline.json`; fix failures before rendering)
Count distinct locations, exterior share, longest single-location stretch, one location's share, average shot length, longest static shot, gaps between re-hooks. Print a table; any failure → rewrite the outline/shots. Show the location list + scene table to the user at the checkpoint.
**Reject these patterns:** whole film in one room · back-and-forth talking heads · same camera angle 3+ times in a row · walking with nothing happening · scenes that end without a turn · long title/logo before the hook.

## 15. Voice performance (TTS acting: tone, pace, emotion) — mandatory
A flat, same-speed read kills a video even with great pictures. Direct every line like an actor.
### 15.1 Per-line direction (screenplay fields)
```yaml
- speaker: VARA
  text: "You think the fish... is just a fish?"
  emotion: sly            # one main emotion (§5)
  intensity: 2            # 1 subtle · 2 clear · 3 big
  pace: slow              # slow | normal | fast | very_fast  (targets below)
  volume: low             # whisper | low | normal | loud | shout
  pause_before: 0.4       # seconds — comic/dramatic beats
  pause_after: 0.2
  emphasis: [fish]        # words to hit
  nonverbal: [chuckle]    # laugh, chuckle, sigh, gasp, breath, scoff, sob, gulp
  subtext: "he knows the secret and enjoys teasing"
```
### 15.2 Pace, pauses & variety
- English speed targets: normal 150–170 words/min · excited/comic 180–210 · scared rambling 210–240 · dramatic/menacing 110–130 · narrator 130–150. Other languages: measure syllables/s on a reference take and scale the same way.
- **Vary pace and energy between consecutive lines** — never 3 lines in a row with the same emotion + pace. Arguments speed up; reveals slow down.
- Pauses: before a punchline 0.4–0.8 s · dramatic reveal 0.8–1.5 s · interruption = cut the previous line with "—" and overlap 0.1–0.3 s · quick banter 0.05–0.2 s gaps.
- Text tricks: punctuation drives prosody ("..." hesitation, "—" cut-off, "!" energy, "?" lift); short sentences; spell out numbers; respell hard names phonetically; native script for each language (never transliterate through another language).
### 15.3 Controls per model (use what the chosen model supports; check its model card for exact names)
| model | emotion / tone | pace / energy |
|---|---|---|
| **ElevenLabs v3/v4** (API) | inline audio tags: `[excited]` `[whispers]` `[shouts]` `[sarcastic]` `[nervous]` `[sad]` `[laughs]` `[sighs]` `[gasps]` | stability 0.30–0.45 for acting, 0.55–0.7 for narrator; speed 0.9–1.15; CAPS on one emphasized word; `language_code` per language |
| **Maya1** | voice description (age, gender, timbre, accent, energy) + inline emotion tags such as `<laugh>` `<sigh>` `<whisper>` `<angry>` `<gasp>` `<cry>` | describe pace in the voice description ("fast excited delivery"); split long lines |
| **Chatterbox Turbo** | paralinguistic tags `[laugh]` `[chuckle]` `[sigh]` `[gasp]` `[cough]`; the reference clip carries the tone | `exaggeration` 0.3 calm … 0.8+ dramatic; lower `cfg_weight` (~0.3) = slower, more deliberate; 0.5 default |
| **Step-Audio-EditX** | generate (or clone), then **edit** emotion (happy/sad/angry/fear/surprise…) and style (whisper, serious, childlike…) — 1–3 edit passes for a stronger effect; insert paralinguistics | speed edit (faster/slower) on the same take |
| **ZONOS3** | emotion vector (happiness, sadness, anger, fear, surprise…) + reference voice | `speaking_rate`; more pitch variation = more expressive |
| any | — | post: rubberband tempo 0.9–1.15 without pitch change (never outside 0.85–1.35) |
### 15.4 Casting & consistency
- Spread voices across pitch, age and energy so every character is recognisable with eyes closed. Lock one reference clip / seed / voice id per character for the whole film (and later parts).
- Key lines (hook, punchlines, reveals): generate 2–3 takes and pick the best.
### 15.5 Voice QA (before the timeline is final)
Whisper transcript vs script (no missing/extra words) · per-line pitch variance and words/min (flag monotone or wrong-pace lines and regenerate) · loudness matched per character · emotions match the picture (§5) · lines land on the beat timings of §12.5.

## 16. Quality bar — gripping, adult, purposeful (mandatory for 2D and 3D; audit before rendering)
The audience is **adults**, not kids. Every second must earn its place. If a frame, line, object or sound does nothing for the story, cut it.

### 16.1 Topic discipline (the #1 failure)
- Write a one-sentence **premise** from the user's topic and a **"what the viewer gets"** promise. Every scene must move the premise forward, raise its stakes, or pay it off. Off-topic scenes, side chatter and random gags not tied to the topic are deleted.
- **Every line of dialogue must do one job:** reveal character, push the plot, set up or land a joke, raise tension, or deliver information the viewer needs. Lines that do none (greetings, "let's go", repeating what we just saw, describing the obvious) are removed.
- No characters explaining what is on screen. Show it. Max one line of exposition in a row.
- Dialogue density: long films 40–60 % of runtime has speech; leave room for action, reactions and music. Shorts: lines only where they hit.
- Audit: for each line write its job in `story/line_audit.yaml`; any line with no job → delete or rewrite.

### 16.2 Tone — adult range, never default "light and cute"
Pick a **primary tone + secondary tone** in the bible from the topic; never default to cheerful/kid-friendly. Range to use: dark humour, satire, deadpan, absurd, slapstick, suspense, thriller, horror-tinged, crime, action/violence, revenge, tragedy, melancholy, romance, triumph, cringe/awkward, rage, fear, paranoia.
- A long film shows **at least 5 distinct emotional colours** (e.g. dread → laugh → anger → grief → triumph); Shorts at least 2 (a turn).
- Contrast drives impact: a laugh right after tension, silence before a shock, a sad beat inside comedy.
- Stakes are real: characters can fail, get hurt, lose things, die off-screen, be betrayed. Consequences carry into later scenes.
- Characters have edges: selfish, cowardly, ruthless, petty, obsessed, sarcastic — not just "nice".
- Violence and darkness are **stylized and implied** (impact frames, silhouettes, cutaways, sound, aftermath) — no gore, no real-world tragedy mockery, no hate toward real groups, no sexual content: keeps YouTube monetization safe.

### 16.3 Colour & look — a new palette every film
- Choose the palette from the tone in the bible (`style.palette`: 5–7 hex colours + `accent`), and **never reuse the previous film's palette** (check `videos/*/story/bible.yaml`). Examples: neo-noir teal/amber, blood-red + bone + ink black, sickly green horror, desaturated war grey + rust, sunset magenta/orange, cold moonlit blue, vintage film sepia, acid neon night, monochrome + one red accent.
- Each location gets its own variation (temperature, time of day) while keeping the film's palette. Darker scenes are allowed and encouraged when the tone wants them: deep shadows, rim light, single key light, fog, night.
- Value contrast: the subject is always the clearest read (lightest or most saturated); backgrounds are quieter (lower contrast, less saturation, softer detail).

### 16.4 Clean, purposeful frames
- **No useless objects.** Every prop/set piece must either be used (held, broken, thrown, hidden in), tell us about the place/character, or set up a later payoff (Chekhov's gun). Decorative clutter that competes with the subject is removed.
- Backgrounds support, never compete: simplified shapes, fewer details than characters, no busy patterns behind faces, depth via haze/blur/value.
- Scale is correct and consistent: doors ~2.1 m, cups fit a hand, a car is ~4.5 m, a boat dwarfs a person; the same prop keeps the same size in every shot (store real sizes in the scene map §12.1).
- Composition: one clear subject, rule of thirds, foreground framing for depth, negative space toward where a character looks or moves.

### 16.5 No filler time
- Banned: slow smooth walks with nothing happening, long establishing shots without information, characters standing waiting, repeated actions, slow fades between ordinary scenes.
- Travel = cut it (exit frame → arrive) or montage 3–5 quick shots with music; a walk on screen only if something happens during it (argument, chase, reveal).
- Enter scenes late, leave early. Start the shot mid-action. Speed ramps on action, cut on movement.
- Holds are only for jokes, shocks and emotion (§12.5 timings) — and then they are deliberate.

### 16.6 Object interaction & physical acting (must look real)
- **Grip:** the hand closes around the object (fingers wrap, thumb opposed), the object is parented to the hand bone for the whole hold, with no floating gap and no passing through fingers. Heavy objects use two hands and the body leans/sags.
- **Pick up:** look → reach (anticipation) → contact frame → lift with weight (slower for heavy) → settle.
- **Throw:** wind-up 6–10 frames → release on the forward arc → object follows a ballistic arc with spin → target reacts on impact (squash, debris, sound) → thrower follow-through.
- **Catch:** eyes track the object → hands move to meet it before arrival → impact absorbs (hands/arm give 2–4 frames) → secure grip.
- **Release / drop:** fingers open first, object falls with gravity, bounces/settles with sound; never vanishes.
- **Ignore / reject:** the character looks away first, then the body turns; the offered object stays visible in the other character's hand.
- **Hand-offs:** both hands touch for ≥ 2 frames; ownership switches on contact.
- Contacts: feet plant without sliding, hands touch surfaces they lean on, sitting compresses on the seat, objects cast contact shadows.
- Hit reactions: impact frame, recoil in the hit direction, delayed overlap (head, hair, clothes), recovery or collapse.

### 16.7 Camera with intent
- Every shot has a reason: reveal, emphasize, isolate, follow, or disorient. Choose lens/angle from the emotion: low angle = power/threat, high angle = weakness, dutch = unease, extreme CU = intensity, wide = isolation/scale, handheld shake = chaos.
- Vary shot sizes (wide → medium → close) and angles; never 3 similar shots in a row. Use push-ins on realisations, crash zooms on comic beats, POV shots for suspense, over-the-shoulder for confrontations.
- The camera tracks the most important object/person (§12.3): a thrown object, a raised weapon, a reacting face.

### 16.8 Sound: clean, purposeful, never noisy
- **Dialogue is king:** speech peaks clear on top; music ducks 8–12 dB under every line; ambience sits 18–25 dB below dialogue.
- **Music follows the emotion of each scene** — change cues at turns (suspense pulse, comic sting, sad piano, action drums); use **silence** before shocks and punchlines. No single loop wallpapering the whole film; no constant busy track under dialogue.
- Ambience is light and specific to the place (two or three layers max). No hiss, hum, or random noise beds.
- Every visible action that should make sound has one (footsteps on the right surface, grab, throw whoosh, impact, cloth, water); sounds that match nothing on screen are removed.
- Final mix −14 to −16 LUFS integrated, true peak ≤ −1 dBTP, no clipping; check on phone speakers and headphones.

### 16.9 Pre-render audit (print a table; fix every ✗ before rendering)
topic: every scene serves the premise ✓/✗ · lines with no job (count must be 0) · tones present (≥ 5 long / ≥ 2 Shorts) · palette differs from previous films · props without purpose (0) · filler shots (walks/holds without event: 0) · scale table consistent · interaction checklist per prop action · camera variety (no 3 similar in a row) · music cue changes at every turn · dialogue intelligibility (music ducked).

## 17. Hard failures from the "What If Thanos Came First?" film (rejected by the user) — mandatory, overrides any shortcut
That film shipped with female-sounding men, a kids-cartoon comedy script on a dark topic, and stiff, unreadable animation. Never repeat it.

### 17.1 Voices: gender, identity, proof
- **Never make characters by pitch/formant-shifting one base voice.** Every speaking character gets its **own real voice** from a TTS that supports voice design or cloning: Maya1 (describe gender/age/timbre), Step-Audio-EditX or Chatterbox with a **different reference clip per character**, Zonos3 speaker embedding, or ElevenLabs voice ids. Post-pitch only ±2 semitones, only to fine-tune.
- **Gender must match the character.** Male = male voice, female = female voice, child = child, creature = designed creature voice. Put `gender` + `age` in every character card and in the voice prompt.
- **Voice QA is a gate** (before the timeline is final): measure median F0 per line (librosa pyin). Male adults 80–170 Hz, female adults 165–260 Hz; any line outside its character's band → regenerate with another voice. Cast members must be audibly distinct (different reference clip/voice id, pairwise median F0 ≥ 15 Hz apart unless a different timbre is proven). Whisper transcript = script.
- **Casting reel first:** one test sentence per character, F0 measured, shown to the user as a table (character, gender, engine, voice id, F0) before the whole script is generated.
- Report honestly which engine and voice each character used and whether it ran on the Kaggle node.

### 17.2 Story: written for the topic, not for gags
- **Tone = what the topic implies.** A villain / war / invasion / "what if" topic is **serious by default** (dread, stakes, loss, irony). Humour is dry, rare (max 1 beat per scene) and never undercuts a threat. **No kids-cartoon comedy, catchphrase quips, puns, or sight-gags that make the antagonist a clown** unless the user asks for comedy.
- **A "what if" must be answered with consequences:** a cause → effect chain (what changes first, who is unprepared, what the world loses, the new equilibrium or twist). Nothing happens "because the script needs it". Every scene ends on a changed situation.
- **Characters from existing IP keep their core personality, powers and rules.** No out-of-character behaviour for a cheap laugh.
- **Script quality gate (before any voice or art):** write the full dialogue, then run a hostile review and fix it: (a) can any line be cut with no loss, (b) do two characters share the same rhythm or diction, (c) is any joke not needed by the premise, (d) does each character act from a want, (e) would a fan of the source accept the logic. Print the review.
- **Show the full script (every line) to the user and wait for approval.** Outline-only approval is not enough.

### 17.3 Animation: it must read, and it must act
- **Every shot shows one clear action in one clear sentence** (write it in the screenplay `function`). If a still does not show who does what to whom, reject the shot. No character standing with an arm stretched out for seconds, no figures sliding around, no characters overlapping each other.
- **Acting bar:** eyes lead the head and body (§12.2), weight shifts, anticipation + follow-through on every hit/throw, reaction shots, cuts on action. No body movement for more than 1.5 s unless it is a deliberate hold.
- **Character-art bar:** distinct silhouettes, recognisable costume and prop shapes, hands that grip, a head that turns (3/4 and profile), mouths that match visemes, believable anatomy. **Primitive polygon-head + capsule-limb figures are not acceptable final art.** If the procedural vector rig cannot reach this bar, build a better rig (layered parts, hands, hair, cloth) or switch to the 3D track. Never ship it and call it done.
- **Staging:** the geography of a fight or chase is visible (who is where, what is hit); big events get wide + impact + reaction.
- **Self-critique:** view the contact sheets and write one line per shot "what a stranger sees". Any shot that reads wrong is fixed. Judge against real YouTube animation, not against "it renders".

### 17.4 Process gates (stop and wait for the user)
1. **Gate A:** full script + cast table (voice ids, gender, F0) + tone/palette → user approves.
2. **Gate B:** a 10–15 s sample with final voices, music and the hardest scene → user approves.
3. Only then the full render. Never produce the whole film before Gate B.
4. Never say "done" or "reads well" about a film whose frames you have not viewed at speed (extract a 2–3 fps strip across the whole film and view it).

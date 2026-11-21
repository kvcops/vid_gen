# TEMPLATES.md — fill-in templates for every film (3D and 2D)

Agents: copy the block, fill every `<...>`, save under `<film>/story/` or `<film>/prompts/`. Do not invent new formats.

---

## 1. Story / style bible — `<film>/story/bible.yaml`
```yaml
title: "<title>"
logline: "<one sentence: who wants what, what stops them, the twist>"
track: 3d | 2d
style_preset: STYLIZED_3D | SEMI_REAL | TOON | FLAT_CARTOON | ANIME_CEL | STORYBOOK_PAINTED | PAPER_CUTOUT
tone: {comedy: 0.6, action: 0.3, emotion: 0.1}
audience: "<e.g. Indian YouTube (English/Telugu), 13+>"
languages:
  main: en                     # ISO code of dialogue + titles: en | te | hi | ta | kn | ml | bn | …
  extra: []                    # other versions to produce, e.g. [te] for an English + Telugu release
title_mode: single             # single | dual_stacked | dual_sequential | per_version  (TEMPLATES §13.3)
text:                          # every on-screen string, per language (never hard-code text in code)
  en: {title: "<English title>", subtitle: "<tagline>", to_be_continued: "To be continued...", disclaimer: "<fan-made fiction disclaimer>"}
  te: {title: "<Telugu title>", subtitle: "<...>", to_be_continued: "<...>", disclaimer: "<...>"}
palette: ["#<hex>", "#<hex>", "#<hex>", "#<hex>", "#<hex>", "#<hex>"]
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
Rules: a laugh or reveal every 20–30 s · every scene ends on a turn · callbacks to earlier jokes · max 2 lines per speech, ≤ 18 words each · stage directions in `action` beats, not in dialogue.

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
Line-level control: emotion tag + paralinguistic tag + pace; put pauses as "..." and commas; one emotion per line.

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

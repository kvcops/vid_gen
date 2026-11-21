# MASTER PROMPT v2 — Code-only 3D animated film pipeline
> Companion files: `AGENTS.md` (rules), `prompts/TEMPLATES.md` (all fill-in templates — prefer them over §5 below if they differ), `prompts/MASTER_PROMPT_2D_animation.md` (faster 2D alternative).
### Blender (render) + Kaggle GPU node (render + all AI audio/motion models) + predefined creative templates

> Paste everything below into Codex / OpenCode / Claude Code as ONE task. Fill only the `<<...>>` lines in §0.
> The user runs ONE Kaggle cell and pastes back `ENDPOINT` + `TOKEN`. Everything else is the agent's job.
> Model choices below were researched (Nov 2026: leaderboards, licences, VRAM, reviews). Re-check each model card's licence at use time.

> **Step 0:** load the ponytail skill first (`.agents/skills/ponytail/SKILL.md`, level full) and follow `AGENTS.md` §0 — minimal code and short replies, but never skip QA or requested features.

---

## 0. FILL THIS (the only creative input)
- **Story idea:** <<one paragraph: premise, twist, tone (comedy/action/drama), ending/cliffhanger>>
- **Languages:** <<main: en (default) | te | hi | …>> · optional extra versions: <<e.g. te>> · title mode: <<single | dual_stacked | dual_sequential | per_version>> (TEMPLATES §13.3)
- **Length / format:** <<e.g. 5–7 min, 16:9 1080p24>> · **Style preset:** <<STYLIZED_3D (default) | SEMI_REAL | TOON>>
- **Characters (names + one-line roles):** <<...>>
- **Commercial use (monetized channel)?** <<yes>> → only commercial-OK models allowed (all defaults below are).

## 1. NON-NEGOTIABLE RULES
1. **Blender only** for picture (latest 5.x, headless `bpy`, EEVEE; Cycles allowed for a few hero shots). **No** Remotion/three.js/Node/npm/puppeteer/web renderers, no AI text-to-video for story shots (identity drifts). AI video (Veo etc.) only for optional intro/outro/establishing plates.
2. **All GPU work on Kaggle** (free). Local Windows laptop (no CUDA) only edits code, sends jobs, downloads mp4/wav, does light ffmpeg/numpy mixing.
3. **ONE Kaggle cell** sets up everything, prints `ENDPOINT` + `TOKEN`, keeps running.
4. **Timeline-first:** script → voices → timeline from real durations → motion/animation → render → SFX/music → mix.
5. **Deterministic:** seeds from stable values (`zlib.crc32`), never Python `hash()` on strings (randomized per process → characters change between shots).
6. **Original characters only** (stylized; never real-actor likeness or names in any generation prompt).
7. **QA before every final render** (§10). Never claim quality you have not looked at.
8. Secrets in local `.env` (`HF_TOKEN`, `KAGGLE_URL`, `KAGGLE_TOKEN`, optional `SARVAM_KEY`); uploaded, never printed.

## 2. MODEL STACK (chosen; commercial-OK; fits a 16 GB Kaggle GPU)
| Job | Default model | Why | Fallback |
|---|---|---|---|
| **Voice design** (create each character's voice from a description) | **Maya1** (`maya-research/maya1`, Apache-2.0, 3B, English) | natural-language voice design + 20+ inline emotion tags (`<laugh> <sigh> <whisper> <angry> <giggle> <chuckle> <gasp> <cry>`…), very expressive | Chatterbox Turbo |
| **Dialogue acting (EN)** | **Step-Audio-EditX** (`stepfun-ai/Step-Audio-EditX`, Apache-2.0, 3B, ~12 GB) | highest-ranked commercial-OK open TTS in blind arenas; zero-shot clone + **emotion editing** (angry/happy/sad/excited/fearful/surprised/disgusted…) + **10 paralinguistic edits** (breath, laugh, sigh…), iterative refinement | Maya1 direct (tags inline) |
| **Fast / bulk lines** | **Chatterbox Turbo** (`ResembleAI/chatterbox-turbo`, MIT) | tags `[laugh] [chuckle] [sigh] [gasp] [groan] [sniff] [cough] [clear throat] [shush]`, `exaggeration` 0.5–0.9, `cfg_weight` 0.3–0.5 for dramatic pacing | — |
| **Telugu / other Indic (optional)** | **ZONOS3-Mini** (`Zyphra/ZONOS3-Mini`, Apache-2.0, 43 langs incl. Telugu/Hindi/Tamil, cloning + emotion/pace steering) | open + emotional + Indic | **Sarvam Bulbul v3 API** (best Telugu MOS in 2026 benchmarks; paid, ₹100 free credit) · IndicF5 (MIT) |
| **Foley from the rendered video** | **HunyuanVideo-Foley XL** (Tencent Hunyuan community licence; 16 GB, 8 GB with `--enable_offload`) | watches each rendered shot + text prompt → synced foley | **Foley-Omni** (MIT, 5.5B, 10 s/pass) |
| **Text-to-SFX & ambience beds** | **MOSS-SoundEffect v2** (Apache-2.0, 1.3B, 48 kHz, ≤30 s) | broadcast-quality SFX/ambience from text | Stable Audio Open 1.0 (community licence) |
| **Music (BGM, stingers)** | **ACE-Step 1.5** (MIT) instrumental mode | commercial-friendly, fast, modest GPU | user-supplied track (loop) |
| **Body motion from text** | **HY-Motion 1.0 Lite** (Tencent community licence, SMPL-H skeleton output) | "man stabs forward then staggers back" → natural mocap-like motion | Mixamo clips (free, manual download) · MoMask (MIT code) |
| **Body motion from video (optional)** | **mixamo-llm-mocap** pipeline (GVHMR → Mixamo-rig retarget in Blender, agent-operable) | act a scene on a phone → character animation | — |
| **Speech QA / timing** | faster-whisper large-v3 (MIT) | intelligibility check + word timestamps for lip-sync | — |
| ❌ Rejected (non-commercial or too big) | Fish S2 Pro (NC, 24 GB), Breeze TTS 2 (NC), IndexTTS2 (NC), MMAudio weights (CC-BY-NC), MusicGen (CC-BY-NC) | | |

**Precision:** P100 and T4 have **no bf16** → load every model in fp16 (or fp32 if unstable). P100 (sm_60): Kaggle's newest CUDA-13 torch may lack Pascal kernels → install a cu126 torch wheel inside the model env and assert `torch.zeros(1).cuda()` works.

## 3. KAGGLE NODE — `kaggle/node_cell.py` (ONE cell)
**3.1 Install:** detect GPUs (`nvidia-smi`); Blender 5.x Linux tarball (parse `download.blender.org/release/BlenderX.Y/`, newest patch); `apt-get install -y libegl1 libgl1 libxi6 libxkbcommon0 libsm6 libxrender1 libxxf86vm1 libxfixes3 ffmpeg fonts-noto-core libraqm0`; `pip install fastapi uvicorn python-multipart uv`; `cloudflared` binary.

**3.2 GPU EEVEE fix (CRITICAL; else EEVEE silently falls back to CPU, ~95 s/frame):** Kaggle ships CUDA libs but no NVIDIA EGL. `ver=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader)` → download `https://us.download.nvidia.com/tesla/$ver/NVIDIA-Linux-x86_64-$ver.run` (fallback XFree86 path) → `sh *.run -x --target nv` → copy only missing libs matching `EGL_nvidia|eglcore|glcore|glsi|tls|GLX_nvidia|gpucomp|glvkspirv|rtcore|nvoptix|ptxjitcompiler|allocator|cfg` into `/usr/lib/x86_64-linux-gnu/` (never overwrite CUDA/NVML) → write `/usr/share/glvnd/egl_vendor.d/10_nvidia.json` (`{"file_format_version":"1.0.0","ICD":{"library_path":"libEGL_nvidia.so.0"}}`) → symlink `.so.0` → `ldconfig` → export `__EGL_VENDOR_LIBRARY_FILENAMES` for all jobs → smoke test EEVEE 1080p (2nd frame < 2 s).

**3.3 Model envs (isolate!):** `python -m venv` fails on Kaggle (no ensurepip) → **`uv venv`** per family: `envs/tts_maya`, `envs/tts_step`, `envs/tts_chatterbox`, `envs/tts_zonos`, `envs/foley`, `envs/sfx`, `envs/music`, `envs/motion`, `envs/whisper`. Always `USE_JAX=0 USE_FLAX=0 USE_TF=0 USE_TORCH=1` (Kaggle's JAX import crashes older transformers). Pin each env to its repo's requirements; never share transformers/numpy/protobuf versions across envs. Each model runs as a small persistent worker (`node/workers/<name>.py`) with a JSON-in/WAV-out job queue so weights load once per session. `HF_TOKEN` for gated models (user clicks "Agree" once).

**3.4 GPU policy (auto):**
- **Blender EEVEE on Kaggle always renders on GPU 0** (NVIDIA EGL chooses it internally; `CUDA_VISIBLE_DEVICES`, Vulkan device prefs and LD_PRELOAD EGL shims were tested — none move it). Don't fight it.
- **T4 ×2:** GPU 0 = 2 concurrent Blender processes; GPU 1 = every CUDA model worker (`CUDA_VISIBLE_DEVICES=1` works for CUDA). **P100 ×1:** run audio/motion models first, unload, then render. Never run models during a final P100 render.

**3.5 API:** FastAPI :8000, header `X-Token`, Cloudflare quick tunnel. `GET /info` · `POST /upload` (tar.gz) · `POST /run {name,gpu,cmd}` · `GET /log/{job}?tail=` · `POST /kill/{job}` (process-group of THAT job only) · `GET /ls` · `GET /download` (dirs tar'd). Jobs `start_new_session=True`. **Never kill by guessed PID** (killed real renders before). Heartbeat loop; print `ENDPOINT : …` / `TOKEN : …`.

## 4. REPO LAYOUT
```
project/ .env  story/{bible.yaml, screenplay.yaml}  kaggle/node_cell.py
tools/  node.py (client)  audio_jobs.py  timeline.py  fit_dialogue.py  sfx_cues.py  mix.py  titles.py  sheet.py  shorts.py
node/   workers/{maya,step,chatterbox,zonos,foley,sfx,music,motion,whisper}.py  render_batch.py  qa_batch.py  assemble.py
blender/ run_shot.py  cams.py  shots/*.py
blender/lib/ core.py rig.py chars.py assets.py retarget.py acting.py sets.py envs.py fx.py shot.py
assets/ media/ audio/ out/
```
Reuse code from earlier films in `vid_gen/videos/` (e.g. `vid_gen/videos/devara/blender/lib/*.py` (characters, rig/IK, acting, sets), `vid_gen/videos/devara/tools/final_mix.py` (layered mix + ducking), `vid_gen/videos/devara/tools/fit_dialogue.py`. Put each new film in its own folder `vid_gen/videos/<film>/` (sub-layout in `AGENTS.md` §2); keep shared things (`kaggle/`, `tools/node.py`, `prompts/MASTER_PROMPT…`) at the root.

## 5. PREDEFINED CREATIVE TEMPLATES (fill these, don't invent formats)
### 5.1 Story bible (`story/bible.yaml`)
```yaml
logline: "<one sentence>"
tone: {comedy: 0.6, action: 0.3, emotion: 0.1}
style_preset: STYLIZED_3D
world: {era: "...", region: "...", palette: ["#b8341b","#f2b552","#0b1b2b"], recurring_motifs: ["red sea","lanterns"]}
locations:
  - id: storm_cliff   # every location = one envs.py builder
    time_of_day: night  weather: storm  key_light: "moon cool 6500K back-left"  practicals: ["lightning"]  ground: "flat ledge z=14.0"
continuity_rules: ["HERO always holds blade in RIGHT hand", "axis of action between HERO and VILLAIN on the boat = world X axis"]
```
### 5.2 Character card (one per character — the agent must fill EVERY field)
```yaml
id: HERO
archetype: mass_hero        # mass_hero | timid_son | villain | sidekick_comic | heroine_sassy | wise_elder | officer | mystery_twin | child | creature
body: {height_m: 1.86, build: 1.10, gender: male, age: 40, posture: "chest out, slow heavy steps"}
face: {head_scale: 1.0, jaw: 0.32, eyes: brown, kohl: true, brows: thick, nose: broad, ears: 1.0}
hair: {style: long_combed_back, color: "#121010", facial: full_beard + thick_mustache}
skin: "#5c3320"
costume: {top: "black shirt, sleeves rolled to elbow, open V", bottom: "dark checked lungi folded to knee", feet: sandals,
          accessories: ["silver kada right wrist", "black thread necklace"]}
signature_prop: {name: machete, hand: R, grip: fist}
silhouette_test: "long hair + beard + blade must read in pure black silhouette"
expressions_default: fierce     # from §5.5
walk_style: {stride: 0.82, bob: 0.02, arm_swing: 0.6, speed: 1.2}   # gait multipliers
voice: {engine: step|maya|chatterbox|zonos, design: "<see 5.3>", fx: "rubberband=pitch=0.94:formant=preserved,lowshelf=g=3:f=150"}
```
### 5.3 Voice casting presets (Maya1 voice-design descriptions; copy + adjust)
- **mass_hero:** "Deep, powerful, gravelly male voice in his forties, slow deliberate commanding delivery, heroic and intimidating, cinematic, close-mic, no background noise."
- **timid_son:** "Soft, gentle young man in his twenties, slightly nervous and polite, warm mid pitch, quick hesitant pacing."
- **villain:** "Rough, raspy, aggressive male voice, low pitch, loud and mocking, fast angry bursts, menacing laugh."
- **sidekick_comic:** "High-pitched excitable comic man, very fast chatter, squeaky when scared, cartoonish energy."
- **heroine_sassy:** "Bright confident young woman, sharp witty delivery, playful sarcasm, clear mid-high pitch."
- **wise_elder:** "Warm raspy elderly storyteller in his seventies, slow, knowing, gentle chuckles, grandfatherly."
- **officer:** "Firm clear middle-aged male officer, crisp formal diction, slightly impatient."
- **mystery_twin:** "Very deep, smooth, slow, menacing whisper-like male voice, calm and confident villainy."
- **narrator:** "Rich cinematic trailer narrator, slow dramatic pauses, deep and resonant."
Per line, the screenplay carries `emotion` (§5.5) + optional inline paralinguistics; the TTS adapter maps them: Maya1 `<laugh>`, Chatterbox `[laugh]`, Step-Audio-EditX emotion/paralinguistic edit calls (1–2 iterations), Zonos emotion steering.
### 5.4 Screenplay (`story/screenplay.yaml`)
```yaml
shots:
  - id: s07
    location: hut_night
    function: "audience learns the stab hit a dried fish"   # a shot is a story decision (no function → cut it)
    size: MCU            # §6.4 vocabulary
    beats:
      - wait: {sec: 1.2, tag: sip, action: "ELDER sips tea, eyes closed"}
      - say: {who: ELDER, text: "Ha ha ha...", emotion: amused, para: "<chuckle>"}
      - say: {who: ELDER, text: "...", emotion: wise, pace: slow, post: 0.5}
      - action: {who: OFFICER, motion: "leans back in shock", tag: shock}   # HY-Motion prompt or library pose
    sfx: ["tea slurp @sip", "glass on wood @sip+1.0"]
    music: {cue: hut_mystery, level: low}
```
### 5.5 Emotion → acting map (face + body + voice; use verbatim)
| emotion | brows / lids / mouth | body | voice |
|---|---|---|---|
| neutral | 0 / 1.0 / slight smile | idle breathing | calm |
| happy | up .25 / .85 / smile .85 | open chest, small bounce | bright, faster |
| laugh | up .4 / .45 / grin + open | head back, hand on belly, shoulders shake | `<laugh>` |
| angry | down, inner −1.0 / .78 / frown .7 | lean in, fists, point | loud, clipped |
| fierce | down −.7 / .72 / frown .3 | still, chin down, wide stance | low, slow |
| shocked | up 1.0 / 1.35 / O .6 | jump back 9 cm, hands up | gasp, high |
| scared | up, inner +.9 / 1.25 / frown .6 | shrink, shrug .6, step back | trembling |
| sad | inner up 1.0 / .7 / frown .6 | head down, slumped | soft, slow, `<sigh>` |
| smug | asym / .7 / half-smile | arms crossed, head tilt | slow, teasing |
| deadpan | flat / .55 / flat | no motion, slow blink | flat |
| wise | up .15 / .7 / smile .35 | slow nods, hands calm | warm, slow |
### 5.6 Camera presets (shot sizes → frame height & lens; eye height = ground + 0.92·H)
`ECU` 0.25 m/85 mm · `CU` 0.45/60 · `MCU` 0.7/50 · `MS` 1.1/40 · `MLS` 1.6/35 · `LS` 2.4/30 · `WS` 5+/24 · `ESTABLISHING` 24 mm high crane.
Rules: axis of action + 30° rule + screen direction + eyeline match; dialogue = establishing → two-shot → OTS → MCU/CU of speaker from the side they face (30–45° off axis) → reaction cut; **reaction-before-reveal** for big moments; low angle + slow push for hero beats; whip pans/fast dolly + handheld noise (0.01–0.03) for action; locked-off wide for comedy timing; hold 0.5–1 s after punchlines.
### 5.7 SFX cue template (`tools/sfx_cues.py`, generated from shot code)
`{shot, t, event, prompt, engine: foley|moss, gain_db}` — every lightning, impact, throw, landing, splash, footstep run, prop handling, door, cloth grab has a cue; ambience bed per location (`moss`, 20–30 s seamless loop prompt).
### 5.8 Music cue sheet
Per section: `{start, end, mood, tempo, instruments, intensity 0–1, sting_at[]}` → ACE-Step instrumental prompt "instrumental, no vocals, <genre>, <instruments>, <mood>, <tempo> BPM, cinematic film score, seamless loop" → stitch with 2–4 s equal-power crossfades.

## 6. BLENDER ENGINE
### 6.1 Render
EEVEE 1920×1080 24 fps, **16 TAA samples** final, AgX "Medium High Contrast", screen-space RT, fast GI, shadows, motion blur 0.45, compositor bloom (Glare). Presets `still` (1280×720/16), `preview` (960×540/8), `final`. Cycles + OptiX denoise only for flagged hero shots.
### 6.2 Characters — two modes (prefer ASSET)
- **ASSET mode (best quality):** base humans from **MPFB2** (free Blender add-on) or CC0 stylized packs (Quaternius/Kenney), or a user-provided Mixamo-rigged FBX. Build costume/hair/props per character card; standardize every rig to the canonical bone map (`hips, spine, chest, neck, head, shoulder/upperarm/forearm/hand.L/R, thigh/shin/foot.L/R` + fingers) via `assets.py`; face via shape keys (ARKit-style names) or the procedural face rig below.
- **PROCEDURAL mode (fallback, fully code):** skin-modifier bodies (Subdiv 3, auto weights), sculpted ellipsoid head (≈H/5.95), face rig (eyeballs + dim glint, blink lids with kohl band, tube brows, shape-key mouth open/wide/O/smile/frown/grin + teeth), combed clump hair (start embedded behind the hairline), **parametric beard patch** (no face-deletion jaggies; mouth sits on beard), costume material zones + trim tubes placed by **ray-cast from INSIDE the limb** (reject outliers), weighted skirts (hips→thighs above knee, thighs→shins below), hands open/fist variants (**build right hand, mirror only left**), flat-soled feet at z=0, wind displace on hair.
- Always: **animate child objects, never bone-parented pivots** (parent compensation lives in the pivot's basis — overwriting it flipped eyes into the skull).
### 6.3 Motion
- **Base motion:** HY-Motion text prompts per `action` beat (or Mixamo clips) → `retarget.py`: SMPL-H/Mixamo joint rotations → canonical rig (rest-pose alignment per bone, scale root translation by leg-length ratio) → **foot-lock post-pass** (detect contacts by low foot velocity+height, pin with analytic IK) → blend clips with 0.2–0.4 s crossfades.
- **Layered acting on top (lib/acting.py):** analytic 2-bone IK for legs/arms (poles, world/parent-space hand targets for touches, grabs, hugs), pose library for gestures, talk gestures keyed to speech envelope, look-at from **eye height** using the **current frame root transform** (not stale `matrix_world`), blinks 2.5–5 s, saccades, expression blending, **lip-sync from Whisper word timings + envelope** (visemes: closed/open/wide/O), props via `hold()` (bone / between-hands / detach to ballistic arcs).
- Gait fallback (procedural): heading **yaw = atan2(dx, −dy)** (sign error = moonwalk), planted feet, duty 0.62/0.38, heel-strike pitch, settle at end. Sitting: **root on floor**, hips to seat+7.5 cm. Characters on vehicles: parent armature to vehicle root; vehicles crossed between must bob identically.
### 6.4 Sets, physics, lighting
- Ground surfaces characters touch are **flat primitives at known heights**; displacement only outside walk zones; **apply scale before displacement**.
- **Physics:** Blender cloth for flags/sails/capes/loose costume tails (bake per shot, cache in `out/cache/<shot>`), rigid body for thrown/falling props (coconut, log, axe head), particles for rain/spray/embers/dust (`visible_shadow=False` on instanced particles), Ocean modifier + spray emitters for water.
- **Fog = finite volume box** (never a world Volume in EEVEE — it kills sun/moon light). Day: sky texture low strength + sun 4–5, exposure −1.4…−1.6. Night: gradient sky + stars + emissive moon, moon sun 2.2–2.6, big soft cool front fill so faces read, warm flickering practicals. Limit shadow-casting point lights (shadow pool overflow).
### 6.5 Titles, staging & timing
Blender text cannot shape complex scripts (Indic conjuncts, Arabic, etc. break): shape with **uharfbuzz + fontTools** -> glyph outlines -> Blender curves -> extrude/bevel/metal materials -> animate with one of the 10 title styles in `TEMPLATES.md` §13 — language-agnostic: text + fonts per language come from the bible and the font registry (§13.2), any script, bilingual modes (§13.3). Staging, object tracking, focus, orientation and timing rules: `TEMPLATES.md` §12 (mandatory for every shot).

## 7. AUDIO PIPELINE (on the node)
1. **Cast:** for each character, Maya1 designs 3 candidate voices from §5.3 → 6–8 s reference each → build `audio/casting_reel_<char>.wav` → **user picks** (ask once).
2. **Lines:** Step-Audio-EditX clones the picked reference, generates each line, then applies `emotion` + paralinguistic edits (≤2 iterations); short punch lines (< 12 chars) via Chatterbox Turbo. Respell English loan words in the target script for non-English lines.
3. **QA:** Whisper every line → reject if WER high, duration < 40 % / > 220 % of estimate, or clipped; regenerate with new seed (max 3).
4. **Post:** per-character ffmpeg FX, trim (40 ms pre / 80 ms post), 48 kHz mono.
5. **Timeline:** `tools/timeline.py` → `audio/timeline.json` (shots, frames, events with start/end/tag, per-frame envelope, word timings) + `audio/dialogue.wav`. Re-generated lines later → `fit_dialogue.py` (keep starts; tempo 0.85–1.35, pitch-preserving).
6. **Foley:** after picture renders, run HunyuanVideo-Foley on each shot clip with a prompt built from that shot's SFX cues; add MOSS spot effects for anything missed; ambience beds per location.
7. **Music:** ACE-Step cues from §5.8.
8. **Mix (`tools/mix.py`):** normalize first (beds RMS −30 dBFS, spot SFX peak −8 dBFS, music RMS −20 dBFS) → buses: dialogue 1.0, beds 0.35–0.55, SFX 0.5, music 0.24 **ducked to ~45 % under speech** (10 ms envelope, 50 ms attack/450 ms release; cumulative-sum smoothing, never full-length `np.convolve`) → `loudnorm=I=-15:TP=-1.5:LRA=11` → export stems + final. Assert per scene: beds ≥ 8 dB and music ≥ 6 dB under dialogue.

## 8. FAILURE CODES (check every QA image against these)
F1 face cropped/turned away while speaking · F2 eyes not on target / looking at sky · F3 foot sinking or floating > 2 cm · F4 seated character not on seat · F5 twisted/mirrored-wrong hand · F6 prop misaligned or floating · F7 identity drift between shots · F8 hair/cloth/skirt intersection · F9 camera inside geometry or wrong side of axis · F10 black/dark (world-volume bug) · F11 washed-out day · F12 character walking backwards · F13 lip-sync off > 2 frames · F14 sound missing for visible impact · F15 music masking dialogue.

## 9. RENDER
Build-only check all shots (`run_shot.py <id> still none`) → QA (§10) → final: workers balanced by frames×complexity, resumable per shot, log `shot n/N frames secs`; ~1–3 s/frame/process on T4. Assemble on the node (per-shot clips with fades → concat) and download only mp4s.

## 10. QA LOOP (mandatory)
1. 3 stills per shot (20/55/90 %) at `still` preset → 3-column contact sheets → inspect every image against §8 → fix → re-QA changed shots (expect 3–4 rounds).
2. Walk/run test on a grid floor (side tracking cam, 8 frames).
3. A 10-second sample clip with final audio for the user before the full render.

## 11. DELIVERABLES
`out/<film>_final.mp4` (1080p24, H.264 CRF 17, AAC 256k, −15 LUFS) · `out/<film>_silent.mp4` · `audio/stem_*.wav` · `audio/timeline.json` · 9:16 Shorts of the best gags (`tools/shorts.py`) · YouTube title/description/tags/chapters from the timeline · README (re-render a shot, regenerate a line, re-mix).

## 12. ACCEPTANCE
No §8 failure codes in final QA; identical character identity in every shot; every line clear and emotional (Whisper QA passed, not robotic); every visible impact has a sound within ±2 frames; music never masks dialogue; the user ran only ONE Kaggle cell.

## 13. WORKING WITH THE USER
Simple English. Ask only for: Kaggle ENDPOINT + TOKEN; HF token + "Agree" on gated models; voice pick from casting reels. Show contact sheets and a 10 s sample early. Never stop a running render unasked; give honest ETAs (frames left × measured s/frame).

### Reference sources used for this spec
Artificial Analysis open-weights TTS arena; Step-Audio-EditX, Maya1, Chatterbox, ZONOS3-Mini, HunyuanVideo-Foley, Foley-Omni, MOSS-SoundEffect, ACE-Step, HY-Motion model cards; Indic TTS Benchmark 2026; DirectorSKILL / scene-director (shot-list & continuity schemas); mixamo-llm-mocap (video→Mixamo retarget).

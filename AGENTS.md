# AGENTS.md — vid_gen (code-only animated film studio)

This file is read automatically by **Codex** and **OpenCode** (and imported by `CLAUDE.md` for Claude Code).
It is the single source of truth for how to work in this repo. Read it fully before doing anything.

---

## 0. LOAD FIRST — token-saving skill "ponytail" (mandatory, before any other step)
Every agent (Claude Code, Codex, OpenCode, others) must load and follow the **ponytail** skill at level **full** for the whole session:
1. **Use the vendored copy (always available):** read `.agents/skills/ponytail/SKILL.md` (identical copy in `.claude/skills/ponytail/SKILL.md`) and follow it.
2. Optional plugin install (adds `/ponytail lite|full|ultra` and per-turn injection):
   - Claude Code: `/plugin marketplace add DietrichGebert/ponytail` then `/plugin install ponytail@ponytail` (two separate prompts)
   - Codex: `codex plugin marketplace add DietrichGebert/ponytail` · `codex plugin add ponytail@ponytail` · trust its hooks in `/hooks`
   - OpenCode: `opencode plugin add @dietrichgebert/ponytail` (or `{ "plugins": ["@dietrichgebert/ponytail"] }` in `opencode.json`)
3. If the vendored file is missing and plugins can't be installed: `curl -sL https://raw.githubusercontent.com/DietrichGebert/ponytail/main/skills/ponytail/SKILL.md -o .agents/skills/ponytail/SKILL.md` (or `git clone --depth 1 https://github.com/DietrichGebert/ponytail`) and read it.
**Scope of ponytail here:** it governs *how much code/text you write* (smallest complete change, reuse existing code in this repo, no unrequested abstractions, short replies). It never overrides this file: the QA loop, the golden rules, film quality, and every feature the user or a master prompt asks for are "asked for" and must be done fully.

## 0.1 HOW THE USER WORKS — one-line requests (auto-routing)
The user will NOT paste prompts. They type things like *"make a video about a lazy lion king, shorts, 50 s"*, *"long funny 3D video on Devara 2 part 2 in Telugu"*, *"2D explainer on black holes, 3 min"*.
On ANY request to make/generate/create/animate a video, short, reel, episode, film or cartoon:
1. Load ponytail (§0) → this file → the **make-video** skill (`.agents/skills/make-video/SKILL.md`, same in `.claude/skills/make-video/`).
2. Follow it: parse the brief with its defaults (format long 16:9 / shorts 9:16, duration, 2D/3D, language — English unless named), auto-load the right master prompt + `prompts/TEMPLATES.md`, create `vid_gen/videos/<slug>/`, do the single checkpoint (outline + Kaggle ENDPOINT/TOKEN), then build to the final mp4 without further questions.

## 1. What this repo is
A studio that turns a story idea into a **finished animated film** (YouTube-ready, 16:9 1080p24, optional 9:16 Shorts) using **only code**:
- **3D track:** Blender (EEVEE) procedural/asset characters, rigs, acting, sets, cameras → `prompts/MASTER_PROMPT_animation_pipeline.md`
- **2D track:** procedural **vector** characters (bezier paths, no image models) rigged and animated by code, rendered with skia-python (CPU) → `prompts/MASTER_PROMPT_2D_animation.md`
- **All GPU work runs on a free Kaggle node** (one notebook cell: `kaggle/render_node.py`). The local machine is a weak Windows laptop (no CUDA): it edits code, sends jobs, downloads results, mixes audio.

## 2. Layout
```
vid_gen/
  AGENTS.md  CLAUDE.md  README.md  .env          # .env = secrets (never print/commit)
  kaggle/render_node.py                         # the ONE Kaggle cell (GPU T4 x2 · Internet ON)
  prompts/
    MASTER_PROMPT_animation_pipeline.md         # 3D track spec
    MASTER_PROMPT_2D_animation.md               # 2D track spec
    TEMPLATES.md                                # shared templates: bibles, character cards, vector design spec, shots, emotions, voices, camera, staging/timing (§12), titles & fonts (§13), SFX, music, YouTube
  tools/node.py  tools/sheet.py                 # Kaggle client · QA contact sheets (shared by all films)
  videos/                                       # every film we make (git-ignored, stays local)
    <film>/                                     # one folder per film, same sub-layout:
      story/ blender/ (or anim2d/) tools/ audio/ assets/ media/ out/ prompts/ README.md
    devara/                                     # film #1 (3D) — reuse its code for new 3D films
```
**New film = new folder** `vid_gen/videos/<film_slug>/`. Never put film-specific files at the root. `videos/` is local only (git-ignored). Reuse code from earlier films in `videos/` (e.g. `videos/devara/blender/lib/`; copy, then adapt).

## 3. Golden rules (non-negotiable)
1. **Picture = Blender (3D or 2.5D) or the pure-Python 2D renderer.** No Remotion / three.js / Node / npm / puppeteer / web renderers. No AI text-to-video for story shots (identity drifts). AI video (Veo etc.) only for optional intro/outro/establishing plates the user supplies.
2. **GPU work only on Kaggle.** Never assume a local GPU.
3. **Timeline-first:** script → voices → `audio/timeline.json` from real durations → animation → render → foley/SFX/music → mix.
4. **Deterministic:** seed with `zlib.crc32(...)`, never Python `hash()` on strings (randomized per process ⇒ characters change between shots).
5. **Original characters only.** Stylized caricatures allowed; never real-person likeness, never real actor names in generation prompts. Add a "fan-made, fictional" disclaimer for parody content.
6. **Commercial-OK models only** (user runs a monetized channel). Check the licence on the model card before adding any model.
7. **QA before every final render** (§7). Look at the images yourself. Never claim quality you have not seen.
8. **Never kill processes by guessed PID.** Only stop a job via `POST /kill/<job>` (process-group of that job). Never stop a running render unless the user asks.
9. **Secrets** live in `.env` (`HF_TOKEN`, `KAGGLE_URL`, `KAGGLE_TOKEN`, `ELEVEN_KEY`, …). Read them; never echo them.
10. **Staging/timing/focus/orientation rules** (`prompts/TEMPLATES.md` §12) and **title/intro/outro rules** (§13) are mandatory for every shot and every film.
11. **No image-generation models** for characters, sets or animation — vector or 3D geometry only. Raster only for user-made thumbnails.
12. **Language-agnostic:** never hard-code a language. Dialogue, titles, cards, disclaimers, fonts and voices come from `bible.yaml` (`languages`, `text.<lang>`, font registry TEMPLATES §13.2). Films may be English, Telugu, Hindi… or several versions.
13. **Ask the user only for:** Kaggle ENDPOINT + TOKEN, HF token / "Agree" on gated models, voice pick from casting reels, creative approval of the script. Decide everything else yourself.

## 4. Kaggle node workflow
1. User runs `kaggle/render_node.py` in one Kaggle cell (Accelerator **GPU T4 x2**, Internet ON) and pastes `ENDPOINT` + `TOKEN` — usually together with the video request — → write them to `.env` as `KAGGLE_URL` / `KAGGLE_TOKEN`, verify with `tools/node.py info`. The link changes every Kaggle session; if `info` fails, ask for fresh lines.
2. `python tools/node.py info` (GPUs, disk, jobs, model install states) · `push <film_dir> [extra files]` · `run <name> <gpu> "<cmd>"` · `log <name> [tail]` · `kill <name>` · `ls <path>` · `get <remote> <local>`.
3. GPU policy: **Blender EEVEE always renders on GPU 0** on Kaggle (EGL picks it; don't try to move it). On T4 x2 run AI models on **GPU 1** (`CUDA_VISIBLE_DEVICES=1` works for CUDA). On a single GPU run models before rendering.
4. Model envs live in `/kaggle/working/envs/<name>` (uv venvs). Run a model with `$ENVS/<name>/bin/python ...`. Check `GET /models` for `ready` / `FAILED`; retry one with `POST /models/install/<name>`.
5. Download only final mp4/wav (assemble clips on the node). Never pull thousands of frames.

## 5. Model stack (commercial-OK, fits 16 GB; details in the master prompts)
- **Voices:** Maya1 (voice design + emotion tags) → Step-Audio-EditX (clone + emotion/paralinguistic editing) · Chatterbox Turbo (fast, tags) · ZONOS3-Mini (43 langs incl. Telugu) · optional ElevenLabs v4 / Sarvam Bulbul v3 APIs if the user provides keys. faster-whisper for QA + word timings.
- **Sound:** HunyuanVideo-Foley (foley from rendered clips) · MOSS-SoundEffect v2 (text-to-SFX, ambience) · ACE-Step 1.5 (music).
- **Motion (3D):** HY-Motion 1.0 Lite (text→motion), Mixamo clips, mixamo-llm-mocap (video→motion).
- **2D:** no image-generation models (raster = heavy, blurry, inconsistent, un-riggable). Vector characters by code (skia-python), optional user SVGs; Rhubarb Lip Sync (visemes, CPU). Titles: uharfbuzz + fontTools glyph outlines (TEMPLATES §13).
- **Rejected (non-commercial or too big):** Fish S2 Pro, Breeze TTS 2, IndexTTS2, MMAudio weights, MusicGen, FLUX.1/.2 [dev].
- P100/T4: **no bf16** → fp16 (or fp32).

## 6. Hard-won engineering lessons (do not repeat these bugs)
| Symptom | Cause → fix |
|---|---|
| EEVEE 95 s/frame, `EGL Error` | Kaggle lacks NVIDIA EGL libs → render_node installs them from the matching driver `.run` |
| All outdoor shots black | World **Volume** in EEVEE kills sun/moon → use a finite fog **box** |
| Character walks backwards | heading yaw must be `atan2(dx, -dy)` (character faces −Y) |
| Seated characters float | root on the **floor**, lower hips to seat + 7.5 cm |
| Right hand twisted | build canonical right hand, **mirror only the left** |
| Eyes inside the skull | bone-parented pivots hold a compensation rotation → animate **child** objects |
| Heads look at the sky / wrong way | look-at must use the **current frame's root transform** and **eye height** (not stale `matrix_world`, not the neck) |
| Cliff became 25 m spikes | **apply object scale before displacement** |
| Collar bar / sleeve spikes | ray-cast trims from **inside** the limb, reject outlier radii |
| Beard stair-steps | parametric beard patch, not face deletion |
| Characters differ between shots | Python `hash()` randomness → `zlib.crc32` seeds |
| "Shadow buffer full" | instanced particles `visible_shadow=False`; limit shadowed point lights |
| Mix took > 10 min | never `np.convolve` a full 48 kHz track — cumulative-sum moving average |
| BGM/SFX drown dialogue | normalize every SFX/bed first, duck music under speech, loudnorm −15 LUFS |
| Telugu sounded wrong ("Devar") | never fake a language via another script; use a native TTS |
| Killed real renders | never kill by PID; use `/kill/<job>` |
| Model install conflicts | one uv env per model; `USE_JAX=0 USE_TF=0`; no shared transformers/numpy pins |

## 7. QA checklist (every shot, before the final render)
3 stills per shot (20/55/90 %) → contact sheet (`tools/sheet.py`) → check: face visible & not cropped while speaking · eyes on target · feet on ground/deck (±2 cm) · seated on seat · hands not twisted · props in hand & oriented · no intersections · camera on correct side of the axis · exposure (not black / not washed out) · 2D: no tearing between parts, mouth on the face, lines consistent. Fix → re-QA changed shots → repeat. Then a **10-second sample with final audio** for the user before the full render.

## 8. Commands cheat-sheet
```bash
python tools/node.py info
python tools/node.py push videos/<film> audio/dialogue.wav           # upload a film folder
python tools/node.py run qa0 0 "python3 blender/qa_batch.py 0"   # jobs run inside the uploaded film folder
python tools/node.py log qa0 40
python tools/node.py get out/<film>_silent.mp4 videos/<film>/out/<film>_silent.mp4
blender -b --factory-startup --python videos/<film>/blender/run_shot.py -- s05 still none   # local build-only check
python videos/<film>/tools/final_mix.py                                 # final audio + picture assembly
```

## 9. How to talk to the user
Very simple English, short sentences. Show progress with contact sheets and short samples. Give honest time estimates (frames left × measured s/frame). Admit mistakes plainly and fix them.

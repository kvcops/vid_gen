---
name: make-video
description: >
  One-line video requests → full pipeline. Use whenever the user asks to make / generate / create / animate a video,
  short, reel, episode, film, cartoon or story (e.g. "make a video about X", "shorts on Y 45s", "long video, 6 min,
  Telugu, 3D"). Loads the repo rules, picks format/track/language defaults, creates the film folder and builds the
  film end-to-end on the Kaggle node. The user never pastes prompts.
argument-hint: "<topic> [shorts|long] [duration] [2d|3d] [language]"
---

# make-video — from one line to a finished film

The user gives only: **topic** (+ optional **format**, **duration**, **2D/3D**, **language**, **style**, **characters**). You do everything else.

## Step 0 — load (automatically, in this order, no user action)
1. `.agents/skills/ponytail/SKILL.md` (level full) — scope limits in `AGENTS.md` §0.
2. `AGENTS.md` (rules, layout, model stack, lessons, QA).
3. The track spec: `prompts/MASTER_PROMPT_animation_pipeline.md` (3D) **or** `prompts/MASTER_PROMPT_2D_animation.md` (2D).
4. `prompts/TEMPLATES.md` (every format you fill).
Treat the chosen master prompt as if the user had pasted it, with its §0 filled from the brief below.

## Step 0.5 — Kaggle connection (first thing)
- If the user's message contains `ENDPOINT : https://….trycloudflare.com` and `TOKEN : …`, write them to `.env` as `KAGGLE_URL=` / `KAGGLE_TOKEN=` (replace old values) and verify with `python tools/node.py info`.
- If missing or `info` fails (links change every Kaggle session): tell the user in one line — "run `kaggle/render_node.py` in one Kaggle cell (GPU T4 x2, Internet ON) and paste the ENDPOINT + TOKEN lines" — and include it in the Step 3 checkpoint message. Writing the script/voices can proceed meanwhile; rendering waits for the link.

## Step 1 — parse the brief → `videos/<slug>/story/brief.yaml`
| field | if the user didn't say |
|---|---|
| format | **long** (16:9 1920×1080) unless the request says short/shorts/reel/vertical → **shorts** (9:16 1080×1920) |
| duration | long: **5–7 min** · shorts: **45–60 s** (hard max 3 min) |
| track | user's choice wins. Else: **shorts → 2D vector** (fast, punchy), **long story/drama/action → 3D**, explainer/comedy sketch → 2D |
| language | **English**; any language named ("in Telugu", "Hindi version") → `languages.main` (+ `extra` for multi-version) |
| tone/style | **adult audience** — primary + secondary tone from the topic (dark humour, satire, suspense, action, tragedy, rage, fear…; TEMPLATES §16.2); **never default to light/kid-friendly**; new palette that differs from every earlier film (§16.3) |
| captions | **off** (user preference) unless asked |
| title mode | `single` (bilingual only if two languages requested) |
| parody of real IP | original caricatures only + fan-made disclaimer (`AGENTS.md` rule 5) |
Film slug: lowercase-kebab of the topic (`vid_gen/videos/<slug>/`, same sub-layout as `AGENTS.md` §2).

## Step 2 — format rules
- **Long (16:9):** TEMPLATES §2 story structure, intro title (§13) + outro/end card 10–20 s with YouTube end-screen space, chapters for the description.
- **Shorts (9:16, 1080×1920):** hook in the **first 1–2 s** (motion + line), one idea, a twist/payoff at 70–85 %, loopable last frame (ends where it began), no long intro — 1 s logo sting max, title as a 1–2 s overlay, end with a 1–2 s button. Compose for vertical: characters centered, MCU/CU-heavy, title-safe 80 %, keep the bottom 20 % and right 15 % clear (platform UI). Faster pacing: shots 0.8–2.5 s.
- **Both:** timing/staging/focus rules (TEMPLATES §12) and language-agnostic titles (§13) are mandatory.
- **Engagement (TEMPLATES §14) — hard minimums, never one closed set:** long 5–7 min ≥ 8 locations, ≥ 50 % exterior, ≤ 60 s in one place, ≥ 2 set pieces, ≥ 3 lighting looks; Shorts ≥ 3 backdrops. Something new on screen every ≤ 5 s, re-hook every 30–45 s, characters move through space. Run the §14.5 self-check on the outline and on the timeline; fix failures before rendering.
- **Quality bar (TEMPLATES §16):** stay on the user's topic (every scene and every line has a job), adult tones with real stakes, fresh palette, clean backgrounds, only purposeful props, no filler walks/holds, believable grip/throw/catch/release, camera with intent, clean mix where music follows emotion. Run the §16.9 audit before rendering.
- **Voice acting (TEMPLATES §15):** every line gets emotion, intensity, pace, volume, pauses, emphasis, nonverbals; vary pace between lines; use the chosen TTS model's own controls (§15.3); voice QA §15.5.

## Step 3 — Gate A: checkpoint with the user (STOP and wait for approval)
**Read `prompts/TEMPLATES.md` §17 first.** Send the **full script (every line, with speaker)**, the hostile-review result (§17.2), the voice casting table (character, gender, engine, voice id, measured F0 — §17.1) and: logline · 6–10 beat outline · **premise + promise, tones, palette (hex), location list + scene table with the §14.5 and §16.9 check results** · cast (names + one-line looks + voice presets) · track/format/duration/language chosen · and, only if Step 0.5 found no live link, ask for the **Kaggle ENDPOINT + TOKEN**. Do not generate all voices, art or renders until the user approves the script and cast. Apply requested changes and re-send only the diffs.

## Step 4 — build (Gate B before the full render)
**Gate B:** once characters and sets exist, render a 10–15 s sample (hardest scene) with final voices and music and **wait for the user's approval** before the full render. View a 2–3 fps strip of the whole film yourself first (§17.4).
Models: core set is preinstalled; `python tools/node.py install <name>` the extra models this film needs (one or two at a time), `remove` them when their step is done (Kaggle disk cap, `AGENTS.md` §4).
script → voices (casting reel mandatory; one real voice per character, correct gender, F0 gate; never pitch-shift one voice into a cast) → timeline → characters/sets → shots → build-only check → QA stills (3 per shot) → fix → 10-second sample with audio (share it) → final render → foley/SFX/music → mix (−15 LUFS) → `videos/<slug>/out/<slug>_final.mp4` (+ `_silent.mp4`, stems) → YouTube package (title/description/tags/chapters or Shorts caption + hashtags).

## Step 5 — report
Final file paths, duration, what was skipped or not checked (ponytail rule), and an honest note on any known flaw.

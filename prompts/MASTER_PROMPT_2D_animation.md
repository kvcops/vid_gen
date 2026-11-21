# MASTER PROMPT — 2D VECTOR animated film pipeline (procedural vector characters, code-animated)

> Paste into Codex / OpenCode / Claude Code as ONE task (they also read `AGENTS.md`). Fill §0 only. Templates: `prompts/TEMPLATES.md`.
> **No image-generation models.** Raster images are heavy, blurry when scaled, inconsistent between generations and cannot be
> rigged cleanly. Every character, prop, background and effect here is **vector geometry built by code** (bezier paths, shapes,
> gradients) → crisp at any resolution, tiny, deterministic, and already split into rig parts.
> Reference designs proving this works: **AnimDSL** (full 2D films from code: procedural bezier characters, 23 pose parameters,
> front/¾/profile/back body angles, walk cycles with staggered joints, damped-spring hair/cloth, camera + transitions) and
> **Rigby2D** (open-source 2D skeletal animator: auto-rig layered SVG, IK, mesh bending, physics, lip-sync, video render).

> **Quality bar:** `TEMPLATES.md` §16 is mandatory — adult audience, on-topic purposeful dialogue, wide emotional range, a new palette per film, clean backgrounds, no useless props, no filler, real object handling, intentional camera, clean mix. Audit §16.9 before rendering.

> **Engagement + voice acting:** follow `TEMPLATES.md` §14 (many locations, mostly exterior, fast cadence, re-hooks — never one closed set) and §15 (per-line emotion/pace/pauses, per-model TTS controls). Run the §14.5 self-check before rendering.

> **Hard rules (TEMPLATES §17):** per-character real voices of the right gender with F0 QA · tone from the topic (no kids' comedy on dark topics) · consequence-driven script approved by the user first · shots must read and characters must act · polygon/capsule figures are not final art · Gate A (script + cast) and Gate B (10 s sample) before the full render.

> **Step 0:** load the ponytail skill first (`.agents/skills/ponytail/SKILL.md`, level full) and follow `AGENTS.md` §0 — minimal code and short replies, but never skip QA or requested features.

## 0. FILL THIS
- Story idea: <<...>> · Languages: <<main: en (default) | te | hi | …; extra versions>> · Length: <<5–7 min 16:9 + Shorts>>
- **Tone:** <<primary + secondary, adult (dark humour / suspense / action / tragedy …) — never default cute>> · **Palette:** <<5–7 hex + accent, chosen from tone, different from previous films>>
- **Vector style:** <<FLAT_CARTOON (bold outlines, flat fills, 1 cel shadow) | THIN_LINE_PASTEL | NO_OUTLINE_SHAPES (Kurzgesagt-like) | PAPER_CUTOUT (texture + drop shadow) | NOIR_SILHOUETTE>>
- Characters: <<names + one-line roles>> · Commercial use: <<yes>>

## 1. WHY 2D VECTOR
- Renders at ~30–120 frames/s per CPU core at 1080p (no GPU needed; Kaggle CPU or your laptop) — minutes instead of hours.
- Zero 3D failure modes (feet sinking, twisted hands, cloth intersections). Perfect identity in every shot. Easy comedy timing.
- Limits: no free 3D camera orbits → use body-angle views, parallax and cuts.

## 2. STACK
| Job | Tool |
|---|---|
| Vector drawing + rendering | **skia-python** (Skia: anti-aliased paths, gradients, blur, masks, blend modes) → raw RGBA frames → ffmpeg pipe. Fallback: pycairo. |
| Optional 2.5D lighting/particles | Blender: import exported SVG parts as curves (or Grease Pencil v3) on planes, orthographic camera, EEVEE 0–4 samples |
| Optional hand-made art | SVG files from Inkscape/Illustrator with layer ids following §4 naming → auto-rigged (Rigby2D-style) |
| Lip-sync | **Rhubarb Lip Sync** (MIT, CPU, `-r phonetic` works for any language) → shapes A–H, X |
| Word timing / emphasis | faster-whisper word timestamps |
| Voices / SFX / music / mix | music changes per scene emotion, ducked 8–12 dB under speech, silence before shocks (TEMPLATES §16.8); same tools as 3D track (`MASTER_PROMPT_animation_pipeline.md` §2, §7) |
| Text / titles | uharfbuzz + fontTools → glyph outlines as vector paths (any language/script: Latin, Indic, Arabic…; fonts per script from TEMPLATES §13.2) — see TEMPLATES §13 |

## 3. CHARACTER CONSTRUCTION (procedural vector)
Each character is a **parametric spec** (TEMPLATES §8) compiled into vector parts:
- **Head:** superellipse/egg with jaw taper, cheek bulge; ears; nose (5 types); eyes = white + iris + pupil + highlight + lids (open/half/closed/happy-arc/angry-slant); brows (thickness, arch, angle per expression); mouth = **9 parametric viseme paths** (A–H, X) morphable with smile/frown amount; teeth/tongue fills; beard/mustache/stubble shapes; hair from a style library (spiky, combed-back, long wavy, curly cloud, bun, braid, bald-ring) built as layered bezier clumps with highlight strokes.
- **Body:** torso shape by build (slim/average/heroic/round), neck; limbs as **tapered bezier capsules** joined with round caps (no gaps at any angle), hands from a small set (open, fist, point, thumbs-up, holding) per side, feet/shoes; clothing as shapes clipped to body regions (shirt, lungi/skirt with hem line, saree pallu, vest, coat), accessories (bangles, chains, glasses, caps, headbands).
- **Style pass:** outline (stroke weight scales with distance-from-camera), flat fill, 1 cel shadow (offset path clipped, multiply), optional rim light stroke, optional paper texture.
- **Body angle (turns):** parameter `yaw ∈ {front, ¾-left, profile-left, back, ¾-right, profile-right}` (+ smooth blend between neighbours by shifting facial features along the head's horizontal arc and swapping limb draw order). Turning = 2–3 frames with a slight squash.
- **Draw order (z):** back arm/leg → torso → front leg → head → front arm; swap sides for mirrored yaw.
- **Silhouette test:** render solid black; each character must be recognizable.

## 4. RIG + NAMING (shared by procedural and SVG characters)
Bones: `root, hips, chest, neck, head, upperarm_L/R, forearm_L/R, hand_L/R, thigh_L/R, shin_L/R, foot_L/R` + face controls `brow_L/R, eye_L/R, lid_L/R, mouth, jaw`.
**Pose parameters (degrees / 0–1):** `torso_bend, torso_twist, head_tilt, head_turn, head_nod, arm_L_angle, arm_R_angle, elbow_L_bend, elbow_R_bend, wrist_L, wrist_R, hand_L_shape, hand_R_shape, hip_shift, leg_L_angle, leg_R_angle, knee_L_bend, knee_R_bend, foot_L, foot_R, brow_raise, brow_angle, lid_open, mouth_smile, mouth_viseme, eye_look_x, eye_look_y, squash_stretch, yaw`.
2-bone IK for planted feet and hand contacts (grab, shoulder touch, hug). SVG layer ids must match bone names (`head`, `upperarm_L`…) for auto-rigging.

## 5. ANIMATION ENGINE
- Pose library (≥ 25 named poses) + emotion map (TEMPLATES §5) + text→pose mapping for `action` beats.
- **Principles, codified:** ease in/out on every key, anticipation 3–8 frames opposite direction, follow-through & overlap (hair/cloth/tails/ears = damped springs, k≈120, damping≈12, lag 2–4 frames), squash & stretch ≤ 15 % keeping area, arcs for hands/heads, holds after punchlines, **smear frames** + speed lines on fast moves, **impact frames** (1–2 frames flat inverted colour), **animate on twos** (12 drawings/s) for characters, camera/FX on ones.
- **Walk/run cycles:** 8 / 6 keys per cycle, staggered joints (hips lead, shoulders counter-rotate, head bob), root speed = stride / cycle time (feet never slide), contact frames get dust puffs on runs.
- **Talking:** Rhubarb visemes on exact time codes (hold ≥ 2 frames, blend 1 frame), blinks every 2.5–5 s (4-frame blink), brow/head accents on stressed words (Whisper timings), breathing squash ±1 %.
- **Staging, tracking, focus, orientation, timing:** follow TEMPLATES §12 exactly.
- **Backgrounds (quiet, purposeful):** lower contrast/saturation and fewer details than characters, no busy patterns behind faces, only props that matter (§16.4), correct scale; vector parallax layers (sky gradient, far silhouettes, mid set, near props, foreground framing elements), 1.5–2× frame width for pans, atmospheric perspective (far layers lighter/bluer, lower contrast), time-of-day palettes.
- **FX (vector):** dust puffs, impact stars, sweat drops, anger veins, sparkles, speed lines, motion trails, rain, splashes, smoke, embers — procedural particle systems drawing paths.
- **Camera 2D:** virtual camera (x, y, zoom, rotation) with damped follow, lead room, shake (Perlin, decaying), push-ins, whip pans with directional blur, split screens, iris/wipe transitions.

## 6. SHOT FORMAT
`TEMPLATES.md` §4 screenplay with 2D fields: `view` (yaw per character), `layout` (x %, ground y %, scale), `bg`, `camera {start, end, ease, shake, follow}`, `fx`, `focus` (which character/prop holds attention).

## 7. RENDER
Render per shot in parallel CPU processes (`multiprocessing`, one per core) → raw frames piped to ffmpeg (yuv420p, CRF 16). Motion blur: 3-sample temporal accumulation on fast parts only. Output 1920×1080 + a 1080×1920 Shorts re-layout pass.

## 8. QA (plus `AGENTS.md` §7)
Joint gaps/tears at extreme angles · stroke weight consistency · mouth/eyes stay inside the head at all yaws · ground contact (shadow ellipse under each character on the ground line) · screen direction & eyelines (§12) · camera lead room · no identity drift · text legibility.

## 9. DELIVERABLES
Final mp4 (1080p24, −15 LUFS), silent master, stems, timeline, Shorts, title/intro/outro (TEMPLATES §13), YouTube package.

### Sources
AnimDSL (procedural 2D films from code, tiny-skia) · Rigby2D (open 2D skeletal animator, SVG auto-rig, IK, physics, lip-sync) · Pose Animator (skeleton-driven SVG paths) · cartoonimator / cutan (code-animated cut-out, Rhubarb visemes) · Rhubarb Lip Sync.

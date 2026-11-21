# దేవర 2 — భాగం 1 : "ఎండు చేప రహస్యం" (fan-made comedy animation)

A fictional, non-commercial fan parody, made for entertainment only. The characters are stylized caricatures inspired by costumes and silhouettes, not likenesses.

## Story (≈ 5.6 min, 35 shots, all-Telugu dialogue, no captions)
Prologue in a red storm → title → 1996: Singappa tells the DSP the "real" ending of Part 1. Vara's knife hit a **2 kg dried fish** in Devara's pocket, and the death was staged. Devara retired to an island with his pet shark **Sundaram** (and is at war with coconuts). In the village, Bhaira still hunts Devara; Kunjara brings him a "Part 2 poster". Thangam finds Vara's **Devara wig**. Night-sea showdown: Vara's wig flies off when he sneezes, Devara bursts out of the sea riding Sundaram, and the "Google Maps" reveal follows. Cliffhanger: **Yethi** arrives with Devara's face, a long-lost brother from a village fair. Outro: "సముద్రం అబద్ధం చెప్పదు… కానీ నేను చెప్తా."

## Outputs
| file | what |
|---|---|
| `out/devara2_part1_final.mp4` | **final film** — Veo intro/outro with Telugu titles, ElevenLabs Telugu dialogue, ambience + 65 SFX, ducked BGM (5:46, 1080p24) |
| `out/devara2_part1_silent.mp4` | animation-only picture (no intro/outro, no audio) — input for re-mixing |
| `audio/dialogue.wav`, `audio/stem_*.wav`, `audio/final_mix.wav` | dialogue / sfx+ambience / bgm / veo stems and the final mix |
| `audio/timeline.json` | exact shot + line timings |
| `media/` | Veo intro/outro clips and the BGM track |
| `prompts/` | Gemini/Veo/thumbnail/YouTube prompts and **MASTER_PROMPT_animation_pipeline.md** (rebuild this pipeline for any new story) |

Re-mix after changing levels/SFX: `python tools/final_mix.py` (SFX library: `tools/gen_sfx.py`, ElevenLabs dialogue: `tools/el.py` + `tools/fit_dialogue.py raw_el dialogue_el`).

## Pipeline
1. `story/script.py`: the screenplay (Telugu), cast to HeyGen voices, and timing beats.
2. `tools/gen_audio.py`: HeyGen `heygen-voice-1-turbo-free`. Telugu is not a supported language in HeyGen, so the Telugu script is transliterated letter by letter into Devanagari (`tools/translit.py`) and spoken with `language=hi`. Whisper transcription confirmed the output is intelligible Telugu. The script also trims silence, extracts lip-sync envelopes, and builds the timeline and dialogue mix.
3. `blender/`: everything is procedural in Blender 5.3 (EEVEE).
   - `lib/chars.py`: characters (skin-modifier bodies, parametric faces/beards/hair, costumes, hands with open/fist states)
   - `lib/rig.py`: armature with **analytic IK solved in Python**, so feet land exactly on the ground or deck
   - `lib/acting.py`: pose library, walk/run with planted feet, look-at, blinks, expressions, audio lip-sync, props
   - `lib/sets.py`, `lib/envs.py`: ocean, storm, hut, rocks, island, village, night sea, ship
   - `shots_a/b/c.py` + `cams.py`: the 35 shots and their cameras
4. `kaggle/render_node.py`: a one-cell Kaggle render node (2× T4, GPU EEVEE via NVIDIA EGL, plus a token-protected API through a Cloudflare tunnel); `tools/node.py` is the client.
5. `blender/render_batch.py` renders the shots; `blender/assemble.py` builds the film with ffmpeg.

Re-render one shot locally: `blender -b --factory-startup --python blender/run_shot.py -- s22 preview all`

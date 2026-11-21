# CLAUDE.md

@.claude/skills/ponytail/SKILL.md
@AGENTS.md
@.claude/skills/make-video/SKILL.md

## Claude Code specifics
- The ponytail skill (imported above, also auto-discovered from `.claude/skills/ponytail/`) is active at level **full** from the first message; its scope limits are in `AGENTS.md` §0.
- The shared rules, layout, model stack and lessons are in `AGENTS.md` (imported above). Follow them exactly.
- Any "make a video …" request → follow the make-video skill (imported above; also `/make-video <topic> [shorts|long] [duration]`). Build a new film from `prompts/MASTER_PROMPT_animation_pipeline.md` (3D) or `prompts/MASTER_PROMPT_2D_animation.md` (2D), filling `prompts/TEMPLATES.md`.
- Long Kaggle jobs: start them with `tools/node.py run`, then wait with a background poll (`until ... grep ALLDONE ...`), not foreground sleeps.
- **Read `prompts/TEMPLATES.md` §17 before any film** (voices/gender, tone, readability, Gates A and B). The last film was rejected for breaking it.
- Look at QA images with the Read tool before declaring a shot done.
- Use the scratchpad for temporary files; keep film outputs inside `videos/<film>/out/`.

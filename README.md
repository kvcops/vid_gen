# vid_gen — make animated videos by just asking

**1. Start the GPU (every session):** open a Kaggle notebook → Accelerator **GPU T4 x2**, Internet **ON** → paste the whole `kaggle/render_node.py` into one cell → Run. After ~5 min it prints:
```
ENDPOINT : https://xxxx.trycloudflare.com
TOKEN    : xxxxxxxx
```
Keep that Kaggle tab open.

**2. Ask for the video:** open this folder in **Claude Code**, **Codex** or **OpenCode** and type your request + paste those two lines:
```
make a funny video about a lazy lion king, shorts, 50 seconds
ENDPOINT : https://xxxx.trycloudflare.com
TOKEN    : xxxxxxxx
```
(format, duration, 2D/3D and language are optional — e.g. `long 3D video, 6 min, Telugu: Devara 2 part 2`)

**3. Approve the short outline** the agent shows → the video lands in `<film>/out/<film>_final.mp4`.

The link changes every Kaggle session — re-run the cell and paste the new lines. Agent rules: `AGENTS.md`

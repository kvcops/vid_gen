import sys, glob, os
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]; pref = sys.argv[3:]
fs = sorted(f for f in glob.glob(os.path.join(src, '*.jpg')) if any(os.path.basename(f).startswith(p) for p in pref))
W, Hh = 640, 360; cols = 3; rows = (len(fs) + cols - 1) // cols
S = Image.new('RGB', (W * cols, Hh * rows))
for i, f in enumerate(fs):
    im = Image.open(f).resize((W, Hh)); d = ImageDraw.Draw(im); d.text((8, 6), os.path.basename(f), fill=(255, 255, 0))
    S.paste(im, ((i % cols) * W, (i // cols) * Hh))
S.save(out, quality=88); print(len(fs))

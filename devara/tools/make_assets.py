"""Render Telugu title cards / poster as PNGs with headless Chrome (correct Telugu shaping)."""
import os, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets'); os.makedirs(OUT, exist_ok=True)
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

def shot(name, html, w, h):
    tmp = os.path.join(tempfile.gettempdir(), f'{name}.html')
    open(tmp, 'w', encoding='utf-8').write(f"<html><head><meta charset='utf-8'><style>html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden}}</style></head><body>{html}</body></html>")
    out = os.path.join(OUT, name + '.png')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--default-background-color=00000000',
                    f'--window-size={w},{h}', f'--screenshot={out}', 'file:///' + tmp.replace('\\', '/')], check=True, capture_output=True)
    print(out)

FONT = "'Nirmala UI','Gautami',sans-serif"
TITLE = f"""<div style="width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center">
<div style="font-family:{FONT};font-weight:800;font-size:330px;line-height:1;letter-spacing:10px;
  background:linear-gradient(180deg,#fff1c9 0%,#f2b552 38%,#b8341b 72%,#5c0c06 100%);-webkit-background-clip:text;color:transparent;
  filter:drop-shadow(0 10px 0 #2a0402) drop-shadow(0 0 40px rgba(255,90,30,.65))">దేవర 2</div>
<div style="font-family:{FONT};font-weight:700;font-size:64px;color:#f6e7c6;letter-spacing:14px;margin-top:28px;text-shadow:0 4px 18px #000">ఎండు చేప రహస్యం</div>
</div>"""
END = f"""<div style="width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center">
<div style="font-family:{FONT};font-weight:800;font-size:200px;letter-spacing:8px;
  background:linear-gradient(180deg,#fff1c9 0%,#f2b552 40%,#b8341b 75%,#5c0c06 100%);-webkit-background-clip:text;color:transparent;
  filter:drop-shadow(0 8px 0 #2a0402) drop-shadow(0 0 36px rgba(255,90,30,.6))">దేవర 2</div>
<div style="font-family:{FONT};font-weight:700;font-size:76px;color:#f6e7c6;letter-spacing:6px;margin-top:20px;text-shadow:0 4px 18px #000">మిగతా కథ... త్వరలో!</div>
<div style="font-family:{FONT};font-size:30px;color:#d9cdb5;opacity:.85;margin-top:70px;text-shadow:0 2px 8px #000">ఇది అభిమానులు చేసిన కల్పిత హాస్య కథ — కేవలం వినోదం కోసం మాత్రమే</div>
</div>"""
POSTER = f"""<div style="width:100%;height:100%;background:radial-gradient(circle at 50% 40%,#8f1d0e 0%,#3a0704 55%,#120202 100%);
  display:flex;flex-direction:column;align-items:center;justify-content:flex-end;position:relative;overflow:hidden">
<svg width="700" height="900" viewBox="0 0 700 900" style="position:absolute;top:60px">
 <path d="M350 120 C300 120 270 170 272 230 C230 250 215 320 230 380 L190 600 L230 610 L260 470 L300 900 L400 900 L440 470 L470 610 L510 600 L470 380
 C485 320 470 250 428 230 C430 170 400 120 350 120 Z" fill="#090101"/>
 <path d="M470 380 L640 140 L660 160 L500 400 Z" fill="#c9c9c9"/>
 <circle cx="350" cy="200" r="250" fill="none" stroke="#ff8a3d" stroke-width="3" opacity=".35"/>
</svg>
<div style="position:relative;font-family:{FONT};font-weight:800;font-size:210px;color:#ffd38a;letter-spacing:8px;text-shadow:0 8px 0 #3a0603,0 0 40px #ff5a1e">దేవర 2</div>
<div style="position:relative;font-family:{FONT};font-weight:700;font-size:56px;color:#fff;margin:6px 0 70px;letter-spacing:6px">త్వరలో</div>
</div>"""

if __name__ == '__main__':
    shot('title', TITLE, 1920, 1080)
    shot('endcard', END, 1920, 1080)
    shot('poster', POSTER, 840, 1200)

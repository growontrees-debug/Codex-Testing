"""Live desktop animation. Install: python -m pip install pillow numpy
Run: python hello_world.py. Space replays; Escape closes the window.
"""
import time
import sys
import tkinter as tk
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk

W, H = 720, 480
rng = np.random.default_rng(7)
def load_font(size):
    for name in ('DejaVuSans.ttf', 'Arial.ttf', 'arial.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)

font = load_font(76)
small = load_font(16)
mask = Image.new('L', (W,H))
d = ImageDraw.Draw(mask)
d.text((W/2,H/2), 'Hello World', font=font, anchor='mm', fill=255)
ys,xs = np.where(np.asarray(mask)>128)
n = 6500
idx = rng.choice(len(xs), n, replace=True)
start = np.column_stack((xs[idx],ys[idx])).astype(float)

# Hand-drawn continent silhouettes in longitude/latitude coordinates.
continents = [
 [(-168,70),(-130,72),(-110,60),(-60,52),(-80,25),(-100,15),(-115,30),(-130,50)],
 [(-81,12),(-50,5),(-35,-8),(-48,-30),(-70,-56),(-78,-20)],
 [(-18,35),(10,38),(35,30),(50,10),(35,-30),(18,-35),(0,-5),(-15,10)],
 [(-10,36),(-12,58),(25,72),(70,72),(110,60),(160,60),(145,40),(120,20),(100,5),(75,8),(50,30),(30,40)],
 [(112,-12),(140,-10),(153,-28),(135,-39),(114,-30)],
 [(-55,60),(-45,82),(-20,78),(-30,62)],
 [(45,-13),(50,-15),(48,-25),(44,-23)],
]
land = Image.new('L', (720,360))
ld = ImageDraw.Draw(land)
for poly in continents:
    ld.polygon([((lon+180)*2,(90-lat)*2) for lon,lat in poly], fill=255)
land = np.asarray(land)
# Sample the visible hemisphere evenly, then recover spherical coordinates.
rr = np.sqrt(rng.random(n))
a = rng.uniform(0,2*np.pi,n)
x,y = rr*np.cos(a),rr*np.sin(a)
z = np.sqrt(1-rr*rr)
lat = np.arcsin(-y)
lon = np.arctan2(x,z)-0.18
island = land[np.clip(((np.pi/2-lat)*180/np.pi*2).astype(int),0,359),
              np.clip(((lon*180/np.pi+180)*2).astype(int),0,719)]>0
target = np.column_stack((360+x*155,240+y*155))
light = np.clip(0.35+0.65*(z*0.8-x*0.4-y*0.3),0.25,1)
base = np.where(island[:,None],np.array([77,223,158]),np.array([38,138,238]))
colors = (base*light[:,None]).astype(int)
stars = rng.integers([0,0],[W,H],size=(100,2))
def render_frame(elapsed):
    t = np.clip((elapsed-1.2)/3.3,0,1)
    ease=t*t*(3-2*t)
    im=Image.new('RGB',(W,H),(6,12,27)); draw=ImageDraw.Draw(im)
    for sx,sy in stars:
        draw.point((int(sx),int(sy)),fill=(55,68,94))
    draw.text((36,28),'FROM A GREETING TO A PLANET',font=small,fill=(118,153,181))
    if t>0:
        for radius in range(166,155,-1):
            c=int((167-radius)*3*ease)
            draw.ellipse((360-radius,240-radius,360+radius,240+radius),outline=(8,c+12,c+30))
    pos=start*(1-ease)+target*ease
    pos[:,0]+=np.sin(a*3+t*6)*np.sin(np.pi*t)*35
    pos[:,1]+=np.cos(a*2+t*6)*np.sin(np.pi*t)*35
    for k,(px,py) in enumerate(pos):
        col=tuple(((1-ease)*np.array([221,242,255])+ease*colors[k]).astype(int))
        draw.ellipse((px-1,py-1,px+1,py+1),fill=col)
    label='Hello World' if t==0 else ('Becoming a world...' if t<1 else 'A world of possibilities')
    draw.text((360,437),label,font=small,anchor='mm',fill=(155,185,207))
    return im


class AnimationWindow:
    def __init__(self, root):
        self.root = root
        root.title('Hello World → Earth')
        root.configure(bg='#060c1b')
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=W, height=H, highlightthickness=0)
        self.canvas.pack()
        self.image_id = self.canvas.create_image(0, 0, anchor='nw')
        tk.Button(root, text='Replay  ·  Space', command=self.replay,
                  bg='#14263b', fg='white', padx=20, pady=8).pack(pady=(0, 12))
        root.bind('<space>', lambda event: self.replay())
        root.bind('<Escape>', lambda event: self.close())
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.pending = None
        self.replay()

    def replay(self):
        if self.pending is not None:
            self.root.after_cancel(self.pending)
            self.pending = None
        self.started = time.perf_counter()
        self.update()

    def update(self):
        self.pending = None
        elapsed = time.perf_counter() - self.started
        self.photo = ImageTk.PhotoImage(render_frame(elapsed))
        self.canvas.itemconfigure(self.image_id, image=self.photo)
        # Render only the current frame; no frame files or GIFs are written.
        if elapsed < 4.5:
            self.pending = self.root.after(16, self.update)

    def close(self):
        if self.pending is not None:
            self.root.after_cancel(self.pending)
        self.root.destroy()


def main():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f'Cannot open a desktop window: {exc}\n'
              'Run this program in a graphical desktop session with Tk installed.', file=sys.stderr)
        return 1
    AnimationWindow(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

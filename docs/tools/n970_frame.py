#!/usr/bin/env python3
"""Convert a picture into the two CMD 10 pixel streams of the Nebular Pro 970Q-N (960 x 672 scan, 4 colours: white, black, red, yellow).

Usage: n970_frame.py picture.png out_prefix [--landscape]
Input: portrait 672 x 960 PNG (upright as the tag is read). Each pixel is mapped to the nearest of white / black / red / yellow.
With --landscape a 960 x 672 picture is rotated 90 deg clockwise first.
Output: out_prefix_pass0.bin and out_prefix_pass1.bin (161280 bytes each); copy them to the Pico as picture_pass0.bin / picture_pass1.bin.

Pixel stream: scan line y (0..671) has 960 pixels x (0..959); portrait pixel (px, py) = scan (x = py, y = px); 4 pixels per byte, first pixel in bits 7..6.
Colour -> 2-bit value in (pass 0, pass 1), verified on hardware:  white 1,1   black 1,0   red 0,1   yellow 2,1
"""
import sys
from PIL import Image
PAL = {'white': (255, 255, 255), 'black': (0, 0, 0), 'red': (200, 40, 20), 'yellow': (255, 220, 0)}
VAL = {'white': (1, 1), 'black': (1, 0), 'red': (0, 1), 'yellow': (2, 1)}
def nearest(c):
    return min(PAL, key=lambda n: sum((a - b) ** 2 for a, b in zip(c, PAL[n])))
def convert(im, landscape=False):
    im = im.convert('RGB')
    if landscape: im = im.transpose(Image.ROTATE_270)
    if im.size != (672, 960): raise SystemExit('need 672 x 960 (portrait) picture, got %s x %s' % im.size)
    px = im.load(); cache = {}
    passes = [bytearray(), bytearray()]
    for y in range(672):
        cur = [0, 0]; n = 0
        for x in range(960):
            c = px[y, x]
            nm = cache.get(c) or cache.setdefault(c, nearest(c))
            for p in (0, 1): cur[p] = (cur[p] << 2) | VAL[nm][p]
            n += 1
            if n == 4:
                for p in (0, 1): passes[p].append(cur[p])
                cur = [0, 0]; n = 0
    return passes
if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) != 2: raise SystemExit(__doc__)
    p0, p1 = convert(Image.open(a[0]), '--landscape' in sys.argv)
    open(a[1] + '_pass0.bin', 'wb').write(p0); open(a[1] + '_pass1.bin', 'wb').write(p1)
    print(len(p0), len(p1))

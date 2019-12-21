#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
from pathlib import Path
import math

print("demGenerator - Module 3: DEM generation from downloaded elevation data")

# zbierz wszystkie dane wysokościowe ze wszystkich plików 'h_XX.txt'
heights = []
hmaxs = []
hmins = []
i = 0
while (Path("demGen_data/h_%d.txt" % i).exists()):
    data = open("demGen_data/h_%d.txt" % i)
    h = []
    while ("true"):
        string = data.readline()
        tab = string.split()
        if (len(tab) != 0):
            h.append(float(tab[0]))
        else:
            break
    heights.append(h)
    hmaxs.append(max(h))
    hmins.append(min(h))
    data.close()
    i += 1
if (i > 0):  
    # sprawdź czy jest n^2 kafelków
    pc = int(math.sqrt(len(heights))) # ilość kafelków w poziomie/pionie
    if (int(pc) == pc):
        # wyznacz h(max), h(min), dh (różnicę wysokości) i r (zakres wysokości)
        hmax = max(hmaxs)
        hmin = min(hmins)
        del hmaxs, hmins
        dh = hmax - hmin
        i = 1
        r = 255
        while (dh > r): # dopóki różnica wysokości jest większa od jego zakresu, zwiększaj to drugie
            i *= 2
            r = 256 * i - 1
        if (hmax > r or hmin < 0):
            dh2 = (r - hmin - hmax) / 2
        else:
            dh2 = 0
        print("H(min): %.2f m, H(max): %.2f m, dH: %.2f m, height scale: %d m" % (hmin, hmax, dh, r))
    
        l = math.sqrt(len(heights[0])) # szerokość/wysokość jednego kafelka
        ltot = int((l - 1) * pc + 1)
        print("Tiles count: %d, DEM size: (%d x %d) px\nDEM generation in progress..." % (len(heights), ltot, ltot))

        dem = Image.new("I", (ltot, ltot))
        d = ImageDraw.Draw(dem)

        for i in range(pc):
            for j in range(pc):
                for k in range(len(heights[pc * i + j])):
                    if (i == 0 and k < l):
                        d.point((j * (l - 1) + (k % l), ltot - (i * (l - 1) + int(k / l)) - 1), round((heights[pc * i + j][k] + dh2) * 65535 / r))
                    if (j == 0 and k % l == 0):
                        d.point((j * (l - 1) + (k % l), ltot - (i * (l - 1) + int(k / l)) - 1), round((heights[pc * i + j][k] + dh2) * 65535 / r))
                    if (k >= l and k % l != 0):
                        d.point((j * (l - 1) + (k % l), ltot - (i * (l - 1) + int(k / l)) - 1), round((heights[pc * i + j][k] + dh2) * 65535 / r))
        dem.save("demGen_data/map_dem.png", "PNG")
        dem.close()
        print("DEM generated and saved")
    else:
        print("Invalid 'h_*.txt' files count! Is: %d. Should be: %d." % (len(heights), math.pow(2, math.floor(math.log2(len(heights))))))
        del heights, hmaxs, hmins
else:
    print("Files with elevation data not found")

w = input("Press ENTER to close...")

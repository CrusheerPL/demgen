#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
from pathlib import Path
import math, locale

if locale.getdefaultlocale()[0] == 'pl_PL':
    lang = ['demGenerator - skrypt 3/3: generowanie DEM z pobranych danych wysokościowych', 'Ilość części (kafelków): %d, wymiary DEM: (%d x %d) px\nGenerowanie DEM...', 'DEM zostało utworzone i zapisane', "Uwaga: nieprawidłowa ilość plików 'h_*.txt'! Jest: %d. Powinno być: %d.", 'Uwaga: nie znaleziono plików z danymi wysokościowymi', 'Wciśnij ENTER, aby zamknąć...']
else:
    lang = ['demGenerator - script 3/3: DEM generation from downloaded elevation data', 'Tiles count: %d, DEM size: (%d x %d) px\nDEM generation in progress...', 'DEM created and saved', "Warning: invalid 'h_*.txt' files count! Is: %d. Should be: %d.", 'Warning: files with elevation data not found', 'Press ENTER to close...']

print(lang[0])

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
        print('H(min): %.2f m, H(max): %.2f m, dH: %.2f m, Height Scale: %d m' % (hmin, hmax, dh, r))
    
        l = math.sqrt(len(heights[0])) # szerokość/wysokość jednego kafelka
        ltot = int((l - 1) * pc + 1)
        print(lang[1] % (len(heights), ltot, ltot))

        dem = Image.new("I", (ltot, ltot))
        dem8 = Image.new("RGB", (ltot, ltot))
        d = ImageDraw.Draw(dem)
        d8 = ImageDraw.Draw(dem8)

        for i in range(pc):
            for j in range(pc):
                for k in range(len(heights[pc * i + j])):
                    if (i == 0 and k < l) or (j == 0 and k % l == 0) or (k >= l and k % l != 0):
                        h2 = heights[pc * i + j][k] + dh2
                        d.point((j * (l - 1) + (k % l), ltot - (i * (l - 1) + int(k / l)) - 1), round(h2 * 65535 / r))
                        demR = math.floor(h2)
                        demG = round(demR + (h2 - demR) * 256)
                        if demG > 255:
                            demR += 1
                            demG -= 255
                        d8.point((j * (l - 1) + (k % l), ltot - (i * (l - 1) + int(k / l)) - 1), (demR, demG, 0))
        dem.save("demGen_data/map_dem_16bit.png", "PNG")
        dem8.save("demGen_data/map_dem_8bit.png", "PNG")
        dem.close()
        dem8.close()
        print(lang[2])
    else:
        print(lang[3] % (len(heights), math.pow(2, math.floor(math.log2(len(heights))))))
        del heights, hmaxs, hmins
else:
    print(lang[4])

w = input(lang[5])

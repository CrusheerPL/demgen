#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
from pathlib import Path
import math, locale, os, pathlib

if locale.getdefaultlocale()[0] == 'pl_PL':
    lang = ['demGenerator - skrypt 3/3: generowanie DEM z pobranych danych wysokościowych', '\nNie można wczytać pliku konfiguracyjnego\nIlość kafelków: ', '\nWczytywanie pliku konfiguracyjnego...', '\nIlość części (kafelków): %d, wymiary DEM: (%d x %d) px\nGenerowanie DEM...', 'DEM zostało utworzone i zapisane', "\nUwaga: nieprawidłowa ilość plików 'h_*.txt'! Jest: %d. Powinno być: %d.\nBrakujące pliki:", '\nUwaga: nie znaleziono plików z danymi wysokościowymi', '\nWciśnij ENTER, aby zamknąć...']
else:
    lang = ['demGenerator - script 3/3: DEM generation from downloaded elevation data', "\nCan't load the config file\nTiles count: ", '\nConfig file is loading...', '\nTiles count: %d, DEM size: (%d x %d) px\nDEM generation in progress...', 'DEM created and saved', "\nWarning: invalid 'h_*.txt' files count! Is: %d. Should be: %d.\nMissing files:", '\nWarning: files with elevation data not found', '\nPress ENTER to close...']

print(lang[0])

heights = []
hmax = []
hmin = []
div = 0

try:
    config = open('demGenerator_config.txt', 'r')
except:
    div = input(lang[1])
else:
    print(lang[2])
    div = config.read().split()[7]
    config.close()

while not (div.isnumeric() and div != '0'):
    div = input(lang[1])

div = int(div)
hf = sorted(pathlib.Path(os.getcwd() + '\\demGen_data').glob('h_*.txt'))

if len(hf) > 0:
    ids = []
    for i in hf:
        idt = int(str(i).split('\\')[-1][2:-4])
        if idt >= 0 and idt < div: ids.append(idt)
        del idt
    ids = sorted(ids)
    # sprawdź czy jest n^2 kafelków
    if len(ids) == div and div == ids[-1] + 1: # sprawdź po id kafelków czy nie ma braków
        pc = int(math.sqrt(div)) # ilość kafelków w poziomie/pionie
        # zbierz wszystkie dane wysokościowe ze wszystkich dostępnych plików 'h_XX.txt'
        for i in ids:
            h = open('demGen_data/h_%d.txt' % i).read().split('\n')
            del h[-1]
            for j in range(len(h)):
                h[j] = float(h[j])
            heights.append(h)
            hmax.append(max(h))
            hmin.append(min(h))
            del h
        # wyznacz h(max), h(min), dh (różnicę wysokości) i r (zakres wysokości)
        hmax = max(hmax)
        hmin = min(hmin)
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
        print(lang[3] % (div, ltot, ltot))

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
        print(lang[4])
    else:
        print(lang[5] % (len(ids), div))
        for i in range(div):
            if not (i in ids):
                print('h_%d.txt' % i)
        del heights, hmax, hmin
else:
    print(lang[6])

w = input(lang[7])

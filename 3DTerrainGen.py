#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os, math, locale, pathlib, tqdm


if locale.getdefaultlocale()[0] == 'pl_PL':
    lang = ['3dTerrainGen - program tworzący statyczne modele 3D terenu z pobranych danych wysokościowych', '\nNie można wczytać pliku konfiguracyjnego - wprowadź dane ręcznie.', '\nWczytywanie pliku konfiguracyjnego...', 'SUKCES', 'Rozdzielczość terenu [m/px]: ', '\nGenerowanie obiektów 3D...', 'Obiekty 3D zapisano w formacie OBJ do folderu "staticTerrain"', '\nUwaga: nie znaleziono plików z danymi wysokościowymi', '\nWciśnij ENTER, aby zamknąć...']
else:
    lang = ['3DTerrainGen: Static 3D terrain model generation from downloaded elevation data', "\nCan't load the config file - you must enter your data manually.", '\nConfig file is loading...', 'SUCCESS', 'Terrain resolution [meters per pixel]: ', '\nGenerating 3D objects...', '3D objects saved in OBJ format to the "staticTerrain" folder', '\nWarning: files with elevation data not found', '\nPress ENTER to close...']

print(lang[0])

try:
    config = open("demGenerator_config.txt", "r")
except:
    print(lang[1])
    d = float(input(lang[4]))
else:
    print(lang[2], end=' ')
    d = float(config.read().split()[6])
    config.close()
    print(lang[3])

tiles = sorted(pathlib.Path(os.getcwd() + '\\demGen_data').glob('h_*.txt'))

if len(tiles) > 0:
    if (not os.path.exists(os.getcwd() + "\\staticTerrain")):
        os.mkdir(os.getcwd() + "\\staticTerrain")
    print(lang[5])
    with tqdm.tqdm(total=len(tiles)) as pbar:
        for i in tiles:
            data = open(i).read().split('\n')
            del data[-1]
            x = math.sqrt(len(data))
            if x == int(x):
                l = x - 1 * d / 2 # pozycja początkowa przy osi z
                it = int(x) # ilość iteracji
                ind = tiles.index(i) + 1
                obj = open('staticTerrain/terrain_%d.obj' % ind, 'w')
                obj.write('o staticTerrain_%d\n' % ind)
                fgp = ['s 1\n']
                for m in range(it):
                    for n in range(it):
                        vid = it * m + n
                        obj.write('v %f %f %f\n' % (-l + n * d, float(data[vid]), l - m * d))
                        if m < (it - 1) and n < (it - 1):
                            s = 'f ' + str(vid + 1) + ' ' + str(vid + 2) + ' ' + str(vid + it + 2) + ' ' + str(vid + it + 1) + '\n'
                            fgp.append(s)
                for k in range(len(fgp)):
                    obj.write(fgp[k])
                obj.close()
            pbar.update(1)
    print(lang[6])
else:
    print(lang[7])

w = input(lang[8])

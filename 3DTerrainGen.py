#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import os
import math

print("3DTerrainGen: Static 3D terrain model generation from downloaded elevation data")

# zbierz wszystkie dane wysokościowe ze wszystkich plików 'h_XX.txt'
heights = []
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
    data.close()
    i += 1

ex = True
if i == 0:
    print("Files with elevation data not found")
    ex = False

if ex:
    try:
        print('Trying to open the config file...')
        config = open("demGenerator_config.txt", "r")
    except:
        print("File not found.")
        d = float(input("Resolution [meters per pixel]: "))
    else:
        string = config.read()
        string = string.split()
        d = float(string[6])
        config.close()

    if (not os.path.exists(os.getcwd() + "\\staticTerrains")):
        os.mkdir(os.getcwd() + "\\staticTerrains")
        
    for j in range(len(heights)):
        x = math.sqrt(len(heights[j]))
        if x == int(x):
            l = x - 1 * d / 2 # pozycja początkowa przy osi z
            it = int(x) # ilość iteracji
            obj = open('staticTerrains/terrain_%d.obj' % j, 'w')
            obj.write('o staticTerrain_%d\n' % j)
            fgp = ['s 1\n']
            for m in range(it):
                for n in range(it):
                    vid = it * m + n
                    obj.write('v %f %f %f\n' % (-l + n * d, heights[j][vid], l - m * d))
                    if (m < (it - 1) and n < (it - 1)):
                        s = 'f ' + str(vid + 1) + ' ' + str(vid + 2) + ' ' + str(vid + it + 2) + ' ' + str(vid + it + 1) + '\n'
                        fgp.append(s)
            for k in range(len(fgp)):
                obj.write(fgp[k])
            obj.close()
    print('Models saved as OBJ files in "staticTerrains" directory')
del heights
w = input("Press ENTER to close...")

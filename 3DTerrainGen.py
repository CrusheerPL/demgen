#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import tqdm

print("3DTerrainGen: Static 3D terrain model generation from downloaded elevation data")

try:
    print('Trying to open the config file...')
    config = open("demGenerator_config.txt", "r")
except:
    print("Can't load the config file.")
    d = float(input("Resolution [meters per pixel]: "))
    div = int(input("Tiles count: "))
else:
    print("Config file is loading...", end=' ')
    string = config.read()
    string = string.split()
    d = float(string[6])
    div = int(string[7])
    config.close()
    print('Done.')

tiles = []
for i in range(div):
    if os.path.exists(os.getcwd() + "\\demGen_data\\xy_%d.txt" % i):
        tiles.append(i)
        
print("Count of 'h_*.txt' files: %d." % len(tiles))

if len(tiles) != 0:
    if (not os.path.exists(os.getcwd() + "\\staticTerrains")):
        os.mkdir(os.getcwd() + "\\staticTerrains")
    print('3D terrains generating in progress...')
    with tqdm.tqdm(total=len(tiles)) as pbar:
        for i in tiles:
            data = open("demGen_data/h_%d.txt" % i)
            heights = []
            while ("true"):
                string = data.readline()
                tab = string.split()
                if (len(tab) != 0):
                    heights.append(float(tab[0]))
                else:
                    break
            data.close()

            x = math.sqrt(len(heights))
            if x == int(x):
                l = x - 1 * d / 2 # pozycja początkowa przy osi z
                it = int(x) # ilość iteracji
                obj = open('staticTerrains/terrain_%d.obj' % i, 'w')
                obj.write('o staticTerrain_%d\n' % i)
                fgp = ['s 1\n']
                for m in range(it):
                    for n in range(it):
                        vid = it * m + n
                        obj.write('v %f %f %f\n' % (-l + n * d, heights[vid], l - m * d))
                        if (m < (it - 1) and n < (it - 1)):
                            s = 'f ' + str(vid + 1) + ' ' + str(vid + 2) + ' ' + str(vid + it + 2) + ' ' + str(vid + it + 1) + '\n'
                            fgp.append(s)
                for k in range(len(fgp)):
                    obj.write(fgp[k])
                obj.close()
            pbar.update(1)
    print('Models saved as OBJ files in "staticTerrains" directory')
del heights
w = input("Press ENTER to close...")

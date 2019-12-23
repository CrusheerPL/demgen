#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
import math
import os

print('Map_weight generator')
use_stdin = True
try:
    print('Trying to open the config file... ', end='')
    config = open("demGenerator_config.txt", "r")
except:
    print("File not found.")
    l = int(input("Map edge length [meters]: "))
else:
    print("Done.\nConfig file is loading...")
    string = config.read()
    string = string.split()
    l = int(string[5])
    use_stdin = False
    config.close()

if (l % 1024 == 0):
    div = int(l / 1024)
    if (not os.path.exists(os.getcwd() + "\\weightMaps")):
        os.mkdir(os.getcwd() + "\\weightMaps")
    print('Creating weight maps...')
    texNames = ["animalMud", "asphalt", "beachSandWet", "concrete", "forestGround", "forestGroundUS", "grass", "grassRough", "grassTown", "gravel", "mountainRock", "mountainRockDark", "plate", "plateDamaged", "riverStoneBank", "roughDirt"]
    texNames2 = ["concreteDirt", "concreteGravel", "riverStoneBankWater", "riverStoneBankWaterEdge", "waterPuddle"]
    for i in range(len(texNames)):
        for j in range(1, 5):
            Image.new('L', (l, l)).save('weightMaps/%s0%s_weight.png' % (texNames[i], j), 'PNG')
    for i in range(len(texNames2)):
        Image.new('L', (l, l)).save('weightMaps/%s01_weight.png' % texNames2[i], 'PNG')
    for i in range(div):
        for j in range(div):
            imid = div * i + j + 1
            if imid < 10:
                imid = '0%d' % imid
            else:
                imid = str(imid)
            wm = Image.new('L', (l, l))
            d = ImageDraw.Draw(wm)
            for m in range(1024 * (div - i), 1024 * (div - i - 1), -1):
                for n in range(1024 * j, 1024 * j + 1024):
                    d.point((n, m - 1), 255)
            wm.save('weightMaps/ortho%s_weight.png' % imid, 'PNG')
    print('Generating extra lines for map.i3d...')
    el = open('weightMaps/mapI3DExtraLines.xml', 'w')
    el2 = ''
    el3 = '\n        <CombinedLayer name="ORTHO" layers="'
    el4 = ''
    el.write('Extra lines which you have to paste to the map.i3d in the text editor:\n\n  <Files>\n    ...\n    <File fileId="100000" filename="textures/terrain/ortho_normal.png"/>')
    fid = 100001
    for i in range(1, int(math.pow(div, 2) + 1)):
        if i < 10:
            imid = '0%d' % i
        else:
            imid = str(i)
        el3 += 'ortho%s;' % imid
        el.write('\n    <File fileId="%d" filename="textures/terrain/ortho%s_diffuse.png"/>' % (fid, imid))
        el4 += '\n    <File fileId="%d" filename="mapDE/ortho%s_weight.png"/>' % (fid + 1, imid)
        el2 += '\n        <Layer name="ortho%s" detailMapId="%d" normalMapId="100000" unitSize="1024" weightMapId="%d" blendContrast="0.2" distanceMapId="YY" attributes="0.208 0.11 0.056 1 2" priority="0"/>' % (imid, fid, fid + 1)
        fid += 2
    el3 += '" noiseFrequency="2"/>'
    el.write(el4 + '\n    ...\n  </Files>\n\n  <Scene>\n    ...\n    <TerrainTransformGroup>\n      <Layers>\n        ...' + el2 + '\n        ...' + el3 + '\n        ...\n      <Layers>\n    <TerrainTransformGroup>\n    ...\n  <Scene>')
    el.close()
else:
    print("Incorrect map edge length")

_ = input('Ready. Press ENTER to close...')

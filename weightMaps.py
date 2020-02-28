#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
import math
import os

print('Weight maps generator')
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
    fs = input('For which FS edition do you want to generate weight maps?\n1. FS 19\n2. FS 17\n3. FS 15\n4. FS 2013\n(1-4): ')
    while not '1' <= fs <= '4':
        fs = input('Incorrect input, retry (1-4): ')

    div = int(l / 1024)
    if (not os.path.exists(os.getcwd() + "\\weightMaps")):
        os.mkdir(os.getcwd() + "\\weightMaps")
    
    print('Creating weight maps...')
    if fs == '1':
        texNames = ["animalMud", "asphalt", "beachSandWet", "concrete", "forestGround", "forestGroundUS", "grass", "grassRough", "grassTown", "gravel", "mountainRock", "mountainRockDark", "plate", "plateDamaged", "riverStoneBank", "roughDirt"]
        texNames2 = ["concreteDirt", "concreteGravel", "riverStoneBankWater", "riverStoneBankWaterEdge", "waterPuddle"]
        for i in range(len(texNames)):
            for j in range(1, 5):
                Image.new('L', (l, l)).save('weightMaps/%s0%s_weight.png' % (texNames[i], j), 'PNG')
    elif fs == '2':
        texNames2 = ["roughDirt", "grass", "mountainRock", "beachSand", "gravel", "concrete", "forestGround", "townGrass", "pigMud"]
    elif fs == '3':
        texNames2 = ["dirt", "grass", "rock", "beachSand", "gravel", "asphalt", "cobblestone", "leaves"]
    else:
        texNames2 = ["asphalt", "beachSand", "cobblestone", "dirt", "grass", "gravel", "lawnGrass", "rock"]
    for i in range(len(texNames2)):
        if fs == '1':
            Image.new('L', (l, l)).save('weightMaps/%s01_weight.png' % texNames2[i], 'PNG')
        else:
            Image.new('L', (l, l)).save('weightMaps/%s_weight.png' % texNames2[i], 'PNG')
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
    el4 = ''
    if fs == '1':
        el.write('FS 19')
    elif fs == '2':
        el.write('FS 17')
    elif fs == '3':
        el.write('FS 15')
    else:
        el.write('FS 2013')
    el.write('\nExtra lines which you have to paste to the map.i3d in the text editor:\n\n  <Files>\n    ...')
    if fs != '4':
        el.write('\n    <File fileId="100000" filename="textures/terrain/ortho_normal.png"/>')
    fid = 100001
    for i in range(1, int(math.pow(div, 2) + 1)):
        if i < 10:
            imid = '0%d' % i
        else:
            imid = str(i)
        if fs == '1':
            el.write('\n    <File fileId="%d" filename="textures/terrain/ortho%s_diffuse.png"/>' % (fid, imid))
            el4 += '\n    <File fileId="%d" filename="mapDE/ortho%s_weight.png"/>' % (fid + 1, imid)
        else:
            el.write('\n    <File fileId="%d" filename="textures/terrain/ortho%s_diffuse.png" relativePath="true"/>' % (fid, imid))
            el4 += '\n    <File fileId="%d" filename="map01/ortho%s_weight.png" relativePath="true"/>' % (fid + 1, imid)
        el2 += '\n        <Layer name="ortho%s" detailMapId="%d" unitSize="1024" weightMapId="%d" distanceMapId="YY" ' % (imid, fid, fid + 1)
        if fs != '4':
            el2 += 'normalMapId="100000" priority="0" '
            if fs == '3':
                el2 += 'attributes="0.208 0.11 0.056 1" '
            else:
                el2 += 'attributes="0.208 0.11 0.056 1 2" '
            if fs == '1':
                el2 += 'blendContrast="0.2"'
        if fs >= '3':
            el2 += 'distanceMapUnitSize="128"'
        el2 += '/>'
        fid += 2
    el.write(el4 + '\n    ...\n  </Files>\n\n  <Scene>\n    ...\n    <TerrainTransformGroup>\n      <Layers>\n        ...' + el2 + '\n        ...\n      </Layers>\n    </TerrainTransformGroup>\n    ...\n  </Scene>\n\n')
    el.close()
else:
    print("Incorrect map edge length")

_ = input('Ready. Press ENTER to close...')

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
    div = int(l / 1024)
    if (not os.path.exists(os.getcwd() + "\\mapWeights")):
        os.mkdir(os.getcwd() + "\\mapWeights")
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
            wm.save('mapWeights/grassRough%s_weight.png' % imid, 'PNG')
    if math.pow(div, 2) > 4:
        el = open('mapWeights/mapI3DExtraLines.xml', 'w')
        el2 = []
        el3 = '\n        <CombinedLayer name="GRASS" layers="grass01;grass02;grass03;grass04'
        el.write('Extra lines which you have to paste to the map.i3d in the text editor:\n\n  <Files>\n    ...')
        fid = 100000
        for i in range(5, int(math.pow(div, 2) + 1)):
            if i < 10:
                imid = '0%d' % i
            else:
                imid = str(i)
            el3 += ';grass%s' % imid
            el.write('\n    <File fileId="%d" filename="textures/terrain/grassRough%s_diffuse.png"/>' % (fid, imid))
            el.write('\n    <File fileId="%d" filename="mapDE/grassRough%s_weight.png"/>' % (fid + 1, imid))
            el2.append('\n        <Layer name="grass%s" detailMapId="%d" normalMapId="XX" unitSize="1024" weightMapId="%d" blendContrast="0.2" distanceMapId="YY" attributes="0.208 0.11 0.056 1 2" priority="0"/>' % (imid, fid, fid + 1))
            fid += 2
        el.write('\n    ...\n  </Files>\n\n  <Scene>\n    ...\n    <TerrainTransformGroup>\n      <Layers>\n        ...')
        for i in range(len(el2)):
            el.write(el2[i])
        el3 += '" noiseFrequency="2"/>'
        el.write('\n        ...' + el3)
        el.write('\n        ...\n      <Layers>\n    <TerrainTransformGroup>\n    ...\n  <Scene>')
        el.close()
else:
    print("Incorrect map edge length")

_ = input('Ready. Press ENTER to close...')

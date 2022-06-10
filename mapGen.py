#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import math, locale, requests, io, os, subprocess, tqdm
from PIL import Image
requests.urllib3.disable_warnings()
cwd = os.getcwd()

if locale.getdefaultlocale()[0] == 'pl_PL':
    lang = ['mapGen - program pobierający zdjęcia lotnicze (ortofotomapy) i mapy cieniowania terenu dla określonego obszaru\n', 'Nie można wczytać pliku konfiguracyjnego - wprowadź dane ręcznie.', 'Wczytywanie pliku konfiguracyjnego...', '\nKraj: %s, wymiary mapy: %s', 'Kraj (PL/CZ/SK): ', 'Współrzędne granic mapy [w stopniach dziesiętnych]:\n- Północ: ', '- Południe: ', '- Zachód: ', '- Wschód:', 'Wymiary mapy [m]: ',
            '\nWybierz wersję FS, dla której mają być przygotowane tekstury:\n1. FS 22\n2. FS 19 i starsze\n(1/2): ', '\nUwaga: wymiary mapy muszą być równe 2^n', '\nPobieranie danych...', '\n\nKonwersja tekstur terenu do formatu DDS...', '\nZapisywanie PDA i mapy cieniowania terenu...', '\nWciśnij ENTER, aby zamknąć...']
else:
    lang = ['mapGen - orthophotomaps and terrain shading maps downloader for a specific area\n', "Can't load the config file - you must enter your data manually.", 'Config file is loading...', '\nCountry: %s, Map dimensions: %s', 'Country (PL/CZ/SK): ', "Map bounds' coordinates [decimal degrees]:\n- North: ", '- South: ', '- West: ', '- East: ', 'Map dimensions [meters]: ',
            '\nChoose the FS version for which textures will be prepared:\n1. FS 22\n2. FS 19 and older\n(1/2): ', '\nWarning: map dimensions must be equal 2^n', '\nDownloading data...', '\n\nConverting terrain textures to DDS format...', '\nSaving map overview image and terrain shading map...', '\nPress ENTER to close...']

print(lang[0])
use_stdin = True
try:
    config = open("demGenerator_config.txt", "r")
except:
    print(lang[1])
else:
    print(lang[2])
    string = config.read()
    string = string.split()
    country = string[0].upper()
    n = float(string[1])
    s = float(string[2])
    w = float(string[3])
    e = float(string[4])
    l = int(string[5])
    print(lang[3] % (country, l))
    use_stdin = False
    config.close()

if use_stdin:
    country = input(lang[4]).upper()
    n = float(input(lang[5]))
    s = float(input(lang[6]))
    w = float(input(lang[7]))
    e = float(input(lang[8]))
    l = int(input(lang[9]))

if s > n:
    n, s = s, n
if w > e:
    w, e = e, w

while country != "CZ" and country != "PL" and country != "SK":
    country = input(lang[4]).upper()

fs = 0
while fs != 1 and fs != 2:
    fs = int(input(lang[10]))

if math.log2(l) != int(math.log2(l)):
    print(lang[11])
else:
    print(lang[12])

    if (not os.path.exists(cwd + "\\demGen_data\\textures")):
        os.mkdir(cwd + "\\demGen_data\\textures")

    shadmap = Image.new('RGB', (l, l))
    
    l = int(l / 1024)

    if l * 2048 <= 16384:
        pda_im = Image.new('RGB', (l * 2048, l * 2048))
    else:
        pda_im = Image.new('RGB', (16384, 16384))
    
    if (l < 1):
        l = 1
    ortos = []
    # topos = [] (unused var)
    shads = []
    dx = (n - s) / l
    dy = (e - w) / l
    pbar = tqdm.tqdm(total = l ** 2)
    for i in range(l):
        for j in range(l):
            x1 = i * dx + s
            x2 = (i + 1) * dx + s
            y1 = j * dy + w
            y2 = (j + 1) * dy + w
            if country == 'CZ':
                url = "https://geoportal.cuzk.cz/WMS_ORTOFOTO_PUB/service.svc/get?LAYERS=GR_ORTFOTORGB&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=XML&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.031478753454327824&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&WIDTH=2000&HEIGHT=2000"
            elif country == 'SK':
                url = 'https://zbgis.skgeodesy.sk/zbgis/rest/services/Ortofoto/MapServer/export?dpi=96&transparent=true&format=png32&layers=show%3A5%2C6&bbox=' + str(y1) + "," + str(x1) + "," + str(y2) + "," + str(x2) + '&bboxSR=4326&imageSR=102100&size=2043%2C2048&f=image'
            else:
                url = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/StandardResolutionTime?REQUEST=GetMap&TRANSPARENT=TRUE&FORMAT=image%2Fpng&VERSION=1.1.1&LAYERS=Raster&STYLES=&EXCEPTIONS=xml&TIME=2021-12-01T00%3A00%3A00.000%2B01%3A00&BBOX=' + str(y1) + "," + str(x1) + "," + str(y2) + "," + str(x2) + '&SRS=EPSG%3A4326&WIDTH=2048&HEIGHT=2048&SERVICE=WMS'
            ortos.append(url)
            connerr = True
            while connerr:
                try:
                    orto = requests.get(url)
                except:
                    continue
                else:
                    if orto.status_code == 200:
                        connerr = False
                        im = Image.open(io.BytesIO(orto.content))
                        if country != 'PL':
                            im = im.resize((2048, 2048), Image.NEAREST)
                        if l * 2048 <= 16384:
                            pda_im.paste(im, (j * 2048, (l - i - 1) * 2048))
                        else:
                            pda_im.paste(im.resize((16384 / l, 16384 / l), Image.LANCZOS), (j * 16384 / l, (l - i - 1) * 16384 / l))
                        if fs == 1:
                            for k in range(2):
                                for m in range(2):
                                    nr = 2 * (l * (2 * i + k) + j) + m + 1
                                    if nr < 10:
                                        nr = '0%d' % nr
                                    else:
                                        nr = str(nr)
                                    im.crop((m * 1024, (1 - k) * 1024, (m + 1) * 1024, (2 - k) * 1024)).transpose(Image.FLIP_TOP_BOTTOM).save('demGen_data/textures/ortho%s_diffuse.png' % nr, 'PNG')
                        else:
                            nr = i * l + j + 1
                            if nr < 10:
                                nr = '0%d' % nr
                            else:
                                nr = str(nr)
                            im.transpose(Image.FLIP_TOP_BOTTOM).save('demGen_data/textures/ortho%s_diffuse.png' % nr, 'PNG')
                        im.close()
                    del orto

            if country != 'SK':
                if country == "CZ":
                    url = "https://ags.cuzk.cz/arcgis2/services/dmr5g/ImageServer/WMSServer?LAYERS=dmr5g%3AGrayscaleHillshade&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=INIMAGE&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.4763809632942847&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&WIDTH=2048&HEIGHT=2048"
                else:
                    url = "http://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/GRID1/WMS/ShadedRelief?&REQUEST=GetMap&TRANSPARENT=FALSE&FORMAT=image/png&VERSION=1.3.0&LAYERS=Raster&STYLES=&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&CRS=EPSG:4326&EXCEPTIONS=xml&WIDTH=2048&HEIGHT=2048"
                shads.append(url)
                connerr = True
                while connerr:
                    try:
                        shad = requests.get(url)
                    except:
                        continue
                    else:
                        if shad.status_code == 200:
                            connerr = False
                            im = Image.open(io.BytesIO(shad.content))
                            shadmap.paste(im.resize((1024, 1024), Image.LANCZOS), (j * 1024, (l - i - 1) * 1024))
                            im.close()
                        del shad
            pbar.update(1)
            
    print(lang[13])
    if fs == 1:
        subprocess.run(cwd + '\\textureTool -inputs "demGen_data\\textures" -arch dds -format bc7 -numMipmaps 8', stdout = subprocess.DEVNULL)
    else:
        subprocess.run(cwd + '\\texconv.exe -r -f DXT5 -l -o "demGen_data\\textures" "demGen_data\\textures\\*.png"', stdout = subprocess.DEVNULL)

    print(lang[14])
    pda_im.save('demGen_data/mapOverwiev.png', 'PNG')
    shadmap.save('demGen_data/terrainShading.png', 'PNG')

    urllist = open('demGen_data/mapGenURLs.txt', 'w')
    urllist.write('Ortho images:\n')
    for i in range(len(ortos)):
        urllist.write(ortos[i] + '\n')
    if country != 'SK':
        urllist.write('\nTerrain shading maps:\n')
        for i in range(len(shads)):
            urllist.write(shads[i] + '\n')
    urllist.close()
w = input(lang[15])

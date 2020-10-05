#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import math

print("mapGen - orthophotomaps, topographic maps and terrain shading maps downloading for a specific area")
use_stdin = True
try:
    config = open("demGenerator_config.txt", "r")
except:
    print("Can't load the config file - you must enter your data manually.")
else:
    print("Config file is loading...")
    string = config.read()
    string = string.split()
    country = string[0]
    n = float(string[1])
    s = float(string[2])
    w = float(string[3])
    e = float(string[4])
    l = int(string[5])
    print("Country: %s, Map's edge length: %s" % (country, l))
    use_stdin = False
    config.close()

if use_stdin:
    country = input("Country code (PL/CZ/SK): ")
    n = float(input("Map bounds' coordinates [decimal degrees]:\n- North: "))
    s = float(input("- South: "))
    w = float(input("- West: "))
    e = float(input("- East: "))
    l = int(input("Map's edge length: "))

if s > n:
    n, s = s, n
if w > e:
    w, e = e, w

while country != "CZ" and country != "PL" and country != "SK":
    country = input("Re-enter the country code (PL/CZ/SK): ")

if country == 'SK':
    import requests
    requests.urllib3.disable_warnings()
else:
    import urllib.request

if country == 'CZ' or country == 'SK':
    from PIL import Image

if math.log2(l) != int(math.log2(l)):
    print("Error: map's edge length must be equal 2^n")
else:
    print("Downloading data...")
    l = int(l / 1024)
    if (l < 1):
        l = 1
    ortos = []
    topos = []
    shads = []
    dx = (n - s) / l
    dy = (e - w) / l
    for i in range(l):
        for j in range(l):
            x1 = i * dx + s
            x2 = (i + 1) * dx + s
            y1 = j * dy + w
            y2 = (j + 1) * dy + w
            if country == "CZ":
                url = "https://geoportal.cuzk.cz/WMS_ORTOFOTO_PUB/service.svc/get?LAYERS=GR_ORTFOTORGB&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=XML&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.031478753454327824&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&WIDTH=2000&HEIGHT=2000"
            elif country == 'SK':
                url = 'https://zbgis.skgeodesy.sk/zbgis/rest/services/Ortofoto/MapServer/export?dpi=96&transparent=true&format=png32&layers=show%3A5%2C6&bbox=' + str(y1) + "," + str(x1) + "," + str(y2) + "," + str(x2) + '&bboxSR=4326&imageSR=102100&size=2043%2C2048&f=image'
            else:
                url = "http://mapy.geoportal.gov.pl/wss/service/img/guest/ORTO_TIME/MapServer/WMSServer?REQUEST=GetMap&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&LAYERS=Raster&STYLES=&EXCEPTIONS=xml&TIME=2020-01-01T00%3A00%3A00.000%2B01%3A00&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&CRS=EPSG%3A4326&WIDTH=2048&HEIGHT=2048&SERVICE=WMS"
            ortos.append(url)
            connerr = True
            while connerr:
                try:
                    if country == 'SK':
                        orto = requests.get(url)
                    else:
                        orto = urllib.request.urlopen(url)
                except:
                    continue
                else:
                    connerr = False
                    fn = "demGen_data/orto_%d.png" % (i * l + j)
                    if country == 'SK':
                        open(fn, "wb").write(orto.content)
                    else:
                        open(fn, "wb").write(orto.read())
                    orto.close()
                    if country == 'CZ' or country =='SK':
                        im = Image.open(fn)
                        im.resize((2048, 2048), resample = Image.NEAREST).save(fn, 'PNG')
                        im.close()
            if (country != 'SK'):
                if country == "CZ":
                    url = "https://ags.cuzk.cz/arcgis2/services/dmr5g/ImageServer/WMSServer?LAYERS=dmr5g%3AGrayscaleHillshade&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=INIMAGE&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.4763809632942847&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&WIDTH=4096&HEIGHT=4096"
                else:
                    url = "http://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/GRID1/WMS/ShadedRelief?&REQUEST=GetMap&TRANSPARENT=FALSE&FORMAT=image/png&VERSION=1.3.0&LAYERS=Raster&STYLES=&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&CRS=EPSG:4326&EXCEPTIONS=xml&WIDTH=4096&HEIGHT=4096"
                shads.append(url)
                connerr = True
                while connerr:
                    try:
                        shad = urllib.request.urlopen(url)
                    except:
                        continue
                    else:
                        connerr = False
                        open("demGen_data/shad_%d.png" % (i * l + j), "wb").write(shad.read())
                        shad.close()
    urllist = open('demGen_data/mapGenURLs.txt', 'w')
    urllist.write('Orthophotomaps:\n')
    for i in range(len(ortos)):
        urllist.write(ortos[i] + '\n')
    if country != 'SK':
        urllist.write('\nTerrain shading maps:\n')
        for i in range(len(shads)):
        	urllist.write(shads[i] + '\n')
        urllist.close()
w = input("Press ENTER to close...")

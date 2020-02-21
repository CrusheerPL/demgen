#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import urllib.request

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

if (use_stdin):
    country = input("Country code (PL/CZ): ")
    n = float(input("Map bounds' coordinates [decimal degrees]:\n- North: "))
    s = float(input("- South: "))
    w = float(input("- West: "))
    e = float(input("- East: "))
    l = int(input("Map's edge length: "))

if s > n:
    n, s = s, n
if w > e:
    w, e = e, w

while (country != "CZ" and country != "PL"):
    country = input("Re-enter the country code (PL/CZ): ")

if (math.log2(l) != int(math.log2(l))):
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
            if (country == "CZ"):
                url = "https://geoportal.cuzk.cz/WMS_ORTOFOTO_PUB/service.svc/get?LAYERS=GR_ORTFOTORGB&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=XML&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.031478753454327824&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&WIDTH=2000&HEIGHT=2000"
            else:
                url = "http://mapy.geoportal.gov.pl/wss/service/img/guest/ORTO_TIME/MapServer/WMSServer?REQUEST=GetMap&TRANSPARENT=TRUE&FORMAT=image%2Fjpeg&VERSION=1.3.0&LAYERS=Raster&STYLES=&EXCEPTIONS=xml&TIME=2020-01-01T00%3A00%3A00.000%2B01%3A00&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&CRS=EPSG%3A4326&WIDTH=2048&HEIGHT=2048&SERVICE=WMS"
            ortos.append(url)
            connerr = True
            while (connerr):
                try:
                    orto = urllib.request.urlopen(url)
                except:
                    continue
                else:
                    connerr = False
                    open("demGen_data/orto_%d.png" % (i * l + j), "wb").write(orto.read())
                    orto.close()
            if (country == "CZ"):
                url = "https://ags.cuzk.cz/arcgis/services/ZABAGED_TOPO/MapServer/WmsServer?LAYERS=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C182%2C183%2C184%2C185%2C186%2C187%2C19%2C20%2C65%2C66%2C67%2C50%2C49%2C69%2C70%2C71%2C72%2C174%2C175%2C176%2C177%2C178%2C179%2C180%2C181%2C61%2C62%2C21%2C22%2C63%2C64%2C188%2C189%2C190%2C191%2C23%2C24%2C25%2C76%2C77%2C78%2C79%2C73%2C74%2C75%2C133%2C134%2C135%2C30%2C29%2C28%2C26%2C27%2C80%2C81%2C129%2C128%2C119%2C120%2C121%2C122%2C100%2C123%2C101%2C124%2C125%2C126%2C130%2C131%2C132%2C127%2C113%2C114%2C115%2C116%2C117%2C118%2C103%2C104%2C105%2C106%2C107%2C108%2C109%2C110%2C102%2C111%2C112%2C82%2C83%2C84%2C85%2C86%2C96%2C97%2C98%2C99%2C87%2C88%2C89%2C90%2C91%2C92%2C93%2C136%2C31%2C32%2C33%2C34%2C35%2C36%2C37%2C38%2C39%2C40%2C41%2C42%2C43%2C44%2C45%2C51%2C52%2C53%2C54%2C55%2C56%2C57%2C58%2C59%2C60%2C146%2C147%2C148%2C149%2C150%2C151%2C152%2C153%2C154%2C155%2C156%2C157%2C158%2C159%2C160%2C161%2C162%2C163%2C164%2C165%2C166%2C167%2C168%2C169%2C170&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=XML&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.9081247041876277&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&WIDTH=4096&HEIGHT=4096"
            else:
                url = "http://mapy.geoportal.gov.pl/wss/service/img/guest/TOPO_SERIA/MapServer/WMSServer?&REQUEST=GetMap&TRANSPARENT=FALSE&FORMAT=image/png&VERSION=1.3.0&LAYERS=Raster_10_1965&STYLES=&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&CRS=EPSG:4326&EXCEPTIONS=xml&WIDTH=2048&HEIGHT=2048"
            topos.append(url)
            connerr = True
            while (connerr):
                try:
                    topo = urllib.request.urlopen(url)
                except:
                    continue
                else:
                    connerr = False
                    open("demGen_data/topo_%d.png" % (i * l + j), "wb").write(topo.read())
                    topo.close()
            if (country == "CZ"):
                url = "https://ags.cuzk.cz/arcgis2/services/dmr5g/ImageServer/WMSServer?LAYERS=dmr5g%3AGrayscaleHillshade&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=INIMAGE&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.4763809632942847&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&WIDTH=4096&HEIGHT=4096"
            else:
                url = "http://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/GRID1/WMS/ShadedRelief?&REQUEST=GetMap&TRANSPARENT=FALSE&FORMAT=image/png&VERSION=1.3.0&LAYERS=Raster&STYLES=&BBOX=" + str(x1) + "," + str(y1) + "," + str(x2) + "," + str(y2) + "&CRS=EPSG:4326&EXCEPTIONS=xml&WIDTH=4096&HEIGHT=4096"
            shads.append(url)
            connerr = True
            while (connerr):
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
    urllist.write('\nTopographic maps:\n')
    for i in range(len(topos)):
        urllist.write(topos[i] + '\n')
    urllist.write('\nTerrain shading maps:\n')
    for i in range(len(shads)):
        urllist.write(shads[i] + '\n')
    urllist.close()
w = input("Press ENTER to close...")

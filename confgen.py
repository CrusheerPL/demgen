#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import filedialog
from tkinter import *
import os
import math
import locale
import xml.dom.minidom as p

if locale.getdefaultlocale()[0] == 'pl_PL':
    lang = ('Wybierz plik', 'KML', 'Wszystkie pliki', 'Wybierz zestaw współrzędnych:', 'Zestaw współrzędnych: %s', 'Kraj (PL/CZ/SK): ', 'Długość krawędzi mapy [m]: ', 'Rozdzielczość terenu [m/px]: ', 'Ilość kafelków: ', "Wciśnij ENTER aby zamknąć...")
else:
    lang = ('Select file', 'KML files', 'All files', 'Choose the coordinates set:', 'Coordinates set: %s', 'Country (PL/CZ/SK): ', "Map's edge length [m]: ", 'Terrain resolution [m/px]: ', 'Tiles count: ', "Press ENTER to close...")
    
Tk().withdraw()

kmlFn = filedialog.askopenfilename(initialdir = os.getcwd(), title = lang[0], filetypes = ((lang[1],"*.kml"),(lang[2],"*.*")))
coords = p.parse(kmlFn).getElementsByTagName('coordinates')
coordscnf = []

for c in coords:
    cl = c.childNodes[0].nodeValue
    cl = cl.splitlines()
    xs, ys = [], []
    for i in range(len(cl)):
        if cl[i] != '':
            x, y, h = cl[i].split(',')
            xs.append(x)
            ys.append(y)
    coordscnf.append('%s %s %s %s' % (max(ys), min(ys), min(xs), max(xs)))

cnfid = 0

if len(coordscnf) > 1:
    print(lang[3])
    for i in range(1, len(coordscnf) + 1):
        print('%d. %s' % (i, coordscnf[i-1]))
    while not cnfid in range(1, len(coordscnf) + 1):
        cnfid = int(input('(1 - %d): ' % (len(coordscnf))))
    print(lang[4] % coordscnf[cnfid-1])
else:
    print(lang[4] % coordscnf[0])
    cnfid = 1

country = ''
while (country != "CZ" and country != "PL" and country != "SK"):
    country = input(lang[5]).upper()
l = int(input(lang[6]))
res = float(input(lang[7]))
tls = int(input(lang[8]))
while (math.sqrt(tls) != int(math.sqrt(tls))):
    tls = input(lang[8])

open("demGenerator_config.txt", "w").write('%s %s %d %f %d' % (country, coordscnf[cnfid-1], l, res, tls))

_ = input(lang[9])

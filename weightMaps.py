#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
from tkinter import Tk, filedialog
import math, os, locale, pathlib
Tk().withdraw()

if locale.getdefaultlocale()[0] == 'pl_PL':
    lang = ['Program generujący weightmapy', '\nNie można wczytać pliku konfiguracyjnego - wprowadź dane ręcznie.', '\nWczytywanie pliku konfiguracyjnego...', 'Wymiary mapy [m]: ', 'Wybierz folder docelowy z danymi mapy', '\nWybierz wersję FS:\n1. FS 22\n2. FS 19\n3. FS 17 i starsze\n(1-3): ', 'Nieprawidłowa opcja, spróbuj ponownie (1-3): ', '\nTworzenie weight map...', 'Uwaga: nieprawidłowe wymiary mapy', '\nWciśnij ENTER, aby zamknąć...']
else:
    lang = ['Weight maps generator', "\nCan't load the config file - you must enter your data manually.", '\nConfig file is loading...', 'Map dimensions [meters]: ', 'Select target folder with map data', '\nChoose FS version:\n1. FS 22\n2. FS 19\n3. FS 17 and older\n(1-3): ', 'Incorrect option, retry (1-3): ', '\nCreating weight maps...', 'Warning: incorrect map dimensions', '\nPress ENTER to close...']

print(lang[0])
use_stdin = True
try:
    config = open("demGenerator_config.txt", "r")
except:
    print(lang[1])
    l = int(input(lang[3]))
else:
    print(lang[2])
    strin = config.read()
    strin = strin.split()
    l = int(strin[5])
    use_stdin = False
    config.close()

if (l % 1024 == 0):
    target_dir = filedialog.askdirectory(initialdir = os.getcwd(), title = lang[4])
    td = sorted(pathlib.Path(target_dir).glob('*_weight.png'))
    ort = sorted(pathlib.Path(target_dir).glob('ortho*_weight.png'))

    fs = int(input(lang[5]))
    while not 1 <= fs <= 3:
        fs = int(input(lang[6]))

    if fs == 1:
        div = int(l / 512)
    else:
        div = int(l / 1024)

    if fs == 3:
        l = int(l/2)

    print(lang[7])
    
    for i in td:
        if not i in ort:
            Image.new('L', (l, l)).save(i, 'PNG')

    for i in range(div):
        for j in range(div):
            imid = div * i + j + 1
            if imid < 10:
                imid = '0%d' % imid
            else:
                imid = str(imid)
            wm = Image.new('L', (l, l))
            d = ImageDraw.Draw(wm)
            if fs == 2:
                dim = 1024
            else:
                dim = 512
            d.rectangle([(j * dim, (div - i) * dim - 1), ((j + 1) * dim - 1, (div - i - 1) * dim)], 255, width = 0)
            wm.save(target_dir + '\\ortho%s_weight.png' % imid, 'PNG')
else:
    print(lang[8])

_ = input(lang[9])

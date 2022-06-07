#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import locale
import platform
import os

if locale.getdefaultlocale()[0] == 'pl_PL':
    lang = ('Program sprawdzający wymagania demGeneratora\n\nSprawdzanie wersji środowiska Pythona...', 'Wersja: %s.%s.%s - poprawna', '\nPróba zaimportowania modułu "%s"...', 'Nie znaleziono tego modułu - teraz nastąpi jego instalacja.\n--------------------', 'Moduł pomyślnie zaimportowano', 'demGen nie wspiera Pythona w wersji %s.%s.%s. Uruchom go w 3.5 - 3.7.', '\nWciśnij ENTER, aby zamknąć...')
else:
    lang = ('demGen requirements checker\n\nPython version checking...', 'Version: %s.%s.%s - correct', '\nTrying to import the "%s" module...', 'Module not found - it will be installed now.\n--------------------', 'Module imported successfully', 'demGen has no support for Python %s.%s.%s. Run it in the Python 3.5 - 3.7 environment.', '\nPress ENTER to close...')

print(lang[0])
ver = platform.python_version_tuple()
if ver[0] == '3' and ver[1] >= '5' and ver[1] <= '7':
    print(lang[1] % (ver[0], ver[1], ver[2]))
    
    print(lang[2] % 'Pillow')
    success = False
    while not success:
        try:
            import PIL
        except:
            print(lang[3])
            os.system("python -m pip install Pillow --user --no-warn-script-location")
            print('--------------------')
        else:
            print(lang[4])
            success = True

    print(lang[2] % 'tqdm')
    success = False
    while not success:
        try:
            import tqdm
        except:
            print(lang[3])
            os.system("python -m pip install tqdm --user --no-warn-script-location")
            print('--------------------')
        else:
            print(lang[4])
            success = True
    print(lang[2] % 'requests')
    success = False
    while not success:
        try:
            import requests
        except:
            print(lang[3])
            os.system("python -m pip install requests --user --no-warn-script-location")
            print('--------------------')
        else:
            print(lang[4])
            success = True
    """ not now
    if os.path.exists(os.getcwd() + '\\texconv.exe'):
        print(lang[6])
    else:
        print(lang[5])
        import urllib.request as req
        success = False
        while not success:
            try:
                f = req.urlopen('https://github.com/Microsoft/DirectXTex/releases/latest/download/texconv.exe')
            except:
                continue
            else:
                if f.getcode() == 200:
                    open('texconv.exe', 'wb').write(f.read())
                    print(lang[8])
                    success = True
    """
else:
    print(lang[5] % (ver[0], ver[1], ver[2]))
    import webbrowser
    webbrowser.open('www.python.org/downloads/release/python-377/')

_ = input(lang[6])

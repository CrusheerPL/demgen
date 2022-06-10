#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import locale, platform, os, shutil

if locale.getdefaultlocale()[0] == 'pl_PL':
    lang = ('Program sprawdzający wymagania demGeneratora\n\nSprawdzanie wersji środowiska Pythona...', 'Wersja: %s.%s.%s - poprawna', '\nPróba zaimportowania biblioteki "%s"...', '\nNie znaleziono tej biblioteki - teraz nastąpi jego instalacja.\n--------------------', ' SUKCES', '\nSprawdzanie obecności programu Texconv...', '\nNie znaleziono – trwa pobieranie...',
            '\nSprawdzanie obecności programu GIANTS Texture Tool...', '\nSkopiowano do głównego folderu demGeneratora', '\nNie znaleziono - pobierz ZIPa z programem z GIANTS Developer Network, wypakuj go i spróbuj ponownie.', 'demGen nie wspiera Pythona w wersji %s.%s.%s. Uruchom go w 3.5 - 3.7.', '\nWciśnij ENTER, aby zamknąć...')
else:
    lang = ('demGen requirements checker\n\nPython version checking...', 'Version: %s.%s.%s - correct', '\nTrying to import the "%s" library...', 'Library not found - it will be installed now.\n--------------------', ' SUCCESS', '\nChecking the Texconv program presency...', '\nNot found – downloading in progress...',
            '\nChecking the GIANTS Texture Tool presency...', "\nCopied to demGen's main folder", '\nNot found - download ZIP with this program from GIANTS Developer Network, unzip it and retry.', 'demGen has no support for Python %s.%s.%s. Run it in the Python 3.5 - 3.7 environment.', '\nPress ENTER to close...')

print(lang[0])
ver = platform.python_version_tuple()
if ver[0] == '3' and ver[1] >= '5' and ver[1] <= '7':
    print(lang[1] % (ver[0], ver[1], ver[2]))
    
    print(lang[2] % 'Pillow', end = '')
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

    print(lang[2] % 'tqdm', end = '')
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
    print(lang[2] % 'requests', end = '')
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
    print(lang[5], end = '')
    if os.path.exists(os.getcwd() + '\\texconv.exe'):
        print(' OK')
    else:
        print(lang[6])
        import requests
        success = False
        while not success:
            try:
                f = requests.get('https://github.com/Microsoft/DirectXTex/releases/latest/download/texconv.exe')
            except:
                continue
            else:
                if f.status_code == 200:
                    open('texconv.exe', 'wb').write(f.content)
                    print(lang[4])
                    success = True
    print(lang[7], end = '')
    if os.path.exists(os.getcwd() + '\\textureTool.exe') and os.path.exists(os.getcwd() + '\\textureTool.xml'):
        print(' OK')
    else:
        root_dir = ''
        if os.path.exists(os.getcwd() + '\\textureTool.exe') and not os.path.exists(os.getcwd() + '\\textureTool.xml'):
            for root, dirs, files in os.walk('C:\\'):
                if 'textureTool.xml' in files:
                    root_dir = root
        else:
            for root, dirs, files in os.walk('C:\\'):
                if 'textureTool.exe' in files:
                    root_dir = root
        if root_dir == '':
            print(lang[9])
        else:
            shutil.copy(root_dir + '\\textureTool.exe', os.getcwd())
            shutil.copy(root_dir + '\\textureTool.xml', os.getcwd())
            print(lang[8])
else:
    print(lang[10] % (ver[0], ver[1], ver[2]))
    import webbrowser
    webbrowser.open('www.python.org/downloads/release/python-377/')

_ = input(lang[11])

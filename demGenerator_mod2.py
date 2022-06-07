#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
from multiprocessing import Pool
from pathlib import Path
import requests, math, tqdm, ast, locale

def openUrl(url):
    connerr = True
    while (connerr):
        try:
            f = requests.get(url)
        except:
            continue
        else:
            if (f.status_code == 200):
                connerr = False
        s = str(f.content, 'utf-8')
        del f
    return s
    
def getHeightCZ(rqUrl):
    z = ast.literal_eval(openUrl(rqUrl)) # JSON to dictionary
    s = ''
    for x in range(len(z['samples'])):
        s += '%s,' % z['samples'][x]['value']
    return s
    
if __name__ == '__main__':
    if locale.getdefaultlocale()[0] == 'pl_PL':
        lang = ['demGenerator - skrypt 2/3: pobieranie danych wysokościowych\nUWAGA:\n- Wymagane połączenie internetowe.\n- Czas wykonywania tego skryptu zależy od prędkości połączenia i ilości danych do przetworzenia.\n- Uruchamianie tego skryptu nie jest zalecane przy ustawionym połączeniu taryfowym.',
                'Nie można wczytać pliku konfiguracyjnego\nKraj (PL/CZ): ', 'Ilość części (kafelków): ', 'Wczytywanie pliku konfiguracyjnego...', 'Kraj: %s', 'Kraj (PL/CZ): ', 'Pobrać dane dla wszystkich kafelków? (y/n): ', 'Nr kafelka: ', "Nie znaleziono pliku 'xy_%d.txt'\nNr kafelka: ", "\nWspółrzędne wczytane z pliku 'xy_%d.txt'",
                "Uwaga: nieprawidłowa ilość danych wejściowych! Jest: %d. Powinno być: %d. Sprawdź zawartość pliku 'xy_%d.txt' w celu poprawienia błędów.", 'Wymiary kafelka: (%d x %d) px', 'Generowanie adresów z zapytaniami...', 'Serwer pobierania danych: %s', 'Pobieranie danych - ta operacja może zająć trochę czasu...',
                'Uwaga (debug): nieprawidłowa ilość punktów - sprawdź zapytanie #%d', "Dane pobrano i zapisano do pliku 'h_%d.txt'", 'Ten skrypt nie wspiera Pythona w wersji %s.%s.%s. Uruchom go w 3.5 - 3.7.', 'Wciśnij ENTER, aby zamknąć...']
    else:
        lang = ['demGenerator - script 2/3: elevation data downloading\nNOTE:\n- Internet connection required.\n- The script execution time depends on the connection speed and the amount of data to be processed.\n- Running this script with enabled tariff connection is not recommended.',
                "Can't load the config file\nCountry (PL/CZ): ", 'Tiles count: ', 'Config file is loading...', 'Country: %s', 'Country (PL/CZ): ', 'Download data for all tiles? (y/n): ', 'Tile number: ', "'xy_%d.txt' not found\nTile number: ", "\nCoordinates read from 'xy_%d.txt'",
                "Warning: incorrect count of input data! Is: %d. Should be: %d. Check the 'xy_%d.txt' file content for errors correction.", 'Tile size: (%d x %d) px', 'Generating query URLs...', 'Data downloading server: %s', 'Downloading data - this operation may take some time...',
                'Warning (debug): insufficient number of points – check query #%d', "Data downloaded and saved to 'h_%d.txt'", 'This script has no support for Python %s.%s.%s. Run it in the Python 3.5 - 3.7 environment.', 'Press ENTER to close...']
    ver = platform.python_version_tuple()
    if (ver[0] == '3' and ver[1] >= '5' and ver[1] <= '7'):
        print(lang[0])
        try:
            config = open("demGenerator_config.txt", "r")
        except:
            country = input(lang[1])
            div = int(input(lang[2]))
        else:
            print(lang[3])
            cnf = config.read().split()
            country, div = cnf[0], int(cnf[7])
            print(lang[4] % country)
        while (country != "CZ" and country != "PL"):
            country = input(lang[5])
        
        if country == 'PL':
            print(lang[13] % 'services.gugik.gov.pl/nmt')
        else:
            print(lang[13] % 'ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer')
            
        tiles = []
        alltiles = '0'
        
        while not alltiles.isalpha() or (alltiles.isalpha() and (alltiles.lower() != 'y' and alltiles.lower() != 'n')):
            alltiles = input(lang[6])
        if alltiles.lower() == 'n':
            tile = int(input(lang[7]))
            while not Path("demGen_data/xy_%d.txt" % tile).exists():
                tile = int(input(lang[8] % tile))
            tiles.append(tile)
        else:
            for i in range(div):
                if Path("demGen_data/xy_%d.txt" % i).exists():
                    tiles.append(i)

        for part in tiles:
            data = open("demGen_data/xy_%d.txt" % part)
            i = 0
            we = []
            while True:
                string = data.readline()
                tab = string.split()
                if len(tab) != 0:
                    we.append([float(tab[0]), float(tab[1])])
                    i += 1
                else:
                    break
            data.close()
            print(lang[9] % part)
            l = int(math.floor(math.sqrt(i)))
            if math.pow(l, 2) != i:
                print(lang[10] % (i, math.pow(l, 2), part))
                del we
            else:
                print(lang[11] % (l, l))
                hstr = []
                wy = []
                
                print(lang[12])
                rqs = []
                if country == 'CZ':
                    jm = 37.0
                else:
                    jm = 200.0
                jmax = int(math.ceil(len(we) / jm))
                with tqdm.tqdm(total=jmax) as pbar:
                    for j in range(jmax):
                        if country == 'CZ':
                            url = 'https://ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer/getSamples?geometry=%7Bpoints%3A%5B'
                        elif country == 'PL':
                            url = 'https://services.gugik.gov.pl/nmt/?request=GetHbyXY&xy='
                        for k in range(int(jm) * j, int(jm) * (j + 1)):
                            if k >= len(we):
                                break
                            if country == 'CZ':
                                url += '%5B' + str(-we[k][0]) + '%2C' + str(-we[k][1]) + '%5D'
                                if k < jm * (j + 1) - 1:
                                    url += '%2C'
                            elif country == 'PL':
                                url += str(we[k][1]) + '%20' + str(we[k][0]) + ','
                        if country == 'CZ':
                            url += '%5D%2CspatialReference%3A%7Bwkid%3A5514%7D%7D&geometryType=esriGeometryMultipoint&sampleDistance=&sampleCount=&mosaicRule=&pixelSize=&returnFirstValueOnly=false&f=pjson'
                        rqs.append(url)
                        pbar.update(1)
                rqlist = open('demGen_data/requestsList_%d.txt' % part, 'w')
                for j in range(len(rqs)):
                    rqlist.write(rqs[j] + '\n')
                rqlist.close()

                # Elevation data downloading
                if country == "CZ":
                    print(lang[14])
                    with Pool(32) as p:
                        hstr = list(tqdm.tqdm(p.imap(getHeightCZ, rqs), total=len(rqs)))
                elif country == "PL":
                    print(lang[14])
                    with Pool(32) as p:
                        hstr = list(tqdm.tqdm(p.imap(openUrl, rqs), total=len(rqs))) # openUrl instead of getHeightPL

                for j in range(len(hstr)):
                    h2str = hstr[j].split(',')
                    if len(h2str) < jm and j != len(hstr) - 1:
                        print(lang[15] % (j + 1))
                    for k in range(len(h2str)):
                        if k < jm: # warunek
                            wy.append(h2str[k])
                output = open("demGen_data/h_%d.txt" % part, "w")
                for j in range(len(wy)):
                    output.write(str(wy[j]) + "\n") # dane uporządkowane
                output.close()
                del we, wy, hstr
                print(lang[16] % part)
    else:
        print(lang[17] % (ver[0], ver[1], ver[2]))
    w = input(lang[18])

#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import platform
from multiprocessing import Pool
from pathlib import Path
import urllib.request
import math
import tqdm
import ast
    
def openUrl(url):
    connerr = True
    while (connerr):
        try:
            f = urllib.request.urlopen(url)
        except:
            continue
        else:
            if (f.getcode() == 200):
                connerr = False
        s = str(f.read(), 'utf-8')
        f.close()
    return s
    
def getHeightCZ(rqUrl):
    z = ast.literal_eval(openUrl(rqUrl)) # JSON to dictionary
    s = ''
    for x in range(len(z['samples'])):
        s += '%s,' % z['samples'][x]['value']
    return s
    
if __name__ == '__main__':
    ver = platform.python_version_tuple()
    if (ver[0] == '3' and ver[1] >= '5' and ver[1] <= '7'):
        print("demGenerator - Module 2: elevation data downloading\nNOTE:\n- Internet connection required.\n- The script execution time depends on the connection speed and the amount of data to be processed.\n- Due to high data consumption, it is not recommended to run it when the tariff connection is set.")
        try:
            config = open("demGenerator_config.txt", "r")
        except:
            country = input("Can't load the config file\nCountry code (PL/CZ): ")
        else:
            print("Config file is loading...")
            country = config.read()
            country = country.split()[0]
            print("Country: %s" % country)
        while (country != "CZ" and country != "PL"):
            country = input("Re-enter the country code (PL/CZ): ")

        part = int(input("Tile number: "))
        while (not Path("demGen_data/xy_%d.txt" % part).exists()):
            part = int(input("'xy_%d.txt' doesn't exist - re-enter the tile number: " % part))
        data = open("demGen_data/xy_%d.txt" % part)
        i = 0
        we = []
        while ("true"):
            string = data.readline()
            tab = string.split()
            if (len(tab) != 0):
                we.append([float(tab[0]), float(tab[1])])
                i += 1
            else:
                break
        data.close()
        print("Coordinates were read from 'xy_%d.txt'" % part)
        l = int(math.floor(math.sqrt(i)))
        if (math.pow(l, 2) != i):
            print("Incorrect count of input data! Is: %d. Should be: %d. Check the 'xy_%d.txt' file ontent and correct the mistakes." % (i, math.pow(l, 2), part))
            del we
        else:
            print("Tile size: (%d x %d) px" % ((l, l)))
            hstr = []
            wy = []
            
            print("Generating query URLs...")
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
                        if (k >= len(we)):
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
            rqlist = open('demGen_data/requestsList.txt', 'w')
            for j in range(len(rqs)):
                rqlist.write(rqs[j] + '\n')
            rqlist.close()
            
            # Elevation data downloading
            if (country == "CZ"):
                print("Downloading data from 'ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer'...\nThis operation may take some time.")
                with Pool(64) as p:
                    hstr = list(tqdm.tqdm(p.imap(getHeightCZ, rqs), total=len(rqs)))
            elif (country == "PL"):
                print("Downloading data from 'services.gugik.gov.pl/nmt'...\nThis operation may take some time.")
                with Pool(64) as p:
                    hstr = list(tqdm.tqdm(p.imap(openUrl, rqs), total=len(rqs))) # openUrl instead of getHeightPL

            for j in range(len(hstr)):
                h2str = hstr[j].split(',')
                if len(h2str) < jm and j != len(hstr) - 1:
                    print('Insufficient number of points – see query #%d' % (j + 1))
                for k in range(len(h2str)):
                    if k < jm:
                        wy.append(h2str[k])
            output = open("demGen_data/h_%d.txt" % part, "w")
            for j in range(len(wy)):
                output.write(str(wy[j]) + "\n") # dane uporządkowane
            output.close()
            del we, wy, hstr
            print("Elevation data downloaded and saved in 'h_%d.txt'." % part)
    else:
        print("This script has no support for Python %s.%s.%s. Run it in the Python 3.5 - 3.7 environment." % (ver[0], ver[1], ver[2]))
    w = input("Press ENTER to close...")

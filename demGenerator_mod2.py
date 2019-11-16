#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool
from pathlib import Path
import urllib.request
import math
import tqdm

def getHeightCZ(data_tab):
    connerr = True
    while (connerr):
        try:
            f = urllib.request.urlopen("https://ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer/identify?geometry={x:-" + str(data_tab[0]) + ",y:-" + str(data_tab[1]) + ",spatialReference:{wkid:5514}}&geometryType=esriGeometryPoint&mosaicRule=&renderingRule=&pixelSize=&time=&returnGeometry=false&returnCatalogItems=false&f=pjson")
        except:
            continue
        else:
            if (f.getcode() == 200):
                    connerr = False
    z = str(f.read())
    f.close()
    z = z.split('"')[9]
    if z != "NoData":
        return float(z)
    else:
        return 0

def getHeightPL(data_tab):
    z = 0
    z_tries = 1
    while (z == 0 and z_tries <= 3):
        connerr = True
        while (connerr):
            try:
                f = urllib.request.urlopen("https://services.gugik.gov.pl/nmt/?request=GetHbyXY&x=" + str(data_tab[0]) + "&y=" + str(data_tab[1]))
            except:
                continue
            else:
                if (f.getcode() == 200):
                    connerr = False
        z = float(f.read())
        f.close()
        if (z == 0):
            z_tries += 1
    return z

if __name__ == '__main__':
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
        if (country == "CZ"):
            print("Downloading data from 'ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer'...")
            with Pool(64) as p:
                wy = list(tqdm.tqdm(p.imap(getHeightCZ, we), total=len(we)))
            output = open("demGen_data/h_%d.txt" % part, "w")
            for j in range(len(wy)):
                output.write(str(wy[j]) + "\n") # dane uporządkowane
            output.close()
            del we, wy
        elif (country == "PL"):
            print("Downloading data from 'services.gugik.gov.pl/nmt'...")
            with Pool(64) as p:
                wy = list(tqdm.tqdm(p.imap(getHeightPL, we), total=len(we)))
            output = open("demGen_data/h_%d.txt" % part, "w")
            for j in range(len(wy)):
                output.write(str(wy[j]) + "\n") # dane uporządkowane
            output.close()
            del we, wy
        print("Elevation data downloaded and saved in 'h_%d.txt'." % part)
    w = input("Press ENTER to close...")

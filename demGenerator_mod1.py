#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import numbers
import math
import os

"""
Original JS code from: https://www.pecina.cz/krovak.html
Author: Tomáš Pecina
E-mail: tomas@pecina.cz
To Python3 translated by: RusheerPL – 2019-11-14
"""
def wgs84_to_sjtsk(B, L, H):
    d2r = math.pi / 180
    a = 6378137.0
    f1 = 298.257223563
    dx = -570.69
    dy = -85.69
    dz = -462.84
    wx = 4.99821 / 3600 * math.pi / 180
    wy = 1.58676 / 3600 * math.pi / 180
    wz = 5.2611 / 3600 * math.pi / 180
    m  = -3.543e-6

    B *= d2r
    L *= d2r

    e2 = 1 - math.pow(1 - 1 / f1, 2)
    rho = a / math.sqrt(1 - e2 * math.pow(math.sin(B), 2))
    x1 = (rho + H) * math.cos(B) * math.cos(L)
    y1 = (rho + H) * math.cos(B) * math.sin(L)
    z1 = ((1 - e2) * rho + H) * math.sin(B)

    x2 = dx + (1 + m) * (x1 + wz * y1 - wy * z1)
    y2 = dy + (1 + m) * (-wz * x1 + y1 + wx * z1)
    z2 = dz + (1 + m) * (wy * x1 - wx * y1 + z1)

    a = 6377397.15508
    f1 = 299.152812853

    ab = f1 / (f1 - 1)
    p = math.sqrt(math.pow(x2, 2) + math.pow(y2, 2))
    e2 = 1 - math.pow(1 - 1 / f1, 2)
    th = math.atan(z2 * ab / p)
    st = math.sin(th)
    ct = math.cos(th)
    t = (z2 + e2 * ab * a * math.pow(st, 3)) / (p - e2 * a * math.pow(ct, 3))

    B = math.atan(t)
    H = math.sqrt(1 + math.pow(t, 2)) * (p - a / math.sqrt(1 + (1 - e2) * math.pow(t, 2)))
    L = 2 * math.atan(y2 / (p + x2))

    a = 6377397.15508
    e = 0.081696831215303
    n = 0.97992470462083
    rho0 = 12310230.12797036
    sinUQ = 0.863499969506341
    cosUQ = 0.504348889819882
    sinVQ = 0.420215144586493
    cosVQ = 0.907424504992097
    alpha  = 1.000597498371542
    k2 = 1.00685001861538

    sinB = math.sin(B)
    t = (1 - e * sinB) / (1 + e * sinB)
    t = math.pow(1 + sinB, 2) / (1 - math.pow(sinB, 2)) * math.exp(e * math.log(t))
    t = k2 * math.exp(alpha * math.log(t))

    sinU = (t - 1) / (t + 1)
    cosU = math.sqrt(1 - math.pow(sinU, 2))
    V = alpha * L
    sinV = math.sin(V)
    cosV = math.cos(V)
    cosDV = cosVQ * cosV + sinVQ * sinV
    sinDV = sinVQ * cosV - cosVQ * sinV
    sinS = sinUQ * sinU + cosUQ * cosU * cosDV
    cosS = math.sqrt(1 - math.pow(sinS, 2))
    sinD = sinDV * cosU / cosS
    cosD = math.sqrt(1 - math.pow(sinD, 2))

    eps = n * math.atan(sinD / cosD)
    rho = rho0 * math.exp(-n * math.log((1 + sinS) / cosS))

    CX = rho * math.sin(eps)
    CY = rho * math.cos(eps)

    return CX, CY


"""
Original C++ code from:  :
    Author: Zbigniew Szymanski
    E-mail: z.szymanski@szymanski-net.eu
    Version: 1.1 
    Changelog (PL):
                    1.1 dodano przeksztalcenie odwrotne PUWG 1992 ->WGS84
                    1.0 przeksztalcenie WGS84 -> PUWG 1992
    Data modyfikacji: 2012-11-27
    Uwagi: Oprogramowanie darmowe. Dozwolone jest wykorzystanie i modyfikacja 
           niniejszego oprogramowania do wlasnych celow pod warunkiem 
           pozostawienia wszystkich informacji z naglowka. W przypadku 
           wykorzystania niniejszego oprogramowania we wszelkich projektach
           naukowo-badawczych, rozwojowych, wdrozeniowych i dydaktycznych prosze
           o zacytowanie nastepujacego artykulu:
       
           Zbigniew Szymanski, Stanislaw Jankowski, Jan Szczyrek, 
           "Reconstruction of environment model by using radar vector field histograms.",
           Photonics Applications in Astronomy, Communications, Industry, and 
           High-Energy Physics Experiments 2012, Proc. of SPIE Vol. 8454, pp. 845422 - 1-8,
           doi:10.1117/12.2001354
       
    Literatura:
           Uriasz, J., “Wybrane odwzorowania kartograficzne”, Akademia Morska w Szczecinie,
           http://uriasz.am.szczecin.pl/naw_bezp/odwzorowania.html
           
To Python3 translated by: RusheerPL – 2019-10-27
"""
def wgs84_do_puwg92(B_stopnie, L_stopnie):
    # konwersja współrzednych z układu WGS 84 do układu PUWG 1992
    # Parametry elipsoidy GRS-80
    e = 0.0818191910428     # pierwszy mimośród elipsoidy
    R0 = 6367449.14577      # promień sfery Lagrange'a
    Snorm = 0.000002        # parametr normujący
    xo = 5760000.0          # parametr centrujący

    # Współczynniki wielomianu
    a0 = 5765181.11148097
    a1 = 499800.81713800
    a2 = -63.81145283
    a3 = 0.83537915
    a4 = 0.13046891
    a5 = -0.00111138
    a6 = -0.00010504

    # Parametry odwzorowania Gaussa-Kruegera dla układu PUWG92
    L0_stopnie = 19.0       # Początek układu współrzędnych PUWG92 (długość)
    m0 = 0.9993
    x0 = -5300000.0
    y0 = 500000.0
    
    B = B_stopnie * math.pi / 180.0
    dL = (L_stopnie - 19.0) * math.pi / 180.0

    # etap I - elipsoida na kulę
    U = 1.0 - e * math.sin(B)
    V = 1.0 + e * math.sin(B)
    K = math.pow((U / V),(e / 2.0))
    C = K * math.tan(B / 2.0 + math.pi / 4.0)
    fi = 2.0 * math.atan(C) - math.pi / 2.0
    d_lambda = (L_stopnie - 19.0) * math.pi / 180.0

    # etap II - kula na walec
    p = math.sin(fi)
    q = math.cos(fi) * math.cos(d_lambda)
    r = 1.0 + math.cos(fi) * math.sin(d_lambda)
    s = 1.0 - math.cos(fi) * math.sin(d_lambda)
    XMERC = R0 * math.atan(p/q)
    YMERC = 0.5 * R0 * math.log(r/s)

    # etap III - walec na płaszczyznę
    Z = complex((XMERC - xo) * Snorm, YMERC * Snorm)
    Zgk = complex(a0+Z*(a1+Z*(a2+Z*(a3+Z*(a4+Z*(a5+Z*a6))))))
    Xgk = Zgk.real
    Ygk = Zgk.imag

    Xpuwg = m0 * Xgk + x0
    Ypuwg = m0 * Ygk + y0
    return Xpuwg, Ypuwg


if __name__ == '__main__':
    print("demGenerator - Module 1: determining the coordinates")
    use_stdin = True
    try:
        config = open("demGenerator_config.txt", "r")
    except:
        print("Can't load the config file - you must enter your data manually.")
    else:
        print("Config file is loading...")
        string = config.read()
        country, n, s, w, e, l, d, div = string.split()
        print("Country: %s, B(min): %s, B(max): %s, L(min): %s, L(max): %s\nMap's dimensions: %s x %s, resolution: %s m/px, %s tile(s)" % (country, s, n, w, e, l, l, d, div))
        use_stdin = False
        print("Data has been read, data processing in progress...")
    
    if (use_stdin):
        country = input("Country code (PL/CZ): ")
        n = input("Map bounds' coordinates [decimal degrees]:\n- North: ")
        s = input("- South: ")
        w = input("- West: ")
        e = input("- East: ")
        l = input("Map edge length [meters]: ")
        d = input("Resolution [meters per pixel]: ")
        div = input("Tiles count (2^n): ")
        print("Data processing in progress...")

    while (country != "CZ" and country != "PL"):
        country = input("Re-enter the country code (PL/CZ): ")

    n = float(n)
    s = float(s)
    w = float(w)
    e = float(e)
    l = int(l)
    d = int(d)
    div = int(div)

    while (math.sqrt(div) != int(math.sqrt(div))):
        div = input("Re-enter the tiles count (must be equal to 2^n): ")
    div = int(math.sqrt(div))

    if (l % (d * div) == 0):
        if (not os.path.exists(os.getcwd() + "\\demGen_data")):
            os.mkdir(os.getcwd() + "\\demGen_data")
        l /= d

        dr = n - s # różnica szerokości geogr.
        dl = e - w # różnica długości geogr.

        if (country == "CZ"):
            if (n >= 47.73 and n <= 51.06 and s >= 47.73 and s <= 51.06 and w >= 12.09 and w <= 22.56 and e >= 12.09 and e <= 22.56):
                for x_iter in range(div):
                    for y_iter in range(div):
                        filename = "demGen_data/xy_" + str(div * x_iter + y_iter) + ".txt"
                        data = open(filename, "w")
                        for i in range(int(x_iter * l / div), int((x_iter + 1) * l / div + 1)):
                            for j in range(int(y_iter * l / div), int((y_iter + 1) * l / div + 1)):
                                wsp1 = s + i * dr / l # szerokość geograficzna B (układ WGS84)
                                wsp2 = w + j * dl / l # długość geograficzna L (układ WGS84)
                                x_sjtsk, y_sjtsk = wgs84_to_sjtsk(wsp1, wsp2, 89.79)
                                data.write(str(x_sjtsk) + " " + str(y_sjtsk) + "\n")
                        data.close()
            else:
                print("Coordinates out of range")
        elif (country == "PL"):
            if (n >= 48 and n <= 56 and s >= 48 and s <= 56 and w >= 13 and w <= 25 and e >= 13 and e <= 25):
                for x_iter in range(div):
                    for y_iter in range(div):
                        filename = "demGen_data/xy_" + str(div * x_iter + y_iter) + ".txt"
                        data = open(filename, "w")
                        for i in range(int(x_iter * l / div), int((x_iter + 1) * l / div + 1)):
                            for j in range(int(y_iter * l / div), int((y_iter + 1) * l / div + 1)):
                                wsp1 = s + i * dr / l # szerokość geograficzna B (układ WGS84)
                                wsp2 = w + j * dl / l # długość geograficzna L (układ WGS84)
                                x_puwg, y_puwg = wgs84_do_puwg92(wsp1, wsp2)
                                data.write(str(x_puwg) + " " + str(y_puwg) + "\n")
                        data.close()
            else:
                print("Coordinates out of range")
    else:
        print("Incorrect input data (map edge length or resolution)")
    w = input("Press ENTER to close...")

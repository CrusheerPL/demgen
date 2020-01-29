from PyQt5.QtWidgets import QInputDialog
import math

k, v = QInputDialog().getText(None, "Input", "Enter the 'demGen_data' directory path:")

if v and k != '':
    rlayer = iface.activeLayer()
    data = open(k + '/xy_0.txt', 'r')
    res = open(k + '/h_0.txt', 'w')
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
    print('Coordinates were read.')
    l = int(math.floor(math.sqrt(i)))
    if (math.pow(l, 2) != i):
        print("Incorrect count of input data! Is: %d. Should be: %d. Check the 'xy_0.txt' file ontent and correct the mistakes." % (i, math.pow(l, 2), part))
        del we
    else:
        print("Tile size: (%d x %d) px\nElevation data reading in progress - this operation may take some time." % ((l, l)))
        for i in range(len(we)):
            ident = rlayer.dataProvider().identify(QgsPointXY(-we[i][0], -we[i][1]), QgsRaster.IdentifyFormatValue)
            res.write('%f\n' % ident.results()[1])
        print("Ready – elevation data saved in 'h_0.txt'.")
    res.close()
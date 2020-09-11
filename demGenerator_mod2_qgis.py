from qgis.PyQt.QtWidgets import QFileDialog
import math, os

indir = QFileDialog.getExistingDirectory(iface.mainWindow(), "Select the demGen's input data directory")
if indir != '':
    rlayer = iface.activeLayer()
    if rlayer != None:
        fns = []
        for i in os.listdir(path = indir):
            if 'xy_' in i: fns.append(i)
        for fn in fns:
            data = open('%s/%s' % (indir, fn), 'r')
            res = open('%s/h_%s' % (indir, fn[3:]), 'w')
            i = 0
            we = []
            while True:
                string = data.readline()
                tab = string.split()
                if len(tab) != 0:
                    we.append([float(tab[0]), float(tab[1])])
                    i += 1
                else: break
            data.close()
            print('%s: input data read successfully' % fn)
            l = int(math.floor(math.sqrt(i)))
            if math.pow(l, 2) != i:
                print("Incorrect count of input data! Is: %d. Should be: %d. Check the '%s' file content and correct the mistakes." % (i, math.pow(l, 2), fn))
                del we
            else:
                print("Tile size: (%d x %d) px\nElevation data reading..." % ((l, l)))
                for i in range(len(we)):
                    ident = rlayer.dataProvider().identify(QgsPointXY(-we[i][0], -we[i][1]), QgsRaster.IdentifyFormatValue)
                    if ident.results()[1] != None:
                        res.write('%f\n' % ident.results()[1])
                    else:
                        res.write('0\n')
                print("Ready – elevation data saved to 'h_%s' file" % fn[3:])
            res.close()

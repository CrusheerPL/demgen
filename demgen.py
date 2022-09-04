"""
demgen app
Author: CrusheerPL
Date released:
  - v1.0: 2022-07-31

CHANGELOG
PL
v1.0:
- wszystkie skrypty z interfejsem konsoli złączone w jedną prostą aplikację z interfejsem graficznym Tk
- dodanie obsługi terenów "pod kątem"
- dodanie możliwości odczytu i zapisu pliku XML z konfiguracją z/do dowolnego folderu
- dodanie możliwości wyboru lokalizacji, w której zapisywane mają być pliki
- dodanie funkcji generowania pliku KML z płaszczyzną wyznaczającą określony obszar
- zmiana sposobu pozyskiwania wszelkich danych wysokościowych

EN
v1.0:
- all scripts with console interface combined into one simple app with Tk GUI
- added ability to "rotate" the target area, load/save XML file w/ configration and select the output directory
- added ability to open specially prepared KML file with a plane that delimits a specific area
- changed elevation data collecting method
"""

from tkinter import filedialog, messagebox, ttk
from tkinter import *
from pathlib import Path
from PIL import Image, ImageDraw
from scipy import interpolate
from lxml import etree as et
from ctypes import windll
import gc, geotiff, io, locale, logging, math, multiprocessing, numpy, os, pyproj, re, requests, shutil, string, subprocess, sys, threading, webbrowser
try:
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass
requests.urllib3.disable_warnings()

# zwróć zawartość strony o danym adresie
# postrq - jeśli True, wyśle żądanie metodą POST, w przeciwnym wypadku - metodą GET
# rqdata - dane do realizacji żądania metodą POST
# jsonout - jeśli True, zwróć dane w formie słownika JSON
def openUrl(url, postrq = False, rqdata = {}, jsonout = False, isST = False):
    connerr = True
    s = None
    while connerr:
        try:
            if not postrq:
                f = requests.get(url)
            else:
                f = requests.post(url, data=rqdata)
        except:
            continue
        else:
            if f.status_code == 200:
                connerr = False
                if jsonout:
                    s = f.json()
                else:
                    s = f.content
            del f
    return s

def exportImg(url):
    with Image.open(io.BytesIO(openUrl(url, isST = True))) as img:
        img.load()
        return img.resize((2048,2048), resample = Image.Resampling.LANCZOS)

# to samo co powyżej, ale bez dodatkowej obróbki
def exportImg2(url):
    with Image.open(io.BytesIO(openUrl(url, isST = True))) as img:
        img.load()
        return img

# Original JS code by Tomáš Pecina (tomas@pecina.cz), source: https://www.pecina.cz/krovak.html
# To Python3 translated by crpl – 2019-11-14
def wgs84_to_sjtsk(B, L, H = 89.79):
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
    return -CX, -CY

# get StoppableThread ID
def getSTID(thr):
    stthr = []
    for i in threading.enumerate():
        if i.__class__.__name__ == 'StoppableThread': stthr.append(i)
    return stthr.index(thr)

# https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread
class StoppableThread(threading.Thread):
    # Thread class with a stop() method. The thread itself has to check
    # regularly for the stopped() condition.
    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class dgGUI:
    def __init__(self):
        self.master = Tk()
        self.master.title('demgen')
        self.master.resizable(0, 0)
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)
        self.master.iconbitmap(default = os.path.join(application_path, 'favicon.ico'))

        # tłumaczenie
        # translation
        if locale.getdefaultlocale()[0] == 'pl_PL':
            self.lang = (('Ścieżka do konfiguracji', 'Wybierz plik z konfiguracją', 'Pliki %s', 'Wszystkie pliki'), ('Kraj:', 'Polska', 'Czechy', 'Słowacja'),
                         ('Współrzędne centralnego punktu mapy', 'Szerokość geograficzna:', 'Długość geograficzna:'),
                         ('Parametry terenu', 'Wymiary:', 'Rozdzielczość:', 'Kąt obrotu (CW):'), 'Ilość kafelków: %d', ('Zapisz dane do folderu:', 'Wybierz folder', 'Zapisz'),
                         ('Zapisz konfigurację', 'Otwórz KML', 'Pobierz dane wysokościowe', 'Generuj DEM', 'Generuj modele 3D terenu', 'Pomoc', 'Wybierz...'),
                         ('Tworzenie tekstur terenu', 'Wybierz wersję:', 'Pobierz:', 'zdjęcia lotnicze', 'cieniowanie terenu', 'Pobierz zdjęcia', 'Generuj weightmapy'),
                         ('Postęp operacji', 'Anuluj', 'Czy chcesz anulować bieżącą operację?'),
                         ('Uwaga', 'Nieprawidłowe dane wejściowe (%s)', 'wymiary terenu lub jego rozdzielczość', 'Współrzędne poza zakresem:\n%s ⩽ B ⩽ %s, %s ⩽ L ⩽ %s.', 'Nie podano pliku wejściowego.\nOperacja została przerwana.',
                          'Nie znaleziono plików z danymi wysokościowymi.', 'Nieprawidłowa ilość plików z danymi wysokościowymi.\nJest: %d. Powinno być: %d. Operacja została przerwana.', 'Nie podano folderu docelowego.\nOperacja została przerwana.',
                          'Nie można wczytać pliku z konfiguracją (%s), gdyż zawiera błędy.', "Szczegóły w pliku 'demgen_log.txt'.", "Tekstury nie mogą być przekonwertowane przez brak wymaganego narzędzia GIANTS Texture Tool. Pobrane obrazy png zostaną przeniesione do folderu 'textures_png'."),
                         ('Zbieranie potrzebnych informacji', 'Generowanie zestawów współrzędnych', 'Generowanie listy punktów', 'Pobieranie obrazu GeoTIFF', 'Odczytywanie danych', 'Zapisywanie', 'Dane wysokościowe zostały pobrane.',
                          'DEM został utworzony i zapisany.', 'Statyczne modele 3D terenu zostały utworzone i zapisane.', 'Wybierz plik GeoTIFF z danymi wysokościowymi'),
                         ('Generowanie adresów URL zdjęć', 'Pobieranie zdjęć', 'Obróbka zdjęć', 'Zapisywanie PDA', 'Zapisywanie mapy cieniowania terenu', 'Konwersja tekstur do formatu DDS', 'Zdjęcia i/lub tekstury zostały zapisane.', 'Nic nie pobrano.', 'Wybierz folder docelowy z danymi mapy', 'Zapisywanie weightmap, proszę czekać...', 'Weightmapy zostały zapisane w folderze docelowym.'))
        else:
            self.lang = (('Configuration path', 'Select configuration file', '%s files', 'All files'), ('Country:', 'Poland', 'Czechia', 'Slovakia'),
                         ('Central point coordinates', 'Latitude:', 'Longitude:'),
                         ('Terrain parameters', 'Dimensions:', 'Resolution:', 'Rotation (CW):'), 'Tiles count: %d', ('Save data to folder:', 'Select output directory', 'Save'),
                         ('Save configration', 'Open KML', 'Collect elevation data', 'Generate DEM', 'Generate 3D objects w/ landform', 'Help', 'Select...'),
                         ('Terrain textures creating', 'Select FS version:', 'Download:', 'aerial imagery', 'hillshade', 'Download imagery', 'Generate weightmaps'),
                         ('Operation progress', 'Cancel', 'Are you sure to cancel this operation?'),
                         ('Warning', 'Incorrect input data (%s)', 'terrain dimensions or resolution', 'Coordinates out of range:\n%s ⩽ B ⩽ %s, %s ⩽ L ⩽ %s.', 'Input file not specified.\nThis operation has been aborted.',
                          'No files with elevation data found.', 'Incorrect count of files with elevation data.\nThere are %d files. Should be: %d. This operation has been aborted.', 'Destination directory not specified.\nThis operation has been aborted.',
                          'Unable to read config file (%s) because it contains errors.', "Details in the 'demgen_log.txt' file.", "Textures cannot be converted due to missing required GIANTS Texture Tool in the current working directory. Moving all png images to 'textures_png' directory."),
                         ('Collecting necessary information', 'Generating coordinates sets', 'Generating point list', 'Downloading GeoTIFF image', 'Reading data', 'Saving', 'Elevation data has been saved.',
                          'DEM has been saved.', '3D objects with landform have been saved.', 'Select GeoTIFF image with elevation data'),
                         ('Generating imagery URLs', 'Downloading imagery', 'Editing imagery', 'Saving PDA image', 'Saving hillshade image', 'Converting textures to DDS format', 'Imagery and/or textures have been saved.', 'Nothing has been downloaded.', 'Select destination directory with map data', 'Saving weightmaps - please wait...', 'Weightmaps have been saved in the destination directory.'))

        # początkowe parametry
        # initial parameters
        self.prWindows = []
        self.cnfFn = ''
        self.dgDataPath = ''
        self.country = 'PL'
        self.latitude = 0.0
        self.longitude = 0.0
        self.mapdim = 2048
        self.terres = 2.0
        self.angle = 0
        self.tiles = 1
        self.coordsSet = [[0, 0], [0, 0], [0, 0], [0, 0]] # [nw, ne, se, sw]
        self.canItDoThat = True

        self.tlsVar = StringVar()
        self.tlsVar.set(self.tiles)
        self.fn1Var = StringVar()
        self.fn2Var = StringVar()
        ttk.Style().configure('TButton', width = 0, padding = '5 1')

	# GUI: ramki
        # GUI: frames
        self.loadFrame = ttk.Frame(self.master, padding = '15 15 15 5')
        self.cnf1Frame = ttk.Frame(self.master, padding = '0 5 0 10')
        self.cnf23Frame = ttk.Frame(self.master, height = 500, padding = '15 0 15 5')
        self.cnf2Frame = ttk.LabelFrame(self.cnf23Frame, text = self.lang[2][0], padding = '5 0', labelanchor = 'n')
        self.cnf2aFrame = ttk.Frame(self.cnf2Frame, padding = '0 10 0 10')
        self.cnf2bFrame = ttk.Frame(self.cnf2Frame, padding = '0 10 0 10')
        self.cnfTerFrame = ttk.LabelFrame(self.cnf23Frame, text = self.lang[3][0], padding = '5 0 5 5', labelanchor = 'n')
        self.cnf3Frame = ttk.Frame(self.cnfTerFrame, padding = '0 4')
        self.cnf4Frame = ttk.Frame(self.cnfTerFrame, padding = '0 4')
        self.cnf5Frame = ttk.Frame(self.cnfTerFrame, padding = '0 4')
        self.l9 = ttk.Label(self.master, text = self.lang[4] % self.tiles, padding = '0 5')
        self.cnf7Frame = ttk.Frame(self.master, padding = '15 5 15 10')
        self.cnfSaveFrame = ttk.Frame(self.master, padding = '0 5')
        self.genFrame = ttk.Frame(self.master, padding = '0 0 0 5')
        self.imgFrame = ttk.LabelFrame(self.master, text = self.lang[7][0], padding = '5 0 5 5', labelanchor = 'n')
        self.imgFrameA = ttk.Frame(self.imgFrame, padding = '0 5')
        self.imgFrameB = ttk.Frame(self.imgFrame, padding = '0 5')
        self.imgFrameC = ttk.Frame(self.imgFrame, padding = '0 5')
        self.abFr = ttk.Frame(self.master, padding = '0 5 0 15')

        self.loadFrame.grid()
        self.cnf1Frame.grid()
        self.cnf23Frame.grid()
        self.cnf2Frame.pack(side = LEFT, fill = 'y', padx = 5)
        self.cnf2aFrame.grid()
        self.cnf2bFrame.grid()
        self.cnfTerFrame.pack(side = LEFT, fill = 'y', padx = 5)
        self.cnf3Frame.grid()
        self.cnf4Frame.grid()
        self.cnf5Frame.grid()
        self.l9.grid()
        self.cnf7Frame.grid()
        self.cnfSaveFrame.grid()
        self.genFrame.grid()
        self.imgFrame.grid(pady = 10)
        self.imgFrameA.grid()
        self.imgFrameB.grid()
        self.imgFrameC.grid()
        self.abFr.grid()

        # elementy ramki self.loadFrame
        # self.loadFrame elements
        self.l1 = ttk.Label(self.loadFrame, text = self.lang[0][0])
        self.lb1 = ttk.Entry(self.loadFrame, width = 50, state = 'readonly', textvariable = self.fn1Var)
        self.b1 = ttk.Button(self.loadFrame, text = '...', command = lambda: self.loadCnf())
        self.l1.grid(row = 0, column = 0)
        self.lb1.grid(row = 0, column = 1, padx = 5)
        self.b1.grid(row = 0, column = 2)

        # elementy ramki self.cnf1Frame
        # self.cnf1Frame elements
        self.cnVar = StringVar()
        self.l2 = ttk.Label(self.cnf1Frame, text = self.lang[1][0])
        self.rb1 = ttk.Radiobutton(self.cnf1Frame, text = 'PL – %s' % self.lang[1][1], variable = self.cnVar, value = 'PL', command = self.cnsel)
        self.rb2 = ttk.Radiobutton(self.cnf1Frame, text = 'CZ – %s' % self.lang[1][2], variable = self.cnVar, value = 'CZ', command = self.cnsel)
        self.rb3 = ttk.Radiobutton(self.cnf1Frame, text = 'SK – %s' % self.lang[1][3], variable = self.cnVar, value = 'SK', command = self.cnsel)
        self.l2.grid(row = 0, column = 0, padx = 5)
        self.rb1.grid(row = 0, column = 1, padx = 5)
        self.rb2.grid(row = 0, column = 2, padx = 5)
        self.rb3.grid(row = 0, column = 3, padx = 5)

        # elementy ramki self.cnf2Frame
        # self.cnf2Frame elements
        self.latVar, self.lonVar = StringVar(), StringVar()
        self.lc1 = ttk.Label(self.cnf2aFrame, text = self.lang[2][1])
        self.e1 = ttk.Entry(self.cnf2aFrame, textvariable = self.latVar)
        self.lc1.pack(side = LEFT)
        self.e1.pack(side = LEFT, padx = 5)
        self.e1.bind('<Return>', self.getlat2)
        self.e1.bind('<Tab>', self.getlat2)
        self.lc2 = ttk.Label(self.cnf2bFrame, text = self.lang[2][2])
        self.e2 = ttk.Entry(self.cnf2bFrame, textvariable = self.lonVar)
        self.lc2.pack(side = LEFT)
        self.e2.pack(side = LEFT, padx = 5)
        self.e2.bind('<Return>', self.getlon2)
        self.e2.bind('<Tab>', self.getlon2)
        self.latVar.set(self.latitude)
        self.lonVar.set(self.longitude)
        
        # elementy ramki self.cnf3Frame
        # self.cnf3Frame elements
        self.dimVar = StringVar()
        self.dimVar.set(self.mapdim)
        self.l3 = ttk.Label(self.cnf3Frame, text = self.lang[3][1])
        self.sb1 = ttk.Spinbox(self.cnf3Frame, from_ = 0, to = 100000, textvariable = self.dimVar, command = lambda: self.getl(), width = 6)
        self.l4 = ttk.Label(self.cnf3Frame, text = 'm')
        self.l3.pack(side = LEFT)
        self.sb1.pack(side = LEFT, padx = 5)
        self.l4.pack(side = LEFT)
        self.sb1.bind('<Return>', self.getl2)
        self.sb1.bind('<Tab>', self.getl2)
        
        # elementy ramki self.cnf4Frame
        # self.cnf4Frame elements
        self.resVar = StringVar()
        self.resVar.set(self.terres)
        self.l5 = ttk.Label(self.cnf4Frame, text = self.lang[3][2])
        self.sb2 = ttk.Spinbox(self.cnf4Frame, from_ = 0.1, to = 100.0, format = '%.1f', increment = 0.1, textvariable = self.resVar, command = lambda: self.getres(), width = 6)
        self.l6 = ttk.Label(self.cnf4Frame, text = 'm/px')
        self.l5.pack(side = LEFT)
        self.sb2.pack(side = LEFT, padx = 5)
        self.l6.pack(side = LEFT)
        self.sb2.bind('<Return>', self.getres2)
        self.sb2.bind('<Tab>', self.getres2)

        # elementy ramki self.cnf5Frame
        # self.cnf5Frame elements
        self.angVar = StringVar()
        self.angVar.set(self.angle)
        self.l7 = ttk.Label(self.cnf5Frame, text = self.lang[3][3])
        self.sb3 = ttk.Spinbox(self.cnf5Frame, from_ = -45.0, to = 45.0, format = '%.1f', increment = 0.1, textvariable = self.angVar, command = lambda: self.getang(), width = 6)
        self.l8 = ttk.Label(self.cnf5Frame, text = '°')
        self.l7.pack(side = LEFT)
        self.sb3.pack(side = LEFT, padx = 5)
        self.l8.pack(side = LEFT)
        self.sb3.bind('<Return>', self.getang2)
        self.sb3.bind('<Tab>', self.getang2)
        
        # elementy ramki self.cnf7Frame
        # self.cnf7Frame elements
        self.l10 = ttk.Label(self.cnf7Frame, text = self.lang[5][0])
        self.lb2 = ttk.Entry(self.cnf7Frame, width = 50, state = 'readonly', textvariable = self.fn2Var)
        self.b2 = ttk.Button(self.cnf7Frame, text = '...', command = lambda: self.dirsel())
        self.l10.pack(side = LEFT)
        self.lb2.pack(side = LEFT, padx = 5)
        self.b2.pack(side = LEFT)

        # elementy ramki self.cnfSaveFrame
        # self.cnfSaveFrame elements
        self.b3 = ttk.Button(self.cnfSaveFrame, text = self.lang[6][0], command = lambda: self.cnfSave())
        self.b3.pack(side = LEFT, padx = 5)
        self.b4 = ttk.Button(self.cnfSaveFrame, text = self.lang[6][1], command = lambda: self.openTempKML())
        self.b4.pack(side = LEFT, padx = 5)
        self.b5 = ttk.Button(self.cnfSaveFrame, text = self.lang[6][2], command = lambda: self.thradd(self.getElevationData))
        self.b5.pack(side = LEFT, padx = 5)
        
        # elementy ramki self.genFrame
        # self.genFrame elements
        self.b8 = ttk.Button(self.genFrame, text = self.lang[6][3], command = lambda: self.thradd(self.generateDem))
        self.b9 = ttk.Button(self.genFrame, text = self.lang[6][4], command = lambda: self.thradd(self.generate3DTerrain, use2ndPBar = True))
        self.b8.pack(side = LEFT, padx = 5)
        self.b9.pack(side = LEFT, padx = 5)
        
        # elementy ramki self.imgFrameA
        # self.imgFrameA elements
        self.fsv = IntVar()
        self.l14 = ttk.Label(self.imgFrameA, text = self.lang[7][1])
        self.rb6d = ttk.Radiobutton(self.imgFrameA, text = 'FS 22', variable = self.fsv, value = 4)
        self.rb6c = ttk.Radiobutton(self.imgFrameA, text = 'FS 19', variable = self.fsv, value = 3)
        self.rb6b = ttk.Radiobutton(self.imgFrameA, text = 'FS 17/15', variable = self.fsv, value = 2)
        self.rb6a = ttk.Radiobutton(self.imgFrameA, text = 'FS 2013', variable = self.fsv, value = 1)
        
        self.l14.pack(side = LEFT, padx = 5)
        self.rb6d.pack(side = LEFT, padx = 5)
        self.rb6c.pack(side = LEFT, padx = 5)
        self.rb6b.pack(side = LEFT, padx = 5)
        self.rb6a.pack(side = LEFT, padx = 5)

        # elementy ramki self.imgFrameB
        # self.imgFrameB elements
        self.dlortho = BooleanVar()
        self.dlshmap = BooleanVar()
        self.l13 = ttk.Label(self.imgFrameB, text = self.lang[7][2], padding = '5 0')
        self.cb1 = ttk.Checkbutton(self.imgFrameB, text = self.lang[7][3], variable = self.dlortho, onvalue = True, offvalue = False, padding = '5 0')
        self.cb2 = ttk.Checkbutton(self.imgFrameB, text = self.lang[7][4], variable = self.dlshmap, onvalue = True, offvalue = False, padding = '5 0')
        self.l13.pack(side = LEFT)
        self.cb1.pack(side = LEFT)
        self.cb2.pack(side = LEFT)

        # elementy ramki self.imgFrameC
        # self.imgFrameC elements
        self.b10 = ttk.Button(self.imgFrameC, text = self.lang[7][5], command = lambda: self.thradd(self.downloadImagery))
        self.b11 = ttk.Button(self.imgFrameC, text = self.lang[7][6], command = lambda: self.thradd(self.generateWMaps))
        self.b10.pack(side = LEFT, padx = 5)
        self.b11.pack(side = LEFT, padx = 5)

        self.about2 = ttk.Label(self.abFr, text = 'demgen v1.0.0 by crpl - CC-BY-SA 4.0 - 2020-22')
        self.helpme = ttk.Button(self.abFr, text = self.lang[6][5], command = lambda: webbrowser.open('https://github.com/CrusheerPL/demGenerator/wiki'))
        self.about2.pack(side = LEFT)
        self.helpme.pack(side = LEFT, padx = 5, ipadx = 5)

        self.rb1.invoke()
        self.rb6d.invoke()
        self.cb1.invoke()

        
    # funkcje programu
    # program functions

    # zaokrąglanie do jedności zgodnie z prawami matematyki
    def rndf(self, n):
        if n - int(n) >= 0.5:
            return int(n) + 1
        return int(n)

    # stwórz nowy wątek / create new thread
    # func - funkcja która ma być wykonana / target function
    # use2ndPBar - jeśli True, dołącz do okna powiązanego z wątkiem drugi pasek postępu
    # *args - argumenty funkcji func / 'func' function's arguments
    def thradd(self, func, use2ndPBar = False, *args):
        def cancel():
            if messagebox.askyesno(title = self.lang[8][1], message = self.lang[8][2], parent = prw):
                logging.info('%s: Operation cancelled by user' % proc)
                proc.stop()
                self.prWindows[getSTID(proc)].destroy()
                gc.collect()
        if self.dgDataPath == '':
            self.dgDataPath = '%s\\demgen_data' % os.getcwd()
            self.fn2Var.set(self.dgDataPath)
        if not os.path.exists(self.dgDataPath):
            os.mkdir(self.dgDataPath)
        self.applyInput()
        proc = StoppableThread(target = func, args = args)
        prw = Toplevel(self.master)
        prw.resizable(0, 0)
        prw.protocol("WM_DELETE_WINDOW", cancel)
        prw.fr = ttk.Frame(prw, padding = '15 10')
        prw.fr.grid()
        # postęp operacji
        prw.l1 = ttk.Label(prw.fr, text = self.lang[8][0], padding = '0 2.5')
        prw.l1.grid(row = 0, column = 0)
        prw.pbars = ttk.Frame(prw.fr, padding = '5 2.5')
        prw.pbars.grid(row = 0, column = 1)
        prw.pbar1 = ttk.Progressbar(prw.pbars, length = 275, maximum = 10, value = 0, mode = 'determinate')
        prw.pbar1.grid(row = 0, column = 0, pady = 2.5)
        prw.l2 = ttk.Label(prw.fr, text = '', padding = '5 2.5 5 5')
        prw.cb = ttk.Button(prw.fr, text = self.lang[8][1], command = cancel)
        if use2ndPBar:
            prw.pbar2 = ttk.Progressbar(prw.pbars, length = 275, maximum = 10, value = 0, mode = 'determinate')
            prw.pbar2.grid(row = 1, column = 0, pady = 2.5)
            prw.l2.grid(row = 2, columnspan = 2)
            prw.cb.grid(row = 3, columnspan = 2, pady = 5)
        else:
            prw.l2.grid(row = 1, columnspan = 2)
            prw.cb.grid(row = 2, columnspan = 2, pady = 5)
        self.prWindows.append(prw)
        proc.start()

    # obliczanie współrzędnych wierzchołków mapy
    # map corners coordinates calculating
    def getCoordsSet(self, b, l, dim, angle):
        brad = math.radians(b)
        lrad = math.radians(l)
        dist1 = dim * math.sqrt(2) * math.cos(math.radians(45 - math.fabs(angle))) / 2
        dist2 = dim * math.sqrt(2) * math.sin(math.radians(45 - math.fabs(angle))) / 2

        # https://en.wikipedia.org/wiki/Latitude#Length_of_a_degree_of_latitude
        # (phi - 0.5 deg) → (phi + 0.5 deg)
        latlen = 111132.954 - 559.822 * math.cos(2 * brad) + 1.175 * math.cos(4 * brad)
        # https://en.wikipedia.org/wiki/Longitude#Length_of_a_degree_of_longitude
        def lonlen(lat):
            return math.radians(math.pi / math.radians(180) * 6378137 * math.cos(math.atan(6356752.3 / 6378137 * math.tan(lat))))
        
        boffset1 = math.radians(dist1 / latlen)
        boffset2 = math.radians(dist2 / latlen)
        loffset1 = math.radians(dist1 / lonlen(brad)) # centralny punkt / central point
        loffset2 = math.radians(dist2 / lonlen(brad + boffset1)) # północ / north
        loffset3 = math.radians(dist2 / lonlen(brad - boffset1)) # południe / south

        # [NW, NE, SE, SW]
        if angle > 0:
            self.coordsSet = [[math.degrees(brad + boffset1), math.degrees(lrad - loffset2)], [math.degrees(brad + boffset2), math.degrees(lrad + loffset1)], [math.degrees(brad - boffset1), math.degrees(lrad + loffset3)], [math.degrees(brad - boffset2), math.degrees(lrad - loffset1)]]
        else:
            self.coordsSet = [[math.degrees(brad + boffset2), math.degrees(lrad - loffset1)], [math.degrees(brad + boffset1), math.degrees(lrad + loffset2)], [math.degrees(brad - boffset2), math.degrees(lrad + loffset1)], [math.degrees(brad - boffset1), math.degrees(lrad - loffset3)]]
        gc.collect()

    # ładowanie pliku konfiguracyjnego
    # config file loading
    def loadCnf(self):
        cnfFn2 = filedialog.askopenfilename(initialdir = os.getcwd(), title = self.lang[0][1], filetypes = ((self.lang[0][2] % 'XML','*.xml'),(self.lang[0][3],'*.*')))
        if cnfFn2 != '':
            logging.info("Loading config file '%s'..." % cnfFn2)
            try:
                conf = et.parse(cnfFn2)
            except:
                logging.exception("(ERROR) XML parse error while reading config file '%s' (details below)" % cnfFn2)
                messagebox.showerror('demgen', self.lang[9][8] % cnfFn2, detail = self.lang[9][9])
            else:
                self.cnfFn = cnfFn2
                self.fn1Var.set(self.cnfFn)
                para1 = conf.find('country')
                if para1 != None:
                    para1 = para1.get('value')
                    if para1 != None:
                        if para1.upper() in ('PL', 'CZ', 'SK'):
                            self.country = para1.upper()
                        else:
                            logging.warning("(WARNING) Element 'demgenConfig.country#value' of config file '%s' has unacceptable value '%s'. Default value has been set." % (cnfFn2, para1))
                            self.country = 'PL'
                    else:
                        logging.warning("(WARNING) Element 'demgenConfig.country#value' not found in config file '%s'. Default value has been set." % cnfFn2)
                        self.country = 'PL'
                else:
                    logging.warning("(WARNING) Element 'demgenConfig.country' not found in config file '%s'. Default value has been set." % cnfFn2)
                    self.country = 'PL'
                para2 = conf.find('centralPoint')
                if para2 != None:
                    para2a = para2.get('latitude')
                    para2b = para2.get('longitude')
                    if para2a != None:
                        try:
                            self.latitude = float(para2a.replace(',', '.'))
                        except:
                            logging.warning("(WARNING) Element 'demgenConfig.centralPoint#latitude' of config file '%s' has unacceptable value '%s'. Default value has been set." % (cnfFn2, para2a))
                            self.latitude = 0
                    else:
                        logging.warning("(WARNING) Element 'demgenConfig.centralPoint#latitude' not found in config file '%s'. Default value has been set." % cnfFn2)
                        self.latitude = 0
                    if para2b != None:
                        try:
                            self.longitude = float(para2b.replace(',', '.'))
                        except:
                            logging.warning("(WARNING) Element 'demgenConfig.centralPoint#longitude' of config file '%s' has unacceptable value '%s'. Default value has been set." % (cnfFn2, para2b))
                            self.longitude = 0
                    else:
                        logging.warning("(WARNING) Element 'demgenConfig.centralPoint#longitude' not found in config file '%s'. Default value has been set." % cnfFn2)
                        self.longitude = 0
                    del para2a, para2b
                else:
                    logging.warning("(WARNING) Element 'demgenConfig.centralPoint' not found in config file '%s'. Default values have been set." % cnfFn2)
                    self.latitude = 0
                    self.longitude = 0
                para3 = conf.find('terrain')
                if para3 != None:
                    para3a = para3.get('size')
                    para3b = para3.get('metersPerPixel')
                    para3c = para3.get('rotation')
                    if para3a != None:
                        try:
                            self.mapdim = int(para3a)
                        except:
                            logging.warning("(WARNING) Element 'demgenConfig.terrain#size' of config file '%s' has unacceptable value '%s'. Default value has been set." % (cnfFn2, para3a))
                            self.mapdim = 2048
                    else:
                        logging.warning("(WARNING) Element 'demgenConfig.terrain#size' not found in config file '%s'. Default value has been set." % cnfFn2)
                        self.mapdim = 2048
                    if para3b != None:
                        try:
                            self.terres = float(para3b.replace(',', '.'))
                        except:
                            logging.warning("(WARNING) Element 'demgenConfig.terrain#metersPerPixel' of config file '%s' has unacceptable value '%s'. Default value has been set." % (cnfFn2, para3b))
                            self.terres = 2
                    else:
                        logging.warning("(WARNING) Element 'demgenConfig.terrain#metersPerPixel' not found in config file '%s'. Default value has been set." % cnfFn2)
                        self.terres = 2
                    if para3c != None:
                        try:
                            self.angle = float(para3c.replace(',', '.'))
                        except:
                            logging.warning("(WARNING) Element 'demgenConfig.terrain#rotation' of config file '%s' has unacceptable value '%s'. Default value has been set." % (cnfFn2, para3c))
                            self.angle = 0
                    else:
                        logging.warning("(WARNING) Element 'demgenConfig.terrain#rotation' not found in config file '%s'. Default value has been set." % cnfFn2)
                        self.angle = 0
                    del para3a, para3b, para3c
                else:
                    logging.warning("(WARNING) Element 'demgenConfig.terrain' not found in config file '%s'. Default values have been set." % cnfFn2)
                    self.mapdim = 2048
                    self.terres = 2
                    self.angle = 0
                para5 = conf.find('dataSavingFolder')
                if para5 != None:
                    para5 = para5.get('path')
                    if para5 != None:
                        if para5[1] == ':':
                            if os.path.exists(para5[:2]):
                                self.dgDataPath = para5
                            else:
                                logging.warning("(WARNING) Path declared in 'demgenConfig.dataSavingFolder#path' element of config file '%s' refers to a nonexistent partition. Data will be saved in default directory (%s\\demgen_data) unless you change it." % (cnfFn2, os.getcwd()))
                                self.dgDataPath = ''
                        else:
                            self.dgDataPath = para5
                    else:
                        logging.warning("(WARNING) Element 'demgenConfig.dataSavingFolder#path' not found in config file '%s'. Default value has been set." % cnfFn2)
                        self.dgDataPath = ''
                else:
                    logging.warning("(WARNING) Element 'demgenConfig.dataSavingFolder' not found in config file '%s'. Default value has been set." % cnfFn2)
                    self.dgDataPath = ''

                self.cnVar.set(self.country)
                self.latVar.set(self.latitude)
                self.lonVar.set(self.longitude)
                self.dimVar.set(self.mapdim)
                self.resVar.set(self.terres)
                self.angVar.set(self.angle)
                self.fn2Var.set(self.dgDataPath)
                self.settls()
                self.getCoordsSet(self.latitude, self.longitude, self.mapdim, self.angle)
                del para1, para2, para3, para5
        gc.collect()

    # wybieranie kraju wraz z włączaniem/wyłączaniem niektórych opcji
    # country selecting
    def cnsel(self):
        self.country = self.cnVar.get()
        self.settls()

    # konwersja koordynatów do stopni z uwzględnieniem błędów, pomyłek
    # converting coordinates to degrees with attention to mistakes
    def coordFormat(self, pos, neg, stringvar):
        coord = stringvar.get()
        l = 0.0
        d = 1
        success = True
        if coord != '':
            try:
                l = float(coord.replace(',', '.'))
            except:
                s = re.findall(r"[\W']+", coord.replace(' ', '').replace("'", '|').replace('.', 'c').replace(',', 'c').replace('-', 'm'))
                coord = re.findall(r"[\w']+", coord.replace(' ', '').replace("'", '|').replace('.', 'c').replace(',', 'c').replace('-', 'm'))
                if len(coord) == 1:
                    try:
                        l = float(coord[0].replace('m', '-').replace('c', '.'))
                    except:
                        success = False
                else:
                    if coord[len(coord) - 1] == pos:
                        d = 1
                    elif coord[len(coord) - 1] == neg:
                        d = -1
                    else:
                        success = False
                    if success:
                        del coord[len(coord) - 1]
                        for i in range(len(coord)):
                            if s[i] == '°':
                                try:
                                    l += float(coord[i].replace('c', '.'))
                                except:
                                    success = False
                            elif s[i] == "|":
                                try:
                                    l += float(coord[i].replace('c', '.')) / 60
                                except:
                                    success = False
                            elif s[i] == '"':
                                try:
                                    l += float(coord[i].replace('c', '.')) / 3600
                                except:
                                    success = False
                            else:
                                success = False
        return l * d, success

    
    # ustawianie szerokości geograficznej centralnego punktu mapy
    # map's central point's latitude setting
    def getlat(self):
        changed = False
        l, s = self.coordFormat('N', 'S', self.latVar)
        if s:
            if self.latitude != l:
                changed = True
            self.latitude = l
        self.latVar.set(self.latitude)
        if changed:
            self.getCoordsSet(self.latitude, self.longitude, self.mapdim, self.angle)

    def getlat2(self, event):
        self.getlat()

    # ustawianie długości geograficznej centralnego punktu mapy
    # map's central point's longitude setting
    def getlon(self):
        changed = False
        l, s = self.coordFormat('E', 'W', self.lonVar)
        if s:
            if self.longitude != l:
                changed = True
            self.longitude = l
        self.lonVar.set(self.longitude)
        if changed:
            self.getCoordsSet(self.latitude, self.longitude, self.mapdim, self.angle)

    def getlon2(self, event):
        self.getlon()

    # ustawianie długości krawędzi mapy
    # map's edge length setting
    def getl(self):
        changed = False
        l = self.dimVar.get()
        dim = self.mapdim
        try:
            self.mapdim = int(l)
        except:
            self.dimVar.set(self.mapdim)
        else:
            if dim != self.mapdim:
                changed = True
        if changed:
            self.getCoordsSet(self.latitude, self.longitude, self.mapdim, self.angle)
            self.settls()

    # jak wyżej; funkcja pod binding
    # as above; function for binding
    def getl2(self, event):
        self.getl()

    # poprawianie wartości zmiennoprzecinkowych (zastępowanie przecinka kropką)
    # float values correcting (replacing ',' with '.')
    def correctFloat(self, s, stringvar, var):
        b = False
        for i in range(len(s)):
            b = b or (s[i].isalpha() or (s[i] in string.punctuation and s[i] != ','))
            if b:
                break
        if not b and s.count(',') == 1:
            s = s.replace(',', '.')
            stringvar.set(s)
            var = float(s)
        else:
            stringvar.set(str(var))
        return var

    # ustawianie rozdzielczości terenu
    # terrain resolution setting
    def getres(self):
        changed = False
        r = self.resVar.get()
        r2 = self.terres
        try:
            self.terres = float(r)
        except:
            self.correctFloat(r, self.resVar, self.terres)
        else:
            if self.terres != r2:
                changed = True
        if changed:
            self.settls()
        
    # jak wyżej; funkcja pod binding
    # as above; function for binding
    def getres2(self, event):
        self.getres()

    # ustawianie ilości kafli w zależności od pewnych parametrów
    def settls(self):
        if math.log2(self.mapdim / self.terres) == int(math.log2(self.mapdim / self.terres)):
            ll = self.mapdim * (math.sin(math.radians(math.fabs(self.angle))) + math.cos(math.radians(math.fabs(self.angle))))
            if self.country == 'CZ':
                if ll < 8192:
                    self.tiles = 1
                else:
                    i = 2
                    while (self.mapdim % i != 0) or (ll / i >= 8192):
                        i += 1
                    self.tiles = int(i) ** 2
            elif self.country == 'SK':
                self.tiles = 1
            else:
                if ll < 4096:
                    self.tiles = 1
                else:
                    i = 2
                    while (self.mapdim % i != 0) or (ll / i >= 4096):
                        i += 1
                    self.tiles = int(i) ** 2
            self.l9.config(text = self.lang[4] % self.tiles, foreground = 'black')
            self.tlsVar.set(self.tiles)
            self.b5.state(['!disabled'])
            self.b10.state(['!disabled'])
            self.b11.state(['!disabled'])
            self.canItDoThat = True
        else:
            self.l9.config(text = self.lang[9][1] % self.lang[9][2], foreground = 'red')
            self.b5.state(['disabled'])
            self.b10.state(['disabled'])
            self.b11.state(['disabled'])
            self.canItDoThat = False

    # ustawianie kątu obrotu terenu
    # terrain rotation angle setting
    def getang(self):
        changed = False
        a = self.angVar.get()
        angold = self.angle
        try:
            self.angle = float(a)
        except:
            self.angle = self.correctFloat(a, self.angVar, self.angle)
        if self.angle > 45 or self.angle < -45:
            self.angle = angold
            self.angVar.set(angold)
        if self.angle != angold:
            changed = True
        if changed:
            self.getCoordsSet(self.latitude, self.longitude, self.mapdim, self.angle)
            self.settls()

    # jak wyżej; funkcja pod binding
    # as above; function for binding
    def getang2(self, event):
        self.getang()

    # ustawianie ilości kafelków
    # tiles count setting
    def gettls(self):
        t = self.tlsVar.get()
        try:
            self.tiles = int(t)
        except:
            self.tlsVar.set(self.tiles)
        self.getAllTiles()

    # jak wyżej; funkcja pod binding
    # as above; function for binding
    def gettls2(self, event):
        self.gettls()
        
    # wybieranie folderu zapisu danych
    # data saving directory selecting
    def dirsel(self):
        d = filedialog.askdirectory(initialdir = os.getcwd(), title = self.lang[5][1])
        if d != '':
            self.dgDataPath = d
            self.fn2Var.set(self.dgDataPath)

    # zapisywanie konfiguracji do pliku
    # save the config to file
    def cnfSave(self):
        self.applyInput()
        cnfpath = filedialog.asksaveasfilename(initialdir = os.getcwd(), title = self.lang[6][0], filetypes = ((self.lang[0][2] % 'XML',"*.xml"),(self.lang[0][3],"*.*")))
        if cnfpath != '':
            logging.info("Saving config to '%s'..." % cnfpath)
            if not cnfpath.endswith('.xml'):
                cnfpath += '.xml'
            self.cnfFn = cnfpath
            self.fn1Var.set(self.cnfFn)
            config = et.Element('demgenConfig')
            config1 = et.SubElement(config, 'country', value = self.country)
            config2 = et.SubElement(config, 'centralPoint', latitude = str(self.latitude), longitude = str(self.longitude))
            config3 = et.SubElement(config, 'terrain', size = str(self.mapdim), metersPerPixel = str(self.terres), rotation = str(self.angle))
            config4 = et.SubElement(config, 'dataSavingFolder', path = self.dgDataPath)
            open(cnfpath, 'wb').write(et.tostring(config, encoding = 'utf-8', pretty_print = True, xml_declaration = True))
            del config, config1, config2, config3, config4
        del cnfpath
        gc.collect()

    # generowanie i otwieranie tymczasowego pliku KML
    # generate and open temporary KML file
    def openTempKML(self):
        self.applyInput()
        logging.info('Generating temporary KML file...')
        kmlpath = '%s\\dgKMLExport.kml' % os.getcwd()
        kmlcontent = et.Element('kml', xmlns = 'http://earth.google.com/kml/2.1')
        kml = et.SubElement(kmlcontent, 'Document')
        kmlA = et.SubElement(kml, 'description')
        kmlA.text = et.CDATA('KML generated by demgen (<a href="https://github.com/CrusheerPL/demGenerator">GitHub repo</a>)')
        kmlB = et.SubElement(kml, 'name')
        kmlB.text = 'dgKMLExport'
        kmlC = et.SubElement(kml, 'LookAt')
        kmlC1 = et.SubElement(kmlC, 'longitude')
        kmlC1.text = str(self.longitude)
        kmlC2 = et.SubElement(kmlC, 'latitude')
        kmlC2.text = str(self.latitude)
        kmlC3 = et.SubElement(kmlC, 'range')
        kmlC3.text = '500'
        kmlC4 = et.SubElement(kmlC, 'tilt')
        kmlC4.text = '0'
        kmlC5 = et.SubElement(kmlC, 'heading')
        kmlC5.text = '0'
        kmlD = et.SubElement(kml, 'Placemark')
        kmlE = et.SubElement(kmlD, 'Style')
        kmlF = et.SubElement(kmlE, 'PolyStyle')
        kmlF1 = et.SubElement(kmlF, 'color')
        kmlF1.text = 'ffffffff'
        kmlF2 = et.SubElement(kmlF, 'fill')
        kmlF2.text = '1'
        kmlF3 = et.SubElement(kmlF, 'outline')
        kmlF3.text = '0'
        kmlG = et.SubElement(kmlD, 'Polygon')
        kmlH = et.SubElement(kmlG, 'altitudeMode')
        kmlH.text = 'relativeToGround'
        kmlI = et.SubElement(kmlG, 'outerBoundaryIs')
        kmlI1 = et.SubElement(kmlI, 'LinearRing')
        kmlI2 = et.SubElement(kmlI1, 'coordinates')
        kmlI2.text = '%s,%s,0.5 %s,%s,0.5 %s,%s,0.5 %s,%s,0.5' % (str(self.coordsSet[0][1]), str(self.coordsSet[0][0]), str(self.coordsSet[1][1]), str(self.coordsSet[1][0]), str(self.coordsSet[2][1]), str(self.coordsSet[2][0]), str(self.coordsSet[3][1]), str(self.coordsSet[3][0]))

        et.ElementTree(kmlcontent).write(kmlpath, encoding = 'utf-8', pretty_print = True, xml_declaration = True)
        os.startfile(kmlpath)
        gc.collect()

    # apply input
    def applyInput(self):
        self.getlat()
        self.getlon()
        self.getl()
        self.getres()
        self.getang()

    # pobieranie danych wysokościowych
    # collect elevation data
    def getElevationData(self):
        self.prWindows[getSTID(threading.currentThread())].title('demgen - %s' % self.lang[6][2])
        # zbieranie wszystkich potrzebnych informacji
        self.prWindows[getSTID(threading.currentThread())].pbar1['value'] = 0
        self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][0])
        if self.canItDoThat:
            cn = self.country # kraj
            md = self.mapdim # wymiary terenu
            res = self.terres # rozdzielczość terenu
            ti = self.tiles # ilość kafelków
            pth = self.dgDataPath # folder docelowy zapisu danych
            coordset = self.coordsSet # zestaw współrzędnych wierzchołków (cały obszar)
            coords = [] # zestawy współrzędnych wierzchołków (każdy kafelek)
            logging.info("Starting job 'getElevationData' (thread: %s) with given input data:\n- Country: %s\n- Map dimensions: %s\n- Terrain resolution: %s\n- Tiles count: %s\n- Output directory: %s\n- Coordinates set: %s" % (threading.currentThread(), cn, md, res, ti, pth, coordset))
            if cn == 'SK':
                maxst = 5
            else:
                maxst = 4 * ti + 2
            self.prWindows[getSTID(threading.currentThread())].pbar1.config(maximum = maxst)

            if cn == 'PL':
                tr = pyproj.Proj('epsg:2180')
                bounds = [56, 48, 13, 25]
            elif cn == 'CZ' or cn == 'SK':
                if cn == 'SK': tr = pyproj.Proj('+proj=krovak +lat_0=49.5 +lon_0=24.8333333333333 +alpha=30.2881397527778 +k=0.9999 +x_0=0 +y_0=0 +ellps=bessel +towgs84=485.021,169.465,483.839,7.786342,4.397554,4.102655,0 +units=m +no_defs')
                bounds = [51.06, 47.73, 12.09, 22.56]
            # elif cn == ... (placeholder for more countries)
            
            if not (bounds[1] <= max([coordset[0][0], coordset[1][0]]) <= bounds[0] and bounds[1] <= min([coordset[2][0], coordset[3][0]]) <= bounds[0] and bounds[2] <= min([coordset[0][1], coordset[3][1]]) <= bounds[3] and bounds[2] <= max([coordset[1][1], coordset[2][1]]) <= bounds[3]):
                logging.warning('(WARNING) getElevationData (thread: %s): Input coordinates out of range (%s <= B <= %s, %s <= L <= %s). Operation has been aborted.' % (threading.currentThread(), bounds[1], bounds[0], bounds[2], bounds[3]))
                messagebox.showwarning('demgen - %s' % self.lang[6][2], self.lang[9][3] % (bounds[1], bounds[0], bounds[2], bounds[3]), parent = self.prWindows[getSTID(threading.currentThread())])
                self.prWindows[getSTID(threading.currentThread())].destroy()
                del cn, md, res, ti, pth, coordset, coords, maxst, self.prWindows[getSTID(threading.currentThread())]
                gc.collect()
                return
            else:
                if cn == 'SK':
                    dempth = filedialog.askopenfilename(initialdir = os.getcwd(), title = self.lang[10][9], filetypes = ((self.lang[0][2] % 'GeoTIFF','*.tif *.tiff'),(self.lang[0][3],'*.*')), parent = self.prWindows[getSTID(threading.currentThread())])
                    if dempth == '':
                        logging.warning('(WARNING) getElevationData (thread: %s): Input file not specified. Operation has been aborted.')
                        messagebox.showwarning('demgen - %s' % self.lang[6][2], self.lang[9][4], parent = self.prWindows[getSTID(threading.currentThread())])
                        self.prWindows[getSTID(threading.currentThread())].destroy()
                        del cn, md, res, ti, pth, coordset, coords, maxst, self.prWindows[getSTID(threading.currentThread())]
                        gc.collect()
                        return
                    else:
                        logging.info('getElevationData (thread: %s): Loading GeoTIFF file...' % threading.currentThread())
                        dem = geotiff.GeoTiff(dempth, as_crs = None, crs_code = 5514)
                        bb = [-dem.tif_bBox[1][0], -dem.tif_bBox[0][0], -dem.tif_bBox[0][1], -dem.tif_bBox[1][1]]
                if not os.path.exists(pth + '\\elevation'):
                    os.mkdir(pth + '\\elevation')
                self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                # generowanie zestawów współrzędnych (1 zestaw - 1 kafelek)
                logging.info('getElevationData (thread: %s): Generating coordinates sets' % threading.currentThread())
                self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][1])
                if ti == 1:
                    coords.append(coordset)
                else:
                    ti = int(math.sqrt(ti))
                    dbl, dll = coordset[3][0] - coordset[0][0], coordset[3][1] - coordset[0][1]
                    dbr, dlr = coordset[2][0] - coordset[1][0], coordset[2][1] - coordset[1][1]
                    for i in range(ti):
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        s1, e1 = [coordset[0][0] + i * dbl / ti, coordset[0][1] + i * dll / ti], [coordset[1][0] + i * dbr / ti, coordset[1][1] + i * dlr / ti]
                        s2, e2 = [coordset[0][0] + (i + 1) * dbl / ti, coordset[0][1] + (i + 1) * dll / ti], [coordset[1][0] + (i + 1) * dbr / ti, coordset[1][1] + (i + 1) * dlr / ti]
                        dbt, dlt = e1[0] - s1[0], e1[1] - s1[1]
                        dbb, dlb = e2[0] - s2[0], e2[1] - s2[1]
                        for j in range(ti):
                            if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                            coords.append([[s1[0] + j * dbt / ti, s1[1] + j * dlt / ti],
                                           [s1[0] + (j + 1) * dbt / ti, s1[1] + (j + 1) * dlt / ti],
                                           [s2[0] + (j + 1) * dbb / ti, s2[1] + (j + 1) * dlb / ti],
                                           [s2[0] + j * dbb / ti, s2[1] + j * dlb / ti]])
                self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                steps = int(md / res / ti)
                for cset in coords:
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                    # przetwarzanie danych - generowanie listy współrzędnych (przekonwertowanych do lokalnego układu)
                    nr = coords.index(cset) + 1
                    logging.info('getElevationData (thread: %s): Generating point list (%d/%d)' % (threading.currentThread(), nr, len(coords)))
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][2] + ' (%d/%d)' % (nr, len(coords)))
                    xy = [[], []]
                    dbl, dll = cset[3][0] - cset[0][0], cset[3][1] - cset[0][1]
                    dbr, dlr = cset[2][0] - cset[1][0], cset[2][1] - cset[1][1]
                    for i in range(steps + 1):
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        s1, e1 = [cset[0][0] + i * dbl / steps, cset[0][1] + i * dll / steps], [cset[1][0] + i * dbr / steps, cset[1][1] + i * dlr / steps]
                        dbt, dlt = e1[0] - s1[0], e1[1] - s1[1]
                        for j in range(steps + 1):
                            if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                            if cn == 'PL' or cn == 'SK':
                                x, y = tr(s1[1] + j * dlt / steps, s1[0] + j * dbt / steps)
                            elif cn == 'CZ':
                                # konwersja współrzędnych odbywa się z użyciem osobnej funkcji zamiast biblioteki pyproj ze względu na rozbieżność wyników pomiędzy obiema tymi metodami
                                x, y = wgs84_to_sjtsk(s1[0] + j * dbt / steps, s1[1] + j * dlt / steps)
                            xy[0].append(x)
                            xy[1].append(y)

                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                    if cn != 'SK':
                        # wyliczanie bbox
                        bb = [min(xy[0]), max(xy[0]), min(xy[1]), max(xy[1])] # x1, x2, y1, y2; x - poziome, y - pionowe
                        if cn == 'CZ': # NMT siatka 2 m
                            if int(bb[0]) % -2 == 0:
                                if bb[0] - int(bb[0]) <= -0.75:
                                    bb[0] = int(bb[0]) - 2.75
                                else:
                                    bb[0] = int(bb[0]) - 0.75
                            else:
                                bb[0] = int(bb[0]) - 1.75
                                
                            if int(bb[1]) % -2 == 0:
                                if bb[1] - int(bb[1]) <= -0.75:
                                    bb[1] = int(bb[1]) - 0.75
                                else:
                                    bb[1] = int(bb[1]) + 1.25
                            else:
                                bb[1] = int(bb[1]) + 0.25

                            if int(bb[2]) % -2 == 0:
                                bb[2] = int(bb[2]) - 1.25
                            else:
                                if bb[2] - int(bb[2]) <= -0.25:
                                    bb[2] = int(bb[2]) - 2.25
                                else:
                                    bb[2] = int(bb[2]) - 0.25

                            if int(bb[3]) % -2 == 0:
                                bb[3] = int(bb[3]) + 0.75
                            else:
                                if bb[3] - int(bb[3]) <= -0.25:
                                    bb[3] = int(bb[3]) - 0.25
                                else:
                                    bb[3] = int(bb[3]) + 1.75
                            imsize = int((bb[1]-bb[0]) / 2) + 1, int((bb[3]-bb[2]) / 2) + 1
                        elif cn == 'PL': # NMT siatka 1 m
                            bb[0] = math.floor(bb[0] - 1)
                            bb[1] = math.ceil(bb[1] + 1)
                            bb[2] = math.floor(bb[2] - 1)
                            bb[3] = math.ceil(bb[3] + 1)
                            imsize = int(bb[1]-bb[0]) + 1, int(bb[3]-bb[2]) + 1
                        # linki do obrazów
                        # pobieranie obrazu GeoTIFF
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        logging.info('getElevationData (thread: %s): Downloading GeoTIFF image (%d/%d)' % (threading.currentThread(), nr, len(coords)))
                        self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][3] + ' (%d/%d)' % (nr, len(coords)))
                        if cn == 'CZ':
                            imurl = 'https://ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer/exportImage?f=image&bbox=' + '%.2f' % bb[0] + '%2C' + '%.2f' % bb[2] + '%2C' + '%.2f' % bb[1] + '%2C' + '%.2f' % bb[3] + '&bboxSR=102067&imageSR=102067&size=' + '%d' % imsize[0] + '%2C' + '%d' % imsize[1] + '&format=tiff&pixelType=F32&noDataInterpretation=esriNoDataMatchAny&interpolation=+RSP_BilinearInterpolation&f=image'
                        elif cn == 'PL':
                            imurl = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/GRID1/WCS/DigitalTerrainModelFormatTIFF?SERVICE=WCS&VERSION=1.0.0&REQUEST=GetCoverage&FORMAT=image/tiff&COVERAGE=DTM_PL-KRON86-NH_TIFF&BBOX=' + '%.2f' % bb[0] + '%2C' + '%.2f' % bb[2] + '%2C' + '%.2f' % bb[1] + '%2C' + '%.2f' % bb[3] + '&CRS=EPSG:2180&RESPONSE_CRS=EPSG:2180&WIDTH=' + '%d' % imsize[0] + '&HEIGHT=' + '%d' % imsize[1]
                        td = open(pth + '\\tiffdem.tiff', 'wb')
                        td.write(openUrl(imurl))
                        td.close()
                        del td
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        dem = geotiff.GeoTiff(pth + '\\tiffdem.tiff', as_crs = None)
                        self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                    
                    # odczytywanie danych
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                    logging.info('getElevationData (thread: %s): Reading data (%d/%d)' % (threading.currentThread(), nr, len(coords)))
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][4] + ' (%d/%d)' % (nr, len(coords)))
                    xin = numpy.arange(0, dem.tif_shape[1])
                    yin = numpy.arange(0, dem.tif_shape[0])
                    zin = numpy.array(dem.read())

                    elevmap = interpolate.RectBivariateSpline(yin, xin, zin)
                    de1 = dem.tif_bBox[1][0] - dem.tif_bBox[0][0] # wschód - zachód
                    de2 = dem.tif_bBox[1][1] - dem.tif_bBox[0][1] # południe - północ
                    min1 = dem.tif_bBox[0][0] # zachód
                    min2 = dem.tif_bBox[0][1] # północ
                    
                    for i in range(len(xy[0])):
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        xy[0][i] = (xy[0][i] - min1) / de1 * (dem.tif_shape[1] - 1)
                        xy[1][i] = (xy[1][i] - min2) / de2 * (dem.tif_shape[0] - 1)

                    zout = elevmap(xy[1], xy[0], grid = False)
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                    # zapisywanie danych
                    logging.info('getElevationData (thread: %s): Saving data (%d/%d)' % (threading.currentThread(), nr, len(coords)))
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][5] + ' (%d/%d)' % (nr, len(coords)))
                    hout = open(pth + '\\elevation\\elevation_%d.txt' % coords.index(cset), 'w', encoding = 'utf-8')
                    for i in zout:
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        hout.write(str(i) + '\n')
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                    del zout, xy, dem
                logging.info('getElevationData (thread: %s): Operation completed successfully' % threading.currentThread())
                messagebox.showinfo('demgen - %s' % self.lang[6][2], self.lang[10][6], parent = self.prWindows[getSTID(threading.currentThread())])
            del cn, md, res, ti, pth, coordset, coords, maxst
        else:
            messagebox.showerror('demgen - %s' % self.lang[6][2], self.lang[9][1] % self.lang[9][2], parent = self.prWindows[getSTID(threading.currentThread())])
        self.prWindows[getSTID(threading.currentThread())].destroy()
        del self.prWindows[getSTID(threading.currentThread())]
        gc.collect()

    # generowanie map_dem z pobranych danych wysokościowych
    # generate map_dem from downloaded elevation data
    def generateDem(self):
        self.prWindows[getSTID(threading.currentThread())].title('demgen - %s' % self.lang[6][3])
        # zbieranie potrzebnych informacji
        self.prWindows[getSTID(threading.currentThread())].pbar1['value'] = 0
        self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][0])
        ti = self.tiles
        pth = self.dgDataPath
        logging.info("Starting job 'generateDem' (thread: %s) with given input data:\n- Tiles count: %s\n- Output directory: %s" % (threading.currentThread(), ti, pth))
        self.prWindows[getSTID(threading.currentThread())].pbar1.config(maximum = ti + 2)
        heights = []
        hmax = []
        hmin = []
        if os.path.exists('%s\\elevation' % pth):
            hf = sorted(Path('%s\\elevation' % pth).glob('elevation_*.txt'))
            if len(hf) != 0:
                ids = []
                for i in hf:
                    idt = int(str(i).split('\\')[-1][10:-4])
                    if 0 <= idt < ti: ids.append(idt)
                    del idt
                ids = sorted(ids)

                # sprawdź czy jest n^2 kafelków
                if len(ids) == ti and ti == ids[-1] + 1: # sprawdź po id kafelków czy nie ma braków
                    pc = int(math.sqrt(ti)) # ilość kafelków w poziomie/pionie
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                    # odczytywanie danych
                    logging.info('generateDem (thread: %s): Reading data' % threading.currentThread())
                    for i in ids:
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][4] + ' (%d/%d)' % (ids.index(i) + 1, len(ids)))
                        f = open('%s\\elevation\\elevation_%d.txt' % (pth, i))
                        h = list(map(float, f.read().splitlines()))
                        f.close
                        del f
                        heights.append(h)
                        hmax.append(max(h))
                        hmin.append(min(h))
                        del h
                        self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                    # wyznacz h(max), h(min), dh (różnicę wysokości) i r (zakres wysokości)
                    hmax = max(hmax)
                    hmin = min(hmin)
                    dh = hmax - hmin
                    i = 1
                    r = 255
                    while dh > r: # dopóki różnica wysokości jest większa od jego zakresu, zwiększaj to drugie
                        i *= 2
                        r = 256 * i - 1
                    if hmax > r or hmin < 0:
                        dh2 = (r - hmin - hmax) / 2
                    else:
                        dh2 = 0

                    logging.info('generateDem (thread: %s): DEM stats:\n- H(min): %.2f m\n- H(max): %.2f m\n- dH: %.2f m\n- Height Scale: %d m' % (threading.currentThread(), hmin, hmax, dh, r))
                    tex = open('%s\\demStats.txt' % pth, 'w', encoding = 'utf-8')
                    tex.write('H(min): %.2f m\nH(max): %.2f m\ndH: %.2f m\nHeight Scale: %d m' % (hmin, hmax, dh, r))
                    tex.close()
                    del tex

                    l = math.sqrt(len(heights[0])) # szerokość/wysokość jednego kafelka
                    ltot = int((l - 1) * pc + 1)
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                    # zapisywanie danych
                    logging.info('generateDem (thread: %s): Saving data' % threading.currentThread())
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][5])
                    dem = Image.new("I", (ltot, ltot))
                    dem8 = Image.new("RGB", (ltot, ltot))
                    d = ImageDraw.Draw(dem)
                    d8 = ImageDraw.Draw(dem8)

                    for i in range(pc):
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        for j in range(pc):
                            if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                            for k in range(len(heights[pc * i + j])):
                                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                                if (i == 0 and k < l) or (j == 0 and k % l == 0) or (k >= l and k % l != 0):
                                    h2 = heights[pc * i + j][k] + dh2
                                    d.point((j * (l - 1) + (k % l), i * (l - 1) + int(k / l)), round(h2 * 65535 / r))
                                    demR = math.floor(h2)
                                    demG = round(demR + (h2 - demR) * 256)
                                    if demG > 255:
                                        demR += 1
                                        demG -= 255
                                    d8.point((j * (l - 1) + (k % l), i * (l - 1) + int(k / l)), (demR, demG, 0))
                    dem.save(pth + '\\map_dem_16bit.png', 'PNG')
                    dem8.save(pth + '\\map_dem_8bit.png', 'PNG')
                    dem.close()
                    dem8.close()
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                    logging.info('generateDem (thread: %s): Operation completed successfully' % threading.currentThread())
                    messagebox.showinfo('demgen - %s' % self.lang[6][3], self.lang[10][7] + '\nH(min): %.2f m, H(max): %.2f m,\ndH: %.2f m, Height Scale: %d m.' % (hmin, hmax, dh, r), parent = self.prWindows[getSTID(threading.currentThread())])
                    del pc, dh, r, l, ltot, dh2, dem, dem8, d, d8
                else:
                    logging.warning('(WARNING) generateDem (thread: %s): Incorrect count of files with elevation data. Operation has been aborted.' % threading.currentThread())
                    messagebox.showwarning('demgen - %s' % self.lang[6][3], self.lang[9][6] % len(ids), ti, parent = self.prWindows[getSTID(threading.currentThread())])
                del ids
            else:
                logging.info('generateDem (thread: %s): No files with elevation data found' % threading.currentThread())
                messagebox.showwarning('demgen - %s' % self.lang[6][3], self.lang[9][5], parent = self.prWindows[getSTID(threading.currentThread())])
            del hf
        else:
            logging.info('generateDem (thread: %s): No files with elevation data found' % threading.currentThread())
            messagebox.showwarning('demgen - %s' % self.lang[6][3], self.lang[9][5], parent = self.prWindows[getSTID(threading.currentThread())])
        self.prWindows[getSTID(threading.currentThread())].destroy()
        del ti, pth, heights, hmax, hmin, self.prWindows[getSTID(threading.currentThread())]
        gc.collect()

    # generuj statyczny trójwymiarowy model terenu (Wavefront OBJ) z pobranych danych wysokościowych
    # generate static 3D terrain model (Wavefront OBJ) from downloaded elevation data
    def generate3DTerrain(self):
        self.prWindows[getSTID(threading.currentThread())].title('demgen - %s' % self.lang[6][4])
        # zbieranie potrzebnych informacji
        self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][0])
        self.prWindows[getSTID(threading.currentThread())].pbar1['value'] = 0
        d = self.terres
        pth = self.dgDataPath
        logging.info("Starting job 'generate3DTerrain' (thread: %s) with given input data:\n- Terrain resolution: %s\n- Output directory: %s" % (threading.currentThread(), d, pth))

        if os.path.exists('%s\\elevation' % pth):
            hf = sorted(Path('%s\\elevation' % pth).glob('elevation_*.txt'))
            if len(hf) != 0:
                ids = []
                for i in hf:
                    ids.append(int(str(i).split('\\')[-1][10:-4]))
                ids = sorted(ids)
                if not os.path.exists('%s\\staticTerrain' % pth):
                    os.mkdir('%s\\staticTerrain' % pth)
                self.prWindows[getSTID(threading.currentThread())].pbar1.config(maximum = 2 * len(ids) + 1)
                self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                # odczytywanie danych:
                for i in ids:
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                    nr = ids.index(i)
                    logging.info('generate3DTerrain (thread: %s): Reading data (%d/%d)' % (threading.currentThread(), nr + 1, len(ids)))
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][4] + ' (%d/%d)' % (nr + 1, len(ids)))
                    self.prWindows[getSTID(threading.currentThread())].pbar2['value'] = 0
                    h = open('%s\\elevation\\elevation_%d.txt' % (pth, i)).read().splitlines()
                    l = int(math.sqrt(len(h))) # wymiary dla rozdzielczości równej 1
                    if l > 513:
                        div = int((l - 1) / 512) # ilość kafli w jednej osi
                        l = 512
                    else:
                        l -= 1
                        div = 1
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                    self.prWindows[getSTID(threading.currentThread())].pbar2.config(maximum = div ** 2)
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                    logging.info('generate3DTerrain (thread: %s): Saving data (%d/%d)' % (threading.currentThread(), nr + 1, len(ids)))
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][5] + ' (%d/%d)' % (nr + 1, len(ids)))
                    # zapisywanie danych
                    for j in range(div):
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        for k in range(div):
                            if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                            obj = open('%s\\staticTerrain\\terrain_%d_%d.obj' % (pth, nr, j * div + k), 'w', encoding = 'utf-8')
                            obj.write('o staticTerrain_%d_%d\n' % (nr, j * div + k))
                            fgp = ['s 1\n']
                            z = -l / 2 * d
                            for m in range(l + 1):
                                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                                x = -l / 2 * d
                                for n in range(l + 1):
                                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                                    vid = int((j * l + m) * (l * div + 1) + k * l + n)
                                    vid2 = (l + 1) * m + n + 1
                                    obj.write('v %f %f %f\n' % (x, float(h[vid]), z))
                                    if m < l and n < l:
                                        s = 'f ' + str(vid2) + ' ' + str(vid2 + 1) + ' ' + str(vid2 + l + 2) + ' ' + str(vid2 + l + 1) + '\n'
                                        fgp.append(s)
                                    x += d
                                z += d
                            for m in fgp:
                                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                                obj.write(m)
                            obj.close()
                            del obj
                            self.prWindows[getSTID(threading.currentThread())].pbar2['value'] += 1
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                logging.info('generate3DTerrain (thread: %s): Operation completed successfully' % threading.currentThread())
                messagebox.showinfo('demgen - %s' % self.lang[6][4], self.lang[10][8], parent = self.prWindows[getSTID(threading.currentThread())])
                del ids
            else:
                logging.info('generate3DTerrain (thread: %s): No files with elevation data found' % threading.currentThread())
                messagebox.showwarning('demgen - %s' % self.lang[6][4], self.lang[9][5], parent = self.prWindows[getSTID(threading.currentThread())])
            del hf
        else:
            logging.info('generate3DTerrain (thread: %s): No files with elevation data found' % threading.currentThread())
            messagebox.showwarning('demgen - %s' % self.lang[6][4], self.lang[9][5], parent = self.prWindows[getSTID(threading.currentThread())])
        self.prWindows[getSTID(threading.currentThread())].destroy()
        del d, pth, self.prWindows[getSTID(threading.currentThread())]
        gc.collect()

    # pobieranie zdjęć lotniczych (z konwersją do formatu DDS) i/lub obrazu cieniowania terenu
    # download aerial imagery (with conversion to DDS format) and/or terrain shading
    def downloadImagery(self):
        self.prWindows[getSTID(threading.currentThread())].title('demgen - %s' % self.lang[7][5])
        self.b10.config(state = DISABLED)
        # zbieranie potrzebnych informacji
        self.prWindows[getSTID(threading.currentThread())].pbar1['value'] = 0
        self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][0])
        if self.canItDoThat:
            cwd = os.getcwd()
            cn = self.country
            fsv = self.fsv.get()
            ordl = self.dlortho.get()
            shdl = self.dlshmap.get()
            alpha = self.angle
            md = self.mapdim
            dgp = self.dgDataPath
            cset = self.coordsSet
            logging.info("Starting job 'downloadImagery' (thread: %s) with given input data:\n- Country: %s\n- Map dimensions: %s\n- Rotation (CW): %s\n- Output directory: %s\n- Coordinates set: %s\n- FS version (1 = FS 2013; 2 = FS 15/17; 3 = FS 19; 4 = FS 22): %s\n- Download aerial imagery: %s\n- Download hillshade image: %s" % (threading.currentThread(), cn, md, alpha, dgp, cset, fsv, ordl, shdl))
            if cn == 'PL':
                bounds = [56, 48, 13, 25]
            elif cn == 'CZ' or cn == 'SK':
                bounds = [51.06, 47.73, 12.09, 22.56]
            # elif cn == ... (placeholder for more countries)

            if not (bounds[1] <= max([cset[0][0], cset[1][0]]) <= bounds[0] and bounds[1] <= min([cset[2][0], cset[3][0]]) <= bounds[0] and bounds[2] <= min([cset[0][1], cset[3][1]]) <= bounds[3] and bounds[2] <= max([cset[1][1], cset[2][1]]) <= bounds[3]):
                logging.warning('(WARNING) downloadImagery (thread: %s): Input coordinates out of range (%s <= B <= %s, %s <= L <= %s). Operation has been aborted.' % (threading.currentThread(), bounds[1], bounds[0], bounds[2], bounds[3]))
                messagebox.showwarning('demgen - %s' % self.lang[7][5], self.lang[9][3] % (str(bounds[1]), str(bounds[0]), str(bounds[2]), str(bounds[3])), parent = self.prWindows[getSTID(threading.currentThread())])
                self.prWindows[getSTID(threading.currentThread())].destroy()
                self.b10.config(state = NORMAL)
                del cwd, cn, fsv, ordl, shdl, alpha, md, dgp, cset, self.prWindows[getSTID(threading.currentThread())]
                return
            elif ordl or shdl:
                til = self.rndf(md / 1024) # ilość tekstur w jednym rzędzie/kolumnie
                if ordl:
                    st = open('%s\\textureUnitSize.txt' % dgp, 'w', encoding = 'utf-8')
                    if fsv == 4:
                        logging.info('downloadImagery (thread: %s): Texture unitSize="%s"' % (threading.currentThread(), md / til / 2))
                        st.write('unitSize="%s"' % (md / til / 2))
                    else:
                        logging.info('downloadImagery (thread: %s): Texture unitSize="%s"' % (threading.currentThread(), md / til))
                        st.write('unitSize="%s"' % (md / til))
                    st.close()
                    del st
                
                maxst = 3 + til ** 2
                if ordl: maxst += 2
                if shdl: maxst += 1
                
                self.prWindows[getSTID(threading.currentThread())].pbar1.config(maximum = maxst)
                imd = 2048 / (math.cos(math.radians(math.fabs(alpha))) + math.sin(math.radians(math.fabs(alpha))))
                tilCoordsB = []
                tilCoordsL = []
                ort = []
                sha = []
                
                # ustal współrzędne wierzchołków kafelków
                # compute the tiles' vertex coordinates
                db1, dl1 = cset[0][0] - cset[3][0], cset[0][1] - cset[3][1]
                db2, dl2 = cset[1][0] - cset[2][0], cset[1][1] - cset[2][1]
                for y_iter in range(til * 2):
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                    # rzędy / rows
                    start1 = [cset[3][0] + y_iter * db1 / til / 2, cset[3][1] + y_iter * dl1 / til / 2]
                    start2 = [cset[3][0] + (y_iter + 1) * db1 / til / 2, cset[3][1] + (y_iter + 1) * dl1 / til / 2]
                    end1 = [cset[2][0] + y_iter * db2 / til / 2, cset[2][1] + y_iter * dl2 / til / 2]
                    end2 = [cset[2][0] + (y_iter + 1) * db2 / til / 2, cset[2][1] + (y_iter + 1) * dl2 / til / 2]
                    db3, dl3 = end1[0] - start1[0], end1[1] - start1[1]
                    db4, dl4 = end2[0] - start2[0], end2[1] - start2[1]
                    for x_iter in range(til * 2):
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                        # [start3, end3, start4, end4]
                        tilCoordsB.append([start1[0] + x_iter * db3 / til / 2, start1[0] + (x_iter + 1) * db3 / til / 2, start2[0] + x_iter * db4 / til / 2, start2[0] + (x_iter + 1) * db4 / til / 2])
                        tilCoordsL.append([start1[1] + x_iter * dl3 / til / 2, start1[1] + (x_iter + 1) * dl3 / til / 2, start2[1] + x_iter * dl4 / til / 2, start2[1] + (x_iter + 1) * dl4 / til / 2])
                self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                # generuj linki do pobrania obrazów
                logging.info('downloadImagery (thread: %s): Generating imagery URLs' % threading.currentThread())
                self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[11][0])
                for i in range(int(math.pow(til * 2, 2))):
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                    if cn == 'PL':
                        if ordl:
                            ort.append('https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/StandardResolutionTime?REQUEST=GetMap&TRANSPARENT=TRUE&FORMAT=image%2Fpng&VERSION=1.1.1&LAYERS=Raster&STYLES=&EXCEPTIONS=xml&TIME=2021-12-01T00%3A00%3A00.000%2B01%3A00&BBOX=' + '%s,%s,%s,%s' % (str(min(tilCoordsL[i])), str(min(tilCoordsB[i])), str(max(tilCoordsL[i])), str(max(tilCoordsB[i]))) + '&SRS=EPSG%3A4326&WIDTH=2048&HEIGHT=2048&SERVICE=WMS')
                        if shdl:
                            sha.append('http://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/GRID1/WMS/ShadedRelief?&REQUEST=GetMap&TRANSPARENT=FALSE&FORMAT=image/png&VERSION=1.3.0&LAYERS=Raster&STYLES=&BBOX=' + '%s,%s,%s,%s' % (str(min(tilCoordsB[i])), str(min(tilCoordsL[i])), str(max(tilCoordsB[i])), str(max(tilCoordsL[i]))) + '&CRS=EPSG%3A4326&WIDTH=1024&HEIGHT=1024&SERVICE=WMS')
                    elif cn == 'CZ':
                        if ordl:
                            ort.append('https://geoportal.cuzk.cz/WMS_ORTOFOTO_PUB/service.svc/get?LAYERS=GR_ORTFOTORGB&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=XML&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.031478753454327824&BBOX=' + '%s,%s,%s,%s' % (str(min(tilCoordsB[i])), str(min(tilCoordsL[i])), str(max(tilCoordsB[i])), str(max(tilCoordsL[i]))) + '&WIDTH=2000&HEIGHT=2000')
                        if shdl:
                            sha.append("https://ags.cuzk.cz/arcgis2/services/dmr5g/ImageServer/WMSServer?LAYERS=dmr5g%3AGrayscaleHillshade&TRANSPARENT=FALSE&FORMAT=image%2Fpng&VERSION=1.3.0&EXCEPTIONS=INIMAGE&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A4326&_OLSALT=0.4763809632942847&BBOX=" + '%s,%s,%s,%s' % (str(min(tilCoordsB[i])), str(min(tilCoordsL[i])), str(max(tilCoordsB[i])), str(max(tilCoordsL[i]))) + "&WIDTH=1024&HEIGHT=1024")
                    elif cn == 'SK':
                        if ordl:
                            ort.append('https://zbgis.skgeodesy.sk/zbgis/rest/services/Ortofoto/MapServer/export?dpi=96&transparent=true&format=png32&layers=show%3A5%2C6&bbox=' + '%s,%s,%s,%s' % (str(min(tilCoordsL[i])), str(min(tilCoordsB[i])), str(max(tilCoordsL[i])), str(max(tilCoordsB[i]))) + '&bboxSR=4326&imageSR=102100&size=2043%2C2048&f=image')
                        if shdl:
                            sha.append('https://zbgisws.skgeodesy.sk/zbgis_dmr3_wms/service.svc/get?request=GetMap&service=WMS&TRANSPARENT=FALSE&FORMAT=image/png&VERSION=1.3.0&LAYERS=0&STYLES=&BBOX=' + '%s,%s,%s,%s' % (str(min(tilCoordsB[i])), str(min(tilCoordsL[i])), str(max(tilCoordsB[i])), str(max(tilCoordsL[i]))) + '&CRS=EPSG%3A4326&WIDTH=1024&HEIGHT=1024')
                    # elif cn = '..': (placeholder for more countries)
                del tilCoordsB, tilCoordsL
                rqlist = open('%s\\downloadImagery_URLs.txt' % dgp, 'w', encoding = 'utf-8')
                if ordl:
                    rqlist.write(self.lang[7][3] + '\n')
                    for url in ort:
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                        rqlist.write(url + '\n')
                if shdl:
                    rqlist.write(self.lang[7][4] + '\n')
                    for url in sha:
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                        rqlist.write(url + '\n')
                rqlist.close()
                del rqlist
                self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                # pobierz i przetwórz obrazy (wykorzystaj multiprocessing)
                logging.info('downloadImagery (thread: %s): Downloading imagery' % threading.currentThread())
                self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[11][1])
                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                with multiprocessing.Pool(16) as p:
                    if ordl: imgs = list(p.imap(exportImg, ort))
                    if shdl: shds = list(p.imap(exportImg2, sha))
                del ort, sha
                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                if ordl:
                    if not os.path.exists('%s\\tmp' % dgp):
                        os.mkdir('%s\\tmp' % dgp)
                    if os.path.exists('%s\\textures' % dgp):
                        shutil.rmtree('%s\\textures' % dgp)
                    os.mkdir('%s\\textures' % dgp)
                    if til * 2048 <= 16384:
                        pda = Image.new('RGB', (til * 2048, til * 2048))
                    else:
                        pda = Image.new('RGB', (16384, 16384))
                if shdl: shim = Image.new('RGB', (til * 1024, til * 1024))
                self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                for y in range(til):
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                    for x in range(til):
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                        logging.info('downloadImagery (thread: %s): Editing imagery (%d/%d)' % (threading.currentThread(), til * y + x + 1, til ** 2))
                        self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[11][2] + ' (%d/%d)' % (til * y + x + 1, til ** 2))
                        if ordl:
                            im = Image.new('RGBA', (2048, 2048))
                            # wklejanie części obrazów
                            im.paste(imgs[til * y * 4 + x * 2].rotate(alpha, resample = Image.Resampling.BICUBIC).crop((1024 - imd / 2, 1024 - imd / 2, 1024 + imd / 2, 1024 + imd / 2)).resize((1024, 1024), resample = Image.Resampling.LANCZOS), box = (0, 1024))
                            im.paste(imgs[til * y * 4 + x * 2 + 1].rotate(alpha, resample = Image.Resampling.BICUBIC).crop((1024 - imd / 2, 1024 - imd / 2, 1024 + imd / 2, 1024 + imd / 2)).resize((1024, 1024), resample = Image.Resampling.LANCZOS), box = (1024, 1024))
                            im.paste(imgs[til * (y * 4 + 2) + x * 2].rotate(alpha, resample = Image.Resampling.BICUBIC).crop((1024 - imd / 2, 1024 - imd / 2, 1024 + imd / 2, 1024 + imd / 2)).resize((1024, 1024), resample = Image.Resampling.LANCZOS))
                            im.paste(imgs[til * (y * 4 + 2) + x * 2 + 1].rotate(alpha, resample = Image.Resampling.BICUBIC).crop((1024 - imd / 2, 1024 - imd / 2, 1024 + imd / 2, 1024 + imd / 2)).resize((1024, 1024), resample = Image.Resampling.LANCZOS), box = (1024, 0))
                            # zapisywanie obrazów
                            if fsv == 4:
                                for k in range(2):
                                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                                    for m in range(2):
                                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                                        nr = 2 * (til * (2 * y + k) + x) + m + 1
                                        if nr < 10:
                                            nr = '0%d' % nr
                                        else:
                                            nr = str(nr)
                                        im.crop((m * 1024, (1 - k) * 1024, (m + 1) * 1024, (2 - k) * 1024)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).save('%s\\tmp\\ortho%s_diffuse.png' % (dgp, nr), 'PNG')
                            else:
                                nr = til * y + x + 1
                                if nr < 10:
                                    nr = '0%d' % nr
                                else:
                                    nr = str(nr)
                                im.save('%s\\tmp\\ortho%s_diffuse.png' % (dgp, nr), 'PNG')
                            if til * 2048 <= 16384:
                                pda.paste(im, box = (x * 2048, (til - y - 1) * 2048))
                            else:
                                pda.paste(im.resize((16384 / til, 16384 / til), resample = Image.Resampling.LANCZOS), box = (x * 16384 / til, (til - y - 1) * 16384 / til))
                            im.close()
                            del im
                        if shdl:
                            with Image.new('RGB', (1024, 1024)) as shim2:
                                shim2.paste(shds[til * y * 4 + x * 2].rotate(alpha, resample = Image.Resampling.BICUBIC).crop((512 - imd / 4, 512 - imd / 4, 512 + imd / 4, 512 + imd / 4)).resize((512, 512), resample = Image.Resampling.LANCZOS), box = (0, 512))
                                shim2.paste(shds[til * y * 4 + x * 2 + 1].rotate(alpha, resample = Image.Resampling.BICUBIC).crop((512 - imd / 4, 512 - imd / 4, 512 + imd / 4, 512 + imd / 4)).resize((512, 512), resample = Image.Resampling.LANCZOS), box = (512, 512))
                                shim2.paste(shds[til * (y * 4 + 2) + x * 2].rotate(alpha, resample = Image.Resampling.BICUBIC).crop((512 - imd / 4, 512 - imd / 4, 512 + imd / 4, 512 + imd / 4)).resize((512, 512), resample = Image.Resampling.LANCZOS))
                                shim2.paste(shds[til * (y * 4 + 2) + x * 2 + 1].rotate(alpha, resample = Image.Resampling.BICUBIC).crop((512 - imd / 4, 512 - imd / 4, 512 + imd / 4, 512 + imd / 4)).resize((512, 512), resample = Image.Resampling.LANCZOS), box = (512, 0))
                                shim.paste(shim2, box = (x * 1024, (til - y - 1) * 1024))
                        self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                if ordl:
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                    # zapisywanie PDA i mapy cieniowania terenu
                    logging.info('downloadImagery (thread: %s): Saving PDA image' % threading.currentThread())
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[11][3])
                    if md < 4096:
                        pda.resize((2048, 2048), resample = Image.Resampling.LANCZOS).save('%s\\tmp\\pda_map_H.png' % dgp, 'PNG')
                    else:
                        pda.resize((4096, 4096), resample = Image.Resampling.LANCZOS).save('%s\\tmp\\pda_map_H.png' % dgp, 'PNG')
                    del imgs
                    pda.save('%s\\mapOverwiev.png' % dgp, 'PNG')
                    del pda
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1

                    # konwersja tekstur do formatu DDS
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                    logging.info('downloadImagery (thread: %s): Converting textures to DDS format' % threading.currentThread())
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[11][5])
                    subprocess.run('%s\\texconv.exe -f DXT1 -l -m 1 -o "%s" "%s\\tmp\\pda_map_H.png"' % (cwd, dgp, dgp), stdout = subprocess.DEVNULL)
                    Path('%s\\tmp\\pda_map_H.png' % dgp).unlink()
                    if fsv == 4:
                        try:
                            subprocess.run('%s\\textureTool -inputs "%s\\tmp" -arch dds -format bc7 -numMipmaps 8' % (cwd, dgp), stdout = subprocess.DEVNULL)
                        except:
                            logging.error("(ERROR) downloadImagery (thread: %s): Textures cannot be converted due to missing required GIANTS Texture Tool in the current working directory. Moving all png images to 'textures_png' directory." % threading.currentThread())
                            messagebox.showerror('demgen - %s' % self.lang[7][5], self.lang[9][10], parent = self.prWindows[getSTID(threading.currentThread())])
                            if os.path.exists('%s\\textures_png' % dgp):
                                shutil.rmtree('%s\\textures_png' % dgp)
                            os.mkdir('%s\\textures_png' % dgp)
                            for i in sorted(Path('%s\\tmp' % dgp).glob('ortho*.png')):
                                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                                shutil.move(str(i), '%s\\textures_png' % dgp)
                        else:
                            for i in sorted(Path('%s\\tmp' % dgp).glob('ortho*.dds')):
                                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                                shutil.move(str(i), '%s\\textures' % dgp)
                    elif fsv == 2 or fsv == 3:
                        subprocess.run('%s\\texconv.exe -r -vflip -f DXT5 -l -o "%s\\textures" "%s\\tmp\\*.png"' % (cwd, dgp, dgp), stdout = subprocess.DEVNULL)
                    else:
                        subprocess.run('%s\\texconv.exe -r -vflip -f DXT1 -l -o "%s\\textures" "%s\\tmp\\*.png"' % (cwd, dgp, dgp), stdout = subprocess.DEVNULL)
                    shutil.rmtree('%s\\tmp' % dgp)
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; self.b10.config(state = NORMAL); return
                if shdl:
                    del shds
                    logging.info('downloadImagery (thread: %s): Saving hillshade image' % threading.currentThread())
                    self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[11][4])
                    shim.save('%s\\terrainShading.png' % dgp, 'PNG')
                    del shim
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                logging.info('downloadImagery (thread: %s): Operation completed successfully' % threading.currentThread())
                messagebox.showinfo('demgen - %s' % self.lang[7][5], self.lang[11][6], parent = self.prWindows[getSTID(threading.currentThread())])
                del til, maxst
            else:
                logging.info('downloadImagery (thread: %s): Nothing has been downloaded' % threading.currentThread())
                messagebox.showinfo('demgen - %s' % self.lang[7][5], self.lang[11][7], parent = self.prWindows[getSTID(threading.currentThread())])
            del cwd, cn, fsv, ordl, shdl, alpha, md, dgp, cset
            self.b10.config(state = NORMAL)
        else:
            messagebox.showerror('demgen - %s' % self.lang[7][5], self.lang[9][1] % self.lang[9][2], parent = self.prWindows[getSTID(threading.currentThread())])
        self.prWindows[getSTID(threading.currentThread())].destroy()
        del self.prWindows[getSTID(threading.currentThread())]
        gc.collect()

    # generowanie weightmap
    # generate weightmaps
    def generateWMaps(self):
        self.prWindows[getSTID(threading.currentThread())].title('demgen - %s' % self.lang[7][6])
        # zbieranie potrzebnych informacji
        self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[10][0])
        if self.canItDoThat:
            md = self.mapdim
            res = self.terres
            fsv = self.fsv.get()
            logging.info("Starting job 'generateWMaps' (thread: %s) with given input data:\n- Map dimensions: %s\n- Terrain resolution: %s\n- FS version (1 = FS 2013; 2 = FS 15/17; 3 = FS 19; 4 = FS 22): %s" % (threading.currentThread(), md, res, fsv))
            
            # md/res zawsze będzie 2^n        
            til = self.rndf(md / 1024) # ilość tekstur w jednym rzędzie/kolumnie (dla FS 22 jeszcze x2)
            if fsv == 4: til *= 2
            if res != 2:
                md = int(md / res * 2)
            # od tego momentu zmienna md służy za wartość wymiaru generowanej weightmapy
            # w przypadku terenów o niestandardowych wymiarach (np. 5120 czy 6144),
            # linie łączeń tekstur na mapie mogą być wyraźniejsze i/lub tekstury mogą być nierówno rozmieszczone

            target_dir = filedialog.askdirectory(initialdir = os.getcwd(), title = self.lang[11][8], parent = self.prWindows[getSTID(threading.currentThread())])
            if target_dir != '':
                logging.info("generateWMaps (thread: %s): Output directory: '%s'" % (threading.currentThread(), target_dir))
                td = sorted(Path(target_dir).glob('*_weight.png')) + sorted(Path(target_dir).glob('gravelAlpine*.png'))
                ort = sorted(Path(target_dir).glob('ortho*_weight.png'))
                for i in ort:
                    if i in td: del td[td.index(i)]

                if fsv == 1 or fsv == 2: # FS17 i starsze
                    md = self.rndf(md / 2)

                self.prWindows[getSTID(threading.currentThread())].pbar1.config(maximum = len(td) + til ** 2 + 1)
                self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                # generowanie weightmap
                logging.info('generateWMaps (thread: %s): Saving weightmaps' % threading.currentThread())
                self.prWindows[getSTID(threading.currentThread())].l2.config(text = self.lang[11][9])
                for i in td:
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                    Image.new('L', (md, md)).save(i, 'PNG')
                    self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1

                for i in range(til):
                    if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                    for j in range(til):
                        if threading.currentThread().stopped(): del self.prWindows[getSTID(threading.currentThread())]; return
                        imid = til * i + j + 1
                        if imid < 10:
                            imid = '0%d' % imid
                        else:
                            imid = str(imid)
                        with Image.new('L', (md, md)) as wm:
                            #wm = Image.new('L', (md, md))
                            d = ImageDraw.Draw(wm)
                            dim = md / til
                            d.rectangle([(j * dim, (til - i) * dim - 1), ((j + 1) * dim - 1, (til - i - 1) * dim)], 255, width = 0)
                            wm.save(target_dir + '\\ortho%s_weight.png' % imid, 'PNG')
                        self.prWindows[getSTID(threading.currentThread())].pbar1['value'] += 1
                logging.info('generateWMaps (thread: %s): Operation completed successfully' % threading.currentThread())
                messagebox.showinfo('demgen - %s' % self.lang[7][6], self.lang[11][10], parent = self.prWindows[getSTID(threading.currentThread())])
            else:
                logging.warning('(WARNING) generateWMaps (thread: %s): Destination directory not specified. Operation has been aborted.' % threading.currentThread())
                messagebox.showwarning('demgen - %s' % self.lang[7][6], self.lang[9][7], parent = self.prWindows[getSTID(threading.currentThread())])
        else:
            messagebox.showerror('demgen - %s' % self.lang[7][6], self.lang[9][1] % self.lang[9][2], parent = self.prWindows[getSTID(threading.currentThread())])
        self.prWindows[getSTID(threading.currentThread())].destroy()
        del self.prWindows[getSTID(threading.currentThread())]
        gc.collect()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    gc.enable()
    logging.basicConfig(filename = '%s\\demgen_log.txt' % os.getcwd(), filemode = 'w', datefmt = '%x %X', format = '%(asctime)s %(message)s', level=20)
    logging.info('demgen v 1.0.0 by crpl - CC-BY-SA 4.0 - 2020-22')
    logging.info('Current working directory: %s', os.getcwd())
    # download texconv.exe if not exists in the current working directory
    if not os.path.exists('%s\\texconv.exe' % os.getcwd()):
        logging.warning('(WARNING) Missing Texconv in the current working directory - installation in progress...')
        connerr = True
        while connerr:
            try:
                txc = requests.get('https://github.com/Microsoft/DirectXTex/releases/latest/download/texconv.exe')
            except:
                continue
            else:
                if txc.status_code == 200:
                    open('%s\\texconv.exe' % os.getcwd(), 'wb').write(txc.content)
                    connerr = False
                    del txc
        logging.info('Texconv downloaded and installed successfully')
        del connerr
    else:
        logging.info('Texconv tool is present in the current working directory')
    dg_gui = dgGUI()
    # look for GIANTS Texture Tool if not exists in the current working directory
    if not (os.path.exists('%s\\textureTool.exe' % os.getcwd()) and os.path.exists('%s\\textureTool.xml' % os.getcwd())):
        logging.warning('(WARNING) Missing GIANTS Texture Tool in the current working directory (at least one necessary file)')
        if locale.getdefaultlocale()[0] == 'pl_PL':
            mess = ('Do pełnego funkcjonowania demgen potrzebuje narzędzia GIANTS Texture Tool. Czy chcesz wyszukać go na dysku i zainstalować w folderze z programem?', 'Wybierz folder, w którym mają być szukane pliki', 'Nie znaleziono potrzebnych plików.', 'Niektóre funkcje mogą nie działać prawidłowo.')
        else:
            mess = ('demgen needs a GIANTS Texture Tool to be fully functional. Do you want to search for it and install it in the program directory?', 'Select the folder where the files will be searched for', 'No necessary files found.', 'Some functions may not work properly.')
        if messagebox.askyesno(title = 'demgen', message = mess[0]):
            fldr = filedialog.askdirectory(initialdir = os.getcwd(), title = mess[1])
            texToolDir = ''
            if fldr != '':
                for root, dirs, files in os.walk(fldr):
                    if 'textureTool.xml' in files and 'textureTool.exe' in files:
                        texToolDir = root
                        break
                if texToolDir != '':
                    shutil.copy('%s\\textureTool.exe' % texToolDir, os.getcwd())
                    shutil.copy('%s\\textureTool.xml' % texToolDir, os.getcwd())
                    logging.info('GIANTS Texture Tool installed successfully')
                else:
                    logging.error('(ERROR) No necessary files found - GIANTS Texture Tool not installed. Some functions may not work properly.')
                    messagebox.showwarning(title = 'demgen', message = '%s %s' % (mess[2], mess[3]))
            else:
                logging.error('(ERROR) GIANTS Texture Tool not installed. Some functions may not work properly.')
                messagebox.showwarning(title = 'demgen', message = mess[3])
            del fldr, texToolDir
        else:
            logging.error('(ERROR) GIANTS Texture Tool not installed. Some functions may not work properly.')
            messagebox.showwarning(title = 'demgen', message = mess[3])
        del mess
    else:
        logging.info('GIANTS Texture Tool is present in the current working directory')
    dg_gui.master.mainloop()

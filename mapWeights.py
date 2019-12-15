from PIL import Image, ImageDraw
import math
import os

print('Map_weight generator')
use_stdin = True
try:
    print('Trying to open the config file... ', end='')
    config = open("demGenerator_config.txt", "r")
except:
    print("File not found.")
    l = int(input("Map edge length [meters]: "))
else:
    print("Done.\nConfig file is loading...")
    string = config.read()
    string = string.split()
    l = int(string[5])
    use_stdin = False
    config.close()

if (l % 1024 == 0):
    div = int(l / 1024)
    if (not os.path.exists(os.getcwd() + "\\mapWeights")):
        os.mkdir(os.getcwd() + "\\mapWeights")
    for i in range(div):
        for j in range(div):
            imid = div * i + j + 1
            if imid < 10:
                imid = '0%d' % imid
            else:
                imid = str(imid)
            wm = Image.new('L', (l, l))
            d = ImageDraw.Draw(wm)
            for m in range(1024 * (div - i), 1024 * (div - i - 1), -1):
                for n in range(1024 * j, 1024 * j + 1024):
                    d.point((n, m - 1), 255)
            wm.save('mapWeights/grassRough%s_weight.png' % imid, 'PNG')
else:
    print("Incorrect input data (map edge length or resolution)")

_ = input('Ready. Press ENTER to close...')

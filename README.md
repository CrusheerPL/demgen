<img src="https://abload.de/img/demgen09j6o.png" align="center"/>
<img src="https://abload.de/img/window_overviewhyknv.png" align="center"/>

# (English – sorry for any mistakes)
To run these scripts you need the Python environment (3.5 to 3.7; https://www.python.org/downloads/) and the Python packages: ***Pillow*** (https://pypi.org/project/Pillow/ or `pip install Pillow` on the command line) and ***tqdm*** (https://pypi.org/project/tqdm/ or `pip install tqdm` on the command line).

## Principle of operation
*demGenerator* is a tool pack which allows you to create a terrain for the Farming Simulator mod-map based on real height data. This repository contains some files:
- ***demGenerator_mod1.py*** – determines the points' coordinates, based on the bounds' coordinates (WGS 84), map edge length and its resolution – all given at the input. The output files' name: `xy_*.txt` (`*` = tile number)
- ***demGenerator_mod2.py*** – downloads the elevation data for points whose coordinates are given in the `xy_*.txt` file (you must only type the tile number as input), and writes it to the `h_*.txt` file in the same order as the coordinates were loaded. **Attention: Internet connection required. The script execution time depends on the connection speed and the amount of data to be processed. Due to high data consumption, it is not recommended to run it when the tariff connection is set.**
- ***demGenerator_mod3.py*** – creates the height map from downloaded elevation data. The each pixel value is expressed by the formula: **`p = h / z * 65535`** (p = value of pixel (16 bit integer grayscale mode), h = height in meters, z = height range (255, 511, 1023, ... m)).
- ***mapGen.py*** – downloads the orthophotomap, topographic map and the terrain shading map by directing queries to appropriate *Web Map Service* servers.
- ***weightMaps.py*** – generates the weight maps and additional lines which you have to paste into the map.i3d file.

## Config file (*demGenerator_config.txt*)
Input data format:

**`cn B_max B_min L_min L_max len res tls`**
- cn = country (PL or CZ)
- B_max = map's north edge latitude
- B_min = map's south edge latitude
- L_min = map's west edge longitude
- L_max = map's east edge longitude
- len = map edge length
- res = map's resolution (meters/pixel)
- tls = total tiles count (always must be equal to 4 ^ n)
**Attention: B_max, B_min, L_min, L_max – WGS 84 coordinates.**

## How to use (tutorial): see Wiki tab

## Credits:
- **WGS84 -> PUWG 1992 converter (C++ function – source: http://www.szymanski-net.eu/programy.html):** Zbigniew Szymański (z.szymanski@szymanski-net.eu)
- **WGS84 -> S-JTSK converter (JavaScript function – source: https://www.pecina.cz/krovak.html):** Tomáš Pecina (tomas@pecina.cz)
- **functions translation into Python + modules 1, 2, 3 + _mapGen.py_ and _weightMaps.py_:**: crpl

### This is a free software. You can modify its code as well as copy the content of this repository to various file hosts, if you indicate the original author and the original source. If you encountered a problem with this software – please create a new topic in the *Issues* tab.

# (polski)
Do uruchomienia skryptów wymagany jest środowisko Pythona w wersji 3.5 – 3.7 (https://www.python.org/downloads/), a także biblioteki ***Pillow*** (https://pypi.org/project/Pillow/ lub komenda `pip install Pillow` w wierszu poleceń) oraz ***tqdm*** (https://pypi.org/project/tqdm/ lub komenda `pip install tqdm` w wierszu poleceń).

## Zasada działania
*demGenerator* jest to pakiet narzędzi pozwalających na samodzielne utworzenie na podstawie realnych danych wysokościowych ukształtowania terenu do mapy do Farming Simulator. To repozytorium zawiera pliki:
- ***demGenerator_mod1.py*** – wyznacza współrzędne punktów do późniejszego pobrania ich wysokości, na podstawie podanych na wejściu współrzędnych granicznych w układzie WGS 84, długości boku odwzorowywanego terenu i jego rozdzielczości. Pliki wyjściowe przyjmują format `xy_*.txt`, przy czym `*` to nr kafelka.
- ***demGenerator_mod2.py*** – pobiera dane wysokościowe dla punktów, których współrzędne podano w wyżej wymienionym pliku tekstowym (należy tylko podać nr kafelka) i zapisuje je do pliku wyjściowego `h_*.txt` w tej samej kolejności, w jakiej zostały wczytane współrzędne. **Uwaga: wymagane połączenie internetowe. Czas wykonywania tego skryptu zależy od prędkości połączenia i ilości danych do przetworzenia. Nie jest zalecane jego uruchamianie przy ustawionym połączeniu taryfowym.**
- ***demGenerator_mod3.py*** – tworzy mapę wysokości z pobranych danych wysokościowych. Wartość każdego piksela wyraża się następującym wzorem: **`p = h / z * 65535`**, gdzie:
  - p – wartość piksela (w trybie szesnastobitowym stałoprzecinkowym w odcieniach szarości)
  - h – wysokość w metrach
  - z – zakres wysokości (255, 511, 1023, ... m).
- ***mapGen.py*** – pobiera ortofotomapy, mapy topograficzne i mapy cieniowania terenu poprzez kierowanie zapytań do odpowiednich serwerów *Web Map Service*.
- ***weightMaps.py*** – generuje *weight maps* i dodatkowe linijki do wklejenia do pliku map.i3d. 

## Plik konfiguracyjny (demGenerator_config.txt)
Format danych wejściowych w tym pliku prezentuje się w następujący sposób:

**`kr B_max B_min L_min L_max len res tls`**, gdzie:
- kr (kraj - PL lub CZ)
- B_max (szerokość geogr. północnej krawędzi mapy)
- B_min (szerokość geogr. południowej krawędzi mapy)
- L_min (długość geogr. zachodniej krawędzi mapy)
- L_max (długość geogr. wschodniej krawędzi mapy)
- len (długość krawędzi mapy)
- res (rozdzielczość [metry/piksel])
- tls (łączna ilość części (kafelków) równa 4 ^ n)

**Uwaga: B_max, B_min, L_min, L_max - współrzędne układu WGS 84.**

## Jak korzystać (poradnik): patrz zakładka Wiki

## Autorzy:
- **funkcja do przeliczania współrzędnych WGS84 -> PUWG 1992** – oryginalny kod w C++ (z: http://www.szymanski-net.eu/programy.html): Zbigniew Szymański (z.szymanski@szymanski-net.eu)
- **funkcja do przeliczania współrzędnych WGS84 -> S-JTSK** – oryginalny kod w JavaScript (z: https://www.pecina.cz/krovak.html): Tomáš Pecina (tomas@pecina.cz)
- **przekład funkcji na język Python + moduły 1, 2, 3 + _mapGen.py_ i _weightMaps.py_:** crpl
### Oprogramowanie darmowe. Wszelkie modyfikacje dozwolone, tak samo jak i kopiowanie zawartości tego repozytorium do różnych hostingów plików, pod warunkiem wskazania oryginalnego autora i źródła. W razie wystąpienia problemów z działaniem oprogramowania – proszę o założenie nowego tematu w zakładce *Issues*.

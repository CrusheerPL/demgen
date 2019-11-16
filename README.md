<img src="https://abload.de/img/104_exjkh3.png" align="center"/>
Heightmap generator for Farming Simulator mod-maps. Supported countries: Poland and Czechia.
<img src="https://abload.de/img/1025nj24.png" align="center"/>

# (English)
To run these scripts you need the Python interpreter (3.5 or later is required; https://www.python.org/downloads/) and the Python packages: *Pillow* (https://pypi.org/project/Pillow/) and *tqdm* (https://pypi.org/project/tqdm/).

# (polski)
Do uruchomienia skryptów wymagany jest interpreter Pythona w wersji 3.5 lub nowszej (https://www.python.org/downloads/), a także biblioteki *Pillow* (https://pypi.org/project/Pillow/) oraz *tqdm* (https://pypi.org/project/tqdm/).

## Zasada działania
*demGenerator* jest to pakiet narzędzi pozwalających na samodzielne wygenerowanie mapy wysokości (*map_dem.png*). Składa się z trzech modułów (skryptów napisanych w języku Python):
- pierwszy (***demGenerator_mod1.py***) wyznacza współrzędne punktów, dla których mają być pobrane wysokości, na podstawie podanych na wejściu współrzędnych granicznych w układzie WGS 84 (w stopniach dziesiętnych), długości boku odwzorowywanego terenu, jego rozdzielczości i kraju (PL lub CZ). Dodatkowo, można podzielić obszar na równe części (dalej: kafelki), dzięki czemu nie trzeba koniecznie tak długo czekać, nim wszystkie dane wysokościowe zostaną pobrane. Pliki wyjściowe przyjmują format `xy_*.txt`, przy czym (`*` w tym przypadku to nr kafelka).
- drugi (***demGenerator_mod2.py***) pobiera dane wysokościowe dla współrzędnych podanych w wyżej wspomnianym pliku tekstowym (należy tylko podać nr kafelka) i zapisuje je do pliku wyjściowego `h_*.txt` w tej samej kolejności, w jakiej zostały wczytane współrzędne. **UWAGA: wymagane połączenie internetowe. Czas wykonywania tego skryptu zależy od prędkości połączenia i ilości danych do przetworzenia. Nie jest zalecane jego uruchamianie przy ustawionym połączeniu taryfowym.**
- trzeci (***demGenerator_mod3.py***) generuje plik *map_dem.png*, zawierający dane wysokościowe ze wszystkich plików opatrzonych nazwą `h_*.txt` (**UWAGA: musi być ich tyle, co kafelków**). Wartość każdego piksela wyraża się następującym wzorem:
**`p = h / z * 65535`**, gdzie:
  - p – wartość piksela (w trybie szesnastobitowym stałoprzecinkowym w odcieniach szarości)
  - h – wysokość w metrach
  - z – zakres wysokości (255, 510, 765, 1020, ... m - zależny od maksymalnej wartości)

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
- tls (ilość części równa 2 ^ n)
**UWAGA: B_max, B_min, L_min, L_max - współrzędne układu WGS 84.**

## Prawidłowe użycie demGeneratorPL
### Tutorial
(link wkrótce)
### Timelapse
(też później)

## Autorzy:
- **funkcja do przeliczania współrzędnych WGS84 -> PUWG 1992:**
  - oryginalny kod w C++ (z: http://www.szymanski-net.eu/programy.html): Zbigniew Szymański (z.szymanski@szymanski-net.eu)
  - na język Python przełożył: RusheerPL
- **funkcja do przeliczania współrzędnych WGS84 -> S-JTSK:**
  - oryginalny kod w JavaScript (z: https://www.pecina.cz/krovak.html): Tomáš Pecina (tomas@pecina.cz)
  - na język Python przełożył: RusheerPL
- **moduły 1, 2, 3:** RusheerPL
### Uwaga od Z. Szymańskiego (dotyczy wyłącznie funkcji do konwersji współrzędnych):
Oprogramowanie darmowe. Dozwolone jest wykorzystanie i modyfikacja niniejszego oprogramowania do własnych celów pod warunkiem  pozostawienia wszystkich informacji z nagłówka. W przypadku wykorzystania niniejszego oprogramowania we wszelkich projektach
naukowo-badawczych, rozwojowych, wdrożeniowych i dydaktycznych proszę o zacytowanie następującego artykułu:
**Zbigniew Szymański, Stanisław Jankowski, Jan Szczyrek, "Reconstruction of environment model by using radar vector field histograms.", Photonics Applications in Astronomy, Communications, Industry, and High-Energy Physics Experiments 2012, Proc. of SPIE Vol. 8454, pp. 845422 - 1-8, doi:10.1117/12.2001354**

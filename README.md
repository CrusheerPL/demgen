![demgen_splash.png](https://abload.de/img/demgen_splash5sc3e.png)

***EN description below.***
# PL
**demgen** jest pomocnym narzędziem przy tworzeniu odwzorowania rzeczywistej lokalizacji w postaci mapy do Farming Simulator. Bazuje na wcześniej opublikowanej i rozwijanej paczce skryptów demGenerator.

Względem swojego poprzednika wprowadzono takie zmiany jak:
* zwiększenie komfortu obsługi poprzez złączenie wszystkich skryptów w jedną aplikację z interfejsem graficznym Tk i zminimalizowanie ryzyka wystąpienia znanych błędów
* dodanie obsługi terenów "pod kątem", tzn. takich, których płaszczyzna jest obrócona o odpowiedni kąt (szczerze, nie wiem jak to najdokładniej wytłumaczyć)
* dodanie możliwości odczytu i zapisu pliku XML z konfiguracją z/do dowolnego folderu
* dodanie możliwości wyboru lokalizacji, w której zapisywane mają być pliki
* dodanie funkcji generowania pliku KML z płaszczyzną wyznaczającą określony obszar
* zmiana sposobu pozyskiwania wszelkich danych wysokościowych, dzięki czemu proces ten może przyspieszyć.

**Kraje, których obszar można odwzorować z użyciem tego programu: Polska, Czechy, Słowacja (w produkcji - [sprawdź mapę dostępności](https://www.geoportal.sk/images/zbgis/lls/prehlad_lokalit_lls_na_poskytovanie.png)).**

---------

### Wymagania
* system operacyjny 64-bitowy (architektura x86-64), Windows 7 lub nowszy (nietestowane w Vista i 11)
* stabilne połączenie internetowe (im szybsze, tym lepiej)
* ok. 2-3 GB wolnej pamięci RAM dla najbardziej zasobożernych operacji (typu pobieranie zdjęć do tekstur; w stanie bezczynności program zużywa ok. 60 MB)
* narzędzie GIANTS Texture Tool przydatne przy tworzeniu tekstur terenu z pobranych zdjęć przystosowanych do standardów FS 22 (opcjonalnie - [pobierz z GDN (wymaga rejestracji)](https://gdn.giants-software.com/downloads.php) i wypakuj gdziekolwiek)

Dodatkowo do zbudowania pliku exe z kodu źródłowego (dla użytkowników zaawansowanych):
* środowisko Python 3.7.9 lub 3.8.10 (można 3.9+, ale wtedy program **może się nie uruchomić w systemach Windows 7 i Vista** - nie testowano)
* Visual Studio (najlepiej ostatnia wspierana wersja; przynajmniej 2017) z kompilatorem języka C oraz Windows SDK - do zbudowania bibliotek PyInstaller i/lub Pillow (wersja deweloperska)
* Biblioteki do Pythona:
  - PyInstaller
  - Pillow (przynajmniej 9.3.0.dev0 - użycie starszej wersji **może prowadzić do wycieków pamięci** w programie; w przypadku wersji deweloperskiej z GitHuba należy instalować ze zbudowanego wcześniej pliku .whl)
  - wheel
  - pytest
  - geotiff
  - imagecodecs
  - lxml
  - numpy
  - pyproj
  - requests
  - scipy

---------

### Autorzy
* główny kod programu, przekład funkcji 'wgs84_to_sjtsk' na język Python, ikona: crpl - Licencja BSD 3-Clause
* oryginalny kod źródłowy funkcji 'wgs84_to_sjtsk' w języku JavaScript: Tomáš Pecina (tomas@pecina.cz), https://www.pecina.cz/krovak.html

Generowane przez program pliki są opracowaniami publicznie dostępnych danych (produkty lotniczego skanowania laserowego oraz zdjęcia) pochodzących z niniejszych instytucji:
* Polska: Główny Urząd Geodezji i Kartografii (GUGiK) - https://www.gov.pl/web/gugik, https://geoportal.gov.pl/
* Czechy: Czech Office for Surveying, Mapping and Cadastre (Český úřad zeměměřický a katastrální, ČÚZK) - https://cuzk.cz/, https://geoportal.cuzk.cz/
* Słowacja: Geodesy, Cartography and Cadastre Authority of the Slovak Republic (Úrad geodézie, kartografie a katastra SR, ÚGKK) - https://www.skgeodesy.sk/, https://www.geoportal.sk/

**Dotyczy tylko skompilowanych paczek:**
* wbudowane środowisko Python 3.8.10, będące rozwiązaniem otwartoźródłowym, zostało wykorzystane na [licencji Python Software Foundation](http://web.archive.org/web/20210506132705/https://docs.python.org/3.8/license.html#psf-license-agreement-for-python-release).  
* wbudowane wymagane do poprawnego działania programu biblioteki do Pythona 3.8, będące rozwiązaniami otwartoźródłowymi, zostały wykorzystane zgodnie z ich odpowiednimi licencjami - więcej informacji w pliku `LICENSES_builtInSoftware.txt` w głównym katalogu repozytorium..

**Wszelkie modyfikacje dozwolone, tak samo jak i kopiowanie zawartości tego repozytorium do różnych hostingów, pod warunkiem wskazania oryginalnych autorów i źródła. W razie wystąpienia problemów z działaniem - daj znać.**  
**Z programu korzystasz wyłącznie na własną odpowiedzialność.**

# EN
**demgen** is an useful open-source tool which allows you to create a terrain for the Farming Simulator mod-map based on real elevation data. It's based on earlier released and developed demGenerator script pack.

Here are the most important changes compared to its precedessor:
* increasing the ease of use by merging all scripts into one app with Tk GUI and reducing the risk of the occurence of known issues
* adding the ability to "rotate" your target area, load/save XML file w/ configration, select the output directory and open specially prepared KML file with a plane that delimits a specific area
* changing the elevation data collecting method - thanks to this the process might speed up.

**Supported countries: Poland, Czechia, Slovakia (in development - [check the availability map](https://www.geoportal.sk/images/zbgis/lls/prehlad_lokalit_lls_na_poskytovanie.png)).**

---------

### Requirements
* 64-bit (x86-64) OS, Windows 7 or newer (not tested in Vista and 11)
* stable internet connection (faster = better)
* ca. 2-3 GB of free RAM for more resource-intensive operations (e.g. downloading photos for terrain textures; the program consumes about 60 MB when idle)
* the GIANTS Texture Tool useful when creating terrain textures adapted to FS 22 standards (optional - [download from GDN (registration required)](https://gdn.giants-software.com/downloads.php) and unzip anywhere)

Additionally, to build an executable from source code (for advanced users):
* Python 3.7.9 or 3.8.10 environment (3.9+ is allowed but the program **cannot be run in Windows 7 and Vista** - not tested)
* Visual Studio (latest supported recommended; minimum 2017) w/ C compiler and Windows SDK - to build the PyInstaller and/or Pillow (dev version) libraries
* Python packages:
  - PyInstaller
  - Pillow (minimum 9.3.0.dev0 - using earlier version **can cause memory leaks**; in case of developer version from GitHub install from previously built .whl file)
  - wheel
  - pytest
  - geotiff
  - imagecodecs
  - lxml
  - numpy
  - pyproj
  - requests
  - scipy

---------

### Authors
* main program code, 'wgs84_to_sjtsk' function translation to Python, app icon: crpl - BSD 3-Clause License
* original 'wgs84_to_sjtsk' JavaScript source code: Tomáš Pecina (tomas@pecina.cz), https://www.pecina.cz/krovak.html

Files generated by this program are compilations of publicly available data (ALS Products and imagery) from these institutions:
* Poland: Head Office of Geodesy and Cartography (Główny Urząd Geodezji i Kartografii, GUGiK) - https://www.gov.pl/web/gugik, https://geoportal.gov.pl/
* Czechia: Czech Office for Surveying, Mapping and Cadastre (Český úřad zeměměřický a katastrální, ČÚZK) - https://cuzk.cz/, https://geoportal.cuzk.cz/
* Slovakia: Geodesy, Cartography and Cadastre Authority of the Slovak Republic (Úrad geodézie, kartografie a katastra SR, ÚGKK) - https://www.skgeodesy.sk/, https://www.geoportal.sk/

**Compiled packages only:**
* built-in Python 3.8.10 environment (an open source solution) has been used in accordance with the [Python Software Foundation licence](http://web.archive.org/web/20210506132705/https://docs.python.org/3.8/license.html#psf-license-agreement-for-python-release)  
* built-in third-party Python packages required for the correct program operation (open source solutions) have been used in accordance with their respective licenses - more informations in `LICENSES_builtInSoftware.txt`.

**Any modifications allowed as well as copying the content of this repo to the various file hosting services, provided the original author and source are indicated. If you encounter any issue - let me know.**  
**You use this program only at your own risk.**

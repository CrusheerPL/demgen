/*
Autor: Zbigniew Szymanski
E-mail: z.szymanski@szymanski-net.eu
Wersja: 1.1
Historia zmian:
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
*/

/*
  Przykladowy program demonstrujacy uzycie funkcji do przeliczania wspolrzednych z
  ukladu WGS84 do ukladu PUWG 1992
*/
#include <iostream>
#include <fstream>
#include <stdio.h>
#include "wgs84_do_puwg92.h"
using namespace std;

int main(void)
{
    ifstream input("dane.txt");
    FILE * output = fopen("wyniki.txt", "w");
    if (!input) return 1;
    while (!input.eof())
    {
        double B_stopnie, L_stopnie, Xpuwg, Ypuwg;
        input >> B_stopnie >> L_stopnie;
        if (puwg92_do_wgs84(B_stopnie, L_stopnie, &Xpuwg, &Ypuwg)==0) fprintf(output, "%11.10f  %11.10f\n", Xpuwg, Ypuwg);
    }
    input.close();
    fclose(output);
    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "mkl.h"

// Paramètres du problème
#define Y0 100.0 // Population initiale
#define R 0.4 // Taux de croissance
#define K 1000.0 // Capacité limite
#define T0 0.0 // Temps initial
#define T_END 20.0 // Temps final
#define N_STEPS 10000 // Nombre d'étapes

// Solution analytique
double solution_analytique(double t) {
    return K / (1.0 + ((K - Y0) / Y0) * exp(-R * t));
}

// Dérivée pour l'équation logistique
void logistic_derivative(int n, double* t, double* y, double* dydt) {
    // dydt = r * y * (1 - y/K)
    // On utilise les fonctions BLAS de MKL
    
    // Copie y dans dydt
    cblas_dcopy(n, y, 1, dydt, 1);
    
    // dydt = -y/K
    cblas_dscal(n, -1.0/K, dydt, 1);
    
    // dydt = 1 + dydt = 1 - y/K
    double one = 1.0;
    int i;
    for(i = 0; i < n; i++) {
        dydt[i] += one;
    }
    
    // dydt = y * (1 - y/K)
    for(i = 0; i < n; i++) {
        dydt[i] *= y[i];
    }
    
    // dydt = r * y * (1 - y/K)
    cblas_dscal(n, R, dydt, 1);
}

// Méthode de Runge-Kutta d'ordre 4
void runge_kutta_4(double* t, double* y, int n_steps) {
    double h = (T_END - T0) / n_steps;
    double* k1 = (double*)mkl_malloc((n_steps+1) * sizeof(double), 64);
    double* k2 = (double*)mkl_malloc((n_steps+1) * sizeof(double), 64);
    double* k3 = (double*)mkl_malloc((n_steps+1) * sizeof(double), 64);
    double* k4 = (double*)mkl_malloc((n_steps+1) * sizeof(double), 64);
    double* y_temp = (double*)mkl_malloc((n_steps+1) * sizeof(double), 64);
    
    // Initialisation
    t[0] = T0;
    y[0] = Y0;
    
    for(int i = 0; i < n_steps; i++) {
        // k1 = h * f(t, y)
        logistic_derivative(1, &t[i], &y[i], &k1[i]);
        k1[i] *= h;
        
        // k2 = h * f(t + h/2, y + k1/2)
        t[i] += h/2;
        y_temp[i] = y[i] + k1[i]/2;
        logistic_derivative(1, &t[i], &y_temp[i], &k2[i]);
        k2[i] *= h;
        
        // k3 = h * f(t + h/2, y + k2/2)
        y_temp[i] = y[i] + k2[i]/2;
        logistic_derivative(1, &t[i], &y_temp[i], &k3[i]);
        k3[i] *= h;
        
        // k4 = h * f(t + h, y + k3)
        t[i] += h/2;
        y_temp[i] = y[i] + k3[i];
        logistic_derivative(1, &t[i], &y_temp[i], &k4[i]);
        k4[i] *= h;
        
        // y[i+1] = y[i] + (k1 + 2*k2 + 2*k3 + k4)/6
        y[i+1] = y[i] + (k1[i] + 2*k2[i] + 2*k3[i] + k4[i])/6.0;
        t[i+1] = t[i];
    }
    
    // Libération mémoire
    mkl_free(k1);
    mkl_free(k2);
    mkl_free(k3);
    mkl_free(k4);
    mkl_free(y_temp);
}

int main() {
    // Allocation alignée pour MKL
    double* t = (double*)mkl_malloc((N_STEPS+1) * sizeof(double), 64);
    double* y_numerique = (double*)mkl_malloc((N_STEPS+1) * sizeof(double), 64);
    double* y_analytique = (double*)mkl_malloc((N_STEPS+1) * sizeof(double), 64);
    
    if(!t || !y_numerique || !y_analytique) {
        printf("Erreur d'allocation mémoire\n");
        return 1;
    }
    
    printf("==================================================\n");
    printf(" Resolution Equation Logistique - RK4 avec MKL\n");
    printf("==================================================\n");
    printf("Parametres :\n");
    printf(" Population initiale y0 = %.1f\n", Y0);
    printf(" Taux de croissance r = %.1f\n", R);
    printf(" Capacite limite K = %.1f\n", K);
    printf(" Intervalle temporel : [%.1f, %.1f]\n", T0, T_END);
    printf(" Nombre d'etapes : %d\n", N_STEPS);
    printf("==================================================\n\n");
    
    // Mesure du temps d'exécution
    double start_time = dsecnd();
    
    // Résolution numérique
    runge_kutta_4(t, y_numerique, N_STEPS);
    
    double end_time = dsecnd();
    double elapsed_time = end_time - start_time;
    
    // Calcul solution analytique
    for(int i = 0; i <= N_STEPS; i++) {
        y_analytique[i] = solution_analytique(t[i]);
    }
    
    // Calcul des erreurs
    double* erreur_abs = (double*)mkl_malloc((N_STEPS+1) * sizeof(double), 64);
    for(int i = 0; i <= N_STEPS; i++) {
        erreur_abs[i] = fabs(y_numerique[i] - y_analytique[i]);
    }
    
    // Erreur maximale
    int index_max;
    double erreur_max = cblas_idamax(N_STEPS+1, erreur_abs, 1);
    index_max = (int)erreur_max;
    
    // Résultats
    printf("RESULTATS :\n");
    printf(" Temps d'execution : %.6f secondes\n", elapsed_time);
    printf(" Solution numerique finale : %.10f\n", y_numerique[N_STEPS]);
    printf(" Solution analytique finale : %.10f\n", y_analytique[N_STEPS]);
    printf(" Erreur absolue finale : %.2e\n", erreur_abs[N_STEPS]);
    printf(" Erreur relative finale : %.2e\n", 
           erreur_abs[N_STEPS] / y_analytique[N_STEPS]);
    printf(" Erreur absolue maximale : %.2e (a t = %.2f)\n", 
           erreur_abs[index_max], t[index_max]);
    printf("==================================================\n\n");
    
    // Sauvegarde des données pour traçage
    printf("Sauvegarde des donnees pour tracage...\n");
    FILE* fichier = fopen("resultats_logistique.dat", "w");
    if(fichier) {
        fprintf(fichier, "# t y_numerique y_analytique erreur_absolue\n");
        for(int i = 0; i <= N_STEPS; i += N_STEPS/200) { // Échantillonnage pour le traçage
            fprintf(fichier, "%.6f %.10f %.10f %.2e\n", 
                    t[i], y_numerique[i], y_analytique[i], erreur_abs[i]);
        }
        fclose(fichier);
        printf("Donnees sauvegardees dans 'resultats_logistique.dat'\n");
    } else {
        printf("Erreur lors de la creation du fichier de sortie\n");
    }
    
    // Instructions pour le traçage avec GNUplot
    printf("\nPour tracer les resultats avec GNUplot :\n");
    printf("----------------------------------------\n");
    printf("1. Creer un script GNUplot (trace.gp) :\n\n");
    printf("set terminal pngcairo enhanced size 1200,800\n");
    printf("set output 'logistique_rk4_mkl.png'\n");
    printf("set multiplot layout 2,1\n");
    printf("set title 'Resolution Equation Logistique - RK4 avec MKL'\n");
    printf("set xlabel 'Temps (t)'\n");
    printf("set ylabel 'Population y(t)'\n");
    printf("plot 'resultats_logistique.dat' using 1:2 with lines lw 2 title 'Numerique (RK4)', \\\n");
    printf(" 'resultats_logistique.dat' using 1:3 with lines lw 2 dt 2 title 'Analytique'\n");
    printf("set title 'Erreur Absolue'\n");
    printf("set ylabel '|y_{num} - y_{ana}|'\n");
    printf("set logscale y\n");
    printf("plot 'resultats_logistique.dat' using 1:4 with lines lw 2 title 'Erreur absolue'\n");
    printf("unset multiplot\n");
    printf("unset output\n");
    printf("\n2. Executer : gnuplot trace.gp\n");
    printf("==================================================\n");
    
    // Libération mémoire
    mkl_free(t);
    mkl_free(y_numerique);
    mkl_free(y_analytique);
    mkl_free(erreur_abs);
    
    return 0;
}
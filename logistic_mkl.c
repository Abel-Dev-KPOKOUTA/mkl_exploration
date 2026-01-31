/*
 * ============================================================================
 * Résolution de l'équation logistique par méthode de Runge-Kutta d'ordre 4
 * Avec Intel Math Kernel Library (MKL)
 * ============================================================================
 * 
 * Équation différentielle : dy/dt = r*y*(1 - y/K)
 * 
 * Paramètres :
 *   - y0 = 100    : Population initiale (bactéries)
 *   - r  = 0.4    : Taux de croissance (h^-1)
 *   - K  = 1000   : Capacité limite
 *   - t  = [0,20] : Intervalle de temps (heures)
 * 
 * Compilation :
 *   gcc -O3 -o logistic_mkl logistic_mkl.c \
 *       -I$MKLROOT/include \
 *       -L$MKLROOT/lib/intel64 \
 *       -lmkl_rt -lpthread -lm -ldl
 * 
 * Exécution :
 *   ./logistic_mkl
 * ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "mkl.h"

// ============================================================================
// Fonction dérivée de l'équation logistique
// ============================================================================
double logistic_derivative(double t, double y, double r, double K) {
    return r * y * (1.0 - y / K);
}

// ============================================================================
// Méthode de Runge-Kutta d'ordre 4 (RK4)
// ============================================================================
void runge_kutta_4(double *y, double t0, double t_end,
                   int n_steps, double r, double K) {
    double h = (t_end - t0) / n_steps;  // Pas de temps
    double t = t0;
    
    for(int i = 0; i < n_steps; i++) {
        // Calcul des 4 pentes k1, k2, k3, k4
        double k1 = h * logistic_derivative(t, *y, r, K);
        double k2 = h * logistic_derivative(t + h/2.0, *y + k1/2.0, r, K);
        double k3 = h * logistic_derivative(t + h/2.0, *y + k2/2.0, r, K);
        double k4 = h * logistic_derivative(t + h, *y + k3, r, K);
        
        // Mise à jour de y
        *y += (k1 + 2.0*k2 + 2.0*k3 + k4) / 6.0;
        t += h;
    }
}

// ============================================================================
// Solution analytique de l'équation logistique
// ============================================================================
double logistic_analytical(double t, double y0, double r, double K) {
    return K / (1.0 + ((K - y0) / y0) * exp(-r * t));
}

// ============================================================================
// Programme principal
// ============================================================================
int main() {
    // ------------------------------------------------------------------------
    // Paramètres du problème
    // ------------------------------------------------------------------------
    double y0 = 100.0;      // Population initiale
    double r = 0.4;         // Taux de croissance
    double K = 1000.0;      // Capacité limite
    double t0 = 0.0;        // Temps initial
    double t_end = 20.0;    // Temps final
    int n_steps = 10000;    // Nombre de pas de temps
    
    // ------------------------------------------------------------------------
    // Résolution numérique avec RK4
    // ------------------------------------------------------------------------
    double y_numerical = y0;
    
    // Mesure du temps d'exécution avec la fonction MKL dsecnd()
    double start_time = dsecnd();
    runge_kutta_4(&y_numerical, t0, t_end, n_steps, r, K);
    double elapsed_time = dsecnd() - start_time;
    
    // ------------------------------------------------------------------------
    // Solution analytique
    // ------------------------------------------------------------------------
    double y_exact = logistic_analytical(t_end, y0, r, K);
    
    // ------------------------------------------------------------------------
    // Calcul des erreurs
    // ------------------------------------------------------------------------
    double error_abs = fabs(y_numerical - y_exact);
    double error_rel = error_abs / y_exact;
    
    // ------------------------------------------------------------------------
    // Affichage des résultats
    // ------------------------------------------------------------------------
    printf("\n");
    printf("========================================================================\n");
    printf("    RÉSOLUTION DE L'ÉQUATION LOGISTIQUE - MÉTHODE RUNGE-KUTTA 4       \n");
    printf("========================================================================\n");
    printf("\n");
    printf("PARAMÈTRES DU PROBLÈME :\n");
    printf("  Population initiale (y0)  : %.1f bactéries\n", y0);
    printf("  Taux de croissance (r)    : %.2f h^-1\n", r);
    printf("  Capacité limite (K)       : %.1f bactéries\n", K);
    printf("  Intervalle de temps       : [%.1f, %.1f] heures\n", t0, t_end);
    printf("  Nombre de pas (n_steps)   : %d\n", n_steps);
    printf("  Pas de temps (h)          : %.6f heures\n", (t_end - t0) / n_steps);
    printf("\n");
    printf("------------------------------------------------------------------------\n");
    printf("RÉSULTATS À t = %.1f heures :\n", t_end);
    printf("------------------------------------------------------------------------\n");
    printf("  Solution numérique (RK4)  : %.10f bactéries\n", y_numerical);
    printf("  Solution analytique       : %.10f bactéries\n", y_exact);
    printf("\n");
    printf("------------------------------------------------------------------------\n");
    printf("ANALYSE DE L'ERREUR :\n");
    printf("------------------------------------------------------------------------\n");
    printf("  Erreur absolue            : %.2e\n", error_abs);
    printf("  Erreur relative           : %.2e (%.6f%%)\n", error_rel, error_rel * 100);
    printf("\n");
    printf("------------------------------------------------------------------------\n");
    printf("PERFORMANCES :\n");
    printf("------------------------------------------------------------------------\n");
    printf("  Temps d'exécution         : %.6f secondes\n", elapsed_time);
    printf("  Temps par itération       : %.2e secondes\n", elapsed_time / n_steps);
    printf("  Itérations par seconde    : %.2e\n", n_steps / elapsed_time);
    printf("\n");
    printf("========================================================================\n");
    printf("  Bibliothèque : Intel Math Kernel Library (MKL)\n");
    printf("  Version MKL  : %d.%d.%d\n", __INTEL_MKL__, __INTEL_MKL_MINOR__, __INTEL_MKL_UPDATE__);
    printf("========================================================================\n");
    printf("\n");
    
    return 0;
}

/*
 * ============================================================================
 * NOTES THÉORIQUES :
 * ============================================================================
 * 
 * L'équation logistique de Verhulst modélise la croissance d'une population
 * avec ressources limitées :
 * 
 *   dy/dt = r*y*(1 - y/K)
 * 
 * où :
 *   - y(t) : population au temps t
 *   - r    : taux de croissance intrinsèque
 *   - K    : capacité de charge de l'environnement
 * 
 * Solution analytique :
 * 
 *   y(t) = K / (1 + ((K-y0)/y0) * exp(-r*t))
 * 
 * Méthode RK4 :
 *   k1 = h * f(t_n, y_n)
 *   k2 = h * f(t_n + h/2, y_n + k1/2)
 *   k3 = h * f(t_n + h/2, y_n + k2/2)
 *   k4 = h * f(t_n + h, y_n + k3)
 *   y_{n+1} = y_n + (k1 + 2*k2 + 2*k3 + k4) / 6
 * 
 * Propriétés RK4 :
 *   - Ordre 4 : erreur locale O(h^5)
 *   - Erreur globale O(h^4)
 *   - 4 évaluations de f par pas
 * 
 * ============================================================================
 */

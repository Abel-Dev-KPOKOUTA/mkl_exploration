/******************************************************************************
 * svd_compress.c - COMPRESSION SVD AVEC BLAS/LAPACK (OpenBLAS)
 * 
 * Cette version utilise les bibliothèques BLAS/LAPACK standard
 * Compatible avec: OpenBLAS, ATLAS, Netlib LAPACK
 * 
 * Auteurs: KPOKOUTA Abel, OUSSOUKPEVI Richenel, ANAHAHOUNDE A. Fredy
 * UNSTIM - ENSGMM | 2025-2026
 ******************************************************************************/

#include "svd_compress.h"
#include <string.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <cblas.h>      // BLAS (cblas_dgemm, cblas_dcopy, etc.)
#include <lapacke.h>    // LAPACK (LAPACKE_dgesvd)

/******************************************************************************
 * Créer une structure SVD
 ******************************************************************************/
SVD* svd_create(int m, int n) {
    SVD *svd = (SVD*)malloc(sizeof(SVD));
    if (!svd) return NULL;
    
    svd->m = m;
    svd->n = n;
    svd->min_dim = (m < n) ? m : n;
    svd->computed = 0;
    
    // Allocation standard (pas besoin de mkl_malloc)
    svd->U = (double*)calloc(m * m, sizeof(double));
    svd->S = (double*)calloc(svd->min_dim, sizeof(double));
    svd->VT = (double*)calloc(n * n, sizeof(double));
    
    if (!svd->U || !svd->S || !svd->VT) {
        svd_free(svd);
        return NULL;
    }
    
    return svd;
}

/******************************************************************************
 * Libérer une structure SVD
 ******************************************************************************/
void svd_free(SVD *svd) {
    if (svd) {
        if (svd->U) free(svd->U);
        if (svd->S) free(svd->S);
        if (svd->VT) free(svd->VT);
        free(svd);
    }
}

/******************************************************************************
 * Obtenir le temps en secondes (pour chronométrage)
 ******************************************************************************/
static double get_time() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

/******************************************************************************
 * VRAIE SVD AVEC LAPACK - LAPACKE_dgesvd
 ******************************************************************************/
int svd_compute(Image *img, SVD *svd) {
    if (!img || !svd) return -1;
    
    printf("\n╔══════════════════════════════════════════════════════════╗\n");
    printf("║  CALCUL SVD AVEC LAPACK (LAPACKE_dgesvd)                ║\n");
    printf("╚══════════════════════════════════════════════════════════╝\n\n");
    
    int m = img->height;
    int n = img->width;
    
    printf("   Image: %d × %d pixels\n", m, n);
    printf("   Nombre de valeurs singulières: %d\n\n", svd->min_dim);
    
    // Copier les données de l'image (LAPACKE_dgesvd modifie la matrice !)
    double *A_copy = (double*)malloc(m * n * sizeof(double));
    if (!A_copy) {
        fprintf(stderr, "   ✗ Erreur allocation mémoire\n");
        return -1;
    }
    
    // Copie simple (pas de cblas_dcopy si pas disponible)
    memcpy(A_copy, img->data, m * n * sizeof(double));
    
    // Tableau de travail pour LAPACKE_dgesvd
    double *superb = (double*)malloc((svd->min_dim - 1) * sizeof(double));
    if (!superb) {
        free(A_copy);
        return -1;
    }
    
    printf("   Lancement LAPACKE_dgesvd...\n");
    
    // Chronométrage
    double t_start = get_time();
    
    // ════════════════════════════════════════════════════════════════════
    // APPEL CRITIQUE : LAPACKE_dgesvd
    // ════════════════════════════════════════════════════════════════════
    lapack_int info = LAPACKE_dgesvd(
        LAPACK_ROW_MAJOR,  // Layout (C standard)
        'A',               // jobu: calculer toute la matrice U (m×m)
        'A',               // jobvt: calculer toute la matrice V^T (n×n)
        m,                 // Nombre de lignes
        n,                 // Nombre de colonnes
        A_copy,            // Matrice A (sera détruite)
        n,                 // Leading dimension de A
        svd->S,            // OUTPUT: valeurs singulières (min_dim)
        svd->U,            // OUTPUT: matrice U (m×m)
        m,                 // Leading dimension de U
        svd->VT,           // OUTPUT: matrice V^T (n×n)
        n,                 // Leading dimension de VT
        superb             // Tableau de travail
    );
    
    double t_elapsed = (get_time() - t_start) * 1000.0;  // En millisecondes
    
    free(A_copy);
    free(superb);
    
    // Vérifier le code de retour
    if (info != 0) {
        fprintf(stderr, "   ✗ ERREUR LAPACKE_dgesvd: code %d\n", (int)info);
        if (info < 0) {
            fprintf(stderr, "      Paramètre %d invalide\n", -(int)info);
        } else {
            fprintf(stderr, "      Algorithme n'a pas convergé\n");
        }
        return -1;
    }
    
    printf("   ✓ SVD calculée en %.2f ms\n\n", t_elapsed);
    
    // Afficher les valeurs singulières principales
    printf("   Valeurs singulières principales:\n");
    printf("      σ₁  = %.2f\n", svd->S[0]);
    if (svd->min_dim >= 2) printf("      σ₂  = %.2f\n", svd->S[1]);
    if (svd->min_dim >= 5) printf("      σ₅  = %.2f\n", svd->S[4]);
    if (svd->min_dim >= 10) printf("      σ₁₀ = %.2f\n", svd->S[9]);
    if (svd->min_dim >= 50) printf("      σ₅₀ = %.2f\n", svd->S[49]);
    
    printf("\n");
    
    svd->computed = 1;
    return 0;
}

/******************************************************************************
 * COMPRESSION SVD - Reconstruction avec k premières valeurs
 * Utilise cblas_dgemm pour multiplication matricielle optimisée
 ******************************************************************************/
Image* svd_compress(SVD *svd, int k) {
    if (!svd || !svd->computed) {
        fprintf(stderr, "   ✗ SVD non calculée\n");
        return NULL;
    }
    
    int m = svd->m;  // hauteur
    int n = svd->n;  // largeur
    
    if (k > svd->min_dim) k = svd->min_dim;
    if (k < 1) k = 1;
    
    printf("   [k=%d] Reconstruction %d×%d...\n", k, m, n);
    
    // Créer l'image résultat
    Image *result = image_create(n, m);
    if (!result) return NULL;
    
    // ════════════════════════════════════════════════════════════════════
    // RECONSTRUCTION OPTIMISÉE: A_k = U_k × Σ_k × V_k^T
    // ════════════════════════════════════════════════════════════════════
    
    // Étape 1: Calculer U_k × Σ_k (multiplication élément par élément)
    // Résultat: matrice Temp de taille m×k
    double *Temp = (double*)malloc(m * k * sizeof(double));
    if (!Temp) {
        image_free(result);
        return NULL;
    }
    
    // Pour chaque colonne j de U_k, multiplier par σ_j
    for (int j = 0; j < k; j++) {
        for (int i = 0; i < m; i++) {
            Temp[i * k + j] = svd->U[i * m + j] * svd->S[j];
        }
    }
    
    // Étape 2: Multiplier Temp × V_k^T avec cblas_dgemm (BLAS Level 3)
    // Temp (m×k) × VT_k (k×n) = A_k (m×n)
    
    printf("      Multiplication Temp × V_k^T avec cblas_dgemm...\n");
    
    cblas_dgemm(
        CblasRowMajor,     // Layout
        CblasNoTrans,      // Temp non transposée
        CblasNoTrans,      // VT non transposée (déjà transposée)
        m,                 // Lignes de Temp
        n,                 // Colonnes de VT
        k,                 // Colonnes de Temp = Lignes de VT
        1.0,               // Alpha (coefficient)
        Temp,              // Matrice Temp (m×k)
        k,                 // Leading dimension de Temp
        svd->VT,           // Matrice VT (k×n) - on prend les k premières lignes
        n,                 // Leading dimension de VT
        0.0,               // Beta (on écrase le résultat)
        result->data,      // OUTPUT: matrice résultat (m×n)
        n                  // Leading dimension du résultat
    );
    
    free(Temp);
    
    // Clamper les valeurs entre 0 et 255
    for (int i = 0; i < m * n; i++) {
        if (result->data[i] < 0.0) result->data[i] = 0.0;
        if (result->data[i] > 255.0) result->data[i] = 255.0;
    }
    
    result->max_value = 255;
    
    printf("      ✓ Image reconstruite\n");
    
    return result;
}

/******************************************************************************
 * Calculer le PSNR (Peak Signal-to-Noise Ratio)
 ******************************************************************************/
double svd_compute_psnr(Image *original, Image *compressed) {
    if (!original || !compressed) return 0.0;
    
    if (original->width != compressed->width || 
        original->height != compressed->height) {
        return 0.0;
    }
    
    int n = original->width * original->height;
    
    // Calculer MSE (Mean Squared Error)
    double mse = 0.0;
    for (int i = 0; i < n; i++) {
        double diff = original->data[i] - compressed->data[i];
        mse += diff * diff;
    }
    mse /= n;
    
    // Si MSE est très petit, la qualité est excellente
    if (mse < 1e-10) {
        return 100.0;  // Valeur arbitraire pour "parfait"
    }
    
    // PSNR = 10 × log₁₀(255² / MSE)
    double psnr = 10.0 * log10((255.0 * 255.0) / mse);
    
    return psnr;
}

/******************************************************************************
 * Calculer le taux de compression
 ******************************************************************************/
double svd_compression_ratio(int m, int n, int k) {
    int original_size = m * n;
    int compressed_size = k * (m + n + 1);
    
    if (compressed_size == 0) return 0.0;
    
    return (double)original_size / (double)compressed_size;
}

/******************************************************************************
 * Calculer l'énergie conservée
 ******************************************************************************/
double svd_energy_retained(SVD *svd, int k) {
    if (!svd || !svd->computed) return 0.0;
    
    if (k > svd->min_dim) k = svd->min_dim;
    if (k < 1) return 0.0;
    
    // Énergie totale = somme des carrés de toutes les valeurs singulières
    double total_energy = 0.0;
    for (int i = 0; i < svd->min_dim; i++) {
        total_energy += svd->S[i] * svd->S[i];
    }
    
    // Énergie conservée avec k valeurs
    double retained_energy = 0.0;
    for (int i = 0; i < k; i++) {
        retained_energy += svd->S[i] * svd->S[i];
    }
    
    if (total_energy < 1e-10) return 0.0;
    
    return (retained_energy / total_energy) * 100.0;
}

/******************************************************************************
 * Exporter les valeurs singulières dans un fichier CSV
 ******************************************************************************/
void svd_export_singular_values(SVD *svd, const char *filename) {
    if (!svd || !svd->computed) return;
    
    FILE *fp = fopen(filename, "w");
    if (!fp) {
        fprintf(stderr, "Erreur: impossible de créer %s\n", filename);
        return;
    }
    
    fprintf(fp, "Index,SingularValue,Energy,CumulativeEnergy\n");
    
    // Calculer l'énergie totale
    double total_energy = 0.0;
    for (int i = 0; i < svd->min_dim; i++) {
        total_energy += svd->S[i] * svd->S[i];
    }
    
    // Écrire chaque valeur singulière
    double cumulative = 0.0;
    for (int i = 0; i < svd->min_dim; i++) {
        double energy = svd->S[i] * svd->S[i];
        cumulative += energy;
        double percent = (cumulative / total_energy) * 100.0;
        
        fprintf(fp, "%d,%.6f,%.6f,%.2f\n", 
                i + 1, svd->S[i], energy, percent);
    }
    
    fclose(fp);
    printf("   ✓ Valeurs singulières exportées: %s\n", filename);
}
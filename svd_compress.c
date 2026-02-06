#include "svd_compress.h"
#include <string.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

// Définitions pour LAPACK et BLAS
#include <lapacke.h>
#include <cblas.h>

/******************************************************************************
 * Créer une structure SVD optimisée pour LAPACK
 ******************************************************************************/
SVD* svd_create(int m, int n) {
    SVD *svd = (SVD*)malloc(sizeof(SVD));
    if (!svd) return NULL;
    
    svd->m = m;
    svd->n = n;
    svd->min_dim = (m < n) ? m : n;
    svd->computed = 0;
    
    // Allocation optimisée : U (m × min_dim), VT (min_dim × n)
    svd->U = (double*)calloc(m * svd->min_dim, sizeof(double));
    svd->S = (double*)calloc(svd->min_dim, sizeof(double));
    svd->VT = (double*)calloc(svd->min_dim * n, sizeof(double));
    
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
 * Calculer la SVD avec LAPACK (dgelsd - divide and conquer)
 ******************************************************************************/
int svd_compute(Image *img, SVD *svd) {
    if (!img || !svd) return -1;
    
    printf("\n╔════════════════════════════════════════════════════════════╗\n");
    printf("║  CALCUL DE LA DÉCOMPOSITION SVD (LAPACK)                 ║\n");
    printf("╚════════════════════════════════════════════════════════════╝\n\n");
    
    int m = img->height;
    int n = img->width;
    int min_dim = svd->min_dim;
    
    printf("   Dimensions: %d × %d pixels\n", m, n);
    printf("   Mémoire allouée: %.2f MB\n", 
           (m * min_dim + min_dim * n + min_dim) * sizeof(double) / (1024.0 * 1024.0));
    
    // 1. Préparer la matrice d'entrée (copie pour ne pas modifier l'original)
    double *A = (double*)malloc(m * n * sizeof(double));
    if (!A) {
        printf("   [ERREUR] Allocation mémoire échouée\n");
        return -1;
    }
    
    // Copier et transposer si nécessaire (LAPACK utilise column-major)
    // Pour les images, on travaille généralement avec m lignes (hauteur) × n colonnes (largeur)
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            A[j * m + i] = img->data[i * n + j];  // Column-major
        }
    }
    
    // 2. Appel à LAPACK dgesvd (SVD complète)
    clock_t start = clock();
    
    // Variables pour LAPACK
    int lda = m;        // Leading dimension of A
    int ldu = m;        // Leading dimension of U
    int ldvt = min_dim; // Leading dimension of VT
    int info;
    double *work;
    int lwork = -1;
    double work_query;
    
    // Requête de la taille optimale de work
    info = LAPACKE_dgesvd(LAPACK_COL_MAJOR, 
                         'S',    // U: m × min_dim
                         'S',    // VT: min_dim × n
                         m, n, A, lda,
                         svd->S,
                         svd->U, ldu,
                         svd->VT, ldvt,
                         &work_query, lwork);
    
    if (info != 0) {
        printf("   [ERREUR LAPACK] dgesvd work query failed: %d\n", info);
        free(A);
        return -1;
    }
    
    // Allouer le workspace optimal
    lwork = (int)work_query;
    work = (double*)malloc(lwork * sizeof(double));
    if (!work) {
        printf("   [ERREUR] Allocation workspace échouée\n");
        free(A);
        return -1;
    }
    
    // Calculer la SVD
    info = LAPACKE_dgesvd(LAPACK_COL_MAJOR,
                         'S', 'S',
                         m, n, A, lda,
                         svd->S,
                         svd->U, ldu,
                         svd->VT, ldvt,
                         work, lwork);
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    // Nettoyer
    free(work);
    free(A);
    
    if (info != 0) {
        printf("   [ERREUR LAPACK] dgesvd failed: %d\n", info);
        return -1;
    }
    
    printf("   ✓ SVD calculée en %.3f secondes\n", elapsed);
    printf("   ✓ Plage des valeurs singulières: σ₁=%.2f, σ_%d=%.2f\n", 
           svd->S[0], min_dim, svd->S[min_dim-1]);
    
    svd->computed = 1;
    return 0;
}

/******************************************************************************
 * Reconstruction SVD avec BLAS pour l'optimisation
 ******************************************************************************/
Image* svd_compress(SVD *svd, int k) {
    if (!svd || !svd->computed) {
        printf("   [ERREUR] SVD non calculée\n");
        return NULL;
    }
    
    if (k > svd->min_dim) k = svd->min_dim;
    if (k < 1) k = 1;
    
    int m = svd->m;
    int n = svd->n;
    
    printf("   [COMPRESSION k=%d] Reconstruction %dx%d\n", k, m, n);
    
    // Créer l'image résultat
    Image *result = image_create(n, m);
    if (!result) return NULL;
    
    // 1. Allouer les matrices temporaires
    double *U_k = (double*)malloc(m * k * sizeof(double));
    double *VT_k = (double*)malloc(k * n * sizeof(double));
    double *S_k = (double*)malloc(k * sizeof(double));
    double *temp = (double*)calloc(m * n, sizeof(double));
    
    if (!U_k || !VT_k || !S_k || !temp) {
        printf("   [ERREUR] Allocation temporaire échouée\n");
        if (U_k) free(U_k);
        if (VT_k) free(VT_k);
        if (S_k) free(S_k);
        if (temp) free(temp);
        image_free(result);
        return NULL;
    }
    
    // 2. Extraire les k premières composantes
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < k; j++) {
            U_k[i + j * m] = svd->U[i + j * m];
        }
    }
    
    for (int i = 0; i < k; i++) {
        S_k[i] = svd->S[i];
        for (int j = 0; j < n; j++) {
            VT_k[i + j * k] = svd->VT[i + j * svd->min_dim];
        }
    }
    
    // 3. Reconstruction: A_k = U_k * diag(S_k) * VT_k
    // Étape 1: temp = diag(S_k) * VT_k
    for (int i = 0; i < k; i++) {
        double sigma = S_k[i];
        cblas_dscal(n, sigma, &VT_k[i], k);  // BLAS: scale rows of VT_k by sigma
    }
    
    // Étape 2: result = U_k * temp (avec BLAS dgemm)
    // Note: On utilise column-major, donc U_k (m×k) * temp (k×n) = résultat (m×n)
    double alpha = 1.0;
    double beta = 0.0;
    cblas_dgemm(CblasColMajor, CblasNoTrans, CblasNoTrans,
                m, n, k,
                alpha,
                U_k, m,
                VT_k, k,
                beta,
                temp, m);
    
    // 4. Copier le résultat dans l'image (et transposer de column-major à row-major)
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            double val = temp[j * m + i];  // Column-major to row-major
            // Clamper les valeurs
            if (val < 0.0) val = 0.0;
            if (val > 255.0) val = 255.0;
            result->data[i * n + j] = val;
        }
    }
    
    // 5. Calculer les statistiques
    double min_val = result->data[0];
    double max_val = result->data[0];
    double sum = 0.0;
    
    for (int i = 0; i < m * n; i++) {
        double val = result->data[i];
        if (val < min_val) min_val = val;
        if (val > max_val) max_val = val;
        sum += val;
    }
    
    printf("   [STATISTIQUES] Min=%.1f, Max=%.1f, Moyenne=%.1f\n", 
           min_val, max_val, sum / (m * n));
    printf("   ✓ Image compressée générée (k=%d)\n", k);
    
    // Nettoyer
    free(U_k);
    free(VT_k);
    free(S_k);
    free(temp);
    
    result->max_value = 255;
    return result;
}

/******************************************************************************
 * Calculer le PSNR (Peak Signal-to-Noise Ratio)
 ******************************************************************************/
double svd_compute_psnr(Image *original, Image *compressed) {
    if (!original || !compressed) return 0.0;
    if (original->width != compressed->width || 
        original->height != compressed->height) return 0.0;
    
    int m = original->height;
    int n = original->width;
    int total = m * n;
    
    if (total == 0) return 0.0;
    
    // Calculer MSE avec BLAS pour plus de rapidité sur les grandes images
    double mse = 0.0;
    
    // Créer un vecteur de différences
    double *diff = (double*)malloc(total * sizeof(double));
    if (!diff) {
        // Fallback: calcul manuel
        for (int i = 0; i < total; i++) {
            double d = original->data[i] - compressed->data[i];
            mse += d * d;
        }
    } else {
        // Utiliser BLAS: diff = original - compressed
        memcpy(diff, original->data, total * sizeof(double));
        cblas_daxpy(total, -1.0, compressed->data, 1, diff, 1);
        
        // Calculer la norme au carré avec BLAS
        mse = cblas_ddot(total, diff, 1, diff, 1);
        free(diff);
    }
    
    mse /= total;
    
    if (mse < 1e-10) return 99.99;
    
    // PSNR = 20 * log10(MAX) - 10 * log10(MSE)
    return 20.0 * log10(255.0) - 10.0 * log10(mse);
}

/******************************************************************************
 * Calculer le taux de compression
 ******************************************************************************/
double svd_compression_ratio(int m, int n, int k) {
    // Stockage original: m * n doubles
    // Stockage compressé: m * k + k + k * n doubles
    double original_size = m * n;
    double compressed_size = m * k + k + k * n;
    
    return original_size / compressed_size;
}

/******************************************************************************
 * Calculer l'énergie conservée
 ******************************************************************************/
double svd_energy_retained(SVD *svd, int k) {
    if (!svd || !svd->computed) return 0.0;
    
    if (k > svd->min_dim) k = svd->min_dim;
    if (k < 1) return 0.0;
    
    // Calculer l'énergie totale et partielle
    double total_energy = cblas_ddot(svd->min_dim, svd->S, 1, svd->S, 1);
    double partial_energy = cblas_ddot(k, svd->S, 1, svd->S, 1);
    
    if (total_energy < 1e-10) return 0.0;
    
    return (partial_energy / total_energy) * 100.0;
}

/******************************************************************************
 * Exporter les valeurs singulières dans un fichier CSV
 ******************************************************************************/
void svd_export_singular_values(SVD *svd, const char *filename) {
    if (!svd || !svd->computed || !filename) return;
    
    FILE *fp = fopen(filename, "w");
    if (!fp) {
        printf("   [ERREUR] Impossible d'ouvrir %s\n", filename);
        return;
    }
    
    fprintf(fp, "Index,ValeurSinguliere,EnergieCumulee\n");
    
    double total_energy = 0.0;
    for (int i = 0; i < svd->min_dim; i++) {
        total_energy += svd->S[i] * svd->S[i];
    }
    
    double cumulative_energy = 0.0;
    for (int i = 0; i < svd->min_dim; i++) {
        cumulative_energy += svd->S[i] * svd->S[i];
        double percent = (cumulative_energy / total_energy) * 100.0;
        fprintf(fp, "%d,%.6f,%.6f\n", i+1, svd->S[i], percent);
    }
    
    fclose(fp);
    printf("   ✓ Valeurs singulières exportées: %s\n", filename);
}
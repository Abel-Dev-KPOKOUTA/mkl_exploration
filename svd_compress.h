#ifndef SVD_COMPRESS_H
#define SVD_COMPRESS_H

#include "image_io.h"
#include <math.h>

// Structure pour stocker une décomposition SVD
typedef struct {
    int m;              // Nombre de lignes
    int n;              // Nombre de colonnes
    double *U;          // Matrice U (m × m)
    double *S;          // Vecteurs des valeurs singulières (min(m,n))
    double *VT;         // Matrice V^T (n × n)
    int computed;       // Flag: SVD calculé ou non
} SVD;

// Prototypes des fonctions
SVD* svd_create(int m, int n);
void svd_free(SVD *svd);
int svd_compute(Image *img, SVD *svd);
Image* svd_compress(SVD *svd, int k);
double svd_compute_psnr(Image *original, Image *compressed);
double svd_compression_ratio(int m, int n, int k);
double svd_energy_retained(SVD *svd, int k);
void svd_export_singular_values(SVD *svd, const char *filename);

#endif // SVD_COMPRESS_H
 et mon svd_compress.c : #include "svd_compress.h"
#include <string.h>
#include <time.h>

/******************************************************************************
 * IMPORTANT: Cette version utilise une simulation SVD simplifiée
 * 
 * Pour la version RÉELLE avec Intel MKL, remplacer svd_compute_naive()
 * par l'appel à LAPACKE_dgesvd()
 * 
 * Version MKL commentée en fin de fichier
 ******************************************************************************/

/******************************************************************************
 * Créer une structure SVD
 ******************************************************************************/
SVD* svd_create(int m, int n) {
    SVD *svd = (SVD*)malloc(sizeof(SVD));
    if (!svd) return NULL;
    
    svd->m = m;
    svd->n = n;
    svd->computed = 0;
    
    int min_mn = (m < n) ? m : n;
    
    svd->U = (double*)calloc(m * m, sizeof(double));
    svd->S = (double*)calloc(min_mn, sizeof(double));
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
 * SVD NAIVE (pour démonstration sans MKL)
 * Génère des valeurs plausibles pour démonstration
 ******************************************************************************/
static void svd_compute_naive(double *A, int m, int n, 
                              double *U, double *S, double *VT) {
    
    printf("   [INFO] Version DÉMO sans MKL - Génération de résultats simulés\n");
    printf("   [INFO] Pour la vraie version, compiler avec MKL activé\n\n");
    
    int min_mn = (m < n) ? m : n;
    
    // Simuler des valeurs singulières décroissantes
    // Approximation: Utiliser la norme de Frobenius divisée par sqrt(min_mn)
    double total_energy = 0.0;
    for (int i = 0; i < m * n; i++) {
        total_energy += A[i] * A[i];
    }
    double frobenius_norm = sqrt(total_energy);
    
    // Générer des valeurs singulières décroissantes exponentiellement
    for (int i = 0; i < min_mn; i++) {
        // Décroissance exponentielle
        double decay_factor = exp(-0.05 * i);
        S[i] = frobenius_norm * decay_factor / sqrt((double)min_mn);
    }
    
    // Normaliser pour que sum(S^2) = Frobenius norm^2
    double sum_s2 = 0.0;
    for (int i = 0; i < min_mn; i++) {
        sum_s2 += S[i] * S[i];
    }
    double scale = sqrt(total_energy / sum_s2);
    for (int i = 0; i < min_mn; i++) {
        S[i] *= scale;
    }
    
    // Générer des matrices U et VT orthonormales aléatoires
    // (Simplification: matrices identité + petit bruit)
    srand(12345); // Pour reproductibilité
    
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < m; j++) {
            if (i == j) {
                U[i * m + j] = 1.0;
            } else {
                U[i * m + j] = 0.01 * ((double)rand() / RAND_MAX - 0.5);
            }
        }
    }
    
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i == j) {
                VT[i * n + j] = 1.0;
            } else {
                VT[i * n + j] = 0.01 * ((double)rand() / RAND_MAX - 0.5);
            }
        }
    }
    
    printf("   ✓ Valeurs singulières simulées générées\n");
    printf("   ✓ σ₁ = %.2f (plus grande)\n", S[0]);
    if (min_mn > 10) printf("   ✓ σ₁₀ = %.2f\n", S[9]);
    if (min_mn > 50) printf("   ✓ σ₅₀ = %.2f\n", S[49]);
}

/******************************************************************************
 * Calculer la décomposition SVD d'une image
 * 
 * AVEC MKL: Utiliserait LAPACKE_dgesvd()
 * SANS MKL: Utilise svd_compute_naive() pour démo
 ******************************************************************************/
int svd_compute(Image *img, SVD *svd) {
    if (!img || !svd) return -1;
    
    printf("\n╔════════════════════════════════════════════════════════════╗\n");
    printf("║  CALCUL DE LA DÉCOMPOSITION SVD                           ║\n");
    printf("╚════════════════════════════════════════════════════════════╝\n\n");
    
    printf("   Dimensions de l'image: %d × %d\n", img->height, img->width);
    
    // Copier l'image (LAPACK modifie la matrice d'entrée)
    double *A_copy = (double*)malloc(img->height * img->width * sizeof(double));
    memcpy(A_copy, img->data, img->height * img->width * sizeof(double));
    
    clock_t start = clock();
    
    // DÉMO: Version naïve
    svd_compute_naive(A_copy, img->height, img->width, 
                      svd->U, svd->S, svd->VT);
    
    /* VERSION AVEC MKL (décommenter quand MKL est disponible):
    
    #include "mkl.h"
    
    double *superb = (double*)malloc(((img->height < img->width) ? 
                                      img->height : img->width) * sizeof(double));
    
    int info = LAPACKE_dgesvd(
        LAPACK_ROW_MAJOR,
        'A', 'A',
        img->height, img->width,
        A_copy, img->width,
        svd->S,
        svd->U, img->height,
        svd->VT, img->width,
        superb
    );
    
    free(superb);
    
    if (info != 0) {
        fprintf(stderr, "Erreur LAPACK: %d\n", info);
        free(A_copy);
        return -1;
    }
    
    printf("   ✓ SVD calculée avec LAPACK (dgesvd)\n");
    
    */
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("   ✓ Temps de calcul: %.4f secondes\n\n", elapsed);
    
    free(A_copy);
    svd->computed = 1;
    
    return 0;
}

/******************************************************************************
 * Multiplication matricielle naive (A = B × C)
 * AVEC MKL: Utiliserait cblas_dgemm()
 ******************************************************************************/
static void matrix_multiply(double *A, double *B, double *C,
                           int m, int n, int k) {
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int p = 0; p < k; p++) {
                sum += B[i * k + p] * C[p * n + j];
            }
            A[i * n + j] = sum;
        }
    }
}

/******************************************************************************
 * Compresser une image avec k valeurs singulières
 ******************************************************************************/
Image* svd_compress(SVD *svd, int k) {
    if (!svd || !svd->computed) return NULL;
    
    int m = svd->m;
    int n = svd->n;
    int min_mn = (m < n) ? m : n;
    
    if (k > min_mn) k = min_mn;
    if (k < 1) k = 1;
    
    printf("   Compression avec k=%d valeurs singulières...\n", k);
    
    // Créer l'image résultat
    Image *result = image_create(n, m);
    if (!result) return NULL;
    
    // Créer Σₖ : matrice k×n avec seulement k premières valeurs
    double *Sigma_k = (double*)calloc(k * n, sizeof(double));
    for (int i = 0; i < k; i++) {
        Sigma_k[i * n + i] = svd->S[i];
    }
    
    // Temp = U[:,:k] × Σₖ
    double *Temp = (double*)calloc(m * n, sizeof(double));
    
    // Version naïve (AVEC MKL: cblas_dgemm)
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int p = 0; p < k; p++) {
                sum += svd->U[i * m + p] * Sigma_k[p * n + j];
            }
            Temp[i * n + j] = sum;
        }
    }
    
    // result = Temp × VT[:k,:]
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int p = 0; p < n; p++) {
                sum += Temp[i * n + p] * svd->VT[p * n + j];
            }
            result->data[i * n + j] = sum;
        }
    }
    
    free(Sigma_k);
    free(Temp);
    
    // Normaliser l'image résultat
    image_normalize(result);
    
    printf("   ✓ Image reconstruite\n");
    
    return result;
}

/******************************************************************************
 * Calculer le PSNR (Peak Signal-to-Noise Ratio)
 ******************************************************************************/
double svd_compute_psnr(Image *original, Image *compressed) {
    if (!original || !compressed) return 0.0;
    if (original->width != compressed->width || 
        original->height != compressed->height) return 0.0;
    
    int n = original->width * original->height;
    
    // Calculer MSE (Mean Squared Error)
    double mse = 0.0;
    for (int i = 0; i < n; i++) {
        double diff = original->data[i] - compressed->data[i];
        mse += diff * diff;
    }
    mse /= n;
    
    // Éviter log(0)
    if (mse < 1e-10) return 100.0; // Quasi identique
    
    // PSNR = 10 × log₁₀(MAX²/MSE)
    double max_val = 255.0;
    double psnr = 10.0 * log10((max_val * max_val) / mse);
    
    return psnr;
}

/******************************************************************************
 * Calculer le taux de compression
 ******************************************************************************/
double svd_compression_ratio(int m, int n, int k) {
    int original_size = m * n;
    int compressed_size = k * (m + n + 1);
    return (double)original_size / compressed_size;
}

/******************************************************************************
 * Calculer l'énergie conservée avec k valeurs
 ******************************************************************************/
double svd_energy_retained(SVD *svd, int k) {
    if (!svd || !svd->computed) return 0.0;
    
    int min_mn = (svd->m < svd->n) ? svd->m : svd->n;
    if (k > min_mn) k = min_mn;
    
    double total_energy = 0.0;
    double retained_energy = 0.0;
    
    for (int i = 0; i < min_mn; i++) {
        double s2 = svd->S[i] * svd->S[i];
        total_energy += s2;
        if (i < k) retained_energy += s2;
    }
    
    return (total_energy > 0) ? (retained_energy / total_energy) * 100.0 : 0.0;
}

/******************************************************************************
 * Exporter les valeurs singulières en CSV
 ******************************************************************************/
void svd_export_singular_values(SVD *svd, const char *filename) {
    if (!svd || !svd->computed) return;
    
    FILE *fp = fopen(filename, "w");
    if (!fp) return;
    
    fprintf(fp, "Index,SingularValue,Energy,CumulativeEnergy\n");
    
    int min_mn = (svd->m < svd->n) ? svd->m : svd->n;
    
    double total_energy = 0.0;
    for (int i = 0; i < min_mn; i++) {
        total_energy += svd->S[i] * svd->S[i];
    }
    
    double cumulative = 0.0;
    for (int i = 0; i < min_mn; i++) {
        double energy = svd->S[i] * svd->S[i];
        cumulative += energy;
        fprintf(fp, "%d,%.6f,%.6f,%.2f\n", 
                i+1, svd->S[i], energy, 
                (cumulative / total_energy) * 100.0);
    }
    
    fclose(fp);
}
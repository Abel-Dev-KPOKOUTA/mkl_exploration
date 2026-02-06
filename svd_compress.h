#ifndef SVD_COMPRESS_H
#define SVD_COMPRESS_H

#include "image_io.h"
#include <math.h>

// Structure pour stocker une décomposition SVD
typedef struct {
    int m;              // Nombre de lignes (hauteur)
    int n;              // Nombre de colonnes (largeur)
    int min_dim;        // min(m, n)
    double *U;          // Matrice U (m × min_dim)
    double *S;          // Vecteur des valeurs singulières (min_dim)
    double *VT;         // Matrice V^T (min_dim × n)
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
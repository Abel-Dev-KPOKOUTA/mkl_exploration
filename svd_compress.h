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

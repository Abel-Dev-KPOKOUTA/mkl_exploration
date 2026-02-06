#include "image_io.h"
#include <ctype.h>

/******************************************************************************
 * Créer une nouvelle image
 ******************************************************************************/
Image* image_create(int width, int height) {
    Image *img = (Image*)malloc(sizeof(Image));
    if (!img) return NULL;
    
    img->width = width;
    img->height = height;
    img->max_value = 255;
    img->data = (double*)calloc(width * height, sizeof(double));
    
    if (!img->data) {
        free(img);
        return NULL;
    }
    
    return img;
}

/******************************************************************************
 * Libérer la mémoire d'une image
 ******************************************************************************/
void image_free(Image *img) {
    if (img) {
        if (img->data) free(img->data);
        free(img);
    }
}

/******************************************************************************
 * Sauter les commentaires dans un fichier PGM
 ******************************************************************************/
static void skip_comments(FILE *fp) {
    int c;
    while ((c = fgetc(fp)) == '#') {
        while ((c = fgetc(fp)) != '\n' && c != EOF);
    }
    ungetc(c, fp);
}

/******************************************************************************
 * Charger une image PGM (Portable Gray Map)
 * Format: P2 (ASCII) ou P5 (binaire)
 ******************************************************************************/
Image* image_load_pgm(const char *filename) {
    FILE *fp = fopen(filename, "rb");
    if (!fp) {
        fprintf(stderr, "Erreur: Impossible d'ouvrir %s\n", filename);
        return NULL;
    }
    
    // Lire le magic number
    char magic[3];
    if (fscanf(fp, "%2s", magic) != 1) {
        fprintf(stderr, "Erreur: Format PGM invalide\n");
        fclose(fp);
        return NULL;
    }
    
    if (strcmp(magic, "P2") != 0 && strcmp(magic, "P5") != 0) {
        fprintf(stderr, "Erreur: Format non supporté (attendu P2 ou P5)\n");
        fclose(fp);
        return NULL;
    }
    
    int is_binary = (strcmp(magic, "P5") == 0);
    
    // Sauter les espaces et commentaires
    skip_comments(fp);
    
    // Lire dimensions
    int width, height, max_val;
    if (fscanf(fp, "%d %d %d", &width, &height, &max_val) != 3) {
        fprintf(stderr, "Erreur: En-tête PGM invalide\n");
        fclose(fp);
        return NULL;
    }
    
    // Créer l'image
    Image *img = image_create(width, height);
    if (!img) {
        fclose(fp);
        return NULL;
    }
    img->max_value = max_val;
    
    // Lire les données
    fgetc(fp); // Sauter le dernier \n
    
    if (is_binary) {
        // Format P5 (binaire)
        unsigned char *buffer = (unsigned char*)malloc(width * height);
        if (fread(buffer, 1, width * height, fp) != (size_t)(width * height)) {
            fprintf(stderr, "Erreur: Lecture des données échouée\n");
            free(buffer);
            image_free(img);
            fclose(fp);
            return NULL;
        }
        
        // Convertir en double
        for (int i = 0; i < width * height; i++) {
            img->data[i] = (double)buffer[i];
        }
        free(buffer);
        
    } else {
        // Format P2 (ASCII)
        for (int i = 0; i < width * height; i++) {
            int val;
            if (fscanf(fp, "%d", &val) != 1) {
                fprintf(stderr, "Erreur: Lecture pixel %d échouée\n", i);
                image_free(img);
                fclose(fp);
                return NULL;
            }
            img->data[i] = (double)val;
        }
    }
    
    fclose(fp);
    return img;
}

/******************************************************************************
 * Sauvegarder une image au format PGM (P5 - binaire)
 ******************************************************************************/
int image_save_pgm(const char *filename, Image *img) {
    if (!img) return -1;
    
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        fprintf(stderr, "Erreur: Impossible de créer %s\n", filename);
        return -1;
    }
    
    // Écrire l'en-tête
    fprintf(fp, "P5\n");
    fprintf(fp, "# Created by SVD Compression Tool\n");
    fprintf(fp, "%d %d\n", img->width, img->height);
    fprintf(fp, "%d\n", img->max_value);
    
    // Convertir et écrire les données
    unsigned char *buffer = (unsigned char*)malloc(img->width * img->height);
    
    for (int i = 0; i < img->width * img->height; i++) {
        // Clamper entre 0 et max_value
        double val = img->data[i];
        if (val < 0.0) val = 0.0;
        if (val > img->max_value) val = img->max_value;
        buffer[i] = (unsigned char)(val + 0.5); // Arrondi
    }
    
    fwrite(buffer, 1, img->width * img->height, fp);
    
    free(buffer);
    fclose(fp);
    return 0;
}

/******************************************************************************
 * Copier une image
 ******************************************************************************/
Image* image_copy(Image *src) {
    if (!src) return NULL;
    
    Image *dst = image_create(src->width, src->height);
    if (!dst) return NULL;
    
    dst->max_value = src->max_value;
    memcpy(dst->data, src->data, src->width * src->height * sizeof(double));
    
    return dst;
}

/******************************************************************************
 * Normaliser une image (pour l'affichage)
 ******************************************************************************/
void image_normalize(Image *img) {
    if (!img) return;
    
    // Trouver min et max
    double min_val = img->data[0];
    double max_val = img->data[0];
    
    for (int i = 1; i < img->width * img->height; i++) {
        if (img->data[i] < min_val) min_val = img->data[i];
        if (img->data[i] > max_val) max_val = img->data[i];
    }
    
    // Éviter division par zéro
    if (max_val - min_val < 1e-10) return;
    
    // Normaliser à [0, 255]
    for (int i = 0; i < img->width * img->height; i++) {
        img->data[i] = 255.0 * (img->data[i] - min_val) / (max_val - min_val);
    }
    
    img->max_value = 255;
}


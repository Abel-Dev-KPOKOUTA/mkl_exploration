// #include "image_io.h"
// #include <ctype.h>

// /******************************************************************************
//  * Créer une nouvelle image
//  ******************************************************************************/
// Image* image_create(int width, int height) {
//     Image *img = (Image*)malloc(sizeof(Image));
//     if (!img) return NULL;
    
//     img->width = width;
//     img->height = height;
//     img->max_value = 255;
//     img->data = (double*)calloc(width * height, sizeof(double));
    
//     if (!img->data) {
//         free(img);
//         return NULL;
//     }
    
//     return img;
// }

// /******************************************************************************
//  * Libérer la mémoire d'une image
//  ******************************************************************************/
// void image_free(Image *img) {
//     if (img) {
//         if (img->data) free(img->data);
//         free(img);
//     }
// }

// /******************************************************************************
//  * Sauter les commentaires dans un fichier PGM
//  ******************************************************************************/
// static void skip_comments(FILE *fp) {
//     int c;
//     while ((c = fgetc(fp)) == '#') {
//         while ((c = fgetc(fp)) != '\n' && c != EOF);
//     }
//     ungetc(c, fp);
// }

// /******************************************************************************
//  * Charger une image PGM (Portable Gray Map)
//  * Format: P2 (ASCII) ou P5 (binaire)
//  ******************************************************************************/
// Image* image_load_pgm(const char *filename) {
//     FILE *fp = fopen(filename, "rb");
//     if (!fp) {
//         fprintf(stderr, "Erreur: Impossible d'ouvrir %s\n", filename);
//         return NULL;
//     }
    
//     // Lire le magic number
//     char magic[3];
//     if (fscanf(fp, "%2s", magic) != 1) {
//         fprintf(stderr, "Erreur: Format PGM invalide\n");
//         fclose(fp);
//         return NULL;
//     }
    
//     if (strcmp(magic, "P2") != 0 && strcmp(magic, "P5") != 0) {
//         fprintf(stderr, "Erreur: Format non supporté (attendu P2 ou P5)\n");
//         fclose(fp);
//         return NULL;
//     }
    
//     int is_binary = (strcmp(magic, "P5") == 0);
    
//     // Sauter les espaces et commentaires
//     skip_comments(fp);
    
//     // Lire dimensions
//     int width, height, max_val;
//     if (fscanf(fp, "%d %d %d", &width, &height, &max_val) != 3) {
//         fprintf(stderr, "Erreur: En-tête PGM invalide\n");
//         fclose(fp);
//         return NULL;
//     }
    
//     // Créer l'image
//     Image *img = image_create(width, height);
//     if (!img) {
//         fclose(fp);
//         return NULL;
//     }
//     img->max_value = max_val;
    
//     // Lire les données
//     fgetc(fp); // Sauter le dernier \n
    
//     if (is_binary) {
//         // Format P5 (binaire)
//         unsigned char *buffer = (unsigned char*)malloc(width * height);
//         if (fread(buffer, 1, width * height, fp) != (size_t)(width * height)) {
//             fprintf(stderr, "Erreur: Lecture des données échouée\n");
//             free(buffer);
//             image_free(img);
//             fclose(fp);
//             return NULL;
//         }
        
//         // Convertir en double
//         for (int i = 0; i < width * height; i++) {
//             img->data[i] = (double)buffer[i];
//         }
//         free(buffer);
        
//     } else {
//         // Format P2 (ASCII)
//         for (int i = 0; i < width * height; i++) {
//             int val;
//             if (fscanf(fp, "%d", &val) != 1) {
//                 fprintf(stderr, "Erreur: Lecture pixel %d échouée\n", i);
//                 image_free(img);
//                 fclose(fp);
//                 return NULL;
//             }
//             img->data[i] = (double)val;
//         }
//     }
    
//     fclose(fp);
//     return img;
// }

// /******************************************************************************
//  * Sauvegarder une image au format PGM (P5 - binaire)
//  ******************************************************************************/
// int image_save_pgm(const char *filename, Image *img) {
//     if (!img) return -1;
    
//     FILE *fp = fopen(filename, "wb");
//     if (!fp) {
//         fprintf(stderr, "Erreur: Impossible de créer %s\n", filename);
//         return -1;
//     }
    
//     // Écrire l'en-tête
//     fprintf(fp, "P5\n");
//     fprintf(fp, "# Created by SVD Compression Tool\n");
//     fprintf(fp, "%d %d\n", img->width, img->height);
//     fprintf(fp, "%d\n", img->max_value);
    
//     // Convertir et écrire les données
//     unsigned char *buffer = (unsigned char*)malloc(img->width * img->height);
    
//     for (int i = 0; i < img->width * img->height; i++) {
//         // Clamper entre 0 et max_value
//         double val = img->data[i];
//         if (val < 0.0) val = 0.0;
//         if (val > img->max_value) val = img->max_value;
//         buffer[i] = (unsigned char)(val + 0.5); // Arrondi
//     }
    
//     fwrite(buffer, 1, img->width * img->height, fp);
    
//     free(buffer);
//     fclose(fp);
//     return 0;
// }

// /******************************************************************************
//  * Copier une image
//  ******************************************************************************/
// Image* image_copy(Image *src) {
//     if (!src) return NULL;
    
//     Image *dst = image_create(src->width, src->height);
//     if (!dst) return NULL;
    
//     dst->max_value = src->max_value;
//     memcpy(dst->data, src->data, src->width * src->height * sizeof(double));
    
//     return dst;
// }

// /******************************************************************************
//  * Normaliser une image (pour l'affichage)
//  ******************************************************************************/
// void image_normalize(Image *img) {
//     if (!img) return;
    
//     // Trouver min et max
//     double min_val = img->data[0];
//     double max_val = img->data[0];
    
//     for (int i = 1; i < img->width * img->height; i++) {
//         if (img->data[i] < min_val) min_val = img->data[i];
//         if (img->data[i] > max_val) max_val = img->data[i];
//     }
    
//     // Éviter division par zéro
//     if (max_val - min_val < 1e-10) return;
    
//     // Normaliser à [0, 255]
//     for (int i = 0; i < img->width * img->height; i++) {
//         img->data[i] = 255.0 * (img->data[i] - min_val) / (max_val - min_val);
//     }
    
//     img->max_value = 255;
// }







#include "image_io.h"
#include <ctype.h>
#include <math.h>

/******************************************************************************
 * Vérifier si un fichier est texte (non binaire)
 ******************************************************************************/
int is_text_file(const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (!file) return 0;
    
    int is_text = 1;
    int c;
    int count = 0;
    
    while ((c = fgetc(file)) != EOF && count < 1024) {
        if ((c < 32 || c > 126) && c != '\n' && c != '\r' && c != '\t' && c != '\0') {
            if (c != 0x1A) { // EOF dans certains fichiers texte
                is_text = 0;
                break;
            }
        }
        count++;
    }
    
    fclose(file);
    return is_text;
}

/******************************************************************************
 * Sauter les commentaires dans un fichier texte
 ******************************************************************************/
static void skip_text_comments(FILE *fp) {
    int c;
    while ((c = fgetc(fp)) == '#') {
        while ((c = fgetc(fp)) != '\n' && c != EOF);
    }
    ungetc(c, fp);
}

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
        fclose(fp);
        return NULL; // Pas un fichier PGM valide
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
    printf("   ✓ Image PGM chargée: %d×%d pixels\n", width, height);
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
 * VERSION AMÉLIORÉE avec messages de débogage
 ******************************************************************************/
void image_normalize(Image *img) {
    if (!img) return;
    
    int total_pixels = img->width * img->height;
    if (total_pixels == 0) return;
    
    // Vérifier si déjà normalisé
    int already_normalized = 1;
    for (int i = 0; i < total_pixels; i++) {
        if (img->data[i] < 0.0 || img->data[i] > 255.0) {
            already_normalized = 0;
            break;
        }
    }
    
    if (already_normalized && img->max_value == 255) {
        return; // Déjà normalisé
    }
    
    // Trouver min et max réels
    double min_val = img->data[0];
    double max_val = img->data[0];
    
    for (int i = 1; i < total_pixels; i++) {
        if (img->data[i] < min_val) min_val = img->data[i];
        if (img->data[i] > max_val) max_val = img->data[i];
    }
    
    // Debug
    printf("   [NORMALIZE] Min=%.2f, Max=%.2f, Range=%.2f\n", 
           min_val, max_val, max_val - min_val);
    
    // Cas particulier: toutes valeurs identiques
    if (max_val - min_val < 1e-10) {
        printf("   [NORMALIZE] Toutes valeurs identiques (~%.2f)\n", min_val);
        if (fabs(min_val) < 1e-10) {
            // Valeurs proches de 0 -> gris moyen
            for (int i = 0; i < total_pixels; i++) {
                img->data[i] = 128.0;
            }
        } else {
            // Valeur constante non nulle
            for (int i = 0; i < total_pixels; i++) {
                img->data[i] = fmin(255.0, fmax(0.0, min_val));
            }
        }
        img->max_value = 255;
        return;
    }
    
    // Normalisation linéaire
    double scale = 255.0 / (max_val - min_val);
    printf("   [NORMALIZE] Scale factor=%.6f\n", scale);
    
    int clamped_count = 0;
    for (int i = 0; i < total_pixels; i++) {
        double normalized = (img->data[i] - min_val) * scale;
        
        // Clamper
        if (normalized < 0.0) {
            normalized = 0.0;
            clamped_count++;
        } else if (normalized > 255.0) {
            normalized = 255.0;
            clamped_count++;
        }
        
        img->data[i] = normalized;
    }
    
    if (clamped_count > 0) {
        printf("   [NORMALIZE] %d pixels clampés (%.1f%%)\n", 
               clamped_count, 100.0 * clamped_count / total_pixels);
    }
    
    img->max_value = 255;
}

/******************************************************************************
 * Charger une matrice depuis un fichier texte simple
 ******************************************************************************/
Image* image_load_matrix(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Erreur: Impossible d'ouvrir %s\n", filename);
        return NULL;
    }
    
    // Sauter les commentaires initiaux
    skip_text_comments(file);
    
    // Essayer de lire les dimensions (format 1: lignes colonnes en tête)
    int rows, cols;
    int has_dimensions = 0;
    
    // Sauvegarder la position
    long pos = ftell(file);
    
    if (fscanf(file, "%d %d", &rows, &cols) == 2) {
        // Vérifier si les dimensions sont raisonnables
        if (rows > 0 && rows < 10000 && cols > 0 && cols < 10000) {
            has_dimensions = 1;
        }
    }
    
    if (!has_dimensions) {
        // Format 2: pas de dimensions, compter lignes et colonnes
        rewind(file);
        skip_text_comments(file);
        
        char line[8192];
        rows = 0;
        cols = 0;
        
        // Compter lignes et déterminer colonnes
        while (fgets(line, sizeof(line), file)) {
            // Nettoyer la ligne
            line[strcspn(line, "\n\r")] = 0;
            
            // Ignorer les lignes vides ou commentaires
            if (line[0] == '\0' || line[0] == '#') {
                continue;
            }
            
            // Compter les colonnes sur la première ligne
            if (rows == 0) {
                char *token;
                char line_copy[8192];
                strcpy(line_copy, line);
                
                token = strtok(line_copy, " \t,;");
                while (token) {
                    cols++;
                    token = strtok(NULL, " \t,;");
                }
            }
            rows++;
        }
        
        if (rows == 0 || cols == 0) {
            fprintf(stderr, "Erreur: Fichier matrice vide ou invalide\n");
            fclose(file);
            return NULL;
        }
        
        // Retourner au début pour lire les données
        rewind(file);
        skip_text_comments(file);
    } else {
        // On a déjà les dimensions, on est positionné après elles
        pos = ftell(file);
    }
    
    printf("   Lecture d'une matrice %d×%d...\n", rows, cols);
    
    // Allouer la mémoire pour la matrice temporaire
    double **temp_data = (double**)malloc(rows * sizeof(double*));
    if (!temp_data) {
        fclose(file);
        return NULL;
    }
    
    for (int i = 0; i < rows; i++) {
        temp_data[i] = (double*)malloc(cols * sizeof(double));
        if (!temp_data[i]) {
            for (int j = 0; j < i; j++) free(temp_data[j]);
            free(temp_data);
            fclose(file);
            return NULL;
        }
    }
    
    // Revenir à la position des données
    if (has_dimensions) {
        fseek(file, pos, SEEK_SET);
    } else {
        rewind(file);
        skip_text_comments(file);
    }
    
    // Lire les données
    char line[8192];
    int line_num = 0;
    
    while (fgets(line, sizeof(line), file) && line_num < rows) {
        // Nettoyer la ligne
        line[strcspn(line, "\n\r")] = 0;
        
        // Ignorer les lignes vides ou commentaires
        if (line[0] == '\0' || line[0] == '#') {
            continue;
        }
        
        // Parser la ligne
        char *token = strtok(line, " \t,;");
        int col_num = 0;
        
        while (token && col_num < cols) {
            // Parser le nombre
            char *endptr;
            double value = strtod(token, &endptr);
            
            if (endptr == token) {
                // Échec de conversion
                fprintf(stderr, "Erreur: Valeur invalide à la ligne %d, colonne %d: '%s'\n", 
                       line_num + 1, col_num + 1, token);
                for (int i = 0; i < rows; i++) free(temp_data[i]);
                free(temp_data);
                fclose(file);
                return NULL;
            }
            
            temp_data[line_num][col_num] = value;
            col_num++;
            token = strtok(NULL, " \t,;");
        }
        
        // Vérifier le nombre de colonnes
        if (col_num != cols) {
            fprintf(stderr, "Erreur: Ligne %d a %d colonnes au lieu de %d\n", 
                   line_num + 1, col_num, cols);
            for (int i = 0; i < rows; i++) free(temp_data[i]);
            free(temp_data);
            fclose(file);
            return NULL;
        }
        
        line_num++;
    }
    
    fclose(file);
    
    if (line_num != rows) {
        fprintf(stderr, "Erreur: %d lignes lues au lieu de %d\n", line_num, rows);
        for (int i = 0; i < rows; i++) free(temp_data[i]);
        free(temp_data);
        return NULL;
    }
    
    // Créer l'image (width = cols, height = rows)
    Image *img = image_create(cols, rows);
    if (!img) {
        for (int i = 0; i < rows; i++) free(temp_data[i]);
        free(temp_data);
        return NULL;
    }
    
    // Copier les données
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            img->data[i * cols + j] = temp_data[i][j];
        }
        free(temp_data[i]);
    }
    free(temp_data);
    
    // Normaliser pour affichage
    image_normalize(img);
    printf("   ✓ Matrice chargée avec succès\n");
    
    return img;
}

/******************************************************************************
 * Charger une matrice depuis un fichier CSV
 ******************************************************************************/
Image* image_load_csv(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Erreur: Impossible d'ouvrir %s\n", filename);
        return NULL;
    }
    
    char line[8192];
    int rows = 0, cols = 0;
    double **temp_data = NULL;
    
    printf("   Lecture d'un fichier CSV...\n");
    
    // Première passe: compter lignes et colonnes
    while (fgets(line, sizeof(line), file)) {
        // Nettoyer la ligne
        line[strcspn(line, "\n\r")] = 0;
        
        // Ignorer les lignes vides ou commentaires
        if (line[0] == '\0' || line[0] == '#') {
            continue;
        }
        
        // Compter les colonnes sur la première ligne non vide
        if (rows == 0) {
            char line_copy[8192];
            strcpy(line_copy, line);
            
            char *token = strtok(line_copy, ",;");
            while (token) {
                // Nettoyer le token
                char *clean_token = token;
                while (*clean_token == ' ' || *clean_token == '\t') clean_token++;
                char *end = clean_token + strlen(clean_token) - 1;
                while (end > clean_token && (*end == ' ' || *end == '\t')) end--;
                *(end + 1) = '\0';
                
                if (strlen(clean_token) > 0) {
                    cols++;
                }
                token = strtok(NULL, ",;");
            }
            
            if (cols == 0) {
                fprintf(stderr, "Erreur: Fichier CSV vide\n");
                fclose(file);
                return NULL;
            }
            
            // Allouer la mémoire temporaire
            temp_data = (double**)malloc(sizeof(double*) * 1000); // Capacité initiale
            if (!temp_data) {
                fclose(file);
                return NULL;
            }
        }
        
        // Allouer la ligne
        if (rows % 1000 == 0) { // Réallouer par blocs de 1000
            temp_data = (double**)realloc(temp_data, sizeof(double*) * (rows + 1000));
            if (!temp_data) {
                fclose(file);
                return NULL;
            }
        }
        
        temp_data[rows] = (double*)malloc(sizeof(double) * cols);
        if (!temp_data[rows]) {
            fclose(file);
            for (int i = 0; i < rows; i++) free(temp_data[i]);
            free(temp_data);
            return NULL;
        }
        
        // Parser les valeurs
        char *token = strtok(line, ",;");
        for (int j = 0; j < cols && token; j++) {
            // Nettoyer le token
            char *clean_token = token;
            while (*clean_token == ' ' || *clean_token == '\t') clean_token++;
            char *end = clean_token + strlen(clean_token) - 1;
            while (end > clean_token && (*end == ' ' || *end == '\t')) end--;
            *(end + 1) = '\0';
            
            char *endptr;
            temp_data[rows][j] = strtod(clean_token, &endptr);
            
            if (endptr == clean_token) {
                fprintf(stderr, "Erreur: Valeur invalide à la ligne %d, colonne %d: '%s'\n", 
                       rows + 1, j + 1, clean_token);
                for (int i = 0; i <= rows; i++) free(temp_data[i]);
                free(temp_data);
                fclose(file);
                return NULL;
            }
            
            token = strtok(NULL, ",;");
        }
        
        rows++;
    }
    
    fclose(file);
    
    if (rows == 0 || cols == 0) {
        fprintf(stderr, "Erreur: Fichier CSV vide ou invalide\n");
        if (temp_data) {
            for (int i = 0; i < rows; i++) free(temp_data[i]);
            free(temp_data);
        }
        return NULL;
    }
    
    printf("   ✓ CSV détecté: %d lignes × %d colonnes\n", rows, cols);
    
    // Créer l'image
    Image *img = image_create(cols, rows);
    if (!img) {
        for (int i = 0; i < rows; i++) free(temp_data[i]);
        free(temp_data);
        return NULL;
    }
    
    // Copier les données
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            img->data[i * cols + j] = temp_data[i][j];
        }
        free(temp_data[i]);
    }
    free(temp_data);
    
    // Normaliser pour affichage
    image_normalize(img);
    printf("   ✓ Données CSV chargées\n");
    
    return img;
}

/******************************************************************************
 * Détection automatique du format et chargement
 ******************************************************************************/
Image* image_load_auto(const char *filename) {
    if (!filename) return NULL;
    
    // Vérifier l'extension du fichier
    const char *ext = strrchr(filename, '.');
    
    if (ext) {
        // Convertir en minuscules
        char ext_lower[10];
        strncpy(ext_lower, ext, sizeof(ext_lower));
        for (int i = 0; ext_lower[i]; i++) {
            ext_lower[i] = tolower(ext_lower[i]);
        }
        
        // Charger selon l'extension
        if (strcmp(ext_lower, ".pgm") == 0) {
            return image_load_pgm(filename);
        } else if (strcmp(ext_lower, ".csv") == 0) {
            return image_load_csv(filename);
        } else if (strcmp(ext_lower, ".txt") == 0 || 
                  strcmp(ext_lower, ".mat") == 0 || 
                  strcmp(ext_lower, ".dat") == 0) {
            return image_load_matrix(filename);
        }
    }
    
    // Si pas d'extension ou extension inconnue, détection automatique
    if (is_text_file(filename)) {
        // Essayer d'abord comme matrice texte
        Image *img = image_load_matrix(filename);
        if (img) return img;
        
        // Essayer comme CSV
        img = image_load_csv(filename);
        if (img) return img;
    } else {
        // Essayer comme PGM
        Image *img = image_load_pgm(filename);
        if (img) return img;
    }
    
    // Échec de tous les essais
    fprintf(stderr, "Erreur: Format de fichier non reconnu: %s\n", filename);
    return NULL;
}
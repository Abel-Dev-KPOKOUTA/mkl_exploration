// /****************************************************************************** 
//  * Description:
//  *   Ce programme démontre la compression d'images en utilisant la SVD.
//  *   Il calcule la décomposition, génère des versions compressées avec
//  *   différentes valeurs de k, et mesure les performances.
//  * 
//  * Compilation:
//  *   Sans MKL (démo): gcc -O3 -o svd_demo main.c image_io.c svd_compress.c -lm
//  *   Avec MKL: gcc -O3 -o svd_mkl main.c image_io.c svd_compress.c \
//  *             -I$MKLROOT/include -L$MKLROOT/lib/intel64 \
//  *             -lmkl_rt -lpthread -lm -ldl
//  ******************************************************************************/

// #include <stdio.h>
// #include <stdlib.h>
// #include <string.h>
// #include "image_io.h"
// #include "svd_compress.h"

// // Tableau des valeurs de k à tester
// static const int K_VALUES[] = {5, 10, 25, 50, 75, 100, 150, 200};
// static const int N_K_VALUES = 8;

// /******************************************************************************
//  * Afficher le logo et les informations
//  ******************************************************************************/
// void print_header() {
//     printf("\n");
//     printf("╔══════════════════════════════════════════════════════════════════╗\n");
//     printf("║                                                                  ║\n");
//     printf("║        COMPRESSION D'IMAGES PAR DÉCOMPOSITION SVD                ║\n");
//     printf("║              avec Intel Math Kernel Library                      ║\n");
//     printf("║                                                                  ║\n");
//     printf("║  Singular Value Decomposition: A = U × Σ × V^T                  ║\n");
//     printf("║                                                                  ║\n");
//     printf("╚══════════════════════════════════════════════════════════════════╝\n");
//     printf("\n");
//     printf("  📚 Projet: Modélisation Mathématique & Calcul Scientifique\n");
//     printf("  🎓 UNSTIM - ENSGMM | Année 2025-2026\n");
//     printf("  👥 Par: KPOKOUTA Abel, OUSSOUKPEVI Richenel, ANAHAHOUNDE A. Fredy\n");
//     printf("\n");
// }

// /******************************************************************************
//  * Créer une image de test (dégradé) si aucune image n'est fournie
//  ******************************************************************************/
// Image* create_test_image(int width, int height) {
//     Image *img = image_create(width, height);
//     if (!img) return NULL;
    
//     printf("   Génération d'une image de test %d×%d...\n", width, height);
    
//     // Créer un motif de test (cercles concentriques + dégradé)
//     int cx = width / 2;
//     int cy = height / 2;
//     double max_dist = sqrt(cx*cx + cy*cy);
    
//     for (int y = 0; y < height; y++) {
//         for (int x = 0; x < width; x++) {
//             int dx = x - cx;
//             int dy = y - cy;
//             double dist = sqrt(dx*dx + dy*dy);
            
//             // Motif: cercles + dégradé
//             double value = 128.0 + 127.0 * sin(dist / max_dist * 10.0 * 3.14159);
//             value += (x / (double)width) * 50.0;
            
//             img->data[y * width + x] = value;
//         }
//     }
    
//     image_normalize(img);
//     printf("   ✓ Image de test générée\n\n");
    
//     return img;
// }

// /******************************************************************************
//  * Traiter une image : SVD + compression
//  ******************************************************************************/
// int process_image(const char *input_file, const char *output_dir) {
    
//     // 1. Charger l'image
//     printf("╔══════════════════════════════════════════════════════════════════╗\n");
//     printf("║  ÉTAPE 1/4: CHARGEMENT DE L'IMAGE                               ║\n");
//     printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
    
//     Image *img = NULL;
    
//     if (input_file) {
//         printf("   Chargement depuis: %s\n", input_file);
//         img = image_load_pgm(input_file);
//         if (!img) {
//             printf("   ⚠ Échec du chargement, création d'une image de test...\n\n");
//             img = create_test_image(256, 256);
//         } else {
//             printf("   ✓ Image chargée: %d×%d pixels\n\n", img->width, img->height);
//         }
//     } else {
//         printf("   Aucune image fournie, création d'une image de test...\n\n");
//         img = create_test_image(256, 256);
//     }
    
//     if (!img) {
//         fprintf(stderr, "Erreur fatale: Impossible de créer/charger l'image\n");
//         return -1;
//     }
    
//     // Sauvegarder l'image originale
//     char orig_path[512];
//     snprintf(orig_path, sizeof(orig_path), "%s/original.pgm", output_dir);
//     image_save_pgm(orig_path, img);
//     printf("   ✓ Image originale sauvegardée: %s\n\n", orig_path);
    
//     // 2. Calculer la SVD
//     printf("╔══════════════════════════════════════════════════════════════════╗\n");
//     printf("║  ÉTAPE 2/4: DÉCOMPOSITION SVD                                   ║\n");
//     printf("╚══════════════════════════════════════════════════════════════════╝\n");
    
//     SVD *svd = svd_create(img->height, img->width);
//     if (!svd) {
//         fprintf(stderr, "Erreur: Allocation SVD échouée\n");
//         image_free(img);
//         return -1;
//     }
    
//     if (svd_compute(img, svd) != 0) {
//         fprintf(stderr, "Erreur: Calcul SVD échoué\n");
//         svd_free(svd);
//         image_free(img);
//         return -1;
//     }
    
//     // Exporter les valeurs singulières
//     char sv_path[512];
//     snprintf(sv_path, sizeof(sv_path), "%s/../data/singular_values.csv", output_dir);
//     svd_export_singular_values(svd, sv_path);
//     printf("   ✓ Valeurs singulières exportées: %s\n\n", sv_path);
    
//     // 3. Compression avec différentes valeurs de k
//     printf("╔══════════════════════════════════════════════════════════════════╗\n");
//     printf("║  ÉTAPE 3/4: COMPRESSION AVEC DIFFÉRENTES VALEURS DE k           ║\n");
//     printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
    
//     printf("┌─────┬──────────┬───────────────┬──────────────┬──────────────┐\n");
//     printf("│  k  │   PSNR   │  Compression  │   Énergie    │   Qualité    │\n");
//     printf("│     │   (dB)   │     Ratio     │   Conservée  │              │\n");
//     printf("├─────┼──────────┼───────────────┼──────────────┼──────────────┤\n");
    
//     // Créer le fichier de résultats
//     char results_path[512];
//     snprintf(results_path, sizeof(results_path), "%s/../data/compression_results.csv", output_dir);
//     FILE *results_fp = fopen(results_path, "w");
//     if (results_fp) {
//         fprintf(results_fp, "k,PSNR_dB,CompressionRatio,EnergyPercent,Quality\n");
//     }
    
//     for (int i = 0; i < N_K_VALUES; i++) {
//         int k = K_VALUES[i];
        
//         // Vérifier que k est valide
//         int min_dim = (img->height < img->width) ? img->height : img->width;
//         if (k > min_dim) continue;
        
//         // Compresser
//         Image *compressed = svd_compress(svd, k);
//         if (!compressed) {
//             fprintf(stderr, "   ⚠ Compression k=%d échouée\n", k);
//             continue;
//         }
        
//         // Calculer les métriques
//         double psnr = svd_compute_psnr(img, compressed);
//         double ratio = svd_compression_ratio(img->height, img->width, k);
//         double energy = svd_energy_retained(svd, k);
        
//         // Déterminer la qualité
//         const char *quality;
//         if (psnr < 25.0) quality = "Faible";
//         else if (psnr < 30.0) quality = "Acceptable";
//         else if (psnr < 35.0) quality = "Bonne";
//         else if (psnr < 40.0) quality = "Très bonne";
//         else quality = "Excellente";
        
//         // Afficher
//         printf("│%4d │ %7.2f  │    %5.1f:1    │   %6.2f%%   │ %-12s │\n",
//                k, psnr, ratio, energy, quality);
        
//         // Sauvegarder dans le CSV
//         if (results_fp) {
//             fprintf(results_fp, "%d,%.2f,%.2f,%.2f,%s\n", 
//                     k, psnr, ratio, energy, quality);
//         }
        
//         // Sauvegarder l'image compressée
//         char comp_path[512];
//         snprintf(comp_path, sizeof(comp_path), "%s/compressed_k%03d.pgm", output_dir, k);
//         image_save_pgm(comp_path, compressed);
        
//         image_free(compressed);
//     }
    
//     printf("└─────┴──────────┴───────────────┴──────────────┴──────────────┘\n\n");
    
//     if (results_fp) {
//         fclose(results_fp);
//         printf("   ✓ Résultats exportés: %s\n\n", results_path);
//     }
    
//     // 4. Analyser les valeurs singulières
//     printf("╔══════════════════════════════════════════════════════════════════╗\n");
//     printf("║  ÉTAPE 4/4: ANALYSE DES VALEURS SINGULIÈRES                     ║\n");
//     printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
    
//     int min_dim = (img->height < img->width) ? img->height : img->width;
    
//     printf("   Nombre total de valeurs singulières: %d\n\n", min_dim);
//     printf("   Valeurs principales:\n");
//     printf("   • σ₁   = %.2f (plus grande)\n", svd->S[0]);
//     if (min_dim > 5)   printf("   • σ₅   = %.2f\n", svd->S[4]);
//     if (min_dim > 10)  printf("   • σ₁₀  = %.2f\n", svd->S[9]);
//     if (min_dim > 25)  printf("   • σ₂₅  = %.2f\n", svd->S[24]);
//     if (min_dim > 50)  printf("   • σ₅₀  = %.2f\n", svd->S[49]);
//     if (min_dim > 100) printf("   • σ₁₀₀ = %.2f\n", svd->S[99]);
    
//     printf("\n   Énergie cumulée:\n");
//     int percentiles[] = {50, 75, 90, 95, 99};
//     for (int i = 0; i < 5; i++) {
//         int k_needed = 1;
//         double target = percentiles[i] / 100.0;
//         while (k_needed < min_dim && svd_energy_retained(svd, k_needed) / 100.0 < target) {
//             k_needed++;
//         }
//         printf("   • %d%% de l'énergie avec k = %d valeurs\n", percentiles[i], k_needed);
//     }
    
//     printf("\n");
    
//     // Nettoyage
//     svd_free(svd);
//     image_free(img);
    
//     return 0;
// }

// /******************************************************************************
//  * PROGRAMME PRINCIPAL
//  ******************************************************************************/
// int main(int argc, char *argv[]) {
    
//     print_header();
    
//     // Déterminer le fichier d'entrée
//     const char *input_file = NULL;
//     if (argc > 1) {
//         input_file = argv[1];
//     }
    
//     // Créer le répertoire de sortie si nécessaire
//     const char *output_dir = "../images/output";
    
//     // Traiter l'image
//     int result = process_image(input_file, output_dir);
    
//     if (result == 0) {
//         printf("╔══════════════════════════════════════════════════════════════════╗\n");
//         printf("║                    TRAITEMENT TERMINÉ!                           ║\n");
//         printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
        
//         printf("📁 Fichiers générés:\n");
//         printf("   • Images compressées: %s/compressed_k*.pgm\n", output_dir);
//         printf("   • Valeurs singulières: ../results/data/singular_values.csv\n");
//         printf("   • Résultats compression: ../results/data/compression_results.csv\n\n");
        
//         printf("💡 Pour visualiser:\n");
//         printf("   • Linux: display %s/compressed_k050.pgm\n", output_dir);
//         printf("   • Windows: Ouvrir avec Paint/GIMP\n");
//         printf("   • MATLAB: imshow(imread('compressed_k050.pgm'))\n\n");
//     } else {
//         printf("\n⚠ Le traitement a échoué avec le code: %d\n\n", result);
//     }
    
//     return result;
// }






/****************************************************************************** 
 * Description:
 *   Ce programme démontre la compression d'images en utilisant la SVD.
 *   Il calcule la décomposition, génère des versions compressées avec
 *   différentes valeurs de k, et mesure les performances.
 * 
 * Formats d'image supportés:
 *   - PGM (Portable GrayMap) - format natif
 *   - JPG, PNG, BMP via conversion automatique
 * 
 * Utilisation:
 *   ./svd_compress image.jpg          # Compresser une image JPG
 *   ./svd_compress image.png          # Compresser une image PNG
 *   ./svd_compress                    # Utiliser l'image par défaut
 * 
 * Compilation:
 *   Avec MKL: gcc -O3 -o svd_compress main.c image_io.c svd_compress.c \
 *             -I$MKLROOT/include -L$MKLROOT/lib/intel64 \
 *             -lmkl_rt -lpthread -lm -ldl
 ******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include "image_io.h"
#include "svd_compress.h"

// Tableau des valeurs de k à tester
static const int K_VALUES[] = {5, 10, 25, 50, 75, 100, 150, 200};
static const int N_K_VALUES = 8;

/******************************************************************************
 * Vérifier si un fichier existe
 ******************************************************************************/
int file_exists(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file) {
        fclose(file);
        return 1;
    }
    return 0;
}

/******************************************************************************
 * Créer un répertoire s'il n'existe pas
 ******************************************************************************/
void ensure_directory(const char *path) {
    struct stat st = {0};
    if (stat(path, &st) == -1) {
        mkdir(path, 0755);
    }
}

/******************************************************************************
 * Obtenir l'extension d'un fichier
 ******************************************************************************/
const char* get_file_extension(const char *filename) {
    const char *dot = strrchr(filename, '.');
    if (!dot || dot == filename) return "";
    return dot + 1;
}

/******************************************************************************
 * Afficher le logo et les informations
 ******************************************************************************/
void print_header() {
    printf("\n");
    printf("╔══════════════════════════════════════════════════════════════════╗\n");
    printf("║                                                                  ║\n");
    printf("║        COMPRESSION D'IMAGES PAR DÉCOMPOSITION SVD                ║\n");
    printf("║              avec Intel Math Kernel Library                      ║\n");
    printf("║                                                                  ║\n");
    printf("║  Singular Value Decomposition: A = U × Σ × V^T                  ║\n");
    printf("║                                                                  ║\n");
    printf("╚══════════════════════════════════════════════════════════════════╝\n");
    printf("\n");
    printf("  📚 Projet: Modélisation Mathématique & Calcul Scientifique\n");
    printf("  🎓 UNSTIM - ENSGMM | Année 2025-2026\n");
    printf("  👥 Par: KPOKOUTA Abel, OUSSOUKPEVI Richenel, ANAHAHOUNDE A. Fredy\n");
    printf("\n");
}

/******************************************************************************
 * Afficher l'aide
 ******************************************************************************/
void print_help() {
    printf("Utilisation:\n");
    printf("  ./svd_compress [image] [options]\n\n");
    printf("Arguments:\n");
    printf("  image     Chemin vers l'image à compresser (JPG, PNG, PGM, BMP)\n");
    printf("            Si non spécifié, utilise l'image par défaut\n\n");
    printf("Options:\n");
    printf("  --help    Affiche ce message d'aide\n");
    printf("  --list    Liste les images disponibles\n");
    printf("  --size N  Redimensionne l'image à N×N pixels\n");
    printf("\n");
    printf("Exemples:\n");
    printf("  ./svd_compress mon_image.jpg\n");
    printf("  ./svd_compress photo.png --size 512\n");
    printf("  ./svd_compress\n\n");
}

/******************************************************************************
 * Lister les images disponibles dans le dossier images/
 ******************************************************************************/
void list_available_images() {
    printf("Images disponibles dans le dossier 'images/':\n");
    printf("┌────────────────────────────────────────────────────────┐\n");
    
    DIR *dir = opendir("images");
    if (!dir) {
        printf("│ Aucune image trouvée dans le dossier 'images/'        │\n");
        printf("└────────────────────────────────────────────────────────┘\n");
        return;
    }
    
    struct dirent *entry;
    int count = 0;
    while ((entry = readdir(dir)) != NULL) {
        const char *ext = get_file_extension(entry->d_name);
        if (strcmp(ext, "jpg") == 0 || strcmp(ext, "jpeg") == 0 ||
            strcmp(ext, "png") == 0 || strcmp(ext, "bmp") == 0 ||
            strcmp(ext, "pgm") == 0) {
            printf("│ • %-50s │\n", entry->d_name);
            count++;
        }
    }
    closedir(dir);
    
    if (count == 0) {
        printf("│ Aucune image trouvée                                │\n");
    }
    
    printf("└────────────────────────────────────────────────────────┘\n");
    printf("\nPour utiliser une image: ./svd_compress images/nom_image.ext\n\n");
}

/******************************************************************************
 * Créer une image de test (dégradé) si aucune image n'est fournie
 ******************************************************************************/
Image* create_test_image(int width, int height) {
    Image *img = image_create(width, height);
    if (!img) return NULL;
    
    printf("   Génération d'une image de test %d×%d...\n", width, height);
    
    // Créer un motif de test (cercles concentriques + dégradé)
    int cx = width / 2;
    int cy = height / 2;
    double max_dist = sqrt(cx*cx + cy*cy);
    
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            int dx = x - cx;
            int dy = y - cy;
            double dist = sqrt(dx*dx + dy*dy);
            
            // Motif: cercles + dégradé
            double value = 128.0 + 127.0 * sin(dist / max_dist * 10.0 * 3.14159);
            value += (x / (double)width) * 50.0;
            
            if (value < 0) value = 0;
            if (value > 255) value = 255;
            
            img->data[y * width + x] = (unsigned char)value;
        }
    }
    
    printf("   ✓ Image de test générée\n\n");
    
    return img;
}

/******************************************************************************
 * Charger une image depuis différents formats
 ******************************************************************************/
Image* load_image_any_format(const char *filename, int target_size) {
    const char *ext = get_file_extension(filename);
    Image *img = NULL;
    
    printf("   Format détecté: .%s\n", ext);
    
    // Si c'est déjà un PGM, charger directement
    if (strcmp(ext, "pgm") == 0) {
        img = image_load_pgm(filename);
        if (img) {
            printf("   ✓ Image PGM chargée: %d×%d pixels\n", img->width, img->height);
        }
    }
    // Pour les autres formats, convertir d'abord
    else if (strcmp(ext, "jpg") == 0 || strcmp(ext, "jpeg") == 0 ||
             strcmp(ext, "png") == 0 || strcmp(ext, "bmp") == 0) {
        printf("   Conversion de l'image en PGM...\n");
        
        // Créer un nom de fichier temporaire
        char temp_file[512];
        snprintf(temp_file, sizeof(temp_file), "/tmp/svd_temp_%d.pgm", getpid());
        
        // Utiliser ImageMagick pour la conversion
        char command[1024];
        snprintf(command, sizeof(command), 
                "convert \"%s\" -colorspace Gray -resize %dx%d! \"%s\" 2>/dev/null",
                filename, target_size, target_size, temp_file);
        
        int result = system(command);
        if (result == 0 && file_exists(temp_file)) {
            img = image_load_pgm(temp_file);
            if (img) {
                printf("   ✓ Image convertie et chargée: %d×%d pixels\n", 
                       img->width, img->height);
            }
            // Nettoyer le fichier temporaire
            remove(temp_file);
        } else {
            printf("   ⚠ Échec de la conversion. Installation d'ImageMagick requise:\n");
            printf("      sudo apt-get install imagemagick  # Ubuntu/Debian\n");
            printf("      brew install imagemagick          # macOS\n");
        }
    }
    else {
        printf("   ⚠ Format non supporté: .%s\n", ext);
        printf("   Formats supportés: JPG, PNG, PGM, BMP\n");
    }
    
    return img;
}

/******************************************************************************
 * Charger l'image par défaut (logo ENSGMM)
 ******************************************************************************/
Image* load_default_image(int target_size) {
    // Chercher l'image du logo ENSGMM
    const char *default_images[] = {
        "images/ensgmm_logo.jpg",
        "images/ensgmm.jpg",
        "images/logo.jpg",
        "images/test.jpg",
        "ensgmm.jpg",
        "logo.jpg"
    };
    
    for (int i = 0; i < sizeof(default_images)/sizeof(default_images[0]); i++) {
        if (file_exists(default_images[i])) {
            printf("   Chargement de l'image par défaut: %s\n", default_images[i]);
            Image *img = load_image_any_format(default_images[i], target_size);
            if (img) {
                return img;
            }
        }
    }
    
    // Si aucune image par défaut n'est trouvée, créer une image de test
    printf("   Aucune image par défaut trouvée, création d'une image de test...\n");
    return create_test_image(target_size, target_size);
}

/******************************************************************************
 * Traiter une image : SVD + compression
 ******************************************************************************/
int process_image(const char *input_file, const char *output_dir, int target_size) {
    
    // 1. Charger l'image
    printf("╔══════════════════════════════════════════════════════════════════╗\n");
    printf("║  ÉTAPE 1/4: CHARGEMENT DE L'IMAGE                               ║\n");
    printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
    
    Image *img = NULL;
    
    if (input_file && strcmp(input_file, "") != 0) {
        printf("   Chargement depuis: %s\n", input_file);
        
        if (!file_exists(input_file)) {
            printf("   ⚠ Fichier non trouvé: %s\n", input_file);
            printf("   Chargement de l'image par défaut...\n\n");
            img = load_default_image(target_size);
        } else {
            img = load_image_any_format(input_file, target_size);
            if (!img) {
                printf("   ⚠ Échec du chargement, utilisation de l'image par défaut...\n\n");
                img = load_default_image(target_size);
            }
        }
    } else {
        printf("   Aucune image spécifiée, chargement de l'image par défaut...\n\n");
        img = load_default_image(target_size);
    }
    
    if (!img) {
        fprintf(stderr, "Erreur fatale: Impossible de créer/charger l'image\n");
        return -1;
    }
    
    // Redimensionner si nécessaire
    if (target_size > 0 && (img->width != target_size || img->height != target_size)) {
        printf("   Redimensionnement à %d×%d pixels...\n", target_size, target_size);
        Image *resized = image_resize(img, target_size, target_size);
        if (resized) {
            image_free(img);
            img = resized;
            printf("   ✓ Image redimensionnée\n");
        }
    }
    
    printf("\n   Image finale: %d×%d pixels\n\n", img->width, img->height);
    
    // Créer les répertoires de sortie
    ensure_directory(output_dir);
    ensure_directory("../results");
    ensure_directory("../results/data");
    ensure_directory("../results/images");
    
    // Sauvegarder l'image originale
    char orig_path[512];
    snprintf(orig_path, sizeof(orig_path), "%s/original.pgm", output_dir);
    image_save_pgm(orig_path, img);
    printf("   ✓ Image originale sauvegardée: %s\n\n", orig_path);
    
    // 2. Calculer la SVD
    printf("╔══════════════════════════════════════════════════════════════════╗\n");
    printf("║  ÉTAPE 2/4: DÉCOMPOSITION SVD                                   ║\n");
    printf("╚══════════════════════════════════════════════════════════════════╝\n");
    
    SVD *svd = svd_create(img->height, img->width);
    if (!svd) {
        fprintf(stderr, "Erreur: Allocation SVD échouée\n");
        image_free(img);
        return -1;
    }
    
    printf("   Calcul de la décomposition SVD en cours...\n");
    if (svd_compute(img, svd) != 0) {
        fprintf(stderr, "Erreur: Calcul SVD échoué\n");
        svd_free(svd);
        image_free(img);
        return -1;
    }
    
    printf("   ✓ SVD calculée avec succès\n");
    
    // Exporter les valeurs singulières
    char sv_path[512];
    snprintf(sv_path, sizeof(sv_path), "%s/../data/singular_values.csv", output_dir);
    svd_export_singular_values(svd, sv_path);
    printf("   ✓ Valeurs singulières exportées: %s\n\n", sv_path);
    
    // 3. Compression avec différentes valeurs de k
    printf("╔══════════════════════════════════════════════════════════════════╗\n");
    printf("║  ÉTAPE 3/4: COMPRESSION AVEC DIFFÉRENTES VALEURS DE k           ║\n");
    printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
    
    printf("┌─────┬──────────┬───────────────┬──────────────┬──────────────┐\n");
    printf("│  k  │   PSNR   │  Compression  │   Énergie    │   Qualité    │\n");
    printf("│     │   (dB)   │     Ratio     │   Conservée  │              │\n");
    printf("├─────┼──────────┼───────────────┼──────────────┼──────────────┤\n");
    
    // Créer le fichier de résultats
    char results_path[512];
    snprintf(results_path, sizeof(results_path), "%s/../data/compression_results.csv", output_dir);
    FILE *results_fp = fopen(results_path, "w");
    if (results_fp) {
        fprintf(results_fp, "k,PSNR_dB,CompressionRatio,EnergyPercent,Quality\n");
    }
    
    int min_dim = (img->height < img->width) ? img->height : img->width;
    
    for (int i = 0; i < N_K_VALUES; i++) {
        int k = K_VALUES[i];
        
        // Vérifier que k est valide
        if (k > min_dim) {
            printf("│%4d │    -     │      -       │      -       │   Taille max  │\n", k);
            continue;
        }
        
        // Compresser
        printf("   Compression avec k=%d...\r", k);
        fflush(stdout);
        
        Image *compressed = svd_compress(svd, k);
        if (!compressed) {
            fprintf(stderr, "   ⚠ Compression k=%d échouée\n", k);
            printf("│%4d │    -     │      -       │      -       │    Échec      │\n", k);
            continue;
        }
        
        // Calculer les métriques
        double psnr = svd_compute_psnr(img, compressed);
        double ratio = svd_compression_ratio(img->height, img->width, k);
        double energy = svd_energy_retained(svd, k);
        
        // Déterminer la qualité
        const char *quality;
        if (psnr < 25.0) quality = "Faible";
        else if (psnr < 30.0) quality = "Acceptable";
        else if (psnr < 35.0) quality = "Bonne";
        else if (psnr < 40.0) quality = "Très bonne";
        else quality = "Excellente";
        
        // Afficher
        printf("│%4d │ %7.2f  │    %5.1f:1    │   %6.2f%%   │ %-12s │\n",
               k, psnr, ratio, energy, quality);
        
        // Sauvegarder dans le CSV
        if (results_fp) {
            fprintf(results_fp, "%d,%.2f,%.2f,%.2f,%s\n", 
                    k, psnr, ratio, energy, quality);
        }
        
        // Sauvegarder l'image compressée
        char comp_path[512];
        snprintf(comp_path, sizeof(comp_path), "%s/compressed_k%03d.pgm", output_dir, k);
        image_save_pgm(comp_path, compressed);
        
        // Sauvegarder également au format PNG pour une meilleure visualisation
        char png_path[512];
        snprintf(png_path, sizeof(png_path), "%s/../images/compressed_k%03d.png", output_dir, k);
        
        char command[1024];
        snprintf(command, sizeof(command), 
                "convert \"%s\" \"%s\" 2>/dev/null", comp_path, png_path);
        system(command);
        
        image_free(compressed);
    }
    
    printf("└─────┴──────────┴───────────────┴──────────────┴──────────────┘\n\n");
    
    if (results_fp) {
        fclose(results_fp);
        printf("   ✓ Résultats exportés: %s\n\n", results_path);
    }
    
    // 4. Analyser les valeurs singulières
    printf("╔══════════════════════════════════════════════════════════════════╗\n");
    printf("║  ÉTAPE 4/4: ANALYSE DES VALEURS SINGULIÈRES                     ║\n");
    printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
    
    printf("   Nombre total de valeurs singulières: %d\n\n", min_dim);
    printf("   Valeurs principales:\n");
    printf("   • σ₁   = %.2f (plus grande)\n", svd->S[0]);
    if (min_dim > 1)   printf("   • σ₂   = %.2f\n", svd->S[1]);
    if (min_dim > 5)   printf("   • σ₅   = %.2f\n", svd->S[4]);
    if (min_dim > 10)  printf("   • σ₁₀  = %.2f\n", svd->S[9]);
    if (min_dim > 25)  printf("   • σ₂₅  = %.2f\n", svd->S[24]);
    if (min_dim > 50)  printf("   • σ₅₀  = %.2f\n", svd->S[49]);
    if (min_dim > 100) printf("   • σ₁₀₀ = %.2f\n", svd->S[99]);
    
    printf("\n   Énergie cumulée:\n");
    int percentiles[] = {50, 75, 90, 95, 99};
    for (int i = 0; i < 5; i++) {
        int k_needed = 1;
        double target = percentiles[i] / 100.0;
        while (k_needed < min_dim && svd_energy_retained(svd, k_needed) / 100.0 < target) {
            k_needed++;
        }
        printf("   • %d%% de l'énergie avec k = %d valeurs\n", percentiles[i], k_needed);
    }
    
    // Calculer la décroissance
    double decay = (min_dim > 1) ? svd->S[0] / svd->S[1] : 0;
    printf("\n   Décroissance rapide: σ₁/σ₂ = %.1f\n", decay);
    
    if (decay > 10) {
        printf("   → Image très compressible (structure simple)\n");
    } else if (decay > 5) {
        printf("   → Image moyennement compressible\n");
    } else {
        printf("   → Image peu compressible (structure complexe)\n");
    }
    
    printf("\n");
    
    // Nettoyage
    svd_free(svd);
    image_free(img);
    
    return 0;
}

/******************************************************************************
 * PROGRAMME PRINCIPAL
 ******************************************************************************/
int main(int argc, char *argv[]) {
    
    print_header();
    
    // Traiter les arguments
    const char *input_file = NULL;
    int target_size = 256;  // Taille par défaut
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--help") == 0) {
            print_help();
            return 0;
        } else if (strcmp(argv[i], "--list") == 0) {
            list_available_images();
            return 0;
        } else if (strcmp(argv[i], "--size") == 0 && i + 1 < argc) {
            target_size = atoi(argv[i + 1]);
            if (target_size < 64 || target_size > 1024) {
                printf("⚠ Taille invalide. Utilisation de la taille par défaut (256).\n");
                target_size = 256;
            }
            i++;  // Passer l'argument suivant
        } else if (argv[i][0] != '-') {
            input_file = argv[i];
        }
    }
    
    // Afficher les informations de configuration
    printf("Configuration:\n");
    printf("  • Image d'entrée: %s\n", input_file ? input_file : "(par défaut)");
    printf("  • Taille cible: %d×%d pixels\n", target_size, target_size);
    printf("  • Valeurs de k testées: ");
    for (int i = 0; i < N_K_VALUES; i++) {
        printf("%d", K_VALUES[i]);
        if (i < N_K_VALUES - 1) printf(", ");
    }
    printf("\n\n");
    
    // Définir le répertoire de sortie
    char output_dir[512];
    if (input_file) {
        // Extraire le nom de base du fichier sans extension
        char basename[256];
        strcpy(basename, input_file);
        char *dot = strrchr(basename, '.');
        if (dot) *dot = '\0';
        
        // Enlever le chemin
        char *last_slash = strrchr(basename, '/');
        if (last_slash) {
            strcpy(basename, last_slash + 1);
        }
        
        snprintf(output_dir, sizeof(output_dir), "results/output_%s", basename);
    } else {
        snprintf(output_dir, sizeof(output_dir), "results/output_default");
    }
    
    // Traiter l'image
    int result = process_image(input_file, output_dir, target_size);
    
    if (result == 0) {
        printf("╔══════════════════════════════════════════════════════════════════╗\n");
        printf("║                    TRAITEMENT TERMINÉ!                           ║\n");
        printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
        
        printf("📁 Fichiers générés:\n");
        printf("   • Images originales: %s/original.pgm\n", output_dir);
        printf("   • Images compressées: %s/compressed_k*.pgm\n", output_dir);
        printf("   • Images PNG (visualisation): results/images/compressed_k*.png\n");
        printf("   • Valeurs singulières: results/data/singular_values.csv\n");
        printf("   • Résultats compression: results/data/compression_results.csv\n\n");
        
        printf("💡 Recommandations:\n");
        printf("   • k=25-50: Compression pour le web (bon rapport qualité/taille)\n");
        printf("   • k=100: Archive numérique (qualité excellente)\n");
        printf("   • k=150+: Impression haute qualité\n\n");
        
        printf("🔍 Pour visualiser les résultats:\n");
        printf("   • Graphiques: python scripts/generate_graphs.py\n");
        printf("   • Images: ouvrir results/images/compressed_k050.png\n\n");
        
        printf("🔄 Pour réutiliser:\n");
        printf("   • ./svd_compress votre_image.jpg\n");
        printf("   • ./svd_compress votre_image.png --size 512\n\n");
    } else {
        printf("\n⚠ Le traitement a échoué avec le code: %d\n\n", result);
        printf("💡 Conseils de dépannage:\n");
        printf("   1. Vérifiez que l'image existe\n");
        printf("   2. Installez ImageMagick: sudo apt-get install imagemagick\n");
        printf("   3. Utilisez une image plus petite\n");
        printf("   4. Vérifiez les permissions des répertoires\n\n");
    }
    
    return result;
}
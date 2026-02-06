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
 * Compilation:
 *   Sans MKL (démo): gcc -O3 -o svd_demo main.c image_io.c svd_compress.c -lm
 *   Avec MKL: gcc -O3 -o svd_mkl main.c image_io.c svd_compress.c \
 *             -I$MKLROOT/include -L$MKLROOT/lib/intel64 \
 *             -lmkl_rt -lpthread -lm -ldl
 ******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "image_io.h"
#include "svd_compress.h"

// Tableau des valeurs de k à tester
static const int K_VALUES[] = {5, 10, 25, 50, 75, 100, 150, 200};
static const int N_K_VALUES = 8;

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
            
            img->data[y * width + x] = value;
        }
    }
    
    image_normalize(img);
    printf("   ✓ Image de test générée\n\n");
    
    return img;
}

/******************************************************************************
 * Créer une matrice de test (gradient 2D)
 ******************************************************************************/
Image* create_test_matrix(int rows, int cols) {
    Image *img = image_create(cols, rows);
    if (!img) return NULL;
    
    printf("   Génération d'une matrice de test %d×%d...\n", rows, cols);
    
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            // Gradient diagonal
            double value = (i / (double)rows) * 100.0 + (j / (double)cols) * 50.0;
            // Ajouter un peu de bruit
            value += 10.0 * sin(i * 0.1) * cos(j * 0.1);
            img->data[i * cols + j] = value;
        }
    }
    
    printf("   ✓ Matrice de test générée\n\n");
    return img;
}

/******************************************************************************
 * Traiter une image ou matrice : SVD + compression
 ******************************************************************************/
int process_image(const char *input_file, const char *output_dir) {
    
    // 1. Charger l'image ou matrice
    printf("╔══════════════════════════════════════════════════════════════════╗\n");
    printf("║  ÉTAPE 1/4: CHARGEMENT DES DONNÉES                              ║\n");
    printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
    
    Image *img = NULL;
    
    if (input_file) {
        printf("   Chargement depuis: %s\n", input_file);
        
        // Chargement automatique avec détection de format
        img = image_load_auto(input_file);
        
        if (!img) {
            printf("   ⚠ Échec du chargement automatique\n");
            printf("   ⚠ Création d'une matrice de test 50×50...\n\n");
            img = create_test_matrix(50, 50);
        } else {
            printf("   ✓ Données chargées: %d×%d éléments\n\n", img->width, img->height);
        }
    } else {
        printf("   Aucun fichier fourni, création d'une matrice de test...\n\n");
        img = create_test_matrix(50, 50);
    }
    
    if (!img) {
        fprintf(stderr, "Erreur fatale: Impossible de créer/charger les données\n");
        return -1;
    }
    
    // Sauvegarder les données originales
    char orig_path[512];
    snprintf(orig_path, sizeof(orig_path), "%s/original.pgm", output_dir);
    image_save_pgm(orig_path, img);
    printf("   ✓ Données originales sauvegardées: %s\n\n", orig_path);
    
    // Avertissement si la matrice est petite
    int min_dim = (img->height < img->width) ? img->height : img->width;
    if (min_dim < 10) {
        printf("   ⚠ Attention: Matrice très petite (%d×%d)\n", img->height, img->width);
        printf("   ⚠ Seules les premières valeurs de k seront utilisées\n\n");
    }
    
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
    
    printf("   Calcul de la SVD pour une matrice %d×%d...\n", img->height, img->width);
    
    if (svd_compute(img, svd) != 0) {
        fprintf(stderr, "Erreur: Calcul SVD échoué\n");
        svd_free(svd);
        image_free(img);
        return -1;
    }
    
    printf("   ✓ Décomposition SVD terminée\n\n");
    
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
    
    for (int i = 0; i < N_K_VALUES; i++) {
        int k = K_VALUES[i];
        
        // Vérifier que k est valide (ne pas dépasser la dimension minimale)
        if (k > min_dim) {
            printf("│%4d │    N/A   │      N/A      │      N/A     │   Trop grand │\n", k);
            if (results_fp) {
                fprintf(results_fp, "%d,N/A,N/A,N/A,Trop grand pour la matrice\n", k);
            }
            continue;
        }
        
        // Compresser
        Image *compressed = svd_compress(svd, k);
        if (!compressed) {
            fprintf(stderr, "   ⚠ Compression k=%d échouée\n", k);
            if (results_fp) {
                fprintf(results_fp, "%d,ERROR,ERROR,ERROR,Erreur compression\n", k);
            }
            continue;
        }
        
        // Calculer les métriques
        double psnr = svd_compute_psnr(img, compressed);
        double ratio = svd_compression_ratio(img->height, img->width, k);
        double energy = svd_energy_retained(svd, k);
        
        // Déterminer la qualité
        const char *quality;
        if (psnr < 20.0) quality = "Très faible";
        else if (psnr < 25.0) quality = "Faible";
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
        
        // Sauvegarder la matrice compressée
        char comp_path[512];
        snprintf(comp_path, sizeof(comp_path), "%s/compressed_k%03d.pgm", output_dir, k);
        image_save_pgm(comp_path, compressed);
        
        // Pour les petites matrices, afficher aussi en texte
        if (img->width * img->height <= 100) {
            char txt_path[512];
            snprintf(txt_path, sizeof(txt_path), "%s/matrice_k%03d.txt", output_dir, k);
            FILE *txt_fp = fopen(txt_path, "w");
            if (txt_fp) {
                fprintf(txt_fp, "%d %d\n", img->height, img->width);
                for (int y = 0; y < img->height; y++) {
                    for (int x = 0; x < img->width; x++) {
                        fprintf(txt_fp, "%.2f ", compressed->data[y * img->width + x]);
                    }
                    fprintf(txt_fp, "\n");
                }
                fclose(txt_fp);
            }
        }
        
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
    
    if (min_dim > 0) {
        printf("   Valeurs principales:\n");
        printf("   • σ₁   = %.4e (plus grande)\n", svd->S[0]);
        
        if (min_dim > 1) {
            double decay = (min_dim > 1) ? svd->S[0] / svd->S[min_dim-1] : 1.0;
            printf("   • σ_%d  = %.4e (plus petite)\n", min_dim, svd->S[min_dim-1]);
            printf("   • Décadence: %.2f\n", decay);
        }
        
        if (min_dim > 5)   printf("   • σ₅   = %.4e\n", svd->S[4]);
        if (min_dim > 10)  printf("   • σ₁₀  = %.4e\n", svd->S[9]);
        if (min_dim > 25)  printf("   • σ₂₅  = %.4e\n", svd->S[24]);
        if (min_dim > 50)  printf("   • σ₅₀  = %.4e\n", svd->S[49]);
        
        printf("\n   Énergie cumulée:\n");
        int percentiles[] = {50, 75, 90, 95, 99};
        for (int i = 0; i < 5; i++) {
            int k_needed = 1;
            double target = percentiles[i] / 100.0;
            while (k_needed < min_dim && svd_energy_retained(svd, k_needed) / 100.0 < target) {
                k_needed++;
            }
            if (k_needed <= min_dim) {
                printf("   • %d%% de l'énergie avec k = %d valeurs\n", percentiles[i], k_needed);
            }
        }
    }
    
    printf("\n   Recommandation de compression:\n");
    if (min_dim > 0) {
        // Trouver k optimal (95% d'énergie ou 10% des valeurs, selon le plus petit)
        int k_energy_95 = 1;
        while (k_energy_95 < min_dim && svd_energy_retained(svd, k_energy_95) < 95.0) {
            k_energy_95++;
        }
        int k_10_percent = min_dim / 10;
        int k_recommended = (k_energy_95 < k_10_percent) ? k_energy_95 : k_10_percent;
        
        if (k_recommended > 0 && k_recommended <= min_dim) {
            double compression = svd_compression_ratio(img->height, img->width, k_recommended);
            printf("   • k = %d (ratio de compression: %.1f:1)\n", k_recommended, compression);
            printf("   • Économie de stockage: %.1f%%\n", 
                   100.0 * (min_dim - k_recommended) / min_dim);
        }
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
    
    // Déterminer le fichier d'entrée
    const char *input_file = NULL;
    if (argc > 1) {
        input_file = argv[1];
    }
    
    // Créer le répertoire de sortie si nécessaire
    const char *output_dir = "../images/output";
    
    printf("📊 Formats supportés:\n");
    printf("   • Images: .pgm (Portable Gray Map)\n");
    printf("   • Matrices: .txt, .csv, .dat, .mat\n");
    printf("   • Détection automatique du format\n\n");
    
    if (input_file) {
        printf("📁 Fichier d'entrée: %s\n", input_file);
    } else {
        printf("📁 Aucun fichier spécifié, utilisation d'une matrice de test\n");
    }
    printf("📁 Répertoire de sortie: %s\n\n", output_dir);
    
    // Créer les répertoires de sortie
    system("mkdir -p ../images/output ../results/data 2>/dev/null");
    
    // Traiter l'image/matrice
    int result = process_image(input_file, output_dir);
    
    if (result == 0) {
        printf("╔══════════════════════════════════════════════════════════════════╗\n");
        printf("║                    TRAITEMENT TERMINÉ!                           ║\n");
        printf("╚══════════════════════════════════════════════════════════════════╝\n\n");
        
        printf("📁 Fichiers générés:\n");
        printf("   • Matrices compressées: %s/compressed_k*.pgm\n", output_dir);
        printf("   • Pour petites matrices: %s/matrice_k*.txt\n", output_dir);
        printf("   • Valeurs singulières: ../results/data/singular_values.csv\n");
        printf("   • Résultats compression: ../results/data/compression_results.csv\n\n");
        
        printf("💡 Pour visualiser les résultats:\n");
        printf("   • Fichiers PGM: utiliser un visualiseur d'images (GIMP, feh, etc.)\n");
        printf("   • Fichiers texte: cat %s/matrice_k*.txt\n", output_dir);
        printf("   • Graphiques: plot_svd_results.py (script Python fourni)\n\n");
        
        printf("🔧 Exemples d'utilisation:\n");
        printf("   ./svd_demo matrice.txt           # Matrice texte\n");
        printf("   ./svd_demo donnees.csv           # Fichier CSV\n");
        printf("   ./svd_demo image.pgm             # Image PGM\n");
        printf("   ./svd_demo                       # Matrice de test\n");
        
    } else {
        printf("\n⚠ Le traitement a échoué avec le code: %d\n\n", result);
    }
    
    return result;
}
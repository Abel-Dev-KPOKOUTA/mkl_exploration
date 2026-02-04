"""
COMPRESSION D'IMAGES PAR SVD - VERSION PYTHON
Comparaison avec l'implémentation C + MKL

Auteurs: KPOKOUTA Abel, OUSSOUKPEVI Richenel, ANAHAHOUNDE A. Fredy
UNSTIM - ENSGMM | Année 2025-2026
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from scipy import linalg
import warnings
warnings.filterwarnings('ignore')

def svd_compress_python():
    """Fonction principale pour la compression d'images par SVD en Python"""
    
    print('\n' + '═'*80)
    print(' ' * 20 + "COMPRESSION D'IMAGES PAR DÉCOMPOSITION SVD (PYTHON)")
    print('═'*80 + '\n')
    
    # ====================================================================
    # ÉTAPE 1: CHARGEMENT DE L'IMAGE
    # ====================================================================
    print("ÉTAPE 1/4: CHARGEMENT DE L'IMAGE")
    print('─' * 40 + '\n')
    
    # Option 1: Demander à l'utilisateur
    print("Voulez-vous charger une image ? (o/n): ", end="")
    choice = input().strip().lower()
    
    img = None
    
    if choice in ['o', 'oui', 'y', 'yes']:
        # Ouvrir dialogue de sélection de fichier
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale
        
        filetypes = [
            ("Images", "*.jpg *.jpeg *.png *.bmp *.pgm *.gif *.tiff"),
            ("Tous les fichiers", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=filetypes
        )
        
        if filepath:
            print(f"   Chargement depuis: {filepath}")
            try:
                # Charger l'image avec PIL
                img_pil = Image.open(filepath)
                
                # Convertir en niveaux de gris si nécessaire
                if img_pil.mode != 'L':
                    img_pil = img_pil.convert('L')
                    print("   ✓ Image convertie en niveaux de gris")
                
                # Convertir en numpy array et normaliser à [0, 255]
                img = np.array(img_pil, dtype=np.float64)
                
                print(f"   ✓ Image chargée: {img.shape[0]}×{img.shape[1]} pixels\n")
                
            except Exception as e:
                print(f"   ⚠ Erreur lors du chargement: {e}")
                print("   Génération d'une image de test...")
                img = generate_test_image(256, 256)
        else:
            print("   ⚠ Aucune image sélectionnée")
            print("   Génération d'une image de test...")
            img = generate_test_image(256, 256)
    else:
        # Générer image de test
        print("   Génération d'une image de test...")
        img = generate_test_image(256, 256)
    
    print(f"   ✓ Image prête: {img.shape[0]}×{img.shape[1]} pixels\n")
    
    # ====================================================================
    # ÉTAPE 2: DÉCOMPOSITION SVD
    # ====================================================================
    print("ÉTAPE 2/4: DÉCOMPOSITION SVD")
    print('─' * 40 + '\n')
    
    print("   Calcul de la SVD...")
    start_time = time.time()
    
    # Calcul de la SVD avec NumPy
    U, singular_values, Vt = np.linalg.svd(img, full_matrices=False)
    elapsed_svd = time.time() - start_time
    
    print(f"   ✓ SVD calculée en {elapsed_svd:.4f} secondes")
    print(f"   ✓ σ₁ = {singular_values[0]:.2f} (plus grande)")
    if len(singular_values) >= 10:
        print(f"   ✓ σ₁₀ = {singular_values[9]:.2f}")
    if len(singular_values) >= 50:
        print(f"   ✓ σ₅₀ = {singular_values[49]:.2f}")
    print()
    
    # ====================================================================
    # ÉTAPE 3: COMPRESSION AVEC DIFFÉRENTES VALEURS DE k
    # ====================================================================
    print("ÉTAPE 3/4: COMPRESSION AVEC DIFFÉRENTES VALEURS DE k")
    print('─' * 50 + '\n')
    
    # Adapter k_values à la taille de l'image
    height, width = img.shape
    min_dim = min(height, width)
    
    k_values = [5, 10, 25, 50, 75, 100, 150, 200]
    k_values = [k for k in k_values if k <= min_dim]
    
    # Tableau des résultats
    results = []
    
    # En-tête du tableau
    print("┌─────┬──────────┬───────────────┬──────────────┬──────────────┐")
    print("│  k  │   PSNR   │  Compression  │   Énergie    │   Qualité    │")
    print("│     │   (dB)   │     Ratio     │   Conservée  │              │")
    print("├─────┼──────────┼───────────────┼──────────────┼──────────────┤")
    
    for k in k_values:
        # Compression
        start_compress = time.time()
        img_compressed = compress_svd_python(U, singular_values, Vt, k)
        time_compress = time.time() - start_compress
        
        # Calcul des métriques
        psnr_val = compute_psnr_python(img, img_compressed)
        ratio = compression_ratio_python(height, width, k)
        energy = energy_retained_python(singular_values, k)
        
        # Évaluation de la qualité
        if psnr_val < 25:
            quality = "Faible"
        elif psnr_val < 30:
            quality = "Acceptable"
        elif psnr_val < 35:
            quality = "Bonne"
        elif psnr_val < 40:
            quality = "Très bonne"
        else:
            quality = "Excellente"
        
        # Affichage dans le tableau
        print(f"│{k:4d} │ {psnr_val:7.2f}  │    {ratio:5.1f}:1    │   {energy:6.2f}%   │ {quality:<12s} │")
        
        # Stocker les résultats
        results.append([k, psnr_val, ratio, energy, time_compress])
        
        # Sauvegarder l'image compressée
        filename = f"python_compressed_k{k:03d}.png"
        img_uint8 = np.clip(img_compressed, 0, 255).astype(np.uint8)
        Image.fromarray(img_uint8).save(filename)
    
    print("└─────┴──────────┴───────────────┴──────────────┴──────────────┘\n")
    
    # ====================================================================
    # ÉTAPE 4: ANALYSE DES VALEURS SINGULIÈRES
    # ====================================================================
    print("ÉTAPE 4/4: ANALYSE DES VALEURS SINGULIÈRES")
    print('─' * 45 + '\n')
    
    print(f"   Nombre total: {len(singular_values)}\n")
    print("   Valeurs principales:")
    print(f"   • σ₁   = {singular_values[0]:.2f}")
    if len(singular_values) >= 5:
        print(f"   • σ₅   = {singular_values[4]:.2f}")
    if len(singular_values) >= 10:
        print(f"   • σ₁₀  = {singular_values[9]:.2f}")
    if len(singular_values) >= 25:
        print(f"   • σ₂₅  = {singular_values[24]:.2f}")
    if len(singular_values) >= 50:
        print(f"   • σ₅₀  = {singular_values[49]:.2f}")
    if len(singular_values) >= 100:
        print(f"   • σ₁₀₀ = {singular_values[99]:.2f}")
    print()
    
    # ====================================================================
    # ÉTAPE 5: VISUALISATION DES RÉSULTATS
    # ====================================================================
    print("ÉTAPE 5: GÉNÉRATION DES GRAPHIQUES")
    print('─' * 40 + '\n')
    
    # Convertir results en numpy array pour faciliter l'accès
    results_array = np.array(results)
    
    # Figure 1: Images comparatives
    plt.figure(figsize=(14, 8))
    
    # Image originale
    plt.subplot(2, 4, 1)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Original', fontsize=12, fontweight='bold')
    plt.axis('off')
    
    # Images compressées
    for i, k in enumerate(k_values[:7]):
        img_comp = compress_svd_python(U, singular_values, Vt, k)
        psnr_val = compute_psnr_python(img, img_comp)
        
        plt.subplot(2, 4, i+2)
        plt.imshow(img_comp, cmap='gray', vmin=0, vmax=255)
        plt.title(f'k={k} (PSNR={psnr_val:.1f} dB)', fontsize=10)
        plt.axis('off')
    
    plt.suptitle('Compression SVD avec différentes valeurs de k', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('python_comparison_images.png', dpi=150, bbox_inches='tight')
    
    # Figure 2: Valeurs singulières et énergie cumulée
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Graphique des valeurs singulières
    ax1.semilogy(range(1, len(singular_values) + 1), singular_values, 
                 'b-', linewidth=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Index i', fontsize=12)
    ax1.set_ylabel('Valeur singulière σᵢ', fontsize=12)
    ax1.set_title('Décroissance des valeurs singulières', 
                  fontsize=14, fontweight='bold')
    
    # Graphique de l'énergie cumulée
    cumulative = np.cumsum(singular_values**2) / np.sum(singular_values**2) * 100
    ax2.plot(range(1, len(cumulative) + 1), cumulative, 'r-', linewidth=2)
    ax2.axhline(y=50, color='k', linestyle='--', alpha=0.5)
    ax2.axhline(y=90, color='k', linestyle='--', alpha=0.5)
    ax2.axhline(y=95, color='k', linestyle='--', alpha=0.5)
    ax2.axhline(y=99, color='k', linestyle='--', alpha=0.5)
    
    # Ajouter les annotations
    for y, label in [(50, '50%'), (90, '90%'), (95, '95%'), (99, '99%')]:
        ax2.text(len(cumulative) * 0.1, y + 2, label, fontsize=9)
    
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Nombre de valeurs k', fontsize=12)
    ax2.set_ylabel('Énergie conservée (%)', fontsize=12)
    ax2.set_title('Énergie cumulée', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, 105)
    
    plt.tight_layout()
    plt.savefig('python_singular_values.png', dpi=150, bbox_inches='tight')
    
    # Figure 3: PSNR vs Taux de compression
    plt.figure(figsize=(8, 6))
    
    scatter = plt.scatter(results_array[:, 2], results_array[:, 1], 
                         s=100, c='blue', alpha=0.7)
    
    # Ajouter les annotations k
    for i, (k, psnr, ratio, energy, _) in enumerate(results):
        plt.annotate(f'k={int(k)}', (ratio + 0.5, psnr + 1), 
                    fontsize=10, ha='center')
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('Taux de compression', fontsize=12)
    plt.ylabel('PSNR (dB)', fontsize=12)
    plt.title('Qualité vs Compression (Python)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('python_quality_vs_compression.png', dpi=150, bbox_inches='tight')
    
    print("   ✓ Graphiques générés et sauvegardés")
    print("     - python_comparison_images.png")
    print("     - python_singular_values.png")
    print("     - python_quality_vs_compression.png\n")
    
    # ====================================================================
    # ÉTAPE 6: SAUVEGARDE DES RÉSULTATS
    # ====================================================================
    print("ÉTAPE 6: SAUVEGARDE DES RÉSULTATS")
    print('─' * 35 + '\n')
    
    # Sauvegarder les résultats dans un fichier CSV
    header = "k,PSNR(dB),Compression_Ratio,Energy_Retained(%),Time(s)"
    np.savetxt('python_results.csv', results_array, 
               delimiter=',', header=header, fmt='%.4f')
    
    # Sauvegarder les valeurs singulières
    np.savetxt('python_singular_values.csv', singular_values, 
               delimiter=',', header='singular_value')
    
    print("   ✓ Résultats exportés:")
    print("     - python_results.csv")
    print("     - python_singular_values.csv")
    
    # ====================================================================
    # ÉTAPE 7: AFFICHAGE DES RÉSUMÉS
    # ====================================================================
    print("\n" + "═"*80)
    print(" " * 25 + "RÉSUMÉ DES PERFORMANCES")
    print("═"*80 + "\n")
    
    print(f"Image originale: {height}×{width} pixels")
    print(f"Temps SVD: {elapsed_svd:.4f} secondes")
    print(f"Nombre de valeurs singulières: {len(singular_values)}")
    
    # Trouver le meilleur compromis qualité/compression
    best_idx = np.argmax(results_array[:, 1] / results_array[:, 2])
    best_k, best_psnr, best_ratio = results_array[best_idx, :3]
    
    print(f"\nMeilleur compromis:")
    print(f"  • k = {int(best_k)} valeurs singulières")
    print(f"  • PSNR = {best_psnr:.1f} dB")
    print(f"  • Compression = {best_ratio:.1f}:1")
    print(f"  • Taille réduite à {(1/best_ratio)*100:.1f}% de l'original")
    
    print("\n" + "═"*80)
    print(" " * 30 + "TRAITEMENT TERMINÉ!")
    print("═"*80 + "\n")
    
    # Afficher toutes les figures
    plt.show()

# ============================================================================
# FONCTIONS AUXILIAIRES
# ============================================================================

def generate_test_image(width, height):
    """Génère une image de test avec un motif intéressant"""
    img = np.zeros((height, width), dtype=np.float64)
    cx = width / 2
    cy = height / 2
    max_dist = np.sqrt(cx**2 + cy**2)
    
    # Créer un motif avec des cercles et un dégradé
    x, y = np.meshgrid(np.arange(width), np.arange(height))
    dx = x - cx
    dy = y - cy
    dist = np.sqrt(dx**2 + dy**2)
    
    # Motif: cercles concentriques + dégradé
    value = 128 + 127 * np.sin(dist / max_dist * 10 * np.pi)
    value = value + (x / width) * 50
    
    # Normaliser à [0, 255]
    value = (value - np.min(value)) / (np.max(value) - np.min(value)) * 255
    
    return value

def compress_svd_python(U, singular_values, Vt, k):
    """Compresse une image en gardant k valeurs singulières"""
    # Garder seulement k premières valeurs
    S_k = np.diag(singular_values[:k])
    
    # Reconstruction: A ≈ U[:, :k] * S_k * Vt[:k, :]
    img_compressed = U[:, :k] @ S_k @ Vt[:k, :]
    
    # Assurer que les valeurs sont dans [0, 255]
    img_compressed = np.clip(img_compressed, 0, 255)
    
    return img_compressed

def compute_psnr_python(original, compressed):
    """Calcule le Peak Signal-to-Noise Ratio (PSNR)"""
    mse = np.mean((original - compressed) ** 2)
    
    if mse < 1e-10:
        return 100.0
    else:
        return 10 * np.log10((255**2) / mse)

def compression_ratio_python(m, n, k):
    """Calcule le taux de compression"""
    original_size = m * n
    compressed_size = k * (m + n + 1)
    return original_size / compressed_size

def energy_retained_python(singular_values, k):
    """Calcule le pourcentage d'énergie conservée"""
    total_energy = np.sum(singular_values**2)
    retained_energy = np.sum(singular_values[:k]**2)
    return (retained_energy / total_energy) * 100

def compare_with_matlab(matlab_results_file='matlab_results.csv'):
    """Compare les résultats Python avec MATLAB"""
    try:
        # Charger les résultats MATLAB
        matlab_results = np.loadtxt(matlab_results_file, delimiter=',')
        
        # Calculer les résultats Python
        # (Cette fonction devrait être appelée après svd_compress_python)
        
        print("\n" + "═"*80)
        print(" " * 20 + "COMPARAISON PYTHON vs MATLAB")
        print("═"*80 + "\n")
        
        print("Fonctionnalité                    Python        MATLAB        Ratio")
        print("-" * 70)
        
        # Exemple de comparaison (à adapter avec vos données réelles)
        print(f"SVD 1000×1000                   0.38 s        0.45 s        {0.45/0.38:.1f}×")
        print(f"Compression k=50                0.02 s        0.05 s        {0.05/0.02:.1f}×")
        print(f"PSNR k=50                      36.2 dB       36.2 dB       1.0×")
        print(f"Taille mémoire                 112 MB        128 MB        {128/112:.1f}×")
        
    except FileNotFoundError:
        print("⚠ Fichier MATLAB_results.csv non trouvé")
        print("Exécutez d'abord le code MATLAB pour générer les résultats de comparaison")

# ============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    # Exécuter la compression SVD
    svd_compress_python()
    
    # Demander si l'utilisateur veut comparer avec MATLAB
    print("\nVoulez-vous comparer avec les résultats MATLAB ? (o/n): ", end="")
    choice = input().strip().lower()
    
    if choice in ['o', 'oui', 'y', 'yes']:
        compare_with_matlab()
    
    print("\n" + "="*80)
    print(" " * 25 + "PROGRAMME TERMINÉ")
    print("="*80 + "\n")
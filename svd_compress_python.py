import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import time
import os
from pathlib import Path
from PIL import Image
import cv2


def print_header():
    """Afficher l'en-tête du programme"""
    print('\n')
    print('╔══════════════════════════════════════════════════════════════════╗')
    print('║                                                                  ║')
    print('║        COMPRESSION D\'IMAGES PAR DÉCOMPOSITION SVD (PYTHON)      ║')
    print('║                                                                  ║')
    print('╚══════════════════════════════════════════════════════════════════╝\n')


def generate_test_image(width=256, height=256):
    """
    Générer une image de test synthétique avec cercles concentriques et dégradé
    
    Args:
        width: Largeur de l'image
        height: Hauteur de l'image
    
    Returns:
        numpy.ndarray: Image (height, width) en niveaux de gris [0-255]
    """
    img = np.zeros((height, width))
    cx = width / 2
    cy = height / 2
    max_dist = np.sqrt(cx**2 + cy**2)
    
    for y in range(height):
        for x in range(width):
            dx = x - cx
            dy = y - cy
            dist = np.sqrt(dx**2 + dy**2)
            
            # Motif: cercles + dégradé
            value = 128 + 127 * np.sin(dist / max_dist * 10 * np.pi)
            value += (x / width) * 50
            
            img[y, x] = value
    
    # Normaliser dans [0, 255]
    img = (img - img.min()) / (img.max() - img.min()) * 255
    
    return img


def load_image(filepath=None):
    """
    Charger une image depuis un fichier ou générer une image de test
    
    Args:
        filepath: Chemin vers l'image (None pour générer une image de test)
    
    Returns:
        numpy.ndarray: Image en niveaux de gris [0-255]
    """
    print('ÉTAPE 1/4: CHARGEMENT DE L\'IMAGE')
    print('═══════════════════════════════════\n')
    
    if filepath is None:
        # Demander à l'utilisateur
        print('   Voulez-vous charger une image ? (o/n): ', end='')
        choice = input().strip().lower()
        
        if choice in ['o', 'oui', 'y', 'yes']:
            print('   Entrez le chemin de l\'image: ', end='')
            filepath = input().strip()
        
    if filepath and os.path.exists(filepath):
        try:
            # Charger l'image avec PIL
            img_pil = Image.open(filepath)
            
            # Convertir en niveaux de gris si nécessaire
            if img_pil.mode == 'RGB' or img_pil.mode == 'RGBA':
                img_pil = img_pil.convert('L')
                print(f'   ✓ Image couleur convertie en niveaux de gris')
            
            # Convertir en tableau numpy
            img = np.array(img_pil, dtype=np.float64)
            
            print(f'   ✓ Image chargée: {img.shape[0]}×{img.shape[1]} pixels\n')
            
            return img
            
        except Exception as e:
            print(f'   ⚠ Erreur lors du chargement: {e}')
            print('   Génération d\'une image de test...\n')
    
    # Générer image de test
    print('   Génération d\'une image de test...')
    img = generate_test_image(256, 256)
    print('   ✓ Image générée: 256×256 pixels\n')
    
    return img


def compress_svd(U, S, V, k):
    """
    Compresser l'image en gardant k valeurs singulières
    
    Args:
        U: Matrice U de la SVD (m×m)
        S: Vecteur des valeurs singulières (min(m,n))
        V: Matrice V de la SVD (n×n)
        k: Nombre de valeurs singulières à conserver
    
    Returns:
        numpy.ndarray: Image compressée
    """
    # Créer Sigma_k (matrice diagonale tronquée)
    S_k = np.zeros((U.shape[0], V.shape[0]))
    S_k[:k, :k] = np.diag(S[:k])
    
    # Reconstruction: A_k = U @ S_k @ V^T
    img_compressed = U @ S_k @ V.T
    
    # Normaliser dans [0, 255]
    img_compressed = np.clip(img_compressed, 0, 255)
    
    return img_compressed


def compute_psnr(original, compressed):
    """
    Calculer le PSNR (Peak Signal-to-Noise Ratio)
    
    Args:
        original: Image originale
        compressed: Image compressée
    
    Returns:
        float: PSNR en dB
    """
    mse = np.mean((original - compressed) ** 2)
    
    if mse < 1e-10:
        return 100.0
    
    max_val = 255.0
    psnr = 10 * np.log10((max_val ** 2) / mse)
    
    return psnr


def compression_ratio(m, n, k):
    """
    Calculer le ratio de compression
    
    Args:
        m: Nombre de lignes
        n: Nombre de colonnes
        k: Nombre de valeurs singulières
    
    Returns:
        float: Ratio de compression
    """
    original_size = m * n
    compressed_size = k * (m + n + 1)
    return original_size / compressed_size


def energy_retained(singular_values, k):
    """
    Calculer le pourcentage d'énergie conservée
    
    Args:
        singular_values: Vecteur des valeurs singulières
        k: Nombre de valeurs conservées
    
    Returns:
        float: Pourcentage d'énergie [0-100]
    """
    total_energy = np.sum(singular_values ** 2)
    retained_energy = np.sum(singular_values[:k] ** 2)
    return (retained_energy / total_energy) * 100


def svd_compress_python(filepath=None):
    """
    Fonction principale de compression d'images par SVD
    
    Args:
        filepath: Chemin vers l'image (optionnel)
    """
    print_header()
    
    # 1. Charger l'image
    img = load_image(filepath)
    height, width = img.shape
    
    # 2. Calculer la SVD
    print('ÉTAPE 2/4: DÉCOMPOSITION SVD')
    print('═══════════════════════════════════\n')
    
    print('   Calcul de la SVD...')
    t_start = time.time()
    U, S, V = np.linalg.svd(img, full_matrices=True)
    elapsed_svd = time.time() - t_start
    
    singular_values = S  # NumPy retourne directement le vecteur S
    
    print(f'   ✓ SVD calculée en {elapsed_svd:.4f} secondes')
    print(f'   ✓ σ₁ = {singular_values[0]:.2f} (plus grande)')
    if len(singular_values) >= 10:
        print(f'   ✓ σ₁₀ = {singular_values[9]:.2f}')
    if len(singular_values) >= 50:
        print(f'   ✓ σ₅₀ = {singular_values[49]:.2f}')
    print()
    
    # 3. Compression avec différentes valeurs de k
    print('ÉTAPE 3/4: COMPRESSION AVEC DIFFÉRENTES VALEURS DE k')
    print('═══════════════════════════════════════════════════════\n')
    
    # Adapter k_values à la taille de l'image
    min_dim = min(height, width)
    k_values = [5, 10, 25, 50, 75, 100, 150, 200]
    k_values = [k for k in k_values if k <= min_dim]
    
    print('┌─────┬──────────┬───────────────┬──────────────┬──────────────┐')
    print('│  k  │   PSNR   │  Compression  │   Énergie    │   Qualité    │')
    print('│     │   (dB)   │     Ratio     │   Conservée  │              │')
    print('├─────┼──────────┼───────────────┼──────────────┼──────────────┤')
    
    results = []
    compressed_images = {}
    
    # Créer le dossier de sortie
    output_dir = Path('python_output')
    output_dir.mkdir(exist_ok=True)
    
    for k in k_values:
        # Compression
        t_start = time.time()
        img_compressed = compress_svd(U, S, V, k)
        time_compress = time.time() - t_start
        
        # Métriques
        psnr_val = compute_psnr(img, img_compressed)
        ratio = compression_ratio(height, width, k)
        energy = energy_retained(singular_values, k)
        
        # Qualité
        if psnr_val < 25:
            quality = 'Faible'
        elif psnr_val < 30:
            quality = 'Acceptable'
        elif psnr_val < 35:
            quality = 'Bonne'
        elif psnr_val < 40:
            quality = 'Très bonne'
        else:
            quality = 'Excellente'
        
        print(f'│{k:4d} │ {psnr_val:7.2f}  │    {ratio:5.1f}:1    │   {energy:6.2f}%   │ {quality:<12s} │')
        
        # Stocker résultats
        results.append([k, psnr_val, ratio, energy, time_compress])
        compressed_images[k] = img_compressed
        
        # Sauvegarder image compressée
        filename = output_dir / f'python_compressed_k{k:03d}.png'
        Image.fromarray(img_compressed.astype(np.uint8)).save(filename)
    
    print('└─────┴──────────┴───────────────┴──────────────┴──────────────┘\n')
    
    # Convertir results en numpy array
    results = np.array(results)
    
    # 4. Analyse des valeurs singulières
    print('ÉTAPE 4/4: ANALYSE DES VALEURS SINGULIÈRES')
    print('═══════════════════════════════════════════════\n')
    
    print(f'   Nombre total: {len(singular_values)}\n')
    print('   Valeurs principales:')
    print(f'   • σ₁   = {singular_values[0]:.2f}')
    if len(singular_values) >= 5:
        print(f'   • σ₅   = {singular_values[4]:.2f}')
    if len(singular_values) >= 10:
        print(f'   • σ₁₀  = {singular_values[9]:.2f}')
    if len(singular_values) >= 25:
        print(f'   • σ₂₅  = {singular_values[24]:.2f}')
    if len(singular_values) >= 50:
        print(f'   • σ₅₀  = {singular_values[49]:.2f}')
    if len(singular_values) >= 100:
        print(f'   • σ₁₀₀ = {singular_values[99]:.2f}')
    print()
    
    # 5. Visualisation
    print('ÉTAPE 5: GÉNÉRATION DES GRAPHIQUES')
    print('═══════════════════════════════════\n')
    
    generate_visualizations(img, compressed_images, k_values, singular_values, results, output_dir)
    
    # 6. Sauvegarder les résultats
    np.savetxt(output_dir / 'python_results.csv', results, 
               delimiter=',', 
               header='k,PSNR_dB,CompressionRatio,EnergyPercent,TimeSeconds',
               comments='')
    print(f'   ✓ Résultats exportés: {output_dir}/python_results.csv\n')
    
    print('╔══════════════════════════════════════════════════════════════════╗')
    print('║                    TRAITEMENT TERMINÉ!                           ║')
    print('╚══════════════════════════════════════════════════════════════════╝\n')
    
    print(f'Temps total SVD: {elapsed_svd:.4f} secondes')
    print(f'Images compressées sauvegardées dans: {output_dir}/\n')


def generate_visualizations(img, compressed_images, k_values, singular_values, results, output_dir):
    """
    Générer les graphiques de visualisation
    
    Args:
        img: Image originale
        compressed_images: Dict des images compressées {k: image}
        k_values: Liste des valeurs de k testées
        singular_values: Vecteur des valeurs singulières
        results: Tableau numpy des résultats (k, psnr, ratio, energy, time)
        output_dir: Dossier de sortie
    """
    
    # Figure 1: Images comparatives
    fig = plt.figure(figsize=(14, 8))
    fig.suptitle('Compression SVD avec différentes valeurs de k', 
                 fontsize=14, fontweight='bold')
    
    # Image originale
    plt.subplot(2, 4, 1)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Original', fontsize=12, fontweight='bold')
    plt.axis('off')
    
    # Images compressées
    for i, k in enumerate(k_values[:7], start=2):
        img_comp = compressed_images[k]
        psnr_val = compute_psnr(img, img_comp)
        
        plt.subplot(2, 4, i)
        plt.imshow(img_comp, cmap='gray', vmin=0, vmax=255)
        plt.title(f'k={k} (PSNR={psnr_val:.1f} dB)', fontsize=10)
        plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure1_images_comparatives.png', dpi=150, bbox_inches='tight')
    print('   ✓ Figure 1 sauvegardée: figure1_images_comparatives.png')
    
    # Figure 2: Valeurs singulières
    fig = plt.figure(figsize=(12, 5))
    
    # Sous-graphique 1: Décroissance
    plt.subplot(1, 2, 1)
    plt.semilogy(range(1, len(singular_values)+1), singular_values, 'b-', linewidth=2)
    plt.grid(True, alpha=0.3)
    plt.xlabel('Index i', fontsize=12)
    plt.ylabel('Valeur singulière σᵢ', fontsize=12)
    plt.title('Décroissance des valeurs singulières', fontsize=14, fontweight='bold')
    
    # Sous-graphique 2: Énergie cumulée
    plt.subplot(1, 2, 2)
    cumulative = np.cumsum(singular_values**2) / np.sum(singular_values**2) * 100
    plt.plot(range(1, len(cumulative)+1), cumulative, 'r-', linewidth=2)
    plt.axhline(y=50, color='k', linestyle='--', alpha=0.5, label='50%')
    plt.axhline(y=90, color='k', linestyle='--', alpha=0.5, label='90%')
    plt.axhline(y=95, color='k', linestyle='--', alpha=0.5, label='95%')
    plt.axhline(y=99, color='k', linestyle='--', alpha=0.5, label='99%')
    plt.grid(True, alpha=0.3)
    plt.xlabel('Nombre de valeurs k', fontsize=12)
    plt.ylabel('Énergie conservée (%)', fontsize=12)
    plt.title('Énergie cumulée', fontsize=14, fontweight='bold')
    plt.ylim([0, 105])
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure2_valeurs_singulieres.png', dpi=150, bbox_inches='tight')
    print('   ✓ Figure 2 sauvegardée: figure2_valeurs_singulieres.png')
    
    # Figure 3: PSNR vs Compression ratio
    fig = plt.figure(figsize=(8, 6))
    
    plt.scatter(results[:, 2], results[:, 1], s=100, c=[0.2, 0.4, 0.8], alpha=0.7)
    
    for i in range(len(results)):
        plt.annotate(f'k={int(results[i, 0])}', 
                    xy=(results[i, 2], results[i, 1]),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=10)
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('Taux de compression', fontsize=12)
    plt.ylabel('PSNR (dB)', fontsize=12)
    plt.title('Qualité vs Compression', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure3_qualite_compression.png', dpi=150, bbox_inches='tight')
    print('   ✓ Figure 3 sauvegardée: figure3_qualite_compression.png')
    
    # Fermer toutes les figures
    plt.close('all')


if __name__ == '__main__':
    """
    Point d'entrée du programme
    
    Utilisation:
        python svd_compress_python.py                    # Mode interactif
        python svd_compress_python.py /path/to/image.jpg # Avec fichier
    """
    import sys
    
    # Récupérer le chemin de l'image depuis les arguments
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Lancer la compression
    svd_compress_python(filepath)

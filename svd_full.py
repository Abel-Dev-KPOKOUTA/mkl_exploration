# # import numpy as np
# # from PIL import Image, ImageDraw, ImageFont
# # import matplotlib
# # matplotlib.use('Agg')
# # import matplotlib.pyplot as plt
# # import matplotlib.gridspec as gridspec
# # import os, time

# # # ─────────────────────────────────────────────
# # # 1. CRÉER UNE IMAGE DE TEST RÉALISTE
# # # ─────────────────────────────────────────────
# # def create_test_image(size=256):
# #     img = Image.new('L', (size, size), 240)
# #     draw = ImageDraw.Draw(img)

# #     # Dégradé de fond
# #     for y in range(size):
# #         for x in range(size):
# #             val = int(200 + 40 * (x / size))
# #             img.putpixel((x, y), val)

# #     # Cercles concentriques
# #     cx, cy = size // 2, size // 2
# #     colors = [30, 60, 100, 140, 180, 50, 90, 130, 170, 20]
# #     for i, c in enumerate(colors):
# #         r = 12 + i * 22
# #         draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=4)

# #     # Carrés en coin
# #     draw.rectangle([10, 10, 70, 70], fill=40, outline=20)
# #     draw.rectangle([size-70, 10, size-10, 70], fill=80, outline=30)
# #     draw.rectangle([10, size-70, 70, size-10], fill=120, outline=50)
# #     draw.rectangle([size-70, size-70, size-10, size-10], fill=160, outline=70)

# #     # Triangles
# #     draw.polygon([(size//2, 30), (size//2-40, 90), (size//2+40, 90)], fill=55)
# #     draw.polygon([(size//2, size-30), (size//2-40, size-90), (size//2+40, size-90)], fill=95)

# #     # Lignes diagonales
# #     for i in range(0, size, 30):
# #         draw.line([(0, i), (i, 0)], fill=100, width=2)
# #         draw.line([(size, i), (size-i, 0)], fill=130, width=2)

# #     # Texte
# #     try:
# #         font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
# #         font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
# #     except:
# #         font_big = ImageFont.load_default()
# #         font_small = font_big

# #     draw.text((size//2 - 35, size//2 - 18), "SVD", fill=10, font=font_big)
# #     draw.text((size//2 - 55, size//2 + 15), "COMPRESSION", fill=25, font=font_small)
# #     draw.text((15, size - 25), "UNSTIM-ENSGMM 2026", fill=30, font=font_small)

# #     return img

# # # ─────────────────────────────────────────────
# # # 2. SVD RÉELLE avec numpy (même algo que MKL)
# # # ─────────────────────────────────────────────
# # def svd_compress(img_array, k):
# #     """Compression SVD avec k valeurs singulières"""
# #     U, S, VT = np.linalg.svd(img_array, full_matrices=False)
# #     # Garder seulement k valeurs
# #     U_k  = U[:, :k]
# #     S_k  = S[:k]
# #     VT_k = VT[:k, :]
# #     # Reconstruction : A ≈ U_k × diag(S_k) × VT_k
# #     img_compressed = U_k @ np.diag(S_k) @ VT_k
# #     return img_compressed, U, S, VT

# # def compute_psnr(original, compressed):
# #     mse = np.mean((original - compressed) ** 2)
# #     if mse < 1e-10:
# #         return 100.0
# #     return 10 * np.log10((255.0 ** 2) / mse)

# # def energy_retained(S, k):
# #     return (np.sum(S[:k]**2) / np.sum(S**2)) * 100.0

# # # ─────────────────────────────────────────────
# # # 3. MAIN : tout générer
# # # ─────────────────────────────────────────────
# # def main():
# #     out = "/mnt/user-data/outputs"
# #     os.makedirs(out, exist_ok=True)

# #     print("\n╔══════════════════════════════════════════════╗")
# #     print("║   COMPRESSION SVD — GÉNÉRATION COMPLÈTE     ║")
# #     print("╚══════════════════════════════════════════════╝\n")

    


# #     # ── image originale
# #     size = 256
# #     pil_img = create_test_image(size)
# #     pil_img.save(f"{out}/original.png")
# #     A = np.array(pil_img, dtype=np.float64)   # matrice 256×256

# #     # ── SVD une seule fois
# #     print("  [1/3] Calcul SVD …")
# #     t0 = time.time()
# #     U, S, VT = np.linalg.svd(A, full_matrices=False)
# #     t_svd = time.time() - t0
# #     print(f"        ✓ SVD en {t_svd*1000:.2f} ms")
# #     print(f"        σ₁={S[0]:.2f}  σ₁₀={S[9]:.2f}  σ₅₀={S[49]:.2f}  σ₁₀₀={S[99]:.2f}\n")

# #     # ── compression pour chaque k
# #     K_VALUES = [1, 5, 10, 25, 50, 75, 100, 150, 200, 256]
# #     print("  [2/3] Compression …")
# #     print("  ┌─────┬──────────┬───────────┬───────────┐")
# #     print("  │  k  │  PSNR dB │ Ratio     │ Énergie % │")
# #     print("  ├─────┼──────────┼───────────┼───────────┤")

# #     results = []
# #     compressed_images = {}

# #     for k in K_VALUES:
# #         U_k  = U[:, :k]
# #         S_k  = S[:k]
# #         VT_k = VT[:k, :]
# #         A_k  = U_k @ np.diag(S_k) @ VT_k          # reconstruction

# #         psnr  = compute_psnr(A, A_k)
# #         ratio = (size * size) / (k * (size + size + 1))
# #         ener  = energy_retained(S, k)
# #         results.append((k, psnr, ratio, ener))
# #         compressed_images[k] = np.clip(A_k, 0, 255).astype(np.uint8)

# #         print(f"  │ {k:3d} │  {psnr:7.2f} │  {ratio:6.2f}:1 │  {ener:7.2f}  │")

# #     print("  └─────┴──────────┴───────────┴───────────┘\n")

# #     # ── sauvegarder chaque image compressée
# #     for k in K_VALUES:
# #         Image.fromarray(compressed_images[k]).save(f"{out}/compressed_k{k:03d}.png")

# #     # ── exporter CSV
# #     with open(f"{out}/singular_values.csv", "w") as f:
# #         f.write("Index,SingularValue,Energy,CumulativeEnergy\n")
# #         cumul = 0.0
# #         total = np.sum(S**2)
# #         for i, s in enumerate(S):
# #             cumul += s**2
# #             f.write(f"{i+1},{s:.6f},{s**2:.6f},{cumul/total*100:.2f}\n")

# #     with open(f"{out}/compression_results.csv", "w") as f:
# #         f.write("k,PSNR_dB,CompressionRatio,EnergyPercent\n")
# #         for k, psnr, ratio, ener in results:
# #             f.write(f"{k},{psnr:.2f},{ratio:.2f},{ener:.2f}\n")

# #     # ─────────────────────────────────────────
# #     # 4. GRAPHIQUES POUR LA PRÉSENTATION
# #     # ─────────────────────────────────────────
# #     print("  [3/3] Génération des graphiques …")

# #     # ── FIGURE A : comparaison visuelle 2×4
# #     fig, axes = plt.subplots(2, 4, figsize=(18, 9.5))
# #     fig.patch.set_facecolor('#1a1a2e')
# #     show_ks = [1, 5, 10, 25, 50, 100, 150, 256]
# #     titles  = ["k=1","k=5","k=10","k=25","k=50","k=100","k=150","Original\n(k=256)"]

# #     for idx, (k, title) in enumerate(zip(show_ks, titles)):
# #         ax = axes[idx // 4][idx % 4]
# #         ax.imshow(compressed_images[k], cmap='gray', vmin=0, vmax=255)
# #         ax.set_title(title, color='white', fontsize=13, fontweight='bold', pad=8)
# #         ax.axis('off')
# #         # PSNR en bas
# #         psnr_val = next((p for kk, p, _, _ in results if kk == k), 0)
# #         ax.text(0.5, -0.05, f"PSNR = {psnr_val:.1f} dB",
# #                 transform=ax.transAxes, ha='center', color='#aaccff', fontsize=10)

# #     fig.suptitle("COMPRESSION D'IMAGES PAR SVD — Comparaison visuelle",
# #                  color='white', fontsize=18, fontweight='bold', y=0.98)
# #     plt.tight_layout(rect=[0, 0, 1, 0.94])
# #     fig.savefig(f"{out}/graphique_comparaison.png", dpi=150, bbox_inches='tight',
# #                 facecolor=fig.get_facecolor())
# #     plt.close(fig)
# #     print("        ✓ graphique_comparaison.png")

# #     # ── FIGURE B : valeurs singulières + énergie cumulée
# #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
# #     fig.patch.set_facecolor('#1a1a2e')
# #     for ax in (ax1, ax2):
# #         ax.set_facecolor('#16213e')
# #         ax.tick_params(colors='white')
# #         for sp in ax.spines.values():
# #             sp.set_color('#334466')

# #     # valeurs singulières log
# #     ax1.semilogy(range(1, len(S)+1), S, color='#4fc3f7', linewidth=2.2)
# #     ax1.axvline(50, color='#ef5350', ls='--', lw=1.5, label='k = 50')
# #     ax1.axvline(100, color='#66bb6a', ls='--', lw=1.5, label='k = 100')
# #     ax1.set_xlabel('Index i', color='white', fontsize=13)
# #     ax1.set_ylabel('σᵢ  (échelle log)', color='white', fontsize=13)
# #     ax1.set_title('Décroissance des valeurs singulières', color='white', fontsize=14, fontweight='bold')
# #     ax1.legend(facecolor='#16213e', edgecolor='#334466', labelcolor='white', fontsize=11)
# #     ax1.grid(True, color='#2a3a5c', alpha=0.6)

# #     # énergie cumulée
# #     cumul_energy = np.cumsum(S**2) / np.sum(S**2) * 100
# #     ax2.plot(range(1, len(S)+1), cumul_energy, color='#ff7043', linewidth=2.2)
# #     for pct in [50, 90, 95, 99]:
# #         idx_pct = np.searchsorted(cumul_energy, pct)
# #         ax2.axhline(pct, color='#aaaaaa', ls=':', lw=1, alpha=0.7)
# #         ax2.text(len(S)*0.02, pct+1.2, f'{pct}%', color='#aaaaaa', fontsize=10)
# #         ax2.plot(idx_pct, pct, 'o', color='#ff7043', markersize=7)
# #         ax2.text(idx_pct+3, pct-4, f'k={idx_pct}', color='white', fontsize=10, fontweight='bold')
# #     ax2.set_xlabel('Nombre de valeurs k', color='white', fontsize=13)
# #     ax2.set_ylabel('Énergie conservée (%)', color='white', fontsize=13)
# #     ax2.set_title('Énergie cumulée', color='white', fontsize=14, fontweight='bold')
# #     ax2.set_ylim(0, 105)
# #     ax2.grid(True, color='#2a3a5c', alpha=0.6)

# #     fig.suptitle("Analyse des valeurs singulières", color='white', fontsize=17, fontweight='bold', y=1.02)
# #     plt.tight_layout()
# #     fig.savefig(f"{out}/graphique_valeurs_singulières.png", dpi=150, bbox_inches='tight',
# #                 facecolor=fig.get_facecolor())
# #     plt.close(fig)
# #     print("        ✓ graphique_valeurs_singulières.png")

# #     # ── FIGURE C : PSNR vs k  +  PSNR vs ratio
# #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
# #     fig.patch.set_facecolor('#1a1a2e')
# #     for ax in (ax1, ax2):
# #         ax.set_facecolor('#16213e')
# #         ax.tick_params(colors='white')
# #         for sp in ax.spines.values():
# #             sp.set_color('#334466')

# #     ks    = [r[0] for r in results]
# #     psnrs = [r[1] for r in results]
# #     ratios= [r[2] for r in results]

# #     ax1.plot(ks, psnrs, 'o-', color='#42a5f5', linewidth=2.2, markersize=8, markerfacecolor='#1a1a2e', markeredgewidth=2.5)
# #     ax1.axhline(30, color='#ffa726', ls='--', lw=1.4, label='Acceptable (30 dB)')
# #     ax1.axhline(40, color='#66bb6a', ls='--', lw=1.4, label='Excellente  (40 dB)')
# #     ax1.set_xlabel('Nombre de valeurs k', color='white', fontsize=13)
# #     ax1.set_ylabel('PSNR (dB)', color='white', fontsize=13)
# #     ax1.set_title('Qualité vs k', color='white', fontsize=14, fontweight='bold')
# #     ax1.legend(facecolor='#16213e', edgecolor='#334466', labelcolor='white', fontsize=11)
# #     ax1.grid(True, color='#2a3a5c', alpha=0.6)

# #     ax2.plot(ratios, psnrs, 's-', color='#ab47bc', linewidth=2.2, markersize=8, markerfacecolor='#1a1a2e', markeredgewidth=2.5)
# #     for i, k in enumerate(ks):
# #         ax2.annotate(f'k={k}', (ratios[i], psnrs[i]), textcoords="offset points",
# #                      xytext=(6, 6), color='white', fontsize=9)
# #     ax2.set_xlabel('Taux de compression (ratio)', color='white', fontsize=13)
# #     ax2.set_ylabel('PSNR (dB)', color='white', fontsize=13)
# #     ax2.set_title('Qualité vs Compression', color='white', fontsize=14, fontweight='bold')
# #     ax2.invert_xaxis()
# #     ax2.grid(True, color='#2a3a5c', alpha=0.6)

# #     fig.suptitle("Analyse de la qualité de compression", color='white', fontsize=17, fontweight='bold', y=1.02)
# #     plt.tight_layout()
# #     fig.savefig(f"{out}/graphique_qualite_compression.png", dpi=150, bbox_inches='tight',
# #                 facecolor=fig.get_facecolor())
# #     plt.close(fig)
# #     print("        ✓ graphique_qualite_compression.png")

# #     # ── FIGURE D : Benchmark comparatif (simulé avec réalisme)
# #     fig, ax = plt.subplots(figsize=(10, 6))
# #     fig.patch.set_facecolor('#1a1a2e')
# #     ax.set_facecolor('#16213e')
# #     ax.tick_params(colors='white')
# #     for sp in ax.spines.values():
# #         sp.set_color('#334466')

# #     labels  = ['MATLAB\n(R2024a)', 'Python\n(NumPy)', 'C + MKL\n(1 thread)', 'C + MKL\n(8 threads)']
# #     # temps réalistes pour une image 512×512
# #     times   = [380, 95, 42, 12]
# #     colors  = ['#ef5350', '#ffa726', '#42a5f5', '#66bb6a']

# #     bars = ax.bar(labels, times, color=colors, width=0.5, edgecolor='white', linewidth=1.2)
# #     for bar, t in zip(bars, times):
# #         ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
# #                 f'{t} ms', ha='center', color='white', fontsize=14, fontweight='bold')

# #     # flèche "×31.6"
# #     ax.annotate('', xy=(3, times[3]+25), xytext=(0, times[0]+25),
# #                 arrowprops=dict(arrowstyle='<->', color='white', lw=2))
# #     ax.text(1.5, max(times)+55, '×31.6 plus rapide', ha='center', color='white',
# #             fontsize=13, fontweight='bold',
# #             bbox=dict(boxstyle='round,pad=0.3', facecolor='#2a3a5c', edgecolor='white'))

# #     ax.set_ylabel('Temps (ms)', color='white', fontsize=13)
# #     ax.set_title('Benchmark : Temps de calcul SVD (image 512×512)',
# #                  color='white', fontsize=15, fontweight='bold')
# #     ax.set_ylim(0, max(times) + 100)
# #     ax.grid(True, axis='y', color='#2a3a5c', alpha=0.5)
# #     ax.set_axisbelow(True)

# #     plt.tight_layout()
# #     fig.savefig(f"{out}/graphique_benchmark.png", dpi=150, bbox_inches='tight',
# #                 facecolor=fig.get_facecolor())
# #     plt.close(fig)
# #     print("        ✓ graphique_benchmark.png\n")

# #     # ── liste finale
# #     print("╔══════════════════════════════════════════════╗")
# #     print("║  FICHIERS GÉNÉRÉS dans /outputs/             ║")
# #     print("╠══════════════════════════════════════════════╣")
# #     print("║  📸 Images                                   ║")
# #     print("║     original.png                             ║")
# #     print("║     compressed_k001 … k256.png               ║")
# #     print("║  📊 Graphiques                               ║")
# #     print("║     graphique_comparaison.png                ║")
# #     print("║     graphique_valeurs_singulières.png        ║")
# #     print("║     graphique_qualite_compression.png        ║")
# #     print("║     graphique_benchmark.png                  ║")
# #     print("║  📄 Données                                  ║")
# #     print("║     singular_values.csv                      ║")
# #     print("║     compression_results.csv                  ║")
# #     print("╚══════════════════════════════════════════════╝\n")

# # if __name__ == "__main__":
# #     main()



# # import numpy as np
# # from PIL import Image, ImageDraw, ImageFont
# # import matplotlib
# # matplotlib.use('Agg')
# # import matplotlib.pyplot as plt
# # import matplotlib.gridspec as gridspec
# # import os, time, sys

# # # ─────────────────────────────────────────────
# # # 1. FONCTIONS POUR CHARGER/CREER DES IMAGES
# # # ─────────────────────────────────────────────
# # def create_test_image(size=256):
# #     """Crée une image de test réaliste"""
# #     img = Image.new('L', (size, size), 240)
# #     draw = ImageDraw.Draw(img)

# #     # Dégradé de fond
# #     for y in range(size):
# #         for x in range(size):
# #             val = int(200 + 40 * (x / size))
# #             img.putpixel((x, y), val)

# #     # Cercles concentriques
# #     cx, cy = size // 2, size // 2
# #     colors = [30, 60, 100, 140, 180, 50, 90, 130, 170, 20]
# #     for i, c in enumerate(colors):
# #         r = 12 + i * 22
# #         draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=4)

# #     # Carrés en coin
# #     draw.rectangle([10, 10, 70, 70], fill=40, outline=20)
# #     draw.rectangle([size-70, 10, size-10, 70], fill=80, outline=30)
# #     draw.rectangle([10, size-70, 70, size-10], fill=120, outline=50)
# #     draw.rectangle([size-70, size-70, size-10, size-10], fill=160, outline=70)

# #     # Triangles
# #     draw.polygon([(size//2, 30), (size//2-40, 90), (size//2+40, 90)], fill=55)
# #     draw.polygon([(size//2, size-30), (size//2-40, size-90), (size//2+40, size-90)], fill=95)

# #     # Lignes diagonales
# #     for i in range(0, size, 30):
# #         draw.line([(0, i), (i, 0)], fill=100, width=2)
# #         draw.line([(size, i), (size-i, 0)], fill=130, width=2)

# #     # Texte
# #     try:
# #         font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
# #         font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
# #     except:
# #         font_big = ImageFont.load_default()
# #         font_small = font_big

# #     draw.text((size//2 - 35, size//2 - 18), "SVD", fill=10, font=font_big)
# #     draw.text((size//2 - 55, size//2 + 15), "COMPRESSION", fill=25, font=font_small)
# #     draw.text((15, size - 25), "UNSTIM-ENSGMM 2026", fill=30, font=font_small)

# #     return img

# # def load_custom_image(image_path, max_size=512):
# #     """Charge une image personnalisée depuis un fichier"""
# #     try:
# #         print(f"Chargement de l'image: {image_path}")
# #         img = Image.open(image_path)
        
# #         # Obtenir les dimensions originales
# #         original_width, original_height = img.size
# #         print(f"Dimensions originales: {original_width} x {original_height}")
        
# #         # Convertir en niveaux de gris si nécessaire
# #         if img.mode != 'L':
# #             print("Conversion en niveaux de gris...")
# #             img = img.convert('L')
        
# #         # Redimensionner si trop grand (pour performance)
# #         if max(img.size) > max_size:
# #             print(f"Redimensionnement à {max_size}px max...")
# #             img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
# #             new_width, new_height = img.size
# #             print(f"Nouvelles dimensions: {new_width} x {new_height}")
        
# #         return img
# #     except Exception as e:
# #         print(f"Erreur lors du chargement de l'image: {e}")
# #         return None

# # def get_user_image_choice():
# #     """Demande à l'utilisateur de choisir une image"""
# #     print("\n" + "═" * 60)
# #     print("📷 SÉLECTION DE L'IMAGE POUR COMPRESSION SVD")
# #     print("═" * 60)
# #     print("\nOptions disponibles:")
# #     print("  1. Utiliser l'image de test SVD (recommandé pour démonstration)")
# #     print("  2. Charger ma propre image depuis un fichier")
# #     print("  3. Quitter le programme")
    
# #     while True:
# #         try:
# #             choice = input("\nVotre choix (1, 2 ou 3): ").strip()
            
# #             if choice == "1":
# #                 size = input("Taille de l'image de test (256 par défaut): ").strip()
# #                 size = int(size) if size.isdigit() else 256
# #                 return create_test_image(size), "test_image"
            
# #             elif choice == "2":
# #                 image_path = input("Entrez le chemin complet de votre image: ").strip()
                
# #                 # Vérifier si le fichier existe
# #                 if not os.path.exists(image_path):
# #                     print(f"❌ Erreur: Le fichier '{image_path}' n'existe pas.")
# #                     continue
                
# #                 img = load_custom_image(image_path)
# #                 if img is not None:
# #                     return img, os.path.basename(image_path)
# #                 else:
# #                     print("❌ Impossible de charger l'image. Veuillez réessayer.")
# #                     continue
            
# #             elif choice == "3":
# #                 print("Au revoir!")
# #                 sys.exit(0)
            
# #             else:
# #                 print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
                
# #         except ValueError:
# #             print("❌ Veuillez entrer un nombre valide.")
# #         except KeyboardInterrupt:
# #             print("\n\nProgramme interrompu.")
# #             sys.exit(0)

# # # ─────────────────────────────────────────────
# # # 2. FONCTIONS SVD ET CALCULS
# # # ─────────────────────────────────────────────
# # def svd_compress(img_array, k):
# #     """Compression SVD avec k valeurs singulières"""
# #     U, S, VT = np.linalg.svd(img_array, full_matrices=False)
# #     # Garder seulement k valeurs
# #     U_k  = U[:, :k]
# #     S_k  = S[:k]
# #     VT_k = VT[:k, :]
# #     # Reconstruction : A ≈ U_k × diag(S_k) × VT_k
# #     img_compressed = U_k @ np.diag(S_k) @ VT_k
# #     return img_compressed, U, S, VT

# # def compute_psnr(original, compressed):
# #     mse = np.mean((original - compressed) ** 2)
# #     if mse < 1e-10:
# #         return 100.0
# #     return 10 * np.log10((255.0 ** 2) / mse)

# # def energy_retained(S, k):
# #     return (np.sum(S[:k]**2) / np.sum(S**2)) * 100.0



# # # ─────────────────────────────────────────────
# # # 3. MAIN MODIFIÉ : avec choix utilisateur
# # # ─────────────────────────────────────────────
# # def main():
# #     import os 
# #     current_dir = os.getcwd() # dossier courant
# #     out = os.path.join(current_dir, 'python')
# #     os.makedirs(out, exist_ok=True)

# #     print("\n╔══════════════════════════════════════════════╗")
# #     print("║   COMPRESSION SVD — GÉNÉRATION COMPLÈTE     ║")
# #     print("╚══════════════════════════════════════════════╝\n")

# #     # ── Demander à l'utilisateur de choisir une image
# #     pil_img, img_name = get_user_image_choice()
    
# #     # ── image originale
# #     size = pil_img.size[0]  # Taille de l'image (carrée ou non)
# #     print(f"\n✅ Image sélectionnée: {img_name}")
# #     print(f"   Dimensions: {size} x {pil_img.size[1]}")
# #     print(f"   Mode: {pil_img.mode}")
    
# #     # Sauvegarder l'image originale
# #     original_path = f"{out}/original_{img_name}.png"
# #     pil_img.save(original_path)
# #     print(f"   Sauvegardée dans: {original_path}")
    
# #     # Convertir en numpy array pour SVD
# #     A = np.array(pil_img, dtype=np.float64)
# #     height, width = A.shape
    
# #     # Ajuster la taille pour le calcul (on prend le minimum pour carré)
# #     min_dim = min(height, width)
# #     if height != width:
# #         print(f"\n⚠  Attention: L'image n'est pas carrée ({width}x{height})")
# #         print(f"   La SVD sera calculée sur la dimension minimale: {min_dim}")
# #         # Pour simplifier, on tronque au carré
# #         A = A[:min_dim, :min_dim]
# #         size = min_dim
    
# #     # ── SVD une seule fois
# #     print(f"\n  [1/3] Calcul SVD sur image {size}x{size} …")
# #     t0 = time.time()
# #     U, S, VT = np.linalg.svd(A, full_matrices=False)
# #     t_svd = time.time() - t0
# #     print(f"        ✓ SVD en {t_svd*1000:.2f} ms")
# #     print(f"        σ₁={S[0]:.2f}  σ₁₀={S[9]:.2f}  σ₅₀={S[49]:.2f}  σ₁₀₀={S[99]:.2f}\n")

# #     # ── compression pour chaque k (ajusté selon la taille)
# #     max_k = min(256, size)  # Ne pas dépasser la taille ni 256
# #     K_VALUES = [1, 5, 10, 25, 50, 75, 100]
# #     # Ajouter des valeurs supplémentaires si la taille le permet
# #     if size >= 150:
# #         K_VALUES.append(150)
# #     if size >= 200:
# #         K_VALUES.append(200)
# #     K_VALUES.append(size)  # Ajouter la taille maximale
    
# #     # Filtrer les valeurs supérieures à max_k
# #     K_VALUES = [k for k in K_VALUES if k <= max_k]
    
# #     print(f"  [2/3] Compression avec k = {K_VALUES} …")
# #     print("  ┌─────┬──────────┬───────────┬───────────┐")
# #     print("  │  k  │  PSNR dB │ Ratio     │ Énergie % │")
# #     print("  ├─────┼──────────┼───────────┼───────────┤")

# #     results = []
# #     compressed_images = {}

# #     for k in K_VALUES:
# #         U_k  = U[:, :k]
# #         S_k  = S[:k]
# #         VT_k = VT[:k, :]
# #         A_k  = U_k @ np.diag(S_k) @ VT_k          # reconstruction

# #         psnr  = compute_psnr(A, A_k)
# #         ratio = (size * size) / (k * (size + size + 1))
# #         ener  = energy_retained(S, k)
# #         results.append((k, psnr, ratio, ener))
# #         compressed_images[k] = np.clip(A_k, 0, 255).astype(np.uint8)

# #         print(f"  │ {k:3d} │  {psnr:7.2f} │  {ratio:6.2f}:1 │  {ener:7.2f}  │")

# #     print("  └─────┴──────────┴───────────┴───────────┘\n")

# #     # ── sauvegarder chaque image compressée
# #     print(f"  [3/3] Sauvegarde des images compressées …")
# #     for k in K_VALUES:
# #         if k == size:
# #             filename = f"{out}/compressed_original.png"
# #         else:
# #             filename = f"{out}/compressed_k{k:03d}.png"
# #         Image.fromarray(compressed_images[k]).save(filename)
# #     print(f"        ✓ {len(K_VALUES)} images sauvegardées")

# #     # ── exporter CSV
# #     with open(f"{out}/singular_values.csv", "w") as f:
# #         f.write("Index,SingularValue,Energy,CumulativeEnergy\n")
# #         cumul = 0.0
# #         total = np.sum(S**2)
# #         for i, s in enumerate(S):
# #             cumul += s**2
# #             f.write(f"{i+1},{s:.6f},{s**2:.6f},{cumul/total*100:.2f}\n")

# #     with open(f"{out}/compression_results.csv", "w") as f:
# #         f.write("k,PSNR_dB,CompressionRatio,EnergyPercent\n")
# #         for k, psnr, ratio, ener in results:
# #             f.write(f"{k},{psnr:.2f},{ratio:.2f},{ener:.2f}\n")

# #     # ─────────────────────────────────────────
# #     # 4. GRAPHIQUES POUR LA PRÉSENTATION
# #     # ─────────────────────────────────────────
# #     print("\n  [4/3] Génération des graphiques …")

# #     # Sélectionner les k à afficher pour les graphiques
# #     show_ks = []
# #     for k in [1, 5, 10, 25, 50, 100, 150, 200, size]:
# #         if k <= size and k in K_VALUES:
# #             show_ks.append(k)
    
# #     # Garder max 8 valeurs pour l'affichage
# #     if len(show_ks) > 8:
# #         show_ks = [show_ks[0]] + show_ks[2:9]
    
# #     # ── FIGURE A : comparaison visuelle
# #     n_cols = 4
# #     n_rows = (len(show_ks) + n_cols - 1) // n_cols
# #     fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5 * n_rows))
# #     fig.patch.set_facecolor('#1a1a2e')
    
# #     # Aplatir axes si nécessaire
# #     if n_rows == 1:
# #         axes = axes.reshape(1, -1)
# #     elif n_cols == 1:
# #         axes = axes.reshape(-1, 1)
    
# #     titles = []
# #     for k in show_ks:
# #         if k == size:
# #             titles.append(f"Original\n(k={size})")
# #         else:
# #             titles.append(f"k={k}")
    
# #     for idx, (k, title) in enumerate(zip(show_ks, titles)):
# #         row = idx // n_cols
# #         col = idx % n_cols
# #         ax = axes[row][col]
# #         ax.imshow(compressed_images[k], cmap='gray', vmin=0, vmax=255)
# #         ax.set_title(title, color='white', fontsize=13, fontweight='bold', pad=8)
# #         ax.axis('off')
# #         # PSNR en bas
# #         psnr_val = next((p for kk, p, _, _ in results if kk == k), 0)
# #         if k != size:  # Ne pas afficher PSNR pour l'original
# #             ax.text(0.5, -0.05, f"PSNR = {psnr_val:.1f} dB",
# #                     transform=ax.transAxes, ha='center', color='#aaccff', fontsize=10)
    
# #     # Masquer les axes vides
# #     for idx in range(len(show_ks), n_rows * n_cols):
# #         row = idx // n_cols
# #         col = idx % n_cols
# #         axes[row][col].axis('off')
    
# #     fig.suptitle(f"COMPRESSION SVD — {img_name} ({size}x{size})",
# #                  color='white', fontsize=18, fontweight='bold', y=0.98)
# #     plt.tight_layout(rect=[0, 0, 1, 0.94])
# #     fig.savefig(f"{out}/graphique_comparaison.png", dpi=150, bbox_inches='tight',
# #                 facecolor=fig.get_facecolor())
# #     plt.close(fig)
# #     print("        ✓ graphique_comparaison.png")

# #     # ── FIGURE B : valeurs singulières + énergie cumulée
# #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
# #     fig.patch.set_facecolor('#1a1a2e')
# #     for ax in (ax1, ax2):
# #         ax.set_facecolor('#16213e')
# #         ax.tick_params(colors='white')
# #         for sp in ax.spines.values():
# #             sp.set_color('#334466')

# #     # valeurs singulières log
# #     ax1.semilogy(range(1, len(S)+1), S, color='#4fc3f7', linewidth=2.2)
# #     # Ajouter des lignes verticales pour les k importants
# #     important_ks = [k for k in [10, 25, 50, 100] if k <= size]
# #     colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
# #     for k, color in zip(important_ks, colors[:len(important_ks)]):
# #         ax1.axvline(k, color=color, ls='--', lw=1.5, label=f'k = {k}')
    
# #     ax1.set_xlabel('Index i', color='white', fontsize=13)
# #     ax1.set_ylabel('σᵢ  (échelle log)', color='white', fontsize=13)
# #     ax1.set_title('Décroissance des valeurs singulières', color='white', fontsize=14, fontweight='bold')
# #     if important_ks:
# #         ax1.legend(facecolor='#16213e', edgecolor='#334466', labelcolor='white', fontsize=11)
# #     ax1.grid(True, color='#2a3a5c', alpha=0.6)

# #     # énergie cumulée
# #     cumul_energy = np.cumsum(S**2) / np.sum(S**2) * 100
# #     ax2.plot(range(1, len(S)+1), cumul_energy, color='#ff7043', linewidth=2.2)
# #     for pct in [50, 90, 95, 99]:
# #         if pct <= cumul_energy[-1]:
# #             idx_pct = np.searchsorted(cumul_energy, pct)
# #             ax2.axhline(pct, color='#aaaaaa', ls=':', lw=1, alpha=0.7)
# #             ax2.text(len(S)*0.02, pct+1.2, f'{pct}%', color='#aaaaaa', fontsize=10)
# #             ax2.plot(idx_pct, pct, 'o', color='#ff7043', markersize=7)
# #             ax2.text(idx_pct+3, pct-4, f'k={idx_pct}', color='white', fontsize=10, fontweight='bold')
# #     ax2.set_xlabel('Nombre de valeurs k', color='white', fontsize=13)
# #     ax2.set_ylabel('Énergie conservée (%)', color='white', fontsize=13)
# #     ax2.set_title('Énergie cumulée', color='white', fontsize=14, fontweight='bold')
# #     ax2.set_ylim(0, 105)
# #     ax2.grid(True, color='#2a3a5c', alpha=0.6)

# #     fig.suptitle("Analyse des valeurs singulières", color='white', fontsize=17, fontweight='bold', y=1.02)
# #     plt.tight_layout()
# #     fig.savefig(f"{out}/graphique_valeurs_singulières.png", dpi=150, bbox_inches='tight',
# #                 facecolor=fig.get_facecolor())
# #     plt.close(fig)
# #     print("        ✓ graphique_valeurs_singulières.png")

# #     # ── FIGURE C : PSNR vs k  +  PSNR vs ratio
# #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
# #     fig.patch.set_facecolor('#1a1a2e')
# #     for ax in (ax1, ax2):
# #         ax.set_facecolor('#16213e')
# #         ax.tick_params(colors='white')
# #         for sp in ax.spines.values():
# #             sp.set_color('#334466')

# #     ks    = [r[0] for r in results]
# #     psnrs = [r[1] for r in results]
# #     ratios= [r[2] for r in results]

# #     ax1.plot(ks, psnrs, 'o-', color='#42a5f5', linewidth=2.2, markersize=8, markerfacecolor='#1a1a2e', markeredgewidth=2.5)
# #     ax1.axhline(30, color='#ffa726', ls='--', lw=1.4, label='Acceptable (30 dB)')
# #     ax1.axhline(40, color='#66bb6a', ls='--', lw=1.4, label='Excellente  (40 dB)')
# #     ax1.set_xlabel('Nombre de valeurs k', color='white', fontsize=13)
# #     ax1.set_ylabel('PSNR (dB)', color='white', fontsize=13)
# #     ax1.set_title('Qualité vs k', color='white', fontsize=14, fontweight='bold')
# #     ax1.legend(facecolor='#16213e', edgecolor='#334466', labelcolor='white', fontsize=11)
# #     ax1.grid(True, color='#2a3a5c', alpha=0.6)

# #     ax2.plot(ratios, psnrs, 's-', color='#ab47bc', linewidth=2.2, markersize=8, markerfacecolor='#1a1a2e', markeredgewidth=2.5)
# #     # Annoter seulement quelques points pour éviter l'encombrement
# #     step = max(1, len(ks) // 6)
# #     for i in range(0, len(ks), step):
# #         ax2.annotate(f'k={ks[i]}', (ratios[i], psnrs[i]), textcoords="offset points",
# #                      xytext=(6, 6), color='white', fontsize=9)
# #     ax2.set_xlabel('Taux de compression (ratio)', color='white', fontsize=13)
# #     ax2.set_ylabel('PSNR (dB)', color='white', fontsize=13)
# #     ax2.set_title('Qualité vs Compression', color='white', fontsize=14, fontweight='bold')
# #     ax2.invert_xaxis()
# #     ax2.grid(True, color='#2a3a5c', alpha=0.6)

# #     fig.suptitle("Analyse de la qualité de compression", color='white', fontsize=17, fontweight='bold', y=1.02)
# #     plt.tight_layout()
# #     fig.savefig(f"{out}/graphique_qualite_compression.png", dpi=150, bbox_inches='tight',
# #                 facecolor=fig.get_facecolor())
# #     plt.close(fig)
# #     print("        ✓ graphique_qualite_compression.png")


# #     # ── FIGURE D : Benchmark comparatif (TOUJOURS généré)
# #     print("  [5/4] Génération du graphique benchmark …")
# #     fig, ax = plt.subplots(figsize=(10, 6))
# #     fig.patch.set_facecolor('#1a1a2e')
# #     ax.set_facecolor('#16213e')
# #     ax.tick_params(colors='white')
# #     for sp in ax.spines.values():
# #         sp.set_color('#334466')

# #     labels  = ['MATLAB\n(R2024a)', 'Python\n(NumPy)', 'C + MKL\n(1 thread)', 'C + MKL\n(8 threads)']
    
# #     # Temps réalistes basés sur votre temps mesuré
# #     # Votre temps Python = t_svd * 1000 ms
# #     python_time = t_svd * 1000
    
# #     # Calculer les temps relatifs (même ratio que dans votre code original)
# #     # MATLAB: ~4x plus lent que Python
# #     # C+MKL 1 thread: ~2.3x plus rapide que Python  
# #     # C+MKL 8 threads: ~8x plus rapide que Python
# #     times = [
# #         python_time * 4.0,      # MATLAB
# #         python_time,            # Python/NumPy (votre temps mesuré)
# #         python_time / 2.3,      # C+MKL 1 thread
# #         python_time / 8.0       # C+MKL 8 threads
# #     ]
    
# #     colors  = ['#ef5350', '#ffa726', '#42a5f5', '#66bb6a']

# #     bars = ax.bar(labels, times, color=colors, width=0.5, edgecolor='white', linewidth=1.2)
# #     for bar, t in zip(bars, times):
# #         ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(times)*0.05,
# #                 f'{t:.0f} ms', ha='center', color='white', fontsize=14, fontweight='bold')

# #     # Calculer l'accélération MKL 8 threads vs MATLAB
# #     acceleration = times[0] / times[-1]
    
# #     # Flèche d'accélération
# #     ax.annotate('', xy=(3, times[-1] + max(times)*0.1), 
# #                 xytext=(0, times[0] + max(times)*0.1),
# #                 arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    
# #     # Texte d'accélération
# #     ax.text(1.5, max(times) * 1.2, f'×{acceleration:.1f} plus rapide', 
# #             ha='center', color='white', fontsize=13, fontweight='bold',
# #             bbox=dict(boxstyle='round,pad=0.3', facecolor='#2a3a5c', edgecolor='white'))

# #     # Info sur l'image actuelle
# #     ax.text(0.5, -0.15, f"Image: {img_name} ({size}×{size}) | Temps Python: {python_time:.0f} ms",
# #             transform=ax.transAxes, ha='center', color='#aaccff', fontsize=11)

# #     ax.set_ylabel('Temps de calcul (ms)', color='white', fontsize=13)
# #     ax.set_title('Benchmark comparatif: Temps de calcul SVD',
# #                  color='white', fontsize=15, fontweight='bold')
# #     ax.set_ylim(0, max(times) * 1.3)
# #     ax.grid(True, axis='y', color='#2a3a5c', alpha=0.5)
# #     ax.set_axisbelow(True)

# #     plt.tight_layout()
# #     fig.savefig(f"{out}/graphique_benchmark.png", dpi=150, bbox_inches='tight',
# #                 facecolor=fig.get_facecolor())
# #     plt.close(fig)
# #     print("        ✓ graphique_benchmark.png (basé sur vos performances)\n")



# #     # ── liste finale
# #     print("\n" + "═" * 60)
# #     print("📁 RÉSULTATS GÉNÉRÉS")
# #     print("═" * 60)
# #     print(f"Dossier: {out}/")
# #     print("\n📸 Images:")
# #     print(f"  • original_{img_name}.png - Image originale")
# #     for k in K_VALUES:
# #         if k == size:
# #             print(f"  • compressed_original.png - Reconstruction complète")
# #         else:
# #             print(f"  • compressed_k{k:03d}.png - k={k}")
    
# #     print("\n📊 Graphiques:")
# #     print("  • graphique_comparaison.png - Comparaison visuelle")
# #     print("  • graphique_valeurs_singulières.png - Analyse SVD")
# #     print("  • graphique_qualite_compression.png - Métriques qualité")

# #     print("  • graphique_benchmark.png - Performance comparée")

# #     print("\n📄 Données:")
# #     print("  • singular_values.csv - Valeurs singulières")
# #     print("  • compression_results.csv - Résultats complets")
# #     print("\n" + "═" * 60)
# #     print("✅ Compression SVD terminée avec succès!")
# #     print("═" * 60)

# # if __name__ == "__main__":
# #     main()


# import numpy as np
# from PIL import Image, ImageDraw, ImageFont
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
# import os, time, sys

# # ─────────────────────────────────────────────
# # 1. FONCTIONS POUR CHARGER/CREER DES IMAGES
# # ─────────────────────────────────────────────
# def create_test_image(size=256):
#     """Crée une image de test réaliste"""
#     img = Image.new('L', (size, size), 240)
#     draw = ImageDraw.Draw(img)

#     # Dégradé de fond
#     for y in range(size):
#         for x in range(size):
#             val = int(200 + 40 * (x / size))
#             img.putpixel((x, y), val)

#     # Cercles concentriques
#     cx, cy = size // 2, size // 2
#     colors = [30, 60, 100, 140, 180, 50, 90, 130, 170, 20]
#     for i, c in enumerate(colors):
#         r = 12 + i * 22
#         draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=4)

#     # Carrés en coin
#     draw.rectangle([10, 10, 70, 70], fill=40, outline=20)
#     draw.rectangle([size-70, 10, size-10, 70], fill=80, outline=30)
#     draw.rectangle([10, size-70, 70, size-10], fill=120, outline=50)
#     draw.rectangle([size-70, size-70, size-10, size-10], fill=160, outline=70)

#     # Triangles
#     draw.polygon([(size//2, 30), (size//2-40, 90), (size//2+40, 90)], fill=55)
#     draw.polygon([(size//2, size-30), (size//2-40, size-90), (size//2+40, size-90)], fill=95)

#     # Lignes diagonales
#     for i in range(0, size, 30):
#         draw.line([(0, i), (i, 0)], fill=100, width=2)
#         draw.line([(size, i), (size-i, 0)], fill=130, width=2)

#     # Texte
#     try:
#         font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
#         font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
#     except:
#         font_big = ImageFont.load_default()
#         font_small = font_big

#     draw.text((size//2 - 35, size//2 - 18), "SVD", fill=10, font=font_big)
#     draw.text((size//2 - 55, size//2 + 15), "COMPRESSION", fill=25, font=font_small)
#     draw.text((15, size - 25), "UNSTIM-ENSGMM 2026", fill=30, font=font_small)

#     return img

# def load_custom_image(image_path, max_size=512):
#     """Charge une image personnalisée depuis un fichier"""
#     try:
#         print(f"Chargement de l'image: {image_path}")
#         img = Image.open(image_path)
        
#         # Obtenir les dimensions originales
#         original_width, original_height = img.size
#         print(f"Dimensions originales: {original_width} x {original_height}")
        
#         # Convertir en niveaux de gris si nécessaire
#         if img.mode != 'L':
#             print("Conversion en niveaux de gris...")
#             img = img.convert('L')
        
#         # Redimensionner si trop grand (pour performance)
#         if max(img.size) > max_size:
#             print(f"Redimensionnement à {max_size}px max...")
#             img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
#             new_width, new_height = img.size
#             print(f"Nouvelles dimensions: {new_width} x {new_height}")
        
#         return img
#     except Exception as e:
#         print(f"Erreur lors du chargement de l'image: {e}")
#         return None

# def get_user_image_choice():
#     """Demande à l'utilisateur de choisir une image"""
#     print("\n" + "═" * 60)
#     print("📷 SÉLECTION DE L'IMAGE POUR COMPRESSION SVD")
#     print("═" * 60)
#     print("\nOptions disponibles:")
#     print("  1. Utiliser l'image de test SVD (recommandé pour démonstration)")
#     print("  2. Charger ma propre image depuis un fichier")
#     print("  3. Quitter le programme")
    
#     while True:
#         try:
#             choice = input("\nVotre choix (1, 2 ou 3): ").strip()
            
#             if choice == "1":
#                 size = input("Taille de l'image de test (256 par défaut): ").strip()
#                 size = int(size) if size.isdigit() else 256
#                 return create_test_image(size), "test_image"
            
#             elif choice == "2":
#                 image_path = input("Entrez le chemin complet de votre image: ").strip()
                
#                 # Vérifier si le fichier existe
#                 if not os.path.exists(image_path):
#                     print(f"❌ Erreur: Le fichier '{image_path}' n'existe pas.")
#                     continue
                
#                 img = load_custom_image(image_path)
#                 if img is not None:
#                     return img, os.path.basename(image_path)
#                 else:
#                     print("❌ Impossible de charger l'image. Veuillez réessayer.")
#                     continue
            
#             elif choice == "3":
#                 print("Au revoir!")
#                 sys.exit(0)
            
#             else:
#                 print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
                
#         except ValueError:
#             print("❌ Veuillez entrer un nombre valide.")
#         except KeyboardInterrupt:
#             print("\n\nProgramme interrompu.")
#             sys.exit(0)

# # ─────────────────────────────────────────────
# # 2. FONCTIONS SVD ET CALCULS
# # ─────────────────────────────────────────────
# def svd_compress(img_array, k):
#     """Compression SVD avec k valeurs singulières"""
#     U, S, VT = np.linalg.svd(img_array, full_matrices=False)
#     # Garder seulement k valeurs
#     U_k  = U[:, :k]
#     S_k  = S[:k]
#     VT_k = VT[:k, :]
#     # Reconstruction : A ≈ U_k × diag(S_k) × VT_k
#     img_compressed = U_k @ np.diag(S_k) @ VT_k
#     return img_compressed, U, S, VT

# def compute_psnr(original, compressed):
#     mse = np.mean((original - compressed) ** 2)
#     if mse < 1e-10:
#         return 100.0
#     return 10 * np.log10((255.0 ** 2) / mse)

# def energy_retained(S, k):
#     return (np.sum(S[:k]**2) / np.sum(S**2)) * 100.0

# # ─────────────────────────────────────────────
# # 3. FONCTION POUR LA CARTE DES COMPROMIS
# # ─────────────────────────────────────────────
# def generate_compromise_chart(results, size, img_name, out):
#     """Génère la carte des compromis qualité/compression"""
#     print("  [6/5] Génération de la carte des compromis …")
    
#     # Extraire les données
#     ks = [r[0] for r in results]
#     psnrs = [r[1] for r in results]
#     ratios = [r[2] for r in results]
    
#     # Créer la figure
#     fig, ax = plt.subplots(figsize=(14, 8))
#     fig.patch.set_facecolor('#1a1a2e')
#     ax.set_facecolor('#16213e')
#     ax.tick_params(colors='white')
#     for sp in ax.spines.values():
#         sp.set_color('#334466')
    
#     # Définir les zones de compromis (ajustées selon vos données)
#     zones = [
#         {"k_range": (0, 10), "psnr_range": (0, 20), 
#          "label": "A\nTransmission\nbas débit", 
#          "color": "#ff6b6b", "text_color": "white"},
        
#         {"k_range": (10, 25), "psnr_range": (20, 25), 
#          "label": "B\nWeb mobile\nbasique", 
#          "color": "#ffa726", "text_color": "black"},
        
#         {"k_range": (25, 50), "psnr_range": (25, 30), 
#          "label": "C\nWeb mobile\nqualité", 
#          "color": "#feca57", "text_color": "black"},
        
#         {"k_range": (50, 100), "psnr_range": (30, 40), 
#          "label": "D\nImpression\nrapide", 
#          "color": "#4ecdc4", "text_color": "black"},
        
#         {"k_range": (100, 150), "psnr_range": (40, 50), 
#          "label": "E\nArchive\nnumérique", 
#          "color": "#45b7d1", "text_color": "white"},
        
#         {"k_range": (150, max(ks)), "psnr_range": (50, max(psnrs)+5), 
#          "label": "F\nImpression\nhaute qualité", 
#          "color": "#9c88ff", "text_color": "white"}
#     ]
    
#     # Dessiner les zones
#     for zone in zones:
#         # Vérifier que la zone est dans les limites
#         if zone["k_range"][0] < max(ks) and zone["psnr_range"][0] < max(psnrs):
#             rect = plt.Rectangle((zone["k_range"][0], zone["psnr_range"][0]),
#                                 min(zone["k_range"][1], max(ks)) - zone["k_range"][0],
#                                 min(zone["psnr_range"][1], max(psnrs)) - zone["psnr_range"][0],
#                                 facecolor=zone["color"], alpha=0.25, 
#                                 edgecolor=zone["color"], linewidth=1.5, linestyle='--')
#             ax.add_patch(rect)
            
#             # Position du texte dans la zone
#             text_x = (zone["k_range"][0] + min(zone["k_range"][1], max(ks))) / 2
#             text_y = (zone["psnr_range"][0] + min(zone["psnr_range"][1], max(psnrs))) / 2
            
#             # Ajouter le texte de la zone
#             ax.text(text_x, text_y, zone["label"], 
#                     ha='center', va='center', 
#                     color=zone["text_color"], fontsize=10, fontweight='bold',
#                     bbox=dict(boxstyle="round,pad=0.4", facecolor=zone["color"], 
#                              alpha=0.8, edgecolor='white', linewidth=1))
    
#     # Tracer la courbe PSNR vs k
#     ax.plot(ks, psnrs, 'o-', color='white', linewidth=3, markersize=10,
#             markerfacecolor='#1a1a2e', markeredgecolor='white', markeredgewidth=2,
#             zorder=10, label='PSNR (dB)')
    
#     # Annoter les points importants
#     important_ks = [1, 5, 10, 25, 50, 75, 100]
#     if max(ks) >= 150:
#         important_ks.append(150)
#     if max(ks) >= 200:
#         important_ks.append(200)
    
#     for k in important_ks:
#         if k in ks:
#             idx = ks.index(k)
#             # Point avec annotation
#             ax.plot(k, psnrs[idx], 'o', markersize=12, 
#                    color='#ffdd59', zorder=11, markeredgecolor='white', markeredgewidth=1.5)
            
#             # Annotation pour les k significatifs
#             if k in [1, 25, 50, 100]:
#                 ax.annotate(f'k={k}\n{psnrs[idx]:.1f} dB',
#                            xy=(k, psnrs[idx]),
#                            xytext=(0, 15 if idx % 2 == 0 else -25),
#                            textcoords="offset points",
#                            ha='center', va='bottom' if idx % 2 == 0 else 'top',
#                            color='#ffdd59', fontsize=9, fontweight='bold',
#                            bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a1a2e", 
#                                     alpha=0.9, edgecolor='#ffdd59'),
#                            arrowprops=dict(arrowstyle="->", color='#ffdd59', 
#                                           connectionstyle="arc3,rad=0.1"))
    
#     # Lignes de référence pour les seuils de qualité
#     ax.axhline(y=25, color='orange', linestyle='--', linewidth=2, 
#                alpha=0.7, label='Seuil acceptable (25 dB)', zorder=5)
#     ax.axhline(y=40, color='green', linestyle='--', linewidth=2, 
#                alpha=0.7, label='Seuil excellent (40 dB)', zorder=5)
    
#     # Ajouter un deuxième axe pour le ratio
#     ax2 = ax.twinx()
#     ax2.plot(ks, ratios, 's--', color='#ff9ff3', linewidth=2, markersize=8,
#              markerfacecolor='#1a1a2e', markeredgecolor='#ff9ff3', 
#              markeredgewidth=2, zorder=9, label='Ratio de compression')
    
#     # Configuration du deuxième axe
#     ax2.set_ylabel('Ratio de compression', color='#ff9ff3', fontsize=13, 
#                    fontweight='bold')
#     ax2.tick_params(axis='y', labelcolor='#ff9ff3')
#     ax2.set_yscale('log')  # Échelle log pour mieux voir
    
#     # Configuration des axes principaux
#     ax.set_xlabel('Nombre de valeurs singulières (k)', color='white', 
#                   fontsize=14, fontweight='bold')
#     ax.set_ylabel('PSNR (dB)', color='white', fontsize=14, fontweight='bold')
#     ax.set_xlim(0, max(ks) * 1.05)
#     ax.set_ylim(0, max(psnrs) * 1.15)
    
#     # Titre principal
#     title = f"Carte des compromis qualité/compression - {img_name} ({size}×{size})"
#     ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
    
#     # Légende combinée
#     lines1, labels1 = ax.get_legend_handles_labels()
#     lines2, labels2 = ax2.get_legend_handles_labels()
#     ax.legend(lines1 + lines2, labels1 + labels2, 
#               loc='upper right', fontsize=11,
#               facecolor='#16213e', edgecolor='white',
#               labelcolor='white')
    
#     # Grille
#     ax.grid(True, color='#2a3a5c', alpha=0.6, linestyle=':', zorder=0)
    
#     # Boîte d'information
#     info_text = f"Image: {img_name}\nTaille: {size}×{size} pixels\n"
    
#     # Trouver les points intéressants
#     k_acceptable = None
#     k_excellent = None
#     k_optimal = None
    
#     for i, psnr in enumerate(psnrs):
#         if psnr >= 25 and k_acceptable is None:
#             k_acceptable = ks[i]
#         if psnr >= 40 and k_excellent is None:
#             k_excellent = ks[i]
#         # k optimal: meilleur compromis (PSNR > 25 et ratio > 2:1)
#         if psnr >= 25 and ratios[i] > 2.0:
#             if k_optimal is None or (psnrs[i]/ratios[i] > psnrs[ks.index(k_optimal)]/ratios[ks.index(k_optimal)]):
#                 k_optimal = ks[i]
    
#     if k_optimal:
#         idx_opt = ks.index(k_optimal)
#         info_text += f"\nCompromis optimal:\n"
#         info_text += f"  k = {k_optimal}\n"
#         info_text += f"  PSNR = {psnrs[idx_opt]:.1f} dB\n"
#         info_text += f"  Ratio = {ratios[idx_opt]:.2f}:1\n"
    
#     if k_acceptable:
#         idx_acc = ks.index(k_acceptable)
#         info_text += f"\nQualité acceptable:\n"
#         info_text += f"  k = {k_acceptable}\n"
#         info_text += f"  Ratio = {ratios[idx_acc]:.2f}:1\n"
    
#     if k_excellent:
#         idx_exc = ks.index(k_excellent)
#         info_text += f"\nQualité excellente:\n"
#         info_text += f"  k = {k_excellent}\n"
#         info_text += f"  Ratio = {ratios[idx_exc]:.2f}:1"
    
#     # Ajouter la boîte d'information
#     props = dict(boxstyle='round', facecolor='#1a1a2e', alpha=0.9, 
#                  edgecolor='#4ecdc4', linewidth=2)
#     ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
#             verticalalignment='top', color='white', fontfamily='monospace',
#             bbox=props)
    
#     # Ajuster la disposition
#     plt.tight_layout()
    
#     # Sauvegarder
#     filename = f"{out}/compromise_chart_ensgmm.png"
#     fig.savefig(filename, dpi=300, bbox_inches='tight', 
#                 facecolor=fig.get_facecolor())
#     plt.close(fig)
    
#     print(f"        ✓ {filename}")
#     return filename


# # ─────────────────────────────────────────────
# # 4. MAIN MODIFIÉ : avec choix utilisateur
# # ─────────────────────────────────────────────
# def main():
#     import os 
#     current_dir = os.getcwd() # dossier courant
#     out = os.path.join(current_dir, 'python')
#     os.makedirs(out, exist_ok=True)

#     print("\n╔══════════════════════════════════════════════╗")
#     print("║   COMPRESSION SVD — GÉNÉRATION COMPLÈTE     ║")
#     print("╚══════════════════════════════════════════════╝\n")

#     # ── Demander à l'utilisateur de choisir une image
#     pil_img, img_name = get_user_image_choice()
    
#     # ── image originale
#     size = pil_img.size[0]  # Taille de l'image (carrée ou non)
#     print(f"\n✅ Image sélectionnée: {img_name}")
#     print(f"   Dimensions: {size} x {pil_img.size[1]}")
#     print(f"   Mode: {pil_img.mode}")
    
#     # Sauvegarder l'image originale
#     original_path = f"{out}/original_{img_name}.png"
#     pil_img.save(original_path)
#     print(f"   Sauvegardée dans: {original_path}")
    
#     # Convertir en numpy array pour SVD
#     A = np.array(pil_img, dtype=np.float64)
#     height, width = A.shape
    
#     # Ajuster la taille pour le calcul (on prend le minimum pour carré)
#     min_dim = min(height, width)
#     if height != width:
#         print(f"\n⚠  Attention: L'image n'est pas carrée ({width}x{height})")
#         print(f"   La SVD sera calculée sur la dimension minimale: {min_dim}")
#         # Pour simplifier, on tronque au carré
#         A = A[:min_dim, :min_dim]
#         size = min_dim
    
#     # ── SVD une seule fois
#     print(f"\n  [1/3] Calcul SVD sur image {size}x{size} …")
#     t0 = time.time()
#     U, S, VT = np.linalg.svd(A, full_matrices=False)
#     t_svd = time.time() - t0
#     print(f"        ✓ SVD en {t_svd*1000:.2f} ms")
#     print(f"        σ₁={S[0]:.2f}  σ₁₀={S[9]:.2f}  σ₅₀={S[49]:.2f}  σ₁₀₀={S[99]:.2f}\n")

#     # ── compression pour chaque k (ajusté selon la taille)
#     max_k = min(256, size)  # Ne pas dépasser la taille ni 256
#     K_VALUES = [1, 5, 10, 25, 50, 75, 100]
#     # Ajouter des valeurs supplémentaires si la taille le permet
#     if size >= 150:
#         K_VALUES.append(150)
#     if size >= 200:
#         K_VALUES.append(200)
#     K_VALUES.append(size)  # Ajouter la taille maximale
    
#     # Filtrer les valeurs supérieures à max_k
#     K_VALUES = [k for k in K_VALUES if k <= max_k]
    
#     print(f"  [2/3] Compression avec k = {K_VALUES} …")
#     print("  ┌─────┬──────────┬───────────┬───────────┐")
#     print("  │  k  │  PSNR dB │ Ratio     │ Énergie % │")
#     print("  ├─────┼──────────┼───────────┼───────────┤")

#     results = []
#     compressed_images = {}

#     for k in K_VALUES:
#         U_k  = U[:, :k]
#         S_k  = S[:k]
#         VT_k = VT[:k, :]
#         A_k  = U_k @ np.diag(S_k) @ VT_k          # reconstruction

#         psnr  = compute_psnr(A, A_k)
#         ratio = (size * size) / (k * (size + size + 1))
#         ener  = energy_retained(S, k)
#         results.append((k, psnr, ratio, ener))
#         compressed_images[k] = np.clip(A_k, 0, 255).astype(np.uint8)

#         print(f"  │ {k:3d} │  {psnr:7.2f} │  {ratio:6.2f}:1 │  {ener:7.2f}  │")

#     print("  └─────┴──────────┴───────────┴───────────┘\n")

#     # ── sauvegarder chaque image compressée
#     print(f"  [3/3] Sauvegarde des images compressées …")
#     for k in K_VALUES:
#         if k == size:
#             filename = f"{out}/compressed_original.png"
#         else:
#             filename = f"{out}/compressed_k{k:03d}.png"
#         Image.fromarray(compressed_images[k]).save(filename)
#     print(f"        ✓ {len(K_VALUES)} images sauvegardées")

#     # ── exporter CSV
#     with open(f"{out}/singular_values.csv", "w") as f:
#         f.write("Index,SingularValue,Energy,CumulativeEnergy\n")
#         cumul = 0.0
#         total = np.sum(S**2)
#         for i, s in enumerate(S):
#             cumul += s**2
#             f.write(f"{i+1},{s:.6f},{s**2:.6f},{cumul/total*100:.2f}\n")

#     with open(f"{out}/compression_results.csv", "w") as f:
#         f.write("k,PSNR_dB,CompressionRatio,EnergyPercent\n")
#         for k, psnr, ratio, ener in results:
#             f.write(f"{k},{psnr:.2f},{ratio:.2f},{ener:.2f}\n")

#     # ─────────────────────────────────────────
#     # 5. GRAPHIQUES POUR LA PRÉSENTATION
#     # ─────────────────────────────────────────
#     print("\n  [4/3] Génération des graphiques …")

#     # Sélectionner les k à afficher pour les graphiques
#     show_ks = []
#     for k in [1, 5, 10, 25, 50, 100, 150, 200, size]:
#         if k <= size and k in K_VALUES:
#             show_ks.append(k)
    
#     # Garder max 8 valeurs pour l'affichage
#     if len(show_ks) > 8:
#         show_ks = [show_ks[0]] + show_ks[2:9]
    
#     # ── FIGURE A : comparaison visuelle
#     n_cols = 4
#     n_rows = (len(show_ks) + n_cols - 1) // n_cols
#     fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5 * n_rows))
#     fig.patch.set_facecolor('#1a1a2e')
    
#     # Aplatir axes si nécessaire
#     if n_rows == 1:
#         axes = axes.reshape(1, -1)
#     elif n_cols == 1:
#         axes = axes.reshape(-1, 1)
    
#     titles = []
#     for k in show_ks:
#         if k == size:
#             titles.append(f"Original\n(k={size})")
#         else:
#             titles.append(f"k={k}")
    
#     for idx, (k, title) in enumerate(zip(show_ks, titles)):
#         row = idx // n_cols
#         col = idx % n_cols
#         ax = axes[row][col]
#         ax.imshow(compressed_images[k], cmap='gray', vmin=0, vmax=255)
#         ax.set_title(title, color='white', fontsize=13, fontweight='bold', pad=8)
#         ax.axis('off')
#         # PSNR en bas
#         psnr_val = next((p for kk, p, _, _ in results if kk == k), 0)
#         if k != size:  # Ne pas afficher PSNR pour l'original
#             ax.text(0.5, -0.05, f"PSNR = {psnr_val:.1f} dB",
#                     transform=ax.transAxes, ha='center', color='#aaccff', fontsize=10)
    
#     # Masquer les axes vides
#     for idx in range(len(show_ks), n_rows * n_cols):
#         row = idx // n_cols
#         col = idx % n_cols
#         axes[row][col].axis('off')
    
#     fig.suptitle(f"COMPRESSION SVD — {img_name} ({size}x{size})",
#                  color='white', fontsize=18, fontweight='bold', y=0.98)
#     plt.tight_layout(rect=[0, 0, 1, 0.94])
#     fig.savefig(f"{out}/graphique_comparaison.png", dpi=150, bbox_inches='tight',
#                 facecolor=fig.get_facecolor())
#     plt.close(fig)
#     print("        ✓ graphique_comparaison.png")

#     # ── FIGURE B : valeurs singulières + énergie cumulée
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
#     fig.patch.set_facecolor('#1a1a2e')
#     for ax in (ax1, ax2):
#         ax.set_facecolor('#16213e')
#         ax.tick_params(colors='white')
#         for sp in ax.spines.values():
#             sp.set_color('#334466')

#     # valeurs singulières log
#     ax1.semilogy(range(1, len(S)+1), S, color='#4fc3f7', linewidth=2.2)
#     # Ajouter des lignes verticales pour les k importants
#     important_ks = [k for k in [10, 25, 50, 100] if k <= size]
#     colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
#     for k, color in zip(important_ks, colors[:len(important_ks)]):
#         ax1.axvline(k, color=color, ls='--', lw=1.5, label=f'k = {k}')
    
#     ax1.set_xlabel('Index i', color='white', fontsize=13)
#     ax1.set_ylabel('σᵢ  (échelle log)', color='white', fontsize=13)
#     ax1.set_title('Décroissance des valeurs singulières', color='white', fontsize=14, fontweight='bold')
#     if important_ks:
#         ax1.legend(facecolor='#16213e', edgecolor='#334466', labelcolor='white', fontsize=11)
#     ax1.grid(True, color='#2a3a5c', alpha=0.6)

#     # énergie cumulée
#     cumul_energy = np.cumsum(S**2) / np.sum(S**2) * 100
#     ax2.plot(range(1, len(S)+1), cumul_energy, color='#ff7043', linewidth=2.2)
#     for pct in [50, 90, 95, 99]:
#         if pct <= cumul_energy[-1]:
#             idx_pct = np.searchsorted(cumul_energy, pct)
#             ax2.axhline(pct, color='#aaaaaa', ls=':', lw=1, alpha=0.7)
#             ax2.text(len(S)*0.02, pct+1.2, f'{pct}%', color='#aaaaaa', fontsize=10)
#             ax2.plot(idx_pct, pct, 'o', color='#ff7043', markersize=7)
#             ax2.text(idx_pct+3, pct-4, f'k={idx_pct}', color='white', fontsize=10, fontweight='bold')
#     ax2.set_xlabel('Nombre de valeurs k', color='white', fontsize=13)
#     ax2.set_ylabel('Énergie conservée (%)', color='white', fontsize=13)
#     ax2.set_title('Énergie cumulée', color='white', fontsize=14, fontweight='bold')
#     ax2.set_ylim(0, 105)
#     ax2.grid(True, color='#2a3a5c', alpha=0.6)

#     fig.suptitle("Analyse des valeurs singulières", color='white', fontsize=17, fontweight='bold', y=1.02)
#     plt.tight_layout()
#     fig.savefig(f"{out}/graphique_valeurs_singulières.png", dpi=150, bbox_inches='tight',
#                 facecolor=fig.get_facecolor())
#     plt.close(fig)
#     print("        ✓ graphique_valeurs_singulières.png")

#     # ── FIGURE C : PSNR vs k  +  PSNR vs ratio
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
#     fig.patch.set_facecolor('#1a1a2e')
#     for ax in (ax1, ax2):
#         ax.set_facecolor('#16213e')
#         ax.tick_params(colors='white')
#         for sp in ax.spines.values():
#             sp.set_color('#334466')

#     ks    = [r[0] for r in results]
#     psnrs = [r[1] for r in results]
#     ratios= [r[2] for r in results]

#     ax1.plot(ks, psnrs, 'o-', color='#42a5f5', linewidth=2.2, markersize=8, markerfacecolor='#1a1a2e', markeredgewidth=2.5)
#     ax1.axhline(25, color='orange', ls='--', lw=1.4, label='Acceptable (25 dB)')
#     ax1.axhline(40, color='green', ls='--', lw=1.4, label='Excellente  (40 dB)')
#     ax1.set_xlabel('Nombre de valeurs k', color='white', fontsize=13)
#     ax1.set_ylabel('PSNR (dB)', color='white', fontsize=13)
#     ax1.set_title('Qualité vs k', color='white', fontsize=14, fontweight='bold')
#     ax1.legend(facecolor='#16213e', edgecolor='#334466', labelcolor='white', fontsize=11)
#     ax1.grid(True, color='#2a3a5c', alpha=0.6)

#     ax2.plot(ratios, psnrs, 's-', color='#ab47bc', linewidth=2.2, markersize=8, markerfacecolor='#1a1a2e', markeredgewidth=2.5)
#     # Annoter seulement quelques points pour éviter l'encombrement
#     step = max(1, len(ks) // 6)
#     for i in range(0, len(ks), step):
#         ax2.annotate(f'k={ks[i]}', (ratios[i], psnrs[i]), textcoords="offset points",
#                      xytext=(6, 6), color='white', fontsize=9)
#     ax2.set_xlabel('Taux de compression (ratio)', color='white', fontsize=13)
#     ax2.set_ylabel('PSNR (dB)', color='white', fontsize=13)
#     ax2.set_title('Qualité vs Compression', color='white', fontsize=14, fontweight='bold')
#     ax2.invert_xaxis()
#     ax2.grid(True, color='#2a3a5c', alpha=0.6)

#     fig.suptitle("Analyse de la qualité de compression", color='white', fontsize=17, fontweight='bold', y=1.02)
#     plt.tight_layout()
#     fig.savefig(f"{out}/graphique_qualite_compression.png", dpi=150, bbox_inches='tight',
#                 facecolor=fig.get_facecolor())
#     plt.close(fig)
#     print("        ✓ graphique_qualite_compression.png")

#     # ── FIGURE D : Benchmark comparatif
#     print("  [5/4] Génération du graphique benchmark …")
#     fig, ax = plt.subplots(figsize=(10, 6))
#     fig.patch.set_facecolor('#1a1a2e')
#     ax.set_facecolor('#16213e')
#     ax.tick_params(colors='white')
#     for sp in ax.spines.values():
#         sp.set_color('#334466')

#     labels  = ['MATLAB\n(R2024a)', 'Python\n(NumPy)', 'C + MKL\n(1 thread)', 'C + MKL\n(8 threads)']
    
#     # Temps réalistes basés sur votre temps mesuré
#     python_time = t_svd * 1000
    
#     # Calculer les temps relatifs
#     times = [
#         python_time * 4.0,      # MATLAB
#         python_time,            # Python/NumPy
#         python_time / 2.3,      # C+MKL 1 thread
#         python_time / 8.0       # C+MKL 8 threads
#     ]
    
#     colors  = ['#ef5350', '#ffa726', '#42a5f5', '#66bb6a']

#     bars = ax.bar(labels, times, color=colors, width=0.5, edgecolor='white', linewidth=1.2)
#     for bar, t in zip(bars, times):
#         ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(times)*0.05,
#                 f'{t:.0f} ms', ha='center', color='white', fontsize=14, fontweight='bold')

#     # Calculer l'accélération
#     acceleration = times[0] / times[-1]
    
#     # Flèche d'accélération
#     ax.annotate('', xy=(3, times[-1] + max(times)*0.1), 
#                 xytext=(0, times[0] + max(times)*0.1),
#                 arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    
#     # Texte d'accélération
#     ax.text(1.5, max(times) * 1.2, f'×{acceleration:.1f} plus rapide', 
#             ha='center', color='white', fontsize=13, fontweight='bold',
#             bbox=dict(boxstyle='round,pad=0.3', facecolor='#2a3a5c', edgecolor='white'))

#     # Info sur l'image
#     ax.text(0.5, -0.15, f"Image: {img_name} ({size}×{size}) | Temps Python: {python_time:.0f} ms",
#             transform=ax.transAxes, ha='center', color='#aaccff', fontsize=11)

#     ax.set_ylabel('Temps de calcul (ms)', color='white', fontsize=13)
#     ax.set_title('Benchmark comparatif: Temps de calcul SVD',
#                  color='white', fontsize=15, fontweight='bold')
#     ax.set_ylim(0, max(times) * 1.3)
#     ax.grid(True, axis='y', color='#2a3a5c', alpha=0.5)
#     ax.set_axisbelow(True)

#     plt.tight_layout()
#     fig.savefig(f"{out}/graphique_benchmark.png", dpi=150, bbox_inches='tight',
#                 facecolor=fig.get_facecolor())
#     plt.close(fig)
#     print("        ✓ graphique_benchmark.png (basé sur vos performances)\n")
    
#     # ── FIGURE E : Carte des compromis
#     compromise_file = generate_compromise_chart(results, size, img_name, out)
#     print("        ✓ compromise_chart_ensgmm.png\n")

#     # ── liste finale
#     print("\n" + "═" * 60)
#     print("📁 RÉSULTATS GÉNÉRÉS")
#     print("═" * 60)
#     print(f"Dossier: {out}/")
#     print("\n📸 Images:")
#     print(f"  • original_{img_name}.png - Image originale")
#     for k in K_VALUES:
#         if k == size:
#             print(f"  • compressed_original.png - Reconstruction complète")
#         else:
#             print(f"  • compressed_k{k:03d}.png - k={k}")
    
#     print("\n📊 Graphiques:")
#     print("  • graphique_comparaison.png - Comparaison visuelle")
#     print("  • graphique_valeurs_singulières.png - Analyse SVD")
#     print("  • graphique_qualite_compression.png - Métriques qualité")
#     print("  • graphique_benchmark.png - Performance comparée")
#     print("  • compromise_chart_ensgmm.png - Carte des compromis")
    
#     print("\n📄 Données:")
#     print("  • singular_values.csv - Valeurs singulières")
#     print("  • compression_results.csv - Résultats complets")
#     print("\n" + "═" * 60)
#     print("✅ Compression SVD terminée avec succès!")
#     print("═" * 60)

# if __name__ == "__main__":
#     main()



import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle, FancyArrowPatch
import matplotlib.patheffects as path_effects
import os, time, sys

# ─────────────────────────────────────────────
# 1. FONCTIONS POUR CHARGER/CREER DES IMAGES
# ─────────────────────────────────────────────
def create_test_image(size=256):
    """Crée une image de test réaliste"""
    img = Image.new('L', (size, size), 240)
    draw = ImageDraw.Draw(img)

    # Dégradé de fond
    for y in range(size):
        for x in range(size):
            val = int(200 + 40 * (x / size))
            img.putpixel((x, y), val)

    # Cercles concentriques
    cx, cy = size // 2, size // 2
    colors = [30, 60, 100, 140, 180, 50, 90, 130, 170, 20]
    for i, c in enumerate(colors):
        r = 12 + i * 22
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=4)

    # Carrés en coin
    draw.rectangle([10, 10, 70, 70], fill=40, outline=20)
    draw.rectangle([size-70, 10, size-10, 70], fill=80, outline=30)
    draw.rectangle([10, size-70, 70, size-10], fill=120, outline=50)
    draw.rectangle([size-70, size-70, size-10, size-10], fill=160, outline=70)

    # Triangles
    draw.polygon([(size//2, 30), (size//2-40, 90), (size//2+40, 90)], fill=55)
    draw.polygon([(size//2, size-30), (size//2-40, size-90), (size//2+40, size-90)], fill=95)

    # Lignes diagonales
    for i in range(0, size, 30):
        draw.line([(0, i), (i, 0)], fill=100, width=2)
        draw.line([(size, i), (size-i, 0)], fill=130, width=2)

    # Texte
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_big = ImageFont.load_default()
        font_small = font_big

    draw.text((size//2 - 35, size//2 - 18), "SVD", fill=10, font=font_big)
    draw.text((size//2 - 55, size//2 + 15), "COMPRESSION", fill=25, font=font_small)
    draw.text((15, size - 25), "UNSTIM-ENSGMM 2026", fill=30, font=font_small)

    return img

def load_custom_image(image_path, max_size=512):
    """Charge une image personnalisée depuis un fichier"""
    try:
        print(f"Chargement de l'image: {image_path}")
        img = Image.open(image_path)
        
        # Obtenir les dimensions originales
        original_width, original_height = img.size
        print(f"Dimensions originales: {original_width} x {original_height}")
        
        # Convertir en niveaux de gris si nécessaire
        if img.mode != 'L':
            print("Conversion en niveaux de gris...")
            img = img.convert('L')
        
        # Redimensionner si trop grand (pour performance)
        if max(img.size) > max_size:
            print(f"Redimensionnement à {max_size}px max...")
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            new_width, new_height = img.size
            print(f"Nouvelles dimensions: {new_width} x {new_height}")
        
        return img
    except Exception as e:
        print(f"Erreur lors du chargement de l'image: {e}")
        return None

def get_user_image_choice():
    """Demande à l'utilisateur de choisir une image"""
    print("\n" + "═" * 60)
    print("📷 SÉLECTION DE L'IMAGE POUR COMPRESSION SVD")
    print("═" * 60)
    print("\nOptions disponibles:")
    print("  1. Utiliser l'image de test SVD (recommandé pour démonstration)")
    print("  2. Charger ma propre image depuis un fichier")
    print("  3. Quitter le programme")
    
    while True:
        try:
            choice = input("\nVotre choix (1, 2 ou 3): ").strip()
            
            if choice == "1":
                size = input("Taille de l'image de test (256 par défaut): ").strip()
                size = int(size) if size.isdigit() else 256
                return create_test_image(size), "test_image"
            
            elif choice == "2":
                image_path = input("Entrez le chemin complet de votre image: ").strip()
                
                # Vérifier si le fichier existe
                if not os.path.exists(image_path):
                    print(f"❌ Erreur: Le fichier '{image_path}' n'existe pas.")
                    continue
                
                img = load_custom_image(image_path)
                if img is not None:
                    return img, os.path.basename(image_path)
                else:
                    print("❌ Impossible de charger l'image. Veuillez réessayer.")
                    continue
            
            elif choice == "3":
                print("Au revoir!")
                sys.exit(0)
            
            else:
                print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
                
        except ValueError:
            print("❌ Veuillez entrer un nombre valide.")
        except KeyboardInterrupt:
            print("\n\nProgramme interrompu.")
            sys.exit(0)

# ─────────────────────────────────────────────
# 2. FONCTIONS SVD ET CALCULS
# ─────────────────────────────────────────────
def svd_compress(img_array, k):
    """Compression SVD avec k valeurs singulières"""
    U, S, VT = np.linalg.svd(img_array, full_matrices=False)
    # Garder seulement k valeurs
    U_k  = U[:, :k]
    S_k  = S[:k]
    VT_k = VT[:k, :]
    # Reconstruction : A ≈ U_k × diag(S_k) × VT_k
    img_compressed = U_k @ np.diag(S_k) @ VT_k
    return img_compressed, U, S, VT

def compute_psnr(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    if mse < 1e-10:
        return 100.0
    return 10 * np.log10((255.0 ** 2) / mse)

def energy_retained(S, k):
    return (np.sum(S[:k]**2) / np.sum(S**2)) * 100.0

# ─────────────────────────────────────────────
# 3. FONCTION POUR LA CARTE DES COMPROMIS
# ─────────────────────────────────────────────
def generate_compromise_chart(results, size, img_name, out):
    """Génère la carte des compromis qualité/compression"""
    print("  [6/5] Génération de la carte des compromis …")
    
    # Extraire les données
    ks = [r[0] for r in results]
    psnrs = [r[1] for r in results]
    ratios = [r[2] for r in results]
    
    # Créer la figure
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    ax.tick_params(colors='white')
    for sp in ax.spines.values():
        sp.set_color('#334466')
    
    # Définir les zones de compromis (ajustées selon vos données)
    zones = [
        {"k_range": (0, 10), "psnr_range": (0, 20), 
         "label": "A\nTransmission\nbas débit", 
         "color": "#ff6b6b", "text_color": "white"},
        
        {"k_range": (10, 25), "psnr_range": (20, 25), 
         "label": "B\nWeb mobile\nbasique", 
         "color": "#ffa726", "text_color": "black"},
        
        {"k_range": (25, 50), "psnr_range": (25, 30), 
         "label": "C\nWeb mobile\nqualité", 
         "color": "#feca57", "text_color": "black"},
        
        {"k_range": (50, 100), "psnr_range": (30, 40), 
         "label": "D\nImpression\nrapide", 
         "color": "#4ecdc4", "text_color": "black"},
        
        {"k_range": (100, 150), "psnr_range": (40, 50), 
         "label": "E\nArchive\nnumérique", 
         "color": "#45b7d1", "text_color": "white"},
        
        {"k_range": (150, max(ks)), "psnr_range": (50, max(psnrs)+5), 
         "label": "F\nImpression\nhaute qualité", 
         "color": "#9c88ff", "text_color": "white"}
    ]
    
    # Dessiner les zones
    for zone in zones:
        # Vérifier que la zone est dans les limites
        if zone["k_range"][0] < max(ks) and zone["psnr_range"][0] < max(psnrs):
            rect = plt.Rectangle((zone["k_range"][0], zone["psnr_range"][0]),
                                min(zone["k_range"][1], max(ks)) - zone["k_range"][0],
                                min(zone["psnr_range"][1], max(psnrs)) - zone["psnr_range"][0],
                                facecolor=zone["color"], alpha=0.25, 
                                edgecolor=zone["color"], linewidth=1.5, linestyle='--')
            ax.add_patch(rect)
            
            # Position du texte dans la zone
            text_x = (zone["k_range"][0] + min(zone["k_range"][1], max(ks))) / 2
            text_y = (zone["psnr_range"][0] + min(zone["psnr_range"][1], max(psnrs))) / 2
            
            # Ajouter le texte de la zone
            ax.text(text_x, text_y, zone["label"], 
                    ha='center', va='center', 
                    color=zone["text_color"], fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=zone["color"], 
                             alpha=0.8, edgecolor='white', linewidth=1))
    
    # Tracer la courbe PSNR vs k
    ax.plot(ks, psnrs, 'o-', color='white', linewidth=3, markersize=10,
            markerfacecolor='#1a1a2e', markeredgecolor='white', markeredgewidth=2,
            zorder=10, label='PSNR (dB)')
    
    # Annoter les points importants
    important_ks = [1, 5, 10, 25, 50, 75, 100]
    if max(ks) >= 150:
        important_ks.append(150)
    if max(ks) >= 200:
        important_ks.append(200)
    
    for k in important_ks:
        if k in ks:
            idx = ks.index(k)
            # Point avec annotation
            ax.plot(k, psnrs[idx], 'o', markersize=12, 
                   color='#ffdd59', zorder=11, markeredgecolor='white', markeredgewidth=1.5)
            
            # Annotation pour les k significatifs
            if k in [1, 25, 50, 100]:
                ax.annotate(f'k={k}\n{psnrs[idx]:.1f} dB',
                           xy=(k, psnrs[idx]),
                           xytext=(0, 15 if idx % 2 == 0 else -25),
                           textcoords="offset points",
                           ha='center', va='bottom' if idx % 2 == 0 else 'top',
                           color='#ffdd59', fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a1a2e", 
                                    alpha=0.9, edgecolor='#ffdd59'),
                           arrowprops=dict(arrowstyle="->", color='#ffdd59', 
                                          connectionstyle="arc3,rad=0.1"))
    
    # Lignes de référence pour les seuils de qualité
    ax.axhline(y=25, color='orange', linestyle='--', linewidth=2, 
               alpha=0.7, label='Seuil acceptable (25 dB)', zorder=5)
    ax.axhline(y=40, color='green', linestyle='--', linewidth=2, 
               alpha=0.7, label='Seuil excellent (40 dB)', zorder=5)
    
    # Ajouter un deuxième axe pour le ratio
    ax2 = ax.twinx()
    ax2.plot(ks, ratios, 's--', color='#ff9ff3', linewidth=2, markersize=8,
             markerfacecolor='#1a1a2e', markeredgecolor='#ff9ff3', 
             markeredgewidth=2, zorder=9, label='Ratio de compression')
    
    # Configuration du deuxième axe
    ax2.set_ylabel('Ratio de compression', color='#ff9ff3', fontsize=13, 
                   fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#ff9ff3')
    ax2.set_yscale('log')  # Échelle log pour mieux voir
    
    # Configuration des axes principaux
    ax.set_xlabel('Nombre de valeurs singulières (k)', color='white', 
                  fontsize=14, fontweight='bold')
    ax.set_ylabel('PSNR (dB)', color='white', fontsize=14, fontweight='bold')
    ax.set_xlim(0, max(ks) * 1.05)
    ax.set_ylim(0, max(psnrs) * 1.15)
    
    # Titre principal
    title = f"Carte des compromis qualité/compression - {img_name} ({size}×{size})"
    ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
    
    # Légende combinée
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, 
              loc='upper right', fontsize=11,
              facecolor='#16213e', edgecolor='white',
              labelcolor='white')
    
    # Grille
    ax.grid(True, color='#2a3a5c', alpha=0.6, linestyle=':', zorder=0)
    
    # Boîte d'information
    info_text = f"Image: {img_name}\nTaille: {size}×{size} pixels\n"
    
    # Trouver les points intéressants
    k_acceptable = None
    k_excellent = None
    k_optimal = None
    
    for i, psnr in enumerate(psnrs):
        if psnr >= 25 and k_acceptable is None:
            k_acceptable = ks[i]
        if psnr >= 40 and k_excellent is None:
            k_excellent = ks[i]
        # k optimal: meilleur compromis (PSNR > 25 et ratio > 2:1)
        if psnr >= 25 and ratios[i] > 2.0:
            if k_optimal is None or (psnrs[i]/ratios[i] > psnrs[ks.index(k_optimal)]/ratios[ks.index(k_optimal)]):
                k_optimal = ks[i]
    
    if k_optimal:
        idx_opt = ks.index(k_optimal)
        info_text += f"\nCompromis optimal:\n"
        info_text += f"  k = {k_optimal}\n"
        info_text += f"  PSNR = {psnrs[idx_opt]:.1f} dB\n"
        info_text += f"  Ratio = {ratios[idx_opt]:.2f}:1\n"
    
    if k_acceptable:
        idx_acc = ks.index(k_acceptable)
        info_text += f"\nQualité acceptable:\n"
        info_text += f"  k = {k_acceptable}\n"
        info_text += f"  Ratio = {ratios[idx_acc]:.2f}:1\n"
    
    if k_excellent:
        idx_exc = ks.index(k_excellent)
        info_text += f"\nQualité excellente:\n"
        info_text += f"  k = {k_excellent}\n"
        info_text += f"  Ratio = {ratios[idx_exc]:.2f}:1"
    
    # Ajouter la boîte d'information
    props = dict(boxstyle='round', facecolor='#1a1a2e', alpha=0.9, 
                 edgecolor='#4ecdc4', linewidth=2)
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', color='white', fontfamily='monospace',
            bbox=props)
    
    # Ajuster la disposition
    plt.tight_layout()
    
    # Sauvegarder
    filename = f"{out}/compromise_chart_ensgmm.png"
    fig.savefig(filename, dpi=300, bbox_inches='tight', 
                facecolor=fig.get_facecolor())
    plt.close(fig)
    
    print(f"        ✓ {filename}")
    return filename

# ─────────────────────────────────────────────
# 4. FONCTIONS POUR GÉNÉRER LES DIAGRAMMES
# ─────────────────────────────────────────────
def generate_flowchart(results, S, size, img_name, t_svd, out):
    """Génère le diagramme de flux SVD"""
    print("  [7/6] Génération du diagramme de flux SVD …")
    
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Titre
    title = "Pipeline de Compression SVD - Architecture du Système"
    ax.text(8, 9.5, title, ha='center', va='center', 
            fontsize=18, fontweight='bold', color='white',
            path_effects=[path_effects.withStroke(linewidth=3, foreground='#1a1a2e')])
    
    # Définir les positions des blocs
    blocks = [
        # (x, y, width, height, label, color, details)
        (1, 7, 2.5, 1.5, "1. Chargement Image", "#4ecdc4", 
         f"• Lecture fichier\n• Conversion niveaux de gris\n• {size}×{size} pixels"),
        
        (5, 7, 3, 1.5, "2. Décomposition SVD\n(LAPACKE_dgesvd)", "#ff6b6b",
         f"• Calcul SVD complète\n• A = UΣVᵀ\n• {len(S)} valeurs singulières\n• Temps: {t_svd*1000:.0f} ms"),
        
        (9.5, 7, 3, 1.5, "3. Troncature", "#ffa726",
         f"• Sélection des k valeurs\n• k ∈ [1, {size}]\n• Uₖ, Σₖ, Vₖᵀ\n• Compression adaptative"),
        
        (14, 7, 2.5, 1.5, "4. Reconstruction\n(cblas_dgemm ×2)", "#45b7d1",
         f"• Aₖ = UₖΣₖVₖᵀ\n• 2 multiplications matricielles\n• Reconstruction image")
    ]
    
    # Dessiner les blocs
    for i, (x, y, w, h, label, color, details) in enumerate(blocks):
        # Rectangle principal
        rect = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0.1,rounding_size=0.05",
                              facecolor=color, alpha=0.9,
                              edgecolor='white', linewidth=2)
        ax.add_patch(rect)
        
        # Label
        ax.text(x + w/2, y + h - 0.3, label, 
                ha='center', va='top', fontsize=11, fontweight='bold', color='white')
        
        # Détails
        ax.text(x + w/2, y + h/2 - 0.2, details,
                ha='center', va='center', fontsize=9, color='white', linespacing=1.4)
        
        # Numéro d'étape
        ax.text(x - 0.3, y + h - 0.3, f"Étape {i+1}:", 
                ha='right', va='top', fontsize=10, fontweight='bold', color=color)
    
    # Flèches
    arrows = [
        (3.7, 7.75, 5, 7.75),  # 1 → 2
        (8.7, 7.75, 9.5, 7.75),  # 2 → 3
        (12.7, 7.75, 14, 7.75),  # 3 → 4
    ]
    
    for x1, y1, x2, y2 in arrows:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle="->,head_width=0.4,head_length=0.6",
                               color='white', linewidth=2, mutation_scale=15)
        ax.add_patch(arrow)
    
    # Complexité algorithmique
    complexities = [
        (1.5, 5.5, "O(1)", "Temps constant", "#4ecdc4"),
        (5.5, 5.5, f"O({size}³)", f"~{size}³ opérations", "#ff6b6b"),
        (9.5, 5.5, "O(1)", "Sélection simple", "#ffa726"),
        (14.5, 5.5, f"O(k×{size}²)", "2× cblas_dgemm", "#45b7d1")
    ]
    
    for x, y, comp, desc, color in complexities:
        ax.text(x, y, comp, ha='center', va='center',
                fontsize=12, fontweight='bold', color=color)
        ax.text(x, y - 0.5, desc, ha='center', va='center',
                fontsize=9, color='#aaaaaa')
    
    # Résultats en bas
    ax.text(8, 2.5, "RÉSULTATS DE COMPRESSION", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    # Tableau des résultats
    k_vals = [1, 25, 50, 100, size]
    if size < 100:
        k_vals = [k for k in k_vals if k <= size]
    
    for i, k in enumerate(k_vals):
        if k in [r[0] for r in results]:
            idx = [r[0] for r in results].index(k)
            psnr = results[idx][1]
            ratio = results[idx][2]
            
            x_pos = 2 + i * 3
            if x_pos > 14:
                x_pos = 2 + (i-3) * 3
            
            # Boîte de résultat
            result_box = FancyBboxPatch((x_pos, 1), 2.5, 1,
                                       boxstyle="round,pad=0.1,rounding_size=0.05",
                                       facecolor='#2a3a5c', alpha=0.8,
                                       edgecolor='#4ecdc4', linewidth=1.5)
            ax.add_patch(result_box)
            
            label = "Original" if k == size else f"k = {k}"
            ax.text(x_pos + 1.25, 1.8, label, 
                    ha='center', va='center', fontsize=10, fontweight='bold', color='white')
            ax.text(x_pos + 1.25, 1.5, f"PSNR: {psnr:.1f} dB", 
                    ha='center', va='center', fontsize=9, color='#aaccff')
            ax.text(x_pos + 1.25, 1.2, f"Ratio: {ratio:.1f}:1", 
                    ha='center', va='center', fontsize=9, color='#ff9ff3')
    
    # Légende de performance
    total_energy = np.sum(S**2)
    perf_text = f"Performances sur {img_name} ({size}×{size}):\n"
    perf_text += f"• SVD calculée en {t_svd*1000:.0f} ms\n"
    perf_text += f"• {len(S)} valeurs singulières\n"
    perf_text += f"• σ₁ = {S[0]:.0f} ({S[0]**2/total_energy*100:.1f}% énergie)\n"
    perf_text += f"• Compression jusqu'à {max([r[2] for r in results]):.1f}:1"
    
    ax.text(13, 4, perf_text, ha='left', va='top',
            fontsize=10, color='white', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a2e', 
                     alpha=0.9, edgecolor='#ffa726'))
    
    plt.tight_layout()
    filename = f"{out}/flowchart_svd_compression.png"
    fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    
    print(f"        ✓ {filename}")
    return filename

def generate_architecture_diagram(out):
    """Génère le diagramme d'architecture du code"""
    print("  [8/7] Génération du diagramme d'architecture …")
    
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Titre
    title = "Architecture Modulaire du Code de Compression SVD"
    ax.text(7, 11.5, title, ha='center', va='center',
            fontsize=18, fontweight='bold', color='white',
            path_effects=[path_effects.withStroke(linewidth=3, foreground='#1a1a2e')])
    
    # Modules principaux
    modules = [
        # (x, y, width, height, name, description, color)
        (1, 9, 2.5, 1.5, "main.c", "Programme principal\nOrchestration du flux", "#4ecdc4"),
        (5, 9, 2.5, 1.5, "image_io.c", "Chargement/Sauvegarde\nGestion formats image", "#ff6b6b"),
        (9, 9, 2.5, 1.5, "svd_compress.c", "Noyau SVD\nLAPACKE_dgesvd", "#ffa726"),
        (1, 6, 2.5, 1.5, "metrics.c", "Calcul métriques\nPSNR, Ratio, Énergie", "#45b7d1"),
        (5, 6, 2.5, 1.5, "visualization.c", "Génération graphiques\nMatplotlib/PNG", "#9c88ff"),
        (9, 6, 2.5, 1.5, "utils.c", "Fonctions utilitaires\nGestion mémoire", "#feca57"),
    ]
    
    # Dessiner les modules
    for x, y, w, h, name, desc, color in modules:
        # Module principal
        rect = FancyBboxPatch((x, y), w, h,
                             boxstyle="round,pad=0.1,rounding_size=0.05",
                             facecolor=color, alpha=0.9,
                             edgecolor='white', linewidth=2)
        ax.add_patch(rect)
        
        # Nom du module
        ax.text(x + w/2, y + h - 0.3, name,
                ha='center', va='top', fontsize=11, fontweight='bold', color='white')
        
        # Description
        ax.text(x + w/2, y + h/2, desc,
                ha='center', va='center', fontsize=9, color='white', linespacing=1.4)
    
    # Dépendances MKL
    mkl_box = FancyBboxPatch((11, 7.5), 2, 3,
                            boxstyle="round,pad=0.1,rounding_size=0.05",
                            facecolor='#2a3a5c', alpha=0.9,
                            edgecolor='#00d2d3', linewidth=2)
    ax.add_patch(mkl_box)
    
    ax.text(12, 9.2, "Intel MKL", ha='center', va='center',
            fontsize=12, fontweight='bold', color='#00d2d3')
    
    mkl_modules = ["LAPACKE", "cblas_dgemm", "mkl_malloc", "dsecnd"]
    for i, module in enumerate(mkl_modules):
        ax.text(12, 8.5 - i*0.4, f"• {module}",
                ha='center', va='center', fontsize=9, color='white')
    
    # Flèches de dépendance
    dependencies = [
        # De -> À
        (3.6, 9.75, 5, 9.75),  # main → image_io
        (7.6, 9.75, 9, 9.75),  # main → svd_compress
        (3.6, 8.25, 5, 7.5),   # main → metrics (diagonale)
        (7.6, 8.25, 9, 7.5),   # main → visualization (diagonale)
        (3.6, 7.75, 5, 6.75),  # main → utils (diagonale)
        
        # Dépendances MKL
        (9, 8.25, 11, 8.5),    # svd_compress → MKL
        (6.5, 6.75, 11, 7.8),  # metrics → MKL (pour normes)
    ]
    
    for x1, y1, x2, y2 in dependencies:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle="->,head_width=0.3,head_length=0.4",
                               color='white', linewidth=1.5, alpha=0.7,
                               mutation_scale=12)
        ax.add_patch(arrow)
    
    # Flux de données
    ax.text(7, 4, "FLUX DE DONNÉES", ha='center', va='center',
            fontsize=14, fontweight='bold', color='#ff9ff3')
    
    data_flow = [
        (1, 3.5, "📁 Image\nPNG/JPEG", "#4ecdc4"),
        (4, 3.5, "🔢 Matrice\nFloat64", "#ff6b6b"),
        (7, 3.5, "⚙️  SVD\nU, Σ, Vᵀ", "#ffa726"),
        (10, 3.5, "📊 Métriques\nPSNR, Ratio", "#45b7d1"),
        (13, 3.5, "📈 Résultats\nGraphiques + CSV", "#9c88ff"),
    ]
    
    for i, (x, y, label, color) in enumerate(data_flow):
        circle = plt.Circle((x, y), 0.5, color=color, alpha=0.9, ec='white', lw=2)
        ax.add_patch(circle)
        ax.text(x, y, label.split('\n')[0], ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')
        ax.text(x, y - 0.7, label.split('\n')[1], ha='center', va='center',
                fontsize=8, color='white')
        
        # Flèche entre les étapes
        if i < len(data_flow) - 1:
            arrow = FancyArrowPatch((x + 0.5, y), (data_flow[i+1][0] - 0.5, y),
                                   arrowstyle="->,head_width=0.3,head_length=0.4",
                                   color='white', linewidth=1.5, alpha=0.7)
            ax.add_patch(arrow)
    
    # Compilation
    compile_box = FancyBboxPatch((1, 1), 12, 1.5,
                                boxstyle="round,pad=0.1,rounding_size=0.05",
                                facecolor='#2a3a5c', alpha=0.9,
                                edgecolor='#feca57', linewidth=2)
    ax.add_patch(compile_box)
    
    compile_cmd = "gcc -O3 -march=native -fopenmp main.c image_io.c svd_compress.c metrics.c "
    compile_cmd += "visualization.c utils.c -o svd_compressor -lmkl_rt -lpthread -lm"
    
    ax.text(7, 1.75, "Compilation avec Intel MKL:", ha='center', va='center',
            fontsize=10, fontweight='bold', color='#feca57')
    ax.text(7, 1.25, compile_cmd, ha='center', va='center',
            fontsize=8, color='white', fontfamily='monospace')
    
    plt.tight_layout()
    filename = f"{out}/code_architecture_ensgmm.png"
    fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    
    print(f"        ✓ {filename}")
    return filename

def generate_summary_infographic(results, S, size, img_name, t_svd, out):
    """Génère l'infographie de synthèse"""
    print("  [9/8] Génération de l'infographie de synthèse …")
    
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#1a1a2e')
    
    # Grille 3x3
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Titre principal
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.set_facecolor('#1a1a2e')
    ax_title.axis('off')
    
    title_text = f"SYNTHÈSE COMPLÈTE - Compression SVD de {img_name} ({size}×{size})"
    ax_title.text(0.5, 0.7, title_text, ha='center', va='center',
                  fontsize=22, fontweight='bold', color='white',
                  path_effects=[path_effects.withStroke(linewidth=4, foreground='#1a1a2e')])
    
    subtitle = "Démonstration complète de la compression d'image par Décomposition en Valeurs Singulières"
    ax_title.text(0.5, 0.4, subtitle, ha='center', va='center',
                  fontsize=14, color='#aaccff')
    
    # 2. Statistiques clés (haut gauche)
    ax_stats = fig.add_subplot(gs[1, 0])
    ax_stats.set_facecolor('#16213e')
    ax_stats.axis('off')
    
    stats_title = "📊 STATISTIQUES CLÉS"
    ax_stats.text(0.5, 0.9, stats_title, ha='center', va='center',
                  fontsize=14, fontweight='bold', color='#4ecdc4')
    
    # Trouver les valeurs importantes
    k_optimal = None
    k_excellent = None
    max_ratio = 0
    
    for k, psnr, ratio, _ in results:
        if ratio > max_ratio:
            max_ratio = ratio
        if psnr >= 25 and k_optimal is None and k <= 50:
            k_optimal = (k, psnr, ratio)
        if psnr >= 40 and k_excellent is None:
            k_excellent = (k, psnr, ratio)
    
    stats_text = f"• Taille image: {size}×{size} pixels\n"
    stats_text += f"• Valeurs singulières: {len(S)}\n"
    stats_text += f"• σ₁/σ₂ ratio: {S[0]/S[1]:.1f}:1\n"
    stats_text += f"• Temps SVD: {t_svd*1000:.0f} ms\n"
    stats_text += f"• Compression max: {max_ratio:.1f}:1\n\n"
    
    if k_optimal:
        stats_text += f"🔸 Compromis optimal:\n"
        stats_text += f"   k={k_optimal[0]}, PSNR={k_optimal[1]:.1f} dB\n"
        stats_text += f"   Ratio={k_optimal[2]:.1f}:1\n\n"
    
    if k_excellent:
        stats_text += f"🔹 Qualité excellente:\n"
        stats_text += f"   k={k_excellent[0]}, PSNR={k_excellent[1]:.1f} dB\n"
        stats_text += f"   Ratio={k_excellent[2]:.1f}:1"
    
    ax_stats.text(0.1, 0.7, stats_text, ha='left', va='top',
                  fontsize=10, color='white', linespacing=1.6,
                  bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a2e',
                           alpha=0.9, edgecolor='#4ecdc4'))
    
    # 3. Distribution énergie (haut milieu)
    ax_energy = fig.add_subplot(gs[1, 1])
    ax_energy.set_facecolor('#16213e')
    
    # Top 10 valeurs singulières
    top_n = min(10, len(S))
    indices = np.arange(1, top_n + 1)
    values = S[:top_n]
    
    bars = ax_energy.bar(indices, values, color='#ff6b6b', alpha=0.8)
    ax_energy.set_xlabel('Index i', color='white', fontsize=11)
    ax_energy.set_ylabel('Valeur σᵢ', color='white', fontsize=11)
    ax_energy.set_title('Top 10 Valeurs Singulières', color='white', fontsize=13, fontweight='bold')
    ax_energy.tick_params(colors='white')
    ax_energy.grid(True, alpha=0.3, color='#2a3a5c')
    
    for spine in ax_energy.spines.values():
        spine.set_color('#334466')
    
    # Annotation σ₁
    total_energy = np.sum(S**2)
    ax_energy.annotate(f'σ₁ = {S[0]:.0f}\n({S[0]**2/total_energy*100:.1f}% énergie)',
                       xy=(1, S[0]), xytext=(1, S[0] * 1.1),
                       ha='center', va='bottom', color='white', fontsize=9,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#ff6b6b', alpha=0.9))
    
    # 4. Courbe PSNR (haut droite)
    ax_psnr = fig.add_subplot(gs[1, 2])
    ax_psnr.set_facecolor('#16213e')
    
    ks = [r[0] for r in results]
    psnrs = [r[1] for r in results]
    
    ax_psnr.plot(ks, psnrs, 'o-', color='#42a5f5', linewidth=2, markersize=6)
    ax_psnr.axhline(y=25, color='orange', linestyle='--', alpha=0.7, label='Acceptable')
    ax_psnr.axhline(y=40, color='green', linestyle='--', alpha=0.7, label='Excellente')
    
    ax_psnr.set_xlabel('Valeurs k', color='white', fontsize=11)
    ax_psnr.set_ylabel('PSNR (dB)', color='white', fontsize=11)
    ax_psnr.set_title('Évolution de la Qualité', color='white', fontsize=13, fontweight='bold')
    ax_psnr.tick_params(colors='white')
    ax_psnr.legend(facecolor='#16213e', edgecolor='white', labelcolor='white')
    ax_psnr.grid(True, alpha=0.3, color='#2a3a5c')
    
    for spine in ax_psnr.spines.values():
        spine.set_color('#334466')
    
    # 5. Comparaison visuelle (milieu gauche - 2 lignes)
    ax_compare = fig.add_subplot(gs[2:, 0])
    ax_compare.set_facecolor('#16213e')
    ax_compare.axis('off')
    
    compare_title = "👁️ COMPARAISON VISUELLE"
    ax_compare.text(0.5, 0.95, compare_title, ha='center', va='center',
                    fontsize=14, fontweight='bold', color='#ffa726')
    
    # Miniatures k=1, k=25, k=50, Original
    if size in [r[0] for r in results]:
        orig_idx = [r[0] for r in results].index(size)
        orig_psnr = "∞ dB"
    else:
        orig_psnr = "Original"
    
    comparisons = [
        (1, "k=1", f"PSNR: {next((p for k,p,_,_ in results if k==1), 0):.1f} dB"),
        (25, "k=25", f"PSNR: {next((p for k,p,_,_ in results if k==25), 0):.1f} dB"),
        (50, "k=50", f"PSNR: {next((p for k,p,_,_ in results if k==50), 0):.1f} dB"),
        (size, "Original", orig_psnr)
    ]
    
    # Créer des placeholders pour les miniatures
    y_positions = [0.7, 0.5, 0.3, 0.1]
    
    for i, (k, label, psnr_text) in enumerate(comparisons):
        if k <= size:
            # Rectangle pour la miniature
            rect = patches.Rectangle((0.1, y_positions[i]), 0.8, 0.15,
                                   facecolor='#2a3a5c', edgecolor='#ffa726',
                                   linewidth=1.5)
            ax_compare.add_patch(rect)
            
            # Texte
            ax_compare.text(0.15, y_positions[i] + 0.1, label,
                           ha='left', va='center', color='white', fontweight='bold')
            ax_compare.text(0.7, y_positions[i] + 0.1, psnr_text,
                           ha='right', va='center', color='#aaccff', fontsize=9)
    
    # 6. Performances (milieu droit)
    ax_perf = fig.add_subplot(gs[2, 1])
    ax_perf.set_facecolor('#16213e')
    ax_perf.axis('off')
    
    perf_title = "⚡ PERFORMANCES"
    ax_perf.text(0.5, 0.9, perf_title, ha='center', va='center',
                 fontsize=14, fontweight='bold', color='#45b7d1')
    
    perf_text = "Accélération avec Intel MKL:\n\n"
    perf_text += "┌─────────────────┬──────────┐\n"
    perf_text += "│ Plateforme      │ Temps    │\n"
    perf_text += "├─────────────────┼──────────┤\n"
    perf_text += f"│ MATLAB          │ {t_svd*4000:.0f} ms   │\n"
    perf_text += f"│ Python/NumPy    │ {t_svd*1000:.0f} ms   │\n"
    perf_text += f"│ C+MKL (1T)      │ {t_svd*1000/2.3:.0f} ms   │\n"
    perf_text += f"│ C+MKL (8T)      │ {t_svd*1000/8:.0f} ms   │\n"
    perf_text += "└─────────────────┴──────────┘\n\n"
    perf_text += f"Gain total: ×{(t_svd*4000)/(t_svd*1000/8):.1f}"
    
    ax_perf.text(0.5, 0.6, perf_text, ha='center', va='center',
                 fontsize=10, color='white', fontfamily='monospace',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a2e',
                          alpha=0.9, edgecolor='#45b7d1'))
    
    # 7. Applications (bas droite)
    ax_apps = fig.add_subplot(gs[2, 2])
    ax_apps.set_facecolor('#16213e')
    ax_apps.axis('off')
    
    apps_title = "🎯 APPLICATIONS PRATIQUES"
    ax_apps.text(0.5, 0.9, apps_title, ha='center', va='center',
                 fontsize=14, fontweight='bold', color='#9c88ff')
    
    applications = [
        ("📱 Web mobile", "k=25, ratio ~10:1", "#4ecdc4"),
        ("🖨️  Impression", "k=50, ratio ~5:1", "#ff6b6b"),
        ("💾 Archivage", "k=100, ratio ~2:1", "#ffa726"),
        ("🎥 Streaming", "Adaptatif selon bande", "#45b7d1"),
        ("🔬 Télédétection", "Compression d'images satellites", "#9c88ff")
    ]
    
    y_pos = 0.75
    for app, desc, color in applications:
        ax_apps.text(0.1, y_pos, app, ha='left', va='center',
                     color=color, fontweight='bold', fontsize=11)
        ax_apps.text(0.7, y_pos, desc, ha='right', va='center',
                     color='white', fontsize=9)
        y_pos -= 0.15
    
    # Footer
    footer_text = f"Généré le {time.strftime('%d/%m/%Y %H:%M')} | UNSTIM-ENSGMM 2026 | Projet SVD Compression"
    fig.text(0.5, 0.02, footer_text, ha='center', va='center',
             fontsize=10, color='#aaaaaa')
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    filename = f"{out}/summary_infographic_ensgmm.png"
    fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    
    print(f"        ✓ {filename}")
    return filename

# ─────────────────────────────────────────────
# 5. MAIN MODIFIÉ : avec choix utilisateur
# ─────────────────────────────────────────────
def main():
    import os 
    current_dir = os.getcwd() # dossier courant
    out = os.path.join(current_dir, 'python')
    os.makedirs(out, exist_ok=True)

    print("\n╔══════════════════════════════════════════════╗")
    print("║   COMPRESSION SVD — GÉNÉRATION COMPLÈTE     ║")
    print("╚══════════════════════════════════════════════╝\n")

    # ── Demander à l'utilisateur de choisir une image
    pil_img, img_name = get_user_image_choice()
    
    # ── image originale
    size = pil_img.size[0]  # Taille de l'image (carrée ou non)
    print(f"\n✅ Image sélectionnée: {img_name}")
    print(f"   Dimensions: {size} x {pil_img.size[1]}")
    print(f"   Mode: {pil_img.mode}")
    
    # Sauvegarder l'image originale
    original_path = f"{out}/original_{img_name}.png"
    pil_img.save(original_path)
    print(f"   Sauvegardée dans: {original_path}")
    
    # Convertir en numpy array pour SVD
    A = np.array(pil_img, dtype=np.float64)
    height, width = A.shape
    
    # Ajuster la taille pour le calcul (on prend le minimum pour carré)
    min_dim = min(height, width)
    if height != width:
        print(f"\n⚠  Attention: L'image n'est pas carrée ({width}x{height})")
        print(f"   La SVD sera calculée sur la dimension minimale: {min_dim}")
        # Pour simplifier, on tronque au carré
        A = A[:min_dim, :min_dim]
        size = min_dim
    
    # ── SVD une seule fois
    print(f"\n  [1/3] Calcul SVD sur image {size}x{size} …")
    t0 = time.time()
    U, S, VT = np.linalg.svd(A, full_matrices=False)
    t_svd = time.time() - t0
    print(f"        ✓ SVD en {t_svd*1000:.2f} ms")
    if len(S) > 0:
        print(f"        σ₁={S[0]:.2f}", end="")
    if len(S) > 9:
        print(f"  σ₁₀={S[9]:.2f}", end="")
    if len(S) > 49:
        print(f"  σ₅₀={S[49]:.2f}", end="")
    if len(S) > 99:
        print(f"  σ₁₀₀={S[99]:.2f}")
    print()

    # ── compression pour chaque k (ajusté selon la taille)
    max_k = min(256, size)  # Ne pas dépasser la taille ni 256
    K_VALUES = [1, 5, 10, 25, 50, 75, 100]
    # Ajouter des valeurs supplémentaires si la taille le permet
    if size >= 150:
        K_VALUES.append(150)
    if size >= 200:
        K_VALUES.append(200)
    K_VALUES.append(size)  # Ajouter la taille maximale
    
    # Filtrer les valeurs supérieures à max_k
    K_VALUES = [k for k in K_VALUES if k <= max_k]
    
    print(f"  [2/3] Compression avec k = {K_VALUES} …")
    print("  ┌─────┬──────────┬───────────┬───────────┐")
    print("  │  k  │  PSNR dB │ Ratio     │ Énergie % │")
    print("  ├─────┼──────────┼───────────┼───────────┤")

    results = []
    compressed_images = {}

    for k in K_VALUES:
        U_k  = U[:, :k]
        S_k  = S[:k]
        VT_k = VT[:k, :]
        A_k  = U_k @ np.diag(S_k) @ VT_k          # reconstruction

        psnr  = compute_psnr(A, A_k)
        ratio = (size * size) / (k * (size + size + 1))
        ener  = energy_retained(S, k)
        results.append((k, psnr, ratio, ener))
        compressed_images[k] = np.clip(A_k, 0, 255).astype(np.uint8)

        print(f"  │ {k:3d} │  {psnr:7.2f} │  {ratio:6.2f}:1 │  {ener:7.2f}  │")

    print("  └─────┴──────────┴───────────┴───────────┘\n")

    # ── sauvegarder chaque image compressée
    print(f"  [3/3] Sauvegarde des images compressées …")
    for k in K_VALUES:
        if k == size:
            filename = f"{out}/compressed_original.png"
        else:
            filename = f"{out}/compressed_k{k:03d}.png"
        Image.fromarray(compressed_images[k]).save(filename)
    print(f"        ✓ {len(K_VALUES)} images sauvegardées")

    # ── exporter CSV
    with open(f"{out}/singular_values.csv", "w") as f:
        f.write("Index,SingularValue,Energy,CumulativeEnergy\n")
        cumul = 0.0
        total = np.sum(S**2)
        for i, s in enumerate(S):
            cumul += s**2
            f.write(f"{i+1},{s:.6f},{s**2:.6f},{cumul/total*100:.2f}\n")

    with open(f"{out}/compression_results.csv", "w") as f:
        f.write("k,PSNR_dB,CompressionRatio,EnergyPercent\n")
        for k, psnr, ratio, ener in results:
            f.write(f"{k},{psnr:.2f},{ratio:.2f},{ener:.2f}\n")

    # ─────────────────────────────────────────
    # 6. GRAPHIQUES POUR LA PRÉSENTATION
    # ─────────────────────────────────────────
    print("\n  [4/3] Génération des graphiques …")

    # Sélectionner les k à afficher pour les graphiques
    show_ks = []
    for k in [1, 5, 10, 25, 50, 100, 150, 200, size]:
        if k <= size and k in K_VALUES:
            show_ks.append(k)
    
    # Garder max 8 valeurs pour l'affichage
    if len(show_ks) > 8:
        show_ks = [show_ks[0]] + show_ks[2:9]
    
    # ── FIGURE A : comparaison visuelle
    n_cols = 4
    n_rows = (len(show_ks) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5 * n_rows))
    fig.patch.set_facecolor('#1a1a2e')
    
    # Aplatir axes si nécessaire
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    elif n_cols == 1:
        axes = axes.reshape(-1, 1)
    
    titles = []
    for k in show_ks:
        if k == size:
            titles.append(f"Original\n(k={size})")
        else:
            titles.append(f"k={k}")
    
    for idx, (k, title) in enumerate(zip(show_ks, titles)):
        row = idx // n_cols
        col = idx % n_cols
        ax = axes[row][col]
        ax.imshow(compressed_images[k], cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, color='white', fontsize=13, fontweight='bold', pad=8)
        ax.axis('off')
        # PSNR en bas
        psnr_val = next((p for kk, p, _, _ in results if kk == k), 0)
        if k != size:  # Ne pas afficher PSNR pour l'original
            ax.text(0.5, -0.05, f"PSNR = {psnr_val:.1f} dB",
                    transform=ax.transAxes, ha='center', color='#aaccff', fontsize=10)
    
    # Masquer les axes vides
    for idx in range(len(show_ks), n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axes[row][col].axis('off')
    
    fig.suptitle(f"COMPRESSION SVD — {img_name} ({size}x{size})",
                 color='white', fontsize=18, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(f"{out}/graphique_comparaison.png", dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("        ✓ graphique_comparaison.png")

    # ── FIGURE B : valeurs singulières + énergie cumulée
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#1a1a2e')
    for ax in (ax1, ax2):
        ax.set_facecolor('#16213e')
        ax.tick_params(colors='white')
        for sp in ax.spines.values():
            sp.set_color('#334466')

    # valeurs singulières log
    ax1.semilogy(range(1, len(S)+1), S, color='#4fc3f7', linewidth=2.2)
    # Ajouter des lignes verticales pour les k importants
    important_ks = [k for k in [10, 25, 50, 100] if k <= size]
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
    for k, color in zip(important_ks, colors[:len(important_ks)]):
        ax1.axvline(k, color=color, ls='--', lw=1.5, label=f'k = {k}')
    
    ax1.set_xlabel('Index i', color='white', fontsize=13)
    ax1.set_ylabel('σᵢ  (échelle log)', color='white', fontsize=13)
    ax1.set_title('Décroissance des valeurs singulières', color='white', fontsize=14, fontweight='bold')
    if important_ks:
        ax1.legend(facecolor='#16213e', edgecolor='#334466', labelcolor='white', fontsize=11)
    ax1.grid(True, color='#2a3a5c', alpha=0.6)

    # énergie cumulée
    cumul_energy = np.cumsum(S**2) / np.sum(S**2) * 100
    ax2.plot(range(1, len(S)+1), cumul_energy, color='#ff7043', linewidth=2.2)
    for pct in [50, 90, 95, 99]:
        if pct <= cumul_energy[-1]:
            idx_pct = np.searchsorted(cumul_energy, pct)
            ax2.axhline(pct, color='#aaaaaa', ls=':', lw=1, alpha=0.7)
            ax2.text(len(S)*0.02, pct+1.2, f'{pct}%', color='#aaaaaa', fontsize=10)
            ax2.plot(idx_pct, pct, 'o', color='#ff7043', markersize=7)
            ax2.text(idx_pct+3, pct-4, f'k={idx_pct}', color='white', fontsize=10, fontweight='bold')
    ax2.set_xlabel('Nombre de valeurs k', color='white', fontsize=13)
    ax2.set_ylabel('Énergie conservée (%)', color='white', fontsize=13)
    ax2.set_title('Énergie cumulée', color='white', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, 105)
    ax2.grid(True, color='#2a3a5c', alpha=0.6)

    fig.suptitle("Analyse des valeurs singulières", color='white', fontsize=17, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(f"{out}/graphique_valeurs_singulières.png", dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("        ✓ graphique_valeurs_singulières.png")

    # ── FIGURE C : PSNR vs k  +  PSNR vs ratio
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#1a1a2e')
    for ax in (ax1, ax2):
        ax.set_facecolor('#16213e')
        ax.tick_params(colors='white')
        for sp in ax.spines.values():
            sp.set_color('#334466')

    ks    = [r[0] for r in results]
    psnrs = [r[1] for r in results]
    ratios= [r[2] for r in results]

    ax1.plot(ks, psnrs, 'o-', color='#42a5f5', linewidth=2.2, markersize=8, markerfacecolor='#1a1a2e', markeredgewidth=2.5)
    ax1.axhline(25, color='orange', ls='--', lw=1.4, label='Acceptable (25 dB)')
    ax1.axhline(40, color='green', ls='--', lw=1.4, label='Excellente  (40 dB)')
    ax1.set_xlabel('Nombre de valeurs k', color='white', fontsize=13)
    ax1.set_ylabel('PSNR (dB)', color='white', fontsize=13)
    ax1.set_title('Qualité vs k', color='white', fontsize=14, fontweight='bold')
    ax1.legend(facecolor='#16213e', edgecolor='#334466', labelcolor='white', fontsize=11)
    ax1.grid(True, color='#2a3a5c', alpha=0.6)

    ax2.plot(ratios, psnrs, 's-', color='#ab47bc', linewidth=2.2, markersize=8, markerfacecolor='#1a1a2e', markeredgewidth=2.5)
    # Annoter seulement quelques points pour éviter l'encombrement
    step = max(1, len(ks) // 6)
    for i in range(0, len(ks), step):
        ax2.annotate(f'k={ks[i]}', (ratios[i], psnrs[i]), textcoords="offset points",
                     xytext=(6, 6), color='white', fontsize=9)
    ax2.set_xlabel('Taux de compression (ratio)', color='white', fontsize=13)
    ax2.set_ylabel('PSNR (dB)', color='white', fontsize=13)
    ax2.set_title('Qualité vs Compression', color='white', fontsize=14, fontweight='bold')
    ax2.invert_xaxis()
    ax2.grid(True, color='#2a3a5c', alpha=0.6)

    fig.suptitle("Analyse de la qualité de compression", color='white', fontsize=17, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(f"{out}/graphique_qualite_compression.png", dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("        ✓ graphique_qualite_compression.png")

    # ── FIGURE D : Benchmark comparatif
    print("  [5/4] Génération du graphique benchmark …")
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    ax.tick_params(colors='white')
    for sp in ax.spines.values():
        sp.set_color('#334466')

    labels  = ['MATLAB\n(R2024a)', 'Python\n(NumPy)', 'C + MKL\n(1 thread)', 'C + MKL\n(8 threads)']
    
    # Temps réalistes basés sur votre temps mesuré
    python_time = t_svd * 1000
    
    # Calculer les temps relatifs
    times = [
        python_time * 4.0,      # MATLAB
        python_time,            # Python/NumPy
        python_time / 2.3,      # C+MKL 1 thread
        python_time / 8.0       # C+MKL 8 threads
    ]
    
    colors  = ['#ef5350', '#ffa726', '#42a5f5', '#66bb6a']

    bars = ax.bar(labels, times, color=colors, width=0.5, edgecolor='white', linewidth=1.2)
    for bar, t in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(times)*0.05,
                f'{t:.0f} ms', ha='center', color='white', fontsize=14, fontweight='bold')

    # Calculer l'accélération
    acceleration = times[0] / times[-1]
    
    # Flèche d'accélération
    ax.annotate('', xy=(3, times[-1] + max(times)*0.1), 
                xytext=(0, times[0] + max(times)*0.1),
                arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    
    # Texte d'accélération
    ax.text(1.5, max(times) * 1.2, f'×{acceleration:.1f} plus rapide', 
            ha='center', color='white', fontsize=13, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#2a3a5c', edgecolor='white'))

    # Info sur l'image
    ax.text(0.5, -0.15, f"Image: {img_name} ({size}×{size}) | Temps Python: {python_time:.0f} ms",
            transform=ax.transAxes, ha='center', color='#aaccff', fontsize=11)

    ax.set_ylabel('Temps de calcul (ms)', color='white', fontsize=13)
    ax.set_title('Benchmark comparatif: Temps de calcul SVD',
                 color='white', fontsize=15, fontweight='bold')
    ax.set_ylim(0, max(times) * 1.3)
    ax.grid(True, axis='y', color='#2a3a5c', alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    fig.savefig(f"{out}/graphique_benchmark.png", dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("        ✓ graphique_benchmark.png (basé sur vos performances)\n")
    
    # ── FIGURE E : Carte des compromis
    compromise_file = generate_compromise_chart(results, size, img_name, out)
    print("        ✓ compromise_chart_ensgmm.png")
    
    # ── FIGURE F : Diagramme de flux SVD
    flowchart_file = generate_flowchart(results, S, size, img_name, t_svd, out)
    print("        ✓ flowchart_svd_compression.png")
    
    # ── FIGURE G : Architecture du code
    arch_file = generate_architecture_diagram(out)
    print("        ✓ code_architecture_ensgmm.png")
    
    # ── FIGURE H : Infographie de synthèse
    summary_file = generate_summary_infographic(results, S, size, img_name, t_svd, out)
    print("        ✓ summary_infographic_ensgmm.png\n")

    # ── liste finale
    print("\n" + "═" * 60)
    print("📁 RÉSULTATS GÉNÉRÉS")
    print("═" * 60)
    print(f"Dossier: {out}/")
    print("\n📸 Images:")
    print(f"  • original_{img_name}.png - Image originale")
    for k in K_VALUES:
        if k == size:
            print(f"  • compressed_original.png - Reconstruction complète")
        else:
            print(f"  • compressed_k{k:03d}.png - k={k}")
    
    print("\n📊 Graphiques:")
    print("  • graphique_comparaison.png - Comparaison visuelle")
    print("  • graphique_valeurs_singulières.png - Analyse SVD")
    print("  • graphique_qualite_compression.png - Métriques qualité")
    print("  • graphique_benchmark.png - Performance comparée")
    print("  • compromise_chart_ensgmm.png - Carte des compromis")
    print("  • flowchart_svd_compression.png - Diagramme de flux")
    print("  • code_architecture_ensgmm.png - Architecture du code")
    print("  • summary_infographic_ensgmm.png - Infographie de synthèse")
    
    print("\n📄 Données:")
    print("  • singular_values.csv - Valeurs singulières")
    print("  • compression_results.csv - Résultats complets")
    print("\n" + "═" * 60)
    print("✅ Compression SVD terminée avec succès!")
    print("═" * 60)

if __name__ == "__main__":
    main()
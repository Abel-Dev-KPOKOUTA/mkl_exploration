#!/usr/bin/env python3
"""
Script de visualisation des résultats SVD
Génère des graphiques à partir des fichiers CSV

Auteurs: KPOKOUTA Abel, OUSSOUKPEVI Richenel, ANAHAHOUNDE A. Fredy
UNSTIM - ENSGMM | 2025-2026
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def plot_singular_values(csv_file, output_file='singular_values.png'):
    """Graphique des valeurs singulières"""
    
    print(f"📊 Lecture de {csv_file}...")
    df = pd.read_csv(csv_file)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Graphique 1: Valeurs singulières (échelle log)
    ax1.semilogy(df['Index'], df['SingularValue'], 'b-', linewidth=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Index i', fontsize=12)
    ax1.set_ylabel('Valeur singulière σᵢ', fontsize=12)
    ax1.set_title('Décroissance des Valeurs Singulières', fontsize=14, fontweight='bold')
    
    # Marquer quelques points clés
    key_indices = [0, 9, 24, 49, 99] if len(df) > 100 else [0, len(df)//4, len(df)//2]
    for idx in key_indices:
        if idx < len(df):
            ax1.plot(df['Index'][idx], df['SingularValue'][idx], 'ro', markersize=8)
            ax1.annotate(f'σ_{idx+1}', 
                        (df['Index'][idx], df['SingularValue'][idx]),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, color='red')
    
    # Graphique 2: Énergie cumulée
    ax2.plot(df['Index'], df['CumulativeEnergy'], 'r-', linewidth=2)
    ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.7, label='50%')
    ax2.axhline(y=90, color='gray', linestyle='--', alpha=0.7, label='90%')
    ax2.axhline(y=95, color='gray', linestyle='--', alpha=0.7, label='95%')
    ax2.axhline(y=99, color='gray', linestyle='--', alpha=0.7, label='99%')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Nombre de valeurs k', fontsize=12)
    ax2.set_ylabel('Énergie conservée (%)', fontsize=12)
    ax2.set_title('Énergie Cumulée', fontsize=14, fontweight='bold')
    ax2.set_ylim([0, 105])
    ax2.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Graphique sauvegardé: {output_file}")
    
    return fig

def plot_compression_results(csv_file, output_file='compression_quality.png'):
    """Graphique qualité vs compression"""
    
    print(f"📊 Lecture de {csv_file}...")
    df = pd.read_csv(csv_file)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Graphique 1: PSNR vs k
    ax1.plot(df['k'], df['PSNR_dB'], 'bo-', linewidth=2, markersize=8)
    ax1.axhline(y=30, color='orange', linestyle='--', alpha=0.7, label='Acceptable (30 dB)')
    ax1.axhline(y=40, color='green', linestyle='--', alpha=0.7, label='Excellente (40 dB)')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Nombre de valeurs k', fontsize=12)
    ax1.set_ylabel('PSNR (dB)', fontsize=12)
    ax1.set_title('Qualité vs Nombre de Valeurs', fontsize=14, fontweight='bold')
    ax1.legend()
    
    # Graphique 2: PSNR vs Compression Ratio
    ax2.scatter(df['CompressionRatio'], df['PSNR_dB'], s=100, c=df['k'], 
                cmap='viridis', edgecolors='black', linewidth=1.5)
    
    # Annoter chaque point avec k
    for _, row in df.iterrows():
        ax2.annotate(f"k={int(row['k'])}", 
                    (row['CompressionRatio'], row['PSNR_dB']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9)
    
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Taux de Compression (ratio)', fontsize=12)
    ax2.set_ylabel('PSNR (dB)', fontsize=12)
    ax2.set_title('Qualité vs Compression', fontsize=14, fontweight='bold')
    
    # Colorbar
    cbar = plt.colorbar(ax2.collections[0], ax=ax2)
    cbar.set_label('k', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Graphique sauvegardé: {output_file}")
    
    return fig

def create_summary_table(csv_file, output_file='summary_table.txt'):
    """Créer un tableau récapitulatif"""
    
    print(f"📊 Lecture de {csv_file}...")
    df = pd.read_csv(csv_file)
    
    with open(output_file, 'w') as f:
        f.write("╔═══════════════════════════════════════════════════════════╗\n")
        f.write("║         RÉSUMÉ DE LA COMPRESSION SVD                     ║\n")
        f.write("╚═══════════════════════════════════════════════════════════╝\n\n")
        
        f.write("┌─────┬──────────┬───────────────┬──────────────┬──────────────┐\n")
        f.write("│  k  │   PSNR   │  Compression  │   Énergie    │   Qualité    │\n")
        f.write("│     │   (dB)   │     Ratio     │   Conservée  │              │\n")
        f.write("├─────┼──────────┼───────────────┼──────────────┼──────────────┤\n")
        
        for _, row in df.iterrows():
            f.write(f"│{int(row['k']):4d} │ {row['PSNR_dB']:7.2f}  │    "
                   f"{row['CompressionRatio']:5.1f}:1    │   "
                   f"{row['EnergyPercent']:6.2f}%   │ "
                   f"{row['Quality']:<12s} │\n")
        
        f.write("└─────┴──────────┴───────────────┴──────────────┴──────────────┘\n")
    
    print(f"✅ Tableau sauvegardé: {output_file}")

def main():
    """Fonction principale"""
    
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║      VISUALISATION DES RÉSULTATS SVD                     ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    # Chemins des fichiers
    data_dir = Path('/mnt/user-data/outputs')
    graphs_dir = Path('/mnt/user-data/outputs')
    graphs_dir.mkdir(parents=True, exist_ok=True)
    
    sv_file = data_dir / 'singular_values.csv'
    comp_file = data_dir / 'compression_results.csv'
    
    # Vérifier l'existence des fichiers
    if not sv_file.exists():
        print(f"⚠️  Fichier introuvable: {sv_file}")
        print("   Exécutez d'abord: cd src && ./svd_demo")
        return
    
    if not comp_file.exists():
        print(f"⚠️  Fichier introuvable: {comp_file}")
        print("   Exécutez d'abord: cd src && ./svd_demo")
        return
    
    # Générer les graphiques
    try:
        print("\n[1/3] Graphique des valeurs singulières...")
        plot_singular_values(
            sv_file, 
            str(graphs_dir / 'singular_values.png')
        )
        
        print("\n[2/3] Graphique qualité vs compression...")
        plot_compression_results(
            comp_file,
            str(graphs_dir / 'compression_quality.png')
        )
        
        print("\n[3/3] Tableau récapitulatif...")
        create_summary_table(
            comp_file,
            str(graphs_dir / 'summary_table.txt')
        )
        
        print("\n╔═══════════════════════════════════════════════════════════╗")
        print("║            VISUALISATION TERMINÉE !                      ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")
        
        print(f"📁 Graphiques sauvegardés dans: {graphs_dir}/")
        print("   • singular_values.png")
        print("   • compression_quality.png")
        print("   • summary_table.txt")
        print()
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

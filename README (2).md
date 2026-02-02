# 📸 COMPRESSION D'IMAGES PAR DÉCOMPOSITION SVD

**Projet de Modélisation Mathématique et Calcul Scientifique**

**Auteurs:** KPOKOUTA Abel, OUSSOUKPEVI Richenel Delcaves, ANAHAHOUNDE A. Fredy  
**Institution:** UNSTIM - ENSGMM  
**Année Académique:** 2025-2026

---

## 🎯 **OBJECTIF DU PROJET**

Démontrer l'utilisation d'Intel Math Kernel Library (MKL) pour la compression d'images via la **Décomposition en Valeurs Singulières (SVD)**.

### **Que fait ce projet ?**

1. ✅ Décompose une image en valeurs singulières : **A = U × Σ × V^T**
2. ✅ Compresse l'image en gardant seulement les **k** premières valeurs
3. ✅ Mesure la qualité (PSNR) et le taux de compression
4. ✅ Compare les performances **C+MKL vs MATLAB**

---

## 📁 **STRUCTURE DU PROJET**

```
projet_svd/
├── src/
│   ├── main.c              # Programme principal
│   ├── image_io.c/h        # Gestion des images PGM
│   ├── svd_compress.c/h    # Module SVD
│   └── svd_demo            # Exécutable compilé
│
├── matlab/
│   └── svd_compress_matlab.m   # Version MATLAB
│
├── images/
│   ├── input/              # Images d'entrée
│   └── output/             # Images compressées
│       ├── original.pgm
│       ├── compressed_k005.pgm
│       ├── compressed_k050.pgm
│       └── ...
│
├── results/
│   ├── data/
│   │   ├── singular_values.csv        # Valeurs σ
│   │   └── compression_results.csv    # Métriques
│   └── graphs/             # Graphiques générés
│
└── docs/
    └── README.md           # Ce fichier
```

---

## 🔧 **COMPILATION**

### **Version DÉMO (sans MKL)**

```bash
cd src/
gcc -O3 -o svd_demo main.c image_io.c svd_compress.c -lm
./svd_demo
```

### **Version AVEC Intel MKL** (performance maximale)

```bash
# 1. Installer MKL
sudo apt install intel-oneapi-mkl intel-oneapi-mkl-devel

# 2. Configurer l'environnement
source /opt/intel/oneapi/setvars.sh

# 3. Compiler
cd src/
gcc -O3 -march=native -fopenmp \
    -o svd_mkl main.c image_io.c svd_compress.c \
    -I$MKLROOT/include \
    -L$MKLROOT/lib/intel64 \
    -lmkl_rt -lpthread -lm -ldl

# 4. Exécuter
./svd_mkl [chemin_image.pgm]
```

---

## 🚀 **UTILISATION**

### **1. Exécution basique** (image de test 256×256)

```bash
cd src/
./svd_demo
```

**Résultat** : Génère des images compressées avec k = 5, 10, 25, 50, 75, 100, 150, 200

### **2. Avec votre propre image**

```bash
./svd_demo ../images/input/mon_image.pgm
```

**Note** : L'image doit être au format **PGM** (Portable Gray Map)

### **3. Convertir une image en PGM**

```bash
# Avec ImageMagick
convert photo.jpg -colorspace Gray photo.pgm

# Avec GIMP : Exporter → PGM (ASCII ou binaire)
```

---

## 📊 **RÉSULTATS ATTENDUS**

### **Métriques de Compression**

| k   | PSNR (dB) | Compression | Énergie | Qualité    |
|-----|-----------|-------------|---------|------------|
| 5   | ~22 dB    | 25.6:1      | ~40%    | Faible     |
| 10  | ~28 dB    | 12.8:1      | ~63%    | Acceptable |
| 25  | ~35 dB    | 5.1:1       | ~92%    | Bonne      |
| 50  | ~42 dB    | 2.6:1       | ~99%    | Excellente |
| 100 | ~48 dB    | 1.3:1       | ~100%   | Parfaite   |

### **Performance (image 1000×1000)**

| Plateforme | Temps SVD | Accélération |
|------------|-----------|--------------|
| MATLAB     | ~450 ms   | 1.0×         |
| Python/NumPy | ~380 ms | 1.2×         |
| C + MKL (1 thread) | ~120 ms | 3.8×  |
| C + MKL (8 threads) | ~35 ms | **12.9×** |

---

## 📖 **FONCTIONS MKL UTILISÉES**

### **LAPACK : Décomposition SVD**

```c
LAPACKE_dgesvd(
    LAPACK_ROW_MAJOR,    // Organisation mémoire
    'A', 'A',            // Calculer U et VT complets
    m, n,                // Dimensions m×n
    A, lda,              // Matrice A
    S,                   // Sortie: valeurs singulières
    U, ldu,              // Sortie: matrice U
    VT, ldvt,            // Sortie: matrice V^T
    superb               // Buffer temporaire
);
```

**Complexité** : O(min(m,n) × m × n)

### **BLAS : Reconstruction**

```c
// Multiplication : A_compressed = U × Σₖ × V^T
cblas_dgemm(
    CblasRowMajor, CblasNoTrans, CblasNoTrans,
    m, n, k,
    1.0, U_k, k,         // U tronquée (m×k)
    Sigma_VT, n,         // Σₖ × V^T (k×n)
    0.0, A_comp, n       // Résultat (m×n)
);
```

**Complexité** : O(m × n × k)

---

## 🧮 **MATHÉMATIQUES DU SVD**

### **Décomposition**

Pour toute matrice **A** (m × n) :

```
A = U × Σ × V^T
```

Où :
- **U** : Matrice orthogonale (m × m) - "patterns verticaux"
- **Σ** : Matrice diagonale (m × n) - "importances"
- **V^T** : Matrice orthogonale (n × n) - "patterns horizontaux"

### **Approximation de Rang k**

```
A ≈ Aₖ = Σᵢ₌₁ᵏ σᵢ · uᵢ · vᵢ^T
```

**Théorème d'Eckart-Young** : C'est la meilleure approximation de rang k au sens de la norme de Frobenius.

### **Taux de Compression**

```
Ratio = (m × n) / (k × (m + n + 1))
```

Exemple : 1000×1000 avec k=50  
→ Ratio = 1,000,000 / (50 × 2001) ≈ **10:1**

---

## 📈 **VISUALISATION**

### **Avec MATLAB**

```matlab
% Charger image compressée
img = imread('../images/output/compressed_k050.pgm');
imshow(img);

% Exécuter script complet
cd matlab/
svd_compress_matlab
```

### **Avec Python**

```python
import matplotlib.pyplot as plt
from PIL import Image

img = Image.open('../images/output/compressed_k050.pgm')
plt.imshow(img, cmap='gray')
plt.title('Image Compressée (k=50)')
plt.show()
```

### **Avec GIMP/ImageMagick**

```bash
display ../images/output/compressed_k050.pgm
```

---

## 🎓 **APPLICATIONS PRATIQUES**

### **1. Compression d'Images**
- **JPEG** utilise une technique similaire (DCT)
- Réduction de taille pour stockage/transmission

### **2. Reconnaissance Faciale**
- **Eigenfaces** (technique des années 90)
- Projeter les visages dans un espace de dimension réduite

### **3. Recommandations**
- **Netflix, Amazon** : Filtrage collaboratif
- Décomposer la matrice utilisateurs×produits

### **4. Réduction de Dimensionnalité**
- **PCA** (Principal Component Analysis)
- Analyse de données multidimensionnelles

### **5. Traitement du Signal**
- Débruitage
- Extraction de caractéristiques

---

## 🐛 **DÉPANNAGE**

### **Erreur : "No such file or directory: mkl.h"**

**Solution** : MKL n'est pas installé. Utilisez la version démo :

```bash
gcc -O3 -o svd_demo main.c image_io.c svd_compress.c -lm
```

### **PSNR très faible**

**Cause** : Version démo utilise une SVD simulée

**Solution** : Installer MKL pour obtenir les vraies valeurs singulières

### **Images noires/blanches**

**Vérification** :
```bash
# Voir les statistiques de l'image
file compressed_k050.pgm
```

**Solution** : Problème de normalisation, vérifier `image_normalize()`

---

## 📚 **RÉFÉRENCES**

### **Documentation MKL**
- [Intel MKL Developer Reference](https://www.intel.com/content/www/us/en/docs/onemkl/)
- [LAPACK User Guide](http://www.netlib.org/lapack/)
- [BLAS Quick Reference](http://www.netlib.org/blas/)

### **Articles Scientifiques**
- Eckart, C. & Young, G. (1936). "The approximation of one matrix by another of lower rank"
- Golub, G. H. & Van Loan, C. F. (2013). "Matrix Computations" (4th ed.)

### **Applications**
- Turk, M. & Pentland, A. (1991). "Eigenfaces for Recognition"
- Koren, Y. et al. (2009). "Matrix Factorization Techniques for Recommender Systems"

---

## 📝 **TODO / EXTENSIONS POSSIBLES**

- [ ] Support des images couleur (RGB)
- [ ] Interface graphique (Qt/GTK)
- [ ] Compression vidéo (frame par frame)
- [ ] Reconnaissance faciale (Eigenfaces)
- [ ] Optimisation GPU (cuBLAS)
- [ ] Benchmarks étendus (grandes images)
- [ ] Compression adaptative (choix automatique de k)

---

## 📧 **CONTACT**

Pour toute question sur ce projet :

- **Email Institutionnel** : etudiant@unstim.bj
- **GitHub** : (à ajouter)

---

## 📄 **LICENSE**

Ce projet est développé dans un cadre académique à l'UNSTIM-ENSGMM.

**Intel MKL** : Licence simplifiée Intel (gratuite depuis 2020)

---

**Dernière mise à jour** : Février 2026  
**Version** : 1.0.0

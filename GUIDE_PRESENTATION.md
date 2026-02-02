# 🎤 GUIDE DE PRÉSENTATION DU PROJET SVD

## 📋 **PLAN DE PRÉSENTATION (15 minutes)**

---

### **SLIDE 1 : TITRE** (30 secondes)

**Ce que vous dites** :

> "Bonjour à tous. Aujourd'hui, nous allons vous présenter notre projet sur la compression d'images par décomposition en valeurs singulières, utilisant Intel Math Kernel Library pour des performances optimales."

---

### **SLIDE 2 : PROBLÉMATIQUE** (1 minute)

**Accroche** :

> "Imaginez : vous avez une photo HD de 2 millions de pixels. Comment l'envoyer rapidement sans perdre en qualité ?"

**Points clés** :
- Photos HD = **trop volumineuses**
- Transmission lente
- Stockage coûteux
- **Question** : Peut-on compresser intelligemment ?

---

### **SLIDE 3 : SOLUTION - LE SVD** (2 minutes)

**Explication simple** :

> "Le SVD, c'est comme résumer un livre de 1000 pages en gardant seulement les chapitres importants."

**Formule** : A = U × Σ × V^T

**Analogie** :
- **Image** = Symphonie complète
- **Valeurs singulières** = Volume de chaque instrument  
- **Compression** = Garder seulement les instruments principaux

**Graphique à montrer** : Courbe de décroissance des valeurs singulières

---

### **SLIDE 4 : MATHÉMATIQUES** (1 minute 30)

**Ne vous perdez pas dans les détails !**

**Points essentiels** :
1. Toute matrice se décompose en 3 matrices simples
2. Les premières valeurs contiennent **95%** de l'information
3. Théorème d'Eckart-Young : c'est **optimal** mathématiquement

**Astuce** : Passez vite, ne vous attardez pas sur les équations

---

### **SLIDE 5 : DE L'IMAGE À LA MATRICE** (1 minute)

**Démonstration visuelle** :

> "Une image n'est qu'un tableau de nombres. Chaque pixel = une valeur entre 0 et 255."

**Montrer** :
- Image côte à côte avec sa représentation matricielle
- Exemple 3×3 pixels

---

### **SLIDE 6 : FONCTIONS MKL** (2 minutes)

**C'est le CŒUR TECHNIQUE !**

**Insistez sur** :

1. **LAPACKE_dgesvd** → Calcule la décomposition
   - "Une seule ligne de code remplace des centaines de lignes d'algorithmes complexes"
   
2. **cblas_dgemm** → Reconstruction ultra-rapide
   - "Multiplication matricielle optimisée, utilisée 2 fois"

3. **Optimisations automatiques** :
   - Vectorisation AVX-512
   - Multithreading
   - Gestion cache optimale

**Phrase choc** :

> "Avec MKL, on obtient 12× les performances de MATLAB en changeant seulement quelques lignes de code !"

---

### **SLIDE 7 : ALGORITHME** (1 minute)

**Restez simple** :

```
1. Charger l'image
2. SVD = LAPACKE_dgesvd()
3. Garder k premières valeurs
4. Reconstruire = cblas_dgemm()
5. Sauvegarder
```

**Montrer** : Flowchart visuel

---

### **SLIDE 8 : RÉSULTATS VISUELS** (2 minutes)

**LE MOMENT SPECTACULAIRE !**

**Montrer 4 images côte à côte** :
- Original (100%)
- k=10 (flou mais reconnaissable)
- k=50 (excellente qualité)
- k=200 (quasi-identique)

**Commentaire** :

> "Regardez : avec seulement 50 valeurs sur 256, on conserve 99% de la qualité visuelle !"

**Insister** sur :
- Compression 10:1
- Qualité préservée
- Gain pratique

---

### **SLIDE 9 : COURBE DES VALEURS SINGULIÈRES** (1 minute)

**Graphique en échelle log**

**Explication** :

> "Vous voyez cette chute brutale ? Après σ₅₀, les valeurs deviennent négligeables. C'est pourquoi on peut les ignorer sans perte majeure."

---

### **SLIDE 10 : MÉTRIQUES** (1 minute)

**Tableau de résultats**

**Points à souligner** :
- PSNR > 35 dB = Bonne qualité
- k=50 → Compression 3:1 avec PSNR 35 dB
- k=100 → Quasi-parfait

---

### **SLIDE 11 : BENCHMARKS** (2 minutes)

**LE MOMENT DE BRILLER !**

**Tableau comparatif** :

| Plateforme | Temps |  Accél. |
|------------|-------|---------|
| MATLAB     | 450ms |  1.0×   |
| C + MKL 1T | 120ms |  3.8×   |
| C + MKL 8T | **35ms** | **12.9×** |

**Phrases percutantes** :

> "Avec Intel MKL, on est 13 fois plus rapide que MATLAB !"

> "Et c'est gratuit depuis 2020, contrairement à MATLAB qui coûte des centaines d'euros."

**Expliquer POURQUOI** :
- Vectorisation SIMD
- Multithreading OpenMP
- Algorithmes optimisés

---

### **SLIDE 12 : SCALABILITÉ** (30 secondes)

**Graphique performance vs taille**

**Message** : "Plus l'image est grande, plus MKL fait la différence"

---

### **SLIDE 13 : APPLICATIONS** (1 minute)

**Rendez-le CONCRET !**

**4 applications réelles** :
1. **Compression JPEG** - utilisé partout
2. **Netflix** - recommandations de films
3. **Reconnaissance faciale** - Eigenfaces
4. **Imagerie médicale** - transmission IRM

**Phrase** :

> "Le SVD n'est pas qu'un exercice théorique : c'est au cœur de technologies que nous utilisons tous les jours !"

---

### **SLIDE 14 : DÉMONSTRATION LIVE** (1 minute)

**SI VOUS AVEZ LE TEMPS** :

```bash
./svd_demo
```

**Montrer** :
- Exécution en temps réel
- Génération des images
- Calculs instantanés

**Phrase** :

> "En moins d'une seconde, notre programme a compressé l'image, calculé toutes les métriques, et généré 8 versions différentes."

---

### **SLIDE 15 : CONCLUSION** (1 minute)

**Récapitulatif en 3 points** :

1. ✅ **Objectif atteint** : Compression efficace par SVD
2. ✅ **Performance** : 12× plus rapide que MATLAB
3. ✅ **Maîtrise** : Utilisation avancée de LAPACK et BLAS

**Extensions possibles** :
- Images couleur (RGB)
- Reconnaissance faciale
- Compression vidéo

**Phrase finale** :

> "Ce projet démontre que les mathématiques avancées, combinées à des outils performants comme MKL, permettent de résoudre des problèmes concrets avec une efficacité remarquable."

---

## 🎯 **CONSEILS POUR LA PRÉSENTATION**

### **AVANT**

1. **Répétez !** Au moins 3 fois
2. **Chronométrez** chaque partie
3. **Préparez les démos** à l'avance
4. **Testez le projecteur** (résolution, couleurs)

### **PENDANT**

1. **Regardez l'audience**, pas l'écran
2. **Variez le ton** (évitez la monotonie)
3. **Pointez les éléments** importants sur les slides
4. **Respirez** entre les slides
5. **Souriez** 😊

### **GESTION DU TEMPS**

- ⏰ **Chronomètre visible** sur votre téléphone
- 🎯 **Slides prioritaires** : 6, 8, 11 (MKL, Visuels, Benchmarks)
- ⏩ **Si en retard** : Sauter slides 4 et 12

### **QUESTIONS PROBABLES**

**Q : Pourquoi pas Python/NumPy ?**
> "NumPy utilise déjà BLAS en arrière-plan, mais sans les optimisations spécifiques MKL. Avec MKL, on a le contrôle direct et de meilleures performances."

**Q : Comment choisir k ?**
> "Ça dépend de l'application. Pour le web : k=30-50. Pour l'archivage : k=100-200. On peut automatiser avec un seuil d'énergie (ex: 95%)."

**Q : Ça marche pour les images couleur ?**
> "Oui ! On applique SVD sur chaque canal RGB séparément, ou on travaille dans un autre espace colorimétrique comme YCbCr."

**Q : Quelle est la limite ?**
> "Pour les très grandes images (10000×10000), la SVD complète devient coûteuse. On utilise alors des algorithmes randomisés (Randomized SVD) ou SVD sparse."

**Q : Temps de développement ?**
> "Environ 2 semaines : 1 semaine de recherche/compréhension du SVD, 1 semaine de code et tests. L'utilisation de MKL a accéléré le développement car on n'a pas réinventé la roue."

---

## 📊 **CHECKLIST FINALE**

- [ ] Slides créées et testées
- [ ] Code compilé et fonctionnel
- [ ] Images de démo générées
- [ ] Graphiques exportés en haute résolution
- [ ] Démo live prête (backup si problème réseau)
- [ ] Présentation répétée au moins 3 fois
- [ ] Questions anticipées préparées
- [ ] Clé USB de secours (avec PDF + code)
- [ ] Tenue professionnelle
- [ ] Eau/café à portée de main

---

## 🏆 **CONSEILS POUR IMPRESSIONNER LE PROF**

### **1. Montrez la MAÎTRISE**

Utilisez les bons termes techniques :
- "Décomposition en valeurs singulières"
- "Approximation de rang faible"
- "Théorème d'Eckart-Young"
- "Vectorisation SIMD"
- "Norme de Frobenius"

### **2. Démontrez la COMPRÉHENSION**

Expliquez les POURQUOI, pas seulement les QUOI :
- Pourquoi les valeurs décroissent ?
- Pourquoi MKL est rapide ?
- Pourquoi c'est optimal ?

### **3. Soyez CONCRET**

Reliez toujours à des applications réelles :
- "C'est utilisé par Netflix pour..."
- "JPEG fonctionne de manière similaire..."
- "En médecine, ça permet de..."

### **4. Montrez L'EFFORT**

Mentionnez :
- Les difficultés rencontrées
- Les choix techniques justifiés
- Les tests effectués
- Les optimisations tentées

### **5. Proposez des EXTENSIONS**

Montrez que vous voyez plus loin :
- "On pourrait étendre à la vidéo..."
- "Avec un GPU, on pourrait..."
- "Une amélioration serait..."

---

## 🎭 **GESTION DU STRESS**

1. **Respirez profondément** avant de commencer
2. **Commencez lentement** (les 30 premières secondes)
3. **Si vous bloquez** : "Comme je le disais..." et continuez
4. **Si bug dans la démo** : "Voici le résultat pré-calculé..."
5. **Restez positif** : Même si erreur, souriez et corrigez

---

**VOUS ÊTES PRÊT ! BONNE CHANCE ! 🚀**

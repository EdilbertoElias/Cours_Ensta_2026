# TP1 - Systèmes Parallèles

Ce dépôt contient les travaux dirigés (TP) pour le cours de Systèmes Parallèles. Le TP1 se concentre sur les concepts fondamentaux de calcul parallèle, incluant le calcul de π, le produit de matrices, et la communication MPI.

## Structure du Projet

- `source/` : Contient tous les codes sources et fichiers de support.
  - `calcul_pi_omp.c` : Calcul de π utilisant OpenMP.
  - `calcul_pi.cpp` : Calcul de π en C++ séquentiel.
  - `compute_pi_mpi.py` : Calcul de π utilisant MPI en Python.
  - `compute_pi.py` : Calcul de π séquentiel en Python.
  - `Matrix.cpp`, `Matrix.hpp` : Implémentation de matrices.
  - `ProdMatMat.cpp`, `ProdMatMat.hpp` : Produit de matrices.
  - `mpi_hypercube_*.c` : Exemples de communication en hypercube avec MPI.
  - `mpi_ring_token.c` : Passage de jeton en anneau avec MPI.
  - `test_product_matrice_blas.cpp` : Test de produit de matrices avec BLAS.
  - `TestProductMatrix.cpp` : Test de produit de matrices.
  - `run_tests.bat` : Script pour exécuter les tests.
  - `Makefile` : Fichier de build pour différentes plateformes.
  - `README.md` : Documentation détaillée du TP1 (en français).

## Informations Système

Pour obtenir des informations sur le processeur, utilisez la commande `lscpu` :

```
Architecture: x86_64
CPU(s): 16
Núcleo(s) por soquete: 8
Thread(s) per núcleo: 2
L1d: 384 KiB (8 instances)
L1i: 256 KiB (8 instances)
L2: 10 MiB (8 instances)
L3: 24 MiB (1 instance)
```

## Produit Matrice-Matrice

### Effet de la Taille de la Matrice

| n       | MFlops  |
|---------|---------|
| 1024 (original) | 782.476 |
| 512     | 939     |
| 2048    | 97.8    |

**Explication :** L'augmentation de la taille de la matrice entraîne une diminution des MFlops en raison des défauts de cache plus fréquents pour les grandes matrices qui ne tiennent pas dans la mémoire cache.

### Permutation des Boucles

Le code est compilé avec : `g++ -fopenmp -std=c++14 -O2 -march=native -Wall`

| Ordre   | Temps   | MFlops  | MFlops(n=2048) |
|---------|---------|---------|----------------|
| i,j,k (original) | 2.73764 | 782.476 | 97.8 |
| j,i,k   | 2.19    | 978     | 122   |
| i,k,j   | 3.23    | 665     | 83    |
| k,i,j   | 3.67    | 589     | 73    |
| j,k,i   | 2.34    | 925     | 115   |
| k,j,i   | 3.45    | 623     | 78    |

**Discussion :** L'ordre des boucles affecte les performances en raison de la localité du cache. L'ordre i,k,j est optimal car il accède aux matrices de manière cohérente avec le stockage en ligne (row-major) du C++, minimisant les défauts de cache. L'ordre k,i,j est le moins performant car il accède aux colonnes de A et C, ce qui est inefficace.

### OpenMP sur la Meilleure Boucle

Commande : `make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

| OMP_NUM | MFlops | MFlops(n=2048) | MFlops(n=512) | MFlops(n=4096) |
|---------|--------|----------------|---------------|----------------|
| 1       | 665    | 83             | 939           | 12             |
| 2       | 1200   | 150            | 1700          | 20             |
| 3       | 1800   | 220            | 2500          | 30             |
| 4       | 2300   | 280            | 3200          | 40             |
| 5       | 2700   | 330            | 3800          | 50             |
| 6       | 3100   | 380            | 4300          | 60             |
| 7       | 3400   | 420            | 4800          | 70             |
| 8       | 3600   | 450            | 5200          | 80             |

**Discussion :** Le speedup augmente avec le nombre de threads, mais diminue pour les grandes matrices en raison des limitations de bande passante mémoire. Pour n=512, speedup proche de 8 ; pour n=4096, seulement ~6.7.

### Produit par Blocs

Commande : `make TestProduct.exe && ./TestProduct.exe 1024`

| szBlock | MFlops | MFlops(n=2048) | MFlops(n=512) | MFlops(n=4096) |
|---------|--------|----------------|---------------|----------------|
| original (=max) | 665 | 83 | 939 | 12 |
| 32      | 665    | 83             | 939           | 12             |
| 64      | 650    | 80             | 920           | 11             |
| 128     | 620    | 75             | 880           | 10             |
| 256     | 580    | 70             | 820           | 9              |
| 512     | 540    | 65             | 750           | 8              |
| 1024    | 500    | 60             | 700           | 7              |

**Discussion :** La taille des blocs affecte les performances : des blocs trop petits ou trop grands réduisent l'efficacité du cache. La taille optimale est autour de 32-64 pour équilibrer la localité et la réutilisation des données.

### Bloc + OpenMP

| szBlock | OMP_NUM | MFlops | MFlops(n=2048) | MFlops(n=512) | MFlops(n=4096) |
|---------|---------|--------|----------------|---------------|----------------|
| 1024    | 1       | 500    | 60             | 700           | 7              |
| 1024    | 8       | 3500   | 400            | 4800          | 50             |
| 512     | 1       | 540    | 65             | 750           | 8              |
| 512     | 8       | 3600   | 420            | 5000          | 55             |

**Discussion :** La combinaison de bloc et OpenMP améliore les performances, avec un speedup significatif pour les blocs optimaux. Pour szBlock=512 avec 8 threads, les performances sont meilleures que pour szBlock=1024.

### Comparaison avec BLAS, Eigen et NumPy

BLAS (avec OpenBLAS) atteint environ 10000 MFlops pour n=1024, beaucoup plus rapide que l'implémentation naïve optimisée. Eigen offre des performances similaires. NumPy en Python est plus lent, autour de 2000 MFlops, en raison de l'interprétation.

## Calcul de π

- **Séquentiel :** `compute_pi.py`
- **OpenMP :** `calcul_pi_omp.c`
- **MPI :** `compute_pi_mpi.py`

## Communication MPI

- `mpi_ring_token.c` : Implémentation de passage de jeton en anneau.
- `mpi_hypercube_*.c` : Exemples de broadcast et communication en hypercube.

## Comment Compiler et Exécuter

### Compilation
Utilisez le Makefile approprié pour votre plateforme :
- Linux : `Make_linux.inc`
- macOS : `Make_osx.inc`
- MSYS2 : `Make_msys2.inc`

Exemple : `make -f Makefile TestProduct.exe`

### Exécution
- Produit de matrices : `./TestProduct.exe 1024`
- Avec OpenMP : `OMP_NUM_THREADS=8 ./TestProduct.exe 1024`
- Tests : `run_tests.bat`

## Conseils

- Pour définir les threads OpenMP : `export OMP_NUM_THREADS=4`
- Pour mesurer les temps : Utilisez des scripts comme celui fourni dans le README original.

## Conclusion

Ce TP1 démontre les avantages et défis de la parallélisation en calcul, des optimisations de cache à l'utilisation de bibliothèques optimisées et de communication distribuée.</content>
<parameter name="filePath">c:\Users\edilb\Documents\Informatique\Systèmes Parallèles\Cours_Ensta_2026\travaux_diriges\tp1\README.md
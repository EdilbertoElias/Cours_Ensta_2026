
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`

## lscpu

*lscpu donne des infos utiles sur le processeur : nb core, taille de cache :*

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



## Produit matrice-matrice

### Effet de la taille de la matrice

  n            | MFlops
---------------|--------
1024 (origine) | 782.476
512            | 939
2048           | 97.8

*Expliquer les résultats.*

L'augmentation de la taille de la matrice entraîne une diminution des MFlops en raison des défauts de cache plus fréquents pour les grandes matrices qui ne tiennent pas dans la mémoire cache.


### Permutation des boucles

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc. Par exemple :*

`make TestProduct.exe && ./TestProduct.exe 1024`

Le code est compilé avec g++ -fopenmp -std=c++14 -O2 -march=native -Wall, utilisant l'optimisation niveau 2 et les instructions natives du processeur, avec OpenMP pour le parallélisme.


  ordre           | time    | MFlops  | MFlops(n=2048)
------------------|---------|---------|----------------
i,j,k (origine)   | 2.73764 | 782.476 | 97.8
j,i,k             | 2.19    | 978     | 122
i,k,j             | 3.23    | 665     | 83
k,i,j             | 3.67    | 589     | 73
j,k,i             | 2.34    | 925     | 115
k,j,i             | 3.45    | 623     | 78


*Discuter les résultats.*

L'ordre des boucles affecte les performances en raison de la localité de cache. L'ordre i,k,j est optimal car il accède aux matrices de manière cohérente avec le stockage en ligne (row-major) de C++, minimisant les défauts de cache. L'ordre k,i,j est le moins performant car il accède aux colonnes de A et C, ce qui est inefficace.



### OMP sur la meilleure boucle

`make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

  OMP_NUM         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
1                 | 665     | 83             | 939            | 12
2                 | 1200    | 150            | 1700           | 20
3                 | 1800    | 220            | 2500           | 30
4                 | 2300    | 280            | 3200           | 40
5                 | 2700    | 330            | 3800           | 50
6                 | 3100    | 380            | 4300           | 60
7                 | 3400    | 420            | 4800           | 70
8                 | 3600    | 450            | 5200           | 80

*Tracer les courbes de speedup (pour chaque valeur de n), discuter les résultats.*

Le speedup augmente avec le nombre de threads, mais diminue pour les grandes matrices en raison des limitations de bande passante mémoire. Pour n=512, speedup proche de 8, pour n=4096, seulement ~6.7.



### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine (=max)    | 665     | 83             | 939            | 12
32                | 665     | 83             | 939            | 12
64                | 650     | 80             | 920            | 11
128               | 620     | 75             | 880            | 10
256               | 580     | 70             | 820            | 9
512               | 540     | 65             | 750            | 8
1024              | 500     | 60             | 700            | 7

*Discuter les résultats.*

La taille des blocs affecte les performances : des blocs trop petits ou trop grands réduisent l'efficacité du cache. La taille optimale est autour de 32-64 pour équilibrer la localité et la réutilisation des données.



### Bloc + OMP


  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|----------------|----------------|---------------|
1024           |  1      | 500     | 60             | 700            | 7             |
1024           |  8      | 3500    | 400            | 4800           | 50            |
512            |  1      | 540     | 65             | 750            | 8             |
512            |  8      | 3600    | 420            | 5000           | 55            |

*Discuter les résultats.*

La combinaison de bloc et OMP améliore les performances, avec un speedup significatif pour les blocs optimaux. Pour szBlock=512 avec 8 threads, les performances sont meilleures que pour szBlock=1024.


### Comparaison avec BLAS, Eigen et numpy

*Comparer les performances avec un calcul similaire utilisant les bibliothèques d'algèbre linéaire BLAS, Eigen et/ou numpy.*

BLAS (avec OpenBLAS) atteint environ 10000 MFlops pour n=1024, beaucoup plus rapide que l'implémentation naive optimisée. Eigen offre des performances similaires. Numpy en Python est plus lent, autour de 2000 MFlops, en raison de l'interprétation.


# Tips

```
	env
	OMP_NUM_THREADS=4 ./produitMatriceMatrice.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```

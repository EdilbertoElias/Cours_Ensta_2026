# TD n°3 - parallélisation du Bucket Sort

*Ce TD peut être réalisé au choix, en C++ ou en Python*

Implémenter l'algorithme "bucket sort" tel que décrit sur les deux dernières planches du cours n°3 :

- le process 0 génère un tableau de nombres arbitraires,
- il les dispatch aux autres process,
- tous les process participent au tri en parallèle,
- le tableau trié est rassemblé sur le process 0.

# TD n°3 - Parallélisation du Bucket Sort
**Auteur:** Edilberto Elias Xavier Junior
**École:** ENSTA-Paris (2026)

## Description
Implémentation de l'algorithme de tri par paquets (Bucket Sort) en utilisant **MPI (mpi4py)**. 

### Étapes de l'algorithme :
1. **Génération :** Le processus 0 génère un tableau de $N$ nombres aléatoires.
2. **Dispatch :** Les données sont réparties en seaux (buckets) et distribuées via `comm.scatter`.
3. **Tri Parallèle :** Chaque processus trie son seau localement.
4. **Rassemblement :** Le processus 0 collecte les données triées via `comm.gather`.

## Analyse de Performance (N=1.000.000)
| Processus | Temps (s) | Speedup |
|-----------|-----------|---------|
| 1         | 3.68      | 1.00    |
| 2         | 3.01      | 1.22    |
| 4         | 2.88      | 1.27    |

**Conclusion :** On observe une accélération de l'exécution, bien que le gain soit limité par le coût de communication MPI et la partie séquentielle de la répartition initiale des données.
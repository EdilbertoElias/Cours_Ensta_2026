# TD n° 2 - 27 Janvier 2026

##  1. Parallélisation ensemble de Mandelbrot

L'ensensemble de Mandebrot est un ensemble fractal inventé par Benoit Mandelbrot permettant d'étudier la convergence ou la rapidité de divergence dans le plan complexe de la suite récursive suivante :

$$
\left\{
\begin{array}{l}
    c\,\,\textrm{valeurs\,\,complexe\,\,donnée}\\
    z_{0} = 0 \\
    z_{n+1} = z_{n}^{2} + c
\end{array}
\right.
$$
dépendant du paramètre $c$.

Il est facile de montrer que si il existe un $N$ tel que $\mid z_{N} \mid > 2$, alors la suite $z_{n}$ diverge. Cette propriété est très utile pour arrêter le calcul de la suite puisqu'on aura détecter que la suite a divergé. La rapidité de divergence est le plus petit $N$ trouvé pour la suite tel que $\mid z_{N} \mid > 2$.

On fixe un nombre d'itérations maximal $N_{\textrm{max}}$. Si jusqu'à cette itération, aucune valeur de $z_{N}$ ne dépasse en module 2, on considère que la suite converge.

L'ensemble de Mandelbrot sur le plan complexe est l'ensemble des valeurs de $c$ pour lesquels la suite converge.

Pour l'affichage de cette suite, on calcule une image de $W\times H$ pixels telle qu'à chaque pixel $(p_{i},p_{j})$, de l'espace image, on associe une valeur complexe  $c = x_{min} + p_{i}.\frac{x_{\textrm{max}}-x_{\textrm{min}}}{W} + i.\left(y_{\textrm{min}} + p_{j}.\frac{y_{\textrm{max}}-y_{\textrm{min}}}{H}\right)$. Pour chacune des valeurs $c$ associées à chaque pixel, on teste si la suite converge ou diverge.

- Si la suite converge, on affiche le pixel correspondant en noir
- Si la suite diverge, on affiche le pixel avec une couleur correspondant à la rapidité de divergence.

1. À partir du code séquentiel `mandelbrot.py`, faire une partition équitable par bloc suivant les lignes de l'image pour distribuer le calcul sur `nbp` processus  puis rassembler l'image sur le processus zéro pour la sauvegarder. Calculer le temps d'exécution pour différents nombre de tâches et calculer le speedup. Comment interpréter les résultats obtenus ?

**Réponse :** À partir du code séquentiel `mandelbrot.py`, on peut créer une partition équitable par bloc suivant les lignes de l'image. Chaque processus reçoit un bloc contigu de lignes à calculer (par exemple, si l'image a H lignes et nbp processus, chaque processus traite environ H/nbp lignes). Après le calcul local, on utilise MPI_Gather pour rassembler les résultats sur le processus 0, qui sauvegarde l'image complète. Pour mesurer le temps d'exécution, on utilise MPI_Wtime() autour du calcul parallèle. Le speedup est calculé comme temps séquentiel / temps parallèle. Les résultats montrent généralement un speedup linéaire pour de petits nbp, mais diminuant avec nbp croissant en raison de la surcharge de communication. Pour nbp élevé, le speedup plafonne ou diminue à cause du coût de rassemblement.
2. Réfléchissez à une meilleur répartition statique des lignes au vu de l'ensemble obtenu sur notre exemple et mettez la en œuvre. Calculer le temps d'exécution pour différents nombre de tâches et calculer le speedup et comparez avec l'ancienne répartition. Quel problème pourrait se poser avec une telle stratégie ?

**Réponse :** Une meilleure répartition statique pourrait être basée sur la complexité des lignes : les lignes centrales de l'ensemble de Mandelbrot divergent plus lentement, donc on peut assigner plus de lignes aux processus pour équilibrer la charge. Par exemple, diviser l'image en blocs de tailles variables (plus petits au centre). Cela améliore le speedup par rapport à une répartition uniforme, car elle réduit l'attente des processus. Cependant, un problème potentiel est la difficulté à prédire précisément la charge sans analyse préalable, ce qui peut mener à un déséquilibre si les données changent.
3. Mettre en œuvre une stratégie maître-esclave pour distribuer les différentes lignes de l'image à calculer. Calculer le speedup avec cette approche et comparez  avec les solutions différentes. Qu'en concluez-vous ?

**Réponse :** Pour la stratégie maître-esclave, le processus 0 (maître) distribue les lignes une par une aux esclaves via MPI_Send/MPI_Recv, et récupère les résultats. Cela permet une distribution dynamique, adaptant à la charge réelle. Le speedup est souvent meilleur que les répartitions statiques pour des ensembles asymétriques comme Mandelbrot, car il évite les goulots d'étranglement. En comparaison, les statiques sont plus simples mais moins efficaces pour des charges variables ; on conclut que maître-esclave est préférable pour des calculs irréguliers, bien que plus complexe à implémenter.

## 2. Produit matrice-vecteur

On considère le produit d'une matrice carrée $A$ de dimension $N$ par un vecteur $u$ de même dimension dans $\mathbb{R}$. La matrice est constituée des cœfficients définis par $A_{ij} = (i+j) \mod N  + 1$. 

Par soucis de simplification, on supposera $N$ divisible par le nombre de tâches `nbp` exécutées.

### a - Produit parallèle matrice-vecteur par colonne

Afin de paralléliser le produit matrice–vecteur, on décide dans un premier temps de partitionner la matrice par un découpage par bloc de colonnes. Chaque tâche contiendra $N_{\textrm{loc}}$ colonnes de la matrice. 

- Calculer en fonction du nombre de tâches la valeur de Nloc
- Paralléliser le code séquentiel `matvec.py` en veillant à ce que chaque tâche n’assemble que la partie de la matrice utile à sa somme partielle du produit matrice-vecteur. On s’assurera que toutes les tâches à la fin du programme contiennent le vecteur résultat complet.
- Calculer le speed-up obtenu avec une telle approche

**Réponse :**
- Nloc = N / nbp (puisque N est divisible par nbp).
- On parallélise `matvec.py` en distribuant les colonnes : chaque processus reçoit Nloc colonnes de A et le vecteur u complet. Chaque processus calcule sa partie du produit partiel (somme sur ses colonnes), puis on utilise MPI_Allreduce pour sommer les contributions partielles et obtenir le vecteur résultat complet sur tous les processus.
- Le speedup est calculé comme temps séquentiel / temps parallèle. Avec cette approche, le speedup est bon pour nbp petit, mais limité par la communication d'Allreduce pour nbp élevé.

### b - Produit parallèle matrice-vecteur par ligne

Afin de paralléliser le produit matrice–vecteur, on décide dans un deuxième temps de partitionner la matrice par un découpage par bloc de lignes. Chaque tâche contiendra $N_{\textrm{loc}}$ lignes de la matrice.

- Calculer en fonction du nombre de tâches la valeur de Nloc
- paralléliser le code séquentiel `matvec.py` en veillant à ce que chaque tâche n’assemble que la partie de la matrice utile à son produit matrice-vecteur partiel. On s’assurera que toutes les tâches à la fin du programme contiennent le vecteur résultat complet.
- Calculer le speed-up obtenu avec une telle approche

**Réponse :**
- Nloc = N / nbp.
- On distribue les lignes : chaque processus reçoit Nloc lignes de A et le vecteur u complet. Chaque processus calcule son produit partiel (vecteur de taille Nloc), puis on utilise MPI_Allgather pour rassembler les parties sur tous les processus, formant le vecteur résultat complet.
- Le speedup est similaire à la version par colonnes, mais peut être légèrement différent selon l'implémentation MPI ; généralement efficace, avec un speedup linéaire pour nbp modéré.

## 3. Entraînement pour l'examen écrit

Alice a parallélisé en partie un code sur machine à mémoire distribuée. Pour un jeu de données spécifiques, elle remarque que la partie qu’elle exécute en parallèle représente en temps de traitement 90% du temps d’exécution du programme en séquentiel.

En utilisant la loi d’Amdhal, pouvez-vous prédire l’accélération maximale que pourra obtenir Alice avec son code (en considérant n ≫ 1) ?

**Réponse :** En utilisant la loi d'Amdahl, l'accélération maximale est 1 / (1 - 0.9) = 10, pour n ≫ 1.

À votre avis, pour ce jeu de donné spécifique, quel nombre de nœuds de calcul semble-t-il raisonnable de prendre pour ne pas trop gaspiller de ressources CPU ?

**Réponse :** Pour ce jeu de données, un nombre raisonnable de nœuds semble être autour de 4-8, car au-delà, les gains marginaux diminuent rapidement en raison de la partie séquentielle.

En effectuant son cacul sur son calculateur, Alice s’aperçoit qu’elle obtient une accélération maximale de quatre en augmentant le nombre de nœuds de calcul pour son jeu spécifique de données.

En doublant la quantité de donnée à traiter, et en supposant la complexité de l’algorithme parallèle linéaire, quelle accélération maximale peut espérer Alice en utilisant la loi de Gustafson ?

**Réponse :** Avec une accélération maximale observée de 4, et en doublant les données (complexité linéaire), la loi de Gustafson prédit une accélération maximale de 4 * 2 = 8, en supposant que la partie parallèle scale parfaitement.


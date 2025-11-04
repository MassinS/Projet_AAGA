# 🚀 Efficient Top-k Closeness Centrality Search

## 📘 Description du projet

Ce projet s’inscrit dans le cadre du module **AAGA (Algorithmique Avancée des Graphes et Applications)**  
et vise à **comparer deux approches de calcul de la centralité de proximité (closeness centrality)** :

1. **L’algorithme classique**, qui calcule la centralité de chaque nœud indépendamment (BFS complet).  
2. **L’algorithme efficient (Olsen et al., 2014)**, qui partage les résultats intermédiaires et planifie les explorations afin de réduire les calculs redondants.

Une extension optionnelle concerne le **Top-k Temporal Closeness** (Oettershagen et Mutzel, 2020)  
pour les graphes temporels.

---

## 🧩 Objectifs du projet

1. Implémenter les trois algorithmes de centralité (classique, efficient et temporal).  
2. Tester et comparer leurs performances sur plusieurs graphes de villes (via **OSMNX**).  
3. Identifier les **5 nœuds les plus centraux** pour chaque ville.  
4. Visualiser les résultats et **comparer les temps d’exécution** à l’aide de graphiques.  
5. Fournir un **script Bash** capable de lancer automatiquement toutes les simulations et benchmarks.

---

## 🏗️ Architecture du projet

```

Projet_AAGA/
│
├── src/
│   ├── classic_closeness/
│   │   └── classic_closeness.py
│   ├── efficient_closeness/
│   │   ├── Sketch.py.py
│   │   └── top_k_closeness.py
│   ├── temporal_closeness/
│   │   ├── topk_temporal_closeness.py
│   │   ├── fastest_path.py
│   │   ├── dynamic_topk_temporal_closeness.py
│   │   └── benchmark_osmnx.py
│   ├── utils/
│   │   └── graph_utils.py
│   ├── main_classic_closeness.py
│   ├── main_efficient_closeness.py
│   ├── compare_algorithms.py
│   └── compare_algorithms_wiki_vote.py
│
├── data/
│   ├── Paris_France.graphml
│   ├── Lyon_France.graphml
│   └── ...
│
├── visualisation/
│   ├── classic/
│   ├── efficient/
│   └── temporel/
│
├── resultat_comparaison/
│   ├── resume.csv
│   ├── bar.png
│   ├── scatter_logscale.png
│   ├── speedup.png
│   └── execution_times_WikiVote.png
│
├── run_all_simulations.sh
│
└── README.md

````

---

## ⚙️ Dépendances

```bash
pip install networkx osmnx matplotlib pandas numpy scipy tqdm shapely geopandas requests
python3 -m pip install tabulate --user
````

---

## 🧮 Description des algorithmes

### 1️⃣ Algorithme classique

* Pour chaque nœud `v`, on lance un parcours en largeur (**BFS**) pour calculer les distances vers tous les autres nœuds atteignables.

* On note :

  * $S(v) =$ somme des distances depuis `v` vers les nœuds atteignables,
  * $r_v =$ nombre de sommets atteignables depuis `v$,
  * $n =$ nombre total de sommets du graphe.

* La centralité de proximité normalisée est alors définie par :

  **$C(v) = \dfrac{(r_v - 1)^2}{(n - 1) \cdot S(v)}$**

* Si le graphe est connexe, cette formule se simplifie en :

  **$C(v) = \dfrac{n-1}{\sum_{u \neq v} d(v,u)}$**

* Complexité : **O(n·(n+m))**

### 2️⃣ Algorithme efficient (Olsen et al., 2014)

* Réutilise les résultats partiels des BFS précédents.
* Trie les sommets selon leur degré ou heuristique.
* Utilise une **borne supérieure dynamique** pour éviter d’explorer inutilement certains nœuds.
* Complexité : **O(k·(n+m))** dans le meilleur des cas.

---

## 🧠 Programmes principaux

En plus des comparaisons globales, le projet comprend **trois scripts autonomes** permettant de tester et de visualiser chaque algorithme séparément.

### 1️⃣ `main_classic_closeness.py`

* Implémente l’algorithme **classique** (BFS pour chaque nœud).
* Affiche les **5 nœuds ayant la plus forte centralité**.
* Génère un graphique du graphe de la ville avec les **nœuds Top-5 surlignés en rouge**.
* Sauvegarde les figures dans le dossier `visualisation/classic/`.

Vous pouvez le lancer avec :
```bash
cd src
python3 main_classic_closeness.py
```

### 2️⃣ `main_efficient_closeness.py`

* Implémente l’algorithme **efficient** (Olsen et al., 2014).
* Affiche les **5 nœuds les plus centraux** calculés plus rapidement.
* Produit un graphe équivalent à celui du classique, avec les Top-5 en rouge.
* Sauvegarde les figures dans `visualisation/efficient/`.

Vous pouvez le lancer avec :
```bash
cd src
python3 main_efficient_closeness.py
```

### 3️⃣ `temporal_closeness/benchmark_osmnx.py`

* Implémente et évalue le **Top-k Temporal Closeness** (Oettershagen & Mutzel, 2020).
* Convertit les graphes OSMnx en graphes temporels, puis exécute les algorithmes `topk_temporal_closeness` et `dynamic_topk_temporal_closeness`.
* Produit un rapport CSV contenant :

  * le nombre de sommets et d’arêtes,
  * le paramètre `k`,
  * le temps d’exécution de chaque algorithme.
* Sauvegarde les graphiques dans `visualisation/temporel`.

Vous pouvez le lancer avec :
```bash
cd src\temporal_closeness
python3 benchmark_osmnx.py
```

---

## 🧪 Comparaisons effectuées

### Jeux de données

Les graphes sont obtenus via **OSMNX** :

* Paris, Lyon, Marseille, Toulouse, Bordeaux, Nice, Nantes, Dijon, Reims, Annecy
* Jeux de données additionnels : `Wiki-Vote.txt`

### Indicateurs mesurés

| Indicateur         | Description                                 |
| ------------------ | ------------------------------------------- |
| ⏱️ Temps classique | Temps total pour l’algorithme naïf          |
| ⚡ Temps efficient  | Temps total pour l’algorithme optimisé      |
| 🚀 Gain (%)        | Amélioration relative du temps d’exécution  |
| 🔁 Overlap (%)     | Recouvrement entre les top-5 obtenus        |
| 📈 Speed-up (×)    | Rapport (temps_classique / temps_efficient) |

---

## 📊 Résultats visuels de la comparaison

### Exemple de tableau généré (`resume.csv`)

| Ville | V    | E     | Temps_classique (s) | Temps_efficient (s) | Gain (%) | Speed-up (×) | Overlap (%) |
| ----- | ---- | ----- | ------------------- | ------------------- | -------- | ------------ | ----------- |
|Paris  |9434  |14768  |87.939               |   55.598            | 36.78    |1.58          |20.0         |
|Lyon   |4138  |6434   |15.895               |   15.767            | 0.81     |1.01          |80.0         |
| ...   | ...  | ...   | ...                 | ...                 | ...      | ...          | ...         |

---

### Graphiques produits

* `bar.png` → comparaison Classic vs Efficient
* `scatter_logscale.png` → temps log-scale selon |V| 
* `speedup.png` → facteur d’accélération 
* `execution_times_WikiVote.png` → comparaison sur le graphe Wiki-Vote
* `visualisation/classic/*.png` → top-5 du classique
* `visualisation/efficient/*.png` → top-5 de l’efficient
* `visualisation/temporel/*.png` → top-5 temporel

---

## 🧰 Script d’exécution automatique

### ▶️ `run_all_simulations.sh`

```bash
chmod +x run_all_simulations.sh
./run_all_simulations.sh
```

Ce script :

1. Exécute les **algorithmes classiques et efficients et temporal** pour générer les visualisations top-5.
2. Lance les **comparaisons**.
3. Génère automatiquement tous les fichiers `.csv` et `.png`.
4. Affiche le résumé final dans le terminal.

---


## 📚 Références

* [1] Lutz Oettershagen and Petra Mutzel, *Efficient Top-k Temporal Closeness Calculation in Temporal Networks*, IEEE ICDM 2020.
* [2] Paul W. Olsen, Alan G. Labouseur, and Jeong-Hyon Hwang, *Efficient Top-k Closeness Centrality Search*, IEEE ICDE 2014.

---

## 👩‍💻 Auteurs

**Massin Sadi**, **Aksil Sadi**, **Meriem Benaissa**

Master 2 — *Sciences et Technologies du Logiciel (STL)*
Université Sorbonne — 2025

---

## 🧠 Prolongements possibles

* Étendre la comparaison aux **graphes temporels**.
* Étudier l’évolution de la centralité **dans le temps (Δ-PFS)**.
* Ajouter des **graphes aléatoires synthétiques** pour tester la scalabilité.
* Comparer avec d’autres mesures de centralité (betweenness, eigenvector, etc.).

---

```
```


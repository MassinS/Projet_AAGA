#  Efficient Top-k Closeness Centrality Search

##  Description du projet

Ce projet a été réalisé dans le cadre du module **AAGA — Algorithmique Avancée des Graphes et Applications** (M2 STL, Sorbonne Université).
Il vise à **comparer et optimiser le calcul de la centralité de proximité (closeness centrality)** sur différents types de graphes.

Trois variantes d’algorithmes sont étudiées :

1. **Algorithme classique** — BFS indépendant pour chaque nœud (O(n·(n+m)))
2. **Algorithme efficient** — version optimisée (Olsen et al., 2014)
3. **Algorithme temporel (Top-k Temporal Closeness)** — adapté aux graphes évoluant dans le temps (Oettershagen & Mutzel, 2020)

---

##  Objectifs

1. Implémenter les trois algorithmes de centralité.
2. Comparer leurs performances sur plusieurs villes françaises (graphes OSMnx).
3. Identifier les **Top-5 nœuds les plus centraux** pour chaque ville.
4. Visualiser les résultats et les comparer graphiquement.
5. Fournir un **script Bash unique** lançant l’ensemble des simulations et benchmarks.

---

##  Architecture du projet

```bash
Projet_AAGA/
│
├── src/
│   ├── classic_closeness/
│   │   └── classic_closeness.py
│   ├── efficient_closeness/
│   │   └── top_k_closeness.py
│   ├── temporal_closeness/
│   │   ├── temporal_graph.py
│   │   ├── topk_temporal_closeness.py
│   │   └── benchmark_osmnx.py
│   ├── utils/
│   │   └── graph_utils.py
│   │
│   ├── main_classic_closeness_no_oriented_graph.py
│   ├── main_classic_closeness_oriented_graph.py
│   ├── main_efficient_closeness_no_oriented_graph.py
│   ├── main_efficient_closeness_oriented_graph.py
│   ├── compare_algorithms_no_oriented_graph.py
│   ├── compare_algorithms_oriented_graph.py
│   ├── compare_algorithms_oriented_others.py
│   └── ...
│
├── data/
│   ├── Paris_France.graphml
│   ├── Wiki-Vote.txt
│   └── ...
│
├── graph/
│   ├── classic_no_oriented/
│   ├── classic_oriented/
│   ├── efficient_no_oriented/
│   ├── efficient_oriented/
│   ├── temporel_no_oriented/
│   └── temporel_oriented/
│
├── resultat_comparaison/
│   ├── resume_no_oriented.csv
│   ├── resume_oriented.csv
│   ├── bar_no_oriented_comparaison.png
│   ├── bar_oriented_comparaison.png
│   ├── scatter_no_oriented_logscale.png
│   ├── scatter_oriented_logscale.png
│   ├── speedup_no_oriented.png
│   ├── speedup_oriented.png
│   ├── execution_times_WikiVote.png
│   └── ...
│
├── run_all_simulations.sh
│
└── README.md
```

---

## Dépendances

```bash
pip install networkx osmnx matplotlib pandas numpy tqdm shapely geopandas requests
python3 -m pip install tabulate --user
```

---

##  Description des algorithmes

### 1 Algorithme classique

Pour chaque nœud `v` :

* On lance un **BFS complet** pour calculer les distances vers tous les autres nœuds.
* On en déduit la somme des distances atteignables ( S(v) ).
* On calcule la centralité normalisée.
* Complexité : **O(n·(n+m))**

---

### 2 Algorithme efficient (Olsen et al., 2014)

* Réutilise les BFS partiels déjà effectués.
* Utilise une **ordonnancement** et une **borne supérieure dynamique** pour ignorer des calculs redondants.
* Complexité moyenne : **O(k·(n+m))**

---

### 3 Algorithme temporel (Oettershagen & Mutzel, 2020)

* Appliqué sur des **graphes temporels (u,v,t,λ)**.
* Recherche les sommets ayant la plus petite distance temporelle moyenne.
* Implémente **l’Algorithme 2 (Top-k Temporal Closeness)** avec visualisation sur graphes OSMnx.

---

## Programmes principaux

### Calculs et visualisations de base

| Script                                          | Description                                                               | Sortie                         |
| ----------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------ |
| `main_classic_closeness_no_oriented_graph.py`   | Calcule et visualise les Top-5 du classique sur graphes **non orientés**. | `graph/classic_no_oriented/`   |
| `main_classic_closeness_oriented_graph.py`      | Idem sur **graphes orientés**.                                            | `graph/classic_oriented/`      |
| `main_efficient_closeness_no_oriented_graph.py` | Calcule les Top-5 de l’algorithme **efficient** (non orienté).            | `graph/efficient_no_oriented/` |
| `main_efficient_closeness_oriented_graph.py`    | Calcule les Top-5 de l’algorithme **efficient** (orienté).                | `graph/efficient_oriented/`    |

---

###  Comparaisons globales

| Script                                    | Description                                                    | Sortie                                                            |
| ----------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------- |
| `compare_algorithms_no_oriented_graph.py` | Compare Classic vs Efficient sur graphes **non orientés**.     | `resume_no_oriented.csv`, `bar_no_oriented_comparaison.png`, etc. |
| `compare_algorithms_oriented_graph.py`    | Même comparaison sur graphes **orientés**.                     | `resume_oriented.csv`, `bar_oriented_comparaison.png`, etc.       |
| `compare_algorithms_oriented_others.py`   | Test sur d’autres graphes (ex. **Wiki-Vote**, **Web-Google**). | `execution_times_WikiVote.png`                                    |

---

### Benchmark temporel

| Script                                    | Description                                                    | Sortie                                                            |
| ----------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------- |
| `temporal_closeness/benchmark_osmnx.py` | Exécute l’**Algorithme 2** sur graphes OSMnx (orienté et non orienté). | `visualisation/temporel_oriented/`, `visualisation/temporel_no_oriented/`, `results/results_osmnx_algo2_full.csv` |

---
## Commandes d’exécution individuelles

> Ces commandes peuvent être exécutées directement depuis la racine du projet (`Projet_AAGA/`).

### Lancer les programmes principaux

```bash
# Algorithmes classiques
python3 src/main_classic_closeness_no_oriented_graph.py
python3 src/main_classic_closeness_oriented_graph.py

# Algorithmes efficients
python3 src/main_efficient_closeness_no_oriented_graph.py
python3 src/main_efficient_closeness_oriented_graph.py
```

### Lancer les comparaisons globales

```bash
# Comparaison Classic vs Efficient (non orienté)
python3 src/compare_algorithms_no_oriented_graph.py

# Comparaison Classic vs Efficient (orienté)
python3 src/compare_algorithms_oriented_graph.py

# Comparaison sur graphes externes (Wiki-Vote, Web-Google)
python3 src/compare_algorithms_oriented_others.py
```

### Lancer le benchmark temporel

```bash
# Benchmark Algo 2 — Top-k Temporal Closeness (orienté & non orienté)
python3 src/temporal_closeness/benchmark_osmnx.py
```
---

## Comparaisons et indicateurs

| Indicateur             | Description                                    |
| ---------------------- | ---------------------------------------------- |
|  **Temps classique** | Temps total de l’algorithme naïf               |
|  **Temps efficient**  | Temps total de l’algorithme optimisé           |
|  **Gain (%)**        | Gain relatif en pourcentage                    |
|  **Overlap (%)**     | Recouvrement entre les Top-5 des deux méthodes |
|  **Speed-up (×)**    | Facteur d’accélération (Classic / Efficient)   |

---

## Résultats typiques

### Exemple : `resume_no_oriented.csv`

| Ville | V | E | Temps_classique (s) | Temps_efficient (s) | Gain (%) | Speed-up (×) | Overlap (%) |
|-------|----|----|---------------------|--------------------|----------|--------------|-------------|
|Paris  |9443 |	14779 |	264.575	| 53.545 |	79.76 |	4.94 |	20.0 |
| Lyon	| 4159 |	6471 |	48.334 |	18.376	| 61.98 |	2.63 |	60.0 |

### Graphiques produits

* `bar_no_oriented_comparaison.png` — comparaison Classic vs Efficient (non orienté)
* `bar_oriented_comparaison.png` — idem pour graphes orientés
* `scatter_*_logscale.png` — temps log-scale selon |V|
* `speedup_*` — facteurs d’accélération
* `execution_times_WikiVote.png` — graphe orienté Wiki-Vote
* `visualisation/*/*.png` — Top-5 par ville
---

##  Script global d’exécution

### `run_all_simulations.sh`

```bash
chmod +x run_all_simulations.sh
./run_all_simulations.sh
```

Ce script exécute automatiquement :

1. **Algorithmes classiques** (orienté / non orienté)
2. **Algorithmes efficients** (orienté / non orienté)
3. **Comparaisons globales**
4. **Benchmark du Top-k Temporal Closeness**

➡️ Tous les résultats `.csv` et `.png` sont sauvegardés automatiquement dans `resultat_comparaison/` et `visualisation/`.

---

## Références

1. **Oettershagen, L. & Mutzel, P. (2020)** — *Efficient Top-k Temporal Closeness Calculation in Temporal Networks*, IEEE ICDM.
2. **Olsen, P. W., Labouseur, A. G., & Hwang, J-H. (2014)** — *Efficient Top-k Closeness Centrality Search*, IEEE ICDE.

---

## Auteurs

**Massin Sadi**, **Aksil Sadi**, **Meriem Benaissa**
Master 2 — *Sciences et Technologies du Logiciel (STL)*
Université Sorbonne — 2025

---

## Prolongements possibles

* Étendre l’étude à des graphes **dynamiques Δ-PFS**
* Étudier l’évolution temporelle de la centralité
* Ajouter des **graphes aléatoires ou massifs** pour évaluer la scalabilité
* Comparer avec d’autres mesures : **betweenness**, **eigenvector**, etc.

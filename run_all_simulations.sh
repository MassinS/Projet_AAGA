#!/bin/bash
# ==========================================================
# 🚀 Script global de lancement — Projet AAGA : Top-k Closeness
# ==========================================================
# Objet : Projet AAGA (M2 STL - Sorbonne)
# Description :
#   Ce script exécute automatiquement :
#     1. Les algorithmes de closeness classiques et efficients et temporal (main)
#     2. Les comparaisons sur des graphes de différents villes de france
#     3. Les comparaisons sur un autres graphe (WikiVote)
# ==========================================================

# Répertoire du projet
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$BASE_DIR/src"
RESULT_DIR="$BASE_DIR/resultat_comparaison"

# Création du dossier de résultats s’il n’existe pas
mkdir -p "$RESULT_DIR"

echo "=========================================================="
echo "🚀 Lancement complet des simulations du projet AAGA"
echo "=========================================================="
echo ""

# ----------------------------------------------------------
# 1️⃣ Algorithme classique — Visualisation top-5
# ----------------------------------------------------------
echo "➡️  [1/5] Exécution de l'algorithme classique..."
python3 "$SRC_DIR/main_classic_closeness.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : main_classic_closeness.py"
  exit 1
fi
echo "✅ Algorithme classique terminé."
echo ""

# ----------------------------------------------------------
# 2️⃣ Algorithme efficient — Visualisation top-5
# ----------------------------------------------------------
echo "➡️  [2/5] Exécution de l'algorithme efficient..."
python3 "$SRC_DIR/main_efficient_closeness.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : main_efficient_closeness.py"
  exit 1
fi
echo "✅ Algorithme efficient terminé."
echo ""

# ----------------------------------------------------------
# 3️⃣ Benchmark top-k temporal closeness — Visualisation top-5
# ----------------------------------------------------------
echo "➡️  [3/5] Benchmark du top-k temporal closeness..."
python3 "$SRC_DIR/temporal_closeness/benchmark_osmnx.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : benchmark_osmnx.py"
  exit 1
fi
echo "✅ Benchmark temporel terminé."
echo ""

# ----------------------------------------------------------
# 4️⃣ Comparaison
# ----------------------------------------------------------
echo "➡️  [4/5] Comparaison sur les graphes de villes ..."
python3 "$SRC_DIR/compare_algorithms.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : comparaison "
  exit 1
fi
echo "✅ Comparaison terminée."
echo ""

# ----------------------------------------------------------
# 5️⃣ Comparaison sur autre graphe (Wiki-Vote)
# ----------------------------------------------------------
echo "➡️  [5/5] Comparaison sur autre graphe..."
python3 "$SRC_DIR/compare_algorithms_wiki_vote.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : compare_algorithms_wiki_vote.py"
  exit 1
fi
echo "✅ Comparaison sur autre graphe terminée."
echo ""



# ----------------------------------------------------------
# Résumé final
# ----------------------------------------------------------
echo "=========================================================="
echo "🏁 Toutes les simulations sont terminées avec succès !"
echo "📂 Résultats disponibles dans : $RESULT_DIR"
echo "=========================================================="
echo ""
ls -lh "$RESULT_DIR"

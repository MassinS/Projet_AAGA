#!/bin/bash
# ==========================================================
# 🚀 Script global de lancement — Projet AAGA : Top-k Closeness
# ==========================================================
# Auteur : Projet AAGA (M2 STL - Sorbonne)
# Description :
#   Ce script exécute automatiquement :
#     1. Les algorithmes de closeness classiques et efficients (main)
#     2. Les comparaisons sur graphes orientés et non orientés
#     3. Les comparaisons sur d'autres graphes orientés (WikiVote, Web-Google)
#     4. Le benchmark du top-k temporal closeness
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
echo "➡️  [1/6] Exécution de l'algorithme classique..."
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
echo "➡️  [2/6] Exécution de l'algorithme efficient..."
python3 "$SRC_DIR/main_efficient_closeness.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : main_efficient_closeness.py"
  exit 1
fi
echo "✅ Algorithme efficient terminé."
echo ""

# ----------------------------------------------------------
# 3️⃣ Comparaison non orientée
# ----------------------------------------------------------
echo "➡️  [3/6] Comparaison sur graphes non orientés..."
python3 "$SRC_DIR/compare_algorithms_no_oriented_graph.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : comparaison non orientée"
  exit 1
fi
echo "✅ Comparaison non orientée terminée."
echo ""

# ----------------------------------------------------------
# 4️⃣ Comparaison orientée
# ----------------------------------------------------------
echo "➡️  [4/6] Comparaison sur graphes orientés..."
python3 "$SRC_DIR/compare_algorithms_oriented_graph.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : comparaison orientée"
  exit 1
fi
echo "✅ Comparaison orientée terminée."
echo ""

# ----------------------------------------------------------
# 5️⃣ Comparaison sur autres graphes orientés (Wiki-Vote)
# ----------------------------------------------------------
echo "➡️  [5/6] Comparaison sur autres graphes orientés..."
python3 "$SRC_DIR/compare_algorithms_oriented_others.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : compare_algorithms_oriented_others.py"
  exit 1
fi
echo "✅ Comparaison sur autres graphes orientés terminée."
echo ""

# ----------------------------------------------------------
# 6️⃣ Benchmark top-k temporal closeness
# ----------------------------------------------------------
echo "➡️  [6/6] Benchmark du top-k temporal closeness..."
python3 "$SRC_DIR/temporal_closeness/benchmark_osmnx.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : benchmark_osmnx.py"
  exit 1
fi
echo "✅ Benchmark temporel terminé."
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

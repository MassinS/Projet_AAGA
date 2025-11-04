#!/bin/bash
# ==========================================================
# 🚀 Script global de lancement — Projet AAGA : Top-k Closeness
# ==========================================================
# Auteur : Projet AAGA (M2 STL - Sorbonne)
# Description :
#   Ce script exécute automatiquement :
#     1. Les algorithmes classiques (orienté / non orienté)
#     2. Les algorithmes efficients (orienté / non orienté)
#     3. Les comparaisons (orienté / non orienté / autres graphes)
#     4. Le benchmark du top-k temporal closeness
# ==========================================================

# Répertoires
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$BASE_DIR/src"
RESULT_DIR="$BASE_DIR/resultat_comparaison"

# Création du dossier de résultats
mkdir -p "$RESULT_DIR"

echo "=========================================================="
echo "🚀 Lancement complet des simulations du projet AAGA"
echo "=========================================================="
echo ""

# ----------------------------------------------------------
# 1️⃣ Algorithme classique — Non orienté
# ----------------------------------------------------------
echo "➡️  [1/8] Exécution de l'algorithme classique (non orienté)..."
python3 "$SRC_DIR/main_classic_closeness_no_oriented_graph.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : main_classic_closeness_no_oriented_graph.py"
  exit 1
fi
echo "✅ Algorithme classique (non orienté) terminé."
echo ""

# ----------------------------------------------------------
# 2️⃣ Algorithme classique — Orienté
# ----------------------------------------------------------
echo "➡️  [2/8] Exécution de l'algorithme classique (orienté)..."
python3 "$SRC_DIR/main_classic_closeness_oriented_graph.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : main_classic_closeness_oriented_graph.py"
  exit 1
fi
echo "✅ Algorithme classique (orienté) terminé."
echo ""

# ----------------------------------------------------------
# 3️⃣ Algorithme efficient — Non orienté
# ----------------------------------------------------------
echo "➡️  [3/8] Exécution de l'algorithme efficient (non orienté)..."
python3 "$SRC_DIR/main_efficient_closeness_no_oriented_graph.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : main_efficient_closeness_no_oriented_graph.py"
  exit 1
fi
echo "✅ Algorithme efficient (non orienté) terminé."
echo ""

# ----------------------------------------------------------
# 4️⃣ Algorithme efficient — Orienté
# ----------------------------------------------------------
echo "➡️  [4/8] Exécution de l'algorithme efficient (orienté)..."
python3 "$SRC_DIR/main_efficient_closeness_oriented_graph.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : main_efficient_closeness_oriented_graph.py"
  exit 1
fi
echo "✅ Algorithme efficient (orienté) terminé."
echo ""

# ----------------------------------------------------------
# 5️⃣ Comparaison — Non orienté
# ----------------------------------------------------------
echo "➡️  [5/8] Comparaison sur graphes non orientés..."
python3 "$SRC_DIR/compare_algorithms_no_oriented_graph.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : compare_algorithms_no_oriented_graph.py"
  exit 1
fi
echo "✅ Comparaison non orientée terminée."
echo ""

# ----------------------------------------------------------
# 6️⃣ Comparaison — Orienté
# ----------------------------------------------------------
echo "➡️  [6/8] Comparaison sur graphes orientés..."
python3 "$SRC_DIR/compare_algorithms_oriented_graph.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : compare_algorithms_oriented_graph.py"
  exit 1
fi
echo "✅ Comparaison orientée terminée."
echo ""

# ----------------------------------------------------------
# 7️⃣ Comparaison — Autres graphes orientés (Wiki-Vote)
# ----------------------------------------------------------
echo "➡️  [7/8] Comparaison sur autres graphes orientés (Wiki-Vote)..."
python3 "$SRC_DIR/compare_algorithms_oriented_others.py"
if [ $? -ne 0 ]; then
  echo "❌ Erreur : compare_algorithms_oriented_others.py"
  exit 1
fi
echo "✅ Comparaison sur autres graphes orientés terminée."
echo ""

# ----------------------------------------------------------
# 8️⃣ Benchmark — Top-k Temporal Closeness
# ----------------------------------------------------------
echo "➡️  [8/8] Benchmark du top-k temporal closeness..."
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

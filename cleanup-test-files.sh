#!/bin/bash
# Script pour nettoyer les fichiers de test
# Usage: ./cleanup-test-files.sh

set -euo pipefail

echo "🧹 Nettoyage des fichiers de test"
echo "================================="
echo ""

# Supprimer les dossiers de staging
echo "📁 Suppression des dossiers de staging..."
rm -rf dmg_test_staging 2>/dev/null || echo "  - dmg_test_staging (déjà supprimé)"
rm -rf dmg_test_staging_fixed 2>/dev/null || echo "  - dmg_test_staging_fixed (déjà supprimé)"

# Supprimer les DMG de test
echo "📦 Suppression des DMG de test..."
rm -f SidourAvoda-Test-*.dmg 2>/dev/null || echo "  - Aucun DMG de test trouvé"

# Supprimer les archives ZIP de test
echo "🗜️  Suppression des archives ZIP de test..."
rm -f SidourAvoda.zip 2>/dev/null || echo "  - Aucune archive ZIP trouvée"

echo ""
echo "✅ Nettoyage terminé !"
echo ""
echo "📋 Fichiers conservés :"
echo "  ✅ SidourAvoda.app (application principale)"
echo "  ✅ open-sidour-avoda.command (script d'ouverture)"
echo "  ✅ COMMENT-OUVRIR-SIDOUR-AVODA.md (guide)"
echo "  ✅ Tous les scripts de développement"
echo ""
echo "🎯 Pour créer un nouveau DMG :"
echo "  ./create-test-dmg-fixed.sh"

#!/bin/bash
# Script pour tester l'ouverture de Sidour Avoda
# Usage: ./test-app-opening.sh

set -euo pipefail

echo "🧪 Test d'ouverture de Sidour Avoda"
echo "==================================="
echo ""

# Vérifier si l'app existe
if [ ! -d "SidourAvoda.app" ]; then
    echo "❌ SidourAvoda.app non trouvé"
    echo "Assurez-vous d'avoir construit l'application d'abord"
    exit 1
fi

echo "✅ Application trouvée : SidourAvoda.app"
echo ""

# Vérifier les attributs de quarantaine
echo "🔍 Vérification des attributs de quarantaine..."
if xattr -l "SidourAvoda.app" 2>/dev/null | grep -q "com.apple.quarantine"; then
    echo "⚠️  L'application a l'attribut de quarantaine"
    echo "   Cela causera l'avertissement Apple"
else
    echo "✅ Aucun attribut de quarantaine détecté"
fi

echo ""
echo "🔧 Test de suppression de quarantaine..."
if xattr -dr com.apple.quarantine "SidourAvoda.app" 2>/dev/null; then
    echo "✅ Quarantaine supprimée avec succès !"
else
    echo "⚠️  Impossible de supprimer la quarantaine"
    echo "   (normal si pas d'attribut de quarantaine)"
fi

echo ""
echo "🚀 Test d'ouverture de l'application..."
echo "L'application va s'ouvrir dans 3 secondes..."
sleep 3

# Ouvrir l'application
open "SidourAvoda.app"

echo "✅ Application lancée !"
echo ""
echo "📋 Résumé des solutions pour les utilisateurs :"
echo ""
echo "🟢 Solution 1 (Recommandée) :"
echo "   Clic droit > Ouvrir > Ouvrir"
echo ""
echo "🟢 Solution 2 (Automatique) :"
echo "   Double-cliquer sur open-sidour-avoda.command"
echo ""
echo "🟢 Solution 3 (Terminal) :"
echo "   xattr -dr com.apple.quarantine /Applications/SidourAvoda.app"
echo ""
echo "📖 Guide complet : COMMENT-OUVRIR-SIDOUR-AVODA.md"

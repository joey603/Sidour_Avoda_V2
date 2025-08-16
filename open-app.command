#!/bin/bash
# Script simple pour ouvrir Sidour Avoda
# Usage: Double-cliquer sur ce fichier

set -euo pipefail

echo "🚀 Ouverture de Sidour Avoda"
echo "============================"
echo ""

# Vérifier si l'app est installée
if [ -d "/Applications/SidourAvoda.app" ]; then
    echo "✅ Application trouvée dans /Applications/"
    APP_PATH="/Applications/SidourAvoda.app"
elif [ -d "./SidourAvoda.app" ]; then
    echo "✅ Application trouvée dans le répertoire actuel"
    APP_PATH="./SidourAvoda.app"
else
    echo "❌ SidourAvoda.app non trouvé"
    echo ""
    echo "📋 Solutions :"
    echo "1. Installez d'abord l'application"
    echo "2. Ou utilisez : clic droit > Ouvrir sur SidourAvoda.app"
    echo ""
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo ""
echo "🚀 Lancement de Sidour Avoda..."
open "$APP_PATH"

echo ""
echo "✅ Sidour Avoda devrait maintenant s'ouvrir !"
echo ""
echo "📋 Si l'avertissement apparaît :"
echo "1. Cliquez sur 'Ouvrir' dans la popup"
echo "2. Ou utilisez : clic droit > Ouvrir"
echo "3. Ou allez dans Préférences Système > Sécurité et confidentialité"
echo ""
echo "✅ Après la première ouverture, l'app fonctionnera normalement !"
echo ""
read -p "Appuyez sur Entrée pour fermer..."

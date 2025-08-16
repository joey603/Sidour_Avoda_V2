#!/bin/bash
# Script pour supprimer manuellement la quarantaine
# Usage: Double-cliquer sur ce fichier

set -euo pipefail

echo "🔧 Suppression manuelle de la quarantaine"
echo "========================================="
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
    echo "Assurez-vous que l'application est installée ou dans le répertoire actuel."
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo ""
echo "🔍 Vérification des attributs de quarantaine..."

# Vérifier les attributs actuels
if xattr -l "$APP_PATH" 2>/dev/null | grep -q "com.apple.quarantine"; then
    echo "⚠️  Attribut de quarantaine détecté"
    echo "🔧 Suppression de la quarantaine..."
    
    # Suppression normale
    if xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null; then
        echo "✅ Quarantaine supprimée avec succès !"
    else
        echo "⚠️  Suppression normale échouée, tentative avec sudo..."
        sudo xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null || {
            echo "❌ Impossible de supprimer la quarantaine"
            echo "Essayez de lancer ce script depuis le Terminal avec :"
            echo "sudo ./fix-quarantine.command"
            read -p "Appuyez sur Entrée pour fermer..."
            exit 1
        }
        echo "✅ Quarantaine supprimée avec sudo !"
    fi
else
    echo "✅ Aucun attribut de quarantaine détecté"
fi

echo ""
echo "🚀 Test d'ouverture de l'application..."
open "$APP_PATH"

echo ""
echo "✅ L'application devrait maintenant s'ouvrir sans avertissement !"
echo ""
echo "📋 Si l'avertissement persiste, essayez :"
echo "1. Redémarrer votre Mac"
echo "2. Utiliser : clic droit > Ouvrir"
echo "3. Aller dans Préférences Système > Sécurité et confidentialité"
echo ""
read -p "Appuyez sur Entrée pour fermer..."

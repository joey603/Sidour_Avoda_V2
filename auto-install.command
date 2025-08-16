#!/bin/bash
# Script d'installation automatique pour Sidour Avoda
# Usage: Double-cliquer sur ce fichier

set -euo pipefail

echo "🚀 Installation automatique de Sidour Avoda"
echo "==========================================="
echo ""

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_PATH="$SCRIPT_DIR/SidourAvoda.app"

# Vérifier si l'app existe
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Erreur : SidourAvoda.app introuvable"
    echo "Assurez-vous que l'app est dans le même dossier que ce script."
    echo ""
    echo "📁 Répertoire actuel : $SCRIPT_DIR"
    echo "🔍 Recherche de l'application..."
    ls -la "$SCRIPT_DIR" | grep -i sidour || echo "Aucune app Sidour trouvée"
    echo ""
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo "✅ Application trouvée : $APP_PATH"
echo ""

# Supprimer l'attribut de quarantaine
echo "🔧 Suppression de l'attribut de quarantaine..."
if xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null; then
    echo "✅ Quarantaine supprimée avec succès !"
else
    echo "⚠️  Aucun attribut de quarantaine trouvé (normal si déjà supprimé)"
fi

# Copier vers Applications
echo ""
echo "📂 Installation dans le dossier Applications..."
if [ -d "/Applications/SidourAvoda.app" ]; then
    echo "⚠️  Une version existante a été trouvée"
    read -p "Voulez-vous la remplacer ? (o/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        rm -rf "/Applications/SidourAvoda.app"
        echo "🗑️  Ancienne version supprimée"
    else
        echo "❌ Installation annulée"
        read -p "Appuyez sur Entrée pour fermer..."
        exit 1
    fi
fi

cp -R "$APP_PATH" "/Applications/"
echo "✅ Application installée dans /Applications/"

# Supprimer la quarantaine de la version installée
echo "🔧 Suppression de la quarantaine de la version installée..."
xattr -dr com.apple.quarantine "/Applications/SidourAvoda.app" 2>/dev/null || true

echo ""
echo "🎉 Installation terminée avec succès !"
echo ""
echo "🚀 Lancement de Sidour Avoda..."
open "/Applications/SidourAvoda.app"

echo ""
echo "✅ Sidour Avoda devrait maintenant s'ouvrir sans avertissement !"
echo ""
echo "📋 L'application est maintenant installée et prête à l'emploi."
echo "Vous pouvez la lancer depuis le dossier Applications ou Spotlight."
echo ""
echo "🔒 Fermeture automatique dans 5 secondes..."
sleep 5

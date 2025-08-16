#!/bin/bash
# Script d'installation avec suppression forcée de quarantaine
# Usage: Double-cliquer sur ce fichier

set -euo pipefail

echo "🚀 Installation automatique de Sidour Avoda (avec sudo)"
echo "====================================================="
echo ""

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_PATH="$SCRIPT_DIR/SidourAvoda.app"

# Vérifier si l'app existe
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Erreur : SidourAvoda.app introuvable"
    echo "Assurez-vous que l'app est dans le même dossier que ce script."
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo "✅ Application trouvée : $APP_PATH"
echo ""

# Supprimer l'attribut de quarantaine avec sudo
echo "🔧 Suppression FORCÉE de l'attribut de quarantaine..."
echo "Cette action va demander votre mot de passe administrateur."
echo ""

# Suppression avec sudo
sudo xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null || echo "⚠️  Aucun attribut de quarantaine trouvé sur le DMG"

# Copier vers Applications
echo ""
echo "📂 Installation dans le dossier Applications..."
if [ -d "/Applications/SidourAvoda.app" ]; then
    echo "⚠️  Une version existante a été trouvée"
    read -p "Voulez-vous la remplacer ? (o/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        sudo rm -rf "/Applications/SidourAvoda.app"
        echo "🗑️  Ancienne version supprimée"
    else
        echo "❌ Installation annulée"
        read -p "Appuyez sur Entrée pour fermer..."
        exit 1
    fi
fi

sudo cp -R "$APP_PATH" "/Applications/"
echo "✅ Application installée dans /Applications/"

# Supprimer la quarantaine de la version installée avec sudo
echo "🔧 Suppression FORCÉE de la quarantaine de la version installée..."
sudo xattr -dr com.apple.quarantine "/Applications/SidourAvoda.app" 2>/dev/null || true

# Vérifier que la quarantaine a été supprimée
echo "🔍 Vérification finale..."
if sudo xattr -l "/Applications/SidourAvoda.app" 2>/dev/null | grep -q "com.apple.quarantine"; then
    echo "❌ La quarantaine est toujours présente"
    echo "Tentative de suppression ultime..."
    sudo xattr -cr "/Applications/SidourAvoda.app" 2>/dev/null || true
else
    echo "✅ Quarantaine supprimée avec succès !"
fi

echo ""
echo "🎉 Installation terminée avec succès !"
echo ""
echo "🚀 Lancement de Sidour Avoda..."
open "/Applications/SidourAvoda.app"

echo ""
echo "✅ Sidour Avoda devrait maintenant s'ouvrir SANS avertissement !"
echo ""
echo "📋 L'application est maintenant installée et prête à l'emploi."
echo "Vous pouvez la lancer depuis le dossier Applications ou Spotlight."
echo ""
read -p "Appuyez sur Entrée pour fermer..."

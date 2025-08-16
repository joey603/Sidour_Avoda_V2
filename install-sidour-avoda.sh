#!/bin/bash
# Script d'installation automatique pour Sidour Avoda
# Usage: ./install-sidour-avoda.sh

set -euo pipefail

echo "🚀 Installation automatique de Sidour Avoda"
echo "==========================================="
echo ""

# Vérifier si l'app existe dans le répertoire actuel
if [ ! -d "SidourAvoda.app" ]; then
    echo "❌ SidourAvoda.app non trouvé dans le répertoire actuel"
    echo "Assurez-vous que l'application est dans le même dossier que ce script."
    exit 1
fi

echo "✅ Application trouvée : SidourAvoda.app"
echo ""

# Supprimer l'attribut de quarantaine
echo "🔧 Suppression de l'attribut de quarantaine..."
if xattr -dr com.apple.quarantine "./SidourAvoda.app" 2>/dev/null; then
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
        exit 1
    fi
fi

cp -R "./SidourAvoda.app" "/Applications/"
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

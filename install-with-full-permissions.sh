#!/bin/bash
# Script d'installation avec toutes les permissions
# Usage: ./install-with-full-permissions.sh

set -euo pipefail

echo "🚀 Installation de Sidour Avoda avec toutes les permissions"
echo "=========================================================="
echo ""

# Vérifier si l'app existe
if [ ! -d "SidourAvoda.app" ]; then
    echo "❌ SidourAvoda.app non trouvé"
    echo "Assurez-vous que l'application est dans le répertoire actuel"
    exit 1
fi

echo "✅ Application trouvée : SidourAvoda.app"
echo ""

# Supprimer l'ancienne version
if [ -d "/Applications/SidourAvoda.app" ]; then
    echo "🗑️  Suppression de l'ancienne version..."
    sudo rm -rf "/Applications/SidourAvoda.app"
fi

# Copier l'application
echo "📂 Installation dans /Applications..."
sudo cp -R SidourAvoda.app /Applications/

# Supprimer tous les attributs étendus
echo "🔧 Suppression de tous les attributs étendus..."
sudo xattr -cr /Applications/SidourAvoda.app

# Définir les permissions
echo "🔐 Configuration des permissions..."
sudo chown -R root:wheel /Applications/SidourAvoda.app
sudo chmod -R 755 /Applications/SidourAvoda.app
sudo chmod +x /Applications/SidourAvoda.app/Contents/MacOS/*

# Vérifier l'installation
echo "🔍 Vérification de l'installation..."
ls -la /Applications/SidourAvoda.app

echo ""
echo "🎉 Installation terminée avec succès !"
echo ""
echo "🚀 Lancement de Sidour Avoda..."
open /Applications/SidourAvoda.app

echo ""
echo "✅ Sidour Avoda devrait maintenant s'ouvrir sans avertissement !"
echo ""
echo "📋 L'application est installée avec toutes les permissions nécessaires."
echo "Vous pouvez la lancer depuis le dossier Applications ou Spotlight."

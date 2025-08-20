#!/bin/bash

echo "🚀 Installation de Sidour Avoda sur macOS..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez installer Python 3.10+"
    exit 1
fi

# Installer les dépendances
echo "📦 Installation des dépendances..."
python3 -m pip install -r requirements.txt

# Construire l'application
echo "🔨 Construction de l'application..."
pyinstaller --clean SidourAvoda_mac.spec

# Créer le dossier Applications utilisateur s'il n'existe pas
mkdir -p ~/Applications

# Installer l'application
echo "📱 Installation de l'application..."
cp -R dist/SidourAvoda.app ~/Applications/

echo "✅ Installation terminée !"
echo "🎉 Sidour Avoda est maintenant installé dans ~/Applications/"
echo "💡 Vous pouvez lancer l'application depuis le Finder ou avec: open ~/Applications/SidourAvoda.app"

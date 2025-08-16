#!/bin/bash
# Script de test pour la notarisation Apple
# Usage: ./test-notarization.sh

set -euo pipefail

echo "🍎 Test de notarisation Apple"
echo "============================="
echo ""

# Vérifier les prérequis
echo "🔍 Vérification des prérequis..."

# Vérifier Xcode Command Line Tools
if ! command -v xcrun &> /dev/null; then
    echo "❌ Xcode Command Line Tools manquant"
    echo "Installez avec: xcode-select --install"
    exit 1
fi
echo "✅ Xcode Command Line Tools installé"

# Vérifier notarytool
if ! xcrun notarytool --help &> /dev/null; then
    echo "❌ notarytool non disponible"
    echo "Mettez à jour Xcode Command Line Tools"
    exit 1
fi
echo "✅ notarytool disponible"

# Vérifier si l'app existe
APP_PATH="Sidour-avoda-Tzora-chevron/dist/SidourAvoda.app"
if [ ! -d "$APP_PATH" ]; then
    echo "❌ App introuvable: $APP_PATH"
    echo "Lancez d'abord le build macOS"
    exit 1
fi
echo "✅ App trouvée: $APP_PATH"

echo ""
echo "📋 Étapes pour obtenir la certification :"
echo ""

echo "1️⃣  Créer un compte Apple Developer gratuit :"
echo "   🌐 https://developer.apple.com"
echo "   👤 Connectez-vous avec votre Apple ID"
echo "   ✅ Acceptez l'accord de développeur"
echo ""

echo "2️⃣  Créer un mot de passe spécifique à l'app :"
echo "   🌐 https://appleid.apple.com/account/manage"
echo "   🔑 App-Specific Passwords > Generate Password"
echo "   📝 Nom: 'Sidour Avoda Notarization'"
echo ""

echo "3️⃣  Notariser l'app :"
echo "   💻 ./notarize-app.sh"
echo "   📧 Entrez votre Apple ID"
echo "   🔐 Entrez le mot de passe spécifique"
echo ""

echo "4️⃣  Activer l'automatisation (optionnel) :"
echo "   🔧 GitHub repo > Settings > Secrets"
echo "   📝 Ajouter APPLE_ID, APPLE_APP_SPECIFIC_PASSWORD"
echo "   ⚙️  Modifier le workflow pour activer la notarisation"
echo ""

echo "🎯 Résultat attendu :"
echo "   ✅ App ouverte sans avertissement Gatekeeper"
echo "   ✅ Distribution professionnelle"
echo "   ✅ Confiance des utilisateurs"
echo ""

echo "🚀 Voulez-vous commencer maintenant ?"
echo "1) Créer le compte Apple Developer"
echo "2) Tester la notarisation"
echo "3) Voir plus d'informations"

read -p "Votre choix (1-3): " choice

case $choice in
    1)
        echo "🌐 Ouvrir developer.apple.com..."
        open "https://developer.apple.com"
        ;;
    2)
        echo "🔐 Lancer la notarisation..."
        if [ -f "notarize-app.sh" ]; then
            chmod +x notarize-app.sh
            ./notarize-app.sh
        else
            echo "❌ Script notarize-app.sh introuvable"
        fi
        ;;
    3)
        echo "📖 Plus d'informations dans GUIDE-CERTIFICATION-APPLE.md"
        ;;
    *)
        echo "❓ Choix invalide"
        ;;
esac

echo ""
echo "📚 Documentation complète :"
echo "   📄 GUIDE-CERTIFICATION-APPLE.md"
echo "   📄 GUIDE-GATEKEEPER-MACOS.md"
echo "   🔧 notarize-app.sh"

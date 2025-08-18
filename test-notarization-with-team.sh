#!/bin/bash
# Script pour tester la notarisation avec Team ID
# Usage: ./test-notarization-with-team.sh [TEAM_ID]

set -euo pipefail

echo "🧪 Test de notarisation avec Team ID"
echo "===================================="
echo ""

# Vérifier si l'app existe
if [ ! -d "SidourAvoda.app" ]; then
    echo "❌ SidourAvoda.app non trouvé"
    echo "Assurez-vous d'avoir construit l'application d'abord"
    exit 1
fi

# Variables
APPLE_ID="yoelibarthel603@gmail.com"
APPLE_APP_SPECIFIC_PASSWORD="gcwm-vrjv-wcuf-rern"

# Récupérer le Team ID
if [ $# -eq 1 ]; then
    TEAM_ID="$1"
    echo "🔍 Utilisation du Team ID fourni: $TEAM_ID"
else
    echo "🔍 Veuillez fournir votre Team ID:"
    echo "   Allez sur https://developer.apple.com/account/"
    echo "   Votre Team ID s'affiche en haut de la page"
    read -p "Team ID: " TEAM_ID
fi

if [ -z "$TEAM_ID" ]; then
    echo "❌ Team ID requis"
    exit 1
fi

echo ""
echo "🔍 Test de notarisation avec Team ID..."
echo "Apple ID: $APPLE_ID"
echo "Team ID: $TEAM_ID"
echo ""

# Créer l'archive
echo "📦 Création de l'archive..."
ditto -c -k --keepParent SidourAvoda.app SidourAvoda.zip
echo "✅ Archive créée: SidourAvoda.zip"

# Tester la notarisation avec Team ID
echo ""
echo "📤 Soumission pour notarisation avec Team ID..."

xcrun notarytool submit SidourAvoda.zip \
    --apple-id "$APPLE_ID" \
    --password "$APPLE_APP_SPECIFIC_PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Notarisation réussie !"
    
    # Agrafer le ticket
    echo "🔗 Agrafage du ticket de notarisation..."
    xcrun stapler staple SidourAvoda.app
    
    echo "✅ Application notarisée avec succès !"
    echo ""
    echo "🎉 Votre app est maintenant notarisée par Apple !"
    echo "Elle peut être distribuée sans avertissements de sécurité."
    echo ""
    echo "💾 Ajoutez ce Team ID comme secret GitHub:"
    echo "   Nom: TEAM_ID"
    echo "   Valeur: $TEAM_ID"
else
    echo ""
    echo "❌ Échec de la notarisation"
    echo ""
    echo "💡 Solutions possibles :"
    echo "1. Vérifiez que le Team ID est correct"
    echo "2. Vérifiez que votre compte Apple Developer est actif"
    echo "3. Attendez quelques minutes après l'inscription"
    echo "4. Réessayez la notarisation"
    exit 1
fi

#!/bin/bash
# Script pour tester la notarisation avec Apple ID comme Team ID
# Usage: ./test-notarization-apple-id.sh

set -euo pipefail

echo "🧪 Test de notarisation avec Apple ID"
echo "====================================="
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

# Utiliser l'Apple ID comme Team ID (méthode pour comptes personnels)
TEAM_ID=$(echo "$APPLE_ID" | sed 's/@.*//')

echo "🔍 Test de notarisation personnelle..."
echo "Apple ID: $APPLE_ID"
echo "Team ID (dérivé): $TEAM_ID"
echo ""

# Créer l'archive
echo "📦 Création de l'archive..."
ditto -c -k --keepParent SidourAvoda.app SidourAvoda.zip
echo "✅ Archive créée: SidourAvoda.zip"

# Tester la notarisation avec Apple ID comme Team ID
echo ""
echo "📤 Soumission pour notarisation (Apple ID comme Team ID)..."

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
    echo "1. Vérifiez que votre compte Apple Developer est complètement activé"
    echo "2. Allez sur https://developer.apple.com/account/"
    echo "3. Acceptez tous les accords nécessaires"
    echo "4. Attendez quelques minutes après l'activation"
    echo "5. Vérifiez que votre Team ID s'affiche en haut de la page"
    echo ""
    echo "🔍 Votre vrai Team ID devrait s'afficher sur :"
    echo "   https://developer.apple.com/account/"
    exit 1
fi

#!/bin/bash
# Script pour activer la notarisation dans le workflow
# Usage: ./enable-notarization.sh

set -euo pipefail

echo "🔧 Activation de la notarisation"
echo "================================"
echo ""

# Vérifier que le fichier workflow existe
if [ ! -f ".github/workflows/macos-build.yml" ]; then
    echo "❌ Fichier workflow non trouvé"
    exit 1
fi

# Activer la notarisation
echo "📝 Modification du workflow..."
sed -i '' 's/if: ${{ false }}  # Set to true if you have Apple Developer credentials/if: ${{ true }}  # Set to true if you have Apple Developer credentials/' .github/workflows/macos-build.yml

echo "✅ Notarisation activée !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Assurez-vous que votre compte Apple Developer est actif"
echo "2. Récupérez votre Team ID sur https://developer.apple.com/account/"
echo "3. Ajoutez les secrets GitHub :"
echo "   - APPLE_ID: yoelibarthel603@gmail.com"
echo "   - APPLE_APP_SPECIFIC_PASSWORD: gcwm-vrjv-wcuf-rern"
echo "   - TEAM_ID: votre_team_id"
echo ""
echo "4. Poussez les changements :"
echo "   git add .github/workflows/macos-build.yml"
echo "   git commit -m 'Enable notarization'"
echo "   git push"
echo ""
echo "🎯 La notarisation sera automatiquement activée au prochain build !"

#!/bin/bash
# Script pour désactiver la notarisation dans le workflow
# Usage: ./disable-notarization.sh

set -euo pipefail

echo "🔧 Désactivation de la notarisation"
echo "==================================="
echo ""

# Vérifier que le fichier workflow existe
if [ ! -f ".github/workflows/macos-build.yml" ]; then
    echo "❌ Fichier workflow non trouvé"
    exit 1
fi

# Désactiver la notarisation
echo "📝 Modification du workflow..."
sed -i '' 's/if: ${{ true }}  # Set to true if you have Apple Developer credentials/if: ${{ false }}  # Set to true if you have Apple Developer credentials/' .github/workflows/macos-build.yml

echo "✅ Notarisation désactivée !"
echo ""
echo "📋 Le build fonctionnera maintenant sans notarisation."
echo "Les utilisateurs devront utiliser les solutions alternatives pour ouvrir l'app :"
echo ""
echo "🟢 Solutions pour ouvrir l'app :"
echo "1. Clic droit > Ouvrir"
echo "2. Terminal: xattr -dr com.apple.quarantine /Applications/SidourAvoda.app"
echo "3. Préférences Système > Sécurité et confidentialité"
echo ""
echo "🎯 Pour réactiver plus tard : ./enable-notarization.sh"

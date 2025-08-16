#!/bin/bash
# Script pour créer un DMG de test avec toutes les solutions (version corrigée)
# Usage: ./create-test-dmg-fixed.sh

set -euo pipefail

echo "📦 Création du DMG de test avec solutions (version corrigée)"
echo "============================================================"
echo ""

# Vérifier si l'app existe
if [ ! -d "SidourAvoda.app" ]; then
    echo "❌ SidourAvoda.app non trouvé"
    echo "Assurez-vous d'avoir construit l'application d'abord"
    exit 1
fi

echo "✅ Application trouvée : SidourAvoda.app"
echo ""

# Créer le dossier de staging
STAGE="dmg_test_staging_fixed"
echo "📁 Création du dossier de staging..."
rm -rf "$STAGE"
mkdir -p "$STAGE"

# Copier l'application
echo "📱 Copie de l'application..."
cp -R SidourAvoda.app "$STAGE/"

# Copier les solutions
echo "🔧 Copie des solutions..."
cp open-sidour-avoda.command "$STAGE/"
cp COMMENT-OUVRIR-SIDOUR-AVODA.md "$STAGE/"

# Créer le lien Applications
echo "📂 Création du lien Applications..."
ln -s /Applications "$STAGE/Applications" || true

# Créer le README principal
echo "📝 Création du README principal..."
cat > "$STAGE/📋 LIRE-AVANT-TOUT.txt" <<'TXT'
Sidour Avoda - macOS
====================

🚨 ATTENTION : macOS peut afficher un avertissement de sécurité

Solutions GRATUITES pour ouvrir l'application :

🟢 SOLUTION 1 (Recommandée) :
- Clic droit sur "SidourAvoda.app" 
- Sélectionner "Ouvrir"
- Cliquer "Ouvrir" dans la popup

🟢 SOLUTION 2 (Automatique) :
- Double-cliquer sur "🔓 Ouvrir-SidourAvoda.command"
- Entrer votre mot de passe si demandé

🟢 SOLUTION 3 (Manuelle) :
- Ouvrir Terminal (Applications > Utilitaires)
- Taper : xattr -dr com.apple.quarantine /Applications/SidourAvoda.app
- Puis double-cliquer sur l'app

🟢 SOLUTION 4 (Préférences Système) :
- Préférences Système > Sécurité et confidentialité
- Cliquer "Autoriser" à côté de SidourAvoda

✅ Après la première ouverture, l'app fonctionnera normalement.

Note : Cette app est développée en Python et n'est pas signée par Apple,
mais elle est 100% sûre et open source.

🔗 Plus d'informations : COMMENT-OUVRIR-SIDOUR-AVODA.md
TXT

# Vérifier le contenu avant création du DMG
echo "🔍 Vérification du contenu avant création..."
echo "📁 Contenu du dossier staging :"
ls -la "$STAGE"

# Créer le DMG
echo ""
echo "📦 Création du DMG..."
ARCH=$(uname -m)
DMG_NAME="SidourAvoda-Test-Fixed-${ARCH}.dmg"

hdiutil create -volname "SidourAvoda" -srcfolder "$STAGE" -ov -format UDZO "$DMG_NAME"

echo "✅ DMG créé : $DMG_NAME"
echo ""

# Vérifier le contenu du DMG
echo "🔍 Vérification du contenu du DMG..."
hdiutil attach "$DMG_NAME" -readonly
VOLUME_NAME=$(hdiutil info | grep "/Volumes/" | tail -1 | awk '{print $3}')
echo "📁 Contenu du DMG :"
ls -la "$VOLUME_NAME"
hdiutil detach "$VOLUME_NAME"

echo ""
echo "🎉 DMG de test créé avec succès !"
echo ""
echo "📋 Contenu inclus :"
echo "  ✅ SidourAvoda.app"
echo "  ✅ 🔓 Ouvrir-SidourAvoda.command (script automatique)"
echo "  ✅ COMMENT-OUVRIR-SIDOUR-AVODA.md (guide complet)"
echo "  ✅ 📋 LIRE-AVANT-TOUT.txt (instructions principales)"
echo "  ✅ Applications (lien pour installation)"
echo ""
echo "🚀 Test du DMG :"
echo "1. Double-cliquer sur $DMG_NAME"
echo "2. Glisser SidourAvoda.app vers Applications"
echo "3. Utiliser une des solutions pour l'ouvrir"
echo ""
echo "📖 Guide complet : COMMENT-OUVRIR-SIDOUR-AVODA.md"

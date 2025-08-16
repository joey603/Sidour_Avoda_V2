#!/bin/bash
# Script pour notariser Sidour Avoda avec un compte Apple Developer gratuit
# Usage: ./notarize-app.sh [path/to/SidourAvoda.app]

set -euo pipefail

APP_PATH="${1:-Sidour-avoda-Tzora-chevron/dist/SidourAvoda.app}"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ Erreur: $APP_PATH introuvable"
    echo "Usage: $0 [path/to/SidourAvoda.app]"
    exit 1
fi

echo "🔐 Notarisation de Sidour Avoda"
echo "================================"
echo "App: $APP_PATH"
echo ""

# Vérifier les prérequis
if ! command -v xcrun &> /dev/null; then
    echo "❌ Xcode Command Line Tools requis"
    echo "Installez avec: xcode-select --install"
    exit 1
fi

# Demander les credentials si pas en variables d'environnement
if [ -z "${APPLE_ID:-}" ]; then
    read -p "🍎 Apple ID: " APPLE_ID
fi

if [ -z "${APPLE_APP_SPECIFIC_PASSWORD:-}" ]; then
    echo "🔑 Créez un mot de passe spécifique à l'app sur:"
    echo "   https://appleid.apple.com/account/manage"
    echo "   Sélectionnez 'App-Specific Passwords'"
    read -s -p "Mot de passe spécifique à l'app: " APPLE_APP_SPECIFIC_PASSWORD
    echo ""
fi

if [ -z "${TEAM_ID:-}" ]; then
    echo "👥 Team ID (optionnel, laissez vide si pas de compte développeur):"
    read -p "Team ID: " TEAM_ID
fi

# Créer un archive pour la notarisation
echo "📦 Création de l'archive..."
TEMP_DIR=$(mktemp -d)
ARCHIVE_PATH="$TEMP_DIR/SidourAvoda.zip"

cd "$(dirname "$APP_PATH")"
ditto -c -k --keepParent "$(basename "$APP_PATH")" "$ARCHIVE_PATH"

        echo "📤 Envoi pour notarisation..."

        # Soumettre pour notarisation
        if [ -n "${TEAM_ID:-}" ]; then
            REQUEST_ID=$(xcrun notarytool submit "$ARCHIVE_PATH" \
                --apple-id "$APPLE_ID" \
                --password "$APPLE_APP_SPECIFIC_PASSWORD" \
                --team-id "$TEAM_ID" \
                --wait)
        else
            REQUEST_ID=$(xcrun notarytool submit "$ARCHIVE_PATH" \
                --apple-id "$APPLE_ID" \
                --password "$APPLE_APP_SPECIFIC_PASSWORD" \
                --wait)
        fi

if [ $? -eq 0 ]; then
    echo "✅ Notarisation réussie!"
    echo "Request ID: $REQUEST_ID"
    
    # Staple le ticket de notarisation
    echo "🔗 Ajout du ticket de notarisation..."
    xcrun stapler staple "$APP_PATH"
    
    echo "✅ App notarisée avec succès!"
    echo "L'app peut maintenant être ouverte sans avertissement Gatekeeper."
else
    echo "❌ Échec de la notarisation"
    echo "Vérifiez vos credentials et réessayez."
fi

# Nettoyer
rm -rf "$TEMP_DIR"

echo ""
echo "📋 Pour activer la notarisation automatique dans GitHub Actions:"
echo "1. Ajoutez ces secrets dans votre repo GitHub:"
echo "   - APPLE_ID: votre Apple ID"
echo "   - APPLE_APP_SPECIFIC_PASSWORD: mot de passe spécifique à l'app"
echo "   - TEAM_ID: votre Team ID (optionnel)"
echo "2. Modifiez le workflow pour activer le job notarize"
echo "3. Changez 'if: \${{ false }}' en 'if: \${{ true }}' dans le workflow"

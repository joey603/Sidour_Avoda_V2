#!/bin/bash
# Script pour trouver le Team ID Apple Developer
# Usage: ./find-team-id.sh

set -euo pipefail

echo "🍎 Recherche du Team ID Apple Developer"
echo "======================================"
echo ""

# Demander les credentials si pas en variables d'environnement
if [ -z "${APPLE_ID:-}" ]; then
    read -p "🍎 Apple ID (email): " APPLE_ID
fi

if [ -z "${APPLE_APP_SPECIFIC_PASSWORD:-}" ]; then
    echo "🔑 Mot de passe spécifique à l'app (gcwm-vrjv-wcuf-rern):"
    read -s -p "Mot de passe: " APPLE_APP_SPECIFIC_PASSWORD
    echo ""
fi

echo ""
echo "🔍 Recherche du Team ID..."

# Méthode 1: Apple Developer Portal (manuel)
echo "📋 Méthode 1 - Apple Developer Portal:"
echo "1. Allez sur: https://developer.apple.com"
echo "2. Connectez-vous avec votre Apple ID"
echo "3. Cliquez sur 'Account' en haut à droite"
echo "4. Votre Team ID s'affiche en haut de la page"
echo ""

# Méthode 2: altool (si disponible)
echo "🔧 Méthode 2 - altool (automatique):"
if command -v xcrun &> /dev/null; then
    echo "Tentative de récupération automatique..."
    TEAM_ID=$(xcrun altool --list-providers -u "$APPLE_ID" -p "$APPLE_APP_SPECIFIC_PASSWORD" 2>/dev/null | grep "Team ID" | awk '{print $3}' || echo "")
    if [ -n "$TEAM_ID" ]; then
        echo "✅ Team ID trouvé: $TEAM_ID"
    else
        echo "❌ Team ID non trouvé avec altool"
    fi
else
    echo "❌ Xcode Command Line Tools non installé"
fi
echo ""

# Méthode 3: notarytool info
echo "🔧 Méthode 3 - notarytool info (automatique):"
if command -v xcrun &> /dev/null; then
    echo "Tentative avec notarytool..."
    TEAM_ID_NOTARY=$(xcrun notarytool info --apple-id "$APPLE_ID" --password "$APPLE_APP_SPECIFIC_PASSWORD" 2>/dev/null | grep -i "team id" | awk '{print $NF}' || echo "")
    if [ -n "$TEAM_ID_NOTARY" ]; then
        echo "✅ Team ID trouvé: $TEAM_ID_NOTARY"
    else
        echo "❌ Team ID non trouvé avec notarytool"
    fi
else
    echo "❌ Xcode Command Line Tools non installé"
fi
echo ""

# Méthode 4: Keychain
echo "🔧 Méthode 4 - Keychain (si certificats installés):"
if command -v security &> /dev/null; then
    echo "Recherche dans le keychain..."
    TEAM_ID_KEYCHAIN=$(security find-identity -v -p codesigning 2>/dev/null | grep "Apple Development" | head -1 | awk '{print $2}' | cut -d'(' -f2 | cut -d')' -f1 || echo "")
    if [ -n "$TEAM_ID_KEYCHAIN" ]; then
        echo "✅ Team ID trouvé: $TEAM_ID_KEYCHAIN"
    else
        echo "❌ Aucun certificat Apple Development trouvé"
    fi
else
    echo "❌ Commande security non disponible"
fi
echo ""

echo "📋 Résumé des Team ID trouvés:"
if [ -n "${TEAM_ID:-}" ]; then
    echo "  - altool: $TEAM_ID"
fi
if [ -n "${TEAM_ID_NOTARY:-}" ]; then
    echo "  - notarytool: $TEAM_ID_NOTARY"
fi
if [ -n "${TEAM_ID_KEYCHAIN:-}" ]; then
    echo "  - keychain: $TEAM_ID_KEYCHAIN"
fi

echo ""
echo "🎯 Recommandation:"
echo "1. Utilisez le Team ID trouvé par altool ou notarytool"
echo "2. Si aucun n'est trouvé, utilisez la Méthode 1 (Apple Developer Portal)"
echo "3. Ajoutez le Team ID comme secret GitHub: TEAM_ID"
echo ""
echo "🔗 Lien direct: https://developer.apple.com/account/"

#!/bin/bash
# Script pour récupérer le Team ID personnel
# Usage: ./get-personal-team-id.sh

set -euo pipefail

echo "🍎 Récupération du Team ID personnel"
echo "==================================="
echo ""

# Demander les credentials
read -p "🍎 Apple ID (email): " APPLE_ID
read -s -p "🔑 Mot de passe spécifique: " APPLE_APP_SPECIFIC_PASSWORD
echo ""

echo ""
echo "🔍 Tentatives de récupération du Team ID personnel..."

# Méthode 1: notarytool info avec format différent
echo "📋 Méthode 1 - notarytool info (format complet):"
if command -v xcrun &> /dev/null; then
    echo "Tentative avec notarytool info..."
    xcrun notarytool info --apple-id "$APPLE_ID" --password "$APPLE_APP_SPECIFIC_PASSWORD" 2>&1 | grep -i "team\|organization\|member" || echo "Aucune information trouvée"
else
    echo "❌ Xcode Command Line Tools non installé"
fi
echo ""

# Méthode 2: altool avec format différent
echo "📋 Méthode 2 - altool list-providers (format complet):"
if command -v xcrun &> /dev/null; then
    echo "Tentative avec altool..."
    xcrun altool --list-providers -u "$APPLE_ID" -p "$APPLE_APP_SPECIFIC_PASSWORD" 2>&1 | grep -i "team\|organization\|member" || echo "Aucune information trouvée"
else
    echo "❌ Xcode Command Line Tools non installé"
fi
echo ""

# Méthode 3: Essayer de créer un certificat pour voir le Team ID
echo "📋 Méthode 3 - Test de création de certificat:"
if command -v xcrun &> /dev/null; then
    echo "Tentative de création de certificat de test..."
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Créer un certificat de test
    xcrun security create-certificate-signing-request \
        -keychain login.keychain \
        -reqfile test.csr \
        -key-size 2048 \
        -key-algorithm rsa \
        -key-usage digitalSignature,keyEncipherment \
        -subject "CN=Test Developer" 2>&1 | grep -i "team\|organization" || echo "Aucune information trouvée"
    
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
else
    echo "❌ Xcode Command Line Tools non installé"
fi
echo ""

# Méthode 4: Vérifier les certificats existants
echo "📋 Méthode 4 - Certificats existants:"
if command -v security &> /dev/null; then
    echo "Recherche de certificats existants..."
    security find-identity -v -p codesigning 2>&1 | grep -i "apple\|development\|team" || echo "Aucun certificat trouvé"
else
    echo "❌ Commande security non disponible"
fi
echo ""

echo "🎯 Solutions alternatives:"
echo ""
echo "1️⃣  Créer un certificat de développement:"
echo "   - Ouvrir Xcode"
echo "   - Xcode > Preferences > Accounts"
echo "   - Ajouter votre Apple ID"
echo "   - Cliquer sur 'Manage Certificates'"
echo "   - Créer un certificat de développement"
echo ""

echo "2️⃣  Utiliser un Team ID par défaut:"
echo "   - Pour les comptes personnels, essayez:"
echo "   - Votre Apple ID sans @ (ex: yoelibarthel603gmailcom)"
echo "   - Ou votre nom d'utilisateur Apple"
echo ""

echo "3️⃣  Vérifier dans Apple Developer Portal:"
echo "   - https://developer.apple.com/account/"
echo "   - Cliquer sur 'Certificates, Identifiers & Profiles'"
echo "   - Regarder dans 'Certificates' ou 'Identifiers'"
echo ""

echo "4️⃣  Contacter Apple Developer Support:"
echo "   - https://developer.apple.com/contact/"
echo "   - Demander votre Team ID personnel"
echo ""

echo "🔧 Test avec Team ID par défaut:"
echo "Tentative avec Apple ID comme Team ID..."
TEST_TEAM_ID=$(echo "$APPLE_ID" | sed 's/@.*//')
echo "Team ID suggéré: $TEST_TEAM_ID"
echo ""
echo "Vous pouvez essayer d'ajouter ce Team ID comme secret GitHub:"
echo "Name: TEAM_ID"
echo "Value: $TEST_TEAM_ID"

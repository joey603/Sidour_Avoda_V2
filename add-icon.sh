#!/bin/bash
# Script pour ajouter une icône à l'application Sidour Avoda
# Usage: ./add-icon.sh

set -euo pipefail

echo "🎨 Ajout d'icône à Sidour Avoda"
echo "==============================="
echo ""

# Vérifier si l'image existe
IMAGE_PATH="Sidour-avoda-Tzora-chevron/assets/calender-2389150_960_720.png"
if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ Image non trouvée : $IMAGE_PATH"
    exit 1
fi

echo "✅ Image trouvée : $IMAGE_PATH"
echo ""

# Créer le dossier icônes s'il n'existe pas
mkdir -p icons

# Convertir l'image en icône macOS
echo "🔄 Conversion de l'image en icône macOS..."

# Créer différentes tailles d'icônes
echo "📏 Création des tailles d'icônes..."

# 16x16
sips -z 16 16 "$IMAGE_PATH" --out icons/icon_16x16.png 2>/dev/null || echo "⚠️  Impossible de créer 16x16"

# 32x32
sips -z 32 32 "$IMAGE_PATH" --out icons/icon_32x32.png 2>/dev/null || echo "⚠️  Impossible de créer 32x32"

# 64x64
sips -z 64 64 "$IMAGE_PATH" --out icons/icon_64x64.png 2>/dev/null || echo "⚠️  Impossible de créer 64x64"

# 128x128
sips -z 128 128 "$IMAGE_PATH" --out icons/icon_128x128.png 2>/dev/null || echo "⚠️  Impossible de créer 128x128"

# 256x256
sips -z 256 256 "$IMAGE_PATH" --out icons/icon_256x256.png 2>/dev/null || echo "⚠️  Impossible de créer 256x256"

# 512x512
sips -z 512 512 "$IMAGE_PATH" --out icons/icon_512x512.png 2>/dev/null || echo "⚠️  Impossible de créer 512x512"

# 1024x1024
sips -z 1024 1024 "$IMAGE_PATH" --out icons/icon_1024x1024.png 2>/dev/null || echo "⚠️  Impossible de créer 1024x1024"

echo "✅ Icônes créées dans le dossier icons/"
echo ""

# Créer le fichier .icns
echo "🎨 Création du fichier icône .icns..."

# Créer le dossier temporaire pour iconutil
mkdir -p icons.iconset

# Copier les icônes avec les noms requis par macOS
cp icons/icon_16x16.png icons.iconset/icon_16x16.png 2>/dev/null || true
cp icons/icon_32x32.png icons.iconset/icon_16x16@2x.png 2>/dev/null || true
cp icons/icon_32x32.png icons.iconset/icon_32x32.png 2>/dev/null || true
cp icons/icon_64x64.png icons.iconset/icon_32x32@2x.png 2>/dev/null || true
cp icons/icon_128x128.png icons.iconset/icon_128x128.png 2>/dev/null || true
cp icons/icon_256x256.png icons.iconset/icon_128x128@2x.png 2>/dev/null || true
cp icons/icon_256x256.png icons.iconset/icon_256x256.png 2>/dev/null || true
cp icons/icon_512x512.png icons.iconset/icon_256x256@2x.png 2>/dev/null || true
cp icons/icon_512x512.png icons.iconset/icon_512x512.png 2>/dev/null || true
cp icons/icon_1024x1024.png icons.iconset/icon_512x512@2x.png 2>/dev/null || true

# Créer le fichier .icns
iconutil -c icns icons.iconset -o SidourAvoda.icns

if [ -f "SidourAvoda.icns" ]; then
    echo "✅ Fichier icône créé : SidourAvoda.icns"
else
    echo "❌ Erreur lors de la création du fichier icône"
    exit 1
fi

echo ""
echo "🎯 Ajout de l'icône à l'application..."

# Vérifier si l'app existe
if [ -d "SidourAvoda.app" ]; then
    # Copier l'icône dans l'application
    cp SidourAvoda.icns SidourAvoda.app/Contents/Resources/ 2>/dev/null || {
        echo "📁 Création du dossier Resources..."
        mkdir -p SidourAvoda.app/Contents/Resources
        cp SidourAvoda.icns SidourAvoda.app/Contents/Resources/
    }
    
    # Modifier le fichier Info.plist pour utiliser l'icône
    echo "📝 Modification du fichier Info.plist..."
    
    # Créer un fichier Info.plist avec l'icône si il n'existe pas
    if [ ! -f "SidourAvoda.app/Contents/Info.plist" ]; then
        cat > SidourAvoda.app/Contents/Info.plist <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIconFile</key>
    <string>SidourAvoda.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.sidouravoda.app</string>
    <key>CFBundleName</key>
    <string>SidourAvoda</string>
    <key>CFBundleDisplayName</key>
    <string>Sidour Avoda</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>SidourAvoda</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
XML
    else
        # Ajouter l'icône au fichier Info.plist existant
        if ! grep -q "CFBundleIconFile" SidourAvoda.app/Contents/Info.plist; then
            # Insérer l'icône avant la fermeture du dict
            sed -i '' 's|</dict>|    <key>CFBundleIconFile</key>\n    <string>SidourAvoda.icns</string>\n</dict>|' SidourAvoda.app/Contents/Info.plist
        fi
    fi
    
    echo "✅ Icône ajoutée à l'application !"
else
    echo "⚠️  Application non trouvée, icône créée : SidourAvoda.icns"
fi

echo ""
echo "🧹 Nettoyage des fichiers temporaires..."
rm -rf icons.iconset
rm -rf icons

echo ""
echo "🎉 Icône ajoutée avec succès !"
echo ""
echo "📋 Pour voir l'icône :"
echo "1. Reconstruire l'application avec PyInstaller"
echo "2. Ou copier SidourAvoda.icns dans l'app existante"
echo ""
echo "🎨 Fichier icône créé : SidourAvoda.icns"

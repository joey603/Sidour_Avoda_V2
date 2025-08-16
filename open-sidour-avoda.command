#!/bin/bash
# Script automatique pour ouvrir Sidour Avoda
# Usage: Double-cliquer sur ce fichier

set -euo pipefail

echo "🔓 Ouverture automatique de Sidour Avoda"
echo "========================================"
echo ""

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_PATH="$SCRIPT_DIR/SidourAvoda.app"

# Vérifier si l'app existe
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Erreur : SidourAvoda.app introuvable"
    echo "Assurez-vous que l'app est dans le même dossier que ce script."
    echo ""
    echo "📁 Répertoire actuel : $SCRIPT_DIR"
    echo "🔍 Recherche de l'application..."
    ls -la "$SCRIPT_DIR" | grep -i sidour || echo "Aucune app Sidour trouvée"
    echo ""
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo "✅ Application trouvée : $APP_PATH"
echo ""

# Supprimer l'attribut de quarantaine
echo "🔧 Suppression de l'attribut de quarantaine..."
if xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null; then
    echo "✅ Quarantaine supprimée avec succès !"
else
    echo "⚠️  Impossible de supprimer la quarantaine automatiquement."
    echo "L'application sera ouverte avec une demande de confirmation."
fi

echo ""
echo "🚀 Lancement de Sidour Avoda..."

# Ouvrir l'application
open "$APP_PATH"

echo "✅ Sidour Avoda devrait maintenant s'ouvrir !"
echo ""
echo "💡 Si l'app ne s'ouvre pas :"
echo "1. Double-cliquez directement sur SidourAvoda.app"
echo "2. Dans la popup, cliquez 'Ouvrir'"
echo "3. Ou utilisez : clic droit > Ouvrir"
echo ""
echo "🔒 Fermeture automatique dans 3 secondes..."
sleep 3

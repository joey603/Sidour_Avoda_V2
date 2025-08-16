#!/bin/bash
# Script pour désactiver temporairement Gatekeeper
# Usage: Double-cliquer sur ce fichier

set -euo pipefail

echo "🔓 Désactivation temporaire de Gatekeeper"
echo "========================================="
echo ""
echo "⚠️  ATTENTION : Cette action désactive temporairement la protection Gatekeeper"
echo "Cela permettra d'ouvrir Sidour Avoda sans avertissement."
echo ""

read -p "Voulez-vous continuer ? (o/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "❌ Opération annulée"
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo ""
echo "🔧 Désactivation de Gatekeeper..."
echo "Cette action va demander votre mot de passe administrateur."
echo ""

# Désactiver Gatekeeper
sudo spctl --master-disable

if [ $? -eq 0 ]; then
    echo "✅ Gatekeeper désactivé avec succès !"
    echo ""
    echo "🚀 Lancement de Sidour Avoda..."
    open "/Applications/SidourAvoda.app"
    
    echo ""
    echo "✅ Sidour Avoda devrait maintenant s'ouvrir sans avertissement !"
    echo ""
    echo "📋 IMPORTANT : Gatekeeper est maintenant désactivé."
    echo "Pour le réactiver plus tard, utilisez :"
    echo "sudo spctl --master-enable"
    echo ""
    echo "🔒 Réactivation automatique dans 30 secondes..."
    sleep 30
    
    echo "🔧 Réactivation de Gatekeeper..."
    sudo spctl --master-enable
    echo "✅ Gatekeeper réactivé !"
else
    echo "❌ Erreur lors de la désactivation de Gatekeeper"
fi

echo ""
read -p "Appuyez sur Entrée pour fermer..."

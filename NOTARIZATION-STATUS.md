# 📋 Statut de la Notarisation Apple

## 🔧 Configuration actuelle

**Statut :** ❌ **DÉSACTIVÉE**

La notarisation Apple est actuellement désactivée dans le workflow GitHub Actions.

## 🚀 Comment activer la notarisation

### 1. **Prérequis**
- Compte Apple Developer actif (gratuit)
- Team ID récupéré depuis https://developer.apple.com/account/
- Secrets GitHub configurés

### 2. **Activation rapide**
```bash
./enable-notarization.sh
```

### 3. **Configuration des secrets GitHub**
Ajoutez ces secrets dans votre repo GitHub :
- `APPLE_ID`: yoelibarthel603@gmail.com
- `APPLE_APP_SPECIFIC_PASSWORD`: gcwm-vrjv-wcuf-rern
- `TEAM_ID`: [votre Team ID depuis Apple Developer]

### 4. **Pousser les changements**
```bash
git add .github/workflows/macos-build.yml
git commit -m "Enable notarization"
git push
```

## 🔍 Comment trouver votre Team ID

1. Allez sur https://developer.apple.com/account/
2. Connectez-vous avec votre Apple ID
3. Le Team ID s'affiche en haut de la page
4. Il ressemble à : `ABC123DEF4` ou `yoelibarthel603`

## 🛠️ Scripts disponibles

- `./enable-notarization.sh` - Active la notarisation
- `./disable-notarization.sh` - Désactive la notarisation
- `./test-notarization-with-team.sh [TEAM_ID]` - Test avec un Team ID
- `./test-notarization-apple-id.sh` - Test avec Apple ID comme Team ID

## 📦 Distribution sans notarisation

Sans notarisation, les utilisateurs devront :

1. **Clic droit > Ouvrir** (recommandé)
2. **Terminal** : `xattr -dr com.apple.quarantine /Applications/SidourAvoda.app`
3. **Préférences Système > Sécurité et confidentialité**

## 🎯 Avantages de la notarisation

- ✅ Ouverture directe sans avertissements
- ✅ Distribution professionnelle
- ✅ Confiance des utilisateurs
- ✅ Pas de contournement de sécurité nécessaire

## 📞 Support

Si vous avez des problèmes avec la notarisation :
1. Vérifiez que votre compte Apple Developer est actif
2. Attendez quelques minutes après l'inscription
3. Vérifiez que tous les accords sont acceptés
4. Contactez Apple Developer Support si nécessaire

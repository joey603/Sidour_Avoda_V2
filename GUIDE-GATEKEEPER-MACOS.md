# 🍎 Guide pour résoudre l'avertissement Gatekeeper sur macOS

## 🚨 Problème
Lors de l'installation de Sidour Avoda sur macOS, vous pouvez voir ce message :
> "Apple n'a pas pu confirmer que « SidourAvoda » ne contenait pas de logiciel malveillant"

## ✅ Solutions GRATUITES

### 🟢 Solution 1 : Clic droit (Recommandée)
1. **Clic droit** sur `SidourAvoda.app`
2. Sélectionner **"Ouvrir"**
3. Cliquer **"Ouvrir"** dans la popup de confirmation
4. ✅ L'app s'ouvre et fonctionne normalement

### 🟢 Solution 2 : Script automatique (Inclus dans le DMG)
1. Double-cliquer sur **"🔓 Ouvrir-SidourAvoda.command"**
2. Entrer votre mot de passe si demandé
3. ✅ L'app s'ouvre automatiquement

### 🟢 Solution 3 : Terminal (Manuelle)
1. Ouvrir **Terminal** (Applications > Utilitaires)
2. Taper cette commande :
   ```bash
   xattr -dr com.apple.quarantine /Applications/SidourAvoda.app
   ```
3. Double-cliquer sur l'app
4. ✅ L'app s'ouvre normalement

### 🟢 Solution 4 : Préférences Système
1. Aller dans **Préférences Système** > **Sécurité et confidentialité**
2. Cliquer **"Autoriser"** à côté de SidourAvoda
3. ✅ L'app peut maintenant s'ouvrir

## 🔐 Solution Permanente : Notarisation Apple (Gratuite)

### Pourquoi cette solution ?
- **Élimine définitivement** l'avertissement Gatekeeper
- **Gratuite** avec un compte Apple Developer
- **Professionnelle** et approuvée par Apple

### Étapes pour notariser :

#### 1. Créer un compte Apple Developer gratuit
- Aller sur [developer.apple.com](https://developer.apple.com)
- Créer un compte avec votre Apple ID
- **Gratuit** pour la notarisation

#### 2. Créer un mot de passe spécifique à l'app
- Aller sur [appleid.apple.com](https://appleid.apple.com/account/manage)
- Sélectionner **"App-Specific Passwords"**
- Créer un nouveau mot de passe pour "Sidour Avoda"

#### 3. Notariser l'app
```bash
# Rendre le script exécutable
chmod +x notarize-app.sh

# Lancer la notarisation
./notarize-app.sh
```

#### 4. Activer la notarisation automatique
1. Dans votre repo GitHub, aller dans **Settings** > **Secrets and variables** > **Actions**
2. Ajouter ces secrets :
   - `APPLE_ID` : votre Apple ID
   - `APPLE_APP_SPECIFIC_PASSWORD` : le mot de passe spécifique créé
   - `TEAM_ID` : votre Team ID (optionnel)
3. Modifier le workflow GitHub pour activer la notarisation

## 📋 Informations techniques

### Qu'est-ce que Gatekeeper ?
- Système de sécurité macOS qui vérifie la signature des apps
- Protège contre les logiciels malveillants
- Bloque les apps non signées par Apple

### Pourquoi Sidour Avoda n'est pas signée ?
- Développée en Python avec PyInstaller
- Open source et 100% sûre
- Pas de signature Apple car pas de compte développeur payant

### La notarisation Apple
- **Gratuite** pour tous les développeurs
- Vérifie que l'app n'est pas malveillante
- Ajoute un "ticket" qui permet l'ouverture sans avertissement
- **Recommandée** pour les apps distribuées publiquement

## 🆘 Support

Si vous rencontrez des problèmes :
1. Essayez d'abord la **Solution 1** (clic droit)
2. Vérifiez que vous avez les permissions administrateur
3. Contactez le développeur si le problème persiste

## ✅ Résultat attendu

Après avoir appliqué une de ces solutions :
- ✅ L'app s'ouvre sans avertissement
- ✅ Fonctionne normalement
- ✅ Pas de problème de sécurité
- ✅ Peut être utilisée quotidiennement

---

**Note** : Toutes ces solutions sont **gratuites** et **sûres**. L'app Sidour Avoda est open source et ne contient aucun logiciel malveillant.

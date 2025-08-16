# 🔐 Configuration des secrets GitHub pour notarisation automatique

## 🎯 Objectif
Configurer GitHub Actions pour notariser automatiquement chaque build de Sidour Avoda.

## 📋 Secrets à configurer

### 1. **APPLE_ID**
- **Valeur** : Votre Apple ID (email)
- **Exemple** : `votre-email@example.com`

### 2. **APPLE_APP_SPECIFIC_PASSWORD**
- **Valeur** : Le mot de passe spécifique créé
- **Exemple** : `gcwm-vrjv-wcuf-rern`

### 3. **TEAM_ID** (optionnel)
- **Valeur** : Votre Team ID Apple Developer
- **Exemple** : `ABC123DEF4`

## 🚀 Étapes de configuration

### Étape 1 : Aller dans les secrets GitHub
1. Allez sur votre repo : **https://github.com/joey603/Sidour_Avoda_V2**
2. Cliquez sur **"Settings"** (onglet)
3. Dans le menu de gauche, cliquez sur **"Secrets and variables"**
4. Cliquez sur **"Actions"**

### Étape 2 : Ajouter les secrets
1. Cliquez sur **"New repository secret"**
2. Ajoutez chaque secret :

#### Secret 1 : APPLE_ID
- **Name** : `APPLE_ID`
- **Value** : Votre Apple ID (email)

#### Secret 2 : APPLE_APP_SPECIFIC_PASSWORD
- **Name** : `APPLE_APP_SPECIFIC_PASSWORD`
- **Value** : `gcwm-vrjv-wcuf-rern`

#### Secret 3 : TEAM_ID (optionnel)
- **Name** : `TEAM_ID`
- **Value** : Votre Team ID (si vous en avez un)

### Étape 3 : Vérifier la configuration
Une fois configuré, le workflow va :
1. ✅ Construire l'app
2. ✅ Notariser automatiquement
3. ✅ Créer un DMG notarisé
4. ✅ Uploader l'artefact

## 🎉 Résultat

Après configuration :
- **Chaque build** sera automatiquement notarisé
- **Tous les utilisateurs** pourront ouvrir l'app sans avertissement
- **Solution permanente** pour toutes les futures versions

## 📊 Workflow activé

Le workflow est maintenant configuré pour :
- ✅ Build automatique sur push vers `macos-build`
- ✅ Notarisation automatique avec vos credentials
- ✅ DMG notarisé disponible en téléchargement

## 🔍 Vérification

Pour vérifier que ça fonctionne :
1. Poussez un commit vers `macos-build`
2. Allez dans **Actions** → **build-macos-app**
3. Vous verrez l'étape "Notarize app" s'exécuter
4. Le DMG notarisé sera disponible en téléchargement

---

**Note** : Une fois configuré, vous n'aurez plus besoin de notariser manuellement. Chaque build sera automatiquement notarisé ! 🎯

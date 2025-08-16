# 🚀 Configuration immédiate des secrets GitHub

## ⚡ Action requise MAINTENANT

Pour activer la notarisation automatique, vous devez configurer les secrets GitHub.

### 📋 Vos informations :
- **Apple ID** : (votre email Apple)
- **Mot de passe spécifique** : `gcwm-vrjv-wcuf-rern`
- **Team ID** : (optionnel, laissez vide si pas de compte développeur payant)

## 🔧 Étapes de configuration :

### 1. Aller dans les secrets GitHub
1. Ouvrez : **https://github.com/joey603/Sidour_Avoda_V2/settings/secrets/actions**
2. Ou naviguez : Repo → Settings → Secrets and variables → Actions

### 2. Ajouter le premier secret
1. Cliquez **"New repository secret"**
2. **Name** : `APPLE_ID`
3. **Value** : Votre Apple ID (email)
4. Cliquez **"Add secret"**

### 3. Ajouter le deuxième secret
1. Cliquez **"New repository secret"**
2. **Name** : `APPLE_APP_SPECIFIC_PASSWORD`
3. **Value** : `gcwm-vrjv-wcuf-rern`
4. Cliquez **"Add secret"**

### 4. Ajouter le troisième secret (optionnel)
1. Cliquez **"New repository secret"**
2. **Name** : `TEAM_ID`
3. **Value** : (laissez vide si pas de Team ID)
4. Cliquez **"Add secret"**

## ✅ Vérification

Une fois configuré, vous devriez voir :
- ✅ `APPLE_ID` dans la liste des secrets
- ✅ `APPLE_APP_SPECIFIC_PASSWORD` dans la liste des secrets
- ✅ `TEAM_ID` dans la liste des secrets (si ajouté)

## 🎯 Prochaines étapes

Après configuration des secrets :
1. Le workflow actuel se terminera
2. Le prochain build sera automatiquement notarisé
3. Tous les futurs builds seront notarisés

---

**Important** : Les secrets sont chiffrés et sécurisés. Seul GitHub y a accès pour les workflows.

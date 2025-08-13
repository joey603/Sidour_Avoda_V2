import sqlite3
import os
import sys
from travailleur import Travailleur
from horaire import Horaire
import json

class Database:
    def __init__(self, db_file="planning_data.db"):
        # Toujours stocker la base dans un dossier utilisateur persistant
        app_dir = None
        try:
            if sys.platform == 'darwin':  # macOS
                app_dir = os.path.expanduser("~/Library/Application Support/Sidour Avoda")
            elif sys.platform.startswith('win'):
                appdata = os.environ.get('APPDATA') or os.path.expanduser("~\\AppData\\Roaming")
                app_dir = os.path.join(appdata, "Sidour Avoda")
            else:
                app_dir = os.path.expanduser("~/.local/share/sidour-avoda")
            os.makedirs(app_dir, exist_ok=True)
            self.db_file = os.path.join(app_dir, db_file)
        except Exception:
            # Fallback: current directory
            self.db_file = db_file
        
        self.conn = None
        self.init_database()
    
    def connect(self):
        """Établit une connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        return self.conn
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def init_database(self):
        """Initialise la structure de la base de données si elle n'existe pas"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Table des sites (NOUVEAU)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            description TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Table des réglages de site (shifts et jours actifs)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_settings (
            site_id INTEGER PRIMARY KEY,
            shifts TEXT,           -- liste séparée par des virgules, ex: "06-14,14-22,22-06"
            active_days TEXT,      -- liste séparée par des virgules, ex: "lundi,mardi,mercredi"
            required_counts TEXT,  -- JSON des capacités par jour/shift
            max_per_person TEXT,   -- JSON des limites par personne et par shift (label -> int, 0 = illimité)
            FOREIGN KEY (site_id) REFERENCES sites (id)
        )
        ''')
        
        # Table des travailleurs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS travailleurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            nb_shifts_souhaites INTEGER NOT NULL,
            site_id INTEGER DEFAULT 1,
            FOREIGN KEY (site_id) REFERENCES sites (id)
        )
        ''')
        
        # Vérifier si la colonne site_id existe déjà dans travailleurs
        cursor.execute("PRAGMA table_info(travailleurs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Ajouter la colonne site_id si elle n'existe pas
        if 'site_id' not in columns:
            try:
                cursor.execute("ALTER TABLE travailleurs ADD COLUMN site_id INTEGER DEFAULT 1")
            except sqlite3.OperationalError:
                pass

        # Migration: s'assurer que la contrainte d'unicité porte sur (nom, site_id) et non sur nom seul
        try:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='travailleurs'")
            row = cursor.fetchone()
            table_sql = row[0] if row else ''
            needs_migration = ('nom TEXT UNIQUE' in table_sql) and ('UNIQUE(nom, site_id)' not in table_sql)
        except Exception:
            needs_migration = False

        if needs_migration:
            try:
                # Désactiver les FK pour la migration de schéma
                cursor.execute("PRAGMA foreign_keys=OFF")
                cursor.execute("BEGIN TRANSACTION")
                # Renommer l'ancienne table
                cursor.execute("ALTER TABLE travailleurs RENAME TO travailleurs_old")
                # Recréer la table avec la bonne contrainte d'unicité composite
                cursor.execute('''
                CREATE TABLE travailleurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    nb_shifts_souhaites INTEGER NOT NULL,
                    site_id INTEGER DEFAULT 1,
                    FOREIGN KEY (site_id) REFERENCES sites (id),
                    UNIQUE(nom, site_id)
                )
                ''')
                # Copier les données en conservant les ids
                cursor.execute('''
                    INSERT INTO travailleurs (id, nom, nb_shifts_souhaites, site_id)
                    SELECT id, nom, nb_shifts_souhaites, COALESCE(site_id, 1) FROM travailleurs_old
                ''')
                # Supprimer l'ancienne table
                cursor.execute("DROP TABLE travailleurs_old")
                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
            finally:
                try:
                    cursor.execute("PRAGMA foreign_keys=ON")
                except Exception:
                    pass

        # S'assurer qu'un index unique composite existe (au cas où)
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_travailleurs_nom_site ON travailleurs(nom, site_id)")
        except Exception:
            pass
        
        # Table des disponibilités
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS disponibilites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            travailleur_id INTEGER NOT NULL,
            jour TEXT NOT NULL,
            shift TEXT NOT NULL,
            FOREIGN KEY (travailleur_id) REFERENCES travailleurs (id) ON DELETE CASCADE
        )
        ''')
        
        # Table des disponibilités pour les gardes de 12h
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS disponibilites_12h (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            travailleur_id INTEGER NOT NULL,
            jour TEXT NOT NULL,
            type_12h TEXT NOT NULL,
            FOREIGN KEY (travailleur_id) REFERENCES travailleurs (id) ON DELETE CASCADE
        )
        ''')
        
        # Table des plannings
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plannings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP,
            site_id INTEGER DEFAULT 1,
            FOREIGN KEY (site_id) REFERENCES sites (id)
        )
        ''')
        
        # Vérifier si la colonne date_modification existe déjà
        cursor.execute("PRAGMA table_info(plannings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Ajouter la colonne date_modification si elle n'existe pas
        if 'date_modification' not in columns:
            try:
                cursor.execute("ALTER TABLE plannings ADD COLUMN date_modification TIMESTAMP")
            except sqlite3.OperationalError:
                # La colonne existe peut-être déjà ou une autre erreur est survenue
                pass
        
        # Vérifier si la colonne site_id existe déjà dans plannings
        cursor.execute("PRAGMA table_info(plannings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Ajouter la colonne site_id si elle n'existe pas
        if 'site_id' not in columns:
            try:
                cursor.execute("ALTER TABLE plannings ADD COLUMN site_id INTEGER DEFAULT 1")
            except sqlite3.OperationalError:
                pass
        
        # Créer le site par défaut s'il n'existe pas
        cursor.execute("SELECT COUNT(*) FROM sites")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO sites (nom, description) VALUES (?, ?)", 
                         ("Site principal", "Site par défaut"))
            # Réglages par défaut: 3 shifts et tous les jours actifs
            cursor.execute(
                "INSERT OR REPLACE INTO site_settings (site_id, shifts, active_days, required_counts, max_per_person) VALUES (1, ?, ?, ?, ?)",
                ("06-14,14-22,22-06", "dimanche,lundi,mardi,mercredi,jeudi,vendredi,samedi", json.dumps({}), json.dumps({"06-14": 6, "14-22": 6, "22-06": 6}))
            )
        else:
            # S'assurer que la colonne required_counts existe
            cursor.execute("PRAGMA table_info(site_settings)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'required_counts' not in cols:
                try:
                    cursor.execute("ALTER TABLE site_settings ADD COLUMN required_counts TEXT")
                except sqlite3.OperationalError:
                    pass
            # S'assurer que la colonne max_per_person existe
            cursor.execute("PRAGMA table_info(site_settings)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'max_per_person' not in cols:
                try:
                    cursor.execute("ALTER TABLE site_settings ADD COLUMN max_per_person TEXT")
                except sqlite3.OperationalError:
                    pass
        
        # Table des assignations de shifts
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planning_id INTEGER NOT NULL,
            travailleur_id INTEGER NOT NULL,
            jour TEXT NOT NULL,
            shift TEXT NOT NULL,
            FOREIGN KEY (planning_id) REFERENCES plannings (id) ON DELETE CASCADE,
            FOREIGN KEY (travailleur_id) REFERENCES travailleurs (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        self.close()
    
    def sauvegarder_travailleur(self, travailleur, ancien_nom=None):
        """Sauvegarde un travailleur dans la base de données
        
        Si ancien_nom est fourni et différent du nom actuel, utilise l'ancien nom
        pour rechercher le travailleur à mettre à jour.
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Nom à utiliser pour la recherche (ancien nom si fourni et différent, sinon nom actuel)
        nom_recherche = ancien_nom if ancien_nom and ancien_nom != travailleur.nom else travailleur.nom
        
        # Vérifier si le travailleur existe déjà (dans le même site uniquement)
        cursor.execute("SELECT id FROM travailleurs WHERE nom = ? AND site_id = ?", (nom_recherche, travailleur.site_id))
        result = cursor.fetchone()
        
        if result:
            # Mettre à jour le travailleur existant
            travailleur_id = result['id']
            
            # Mettre à jour le nom, le nombre de shifts souhaités ET le site
            cursor.execute(
                "UPDATE travailleurs SET nom = ?, nb_shifts_souhaites = ?, site_id = ? WHERE id = ?",
                (travailleur.nom, travailleur.nb_shifts_souhaites, travailleur.site_id, travailleur_id)
            )
            
            # Supprimer les anciennes disponibilités
            cursor.execute("DELETE FROM disponibilites WHERE travailleur_id = ?", (travailleur_id,))
            cursor.execute("DELETE FROM disponibilites_12h WHERE travailleur_id = ?", (travailleur_id,))
        else:
            # Vérifier si un travailleur avec le nouveau nom existe déjà dans le même site
            if ancien_nom and ancien_nom != travailleur.nom:
                cursor.execute("SELECT id FROM travailleurs WHERE nom = ? AND site_id = ?", (travailleur.nom, travailleur.site_id))
                if cursor.fetchone():
                    # Un travailleur avec ce nom existe déjà, on annule l'opération
                    conn.close()
                    return None
                
            # Créer un nouveau travailleur avec le site_id
            cursor.execute(
                "INSERT INTO travailleurs (nom, nb_shifts_souhaites, site_id) VALUES (?, ?, ?)",
                (travailleur.nom, travailleur.nb_shifts_souhaites, travailleur.site_id)
            )
            travailleur_id = cursor.lastrowid
        
        # Ajouter les disponibilités
        for jour, shifts in travailleur.disponibilites.items():
            for shift in shifts:
                cursor.execute(
                    "INSERT INTO disponibilites (travailleur_id, jour, shift) VALUES (?, ?, ?)",
                    (travailleur_id, jour, shift)
                )
        
        # Ajouter les disponibilités pour les gardes de 12h
        if hasattr(travailleur, 'disponibilites_12h'):
            for jour, types_12h in travailleur.disponibilites_12h.items():
                for type_12h in types_12h:
                    cursor.execute(
                        "INSERT INTO disponibilites_12h (travailleur_id, jour, type_12h) VALUES (?, ?, ?)",
                        (travailleur_id, jour, type_12h)
                    )
        
        conn.commit()
        self.close()
        return travailleur_id
    
    def charger_travailleurs(self):
        """Charge tous les travailleurs depuis la base de données"""
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nom, nb_shifts_souhaites, site_id FROM travailleurs")
        travailleurs_data = cursor.fetchall()
        
        travailleurs = []
        for t_data in travailleurs_data:
            # Charger les disponibilités normales
            disponibilites = {}
            cursor.execute(
                "SELECT jour, shift FROM disponibilites WHERE travailleur_id = ?",
                (t_data['id'],)
            )
            dispos = cursor.fetchall()
            
            for dispo in dispos:
                jour = dispo['jour']
                shift = dispo['shift']
                
                if jour not in disponibilites:
                    disponibilites[jour] = []
                
                disponibilites[jour].append(shift)
            
            # Charger les disponibilités 12h
            disponibilites_12h = {}
            cursor.execute(
                "SELECT jour, type_12h FROM disponibilites_12h WHERE travailleur_id = ?",
                (t_data['id'],)
            )
            dispos_12h = cursor.fetchall()
            
            for dispo in dispos_12h:
                jour = dispo['jour']
                type_12h = dispo['type_12h']
                
                if jour not in disponibilites_12h:
                    disponibilites_12h[jour] = []
                
                disponibilites_12h[jour].append(type_12h)
            
            # Créer l'objet Travailleur
            travailleur = Travailleur(t_data['nom'], disponibilites, t_data['nb_shifts_souhaites'], site_id=t_data['site_id'])
            travailleur.disponibilites_12h = disponibilites_12h
            travailleurs.append(travailleur)
        
        self.close()
        return travailleurs
    
    def supprimer_travailleur(self, nom, site_id=None):
        """Supprime un travailleur de la base de données. Si site_id est fourni, limite au site."""
        conn = self.connect()
        cursor = conn.cursor()
        
        if site_id is not None:
            cursor.execute("SELECT id FROM travailleurs WHERE nom = ? AND site_id = ?", (nom, site_id))
        else:
            cursor.execute("SELECT id FROM travailleurs WHERE nom = ?", (nom,))
        result = cursor.fetchone()
        
        if result:
            travailleur_id = result['id']
            cursor.execute("DELETE FROM disponibilites WHERE travailleur_id = ?", (travailleur_id,))
            cursor.execute("DELETE FROM disponibilites_12h WHERE travailleur_id = ?", (travailleur_id,))
            cursor.execute("DELETE FROM travailleurs WHERE id = ?", (travailleur_id,))
            conn.commit()
            self.close()
            return True
        
        self.close()
        return False
    
    def sauvegarder_planning(self, planning, nom=None, site_id=1):
        """Sauvegarde un planning dans la base de données"""
        from datetime import datetime
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Créer un nouveau planning avec site_id
        date_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO plannings (date_creation, nom, site_id) VALUES (?, ?, ?)",
            (date_creation, nom, site_id)
        )
        planning_id = cursor.lastrowid
        
        # Récupérer les IDs des travailleurs
        travailleurs_ids = {}
        for travailleur in planning.travailleurs:
            cursor.execute("SELECT id FROM travailleurs WHERE nom = ? AND site_id = ?", (travailleur.nom, site_id))
            result = cursor.fetchone()
            if result:
                travailleurs_ids[travailleur.nom] = result['id']
        
        # Sauvegarder les assignations en gérant les multi-capacités ("nom1 / nom2 / ...")
        for jour, shifts_map in planning.planning.items():
            for shift, travailleur_nom in shifts_map.items():
                if not travailleur_nom:
                    continue
                noms = [n.strip() for n in str(travailleur_nom).split(" / ") if n.strip()]
                for nom_simple in noms:
                    travailleur_id = travailleurs_ids.get(nom_simple)
                    if travailleur_id:
                        cursor.execute(
                            "INSERT INTO assignations (planning_id, travailleur_id, jour, shift) VALUES (?, ?, ?, ?)",
                            (planning_id, travailleur_id, jour, shift)
                        )
        
        conn.commit()
        self.close()
        return planning_id
    
    def charger_planning(self, planning_id):
        """Charge un planning depuis la base de données"""
        from planning import Planning
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Vérifier si le planning existe
        cursor.execute("SELECT id, site_id FROM plannings WHERE id = ?", (planning_id,))
        row = cursor.fetchone()
        if not row:
            self.close()
            return None
        site_id = row[1]
        
        # Charger les réglages (jours/shifts) du site associé pour construire une structure complète
        shifts_list, days_list = self.charger_reglages_site(site_id)
        # Créer un planning structuré selon ces réglages
        planning = Planning(site_id=site_id, jours=days_list, shifts=shifts_list)
        
        # Charger les travailleurs
        try:
            # Restreindre aux travailleurs de ce site pour cohérence
            planning.travailleurs = self.charger_travailleurs_par_site(site_id)
        except Exception:
            planning.travailleurs = self.charger_travailleurs()
        
        # Charger les assignations
        cursor.execute(
            """
            SELECT a.jour, a.shift, t.nom 
            FROM assignations a
            JOIN travailleurs t ON a.travailleur_id = t.id
            WHERE a.planning_id = ?
            """,
            (planning_id,)
        )
        assignations = cursor.fetchall()
        # Agréger par (jour, shift) pour reconstruire les cellules multi-capacité
        cellules = {}
        for row in assignations:
            cle = (row['jour'], row['shift'])
            cellules.setdefault(cle, []).append(row['nom'])
        # Remplir le planning
        for (jour, shift), noms in cellules.items():
            if jour in planning.planning and shift in planning.planning[jour]:
                planning.planning[jour][shift] = " / ".join(noms)
        
        self.close()
        return planning
    
    def lister_plannings(self):
        """Liste tous les plannings enregistrés"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, date_creation, nom FROM plannings ORDER BY date_creation DESC")
        plannings = cursor.fetchall()
        
        self.close()
        return plannings

    # Réglages de site: sauvegarde/chargement
    def sauvegarder_reglages_site(self, site_id, shifts_list, active_days_list, required_counts: dict | None = None, max_per_person: dict | None = None):
        """Sauvegarde les réglages de shifts et jours actifs d'un site.
        Optionnellement, enregistre les capacités par jour/shift et les limites par personne (par label de shift)."""
        conn = self.connect()
        cursor = conn.cursor()
        shifts_text = ",".join(shifts_list)
        days_text = ",".join(active_days_list)
        if required_counts is not None or max_per_person is not None:
            try:
                rc_text = json.dumps(required_counts)
            except Exception:
                rc_text = json.dumps({})
            try:
                mp_text = json.dumps(max_per_person) if max_per_person is not None else None
            except Exception:
                mp_text = None
            # Choisir la requête en fonction de la présence de la colonne max_per_person
            try:
                cursor.execute(
                    "INSERT OR REPLACE INTO site_settings (site_id, shifts, active_days, required_counts, max_per_person) VALUES (?, ?, ?, ?, ?)",
                    (site_id, shifts_text, days_text, rc_text, mp_text)
                )
            except Exception:
                # Fallback si colonne absente
                cursor.execute(
                    "INSERT OR REPLACE INTO site_settings (site_id, shifts, active_days, required_counts) VALUES (?, ?, ?, ?)",
                    (site_id, shifts_text, days_text, rc_text)
                )
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO site_settings (site_id, shifts, active_days) VALUES (?, ?, ?)",
                (site_id, shifts_text, days_text)
            )
        conn.commit()
        self.close()

    def charger_reglages_site(self, site_id):
        """Charge les réglages d'un site. Retourne (shifts_list, active_days_list)."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT shifts, active_days FROM site_settings WHERE site_id = ?", (site_id,))
        row = cursor.fetchone()
        self.close()
        if row and row[0] and row[1]:
            shifts = [s.strip() for s in row[0].split(',') if s.strip()]
            days = [d.strip() for d in row[1].split(',') if d.strip()]
            return shifts, days
        # Valeurs par défaut
        return list(Horaire.get_all_shifts()), list(Horaire.get_all_jours())

    def charger_capacites_site(self, site_id):
        """Retourne un dict {jour: {shift: int}} des capacités requises (1 par défaut)."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT required_counts, shifts, active_days FROM site_settings WHERE site_id = ?", (site_id,))
        row = cursor.fetchone()
        self.close()
        capacites = {}
        if row:
            rc_text = row[0] if isinstance(row, (list, tuple)) else row['required_counts'] if row and 'required_counts' in row.keys() else None
            if rc_text:
                try:
                    capacites = json.loads(rc_text)
                except Exception:
                    capacites = {}
        # S'assurer d'avoir au moins 1 pour tous jours/shifts connus
        shifts = [s.strip() for s in (row[1] if isinstance(row, (list, tuple)) else row['shifts']).split(',')] if row else list(Horaire.get_all_shifts())
        days = [d.strip() for d in (row[2] if isinstance(row, (list, tuple)) else row['active_days']).split(',')] if row else list(Horaire.get_all_jours())
        fixed = {}
        for j in days:
            fixed[j] = {}
            for s in shifts:
                try:
                    v = int(capacites.get(j, {}).get(s, 1))
                except Exception:
                    v = 1
                fixed[j][s] = max(1, v)
        return fixed

    def charger_limites_par_personne(self, site_id):
        """Retourne un dict {shift_label: int} où 0 signifie illimité. Par défaut {'22-06': 3}."""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT max_per_person, shifts FROM site_settings WHERE site_id = ?", (site_id,))
            row = cursor.fetchone()
        except Exception:
            row = None
        self.close()
        limites = {}
        if row:
            try:
                raw = row[0] if isinstance(row, (list, tuple)) else row['max_per_person'] if row and 'max_per_person' in row.keys() else None
            except Exception:
                raw = None
            if raw:
                try:
                    limites = json.loads(raw) or {}
                except Exception:
                    limites = {}
        # Valeur par défaut pour la nuit si présente dans les shifts standards
        if not limites:
            try:
                shifts_text = row[1] if isinstance(row, (list, tuple)) else row['shifts']
                shifts = [s.strip() for s in shifts_text.split(',') if s.strip()] if shifts_text else []
            except Exception:
                shifts = []
            # Défauts raisonnables
            if '06-14' in shifts:
                limites['06-14'] = 7
            if '14-22' in shifts:
                limites['14-22'] = 7
            if '22-06' in shifts or not shifts:
                limites['22-06'] = 3
        return limites
    
    def lister_plannings_par_site(self, site_id=None):
        """Liste tous les plannings d'un site spécifique ou tous si site_id est None"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if site_id:
            cursor.execute("""
                SELECT p.id, p.date_creation, p.nom, s.nom as site_nom 
                FROM plannings p 
                JOIN sites s ON p.site_id = s.id 
                WHERE p.site_id = ? 
                ORDER BY p.date_creation DESC
            """, (site_id,))
        else:
            cursor.execute("""
                SELECT p.id, p.date_creation, p.nom, s.nom as site_nom 
                FROM plannings p 
                JOIN sites s ON p.site_id = s.id 
                ORDER BY p.date_creation DESC
            """)
        
        plannings = cursor.fetchall()
        
        self.close()
        return plannings
    
    def mettre_a_jour_planning(self, planning_id, planning):
        """Met à jour un planning existant dans la base de données"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Supprimer les assignations existantes pour ce planning
            cursor.execute("DELETE FROM assignations WHERE planning_id = ?", (planning_id,))
            
            # Récupérer les IDs des travailleurs
            travailleurs_ids = {}
            for travailleur in planning.travailleurs:
                cursor.execute("SELECT id FROM travailleurs WHERE nom = ?", (travailleur.nom,))
                result = cursor.fetchone()
                if result:
                    travailleurs_ids[travailleur.nom] = result['id']
            
            # Insérer les nouvelles assignations
            for jour, shifts_map in planning.planning.items():
                for shift in shifts_map.keys():
                    travailleur_nom = planning.planning[jour][shift]
                    if travailleur_nom:
                        # Vérifier si c'est une garde partagée
                        if " / " in travailleur_nom:
                            noms = travailleur_nom.split(" / ")
                            for nom in noms:
                                if nom in travailleurs_ids:
                                    cursor.execute(
                                        "INSERT INTO assignations (planning_id, travailleur_id, jour, shift) VALUES (?, ?, ?, ?)",
                                        (planning_id, travailleurs_ids[nom], jour, shift)
                                    )
                        else:
                            # Garde simple
                            if travailleur_nom in travailleurs_ids:
                                cursor.execute(
                                    "INSERT INTO assignations (planning_id, travailleur_id, jour, shift) VALUES (?, ?, ?, ?)",
                                    (planning_id, travailleurs_ids[travailleur_nom], jour, shift)
                                )
            
            # Mettre à jour la date de modification du planning
            import datetime
            date_modification = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE plannings SET date_modification = ? WHERE id = ?",
                (date_modification, planning_id)
            )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du planning: {e}")
            conn.rollback()
            return False
        finally:
            self.close()
    
    def supprimer_planning(self, planning_id):
        """Supprime un planning de la base de données"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Supprimer d'abord les assignations liées à ce planning
            cursor.execute("DELETE FROM assignations WHERE planning_id = ?", (planning_id,))
            
            # Puis supprimer le planning lui-même
            cursor.execute("DELETE FROM plannings WHERE id = ?", (planning_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du planning: {e}")
            conn.rollback()
            return False
        finally:
            self.close()
    
    def obtenir_info_planning(self, planning_id):
        """Récupère les informations d'un planning spécifique"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Vérifier si la colonne date_modification existe
        cursor.execute("PRAGMA table_info(plannings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'date_modification' in columns:
            cursor.execute("SELECT id, nom, date_creation, date_modification, site_id FROM plannings WHERE id = ?", (planning_id,))
        else:
            cursor.execute("SELECT id, nom, date_creation, site_id FROM plannings WHERE id = ?", (planning_id,))
        
        planning_info = cursor.fetchone()
        
        self.close()
        
        if planning_info:
            result = dict(planning_info)
            # Ajouter date_modification si elle n'existe pas dans le résultat
            if 'date_modification' not in result:
                result['date_modification'] = None
            # Garantir la présence de site_id
            if 'site_id' not in result:
                # Interroger séparément si nécessaire
                try:
                    cursor = self.connect().cursor()
                    cursor.execute("SELECT site_id FROM plannings WHERE id = ?", (planning_id,))
                    row = cursor.fetchone()
                    result['site_id'] = row['site_id'] if row else None
                    self.close()
                except Exception:
                    result['site_id'] = None
            return result
        else:
            return None
    
    def modifier_nom_planning(self, planning_id, nouveau_nom):
        """Modifie le nom d'un planning existant"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Mettre à jour le nom du planning
            cursor.execute(
                "UPDATE plannings SET nom = ? WHERE id = ?",
                (nouveau_nom, planning_id)
            )
            
            # Mettre à jour la date de modification
            import datetime
            date_modification = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE plannings SET date_modification = ? WHERE id = ?",
                (date_modification, planning_id)
            )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur lors de la modification du nom du planning: {e}")
            conn.rollback()
            return False
        finally:
            self.close()
    
    def mettre_a_jour_nom_travailleur_dans_plannings(self, travailleur_id, nouveau_nom):
        """Met à jour le nom d'un travailleur dans les assignations existantes"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Récupérer tous les plannings qui contiennent des assignations pour ce travailleur
        cursor.execute("""
            SELECT DISTINCT planning_id FROM assignations 
            WHERE travailleur_id = ?
        """, (travailleur_id,))
        
        plannings = cursor.fetchall()
        
        # Rien à faire si aucun planning n'utilise ce travailleur
        if not plannings:
            self.close()
            return
        
        # Mettre à jour le nom du travailleur dans les assignations
        # (Pas besoin de mettre à jour la table assignations car elle utilise l'ID, pas le nom)
        
        conn.commit()
        self.close() 

    def sauvegarder_site(self, nom, description=""):
        """Sauvegarde un nouveau site"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO sites (nom, description) VALUES (?, ?)",
                (nom, description)
            )
            site_id = cursor.lastrowid
            conn.commit()
            return site_id
        except sqlite3.IntegrityError:
            return None  # Site existe déjà
        finally:
            self.close()
    
    def charger_sites(self):
        """Charge tous les sites"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nom, description FROM sites ORDER BY nom")
        sites = cursor.fetchall()
        
        self.close()
        return sites
    
    def charger_travailleurs_par_site(self, site_id=1):
        """Charge les travailleurs d'un site spécifique"""
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nom, nb_shifts_souhaites, site_id FROM travailleurs WHERE site_id = ?", (site_id,))
        travailleurs_data = cursor.fetchall()
        
        travailleurs = []
        for t_data in travailleurs_data:
            # Charger les disponibilités normales
            disponibilites = {}
            cursor.execute(
                "SELECT jour, shift FROM disponibilites WHERE travailleur_id = ?",
                (t_data['id'],)
            )
            dispos = cursor.fetchall()
            
            for dispo in dispos:
                jour = dispo['jour']
                shift = dispo['shift']
                
                if jour not in disponibilites:
                    disponibilites[jour] = []
                
                disponibilites[jour].append(shift)
            
            # Charger les disponibilités 12h
            disponibilites_12h = {}
            cursor.execute(
                "SELECT jour, type_12h FROM disponibilites_12h WHERE travailleur_id = ?",
                (t_data['id'],)
            )
            dispos_12h = cursor.fetchall()
            
            for dispo in dispos_12h:
                jour = dispo['jour']
                type_12h = dispo['type_12h']
                
                if jour not in disponibilites_12h:
                    disponibilites_12h[jour] = []
                
                disponibilites_12h[jour].append(type_12h)
            
            # Créer l'objet Travailleur
            travailleur = Travailleur(t_data['nom'], disponibilites, t_data['nb_shifts_souhaites'], site_id=t_data['site_id'])
            travailleur.disponibilites_12h = disponibilites_12h
            travailleurs.append(travailleur)
        
        self.close()
        return travailleurs
    
    def supprimer_site(self, site_id):
        """Supprime un site (si aucun travailleur/planning associé)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Vérifier s'il y a des travailleurs associés
        cursor.execute("SELECT COUNT(*) FROM travailleurs WHERE site_id = ?", (site_id,))
        if cursor.fetchone()[0] > 0:
            self.close()
            return False  # Ne peut pas supprimer, il y a des travailleurs
        
        # Vérifier s'il y a des plannings associés
        cursor.execute("SELECT COUNT(*) FROM plannings WHERE site_id = ?", (site_id,))
        if cursor.fetchone()[0] > 0:
            self.close()
            return False  # Ne peut pas supprimer, il y a des plannings
        
        cursor.execute("DELETE FROM sites WHERE id = ?", (site_id,))
        conn.commit()

        self.close()
        return True 

    def supprimer_site_avec_travailleurs(self, site_id):
        """Supprime un site ET tous ses travailleurs associés"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Commencer une transaction
            cursor.execute("BEGIN")
            
            # 1. Supprimer les disponibilités des travailleurs du site
            cursor.execute("""
                DELETE FROM disponibilites 
                WHERE travailleur_id IN (
                    SELECT id FROM travailleurs WHERE site_id = ?
                )
            """, (site_id,))
            
            # 2. Supprimer les disponibilités 12h des travailleurs du site
            cursor.execute("""
                DELETE FROM disponibilites_12h 
                WHERE travailleur_id IN (
                    SELECT id FROM travailleurs WHERE site_id = ?
                )
            """, (site_id,))
            
            # 3. Supprimer les assignations des plannings du site
            cursor.execute("""
                DELETE FROM assignations 
                WHERE planning_id IN (
                    SELECT id FROM plannings WHERE site_id = ?
                )
            """, (site_id,))
            
            # 4. Supprimer les plannings du site
            cursor.execute("DELETE FROM plannings WHERE site_id = ?", (site_id,))
            
            # 5. Supprimer les travailleurs du site
            cursor.execute("DELETE FROM travailleurs WHERE site_id = ?", (site_id,))
            
            # 6. Enfin, supprimer le site lui-même
            cursor.execute("DELETE FROM sites WHERE id = ?", (site_id,))
            
            # Valider la transaction
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression du site avec travailleurs: {e}")
            conn.rollback()
            return False
        finally:
            self.close()
    
    def compter_elements_site(self, site_id):
        """Compte le nombre de travailleurs et plannings d'un site"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Compter les travailleurs
        cursor.execute("SELECT COUNT(*) FROM travailleurs WHERE site_id = ?", (site_id,))
        nb_travailleurs = cursor.fetchone()[0]
        
        # Compter les plannings
        cursor.execute("SELECT COUNT(*) FROM plannings WHERE site_id = ?", (site_id,))
        nb_plannings = cursor.fetchone()[0]
        
        self.close()
        return nb_travailleurs, nb_plannings 
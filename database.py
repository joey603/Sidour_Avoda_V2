import sqlite3
import os
from travailleur import Travailleur
from horaire import Horaire

class Database:
    def __init__(self, db_file="planning_data.db"):
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
        
        # Table des travailleurs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS travailleurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            nb_shifts_souhaites INTEGER NOT NULL
        )
        ''')
        
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
            date_modification TIMESTAMP
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
    
    def sauvegarder_travailleur(self, travailleur):
        """Sauvegarde un travailleur dans la base de données"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Vérifier si le travailleur existe déjà
        cursor.execute("SELECT id FROM travailleurs WHERE nom = ?", (travailleur.nom,))
        result = cursor.fetchone()
        
        if result:
            # Mettre à jour le travailleur existant
            travailleur_id = result['id']
            cursor.execute(
                "UPDATE travailleurs SET nb_shifts_souhaites = ? WHERE id = ?",
                (travailleur.nb_shifts_souhaites, travailleur_id)
            )
            
            # Supprimer les anciennes disponibilités
            cursor.execute("DELETE FROM disponibilites WHERE travailleur_id = ?", (travailleur_id,))
            cursor.execute("DELETE FROM disponibilites_12h WHERE travailleur_id = ?", (travailleur_id,))
        else:
            # Créer un nouveau travailleur
            cursor.execute(
                "INSERT INTO travailleurs (nom, nb_shifts_souhaites) VALUES (?, ?)",
                (travailleur.nom, travailleur.nb_shifts_souhaites)
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
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nom, nb_shifts_souhaites FROM travailleurs")
        travailleurs_data = cursor.fetchall()
        
        travailleurs = []
        for t_data in travailleurs_data:
            # Récupérer les disponibilités
            cursor.execute(
                "SELECT jour, shift FROM disponibilites WHERE travailleur_id = ?",
                (t_data['id'],)
            )
            disponibilites_data = cursor.fetchall()
            
            # Construire le dictionnaire de disponibilités
            disponibilites = {}
            for d_data in disponibilites_data:
                jour = d_data['jour']
                shift = d_data['shift']
                if jour not in disponibilites:
                    disponibilites[jour] = []
                disponibilites[jour].append(shift)
            
            # Récupérer les disponibilités pour les gardes de 12h
            cursor.execute(
                "SELECT jour, type_12h FROM disponibilites_12h WHERE travailleur_id = ?",
                (t_data['id'],)
            )
            disponibilites_12h_data = cursor.fetchall()
            
            # Construire le dictionnaire de disponibilités pour les gardes de 12h
            disponibilites_12h = {}
            for d_data in disponibilites_12h_data:
                jour = d_data['jour']
                type_12h = d_data['type_12h']
                if jour not in disponibilites_12h:
                    disponibilites_12h[jour] = []
                disponibilites_12h[jour].append(type_12h)
            
            # Créer l'objet Travailleur
            travailleur = Travailleur(t_data['nom'], disponibilites, t_data['nb_shifts_souhaites'])
            travailleur.disponibilites_12h = disponibilites_12h
            travailleurs.append(travailleur)
        
        self.close()
        return travailleurs
    
    def supprimer_travailleur(self, nom):
        """Supprime un travailleur de la base de données"""
        conn = self.connect()
        cursor = conn.cursor()
        
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
    
    def sauvegarder_planning(self, planning, nom=None):
        """Sauvegarde un planning dans la base de données"""
        from datetime import datetime
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Créer un nouveau planning
        date_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO plannings (date_creation, nom) VALUES (?, ?)",
            (date_creation, nom)
        )
        planning_id = cursor.lastrowid
        
        # Récupérer les IDs des travailleurs
        travailleurs_ids = {}
        for travailleur in planning.travailleurs:
            cursor.execute("SELECT id FROM travailleurs WHERE nom = ?", (travailleur.nom,))
            result = cursor.fetchone()
            if result:
                travailleurs_ids[travailleur.nom] = result['id']
        
        # Sauvegarder les assignations
        for jour in Horaire.get_all_jours():
            for shift in Horaire.get_all_shifts():
                travailleur_nom = planning.planning[jour][shift]
                if travailleur_nom and travailleur_nom in travailleurs_ids:
                    cursor.execute(
                        "INSERT INTO assignations (planning_id, travailleur_id, jour, shift) VALUES (?, ?, ?, ?)",
                        (planning_id, travailleurs_ids[travailleur_nom], jour, shift)
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
        cursor.execute("SELECT id FROM plannings WHERE id = ?", (planning_id,))
        if not cursor.fetchone():
            self.close()
            return None
        
        # Créer un nouveau planning
        planning = Planning()
        
        # Charger les travailleurs
        planning.travailleurs = self.charger_travailleurs()
        
        # Charger les assignations
        cursor.execute("""
            SELECT a.jour, a.shift, t.nom 
            FROM assignations a
            JOIN travailleurs t ON a.travailleur_id = t.id
            WHERE a.planning_id = ?
        """, (planning_id,))
        
        assignations = cursor.fetchall()
        
        # Initialiser le planning
        planning.planning = {jour: {shift: None for shift in Horaire.get_all_shifts()}
                            for jour in Horaire.get_all_jours()}
        
        # Remplir le planning avec les assignations
        for assignation in assignations:
            jour = assignation['jour']
            shift = assignation['shift']
            nom = assignation['nom']
            planning.planning[jour][shift] = nom
        
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
            for jour in Horaire.JOURS:
                for shift in Horaire.SHIFTS.values():
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
            cursor.execute("SELECT id, nom, date_creation, date_modification FROM plannings WHERE id = ?", (planning_id,))
        else:
            cursor.execute("SELECT id, nom, date_creation FROM plannings WHERE id = ?", (planning_id,))
        
        planning_info = cursor.fetchone()
        
        self.close()
        
        if planning_info:
            result = dict(planning_info)
            # Ajouter date_modification si elle n'existe pas dans le résultat
            if 'date_modification' not in result:
                result['date_modification'] = None
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
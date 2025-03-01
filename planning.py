from travailleur import Travailleur
from horaire import Horaire
import random
from database import Database
import datetime

class Planning:
    def __init__(self):
        self.planning = {jour: {shift: None for shift in Horaire.get_all_shifts()}
                        for jour in Horaire.get_all_jours()}
        self.travailleurs = []
        self.mode_12h = False  # Mode pour autoriser les gardes de 12h

    def ajouter_travailleur(self, travailleur):
        self.travailleurs.append(travailleur)

    def get_shift_precedent(self, jour, shift):
        """Retourne le jour et le shift précédent dans la séquence"""
        jours = Horaire.get_all_jours()
        shifts = list(Horaire.get_all_shifts())
        
        jour_idx = jours.index(jour)
        shift_idx = shifts.index(shift)
        
        if shift_idx > 0:
            # Même jour, shift précédent
            return jour, shifts[shift_idx - 1]
        elif jour_idx > 0:
            # Jour précédent, dernier shift
            return jours[jour_idx - 1], shifts[-1]
        else:
            # Premier shift du premier jour, pas de précédent
            return None, None

    def get_shift_suivant(self, jour, shift):
        """Retourne le jour et le shift suivant dans la séquence"""
        jours = Horaire.get_all_jours()
        shifts = list(Horaire.get_all_shifts())
        
        jour_idx = jours.index(jour)
        shift_idx = shifts.index(shift)
        
        if shift_idx < len(shifts) - 1:
            # Même jour, shift suivant
            return jour, shifts[shift_idx + 1]
        elif jour_idx < len(jours) - 1:
            # Jour suivant, premier shift
            return jours[jour_idx + 1], shifts[0]
        else:
            # Dernier shift du dernier jour, pas de suivant
            return None, None

    def travailleur_a_shift_adjacent(self, travailleur_nom, jour, shift, planning=None):
        """Vérifie si le travailleur a un shift adjacent (avant ou après)"""
        # Utiliser le planning fourni ou le planning par défaut
        planning_a_verifier = planning if planning is not None else self.planning
        
        # Vérifier le shift précédent
        jour_prec, shift_prec = self.get_shift_precedent(jour, shift)
        if jour_prec and planning_a_verifier[jour_prec][shift_prec] == travailleur_nom:
            return True
            
        # Vérifier le shift suivant
        jour_suiv, shift_suiv = self.get_shift_suivant(jour, shift)
        if jour_suiv and planning_a_verifier[jour_suiv][shift_suiv] == travailleur_nom:
            return True
            
        return False

    def compter_shifts_nuit(self, travailleur_nom, planning=None):
        """Compte le nombre de shifts de nuit assignés à un travailleur"""
        # Utiliser le planning fourni ou le planning par défaut
        planning_a_verifier = planning if planning is not None else self.planning
        
        shifts_nuit = 0
        for jour in Horaire.get_all_jours():
            if planning_a_verifier[jour]["22-06"] == travailleur_nom:
                shifts_nuit += 1
        return shifts_nuit

    def travailleur_travaille_jour(self, travailleur_nom, jour, planning=None):
        """Vérifie si un travailleur travaille un jour donné"""
        planning_a_verifier = planning if planning is not None else self.planning
        
        for shift in Horaire.get_all_shifts():
            if planning_a_verifier[jour][shift] == travailleur_nom:
                return True
        return False

    def compter_jours_consecutifs(self, travailleur_nom, jour_final, planning=None):
        """Compte le nombre de jours consécutifs travaillés jusqu'à un jour donné"""
        planning_a_verifier = planning if planning is not None else self.planning
        jours = Horaire.get_all_jours()
        
        # Trouver l'index du jour final
        jour_idx = jours.index(jour_final)
        
        # Compter les jours consécutifs en remontant dans le temps
        jours_consecutifs = 0
        for i in range(jour_idx, -1, -1):
            jour = jours[i]
            if self.travailleur_travaille_jour(travailleur_nom, jour, planning_a_verifier):
                jours_consecutifs += 1
            else:
                break
        
        return jours_consecutifs

    def calculer_score_planning(self, planning=None):
        """Calcule un score pour le planning actuel (plus élevé = meilleur)"""
        # Utiliser le planning fourni ou le planning par défaut
        planning_a_verifier = planning if planning is not None else self.planning
        
        score = 0
        
        # Pénalité pour les shifts non assignés
        shifts_non_assignes = 0
        for jour in Horaire.get_all_jours():
            for shift in Horaire.get_all_shifts():
                if planning_a_verifier[jour][shift] is None:
                    shifts_non_assignes += 1
        
        # Pénalité pour les shifts consécutifs (très forte en mode normal)
        shifts_consecutifs = 0
        for jour in Horaire.get_all_jours():
            for shift in Horaire.get_all_shifts():
                travailleur = planning_a_verifier[jour][shift]
                if travailleur:
                    if self.travailleur_a_shift_adjacent(travailleur, jour, shift, planning_a_verifier):
                        shifts_consecutifs += 1
        
        # Pénalité pour les travailleurs qui n'ont pas leur nombre de shifts souhaités
        ecart_shifts_souhaites = 0
        for travailleur in self.travailleurs:
            # Compter les shifts assignés dans ce planning
            shifts_assignes = 0
            for jour in Horaire.get_all_jours():
                for shift in Horaire.get_all_shifts():
                    if planning_a_verifier[jour][shift] == travailleur.nom:
                        shifts_assignes += 1
            
            ecart = abs(shifts_assignes - travailleur.nb_shifts_souhaites)
            ecart_shifts_souhaites += ecart
        
        # Pénalité pour les travailleurs qui font plus de 3 shifts de nuit
        exces_nuit = 0
        for travailleur in self.travailleurs:
            shifts_nuit = self.compter_shifts_nuit(travailleur.nom, planning_a_verifier)
            if shifts_nuit > 3:
                exces_nuit += (shifts_nuit - 3)
        
        # Pénalité pour les travailleurs qui travaillent 7 jours consécutifs
        jours_consecutifs_excessifs = 0
        for travailleur in self.travailleurs:
            for jour in Horaire.get_all_jours():
                jours_consecutifs = self.compter_jours_consecutifs(travailleur.nom, jour, planning_a_verifier)
                if jours_consecutifs >= 7:
                    jours_consecutifs_excessifs += 1
        
        # Calcul du score final (négatif car ce sont des pénalités)
        penalite_consecutif = 1000 if not self.mode_12h else 10  # Très forte pénalité en mode normal
        score = -(shifts_non_assignes * 100 + shifts_consecutifs * penalite_consecutif + 
                 ecart_shifts_souhaites * 5 + exces_nuit * 50 + jours_consecutifs_excessifs * 2000)
        
        return score

    def generer_planning_optimise(self):
        """Génère un planning optimisé en testant plusieurs solutions"""
        import random
        
        # Nombre d'itérations pour trouver la meilleure solution
        nb_iterations = 1000
        
        # Garder trace du meilleur planning trouvé
        meilleur_score = float('-inf')
        meilleur_planning = None
        meilleure_assignation = None
        
        # Générer plusieurs plannings et garder le meilleur
        for _ in range(nb_iterations):
            # Réinitialiser le planning pour cette itération
            planning_test = {jour: {shift: None for shift in Horaire.get_all_shifts()}
                            for jour in Horaire.get_all_jours()}
            
            # Réinitialiser les shifts assignés pour cette itération
            for travailleur in self.travailleurs:
                travailleur.shifts_assignes = 0
            
            # Mélanger l'ordre des jours et des shifts pour diversifier les solutions
            jours = list(Horaire.get_all_jours())
            shifts = list(Horaire.get_all_shifts())
            random.shuffle(jours)
            
            # Pour chaque jour et shift, assigner un travailleur disponible
            for jour in jours:
                for shift in shifts:
                    # Trouver les travailleurs disponibles pour ce shift
                    travailleurs_disponibles = []
                    for travailleur in self.travailleurs:
                        # Vérifier si le travailleur est disponible et n'a pas de shift adjacent
                        if (travailleur.est_disponible(jour, shift) and 
                            not self.travailleur_a_shift_adjacent(travailleur.nom, jour, shift, planning_test)):
                            
                            # Vérifier la limite de shifts de nuit
                            if shift == "22-06" and self.compter_shifts_nuit(travailleur.nom, planning_test) >= 3:
                                # Sauter ce travailleur s'il a déjà 3 shifts de nuit
                                continue
                            
                            # Vérifier si le travailleur n'a pas dépassé son nombre de shifts souhaités
                            if travailleur.shifts_assignes < travailleur.nb_shifts_souhaites:
                                # Vérifier si le travailleur ne travaille pas déjà 6 jours consécutifs
                                jours_consecutifs = self.compter_jours_consecutifs(travailleur.nom, jour, planning_test)
                                if jours_consecutifs < 6:  # Autoriser jusqu'à 6 jours consécutifs
                                    travailleurs_disponibles.append(travailleur)
                    
                    # Si des travailleurs sont disponibles, en choisir un
                    if travailleurs_disponibles:
                        # Trier les travailleurs par écart entre shifts assignés et souhaités
                        travailleurs_disponibles.sort(
                            key=lambda t: (t.shifts_assignes - t.nb_shifts_souhaites)
                        )
                        
                        # Choisir le travailleur avec le plus grand écart négatif
                        travailleur = travailleurs_disponibles[0]
                        planning_test[jour][shift] = travailleur.nom
                        travailleur.shifts_assignes += 1
            
            # Calculer le score de ce planning
            score = self.calculer_score_planning(planning_test)
            
            # Si ce planning est meilleur que le précédent, le garder
            if score > meilleur_score:
                meilleur_score = score
                meilleur_planning = {jour: {shift: planning_test[jour][shift] 
                                          for shift in Horaire.get_all_shifts()}
                                    for jour in Horaire.get_all_jours()}
                meilleure_assignation = {t.nom: t.shifts_assignes for t in self.travailleurs}
        
        # Restaurer le meilleur planning trouvé
        self.planning = meilleur_planning
        
        # Restaurer les shifts assignés
        for travailleur in self.travailleurs:
            if travailleur.nom in meilleure_assignation:
                travailleur.shifts_assignes = meilleure_assignation[travailleur.nom]

    def generer_planning(self, mode_12h=False):
        """Méthode principale pour générer le planning"""
        self.mode_12h = mode_12h
        
        # Réinitialiser le planning
        self.planning = {jour: {shift: None for shift in Horaire.get_all_shifts()}
                        for jour in Horaire.get_all_jours()}
        
        # Réinitialiser les shifts assignés pour tous les travailleurs
        for travailleur in self.travailleurs:
            travailleur.shifts_assignes = 0
        
        # Générer le planning optimisé sans combler les trous
        self.generer_planning_optimise()
        
        # Ne pas combler les trous automatiquement
        # La méthode combler_trous() sera appelée séparément si l'utilisateur le souhaite

    def afficher_planning(self):
        print("\nPlanning de la semaine:")
        print("=" * 80)
        print(f"{'Jour':<12}{'06-14':<20}{'14-22':<20}{'22-06':<20}")
        print("-" * 80)
        
        for jour in Horaire.get_all_jours():
            ligne = f"{jour:<12}"
            for shift in Horaire.get_all_shifts():
                travailleur = self.planning[jour][shift]
                ligne += f"{travailleur if travailleur else 'Non assigné':<20}"
            print(ligne)

    def sauvegarder(self, nom=None):
        """Sauvegarde le planning dans la base de données"""
        if not nom:
            # Générer un nom par défaut avec la date
            nom = f"Planning du {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        db = Database()
        planning_id = db.sauvegarder_planning(self, nom)
        return planning_id

    @staticmethod
    def charger(planning_id):
        """Charge un planning depuis la base de données"""
        db = Database()
        return db.charger_planning(planning_id)

    @staticmethod
    def lister_plannings():
        """Liste tous les plannings enregistrés"""
        db = Database()
        return db.lister_plannings()

    def combler_trous(self):
        """Comble les trous dans le planning sans tenir compte des shifts souhaités"""
        # Identifier les shifts non assignés
        shifts_non_assignes = []
        for jour in Horaire.get_all_jours():
            for shift in Horaire.get_all_shifts():
                if self.planning[jour][shift] is None:
                    shifts_non_assignes.append((jour, shift))
        
        # Si aucun trou, rien à faire
        if not shifts_non_assignes:
            print("Aucun trou à combler dans le planning.")
            return
        
        print(f"Trous à combler: {len(shifts_non_assignes)}")
        
        # Pour chaque trou, trouver un travailleur disponible
        for jour, shift in shifts_non_assignes:
            print(f"\nTentative de combler le trou pour {jour} {shift}")
            
            # Afficher les disponibilités pour débogage
            self.debug_disponibilites(jour, shift)
            
            # Trouver les travailleurs disponibles pour ce shift
            travailleurs_disponibles = []
            for travailleur in self.travailleurs:
                if travailleur.est_disponible(jour, shift):
                    # En mode normal, vérifier qu'il n'y a pas de shifts adjacents
                    if not self.mode_12h and self.travailleur_a_shift_adjacent(travailleur.nom, jour, shift):
                        print(f"  {travailleur.nom} a un shift adjacent, ignoré")
                        continue
                    
                    # Vérifier la limite de shifts de nuit
                    if shift == "22-06" and self.compter_shifts_nuit(travailleur.nom) >= 3:
                        print(f"  {travailleur.nom} a déjà 3 shifts de nuit, ignoré")
                        continue
                    
                    # Vérifier si le travailleur ne travaille pas déjà 6 jours consécutifs
                    jours_consecutifs = self.compter_jours_consecutifs(travailleur.nom, jour)
                    if jours_consecutifs >= 6:
                        print(f"  {travailleur.nom} a déjà travaillé 6 jours consécutifs, ignoré")
                        continue
                    
                    travailleurs_disponibles.append(travailleur)
            
            print(f"  Travailleurs disponibles (première passe): {[t.nom for t in travailleurs_disponibles]}")
            
            # Si aucun travailleur disponible avec les contraintes, assouplir les contraintes
            if not travailleurs_disponibles:
                print("  Assouplissement des contraintes...")
                for travailleur in self.travailleurs:
                    if travailleur.est_disponible(jour, shift):
                        travailleurs_disponibles.append(travailleur)
                
                print(f"  Travailleurs disponibles (deuxième passe): {[t.nom for t in travailleurs_disponibles]}")
            
            # Assigner le shift au travailleur disponible
            if travailleurs_disponibles:
                # Trier par nombre de shifts déjà assignés
                travailleurs_disponibles.sort(key=lambda t: t.shifts_assignes)
                travailleur = travailleurs_disponibles[0]
                print(f"  Assignation à {travailleur.nom} (shifts assignés: {travailleur.shifts_assignes})")
                
                self.planning[jour][shift] = travailleur.nom
                travailleur.shifts_assignes += 1
            else:
                print(f"  Impossible de combler le trou: aucun travailleur disponible")

    def debug_disponibilites(self, jour, shift):
        """Affiche les disponibilités des travailleurs pour un jour et un shift donnés"""
        print(f"\nDébogage des disponibilités pour {jour} {shift}:")
        for travailleur in self.travailleurs:
            est_dispo = travailleur.est_disponible(jour, shift)
            a_shift_adjacent = self.travailleur_a_shift_adjacent(travailleur.nom, jour, shift)
            shifts_nuit = self.compter_shifts_nuit(travailleur.nom)
            
            print(f"  {travailleur.nom}:")
            print(f"    - Disponible: {est_dispo}")
            print(f"    - A shift adjacent: {a_shift_adjacent}")
            print(f"    - Shifts de nuit: {shifts_nuit}")
            print(f"    - Shifts assignés: {travailleur.shifts_assignes}")
            print(f"    - Shifts souhaités: {travailleur.nb_shifts_souhaites}")
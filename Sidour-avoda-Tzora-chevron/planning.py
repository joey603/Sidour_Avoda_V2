from travailleur import Travailleur
from horaire import Horaire
import random
from database import Database
import datetime
import copy
from typing import Callable

class Planning:
    def __init__(self, site_id=1, jours=None, shifts=None):
        jours_effectifs = list(jours) if jours else list(Horaire.get_all_jours())
        shifts_effectifs = list(shifts) if shifts else list(Horaire.get_all_shifts())
        self.planning = {jour: {shift: None for shift in shifts_effectifs}
                        for jour in jours_effectifs}
        self.travailleurs = []
        self.mode_12h = False  # Mode pour autoriser les gardes de 12h
        self.site_id = site_id  # NOUVEAU: ID du site pour ce planning
        # Alternatives de planning ayant le même meilleur score
        self.alternatives = []  # liste de plannings (dict jour->shift->nom)
        self.best_score = None
        self.current_alternative_index = -1
        # Capacités par jour/shift (nombre de personnes requises)
        try:
            db = Database()
            self.capacites = db.charger_capacites_site(site_id)
            self.limites_par_personne = db.charger_limites_par_personne(site_id)
        except Exception:
            self.capacites = {j: {s: 1 for s in shifts_effectifs} for j in jours_effectifs}
            self.limites_par_personne = {"06-14": 6, "14-22": 6, "22-06": 6}
        # Pondération de pénalité pour places non pourvues (réduite pour favoriser des variantes)
        self.penalite_manquant = 30

    def _get_travailleur_par_nom(self, nom):
        for t in self.travailleurs:
            if t.nom == nom:
                return t
        return None

    def ajouter_travailleur(self, travailleur):
        self.travailleurs.append(travailleur)

    def _ordered_days(self):
        dynamic_days = list(self.planning.keys())
        return [j for j in Horaire.get_all_jours() if j in dynamic_days]

    def _ordered_shifts(self):
        if not self.planning:
            return list(Horaire.get_all_shifts())
        return list(next(iter(self.planning.values())).keys())

    def _ordered_days_from_planning(self, planning_dict):
        """Retourne les jours dans l'ordre standard, filtrés par ceux présents dans planning_dict."""
        if not planning_dict:
            return list(Horaire.get_all_jours())
        present = set(planning_dict.keys())
        return [j for j in Horaire.get_all_jours() if j in present]

    def get_shift_precedent(self, jour, shift):
        """Retourne le jour et le shift précédent dans la séquence (config active)."""
        jours = self._ordered_days()
        shifts = self._ordered_shifts()
        
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
        """Retourne le jour et le shift suivant dans la séquence (config active)."""
        jours = self._ordered_days()
        shifts = self._ordered_shifts()
        
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
        if jour_prec:
            val = planning_a_verifier[jour_prec][shift_prec]
            if val and travailleur_nom.strip() in [n.strip() for n in str(val).split(" / ") if n.strip()]:
                return True
            
        # Vérifier le shift suivant
        jour_suiv, shift_suiv = self.get_shift_suivant(jour, shift)
        if jour_suiv:
            val = planning_a_verifier[jour_suiv][shift_suiv]
            if val and travailleur_nom.strip() in [n.strip() for n in str(val).split(" / ") if n.strip()]:
                return True
            
        return False

    def compter_shifts_nuit(self, travailleur_nom, planning=None):
        """Compte le nombre de shifts de nuit assignés à un travailleur"""
        # Utiliser le planning fourni ou le planning par défaut
        planning_a_verifier = planning if planning is not None else self.planning
        
        shifts_nuit = 0
        for jour in (planning_a_verifier.keys() if planning_a_verifier else Horaire.get_all_jours()):
            # Compter uniquement si le shift de nuit existe dans la config
            if "22-06" in planning_a_verifier[jour]:
                val = planning_a_verifier[jour]["22-06"]
                if val and travailleur_nom.strip() in [n.strip() for n in str(val).split(" / ") if n.strip()]:
                    shifts_nuit += 1
        return shifts_nuit

    def compter_shifts_par_type(self, travailleur_nom, planning=None):
        """Compte le nombre de shifts par type pour un travailleur"""
        planning_a_verifier = planning if planning is not None else self.planning
        counts = {}
        for jour in planning_a_verifier:
            for shift in planning_a_verifier[jour]:
                val = planning_a_verifier[jour][shift]
                if val and travailleur_nom.strip() in [n.strip() for n in str(val).split(" / ") if n.strip()]:
                    counts[shift] = counts.get(shift, 0) + 1
        return counts

    def respecte_limites_par_personne(self, travailleur_nom, jour, shift, planning=None):
        """Vérifie si l'assignation respecte les limites par personne"""
        planning_a_verifier = planning if planning is not None else self.planning
        
        # Compter les shifts actuels par type
        counts = self.compter_shifts_par_type(travailleur_nom, planning_a_verifier)
        
        # Vérifier si l'assignation dépasserait la limite pour ce type de shift
        limite = self.limites_par_personne.get(shift, 6)  # 6 par défaut
        count_actuel = counts.get(shift, 0)
        
        return count_actuel < limite

    def travailleur_travaille_jour(self, travailleur_nom, jour, planning=None):
        """Vérifie si un travailleur travaille un jour donné"""
        planning_a_verifier = planning if planning is not None else self.planning
        # Accès sûr: si le jour n'existe pas dans ce planning, retourner False
        shifts_map = planning_a_verifier.get(jour)
        if not shifts_map:
            return False
        for shift, assigne in shifts_map.items():
            if assigne and travailleur_nom.strip() in [n.strip() for n in str(assigne).split(" / ") if n.strip()]:
                return True
        return False

    def compter_jours_consecutifs(self, travailleur_nom, jour_final, planning=None):
        """Compte le nombre de jours consécutifs travaillés jusqu'à un jour donné"""
        planning_a_verifier = planning if planning is not None else self.planning
        jours = self._ordered_days_from_planning(planning_a_verifier)
        if not jours or jour_final not in jours:
            return 0
        # Trouver l'index du jour final dans l'ordre effectif
        jour_idx = jours.index(jour_final)
        # Compter en remontant
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
        
        # Pénalité pour les shifts non assignés (capacité)
        shifts_non_assignes = 0
        jours_dyn = list(planning_a_verifier.keys())
        shifts_dyn = list(next(iter(planning_a_verifier.values())).keys()) if planning_a_verifier else list(Horaire.get_all_shifts())
        trous_par_jour = {jour: 0 for jour in jours_dyn}
        for jour in jours_dyn:
            for shift in shifts_dyn:
                cap = int(self.capacites.get(jour, {}).get(shift, 1))
                val = planning_a_verifier[jour][shift]
                assignes = 0
                if val:
                    assignes = len([n for n in str(val).split(" / ") if n.strip()])
                manquants = max(0, cap - assignes)
                shifts_non_assignes += manquants
                trous_par_jour[jour] += manquants
        
        # Pénalité pour les shifts consécutifs (très forte en mode normal)
        shifts_consecutifs = 0
        for jour in jours_dyn:
            for shift in shifts_dyn:
                travailleur = planning_a_verifier[jour][shift]
                if travailleur:
                    if self.travailleur_a_shift_adjacent(travailleur, jour, shift, planning_a_verifier):
                        shifts_consecutifs += 1
        
        # Pénalité pour les travailleurs qui n'ont pas leur nombre de shifts souhaités
        ecart_shifts_souhaites = 0
        # Conserver aussi les ratios de satisfaction pour une pénalité d'iniquité
        ratios_satisfaction = []
        for travailleur in self.travailleurs:
            # Compter les shifts assignés dans ce planning
            shifts_assignes = 0
            for jour in jours_dyn:
                for shift in shifts_dyn:
                    val = planning_a_verifier[jour][shift]
                    if val and travailleur.nom.strip() in [n.strip() for n in str(val).split(" / ") if n.strip()]:
                        shifts_assignes += 1
            
            ecart = abs(shifts_assignes - travailleur.nb_shifts_souhaites)
            ecart_shifts_souhaites += ecart

            # Ratio de satisfaction: 1.0 signifie objectif atteint
            denom = max(1, travailleur.nb_shifts_souhaites)
            ratio = shifts_assignes / denom
            ratios_satisfaction.append(ratio)
        
        # Pénalité pour les dépassements de limites par personne
        exces_limites = 0
        for travailleur in self.travailleurs:
            counts = self.compter_shifts_par_type(travailleur.nom, planning_a_verifier)
            for shift, count in counts.items():
                limite = self.limites_par_personne.get(shift, 6)
                if count > limite:
                    exces_limites += (count - limite)
        
        # Pénalité pour les travailleurs qui travaillent 7 jours consécutifs
        jours_consecutifs_excessifs = 0
        for travailleur in self.travailleurs:
            for jour in jours_dyn:
                jours_consecutifs = self.compter_jours_consecutifs(travailleur.nom, jour, planning_a_verifier)
                if jours_consecutifs >= 7:
                    jours_consecutifs_excessifs += 1
        
        # Pénalité d'iniquité: variance des ratios de satisfaction
        inequite = 0.0
        if ratios_satisfaction:
            moyenne = sum(ratios_satisfaction) / len(ratios_satisfaction)
            # Utiliser la somme des écarts absolus pour une pénalité robuste
            inequite = sum(abs(r - moyenne) for r in ratios_satisfaction)

        # Pénalité d'iniquité: variance des ratios de satisfaction
        penalite_consecutif = 1000 if not self.mode_12h else 10  # Très forte pénalité en mode normal
        # Pénalité pour les trous concentrés le même jour (seulement les trous au-delà du premier)
        penalite_trous_concentres = sum(max(0, n - 1) for n in trous_par_jour.values()) * 50
        score = -(shifts_non_assignes * self.penalite_manquant + shifts_consecutifs * penalite_consecutif + 
                 ecart_shifts_souhaites * 5 + exces_limites * 50 + jours_consecutifs_excessifs * 2000 + 
                 inequite * 30 + penalite_trous_concentres)
        
        return score

    def generer_planning_optimise(self, progress_cb: Callable | None = None):
        """Génère un planning optimisé en testant plusieurs solutions"""
        import random
        
        # Nombre d'itérations pour trouver la meilleure solution
        # Dynamique: en fonction du nombre total de sous-slots requis (capacités)
        try:
            jours_iter = list(self.planning.keys()) if self.planning else list(Horaire.get_all_jours())
            shifts_iter = list(next(iter(self.planning.values())).keys()) if self.planning else list(Horaire.get_all_shifts())
            total_sous_slots = 0
            for j in jours_iter:
                for s in shifts_iter:
                    try:
                        cap = int(self.capacites.get(j, {}).get(s, 1))
                    except Exception:
                        cap = 1
                    total_sous_slots += max(1, cap)
            # Augmenter la couverture: facteur ×40 et plafond 5000
            nb_iterations = min(5000, 200 + 60 * total_sous_slots)
            try:
                print(f"DEBUG: total_sous_slots={total_sous_slots}, nb_iterations={nb_iterations}")
            except Exception:
                pass
        except Exception:
            nb_iterations = 1200
        
        # Garder trace du meilleur planning trouvé
        meilleur_score = float('-inf')
        meilleur_planning = None
        meilleure_assignation = None
        # Alternatives avec le même score
        alternatives = []
        signatures_vues = set()
        
        # Générer plusieurs plannings et garder le meilleur
        for iter_idx in range(nb_iterations):
            # Réinitialiser le planning pour cette itération
            jours_iter = list(self.planning.keys())
            shifts_iter = list(next(iter(self.planning.values())).keys()) if self.planning else list(Horaire.get_all_shifts())
            planning_test = {jour: {shift: None for shift in shifts_iter}
                            for jour in jours_iter}
            # Progress callback
            if progress_cb is not None:
                try:
                    progress_cb(iter_idx + 1, nb_iterations)
                except Exception:
                    pass
            
            # Réinitialiser les shifts assignés pour cette itération
            for travailleur in self.travailleurs:
                travailleur.shifts_assignes = 0
            
            # Mélanger l'ordre des jours et des shifts pour diversifier les solutions
            jours = list(self.planning.keys())
            shifts = list(next(iter(self.planning.values())).keys()) if self.planning else list(Horaire.get_all_shifts())
            random.shuffle(jours)
            
            # Pour chaque jour et shift, assigner un travailleur disponible
            for jour in jours:
                for shift in shifts:
                    cap = int(self.capacites.get(jour, {}).get(shift, 1))
                    assigned_names = []
                    # Affecter jusqu'à cap travailleurs
                    for _ in range(cap):
                        travailleurs_disponibles = []
                        for travailleur in self.travailleurs:
                            if travailleur.nom in assigned_names:
                                continue
                            conditions_ok = (
                                travailleur.est_disponible(jour, shift)
                                and not self.travailleur_a_shift_adjacent(travailleur.nom, jour, shift, planning_test)
                            )
                            if not conditions_ok:
                                continue
                            # Interdire deux gardes le même jour (même si non adjacentes)
                            if self.travailleur_travaille_jour(travailleur.nom, jour, planning_test):
                                continue
                            if not self.respecte_limites_par_personne(travailleur.nom, jour, shift, planning_test):
                                continue
                            if travailleur.shifts_assignes < travailleur.nb_shifts_souhaites:
                                jours_consecutifs = self.compter_jours_consecutifs(travailleur.nom, jour, planning_test)
                                if jours_consecutifs < 6:
                                    travailleurs_disponibles.append(travailleur)
                        if not travailleurs_disponibles:
                            break
                        def _fairness_key(t):
                            denom = max(1, t.nb_shifts_souhaites)
                            ratio = t.shifts_assignes / denom
                            deficit = t.shifts_assignes - t.nb_shifts_souhaites
                            return (ratio, deficit, t.shifts_assignes)
                        travailleurs_disponibles.sort(key=_fairness_key)
                        # Éviter deux gardes d'affilée en priorité
                        choisi = next((t for t in travailleurs_disponibles if not self.travailleur_a_shift_adjacent(t.nom, jour, shift, planning_test) and not self.travailleur_travaille_jour(t.nom, jour, planning_test)), travailleurs_disponibles[0])
                        assigned_names.append(choisi.nom)
                        choisi.shifts_assignes += 1
                        planning_test[jour][shift] = " / ".join(assigned_names)
                    # Important: si assigned_names < cap, laisser des places vides (tolérées pour variantes)
            
            # Tenter de redistribuer les trous pour éviter de les concentrer le même jour
            planning_ameliore = self.redistribuer_trous(planning_test)
            
            # Calculer le score de ce planning
            score = self.calculer_score_planning(planning_ameliore)
            
            # Si ce planning est meilleur que le précédent, le garder
            if score > meilleur_score + 1e-6:
                meilleur_score = score
                jours_dyn = list(planning_ameliore.keys())
                shifts_dyn = list(next(iter(planning_ameliore.values())).keys()) if planning_ameliore else list(Horaire.get_all_shifts())
                meilleur_planning = {jour: {shift: planning_ameliore[jour][shift] 
                                          for shift in shifts_dyn}
                                    for jour in jours_dyn}
                # Réinitialiser les alternatives avec la nouvelle meilleure solution
                alternatives = [copy.deepcopy(meilleur_planning)]
                signatures_vues = {self._signature_planning(meilleur_planning)}
                # Recalculer les shifts assignés après redistribution pour cohérence
                counts = {t.nom: 0 for t in self.travailleurs}
                for jour in jours_dyn:
                    for shift in shifts_dyn:
                        nom = meilleur_planning[jour][shift]
                        if nom:
                            counts[nom] = counts.get(nom, 0) + 1
                meilleure_assignation = counts
            elif abs(score - meilleur_score) <= 20 and meilleur_planning is not None:
                # Ajouter comme alternative si différente
                jours_dyn = list(planning_ameliore.keys())
                shifts_dyn = list(next(iter(planning_ameliore.values())).keys()) if planning_ameliore else list(Horaire.get_all_shifts())
                candidat = {jour: {shift: planning_ameliore[jour][shift] 
                                   for shift in shifts_dyn}
                            for jour in jours_dyn}
                sig = self._signature_planning(candidat)
                if sig not in signatures_vues:
                    alternatives.append(copy.deepcopy(candidat))
                    signatures_vues.add(sig)
        
        # Restaurer le meilleur planning trouvé
        self.planning = meilleur_planning
        
        # Restaurer les shifts assignés
        for travailleur in self.travailleurs:
            if travailleur.nom in meilleure_assignation:
                travailleur.shifts_assignes = meilleure_assignation[travailleur.nom]
        
        # Stocker les alternatives et l'index courant + variantes intra-jour
        voisins = self._generate_same_day_swaps(meilleur_planning)
        for cand in voisins:
            sc = self.calculer_score_planning(cand)
            if abs(sc - meilleur_score) <= 20:
                sig = self._signature_planning(cand)
                if sig not in signatures_vues:
                    alternatives.append(copy.deepcopy(cand))
                    signatures_vues.add(sig)
        self.alternatives = alternatives if alternatives else [copy.deepcopy(self.planning)]
        self.best_score = meilleur_score
        self.current_alternative_index = 0

    def _signature_planning(self, planning_dict):
        """Construit une signature immuable du planning pour déduplication."""
        jours_dyn = list(planning_dict.keys())
        shifts_dyn = list(next(iter(planning_dict.values())).keys()) if planning_dict else []
        return tuple(
            (jour, tuple((shift, planning_dict[jour][shift]) for shift in shifts_dyn))
            for jour in jours_dyn
        )

    def _recompute_shifts_assignes_from(self, planning_dict):
        counts = {t.nom: 0 for t in self.travailleurs}
        for jour, shifts_map in planning_dict.items():
            for shift, nom in shifts_map.items():
                if nom:
                    counts[nom] = counts.get(nom, 0) + 1
        for t in self.travailleurs:
            t.shifts_assignes = counts.get(t.nom, 0)

    def _names_in_cell(self, planning_dict, jour, shift):
        val = planning_dict[jour][shift]
        if not val:
            return []
        return [n.strip() for n in str(val).split(" / ") if n.strip()]

    def _write_names_in_cell(self, planning_dict, jour, shift, names_list):
        planning_dict[jour][shift] = " / ".join(names_list) if names_list else None

    def _generate_same_day_swaps(self, planning_base):
        candidats = []
        jours = list(planning_base.keys())
        shifts = list(next(iter(planning_base.values())).keys()) if planning_base else []
        for jour in jours:
            for s1 in shifts:
                noms_s1 = self._names_in_cell(planning_base, jour, s1)
                for nom in noms_s1:
                    for s2 in shifts:
                        if s2 == s1:
                            continue
                        cap_s2 = int(self.capacites.get(jour, {}).get(s2, 1))
                        noms_s2 = self._names_in_cell(planning_base, jour, s2)
                        if len(noms_s2) >= cap_s2 or nom in noms_s2:
                            continue
                        cand = copy.deepcopy(planning_base)
                        self._write_names_in_cell(cand, jour, s1, [n for n in noms_s1 if n != nom])
                        self._write_names_in_cell(cand, jour, s2, noms_s2 + [nom])
                        if self.travailleur_a_shift_adjacent(nom, jour, s2, cand):
                            continue
                        candidats.append(cand)
        return candidats

    def next_alternative(self):
        """Passe à l'alternative suivante si disponible. Retourne True si changé."""
        if not self.alternatives:
            return False
        self.current_alternative_index = (self.current_alternative_index + 1) % len(self.alternatives)
        self.planning = copy.deepcopy(self.alternatives[self.current_alternative_index])
        self._recompute_shifts_assignes_from(self.planning)
        return True

    def prev_alternative(self):
        """Revient à l'alternative précédente si disponible. Retourne True si changé."""
        if not self.alternatives:
            return False
        self.current_alternative_index = (self.current_alternative_index - 1) % len(self.alternatives)
        self.planning = copy.deepcopy(self.alternatives[self.current_alternative_index])
        self._recompute_shifts_assignes_from(self.planning)
        return True

    def get_alternative_info(self):
        """Retourne (total, index_courant_1_based, best_score)."""
        total = len(self.alternatives) if self.alternatives else 0
        index_1 = (self.current_alternative_index + 1) if self.current_alternative_index >= 0 else 0
        return total, index_1, self.best_score

    def redistribuer_trous(self, planning):
        """Essaie d'étaler les trous (shifts None) sur différents jours quand possible.
        Idée: si un jour a plus d'un trou et un autre jour a 0 trou, on tente un swap
        en déplaçant un shift d'un jour plein vers le jour qui a trop de trous,
        en respectant les contraintes principales.
        """
        # Utiliser la configuration dynamique du planning fourni
        jours = list(planning.keys())
        shifts = list(next(iter(planning.values())).keys()) if planning else []

        # Compter les trous par jour
        trous_par_jour = {jour: sum(1 for s in shifts if planning[jour].get(s) is None) for jour in jours}

        # Si aucun jour n'a plus d'un trou, rien à faire
        if all(n <= 1 for n in trous_par_jour.values()):
            return planning

        # Tenter quelques passes pour améliorer
        for _ in range(10):
            # Trouver un jour surchargé en trous et un jour sans trou
            jour_trop_trous = next((j for j, n in trous_par_jour.items() if n > 1), None)
            jour_sans_trou = next((j for j, n in trous_par_jour.items() if n == 0), None)
            if not jour_trop_trous or not jour_sans_trou:
                break

            # Chercher un shift assigné au jour sans trou qui pourrait être déplacé
            deplace = False
            for shift in shifts:
                nom_travailleur = planning[jour_sans_trou][shift]
                if nom_travailleur is None:
                    continue

                travailleur = self._get_travailleur_par_nom(nom_travailleur)
                if not travailleur:
                    continue

                # Conditions pour déplacer ce shift vers le jour à trous:
                # - travailleur disponible ce jour et ce shift
                # - pas de shift adjacent créé
                # - pas dépasser limites (nuit, jours consécutifs)
                if (travailleur.est_disponible(jour_trop_trous, shift) and
                    not self.travailleur_a_shift_adjacent(travailleur.nom, jour_trop_trous, shift, planning) and
                    not (shift == "22-06" and self.compter_shifts_nuit(travailleur.nom, planning) >= 3) and
                    self.compter_jours_consecutifs(travailleur.nom, jour_trop_trous, planning) < 6):

                    # Trouver une case vide dans le jour surchargé
                    for shift_cible in shifts:
                        if planning[jour_trop_trous][shift_cible] is None:
                            # Déplacer
                            planning[jour_trop_trous][shift_cible] = nom_travailleur
                            planning[jour_sans_trou][shift] = None
                            trous_par_jour[jour_trop_trous] -= 1
                            trous_par_jour[jour_sans_trou] += 1
                            deplace = True
                            break
                if deplace:
                    break

            if not deplace:
                # Impossible de déplacer dans cette configuration, sortir
                break

        return planning

    def generer_planning(self, mode_12h: bool = False, progress_cb: Callable | None = None):
        """Méthode principale pour générer le planning"""
        self.mode_12h = mode_12h
        
        # Réinitialiser le planning en conservant la configuration actuelle (jours/shifts dynamiques)
        jours_iter = list(self.planning.keys()) if self.planning else list(Horaire.get_all_jours())
        shifts_iter = list(next(iter(self.planning.values())).keys()) if self.planning else list(Horaire.get_all_shifts())
        self.planning = {jour: {shift: None for shift in shifts_iter} for jour in jours_iter}
        
        # Réinitialiser les shifts assignés pour tous les travailleurs
        for travailleur in self.travailleurs:
            travailleur.shifts_assignes = 0
        
        # Générer le planning optimisé sans combler les trous
        self.generer_planning_optimise(progress_cb=progress_cb)
        
        # Ne pas combler les trous automatiquement
        # La méthode combler_trous() sera appelée séparément si l'utilisateur le souhaite

    def afficher_planning(self):
        print("\nPlanning de la semaine:")
        print("=" * 80)
        shifts_dyn = self._ordered_shifts()
        print(f"{'Jour':<12}" + "".join(f"{s:<20}" for s in shifts_dyn))
        print("-" * 80)
        
        for jour in self._ordered_days():
            ligne = f"{jour:<12}"
            for shift in shifts_dyn:
                travailleur = self.planning[jour][shift]
                ligne += f"{travailleur if travailleur else 'Non assigné':<20}"
            print(ligne)

    def sauvegarder(self, nom=None, site_id=None):
        """Sauvegarde le planning dans la base de données"""
        if not nom:
            # Générer un nom par défaut avec la date
            nom = f"Planning du {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Utiliser le site_id fourni ou celui du planning
        site_a_utiliser = site_id if site_id is not None else self.site_id
        
        db = Database()
        planning_id = db.sauvegarder_planning(self, nom, site_a_utiliser)
        return planning_id

    @staticmethod
    def charger(planning_id):
        """Charge un planning depuis la base de données"""
        db = Database()
        return db.charger_planning(planning_id)

    @staticmethod
    def lister_plannings(site_id=None):
        """Liste tous les plannings d'un site ou tous les plannings"""
        db = Database()
        return db.lister_plannings_par_site(site_id)

    def combler_trous(self):
        """Comble les trous dans le planning sans tenir compte des shifts souhaités"""
        # Identifier les "places" non assignées en tenant compte de la capacité
        shifts_non_assignes = []
        jours_dyn = list(self.planning.keys())
        shifts_dyn = list(next(iter(self.planning.values())).keys()) if self.planning else []
        for jour in jours_dyn:
            for shift in shifts_dyn:
                cap = int(self.capacites.get(jour, {}).get(shift, 1))
                val = self.planning[jour][shift]
                assignes = 0
                noms = []
                if val:
                    noms = [n.strip() for n in str(val).split(" / ") if n.strip()]
                    assignes = len(noms)
                manquants = max(0, cap - assignes)
                for _ in range(manquants):
                    shifts_non_assignes.append((jour, shift))
        
        # Si aucun trou, rien à faire
        if not shifts_non_assignes:
            print("Aucun trou à combler dans le planning.")
            return 0, 0
        
        print(f"Trous à combler: {len(shifts_non_assignes)}")
        
        # Pour chaque trou, trouver un travailleur disponible
        for jour, shift in shifts_non_assignes:
            print(f"\nTentative de combler le trou pour {jour} {shift}")
            
            # Afficher les disponibilités pour débogage
            self.debug_disponibilites(jour, shift)
            
            # Ensemble des noms déjà affectés ce jour (tous shifts et sous-cases)
            deja_affectes_ce_jour = set()
            for s_chk, val_chk in self.planning[jour].items():
                if val_chk:
                    for n in str(val_chk).split(" / "):
                        n = n.strip()
                        if n:
                            deja_affectes_ce_jour.add(n)
            print(f"  Déjà affectés le {jour}: {sorted(list(deja_affectes_ce_jour))}")
            
            # Trouver les travailleurs disponibles pour ce shift
            travailleurs_disponibles = []
            for travailleur in self.travailleurs:
                if travailleur.est_disponible(jour, shift):
                    # Toujours éviter deux gardes d'affilée, même en mode 12h
                    if self.travailleur_a_shift_adjacent(travailleur.nom, jour, shift):
                        print(f"  {travailleur.nom} a un shift adjacent, ignoré")
                        continue
                    # Interdire deux gardes le même jour (complément de sécurité)
                    if travailleur.nom in deja_affectes_ce_jour:
                        print(f"  {travailleur.nom} déjà affecté le {jour}, ignoré")
                        continue
                    # Respecter la limite max par personne pour ce type de shift
                    if not self.respecte_limites_par_personne(travailleur.nom, jour, shift):
                        print(f"  {travailleur.nom} atteindrait la limite max pour {shift}, ignoré")
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
                        # Même en assouplissement, interdire les gardes consécutives
                        if self.travailleur_a_shift_adjacent(travailleur.nom, jour, shift):
                            continue
                        # Et interdire deux gardes le même jour
                        if travailleur.nom in deja_affectes_ce_jour:
                            continue
                        # Même en assouplissement, ne pas dépasser la limite max par personne
                        if not self.respecte_limites_par_personne(travailleur.nom, jour, shift):
                            continue
                        travailleurs_disponibles.append(travailleur)
                print(f"  Travailleurs disponibles (deuxième passe): {[t.nom for t in travailleurs_disponibles]}")
            
            # Assigner le shift au travailleur disponible
            if travailleurs_disponibles:
                # Prioriser ceux qui sont le plus en déficit par rapport à leur souhait
                # puis par ratio assignés/souhaités pour maintenir l'équité
                def _fairness_key_fill(t):
                    denom = max(1, t.nb_shifts_souhaites)
                    ratio = t.shifts_assignes / denom
                    deficit = t.shifts_assignes - t.nb_shifts_souhaites
                    return (deficit, ratio, t.shifts_assignes)

                # Priorité supplémentaire: placer d'abord ceux en dessous de leur souhait
                sous_objectif = [t for t in travailleurs_disponibles if t.shifts_assignes < t.nb_shifts_souhaites]
                if sous_objectif:
                    sous_objectif.sort(key=_fairness_key_fill)
                    travailleur = next((t for t in sous_objectif if not self.travailleur_a_shift_adjacent(t.nom, jour, shift)), sous_objectif[0])
                else:
                    travailleurs_disponibles.sort(key=_fairness_key_fill)
                    travailleur = next((t for t in travailleurs_disponibles if not self.travailleur_a_shift_adjacent(t.nom, jour, shift)), travailleurs_disponibles[0])
                print(f"  Assignation à {travailleur.nom} (shifts assignés: {travailleur.shifts_assignes})")
                
                # Ne pas affecter si cela crée deux gardes d'affilée
                if self.travailleur_a_shift_adjacent(travailleur.nom, jour, shift):
                    print(f"  {travailleur.nom} aurait deux gardes d'affilée, ignoré")
                    continue
                # Sécurité finale: ne pas dépasser la limite au moment d'écrire
                if not self.respecte_limites_par_personne(travailleur.nom, jour, shift):
                    print(f"  {travailleur.nom} dépasserait la limite max pour {shift}, ignoré")
                    continue
                val = self.planning[jour][shift]
                if val:
                    existants = [n.strip() for n in str(val).split(" / ") if n.strip()]
                    if travailleur.nom in existants:
                        continue
                else:
                    existants = []
                existants.append(travailleur.nom)
                self.planning[jour][shift] = " / ".join(existants)
                # Mettre à jour le set du jour pour les trous suivants de la même journée
                deja_affectes_ce_jour.add(travailleur.nom)
                travailleur.shifts_assignes += 1
            else:
                print(f"  Impossible de combler le trou: aucun travailleur disponible")

        return trous_combles, len(shifts_non_assignes)

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
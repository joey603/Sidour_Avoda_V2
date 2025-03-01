class Travailleur:
    def __init__(self, nom, disponibilites, nb_shifts_souhaites):
        self.nom = nom
        # disponibilites sera un dictionnaire avec les jours comme clés
        # et une liste des horaires disponibles comme valeurs
        self.disponibilites = disponibilites
        self.disponibilites_12h = {}  # Pour les gardes de 12h (matin_12h: 06-18, nuit_12h: 18-06)
        self.nb_shifts_souhaites = nb_shifts_souhaites
        self.shifts_assignes = 0

    def est_disponible(self, jour, shift):
        """Vérifie si le travailleur est disponible pour un jour et un shift donnés"""
        return jour in self.disponibilites and shift in self.disponibilites[jour]
        
    def est_disponible_12h(self, jour, type_12h):
        """Vérifie si le travailleur est disponible pour une garde de 12h un jour donné"""
        return jour in self.disponibilites_12h and type_12h in self.disponibilites_12h[jour] 
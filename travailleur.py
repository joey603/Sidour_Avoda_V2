class Travailleur:
    def __init__(self, nom, disponibilites, nb_shifts_souhaites):
        self.nom = nom
        # disponibilites sera un dictionnaire avec les jours comme clés
        # et une liste des horaires disponibles comme valeurs
        self.disponibilites = disponibilites
        self.nb_shifts_souhaites = nb_shifts_souhaites
        self.shifts_assignes = 0

    def est_disponible(self, jour, shift):
        """Vérifie si le travailleur est disponible pour un jour et un shift donnés"""
        return jour in self.disponibilites and shift in self.disponibilites[jour] 
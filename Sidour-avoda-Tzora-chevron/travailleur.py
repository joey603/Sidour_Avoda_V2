class Travailleur:
    def __init__(self, nom, disponibilites, nb_shifts_souhaites, site_id=1):
        self.nom = nom
        self.disponibilites = disponibilites
        self.disponibilites_12h = {}
        self.nb_shifts_souhaites = nb_shifts_souhaites
        self.shifts_assignes = 0
        self.site_id = site_id

    def est_disponible(self, jour, shift):
        return jour in self.disponibilites and shift in self.disponibilites[jour]

    def est_disponible_12h(self, jour, type_12h):
        return jour in self.disponibilites_12h and type_12h in self.disponibilites_12h[jour]



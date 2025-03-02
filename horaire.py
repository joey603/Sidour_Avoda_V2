class Horaire:
    SHIFTS = {
        "matin": "06-14",
        "apres_midi": "14-22",
        "nuit": "22-06"
    }
    
    JOURS = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]

    @staticmethod
    def get_all_shifts():
        return Horaire.SHIFTS.values()

    @staticmethod
    def get_all_jours():
        return Horaire.JOURS 
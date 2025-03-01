class Horaire:
    SHIFTS = {
        "matin": "06-14",
        "apres_midi": "14-22",
        "nuit": "22-06"
    }
    
    JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

    @staticmethod
    def get_all_shifts():
        return Horaire.SHIFTS.values()

    @staticmethod
    def get_all_jours():
        return Horaire.JOURS 
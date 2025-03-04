class Horaire:
    SHIFTS = {
        "matin": "06-14",
        "apres_midi": "14-22",
        "nuit": "22-06"
    }
    
    JOURS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    @staticmethod
    def get_all_shifts():
        return Horaire.SHIFTS.values()

    @staticmethod
    def get_all_jours():
        return Horaire.JOURS 
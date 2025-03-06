import sys
import os
import traceback
from interface import InterfacePlanning
import tkinter as tk

def resource_path(relative_path):
    """Obtenir le chemin absolu des ressources"""
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def main():
    try:
        # Création de l'interface avec 8 heures de repos minimum entre les gardes
        app = InterfacePlanning(repos_minimum_entre_gardes=8)
        
        # Configurer l'icône et le titre
        icon_path = resource_path("assets/calender-2389150_960_720.png")
        app.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        app.root.title("Sidour Avoda")
        
        # Lancer l'application
        app.run()
    except Exception as e:
        # Enregistrer l'erreur dans un fichier
        with open(os.path.expanduser("~/sidour_avoda_error.log"), "w") as f:
            f.write(f"Erreur: {str(e)}\n")
            f.write(traceback.format_exc())
        
        # Afficher l'erreur dans une fenêtre si possible
        try:
            root = tk.Tk()
            root.withdraw()
            tk.messagebox.showerror("Erreur", f"Une erreur s'est produite: {str(e)}\nConsultez le fichier ~/sidour_avoda_error.log pour plus de détails.")
            root.destroy()
        except:
            pass
        
        # Réafficher l'erreur dans la console
        print(f"Erreur: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 
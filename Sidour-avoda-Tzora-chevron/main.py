import sys
import os
import traceback
# Rendre robustes les imports quand packagé
base_dir = None
try:
    base_dir = sys._MEIPASS  # dossier d'extraction PyInstaller
except Exception:
    base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir and base_dir not in sys.path:
    sys.path.insert(0, base_dir)
# Si interface.py a été inclus comme data, ajouter aussi le répertoire courant
cwd = os.getcwd()
if cwd and cwd not in sys.path:
    sys.path.append(cwd)
from interface import InterfacePlanning
import threading

# Application metadata for auto-update
APP_NAME = "Sidour Avoda"
APP_VERSION = "1.0.0"

def check_for_updates_in_background():
    """Check for app updates without blocking the UI. Safe no-op if not configured."""
    try:
        # Lazy import to avoid hard dependency if not packaged with updates configured
        from pyupdater.client import Client
        try:
            from client_config import ClientConfig
        except Exception:
            # No client config present, silently skip
            return
        client = Client(ClientConfig(), refresh=True)
        app_key = APP_NAME.lower().replace(" ", "-")
        app_update = client.update_check(app_key, APP_VERSION)
        if app_update:
            # Download and restart into the new version automatically
            app_update.download()
            if app_update.is_downloaded():
                app_update.extract_restart()
    except Exception:
        # Fail silently: updates are best-effort
        pass
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
        # Centrer la fenêtre au lancement et assurer une largeur suffisante
        try:
            app.root.update_idletasks()
            w = app.root.winfo_width() or app.root.winfo_reqwidth()
            h = app.root.winfo_height() or app.root.winfo_reqheight()
            # Valeurs de secours si non calculées
            if w <= 1:
                w = 1200
            if h <= 1:
                h = 700
            sw = app.root.winfo_screenwidth()
            sh = app.root.winfo_screenheight()
            x = max((sw - w) // 2, 0)
            y = max((sh - h) // 2, 0)
            app.root.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass
        
        # Lancer un check de mise à jour en arrière-plan (non bloquant)
        try:
            threading.Thread(target=check_for_updates_in_background, daemon=True).start()
        except Exception:
            pass

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
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}\nSee ~/sidour_avoda_error.log for details.")
            root.destroy()
        except Exception:
            pass
        
        # Réafficher l'erreur dans la console
        print(f"Erreur: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 
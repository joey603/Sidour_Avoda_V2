import sys
import os
import traceback
from interface import InterfacePlanning
import threading

# Application metadata for auto-update
APP_NAME = "Sidour Avoda"
APP_VERSION = "1.0.0"
GITHUB_OWNER = "joey603"
GITHUB_REPO = "Sidour_Avoda_V2"

def get_current_version() -> str:
    """Return the version embedded at build-time (version.txt), fallback to APP_VERSION."""
    try:
        version_path = resource_path("version.txt")
        if os.path.exists(version_path):
            with open(version_path, "r", encoding="utf-8") as f:
                v = f.read().strip()
                if v:
                    return v.lstrip("v")
    except Exception:
        pass
    return APP_VERSION


def _parse_version(version_str: str):
    try:
        vs = version_str.lstrip("v")
        parts = [int(p) for p in vs.split(".") if p.isdigit() or p.isnumeric()]
        # Normalize to 3 parts
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])
    except Exception:
        return (0, 0, 0)


def _get_latest_release_info():
    """Query GitHub Releases API for latest release info. Returns (tag, asset_url) or (None, None)."""
    try:
        import json
        from urllib.request import Request, urlopen
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
        req = Request(url, headers={"User-Agent": "SidourAvodaUpdater"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        tag = str(data.get("tag_name") or "").strip()
        assets = data.get("assets") or []
        asset_url = None
        # Prefer the installer asset
        for a in assets:
            name = (a.get("name") or "").lower()
            if "setup" in name and name.endswith(".exe"):
                asset_url = a.get("browser_download_url")
                break
        if not asset_url:
            # Fallback to any .exe
            for a in assets:
                name = (a.get("name") or "").lower()
                if name.endswith(".exe"):
                    asset_url = a.get("browser_download_url")
                    break
        if tag and asset_url:
            return tag.lstrip("v"), asset_url
    except Exception:
        pass
    return None, None


def _download_and_launch_installer(installer_url: str, tk_root=None):
    try:
        import tempfile
        import subprocess
        from urllib.request import Request, urlopen
        # Optional blocking modal
        modal = None
        if tk_root is not None:
            try:
                modal = tk.Toplevel(tk_root)
                modal.title("Updating...")
                modal.resizable(False, False)
                modal.transient(tk_root)
                modal.grab_set()
                modal.protocol("WM_DELETE_WINDOW", lambda: None)
                import tkinter.ttk as ttk
                frame = ttk.Frame(modal, padding=20)
                frame.pack(fill="both", expand=True)
                label = ttk.Label(frame, text="Downloading and installing update...\nPlease wait.")
                label.pack(pady=(0,10))
                bar = ttk.Progressbar(frame, mode='indeterminate', length=260)
                bar.pack()
                bar.start(12)
                tk_root.update_idletasks()
                w = modal.winfo_reqwidth() or 320
                h = modal.winfo_reqheight() or 120
                sw = tk_root.winfo_screenwidth(); sh = tk_root.winfo_screenheight()
                x = max((sw - w)//2, 0); y = max((sh - h)//2, 0)
                modal.geometry(f"{w}x{h}+{x}+{y}")
                tk_root.update()
            except Exception:
                modal = None
        # Download to temp
        req = Request(installer_url, headers={"User-Agent": "SidourAvodaUpdater"})
        with urlopen(req, timeout=30) as resp:
            content = resp.read()
        tmpdir = tempfile.mkdtemp(prefix="sidour_avoda_")
        installer_path = os.path.join(tmpdir, "Sidour-Avoda-Setup.exe")
        with open(installer_path, "wb") as f:
            f.write(content)
        # Launch installer silently if possible, then exit app
        # /CLOSEAPPLICATIONS and /RESTARTAPPLICATIONS demand the app to register itself, but we rely on relaunch in installer [Run]
        flags = ["/VERYSILENT", "/NORESTART", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"]
        try:
            subprocess.Popen([installer_path] + flags, close_fds=True, shell=False)
        except Exception:
            subprocess.Popen([installer_path], close_fds=True, shell=False)
        # If current exe is a versioned portable (SidourAvoda-v*.exe), schedule its deletion on next reboot
        try:
            import ctypes, sys
            exe_path = sys.executable
            base = os.path.basename(exe_path).lower()
            if base.startswith("sidouravoda-v") and base.endswith(".exe"):
                # MoveFileEx with MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
                ctypes.windll.kernel32.MoveFileExW(exe_path, None, 0x4)
        except Exception:
            pass
        # Hard-exit so installer can replace files
        os._exit(0)
    except Exception:
        pass


def check_for_updates_in_background(tk_root=None):
    """Check GitHub Releases in background. If newer, prompt user to update now.
    If a Tk root is provided, the prompt is scheduled on the UI thread.
    """
    try:
        # Only relevant on Windows packaged app
        if sys.platform != "win32":
            return
        current = get_current_version()
        latest, asset_url = _get_latest_release_info()
        if not latest or not asset_url:
            return
        if _parse_version(latest) <= _parse_version(current):
            return
        # Define prompt function
        def _prompt():
            try:
                from tkinter import messagebox
                if messagebox.askyesno(
                    "Update available",
                    f"A new version {latest} is available (you have {current}).\n\nDownload and install now?",
                    parent=tk_root if tk_root else None,
                ):
                    threading.Thread(target=_download_and_launch_installer, args=(asset_url, tk_root), daemon=True).start()
            except Exception:
                pass
        # Schedule on Tk main loop if possible
        if tk_root is not None:
            try:
                tk_root.after(0, _prompt)
                return
            except Exception:
                pass
        # Fallback: use Windows system MessageBox from this thread
        try:
            import ctypes
            MB_YESNO = 0x00000004
            MB_ICONINFORMATION = 0x00000040
            res = ctypes.windll.user32.MessageBoxW(
                0,
                f"A new version {latest} is available (you have {current}).\n\nDownload and install now?",
                "Sidour Avoda Update",
                MB_YESNO | MB_ICONINFORMATION,
            )
            IDYES = 6
            if res == IDYES:
                threading.Thread(target=_download_and_launch_installer, args=(asset_url, None), daemon=True).start()
        except Exception:
            pass
    except Exception:
        pass
import tkinter as tk

def resource_path(relative_path):
    """Obtenir le chemin absolu des ressources"""
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Utiliser le dossier du fichier courant (par ex. 'Sidour-avoda-Tzora-chevron')
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def main():
    try:
        # Création de l'interface avec 8 heures de repos minimum entre les gardes
        app = InterfacePlanning(repos_minimum_entre_gardes=8)
        
        # Configurer l'icône et le titre (tolérant si l'icône est absente)
        icon_path = resource_path("assets/calender-2389150_960_720.png")
        try:
            if os.path.exists(icon_path):
                app.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception:
            # En cas d'absence de fichier ou d'erreur Tk, ignorer silencieusement
            pass
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
            threading.Thread(target=lambda: check_for_updates_in_background(app.root), daemon=True).start()
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
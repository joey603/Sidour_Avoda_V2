import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
import random
from horaire import Horaire
from travailleur import Travailleur
from planning import Planning
from database import Database
import datetime

class InterfacePlanning:
    def __init__(self, repos_minimum_entre_gardes=8):
        self.repos_minimum_entre_gardes = repos_minimum_entre_gardes
        self.root = tk.Tk()
        self.root.title("Planning Manager")
        self.root.geometry("1400x750")
        self.root.configure(bg="#f0f0f0")
        
        # Variables pour la gestion des sites
        self.site_actuel_id = 1
        self.site_actuel_nom = tk.StringVar()
        self.sites_disponibles = []
        
        # Variables de base
        self.colors = ["#FFD700", "#87CEFA", "#98FB98", "#FFA07A", "#DDA0DD", "#AFEEEE", "#D8BFD8"]
        self.travailleur_colors = {}
        self.title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.header_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = tkfont.Font(family="Helvetica", size=10)
        
        self.planning = Planning()
        self.nom_var = tk.StringVar()
        self.nb_shifts_var = tk.StringVar()
        self.mode_edition = False
        self.travailleur_en_edition = None
        
        # Disponibilités
        self.disponibilites = {jour: {shift: tk.BooleanVar() 
            for shift in Horaire.SHIFTS.values()}
            for jour in Horaire.JOURS}
        
        self.disponibilites_12h = {jour: {
            "matin_12h": tk.BooleanVar(),
            "nuit_12h": tk.BooleanVar()
        } for jour in Horaire.JOURS}
        
        # Interface de base
        self.creer_interface_minimal()
        
    def creer_interface_minimal(self):
        # Interface ultra-simple pour tester
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        label = ttk.Label(main_frame, text="Minimal interface - Sites management test")
        label.pack(pady=20)
        
        btn_test = ttk.Button(main_frame, text="Test OK - Interface works!",
                              command=lambda: messagebox.showinfo("Test", "Interface works!"))
        btn_test.pack(pady=10)
    
    def run(self):
        self.root.mainloop() 
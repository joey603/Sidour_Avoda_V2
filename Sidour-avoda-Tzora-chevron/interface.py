import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
import random
import threading
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
        self.root.geometry("1400x750")  # Augmenté la largeur pour le sélecteur de site
        self.root.configure(bg="#f0f0f0")
        
        # NOUVEAU: Variables pour la gestion des sites
        self.site_actuel_id = 1  # Site par défaut
        self.site_actuel_nom = tk.StringVar()
        self.sites_disponibles = []
        
        # NOUVEAU: Dictionnaire de traduction français -> anglais pour l'affichage
        self.jours_traduction = {
            "dimanche": "Sunday",
            "lundi": "Monday", 
            "mardi": "Tuesday",
            "mercredi": "Wednesday",
            "jeudi": "Thursday",
            "vendredi": "Friday",
            "samedi": "Saturday"
        }
        
        # Définition des couleurs
        self.colors = ["#FFD700", "#87CEFA", "#98FB98", "#FFA07A", "#DDA0DD", "#AFEEEE", "#D8BFD8"]
        self.travailleur_colors = {}
        
        # Palette de couleurs professionnelle - couleurs plus vives
        self.primary_color = "#1a237e"    # Bleu très foncé
        self.secondary_color = "#4285f4"  # Bleu Google
        self.accent_color = "#f44336"     # Rouge Material
        self.success_color = "#4caf50"    # Vert Material
        self.warning_color = "#ff9800"    # Orange Material
        self.light_bg = "#f5f5f5"         # Gris très clair
        self.dark_bg = "#263238"          # Bleu-gris très foncé
        
        # Police personnalisée
        self.title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.header_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = tkfont.Font(family="Helvetica", size=10)
        
        self.planning = Planning()
        # Etat UI: planning généré ou non
        self._has_generated_planning = False
        
        # Variables pour le formulaire
        self.nom_var = tk.StringVar()
        self.nb_shifts_var = tk.StringVar()
        self.mode_edition = False
        self.travailleur_en_edition = None
        # Compteur pour la liste des travailleurs
        self.nb_workers_var = tk.StringVar(value="")
        
        # Création des disponibilités (sera reconstruit selon les réglages du site)
        self.disponibilites = {}
        self.disponibilites_12h = {}
        
        # NOUVEAU: Charger les sites et créer l'interface
        self.charger_sites()
        # Construire les structures de disponibilités selon réglages
        self._rebuild_disponibilites_from_settings()
        self.creer_interface()
        
        # Charger les travailleurs après l'initialisation de l'interface
        self.charger_travailleurs_db()

    def charger_sites(self):
        """Charge la liste des sites disponibles"""
        db = Database()
        self.sites_disponibles = db.charger_sites()
        if self.sites_disponibles:
            self.site_actuel_id = self.sites_disponibles[0]['id']
            self.site_actuel_nom.set(self.sites_disponibles[0]['nom'])
            # Charger aussi les réglages du site (jours/shifts)
            self._charger_reglages_site_actuel()

    def creer_interface(self):
        # Frame principale avec deux colonnes
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # NOUVEAU: Frame pour la sélection de site en haut
        site_frame = ttk.Frame(main_frame)
        site_frame.pack(fill="x", pady=(0, 10))
        
        # Sélecteur de site
        ttk.Label(site_frame, text="Current site:", font=self.header_font).pack(side="left", padx=(0, 10))
        
        site_values = [site['nom'] for site in self.sites_disponibles]
        self.site_combobox = ttk.Combobox(site_frame, textvariable=self.site_actuel_nom, 
                                         values=site_values, state="readonly", width=25)
        self.site_combobox.pack(side="left", padx=(0, 10))
        self.site_combobox.bind('<<ComboboxSelected>>', self.changer_site)
        
        # Bouton pour ajouter un site
        btn_add_site = self.create_styled_button(site_frame, "➕ Add Site", 
                                                 self.ouvrir_ajout_site, "load")
        btn_add_site.pack(side="left", padx=(10, 0))
        # Bouton pour gérer le site sélectionné
        btn_gerer_sites = self.create_styled_button(site_frame, "⚙️ Manage Site", 
                                                   self.ouvrir_gestion_sites, "load")
        btn_gerer_sites.pack(side="left", padx=(10, 0))
        
        # Séparateur
        ttk.Separator(main_frame, orient='horizontal').pack(fill="x", pady=5)
        
        # Style pour les widgets
        style = ttk.Style()
        style.configure("TLabel", background="#f0f0f0", font=self.normal_font)
        style.configure("TFrame", background="#f0f0f0")
        
        # Styles améliorés pour les boutons et les sections
        style.configure("TButton", font=self.normal_font, padding=6)
        
        # Créer des styles de boutons personnalisés sans modifier les couleurs de fond/texte
        # qui peuvent causer des problèmes avec certains thèmes ttk
        style.configure("Action.TButton", font=self.normal_font, padding=8)
        style.configure("Cancel.TButton", font=self.normal_font, padding=8)
        
        style.configure("Section.TLabelframe", background="#f0f0f0", borderwidth=2, relief="ridge")
        style.configure("Section.TLabelframe.Label", background="#f0f0f0", font=self.header_font, foreground="#2c3e50")
        
        style.configure("TCheckbutton", background="#f0f0f0")
        style.configure("TLabelframe", background="#f0f0f0", font=self.header_font)
        style.configure("TLabelframe.Label", background="#f0f0f0", font=self.header_font)
        
        # Colonne gauche - Outils et liste des travailleurs (plus étroit)
        left_frame = ttk.Frame(main_frame, padding=10, width=360)
        left_frame.pack(side=tk.LEFT, fill="y")
        left_frame.pack_propagate(False)
        
        # Configurer left_frame pour qu'il s'adapte à la taille de la fenêtre
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=0)  # Titre
        left_frame.rowconfigure(1, weight=1)  # Liste
        left_frame.rowconfigure(2, weight=0)  # Boutons génération
        left_frame.rowconfigure(3, weight=0)  # Boutons DB
        
        # Titre modifié pour inclure le site
        self.titre_label = ttk.Label(left_frame, text=f"Planning workers - {self.site_actuel_nom.get()}", 
                                    font=self.title_font)
        self.titre_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # (Toolbar supprimée) Le bouton Add est déplacé dans la section "Workers registered"
        
        # Liste des travailleurs
        liste_frame = ttk.Frame(left_frame)
        liste_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        liste_frame.columnconfigure(0, weight=1)
        liste_frame.rowconfigure(0, weight=1)
        self.creer_liste_travailleurs(liste_frame)
        
        # Frame pour les boutons de génération
        frame_generation = ttk.Frame(left_frame)
        frame_generation.grid(row=2, column=0, sticky="ew", pady=10)
        frame_generation.columnconfigure(0, weight=1)
        frame_generation.columnconfigure(1, weight=1)
        frame_generation.columnconfigure(2, weight=1)
        frame_generation.columnconfigure(3, weight=1)
        frame_generation.columnconfigure(4, weight=1)
        
        # Boutons pour générer le planning - utiliser des boutons tk standard pour plus de contrôle visuel
        self.btn_generer_planning = self.create_styled_button(frame_generation, "🧮 Planning creation", 
                                              self.generer_planning_async, "action")
        self.btn_generer_planning.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.btn_fill_holes = self.create_styled_button(frame_generation, "🧩 Fill holes", 
                                             self.combler_trous, "action")
        self.btn_fill_holes.grid(row=0, column=1, padx=5, sticky="ew")
        # Removed 12h generation button

        # Boutons pour parcourir les alternatives de même score
        self.btn_prev_alt = self.create_styled_button(frame_generation, "⬅️ Previous alternative", 
                                                 self.prev_alternative_planning, "action")
        self.btn_prev_alt.grid(row=0, column=3, padx=5, sticky="ew")

        self.btn_next_alt = self.create_styled_button(frame_generation, "➡️ Next alternative", 
                                                 self.next_alternative_planning, "action")
        self.btn_next_alt.grid(row=0, column=4, padx=5, sticky="ew")

        # Label d'information sur les alternatives
        self.alt_info_var = tk.StringVar(value="")
        alt_info_label = ttk.Label(frame_generation, textvariable=self.alt_info_var)
        alt_info_label.grid(row=1, column=0, columnspan=5, sticky="w", padx=5)
        
        # Désactiver par défaut tant qu'aucun planning n'est créé
        try:
            self.btn_fill_holes.configure(state=tk.DISABLED)
            self.btn_prev_alt.configure(state=tk.DISABLED)
            self.btn_next_alt.configure(state=tk.DISABLED)
        except Exception:
            pass
        
        # Frame pour la sauvegarde et le chargement
        frame_db = ttk.Frame(left_frame)
        frame_db.grid(row=3, column=0, sticky="ew", pady=10)
        frame_db.columnconfigure(0, weight=1)
        frame_db.columnconfigure(1, weight=1)
        frame_db.columnconfigure(2, weight=1)
        
        btn_sauvegarder = self.create_styled_button(frame_db, "💾 Save Planning", 
                                                 self.sauvegarder_planning, "save")
        btn_sauvegarder.grid(row=0, column=0, padx=5, sticky="ew")
        
        btn_agenda = self.create_styled_button(frame_db, "📅 Agenda Plannings", 
                                                self.ouvrir_agenda_plannings, "load")
        btn_agenda.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Zone centrale contenant la colonne gauche (workers) et droite (week planning)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=3)  # donner plus d'espace au week planning
        content_frame.rowconfigure(0, weight=1)
        
        # Colonne droite - Affichage du planning
        right_frame = ttk.Frame(content_frame, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")
        # Assurer une largeur minimale confortable
        right_frame.update_idletasks()
        try:
            right_frame.minsize(900, 400)
        except Exception:
            pass
        
        # Title
        titre_planning = ttk.Label(right_frame, text="Week Planning", font=self.title_font)
        titre_planning.pack(pady=(0, 20))
        
        # Creation of the canvas for the visual planning
        self.canvas_frame = ttk.Frame(right_frame, padding=5)
        self.canvas_frame.pack(fill="both", expand=True)
        # Donner plus d'espace horizontal au planning
        try:
            self.canvas_frame.columnconfigure(0, weight=1)
            self.canvas_frame.rowconfigure(0, weight=1)
        except Exception:
            pass
        
        # Initialisation du canvas vide
        self.creer_planning_visuel()

    def create_styled_button(self, parent, text, command, button_type="action", width: int = 150, height: int = 40):
        """Create a styled button with vibrant colors"""
        # Define vibrant colors to ensure they display
        if button_type == "action":
            bg_color = "#007BFF"  # Bright blue
            hover_color = "#0056b3"
        elif button_type == "cancel":
            bg_color = "#DC3545"  # Bright red
            hover_color = "#c82333"
        elif button_type == "save":
            bg_color = "#28A745"  # Vert vif
            hover_color = "#218838"
        elif button_type == "load":
            bg_color = "#FFC107"  # Jaune vif
            hover_color = "#e0a800"
            fg_color = "black"    # Texte noir pour le jaune
        elif button_type == "secondary":
            bg_color = "#6c757d"  # Gris foncé
            hover_color = "#5a6268"
        else:
            bg_color = "#007BFF"
            hover_color = "#0056b3"
        
        # Couleur du texte (noir pour le jaune, blanc pour les autres)
        fg_color = "black" if button_type == "load" else "white"
        
        # Créer un Canvas pour le bouton personnalisé
        canvas_width = max(60, int(width))
        canvas_height = max(28, int(height))
        
        canvas = tk.Canvas(
            parent,
            width=canvas_width,
            height=canvas_height,
            bg=bg_color,
            highlightthickness=0,
            cursor="hand2",
            takefocus=0
        )
        
        # Ajouter le texte au centre du canvas
        text_id = canvas.create_text(
            canvas_width // 2,
            canvas_height // 2,
            text=text,
            fill=fg_color,
            font=self.normal_font
        )
        
        # Gestion du clic (sur relâchement) avec prévention de propagation
        def on_press(event):
            return "break"

        def on_release(event):
            if not getattr(canvas, "enabled", True):
                return "break"
            x, y = event.x, event.y
            if 0 <= x <= canvas.winfo_width() and 0 <= y <= canvas.winfo_height():
                # Debounce: temporarily unbind during execution
                try:
                    canvas.unbind("<ButtonRelease-1>")
                except Exception:
                    pass
                try:
                    command()
                finally:
                    try:
                        if canvas.winfo_exists():
                            canvas.bind("<ButtonRelease-1>", on_release)
                    except Exception:
                        pass
            return "break"
        
        # Fonctions pour les effets de survol
        def on_enter(event):
            canvas.config(bg=hover_color)
        
        def on_leave(event):
            canvas.config(bg=bg_color)
        
        # Lier les événements
        canvas.bind("<Button-1>", on_press)
        canvas.bind("<ButtonRelease-1>", on_release)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        
        # Stocker l'état du bouton
        canvas.enabled = True
        
        # Méthode pour activer/désactiver le bouton
        def configure(**kwargs):
            if "state" in kwargs:
                if kwargs["state"] == tk.DISABLED:
                    canvas.enabled = False
                    canvas.config(bg="#cccccc")  # Gris pour désactivé
                    canvas.unbind("<Button-1>")
                    canvas.unbind("<ButtonRelease-1>")
                    canvas.unbind("<Enter>")
                    canvas.unbind("<Leave>")
                else:
                    canvas.enabled = True
                    canvas.config(bg=bg_color)
                    canvas.bind("<Button-1>", on_press)
                    canvas.bind("<ButtonRelease-1>", on_release)
                    canvas.bind("<Enter>", on_enter)
                    canvas.bind("<Leave>", on_leave)
        
        # Ajouter la méthode configure au canvas
        canvas.configure = configure
        
        return canvas

    def creer_formulaire_travailleur(self, frame):
        # Frame pour le formulaire d'ajout de travailleur
        self.form_label_frame = ttk.LabelFrame(frame, text="Add a worker", padding=10, style="Section.TLabelframe")
        self.form_label_frame.grid(row=0, column=0, sticky="nsew")
        self.form_label_frame.columnconfigure(0, weight=1)
        self.form_label_frame.rowconfigure(0, weight=0)  # Info frame
        self.form_label_frame.rowconfigure(1, weight=1)  # Dispo frame
        self.form_label_frame.rowconfigure(2, weight=0)  # Boutons
        
        # Nom et nombre de shifts
        info_frame = ttk.Frame(self.form_label_frame)
        info_frame.grid(row=0, column=0, sticky="ew", pady=5)
        info_frame.columnconfigure(0, weight=0)
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(2, weight=0)
        info_frame.columnconfigure(3, weight=0)
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.nom_var, width=25).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(info_frame, text="Desired number of shifts:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.nb_shifts_var, width=5).grid(row=0, column=3, padx=5, pady=5)
        
        # Availability section (dynamic)
        self._build_availabilities_section()
        
        # Boutons
        btn_frame = ttk.Frame(self.form_label_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        # Utiliser des boutons stylisés
        self.btn_ajouter = self.create_styled_button(btn_frame, "Add worker", 
                                                  self.ajouter_travailleur, "action")
        self.btn_ajouter.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.btn_annuler = self.create_styled_button(btn_frame, "Cancel", 
                                                  self.annuler_edition, "cancel")
        self.btn_annuler.enabled = False
        self.btn_annuler.config(bg="#cccccc")
        self.btn_annuler.unbind("<Button-1>")
        self.btn_annuler.unbind("<Enter>")
        self.btn_annuler.unbind("<Leave>")
        self.btn_annuler.grid(row=0, column=1, padx=5, sticky="ew")

    def creer_liste_travailleurs(self, frame):
        # Liste des travailleurs
        frame_liste = ttk.LabelFrame(frame, text="Workers registered", padding=10, style="Section.TLabelframe")
        frame_liste.grid(row=0, column=0, sticky="nsew")
        frame_liste.columnconfigure(0, weight=1)
        frame_liste.columnconfigure(1, weight=0)
        frame_liste.rowconfigure(0, weight=1)  # Table
        frame_liste.rowconfigure(1, weight=0)  # Ligne des boutons
        
        # Style amélioré pour le tableau
        tv_style = ttk.Style()
        try:
            tv_style.configure('Workers.Treeview', font=self.normal_font, rowheight=26)
            tv_style.configure('Workers.Treeview.Heading', font=self.header_font, background="#e9ecef", foreground="#2c3e50")
            tv_style.map('Workers.Treeview', background=[('selected', '#cfe8ff')], foreground=[('selected', '#000000')])
        except Exception:
            pass

        # Création d'un Treeview pour afficher les travailleurs sous forme de tableau
        columns = ("nom", "shifts")
        self.table_travailleurs = ttk.Treeview(frame_liste, columns=columns, show="headings", height=10, style='Workers.Treeview')
        # Fonctions de tri
        def _sort_table(col, reverse=False):
            try:
                data = [(self.table_travailleurs.set(k, col), k) for k in self.table_travailleurs.get_children('')]
                if col == 'shifts':
                    def _as_int(val):
                        try:
                            return int(val)
                        except Exception:
                            return 0
                    data.sort(key=lambda x: _as_int(x[0]), reverse=reverse)
                else:
                    data.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)
                for idx, (_val, k) in enumerate(data):
                    self.table_travailleurs.move(k, '', idx)
                self.table_travailleurs.heading(col, command=lambda: _sort_table(col, not reverse))
            except Exception:
                pass

        self.table_travailleurs.heading("nom", text="Name", command=lambda: _sort_table('nom', False))
        self.table_travailleurs.heading("shifts", text="Desired shifts", command=lambda: _sort_table('shifts', False))
        
        self.table_travailleurs.column("nom", width=180, minwidth=160, anchor='w', stretch=True)
        self.table_travailleurs.column("shifts", width=110, minwidth=90, anchor='center', stretch=False)
        
        # Scrollbar pour la table
        scrollbar = ttk.Scrollbar(frame_liste, orient="vertical", command=self.table_travailleurs.yview)
        self.table_travailleurs.configure(yscrollcommand=scrollbar.set)
        
        # Placement de la table et de la scrollbar
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table_travailleurs.grid(row=0, column=0, sticky="nsew")

        # Tags pour zébrer les lignes
        try:
            self.table_travailleurs.tag_configure('evenrow', background='#ffffff')
            self.table_travailleurs.tag_configure('oddrow', background='#f7f7f7')
        except Exception:
            pass

        # Ligne des actions + compteur
        actions_row = ttk.Frame(frame_liste)
        actions_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        actions_row.columnconfigure(0, weight=1)
        ttk.Label(actions_row, textvariable=self.nb_workers_var).grid(row=0, column=0, sticky='w', padx=4)
        # Bouton Add moins large
        btn_add_small = self.create_styled_button(actions_row, "➕ Add worker", 
                                                  lambda: self.ouvrir_popup_travailleur(modifier=False), 
                                                  "action", width=120, height=34)
        btn_add_small.grid(row=0, column=1, padx=4, sticky="e")
        
        # Lier la sélection dans la table à l'édition
        self.table_travailleurs.bind('<<TreeviewSelect>>', self.selectionner_travailleur)


    def creer_planning_visuel(self):
        """Create a visual representation of the planning"""
        # Delete the old planning if it exists
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        # Créer un nouveau frame pour le planning
        planning_frame = ttk.Frame(self.canvas_frame)
        planning_frame.pack(fill="both", expand=True)
        
        # Assigner des couleurs aux travailleurs s'ils n'en ont pas déjà
        for travailleur in self.planning.travailleurs:
            if travailleur.nom not in self.travailleur_colors:
                # Assigner une couleur aléatoire parmi celles disponibles
                if self.colors:
                    color = self.colors.pop(0)
                else:
                    # Si toutes les couleurs prédéfinies sont utilisées, générer une couleur aléatoire
                    r = random.randint(100, 240)
                    g = random.randint(100, 240)
                    b = random.randint(100, 240)
                    color = f"#{r:02x}{g:02x}{b:02x}"
                self.travailleur_colors[travailleur.nom] = color
        
        # Headers of the columns (dynamiques par site)
        ttk.Label(planning_frame, text="Day", font=self.header_font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        dynamic_shifts = list(next(iter(self.planning.planning.values())).keys()) if self.planning and self.planning.planning else list(Horaire.SHIFTS.values())
        for i, shift in enumerate(dynamic_shifts):
            ttk.Label(planning_frame, text=shift, font=self.header_font).grid(row=0, column=i+1, padx=5, pady=5)
        
        # Remplir le planning
        # Charger les capacités (nombre de personnes requises par jour/shift) pour le site courant
        try:
            caps = Database().charger_capacites_site(self.site_actuel_id)
        except Exception:
            caps = {}
        dynamic_days = list(self.planning.planning.keys()) if self.planning and self.planning.planning else list(Horaire.JOURS)
        for i, jour in enumerate(dynamic_days):
            ttk.Label(planning_frame, text=self.traduire_jour(jour), font=self.normal_font).grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
            
            for j, shift in enumerate(dynamic_shifts):
                travailleur = self.planning.planning[jour][shift]
                
                # Créer un frame pour la cellule
                cell_frame = ttk.Frame(planning_frame, width=150, height=50)
                cell_frame.grid(row=i+1, column=j+1, padx=2, pady=2, sticky="nsew")
                cell_frame.grid_propagate(False)  # Empêcher le frame de s'adapter à son contenu
                
                # Déterminer capacité
                cap = max(1, int(caps.get(jour, {}).get(shift, 1)))
                # Liste des noms (support "nom1 / nom2 / nom3")
                noms = []
                if travailleur:
                    noms = [n.strip() for n in travailleur.split("/")]
                while len(noms) < cap:
                    noms.append(None)
                # Construire des sous-lignes
                inner = ttk.Frame(cell_frame)
                inner.pack(fill="both", expand=True)
                for r in range(cap):
                    inner.rowconfigure(r, weight=1)
                inner.columnconfigure(0, weight=1)
                for idx, nom in enumerate(noms[:cap]):
                    if nom:
                        color = self.travailleur_colors.get(nom, "#FFFFFF")
                        lbl = tk.Label(
                            inner,
                            text=nom,
                            bg=color,
                            font=self.normal_font,
                            relief="raised",
                            borderwidth=1,
                        )
                    else:
                        lbl = tk.Label(
                            inner,
                            text="Unassigned",
                            bg="#F0F0F0",
                            font=self.normal_font,
                            relief="sunken",
                            borderwidth=1,
                        )
                    lbl.grid(row=idx, column=0, sticky="nsew")
        
        # Configurer les colonnes pour qu'elles s'étendent
        for i in range(len(dynamic_shifts) + 1):  # 1 colonne pour les jours + colonnes dynamiques
            planning_frame.columnconfigure(i, weight=1)
        
        # Configurer les lignes pour qu'elles s'étendent
        for i in range(len(dynamic_days) + 1):  # 1 ligne pour les en-têtes + lignes dynamiques
            planning_frame.rowconfigure(i, weight=1)

    def ajouter_travailleur(self) -> bool:
        """Ajoute ou modifie un travailleur selon le mode courant.
        Retourne True en cas de succès, False si validation invalide/erreur utilisateur."""
        # Vérifier qu'un site est sélectionné
        if self.site_actuel_id is None:
            messagebox.showerror("Error", "Please select a site before adding a worker.")
            return False
        
        # Récupérer les valeurs du formulaire
        nom = self.nom_var.get().strip()
        nb_shifts_str = self.nb_shifts_var.get().strip()
        
        # Validation des entrées
        if not nom:
            messagebox.showerror("Error", "Please enter a name")
            return False
        
        try:
            nb_shifts = int(nb_shifts_str)
            if nb_shifts <= 0:
                raise ValueError("The number of shifts must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of shifts")
            return False
        
        # Récupérer les disponibilités (dynamiques selon le site)
        disponibilites = {}
        dynamic_days = list(self.disponibilites.keys()) if self.disponibilites else (self.reglages_site.get("jours") if hasattr(self, 'reglages_site') else list(Horaire.JOURS))
        for jour in dynamic_days:
            shifts_dispo = []
            for shift, var in self.disponibilites.get(jour, {}).items():
                if var.get():
                    shifts_dispo.append(shift)
            if shifts_dispo:
                disponibilites[jour] = shifts_dispo
        
        if not disponibilites:
            messagebox.showerror("Error", "Please select at least one availability")
            return False
        
        # Créer ou mettre à jour le travailleur
        if self.mode_edition and self.travailleur_en_edition:
            # Stocker l'ancien nom avant modification
            ancien_nom = self.travailleur_en_edition.nom
            
            # Mettre à jour le travailleur existant
            self.travailleur_en_edition.nom = nom
            self.travailleur_en_edition.nb_shifts_souhaites = nb_shifts
            self.travailleur_en_edition.disponibilites = disponibilites
            
            # Save in the database
            db = Database()
            db.sauvegarder_travailleur(self.travailleur_en_edition, ancien_nom)
            
            # Si le nom a changé, mettre à jour tous les plannings où ce travailleur est référencé
            if ancien_nom != nom:
                self.mettre_a_jour_references_travailleur(ancien_nom, nom)
            
            messagebox.showinfo("Success", f"Worker {nom} modified successfully")
        else:
            # Création d'un nouveau travailleur AVEC le site actuel
            travailleur = Travailleur(nom, disponibilites, nb_shifts, self.site_actuel_id)
            self.planning.ajouter_travailleur(travailleur)
            
            print(f"Nouveau travailleur '{nom}' ajouté au site {self.site_actuel_id}")
            
            # Sauvegarder dans la base de données
            db = Database()
            db.sauvegarder_travailleur(travailleur)
        
        # Important: recharger SEULEMENT les travailleurs du site actuel
        print(f"Rechargement des travailleurs pour le site {self.site_actuel_id}")
        self.charger_travailleurs_db()
        
        # Réinitialiser le formulaire après l'ajout ou la modification
        self.reinitialiser_formulaire()
        return True

    def reinitialiser_formulaire(self):
        """Réinitialise le formulaire de saisie"""
        self.nom_var.set("")
        self.nb_shifts_var.set("")
        
        # Réinitialiser toutes les disponibilités (dynamiques selon le site)
        for jour, shifts_map in self.disponibilites.items():
            for shift, var in shifts_map.items():
                var.set(False)
        # 12h removed
        
        # Réinitialiser le mode édition
        self.mode_edition = False
        self.travailleur_en_edition = None
        
        # Au lieu de:
        # self.btn_ajouter.config(text="Add worker")
        
        # Utilisez (si la popup/form existe encore):
        if hasattr(self, 'btn_ajouter') and self.btn_ajouter is not None:
            try:
                if self.btn_ajouter.winfo_exists():
                    self.mettre_a_jour_texte_bouton(self.btn_ajouter, "Add worker")
            except Exception:
                pass
        
        # Changer le titre du formulaire (si présent)
        try:
            if hasattr(self, 'form_label_frame') and self.form_label_frame is not None and self.form_label_frame.winfo_exists():
                self.form_label_frame.configure(text="Add worker")
        except Exception:
            pass
        
        # Désactiver le bouton Annuler uniquement si aucune popup n'est ouverte (contexte formulaire embarqué)
        popup_ouverte = hasattr(self, '_worker_popup') and self._worker_popup is not None and self._worker_popup.winfo_exists()
        if not popup_ouverte and hasattr(self, 'btn_annuler') and self.btn_annuler is not None:
            if hasattr(self.btn_annuler, 'configure'):
                try:
                    self.btn_annuler.configure(state=tk.DISABLED)
                except Exception:
                    pass
            else:
                # Si c'est un canvas
                try:
                    self.btn_annuler.enabled = False
                    self.btn_annuler.config(bg="#6c757d")
                    self.btn_annuler.unbind("<Button-1>")
                    self.btn_annuler.unbind("<Enter>")
                    self.btn_annuler.unbind("<Leave>")
                except Exception:
                    pass

    def mettre_a_jour_liste_travailleurs(self):
        """Met à jour la liste des travailleurs affichée dans l'interface"""
        print("DEBUG: Début mise à jour liste travailleurs")
        
        # Effacer tous les éléments existants
        for item in self.table_travailleurs.get_children():
            self.table_travailleurs.delete(item)
        print(f"DEBUG: Anciens éléments supprimés")
        
        # Trier les travailleurs par nom pour une meilleure lisibilité
        travailleurs_tries = sorted(self.planning.travailleurs, key=lambda t: t.nom)
        print(f"DEBUG: {len(travailleurs_tries)} travailleurs à afficher")
        
        # Remplir avec les travailleurs actuels
        for idx, travailleur in enumerate(travailleurs_tries):
            print(f"DEBUG: Ajout de {travailleur.nom} à la liste")
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.table_travailleurs.insert("", tk.END, values=(travailleur.nom, travailleur.nb_shifts_souhaites), tags=(tag,))
        
        # Forcer le rafraîchissement de l'affichage
        print("DEBUG: Rafraîchissement de l'affichage...")
        self.table_travailleurs.update_idletasks()
        self.table_travailleurs.update()
        
        # Mettre à jour le compteur
        try:
            self.nb_workers_var.set(f"Workers: {len(travailleurs_tries)}")
        except Exception:
            pass

        print("DEBUG: Fin mise à jour liste travailleurs")

    def selectionner_travailleur(self, event):
        """Select a worker in the list to edit"""
        selection = self.table_travailleurs.selection()
        if not selection:
            return
        
        # Récupérer le nom du travailleur sélectionné
        item = selection[0]
        nom_travailleur = self.table_travailleurs.item(item, "values")[0]
        
        # Trouver le travailleur correspondant
        for travailleur in self.planning.travailleurs:
            if travailleur.nom == nom_travailleur:
                # Remplir le formulaire avec les données du travailleur
                self.nom_var.set(travailleur.nom)
                self.nb_shifts_var.set(str(travailleur.nb_shifts_souhaites))
                
                # Réinitialiser toutes les disponibilités (dynamiques)
                for jour, shifts_map in self.disponibilites.items():
                    for shift, var in shifts_map.items():
                        var.set(False)
                for jour, types_map in self.disponibilites_12h.items():
                    for key, var in types_map.items():
                        var.set(False)
                
                # Définir les disponibilités du travailleur
                for jour, shifts in travailleur.disponibilites.items():
                    for shift in shifts:
                        if jour in self.disponibilites and shift in self.disponibilites[jour]:
                            self.disponibilites[jour][shift].set(True)
                
                # Définir les disponibilités 12h si elles existent
                if hasattr(travailleur, 'disponibilites_12h'):
                    for jour, shifts_12h in travailleur.disponibilites_12h.items():
                        for shift_12h in shifts_12h:
                            if jour in self.disponibilites_12h and shift_12h in self.disponibilites_12h[jour]:
                                self.disponibilites_12h[jour][shift_12h].set(True)
                
                # Passer en mode édition
                self.mode_edition = True
                self.travailleur_en_edition = travailleur
                
                # Si la popup n'est pas ouverte, ouvrir directement la popup de modification
                try:
                    self.ouvrir_popup_travailleur(modifier=True)
                except Exception:
                    pass
                
                break

    def annuler_edition(self):
        """Annule l'édition en cours et réinitialise le formulaire"""
        self.reinitialiser_formulaire()
        # Désélectionner dans la table
        for item in self.table_travailleurs.selection():
            self.table_travailleurs.selection_remove(item)

    def verifier_repos_entre_gardes(self, planning, travailleur):
        """Vérifie qu'il y a assez de repos entre les gardes d'un travailleur (jours/shifts dynamiques)."""
        gardes = []
        dynamic_days = list(planning.keys())
        for idx_jour, jour in enumerate(dynamic_days):
            for shift_str, assigne in planning[jour].items():
                if assigne != travailleur.nom:
                    continue
                try:
                    d_s, f_s = shift_str.split('-')
                    d = int(d_s)
                    f = int(f_s)
                except Exception:
                    continue
                gardes.append((idx_jour, d, f))
        gardes.sort(key=lambda x: (x[0], x[1]))
        for i in range(len(gardes) - 1):
            j1, d1, f1 = gardes[i]
            j2, d2, f2 = gardes[i + 1]
            duree1 = (f1 - d1) % 24 or 1
            fin1 = (d1 + duree1) % 24
            if j1 == j2:
                intervalle = d2 - fin1
                if intervalle < 0:
                    intervalle += 24
                else:
                    intervalle = (j2 - j1) * 24 + (d2 - fin1)
                if intervalle < 0:
                    intervalle += 24
            if intervalle < self.repos_minimum_entre_gardes:
                return False
        return True

    def generer_planning(self):
        """Calcule un nouveau planning optimisé et met à jour les données du modèle.
        Ne fait aucun appel UI; retourne le nombre de trous (int)."""
        if not self.planning.travailleurs:
            # Ne pas appeler messagebox ici (thread worker). Signaler via valeur spéciale
            return None
        
        # Générer un planning initial
        self.planning.generer_planning(mode_12h=False)
        
        # Essayer plusieurs générations et garder la meilleure
        meilleur_planning = self.evaluer_planning(self.planning.planning)
        meilleure_evaluation = self.compter_trous(self.planning.planning)
        meilleure_repartition_nuit = self.evaluer_repartition_nuit(self.planning.planning)
        meilleure_proximite = self.evaluer_proximite_gardes(self.planning.planning)
        
        # Essayer 15 générations supplémentaires pour trouver un meilleur planning
        for _ in range(15):
            planning_test = Planning()
            planning_test.travailleurs = self.planning.travailleurs.copy()
            planning_test.generer_planning(mode_12h=False)
            
            evaluation = self.compter_trous(planning_test.planning)
            repartition_nuit = self.evaluer_repartition_nuit(planning_test.planning)
            proximite = self.evaluer_proximite_gardes(planning_test.planning)
            
            # Priorité 1: moins de trous
            # Priorité 2: meilleure répartition des nuits
            # Priorité 3: moins de gardes rapprochées
            if (evaluation < meilleure_evaluation or 
                (evaluation == meilleure_evaluation and repartition_nuit < meilleure_repartition_nuit) or
                (evaluation == meilleure_evaluation and repartition_nuit == meilleure_repartition_nuit and proximite < meilleure_proximite)):
                meilleur_planning = {j: {s: planning_test.planning[j][s] for s in Horaire.SHIFTS.values()} for j in Horaire.JOURS}
                meilleure_evaluation = evaluation
                meilleure_repartition_nuit = repartition_nuit
                meilleure_proximite = proximite
        
        # Utiliser le meilleur planning trouvé (modèle)
        self.planning.planning = meilleur_planning
        
        # Retourner le nombre de trous pour l'affichage ultérieur sur le thread UI
        return meilleure_evaluation

    def next_alternative_planning(self):
        if hasattr(self.planning, 'next_alternative') and self.planning.next_alternative():
            # Raffraîchir l'affichage
            self.creer_planning_visuel()
            total, index_1, best_score = self.planning.get_alternative_info()
            if total > 1:
                self.alt_info_var.set(f"Alternatives: {index_1}/{total} (score={best_score:.0f})")
            else:
                self.alt_info_var.set("")
            # Mettre à jour l'état des boutons alt
            try:
                if total and total > 1:
                    self.btn_prev_alt.configure(state=tk.NORMAL)
                    self.btn_next_alt.configure(state=tk.NORMAL)
                else:
                    self.btn_prev_alt.configure(state=tk.DISABLED)
                    self.btn_next_alt.configure(state=tk.DISABLED)
            except Exception:
                pass
        else:
            messagebox.showinfo("Info", "No alternative available.")

    def prev_alternative_planning(self):
        if hasattr(self.planning, 'prev_alternative') and self.planning.prev_alternative():
            self.creer_planning_visuel()
            total, index_1, best_score = self.planning.get_alternative_info()
            if total > 1:
                self.alt_info_var.set(f"Alternatives: {index_1}/{total} (score={best_score:.0f})")
            else:
                self.alt_info_var.set("")
            # Mettre à jour l'état des boutons alt
            try:
                if total and total > 1:
                    self.btn_prev_alt.configure(state=tk.NORMAL)
                    self.btn_next_alt.configure(state=tk.NORMAL)
                else:
                    self.btn_prev_alt.configure(state=tk.DISABLED)
                    self.btn_next_alt.configure(state=tk.DISABLED)
            except Exception:
                pass
        else:
            messagebox.showinfo("Info", "No alternative available.")

    def compter_trous(self, planning):
        """Count the number of holes in a planning"""
        trous = 0
        for jour, shifts_map in planning.items():
            for shift, val in shifts_map.items():
                if val is None:
                    trous += 1
        return trous

    def evaluer_planning(self, planning):
        """Evaluate the quality of a planning based on several criteria"""
        # Copy the planning to avoid modifying it
        planning_copie = {j: {s: planning[j][s] for s in planning[j].keys()} for j in planning.keys()}
        
        # Vérifier la répartition des gardes de nuit
        gardes_nuit_par_travailleur = {}
        for jour in planning.keys():
            travailleur = planning[jour].get("22-06")
            if travailleur:
                if travailleur not in gardes_nuit_par_travailleur:
                    gardes_nuit_par_travailleur[travailleur] = 0
                gardes_nuit_par_travailleur[travailleur] += 1
        
        return planning_copie

    def evaluer_repartition_nuit(self, planning):
        """Evaluate the distribution of night shifts between workers"""
        # Count the night shifts per worker
        gardes_nuit_par_travailleur = {}
        for jour in planning.keys():
            travailleur = planning[jour].get("22-06")
            if travailleur:
                if travailleur not in gardes_nuit_par_travailleur:
                    gardes_nuit_par_travailleur[travailleur] = 0
                gardes_nuit_par_travailleur[travailleur] += 1
        
        # Si aucune garde de nuit n'est assignée, retourner une valeur élevée
        if not gardes_nuit_par_travailleur:
            return 100
        
        # Calculer l'écart-type des gardes de nuit (mesure de la dispersion)
        nb_gardes = list(gardes_nuit_par_travailleur.values())
        moyenne = sum(nb_gardes) / len(nb_gardes)
        variance = sum((x - moyenne) ** 2 for x in nb_gardes) / len(nb_gardes)
        ecart_type = variance ** 0.5
        
        return ecart_type  # Plus l'écart-type est petit, plus la répartition est équilibrée

    def evaluer_proximite_gardes(self, planning):
        """Evaluate the number of adjacent shifts (8h gap) for each worker"""
        # Mapping of shifts to start and end times
        shift_heures = {
            "06-14": (6, 14),
            "14-22": (14, 22),
            "22-06": (22, 6)  # La fin est à 6h le jour suivant
        }
        
        # Créer une liste chronologique des gardes par travailleur
        gardes_par_travailleur = {}
        
        for i, jour in enumerate(planning.keys()):
            for shift, (debut, fin) in shift_heures.items():
                if shift not in planning[jour]:
                    continue
                travailleur = planning[jour][shift]
                if travailleur:
                    if travailleur not in gardes_par_travailleur:
                        gardes_par_travailleur[travailleur] = []
                    
                    # Stocker (jour_index, heure_debut, heure_fin)
                    gardes_par_travailleur[travailleur].append((i, debut, fin))
        
        # Compter les gardes rapprochées (moins de 16h entre la fin d'une garde et le début de la suivante)
        total_gardes_rapprochees = 0
        
        for travailleur, gardes in gardes_par_travailleur.items():
            # Trier les gardes par jour puis par heure de début
            gardes.sort()
            
            for i in range(len(gardes) - 1):
                jour1, debut1, fin1 = gardes[i]
                jour2, debut2, fin2 = gardes[i + 1]
                
                # Calculer l'intervalle en heures
                if jour1 == jour2:
                    # Même jour
                    intervalle = debut2 - fin1
                else:
                    # Jours différents
                    jours_entre = jour2 - jour1
                    if fin1 > debut1:  # Garde normale
                        intervalle = (jours_entre * 24) - fin1 + debut2
                    else:  # Garde de nuit (22-06)
                        intervalle = ((jours_entre - 1) * 24) + (24 - fin1) + debut2
                
                # Si l'intervalle est inférieur à 16h (8h de repos + 8h de garde), c'est une garde rapprochée
                if intervalle < 16:
                    total_gardes_rapprochees += 1
        
        return total_gardes_rapprochees

    def generer_planning_12h(self):
        """Generate 12h shifts based on the workers' availabilities"""
        if not self.planning.travailleurs:
            messagebox.showerror("Error", "Please add at least one worker")
            return
        
        # Identifier les jours où des gardes de 12h peuvent être créées
        jours_avec_12h = set()
        for travailleur in self.planning.travailleurs:
            if hasattr(travailleur, 'disponibilites_12h'):
                for jour in travailleur.disponibilites_12h:
                    jours_avec_12h.add(jour)
        
        if not jours_avec_12h:
            messagebox.showinfo("Information", "No worker has availability for 12h shifts")
            return
        
        # Pour chaque jour, essayer de créer des gardes de 12h
        gardes_12h_creees = 0
        
        for jour in jours_avec_12h:
            # Chercher un travailleur pour la garde de matin 12h (06-18)
            travailleur_matin = None
            for travailleur in self.planning.travailleurs:
                if (hasattr(travailleur, 'disponibilites_12h') and 
                    jour in travailleur.disponibilites_12h and 
                    'matin_12h' in travailleur.disponibilites_12h[jour]):
                    travailleur_matin = travailleur
                    break
            
            # Chercher un travailleur pour la garde de nuit 12h (18-06)
            travailleur_nuit = None
            for travailleur in self.planning.travailleurs:
                if (hasattr(travailleur, 'disponibilites_12h') and 
                    jour in travailleur.disponibilites_12h and 
                    'nuit_12h' in travailleur.disponibilites_12h[jour]):
                    travailleur_nuit = travailleur
                    break
            
            # Si on a trouvé un travailleur pour le matin, lui assigner le shift 06-14
            if travailleur_matin:
                self.planning.planning[jour]["06-14"] = travailleur_matin.nom
            
            # Si on a trouvé un travailleur pour la nuit, lui assigner le shift 22-06
            if travailleur_nuit:
                self.planning.planning[jour]["22-06"] = travailleur_nuit.nom
            
            # Si on a les deux travailleurs, partager le shift 14-22
            if travailleur_matin and travailleur_nuit:
                self.planning.planning[jour]["14-22"] = f"{travailleur_matin.nom} / {travailleur_nuit.nom}"
                gardes_12h_creees += 2  # Deux gardes de 12h créées (matin et nuit)
            # Si on a seulement le travailleur du matin
            elif travailleur_matin:
                self.planning.planning[jour]["14-22"] = travailleur_matin.nom
                gardes_12h_creees += 1  # Une garde de 12h créée (matin)
            # Si on a seulement le travailleur de nuit
            elif travailleur_nuit:
                self.planning.planning[jour]["14-22"] = travailleur_nuit.nom
                gardes_12h_creees += 1  # Une garde de 12h créée (nuit)
        
        # Mettre à jour l'affichage
        self.creer_planning_visuel()
        
        if gardes_12h_creees > 0:
            messagebox.showinfo("Success", f"{gardes_12h_creees} 12h shift(s) created successfully")
        else:
            messagebox.showinfo("Information", "No 12h shift could be created. Check the workers' availabilities for 12h shifts.")

    def combler_trous(self):
        """Délègue au coeur Planning puis affiche un popup avec le ratio rempli/restant (en anglais)."""
        print("=== FILL_HOLES: UI → core Planning.combler_trous ===")
        def _count_unassigned_slots(planning_obj):
            try:
                jours = list(planning_obj.planning.keys())
                shifts = list(next(iter(planning_obj.planning.values())).keys()) if planning_obj.planning else []
                missing = 0
                for j in jours:
                    for s in shifts:
                        cap = 1
                        try:
                            cap = int(planning_obj.capacites.get(j, {}).get(s, 1))
                        except Exception:
                            cap = 1
                        val = planning_obj.planning[j].get(s)
                        names = []
                        if val:
                            names = [n.strip() for n in str(val).split(" / ") if n.strip()]
                        missing += max(0, cap - len(names))
                return missing
            except Exception:
                return 0

        before_missing = _count_unassigned_slots(self.planning)
        try:
            # Appel coeur: peut retourner (filled, total_estime) mais on reconte précisément après
            self.planning.combler_trous()
        except Exception as e:
            print(f"ERROR Fill holes (core): {e}")
        self.creer_planning_visuel()
        after_missing = _count_unassigned_slots(self.planning)
        filled_effective = max(0, before_missing - after_missing)
        # Mettre à jour l'état du bouton Fill Holes
        try:
            self.btn_fill_holes.configure(state=(tk.NORMAL if after_missing > 0 else tk.DISABLED))
        except Exception:
            pass
        try:
            from tkinter import messagebox
            messagebox.showinfo(
                "Fill holes",
                f"Filled {filled_effective} of {before_missing} holes (remaining: {after_missing})"
            )
        except Exception:
            pass

    def compter_gardes_rapprochees(self, planning, nom_travailleur):
        """Compte le nombre de gardes rapprochées pour un travailleur (jours/shifts dynamiques)."""
        gardes = []  # (idx_jour, debut, fin)
        dynamic_days = list(planning.keys())
        for i, jour in enumerate(dynamic_days):
            for shift, assigne in planning[jour].items():
                if assigne != nom_travailleur:
                    continue
                try:
                    d_s, f_s = shift.split('-')
                    d, f = int(d_s), int(f_s)
                except Exception:
                    continue
                gardes.append((i, d, f))
        gardes.sort(key=lambda x: (x[0], x[1]))
        gardes_rapprochees = 0
        for i in range(len(gardes) - 1):
            j1, d1, f1 = gardes[i]
            j2, d2, f2 = gardes[i + 1]
            duree1 = (f1 - d1) % 24 or 1
            fin1 = (d1 + duree1) % 24
            if j1 == j2:
                intervalle = d2 - fin1
                if intervalle < 0:
                    intervalle += 24
            else:
                intervalle = (j2 - j1) * 24 + (d2 - fin1)
                if intervalle < 0:
                    intervalle += 24
            if intervalle < 16:
                gardes_rapprochees += 1
        return gardes_rapprochees

    def charger_travailleurs_db(self):
        """Charge les travailleurs du site actuel depuis la base de données"""
        # Si aucun site n'est sélectionné, ne rien charger
        if self.site_actuel_id is None:
            print("DEBUG: Aucun site sélectionné - pas de chargement de travailleurs")
            self.planning.travailleurs = []
            self.mettre_a_jour_liste_travailleurs()
            return
        
        print(f"DEBUG: Début chargement travailleurs pour site {self.site_actuel_id}")
        
        db = Database()
        travailleurs = db.charger_travailleurs_par_site(self.site_actuel_id)
        
        # IMPORTANT: Vider la liste actuelle avant de recharger
        self.planning.travailleurs = []
        print(f"DEBUG: Liste des travailleurs vidée")
        
        # Ajouter les travailleurs du site actuel
        for travailleur in travailleurs:
            self.planning.ajouter_travailleur(travailleur)
        
        print(f"Chargement site {self.site_actuel_id}: {len(travailleurs)} travailleurs")
        for t in travailleurs:
            print(f"  - {t.nom} (site_id: {getattr(t, 'site_id', 'non défini')})")
        
        # Forcer la mise à jour de la liste
        print("DEBUG: Mise à jour de la liste des travailleurs...")
        self.mettre_a_jour_liste_travailleurs()
        
        # Forcer le rafraîchissement graphique
        print("DEBUG: Forcer rafraîchissement graphique...")
        self.table_travailleurs.update_idletasks()
        self.table_travailleurs.update()
        
        print(f"DEBUG: Fin chargement travailleurs - {len(self.planning.travailleurs)} travailleurs chargés")

    def sauvegarder_planning(self):
        """Save the current planning in the database"""
        # Get the date of the next Sunday
        import datetime
        
        # Obtenir la date actuelle
        aujourd_hui = datetime.date.today()
        
        # Calculer le nombre de jours jusqu'au prochain dimanche
        jours_jusqu_a_dimanche = (6 - aujourd_hui.weekday()) % 7
        
        # Si aujourd'hui est dimanche, on prend le dimanche suivant
        if jours_jusqu_a_dimanche == 0:
            jours_jusqu_a_dimanche = 7
        
        # Obtenir la date du prochain dimanche
        prochain_dimanche = aujourd_hui + datetime.timedelta(days=jours_jusqu_a_dimanche)
        
        # Formater la date pour le nom du planning avec le site
        site_nom = self.site_actuel_nom.get()
        nom_planning = f"Planning {site_nom} - week of {prochain_dimanche.strftime('%d/%m/%Y')}"
        
        # Demander confirmation à l'utilisateur
        confirmation = messagebox.askyesno(
            "Confirmation", 
            f"Do you want to save this planning for site '{site_nom}'\n"
            f"for the week of {prochain_dimanche.strftime('%d/%m/%Y')}?"
        )
        
        if confirmation:
            # Sauvegarder le planning avec le site actuel
            planning_id = self.planning.sauvegarder(nom_planning, self.site_actuel_id)
            messagebox.showinfo("Success", f"Planning saved for {site_nom} - week of {prochain_dimanche.strftime('%d/%m/%Y')}")
            return planning_id
        return None

    def charger_planning(self):
        """Charge a planning from the database"""
        # Récupérer la liste des plannings disponibles
        plannings = self.planning.lister_plannings()
        
        if not plannings:
            messagebox.showinfo("Information", "No planning saved")
            return
        
        # Créer une liste de choix avec les noms des plannings
        choix = []
        for p in plannings:
            date_str = p['date_creation'].split(' ')[0] if ' ' in p['date_creation'] else p['date_creation']
            choix.append(f"{p['id']} - {p['nom']} (created on {date_str})")
        
        # Demander à l'utilisateur de choisir un planning
        choix_planning = simpledialog.askstring(
            "Load a planning",
            "Choose a planning to load (enter the number):",
            initialvalue=choix[0].split(' - ')[0]
        )
        
        if not choix_planning:
            return
        
        try:
            planning_id = int(choix_planning.split(' - ')[0] if ' - ' in choix_planning else choix_planning)
            planning_charge = self.planning.charger(planning_id)
            
            if planning_charge:
                # Remplacer le planning actuel par celui chargé
                self.planning = planning_charge
                
                # Mettre à jour l'interface
                self.mettre_a_jour_liste_travailleurs()
                self.creer_planning_visuel()
                
                messagebox.showinfo("Success", "Planning loaded successfully")
                
                # Proposer de télécharger le planning
                self.proposer_telechargement_planning()
            else:
                messagebox.showerror("Error", "Impossible to load the planning")
        except ValueError:
            messagebox.showerror("Error", "Invalid planning number")

    def proposer_telechargement_planning(self):
        """Propose to the user to download the planning in CSV format"""
        confirmation = messagebox.askyesno(
            "Download", 
            "Do you want to download this planning in CSV format ?"
        )
        
        if confirmation:
            self.telecharger_planning_csv()

    def telecharger_planning_csv(self):
        """Export the current planning to CSV format"""
        import csv
        from tkinter import filedialog
        
        # Demander à l'utilisateur où sauvegarder le fichier
        fichier = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save the planning"
        )
        
        if not fichier:
            return
        
        try:
            with open(fichier, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Écrire l'en-tête
                en_tete = ["Day"] + list(Horaire.SHIFTS.values())
                writer.writerow(en_tete)
                
                # Écrire les données du planning
                for jour in Horaire.JOURS:
                    ligne = [jour]
                    for shift in Horaire.SHIFTS.values():
                        travailleur = self.planning.planning[jour][shift]
                        ligne.append(travailleur if travailleur else "Not assigned")
                    writer.writerow(ligne)
                
            messagebox.showinfo("Success", f"Planning exported successfully to {fichier}")
        except Exception as e:
            messagebox.showerror("Error", f"Error during exportation: {str(e)}")

    def supprimer_travailleur(self):
        # Si on est en mode popup modification, supprimer directement le travailleur en édition
        if getattr(self, 'mode_edition', False) and getattr(self, 'travailleur_en_edition', None):
            nom_travailleur = self.travailleur_en_edition.nom
        else:
            # Obtenir la sélection actuelle depuis la liste
            selection = self.table_travailleurs.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a worker to delete")
                return
            item = selection[0]
            nom_travailleur = self.table_travailleurs.item(item, "values")[0]
        
        # Demander confirmation
        if messagebox.askyesno("Confirmation", f"Are you sure you want to delete worker {nom_travailleur}?"):
            db = Database()
            db.supprimer_travailleur(nom_travailleur, site_id=self.site_actuel_id)
            
            # Recharger les travailleurs du site courant uniquement
            self.planning.travailleurs = db.charger_travailleurs_par_site(self.site_actuel_id)
            
            # Mettre à jour l'interface
            self.mettre_a_jour_liste_travailleurs()
            self.reinitialiser_formulaire()
            
            messagebox.showinfo("Success", f"Worker {nom_travailleur} deleted successfully")
            # Fermer la popup si ouverte
            self._close_worker_popup_if_open()

    def ouvrir_agenda_plannings(self):
        """Open a window to view and modify existing plannings (supports empty list)."""
        db = Database()
        # Créer une nouvelle fenêtre
        agenda_window = tk.Toplevel(self.root)
        agenda_window.title(f"Agenda des plannings - {self.site_actuel_nom.get()}")
        agenda_window.geometry("1000x600")
        agenda_window.configure(bg="#f0f0f0")
        # Forcer un thème ttk compatible avec les couleurs de lignes sur macOS
        try:
            style_agenda = ttk.Style(agenda_window)
            prev_theme = style_agenda.theme_use()
            agenda_window._prev_theme = prev_theme
            if prev_theme in ("aqua", "vista", "winnative", "xpnative"):
                style_agenda.theme_use("clam")
        except Exception:
            pass
        
        # Créer un cadre pour l'agenda
        agenda_frame = ttk.Frame(agenda_window, padding=10)
        agenda_frame.pack(fill="both", expand=True)
        
        # Barre d'options (sélection de site)
        options_frame = ttk.Frame(agenda_frame)
        options_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(options_frame, text="Site:").pack(side="left", padx=(0, 6))
        # Construire la liste des sites
        sites_list = [(s['id'], s['nom']) for s in self.sites_disponibles] if hasattr(self, 'sites_disponibles') else []
        site_id_by_name = {name: sid for sid, name in sites_list}
        site_names = ["All sites"] + [name for _, name in sites_list]
        site_filter_var = tk.StringVar(value=self.site_actuel_nom.get() if self.site_actuel_nom.get() else (site_names[1] if len(site_names) > 1 else "All sites"))
        site_combo = ttk.Combobox(options_frame, textvariable=site_filter_var, values=site_names, state="readonly", width=30)
        site_combo.pack(side="left")
        
        # Zone liste (séparée pour éviter de mélanger pack et grid sur le même parent)
        list_frame = ttk.Frame(agenda_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Créer un Treeview pour afficher les plannings
        columns = ("id", "nom", "date_creation")
        agenda_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configurer les en-têtes
        agenda_tree.heading("id", text="ID")
        agenda_tree.heading("nom", text="Planning name")
        agenda_tree.heading("date_creation", text="Creation date")
        
        # Configurer les colonnes
        agenda_tree.column("id", width=50, anchor="center")
        agenda_tree.column("nom", width=300)
        agenda_tree.column("date_creation", width=150)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=agenda_tree.yview)
        agenda_tree.configure(yscrollcommand=scrollbar.set)
        
        # Couleurs inspirées du week planning
        try:
            agenda_tree.tag_configure("morning_row", background="#e8f8f0")   # clair dérivé de #a8e6cf
            agenda_tree.tag_configure("afternoon_row", background="#fff5d6") # clair dérivé de #ffcc5c
            agenda_tree.tag_configure("night_row", background="#efe6fb")     # clair dérivé de #b19cd9
        except Exception:
            pass
        
        # Placer les widgets
        agenda_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configurer le redimensionnement
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Fonction pour recharger selon filtre de site
        def actualiser_liste():
            # Déterminer le site sélectionné
            nom_sel = site_filter_var.get()
            if nom_sel == "All sites":
                liste = db.lister_plannings_par_site(None)
                agenda_window.title("Agenda des plannings - Tous les sites")
                append_site = True
            else:
                site_id = site_id_by_name.get(nom_sel)
                liste = db.lister_plannings_par_site(site_id)
                agenda_window.title(f"Agenda des plannings - {nom_sel}")
                append_site = False
            # Vider
            for item in agenda_tree.get_children():
                agenda_tree.delete(item)
            # Remplir
            for idx, p in enumerate(liste):
                row_tag = ["morning_row", "afternoon_row", "night_row"][idx % 3]
                nom_aff = p['nom'] + (f" ({p['site_nom']})" if append_site else "")
                agenda_tree.insert("", "end", values=(p['id'], nom_aff, p['date_creation']), tags=(str(p['id']), row_tag))

        # Lier le changement de site
        site_combo.bind('<<ComboboxSelected>>', lambda e: actualiser_liste())
        # Initialiser la liste
        actualiser_liste()
        
        # Cadre pour les boutons d'action
        action_frame = ttk.Frame(agenda_window, padding=10)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        # Fonction pour obtenir le planning sélectionné
        def get_selected_planning():
            selection = agenda_tree.selection()
            if not selection:
                messagebox.showwarning("Attention", "Please select a planning")
                return None
            
            item = selection[0]
            planning_id = int(agenda_tree.item(item, "tags")[0])
            return planning_id, item
        
        # Fonction pour ouvrir le planning sélectionné
        def ouvrir_planning_selectionne():
            result = get_selected_planning()
            if result:
                planning_id, _ = result
                self.ouvrir_planning_pour_modification(planning_id, agenda_window)
        
        # Fonction pour renommer un planning
        def renommer_planning():
            result = get_selected_planning()
            if not result:
                return
            
            planning_id, item = result
            
            # Récupérer le nom actuel
            nom_actuel = agenda_tree.item(item, "values")[1]
            
            # Demander le nouveau nom
            nouveau_nom = simpledialog.askstring(
                "Rename the planning",
                "Enter the new name of the planning:",
                initialvalue=nom_actuel,
                parent=agenda_window
            )
            
            if nouveau_nom and nouveau_nom != nom_actuel:
                # Mettre à jour le nom dans la base de données
                db = Database()
                if db.modifier_nom_planning(planning_id, nouveau_nom):
                    # Rafraîchir la liste pour refléter le tri/affichage
                    actualiser_liste()
                    messagebox.showinfo("Success", "Planning renamed successfully")
                else:
                    messagebox.showerror("Error", "Impossible to rename the planning")
        
        # Fonction pour supprimer un planning
        def supprimer_planning():
            result = get_selected_planning()
            if not result:
                return
            
            planning_id, item = result
            
            # Demander confirmation
            confirmation = messagebox.askyesno(
                "Confirmation",
                "Are you sure you want to delete this planning?\nThis action is irreversible.",
                parent=agenda_window
            )
            
            if confirmation:
                # Supprimer le planning de la base de données
                db = Database()
                if db.supprimer_planning(planning_id):
                    # Rafraîchir la liste
                    actualiser_liste()
                    messagebox.showinfo("Success", "Planning deleted successfully")
                else:
                    messagebox.showerror("Error", "Impossible to delete the planning")
        
        # Ajouter les boutons d'action
        btn_ouvrir = ttk.Button(action_frame, text="📂 Open", command=ouvrir_planning_selectionne)
        btn_ouvrir.pack(side="left", padx=5)
        
        btn_renommer = ttk.Button(action_frame, text="✏️ Rename", command=renommer_planning)
        btn_renommer.pack(side="left", padx=5)
        
        btn_supprimer = ttk.Button(action_frame, text="🗑️ Delete", command=supprimer_planning)
        btn_supprimer.pack(side="left", padx=5)
        
        # Double-clic pour ouvrir un planning
        agenda_tree.bind("<Double-1>", lambda event: ouvrir_planning_selectionne())
        
        # Ajouter un bouton pour fermer l'agenda
        def _close_agenda():
            try:
                if hasattr(agenda_window, "_prev_theme"):
                    ttk.Style(agenda_window).theme_use(agenda_window._prev_theme)
            except Exception:
                pass
            agenda_window.destroy()

        agenda_window.protocol("WM_DELETE_WINDOW", _close_agenda)
        btn_fermer = ttk.Button(agenda_window, text="✖️ Close", command=_close_agenda)
        btn_fermer.pack(pady=10)

    def ouvrir_planning_pour_modification(self, planning_id, parent_window=None):
        """Open an existing planning for modification with the same visual style as the main page"""
        # Charger le planning depuis la base de données
        planning_charge = Planning.charger(planning_id)
        
        if not planning_charge:
            messagebox.showerror("Error", "Impossible to load the planning")
            return
        
        # Récupérer les informations du planning
        db = Database()
        try:
            planning_info = db.obtenir_info_planning(planning_id)
            
            if not planning_info:
                messagebox.showerror("Error", "Impossible to retrieve planning information")
                return
            
            # Créer une nouvelle fenêtre
            planning_window = tk.Toplevel(self.root)
            planning_window.title(f"Planning: {planning_info['nom']}")
            planning_window.geometry("1200x800")
            planning_window.configure(bg="#f0f0f0")
            
            # Stocker l'ID du planning pour la sauvegarde ultérieure
            planning_window.planning_id = planning_id
            planning_window.planning = planning_charge
            
            # Créer un cadre pour le planning
            planning_frame = ttk.Frame(planning_window, padding=10)
            planning_frame.pack(fill="both", expand=True)
            
            # Créer un Canvas pour le planning visuel (similaire à l'interface principale)
            canvas_frame = ttk.Frame(planning_frame)
            canvas_frame.pack(side="left", fill="both", expand=True, pady=10)
            
            # Déterminer jours/shifts dynamiques pour ce planning selon son site
            site_id_planning = planning_info.get('site_id') if isinstance(planning_info, dict) else None
            try:
                if site_id_planning:
                    db_local = Database()
                    shifts_dyn, jours_dyn = db_local.charger_reglages_site(site_id_planning)
                    capacities = db_local.charger_capacites_site(site_id_planning)
                else:
                    shifts_dyn, jours_dyn = list(Horaire.SHIFTS.values()), list(Horaire.JOURS)
                    capacities = {j: {s: 1 for s in shifts_dyn} for j in jours_dyn}
            except Exception:
                shifts_dyn, jours_dyn = list(Horaire.SHIFTS.values()), list(Horaire.JOURS)
                capacities = {j: {s: 1 for s in shifts_dyn} for j in jours_dyn}

            # Assigner des couleurs pour tous les travailleurs déjà présents dans ce planning
            def _assign_color_if_needed(worker_name: str):
                if not worker_name or worker_name == "Not assigned":
                    return
                if worker_name not in self.travailleur_colors:
                    if self.colors:
                        color = self.colors.pop(0)
                    else:
                        import random
                        r = random.randint(100, 240)
                        g = random.randint(100, 240)
                        b = random.randint(100, 240)
                        color = f"#{r:02x}{g:02x}{b:02x}"
                    self.travailleur_colors[worker_name] = color

            try:
                for j, smap in planning_charge.planning.items():
                    for s, val in smap.items():
                        if val:
                            for n in [x.strip() for x in str(val).split(" / ") if x.strip()]:
                                _assign_color_if_needed(n)
                        else:
                            _assign_color_if_needed(val)
            except Exception:
                pass
            
            # Canvas pour le planning
            canvas_width = 1000
            canvas_height = 550
            canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height, bg="white", highlightthickness=1, highlightbackground="#ddd")
            canvas.pack(fill="both", expand=True)
            
            # Palette de couleurs pour les colonnes (dynamique selon les shifts du site)
            # On assigne cycliquement Morning/Afternoon/Night-like aux shifts triés par heure de début
            def _parse_start(s):
                try:
                    return int(s.split('-')[0])
                except Exception:
                    return 0
            base_palette = ["#a8e6cf", "#ffecb3", "#e8e0ff"]  # morning, afternoon, night (pastel)
            shifts_sorted = sorted(shifts_dyn, key=_parse_start)
            shift_colors = {}
            for idx, s in enumerate(shifts_sorted):
                shift_colors[s] = base_palette[idx % len(base_palette)]
            
            # Dimensions des cellules selon les réglages du site du planning
            cell_width = canvas_width / (len(shifts_dyn) + 1)
            cell_height = canvas_height / (len(jours_dyn) + 1)
            
            # Dessiner les en-têtes de colonnes (shifts)
            canvas.create_rectangle(0, 0, cell_width, cell_height, fill="#f0f0f0", outline="#ccc")
            canvas.create_text(cell_width/2, cell_height/2, text="Day", font=("Arial", 10, "bold"))
            
            for i, shift in enumerate(shifts_dyn):
                x0 = cell_width * (i + 1)
                y0 = 0
                x1 = cell_width * (i + 2)
                y1 = cell_height
                fill_color = shift_colors.get(shift, "#e0e0e0")
                canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline="#000000")
                canvas.create_text((x0 + x1)/2, (y0 + y1)/2, text=shift, font=("Arial", 10, "bold"))
            
            # Couleurs par jour (ligne entière)
            day_palette = ["#eef7ff", "#f7ffee", "#fff6ee", "#f2f0ff", "#eefaf7", "#fff0f0", "#f0fff7"]
            day_colors = {jour: day_palette[i % len(day_palette)] for i, jour in enumerate(jours_dyn)}
            
            # Dessiner les en-têtes de lignes (jours)
            for i, jour in enumerate(jours_dyn):
                x0 = 0
                y0 = cell_height * (i + 1)
                x1 = cell_width
                y1 = cell_height * (i + 2)
                canvas.create_rectangle(x0, y0, x1, y1, fill=day_colors[jour], outline="#000000")
                canvas.create_text((x0 + x1)/2, (y0 + y1)/2, text=self.traduire_jour(jour), font=("Arial", 10, "bold"))
            
            # Dessiner les cellules avec les assignations
            cellules = {}  # Pour stocker les références aux cellules pour modification ultérieure
            
            # Index rapides pour recalcule des coordonnées
            day_index = {jour: i for i, jour in enumerate(jours_dyn)}
            shift_index = {shift: j for j, shift in enumerate(shifts_dyn)}

            # Fonction utilitaire pour redessiner une cellule selon l'état courant
            def _draw_cell(jour, shift):
                i = day_index[jour]
                j = shift_index[shift]
                x0 = cell_width * (j + 1)
                y0 = cell_height * (i + 1)
                x1 = cell_width * (j + 2)
                y1 = cell_height * (i + 2)
                # Effacer tous les items de cette cellule via un tag dédié
                tag = f"cell_{jour}_{shift}"
                try:
                    canvas.delete(tag)
                except Exception:
                    pass
                # Valeur actuelle
                val = planning_window.planning.planning.get(jour, {}).get(shift)
                # Capacité de la cellule
                cap = max(1, int(capacities.get(jour, {}).get(shift, 1)))
                names = []
                if val:
                    names = [n.strip() for n in str(val).split(" / ") if n.strip()]
                while len(names) < cap:
                    names.append(None)
                slice_h = (y1 - y0) / cap
                # Dessiner chaque sous-case
                for idx_slice, nom_slice in enumerate(names):
                    sy0 = y0 + idx_slice * slice_h
                    sy1 = sy0 + slice_h
                    if nom_slice:
                        c = self.travailleur_colors.get(nom_slice, "#e0f7fa")
                        rid = canvas.create_rectangle(x0, sy0, x1, sy1, fill=c, outline="#000000", tags=(tag,))
                        tid = canvas.create_text((x0 + x1)/2, (sy0 + sy1)/2, text=nom_slice, width=cell_width*0.9, font=("Arial", 9), tags=(tag,))
                    else:
                        rid = canvas.create_rectangle(x0, sy0, x1, sy1, fill="#ffe5e5", outline="#000000", tags=(tag,))
                        tid = canvas.create_text((x0 + x1)/2, (sy0 + sy1)/2, text="Not assigned", fill="#cc0000", width=cell_width*0.9, font=("Arial", 9, "bold"), tags=(tag,))
                # Mettre à jour l'état mémoire
                cellules.setdefault(jour, {})[shift] = {"tag": tag, "travailleur": val}
                # Bind clic sur toute la cellule
                canvas.tag_bind(tag, "<Button-1>", lambda e, j=jour, s=shift: modifier_cellule(j, s))

            # Panneau de statistiques: nombre de gardes par travailleur
            stats_frame = ttk.LabelFrame(planning_frame, text="Shifts per worker", padding=8)
            stats_frame.pack(side="right", fill="y", padx=8)

            def _compute_counts():
                counts = {}
                for jour in jours_dyn:
                    for shift in shifts_dyn:
                        val = planning_charge.planning.get(jour, {}).get(shift)
                        if not val:
                            continue
                        for n in [x.strip() for x in str(val).split(" / ") if x.strip()]:
                            counts[n] = counts.get(n, 0) + 1
                return counts

            def _render_stats():
                for child in stats_frame.winfo_children():
                    child.destroy()
                counts = _compute_counts()
                for name in sorted(counts.keys()):
                    row = ttk.Frame(stats_frame)
                    row.pack(fill="x", pady=2)
                    color = self.travailleur_colors.get(name, "#e0e0e0")
                    swatch = tk.Label(row, width=2, bg=color)
                    swatch.pack(side="left", padx=(0,6))
                    ttk.Label(row, text=name).pack(side="left")
                    ttk.Label(row, text=f"({counts[name]})").pack(side="right")

            _render_stats()
            
            for i, jour in enumerate(jours_dyn):
                cellules[jour] = {}
                for j, shift in enumerate(shifts_dyn):
                    x0 = cell_width * (j + 1)
                    y0 = cell_height * (i + 1)
                    x1 = cell_width * (j + 2)
                    y1 = cell_height * (i + 2)
                    
                    # Récupérer le travailleur assigné
                    travailleur = planning_charge.planning.get(jour, {}).get(shift)
                    
                    # Capacité requise pour cette case
                    cap = max(1, int(capacities.get(jour, {}).get(shift, 1)))
                    # Valeur peut contenir des noms séparés par ' / '
                    noms = []
                    if travailleur:
                        if " / " in travailleur:
                            noms = [n.strip() for n in travailleur.split(" / ")]
                        else:
                            noms = [travailleur]
                    # Compléter avec des vides si moins de cap
                    while len(noms) < cap:
                        noms.append(None)
                    # Hauteur de tranche
                    slice_h = (y1 - y0) / cap
                    rect_id = None
                    rect2_id = None
                    text_id = None
                    for idx_slice, nom_slice in enumerate(noms):
                        sy0 = y0 + idx_slice * slice_h
                        sy1 = sy0 + slice_h
                        if nom_slice:
                            c = self.travailleur_colors.get(nom_slice, "#e0f7fa")
                            rid = canvas.create_rectangle(x0, sy0, x1, sy1, fill=c, outline="#000000")
                            tid = canvas.create_text((x0 + x1)/2, (sy0 + sy1)/2, text=nom_slice, width=cell_width*0.9, font=("Arial", 9))
                        else:
                            rid = canvas.create_rectangle(x0, sy0, x1, sy1, fill="#ffe5e5", outline="#000000")
                            tid = canvas.create_text((x0 + x1)/2, (sy0 + sy1)/2, text="Not assigned", fill="#cc0000", width=cell_width*0.9, font=("Arial", 9, "bold"))
                        # Bind
                        canvas.tag_bind(rid, "<Button-1>", lambda e, j=jour, s=shift: modifier_cellule(j, s))
                        canvas.tag_bind(tid, "<Button-1>", lambda e, j=jour, s=shift: modifier_cellule(j, s))
                        # garder le premier
                        if idx_slice == 0:
                            rect_id = rid
                            text_id = tid
                    # pas de rect2 dans ce mode multi-capacité
                    rect2_id = None
                    
                    # Stocker les IDs pour pouvoir les modifier plus tard
                    cellules[jour][shift] = {"rect": rect_id, "rect2": rect2_id if 'rect2_id' in locals() else None, "text": text_id, "travailleur": travailleur}
                    
                    # Ajouter un gestionnaire de clic pour modifier l'assignation
                    canvas.tag_bind(rect_id, "<Button-1>", 
                                    lambda e, j=jour, s=shift: modifier_cellule(j, s))
                    if 'rect2_id' in locals() and rect2_id:
                        canvas.tag_bind(rect2_id, "<Button-1>", lambda e, j=jour, s=shift: modifier_cellule(j, s))
                    canvas.tag_bind(text_id, "<Button-1>", lambda e, j=jour, s=shift: modifier_cellule(j, s))
            
            # Fonction pour modifier une cellule
            def modifier_cellule(jour, shift):
                # Liste de tous les travailleurs + "Non assigné"
                # Filtrer les travailleurs par site du planning si possible
                site_id_planning_local = planning_info.get('site_id') if isinstance(planning_info, dict) else None
                travailleurs = [t.nom for t in planning_charge.travailleurs if getattr(t, 'site_id', None) in (site_id_planning_local, None)]
                travailleurs.append("Not assigned")
                
                # Obtenir une liste de tous les noms des travailleurs dans la base de données
                db = Database()
                if site_id_planning_local:
                    tous_travailleurs = [t.nom for t in db.charger_travailleurs_par_site(site_id_planning_local)]
                else:
                    tous_travailleurs = [t.nom for t in db.charger_travailleurs()]
                
                # Fusionner avec les travailleurs actuels et éliminer les doublons
                tous_noms = list(set(travailleurs + tous_travailleurs))
                tous_noms.sort()
                
                # Fenêtre de sélection pour choisir un travailleur
                selection_window = tk.Toplevel(planning_window)
                selection_window.title(f"Assign a worker for {self.traduire_jour(jour)} - {shift}")
                selection_window.geometry("300x400")
                selection_window.transient(planning_window)
                selection_window.grab_set()
                selection_window.focus_set()
                
                # Frame pour contenir la liste
                frame = ttk.Frame(selection_window, padding=10)
                frame.pack(fill="both", expand=True)
                
                # Label
                ttk.Label(frame, text=f"Choose a worker for\n{self.traduire_jour(jour)} - {shift}:", 
                         font=("Arial", 10, "bold")).pack(pady=10)
                
                # Listbox avec scrollbar
                list_frame = ttk.Frame(frame)
                list_frame.pack(fill="both", expand=True)
                
                scrollbar = ttk.Scrollbar(list_frame)
                scrollbar.pack(side="right", fill="y")
                
                listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 12))
                listbox.pack(side="left", fill="both", expand=True)
                
                scrollbar.config(command=listbox.yview)
                
                # Ajouter les options à la listbox
                for nom in tous_noms:
                    listbox.insert(tk.END, nom)
                
                # Ajouter "Non assigné" comme dernière option
                if "Not assigned" not in tous_noms:
                    listbox.insert(tk.END, "Not assigned")
                
                # Sélectionner le travailleur actuel
                actuel = cellules[jour][shift]["travailleur"]
                if actuel in tous_noms:
                    index = tous_noms.index(actuel)
                    listbox.selection_set(index)
                    listbox.see(index)
                elif actuel is None and "Not assigned" in tous_noms:
                    index = tous_noms.index("Not assigned")
                    listbox.selection_set(index)
                    listbox.see(index)
                
                # Fonction pour appliquer le choix
                def appliquer_choix():
                    selections = listbox.curselection()
                    if selections:
                        choix = listbox.get(selections[0])
                        if choix == "Not assigned":
                            if jour in planning_window.planning.planning and shift in planning_window.planning.planning[jour]:
                                planning_window.planning.planning[jour][shift] = None
                            cellules[jour][shift]["travailleur"] = None
                            # Redessiner pour prendre la couleur rouge Not assigned
                            _draw_cell(jour, shift)
                        else:
                            # garantir une couleur pour le travailleur
                            if choix not in self.travailleur_colors:
                                # assigne une nouvelle couleur simple
                                import random
                                r = random.randint(100, 240)
                                g = random.randint(100, 240)
                                b = random.randint(100, 240)
                                self.travailleur_colors[choix] = f"#{r:02x}{g:02x}{b:02x}"
                            if jour not in planning_window.planning.planning:
                                # si le jour n'est pas dans la structure (devrait être rare), ignorer en sécurité
                                selection_window.destroy()
                                return
                            if shift not in planning_window.planning.planning[jour]:
                                selection_window.destroy()
                                return
                            planning_window.planning.planning[jour][shift] = choix
                            cellules[jour][shift]["travailleur"] = choix
                            # Redessiner la cellule avec la couleur du travailleur
                            _draw_cell(jour, shift)
                        # Mettre à jour le panneau de stats
                        _render_stats()
                        selection_window.destroy()
                
                # Boutons
                btn_frame = ttk.Frame(frame)
                btn_frame.pack(fill="x", pady=10)
                
                ttk.Button(btn_frame, text="✅ Validate", command=appliquer_choix).pack(side="left", padx=5, expand=True)
                ttk.Button(btn_frame, text="✖️ Cancel", command=selection_window.destroy).pack(side="right", padx=5, expand=True)
                
                # Double-clic pour sélectionner
                listbox.bind("<Double-1>", lambda e: appliquer_choix())
            
            # Fonction pour sauvegarder le planning modifié
            def sauvegarder_planning_modifie():
                if db.mettre_a_jour_planning(planning_id, planning_window.planning):
                    messagebox.showinfo("Success", "Planning updated successfully")
                    # Fermer la fenêtre d'édition
                    planning_window.destroy()
                    # Rafraîchir l'agenda si nécessaire
                    if parent_window:
                        parent_window.destroy()
                        self.ouvrir_agenda_plannings()
                else:
                    messagebox.showerror("Error", "Impossible to update the planning")
            
            # Fonctions pour exporter le planning
            def exporter_planning():
                self.telecharger_planning_csv(planning_window.planning)
            
            # Frame pour les boutons en bas
            button_frame = ttk.Frame(planning_window, padding=10)
            button_frame.pack(fill="x", side="bottom")
            
            # Boutons
            ttk.Button(button_frame, text="💾 Save", command=sauvegarder_planning_modifie).pack(side="left", padx=5)
            ttk.Button(button_frame, text="📤 Export to CSV", command=exporter_planning).pack(side="left", padx=5)
            ttk.Button(button_frame, text="✖️ Close without saving", command=planning_window.destroy).pack(side="right", padx=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def telecharger_planning_csv(self, planning_to_export=None):
        """Export the current or specified planning to CSV format"""
        import csv
        from tkinter import filedialog
        
        # Utiliser le planning spécifié ou le planning actuel
        planning_a_exporter = planning_to_export if planning_to_export else self.planning
        
        # Demander à l'utilisateur où sauvegarder le fichier
        fichier = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save planning"
        )
        
        if not fichier:
            return
        
        try:
            with open(fichier, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Écrire l'en-tête
                # Export selon les shifts/jours du planning transmis s'il est fourni
                if planning_a_exporter and hasattr(planning_a_exporter, 'planning') and planning_a_exporter.planning:
                    export_days = list(planning_a_exporter.planning.keys())
                    export_shifts = list(next(iter(planning_a_exporter.planning.values())).keys()) if export_days else list(Horaire.SHIFTS.values())
                else:
                    export_days = list(Horaire.JOURS)
                    export_shifts = list(Horaire.SHIFTS.values())
                en_tete = ["Day"] + export_shifts
                writer.writerow(en_tete)
                
                # Écrire les données du planning
                for jour in export_days:
                    ligne = [self.traduire_jour(jour)]
                    for shift in export_shifts:
                        travailleur = planning_a_exporter.planning.get(jour, {}).get(shift)
                        ligne.append(travailleur if travailleur else "Not assigned")
                    writer.writerow(ligne)
                
            messagebox.showinfo("Success", f"Planning exported successfully to {fichier}")
        except Exception as e:
            messagebox.showerror("Error", f"Error during exportation: {str(e)}")

    def run(self):
        self.root.mainloop()

    def mettre_a_jour_references_travailleur(self, ancien_nom, nouveau_nom):
        """Met à jour toutes les références à un travailleur dont le nom a changé"""
        # Mise à jour dans le planning actuel
        for jour in self.planning.planning:
            for shift in self.planning.planning[jour]:
                if self.planning.planning[jour][shift] == ancien_nom:
                    self.planning.planning[jour][shift] = nouveau_nom
                elif self.planning.planning[jour][shift] and " / " in self.planning.planning[jour][shift]:
                    noms = self.planning.planning[jour][shift].split(" / ")
                    if ancien_nom in noms:
                        index = noms.index(ancien_nom)
                        noms[index] = nouveau_nom
                        self.planning.planning[jour][shift] = " / ".join(noms)
        
        # Mise à jour des couleurs
        if ancien_nom in self.travailleur_colors:
            color = self.travailleur_colors[ancien_nom]
            self.travailleur_colors[nouveau_nom] = color
            del self.travailleur_colors[ancien_nom]
        
        # Rafraîchir l'affichage
        self.afficher_planning()

    # --- Loader & exécution asynchrone pour la génération ---
    def _show_loader(self, message: str = "Generating planning..."):
        try:
            if hasattr(self, '_loader_win') and self._loader_win is not None and self._loader_win.winfo_exists():
                return
        except Exception:
            pass
        # Désactiver temporairement les actions sensibles pour éviter des états intermédiaires d'UI
        try:
            if hasattr(self, 'btn_generer_planning') and self.btn_generer_planning is not None:
                self.btn_generer_planning.configure(state=tk.DISABLED)
        except Exception:
            pass
        win = tk.Toplevel(self.root)
        win.title("Please wait")
        win.configure(bg="#f0f0f0")
        win.transient(self.root)
        win.grab_set()
        self._loader_win = win
        frame = ttk.Frame(win, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=message, font=self.normal_font).pack(pady=(0, 10))
        # Progressbar indéterminée
        pb = ttk.Progressbar(frame, mode="indeterminate")
        pb.pack(fill="x")
        pb.start(10)
        self._loader_pb = pb
        # Centrer la fenêtre du loader
        try:
            win.update_idletasks()
            width, height = 320, 120
            # Taille/position de la fenêtre parent si disponible
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            if rw and rh and rw > 1 and rh > 1:
                x = rx + max(0, (rw - width) // 2)
                y = ry + max(0, (rh - height) // 2)
            else:
                sw = win.winfo_screenwidth()
                sh = win.winfo_screenheight()
                x = max(0, (sw - width) // 2)
                y = max(0, (sh - height) // 2)
            win.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            try:
                win.geometry("320x120")
            except Exception:
                pass

    def _hide_loader(self):
        try:
            if hasattr(self, '_loader_pb') and self._loader_pb is not None:
                try:
                    self._loader_pb.stop()
                except Exception:
                    pass
                self._loader_pb = None
            if hasattr(self, '_loader_win') and self._loader_win is not None and self._loader_win.winfo_exists():
                self._loader_win.destroy()
            self._loader_win = None
            # Réactiver le bouton générer et forcer un rafraîchissement final propre
            try:
                if hasattr(self, 'btn_generer_planning') and self.btn_generer_planning is not None:
                    self.btn_generer_planning.configure(state=tk.NORMAL)
            except Exception:
                pass
            # Recréer le planning visuel une fois que tout est prêt (dans le thread Tk)
            try:
                self.creer_planning_visuel()
            except Exception:
                pass
        except Exception:
            self._loader_win = None

    def generer_planning_async(self):
        # Afficher loader et lancer la génération en thread
        self._show_loader("Generating planning... This may take a moment")
        def _task():
            try:
                holes = self.generer_planning()
            finally:
                # Revenir au thread Tk via after
                try:
                    def _finish_ui():
                        # Fermer le loader puis construire l'UI du planning et afficher la confirmation
                        self._hide_loader()
                        # Construire/rafraîchir visuel + info alternatives
                        try:
                            self.creer_planning_visuel()
                            total, index_1, best_score = self.planning.get_alternative_info() if hasattr(self.planning, 'get_alternative_info') else (0, 0, None)
                            if total > 1:
                                self.alt_info_var.set(f"Alternatives: {index_1}/{total} (score={best_score:.0f})")
                            else:
                                self.alt_info_var.set("")
                            # Activer/désactiver Fill Holes selon trous
                            try:
                                missing = 0
                                jours = list(self.planning.planning.keys())
                                shifts = list(next(iter(self.planning.planning.values())).keys()) if self.planning.planning else []
                                for j in jours:
                                    for s in shifts:
                                        cap = 1
                                        try:
                                            cap = int(self.planning.capacites.get(j, {}).get(s, 1))
                                        except Exception:
                                            cap = 1
                                        val = self.planning.planning[j].get(s)
                                        names = []
                                        if val:
                                            names = [n.strip() for n in str(val).split(" / ") if n.strip()]
                                        missing += max(0, cap - len(names))
                                self.btn_fill_holes.configure(state=(tk.NORMAL if missing > 0 else tk.DISABLED))
                            except Exception:
                                pass
                            # Activer/désactiver alternatives
                            try:
                                if total and total > 1:
                                    self.btn_prev_alt.configure(state=tk.NORMAL)
                                    self.btn_next_alt.configure(state=tk.NORMAL)
                                else:
                                    self.btn_prev_alt.configure(state=tk.DISABLED)
                                    self.btn_next_alt.configure(state=tk.DISABLED)
                            except Exception:
                                pass
                            # Marquer qu'un planning existe
                            self._has_generated_planning = True
                        except Exception:
                            pass
                        # Enfin, afficher la popup de confirmation si le calcul était valide
                        if holes is None:
                            messagebox.showerror("Error", f"Please add at least one worker to site '{self.site_actuel_nom.get()}'")
                        else:
                            messagebox.showinfo("Success", f"Planning generated successfully for site '{self.site_actuel_nom.get()}' ({holes} holes remaining)")
                    # Petit délai pour s'assurer que le loader est fermé avant le popup
                    self.root.after(50, _finish_ui)
                except Exception:
                    pass
        th = threading.Thread(target=_task, daemon=True)
        th.start()

    def recharger_travailleurs(self):
        """Recharge tous les travailleurs depuis la base de données et met à jour l'interface"""
        db = Database()
        self.planning.travailleurs = db.charger_travailleurs()
        self.mettre_a_jour_liste_travailleurs()

    def mettre_a_jour_texte_bouton(self, bouton, nouveau_texte):
        """Met à jour le texte d'un bouton de manière appropriée selon le type de bouton utilisé"""
        # Si votre bouton est une instance personnalisée avec une méthode spécifique
        if hasattr(bouton, 'set_text'):
            bouton.set_text(nouveau_texte)
        # Si votre bouton utilise une étiquette (label) interne
        elif hasattr(bouton, 'label'):
            bouton.label.config(text=nouveau_texte)
        # Si votre bouton est un canvas avec du texte
        elif isinstance(bouton, tk.Canvas):
            try:
                if bouton.winfo_exists():
                    # Trouver l'ID du texte dans le canvas
                    text_items = [item for item in bouton.find_all() if bouton.type(item) == "text"]
                    if text_items:
                        bouton.itemconfig(text_items[0], text=nouveau_texte)
            except Exception:
                pass

    def changer_site(self, event):
        """Change le site actuel et recharge les travailleurs"""
        nom_site = self.site_actuel_nom.get()
        
        # Vérifier si c'est un message d'erreur (site supprimé)
        if "⚠️" in nom_site or "supprimé" in nom_site:
            print(f"DEBUG: Tentative de sélection d'un site supprimé: {nom_site}")
            return
        
        # Trouver l'ID du site sélectionné
        site_trouve = False
        for site in self.sites_disponibles:
            if site['nom'] == nom_site:
                self.site_actuel_id = site['id']
                site_trouve = True
                break
        
        if not site_trouve:
            print(f"DEBUG: Site '{nom_site}' non trouvé dans les sites disponibles")
            messagebox.showerror("Error", f"The site '{nom_site}' no longer exists.")
            return
        
        print(f"Changement vers le site: {nom_site} (ID: {self.site_actuel_id})")
        
        # Recharger les réglages du site (jours/shifts) puis les travailleurs
        self._charger_reglages_site_actuel()
        # Recréer la structure du planning selon les réglages
        jours, shifts = self.reglages_site['jours'], self.reglages_site['shifts']
        self.planning = Planning(site_id=self.site_actuel_id, jours=jours, shifts=shifts)
        self.charger_travailleurs_db()
        # Rebuild availabilities section to match site settings (si la popup est ouverte)
        self._rebuild_disponibilites_from_settings()
        try:
            if hasattr(self, 'form_label_frame') and self.form_label_frame is not None and self.form_label_frame.winfo_exists():
                self._build_availabilities_section()
        except Exception:
            pass
        # Réinitialiser les infos d'alternatives/score lors d'un changement de site
        if hasattr(self, 'alt_info_var'):
            self.alt_info_var.set("")
        
        # Mettre à jour le titre avec le nombre de travailleurs
        nb_travailleurs = len(self.planning.travailleurs)
        self.titre_label.configure(text=f"Planning workers - {nom_site} ({nb_travailleurs} travailleurs)")
        
        # Réinitialiser le formulaire
        self.reinitialiser_formulaire()
        
        # Réafficher le planning selon la nouvelle structure
        self.creer_planning_visuel()
        
        print(f"Site changé vers {nom_site}. Nombre de travailleurs: {nb_travailleurs}")

    def ouvrir_gestion_sites(self):
        """Ouvre la fenêtre de gestion du site sélectionné (modifier réglages)"""
        # Créer une nouvelle fenêtre
        sites_window = tk.Toplevel(self.root)
        sites_window.title("Manage Site")
        sites_window.geometry("1000x650")
        sites_window.configure(bg="#f0f0f0")
        sites_window.transient(self.root)
        sites_window.grab_set()
        try:
            sites_window.update_idletasks()
            sites_window.minsize(900, 550)
        except Exception:
            pass
        
        # Frame principal
        main_frame = ttk.Frame(sites_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Cette fenêtre ne gère plus l'ajout; utiliser "Add Site" séparément
        
        # Section réglages du site sélectionné
        settings_frame = ttk.LabelFrame(main_frame, text="Selected site settings", padding=10)
        settings_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(settings_frame, text="Shifts:").grid(row=0, column=0, sticky="w", pady=(5, 0))
        # Contrôles pour Morning / Afternoon / Night
        controls_frame = ttk.Frame(settings_frame)
        controls_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(5, 0))
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(2, weight=1)

        morning_var = tk.BooleanVar(value=True)
        afternoon_var = tk.BooleanVar(value=True)
        night_var = tk.BooleanVar(value=True)

        # Spinboxes utilitaires (0-23)
        def make_hour_spinbox(parent, var):
            return tk.Spinbox(parent, from_=0, to=23, wrap=True, width=3, textvariable=var, state="normal", format="%02.0f")

        # Morning controls
        morning_frame = ttk.LabelFrame(controls_frame, text="Morning")
        morning_frame.grid(row=0, column=0, padx=5, sticky="ew")
        morning_check = ttk.Checkbutton(morning_frame, text="Enable", variable=morning_var)
        morning_check.grid(row=0, column=0, pady=2, sticky="w")
        ttk.Label(morning_frame, text="Start:").grid(row=1, column=0, sticky="w")
        morning_start_var = tk.StringVar(value="06")
        morning_start_sb = make_hour_spinbox(morning_frame, morning_start_var)
        morning_start_sb.grid(row=1, column=1, padx=2)
        ttk.Label(morning_frame, text="End:").grid(row=1, column=2, sticky="w")
        morning_end_var = tk.StringVar(value="14")
        morning_end_sb = make_hour_spinbox(morning_frame, morning_end_var)
        morning_end_sb.grid(row=1, column=3, padx=2)

        # Afternoon controls
        afternoon_frame = ttk.LabelFrame(controls_frame, text="Afternoon")
        afternoon_frame.grid(row=0, column=1, padx=5, sticky="ew")
        afternoon_check = ttk.Checkbutton(afternoon_frame, text="Enable", variable=afternoon_var)
        afternoon_check.grid(row=0, column=0, pady=2, sticky="w")
        ttk.Label(afternoon_frame, text="Start:").grid(row=1, column=0, sticky="w")
        afternoon_start_var = tk.StringVar(value="14")
        afternoon_start_sb = make_hour_spinbox(afternoon_frame, afternoon_start_var)
        afternoon_start_sb.grid(row=1, column=1, padx=2)
        ttk.Label(afternoon_frame, text="End:").grid(row=1, column=2, sticky="w")
        afternoon_end_var = tk.StringVar(value="22")
        afternoon_end_sb = make_hour_spinbox(afternoon_frame, afternoon_end_var)
        afternoon_end_sb.grid(row=1, column=3, padx=2)

        # Night controls
        night_frame = ttk.LabelFrame(controls_frame, text="Night")
        night_frame.grid(row=0, column=2, padx=5, sticky="ew")
        night_check = ttk.Checkbutton(night_frame, text="Enable", variable=night_var)
        night_check.grid(row=0, column=0, pady=2, sticky="w")
        ttk.Label(night_frame, text="Start:").grid(row=1, column=0, sticky="w")
        night_start_var = tk.StringVar(value="22")
        night_start_sb = make_hour_spinbox(night_frame, night_start_var)
        night_start_sb.grid(row=1, column=1, padx=2)
        ttk.Label(night_frame, text="End:").grid(row=1, column=2, sticky="w")
        night_end_var = tk.StringVar(value="06")
        night_end_sb = make_hour_spinbox(night_frame, night_end_var)
        night_end_sb.grid(row=1, column=3, padx=2)

        def update_spin_states():
            state_m = "normal" if morning_var.get() else "disabled"
            state_a = "normal" if afternoon_var.get() else "disabled"
            state_n = "normal" if night_var.get() else "disabled"
            for w in (morning_start_sb, morning_end_sb): w.config(state=state_m)
            for w in (afternoon_start_sb, afternoon_end_sb): w.config(state=state_a)
            for w in (night_start_sb, night_end_sb): w.config(state=state_n)

        morning_check.configure(command=update_spin_states)
        afternoon_check.configure(command=update_spin_states)
        night_check.configure(command=update_spin_states)
        update_spin_states()

        ttk.Label(settings_frame, text="Active days:").grid(row=1, column=0, sticky="w", pady=5)
        days_frame = ttk.Frame(settings_frame)
        days_frame.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        # Map English labels to French keys used en base
        day_order = [
            ("Sunday", "dimanche"),
            ("Monday", "lundi"),
            ("Tuesday", "mardi"),
            ("Wednesday", "mercredi"),
            ("Thursday", "jeudi"),
            ("Friday", "vendredi"),
            ("Saturday", "samedi"),
        ]
        day_vars = {}
        for i, (label_en, key_fr) in enumerate(day_order):
            var = tk.BooleanVar(value=True)
            day_vars[key_fr] = var
            chk = ttk.Checkbutton(days_frame, text=label_en, variable=var)
            chk.grid(row=i // 4, column=i % 4, padx=4, pady=2, sticky="w")

        settings_frame.columnconfigure(1, weight=1)

        def charger_reglages_site_courant():
            if not self.site_actuel_id:
                messagebox.showerror("Error", "No site selected")
                return
            dbs = Database()
            shifts, jours = dbs.charger_reglages_site(self.site_actuel_id)
            # Peupler les contrôles à partir des shifts: assigner par ordre de début
            def parse_shift(shift_str):
                try:
                    a, b = shift_str.split('-')
                    return int(a), int(b)
                except Exception:
                    return None
            parsed = [(s, parse_shift(s)) for s in shifts]
            parsed = [(s, p) for s, p in parsed if p is not None]
            parsed.sort(key=lambda x: x[1][0])
            # Reset defaults
            morning_var.set(False); afternoon_var.set(False); night_var.set(False)
            morning_start_var.set("06"); morning_end_var.set("14")
            afternoon_start_var.set("14"); afternoon_end_var.set("22")
            night_start_var.set("22"); night_end_var.set("06")
            # Assigner dans l'ordre: morning, afternoon, night
            targets = [
                (morning_var, morning_start_var, morning_end_var),
                (afternoon_var, afternoon_start_var, afternoon_end_var),
                (night_var, night_start_var, night_end_var),
            ]
            for idx, (_, (start, end)) in enumerate(parsed[:3]):
                var, vstart, vend = targets[idx]
                var.set(True)
                vstart.set(f"{start:02d}")
                vend.set(f"{end:02d}")
            update_spin_states()
            # Mettre à jour les cases à cocher des jours actifs
            for _, key_fr in day_order:
                day_vars[key_fr].set(key_fr in jours)
            # Rebuild capacities grid to reflect times
            if 'rebuild_capacities_grid' in locals():
                try:
                    rebuild_capacities_grid()
                except Exception:
                    pass

        # Capacités par jour/shift
        ttk.Label(settings_frame, text="Required staff (per day/shift):").grid(row=2, column=0, sticky="nw", pady=(10,0))
        capacities_frame = ttk.Frame(settings_frame)
        capacities_frame.grid(row=2, column=1, sticky="ew", padx=(10,0), pady=(10,0))
        capacities_vars = {}
        # Bâtir une grille dynamique des jours vs shifts avec Spinbox de 1..10
        def rebuild_capacities_grid():
            for child in capacities_frame.winfo_children():
                child.destroy()
            shifts, jours = [], []
            try:
                dbtmp = Database()
                shifts, jours = dbtmp.charger_reglages_site(self.site_actuel_id)
                saved_caps = dbtmp.charger_capacites_site(self.site_actuel_id)
            except Exception:
                shifts, jours = (list(Horaire.SHIFTS.values()), list(Horaire.JOURS))
                saved_caps = {j: {s: 1 for s in shifts} for j in jours}
            # entêtes
            ttk.Label(capacities_frame, text="Day").grid(row=0, column=0, padx=4, pady=2)
            for ci, s in enumerate(shifts, 1):
                ttk.Label(capacities_frame, text=s).grid(row=0, column=ci, padx=4, pady=2)
            # lignes
            for ri, j in enumerate(jours, 1):
                ttk.Label(capacities_frame, text=self.traduire_jour(j)).grid(row=ri, column=0, padx=4, pady=2, sticky="w")
                for ci, s in enumerate(shifts, 1):
                    var = tk.StringVar(value=str(saved_caps.get(j, {}).get(s, 1)))
                    capacities_vars.setdefault(j, {})[s] = var
                    sb = tk.Spinbox(capacities_frame, from_=1, to=10, width=3, textvariable=var)
                    sb.grid(row=ri, column=ci, padx=2, pady=2)
        rebuild_capacities_grid()

        def sauvegarder_reglages_site_courant():
            if not self.site_actuel_id:
                messagebox.showwarning("Warning", "No site selected")
                return
            # Validation des séquences horaires: chaque début ne doit pas précéder la fin précédente
            def _to_int(v):
                try:
                    return int(v.get())
                except Exception:
                    return None
            seq = []
            if morning_var.get():
                ms, me = _to_int(morning_start_var), _to_int(morning_end_var)
                if ms is None or me is None:
                    messagebox.showerror("Error", "Invalid Morning hours")
                    return
                # Morning doit finir après son début (même jour)
                if ms >= me:
                    messagebox.showerror("Error", "Morning end must be after Morning start")
                    return
                seq.append(("Morning", ms, me, "morning"))
            if afternoon_var.get():
                as_, ae = _to_int(afternoon_start_var), _to_int(afternoon_end_var)
                if as_ is None or ae is None:
                    messagebox.showerror("Error", "Invalid Afternoon hours")
                    return
                # Autoriser le passage de minuit mais limiter la durée à 12h max et > 0
                duree_afternoon = (ae - as_) % 24
                if duree_afternoon == 0 or duree_afternoon > 12:
                    messagebox.showerror("Error", "Afternoon end must be after Afternoon start")
                    return
                seq.append(("Afternoon", as_, ae, "afternoon"))
            if night_var.get():
                ns, ne = _to_int(night_start_var), _to_int(night_end_var)
                if ns is None or ne is None:
                    messagebox.showerror("Error", "Invalid Night hours")
                    return
                # Night peut chevaucher minuit; pas de contrainte start<end ici
                seq.append(("Night", ns, ne, "night"))
            # Contraintes d'ordre entre shifts consécutifs activés
            for i in range(len(seq) - 1):
                prev, nxt = seq[i], seq[i + 1]
                if nxt[1] < prev[2]:
                    messagebox.showerror(
                        "Error",
                        f"{nxt[0]} start ({nxt[1]:02d}) must be greater than or equal to {prev[0]} end ({prev[2]:02d})"
                    )
                    return
            # Contrainte de chevauchement fin de nuit -> début du matin (wrap autour minuit)
            if night_var.get() and morning_var.get():
                try:
                    ms = int(morning_start_var.get())
                    ne = int(night_end_var.get())
                except Exception:
                    messagebox.showerror("Error", "Invalid Morning/Night hours")
                    return
                # Morning doit commencer à/s après la fin de Night (ex: 06 >= 06)
                if ms < ne:
                    messagebox.showerror(
                        "Error",
                        f"Morning start ({ms:02d}) must be greater than or equal to Night end ({ne:02d})"
                    )
                    return
            # Construire la liste des shifts à partir des contrôles
            shifts_list = []
            if morning_var.get():
                shifts_list.append(f"{int(morning_start_var.get()):02d}-{int(morning_end_var.get()):02d}")
            if afternoon_var.get():
                shifts_list.append(f"{int(afternoon_start_var.get()):02d}-{int(afternoon_end_var.get()):02d}")
            if night_var.get():
                shifts_list.append(f"{int(night_start_var.get()):02d}-{int(night_end_var.get()):02d}")
            # Construire la liste des jours actifs à partir des cases cochées
            days_list = [key_fr for _, key_fr in day_order if day_vars[key_fr].get()]
            if not shifts_list:
                messagebox.showerror("Error", "Please configure at least one shift")
                return
            if not days_list:
                messagebox.showerror("Error", "Please select at least one active day")
                return
            # Capacités
            required_counts = {}
            for j, m in capacities_vars.items():
                required_counts[j] = {}
                for s, v in m.items():
                    try:
                        required_counts[j][s] = int(v.get())
                    except Exception:
                        required_counts[j][s] = 1
            dbs = Database()
            dbs.sauvegarder_reglages_site(self.site_actuel_id, shifts_list, days_list, required_counts)
            messagebox.showinfo("Success", "Site settings saved")
            # Rafraîchir immédiatement la popup avec les valeurs persistées
            try:
                charger_reglages_site_courant()
            except Exception:
                pass
            # Si l'on modifie le site courant, recharger structure et UI
            if self.site_actuel_id:
                self._charger_reglages_site_actuel()
                new_planning = Planning(site_id=self.site_actuel_id, jours=days_list, shifts=shifts_list)
                new_planning.travailleurs = self.planning.travailleurs
                self.planning = new_planning
                self.creer_planning_visuel()
                # Refresh availabilities as well
                self._rebuild_disponibilites_from_settings()
                self._build_availabilities_section()
                # Réinitialiser les infos d'alternatives/score après changement de réglages
                if hasattr(self, 'alt_info_var'):
                    self.alt_info_var.set("")

        # (Déplacé en bas à côté de Cancel)

        # Charger immédiatement les réglages du site courant
        try:
            charger_reglages_site_courant()
        except Exception as e:
            print(f"DEBUG: Impossible de charger les réglages du site courant: {e}")
        
        def supprimer_site_avec_travailleurs():
            print("=== DEBUG: Begin site deletion ===")

            # Current site
            vrai_site_id = self.site_actuel_id
            site_nom = self.site_actuel_nom.get()
            if not vrai_site_id:
                messagebox.showwarning("Warning", "No site selected")
                return

            print(f"DEBUG: Site to delete - ID: {vrai_site_id}, Name: {site_nom}")

            # Get counts to show in confirmation
            db = Database()
            nb_travailleurs, nb_plannings = db.compter_elements_site(vrai_site_id)
            print(f"DEBUG: Items to delete - Workers: {nb_travailleurs}, Plannings: {nb_plannings}")

            # Keep track of current site selection
            site_actuel_avant_rechargement = self.site_actuel_id
            print(
                f"DEBUG: Currently selected site - ID: {site_actuel_avant_rechargement}, "
                f"Is current: {site_actuel_avant_rechargement == vrai_site_id}"
            )

            # Confirmation (English)
            message = (
                f"Are you sure you want to delete the site '{site_nom}'?\n\n"
                f"This will permanently delete:\n"
                f"• {nb_travailleurs} worker(s)\n"
                f"• {nb_plannings} planning(s)\n"
                f"• All associated data\n\n"
                f"This action is irreversible!"
            )

            print("DEBUG: Showing confirmation dialog...")
            if not messagebox.askyesno(" Delete confirmation", message):
                print("DEBUG: Deletion cancelled by user")
                return

            print("DEBUG: Confirmation received, deleting...")

            # Execute deletion
            resultat = db.supprimer_site_avec_travailleurs(vrai_site_id)
            print(f"DEBUG: Deletion result: {resultat}")

            if resultat:
                print("DEBUG: Deletion successful, updating UI...")

                # Reload sites list
                print("DEBUG: Reloading sites list...")
                self.charger_sites()
                site_values = [site['nom'] for site in self.sites_disponibles]
                self.site_combobox.configure(values=site_values)

                # If deleted site was selected, show clean empty page
                if site_actuel_avant_rechargement == vrai_site_id:
                    print("DEBUG: Deleted site was selected - showing empty page...")

                    # 1) Reset current site
                    print("DEBUG: Step 1 - Reset current site")
                    self.site_actuel_id = None
                    self.site_actuel_nom.set("")
                    self.site_combobox.set("")

                    # 2) Clear workers list
                    print("DEBUG: Step 2 - Clear all workers")
                    self.planning.travailleurs = []

                    # 3) Clear workers list UI
                    print("DEBUG: Step 3 - Clear workers table")
                    for item in self.table_travailleurs.get_children():
                        self.table_travailleurs.delete(item)

                    # 4) Reset planning structure
                    print("DEBUG: Step 4 - Reset planning")
                    self.planning.planning = {
                        jour: {shift: None for shift in Horaire.SHIFTS.values()}
                        for jour in Horaire.JOURS
                    }

                    # 5) Refresh visual
                    print("DEBUG: Step 5 - Refresh visual planning")
                    self.creer_planning_visuel()

                    # 6) Update title
                    print("DEBUG: Step 6 - Update title")
                    self.titre_label.configure(text="Planning workers - No site selected")

                    # 7) Reset form
                    print("DEBUG: Step 7 - Reset form")
                    self.reinitialiser_formulaire()

                    # 8) Force UI refresh
                    print("DEBUG: Step 8 - Force UI refresh")
                    self.root.update_idletasks()
                    self.root.update()

                    print("DEBUG: ✅ Empty page displayed")

                    # Final info message (English)
                    messagebox.showinfo(
                        "🗑️ Site deleted",
                        (
                            f"The site '{site_nom}' has been successfully deleted.\n\n"
                            f"All associated workers and plannings have been deleted.\n\n"
                            f"Select an existing site or create a new one to continue."
                        ),
                    )
                else:
                    print("DEBUG: Deleted site was not the selected one")
                    messagebox.showinfo("✅ Success", f"Site '{site_nom}' deleted successfully")

                # Close Manage Site window after deletion
                try:
                    sites_window.destroy()
                except Exception:
                    pass
            else:
                print("DEBUG: Error during deletion")
                messagebox.showerror("❌ Error", "An error occurred while deleting the site")

            print("=== DEBUG: End site deletion ===")
        
        # Boutons d'action (pour le site courant)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        btn_supprimer = self.create_styled_button(btn_frame, "🗑️ Delete site", supprimer_site_avec_travailleurs, "cancel")
        btn_supprimer.pack(side="left", padx=5)

        # Boutons à droite: Save settings puis Cancel (Cancel tout à droite)
        btn_save_settings_bottom = self.create_styled_button(
            btn_frame,
            "💾 Save settings",
            sauvegarder_reglages_site_courant,
            "save",
            width=180,
            height=44,
        )
        btn_save_settings_bottom.pack(side="right", padx=5)

        btn_fermer = self.create_styled_button(btn_frame, "✖️ Cancel", sites_window.destroy, "secondary", width=140, height=44)
        btn_fermer.pack(side="right", padx=5)
        
        # Rien à lister ici: on agit sur le site courant

    def basculer_vers_site(self, site_id, site_nom):
        """Bascule vers un site spécifique et met à jour toute l'interface"""
        print(f"DEBUG: Basculement vers le site '{site_nom}' (ID: {site_id})")
        
        # Changer le site actuel
        self.site_actuel_id = site_id
        self.site_actuel_nom.set(site_nom)
        self.site_combobox.set(site_nom)
        
        # Recharger les travailleurs du nouveau site
        self.charger_travailleurs_db()
        
        # Vider le planning actuel
        self.planning.planning = {jour: {shift: None for shift in Horaire.SHIFTS.values()}
                                for jour in Horaire.JOURS}
        
        # Mettre à jour l'affichage visuel du planning
        self.creer_planning_visuel()
        
        # Mettre à jour le titre avec le nombre de travailleurs
        nb_travailleurs = len(self.planning.travailleurs)
        self.titre_label.configure(text=f"Planning workers - {site_nom} ({nb_travailleurs} travailleurs)")
        
        # Réinitialiser le formulaire
        self.reinitialiser_formulaire()
        
        print(f"DEBUG: ✅ Basculement terminé vers '{site_nom}'")

    def traduire_jour(self, jour_fr):
        """Traduit un jour du français vers l'anglais pour l'affichage"""
        return self.jours_traduction.get(jour_fr, jour_fr)

    def _charger_reglages_site_actuel(self):
        """Charge dans self.reglages_site les shifts et jours actifs du site courant.
        Si aucun site n'est sélectionné, utilise les valeurs par défaut d'`Horaire`."""
        if not self.site_actuel_id:
            self.reglages_site = {
                "shifts": list(Horaire.SHIFTS.values()),
                "jours": list(Horaire.JOURS),
            }
            return
        db = Database()
        shifts, jours = db.charger_reglages_site(self.site_actuel_id)
        self.reglages_site = {"shifts": shifts, "jours": jours}

    def _rebuild_disponibilites_from_settings(self):
        jours = self.reglages_site.get("jours") if hasattr(self, 'reglages_site') else None
        shifts = self.reglages_site.get("shifts") if hasattr(self, 'reglages_site') else None
        jours = jours if jours else list(Horaire.JOURS)
        shifts = shifts if shifts else list(Horaire.SHIFTS.values())
        self.disponibilites = {jour: {shift: tk.BooleanVar() for shift in shifts} for jour in jours}
        # 12h removed

    def _build_availabilities_section(self):
        # Si le conteneur de formulaire n'existe pas (popup fermée), ne pas construire l'UI
        if not hasattr(self, 'form_label_frame') or self.form_label_frame is None:
            return
        try:
            if not self.form_label_frame.winfo_exists():
                return
        except Exception:
            return
        # Clear previous if exists
        existing = getattr(self, 'dispo_container', None)
        if existing and existing.winfo_exists():
            existing.destroy()
        # Parent
        self.dispo_container = ttk.Frame(self.form_label_frame)
        self.dispo_container.grid(row=1, column=0, sticky="nsew", pady=5)
        self.dispo_container.columnconfigure(0, weight=1)
        self.dispo_container.columnconfigure(1, weight=0)
        # Ligne 0: barre de contrôle (bouton tout cocher)
        controls_bar = ttk.Frame(self.dispo_container)
        controls_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        # Coche globale: shifts standards
        select_all_shifts_var = tk.BooleanVar(value=False)
        self.select_all_shifts_var = select_all_shifts_var
        def _on_select_all_shifts():
            value = bool(select_all_shifts_var.get())
            dynamic_days = self.reglages_site.get("jours") if hasattr(self, 'reglages_site') else list(Horaire.JOURS)
            dynamic_shifts = self.reglages_site.get("shifts") if hasattr(self, 'reglages_site') else list(Horaire.SHIFTS.values())
            for jour in dynamic_days:
                for shift in dynamic_shifts:
                    var = self.disponibilites.setdefault(jour, {}).setdefault(shift, tk.BooleanVar())
                    var.set(value)
        ttk.Checkbutton(controls_bar, text="Select all shifts", variable=select_all_shifts_var, command=_on_select_all_shifts).pack(side="left")
        # Séparation visuelle
        ttk.Separator(controls_bar, orient='vertical').pack(side="left", fill="y", padx=8)
        # 12h removed
        # Ligne 1: Canvas + scrollbar
        self.dispo_container.rowconfigure(1, weight=1)
        dispo_canvas = tk.Canvas(self.dispo_container, borderwidth=0, highlightthickness=0)
        dispo_scrollbar = ttk.Scrollbar(self.dispo_container, orient="vertical", command=dispo_canvas.yview)
        dispo_frame = ttk.LabelFrame(dispo_canvas, text="Availabilities", padding=10)
        dispo_canvas.configure(yscrollcommand=dispo_scrollbar.set)
        dispo_canvas.grid(row=1, column=0, sticky="nsew", padx=(0, 0))
        dispo_scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 0))
        dispo_window_id = dispo_canvas.create_window((0, 0), window=dispo_frame, anchor="nw", tags=("dispo_frame",))
        # Dynamic days/shifts
        dynamic_days = self.reglages_site.get("jours") if hasattr(self, 'reglages_site') else list(Horaire.JOURS)
        dynamic_shifts = self.reglages_site.get("shifts") if hasattr(self, 'reglages_site') else list(Horaire.SHIFTS.values())
        # 12h removed
        total_cols = 1 + len(dynamic_shifts)
        for i in range(total_cols):
            dispo_frame.columnconfigure(i, weight=1, uniform="avail")
        # Header
        ttk.Label(dispo_frame, text="Day", font=self.header_font).grid(row=0, column=0, padx=6, pady=5, sticky="nsew")
        col = 1
        for shift in dynamic_shifts:
            ttk.Label(dispo_frame, text=shift, font=self.header_font).grid(row=0, column=col, padx=10, pady=5, sticky="nsew")
            col += 1
        morning12_col = None
        night12_col = None
        # Rows
        for i, jour in enumerate(dynamic_days, 1):
            ttk.Label(dispo_frame, text=self.traduire_jour(jour)).grid(row=i, column=0, padx=8, pady=2, sticky="nsew")
            col = 1
            for shift in dynamic_shifts:
                var = self.disponibilites.setdefault(jour, {}).setdefault(shift, tk.BooleanVar())
                ttk.Checkbutton(dispo_frame, variable=var).grid(row=i, column=col, padx=8, pady=2, sticky="nsew")
                col += 1
            # 12h removed
        # Scroll region
        def on_frame_configure(event):
            dispo_canvas.configure(scrollregion=dispo_canvas.bbox("all"))
        def on_canvas_configure(event):
            dispo_canvas.itemconfigure(dispo_window_id, width=event.width)
            col_width = max(int(event.width / max(1, total_cols)) - 4, 60)
            for i in range(total_cols):
                dispo_frame.columnconfigure(i, minsize=col_width)
        dispo_frame.bind("<Configure>", on_frame_configure)
        dispo_canvas.bind("<Configure>", on_canvas_configure)

        # Défilement à la molette (Mac/Windows/Linux)
        def _on_mousewheel(event):
            try:
                if event.delta:
                    # Windows/Mac
                    direction = -1 if event.delta > 0 else 1
                    dispo_canvas.yview_scroll(direction, "units")
                else:
                    # Linux (Button-4/5)
                    if getattr(event, 'num', None) == 4:
                        dispo_canvas.yview_scroll(-1, "units")
                    elif getattr(event, 'num', None) == 5:
                        dispo_canvas.yview_scroll(1, "units")
            except Exception:
                pass

        # Activer le scroll lorsque la souris survole la zone
        def _bind_wheel(_):
            dispo_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            dispo_canvas.bind_all("<Button-4>", _on_mousewheel)
            dispo_canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_wheel(_):
            dispo_canvas.unbind_all("<MouseWheel>")
            dispo_canvas.unbind_all("<Button-4>")
            dispo_canvas.unbind_all("<Button-5>")

        dispo_canvas.bind("<Enter>", _bind_wheel)
        dispo_canvas.bind("<Leave>", _unbind_wheel)

    def _close_worker_popup_if_open(self):
        try:
            if hasattr(self, '_worker_popup') and self._worker_popup is not None and self._worker_popup.winfo_exists():
                self._worker_popup.destroy()
            # Nettoyer les références des widgets de la popup pour éviter d'y accéder après destruction
            self._worker_popup = None
            try:
                if hasattr(self, 'form_label_frame') and self.form_label_frame is not None and not self.form_label_frame.winfo_exists():
                    self.form_label_frame = None
            except Exception:
                self.form_label_frame = None
            try:
                if hasattr(self, 'dispo_container') and self.dispo_container is not None and not self.dispo_container.winfo_exists():
                    self.dispo_container = None
            except Exception:
                self.dispo_container = None
            try:
                if hasattr(self, 'btn_ajouter') and self.btn_ajouter is not None and not self.btn_ajouter.winfo_exists():
                    self.btn_ajouter = None
            except Exception:
                self.btn_ajouter = None
            try:
                if hasattr(self, 'btn_annuler') and self.btn_annuler is not None and not self.btn_annuler.winfo_exists():
                    self.btn_annuler = None
            except Exception:
                self.btn_annuler = None
        except Exception:
            self._worker_popup = None

    def remplir_formulaire_pour_travailleur(self, travailleur):
        """Pré-remplit les champs du formulaire avec un objet `Travailleur`."""
        if not travailleur:
            return
        # Nom et shifts
        self.nom_var.set(travailleur.nom)
        self.nb_shifts_var.set(str(travailleur.nb_shifts_souhaites))
        # Réinitialiser
        for jour, shifts_map in self.disponibilites.items():
            for shift, var in shifts_map.items():
                var.set(False)
        for jour, types_map in self.disponibilites_12h.items():
            for key, var in types_map.items():
                var.set(False)
        # Coche dynamiques
        for jour, shifts in getattr(travailleur, 'disponibilites', {}).items():
            for shift in shifts:
                if jour in self.disponibilites and shift in self.disponibilites[jour]:
                    self.disponibilites[jour][shift].set(True)
        if hasattr(travailleur, 'disponibilites_12h'):
            for jour, shifts_12h in travailleur.disponibilites_12h.items():
                for shift_12h in shifts_12h:
                    if jour in self.disponibilites_12h and shift_12h in self.disponibilites_12h[jour]:
                        self.disponibilites_12h[jour][shift_12h].set(True)

    def _build_form_popup(self, parent, modifier: bool = False):
        """Construit le formulaire dans une popup parent."""
        # Cadre principal
        container = ttk.Frame(parent, padding=10)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        # LabelFrame utilisé par les méthodes existantes
        self.form_label_frame = ttk.LabelFrame(container, text=("Modify worker" if modifier else "Add a worker"), padding=10, style="Section.TLabelframe")
        self.form_label_frame.grid(row=0, column=0, sticky="nsew")
        self.form_label_frame.columnconfigure(0, weight=1)
        self.form_label_frame.rowconfigure(0, weight=0)
        self.form_label_frame.rowconfigure(1, weight=1)
        self.form_label_frame.rowconfigure(2, weight=0)

        # Zone infos
        info_frame = ttk.Frame(self.form_label_frame)
        info_frame.grid(row=0, column=0, sticky="ew", pady=5)
        info_frame.columnconfigure(0, weight=0)
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(2, weight=0)
        info_frame.columnconfigure(3, weight=0)
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.nom_var, width=25).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(info_frame, text="Desired number of shifts:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.nb_shifts_var, width=5).grid(row=0, column=3, padx=5, pady=5)

        # Availabilities dynamiques
        self._rebuild_disponibilites_from_settings()
        self._build_availabilities_section()

        # Boutons
        btns = ttk.Frame(self.form_label_frame)
        btns.grid(row=2, column=0, sticky="ew", pady=10)
        if modifier:
            # En mode modification, on affiche Modify et Delete sur une première rangée
            # et Cancel en dessous au centre
            btns.columnconfigure(0, weight=1)
            btns.columnconfigure(1, weight=1)
            btns.rowconfigure(0, weight=0)
            btns.rowconfigure(1, weight=0)
        else:
            btns.columnconfigure(0, weight=1)
            btns.columnconfigure(1, weight=1)

        def on_validate():
            # Appelle la méthode existante; ne fermer la popup que si succès
            ok = self.ajouter_travailleur()
            if ok:
                self._close_worker_popup_if_open()

        def on_cancel():
            # En mode ajout: réinitialiser et fermer; en mode modif: annuler édition et fermer
            if not modifier:
                try:
                    self.reinitialiser_formulaire()
                except Exception:
                    pass
            else:
                self.annuler_edition()
            self._close_worker_popup_if_open()

        self.btn_ajouter = self.create_styled_button(btns, ("✏️ Modify worker" if modifier else "➕ Add worker"), on_validate, "action")
        if modifier:
            self.btn_ajouter.grid(row=0, column=0, padx=5, sticky="ew")
        else:
            self.btn_ajouter.grid(row=0, column=0, padx=5, sticky="ew")
        
        # Bouton Delete seulement en mode modification
        if modifier:
            def on_delete():
                try:
                    self.supprimer_travailleur()
                except Exception:
                    pass
            btn_supprimer = self.create_styled_button(btns, "🗑️ Delete", on_delete, "cancel")
            btn_supprimer.grid(row=0, column=1, padx=5, sticky="ew")
            
            # Close en gris clair, en dessous, centré
            self.btn_annuler = self.create_styled_button(btns, "✖️ Close", on_cancel, "secondary")
            self.btn_annuler.grid(row=1, column=0, columnspan=2, padx=60, pady=(8, 0), sticky="ew")
        else:
            # Mode ajout: Close en gris clair, centré en dessous du bouton Add
            btns.rowconfigure(0, weight=0)
            btns.rowconfigure(1, weight=0)
            self.btn_annuler = self.create_styled_button(btns, "✖️ Close", on_cancel, "secondary")
            # Étendre le bouton Add sur toute la ligne pour l'alignement
            self.btn_ajouter.grid_configure(columnspan=2)
            self.btn_annuler.grid(row=1, column=0, columnspan=2, padx=60, pady=(8, 0), sticky="ew")

    def ouvrir_popup_travailleur(self, modifier: bool = False):
        """Ouvre une popup pour ajouter/modifier un travailleur."""
        # Vérifier qu'un site est sélectionné pour l'ajout
        if not modifier and self.site_actuel_id is None:
            messagebox.showerror("Error", "Please select a site before adding a worker.")
            return
        # Créer popup
        self._close_worker_popup_if_open()
        popup = tk.Toplevel(self.root)
        popup.title("Modify worker" if modifier else "Add worker")
        popup.geometry("760x600")
        popup.configure(bg="#f0f0f0")
        popup.transient(self.root)
        popup.grab_set()
        self._worker_popup = popup

        # Construire le formulaire
        self._build_form_popup(popup, modifier=modifier)

        # Initialiser le formulaire selon le mode
        if modifier and self.travailleur_en_edition:
            # Pré-remplir pour modification
            self.remplir_formulaire_pour_travailleur(self.travailleur_en_edition)
        else:
            # Mode ajout: champs vides + cases décochées
            try:
                self.reinitialiser_formulaire()
            except Exception:
                # Fallback manuel si nécessaire
                self.nom_var.set("")
                self.nb_shifts_var.set("")
                for jour, shifts_map in self.disponibilites.items():
                    for shift, var in shifts_map.items():
                        var.set(False)
                for jour, types_map in self.disponibilites_12h.items():
                    for key, var in types_map.items():
                        var.set(False)

    def ouvrir_popup_modifier_selection(self):
        """Ouvre la popup de modification pour l'élément sélectionné dans la table."""
        selection = self.table_travailleurs.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a worker to modify")
            return
        item = selection[0]
        nom_travailleur = self.table_travailleurs.item(item, "values")[0]
        cible = None
        for t in self.planning.travailleurs:
            if t.nom == nom_travailleur:
                cible = t
                break
        if not cible:
            messagebox.showerror("Error", "Selected worker not found")
            return
        # Préparer mode édition
        self.mode_edition = True
        self.travailleur_en_edition = cible
        # Ouvrir popup et pré-remplir
        self.ouvrir_popup_travailleur(modifier=True)
        try:
            self.remplir_formulaire_pour_travailleur(cible)
        except Exception:
            pass

    def ouvrir_ajout_site(self):
        """Ouvre la fenêtre d'ajout d'un site avec configuration initiale (shifts + jours actifs)."""
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Site")
        # Agrandir la fenêtre pour afficher tous les éléments confortablement
        add_window.geometry("1000x720")
        add_window.configure(bg="#f0f0f0")
        add_window.transient(self.root)
        add_window.grab_set()
        # Taille minimale et centrage
        try:
            add_window.update_idletasks()
            add_window.minsize(900, 650)
            # Centrer par rapport à la fenêtre principale
            rw = self.root.winfo_width(); rh = self.root.winfo_height()
            rx = self.root.winfo_rootx(); ry = self.root.winfo_rooty()
            width, height = 1000, 720
            if rw and rh and rw > 1 and rh > 1:
                x = rx + max(0, (rw - width) // 2)
                y = ry + max(0, (rh - height) // 2)
            else:
                sw = add_window.winfo_screenwidth(); sh = add_window.winfo_screenheight()
                x = max(0, (sw - width) // 2)
                y = max(0, (sh - height) // 2)
            add_window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

        main = ttk.Frame(add_window, padding=20)
        main.pack(fill="both", expand=True)

        # Nom & Description
        ttk.Label(main, text="Site name:").grid(row=0, column=0, sticky="w")
        nom_var = tk.StringVar()
        ttk.Entry(main, textvariable=nom_var, width=30).grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ttk.Label(main, text="Description:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        desc_var = tk.StringVar()
        ttk.Entry(main, textvariable=desc_var, width=30).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(6, 0))
        main.columnconfigure(1, weight=1)

        # Shifts (Morning/Afternoon/Night)
        settings_frame = ttk.LabelFrame(main, text="Shifts", padding=10)
        settings_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 8))

        def make_hour_spinbox(parent, var):
            return tk.Spinbox(parent, from_=0, to=23, wrap=True, width=3, textvariable=var, state="normal", format="%02.0f")

        controls_frame = ttk.Frame(settings_frame)
        controls_frame.pack(fill="x")
        morning_var = tk.BooleanVar(value=True)
        afternoon_var = tk.BooleanVar(value=True)
        night_var = tk.BooleanVar(value=True)

        # Morning
        mf = ttk.LabelFrame(controls_frame, text="Morning")
        mf.grid(row=0, column=0, padx=5, sticky="w")
        ttk.Checkbutton(mf, text="Enable", variable=morning_var).grid(row=0, column=0, pady=2, sticky="w")
        ttk.Label(mf, text="Start:").grid(row=1, column=0, sticky="w")
        m_start = tk.StringVar(value="06"); m_start_sb = make_hour_spinbox(mf, m_start); m_start_sb.grid(row=1, column=1)
        ttk.Label(mf, text="End:").grid(row=1, column=2, sticky="w")
        m_end = tk.StringVar(value="14"); m_end_sb = make_hour_spinbox(mf, m_end); m_end_sb.grid(row=1, column=3)

        # Afternoon
        af = ttk.LabelFrame(controls_frame, text="Afternoon")
        af.grid(row=0, column=1, padx=5, sticky="w")
        ttk.Checkbutton(af, text="Enable", variable=afternoon_var).grid(row=0, column=0, pady=2, sticky="w")
        ttk.Label(af, text="Start:").grid(row=1, column=0, sticky="w")
        a_start = tk.StringVar(value="14"); a_start_sb = make_hour_spinbox(af, a_start); a_start_sb.grid(row=1, column=1)
        ttk.Label(af, text="End:").grid(row=1, column=2, sticky="w")
        a_end = tk.StringVar(value="22"); a_end_sb = make_hour_spinbox(af, a_end); a_end_sb.grid(row=1, column=3)

        # Night
        nf = ttk.LabelFrame(controls_frame, text="Night")
        nf.grid(row=0, column=2, padx=5, sticky="w")
        ttk.Checkbutton(nf, text="Enable", variable=night_var).grid(row=0, column=0, pady=2, sticky="w")
        ttk.Label(nf, text="Start:").grid(row=1, column=0, sticky="w")
        n_start = tk.StringVar(value="22"); n_start_sb = make_hour_spinbox(nf, n_start); n_start_sb.grid(row=1, column=1)
        ttk.Label(nf, text="End:").grid(row=1, column=2, sticky="w")
        n_end = tk.StringVar(value="06"); n_end_sb = make_hour_spinbox(nf, n_end); n_end_sb.grid(row=1, column=3)

        # Days
        days_frame = ttk.LabelFrame(main, text="Active days", padding=10)
        days_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        day_order = [
            ("Sunday", "dimanche"), ("Monday", "lundi"), ("Tuesday", "mardi"),
            ("Wednesday", "mercredi"), ("Thursday", "jeudi"), ("Friday", "vendredi"), ("Saturday", "samedi")
        ]
        day_vars = {key_fr: tk.BooleanVar(value=True) for _, key_fr in day_order}
        for i, (en, fr) in enumerate(day_order):
            ttk.Checkbutton(days_frame, text=en, variable=day_vars[fr]).grid(row=i // 4, column=i % 4, padx=4, pady=2, sticky="w")

        def build_shifts():
            shifts = []
            if morning_var.get():
                shifts.append(f"{int(m_start.get()):02d}-{int(m_end.get()):02d}")
            if afternoon_var.get():
                shifts.append(f"{int(a_start.get()):02d}-{int(a_end.get()):02d}")
            if night_var.get():
                shifts.append(f"{int(n_start.get()):02d}-{int(n_end.get()):02d}")
            return shifts

        def get_active_days():
            return [fr for _, fr in day_order if day_vars[fr].get()]

        # Required staff (capacities)
        caps_group = ttk.LabelFrame(main, text="Required staff (per day/shift)", padding=10)
        caps_group.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 8))
        caps_vars = {}
        caps_frame = ttk.Frame(caps_group)
        caps_frame.pack(fill="x")

        def rebuild_caps_grid():
            # Reconstruire la grille selon shifts/days actifs
            for child in caps_frame.winfo_children():
                child.destroy()
            shifts = build_shifts()
            jours = get_active_days()
            if not shifts or not jours:
                return
            # Conserver les valeurs saisies si possible
            previous = {j: {s: (caps_vars.get(j, {}).get(s).get() if caps_vars.get(j, {}).get(s) else "") for s in (caps_vars.get(j, {}) or {})} for j in caps_vars}
            # En-têtes
            ttk.Label(caps_frame, text="Day").grid(row=0, column=0, padx=4, pady=2)
            for ci, s in enumerate(shifts, 1):
                ttk.Label(caps_frame, text=s).grid(row=0, column=ci, padx=4, pady=2)
            # Lignes
            for ri, j in enumerate(jours, 1):
                ttk.Label(caps_frame, text=self.traduire_jour(j)).grid(row=ri, column=0, padx=4, pady=2, sticky="w")
                for ci, s in enumerate(shifts, 1):
                    default_val = previous.get(j, {}).get(s, "1") or "1"
                    var = caps_vars.setdefault(j, {}).setdefault(s, tk.StringVar(value=default_val))
                    tk.Spinbox(caps_frame, from_=1, to=10, width=3, textvariable=var).grid(row=ri, column=ci, padx=2, pady=2)

        # Rebuild capacities grid when shifts/days change
        def on_change_and_rebuild(fn=None):
            if callable(fn):
                fn()
            rebuild_caps_grid()

        # Hook changes for shifts
        orig_update_spin_states = None
        try:
            orig_update_spin_states = update_spin_states
        except Exception:
            pass
        def update_spin_states_wrapper():
            if orig_update_spin_states:
                orig_update_spin_states()
            rebuild_caps_grid()
        # Remplacer les callbacks sur les checkbuttons shift
        try:
            morning_var.trace_add('write', lambda *args: update_spin_states_wrapper())
            afternoon_var.trace_add('write', lambda *args: update_spin_states_wrapper())
            night_var.trace_add('write', lambda *args: update_spin_states_wrapper())
        except Exception:
            pass
        # Rebuild when hours change
        try:
            m_start.trace_add('write', lambda *args: rebuild_caps_grid())
            m_end.trace_add('write', lambda *args: rebuild_caps_grid())
            a_start.trace_add('write', lambda *args: rebuild_caps_grid())
            a_end.trace_add('write', lambda *args: rebuild_caps_grid())
            n_start.trace_add('write', lambda *args: rebuild_caps_grid())
            n_end.trace_add('write', lambda *args: rebuild_caps_grid())
        except Exception:
            pass
        # Hook day checkbuttons
        for i, (en, fr) in enumerate(day_order):
            # reconfigurer la commande pour rebuild
            # On recrée le checkbutton avec commande si nécessaire
            # Mais ici on peut attacher un trace sur la variable
            try:
                day_vars[fr].trace_add('write', lambda *args: rebuild_caps_grid())
            except Exception:
                pass

        # Première construction
        rebuild_caps_grid()

        def save_site():
            nom = nom_var.get().strip()
            if not nom:
                messagebox.showerror("Erreur", "Veuillez entrer un nom de site")
                return
            description = desc_var.get().strip()
            shifts_list = build_shifts()
            days_list = get_active_days()
            if not shifts_list:
                messagebox.showerror("Erreur", "Veuillez définir au moins un shift")
                return
            if not days_list:
                messagebox.showerror("Erreur", "Veuillez sélectionner au moins un jour actif")
                return
            # Construire required_counts depuis la grille
            required_counts = {}
            for j in days_list:
                required_counts[j] = {}
                for s in shifts_list:
                    try:
                        required_counts[j][s] = int(caps_vars.get(j, {}).get(s, tk.StringVar(value="1")).get())
                    except Exception:
                        required_counts[j][s] = 1
            db = Database()
            site_id = db.sauvegarder_site(nom, description)
            if not site_id:
                messagebox.showerror("Erreur", "Un site avec ce nom existe déjà")
                return
            db.sauvegarder_reglages_site(site_id, shifts_list, days_list, required_counts)
            messagebox.showinfo("Succès", f"Site '{nom}' créé")
            # Rafraîchir la liste en haut
            self.charger_sites()
            self.site_combobox.configure(values=[site['nom'] for site in self.sites_disponibles])
            add_window.destroy()

        btns = ttk.Frame(main)
        btns.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        # Utiliser le même style que dans "Manage Site"
        btn_create_site = self.create_styled_button(btns, "✅ Create", save_site, "save", width=180, height=44)
        btn_create_site.pack(side="right", padx=(6, 0))
        btn_cancel_site = self.create_styled_button(btns, "✖️ Cancel", add_window.destroy, "secondary", width=140, height=44)
        btn_cancel_site.pack(side="right", padx=6)
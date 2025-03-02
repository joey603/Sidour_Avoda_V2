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
        self.root.title("Gestionnaire de Planning")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
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
        
        # Variables pour le formulaire
        self.nom_var = tk.StringVar()
        self.nb_shifts_var = tk.StringVar()
        self.mode_edition = False
        self.travailleur_en_edition = None
        
        # Création des disponibilités
        self.disponibilites = {jour: {shift: tk.BooleanVar() 
            for shift in Horaire.SHIFTS.values()}
            for jour in Horaire.JOURS}
        
        # Création des disponibilités pour les gardes de 12h
        self.disponibilites_12h = {jour: {
            "matin_12h": tk.BooleanVar(),  # 06-18
            "nuit_12h": tk.BooleanVar()    # 18-06
        } for jour in Horaire.JOURS}
        
        # Créer l'interface
        self.creer_interface()
        
        # Charger les travailleurs après l'initialisation de l'interface
        self.charger_travailleurs_db()

    def creer_interface(self):
        # Frame principale avec deux colonnes
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
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
        
        # Colonne gauche - Formulaire et liste des travailleurs
        left_frame = ttk.Frame(main_frame, padding=10)
        left_frame.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Configurer left_frame pour qu'il s'adapte à la taille de la fenêtre
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=0)  # Titre
        left_frame.rowconfigure(1, weight=1)  # Formulaire
        left_frame.rowconfigure(2, weight=1)  # Liste
        left_frame.rowconfigure(3, weight=0)  # Boutons génération
        left_frame.rowconfigure(4, weight=0)  # Boutons DB
        
        # Titre
        titre_label = ttk.Label(left_frame, text="Gestion des Travailleurs", font=self.title_font)
        titre_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Frame pour l'ajout de travailleur
        form_frame = ttk.Frame(left_frame)
        form_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(0, weight=1)
        self.creer_formulaire_travailleur(form_frame)
        
        # Liste des travailleurs
        liste_frame = ttk.Frame(left_frame)
        liste_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        liste_frame.columnconfigure(0, weight=1)
        liste_frame.rowconfigure(0, weight=1)
        self.creer_liste_travailleurs(liste_frame)
        
        # Frame pour les boutons de génération
        frame_generation = ttk.Frame(left_frame)
        frame_generation.grid(row=3, column=0, sticky="ew", pady=10)
        frame_generation.columnconfigure(0, weight=1)
        frame_generation.columnconfigure(1, weight=1)
        frame_generation.columnconfigure(2, weight=1)
        
        # Boutons pour générer le planning - utiliser des boutons tk standard pour plus de contrôle visuel
        btn_generer = self.create_styled_button(frame_generation, "Générer Planning", 
                                              self.generer_planning, "action")
        btn_generer.grid(row=0, column=0, padx=5, sticky="ew")
        
        btn_combler = self.create_styled_button(frame_generation, "Combler les trous", 
                                             self.combler_trous, "action")
        btn_combler.grid(row=0, column=1, padx=5, sticky="ew")
        
        btn_generer_12h = self.create_styled_button(frame_generation, "Suggestion 12h", 
                                                 self.generer_planning_12h, "action")
        btn_generer_12h.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Frame pour la sauvegarde et le chargement
        frame_db = ttk.Frame(left_frame)
        frame_db.grid(row=4, column=0, sticky="ew", pady=10)
        frame_db.columnconfigure(0, weight=1)
        frame_db.columnconfigure(1, weight=1)
        frame_db.columnconfigure(2, weight=1)
        
        btn_sauvegarder = self.create_styled_button(frame_db, "Sauvegarder Planning", 
                                                 self.sauvegarder_planning, "save")
        btn_sauvegarder.grid(row=0, column=0, padx=5, sticky="ew")
        
    
        
        btn_agenda = self.create_styled_button(frame_db, "Agenda Plannings", 
                                                self.ouvrir_agenda_plannings, "action")
        btn_agenda.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Colonne droite - Affichage du planning
        right_frame = ttk.Frame(main_frame, padding=10)
        right_frame.pack(side=tk.RIGHT, fill="both", expand=True)
        
        # Titre
        titre_planning = ttk.Label(right_frame, text="Planning de la Semaine", font=self.title_font)
        titre_planning.pack(pady=(0, 20))
        
        # Création du canvas pour le planning visuel
        self.canvas_frame = ttk.Frame(right_frame, padding=5)
        self.canvas_frame.pack(fill="both", expand=True)
        
        # Initialisation du canvas vide
        self.creer_planning_visuel()

    def create_styled_button(self, parent, text, command, button_type="action"):
        """Crée un bouton stylisé avec des couleurs vives garanties"""
        # Définir des couleurs très vives pour s'assurer qu'elles s'affichent
        if button_type == "action":
            bg_color = "#007BFF"  # Bleu vif
            hover_color = "#0056b3"
        elif button_type == "cancel":
            bg_color = "#DC3545"  # Rouge vif
            hover_color = "#c82333"
        elif button_type == "save":
            bg_color = "#28A745"  # Vert vif
            hover_color = "#218838"
        elif button_type == "load":
            bg_color = "#FFC107"  # Jaune vif
            hover_color = "#e0a800"
            fg_color = "black"    # Texte noir pour le jaune
        else:
            bg_color = "#007BFF"
            hover_color = "#0056b3"
        
        # Couleur du texte (noir pour le jaune, blanc pour les autres)
        fg_color = "black" if button_type == "load" else "white"
        
        # Créer un Canvas pour le bouton personnalisé
        canvas_width = 150
        canvas_height = 40
        
        canvas = tk.Canvas(
            parent,
            width=canvas_width,
            height=canvas_height,
            bg=bg_color,
            highlightthickness=0
        )
        
        # Ajouter le texte au centre du canvas
        text_id = canvas.create_text(
            canvas_width // 2,
            canvas_height // 2,
            text=text,
            fill=fg_color,
            font=self.normal_font
        )
        
        # Fonction pour gérer le clic
        def on_click(event):
            command()
        
        # Fonctions pour les effets de survol
        def on_enter(event):
            canvas.config(bg=hover_color)
        
        def on_leave(event):
            canvas.config(bg=bg_color)
        
        # Lier les événements
        canvas.bind("<Button-1>", on_click)
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
                    canvas.unbind("<Enter>")
                    canvas.unbind("<Leave>")
                else:
                    canvas.enabled = True
                    canvas.config(bg=bg_color)
                    canvas.bind("<Button-1>", on_click)
                    canvas.bind("<Enter>", on_enter)
                    canvas.bind("<Leave>", on_leave)
        
        # Ajouter la méthode configure au canvas
        canvas.configure = configure
        
        return canvas

    def creer_formulaire_travailleur(self, frame):
        # Frame pour le formulaire d'ajout de travailleur
        self.form_label_frame = ttk.LabelFrame(frame, text="Ajouter un travailleur", padding=10, style="Section.TLabelframe")
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
        
        ttk.Label(info_frame, text="Nom:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.nom_var, width=25).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(info_frame, text="Nombre de shifts souhaités:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.nb_shifts_var, width=5).grid(row=0, column=3, padx=5, pady=5)
        
        # Conteneur pour la section des disponibilités avec scrollbar
        dispo_container = ttk.Frame(self.form_label_frame)
        dispo_container.grid(row=1, column=0, sticky="nsew", pady=5)
        dispo_container.columnconfigure(0, weight=1)
        dispo_container.columnconfigure(1, weight=0)  # Colonne de la scrollbar sans expansion
        dispo_container.rowconfigure(0, weight=1)
        
        # Créer un canvas pour permettre le défilement
        dispo_canvas = tk.Canvas(dispo_container, borderwidth=0, highlightthickness=0)
        dispo_scrollbar = ttk.Scrollbar(dispo_container, orient="vertical", command=dispo_canvas.yview)
        
        # Frame à l'intérieur du canvas qui contiendra les disponibilités
        dispo_frame = ttk.LabelFrame(dispo_canvas, text="Disponibilités", padding=10)
        
        # Configurer le canvas pour qu'il défile avec la frame interne
        dispo_canvas.configure(yscrollcommand=dispo_scrollbar.set)
        
        # Placer les widgets dans le conteneur sans espace entre eux
        dispo_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 0))
        dispo_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 0))
        
        # Créer une fenêtre dans le canvas pour y placer la frame
        dispo_canvas.create_window((0, 0), window=dispo_frame, anchor="nw", tags="dispo_frame")
        
        # Configurer les colonnes pour qu'elles s'adaptent avec une largeur plus importante
        for i in range(6):  # 1 pour le jour + 3 pour les shifts + 2 pour les 12h
            if i == 0:
                dispo_frame.columnconfigure(i, weight=1, minsize=100)  # Colonne des jours
            else:
                dispo_frame.columnconfigure(i, weight=2, minsize=120)  # Colonnes des shifts et 12h
        
        # En-têtes des colonnes
        ttk.Label(dispo_frame, text="Jour", font=self.header_font).grid(row=0, column=0, padx=10, pady=5)
        col = 1
        for shift in Horaire.SHIFTS.values():
            ttk.Label(dispo_frame, text=shift, font=self.header_font).grid(row=0, column=col, padx=20, pady=5)
            col += 1
        
        # Ajouter les colonnes pour les gardes de 12h
        ttk.Label(dispo_frame, text="Matin 12h\n(06-18)", font=self.header_font).grid(row=0, column=col, padx=20, pady=5)
        col += 1
        ttk.Label(dispo_frame, text="Nuit 12h\n(18-06)", font=self.header_font).grid(row=0, column=col, padx=20, pady=5)
        
        # Lignes pour chaque jour avec plus d'espace horizontal
        for i, jour in enumerate(Horaire.JOURS, 1):
            ttk.Label(dispo_frame, text=jour).grid(row=i, column=0, padx=15, pady=2, sticky="w")
            col = 1
            for shift in Horaire.SHIFTS.values():
                ttk.Checkbutton(dispo_frame, variable=self.disponibilites[jour][shift]).grid(row=i, column=col, padx=20, pady=2)
                col += 1
            
            # Ajouter les cases à cocher pour les gardes de 12h avec plus d'espace
            ttk.Checkbutton(dispo_frame, variable=self.disponibilites_12h[jour]["matin_12h"]).grid(row=i, column=col, padx=20, pady=2)
            col += 1
            ttk.Checkbutton(dispo_frame, variable=self.disponibilites_12h[jour]["nuit_12h"]).grid(row=i, column=col, padx=20, pady=2)
        
        # Fonction pour ajuster la taille du canvas quand la frame interne change
        def configure_scroll_region(event):
            dispo_canvas.configure(scrollregion=dispo_canvas.bbox("all"))
            # Définir la largeur du canvas pour qu'elle corresponde à celle de la frame
            width = dispo_frame.winfo_reqwidth()
            dispo_canvas.config(width=width)
            
            # Forcer une largeur minimale pour le canvas
            if width < 200:  # Définir une largeur minimale
                dispo_canvas.config(width=1000)
        
        # Lier la fonction à l'événement de configuration de la frame
        dispo_frame.bind("<Configure>", configure_scroll_region)
        
        # Boutons
        btn_frame = ttk.Frame(self.form_label_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        # Utiliser des boutons stylisés
        self.btn_ajouter = self.create_styled_button(btn_frame, "Ajouter Travailleur", 
                                                  self.ajouter_travailleur, "action")
        self.btn_ajouter.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.btn_annuler = self.create_styled_button(btn_frame, "Annuler", 
                                                  self.annuler_edition, "cancel")
        self.btn_annuler.enabled = False
        self.btn_annuler.config(bg="#cccccc")
        self.btn_annuler.unbind("<Button-1>")
        self.btn_annuler.unbind("<Enter>")
        self.btn_annuler.unbind("<Leave>")
        self.btn_annuler.grid(row=0, column=1, padx=5, sticky="ew")

    def creer_liste_travailleurs(self, frame):
        # Liste des travailleurs
        frame_liste = ttk.LabelFrame(frame, text="Travailleurs enregistrés", padding=10, style="Section.TLabelframe")
        frame_liste.grid(row=0, column=0, sticky="nsew")
        frame_liste.columnconfigure(0, weight=1)
        frame_liste.rowconfigure(0, weight=1)  # Table
        frame_liste.rowconfigure(1, weight=0)  # Boutons
        
        # Création d'un Treeview pour afficher les travailleurs sous forme de tableau
        columns = ("nom", "shifts")
        self.table_travailleurs = ttk.Treeview(frame_liste, columns=columns, show="headings", height=8)
        self.table_travailleurs.heading("nom", text="Nom")
        self.table_travailleurs.heading("shifts", text="Shifts souhaités")
        
        self.table_travailleurs.column("nom", width=150)
        self.table_travailleurs.column("shifts", width=100)
        
        # Scrollbar pour la table
        scrollbar = ttk.Scrollbar(frame_liste, orient="vertical", command=self.table_travailleurs.yview)
        self.table_travailleurs.configure(yscrollcommand=scrollbar.set)
        
        # Placement de la table et de la scrollbar
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table_travailleurs.grid(row=0, column=0, sticky="nsew")
        
        # Lier la sélection dans la table à l'édition
        self.table_travailleurs.bind('<<TreeviewSelect>>', self.selectionner_travailleur)
        
        # Boutons pour gérer les travailleurs
        btn_frame = ttk.Frame(frame_liste)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        btn_frame.columnconfigure(0, weight=1)
        
        # Utiliser un bouton stylisé
        btn_supprimer = self.create_styled_button(btn_frame, "Supprimer", 
                                               self.supprimer_travailleur, "cancel")
        btn_supprimer.grid(row=0, column=0, sticky="e", padx=5)

    def creer_planning_visuel(self):
        """Crée une représentation visuelle du planning"""
        # Supprimer l'ancien planning s'il existe
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
        
        # En-têtes des colonnes
        ttk.Label(planning_frame, text="Jour", font=self.header_font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        for i, shift in enumerate(Horaire.SHIFTS.values()):
            ttk.Label(planning_frame, text=shift, font=self.header_font).grid(row=0, column=i+1, padx=5, pady=5)
        
        # Remplir le planning
        for i, jour in enumerate(Horaire.JOURS):
            ttk.Label(planning_frame, text=jour.capitalize(), font=self.normal_font).grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
            
            for j, shift in enumerate(Horaire.SHIFTS.values()):
                travailleur = self.planning.planning[jour][shift]
                
                # Créer un frame pour la cellule
                cell_frame = ttk.Frame(planning_frame, width=150, height=50)
                cell_frame.grid(row=i+1, column=j+1, padx=2, pady=2, sticky="nsew")
                cell_frame.grid_propagate(False)  # Empêcher le frame de s'adapter à son contenu
                
                if travailleur:
                    # Vérifier si c'est une garde partagée (format: "nom1 / nom2")
                    if " / " in travailleur:
                        # Diviser la cellule en deux parties (haut/bas)
                        noms = travailleur.split(" / ")
                        if len(noms) == 2:
                            # Créer un frame pour contenir les deux labels
                            shared_frame = ttk.Frame(cell_frame)
                            shared_frame.pack(fill="both", expand=True)
                            
                            # Configurer le frame pour qu'il ait deux lignes de même hauteur
                            shared_frame.rowconfigure(0, weight=1)
                            shared_frame.rowconfigure(1, weight=1)
                            shared_frame.columnconfigure(0, weight=1)
                            
                            # Obtenir les couleurs des deux travailleurs
                            color1 = self.travailleur_colors.get(noms[0], "#FFFFFF")
                            color2 = self.travailleur_colors.get(noms[1], "#FFFFFF")
                            
                            # Créer deux labels, un pour chaque travailleur
                            label1 = tk.Label(shared_frame, text=noms[0], bg=color1, 
                                            font=self.normal_font, relief="raised", borderwidth=1)
                            label1.grid(row=0, column=0, sticky="nsew")
                            
                            label2 = tk.Label(shared_frame, text=noms[1], bg=color2, 
                                            font=self.normal_font, relief="raised", borderwidth=1)
                            label2.grid(row=1, column=0, sticky="nsew")
                        else:
                            # Cas imprévu, utiliser un affichage standard
                            label = tk.Label(cell_frame, text=travailleur, bg="#F0F0F0", 
                                           font=self.normal_font, relief="raised", borderwidth=1)
                            label.pack(fill="both", expand=True)
                    else:
                        # Utiliser la couleur associée au travailleur
                        color = self.travailleur_colors.get(travailleur, "#FFFFFF")
                        
                        # Créer un label avec un fond coloré
                        label = tk.Label(cell_frame, text=travailleur, bg=color, 
                                       font=self.normal_font, relief="raised", borderwidth=1)
                        label.pack(fill="both", expand=True)
                else:
                    # Cellule vide
                    label = tk.Label(cell_frame, text="Non assigné", bg="#F0F0F0", 
                                   font=self.normal_font, relief="sunken", borderwidth=1)
                    label.pack(fill="both", expand=True)
        
        # Configurer les colonnes pour qu'elles s'étendent
        for i in range(4):  # 1 colonne pour les jours + 3 colonnes pour les shifts
            planning_frame.columnconfigure(i, weight=1)
        
        # Configurer les lignes pour qu'elles s'étendent
        for i in range(8):  # 1 ligne pour les en-têtes + 7 lignes pour les jours
            planning_frame.rowconfigure(i, weight=1)

    def ajouter_travailleur(self):
        # Récupérer les valeurs du formulaire
        nom = self.nom_var.get().strip()
        nb_shifts_str = self.nb_shifts_var.get().strip()
        
        # Validation des entrées
        if not nom:
            messagebox.showerror("Erreur", "Veuillez entrer un nom")
            return
        
        try:
            nb_shifts = int(nb_shifts_str)
            if nb_shifts <= 0:
                raise ValueError("Le nombre de shifts doit être positif")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide de shifts")
            return
        
        # Récupérer les disponibilités
        disponibilites = {}
        disponibilites_12h = {}
        
        for jour in Horaire.JOURS:
            shifts_dispo = []
            for shift in Horaire.SHIFTS.values():
                if self.disponibilites[jour][shift].get():
                    shifts_dispo.append(shift)
            
            shifts_12h = []
            if self.disponibilites_12h[jour]["matin_12h"].get():
                shifts_12h.append("matin_12h")
            if self.disponibilites_12h[jour]["nuit_12h"].get():
                shifts_12h.append("nuit_12h")
            
            if shifts_dispo:  # Ajouter seulement si au moins un shift est disponible
                disponibilites[jour] = shifts_dispo
            
            if shifts_12h:  # Ajouter seulement si au moins une garde de 12h est disponible
                disponibilites_12h[jour] = shifts_12h
        
        if not disponibilites and not disponibilites_12h:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins une disponibilité")
            return
        
        # Créer ou mettre à jour le travailleur
        if self.mode_edition and self.travailleur_en_edition:
            # Trouver l'index du travailleur en édition
            index = self.planning.travailleurs.index(self.travailleur_en_edition)
            
            # Mettre à jour le travailleur
            self.planning.travailleurs[index].nom = nom
            self.planning.travailleurs[index].nb_shifts_souhaites = nb_shifts
            self.planning.travailleurs[index].disponibilites = disponibilites
            self.planning.travailleurs[index].disponibilites_12h = disponibilites_12h
            
            messagebox.showinfo("Succès", f"Travailleur {nom} modifié avec succès")
            
            # Sauvegarder dans la base de données
            db = Database()
            db.sauvegarder_travailleur(self.planning.travailleurs[index])
            
            # Réinitialiser le mode édition
            self.mode_edition = False
            self.travailleur_en_edition = None
            self.btn_ajouter.config(text="Ajouter Travailleur")
            self.btn_annuler.config(state=tk.DISABLED)
        else:
            # Création d'un nouveau travailleur
            travailleur = Travailleur(nom, disponibilites, nb_shifts)
            travailleur.disponibilites_12h = disponibilites_12h
            self.planning.ajouter_travailleur(travailleur)
            
            # Sauvegarder dans la base de données
            db = Database()
            db.sauvegarder_travailleur(travailleur)
            
            messagebox.showinfo("Succès", f"Travailleur {nom} ajouté avec succès")
        
        # Mise à jour de la liste des travailleurs
        self.mettre_a_jour_liste_travailleurs()
        
        # Réinitialisation du formulaire
        self.reinitialiser_formulaire()

    def reinitialiser_formulaire(self):
        self.nom_var.set("")
        self.nb_shifts_var.set("")
        for jour in Horaire.JOURS:
            for shift in Horaire.SHIFTS.values():
                self.disponibilites[jour][shift].set(False)
            self.disponibilites_12h[jour]["matin_12h"].set(False)
            self.disponibilites_12h[jour]["nuit_12h"].set(False)

    def mettre_a_jour_liste_travailleurs(self):
        # Vider la table
        for item in self.table_travailleurs.get_children():
            self.table_travailleurs.delete(item)
        
        # Remplir avec les travailleurs actuels
        for travailleur in self.planning.travailleurs:
            self.table_travailleurs.insert("", tk.END, values=(travailleur.nom, travailleur.nb_shifts_souhaites))

    def selectionner_travailleur(self, event):
        """Sélectionne un travailleur dans la liste pour l'éditer"""
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
                
                # Réinitialiser toutes les disponibilités
                for jour in Horaire.JOURS:
                    for shift in Horaire.SHIFTS.values():
                        self.disponibilites[jour][shift].set(False)
                    self.disponibilites_12h[jour]["matin_12h"].set(False)
                    self.disponibilites_12h[jour]["nuit_12h"].set(False)
                
                # Définir les disponibilités du travailleur
                for jour, shifts in travailleur.disponibilites.items():
                    for shift in shifts:
                        self.disponibilites[jour][shift].set(True)
                
                # Définir les disponibilités 12h si elles existent
                if hasattr(travailleur, 'disponibilites_12h'):
                    for jour, shifts_12h in travailleur.disponibilites_12h.items():
                        for shift_12h in shifts_12h:
                            self.disponibilites_12h[jour][shift_12h].set(True)
                
                # Passer en mode édition
                self.mode_edition = True
                self.travailleur_en_edition = travailleur
                
                # Changer le titre du formulaire
                self.form_label_frame.configure(text="Modifier un travailleur")
                
                # Changer le texte du bouton Ajouter en Modifier
                if hasattr(self.btn_ajouter, 'itemconfig'):
                    # Si c'est un canvas
                    text_id = self.btn_ajouter.find_withtag("all")[0]  # Trouver le texte dans le canvas
                    self.btn_ajouter.itemconfig(text_id, text="Modifier Travailleur")
                else:
                    # Si c'est un bouton standard
                    self.btn_ajouter.config(text="Modifier Travailleur")
                
                # Activer le bouton Annuler
                if hasattr(self.btn_annuler, 'configure'):
                    self.btn_annuler.configure(state=tk.NORMAL)
                else:
                    # Si c'est un canvas
                    self.btn_annuler.enabled = True
                    self.btn_annuler.config(bg="#DC3545")
                    self.btn_annuler.bind("<Button-1>", lambda e: self.annuler_edition())
                    self.btn_annuler.bind("<Enter>", lambda e: self.btn_annuler.config(bg="#c82333"))
                    self.btn_annuler.bind("<Leave>", lambda e: self.btn_annuler.config(bg="#DC3545"))
                
                break

    def annuler_edition(self):
        """Annule l'édition en cours et réinitialise le formulaire"""
        self.mode_edition = False
        self.travailleur_en_edition = None
        
        # Réinitialiser le formulaire
        self.nom_var.set("")
        self.nb_shifts_var.set("")
        
        # Réinitialiser toutes les disponibilités
        for jour in Horaire.JOURS:
            for shift in Horaire.SHIFTS.values():
                self.disponibilites[jour][shift].set(False)
            self.disponibilites_12h[jour]["matin_12h"].set(False)
            self.disponibilites_12h[jour]["nuit_12h"].set(False)
        
        # Changer le titre du formulaire
        self.form_label_frame.configure(text="Ajouter un travailleur")
        
        # Changer le texte du bouton Modifier en Ajouter
        if hasattr(self.btn_ajouter, 'itemconfig'):
            # Si c'est un canvas
            text_id = self.btn_ajouter.find_withtag("all")[0]  # Trouver le texte dans le canvas
            self.btn_ajouter.itemconfig(text_id, text="Ajouter Travailleur")
        else:
            # Si c'est un bouton standard
            self.btn_ajouter.config(text="Ajouter Travailleur")
        
        # Désactiver le bouton Annuler
        if hasattr(self.btn_annuler, 'configure'):
            self.btn_annuler.configure(state=tk.DISABLED)
        else:
            # Si c'est un canvas
            self.btn_annuler.enabled = False
            self.btn_annuler.config(bg="#cccccc")
            self.btn_annuler.unbind("<Button-1>")
            self.btn_annuler.unbind("<Enter>")
            self.btn_annuler.unbind("<Leave>")

    def verifier_repos_entre_gardes(self, planning, travailleur):
        """Vérifie qu'il y a suffisamment de repos entre les gardes d'un travailleur"""
        # Créer une liste chronologique de toutes les gardes
        gardes_chronologiques = []
        
        # Mapping des noms de shifts aux heures de début
        shift_heures = {
            "06-14": 6,   # Matin
            "14-22": 14,  # Après-midi
            "22-06": 22   # Nuit
        }
        
        for i, jour in enumerate(Horaire.JOURS):
            for shift_name, shift_value in Horaire.SHIFTS.items():
                if planning[jour][shift_value] == travailleur.nom:
                    # Obtenir l'heure de début du shift
                    heure_debut = shift_heures[shift_value]
                    
                    # Stocker (jour_index, heure_debut, shift_name)
                    gardes_chronologiques.append((i, heure_debut, shift_value))
        
        # Trier par jour puis par heure
        gardes_chronologiques.sort()
        
        # Vérifier les intervalles entre gardes consécutives
        for i in range(len(gardes_chronologiques) - 1):
            jour1, heure1, shift1 = gardes_chronologiques[i]
            jour2, heure2, shift2 = gardes_chronologiques[i + 1]
            
            # Calculer l'intervalle en heures entre la fin de la première garde et le début de la suivante
            # Déterminer la durée de la première garde (8 heures standard)
            duree_garde = 8
            
            # Gérer le cas spécial de la garde de nuit qui chevauche minuit
            fin_premiere_garde = heure1 + duree_garde
            if shift1 == "22-06":
                fin_premiere_garde = (heure1 + duree_garde) % 24  # Pour gérer le passage à minuit
            
            # Calculer l'intervalle
            if jour1 == jour2:
                # Même jour
                if shift1 == "22-06" and heure2 < heure1:  # Si la première garde est de nuit et la seconde est le matin du jour suivant
                    intervalle = heure2 - fin_premiere_garde + 24
                else:
                    intervalle = heure2 - fin_premiere_garde
            else:
                # Jours différents
                jours_entre = jour2 - jour1
                if shift1 == "22-06":
                    # Si la première garde est de nuit, elle se termine le jour suivant
                    jours_entre -= 1
                
                intervalle = (jours_entre * 24) + (heure2 - fin_premiere_garde)
                if intervalle < 0:  # Correction pour les cas où la fin est avant le début (passage par minuit)
                    intervalle += 24
            
            # Vérifier si l'intervalle est suffisant
            if intervalle < self.repos_minimum_entre_gardes:
                return False
                
        return True

    def generer_planning(self):
        if not self.planning.travailleurs:
            messagebox.showerror("Erreur", "Veuillez ajouter au moins un travailleur")
            return
        
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
        
        # Utiliser le meilleur planning trouvé
        self.planning.planning = meilleur_planning
        
        self.creer_planning_visuel()
        messagebox.showinfo("Succès", f"Planning généré avec succès ({meilleure_evaluation} trous restants)")

    def compter_trous(self, planning):
        """Compte le nombre de trous dans un planning"""
        trous = 0
        for jour in Horaire.JOURS:
            for shift in Horaire.SHIFTS.values():
                if planning[jour][shift] is None:
                    trous += 1
        return trous

    def evaluer_planning(self, planning):
        """Évalue la qualité d'un planning en fonction de plusieurs critères"""
        # Copier le planning pour ne pas le modifier
        planning_copie = {j: {s: planning[j][s] for s in Horaire.SHIFTS.values()} for j in Horaire.JOURS}
        
        # Vérifier la répartition des gardes de nuit
        gardes_nuit_par_travailleur = {}
        for jour in Horaire.JOURS:
            travailleur = planning[jour]["22-06"]
            if travailleur:
                if travailleur not in gardes_nuit_par_travailleur:
                    gardes_nuit_par_travailleur[travailleur] = 0
                gardes_nuit_par_travailleur[travailleur] += 1
        
        return planning_copie

    def evaluer_repartition_nuit(self, planning):
        """Évalue la répartition des gardes de nuit entre les travailleurs"""
        # Compter les gardes de nuit par travailleur
        gardes_nuit_par_travailleur = {}
        for jour in Horaire.JOURS:
            travailleur = planning[jour]["22-06"]
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
        """Évalue le nombre de gardes rapprochées (8h d'écart) pour chaque travailleur"""
        # Mapping des shifts à des heures de début et de fin
        shift_heures = {
            "06-14": (6, 14),
            "14-22": (14, 22),
            "22-06": (22, 6)  # La fin est à 6h le jour suivant
        }
        
        # Créer une liste chronologique des gardes par travailleur
        gardes_par_travailleur = {}
        
        for i, jour in enumerate(Horaire.JOURS):
            for shift, (debut, fin) in shift_heures.items():
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
        """Génère des gardes de 12h en fonction des disponibilités des travailleurs"""
        if not self.planning.travailleurs:
            messagebox.showerror("Erreur", "Veuillez ajouter au moins un travailleur")
            return
        
        # Identifier les jours où des gardes de 12h peuvent être créées
        jours_avec_12h = set()
        for travailleur in self.planning.travailleurs:
            if hasattr(travailleur, 'disponibilites_12h'):
                for jour in travailleur.disponibilites_12h:
                    jours_avec_12h.add(jour)
        
        if not jours_avec_12h:
            messagebox.showinfo("Information", "Aucun travailleur n'a de disponibilités pour les gardes de 12h")
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
            messagebox.showinfo("Succès", f"{gardes_12h_creees} garde(s) de 12h créée(s) avec succès")
        else:
            messagebox.showinfo("Information", "Aucune garde de 12h n'a pu être créée. Vérifiez les disponibilités des travailleurs pour les gardes de 12h.")

    def combler_trous(self):
        """Comble les trous dans le planning en respectant les contraintes de repos
        et en tenant compte des disponibilités des travailleurs, mais pas du nombre de shifts souhaités"""
        # Créer une liste des trous à combler
        trous = []
        for jour in Horaire.JOURS:
            for shift in Horaire.SHIFTS.values():
                if self.planning.planning[jour][shift] is None:
                    trous.append((jour, shift))
        
        if not trous:
            messagebox.showinfo("Information", "Aucun trou à combler dans le planning")
            return
        
        # Trier les trous pour favoriser les possibilités de gardes de 12h
        # Priorité aux shifts qui peuvent former des gardes de 12h
        def priorite_shift(trou):
            jour, shift = trou
            # Donner une priorité plus élevée aux shifts qui peuvent former des gardes de 12h
            if shift == "22-06":  # Priorité maximale aux gardes de nuit
                return -1
            elif shift == "06-14":
                return 0
            elif shift == "14-22":
                return 1
            return 2
        
        trous.sort(key=priorite_shift)
        
        # Compter les gardes de nuit déjà assignées par travailleur
        gardes_nuit_par_travailleur = {}
        for jour in Horaire.JOURS:
            travailleur = self.planning.planning[jour]["22-06"]
            if travailleur:
                if travailleur not in gardes_nuit_par_travailleur:
                    gardes_nuit_par_travailleur[travailleur] = 0
                gardes_nuit_par_travailleur[travailleur] += 1
        
        # Combler les trous un par un
        trous_combles = 0
        for jour, shift in trous:
            travailleurs_disponibles = []
            
            # Vérifier chaque travailleur
            for travailleur in self.planning.travailleurs:
                # Vérifier si le travailleur est disponible pour ce jour et ce shift
                if jour not in travailleur.disponibilites or shift not in travailleur.disponibilites[jour]:
                    continue
                
                # Vérifier si le travailleur a des disponibilités pour les gardes de 12h
                a_dispo_12h = False
                if hasattr(travailleur, 'disponibilites_12h') and jour in travailleur.disponibilites_12h:
                    if (shift == "06-14" or shift == "14-22") and "matin_12h" in travailleur.disponibilites_12h[jour]:
                        a_dispo_12h = True
                    elif (shift == "14-22" or shift == "22-06") and "nuit_12h" in travailleur.disponibilites_12h[jour]:
                        a_dispo_12h = True
                
                # Créer une copie temporaire du planning pour tester
                planning_test = {j: {s: self.planning.planning[j][s] 
                                   for s in Horaire.SHIFTS.values()}
                               for j in Horaire.JOURS}
                
                planning_test[jour][shift] = travailleur.nom
                
                # Vérifier si cette affectation respecte les contraintes de repos
                if self.verifier_repos_entre_gardes(planning_test, travailleur):
                    # Nombre de gardes de nuit déjà assignées à ce travailleur
                    nb_nuits = gardes_nuit_par_travailleur.get(travailleur.nom, 0)
                    
                    # Calculer le nombre de gardes rapprochées que cette affectation créerait
                    nb_gardes_rapprochees = self.compter_gardes_rapprochees(planning_test, travailleur.nom)
                    
                    # Ajouter le travailleur avec ses priorités
                    travailleurs_disponibles.append((travailleur, a_dispo_12h, nb_nuits, nb_gardes_rapprochees))
            
            if travailleurs_disponibles:
                # Critères de tri différents selon le type de shift
                if shift == "22-06":  # Pour les gardes de nuit
                    # Trier par nombre de gardes de nuit (du moins au plus), puis par gardes rapprochées
                    travailleurs_disponibles.sort(key=lambda t: (t[2], t[3]))
                else:
                    # Trier d'abord par disponibilité 12h, puis par nombre de gardes rapprochées, puis par nombre de shifts total
                    travailleurs_disponibles.sort(key=lambda t: (
                        not t[1],  # False (pas de dispo 12h) vient après True (a dispo 12h)
                        t[3],      # Nombre de gardes rapprochées (du moins au plus)
                        sum(1 for j in Horaire.JOURS for s in Horaire.SHIFTS.values() 
                            if self.planning.planning[j][s] == t[0].nom)
                    ))
                
                # Choisir le travailleur avec la meilleure priorité
                travailleur_choisi = travailleurs_disponibles[0][0]
                self.planning.planning[jour][shift] = travailleur_choisi.nom
                
                # Mettre à jour le compteur de gardes de nuit si nécessaire
                if shift == "22-06":
                    if travailleur_choisi.nom not in gardes_nuit_par_travailleur:
                        gardes_nuit_par_travailleur[travailleur_choisi.nom] = 0
                    gardes_nuit_par_travailleur[travailleur_choisi.nom] += 1
                
                trous_combles += 1
        
        self.creer_planning_visuel()
        
        if trous_combles == len(trous):
            messagebox.showinfo("Succès", f"Tous les trous ont été comblés avec succès ({trous_combles} trous)")
        else:
            messagebox.showinfo("Information", f"{trous_combles} trous comblés sur {len(trous)}")

    def compter_gardes_rapprochees(self, planning, nom_travailleur):
        """Compte le nombre de gardes rapprochées pour un travailleur donné"""
        # Mapping des shifts à des heures de début et de fin
        shift_heures = {
            "06-14": (6, 14),
            "14-22": (14, 22),
            "22-06": (22, 6)  # La fin est à 6h le jour suivant
        }
        
        # Créer une liste chronologique des gardes du travailleur
        gardes = []
        
        for i, jour in enumerate(Horaire.JOURS):
            for shift, (debut, fin) in shift_heures.items():
                if planning[jour][shift] == nom_travailleur:
                    # Stocker (jour_index, heure_debut, heure_fin)
                    gardes.append((i, debut, fin))
        
        # Trier les gardes par jour puis par heure de début
        gardes.sort()
        
        # Compter les gardes rapprochées (moins de 16h entre la fin d'une garde et le début de la suivante)
        gardes_rapprochees = 0
        
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
                gardes_rapprochees += 1
        
        return gardes_rapprochees

    def charger_travailleurs_db(self):
        """Charge les travailleurs depuis la base de données"""
        db = Database()
        travailleurs = db.charger_travailleurs()
        for travailleur in travailleurs:
            self.planning.ajouter_travailleur(travailleur)
        self.mettre_a_jour_liste_travailleurs()

    def sauvegarder_planning(self):
        """Sauvegarde le planning actuel dans la base de données"""
        # Obtenir la date du prochain dimanche
        import datetime
        
        # Obtenir la date actuelle
        aujourd_hui = datetime.date.today()
        
        # Calculer le nombre de jours jusqu'au prochain dimanche
        # 6 = samedi (dernier jour de la semaine en Python où lundi=0, dimanche=6)
        # Donc (6 - jour_semaine) % 7 donne le nombre de jours jusqu'au dimanche
        jours_jusqu_a_dimanche = (6 - aujourd_hui.weekday()) % 7
        
        # Si aujourd'hui est dimanche, on prend le dimanche suivant
        if jours_jusqu_a_dimanche == 0:
            jours_jusqu_a_dimanche = 7
        
        # Obtenir la date du prochain dimanche
        prochain_dimanche = aujourd_hui + datetime.timedelta(days=jours_jusqu_a_dimanche)
        
        # Formater la date pour le nom du planning
        nom_planning = f"Planning semaine du {prochain_dimanche.strftime('%d/%m/%Y')}"
        
        # Demander confirmation à l'utilisateur
        confirmation = messagebox.askyesno(
            "Confirmation", 
            f"Voulez-vous sauvegarder ce planning pour la semaine commençant le {prochain_dimanche.strftime('%d/%m/%Y')} ?"
        )
        
        if confirmation:
            # Sauvegarder le planning avec le nom formaté
            planning_id = self.planning.sauvegarder(nom_planning)
            messagebox.showinfo("Succès", f"Planning sauvegardé pour la semaine du {prochain_dimanche.strftime('%d/%m/%Y')}")
            return planning_id
        return None

    def charger_planning(self):
        """Charge un planning depuis la base de données"""
        # Récupérer la liste des plannings disponibles
        plannings = self.planning.lister_plannings()
        
        if not plannings:
            messagebox.showinfo("Information", "Aucun planning sauvegardé")
            return
        
        # Créer une liste de choix avec les noms des plannings
        choix = []
        for p in plannings:
            date_str = p['date_creation'].split(' ')[0] if ' ' in p['date_creation'] else p['date_creation']
            choix.append(f"{p['id']} - {p['nom']} (créé le {date_str})")
        
        # Demander à l'utilisateur de choisir un planning
        choix_planning = simpledialog.askstring(
            "Charger un planning",
            "Choisissez un planning à charger (entrez le numéro):",
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
                
                messagebox.showinfo("Succès", "Planning chargé avec succès")
                
                # Proposer de télécharger le planning
                self.proposer_telechargement_planning()
            else:
                messagebox.showerror("Erreur", "Impossible de charger le planning")
        except ValueError:
            messagebox.showerror("Erreur", "Numéro de planning invalide")

    def proposer_telechargement_planning(self):
        """Propose à l'utilisateur de télécharger le planning au format CSV"""
        confirmation = messagebox.askyesno(
            "Téléchargement", 
            "Voulez-vous télécharger ce planning au format CSV ?"
        )
        
        if confirmation:
            self.telecharger_planning_csv()

    def telecharger_planning_csv(self):
        """Exporte le planning actuel au format CSV"""
        import csv
        from tkinter import filedialog
        
        # Demander à l'utilisateur où sauvegarder le fichier
        fichier = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Enregistrer le planning"
        )
        
        if not fichier:
            return
        
        try:
            with open(fichier, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Écrire l'en-tête
                en_tete = ["Jour"] + list(Horaire.SHIFTS.values())
                writer.writerow(en_tete)
                
                # Écrire les données du planning
                for jour in Horaire.JOURS:
                    ligne = [jour]
                    for shift in Horaire.SHIFTS.values():
                        travailleur = self.planning.planning[jour][shift]
                        ligne.append(travailleur if travailleur else "Non assigné")
                    writer.writerow(ligne)
                
            messagebox.showinfo("Succès", f"Planning exporté avec succès vers {fichier}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation: {str(e)}")

    def supprimer_travailleur(self):
        # Récupérer l'item sélectionné
        selection = self.table_travailleurs.selection()
        if not selection:
            messagebox.showinfo("Information", "Veuillez sélectionner un travailleur à supprimer")
            return
        
        # Récupérer le nom du travailleur sélectionné
        item = selection[0]
        nom_travailleur = self.table_travailleurs.item(item, "values")[0]
        
        # Demander confirmation
        confirmation = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer {nom_travailleur} ?")
        if not confirmation:
            return
        
        # Trouver et supprimer le travailleur
        for index, travailleur in enumerate(self.planning.travailleurs):
            if travailleur.nom == nom_travailleur:
                # Supprimer de la liste des travailleurs
                self.planning.travailleurs.pop(index)
                
                # Supprimer de la base de données
                db = Database()
                db.supprimer_travailleur(travailleur.nom)
                
                # Si le travailleur était en édition, annuler l'édition
                if self.mode_edition and self.travailleur_en_edition and self.travailleur_en_edition.nom == nom_travailleur:
                    self.annuler_edition()
                
                # Mettre à jour l'affichage
                self.mettre_a_jour_liste_travailleurs()
                messagebox.showinfo("Succès", f"Travailleur {nom_travailleur} supprimé avec succès")
                break

    def ouvrir_agenda_plannings(self):
        """Ouvre une fenêtre d'agenda pour visualiser et modifier les plannings existants"""
        # Récupérer tous les plannings
        plannings = self.planning.lister_plannings()
        
        if not plannings:
            messagebox.showinfo("Information", "Aucun planning sauvegardé")
            return
        
        # Créer une nouvelle fenêtre
        agenda_window = tk.Toplevel(self.root)
        agenda_window.title("Agenda des Plannings")
        agenda_window.geometry("900x600")
        agenda_window.configure(bg="#f0f0f0")
        
        # Créer un cadre pour l'agenda
        agenda_frame = ttk.Frame(agenda_window, padding=10)
        agenda_frame.pack(fill="both", expand=True)
        
        # Créer un Treeview pour afficher les plannings
        columns = ("id", "nom", "date_creation")
        agenda_tree = ttk.Treeview(agenda_frame, columns=columns, show="headings", height=20)
        
        # Configurer les en-têtes
        agenda_tree.heading("id", text="ID")
        agenda_tree.heading("nom", text="Nom du Planning")
        agenda_tree.heading("date_creation", text="Date de création")
        
        # Configurer les colonnes
        agenda_tree.column("id", width=50, anchor="center")
        agenda_tree.column("nom", width=300)
        agenda_tree.column("date_creation", width=150)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(agenda_frame, orient="vertical", command=agenda_tree.yview)
        agenda_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placer les widgets
        agenda_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configurer le redimensionnement
        agenda_frame.columnconfigure(0, weight=1)
        agenda_frame.rowconfigure(0, weight=1)
        
        # Remplir l'arbre avec les plannings
        for p in plannings:
            item_id = agenda_tree.insert("", "end", values=(
                p['id'], 
                p['nom'], 
                p['date_creation']
            ))
            
            # Stocker l'ID du planning dans l'item pour référence
            agenda_tree.item(item_id, tags=(str(p['id']),))
        
        # Cadre pour les boutons d'action
        action_frame = ttk.Frame(agenda_window, padding=10)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        # Fonction pour obtenir le planning sélectionné
        def get_selected_planning():
            selection = agenda_tree.selection()
            if not selection:
                messagebox.showwarning("Attention", "Veuillez sélectionner un planning")
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
                "Renommer le planning",
                "Entrez le nouveau nom du planning:",
                initialvalue=nom_actuel,
                parent=agenda_window
            )
            
            if nouveau_nom and nouveau_nom != nom_actuel:
                # Mettre à jour le nom dans la base de données
                db = Database()
                if db.modifier_nom_planning(planning_id, nouveau_nom):
                    # Mettre à jour l'affichage
                    values = list(agenda_tree.item(item, "values"))
                    values[1] = nouveau_nom
                    agenda_tree.item(item, values=values)
                    messagebox.showinfo("Succès", "Planning renommé avec succès")
                else:
                    messagebox.showerror("Erreur", "Impossible de renommer le planning")
        
        # Fonction pour supprimer un planning
        def supprimer_planning():
            result = get_selected_planning()
            if not result:
                return
            
            planning_id, item = result
            
            # Demander confirmation
            confirmation = messagebox.askyesno(
                "Confirmation",
                "Êtes-vous sûr de vouloir supprimer ce planning ?\nCette action est irréversible.",
                parent=agenda_window
            )
            
            if confirmation:
                # Supprimer le planning de la base de données
                db = Database()
                if db.supprimer_planning(planning_id):
                    # Supprimer l'item de l'arbre
                    agenda_tree.delete(item)
                    messagebox.showinfo("Succès", "Planning supprimé avec succès")
                else:
                    messagebox.showerror("Erreur", "Impossible de supprimer le planning")
        
        # Ajouter les boutons d'action
        btn_ouvrir = ttk.Button(action_frame, text="Ouvrir", command=ouvrir_planning_selectionne)
        btn_ouvrir.pack(side="left", padx=5)
        
        btn_renommer = ttk.Button(action_frame, text="Renommer", command=renommer_planning)
        btn_renommer.pack(side="left", padx=5)
        
        btn_supprimer = ttk.Button(action_frame, text="Supprimer", command=supprimer_planning)
        btn_supprimer.pack(side="left", padx=5)
        
        # Double-clic pour ouvrir un planning
        agenda_tree.bind("<Double-1>", lambda event: ouvrir_planning_selectionne())
        
        # Ajouter un bouton pour fermer l'agenda
        btn_fermer = ttk.Button(agenda_window, text="Fermer", command=agenda_window.destroy)
        btn_fermer.pack(pady=10)

    def ouvrir_planning_pour_modification(self, planning_id, parent_window=None):
        """Ouvre un planning existant pour modification avec le même style visuel que la page principale"""
        # Charger le planning depuis la base de données
        planning_charge = Planning.charger(planning_id)
        
        if not planning_charge:
            messagebox.showerror("Erreur", "Impossible de charger le planning")
            return
        
        # Récupérer les informations du planning
        db = Database()
        try:
            planning_info = db.obtenir_info_planning(planning_id)
            
            if not planning_info:
                messagebox.showerror("Erreur", "Impossible de récupérer les informations du planning")
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
            canvas_frame.pack(fill="both", expand=True, pady=10)
            
            # Canvas pour le planning
            canvas_width = 1000
            canvas_height = 550
            canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height, bg="white", highlightthickness=1, highlightbackground="#ddd")
            canvas.pack(fill="both", expand=True)
            
            # Définir les couleurs pour les différents shifts
            colors = {
                "06-14": "#a8e6cf",  # Vert clair pour le matin
                "14-22": "#ffcc5c",  # Jaune pour l'après-midi
                "22-06": "#b19cd9"   # Violet pour la nuit
            }
            
            # Dimensions des cellules
            cell_width = canvas_width / (len(Horaire.SHIFTS) + 1)
            cell_height = canvas_height / (len(Horaire.JOURS) + 1)
            
            # Dessiner les en-têtes de colonnes (shifts)
            canvas.create_rectangle(0, 0, cell_width, cell_height, fill="#f0f0f0", outline="#ccc")
            canvas.create_text(cell_width/2, cell_height/2, text="Jour", font=("Arial", 10, "bold"))
            
            for i, shift in enumerate(Horaire.SHIFTS.values()):
                x0 = cell_width * (i + 1)
                y0 = 0
                x1 = cell_width * (i + 2)
                y1 = cell_height
                canvas.create_rectangle(x0, y0, x1, y1, fill=colors[shift], outline="#ccc")
                canvas.create_text((x0 + x1)/2, (y0 + y1)/2, text=shift, font=("Arial", 10, "bold"))
            
            # Dessiner les en-têtes de lignes (jours)
            for i, jour in enumerate(Horaire.JOURS):
                x0 = 0
                y0 = cell_height * (i + 1)
                x1 = cell_width
                y1 = cell_height * (i + 2)
                canvas.create_rectangle(x0, y0, x1, y1, fill="#f0f0f0", outline="#ccc")
                canvas.create_text((x0 + x1)/2, (y0 + y1)/2, text=jour, font=("Arial", 10, "bold"))
            
            # Dessiner les cellules avec les assignations
            cellules = {}  # Pour stocker les références aux cellules pour modification ultérieure
            
            for i, jour in enumerate(Horaire.JOURS):
                cellules[jour] = {}
                for j, shift in enumerate(Horaire.SHIFTS.values()):
                    x0 = cell_width * (j + 1)
                    y0 = cell_height * (i + 1)
                    x1 = cell_width * (j + 2)
                    y1 = cell_height * (i + 2)
                    
                    # Récupérer le travailleur assigné
                    travailleur = planning_charge.planning[jour][shift]
                    
                    # Créer la cellule
                    rect_id = canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="#ccc")
                    text_id = canvas.create_text(
                        (x0 + x1)/2, (y0 + y1)/2, 
                        text=travailleur if travailleur else "Non assigné", 
                        width=cell_width*0.9,  # Limiter la largeur du texte
                        font=("Arial", 9)
                    )
                    
                    # Stocker les IDs pour pouvoir les modifier plus tard
                    cellules[jour][shift] = {
                        "rect": rect_id,
                        "text": text_id,
                        "travailleur": travailleur
                    }
                    
                    # Ajouter un gestionnaire de clic pour modifier l'assignation
                    canvas.tag_bind(rect_id, "<Button-1>", 
                                    lambda e, j=jour, s=shift: modifier_cellule(j, s))
                    canvas.tag_bind(text_id, "<Button-1>", 
                                    lambda e, j=jour, s=shift: modifier_cellule(j, s))
            
            # Fonction pour modifier une cellule
            def modifier_cellule(jour, shift):
                # Liste de tous les travailleurs + "Non assigné"
                travailleurs = [t.nom for t in planning_charge.travailleurs]
                travailleurs.append("Non assigné")
                
                # Obtenir une liste de tous les noms des travailleurs dans la base de données
                db = Database()
                tous_travailleurs = [t.nom for t in db.charger_travailleurs()]
                
                # Fusionner avec les travailleurs actuels et éliminer les doublons
                tous_noms = list(set(travailleurs + tous_travailleurs))
                tous_noms.sort()
                
                # Fenêtre de sélection pour choisir un travailleur
                selection_window = tk.Toplevel(planning_window)
                selection_window.title(f"Assigner un travailleur pour {jour} - {shift}")
                selection_window.geometry("300x400")
                selection_window.transient(planning_window)
                selection_window.grab_set()
                selection_window.focus_set()
                
                # Frame pour contenir la liste
                frame = ttk.Frame(selection_window, padding=10)
                frame.pack(fill="both", expand=True)
                
                # Label
                ttk.Label(frame, text=f"Choisir un travailleur pour\n{jour} - {shift}:", 
                         font=("Arial", 10, "bold")).pack(pady=10)
                
                # Listbox avec scrollbar
                list_frame = ttk.Frame(frame)
                list_frame.pack(fill="both", expand=True)
                
                scrollbar = ttk.Scrollbar(list_frame)
                scrollbar.pack(side="right", fill="y")
                
                listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 9))
                listbox.pack(side="left", fill="both", expand=True)
                
                scrollbar.config(command=listbox.yview)
                
                # Ajouter les options à la listbox
                for nom in tous_noms:
                    listbox.insert(tk.END, nom)
                
                # Ajouter "Non assigné" comme dernière option
                if "Non assigné" not in tous_noms:
                    listbox.insert(tk.END, "Non assigné")
                
                # Sélectionner le travailleur actuel
                actuel = cellules[jour][shift]["travailleur"]
                if actuel in tous_noms:
                    index = tous_noms.index(actuel)
                    listbox.selection_set(index)
                    listbox.see(index)
                elif actuel is None and "Non assigné" in tous_noms:
                    index = tous_noms.index("Non assigné")
                    listbox.selection_set(index)
                    listbox.see(index)
                
                # Fonction pour appliquer le choix
                def appliquer_choix():
                    selections = listbox.curselection()
                    if selections:
                        choix = listbox.get(selections[0])
                        if choix == "Non assigné":
                            planning_window.planning.planning[jour][shift] = None
                            cellules[jour][shift]["travailleur"] = None
                            canvas.itemconfig(cellules[jour][shift]["text"], text="Non assigné")
                        else:
                            planning_window.planning.planning[jour][shift] = choix
                            cellules[jour][shift]["travailleur"] = choix
                            canvas.itemconfig(cellules[jour][shift]["text"], text=choix)
                        selection_window.destroy()
                
                # Boutons
                btn_frame = ttk.Frame(frame)
                btn_frame.pack(fill="x", pady=10)
                
                ttk.Button(btn_frame, text="Valider", command=appliquer_choix).pack(side="left", padx=5, expand=True)
                ttk.Button(btn_frame, text="Annuler", command=selection_window.destroy).pack(side="right", padx=5, expand=True)
                
                # Double-clic pour sélectionner
                listbox.bind("<Double-1>", lambda e: appliquer_choix())
            
            # Fonction pour sauvegarder le planning modifié
            def sauvegarder_planning_modifie():
                if db.mettre_a_jour_planning(planning_id, planning_window.planning):
                    messagebox.showinfo("Succès", "Planning mis à jour avec succès")
                    # Fermer la fenêtre d'édition
                    planning_window.destroy()
                    # Rafraîchir l'agenda si nécessaire
                    if parent_window:
                        parent_window.destroy()
                        self.ouvrir_agenda_plannings()
                else:
                    messagebox.showerror("Erreur", "Impossible de mettre à jour le planning")
            
            # Fonctions pour exporter le planning
            def exporter_planning():
                self.telecharger_planning_csv(planning_window.planning)
            
            # Frame pour les boutons en bas
            button_frame = ttk.Frame(planning_window, padding=10)
            button_frame.pack(fill="x", side="bottom")
            
            # Boutons
            ttk.Button(button_frame, text="Sauvegarder", command=sauvegarder_planning_modifie).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Exporter en CSV", command=exporter_planning).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Fermer sans sauvegarder", command=planning_window.destroy).pack(side="right", padx=5)
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")

    def telecharger_planning_csv(self, planning_to_export=None):
        """Exporte le planning actuel ou spécifié au format CSV"""
        import csv
        from tkinter import filedialog
        
        # Utiliser le planning spécifié ou le planning actuel
        planning_a_exporter = planning_to_export if planning_to_export else self.planning
        
        # Demander à l'utilisateur où sauvegarder le fichier
        fichier = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Enregistrer le planning"
        )
        
        if not fichier:
            return
        
        try:
            with open(fichier, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Écrire l'en-tête
                en_tete = ["Jour"] + list(Horaire.SHIFTS.values())
                writer.writerow(en_tete)
                
                # Écrire les données du planning
                for jour in Horaire.JOURS:
                    ligne = [jour]
                    for shift in Horaire.SHIFTS.values():
                        travailleur = planning_a_exporter.planning[jour][shift]
                        ligne.append(travailleur if travailleur else "Non assigné")
                    writer.writerow(ligne)
                
            messagebox.showinfo("Succès", f"Planning exporté avec succès vers {fichier}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation: {str(e)}")

    def run(self):
        self.root.mainloop() 
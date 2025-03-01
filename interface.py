import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
import random
from horaire import Horaire
from travailleur import Travailleur
from planning import Planning
from database import Database

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
        style.configure("TButton", font=self.normal_font)
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
        
        # Boutons pour générer le planning
        btn_generer = ttk.Button(frame_generation, text="Générer Planning", 
                  command=self.generer_planning)
        btn_generer.grid(row=0, column=0, padx=5, sticky="ew")
        
        btn_generer_12h = ttk.Button(frame_generation, text="Suggestion 12h", 
                  command=self.generer_planning_12h)
        btn_generer_12h.grid(row=0, column=1, padx=5, sticky="ew")
        
        btn_combler = ttk.Button(frame_generation, text="Combler les trous", 
                  command=self.combler_trous)
        btn_combler.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Frame pour la sauvegarde et le chargement
        frame_db = ttk.Frame(left_frame)
        frame_db.grid(row=4, column=0, sticky="ew", pady=10)
        frame_db.columnconfigure(0, weight=1)
        frame_db.columnconfigure(1, weight=1)
        
        btn_sauvegarder = ttk.Button(frame_db, text="Sauvegarder Planning", 
                  command=self.sauvegarder_planning)
        btn_sauvegarder.grid(row=0, column=0, padx=5, sticky="ew")
        
        btn_charger = ttk.Button(frame_db, text="Charger Planning", 
                  command=self.charger_planning)
        btn_charger.grid(row=0, column=1, padx=5, sticky="ew")
        
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

    def creer_formulaire_travailleur(self, frame):
        # Frame pour le formulaire d'ajout de travailleur
        form_frame = ttk.LabelFrame(frame, text="Ajouter un travailleur", padding=10)
        form_frame.grid(row=0, column=0, sticky="nsew")
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(0, weight=0)  # Info frame
        form_frame.rowconfigure(1, weight=1)  # Dispo frame
        form_frame.rowconfigure(2, weight=0)  # Boutons
        
        # Nom et nombre de shifts
        info_frame = ttk.Frame(form_frame)
        info_frame.grid(row=0, column=0, sticky="ew", pady=5)
        info_frame.columnconfigure(0, weight=0)
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(2, weight=0)
        info_frame.columnconfigure(3, weight=0)
        
        ttk.Label(info_frame, text="Nom:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.nom_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(info_frame, text="Nombre de shifts souhaités:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.nb_shifts_var, width=5).grid(row=0, column=3, padx=5, pady=5)
        
        # Disponibilités
        dispo_frame = ttk.LabelFrame(form_frame, text="Disponibilités", padding=10)
        dispo_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # Configurer les colonnes pour qu'elles s'adaptent
        for i in range(6):  # 1 pour le jour + 3 pour les shifts + 2 pour les 12h
            dispo_frame.columnconfigure(i, weight=1)
        
        # En-têtes des colonnes
        ttk.Label(dispo_frame, text="Jour", font=self.header_font).grid(row=0, column=0, padx=5, pady=5)
        col = 1
        for shift in Horaire.SHIFTS.values():
            ttk.Label(dispo_frame, text=shift, font=self.header_font).grid(row=0, column=col, padx=5, pady=5)
            col += 1
        
        # Ajouter les colonnes pour les gardes de 12h
        ttk.Label(dispo_frame, text="Matin 12h\n(06-18)", font=self.header_font).grid(row=0, column=col, padx=5, pady=5)
        col += 1
        ttk.Label(dispo_frame, text="Nuit 12h\n(18-06)", font=self.header_font).grid(row=0, column=col, padx=5, pady=5)
        
        # Lignes pour chaque jour
        for i, jour in enumerate(Horaire.JOURS, 1):
            ttk.Label(dispo_frame, text=jour).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            col = 1
            for shift in Horaire.SHIFTS.values():
                ttk.Checkbutton(dispo_frame, variable=self.disponibilites[jour][shift]).grid(row=i, column=col, padx=5, pady=2)
                col += 1
            
            # Ajouter les cases à cocher pour les gardes de 12h
            ttk.Checkbutton(dispo_frame, variable=self.disponibilites_12h[jour]["matin_12h"]).grid(row=i, column=col, padx=5, pady=2)
            col += 1
            ttk.Checkbutton(dispo_frame, variable=self.disponibilites_12h[jour]["nuit_12h"]).grid(row=i, column=col, padx=5, pady=2)
        
        # Boutons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        self.btn_ajouter = ttk.Button(btn_frame, text="Ajouter Travailleur", command=self.ajouter_travailleur)
        self.btn_ajouter.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.btn_annuler = ttk.Button(btn_frame, text="Annuler", command=self.annuler_edition, state=tk.DISABLED)
        self.btn_annuler.grid(row=0, column=1, padx=5, sticky="ew")

    def creer_liste_travailleurs(self, frame):
        # Liste des travailleurs
        frame_liste = ttk.LabelFrame(frame, text="Travailleurs enregistrés", padding=10)
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
        
        btn_supprimer = ttk.Button(btn_frame, text="Supprimer", command=self.supprimer_travailleur)
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
        # Récupérer l'item sélectionné
        selection = self.table_travailleurs.selection()
        if not selection:
            return
        
        # Récupérer l'index du travailleur sélectionné
        item = selection[0]
        nom_travailleur = self.table_travailleurs.item(item, "values")[0]
        
        # Trouver le travailleur correspondant
        for index, travailleur in enumerate(self.planning.travailleurs):
            if travailleur.nom == nom_travailleur:
                # Passer en mode édition
                self.mode_edition = True
                self.travailleur_en_edition = travailleur
                
                # Remplir le formulaire avec les données du travailleur
                self.nom_var.set(travailleur.nom)
                self.nb_shifts_var.set(str(travailleur.nb_shifts_souhaites))
                
                # Réinitialiser toutes les cases à cocher
                for jour in Horaire.JOURS:
                    for shift in Horaire.SHIFTS.values():
                        self.disponibilites[jour][shift].set(False)
                    self.disponibilites_12h[jour]["matin_12h"].set(False)
                    self.disponibilites_12h[jour]["nuit_12h"].set(False)
                
                # Cocher les cases correspondant aux disponibilités
                for jour, shifts in travailleur.disponibilites.items():
                    for shift in shifts:
                        self.disponibilites[jour][shift].set(True)
                
                # Cocher les cases correspondant aux disponibilités de 12h
                if hasattr(travailleur, 'disponibilites_12h'):
                    for jour, shifts_12h in travailleur.disponibilites_12h.items():
                        for shift_12h in shifts_12h:
                            self.disponibilites_12h[jour][shift_12h].set(True)
                
                # Mettre à jour les boutons
                self.btn_ajouter.config(text="Modifier Travailleur")
                self.btn_annuler.config(state=tk.NORMAL)
                break

    def annuler_edition(self):
        self.mode_edition = False
        self.travailleur_en_edition = None
        self.btn_ajouter.config(text="Ajouter Travailleur")
        self.btn_annuler.config(state=tk.DISABLED)
        self.reinitialiser_formulaire()

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
            
        self.planning.generer_planning(mode_12h=False)
        self.creer_planning_visuel()
        messagebox.showinfo("Succès", "Planning généré avec succès")

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
        
        # Mélanger la liste des trous pour éviter les biais
        random.shuffle(trous)
        
        # Combler les trous un par un
        trous_combles = 0
        for jour, shift in trous:
            travailleurs_disponibles = []
            
            # Vérifier chaque travailleur
            for travailleur in self.planning.travailleurs:
                # Vérifier si le travailleur est disponible pour ce jour et ce shift
                if jour not in travailleur.disponibilites or shift not in travailleur.disponibilites[jour]:
                    continue
                
                # Créer une copie temporaire du planning pour tester
                planning_test = {j: {s: self.planning.planning[j][s] 
                                   for s in Horaire.SHIFTS.values()}
                               for j in Horaire.JOURS}
                
                planning_test[jour][shift] = travailleur.nom
                
                # Vérifier si cette affectation respecte les contraintes de repos
                if self.verifier_repos_entre_gardes(planning_test, travailleur):
                    travailleurs_disponibles.append(travailleur)
            
            if travailleurs_disponibles:
                # Trier les travailleurs par nombre de shifts déjà assignés (du moins au plus)
                travailleurs_disponibles.sort(key=lambda t: sum(
                    1 for j in Horaire.JOURS for s in Horaire.SHIFTS.values() 
                    if self.planning.planning[j][s] == t.nom
                ))
                
                # Choisir le travailleur avec le moins de shifts assignés
                travailleur_choisi = travailleurs_disponibles[0]
                self.planning.planning[jour][shift] = travailleur_choisi.nom
                trous_combles += 1
        
        self.creer_planning_visuel()
        
        if trous_combles == len(trous):
            messagebox.showinfo("Succès", f"Tous les trous ont été comblés avec succès ({trous_combles} trous)")
        else:
            messagebox.showinfo("Information", f"{trous_combles} trous comblés sur {len(trous)}")

    def charger_travailleurs_db(self):
        """Charge les travailleurs depuis la base de données"""
        db = Database()
        travailleurs = db.charger_travailleurs()
        for travailleur in travailleurs:
            self.planning.ajouter_travailleur(travailleur)
        self.mettre_a_jour_liste_travailleurs()

    def sauvegarder_planning(self):
        """Sauvegarde le planning actuel dans la base de données"""
        if not self.planning.travailleurs:
            messagebox.showerror("Erreur", "Aucun travailleur n'est enregistré")
            return
        
        # Demander un nom pour le planning
        nom = simpledialog.askstring("Nom du planning", "Entrez un nom pour ce planning:")
        if nom:
            planning_id = self.planning.sauvegarder(nom)
            messagebox.showinfo("Succès", f"Planning '{nom}' sauvegardé avec succès")

    def charger_planning(self):
        """Charge un planning depuis la base de données"""
        # Récupérer la liste des plannings
        plannings = Planning.lister_plannings()
        if not plannings:
            messagebox.showinfo("Information", "Aucun planning n'est enregistré")
            return
        
        # Créer une fenêtre de dialogue pour choisir un planning
        dialog = tk.Toplevel(self.root)
        dialog.title("Charger un planning")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Liste des plannings
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Sélectionnez un planning à charger:", font=self.header_font).pack(pady=10)
        
        # Créer un Treeview pour afficher les plannings
        columns = ("id", "date", "nom")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("id", text="ID")
        tree.heading("date", text="Date de création")
        tree.heading("nom", text="Nom")
        
        tree.column("id", width=50)
        tree.column("date", width=150)
        tree.column("nom", width=250)
        
        for planning in plannings:
            tree.insert("", "end", values=(planning["id"], planning["date_creation"], planning["nom"]))
        
        tree.pack(fill="both", expand=True, pady=10)
        
        # Boutons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        selected_id = [None]  # Variable pour stocker l'ID sélectionné
        
        def on_select(event):
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                selected_id[0] = item["values"][0]
        
        def on_load():
            if selected_id[0]:
                dialog.destroy()
                planning = Planning.charger(selected_id[0])
                if planning:
                    self.planning = planning
                    self.creer_planning_visuel()
                    self.mettre_a_jour_liste_travailleurs()
                    messagebox.showinfo("Succès", "Planning chargé avec succès")
        
        def on_cancel():
            dialog.destroy()
        
        tree.bind("<<TreeviewSelect>>", on_select)
        
        ttk.Button(btn_frame, text="Charger", command=on_load).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Attendre que la fenêtre soit fermée
        self.root.wait_window(dialog)

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

    def run(self):
        self.root.mainloop() 
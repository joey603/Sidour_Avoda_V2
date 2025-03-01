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
        
        # Titre
        titre_label = ttk.Label(left_frame, text="Gestion des Travailleurs", font=self.title_font)
        titre_label.pack(pady=(0, 20))
        
        # Frame pour l'ajout de travailleur
        frame_ajout = ttk.LabelFrame(left_frame, text="Ajouter/Modifier un travailleur", padding=10)
        frame_ajout.pack(padx=10, pady=5, fill="x")

        # Nom du travailleur
        ttk.Label(frame_ajout, text="Nom:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_ajout, textvariable=self.nom_var, width=25).grid(row=0, column=1, padx=5, pady=5)

        # Nombre de shifts souhaités
        ttk.Label(frame_ajout, text="Nombre de shifts souhaités:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_ajout, textvariable=self.nb_shifts_var, width=25).grid(row=1, column=1, padx=5, pady=5)

        # Tableau des disponibilités
        frame_dispo = ttk.LabelFrame(left_frame, text="Disponibilités", padding=10)
        frame_dispo.pack(padx=10, pady=10, fill="both", expand=True)

        # En-têtes des colonnes
        ttk.Label(frame_dispo, text="Jour", font=self.header_font).grid(row=0, column=0, padx=5, pady=5)
        for i, shift in enumerate(Horaire.SHIFTS.values()):
            ttk.Label(frame_dispo, text=shift, font=self.header_font).grid(row=0, column=i+1, padx=5, pady=5)

        # Cases à cocher pour chaque jour et shift
        for i, jour in enumerate(Horaire.JOURS):
            ttk.Label(frame_dispo, text=jour.capitalize()).grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
            for j, shift in enumerate(Horaire.SHIFTS.values()):
                ttk.Checkbutton(frame_dispo, variable=self.disponibilites[jour][shift]
                    ).grid(row=i+1, column=j+1, padx=5, pady=5)

        # Boutons d'action pour le formulaire
        frame_boutons = ttk.Frame(left_frame)
        frame_boutons.pack(pady=10)
        
        self.btn_ajouter = ttk.Button(frame_boutons, text="Ajouter Travailleur", 
                  command=self.ajouter_travailleur, width=20)
        self.btn_ajouter.pack(side=tk.LEFT, padx=5)
        
        self.btn_annuler = ttk.Button(frame_boutons, text="Annuler", 
                  command=self.annuler_edition, width=20, state=tk.DISABLED)
        self.btn_annuler.pack(side=tk.LEFT, padx=5)
        
        # Liste des travailleurs
        frame_liste = ttk.LabelFrame(left_frame, text="Travailleurs enregistrés", padding=10)
        frame_liste.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Scrollbar pour la liste
        scrollbar = ttk.Scrollbar(frame_liste)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Liste des travailleurs
        self.liste_travailleurs = tk.Listbox(frame_liste, yscrollcommand=scrollbar.set, 
                                           font=self.normal_font, height=6)
        self.liste_travailleurs.pack(fill="both", expand=True)
        scrollbar.config(command=self.liste_travailleurs.yview)
        
        # Lier la sélection dans la liste à l'édition
        self.liste_travailleurs.bind('<<ListboxSelect>>', self.selectionner_travailleur)
        
        # Frame pour les boutons de génération
        frame_generation = ttk.Frame(left_frame)
        frame_generation.pack(pady=10)
        
        # Boutons pour générer le planning
        btn_generer = ttk.Button(frame_generation, text="Générer Planning", 
                  command=self.generer_planning, width=20)
        btn_generer.pack(side=tk.LEFT, padx=5)
        
        btn_generer_12h = ttk.Button(frame_generation, text="Suggestion 12h", 
                  command=self.generer_planning_12h, width=20)
        btn_generer_12h.pack(side=tk.LEFT, padx=5)
        
        btn_combler = ttk.Button(frame_generation, text="Combler les trous", 
                  command=self.combler_trous, width=20)
        btn_combler.pack(side=tk.LEFT, padx=5)
        
        # Frame pour la sauvegarde et le chargement
        frame_db = ttk.Frame(left_frame)
        frame_db.pack(pady=10)
        
        btn_sauvegarder = ttk.Button(frame_db, text="Sauvegarder Planning", 
                  command=self.sauvegarder_planning, width=20)
        btn_sauvegarder.pack(side=tk.LEFT, padx=5)
        
        btn_charger = ttk.Button(frame_db, text="Charger Planning", 
                  command=self.charger_planning, width=20)
        btn_charger.pack(side=tk.LEFT, padx=5)
        
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
        for jour in Horaire.JOURS:
            shifts_dispo = []
            for shift in Horaire.SHIFTS.values():
                if self.disponibilites[jour][shift].get():
                    shifts_dispo.append(shift)
            if shifts_dispo:  # Ajouter seulement si au moins un shift est disponible
                disponibilites[jour] = shifts_dispo
        
        if not disponibilites:
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

    def mettre_a_jour_liste_travailleurs(self):
        # Vider la liste
        self.liste_travailleurs.delete(0, tk.END)
        
        # Remplir avec les travailleurs actuels
        for travailleur in self.planning.travailleurs:
            self.liste_travailleurs.insert(tk.END, travailleur.nom)

    def selectionner_travailleur(self, event):
        # Récupérer l'index sélectionné
        selection = self.liste_travailleurs.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.planning.travailleurs):
            travailleur = self.planning.travailleurs[index]
            
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
            
            # Cocher les cases correspondant aux disponibilités
            for jour, shifts in travailleur.disponibilites.items():
                for shift in shifts:
                    self.disponibilites[jour][shift].set(True)
            
            # Mettre à jour les boutons
            self.btn_ajouter.config(text="Modifier Travailleur")
            self.btn_annuler.config(state=tk.NORMAL)

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
        if not self.planning.travailleurs:
            messagebox.showerror("Erreur", "Veuillez ajouter au moins un travailleur")
            return
            
        self.planning.generer_planning(mode_12h=True)
        self.creer_planning_visuel()
        messagebox.showinfo("Succès", "Planning avec gardes de 12h généré avec succès")

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

    def run(self):
        self.root.mainloop() 
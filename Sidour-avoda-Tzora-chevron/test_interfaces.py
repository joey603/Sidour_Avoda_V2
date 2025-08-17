#!/usr/bin/env python3
"""
Script de test pour comparer les interfaces Sidour Avoda
Permet de choisir entre l'interface originale et l'interface modernisée
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

def launch_original_interface():
    """Lance l'interface originale"""
    try:
        from interface import InterfacePlanning
        app = InterfacePlanning(repos_minimum_entre_gardes=8)
        app.root.title("Sidour Avoda - Interface Originale")
        app.run()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du lancement de l'interface originale:\n{str(e)}")

def launch_modern_interface():
    """Lance l'interface modernisée"""
    try:
        from interface_2 import InterfacePlanning
        app = InterfacePlanning(repos_minimum_entre_gardes=8)
        app.root.title("Sidour Avoda Pro - Interface Modernisée")
        app.run()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du lancement de l'interface modernisée:\n{str(e)}")

def create_test_window():
    """Crée la fenêtre de sélection d'interface"""
    root = tk.Tk()
    root.title("Sidour Avoda - Sélecteur d'Interface")
    root.geometry("500x300")
    root.resizable(False, False)
    
    # Centrer la fenêtre
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    # Style moderne
    style = ttk.Style()
    style.theme_use('clam')
    
    # Frame principal
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)
    
    # Titre
    title_label = ttk.Label(main_frame, text="Sidour Avoda", 
                           font=("Helvetica", 18, "bold"))
    title_label.pack(pady=(0, 10))
    
    subtitle_label = ttk.Label(main_frame, text="Sélecteur d'Interface", 
                              font=("Helvetica", 12))
    subtitle_label.pack(pady=(0, 30))
    
    # Description
    desc_frame = ttk.LabelFrame(main_frame, text="Choisissez votre interface", padding=15)
    desc_frame.pack(fill="x", pady=(0, 20))
    
    ttk.Label(desc_frame, text="• Interface Originale : Design classique Tkinter", 
              font=("Helvetica", 10)).pack(anchor="w", pady=2)
    ttk.Label(desc_frame, text="• Interface Modernisée : Design Bootstrap avec ttkbootstrap", 
              font=("Helvetica", 10)).pack(anchor="w", pady=2)
    
    # Boutons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)
    
    # Bouton interface originale
    btn_original = ttk.Button(button_frame, text="🎨 Interface Originale", 
                             command=lambda: [root.destroy(), launch_original_interface()],
                             style="TButton")
    btn_original.pack(side="left", padx=10)
    
    # Bouton interface modernisée
    btn_modern = ttk.Button(button_frame, text="✨ Interface Modernisée", 
                           command=lambda: [root.destroy(), launch_modern_interface()],
                           style="TButton")
    btn_modern.pack(side="left", padx=10)
    
    # Bouton quitter
    btn_quit = ttk.Button(main_frame, text="❌ Quitter", 
                         command=root.destroy)
    btn_quit.pack(pady=(20, 0))
    
    # Informations
    info_label = ttk.Label(main_frame, text="💡 Les deux interfaces ont les mêmes fonctionnalités", 
                          font=("Helvetica", 9), foreground="gray")
    info_label.pack(pady=(10, 0))
    
    return root

def main():
    """Fonction principale"""
    try:
        # Vérifier que les modules sont disponibles
        try:
            import interface
        except ImportError:
            messagebox.showerror("Erreur", "Module 'interface' non trouvé")
            return
        
        try:
            import interface_2
        except ImportError:
            messagebox.showerror("Erreur", "Module 'interface_2' non trouvé")
            return
        
        # Créer et lancer la fenêtre de sélection
        root = create_test_window()
        root.mainloop()
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        messagebox.showerror("Erreur", f"Erreur lors du lancement:\n{str(e)}")

if __name__ == "__main__":
    main()

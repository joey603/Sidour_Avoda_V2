from interface import InterfacePlanning

def main():
    # Création de l'interface avec 8 heures de repos minimum entre les gardes
    app = InterfacePlanning(repos_minimum_entre_gardes=8)
    app.run()

if __name__ == "__main__":
    main() 
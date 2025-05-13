import os
from dotenv import load_dotenv
load_dotenv()

import getpass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from gestion_emplacements.models import UtilisateurDB, Base 

DB_USER = os.environ.get('DB_USER', 'Pierrick')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'entrepot_db')
if not DB_PASSWORD:
    raise ValueError("La variable d'environnement DB_PASSWORD est manquante (vérifiez .env)!")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fonctions de gestion des utilisateurs ---

def lister_utilisateurs(db_session):
    """Affiche tous les utilisateurs."""
    print("\n--- Liste des Utilisateurs ---")
    utilisateurs = db_session.query(UtilisateurDB).order_by(UtilisateurDB.nom_utilisateur).all()
    if not utilisateurs:
        print("Aucun utilisateur trouvé.")
        return
    for u in utilisateurs:
        print(f"ID: {u.id}, Nom d'utilisateur: {u.nom_utilisateur}, Rôle: {u.role or 'N/A'}")
    print("----------------------------")

def ajouter_utilisateur(db_session):
    """Ajoute un nouvel utilisateur."""
    print("\n--- Ajout d'un Nouvel Utilisateur ---")
    nom_utilisateur = input("Nom d'utilisateur : ").strip()
    if not nom_utilisateur:
        print("Le nom d'utilisateur ne peut pas être vide.")
        return

    utilisateur_existant = db_session.query(UtilisateurDB).filter_by(nom_utilisateur=nom_utilisateur).first()
    if utilisateur_existant:
        print(f"L'utilisateur '{nom_utilisateur}' existe déjà.")
        return

    while True:
        mot_de_passe = getpass.getpass("Mot de passe : ")
        mot_de_passe_confirm = getpass.getpass("Confirmez le mot de passe : ")
        if mot_de_passe == mot_de_passe_confirm:
            if not mot_de_passe:
                print("Le mot de passe ne peut pas être vide.")
            else:
                break
        else:
            print("Les mots de passe ne correspondent pas. Réessayez.")
    
    role = input(f"Rôle (optionnel, ex: 'admin', 'utilisateur', laisser vide pour 'utilisateur' par défaut) : ").strip() or "utilisateur"
    
    nouvel_utilisateur = UtilisateurDB(
        nom_utilisateur=nom_utilisateur,
        role=role
    )
    nouvel_utilisateur.set_mot_de_passe(mot_de_passe)

    try:
        db_session.add(nouvel_utilisateur)
        db_session.commit()
        print(f"Utilisateur '{nom_utilisateur}' créé avec succès !")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Erreur lors de la création de l'utilisateur : {e}")

def supprimer_utilisateur(db_session):
    """Supprime un utilisateur existant."""
    print("\n--- Suppression d'un Utilisateur ---")
    nom_utilisateur = input("Nom d'utilisateur à supprimer : ").strip()
    if not nom_utilisateur:
        print("Nom d'utilisateur non fourni.")
        return

    utilisateur = db_session.query(UtilisateurDB).filter_by(nom_utilisateur=nom_utilisateur).first()
    if not utilisateur:
        print(f"L'utilisateur '{nom_utilisateur}' n'a pas été trouvé.")
        return

    confirmation = input(f"Êtes-vous sûr de vouloir supprimer l'utilisateur '{nom_utilisateur}' (ID: {utilisateur.id}) ? (oui/non) : ").strip().lower()
    if confirmation == 'oui':
        try:
            db_session.delete(utilisateur)
            db_session.commit()
            print(f"Utilisateur '{nom_utilisateur}' supprimé avec succès.")
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Erreur lors de la suppression de l'utilisateur : {e}")
    else:
        print("Suppression annulée.")

def modifier_mot_de_passe(db_session):
    """Modifie le mot de passe d'un utilisateur existant."""
    print("\n--- Modification du Mot de Passe ---")
    nom_utilisateur = input("Nom d'utilisateur dont le mot de passe doit être modifié : ").strip()
    if not nom_utilisateur:
        print("Nom d'utilisateur non fourni.")
        return

    utilisateur = db_session.query(UtilisateurDB).filter_by(nom_utilisateur=nom_utilisateur).first()
    if not utilisateur:
        print(f"L'utilisateur '{nom_utilisateur}' n'a pas été trouvé.")
        return

    while True:
        nouveau_mot_de_passe = getpass.getpass(f"Nouveau mot de passe pour '{nom_utilisateur}' : ")
        nouveau_mot_de_passe_confirm = getpass.getpass("Confirmez le nouveau mot de passe : ")
        if nouveau_mot_de_passe == nouveau_mot_de_passe_confirm:
            if not nouveau_mot_de_passe:
                print("Le nouveau mot de passe ne peut pas être vide.")
            else:
                break
        else:
            print("Les mots de passe ne correspondent pas. Réessayez.")
            
    try:
        utilisateur.set_mot_de_passe(nouveau_mot_de_passe)
        db_session.commit()
        print(f"Le mot de passe pour l'utilisateur '{nom_utilisateur}' a été modifié avec succès.")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Erreur lors de la modification du mot de passe : {e}")

# --- Menu Principal du Script ---
def menu_principal():
    db_session = SessionLocal()
    try:
        while True:
            print("\n--- Gestion des Utilisateurs ---")
            print("1. Ajouter un utilisateur")
            print("2. Lister les utilisateurs")
            print("3. Modifier le mot de passe d'un utilisateur")
            print("4. Supprimer un utilisateur")
            print("5. Quitter")
            choix = input("Votre choix : ").strip()

            if choix == '1':
                ajouter_utilisateur(db_session)
            elif choix == '2':
                lister_utilisateurs(db_session)
            elif choix == '3':
                modifier_mot_de_passe(db_session)
            elif choix == '4':
                supprimer_utilisateur(db_session)
            elif choix == '5':
                print("Fin du script.")
                break
            else:
                print("Choix invalide, veuillez réessayer.")
    finally:
        db_session.close()

if __name__ == "__main__":
    menu_principal()

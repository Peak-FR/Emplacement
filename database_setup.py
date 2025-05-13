import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from gestion_emplacements.models import Base
from gestion_emplacements.entrepot import Entrepot

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

def initialiser_base_de_donnees_et_peupler():
    print(f"Connexion à la base de données via: {engine.url}")
    try:
        print("Tentative de création des tables (si elles n'existent pas)...")
        Base.metadata.create_all(bind=engine)
        print("Tables vérifiées/créées avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création des tables : {e}")
        return

    db_session = SessionLocal()
    
    mon_entrepot = Entrepot()
    try:
        print("Tentative d'initialisation de la structure de l'entrepôt en base de données...")
        mon_entrepot.initialiser_entrepot_en_base_de_donnees(db_session)
        print("Processus d'initialisation de l'entrepôt terminé.")

    except Exception as e:
        print(f"Une erreur s'est produite lors du peuplement de l'entrepôt : {e}")
    finally:
        db_session.close(
        print("Session de base de données fermée.")

# --- Exécution du script ---
if __name__ == '__main__':
    print("Démarrage du script de configuration de la base de données...")
    initialiser_base_de_donnees_et_peupler()
    print("Script de configuration de la base de données terminé.")

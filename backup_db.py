import os
import subprocess
import datetime
from dotenv import load_dotenv
import shlex

load_dotenv()

print("Lecture des paramètres de connexion BDD depuis l'environnement...")

db_name = os.environ.get('DB_NAME', 'entrepot_db') 
db_user = os.environ.get('DB_USER', 'Pierrick')    
db_password = os.environ.get('DB_PASSWORD')      
db_host = os.environ.get('DB_HOST', 'localhost') 
db_port = os.environ.get('DB_PORT', '5432') 


if not db_password:
    raise ValueError("La variable d'environnement DB_PASSWORD est manquante ! Vérifiez le fichier .env.")


# Définir le chemin de sauvegarde...
backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
os.makedirs(backup_dir, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_filename = f"{db_name}_backup_{timestamp}.dump"
backup_filepath = os.path.join(backup_dir, backup_filename)

# Construire la commande pg_dump en utilisant les variables lues
pg_dump_executable = '/Applications/Postgres.app/Contents/Versions/17/bin/pg_dump'
pg_dump_cmd = [
    pg_dump_executable,
    '-h', db_host,
    '-p', db_port,
    '-U', db_user,
    '-d', db_name,
    '-F', 'c',
    '-f', backup_filepath
]

env_with_password = os.environ.copy()
env_with_password['PGPASSWORD'] = db_password

print(f"\nLancement de la sauvegarde vers : {backup_filepath}")
print(f"Commande exécutée (simplifié): pg_dump -h {db_host} ... -d {db_name} -f {backup_filepath}")

try:
    result = subprocess.run(pg_dump_cmd, capture_output=True, text=True, check=True, env=env_with_password)
    print("Sauvegarde terminée avec succès !")
    if result.stdout:
        print("Sortie standard:")
        print(result.stdout)



except subprocess.CalledProcessError as e:
    print(f"ERREUR lors de l'exécution de pg_dump (code retour: {e.returncode}) :")
    print("Erreur standard:")
    print(e.stderr)
except FileNotFoundError:
     print("ERREUR: La commande 'pg_dump' n'a pas été trouvée. Assurez-vous que les outils client PostgreSQL sont installés et dans le PATH système.")
except Exception as e:
    print(f"Une erreur inattendue est survenue : {e}")

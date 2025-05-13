# Emplacement
Module de gestion des emplacements


# EmplacELFR - Gestionnaire d'emplacements d'Entrepôt

## Description

EmplacELFR est une application web développée avec Flask et Python pour la gestion des emplacements et des produits dans un entrepôt. Elle permet de visualiser le plan de l'entrepôt, d'assigner des produits à des emplacements, de rechercher des emplacements libres ou des produits spécifiques, de consulter l'historique des mouvements et d'obtenir des statistiques sur l'occupation.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :

* Python (version 3.8+ recommandée)
* pip (gestionnaire de paquets Python)
* Git (pour cloner le projet si hébergé sur un dépôt)
* PostgreSQL (serveur de base de données)

## Installation et Configuration

Suivez ces étapes pour configurer l'application en local ou sur un serveur de développement/test :

1.  **Cloner le Dépôt (si applicable) :**
    Si le code est sur un dépôt Git, clonez-le :
    ```bash
    git clone [URL_DE_VOTRE_DEPOT_GIT]
    cd EmplacELFR 
    ```
    Sinon, copiez les fichiers du projet dans un dossier local.

2.  **Créer un Environnement Virtuel :**
    Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet.
    ```bash
    python3 -m venv venv 
    source venv/bin/activate  # Sur macOS/Linux
    # venv\Scripts\activate    # Sur Windows
    ```

3.  **Installer les Dépendances :**
    Installez toutes les bibliothèques Python nécessaires listées dans `requirements.txt` :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurer la Base de Données PostgreSQL :**
    * Assurez-vous que votre serveur PostgreSQL est en cours d'exécution.
    * Créez une base de données pour l'application (par exemple, `entrepot_db`).
    * Créez un utilisateur PostgreSQL (par exemple, `Pierrick`) et accordez-lui les droits nécessaires sur cette base de données.
        ```sql
        -- Exemple de commandes SQL (à exécuter en tant que superutilisateur PostgreSQL)
        -- CREATE USER Pierrick WITH PASSWORD 'AZERTY';
        -- CREATE DATABASE entrepot_db OWNER Pierrick;
        -- GRANT ALL PRIVILEGES ON DATABASE entrepot_db TO Pierrick;
        ```

5.  **Configurer les Variables d'Environnement :**
    * Copiez le fichier `.env.example` (si vous en créez un) en `.env` :
        ```bash
        cp .env.example .env 
        ```
        (Si vous n'avez pas de `.env.example`, créez directement le fichier `.env`)
    * Modifiez le fichier `.env` à la racine du projet avec vos propres informations :
        ```dotenv
        # Contenu du fichier .env
        SECRET_KEY='VOTRE_CLE_SECRETE_FORTE_ET_ALEATOIRE_ICI' # Générez-en une (ex: python -c "import secrets; print(secrets.token_hex(32))")
        
        DB_NAME='entrepot_db'
        DB_USER='Pierrick'
        DB_PASSWORD='AZERTY' # Votre mot de passe BDD
        DB_HOST='localhost'
        DB_PORT='5432'
        
        # Optionnel si app.py utilise directement les variables ci-dessus pour construire l'URL
        # DATABASE_URL='postgresql://Pierrick:AZERTY@localhost:5432/entrepot_db'
        
        FLASK_APP='app.py'
        FLASK_ENV='development' # Mettre 'production' pour le déploiement
        ```

6.  **Initialiser la Base de Données (Schéma et Structure) :**
    Exécutez le script pour créer les tables et la structure de base de l'entrepôt :
    ```bash
    python database_setup.py
    ```
    Vérifiez les messages dans la console pour vous assurer que tout s'est bien passé.

7.  **Créer un Premier Utilisateur (Admin) :**
    Exécutez le script de gestion des utilisateurs pour créer au moins un compte (par exemple, un compte admin) :
    ```bash
    python admin_users.py
    ```
    Suivez les instructions pour ajouter un utilisateur.

## Lancer l'Application

1.  **En Mode Développement :**
    Une fois l'environnement virtuel activé et les variables d'environnement configurées (via `.env` et `load_dotenv()` dans `app.py`), vous pouvez lancer le serveur de développement Flask :
    ```bash
    flask run 
    ```
    Ou si vous avez `host='0.0.0.0'` dans `app.py` :
    ```bash
    python app.py
    ```
    L'application devrait être accessible à `http://127.0.0.1:5001` (ou le port que vous avez configuré).

2.  **En Mode Production :**
    Pour un déploiement en production, n'utilisez PAS le serveur de développement Flask. Utilisez un serveur WSGI robuste comme Gunicorn derrière un reverse proxy (Nginx ou Apache).
    * Assurez-vous que `FLASK_ENV=production` dans votre `.env` sur le serveur.
    * Exemple de commande Gunicorn (à adapter) :
        ```bash
        gunicorn --workers 4 --bind 0.0.0.0:8000 app:app 
        ```
        (Le `0.0.0.0:8000` est l'endroit où Gunicorn écoute ; Nginx/Apache redirigerait ensuite le trafic public vers ce port).

## Scripts Utilitaires

* `database_setup.py` : Initialise le schéma de la base de données et la structure de base de l'entrepôt. À lancer une fois lors de la configuration initiale.
* `admin_users.py` : Permet de gérer les utilisateurs de l'application (ajouter, lister, modifier mot de passe, supprimer) en ligne de commande.
* `backup_db.py` : Script pour effectuer des sauvegardes de la base de données PostgreSQL en utilisant `pg_dump`.
    * **Sauvegarde :** `python backup_db.py` (crée un fichier `.dump` dans le dossier `backups/`).
    * **Restauration (exemple) :** `pg_restore -h localhost -U VOTRE_USER -d VOTRE_BASE_CIBLE backups/NOM_DU_FICHIER.dump` (la base cible doit exister et être vide de préférence).

## Structure du Projet (Aperçu)

EmplacELFR/
├── .env                 # (Local, NON VERSIONNÉ) Variables d'environnement
├── .env.example         # (Versionné) Exemple de fichier .env
├── .gitignore           # Fichiers/dossiers à ignorer par Git
├── app.py               # Application Flask principale, routes API
├── admin_users.py       # Script de gestion des utilisateurs
├── backup_db.py         # Script de sauvegarde de la BDD
├── database_setup.py    # Script d'initialisation de la BDD
├── requirements.txt     # Dépendances Python
├── static/              # Fichiers statiques (CSS, JS client, images)
│   ├── style.css
│   ├── script.js
│   └── images/
│       └── ...
├── templates/           # Templates HTML (Flask)
│   ├── index.html
│   └── login.html
├── gestion_emplacements/ # Module pour la logique métier et les modèles BDD
│   ├── __init__.py
│   ├── entrepot.py      # Classe Entrepot (logique métier)
│   └── models.py        # Modèles SQLAlchemy (schéma BDD)
└── backups/             # (NON VERSIONNÉ) Dossier pour les sauvegardes locales de la BDD


## Notes de Déploiement

* **Serveur WSGI :** Utilisez Gunicorn ou uWSGI.
* **Reverse Proxy :** Nginx ou Apache est recommandé pour servir les fichiers statiques, gérer HTTPS, et transférer les requêtes à Gunicorn.
* **Variables d'Environnement :** Configurez `SECRET_KEY`, `DATABASE_URL` (ou les variables DB individuelles), et `FLASK_ENV='production'` directement sur le serveur de production (pas via un fichier `.env` versionné).
* **Base de Données :** Utilisez une instance PostgreSQL robuste, idéalement avec des sauvegardes automatisées gérées par votre hébergeur ou via des scripts `cron` utilisant `backup_db.py`.
* **Fichiers Statiques :** En production, Nginx/Apache devrait servir directement le dossier `static/` pour de meilleures performances.

---

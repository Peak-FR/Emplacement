import os
from dotenv import load_dotenv 
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, g
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from functools import wraps


from gestion_emplacements.entrepot import Entrepot
from gestion_emplacements.models import EmplacementDB, UtilisateurDB, AlleeDB, Base


load_dotenv()
loaded = load_dotenv()
print(f"Fichier .env chargé: {loaded}")


app = Flask(__name__)

# --- CONFIGURATION SÉCURISÉE ---
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("La variable d'environnement SECRET_KEY n'est pas définie!")
app.secret_key = SECRET_KEY

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie!")


try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"ERREUR: Impossible de créer l'engine SQLAlchemy ou la session factory. Vérifiez DATABASE_URL.")
    print(f"Erreur détaillée: {e}")  
    exit()

mon_entrepot = Entrepot()


def login_requis(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'utilisateur_connecte' not in session:
            if request.accept_mimetypes.accept_json and \
               not request.accept_mimetypes.accept_html:
                return jsonify({"erreur": "Accès non autorisé. Veuillez vous connecter."}), 401
            else:
                return redirect(url_for('page_de_connexion', next=request.url))
        g.utilisateur_nom = session.get('utilisateur_connecte')
        g.utilisateur_id = session.get('utilisateur_id')
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES D'AUTHENTIFICATION ---
@app.route('/connexion')
def page_de_connexion():
    if 'utilisateur_connecte' in session:
        return redirect(url_for('interface_principale'))
    return render_template('login.html')

@app.route('/api/auth/login', methods=['POST'])
def login_api():
    donnees = request.get_json()
    if not donnees or not donnees.get('nom_utilisateur') or not donnees.get('mot_de_passe'):
        return jsonify({"erreur": "Nom d'utilisateur et mot de passe requis."}), 400

    nom_utilisateur = donnees.get('nom_utilisateur')
    mot_de_passe = donnees.get('mot_de_passe')

    db_session = SessionLocal()
    try:
        utilisateur = db_session.query(UtilisateurDB).filter_by(nom_utilisateur=nom_utilisateur).first()
        if utilisateur and utilisateur.verifier_mot_de_passe(mot_de_passe) and utilisateur.est_actif:
            session.clear()
            session['utilisateur_connecte'] = utilisateur.nom_utilisateur
            session['utilisateur_id'] = utilisateur.id
            print(f"Utilisateur '{utilisateur.nom_utilisateur}' connecté.")
            return jsonify({"message": "Connexion réussie.", "utilisateur": utilisateur.nom_utilisateur}), 200
        elif utilisateur and not utilisateur.est_actif:
             print(f"Tentative de connexion pour l'utilisateur inactif '{nom_utilisateur}'.")
             return jsonify({"erreur": "Ce compte utilisateur est désactivé."}), 403
        else:
            print(f"Échec de connexion pour '{nom_utilisateur}'.")
            return jsonify({"erreur": "Nom d'utilisateur ou mot de passe incorrect."}), 401
    except Exception as e:
        print(f"Erreur serveur pendant le login: {e}")
        db_session.rollback()
        return jsonify({"erreur": "Erreur interne du serveur lors de la connexion."}), 500
    finally:
        db_session.close()

@app.route('/api/auth/logout', methods=['POST'])
@login_requis
def logout_api():
    utilisateur_deconnecte = session.pop('utilisateur_connecte', None)
    session.pop('utilisateur_id', None)
    session.clear()
    print(f"Utilisateur '{utilisateur_deconnecte}' déconnecté.")
    return jsonify({"message": "Déconnexion réussie."}), 200

@app.route('/api/auth/status', methods=['GET'])
def status_api():
    if 'utilisateur_connecte' in session:
        return jsonify({
            "connecte": True,
            "utilisateur": session['utilisateur_connecte'],
            }), 200
    else:
        return jsonify({"connecte": False}), 200


# --- ROUTES POUR L'INTERFACE UTILISATEUR (FRONTEND) ---
@app.route('/')
@login_requis
def interface_principale():
    return render_template('index.html', nom_utilisateur=session.get('utilisateur_connecte'))


# --- ROUTES API POUR LA GESTION DE L'ENTREPÔT (PROTÉGÉES) ---
@app.route('/api/emplacements/<string:id_emplacement_str>', methods=['GET'])
@login_requis
def get_emplacement(id_emplacement_str: str):
    db_session = SessionLocal()
    try:
        emplacement_db = mon_entrepot.get_emplacement_par_id_complet(db_session, id_emplacement_str)
        if emplacement_db:
            return jsonify({
                "id_emplacement_str": emplacement_db.id_emplacement_str,
                "taille": emplacement_db.taille,
                "allee_lettre": emplacement_db.allee_lettre,
                "rack_numero": emplacement_db.rack_numero,
                "niveau": emplacement_db.niveau,
                "position_dans_niveau": emplacement_db.position_dans_niveau,
                "est_libre": emplacement_db.est_libre,
                "produit_id": emplacement_db.produit_id,
                "produit_nom": emplacement_db.produit_nom
            }), 200
        else:
            return jsonify({"erreur": "Emplacement non trouvé"}), 404
    except Exception as e:
        print(f"Erreur API get_emplacement: {e}")
        return jsonify({"erreur": f"Erreur interne du serveur."}), 500
    finally:
        db_session.close()

@app.route('/api/emplacements/optimal-libre', methods=['GET'])
@login_requis
def get_optimal_libre_emplacement():
    taille_recherchee = request.args.get('taille')
    exclure_J_str = request.args.get('exclure_allee_J', 'true').lower()
    exclure_allee_J = exclure_J_str == 'true'
    seulement_J_str = request.args.get('chercher_seulement_allee_J', 'false').lower()
    chercher_uniquement_allee_J = seulement_J_str == 'true'
    eparpillement_str = request.args.get('eparpillage_total', 'false').lower()
    mode_eparpillage_total = eparpillement_str == 'true'

    if not taille_recherchee:
        return jsonify({"erreur": "Le paramètre 'taille' est manquant et obligatoire."}), 400

    db_session = SessionLocal()
    try:
        emplacement_optimal_db = mon_entrepot.trouver_emplacement_libre_optimal(
            session=db_session,
            taille_recherchee=taille_recherchee,
            exclure_allee_J_par_defaut=exclure_allee_J,
            chercher_uniquement_allee_J=chercher_uniquement_allee_J,
            mode_eparpillage_total=mode_eparpillage_total
        )
        if emplacement_optimal_db:
            return jsonify({
                "id_emplacement_str": emplacement_optimal_db.id_emplacement_str,
                "taille": emplacement_optimal_db.taille,
                "allee_lettre": emplacement_optimal_db.allee_lettre,
                "rack_numero": emplacement_optimal_db.rack_numero,
                "niveau": emplacement_optimal_db.niveau,
                "position_dans_niveau": emplacement_optimal_db.position_dans_niveau,
                "est_libre": emplacement_optimal_db.est_libre
            }), 200
        else:
            message_erreur = f"Aucun emplacement libre trouvé pour la taille '{taille_recherchee}'"
            return jsonify({"message": message_erreur}), 404
    except ValueError as ve:
        return jsonify({"erreur": f"Valeur de paramètre invalide: {str(ve)}"}), 400
    except Exception as e:
        print(f"Erreur API get_optimal_libre_emplacement: {e}")
        return jsonify({"erreur": f"Erreur interne du serveur."}), 500
    finally:
        db_session.close()

@app.route('/api/emplacements/<string:id_emplacement_str>/assigner', methods=['POST'])
@login_requis
def assigner_produit_api(id_emplacement_str: str):
    donnees_requete = request.get_json()
    if not donnees_requete:
        return jsonify({"erreur": "Aucune donnée JSON fournie."}), 400

    nom_produit = donnees_requete.get('nom_produit')
    id_produit = donnees_requete.get('id_produit')
    if not nom_produit or not id_produit:
        return jsonify({"erreur": "Les champs 'nom_produit' et 'id_produit' sont obligatoires."}), 400

    utilisateur_actuel = g.utilisateur_nom

    db_session = SessionLocal()
    try:
        success, message, emplacement_modifie = mon_entrepot.assigner_produit_a_emplacement(
            session=db_session,
            id_emplacement_str=id_emplacement_str,
            nom_produit=nom_produit,
            id_produit=id_produit,
            nom_utilisateur_actionneur=utilisateur_actuel
        )
        if success:
            db_session.commit()
            return jsonify({
                "message": message,
                "emplacement": {
                    "id_emplacement_str": emplacement_modifie.id_emplacement_str,
                    "est_libre": emplacement_modifie.est_libre,
                    "produit_nom": emplacement_modifie.produit_nom,
                    "produit_id": emplacement_modifie.produit_id
                }
            }), 200
        else:
            db_session.rollback()
            status_code = 409
            if "non trouvé" in message.lower():
                status_code = 404
            elif "déjà présent dans cet emplacement" in message.lower():
                status_code = 200
            elif "existe déjà à l'emplacement" in message.lower():
                status_code = 409
            elif "déjà occupé par" in message.lower():
                status_code = 409
            return jsonify({"erreur": message}), status_code
    except Exception as e:
        db_session.rollback()
        print(f"Erreur API assigner_produit_api: {e}")
        return jsonify({"erreur": f"Erreur interne du serveur lors de l'assignation."}), 500
    finally:
        db_session.close()


@app.route('/api/emplacements/<string:id_emplacement_str>/liberer', methods=['POST'])
@login_requis
def liberer_emplacement_api_route(id_emplacement_str: str):
    utilisateur_actuel = g.utilisateur_nom

    db_session = SessionLocal()
    try:
        success, message, emplacement_modifie = mon_entrepot.liberer_emplacement_par_id(
            session=db_session,
            id_emplacement_str=id_emplacement_str,
            nom_utilisateur_actionneur=utilisateur_actuel
        )
        if success:
            db_session.commit()
            return jsonify({
                "message": message,
                "emplacement": {
                    "id_emplacement_str": emplacement_modifie.id_emplacement_str,
                    "est_libre": emplacement_modifie.est_libre,
                    "produit_nom": emplacement_modifie.produit_nom,
                    "produit_id": emplacement_modifie.produit_id
                }
            }), 200
        else:
            db_session.rollback()
            status_code = 409
            if "non trouvé" in message.lower():
                status_code = 404
            elif "déjà libre" in message.lower():
                 status_code = 200
            return jsonify({"erreur": message}), status_code
    except Exception as e:
        db_session.rollback()
        print(f"Erreur API liberer_emplacement_api_route: {e}")
        return jsonify({"erreur": f"Erreur interne du serveur lors de la libération."}), 500
    finally:
        db_session.close()

@app.route('/api/emplacements/liberer-en-masse', methods=['POST'])
@login_requis
def liberer_emplacements_en_masse_api():
    donnees_requete = request.get_json()
    ids_emplacements_a_liberer = donnees_requete.get('ids_emplacements')

    if not ids_emplacements_a_liberer or not isinstance(ids_emplacements_a_liberer, list):
        return jsonify({"erreur": "Le champ 'ids_emplacements' est manquant ou n'est pas une liste."}), 400
    if not all(isinstance(item, str) for item in ids_emplacements_a_liberer):
         return jsonify({"erreur": "La liste 'ids_emplacements' doit contenir uniquement des chaînes de caractères."}), 400

    utilisateur_actuel = g.utilisateur_nom

    db_session = SessionLocal()
    try:
        resultats = mon_entrepot.liberer_emplacements_en_masse(
            session=db_session,
            liste_id_emplacement_str=ids_emplacements_a_liberer,
            nom_utilisateur_actionneur=utilisateur_actuel
        )
        return jsonify({
            "message": "Opération de libération en masse traitée.",
            "details": resultats
        }), 200
    except Exception as e:
        db_session.rollback()
        print(f"Erreur API liberer_emplacements_en_masse_api: {e}")
        return jsonify({"erreur": f"Erreur interne du serveur lors de la libération en masse."}), 500
    finally:
        db_session.close()


@app.route('/api/emplacements/assigner-en-masse', methods=['POST'])
@login_requis
def assigner_produits_en_masse_api():
    donnees_requete = request.get_json()
    produits_a_assigner = donnees_requete.get('produits_a_assigner')
    if not produits_a_assigner or not isinstance(produits_a_assigner, list):
         return jsonify({"erreur": "Le champ 'produits_a_assigner' est manquant ou n'est pas une liste."}), 400

    exclure_J_global = donnees_requete.get('exclure_allee_J', True)
    mode_eparpillage_total_global = donnees_requete.get('mode_eparpillage_total_global', False)
    utilisateur_actuel = g.utilisateur_nom

    db_session = SessionLocal()
    try:
        resultats = mon_entrepot.assigner_produits_en_masse(
            session=db_session,
            produits_a_assigner=produits_a_assigner,
            exclure_allee_J_global=exclure_J_global,
            mode_eparpillage_total_global=mode_eparpillage_total_global,
            nom_utilisateur_actionneur=utilisateur_actuel
        )
        return jsonify({
            "message": "Opération d'assignation en masse traitée.",
            "details_assignations": resultats
        }), 200
    except Exception as e:
        db_session.rollback()
        print(f"Erreur API assigner_produits_en_masse_api: {e}")
        return jsonify({"erreur": f"Erreur interne du serveur lors de l'assignation en masse."}), 500
    finally:
        db_session.close()

@app.route('/api/allees/<string:lettre_allee>/details', methods=['GET'])
@login_requis
def get_details_allee_api(lettre_allee):
    db_session = SessionLocal()
    try:
        details_allee = mon_entrepot.get_allee_details_complete(db_session, lettre_allee)
        if details_allee:
            return jsonify(details_allee), 200
        else:
            return jsonify({"erreur": f"L'allée '{lettre_allee}' n'a pas été trouvée."}), 404
    except Exception as e:
        print(f"Erreur API get_details_allee_api pour {lettre_allee}: {e}")
        return jsonify({"erreur": f"Erreur interne du serveur."}), 500
    finally:
        db_session.close()

@app.route('/api/allees', methods=['GET'])
@login_requis
def get_toutes_les_allees_api():
    db_session = SessionLocal()
    try:
        allees_result = db_session.query(AlleeDB.lettre_allee).order_by(AlleeDB.lettre_allee).all()
        lettres_allees = [a[0] for a in allees_result]
        return jsonify({"allees": lettres_allees}), 200
    except Exception as e:
         print(f"Erreur API get_toutes_les_allees_api: {e}")
         return jsonify({"erreur": f"Erreur interne du serveur."}), 500
    finally:
        db_session.close()

@app.route('/api/produits/rechercher', methods=['GET'])
@login_requis
def rechercher_produit_api():
    terme_recherche = request.args.get('q', None)

    if not terme_recherche or len(terme_recherche) < 2:
        return jsonify({"erreur": "Veuillez fournir un terme de recherche d'au moins 2 caractères."}), 400

    db_session = SessionLocal()
    try:
        emplacements_avec_produit = mon_entrepot.rechercher_produit(db_session, terme_recherche)

        resultats = []
        for emp in emplacements_avec_produit:
            resultats.append({
                "id_emplacement_str": emp.id_emplacement_str,
                "produit_nom": emp.produit_nom,
                "produit_id": emp.produit_id,
                "taille": emp.taille,
                "allee_lettre": emp.allee_lettre,
                "rack_numero": emp.rack_numero,
                "niveau": emp.niveau,
                "position_dans_niveau": emp.position_dans_niveau
            })
        return jsonify(resultats), 200
    except Exception as e:
        print(f"Erreur API rechercher_produit_api: {e}")
        return jsonify({"erreur": "Erreur interne du serveur lors de la recherche."}), 500
    finally:
        db_session.close()

@app.route('/api/entrepot/statistiques', methods=['GET'])
@login_requis
def get_statistiques_entrepot_api():
    db_session = SessionLocal()
    try:
        statistiques = mon_entrepot.get_statistiques_entrepot(db_session)
        if "erreur" in statistiques:
             return jsonify(statistiques), 500
        return jsonify(statistiques), 200
    except Exception as e:
        print(f"Erreur API get_statistiques_entrepot_api: {e}")
        return jsonify({"erreur": "Erreur interne du serveur lors du calcul des statistiques."}), 500
    finally:
        db_session.close()

@app.route('/api/historique', methods=['GET'])
@login_requis
def get_historique_api():
    try:
        page = request.args.get('page', 1, type=int)
        par_page = request.args.get('par_page', 15, type=int)
        type_action = request.args.get('type_action', None, type=str)
        id_emplacement = request.args.get('id_emplacement', None, type=str)
        id_produit = request.args.get('id_produit', None, type=str)

        if page < 1: page = 1
        if par_page < 1: par_page = 15
        if par_page > 100: par_page = 100

        db_session = SessionLocal()
        try:
            historique_data = mon_entrepot.get_historique_mouvements(
                session=db_session,
                page=page,
                elements_par_page=par_page,
                type_action_filtre=type_action,
                id_emplacement_filtre=id_emplacement,
                id_produit_filtre=id_produit
            )
            return jsonify(historique_data), 200
        except Exception as e_inner:
            print(f"Erreur interne lors de la récupération de l'historique : {e_inner}")
            return jsonify({"erreur": "Erreur serveur lors de la récupération de l'historique."}), 500
        finally:
            db_session.close()

    except ValueError:
        return jsonify({"erreur": "Paramètres de page ou par_page invalides."}), 400
    except Exception as e_outer:
        print(f"Erreur API get_historique_api: {e_outer}")
        return jsonify({"erreur": "Erreur interne du serveur."}), 500


# --- Lancement de l'application Flask (pour le développement) ---
if __name__ == '__main__':
    print("-----------------------------------------------------")
    print("Démarrage du serveur Flask de développement...")
    print(f"SECRET_KEY chargée: {'Oui' if SECRET_KEY else 'NON (ERREUR!)'}")
    print(f"DATABASE_URL chargée: {'Oui' if DATABASE_URL else 'NON (ERREUR!)'}")
    print("Accédez à l'application via http://127.0.0.1:5001 (ou votre IP locale)")
    print("-----------------------------------------------------")
    app.run(debug=True, host='0.0.0.0', port=5001)

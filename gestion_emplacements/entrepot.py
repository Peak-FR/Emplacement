# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session, aliased
from sqlalchemy import case, func , or_, desc
from .models import AlleeDB, RackDB, EmplacementDB, HistoriqueMouvementDB

class Entrepot:
    def __init__(self):
        """
        L'entrepot n'a plus besoin de stocker les allees en memoire ici,
        car il operera directement sur la base de donnees via des sessions.
        """
        pass

    def _creer_ou_recuperer_allee(self, session: Session, lettre_allee: str) -> AlleeDB:
        allee_db = session.query(AlleeDB).filter_by(lettre_allee=lettre_allee).first()
        if not allee_db:
            allee_db = AlleeDB(lettre_allee=lettre_allee)
            session.add(allee_db)
        return allee_db

    def initialiser_entrepot_en_base_de_donnees(self, session: Session):
        premiere_allee_attendue = "A"
        if session.query(AlleeDB).filter_by(lettre_allee=premiere_allee_attendue).first() and \
           session.query(RackDB).filter_by(id_rack_complet_str=f"{premiere_allee_attendue}1").first():
            print("L'entrepot semble deja initialise en base de donnees. Initialisation ignoree.")
            return
        print("Initialisation de la structure de l'entrepot en base de donnees...")
        configurations_allees = [
            {"lettre": "A", "racks": [
                {"numeros_debut": 1, "numeros_fin": 24, "niveaux": 10, "empl_par_niveau": 5, "taille_specifique": "Grand"},
                {"numeros_debut": 25, "numeros_fin": 30, "niveaux": 10, "empl_par_niveau": 5, "taille_specifique": "Petit"}
            ]},
            *[{"lettre": l, "racks": [{"numeros_debut": 1, "numeros_fin": 29, "niveaux": 10, "empl_par_niveau": 3, "taille_specifique": "Moyen"}]}
              for l in ["B", "C", "D", "E", "G", "H", "I"]],
            {"lettre": "F", "racks": [{"numeros_debut": 1, "numeros_fin": 27, "niveaux": 10, "empl_par_niveau": 3, "taille_specifique": "Moyen"}]},
            {"lettre": "J", "racks": [{"numeros_debut": 1, "numeros_fin": 7, "niveaux": 10, "empl_par_niveau": 3, "taille_specifique": "Moyen"}]}
        ]
        try:
            for config_allee_data in configurations_allees:
                lettre_allee_principale = config_allee_data["lettre"]
                allee_db_obj = self._creer_ou_recuperer_allee(session, lettre_allee_principale)
                for rack_cfg_detail in config_allee_data["racks"]:
                    taille_effective = rack_cfg_detail["taille_specifique"]
                    for rack_num_detail in range(rack_cfg_detail["numeros_debut"], rack_cfg_detail["numeros_fin"] + 1):
                        rack_id_str_detail = f"{lettre_allee_principale}{rack_num_detail}"
                        if session.query(RackDB).filter_by(id_rack_complet_str=rack_id_str_detail).first():
                            continue
                        nouveau_rack_db = RackDB(id_rack_complet_str=rack_id_str_detail, allee_lettre=lettre_allee_principale, numero_rack=rack_num_detail, nombre_niveaux=rack_cfg_detail["niveaux"], emplacements_par_niveau=rack_cfg_detail["empl_par_niveau"], taille_emplacements_par_defaut=taille_effective, allee=allee_db_obj)
                        session.add(nouveau_rack_db)
                        for niv_detail in range(1, rack_cfg_detail["niveaux"] + 1):
                            for pos_detail in range(1, rack_cfg_detail["empl_par_niveau"] + 1):
                                emp_id_str_detail = f"{rack_id_str_detail}-{niv_detail}-{pos_detail}"
                                if session.query(EmplacementDB).filter_by(id_emplacement_str=emp_id_str_detail).first():
                                    continue
                                emp_db_detail = EmplacementDB(id_emplacement_str=emp_id_str_detail, taille=taille_effective, allee_lettre=lettre_allee_principale, rack_numero=rack_num_detail, niveau=niv_detail, position_dans_niveau=pos_detail, rack=nouveau_rack_db)
                                session.add(emp_db_detail)
            session.commit()
            print("Entrepot initialise et sauvegarde en base de donnees.")
        except Exception as e:
            session.rollback()
            print(f"Erreur lors de l'initialisation de l'entrepot en BDD : {e}")
            raise


    def get_emplacement_par_id_complet(self, session: Session, id_emplacement_str: str) -> EmplacementDB | None:
        """
        Recupere un objet EmplacementDB specifique a partir de son ID complet
        en interrogeant la base de donnees.
        'session' est une instance de Session SQLAlchemy active.
        """
        try:
            emplacement = session.query(EmplacementDB).filter_by(id_emplacement_str=id_emplacement_str).first()
            return emplacement
        except Exception as e:
            print(f"Erreur lors de la récupération de l'emplacement '{id_emplacement_str}': {e}")
            return None

    def trouver_emplacement_libre_optimal(self, session: Session, taille_recherchee: str,
                                          exclure_allee_J_par_defaut: bool = True,
                                          chercher_uniquement_allee_J: bool = False,
                                          ids_emplacements_a_exclure: list = None,
                                          mode_eparpillage_total: bool = False
                                          ) -> EmplacementDB | None:
        try:
            query = session.query(EmplacementDB)
            query = query.filter(EmplacementDB.est_libre == True)
            query = query.filter(EmplacementDB.taille == taille_recherchee)

            case_priorite_niveau = case(
                (EmplacementDB.niveau <= 7, 0), else_=1 # 0 pour niveaux 1-7, 1 pour 8-10
            )

            if ids_emplacements_a_exclure:
                query = query.filter(EmplacementDB.id_emplacement_str.notin_(ids_emplacements_a_exclure))

            if chercher_uniquement_allee_J:
                print("INFO: Recherche uniquement en Allee J (avec priorite niveaux hauts).")
                query = query.filter(EmplacementDB.allee_lettre == 'J')
                query = query.order_by(
                    case_priorite_niveau, EmplacementDB.niveau,
                    EmplacementDB.rack_numero, EmplacementDB.position_dans_niveau,
                    func.random()
                )
            elif mode_eparpillage_total:
                print("INFO: Recherche en mode eparpillement total (avec priorite niveaux hauts).")
                if exclure_allee_J_par_defaut:
                    query = query.filter(EmplacementDB.allee_lettre != 'J')
                # D'abord les niveaux 1-7 au hasard, puis les niveaux 8-10 au hasard
                query = query.order_by(case_priorite_niveau, EmplacementDB.niveau, func.random())
            else:
                print("INFO: Recherche avec priorisation standard (avec priorite niveaux hauts).")
                if exclure_allee_J_par_defaut:
                    query = query.filter(EmplacementDB.allee_lettre != 'J')

                ordre_allees_preferees = ["A", "B", "C", "D", "E", "G", "H", "I", "F"]
                case_ordre_allees_conditions = {lettre: index for index, lettre in enumerate(ordre_allees_preferees)}
                if not exclure_allee_J_par_defaut and 'J' not in ordre_allees_preferees:
                    case_ordre_allees_conditions['J'] = len(ordre_allees_preferees)
                case_ordre_allees = case(case_ordre_allees_conditions, value=EmplacementDB.allee_lettre, else_=len(ordre_allees_preferees) + 1 )

                query = query.order_by(
                    case_priorite_niveau,             # 1. Groupe de priorite de niveau (0 pour 1-7, 1 pour 8-10)
                    EmplacementDB.niveau,             # 2. Numero de niveau exact (1, 2, ...)
                    EmplacementDB.rack_numero,        # 3. Numero de Rack (1, 2, ...)
                    case_ordre_allees,                # 4. Allee (A, B, ...)
                    EmplacementDB.position_dans_niveau, # 5. Position
                    func.random()                     # 6. Aleatoire
                )

            emplacement_optimal = query.first()

            if emplacement_optimal:
                if chercher_uniquement_allee_J:
                    print(f"INFO: Emplacement trouvé (Allee J): {emplacement_optimal.id_emplacement_str}")
                elif mode_eparpillage_total:
                    print(f"INFO: Emplacement trouvé (Eparpillement Total): {emplacement_optimal.id_emplacement_str}")
                elif emplacement_optimal.niveau > 7:
                    print(f"INFO: Aucun emplacement 'haut' (niveaux 1-7) trouvé. Proposition d'un 'bas': {emplacement_optimal.id_emplacement_str}")

            return emplacement_optimal

        except Exception as e:
            print(f"Erreur lors de la recherche d'un emplacement libre optimal : {e}")
            return None


    def assigner_produit_a_emplacement(self, session: Session, id_emplacement_str: str,
                                          nom_produit: str, id_produit: str, nom_utilisateur_actionneur: str = "SYSTEME") -> tuple[bool, str, EmplacementDB | None]:
        """
        Tente d'assigner un produit a un emplacement. ID Produit est maintenant obligatoire.
        NE FAIT PAS DE COMMIT.
        Retourne (succes_bool, message_str, emplacement_modifie_ou_None).
        """
        if not id_produit:
            return False, "L'ID Produit est manquant et obligatoire.", None

        # 1. Verifier si ce produit_id specifique existe deja ailleurs
        emplacement_existant_du_produit = self.verifier_si_produit_existe(session, id_produit)
        if emplacement_existant_du_produit:
            if emplacement_existant_du_produit.id_emplacement_str == id_emplacement_str:
                return False, f"Produit (ID: {id_produit}) est déjà present dans cet emplacement '{id_emplacement_str}'.", emplacement_existant_du_produit
            else:
                return False, f"Produit (ID: {id_produit}) existe déjà à l'emplacement '{emplacement_existant_du_produit.id_emplacement_str}'. Assignation à '{id_emplacement_str}' annulée.", None

        # 2. Recuperer l'emplacement cible
        emplacement = self.get_emplacement_par_id_complet(session, id_emplacement_str)

        if not emplacement:
            return False, f"Emplacement cible '{id_emplacement_str}' non trouvé.", None

        # 3. Verifier si l'emplacement cible est libre
        if not emplacement.est_libre:
            return False, f"Emplacement '{id_emplacement_str}' déjà occupé par '{emplacement.produit_nom}' (ID: {emplacement.produit_id}).", emplacement

        # 4. Si toutes les verifications sont passees, on peut assigner
        emplacement.marquer_comme_assigne(nom_produit, id_produit)
        session.add(emplacement)

        # Creer l'entree d'historique
        historique_entry = HistoriqueMouvementDB(
            type_action="ASSIGNATION",
            id_emplacement_str=emplacement.id_emplacement_str,
            produit_id=id_produit,
            produit_nom=nom_produit,
            utilisateur_nom=nom_utilisateur_actionneur
        )
        session.add(historique_entry)

        return True, f"Produit '{nom_produit}' (ID: {id_produit}) assigné à '{id_emplacement_str}'.", emplacement

    def liberer_emplacement_par_id(self, session: Session, id_emplacement_str: str,
                                      nom_utilisateur_actionneur: str = "SYSTEME") -> tuple[bool, str, EmplacementDB | None]:
        try:
            emplacement = self.get_emplacement_par_id_complet(session, id_emplacement_str)

            if not emplacement:
                return {
                    "id_emplacement_str": id_emplacement_str, "status": "NON_TROUVE",
                    "message_operation": f"Emplacement '{id_emplacement_str}' non trouvé.",
                    "ancien_produit_nom": None, "ancien_produit_id": None
                }

            if emplacement.est_libre:
                return {
                    "id_emplacement_str": id_emplacement_str, "status": "DEJA_LIBRE",
                    "message_operation": f"Emplacement '{id_emplacement_str}' déjà libre.",
                    "ancien_produit_nom": None, "ancien_produit_id": None
                }

            # Sauvegarder les infos du produit AVANT de le marquer comme libre
            nom_produit_avant = emplacement.produit_nom
            id_produit_avant = emplacement.produit_id

            succes_marquage = emplacement.marquer_comme_libre()

            if not succes_marquage:
                return {
                    "id_emplacement_str": id_emplacement_str, "status": "ERREUR_MARQUAGE",
                    "message_operation": f"Echec du marquage comme libre pour {id_emplacement_str}, état inattendu.",
                    "ancien_produit_nom": nom_produit_avant,
                    "ancien_produit_id": id_produit_avant
                }

            session.add(emplacement)

            historique_entry = HistoriqueMouvementDB(
                type_action="LIBERATION",
                id_emplacement_str=emplacement.id_emplacement_str,
                produit_id=id_produit_avant,
                produit_nom=nom_produit_avant,
                utilisateur_nom=nom_utilisateur_actionneur
            )
            session.add(historique_entry)

            return {
                "id_emplacement_str": id_emplacement_str, "status": "LIBERATION_NECESSAIRE",
                "message_operation": f"Pret pour libération.",
                "ancien_produit_nom": nom_produit_avant,
                "ancien_produit_id": id_produit_avant
            }

        except Exception as e:
            print(f"Erreur DANS liberer_emplacement_par_id pour '{id_emplacement_str}': {e}")
            return {
                "id_emplacement_str": id_emplacement_str, "status": "ERREUR",
                "message_operation": f"Erreur serveur lors de la tentative de libération de '{id_emplacement_str}'.",
                "ancien_produit_nom": "N/A", "ancien_produit_id": "N/A"
            }

    def liberer_emplacements_en_masse(self, session: Session, liste_id_emplacement_str: list,
                                           nom_utilisateur_actionneur: str = "SYSTEME_MASSE") -> dict:
        resultats_par_id = {}
        ids_necessitant_commit = []

        for id_emp_str in liste_id_emplacement_str:
            operation_detail = self.liberer_emplacement_par_id(
                session=session,
                id_emplacement_str=id_emp_str,
                nom_utilisateur_actionneur=nom_utilisateur_actionneur
            )
            resultats_par_id[id_emp_str] = operation_detail
            if operation_detail["status"] == "LIBERATION_NECESSAIRE":
                ids_necessitant_commit.append(id_emp_str)

        if ids_necessitant_commit:
            try:
                session.commit()
                print(f"Libération en masse : {len(ids_necessitant_commit)} emplacements commités par '{nom_utilisateur_actionneur}'.")
                for id_emp in ids_necessitant_commit:
                    resultats_par_id[id_emp]["status_final"] = "Libéré avec succes"
                    resultats_par_id[id_emp]["message_final"] = f"Libéré (contenait '{resultats_par_id[id_emp]['ancien_produit_nom']}', ID: {resultats_par_id[id_emp]['ancien_produit_id']})."

            except Exception as e:
                session.rollback()
                print(f"Erreur lors du commit de la libération en masse : {e}. Rollback effectue.")
                for id_emp in ids_necessitant_commit:
                    resultats_par_id[id_emp]["status_final"] = "Echec (Rollback)"
                    resultats_par_id[id_emp]["message_final"] = "Libération annulée (erreur de sauvegarde globale)."
        else:
            print("Liberation en masse : Aucun emplacement n'a nécessité de modification pour libération.")

        for id_emp, detail in resultats_par_id.items():
            if "status_final" not in detail:
                detail["status_final"] = detail["status"]
                detail["message_final"] = detail["message_operation"]

        return resultats_par_id

    def assigner_produits_en_masse(self, session: Session, produits_a_assigner: list,
                                   exclure_allee_J_global: bool = True,
                                   mode_eparpillage_total_global: bool = False,
                                   nom_utilisateur_actionneur: str = "SYSTEME"
                                   ) -> list:
        resultats_batch = []
        ids_emplacements_reserves_pour_ce_lot = []

        for prod_data in produits_a_assigner:
            nom_produit = prod_data.get('nom_produit')
            taille_requise = prod_data.get('taille_requise')
            id_produit = prod_data.get('id_produit')

            if not nom_produit or not taille_requise or not id_produit:
                resultats_batch.append({
                    "produit_nom": nom_produit or "Inconnu", "id_produit": id_produit or "N/A",
                    "statut": "Echec", "message": "Données produit incomplètes (nom, ID produit et taille requis)."
                })
                continue

            if id_produit:
                emplacement_existant_pour_ce_produit = self.verifier_si_produit_existe(session, id_produit)
                if emplacement_existant_pour_ce_produit:
                    resultats_batch.append({
                        "produit_nom": nom_produit, "id_produit": id_produit,
                        "statut": "Ignore",
                        "message": f"Produit déjà présent à l'emplacement '{emplacement_existant_pour_ce_produit.id_emplacement_str}'."
                    })
                    continue

            # Trouver un emplacement optimal en excluant ceux deja pris pour ce lot
            emplacement_optimal = self.trouver_emplacement_libre_optimal(
                session,
                taille_recherchee=taille_requise,
                exclure_allee_J_par_defaut=exclure_allee_J_global,
                chercher_uniquement_allee_J=False,
                mode_eparpillage_total=mode_eparpillage_total_global,
                ids_emplacements_a_exclure=ids_emplacements_reserves_pour_ce_lot
            )

            if not emplacement_optimal:
                resultats_batch.append({
                    "produit_nom": nom_produit, "id_produit": id_produit,
                    "statut": "Echec",
                    "message": f"Aucun emplacement libre de taille '{taille_requise}' trouvé (en tenant compte des reservations du lot)."
                })
                continue

            success_assign, msg_assign, emp_assigne_obj = self.assigner_produit_a_emplacement(
                session, emplacement_optimal.id_emplacement_str, nom_produit, id_produit, nom_utilisateur_actionneur=nom_utilisateur_actionneur
            )

            if success_assign:
                ids_emplacements_reserves_pour_ce_lot.append(emplacement_optimal.id_emplacement_str)
                resultats_batch.append({
                    "produit_nom": nom_produit, "id_produit": id_produit,
                    "statut": "Assigné",
                    "emplacement_assigne": emplacement_optimal.id_emplacement_str,
                    "message": msg_assign
                })
            else:
                resultats_batch.append({
                    "produit_nom": nom_produit, "id_produit": id_produit,
                    "statut": "Echec",
                    "emplacement_tente": emplacement_optimal.id_emplacement_str,
                    "message": msg_assign
                })

        if any(r["statut"] == "Assigné" for r in resultats_batch):
            try:
                session.commit()
                nb_assignes = sum(1 for r in resultats_batch if r["statut"] == "Assigné")
                print(f"Assignation en masse : {nb_assignes} produits assignés et commités (Mode eparpillement: {mode_eparpillage_total_global}).")
            except Exception as e:
                session.rollback()
                print(f"Erreur lors du commit de l'assignation en masse : {e}. Rollback effectué.")
                for res in resultats_batch:
                    if res["statut"] == "Assigné":
                        res["statut"] = "Echec (Rollback)"
                        res["message"] = "L'assignation a ete annulee (erreur de sauvegarde globale)."
        else:
            print("Assignation en masse : Aucun produit n'a pu etre assigné dans ce lot.")

        return resultats_batch

    def get_allee_details_complete(self, session: Session, lettre_allee_cible: str) -> dict | None:
        """
        Recupere les details complets d'une allee, y compris tous ses racks et leurs emplacements.
        """
        allee_cible = session.query(AlleeDB).filter(AlleeDB.lettre_allee == lettre_allee_cible.upper()).first()

        if not allee_cible:
            print(f"Aucune allée trouvée pour la lettre : {lettre_allee_cible.upper()}")
            return None

        racks_db = session.query(RackDB)\
            .filter(RackDB.allee_lettre == allee_cible.lettre_allee) \
            .order_by(RackDB.numero_rack)\
            .all()

        racks_info_list = []
        for rack_db in racks_db:
            emplacements_db = session.query(EmplacementDB)\
                .filter(EmplacementDB.rack_id == rack_db.id) \
                .order_by(EmplacementDB.niveau, EmplacementDB.position_dans_niveau)\
                .all()

            emplacements_list_data = []
            for emp_db in emplacements_db:
                emplacements_list_data.append({
                    "id_emplacement_str": emp_db.id_emplacement_str,
                    "niveau": emp_db.niveau,
                    "position_dans_niveau": emp_db.position_dans_niveau,
                    "taille": emp_db.taille,
                    "est_libre": emp_db.est_libre,
                    "produit_nom": emp_db.produit_nom,
                    "produit_id": emp_db.produit_id
                })

            racks_info_list.append({
                "id_rack_complet_str": rack_db.id_rack_complet_str,
                "numero_rack": rack_db.numero_rack,
                "allee_lettre": rack_db.allee_lettre,
                "taille_emplacements_par_defaut": rack_db.taille_emplacements_par_defaut,
                "nombre_niveaux": rack_db.nombre_niveaux,
                "emplacements_par_niveau": rack_db.emplacements_par_niveau,
                "emplacements": emplacements_list_data
            })

        return {
            "lettre_allee": allee_cible.lettre_allee,
            "racks_info": racks_info_list
        }

    def verifier_si_produit_existe(self, session: Session, id_produit: str) -> EmplacementDB | None:
        """
        Verifie si un produit avec cet id_produit est deja assigne a un emplacement.
        Retourne l'objet EmplacementDB si trouve, sinon None.
        """
        if not id_produit:
            return None

        emplacement_existant = session.query(EmplacementDB)\
            .filter(EmplacementDB.produit_id == id_produit, EmplacementDB.est_libre == False)\
            .first()
        return emplacement_existant

    def rechercher_produit(self, session: Session, terme_recherche: str) -> list[EmplacementDB]:
        """
        Recherche des produits par ID exact ou par nom partiel (insensible a la casse).
        Retourne une liste d'objets EmplacementDB ou les produits sont trouves.
        """
        if not terme_recherche:
            return []

        terme_recherche_lower = terme_recherche.lower()

        query = session.query(EmplacementDB).filter(
            EmplacementDB.est_libre == False,
            or_(
                EmplacementDB.produit_id == terme_recherche,
                EmplacementDB.produit_nom.ilike(f"%{terme_recherche_lower}%")
            )
        )

        emplacements_trouves = query.all()
        return emplacements_trouves

    def get_statistiques_entrepot(self, session: Session) -> dict:
        """
        Calcule et retourne des statistiques de base sur l'occupation de l'entrepot.
        """
        stats = {}

        try:
            total_emplacements = session.query(func.count(EmplacementDB.id)).scalar()
            stats['total_emplacements'] = total_emplacements

            if total_emplacements == 0:
                stats['emplacements_occupes'] = 0
                stats['emplacements_libres'] = 0
                stats['emplacements_hauts_libres_global'] = 0
                stats['taux_occupation_global'] = 0.0
                stats['par_taille'] = {}
                stats['par_allee'] = {}
                return stats

            emplacements_occupes = session.query(func.count(EmplacementDB.id))\
                .filter(EmplacementDB.est_libre == False).scalar()
            stats['emplacements_occupes'] = emplacements_occupes

            emplacements_libres = total_emplacements - emplacements_occupes
            stats['emplacements_libres'] = emplacements_libres

            if total_emplacements > 0:
                stats['taux_occupation_global'] = round((emplacements_occupes / total_emplacements) * 100, 2)
            else:
                stats['taux_occupation_global'] = 0.0

            emplacements_hauts_libres_global = session.query(func.count(EmplacementDB.id))\
                .filter(EmplacementDB.est_libre == True, EmplacementDB.niveau <= 7).scalar()
            stats['emplacements_hauts_libres_global'] = emplacements_hauts_libres_global

            stats_par_taille = session.query(
                EmplacementDB.taille,
                func.count(EmplacementDB.id).label('total'),
                func.sum(case((EmplacementDB.est_libre == False, 1), else_=0)).label('occupes')
            ).group_by(EmplacementDB.taille).all()

            stats['par_taille'] = {}
            tailles_existantes = session.query(EmplacementDB.taille).distinct().all()
            for (taille,) in tailles_existantes:
                total_t = session.query(func.count(EmplacementDB.id)).filter(EmplacementDB.taille == taille).scalar()
                occupes_t = session.query(func.count(EmplacementDB.id)).filter(EmplacementDB.taille == taille, EmplacementDB.est_libre == False).scalar()

                total_hauts_t = session.query(func.count(EmplacementDB.id)).filter(EmplacementDB.taille == taille, EmplacementDB.niveau <= 7).scalar()
                occupes_hauts_t = session.query(func.count(EmplacementDB.id)).filter(EmplacementDB.taille == taille, EmplacementDB.niveau <= 7, EmplacementDB.est_libre == False).scalar()
                libres_hauts_t = total_hauts_t - occupes_hauts_t

                stats['par_taille'][taille] = {
                    'total': total_t,
                    'occupes': occupes_t,
                    'libres': total_t - occupes_t,
                    'taux_occupation': round((occupes_t / total_t) * 100, 2) if total_t > 0 else 0.0,
                    'total_hauts': total_hauts_t,
                    'occupes_hauts': occupes_hauts_t,
                    'libres_hauts': libres_hauts_t,
                    'taux_occupation_hauts': round((occupes_hauts_t / total_hauts_t) * 100, 2) if total_hauts_t > 0 else 0.0
                }

            stats_par_allee_query = session.query(
                EmplacementDB.allee_lettre,
                func.count(EmplacementDB.id).label('total_allee'),
                func.sum(case((EmplacementDB.est_libre == False, 1), else_=0)).label('occupes_allee')
            ).group_by(EmplacementDB.allee_lettre).order_by(EmplacementDB.allee_lettre).all()

            stats['par_allee'] = {}
            allees_existantes = session.query(EmplacementDB.allee_lettre).distinct().order_by(EmplacementDB.allee_lettre).all()
            for (lettre_allee,) in allees_existantes:
                total_a = session.query(func.count(EmplacementDB.id)).filter(EmplacementDB.allee_lettre == lettre_allee).scalar()
                occupes_a = session.query(func.count(EmplacementDB.id)).filter(EmplacementDB.allee_lettre == lettre_allee, EmplacementDB.est_libre == False).scalar()

                total_hauts_a = session.query(func.count(EmplacementDB.id)).filter(EmplacementDB.allee_lettre == lettre_allee, EmplacementDB.niveau <= 7).scalar()
                occupes_hauts_a = session.query(func.count(EmplacementDB.id)).filter(EmplacementDB.allee_lettre == lettre_allee, EmplacementDB.niveau <= 7, EmplacementDB.est_libre == False).scalar()
                libres_hauts_a = total_hauts_a - occupes_hauts_a

                stats['par_allee'][lettre_allee] = {
                    'total': total_a,
                    'occupes': occupes_a,
                    'libres': total_a - occupes_a,
                    'taux_occupation': round((occupes_a / total_a) * 100, 2) if total_a > 0 else 0.0,
                    'total_hauts': total_hauts_a,
                    'occupes_hauts': occupes_hauts_a,
                    'libres_hauts': libres_hauts_a,
                    'taux_occupation_hauts': round((occupes_hauts_a / total_hauts_a) * 100, 2) if total_hauts_a > 0 else 0.0
                }
            return stats

        except Exception as e:
            print(f"Erreur lors du calcul des statistiques: {e}")
            return {"erreur": "Impossible de calculer les statistiques."}

    def get_historique_mouvements(self, session: Session,
                                  page: int = 1,
                                  elements_par_page: int = 20,
                                  type_action_filtre: str = None,
                                  id_emplacement_filtre: str = None,
                                  id_produit_filtre: str = None,
                                  ) -> dict:
        """
        Recupere l'historique des mouvements avec pagination et filtres optionnels.
        """
        if page < 1:
            page = 1
        if elements_par_page < 1:
            elements_par_page = 20

        query = session.query(HistoriqueMouvementDB)

        if type_action_filtre:
            query = query.filter(HistoriqueMouvementDB.type_action == type_action_filtre.upper())
        if id_emplacement_filtre:
            query = query.filter(HistoriqueMouvementDB.id_emplacement_str.ilike(f"%{id_emplacement_filtre}%"))
        if id_produit_filtre:
            query = query.filter(HistoriqueMouvementDB.produit_id.ilike(f"%{id_produit_filtre}%"))

        total_elements = query.count()
        total_pages = (total_elements + elements_par_page - 1) // elements_par_page

        mouvements = query.order_by(desc(HistoriqueMouvementDB.timestamp))\
                             .offset((page - 1) * elements_par_page)\
                             .limit(elements_par_page)\
                             .all()

        resultat = {
            "mouvements": [
                {
                    "timestamp": mouvement.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "type_action": mouvement.type_action,
                    "id_emplacement_str": mouvement.id_emplacement_str,
                    "produit_id": mouvement.produit_id,
                    "produit_nom": mouvement.produit_nom,
                    "utilisateur_nom": mouvement.utilisateur_nom
                } for mouvement in mouvements
            ],
            "pagination": {
                "page_actuelle": page,
                "elements_par_page": elements_par_page,
                "total_elements": total_elements,
                "total_pages": total_pages
            }
        }
        return resultat

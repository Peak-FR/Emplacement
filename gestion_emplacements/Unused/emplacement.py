class Emplacement:
    def __init__(self, id_emplacement, taille, allee, rack_numero, niveau, position_dans_niveau):
        self.id_emplacement = id_emplacement
        self.taille = taille
        self.allee = allee
        self.rack_numero = rack_numero
        self.niveau = niveau
        self.position_dans_niveau = position_dans_niveau

        self.est_libre = True
        self.produit_id_externe = None
        self.produit_nom = None 

    def assigner_produit(self, nom_produit, id_produit_externe=None):
        if self.est_libre:
            self.produit_nom = nom_produit
            self.produit_id_externe = id_produit_externe
            self.est_libre = False
            print(f"Produit '{nom_produit}' (ID: {id_produit_externe}) assigné à l'emplacement {self.id_emplacement}.")
            return True
        else:
            print(f"Erreur : L'emplacement {self.id_emplacement} est déjà occupé par '{self.produit_nom}' (ID: {self.produit_id_externe}).")
            return False

    def liberer_emplacement(self):
        if not self.est_libre:
            produit_ancien_nom = self.produit_nom
            produit_ancien_id = self.produit_id_externe
            self.produit_nom = None
            self.produit_id_externe = None
            self.est_libre = True
            print(f"Emplacement {self.id_emplacement} (contenait '{produit_ancien_nom}', ID: {produit_ancien_id}) libéré.")
            return True
        else:
            print(f"Info : L'emplacement {self.id_emplacement} est déjà libre.")
            return False

    def __str__(self):
        if self.est_libre:
            statut = "Libre"
        else:
            details_produit = self.produit_nom
            if self.produit_id_externe:
                details_produit += f" (ID: {self.produit_id_externe})"
            statut = f"Occupé par: {details_produit}"
        return f"Emplacement {self.id_emplacement} (Allée: {self.allee}, Rack: {self.rack_numero}, Nv: {self.niveau}, Pos: {self.position_dans_niveau}, Taille: {self.taille}) - Statut: {statut}"

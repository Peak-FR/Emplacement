from .emplacement import Emplacement

class Rack:
    def __init__(self, allee_lettre, numero_rack, nombre_niveaux, emplacements_par_niveau, taille_emplacements):
        self.allee_lettre = allee_lettre
        self.numero_rack = numero_rack
        
        self.id_rack_complet_str = f"{allee_lettre}{numero_rack}"
        
        self.nombre_niveaux = nombre_niveaux
        self.emplacements_par_niveau = emplacements_par_niveau
        self.taille_emplacements_par_defaut = taille_emplacements
        
        self.emplacements = []
        self._initialiser_emplacements()

    def _initialiser_emplacements(self):
        for niveau in range(1, self.nombre_niveaux + 1):
            for position in range(1, self.emplacements_par_niveau + 1):
                id_emplacement_str = f"{self.id_rack_complet_str}-{niveau}-{position}"
                
                emplacement_obj = Emplacement(
                    id_emplacement=id_emplacement_str,
                    taille=self.taille_emplacements_par_defaut,
                    allee=self.allee_lettre,
                    rack_numero=self.numero_rack,
                    niveau=niveau,
                    position_dans_niveau=position
                )
                self.emplacements.append(emplacement_obj)

    def get_emplacements_libres(self, taille_recherchee=None):
        
        libres = []
        for emp in self.emplacements:
            if emp.est_libre:
                if taille_recherchee is None or emp.taille == taille_recherchee:
                    libres.append(emp)
        return libres

    def __str__(self):

        nb_libres = len(self.get_emplacements_libres()) 
        return (f"Rack {self.id_rack_complet_str} (Allée: {self.allee_lettre}, N°: {self.numero_rack}, "
                f"{self.nombre_niveaux} niveaux, {self.emplacements_par_niveau} empl/niveau, "
                f"Taille: {self.taille_emplacements_par_defaut}) - "
                f"{nb_libres}/{len(self.emplacements)} libres")

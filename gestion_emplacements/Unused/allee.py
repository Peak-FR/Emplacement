from .rack import Rack

class Allee:
    def __init__(self, lettre_allee):
        self.lettre_allee = lettre_allee
        self.racks = [] 

    def ajouter_rack(self, rack_obj):
        """Ajoute un objet Rack à l'allée."""
        if isinstance(rack_obj, Rack) and rack_obj.allee_lettre == self.lettre_allee:
            self.racks.append(rack_obj)
        else:
            print(f"Erreur : Impossible d'ajouter le rack (ID: {getattr(rack_obj, 'id_rack_complet_str', 'Inconnu')}) "
                  f"à l'allée {self.lettre_allee}. Vérifiez l'appartenance ou le type de l'objet.")

    def get_rack_par_numero(self, numero_rack_int):
        """Récupère un rack spécifique de l'allée par son numéro."""
        for rack in self.racks:
            if rack.numero_rack == numero_rack_int:
                return rack
        return None

    def get_tous_emplacements_allee(self):
        """Retourne une liste de tous les objets Emplacement dans cette allée."""
        tous_emplacements = []
        for rack in self.racks:
            tous_emplacements.extend(rack.emplacements)
        return tous_emplacements

    def get_emplacements_libres_allee(self, taille_recherchee=None):
        """Retourne une liste des objets Emplacement libres dans cette allée, 
           éventuellement filtrée par taille."""
        emplacements_libres_dans_allee = []
        for rack_obj in self.racks:
            if taille_recherchee is None or rack_obj.taille_emplacements_par_defaut == taille_recherchee:
                emplacements_libres_dans_allee.extend(rack_obj.get_emplacements_libres(taille_recherchee=taille_recherchee))
        return emplacements_libres_dans_allee
        
    def __str__(self):
        """Représentation textuelle de l'objet Allée."""
        nombre_total_emplacements = sum(len(rack.emplacements) for rack in self.racks)
        nombre_emplacements_libres = sum(len(rack.get_emplacements_libres()) for rack in self.racks)
        
        return (f"Allée {self.lettre_allee} (Contient {len(self.racks)} racks, "
                f"{nombre_emplacements_libres}/{nombre_total_emplacements} emplacements libres)")

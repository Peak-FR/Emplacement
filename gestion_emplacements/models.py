from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash


# --- Définition de la Base Déclarative ---
Base = declarative_base()

# --- Définition du Modèle EmplacementDB ---

class EmplacementDB(Base):
    __tablename__ = 'emplacements'

    # Colonnes de la table:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # ID numérique unique pour la BDD
    
    # Identifiant métier, lisible et unique (ex: "A1-1-1")
    id_emplacement_str = Column(String(50), unique=True, index=True, nullable=False) 
    
    taille = Column(String(50), nullable=False)                 # Ex: "Grand", "Petit", "Moyen"
    allee_lettre = Column(String(10), index=True, nullable=False) # Ex: "A"
    rack_numero = Column(Integer, index=True, nullable=False)     # Ex: 1
    niveau = Column(Integer, nullable=False)                      # Ex: 1 (tiroir)
    position_dans_niveau = Column(Integer, nullable=False)        # Ex: 1
    
    est_libre = Column(Boolean, default=True, nullable=False)
    produit_id = Column(String(100), nullable=True, index=True) # ID Produit
    produit_nom = Column(String(255), nullable=True)            # Nom du produit
    
    # Clé étrangère pour lier cet emplacement à un rack spécifique.
    rack_id = Column(Integer, ForeignKey('racks.id'), nullable=False)
    
    # Définition de la relation avec la table/classe RackDB.
    rack = relationship("RackDB", back_populates="emplacements")

    def __repr__(self):
        statut_produit = ""
        if not self.est_libre:
            statut_produit = f"Occupé par: {self.produit_nom or 'N/A'}"
            if self.produit_id:
                statut_produit += f" (IDP: {self.produit_id})"
        else:
            statut_produit = "Libre"
            
        return (f"<EmplacementDB(id_str='{self.id_emplacement_str}', "
                f"taille='{self.taille}', statut='{statut_produit}')>")

    # --- Méthodes Logiques (adaptées pour un modèle ORM) ---
    def marquer_comme_assigne(self, nom_produit, id_produit=None):
        """Marque l'emplacement comme occupé par un produit."""
        if self.est_libre:
            self.produit_nom = nom_produit
            self.produit_id = id_produit
            self.est_libre = False
            return True
        else:
            print(f"AVERTISSEMENT: Tentative d'assigner à un emplacement déjà occupé: {self.id_emplacement_str}")
            return False

    def marquer_comme_libre(self):
        """Marque l'emplacement comme libre."""
        if not self.est_libre:
            produit_quitte = self.produit_nom
            self.produit_nom = None
            self.produit_id = None
            self.est_libre = True
            return True
        return False

class RackDB(Base):
    __tablename__ = 'racks'

    # Colonnes de la table:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    id_rack_complet_str = Column(String(50), unique=True, index=True, nullable=False)
    
    allee_lettre = Column(String(10), index=True, nullable=False) # Ex: "A"
    numero_rack = Column(Integer, nullable=False)               # Ex: 1
    
    nombre_niveaux = Column(Integer, nullable=False)
    emplacements_par_niveau = Column(Integer, nullable=False)
    taille_emplacements_par_defaut = Column(String(50), nullable=False) # Ex: "Grand", "Petit", "Moyen"

    # Clé étrangère pour lier ce rack à une allée spécifique.
    allee_id = Column(Integer, ForeignKey('allees.id'), nullable=False)

    # Définition de la relation avec la table/classe AlleeDB.
    allee = relationship("AlleeDB", back_populates="racks")
    
    # Définition de la relation avec la table/classe EmplacementDB.
    emplacements = relationship("EmplacementDB", back_populates="rack", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<RackDB(id_str='{self.id_rack_complet_str}', allée='{self.allee_lettre}', "
                f"taille_empl='{self.taille_emplacements_par_defaut}', "
                f"niveaux={self.nombre_niveaux}, empl_par_niveau={self.emplacements_par_niveau})>")

class AlleeDB(Base):
    __tablename__ = 'allees'

    # Colonnes de la table:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Lettre identifiant l'allée, ex: "A", "B". Doit être unique.
    lettre_allee = Column(String(10), unique=True, index=True, nullable=False)

    # Définition de la relation avec la table/classe RackDB.
    racks = relationship("RackDB", back_populates="allee", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AlleeDB(lettre='{self.lettre_allee}')>"
    
    
class UtilisateurDB(Base):
    __tablename__ = "utilisateurs"
    id = Column(Integer, primary_key=True, index=True)
    nom_utilisateur = Column(String(100), unique=True, index=True, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="utilisateur", nullable=True)
    est_actif = Column(Boolean, default=True)

    # Méthodes pour gérer le mot de passe
    def set_mot_de_passe(self, mot_de_passe):
        self.mot_de_passe_hash = generate_password_hash(mot_de_passe)

    def verifier_mot_de_passe(self, mot_de_passe):
        return check_password_hash(self.mot_de_passe_hash, mot_de_passe)

    def __repr__(self):
        return f"<UtilisateurDB(id={self.id}, nom_utilisateur='{self.nom_utilisateur}')>"
    
class HistoriqueMouvementDB(Base):
    __tablename__ = "historique_mouvements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    type_action = Column(String(50), nullable=False)
    id_emplacement_str = Column(String(50), index=True, nullable=False)
    produit_id = Column(String(100), nullable=True, index=True)
    produit_nom = Column(String(255), nullable=True)
    utilisateur_nom = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<HistoriqueMouvementDB(action='{self.type_action}', empl='{self.id_emplacement_str}', user='{self.utilisateur_nom}')>"


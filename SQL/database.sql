CREATE TABLE classe (
   Nom_classe VARCHAR(3) PRIMARY KEY,
   Agenda VARCHAR(255)
);

CREATE TABLE membre (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Cle_API VARCHAR(50) NOT NULL UNIQUE,
   Nom VARCHAR(50) NOT NULL,
   Prenom VARCHAR(30) NOT NULL,
   Classe VARCHAR(3) NOT NULL DEFAULT 'DE',
   Role_Association VARCHAR(30) NOT NULL DEFAULT 'Membre',
   Photo_profil VARCHAR(50) NOT NULL DEFAULT 'default',
   Date_inscription VARCHAR(10) NOT NULL,
   Plante_Principale INTEGER DEFAULT NULL,
   FOREIGN KEY (Classe) REFERENCES classe(Nom_classe)
);

CREATE TABLE plante (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Nom VARCHAR(50) NOT NULL,
   Type_Plante VARCHAR(50) NOT NULL,
   Statut VARCHAR(20) DEFAULT 'Normale',
   Localisation VARCHAR(25) NOT NULL,
   Humidite REAL DEFAULT 0.0,
   Temperature REAL DEFAULT 0.0,
   Luminosite REAL DEFAULT 0.0,
   Derniere_Photo VARCHAR(50) DEFAULT 'None',
   Superviseur INTEGER DEFAULT NULL,
   FOREIGN KEY (Superviseur) REFERENCES membre(Id)
);

CREATE TABLE intervention (
   Id INTEGER PRIMARY KEY AUTOINCREMENT,
   Date_intervention VARCHAR(20),
   Id_intervenant INTEGER DEFAULT NULL,
   Id_Plante INTEGER DEFAULT NULL,
   Note VARCHAR(250) DEFAULT '',
   FOREIGN KEY (Id_intervenant) REFERENCES membre(Id),
   FOREIGN KEY (Id_Plante) REFERENCES plante(Id)
);

CREATE TABLE rapport (
   Date_Rapport VARCHAR(7) PRIMARY KEY,
   Id_Plante INTEGER DEFAULT NULL,
   Histo_Hum VARCHAR(255) DEFAULT '',
   Histo_Temp VARCHAR(255) DEFAULT '',
   Histo_Lum VARCHAR(255) DEFAULT '',
   Histo_Photo VARCHAR(50),
   FOREIGN KEY (Id_Plante) REFERENCES plante(Id)
);

CREATE TABLE Cartes (
   Identifier VARCHAR(50) PRIMARY KEY,
   Plantes VARCHAR(20) DEFAULT ''
);

-- Default Values
INSERT INTO classe (Nom_classe, Agenda) VALUES ('DE', 'Agenda DEFAULT');

INSERT INTO membre (Cle_API, Nom, Prenom, Classe, Role_Association, Photo_profil, Date_inscription, Plante_Principale) 
VALUES ('DEFAULT_API_KEY', 'Everyone', 'Everyone', 'DE', 'Everyone', 'everyone', '2024-01-01', NULL);
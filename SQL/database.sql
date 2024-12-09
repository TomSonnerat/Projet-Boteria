CREATE TABLE IF NOT EXISTS classe (
    Nom_classe VARCHAR(3) PRIMARY KEY,
    Agenda VARCHAR(255),
    Liste_membre VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS membre (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Cle_API VARCHAR NOT NULL UNIQUE,
    Nom VARCHAR(50) NOT NULL,
    Prenom VARCHAR(30) NOT NULL,
    Classe VARCHAR(3) NOT NULL,
    Role_Association VARCHAR(30) NOT NULL DEFAULT 'Membre',
    Photo_profil VARCHAR(50) NOT NULL DEFAULT 'default',
    Date_inscription VARCHAR(10) NOT NULL,
    Plante_Principale INT,
)

CREATE TABLE IF NOT EXISTS plante (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nom VARCHAR(50) NOT NULL,
    Type_Plante VARCHAR(50) NOT NULL,
    Statut VARCHAR(20) DEFAULT 'Normale',
    Localisation VARCHAR(25) NOT NULL,
    Humidite FLOAT DEFAULT 0.0,
    Temperature FLOAT DEFAULT 0.0,
    Luminosite FLOAT DEFAULT 0.0,
    Derniere_Photo VARCHAR(50) DEFAULT 'None',
    Superviseur INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_superviseur FOREIGN KEY (Superviseur) REFERENCES membre(Id)
)

CREATE TABLE IF NOT EXISTS intervention (
    Id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    Date_intervention VARCHAR(20),
    Id_intervenant INT NOT NULL DEFAULT 0,
    Id_Plante INT NOT NULL DEFAULT 0,
    Note VARCHAR(250) DEFAULT '',
    CONSTRAINT fk_intervenant FOREIGN KEY (Id_intervenant) REFERENCES membre(Id),
    CONSTRAINT fk_plante FOREIGN KEY (Id_Plante) REFERENCES plante(Id)
)

CREATE TABLE IF NOT EXISTS rapport (
    Date_Rapport VARCHAR(7) PRIMARY KEY?
    Id_Plante INT NOT NULL DEFAULT 0,
    Histo_Hum VARCHAR(255) DEFAULT '',
    Histo_Temp VARCHAR(255) DEFAULT '',
    Histo_Lum VARCHAR(255) DEFAULT '',
    Histo_Photo VARCHAR(50),
    CONSTRAINT fk_id_plante FOREIGN KEY (Id_Plante) REFERENCES plante(Id)
)

CREATE TABLE IF NOT EXISTS Cartes (
    Identifier VARCHAR(50) NOT NULL PRIMARY KEY,
    Plantes VARCHAR(20) DEFAULT ''
)
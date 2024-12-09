--  This is for test only, use manual installation for your data

INSERT INTO classe (Nom_classe, Agenda)
VALUES
('1A', 'Agenda 1A'),
('1B', 'Agenda 1B'),
('2A', 'Agenda 2A');

INSERT INTO membre (Cle_API, Nom, Prenom, Classe, Role_Association, Photo_profil, Date_inscription, Plante_Principale)
VALUES
('APIKEY1', 'Smith', 'John', '1A', 'President', 'smith.jpg', '2024-01-01', 1),
('APIKEY2', 'Doe', 'Jane', '1B', 'Treasurer', 'doe.jpg', '2024-01-02', 2),
('APIKEY3', 'Brown', 'Charlie', '2A', 'Secretary', 'brown.jpg', '2024-01-03', 3),
('APIKEY4', 'Johnson', 'Emily', '1A', 'Vice President', 'emily.jpg', '2024-01-04', 4),
('APIKEY5', 'Williams', 'Ethan', '1B', 'Event Manager', 'ethan.jpg', '2024-01-05', 5),
('APIKEY6', 'Garcia', 'Sophia', '2A', 'Volunteer', 'sophia.jpg', '2024-01-06', 6),
('APIKEY7', 'Martinez', 'Oliver', '1A', 'Volunteer', 'oliver.jpg', '2024-01-07', 7),
('APIKEY8', 'Davis', 'Amelia', '1B', 'Volunteer', 'amelia.jpg', '2024-01-08', 8),
('APIKEY9', 'Rodriguez', 'Mia', '2A', 'Volunteer', 'mia.jpg', '2024-01-09', 9),
('APIKEY10', 'Clark', 'Lucas', '1A', 'Volunteer', 'lucas.jpg', '2024-01-10', 10);

INSERT INTO plante (Nom, Type_Plante, Statut, Localisation, Humidite, Temperature, Luminosite, Derniere_Photo, Superviseur)
VALUES
('Fern', 'Indoor', 'normal', 'Localisation', 45.2, 22.5, 300, 'fern.jpg', 1),
('Cactus', 'Succulent', 'Dry', 'Localisation', 15.0, 27.3, 500, 'cactus.jpg', 2),
('Basil', 'Herb', 'Watered', 'Localisation', 60.0, 25.0, 200, 'basil.jpg', 3),
('Aloe Vera', 'Succulent', 'normal', 'Localisation', 50.0, 24.0, 250, 'aloe_vera.jpg', 4),
('Lavender', 'Herb', 'normal', 'Localisation', 20.0, 23.5, 400, 'lavender.jpg', 5),
('Snake Plant', 'Indoor', 'normal', 'Localisation', 35.0, 22.0, 300, 'snake_plant.jpg', 6),
('Money Plant', 'Indoor', 'normal', 'Localisation ', 60.0, 24.5, 320, 'money_plant.jpg', 7),
('Peace Lily', 'Flower', 'normal', 'Localisation', 70.0, 21.5, 200, 'peace_lily.jpg', 8),
('Spider Plant', 'Indoor', 'normal', 'Localisation', 80.0, 22.0, 180, 'spider_plant.jpg', 9),
('Rose', 'Flower', 'normal', 'Localisation', 30.0, 26.0, 600, 'rose.jpg', 10),
('Bamboo', 'Indoor', 'normal', 'Localisation', 65.0, 23.0, 150, 'bamboo.jpg', 1),
('Orchid', 'Flower', 'normal', 'Localisation', 55.0, 25.0, 400, 'orchid.jpg', 2),
('Palm', 'Outdoor', 'normal', 'Localisation', 40.0, 28.0, 500, 'palm.jpg', 3);

INSERT INTO intervention (Date_intervention, Id_intervenant, Id_Plante, Note)
VALUES
('2024-12-01', 1, 1, 'Lorem Ipsum Dolor Sit Amet'),
('2024-12-02', 2, 2, 'Lorem Ipsum Dolor Sit Amet'),
('2024-12-03', 3, 3, 'Lorem Ipsum Dolor Sit Amet');

INSERT INTO rapport (Date_Rapport, Id_Plante, Histo_Hum, Histo_Temp, Histo_Lum, Histo_Photo)
VALUES
('2024-01', 1, '45,46,47', '22,23,22', '300,310,320', 'fern_hist.jpg'),
('2024-02', 2, '15,16,14', '27,28,27', '500,520,510', 'cactus_hist.jpg'),
('2024-03', 3, '60,62,59', '25,26,25', '200,210,220', 'basil_hist.jpg');

INSERT INTO Cartes (Identifier, Plantes)
VALUES
('Card001', '1,2'),
('Card002', '3'),
('Card003', '2,3');
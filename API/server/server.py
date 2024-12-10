import os
import http.server
import socketserver
import json
import logging
import sqlite3
import urllib.parse
import datetime
import base64

PORT = 5000

script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, "server.log")
db_path = os.path.join(script_dir, "plant_tracking.db")
photos_dir = os.path.join(script_dir, "plant_photos")

os.makedirs(photos_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)

class PlantTrackingHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            sensor_data = json.loads(post_data.decode('utf-8'))

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            if path == '/sensor-data':
                cursor.execute("""
                    SELECT c.Plantes 
                    FROM Cartes c 
                    WHERE c.Identifier = ?
                """, (sensor_data['id'],))
                card_result = cursor.fetchone()

                if not card_result:
                    self.send_error_response(404, "No card found with this identifier")
                    return

                plant_ids = [int(pid) for pid in card_result[0].split(',')]

                for plant_id in plant_ids:
                    cursor.execute("""
                        UPDATE plante 
                        SET 
                            Temperature = ?, 
                            Luminosite = ?,
                            Derniere_Photo = ?
                        WHERE Id = ?
                    """, (
                        sensor_data['temperature'], 
                        sensor_data['light'], 
                        f"{plant_id}/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        plant_id
                    ))

                    ground_humidity = sensor_data.get('ground_humidity', [])
                    if isinstance(ground_humidity, list) and ground_humidity:
                        cursor.execute("""
                            UPDATE plante 
                            SET Humidite = ? 
                            WHERE Id = ?
                        """, (ground_humidity[0], plant_id))

                    if sensor_data.get('image'):
                        plant_photo_dir = os.path.join(photos_dir, str(plant_id))
                        os.makedirs(plant_photo_dir, exist_ok=True)
                        
                        image_path = os.path.join(
                            plant_photo_dir, 
                            f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        )
                        
                        with open(image_path, 'wb') as image_file:
                            image_file.write(base64.b64decode(sensor_data['image']))

                    current_month = datetime.datetime.now().strftime('%Y-%m')
                    cursor.execute("""
                        INSERT OR REPLACE INTO rapport (
                            Date_Rapport, 
                            Id_Plante, 
                            Histo_Hum, 
                            Histo_Temp, 
                            Histo_Lum, 
                            Histo_Photo
                        ) VALUES (
                            ?, ?, 
                            (SELECT COALESCE(Histo_Hum, '') || ',' || ? FROM rapport WHERE Date_Rapport = ? AND Id_Plante = ?), 
                            (SELECT COALESCE(Histo_Temp, '') || ',' || ? FROM rapport WHERE Date_Rapport = ? AND Id_Plante = ?), 
                            (SELECT COALESCE(Histo_Lum, '') || ',' || ? FROM rapport WHERE Date_Rapport = ? AND Id_Plante = ?), 
                            ?
                        )
                    """, (
                        current_month, plant_id, 
                        ground_humidity[0] if ground_humidity else 0, current_month, plant_id,
                        sensor_data['temperature'], current_month, plant_id,
                        sensor_data['light'], current_month, plant_id,
                        f"{plant_id}/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    ))

                conn.commit()
                
                self.send_json_response({"status": "success", "plants_updated": len(plant_ids)})

            else:
                self.send_error_response(404, "Endpoint not found")

            conn.close()

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            self.send_error_response(500, f"Database error: {str(e)}")
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            self.send_error_response(400, "Invalid JSON data")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            self.send_error_response(500, f"Unexpected server error: {str(e)}")

    def do_GET(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            params = urllib.parse.parse_qs(parsed_path.query)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            if path == '/GetPlantList':
                cursor.execute("SELECT Id, Nom FROM plante")
                results = cursor.fetchall()
                self.send_json_response([{"id": row[0], "nom": row[1]} for row in results])

            elif path == '/GetPlantInfos':
                plant_id = params.get('id', [None])[0]
                if plant_id:
                    cursor.execute("""
                        SELECT Id, Nom, Type_Plante, Localisation, Humidite, Temperature, Luminosite, Derniere_Photo 
                        FROM plante 
                        WHERE Id = ?
                    """, (plant_id,))
                    row = cursor.fetchone()
                    if row:
                        self.send_json_response({
                            "id": row[0], "nom": row[1], "type_plante": row[2], 
                            "localisation": row[3], "humidite": row[4], 
                            "temperature": row[5], "luminosite": row[6], 
                            "derniere_photo": row[7]
                        })
                    else:
                        self.send_error_response(404, "Plant not found")

            elif path == '/GetPlantBesoins':
                plant_id = params.get('id', [None])[0]
                if plant_id:
                    cursor.execute("""
                        SELECT statut, superviseur, 
                        (SELECT date_intervention FROM intervention 
                         WHERE Id_Plante = plante.Id 
                         ORDER BY date_intervention DESC LIMIT 1) as last_intervention_date
                        FROM plante 
                        WHERE Id = ?
                    """, (plant_id,))
                    row = cursor.fetchone()
                    if row:
                        self.send_json_response({
                            "statut": row[0], 
                            "superviseur": row[1], 
                            "derniere_intervention": row[2]
                        })
                    else:
                        self.send_error_response(404, "Plant not found")

            elif path == '/GetPlantInterventions':
                plant_id = params.get('id_plante', [None])[0]
                if plant_id:
                    cursor.execute("""
                        SELECT date_intervention, Id 
                        FROM intervention 
                        WHERE Id_Plante = ?
                    """, (plant_id,))
                    results = cursor.fetchall()
                    self.send_json_response([
                        {"date_intervention": row[0], "id": row[1]} 
                        for row in results
                    ])

            elif path == '/GetInterventionInfos':
                intervention_id = params.get('id_intervention', [None])[0]
                if intervention_id:
                    cursor.execute("""
                        SELECT membre.Nom, id_intervenant, role_association, 
                               id_plante, plante.Nom, note, intervention.Id
                        FROM intervention
                        JOIN plante ON plante.Id = id_plante
                        JOIN membre ON membre.Id = id_intervenant
                        WHERE intervention.Id = ?
                    """, (intervention_id,))
                    row = cursor.fetchone()
                    if row:
                        self.send_json_response({
                            "nom_intervenant": row[0], 
                            "id_intervenant": row[1], 
                            "role_intervenant": row[2],
                            "id_plante": row[3], 
                            "nom_plante": row[4], 
                            "note": row[5], 
                            "id_intervention": row[6]
                        })
                    else:
                        self.send_error_response(404, "Intervention not found")

            elif path == '/GetLatestIntervention':
                plant_id = params.get('id_plante', [None])[0]
                if plant_id:
                    cursor.execute("""
                        SELECT membre.Nom, id_intervenant, role_association, 
                               plante.Nom, id_plante, note, intervention.Id
                        FROM intervention
                        JOIN plante ON plante.Id = id_plante
                        JOIN membre ON membre.Id = id_intervenant
                        WHERE Id_Plante = ?
                        ORDER BY date_intervention DESC 
                        LIMIT 1
                    """, (plant_id,))
                    row = cursor.fetchone()
                    if row:
                        self.send_json_response({
                            "nom_intervenant": row[0], 
                            "id_intervenant": row[1], 
                            "role_intervenant": row[2],
                            "nom_plante": row[3], 
                            "id_plante": row[4], 
                            "note": row[5], 
                            "id_intervention": row[6]
                        })
                    else:
                        self.send_error_response(404, "No intervention found for this plant")

            elif path == '/GetAllRapports':
                plant_id = params.get('id_plante', [None])[0]
                if plant_id:
                    cursor.execute("""
                        SELECT Id, Date_Rapport 
                        FROM rapport 
                        WHERE Id_Plante = ? 
                        ORDER BY Date_Rapport DESC
                    """, (plant_id,))
                    results = cursor.fetchall()
                    self.send_json_response([
                        {"id": row[0], "date_rapport": row[1]} 
                        for row in results
                    ])

            elif path == '/GetRapport':
                rapport_id = params.get('id_rapport', [None])[0]
                if rapport_id:
                    cursor.execute("""
                        SELECT Date_Rapport, Histo_Hum, Histo_Temp, Histo_Lum, Histo_Photo 
                        FROM rapport 
                        WHERE Date_Rapport = ?
                    """, (rapport_id,))
                    row = cursor.fetchone()
                    if row:
                        self.send_json_response({
                            "date_rapport": row[0], 
                            "historique_humidite": row[1], 
                            "historique_temperature": row[2], 
                            "historique_luminosite": row[3], 
                            "photo": row[4]
                        })
                    else:
                        self.send_error_response(404, "Rapport not found")

            elif path == '/GetLatestRapport':
                plant_id = params.get('id_plante', [None])[0]
                if plant_id:
                    cursor.execute("""
                        SELECT Date_Rapport, Histo_Hum, Histo_Temp, Histo_Lum, Histo_Photo 
                        FROM rapport 
                        WHERE Id_Plante = ? 
                        ORDER BY Date_Rapport DESC 
                        LIMIT 1
                    """, (plant_id,))
                    row = cursor.fetchone()
                    if row:
                        self.send_json_response({
                            "date_rapport": row[0], 
                            "historique_humidite": row[1], 
                            "historique_temperature": row[2], 
                            "historique_luminosite": row[3], 
                            "photo": row[4]
                        })
                    else:
                        self.send_error_response(404, "No rapport found for this plant")

            elif path == '/GetListeMembre':
                cursor.execute("""
                    SELECT Id, Nom, Prenom, Classe, Role_Association 
                    FROM membre 
                    ORDER BY Classe, Nom
                """)
                results = cursor.fetchall()
                self.send_json_response([{
                    "id": row[0], "nom": row[1], "prenom": row[2], 
                    "classe": row[3], "role": row[4]
                } for row in results])

            elif path == '/GetMembreInfos':
                membre_id = params.get('id_membre', [None])[0]
                if membre_id:
                    cursor.execute("""
                        SELECT 
                            m.Nom, 
                            m.Prenom, 
                            m.Classe, 
                            m.Role_Association, 
                            m.Date_inscription,
                            (julianday('now') - julianday(m.Date_inscription)) / 365.25 AS Anciennete,
                            p.Nom AS Plante_Principale,
                            (SELECT COUNT(*) FROM intervention WHERE Id_intervenant = m.Id) AS Nombre_Interventions
                        FROM 
                            membre m
                        LEFT JOIN 
                            plante p ON m.Plante_Principale = p.Id
                        WHERE 
                            m.Id = ?
                    """, (membre_id,))
                    row = cursor.fetchone()
                    if row:
                        self.send_json_response({
                            "nom": row[0], 
                            "prenom": row[1], 
                            "classe": row[2], 
                            "role": row[3], 
                            "date_inscription": row[4],
                            "anciennete_annees": round(row[5], 2),
                            "plante_principale": row[6],
                            "nombre_interventions": row[7]
                        })
                    else:
                        self.send_error_response(404, "Member not found")

            elif path == '/GetHierarchie':
                cursor.execute("""
                    SELECT Nom, Prenom, Role_Association 
                    FROM membre 
                    WHERE Role_Association IN (
                        'President', 
                        'Vice President', 
                        'Secrétaire', 
                        'Trésorier', 
                        'Responsable Communication'
                    ) 
                    ORDER BY 
                        CASE Role_Association 
                            WHEN 'President' THEN 1 
                            WHEN 'Vice President' THEN 2 
                            WHEN 'Secrétaire' THEN 3 
                            WHEN 'Trésorier' THEN 4 
                            WHEN 'Responsable Communication' THEN 5 
                        END
                """)
                results = cursor.fetchall()
                self.send_json_response([{
                    "nom": row[0], "prenom": row[1], "role": row[2]
                } for row in results])

            elif path == '/GetAgendaClasse':
                classe = params.get('classe', [None])[0]
                if classe:
                    cursor.execute("""
                        SELECT Agenda 
                        FROM classe 
                        WHERE Nom_classe = ?
                    """, (classe,))
                    row = cursor.fetchone()
                    if row:
                        self.send_json_response({"agenda": row[0]})
                    else:
                        self.send_error_response(404, "Classe not found")

            else:
                self.send_error_response(404, "Endpoint not found")

            conn.close()

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            self.send_error_response(500, f"Database error: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            self.send_error_response(500, f"Unexpected server error: {str(e)}")

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def initialize_database():
    if os.path.exists(db_path):
        logging.info(f"Database already exists at {db_path}. Skipping initialization.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE classe (
       Nom_classe VARCHAR(3) PRIMARY KEY,
       Agenda VARCHAR(255)
    )
    """)
    
    cursor.execute("""
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
    )
    """)
    
    cursor.execute("""
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
    )
    """)
    
    cursor.execute("""
    CREATE TABLE intervention (
       Id INTEGER PRIMARY KEY AUTOINCREMENT,
       Date_intervention VARCHAR(20),
       Id_intervenant INTEGER DEFAULT NULL,
       Id_Plante INTEGER DEFAULT NULL,
       Note VARCHAR(250) DEFAULT '',
       FOREIGN KEY (Id_intervenant) REFERENCES membre(Id),
       FOREIGN KEY (Id_Plante) REFERENCES plante(Id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE rapport (
       Date_Rapport VARCHAR(7) PRIMARY KEY,
       Id_Plante INTEGER DEFAULT NULL,
       Histo_Hum VARCHAR(255) DEFAULT '',
       Histo_Temp VARCHAR(255) DEFAULT '',
       Histo_Lum VARCHAR(255) DEFAULT '',
       Histo_Photo VARCHAR(50),
       FOREIGN KEY (Id_Plante) REFERENCES plante(Id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE Cartes (
       Identifier VARCHAR(50) PRIMARY KEY,
       Plantes VARCHAR(20) DEFAULT ''
    )
    """)
    
    # Data de test
    
    cursor.execute("""
    INSERT INTO classe (Nom_classe, Agenda)
    VALUES
    ('2B', 'Agenda 2B'),
    ('3A', 'Agenda 3A'),
    ('3B', 'Agenda 3B'),
    ('4A', 'Agenda 4A'),
    ('4B', 'Agenda 4B'),
    ('5A', 'Agenda 5A'),
    ('5B', 'Agenda 5B'),
    ('6A', 'Agenda 6A'),
    ('6B', 'Agenda 6B')
    """)

    cursor.execute("""
    INSERT INTO membre (Cle_API, Nom, Prenom, Classe, Role_Association, Photo_profil, Date_inscription, Plante_Principale)
    VALUES
    ('APIKEY11', 'Wilson', 'Olivia', '2B', 'Responsable Communication', 'olivia.jpg', '2024-01-11', 11),
    ('APIKEY12', 'Taylor', 'Noah', '3A', 'Responsable Technique', 'noah.jpg', '2024-01-12', 12),
    ('APIKEY13', 'Anderson', 'Emma', '3B', 'Responsable Logistique', 'emma.jpg', '2024-01-13', 13),
    ('APIKEY14', 'Thomas', 'Liam', '4A', 'Responsable Événementiel', 'liam.jpg', '2024-01-14', 14),
    ('APIKEY15', 'Jackson', 'Ava', '4B', 'Responsable Formation', 'ava.jpg', '2024-01-15', 15),
    ('APIKEY16', 'White', 'Sophia', '2B', 'Volunteer', 'sophia_w.jpg', '2024-01-16', 16),
    ('APIKEY17', 'Harris', 'Mason', '3A', 'Volunteer', 'mason.jpg', '2024-01-17', 17),
    ('APIKEY18', 'Martin', 'Isabella', '3B', 'Volunteer', 'isabella.jpg', '2024-01-18', 18),
    ('APIKEY19', 'Thompson', 'James', '4A', 'Volunteer', 'james.jpg', '2024-01-19', 19),
    ('APIKEY20', 'Garcia', 'Charlotte', '4B', 'Volunteer', 'charlotte.jpg', '2024-01-20', 20),
    ('APIKEY21', 'Rodriguez', 'Daniel', '5A', 'Responsable Environnement', 'daniel.jpg', '2024-01-21', 21),
    ('APIKEY22', 'Lee', 'Aria', '5B', 'Responsable Recherche', 'aria.jpg', '2024-01-22', 22),
    ('APIKEY23', 'Chen', 'Ethan', '6A', 'Responsable Développement', 'ethan_chen.jpg', '2024-01-23', 23),
    ('APIKEY24', 'Kumar', 'Mia', '6B', 'Responsable Innovation', 'mia_kumar.jpg', '2024-01-24', 24),
    ('APIKEY25', 'Schmidt', 'Lucas', '5A', 'Volunteer', 'lucas_schmidt.jpg', '2024-01-25', 25),
    ('APIKEY26', 'Wang', 'Sophie', '5B', 'Volunteer', 'sophie_wang.jpg', '2024-01-26', 26),
    ('APIKEY27', 'Nguyen', 'Oliver', '6A', 'Volunteer', 'oliver_nguyen.jpg', '2024-01-27', 27),
    ('APIKEY28', 'Patel', 'Emma', '6B', 'Volunteer', 'emma_patel.jpg', '2024-01-28', 28),
    ('APIKEY29', 'Kim', 'Isabella', '5A', 'Volunteer', 'isabella_kim.jpg', '2024-01-29', 29),
    ('APIKEY30', 'Tanaka', 'Aiden', '5B', 'Volunteer', 'aiden_tanaka.jpg', '2024-01-30', 30)
    """)

    cursor.execute("""
    INSERT INTO plante (Nom, Type_Plante, Statut, Localisation, Humidite, Temperature, Luminosite, Derniere_Photo, Superviseur)
    VALUES
    ('Monstera', 'Indoor', 'normal', 'Serre', 55.0, 24.5, 280, 'monstera.jpg', 11),
    ('Sunflower', 'Outdoor', 'Flowering', 'Jardin', 35.0, 26.0, 600, 'sunflower.jpg', 12),
    ('Mint', 'Herb', 'Watered', 'Cuisine', 70.0, 23.5, 220, 'mint.jpg', 13),
    ('Bonsai', 'Indoor', 'Pruned', 'Atelier', 25.0, 22.0, 350, 'bonsai.jpg', 14),
    ('Venus Flytrap', 'Carnivorous', 'Feeding', 'Laboratoire', 80.0, 25.5, 400, 'venus.jpg', 15),
    ('Rosemary', 'Herb', 'Dry', 'Terrasse', 15.0, 27.0, 500, 'rosemary.jpg', 16),
    ('Jade Plant', 'Succulent', 'normal', 'Bureau', 20.0, 26.5, 450, 'jade.jpg', 17),
    ('Tulip', 'Flower', 'Budding', 'Jardin', 45.0, 21.0, 250, 'tulip.jpg', 18),
    ('Ficus', 'Indoor', 'normal', 'Couloir', 60.0, 23.0, 300, 'ficus.jpg', 19),
    ('Pitcher Plant', 'Carnivorous', 'Feeding', 'Laboratoire', 75.0, 24.0, 380, 'pitcher.jpg', 20),
    ('Mimosa', 'Sensitive', 'Sensitive', 'Laboratoire Etude', 70.0, 23.0, 280, 'mimosa.jpg', 29),
    ('Hibiscus', 'Flower', 'Flowering', 'Serre Tropicale', 65.0, 28.0, 550, 'hibiscus.jpg', 21),
    ('Sage', 'Herb', 'Harvesting', 'Jardin Aromatique', 30.0, 22.5, 400, 'sage.jpg', 22),
    ('Rubber Plant', 'Indoor', 'Growing', 'Bureau Principal', 50.0, 25.0, 320, 'rubber_plant.jpg', 23),
    ('Strawberry', 'Fruit', 'Fruiting', 'Serre de Culture', 40.0, 24.0, 480, 'strawberry.jpg', 24),
    ('Carnation', 'Flower', 'Budding', 'Jardin Floral', 55.0, 21.5, 300, 'carnation.jpg', 25),
    ('Basil Varietal', 'Herb', 'Experimental', 'Laboratoire de Botanique', 60.0, 26.0, 250, 'basil_var.jpg', 26),
    ('Dwarf Pomegranate', 'Fruit', 'normal', 'Terrasse', 35.0, 27.5, 500, 'pomegranate.jpg', 27),
    ('Succulent Garden', 'Succulent', 'Propagating', 'Atelier de Propagation', 20.0, 25.5, 450, 'succulent_garden.jpg', 28),
    ('Mimosa', 'Sensitive', 'Sensitive', 'Laboratoire Etude', 70.0, 23.0, 280, 'mimosa.jpg', 29),
    ('Chinese Lantern', 'Decorative', 'Fruiting', 'Serre Décorative', 45.0, 22.0, 380, 'lantern_plant.jpg', 30)
    """)

    cursor.execute("""
    INSERT INTO intervention (Date_intervention, Id_intervenant, Id_Plante, Note)
    VALUES
    ('2024-12-04', 11, 11, 'Arrosage et vérification de la santé générale'),
    ('2024-12-05', 12, 12, 'Taille et nutrition'),
    ('2024-12-06', 13, 13, 'Coupe et préparation pour séchage'),
    ('2024-12-07', 14, 14, 'Réévaluation des techniques de taille'),
    ('2024-12-08', 15, 15, 'Contrôle des proies et de environnement'),
    ('2024-12-09', 16, 16, 'Préparation pour la période sèche'),
    ('2024-12-10', 17, 17, 'Fertilisation et rotation'),
    ('2024-12-11', 18, 18, 'Préparation pour la floraison'),
    ('2024-12-12', 19, 19, 'Ajustement de exposition lumineuse'),
    ('2024-12-13', 20, 20, 'Suivi du cycle de nutrition'),
    ('2024-12-14', 21, 21, 'Évaluation du potentiel de floraison'),
    ('2024-12-15', 22, 22, 'Préparation de herbe pour séchage'),
    ('2024-12-16', 23, 23, 'Optimisation de la croissance'),
    ('2024-12-17', 24, 24, 'Suivi de la production de fruits'),
    ('2024-12-18', 25, 25, 'Préparation pour la période de floraison'),
    ('2024-12-19', 26, 26, 'Analyse des variants génétiques'),
    ('2024-12-20', 27, 27, 'Évaluation de la production fruitière'),
    ('2024-12-21', 28, 28, 'Techniques de propagation'),
    ('2024-12-22', 29, 29, 'Étude du comportement sensible'),
    ('2024-12-23', 30, 30, 'Documentation des caractéristiques décoratives')
    """)

    cursor.execute("""
    INSERT INTO rapport (Date_Rapport, Id_Plante, Histo_Hum, Histo_Temp, Histo_Lum, Histo_Photo)
    VALUES
    ('2024-04', 11, '55,56,57', '24,25,24', '280,290,270', 'monstera_hist.jpg'),
    ('2024-05', 12, '35,36,34', '26,27,26', '600,620,580', 'sunflower_hist.jpg'),
    ('2024-06', 13, '70,72,69', '23,24,23', '220,230,210', 'mint_hist.jpg'),
    ('2024-07', 14, '25,26,24', '22,23,22', '350,360,340', 'bonsai_hist.jpg'),
    ('2024-08', 15, '80,82,79', '25,26,25', '400,420,380', 'venus_hist.jpg'),
    ('2024-09', 21, '65,67,63', '28,29,27', '550,570,530', 'hibiscus_hist.jpg'),
    ('2024-10', 22, '30,32,28', '22,23,22', '400,420,380', 'sage_hist.jpg'),
    ('2024-11', 23, '50,52,48', '25,26,24', '320,340,300', 'rubber_plant_hist.jpg'),
    ('2024-12', 24, '40,42,38', '24,25,23', '480,500,460', 'strawberry_hist.jpg'),
    ('2024-13', 25, '55,57,53', '21,22,20', '300,320,280', 'carnation_hist.jpg')
    """)

    cursor.execute("""
    INSERT INTO Cartes (Identifier, Plantes)
    VALUES
    ('Card004', '11,12'),
    ('Card005', '13,14'),
    ('Card006', '15,16'),
    ('Card007', '17,18'),
    ('Card008', '19,20'),
    ('Card009', '21,22'),
    ('Card010', '23,24'),
    ('Card011', '25,26'),
    ('Card012', '27,28'),
    ('Card013', '29,30')
    """)
        
    conn.commit()
    conn.close()
    
    logging.info(f"Database initialized at {db_path}")

if __name__ == "__main__":
    initialize_database()
    try:
        with socketserver.TCPServer(("", PORT), PlantTrackingHandler) as httpd:
            logging.info(f"Server running on port {PORT}")
            logging.info("Available endpoints:")
            logging.info("- /GetPlantList")
            logging.info("- /GetPlantInfos?id={plantId}")
            logging.info("- /GetPlantBesoins?id={plantId}")
            logging.info("- /GetPlantInterventions?id_plante={plantId}")
            logging.info("- /GetInterventionInfos?id_intervention={interventionId}")
            logging.info("- /GetLatestIntervention?id_plante={plantId}")
            logging.info("- /GetAllRapports?id_plante={plantId}")
            logging.info("- /GetRapport?id_rapport={rapportId}")
            logging.info("- /GetLatestRapport?id_plante={plantId}")
            logging.info("- /GetListeMembre")
            logging.info("- /GetMembreInfos?id_membre={membreId}")
            logging.info("- /GetHierarchie")
            logging.info("- /GetAgendaClasse?classe={className}")
            logging.info("ESP endpoint: /sensor-data (POST)")
            
            httpd.serve_forever()
    except Exception as e:
        logging.critical(f"Error starting server: {e}")
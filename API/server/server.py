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
                # Check authentication using Cartes identifier
                cursor.execute("""
                    SELECT c.Plantes 
                    FROM Cartes c 
                    WHERE c.Identifier = ?
                """, (sensor_data['id'],))
                card_result = cursor.fetchone()

                if not card_result:
                    self.send_error_response(404, "No card found with this identifier")
                    return

                # Get the list of plant IDs associated with this card
                plant_ids = [int(pid) for pid in card_result[0].split(',')]

                # Update each plant associated with the card
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

                    # Handle ground humidity if available
                    ground_humidity = sensor_data.get('ground_humidity', [])
                    if isinstance(ground_humidity, list) and ground_humidity:
                        # If multiple humidity readings, use the first one
                        cursor.execute("""
                            UPDATE plante 
                            SET Humidite = ? 
                            WHERE Id = ?
                        """, (ground_humidity[0], plant_id))

                    # Handle image saving
                    if sensor_data.get('image'):
                        plant_photo_dir = os.path.join(photos_dir, str(plant_id))
                        os.makedirs(plant_photo_dir, exist_ok=True)
                        
                        image_path = os.path.join(
                            plant_photo_dir, 
                            f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        )
                        
                        with open(image_path, 'wb') as image_file:
                            image_file.write(base64.b64decode(sensor_data['image']))

                    # Update monthly report
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
    
    cursor.execute("INSERT INTO classe (Nom_classe, Agenda) VALUES ('DE', 'Agenda DEFAULT')")
    cursor.execute("""
    INSERT INTO classe (Nom_classe, Agenda)
    VALUES
    ('1A', 'Agenda 1A'),
    ('1B', 'Agenda 1B'),
    ('2A', 'Agenda 2A')
    """)
    
    cursor.execute("""
    INSERT INTO membre (Cle_API, Nom, Prenom, Classe, Role_Association, Photo_profil, Date_inscription, Plante_Principale) 
    VALUES ('DEFAULT_API_KEY', 'Everyone', 'Everyone', 'DE', 'Everyone', 'everyone', '2024-01-01', NULL)
    """)
    
    cursor.execute("""
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
    ('APIKEY10', 'Clark', 'Lucas', '1A', 'Volunteer', 'lucas.jpg', '2024-01-10', 10)
    """)
    
    cursor.execute("""
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
    ('Palm', 'Outdoor', 'normal', 'Localisation', 40.0, 28.0, 500, 'palm.jpg', 3)
    """)
    
    cursor.execute("""
    INSERT INTO intervention (Date_intervention, Id_intervenant, Id_Plante, Note)
    VALUES
    ('2024-12-01', 1, 1, 'Lorem Ipsum Dolor Sit Amet'),
    ('2024-12-02', 2, 2, 'Lorem Ipsum Dolor Sit Amet'),
    ('2024-12-03', 3, 3, 'Lorem Ipsum Dolor Sit Amet')
    """)
    
    cursor.execute("""
    INSERT INTO rapport (Date_Rapport, Id_Plante, Histo_Hum, Histo_Temp, Histo_Lum, Histo_Photo)
    VALUES
    ('2024-01', 1, '45,46,47', '22,23,22', '300,310,320', 'fern_hist.jpg'),
    ('2024-02', 2, '15,16,14', '27,28,27', '500,520,510', 'cactus_hist.jpg'),
    ('2024-03', 3, '60,62,59', '25,26,25', '200,210,220', 'basil_hist.jpg')
    """)
    
    cursor.execute("""
    INSERT INTO Cartes (Identifier, Plantes)
    VALUES
    ('Card001', '1,2'),
    ('Card002', '3'),
    ('Card003', '2,3')
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
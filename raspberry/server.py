import os
import http.server
import socketserver
import json
import logging
import sqlite3

PORT = 5000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "plant_tracking.db")

def initialize_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        idmember INTEGER PRIMARY KEY AUTOINCREMENT,
        familyname VARCHAR(30) NOT NULL,
        name VARCHAR(20) NOT NULL,
        class VARCHAR(2) NOT NULL,
        role VARCHAR(15),
        dateinscription DATE NOT NULL,
        givenplant VARCHAR(30),
        FOREIGN KEY(class) REFERENCES classes(nomclasse)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plant (
        idplant INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50),
        especes VARCHAR(50),
        status VARCHAR(20),
        location VARCHAR(50),
        humidity FLOAT,
        temperature FLOAT,
        luminosity FLOAT,
        owner VARCHAR(50),
        FOREIGN KEY(owner) REFERENCES members(idmember)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rapport ( 
        moisrapport TEXT PRIMARY KEY,
        humidity FLOAT,
        temperature FLOAT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        nomclasse VARCHAR(3) PRIMARY KEY
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classe (
        idclass VARCHAR(3) PRIMARY KEY,
        membername VARCHAR(15),
        numberstudent INTEGER
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS INTERVENTION (
        idintervention INTEGER PRIMARY KEY AUTOINCREMENT,
        plant VARCHAR(30),
        intervenant VARCHAR(70),
        mission VARCHAR(50),
        date DATE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS identifiers (
        identifier VARCHAR(24) PRIMARY KEY,
        plantes TEXT
    )
    """)
    conn.commit()
    conn.close()

class SensorDataHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        logging.info(f"POST request received from {self.client_address}")
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            sensor_data = json.loads(post_data.decode('utf-8'))
            logging.info(f"Received Data: {json.dumps(sensor_data, indent=4)}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        except json.JSONDecodeError:
            logging.error("Error decoding JSON")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Invalid JSON"}')
        except Exception as e:
            logging.error(f"Server error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Server error"}')

if __name__ == "__main__":
    initialize_database()
    try:
        with socketserver.TCPServer(("", PORT), SensorDataHandler) as httpd:
            logging.info(f"Server running on port {PORT}")
            logging.info("Press Ctrl+C to stop the server.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down the server.")
    except Exception as e:
        logging.critical(f"Error starting the server: {e}")

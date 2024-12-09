import http.server
import socketserver
import json
import logging

PORT = 5000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

class SensorDataHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        logging.info(f" POST: {self.client_address}")
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            sensor_data = json.loads(post_data.decode('utf-8'))
            logging.info(f"Data: {json.dumps(sensor_data, indent=4)}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        
        except json.JSONDecodeError:
            logging.error("Error JSON")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Error JSON"}')
        except Exception as e:
            logging.error(f"Server Error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Server error"}')


try:
    with socketserver.TCPServer(("", PORT), SensorDataHandler) as httpd:
        logging.info(f"Port: {PORT}")
        logging.info("Press Ctrl+C to stop the server.")
        httpd.serve_forever()
except KeyboardInterrupt:
    logging.info("Server downed")
except Exception as e:
    logging.critical(f"Start error: {e}")

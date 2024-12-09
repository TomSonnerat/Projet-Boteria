import http.server
import socketserver
import json

PORT = 5000

class SensorDataHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            sensor_data = json.loads(post_data.decode('utf-8'))
            print("Received data:")
            print(json.dumps(sensor_data, indent=4))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        except json.JSONDecodeError:

            print("Invalid JSON received!")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Invalid JSON"}')

# Create the server
with socketserver.TCPServer(("", PORT), SensorDataHandler) as httpd:
    print(f"Serving on port {PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the server.")
        httpd.server_close()

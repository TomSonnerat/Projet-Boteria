from flask import Flask, request, jsonify
import os

app = Flask(__name__)

SAVE_FOLDER = "received_data"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        image = request.data
        if image:
            image_path = os.path.join(SAVE_FOLDER, "image.jpg")
            with open(image_path, "wb") as img_file:
                img_file.write(image)
            print(f"Image received and saved to {image_path}")
            return jsonify({"status": "success", "message": "Image received"}), 200
        else:
            return jsonify({"status": "error", "message": "No image"}), 400
    except Exception as e:
        print(f"Error receiving image: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    try:
        sensor_data = request.json
        if sensor_data:
            print("Sensor data received:")
            for key, value in sensor_data.items():
                print(f"  {key}: {value}")
            return jsonify({"status": "success", "message": "Sensor data received"}), 200
        else:
            return jsonify({"status": "error", "message": "No senso"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


app.run(host='192.168.1.26', port=5000)
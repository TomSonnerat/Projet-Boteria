import requests
import json

SERVER_URL = "http://0.0.0.0:5000/sensor-data"

def send_custom_data():
    data = {
        "id": "test1234567890abcdef1234",
        "temperature": 23.7,
        "humidity": 50.4,
        "light": 800,
        "ground_humidity": [45, 50, 40],
        "image": "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
    }

    try:
        response = requests.post(SERVER_URL, json=data)
        print("Response:")
        print(response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("Error: ", e)

if __name__ == "__main__":
    send_custom_data()

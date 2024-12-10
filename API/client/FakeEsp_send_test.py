import requests
import base64
import os
import random
import json

ServerUrl = "http://localhost:5000/sensor-data"
TestApiKeys = [
    "Card001",
    "Card002",
]

def GenerateTestImage():
    from PIL import Image, ImageDraw
    import io

    Image = Image.new('RGB', (100, 100), color='white')
    Draw = ImageDraw.Draw(Image)
    
    Draw.rectangle([20, 20, 80, 80], 
                   fill=(random.randint(0, 255), 
                         random.randint(0, 255), 
                         random.randint(0, 255)))
    
    Buffer = io.BytesIO()
    Image.save(Buffer, format='PNG')
    
    return base64.b64encode(Buffer.getvalue()).decode('utf-8')

def TestSensorData(ApiKey):
    TestData = {
        "id": ApiKey,
        "temperature": round(random.uniform(20.0, 30.0), 1),
        "light": random.randint(100, 1000),
        "ground_humidity": [
            round(random.uniform(10.0, 80.0), 1),
            round(random.uniform(10.0, 80.0), 1),
            round(random.uniform(10.0, 80.0), 1)
        ],
        "image": GenerateTestImage()
    }

    try:
        Response = requests.post(ServerUrl, json=TestData)
        
        print(f"\nTesting with API Key: {ApiKey}")
        print("Request Data:")
        print(json.dumps({
            "temperature": TestData["temperature"],
            "light": TestData["light"],
            "ground_humidity": TestData["ground_humidity"]
        }, indent=2))
        
        print("\nResponse:")
        print(f"Status Code: {Response.status_code}")
        
        try:
            ResponseJson = Response.json()
            print("Response Body:")
            print(json.dumps(ResponseJson, indent=2))
        except ValueError:
            print("Response is not JSON")
            print(Response.text)
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

def RunComprehensiveTests():
    for ApiKey in TestApiKeys:
        TestSensorData(ApiKey)
        print("\n" + "-"*40 + "\n")

def Main():
    try:
        import requests
        import PIL.Image
    except ImportError:
        print("Please install required libraries:")
        print("pip install requests Pillow")
        return

    RunComprehensiveTests()

if __name__ == "__main__":
    Main()
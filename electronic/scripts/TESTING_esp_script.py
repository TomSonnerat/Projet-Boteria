import network
import urequests
import machine
import base64
import random
import esp32_cam

WiFiSSID = "SSID"
WiFiPassword = "12345"

ReceiverIP = "192.168.1.26"
ReceiverPort = 5000

EmulateErrors = False
ErrorProbability = 0.2
SleepMs = 3600000

CameraPins = {
    "PWDN": 32,
    "RESET": -1,
    "XCLK": 0,
    "SIOD": 26,
    "SIOC": 27,
    "Y9": 35,
    "Y8": 34,
    "Y7": 39,
    "Y6": 36,
    "Y5": 21,
    "Y4": 19,
    "Y3": 18,
    "Y2": 5,
    "VSYNC": 25,
    "HREF": 23,
    "PCLK": 22
}

class SensorNode:
    def __init__(self):
        self.wifi = network.WLAN(network.STA_IF)
        
        self.camera = esp32_cam.Camera(
            pin_pwdn=CameraPins["PWDN"],
            pin_reset=CameraPins["RESET"], 
            pin_xclk=CameraPins["XCLK"],
            pin_sda=CameraPins["SIOD"],
            pin_scl=CameraPins["SIOC"],
            pin_d0=CameraPins["Y2"],
            pin_d1=CameraPins["Y3"],
            pin_d2=CameraPins["Y4"],
            pin_d3=CameraPins["Y5"],
            pin_d4=CameraPins["Y6"],
            pin_d5=CameraPins["Y7"],
            pin_d6=CameraPins["Y8"],
            pin_d7=CameraPins["Y9"],
            pin_vsync=CameraPins["VSYNC"],
            pin_href=CameraPins["HREF"],
            pin_pclk=CameraPins["PCLK"],
            format=esp32_cam.JPEG,
            framesize=esp32_cam.FRAME_QVGA,
            jpeg_quality=10
        )
    
    def _simulate_sensor_error(self):
        return EmulateErrors and random.random() < ErrorProbability
    
    def connectWiFi(self):
        if not self.wifi.isconnected():
            self.wifi.active(True)
            self.wifi.connect(WiFiSSID, WiFiPassword)
            
            timeout = 10
            while not self.wifi.isconnected() and timeout > 0:
                machine.time_pulse_us(1)
                timeout -= 1
    
    def readDht11Temp(self):
        if self._simulate_sensor_error():
            return None
        
        return round(random.uniform(15, 35), 1)
    
    def readDht11Humidity(self):
        if self._simulate_sensor_error():
            return None
        
        return round(random.uniform(10, 90), 1)
    
    def readLightIntensity(self):
        if self._simulate_sensor_error():
            return None
        
        return round(random.uniform(0, 1000), 1)
    
    def readGroundHumidity(self):
        ground_humidity_readings = []
        
        for _ in range(3):
            if self._simulate_sensor_error():
                ground_humidity_readings.append(None)
            else:
                ground_humidity_readings.append(round(random.uniform(0, 100), 1))
        
        return ground_humidity_readings
    
    def captureImage(self):
        try:
            self.camera.init()
            frame = self.camera.capture()
            if frame:
                return base64.b64encode(frame).decode('utf-8')
            return None
        except Exception:
            return None
    
    def sendSensorData(self):
        temperature = self.readDht11Temp()
        humidity = self.readDht11Humidity()
        light = self.readLightIntensity()
        ground_humidity = self.readGroundHumidity()
        
        image_base64 = self.captureImage()
        
        sensorData = {
            "temperature": temperature,
            "humidity": humidity,
            "light": light,
            "ground_humidity": ground_humidity,
            "image": image_base64
        }
        
        try:
            if self.wifi.isconnected():
                url = f"http://{ReceiverIP}:{ReceiverPort}/sensor-data"
                urequests.post(url, json=sensorData)
        except Exception:
            pass
    
    def deepSleep(self):
        machine.deepsleep(SleepMs)

sensorNode = SensorNode()

while True:
    sensorNode.connectWiFi()
    sensorNode.sendSensorData()
    sensorNode.deepSleep()
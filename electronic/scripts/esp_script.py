import network
import urequests
import machine
import sdcard
import uos
from machine import I2C, Pin, ADC
import dht
import esp32_cam

WiFiSSID = "SSID"
WiFiPassword = "12345"

ReceiverIP = "192.168.1.26"
ReceiverPort = 5000

DhtPin = 14
LightSda = 21
LightScl = 22
GroundHumidityPins = [33, 32, 35]
PowerManagementPin = 27

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
        
        self.dhtSensor = dht.DHT11(machine.Pin(DhtPin))
        
        self.i2c = I2C(0, scl=Pin(LightScl), sda=Pin(LightSda))
        
        self.groundHumiditySensors = [ADC(Pin(pin)) for pin in GroundHumidityPins]
        for sensor in self.groundHumiditySensors:
            sensor.atten(ADC.ATTN_11DB)
        
        self.powerPin = Pin(PowerManagementPin, Pin.OUT)
        
        self.logCounter = 0
        
        try:
            self.sd = sdcard.SDCard(machine.SPI(1), machine.Pin(5))
            uos.mount(self.sd, '/sd')
            uos.mkdir('/sd/sensor_logs')
        except Exception:
            self.sd = None
        
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
    
    def connectWiFi(self):
        if not self.wifi.isconnected():
            self.wifi.active(True)
            self.wifi.connect(WiFiSSID, WiFiPassword)
            
            timeout = 10
            while not self.wifi.isconnected() and timeout > 0:
                machine.time_pulse_us(1)
                timeout -= 1
    
    def readDht11Temp(self):
        try:
            self.dhtSensor.measure()
            return self.dhtSensor.temperature()
        except Exception:
            return None
    
    def readDht11Humidity(self):
        try:
            self.dhtSensor.measure()
            return self.dhtSensor.humidity()
        except Exception:
            return None
    
    def readLightIntensity(self):
        return None
    
    def readGroundHumidity(self):
        try:
            return [sensor.read() for sensor in self.groundHumiditySensors]
        except Exception:
            return [None] * len(self.groundHumiditySensors)
    
    def captureImage(self):
        try:
            self.camera.init()
            frame = self.camera.capture()
            
            if frame:
                url = f"http://{ReceiverIP}:{ReceiverPort}/upload"
                headers = {"Content-Type": "image/jpeg"}
                urequests.post(url, data=frame, headers=headers)
            
            return frame
        except Exception:
            return None
    
    def sendSensorData(self):
        self.powerPin.value(1)
        
        sensorData = {
            "temperature": self.readDht11Temp(),
            "humidity": self.readDht11Humidity(),
            "light": self.readLightIntensity(),
            "ground_humidity": self.readGroundHumidity()
        }
        
        try:
            if self.wifi.isconnected():
                url = f"http://{ReceiverIP}:{ReceiverPort}/sensor-data"
                urequests.post(url, json=sensorData)
            else:
                if self.sd:
                    self.logCounter += 1
                    filename = f"/sd/sensor_logs/sensor_data_{self.logCounter}.txt"
                    
                    with open(filename, 'w') as f:
                        f.write(str(sensorData))
        except Exception:
            pass
        
        self.powerPin.value(0)
    
    def deepSleep(self, sleepMs=60000):
        machine.deepsleep(sleepMs)

sensorNode = SensorNode()

while True:
    sensorNode.connectWiFi()
    sensorNode.captureImage()
    sensorNode.sendSensorData()
    sensorNode.deepSleep()
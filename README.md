# Projet Boteria 🌱

---

## Presentation

**Projet Boteria** is a plant tracking system designed to monitor and collect data about plants' environment. This project combines hardware and software to track various parameters such as humidity, luminosity, acidity, and more, sending data to an HTTP endpoint every hour.

---

## Features

- **Data Collection**
    - Soil humidity (3 sensors)
    - Temperature and humidity (DHT11)
    - Luminosity (BH1750)
    - Plant photo capture (ESP32-CAM)
- **Data Management**
    - Hourly data collection
    - Data transmission to a Raspberry Pi for further processing and storage
    - Accessible API for data retrieval

---

## Project Structure

```
plaintext
Copier le code
├── Hardware/
│   ├── ESP32-CAM/
│   ├── Sensors/
│   ├── Voltage-Regulation/
├── RaspberryPi/
│   ├── Data-Collection/
│   ├── Database/
│   ├── API/
├── Documentation/
│   ├── Schematics/
│   ├── Setup-Instructions.md
├── README.md
```

---

### Current Focus

The initial phase of the project emphasizes the **hardware aspect** to ensure robust and accurate data collection.

---

## Hardware Components

- **ESP32-CAM Module**
    - Collects and sends data to the Raspberry Pi.
    - Takes periodic photos of plants.
- **Sensors**
    - **BH1750**: Measures ambient light.
    - **DHT11**: Captures temperature and humidity.
    - **3 Soil Moisture Sensors**: Tracks soil humidity levels.
- **Power Supply**
    - Powered by a 3xAA battery pack with an AMS1117 voltage regulator (4.5V to 3.3V).

---

## Software

- **Python** for backend data processing and API development.
- **Thonny IDE and MicroPython** for ESP32-CAM module programming.

---

## Installation

1. Hardware Setup

- Assemble the sensors and ESP32-CAM module.
- Connect the power supply via the voltage regulator.
- Ensure all components are properly wired and operational.

2. Software Setup

- Clone the Repository

```bash
bash
Copier le code
git clone https://github.com/TomSonnerat/Projet-Boteria.git
cd Projet-Boteria

```

- Install Python Requirements

Ensure you have Python 3.9 or higher installed. Then, install the required Python packages:

```bash
pip install -r requirements.txt
```

### Thonny IDE

1. Install the Thonny IDE.
2. Add the ESP32 board to the Thonny by following this guide. in hardware/guide.md

## License

This project is licensed under the MIT License.
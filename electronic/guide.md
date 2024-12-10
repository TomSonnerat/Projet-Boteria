# Guide

Welcome to this guide for the hardware setup.

---

### Construct hardware

- Get the required hardware thanks to the hardware/component-list.pdf
- For estimating your battery life, you can use the hardware/battery-calculator.py
- Assemble the hardware part thanks to the electronic-schema.png

### Install MicroPython

This project is based on the MicroPython firmware:

- Download the [Micropython Camera Driver for ESP32-CAM](https://github.com/lemariva/micropython-camera-driver)
- Download Thonny IDE
- Install esptool

```sql
pip3 install esptool
```

- Go to the Micropython firmware folder

```sql
cd Path/To/Drivers/firmware
```

- Flash your ESP drivers and install the new one (replace path with yours and select the right port)

```sql
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20210902-v1.17.bin
```

Select the right board in Thonny IDE.

For full details, check this [lib](https://lemariva.com/blog/2022/01/micropython-upgraded-support-cameras-m5camera-esp32-cam-etc)

---

### Testing

- You can test the connection between the ESP32 with the server thanks to the scripts/TESTING_esp_script.py script.
- You can emulate data sending with the ESP32-CAM to the server using ../API/FakeEsp_send_test.py
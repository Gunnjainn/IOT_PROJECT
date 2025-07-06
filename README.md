# Home Automation and real-time energy monitoring system (ESP32 + Raspberry Pi)

This is a lightweight IoT system using ESP32 and Raspberry Pi for real-time environmental monitoring and automation. It consists of:

- An **ESP32 node** that reads:
  - 🌡️ Temperature & humidity from a DHT22 sensor
  - 🎤 Sound level from an analog sound sensor
  - 🔘 Button press state
  - 📡 Publishes the data via MQTT

- A **Raspberry Pi subscriber** that:
  - 📟 Displays data on a 16x2 I2C LCD
  - 💡 Controls LEDs based on temperature, button state, and time
  - ⚠️ Triggers alerts during night-time sound events
  - ☁️ Uploads readings to ThingSpeak
  - 🔋 Tracks fan energy usage

---

## 📂 Files

| File                    | Description                              |
|-------------------------|------------------------------------------|
| `esp32_sensor_node.ino` | ESP32 Arduino code (MQTT publisher)      |
| `rpi_mqtt_receiver.py`  | Python script for Raspberry Pi (MQTT subscriber, logic, cloud upload) |
| `requirements.txt`      | Python dependencies for Raspberry Pi     |

---

## ✅ How to Run

### 1. ESP32 Setup

- Upload `esp32_sensor_node.ino` via Arduino IDE
- Libraries needed:
  - `WiFi.h`
  - `PubSubClient.h`
  - `DHT.h`
- Update Wi-Fi credentials and MQTT broker IP:
  ```cpp
  const char* ssid = "your_wifi_ssid";
  const char* password = "your_wifi_password";
  const char* mqtt_server = "raspberry_pi_ip_address";

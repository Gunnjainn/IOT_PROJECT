import json
import time
import requests
from gpiozero import LED
from RPLCD.i2c import CharLCD
import paho.mqtt.client as mqtt
from datetime import datetime
# Devices setup
projector_led = LED(17)           # Fan indicator LED
alert_led = LED(27)         # Alert LED for motion/sound at night
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)
# ThingSpeak setup
THINGSPEAK_API_KEY = "GET5PKDSNMIJ1DM7"
THINGSPEAK_URL = "https://api.thingspeak.com/update"
# Fan energy monitoring variables
fan_power_watts = 25
energy_wh = 0
last_time = time.time()
# MQTT settings
MQTT_BROKER = "localhost"
MQTT_TOPIC = "iot/sensordata"
def display_message(line1, line2, delay=2):
    lcd.clear()
    lcd.write_string(line1)
    lcd.crlf()
    lcd.write_string(line2)
    time.sleep(delay)
def calculate_fan_speed(temp):
    if temp < 25:
        return 0
    elif 25 <= temp < 30:
        return 50
    else:
        return 100
def is_night():
    current_hour = datetime.now().hour
    return current_hour >= 20 or current_hour < 6  # Night: 8 PM – 6 AM
def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(MQTT_TOPIC)
def on_message(client, userdata, msg):
    global energy_wh, last_time
    try:
        payload = json.loads(msg.payload.decode())
        print("Received:", payload)
        temperature = float(payload.get("temperature", 0))
        humidity = float(payload.get("humidity", 0))
        sound = int(payload.get("sound", 0))
        button = int(payload.get("button", 1))  # 0 = pressed
        # Fan logic
        fan_speed = calculate_fan_speed(temperature)
        projector_led.on() if fan_speed > 0 else projector_led.off()
        # Energy tracking
        current_time = time.time()
        elapsed_time = current_time - last_time
        last_time = current_time
        if fan_speed > 0:
            energy_used = (fan_power_watts * elapsed_time) / 3600
            energy_wh += energy_used
        # Anti-theft alert via LED
        if(sound > 50):  # Adjust threshold if needed
            print("Alert: Motion or Sound detected at night!")
            for _ in range(3):  # Blink alert LED 3 times
                alert_led.on()
                time.sleep(0.5)
                alert_led.off()
                time.sleep(0.5)
            display_message("ALERT: Night", "Motion/Sound!")
        # Button press logic
        if button == 0:
            print("Button pressed: Projector ON, Lights OFF")
            projector_led.off()
            display_message("Projector ON", "Lights OFF", delay=2)
        # LCD display
        line1 = f"T:{temperature:.1f}C F:{fan_speed}%"
        line2 = f"S:{sound}"
        display_message(line1, line2, delay=2)
        # Send to ThingSpeak
        payload = {
            "api_key": THINGSPEAK_API_KEY,
            "field1": temperature,
            "field2": humidity,
            "field3": sound,
            "field5": button,
            "field6": fan_speed,
            "field7": round(energy_wh, 4)
        }
        r = requests.post(THINGSPEAK_URL, params=payload)
        if r.status_code == 200:
            print("Data sent to ThingSpeak.")
        else:
            print("ThingSpeak error:", r.text)
    except Exception as e:
        print("Error:", e)
# MQTT setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Exiting...")
    lcd.clear()
    projector_led.off()
    alert_led.off()

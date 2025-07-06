#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
// Replace with your Wi-Fi and MQTT credentials
const char* ssid = "Aditya";
const char* password = "sharma123";
const char* mqtt_server = "192.168.41.195";  // Replace with RPi IP
WiFiClient espClient;
PubSubClient client(espClient);
// DHT sensor config
#define DHTPIN 21    // Digital pin for DHT
#define DHTTYPE DHT22  // Or DHT11
DHT dht(DHTPIN, DHTTYPE);
// Other sensors
#define SOUND_PIN 3     // Analog pin
#define BUTTON_PIN 18    // Digital pin
void setup_wifi() {
  delay(10);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
}
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}
void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int soundValue = analogRead(SOUND_PIN);
  int buttonState = digitalRead(BUTTON_PIN); // 0 = pressed
  // Check if DHT read was successful
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  // Prepare payload
  String payload = "{";
  payload += "\"temperature\":" + String(temperature) + ",";
  payload += "\"humidity\":" + String(humidity) + ",";
  payload += "\"sound\":" + String(soundValue) + ",";
  payload += "\"button\":" + String(buttonState == LOW ? 1 : 0);
  payload += "}";
  Serial.println("Publishing payload:");
  Serial.println(payload);
  client.publish("iot/sensordata", payload.c_str());
  delay(2000); // Delay between readings
}

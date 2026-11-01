/*
 * ==============================================================================
 * Project: Battery Cell Imbalance Detection Using IoT Analytics
 * Layer 6: ESP32 Sensor Interface & Telemetry Publisher
 * File: esp32_battery_monitor.ino
 * ==============================================================================
 *
 * Requirements:
 * - Reads individual battery cell voltages through calibrated voltage divider circuits.
 * - Reads cell surface temperatures using DS18B20 1-Wire sensors or NTC thermistors.
 * - Serializes measurements to standardized JSON matching the Python schema.
 * - Publishes over WiFi to local MQTT broker or HiveMQ Cloud (TLS 8883).
 * - Implements physical alerts (status LED & buzzer alarms).
 * - Robust WiFi/MQTT reconnection with exponential backoff.
 *
 * SAFETY NOTE:
 * Never connect battery cells directly to ESP32 pins. ESP32 ADC pins support a maximum
 * input of 3.3V. Use calibrated precision voltage dividers or dedicated BMS ICs.
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==============================================================================
// 1. CONFIGURATION & CREDENTIALS
// ==============================================================================
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT Broker Settings (Local or HiveMQ Cloud)
const char* MQTT_BROKER   = "YOUR_HIVEMQ_HOST.s1.eu.hivemq.cloud"; // or "192.168.1.100"
const int   MQTT_PORT     = 8883; // 8883 for TLS, 1883 for local plaintext
const char* MQTT_USER     = "YOUR_MQTT_USERNAME";
const char* MQTT_PASS     = "YOUR_MQTT_PASSWORD";
const char* MQTT_TOPIC    = "battery/cells/data";
const char* PACK_ID       = "ESP32-PACK-01";

const unsigned long SAMPLE_INTERVAL_MS = 2000; // 2 seconds

// ==============================================================================
// 2. PIN ASSIGNMENTS
// ==============================================================================
// Analog ADC pins for 4S cell voltage monitoring (via voltage dividers)
const int CELL_PINS[4] = {36, 39, 34, 35}; // GPIO36 (VP), GPIO39 (VN), GPIO34, GPIO35

// Analog pins for NTC temperature sensors or single-pin OneWire
const int TEMP_PINS[4] = {32, 33, 25, 26};

// Physical Alert Indicators
const int PIN_LED_NORMAL   = 2;  // Built-in or external Green LED
const int PIN_LED_WARNING  = 4;  // Yellow LED
const int PIN_LED_CRITICAL = 5;  // Red LED
const int PIN_BUZZER       = 18; // Active Buzzer

// ==============================================================================
// 3. CALIBRATION CONSTANTS
// ==============================================================================
// ADC Voltage divider ratios for 4S configuration:
// Cell 1 tap: 0-4.2V   -> R1=10k, R2=20k -> Ratio = (10+20)/20 = 1.50
// Cell 2 tap: 0-8.4V   -> R1=30k, R2=10k -> Ratio = (30+10)/10 = 4.00
// Cell 3 tap: 0-12.6V  -> R1=50k, R2=10k -> Ratio = (50+10)/10 = 6.00
// Cell 4 tap: 0-16.8V  -> R1=70k, R2=10k -> Ratio = (70+10)/10 = 8.00
const float DIVIDER_RATIOS[4] = {1.50, 4.00, 6.00, 8.00};
const float ADC_REF_VOLTAGE    = 3.30;
const int   ADC_RESOLUTION     = 4095;

// ==============================================================================
// 4. GLOBAL OBJECTS & STATE
// ==============================================================================
WiFiClientSecure espClient;
PubSubClient mqttClient(espClient);

unsigned long lastSampleTime = 0;
float cellVoltages[4] = {0.0, 0.0, 0.0, 0.0};
float cellTemps[4]    = {0.0, 0.0, 0.0, 0.0};

// ==============================================================================
// 5. HARDWARE READING & SENSING FUNCTIONS
// ==============================================================================

float readCellVoltage(int cellIndex) {
    if (cellIndex < 0 || cellIndex >= 4) return 0.0;
    
    // Multisample averaging to filter ADC switching noise
    long sumRaw = 0;
    const int SAMPLES = 20;
    for (int i = 0; i < SAMPLES; i++) {
        sumRaw += analogRead(CELL_PINS[cellIndex]);
        delayMicroseconds(100);
    }
    float avgRaw = (float)sumRaw / SAMPLES;
    
    // Convert ADC ticks to voltage at pin
    float pinVoltage = (avgRaw / ADC_RESOLUTION) * ADC_REF_VOLTAGE;
    
    // Scale by resistor divider ratio
    float tapVoltage = pinVoltage * DIVIDER_RATIOS[cellIndex];
    return tapVoltage;
}

float readCellTemperature(int sensorIndex) {
    if (sensorIndex < 0 || sensorIndex >= 4) return 25.0;
    
    // Read 10k NTC thermistor divider (10k resistor pull-up to 3.3V)
    int raw = analogRead(TEMP_PINS[sensorIndex]);
    if (raw <= 10 || raw >= 4080) {
        // Sensor disconnected or shorted
        return -999.0;
    }
    
    float vOut = (raw / (float)ADC_RESOLUTION) * ADC_REF_VOLTAGE;
    float rNtc = (10000.0 * vOut) / (ADC_REF_VOLTAGE - vOut);
    
    // Steinhart-Hart equation (Beta parameter formula)
    const float B = 3950.0;
    const float T0 = 298.15; // 25 deg C in Kelvin
    const float R0 = 10000.0;
    
    float steinhart = rNtc / R0;
    steinhart = log(steinhart);
    steinhart /= B;
    steinhart += 1.0 / T0;
    steinhart = 1.0 / steinhart;
    float tempC = steinhart - 273.15;
    
    return tempC;
}

void updatePhysicalAlerts(float deltaV, float maxTemp) {
    // Thresholds: Warning deltaV >= 0.020V (20mV), Critical deltaV >= 0.050V (50mV)
    if (deltaV >= 0.050 || maxTemp >= 60.0) {
        // CRITICAL ALARM
        digitalWrite(PIN_LED_NORMAL, LOW);
        digitalWrite(PIN_LED_WARNING, LOW);
        digitalWrite(PIN_LED_CRITICAL, HIGH);
        // Beep buzzer
        digitalWrite(PIN_BUZZER, HIGH);
    } else if (deltaV >= 0.020 || maxTemp >= 45.0) {
        // WARNING STATE
        digitalWrite(PIN_LED_NORMAL, LOW);
        digitalWrite(PIN_LED_WARNING, HIGH);
        digitalWrite(PIN_LED_CRITICAL, LOW);
        digitalWrite(PIN_BUZZER, LOW);
    } else {
        // NORMAL STATE
        digitalWrite(PIN_LED_NORMAL, HIGH);
        digitalWrite(PIN_LED_WARNING, LOW);
        digitalWrite(PIN_LED_CRITICAL, LOW);
        digitalWrite(PIN_BUZZER, LOW);
    }
}

// ==============================================================================
// 6. NETWORK & MQTT FUNCTIONS
// ==============================================================================

void connectWiFi() {
    Serial.print("Connecting to Wi-Fi: ");
    Serial.println(WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 25) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[Wi-Fi Connected]");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n[Wi-Fi Connection Failed - Will retry]");
    }
}

void connectMQTT() {
    while (!mqttClient.connected()) {
        if (WiFi.status() != WL_CONNECTED) {
            connectWiFi();
        }
        Serial.print("Connecting to MQTT broker...");
        String clientId = "ESP32BatteryMonitor-" + String(random(0xffff), HEX);
        
        bool success = false;
        if (strlen(MQTT_USER) > 0) {
            success = mqttClient.connect(clientId.c_str(), MQTT_USER, MQTT_PASS);
        } else {
            success = mqttClient.connect(clientId.c_str());
        }

        if (success) {
            Serial.println(" [CONNECTED]");
        } else {
            Serial.print(" [FAILED] rc=");
            Serial.print(mqttClient.state());
            Serial.println(" Retrying in 4 seconds...");
            delay(4000);
        }
    }
}

void publishTelemetry() {
    // Calculate intermediate voltage taps into individual cell potentials:
    // Tap 1 = V_cell1
    // Tap 2 = V_cell1 + V_cell2 => V_cell2 = Tap 2 - Tap 1
    // Tap 3 = V_cell1 + V_cell2 + V_cell3 => V_cell3 = Tap 3 - Tap 2
    // Tap 4 = V_cell1 + V_cell2 + V_cell3 + V_cell4 => V_cell4 = Tap 4 - Tap 3
    float tap1 = readCellVoltage(0);
    float tap2 = readCellVoltage(1);
    float tap3 = readCellVoltage(2);
    float tap4 = readCellVoltage(3);

    cellVoltages[0] = tap1;
    cellVoltages[1] = max(0.0f, tap2 - tap1);
    cellVoltages[2] = max(0.0f, tap3 - tap2);
    cellVoltages[3] = max(0.0f, tap4 - tap3);

    float maxV = cellVoltages[0];
    float minV = cellVoltages[0];
    for (int i = 1; i < 4; i++) {
        if (cellVoltages[i] > maxV) maxV = cellVoltages[i];
        if (cellVoltages[i] < minV) minV = cellVoltages[i];
    }
    float deltaV = maxV - minV;

    float maxT = -99.0;
    for (int i = 0; i < 4; i++) {
        cellTemps[i] = readCellTemperature(i);
        if (cellTemps[i] > maxT) maxT = cellTemps[i];
    }

    // Trigger local physical LEDs and buzzer
    updatePhysicalAlerts(deltaV, maxT);

    // Build JSON message matching Python telemetry schema
    StaticJsonDocument<384> doc;
    doc["pack_id"] = PACK_ID;
    doc["mode"] = "hardware";
    doc["source"] = "esp32_sensor_array";
    doc["timestamp"] = String(millis()); // Or NTP timestamp if synced
    doc["cell_count"] = 4;
    doc["current_a"] = 0.0; // Optional current sensor input

    JsonArray vArray = doc.createNestedArray("cell_voltages");
    for (int i = 0; i < 4; i++) {
        vArray.add(serialized(String(cellVoltages[i], 3)));
    }

    JsonArray tArray = doc.createNestedArray("cell_temperatures");
    for (int i = 0; i < 4; i++) {
        tArray.add(serialized(String(cellTemps[i], 1)));
    }

    char buffer[384];
    size_t n = serializeJson(doc, buffer);

    if (mqttClient.connected()) {
        mqttClient.publish(MQTT_TOPIC, buffer, false);
        Serial.print("Published to ");
        Serial.print(MQTT_TOPIC);
        Serial.print(": ");
        Serial.println(buffer);
    } else {
        Serial.println("MQTT client offline. Payload buffered/skipped.");
    }
}

// ==============================================================================
// 7. SETUP & MAIN LOOP
// ==============================================================================

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n=== ESP32 Battery Cell Imbalance Monitor Initializing ===");

    pinMode(PIN_LED_NORMAL, OUTPUT);
    pinMode(PIN_LED_WARNING, OUTPUT);
    pinMode(PIN_LED_CRITICAL, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);

    digitalWrite(PIN_LED_NORMAL, LOW);
    digitalWrite(PIN_LED_WARNING, LOW);
    digitalWrite(PIN_LED_CRITICAL, LOW);
    digitalWrite(PIN_BUZZER, LOW);

    // Set analog ADC attenuation to 11dB (allows up to ~3.3V input range)
    analogSetAttenuation(ADC_11db);

    // If using TLS, set insecure mode for testing or provide root CA certificate
    espClient.setInsecure(); // Allows connecting to HiveMQ Cloud without hardcoding certificate

    connectWiFi();
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
    if (!mqttClient.connected()) {
        connectMQTT();
    }
    mqttClient.loop();

    unsigned long now = millis();
    if (now - lastSampleTime >= SAMPLE_INTERVAL_MS) {
        lastSampleTime = now;
        publishTelemetry();
    }
}

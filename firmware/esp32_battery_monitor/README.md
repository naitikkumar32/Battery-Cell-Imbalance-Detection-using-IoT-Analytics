# Layer 6 — ESP32 Hardware Integration & Firmware Guide

## 1. Overview
The ESP32 microcontroller serves as the edge sensor node for physical battery packs. It captures individual cell voltages via precision voltage dividers, acquires cell surface temperatures using 10k NTC thermistors (or DS18B20 1-Wire sensors), validates readings, executes local LED/buzzer alarms, and transmits standardized JSON telemetry to HiveMQ Cloud or a local MQTT broker over TLS.

---

## 2. Bill of Materials (BOM) & Estimated Prototype Cost

| Item # | Component Description | Specification / Part Number | Qty | Est. Cost (INR) | Est. Cost (USD) |
|---|---|---|---|---|---|
| 1 | Microcontroller Board | ESP32 NodeMCU-32S (Wi-Fi + BLE) | 1 | ₹450 | $5.50 |
| 2 | Voltage Divider Resistors | 1% Metal Film Resistors (10k, 20k, 30k, 50k, 70k) | 8 | ₹40 | $0.50 |
| 3 | Temperature Sensors | 10k NTC Thermistors (B=3950) or DS18B20 Waterproof | 4 | ₹200 | $2.40 |
| 4 | Current Sensor (Optional) | ACS712-20A or INA219 High-Side I2C Module | 1 | ₹180 | $2.20 |
| 5 | Visual Indicators | 5mm LEDs (Green, Yellow, Red) | 3 | ₹15 | $0.20 |
| 6 | Acoustic Alert | 5V Active Buzzer Module | 1 | ₹35 | $0.45 |
| 7 | Prototyping Hardware | Solderless Breadboard & 40x Jumper Wires | 1 | ₹160 | $2.00 |
| 8 | Power Supply / Cable | 5V 2A Micro-USB Cable & Adapter | 1 | ₹150 | $1.80 |
| **Total** | **Estimated Prototype Cost** | | | **~₹1,230** | **~$15.05** |

---

## 3. Pin-by-Pin Hardware Wiring Guide

### A. Voltage Divider Sensing Interface (4S Pack: Nominal 14.8V, Max 16.8V)
> [!CAUTION]
> **CRITICAL ELECTRICAL SAFETY:**
> ESP32 ADC inputs will be permanently damaged if exposed to voltages exceeding **3.3V**.
> Never connect any battery terminal directly to an ESP32 pin. Use the voltage divider network below:

| Battery Tap | Max Voltage | Resistor Divider Network | Attenuated Max Pin Voltage | ESP32 ADC Pin |
|---|---|---|---|---|
| **Cell 1 (+) Tap** | 4.20 V | R1 = 10 kΩ, R2 = 20 kΩ (Ratio: 1.50) | 2.80 V | **GPIO 36 (VP)** |
| **Cell 2 (+) Tap** | 8.40 V | R1 = 30 kΩ, R2 = 10 kΩ (Ratio: 4.00) | 2.10 V | **GPIO 39 (VN)** |
| **Cell 3 (+) Tap** | 12.60 V | R1 = 50 kΩ, R2 = 10 kΩ (Ratio: 6.00) | 2.10 V | **GPIO 34** |
| **Cell 4 (+) Tap** | 16.80 V | R1 = 70 kΩ, R2 = 10 kΩ (Ratio: 8.00) | 2.10 V | **GPIO 35** |
| **Pack Negative (-)**| 0.00 V | Direct connection to ESP32 Ground | 0.00 V | **GND** |

*Note: Individual cell voltages are calculated differentially in software: $V_{Cell 2} = V_{Tap 2} - V_{Tap 1}$, etc.*

### B. Temperature Sensor Wiring (10k NTC Thermistors)
- Connect one terminal of each NTC thermistor to **GND**.
- Connect the other terminal to the respective ESP32 analog pin (**GPIO 32, 33, 25, 26**).
- Place a **10 kΩ 1% pull-up resistor** from each pin to the **3.3V rail**.
- Attach the thermistor beads directly to the cylindrical or prismatic cell casings using thermal tape or silicone thermal pads.

> [!NOTE]
> **Why DHT11 is Unsuitable for Cell Monitoring:**
> The DHT11 is an ambient air humidity/temperature sensor with a bulky plastic enclosure and slow thermal response (>10 seconds). Battery cell safety requires **direct surface-contact sensors** (such as NTC thermistors or DS18B20 metal probe sensors) with high thermal conductivity to detect rapid localized thermal runaway.

### C. Physical Alert Indicators
- **Green LED (Normal):** GPIO 2 -> 330Ω resistor -> Anode, Cathode to GND.
- **Yellow LED (Warning):** GPIO 4 -> 330Ω resistor -> Anode, Cathode to GND.
- **Red LED (Critical):** GPIO 5 -> 330Ω resistor -> Anode, Cathode to GND.
- **Active Buzzer:** Positive (+) to GPIO 18, Negative (-) to GND.

---

## 4. Pre-Commissioning Validation & Safety Procedure

Before connecting any real lithium-ion or LiFePO4 cells to the circuit:

### Step 1: Bench Power Supply Testing (Current-Limited)
1. Set a dual or multi-channel bench DC power supply to **3.70 V** with current limit set to **50 mA**.
2. Connect the power supply ground to the prototype board ground.
3. Apply 3.70 V to Tap 1 and measure the voltage at GPIO 36 with a calibrated Digital Multimeter (DMM).
4. Verify that the voltage at GPIO 36 is approximately **2.47 V** and never exceeds **3.30 V**.

### Step 2: DMM Calibration Procedure
1. Open the Arduino IDE Serial Monitor at `115200 baud`.
2. Compare the voltage reported on the serial console with the precision reading on your reference handheld DMM.
3. If an offset exists due to resistor tolerance (e.g. ±1%), adjust the calibration scalar constants (`DIVIDER_RATIOS`) in `esp32_battery_monitor.ino`:
   $$\text{Corrected Ratio} = \text{Nominal Ratio} \times \left(\frac{V_{DMM}}{V_{Measured}}\right)$$

### Step 3: Wireless Cloud Broker Verification
1. Enter your Wi-Fi credentials and HiveMQ Cloud cluster hostname in `esp32_battery_monitor.ino`.
2. Flash the firmware using Arduino IDE or PlatformIO.
3. Observe the Serial Monitor:
   - Wi-Fi connection confirmed and local IP assigned.
   - Secure TLS connection established to port 8883.
   - Outbound JSON packets matching the Python schema published every 2 seconds.

---

## 5. Industrial Safety Disclaimers
1. This prototype monitoring circuit is designed for educational analytics and imbalance diagnosis.
2. It is **NOT** a certified Battery Management System (BMS) and does **NOT** replace hardware-level overcurrent fuses, secondary independent protection ICs, or contactor disconnects.
3. Never attempt to deliberately overcharge, short-circuit, or overheat battery cells.

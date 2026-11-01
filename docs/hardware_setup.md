# Hardware Setup & Electrical Interfacing Guide

## 1. Safety First
> [!CAUTION]
> **HIGH RISK OF SHORT CIRCUIT & THERMAL RUNAWAY:**
> Lithium-ion cells possess exceptionally low internal resistance and can deliver instantaneous currents exceeding 50 Amperes, leading to violent fires or explosions if short-circuited.
> - Always perform bench testing using a current-limited DC power supply (set to 50mA limit) or potentiometer voltage dividers before connecting real battery cells.
> - Ensure all connections have insulated heat-shrink tubing.
> - Never bridge adjacent cell balance taps.

---

## 2. Voltage Measurement Principles (4S Pack Architecture)
In a series-connected 4-cell (4S) lithium pack:
- Cell 1: 0 V to 4.2 V (Referenced to ground)
- Cell 2: 4.2 V to 8.4 V (Floating with respect to ground)
- Cell 3: 8.4 V to 12.6 V (Floating with respect to ground)
- Cell 4: 12.6 V to 16.8 V (Floating with respect to ground)

Because the ESP32 shares a single common ground, voltage divider taps measure cumulative potential at each node:
- **Tap 1 ($V_{Tap1}$):** Measures Cell 1 directly ($V_{Cell1} = V_{Tap1}$).
- **Tap 2 ($V_{Tap2}$):** Measures cumulative voltage of Cells 1+2 ($V_{Cell2} = V_{Tap2} - V_{Tap1}$).
- **Tap 3 ($V_{Tap3}$):** Measures cumulative voltage of Cells 1+2+3 ($V_{Cell3} = V_{Tap3} - V_{Tap2}$).
- **Tap 4 ($V_{Tap4}$):** Measures total pack voltage ($V_{Cell4} = V_{Tap4} - V_{Tap3}$).

---

## 3. Voltage Divider Mathematical Formulation
For any voltage tap $V_{in}$, the attenuated voltage $V_{out}$ presented to the ESP32 ADC pin is given by:

$$V_{out} = V_{in} \times \left( \frac{R_2}{R_1 + R_2} \right)$$

Solving for the scaling divider ratio:

$$\text{Ratio} = \frac{R_1 + R_2}{R_2} = 1 + \frac{R_1}{R_2}$$

$$\text{Reconstructed } V_{in} = V_{out} \times \text{Ratio}$$

### Resistor Selections (1% Metal Film Precision):
1. **Tap 1 (Max 4.2V):**
   - $R_1 = 10\text{ k}\Omega$, $R_2 = 20\text{ k}\Omega$
   - $\text{Ratio} = (10+20)/20 = 1.50$
   - $V_{out, max} = 4.2 / 1.50 = 2.80\text{ V}$ (Safe for 3.3V ADC)
2. **Tap 2 (Max 8.4V):**
   - $R_1 = 30\text{ k}\Omega$, $R_2 = 10\text{ k}\Omega$
   - $\text{Ratio} = (30+10)/10 = 4.00$
   - $V_{out, max} = 8.4 / 4.00 = 2.10\text{ V}$
3. **Tap 3 (Max 12.6V):**
   - $R_1 = 50\text{ k}\Omega$, $R_2 = 10\text{ k}\Omega$
   - $\text{Ratio} = (50+10)/10 = 6.00$
   - $V_{out, max} = 12.6 / 6.00 = 2.10\text{ V}$
4. **Tap 4 (Max 16.8V):**
   - $R_1 = 70\text{ k}\Omega$, $R_2 = 10\text{ k}\Omega$
   - $\text{Ratio} = (70+10)/10 = 8.00$
   - $V_{out, max} = 16.8 / 8.00 = 2.10\text{ V}$

---

## 4. ESP32 Non-Linearity & Calibration
The ESP32 integrated SAR ADC exhibits known non-linearities below 0.15V and above 3.10V.
To maintain high precision measurement:
1. All attenuated outputs are engineered to sit comfortably within the linear window (**1.5V to 2.8V**).
2. The firmware uses 20-sample oversampling to suppress thermal and switching noise.
3. Multi-point calibration curves can be applied via the ESP32 `esp_adc_cal` API if sub-millivolt hardware precision is required.

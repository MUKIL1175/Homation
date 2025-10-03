from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep
import network
import urequests

# ========================================================= OLED Setup ===========================================================
# ESP32 safe I2C pins: SDA=21, SCL=22
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
oled = SSD1306_I2C(128, 64, i2c)
sleep(0.1)

# ====================================================== Relay GPIO Mapping ======================================================
relay = {
    0: 2,       # onboard LED (active-low)
    1: 4, 2: 5, 3: 12, 4: 13,
    5: 14, 6: 15, 7: 16, 8: 17
}
relays = {}

# ============================================ WiFi Connection =====================================================
def connect_wifi(ssid, password):
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Connecting to WiFi...", end='')
    while not wlan.isconnected():
        sleep(1)
        print(".", end='')
    print("\nConnected! IP:", wlan.ifconfig()[0])

# ================================================ Welcome Animation ============================================================
def welcome():
    oled.fill(0)
    for y in range(-20, 10):
        oled.fill(0)
        oled.text("Welcome", 35, y)
        oled.text("PROJECT X", 25, y + 20)
        oled.show()
        sleep(0.05)
    sleep(1)
    for i in range(3):
        oled.fill_rect(25, y + 20, 80, 10, 0)
        oled.show()
        sleep(0.1)
        oled.text("PROJECT X", 25, y + 20)
        oled.show()
        sleep(0.1)
    sleep(0.5)
    oled.fill(0)
    oled.text("Connecting...", 0, 0)
    oled.show()
    while not wlan.isconnected():
        sleep(0.2)
    oled.fill(0)
    oled.text("Connected", 0, 0)
    oled.text("with IP:", 0, 10)
    oled.text(wlan.ifconfig()[0], 0, 20)
    oled.show()
    sleep(1)
    oled.fill(0)
    oled.text("STATUS DASHBOARD", 0, 0)
    oled.show()

# ================================================= Dashboard (Fast & Aligned) ===================================================
def show(data):
    if not isinstance(data, list) or len(data) < 9:
        return
    rows = 2
    cols = 4
    for row in range(rows):
        line = ""
        for col in range(cols):
            idx = row * cols + col
            if idx >= len(data) - 1:
                break
            state = data[idx + 1]  # skip index 0 for onboard LED
            line += "{}:{}".format(idx, 1 if state else 0)
            if col != cols - 1:
                line += " "  # horizontal spacing
        oled.fill_rect(0, 20 + row * 10, 128, 10, 0)
        oled.text(line, 0, 20 + row * 10)
    oled.show()

# =============================================== Relay Assignment Section ======================================================
def assign_relay(relay):
    for key, value in relay.items():
        relays[key] = Pin(value, Pin.OUT)
        # Default states: onboard LED OFF (active-low = 1), other relays OFF (active-high = 0)
        if key == 0:
            relays[key].value(0)  # LED OFF
        else:
            relays[key].value(0)  # Relay OFF
    return relays

# =========================================== Data Fetching from Firebase DB =====================================================
def get_firebase_data():
    url = "https://nfc-xxxxxxx-rtdb.asia-southeast1.firebasedatabase.app/relays.json?auth=DOUY15wKNc65svUCTnVUIafYuRZjrLzzRd7oQ7RR"
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            raw_data = response.json()
            response.close()
            data_list = []

            # Convert dict or list to list, index 0 = onboard LED
            if isinstance(raw_data, dict):
                # dict may use keys "0"-"8"
                for i in range(len(relay)):
                    data_list.append(int(raw_data.get(str(i), 0)))
            elif isinstance(raw_data, list):
                data_list = [int(x) for x in raw_data]
                if len(data_list) < len(relay):
                    # pad with 0
                    data_list += [0] * (len(relay) - len(data_list))
            else:
                return None

            return data_list
        else:
            print("Error code:", response.status_code)
            response.close()
            return None
    except Exception as e:
        print("Error fetching data:", e)
        return None

# ========================================= Controlling and Powering the Relay ===================================================
def relay_control(data):
    if not isinstance(data, list):
        return
    for key, pin_obj in relays.items():
        if key >= len(data):
            state = 0
        else:
            state = data[key]

        # Onboard LED (active-low but map 1=ON, 0=OFF from Firebase)
        if key == 0:
            pin_obj.value(0 if state == 0 else 1)
        else:
            pin_obj.value(1 if state == 0 else 0)  # relays active-high


# ====================================================== MAIN ====================================================================
connect_wifi("xxxxxx", "xxxxxxxx")
assign_relay(relay)

try:
    welcome()
    while True:
        data = get_firebase_data()
        if data:
            relay_control(data)
            show(data)
        sleep(0.5)
except KeyboardInterrupt:
    print("Program interrupted by user.")
    oled.fill(0)
    oled.show()


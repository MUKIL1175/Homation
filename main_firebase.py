from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep
import network
import urequests

# ========================================================= OLED Setup ===========================================================
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# ====================================================== Relay GPIO Mapping ======================================================
relay = {
    0: "LED",       # Optional
    1: 2,  2: 3,  3: 4,  4: 5,
    5: 6,  6: 7,  7: 8,  8: 9,
    9: 10, 10: 11, 11: 12, 12: 13,
    13: 14, 14: 15, 15: 16, 16: 17
}
relays = {}

# ============================================ Wifi connection establishment ======================================================
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

# ================================================ Welcome Animation =============================================================
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
    sleep(3)
    oled.fill(0)

# ================================================= Dashboard ====================================================================
def show(data):
    if not isinstance(data, list) or len(data) < 17:
        oled.fill(0)
        oled.text("Invalid data", 0, 20)
        oled.show()
        return

    for page in range(2): 
        oled.fill(0)
        oled.text("STATUS DASHBOARD", 0, 0)
        base_index = 1 + page * 8
        for i in range(8):
            relay_num = base_index + i
            if relay_num >= len(data):
                break
            state = data[relay_num]
            status = "ON" if state else "OFF"
            oled.text("R{:02d} -> {:>3}".format(relay_num, status), 0, 10 + i * 8)
        oled.show()
        sleep(2)

# =============================================== Relay Assignment Section =======================================================
def assign_relay(relay):
    for key, value in relay.items():
        if key == 0:  # Skip LED
            continue
        relays[key] = Pin(value, Pin.OUT)
        relays[key].value(1)  # Default OFF
    return relays

# =========================================== Data Fetching from Firebase DB ======================================================
def get_firebase_data():
    url = "https://nfc-xxxxx-default-rtdb.asia-southeast1.firebasedatabase.app/relays.json"
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error code:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None

# ========================================= Controlling and Powering the Relay ===================================================
def relay_control(data):
    if not isinstance(data, list):
        print("Invalid data format. Expected list.")
        return
    
    relay_states = data[1:]  # Skip index 0
    for i, state in enumerate(relay_states):
        relay_number = i + 1
        if relay_number in relays:
            relays[relay_number].value(0 if state else 1)

# ====================================================== MAIN ====================================================================
connect_wifi("Blaze", "Monamukil")
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

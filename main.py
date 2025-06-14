from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep
import network
import urequests

# ========================================================= OLED Setup ===========================================================
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# ====================================================== Relay GPIO Mapping ======================================================
relay = {1: 2, 2: 3, 3: 4, 4: "LED"}
relays = {}

# ============================================ Wifi connection establisment ======================================================
def connect_wifi(ssid, password):
    global wlan  # Add this line
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Connecting to WiFi...", end='')
    while not wlan.isconnected():
        sleep(1)
        print(".", end='')
    print("\nConnected! IP:", wlan.ifconfig()[0])

# ================================================ Welcome Animation =============================================================
# def welcome():
#     oled.fill(0)
#     while not wlan.isconnected():
#         oled.text("Connecting.....",0,0)
#         oled.show()
#     oled.text("connected",0,0); oled.text("with Internet !",0,10)
#     oled.show()
#     sleep(3); oled.fill(0)
#     for y in range(-20, 10):  
#         oled.fill(0)
#         oled.text("Welcome", 35, y)
#         oled.text("PROJECT X", 25, y + 20)
#         oled.show()
#         sleep(0.05)
#     sleep(1)
# 
#     for i in range(3):
#         oled.fill_rect(25, y + 20, 80, 10, 0)
#         oled.show()
#         sleep(0.1)
#         oled.text("PROJECT X", 25, y + 20)
#         oled.show()
#         sleep(0.1)
#     sleep(0.5)
def welcome():
    oled.fill(0)

    # Step 1: Show "Welcome PROJECT X" animation
    for y in range(-20, 10):  
        oled.fill(0)
        oled.text("Welcome", 35, y)
        oled.text("PROJECT X", 25, y + 20)
        oled.show()
        sleep(0.05)
    sleep(1)

    # Flashing "PROJECT X"
    for i in range(3):
        oled.fill_rect(25, y + 20, 80, 10, 0)
        oled.show()
        sleep(0.1)
        oled.text("PROJECT X", 25, y + 20)
        oled.show()
        sleep(0.1)
    sleep(0.5)

    # Step 2: Show "Connecting..." while waiting for Wi-Fi
    oled.fill(0)
    oled.text("Connecting...", 0, 0)
    oled.show()

    while not wlan.isconnected():
        sleep(0.2)

    # Step 3: Show connected status with IP
    oled.fill(0)
    oled.text("Connected", 0, 0)
    oled.text("with IP:", 0, 10)
    oled.text(wlan.ifconfig()[0], 0, 20)  # Shows IP address
    oled.show()
    sleep(3)
    oled.fill(0)

# ================================================= Dashboard ====================================================================
def show(data):
    #print("Displaying on OLED:", data)
    oled.fill(0)
    oled.text("STATUS DASHBOARD", 0, 0)
    try:
        oled.text("R1 -> |{}|".format(data[1]), 0, 20)
        oled.text("R2 -> |{}|".format(data[2]), 0, 30)
        oled.text("R3 -> |{}|".format(data[3]), 0, 40)
        if data[4] == 1:
            oled.text("R4 -> |0|", 0, 50)
        else:
            oled.text("R4 -> |1|", 0, 50)
            
    except:
        oled.text("Error loading data", 0, 30)

    oled.show()

# =============================================== relay assingment section =======================================================
def assign_relay(relay):
    for key, value in relay.items():
        relays[key] = Pin(value, Pin.OUT)
        relays[key].value(1)  # Default OFF
    return relays

# =========================================== data fetching from firebase DB ======================================================
def get_firebase_data():
    url = "https://nfc-esp32-default-rtdb.asia-southeast1.firebasedatabase.app/relays.json"
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            data = response.json()
            #print("Firebase Data:", data)
            return data
        else:
            print("Error code:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None

# ========================================= controlling and powering the relay =======================================================
def relay_control(data):
    if not isinstance(data, list):
        print("Invalid data format. Expected list.")
        return
    
    relay_states = data[1:]  # Skip index 0
    #print("Processed States:", relay_states)

    for i, state in enumerate(relay_states):
        relay_number = i + 1
        if relay_number in relays:
            relays[relay_number].value(0 if state else 1)

# ====================================================== MAIN ====================================================================
connect_wifi("Blaze", "1234567890")
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




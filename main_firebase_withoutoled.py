from machine import Pin
from time import sleep
import network
import urequests

buz = Pin(15, Pin.OUT)
buz.value(0)
# ====================================================== Relay GPIO Mapping ======================================================
relay = {       
    1: 2,  2: 3,  3: 4,  4: 5,
    5: 6,  6: 7,  7: 8,  8: 9,
    9: 10, 10: 11, 11: 12, 12: 13,
    13: 14, 14: 16, 15: 17
}
relays = {}

# ============================================ Wifi Connection ====================================================================
def connect_wifi(ssid, password):
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Connecting to WiFi...", end='')
    while not wlan.isconnected():
        sleep(0.5);buz.on();sleep(0.1);buz.off()
        print(".", end='')
    print("\nConnected! IP:", wlan.ifconfig()[0])
    for _ in range(4):
        buz.value(1)
        sleep(0.1)
        buz.value(0)
        sleep(0.1)
    

# =============================================== Relay Assignment Section ========================================================
def assign_relay(relay):
    for key, value in relay.items():
        if key == 0:  
            continue
        relays[key] = Pin(value, Pin.OUT)
        relays[key].value(1) 
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

# ========================================= Controlling and Powering the Relay ====================================================
def relay_control(data):
    if not isinstance(data, list):
        print("Invalid data format. Expected list.")
        return
    
    relay_states = data[1:]  
    for i, state in enumerate(relay_states):
        relay_number = i + 1
        if relay_number in relays:
            relays[relay_number].value(0 if state else 1)

# ====================================================== MAIN ====================================================================
connect_wifi("Blaze", "Monamukil")
assign_relay(relay)

try:
    while True:
        data = get_firebase_data()
        if data:
            relay_control(data)
        sleep(0.5)
except KeyboardInterrupt:
    print("Program interrupted by user.")
    buz.off()
buz.off()

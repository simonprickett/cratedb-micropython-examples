import json
import network
import time
import cratedb
from machine import ADC

import envvars

# Set up the sound sensor.
sound_sensor = ADC(0)

# Set up the light sensor.
light_sensor = ADC(1)

# Set up CrateDB.
crate = cratedb.CrateDB(
    host=envvars.CRATEDB_HOST,
    user=envvars.CRATEDB_USER,
    password=envvars.CRATEDB_PASSWORD
)

# Set up the WiFi and connect.
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(envvars.WIFI_SSID, envvars.WIFI_PASSWORD)

while not wlan.isconnected() and wlan.status() >= 0:
    print("Connecting to wifi...")
    time.sleep(0.5)

print("Connected to wifi!")
sensor_id = wlan.ifconfig()[0]

print(f"Sensor ID: {sensor_id}")

while True:
    # Read the sensors.
    light = light_sensor.read_u16()
    sound = sound_sensor.read_u16()
    
    print(f"light: {light}, sound: {sound}")
    
    response = crate.execute(
        "INSERT INTO sensor_readings (sensor_id, light, sound) VALUES (?, ?, ?)",
        [
            sensor_id,
            light,
            sound
        ]
    )
    
    if (response["rowcount"] == 1):
        print("Inserted into CrateDB.")
        
    
    time.sleep(10)
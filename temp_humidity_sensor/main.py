import network
import requests

from dht11 import *
from machine import Pin, I2C
from time import sleep

import envvars

dht2 = DHT(18)  # Temperature and humidity sensor connected to D18

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
    temp, humid = dht2.readTempHumid()  # Read temperature and humidity
    print(f"temp: {temp}, humid: {humid}")    

    sql = f"INSERT INTO sensor_readings (sensor_id, temp, humidity) VALUES ('{sensor_id}', {temp}, {humid})"
    
    response_doc = requests.post(
        envvars.CRATEDB_URL,
        headers = {
            "Authorization": f"Basic {envvars.CRATEDB_CREDENTIALS}"
        },
        json = {
            "stmt": sql
        }
    ).json()
    
    if (response_doc["rowcount"] == 1):
        print("Inserted into CrateDB.")    
    
    sleep(10)
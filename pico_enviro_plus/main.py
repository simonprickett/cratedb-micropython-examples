import envvars
import json
import microcrate
import network
import time

from machine import Pin, ADC, UART
from picographics import PicoGraphics, DISPLAY_ENVIRO_PLUS
from pimoroni import RGBLED, Button
from breakout_bme68x import BreakoutBME68X, STATUS_HEATER_STABLE
from pimoroni_i2c import PimoroniI2C
from breakout_ltr559 import BreakoutLTR559


# change this to adjust temperature compensation
TEMPERATURE_OFFSET = 3

UPDATE_INTERVAL = 30  # how often to send data, in seconds.

# Set up CrateDB.
crate = microcrate.CrateDB(
    host=envvars.CRATEDB_HOST,
    user=envvars.CRATEDB_USER,
    password=envvars.CRATEDB_PASSWORD
)

# set up wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(envvars.WIFI_SSID, envvars.WIFI_PASSWORD)

while not wlan.isconnected() and wlan.status() >= 0:
    print("Connecting to wifi...")
    time.sleep(0.5)

ip_addr = wlan.ifconfig()[0]
print(f"Connected to wifi as {ip_addr}")

# set up the display
display = PicoGraphics(display=DISPLAY_ENVIRO_PLUS)
display.set_backlight(1.0)

# set up the LED
led = RGBLED(6, 7, 10, invert=True)
led.set_rgb(255, 0, 0)

# set up the buttons
button_a = Button(12, invert=True)
button_b = Button(13, invert=True)

# set up the Pico W's I2C
PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)

# set up BME688 and LTR559 sensors
bme = BreakoutBME68X(i2c, address=0x77)
ltr = BreakoutLTR559(i2c)

# set up analog channel for microphone
mic = ADC(Pin(26))

# some constants we'll use for drawing
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)

WIDTH, HEIGHT = display.get_bounds()
display.set_font("bitmap8")

# some other variables we'll use to keep track of stuff
current_time = 0
last_sent_time = 0
send_success = False
e = "Wait a minute"

while True:

    # read BME688
    temperature, pressure, humidity, gas, status, _, _ = bme.read()
    pressure = pressure / 100
    heater = "Stable" if status & STATUS_HEATER_STABLE else "Unstable"

    # correct temperature and humidity using an offset
    corrected_temperature = temperature - TEMPERATURE_OFFSET
    dewpoint = temperature - ((100 - humidity) / 5)
    corrected_humidity = 100 - (5 * (corrected_temperature - dewpoint))

    # read LTR559
    ltr_reading = ltr.get_reading()
    lux = ltr_reading[BreakoutLTR559.LUX]
    prox = ltr_reading[BreakoutLTR559.PROXIMITY]

    # read mic
    mic_reading = mic.read_u16()

    if heater == "Stable" and ltr_reading is not None:
        led.set_rgb(0, 0, 0)
        current_time = time.ticks_ms()
        if (current_time - last_sent_time) / 1000 >= UPDATE_INTERVAL:
            try:
                print(f"temp: {corrected_temperature}")
                print(f"humidity: {corrected_humidity}")
                print(f"pressure: {pressure}")
                print(f"gas: {gas}")
                print(f"light: {lux}")
                print(f"sound: {mic_reading}")
                
                others = {
                    "pressure": pressure,
                    "gas": gas,
                    "location": {
                        "name": "Office",
                        "phone": "01150000000"
                    }
                }

                # Send data to CrateDB.
                response = crate.execute(
                    """
                        INSERT INTO sensor_readings (sensor_id, temp, humidity, light, sound, others) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [
                        ip_addr,
                        corrected_temperature,
                        corrected_humidity,
                        lux,
                        mic_reading,
                        others
                    ]
                )

                last_sent_time = time.ticks_ms()
                led.set_rgb(0, 50, 0)
                send_success = True
            except Exception as e:
                print(e)
                send_success = False
                led.set_rgb(255, 0, 0)
    else:
        # light up the LED red if there's a problem with network/database or sensor readings
        led.set_rgb(255, 0, 0)

    # turn off the backlight with A and turn it back on with B
    # things run a bit hotter when screen is on, so we're applying a different temperature offset
    if button_a.is_pressed:
        display.set_backlight(1.0)
        TEMPERATURE_OFFSET = 5
        time.sleep(0.5)
    elif button_b.is_pressed:
        display.set_backlight(0)
        TEMPERATURE_OFFSET = 3
        time.sleep(0.5)

    # draw some stuff on the screen
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    display.text("Posting Enviro+ data to CrateDB.", 10, 10, WIDTH, scale=3)
    if send_success is True:
        current_time = time.ticks_ms()
        display.set_pen(GREEN)
        display.text(f"Last sent {(current_time - last_sent_time) / 1000:.0f} seconds ago", 10, 130, WIDTH, scale=3)
    else:
        display.set_pen(RED)
        display.text(e, 10, 130, WIDTH, scale=3)
    display.update()

    time.sleep(1.0)
from gfx_pack import SWITCH_A, SWITCH_B, SWITCH_C, SWITCH_D
import gfx
import network
import sys
import time

import cratedisplay
import envvars


SPINNER_CHARS = [ "\\", "|", "/", "-" ]

display = gfx.display

def main_menu():
    gfx.set_backlight(0, 0, 0, 80)
    gfx.clear_screen()
    ip_address = wlan.ifconfig()[0]
    gfx.display_centered(ip_address, 8, 2)
    x_pos = gfx.display_centered("A - SHOW DATA", 27, 1)
    display.text("B - SOMETHING ELSE", x_pos, 36, gfx.DISPLAY_WIDTH, 1)
    display.text("C - SOMETHING ELSE", x_pos, 45, gfx.DISPLAY_WIDTH, 1)
    display.text("D - SOMETHING ELSE", x_pos, 54, gfx.DISPLAY_WIDTH, 1)
    display.update()
    
display.set_font("bitmap_8")

gfx.clear_screen()
gfx.set_backlight(128, 16, 0, 0)
gfx.display_centered("STARTING UP!", 25, 2)
display.update()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(envvars.WIFI_SSID, envvars.WIFI_PASSWORD)

n = 0
while not wlan.isconnected() and wlan.status() >= 0:
    gfx.clear_screen()
    display.text(f"CONNECTING {SPINNER_CHARS[n]}", 2, 25, gfx.DISPLAY_WIDTH, 2)
    display.update()
    
    n = n + 1 if n < len(SPINNER_CHARS) - 1 else 0
    
    time.sleep(0.2)

gfx.clear_screen()

if wlan.status() == network.STAT_GOT_IP:
    gfx.display_centered("CONNECTED!", 25, 2)
elif wlan.status() == network.STAT_WRONG_PASSWORD:
    gfx.display_centered("WRONG WIFI PASSWORD!", 25, 1)
elif wlan.status() == network.STAT_NO_AP_FOUND:
    gfx.display_centered("WRONG WIFI SSID!", 25, 1)
else:
    gfx.display_centered("WIFI CONNECTION ERROR!", 25, 1)

display.update()

if wlan.status() == network.STAT_GOT_IP:
    gfx.flash_backlight(5, 0, 64, 0, 0)
    gfx.set_backlight(0, 0, 0, 80)
    time.sleep(1)
else:
    gfx.flash_backlight(5, 128, 0, 0, 0)
    gfx.set_backlight(128, 0, 0, 0)
    
    # Stop as we can't do anything without wifi.
    sys.exit(1)

main_menu()

while True:
    if gfx.gp.switch_pressed(SWITCH_A):
        cratedisplay.run()
        main_menu()
    elif gfx.gp.switch_pressed(SWITCH_B):
        main_menu()
    elif gfx.gp.switch_pressed(SWITCH_C):
        main_menu()
    elif gfx.gp.switch_pressed(SWITCH_D):
        main_menu()
        
    time.sleep(0.01)

    
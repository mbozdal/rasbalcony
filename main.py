import network
import sys
import urequests
import time
from time import sleep
from machine import Pin, RTC, reset
import ntptime
import os
from ota import OTAUpdater
from CONFIG import SSID, PASSWORD,things_speak_api_key,firmware_ota_url
import watering

os.chdir("/")

#Network Initialization
ssid = SSID
password = PASSWORD

#ota location
firmware_url = firmware_ota_url


def log(data):
    try:
        file = open("log.txt", "a")
        rtc = RTC()
        file.write(str(data) + "\t" + str(rtc.datetime()) + "\n")
        file.close()
    except Exception as e:
        print("Error occurred while logging:", str(e))
        machine.reset()


def connect_WiFi():
    MAX_ATTEMPTS = 50  # Maximum number of connection attempts
    attempt = 0

    while attempt < MAX_ATTEMPTS:
        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                print('Waiting for connection...')
                sleep(10)
                attempt += 1
                if attempt >= MAX_ATTEMPTS:
                    print('Unable to establish a connection. Resetting...')
                    machine.reset()
            ip = wlan.ifconfig()[0]
            print(f'Connected on {ip}')
            return ip
        except Exception as e:
            print('Error occurred while connecting to WiFi:', str(e))
            log(f"E2 WCE") #WiFi Connection Error
            machine.reset()




# Main Program

ip = connect_WiFi()  # Connect to Network


try:
    ntptime.settime()  # Update time from NTP server
except Exception as e:
    print('Error occurred while updating time:', str(e))
    log("E1 TUE") # Time Update Error
    machine.reset()

log("E0")  # log reset


# Function to execute watering logic - redundant
def execute_watering_logic():
    try:
        import watering  # Import watering logic from watering.py
        watering.water_plants()  # Call watering function from watering.py
    except Exception as e:
        print('Error occurred while executing watering logic:', str(e))
        machine.reset()




signal_led = Pin(0, Pin.OUT) #signal LED
# Main program loop
while True:
    try:
        signal_led.on()
        print(1)
        ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "watering.py")
        ota_updater.download_and_install_update_if_available_noRESET()
        print(2)
        time.sleep(5)  # led check
        
        
        # After OTA update, execute the updated script
        try:    # Reload the module to apply changes
                # Remove the module from the module cache
            if 'watering' in sys.modules:
                del sys.modules['watering']
        
            # Re-import the module to apply changes
            import watering

            # Call the main function or logic from the updated module
            watering.main()
            
            
            print("Watering logic executed successfully.")
        except Exception as e:
            print('Error occurred while executing watering logic:', str(e))
        
        
        
        
        print(3)
        time.sleep(1)  # led check
        signal_led.off()
        time.sleep(10)  # Wait for 5 minutes before checking again
    except Exception as e:
        print('Error occurred in main OTA program loop:', str(e))
        machine.reset()

import sys
import machine
import network
import urequests
import time
from time import sleep
from machine import Pin, RTC, reset
import ntptime
import os
from CONFIG import SSID, PASSWORD,things_speak_api_key

os.chdir("/")


#ThingSpeak Initialization
server = "http://api.thingspeak.com/"
apikey = things_speak_api_key
field = 1

global last_watering_time

##pin assignments##
#internal temperature
adcpin = 4
temperature_internal = machine.ADC(adcpin)

#GPIOs
signal_led = Pin(0, Pin.OUT) #signal LED

pumpA = Pin(18, Pin.OUT)
pumpB = Pin(19, Pin.OUT)
pumpC = Pin(20, Pin.OUT)
pumpD = Pin(21, Pin.OUT)



#initial parameters
last_watering_time = 0
watering_period = 12*60*60

pumps = [pumpA, pumpB, pumpC, pumpD]

# Turn off pumps - precaution
for pump in pumps:
    pump.off()
    
signal_led.on()

def log(data):
    try:
        file = open("log.txt", "a")
        rtc = RTC()
        file.write(str(data) + "\t" + str(rtc.datetime()) + "\n")
        file.close()
    except Exception as e:
        print("Error occurred while logging:", str(e))
        machine.reset()

def param(update):
    try:
        with open("param.txt", "r+") as file:
            lines = file.readlines()
            last_watering_time = lines[0].strip() if lines else ""

            if update == 0:
                lw = last_watering_time
            elif update == 1:
                last_watering_time = str(ntptime.time())  # update last watering
                file.seek(0)
                file.write(last_watering_time + "\n")
                next_watering_line = str(int(last_watering_time) + watering_period)
                file.write(next_watering_line + "\n")

        return last_watering_time
    except Exception as e:
        print("Error occurred while handling parameters:", str(e))
        machine.reset()


def read_temperature():
    adc_value = temperature_internal.read_u16()
    volt = (3.3/65535)*adc_value
    temperature = 27 - (volt - 0.706)/0.001721
    return round(temperature, 1)

       
def thingSpeak(field, data):
    signal_led.on()
    try:
        data= str(data).replace(" ", "")
        url = f"{server}/update?api_key={apikey}&field{field}={data}"
        request = urequests.post(url)
        request.close()
        signal_led.off()
    except Exception as e:
        print('Error occurred:', str(e))
        log(f"E1 {field} {data}") #ThingSpeak Communication Error
        machine.reset()   
            
        
def water_plants(pump, duration):
    param(1)  # Update with current watering
    pump.on()
    try:
        print(pump)
    except Exception as e:
        print('Error occurred while water_plants:', str(e))
    thingSpeak(3, str(pump))
    sleep(duration)
    pump.off()
    thingSpeak(3, 0)
        

def main():# Main Program
    signal_led.off()
    sleep(1)
    signal_led.on()
    sleep(1)
    signal_led.off()
    sleep(1)
    signal_led.on()
    sleep(1)
    signal_led.off()
    sleep(1)
    signal_led.on()
    sleep(1)
    signal_led.off()
    sleep(1)
    signal_led.on()
    sleep(1)
    signal_led.off()
    sleep(1)
    signal_led.on()
    sleep(1)
    signal_led.off()
    sleep(1)
    signal_led.on()
    try:
        ntptime.settime()  # Update time from NTP server
    except Exception as e:
        print('Error occurred while updating time:', str(e))
        log("E1 TUE") # Time Update Error
        machine.reset()

    signal_led.off()

    print(ntptime.time())

    try:
        last_watering_time = int(param(0))
        temperature_pico = read_temperature()
        thingSpeak(1, temperature_pico)
        sleep(15)
        thingSpeak(2, (last_watering_time + watering_period - ntptime.time()))
        sleep(15)

        if (last_watering_time + watering_period) - ntptime.time() <= 0:
            water_plants(pumpA,30)
            sleep(60)
            water_plants(pumpB,30)
            sleep(60)
            water_plants(pumpC,30)
            sleep(60)
            water_plants(pumpD,30)
            sleep(60)          
        
    except Exception as e:
        print('Error occurred in main program loop:', str(e))
        log("E2 MPE") #main Program Error
        machine.reset()



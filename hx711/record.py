import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import sys
import os
import json
from datetime import datetime
from hx711 import HX711

failed_read_halt_limit = 10
referenceUnit = -465
temperature = None
humidity = None
failed_reads = 0
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

def log(message):
    if type(message) is not type(""):
        message = json.dumps(message)
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    logfiledate = datetime.now().strftime("%Y%m%d")
    logfile = "/home/ian/sensor_data-"+logfiledate+".log"
    entry = timestamp + ": " + message + "\n"
    print(entry)
    if os.path.exists(logfile):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    with open(logfile, append_write) as write_file:
        write_file.write(entry)

def cleanAndExit():
    print("Cleaning...")
    GPIO.cleanup()
        
    print("Bye!")
    sys.exit()


def read_sensor():
    global temperature
    global humidity
    global failed_reads

    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
    while temperature is None and failed_reads < failed_read_halt_limit:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
        if temperature is None:
            failed_reads = failed_reads + 1
            time.sleep(1)
    if temperature is not None:
        temperature = temperature * 9/5.0 + 32

    if humidity is not None and temperature is not None:
        log('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    
    if humidity is None:
        humidity = 0
    
    if temperature is None:
        log("sensor failed")
    
    failed_reads = 0

while True:
    try:
        read_sensor()
        val = hx.get_weight(5)
        log(val)

        hx.power_down()
        hx.power_up()
        time.sleep(10)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
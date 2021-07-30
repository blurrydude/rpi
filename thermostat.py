import Adafruit_DHT
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
temperature = temperature * 9/5.0 + 32

if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))

GPIO.setup(26, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

GPIO.output(26, GPIO.HIGH)
time.sleep(1)
GPIO.output(20, GPIO.HIGH)
time.sleep(1)
GPIO.output(21, GPIO.HIGH)
time.sleep(1)

GPIO.output(26, GPIO.LOW)
time.sleep(1)
GPIO.output(20, GPIO.LOW)
time.sleep(1)
GPIO.output(21, GPIO.LOW)

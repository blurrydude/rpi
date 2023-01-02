import Adafruit_DHT
import time
import RPi.GPIO as GPIO

# Set the sensor type and gpio pin
sensor = Adafruit_DHT.DHT11
gpio_pin = 4

# Set the low and high temperature thresholds
low_temp = 20
high_temp = 25

# Set the number of minutes to wait before turning on gpio pin 22
wait_minutes = 5

# Set the duration of time to keep gpio pin 22 on (in minutes)
duration = 2

# Set the gpio pin numbering scheme
GPIO.setmode(GPIO.BCM)

# Set gpio pins 20, 21, and 22 as outputs
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

# Set the start time
start_time = time.time()

while True:
  # Read the humidity and temperature
  humidity, temperature = Adafruit_DHT.read(sensor, gpio_pin)
  
  # If the read is successful, check the temperature and set the gpio pins accordingly
  if humidity is not None and temperature is not None:
    print("Temperature: {:.1f} C  Humidity: {}%".format(temperature, humidity))
    if temperature < low_temp:
      GPIO.output(20, GPIO.HIGH)
      GPIO.output(21, GPIO.LOW)
      start_time = time.time()
    elif temperature > high_temp:
      GPIO.output(20, GPIO.LOW)
      GPIO.output(21, GPIO.HIGH)
      start_time = time.time()
    else:
      GPIO.output(20, GPIO.LOW)
      GPIO.output(21, GPIO.LOW)
      # Check if the elapsed time is greater than the wait time
      elapsed_time = time.time() - start_time
      if elapsed_time > wait_minutes * 60:
        # Turn on gpio pin 22
        GPIO.output(22, GPIO.HIGH)
        # Wait for the duration of time specified
        time.sleep(duration * 60)
        # Turn off gpio pin 22
        GPIO.output(22, GPIO.LOW)
  else:
    print("Failed to retrieve data from sensor")
    
  # Wait for 5 seconds before taking the next reading
  time.sleep(5)

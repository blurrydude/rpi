from gpiozero import LED
from time import sleep

leds = [
    LED("GPIO5"),
    LED("GPIO6"),
    LED("GPIO13"),
    LED("GPIO16"),
    LED("GPIO19"),
    LED("GPIO20"),
    LED("GPIO21"),
    LED("GPIO26")
]

for led in leds:
    led.on()

while True:
    for led in leds:
        led.off()
        sleep(1)
        led.on()
        sleep(3)
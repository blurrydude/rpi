from ssd1306 import SSD1306_I2C
from machine import Pin, PWM, I2C
import math

class Display:
    def __init__(self):
        i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=200000)
        devices = i2c.scan()
        self.detected = True
        if len(devices) == 0:
            self.detected = False
            return
        self.oled = SSD1306_I2C(128,64,i2c)
    
    def display_text(self, text):
        self.oled.fill(0)
        for i in range(len(text)):
            y = math.floor(i/16)
            x = i-(y*16)
            self.oled.text(text[i],x*8,y*8)
        self.oled.show()

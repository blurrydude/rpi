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
        self.cycle = 0
        self.asleep = False
    
    def display_text(self, text, centered = False):
        if self.asleep:
            self.wake()
        self.oled.fill(0)
        stringy = isinstance(text, str)
        if stringy and len(text) > 16:
            stringy = False
            text = self.wrap(text)
        if centered:
            if stringy:
                text = self.center(text)
            else:
                for i in range(len(text)):
                    text[i] = self.center(text[i])
        for i in range(len(text)):
            if stringy:
                y = math.floor(i/16)
                x = i-(y*16)
            else:
                y = i
                x = 0
            self.oled.text(text[i],x*8,y*8)
        self.oled.show()
    
    def center(self, text):
        while len(text) < 16:
            text = ' ' + text + ' '
        return text
    
    def wrap(self, text):
        current_line = ''
        lines = []
        words = text.split()
        for word in words:
            if len(current_line + word) > 16:
                lines.append(current_line)
                current_line = word + ' '
            else:
                current_line = current_line + word + ' '
        if current_line != lines[len(lines)-1]:
            lines.append(current_line)
        return lines
    
    def wake(self):
        self.oled.poweron()
        self.asleep = False
        self.cycle = 0

    def update(self, input):
        if input:
            self.cycle = 0
            return
        
        self.cycle = self.cycle + 1
        
        if self.cycle > 6000:
            if self.asleep:
                self.oled.poweron()
                self.asleep = False
                self.cycle = 5000
            else:
                self.oled.poweroff()
                self.asleep = True
                self.cycle = 0

    def draw_line(self, point_a, point_b):
        self.oled.line(point_a[0],point_a[1],point_b[0],point_b[1],1)

    def draw_circle(self, x, y, r):
        # Draw a circle centered at (x,y) with radius r
        for i in range(x - r, x + r + 1):
            for j in range(y - r, y + r + 1):
                if (i - x)**2 + (j - y)**2 <= r**2:
                    self.oled.pixel(i, j, 1)
                    
    def draw_hexagon(self, x, y, r):
        # Draw a hexagon centered at (x,y) with radius r
        for i in range(6):
            x1 = x + r * math.cos(i * math.pi / 3)
            y1 = y + r * math.sin(i * math.pi / 3)
            x2 = x + r * math.cos((i + 1) * math.pi / 3)
            y2 = y + r * math.sin((i + 1) * math.pi / 3)
            self.oled.line(int(x1), int(y1), int(x2), int(y2), 1)
    
    def draw_points(self, points):
        for point in points:
            self.oled.pixel(point[0], point[1], 1)


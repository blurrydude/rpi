from ssd1306 import SSD1306_I2C
from machine import Pin, PWM, I2C
import math

class Display:
    def __init__(self, sda=8, scl=9):
        # Initialize an I2C object for communication with the display
        i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=200000)
        
        # Scan for devices on the I2C bus and check if the display is detected
        devices = i2c.scan()
        self.detected = True
        if len(devices) == 0:
            self.detected = False
            return
        
        # If the display is detected, create an SSD1306_I2C object with the given parameters
        self.oled = SSD1306_I2C(128,64,i2c)
        self.cycle = 0
        self.asleep = False

    def display_text(self, text, centered = False):
        # Wake the display if it is asleep
        if self.asleep:
            self.wake()
        
        # Clear the display
        self.oled.fill(0)
        
        # Check if the input text is a string and longer than 16 characters
        stringy = isinstance(text, str)
        if stringy and len(text) > 16:
            stringy = False
            text = self.wrap(text)
        
        # Center the text if requested
        if centered:
            if stringy:
                text = self.center(text)
            else:
                for i in range(len(text)):
                    text[i] = self.center(text[i])
        
        # Display the text on the screen
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
        # Add spaces to the left and right of the text until it is centered on a 16-character line
        while len(text) < 16:
            text = ' ' + text + ' '
        return text

    def wrap(self, text):
        # Wrap the input text so that it fits on the display (16 characters per line)
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
        # Turn on the display and reset the sleep cycle counter
        self.oled.poweron()
        self.asleep = False
        self.cycle = 0

    def update(self, input):
        # If there is any input, reset the sleep cycle counter and return
        if input:
            self.cycle = 0
            return
        
        # Increment the sleep cycle counter
        self.cycle = self.cycle + 1
        
        # If the sleep cycle has reached a threshold, put the display to sleep or wake it up
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
        # Draw a line between two points
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

# Define a class called Button
class Button:
    # Define an __init__() method that initializes the Button object
    def __init__(self, pin):
        # Store the pin number passed in as an argument in an instance variable called 'pin'
        # Configure the pin as an input with a pull-down resistor
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        # Initialize a boolean variable called 'pressed' to False to indicate that the button is not currently pressed
        self.pressed = False
        # Initialize a counter called 'since_last_press' to 0 to keep track of how long it has been since the button was last pressed
        self.since_last_press = 0
        # Initialize instance variables called 'on_down' and 'on_up' to None
        # These will be used to store callback functions that will be executed when the button is pressed or released
        self.on_down = None
        self.on_up = None

    # Define an 'update' method that checks the current state of the button and executes the corresponding callback function
    def update(self):
        # Read the current state of the button and store it in a variable called 'pressed'
        pressed = self.pin.value() > 0
        # If the current state of the button is different from the previous state, update the 'pressed' variable, reset the 'since_last_press' counter to 0, and call the 'handle_button' method to execute the appropriate callback function
        if pressed != self.pressed:
            self.pressed = pressed
            self.since_last_press = 0
            self.handle_button()
            return True
        # If the button has not been pressed or released, increment the 'since_last_press' counter by 1
        # If the counter is less than 2000, return False to indicate that no button event occurred
        if self.since_last_press < 2000:
            self.since_last_press = self.since_last_press + 1
        return False

    # Define a 'handle_button' method that executes the appropriate callback function when the button is pressed or released
    def handle_button(self):
        # If the button is currently pressed and a callback function has been assigned to the 'on_down' instance variable, execute that function
        if self.pressed and self.on_down is not None:
            self.on_down()
        # If the button is currently not pressed and a callback function has been assigned to the 'on_up' instance variable, execute that function
        if self.pressed is False and self.on_up is not None:
            self.on_up()

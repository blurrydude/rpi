from machine import Pin, PWM, I2C, RTC
from buttons import Button
import time

class RelayBoardBrain:
    def __init__(self, main_brain):
        self.main_brain = main_brain
        self.buttons = [
            Button(26),
            Button(27),
            Button(28)
        ]
        self.buttons[0].on_up = self.button_1_press
        self.buttons[1].on_up = self.button_2_press
        self.buttons[2].on_up = self.button_3_press
        self.relays = [
            Pin(2, Pin.OUT),
            Pin(3, Pin.OUT),
            Pin(4, Pin.OUT),
            Pin(5, Pin.OUT),
            Pin(6, Pin.OUT),
            Pin(7, Pin.OUT),
            Pin(10, Pin.OUT),
            Pin(11, Pin.OUT),
            Pin(12, Pin.OUT),
            Pin(13, Pin.OUT),
            Pin(14, Pin.OUT),
            Pin(16, Pin.OUT),
            Pin(17, Pin.OUT),
            Pin(18, Pin.OUT),
            Pin(19, Pin.OUT),
            Pin(20, Pin.OUT),
            Pin(21, Pin.OUT),
            Pin(22, Pin.OUT)
        ]
        self.button_map = []
        sb = 0
        b = 0
        for i in range(len(self.relays)):
            self.button_map.append([f"{sb}|{b}"])
            if b == 2:
                b = 0
                sb = sb + 1
            else:
                b = b + 1
    
    def start(self):
        while True:
            message = self.main_brain.comms.read().strip('\n')
            reply = "nothing changed"
            for i in range(len(self.button_map)):
                if message in self.button_map[i]:
                    self.relays[i].toggle()
                    reply = f"Circuit {i} toggled"
            self.send_states(reply)
            time.sleep(0.2)
    
    def send_states(self, message):
        states = ""
        for relay in self.relays:
            states = states + f"{relay.value()}"
        self.main_brain.comms.send(f"{states}|{message}")
    
    def button_1_press(self):
        self.main_brain.display.display_text("button 1")
    
    def button_2_press(self):
        self.main_brain.display.display_text("button 2")
    
    def button_3_press(self):
        self.main_brain.display.display_text("button 3")
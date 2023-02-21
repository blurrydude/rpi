from machine import Pin, PWM, I2C, RTC
from buttons import Button
import time

class SwitchBrain:
    def __init__(self, main_brain):
        self.main_brain = main_brain
        button1 = Button(16)
        button1.on_up = self.button_1_press
        button2 = Button(17)
        button2.on_up = self.button_2_press
        button3 = Button(18)
        button3.on_up = self.button_3_press
        button4 = Button(19)
        button4.on_up = self.button_4_press
        self.buttons = [
            button1,
            button2,
            button3,
            button4
        ]
    
    def start(self):
        while True:
            self.main_brain.update()
            time.sleep(0.1)
    
    def button_1_press(self):
        self.main_brain.display.display_text("button 1 pressed")
        reply = self.main_brain.comms.send_receive(self.main_brain.device_id,"0")
        self.handle_reply(reply)
    
    def button_2_press(self):
        self.main_brain.display.display_text("button 2 pressed")
        reply = self.main_brain.comms.send_receive(self.main_brain.device_id,"1")
        self.handle_reply(reply)
    
    def button_3_press(self):
        self.main_brain.display.display_text("button 3 pressed")
        reply = self.main_brain.comms.send_receive(self.main_brain.device_id,"2")
        self.handle_reply(reply)
    
    def button_4_press(self):
        self.main_brain.device_id = self.main_brain.device_id + 1
        if self.main_brain.device_id >= 64:
            self.main_brain.device_id = 0
        self.main_brain.display.display_text(f"Set device id to {self.main_brain.device_id}")
    
    def handle_reply(self, reply):
        data = reply.split('|')
        self.main_brain.circuitstates = data[0]
        self.main_brain.display.display_text(data[1])

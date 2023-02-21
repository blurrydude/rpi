from machine import Pin, UART, I2C
from ssd1306 import SSD1306_I2C
from time import time_ns, sleep
import math

class Button:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.pressed = False
        self.since_last_press = 0
        self.on_down = None
        self.on_up = None

    def update(self):
        pressed = self.pin.value() > 0
        if pressed != self.pressed:
            self.pressed = pressed
            self.since_last_press = 0
            self.handle_button()
            return True
        if self.since_last_press < 2000:
            self.since_last_press = self.since_last_press + 1
        return False

    def handle_button(self):
        if self.pressed and self.on_down is not None:
            self.on_down()
        if self.pressed is False and self.on_up is not None:
            self.on_up()


class Comms:
    def __init__(self, main_brain):
        self.brain = main_brain
        self.comms = Easy_comms(uart_id=0, baud_rate=9600)
        self.comms.start()
        
    def send_receive(self, did, message):
        self.comms.send(f"{did}|{message}")
        reply = None
        while reply is None:
            reply = self.comms.read()
        return reply
    
    def read(self):
        reply = None
        while reply is None:
            reply = self.comms.read()
        return reply
    
    def send(self, message):
        self.comms.send(message)

class Easy_comms:
 
    uart_id = 0
    baud_rate = 9600
    timeout = 1000 # milliseconds
    
    def __init__(self, uart_id:int, baud_rate:int=None):
        self.uart_id = uart_id
        if baud_rate: self.baud_rate = baud_rate

        # set the baud rate
        self.uart = UART(self.uart_id,self.baud_rate)

        # Initialise the UART serial port
        self.uart.init()
            
    def send(self, message:str):
        print(f'sending message: {message}')
        message = message + '\n'
        self.uart.write(bytes(message,'utf-8'))
        
    def start(self):
        message = "ahoy\n"
        print(message)
        #self.send(message)

    def read(self)->str:
        start_time = time_ns()
        current_time = start_time
        new_line = False
        message = ""
        while (not new_line) or (current_time <= (start_time + self.timeout)):
            if (self.uart.any() > 0):
                message = message + self.uart.read().decode('utf-8')
                if '\n' in message:
                    new_line = True
                    message = message.strip('\n')
                    # print(f'received message: {message}')
                    return message
        else:
            return None

class Display:
    def __init__(self, data_pin, clock_pin):
        i2c = I2C(0, sda=Pin(data_pin), scl=Pin(clock_pin), freq=200000)
        devices = i2c.scan()
        self.detected = True
        self.cycle = 0
        self.asleep = False
        if len(devices) == 0:
            self.detected = False
            return
        self.oled = SSD1306_I2C(128,64,i2c)
    
    def display_text(self, text, centered = False):
        if self.detected is False:
            print(text)
            return
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
            sleep(0.2)
    
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
            sleep(0.1)
    
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


class MainBrain:
    def __init__(self, device_id, relay_brain = False):
        self.device_id = device_id
        self.circuitstates = ""
        self.display = Display(8,9)
        self.comms = Comms(self)
        self.subbrain = None
        if relay_brain is True:
            self.display.display_text("I am a relay board")
            sleep(2)
            self.subbrain = RelayBoardBrain(self)
        else:
            self.display.display_text("I am a switch plate")
            sleep(2)
            self.subbrain = SwitchBrain(self)
        self.subbrain.start()
    
    def update(self):
        if self.subbrain is None:
            return
        input = False
        for button in self.subbrain.buttons:
            if button.update() is True:
                input = True
        
        self.display.update(input)


if __name__ == "__main__":
    brain = MainBrain(0, True)
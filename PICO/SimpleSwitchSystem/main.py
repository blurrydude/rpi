from machine import Pin, PWM, I2C, RTC
from buzzer import Buzzer
from sensor import Sensor
from display import Display
from comms import Comms
from relayboardbrain import RelayBoardBrain
from switchbrain import SwitchBrain
import time

class MainBrain:
    def __init__(self, device_id, relay_brain = False):
        self.device_id = device_id
        self.circuitstates = ""
        self.display = Display(8,9)
        self.buzzer = Buzzer(15)
        self.temp_sensor = Sensor()
        self.comms = Comms(self)
        self.subbrain = None
        if relay_brain is True:
            self.display.display_text("I am a relay board")
            time.sleep(2)
            self.subbrain = RelayBoardBrain(self)
        else:
            self.display.display_text("I am a switch plate")
            time.sleep(2)
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
    
    # while True:
    #     message = brain.comms.read()

    #     if message is not None:
    #         brain.display.display_text(message.strip('\n'))
        
    #     time.sleep(1)
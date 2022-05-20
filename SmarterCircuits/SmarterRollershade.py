import json
import time
import _thread
try:
    import board
    from adafruit_motorkit import MotorKit
    import RPi.GPIO as GPIO
    libraries_available = True
except:
    libraries_available = False
class RollershadeState:
    def __init__(self, name):
        self.name = name
        self.shade_up = []

class Rollershade:
    def __init__(self, mcp, name):
        self.mcp = mcp
        self.name = name
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(23, GPIO.BOTH, callback=self.break_beam_callback)
        
        self.ir_state = GPIO.input(23)

        self.kit = MotorKit(0x61)
        self.running = True
        self.read_pins = [12,16,20]#,21]
        self.motors = [
            self.kit.motor1,
            self.kit.motor2,
            self.kit.motor3
        ]
        self.moving = [
            False,
            False,
            False,
            False
        ]
        self.shade_up = [
            False,
            False,
            False
        ]
    
    def break_beam_callback(self, channel):
        self.ir_state = GPIO.input(23)
        self.state_change()

    def set_state(self, addy, state):
        if addy == 5:
            for i in range(3):
                self.set_state(i, state)
            return
        if self.moving[addy] is True:
            return
        if addy >= len(self.read_pins):
            return
        input_state = GPIO.input(self.read_pins[addy])
        if state == input_state:
            return
        if state == 0:
            _thread.start_new_thread(self.open_shade, (addy,))
        else:
            _thread.start_new_thread(self.close_shade, (addy,))

    def state_change(self):
        self.mcp.mqtt.publish("smarter_circuits/rollershade/"+self.name+"/state",json.dumps(self.shade_up))
        data = "Left shade "
        if self.shade_up[0] is True:
            data = data + "up"
        else:
            data = data + "down"
        data = data + "\nCenter shade "
        if self.shade_up[1] is True:
            data = data + "up"
        else:
            data = data + "down"
        data = data + "\nRight shade "
        if self.shade_up[2] is True:
            data = data + "up"
        else:
            data = data + "down"
        self.mcp.send_discord_message(self.mcp.discord_house_room,data)
    
    def close_shade(self, addy):
        if self.moving[addy] is True:
            return
        self.moving[addy] = True
        self.motors[addy].throttle = 1.0
        time.sleep(6)
        self.motors[addy].throttle = 0.0
        self.moving[addy] = False
        input_state = GPIO.input(self.read_pins[addy])
        self.shade_up[addy] = input_state != 1
        self.state_change()
    
    def open_shade(self, addy):
        if self.moving[addy] is True:
            return
        self.moving[addy] = True
        input_state = GPIO.input(self.read_pins[addy])
        self.motors[addy].throttle = -1.0
        start = time.time()
        while input_state == 1 and time.time() - start < 10:
            input_state = GPIO.input(self.read_pins[addy])
        self.motors[addy].throttle = 0.0
        self.moving[addy] = False
        self.shade_up[addy] = input_state != 1
        self.state_change()
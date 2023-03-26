from mycroft import MycroftSkill, intent_file_handler
import paho.mqtt.client as mqtt
import time
import _thread
import serial

class Thinker:
    def __init__(self, skill):
        self.skill = skill
        self.skill.client.on_message = self.on_message
        self.skill.client.connect('192.168.2.200')
        self.skill.client.subscribe('mycroft_out')
        _thread.start_new_thread(self.run, ())
    
    def run(self):
        self.skill.client.loop_start()
        while True:
            time.sleep(1)
    
    def on_message(self, userdata, message):
        self.speak_dialog('mqtt.send', data={
            'action': message
        })

class SendMqtt(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.client = mqtt.Client()
        self.thinker = Thinker(self)
        self.serial = serial.Serial ("/dev/ttyS0", 9600) 

    def send_pixels(self, pixels):
        c = ""
        for pixel in pixels:
            c = c + f"{pixel[0]}{pixel[1]}{pixel[2]}{pixel[3]}|"
        b = bytes(c, 'utf-8')
        self.serial.write(b)

    def smile(self, color):
        pixels = [
            [1,1,color,"7F"],
            [6,1,color,"7F"],
            [3,3,color,"7F"],
            [4,3,color,"7F"],
            [1,6,color,"7F"],
            [2,7,color,"7F"],
            [3,7,color,"7F"],
            [4,7,color,"7F"],
            [5,7,color,"7F"],
            [6,6,color,"7F"]
        ]
        self.send_pixels(pixels)

    def blank(self):
        pixels = []
        for x in range(8):
            for y in range(8):
                pixels.append([x,y,"000000","00"])
        
        self.send_pixels(pixels)

    @intent_file_handler('assistant.mqtt.intent')
    def handle_mqtt_send(self, message):
        action = message.data.get('action')

        self.smile("00FF00")
        self.client.publish('smarter_circuits/command',action)
        self.blank()

        self.speak_dialog('mqtt.send', data={
            'action': 'I have done as you asked'
        })

def create_skill():
    return SendMqtt()



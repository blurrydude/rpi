from machine import Pin, PWM, I2C, RTC
from display import Display
import network
from umqtt.simple import MQTTClient
import math
import time

# Set the SSID and passphrase of the ORBI56 network
ssid = 'SSID'
password = 'passphrase'

# Set the IP address of the MQTT broker and the topic to publish to
mqtt_server = '192.168.2.200'
mqtt_topic = b'motion/pico_motion_1'

screen = Display(8,9)

light = Pin(0, machine.Pin.OUT)
laser = Pin(1, machine.Pin.OUT)
beam_1 = Pin(19, Pin.IN, Pin.PULL_UP)
beam_2 = Pin(20, Pin.IN, Pin.PULL_UP)
motion = Pin(21, Pin.IN, Pin.PULL_DOWN)

last_state_1 = 0
last_state_2 = 0
last_motion = 0
light_on_time = 0
light_on = False

screen.display_text(f"Waiting for wifi...")

# Connect to the Wi-Fi network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, password)
cx = 0
pi = 1
# Wait for the connection to be established
while not sta_if.isconnected():
    screen.oled.pixel(cx, 64, pi)
    if cx >= 128:
        cx = 0
        if pi == 1:
            pi = 0
        else:
            pi = 1
    screen.oled.show()
    time.sleep(0.1)
    pass

screen.display_text(f"Wifi connected")
time.sleep(2)

def send_mqtt_message(topic, message):
    # Create an MQTT client and connect to the broker
    client = MQTTClient('pico', mqtt_server)
    client.connect()

    # Publish the message to the MQTT broker
    client.publish(topic.encode(), message.encode())

    # Disconnect from the MQTT broker
    client.disconnect()

#laser.value(1)
laser.value(0)
last_first = 0

while True:
    state_1 = beam_1.value()
    state_2 = beam_2.value()
    movement = motion.value()
    
    sense = False
    
    if light_on is True:
        light_on_time = light_on_time + 1
    if light_on_time > 100:
        light_on_time = 0
        light_on = False
        sense = True
        light.value(0)
    
    if state_1 != last_state_1:
        last_state_1 = state_1
    if state_2 != last_state_2:
        last_state_2 = state_2
    if state_1 == 1 and state_2 == 0:
        if last_first == 0:
            last_first = 1
    if state_1 == 0 and state_2 == 1:
        if last_first == 0:
            last_first = 2
    if state_1 == 1 and state_2 == 1:
        if last_first == 1:
            print("inbound")
            last_first = 0
        if last_first == 2:
            print("outbound")
            last_first = 0
    if last_first != 0 and state_1 == 0 and state_2 == 0:
        last_first = 0
        
    if movement != last_motion:
        last_motion = movement
        sense = True
    if sense is True:
        screen.oled.fill(0)
        a = (10,10)
        b = (118,10)
        c = (10,54)
        d = (118,54)
        screen.draw_line(a,b)
        screen.draw_line(b,d)
        screen.draw_line(d,c)
        screen.draw_line(c,a)
                
        if movement == 1:
            screen.draw_circle(64, 32, 8)
            if light_on is False:
                light_on = True
                light.value(1)
                light_on_time = 0
            send_mqtt_message('motion/pico_motion_1','active')
        else:
            send_mqtt_message('motion/pico_motion_1','inactive')
        
        screen.oled.show()
    time.sleep(0.05)


import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import socket

myname = socket.gethostname()
############# CONFIG #############
broker = "192.168.1.22"
live = True
##################################
last_press = 0
running = True
client = mqtt.Client()

circuit_state = {
    "A1": False,
    "B1": False,
    "C1": False,
    "C2": False,
    "D1": False,
    "D2": False,
    "E1": False,
    "E2": False,
    "F1": False,
    "F2": False,
    "G1": False,
    "G2": False,
    "H1": False,
    "H2": False,
    "I1": False,
    "I2": False,
    "J1": False,
    "J2": False
}

circuit = {
    "A1": {"id": "A1", "address": "shelly1pm-8CAAB574C489", "relay":"0"}, #192.168.1.60 - Fireplace Lights
    "B1": {"id": "B1", "address": "shelly1pm-84CCA8A11963", "relay":"0"}, #192.168.1.62 - Lamp Post and Driveway
    "C1": {"id": "C1", "address": "shellyswitch25-8CAAB55F44D6", "relay":"0"}, #192.168.1.243 - Porch Light
    "C2": {"id": "C2", "address": "shellyswitch25-8CAAB55F44D6", "relay":"1"}, #192.168.1.243 - Dining Room Light
    "D1": {"id": "D1", "address": "shellyswitch25-8CAAB55F405D", "relay":"0"}, #192.168.1.242 - Office Fan
    "D2": {"id": "D2", "address": "shellyswitch25-8CAAB55F405D", "relay":"1"}, #192.168.1.242 - Kitchen Lights
    "E1": {"id": "E1", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"0"}, #192.168.1.244 - Office Lights
    "E2": {"id": "E2", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"1"}, #192.168.1.244 - Unknown
    "F1": {"id": "F1", "address": "shellyswitch25-8CAAB55F4553", "relay":"0"}, #192.168.1.245 - Unknown
    "F2": {"id": "F2", "address": "shellyswitch25-8CAAB55F4553", "relay":"1"}, #192.168.1.245 - Bar Lights
    "G1": {"id": "G1", "address": "shellyswitch25-8CAAB55F44D7", "relay":"0"}, #192.168.1.61  - Unknown
    "G2": {"id": "G2", "address": "shellyswitch25-8CAAB55F44D7", "relay":"1"}, #192.168.1.61  - Unknown
    "H1": {"id": "H1", "address": "shellyswitch25-8CAAB561DDED", "relay":"0"}, #192.168.1.240 - Bathroom Lights and Fan
    "H2": {"id": "H2", "address": "shellyswitch25-8CAAB561DDED", "relay":"1"}, #192.168.1.240 - Garage Lights
    "I1": {"id": "I1", "address": "shellyswitch25-8CAAB561DDCF", "relay":"0"}, #192.168.1.241 - Master Bath Lights
    "I2": {"id": "I2", "address": "shellyswitch25-8CAAB561DDCF", "relay":"1"}, #192.168.1.241 - Stairway Lights
    "J1": {"id": "J1", "address": "shellyswitch25-8CAAB55F402F", "relay":"0"}, #192.168.1.239 - Hallway
    "J2": {"id": "J2", "address": "shellyswitch25-8CAAB55F402F", "relay":"1"} #192.168.1.239 - Master Bath Vent Fan
}
pin = {
     "4": {"switch": 1,  "circuit": ""}, # Was something else
    "17": {"switch": 2,  "circuit": "C2"},
    "27": {"switch": 3,  "circuit": ""}, # Was something else
    "22": {"switch": 4,  "circuit": "B1"},
     "5": {"switch": 5,  "circuit": "C1"},
     "6": {"switch": 6,  "circuit": "F2"},
    "13": {"switch": 7,  "circuit": "D1"},
    "19": {"switch": 8,  "circuit": "A1"},
    "26": {"switch": 9,  "circuit": "E1"},
    "18": {"switch": 10, "circuit": "D2"},
    "23": {"switch": 11, "circuit": ""}, # Was something else
    "24": {"switch": 12, "circuit": ""}, # Was something else
    "25": {"switch": 13, "circuit": ""}, # Was something else
     "8": {"switch": 14, "circuit": "H2"},
     "7": {"switch": 15, "circuit": "H1"},
    "12": {"switch": 16, "circuit": "I2"},
    "16": {"switch": 17, "circuit": "I1"},
    "20": {"switch": 18, "circuit": "J2"},
    "21": {"switch": 19, "circuit": "J1"}
}

def mosquittoMessage(message):
    mosquittoDo(myname+"/status",message)

def mosquittoDo(topic, command):
    client.publish(topic,command)

def on_message(client, userdata, message):
    global running
    result = str(message.payload.decode("utf-8"))
    print("Client: "+client)
    print("Received: "+result)
    
def do_circuit(id, milli):
    global circuit_state
    pdata = pin[id]
    if pdata["circuit"] == "":
        return
    sid = pdata["switch"]
    cid = pdata["circuit"]
    topic = "shellies/"+circuit[cid]["address"]+"/relay/"+circuit[cid]["relay"]+"/command"
    state = circuit_state[cid]
    command = ""
    if state is True:
        command = "off"
        circuit_state[cid] = False
    else:
        command = "on"
        circuit_state[cid] = True
    if live is True:
        mosquittoDo(topic,command)
    print("Switch "+str(sid)+" at "+str(milli))

def button_callback(channel):
    global last_press
    id = str(channel)
    milli = round(time.time() * 1000)
    diff = milli - last_press
    last_press = milli
    if diff > 2000:
        do_circuit(id, milli)

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(4,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(17,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(27,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(22,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(5,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(6,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(13,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(19,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(26,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(18,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(23,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(24,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(25,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(8,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(7,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(12,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(16,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(20,GPIO.RISING,callback=button_callback)
GPIO.add_event_detect(21,GPIO.RISING,callback=button_callback)


if __name__ == "__main__":
    client.on_message = on_message
    client.connect(broker)
    subscriptions = []
    for k in circuit.keys():
        c = circuit[k]
        addy = "shellies/"+c["address"]
        subscriptions.append((addy, 0))
    client.subscribe(subscriptions)
    client.loop_start()
    while running is True:
        time.sleep(5)
        mosquittoMessage("alive at "+str(round(time.time())))
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()
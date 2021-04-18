import RPi.GPIO as GPIO
import time
from datetime import datetime
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
connected = False

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
    "A1": {"id": "A1", "address": "shelly1pm-8CAAB574C489", "relay":"0"     , "pressed":0, "label":"Fireplace"}, #192.168.1.60 - Fireplace Lights
    "B1": {"id": "B1", "address": "shelly1pm-84CCA8A11963", "relay":"0"     , "pressed":0, "label":"Lamp post"}, #192.168.1.62 - Lamp Post and Driveway
    "C1": {"id": "C1", "address": "shellyswitch25-8CAAB55F44D6", "relay":"0", "pressed":0, "label":"Porch"}, #192.168.1.243 - Porch Light
    "C2": {"id": "C2", "address": "shellyswitch25-8CAAB55F44D6", "relay":"1", "pressed":0, "label":"Dining Room"}, #192.168.1.243 - Dining Room Light
    "D1": {"id": "D1", "address": "shellyswitch25-8CAAB55F405D", "relay":"0", "pressed":0, "label":"Office Fan"}, #192.168.1.242 - Office Fan
    "D2": {"id": "D2", "address": "shellyswitch25-8CAAB55F405D", "relay":"1", "pressed":0, "label":"Kitchen"}, #192.168.1.242 - Kitchen Lights
    "E1": {"id": "E1", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"0", "pressed":0, "label":"Office Lights"}, #192.168.1.244 - Office Lights
    "E2": {"id": "E2", "address": "shellyswitch25-8CAAB55F3B3F", "relay":"1", "pressed":0, "label":"Unknown 1"}, #192.168.1.244 - Unknown
    "F1": {"id": "F1", "address": "shellyswitch25-8CAAB55F4553", "relay":"0", "pressed":0, "label":"Unknown 2"}, #192.168.1.245 - Unknown
    "F2": {"id": "F2", "address": "shellyswitch25-8CAAB55F4553", "relay":"1", "pressed":0, "label":"Bar"}, #192.168.1.245 - Bar Lights
    "G1": {"id": "G1", "address": "shellyswitch25-8CAAB55F44D7", "relay":"0", "pressed":0, "label":"Unknown 3"}, #192.168.1.61  - Unknown
    "G2": {"id": "G2", "address": "shellyswitch25-8CAAB55F44D7", "relay":"1", "pressed":0, "label":"Unknown 4"}, #192.168.1.61  - Unknown
    "H1": {"id": "H1", "address": "shellyswitch25-8CAAB561DDED", "relay":"0", "pressed":0, "label":"Guest Bathroom"}, #192.168.1.240 - Bathroom Lights and Fan
    "H2": {"id": "H2", "address": "shellyswitch25-8CAAB561DDED", "relay":"1", "pressed":0, "label":"Garage Lights"}, #192.168.1.240 - Garage Lights
    "I1": {"id": "I1", "address": "shellyswitch25-8CAAB561DDCF", "relay":"0", "pressed":0, "label":"Master Bath"}, #192.168.1.241 - Master Bath Lights
    "I2": {"id": "I2", "address": "shellyswitch25-8CAAB561DDCF", "relay":"1", "pressed":0, "label":"Stairway"}, #192.168.1.241 - Stairway Lights
    "J1": {"id": "J1", "address": "shellyswitch25-8CAAB55F402F", "relay":"0", "pressed":0, "label":"Hallway"}, #192.168.1.239 - Hallway
    "J2": {"id": "J2", "address": "shellyswitch25-8CAAB55F402F", "relay":"1", "pressed":0, "label":"Shower Fan"} #192.168.1.239 - Master Bath Vent Fan
}
reverse_lookup = {} #I can't figure out a better or faster way
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
    try:
        client.connect(broker)
        client.publish(topic,command)
        client.disconnect()
    except:
        print("BAD - Failed to publish "+command+" to "+topic)

def on_message(client, userdata, message):
    global running
    result = str(message.payload.decode("utf-8"))
    topic = message.topic
    cid = reverse_lookup[topic]
    if result == "on":
        circuit_state[cid] = True
    else:
        circuit_state[cid] = False
    
def do_circuit(id, ts):
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
    dt_object = datetime.fromtimestamp(ts)
    print(circuit[cid]["label"]+" "+command+" at "+str(dt_object))

def getTimeStamp():
    return time.time()

def button_callback(channel):
    global last_press
    id = str(channel)
    ts = getTimeStamp()
    if ts > last_press+1.5:
        tap(id, ts)
        last_press = ts

def tap(id, ts):
    do_circuit(id, ts)
#     pdata = pin[id]
#     cid = pdata["circuit"]
#     if circuit[cid]["pressed"] > 0:
#         circuit[cid]["pressed"] = 0
#         print("switch "+cid+" confirmed")
#         do_circuit(id, ts)
#     else:
#         circuit[cid]["pressed"] = ts
#         print("switch "+cid+" pressed")
#     limit = ts - 3
#     for ck in circuit.keys():
#         if ck != cid and circuit[ck]["pressed"] != 0 and circuit[ck]["pressed"] < limit:
#             circuit[ck]["pressed"] = 0
#             print("switch "+str(circuit[ck]["id"])+" cleared")
        

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

GPIO.add_event_detect(4,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(17,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(27,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(22,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(5,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(6,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(13,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(19,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(26,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(18,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(23,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(24,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(25,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(8,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(7,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(12,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(16,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(20,GPIO.FALLING,callback=button_callback)
GPIO.add_event_detect(21,GPIO.FALLING,callback=button_callback)


if __name__ == "__main__":
    #subscriptions = []
    #for k in circuit.keys():
    #    c = circuit[k]
    #    addy = "shellies/"+c["address"]+"/relay/"+c["relay"]
    #    print("preparing "+addy)
    #    subscriptions.append((addy, 0))
    #    reverse_lookup[addy] = k
    start = time.time()
    last_pulse = start
    while running is True:
        while connected is False:
            try:
                #client.on_message = on_message
                #client.connect(broker)
                #client.subscribe(subscriptions)
                #client.loop_start()
                connected = True
            except:
                print("BAD - client failed connection. Will try again in five seconds")
                connected = False
                time.sleep(5)
        now = time.time()
        if now - last_pulse >= 5:
            mosquittoMessage("alive at "+str(round(time.time())))
            last_pulse = now
        
    #try:
        #client.loop_stop()
        #client.disconnect()
    #except:
        #print("INFO - Client diconnet failed. Maybe, the connection failed first or during runtime.")
    GPIO.cleanup()
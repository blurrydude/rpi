import paho.mqtt.client as mqtt
import time
import json
import os

running = True

client = mqtt.Client()

def on_message(client, userdata, message):
    global running
    data = str(message.payload.decode("utf-8"))
    bits = message.topic.split('/')
    address = bits[1]
    property = message.topic.replace("shellies/"+address+"/","").replace("/","_")
    filename = "circuitstate_"+address+".json"
    if os.path.exists(filename):
        read_file = open(filename)
        state = json.load(read_file)
    else:
        state = {}
    state[property] = data
    write_file = open(filename, "w")
    json.dump(obj=state, fp=write_file)

if __name__ == "__main__":
    client.on_message = on_message
    client.connect('192.168.0.8')
    client.subscribe("shellies/#")
    client.loop_start()
    while running is True:
        time.sleep(1)
    client.loop_stop()
    client.disconnect()
from flask_api import FlaskAPI
import paho.mqtt.client as mqtt
import os
import json

def mosquittoDo(topic, command):
    try:
        client = mqtt.Client()
        client.connect("192.168.0.8")
        client.publish(topic,command)
        client.disconnect()
    except:
        print('failed')
    return 'OK'

app = FlaskAPI(__name__)

circuits = {
    "reading_light": {
        "address": "shelly1pm-8CAAB55F83AA",
        "relay": "0"
    }
}

@app.route('/states')
def states():
    ext = ('.json')
    states = {}
    for f in os.listdir():
        if f.endswith(ext) and "circuitstate_" in f:
            a = f.split("_")
            b = a[1].split(".")
            address = b[0]
            x = open(f)
            circuit = json.load(x)
            states[address] = circuit
        else:
            continue
    return states

@app.route('/control/<text>')
def control(text):
    command = text.lower()
    state = "off"
    command_list = []
    if "on" in command:
        state = "on"
    if "turn" in command:
        for circuit in circuits.keys():
            c = circuits[circuit]
            if circuit.lower().replace('_',' ') in command:
                topic = "shellies/"+c["address"]+"/relay/"+c["relay"]+"/command"
                command_list.append({"t":topic,"c":state})
    for cmd in command_list:
        mosquittoDo(cmd["t"],cmd["c"])
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')


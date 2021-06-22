from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask_cors import CORS
import paho.mqtt.client as mqtt
import time

class KeywordTopic:
  def __init__(self, keyword, topic):
    self.keyword = keyword
    self.topic = topic

class MosquittoCommand:
  def __init__(self, keyword, topic, command):
    self.keyword = keyword
    self.topic = topic
    self.command = command

received = False
result = "none"
keywordTopics = [
    #KeywordTopic("ocean", "shellies/shelly1pm-84CCA8A11963/relay/0/command"),
    #KeywordTopic("shop fan", "shellies/shelly1pm-8CAAB574C489/relay/0/command"),
    #KeywordTopic("fireplace light", "shellies/shellyswitch25-8CAAB55F44D7/relay/0/command"),
    #KeywordTopic("dining room light", "shellies/shellyswitch25-8CAAB55F44D7/relay/0/command")
]
circuit = {
    "A1": {"id": "A1", "address": "shelly1pm-8CAAB574C489",      "relay":"0"}, #192.168.1.60 - Fireplace Lights
    "B1": {"id": "B1", "address": "shelly1pm-84CCA8A11963",      "relay":"0"}, #192.168.1.62 - Lamp Post and Driveway
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
mqttCommands = [
    MosquittoCommand("open bay one", "garagepi/commands", "0:1"),
    MosquittoCommand("close bay one", "garagepi/commands", "0:0"),
    MosquittoCommand("open bay 1", "garagepi/commands", "0:1"),
    MosquittoCommand("close bay 1", "garagepi/commands", "0:0"),
    MosquittoCommand("close bay two", "garagepi/commands", "1:0"),
    MosquittoCommand("open bay two", "garagepi/commands", "1:1"),
    MosquittoCommand("close bay to", "garagepi/commands", "1:0"),
    MosquittoCommand("open bay to", "garagepi/commands", "1:1"),
    MosquittoCommand("close bay 2", "garagepi/commands", "1:0"),
    MosquittoCommand("open bay 2", "garagepi/commands", "1:1"),
    MosquittoCommand("open garage door one", "garagepi/commands", "0:1"),
    MosquittoCommand("close garage door one", "garagepi/commands", "0:0"),
    MosquittoCommand("open garage door 1", "garagepi/commands", "0:1"),
    MosquittoCommand("close garage door 1", "garagepi/commands", "0:0"),
    MosquittoCommand("close garage door two", "garagepi/commands", "1:0"),
    MosquittoCommand("open garage door two", "garagepi/commands", "1:1"),
    MosquittoCommand("close garage door to", "garagepi/commands", "1:0"),
    MosquittoCommand("open garage door to", "garagepi/commands", "1:1"),
    MosquittoCommand("close garage door 2", "garagepi/commands", "1:0"),
    MosquittoCommand("open garage door 2", "garagepi/commands", "1:1"),
    MosquittoCommand("open garage door right", "garagepi/commands", "0:1"),
    MosquittoCommand("close garage door right", "garagepi/commands", "0:0"),
    MosquittoCommand("close garage door left", "garagepi/commands", "1:0"),
    MosquittoCommand("open garage door left", "garagepi/commands", "1:1"),
    MosquittoCommand("close shop door", "garagepi/commands", "1:0"),
    MosquittoCommand("open shop door", "garagepi/commands", "1:1"),
    MosquittoCommand("start ocean", "whitenoisepi/commands", "start"),
    MosquittoCommand( "stop ocean", "whitenoisepi/commands", "stop"),
    MosquittoCommand("on ocean", "whitenoisepi/commands", "on"),
    MosquittoCommand( "off ocean", "whitenoisepi/commands", "off"),
    #MosquittoCommand("start bedroom fan", "shellies/shelly1pm-/relay/0/command", "on"),
    #MosquittoCommand( "stop bedroom fan", "shellies/shelly1pm-/relay/0/command", "off"),
    #MosquittoCommand("start library fan", "shellies/shelly1pm-/relay/0/command", "on"),
    #MosquittoCommand( "stop library fan", "shellies/shelly1pm-/relay/0/command", "off"),
    MosquittoCommand("start office fan", "shellies/shellyswitch25-8CAAB55F405D/relay/0/command", "on"),
    MosquittoCommand( "stop office fan", "shellies/shellyswitch25-8CAAB55F405D/relay/0/command", "off"),
    MosquittoCommand("start shower fan", "shellies/shellyswitch25-8CAAB55F402F/relay/1/command", "on"),
    MosquittoCommand( "stop shower fan", "shellies/shellyswitch25-8CAAB55F402F/relay/1/command", "off"),
    MosquittoCommand("turn on office fan", "shellies/shellyswitch25-8CAAB55F405D/relay/0/command", "on"),
    MosquittoCommand("turn off office fan", "shellies/shellyswitch25-8CAAB55F405D/relay/0/command", "off"),
    MosquittoCommand("turn on shower fan", "shellies/shellyswitch25-8CAAB55F402F/relay/1/command", "on"),
    MosquittoCommand("turn off shower fan", "shellies/shellyswitch25-8CAAB55F402F/relay/1/command", "off"),
    MosquittoCommand("turn on fireplace", "shellies/shelly1pm-8CAAB574C489/relay/0/command", "on"),
    MosquittoCommand(    "turn off fireplace", "shellies/shelly1pm-8CAAB574C489/relay/0/command", "off"),
    MosquittoCommand("turn on dining room", "shellies/shellyswitch25-8CAAB55F44D6/relay/1/command", "on"),
    MosquittoCommand(    "turn off dining room", "shellies/shellyswitch25-8CAAB55F44D6/relay/1/command", "off"),
    #MosquittoCommand("turn on bedroom", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off bedroom", "shellies/shellyswitch25-/relay/0/command", "off"),
    #MosquittoCommand("turn on library", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off library", "shellies/shellyswitch25-/relay/0/command", "off"),
    #MosquittoCommand("turn on workout room", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off workout room", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("turn on hallway", "shellies/shellyswitch25-8CAAB55F402F/relay/0/command", "on"),
    MosquittoCommand(    "turn off hallway", "shellies/shellyswitch25-8CAAB55F402F/relay/0/command", "off"),
    MosquittoCommand("turn on master bath", "shellies/shellyswitch25-8CAAB561DDCF/relay/0/command", "on"),
    MosquittoCommand(    "turn off master bath", "shellies/shellyswitch25-8CAAB561DDCF/relay/0/command", "off"),
    MosquittoCommand("turn on guest bath", "shellies/shellyswitch25-8CAAB561DDED/relay/0/command", "on"),
    MosquittoCommand(    "turn off guest bath", "shellies/shellyswitch25-8CAAB561DDED/relay/0/command", "off"),
    #MosquittoCommand("turn on living room", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off living room", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("turn on kitchen", "shellies/shellyswitch25-8CAAB55F405D/relay/1/command", "on"),
    MosquittoCommand(    "turn off kitchen", "shellies/shellyswitch25-8CAAB55F405D/relay/1/command", "off"),
    MosquittoCommand("turn on bar", "shellies/shellyswitch25-8CAAB55F4553/relay/1/command", "on"),
    MosquittoCommand(    "turn off bar", "shellies/shellyswitch25-8CAAB55F4553/relay/1/command", "off"),
    MosquittoCommand("turn on office", "shellies/shellyswitch25-8CAAB55F3B3F/relay/0/command", "on"),
    MosquittoCommand(    "turn off office", "shellies/shellyswitch25-8CAAB55F3B3F/relay/0/command", "off"),
    MosquittoCommand("turn on unknown one", "shellies/shellyswitch25-8CAAB55F3B3F/relay/1/command", "on"),
    MosquittoCommand(    "turn off unknown one", "shellies/shellyswitch25-8CAAB55F3B3F/relay/1/command", "off"),
    MosquittoCommand("turn on unknown two", "shellies/shellyswitch25-8CAAB55F4553/relay/0/command", "on"),
    MosquittoCommand(    "turn off unknown two", "shellies/shellyswitch25-8CAAB55F4553/relay/0/command", "off"),
    MosquittoCommand("turn on unknown three", "shellies/shellyswitch25-8CAAB55F44D7/relay/0/command", "on"),
    MosquittoCommand(    "turn off unknown three", "shellies/shellyswitch25-8CAAB55F44D7/relay/0/command", "off"),
    MosquittoCommand("turn on unknown four", "shellies/shellyswitch25-8CAAB55F44D7/relay/1/command", "on"),
    MosquittoCommand(    "turn off unknown four", "shellies/shellyswitch25-8CAAB55F44D7/relay/1/command", "off"),
    #MosquittoCommand("turn on table one", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off table one", "shellies/shellyswitch25-/relay/0/command", "off"),
    #MosquittoCommand("turn on table two", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off table two", "shellies/shellyswitch25-/relay/0/command", "off"),
    #MosquittoCommand("turn on pool table", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off pool table", "shellies/shellyswitch25-/relay/0/command", "off"),
    #MosquittoCommand("turn on deck", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off deck", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("turn on porch", "shellies/shellyswitch25-8CAAB55F44D6/relay/0/command", "on"),
    MosquittoCommand(    "turn off porch", "shellies/shellyswitch25-8CAAB55F44D6/relay/0/command", "off"),
    MosquittoCommand("turn on lamp post", "shellies/shelly1pm-84CCA8A11963/relay/0/command", "on"),
    MosquittoCommand(    "turn off lamp post", "shellies/shelly1pm-84CCA8A11963/relay/0/command", "off"),
    #MosquittoCommand("turn on driveway", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off driveway", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("turn on garage", "shellies/shellyswitch25-8CAAB561DDED/relay/1/command", "on"),
    MosquittoCommand(    "turn off garage", "shellies/shellyswitch25-8CAAB561DDED/relay/1/command", "off"),
    MosquittoCommand("turn on stairs", "shellies/shellyswitch25-8CAAB561DDCF/relay/1/command", "on"),
    MosquittoCommand(    "turn off stairs", "shellies/shellyswitch25-8CAAB561DDCF/relay/1/command", "off"),
    MosquittoCommand("turn on shop", "shellies/shellyswitch25-8CAAB561DDED/relay/1/command", "on"),
    MosquittoCommand(    "turn off shop", "shellies/shellyswitch25-8CAAB561DDED/relay/1/command", "off"),
    #MosquittoCommand("turn on electronics room", "shellies/shellyswitch25-/relay/0/command", "on"),
    #MosquittoCommand(    "turn off electronics room", "shellies/shellyswitch25-/relay/0/command", "off")
]

mqttCommands.append(MosquittoCommand("set bedroom color black", "windowpi/commands", "0:0:0:0"))
mqttCommands.append(MosquittoCommand("set bedroom color full",  "windowpi/commands", "0:255:255:255"))
mqttCommands.append(MosquittoCommand("set bedroom color gradient",  "windowpi/commands", "3:0"))
mqttCommands.append(MosquittoCommand("set bedroom color rainbow",  "windowpi/commands", "4:0"))
mqttCommands.append(MosquittoCommand("set game room color black", "clockpi/commands", "0:0:0:0"))
mqttCommands.append(MosquittoCommand("set game room color full",  "clockpi/commands", "0:255:255:255"))
mqttCommands.append(MosquittoCommand("set game room color gradient",  "clockpi/commands", "3:0"))
mqttCommands.append(MosquittoCommand("set game room color rainbow",  "clockpi/commands", "4:0"))
mqttCommands.append(MosquittoCommand("set canvas color black", "canvaspi/commands", "0:0:0:0"))
mqttCommands.append(MosquittoCommand("set canvas color full",  "canvaspi/commands", "0:255:255:255"))
mqttCommands.append(MosquittoCommand("set canvas color gradient",  "canvaspi/commands", "3:0"))
mqttCommands.append(MosquittoCommand("set canvas color rainbow",  "canvaspi/commands", "4:0"))
## Load colors dynamically because I'm too lazy to code it all out
colors = ["green","yellow","white","blue","red","purple","orange"]
rgb = ["0:192:0","96:96:0","64:64:64","0:0:192","192:0:0","96:0:96","128:64:0"]
brightrgb = ["0:255:0","255:255:0","128:128:128","0:0:255","255:0:0","255:0:255","255:128:0"]
i = 0
for color in colors:
    mqttCommands.append(MosquittoCommand("set bedroom color bright "+color, "windowpi/commands", "0:" + brightrgb[i]))
    mqttCommands.append(MosquittoCommand("set bedroom color "+color, "windowpi/commands", "0:" + rgb[i]))
    mqttCommands.append(MosquittoCommand("set game room color bright "+color, "clockpi/commands", "0:" + brightrgb[i]))
    mqttCommands.append(MosquittoCommand("set game room color "+color, "clockpi/commands", "0:" + rgb[i]))
    mqttCommands.append(MosquittoCommand("set canvas color bright "+color, "canvaspi/commands", "0:" + brightrgb[i]))
    mqttCommands.append(MosquittoCommand("set canvas color "+color, "canvaspi/commands", "0:" + rgb[i]))
    i = i + 1

def on_message(client, userdata, message):
    global received
    global result
    result = str(message.payload.decode("utf-8"))
    print("message received ", result)
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    received = True

def mosquittoDo(topic, command):
    global received
    global result
    client = mqtt.Client()
    client.connect("192.168.1.22")
    client.publish(topic,command)
    client.disconnect()
    return 'OK'

app = FlaskAPI(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/circuit/<cid>/<action>')
def action(cid, action):
    mosquittoDo("shellies/"+circuit[cid]["address"]+"/relay/"+circuit[cid]["relay"]+"/command",action)
    return 'OK'

@app.route('/control/<text>')
def control(text):
    command = text.lower()
    mosquittoDo("incoming/commands", command)
    if "switch to" in command:
        if "night mode" in command:
            control("turn off shop")
            control("turn on stairs")
            control("turn on porch")
            control("turn on lamp post")
            control("turn off kitchen")
            control("turn off bar")
            control("turn off fireplace")
            control("turn off office")
            control("turn off dining room")
            control("turn off guest bathroom")
            control("turn off hallway")
            control("turn off shower fan")
            control("turn off master bath")
            return 'OK'
        if "evening mode" in command:
            control("turn off shop")
            control("turn on stairs")
            control("turn on porch")
            control("turn on lamp post")
            control("turn off kitchen")
            control("turn off bar")
            control("turn on fireplace")
            control("turn off office")
            control("turn off dining room")
            control("turn off guest bathroom")
            control("turn off hallway")
            control("turn off shower fan")
            control("turn on master bath")
            return 'OK'
        if "morning mode" in command:
            control("turn on shop")
            control("turn off stairs")
            control("turn on kitchen")
            control("turn on bar")
            control("turn off fireplace")
            control("turn off office")
            control("turn off dining room")
            control("turn off guest bathroom")
            control("turn off hallway")
            control("turn off shower fan")
            control("turn off master bath")
            return 'OK'
        if "lunch mode" in command:
            control("turn on kitchen")
            control("turn on bar")
            control("turn on dining room")
            return 'OK'
        if "shower mode" in command:
            control("turn on shower fan")
            control("turn on master bath")
            return 'OK'
    for cmd in mqttCommands:
        words = cmd.keyword.split(' ')
        count = 0
        for word in words:
            if word in command:
                count = count + 1
        if count == len(words):
            mosquittoDo(cmd.topic, cmd.command)
    return 'OK'

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='192.168.1.23')


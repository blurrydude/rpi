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
    MosquittoCommand("start ocean", "shellies/shelly1pm-84CCA8A11963/relay/0/command", "on"),
    MosquittoCommand( "stop ocean", "shellies/shelly1pm-84CCA8A11963/relay/0/command", "off"),
    MosquittoCommand("on ocean", "shellies/shelly1pm-84CCA8A11963/relay/0/command", "on"),
    MosquittoCommand( "off ocean", "shellies/shelly1pm-84CCA8A11963/relay/0/command", "off"),
    MosquittoCommand("start shop fan", "shellies/shelly1pm-8CAAB574C489/relay/0/command", "on"),
    MosquittoCommand( "stop shop fan", "shellies/shelly1pm-8CAAB574C489/relay/0/command", "off"),
    MosquittoCommand("on shop fan", "shellies/shelly1pm-8CAAB574C489/relay/0/command", "on"),
    MosquittoCommand( "off shop fan", "shellies/shelly1pm-8CAAB574C489/relay/0/command", "off"),
    MosquittoCommand("start bedroom fan", "shellies/shelly1pm-/relay/0/command", "on"),
    MosquittoCommand( "stop bedroom fan", "shellies/shelly1pm-/relay/0/command", "off"),
    MosquittoCommand("start library fan", "shellies/shelly1pm-/relay/0/command", "on"),
    MosquittoCommand( "stop library fan", "shellies/shelly1pm-/relay/0/command", "off"),
    MosquittoCommand("start office fan", "shellies/shelly1pm-/relay/0/command", "on"),
    MosquittoCommand( "stop office fan", "shellies/shelly1pm-/relay/0/command", "off"),
    MosquittoCommand("illuminate fireplace", "shellies/shellyswitch25-8CAAB55F44D7/relay/0/command", "on"),
    MosquittoCommand(    "darken fireplace", "shellies/shellyswitch25-8CAAB55F44D7/relay/0/command", "off"),
    MosquittoCommand("illuminate dining room", "shellies/shellyswitch25-8CAAB55F44D7/relay/0/command", "on"),
    MosquittoCommand(    "darken dining room", "shellies/shellyswitch25-8CAAB55F44D7/relay/0/command", "off"),
    MosquittoCommand("illuminate bedroom", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken bedroom", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate library", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken library", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate workout room", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken workout room", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate hallway", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken hallway", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate master bath", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken master bath", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate bathroom", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken bathroom", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate living room", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken living room", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate kitchen", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken kitchen", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate bar", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken bar", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate office", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken office", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate table one", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken table one", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate table two", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken table two", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate pool table", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken pool table", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate deck", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken deck", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate porch", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken porch", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate lamp post", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken lamp post", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate driveway", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken driveway", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate garage", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken garage", "shellies/shellyswitch25-/relay/0/command", "off"),
    MosquittoCommand("illuminate electronics room", "shellies/shellyswitch25-/relay/0/command", "on"),
    MosquittoCommand(    "darken electronics room", "shellies/shellyswitch25-/relay/0/command", "off")
]

mqttCommands.append(MosquittoCommand("set bedroom color black", "windowpi/commands", "*,0,0,0"))
mqttCommands.append(MosquittoCommand("set bedroom color full",  "windowpi/commands", "*,255,255,255"))
mqttCommands.append(MosquittoCommand("set game room color black", "clockpi/commands", "*,0,0,0"))
mqttCommands.append(MosquittoCommand("set game room color full",  "clockpi/commands", "*,255,255,255"))
mqttCommands.append(MosquittoCommand("set canvas color black", "canvaspi/commands", "*,0,0,0"))
mqttCommands.append(MosquittoCommand("set canvas color full",  "canvaspi/commands", "*,255,255,255"))
## Load colors dynamically because I'm too lazy to code it all out
colors = ["green","yellow","white","blue","red","purple","orange"]
rgb = ["0,192,0","96,96,0","64,64,64","0,0,192","192,0,0","96,0,96","128,64,0"]
brightrgb = ["0,255,0","255,255,0","128,128,128","0,0,255","255,0,0","255,0,255","255,128,0"]
i = 0
for color in colors:
    mqttCommands.append(MosquittoCommand("set bedroom color bright "+color, "windowpi/commands", "*," + brightrgb[i]))
    mqttCommands.append(MosquittoCommand("set bedroom color "+color, "windowpi/commands", "*," + rgb[i]))
    mqttCommands.append(MosquittoCommand("set game room color bright "+color, "clockpi/commands", "*," + brightrgb[i]))
    mqttCommands.append(MosquittoCommand("set game room color "+color, "clockpi/commands", "*," + rgb[i]))
    mqttCommands.append(MosquittoCommand("set canvas color bright "+color, "canvaspi/commands", "*," + brightrgb[i]))
    mqttCommands.append(MosquittoCommand("set canvas color "+color, "canvaspi/commands", "*," + rgb[i]))
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

@app.route('/mqtt/<deviceId>/<address>/<action>')
def action(deviceId, address, action):
    mosquittoDo("shellies/"+deviceId+"/relay/"+address+"/command",action)
    return 'OK'

@app.route('/control/<text>')
def control(text):
    command = text.lower()
    mosquittoDo("incoming/commands", command)
    for cmd in mqttCommands:
        words = cmd.keyword.split(' ')
        count = 0
        for word in words:
            if word in command:
                count = count + 1
        if count == len(words):
            mosquittoDo(cmd.topic, cmd.command)
            return 'OK'
    return 'NO'

if __name__ == '__main__':
    app.run(debug=False, port=8080, host='192.168.1.23')


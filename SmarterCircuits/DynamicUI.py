#! /usr/bin/env python3
import time
from tkinter import * 
import json
import paho.mqtt.client as mqtt
import datetime
import os

from ShellyDevices import RelayModule

root = os.path.dirname(os.path.realpath(__file__))+"/" #'C:\\Code\\rpi\\SmarterCircuits\\'

client = mqtt.Client()
master = Tk() 
master.configure(bg='black')
base_width = 800
base_height = 600
circuit_button_x = 690
circuit_button_width = 250
circuit_button_height = 48
circuit_button_y_start = 35
circuit_button_font_size = 20
info_block_x = 20
info_block_y = 600
info_block_font_size = 20
info_block_spacing = 32
points_scale = 1

show_points = False
show_room_names = False

selected_room = ""
room_circuits = []
circuits = []

points = []
lines = []
rooms = []

roomstats = {}
last_notification = ""

def on_message(client, userdata, message):
    global roomstats
    global last_notification
    result = str(message.payload.decode("utf-8"))
    topic = message.topic.split('/')
    if topic[0] == "notifications":
        if message != last_notification:
            last_notification = message
            draw_all()
        return
    if topic[0] == "shellies":
        handle_shelly_message(message.topic, result)
        return
    data = json.loads(result)
    if topic[1] == 'sensors':
        temp = round(data['temp'],2)
        hum = round(data['hum'],2)
        if topic[2] not in roomstats.keys() or roomstats[topic[2]]["temp"] != temp:
            roomstats[topic[2]] = {"temp":temp, "hum": hum}
            draw_all()
    elif topic[1] == 'thermostats':
        temp = data['state']['temperature']
        hum = data['state']['humidity']
        if topic[2] not in roomstats.keys() or roomstats[topic[2]]["temp"] != temp:
            roomstats[topic[2]] = {"temp":temp, "hum": hum}
            draw_all()

def click(event):
    global show_points
    global show_room_names
    x, y = event.x, event.y
    #print('{}, {}'.format(x, y))
    if x > base_width - 10 and y < 10:
        show_points = show_points == False
        master.attributes('-fullscreen', show_points == False)
        draw_all()
        return
    if x < 10 and y < 10:
        show_room_names = show_room_names == False
        draw_all()
        return
    for room in rooms:
        rectangles = room["rectangles"]
        init = False
        for rectangle in rectangles:
            a = points[rectangle[0]]
            b = points[rectangle[1]]
            if x >= a[0] and x <= b[0] and y >= a[1] and y <= b[1]:
                init = True
        if init:
            click_room(room)
            return
    
    c = 0
    for circuit in room_circuits:
        rx1 = circuit_button_x
        ry1 = circuit_button_y_start+(c*(circuit_button_height+8))
        rx2 = rx1 + circuit_button_width
        ry2 = ry1 + circuit_button_height
        c = c + 1
        if x >= rx1 and x <= rx2 and y >= ry1 and y <= ry2:
            click_circuit(circuit)
            return

def click_circuit(circuit):
    #print(circuit.name+" clicked")
    client.publish('smarter_circuits/commands','toggle '+circuit.name.lower())

def click_room(room):
    global selected_room
    global room_circuits
    if room["name"] == "":
        return
    #print(room["name"]+" clicked")
    selected_room = room["name"]
    
    room_circuits = []
    for circuit in circuits:
        if room["name"] in circuit.zones:
            #print(circuit)
            room_circuits.append(circuit)
    
    draw_all()

def rect(top_left, bottom_right, fill):
    x1 = top_left[0]
    y1 = top_left[1]
    x2 = bottom_right[0]
    y2 = bottom_right[1]
    canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=fill)

def draw_room(room):
    rectangles = room["rectangles"]
    name = room["name"]
    color = room["color"]
    for rectangle in rectangles:
        a = points[rectangle[0]]
        b = points[rectangle[1]]
        rect(a,b,color)
    tl = points[rectangles[0][0]]
    br = points[rectangles[0][1]]
    x = tl[0] + ((br[0] - tl[0]) /2)
    y = points[rectangles[0][0]][1] + 12
    if show_room_names and name != '':
        canvas.create_text(x,y,text=name,fill='black')

def draw_all():
    global canvas
    load_config()
    canvas.destroy()
    canvas = Canvas(master, width=base_width, height=base_height, bg='black') 
    canvas.place(x=0, y=0) 
    canvas.create_rectangle(0, 0, base_width, base_height, fill="black", outline="black")
    
    for room in rooms:
        draw_room(room)

    for line in lines:
        a = points[line[0]]
        b = points[line[1]]
        canvas.create_line(a[0],a[1],b[0],b[1],fill='black',width=2)

    if show_points:
        i = 0
        for point in points:
            x = point[0]
            y = point[1]
            canvas.create_rectangle(x,y,x+1,y+1, fill="green", outline="green") 
            tx = x
            ty = y - 8
            canvas.create_text(tx,ty,text=str(i),fill='white')
            i = i + 1
    
    if selected_room != "":
        canvas.create_text(circuit_button_x+(circuit_button_width/2),15,text=selected_room,fill='white')
    
    c = 0
    for circuit in room_circuits:
        y = circuit_button_y_start+(c*(circuit_button_height+8))
        fill = "red"
        if circuit.status.relay.on:
            fill = "green"
        watts = circuit.status.relay.power
        canvas.create_rectangle(circuit_button_x,y,circuit_button_x+circuit_button_width,y+circuit_button_height, fill=fill, outline="gray") 
        canvas.create_text(circuit_button_x+(circuit_button_width/2),y+(circuit_button_height/2),text=circuit.name+" ~ "+str(round(watts))+"W",fill='black',font="Times "+str(circuit_button_font_size))
        c = c + 1
    
    c = 0
    y = info_block_y
    for room in roomstats.keys():
        canvas.create_text(info_block_x,y,text=room+": "+str(round(roomstats[room]["temp"],2)),fill='white',anchor='nw',font='times '+str(info_block_font_size))
        y = y + info_block_spacing
        c = c + 1
    
    canvas.create_text(info_block_x,y,text="Notification: "+last_notification,fill='yellow',anchor='nw',font='times '+str(info_block_font_size))

def load_config():
    global points
    global lines
    global rooms
    global circuit_button_x
    global circuit_button_width
    global circuit_button_height
    global circuit_button_y_start
    global circuit_button_font_size
    global info_block_x
    global info_block_y
    global info_block_font_size
    global info_block_spacing
    global points_scale
    global base_width
    global base_height
    config_data = open(root+'DynamicUI.json')
    config = json.load(config_data)
    points = config["points"]
    for point in points:
        point[0] = point[0] * points_scale
        point[1] = point[1] * points_scale
    lines = config["lines"]
    rooms = config["rooms"]
    circuit_button_x = config["circuit_button_x"]
    circuit_button_width = config["circuit_button_width"]
    circuit_button_height = config["circuit_button_height"]
    circuit_button_y_start = config["circuit_button_y_start"]
    circuit_button_font_size = config["circuit_button_font_size"]
    info_block_x = config["info_block_x"]
    info_block_y = config["info_block_y"]
    info_block_font_size = config["info_block_font_size"]
    info_block_spacing = config["info_block_spacing"]
    points_scale = config["points_scale"]
    if config["base_width"] != base_width:
        base_width = config["base_width"]
        base_height = config["base_height"]
        master.geometry(str(base_width)+"x"+str(base_height))

def handle_shelly_message(topic, message):
    s = topic.split('/')
    id = s[1]
    if "pro4pm" in id:
        handle_shelly_pro4pm_message(id, topic.replace("shellies/"+id+"/",""), message)
    if "1pm" in id or "switch25" in id:
        handle_shelly_relay_message(id, topic.replace("shellies/"+id+"/",""), message)
    if "dimmer2" in id:
        handle_shelly_dimmer_message(id, topic.replace("shellies/"+id+"/",""), message)
    return

def update_circuit(id, on = None, power = None, voltage = None):
    for circuit in circuits:
        if(circuit.id != id):
            continue

def handle_shelly_pro4pm_message(id, topic, message):
    if "status" not in topic:
        return
    data = json.loads(message)
    for circuit in circuits:
        if(circuit.id != id):
            continue
        if(int(circuit.relay_id) != data["id"]):
            continue
        circuit.status.relay.on = data["output"]
        on = data["output"]
        if on != circuit.status.relay.on:
            circuit.status.relay.on = data["output"]
            check_room_states(circuit.name)
        power = data["apower"]
        if power != circuit.status.relay.power:
            circuit.status.relay.power = power
        circuit.status.relay.energy = data["current"]
        circuit.status.temperature = data["temperature"]["tC"]
        circuit.status.temperature_f = data["temperature"]["tF"]
        circuit.status.voltage = data["voltage"]

def handle_shelly_dimmer_message(id, subtopic, message):
    for circuit in circuits:
        if(circuit.id != id):
            continue
        if subtopic == "light/"+circuit.relay_id:
            on = message == "on"
            if on != circuit.status.relay.on:
                circuit.status.relay.on = message == "on"
                check_room_states(circuit.name)
        if subtopic == "light/"+circuit.relay_id+"/power":
            power = float(message)
            if power != circuit.status.relay.power:
                circuit.status.relay.power = power
        if subtopic == "light/"+circuit.relay_id+"/energy":
            circuit.status.relay.energy = int(message)
        if subtopic == "temperature":
            circuit.status.temperature = float(message)
        if subtopic == "temperature_f":
            circuit.status.temperature_f = float(message)
        if subtopic == "overtemperature":
            circuit.status.overtemperature = int(message)
        if subtopic == "temperature_status":
            circuit.status.temperature = message
        if subtopic == "voltage":
            circuit.status.voltage = float(message)  

def handle_shelly_relay_message(id, subtopic, message):
    for circuit in circuits:
        if(circuit.id != id):
            continue
        if subtopic == "relay/"+circuit.relay_id:
            on = message == "on"
            if on != circuit.status.relay.on:
                circuit.status.relay.on = message == "on"
                check_room_states(circuit.name)
        if subtopic == "relay/"+circuit.relay_id+"/power":
            power = float(message)
            if power != circuit.status.relay.power:
                circuit.status.relay.power = power
        if subtopic == "relay/"+circuit.relay_id+"/energy":
            circuit.status.relay.energy = int(message)
        if subtopic == "temperature":
            circuit.status.temperature = float(message)
        if subtopic == "temperature_f":
            circuit.status.temperature_f = float(message)
        if subtopic == "overtemperature":
            circuit.status.overtemperature = int(message)
        if subtopic == "temperature_status":
            circuit.status.temperature = message
        if subtopic == "voltage":
            circuit.status.voltage = float(message)    

def check_room_states(name):
    update = False
    for room_circuit in room_circuits:
        if name != room_circuit.name:
            continue
        update = True
    if update:
        draw_all()

def load_circuits():
    global circuits
    circuit_data = open(root+'circuits.json')
    circuit_list = json.load(circuit_data)
    circuits = []
    for circuit in circuit_list:
        circuits.append(RelayModule(circuit["id"],circuit["ip_address"],circuit["name"],circuit["relay_id"],circuit["location"],circuit["zones"],circuit["on_modes"],circuit["off_modes"]))

if __name__ == "__main__":
    load_circuits()
    load_config()
    canvas = Canvas(master, width=base_width, height=base_height, bg='black')
    master.geometry(str(base_width)+"x"+str(base_height))
    master.attributes('-fullscreen', True)
    master.configure(bg='black')
    client.on_message = on_message
    client.connect('192.168.2.200')
    client.subscribe('shellies/#')
    client.subscribe('smarter_circuits/sensors/#')
    client.subscribe('smarter_circuits/thermostats/#')
    client.subscribe('notifications')
    client.loop_start()
    draw_all()
    master.bind('<Button-1>', click)
    master.mainloop() 
        
    client.loop_stop()
    client.disconnect()
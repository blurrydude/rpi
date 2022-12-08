#! /usr/bin/env python3
import time
from tkinter import * 
import json
import paho.mqtt.client as mqtt
import datetime

root = 'C:\\Code\\rpi\\SmarterCircuits\\'

client = mqtt.Client()
master = Tk() 
master.geometry("1024x768")

canvas = Canvas(master, width=1024, height=768) 
canvas.place(x=0, y=0) 

show_points = False

selected_room = ""
room_circuits = []

points = []
lines = []
rooms = []

roomstats = {}
last_notification = ""

circuit_button_x = 690
circuit_button_width = 250
circuit_button_height = 48
circuit_button_y_start = 35

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
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))
    if x > 1000 and y < 24:
        show_points = show_points == False
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
    print(circuit+" clicked")
    client.publish('smarter_circuits/commands','toggle '+circuit.lower())

def click_room(room):
    global selected_room
    global room_circuits
    if room["name"] == "":
        return
    print(room["name"]+" clicked")
    selected_room = room["name"]
    
    config_data = open(root+'circuits.json')
    circuits = json.load(config_data)
    room_circuits = []
    for circuit in circuits:
        if room["name"] in circuit["zones"]:
            print(circuit)
            room_circuits.append(circuit["name"])
    
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
    if name != '':
        canvas.create_text(x,y,text=name,fill='black')

def draw_all():
    global canvas
    load_config()
    canvas.destroy()
    canvas = Canvas(master, width=1024, height=768) 
    canvas.place(x=0, y=0) 
    canvas.create_rectangle(0, 0, 1024, 768, fill="black")
    
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
        canvas.create_text(820,15,text=selected_room,fill='white')
    
    c = 0
    for circuit in room_circuits:
        y = circuit_button_y_start+(c*(circuit_button_height+8))
        canvas.create_rectangle(circuit_button_x,y,circuit_button_x+circuit_button_width,y+circuit_button_height, fill="green", outline="green") 
        canvas.create_text(circuit_button_x+(circuit_button_width/2),y+(circuit_button_height/2),text=circuit,fill='black',font="Times 20")
        c = c + 1
    
    c = 0
    y = 600
    for room in roomstats.keys():
        y = 600+(c*36)
        canvas.create_text(20,y,text=room+": "+str(round(roomstats[room]["temp"],2)),fill='white',anchor='nw',font='times 24')
        c = c + 1
    
    canvas.create_text(20,y+36,text=datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")+" - "+last_notification,fill='yellow',anchor='nw',font='times 24')

def load_config():
    global points
    global lines
    global rooms
    config_data = open(root+'DynamicUI.json')
    config = json.load(config_data)
    points = config["points"]
    lines = config["lines"]
    rooms = config["rooms"]

if __name__ == "__main__":
    load_config()
    client.on_message = on_message
    client.connect('192.168.2.200')
    client.subscribe('smarter_circuits/sensors/#')
    client.subscribe('smarter_circuits/thermostats/#')
    client.subscribe('notifications')
    client.loop_start()
    draw_all()
    master.bind('<Button-1>', click)
    master.mainloop() 
        
    client.loop_stop()
    client.disconnect()
#! /usr/bin/env python3
import time
from tkinter import * 
from shapely.geometry import LineString
from MainScreen import MainScreen
from MenuScreen import MenuScreen
from ClimateScreen import ClimateScreen

class UI:
    def __init__(self, brain):
        self.brain = brain
        self.fullscreen = True
        self.config = self.brain.config
        self.show_points = False
        self.show_room_names = False
        self.screen = "main"
        self.screens = {
            "main": MainScreen(self),
            "menu": MenuScreen(self),
            "climate": ClimateScreen(self)
        }
        self.master = Tk()
        self.canvas = Canvas(self.master, width=self.config.base_width, height=self.config.base_height, bg='black')
        self.room_circuits = []
        self.selected_room = ""

    def start(self):
        self.reset_resolution(True)
        self.master.bind('<Button-1>', self.click)
        self.draw_all()
        self.master.mainloop()
    
    def stop(self): 
        self.master.destroy()
    
    def toggle_fullscreen(self):
        self.fullscreen = self.fullscreen == False
        self.reset_resolution(self.fullscreen)
    
    def reset_resolution(self, fullscreen = False):
        self.master.geometry(str(self.config.base_width)+"x"+str(self.config.base_height))
        self.master.attributes('-fullscreen', fullscreen)
        self.master.configure(bg='black')
        self.reset_canvas()
    
    def reset_canvas(self):
        self.canvas.destroy()
        self.canvas = Canvas(self.master, width=self.config.base_width, height=self.config.base_height, bg='black')
        self.canvas.place(x=0, y=0) 
        self.rect((0, 0), (self.config.base_width, self.config.base_height), "black")
    
    def rect(self, top_left, bottom_right, fill):
        x1 = top_left[0]
        y1 = top_left[1]
        x2 = bottom_right[0]
        y2 = bottom_right[1]
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=fill)

    def point_in_shape(self, point, shape_points):
        if len(shape_points) > 2:
            return self.point_in_polygon(point, shape_points)
        return self.point_in_rect(point, shape_points)

    def point_in_rect(self, point, rect_points):
        return point[0] >= rect_points[0][0] and point[0] <= rect_points[1][0] and point[1] >= rect_points[0][1] and point[1] <= rect_points[1][1]

    def point_in_polygon(self, point, shape_points):
        crosses = 0
        far_point = (point[0]+self.config.base_width, point[1])
        if self.lines_cross(point, far_point, shape_points[0], shape_points[len(shape_points)-1]):
            crosses = crosses + 1
        for i in range(len(shape_points)-1):
            x = i + 1
            if self.lines_cross(point, far_point, shape_points[i], shape_points[x]):
                crosses = crosses + 1
        if crosses == 0 or crosses == 2:
            return False
        return True

    def lines_cross(p1,p2,p3,p4):
        line = LineString([p1,p2])
        other = LineString([p3,p4])
        return line.intersects(other)

    def click(self, event):
        x, y = event.x, event.y
        #print('{}, {}'.format(x, y))
        self.screens[self.screen].click(x, y)

    def switch_screen(self, switch_to):
        self.screen = switch_to
        self.draw_all()

    def detect_home_click(self, x, y):
        crosses = 0
        unit = self.config.circuit_button_height
        half_unit = unit / 2
        p1 = (x,y)
        p2 = (x+self.config.base_width,y)
        a = (unit,unit)
        b = (unit+half_unit,half_unit)
        c = (unit*2,unit)
        d = (unit*2,unit*1.5)
        e = (unit,unit*1.5)
        if self.lines_cross(p1,p2,a,b):
            crosses = crosses + 1
        if self.lines_cross(p1,p2,b,c):
            crosses = crosses + 1
        if self.lines_cross(p1,p2,c,d):
            crosses = crosses + 1
        if self.lines_cross(p1,p2,d,e):
            crosses = crosses + 1
        if self.lines_cross(p1,p2,a,e):
            crosses = crosses + 1
        if crosses == 0 or crosses == 2:
            return False
        self.switch_screen("main")
        return True

    def lines_cross(self, p1,p2,p3,p4):
        line = LineString([p1,p2])
        other = LineString([p3,p4])
        return line.intersects(other)

    def click_circuit(self, circuit):
        #print(circuit.name+" clicked")
        self.brain.mqtt.client.publish('smarter_circuits/commands','toggle '+circuit.name.lower())

    def click_room(self, room):
        if room["name"] == "":
            return
        #print(room["name"]+" clicked")
        self.selected_room = room["name"]
        
        self.room_circuits = []
        for circuit in self.brain.circuits:
            if room["name"] in circuit.zones:
                #print(circuit)
                self.room_circuits.append(circuit)
        
        self.draw_all()

    def draw_room(self, room):
        rectangles = room["rectangles"]
        name = room["name"]
        color = room["color"]
        for rectangle in rectangles:
            a = self.config.points[rectangle[0]]
            b = self.config.points[rectangle[1]]
            self.rect(a,b,color)
        tl = self.config.points[rectangles[0][0]]
        br = self.config.points[rectangles[0][1]]
        x = tl[0] + ((br[0] - tl[0]) /2)
        y = self.config.points[rectangles[0][0]][1] + 12
        if self.show_room_names and name != '':
            self.canvas.create_text(x,y,text=name,fill='black')

    def draw_all(self):
        self.brain.ticks = 0
        self.config.load_config()
        self.reset_canvas()
        self.screens[self.screen].draw()

    def draw_button(self, x, y, label, color):
        unit = self.config.circuit_button_height
        self.canvas.create_rectangle(x,y,x+self.config.circuit_button_width,y+self.config.circuit_button_height,fill=color,outline=color)
        self.canvas.create_text(x+(self.config.circuit_button_width/2),y+(unit/2),text=label,fill="white", font='times '+str(self.config.circuit_button_font_size))
        
    def draw_home_button(self):
        unit = self.config.circuit_button_height
        half_unit = unit / 2
        self.canvas.create_polygon(
            unit,unit,
            unit+half_unit,half_unit,
            unit*2,unit,
            unit*2,unit*1.5,
            unit,unit*1.5,
            fill="orange", outline="orange")
        bit = unit / 7
        wy = unit + bit
        wx = wy
        self.canvas.create_rectangle(wx,unit,wx+bit,wy,fill="black",outline="black")
        wx = wx + bit + bit
        self.canvas.create_rectangle(wx,unit,wx+bit,unit*1.5,fill="black",outline="black")
        wx = wx + bit + bit
        self.canvas.create_rectangle(wx,unit,wx+bit,wy,fill="black",outline="black")

    def draw_screen_title(self, title):
        tx = self.config.base_width / 2
        ty = 16
        self.canvas.create_text(tx,ty,text=title,fill='white',font='times '+str(self.config.circuit_button_font_size))

    def draw_mqtt_status(self):
        status_color = 'green'
        status = 'connected'
        if self.brain.mqtt.client.is_connected() is False:
            status_color = 'red'
            status = 'disconnected'
        self.canvas.create_text(self.config.circuit_button_height*2,6,text="MQTT: "+status,fill=status_color,anchor='nw',font='times '+str(self.config.info_block_font_size))

    def check_room_states(self, name):
        if self.screen != "main":
            return
        update = False
        for room_circuit in self.room_circuits:
            if name != room_circuit.name:
                continue
            update = True
        if update:
            self.draw_all()
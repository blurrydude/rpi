class MainScreen:
    def __init__(self, ui):
        self.ui = ui
    
    def click(self, x, y):
        if x >= 200 and x <= 200+self.ui.config.circuit_button_width and y >= self.ui.config.info_block_y and y <= self.ui.config.info_block_y+self.ui.config.circuit_button_height:
            self.ui.switch_screen("menu")
            return

        for room in self.ui.config.rooms:
            rectangles = room["rectangles"]
            init = False
            for rectangle in rectangles:
                a = self.ui.config.points[rectangle[0]]
                b = self.ui.config.points[rectangle[1]]
                if x >= a[0] and x <= b[0] and y >= a[1] and y <= b[1]:
                    init = True
            if init:
                self.ui.click_room(room)
                return
        
        c = 0
        for circuit in self.ui.room_circuits:
            rx1 = self.ui.config.circuit_button_x
            ry1 = self.ui.config.circuit_button_y_start+(c*(self.ui.config.circuit_button_height+8))
            rx2 = rx1 + self.ui.config.circuit_button_width
            ry2 = ry1 + self.ui.config.circuit_button_height
            c = c + 1
            if x >= rx1 and x <= rx2 and y >= ry1 and y <= ry2:
                self.ui.click_circuit(circuit)
                return

    def draw(self):
        for room in self.ui.config.rooms:
            self.ui.draw_room(room)

        for line in self.ui.config.lines:
            a = self.ui.config.points[line[0]]
            b = self.ui.config.points[line[1]]
            self.ui.canvas.create_line(a[0],a[1],b[0],b[1],fill='black',width=2)

        if self.ui.show_points:
            i = 0
            for point in self.ui.config.points:
                x = point[0]
                y = point[1]
                self.ui.canvas.create_rectangle(x,y,x+1,y+1, fill="green", outline="green") 
                tx = x
                ty = y - 8
                self.ui.canvas.create_text(tx,ty,text=str(i),fill='white')
                i = i + 1
        
        if self.ui.selected_room != "":
            self.ui.canvas.create_text(self.ui.config.circuit_button_x+(self.ui.config.circuit_button_width/2),15,text=self.ui.selected_room,fill='white')
        
        c = 0
        for circuit in self.ui.room_circuits:
            y = self.ui.config.circuit_button_y_start+(c*(self.ui.config.circuit_button_height+8))
            fill = "red"
            if circuit.status.relay.on:
                fill = "green"
            watts = circuit.status.relay.power
            self.ui.canvas.create_rectangle(self.ui.config.circuit_button_x,y,self.ui.config.circuit_button_x+self.ui.config.circuit_button_width,y+self.ui.config.circuit_button_height, fill=fill, outline="gray") 
            self.ui.canvas.create_text(self.ui.config.circuit_button_x+(self.ui.config.circuit_button_width/2),y+(self.ui.config.circuit_button_height/2),text=circuit.name+" ~ "+str(round(watts))+"W",fill='black',font="Times "+str(self.ui.config.circuit_button_font_size))
            c = c + 1
        
        c = 0
        y = self.ui.config.info_block_y
        for room in self.ui.brain.roomstats.keys():
            self.ui.canvas.create_text(self.ui.config.info_block_x,y,text=room+": "+str(round(self.ui.brain.roomstats[room]["temp"],2)),fill='white',anchor='nw',font='times '+str(self.ui.config.info_block_font_size))
            y = y + self.ui.config.info_block_spacing
            c = c + 1
        
        self.ui.canvas.create_text(self.ui.config.info_block_x,y,text="Notification: "+self.ui.brain.last_notification,fill='yellow',anchor='nw',font='times '+str(self.ui.config.info_block_font_size))
        y = y + self.ui.config.info_block_spacing

        self.ui.draw_mqtt_status()

        self.ui.canvas.create_rectangle(300,self.ui.config.info_block_y,300+(self.ui.config.circuit_button_width/2),self.ui.config.info_block_y+self.ui.config.circuit_button_height, fill='purple', outline="white")
        self.ui.canvas.create_text(300+(self.ui.config.circuit_button_width/4),self.ui.config.info_block_y+(self.ui.config.circuit_button_height/2),text="MENU",fill='white',font="Times "+str(self.ui.config.circuit_button_font_size))

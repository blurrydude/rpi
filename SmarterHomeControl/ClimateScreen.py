class ClimateScreen:
    def __init__(self, ui):
        self.ui = ui

    def draw(self):
        self.ui.draw_screen_title("CLIMATE")
        self.ui.draw_home_button()
        self.ui.draw_mqtt_status()
        c = 0
        y = self.ui.config.circuit_button_height*3
        unit = self.ui.config.circuit_button_height/2
        for room in self.ui.brain.roomstats.keys():
            roomstat = self.ui.brain.roomstats[room]
            if roomstat["hvac"] is False:
                continue
            fill = 'white'
            if roomstat["disabled"] is True:
                fill = 'dark gray'
            #self.ui.canvas.create_text(self.ui.config.circuit_button_height,y,text=room+": "+str(round(roomstat["temp"],2))+" (H:"+str(roomstat["high"])+", L:"+str(roomstat["low"])+") "+roomstat["status"],fill=fill,anchor='nw',font='times '+str(self.ui.config.info_block_font_size))
            self.ui.canvas.create_text(unit,y,text=room+": ",anchor='w',fill=fill,font='times '+str(self.ui.config.circuit_button_font_size))
            self.ui.canvas.create_text(unit*8,y,text=str(round(roomstat["temp"],2)),anchor='w',fill=fill,font='times '+str(self.ui.config.circuit_button_font_size))
            self.ui.canvas.create_text(unit*16,y,text="heat below: "+str(roomstat["low"]),fill=fill,font='times '+str(self.ui.config.circuit_button_font_size))
            self.ui.canvas.create_text(unit*32,y,text=roomstat["status"],anchor='w',fill=fill,font='times '+str(self.ui.config.circuit_button_font_size))
            self.ui.canvas.create_polygon(
                unit*15,y-unit,
                unit*16,y-(unit*2),
                unit*17,y-unit,
                fill="red",outline="red")
            self.ui.canvas.create_polygon(
                unit*15,y+unit,
                unit*16,y+(unit*2),
                unit*17,y+unit,
                fill="blue",outline="blue")
            self.ui.canvas.create_text(unit*26,y,text="cool above: "+str(roomstat["high"]),fill=fill,font='times '+str(self.ui.config.circuit_button_font_size))
            self.ui.canvas.create_polygon(
                unit*25,y-unit,
                unit*26,y-(unit*2),
                unit*27,y-unit,
                fill="red",outline="red")
            self.ui.canvas.create_polygon(
                unit*25,y+unit,
                unit*26,y+(unit*2),
                unit*27,y+unit,
                fill="blue",outline="blue")
            y = y + (self.ui.config.circuit_button_height*3)
            c = c + 1

    def click(self, x, y):
        if self.ui.detect_home_click(x,y):
            return
        py = self.ui.config.circuit_button_height*3
        unit = self.ui.config.circuit_button_height/2
        for room in self.ui.brain.roomstats.keys():
            roomstat = self.ui.brain.roomstats[room]
            poly_up_low = [
                (unit*15,py-unit),
                (unit*16,py-(unit*2)),
                (unit*17,py-unit)]
            poly_down_low = [
                (unit*15,py+unit),
                (unit*16,py+(unit*2)),
                (unit*17,py+unit)]
            poly_up_high = [
                (unit*25,py-unit),
                (unit*26,py-(unit*2)),
                (unit*27,py-unit)]
            poly_down_high = [
                (unit*25,py+unit),
                (unit*26,py+(unit*2)),
                (unit*27,py+unit)]

            py = py + (self.ui.config.circuit_button_height*3)
            update = False
            if self.ui.point_in_polygon((x,y), poly_down_low):
                roomstat["low"] = roomstat["low"] - 1
                update = True
            if self.ui.point_in_polygon((x,y), poly_up_low):
                roomstat["low"] = roomstat["low"] + 1
                update = True
            if self.ui.point_in_polygon((x,y), poly_down_high):
                roomstat["high"] = roomstat["high"] - 1
                update = True
            if self.ui.point_in_polygon((x,y), poly_up_high):
                roomstat["high"] = roomstat["high"] + 1
                update = True
            if update:
                self.ui.brain.set_thermostat(room, roomstat["low"], roomstat["high"])
                self.ui.draw_all()
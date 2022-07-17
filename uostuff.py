from audioop import minmax
from PIL import Image
import os
import json

items = {}
#directory = "C:\\Users\\idkline\\Dropbox\\UOStuff\\UOArt\\Items\\"
directory = "/home/ian/Dropbox/UOStuff/UOArt/Items/"
home_dir = os.path.dirname(os.path.realpath(__file__))+"/"

image_size = (1920, 1080)
screen_offeset_x = 540
screen_offeset_y = 100
img = Image.new(mode="RGBA", size=image_size)

def get_item_image(id):
    f = os.path.join(directory, str(id)+".png")    
    item = Image.open(f)
    return item

def cart_to_iso(point):
    isoX = point[0] - point[1]
    isoY = (point[0] + point[1])/2
    return [isoX, isoY]

def mappos_to_screen_pos(x, y, h = 0):
    rsx = (y * -22) + (x * 22)
    rsy = (y * 22) + (x * 22) - h
    return [rsx, rsy, 0]

def add_item(img, itemnum, map_pos):
    global items
    item = items[str(itemnum)]
    point = mappos_to_screen_pos(map_pos[0],map_pos[1],item.height-44-map_pos[2])
    screen_pos = (
        point[0] + screen_offeset_x,
        point[1] + screen_offeset_y
    )
    #print("adding item "+str(itemnum)+" at map_pos ("+str(map_pos[0])+","+str(map_pos[1])+","+str(map_pos[2])+") screen_pos ("+str(screen_pos[0])+","+str(screen_pos[1])+")")
    img.paste(item, screen_pos, item)

def read_json():
    global items
    data = json.load(open(home_dir+'uostuff.json'))
    for datum in data:
        if str(datum["itemid"]) not in items.keys():
            items[str(datum["itemid"])] = get_item_image(datum["itemid"])
    for datum in data:
        if datum["command"] == "tile":
            tile_item(datum["target1"], datum["target2"], datum["itemid"])
        if datum["command"] == "add":
            add_item(img, datum["itemid"], datum["target"])

def tile_item(target1, target2, itemid):
    for y in range(target1[1],target2[1]+1):
        for x in range(target1[0],target2[0]+1):
            add_item(img, itemid, (x,y,target1[2]))

read_json()
img.show()
from audioop import minmax
from PIL import Image
import os

directory = "C:\\Users\\idkline\\Dropbox\\UOStuff\\UOArt\\Items\\"
#directory = "/home/ian/Dropbox/UOStuff/UOArt/Items/"
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
    return (rsx, rsy)

def add_item(img, item, screen_pos):
    img.paste(item, screen_pos, item)
items = {}
rowstart = (0,0)
points = []
minx = 0
maxx = 0
maxy = 0
for y in range(10):
    # #screen_pos = mappos_to_screen_pos(x*44, y*22)
    # rowstart = (
    #     rowstart[0] - 22,
    #     rowstart[1] + 22
    # )
    # screen_pos = rowstart
    points.append([])
    for x in range(10):
        screen_pos = mappos_to_screen_pos(x, y)
        #img.paste(tile, screen_pos, tile)
        points[y].append([screen_pos[0], screen_pos[1], 1180])
        if screen_pos[0] < minx:
            minx = screen_pos[0]
        if screen_pos[0] > maxx:
            maxx = screen_pos[0]
        if screen_pos[1] > maxy:
            maxy = screen_pos[1]
        # screen_pos = (
        #     screen_pos[0] + 22,
        #     screen_pos[1] + 22
        # )
maxx = maxx - minx
items_to_load = []
for xpoints in points:
    for point in xpoints:
        if point[2] not in items_to_load:
            items_to_load.append(point[2])

for item in items_to_load:
    items[str(item)] = get_item_image(item)

img = Image.new(mode="RGBA", size=(maxx+44,maxy+44))
for xpoints in points:
    for point in xpoints:
        screen_pos = (
            point[0] - minx,
            point[1]
        )
        add_item(img, items[str(point[2])], screen_pos)
wall = get_item_image(2475)
point = mappos_to_screen_pos(9,0,wall.height-44)
screen_pos = (
    point[0] - minx,
    point[1]
)
add_item(img, wall, screen_pos)
img.show()
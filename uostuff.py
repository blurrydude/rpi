from PIL import Image
import os

directory = "C:\\Users\\idkline\\Dropbox\\UOStuff\\UOArt\\Items\\"
def get_item_image(id):
    f = os.path.join(directory, str(id)+".png")    
    item = Image.open(f)
    return item

def cart_to_iso(point):
    isoX = point[0] - point[1]
    isoY = (point[0] + point[1])/2
    return [isoX, isoY]

def mappos_to_screen_pos(x, y):
    iso = cart_to_iso((x, y))
    return (int(iso[0]), int(iso[1]))

img = Image.new(mode="RGBA", size=(1024,768))
tile = get_item_image(1173)
for x in range(10):
    for y in range(10):
        screen_pos = mappos_to_screen_pos(x*44, y*22)
        img.paste(tile, screen_pos, tile)
img.show()
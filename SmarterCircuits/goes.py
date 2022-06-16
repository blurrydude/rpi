import math
import os
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime, timedelta

save_path = "C:/Temp/GOES/"
last_grab = datetime.now() - timedelta(minutes=5)

def grab_images():
    goes16baseUrl = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/cgl/" #16/latest.jpg"
    now = datetime.now()
    nowstr = now.strftime("%Y%m%d%H%M")
    for i in range(1,17):
        index = str(i)
        if i < 10:
            index = "0"+index
        url = goes16baseUrl+index+"/latest.jpg"
        print("GRAB: "+url)
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.save(save_path+index+"-"+nowstr+".jpg")

def run():
    while True:
        if last_grab < datetime.now() - timedelta(minutes=5):
            last_grab = datetime.now()
            grab_images()

def process_band_11():
    frames = []
    for filename in os.listdir(save_path):
        f = os.path.join(save_path, filename)
        # checking if it is a file
        c = 0
        if os.path.isfile(f) and filename.startswith("11-"):
            img = Image.open(f)
            frames.append([])
            for y in range(img.height):
                frames[c].append([])
                for x in range(img.width):
                    p = img.getpixel((x,y))
                    r = p[0]
                    g = p[1]
                    b = p[2]
                    rgd = abs(r-g)
                    rbd = abs(r-b)
                    if rgd < 60 and rbd < 60:
                        frames[c][y].append(0)
                    else:
                        frames[c][y].append(r)
    home = (1085,1350)
    mass_in_range = 0
    for frame in frames:
        w = len(frame[0])
        h = len(frame)
        img = Image.new(mode="RGB",size=(w,h))
        for y in range(h):
            for x in range(w):
                d = math.dist(home,(x,y))/3
                r = 0
                if frame[y][x] >= 200:
                    r = 255
                g = 0
                b = int(max(0,255 - d))
                if b > 0 and r > 0:
                    g = 255
                    mass_in_range = mass_in_range + 1
                img.putpixel((x,y),(r,g,b))

        print("storm mass in range: "+str(mass_in_range))
        draw_cross_hair(home,img)
        img.show()

def draw_cross_hair(xy,img):
    x = xy[0]
    y = xy[1]
    img.putpixel((x-3,y),(0,255,0))
    img.putpixel((x-2,y),(0,255,0))
    img.putpixel((x-1,y),(0,255,0))
    img.putpixel((x,y),(0,255,0))
    img.putpixel((x+1,y),(0,255,0))
    img.putpixel((x+2,y),(0,255,0))
    img.putpixel((x+3,y),(0,255,0))
    img.putpixel((x,y-3),(0,255,0))
    img.putpixel((x,y-2),(0,255,0))
    img.putpixel((x,y-1),(0,255,0))
    img.putpixel((x,y+1),(0,255,0))
    img.putpixel((x,y+2),(0,255,0))
    img.putpixel((x,y+3),(0,255,0))

if __name__ == "__main__":
    process_band_11()
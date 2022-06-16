import math
import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from datetime import datetime, timedelta

save_path = "C:/Temp/GOES/"
last_grab = datetime.now() - timedelta(minutes=5)
pixels_per_mile = 3
data = []
home = (1085,1350)
myFont = ImageFont.truetype(save_path+'Ubuntu-Regular.ttf', 24)

def grab_images():
    now = datetime.now()
    nowstr = now.strftime("%Y%m%d%H%M")
    for i in range(1,17):
        index = str(i)
        if i < 10:
            index = "0"+index
        grab_image(index,save_path+index+"-"+nowstr+".jpg")

def grab_image(band,save_file):
    goes16baseUrl = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/cgl/"
    url = goes16baseUrl+band+"/latest.jpg"
    print("GRAB: "+url)
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.save(save_file)

def run():
    global last_grab
    while True:
        now = datetime.now()
        if last_grab < now - timedelta(minutes=5):
            last_grab = now
            grab_and_process()

def grab_and_process():
    now = datetime.now()
    nowstr = now.strftime("%Y%m%d%H%M")
    file_path = save_path+"11-"+nowstr+".jpg"
    grab_image("11",file_path)
    process_band_11_image(file_path)

def process_band_11():
    for filename in os.listdir(save_path):
        f = os.path.join(save_path, filename)
        # checking if it is a file
        if os.path.isfile(f) and filename.startswith("11-"):
            process_band_11_image(f)
    
def process_band_11_image(f):
    global data
    mass_in_range = 0
    closest_mass = 1000000
    print("reading band 11 image")
    img = Image.open(f)
    w = img.width
    h = img.height
    nimg = Image.new(mode="RGB",size=(w,h))
    print("image is "+str(w)+" by "+str(h))
    for y in range(h):
        for x in range(w):
            d = math.dist(home,(x,y))/2
            p = img.getpixel((x,y))
            r = p[0]
            g = p[1]
            b = p[2]
            nr = 0
            ng = 0
            nb = int(max(0,255 - d))
            rgd = abs(r-g)
            rbd = abs(r-b)
            if rgd < 60 and rbd < 60:
                nimg.putpixel((x,y),(nr,ng,nb))
                continue
            if r >= 200:
                nr = 255
                miles = round(d * pixels_per_mile)
                if miles < closest_mass:
                    closest_mass = miles
            if nb > 0 and nr > 0:
                ng = 255
                mass_in_range = mass_in_range + 1
            nimg.putpixel((x,y),(nr,ng,nb))
    if closest_mass == 1000000:
        closest_mass = 0
    imgdraw = ImageDraw.Draw(nimg)
    imgdraw.text((28, 32), "mass in range: "+str(mass_in_range), font=myFont, fill=(255, 255, 255))
    imgdraw.text((28, 64), "closest mass: "+str(closest_mass)+" miles", font=myFont, fill=(255, 255, 255))
    data.append({
        "mass_in_range":mass_in_range,
        "closest_mass":closest_mass,
    })
    draw_cross_hair(home,nimg)
    nimg.save(f.replace("11-","processed"))

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
    run()
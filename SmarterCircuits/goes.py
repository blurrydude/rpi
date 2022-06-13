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

if __name__ == "__main__":
    while True:
        if last_grab < datetime.now() - timedelta(minutes=5):
            last_grab = datetime.now()
            grab_images()

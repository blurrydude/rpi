# import the Python Imaging Library (PIL) to work with bitmap files
from PIL import Image
import paho.mqtt.client as mqtt

client = mqtt.Client()
# open the bitmap file
img = Image.open('/home/ian/rpi/PICO/led_assistant/your_image.png')

# get the size of the image in pixels
width, height = img.size

# create an empty list to store the pixel information
pixels = ""

# iterate over each pixel in the image
for y in range(height):
    for x in range(width):
        # get the color value(s) for the current pixel
        if img.mode == 'RGB':
            r, g, b = img.getpixel((x, y))
            color = '{:02X}{:02X}{:02X}'.format(r, g, b)
        elif img.mode == 'RGBA':
            r, g, b, a = img.getpixel((x, y))
            if a == 0:
                # if the alpha value is 0, the pixel is transparent
                color = '000000'
            else:
                color = '{:02X}{:02X}{:02X}'.format(r, g, b)
        elif img.mode == 'L':
            l = img.getpixel((x, y))
            color = '{:02X}{:02X}{:02X}'.format(l, l, l)
        else:
            raise ValueError('Unsupported image mode: %s' % img.mode)
        # add the pixel information to the row list
        if color != "000000":
            pixels = pixels + f"{x}{y}{color}64|"

# print the pixels list
print(pixels)
client.connect("192.168.2.200")
client.publish("smarter_circuits/rgbring",pixels)
client.disconnect()
#00FF000064|7000FF0064|11FF000064|6100FF0064|22FF000064|5200FF0064|250000FF64|55FFFF0064|160000FF64|66FFFF0064|070000FF64|77FFFF0064
#10FF000064|11FF000064|6100FF0064|7100FF0064|22FF000064|5200FF0064|250000FF64|55FFFF0064|060000FF64|160000FF64|66FFFF0064|67FFFF0064
#10FF000064|21FF000064|7100FF0064|22FF000064|5200FF0064|6200FF0064|150000FF64|250000FF64|55FFFF0064|060000FF64|56FFFF0064|67FFFF0064
#20FF000064|21FF000064|32FF000064|6200FF0064|7200FF0064|5300FF0064|240000FF64|050000FF64|150000FF64|45FFFF0064|56FFFF0064|57FFFF0064
#30FF000064|31FF000064|32FF000064|5300FF0064|6300FF0064|7300FF0064|040000FF64|140000FF64|240000FF64|45FFFF0064|46FFFF0064|47FFFF0064
#40FF000064|41FF000064|42FF000064|030000FF64|130000FF64|230000FF64|5400FF0064|6400FF0064|7400FF0064|35FFFF0064|36FFFF0064|37FFFF0064
#50FF000064|51FF000064|020000FF64|120000FF64|42FF000064|230000FF64|5400FF0064|35FFFF0064|6500FF0064|7500FF0064|26FFFF0064|27FFFF0064
#60FF000064|010000FF64|51FF000064|120000FF64|220000FF64|52FF000064|25FFFF0064|5500FF0064|6500FF0064|26FFFF0064|7600FF0064|17FFFF0064
#60FF000064|010000FF64|110000FF64|61FF000064|220000FF64|52FF000064|25FFFF0064|5500FF0064|16FFFF0064|6600FF0064|7600FF0064|17FFFF0064
#000000FF64|70FF000064|110000FF64|61FF000064|220000FF64|52FF000064|25FFFF0064|5500FF0064|16FFFF0064|6600FF0064|07FFFF0064|7700FF0064

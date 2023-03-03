from PIL import Image, ImageDraw
import math

# Define the size of the image and the starting coordinate
room_width = 20
room_length = 12
beam_length = 2000
scale = 50
image_w = room_width * scale
image_h = room_length * scale
img_size = (image_w, image_h)
coordinates = [(0, 12),(20,12)]

# Create a new image with a black background
img = Image.new('RGB', img_size, color='black')

# Define the angle step size in radians
angle_step = math.radians(9)

for coord in coordinates:
    # Loop through the angles and draw lines
    for i in range(0, 360, 9):
        x = coord[0] * scale
        y = coord[1] * scale
        angle = math.radians(i)
        end_x = int(x + beam_length * math.cos(angle))
        end_y = int(y + beam_length * math.sin(angle))
        img_draw = ImageDraw.Draw(img)
        img_draw.line((x, y, end_x, end_y), fill=(255, 255, 255), width=1)

# Save the image as a bitmap file
img.save('/home/ian/rpi/tools/output.bmp')

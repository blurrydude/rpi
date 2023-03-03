from PIL import Image

# Open the image
img = Image.open('/home/ian/rpi/tools/pixelart2.png')

# Get the size of the image
width, height = img.size

file = open('/home/ian/rpi/tools/pixelart.txt','w')
r = 0
# Loop through each pixel in the image
for x in range(width):
    for y in range(height):
        # Get the color of the pixel
        pixel = img.getpixel((x, y))
        
        # Check if the pixel is white
        if pixel[0] > 200:
            # Print the coordinates of the white pixel
            file.write(f"({x}, {y}),")
            r = r + 1
            if r >= 20:
                r = 0
                file.write("\n")

file.close()
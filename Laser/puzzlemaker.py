import random
import svgwrite

# Set up the dimensions of the rectangle
width = 200
height = 100

# Create the SVG image
dwg = svgwrite.Drawing('image.svg', size=(f'{width}mm', f'{height}mm'))

# Set the starting point for the drawing
x = 0
y = 0

while y < height:
    # Move down the y axis a random distance
    y += random.randint(20, 30)
    
    while x < width:
        # Draw a line to the right between 10 and 30 mm long
        x += random.randint(10, 30)
        dwg.add(dwg.line((x, y), (x, y), stroke='black'))
        
        # Create a half circle upwards or downwards randomly with a radius between 5 and 20 mm
        direction = random.choice(['up', 'down'])
        radius = random.randint(5, 20)
        if direction == 'up':
            dwg.add(dwg.path(d="M %d %d A %d %d 0 0 1 %d %d" % (x, y, radius, radius, x, y - radius), stroke='black'))
        else:
            dwg.add(dwg.path(d="M %d %d A %d %d 0 0 1 %d %d" % (x, y, radius, radius, x, y + radius), stroke='black'))
        
    # Draw a line to the edge of the rectangle
    dwg.add(dwg.line((x, y), (width, y), stroke='black'))

# Save the image
dwg.save()

import random

def create_brick_pattern(width, height, min_brick_width, max_brick_width, min_brick_height, max_brick_height):
    # Create the SVG header
    svg = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    svg += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n'
    svg += '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    svg += '<svg width="' + str(width) + '" height="' + str(height) + '"\n'
    svg += 'xmlns="http://www.w3.org/2000/svg" version="1.1">\n'

    # Draw the bricks
    for y in range(0, height, max_brick_height):
        for x in range(0, width, max_brick_width):
            # Randomize brick width and height
            brick_width = random.randint(min_brick_width, max_brick_width)
            brick_height = random.randint(min_brick_height, max_brick_height)
            # Randomize brick shading
            gray = random.randint(0,255)
            color = 'rgb(' + str(gray) + ',' + str(gray) + ',' + str(gray) + ')'
            svg += '<rect x="' + str(x) + '" y="' + str(y) + '" width="' + str(brick_width) + '" height="' + str(brick_height) + '" fill="' + color + '"/>\n'

    # Close the SVG tag
    svg += '</svg>\n'

    return svg

# Example usage
width = 300
height = 200
min_brick_width = 10
max_brick_width = 20
min_brick_height = 5
max_brick_height = 10

svg_output = create_brick_pattern(width, height, min_brick_width, max_brick_width, min_brick_height, max_brick_height)

#save the output to a file
with open("/home/ian/rpi/Laser/brick_pattern.svg", "w") as file:
    file.write(svg_output)

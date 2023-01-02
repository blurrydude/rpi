import re

def parse_gcode(gcode_str):
    """Parses G-code and returns a list of command tuples."""
    # Split the G-code string into lines
    lines = gcode_str.strip().split("\n")

    # Compile a regular expression to match G-code commands
    pattern = re.compile(r"^G(\d+)\s*(.*)$")

    # Iterate over the lines and parse the G-code commands
    commands = []
    for line in lines:
        match = pattern.match(line)
        if match:
            command = int(match.group(1))
            params = match.group(2).strip()
            commands.append((command, params))

    return commands

def generate_bitmap(gcode_str, width, height):
    """Generates a bitmap from G-code commands."""
    # Parse the G-code into a list of commands
    commands = parse_gcode(gcode_str)

    # Create a blank bitmap with the specified width and height
    bitmap = [[0 for _ in range(width)] for _ in range(height)]

    # Initialize the current position to the origin
    x = 0
    y = 0

    # Iterate over the commands and update the bitmap
    for command, params in commands:
        if command == 1:  # Move command
            # Parse the X and Y coordinates from the parameters string
            x_match = re.search(r"X(\-?\d+)", params)
            y_match = re.search(r"Y(\-?\d+)", params)
            if x_match:
                x = int(x_match.group(1))
            if y_match:
                y = int(y_match.group(1))

            # Set the pixel at the current position to 1
            bitmap[y][x] = 1

    return bitmap

# Example usage
gcode_str = "G1 X0 Y0\nG1 X1 Y0\nG1 X1 Y1\nG1 X0 Y1"
bitmap = generate_bitmap(gcode_str, 10, 10)

# Print the resulting bitmap
for row in bitmap:
    print(row)

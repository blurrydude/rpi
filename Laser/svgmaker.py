import svgwrite

def create_house_panel(scale, stories):
    # Set the dimensions of the building based on the scale
    width = scale * 20
    height = scale * (stories * 10)
    finger_size = int(scale * 0.5)
    overhang = int(scale * 2)
    door_width = int(scale * 2)
    door_height = int(scale * 4)
    window_width = int(scale)
    window_height = int(scale * 2)
    
    # Create a new SVG file
    dwg = svgwrite.Drawing('/home/ian/rpi/Laser/panel.svg', profile='tiny')
    
    # Create the main rectangle for the panel
    rect = dwg.add(dwg.rect((0, 0), (width, height), stroke='black', fill='none'))
    
    # Create the finger joints on the top and bottom edges of the panel
    for i in range(0, width, finger_size):
        finger_top = dwg.add(dwg.rect((i, 0), (finger_size, finger_size), stroke='black', fill='none'))
        finger_bottom = dwg.add(dwg.rect((i, height-finger_size), (finger_size, finger_size), stroke='black', fill='none'))
        
    # Create the finger joints on the left and right edges of the panel
    for i in range(0, height, finger_size):
        finger_left = dwg.add(dwg.rect((0, i), (finger_size, finger_size), stroke='black', fill='none'))
        finger_right = dwg.add(dwg.rect((width-finger_size, i), (finger_size, finger_size), stroke='black', fill='none'))
        
    # Create the front door
    door = dwg.add(dwg.rect(((width-door_width)/2, height-door_height), (door_width, door_height), stroke='black', fill='none'))
    
    # Create windows in all the walls
    window1 = dwg.add(dwg.rect((finger_size, finger_size), (window_width, window_height), stroke='black', fill='none'))
    window2 = dwg.add(dwg.rect((width-finger_size-window_width, finger_size), (window_width, window_height), stroke='black', fill='none'))
    window3 = dwg.add(dwg.rect((finger_size, height-finger_size-window_height), (window_width, window_height), stroke='black', fill='none'))
    window4 = dwg.add(dwg.rect((width-finger_size-window_width, height-finger_size-window_height), (window_width, window_height), stroke='black', fill='none'))
    
    # Create the roof shape
    roof = dwg.add(dwg.polygon([(0, height-overhang), (width/2, 0-overhang), (width, height-overhang)], stroke='black', fill='none'))
    
    # Save the SVG file
    dwg.save()

create_house_panel(24,2)